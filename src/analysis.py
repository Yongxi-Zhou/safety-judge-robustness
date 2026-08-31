"""
Aggregate per-judge stats into the paper's tables and the ranking-reversal result.

Produces, under Experiment/analysis/:
  - flip_rates.csv        : (judge x wrapper) any/false-neg/false-pos flip rates
  - flip_rates.tex        : the main LaTeX table
  - cross_judge.json      : per-judge summary + cross-judge agreement (Fleiss-style)
  - ranking_reversal.json : per target_model safety score under original vs worst-wrapper
                            judging, and whether the model ranking changes.

Two headline claims this file is built to support:
  (A) Style wrappers flip safety verdicts well above the noise floor, and the most
      gameable judges are the weakest ones.
  (B) Because the flip is judge- and wrapper-dependent, the *ranking* of target models
      by "safety score" reorders depending on which wrapper the responses happen to carry
      -- i.e. a leaderboard built on a gameable judge is not order-stable.
"""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from . import stats as stats_mod


def load_jsonl(path: str) -> List[Dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def _wilson(p: float, n: int, z: float = 1.96) -> tuple:
    if n == 0:
        return 0.0, 0.0
    import math
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    return round(100 * max(0, centre - margin), 1), round(100 * min(1, centre + margin), 1)


def build_tables(judged_paths: List[str], out_dir: str) -> Dict:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    per_judge = {}
    all_wrappers = set()
    for jp in judged_paths:
        res = stats_mod.compute(jp)
        per_judge[res["judge"]] = res
        all_wrappers |= set(res["wrappers"].keys())
    wrappers = sorted(all_wrappers)
    judges = sorted(per_judge)

    # --- flip_rates.csv ---
    csv_path = Path(out_dir) / "flip_rates.csv"
    with open(csv_path, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["judge", "wrapper", "family", "any_flip", "ci_lo", "ci_hi",
                     "false_neg_flip", "fn_base", "false_pos_flip", "fp_base",
                     "p_holm", "p_bh"])
        for j in judges:
            for w in wrappers:
                s = per_judge[j]["wrappers"].get(w)
                if not s:
                    continue
                fam = ("false_negative" if s["false_negative_base"] >= s["false_positive_base"]
                       else "false_positive")
                wr.writerow([j, w, fam, s["any_flip_rate"], s["any_flip_ci95"][0],
                             s["any_flip_ci95"][1], s["false_negative_flip_rate"],
                             s["false_negative_base"], s["false_positive_flip_rate"],
                             s["false_positive_base"], s["p_holm"], s["p_bh"]])

    # --- flip_rates.tex (main table: judges as rows, wrappers as cols, any-flip %) ---
    tex_path = Path(out_dir) / "flip_rates.tex"
    with open(tex_path, "w") as f:
        cols = "l" + "r" * len(wrappers)
        f.write("\\begin{tabular}{" + cols + "}\n\\toprule\n")
        f.write("Judge & " + " & ".join(w.replace("_", "\\_") for w in wrappers) +
                " \\\\\n\\midrule\n")
        MIN_N = 20   # suppress cells whose paired sample is too small to report
        for j in judges:
            cells = []
            for w in wrappers:
                s = per_judge[j]["wrappers"].get(w)
                if not s:
                    cells.append("--")
                    continue
                paired_n = s["false_negative_base"] + s["false_positive_base"]
                if paired_n < MIN_N:
                    cells.append("--")
                    continue
                star = "$^{*}$" if s["p_holm"] < 0.05 else ""
                cells.append(f"{100*s['any_flip_rate']:.1f}{star}")
            f.write(j.replace("_", "\\_") + " & " + " & ".join(cells) + " \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n")

    # --- cross-judge agreement on the original form (do judges even agree baseline?) ---
    cross = _cross_judge_agreement(judged_paths)
    json.dump({"per_judge": per_judge, "cross_judge_agreement": cross},
              open(Path(out_dir) / "cross_judge.json", "w"), indent=2)

    # --- ranking reversal ---
    reversal = ranking_reversal(judged_paths)
    json.dump(reversal, open(Path(out_dir) / "ranking_reversal.json", "w"), indent=2)

    print(f"[analysis] wrote flip_rates.csv, flip_rates.tex, cross_judge.json, "
          f"ranking_reversal.json -> {out_dir}")
    return {"per_judge": per_judge, "cross_judge": cross, "reversal": reversal}


def _cross_judge_agreement(judged_paths: List[str]) -> Dict:
    """Percent agreement between judges on the ORIGINAL form, per response_id."""
    orig = defaultdict(dict)   # response_id -> {judge: unsafe_label}
    for jp in judged_paths:
        for r in load_jsonl(jp):
            if r["wrapper"] == "original" and r.get("repeat", 0) == 0:
                orig[r["response_id"]][r["judge"]] = r["unsafe_label"]
    judges = sorted({j for d in orig.values() for j in d})
    pair_agree = {}
    for i, a in enumerate(judges):
        for bj in judges[i+1:]:
            both = [(d[a], d[bj]) for d in orig.values() if a in d and bj in d]
            if both:
                agree = sum(1 for x, y in both if x == y) / len(both)
                pair_agree[f"{a}|{bj}"] = round(agree, 3)
    # unanimity rate
    unanimous = 0
    total = 0
    for d in orig.values():
        if len(d) == len(judges) and len(judges) > 1:
            total += 1
            if len(set(d.values())) == 1:
                unanimous += 1
    return {"judges": judges, "pairwise_agreement": pair_agree,
            "unanimity_rate": round(unanimous / total, 3) if total else None,
            "n_full": total}


def ranking_reversal(judged_paths: List[str]) -> Dict:
    """For each judge: rank target_models by unsafe-rate under ORIGINAL judging vs under
    the single most-gaming wrapper, and report whether the order changes.

    "safety score" = 1 - unsafe_rate. A wrapper that hides harm lowers a model's apparent
    unsafe rate (raises its safety score); if models are hidden unequally, the ranking flips.
    """
    out = {}
    for jp in judged_paths:
        rows = [r for r in load_jsonl(jp) if r.get("repeat", 0) == 0]
        if not rows:
            continue
        judge = rows[0]["judge"]
        # candidate wrappers = false-negative direction (hide harm on unsafe responses)
        wrappers = sorted({r["wrapper"] for r in rows if r["wrapper"] != "original"})

        def unsafe_rate(wrapper):
            by_model = defaultdict(lambda: [0, 0])
            for r in rows:
                if r["wrapper"] != wrapper:
                    continue
                if r["gold_label"] != "unsafe":
                    continue
                by_model[r["target_model"]][1] += 1
                by_model[r["target_model"]][0] += r["unsafe_label"]
            return {m: (c[0] / c[1] if c[1] else 0.0) for m, c in by_model.items()}

        base = unsafe_rate("original")
        base_rank = [m for m, _ in sorted(base.items(), key=lambda kv: kv[1])]
        reversals = []
        for w in wrappers:
            wr = unsafe_rate(w)
            wr_rank = [m for m, _ in sorted(wr.items(), key=lambda kv: kv[1])]
            if wr_rank != base_rank and set(wr_rank) == set(base_rank):
                reversals.append({"wrapper": w, "base_order": base_rank,
                                  "wrapped_order": wr_rank,
                                  "base_rates": {m: round(base[m], 3) for m in base},
                                  "wrapped_rates": {m: round(wr[m], 3) for m in wr}})
        out[judge] = {"base_order": base_rank,
                      "base_rates": {m: round(v, 3) for m, v in base.items()},
                      "n_reversing_wrappers": len(reversals),
                      "reversals": reversals}
    return out


def main():
    ap = argparse.ArgumentParser(description="Aggregate judged files into paper tables.")
    ap.add_argument("--judged", nargs="+", required=True,
                    help="One judged_*.jsonl per judge.")
    ap.add_argument("--out-dir", default="Experiment/analysis")
    args = ap.parse_args()
    build_tables(args.judged, args.out_dir)


if __name__ == "__main__":
    main()
