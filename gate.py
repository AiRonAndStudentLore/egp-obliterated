"""
Execution Gate — run in a LIVE subprocess. Never import into the orchestrator.

Verifies compiled detector rules against their synthetic test suite:
  - registry: Matcher.add() must succeed (malformed keys/attrs rejected HERE,
    in an isolated process, so they can never poison a live registry)
  - positives: must fire in BOTH regex_triage and spaCy Matcher
  - negatives: must fire in NEITHER

Input : JSON array of rules on stdin
Output: JSON array of verdicts on stdout
        [{egp_id, verdict: "passed"|"registry_error"|"regex_error"|"test_failures", failures: [...]}]
"""
import json
import re
import sys

import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")


def gate(rule: dict) -> dict:
    out = {
        "egp_id": rule["egp_id"],
        "verdict": "passed",
        "failures": [],
    }

    # --- Stage 1: regex compiles? ---
    try:
        rx = re.compile(rule["detection"]["regex_triage"], re.I)
    except re.error as e:
        out["verdict"] = "regex_error"
        out["failures"].append(f"regex does not compile: {e}")
        return out

    # --- Stage 2: THE GATE — Matcher.add in isolation ---
    # Fresh Matcher per rule: a malformed pattern can never contaminate
    # the vocab registry used by other rules in this run.
    try:
        matcher = Matcher(nlp.vocab)
        matcher.add(rule["egp_id"], [rule["detection"]["spacy_token_pattern"]])
    except Exception as e:  # malformed attribute keys, wrong types, bad ops
        out["verdict"] = "registry_error"
        out["failures"].append(f"Matcher.add rejected pattern: {e}")
        return out

    # --- Stage 3: synthetic test suite ---
    for pos in rule["unit_tests"]["positives"]:
        if not rx.search(pos):
            out["verdict"] = "test_failures"
            out["failures"].append(f"regex MISSED positive: {pos!r}")
        try:
            if not matcher(nlp(pos)):
                out["verdict"] = "test_failures"
                out["failures"].append(f"spaCy MISSED positive: {pos!r}")
        except Exception as e:
            out["verdict"] = "test_failures"
            out["failures"].append(f"spaCy ERROR on positive {pos!r}: {e}")

    for neg in rule["unit_tests"]["negatives"]:
        if rx.search(neg):
            out["verdict"] = "test_failures"
            out["failures"].append(f"regex FALSE-POSITIVE on negative: {neg!r}")
        try:
            if matcher(nlp(neg)):
                out["verdict"] = "test_failures"
                out["failures"].append(f"spaCy FALSE-POSITIVE on negative: {neg!r}")
        except Exception as e:
            out["verdict"] = "test_failures"
            out["failures"].append(f"spaCy ERROR on negative {neg!r}: {e}")

    return out


def main() -> None:
    rules = json.load(sys.stdin)
    if not isinstance(rules, list):
        rules = [rules]
    print(json.dumps([gate(r) for r in rules], indent=1))


if __name__ == "__main__":
    main()
