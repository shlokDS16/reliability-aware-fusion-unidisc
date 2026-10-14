"""Final census counts from the adjudicated codes (research/review/coverage/census-final.csv)."""
import csv
from collections import Counter
from pathlib import Path

rows = list(csv.DictReader(open(Path(__file__).resolve().parents[2] / "research/review/coverage/census-final.csv", encoding="utf8")))
f2 = lambda r: "NA" if r["F2_codes"] == "NA" else "NS" if r["F2_codes"] == "NS" else "plain" if r["F2_codes"] == "U" else "non-plain"
print("papers:", len(rows))
print("F2 headline value rule:", dict(Counter(f2(r) for r in rows)))
cls = Counter(c for r in rows if f2(r) == "non-plain" for c in r["F2_codes"].split("+"))
print("  classes among non-plain:", dict(cls))
gen = [r for r in rows if r["F1_metric"] and f2(r) != "NA"]
print("papers with a headline generated-sample result:", len(gen))
for g in ("non-plain", "plain", "NS"):
    sub = [r for r in gen if f2(r) == g]
    print(f"  {g:9s} n={len(sub):2d}  entropy/diversity reported (F3=Yes): {sum(r['F3'] == 'Yes' for r in sub)}")
sw = [r for r in gen if r["F4"] in ("Yes", "Partial")]
print("step sweep reported:", len(sw), "| value rule fixed stated (F5):", dict(Counter(r["F5"] for r in sw)))
gd = [r for r in gen if "G" in r["F2_codes"].split("+")]
print("guided headlines:", len(gd), "| guidance fixed in sweep (F6):", dict(Counter(r["F6"] for r in gd)))
