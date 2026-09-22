"""
Advanced EGP (English Grammar Profile) Parser.
This module provides a declarative, regex-like token pattern matching engine
designed to scale up to all 1,222 EGP Can-Do statements.

It evaluates token rules against the normalized token 'rows' extracted per turn:
row: {"text": ..., "lemma": ..., "pos": ..., "tag": ..., "dep": ..., "morph": ...}

Pattern definitions support lists of token constraints:
- exact string matches (e.g. {"lemma": "have"})
- IN lists (e.g. {"lemma": {"IN": ["have", "has"]}})
- operators for repetition:
  "OP": "?" (0 or 1), "+" (1 or more), "*" (0 or more)
- structural lookaheads / dependency checks using a callback or multi-token span.
"""

import re
from typing import List, Dict, Any, Tuple

def _match_token(token: Dict[str, str], constraint: Dict[str, Any]) -> bool:
    """Evaluate a single token against a constraint dictionary."""
    for key, val in constraint.items():
        if key == "OP":
            continue
        
        token_val = token.get(key, "")
        
        # Exact match or IN list
        if isinstance(val, dict):
            if "IN" in val:
                if token_val not in val["IN"]:
                    return False
            elif "NOT_IN" in val:
                if token_val in val["NOT_IN"]:
                    return False
            elif "REGEX" in val:
                if not re.search(val["REGEX"], token_val):
                    return False
            elif "HAS" in val: # for morphology strings like "Tense=Past|VerbForm=Fin"
                if val["HAS"] not in token_val:
                    return False
        else:
            if token_val != val:
                return False
    return True

def find_matches(rows: List[Dict[str, str]], pattern: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
    """
    Finds contiguous spans in `rows` that match the `pattern`.
    Returns a list of (start_index, end_index) tuples (inclusive of start, inclusive of end).
    Supports OP modifiers: ?, +, *
    """
    matches = []
    n_rows = len(rows)
    
    # Very simple backtracking matcher for token streams
    def match_at(token_idx, pat_idx) -> List[int]:
        if pat_idx == len(pattern):
            return [token_idx]
            
        p = pattern[pat_idx]
        op = p.get("OP", "")
        
        # OP: ? (0 or 1)
        if op == "?":
            # try with 1
            if token_idx < n_rows and _match_token(rows[token_idx], p):
                res = match_at(token_idx + 1, pat_idx + 1)
                if res: return res
            # try with 0
            return match_at(token_idx, pat_idx + 1)
            
        # OP: * (0 or more)
        elif op == "*":
            # greedily consume
            max_consume = 0
            curr_idx = token_idx
            while curr_idx < n_rows and _match_token(rows[curr_idx], p):
                max_consume += 1
                curr_idx += 1
                
            for c in range(max_consume, -1, -1):
                res = match_at(token_idx + c, pat_idx + 1)
                if res: return res
            return []
            
        # OP: + (1 or more)
        elif op == "+":
            if token_idx >= n_rows or not _match_token(rows[token_idx], p):
                return []
            
            # consume at least 1, then greedily consume rest
            max_consume = 1
            curr_idx = token_idx + 1
            while curr_idx < n_rows and _match_token(rows[curr_idx], p):
                max_consume += 1
                curr_idx += 1
                
            for c in range(max_consume, 0, -1):
                res = match_at(token_idx + c, pat_idx + 1)
                if res: return res
            return []
            
        # Default (exactly 1)
        else:
            if token_idx < n_rows and _match_token(rows[token_idx], p):
                return match_at(token_idx + 1, pat_idx + 1)
            return []

    # Try matching from every starting position
    for start_idx in range(n_rows):
        res = match_at(start_idx, 0)
        if res:
            # res is a list of ending indices (exclusive). We take the first successful match end.
            end_idx = res[0] - 1
            if end_idx >= start_idx:
                matches.append((start_idx, end_idx))
                
    return matches

class EGPEngine:
    def __init__(self, patterns_map: Dict[str, List[Dict[str, Any]]]):
        """
        patterns_map: Dict mapping EGP_ID to the actual token pattern list.
        """
        self.patterns_map = patterns_map
        
    def analyze_turn(self, rows: List[Dict[str, str]], turn_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Applies all patterns to a turn.
        Returns a list of event objects.
        """
        events = []
        for egp_id, pattern in self.patterns_map.items():
            spans = find_matches(rows, pattern)
            for start, end in spans:
                span_text = " ".join(rows[i]["text"] for i in range(start, end + 1))
                events.append({
                    "turn": turn_info.get("i"),
                    "ts_ms": turn_info.get("ts_ms"),
                    "speaker": turn_info.get("speaker"),
                    "egp_id": egp_id,
                    "span_text": span_text,
                    "start_idx": start,
                    "end_idx": end
                })
        return events
