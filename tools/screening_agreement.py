"""Screening agreement and disagreement list (protocol section 4, steps 3 and 4).

Reads screener-A and screener-B decisions (and, when filled, the human sample) and reports Cohen's
kappa with confusion tables for A vs B, A vs human and B vs human, on the three-way decision and on
the binary "pass to full text" (include or unclear) vs exclude. Writes the list of A-B
disagreements for human resolution to research/review/screening/disagreements.csv.

    python tools/screening_agreement.py
"""
import csv
import json
from collections import Counter
from pathlib import Path

SCR = Path(__file__).resolve().parents[1] / "research" / "review" / "screening"


def load(folder: str) -> dict[str, dict]:
    out = {}
    for f in sorted((SCR / folder).glob("batch-*.jsonl")):
        for line in open(f, encoding="utf8"):
            d = json.loads(line)
            out[d["sid"]] = d
    return out


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan")


def report(name, x, y):
    common = sorted(set(x) & set(y))
    if not common:
        print(f"{name}: no common records")
        return
    three = [(x[s], y[s]) for s in common]
    passed = [(a != "exclude", b != "exclude") for a, b in three]
    po3, k3 = kappa(three)
    po2, k2 = kappa(passed)
    print(f"{name}: n={len(common)}  three-way agree {po3:.3f} kappa {k3:.3f} | pass-to-full-text agree {po2:.3f} kappa {k2:.3f}")
    labels = ["include", "unclear", "exclude"]
    c = Counter(three)
    print("    rows = first, cols = second: " + "  ".join(f"{l[:4]:>5s}" for l in labels))
    for a in labels:
        print(f"    {a:8s}" + " " * 25 + "  ".join(f"{c[(a, b)]:5d}" for b in labels))


A = {s: d["decision"] for s, d in load("screener-A").items()}
B = {s: d["decision"] for s, d in load("screener-B").items()}
print(f"screener A records: {len(A)}; screener B records: {len(B)}")
print("A:", dict(Counter(A.values())), " B:", dict(Counter(B.values())))
report("A vs B", A, B)

H = {}
hfile = SCR / "human-sample.csv"
for r in csv.DictReader(open(hfile, encoding="utf-8-sig")):
    d = (r.get("decision (include/exclude/unclear)") or "").strip().lower()
    if d in ("include", "exclude", "unclear"):
        H[r["sid"]] = d
print(f"human sample decisions filled: {len(H)}")
if H:
    report("A vs human", A, H)
    report("B vs human", B, H)

recs = {json.loads(l)["sid"]: json.loads(l) for l in open(SCR / "records.jsonl", encoding="utf8")}
dA, dB = load("screener-A"), load("screener-B")
rows = [s for s in sorted(set(A) & set(B)) if (A[s] != "exclude") != (B[s] != "exclude")]
with open(SCR / "disagreements.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["sid", "arxiv", "title", "A", "A_code", "A_reason", "B", "B_code", "B_reason", "human_resolution"])
    for s in rows:
        w.writerow([s, recs[s]["arxiv"], recs[s]["title"], dA[s]["decision"], dA[s].get("code", ""),
                    dA[s].get("reason", ""), dB[s]["decision"], dB[s].get("code", ""), dB[s].get("reason", ""), ""])
print(f"pass/exclude disagreements written for human resolution: {len(rows)}")
both_pass = sum(1 for s in set(A) & set(B) if A[s] != "exclude" and B[s] != "exclude")
print(f"records both screeners pass to full text: {both_pass}")
