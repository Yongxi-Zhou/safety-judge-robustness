#!/usr/bin/env bash
# Full experiment run: rulebased (free) + gpt4o + strongreject (gpt-4o-mini), then analysis.
# Loads ONLY OPENAI_API_KEY from the given .env; ignores any ambient OPENAI_BASE_URL so the
# rubric judges hit real OpenAI (not a DashScope/Qwen compatible endpoint).
set -euo pipefail
cd "$(dirname "$0")/.."

ENVFILE="${1:-$(cd "$(dirname "$0")/.." && pwd)/.env}"
export OPENAI_API_KEY="$(grep -E '^OPENAI_API_KEY=' "$ENVFILE" | head -1 | cut -d= -f2-)"
unset OPENAI_BASE_URL OPENAI_JUDGE_BASE_URL || true
PY=./.venv/bin/python

echo "[run_full] rulebased (free)…"
$PY -m src.pipeline --stage 3 --judge rulebased

echo "[run_full] gpt4o (gpt-4o-mini), repeats=3 noise floor on originals…"
$PY -m src.pipeline --stage 3 --judge gpt4o --repeats 3 --concurrency 4

echo "[run_full] strongreject (gpt-4o-mini), repeats=1…"
$PY -m src.pipeline --stage 3 --judge strongreject --repeats 1 --concurrency 4

echo "[run_full] per-judge stats…"
for J in rulebased gpt4o strongreject; do $PY -m src.pipeline --stage 4 --judge "$J"; done

echo "[run_full] aggregate…"
$PY -m src.pipeline --stage 5 --judges rulebased gpt4o strongreject

echo "[run_full] DONE"
