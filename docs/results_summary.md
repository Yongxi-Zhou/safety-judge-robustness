# Results Summary (real run, 7-judge panel incl. a deployed guard model)

Run: 2026-08-30. Panel (all API-served, no GPU): `rulebased` (keyword); `gpt4o` (GPT-4o-mini
generic rubric); `strongreject` (GPT-4o-mini StrongREJECT rubric); `deepseek` (DeepSeek-Chat);
`qwen` (Qwen-Plus); `claude` (Claude Haiku 4.5); `llamaguard_or` (**Llama Guard 4 12B** via
OpenRouter — the purpose-built moderation model). All 7 judges complete on all 600 responses.
Response set: 600 JailbreakBench completions (300 unsafe + 300 refusal) across GPT-3.5, GPT-4,
Vicuna-13B, Llama-2-7B; 10 harm categories. Realized cost < ~$5.

## Full any-flip matrix (%, * = McNemar Holm-significant)

| Judge | disclaimer | edu_framing | ethical | fake_cot | harm_adj | lecture | moralizing | pseudo_comply | refusal_then_comply |
|---|---|---|---|---|---|---|---|---|---|
| rulebased | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | **100.0\*** | 0.0 |
| gpt4o | 2.8 | 1.0 | 4.8 | 2.4 | 0.8 | 0.4 | 0.0 | 1.9 | **19.9\*** |
| strongreject | 0.0 | 0.0 | 0.0 | 0.3 | 1.5 | 2.3 | 0.0 | 1.1 | 1.7 |
| deepseek | 1.7 | 3.5 | 0.0 | 0.4 | 1.1 | 0.4 | 0.0 | 1.8 | 3.5 |
| qwen | 0.0 | 0.7 | 2.7 | 0.0 | 0.4 | 0.0\* | 0.0 | 2.3 | 0.7 |
| claude | 0.0\* | 0.0 | 0.0 | 0.0\* | 1.8 | 1.8 | 0.0 | 0.7 | 0.4 |
| **llamaguard_or** | 2.2 | **12.3\*** | 3.6 | 1.8 | 0.4 | 1.1 | 0.0\* | 0.0 | **8.3\*** |

## Headline findings

**H1 — gameable, judge-specific, and it hits the deployed guard.**
- GPT-4o-mini: `refusal_then_comply` flips **19.9%** (CI [15,24], Holm p<1e-4, floor 0.5%).
- **Llama Guard 4** (purpose-built moderator): `educational_framing` flips **12.3%** (Holm-sig),
  `refusal_then_comply` **8.3%** (Holm-sig). Real deployed guards are gamed too — the money result.
- Keyword judge: `pseudo_comply_frame` 100% false-positive flip.
- Robust chat judges barely move (Claude 0.4%, Qwen 0.7%, DeepSeek 3.5% on refusal_then_comply).

**Different judges, different blind spots.** The framing that fools Llama Guard (edu_framing
12.3%) barely moves GPT-4o-mini (1.0%); the token-refusal trick that fools GPT-4o-mini (19.9%)
only mildly moves Llama Guard (8.3%). No single wrapper is universally strongest.

**H2 — it's the judge.** (a) Cross-vendor spread 0.4–19.9% on the identical wrapper. (b)
Prompt-only: same model (GPT-4o-mini), StrongREJECT rubric cuts refusal_then_comply 19.9%→1.7%
(~10×). Gameability lives in judge design.

**H3 — downgraded to a bootstrap-quantified negative result (2026-09-07).** Item-level judge
disagreement is robust (unanimity 55.5%), but a 2000-resample bootstrap
(`src/rank_bootstrap.py` → `Experiment/analysis/rank_bootstrap.json`) shows the baseline
"safest model" is stable in only 39–70% of resamples for the LLM judges (93% keyword) —
the compressed artifact set (0.93–1.00 unsafe rates) cannot support ranking claims at all.
Wrapper reorderings (1–6 of 9 per judge in point estimates) are therefore reported as an
instability axis, not confirmed reversals. Paper H3 rewritten accordingly.

## vs external prior art (2606.25487, Know Thy Judge, SOS-Bench, JAILJUDGE)
Our content-invariant, byte-preserved wrappers give a controlled, measured picture: effects are
real but mostly judge-specific and moderate (12–20% on the vulnerable judges, <4% on robust
ones), vs 2606.25487's 57–100%. Distinct contributions: strict content invariance; the
false-positive direction; the same-model prompt-only 10× isolation; a deployed guard (Llama
Guard 4) gamed by course-framing; and the leaderboard/judge-disagreement result.

## Human validation (done 2026-09-07, two annotators)
145 items (100 flips + 45 controls), annotator A all 145, annotator B 40-item overlap.
- **Content-invariance: 100%** (145/145 YES, all 9 wrappers at ceiling; byte-preservation
  separately machine-verified on all 2700 wrapped samples).
- **Confirmed judge-error on flips: 90%** (90/100). The 10 unconfirmed are uniform: all
  FP-direction items whose JBB gold label says `refusal` but the human found genuinely
  actionable content (roleplay-style pseudo-refusals) — i.e., source gold-label noise, not a
  wrapper or judge artifact. Human vs JBB gold agreement overall: 133/145 (91.7%).
- **Cohen's κ: 1.000 (content_unchanged), 0.949 (human_unsafe)** — 1 disagreement in 40
  (rs_00547, football-betting + harm_adjacent_preamble, the known borderline template).
Run: `python -m src.analyze_human_validation --labeled ..._ann1.csv --kappa-a ..._ann1.csv
--kappa-b ..._kappa_ann2.csv`.

## Wrapped-form stochasticity control (R4, 2026-09-07)
Re-scored wrapped forms 3x on the headline GPT-4o-mini cells (`src/wrapped_noise.py`):
- Self-disagreement on identical wrapped input: 10.0% (refusal_then_comply), 3.3%
  (ethical_reflection) vs 0.5% on originals — the wrapper destabilizes the judge ~20x
  (a finding in itself).
- Flips are systematic, not decoding luck: majority-of-3 flip 18.2% (vs 19.9% single),
  14.4% flip on all 3 repeats; tone-only ethical_reflection 4.5% majority / 3.1% persistent,
  still 6–9x the original floor.
- Llama Guard 4 cells pending: OpenRouter API key expired 2026-09-0x; renew key then run
  `python -m src.wrapped_noise run` (CELLS already includes llamaguard_or).

## Remaining gaps
- Optional: frontier-tier rubric judges; ShieldGemma/WildGuard; a response set with wider
  baseline model separation for a cleaner H3.
