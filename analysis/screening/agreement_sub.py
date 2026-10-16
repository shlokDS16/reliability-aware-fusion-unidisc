"""Agreement and D0030 decisions for the subscription-database dual batch (dual-subscription/batch-sub-01.jsonl).

Same statistics as agreement_v2.py (kappa with percentile bootstrap B = 2000, seed 20261024; Gwet's AC1),
for pass (include or unclear) vs exclude and for the three-way decision. D0030: a record passes to full text
if either screener passes it. Writes dual-subscription/disagreements-sub.csv and passed-ta.jsonl.

    python analysis/screening/agreement_sub.py
"""
import csv, json, random, sys
from pathlib import Path

from collections import Counter


# kappa and ac1 copied verbatim from agreement_v2.py (importing it reruns its report)
def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n / n
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


def ac1(pairs):
    n = len(pairs)
    cats = sorted({x for p in pairs for x in p})
    po = sum(a == b for a, b in pairs) / n
    pi = {k: (sum(a == k for a, _ in pairs) + sum(b == k for _, b in pairs)) / (2 * n) for k in cats}
    q = len(cats)
    pe = sum(p * (1 - p) for p in pi.values()) / (q - 1) if q > 1 else 0
    return (po - pe) / (1 - pe)


D = Path(__file__).resolve().parents[2] / "research/review/screening/v2/dual-subscription"
batch = [json.loads(l) for l in open(D / "batch-sub-01.jsonl", encoding="utf-8") if l.strip()]
A = {d["id"]: d for d in map(json.loads, open(D / "screener-A-batch-sub-01.jsonl", encoding="utf-8"))}
B = {d["id"]: d for d in map(json.loads, open(D / "screener-B-batch-sub-01.jsonl", encoding="utf-8"))}
ids = [r["id"] for r in batch]
assert set(ids) == set(A) == set(B) and len(ids) == len(set(ids))
P = lambda d: "pass" if d["decision"] in ("include", "unclear") else "exclude"


def boot(pairs, B_=2000, seed=20261024):
    rng, ks = random.Random(seed), []
    for _ in range(B_):
        s = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        ks.append(kappa(s)[1])
    ks.sort()
    return ks[int(0.025 * B_)], ks[int(0.975 * B_) - 1]


rep = {}
for name, f in (("pass_vs_exclude", P), ("three_way", lambda d: d["decision"])):
    pairs = [(f(A[i]), f(B[i])) for i in ids]
    po, k = kappa(pairs)
    lo, hi = boot(pairs)
    rep[name] = {"n": len(pairs), "raw_agreement": round(po, 4), "kappa": round(k, 4), "kappa_95ci_bootstrap": [round(lo, 4), round(hi, 4)], "ac1": round(ac1(pairs), 4)}
passed = [i for i in ids if P(A[i]) == "pass" or P(B[i]) == "pass"]
both = sum(1 for i in ids if P(A[i]) == "pass" and P(B[i]) == "pass")
rep["d0030"] = {"passed_either": len(passed), "passed_both": both, "passed_one_only": len(passed) - both, "excluded_both": len(ids) - len(passed)}
rows = {r["id"]: r for r in batch}
with open(D / "passed-ta.jsonl", "w", encoding="utf-8") as fh:
    for i in sorted(passed):
        fh.write(json.dumps({**rows[i], "A": A[i]["decision"], "B": B[i]["decision"]}, ensure_ascii=False) + "\n")
with open(D / "disagreements-sub.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["id", "A_decision", "A_code", "A_reason", "B_decision", "B_code", "B_reason", "title"])
    for i in sorted(ids):
        if A[i]["decision"] != B[i]["decision"]:
            w.writerow([i, A[i]["decision"], A[i]["code"], A[i]["reason"], B[i]["decision"], B[i]["code"], B[i]["reason"], rows[i]["title"]])
(D / "agreement-sub.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
print(json.dumps(rep, indent=1))
