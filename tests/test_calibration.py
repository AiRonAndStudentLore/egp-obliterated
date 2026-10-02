"""Calibration against the corpus's independent EGP distillation.

Budgets, not thresholds. The point is to make a silent drift in calibration visible
on a PR, and to record the honest baseline: 62.1% category agreement with a severe
band skew, both measured on real learner speech.
"""

from __future__ import annotations

import pytest

from egp_engine.calibrate import calibrate

MIN_AGREEMENT_PCT = 50.0


def test_category_agreement_against_real_ground_truth(calibration):
    report = calibration
    assert report["learner_events"] > 500, (
        f"only {report['learner_events']} ground-truth events resolved; the "
        f"calibration would be too small to mean anything"
    )
    assert report["category_agreement_pct"] >= MIN_AGREEMENT_PCT, (
        f"category agreement fell to {report['category_agreement_pct']}% "
        f"(baseline 62.1%, floor {MIN_AGREEMENT_PCT}%)"
    )


def test_engine_does_not_overreach_above_the_reference_ceiling(calibration):
    """The reference places these learners at A1/A2 with zero C1/C2.

    The engine attributes C1 and C2 to them, because higher bands are compiled with
    wider `IN` lists over rarer vocabulary and so fire more readily on hesitant
    speech. This is tracked rather than gated — it is a known structural defect in
    the compiled set, and the ceiling here is deliberately loose so that a genuine
    regression is still caught.
    """
    report = calibration
    bands = report["bands"]
    over = sum(
        counts["engine"]
        for band, counts in bands.items()
        if band in ("C1", "C2")
    )
    total = sum(c["engine"] for c in report["categories"].values()) or 1
    share = 100.0 * over / total
    assert share <= 12.0, (
        f"C1/C2 attribution rose to {share:.1f}% of matched events; higher-band "
        f"patterns are over-firing on learner speech"
    )


def test_level_tie_break_is_not_the_cause_of_the_band_skew(compiled, corpus_turns):
    """Pins the diagnosis so it cannot be silently re-attributed to arbitration.

    Flipping `highest_level_wins` moves agreement by well under a point and leaves
    the band skew substantially intact, which is what establishes the skew as a
    property of the compiled patterns.
    """
    high = calibrate(compiled, max_sessions=40, highest_level_wins=True)
    low = calibrate(compiled, max_sessions=40, highest_level_wins=False)
    if "error" in high or "error" in low:
        pytest.skip("corpus unavailable")

    delta = abs(high["category_agreement_pct"] - low["category_agreement_pct"])
    assert delta < 3.0, (
        f"level tie-break now moves agreement by {delta:.1f} points, which would "
        f"mean the diagnosis in egp_engine/calibrate.py is stale"
    )
