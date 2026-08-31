# Precedents: "same method, model → judge" published as two independent papers

Compiled to justify that the group's two papers — (P1) surface-form sensitivity of safety
**models** and (P2, this project) style sensitivity of safety **judges** — are distinct
contributions, not salami slicing.

## Strongest precedent pairs (model-side → evaluator-side, both at reputable venues)

| # | Model-side paper | Evaluator/judge-side paper | Note |
|---|---|---|---|
| 1 | Universal Adversarial Triggers (Wallace et al., **EMNLP 2019**) | Is LLM-as-a-Judge Robust? Universal Adversarial Attacks on Zero-shot LLM Assessment (Raina, Liusie, Gales, **EMNLP 2024**) | Same construct (input-agnostic trigger), model → judge, both EMNLP. Best clean transfer. |
| 2 | Lost in the Middle (Liu et al., **TACL 2024**) | Judging the Judges: Position Bias in LLM-as-a-Judge (Shi et al., **AACL-IJCNLP 2025**) | Position bias, model → judge. |
| 3 | FormatSpread: Sensitivity to Spurious Prompt Features (Sclar et al., **ICLR 2024**) | Know Thy Judge: Robustness Meta-Evaluation of LLM Safety Judges (Eiras et al., arXiv 2503.04474) | Prompt-sensitivity of models → of safety judges. Most on-point to P1/P2. |
| 4 | State of What Art? Multi-Prompt Eval (Mizrahi et al., **TACL 2024**) | LLMs Cannot Reliably Judge (Yet?) (arXiv 2506.09443) | Multi-prompt fragility, model → judge; judge paper uses flip-rate framing. |
| 5 | GCG universal jailbreak (Zou et al., 2023) | How Reliable Is Your Jailbreak Judge? (arXiv 2606.25487); JAILJUDGE (ICLR track) | Jailbreak of model → reliability/gameability of jailbreak judge. **Closest to P2 — also a novelty risk, see below.** |

## Same-group "same method, new object" precedents (both accepted separately)
- **HELM → HEIM → VHELM** (Stanford CRFM; TMLR 2023 → NeurIPS D&B 2023 → NeurIPS D&B 2024). Cleanest "same holistic-eval method, new object each time."
- **LLM-as-a-Judge/MT-Bench (NeurIPS 2023) → Arena-Hard/BenchBuilder (2024)** (LMSYS).
- **Red Teaming LMs with LMs (EMNLP 2022) → Model-Written Evaluations (ACL Findings 2023)** (Perez et al.).
- **CheckList (ACL 2020 Best Paper) → AdaTest (ACL 2022)** (Ribeiro et al.).
- **RewardBench (NAACL Findings 2025) → RewardBench 2 (2026)** (Ai2) — model-eval → reward-model-eval.
- **WildTeaming / WildGuard / WildBench** (Ai2, NeurIPS 2024) — one "in-the-wild" method split into 3 standalone papers.

## The formal rules (must satisfy)
- **ARR/ACL:** an author's two submissions must not overlap **>75%** in content/results; "salami-sliced papers are not welcome and may be desk rejected." Cross-cite + disclose concurrent related work.
- **NeurIPS 2025:** "slicing contributions too thinly is discouraged"; reviewers treat any overlapping-author submission as prior work, and "if publishing one would render the other too incremental, both may be rejected." → must cite the sibling and make each stand alone.
- **COPE:** salami = same population + same method + same question. NOT salami if different hypothesis / object / method.

## Legitimacy checklist applied to P1 vs P2
| Test | P1 (models) | P2 (judges) | Pass? |
|---|---|---|---|
| Research question | Is a model's safety behavior stable across prompt surface forms? | Does a judge's verdict track content or style? | ✓ different |
| Object under test | the model | the judge | ✓ different |
| Headline finding | union-minus-worst gap 3.3–12.9pp | flip 19.9%; 10× prompt effect; 5/9 ranking reversals | ✓ non-overlapping |
| Standalone value | yes | yes | ✓ |
| Method role | perturbation+stats to test the model | same stats to test the judge | shared skeleton — differentiate framing |
| Merge test | merging dilutes two distinct messages | — | ✓ legitimately separate |

**Verdict:** P1 and P2 clear every salami criterion — different question, different object, non-overlapping findings. The shared statistical skeleton (meaning-preserving perturbation + McNemar/bootstrap flip rates) must be explicitly framed as "reused as a tool," with P1 cited as the group's prior work.

## The REAL risk is external prior art, not self-overlap
P2's contribution overlaps with existing judge-robustness work that must be cited and differentiated:
- **arXiv 2606.25487 "How Reliable Is Your Jailbreak Judge?"** — reports benign-framing wrappers flip safety-judge verdicts 57–100%. Very close to P2's style-wrapper attack.
- **JAILJUDGE** (ICLR track) — benchmark for jailbreak-judge reliability.
- **Know Thy Judge** (2503.04474) — robustness meta-evaluation of safety judges.
- **"Style Outweighs Substance: Failure Modes of LLM Judges"** (Feuer et al., SOS-Bench, 2409.15268).

P2 must carve a differentiated niche vs these: e.g., strict **content-invariance by construction** (byte-preserved body, not benign paraphrase), the **false-positive direction** (harm-inventing on refusals), the **same-model prompt-only 10× contrast** (gpt4o vs strongreject), and the **leaderboard-reversal** result. "They show judges are foolable; we isolate that it is the judge prompt, quantify both directions against a noise floor, and show it reorders leaderboards."

## Caveat
Double-check before citing: Perez "Model-Written Evaluations" arXiv id (2212.09251) and the exact ARR ">75%" wording against the live CFP.
