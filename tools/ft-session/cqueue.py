"""Build C queue part <q> and group <g> from filed batches t1b<lo>..t1b<hi> (same logic as the c-queue-7 build, plus
records whose quote stayed unaccepted after the one return: batch-log 'quote_after_return', criteria v1.6 s5.2).

    python -I cqueue.py <worktree> <dispatch root> <q> <g> <lo> <hi>
Tranche: FT_TRANCHE (default t1): base analysis/screening/ft-<tranche>/, batches <tranche>b<NNN>, C groups c-<tranche>-<g>,
pending file <tranche>-pending-B.jsonl (2026-10-20).
Writes analysis/screening/ft-t1/c-queue-<q>.jsonl, <root>/c-rows-<q>.jsonl, <root>/c-t1-<g>.ids; prints ids.
"""
import json, os, sys
from pathlib import Path

W, S, q, g, lo, hi = sys.argv[1:7]
W, S = Path(W), Path(S)
TR = os.environ.get("FT_TRANCHE", "t1")
base = W / "analysis/screening" / f"ft-{TR}"
SUP = {(r["id"], r["group"]) for r in map(json.loads, open(base / "c-superseded.jsonl", encoding="utf-8")) if r} if (base / "c-superseded.jsonl").exists() else set()
done = set()
for f in base.glob(f"c/c-{TR}-*/FC-*.jsonl"):
    done |= {json.loads(l)["id"] for l in open(f, encoding="utf-8") if l.strip()} - {i for i, g in SUP if g == f.parent.name}
A, B, bo = {}, {}, {}
batches = [f"{TR}b{n:03d}" for n in range(int(lo), int(hi) + 1)]
for b in batches:
    for role, st in (("A", A), ("B", B)):
        for l in open(base / b / f"F{role}-{b}.jsonl", encoding="utf-8"):
            if l.strip():
                r = json.loads(l); st[r["id"]] = r; bo[r["id"]] = b
qbad = set()
for l in open(base / "batch-log.jsonl", encoding="utf-8"):
    e = json.loads(l)
    if e.get("event") == "quote_after_return" and e.get("batch") in batches:
        qbad.add(e["id"])
PEND = {json.loads(l)["id"] for l in open(base / f"{TR}-pending-B.jsonl", encoding="utf-8") if l.strip()} if (base / f"{TR}-pending-B.jsonl").exists() else set()
out = {}
for i in A:
    if i in PEND:   # B unavailable: waits for the human author, not C
        continue
    w = []
    if A[i]["decision"] != B[i]["decision"]: w.append("disagree")
    if "adjudicate" in (A[i]["decision"], B[i]["decision"]): w.append("adjudicate_row")
    if i in qbad: w.append("quote_not_accepted_after_return")
    if w and i not in done: out[i] = w
ids = sorted(out)
with open(base / f"c-queue-{q}.jsonl", "w", encoding="utf-8", newline="\n") as f:
    for i in ids:
        f.write(json.dumps({"id": i, "batch": bo[i], "why": out[i], "A": A[i]["decision"], "B": B[i]["decision"]}) + "\n")
(S / f"c-rows-{q}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in [A[i] for i in ids] + [B[i] for i in ids]), encoding="utf-8")
(S / f"c-{TR}-{g}.ids").write_text("\n".join(ids) + "\n")
print(ids)
