"""Second reader (EB, Claude Sonnet 5.5) and adjudicator (EC, Claude Fable 5.1) draw for the landmark tranche (D0061).

    python -I analysis/extraction/lmk/second_reader.py

Run once, after the stop point: the extracted set is the prefix of extraction-order.json of length n (usable EA
sessions in batch-log.jsonl). Draw: random.Random(20261025).shuffle over the prefix in order position; the first
max(2, ceil(n / 10)) ids. Writes second-reader.json (refuses to overwrite).
"""
import json
import math
import random
from pathlib import Path

D = Path(__file__).resolve().parent
out = D / "second-reader.json"
if out.exists():
    raise SystemExit("second-reader.json exists; the draw is fixed")
order = json.load(open(D / "extraction-order.json", encoding="utf-8"))["order"]
usable = {}
for l in open(D / "batch-log.jsonl", encoding="utf-8"):
    if l.strip():
        r = json.loads(l)
        if r["role"] == "EA":
            usable[r["batch"]] = bool(r.get("usable"))
done = {json.load(open(D / "extraction-order.json", encoding="utf-8"))["batches"][b][0] for b, ok in usable.items() if ok}
n = 0
while n < len(order) and order[n] in done:
    n += 1
assert done == set(order[:n]), "extracted set is not a prefix of the order"
prefix = order[:n]
pool = list(prefix)
random.Random(20261025).shuffle(pool)
k = max(2, math.ceil(n / 10))
doc = {"decision": "D0061 (full D; orchestrator rule: second reader and adjudicator on a random 10 percent, at least 2)",
       "n_extracted": n, "prefix": prefix, "seed": 20261025, "k": k, "ids": pool[:k]}
out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
print(json.dumps(doc))
