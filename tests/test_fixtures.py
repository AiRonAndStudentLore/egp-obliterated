"""Per-rule own-fixture regression.

This is the same contract `gate.py` enforces, re-expressed as a blocking suite so a
pattern change cannot land without running it. `gate.py` is not rewritten or
imported; it stays the live subprocess validator for the compile loop.
"""

from __future__ import annotations

import re

import pytest


def test_own_positive_fires_own_rule(rules, matrix):
    failures = [
        (egp_id, res)
        for egp_id, res in matrix["own"].items()
        if not res["pos_fired"]
    ]
    assert not failures, f"regex/spaCy missed own positive for {len(failures)} rules: {failures[:5]}"


def test_own_negative_does_not_fire_own_rule(rules, matrix):
    """A false-positive leak: the rule firing on its own near-miss distractor."""
    failures = [
        (egp_id, res)
        for egp_id, res in matrix["own"].items()
        if res["neg_fired"]
    ]
    assert not failures, (
        f"{len(failures)} rules fire on their own negative fixture: {failures[:5]}"
    )


def test_regex_triage_meets_its_contract(rules):
    """`gate.py` requires the regex to fire on positives and NOT on negatives.

    The engine treats the token pattern as final authority, but the regex is still
    part of the compilation contract, so it stays under test here rather than being
    allowed to rot unnoticed.
    """
    leaks, misses = [], []
    for rule in rules:
        rx = re.compile(rule["detection"]["regex_triage"], re.I)
        for pos in rule["unit_tests"]["positives"]:
            if not rx.search(pos):
                misses.append((rule["egp_id"], pos))
        for neg in rule["unit_tests"]["negatives"]:
            if rx.search(neg):
                leaks.append((rule["egp_id"], neg))
    assert not misses, f"regex_triage MISSED {len(misses)} own positives: {misses[:5]}"
    assert not leaks, f"regex_triage FALSE-POSITIVE on {len(leaks)} own negatives: {leaks[:5]}"
