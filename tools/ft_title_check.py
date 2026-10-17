"""Check that each converted full text (research/sources/md/fulltext-pymupdf/<id>.txt) is the paper it is filed
under: the record title (ft-routes.jsonl, analysis/screening/ft-routes-extra.jsonl) must appear in the first
6,000 characters, either as its first 40 normalised characters or with at least 80 percent of its words of 4+
letters. Flags each failure, and whether the title occurs anywhere in the file (e.g. a proceedings volume or
abstract book that holds the paper), and files above 1,000,000 characters. Titles and text are NFKC-normalised
(ligatures), LaTeX commands and hyphenated line breaks removed. Flags already checked by reading the file are
listed with their note in research/review/fulltext/title-check-verified.json. Writes
research/review/fulltext/title-check.json. Metadata and local files only.

    python tools/ft_title_check.py
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TXT = ROOT / "research/sources/md/fulltext-pymupdf"
LATEX = re.compile(r"\\[a-zA-Z]+")
HYPHEN_BREAK = re.compile(r"(\w)-\s*\n\s*(\w)")


def clean(t):
    t = unicodedata.normalize("NFKC", t or "")          # ligatures such as U+FB00 -> ff
    t = LATEX.sub(" ", t)                                 # LaTeX commands in titles
    return HYPHEN_BREAK.sub(lambda m: m.group(1) + m.group(2), t)


def norm(t):
    return re.sub(r"[^a-z0-9]", "", clean(t).lower())


rows = {}
for table in (ROOT / "research/review/fulltext/ft-routes.jsonl", ROOT / "analysis/screening/ft-routes-extra.jsonl"):
    for line in open(table, encoding="utf-8"):
        if line.strip():
            r = json.loads(line); rows[r["id"]] = r

VER = ROOT / "research/review/fulltext/title-check-verified.json"   # flags checked by reading the file
verified = json.loads(VER.read_text(encoding="utf-8")) if VER.exists() else {}
flags, n = [], 0
for p in sorted(TXT.glob("*.txt")):
    i = p.stem
    if i not in rows:
        flags.append({"id": i, "flag": "no route row"}); continue
    n += 1
    text = p.read_text(encoding="utf-8")
    head, title = norm(text[:6000]), norm(rows[i]["title"])
    words = [w for w in re.findall(r"[a-z0-9]+", clean(rows[i]["title"]).lower()) if len(w) >= 4]
    frac = sum(w in head for w in words) / max(1, len(words))
    big = len(text) > 1_000_000
    if (title[:40] in head or frac >= 0.8) and not big:
        continue
    pos = norm(text).find(title[:40]) if title else -1
    flags.append({"id": i, "title": rows[i]["title"], "chars": len(text), "page1_word_fraction": round(frac, 2),
                  "title_found_later": pos >= 0, "flag": "very large file" if big else "title not on page 1",
                  "verified": verified.get(i)})

out = {"checked": n, "flagged": len(flags), "flagged_not_verified": sum(1 for f in flags if not f.get("verified")),
       "rule": "first 40 normalised title chars or >= 80% of 4+ letter words in the first 6,000 chars; "
               "files > 1,000,000 chars always flagged", "flags": flags}
(ROOT / "research/review/fulltext/title-check.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                                encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k != "flags"}))
for f in flags:
    print(f["id"], f["flag"], f.get("page1_word_fraction"), f.get("title_found_later"), (f.get("title") or "")[:70])
