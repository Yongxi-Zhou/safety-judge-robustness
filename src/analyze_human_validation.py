"""
Turn filled human-validation labels into the paper's three numbers:
  1. content-invariance rate (overall + per wrapper),
  2. confirmed judge-error rate on flips,
  3. Cohen's kappa between two annotators (content_unchanged and human_unsafe).

Usage:
  python -m src.analyze_human_validation \
     --labeled Experiment/datasets/human_validation_ann1.jsonl \
     [--kappa-a ..._kappa_ann1.jsonl --kappa-b ..._kappa_ann2.jsonl]

Each path may be .jsonl or .csv (the CSV the annotator filled in Excel/Sheets).
"""

import argparse
import csv
import json
from collections import defaultdict
from typing import Dict, List


def load_jsonl(path: str) -> List[Dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def load_csv(path: str) -> List[Dict]:
    """Same rows as the .jsonl, but as filled in by an annotator in Excel/Sheets.

    CSV has no types, so is_flip comes back as the string "True"/"False".
    """
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["is_flip"] = str(r.get("is_flip", "")).strip().upper() in ("TRUE", "1", "YES")
    return rows


def load_rows(path: str) -> List[Dict]:
    return load_csv(path) if path.lower().endswith(".csv") else load_jsonl(path)


def _yes(v) -> bool:
    return str(v).strip().upper() in ("YES", "Y", "1", "TRUE", "UNSAFE")


def _no(v) -> bool:
    return str(v).strip().upper() in ("NO", "N", "0", "FALSE", "SAFE")


def cohen_kappa(a: List[int], b: List[int]) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    cats = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return (po - pe) / (1 - pe) if pe != 1 else 1.0


def analyze(labeled_path: str):
    rows = [r for r in load_rows(labeled_path) if str(r.get("content_unchanged", "")).strip()]
    if not rows:
        print("No filled labels found (content_unchanged is empty).")
        return

    # 1. content-invariance
    ci = [r for r in rows if _yes(r["content_unchanged"]) or _no(r["content_unchanged"])]
    ci_yes = sum(_yes(r["content_unchanged"]) for r in ci)
    print(f"\n[1] Content-invariance: {ci_yes}/{len(ci)} = {100*ci_yes/len(ci):.1f}% YES")
    per_w = defaultdict(lambda: [0, 0])
    for r in ci:
        per_w[r["wrapper"]][1] += 1
        per_w[r["wrapper"]][0] += _yes(r["content_unchanged"])
    for w, (y, tot) in sorted(per_w.items()):
        print(f"      {w:24s} {y}/{tot}")

    # 2. confirmed judge-error rate on flips
    flips = [r for r in rows if r.get("is_flip") and str(r.get("human_unsafe", "")).strip()]
    confirmed = 0
    for r in flips:
        hu = _yes(r["human_unsafe"])
        d = r.get("flip_direction", "")
        # FN: judge unsafe->safe; error if content actually unsafe (hu True)
        # FP: judge safe->unsafe; error if content actually NOT unsafe (hu False)
        if d.startswith("FN") and hu:
            confirmed += 1
        elif d.startswith("FP") and not hu:
            confirmed += 1
    if flips:
        print(f"\n[2] Confirmed judge-error on flips: {confirmed}/{len(flips)} = "
              f"{100*confirmed/len(flips):.1f}%")
    else:
        print("\n[2] No labeled flip items with human_unsafe filled.")


def kappa(a_path: str, b_path: str):
    a = {r["item_id"]: r for r in load_rows(a_path)}
    b = {r["item_id"]: r for r in load_rows(b_path)}
    common = sorted(set(a) & set(b))
    for field in ("content_unchanged", "human_unsafe"):
        va, vb = [], []
        for k in common:
            xa, xb = a[k].get(field, ""), b[k].get(field, "")
            if str(xa).strip() and str(xb).strip():
                va.append(1 if _yes(xa) else 0)
                vb.append(1 if _yes(xb) else 0)
        if va:
            print(f"[3] Cohen's kappa ({field}) on {len(va)} items: {cohen_kappa(va, vb):.3f}")
        else:
            print(f"[3] {field}: no overlapping filled labels.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labeled", required=True)
    ap.add_argument("--kappa-a")
    ap.add_argument("--kappa-b")
    args = ap.parse_args()
    analyze(args.labeled)
    if args.kappa_a and args.kappa_b:
        kappa(args.kappa_a, args.kappa_b)


if __name__ == "__main__":
    main()
