"""Adjudicate flagged rules with a stronger second judge.

Re-judges rules flagged critical/suspect by the glm-5.3-flash audit using
gemini-3.1-pro (different lineage, stronger). Output merges into
data/label_agreement.json with an 'adjudication' field per rule.

verdict logic:
  both judges agree bad  -> redispatch (Jules fix with evidence)
  judges disagree        -> goldset (human tiebreak)
  pro-judge overrules    -> upgrade to solid
"""

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, "/home/hayron/MyProjects/EGP OBLITERATED")
from compile_batch import call_openrouter

EGP_DIR = Path("/home/hayron/MyProjects/EGP OBLITERATED")
DATA = EGP_DIR / "data"
MODEL = "google/gemini-3.1-pro-preview"
FALLBACK = "google/gemini-2.5-flash"
HITS, NONHITS = 8, 5


def get_key():
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    for line in Path.home().joinpath(".bashrc").read_text().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("no OPENROUTER_API_KEY")


def load_hits():
    hits = {}
    all_sents = []
    for line in (DATA / "train_corpus.jsonl").open():
        ex = json.loads(line)
        all_sents.append(ex["text"])
        for l in ex["labels"]:
            hits.setdefault(l, []).append(ex["text"])
    return hits, all_sents


def judge(can_do, sentences, expecting, key):
    kind = "does demonstrate" if expecting == "hit" else "does NOT demonstrate"
    listing = "\n".join(f"{i+1}. {s}" for i, s in enumerate(sentences))
    prompt = (
        f"Can-do statement: {can_do}\n\n"
        f"For each numbered learner sentence, answer strictly YES or NO: the sentence {kind} "
        f"the grammar structure described. IMPORTANT: these are ESL learners — accept non-native "
        f"variants, missing tense marking, and imperfect morphology IF the target structure is "
        f"recognizably attempted or present. Judge meaning and function, not nativeness.\n\n"
        f"{listing}\n\n"
        f'Reply with ONLY: {{"answers": ["YES" or "NO", ...]}}'
    )
    for model in (MODEL, FALLBACK):
        try:
            resp = call_openrouter(key, model, [
                {"role": "system", "content": "You are an expert ESL grammar examiner. Output JSON only. Be brief."},
                {"role": "user", "content": prompt},
            ], max_tokens=2000)
            msg = resp["choices"][0]["message"]
            raw = msg.get("content")
            if not raw and msg.get("reasoning"):
                tail = msg["reasoning"][-800:]
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


def main():
    key = get_key()
    report = json.loads((DATA / "label_agreement.json").read_text())
    flags = [e for e, v in report["rules"].items()
             if v.get("verdict") in ("critical", "suspect")]
    print(f"re-adjudicating {len(flags)} flagged rules with {MODEL}", flush=True)
    hits, all_sents = load_hits()

    import random
    random.seed(11)
    for rule in json.loads((EGP_DIR / "egp_compiled.json").read_text()):
        eid = rule["egp_id"]
        if eid not in flags:
            continue
        hit_sents = (hits.get(eid) or [])[:HITS]
        hit_set = set(hit_sents)
        cand = [t for t in all_sents if t not in hit_set]
        nonhit_sents = random.sample(cand, min(NONHITS, len(cand)))
        pro_fp = pro_bs = None
        if hit_sents:
            ans = judge(rule.get("can_do_statement", ""), hit_sents, "hit", key)
            if ans:
                pro_fp = 1 - sum(ans) / len(ans)
        if nonhit_sents:
            ans = judge(rule.get("can_do_statement", ""), nonhit_sents, "nonhit", key)
            if ans:
                pro_bs = sum(ans) / len(ans)

        flash = report["rules"][eid]
        f_fp = flash.get("false_positive_rate")
        f_bs = flash.get("blind_spot_rate")
        if pro_fp is None and pro_bs is None:
            adjudication = "unresolved"
        else:
            p_fp = pro_fp if pro_fp is not None else 0
            p_bs = pro_bs if pro_bs is not None else 0
            if (f_fp or 0) >= 0.5 and p_fp >= 0.5:
                adjudication = "redeliver"      # both judges: rule fires wrongly
            elif (f_bs or 0) >= 0.5 and p_bs >= 0.5:
                adjudication = "redeliver"      # both judges: rule misses
            elif (f_fp or 0) >= 0.5 and p_fp < 0.25:
                adjudication = "overruled"      # flash wrong, rule fine
            elif (f_bs or 0) >= 0.5 and p_bs < 0.25:
                adjudication = "overruled"
            else:
                adjudication = "goldset"        # judges disagree -> human
        report["rules"][eid]["adjudication"] = adjudication
        report["rules"][eid]["pro_false_positive_rate"] = pro_fp
        report["rules"][eid]["pro_blind_spot_rate"] = pro_bs
        print(f"  {eid[-8:]}: flash(fp={f_fp},bs={f_bs}) pro(fp={pro_fp},bs={pro_bs}) -> {adjudication}", flush=True)
        DATA.joinpath("label_agreement.json").write_text(json.dumps(report, indent=1))
        time.sleep(0.5)

    tally = {}
    for v in report["rules"].values():
        a = v.get("adjudication")
        if a:
            tally[a] = tally.get(a, 0) + 1
    print(f"ADJUDICATION: {tally}")


if __name__ == "__main__":
    main()
