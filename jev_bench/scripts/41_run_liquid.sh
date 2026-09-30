#!/usr/bin/env bash
# Hosted D1 evaluation. No GPU or GCP configuration required.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
MODE="${1:-dry-run}"
RUN_ID="${LIQUID_RUN_ID:-liquid-d1}"
CONCURRENCY="${LIQUID_CONCURRENCY:-8}"
if [[ ! "$CONCURRENCY" =~ ^[1-9][0-9]*$ ]]; then
  echo "LIQUID_CONCURRENCY must be a positive integer" >&2
  exit 2
fi
echo "Liquid client concurrency: $CONCURRENCY"
COMMON=(--endpoint liquid --model d1:free --label liquid-d1
  --skip vqa_rad --skip scienceqa_image --concurrency "$CONCURRENCY" --timeout 300)
case "$MODE" in
  dry-run)
    uv run workspace/run_eval.py "${COMMON[@]}" --dry-run
    ;;
  trial)
    # Exercise all three primitives and 77-way choices before a full run.
    uv run workspace/run_eval.py "${COMMON[@]}" --run-id "${RUN_ID}-trial" \
      --only prompt_injections --only banking77 --only sst5 --limit 3
    uv run workspace/score_runs.py --run-id "${RUN_ID}-trial"
    uv run workspace/report.py --run-id "${RUN_ID}-trial"
    ;;
  full)
    uv run workspace/run_eval.py "${COMMON[@]}" --run-id "${RUN_ID}-full"
    uv run workspace/score_runs.py --run-id "${RUN_ID}-full"
    uv run workspace/report.py --run-id "${RUN_ID}-full"
    ;;
  *) echo "usage: bash scripts/41_run_liquid.sh {dry-run|trial|full}" >&2; exit 2 ;;
esac
