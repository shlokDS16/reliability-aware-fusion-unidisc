"""Calibration / headroom / test folds (v2 section 7.5; SAP section 3 and Addendum 1 N13): fixed seed, by COCO val2017 image id, disjoint from each other and
from all probe-1 and probe-2 image ids; captions of 5 to 32 tokens.

The test fold is ONE ordered list of 500 items (SAP section 3): `test` = its first 300 (the base fold), `test_ext` = items 301-500 (the optional extension of the
n-rule, R2). The walk is sequential, so building with a total of 300 or 500 gives the same first 300 items, and negatives are drawn inside each block, so the base
fold is identical whether or not the extension is ever used (property tested). Each item gets its negative caption for the primary (deranged) contrast: a random other
item of the SAME block whose image shares no annotated COCO category with this one (v2 Alg. 11 step 5); if none exists any other item with a different caption is used
and `neg_restricted` is False for it.

Caption length is counted with the UniDisc text tokenizer (NousResearch/Llama-2-7b-hf, local HF cache, tokenizer files only, no model weights) exactly as
`UniScorer.caption_ids` does; the file is frozen and committed before M3 (`python -m exp_p2.gate.folds --write`)."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import config, data                                        # noqa: E402

TEST_BASE, TEST_TOTAL = 300, 500
TOKENIZER_NAME = "NousResearch/Llama-2-7b-hf"


def assign_negatives(items: list[dict], image_cats: dict[int, set[str]] | None, rng: np.random.Generator, offset: int = 0) -> None:
    """Draw a negative for every item of `items` from `items` itself. `offset` shifts the stored indices (block position inside a larger list)."""
    n = len(items)
    cats = [(image_cats or {}).get(it["image_id"], set()) for it in items]
    for i, it in enumerate(items):
        cand_r = [j for j in range(n) if j != i and not (cats[i] & cats[j]) and items[j]["caption"] != it["caption"]] if image_cats is not None else []
        pool, restricted = (cand_r, True) if cand_r else ([j for j in range(n) if j != i and items[j]["caption"] != it["caption"]], False)
        j = int(pool[int(rng.integers(0, len(pool)))])
        it.update(neg_idx=j + offset, neg_image_id=items[j]["image_id"], neg_caption=items[j]["caption"], neg_restricted=restricted)


def build_folds(captions: dict[int, list[str]], n_tok_fn, exclude_ids: set[int], *, seed: int = config.SEED_GATE, sizes=(config.N_CAL, config.N_HEAD, TEST_TOTAL),
                test_base: int = TEST_BASE, tok_range=config.TOK_RANGE, image_cats: dict[int, set[str]] | None = None) -> dict:
    """sizes = (calibration, headroom, test TOTAL). Returns dict(meta, cal, head, test, test_ext)."""
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
    assign_negatives(folds["cal"], image_cats, np.random.default_rng([seed, 8, config.FOLD_GID_OFFSET["cal"]]))
    assign_negatives(folds["head"], image_cats, np.random.default_rng([seed, 8, config.FOLD_GID_OFFSET["head"]]))
    t = folds["test"]
    blocks = [(0, min(test_base, len(t))), (test_base, len(t))]
    for lo, hi in blocks:
        if hi > lo:
            blk = t[lo:hi]
            assign_negatives(blk, image_cats, np.random.default_rng([seed, 8, config.FOLD_GID_OFFSET["test"], lo]), offset=lo)
    out = dict(meta=dict(seed=seed, sizes=list(sizes), test_base=test_base, tok_range=list(tok_range), n_excluded=len(exclude_ids), annotations_used=image_cats is not None),
               cal=folds["cal"], head=folds["head"], test=t[:test_base], test_ext=t[test_base:])
    out["meta"]["sha1"] = hashlib.sha1(json.dumps({k: out[k] for k in ("cal", "head", "test", "test_ext")}, sort_keys=True).encode()).hexdigest()[:16]
    return out


def test_items(folds: dict, n: int | None = None) -> list[dict]:
    """The ordered test list: the base fold, then the extension, cut at n (default: base only)."""
    allt = folds["test"] + folds.get("test_ext", [])
    return allt[:n] if n else folds["test"]


def check_folds(folds: dict, exclude_ids: set[int]) -> None:
    """Disjointness checks used by the tests and by the runner after loading."""
    seen: set[int] = set()
    for k in ("cal", "head", "test", "test_ext"):
        ids = {it["image_id"] for it in folds.get(k, [])}
        assert len(ids) == len(folds.get(k, [])), f"duplicate image in fold {k}"
        assert not (ids & seen), "folds overlap"
        assert not (ids & exclude_ids), "fold uses a probe image"
        seen |= ids
    gids = [it["gid"] for k in ("cal", "head", "test", "test_ext") for it in folds.get(k, [])]
    assert len(set(gids)) == len(gids)


def folds_path(run_id: str = config.FOLDS_RUN_ID) -> Path:
    return Path(common.RUNS) / run_id / "folds.json"


def save_folds(folds: dict, path: Path | None = None) -> Path:
    path = Path(path) if path else folds_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(folds, indent=1), encoding="utf8")
    tmp.replace(path)
    return path


def verify_tokens(folds: dict, n_tok_fn) -> dict:
    """Compare the stored token counts with a (possibly different) tokenizer path, e.g. the real UniScorer.caption_ids at run time. Returns the mismatch report."""
    bad = [(k, it["idx"], it["n_tok"], n_tok_fn(it["caption"])) for k in ("cal", "head", "test", "test_ext") for it in folds.get(k, []) if n_tok_fn(it["caption"]) != it["n_tok"]]
    return dict(n_mismatch=len(bad), mismatches=bad[:20],
                n_outside_range=sum(1 for _, _, _, m in bad if not (config.TOK_RANGE[0] <= m <= config.TOK_RANGE[1])))


MAX_FAIL_FRACTION = 0.10         # SAP Addendum 2 A2.1 item 2: more than 10 percent of any one fold failing the real-tokenizer check is a fold-construction defect


def token_check(folds: dict, n_tok_fn) -> dict:
    """SAP A2.1 item 2. Compare the frozen counts with the runtime tokenizer path. An item whose RUNTIME count falls outside 5-32 is EXCLUDED from every analysis, counted, and NOT
    replaced (the order of the remaining ids is unchanged, so the test300 == test500[:300] prefix property holds as far as possible); the exclusion depends on caption text only.
    A count that differs from the frozen one but stays inside 5-32 is reported (it does not exclude). If more than 10 percent of any one fold is excluded, or differs, `defect` is
    True and the run must stop and report (no refolding without a new card version)."""
    lo, hi = config.TOK_RANGE
    per, excluded = {}, {}
    for k in ("cal", "head", "test", "test_ext"):
        items = folds.get(k, [])
        counts = [(it["idx"], it["n_tok"], n_tok_fn(it["caption"])) for it in items]
        out = [i for i, _, m in counts if not (lo <= m <= hi)]
        mism = [i for i, st, m in counts if m != st and lo <= m <= hi]
        n = len(items)
        per[k] = dict(n=n, n_excluded=len(out), excluded_idx=out, n_mismatch_in_range=len(mism), fraction_excluded=len(out) / n if n else 0.0, fraction_mismatch=len(mism) / n if n else 0.0)
        excluded[k] = out
    defect = [k for k, v in per.items() if v["fraction_excluded"] > MAX_FAIL_FRACTION or v["fraction_mismatch"] > MAX_FAIL_FRACTION]
    return dict(per_fold=per, excluded=excluded, n_excluded_total=sum(len(v) for v in excluded.values()), defect=bool(defect), defect_folds=defect, max_fail_fraction=MAX_FAIL_FRACTION,
                rule="excluded, counted, not replaced (SAP A2.1 item 2)")


def ensure_folds(n_tok_fn, path: Path | None = None) -> dict:
    """Load the folds file if it exists, else build it (needs a token counter and the local COCO files) and write it."""
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


def hf_token_counter(slow: bool = False):
    """Caption token count exactly as UniScorer.caption_ids: tokenise '<s>' + caption without special tokens and drop the leading <s>. Local cache only."""
    import os
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    import transformers
    tok = transformers.AutoTokenizer.from_pretrained(TOKENIZER_NAME, local_files_only=True, use_fast=not slow)
    return lambda c: len(tok("<s>" + c, add_special_tokens=False)["input_ids"][1:])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="build and write runs/P2-GATE-FOLDS/folds.json (refuses to overwrite an existing file)")
    ap.add_argument("--slow", action="store_true", help="use the slow SentencePiece tokenizer (UniDisc config use_slow_tokenizer)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    path = Path(a.out) if a.out else folds_path()
    if path.exists():
        print(f"{path} exists; not overwriting (it is frozen once committed)", file=sys.stderr)
        return 2
    fn = hf_token_counter(a.slow)
    f = ensure_folds(fn, path) if a.write else None
    if f is not None:
        other = hf_token_counter(not a.slow)
        rep = verify_tokens(f, other)
        print(json.dumps(dict(path=str(path), sizes={k: len(f[k]) for k in ("cal", "head", "test", "test_ext")}, sha1=f["meta"]["sha1"], slow_vs_fast=rep)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
