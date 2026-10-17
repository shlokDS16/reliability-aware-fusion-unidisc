"""Independent check of agreement-ft-t1.json: recomputes the kappas with scikit-learn's cohen_kappa_score and
the binary AC1 and p_pos/p_neg from the 2 x 2 cell formulas (Gwet 2008; Cicchetti and Feinstein 1990), from
the raw F{A,B} rows, and asserts equality with the JSON to 4 decimals. Exit 0 = all match.

    python analysis/screening/check_agreement_ft_t1.py
"""
import json
from pathlib import Path

from sklearn.metrics import cohen_kappa_score

HERE = Path(__file__).resolve().parent
res = json.loads((HERE / "agreement-ft-t1.json").read_text(encoding="utf-8"))


def rows(who):
    out = {}
    for p in sorted((HERE / "ft-t1").glob(f"t1b*/F{who}-t1b*.jsonl")):
        if "DISCARDED" not in p.name:
            for l in open(p, encoding="utf-8"):
                if l.strip():
                    d = json.loads(l); out[d["id"]] = d
    return out


A, B = rows("A"), rows("B")
ids = sorted(A)
assert ids == sorted(B) and len(ids) == res["rows"]["both"]
a3 = [A[i]["decision"] for i in ids]; b3 = [B[i]["decision"] for i in ids]
checks = []


def eq(name, x, y):
    ok = abs(x - y) < 5e-5
    checks.append((name, round(x, 4), y, ok))


def binary(x, y):
    n = len(x); a = sum(p and q for p, q in zip(x, y)); d = sum((not p) and (not q) for p, q in zip(x, y))
    b = sum(p and not q for p, q in zip(x, y)); c = n - a - b - d
    po = (a + d) / n; q = ((a + b) + (a + c)) / (2 * n); pe = 2 * q * (1 - q)
    return dict(ac1=(po - pe) / (1 - pe), p_pos=2 * a / (2 * a + b + c), p_neg=2 * d / (2 * d + b + c))


ap = [v != "exclude" for v in a3]; bp = [v != "exclude" for v in b3]
eq("pass kappa", cohen_kappa_score(ap, bp), res["pass_vs_exclude"]["kappa"])
for k, v in binary(ap, bp).items():
    eq(f"pass {k}", v, res["pass_vs_exclude"][k])
ai = [v == "include" for v in a3]; bi = [v == "include" for v in b3]
eq("include kappa", cohen_kappa_score(ai, bi), res["include_vs_not"]["kappa"])
eq("include ac1", binary(ai, bi)["ac1"], res["include_vs_not"]["ac1"])
eq("three-way kappa", cohen_kappa_score(a3, b3), res["three_way"]["kappa"])
jx = [i for i in ids if A[i]["decision"] == B[i]["decision"] == "exclude"]
eq("code kappa", cohen_kappa_score([A[i]["code"] for i in jx], [B[i]["code"] for i in jx]),
   res["codes_on_joint_exclusions"]["kappa"])
ji = [i for i in ids if A[i]["decision"] == B[i]["decision"] == "include"]
eq("i1 kappa", cohen_kappa_score([A[i].get("i1", "") for i in ji], [B[i].get("i1", "") for i in ji]),
   res["joint_inclusions"]["i1"]["kappa"])
for c in checks:
    print(*c)
bad = [c for c in checks if not c[3]]
print("all match" if not bad else f"MISMATCH {len(bad)}")
raise SystemExit(1 if bad else 0)
