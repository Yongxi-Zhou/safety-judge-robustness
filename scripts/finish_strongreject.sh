#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/.."
ENVFILE="${1:-$(cd "$(dirname "$0")/.." && pwd)/.env}"
export OPENAI_API_KEY="$(grep -E '^OPENAI_API_KEY=' "$ENVFILE" | head -1 | cut -d= -f2-)"
unset OPENAI_BASE_URL OPENAI_JUDGE_BASE_URL || true
# loop: resume until complete (each resume skips done work); gentle concurrency
for i in $(seq 1 40); do
  n=$(wc -l < Experiment/outputs/judged_strongreject.jsonl)
  [ "$n" -ge 3300 ] && { echo "complete: $n"; break; }
  ./.venv/bin/python -m src.pipeline --stage 3 --judge strongreject --repeats 1 --concurrency 2 || true
done
./.venv/bin/python -m src.pipeline --stage 4 --judge strongreject || true
./.venv/bin/python -m src.pipeline --stage 5 --judges rulebased gpt4o strongreject || true
echo "STRONGREJECT_DONE"
