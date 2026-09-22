# AGENTS.md — EGP OBLITERATED

## What this project is

A compiler that translates English Grammar Profile (EGP) can-do statements into
**deterministic detector rules** for a learner-transcript analysis engine.
Each rule = `regex_triage` (fast prefilter) + `spacy_token_pattern` (spaCy Matcher tokens).

## Read first

- `SYSTEM_PROMPT.txt` — the complete compilation contract. It defines the output schema,
  the four cognitive domains for ontology mapping, unit-test requirements, and
  spaCy POS-tag quirks (Rule 5). Follow it exactly.
- `batches/batch_001_demonstratives.json` — a **golden example** of a fully passed batch.
  Mirror its structure and quality.
- `gate.py` — the validator that every rule must pass. If your regex does not compile
  or your spaCy pattern is malformed, this rejects the row.

## Session task convention

Task prompts arrive with two sections:

- `## TASK` — what to compile and where to write the output
- `## ROWS` — the JSON rows to compile

**Write ONLY the file the task names** (e.g. `batches/jules_batch_003.json`).
Do not modify `gate.py`, `build_batch.py`, `egp_compiled.json`, the database,
or anything else. No README updates. No refactoring.

## Output contract

A JSON array of rule objects, input order preserved. Each object = the input row
(keep `egp_id`, `level`, `super_category`, `sub_category`, `lexical_range`,
`guideword`, `can_do_statement` unchanged) plus:

```json
{
  "detection": {
    "regex_triage": "<python re.compile-able string>",
    "spacy_token_pattern": [{"LOWER": "would"}, {"OP": "?"}, {"LOWER": "like"}]
  },
  "unit_tests": {
    "positives": ["two realistic spoken utterances that MUST match"],
    "negatives": ["two near-miss distractors that MUST NOT match"]
  }
}
```

## Hard requirements

1. Every `regex_triage` must pass `python re.compile()` — verify each one before committing.
2. `spacy_token_pattern` is a **flat list of token dicts**. Valid attrs: `LOWER`, `LEMMA`,
   `POS`, `TAG`, `DEP`, `OP`, `IN`. No nested lists.
3. Exactly 2 positives + 2 negatives per rule. Negatives must contain overlapping
   vocabulary with the positives (they prove the rule isn't firing on surface similarity).
4. Design around en_core_web_sm POS quirks: sentence-initial capitalized adverbs tag as
   PROPN; prefer `LOWER` anchoring over `POS`; use `OP: "?"` for optional slots.
5. Handle contractions (`I'm`, `don't`, `it's`) explicitly in regexes.

## Quality bar

These rules run against real ESL learner speech (ASR transcripts, disfluencies included).
False positives poison downstream learner metrics. When in doubt, tighten the pattern —
a missed rare hit costs less than a wrong hit.
