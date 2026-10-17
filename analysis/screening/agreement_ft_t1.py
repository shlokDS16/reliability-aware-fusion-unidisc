"""Full-text screening agreement for tranche T1 (criteria v1.6 audit copy s4 item 3), before adjudication.

Screeners A (claude-sonnet-5-5) and B (claude-opus-5-5) on analysis/screening/ft-t1/t1b*/F{A,B}-t1b*.jsonl
(files with DISCARDED in the name are excluded: isolation failures that were rerun). Reports, for pass
(include or adjudicate; D0030's convention) vs exclude, for include vs not include (sensitivity) and for
the three-way decision (include / exclude / adjudicate): raw agreement, Cohen's kappa with a percentile
bootstrap interval (B = 2000, seed 20261024), positive and negative agreement (p_pos, p_neg; Cicchetti and
Feinstein 1990), bias and prevalence indices (Byrt et al. 1993), Gwet's AC1. Also: adjudicate rate per
screener; exclusion-code agreement on joint exclusions; I1 and nonlang_only agreement on joint inclusions;
agreement per rule cited (presence or absence of each rule id in the `rules` field). Writes
agreement-ft-t1.json next to this script.

    python analysis/screening/agreement_ft_t1.py
"""
import json
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
FT = HERE / "ft-t1"
OUT = HERE / "agreement-ft-t1.json"


def load(who):
    out = {}
    for p in sorted(FT.glob(f"t1b*/F{who}-t1b*.jsonl")):
        if "DISCARDED" in p.name:
            continue
        for line in open(p, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
                if d["id"] in out:
                    raise SystemExit(f"duplicate {who} row for {d['id']} in {p}")
                out[d["id"]] = d
    return out


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


A, B = load("A"), load("B")
ids = sorted(set(A) & set(B))
res = {"scope": "T1 full-text, screeners A vs B before adjudication (criteria v1.6 A s4 item 3)",
       "files": "analysis/screening/ft-t1/t1b*/F{A,B}-t1b*.jsonl, DISCARDED files excluded",
       "rows": {"A": len(A), "B": len(B), "both": len(ids),
                "A_only_ids": sorted(set(A) - set(B)), "B_only_ids": sorted(set(B) - set(A))},
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
                                "exclude_codes": dict(Counter(D[i]["code"] for i in ids
                                                              if D[i]["decision"] == "exclude"))}
res["sent_to_C"] = sum(a != b or "adjudicate" in (a, b) for a, b in three)
cq = [json.loads(l) for p in sorted(FT.glob("c-queue-*.jsonl")) for l in open(p, encoding="utf-8") if l.strip()]
dis = {i for i in ids if A[i]["decision"] != B[i]["decision"] or "adjudicate" in (A[i]["decision"], B[i]["decision"])}
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
    "same_code_and_xsub": sum(A[i]["code"] == B[i]["code"] and A[i].get("xsub", "") == B[i].get("xsub", "")
                              for i in jx)}

ji = [i for i in ids if A[i]["decision"] == "include" and B[i]["decision"] == "include"]
ip = [(A[i].get("i1", ""), B[i].get("i1", "")) for i in ji]
nl = [(bool(A[i].get("nonlang_only")), bool(B[i].get("nonlang_only"))) for i in ji]
res["joint_inclusions"] = {
    "n": len(ji),
    "i1": {"same": sum(a == b for a, b in ip), "kappa": kappa(ip)[1], "ac1": ac1(ip),
           "table_A_by_B": {f"{a}|{b}": n for (a, b), n in sorted(Counter(ip).items())}},
    "nonlang_only": {**binary_stats(nl), "A_true": sum(a for a, _ in nl), "B_true": sum(b for _, b in nl)}}
res["nonlang_only_all_rows"] = {w: sum(bool(D[i].get("nonlang_only")) for i in ids) for w, D in (("A", A), ("B", B))}

rules = sorted({r for D in (A, B) for i in ids for r in (D[i].get("rules") or [])})
per_rule = {}
for r in rules:
    pr = [(r in (A[i].get("rules") or []), r in (B[i].get("rules") or [])) for i in ids]
    st = binary_stats(pr); po, k = kappa(pr)
    per_rule[r] = {"cited_A": st["both_pos"] + st["A_only_pos"], "cited_B": st["both_pos"] + st["B_only_pos"],
                   "cited_both": st["both_pos"], "p_pos": st["p_pos"], "kappa": k}
res["per_rule_citation"] = {"note": "presence of the rule id in each screener's rules field, all records",
                            "rules": per_rule}

res = rnd(res)
OUT.write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
p, i3 = res["pass_vs_exclude"], res["three_way"]
print(f"rows A {len(A)} B {len(B)} both {len(ids)}")
print(f"pass/exclude raw {p['raw_agreement']} kappa {p['kappa']} {p['kappa_ci95']} AC1 {p['ac1']} "
      f"p_pos {p['p_pos']} p_neg {p['p_neg']} BI {p['bias_index']} PI {p['prevalence_index']}")
print(f"three-way    raw {i3['raw_agreement']} kappa {i3['kappa']} {i3['kappa_ci95']} AC1 {i3['ac1']}")
print("include/not  ", {k: res['include_vs_not'][k] for k in ('raw_agreement', 'kappa', 'kappa_ci95', 'ac1')})
print("table", i3["table_A_by_B"])
print("C queue", res["C_queue"])
print("adjudicate rate", {w: res["per_screener"][w]["adjudicate_rate"] for w in "AB"}, "sent to C", res["sent_to_C"])
print("joint exclusions", {k: v for k, v in res["codes_on_joint_exclusions"].items() if k != "table_A_by_B"})
print("joint inclusions i1", res["joint_inclusions"]["i1"]["same"], "/", res["joint_inclusions"]["n"],
      "nonlang", res["joint_inclusions"]["nonlang_only"])
print(f"wrote {OUT}")
