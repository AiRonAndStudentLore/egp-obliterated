"""Schema and compilation-contract invariants over all 1,218 rules."""

from __future__ import annotations

import re

import pytest

from egp_engine.load import LEVEL_RANK
from tests.conftest import CONTRACT_TOKEN_ATTRS, LEVELS, SPACY_TOKEN_ATTRS


def test_no_duplicate_egp_id(rules):
    ids = [r["egp_id"] for r in rules]
    dupes = {i for i in ids if ids.count(i) > 1}
    assert not dupes, f"duplicate egp_id: {sorted(dupes)[:5]}"


def test_required_top_level_fields(rules):
    required = {
        "egp_id", "level", "super_category", "sub_category",
        "guideword", "can_do_statement", "ontology", "detection", "unit_tests",
    }
    for rule in rules:
        missing = required - rule.keys()
        assert not missing, f"{rule['egp_id']}: missing {sorted(missing)}"


def test_level_is_a_known_cefr_band(rules):
    for rule in rules:
        assert rule["level"].strip().upper() in LEVELS, (
            f"{rule['egp_id']}: unrecognised level {rule['level']!r}"
        )


def test_dirty_levels_are_normalised_in_arbitration(rules, compiled):
    """Three rules ship levels with trailing whitespace ('A2 ', 'B1 ', 'B1     ').

    They are legal here — this asserts the arbitration layer normalises them, so
    level ordering can never be corrupted by stray padding.
    """
    dirty = [r for r in rules if r["level"] != r["level"].strip().upper()]
    assert len(dirty) <= 5, f"unexpected jump in dirty level values: {len(dirty)}"
    for rule in dirty:
        idx = compiled.index_by_id[rule["egp_id"]]
        assert compiled.features[idx].level_rank == LEVEL_RANK[rule["level"].strip().upper()]


def test_token_pattern_is_a_flat_list_of_dicts(rules):
    for rule in rules:
        pattern = rule["detection"]["spacy_token_pattern"]
        assert isinstance(pattern, list) and pattern, rule["egp_id"]
        for tok in pattern:
            assert isinstance(tok, dict), f"{rule['egp_id']}: nested token found"
            for key, val in tok.items():
                assert not isinstance(val, list), (
                    f"{rule['egp_id']}: attribute {key} is a raw list; "
                    f"spaCy requires an IN dict"
                )


def test_token_pattern_uses_only_supported_attrs(rules):
    for rule in rules:
        for tok in rule["detection"]["spacy_token_pattern"]:
            extra = set(tok) - SPACY_TOKEN_ATTRS
            assert not extra, f"{rule['egp_id']}: unsupported attrs {sorted(extra)}"


def test_no_out_of_contract_token_attrs(rules):
    """The compiled set must stay inside the attribute set Rule 2 now sanctions.

    This was previously a reporting test over a narrower contract list: 133 token
    dicts reached for ORTH, IS_PUNCT, IS_ALPHA, LENGTH, TEXT, MORPH, IS_LOWER and
    IS_SENT_START, none of which the contract named. The contract has been widened
    to match reality — en_core_web_sm handles every one of them natively and each
    buys structural precision — so this is now a hard gate.
    """
    offenders: dict[str, int] = {}
    for rule in rules:
        for tok in rule["detection"]["spacy_token_pattern"]:
            for key in set(tok) - CONTRACT_TOKEN_ATTRS:
                offenders[key] = offenders.get(key, 0) + 1
    assert not offenders, (
        f"token dicts use attributes outside the SYSTEM_PROMPT Rule 2 contract: "
        f"{offenders}"
    )


def test_structural_attributes_are_actually_used(rules, capsys):
    """The band skew diagnosis depends on structural attributes being available.

    `egp_engine/calibrate.py` attributes the A1->B1/C2 skew to lexical sprawl
    standing in for structure. If the compiler stops using ORTH, IS_SENT_START,
    IS_PUNCT and IS_ALPHA, the documented remedy in Rule 6 is not being taken and
    the skew will not close. Reported, not gated, so the counts are visible on a PR.
    """
    counts: dict[str, int] = {}
    for rule in rules:
        for tok in rule["detection"]["spacy_token_pattern"]:
            for key in ("ORTH", "IS_SENT_START", "IS_PUNCT", "IS_ALPHA", "MORPH", "LENGTH"):
                if key in tok:
                    counts[key] = counts.get(key, 0) + 1
    with capsys.disabled():
        print("\n  structural attribute usage in the compiled set:")
        for key, n in sorted(counts.items(), key=lambda kv: -kv[1]):
            print(f"    {key:<15} {n:>4} token dicts")
    assert counts, "no structural attribute is used anywhere in the compiled set"


def test_regex_compiles(rules):
    for rule in rules:
        re.compile(rule["detection"]["regex_triage"], re.I)


def test_two_positives_and_two_negatives_per_rule(rules):
    for rule in rules:
        ut = rule["unit_tests"]
        assert len(ut["positives"]) >= 2, f"{rule['egp_id']}: only {len(ut['positives'])} positives"
        assert len(ut["negatives"]) >= 2, f"{rule['egp_id']}: only {len(ut['negatives'])} negatives"


def test_negatives_overlap_positive_vocabulary(rules, capsys):
    """A negative sharing no vocabulary with the positives cannot prove anything.

    It passes whether or not the rule is over-broad, so it is not a test. 27 rules
    are in this state, which is a real gap in the compiled set — reported, and held
    to a budget so the count can only improve.
    """
    import re as _re

    weak = []
    for rule in rules:
        pos_words = set()
        for pos in rule["unit_tests"]["positives"]:
            pos_words |= set(_re.findall(r"[a-z']+", pos.lower()))
        if not any(
            pos_words & set(_re.findall(r"[a-z']+", neg.lower()))
            for neg in rule["unit_tests"]["negatives"]
        ):
            weak.append(rule["egp_id"])

    with capsys.disabled():
        print(f"\n  {len(weak)} rules have no vocabulary-overlapping negative fixture")
    assert len(weak) <= 27, (
        f"weak-negative count rose from 27 to {len(weak)}; a new rule was compiled "
        f"with a distractor that shares no vocabulary with its positives: {weak[:3]}"
    )


def test_ontology_is_complete(rules, capsys):
    """12 rules ship an entirely empty ontology block.

    This directly disables ontology grounding for those rules, since the coaching
    prompt has no `pedagogical_hook` to draw on. Budgeted rather than gated, so the
    number can only fall.
    """
    empty = [
        rule["egp_id"]
        for rule in rules
        if any(
            not (rule["ontology"].get(f) or "").strip()
            for f in ("domain", "mental_model", "pedagogical_hook", "agency_or_distance")
        )
    ]
    with capsys.disabled():
        print(f"\n  {len(empty)} rules have an empty ontology block: {empty[:4]}")
    assert len(empty) <= 12, (
        f"empty-ontology count rose from 12 to {len(empty)}: {empty[:3]}"
    )


def test_ontology_domain_is_one_of_four(rules):
    allowed = {"TEMPORAL_ASPECT", "EPISTEMIC_STANCE", "DEONTIC_FORCE", "ENTITY_TOPOLOGY"}
    for rule in rules:
        assert rule["ontology"]["domain"] in allowed, rule["egp_id"]
