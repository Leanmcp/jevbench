#!/usr/bin/env bash
# Build the paper. Run fetch_template.sh first, once.
#
#   bash build.sh          # build main.pdf
#   bash build.sh clean    # remove build artifacts
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

if [ "${1:-}" = "clean" ]; then
  rm -f main.aux main.log main.out main.bbl main.blg main.pdf main.toc build*.log bibtex.log
  echo "cleaned"; exit 0
fi

[ -f arxiv.sty ] || { echo "arxiv.sty missing. Run: bash fetch_template.sh" >&2; exit 1; }

# Two pdflatex passes for cross-references, with a bibtex pass between them.
# bibtex warns while references.bib is still empty; that is not a build failure.
pdflatex -interaction=nonstopmode -halt-on-error main.tex > build1.log 2>&1 || {
  echo "FAILED on pass 1. Last 40 lines:" >&2; tail -40 build1.log >&2; exit 1; }
bibtex main > bibtex.log 2>&1 || true
pdflatex -interaction=nonstopmode -halt-on-error main.tex > build2.log 2>&1 || {
  echo "FAILED on pass 2. Last 40 lines:" >&2; tail -40 build2.log >&2; exit 1; }
pdflatex -interaction=nonstopmode -halt-on-error main.tex > build3.log 2>&1 || true

pages=$(grep -o 'Output written on main.pdf ([0-9]* pages' build3.log | grep -o '[0-9]*' | head -1)
bytes=$(wc -c < main.pdf | tr -d ' ')
echo "built main.pdf (${pages:-unknown} pages, ${bytes} bytes)"

echo
echo "checks:"
n_cite=$(grep -c 'LaTeX Warning: Citation' build3.log || true)
n_ref=$(grep -c 'LaTeX Warning: Reference' build3.log || true)
n_over=$(grep -c 'Overfull \\hbox' build3.log || true)
n_draft=$(grep -c 'draftnote' main.tex || true)
echo "  undefined citations : ${n_cite}"
echo "  undefined refs      : ${n_ref}"
echo "  overfull hboxes     : ${n_over}"
echo "  draftnote markers   : ${n_draft}  (must be 0 before submission)"
