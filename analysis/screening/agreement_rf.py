"""Agreement and D0030 decisions for the free-source rescue positives (D0036; dual-rescue-free/batch-rf-*.jsonl).

Same statistics and rule as agreement_sub.py (kappa with percentile bootstrap B = 2000, seed 20261024; Gwet's AC1;
D0030: a record passes to full text if either screener marks it include or unclear). Reads every batch-rf-NN.jsonl
with both screener files present. Writes dual-rescue-free/agreement-rf.json, disagreements-rf.csv, passed-ta-rf.jsonl.

    python -I analysis/screening/agreement_rf.py
"""
import csv, glob, json, random
from pathlib import Path
from collections import Counter


# kappa and ac1 copied verbatim from agreement_sub.py (importing it reruns its report)
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


def boot(pairs, B_=2000, seed=20261024):
    rng, ks = random.Random(seed), []
    for _ in range(B_):
        s = [pairs[rng.randrange(len(pairs))] for _ in pairs]
        ks.append(kappa(s)[1])
    ks.sort()
    return ks[int(0.025 * B_)], ks[int(0.975 * B_) - 1]


D = Path(__file__).resolve().parents[2] / "research/review/screening/v2/dual-rescue-free"
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
man = json.load(open(D / "manifest.json", encoding="utf-8"))
batch, A, B, done = [], {}, {}, []
for name in sorted(man["batches"]):
    stem = name[:-6]
    fa, fb = D / f"screener-A-{stem}.jsonl", D / f"screener-B-{stem}.jsonl"
    if not (fa.exists() and fb.exists()):
        continue
    done.append(stem)
    batch += jl(D / name)
    A.update({d["id"]: d for d in jl(fa)})
    B.update({d["id"]: d for d in jl(fb)})
ids = [r["id"] for r in batch]
assert set(ids) == set(A) == set(B) and len(ids) == len(set(ids))
P = lambda d: "pass" if d["decision"] in ("include", "unclear") else "exclude"
rep = {"batches": done, "batches_pending": [n[:-6] for n in sorted(man["batches"]) if n[:-6] not in done]}
for name, f in (("pass_vs_exclude", P), ("three_way", lambda d: d["decision"])):
    pairs = [(f(A[i]), f(B[i])) for i in ids]
    po, k = kappa(pairs)
    lo, hi = boot(pairs)
    rep[name] = {"n": len(pairs), "raw_agreement": round(po, 4), "kappa": round(k, 4), "kappa_95ci_bootstrap": [round(lo, 4), round(hi, 4)],
                 "ac1": round(ac1(pairs), 4), "table": dict(Counter(f"{a}|{b}" for a, b in pairs))}
passed = [i for i in ids if P(A[i]) == "pass" or P(B[i]) == "pass"]
both = sum(1 for i in ids if P(A[i]) == "pass" and P(B[i]) == "pass")
rep["d0030"] = {"passed_either": len(passed), "passed_both": both, "passed_one_only": len(passed) - both, "excluded_both": len(ids) - len(passed)}
rows = {r["id"]: r for r in batch}
with open(D / "passed-ta-rf.jsonl", "w", encoding="utf-8") as fh:
    for i in sorted(passed):
        fh.write(json.dumps({**rows[i], "A": A[i]["decision"], "B": B[i]["decision"]}, ensure_ascii=False) + "\n")
with open(D / "disagreements-rf.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["id", "A_decision", "A_code", "A_reason", "B_decision", "B_code", "B_reason", "title"])
    for i in sorted(ids):
        if A[i]["decision"] != B[i]["decision"]:
            w.writerow([i, A[i]["decision"], A[i]["code"], A[i]["reason"], B[i]["decision"], B[i]["code"], B[i]["reason"], rows[i]["title"]])
(D / "agreement-rf.json").write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")
print(json.dumps(rep, indent=1))
