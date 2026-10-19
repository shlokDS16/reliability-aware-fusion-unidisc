"""Reversal test of the title/abstract re-check (criteria v1.6 section 5.2): K = sampled records included at
full text after A/B agreement or C's ruling (Route F).

    python -I analysis/screening/ta_recheck_k.py

Reads the frozen sample (sha256 checked), analysis/screening/ft-t1/t1-decisions-all.jsonl (one row per T1
record: A=B rows and C rulings) and t1-not-retrieved.jsonl. Prints and writes ta-recheck-k.json: K, the
sampled ids by status (included, excluded, not retrieved, not in T1), and per included id its source (A=B or C).
The rule (K >= 1 -> all 797 frame candidates go to full text) is applied by the human author, not here.
"""
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLE = HERE / "ta-recheck-sample-v1.3-frozen.json"
SHA = "958867658120c323446ee5692ec82702deb4464e0977a6030287ced035b7ac6c"
assert hashlib.sha256(SAMPLE.read_bytes()).hexdigest() == SHA, "sample file changed"
ids = json.loads(SAMPLE.read_text(encoding="utf-8"))["ids"]
dec = {r["id"]: r for r in map(json.loads, (HERE / "ft-t1/t1-decisions-all.jsonl").read_text(encoding="utf-8").splitlines()) if r}
nr = {r["id"]: r for r in map(json.loads, (HERE / "ft-t1/t1-not-retrieved.jsonl").read_text(encoding="utf-8").splitlines()) if r}
out = {"included": [], "excluded": [], "not_retrieved": [], "not_in_T1": []}
for i in sorted(ids):
    if i in dec:
        r = dec[i]
        (out["included"] if r["decision"] == "include" else out["excluded"]).append(
            {"id": i, "source": r["source"], "code": r.get("code", ""), "batch": r["batch"]})
    elif i in nr:
        out["not_retrieved"].append({"id": i, "code": nr[i]["code"]})
    else:
        out["not_in_T1"].append(i)
res = {"n_sample": len(ids), "K": len(out["included"]),
       "counts": {k: len(v) for k, v in out.items()},
       "rule": "criteria-v1.6 s5.2: if K >= 1, all 797 frame candidates are screened at full text; else report K = 0 and the one-sided 95% upper bound",
       **out}
(HERE / "ta-recheck-k.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
print(json.dumps({k: res[k] for k in ("n_sample", "K", "counts")}))
print("included:", [(r["id"], r["source"]) for r in out["included"]])
print("not in T1:", out["not_in_T1"])
