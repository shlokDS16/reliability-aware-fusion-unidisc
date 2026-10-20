"""Independent recomputation of T1 derived files (gate-auditor re-audit 2; copy of reaudit1/recompute.py with two adapted checks:
provenance is now built from the 885 FA ids (finding 18 fix), and the PRISMA pending label is now
`awaiting_second_screener_B_unavailable` (finding 15 fix)). Read-only on the repo."""
import json, glob, re, collections, random, hashlib, sys
from pathlib import Path
R = Path(sys.argv[1]); FT = R / "analysis/screening/ft-t1"; SCR = R / "analysis/screening"
C_ = collections.Counter
def jl(p): return [json.loads(l) for l in open(p, encoding="utf8") if l.strip()]
out = []
def say(*a): out.append(" ".join(str(x) for x in a)); print(*a)

# plans
plan = {}
for p in sorted((R / "research/review/fulltext").glob("t1-batches-part*.json")):
    for b, ids in json.load(open(p, encoding="utf8"))["batches"].items():
        assert b not in plan; plan[b] = ids
allp = [i for v in plan.values() for i in v]
say("plan batches", len(plan), "ids", len(allp), "unique", len(set(allp)))
pend = {r["id"]: r for r in jl(FT / "t1-pending-B.jsonl")}
say("pending", sorted(pend))
A, B, bo = {}, {}, {}
for b, ids in plan.items():
    for role, st in (("A", A), ("B", B)):
        f = FT / b / f"F{role}-{b}.jsonl"
        rows = jl(f)
        got = [r["id"] for r in rows]
        assert len(got) == len(set(got)), (b, role)
        exp = set(ids) - (set(pend) if role == "B" else set())
        if set(got) != exp: say("ID MISMATCH", b, role, sorted(set(got) ^ exp))
        for r in rows:
            assert r["id"] not in st; st[r["id"]] = r; bo[r["id"]] = b
            want = "FA-claude-sonnet-5-5" if role == "A" else "FB-claude-opus-5-5"
            if r.get("screener") != want: say("SCREENER FIELD", b, role, r["id"], r.get("screener"))
say("FA", len(A), "FB", len(B), "pending in B:", [i for i in pend if i in B])
# folder listing: every non-DISCARDED F file is the plan file
for d in sorted(FT.glob("t1b*")):
    for f in d.glob("F*.jsonl"):
        if "DISCARDED" not in f.name and f.name not in (f"FA-{d.name}.jsonl", f"FB-{d.name}.jsonl"): say("EXTRA F FILE", f)
# C rows
sup = {(r["id"], r["group"]) for r in jl(FT / "c-superseded.jsonl")}
Crow = {}; Call = C_()
for f in sorted(FT.glob("c/c-t1-*/FC-*.jsonl")):
    g = f.parent.name
    for r in jl(f):
        Call[r["id"]] += 1
        if (r["id"], g) in sup: continue
        assert r["id"] not in Crow, r["id"]; Crow[r["id"]] = dict(r, group=g)
        if r.get("screener") != "FC-claude-fable-5-1" or r["decision"] not in ("include", "exclude"): say("C ROW BAD", r["id"])
say("FC rows total", sum(Call.values()), "used", len(Crow), "superseded", sorted(sup), "superseded used?", [i for i, g in sup if Crow.get(i, {}).get("group") == g])
ids = sorted(set(A) & set(B))
dis = {i for i in ids if A[i]["decision"] != B[i]["decision"] or "adjudicate" in (A[i]["decision"], B[i]["decision"])}
cq = [r for p in sorted(FT.glob("c-queue-*.jsonl"), key=lambda p: int(p.stem.split("-")[-1])) for r in jl(p)]
cqi = {r["id"] for r in cq}
say("dis/adj", len(dis), "queued rows", len(cq), "unique", len(cqi), "dis not queued", sorted(dis - cqi),
    "queued not ruled", sorted(cqi - set(Crow)), "ruled not queued", sorted(set(Crow) - cqi), "pending queued", sorted(cqi & set(pend)))
say("quote-only reasons", dict(C_(w for r in cq if r["id"] not in dis for w in r.get("why", []))))
# decisions
dec = []
for i in ids:
    src = "C" if i in Crow else "A=B"; r = Crow[i] if i in Crow else A[i]
    if src == "A=B": assert A[i]["decision"] == B[i]["decision"] != "adjudicate"
    dec.append({"id": i, "batch": bo[i], "decision": r["decision"], "code": r.get("code", ""), "xsub": r.get("xsub", ""), "i1": r.get("i1", ""),
                "nonlang_only": r.get("nonlang_only", False), "source": src, "A": A[i]["decision"], "B": B[i]["decision"]})
filed = {r["id"]: r for r in jl(FT / "t1-decisions-all.jsonl")}
diff = [(d["id"], k, d[k], filed.get(d["id"], {}).get(k)) for d in dec for k in d if filed.get(d["id"], {}).get(k) != d[k]]
say("decisions recomputed", len(dec), "filed", len(filed), "ids equal", set(filed) == {d["id"] for d in dec}, "field diffs", diff[:10], len(diff))
say("pending in decisions?", [i for i in pend if i in filed])
# summary
def part(b): return "p19" if b >= "t1b077" else ("OR" if b >= "t1b035" else "OA")
S = json.load(open(FT / "t1-summary-all.json", encoding="utf8"))
mine = {"n": len(dec), "decision": dict(C_(d["decision"] for d in dec)),
        "by_part": {p: dict(C_(d["decision"] for d in dec if part(d["batch"]) == p)) for p in ("OA", "OR", "p19")},
        "exclude_codes": dict(C_(d["code"] for d in dec if d["decision"] == "exclude")),
        "include_i1": dict(C_(d["i1"] for d in dec if d["decision"] == "include")),
        "nonlang": sum(1 for d in dec if d["decision"] == "include" and d["nonlang_only"]),
        "C": len(Crow), "C_decision": dict(C_(r["decision"] for r in Crow.values())),
        "C_basis": dict(C_(r.get("basis") for r in Crow.values())),
        "nr": len(jl(FT / "t1-not-retrieved.jsonl")), "pending": sorted(pend)}
say("summary mine", json.dumps(mine))
chk = [mine["n"] == S["n"], mine["decision"] == S["decision"], sorted(mine["by_part"].values(), key=str) == sorted(S["by_part"].values(), key=str),
       mine["exclude_codes"] == S["exclude_codes"], mine["include_i1"] == S["include_i1"], mine["nonlang"] == S["include_nonlang_only"],
       mine["C"] == S["adjudicated_by_C"], mine["C_decision"] == S["C_decision"], mine["nr"] == S["not_retrieved_X6"], mine["pending"] == S["pending_B_unavailable"]]
say("summary checks", chk)
# A=B secondary-field ties (finding 5)
ties = [(i, k, A[i].get(k), B[i].get(k)) for i in ids if i not in Crow for k in ("code", "i1", "nonlang_only") if A[i].get(k, "" if k != "nonlang_only" else False) != B[i].get(k, "" if k != "nonlang_only" else False)]
say("A=B secondary ties", ties)
decB = [dict(d, code=B[d["id"]].get("code", ""), i1=B[d["id"]].get("i1", ""), nonlang_only=B[d["id"]].get("nonlang_only", False)) if d["source"] == "A=B" else d for d in dec]
say("with B values: codes", dict(C_(d["code"] for d in decB if d["decision"] == "exclude")), "i1", dict(C_(d["i1"] for d in decB if d["decision"] == "include")),
    "nonlang", sum(1 for d in decB if d["decision"] == "include" and d["nonlang_only"]))
# agreement: own formulas
def kap(pairs):
    n = len(pairs); po = sum(a == b for a, b in pairs) / n
    ma, mb = C_(a for a, _ in pairs), C_(b for _, b in pairs)
    pe = sum(ma[k] * mb[k] for k in set(ma) | set(mb)) / n ** 2
    return po, (po - pe) / (1 - pe)
def ac1(pairs):
    n = len(pairs); cats = {x for p in pairs for x in p}; q = len(cats); po = sum(a == b for a, b in pairs) / n
    pe = sum(((sum(a == k for a, _ in pairs) + sum(b == k for _, b in pairs)) / (2 * n)) * (1 - (sum(a == k for a, _ in pairs) + sum(b == k for _, b in pairs)) / (2 * n)) for k in cats) / (q - 1)
    return (po - pe) / (1 - pe)
def boot(pairs, B_=2000, seed=20261024):
    rng = random.Random(seed); ks = []
    for _ in range(B_):
        s = [pairs[rng.randrange(len(pairs))] for _ in pairs]; ks.append(kap(s)[1])
    ks.sort(); return round(ks[int(0.025 * B_)], 4), round(ks[int(0.975 * B_) - 1], 4)
def boot_np(pairs, B_=2000, seed=20261024):   # different resampler (choices): robustness only
    rng = random.Random(seed + 1); ks = sorted(kap(rng.choices(pairs, k=len(pairs)))[1] for _ in range(B_))
    return round(ks[49], 4), round(ks[1949], 4)
AG = json.load(open(SCR / "agreement-ft-t1.json", encoding="utf8"))
three = [(A[i]["decision"], B[i]["decision"]) for i in ids]
sets = {"pass_vs_exclude": [(a != "exclude", b != "exclude") for a, b in three], "include_vs_not": [(a == "include", b == "include") for a, b in three], "three_way": three}
for k, pr in sets.items():
    po, kk = kap(pr); f = AG[k]
    line = [k, len(pr), round(po, 4), round(kk, 4), round(ac1(pr), 4), boot(pr), boot_np(pr), "| filed", f["n"], f["raw_agreement"], f["kappa"], f["ac1"], f["kappa_ci95"]]
    if k != "three_way":
        a = sum(x and y for x, y in pr); d = sum((not x) and (not y) for x, y in pr); b = sum(x and not y for x, y in pr); c = sum((not x) and y for x, y in pr)
        n = len(pr); mineb = dict(both_pos=a, both_neg=d, A_only_pos=b, B_only_pos=c, p_pos=round(2 * a / (2 * a + b + c), 4), p_neg=round(2 * d / (2 * d + b + c), 4), bias_index=round(abs(b - c) / n, 4), prevalence_index=round(abs(a - d) / n, 4))
        line += ["2x2 equal", all(f[x] == v for x, v in mineb.items()), mineb]
    else:
        line += ["table equal", {f"{a}|{b}": n for (a, b), n in C_(three).items()} == f["table_A_by_B"]]
    say(*line)
for who, D in (("A", A), ("B", B)):
    c = C_(D[i]["decision"] for i in ids)
    say("per", who, dict(c), round(c["adjudicate"] / len(ids), 4), dict(C_(D[i]["code"] for i in ids if D[i]["decision"] == "exclude")),
        "filed eq", dict(c) == AG["per_screener"][who]["decisions"] and dict(C_(D[i]["code"] for i in ids if D[i]["decision"] == "exclude")) == AG["per_screener"][who]["exclude_codes"])
say("C_queue filed", AG["C_queue"], "sent_to_C", AG["sent_to_C"], "mine", len(dis))
jx = [i for i in ids if A[i]["decision"] == B[i]["decision"] == "exclude"]
cp = [(A[i]["code"], B[i]["code"]) for i in jx]
say("joint excl", len(jx), sum(a == b for a, b in cp), round(kap(cp)[1], 4), round(ac1(cp), 4), "filed", AG["codes_on_joint_exclusions"]["n"], AG["codes_on_joint_exclusions"]["same_code"], AG["codes_on_joint_exclusions"]["kappa"], AG["codes_on_joint_exclusions"]["ac1"],
    "table eq", {f"{a}|{b}": n for (a, b), n in C_(cp).items()} == AG["codes_on_joint_exclusions"]["table_A_by_B"],
    "xsub", sum(A[i]["code"] == B[i]["code"] and A[i].get("xsub", "") == B[i].get("xsub", "") for i in jx), AG["codes_on_joint_exclusions"]["same_code_and_xsub"])
ji = [i for i in ids if A[i]["decision"] == B[i]["decision"] == "include"]
ip = [(A[i].get("i1", ""), B[i].get("i1", "")) for i in ji]
say("joint incl", len(ji), sum(a == b for a, b in ip), round(kap(ip)[1], 4), round(ac1(ip), 4), "filed", AG["joint_inclusions"]["n"], AG["joint_inclusions"]["i1"]["same"], AG["joint_inclusions"]["i1"]["kappa"], AG["joint_inclusions"]["i1"]["ac1"])
# per-rule citations
rules = sorted({x for D in (A, B) for i in ids for x in D[i].get("rules", [])})
bad = []
for ru in rules:
    pr = [(ru in A[i].get("rules", []), ru in B[i].get("rules", [])) for i in ids]
    ca, cb, cboth = sum(a for a, _ in pr), sum(b for _, b in pr), sum(a and b for a, b in pr)
    f = AG["per_rule_citation"]["rules"].get(ru)
    if not f or (f["cited_A"], f["cited_B"], f["cited_both"]) != (ca, cb, cboth) or abs(f["kappa"] - round(kap(pr)[1], 4)) > 1e-4: bad.append((ru, ca, cb, cboth, round(kap(pr)[1], 4), f))
say("per-rule mismatches", bad, "rules", len(rules), len(AG["per_rule_citation"]["rules"]))
# K
smp = SCR / "ta-recheck-sample-v1.3-frozen.json"
say("sample sha", hashlib.sha256(smp.read_bytes()).hexdigest())
sids = json.load(open(smp, encoding="utf8"))["ids"]
dd = {d["id"]: d for d in dec}
inc = sorted(i for i in sids if i in dd and dd[i]["decision"] == "include"); exc = [i for i in sids if i in dd and dd[i]["decision"] == "exclude"]
nin = sorted(i for i in sids if i not in dd)
KF = json.load(open(SCR / "ta-recheck-k.json", encoding="utf8"))
say("K", len(inc), inc, "excl", len(exc), "not in T1", len(nin), "| filed", KF["K"], KF["counts"], "lists eq", [r["id"] for r in KF["included"]] == inc and sorted(r["id"] for r in KF["excluded"]) == sorted(exc) and KF["not_in_T1"] == nin,
    "included detail eq", all(r == {"id": i, "source": dd[i]["source"], "code": dd[i]["code"], "batch": dd[i]["batch"]} for r, i in zip(KF["included"], inc)),
    "excluded detail eq", all(r == {"id": r["id"], "source": dd[r["id"]]["source"], "code": dd[r["id"]]["code"], "batch": dd[r["id"]]["batch"]} for r in KF["excluded"]))
say("pending in sample", [i for i in pend if i in sids])
# recheck boxes / C8
extra = {r["id"]: r for r in jl(SCR / "ft-routes-extra.jsonl")}
c8 = [i for i, r in extra.items() if "c8" in r["group"].split("+")]
smpx = [i for i, r in extra.items() if "recheck-sample" in r["group"].split("+")]
c8f = {r["id"] for r in jl(SCR / "ta-recheck-c8-candidates-v1.4.jsonl")}
say("c8 extra", len(c8), "c8 file", len(c8f), "equal", set(c8) == c8f, "sample extra", len(smpx), "== sample", set(smpx) == set(sids))
for nm, grp in (("sample", smpx), ("c8", c8)):
    say(nm, "n", len(grp), "screened", sum(i in dd for i in grp), "inc", sum(i in dd and dd[i]["decision"] == "include" for i in grp), "exc", sum(i in dd and dd[i]["decision"] == "exclude" for i in grp),
        "not decided", sorted(i for i in grp if i not in dd), "pending among", sorted(i for i in grp if i in pend))
say("pending groups", {i: extra.get(i, {}).get("group") for i in pend}, "pending batch", {i: bo.get(i) for i in pend})
say("recheck full_text_screened", sum(1 for i, r in extra.items() if r["group"] != "ta-pass-unrouted" and i in dd), "to_full_text", sum(1 for r in extra.values() if r["group"] != "ta-pass-unrouted"))
# PRISMA T1 fields
P = json.load(open(R / "analysis/prisma/prisma-flow.json", encoding="utf8"))
ft = {r["id"]: r for r in jl(R / "research/review/fulltext/ft-routes.jsonl")}
fetch, got = {}, set()
for r in jl(R / "research/review/fulltext/fetch-log.jsonl"):
    fetch[r["id"]] = r["status"]
    if r["status"] == "ok" and (R / f"research/sources/md/fulltext-pymupdf/{r['id']}.txt").exists(): got.add(r["id"])
nr = {r["id"] for r in jl(FT / "t1-not-retrieved.jsonl")}
st = C_()
for i, r in ft.items():
    if i in dd: st["screened"] += 1
    elif i in nr: st["nr"] += 1
    elif i in got: st["retrieved_not_yet"] += 1
    else: st[r["route_type"] + ":" + str(fetch.get(i))] += 1
ex = C_(("retrieved_not_yet" if i in got else "pending_" + r["route_type"]) for i, r in extra.items() if i not in dd)
say("ft-routes status", dict(st), "extra", dict(ex), "which retrieved_not_yet in extra", sorted(i for i, r in extra.items() if i not in dd and i in got))
say("ft-routes dup", sum(1 for r in ft.values() if r["route_type"] == "duplicate"), "reports_sought", len(ft) - sum(1 for r in ft.values() if r["route_type"] == "duplicate") + len(extra))
T = P["full_text_T1"]
say("PRISMA filed", {k: T[k] for k in ("reports_sought", "screened", "include", "exclude", "exclude_codes", "include_i1", "include_nonlang_only", "adjudicated_by_C", "agreement_pass_exclude_kappa", "agreement_pass_exclude_kappa_ci95")}, T["status_ft_routes"], T["status_ft_routes_extra"])
say("PRISMA recheck", {k: P["recheck"][k] for k in ("to_full_text", "full_text_screened")}, json.dumps(P["recheck"]["boxes"]))
say("PRISMA K", P["recheck"]["K"]["K"], P["recheck"]["K"]["counts"])
say("PRISMA mentions pending:", [k for k in json.dumps(P).split('"') if "pend" in k.lower() and "B" in k], "open mentions M13184:", any("M13184" in o or "B unavailable" in o or "pending-B" in o for o in P["open"]))
say("PRISMA awaiting B (extra status)", T["status_ft_routes_extra"].get("awaiting_second_screener_B_unavailable"), "c8 box awaiting", P["recheck"]["boxes"]["c8"].get("awaiting_second_screener"), "== pending", sorted(P["recheck"]["boxes"]["c8"].get("awaiting_second_screener", [])) == sorted(pend))
say("PRISMA open lines citing D0035-D0041", [d for d in ("D0035","D0036","D0037","D0041") if any(d in o for o in P["open"])], "status", T.get("status"))
# provenance
prov = jl(FT / "t1-provenance.jsonl")
ok = {}
for r in jl(R / "research/review/fulltext/fetch-log.jsonl"):
    if r.get("status") == "ok": ok[r["id"]] = r
pdiff = [p["id"] for p in prov if (ok.get(p["id"], {}).get("route", "no ok fetch-log entry"), ok.get(p["id"], {}).get("sha256")) != (p["route"], p["pdf_sha256"])]
say("provenance rows", len(prov), "ids == FA ids", {p["id"] for p in prov} == set(A), "decided ids covered", set(dd) <= {p["id"] for p in prov}, "dup ids", len(prov) - len({p["id"] for p in prov}), "diffs", pdiff[:5], "routes", dict(C_(p["route"] for p in prov)), "pending have fetch-ok", {i: ok.get(i, {}).get("route") for i in pend})
open(Path(__file__).with_suffix(".out.txt"), "w", encoding="utf8").write("\n".join(out))
