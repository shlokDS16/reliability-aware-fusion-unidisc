"""Fresh pools of EXP-003 (card 3). Eval venv. Writes runs/EXP-003/pools.json with the id lists, their SHA-256 and a machine check of
disjointness from every block of runs/EXP-001/gates/coco_draw.json.

Order of operations (the card says "permute the eligible leftovers with seed 1303"): one caption per COCO val2017 image (smallest annotation
id, analysis/EXP-001/coco_draw.load_captions), images sorted by image id, remove the ids of all blocks of coco_draw.json, keep the rung-2
eligible items (prefix_rule v2, spaCy en_core_web_sm), keep that list in image-id order, permute with numpy default_rng(1303).permutation,
take E3-PILOT 16, E3-CTRL 48, E3-MAIN 150 in that order.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "analysis" / "EXP-001")]

from exp003.config import POOL_ORDER, POOL_SIZE, PERM_SEED, RUNS  # noqa: E402

ANN = Path(r"C:\Users\Shlok\.cache\dlm_dl\coco\ann\annotations\captions_val2017.json")
DRAW = ROOT / "runs" / "EXP-001" / "gates" / "coco_draw.json"


def sha_ids(ids) -> str:
    return hashlib.sha256(json.dumps([int(i) for i in ids]).encode()).hexdigest()


def build(ann=ANN, draw=DRAW, tagger=None):
    import coco_draw as cd
    import prefix_rule as pr
    tagger = tagger or pr.SpacyTagger()
    items = cd.load_captions(ann)                                  # [(id, file, caption)] sorted by id
    d = json.loads(Path(draw).read_text(encoding="utf8"))
    excluded = {int(x["image_id"]) for v in d["blocks"].values() for x in v}
    left = [it for it in items if it[0] not in excluded]
    elig = []
    for iid, fn, cap in left:
        r = pr.prefix_for(cap, tagger, 2)
        if r.eligible:
            elig.append(dict(image_id=int(iid), file=fn, caption=cap, prefix=r.prefix, n_prefix_words=r.n_words, target_noun=r.target_noun))
    perm = np.random.default_rng(PERM_SEED).permutation(len(elig))
    order = [elig[i] for i in perm]
    pools, k = {}, 0
    for name in POOL_ORDER:
        n = POOL_SIZE[name]
        pools[name] = order[k:k + n]
        k += n
    out = dict(card="EXP-003 v0.3.2", perm_seed=PERM_SEED, tagger=dict(name="en_core_web_sm", version=tagger.meta.get("version")),
               n_images=len(items), n_excluded_coco_draw=len(excluded), n_left=len(left), n_rung2_eligible_left=len(elig),
               card_expects=dict(n_left=2200, n_rung2_eligible_left=1394),
               matches_card=bool(len(left) == 2200 and len(elig) == 1394), enough=bool(len(elig) >= k),
               pools={n: dict(ids=[x["image_id"] for x in v], ids_sha256=sha_ids([x["image_id"] for x in v]), items=v) for n, v in pools.items()})
    all_ids = [x["image_id"] for v in pools.values() for x in v]
    out["disjoint_from_coco_draw"] = bool(not (set(all_ids) & excluded))
    out["pools_pairwise_disjoint"] = bool(len(all_ids) == len(set(all_ids)))
    return out


def main():
    out = build()
    p = RUNS / "pools.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    p.write_text(txt, encoding="utf8")
    sha = hashlib.sha256(txt.encode("utf8")).hexdigest()
    (RUNS / "pools.json.sha256").write_text(sha + "\n")
    print({k: v for k, v in out.items() if k != "pools"}, "sha256", sha)
    assert out["disjoint_from_coco_draw"] and out["pools_pairwise_disjoint"] and out["enough"]


if __name__ == "__main__":
    main()
