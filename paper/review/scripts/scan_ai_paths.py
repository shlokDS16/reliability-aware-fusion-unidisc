"""List AI model names and repository-file pointers in the prose (comments ignored).

Usage: python scripts/scan_ai_paths.py  (run from paper/review). Exit 1 if anything is found
outside the Declaration on the use of AI.
"""
import re
import sys
from pathlib import Path

PAT = re.compile(
    r"(research|analysis|tools|runs|paper|exp00\d)/[A-Za-z0-9_\-]|\.md\b|\.py\b|\.jsonl?\b"
    r"|Codex|Claude|ChatGPT|OpenAI|Anthropic|gpt-|\bOpus\b|\bSonnet\b|\bFable\b|\bHaiku\b"
)
COMMENT = re.compile(r"(?<!\\)%")
files = [Path("main.tex"), Path("supplement.tex")] + sorted(Path("sections").glob("*.tex")) + sorted(
    Path("tables").glob("*.tex"))
hits = 0
for f in files:
    in_decl = False
    for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if "Declaration on the use of AI" in line:
            in_decl = True
        if in_decl and line.startswith("\\bibliography"):
            in_decl = False
        text = COMMENT.split(line)[0]
        if PAT.search(text) and not in_decl:
            hits += 1
            print(f"{f}:{i}: {text.strip()[:240]}")
print(f"{hits} hits")
sys.exit(1 if hits else 0)
