"""Freeze the re-check frame and sample (criteria v1.3 section 5).

Copies analysis/screening/ta-recheck-candidates-v1.2.jsonl (797 candidates from ta_recheck_select.py, seed
20261016 sample flagged in_sample) to a frozen frame file, writes the sampled ids to their own file, and
prints SHA-256 digests. Later changes to the title/abstract screening files (for example the subscription
queue) must never change these files: the subscription and title-resolved queues get their own frame and
sample, computed after their title/abstract screening, never a redraw of this one.

    python analysis/screening/ta_recheck_freeze.py

Refuses to overwrite an existing frozen file whose digest differs.
"""
import hashlib
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
SRC = D / "ta-recheck-candidates-v1.2.jsonl"
FRAME = D / "ta-recheck-frame-v1.3-frozen.jsonl"
SAMPLE = D / "ta-recheck-sample-v1.3-frozen.json"
EXPECTED_SRC = "a9180fe4bdb7956b8d8e6c4340559c94ac4f877cbc6376d1dad99995bb32d79a"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    src = SRC.read_bytes()
    if sha(src) != EXPECTED_SRC:
        sys.exit(f"candidates file changed (sha256 {sha(src)}), expected {EXPECTED_SRC}; not freezing")
    rows = [json.loads(l) for l in src.decode("utf-8").splitlines() if l.strip()]
    ids = sorted(r["id"] for r in rows if r.get("in_sample"))
    sample = json.dumps({"seed": 20261016, "n": len(ids), "frame_n": len(rows),
                         "frame_sha256": sha(src), "ids": ids}, indent=1).encode("utf-8")
    for path, data in ((FRAME, src), (SAMPLE, sample)):
        if path.exists() and sha(path.read_bytes()) != sha(data):
            sys.exit(f"{path.name} exists with different content; refusing to overwrite")
        path.write_bytes(data)
        print(f"{path.name}: sha256 {sha(data)}")
    print(f"frame {len(rows)} candidates; sample {len(ids)} ids")


if __name__ == "__main__":
    main()
