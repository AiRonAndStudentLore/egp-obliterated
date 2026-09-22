#!/usr/bin/env python
"""
compile_batch.py — LLM-as-compiler step.

Pulls the next N pending EGP rows for a given sub-category from SQLite, builds
the SYSTEM_PROMPT + payload, calls the configured LLM backend, parses the JSON
array response, and writes it to batches/<sub_category-slug>-NNN.json.

The compile output is then consumed by build_batch.py.

Backends:
  openrouter  POSTs directly to https://openrouter.ai/api/v1/chat/completions
              (default). Requires OPENROUTER_API_KEY env var.
  crow        uses `crow-cli run`. Whatever model crow is configured for.

Usage (openrouter backend, default — using MiniMax M3):
  OPENROUTER_API_KEY=sk-or-... \\
  .venv/bin/python compile_batch.py \\
    --sub-category "adverbs and adverb phrases: types and meanings" \\
    --limit 15

Or pick another model preset:
  .venv/bin/python compile_batch.py \\
    --model gemma-4-26b-free --sub-category "position" --limit 15

Or dry-run (writes prompt only, no API call):
  python compile_batch.py ... --dry-run

Cost notes (minimax/minimax-m3 default on OpenRouter):
  $0.30/M input, $1.20/M output. A 15-row batch (~15K input, ~6K output) ~$0.012.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).parent
DB = ROOT / "egp_pipeline.db"
BATCH_DIR = ROOT / "batches"
PROMPT_PATH = ROOT / "SYSTEM_PROMPT.txt"
DEFAULT_BASE = "https://openrouter.ai/api/v1"
DEFAULT_BACKEND = "openrouter"
DEFAULT_MODEL = "minimax/minimax-m2.7"

# Curated cheap-good model presets for the openrouter backend.
# Naming convention for presets: <family>-<size>  -> OpenRouter model id.
# Free-tier variants (':free') on OpenRouter are rate-limited/queued but
# zero-cost. Drop the suffix or pick the paid tier if you need higher
# throughput. The crow backend ignores these (model is set in crow-cli).
MODEL_PRESETS = {
    # MiniMax M3 / M2.7
    "minimax-m3":     "minimax/minimax-m3",
    "minimax-m2.7":   "minimax/minimax-m2.7",
    "minimax-01":     "minimax/minimax-01",
    # Google Gemini 2.5
    "gemini-2.5-pro":   "google/gemini-2.5-pro",
    "gemini-2.5-pro-batch": "google/gemini-2.5-pro:batch",
    "gemini-2.5-flash": "google/gemini-2.5-flash",
    "gemini-2.5-flash-lite": "google/gemini-2.5-flash-lite",
    # Qwen 3.8 Flash
    "qwen3.8-flash":  "qwen/qwen3.8-flash",
    "qwen3.7-flash":  "qwen/qwen3.7-flash",
    "qwen3-coder-flash": "qwen/qwen3-coder-flash",
    # Gemma 4 (Google).
    "gemma-4-26b-free": "google/gemma-4-26b-a4b-it:free",
    "gemma-4-26b-paid": "google/gemma-4-26b-a4b-it",
    "gemma-4-31b-free": "google/gemma-4-31b-it:free",
    "gemma-4-31b-paid": "google/gemma-4-31b-it",
    # Gemma 3.
    "gemma-3-4b":       "google/gemma-3-4b-it",
    "gemma-3-12b":      "google/gemma-3-12b-it",
    "gemma-3-27b":      "google/gemma-3-27b-it",
    # Llama fallback.
    "llama-3.1-8b":     "meta-llama/llama-3.1-8b-instruct",
    "llama-3.3-70b":    "meta-llama/llama-3.3-70b-instruct",
}

PRESET_NAMES = ", ".join(sorted(MODEL_PRESETS.keys()))


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60]


def fetch_slice(sub_category: str, limit: int) -> list[dict]:
    """Pull the next N pending rows for a sub-category, in row order."""
    import sqlite3
    c = sqlite3.connect(str(DB))
    c.row_factory = sqlite3.Row
    rows = c.execute("""
        SELECT egp_id, row_number, level, super_category, sub_category,
               lexical_range, guideword, can_do_statement, example_raw
          FROM rows
         WHERE status='pending' AND sub_category=?
         ORDER BY row_number
         LIMIT ?
    """, (sub_category, limit)).fetchall()
    c.close()
    out = []
    for r in rows:
        out.append({
            "egp_id": r["egp_id"],
            "level": r["level"],
            "super_category": r["super_category"],
            "sub_category": r["sub_category"],
            "lexical_range": r["lexical_range"],
            "guideword": r["guideword"],
            "can_do_statement": r["can_do_statement"],
            "examples": [e for e in (r["example_raw"] or "").split("\n") if e.strip()],
        })
    return out


def build_messages(slice_rows: list[dict]) -> list[dict]:
    """Compose the OpenAI-compatible messages payload (for the OpenRouter backend)."""
    system = PROMPT_PATH.read_text().strip()
    payload_json = json.dumps(slice_rows, indent=1)
    user_block = (
        f"INPUT DATA ({len(slice_rows)} entries — use these exact egp_ids):\n\n"
        f"{payload_json}\n\n"
        f"REMEMBER: Return a JSON array of detector objects ONLY. "
        f"No commentary, no Markdown fences, no intro/outro text. "
        f"Use only the egp_ids above."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_block},
    ]


def build_single_prompt(slice_rows: list[dict]) -> str:
    """Compose a single-string prompt for the crow-cli backend.

    crow-cli run takes one [PROMPT] arg, so we concatenate system + user
    instructions. The system prompt is unmodified (still tells the model
    'return a JSON array only'). The user block carries the actual rows.
    """
    system = PROMPT_PATH.read_text().strip()
    payload_json = json.dumps(slice_rows, indent=1)
    user_block = (
        f"INPUT DATA ({len(slice_rows)} entries — use these exact egp_ids):\n\n"
        f"{payload_json}"
    )
    # Sandwich: system instructions first, then the data, then a final reminder.
    # Most chat models follow the LAST directive best, so we keep the JSON-only
    # reminder at the bottom.
    return (
        f"{system}\n\n"
        f"---\n\n"
        f"{user_block}\n\n"
        f"---\n\n"
        f"REMINDER: Return a JSON array of detector objects ONLY. "
        f"No commentary, no Markdown fences, no intro/outro text. "
        f"Use only the egp_ids above."
    )


def call_crow(prompt: str, timeout: int = 600) -> str:
    """Invoke `crow-cli run <prompt>` and extract the assistant's text.

    crow-cli prints a TUI transcript with dividers. The assistant's reply
    sits between the second 'Assistant' header and the trailing 'Session:'
    footer. We extract just that.
    """
    proc = subprocess.run(
        ["crow-cli", "run", prompt],
        capture_output=True, text=True, timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"crow-cli failed (exit {proc.returncode}): {proc.stderr[:500]}")
    text = proc.stdout
    # Find the Assistant section and the next Session: footer.
    m = re.search(
        r"Assistant\s*[-─]+\s*\n(.*?)(?:\n\s*[-─]+\s*\n|\nSession:)",
        text, re.DOTALL,
    )
    if not m:
        # Fallback: take everything after the last 'Assistant' divider.
        idx = text.rfind("Assistant")
        body = text[idx:] if idx >= 0 else text
        return body.split("Session:")[0].strip()
    return m.group(1).strip()


def call_openrouter(
    api_key: str, model: str, messages: list[dict],
    base_url: str = DEFAULT_BASE,
    temperature: float = 0.0, max_tokens: int = 8192,
    timeout: int = 180, referer: str = "", title: str = "",
) -> dict:
    """POST to OpenRouter. Returns the parsed JSON response. Raises on error."""
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title
    url = urljoin(base_url.rstrip("/") + "/", "chat/completions")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")[:1000]
        except Exception:
            pass
        raise RuntimeError(f"OpenRouter HTTP {e.code}: {err_body}") from e


def extract_json_array(text: str) -> list:
    """The LLM may wrap output in a JSON object or array. Find the rules list."""
    # Try direct array parse first.
    text = text.strip()
    if text.startswith("["):
        return json.loads(text)
    # Try to find an array inside.
    m = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    # Try JSON object containing an array under common keys.
    obj = json.loads(text)
    for key in ("rules", "detectors", "results", "items", "compilations"):
        if isinstance(obj, dict) and isinstance(obj.get(key), list):
            return obj[key]
    raise ValueError("could not extract a JSON array from LLM response")


def next_batch_path(sub_category: str) -> Path:
    """Compute batches/<slug>-NNN.json — auto-increment on collision."""
    BATCH_DIR.mkdir(exist_ok=True)
    base = slug(sub_category)
    n = 1
    while True:
        p = BATCH_DIR / f"batch_{n:03d}_{base}.json"
        if not p.exists():
            return p
        n += 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sub-category", required=True,
                    help="exact sub_category string (e.g. 'adverbs and adverb phrases: types and meanings')")
    ap.add_argument("--limit", type=int, default=15, help="max rows to compile (default 15)")
    ap.add_argument("--backend", choices=("crow", "openrouter"), default=DEFAULT_BACKEND,
                    help=f"LLM backend (default {DEFAULT_BACKEND}). "
                         f"crow = use `crow-cli run`. openrouter = POST to OpenRouter.")
    ap.add_argument("--model", default=None,
                    help="openrouter-only: model id or preset name (e.g. gemma-4-26b-free). "
                         "Ignored by the crow backend (model is set in crow-cli). "
                         f"Default if openrouter chosen: {DEFAULT_MODEL}. Presets: {PRESET_NAMES}")
    ap.add_argument("--api-key", default=os.environ.get("OPENROUTER_API_KEY"),
                    help="openrouter-only: OpenRouter API key (default: $OPENROUTER_API_KEY)")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=8192)
    ap.add_argument("--dry-run", action="store_true",
                    help="print the messages payload + write prompt.txt; do not call LLM")
    ap.add_argument("--out", type=Path, default=None, help="explicit output path; default auto-named")
    args = ap.parse_args()

    if not args.sub_category:
        print("error: --sub-category is required", file=sys.stderr)
        return 2

    # Resolve preset -> full model id (openrouter only)
    if args.backend == "openrouter":
        model = args.model or DEFAULT_MODEL
        if model in MODEL_PRESETS:
            model = MODEL_PRESETS[model]
            print(f"(resolved preset -> {model})")
        args.model = model

    print(f"=== FETCHING SLICE ===")
    slice_rows = fetch_slice(args.sub_category, args.limit)
    print(f"  {len(slice_rows)} rows for '{args.sub_category}'")
    if not slice_rows:
        print("  nothing pending for that sub-category — exiting", file=sys.stderr)
        return 4
    for r in slice_rows:
        print(f"    [{r['level']:<2}] {r['egp_id'][-14:]}  {r['guideword']}")

    # Compose prompt(s)
    if args.backend == "crow":
        prompt = build_single_prompt(slice_rows)
    else:
        messages = build_messages(slice_rows)
        prompt = ("SYSTEM:\n" + messages[0]["content"]
                  + "\n\nUSER:\n" + messages[1]["content"])

    if args.dry_run:
        out_prompt = BATCH_DIR / f"_prompt_{slug(args.sub_category)}_{uuid.uuid4().hex[:6]}.txt"
        out_prompt.write_text(prompt)
        print(f"  dry-run: wrote prompt -> {out_prompt}")
        return 0

    print(f"=== CALLING {args.backend.upper()} ===")
    if args.backend == "crow":
        print(f"  model: whatever crow-cli is configured for")
    else:
        if not args.api_key:
            print("error: OPENROUTER_API_KEY not set (or pass --api-key)", file=sys.stderr)
            return 5
        print(f"  model:       {args.model}")
        print(f"  temperature: {args.temperature}")
        print(f"  max_tokens:  {args.max_tokens}")

    # Dispatch
    last_err = None
    for attempt in range(2):
        try:
            t0 = time.time()
            if args.backend == "crow":
                content = call_crow(prompt)
            else:
                resp = call_openrouter(
                    api_key=args.api_key, model=args.model, messages=messages,
                    temperature=args.temperature, max_tokens=args.max_tokens,
                    referer=os.environ.get("OPENROUTER_REFERER", ""),
                    title=os.environ.get("OPENROUTER_TITLE", ""),
                )
                usage = resp.get("usage") or {}
                print(f"  response in {time.time()-t0:.1f}s; usage: {usage}")
                content = resp["choices"][0]["message"]["content"]
            print(f"  total {time.time()-t0:.1f}s")
            rules = extract_json_array(content)
            print(f"  parsed {len(rules)} rules from response")
            break
        except Exception as e:
            last_err = e
            print(f"  attempt {attempt + 1} failed: {e}", file=sys.stderr)
            time.sleep(2 ** attempt)
    else:
        print(f"all attempts failed; last error: {last_err}", file=sys.stderr)
        return 6

    out_path = args.out or next_batch_path(args.sub_category)
    out_path.write_text(json.dumps(rules, indent=1))
    print(f"=== WROTE {len(rules)} RULES -> {out_path} ===")
    print(f"next: python build_batch.py {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
