#!/usr/bin/env bash
# User-invoked only: calls the existing hosted typed-decision endpoints.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
mode="${1:-dry-run}"
provider="${2:-jev}"
case "$mode" in dry-run|trial|full) ;; *) echo "Mode must be dry-run, trial or full" >&2; exit 2;; esac
case "$provider" in
  jev) model=jev-1.13.0 ;;
  liquid) model=d1:free ;;
  *) echo "Provider must be jev or liquid (D1)" >&2; exit 2 ;;
esac
selected=(--only mcpmark_server_routing --only mcpbench_server_routing
          --only mcpmark_tool_selection --only mcpbench_tool_selection)
uv run workspace/verify_cases.py "${selected[@]}"
# Require all four files: the generic runner otherwise accepts a partial match.
for slice in mcpmark_server_routing mcpbench_server_routing mcpmark_tool_selection mcpbench_tool_selection; do
  [[ -s "data/cases/$slice.jsonl" ]] || { echo "Missing $slice; run build_mcp_cases.py" >&2; exit 2; }
done
run_id="${MCP_RUN_ID:-mcp-v1-$provider-$mode}"
args=(--endpoint "$provider" --model "$model" --run-id "$run_id"
      --concurrency "${MCP_CONCURRENCY:-2}" --timeout 300 "${selected[@]}")
case "$mode" in
  dry-run) uv run workspace/run_eval.py "${args[@]}" --dry-run ;;
  trial|full)
    if [[ "$mode" == trial ]]; then args+=(--limit 3); fi
    uv run workspace/run_eval.py "${args[@]}"
    uv run workspace/score_runs.py --run-id "$run_id"
    uv run workspace/report.py --run-id "$run_id"
    ;;
esac
