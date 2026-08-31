"""
Export a stratified sample of wrapped responses for manual verification.

Two things a reviewer will ask for, both answered by a small human-labeled subset:
  1. Content-invariance check: confirm the wrapper truly did NOT change the operational
     content (so a verdict flip is judge error, not a real safety change). The template
     asks the annotator to mark `content_unchanged` yes/no.
  2. Judge-error direction: on flipped items, confirm which judge (original vs wrapped)
     is wrong, anchoring the flip rate to human ground truth (analogue of the reference
     project's kappa anchoring).

Stratifies by (wrapper_family, gold_label) so both attack directions are covered.

Usage:
  python -m src.human_subset --wrapped Experiment/datasets/wrapped_responses.jsonl \
      --n 150 --out Experiment/datasets/human_subset_template.jsonl
"""

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


def load_jsonl(path: str) -> List[Dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def export_subset(wrapped_path: str, n: int, out_path: str, seed: int = 7) -> str:
    rows = [r for r in load_jsonl(wrapped_path) if r["wrapper"] != "original"]
    strata = defaultdict(list)
    for r in rows:
        strata[(r["wrapper_family"], r["gold_label"])].append(r)
    rng = random.Random(seed)
    per = max(1, n // max(1, len(strata)))
    picked: List[Dict] = []
    for key, items in sorted(strata.items()):
        rng.shuffle(items)
        picked.extend(items[:per])
    picked = picked[:n]

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in picked:
            f.write(json.dumps({
                "sample_id": r["sample_id"],
                "wrapper": r["wrapper"],
                "wrapper_family": r["wrapper_family"],
                "gold_label": r["gold_label"],
                "behavior": r["behavior"],
                "response_text": r["response_text"],
                # --- annotator fills these ---
                "content_unchanged": "",     # YES = wrapper added only style, not content
                "human_unsafe": "",          # YES/NO: is the underlying content unsafe?
                "notes": "",
            }, ensure_ascii=False) + "\n")
    print(f"[human_subset] wrote {len(picked)} items ({len(strata)} strata) -> {out_path}")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Export a stratified human-label template.")
    ap.add_argument("--wrapped", default="Experiment/datasets/wrapped_responses.jsonl")
    ap.add_argument("--n", type=int, default=150)
    ap.add_argument("--out", default="Experiment/datasets/human_subset_template.jsonl")
    args = ap.parse_args()
    export_subset(args.wrapped, args.n, args.out)


if __name__ == "__main__":
    main()
