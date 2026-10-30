"""CPU dry run on the real local COCO metadata: folds, restricted negatives and the hard-negative builder. NO model, no tokenizer, no GPU.

    python -m exp_p2.gate.cpu_dryrun [--out runs/P2-GATE-CPU]

The UniDisc tokenizer is not available without loading the model package, so caption length is approximated by 1.3 x the word count (rounded up) ONLY for this
dry run; the real folds (runs/P2-GATE-FOLDS/folds.json) are built by the first GPU runner with the real tokenizer and are not touched here. The point is to
check that the local files load, the folds are disjoint from the probes, negatives can be restricted by category, and to see the hard-negative yield."""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import data, folds, hardneg                                # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(common.RUNS) / "P2-GATE-CPU"))
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cat_super, image_cats = data.load_instances()
    caps = common.load_captions()
    excl = data.probe_image_ids()
    f = folds.build_folds(caps, lambda c: math.ceil(1.3 * len(c.split())), excl, image_cats=image_cats)
    folds.check_folds(f, excl)
    res = dict(note="dry run: caption length approximated by ceil(1.3 * words); not the real folds", n_categories=len(cat_super), n_images_with_annotations=len(image_cats),
               n_excluded_probe_ids=len(excl), fold_sizes={k: len(f[k]) for k in ("cal", "head", "test")}, fold_sha1=f["meta"]["sha1"],
               frac_negatives_restricted={k: sum(it["neg_restricted"] for it in f[k]) / len(f[k]) for k in ("cal", "head", "test")},
               table_categories_equal_instances_file=bool(set(cat_super) == set(hardneg.CATS)))
    hn = {}
    for k in ("head", "test"):
        recs, skipped = hardneg.build_hard_negatives(f[k], image_cats, caps, cat_super, seed=20261029)
        hn[k] = dict(n_items=len(f[k]), n_built=len(recs), yield_=len(recs) / len(f[k]), skipped=dict(skipped), examples=recs[:8])
        hardneg.audit_sheet(recs[:100], out / f"hardneg_audit_sheet_{k}_first100.jsonl")
    res["hard_negatives"] = hn
    (out / "cpu_dryrun.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf8")
    print(json.dumps({k: v for k, v in res.items() if k != "hard_negatives"}, indent=1))
    print({k: (v["n_built"], v["n_items"], v["skipped"]) for k, v in hn.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
