"""Spawn a wave of Jules sessions via CLI pipe mode.

Usage: python3 scripts/jules_spawn_wave_cli.py --from-batch 2 --count 15
Reads pending rows, builds prompt files, spawns one session per batch via
`jules remote new --repo ...` (pipe mode), records session IDs in
data/jules_cli_sessions.json immediately after each spawn (crash-safe).
"""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jules_spawn_wave import pending_rows, build_prompt, BATCH_SIZE, EGP_DIR

REPO = "AiRonAndStudentLore/egp-obliterated"
STATE = EGP_DIR / "data" / "jules_cli_sessions.json"
PROMPT_DIR = EGP_DIR / "batches" / "jules_prompts"


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"sessions": []}


def save_state(state):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-batch", type=int, default=1, help="1-based batch index to start at")
    ap.add_argument("--count", type=int, default=15)
    ap.add_argument("--repo", default=REPO)
    args = ap.parse_args()

    rows = pending_rows()
    state = load_state()
    spawned_ids = {s["batch_index"] for s in state["sessions"]}

    total_batches = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
    n_spawned = 0
    for b in range(args.from_batch - 1, total_batches):
        if n_spawned >= args.count:
            break
        if b in spawned_ids:
            print(f"batch_{b+1:03d}: already spawned, skip")
            continue
        batch = rows[b * BATCH_SIZE : (b + 1) * BATCH_SIZE]
        prompt = build_prompt(batch, b + 1)
        PROMPT_DIR.mkdir(exist_ok=True)
        prompt_file = PROMPT_DIR / f"batch_{b+1:03d}.txt"
        prompt_file.write_text(prompt)

        r = subprocess.run(
            ["jules", "remote", "new", "--repo", args.repo],
            stdin=prompt_file.open(),
            capture_output=True, text=True, timeout=120,
        )
        out = r.stdout + r.stderr
        m = re.search(r"ID:\s*(\d+)", out)
        if not m:
            print(f"batch_{b+1:03d}: SPAWN FAILED: {out[:300]}")
            continue
        sid = m.group(1)
        state["sessions"].append({
            "batch_index": b,
            "batch_file": f"batches/jules_batch_{b+1:03d}.json",
            "session_id": sid,
            "state": "SPAWNED",
            "fetched": False,
            "gated": None,
            "spawned_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "egp_ids": [r_["egp_id"] for r_ in batch],
        })
        save_state(state)  # immediate persistence — crash-safe
        n_spawned += 1
        print(f"batch_{b+1:03d}: session {sid} ({batch[0]['level']} {batch[0]['sub_category']})")
        time.sleep(1)

    print(f"\nspawned {n_spawned}; total tracked {len(state['sessions'])}")


if __name__ == "__main__":
    main()
