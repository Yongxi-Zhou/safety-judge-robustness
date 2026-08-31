"""
5-stage orchestrator for the style-wrapper judge-gaming experiment.

  Stage 1  build     : construct the fixed response set (dataset.py). --demo for fixture.
  Stage 2  wrap      : expand into content-invariant wrapped variants (wrap.py).
  Stage 3  judge     : score wrapped responses with one judge (judges.py).
  Stage 4  stats     : flip rates + McNemar + bootstrap CI for one judged file (stats.py).
  Stage 5  analyze   : aggregate all judged files into tables + ranking reversal (analysis.py).

Stages 3/4 are per-judge; stage 5 consumes every judged_*.jsonl at once.

Quick offline smoke test (no keys, rule-based judge, demo data):
  python -m src.pipeline --smoke

Full flow for one judge:
  python -m src.pipeline --stage 1 --demo          # or --raw <completions.jsonl>
  python -m src.pipeline --stage 2
  python -m src.pipeline --stage 3 --judge rulebased
  python -m src.pipeline --stage 4 --judge rulebased
  python -m src.pipeline --stage 5 --judges rulebased gpt4o llamaguard
"""

import argparse
from pathlib import Path

from . import dataset, wrap, judges, stats, analysis

RESPONSE_SET = "Experiment/datasets/response_set.jsonl"
WRAPPED = "Experiment/datasets/wrapped_responses.jsonl"
OUT_DIR = "Experiment/outputs"
ANALYSIS_DIR = "Experiment/analysis"


def judged_path(judge: str) -> str:
    return f"{OUT_DIR}/judged_{judge}.jsonl"


def stage1(args):
    if args.raw:
        rows = dataset.from_raw(args.raw)
    else:
        rows = dataset.demo_fixture()
    dataset.write_jsonl(RESPONSE_SET, rows)
    print(f"[stage1] {len(rows)} responses -> {RESPONSE_SET}")


def stage2(args):
    wrap.expand(RESPONSE_SET, WRAPPED)


def stage3(args):
    judges.run_judge(args.judge, WRAPPED, judged_path(args.judge),
                     repeats=args.repeats, limit=args.limit,
                     concurrency=getattr(args, "concurrency", 8))


def stage4(args):
    out = f"{ANALYSIS_DIR}/stats_{args.judge}.json"
    res = stats.compute(judged_path(args.judge))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    import json
    json.dump(res, open(out, "w"), indent=2)
    print(f"[stage4] {args.judge}: {res['n_responses']} responses -> {out}")
    for w, s in res["wrappers"].items():
        print(f"    {w:22s} any-flip={s['any_flip_rate']:.3f} "
              f"p_holm={s['p_holm']}")


def stage5(args):
    paths = [judged_path(j) for j in args.judges if Path(judged_path(j)).exists()]
    if not paths:
        raise SystemExit("[stage5] no judged_*.jsonl found; run stage 3 first.")
    analysis.build_tables(paths, ANALYSIS_DIR)


def smoke(args):
    print("=== SMOKE TEST (offline, rule-based judge, demo fixture) ===")
    class A:  # noqa: N801 -- tiny arg shim
        raw = None; judge = "rulebased"; repeats = 1; limit = None
        judges = ["rulebased"]
    a = A()
    stage1(a); stage2(a); stage3(a); stage4(a); stage5(a)
    print("=== SMOKE OK: pipeline ran end-to-end. See Experiment/analysis/ ===")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", type=int, choices=[1, 2, 3, 4, 5])
    ap.add_argument("--smoke", action="store_true", help="Run stages 1-5 offline on demo data.")
    ap.add_argument("--demo", action="store_true", help="Stage 1: use the demo fixture.")
    ap.add_argument("--raw", default=None, help="Stage 1: ingest a raw completions JSONL.")
    ap.add_argument("--judge", default="rulebased", choices=judges.ALL_JUDGES)
    ap.add_argument("--judges", nargs="+", default=judges.ALL_JUDGES,
                    help="Stage 5: judged files to aggregate.")
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--concurrency", type=int, default=8)
    args = ap.parse_args()

    if args.smoke:
        smoke(args)
        return
    if args.stage is None:
        ap.error("pass --stage N or --smoke")
    {1: stage1, 2: stage2, 3: stage3, 4: stage4, 5: stage5}[args.stage](args)


if __name__ == "__main__":
    main()
