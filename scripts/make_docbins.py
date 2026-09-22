"""Convert train_corpus.jsonl -> spaCy DocBin (train/dev/test) for textcat_multilabel training.

Split: stratified-ish by student — 90% train / 5% dev / 5% test.
Labels: every egp_id observed in the corpus.
"""

import json
import random
from pathlib import Path

import spacy
from spacy.tokens import DocBin
from collections import Counter

EGP_DIR = Path("/home/hayron/MyProjects/EGP OBLITERATED")
DATA = EGP_DIR / "data"
random.seed(42)

def main():
    examples = [json.loads(line) for line in (DATA / "train_corpus.jsonl").open()]
    all_labels = sorted({l for ex in examples for l in ex["labels"]})
    print(f"{len(examples)} examples, {len(all_labels)} labels")

    # per-student split: whole students go to dev/test (cleanest held-out design)
    students = sorted({ex["student"] for ex in examples})
    random.shuffle(students)
    test_students = set(students[:2])
    dev_students = set(students[2:3])
    print(f"test students: {sorted(test_students)}, dev students: {sorted(dev_students)}")

    nlp = spacy.blank("en")
    bins = {"train": DocBin(), "dev": DocBin(), "test": DocBin()}
    counts = Counter()

    for ex in examples:
        if ex["student"] in test_students:
            split = "test"
        elif ex["student"] in dev_students:
            split = "dev"
        else:
            split = "train"
        doc = nlp.make_doc(ex["text"])
        doc.cats = {l: (1.0 if l in ex["labels"] else 0.0) for l in all_labels}
        bins[split].add(doc)
        counts[split] += 1

    for split, bin_ in bins.items():
        path = DATA / f"{split}.spacy"
        bin_.to_disk(path)
        print(f"{split}: {counts[split]} docs -> {path}")

    (DATA / "labels.json").write_text(json.dumps(all_labels))

if __name__ == "__main__":
    main()
