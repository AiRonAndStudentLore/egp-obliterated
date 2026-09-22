"""
Discord & Friction Analyzer

Scans a Trill session's turns and NLP output to detect "discord", tension,
or conversational friction. Friction is highly valuable for the Heutagogical Loop
as it indicates points of misunderstanding, struggle, or deep debate.

Metrics detected:
- Frequent disagreement markers ("no", "actually", "but", "wait")
- Turn-taking clashes (interruptions, timestamp overlaps)
- Negative sentiment (if AssemblyAI sentiment analysis is available in raw_aai.json)
"""

import json
import os
import re

DISAGREEMENT_MARKERS = {"actually", "but", "no", "wait", "disagree", "wrong"}

def load_json(path):
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def analyze_discord(session_dir):
    """
    Analyzes the session for discord markers.
    Expects to be run in a directory containing transcript.txt, metrics.json,
    raw_aai.json, and the nlp JSONs.
    """
    
    # Locate files
    metrics_path = os.path.join(session_dir, "metrics.json")
    raw_aai_path = os.path.join(session_dir, "raw_aai.json")
    transcript_path = os.path.join(session_dir, "transcript.txt")
    
    # Also find the index nlp json
    nlp_path = None
    for f in os.listdir(session_dir):
        if f.endswith("--nlp.json"):
            nlp_path = os.path.join(session_dir, f)
            break
            
    if not nlp_path:
        return {"error": "No --nlp.json found for discord analysis."}
        
    nlp_data = load_json(nlp_path)
    if not nlp_data:
        return {"error": "Failed to load --nlp.json"}
        
    turns = nlp_data.get("turns_index", [])
    if not turns:
        return {"error": "No turns found in NLP data."}
        
    raw_aai = load_json(raw_aai_path) or {}
    
    friction_events = []
    
    # 1. Linguistic Disagreement Search
    # Using the detail layer (--nlp-tokens.json) if available, otherwise just regex on text.
    tokens_path = nlp_path.replace("--nlp.json", "--nlp-tokens.json")
    tokens_data = load_json(tokens_path)
    
    if tokens_data:
        vocab = tokens_data.get("vocab", [])
        for turn in tokens_data.get("turns", []):
            i, ts_ms, speaker, line = turn[0]
            words = []
            for r in turn[1]:
                text = r[0].lower()
                words.append(text)
                
            if any(marker in words for marker in DISAGREEMENT_MARKERS):
                # Count the density
                marker_count = sum(1 for w in words if w in DISAGREEMENT_MARKERS)
                if marker_count >= 1:
                    friction_events.append({
                        "type": "linguistic_disagreement",
                        "turn_i": i,
                        "ts_ms": ts_ms,
                        "speaker": speaker,
                        "markers_found": marker_count
                    })
                    
    # 2. Interruption / Turn-taking clash
    # Looking at rapid succession of timestamps (< 500ms diff)
    for idx in range(1, len(turns)):
        prev = turns[idx-1]
        curr = turns[idx]
        
        diff = curr["ts_ms"] - prev["ts_ms"]
        if diff < 1000 and prev["speaker"] != curr["speaker"]:
            friction_events.append({
                "type": "rapid_interruption",
                "turn_i": curr["i"],
                "ts_ms": curr["ts_ms"],
                "speaker": curr["speaker"],
                "diff_ms": diff
            })
            
    # 3. Sentiment Analysis (if AssemblyAI produced it)
    sentiment_results = raw_aai.get("sentiment_analysis_results", [])
    for sent in sentiment_results:
        if sent.get("sentiment") == "NEGATIVE":
            friction_events.append({
                "type": "negative_sentiment",
                "ts_ms": sent.get("start", 0),
                "speaker": sent.get("speaker", "UNKNOWN"),
                "text": sent.get("text", "")
            })
            
    return {
        "friction_score": len(friction_events),
        "friction_events": friction_events
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        session_dir = sys.argv[1]
        res = analyze_discord(session_dir)
        print(json.dumps(res, indent=2))
    else:
        print("Usage: python discord_analyzer.py <session_dir>")
