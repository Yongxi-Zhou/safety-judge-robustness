"""
Fetch JailbreakBench attack artifacts and convert them to the raw response schema
consumed by `dataset.from_raw`.

Each JailbreakBench artifact (attack-artifacts/<METHOD>/black_box/<MODEL>.json) has a
`jailbreaks` list of records with: goal, behavior, category, prompt, response, and the
gold label `jailbroken` (bool, from the JailbreakBench classifier). We map:

    behavior     <- goal
    category     <- category
    response     <- response            (the text the judge will score)
    label        <- "unsafe" if jailbroken else "refusal"
    target_model <- MODEL               (for the ranking-reversal analysis)

We pull several (method, model) pairs so the set spans multiple target models, then
balance to a target count per class so both attack directions are powered.

Usage:
  python -m src.fetch_jbb --out Experiment/datasets/raw/jailbreakbench_completions.jsonl \
      --per-class 300
"""

import argparse
import json
import urllib.request
from pathlib import Path
from typing import Dict, List

RAW_BASE = ("https://raw.githubusercontent.com/JailbreakBench/artifacts/main/"
            "attack-artifacts/{method}/{variant}/{model}.json")

# (method, variant, model) triples that exist in the artifacts repo. Spanning several
# attacks and all four target models gives a spread of jailbroken/refusal outcomes:
# PAIR + random-search skew unsafe; GCG/DSN white-box and JBC manual on llama-2/gpt-4
# contribute many refusals for the false-positive direction.
DEFAULT_SOURCES = [
    ("PAIR", "black_box", "vicuna-13b-v1.5"),
    ("PAIR", "black_box", "llama-2-7b-chat-hf"),
    ("PAIR", "black_box", "gpt-3.5-turbo-1106"),
    ("PAIR", "black_box", "gpt-4-0125-preview"),
    ("prompt_with_random_search", "black_box", "vicuna-13b-v1.5"),
    ("prompt_with_random_search", "black_box", "llama-2-7b-chat-hf"),
    ("prompt_with_random_search", "black_box", "gpt-3.5-turbo-1106"),
    ("prompt_with_random_search", "black_box", "gpt-4-0125-preview"),
    ("GCG", "white_box", "vicuna-13b-v1.5"),
    ("GCG", "white_box", "llama-2-7b-chat-hf"),
    ("DSN", "white_box", "vicuna-13b-v1.5"),
    ("DSN", "white_box", "llama-2-7b-chat-hf"),
    ("JBC", "manual", "gpt-3.5-turbo-1106"),
    ("JBC", "manual", "gpt-4-0125-preview"),
    ("JBC", "manual", "llama-2-7b-chat-hf"),
    ("JBC", "manual", "vicuna-13b-v1.5"),
]


def _fetch_json(url: str, timeout: int = 40) -> Dict:
    req = urllib.request.Request(url, headers={"User-Agent": "safety-judge-robustness"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch(sources: List, per_class: int) -> List[Dict]:
    unsafe: List[Dict] = []
    refusal: List[Dict] = []
    seen = set()
    for method, variant, model in sources:
        url = RAW_BASE.format(method=method, variant=variant, model=model)
        try:
            art = _fetch_json(url)
        except Exception as e:  # noqa: BLE001
            print(f"[fetch_jbb] skip {method}/{model}: {e}")
            continue
        n_u = n_r = 0
        for rec in art.get("jailbreaks", []):
            resp = (rec.get("response") or "").strip()
            if not resp:
                continue
            key = (model, (rec.get("goal") or "").strip(), resp[:120])
            if key in seen:
                continue
            seen.add(key)
            row = {
                "source": f"jailbreakbench_{method}",
                "behavior": (rec.get("goal") or rec.get("behavior") or "").strip(),
                "category": rec.get("category", "unspecified"),
                "response": resp,
                "label": "unsafe" if rec.get("jailbroken") else "refusal",
                "target_model": model,
            }
            if row["label"] == "unsafe":
                unsafe.append(row); n_u += 1
            else:
                refusal.append(row); n_r += 1
        print(f"[fetch_jbb] {method}/{model}: {n_u} unsafe, {n_r} refusal")

    # balance: cap each class at per_class, round-robin across target models for spread
    unsafe = _balance(unsafe, per_class)
    refusal = _balance(refusal, per_class)
    out = unsafe + refusal
    print(f"[fetch_jbb] balanced -> {len(unsafe)} unsafe + {len(refusal)} refusal "
          f"= {len(out)} responses across "
          f"{len(set(r['target_model'] for r in out))} target models")
    return out


def _balance(rows: List[Dict], cap: int) -> List[Dict]:
    """Cap to `cap`, spreading across target_models round-robin so no single model dominates."""
    by_model: Dict[str, List[Dict]] = {}
    for r in rows:
        by_model.setdefault(r["target_model"], []).append(r)
    order = sorted(by_model)
    picked: List[Dict] = []
    i = 0
    while len(picked) < cap and any(by_model[m] for m in order):
        m = order[i % len(order)]
        if by_model[m]:
            picked.append(by_model[m].pop())
        i += 1
    return picked


def write_jsonl(path: str, rows: List[Dict]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Fetch + convert JailbreakBench artifacts.")
    ap.add_argument("--out", default="Experiment/datasets/raw/jailbreakbench_completions.jsonl")
    ap.add_argument("--per-class", type=int, default=300,
                    help="Max responses per gold class (unsafe / refusal).")
    args = ap.parse_args()
    rows = fetch(DEFAULT_SOURCES, args.per_class)
    write_jsonl(args.out, rows)
    print(f"[fetch_jbb] wrote {len(rows)} rows -> {args.out}")


if __name__ == "__main__":
    main()
