#!/usr/bin/env bash
# Download source/data only. Does not install or execute upstream code.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
base="$root/data/upstream"
mkdir -p "$base"
fetch() {
  local name="$1" url="$2" revision="$3" dest="$base/$1"
  if [[ ! -d "$dest" ]]; then
    git clone --depth 1 "$url" "$dest"
  fi
  [[ -d "$dest/.git" ]] || { echo "Not a Git checkout: $dest" >&2; exit 1; }
  [[ "$(git -C "$dest" remote get-url origin)" == "$url" ]] || { echo "Unexpected origin: $dest" >&2; exit 1; }
  [[ -z "$(git -C "$dest" status --porcelain)" ]] || { echo "Refusing to change dirty checkout: $dest" >&2; exit 1; }
  if ! git -C "$dest" cat-file -e "$revision^{commit}" 2>/dev/null; then
    git -C "$dest" fetch --depth 1 origin "$revision"
  fi
  git -C "$dest" checkout --detach "$revision"
  [[ "$(git -C "$dest" rev-parse HEAD)" == "$revision" ]]
  echo "$name pinned at $revision"
}
fetch mcpmark https://github.com/eval-sys/mcpmark.git cd45b7f57923b9b3985467f5139927575f83141c
fetch mcpbench https://github.com/Accenture/mcp-bench.git 7a8eaeae83a842a2949080acc5473f65e1569daf
