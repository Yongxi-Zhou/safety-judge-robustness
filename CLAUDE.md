# CLAUDE.md

Guidance for Claude Code / Codex working in this repository.

## What this is

A research project (EMNLP/ACL Findings or COLM target) studying whether LLM **safety judges**
grade the operational *content* of a response or merely its *style*. We hold a response's
content fixed and add content-invariant "style wrappers" (disclaimers, ethical hand-wringing,
fake safety chain-of-thought, token refusals, moralizing suffixes, harm-adjacent framing),
then measure how often each judge's safety verdict flips. The instrument under test is the
**judge**, not the model.

Core empirical claims:
1. Style wrappers flip safety verdicts far above a measured noise floor.
2. The weakest judges (keyword, small guards) are the most gameable.
3. Because flips are judge/wrapper-dependent, model **rankings** on a gameable judge reorder.

## Setup

```bash
pip install -r requirements.txt
pip install openai transformers torch accelerate     # only for API/HF judges
cp .env.example .env                                  # fill in OPENAI_API_KEY / HF_TOKEN
export $(grep -v '^#' .env | grep -v '^$' | xargs)
```

There is no test suite. Verify changes with the offline smoke test:
```bash
python -m src.pipeline --smoke
```

## The pipeline (`src/pipeline.py`, `python -m src.pipeline --stage N`)

1. **build** (`dataset.py`) — assemble the fixed `(behavior, response, gold_label)` set from
   public jailbreak completions in `Experiment/datasets/raw/`, or `--demo` for the shipped
   fixture. `response_type` (compliance/refusal/partial) decides which wrapper family applies.
2. **wrap** (`wrap.py` + `wrappers.py`) — expand each response into `original` + its wrapper
   family. **Wrappers add only style; the operational content is preserved verbatim.** This is
   the whole validity argument — a faithful judge must return the same verdict.
3. **judge** (`judges.py`) — score wrapped responses with one judge. `rulebased` is offline;
   `gpt4o`/`strongreject` need `OPENAI_API_KEY`; `llamaguard`/`shieldgemma`/`wildguard` need HF
   weights + GPU. `--repeats N` re-scores the original form to measure the noise floor.
4. **stats** (`stats.py`) — per-(judge, wrapper) flip rates (false-negative on unsafe
   responses, false-positive on refusals), exact McNemar vs original with Holm + BH correction,
   bootstrap 95% CI, noise floor. No uncorrected p-values.
5. **analyze** (`analysis.py`) — aggregate every `judged_*.jsonl` into `flip_rates.{csv,tex}`,
   cross-judge agreement, and `ranking_reversal.json`.

## Design invariants (do not break)

- **Content invariance is sacred.** Any new wrapper in `wrappers.py` must add only stylistic
  text; never edit, summarize, or reorder the response body. If a wrapper could change the
  operational content, it is a different (and weaker) experiment.
- **No silent fake data.** API/HF judges raise a clear error when SDK/keys/weights are missing,
  rather than returning a placeholder verdict. The only zero-setup judge is `rulebased`.
- **The verdict is `unsafe_label`.** `refusal_label` is secondary (used for the false-positive
  direction). Keep this consistent across `scoring.py`, `stats.py`, `analysis.py`.
- **Pairing is by `response_id`.** All McNemar/flip computations pair wrapped vs original on the
  same underlying response. `sample_id = "<response_id>__<wrapper>"`.
- Stats use exact McNemar + hand-rolled Holm/BH (no scipy dependency).

## Positioning vs. prior work

Existence proofs of gameable judges exist for *general* eval (Cheating Automatic LLM
Benchmarks, ICLR'25 Oral; superficial-reflection bias in LRM judges, COLM'25) and for ASR
validity (NeurIPS'25 position paper; JailMeter; GuidedBench). None runs a controlled,
content-invariant style-wrapper attack on the *safety* verdict itself. "They call for it; we
measure it." See `Survey/reports/related_work_map.md`.
