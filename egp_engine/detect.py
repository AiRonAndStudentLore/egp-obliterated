"""Detection entry points: one sentence, a batch, or a full speaker-attributed turn stream."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import spacy
from spacy.tokens import Doc

from egp_engine.arbitrate import (
    ArbitrationPolicy,
    Candidate,
    candidate_from_match,
    macro_candidates,
    rank_candidates,
    stage_agreement,
)
from egp_engine.load import CompiledRules, load

#: Tokens ASR emits for hesitation and repair. Stripped before matching because
#: compiled regexes carry at most one adverb gap and no general filler slot.
FILLER = re.compile(
    r"(?<![\w'])\b(?:uh+|um+|erm+|er+|ah+|hmm+|eh+|mhm+)\b(?![\w'])", re.I
)

#: Immediate word repetition from a false start: "before the at least before the".
REPEAT = re.compile(r"\b(\w+)(\s+\1\b){1,}", re.I)

#: Trailing truncation marker left by an abandoned utterance.
TRUNCATION = re.compile(r"(?:\s+(?:-|\.\.\.|—|-{2,}))+\s*$")

#: Punctuation left orphaned once a filler token between commas is removed.
#: Collapses the whole run, not just its first separator: "example, um, where" leaves
#: "example, , where", whose run ", ," must become ", " rather than ",,".
ORPHAN_PUNCT = re.compile(r"[,;](?:\s*[,;])+")
SPACE_BEFORE_PUNCT = re.compile(r"\s+([,;:.!?])")

#: Token overlap at or above which a student turn is treated as an echo of the tutor.
ECHO_OVERLAP = 0.7

_WORD = re.compile(r"[a-z']+")


@dataclass
class Detection:
    """Result for one utterance."""

    text: str
    normalized: str
    candidates: list[Candidate] = field(default_factory=list)
    macro: list[Candidate] = field(default_factory=list)
    stage: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    @property
    def fired(self) -> list[Candidate]:
        return self.candidates

    @property
    def egp_ids(self) -> list[str]:
        return [c.egp_id for c in self.candidates]

    def hooks(self, compiled: CompiledRules) -> list[dict[str, str]]:
        """Ontology grounding for the coaching prompt (P5)."""
        out = []
        for c in self.candidates:
            onto = compiled.rules[c.idx].get("ontology") or {}
            out.append(
                {
                    "egp_id": c.egp_id,
                    "guideword": c.guideword,
                    "level": c.level,
                    "super_category": c.super_category,
                    "mental_model": onto.get("mental_model", ""),
                    "pedagogical_hook": onto.get("pedagogical_hook", ""),
                }
            )
        return out


def normalize(text: str, *, strip_fillers: bool = True) -> str:
    """Repair-layer normalisation for ASR speech.

    The compiled rules were written against clean written English: no filler, no
    false starts, no truncation markers. Real transcripts contain all three, and the
    fixtures contain none, so nothing in the rule set can absorb them.
    """
    out = text
    if strip_fillers:
        out = FILLER.sub(" ", out)
        out = ORPHAN_PUNCT.sub(",", out)
    out = REPEAT.sub(r"\1", out)
    out = TRUNCATION.sub("", out)
    out = SPACE_BEFORE_PUNCT.sub(r"\1", out)
    return re.sub(r"\s+", " ", out).strip()


def _regex_hits(compiled: CompiledRules, text: str) -> set[int]:
    """Regex stage — provenance only, never the decision authority.

    A full unswept 1,218-regex sweep is the only sound form. Any prefilter derived
    from the spaCy token pattern is unsound here, because it gates a *different*
    artifact: measured against a full sweep it silently dropped 104 of 2,781 real
    matches, since a regex can match through a branch that never mentions the
    pattern's literal anchor.

    It is also the expensive half. Measured over 600 real learner turns: 16.5 ms per
    turn for 1,218 regexes (18.2 matches each) against 6.5 ms per turn for the whole
    spaCy Matcher. Greedy surface-form regexes are the original bottleneck, so
    running them by default would reinstate it. Off by default; on for audit.
    """
    return {idx for idx, rx in enumerate(compiled.regexes) if rx.search(text)}


def _spacy_hits(compiled: CompiledRules, doc: Doc) -> dict[int, list[tuple[int, int]]]:
    out: dict[int, list[tuple[int, int]]] = {}
    for key, start, end in compiled.matcher(doc):
        out.setdefault(key, []).append((start, end))
    return out


def _detect_doc(
    compiled: CompiledRules,
    text: str,
    doc: Doc,
    policy: ArbitrationPolicy,
    provenance: bool = False,
) -> Detection:
    spacy_spans = _spacy_hits(compiled, doc)
    regex_idx = _regex_hits(compiled, text) if provenance else set()

    candidates: list[Candidate] = []
    for idx, spans in spacy_spans.items():
        for start, end in spans:
            stage = "both" if (provenance and idx in regex_idx) else "spacy"
            candidates.append(candidate_from_match(compiled, idx, doc[start:end], stage))
    if provenance:
        for idx in regex_idx - set(spacy_spans):
            rule = compiled.rules[idx]
            feat = compiled.features[idx]
            candidates.append(
                Candidate(
                    idx=idx,
                    egp_id=rule["egp_id"],
                    start=-1,
                    end=-1,
                    text="",
                    level=(rule.get("level") or "").strip(),
                    guideword=rule.get("guideword", ""),
                    super_category=rule.get("super_category", ""),
                    mandatory_tokens=feat.mandatory_tokens,
                    in_list_size=feat.max_in_list_size,
                    constrained=feat.has_pos_or_dep,
                    level_rank=feat.level_rank,
                    arbitration_eligible=feat.arbitration_eligible,
                    quarantine_reason=feat.quarantine_reason,
                    matched_by="regex",
                )
            )

    det = Detection(
        text=text,
        normalized=text,
        candidates=rank_candidates(candidates, policy),
        macro=macro_candidates(candidates),
        stage=stage_agreement(candidates) if provenance else {"mode": "matcher_only"},
    )
    if provenance:
        if regex_idx - set(spacy_spans):
            det.notes.append("regex_only_hits")
        if set(spacy_spans) - regex_idx:
            det.notes.append("spacy_only_hits")
    if len(det.macro):
        det.notes.append(f"{len(det.macro)}_quarantined")
    return det


def detect(
    text: str,
    compiled: CompiledRules | None = None,
    policy: ArbitrationPolicy = ArbitrationPolicy(),
    *,
    normalize_input: bool = True,
    provenance: bool = False,
) -> Detection:
    """Detect on one utterance. The spaCy Matcher is the authority."""
    compiled = compiled or load()
    body = normalize(text) if normalize_input else text
    doc = compiled.nlp(body)
    det = _detect_doc(compiled, body, doc, policy, provenance)
    det.text = text
    return det


def detect_batch(
    texts: Sequence[str],
    compiled: CompiledRules | None = None,
    policy: ArbitrationPolicy = ArbitrationPolicy(),
    *,
    normalize_input: bool = True,
    batch_size: int = 64,
    provenance: bool = False,
) -> list[Detection]:
    """Detect on many utterances with ONE parse pass per batch.

    `nlp.pipe` is worth 3.4x over a serial loop (measured 5.07s -> 1.50s per 1,000
    short sentences) and is the single largest performance lever, because the parse
    cannot be disabled: 595 rules need POS, 371 LEMMA, 280 TAG, 160 DEP.
    """
    compiled = compiled or load()
    originals = list(texts)
    bodies = [normalize(t) if normalize_input else t for t in originals]
    out: list[Detection] = []
    for original, body, doc in zip(
        originals, bodies, compiled.nlp.pipe(bodies, batch_size=batch_size)
    ):
        det = _detect_doc(compiled, body, doc, policy, provenance)
        det.text = original
        out.append(det)
    return out


def _echo_overlap(student_text: str, tutor_text: str) -> float:
    """Fraction of the STUDENT's content words already present in the tutor's turn.

    The denominator is the student's word count, not the tutor's: the question is
    how much of what the student said came from the tutor. Dividing by the tutor's
    count instead penalises a tutor turn that was merely longer, which is the common
    case, and makes a verbatim echo of a long prompt score below threshold.
    """
    wa = set(_WORD.findall(student_text.lower()))
    wb = set(_WORD.findall(tutor_text.lower()))
    if not wa:
        return 0.0
    return len(wa & wb) / len(wa)


def is_echo(student_text: str, tutor_text: str | None, threshold: float = ECHO_OVERLAP) -> bool:
    """True when the student turn repeats the tutor's preceding turn.

    Echo turns are mimicry, not production. A rule match on an echo is an
    artifact of the rule, not evidence about the learner, so it must not be
    tallied.
    """
    if not tutor_text:
        return False
    return _echo_overlap(student_text, tutor_text) >= threshold


@dataclass
class TurnResult:
    index: int
    speaker: str
    text: str
    is_learner: bool
    is_echo: bool
    detection: Detection | None


def detect_turns(
    turns: Iterable[dict[str, Any]],
    compiled: CompiledRules | None = None,
    policy: ArbitrationPolicy = ArbitrationPolicy(),
    *,
    learner: str = "B",
    echo_threshold: float = ECHO_OVERLAP,
) -> list[TurnResult]:
    """Detect across a speaker-attributed turn stream, flagging echoes.

    `turns` is a sequence of {"speaker": "A"|"B", "text": str}. Echo detection
    needs the immediately preceding turn from the other speaker, so this cannot be
    done per-sentence.
    """
    compiled = compiled or load()
    turns = list(turns)
    is_learner = [t.get("speaker") == learner for t in turns]
    results: list[TurnResult] = []

    for i, turn in enumerate(turns):
        prev = None
        for j in range(i - 1, -1, -1):
            if is_learner[j] != is_learner[i]:
                prev = turn_text(turns[j])
                break
        echo = is_echo(turn_text(turn), prev, echo_threshold) if is_learner[i] else False
        results.append(
            TurnResult(
                index=i,
                speaker=turn.get("speaker", "?"),
                text=turn_text(turn),
                is_learner=is_learner[i],
                is_echo=echo,
                detection=None if echo else detect(turn_text(turn), compiled, policy),
            )
        )
    return results


def turn_text(turn: dict[str, Any]) -> str:
    for key in ("text", "transcript", "utterance", "line"):
        val = turn.get(key)
        if isinstance(val, str) and val.strip():
            return val
    return ""
