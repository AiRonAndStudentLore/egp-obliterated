"""
EGP Obliteration pipeline — Excel row-by-row -> SQLite -> compiled rules -> Execution Gate.

Status lifecycle:
  pending                row compiled? no (or rejected back from gate)
  testing                pattern + test_suite ingested, awaiting gate verdict
  passed                 Execution Gate green (regex + spaCy, positives AND negatives)
  unmatchable_pragmatic  human-marked: pattern space can't express the can-do pragmatics

Usage:
  .venv/bin/python pipeline.py init                    # seed DB from Excel (row-by-row)
  .venv/bin/python pipeline.py stats                   # status counts
  .venv/bin/python pipeline.py next 15                 # print next pending batch (SYSTEM_PROMPT input)
  .venv/bin/python pipeline.py ingest batches/x.json   # upsert patterns, status -> testing
  .venv/bin/python pipeline.py gate                    # run Execution Gate on all testing rows (subprocess)
  .venv/bin/python pipeline.py show <status>           # list rows with that status
  .venv/bin/python pipeline.py mark <egp_id> unmatchable_pragmatic
"""
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import openpyxl

DB_PATH = Path(__file__).parent / "egp_pipeline.db"
EXCEL_PATH = Path("/home/hayron/MyProjects/English Grammar Profile Online.xlsx")
GATE = Path(__file__).parent / "gate.py"
PY = sys.executable

SCHEMA = """
CREATE TABLE IF NOT EXISTS rows (
    egp_id           TEXT PRIMARY KEY,
    row_number       INTEGER,
    level            TEXT,
    super_category   TEXT,
    sub_category     TEXT,
    lexical_range    TEXT,
    guideword        TEXT,
    can_do_statement TEXT,
    example_raw      TEXT,
    status           TEXT NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending','testing','passed','unmatchable_pragmatic')),
    pattern_json     TEXT,
    test_suite_json  TEXT,
    error            TEXT,
    updated_at       TEXT
);
CREATE INDEX IF NOT EXISTS idx_rows_status ON rows(status);
"""


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------- commands

def cmd_init() -> None:
    wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True)
    ws = wb["Data"]
    header = None
    conn = db()
    conn.executescript(SCHEMA)
    seeded = 0
    for row_number, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if header is None:
            header = [str(c).strip() if c else "" for c in row]
            continue
        rec = dict(zip(header, row))
        conn.execute(
            """INSERT OR IGNORE INTO rows
               (egp_id, row_number, level, super_category, sub_category,
                lexical_range, guideword, can_do_statement, example_raw, status, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?, 'pending', ?)""",
            (
                str(rec["id"]),
                row_number,
                rec["Level"],
                rec["SuperCategory"],
                rec["SubCategory"],
                str(rec["Lexical Range"]),
                rec["Guideword"],
                rec["Can-do statement"],
                rec["Example"],
                now(),
            ),
        )
        seeded += 1
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM rows").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM rows WHERE status='pending'").fetchone()[0]
    print(f"Excel rows processed: {seeded}")
    print(f"DB rows total: {total}  pending: {pending}")
    conn.close()


def cmd_stats() -> None:
    conn = db()
    rows = conn.execute(
        "SELECT status, COUNT(*) AS n FROM rows GROUP BY status ORDER BY n DESC"
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM rows").fetchone()[0]
    print(f"total: {total}")
    for r in rows:
        print(f"  {r['status']:<24} {r['n']}")
    conn.close()


def cmd_next(n: int) -> None:
    conn = db()
    rows = conn.execute(
        """SELECT egp_id, level, super_category, sub_category, lexical_range,
                  guideword, can_do_statement, example_raw
           FROM rows WHERE status='pending' ORDER BY row_number LIMIT ?""",
        (n,),
    ).fetchall()
    out = []
    for r in rows:
        out.append(
            {
                "egp_id": r["egp_id"],
                "level": r["level"],
                "super_category": r["super_category"],
                "sub_category": r["sub_category"],
                "lexical_range": r["lexical_range"],
                "guideword": r["guideword"],
                "can_do_statement": r["can_do_statement"],
                "examples": [e for e in (r["example_raw"] or "").split("\n") if e.strip()],
            }
        )
    print(json.dumps(out, indent=1))
    conn.close()


def cmd_ingest(path: str) -> None:
    rules = json.loads(Path(path).read_text())
    conn = db()
    ok, missing = 0, []
    for rule in rules:
        row = conn.execute(
            "SELECT 1 FROM rows WHERE egp_id=?", (rule["egp_id"],)
        ).fetchone()
        if not row:
            missing.append(rule["egp_id"])
            continue
        conn.execute(
            """UPDATE rows SET status='testing', pattern_json=?, test_suite_json=?,
               error=NULL, updated_at=? WHERE egp_id=?""",
            (
                json.dumps(rule["detection"]),
                json.dumps(rule["unit_tests"]),
                now(),
                rule["egp_id"],
            ),
        )
        ok += 1
    conn.commit()
    print(f"ingested: {ok} -> testing")
    if missing:
        print(f"NOT in DB (skipped): {missing}")
    conn.close()


def cmd_gate() -> None:
    conn = db()
    testing = conn.execute(
        "SELECT egp_id, level, super_category, sub_category, guideword, can_do_statement, pattern_json, test_suite_json FROM rows WHERE status='testing'"
    ).fetchall()
    if not testing:
        print("nothing in 'testing' — ingest a batch first")
        return

    rules = []
    for r in testing:
        rules.append(
            {
                "egp_id": r["egp_id"],
                "level": r["level"],
                "super_category": r["super_category"],
                "sub_category": r["sub_category"],
                "guideword": r["guideword"],
                "can_do_statement": r["can_do_statement"],
                "detection": json.loads(r["pattern_json"]),
                "unit_tests": json.loads(r["test_suite_json"]),
            }
        )

    # THE EXECUTION GATE — fresh subprocess, so a malformed pattern
    # dies here and can never poison a live registry.
    proc = subprocess.run(
        [PY, str(GATE)],
        input=json.dumps(rules),
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        print("GATE subprocess crashed:", proc.stderr[-2000:])
        sys.exit(1)

    verdicts = json.loads(proc.stdout)
    passed = rejected = failed = 0
    for v in verdicts:
        if v["verdict"] == "passed":
            conn.execute(
                "UPDATE rows SET status='passed', error=NULL, updated_at=? WHERE egp_id=?",
                (now(), v["egp_id"]),
            )
            passed += 1
        elif v["verdict"] in ("registry_error", "regex_error"):
            # malformed pattern — reject back to pending, error recorded
            conn.execute(
                "UPDATE rows SET status='pending', error=?, updated_at=? WHERE egp_id=?",
                (v["verdict"] + ": " + "; ".join(v["failures"]), now(), v["egp_id"]),
            )
            rejected += 1
            print(f"REJECTED {v['egp_id']}: {v['failures']}")
        else:
            conn.execute(
                "UPDATE rows SET status='pending', error=?, updated_at=? WHERE egp_id=?",
                ("; ".join(v["failures"]), now(), v["egp_id"]),
            )
            failed += 1
            for f in v["failures"]:
                print(f"FAIL {v['egp_id'][:20]}…  {f}")
    conn.commit()
    print(f"gate: {passed} passed, {rejected} registry/regex rejected, {failed} test failures")
    conn.close()


def cmd_show(status: str) -> None:
    conn = db()
    rows = conn.execute(
        "SELECT egp_id, level, sub_category, guideword, error FROM rows WHERE status=? ORDER BY row_number",
        (status,),
    ).fetchall()
    for r in rows:
        print(f"{r['egp_id'][:28]}  {r['level']:<4} {r['sub_category']:<22} {r['guideword'][:45]}")
        if r["error"]:
            print(f"    err: {r['error'][:120]}")
    print(f"({len(rows)} rows)")
    conn.close()


def cmd_mark(egp_id: str, status: str) -> None:
    assert status in ("pending", "testing", "passed", "unmatchable_pragmatic")
    conn = db()
    conn.execute("UPDATE rows SET status=?, updated_at=? WHERE egp_id=?", (status, now(), egp_id))
    conn.commit()
    print(f"{egp_id} -> {status}")
    conn.close()


# ---------------------------------------------------------------- entry

def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "init":
        cmd_init()
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "next":
        cmd_next(int(sys.argv[2]) if len(sys.argv) > 2 else 15)
    elif cmd == "ingest":
        cmd_ingest(sys.argv[2])
    elif cmd == "gate":
        cmd_gate()
    elif cmd == "show":
        cmd_show(sys.argv[2] if len(sys.argv) > 2 else "pending")
    elif cmd == "mark":
        cmd_mark(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
