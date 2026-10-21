"""Final checks for the revision (2026-10-21): AI model names only in the Declaration, no repository paths,
no hidden Unicode carriers, in the DOCX text and the PDF texts. Run from the repository root."""
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

R = Path("paper/review")
NAMES = re.compile(r"Claude|Codex|ChatGPT|OpenAI|Anthropic|gpt-|\bOpus\b|\bSonnet\b|\bFable\b|\bHaiku\b")
PATHS = re.compile(r"\b(research|analysis|tools|runs)/[A-Za-z0-9_\-]+|\.md\b|\.jsonl\b")
HIDDEN = re.compile("[​-‏‪-‮⁠-⁤﻿\U000e0000-\U000e007f]")


def docx_text(p):
    x = zipfile.ZipFile(p).read("word/document.xml").decode("utf-8")
    return re.sub(r"<[^>]+>", " ", x)


def pdf_text(p):
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ".") / (p.stem + ".txt")
    subprocess.run([shutil.which("pdftotext"), "-enc", "UTF-8", str(p), str(out)], check=True)
    return out.read_text(encoding="utf-8", errors="replace")


bad = 0
for name, text in [("main.docx", docx_text(R / "docx/main.docx")), ("main.pdf", pdf_text(R / "main.pdf")),
                   ("supplement.pdf", pdf_text(R / "supplement.pdf"))]:
    if name == "main.docx":
        text = text.replace("​", "")          # Word equation spacing (OMML), not a hidden carrier
    decl = text.rfind("Declaration on the use of AI")
    end = min([i for i in (text.find("Acknowledg", decl), text.find("References", decl)) if i > 0] or [len(text)])
    for m in NAMES.finditer(text):
        # allowed only inside the Declaration (from its heading to the acknowledgements or references)
        if not (name.startswith("main") and decl >= 0 and decl <= m.start() <= end):
            bad += 1
            print(name, "name:", text[max(0, m.start() - 60):m.end() + 40].replace("\n", " "))
    for m in PATHS.finditer(text):
        bad += 1
        print(name, "path:", text[max(0, m.start() - 60):m.end() + 40].replace("\n", " "))
    h = HIDDEN.findall(text)
    if h:
        bad += 1
        print(name, "hidden unicode:", sorted(set(hex(ord(c)) for c in h)))
for f in list(R.glob("*.tex")) + list((R / "sections").glob("*.tex")) + list((R / "tables").glob("*.tex")) + list(R.glob("*.bib")):
    h = HIDDEN.findall(f.read_text(encoding="utf-8"))
    if h:
        bad += 1
        print(f, "hidden unicode:", sorted(set(hex(ord(c)) for c in h)))
print("problems:", bad)
sys.exit(1 if bad else 0)
