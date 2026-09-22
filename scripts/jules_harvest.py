"""Harvest loop for Jules rule-farm sessions.

Polls all spawned sessions in data/jules_cli_sessions.json:
  COMPLETED -> fetch final patch -> git apply -> validate JSON -> report
  FAILED    -> mark dead, record egp_ids for manual rescue
Slots freed by completion can be refilled with --refill N (spawns next pending batches).

Usage:
  python3 scripts/jules_harvest.py                 # poll + fetch + gate once
  python3 scripts/jules_harvest.py --watch 120     # loop every 120s
  python3 scripts/jules_harvest.py --refill 5      # also spawn 5 next batches after harvest
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jules_fetch_patch import fetch_activities
from jules_spawn_wave import EGP_DIR, pending_rows, build_prompt, BATCH_SIZE
from jules_spawn_wave_cli import STATE, PROMPT_DIR, load_state, save_state, REPO

TERMINAL = {"COMPLETED", "FAILED"}


def session_state(sid):
    import os
    import urllib.request
    key = os.environ.get("JULES_CODER_API_KEY")
    if not key:
        for line in Path.home().joinpath(".bashrc").read_text().splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if line.startswith("JULES_CODER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    req = urllib.request.Request(
        f"https://jules.googleapis.com/v1alpha/sessions/{sid}",
        headers={"X-Goog-Api-Key": key},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read()).get("state")


ALLOWED_PREFIXES = ("batches/",)


def patch_is_safe(patch_file):
    """Reject patches that touch anything outside batches/ (deletion guard)."""
    r = subprocess.run(["git", "apply", "--numstat", patch_file], cwd=EGP_DIR,
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            path = parts[2]
            if not path.startswith(ALLOWED_PREFIXES):
                return False, path
    return True, None


def gate_batch(batch_file, egp_ids):
    """Run build_batch, then read the report JSON for THIS batch's egp_ids only.
    (build_batch re-verifies the whole registry each run; stdout aggregates.)"""
    stem = Path(batch_file).stem
    report = EGP_DIR / "batches" / f"_report_{stem}.json"
    r = subprocess.run(
        [sys.executable, "build_batch.py", batch_file, "--no-autofix",
         "--report", str(report)],
        cwd=EGP_DIR, capture_output=True, text=True, timeout=600,
    )
    if not report.exists():
        return {"error": f"no report; stderr: {r.stderr[-300:]}"}
    rep = json.loads(report.read_text())
    want = set(egp_ids)
    p = rej = f_ = 0
    rows = rep.get("verdicts", [])
    for row in rows:
        if row.get("egp_id") not in want:
            continue
        verdict = (row.get("verdict") or row.get("gate") or row.get("status") or "").lower()
        if "pass" in verdict:
            p += 1
        elif "reject" in verdict:
            rej += 1
        else:
            f_ += 1
    return {"p": p, "rej": rej, "f": f_}


def harvest_once(refill=0):
    state = load_state()
    completed = failed = in_flight = 0
    for s in state["sessions"]:
        gated = s.get("gated")
        already_done = (
            s.get("state") in TERMINAL
            and gated is not None
            and "error" not in str(gated)
        )
        if already_done:
            continue  # clean terminal state; errors retry
        try:
            st = session_state(s["session_id"])
        except Exception as e:
            print(f"batch_{s['batch_index']+1:03d}: poll error {e}", flush=True)
            continue
        s["state"] = st
        if st == "COMPLETED":
            completed += 1
            patch_file = f"/tmp/opencode/jules_batch_{s['batch_index']+1:03d}.patch"
            try:
                subprocess.run(
                    [sys.executable, str(Path(__file__).parent / "jules_fetch_patch.py"),
                     s["session_id"], patch_file],
                    capture_output=True, text=True, timeout=60,
                )
                safe, bad_path = patch_is_safe(patch_file)
                if not safe:
                    s["gated"] = {"error": f"patch rejected: touches {bad_path}"}
                    print(f"batch_{s['batch_index']+1:03d}: PATCH REJECTED (touches {bad_path})")
                    continue
                r = subprocess.run(["git", "apply", "--check", patch_file], cwd=EGP_DIR,
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    r = subprocess.run(["git", "apply", "--3way", patch_file], cwd=EGP_DIR,
                                       capture_output=True, text=True)
                else:
                    subprocess.run(["git", "apply", patch_file], cwd=EGP_DIR, check=True)
                bf = s["batch_file"]
                ok, reason = False, None
                if not (EGP_DIR / bf).exists():
                    reason = "batch file missing after apply"
                else:
                    try:
                        parsed = json.loads((EGP_DIR / bf).read_text())
                        if not isinstance(parsed, list) or len(parsed) != len(s["egp_ids"]):
                            reason = f"rule count mismatch: {len(parsed) if isinstance(parsed, list) else '?'} != {len(s['egp_ids'])}"
                        else:
                            ok = True
                    except json.JSONDecodeError as e:
                        reason = f"invalid JSON: {e}"
                if ok:
                    g = gate_batch(bf, s["egp_ids"])
                    s["gated"] = g
                    s["fetched"] = True
                    print(f"batch_{s['batch_index']+1:03d}: COMPLETED -> gate {g}", flush=True)
                else:
                    s["gated"] = {"error": reason}
                    s["fetched"] = True
                    print(f"batch_{s['batch_index']+1:03d}: VERIFICATION FAILED: {reason}", flush=True)
            except subprocess.CalledProcessError as e:
                s["gated"] = {"error": f"apply/patch error: {e.stderr[:200]}"}
                print(f"batch_{s['batch_index']+1:03d}: patch apply failed", flush=True)
        elif st == "FAILED":
            failed += 1
            s["gated"] = {"error": "session FAILED"}
            print(f"batch_{s['batch_index']+1:03d}: FAILED", flush=True)
        else:
            in_flight += 1
    save_state(state)
    print(f"\nsummary: completed={completed} failed={failed} in_flight={in_flight}", flush=True)

    if refill > 0:
        state = load_state()
        assigned = {e for s in state["sessions"] for e in s.get("egp_ids", [])}
        rows = [r for r in pending_rows() if r["egp_id"] not in assigned]
        n = 0
        next_index = max(s["batch_index"] for s in state["sessions"]) + 1
        for i in range(0, len(rows), BATCH_SIZE):
            if n >= refill:
                break
            b = next_index
            next_index += 1
            batch = rows[i : i + BATCH_SIZE]
            prompt = build_prompt(batch, b + 1)
            pf = PROMPT_DIR / f"batch_{b+1:03d}.txt"
            PROMPT_DIR.mkdir(exist_ok=True)
            pf.write_text(prompt)
            r = subprocess.run(["jules", "remote", "new", "--repo", REPO],
                               stdin=pf.open(), capture_output=True, text=True, timeout=120)
            import re as _re
            m = _re.search(r"ID:\s*(\d+)", r.stdout + r.stderr)
            if not m:
                print(f"batch_{b+1:03d}: refill spawn failed: {(r.stdout+r.stderr)[:150]}", flush=True)
                continue
            state["sessions"].append({
                "batch_index": b, "batch_file": f"batches/jules_batch_{b+1:03d}.json",
                "session_id": m.group(1), "state": "SPAWNED", "fetched": False,
                "gated": None, "spawned_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "egp_ids": [x["egp_id"] for x in batch],
            })
            save_state(state)
            n += 1
            print(f"batch_{b+1:03d}: refilled session {m.group(1)}", flush=True)
            time.sleep(2)
    return state


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", type=int, default=0, help="loop every N seconds")
    ap.add_argument("--refill", type=int, default=0)
    args = ap.parse_args()
    if args.watch:
        while True:
            harvest_once(refill=args.refill)
            print("=" * 60, flush=True)
            time.sleep(args.watch)
    else:
        harvest_once(refill=args.refill)
