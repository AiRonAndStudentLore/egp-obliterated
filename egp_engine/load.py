"""Rule loading, matcher construction, and the derived arbitration features."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import spacy
from spacy.matcher import Matcher

ROOT = Path(__file__).resolve().parent.parent
COMPILED_PATH = ROOT / "egp_compiled.json"
ARBITRATION_PATH = ROOT / "egp_arbitration.json"

LEVEL_RANK = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4, "C2": 5}

#: Length of the ranked list returned per utterance.
DEFAULT_TOP_K = 5

#: `en_core_web_sm` is the only model in pyproject.toml, and the rules were compiled
#: against it. `disable=["ner"]` is the one free win: no rule pattern uses `ENT_*`.
DISABLED_PIPELINE = ["ner"]


def count_mandatory_tokens(pattern: list[dict[str, Any]]) -> int:
    """Tokens that must match, i.e. everything except optional/repeating slots."""
    return sum(1 for tok in pattern if tok.get("OP") not in ("?", "*", "+"))


def max_in_list_size(pattern: list[dict[str, Any]]) -> int:
    """Size of the widest `IN` list in the pattern.

    A rule is only as constrained as its most permissive slot, so the widest list is
    the honest measure of how loose the rule is. 0 means no `IN` list at all, which
    ranks as maximally specific.
    """
    widest = 0
    for tok in pattern:
        for attr in ("LOWER", "LEMMA", "TAG", "POS", "DEP"):
            val = tok.get(attr)
            if isinstance(val, dict) and isinstance(val.get("IN"), list):
                widest = max(widest, len(val["IN"]))
    return widest


def has_pos_or_dep(pattern: list[dict[str, Any]]) -> bool:
    """True when the pattern constrains part-of-speech or dependency."""
    return any("POS" in tok or "DEP" in tok for tok in pattern)


def literal_anchors(pattern: list[dict[str, Any]]) -> tuple[str, ...]:
    """Lowercase literal words the pattern insists on, used to prefilter the regex stage.

    This is a plain substring test, not an automaton, and it never gates the
    spaCy Matcher — only the (cheap) regex sweep.
    """
    out: list[str] = []
    for tok in pattern:
        low = tok.get("LOWER")
        if isinstance(low, str) and low not in ("*",):
            out.append(low.lower())
    return tuple(dict.fromkeys(out))


@dataclass(frozen=True)
class RuleFeatures:
    """Derived, never hand-authored. Recomputed from the pattern on every load."""

    level_rank: int
    mandatory_tokens: int
    max_in_list_size: int
    has_pos_or_dep: bool
    pattern_len: int
    anchors: tuple[str, ...]
    arbitration_eligible: bool
    quarantine_reason: str | None = None

    def specificity_key(self, level_highest_wins: bool) -> tuple:
        """Ascending tuple; lower sorts first and therefore wins.

        Primary and secondary terms are the specificity of the RULE, not the geometry
        of the span. Span length is deliberately last: 82 of 1,218 rules have at most
        one mandatory token (including `[{"LOWER": "but"}]`), so any ordering that
        promotes short spans hands the engine to the degenerate rules.

        Two sign choices deserve stating explicitly, because the intuitive negation is
        wrong for both:

          * `mandatory_tokens` is negated — MORE mandatory tokens is more specific,
            so it must sort lower.
          * `in_list_size` is NOT negated — a SMALLER `IN` list is the more specific
            rule, so it must sort lower. Negating it would rank a 40-item list above
            a 3-item one, which is the loosest rule winning.
        """
        level = -self.level_rank if level_highest_wins else self.level_rank
        return (
            -self.mandatory_tokens,
            self.max_in_list_size,
            not self.has_pos_or_dep,
            level,
            self.pattern_len,
        )


@dataclass
class CompiledRules:
    """The loaded rule set plus one shared Matcher keyed by integer rule index."""

    rules: list[dict[str, Any]]
    features: list[RuleFeatures]
    regexes: list[re.Pattern[str]]
    matcher: Matcher
    nlp: spacy.Language
    index_by_id: dict[str, int] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.rules)

    def eligible(self, idx: int) -> bool:
        return self.features[idx].arbitration_eligible


def _arbitration_overrides() -> dict[str, dict[str, Any]]:
    if not ARBITRATION_PATH.exists():
        return {}
    raw = json.loads(ARBITRATION_PATH.read_text())
    return raw.get("rules", raw) if isinstance(raw, dict) else {}


def load(
    compiled_path: Path | str = COMPILED_PATH,
    arbitration_path: Path | str | None = ARBITRATION_PATH,
    *,
    nlp: spacy.Language | None = None,
) -> CompiledRules:
    """Load rules, derive features, and register every pattern into one Matcher."""
    rules: list[dict[str, Any]] = json.loads(Path(compiled_path).read_text())
    if not isinstance(rules, list):
        raise TypeError(f"{compiled_path} must contain a JSON array of rules")

    overrides: dict[str, dict[str, Any]] = {}
    if arbitration_path is not None and Path(arbitration_path).exists():
        raw = json.loads(Path(arbitration_path).read_text())
        overrides = raw.get("rules", raw) if isinstance(raw, dict) else {}

    if nlp is None:
        nlp = spacy.load("en_core_web_sm", disable=DISABLED_PIPELINE)

    matcher = Matcher(nlp.vocab)
    features: list[RuleFeatures] = []
    regexes: list[re.Pattern[str]] = []
    index_by_id: dict[str, int] = {}

    for idx, rule in enumerate(rules):
        egp_id = rule["egp_id"]
        if egp_id in index_by_id:
            raise ValueError(f"duplicate egp_id in compiled set: {egp_id}")
        index_by_id[egp_id] = idx

        pattern = rule["detection"]["spacy_token_pattern"]
        matcher.add(idx, [pattern])
        regexes.append(re.compile(rule["detection"]["regex_triage"], re.I))

        level = (rule.get("level") or "A1").strip().upper()
        ov = overrides.get(egp_id, {})
        features.append(
            RuleFeatures(
                level_rank=LEVEL_RANK.get(level, 0),
                mandatory_tokens=count_mandatory_tokens(pattern),
                max_in_list_size=max_in_list_size(pattern),
                has_pos_or_dep=has_pos_or_dep(pattern),
                pattern_len=len(pattern),
                anchors=literal_anchors(pattern),
                arbitration_eligible=bool(ov.get("arbitration_eligible", True)),
                quarantine_reason=ov.get("quarantine_reason"),
            )
        )

    return CompiledRules(
        rules=rules,
        features=features,
        regexes=regexes,
        matcher=matcher,
        nlp=nlp,
        index_by_id=index_by_id,
    )


def text_lower(text: str) -> str:
    return text.lower()
