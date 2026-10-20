"""Decisions, summary and A-B agreement for a later full-text tranche (R797 D0035, S1243 D0037, ...), criteria v1.6
audit copy s4 item 3. Same statistics as agreement_ft_t1.py (which stays frozen for the T1 gate) and the same
decision logic as tools/ft-session/refresh_t1.py, plus the tranche rules of 2026-10-20:

- rows listed in ft-<tranche>/superseded-rows.jsonl ({id, batch, roles}) are skipped (e.g. rows made on a wrong
  file; the record is re-screened in a later batch and only that pair counts);
- C rulings listed in ft-<tranche>/c-superseded.jsonl ({id, group}) are skipped;
- records in ft-<tranche>/<tranche>-pending-B.jsonl (Screener B unavailable, D0041/D0046) are left out of the
  agreement and of the decisions and listed for the human author;
- files with DISCARDED in the name are skipped (isolation failures that were rerun).

Agreement: pass (include or adjudicate; D0030) vs exclude, include vs not, three-way; raw agreement, Cohen's kappa
with a percentile bootstrap interval (B = 2000, seed 20261024), p_pos/p_neg, bias and prevalence indices, Gwet's
AC1; codes on joint exclusions; I1 and nonlang_only on joint inclusions; per-rule citation. Decisions: A=B where
A and B agree on include/exclude, else C's ruling; a record that needs C and has none is listed as awaiting C
(the script does not fail, since tranches are refreshed while C groups run).

    python -I analysis/screening/agreement_ft_tranche.py <tranche, e.g. r797>

Writes ft-<tranche>/<tranche>-decisions-all.jsonl, ft-<tranche>/<tranche>-summary-all.json and
agreement-ft-<tranche>.json. Counts are interim until the tranche's gate audit; nothing here is final.
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
TR = sys.argv[1]
FT = HERE / f"ft-{TR}"
FRAME = HERE / f"{TR}-tranche-ids.txt"
OUT = HERE / f"agreement-ft-{TR}.json"


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if p.exists() else []


SUP_ROWS = {(r["id"], r["batch"], role) for r in jl(FT / "superseded-rows.jsonl") for role in r["roles"]}
SUP_C = {(r["id"], r["group"]) for r in jl(FT / "c-superseded.jsonl")}
PEND = {r["id"]: r for r in jl(FT / f"{TR}-pending-B.jsonl")}


def load(who):
    out, batch = {}, {}
    for p in sorted(FT.glob(f"{TR}b*/F{who}-{TR}b*.jsonl")):
        if "DISCARDED" in p.name:
            continue
        for d in jl(p):
            if (d["id"], p.parent.name, who) in SUP_ROWS:
                continue
            if d["id"] in out:
                raise SystemExit(f"duplicate {who} row for {d['id']} in {p} (not in superseded-rows.jsonl)")
            out[d["id"]] = d; batch[d["id"]] = p.parent.name
    return out, batch


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


def ac1(pairs):
    n = len(pairs)
    cats = sorted({x for p in pairs for x in p}, key=str)
    po = sum(a == b for a, b in pairs) / n
    pi = {k: (sum(a == k for a, _ in pairs) + sum(b == k for _, b in pairs)) / (2 * n) for k in cats}
    q = len(cats)
    pe = sum(p * (1 - p) for p in pi.values()) / (q - 1) if q > 1 else 0
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def binary_stats(pairs):
    a = sum(x and y for x, y in pairs); d = sum((not x) and (not y) for x, y in pairs)
    b = sum(x and not y for x, y in pairs); c = sum((not x) and y for x, y in pairs); n = len(pairs)
    return dict(n=n, both_pos=a, both_neg=d, A_only_pos=b, B_only_pos=c,
                p_pos=2 * a / (2 * a + b + c) if a + b + c else None,
                p_neg=2 * d / (2 * d + b + c) if d + b + c else None,
                bias_index=abs(b - c) / n, prevalence_index=abs(a - d) / n)


def boot_kappa(pairs, B=2000, seed=20261024):
    rng = random.Random(seed); ks = []
    for _ in range(B):
        s = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        ks.append(kappa(s)[1])
    ks = sorted(k for k in ks if k == k)
    return ks[int(0.025 * len(ks))], ks[int(0.975 * len(ks)) - 1]


def summary(pairs):
    po, k = kappa(pairs); lo, hi = boot_kappa(pairs)
    return dict(n=len(pairs), raw_agreement=po, kappa=k, kappa_ci95=[lo, hi], ac1=ac1(pairs))


def rnd(x):
    if isinstance(x, float):
        return round(x, 4)
    if isinstance(x, dict):
        return {k: rnd(v) for k, v in x.items()}
    if isinstance(x, list):
        return [rnd(v) for v in x]
    return x


(A, bo), (B, _) = load("A"), load("B")
for i in PEND:
    A.pop(i, None); B.pop(i, None)
ids = sorted(set(A) & set(B))
C = {}
for f in sorted(FT.glob(f"c/c-{TR}-*/FC-*.jsonl")):
    for r in jl(f):
        if (r["id"], f.parent.name) not in SUP_C:
            C[r["id"]] = r

# ---------------------------------------------------------------- decisions and summary
needs_c = lambda i: A[i]["decision"] != B[i]["decision"] or "adjudicate" in (A[i]["decision"], B[i]["decision"])
awaiting_c = sorted(i for i in ids if needs_c(i) and i not in C)
rows = []
for i in ids:
    if i in awaiting_c:
        continue
    src = "C" if needs_c(i) else "A=B"
    r = C[i] if src == "C" else A[i]
    rows.append({"id": i, "batch": bo[i], "decision": r["decision"], "code": r.get("code", ""), "xsub": r.get("xsub", ""),
                 "i1": r.get("i1", ""), "nonlang_only": r.get("nonlang_only", False), "source": src,
                 "A": A[i]["decision"], "B": B[i]["decision"]})
with open(FT / f"{TR}-decisions-all.jsonl", "w", encoding="utf-8", newline="\n") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
frame = [l.strip() for l in open(FRAME, encoding="utf-8") if l.strip()] if FRAME.exists() else []
held = {r["id"] for r in jl(FT / "held-texts.jsonl")}
seen = set(A) | set(B) | set(PEND)
batches = sorted(set(bo.values()))
s = {"tranche": TR, "scope": f"{TR} full-text model screening, batches {batches[0] if batches else '-'}-{batches[-1] if batches else '-'}",
     "status": "INTERIM: screened so far; A-B rows, C rulings filed so far; before the tranche gate audit and the human "
               "author review (protocol s4 step 4); not final",
     "frame": len(frame), "screened_A_and_B": len(ids), "decided": len(rows), "awaiting_C": awaiting_c,
     "pending_B_unavailable": sorted(PEND), "held_texts": sorted(held - seen),
     "frame_not_yet_screened": len(set(frame) - seen) if frame else None,
     "superseded_rows_skipped": sorted({f"{i}@{b}:{r}" for i, b, r in SUP_ROWS}),
     "decision": dict(Counter(r["decision"] for r in rows)),
     "source": dict(Counter(r["source"] for r in rows)),
     "exclude_codes": dict(Counter(r["code"] for r in rows if r["decision"] == "exclude")),
     "include_i1": dict(Counter(r["i1"] for r in rows if r["decision"] == "include")),
     "include_nonlang_only": sum(1 for r in rows if r["decision"] == "include" and r["nonlang_only"]),
     "C_rulings_used": sum(1 for r in rows if r["source"] == "C"),
     "files": f"{TR}-decisions-all.jsonl; c-queue-*.jsonl; c/c-{TR}-*; batch-log.jsonl; superseded-rows.jsonl; "
              f"held-texts.jsonl; agreement-ft-{TR}.json"}
json.dump(s, open(FT / f"{TR}-summary-all.json", "w", encoding="utf-8", newline="\n"), indent=1)

# ---------------------------------------------------------------- agreement (before adjudication)
res = {"scope": f"{TR} full-text, screeners A vs B before adjudication (criteria v1.6 A s4 item 3); INTERIM",
       "files": f"analysis/screening/ft-{TR}/{TR}b*/F{{A,B}}-{TR}b*.jsonl; DISCARDED files, superseded rows and "
                f"B-unavailable records excluded",
       "rows": {"A": len(A), "B": len(B), "both": len(ids),
                "A_only_ids": sorted(set(A) - set(B)), "B_only_ids": sorted(set(B) - set(A)),
                "pending_B_unavailable": sorted(PEND)},
       "bootstrap": {"B": 2000, "seed": 20261024, "type": "percentile"}}
three = [(A[i]["decision"], B[i]["decision"]) for i in ids]
bpass = [(A[i]["decision"] != "exclude", B[i]["decision"] != "exclude") for i in ids]
binc = [(A[i]["decision"] == "include", B[i]["decision"] == "include") for i in ids]
res["pass_vs_exclude"] = {**summary(bpass), **binary_stats(bpass),
                          "note": "pass = include or adjudicate (D0030); positive = pass"}
res["include_vs_not"] = {**summary(binc), **binary_stats(binc),
                         "note": "sensitivity: adjudicate counted with exclude; positive = include"}
res["three_way"] = {**summary(three),
                    "table_A_by_B": {f"{a}|{b}": n for (a, b), n in sorted(Counter(three).items())}}
res["per_screener"] = {}
for who, D in (("A", A), ("B", B)):
    c = Counter(D[i]["decision"] for i in ids)
    res["per_screener"][who] = {"decisions": dict(c), "adjudicate_rate": c["adjudicate"] / len(ids),
                                "exclude_codes": dict(Counter(D[i]["code"] for i in ids if D[i]["decision"] == "exclude"))}
res["sent_to_C"] = sum(a != b or "adjudicate" in (a, b) for a, b in three)
cq = [r for p in sorted(FT.glob("c-queue-*.jsonl")) for r in jl(p)]
dis = {i for i in ids if needs_c(i)}
cqi = {r["id"] for r in cq}
res["C_queue"] = {"rows": len(cq), "unique": len(cqi), "disagreement_or_adjudicate": len(dis & cqi),
                  "disagreement_or_adjudicate_not_queued": sorted(dis - cqi),
                  "queued_for_quote_check_only": len(cqi - dis),
                  "quote_only_reasons": dict(Counter(w for r in cq if r["id"] not in dis for w in r.get("why", [])))}
jx = [i for i in ids if A[i]["decision"] == "exclude" and B[i]["decision"] == "exclude"]
cp = [(A[i]["code"], B[i]["code"]) for i in jx]
res["codes_on_joint_exclusions"] = {
    "n": len(jx), "same_code": sum(a == b for a, b in cp),
    "kappa": kappa(cp)[1] if jx else None, "ac1": ac1(cp) if jx else None,
    "table_A_by_B": {f"{a}|{b}": n for (a, b), n in sorted(Counter(cp).items())},
    "same_code_and_xsub": sum(A[i]["code"] == B[i]["code"] and A[i].get("xsub", "") == B[i].get("xsub", "") for i in jx)}
ji = [i for i in ids if A[i]["decision"] == "include" and B[i]["decision"] == "include"]
ip = [(A[i].get("i1", ""), B[i].get("i1", "")) for i in ji]
nl = [(bool(A[i].get("nonlang_only")), bool(B[i].get("nonlang_only"))) for i in ji]
res["joint_inclusions"] = {
    "n": len(ji),
    "i1": {"same": sum(a == b for a, b in ip), "kappa": kappa(ip)[1] if ji else None, "ac1": ac1(ip) if ji else None,
           "table_A_by_B": {f"{a}|{b}": n for (a, b), n in sorted(Counter(ip).items())}},
    "nonlang_only": {**(binary_stats(nl) if ji else {}), "A_true": sum(a for a, _ in nl), "B_true": sum(b for _, b in nl)}}
rules = sorted({r for D in (A, B) for i in ids for r in (D[i].get("rules") or [])})
per_rule = {}
for r in rules:
    pr = [(r in (A[i].get("rules") or []), r in (B[i].get("rules") or [])) for i in ids]
    st = binary_stats(pr); po, k = kappa(pr)
    per_rule[r] = {"cited_A": st["both_pos"] + st["A_only_pos"], "cited_B": st["both_pos"] + st["B_only_pos"],
                   "cited_both": st["both_pos"], "p_pos": st["p_pos"], "kappa": k}
res["per_rule_citation"] = {"note": "presence of the rule id in each screener's rules field, all records", "rules": per_rule}
res = rnd(res)
OUT.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
p, i3 = res["pass_vs_exclude"], res["three_way"]
print(json.dumps({k: v for k, v in s.items() if k not in ("files", "superseded_rows_skipped")}))
print(f"pass/exclude n {p['n']} raw {p['raw_agreement']} kappa {p['kappa']} {p['kappa_ci95']} AC1 {p['ac1']}")
print(f"three-way raw {i3['raw_agreement']} kappa {i3['kappa']} table {i3['table_A_by_B']}")
print("C queue", res["C_queue"])
