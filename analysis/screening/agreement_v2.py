"""Screening agreement for the 2026-10-15 search update (D0026-D0029), before reconciliation.

Screeners A (Claude Sonnet) and B (Claude Opus) on research/review/screening/v2/batch-*.jsonl.
Reports, for pass (include or unclear) vs exclude and for the three-way decision: raw agreement,
Cohen's kappa with a percentile bootstrap interval (B = 2000, seed 20261024), positive and negative
agreement (p_pos, p_neg; Cicchetti and Feinstein 1990), bias and prevalence indices (Byrt et al.
1993), Gwet's AC1. Also the rescue screener's (Claude Haiku) agreement with the validation screener
(Claude Sonnet) on the V1 records both screened. Writes disagreements-v2.csv.

    python analysis/screening/agreement_v2.py
"""
import csv
import json
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "research" / "review" / "screening" / "v2"


def load(pattern):
    out = {}
    for p in sorted(V2.glob(pattern)):
        for line in open(p, encoding="utf-8"):
            if line.strip():
                d = json.loads(line)
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
    cats = sorted({x for p in pairs for x in p})
    po = sum(a == b for a, b in pairs) / n
    pi = {k: (sum(a == k for a, _ in pairs) + sum(b == k for _, b in pairs)) / (2 * n) for k in cats}
    q = len(cats)
    pe = sum(p * (1 - p) for p in pi.values()) / (q - 1) if q > 1 else 0
    return (po - pe) / (1 - pe)


def binary_stats(pairs):
    a = sum(x and y for x, y in pairs); d = sum((not x) and (not y) for x, y in pairs)
    b = sum(x and not y for x, y in pairs); c = sum((not x) and y for x, y in pairs); n = len(pairs)
    return dict(n=n, both_pass=a, both_exclude=d, A_only=b, B_only=c,
                p_pos=2 * a / (2 * a + b + c) if a + b + c else float("nan"),
                p_neg=2 * d / (2 * d + b + c) if d + b + c else float("nan"),
                bias_index=abs(b - c) / n, prevalence_index=abs(a - d) / n)


def boot_kappa(pairs, B=2000, seed=20261024):
    rng = random.Random(seed); ks = []
    for _ in range(B):
        s = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        ks.append(kappa(s)[1])
    ks.sort()
    return ks[int(0.025 * B)], ks[int(0.975 * B) - 1]


A, B = load("screener-A-batch-*.jsonl"), load("screener-B-batch-*.jsonl")
ids = sorted(set(A) & set(B))
print(f"A rows {len(A)}, B rows {len(B)}, both {len(ids)}")
three = [(A[i]["decision"], B[i]["decision"]) for i in ids]
bpass = [(A[i]["decision"] != "exclude", B[i]["decision"] != "exclude") for i in ids]
for name, pairs in (("pass vs exclude", bpass), ("three-way", three)):
    po, k = kappa(pairs); lo, hi = boot_kappa(pairs)
    print(f"{name:16s} raw {po:.3f} kappa {k:.3f} [{lo:.3f}, {hi:.3f}] AC1 {ac1(pairs):.3f}")
print("binary detail:", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in binary_stats(bpass).items()})
print("three-way table:", dict(Counter(three)))
for who, D in (("A", A), ("B", B)):
    print(f"screener {who}:", dict(Counter(d["decision"] for d in D.values())))
with open(V2 / "disagreements-v2.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["id", "A_decision", "A_code", "A_reason", "B_decision", "B_code", "B_reason"])
    for i in ids:
        if A[i]["decision"] != B[i]["decision"]:
            w.writerow([i, A[i]["decision"], A[i].get("code", ""), A[i].get("reason", ""),
                        B[i]["decision"], B[i].get("code", ""), B[i].get("reason", "")])
union = sum(A[i]["decision"] != "exclude" or B[i]["decision"] != "exclude" for i in ids)
print(f"records passed by A or B (to full text or adjudication): {union}")

# rescue screener sensitivity on V1 (validation screener as reference)
R, Vd = load("rescue/screener-R-rescue-*.jsonl"), load("screener-V-validation.jsonl")
ov = [i for i in Vd if i in R]
if ov:
    pos = lambda d: d["decision"] != "exclude"
    tp = sum(pos(Vd[i]) and pos(R[i]) for i in ov); fn = sum(pos(Vd[i]) and not pos(R[i]) for i in ov)
    fp = sum(pos(R[i]) and not pos(Vd[i]) for i in ov)
    print(f"rescue vs validation on {len(ov)} V1 records: reference positives {tp + fn}, caught {tp}, missed {fn}, extra {fp}")
    print("rescue decisions:", dict(Counter(d["decision"] for d in R.values())), "rows", len(R))
