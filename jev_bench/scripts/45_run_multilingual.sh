#!/usr/bin/env bash
# The OpenRouter decision models on the translated safety slices, so they can be
# compared with their English runs (or-*-full). Cases come from translate_cases.py.
#
#   bash scripts/45_run_multilingual.sh trial zh all       # 3 cases per slice, every model
#   bash scripts/45_run_multilingual.sh full  zh all
#   bash scripts/45_run_multilingual.sh full  zh cloudflare/clef
#   VARIANT=state bash scripts/45_run_multilingual.sh full zh all
#
# VARIANT=full (default) reads data/cases_<lang>_full: state and question both
# translated. VARIANT=state reads data/cases_<lang>: state translated, question
# left in English. Run ids are or-<model>-<lang> and or-<model>-<lang>-enq.
# Then: uv run workspace/compare_langs.py
#
# SLICES=safety limits the run to the five safety slices (jailbreak_classification,
# prompt_injections, aegis2, aegis2_response, atbench500); SLICES="a b" to any list.
#
# Needs OPENROUTER_API_KEY in the shell. Re-running resumes; cases already
# answered are not sent again.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

# The 14 models of 43_run_openrouter.sh, each with a full English run. liquid/d1 is
# left out: its OpenRouter English run covers one slice only.
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
LANG_CODE="${2:-}"
TARGET="${3:-}"
VARIANT="${VARIANT:-full}"
CONCURRENCY="${OPENROUTER_CONCURRENCY:-8}"
SLICES="${SLICES:-}"
[[ "$SLICES" == safety ]] && SLICES="jailbreak_classification prompt_injections aegis2 aegis2_response atbench500"
ONLY=()
for s in $SLICES; do ONLY+=(--only "$s"); done
if [[ -z "$MODE" || -z "$LANG_CODE" || -z "$TARGET" ]]; then
  echo "usage: bash scripts/45_run_multilingual.sh {dry-run|trial|full} {zh|ar|hi|vi|sw|es|ta|kn|fr|ru} {<model-id>|all}" >&2
  exit 2
fi
case "$VARIANT" in
  full)  CASES_DIR="data/cases_${LANG_CODE}_full"; SUFFIX="$LANG_CODE" ;;
  state) CASES_DIR="data/cases_${LANG_CODE}";      SUFFIX="${LANG_CODE}-enq" ;;
  *) echo "VARIANT must be full or state" >&2; exit 2 ;;
esac
if ! compgen -G "$CASES_DIR/*.jsonl" > /dev/null; then
  echo "$CASES_DIR has no case files. Build them first:" >&2
  echo "  uv run workspace/translate_cases.py --langs $LANG_CODE --assemble-only" >&2
  exit 2
fi
if [[ "$TARGET" == all ]]; then TARGETS=("${MODELS[@]}"); else TARGETS=("$TARGET"); fi
export JEV_CASES_DIR="$CASES_DIR"

run_one() {
  local model="$1"
  local label="or-${model//\//-}"
  local common=(--endpoint openrouter --model "$model" --label "$label"
    --concurrency "$CONCURRENCY" --timeout 300 ${ONLY[@]+"${ONLY[@]}"})
  # Same string-state rule as 43_run_openrouter.sh.
  case "$model" in
    respan/span-01|scaledown/classify-1) common+=(--state-as-string) ;;
  esac
  echo "== $model  ($label, $CASES_DIR)"
  case "$MODE" in
    dry-run)
      uv run workspace/run_eval.py "${common[@]}" --dry-run
      ;;
    trial)
      uv run workspace/run_eval.py "${common[@]}" --run-id "${label}-${SUFFIX}-trial" --limit 3
      uv run workspace/score_runs.py --run-id "${label}-${SUFFIX}-trial"
      ;;
    full)
      uv run workspace/run_eval.py "${common[@]}" --run-id "${label}-${SUFFIX}"
      uv run workspace/score_runs.py --run-id "${label}-${SUFFIX}"
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
