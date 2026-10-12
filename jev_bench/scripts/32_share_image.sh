#!/usr/bin/env bash
# Regenerate site/og.png, the preview image iMessage, X, LinkedIn and Slack show
# when someone shares the link. It is a real screenshot of the site's top: the
# title and the start of the Index chart. Rerun after rebuilding site/data.js.
#
#   bash jev_bench/scripts/32_share_image.sh
#
# Captured at 1231x646 so the frame ends in the gap between chart rows, then
# scaled to exactly 1200x630 (1.91:1, what every preview card expects), at 2x
# for sharp phone screens.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --blink-settings=preferredColorScheme=1 --window-size=1231,646 --virtual-time-budget=6000 \
  --screenshot="$TMP/shot.png" "file://$ROOT/site/index.html" 2>/dev/null
sips -z 1260 2400 "$TMP/shot.png" --out "$ROOT/site/og.png" >/dev/null
sips -g pixelWidth -g pixelHeight "$ROOT/site/og.png" | tail -2
