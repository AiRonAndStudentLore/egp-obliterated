"""Generate `egp_arbitration.json`.

Emits derived arbitration features plus the catch-all quarantine list. Never
mutates `egp_compiled.json` — the compiled set stays the compiler's output, and
everything the runtime needs on top of it lives in this sibling file.

A rule is quarantined when it is *empirically* unspecific, measured two ways:

  1. Structural: the pattern carries almost no constraint (at most one mandatory
     token, and that token pinned only by POS/DEP or a wide `IN` list).
  2. Behavioural: it fires on an implausible fraction of real learner speech,
     measured over a transcript corpus.

Behavioural evidence is the stronger signal and takes precedence when available.
Guessing from `guideword` text is not used: a grep for "MAIN VERBS" is a guess
about intent, whereas a hit rate is a measurement of consequence.

Usage:
    python -m egp_engine.build_arbitration
    python -m egp_engine.build_arbitration --corpus "/home/hayron/By Student"
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
from pathlib import Path
from typing import Any, Iterable

from egp_engine.load import (
    ARBITRATION_PATH,
    COMPILED_PATH,
    LEVEL_RANK,
    count_mandatory_tokens,
    has_pos_or_dep,
    literal_anchors,
    max_in_list_size,
)

#: A pattern with at most this many mandatory tokens cannot discriminate clause
#: shape from anything else in the language.
MAX_MANDATORY_FOR_SPECIFIC = 1

#: A rule firing on more than this fraction of real turns is not discriminating on
#: that population, whatever its pattern looks like. Calibrated against the measured
#: hit-rate distribution, which is heavily skewed: median 0.2%, p95 ~19%, with a
#: short head of clause-wrapper rules saturating far above 100%.
CORPUS_HIT_RATE_QUARANTINE = 0.25

TURN_LINE = re.compile(r"^\s*\[\d+\]\s+([A-Za-z0-9_]+)\s*:\s*(.*)$")


def structural_genericity(pattern: list[dict[str, Any]]) -> tuple[bool, str]:
    """Structural over-specificity test. Returns (is_generic, reason).

    Recorded as evidence only. It is NOT part of the quarantine decision: on its own
    it flagged several hundred rules, including ones measured at a 0.0% corpus hit
    rate, which is precisely the kind of guess-from-intent that guessing from
    `guideword` text would be. Behavioural evidence decides.
    """
    mandatory = count_mandatory_tokens(pattern)
    in_size = max_in_list_size(pattern)
    anchors = literal_anchors(pattern)
    if mandatory == 0:
        return True, "zero mandatory tokens"
    reasons = []
    if not anchors:
        reasons.append("no literal anchor")
    if in_size >= 8:
        reasons.append(f"IN list of {in_size}")
    if not has_pos_or_dep(pattern) and not anchors:
        reasons.append("unconstrained")
    if reasons:
        return True, f"{mandatory} mandatory token(s); " + "; ".join(reasons)
    return False, ""


def read_turns(corpus_root: str | Path) -> list[tuple[str, str]]:
    """Yield (speaker, text) for every turn in every `--transcript.txt` under root.

    The sibling `--nlp.json` carries `analysis.learner`, so learner turns can be
    separated from tutor turns; the speaker label alone is ambiguous and the
    pipeline marks that field `heuristic_unverified`.
    """
    root = Path(corpus_root)
    if not root.is_dir():
        raise NotADirectoryError(root)
    out: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*--transcript.txt")):
        learner = _learner_for(path)
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for line in text.splitlines():
            m = TURN_LINE.match(line)
            if not m:
                continue
            speaker, body = m.group(1), m.group(2).strip()
            if body:
                out.append(("learner" if speaker == learner else "tutor", body))
    return out


def _learner_for(transcript_path: Path) -> str:
    nlp_json = transcript_path.with_name(
        transcript_path.name.replace("--transcript.txt", "--nlp.json")
    )
    if not nlp_json.exists():
        return "B"
    try:
        analysis = json.loads(nlp_json.read_text()).get("analysis") or {}
    except (OSError, ValueError):
        return "B"
    return analysis.get("learner") or "B"


def measure_corpus_hit_rates(
    rules: list[dict[str, Any]],
    turns: list[tuple[str, str]],
    *,
    batch_size: int = 256,
    max_turns: int | None = None,
    role: str = "learner",
) -> tuple[dict[str, float], dict[str, int]]:
    """Per-turn hit rate for each rule: the fraction of turns it fires on AT ALL.

    Counting matches instead of turns is wrong — a rule firing on five spans in one
    turn is one turn of evidence, not five. Returns (rates, counts).
    """
    import spacy
    from spacy.matcher import Matcher

    texts = [t for speaker, t in turns if role == "all" or speaker == role]
    if max_turns:
        texts = texts[:max_turns]
    if not texts:
        return {}, {"turns": 0}

    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    matcher = Matcher(nlp.vocab)
    for idx, rule in enumerate(rules):
        matcher.add(idx, [rule["detection"]["spacy_token_pattern"]])

    hit_turns = collections.Counter()
    for doc in nlp.pipe(texts, batch_size=batch_size):
        for key in {key for key, _s, _e in matcher(doc)}:
            hit_turns[key] += 1

    n = len(texts)
    rates = {rules[i]["egp_id"]: hit_turns[i] / n for i in range(len(rules))}
    return rates, {"turns": n, "role": role}


def build(
    compiled_path: Path = COMPILED_PATH,
    out_path: Path = ARBITRATION_PATH,
    corpus: str | None = None,
    corpus_max_turns: int | None = None,
) -> dict[str, Any]:
    rules = json.loads(Path(compiled_path).read_text())

    fixture_total = sum(len(r["unit_tests"]["positives"]) for r in rules)

    corpus_rates: dict[str, float] = {}
    corpus_info: dict[str, int] = {"turns": 0}
    if corpus:
        turns = read_turns(corpus)
        corpus_rates, corpus_info = measure_corpus_hit_rates(
            rules, turns, max_turns=corpus_max_turns
        )

    entries: dict[str, dict[str, Any]] = {}
    quarantined: list[str] = []
    level_dirty: list[str] = []

    for rule in rules:
        egp_id = rule["egp_id"]
        pattern = rule["detection"]["spacy_token_pattern"]
        raw_level = rule.get("level") or ""
        level = raw_level.strip().upper()
        if raw_level != level:
            level_dirty.append(egp_id)

        generic, struct_reason = structural_genericity(pattern)
        rate = corpus_rates.get(egp_id)
        eligible = True
        reason: str | None = None

        if rate is not None and rate > CORPUS_HIT_RATE_QUARANTINE:
            eligible = False
            reason = (
                f"fires on {rate:.1%} of real learner turns "
                f"(> {CORPUS_HIT_RATE_QUARANTINE:.0%}); clause wrapper, not a "
                f"discriminating construction on this population"
            )

        if not eligible:
            quarantined.append(egp_id)

        entries[egp_id] = {
            "level_norm": level,
            "level_rank": LEVEL_RANK.get(level, 0),
            "mandatory_tokens": count_mandatory_tokens(pattern),
            "in_list_size": max_in_list_size(pattern),
            "constrained": has_pos_or_dep(pattern),
            "pattern_len": len(pattern),
            "arbitration_eligible": eligible,
            "quarantine_reason": None if eligible else reason,
            "evidence": {
                "fixture_positive_count": len(rule["unit_tests"]["positives"]),
                "corpus_hit_rate": None if rate is None else round(rate, 6),
                "structurally_generic": generic,
                "structural_note": struct_reason or None,
            },
        }

    doc = {
        "schema_version": 1,
        "generated_from": Path(compiled_path).name,
        "specificity_key": [
            "-mandatory_tokens",
            "in_list_size (smaller = more specific)",
            "not constrained(POS/DEP)",
            "level_rank (highest band wins)",
            "span_len",
        ],
        "quarantine_policy": {
            "tier": "background",
            "purpose": "macro clause telemetry only (e.g. is the student producing full sentences)",
            "barred_from": [
                "coaching triggers",
                "highlights",
                "student friction tallies",
            ],
            "rule": "quarantined rules are reported in Detection.macro and never in Detection.candidates",
        },
        "evidence": {
            "rules_total": len(rules),
            "fixture_positives_total": fixture_total,
            "corpus_root": corpus,
            "corpus_turns_measured": corpus_info.get("turns", 0),
            "corpus_role_measured": corpus_info.get("role"),
            "corpus_hit_rate_quarantine_threshold": CORPUS_HIT_RATE_QUARANTINE,
            "structural_genericity_threshold_mandatory_tokens": MAX_MANDATORY_FOR_SPECIFIC,
        },
        "counts": {
            "arbitration_eligible": len(rules) - len(quarantined),
            "quarantined": len(quarantined),
            "levels_normalized": len(level_dirty),
        },
        "rules": entries,
    }

    out_path = Path(out_path)
    out_path.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    return doc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--compiled", default=str(COMPILED_PATH))
    ap.add_argument("--out", default=str(ARBITRATION_PATH))
    ap.add_argument("--corpus", default=os.environ.get("EGP_CORPUS") or None)
    ap.add_argument("--corpus-max-turns", type=int, default=None)
    args = ap.parse_args(argv)

    doc = build(
        Path(args.compiled),
        Path(args.out),
        corpus=args.corpus,
        corpus_max_turns=args.corpus_max_turns,
    )
    ev = doc["evidence"]
    print(f"wrote {args.out}")
    print(f"  rules              {ev['rules_total']}")
    print(f"  corpus turns       {ev['corpus_turns_measured'] or 'NOT MEASURED'}")
    print(f"  arbitration_eligible {doc['counts']['arbitration_eligible']}")
    print(f"  quarantined          {doc['counts']['quarantined']}")
    print(f"  levels normalized    {doc['counts']['levels_normalized']}")

    rules = {r["egp_id"]: r for r in json.loads(Path(args.compiled).read_text())}
    quarantined = [
        (egp_id, entry) for egp_id, entry in doc["rules"].items()
        if not entry["arbitration_eligible"]
    ]
    if quarantined:
        print("  quarantined (background tier, telemetry only):")
        for egp_id, entry in sorted(
            quarantined, key=lambda kv: -kv[1]["evidence"]["corpus_hit_rate"] or 0
        ):
            rate = entry["evidence"]["corpus_hit_rate"]
            rate_s = "n/a" if rate is None else f"{rate:.1%}"
            print(
                f"    [{rules[egp_id].get('level', '').strip():<2}] "
                f"{rules[egp_id].get('guideword', '')[:38]:<40} "
                f"corpus={rate_s:>7}  {entry['quarantine_reason']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
