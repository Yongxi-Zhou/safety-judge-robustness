# Paper Framing

## One-sentence pitch
Safety judges grade style, not just substance: adding content-invariant stylistic wrappers to a
fixed response flips widely used safety judges' verdicts — enough to reorder safety leaderboards.

## Why this framing wins
- **Free motivation.** An ICLR 2025 Oral (null-model cheating) and a NeurIPS 2025 position paper
  (ASR validity) have already convinced the community that judges are the weak link. Reviewers
  arrive pre-sold; we supply the missing controlled measurement for *safety*.
- **Cheap and decisive.** The instrument under test is the judge, so no target-model queries are
  needed — just re-scoring a fixed response set. < $5 + a few GPU-hours.
- **Content invariance = airtight validity.** Because wrappers add only style (byte-preserved
  body), a verdict flip is unambiguously judge error, not a real safety change. No LLM-rewrite
  confound, no intent-preservation guesswork.
- **A memorable artifact.** The ranking-reversal table ("swap a disclaimer in and model B
  overtakes model A on the safety leaderboard") is the figure people screenshot.

## Contrast with the group's two prior papers
- Prior: single-run vs repeated-run **model** stability; single canonical vs surface-form
  **model** safety. Object under test = the model; source of variation = decoding / prompt form.
- This: single style vs style-wrapped **judge** verdict. Object under test = the judge; source
  of variation = response surface style. Same "benchmark-as-instrument" DNA, new and hotter
  target per the 2025–26 survey.

## Titles (pick one)
1. *Style Over Substance: Content-Invariant Wrappers Flip LLM Safety-Judge Verdicts*
2. *Judging the Judge: Safety Verdicts Are Gameable by Style Alone*
3. *A Disclaimer Is All You Need: Stylistic Gaming of LLM Safety Judges*

## Risks & rebuttals
- "Some wrappers are obviously adversarial (token refusal)." → Report per-wrapper; the subtle
  ones (disclaimer, ethical reflection, moralizing suffix) carry the result; obvious ones go to
  an appendix. Aggregate CI excludes the noise floor regardless.
- "Only 9 wrappers." → Scoped as a characterization of this wrapper set, not a population — same
  discipline as the group's prior work.
- "Just fine-tune a better judge." → We diagnose; mitigation (content-only rubric, majority-vote
  panel) is a one-paragraph future-work pointer, and our cross-judge data already shows the
  strong rubric judge is least gameable.

## Sibling ideas parked for later (from the same survey)
- Family-preference leakage in *safety* judges (ICLR'26 Preference Leakage, safety version).
- Black-box evaluation-awareness → refusal-rate shift on API models.
- Chat-safety knowledge–action gap (classify-vs-comply on the same prompt).
