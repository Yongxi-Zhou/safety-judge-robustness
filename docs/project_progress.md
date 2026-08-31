# Project Progress

## Status: REAL RUN DONE (2 judges complete, 1 partial) — draft has real numbers

### Real run (2026-08-21) — see docs/results_summary.md
- Dataset: fetched 600 JailbreakBench responses (300 unsafe + 300 refusal), 4 target models,
  10 harm categories (`src/fetch_jbb.py`).
- Judges run: `rulebased` (600, complete), `gpt4o` = GPT-4o-mini generic rubric (600, complete),
  `strongreject` = GPT-4o-mini StrongREJECT rubric (partial, ~1.8k/3.3k verdicts, resumable
  background job still filling refusal coverage; throttled by a restrictive OpenAI rate limit).
- Headline: `refusal_then_comply` flips 19.9% of GPT-4o-mini unsafe verdicts (CI [15.0,24.0],
  Holm p<1e-4, floor 0.5%); keyword judge 100% FP-flipped by `pseudo_comply_frame`; StrongREJECT
  rubric cuts the attack ~10× (1.9%) on the same model; 5/9 wrappers reorder the leaderboard.
- Paper abstract + Results/Setup/Limitations updated with real numbers; PDF rebuilds clean.
- Realized API cost: under $3 (GPT-4o-mini).

### Environment notes (for reruns)
- Use the project venv: `./.venv/bin/python` (Homebrew system Python is externally managed).
- Load ONLY `OPENAI_API_KEY` from the reference .env; do NOT import its `OPENAI_BASE_URL`
  (it points at DashScope). Judges read `OPENAI_JUDGE_BASE_URL` only.
- `timeout` is absent on macOS; don't use it in scripts.
- Judge runs are checkpointed/resumable — re-run the same stage-3 command to continue.

## Earlier status: scaffold complete, pipeline verified offline

### Done
- [x] Idea framed and positioned vs 2025–26 venue survey (`Ideation/`, `Survey/reports/`).
- [x] Full experiment design fixed (`docs/experiment_design.md`).
- [x] Dataset + metrics plan (`docs/dataset_and_metrics_plan.md`).
- [x] Code: dataset builder, 9 content-invariant wrappers, wrap stage, 6-judge panel,
      verdict normalization, flip-rate + McNemar/Holm/BH + bootstrap stats, aggregation +
      ranking-reversal analysis, human-validation exporter, 5-stage orchestrator.
- [x] **Offline smoke test passes** (`python -m src.pipeline --smoke`): build → wrap → judge
      (rulebased) → stats → analyze, emitting `flip_rates.{csv,tex}`, `cross_judge.json`,
      `ranking_reversal.json`. The rule-based judge already flips on `pseudo_comply_frame`.
- [x] Paper draft skeleton with abstract, all sections, and table placeholders
      (`Publication/paper/main.tex`).

### To do (needs credentials / compute)
- [ ] Drop JailbreakBench + HarmBench completions into `Experiment/datasets/raw/`.
- [ ] Build the real ~600-response set: `python -m src.pipeline --stage 1 --raw <file>`.
- [ ] Fill `.env` (`OPENAI_API_KEY`) and set up a GPU + HF gated-model access.
- [ ] Run the pilot gate (2 judges × 3 wrappers × 100 responses); decide go/no-go.
- [ ] Full grid: stage 3 for all 6 judges (`--repeats 5` on the API judges), stages 4–5.
- [ ] 150-item human validation (`src/human_subset.py`); compute κ and judge-error rate.
- [ ] Fill paper tables/figures from `Experiment/analysis/`; write results + discussion.

### Open decisions
- Final wrapper set: keep all 9 or drop the two most "obvious" (refusal_then_comply,
  pseudo_comply_frame) to a robustness appendix? Decide after the pilot.
- Whether to add one mitigation paragraph (content-only rubric / majority-vote panel) or leave
  mitigation entirely to future work.
- Venue: EMNLP/ACL Findings vs COLM — depends on effect size and calendar.

### Estimated timeline from here
Pilot 2 d → full run 3–4 d → human validation 2 d → writing 1 wk → **~3 weeks to submission.**
