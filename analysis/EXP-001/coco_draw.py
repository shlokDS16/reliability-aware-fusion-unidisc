"""COCO val2017 draw (EXP-001 card v0.5, section 3 item 8 and 4.5). Pre-freeze amendment allowed by the card.

One caption per image (the annotation with the smallest id), images sorted by image id, permuted with seed 777; eligibility by
the prefix rule (4.2) at rung 1 (and, for the PG2 pool only, rung 2); blocks assigned to pools in a fixed order; items are never
selected or dropped by any model output. Pool blocks are disjoint. Writes coco_draw.json (ids, captions, prefixes, blocks).

Run (eval venv):  python analysis/EXP-001/coco_draw.py --ann <captions_val2017.json> --out runs/EXP-001/gates/coco_draw.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

import prefix_rule as pr

SEED = 777
# order of the block allocation among rung-1 eligible items (permuted order); sizes from 4.3-4.5
BLOCKS_RUNG1 = [("GATE_GUIDED", 32), ("PG", 24), ("D0", 64), ("D1", 128), ("D2", 256), ("D3", 1000), ("D4", 250), ("D5", 128),
                ("PCB", 96), ("REFT2I", 250)]
BLOCKS_RUNG2 = [("PG2", 24)]
# real-pair references (need not be prefix-eligible): taken from the permuted list tail, disjoint from the blocks above
BLOCKS_ANY = [("PCF", 48), ("REFREAL", 500)]


def load_captions(path):
    d = json.load(open(path, encoding="utf8"))
    first = {}
    for a in sorted(d["annotations"], key=lambda a: a["id"]):
        first.setdefault(a["image_id"], a["caption"])
    imgs = {i["id"]: i["file_name"] for i in d["images"]}
    return [(iid, imgs[iid], first[iid]) for iid in sorted(first)]


def draw(items, tagger):
    perm = np.random.default_rng(SEED).permutation(len(items))
    order = [items[i] for i in perm]
    r1, r2, elig1, elig2 = {}, {}, [], []
    for iid, fn, cap in order:
        a = pr.prefix_for(cap, tagger, 1)
        b = pr.prefix_for(cap, tagger, 2)
        r1[iid], r2[iid] = a, b
        if a.eligible:
            elig1.append(iid)
        if b.eligible:
            elig2.append(iid)
    info = {i[0]: dict(file=i[1], caption=i[2]) for i in items}
    used, blocks = set(), {}

    def take(name, n, pool):
        got = [i for i in pool if i not in used][:n]
        used.update(got)
        blocks[name] = got
        return len(got) == n

    short = {}
    for name, n in BLOCKS_RUNG1:
        short[name] = not take(name, n, elig1)
    for name, n in BLOCKS_RUNG2:
        short[name] = not take(name, n, elig2)
    anyp = [i[0] for i in order]
    for name, n in BLOCKS_ANY:
        short[name] = not take(name, n, anyp[::-1])
    out = {
        "seed": SEED, "n_images": len(items), "rule": pr.RULE_VERSION,
        "eligible_rung1": len(elig1), "eligible_rung2": len(elig2),
        "share_rung1": len(elig1) / len(items), "share_rung2": len(elig2) / len(items),
        "need_rung1": sum(n for _, n in BLOCKS_RUNG1), "short": short,
        "blocks": {k: [dict(image_id=i, file=info[i]["file"], caption=info[i]["caption"],
                            prefix=(r1[i].prefix if k not in ("PG2",) else r2[i].prefix) if (r1[i].eligible or k == "PG2") else None,
                            target_noun=(r1[i].target_noun if k != "PG2" else r2[i].target_noun) if (r1[i].eligible or k == "PG2") else None)
                       for i in v] for k, v in blocks.items()},
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ann", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    items = load_captions(a.ann)
    tagger = pr.SpacyTagger()
    out = draw(items, tagger)
    out["tagger"] = dict(name="en_core_web_sm", version=tagger.meta.get("version"), spacy_version=__import__("spacy").__version__)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    Path(a.out).write_text(txt, encoding="utf8")
    print(out["n_images"], out["eligible_rung1"], round(out["share_rung1"], 4), out["eligible_rung2"], out["short"])
    print("sha256", hashlib.sha256(txt.encode("utf8")).hexdigest())


if __name__ == "__main__":
    main()
