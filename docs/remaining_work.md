# Remaining Work to Submission

Status snapshot (2026-08-30): dataset + pipeline + 3-judge run + draft with real numbers done.
The core claims (H1 gameable, H2 judge-property/10×, H3 ranking reversal) hold on complete
`rulebased` + `gpt4o` (GPT-4o-mini) data. Gaps below, prioritized.

## Tier 1 — must-have for a credible submission

### T1.1 Broaden the judge panel — DONE (API-only, no GPU, no Llama) ✅
- [x] **Claude judge** (Claude Haiku 4.5) — complete, 600 responses.
- [x] **DeepSeek judge** (deepseek-chat) — complete, 600 responses.
- [x] **Qwen judge** (qwen-plus) — complete, 600 responses.
Panel is now 6 judges across 4 vendors (rulebased, GPT-4o-mini ×2 rubrics, DeepSeek, Qwen,
Claude). Key result: gameability is judge-specific (refusal_then_comply 19.9% on GPT-4o-mini vs
0.4–3.5% elsewhere). See docs/results_summary.md.
- [ ] *(optional)* **GPT-4o (full)** judge — registry name `gpt4o_full` wired; not run (OpenAI
  key throttled). Run when a faster key is available.
- [ ] *(optional, still API)* **Llama Guard 3 via Bedrock/OpenRouter** — the deployed guard angle.
- [ ] *(optional, needs GPU)* ShieldGemma, WildGuard via HF.

### T1.2 Finish StrongREJECT false-positive coverage — DONE ✅
- [x] Completed via OpenRouter (`openai/gpt-4o-mini`, dodges the throttled direct key). Full
  600/600; confirms StrongREJECT robust (refusal_then_comply 1.7% vs gpt4o 19.9%).

### T1.1b Deployed guard model — DONE ✅
- [x] **Llama Guard 4 12B** via OpenRouter (`scripts/run_llamaguard.sh`). 600/600. Significantly
  gamed: educational_framing 12.3% (Holm-sig), refusal_then_comply 8.3% (Holm-sig). The paper's
  strongest deployment-relevant result. Panel is now 7 judges.

### T1.3 Human validation (150 items) — anchors the whole validity claim
- [ ] Two annotators label the stratified subset (`src/human_subset.py`): `content_unchanged`
  (validity) + `human_unsafe` (ground truth). Report inter-annotator κ and the % of flips
  confirmed as judge errors. Target κ ≥ 0.8.

## Tier 2 — strengthen / preempt reviewer objections

### T2.1 H3 needs a response set with real per-model separation
- [ ] Current base unsafe rates are compressed (0.93–1.00) so ranking reversals are on tiny
  margins. Build/select a set where the four models genuinely differ in safety (mix in more
  refusals, or non-jailbreak responses), so the leaderboard reversal lands on a real gap.

### T2.2 Power the subtle wrappers (or frame them honestly)
- [ ] disclaimer / ethical_reflection / fake_cot clear the noise floor by CI but not Holm at
  n≈291. Either raise n (more responses) or frame as "subtle wrappers small-but-real, the strong
  wrapper large." Note 2606.25487 reports 57–100% flips — reviewers will compare.

### T2.3 At least one frontier judge
- [ ] Include GPT-4o (not mini) and/or Claude so the headline "even strong judges flip" holds.

## Tier 3 — positioning & polish (write-up)

### T3.1 Differentiate from external prior art (most urgent writing task)
- [ ] Read in full and write a point-by-point delta vs: **2606.25487 "How Reliable Is Your
  Jailbreak Judge?"**, **Know Thy Judge (2503.04474)**, **JAILJUDGE**, **SOS-Bench (2409.15268)**.
  Our niche: content-invariance by construction; false-positive direction; same-model prompt-only
  10× contrast; leaderboard reversal. See `Survey/reports/independent_paper_precedents.md`.

### T3.2 Supplementary analyses (code exists, just run)
- [ ] Per-harm-category flip breakdown.
- [ ] Wrapper redundancy curve (how many wrappers cover X% of a judge's flippable surface —
  mirrors P1's redundancy characterization).

### T3.3 Cross-cite P1
- [ ] Cite the group's surface-form-sensitivity paper as prior work; frame this as moving
  instability from the model to the measurement instrument.

## Paths to submission
- **Minimum viable (Findings/COLM short):** T1.1 (API judges) + T1.2 + T1.3 + T3.1. ~1.5–2 weeks.
- **Strong (main track):** add T2.1–T2.3. ~+1 week.

## Why not (necessarily) Llama
Llama Guard was in the plan only as the canonical *deployed guard model*, not because the thesis
needs it. It is API-accessible (Bedrock/Together/Groq), so "needs a GPU" is false — but a
cross-vendor chat-judge panel (Claude + DeepSeek + Qwen + GPT-4o) already delivers the diversity
the paper needs, entirely via API. Add Llama Guard via Bedrock only if we want the explicit
"purpose-built moderator is also gamed" sentence.
