"""Agreement between the two codings of the random-sample census (codebook v1 + v1.1).

Coder B: research/review/census/coder-B.jsonl (Codex, ranks 1-91) plus coder-B-claude-*.jsonl
(Claude Opus, from rank 92; D0015). Coder A: coder-A-claude-*.jsonl (Claude Sonnet, blind).
Agreement and Cohen's kappa are computed before any reconciliation, on ranks both coders coded.
Writes research/review/census/disagreements-random.csv (one row per rank and field that differ)
and prints the census headline counts under each coder.

    python analysis/census/agreement_random.py [--upto RANK]
"""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

CEN = Path(__file__).resolve().parents[2] / "research" / "review" / "census"


def load(paths):
    rows = {}
    for p in paths:
        for line in open(p, encoding="utf8"):
            if line.strip():
                d = json.loads(line)
                rows[int(d["rank"])] = d
    return rows


def elig(d):
    v = str(d.get("eligible", "")).strip().lower()
    return {"y": "yes", "yes": "yes", "n": "no", "no": "no"}.get(v, "NA")


def letters(d):
    # tokens joined by "+": "G+NS" is {G}, not {G, S} (bug in the first run, fixed 2026-10-15)
    s = (d.get("F2_codes") or "").strip()
    return {t.strip() for t in re.split(r"\+", s)} & set("ATPSGMC")


def nonplain(d):
    """headline uses a non-plain value rule: yes / no / unknown (NS, NA)"""
    s = (d.get("F2_codes") or "").strip()
    if s in ("NS", "NA", ""):
        return "unknown"
    return "no" if s == "U" else "yes"


def norm(v):
    v = (v or "").strip().lower()
    return {"yes": "yes", "no": "no", "partial": "partial", "stated": "stated",
            "not stated": "not stated", "na": "NA", "": "NA"}.get(v, v)


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return float("nan"), float("nan"), 0
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return po, (po - pe) / (1 - pe) if pe < 1 else float("nan"), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--upto", type=int, default=None)
    ap.add_argument("--exclude", default="", help="comma-separated ranks to leave out (e.g. coder read failures)")
    ap.add_argument("--out", default="disagreements-random.csv")
    a = ap.parse_args()
    excl = {int(x) for x in a.exclude.split(",") if x.strip()}
    B = load([CEN / "coder-B.jsonl", *sorted(CEN.glob("coder-B-claude-*.jsonl"))])
    A = load(sorted(CEN.glob("coder-A-claude-*.jsonl")))
    ranks = sorted(r for r in set(A) & set(B) if (a.upto is None or r <= a.upto) and r not in excl)
    ranks = [r for r in ranks if A[r].get("exclusion_code") != "NO_TEXT" and B[r].get("exclusion_code") != "NO_TEXT"]
    print(f"coder B rows {len(B)} (eligible {sum(elig(d) == 'yes' for d in B.values())}); "
          f"coder A rows {len(A)}; ranks both coded with text: {len(ranks)}")

    out, dis = [], []
    out.append(("eligible (yes/no)", *kappa([(elig(A[r]), elig(B[r])) for r in ranks])))
    both = [r for r in ranks if elig(A[r]) == elig(B[r]) == "yes"]
    out.append(("non-plain value rule (yes/no/unknown)", *kappa([(nonplain(A[r]), nonplain(B[r])) for r in both])))
    det = [r for r in both if "unknown" not in (nonplain(A[r]), nonplain(B[r]))]
    out.append(("non-plain value rule, both determinable", *kappa([(nonplain(A[r]), nonplain(B[r])) for r in det])))
    out.append(("value rule determinable (not NS/NA)",
                *kappa([(nonplain(A[r]) != "unknown", nonplain(B[r]) != "unknown") for r in both])))
    for L in "ATPSGM":
        out.append((f"class {L} present (both determinable)", *kappa([(L in letters(A[r]), L in letters(B[r])) for r in det])))
    for f, name in (("F3", "F3 diversity paired"), ("F4", "F4 step sweep"), ("F5", "F5 rule fixed stated"),
                    ("F6", "F6")):
        out.append((name, *kappa([(norm(A[r].get(f)), norm(B[r].get(f))) for r in both])))

    print(f"\n{'field':45s} {'agree':>6s} {'kappa':>6s} {'n':>4s}")
    for name, po, k, n in out:
        print(f"{name:45s} {po:6.2f} {k:6.2f} {n:4d}")

    for r in ranks:
        fields = [("eligible", elig(A[r]), elig(B[r]))]
        if r in both:
            fields += [("nonplain", nonplain(A[r]), nonplain(B[r])),
                       ("F2_codes", A[r].get("F2_codes"), B[r].get("F2_codes"))]
            fields += [(f, norm(A[r].get(f)), norm(B[r].get(f))) for f in ("F3", "F4", "F5", "F6")]
        for f, va, vb in fields:
            if va != vb:
                dis.append({"rank": r, "sid": A[r].get("sid"), "arxiv": A[r].get("arxiv"), "field": f,
                            "coder_A": va, "coder_B": vb, "coder_B_source": B[r].get("coder", "B-codex")})
    with open(CEN / a.out, "w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, fieldnames=["rank", "sid", "arxiv", "field", "coder_A", "coder_B", "coder_B_source"])
        w.writeheader()
        w.writerows(dis)
    print(f"\n{len(dis)} disagreements written to {a.out}")

    for name, C in (("coder A", A), ("coder B", B)):
        el = [d for r, d in C.items() if r in set(ranks) and elig(d) == "yes"]
        print(f"{name}: eligible {len(el)}; headline non-plain {dict(Counter(nonplain(d) for d in el))}; "
              f"F3 {dict(Counter(norm(d.get('F3')) for d in el))}; F4 {dict(Counter(norm(d.get('F4')) for d in el))}; "
              f"F5 {dict(Counter(norm(d.get('F5')) for d in el))}")


if __name__ == "__main__":
    main()
