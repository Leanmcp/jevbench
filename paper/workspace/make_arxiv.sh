#!/usr/bin/env bash
# Build the paper and package its source for arXiv.
#
#   time bash paper/workspace/make_arxiv.sh          # tar.gz (what arXiv expects)
#   time bash paper/workspace/make_arxiv.sh --zip    # also write a .zip
#
# Writes to paper/dist/:
#   jevbench-arxiv-<date>.tar.gz   upload this to arXiv
#   jevbench-arxiv-<date>.zip      same files, only with --zip
#   jevbench-<date>.pdf            the locally built PDF, for your records
#
# arXiv compiles the source itself and does not run BibTeX, so the bundle carries
# the generated main.bbl. The PDF is kept out of the bundle, because arXiv builds
# its own. Before packaging, the bundle is compiled on its own in a clean folder,
# so a missing file fails here instead of at arXiv.
set -Eeuo pipefail

ZIP=0
for a in "$@"; do
  case "$a" in
    --zip) ZIP=1 ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown flag: $a  (try --help)" >&2; exit 2 ;;
  esac
done

PAPER="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LATEX="$PAPER/latex"
DIST="$PAPER/dist"
STAMP="$(date +%Y%m%d)"
NAME="jevbench-arxiv-$STAMP"

say() { printf '\n[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }

# 1. Fresh build, which also regenerates main.bbl from references.bib.
say "building the paper"
bash "$LATEX/genpdf.sh" --clean --quiet
for f in main.pdf main.bbl; do
  [ -s "$LATEX/$f" ] || { echo "build did not produce $f" >&2; exit 1; }
done
if grep -q 'LaTeX Warning: .*undefined' "$LATEX/build3.log"; then
  echo "undefined references or citations remain; see $LATEX/build3.log" >&2
  exit 1
fi
if grep -rq '\\draftnote{' "$LATEX/sections"; then
  echo "draft notes remain in sections/; remove them before submitting" >&2
  exit 1
fi

# 2. Stage exactly the files the source needs.
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
say "staging source in $STAGE"
cp "$LATEX/main.tex" "$LATEX/main.bbl" "$LATEX/arxiv.sty" "$STAGE/"
mkdir -p "$STAGE/sections" "$STAGE/figures"
cp "$LATEX"/sections/*.tex "$STAGE/sections/"
cp "$LATEX"/figures/*.tex "$STAGE/figures/"

# 3. Compile the staged copy without BibTeX, as arXiv does.
say "test-compiling the staged source"
TEST="$(mktemp -d)"
trap 'rm -rf "$STAGE" "$TEST"' EXIT
cp -R "$STAGE"/. "$TEST/"
( cd "$TEST"
  for pass in 1 2 3; do
    if ! pdflatex -interaction=nonstopmode -halt-on-error main.tex > "build$pass.log" 2>&1; then
      echo "staged source failed to compile (pass $pass):" >&2
      grep -n -A4 '^!' "build$pass.log" | head -30 >&2
      exit 1
    fi
  done
  if grep -q 'LaTeX Warning: .*undefined' build3.log; then
    echo "staged source has undefined references; a file is missing from the bundle" >&2
    exit 1
  fi
)

# 4. Package.
mkdir -p "$DIST"
tar -czf "$DIST/$NAME.tar.gz" -C "$STAGE" .
if [ "$ZIP" -eq 1 ]; then
  rm -f "$DIST/$NAME.zip"
  ( cd "$STAGE" && zip -qr "$DIST/$NAME.zip" . )
fi
cp "$LATEX/main.pdf" "$DIST/jevbench-$STAMP.pdf"

say "done"
echo "  arXiv source : $DIST/$NAME.tar.gz ($(du -h "$DIST/$NAME.tar.gz" | cut -f1))"
[ "$ZIP" -eq 1 ] && echo "  zip          : $DIST/$NAME.zip"
echo "  local PDF    : $DIST/jevbench-$STAMP.pdf"
echo
echo "Bundle contents:"
tar -tzf "$DIST/$NAME.tar.gz" | sed 's/^/  /'
