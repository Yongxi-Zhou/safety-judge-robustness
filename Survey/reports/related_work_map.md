# Related-Work Map — Safety × Evaluation (COLM / ICLR / ICML / NeurIPS / ACL / EMNLP / AAAI, 2025–26)

Compiled from a multi-venue survey. Our contribution sits in the **"the judge is the weakest
link"** cluster; we are the first controlled *content-invariant style attack on the safety
verdict itself* with a leaderboard-reversal demonstration.

## Cluster 1 — Gameable / unreliable judges (our direct lineage)
- **Cheating Automatic LLM Benchmarks: Null Models Achieve High Win Rates** — ICLR 2025 (Oral).
  A constant, input-independent reply wins 86.5% on AlpacaEval 2.0. Existence proof that
  LLM-judge leaderboards are gameable with zero real content. *We port this to safety and make
  the manipulation content-invariant rather than content-free.*
- **Assessing Judging Bias in Large Reasoning Models** — COLM 2025. Reasoning-mimicking phrases
  sway judges ("superficial reflection bias"). *Our `fake_cot` wrapper is the safety analogue.*
- **Pairwise or Pointwise? Evaluating Feedback Protocols for Bias in LLM-Based Evaluation** —
  COLM 2025. Protocol choice changes verdicts; pairwise judging is exploitable.
- **Rating Roulette: Self-Inconsistency in LLM-as-a-Judge** — Findings of EMNLP 2025.
  Intra-rater run-to-run instability of judges. *Motivates our noise-floor control.*
- **Preference Leakage: A Contamination Problem in LLM-as-a-Judge** — ICLR 2026. Judges favor
  their own model family. (Basis for our sibling idea; cited as related bias channel.)

## Cluster 2 — ASR / jailbreak-eval validity
- **Comparison Requires Valid Measurement: Rethinking ASR Comparisons in AI Red Teaming** —
  NeurIPS 2025 (Position). Most cross-paper ASR comparisons are invalid (judge error,
  prompt-set composition, attempt budget). *Our closest "call to arms"; we supply data on one
  concrete failure mode.*
- **JailMeter: An Evidence-Based Evaluation Framework for Jailbreak Attacks** — Findings of ACL
  2026. Validates an attack only if the response comprehends intent AND answers completely.
- **GuidedBench: Measuring and Mitigating Evaluation Discrepancies of In-the-wild Jailbreaks**
  — ICLR 2026. Per-case criteria cut inter-evaluator variance ≥76%; many "~100% ASR" methods
  produce incomplete harmful content.
- **Confusion is the Final Barrier: Rethinking Jailbreak Evaluation** — Findings of EMNLP 2025.
  ASR overstates real misuse; "success" ≠ dangerous knowledge.
- **Refusal-Aware Red Teaming: Exposing Inconsistency in Safety Evaluations** — EMNLP 2025.
  Internal refusal signal disagrees with external judge verdicts.

## Cluster 3 — Over-refusal & the safety/helpfulness frontier
- **OR-Bench** — ICML 2025. 80K "seemingly toxic" benign prompts; safety and over-refusal
  correlate (both measured by LLM judges — *a shared-bias confound our false-positive
  direction speaks to*).
- **FalseReject** — COLM 2025. 16K over-refusal prompts with structured-reasoning responses.
- **XSTest**, **SORRY-Bench** (ICLR 2025, with a judge meta-evaluation), **AdaCD** (ACL 2026).

## Cluster 4 — Guardrail / pipeline / agent-safety evaluation
- **STACK: Adversarial Attacks on LLM Safeguard Pipelines** — AAAI 2026. Attacks full
  input+model+output guard pipelines. *We attack the guard/judge from the scoring side, not the
  input side.*
- **AgentAuditor** (NeurIPS 2025), **Agent-SafetyBench** (ACL 2025), **SafeToolBench**
  (EMNLP 2025), **AgentRewardBench** (COLM 2025) — trajectory/tool-safety judging.

## Cluster 5 — Evaluation-awareness / sandbagging (sibling idea territory)
- **Steering Evaluation-Aware LMs To Act Like They Are Deployed** — ICLR 2026 (white-box).
- **LLMs Often Know When They Are Being Evaluated** — arXiv, widely cited.

## The gap we fill
Every failure mode above — null-model cheating, superficial-reflection bias, ASR invalidity,
shared judge bias in the over-refusal frontier — is demonstrated for *general* eval or for the
*attack-input* side. **No accepted paper runs a controlled, content-invariant style-wrapper
attack on the safety verdict and shows it reorders a safety leaderboard.** That is our paper.

## Key citations to include (verify DOIs at write-up)
Cheating Automatic LLM Benchmarks (ICLR'25); ASR position paper (NeurIPS'25); JailMeter (ACL'26
Findings); GuidedBench (ICLR'26); Assessing Judging Bias in LRMs (COLM'25); Rating Roulette
(EMNLP'25 Findings); OR-Bench (ICML'25); SORRY-Bench (ICLR'25); Llama Guard; ShieldGemma;
WildGuard; StrongREJECT; HarmBench; JailbreakBench.
