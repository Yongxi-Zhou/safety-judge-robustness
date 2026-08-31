#!/usr/bin/env bash
# Run the cross-vendor API judges (Claude, DeepSeek, Qwen) — no GPU, no Llama.
# Loads the LAST occurrence of each key from the reference .env (it has stale duplicates
# first), strips quotes/whitespace, and does NOT import OPENAI_BASE_URL.
set -uo pipefail
cd "$(dirname "$0")/.."
ENVFILE="${1:-$(cd "$(dirname "$0")/.." && pwd)/.env}"
key() { grep -E "^$1=" "$ENVFILE" | tail -1 | cut -d= -f2- | tr -d '\r"'"'"' '; }
export ANTHROPIC_API_KEY="$(key ANTHROPIC_API_KEY)"
export DEEPSEEK_API_KEY="$(key DEEPSEEK_API_KEY)"
export DASHSCOPE_API_KEY="$(key DASHSCOPE_API_KEY)"
unset OPENAI_BASE_URL OPENAI_JUDGE_BASE_URL || true
PY=./.venv/bin/python

for J in "$@"; do :; done   # no-op to keep $@ usable below
JUDGES=("deepseek" "qwen" "claude")
for J in "${JUDGES[@]}"; do
  echo "[run_api_judges] $J …"
  $PY -m src.pipeline --stage 3 --judge "$J" --repeats 1 --concurrency 4 || \
    echo "[run_api_judges] $J interrupted (resumable)"
  $PY -m src.pipeline --stage 4 --judge "$J" || true
done
echo "[run_api_judges] aggregate…"
$PY -m src.pipeline --stage 5 --judges rulebased gpt4o strongreject deepseek qwen claude || true
echo "API_JUDGES_DONE"
