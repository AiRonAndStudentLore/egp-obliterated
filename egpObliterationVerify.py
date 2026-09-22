import json
import re
import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")

with open("egp_compiled.json") as f:
    rules = json.load(f)

for rule in rules:
    rule_id = rule["egp_id"]
    rx = re.compile(rule["detection"]["regex_triage"], re.I)

    # Setup spaCy Matcher
    matcher = Matcher(nlp.vocab)
    matcher.add(rule_id, [rule["detection"]["spacy_token_pattern"]])

    # Test positives
    for pos in rule["unit_tests"]["positives"]:
        assert rx.search(pos), f"Regex failed positive on [{rule_id}]: {pos}"
        doc = nlp(pos)
        assert len(matcher(doc)) > 0, f"spaCy failed positive on [{rule_id}]: {pos}"

    # Test negatives
    for neg in rule["unit_tests"]["negatives"]:
        assert not rx.search(neg), f"Regex false positive on [{rule_id}]: {neg}"
        doc = nlp(neg)
        assert len(matcher(doc)) == 0, f"spaCy false positive on [{rule_id}]: {neg}"

print("Batch verified successfully.")
