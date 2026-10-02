"""Calibration against the corpus's own EGP distillation.

The `egp.events[]` block in each session's `--nlp.json` is an independent,
deterministic distillation of the grammar structures actually present, keyed by
`{turn, line, speaker, category, egp_level}`. It is the only ground truth in the
project that was not written by the same compiler process that produced
`egp_compiled.json`, so it is the only honest check on whether the detector is
calibrated to real learner speech.

Measured baseline over 5,595 learner events from 120 sessions:

    category agreement     62.1%
    band skew              severe. Reference is A1-heavy (3520 A1 / 1724 A2 /
                           351 B1, zero C1/C2); the engine reports B1-heavy
                           (936 A1 / 930 A2 / 1404 B1) and attributes C1/C2 to
                           learners the reference places at A1.

The band skew is NOT an arbitration artifact. Flipping the level tie-break moves
agreement 62.1% -> 62.6% and leaves the skew substantially intact, so it is a
property of the compiled patterns themselves: leniency scales with vocabulary
breadth, and higher bands are compiled with wider `IN` lists over rarer
vocabulary, so a B1 pattern fires on hesitant A1 speech more readily than the A1
pattern meant to describe it. Fixing that means recompiling band-weighted, not
retuning the ranking.
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
from pathlib import Path
from typing import Any

from egp_engine import ArbitrationPolicy, detect_batch, load
from egp_engine.detect import normalize

TURN_LINE = re.compile(r"^\s*\[\d+\]\s+([A-Za-z0-9_]+)\s*:\s*(.*)$")

DEFAULT_CORPUS = os.environ.get("EGP_CORPUS", "/home/hayron/By Student")
DEFAULT_SESSIONS = 120


def collect_events(
    corpus_root: str | Path = DEFAULT_CORPUS,
    max_sessions: int = DEFAULT_SESSIONS,
) -> tuple[list[str], list[dict[str, Any]]]:
    """Pair every learner EGP event with the transcript line it came from."""
    root = Path(corpus_root)
    if not root.is_dir():
        return [], []
    texts: list[str] = []
    events: list[dict[str, Any]] = []

    for path in sorted(root.rglob("*--nlp.json"))[:max_sessions]:
        try:
            doc = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        evs = (doc.get("egp") or {}).get("events") or []
        if not evs:
            continue
        ref = (doc.get("reference") or {}).get("transcript")
        if not ref:
            continue
        tpath = path.parent / ref
        if not tpath.exists():
            continue
        learner = (doc.get("analysis") or {}).get("learner") or "B"

        lines: dict[int, tuple[str, str]] = {}
        for line in tpath.read_text(errors="ignore").splitlines():
            m = TURN_LINE.match(line)
            if m:
                lines[len(lines) + 1] = (m.group(1), m.group(2).strip())

        for ev in evs:
            if ev.get("speaker") != learner:
                continue
            got = lines.get(ev.get("line") or 0)
            if not got or not got[1]:
                continue
            texts.append(got[1])
            events.append(
                {
                    "category": ev.get("category") or "",
                    "egp_level": ev.get("egp_level") or "",
                    "structure": ev.get("structure") or "",
                    "span": ev.get("span") or "",
                }
            )
    return texts, events


def _same_category(rule_super: str, truth: str) -> bool:
    if not rule_super or not truth:
        return False
    up_rule, up_truth = rule_super.upper(), truth.upper()
    return up_rule in up_truth or up_truth.startswith(up_rule[:8])


def calibrate(
    compiled=None,
    corpus_root: str | Path = DEFAULT_CORPUS,
    max_sessions: int = DEFAULT_SESSIONS,
    top_k: int = 12,
    **policy_kwargs,
) -> dict[str, Any]:
    compiled = compiled or load()
    texts, events = collect_events(corpus_root, max_sessions)
    if not texts:
        return {"error": f"no ground-truth events found under {corpus_root}"}

    dets = detect_batch(texts, compiled, ArbitrationPolicy(top_k=top_k, **policy_kwargs))

    agree = 0
    by_category_truth: collections.Counter = collections.Counter()
    by_category_engine: collections.Counter = collections.Counter()
    band_truth: collections.Counter = collections.Counter()
    band_engine: collections.Counter = collections.Counter()

    for det, ev in zip(dets, events):
        cat, lv = ev["category"], ev["egp_level"]
        by_category_truth[cat] += 1
        band_truth[lv] += 1
        for cand in det.candidates:
            if _same_category(cand.super_category, cat):
                agree += 1
                by_category_engine[cat] += 1
                band_engine[cand.level] += 1
                break

    total = len(texts)
    return {
        "corpus_root": str(corpus_root),
        "sessions": max_sessions,
        "learner_events": total,
        "category_agreement_pct": round(100.0 * agree / total, 2),
        "categories": {
            cat: {"truth": n, "engine": by_category_engine.get(cat, 0)}
            for cat, n in by_category_truth.most_common(20)
        },
        "bands": {
            band: {"truth": band_truth.get(band, 0), "engine": band_engine.get(band, 0)}
            for band in sorted(set(band_truth) | set(band_engine))
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    ap.add_argument("--sessions", type=int, default=DEFAULT_SESSIONS)
    ap.add_argument("--top-k", type=int, default=12)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    report = calibrate(
        corpus_root=args.corpus, max_sessions=args.sessions, top_k=args.top_k
    )
    if args.json or "error" in report:
        print(json.dumps(report, indent=2))
        return 1 if "error" in report else 0

    print(f"corpus        {report['corpus_root']}  ({report['sessions']} sessions)")
    print(f"learner events with a resolvable line: {report['learner_events']}")
    print(f"category agreement: {report['category_agreement_pct']}%")
    print("\n  category                          truth  engine")
    for cat, counts in report["categories"].items():
        print(f"    {cat[:32]:<34} {counts['truth']:>5} {counts['engine']:>6}")
    print("\n  band     truth  engine")
    for band, counts in report["bands"].items():
        print(f"    {band:<7} {counts['truth']:>5} {counts['engine']:>6}")
    print(
        "\nBand skew is a property of the compiled patterns, not of arbitration: "
        "leniency scales with vocabulary\nbreadth, so higher bands over-fire on "
        "hesitant A1 speech. Flipping the level\ntie-break moves agreement by "
        "<1 point and leaves the skew intact."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
