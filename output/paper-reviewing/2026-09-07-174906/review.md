# Paper Review: Style Over Substance: Content-Invariant Wrappers Flip LLM Safety-Judge Verdicts

*Format: generic academic · Severity: standard · Reviewed: 2026-09-07*
*Reviewer note: review produced with full knowledge of the project's internals; calibrated to what an external reviewer would see in the PDF alone.*

## Summary

The paper asks whether automatic safety judges (keyword baselines, rubric-prompted LLMs, and deployed guard models) grade the operational content of a response or merely its style. It constructs nine "content-invariant style wrappers" — fixed strings prepended/appended to a response with the body preserved byte-for-byte — and measures verdict-flip rates over 600 JailbreakBench responses × 8 judges, with paired McNemar tests, bootstrap CIs, measured noise floors on both original and wrapped forms, a tone-only vs. assertion-adding stratification, a 145-item two-annotator human validation (κ=0.95–1.0), and a bootstrap analysis showing the underlying leaderboard is unstable to sampling. Headline findings: a token-refusal wrapper flips 19.9% of GPT-4o-mini's correct unsafe verdicts (systematic under majority-of-3 rescoring); the deployed Llama Guard 4 is deterministically fooled 12.3% by a course-framing sentence while a second deployed guard (gpt-oss-safeguard-20b) is immune; a prompt-only change (StrongREJECT-style rubric) cuts the attack ~10×.

## Strengths

1. **Causal cleanliness by construction.** Byte-preserved wrapping eliminates the intent-preservation confound that plagues LLM-rewrite-based reformulation studies; the paired design plus correct-on-original denominators makes each counted flip unambiguously wrapper-induced. The 2,700-sample byte-level check and 100% human content-invariance rate close the loop.
2. **Unusually complete controls.** Original-form noise floor, wrapped-form noise floor, majority-of-three rescoring, tone-only/assertion-adding stratification, Holm+BH correction, and a bootstrap that *undercuts the authors' own H3* — the willingness to report a negative result (rankings unstable to sampling alone) is exemplary and rare.
3. **The two-guard contrast is genuinely informative.** Llama Guard 4 deterministically (0.33% self-disagreement, 11.9% flip on all three repeats) waves decorated harm through, while gpt-oss-safeguard-20b never exceeds its own noise floor. This turns the paper from "judges are gameable" into "robustness is an attainable, auditable, judge-specific property," which is actionable.
4. **Honest scoping.** The introduction explicitly disclaims universality ("most judges in our panel are robust to most wrappers"), and the limitations section pre-empts the strongest objection (whether assertion-adding wrappers are really "style") with the stratified reporting.
5. **Cheap and reproducible.** All-API panel, <$5, code+labels released, offline smoke test.

## Weaknesses

1. **Title collision and a missing, directly-relevant prior line (major).** *Style Over Substance: Evaluation Biases for Large Language Models* (Wu & Aji, 2023; COLING; ~80 citations) already established that LLM evaluators favor style over factual substance in general evaluation, and shares this paper's exact title phrase. It is neither cited nor differentiated. The foundational LLM-judge bias literature (Zheng et al. 2023, MT-Bench/Chatbot Arena — position, verbosity, self-enhancement biases; Wang et al. 2023, positional-bias "not fair evaluators") is also absent, as is JudgeDeceiver (Shi et al., CCS 2024, ~216 citations), the closest *attack-side* relative: it manipulates LLM-as-a-judge from the response side via optimized injected sequences. The paper's actual novelty (safety verdict, byte-invariance, FP direction, deployed guards) survives all of these, but the current related-work section leaves the novelty claim exposed and the title invites an unfavorable comparison.
2. **Systems named but never cited (major, easy fix).** Llama Guard (4) is attacked, "StrongREJECT-style rubric" names a benchmark, and ShieldGemma/WildGuard/HarmBench are mentioned — yet none of the original papers (Inan et al. 2023; Souly et al. 2024; Zeng et al. 2024; Han et al. 2024; Mazeika et al. 2024) appears in the reference list. (BibTeX entries for three of these exist in the source but are never \cite'd.)
3. **Effects on most judges are small and sub-significance.** Five of eight judges never exceed 3.5% on any wrapper; subtle harm-hiding wrappers do not survive Holm anywhere. The paper says this honestly, but the abstract's emphasis structure still leads with the two vulnerable judges; a skeptical reader can summarize the same table as "two judges have two bugs."
4. **Dated response distribution.** All 600 responses come from 2023-era targets (GPT-3.5, GPT-4-0125, Vicuna-13B, Llama-2-7B) and ~60% are truncated mid-sentence at the artifacts' length cap. Whether stylistic wrappers interact the same way with longer, modern, non-truncated responses is untested.
5. **Human validation depth.** One annotator labels all 145 items; the second labels only a 40-item overlap. κ is excellent, but annotator identity/expertise/instructions are not described in the paper body, and 145 of ~2,700 wrapped samples is a thin slice for the content-invariance claim (mitigated by the byte-level check).
6. **Tangential citations in the Discussion.** Person re-identification under clothing change and brain-lesion segmentation are a stretch for the "invariance principle" sentence; likewise the text-to-SQL benchmark audits in §2. These read as padding and dilute an otherwise tight paper.

## Major Issues

1. **Missing engagement with the LLM-judge-bias and judge-attack literature.**
   → Fix: add ~4 citations (Wu & Aji 2023; Zheng et al. 2023; Wang et al. 2023; Shi et al. 2024) with 2–3 sentences of differentiation: prior work shows style bias in *general* pairwise evaluation and optimization-based judge attacks; this paper shows *semantic-free, zero-cost, human-readable* wrappers flip the *safety* verdict on *deployed guards*, with content invariance by construction. Consider whether to keep the title given the collision — a subtitle tweak ("…Flip LLM Safety-Judge Verdicts" already differentiates; keeping it is defensible, but the first citation of Wu & Aji should acknowledge the borrowed phrase.
2. **Cite the systems you attack and name.**
   → Fix: \cite llamaguard, strongreject, harmbench (entries already in the .bib), and add ShieldGemma/WildGuard citations where named.
3. **Dual-use and disclosure.**
   → Fix: the Ethics section argues wrappers confer no new capability, which is true for *models* — but the released wrapper strings are working evasion recipes against a *deployed moderation filter* (Llama Guard 4, 12.3% deterministic evasion). State whether the findings were disclosed to Meta (and OpenAI for the destabilization result) before release, or justify why disclosure is unnecessary; reviewers at security venues (e.g., SaTML) will ask.

## Minor Issues

1. Table 1 is dense: nine long snake_case column headers force a heavy \resizebox; consider transposing (wrappers as rows, grouped by stratum and direction), shortening names, and bolding Holm-significant cells. CIs appear only in prose — an appendix table with CI and per-direction rates would help.
2. The stratified aggregate "keyword judge: 0% vs. 30.7%" needs one clause explaining that 30.7% is the item-weighted mean over all four assertion-adding wrappers (readers will look for it in Table 1 and find only 100%/0%).
3. "up to 7 forms" (abstract) vs. "9 wrappers" elsewhere — the 7 comes from per-response applicable forms (original + 6 or original + 3); one parenthetical would prevent a reviewer double-take.
4. Author block says single author + "co-authors TBD" style affiliation; ensure finalized before submission. Annotator provenance (who, qualifications, compensation if applicable) should be one sentence in §5 or an appendix.
5. Repository URL is promised ("released") but not given; add (anonymized for review if needed).
6. Consider trimming the re-ID/medical-segmentation sentence and the text-to-SQL citations, or moving them to a footnote.

## Questions for Authors

1. Is the 19.9%→1.7% StrongREJECT-rubric reduction robust to prompt paraphrase, or is the specific rubric wording load-bearing? (One paraphrase-of-rubric control would cement H2.)
2. For Llama Guard 4, does the educational-framing flip persist when the wrapper is translated or lightly paraphrased? (Determinism at 11.9% suggests a template-level blind spot — is it the exact string or the framing concept?)
3. Were Meta/OpenAI notified of the deterministic evasion/destabilization results before public release?
4. Can you report the tone-only stratum's CI-vs-floor test per judge explicitly (which tone-only cells clear the floor with CI, not just point estimates)?
5. Do wrapped-form noise floors for the *robust* judges (e.g., Claude at 0.4%) stay at original-form levels, or does destabilization occur without flips?

## Missing Related Work

| Paper | Key contribution | Relevance | Cite in |
|---|---|---|---|
| Wu & Aji 2023, "Style Over Substance: Evaluation Biases for LLMs" (COLING) | LLM evaluators prefer stylistic quality over factual accuracy | Same phenomenon, general-eval side; same title phrase | §1, §2 ¶1 |
| Zheng et al. 2023, "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS D&B) | Foundational LLM-judge protocol; position/verbosity/self-enhancement biases | The canonical judge-bias reference | §2 ¶1 |
| Wang et al. 2023, "Large Language Models are not Fair Evaluators" | Positional bias; calibration mitigations | Judge-bias line | §2 ¶1 |
| Shi et al. 2024, "Optimization-based Prompt Injection Attack to LLM-as-a-Judge" (CCS) | Adversarial injected sequences flip judge selections | Closest attack-on-judge work; needs differentiation (optimized vs. human-readable zero-cost) | §2 ¶1 or ¶3 |
| Inan et al. 2023 (Llama Guard); Souly et al. 2024 (StrongREJECT); Mazeika et al. 2024 (HarmBench); Zeng et al. 2024 (ShieldGemma); Han et al. 2024 (WildGuard) | The systems named/attacked | Named in text, uncited | §3–4 |

## Scores

- **Overall Assessment**: **Accept (weak accept at a top venue)**
- **Overall Score**: 7/10
- **Confidence**: High (4/5)
- **Novelty**: Medium-High — controlled measurement + FP direction + deployed-guard contrast are new; style-bias phenomenon itself is not, and the related-work gap currently understates that
- **Technical Soundness**: High — control structure is the paper's outstanding feature
- **Significance**: Medium-High — directly actionable for anyone running safety evals; negative leaderboard result useful to the field
- **Clarity**: High — terminology section and honest scoping; Table 1 presentation is the weak spot
- **Reproducibility**: High — code/labels/smoke-test released; add repo URL and annotator details

## Additional Notes

The fastest route to a higher score: (i) the four missing judge-bias/judge-attack citations with sharp differentiation, (ii) cite the attacked systems, (iii) a disclosure statement. All are text-only fixes. The one cheap experiment that would strengthen H2 materially is a rubric-paraphrase control (Q1).
