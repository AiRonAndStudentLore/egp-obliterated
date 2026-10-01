"""Cross-rule collision matrix.

`gate.py` builds a fresh Matcher per rule and only ever asks whether rule R fires on
R's own fixtures. No question of the form "does rule R fire when it should not, in
combination with the other 1,217 rules" is observable there, so the suite in
`test_fixtures.py` is green while the engine still returns a dozen rules for one
utterance.

This module measures that and holds it to a committed budget. The budgets are
calibrated, not aspirational: the measured baseline is 100% of positive fixtures
firing at least one foreign rule, with a mean of 13.8 rules per positive. Tightening
a budget is how precision improves; loosening one is how it silently regresses.
"""

from __future__ import annotations

import statistics

from egp_engine import ArbitrationPolicy, detect_batch


def _positives(matrix):
    return [
        (egp_id, res["pos_foreign"])
        for egp_id, res in matrix["own"].items()
    ]


def test_mean_rules_per_positive_within_budget(matrix, collision_budget):
    sizes = [
        size
        for size, kind in zip(matrix["per_text_fired"], matrix["kinds"])
        if kind == "pos"
    ]
    mean = statistics.fmean(sizes)
    assert mean <= collision_budget["max_mean_rules_per_positive"], (
        f"mean rules fired per positive rose to {mean:.1f} "
        f"(budget {collision_budget['max_mean_rules_per_positive']}); "
        f"median={statistics.median(sizes)} max={max(sizes)}"
    )


def test_mean_rules_per_negative_within_budget(matrix, collision_budget):
    sizes = [
        size
        for size, kind in zip(matrix["per_text_fired"], matrix["kinds"])
        if kind == "neg"
    ]
    mean = statistics.fmean(sizes)
    assert mean <= collision_budget["max_mean_rules_per_negative"], (
        f"mean rules fired per negative rose to {mean:.1f} "
        f"(budget {collision_budget['max_mean_rules_per_negative']})"
    )


def test_collision_rate_does_not_worsen(matrix, collision_budget):
    with_foreign = sum(1 for _, n in _positives(matrix) if n > 0)
    total = len(matrix["own"])
    pct = 100.0 * with_foreign / total
    assert pct <= collision_budget["max_positives_with_any_foreign_rule_pct"] + 1e-9, (
        f"{pct:.1f}% of positive fixtures fire a foreign rule "
        f"(budget {collision_budget['max_positives_with_any_foreign_rule_pct']}%)"
    )


def test_worst_collision_report(matrix, rules, capsys):
    """Not a gate — a diagnosis. Prints the rules that dominate false-positive load."""
    by_id = {r["egp_id"]: r for r in rules}
    foreign = sorted(
        ((res["pos_foreign"], egp_id) for egp_id, res in matrix["own"].items()),
        reverse=True,
    )[:15]
    with capsys.disabled():
        print("\n  rules that fire on the most foreign positives:")
        for count, egp_id in foreign:
            rule = by_id[egp_id]
            print(
                f"    {count:3d}  [{rule['level'].strip():<2}] "
                f"{rule['guideword'][:44]}"
            )
    assert foreign, "no collisions reported, which cannot be true"


def test_quarantined_rules_never_reach_candidates(compiled, rules):
    """The quarantine contract: barred from coaching triggers and friction tallies.

    Quarantined rules still fire and are still reported in `Detection.macro` for
    macro clause telemetry. They must not appear in `Detection.candidates`.
    """
    quarantined = [
        r for r in rules
        if not compiled.features[compiled.index_by_id[r["egp_id"]]].arbitration_eligible
    ]
    assert quarantined, "expected the catch-all quarantine list to be non-empty"

    texts = []
    for rule in rules[:120]:
        texts.extend(rule["unit_tests"]["positives"])

    q_ids = {r["egp_id"] for r in quarantined}
    leaks = 0
    for det in detect_batch(texts, compiled, ArbitrationPolicy(top_k=25), provenance=True):
        leaked = q_ids & set(det.egp_ids)
        if leaked:
            leaks += 1
        assert not (set(det.egp_ids) & q_ids), (
            f"quarantined rule {sorted(leaked)} reached candidates on {det.text[:50]!r}"
        )
    assert leaks == 0


def test_candidates_preserve_overlap(compiled, rules):
    """Ranking, not selection: two rules on the same tokens must both survive.

    This is the invariant that `spacy.util.filter_spans` violates. Its sort key is
    `(end - start, -start)`, reverse, i.e. longest-then-leftmost, so on this dataset
    it crowns generic A1 clause wrappers and discards the specific rules.
    """
    text = "there is a lot of good person and a lot of bad persons"
    det = detect_batch([text], compiled, ArbitrationPolicy(top_k=25))[0]

    spans = [(c.start, c.end) for c in det.candidates if c.start >= 0]
    assert len(spans) >= 2, "expected multiple candidates on this utterance"
    overlapping = [
        (a, b)
        for i, a in enumerate(spans)
        for b in spans[i + 1:]
        if a[0] < b[1] and b[0] < a[1]
    ]
    assert overlapping, (
        "no overlapping candidates survived — arbitration is behaving like a "
        "disjoint span filter, which is the regression this suite exists to catch"
    )
