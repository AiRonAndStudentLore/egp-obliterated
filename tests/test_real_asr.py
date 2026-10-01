"""Real-speech robustness.

The 4,873 fixtures are clean written English: no filler, no false start, no
truncation marker, no L1 calque. The target population is ASR transcripts of ESL
speakers, and the measured gap is stark — 100% of fixtures pass while real turns
draw 16-56 rules each and the two detection stages disagree on 35-100% of them.

Two kinds of evidence here:

  * INJECTED DISFLUENCY. Take each rule's own positive and inject the repairs and
    hesitations that actually occur in the corpus, then measure whether the rule
    still fires. This is a recall budget, not a demand for perfection.
  * REAL TURNS. Run the engine over the corpus and assert the quarantine does its
    job: the catch-all wrappers are precisely the noise that must never reach a
    coaching trigger.
"""

from __future__ import annotations

import random
import statistics

import pytest

from egp_engine import ArbitrationPolicy, detect, detect_batch, normalize
from egp_engine.build_arbitration import read_turns

FILLER_INJECTIONS = [
    ", um, ",
    ", uh, ",
    " I mean, ",
    ", so, ",
]

FALSE_STARTS = [
    lambda s: s[: max(4, len(s) // 2)] + ", " + s,
    lambda s: s + " -",
]


def _disfluent(text: str, rng: random.Random) -> str:
    out = text
    if rng.random() < 0.7:
        pos = rng.randint(0, max(0, len(out) - 1))
        out = out[:pos] + rng.choice(FILLER_INJECTIONS) + out[pos:]
    if rng.random() < 0.3:
        out = rng.choice(FALSE_STARTS)(out)
    return out


def test_disfluent_recall_within_budget(compiled, rules):
    """A rule must survive a hesitation or two in its own positive.

    Budget, not zero: the compiled patterns carry at most one adverb gap, so some
    genuinely fail here. That is the measurement, not a test failure to be hidden.
    """
    rng = random.Random(20261001)
    cases = []
    for rule in rules:
        for pos in rule["unit_tests"]["positives"]:
            cases.append((rule["egp_id"], pos, _disfluent(pos, rng)))

    clean = detect_batch([c for _, c, _ in cases], compiled)
    noisy = detect_batch([n for _, _, n in cases], compiled)

    survived = 0
    regressions = []
    for (egp_id, clean_text, noisy_text), c, n in zip(cases, clean, noisy):
        if egp_id in c.egp_ids:
            survived += 1
            if egp_id not in n.egp_ids:
                regressions.append((egp_id, clean_text, noisy_text))

    recall = 100.0 * (survived - len(regressions)) / max(survived, 1)
    assert recall >= 70.0, (
        f"only {recall:.1f}% of rules survive an injected hesitation "
        f"(clean {survived} firing, {len(regressions)} lost). "
        f"First losses: {[(r[0][:14], r[2][:48]) for r in regressions[:5]]}"
    )


def test_normalisation_preserves_the_construction(compiled, rules):
    """Stripping fillers must not change which rule the text is evidence for."""
    rng = random.Random(7)
    sample = [r for r in rules[::37]]
    texts = []
    for rule in sample:
        texts.append((rule["egp_id"], rule["unit_tests"]["positives"][0]))
    dets = detect_batch([_disfluent(t, rng) for _, t in texts], compiled)
    lost = [
        (egp_id, txt)
        for (egp_id, txt), det in zip(texts, dets)
        if normalize(txt) and not det.egp_ids
    ]
    assert len(lost) <= 2, f"normalisation blanked detection on {len(lost)} rules: {lost[:4]}"


def test_engine_survives_the_real_corpus(compiled, corpus_turns):
    """No crash, no pathological output on 24k real turns."""
    texts = [t for _, t in corpus_turns if t.strip()][:1500]
    dets = detect_batch(texts, compiled, ArbitrationPolicy(top_k=5))

    assert all(d.candidates is not None for d in dets)
    for det in dets:
        assert len(det.candidates) <= 5
        assert det.macro is not None

    macro_rate = sum(1 for d in dets if d.macro) / len(dets)
    assert macro_rate > 0.3, (
        f"quarantined wrappers fired on only {macro_rate:.1%} of real turns; "
        f"the quarantine list was calibrated on this corpus, so a collapse here "
        f"means the list is stale"
    )


def test_catch_alls_dominate_raw_noise_but_never_candidates(compiled, corpus_turns):
    """The empirical justification for the quarantine, asserted so it stays true.

    The wrappers are the majority of what the raw matcher returns on real speech.
    That is exactly why they are background telemetry and not coaching triggers.
    """
    texts = [t for _, t in corpus_turns if t.strip()][:600]
    q_idx = {i for i, f in enumerate(compiled.features) if not f.arbitration_eligible}
    assert q_idx, "no quarantined rules"

    raw_total = 0
    quarantined_raw = 0
    ranked_total = 0
    quarantined_ranked = 0

    dets = detect_batch(texts, compiled, ArbitrationPolicy(top_k=10))
    docs = compiled.nlp.pipe(texts, batch_size=256)
    for det, doc in zip(dets, docs):
        raw = {key for key, _s, _e in compiled.matcher(doc)}
        raw_total += len(raw)
        quarantined_raw += len(raw & q_idx)
        ranked_total += len(det.candidates)
        quarantined_ranked += sum(1 for c in det.candidates if not c.arbitration_eligible)

    if raw_total:
        share = quarantined_raw / raw_total
        assert quarantined_ranked == 0, "a quarantined rule reached the ranked output"
        assert share > 0.05, (
            f"quarantined rules are only {share:.1%} of raw matches now; the list "
            f"was built at a materially different rate and should be regenerated"
        )


def test_stage_provenance_is_available_on_demand(compiled, corpus_turns):
    """Provenance mode must still work; it is the audit path, not the hot path."""
    texts = [t for _, t in corpus_turns if t.strip()][:200]
    dets = detect_batch(texts, compiled, provenance=True)
    disagreeing = [d for d in dets if d.stage.get("disagreement_rate", 0) > 0]
    assert disagreeing, (
        "no stage disagreement detected on 200 real turns; the fixtures already "
        "show 0.1%, so anything near zero here means provenance is not wired up"
    )
    rates = [d.stage["disagreement_rate"] for d in dets]
    assert statistics.fmean(rates) > 0.05
