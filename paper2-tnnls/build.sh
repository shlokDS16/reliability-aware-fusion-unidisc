#!/usr/bin/env bash
# Build paper2-tnnls: main.pdf (+ supplement/supplement.pdf), then the TNNLS checks.
# Usage (Git Bash or PowerShell with bash on PATH):  bash build.sh [--clean]
# Checks: zero undefined references/citations, every font embedded (CIS: "all font embedded"), page count vs the 15-page cap,
# empty column space (scripts/check_column_gaps.py), open \todo count.
set -u
cd "$(dirname "$0")"
if [ "${1:-}" = "--clean" ]; then latexmk -C main.tex >/dev/null 2>&1; latexmk -C -cd supplement/supplement.tex >/dev/null 2>&1; fi
status=0
latexmk -pdf -interaction=nonstopmode main.tex >build.log 2>&1 || { echo "main: latexmk FAILED, see build.log"; tail -n 25 build.log; exit 1; }
latexmk -pdf -interaction=nonstopmode -cd supplement/supplement.tex >supplement/build.log 2>&1 || { echo "supplement: latexmk FAILED"; tail -n 25 supplement/build.log; status=1; }

echo "== undefined references/citations, overfull boxes > 2pt"
grep -h -E "Reference .* undefined|Citation .* undefined|There were undefined|Label\(s\) may have changed" main.log supplement/supplement.log | sort | uniq -c
grep -h -E "Overfull \\\\[hv]box \(([2-9]|[1-9][0-9]+)\.[0-9]+pt" main.log supplement/supplement.log | head -20
echo "== fonts (every row must say emb yes)"
pdffonts main.pdf | awk 'NR>2 && $(NF-4)!="yes" {print "NOT EMBEDDED: " $0; bad=1} END{ if(!bad) print "all embedded" }'
pages=$(pdfinfo main.pdf | awk '/^Pages:/{print $2}')
echo "== pages: $pages (Full Paper: 10 free, hard cap 15 incl. references; placeholder build lists the whole reference file)"
echo "== column gaps"
python -E scripts/check_column_gaps.py main.pdf || status=1
echo "== open \\todo items in sources: $(cat sections/*.tex back/*.tex main.tex | grep -o '\\todo{' | wc -l)"
exit $status
