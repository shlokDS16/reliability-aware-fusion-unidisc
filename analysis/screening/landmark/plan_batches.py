"""Title check and batch plan for the landmark tranche L (D0061; tranche code 'lmk').

Title check: the rule of tools/ft_title_check.py (first 40 normalised title characters, or at least 80 percent of
the title's 4+ letter words, in the first 6,000 characters; files above 1,000,000 characters flagged), applied to
the 44 tranche texts only, so the shared research/review/fulltext/title-check.json is not rewritten. Titles come
from landmark-routes.jsonl (corpus titles). Writes analysis/screening/landmark/title-check.json.

Plan: as tools/ft_plan_tranche.py: ids that passed the title check, shuffled with random.Random(seed), cut into
batches of 10; biology-heavy records (same BIO pattern) in batches of 3; chunk order shuffled with seed + 1.
Writes research/review/fulltext/lmk-batches-part1.json and tools/ft-session/lmkb<NNN>.ids (copied to
FT_DISPATCH_ROOT if set). Plans are never rewritten.

    python -I analysis/screening/landmark/plan_batches.py 20261022
"""
import json
import os
import random
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TXT = ROOT / "research/sources/md/fulltext-pymupdf"
FT = ROOT / "research/review/fulltext"
LATEX = re.compile(r"\\[a-zA-Z]+")
HYPHEN_BREAK = re.compile(r"(\w)-\s*\n\s*(\w)")
BIO = re.compile(r"\b(protein|peptide|antibod\w*|enzyme|m?RNA|ncRNA|DNA|genom\w*|nucleotide|amino[- ]acid|"
                 r"molecul\w*|drug|ligand|biolog\w*|cell(?:s|ular)?|gene|virus|viral|pathogen|toxin)\b", re.I)


def clean(t):
    t = unicodedata.normalize("NFKC", t or "")
    t = LATEX.sub(" ", t)
    return HYPHEN_BREAK.sub(lambda m: m.group(1) + m.group(2), t)


def norm(t):
    return re.sub(r"[^a-z0-9]", "", clean(t).lower())


seed = int(sys.argv[1])
out = FT / "lmk-batches-part1.json"
if out.exists():
    sys.exit(f"{out.name} exists; plans are never rewritten")
routes = [json.loads(l) for l in open(HERE / "landmark-routes.jsonl", encoding="utf-8") if l.strip()]
titles = {r["id"]: r["title"] for r in routes}
flags, ok = [], []
for i, title in titles.items():
    text = (TXT / f"{i}.txt").read_text(encoding="utf-8")
    head, t = norm(text[:6000]), norm(title)
    words = [w for w in re.findall(r"[a-z0-9]+", clean(title).lower()) if len(w) >= 4]
    frac = sum(w in head for w in words) / max(1, len(words))
    big = len(text) > 1_000_000
    if (t[:40] in head or frac >= 0.8) and not big:
        ok.append(i)
    else:
        flags.append({"id": i, "title": title, "chars": len(text), "page1_word_fraction": round(frac, 2),
                      "flag": "very large file" if big else "title not on page 1"})
(HERE / "title-check.json").write_text(json.dumps({"checked": len(titles), "flagged": len(flags), "flags": flags},
                                                  indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
if flags:
    print(json.dumps(flags, indent=1))
    sys.exit("title-check flags: read the files, then plan")
ready = sorted(ok)
bio = {i for i in ready if BIO.search(titles[i] + " " + (TXT / f"{i}.txt").read_text(encoding="utf-8")[:3000])}
random.Random(seed).shuffle(ready)
norm_ids, bio_ids = [i for i in ready if i not in bio], [i for i in ready if i in bio]
chunks = [norm_ids[k:k + 10] for k in range(0, len(norm_ids), 10)] + [bio_ids[k:k + 3] for k in range(0, len(bio_ids), 3)]
random.Random(seed + 1).shuffle(chunks)
batches = {f"lmkb{k + 1:03d}": c for k, c in enumerate(chunks)}
plan = {"tranche": "LMK", "decision": "D0061", "part": 1, "seed": seed, "size": 10, "bio_size": 3, "n": len(ready),
        "bio_batches": sorted(b for b, c in batches.items() if c and c[0] in bio), "batches": batches}
out.write_text(json.dumps(plan, indent=1) + "\n", encoding="utf-8")
droot = os.environ.get("FT_DISPATCH_ROOT")
for b, c in batches.items():
    (ROOT / f"tools/ft-session/{b}.ids").write_text("\n".join(c) + "\n", encoding="utf-8")
    if droot:
        Path(droot).mkdir(parents=True, exist_ok=True)
        (Path(droot) / f"{b}.ids").write_text("\n".join(c) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in plan.items() if k != "batches"}), {b: len(c) for b, c in batches.items()})
