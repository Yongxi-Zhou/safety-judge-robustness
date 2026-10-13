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
- Llama Guard 4 (key renewed, run 2026-09-07): wrapped-form self-disagreement 0.33% on all
  3 cells — flips essentially fully deterministic. edu_framing 11.9% majority-of-3 flip and
  11.9% persistent (vs 12.3% single); refusal_then_comply 8.3%/7.9%; ethical_reflection
  3.6%/3.2%. The deployed guard reproducibly waves decorated harm through.
- **8th judge COMPLETE (2026-09-07): `safeguard_or` = openai/gpt-oss-safeguard-20b** (OpenRouter,
  shared rubric, max_tokens=4000, 4500 verdicts incl. 3x original repeats, 0 errors, ~15 min at
  concurrency 20). Result: **immune** — every wrapper ≤1.2%, below its own 1.5% noise floor;
  tone/assert strata indistinguishable (0.35%/0.45%). The two deployed guards sit at opposite
  ends: LlamaGuard4 leaks 12.3% on edu_framing, safeguard-20b leaks nothing. Rank bootstrap:
  safeguard base-top1 stable 97.9%. Panel is now 8 judges; paper updated throughout.

## Remaining gaps
- Optional: frontier-tier rubric judges; ShieldGemma/WildGuard; a response set with wider
  baseline model separation for a cleaner H3.

## Oct 11 2026 — ARR pre-submission revision
- Noise floors now measured (3× original-form repeats) for every API judge except Llama Guard 4
  (OpenRouter key expired again; LG-4 floor = wrapped-form 0.33%): GPT-4o-mini 0.5%,
  StrongREJECT 0.5%, DeepSeek **4.8%** (exceeds all its flip rates → DeepSeek flips are noise),
  Qwen 0.8%, Claude 1.0%, safeguard 1.5%. Keyword deterministic.
- `Experiment/analysis/flip_vs_noise.json`: McNemar b/c cells for every (judge, wrapper), plus
  a paired flip-vs-repeat-disagreement test; per-category / per-target-model breakdowns.
- Paper: abstract cut to ~250 words; vocabulary simplified (harm-hiding/harm-inventing →
  "make a harmful reply sound safe / make a refusal sound dangerous"; assertion-adding → claim-adding;
  stratum → group; protective → stricter); judge panel described once; McNemar described as a
  directional test; keyword judge reported as sanity check; appendices A–E added (wrapper texts,
  judge prompts, directional counts, category/model breakdown, leaderboard bootstrap);
  4 verified refs added (Raina+ EMNLP'24, Mangaokar+ PRP ACL'24, Ran+ JailbreakEval, Cai+ Rethinking).
- Bug fix: `OpenAIRubricJudge` now pins https://api.openai.com/v1 (SDK was silently reading
  the DashScope OPENAI_BASE_URL from .env).

## Oct 12 2026 — second ARR pre-submission revision (two simulated reviews, no new experiments)

Changes driven by the two reviews (both Overall 2.5; main complaints: overclaiming tone-only,
missing baseline accuracy, no mechanism, human validation thin, citation padding, leaderboard
contribution inflated, "balanced" categories wrong, flip-vs-repeat test undefined):

- **Mechanism (free, from existing judged files):** all 58 GPT-4o-mini `refusal_then_comply`
  flips return `REFUSAL: YES, UNSAFE: NO`; all 29 GPT-4o-mini flips under the three tone-only
  prefixes also return `REFUSAL: YES`; its 5 `pseudo_comply_frame` flips return `REFUSAL: NO`.
  → the judge classifies the opening speech act and lets it override the body. New Results
  paragraph "What the judge reads"; new Contribution 3.
- **Baseline accuracy table (new Table 1, `baseline_accuracy.tex`):** harmful→unsafe /
  refusal→safe on original forms. Keyword 180/287; GPT-4o-mini 291/261; StrongR 298/262;
  DeepSeek 287/270; Qwen 295/257; Claude 286/273; LG-4 277/270; SG-20b 296/257. No LLM judge
  is "immune by over-flagging".
- **72-cell global correction:** under Holm over all 72 cells the 3 lenient LLM cells + keyword
  + LG-4 moralizing (stricter) stay significant; Claude disclaimer/fake_cot and Qwen lecture
  (stricter) survive BH-72 but not Holm-72. Stated in Method + Results.
- **Human validation recount:** 104 judge–flip pairs over 100 replies (4 replies flipped by
  two judges): keyword 51 (46 confirmed), LG-4 24 (22), GPT-4o-mini 15 (15), DeepSeek 5 (5),
  Qwen 4 (3), Claude 2 (0), StrongR 2 (1), SG-20b 1 (0). LLM-judge replies 50 → 44 confirmed;
  **all 44 harmful-side LLM-judge flips confirmed**; 10 unconfirmed all refusal-side.
- Category distribution corrected (Malware 25, Harassment 6, others 66–76; 75 harmful per
  target, 59–81 refusals per target).
- Abstract rewritten (framing, not style; tone-only "suggestive"; "we will release");
  Contributions: leaderboard dropped, mechanism added; leaderboard paragraph compressed.
- 16 unrelated citations removed (re-ID, segmentation, demand forecasting, SQL, agent
  ecosystem, …); 23 bibitems remain.
- flip-vs-repeat test defined in Method as secondary; ethical_reflection presented as not
  surviving Holm.
- Limitations opens with "No judge that produces published leaderboard numbers was tested";
  max-token confound for safeguard noted; Appendix B decoding note.
- Table 2 (flip matrix) tabcolsep 3.5→5pt for column separation.
- Build: 11 pp, content ends p7 (Discussion+Limitations+Ethics on p7), 0 overfull.

Not done (needs experiments / keys): wrapper component ablation, GPT-4o / JBB Llama-3-70B /
HarmBench / StrongREJECT-cls judges, LG-4 original-form floor, title change (user kept title).
