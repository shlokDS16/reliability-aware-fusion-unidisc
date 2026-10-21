"""Build the landmark tranche L (decision D0061).

Frame: the 47 models of research/review/coverage/design-space-v1.csv. A model is
"covered" if any corpus record with its arXiv id is among the 615 included
studies (analysis/rq1/rq1-includes.jsonl). Every other model forms tranche L.
For each model the script records which record ids carry the arXiv id and how
each was handled before the D0051 freeze (T1, R797, S1243 or none).

Run: python -I analysis/screening/landmark/build_tranche.py
Writes analysis/screening/landmark/landmark-frame.jsonl (47 rows),
landmark-tranche-ids.txt (one record id per tranche paper) and
landmark-frame-summary.json.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def norm(a):
    if not a:
        return None
    a = str(a).strip()
    a = re.sub(r"^(arxiv:|https?://arxiv\.org/(abs|pdf)/)", "", a, flags=re.I)
    a = re.sub(r"v\d+$", "", a)
    a = a.replace(".pdf", "")
    return a or None


def jl(p):
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


ids_by_arxiv = {}
titles = {}


def add(a, rid, title=None):
    a = norm(a)
    if not a or not rid:
        return
    ids_by_arxiv.setdefault(a, set()).add(rid)
    if title and rid not in titles:
        titles[rid] = title


for r in jl(ROOT / "research/review/screening/records.jsonl"):
    add(r.get("arxiv"), r.get("sid"), r.get("title"))
for r in jl(ROOT / "research/review/corpus/new-records-2026-10-15-v2.jsonl"):
    add(r.get("arxiv"), r.get("nid"), r.get("title"))
for name in ["analysis/screening/ft-routes-seed1243.jsonl",
             "analysis/screening/ft-routes-recheck797.jsonl",
             "analysis/screening/ft-routes-extra.jsonl",
             "research/review/fulltext/ft-routes.jsonl"]:
    p = ROOT / name
    if p.exists():
        for r in jl(p):
            add(r.get("arxiv"), r.get("id"), r.get("title"))

includes = {r["id"] for r in jl(ROOT / "analysis/rq1/rq1-includes.jsonl")}
t1 = {r["id"]: r for r in jl(ROOT / "analysis/screening/ft-t1/t1-decisions-all.jsonl")}
r797_dec = {}
p = ROOT / "analysis/screening/ft-r797/r797-decisions-all.jsonl"
if p.exists():
    r797_dec = {r["id"]: r for r in jl(p)}
r797 = set((ROOT / "analysis/screening/r797-tranche-ids.txt").read_text().split())
s1243 = set((ROOT / "analysis/screening/s1243-tranche-ids.txt").read_text().split())


def status(rid):
    if rid in includes:
        return "included_615"
    if rid in t1:
        return "T1_" + t1[rid]["decision"] + ("_" + t1[rid]["code"] if t1[rid].get("code") else "")
    if rid in r797_dec:
        d = r797_dec[rid]
        return "R797_" + str(d.get("decision")) + ("_" + d["code"] if d.get("code") else "")
    if rid in r797:
        return "R797_not_screened"
    if rid in s1243:
        return "S1243_not_screened"
    return "other"


rows = []
with open(ROOT / "research/review/coverage/design-space-v1.csv", encoding="utf-8") as f:
    for m in csv.DictReader(f):
        a = norm(m["arXiv ID"])
        rids = sorted(ids_by_arxiv.get(a, set()))
        st = {rid: status(rid) for rid in rids}
        covered = any(v == "included_615" for v in st.values())
        # Tranche record: prefer the seed (S1243) record, then R797, then any.
        pick = None
        if not covered and rids:
            for pref in ("S1243_not_screened", "R797_not_screened"):
                c = [r for r in rids if st[r] == pref]
                if c:
                    pick = c[0]
                    break
            if pick is None:
                pick = rids[0]
        rows.append({"model_id": m["id"], "name": m["name"], "arxiv": a,
                     "record_ids": rids, "status": st, "covered_615": covered,
                     "tranche_record": pick,
                     "title": titles.get(pick) if pick else None})

with open(OUT / "landmark-frame.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
tr = [r for r in rows if not r["covered_615"]]
(OUT / "landmark-tranche-ids.txt").write_text(
    "\n".join(r["tranche_record"] or ("NOID-" + r["model_id"]) for r in tr) + "\n")
summary = {
    "frame_models": len(rows),
    "covered_615": sum(r["covered_615"] for r in rows),
    "tranche_L": len(tr),
    "tranche_without_record": [r["model_id"] for r in tr if not r["tranche_record"]],
    "tranche_without_arxiv": [r["model_id"] for r in tr if not r["arxiv"]],
    "tranche_prior_status": {},
}
for r in tr:
    s = r["status"].get(r["tranche_record"], "no_record") if r["tranche_record"] else "no_record"
    summary["tranche_prior_status"][s] = summary["tranche_prior_status"].get(s, 0) + 1
(OUT / "landmark-frame-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
for r in rows:
    print(r["model_id"], r["name"][:28].ljust(28), r["arxiv"], "COVERED" if r["covered_615"] else "L",
          r["tranche_record"], r["status"])
