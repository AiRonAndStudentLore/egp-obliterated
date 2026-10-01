"""Ontology grounding for the coaching model.

A rule match is an abstract grammar id. The leverage in this dataset is the
accompanying ontology: `mental_model` is the cognitive frame and
`pedagogical_hook` is the metaphor the learner is asked to reach for. Feeding the
hook into the prompt forces the model to adopt the framework's own metaphor instead
of emitting a generic grammar lecture.

`egp_compiled.json` scores what the learner produced, so the default register here is
affirmation and extension of a successful construction, not correction. The
`stance` argument is explicit rather than inferred, because guessing wrong produces
exactly the boilerplate this module exists to prevent.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from egp_engine.arbitrate import Candidate
from egp_engine.load import CompiledRules

Stance = Literal["affirm", "probe", "repair"]

STANCES: dict[Stance, str] = {
    "affirm": (
        "The learner produced this construction successfully. Name what they did "
        "in one short sentence using the coaching concept below, then offer one "
        "natural sentence that stretches it slightly further."
    ),
    "probe": (
        "The learner produced this construction. In one short sentence, point out "
        "the part of the concept below they have already grasped and ask a single "
        "question that pushes them to use it deliberately."
    ),
    "repair": (
        "The learner missed part of this construction. Apply the specific coaching "
        "concept below. Suggest a natural rewrite in one sentence. Do not lecture "
        "about the rule in general and do not restate the rule's name."
    ),
}

#: Fields that must be present for a rule to be usable as a coaching source.
REQUIRED_ONTOLOGY_FIELDS = ("mental_model", "pedagogical_hook")


@dataclass(frozen=True)
class CoachingPrompt:
    egp_id: str
    guideword: str
    level: str
    stance: Stance
    system: str
    user: str
    complete: bool
    missing: tuple[str, ...] = ()

    def as_messages(self) -> list[dict[str, str]]:
        return [{"role": "system", "content": self.system}, {"role": "user", "content": self.user}]


def _field(rule: dict[str, Any], name: str) -> str:
    return ((rule.get("ontology") or {}).get(name) or "").strip()


def build_prompt(
    candidate: Candidate,
    compiled: CompiledRules,
    stance: Stance = "affirm",
    *,
    extra: str = "",
) -> CoachingPrompt:
    """Build the two-message coaching exchange for one fired rule."""
    rule = compiled.rules[candidate.idx]
    missing = tuple(f for f in REQUIRED_ONTOLOGY_FIELDS if not _field(rule, f))
    mental = _field(rule, "mental_model")
    hook = _field(rule, "pedagogical_hook")
    domain = _field(rule, "domain")
    agency = _field(rule, "agency_or_distance")

    system = (
        "You coach ESL learners through the English Grammar Profile framework. "
        "You always teach through the framework's own cognitive metaphor, never "
        "through generic grammar terminology. Keep every response to one or two "
        "sentences.\n\n"
        f"Teaching stance for this turn: {STANCES[stance]}"
    )

    parts = [
        f"EGP rule: {candidate.guideword}",
        f"CEFR band: {candidate.level or rule.get('level', '').strip()}",
    ]
    if domain:
        parts.append(f"Cognitive domain: {domain.replace('_', ' ').title()}")
    if mental:
        parts.append(f"Cognitive model the learner is building: {mental}")
    if hook:
        parts.append(f"Coaching concept to apply: {hook}")
    if agency:
        parts.append(f"Agency/distance framing: {agency}")
    if extra:
        parts.append(extra)
    if missing:
        parts.append(
            f"[metadata gap: ontology.{', '.join(missing)} is empty for this rule; "
            f"coach from the construction alone and do not invent a metaphor]"
        )

    user = "\n".join(parts)
    if candidate.text:
        user += f"\n\nWhat the learner actually said: \"{candidate.text.strip()}\""

    return CoachingPrompt(
        egp_id=candidate.egp_id,
        guideword=candidate.guideword,
        level=candidate.level,
        stance=stance,
        system=system,
        user=user,
        complete=not missing,
        missing=missing,
    )


def build_session_prompts(
    candidates: list[Candidate],
    compiled: CompiledRules,
    stance: Stance = "affirm",
    *,
    limit: int = 3,
) -> list[CoachingPrompt]:
    """Top-N coaching prompts from an already-ranked candidate list."""
    return [build_prompt(c, compiled, stance) for c in candidates[:limit]]


def audit_ontology_coverage(compiled: CompiledRules) -> dict[str, Any]:
    """Which rules cannot ground a coaching prompt, and why."""
    gaps: list[dict[str, str]] = []
    for idx, rule in enumerate(compiled.rules):
        missing = [f for f in REQUIRED_ONTOLOGY_FIELDS if not _field(rule, f)]
        if missing:
            gaps.append(
                {
                    "egp_id": rule["egp_id"],
                    "guideword": rule.get("guideword", ""),
                    "level": (rule.get("level") or "").strip(),
                    "missing": ",".join(missing),
                }
            )
    return {
        "rules_total": len(compiled.rules),
        "groundable": len(compiled.rules) - len(gaps),
        "not_groundable": len(gaps),
        "gaps": gaps,
    }
