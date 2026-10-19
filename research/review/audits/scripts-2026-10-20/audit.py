import json, collections, glob, os, re, hashlib
R = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706"
S = R + "/analysis/screening"
FT = S + "/ft-t1"
def jl(p):
    out = []
    with open(p, encoding="utf-8") as f:
        for n, l in enumerate(f, 1):
            if l.strip():
                out.append(json.loads(l))
    return out
P = lambda *a: print(*a)

# ---------- 1. batch plans
plan = {}; plan_part = {}; id_batches = collections.defaultdict(list)
for p in sorted(glob.glob(R + "/research/review/fulltext/t1-batches-part*.json")):
    d = json.load(open(p, encoding="utf-8"))
    part = os.path.basename(p)
    n = sum(len(v) for v in d["batches"].values())
    if d.get("n") != n: P("PLAN n mismatch", part, d.get("n"), n)
    for b, ids in d["batches"].items():
        if b in plan: P("BATCH IN TWO PARTS", b, plan_part[b], part)
        plan[b] = ids; plan_part[b] = part
        for i in ids: id_batches[i].append(b)
P("plan batches", len(plan), "ids", sum(len(v) for v in plan.values()), "unique ids", len(id_batches))
dups = {i: b for i, b in id_batches.items() if len(b) > 1}
P("ids in >1 batch (plans):", dups)
dirs = sorted(os.path.basename(x) for x in glob.glob(FT + "/t1b*"))
P("dirs", len(dirs), "plan-not-dir", sorted(set(plan) - set(dirs)), "dir-not-plan", sorted(set(dirs) - set(plan)))
for b in dirs:
    if len(plan.get(b, [])) != 10: P("batch size", b, len(plan.get(b, [])))

# ---------- rows
A = {}; B = {}; rowbatch = {}
problems = []
all_ids_seen = collections.Counter()
for b in dirs:
    for role, store in (("A", A), ("B", B)):
        f = f"{FT}/{b}/F{role}-{b}.jsonl"
        rows = jl(f)
        ids = [r["id"] for r in rows]
        c = collections.Counter(ids)
        if any(v > 1 for v in c.values()): problems.append((b, role, "dup rows", [k for k, v in c.items() if v > 1]))
        if set(ids) != set(plan[b]): problems.append((b, role, "id set != plan", sorted(set(ids) ^ set(plan[b]))))
        exp_scr = {"A": "FA-claude-sonnet-5-5", "B": "FB-claude-opus-5-5"}[role]
        for r in rows:
            if r.get("screener") != exp_scr: problems.append((b, role, r["id"], "screener", r.get("screener")))
            if r.get("decision") not in ("include", "exclude", "adjudicate"): problems.append((b, role, r["id"], "decision", r.get("decision")))
            if r["id"] in store: problems.append((b, role, r["id"], "id also in batch", rowbatch.get(r["id"])))
            store[r["id"]] = r; rowbatch[r["id"]] = b
P("row problems:", problems)
P("A rows", len(A), "B rows", len(B))

# discarded files and their log events
log = jl(FT + "/batch-log.jsonl")
disc_events = [(e["batch"], e["role"]) for e in log if e.get("event") == "discarded"]
for f in sorted(glob.glob(FT + "/t1b*/*DISCARDED*")):
    b = os.path.basename(os.path.dirname(f)); fn = os.path.basename(f)
    role = re.match(r"(?:F|isolation-|quote-check-)([AB])", fn).group(1)
    ok = (b, role) in disc_events
    P("DISCARDED file", b, fn, "logged discard:", ok)
    if fn.startswith("F"):
        rows = jl(f)
        P("   discarded rows", len(rows))

# result lines: last per batch
res = collections.defaultdict(list)
for i, e in enumerate(log, 1):
    if "event" not in e: res[e["batch"]].append((i, e))
for b in dirs:
    if b not in res: P("no result line", b); continue
    ln, last = res[b][-1]
    if not (last.get("isolation_A") and last.get("isolation_B")): P("last result line isolation not both true", b, ln, last.get("isolation_A"), last.get("isolation_B"))
    if last.get("rows_A") != 10 or last.get("rows_B") != 10 or last.get("missing_A") or last.get("missing_B"): P("last result rows", b, ln, last.get("rows_A"), last.get("rows_B"))
# ---------- 2. isolation files
basenames = collections.Counter()
for b in dirs:
    for role in "AB":
        d = json.load(open(f"{FT}/{b}/isolation-{role}.json", encoding="utf-8"))
        basenames[d["basename"]] += 1
        if not d.get("pass") or d.get("flags"): P("ISOLATION FAIL", b, role, d)
        if not d["basename"].startswith(f"{role}-{b}-"): P("isolation basename mismatch", b, role, d["basename"])
for f in sorted(glob.glob(FT + "/t1b*/isolation-*DISCARDED*.json")):
    d = json.load(open(f, encoding="utf-8")); basenames[d["basename"]] += 1
    P("discarded isolation", os.path.relpath(f, FT), d.get("pass"), str(d.get("flags"))[:150])
cdirs = sorted(os.path.basename(x) for x in glob.glob(FT + "/c/c-t1-*"))
for c in cdirs:
    d = json.load(open(f"{FT}/c/{c}/isolation-C.json", encoding="utf-8"))
    basenames[d["basename"]] += 1
    if not d.get("pass") or d.get("flags"): P("C ISOLATION FAIL", c, d)
    if not d["basename"].startswith(f"C-{c}-"): P("C basename mismatch", c, d["basename"])
P("basename reused:", [k for k, v in basenames.items() if v > 1])
# dispatch log uniqueness
dl = jl(R + "/research/review/fulltext/dispatch-log.jsonl")
dbn = collections.Counter(x["basename"] for x in dl if "basename" in x)
P("dispatch-log basenames reused:", [k for k, v in dbn.items() if v > 1])
dset = set(dbn)
for k in basenames:
    if k not in dset: P("isolation basename not in dispatch-log:", k)
for x in dl:
    if "basename" in x and x.get("model") != {"A": "claude-sonnet-5-5", "B": "claude-opus-5-5", "C": "claude-fable-5-1"}[x["role"]]: P("dispatch model mismatch", x)
# dispatch ids sha vs plan
for x in dl:
    b = x.get("batch")
    if b in plan:
        h = hashlib.sha256("\n".join(sorted(plan[b])).encode()).hexdigest()
        if h != x["ids_sha256"]: P("dispatch ids sha != plan", x["basename"])
# c-run-log
crl = jl(S + "/c-run-log.jsonl")
P("c-run-log route:", crl[0].get("route"), crl[0].get("date"))
last_c = {}
for e in crl[1:]:
    last_c.setdefault(e["batch"], []).append(e)
for c in cdirs:
    es = last_c.get(c, [])
    comp = [e for e in es if str(e.get("outcome", "")).startswith("complete")]
    if not comp: P("no complete C session", c)
    bns = set(e["basename"] for e in comp)
    iso = json.load(open(f"{FT}/c/{c}/isolation-C.json", encoding="utf-8"))["basename"]
    if bns != {iso}: P("C session basename mismatch", c, bns, iso)
    if any(not e.get("isolation") for e in comp): P("C complete with isolation false", c)
    if any(e.get("model") != "claude-fable-5-1" for e in es): P("C model", c)
    if comp[-1].get("quotes_not_accepted"): P("C final quotes not accepted", c, comp[-1]["quotes_not_accepted"])
for k in last_c:
    if k not in cdirs: P("c-run-log batch without dir", k)
# C dispatch log: role C batches
cdl = [x for x in dl if x.get("role") == "C"]
P("C dispatches", len(cdl), collections.Counter(x["batch"] for x in cdl))

# ---------- 3. quotes
qbad = []
for b in dirs:
    for role in "AB":
        for q in jl(f"{FT}/{b}/quote-check-{role}.jsonl"):
            if q["status"] != "found": qbad.append((b, role, q["id"], q["i"], q["status"]))
P("unaccepted quotes in final quote-check A/B files:", len(qbad))
for x in qbad: P("  ", x)
# quote-check coverage: one entry per evidence item?
miss_q = 0
for b in dirs:
    for role, store in (("A", A), ("B", B)):
        qs = {(q["id"], q["i"]) for q in jl(f"{FT}/{b}/quote-check-{role}.jsonl")}
        for i in plan[b]:
            for k in range(len(store[i].get("evidence", []))):
                if (i, k) not in qs: miss_q += 1
P("evidence items without a quote-check entry:", miss_q)
qret = [e for e in log if e.get("event") == "quote_return"]
qafter = [e for e in log if e.get("event") == "quote_after_return"]
qnp = [e for e in log if e.get("event") == "quote_return_not_possible"]
returned = set()
for e in qret:
    for i in e["ids"]: returned.add((e["batch"], e["role"], i))
cnt = collections.Counter((e["batch"], e["role"]) for e in qret)
P("quote_return events per (batch, role) >1:", {k: v for k, v in cnt.items() if v > 1})
idret = collections.Counter()
for e in qret:
    for i in e["ids"]: idret[(e["batch"], e["role"], i)] += 1
P("id returned >1 times:", {k: v for k, v in idret.items() if v > 1})
np_ids = set(e["id"] for e in qnp)
after_ids = set(e["id"] for e in qafter)
P("quote_return ids", len(returned), "not_possible ids", len(np_ids), "after_return ids", sorted(after_ids))

# ---------- 4. C coverage
queue = []
for p in sorted(glob.glob(FT + "/c-queue-*.jsonl")):
    for r in jl(p): r["_q"] = os.path.basename(p); queue.append(r)
qids = collections.Counter(r["id"] for r in queue)
P("queue rows", len(queue), "unique", len(qids), "dups", [k for k, v in qids.items() if v > 1])
qmap = {r["id"]: r for r in queue}
FC = {}; fcfile = collections.defaultdict(list)
for c in cdirs:
    for r in jl(f"{FT}/c/{c}/FC-{c}.jsonl"):
        fcfile[r["id"]].append(c)
        FC[r["id"]] = r
        if r.get("screener") != "FC-claude-fable-5-1": P("FC screener", c, r["id"], r.get("screener"))
        if r.get("decision") not in ("include", "exclude"): P("FC decision", c, r["id"], r.get("decision"))
P("FC rows unique ids", len(FC), "ids ruled >1:", {k: v for k, v in fcfile.items() if len(v) > 1})
P("queued not ruled:", sorted(set(qids) - set(FC)))
P("ruled not queued:", sorted(set(FC) - set(qids)))
# C quote checks
for c in cdirs:
    for q in jl(f"{FT}/c/{c}/quote-check-C.jsonl"):
        if q["status"] != "found": P("C quote unaccepted (final file)", c, q["id"], q["i"], q["status"])
# dispatch membership: C dispatch ids sha equals FC ids
for x in cdl:
    c = x["batch"]
    ids = sorted(k for k, v in fcfile.items() if c in v)
    h = hashlib.sha256("\n".join(ids).encode()).hexdigest()
    if h != x["ids_sha256"]: P("C dispatch ids sha != FC ids", x["basename"], len(ids), x["n"])
# disagreements / adjudicate from rows
need = set()
for i in A:
    a, b = A[i]["decision"], B[i]["decision"]
    if a != b or "adjudicate" in (a, b): need.add(i)
P("disagree-or-adjudicate from rows:", len(need), "not queued:", sorted(need - set(qids)))
extra = sorted(set(qids) - need)
P("queued without disagreement (quote-only):", len(extra), extra)
# check quote-only queue reasons
for i in extra:
    P("   ", i, qmap[i].get("why"), qmap[i]["_q"], "np" if i in np_ids else "", "after" if i in after_ids else "")
# reasons in queue vs actual
for r in queue:
    i = r["id"]
    if i in A and (r.get("A") not in (None, A[i]["decision"]) or r.get("B") not in (None, B[i]["decision"])):
        P("queue A/B label differs from rows", i, r.get("A"), A[i]["decision"], r.get("B"), B[i]["decision"])
    if r.get("batch") and r["batch"] != rowbatch.get(i): P("queue batch differs", i, r["batch"], rowbatch.get(i))
# every quote-unaccepted after return / not-possible record queued?
for i in np_ids | after_ids:
    if i not in qids: P("quote problem not queued:", i)
# remaining unaccepted quotes in final A/B files: is the id queued?
for (b, role, i, k, st) in qbad:
    tag = "returned" if (b, role, i) in returned else ("not_possible" if i in np_ids else "NOT RETURNED")
    P("  final-unaccepted", b, role, i, k, st, tag, "queued" if i in qids else "NOT QUEUED")

# ---------- 5. reproduce decisions
def fields(r):
    return {k: r.get(k, "") for k in ("decision", "code", "xsub", "i1", "nonlang_only")}
dec = {}
for i in A:
    if i in FC:
        r = FC[i]; d = fields(r); d["source"] = "C"
    else:
        a, b = A[i], B[i]
        assert a["decision"] == b["decision"] and a["decision"] != "adjudicate", i
        d = fields(a); d["source"] = "A=B"
        if a["decision"] == "exclude" and a.get("code") != b.get("code"):
            d["code_conflict"] = (a.get("code"), b.get("code"))
        if a["decision"] == "include" and a.get("i1") != b.get("i1"):
            d["i1_conflict"] = (a.get("i1"), b.get("i1"))
        if a.get("nonlang_only") != b.get("nonlang_only"):
            d["nl_conflict"] = (a.get("nonlang_only"), b.get("nonlang_only"))
    dec[i] = d
filed = {r["id"]: r for r in jl(FT + "/t1-decisions-all.jsonl")}
P("filed decisions", len(filed), "recomputed", len(dec), "id diff", sorted(set(filed) ^ set(dec)))
diffs = []
for i in dec:
    f = filed.get(i)
    if not f: continue
    for k in ("decision", "code", "xsub", "i1", "nonlang_only", "source"):
        if (f.get(k) if f.get(k) is not None else "") != (dec[i].get(k) if dec[i].get(k) is not None else ""):
            diffs.append((i, k, f.get(k), dec[i].get(k)))
    if f.get("batch") != rowbatch[i]: diffs.append((i, "batch", f.get("batch"), rowbatch[i]))
P("field diffs:", len(diffs))
for x in diffs[:40]: P("  ", x)
conf = {i: d for i, d in dec.items() if any(k in d for k in ("code_conflict", "i1_conflict", "nl_conflict"))}
P("A=B rows with field conflicts:", len(conf))
for i, d in conf.items(): P("  ", i, {k: d[k] for k in d if k.endswith("conflict")}, "filed:", filed[i].get("code"), filed[i].get("i1"), filed[i].get("nonlang_only"))
cd = collections.Counter(d["decision"] for d in dec.values())
codes = collections.Counter(d["code"] for d in dec.values() if d["decision"] == "exclude")
i1 = collections.Counter(d["i1"] for d in dec.values() if d["decision"] == "include")
nl = sum(1 for d in dec.values() if d["decision"] == "include" and d["nonlang_only"] is True)
Cn = collections.Counter(d["decision"] for d in dec.values() if d["source"] == "C")
P("recomputed decisions", dict(cd), "codes", dict(codes), "i1", dict(i1), "nonlang_only incl", nl, "C", sum(Cn.values()), dict(Cn))
# by part
bp = collections.defaultdict(collections.Counter)
for i, d in dec.items(): bp[plan_part[rowbatch[i]]][d["decision"]] += 1
for k in sorted(bp): P("  part", k, dict(bp[k]))
def rng(lo, hi):
    c = collections.Counter()
    for i, d in dec.items():
        n = int(rowbatch[i][3:])
        if lo <= n <= hi: c[d["decision"]] += 1
    return dict(c)
P("t1b001-034", rng(1, 34), "t1b035-076", rng(35, 76), "t1b077-093", rng(77, 93))
summ = json.load(open(FT + "/t1-summary-all.json", encoding="utf-8"))
P("summary file:", summ["n"], summ["decision"], summ["exclude_codes"], summ["include_i1"], summ["include_nonlang_only"], summ["adjudicated_by_C"], summ["C_decision"])
# nonlang_only for all decisions (not only includes)
P("nonlang_only true among all decisions:", sum(1 for d in dec.values() if d["nonlang_only"] is True))

# ---------- 6. agreement
def kappa(tp, tn, a_only, b_only):
    n = tp + tn + a_only + b_only
    po = (tp + tn) / n
    pa = (tp + a_only) / n; pb = (tp + b_only) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return po, (po - pe) / (1 - pe)
pos = lambda d: d in ("include", "adjudicate")
tp = sum(1 for i in A if pos(A[i]["decision"]) and pos(B[i]["decision"]))
tn = sum(1 for i in A if not pos(A[i]["decision"]) and not pos(B[i]["decision"]))
ao = sum(1 for i in A if pos(A[i]["decision"]) and not pos(B[i]["decision"]))
bo = sum(1 for i in A if not pos(A[i]["decision"]) and pos(B[i]["decision"]))
po, k = kappa(tp, tn, ao, bo)
P("pass/exclude: both_pos", tp, "both_neg", tn, "A_only", ao, "B_only", bo, "raw", round(po, 4), "kappa", round(k, 4))
p_pos = 2 * tp / (2 * tp + ao + bo); p_neg = 2 * tn / (2 * tn + ao + bo)
P("p_pos", round(p_pos, 4), "p_neg", round(p_neg, 4), "bias", round(abs(ao - bo) / len(A), 4), "prev", round(abs(tp - tn) / len(A), 4))
inc = lambda d: d == "include"
tp2 = sum(1 for i in A if inc(A[i]["decision"]) and inc(B[i]["decision"]))
tn2 = sum(1 for i in A if not inc(A[i]["decision"]) and not inc(B[i]["decision"]))
ao2 = sum(1 for i in A if inc(A[i]["decision"]) and not inc(B[i]["decision"]))
bo2 = sum(1 for i in A if not inc(A[i]["decision"]) and inc(B[i]["decision"]))
P("include vs not:", tp2, tn2, ao2, bo2, [round(x, 4) for x in kappa(tp2, tn2, ao2, bo2)])
t3 = collections.Counter(f"{A[i]['decision']}|{B[i]['decision']}" for i in A)
P("3-way table", dict(sorted(t3.items())))
cats = ["include", "exclude", "adjudicate"]; n = len(A)
po3 = sum(t3[f"{c}|{c}"] for c in cats) / n
pe3 = sum((sum(t3[f"{c}|{d}"] for d in cats) / n) * (sum(t3[f"{d}|{c}"] for d in cats) / n) for c in cats)
P("3-way raw", round(po3, 4), "kappa", round((po3 - pe3) / (1 - pe3), 4))
# bootstrap kappa pass/exclude, same seed if implementation is comparable
import random
ids = sorted(A); rnd = random.Random(20261024); ks = []
for _ in range(2000):
    s = [ids[rnd.randrange(n)] for _ in range(n)]
    a = sum(1 for i in s if pos(A[i]["decision"]) and pos(B[i]["decision"]))
    b_ = sum(1 for i in s if not pos(A[i]["decision"]) and not pos(B[i]["decision"]))
    c_ = sum(1 for i in s if pos(A[i]["decision"]) and not pos(B[i]["decision"]))
    d_ = n - a - b_ - c_
    ks.append(kappa(a, b_, c_, d_)[1])
ks.sort(); P("my bootstrap 95%", round(ks[49], 4), round(ks[1949], 4))
pa = collections.Counter(A[i]["decision"] for i in A); pb = collections.Counter(B[i]["decision"] for i in B)
P("per screener", dict(pa), dict(pb), "adj rate", round(pa["adjudicate"] / n, 4), round(pb["adjudicate"] / n, 4))
# rows for agreement: are all A/B rows final (non-discarded)? -> yes by construction

# ---------- 7. K
samp = json.load(open(S + "/ta-recheck-sample-v1.3-frozen.json", encoding="utf-8"))
sids = samp["ids"]
P("sample n", len(sids), len(set(sids)))
Kinc = sorted(i for i in sids if i in dec and dec[i]["decision"] == "include")
Kexc = sorted(i for i in sids if i in dec and dec[i]["decision"] == "exclude")
notin = sorted(i for i in sids if i not in dec)
P("K", len(Kinc), Kinc, "excluded", len(Kexc), "not in T1", len(notin), notin)
P("K sources", [(i, dec[i]["source"], rowbatch[i]) for i in Kinc])
kf = json.load(open(S + "/ta-recheck-k.json", encoding="utf-8"))
P("filed K", kf["K"], kf["counts"], [x["id"] for x in kf["included"]])
P("filed excl ids == mine:", sorted(x["id"] for x in kf["excluded"]) == Kexc)
# sample ids per batch (mixing)
sb = collections.Counter(rowbatch[i] for i in sids if i in rowbatch)
P("sample ids per batch:", dict(sorted(sb.items())))
# C8
c8 = [json.loads(l) for l in open(S + "/ta-recheck-c8-candidates-v1.4.jsonl", encoding="utf-8") if l.strip()]
c8ids = [r.get("id") for r in c8]
P("C8 n", len(c8ids), "in T1", sum(1 for i in c8ids if i in dec), "not in T1", [i for i in c8ids if i not in dec])
P("C8 decisions", collections.Counter(dec[i]["decision"] for i in c8ids if i in dec))
P("sample∩C8", set(sids) & set(c8ids))
# not-retrieved file vs sample
nr = [r["id"] for r in jl(FT + "/t1-not-retrieved.jsonl")]
P("not-retrieved", nr, "in decisions:", [i for i in nr if i in dec], "in sample:", [i for i in nr if i in sids])
json.dump({"dec": dec, "rowbatch": rowbatch, "sids": sids, "c8": c8ids}, open(os.path.dirname(__file__) + "/state.json", "w"))
