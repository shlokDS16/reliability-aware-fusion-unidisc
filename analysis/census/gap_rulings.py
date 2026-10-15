"""Effect of codebook v1.2 gap rulings on the census counts (D0020(3); gate audit C9).

For each v1.2 item tagged [gap] (and B-10, disclosed as a judgement call), lists the ranks whose
adjudication or harmonisation basis cites it and bounds its effect: the number of those ranks in
each headline numerator is the most that numerator could fall if the ruling went the other way.

    python analysis/census/gap_rulings.py
"""
import json
import re
from collections import defaultdict
from pathlib import Path

CEN = Path(__file__).resolve().parents[2] / "research" / "review" / "census"
GAP = ["B-3", "B-4", "B-6", "B-8", "B-9", "B-10", "B-13", "B-15", "B-17", "B-18", "B-19", "B-21", "B-22", "B-24"]
rows = [json.loads(l) for l in open(CEN / "census-random-final.jsonl", encoding="utf8") if l.strip()]


def toks(s):
    return {t.strip() for t in (s or "").split("+")}


def cls(d):
    s = (d.get("F2_codes") or "").strip()
    if s in ("NA", "") or str(d.get("eligible")).lower() != "yes":
        return None
    return "U" if s == "U" else ("nonplain" if toks(s) & set("ATPSGMC") else "NS")


cites = defaultdict(set)
for d in rows:
    texts = [v.get("basis", "") for v in (d.get("adjudication") or {}).values() if isinstance(v, dict)]
    texts += [h.get("basis", "") + " " + str(h.get("item", "")) for h in d.get("harmonisation") or []]
    for t in texts:
        for item in set(re.findall(r"B-\d+", t)):
            cites[item].add(int(d["rank"]))

byrank = {int(d["rank"]): d for d in rows}
print(f"{'item':6s} {'ranks':>5s} {'in F2 denom':>11s} {'non-plain':>9s} {'NS':>4s} {'U':>3s} {'F4 yes/partial':>14s} {'F5 stated':>9s}  ranks")
for item in GAP:
    rk = sorted(cites.get(item, ()))
    c = [cls(byrank[r]) for r in rk]
    f4 = sum(str(byrank[r].get("F4")).lower() in ("yes", "partial") for r in rk)
    f5 = sum(str(byrank[r].get("F5")).lower() == "stated" for r in rk)
    print(f"{item:6s} {len(rk):5d} {sum(x is not None for x in c):11d} {c.count('nonplain'):9d} {c.count('NS'):4d} "
          f"{c.count('U'):3d} {f4:14d} {f5:9d}  {','.join(map(str, rk))}")
print("\nReading: a ruling can lower 'non-plain or not stated' only by turning a row into U, and lower"
      " 'non-plain stated' by at most its non-plain column; eligibility rulings (B-3, B-4, B-6, B-8)"
      " change the denominator by at most their 'ranks' column.")
