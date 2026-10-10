#!/usr/bin/env bash
# Anonymous ACL/ARR review build. Regenerates main.tex from ../arxiv/main.tex with the
# anonymous switches flipped, then compiles. Output: main-anon.pdf
set -e
cd "$(dirname "$0")"
cp ../arxiv/acl.sty ../arxiv/acl_natbib.bst ../arxiv/custom.bib ../arxiv/flip_rates_wide.tex .
sed -e 's/^\\anonymoussubmissionfalse$/\\anonymoussubmissiontrue/' \
    -e 's/^\\preprintversiontrue$/\\preprintversionfalse/' ../arxiv/main.tex > main.tex
for i in 1 2; do pdflatex -interaction=nonstopmode main.tex >/dev/null; bibtex main >/dev/null || true; done
pdflatex -interaction=nonstopmode main.tex >/dev/null; pdflatex -interaction=nonstopmode main.tex | grep "Output written"
cp main.pdf main-anon.pdf && echo "Built main-anon.pdf"
