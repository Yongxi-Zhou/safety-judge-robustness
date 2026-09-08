"""Generate the paper's flip-rate table (wrappers as rows, judges as columns).

Reads Experiment/analysis/flip_rates.csv, writes a booktabs tabular grouped by
attack direction, with a tone-only/assertion-adding stratum marker per wrapper and
a * on Holm-significant cells. Layout-agnostic: the paper wraps it in table or table*.

Usage: python -m src.make_flip_table [out.tex]
"""
import csv
import sys

JUDGES = [("rulebased", "Keyword"), ("gpt4o", "GPT-4o-m"), ("strongreject", "StrongR"),
          ("deepseek", "DeepSeek"), ("qwen", "Qwen"), ("claude", "Claude"),
          ("llamaguard_or", "LG-4"), ("safeguard_or", "SG-20b")]
TONE = {"disclaimer_prefix", "ethical_reflection", "fake_cot", "moralizing_suffix", "lecture_suffix"}
GROUPS = [
    ("Harm-hiding wrappers (applied to genuinely harmful responses)",
     ["disclaimer_prefix", "ethical_reflection", "fake_cot", "moralizing_suffix",
      "educational_framing", "refusal_then_comply"]),
    ("Harm-inventing wrappers (applied to refusals)",
     ["lecture_suffix", "harm_adjacent_preamble", "pseudo_comply_frame"]),
]
PRETTY = {
    "disclaimer_prefix": "disclaimer prefix", "ethical_reflection": "ethical reflection",
    "fake_cot": "fake reasoning block", "moralizing_suffix": "moralizing suffix",
    "educational_framing": "educational framing", "refusal_then_comply": "refusal-then-comply",
    "lecture_suffix": "lecture suffix", "harm_adjacent_preamble": "harm-adjacent preamble",
    "pseudo_comply_frame": "pseudo-compliance frame",
}


def main(out="Publication/paper/flip_rates_wide.tex"):
    rows = list(csv.DictReader(open("Experiment/analysis/flip_rates.csv")))
    cell = {}
    for r in rows:
        v = 100 * float(r["any_flip"])
        star = float(r["p_holm"]) < 0.05
        cell[(r["judge"], r["wrapper"])] = (v, star)

    lines = [r"\begin{tabular}{llrrrrrrrr}", r"\toprule",
             r"Wrapper & Stratum & " + " & ".join(n for _, n in JUDGES) + r" \\",
             r"\midrule"]
    for gi, (label, wrappers) in enumerate(GROUPS):
        if gi:
            lines.append(r"\midrule")
        lines.append(r"\multicolumn{10}{l}{\emph{" + label + r"}} \\[1pt]")
        for w in wrappers:
            vals = []
            for j, _ in JUDGES:
                v, star = cell[(j, w)]
                s = f"{v:.1f}"
                if star:
                    s = r"\textbf{" + s + r"}$^{*}$"
                vals.append(s)
            stratum = "tone" if w in TONE else "assert."
            lines.append(PRETTY[w] + " & " + stratum + " & " + " & ".join(vals) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main(*sys.argv[1:])
