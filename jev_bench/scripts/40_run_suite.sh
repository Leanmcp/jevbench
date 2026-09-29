#!/usr/bin/env bash
# Run the benchmark against one model. Resumable, so re-running continues.
#
#   bash 40_run_suite.sh clm                 # full text suite on CLM
#   bash 40_run_suite.sh clm trial           # 20-case parse check first
#   bash 40_run_suite.sh djev
#   bash 40_run_suite.sh jev
#
# Always run the trial before the full suite: it catches a wire-schema or auth
# mismatch for 20 requests instead of 8,016.
set -Eeuo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/00_config.sh"
cd "$BENCH_DIR"

TARGET="${1:-}"
MODE="${2:-full}"
CONCURRENCY="${3:-16}"   # client-side parallel requests; encoder allows max-num-seqs 32

case "$TARGET" in
  clm)
    ENDPOINT="http://127.0.0.1:${CLM_LOCAL_PORT}/v1/systemone"
    LABEL="clm-v0.1-8B"
    # clm-serve only enforces auth when CLM_API_KEY is set, but our client sends a
    # bearer header whenever TYPESAFE_API_KEY exists. Unset it for this run so a
    # stray 401 is impossible and no key is sent to a non-vendor endpoint.
    unset TYPESAFE_API_KEY
    EXTRA=(--no-send-model --seed 0 --samples 1)
    ;;
  djev)
    ENDPOINT="http://127.0.0.1:${LOCAL_PORT}/v1/request"
    LABEL="djev-0.1"
    EXTRA=(--no-send-model --seed 0 --samples 1)
    ;;
  jev)
    ENDPOINT="https://api.typesafe.ai/v1/systemone"
    LABEL="jev-1.13.0"
    EXTRA=(--model jev-1.13.0)
    ;;
  *)
    echo "usage: bash 40_run_suite.sh {clm|djev|jev} [trial|full]" >&2; exit 2 ;;
esac

say "target $TARGET  endpoint $ENDPOINT  mode $MODE"
if ! curl -fsS --max-time 8 "${ENDPOINT%/v1/*}/health" >/dev/null 2>&1; then
  say "note: /health did not answer. For the hosted API that is expected."
fi

if [ "$MODE" = "trial" ]; then
  say "20-case trial on the smallest slice"
  time uv run workspace/run_eval.py --endpoint "$ENDPOINT" --label "$LABEL" "${EXTRA[@]}" \
    --run-id "${LABEL}-trial" --only prompt_injections --limit 20 --concurrency 1 --timeout 300
  say "inspect the parsed fields before the full run:"
  uv run python - <<'PY'
import json, sys, pathlib
sys.path.insert(0, "workspace")
import common as C
runs = sorted(C.RUNS.glob("*-trial"), key=lambda p: p.stat().st_mtime)
recs = C.read_jsonl(runs[-1] / "predictions.jsonl")
ok = [r for r in recs if not r.get("error") and not r.get("parse_error")]
print(f"{runs[-1].name}: {len(ok)}/{len(recs)} parsed")
for r in recs[:3]:
    print({k: r.get(k) for k in ("case_id","pred","p_true","confidence","input_tokens","error","parse_error")})
PY
  say "if that looks right: bash 40_run_suite.sh $TARGET full"
  exit 0
fi

say "full text suite, 8,016 cases"
time uv run workspace/run_eval.py --endpoint "$ENDPOINT" --label "$LABEL" "${EXTRA[@]}" \
  --run-id "${LABEL}-full" --concurrency "$CONCURRENCY" --timeout 300

say "scoring"
uv run workspace/score_runs.py --run-id "${LABEL}-full"
uv run workspace/report.py --run-id "${LABEL}-full"
say "done. report in reports/RESULTS_${LABEL}-full.md"
