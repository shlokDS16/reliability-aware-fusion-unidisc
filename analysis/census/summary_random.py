"""Census counts on the adjudicated random sample (codebook v1.2; D0020).

Reads research/review/census/census-random-final-*.jsonl. Prints the headline counts on the final
rows and, as a sensitivity, on rows where every cell both coders agreed on is restored to the
agreed value (undoing the adjudicators' v1.2-triggered changes to agreed cells).

    python analysis/census/summary_random.py
"""
import json
from collections import Counter
from pathlib import Path

CEN = Path(__file__).resolve().parents[2] / "research" / "review" / "census"
rows = {}
merged = CEN / "census-random-final.jsonl"   # harmonised merge of the two halves, when present
for p in [merged] if merged.exists() else sorted(CEN.glob("census-random-final-r*.jsonl")):
    for line in open(p, encoding="utf8"):
        if line.strip():
            d = json.loads(line)
            rows[int(d["rank"])] = d


def restored(d):
    """undo changes to cells where coder A and coder B agreed"""
    d = dict(d)
    for f, a in (d.get("adjudication") or {}).items():
        if isinstance(a, dict) and "A" in a and a.get("A") == a.get("B") and f in d:
            d[f] = a["A"]
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


def low(v):
    return (v or "").strip().lower()


def report(name, R):
    el = [d for d in R if low(d.get("eligible")) == "yes"]
    met = [d for d in el if (d.get("F1_metric") or "NA") != "NA" or low(d.get("F1_task")) == "ql"]
    f2 = [d for d in el if nonplain(d) != "NA" and (d.get("F1_metric") or "NA") != "NA"]
    np_ = Counter(nonplain(d) for d in f2)
    sweeps = [d for d in f2 if low(d.get("F4")) in ("yes", "partial")]
    print(f"\n== {name}")
    print(f"ranks {len(R)}; no text {sum(d.get('exclusion_code') == 'NO_TEXT' for d in R)}; "
          f"eligible {len(el)}; excluded {dict(Counter(d.get('exclusion_code') for d in R if low(d.get('eligible')) == 'no'))}")
    print(f"eligible with a generated-sample metric (F2-F6 denominator): {len(f2)}; F1 NA: "
          f"{sum((d.get('F1_metric') or 'NA') == 'NA' for d in el)}")
    print(f"headline value rule: non-plain {np_['yes']}, plain stated (U) {np_['no']}, not stated (NS) {np_['unknown']}; "
          f"non-plain or not stated {np_['yes'] + np_['unknown']} of {len(f2)}")
    letters = Counter(t for d in f2 for t in toks(d.get("F2_codes")) if t in set("ATPSGMC"))
    print(f"letters (papers with each): {dict(sorted(letters.items()))}; any '+NS' {sum('NS' in toks(d.get('F2_codes')) and nonplain(d) == 'yes' for d in f2)}")
    print(f"F3 diversity paired with headline: {dict(Counter(low(d.get('F3')) for d in f2))}")
    print(f"F4 step sweep: {dict(Counter(low(d.get('F4')) for d in f2))}")
    print(f"F5 among sweeps: {dict(Counter(low(d.get('F5')) for d in sweeps))}; F6 among sweeps: "
          f"{dict(Counter(low(d.get('F6')) for d in sweeps))}")


R = [rows[r] for r in sorted(rows)]
print(f"ranks present: {min(rows)}-{max(rows)} ({len(rows)} rows)")
report("final (adjudicated under v1.2)", R)
report("sensitivity: agreed cells restored", [restored(d) for d in R])
