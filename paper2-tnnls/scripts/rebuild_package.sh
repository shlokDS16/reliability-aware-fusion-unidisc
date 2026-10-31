#!/usr/bin/env bash
# One-command rebuild of every Paper 2 submission file after a text edit (for example the AI sentence in main.tex, Acknowledgment).
#   bash paper2-tnnls/scripts/rebuild_package.sh
# Builds: review and author PDFs, supplement PDF, cover letter, review and author Word files (rendered through Word for a check),
# then copies them into paper2-tnnls/docx/ and paper2-tnnls/SUBMISSION-PACKAGE/ and scans the review copies for author identifiers.
# Stops at the first failure. Takes about 20-25 minutes (the Word renders are the slow part). Nothing is committed or pushed.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"          # paper2-tnnls
PY="C:/Users/Shlok/Downloads/Multi-Modality Language model/.venv/Scripts/python.exe"
[ -n "$HERE" ] && [ -f "$HERE/main.tex" ] || { echo "STOP: paper2-tnnls not found"; exit 1; }
PKG="$HERE/SUBMISSION-PACKAGE"
TMP="$(mktemp -d)"
[ -n "$TMP" ] && [ -d "$TMP" ] || { echo "STOP: no temp dir"; exit 1; }
cd "$HERE"

echo "== 1/5 PDFs (review, author, supplement)"
"$PY" -I scripts/prepare_bib.py | tail -1
bash build.sh | tee "$TMP/build.txt" | grep -E "pages|undefined|FAILED" || true
if grep -q "LaTeX Warning: .*undefined\|There were undefined\|FAILED" "$TMP/build.txt"; then echo "STOP: undefined reference or failed build (see build.log)"; exit 1; fi
PM=$(pdfinfo main.pdf | awk '/^Pages:/{print $2}')
[ "$PM" -le 15 ] || { echo "STOP: main.pdf has $PM pages (cap 15)"; exit 1; }

echo "== 2/5 cover letter"
(cd "$PKG/source" && latexmk -pdf -interaction=nonstopmode cover_letter.tex >/dev/null 2>&1)

echo "== 3/5 Word files (review, then author)"
python scripts/make_docx.py --render --out "$TMP/anon" > "$TMP/anon.log" 2>&1 || { echo "STOP: review Word build failed ($TMP/anon.log)"; exit 1; }
python scripts/make_docx.py --camera --main-only --render --out "$TMP/cam" > "$TMP/cam.log" 2>&1 || { echo "STOP: author Word build failed ($TMP/cam.log)"; exit 1; }
grep "pages:" "$TMP/anon.log" "$TMP/cam.log" || true

echo "== 4/5 copy into docx/ and SUBMISSION-PACKAGE/"
cp "$TMP"/anon/Paper2_TNNLS_manuscript.docx "$TMP"/anon/Paper2_TNNLS_manuscript.word.pdf "$TMP"/anon/Paper2_TNNLS_supplement.docx \
   "$TMP"/anon/Paper2_TNNLS_supplement.word.pdf "$TMP"/anon/verify_manuscript.txt "$TMP"/anon/verify_supplement.txt docx/
cp "$TMP"/cam/Paper2_TNNLS_manuscript_authors.docx "$TMP"/cam/Paper2_TNNLS_manuscript_authors.word.pdf "$TMP"/cam/verify_manuscript_authors.txt docx/
cp main.pdf "$PKG/01_Manuscript_anonymous.pdf"
cp supplement/supplement.pdf "$PKG/02_Supplementary_Material_anonymous.pdf"
cp "$PKG/source/cover_letter.pdf" "$PKG/03_Cover_Letter.pdf"
cp main_camera.pdf "$PKG/at-acceptance/Manuscript_author_version.pdf"
cp docx/Paper2_TNNLS_manuscript_authors.docx "$PKG/at-acceptance/Manuscript_author_version.docx"
cp docx/Paper2_TNNLS_manuscript.docx "$PKG/optional/Manuscript_anonymous.docx"
cp docx/Paper2_TNNLS_supplement.docx "$PKG/optional/Supplementary_Material_anonymous.docx"

echo "== 5/5 identifier scan of the review copies (must be 0 each; the generic 'DOI withheld' sentence is allowed)"
"$PY" - "$PKG" <<'EOF'
import re, subprocess, sys, zipfile
from pathlib import Path
pkg = Path(sys.argv[1])
pat = re.compile(r"(?i)shlok|goenka|vairavasundaram|subramaniyaswamy|balaji|vellore|vit\.ac\.in|zenodo\.2\d{7}|github\.com/shlok")
bad = 0
for f in ("01_Manuscript_anonymous.pdf", "02_Supplementary_Material_anonymous.pdf"):
    t = subprocess.run(["pdftotext", str(pkg / f), "-"], capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout
    n = len(pat.findall(t)); bad += n; print(f, n)
for f in ("optional/Manuscript_anonymous.docx", "optional/Supplementary_Material_anonymous.docx"):
    z = zipfile.ZipFile(pkg / f)
    t = " ".join(z.read(m).decode("utf-8", "ignore") for m in z.namelist() if m.endswith(".xml"))
    n = len(pat.findall(t)); bad += n; print(f, n)
sys.exit(1 if bad else 0)
EOF
echo "== done: main $PM pages; check SUBMIT-HERE.md if the page count changed. Then commit and push."
