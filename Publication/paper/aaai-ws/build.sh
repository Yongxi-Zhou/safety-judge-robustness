#!/usr/bin/env bash
# AAAI-27 workshop builds. main-anon.pdf = [submission] (double-blind workshops, e.g. DAI);
# main-authors.pdf = author version (single-blind workshops, e.g. SPF-LLM, AICS).
set -e
cd "$(dirname "$0")"
cp ../custom.bib ../flip_rates_wide.tex ../baseline_accuracy.tex .
build () {  # $1 = output name, $2 = sty option
  sed -e "s/^\\\\usepackage\[submission\]{aaai2027}/\\\\usepackage$2{aaai2027}/" main.tex > _b.tex
  for i in 1 2; do pdflatex -interaction=nonstopmode _b.tex >/dev/null || true; bibtex _b >/dev/null || true; done
  pdflatex -interaction=nonstopmode _b.tex >/dev/null || true
  pdflatex -interaction=nonstopmode _b.tex | grep "Output written"
  cp _b.pdf "$1"; cp _b.log "${1%.pdf}.log"
}
build main-anon.pdf "[submission]"
build main-authors.pdf ""
rm -f _b.aux _b.bbl _b.blg _b.out _b.pdf _b.log _b.tex
echo "Built main-anon.pdf and main-authors.pdf"
