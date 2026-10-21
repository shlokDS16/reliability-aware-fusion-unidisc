"""Build the local release folder for Paper 1 (research/RELEASE-GUIDE-paper1.md). Nothing is uploaded.

    python -I tools/build_release_paper1.py <out_dir>

Copies an allow-list of paths from this worktree into <out_dir> (which must not exist): code (tools/, tests/,
analysis/), the manuscript sources and PDFs (paper/review/), the protocol, criteria, extraction form, codebooks,
audits and ledgers (research/review/ without full texts, research/ledgers/, research/preregistration/), the EXP-003
analysis outputs, and CONTRACT.md. Left out: every full text and PDF from the literature (research/sources/), the
census HTML texts, raw database exports, generated images, private notes (research/*.md pages written for the
authors), the blind human-check model answers until the check is done, and caches.
Bibliographic records (research/review/corpus/*.jsonl, research/review/screening/**.jsonl) keep ids, titles, authors,
years, venues, identifiers and decisions; their "abstract" fields are removed (database licence terms).
Writes MANIFEST.sha256 (one line per file) and a secret scan report SECRET-SCAN.txt; exits 1 if the scan finds a hit.
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]).resolve()
INCLUDE = ["tools", "tests", "analysis", "paper/review", "research/review", "research/ledgers",
           "research/preregistration", "research/CONTRACT.md", "runs/EXP-003/analysis",
           "runs/EXP-003/ctrl/controls_decision.json"]
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", "fulltext-pymupdf", "census-text-paged", "pdfs", "html", "search-raw",
                "gen", "images", "img", ".venv", "node_modules"}
EXCLUDE_FILES = {"human-check-model-answers.json", "main-flat.tex", "main-pandoc.docx"}   # + docx build intermediates
EXCLUDE_SUFFIX = {".pdf.part", ".pyc", ".aux", ".log", ".fls", ".fdb_latexmk", ".out", ".blg", ".synctex.gz", ".png.tmp"}
KEEP_PDF = {"paper/review/main.pdf", "paper/review/supplement.pdf"}
STRIP_ABSTRACT = re.compile(r"^research/review/(corpus|screening)/.*\.jsonl$")
SECRET = re.compile(r"(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|api[_-]?key\s*[:=]\s*['\"][^'\"]{12,}|"
                    r"Bearer\s+[A-Za-z0-9._-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.I)


def wanted(rel):
    parts = set(Path(rel).parts)
    if parts & EXCLUDE_DIRS or Path(rel).name in EXCLUDE_FILES:
        return False
    if any(rel.endswith(s) for s in EXCLUDE_SUFFIX):
        return False
    if rel.lower().endswith(".pdf") and rel not in KEEP_PDF:
        return False
    if rel.startswith("research/review/fulltext/") and not rel.endswith((".jsonl", ".md", ".json", ".py")):
        return False
    return True


def main():
    assert not OUT.exists(), f"{OUT} exists; choose a new folder"
    files = []
    for inc in INCLUDE:
        src = ROOT / inc
        if src.is_file():
            files.append(src)
        elif src.is_dir():
            files += [p for p in src.rglob("*") if p.is_file()]
    n_strip = 0
    man, hits = [], []
    for src in sorted(set(files)):
        rel = src.relative_to(ROOT).as_posix()
        if not wanted(rel):
            continue
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if STRIP_ABSTRACT.match(rel):
            out_lines = []
            for line in src.read_text(encoding="utf-8", errors="replace").splitlines():
                try:
                    r = json.loads(line)
                except ValueError:
                    out_lines.append(line)
                    continue
                if isinstance(r, dict) and "abstract" in r:
                    r.pop("abstract")
                    n_strip += 1
                out_lines.append(json.dumps(r, ensure_ascii=False))
            dst.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
        else:
            shutil.copy2(src, dst)
        b = dst.read_bytes()
        man.append(f"{hashlib.sha256(b).hexdigest()}  {rel}")
        if dst.suffix in (".py", ".md", ".json", ".jsonl", ".txt", ".tex", ".toml", ".yaml", ".yml", ".cfg", ".ini", ".sh", ".bat"):
            for m in SECRET.finditer(b.decode("utf-8", errors="replace")):
                hits.append(f"{rel}: {m.group(0)[:12]}...")
    for name in ("README.md", "LICENSE", "LICENSE-DATA"):          # release root files (templates)
        shutil.copy2(ROOT / "paper/review/release" / name, OUT / name)
        man.append(f"{hashlib.sha256((OUT / name).read_bytes()).hexdigest()}  {name}")
    (OUT / "MANIFEST.sha256").write_text("\n".join(man) + "\n", encoding="utf-8")
    (OUT / "SECRET-SCAN.txt").write_text(("\n".join(hits) or "no hits") + "\n", encoding="utf-8")
    size = sum((OUT / l.split("  ", 1)[1]).stat().st_size for l in man)
    print(f"{len(man)} files, {size / 1e6:.1f} MB, abstracts stripped from {n_strip} records, secret hits {len(hits)}")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
