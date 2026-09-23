"""Plan D — Jules wave spawner.

Reads pending rows from egp_pipeline.db, slices them into batches of 15,
posts one Jules session per batch (AUTO_CREATE_PR) and tracks them in
data/jules_sessions.json.

Usage:
  python3 scripts/jules_spawn_wave.py --dry-run        # show batches, no API calls
  python3 scripts/jules_spawn_wave.py --spawn N        # spawn N sessions
  python3 scripts/jules_spawn_wave.py --status         # poll spawned sessions
Requires: JULES_CODER_API_KEY in env; repo connected to Jules.
"""

import argparse
import json
import os
import sqlite3
import time
import urllib.request
from pathlib import Path

EGP_DIR = Path("/home/hayron/MyProjects/EGP OBLITERATED")
DB = EGP_DIR / "egp_pipeline.db"
STATE = EGP_DIR / "data" / "jules_sessions.json"
API = "https://jules.googleapis.com/v1alpha"
BATCH_SIZE = 15
SOURCE = "sources/github/AiRonAndStudentLore/egp-obliterated"
BRANCH = "master"


def api_key():
    key = os.environ.get("JULES_CODER_API_KEY")
    if not key:
        # try to pull from bashrc
        try:
            for line in Path.home().joinpath(".bashrc").read_text().splitlines():
                if line.startswith("export JULES_CODER_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
        except OSError:
            pass
    if not key:
        raise SystemExit("JULES_CODER_API_KEY not found")
    return key


def call_api(path, method="GET", body=None):
    req = urllib.request.Request(
        f"{API}{path}",
        method=method,
        headers={
            "X-Goog-Api-Key": api_key(),
            "Content-Type": "application/json",
        },
        data=json.dumps(body).encode() if body else None,
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def pending_rows():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT egp_id, level, super_category, sub_category, lexical_range, "
        "guideword, can_do_statement, example_raw FROM rows "
        "WHERE status='pending' ORDER BY super_category, sub_category, egp_id"
    ).fetchall()
    con.close()
    return rows


def build_prompt(batch, batch_index):
    system = (EGP_DIR / "SYSTEM_PROMPT.txt").read_text()
    payload = json.dumps(
        [
            {
                "egp_id": r["egp_id"],
                "level": r["level"],
                "super_category": r["super_category"],
                "sub_category": r["sub_category"],
                "lexical_range": r["lexical_range"],
                "guideword": r["guideword"],
                "can_do_statement": r["can_do_statement"],
                "example_raw": r["example_raw"],
            }
            for r in batch
        ],
        indent=1,
    )
    return (
        f"{system}\n\n"
        f"## TASK\n"
        f"Compile detection rules for the {len(batch)} EGP rows below.\n\n"
        f"Create ONE file: `batches/jules_batch_{batch_index:03d}.json`\n"
        f"- A JSON array with exactly {len(batch)} objects, input order preserved.\n"
        f"- Each object = the input row (keep egp_id, level, super_category, sub_category, "
        f"lexical_range, guideword, can_do_statement unchanged) PLUS:\n"
        f'  - "detection": {{"regex_triage": "<regex string>", '
        f'"spacy_token_pattern": [<token dicts>]}}\n'
        f'  - "unit_tests": {{"positives": [2 example sentences], '
        f'"negatives": [2 near-miss sentences]}}\n'
        f"- Every regex_triage MUST compile with python re.compile — verify before "
        f"committing. Every spacy_token_pattern must be a flat list of token dicts.\n"
        f"- ABSOLUTE FILE SCOPE: your final change must be exactly ONE new file, "
        f"`batches/jules_batch_{batch_index:03d}.json`. Do NOT create, modify, or delete "
        f"any other file — not build_batch.py, gate.py, egp_compiled.json, README, or "
        f"scratch scripts. If you write helper scripts during development, delete them "
        f"so they never appear in the final diff.\n"
        f"- Do NOT run build_batch.py, gate.py, or egpObliterationVerify.py.\n\n"
        f"## ROWS\n```json\n{payload}\n```"
    )


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"sessions": []}


def save_state(state):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1))


def cmd_dry_run(args):
    rows = pending_rows()
    print(f"{len(rows)} pending rows -> {len(rows) // BATCH_SIZE} batches of {BATCH_SIZE}")
    for i in range(0, min(len(rows), args.limit * BATCH_SIZE), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        cats = sorted({(r["level"], r["sub_category"]) for r in batch})
        print(f"  batch_{i//BATCH_SIZE + 1}: {len(batch)} rows  {cats[0]}..")


def cmd_spawn(args):
    state = load_state()
    spawned = {s.get("batch_index") for s in state["sessions"]}
    rows = pending_rows()
    n_new = 0
    for i in range(0, len(rows), BATCH_SIZE):
        if n_new >= args.spawn:
            break
        batch_index = i // BATCH_SIZE
        if batch_index in spawned:
            continue
        batch = rows[i : i + BATCH_SIZE]
        prompt = build_prompt(batch)
        body = {
            "prompt": prompt,
            "sourceContext": {
                "source": SOURCE,
                "githubRepoContext": {"startingBranch": BRANCH},
            },
            "automationMode": "AUTO_CREATE_PR",
            "title": f"EGP batch {batch_index + 1} ({batch[0]['level']} {batch[0]['sub_category']})",
        }
        try:
            resp = call_api("/sessions", "POST", body)
        except urllib.error.HTTPError as e:
            print(f"batch_{batch_index + 1}: HTTP {e.code} {e.read()[:200]}")
            continue
        state["sessions"].append(
            {
                "batch_index": batch_index,
                "session_id": resp["id"],
                "name": resp["name"],
                "url": resp.get("url"),
                "state": resp.get("state"),
                "spawned_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "egp_ids": [r["egp_id"] for r in batch],
            }
        )
        n_new += 1
        print(f"batch_{batch_index + 1}: spawned session {resp['id']}")
        time.sleep(1)
    save_state(state)
    print(f"\nspawned {n_new} new sessions; total tracked: {len(state['sessions'])}")


def cmd_status(_args):
    state = load_state()
    active = 0
    for s in state["sessions"]:
        try:
            resp = call_api(f"/{s['name']}")
            s["state"] = resp.get("state")
            if resp.get("state") == "COMPLETED":
                s["outputs"] = resp.get("outputs", [])
            if resp.get("state") not in ("COMPLETED", "FAILED"):
                active += 1
            print(f"{s['name']}: {s['state']}" + (f"  PR: {s['outputs'][0]['pullRequest']['url']}" if s.get('outputs') else ""))
        except Exception as e:
            print(f"{s['name']}: ERROR {e}")
    save_state(state)
    print(f"\nactive: {active} / {len(state['sessions'])}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dry-run")
    d.add_argument("--limit", type=int, default=10)
    sub.add_parser("spawn").add_argument("--spawn", type=int, default=15)
    sub.add_parser("status")
    args = p.parse_args()
    {"dry-run": cmd_dry_run, "spawn": cmd_spawn, "status": cmd_status}[args.cmd](args)
