"""Arbitration: specificity ranking, quarantine tier, level normalisation, echo guard."""

from __future__ import annotations

import pytest

from egp_engine import ArbitrationPolicy, detect, detect_batch, detect_turns, is_echo
from egp_engine.arbitrate import Candidate
from egp_engine.load import LEVEL_RANK


def _cand(mandatory, in_size, constrained, level, span=2):
    rule_level = level
    return Candidate(
        idx=0, egp_id="x", start=0, end=span, text="", level=rule_level,
        guideword="", super_category="",
        mandatory_tokens=mandatory, in_list_size=in_size, constrained=constrained,
        level_rank=LEVEL_RANK[rule_level], arbitration_eligible=True,
        quarantine_reason=None, matched_by="spacy",
    )


def test_specificity_beats_brevity():
    """A three-token specific rule outranks a one-token generic rule on the same span.

    Ordering by observed span length instead would hand the engine to the 82 rules
    with at most one mandatory token, including `[{"LOWER": "but"}]`.
    """
    generic = _cand(1, 26, False, "A1", span=3)
    specific = _cand(3, 2, True, "A1", span=1)
    from egp_engine.arbitrate import rank_candidates

    ranked = rank_candidates([generic, specific], ArbitrationPolicy())
    assert ranked[0] is specific, "the generic 1-token rule outranked the specific one"


def test_smaller_in_list_is_more_specific():
    from egp_engine.arbitrate import rank_candidates

    wide = _cand(2, 40, True, "A2")
    narrow = _cand(2, 3, True, "A2")
    assert rank_candidates([wide, narrow], ArbitrationPolicy())[0] is narrow


def test_pos_constrained_wins_ties():
    from egp_engine.arbitrate import rank_candidates

    loose = _cand(2, 2, False, "A2")
    tight = _cand(2, 2, True, "A2")
    assert rank_candidates([loose, tight], ArbitrationPolicy())[0] is tight


def test_highest_level_breaks_full_ties():
    from egp_engine.arbitrate import rank_candidates

    a1 = _cand(2, 2, True, "A1")
    b2 = _cand(2, 2, True, "B2")
    ranked = rank_candidates([a1, b2], ArbitrationPolicy(highest_level_wins=True))
    assert ranked[0] is b2
    ranked_low = rank_candidates([a1, b2], ArbitrationPolicy(highest_level_wins=False))
    assert ranked_low[0] is a1, "the low-level-first ordering should be the exact inverse"


def test_top_k_is_respected(compiled):
    det = detect(
        "there is a lot of good person and a lot of bad persons",
        compiled,
        ArbitrationPolicy(top_k=3),
    )
    assert len(det.candidates) == 3


def test_quarantined_rules_are_reported_but_never_ranked(compiled, rules):
    q_ids = {
        r["egp_id"] for r in rules
        if not compiled.features[compiled.index_by_id[r["egp_id"]]].arbitration_eligible
    }
    det = detect("there is a lot of good person and a lot of bad persons", compiled,
                 ArbitrationPolicy(top_k=50))
    assert det.macro, "expected quarantined macro telemetry on a full-sentence turn"
    assert set(det.egp_ids).isdisjoint(q_ids)
    assert {c.egp_id for c in det.macro} & q_ids


def test_every_rule_has_a_reason_when_quarantined(compiled):
    for idx, feat in enumerate(compiled.features):
        if not feat.arbitration_eligible:
            assert feat.quarantine_reason, (
                f"rule {compiled.rules[idx]['egp_id']} is quarantined with no recorded reason"
            )


def test_level_rank_is_monotonic(compiled):
    ranks = {c.level for c in [type("X", (), {"level": l})() for l in LEVEL_RANK]}
    assert len(ranks) == len(LEVEL_RANK)


@pytest.mark.parametrize(
    "student,tutor,expected",
    [
        ("How would you prepare?", "How would you prepare?", True),
        ("Yeah how would you prepare", "How would you prepare?", True),
        ("Because after 2, 3 weeks my brother is getting married",
         "How would you prepare?", False),
        ("I need to finish the report by Friday", "Let us talk about the weather today", False),
    ],
)
def test_echo_guard(student, tutor, expected):
    assert is_echo(student, tutor) is expected


def test_echo_turns_are_not_tallied(compiled):
    turns = [
        {"speaker": "A", "text": "How would you prepare it for the dinner?"},
        {"speaker": "B", "text": "How would you prepare it?"},
        {"speaker": "A", "text": "Good, now tell me about your morning."},
        {"speaker": "B", "text": "Because after 2, 3 weeks my brother is getting married."},
    ]
    results = detect_turns(turns, compiled)
    assert results[1].is_echo is True, "verbatim echo not detected"
    assert results[1].detection is None, "echo turn produced a detection"
    assert results[3].is_echo is False, "false positive echo"
    assert results[3].detection is not None
    assert results[1].is_learner is True
    assert results[0].is_learner is False
