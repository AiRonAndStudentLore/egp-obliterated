"""Shared fixtures.

The whole fixture matrix is computed ONCE per session via `nlp.pipe` and then
asserted against. Parametrising 1,218 rules into 1,218 independent tests that each
re-parse their own sentences would re-do the same 4,873 parses thousands of times.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from egp_engine.load import COMPILED_PATH, load

CORPUS_ROOT = os.environ.get("EGP_CORPUS", "/home/hayron/By Student")

LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2"}

#: Sessions used for the ground-truth calibration. 60 resolves ~2,800 learner
#: EGP events, which is enough to see a several-point move in agreement.
CALIBRATION_SESSIONS = 60

#: Every attribute spaCy's Matcher actually accepts on a token dict.
SPACY_TOKEN_ATTRS = {
    "ORTH", "TEXT", "LOWER", "NORM", "LEMMA", "LENGTH", "IS_ALPHA", "IS_DIGIT",
    "IS_SPACE", "IS_LOWER", "IS_TITLE", "IS_UPPER", "IS_PUNCT", "LIKE_NUM",
    "LIKE_WORD", "LIKE_DATE", "PERCENT", "IS_STOP", "POS", "TAG", "DEP",
    "HEAD", "ENT_TYPE", "ENT_IOB", "ENT_ID", "LEMMA_", "MORPH", "OP", "IN",
    "IS_SENT_START", "SHAPE", "IDX", "ENT_KB_ID", "ENT_LABEL", "ENT_DESC",
}

#: The narrower set `SYSTEM_PROMPT.txt` instructs the compiler to use. Patterns
#: reaching outside it still run — spaCy accepts them — but they are out of contract
#: and are reported separately by `test_out_of_contract_token_attrs`.
CONTRACT_TOKEN_ATTRS = {"LOWER", "LEMMA", "POS", "TAG", "DEP", "OP", "IN"}


@pytest.fixture(scope="session")
def rules() -> list[dict]:
    return json.loads(Path(COMPILED_PATH).read_text())


@pytest.fixture(scope="session")
def compiled():
    return load()


@pytest.fixture(scope="session")
def matrix(compiled, rules) -> dict:
    """Per-rule own-fixture results plus the cross-rule collision matrix.

    This is the dimension `gate.py` structurally cannot see: `gate.py` builds a
    fresh Matcher per rule and only ever checks that rule against its own fixtures,
    so no collision between two rules is observable there.
    """
    flat: list[tuple[str, str, str]] = []
    for rule in rules:
        for pos in rule["unit_tests"]["positives"]:
            flat.append((rule["egp_id"], "pos", pos))
        for neg in rule["unit_tests"]["negatives"]:
            flat.append((rule["egp_id"], "neg", neg))

    texts = [t for _, _, t in flat]
    docs = list(compiled.nlp.pipe(texts, batch_size=256))

    own: dict[str, dict] = {
        r["egp_id"]: {"pos_fired": False, "neg_fired": False, "pos_foreign": 0, "neg_any": 0}
        for r in rules
    }
    for (egp_id, kind, _text), doc in zip(flat, docs):
        fired = {key for key, _s, _e in compiled.matcher(doc)}
        # The Matcher is keyed by INTEGER rule index, never by egp_id.
        idx = compiled.index_by_id[egp_id]
        if kind == "pos":
            if idx in fired:
                own[egp_id]["pos_fired"] = True
            own[egp_id]["pos_foreign"] = len(fired - {idx})
        else:
            if idx in fired:
                own[egp_id]["neg_fired"] = True
            own[egp_id]["neg_any"] = len(fired)

    sizes = [len({key for key, _s, _e in compiled.matcher(d)}) for d in docs]
    return {"own": own, "per_text_fired": sizes, "texts": texts, "kinds": [k for _, k, _ in flat]}


@pytest.fixture(scope="session")
def collision_budget() -> dict:
    """Committed ceilings. Tightening these is how precision improves; loosening them
    is how it silently regresses. Values are the measured baseline."""
    return {
        "max_mean_rules_per_positive": 30.0,
        "max_positives_with_any_foreign_rule_pct": 100.0,
        "max_mean_rules_per_negative": 30.0,
    }


@pytest.fixture(scope="session")
def corpus_turns():
    if not Path(CORPUS_ROOT).is_dir():
        pytest.skip(f"corpus not available at {CORPUS_ROOT}")
    from egp_engine.build_arbitration import read_turns

    turns = read_turns(CORPUS_ROOT)
    if not turns:
        pytest.skip("no turns parsed from corpus")
    return turns


@pytest.fixture(scope="session")
def calibration(compiled, corpus_turns):
    """One calibration run shared by every test in `test_calibration.py`.

    Each separate call re-parses the corpus, and three of them pushed the suite past
    five minutes.
    """
    from egp_engine.calibrate import calibrate

    report = calibrate(compiled, max_sessions=CALIBRATION_SESSIONS)
    if "error" in report:
        pytest.skip(report["error"])
    return report
