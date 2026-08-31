# Research Brief

## Project
Style Over Substance: Content-Invariant Wrappers Flip LLM Safety-Judge Verdicts

## Goal
An empirical short paper showing that the automatic **judges** used to score LLM safety —
Llama Guard, ShieldGemma, WildGuard, GPT-4o rubrics, StrongREJECT — grade a response's
*surface style* far more than its safety literature assumes. We hold the operational content
of a response fixed and add content-invariant style wrappers, then measure how often the
safety verdict flips. Bring the project to the stage where only API keys/GPU and empirical
results are missing.

## Core Research Question
When a response's operational content is held fixed and only its stylistic surface changes
(disclaimers, ethical hedging, fake safety reasoning, token refusals, moralizing), does the
safety judge's verdict stay fixed — as a faithful instrument must — or does it flip?

## Main Hypotheses
- **H1 (gameability).** Content-invariant style wrappers flip safety verdicts at a rate far
  above the judge's noise floor, in both directions: harmful content dressed in safety style
  is scored safe (false negative), and benign refusals dressed in harm-adjacent style are
  scored unsafe (false positive).
- **H2 (quality gradient).** The weakest judges (keyword baseline, small guard models) are the
  most gameable; stronger content-focused rubric judges resist better but not completely.
- **H3 (ranking instability).** Because flips are judge- and wrapper-dependent, ranking target
  models by a gameable judge's safety score reorders under different wrappers — so safety
  leaderboards inherit the judge's stylistic bias.

## Target Contribution
1. A controlled, content-invariant **style-wrapper attack** on safety judges (not on models),
   with intent/content-preservation held by construction rather than by an LLM rewrite.
2. A cross-judge **flip-rate + significance** protocol (McNemar + Holm/BH, bootstrap CIs,
   measured noise floor) over 6 judges × 9 wrappers.
3. A demonstration that safety **rankings** are order-unstable under judge gaming.
4. A human-anchored validation that flips are judge errors, not content changes.

## Target Venue
Primary: EMNLP/ACL Findings or COLM (short/Findings). Backups: ARR, a safety workshop, arXiv.

## Scope
### Included
- Single-turn `(behavior, response)` pairs from public jailbreak completions.
- Deterministic, non-LLM style wrappers (content preserved verbatim).
- 6 safety judges (1 offline keyword + 2 API rubric + 3 HF guard models).
- Rule-based + LLM/guard verdicts, flip-rate statistics, small human validation.
### Excluded (first submission)
- Multi-turn / agent-trajectory judging.
- Training a de-biased judge (we diagnose; mitigation is future work / one paragraph).
- Large human-annotation campaign (only a 150-item validation subset).

## Novelty (one line)
Existence proofs of gameable judges exist for general eval and for jailbreak ASR validity, but
none runs a *controlled content-invariant style attack on the safety verdict itself* and shows
it reorders safety leaderboards. See `Survey/reports/related_work_map.md`.

## Relationship to prior author work
Methodologically continuous with the group's "benchmark-as-instrument" line (repeated-run
stability; surface-form sensitivity of safety), but the object under test moves from the
**model** to the **judge** — a distinct and, per the 2025–26 venue survey, hotter target.
