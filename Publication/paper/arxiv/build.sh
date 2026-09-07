#!/usr/bin/env bash
# Build the arXiv preprint PDF from this self-contained directory.
set -e
cd "$(dirname "$0")"
pdflatex -interaction=nonstopmode main.tex > /dev/null || true
bibtex main > /dev/null || true
pdflatex -interaction=nonstopmode main.tex > /dev/null || true
pdflatex -interaction=nonstopmode main.tex
echo "Built arxiv/main.pdf"
