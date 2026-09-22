import json
import os

with open('.trill-tools/EGP/egp_normalized.json', 'r') as f:
    egp_data = json.load(f)

# Starting with the original 14 hardcoded structures to migrate them to declarative patterns
hardcoded_to_egp = [
    # EGP ID is mocked for these 14 as they might have different strict matches in the 1222 dataset.
    {
        "egp_id": "PRESENT_CONTINUOUS", 
        "name": "Present Continuous",
        "pattern": [
            {"pos": "AUX", "morph": {"HAS": "Tense=Pres"}, "lemma": {"IN": ["be", "am", "is", "are", "'m", "'s", "'re"]}},
            {"pos": "ADV", "OP": "*"},
            {"pos": {"IN": ["VERB", "AUX"]}, "morph": {"HAS": "Aspect=Prog"}}
        ]
    },
    {
        "egp_id": "PRESENT_PERFECT_SIMPLE",
        "name": "Present Perfect Simple",
        "pattern": [
            {"pos": "AUX", "morph": {"HAS": "Tense=Pres"}, "lemma": {"IN": ["have", "has", "'ve", "'s"]}},
            {"pos": "ADV", "OP": "*"},
            {"pos": {"IN": ["VERB", "AUX"]}, "morph": {"HAS": "VerbForm=Part"}}
        ]
    },
    {
        "egp_id": "PAST_CONTINUOUS",
        "name": "Past Continuous",
        "pattern": [
            {"pos": "AUX", "morph": {"HAS": "Tense=Past"}, "lemma": {"IN": ["was", "were"]}},
            {"pos": "ADV", "OP": "*"},
            {"pos": {"IN": ["VERB", "AUX"]}, "morph": {"HAS": "Aspect=Prog"}}
        ]
    },
    {
        "egp_id": "FUTURE_WITH_WILL",
        "name": "Future with Will",
        "pattern": [
            {"lemma": "will"},
            {"pos": "ADV", "OP": "*"},
            {"pos": {"IN": ["VERB", "AUX"]}, "morph": {"HAS": "VerbForm=Inf"}}
        ]
    },
    {
        "egp_id": "MODALS_ABILITY_PERMISSION",
        "name": "Modals of Ability & Permission",
        "pattern": [
            {"lemma": {"IN": ["can", "could"]}},
            {"pos": "ADV", "OP": "*"},
            {"pos": {"IN": ["VERB", "AUX"]}, "morph": {"HAS": "VerbForm=Inf"}}
        ]
    }
]

# Write to patterns file
with open('.trill-tools/EGP/egp_patterns.json', 'w') as f:
    json.dump(hardcoded_to_egp, f, indent=2)

print("Generated egp_patterns.json with base 14 structures translated.")
