#!/usr/bin/env bash
# Generate main.pdf from the LaTeX sources.
#
#   bash genpdf.sh            build, then report what still needs attention
#   bash genpdf.sh --open     build and open the PDF
#   bash genpdf.sh --clean    remove build artifacts, then build
#   bash genpdf.sh --quiet    build only, no report
#
# First run on a fresh clone needs the style file once:
#   bash fetch_template.sh
#
# Sources: main.tex is the spine and \input s every file in sections/ (one per
# paper section) and figures/ (one TikZ file per figure); references.bib is the bibliography;
# arxiv.sty is the vendored preprint style.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

OPEN=0; QUIET=0
for a in "$@"; do
  case "$a" in
    --open)  OPEN=1 ;;
    --quiet) QUIET=1 ;;
    --clean) rm -f main.aux main.log main.out main.bbl main.blg main.toc build*.log bibtex.log ;;
    -h|--help) sed -n '2,16p' "$0"; exit 0 ;;
    *) echo "unknown flag: $a  (try --help)" >&2; exit 2 ;;
  esac
done

[ -f arxiv.sty ] || { echo "arxiv.sty is missing. Run: bash fetch_template.sh" >&2; exit 1; }
for f in main.tex references.bib; do
  [ -f "$f" ] || { echo "$f is missing" >&2; exit 1; }
done

run() {  # run() <logfile> <label>
  if ! pdflatex -interaction=nonstopmode -halt-on-error main.tex > "$1" 2>&1; then
    echo "FAILED on $2. The error and its surrounding lines:" >&2
    grep -n -A4 '^!' "$1" | head -30 >&2
    echo >&2; echo "Full log: latex/$1" >&2
    exit 1
  fi
}

# Two pdflatex passes around a bibtex pass: the first discovers the citations,
# bibtex resolves them, the second and third place them and settle the
# cross-references and table numbering.
run build1.log "pass 1 of 3"
bibtex main > bibtex.log 2>&1 || true   # warns while a citation is unresolved; not fatal
run build2.log "pass 2 of 3"
run build3.log "pass 3 of 3"

pages=$(grep -o 'Output written on main.pdf ([0-9]* pages' build3.log | grep -o '[0-9]*' | head -1)
bytes=$(wc -c < main.pdf | tr -d ' ')
printf 'built main.pdf  %s pages  %s bytes\n' "${pages:-unknown}" "$bytes"

if [ "$QUIET" -eq 0 ]; then
  n_cite=$(grep -c 'LaTeX Warning: Citation'  build3.log || true)
  n_ref=$( grep -c 'LaTeX Warning: Reference' build3.log || true)
  n_over=$(grep -c 'Overfull \\hbox'          build3.log || true)
  n_draft=$(grep -c '\\draftnote{'            main.tex sections/*.tex 2>/dev/null | awk -F: '{s+=$2} END{print s+0}')
  n_bib=$(grep -c '^\\bibitem' main.bbl 2>/dev/null || echo 0)
  n_memory=$(grep -c '^% \[memory\]' references.bib || true)
  echo
  echo "checks"
  printf '  %-26s %s\n' "undefined citations"   "$n_cite"
  printf '  %-26s %s\n' "undefined references"  "$n_ref"
  printf '  %-26s %s\n' "overfull hboxes"       "$n_over"
  printf '  %-26s %s\n' "bibliography entries"  "$n_bib"
  printf '  %-26s %s  %s\n' "unverified citations" "$n_memory" "(tagged [memory] in references.bib)"
  printf '  %-26s %s  %s\n' "draft markers"     "$n_draft" "(must reach 0 before submission)"
  if [ "${n_draft:-0}" -gt 0 ]; then
    echo
    echo "  remaining draft markers:"
    grep -n '\\draftnote{' main.tex sections/*.tex 2>/dev/null | sed 's/\\draftnote{/ -> /' | cut -c1-110 | sed 's/^/    /'
  fi
fi

[ "$OPEN" -eq 1 ] && open main.pdf && echo "opened main.pdf"
exit 0
