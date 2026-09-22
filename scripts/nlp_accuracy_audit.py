"""NLP accuracy audit — empirical sanity check before trusting precomputed nlp.json.

Verifies:
1. vocabulary_pool.words actually appear in sibling transcript
2. ASR confidence distribution across corpus
3. speaker_id "verified" status — what does the heuristic actually check?
4. POS-tag sanity: run en_core_web_sm on a sample, compare counts vs nlp.json claims
5. Stale model risk: nlp.json claims en_core_web_trf but only sm installed locally
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict
import statistics

ROOT = Path("/home/hayron/By Student")

def find_session_files():
    """Return list of (student, nlp_path, transcript_path, data_path, metrics_path) tuples."""
    sessions = []
    for student_dir in ROOT.iterdir():
        if not student_dir.is_dir() or not (student_dir / "lesson_deltas_ro").exists():
            continue
        for nlp_path in (student_dir / "lesson_deltas_ro").rglob("*--nlp.json"):
            session_id = nlp_path.name.replace("--nlp.json", "")
            session_dir = nlp_path.parent
            transcript = session_dir / f"{session_id}--transcript.txt"
            data = session_dir / f"{session_id}--data.json"
            metrics = session_dir / f"{session_id}--metrics.json"
            if transcript.exists() and data.exists():
                sessions.append({
                    "student": student_dir.name,
                    "session": session_id,
                    "nlp": nlp_path,
                    "transcript": transcript,
                    "data": data,
                    "metrics": metrics if metrics.exists() else None,
                })
    return sessions

def normalize_word(w):
    return re.sub(r"[^\w']", "", w.lower()).strip()

def audit_vocabulary_coverage(nlp, transcript_text):
    """Check: do vocabulary_pool.words actually appear in the transcript?"""
    pool = nlp.get("vocabulary_pool", {}).get("words", [])
    if not pool:
        return None
    transcript_lower = transcript_text.lower()
    in_text = 0
    not_in_text = []
    for entry in pool[:100]:  # sample top 100
        word = entry.get("word", "")
        if not word:
            continue
        if word.lower() in transcript_lower or normalize_word(word) in transcript_lower:
            in_text += 1
        else:
            not_in_text.append((word, entry.get("lemma", "?"), entry.get("count", 0)))
    return {
        "pool_size": len(pool),
        "sampled": 100,
        "in_transcript": in_text,
        "missing_examples": not_in_text[:10],
    }

def audit_asr_confidence(data):
    """Distribution of utterance-level confidence."""
    confs = [u["confidence"] for u in data["utterances"] if "confidence" in u]
    if not confs:
        return None
    tiers = {"high(>=0.85)": 0, "mid(0.6-0.85)": 0, "low(<0.6)": 0}
    for c in confs:
        if c >= 0.85:
            tiers["high(>=0.85)"] += 1
        elif c >= 0.6:
            tiers["mid(0.6-0.85)"] += 1
        else:
            tiers["low(<0.6)"] += 1
    return {
        "count": len(confs),
        "min": min(confs),
        "max": max(confs),
        "mean": round(statistics.mean(confs), 4),
        "median": round(statistics.median(confs), 4),
        "stdev": round(statistics.stdev(confs), 4) if len(confs) > 1 else 0,
        "tiers": tiers,
    }

def audit_speaker_id_method(metrics):
    """Read the metrics.json speaker identification methodology."""
    if not metrics:
        return None
    return {
        "identified_learner": metrics.get("session_meta", {}).get("identified_learner"),
        "identified_tutor": metrics.get("session_meta", {}).get("identified_tutor"),
        "speakers_listed": metrics.get("session_meta", {}).get("speakers", []),
        "original_filename": metrics.get("session_meta", {}).get("original_filename"),
        "has_confidence_stats": "confidence_stats" in metrics,
        "speakers_with_confidence": list(metrics.get("confidence_stats", {}).keys()),
    }

def audit_pos_distribution_match(nlp, transcript_text):
    """Cross-check nlp.json POS counts vs re-derived POS from transcript text.
    Note: re-derivation uses en_core_web_sm (only one installed), nlp.json used en_core_web_trf.
    We expect SOME divergence but ratios should be similar."""
    try:
        import spacy
        nlp_sm = spacy.load("en_core_web_sm")
    except Exception as e:
        return {"error": str(e)}

    # Take learner-only text (filter to non-tutor speaker — but we don't have labels here,
    # so just sample first 2000 chars of transcript)
    sample_text = transcript_text[:2000]
    doc = nlp_sm(sample_text)
    sm_pos = Counter(tok.pos_ for tok in doc if not tok.is_space and not tok.is_punct)

    # Get nlp.json claims for the learner speaker (if identifiable)
    speakers = nlp.get("speakers", {})
    learner_name = None
    for name, info in speakers.items():
        if info.get("role") == "learner":
            learner_name = name
            break
    if not learner_name:
        learner_name = list(speakers.keys())[1] if len(speakers) > 1 else None
    if not learner_name or learner_name not in speakers:
        return {"error": "no learner speaker found"}
    trf_learner_pos = speakers[learner_name].get("pos_dist", {})

    # Compare ratios for major POS
    sm_total = sum(sm_pos.values())
    trf_total = sum(trf_learner_pos.values())
    if sm_total == 0 or trf_total == 0:
        return {"error": "zero counts"}
    comparison = {}
    for pos in ["NOUN", "VERB", "ADJ", "ADV", "PRON", "DET", "ADP", "AUX"]:
        sm_pct = sm_pos.get(pos, 0) / sm_total * 100
        trf_pct = trf_learner_pos.get(pos, 0) / trf_total * 100
        comparison[pos] = {
            "sm_pct": round(sm_pct, 1),
            "trf_pct": round(trf_pct, 1),
            "delta_pct": round(sm_pct - trf_pct, 1),
        }
    return {
        "learner_speaker": learner_name,
        "comparison": comparison,
        "sm_sample_words": sm_total,
        "trf_total_tokens": trf_total,
    }

def main():
    import sys
    sessions = find_session_files()
    print(f"Found {len(sessions)} sessions with both nlp.json + transcript + data.json")
    print()

    # Pick 5 sessions spread across students
    by_student = defaultdict(list)
    for s in sessions:
        by_student[s["student"]].append(s)
    sample = []
    for student, sess_list in sorted(by_student.items()):
        if sess_list:
            sample.append(sess_list[0])
        if len(sample) >= 6:
            break

    print("=" * 80)
    print("VOCABULARY POOL COVERAGE (do nlp.json words actually appear in transcript?)")
    print("=" * 80)
    for s in sample:
        try:
            nlp = json.loads(s["nlp"].read_text())
            transcript = s["transcript"].read_text()
            cov = audit_vocabulary_coverage(nlp, transcript)
            if cov:
                print(f"\n{s['student']} / {s['session']}:")
                print(f"  pool_size={cov['pool_size']}, sampled={cov['sampled']}, in_transcript={cov['in_transcript']}/{cov['sampled']}")
                if cov["missing_examples"]:
                    print(f"  MISSING examples (word | lemma | count):")
                    for w, l, c in cov["missing_examples"]:
                        print(f"    '{w}' (lemma={l}, count={c})")
        except Exception as e:
            print(f"\n{s['student']} / {s['session']}: ERROR {e}")

    print()
    print("=" * 80)
    print("ASR CONFIDENCE DISTRIBUTION (per-utterance)")
    print("=" * 80)
    all_confs = []
    for s in sessions:
        try:
            data = json.loads(s["data"].read_text())
            audit = audit_asr_confidence(data)
            if audit:
                all_confs.append((s["student"], s["session"], audit))
        except Exception:
            pass
    print(f"\nTotal sessions with confidence: {len(all_confs)}")
    if all_confs:
        overall_means = [a[2]["mean"] for a in all_confs if a[2]]
        overall_lows = [a[2]["tiers"]["low(<0.6)"] / max(1, a[2]["count"]) for a in all_confs if a[2]]
        print(f"Cross-session mean of mean-confidence: {round(statistics.mean(overall_means), 4)}")
        print(f"Cross-session mean of low-tier ratio:   {round(statistics.mean(overall_lows), 4)}")
        print(f"\nFirst 5 sessions:")
        for student, sess, a in all_confs[:5]:
            print(f"  {student}/{sess}: mean={a['mean']}, low_tier={a['tiers']['low(<0.6)']}/{a['count']}")

    print()
    print("=" * 80)
    print("SPEAKER ID METHODOLOGY")
    print("=" * 80)
    for s in sample:
        if s["metrics"]:
            try:
                m = json.loads(s["metrics"].read_text())
                info = audit_speaker_id_method(m)
                print(f"\n{s['student']} / {s['session']}:")
                print(f"  learner: {info['identified_learner']}, tutor: {info['identified_tutor']}")
                print(f"  speakers_in_meta: {info['speakers_listed']}")
                print(f"  speakers_with_confidence_stats: {info['speakers_with_confidence']}")
                print(f"  source file: {info['original_filename']}")
            except Exception as e:
                print(f"\n{s['student']} / {s['session']}: ERROR {e}")
        else:
            print(f"\n{s['student']} / {s['session']}: NO metrics.json")

    print()
    print("=" * 80)
    print("POS DISTRIBUTION: en_core_web_sm (local) vs en_core_web_trf (nlp.json claims)")
    print("=" * 80)
    for s in sample[:3]:  # only 3 — POS tagging is slow
        try:
            nlp = json.loads(s["nlp"].read_text())
            transcript = s["transcript"].read_text()
            audit = audit_pos_distribution_match(nlp, transcript)
            if "error" in audit:
                print(f"\n{s['student']} / {s['session']}: ERROR {audit['error']}")
                continue
            print(f"\n{s['student']} / {s['session']} (learner={audit['learner_speaker']}):")
            print(f"  {'POS':<8} {'sm %':>7} {'trf %':>7} {'delta':>8}")
            for pos, vals in audit["comparison"].items():
                print(f"  {pos:<8} {vals['sm_pct']:>7} {vals['trf_pct']:>7} {vals['delta_pct']:>+8}")
        except Exception as e:
            print(f"\n{s['student']} / {s['session']}: ERROR {e}")

if __name__ == "__main__":
    main()
