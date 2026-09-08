"""
R4 control: measure judge stochasticity on WRAPPED forms, not just the original form.

The main pipeline's noise floor re-scores only the original form (repeats>1 in
judges.run_judge). A skeptic can object that wrapped inputs might be noisier (longer,
closer to the decision boundary), so part of a "flip" could be wrapped-form randomness.
This script re-scores the wrapped form of selected headline (judge, wrapper) cells two
more times (repeat 1, 2); combined with repeat 0 from the main judged_*.jsonl, each item
has 3 verdicts and the wrapped-form noise floor is the fraction of items whose 3 verdicts
are not identical -- the same definition stats._noise_floor uses for the original form.

Usage:
  python -m src.wrapped_noise run       # score (resumable, appends)
  python -m src.wrapped_noise report    # print wrapped-form floors vs flip rates
"""

import json
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path

from .judges import get_judge, load_jsonl

WRAPPED = "Experiment/datasets/wrapped_responses.jsonl"
CELLS = {
    "gpt4o":         ["refusal_then_comply", "ethical_reflection"],
    "llamaguard_or": ["educational_framing", "refusal_then_comply", "ethical_reflection"],
}
EXTRA_REPEATS = (1, 2)   # repeat 0 lives in Experiment/outputs/judged_<judge>.jsonl
OUT = "Experiment/outputs/wrapped_noise_{judge}.jsonl"


def run(concurrency: int = 6, limit: int = None):
    rows = load_jsonl(WRAPPED)
    for judge_name, wrappers in CELLS.items():
        judge = get_judge(judge_name)
        out_path = OUT.format(judge=judge_name)
        done = set()
        if Path(out_path).exists():
            for r in load_jsonl(out_path):
                done.add((r["sample_id"], r["repeat"]))
        todo = [(r, rep) for r in rows if r["wrapper"] in wrappers
                for rep in EXTRA_REPEATS if (r["sample_id"], rep) not in done]
        if limit:
            todo = todo[:limit]
        print(f"[wrapped_noise:{judge_name}] {len(todo)} calls to make "
              f"({len(done)} already present)")
        if not todo:
            continue
        lock = threading.Lock()
        fout = open(out_path, "a", encoding="utf-8")
        t0 = time.time(); n = [0]

        def work(task, judge=judge, judge_name=judge_name, fout=fout, n=n, t0=t0, lock=lock):
            r, rep = task
            try:
                v = judge.score(r["behavior"], r["response_text"])
            except Exception as e:  # noqa: BLE001
                print(f"[wrapped_noise:{judge_name}] ERROR {r['sample_id']} rep{rep}: "
                      f"{type(e).__name__} {str(e)[:80]}")
                return
            rec = {"sample_id": r["sample_id"], "response_id": r["response_id"],
                   "wrapper": r["wrapper"], "judge": judge_name, "repeat": rep,
                   "refusal_label": v.refusal_label, "unsafe_label": v.unsafe_label}
            with lock:
                fout.write(json.dumps(rec) + "\n"); fout.flush()
                n[0] += 1
                if n[0] % 100 == 0:
                    rate = n[0] / (time.time() - t0)
                    print(f"[wrapped_noise:{judge_name}] {n[0]}/{len(todo)} ({rate:.1f}/s)")

        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=concurrency) as ex:
            list(ex.map(work, todo))
        fout.close()
        print(f"[wrapped_noise:{judge_name}] done -> {out_path}")


def report():
    for judge_name, wrappers in CELLS.items():
        # repeat 0 from the main run
        r0 = {}
        for r in load_jsonl(f"Experiment/outputs/judged_{judge_name}.jsonl"):
            if r.get("repeat", 0) == 0 and r["wrapper"] in wrappers:
                r0[r["sample_id"]] = r["unsafe_label"]
        extra = defaultdict(dict)
        p = OUT.format(judge=judge_name)
        if not Path(p).exists():
            print(f"[wrapped_noise:{judge_name}] no data yet"); continue
        for r in load_jsonl(p):
            extra[r["sample_id"]][r["repeat"]] = r["unsafe_label"]
        per_w = defaultdict(lambda: [0, 0])
        for sid, reps in extra.items():
            if sid not in r0 or len(reps) < len(EXTRA_REPEATS):
                continue
            verdicts = [r0[sid]] + [reps[i] for i in sorted(reps)]
            w = sid.split("__")[1]
            per_w[w][1] += 1
            per_w[w][0] += int(len(set(verdicts)) > 1)
        for w, (flips, tot) in sorted(per_w.items()):
            if tot:
                print(f"{judge_name:15s} {w:22s} wrapped-form floor: "
                      f"{flips}/{tot} = {100*flips/tot:.2f}%")


if __name__ == "__main__":
    {"run": run, "report": report}[sys.argv[1] if len(sys.argv) > 1 else "report"]()
