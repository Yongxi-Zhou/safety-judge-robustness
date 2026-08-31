# Safety-Judge Robustness

Do LLM safety judges grade **content** or **style**? This project shows that
content-invariant *style wrappers* — educational disclaimers, ethical hand-wringing, fake
safety chain-of-thought, token refusals, moralizing suffixes — systematically flip the
verdicts of widely used safety judges (Llama Guard, ShieldGemma, WildGuard, GPT-4o rubric,
StrongREJECT, and a keyword baseline), even though the operational content of the response
is unchanged. Because the flip is judge- and wrapper-dependent, safety **leaderboards** built
on a gameable judge are not order-stable. Target venue: EMNLP / ACL Findings or COLM.

The instrument under test is the **judge**, not the model — so the unit of data is a fixed
`(behavior, response)` pair with a trusted gold label, and we only decorate the response.

## Project structure

```
├── judges.toml                # Judge panel (the instrument under test) + setup/cost
├── requirements.txt
│
├── src/                       # All experiment code
│   ├── pipeline.py            # 5-stage orchestrator (+ offline --smoke)
│   ├── dataset.py             # Build the fixed response set (raw ingest or --demo fixture)
│   ├── wrappers.py            # The content-invariant style-wrapper definitions
│   ├── wrap.py                # Stage 2: expand responses into wrapped variants
│   ├── judges.py              # Judge panel: rulebased (offline) + API/HF adapters
│   ├── scoring.py             # Verdict normalization + rule-based keyword judge
│   ├── stats.py               # Flip rates, exact McNemar + Holm/BH, bootstrap CI, noise floor
│   ├── analysis.py            # Aggregate tables (CSV/LaTeX), cross-judge agreement, ranking reversal
│   └── human_subset.py        # Stratified human-validation template export
│
├── Experiment/
│   ├── configs/experiment.yaml
│   ├── datasets/              # response_set, wrapped_responses, raw/ (source completions)
│   ├── outputs/              # judged_<judge>.jsonl
│   └── analysis/             # flip_rates.{csv,tex}, cross_judge.json, ranking_reversal.json
│
├── Publication/paper/         # LaTeX paper draft
├── Survey/reports/            # Related-work map (from the conference survey)
├── Ideation/ideas/            # Framing / novelty positioning
└── docs/                      # Research brief, experiment design, dataset+metrics, progress
```

## Quick start

```bash
pip install -r requirements.txt

# End-to-end offline smoke test — no API keys, rule-based judge, shipped demo fixture.
# Proves the whole pipeline (build → wrap → judge → stats → analyze) runs.
python -m src.pipeline --smoke

# --- real run, one judge at a time ---
# Stage 1: build the fixed response set from public jailbreak completions
python -m src.pipeline --stage 1 --raw Experiment/datasets/raw/jailbreakbench_completions.jsonl
# Stage 2: expand into content-invariant wrapped variants
python -m src.pipeline --stage 2
# Stage 3: score with each judge (rulebased offline; others need .env / GPU)
python -m src.pipeline --stage 3 --judge gpt4o --repeats 5     # repeats -> noise floor
python -m src.pipeline --stage 3 --judge llamaguard
# Stage 4: per-judge flip rates + significance
python -m src.pipeline --stage 4 --judge gpt4o
# Stage 5: aggregate all judges into the paper tables + ranking reversal
python -m src.pipeline --stage 5 --judges rulebased gpt4o strongreject llamaguard shieldgemma wildguard

# Human-validation template (content-invariance + judge-error anchoring)
python -m src.human_subset --n 150
```

## The judge panel

| Judge | Kind | Setup | Role |
|---|---|---|---|
| `rulebased` | keyword | none (offline) | weak baseline; most gameable |
| `gpt4o` | OpenAI rubric | `OPENAI_API_KEY` | strong LLM-judge baseline |
| `strongreject` | OpenAI rubric | `OPENAI_API_KEY` | content-only rubric |
| `llamaguard` | HF guard | GPU + gated access | deployed moderation guard |
| `shieldgemma` | HF guard | GPU + gated access | probability guard |
| `wildguard` | HF guard | GPU | open guard |

## Status

Code and paper scaffold complete; pipeline verified end-to-end offline (`--smoke`). What
remains before submission: (1) API keys / a GPU for the six judges, (2) dropping public
jailbreak completions into `Experiment/datasets/raw/`, (3) running the real experiment,
(4) the 150-item human validation. See `docs/project_progress.md`.
