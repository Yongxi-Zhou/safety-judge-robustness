"""
R3 control: bootstrap support for leaderboard-reversal claims.

The base per-model unsafe rates on this artifact set are compressed (0.93-1.00 for the
LLM judges), so a wrapper-induced re-ordering can ride on a handful of responses. For
every (judge, wrapper) reversal reported in ranking_reversal.json, this script
bootstraps responses within each target model (2000 resamples) and reports:

  - p_base   : P(bootstrap base ranking top-1 == point-estimate base top-1)
               (how stable the baseline "safest model" claim is at all)
  - p_rev    : P(bootstrap wrapped ranking != bootstrap base ranking)
               (how often the wrapper changes the ranking, accounting for sampling noise)

A reversal is reported as "bootstrap-supported" if p_rev >= 0.5 -- i.e., under resampling
the wrapper changes the ranking more often than not. Output:
Experiment/analysis/rank_bootstrap.json.

Usage: python -m src.rank_bootstrap
"""

import json
import random
from collections import defaultdict

from .judges import load_jsonl

JUDGES = ["rulebased", "gpt4o", "strongreject", "deepseek", "qwen", "claude", "llamaguard_or"]
B = 2000
SEED = 7


def main():
    rng = random.Random(SEED)
    out = {}
    for judge in JUDGES:
        rows = [r for r in load_jsonl(f"Experiment/outputs/judged_{judge}.jsonl")
                if r.get("repeat", 0) == 0 and r["gold_label"] == "unsafe"]
        # verdicts[(model)][response_id][wrapper] = unsafe_label
        by_model = defaultdict(lambda: defaultdict(dict))
        wrappers = set()
        for r in rows:
            by_model[r["target_model"]][r["response_id"]][r["wrapper"]] = r["unsafe_label"]
            wrappers.add(r["wrapper"])
        wrappers.discard("original")
        models = sorted(by_model)
        ids = {m: sorted(by_model[m]) for m in models}

        def ranking(sample, wrapper):
            rates = []
            for m in models:
                vals = [by_model[m][rid].get(wrapper) for rid in sample[m]]
                vals = [v for v in vals if v is not None]
                rates.append((sum(vals) / len(vals) if vals else 0.0, m))
            return tuple(m for _, m in sorted(rates))  # safest (lowest unsafe rate) first

        point_base = ranking(ids, "original")
        judge_out = {"point_base_order": list(point_base), "wrappers": {}}
        base_top_hits = 0
        rev_hits = {w: 0 for w in wrappers}
        for _ in range(B):
            sample = {m: [rng.choice(ids[m]) for _ in ids[m]] for m in models}
            b_base = ranking(sample, "original")
            if b_base[0] == point_base[0]:
                base_top_hits += 1
            for w in wrappers:
                if ranking(sample, w) != b_base:
                    rev_hits[w] += 1
        judge_out["p_base_top1_stable"] = base_top_hits / B
        for w in sorted(wrappers):
            judge_out["wrappers"][w] = {"p_rev": rev_hits[w] / B}
        out[judge] = judge_out
        sup = [w for w in wrappers if rev_hits[w] / B >= 0.5]
        print(f"{judge:15s} base-top1 stable {100*base_top_hits/B:5.1f}% | "
              f"reversal p>=0.5 on {len(sup)}/{len(wrappers)} wrappers: {sorted(sup)}")
    with open("Experiment/analysis/rank_bootstrap.json", "w") as f:
        json.dump(out, f, indent=1)
    print("wrote Experiment/analysis/rank_bootstrap.json")


if __name__ == "__main__":
    main()
