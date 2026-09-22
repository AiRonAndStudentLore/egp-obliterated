"""
EGP 1222 Pattern Compiler

This script serves as the framework for translating the 1222 natural language EGP
descriptors (from egp_normalized.json) into declarative token patterns. 

Because translating all 1222 statements accurately requires complex NLP/LLM interpretation
of the 'can_do_statement' and 'examples', this script provides the infrastructure.
It currently implements a keyword-based heuristic fallback to demonstrate the conversion
pipeline, but is designed to be hooked up to an LLM or a more robust rule-generation module.
"""

import json
import os
import re

def heuristic_translation(egp_entry):
    """
    A basic heuristic to generate a fallback pattern based on the text.
    In production, this function would call an LLM API with the guideword and examples
    to generate a highly accurate pattern schema.
    """
    statement = egp_entry.get("can_do_statement", "").lower()
    guideword = egp_entry.get("guideword", "").lower()
    
    pattern = []
    
    # 1. Very basic heuristic examples:
    if "two adjectives with 'but'" in guideword:
        pattern = [
            {"pos": "ADJ"},
            {"lemma": "but"},
            {"pos": "ADJ"}
        ]
    elif "two adjectives with 'and'" in guideword:
        pattern = [
            {"pos": "ADJ"},
            {"lemma": "and"},
            {"pos": "ADJ"}
        ]
    elif "present continuous" in guideword:
        pattern = [
            {"pos": "AUX", "morph": {"HAS": "Tense=Pres"}, "lemma": {"IN": ["be", "am", "is", "are", "'m", "'s", "'re"]}},
            {"pos": "ADV", "OP": "*"},
            {"pos": {"IN": ["VERB", "AUX"]}, "morph": {"HAS": "Aspect=Prog"}}
        ]
    else:
        # Fallback: Just look for a specific keyword if it's explicitly quoted
        # E.g. "Can use 'although'" -> look for lemma "although"
        quotes = re.findall(r"'([^']*)'", statement)
        if quotes:
            target_word = quotes[0].lower()
            if target_word.isalpha():
                pattern = [{"lemma": target_word}]
                
    if not pattern:
        # Absolute fallback for complex ones we can't easily parse without an LLM
        # We assign an empty pattern so we know it needs manual/LLM generation
        pattern = [] 
        
    return {
        "egp_id": egp_entry.get("egp_id"),
        "name": egp_entry.get("guideword"),
        "pattern": pattern
    }

def compile_egp_rules():
    input_path = ".trill-tools/EGP/egp_normalized.json"
    output_path = ".trill-tools/EGP/1222_egp_patterns.json"
    
    if not os.path.exists(input_path):
        print(f"Error: Could not find {input_path}")
        return
        
    with open(input_path, 'r', encoding='utf-8') as f:
        egp_data = json.load(f)
        
    compiled_patterns = []
    
    print(f"Processing {len(egp_data)} EGP statements...")
    
    for entry in egp_data:
        compiled_patterns.append(heuristic_translation(entry))
        
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(compiled_patterns, f, indent=2, ensure_ascii=False)
        
    generated = sum(1 for p in compiled_patterns if p.get("pattern"))
    empty = len(compiled_patterns) - generated
    
    print(f"Successfully generated {output_path}")
    print(f"Total Rules: {len(compiled_patterns)}")
    print(f"Populated Patterns (Heuristic): {generated}")
    print(f"Empty Patterns (Require LLM/Manual): {empty}")
    print("Note: The heuristic translation is a baseline. For full coverage, plug an LLM into the `heuristic_translation` function.")

if __name__ == "__main__":
    compile_egp_rules()
