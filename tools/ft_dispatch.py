"""Build an isolated dispatch folder for one full-text screening session (criteria v1.6, D0032).

    python tools/ft_dispatch.py --role A|B|C --batch <name> --ids <file with one id per line> --root <scratch dir> [--rows <jsonl of A/B rows, role C>]

Creates <root>/<role>-<batch>-<uuid4>/ (basename never reused) holding only CONTRACT.md,
criteria-v1.6-screener.md, fulltext/<id>.txt for each id (from research/sources/md/fulltext-pymupdf),
dispatch.json (ids in a seeded shuffle, output file name, full-text version string, possible duplicates)
and, for role C, the two screener rows per record. Nothing says why a record is in the batch.
Appends a line to research/review/fulltext/dispatch-log.jsonl (basename, role, batch, ids sha256, files sha256).
"""
import argparse, hashlib, json, random, shutil, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "research/sources/md/fulltext-pymupdf"   # PyMuPDF text with === page N === markers (tools/pdf_to_text.py)
LOG = ROOT / "research/review/fulltext/dispatch-log.jsonl"
MODEL = {"A": "claude-sonnet-5-5", "B": "claude-opus-5-5", "C": "claude-fable-5-1"}
sha = lambda b: hashlib.sha256(b).hexdigest()

ap = argparse.ArgumentParser()
ap.add_argument("--role", required=True, choices="ABC")
ap.add_argument("--batch", required=True)
ap.add_argument("--ids", required=True)
ap.add_argument("--root", required=True)
ap.add_argument("--rows")
ap.add_argument("--dups", help="json {id: other_id} of possible duplicates within the batch")
a = ap.parse_args()
ids = [l.strip() for l in open(a.ids, encoding="utf8") if l.strip()]
missing = [i for i in ids if not (MD / f"{i}.txt").exists()]
if missing:
    raise SystemExit(f"no full text for {len(missing)} ids: {missing[:10]}")
random.Random(f"{a.batch}-{a.role}").shuffle(ids)
name = f"{a.role}-{a.batch}-{uuid.uuid4()}"
d = Path(a.root) / name
(d / "fulltext").mkdir(parents=True)
shutil.copy(ROOT / "research/CONTRACT.md", d / "CONTRACT.md")
shutil.copy(ROOT / "research/review/screening/criteria-v1.6-screener.md", d / "criteria-v1.6-screener.md")
files = {}
for i in ids:
    b = (MD / f"{i}.txt").read_bytes()
    (d / "fulltext" / f"{i}.txt").write_bytes(b)
    files[i] = sha(b)
out = f"F{a.role}-{a.batch}.jsonl"
disp = {"role": a.role, "model": MODEL[a.role], "batch": a.batch, "ids": ids, "output_file": out,
        "ft": "pymupdf-1.27.2.3 text of the open-access PDF, page markers '=== page N ===' (research/review/fulltext/fetch-log.jsonl)",
        "possible_duplicates": json.load(open(a.dups, encoding="utf8")) if a.dups else {}}
if a.role == "C":
    rows = [json.loads(l) for l in open(a.rows, encoding="utf8") if l.strip()]
    (d / "screener-rows.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows if r["id"] in set(ids)), encoding="utf8")
(d / "dispatch.json").write_text(json.dumps(disp, indent=1), encoding="utf8")
with LOG.open("a", encoding="utf8") as fh:
    fh.write(json.dumps({"basename": name, "role": a.role, "model": MODEL[a.role], "batch": a.batch, "n": len(ids),
                         "ids_sha256": sha("\n".join(sorted(ids)).encode()), "files_sha256": sha(json.dumps(files, sort_keys=True).encode())}) + "\n")
print(d)
