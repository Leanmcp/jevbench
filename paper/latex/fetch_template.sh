#!/usr/bin/env bash
# Fetch the arXiv preprint LaTeX style and record exactly what was fetched.
#
# Source: https://github.com/kourgeorge/arxiv-style  (arxiv.sty, MIT-licensed,
# derived from the NeurIPS style file). This is a community preprint style, not
# an official arXiv template: arXiv itself imposes no document class. Swap
# arxiv.sty for a venue class (neurips_2026.sty, acl.sty, iclr2026_conference.sty)
# when targeting a specific conference; main.tex needs no other change.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

BASE="https://raw.githubusercontent.com/kourgeorge/arxiv-style/master"
for f in arxiv.sty; do
  echo "fetching $f"
  curl -fsSL --max-time 60 -o "$f" "$BASE/$f"
done
# Upstream's own example, kept for reference only; main.tex does not include it.
curl -fsSL --max-time 60 -o template-upstream.tex.txt "$BASE/template.tex"

{
  echo "# Provenance of vendored LaTeX style"
  echo "fetched_at: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  echo "source: https://github.com/kourgeorge/arxiv-style"
  echo "files:"
  for f in arxiv.sty template-upstream.tex.txt; do
    echo "  - name: $f"
    echo "    bytes: $(wc -c < "$f" | tr -d ' ')"
    echo "    sha256: $(shasum -a 256 "$f" | awk '{print $1}')"
  done
} > TEMPLATE_PROVENANCE.txt

echo "done:"; cat TEMPLATE_PROVENANCE.txt
