#!/usr/bin/env bash
# Hosted decision models through OpenRouter's Decisions API. No GPU, one key.
#
#   bash scripts/43_run_openrouter.sh dry-run cloudflare/clef
#   bash scripts/43_run_openrouter.sh trial   cloudflare/clef      # 9 cases, all three types
#   bash scripts/43_run_openrouter.sh full    cloudflare/clef
#   bash scripts/43_run_openrouter.sh trial   all                  # every model in MODELS below
#
# Needs OPENROUTER_API_KEY in the shell. Model ids come from
#   curl -s 'https://openrouter.ai/api/v1/models?output_modalities=decisions'
# Every row records OpenRouter's billed usage.cost, so report cost from the data,
# not from the price list.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

# Decision models listed on OpenRouter on 2026-10-11 that are not yet benchmarked
# (scaledown/classify-1 added 2026-10-15).
# Left out: typesafe/jev-1.13 and liquid/d1 (already run direct), ~typesafe/jev-latest
# (a moving alias) and the :free variants (rate-limited copies of paid ones).
MODELS=(
  cloudflare/clef
  cloudflare/clef-flash
  cloudflare/clef-omni
  perplexity/pplx-decider-v1.1-27b
  openai/gpt-6-luna-decisions
  microsoft/microsoft-decision-1
  upstage/solar-decide
  upstage/solar-decide-flash
  nace-ai/drex-v1.5
  inception/mercury-decide
  togethercomputer/tev1-4b-experimental
  jaredpalmer/kev-4b
  respan/span-01
  scaledown/classify-1
)

MODE="${1:-}"
TARGET="${2:-}"
CONCURRENCY="${OPENROUTER_CONCURRENCY:-8}"
if [[ -z "$MODE" || -z "$TARGET" ]]; then
  echo "usage: bash scripts/43_run_openrouter.sh {dry-run|trial|full} {<model-id>|all}" >&2
  exit 2
fi
if [[ ! "$CONCURRENCY" =~ ^[1-9][0-9]*$ ]]; then
  echo "OPENROUTER_CONCURRENCY must be a positive integer" >&2
  exit 2
fi
if [[ "$TARGET" == all ]]; then TARGETS=("${MODELS[@]}"); else TARGETS=("$TARGET"); fi

run_one() {
  local model="$1"
  local label="or-${model//\//-}"
  local common=(--endpoint openrouter --model "$model" --label "$label"
    --skip vqa_rad --skip scienceqa_image --concurrency "$CONCURRENCY" --timeout 300)
  # These APIs reject an object state (ScaleDown: "state must be a string or an
  # object with only text, document, and document_mime_type"), so send it as
  # JSON text. Keep in step with state_as_string in models.json.
  case "$model" in
    respan/span-01|scaledown/classify-1) common+=(--state-as-string) ;;
  esac
  echo "== $model  ($label)"
  case "$MODE" in
    dry-run)
      uv run workspace/run_eval.py "${common[@]}" --dry-run
      ;;
    trial)
      # Noul, Score and 77-way Choice, so a wire or parse mismatch shows on 9 requests.
      uv run workspace/run_eval.py "${common[@]}" --run-id "${label}-trial" \
        --only prompt_injections --only banking77 --only sst5 --limit 3
      uv run workspace/score_runs.py --run-id "${label}-trial"
      ;;
    full)
      uv run workspace/run_eval.py "${common[@]}" --run-id "${label}-full"
      uv run workspace/score_runs.py --run-id "${label}-full"
      uv run workspace/report.py --run-id "${label}-full"
      ;;
    *) echo "unknown mode $MODE" >&2; exit 2 ;;
  esac
}

failed=()
for m in "${TARGETS[@]}"; do
  run_one "$m" || failed+=("$m")
done
if (( ${#failed[@]} )); then
  echo; echo "failed or incomplete: ${failed[*]}" >&2
  exit 1
fi
