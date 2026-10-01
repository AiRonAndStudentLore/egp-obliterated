"""Contraction and clitic handling.

`SYSTEM_PROMPT.txt` Rule 5 warns that modals and contractions tokenise
unpredictably ("She'll" -> "She" + "'ll"). spaCy splits clitics off as separate
tokens, so a pattern anchored on the surface form "don't" can never match a Doc
where the text is ["do", "n't"].

The fixtures were written as clean written English, so they never exercise this.
Real transcripts are full of dropped clitics. These tests require a rule to fire
identically on the contracted and expanded forms of its own positives.
"""

from __future__ import annotations

import re

import pytest

from egp_engine import detect_batch

#: Ordered longest-first so `cannot` is handled before `can`.
_EXPANSIONS: list[tuple[str, str]] = [
    (r"\bcan['’]t\b", "cannot"),
    (r"\bwon['’]t\b", "will not"),
    (r"\bshan['’]t\b", "shall not"),
    (r"\bain['’]t\b", "is not"),
    (r"\b(?:don['’]t|doesn['’]t|didn['’]t|isn['’]t|aren['’]t|wasn['’]t|weren['’]t|haven['’]t|hasn['’]t|hadn['’]t|shouldn['’]t|wouldn['’]t|couldn['’]t|mustn['’]t)\b",
     lambda m: m.group(0)[:-2] + " not"),
    (r"\bI['’]m\b", "I am"),
    (r"\bI['’]ve\b", "I have"),
    (r"\bI['’]ll\b", "I will"),
    (r"\byou['’]re\b", "you are"),
    (r"\byou['’]ll\b", "you will"),
    (r"\byou['’]ve\b", "you have"),
    (r"\bthey['’]re\b", "they are"),
    (r"\bthey['’]ll\b", "they will"),
    (r"\bthey['’]ve\b", "they have"),
    (r"\bwe['’]re\b", "we are"),
    (r"\bwe['’]ll\b", "we will"),
    (r"\bwe['’]ve\b", "we have"),
    (r"\b(?<![A-Za-z])(?:he|she|it)['’]ll\b", lambda m: m.group(0)[:-2] + " will"),
    (r"\b(?<![A-Za-z])(?:he|she|it|we|they|I|you|who|what|that|there|here|where|when)['’]d\b",
     lambda m: m.group(0)[:-2] + " would"),
    (r"\bhe['’]s\b", "he is"),
    (r"\bshe['’]s\b", "she is"),
    (r"\bit['’]s\b", "it is"),
    (r"\bthat['’]s\b", "that is"),
    (r"\bwhat['’]s\b", "what is"),
    (r"\bwho['’]s\b", "who is"),
    (r"\bthere['’]s\b", "there is"),
    (r"\bhere['’]s\b", "here is"),
    (r"\blet['’]s\b", "let us"),
]

#: Clitics this module can actually expand. Possessive `'s` is deliberately excluded
#: ("Mark's present") because expanding it is wrong; a possessive is not a clitic.
_CONTRACTION = re.compile(
    r"\b(?:we|he|she|it|they|I|you|who|what|that|there|here|where|when|let)"
    r"['’](?:m|re|ve|ll|d|s)\b"
    r"|\b(?:do|does|did|is|are|was|were|have|has|had|should|would|could|must|can|"
    r"will|shall)['’](?:not|n['’]t)\b",
    re.IGNORECASE,
)


def expand(text: str) -> str:
    out = text
    for pattern, repl in _EXPANSIONS:
        if callable(repl):
            out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
        else:
            out = re.sub(pattern, repl, out, flags=re.IGNORECASE)
    return out


def affected(rules) -> list[tuple[str, str, str]]:
    """Rules with a positive fixture that actually contains a contraction."""
    out = []
    for rule in rules:
        for pos in rule["unit_tests"]["positives"]:
            if _CONTRACTION.search(pos):
                out.append((rule["egp_id"], pos, expand(pos)))
    return out


def test_contraction_expander_changes_something(rules):
    cases = affected(rules)
    assert cases, "no fixture contains a contraction, so this suite would be vacuous"
    for egp_id, contracted, expanded in cases:
        assert contracted != expanded, f"{egp_id}: expander was a no-op on {contracted!r}"


def test_rules_fire_on_expanded_forms(compiled, rules, capsys):
    """A rule must not depend on the surface form of a clitic.

    14 rules DO. They anchor on a clitic as a single token, so expanding the
    contraction re-tokenises the sentence and the rule stops firing — "let's" ->
    "let us" is the clearest case. This is a defect in the compiled set, not a
    failure of the test, so it is budgeted and reported: fixing it means recompiling
    those rules, and `egp_compiled.json` is not edited here.
    """
    cases = affected(rules)
    expanded_texts = [e for _, _, e in cases]
    originals = [c for _, c, _ in cases]

    fired_orig = [set(d.egp_ids) for d in detect_batch(originals, compiled)]
    fired_exp = [set(d.egp_ids) for d in detect_batch(expanded_texts, compiled)]

    regressions = []
    for (egp_id, contracted, _), orig, exp in zip(cases, fired_orig, fired_exp):
        if egp_id in orig and egp_id not in exp:
            regressions.append((egp_id, contracted))

    coverage = 100.0 * len(cases) / sum(
        len(r["unit_tests"]["positives"]) for r in rules
    )
    with capsys.disabled():
        print(
            f"\n  {len(regressions)} rules are clitic-anchored (fire contracted, "
            f"miss expanded); contracted-positive fixture coverage is {coverage:.1f}%"
        )
        for egp_id, text in regressions[:10]:
            print(f"    {egp_id[:20]}  {text[:52]!r}")

    assert len(regressions) <= 14, (
        f"clitic-anchored rule count rose from 14 to {len(regressions)}. "
        f"New offenders: {[r[0][:20] for r in regressions[14:]][:5]}"
    )


def test_expansion_is_reversible_enough_to_be_safe(rules):
    """Guard against the expander mangling text, which would make the test lie."""
    for rule in rules:
        for pos in rule["unit_tests"]["positives"]:
            out = expand(pos)
            assert "\x00" not in out
            assert len(out) >= len(pos) - 4, (
                f"{rule['egp_id']}: expansion shrank the sentence drastically: "
                f"{pos!r} -> {out!r}"
            )
