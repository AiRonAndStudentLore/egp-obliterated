"""Dispatch flagged rules to Jules for pattern fixes, with judge evidence.

Reads data/redeliver_egp_ids.json; for each rule includes: current detection,
corpus hit sentences (the ones both judges saw), and judge verdicts.
Jules writes batches/jules_fix_batch_N.json with corrected rules.
"""

import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jules_fetch_patch import fetch_activities

EGP_DIR = Path("/home/hayron/MyProjects/EGP OBLITERATED")
DATA = EGP_DIR / "data"
STATE = DATA / "jules_fix_sessions.json"
PROMPT_DIR = EGP_DIR / "batches" / "fix_prompts"
REPO = "AiRonAndStudentLore/egp-obliterated"
PER_SESSION = 9


def build_prompts():
    rules = {r["egp_id"]: r for r in json.loads((EGP_DIR / "egp_compiled.json").read_text())}
    agreement = json.loads((DATA / "label_agreement.json").read_text())["rules"]
    redeliver = json.loads((DATA / "redeliver_egp_ids.json").read_text())

    hits = {}
    for line in (DATA / "train_corpus.jsonl").open():
        ex = json.loads(line)
        for l in ex["labels"]:
            hits.setdefault(l, []).append(ex["text"])

    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    chunks = [redeliver[i:i + PER_SESSION] for i in range(0, len(redeliver), PER_SESSION)]
    for i, chunk in enumerate(chunks, 1):
        rows = []
        for eid in chunk:
            r = rules[eid]
            a = agreement.get(eid, {})
            rows.append({
                "egp_id": eid,
                "level": r["level"],
                "sub_category": r["sub_category"],
                "guideword": r["guideword"],
                "can_do_statement": r["can_do_statement"],
                "current_regex_triage": r["detection"]["regex_triage"],
                "current_spacy_token_pattern": r["detection"]["spacy_token_pattern"],
                "sentences_rule_matched": (hits.get(eid) or [])[:8],
                "judge1_false_positive_rate": a.get("false_positive_rate"),
                "judge1_blind_spot_rate": a.get("blind_spot_rate"),
                "judge2_false_positive_rate": a.get("pro_false_positive_rate"),
                "judge2_blind_spot_rate": a.get("pro_blind_spot_rate"),
            })
        prompt = (
            "You are fixing over-broad ESL grammar detector rules. Two independent judges "
            "reviewed the sentences each rule currently matches and CONCUR the rule is wrong.\n\n"
            "For each rule below:\n"
            "1. Read can_do_statement — the ONLY thing the rule should detect.\n"
            "2. Read sentences_rule_matched — judges say these should NOT all match.\n"
            "3. Rewrite regex_triage (python re.compile-able) and spacy_token_pattern "
            "(flat token dicts; prefer LOWER anchors; use OP for optional slots) so the "
            "rule matches ONLY genuine demonstrations of the can-do, including learner "
            "variants ('I see you soon' without future marker is still 'see you soon').\n"
            "4. unit_tests: 2 positives (MUST match) + 2 negatives with overlapping "
            "vocabulary (MUST NOT match). Choose positives that satisfy the judges' standard.\n\n"
            f"Write ONE file: `batches/jules_fix_batch_{i:03d}.json` — JSON array, one object "
            "per rule in input order, each = {egp_id, detection: {regex_triage, "
            "spacy_token_pattern}, unit_tests: {positives: [2], negatives: [2]}}.\n"
            "ABSOLUTE: exactly one new file, nothing else touched. Do not run any scripts.\n\n"
            "## RULES\n```json\n" + json.dumps(rows, indent=1) + "\n```"
        )
        (PROMPT_DIR / f"fix_batch_{i:03d}.txt").write_text(prompt)
    print(f"built {len(chunks)} fix-session prompts")
    return len(chunks)


def spawn():
    state = {"sessions": []}
    if STATE.exists():
        state = json.loads(STATE.read_text())
    existing = {s["fix_index"] for s in state["sessions"]}
    prompts = sorted(PROMPT_DIR.glob("fix_batch_*.txt"))
    for pf in prompts:
        idx = int(re.search(r"(\d+)", pf.stem).group(1))
        if idx in existing:
            continue
        r = subprocess.run(["jules", "remote", "new", "--repo", REPO],
                           stdin=pf.open(), capture_output=True, text=True, timeout=120)
        m = re.search(r"ID:\s*(\d+)", r.stdout + r.stderr)
        if not m:
            print(f"fix_batch_{idx:03d}: spawn failed: {(r.stdout+r.stderr)[:150]}")
            continue
        state["sessions"].append({
            "fix_index": idx, "session_id": m.group(1), "state": "SPAWNED",
            "output": f"batches/jules_fix_batch_{idx:03d}.json",
            "fetched": False, "spawned_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        })
        print(f"fix_batch_{idx:03d}: session {m.group(1)}")
        time.sleep(1)
        STATE.write_text(json.dumps(state, indent=1))
    print(f"spawned sessions: {len(state['sessions'])}")


def harvest():
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
    state = json.loads(STATE.read_text())
    for s in state["sessions"]:
        if s["state"] == "COMPLETED" and s.get("fetched"):
            continue
        req = urllib.request.Request(
            f"https://jules.googleapis.com/v1alpha/sessions/{s['session_id']}",
            headers={"X-Goog-Api-Key": key})
        st = json.loads(urllib.request.urlopen(req, timeout=30).read()).get("state")
        s["state"] = st
        if st != "COMPLETED":
            print(f"fix_{s['fix_index']:03d}: {st}")
            continue
        pf = f"/tmp/opencode/jules_fix_{s['fix_index']:03d}.patch"
        subprocess.run([sys.executable, str(Path(__file__).parent / "jules_fetch_patch.py"),
                        s["session_id"], pf], capture_output=True, text=True)
        num = subprocess.run(["git", "apply", "--numstat", pf], cwd=EGP_DIR,
                             capture_output=True, text=True).stdout
        paths = [l.split("\t")[-1] for l in num.splitlines() if l.strip()]
        if not all(p.startswith("batches/") for p in paths):
            s["fetched"] = True
            print(f"fix_{s['fix_index']:03d}: REJECTED touches {paths}")
            continue
        app = subprocess.run(["git", "apply", pf], cwd=EGP_DIR, capture_output=True, text=True)
        ok = (EGP_DIR / s["output"]).exists()
        s["fetched"] = ok
        print(f"fix_{s['fix_index']:03d}: {'OK' if ok else 'OUTPUT MISSING'}")
    STATE.write_text(json.dumps(state, indent=1))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--spawn", action="store_true")
    ap.add_argument("--harvest", action="store_true")
    a = ap.parse_args()
    if a.build:
        build_prompts()
    if a.spawn:
        spawn()
    if a.harvest:
        harvest()
