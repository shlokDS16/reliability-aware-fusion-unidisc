"""Landmark-model coverage: for each of the 47 design-space models, is its paper among the 615 included studies, among
the seed-corpus records, or in the census random sample, and where does the paper discuss it.

    python -I paper/review/scripts/landmark_coverage.py

Inputs (all read-only):
  research/review/coverage/design-space-v1.csv            id, name, arXiv ID of the 47 models
  analysis/rq1/rq1-includes.jsonl                         the 615 included record ids (M..., U..., R...)
  research/review/corpus/*.jsonl                          record id -> arXiv id (fields id, arxiv)
  analysis/screening/ft-t1/t1-decisions-all.jsonl         T1 full-text decisions (cross-check of the included ids)
  research/review/screening/records.jsonl                 the 1,453 deduplicated seed-corpus records (sid, arxiv)
  research/review/census/census-random-final.jsonl        the census random sample (field arxiv)
  paper/review/sections/*.tex                             \\cite{arXiv:...} keys, for the main-text sections
Outputs:
  paper/review/tables/landmark-coverage.tex               longtable for supplement S5
  paper/review/tables/landmark-coverage.json              counts quoted in the text (the only source for them)
"""
import csv
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REV = ROOT / "paper/review"


def jl(p):
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def norm(a):
    a = (a or "").strip().lower().replace("arxiv:", "")
    return re.sub(r"v\d+$", "", a)


models = list(csv.DictReader(open(ROOT / "research/review/coverage/design-space-v1.csv", encoding="utf-8")))
assert len(models) == 47, len(models)

inc_ids = {r["id"] for r in jl(ROOT / "analysis/rq1/rq1-includes.jsonl")}
t1_inc = {r["id"] for r in jl(ROOT / "analysis/screening/ft-t1/t1-decisions-all.jsonl") if r.get("decision") == "include"}

def ntitle(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


# Many included records (subscription databases, title resolution) carry no arXiv id, so a model also counts as
# included when an included record has the same normalised title as any corpus record with the model's arXiv id.
id2ax, id2title, ax2titles = {}, {}, {}
seed = jl(ROOT / "research/review/screening/records.jsonl")
for f in sorted(glob.glob(str(ROOT / "research/review/corpus/*.jsonl"))) + ["seed"]:
    for r in (seed if f == "seed" else jl(f)):
        i = r.get("id") or r.get("sid") or r.get("record_id")
        a = r.get("arxiv")
        if not isinstance(a, str):        # the curated-list records keep arXiv metadata in a dict; id in canonical_id
            a = (r.get("canonical_id") or "") if str(r.get("canonical_id", "")).startswith("arXiv:") else ""
        a = norm(a)
        if i and a:
            id2ax.setdefault(i, a)
        if i and r.get("title"):
            id2title.setdefault(i, ntitle(r["title"]))
        if a and r.get("title"):
            ax2titles.setdefault(a, set()).add(ntitle(r["title"]))
seed_ax = {norm(r["arxiv"]) for r in seed if r.get("arxiv")}

inc_ax, inc_title = {}, {}
for i in sorted(inc_ids):
    if i in id2ax:
        inc_ax.setdefault(id2ax[i], i)
    if id2title.get(i):
        inc_title.setdefault(id2title[i], i)


def included_record(ax):
    if ax in inc_ax:
        return inc_ax[ax], "arXiv id"
    for t in ax2titles.get(ax, ()):
        if len(t) > 15 and t in inc_title:
            return inc_title[t], "title"
    return None, None
census = jl(ROOT / "research/review/census/census-random-final.jsonl")
cen_ax = {norm(r.get("arxiv")): r for r in census if r.get("arxiv")}

# main-text sections that cite each arXiv key
cites = {}
for f in sorted(glob.glob(str(REV / "sections/*.tex"))):
    sec = int(Path(f).name[:2])
    txt = open(f, encoding="utf-8").read()
    txt = "\n".join(l.split("%")[0] if not l.lstrip().startswith("%") else "" for l in txt.splitlines())
    for grp in re.findall(r"\\cite[pt]?\{([^}]*)\}", txt):
        for k in grp.split(","):
            k = k.strip()
            if k.startswith("arXiv:"):
                cites.setdefault(norm(k), set()).add(sec)

rows = []
for m in models:
    ax = norm(m["arXiv ID"])
    rec, how = included_record(ax)
    rows.append({"id": m["id"], "name": m["name"], "arxiv": ax, "titles_known": len(ax2titles.get(ax, ())),
                 "included": rec is not None, "included_record": rec, "matched_by": how,
                 "seed_record": ax in seed_ax,
                 "census": ax in cen_ax, "census_eligible": (cen_ax.get(ax) or {}).get("eligible"),
                 "main_sections": sorted(cites.get(ax, set()))})

C = {"models": len(rows),
     "included": sum(r["included"] for r in rows),
     "not_included": sum(not r["included"] for r in rows),
     "seed_record": sum(r["seed_record"] for r in rows),
     "not_included_but_seed_record": sum((not r["included"]) and r["seed_record"] for r in rows),
     "census": sum(r["census"] for r in rows),
     "not_included_but_census": sum((not r["included"]) and r["census"] for r in rows),
     "cited_in_main_text": sum(bool(r["main_sections"]) for r in rows),
     "not_included_cited_in_main_text": sum((not r["included"]) and bool(r["main_sections"]) for r in rows),
     "included_ids_not_in_t1_includes": sorted(r["included_record"] for r in rows if r["included"] and r["included_record"] not in t1_inc),
     "included_ids_without_arxiv": len([i for i in inc_ids if i not in id2ax]),
     "included_ids_without_title": len([i for i in inc_ids if not id2title.get(i)]),
     "models_without_known_title": [r["id"] for r in rows if not r["titles_known"]],
     "n_included_ids": len(inc_ids), "n_census": len(census)}
(REV / "tables/landmark-coverage.json").write_text(json.dumps({"counts": C, "rows": rows}, indent=1) + "\n", encoding="utf-8")


def tex(s):
    return s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_").replace("#", r"\#")


yn = lambda b: "yes" if b else "no"
T = [r"% generated by paper/review/scripts/landmark_coverage.py; do not edit",
     r"\begin{longtable}{@{}l p{4.2cm} l l l l p{2.6cm}@{}}",
     r"\caption{Coverage of the 47 design-space models by the review's study sets. Included: the paper is one of the "
     + str(C["n_included_ids"]) + r" included studies. Seed record: it is one of the deduplicated seed-corpus records, most of "
     r"which were not assessed at full text when screening was frozen. Census: it is in the census random sample ("
     + str(C["n_census"]) + r" records). Main text: the sections that cite it; every model is also a row of the design-space table.}"
     r"\label{tab:landmark}\\",
     r"\toprule", r"Row & Model & arXiv & Included & Seed record & Census & Main text \\", r"\midrule", r"\endfirsthead",
     r"\toprule", r"Row & Model & arXiv & Included & Seed record & Census & Main text \\", r"\midrule", r"\endhead"]
for r in rows:
    secs = ", ".join(f"S{s}" if False else str(s) for s in r["main_sections"]) or "--"
    T.append(" & ".join([r["id"], tex(r["name"]), r["arxiv"], yn(r["included"]), yn(r["seed_record"]),
                         yn(r["census"]), ("Sec.~" + secs) if r["main_sections"] else "--"]) + r" \\")
T += [r"\midrule",
      f"Total & {C['models']} models & & {C['included']} & {C['seed_record']} & {C['census']} & {C['cited_in_main_text']} cited \\\\",
      r"\bottomrule", r"\end{longtable}"]
(REV / "tables/landmark-coverage.tex").write_text("\n".join(T) + "\n", encoding="utf-8")
print(json.dumps(C, indent=1))
