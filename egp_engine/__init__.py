"""EGP detection engine.

Deterministic runtime over `egp_compiled.json` for ESL learner transcripts.

Design decisions and the measurements that forced them:

  * ONE spaCy parse + ONE shared Matcher holding every rule, registered under an
    INTEGER index. spaCy hashes string keys to int64 and `Matcher.get` cannot
    reverse a string key, so integer keys are the only lossless option.
  * NO Aho-Corasick / keyword prefilter. A prefiltered Matcher must be rebuilt per
    candidate set; Matcher construction then dominates and the whole thing measured
    3.2x SLOWER than one unfiltered Matcher, while dropping ~27% of matches.
  * RANKING, not selection. Multiple grammar phenomena legitimately fire on the same
    tokens. `spacy.util.filter_spans` picks longest-then-leftmost, which on this
    dataset crowns generic A1 clause wrappers and discards the specific rules.
    Overlaps are preserved; the engine returns a scored, ranked top-k.
  * TWO STAGES WITH PROVENANCE. regex_triage and spacy_token_pattern agree on 99.9%
    of synthetic fixtures but disagree on real ASR in both directions. Both stages
    run; disagreement is recorded, never silently dropped.
"""

from egp_engine.load import CompiledRules, load
from egp_engine.arbitrate import ArbitrationPolicy, rank_candidates
from egp_engine.detect import (
    Detection,
    TurnResult,
    detect,
    detect_batch,
    detect_turns,
    is_echo,
    normalize,
)

__all__ = [
    "ArbitrationPolicy",
    "CompiledRules",
    "Detection",
    "TurnResult",
    "detect",
    "detect_batch",
    "detect_turns",
    "is_echo",
    "load",
    "normalize",
    "rank_candidates",
]
