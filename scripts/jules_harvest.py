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


def gate_batch(batch_file):
    r = subprocess.run(
        [sys.executable, "build_batch.py", batch_file, "--no-autofix",
         "--report", str(EGP_DIR / "batches" / f"_report_{Path(batch_file).stem}.json")],
        cwd=EGP_DIR, capture_output=True, text=True, timeout=300,
    )
    out = r.stdout
    passed = "PRECHECK" in out
    # parse "cycle 1: gate = N passed" from output
    import re as _re
    m = _re.search(r"gate = (\d+) passed, (\d+) rejected, (\d+) failed", out)
    if m:
        return {"p": int(m.group(1)), "rej": int(m.group(2)), "f": int(m.group(3))}
    return None


def harvest_once(refill=0):
    state = load_state()
    completed = failed = in_flight = 0
    for s in state["sessions"]:
        if s.get("state") in TERMINAL and s.get("gated") is not None:
            continue  # already done
        try:
            st = session_state(s["session_id"])
        except Exception as e:
            print(f"batch_{s['batch_index']+1:03d}: poll error {e}")
            continue
        s["state"] = st
        if st == "COMPLETED":
            completed += 1
            patch_file = f"/tmp/opencode/jules_batch_{s['batch_index']+1:03d}.patch"
            try:
                acts = fetch_activities(s["session_id"])
                # reuse fetch_activities? it prints; simpler: call internal
            except SystemExit:
                pass
            try:
                subprocess.run(
                    [sys.executable, str(Path(__file__).parent / "jules_fetch_patch.py"),
                     s["session_id"], patch_file],
                    capture_output=True, text=True, timeout=60,
                )
                r = subprocess.run(["git", "apply", "--check", patch_file], cwd=EGP_DIR,
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    r = subprocess.run(["git", "apply", "--3way", patch_file], cwd=EGP_DIR,
                                       capture_output=True, text=True)
                else:
                    subprocess.run(["git", "apply", patch_file], cwd=EGP_DIR, check=True)
                bf = s["batch_file"]
                if (EGP_DIR / bf).exists():
                    g = gate_batch(bf)
                    s["gated"] = g
                    s["fetched"] = True
                    print(f"batch_{s['batch_index']+1:03d}: COMPLETED -> gate {g}")
                else:
                    s["gated"] = {"error": "batch file missing after apply"}
                    print(f"batch_{s['batch_index']+1:03d}: COMPLETED but {bf} missing!")
            except subprocess.CalledProcessError as e:
                s["gated"] = {"error": f"apply/patch error: {e.stderr[:200]}"}
                print(f"batch_{s['batch_index']+1:03d}: patch apply failed")
        elif st == "FAILED":
            failed += 1
            s["gated"] = {"error": "session FAILED"}
            print(f"batch_{s['batch_index']+1:03d}: FAILED")
        else:
            in_flight += 1
    save_state(state)
    print(f"\nsummary: completed={completed} failed={failed} in_flight={in_flight}")

    if refill > 0:
        done_batches = {s["batch_index"] for s in state["sessions"]}
        rows = pending_rows()
        total = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
        from jules_spawn_wave_cli import build_prompt as bp  # same builder
        n = 0
        for b in range(total):
            if n >= refill:
                break
            if b in done_batches:
                continue
            batch = rows[b * BATCH_SIZE:(b + 1) * BATCH_SIZE]
            prompt = build_prompt(batch, b + 1)
            pf = PROMPT_DIR / f"batch_{b+1:03d}.txt"
            PROMPT_DIR.mkdir(exist_ok=True)
            pf.write_text(prompt)
            r = subprocess.run(["jules", "remote", "new", "--repo", REPO],
                               stdin=pf.open(), capture_output=True, text=True, timeout=120)
            import re as _re
            m = _re.search(r"ID:\s*(\d+)", r.stdout + r.stderr)
            if not m:
                print(f"batch_{b+1:03d}: refill spawn failed: {(r.stdout+r.stderr)[:150]}")
                continue
            state["sessions"].append({
                "batch_index": b, "batch_file": f"batches/jules_batch_{b+1:03d}.json",
                "session_id": m.group(1), "state": "SPAWNED", "fetched": False,
                "gated": None, "spawned_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "egp_ids": [x["egp_id"] for x in batch],
            })
            save_state(state)
            n += 1
            print(f"batch_{b+1:03d}: refilled session {m.group(1)}")
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
            print("=" * 60)
            time.sleep(args.watch)
    else:
        harvest_once(refill=args.refill)
