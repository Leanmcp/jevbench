#!/usr/bin/env bash
# Open-weight Liquid d1 against a server already started on this machine:
#
#   uv run workspace/serve_d1_local.py --model LiquidAI/d1-3B          # shell 1
#   bash scripts/44_run_d1_local.sh trial d1-3B                         # shell 2
#   bash scripts/44_run_d1_local.sh full  d1-3B
#
# The label must match the model the server loaded (d1-3B or d1-omni-600M);
# the server reports its model id and revision on every reply as model_reported.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

MODE="${1:-}"
LABEL="${2:-}"
if [[ -z "$MODE" || ! "$LABEL" =~ ^d1-(3B|omni-600M)$ ]]; then
  echo "usage: bash scripts/44_run_d1_local.sh {dry-run|trial|full} {d1-3B|d1-omni-600M}" >&2
  exit 2
fi
# The server holds one model behind a lock, so more clients only queue.
COMMON=(--endpoint d1local --no-send-model --label "liquid-$LABEL"
  --skip vqa_rad --skip scienceqa_image --concurrency 2 --timeout 600)
case "$MODE" in
  dry-run)
    uv run workspace/run_eval.py "${COMMON[@]}" --dry-run
    ;;
  trial)
    uv run workspace/run_eval.py "${COMMON[@]}" --run-id "liquid-$LABEL-trial" \
      --only prompt_injections --only banking77 --only sst5 --limit 3
    uv run workspace/score_runs.py --run-id "liquid-$LABEL-trial"
    ;;
  full)
    uv run workspace/run_eval.py "${COMMON[@]}" --run-id "liquid-$LABEL-full"
    uv run workspace/score_runs.py --run-id "liquid-$LABEL-full"
    uv run workspace/report.py --run-id "liquid-$LABEL-full"
    ;;
  *) echo "unknown mode $MODE" >&2; exit 2 ;;
esac
