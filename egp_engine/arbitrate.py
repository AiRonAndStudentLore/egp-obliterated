"""Candidate ranking.

The engine never partitions a sentence into disjoint spans. Multiple grammar
phenomena legitimately co-occur across the same token boundaries, and forcing a
single winner was the root cause of the engine discarding specific pedagogical
nuggets in favour of generic clause wrappers. Overlaps are preserved and every
candidate is scored.

Ordering is by RULE specificity, not span geometry:

    (-mandatory_tokens, -IN_list_size, has_pos_or_dep, level_rank, pattern_len)

`pattern_len` — not the observed span length — is the final term. 82 of 1,218 rules
have at most one mandatory token, so any key that promotes short observed spans
hands the engine to degenerate rules such as `[{"LOWER": "but"}]`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spacy.tokens import Doc, Span

from egp_engine.load import CompiledRules, RuleFeatures

#: When True, a higher CEFR band wins a full tie (B1 beats A1).
#:
#: Both orderings are supported because the two terms pull in opposite directions
#: from different sources: the compilation contract wants *specificity* to lead,
#: while the pedagogical goal is "do not tally basic noise when the speaker is
#: actually using higher-tier syntax". They only diverge on an exact tie in the
#: first three terms, which is precisely the case of sibling rules covering the same
#: construction at different bands. `tests/test_arbitration.py` reports the number
#: of decisions each ordering flips on the real corpus.
DEFAULT_HIGHEST_LEVEL_WINS = True


@dataclass(frozen=True)
class ArbitrationPolicy:
    top_k: int = 5
    highest_level_wins: bool = DEFAULT_HIGHEST_LEVEL_WINS
    include_ineligible: bool = False


@dataclass(frozen=True)
class Candidate:
    """One rule firing on one span, with both stages' provenance recorded."""

    idx: int
    egp_id: str
    start: int
    end: int
    text: str
    level: str
    guideword: str
    super_category: str
    mandatory_tokens: int
    in_list_size: int
    constrained: bool
    level_rank: int
    arbitration_eligible: bool
    quarantine_reason: str | None
    matched_by: str

    @property
    def specificity_key(self) -> tuple:
        level = -self.level_rank if DEFAULT_HIGHEST_LEVEL_WINS else self.level_rank
        return (-self.mandatory_tokens, self.in_list_size, not self.constrained, level)


def candidate_from_match(
    compiled: CompiledRules,
    idx: int,
    span: Span,
    matched_by: str,
) -> Candidate:
    rule = compiled.rules[idx]
    feat: RuleFeatures = compiled.features[idx]
    return Candidate(
        idx=idx,
        egp_id=rule["egp_id"],
        start=span.start,
        end=span.end,
        text=span.text,
        level=(rule.get("level") or "").strip(),
        guideword=rule.get("guideword", ""),
        super_category=rule.get("super_category", ""),
        mandatory_tokens=feat.mandatory_tokens,
        in_list_size=feat.max_in_list_size,
        constrained=feat.has_pos_or_dep,
        level_rank=feat.level_rank,
        arbitration_eligible=feat.arbitration_eligible,
        quarantine_reason=feat.quarantine_reason,
        matched_by=matched_by,
    )


def rank_candidates(
    candidates: list[Candidate],
    policy: ArbitrationPolicy = ArbitrationPolicy(),
) -> list[Candidate]:
    """Score and rank. Overlapping candidates are all retained."""
    pool = candidates if policy.include_ineligible else [
        c for c in candidates if c.arbitration_eligible
    ]
    return sorted(
        pool,
        key=lambda c: (
            -c.mandatory_tokens,
            c.in_list_size,
            not c.constrained,
            -c.level_rank if policy.highest_level_wins else c.level_rank,
            c.end - c.start,
        ),
    )[: policy.top_k]


def macro_candidates(candidates: list[Candidate]) -> list[Candidate]:
    """The quarantined rules — telemetry only.

    These track whether the student is producing full sentences and comparable
    clause structure. They are barred from coaching triggers, highlights, and
    student friction tallies.
    """
    return [c for c in candidates if not c.arbitration_eligible]


def stage_agreement(candidates: list[Candidate]) -> dict[str, Any]:
    """How the two stages lined up. Disagreement is a review signal, not a drop."""
    by_rule: dict[str, set[str]] = {}
    for c in candidates:
        by_rule.setdefault(c.egp_id, set()).add(c.matched_by)
    both = [k for k, v in by_rule.items() if len(v) == 2]
    spacy_only = [k for k, v in by_rule.items() if v == {"spacy"}]
    regex_only = [k for k, v in by_rule.items() if v == {"regex"}]
    return {
        "agree": len(both),
        "spacy_only": len(spacy_only),
        "regex_only": len(regex_only),
        "disagreement_rate": round(
            (len(spacy_only) + len(regex_only)) / max(len(by_rule), 1), 4
        ),
    }
