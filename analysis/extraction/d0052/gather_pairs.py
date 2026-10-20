"""Collect the latest EA and EB record (pass 2 if present, else pass 1) for each second-reader id (D0054) into
analysis/extraction/d0052/ec-input/EA-pairs.jsonl and EB-pairs.jsonl, for ex_dispatch.py --role EC.

    python -I analysis/extraction/d0052/gather_pairs.py
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent
ids = json.load(open(D / "seed-sample.json", encoding="utf-8"))["second_reader_ids"]


def latest(role):
    out = {}
    for folder in sorted((D / role).glob("*")):
        files = sorted(folder.glob(f"{role}-*.jsonl"))
        p2 = [f for f in files if f.stem.endswith("-pass2")]
        use = p2 or [f for f in files if not f.stem.endswith("-pass2")]
        for f in use:
            for line in open(f, encoding="utf-8"):
                if line.strip().startswith("{"):
                    r = json.loads(line)
                    out[r["id"]] = r
    return out


ea, eb = latest("EA"), latest("EB")
(D / "ec-input").mkdir(exist_ok=True)
for name, src in (("EA-pairs.jsonl", ea), ("EB-pairs.jsonl", eb)):
    missing = [i for i in ids if i not in src]
    assert not missing, (name, missing)
    (D / "ec-input" / name).write_text("".join(json.dumps(src[i]) + "\n" for i in ids), encoding="utf-8")
print("pairs written for", ids)
