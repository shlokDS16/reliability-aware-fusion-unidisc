import json, glob, os, collections, re
R = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706"
S = R + "/analysis/screening"; FT = S + "/ft-t1"
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
dl = [x for x in jl(R + "/research/review/fulltext/dispatch-log.jsonl") if "basename" in x]
log = jl(FT + "/batch-log.jsonl")
crl = jl(S + "/c-run-log.jsonl")
known = {}
for f in glob.glob(FT + "/t1b*/isolation-*.json") + glob.glob(FT + "/c/*/isolation-C.json"):
    d = json.load(open(f, encoding="utf-8")); known[d["basename"]] = os.path.relpath(f, FT)
logged = []
for e in log:
    if e.get("event") in ("discarded", "failed"):
        for bn in str(e.get("basename", "")).split(", "):
            logged.append((bn, e["event"], e["batch"], e["role"]))
for e in crl[1:]:
    logged.append((e["basename"], e.get("outcome"), e["batch"], "C"))
def match(bn):
    hits = [x for x in logged if x[0] and (bn.startswith(x[0]) or x[0].startswith(bn))]
    return hits
un = []
for x in dl:
    bn = x["basename"]
    if x["batch"].startswith("pilot"): continue
    if bn in known: continue
    h = match(bn)
    if not h: un.append((bn, x["batch"], x["role"]))
print("dispatched sessions (non-pilot):", sum(1 for x in dl if not x["batch"].startswith("pilot")))
print("dispatched, neither final/discarded file nor logged failed/discarded:", len(un))
for u in un: print("  ", u)
dset = [x["basename"] for x in dl]
for bn, ev, b, r in logged:
    if bn and not any(d.startswith(bn) for d in dset): print("logged but not in this dispatch-log:", bn, ev, b, r)
# result lines with quotes_not_accepted > 0 followed by quote_return/not_possible
qret = collections.defaultdict(set)
for e in log:
    if e.get("event") == "quote_return":
        qret[(e["batch"], e["role"])] |= set(e["ids"])
    if e.get("event") == "quote_return_not_possible":
        for b, r, *_ in e["entries"]: qret[(b, r)].add(e["id"])
for idx, e in enumerate(log, 1):
    if "event" in e: continue
    for r in "AB":
        n = e.get(f"quotes_not_accepted_{r}", 0)
        if n and not qret.get((e["batch"], r)):
            print("result line with unaccepted quotes but no return/not-possible:", idx, e["batch"], r, n)
# per batch count of result lines
rl = collections.Counter(e["batch"] for e in log if "event" not in e)
print("batches with >1 result line:", {k: v for k, v in rl.items() if v > 1})
# result lines last one vs final rows: agree/disagree consistency
A = {}; B = {}
for d in sorted(glob.glob(FT + "/t1b*")):
    b = os.path.basename(d)
    for role, st in (("A", A), ("B", B)):
        for r in jl(f"{d}/F{role}-{b}.jsonl"): st[r["id"]] = (b, r)
last = {}
for e in log:
    if "event" not in e: last[e["batch"]] = e
for b, e in sorted(last.items()):
    ids = [i for i in A if A[i][0] == b]
    dis = sorted(i for i in ids if A[i][1]["decision"] != B[i][1]["decision"])
    adj = sorted(i for i in ids if "adjudicate" in (A[i][1]["decision"], B[i][1]["decision"]))
    agree = sum(1 for i in ids if A[i][1]["decision"] == B[i][1]["decision"])
    if sorted(e.get("disagree", [])) != dis or e.get("agree") != agree:
        print("result line differs from rows", b, e.get("agree"), agree, e.get("disagree"), dis)
    if sorted(e.get("adjudicate", [])) != adj:
        print("adjudicate list differs", b, e.get("adjudicate"), adj)
# C queue batches vs FC grouping, ruled sessions per queue
q = {}
for p in sorted(glob.glob(FT + "/c-queue-*.jsonl")):
    for r in jl(p): q[r["id"]] = os.path.basename(p)
fc = {}
for p in sorted(glob.glob(FT + "/c/c-t1-*/FC-*.jsonl")):
    for r in jl(p): fc[r["id"]] = os.path.basename(os.path.dirname(p))
m = collections.defaultdict(collections.Counter)
for i in q: m[q[i]][fc.get(i)] += 1
for k in sorted(m, key=lambda s: int(re.findall(r"\d+", s)[0])): print(k, dict(m[k]))
# C rows: basis field, and FC fields
FCr = {}
for p in sorted(glob.glob(FT + "/c/c-t1-*/FC-*.jsonl")):
    for r in jl(p): FCr[r["id"]] = r
print("basis", collections.Counter(r.get("basis") for r in FCr.values()))
# C overturn vs A=B on quote-only items
for i in ["M06856","M07612","M07778","M07806","M08083","M08158","M08240","M09321","M09594","M10977","M10996","M15367","M16826","M18364","M19307","U03065"]:
    a = A[i][1]["decision"]; b = B[i][1]["decision"]; c = FCr[i]["decision"]
    if c != a: print("quote-only record: C differs from A=B", i, a, b, c)
# ft field / screener version info
print("ft values A:", collections.Counter(r[1].get("ft", "")[:60] for r in A.values()).most_common(5))
