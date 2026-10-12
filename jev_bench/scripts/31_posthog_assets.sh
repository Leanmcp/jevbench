#!/usr/bin/env bash
# Self-host posthog-js for the website under bland file names.
#
#   bash jev_bench/scripts/31_posthog_assets.sh [version]   # default: the pinned version below
#
# Ad blockers match PostHog by file name (array.js, recorder.js,
# dead-clicks-autocapture.js), whatever the host. GitHub Pages cannot rewrite
# paths, so the files are copied into site/_p/ under short neutral names, and
# site/analytics.js maps every /static/<chunk>.js request onto them. All copies
# come from one pinned npm version, so the loader and its chunks always match.
# Upgrading: pass a new version, check it has no advisory, commit site/_p/.
set -Eeuo pipefail
VERSION="${1:-1.438.7}"
OUT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/site/_p"
CDN="https://cdn.jsdelivr.net/npm/posthog-js@${VERSION}/dist"

# Browser chunks posthog-js loads lazily from /static/<name>.js. Module and
# alternative full builds are left out: the page loads array.js only.
CHUNKS=(
  array recorder posthog-recorder lazy-recorder recorder-v2 rrweb rrweb-plugin-console-record
  dead-clicks-autocapture web-vitals web-vitals-with-attribution web-vitals-soft-navs
  exception-autocapture surveys product-tours conversations logs tracing-headers
  element-inference default-extensions extension-bundles external-scripts-loader
  all-external-dependencies customizations
)

rm -rf "$OUT" && mkdir -p "$OUT"
map="{"
for name in "${CHUNKS[@]}"; do
  # Neutral name: first 8 hex of the chunk name's sha1, so no filter word survives.
  short="$(printf '%s' "$name" | shasum | cut -c1-8)"
  curl -fsS "$CDN/$name.js" -o "$OUT/$short.js"
  map+="\"$name\":\"$short\","
done
map="${map%,}}"
printf '{"version":"%s","files":%s}\n' "$VERSION" "$map" > "$OUT/map.json"
# The same map as a script, so site/analytics.js has it before PostHog loads.
printf 'window.__PH_ASSETS = {"version":"%s","files":%s};\n' "$VERSION" "$map" > "$OUT/map.js"
echo "posthog-js $VERSION: ${#CHUNKS[@]} files in site/_p/, map in site/_p/map.json"
