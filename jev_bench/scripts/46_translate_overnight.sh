#!/usr/bin/env bash
# Overnight translation through Codex: new languages and new slices only.
#
#   time caffeinate -i bash scripts/46_translate_overnight.sh 2>&1 | tee -a data/translations/overnight.log
#
# Never redoes work: translate_cases.py skips every string already answered in
# data/translations/<lang>/translations.jsonl (no --force anywhere here). Safe to
# stop with Ctrl-C and start again; it resumes.
#
# Order, most wanted first, so a short night still delivers the important part:
#   1. Tamil, Kannada, French and Russian on the five safety slices (the six other languages have them).
#   2. Eight languages on the decision slices below.
#   3. One more pass of 1-2, which resends only calls that crashed or timed out.
#   4. Rebuild data/cases_<lang>/ and data/cases_<lang>_full/ for every slice.
# A step that stops (Codex usage limit, network) is retried after a wait.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

SAFETY=(jailbreak_classification prompt_injections aegis2 aegis2_response atbench500)
DECISION=(banking77 mmlu_pro medmcqa scienceqa_text
          mcpbench_server_routing mcpbench_tool_selection mcpmark_server_routing mcpmark_tool_selection)
ALL_LANGS=(hi ta kn zh ar vi sw es fr ru)
NEW_LANGS=(ta kn fr ru)

TRIES="${TRIES:-6}"          # attempts per step
WAIT="${WAIT:-1800}"         # seconds between attempts (Codex limits reset in hours)
FLAGS=(--workers 6 --batch-chars 12000 --batch-max 40)

stamp() { date '+%Y-%m-%d %H:%M:%S'; }

# Two writers on one language's files would race; wait for any earlier run.
while pgrep -f "workspace/translate_cases.py" > /dev/null; do
  echo "$(stamp) another translate_cases.py is running; waiting 5 min"
  sleep 300
done

step() {
  local name="$1"; shift
  local n
  for (( n = 1; n <= TRIES; n++ )); do
    echo; echo "$(stamp) == $name (attempt $n/$TRIES)"
    if uv run workspace/translate_cases.py "${FLAGS[@]}" "$@"; then
      echo "$(stamp) == $name done"
      return 0
    fi
    (( n < TRIES )) && { echo "$(stamp) $name stopped early; retrying in $((WAIT / 60)) min"; sleep "$WAIT"; }
  done
  echo "$(stamp) == $name gave up after $TRIES attempts; later steps still run"
  return 0
}

for pass in 1 2; do
  echo; echo "$(stamp) ######## pass $pass"
  step "safety slices, ta kn fr ru" --langs "${NEW_LANGS[@]}" --slices "${SAFETY[@]}"
  step "decision slices, all languages"   --langs "${ALL_LANGS[@]}" --slices "${DECISION[@]}"
done

echo; echo "$(stamp) == rebuilding case files"
uv run workspace/translate_cases.py --assemble-only --langs "${ALL_LANGS[@]}" \
  --slices "${SAFETY[@]}" "${DECISION[@]}"
echo "$(stamp) == all done"
