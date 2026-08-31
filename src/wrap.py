"""
Stage 2: expand the fixed response set into wrapped variants.

For each response, emit `original` plus every wrapper in the applicable family (chosen by
`response_type`; see wrappers.wrappers_for). The wrapped text is the ONLY thing that
changes -- behavior, gold_label, category, target_model are carried through unchanged.

Output schema (Experiment/datasets/wrapped_responses.jsonl):
    {
      "sample_id": "rs_00007__disclaimer_prefix",
      "response_id": "rs_00007",
      "wrapper": "disclaimer_prefix",
      "wrapper_family": "false_negative",
      "behavior": "...", "category": "...", "gold_label": "unsafe",
      "response_type": "compliance", "target_model": "model_v",
      "response_text": "<wrapped text>"
    }

Usage:
  python -m src.wrap --in Experiment/datasets/response_set.jsonl \
      --out Experiment/datasets/wrapped_responses.jsonl
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List

from .wrappers import wrappers_for, apply_wrapper


def load_jsonl(path: str) -> List[Dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def write_jsonl(path: str, rows: List[Dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def expand(response_set_path: str, out_path: str) -> str:
    rows = load_jsonl(response_set_path)
    out: List[Dict] = []
    for r in rows:
        for w in wrappers_for(r["response_type"]):
            out.append({
                "sample_id": f"{r['response_id']}__{w.name}",
                "response_id": r["response_id"],
                "wrapper": w.name,
                "wrapper_family": w.family,
                "behavior": r["behavior"],
                "category": r["category"],
                "gold_label": r["gold_label"],
                "response_type": r["response_type"],
                "target_model": r.get("target_model", "unknown"),
                "response_text": apply_wrapper(w.name, r["response_text"]),
            })
    write_jsonl(out_path, out)
    n_orig = sum(x["wrapper"] == "original" for x in out)
    print(f"[wrap] {n_orig} responses -> {len(out)} wrapped rows "
          f"(x{len(out)/max(1,n_orig):.1f}) -> {out_path}")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Expand responses into wrapped variants.")
    ap.add_argument("--in", dest="inp", default="Experiment/datasets/response_set.jsonl")
    ap.add_argument("--out", default="Experiment/datasets/wrapped_responses.jsonl")
    args = ap.parse_args()
    expand(args.inp, args.out)


if __name__ == "__main__":
    main()
