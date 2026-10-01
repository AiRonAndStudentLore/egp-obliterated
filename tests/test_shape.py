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


def test_out_of_contract_token_attrs(rules, capsys):
    """Attributes outside `SYSTEM_PROMPT.txt`'s enumerated list.

    These run fine under spaCy, so this is a reporting test, not a gate. It exists
    because the contract and the compiled data disagree: 133 token dicts reach for
    ORTH, IS_PUNCT, IS_ALPHA, LENGTH, TEXT, MORPH or IS_LOWER, none of which the
    contract names. Either the contract is incomplete or the compiler drifted.
    """
    seen: dict[str, list[str]] = {}
    for rule in rules:
        for tok in rule["detection"]["spacy_token_pattern"]:
            for key in set(tok) - CONTRACT_TOKEN_ATTRS:
                seen.setdefault(key, []).append(rule["egp_id"])
    with capsys.disabled():
        if seen:
            print("\n  token attrs outside the SYSTEM_PROMPT contract list:")
            for key, ids in sorted(seen.items(), key=lambda kv: -len(kv[1])):
                print(f"    {key:<12} {len(ids):>3} rules")
    assert True


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
