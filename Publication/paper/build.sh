#!/usr/bin/env bash
# Build the paper PDF. Requires a standard LaTeX install (pdflatex + bibtex).
set -e
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode main.tex
bibtex main || true
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
echo "Built main.pdf"
