import json

with open("batches/jules_batch_137.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Fix double backslash in negative lookahead (regex_triage string should be \\s so JSON parses to \s)
data[8]["detection"]["regex_triage"] = r"\b(?:in|on|at|to(?!\s+[a-z]+)|with|for|about|from|by|of)\s+(?:the|a|an|my|your|his|her|our|their)?\s*[a-z]+\b"

with open("batches/jules_batch_137.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
