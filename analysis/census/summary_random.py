"""Census counts on the adjudicated random sample (codebook v1.2; D0020, D0021).

Reads research/review/census/census-random-final.jsonl (harmonised merge; the per-half files if the
merge is absent). Prints the headline counts on the final rows and, as a sensitivity, on rows where
every cell both coders agreed on (coder files, normalised) is restored to the agreed value.

Denominators (codebook v1.2 B-28, gate audit 2026-10-15 C1): the value rule (F2) is counted on
eligible rows with an F2 code, which includes samples-only (QL) rows; F3 to F6 are counted on
eligible rows with a generated-sample metric.

    python analysis/census/summary_random.py
"""
import json
from collections import Counter
from pathlib import Path

CEN = Path(__file__).resolve().parents[2] / "research" / "review" / "census"


def load(paths):
    out = {}
    for p in paths:
        for line in open(p, encoding="utf8"):
            if line.strip():
                d = json.loads(line)
                out[int(d["rank"])] = d
    return out


merged = CEN / "census-random-final.jsonl"
rows = load([merged] if merged.exists() else sorted(CEN.glob("census-random-final-r*.jsonl")))
A = load(sorted(CEN.glob("coder-A-claude-*.jsonl")))
B = load([CEN / "coder-B.jsonl", *sorted(CEN.glob("coder-B-claude-*.jsonl"))])


def low(v):
    return (str(v) if v is not None else "").strip().lower()


def norm(f, v):
    v = low(v)
    if f == "eligible":
        return {"y": "yes", "yes": "yes", "n": "no", "no": "no"}.get(v, "NA")
    return "NA" if v in ("", "na") else v


def isna(v):
    return low(v) in ("", "na", "ql")


def restored(r, d):
    """sensitivity: every cell coder A and coder B agreed on (after normalisation) takes the agreed value"""
    d = dict(d)
    a, b = A.get(r), B.get(r)
    if not a or not b or d.get("exclusion_code") == "NO_TEXT":
        return d
    for f in ("eligible", "exclusion_code", "F2_codes", "F3", "F4", "F5", "F6"):
        if norm(f, a.get(f)) == norm(f, b.get(f)):
            d[f] = norm(f, a.get(f)) if f in ("eligible",) else a.get(f)
    # F1: agreement on whether a generated-sample metric exists
    if isna(a.get("F1_metric")) == isna(b.get("F1_metric")) and isna(d.get("F1_metric")) != isna(a.get("F1_metric")):
        d["F1_metric"] = a.get("F1_metric")
    # a row restored to eligible whose F2 the coders disputed and the final row left NA: count as NS
    if low(d.get("eligible")) == "yes" and isna(d.get("F2_codes")) and not isna(d.get("F1_metric")):
        d["F2_codes"] = "NS"
    return d


def toks(s):
    return {t.strip() for t in (s or "").split("+")}


def nonplain(d):
    s = (d.get("F2_codes") or "").strip()
    if s in ("NA", ""):
        return "NA"
    if s == "U":
        return "no"
    if toks(s) & set("ATPSGMC"):
        return "yes"
    return "unknown"   # NS only


def wilson(k, n, z=1.959964):
    if n == 0:
        return "n=0"
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / (1 + z * z / n)
    return f"{k}/{n} = {p:.3f} [95% Wilson {c - h:.3f}, {c + h:.3f}]"


def report(name, R):
    el = [d for d in R if low(d.get("eligible")) == "yes"]
    v = [d for d in el if nonplain(d) != "NA"]                       # value-rule denominator (incl. QL)
    m = [d for d in el if not isna(d.get("F1_metric"))]              # F3-F6 denominator
    np_ = Counter(nonplain(d) for d in v)
    sweeps = [d for d in m if low(d.get("F4")) in ("yes", "partial")]
    print(f"\n== {name}")
    print(f"ranks {len(R)}; no text {sum(d.get('exclusion_code') == 'NO_TEXT' for d in R)}; "
          f"eligible {len(el)}; excluded {dict(Counter(d.get('exclusion_code') for d in R if low(d.get('eligible')) == 'no'))}")
    print(f"value-rule denominator (eligible with an F2 code, incl. QL): {len(v)}; "
          f"QL (F2 coded, no metric): {sum(isna(d.get('F1_metric')) for d in v)}; "
          f"F3-F6 denominator (eligible with a metric): {len(m)}; eligible with no F2 code: {len(el) - len(v)}")
    print(f"headline value rule: non-plain {np_['yes']}, plain stated (U) {np_['no']}, not stated (NS) {np_['unknown']}; "
          f"non-plain or not stated {np_['yes'] + np_['unknown']} of {len(v)}")
    letters = Counter(t for d in v for t in toks(d.get("F2_codes")) if t in set("ATPSGMC"))
    print(f"letters (papers with each): {dict(sorted(letters.items()))}; any '+NS' "
          f"{sum('NS' in toks(d.get('F2_codes')) and nonplain(d) == 'yes' for d in v)}")
    print(f"F3 diversity paired with headline: {dict(Counter(low(d.get('F3')) for d in m))}")
    print(f"F4 headline at two or more step settings: {dict(Counter(low(d.get('F4')) for d in m))}")
    print(f"F5 among sweeps: {dict(Counter(low(d.get('F5')) for d in sweeps))}; F6 among sweeps: "
          f"{dict(Counter(low(d.get('F6')) for d in sweeps))}")
    print("proportions (intervals treat ranks as a simple random sample of the census pool):")
    print(f"  non-plain or not stated: {wilson(np_['yes'] + np_['unknown'], len(v))}")
    print(f"  non-plain stated:        {wilson(np_['yes'], len(v))}")
    print(f"  diversity paired (F3):   {wilson(sum(low(d.get('F3')) == 'yes' for d in m), len(m))}")
    print(f"  step settings >= 2 (F4 yes/partial): {wilson(len(sweeps), len(m))}")
    print(f"  rule fixed stated among sweeps (F5): {wilson(sum(low(d.get('F5')) == 'stated' for d in sweeps), len(sweeps))}")


R = [rows[r] for r in sorted(rows)]
print(f"ranks present: {min(rows)}-{max(rows)} ({len(rows)} rows)")
report("final (adjudicated under v1.2)", R)
report("sensitivity: cells both coders agreed on restored", [restored(r, rows[r]) for r in sorted(rows)])
