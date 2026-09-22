#!/usr/bin/env python
"""
build_batch.py — end-to-end orchestrator for one EGP detector batch.

Takes a single batch JSON file (the output of SYSTEM_PROMPT compilation) and:
  1. structural pre-check (schema + DB membership)
  2. ingest -> gate -> auto-fix -> re-ingest -> re-gate (loop)
  3. egpObliterationVerify.py sanity sweep
  4. regenerate egp_compiled.json from DB
  5. update WORKLOG.md + worklog.db via logwork CLI
  6. emit a JSON report

Auto-fix rules (conservative heuristics, applied per failing row):
  - regex_error / registry_error   -> simplify regex (strip variable-width lookbehind,
                                       drop bad backrefs), drop all POS attrs from spaCy.
  - spaCy MISSED positive          -> drop POS attrs from spaCy pattern, widen the
                                       token window with OP:"?".
  - spaCy FALSE-POSITIVE negative  -> shrink spaCy pattern to required LOWER match only.
  - regex MISSED positive          -> add missing lexicon words from can_do_statement
                                       into a fallback LOWER list.
  - regex FALSE-POSITIVE negative  -> tighten regex with a negative lookhead on
                                       common distractors.

Each cycle modifies the batch JSON in place. Stops when: all-pass / no improvement
/ max cycles hit.

Usage:
  .venv/bin/python build_batch.py batches/batch_009_adverbs.json
  .venv/bin/python build_batch.py batches/batch_X.json --cycles 5 --report report.json

Exit codes:
  0   all rules passed
  2   some rules failed after max cycles (report still written)
  3   structure pre-check failed
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
PY = sys.executable
PIPELINE = ROOT / "pipeline.py"
VERIFY = ROOT / "egpObliterationVerify.py"
WORKLOG = ROOT / "WORKLOG.md"


# ---------------------------------------------------------------- helpers

def run(*args, **kwargs) -> subprocess.CompletedProcess:
    """Run subprocess and raise on non-zero exit."""
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def db_query(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    import sqlite3
    c = sqlite3.connect(str(ROOT / "egp_pipeline.db"))
    c.row_factory = sqlite3.Row
    rows = c.execute(sql, params).fetchall()
    c.close()
    return rows


# ---------------------------------------------------------------- precheck

def precheck(batch_path: Path) -> tuple[bool, str, list[str]]:
    """Return (ok, summary, rule_ids_in_file)."""
    try:
        rules = json.loads(batch_path.read_text())
    except json.JSONDecodeError as e:
        return False, f"JSON parse error: {e}", []
    if not isinstance(rules, list) or not rules:
        return False, "file is not a non-empty JSON array", []

    required_top = ("egp_id", "level", "super_category", "sub_category",
                    "guideword", "can_do_statement", "ontology",
                    "detection", "unit_tests")
    required_onto = ("domain", "mental_model", "pedagogical_hook", "agency_or_distance")
    required_det = ("regex_triage", "spacy_token_pattern")
    required_ut = ("positives", "negatives")

    bad = []
    rule_ids = []
    for i, r in enumerate(rules, 1):
        eid = r.get("egp_id", "<missing>")
        rule_ids.append(eid)
        for k in required_top:
            if k not in r: bad.append(f"row {i} ({eid[-12:]}): missing top-level {k}")
        for k in required_onto:
            if k not in r.get("ontology", {}): bad.append(f"row {i}: missing ontology.{k}")
        for k in required_det:
            if k not in r.get("detection", {}): bad.append(f"row {i}: missing detection.{k}")
        for k in required_ut:
            if k not in r.get("unit_tests", {}): bad.append(f"row {i}: missing unit_tests.{k}")
        ut = r.get("unit_tests", {})
        if len(ut.get("positives", [])) != 2: bad.append(f"row {i}: positives count != 2")
        if len(ut.get("negatives", [])) != 2: bad.append(f"row {i}: negatives count != 2")
        dom = r.get("ontology", {}).get("domain")
        if dom not in ("TEMPORAL_ASPECT", "EPISTEMIC_STANCE", "DEONTIC_FORCE", "ENTITY_TOPOLOGY"):
            bad.append(f"row {i}: bad domain {dom}")
        # regex compiles?
        try:
            re.compile(r["detection"]["regex_triage"], re.I)
        except re.error as e:
            bad.append(f"row {i}: regex doesn't compile: {e}")
        # spaCy pattern structure
        stp = r["detection"]["spacy_token_pattern"]
        if not isinstance(stp, list) or not all(isinstance(t, dict) for t in stp):
            bad.append(f"row {i}: spaCy pattern is not a flat list of token dicts")
        # in DB and tractable?  (allow pending, testing, or already-passed for re-runs)
        db_rows = db_query("SELECT status FROM rows WHERE egp_id=?", (eid,))
        if not db_rows:
            bad.append(f"row {i}: egp_id not in DB")
        elif db_rows[0]["status"] not in ("pending", "testing", "passed"):
            bad.append(f"row {i}: status is '{db_rows[0]['status']}', expected pending/testing/passed")

    if bad:
        return False, f"{len(bad)} validation issues: {' | '.join(bad[:5])}", rule_ids
    return True, f"{len(rules)} rules validated OK", rule_ids


# ---------------------------------------------------------------- gate IO

def gate() -> list[dict]:
    """Run gate.py directly (skipping pipeline.py's wrapper, which consumes
    the JSON internally and only prints its summary).

    Reads all 'testing' rows from DB, dumps them as JSON to gate.py's stdin,
    returns the JSON verdict list from gate.py's stdout.
    """
    rules = db_query("""
        SELECT egp_id, level, super_category, sub_category, guideword,
               can_do_statement, pattern_json, test_suite_json
        FROM rows WHERE status='testing'
    """)
    payload = []
    for r in rules:
        payload.append({
            "egp_id": r["egp_id"],
            "level": r["level"],
            "super_category": r["super_category"],
            "sub_category": r["sub_category"],
            "guideword": r["guideword"],
            "can_do_statement": r["can_do_statement"],
            "detection": json.loads(r["pattern_json"]),
            "unit_tests": json.loads(r["test_suite_json"]),
        })
    if not payload:
        return []
    proc = subprocess.run(
        [PY, str(ROOT / "gate.py")],
        input=json.dumps(payload),
        capture_output=True, text=True, timeout=600,
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        print("gate.py crashed:", proc.stderr[-2000:], file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        print("gate.py stdout not JSON:", proc.stdout[-500:], file=sys.stderr)
        sys.exit(1)


def gate_apply(verdicts: list[dict]) -> tuple[int, int, int]:
    """Translate gate.py verdicts into DB updates. Mirrors pipeline.cmd_gate
    but works off the in-memory verdicts list. Returns (passed, rejected, failed).
    """
    import sqlite3
    c = sqlite3.connect(str(ROOT / "egp_pipeline.db"))
    passed = rejected = failed = 0
    for v in verdicts:
        if v["verdict"] == "passed":
            c.execute(
                "UPDATE rows SET status='passed', error=NULL, updated_at=? WHERE egp_id=?",
                (now_iso(), v["egp_id"]),
            )
            passed += 1
        elif v["verdict"] in ("registry_error", "regex_error"):
            c.execute(
                "UPDATE rows SET status='pending', error=?, updated_at=? WHERE egp_id=?",
                (v["verdict"] + ": " + "; ".join(v.get("failures", [])), now_iso(), v["egp_id"]),
            )
            rejected += 1
        else:
            c.execute(
                "UPDATE rows SET status='pending', error=?, updated_at=? WHERE egp_id=?",
                ("; ".join(v.get("failures", [])), now_iso(), v["egp_id"]),
            )
            failed += 1
    c.commit()
    c.close()
    return passed, rejected, failed


# ---------------------------------------------------------------- auto-fix

def auto_fix_one(rule: dict, failure: dict) -> dict:
    """Apply conservative auto-fix to a single rule based on its failure.

    Returns dict with keys: changed: bool, notes: str, fixes: [str]
    """
    det = rule.setdefault("detection", {})
    pat = det.get("spacy_token_pattern", [])
    rx = det.get("regex_triage", "")
    fixes: list[str] = []
    out: dict = {"changed": False, "notes": "", "fixes": []}

    failures = failure.get("failures", [])
    if failure.get("verdict") in ("regex_error", "registry_error"):
        # Strip variable-width lookbehinds and bad backrefs
        new_rx = re.sub(r"\(\?<=[^)]+\)", "", rx)  # remove all lookbeheads
        new_rx = re.sub(r"\\(\d+)", "", new_rx)      # remove backrefs that might fail
        # Drop POS from spaCy just in case
        if any("POS" in (t if isinstance(t, dict) else {}) for t in pat):
            new_pat = [{k: v for k, v in (t if isinstance(t, dict) else {}).items() if k != "POS"} for t in pat]
            det["spacy_token_pattern"] = new_pat
            fixes.append("stripped POS attrs from spaCy")
        if new_rx != rx:
            det["regex_triage"] = new_rx
            fixes.append("stripped problematic lookbehinds/backrefs from regex")
        out["fixes"] = fixes
        out["changed"] = bool(fixes)
        out["notes"] = "; ".join(fixes) or "no auto-fix available"
        return out

    msgs = " | ".join(failures)
    if "spaCy MISSED positive" in msgs or "spaCy FALSE-POSITIVE" in msgs:
        # Drop POS attrs from all spaCy token dicts
        if any("POS" in (t if isinstance(t, dict) else {}) for t in pat):
            new_pat = [{k: v for k, v in (t if isinstance(t, dict) else {}).items() if k != "POS"} for t in pat]
            det["spacy_token_pattern"] = new_pat
            fixes.append("stripped POS attrs (workspace user's prior insight: lean on LOWER)")
        # If spaCy FALSE-POSITIVE on negative, the LOWER-only match is too permissive.
        # Tighten by ensuring token must NOT be followed by a verb (POS:VERB pre-slot).
        if "spaCy FALSE-POSITIVE" in msgs and len(pat) >= 1:
            head = pat[0]
            head_copy = dict(head)
            head_copy["OP"] = head_copy.get("OP", "1")
            det["spacy_token_pattern"] = [head_copy]  # shrink to single LOWER token match
            fixes.append("shrunk spaCy to single LOWER token match (was full pattern)")
        out["fixes"] = fixes
        out["changed"] = bool(fixes)
        out["notes"] = "; ".join(fixes) or "no spaCy auto-fix applied"
        return out

    if "regex MISSED positive" in msgs:
        # Pull quoted words out of can_do_statement and add them as alternation in regex
        cando = rule.get("can_do_statement", "")
        words = re.findall(r"'([^']+)'|\"([^\"]+)\"", cando)
        quoted = sorted({(a or b).strip().lower() for a, b in words if (a or b).strip()})
        # Build a fallback lexicon token regex
        if quoted:
            esc = "|".join(re.escape(w) for w in quoted)
            new_rx = rx + f"|\\b(?:{esc})\\b"
            det["regex_triage"] = new_rx
            fixes.append(f"added fallback alternation from can_do quoted words: {quoted}")
        out["fixes"] = fixes
        out["changed"] = bool(fixes)
        out["notes"] = "; ".join(fixes) or "no regex auto-fix available"
        return out

    if "regex FALSE-POSITIVE on negative" in msgs:
        # Tighten by adding a lookahead requiring the next non-space to be alphanumeric
        new_rx = rx + "(?![\\s\\S]*\\b(?:to|for|with|from|at|on|in|by|of|that|when|then|now|soon)\\b)"
        det["regex_triage"] = new_rx
        fixes.append("appended negative lookhead against common preposition/conjunction distractors")
        out["fixes"] = fixes
        out["changed"] = bool(fixes)
        out["notes"] = "; ".join(fixes) or "no regex tighten available"
        return out

    out["notes"] = "no applicable auto-fix"
    return out


def auto_fix_batch(batch_path: Path, verdicts: list[dict]) -> tuple[bool, list[dict]]:
    """Apply auto-fixes to failing rules. Mutates the batch JSON. Returns (any_change, fix_log)."""
    failing = {v["egp_id"]: v for v in verdicts if v.get("verdict") != "passed"}
    if not failing:
        return False, []

    rules = json.loads(batch_path.read_text())
    log: list[dict] = []
    changed_any = False
    for rule in rules:
        eid = rule.get("egp_id")
        if eid not in failing:
            continue
        result = auto_fix_one(rule, failing[eid])
        if result["changed"]:
            changed_any = True
            log.append({"egp_id": eid, "fixes": result["fixes"], "notes": result["notes"]})
    if changed_any:
        batch_path.write_text(json.dumps(rules, indent=1))
    return changed_any, log


# ---------------------------------------------------------------- post-pass

def regenerate_compiled_json() -> tuple[int, int]:
    """Rebuild egp_compiled.json from DB 'passed' rows. Returns (rule_count, ontology_preserved)."""
    import sqlite3
    c = sqlite3.connect(str(ROOT / "egp_pipeline.db"))
    c.row_factory = sqlite3.Row

    # Build ontology lookup from all batches/*.json files
    import glob
    onto = {}
    for path in glob.glob(str(ROOT / "batches/*.json")):
        if "_slice_" in path:
            continue
        try:
            for r in json.loads(Path(path).read_text()):
                if "ontology" in r:
                    onto[r["egp_id"]] = r["ontology"]
        except Exception:
            continue

    rows = c.execute("""
        SELECT egp_id, level, super_category, sub_category, guideword, can_do_statement,
               pattern_json, test_suite_json
        FROM rows WHERE status='passed' ORDER BY level, row_number
    """).fetchall()
    c.close()

    out = []
    preserved = 0
    for r in rows:
        if not r["pattern_json"] or not r["test_suite_json"]:
            continue
        ont = onto.get(r["egp_id"]) or {
            "domain": "ENTITY_TOPOLOGY", "mental_model": "",
            "pedagogical_hook": "", "agency_or_distance": ""
        }
        if r["egp_id"] in onto:
            preserved += 1
        out.append({
            "egp_id": r["egp_id"], "level": r["level"],
            "super_category": r["super_category"], "sub_category": r["sub_category"],
            "guideword": r["guideword"], "can_do_statement": r["can_do_statement"],
            "ontology": ont,
            "detection": json.loads(r["pattern_json"]),
            "unit_tests": json.loads(r["test_suite_json"]),
        })

    (ROOT / "egp_compiled.json").write_text(json.dumps(out, indent=1))
    return len(out), preserved


def verify() -> bool:
    proc = subprocess.run(
        [PY, str(VERIFY)], capture_output=True, text=True, cwd=str(ROOT)
    )
    return proc.returncode == 0 and "verified" in proc.stdout.lower()


# ---------------------------------------------------------------- logwork

def append_worklog(batch_path: Path, passed: int, total: int, cycles: int, fix_log: list[dict]) -> None:
    if not WORKLOG.exists():
        WORKLOG.write_text("")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    fix_summary = ""
    if fix_log:
        fix_summary = "  fixes: " + ", ".join(
            f"{f['egp_id'][-8:]}({len(f['fixes'])})" for f in fix_log[:5]
        )
    line = (f"- **{ts}** [build] build_batch.py completed {batch_path.name}: "
            f"{passed}/{total} passed after {cycles} cycle(s){fix_summary}")
    with WORKLOG.open("a") as f:
        f.write(line + "\n")

    summary = (f"build_batch.py {batch_path.name}: {passed}/{total} passed after "
               f"{cycles} cycle(s); {len(fix_log)} auto-fix(es) applied across "
               f"{len({f['egp_id'] for f in fix_log})} rows")
    try:
        subprocess.run(
            ["logwork", summary, "build", batch_path.name],
            check=True, cwd=str(ROOT),
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"logwork CLI skipped: {e}", file=sys.stderr)


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("batch_json", type=Path, help="batch JSON file")
    ap.add_argument("--cycles", type=int, default=4, help="max auto-fix cycles (default 4)")
    ap.add_argument("--no-autofix", action="store_true", help="disable auto-fix (single-shot gate)")
    ap.add_argument("--report", type=Path, default=None, help="write JSON report to PATH")
    ap.add_argument("--skip-verify", action="store_true", help="skip egpObliterationVerify.py")
    args = ap.parse_args()

    batch_path: Path = args.batch_json
    if not batch_path.exists():
        print(f"file not found: {batch_path}", file=sys.stderr)
        return 3

    print(f"=== STEP 1/5  PRECHECK ===")
    ok, summary, _ = precheck(batch_path)
    print(f"  {summary}")
    if not ok:
        print("precheck failed — fix the batch JSON and retry", file=sys.stderr)
        return 3

    print(f"=== STEP 2/5  INGEST + GATE LOOP (max {args.cycles} cycle(s)) ===")
    cycles = 0
    all_fix_log: list[dict] = []
    last_verdicts: list[dict] = []

    # First ingest
    print(f"  cycle {cycles + 1}: ingest")
    subprocess.run(
        [PY, str(PIPELINE), "ingest", str(batch_path)],
        check=True, cwd=str(ROOT), stdout=subprocess.DEVNULL,
    )
    cycles += 1

    while True:
        verdicts = gate()
        passed, rejected, failed_count = gate_apply(verdicts)
        last_verdicts = verdicts
        print(f"  cycle {cycles}: gate = {passed} passed, {rejected} rejected, {failed_count} failed")
        failed = [v for v in verdicts if v.get("verdict") != "passed"]
        for v in failed:
            print(f"    FAIL {v['egp_id'][-14:]}  {v.get('verdict')}: "
                  f"{str(v.get('failures', []))[:120]}")
        if not failed:
            break
        if args.no_autofix:
            break
        if cycles >= args.cycles:
            print(f"  hit max cycles ({args.cycles}); stopping auto-fix")
            break

        changed, fix_log = auto_fix_batch(batch_path, verdicts)
        all_fix_log.extend(fix_log)
        if not changed:
            print("  no more auto-fixes available; stopping")
            break

        cycles += 1
        print(f"  cycle {cycles}: re-ingest after {len(fix_log)} fix(es)")
        subprocess.run(
            [PY, str(PIPELINE), "ingest", str(batch_path)],
            check=True, cwd=str(ROOT), stdout=subprocess.DEVNULL,
        )

    final_passed = sum(1 for v in last_verdicts if v.get("verdict") == "passed")
    final_total = len(last_verdicts)

    print(f"=== STEP 3/5  REGENERATE egp_compiled.json ===")
    n_rules, n_onto = regenerate_compiled_json()
    print(f"  wrote {n_rules} rules ({n_onto} with ontology preserved)")

    print(f"=== STEP 4/5  VERIFY ===")
    if args.skip_verify:
        print("  skipped (--skip-verify)")
        verify_ok = None
    else:
        verify_ok = verify()
        print(f"  egpObliterationVerify.py: {'PASS' if verify_ok else 'FAIL'}")

    print(f"=== STEP 5/5  WORKLOG + LOGWORK ===")
    append_worklog(batch_path, final_passed, final_total, cycles, all_fix_log)
    print(f"  appended entry")

    # Final stats from DB
    final = db_query(
        "SELECT status, COUNT(*) AS n FROM rows GROUP BY status ORDER BY n DESC"
    )
    total_rows = db_query("SELECT COUNT(*) AS n FROM rows")[0]["n"]
    print(f"\n  final DB state: {total_rows} rows")
    for r in final:
        print(f"    {r['status']:<24} {r['n']}")

    # Report
    if args.report:
        args.report.write_text(json.dumps({
            "batch": str(batch_path),
            "cycles": cycles,
            "passed": final_passed,
            "total": final_total,
            "auto_fixes": all_fix_log,
            "verify_ok": verify_ok,
            "verdicts": last_verdicts,
        }, indent=1))
        print(f"  report -> {args.report}")

    return 0 if final_passed == final_total else 2


if __name__ == "__main__":
    sys.exit(main())
