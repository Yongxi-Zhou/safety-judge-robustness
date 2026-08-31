# Dataset & Metrics Plan

## Response set (what the judges score)

Target: **~600 responses** = ~300 unsafe-compliance + ~300 refusal, spanning ≥3 harm
categories and 5 target models (so the set doubles as a mini safety leaderboard).

### Sources (drop into `Experiment/datasets/raw/` as JSONL)
- **JailbreakBench** artifacts — released attack completions with harmful/benign labels.
  https://github.com/JailbreakBench/jailbreakbench
- **HarmBench** completions — per-behavior model responses with classifier labels.
  https://github.com/centerforaisafety/HarmBench
- **StrongREJECT** / **AdvBench** responses where available, for category coverage.

Expected raw line (superset tolerated by `dataset.from_raw`):
```json
{"behavior": "...", "category": "cybercrime", "response": "...",
 "label": "unsafe|safe|refusal", "target_model": "vicuna-13b"}
```

### Construction rules (`src/dataset.py`)
- Map source labels → `gold_label ∈ {unsafe, refusal}` and `response_type ∈ {compliance,
  refusal, partial}` via `_normalize_label`.
- Keep only responses with non-empty `response_text`.
- Balance the set to ~50/50 unsafe/refusal so both attack directions are powered.
- Preserve `target_model` for the ranking-reversal analysis; sample 5 models with a spread of
  baseline safety.
- **Only responses each judge scores correctly on `original` enter that judge's flip
  denominator** (applied downstream in `stats.py`), so a flip is unambiguously wrapper-induced.

### Demo fixture
`dataset.demo_fixture()` ships 12 synthetic responses (compliance/refusal × 3 categories × 2
models) with non-operational placeholder "harmful" bodies. Used only for the offline
`--smoke` pipeline check; never reported as results.

## Metrics (`src/stats.py`, `src/analysis.py`)

| Metric | Definition | Where |
|---|---|---|
| False-negative flip rate | P(wrapped safe \| gold unsafe, original unsafe) | per (judge, wrapper) |
| False-positive flip rate | P(wrapped unsafe \| gold refusal, original safe) | per (judge, wrapper) |
| Any-flip rate + 95% CI | union of the two, bootstrap over `response_id` (5000×) | per (judge, wrapper) |
| McNemar p (Holm, BH) | exact test, original vs wrapped, corrected across the family | per (judge, wrapper) |
| Noise floor | original-form verdict instability across 5 repeats | per judge |
| Cross-judge agreement | pairwise % agreement + unanimity on `original` | panel |
| Ranking reversal | # wrappers that reorder target models by unsafe-rate; Kendall-τ | per judge |

### Headline numbers the paper will report
1. Max any-flip rate per judge, with CI clearing the noise floor (H1).
2. Judge ordering by mean flip rate (H2).
3. Count of ranking reversals + one worked example table (H3).
4. Human-confirmed judge-error rate on flipped items + content-invariance κ.

## Output files
- `Experiment/outputs/judged_<judge>.jsonl` — per-verdict records.
- `Experiment/analysis/stats_<judge>.json` — per-judge flip stats.
- `Experiment/analysis/flip_rates.{csv,tex}` — main cross-judge table.
- `Experiment/analysis/cross_judge.json` — baseline agreement.
- `Experiment/analysis/ranking_reversal.json` — leaderboard instability.
