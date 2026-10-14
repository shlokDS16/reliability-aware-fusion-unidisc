"""Agreement between the two census codings (framework-v2 D2).

Coder 1: research/review/coverage/design-space-v1.csv (coded before codebook v1; fields mapped).
Coder 2: research/review/coverage/census-coder2.csv (codebook v1, blind to coder 1).
Reports raw agreement and Cohen's kappa per mapped field, on rows both coders could code, plus
the census headline counts under each coder. Mapping choices are printed with the results.
"""
import csv
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "research" / "review" / "coverage"
c1 = {r["id"]: r for r in csv.DictReader(open(ROOT / "design-space-v1.csv", encoding="utf8"))}
c2 = {r["id"]: r for r in csv.DictReader(open(ROOT / "census-coder2.csv", encoding="utf8"))}
CLS = "value-rule classes (A argmax, T low temp, P top-p/k, S sample-then-filter, G guidance, M sequence-level selection)"


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return float("nan"), float("nan"), 0
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan"), n


def letters1(r):
    return set(re.findall(r"\b([ATPSGM])\b", r[CLS] or ""))


def letters2(r):
    s = r["F2_codes"]
    return set() if s in ("NS", "NA", "U", "") else set(s.split("+"))


def headline1(r):
    """coder 1: does the headline use a non-plain value rule? yes / no / unknown"""
    v = (r["headline uses E_sel-type rule"] or "").lower()
    # 'controlled' rows (CANDI, Simplex Relaxation) use temperature below 1 with an entropy frontier: non-plain
    return "yes" if v.startswith(("yes", "controlled")) else ("no" if v.startswith("no") else "unknown")


def headline2(r):
    s = r["F2_codes"]
    if s in ("NS", "NA", ""):
        return "unknown"
    return "no" if s == "U" else "yes"


ids = sorted(set(c1) & set(c2))
out = []
pairs = [(headline1(c1[i]), headline2(c2[i])) for i in ids]
out.append(("non-plain value rule (yes/no/unknown), all rows", *kappa(pairs)))
both = [(a, b) for a, b in pairs if a != "unknown" and b != "unknown"]
out.append(("non-plain value rule, rows both coded yes/no", *kappa(both)))
for L in "ATPSGM":
    pr = [(L in letters1(c1[i]), L in letters2(c2[i])) for i in ids
          if headline1(c1[i]) != "unknown" and headline2(c2[i]) != "unknown"]
    out.append((f"class {L} present (rows both coded)", *kappa(pr)))


def yn1(v):
    v = (v or "").lower()
    return "yes" if v.startswith("yes") else "no" if v.startswith("no") else None


def yn2(v):
    return {"Yes": "yes", "No": "no"}.get(v)


pr = [(yn1(c1[i]["entropy or diversity reported"]), yn2(c2[i]["F3"])) for i in ids]
pr = [p for p in pr if None not in p]
out.append(("entropy or diversity reported (yes/no rows)", *kappa(pr)))


def sw1(v):
    v = (v or "").lower()
    return None if v.startswith(("ns", "qual")) else ("yes" if v.startswith(("yes", "partial")) else "no")


def sw2(v):
    return {"Yes": "yes", "Partial": "yes", "No": "no"}.get(v)


pr = [(sw1(c1[i]["step sweep reported"]), sw2(c2[i]["F4"])) for i in ids]
pr = [p for p in pr if None not in p]
out.append(("step sweep reported (coder 1 'ns' rows excluded)", *kappa(pr)))

print(f"{'field':55s} {'agree':>6s} {'kappa':>6s} {'n':>3s}")
for name, po, k, n in out:
    print(f"{name:55s} {po:6.2f} {k:6.2f} {n:3d}")

pr = [(headline1(c1[i]) != "unknown", headline2(c2[i]) != "unknown") for i in ids]
out2 = kappa(pr)
print(f"{'value rule determinable (not NS/NA/unclear)':55s} {out2[0]:6.2f} {out2[1]:6.2f} {out2[2]:3d}")

h1, h2 = Counter(headline1(c1[i]) for i in ids), Counter(headline2(c2[i]) for i in ids)
print("\ncoder 1 headline non-plain:", dict(h1))
print("coder 2 headline non-plain:", dict(h2))
print("coder 2 F2 codes:", dict(Counter(c2[i]["F2_codes"] for i in ids)))
print("\ndisagreements on non-plain value rule (id, name, coder1, coder2 codes):")
for i in ids:
    a, b = headline1(c1[i]), headline2(c2[i])
    if a != b:
        print(f"  {i} {c1[i]['name'][:28]:28s} c1={a:7s} [{','.join(sorted(letters1(c1[i])))}]  "
              f"c2={b:7s} [{c2[i]['F2_codes']}]")
