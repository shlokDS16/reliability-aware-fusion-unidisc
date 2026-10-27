"""Calibration / headroom / test folds (v2 section 7.5): fixed seed, by COCO val2017 image id, disjoint from each other and from all probe-1 and probe-2
image ids; captions of 5 to 32 tokens. Each item also gets its negative caption for the primary (deranged) contrast: a random other item of the SAME
fold whose image shares no annotated COCO category with this one (v2 Alg. 11 step 5); if no such item exists (or annotations are missing) any other
item with a different caption is used and `neg_restricted` is False for it.

Tokenisation needs the UniDisc tokenizer, so the folds are built inside the first runner that has a scorer (M2), or by any caller passing `n_tok_fn`.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from exp_p2 import common
from exp_p2.gate import config, data


def assign_negatives(items: list[dict], image_cats: dict[int, set[str]] | None, rng: np.random.Generator) -> None:
    n = len(items)
    cats = [(image_cats or {}).get(it["image_id"], set()) for it in items]
    for i, it in enumerate(items):
        cand_r = [j for j in range(n) if j != i and not (cats[i] & cats[j]) and items[j]["caption"] != it["caption"]] if image_cats is not None else []
        pool, restricted = (cand_r, True) if cand_r else ([j for j in range(n) if j != i and items[j]["caption"] != it["caption"]], False)
        j = int(pool[int(rng.integers(0, len(pool)))])
        it.update(neg_idx=j, neg_image_id=items[j]["image_id"], neg_caption=items[j]["caption"], neg_restricted=restricted)


def build_folds(captions: dict[int, list[str]], n_tok_fn, exclude_ids: set[int], *, seed: int = config.SEED_GATE, sizes=(config.N_CAL, config.N_HEAD, config.N_TEST),
                tok_range=config.TOK_RANGE, image_cats: dict[int, set[str]] | None = None) -> dict:
    ids = sorted(i for i in captions if i not in exclude_ids)
    rng = np.random.default_rng([seed, 7])
    order = rng.permutation(len(ids))
    names = ("cal", "head", "test")
    need = dict(zip(names, sizes))
    folds: dict[str, list[dict]] = {k: [] for k in names}
    cur = 0
    for j in order:
        if cur >= len(names):
            break
        iid = ids[int(j)]
        cs = captions[iid]
        c = cs[int(rng.integers(0, len(cs)))]
        nt = n_tok_fn(c)
        if not (tok_range[0] <= nt <= tok_range[1]):
            continue
        name = names[cur]
        idx = len(folds[name])
        folds[name].append(dict(idx=idx, gid=config.FOLD_GID_OFFSET[name] + idx, image_id=int(iid), caption=c, n_tok=int(nt)))
        if len(folds[name]) == need[name]:
            cur += 1
    for k in names:
        if len(folds[k]) < need[k]:
            raise RuntimeError(f"not enough eligible items for fold {k}: {len(folds[k])} < {need[k]}")
        assign_negatives(folds[k], image_cats, np.random.default_rng([seed, 8, config.FOLD_GID_OFFSET[k]]))
    meta = dict(seed=seed, sizes=list(sizes), tok_range=list(tok_range), n_excluded=len(exclude_ids), annotations_used=image_cats is not None)
    out = dict(meta=meta, **folds)
    out["meta"]["sha1"] = hashlib.sha1(json.dumps({k: folds[k] for k in names}, sort_keys=True).encode()).hexdigest()[:16]
    return out


def check_folds(folds: dict, exclude_ids: set[int]) -> None:
    """Disjointness checks used by the tests and by the runner after loading."""
    seen: set[int] = set()
    for k in ("cal", "head", "test"):
        ids = {it["image_id"] for it in folds[k]}
        assert len(ids) == len(folds[k]), f"duplicate image in fold {k}"
        assert not (ids & seen), "folds overlap"
        assert not (ids & exclude_ids), "fold uses a probe image"
        seen |= ids


def folds_path(run_id: str = config.FOLDS_RUN_ID) -> Path:
    return Path(common.RUNS) / run_id / "folds.json"


def save_folds(folds: dict, path: Path | None = None) -> Path:
    path = Path(path) if path else folds_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(folds, indent=1), encoding="utf8")
    tmp.replace(path)
    return path


def ensure_folds(n_tok_fn, path: Path | None = None) -> dict:
    """Load the folds file if it exists, else build it (needs the tokenizer via n_tok_fn and the local COCO files) and write it."""
    path = Path(path) if path else folds_path()
    if path.exists():
        return json.loads(path.read_text(encoding="utf8"))
    try:
        _, image_cats = data.load_instances()
    except FileNotFoundError:
        image_cats = None
    excl = data.probe_image_ids()
    folds = build_folds(common.load_captions(), n_tok_fn, excl, image_cats=image_cats)
    check_folds(folds, excl)
    save_folds(folds, path)
    return folds
