#!/usr/bin/env bash
# Finish the throttled strongreject run by routing gpt-4o-mini through OpenRouter
# (same model, higher rate limits). Resumes: the ~1888 verdicts already scored via the
# direct OpenAI key are skipped; only the remaining rows are fetched. Pass --fresh to
# discard the partial file and re-score all 3300 via OpenRouter for single-provider provenance.
set -uo pipefail
cd "$(dirname "$0")/.."
ENVFILE="${1:-$(cd "$(dirname "$0")/.." && pwd)/.env}"
key() { grep -E "^$1=" "$ENVFILE" | tail -1 | cut -d= -f2- | tr -d '\r"'"'"' '; }

OR_KEY="$(key OPENROUTER_API_KEY)"
if [ -z "$OR_KEY" ] || [ "$OR_KEY" = "sk-or-REPLACE_ME" ]; then
  echo "ERROR: set OPENROUTER_API_KEY in $ENVFILE first (https://openrouter.ai/keys)"; exit 1
fi

# route the OpenAI-compatible rubric judge through OpenRouter's gpt-4o-mini
export OPENAI_JUDGE_API_KEY="$OR_KEY"
export OPENAI_JUDGE_BASE_URL="https://openrouter.ai/api/v1"
export OPENAI_JUDGE_MODEL="openai/gpt-4o-mini"
unset OPENAI_BASE_URL || true
PY=./.venv/bin/python

[ "${2:-}" = "--fresh" ] && rm -f Experiment/outputs/judged_strongreject.jsonl && echo "[fresh] cleared partial file"

echo "[strongreject→OpenRouter] probe…"
$PY -c "from src.judges import get_judge; v=get_judge('strongreject').score('x','I cannot help with that.'); print('probe ok, unsafe=',v.unsafe_label)"

echo "[strongreject→OpenRouter] resume run…"
$PY -m src.pipeline --stage 3 --judge strongreject --repeats 1 --concurrency 6
$PY -m src.pipeline --stage 4 --judge strongreject
$PY -m src.pipeline --stage 5 --judges rulebased gpt4o strongreject deepseek qwen claude
echo "STRONGREJECT_DONE"
