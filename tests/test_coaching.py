"""Ontology grounding: the coaching prompt the 4B model receives."""

from __future__ import annotations

from egp_engine import ArbitrationPolicy, detect
from egp_engine.coaching import (
    STANCES,
    audit_ontology_coverage,
    build_prompt,
    build_session_prompts,
)


def test_prompt_carries_the_pedagogical_hook(compiled):
    det = detect("this information is very useful for my report", compiled,
                 ArbitrationPolicy(top_k=8))
    assert det.candidates, "no candidates fired"
    prompts = build_session_prompts(det.candidates, compiled)
    assert prompts
    grounded = [p for p in prompts if p.complete]
    assert grounded, "every prompt fell back to a metadata gap"
    for p in grounded:
        assert "Coaching concept to apply:" in p.user
        assert "Cognitive model the learner is building:" in p.user
        assert p.system != ""


def test_prompt_does_not_leak_the_rule_name_as_a_lecture(compiled):
    """`repair` stance explicitly forbids restating the rule's name as a lecture."""
    det = detect("this information is very useful for my report", compiled,
                 ArbitrationPolicy(top_k=4))
    prompt = build_prompt(det.candidates[0], compiled, "repair")
    assert "Do not lecture" in prompt.system
    assert prompt.as_messages()[0]["role"] == "system"
    assert prompt.as_messages()[1]["role"] == "user"


def test_every_stance_is_registered():
    assert set(STANCES) == {"affirm", "probe", "repair"}


def test_prompt_reports_ontology_gaps_rather_than_inventing(compiled):
    report = audit_ontology_coverage(compiled)
    assert report["rules_total"] == len(compiled)
    assert report["groundable"] + report["not_groundable"] == report["rules_total"]
    for gap in report["gaps"]:
        assert gap["missing"], gap
    if report["not_groundable"]:
        det = detect("there is a lot of good person and a lot of bad persons", compiled,
                     ArbitrationPolicy(top_k=50))
        prompts = [build_prompt(c, compiled) for c in det.candidates]
        for p in prompts:
            if not p.complete:
                assert "metadata gap" in p.user
                assert "do not invent a metaphor" in p.user
