"""Landmark tranche (D0061): final full-text decisions and summary, same logic as tools/ft-session/refresh_t1.py.

    python -I analysis/screening/landmark/refresh_lmk.py

Reads analysis/screening/ft-lmk/lmkb*/F{A,B}-<batch>.jsonl and adjudicator rows ft-lmk/c/c-lmk-*/FC-*.jsonl (when
A and B differ or one says adjudicate). Writes ft-lmk/lmk-decisions-all.jsonl (id, batch, decision, code, xsub, i1,
nonlang_only, mm_A, mm_B, rq_A, rq_B, source, A, B) and ft-lmk/lmk-summary-all.json. Fails if a disagreement has no
C row or if A and B screened different ids.
"""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
base = ROOT / "analysis/screening/ft-lmk"
plan = json.loads((ROOT / "research/review/fulltext/lmk-batches-part1.json").read_text(encoding="utf-8"))
A, B, bo = {}, {}, {}
for b in plan["batches"]:
    for role, st in (("A", A), ("B", B)):
        for line in open(base / b / f"F{role}-{b}.jsonl", encoding="utf-8"):
            if line.strip():
                r = json.loads(line)
                st[r["id"]] = r
                bo[r["id"]] = b
assert set(A) == set(B) == {i for c in plan["batches"].values() for i in c}, "A, B and the plan differ"
C = {}
for f in sorted(base.glob("c/c-lmk-*/FC-*.jsonl")):
    for line in open(f, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            C[r["id"]] = r
need = [i for i in A if (A[i]["decision"] != B[i]["decision"] or "adjudicate" in (A[i]["decision"], B[i]["decision"]))
        and i not in C]
assert not need, need
rows = []
for i in sorted(A):
    src = "C" if i in C else "A=B"
    r = C[i] if i in C else A[i]
    rows.append({"id": i, "batch": bo[i], "decision": r["decision"], "code": r.get("code", ""), "xsub": r.get("xsub", ""),
                 "i1": r.get("i1", ""), "nonlang_only": r.get("nonlang_only", False),
                 "mm_A": A[i].get("mm"), "mm_B": B[i].get("mm"), "rq_A": A[i].get("rq", []), "rq_B": B[i].get("rq", []),
                 "source": src, "A": A[i]["decision"], "B": B[i]["decision"]})
with open(base / "lmk-decisions-all.jsonl", "w", encoding="utf-8", newline="\n") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
s = {"scope": "landmark tranche L (D0061), batches " + ", ".join(plan["batches"]),
     "n": len(rows), "decision": dict(collections.Counter(r["decision"] for r in rows)),
     "exclude_codes": dict(collections.Counter(r["code"] for r in rows if r["decision"] == "exclude")),
     "exclude_xsub": dict(collections.Counter(r["xsub"] for r in rows if r["decision"] == "exclude")),
     "include_i1": dict(collections.Counter(r["i1"] for r in rows if r["decision"] == "include")),
     "include_nonlang_only": sum(1 for r in rows if r["decision"] == "include" and r["nonlang_only"]),
     "agree_A_B": sum(1 for r in rows if r["A"] == r["B"]), "adjudicated_by_C": len(C),
     "C_decision": dict(collections.Counter(C[i]["decision"] for i in C)),
     "files": "lmk-decisions-all.jsonl; batch-log.jsonl; lmkb00*/; c/ (if any)"}
(base / "lmk-summary-all.json").write_text(json.dumps(s, indent=1) + "\n", encoding="utf-8")
print(json.dumps(s, indent=1))
