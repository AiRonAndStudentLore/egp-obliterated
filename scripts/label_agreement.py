"""Label verification Layer 1: independent LLM second-opinion on rule-labeled corpus.

For each active rule: sample sentences where the rule FIRED (positives) and
where it did NOT (negatives, near-miss preferred). Ask a cloud LLM — given ONLY
the can-do statement, no rules — whether each sentence demonstrates the can-do.
Agreement rate per rule = label quality score.

Output: data/label_agreement.json
  per-rule: {hits_checked, llm_agrees_on_hits, false_positive_rate,
             nonhits_checked, llm_disagrees_on_nonhits, blind_spot_rate,
             verdict: solid|suspect|critical}

Uses OPENROUTER_API_KEY + gemini-2.5-flash-lite via compile_batch.call_openrouter.
"""

import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "/home/hayron/MyProjects/EGP OBLITERATED")
from compile_batch import call_openrouter

EGP_DIR = Path("/home/hayron/MyProjects/EGP OBLITERATED")
DATA = EGP_DIR / "data"
CORPUS = DATA / "train_corpus.jsonl"
MODEL = "z-ai/glm-5.3-flash"
FALLBACK_MODEL = "google/gemini-2.5-flash-lite"
HITS_PER_RULE = 8
NONHITS_PER_RULE = 5
CONCURRENCY = 12
random.seed(7)


def load_corpus_by_label():
    """Map egp_id -> hit sentences. Nonhits for rule X = corpus sentences lacking label X."""
    hits = {}
    all_sents = []
    for line in CORPUS.open():
        ex = json.loads(line)
        all_sents.append(ex["text"])
        for l in ex["labels"]:
            hits.setdefault(l, []).append(ex["text"])
    return hits, all_sents


def llm_verdicts(can_do, sentences, expecting, key):
    kind = "does demonstrate" if expecting == "hit" else "does NOT demonstrate"
    listing = "\n".join(f"{i+1}. {s}" for i, s in enumerate(sentences))
    prompt = (
        f"Can-do statement: {can_do}\n\n"
        f"For each numbered sentence, answer strictly YES or NO: the sentence {kind} "
        f"the grammar structure described. Judge meaning and structure, not style. "
        f"Spoken register, minor disfluencies (um, repeated words) are fine.\n\n"
        f"{listing}\n\n"
        f'Reply with ONLY: {{"answers": ["YES" or "NO", ...]}} — one per sentence, in order.'
    )
    for model in (MODEL, FALLBACK_MODEL):
        try:
            resp = call_openrouter(key, model, [
                {"role": "system", "content": "You are a precise ESL grammar annotator. Output JSON only. Be brief."},
                {"role": "user", "content": prompt},
            ], max_tokens=1500)
            msg = resp["choices"][0]["message"]
            raw = msg.get("content")
            if not raw and msg.get("reasoning"):
                tail = msg["reasoning"][-600:]
                if "{" in tail:
                    raw = tail[tail.rindex("{"):]
            data = json.loads(raw.strip())
            arr = data.get("answers") if isinstance(data, dict) else data
            arr = [str(x).strip().upper().startswith("Y") for x in arr]
            if len(arr) == len(sentences):
                return arr
        except Exception:
            continue
    return None


def judge_one_rule(egp_id, rule, hit_sents, nonhit_sents, key):
    can_do = rule.get("can_do_statement", "")
    fp = bs = None
    if hit_sents:
        ans = llm_verdicts(can_do, hit_sents, "hit", key)
        if ans:
            fp = 1 - sum(1 for a in ans if a) / len(hit_sents)
    if nonhit_sents:
        ans = llm_verdicts(can_do, nonhit_sents, "nonhit", key)
        if ans:
            bs = sum(1 for a in ans if a) / len(nonhit_sents)
    verdict = "no_data"
    if fp is not None and bs is not None:
        verdict = ("solid" if fp <= 0.25 and bs <= 0.25
                   else "critical" if fp >= 0.5 or bs >= 0.5 else "suspect")
    return egp_id, {
        "guideword": rule.get("guideword"),
        "can_do": can_do[:90],
        "hits_checked": len(hit_sents),
        "false_positive_rate": fp,
        "nonhits_checked": len(nonhit_sents),
        "blind_spot_rate": bs,
        "verdict": verdict,
    }


def parse_answers(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").lstrip("json").strip()
    try:
        arr = json.loads(raw)
        return [str(x).strip().upper().startswith("Y") for x in arr]
    except Exception:
        yes = [x.strip().upper().startswith("Y") for x in raw.split(",")]
        return yes if yes else None


def judge_one_rule(egp_id, rule, hit_sents, nonhit_sents, key):
    fp = bs = None
    if hit_sents:
        ans = llm_verdicts(rule.get("can_do_statement", ""), hit_sents, "hit", key)
        if ans:
            fp = 1 - sum(1 for a in ans if a) / len(hit_sents)
    if nonhit_sents:
        ans = llm_verdicts(rule.get("can_do_statement", ""), nonhit_sents, "nonhit", key)
        if ans:
            bs = sum(1 for a in ans if a) / len(nonhit_sents)
    verdict = "no_data"
    if fp is not None and bs is not None:
        verdict = ("solid" if fp <= 0.25 and bs <= 0.25
                   else "critical" if fp >= 0.5 or bs >= 0.5 else "suspect")
    return egp_id, {
        "guideword": rule.get("guideword"),
        "can_do": rule.get("can_do_statement", "")[:90],
        "hits_checked": len(hit_sents),
        "false_positive_rate": fp,
        "nonhits_checked": len(nonhit_sents),
        "blind_spot_rate": bs,
        "verdict": verdict,
    }


def main():
    import os
    from concurrent.futures import ThreadPoolExecutor, as_completed
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        for line in Path.home().joinpath(".bashrc").read_text().splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if line.startswith("OPENROUTER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    if not key:
        raise SystemExit("OPENROUTER_API_KEY not found")

    compiled = json.loads((EGP_DIR / "egp_compiled.json").read_text())
    rules = compiled if isinstance(compiled, list) else []
    hits, all_sents = load_corpus_by_label()
    print(f"rules: {len(rules)}; rules with corpus hits: {len(hits)}; model: {MODEL} x{CONCURRENCY}", flush=True)

    report = {"model": MODEL, "sampled": {"hits": HITS_PER_RULE, "nonhits": NONHITS_PER_RULE}, "rules": {}}
    jobs = []
    for rule in rules:
        eid = rule["egp_id"]
        hit_sents = (hits.get(eid) or [])[:HITS_PER_RULE]
        hit_set = set(hit_sents)
        candidates = [t for t in all_sents if t not in hit_set]
        nonhit_sents = random.sample(candidates, min(NONHITS_PER_RULE, len(candidates)))
        jobs.append((eid, rule, hit_sents, nonhit_sents))

    done = 0
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futs = {ex.submit(judge_one_rule, e, r, h, n, key): e for e, r, h, n in jobs}
        for fut in as_completed(futs):
            try:
                eid, res = fut.result()
                report["rules"][eid] = res
            except Exception as e:
                eid = futs[fut]
                report["rules"][eid] = {"verdict": "error", "error": str(e)[:120]}
            done += 1
            if done % 50 == 0:
                DATA.joinpath("label_agreement.json").write_text(json.dumps(report, indent=1))
                print(f"  ...{done}/{len(jobs)} rules audited", flush=True)

    DATA.joinpath("label_agreement.json").write_text(json.dumps(report, indent=1))
    tally = {}
    for v in report["rules"].values():
        tally[v["verdict"]] = tally.get(v["verdict"], 0) + 1
    print(f"DONE: {len(jobs)} rules audited; verdicts: {tally}")


if __name__ == "__main__":
    main()
