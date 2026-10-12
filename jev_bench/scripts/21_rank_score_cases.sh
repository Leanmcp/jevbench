#!/usr/bin/env bash
# Build and verify the ranking and scoring slices (SciFact, NFCorpus, HelpSteer2,
# RewardBench 2). Downloads pinned files from Hugging Face; calls no model.
#
#   time bash scripts/21_rank_score_cases.sh
#
# Then run them like any other slice: uv run workspace/matrix.py
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

uv run workspace/build_rank_score_cases.py
only=()
while IFS= read -r s; do only+=(--only "$s"); done < <(uv run workspace/build_rank_score_cases.py --list)
uv run workspace/verify_cases.py "${only[@]}"
