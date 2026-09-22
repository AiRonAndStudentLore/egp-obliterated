# EGP 1222 Parser Specification

## Objective
The current system hardcodes 14 EGP categories directly into python logic. We need a system that can accurately identify all 1,222 EGP categories (from A1 to C2) defined in `egp_normalized.json`. Because these statements are currently natural language ("Can use 'but' to join..."), they must be systematically compiled into machine-readable declarative patterns that our advanced token matcher can execute against the NLP pipeline's token streams.

## The Challenge
The 1,222 descriptors in the EGP are abstract. For example:
- **Guideword:** `FORM: COMBINING TWO ADJECTIVES WITH 'BUT'`
- **Can-do:** `Can use 'but' to join a limited range of common adjectives, after 'be'.`

To detect this, the system needs a structured formula:
`[Token(POS=ADJ)] -> [Token(LEMMA="but")] -> [Token(POS=ADJ)]`

Some are even more complex, requiring specific dependency head matching, morphological tags, or complex sequences.

## Strategy: The EGP Pattern Compiler

We will build a pipeline (a "Compiler") to convert `egp_normalized.json` into a comprehensive ruleset: `1222_egp_patterns.json`.

### Phase 1: Algorithmic Seeding & LLM Generation
We cannot manually write 1,222 regex-like rules. We will build a generator script that iterates over `egp_normalized.json` and uses an LLM (via an API or offline model script) to translate the `can_do_statement`, `guideword`, and `examples` into our JSON schema. 

The prompt to the generation script will strictly enforce our token schema:
```json
{
  "egp_id": "1741163706316x198445876411383900",
  "name": "FORM: COMBINING TWO ADJECTIVES WITH 'BUT'",
  "pattern": [
    {"pos": "ADJ"},
    {"lemma": "but"},
    {"pos": "ADJ"}
  ]
}
```

### Phase 2: The Pattern Schema
The schema (already supported by our `advanced_egp_parser.py`) is capable of capturing the complexity of the 1222 rules:

1.  **Lexical Matching:** `{"lemma": "will"}`, `{"text": "actually"}`
2.  **Part-of-Speech/Tags:** `{"pos": "VERB"}`, `{"tag": "MD"}`
3.  **Morphological Features:** `{"morph": {"HAS": "Aspect=Prog"}}`
4.  **Multi-Choice:** `{"lemma": {"IN": ["have", "has", "had"]}}`
5.  **Repetition Operators:** 
    *   `{"OP": "?"}` (Optional modifiers/adverbs)
    *   `{"OP": "*"}` (Zero or more tokens, useful for skipping intervening words)
    *   `{"OP": "+"}` (One or more tokens)
6.  **Dependency Links (Future expansion):** `{"dep": "nsubj", "head_lemma": "be"}`

### Phase 3: The Execution Pipeline
1.  **Load:** `advanced_egp_parser.py` loads `1222_egp_patterns.json`.
2.  **Scan:** As `session_nlp.py` processes a turn, it passes the interned token rows to the parser.
3.  **Match:** The parser backtracks through the rules (using the operators `*`, `+`, `?`) and identifies all spans that match *any* of the 1222 EGP categories.
4.  **Emit:** It emits the exact EGP ID, which maps back to the CEFR level and category for the Heutagogical Loop and student metrics.

## Why this works
By decoupling the rules from the Python logic into a JSON pattern file, we can:
1. Update, fix, or tweak a rule for a specific EGP category without touching the parser engine.
2. Rapidly generate the rules using an LLM based on the Cambridge examples.
3. Keep the "fast path" of `session_nlp.py` blazing fast, as it just iterates over a JSON state machine rather than booting up 1,222 Python functions.
