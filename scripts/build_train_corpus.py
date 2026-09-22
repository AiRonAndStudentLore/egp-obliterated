"""Build training corpus for spaCy textcat: real learner utterances auto-labeled by our 150 gate-passed EGP rules.

Pipeline:
  1. Scan /home/hayron/By Student/*/lesson_deltas_ro/*/--data.json
  2. Filter: session must have metrics.json; utterance confidence >= 0.6; speaker == learner
  3. Split utterances into sentences (spaCy sentencizer)
  4. Auto-label: run egp_compiled.json rules (regex_triage + spacy_token_pattern) per sentence
  5. Emit spaCy textcat_multi format + stats JSON

Output:
  data/train_corpus.spacy-compatible.jsonl   (text, labels) pairs
  data/corpus_stats.json                      (counts, per-rule hit rates)
"""

import json
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path("/home/hayron/By Student")
EGP_DIR = Path("/home/hayron/MyProjects/EGP OBLITERATED")
OUT_DIR = EGP_DIR / "data"
OUT_DIR.mkdir(exist_ok=True)

MIN_CONFIDENCE = 0.6
MIN_WORDS = 3  # skip "Yeah." / "Okay." backchannels


def load_rules():
    compiled = json.loads((EGP_DIR / "egp_compiled.json").read_text())
    rules = compiled if isinstance(compiled, list) else compiled.get("rules", [])
    active = []
    for r in rules:
        det = r.get("detection", {})
        if det.get("regex_triage") or det.get("spacy_token_pattern"):
            active.append({
                "egp_id": r["egp_id"],
                "regex_triage": det.get("regex_triage"),
                "spacy_token_pattern": det.get("spacy_token_pattern"),
            })
    return active


def iter_learner_sentences():
    """Yield (student, session_id, sentence_text) for every qualifying learner sentence."""
    for student_dir in sorted(ROOT.iterdir()):
        deltas = student_dir / "lesson_deltas_ro"
        if not student_dir.is_dir() or not deltas.exists():
            continue
        for data_path in deltas.rglob("*--data.json"):
            metrics_path = data_path.with_name(data_path.name.replace("--data.json", "--metrics.json"))
            if not metrics_path.exists():
                continue  # speaker ID unverified
            try:
                data = json.loads(data_path.read_text())
                metrics = json.loads(metrics_path.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            learner = metrics.get("session_meta", {}).get("identified_learner")
            if not learner:
                continue
            session_id = data_path.name.replace("--data.json", "")
            for utt in data.get("utterances", []):
                if utt.get("speaker") != learner:
                    continue
                if utt.get("confidence", 0) < MIN_CONFIDENCE:
                    continue
                for sent in split_sentences(utt.get("text", "")):
                    if len(sent.split()) >= MIN_WORDS:
                        yield student_dir.name, session_id, sent


def split_sentences(text):
    # lightweight split — avoid loading spaCy here; rules re-tokenize anyway
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def main():
    rules = load_rules()
    print(f"Loaded {len(rules)} active rules from egp_compiled.json", flush=True)

    nlp = None
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm", disable=["ner"])
    except Exception as e:
        print(f"WARN: spaCy unavailable ({e}) — regex triage only", flush=True)

    matcher = None
    if nlp is not None:
        from spacy.matcher import Matcher
        matcher = Matcher(nlp.vocab)
        n_rules = 0
        for rule in rules:
            patterns = rule.get("spacy_token_pattern") or []
            if not patterns:
                continue
            # patterns may be a list of token-dicts (single pattern) or list of lists
            try:
                if patterns and isinstance(patterns[0], dict):
                    pattern_sets = [patterns]
                else:
                    pattern_sets = [p for p in patterns if isinstance(p, list) and p]
                for i, ps in enumerate(pattern_sets):
                    key = f"{rule['egp_id']}__{i}"
                    matcher.add(key, [ps])
                    n_rules += 1
            except Exception:
                continue
        print(f"Added {n_rules} spaCy matcher patterns", flush=True)

    compiled_regex = []
    for rule in rules:
        rx = rule.get("regex_triage")
        if not rx:
            continue
        try:
            compiled_regex.append((rule["egp_id"], re.compile(rx, re.IGNORECASE)))
        except re.error:
            continue
    print(f"Compiled {len(compiled_regex)} regex triage patterns", flush=True)

    examples = []
    label_counts = Counter()
    rule_hits = Counter()
    total_sentences = 0
    by_student = Counter()

    for student, session_id, sent in iter_learner_sentences():
        total_sentences += 1
        by_student[student] += 1
        labels = set()

        for egp_id, rx in compiled_regex:
            if rx.search(sent):
                labels.add(egp_id)
                rule_hits[egp_id] += 1

        if matcher is not None and sent:
            doc = nlp(sent)
            for match_id, start, end in matcher(doc):
                key = nlp.vocab.strings[match_id]
                egp_id = key.split("__")[0]
                labels.add(egp_id)
                rule_hits[egp_id] += 1

        if labels:
            label_counts.update(labels)
            examples.append({
                "text": sent,
                "labels": sorted(labels),
                "student": student,
                "session": session_id,
            })

        if total_sentences % 2000 == 0:
            print(f"  ...{total_sentences} sentences, {len(examples)} labeled", flush=True)

    out_path = OUT_DIR / "train_corpus.jsonl"
    with out_path.open("w") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    stats = {
        "total_learner_sentences": total_sentences,
        "labeled_sentences": len(examples),
        "label_rate": round(len(examples) / max(1, total_sentences), 4),
        "unique_labels": len(label_counts),
        "per_student_sentences": dict(by_student.most_common()),
        "top_rules_by_hits": label_counts.most_common(25),
        "rules_never_fired": len(rules) - len(label_counts),
    }
    (OUT_DIR / "corpus_stats.json").write_text(json.dumps(stats, indent=2))

    print(f"\nDONE: {total_sentences} learner sentences -> {len(examples)} labeled ({stats['label_rate']*100:.1f}%)")
    print(f"unique can-dos observed: {len(label_counts)} / {len(rules)} rules")
    print(f"rules that NEVER fired on real speech: {stats['rules_never_fired']}")
    print(f"wrote {out_path} + data/corpus_stats.json")


if __name__ == "__main__":
    main()
