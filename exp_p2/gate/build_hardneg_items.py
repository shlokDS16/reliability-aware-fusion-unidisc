"""Family H items (hard negatives, DRAFT pending the lead's go/no-go): builds runs/P2-HARDNEG-ITEMS/folds_hardneg.json from the SugarCrepe files
(research/paper2/data/sugarcrepe-probe/, MIT, pinned commit 0047054b, SHA-256 in SHA256SUMS.txt) and the existing pools. CPU only, no model, no GPU.

    python -m exp_p2.gate.build_hardneg_items [--out PATH] [--slow]        # refuses to overwrite an existing file (it is frozen once committed)

Output has the schema of folds.json so the pinned runners can read it with --folds-path: `head` = H3 (50 items, headroom stage), `test` = H4 (300 items, main stage), `cal` and `test_ext` empty.
Per item: idx, gid, image_id, caption, n_tok (as folds.json) plus neg_caption, n_tok_neg, tok_diff (= n_tok_neg - n_tok), subset, neg_source. `neg_caption` is the SugarCrepe negative, so the
runner's per-item negative needs no change.

Selection rule (all of it deterministic given the seed and the input files; nothing about any model outcome is read):
  1. one candidate row per (subset, image); images in any existing pool are dropped: cal, head, test, test_ext of folds.json, probe 1 and 2 (selection.json), the M1 and M5 item files if present;
  2. both captions must have 5 to 32 UniDisc caption tokens (config.TOK_RANGE; the runtime tokenizer path of folds.hf_token_counter); rows with an identical positive and negative are dropped;
  3. quotas per subset: H4 300 = 42 or 43 per subset, H3 50 = 7 or 8 per subset (the +1 subsets are drawn with the seed); H3 and H4 never share an image, and no image is used in two subsets;
  4. subsets are filled from the scarcest (fewest eligible images) to the most common, so the smallest subset (swap_obj) always reaches its quota; inside a subset the images are a seeded permutation;
  5. the final order of H3 and of H4 is a seeded shuffle, so that a partly finished run is still spread over the seven subsets.
"""
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
from exp_p2.gate import config, data, folds                                 # noqa: E402

RUN_ID = "P2-HARDNEG-ITEMS"
SUBSETS = ("replace_obj", "replace_att", "replace_rel", "swap_obj", "swap_att", "add_obj", "add_att")      # the seven SugarCrepe files; canonical order
N_H3, N_H4 = 50, 300
GID_OFFSET = {"head": 6000, "test": 7000}      # gid = offset + idx; the folds use 0-2499, family B 4000/5000 (foil.py GID_FIT/GID_TEST); 6000/7000 are free, so no mask or jitter stream is shared
# Selection seed. LOCAL constant on purpose: seeds.ANALYSES is the analysis-seed table and its next append position (32) is reserved for tier3_fusion (tier3_fusion.SEED_SPAWN_KEY, A4.1.7);
# appending a name there would move that child. Same pattern as folds.py, which builds its streams as default_rng([SEED_GATE, k, ...]). Stream 9 is unused by folds.py (7 and 8 are used).
SELECT_SEED = [config.SEED_GATE, 9]
SUGARCREPE_DIR = ROOT / "research" / "paper2" / "data" / "sugarcrepe-probe"
OPTIONAL_ITEM_FILES = ("P2-GATE-M1", "P2-GATE-M5")      # runs/<id>/items.jsonl; their images come from the probe lists and the folds, so they are normally already covered; read for image_id only


def norm(s: str) -> str:
    return " ".join(str(s).split())          # as common.load_captions


def sha256_lf(path: Path) -> str:
    """SHA-256 of the file with CRLF turned into LF: a checkout with core.autocrlf=true rewrites the committed (LF) bytes, and SHA256SUMS.txt is the hash of the LF bytes."""
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def verify_sha256(directory: Path = SUGARCREPE_DIR) -> list[str]:
    """Names of the seven data files whose (LF-normalised) SHA-256 differs from SHA256SUMS.txt (empty list = all match). Raises FileNotFoundError if the sums file or a data file is missing."""
    sums = {}
    for line in (directory / "SHA256SUMS.txt").read_text(encoding="utf8").splitlines():
        if line.strip():
            h, name = line.split(None, 1)
            sums[name.strip().lstrip("*")] = h
    bad = []
    for s in SUBSETS:
        name = f"{s}.json"
        if sha256_lf(directory / name) != sums.get(name):
            bad.append(name)
    return bad


def load_sugarcrepe(directory: Path = SUGARCREPE_DIR) -> list[dict]:
    """All rows of the seven files in canonical order: dict(subset, key, image_id, caption, neg_caption)."""
    rows = []
    for s in SUBSETS:
        d = json.loads((directory / f"{s}.json").read_text(encoding="utf8"))
        for k in sorted(d, key=int):
            r = d[k]
            rows.append(dict(subset=s, key=int(k), filename=str(r["filename"]), image_id=int(str(r["filename"]).split(".")[0]), caption=norm(r["caption"]), neg_caption=norm(r["negative_caption"])))
    return rows


def exclusion_ids(runs: Path | None = None, extra_files: tuple[str, ...] = OPTIONAL_ITEM_FILES, by_source: dict | None = None) -> tuple[set[int], dict]:
    """Image ids of every existing pool. folds.json and both probe selection.json files are REQUIRED (data.probe_image_ids would silently skip a missing one); M1/M5 item files are read if present.
    Returns (ids, report) with the number of ids per source and the sources that were absent. `by_source`, if given, is filled with the id set of every source (for the H-L7 samples)."""
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    ids: set[int] = set()
    rep: dict = dict(sources={}, missing_optional=[])
    fp = runs / config.FOLDS_RUN_ID / "folds.json"
    if not fp.exists():
        raise FileNotFoundError(f"{fp} missing: the exclusion list needs the existing folds")
    f = json.loads(fp.read_text(encoding="utf8"))
    for k in ("cal", "head", "test", "test_ext"):
        s = {int(it["image_id"]) for it in f.get(k, [])}
        rep["sources"][f"folds.{k}"] = len(s)
        ids |= s
        if by_source is not None:
            by_source[f"folds.{k}"] = s
    for rid in ("P2-PROBE-01", "P2-PROBE-02"):
        sp = runs / rid / "selection.json"
        if not sp.exists():
            raise FileNotFoundError(f"{sp} missing: probe image ids are required for the exclusion list")
    p = data.probe_image_ids(runs)
    rep["sources"]["probe1+probe2"] = len(p)
    ids |= p
    if by_source is not None:
        by_source["probe1+probe2"] = set(p)
    for rid in extra_files:
        ip = runs / rid / "items.jsonl"
        if not ip.exists():
            rep["missing_optional"].append(str(ip.relative_to(runs)) if runs in ip.parents else str(ip))
            continue
        s = {int(r["image_id"]) for r in common.read_jsonl(ip) if "image_id" in r}
        rep["sources"][rid] = len(s)
        ids |= s
        if by_source is not None:
            by_source[rid] = s
    rep["n_excluded_images"] = len(ids)
    return ids, rep


def h_l6(rows: list[dict], excluded: set[int]) -> dict:
    """H-L6 positive control: the number of SugarCrepe rows (whole release) whose image id matches an excluded set must be > 0, else the id format does not match and the exclusion filter proves nothing."""
    n = sum(1 for r in rows if r["image_id"] in excluded)
    return dict(n_rows_in_existing_pools=n, ok=bool(n > 0))


def foil_pool_ids(runs: Path | None = None) -> set[int]:
    """Image ids of the family B (FOIL) pool: `fit` and `test` of runs/P2-GATE-FOIL/pool.json. Raises FileNotFoundError if the file is missing (H-L4 is an assertion, not optional)."""
    p = (Path(runs) if runs is not None else Path(common.RUNS)) / "P2-GATE-FOIL" / "pool.json"
    if not p.exists():
        raise FileNotFoundError(f"{p} missing: H-L4 (disjoint from the FOIL pool) needs it")
    d = json.loads(p.read_text(encoding="utf8"))
    return {int(it["image_id"]) for k in ("fit", "test") for it in d.get(k, [])}


def h_l4(items: list[dict], foil_ids: set[int]) -> dict:
    """H-L4 (FX-1): no H item image is in the FOIL pool; raises AssertionError with the count otherwise. Returns the count record."""
    shared = sorted({int(it["image_id"]) for it in items} & set(foil_ids))
    assert not shared, f"H-L4: {len(shared)} H image ids are in the FOIL pool, e.g. {shared[:5]}"
    return dict(checked=True, n_foil_pool_images=len(foil_ids), n_overlap=0)


def h_l7_samples(rows: list[dict], by_source: dict) -> list[dict]:
    """H-L7: for cal, head, test, test_ext and probe, the smallest matched image id with the SugarCrepe file name and the COCO file name, for a hand check by the data-steward."""
    by_id: dict[int, dict] = {}
    for r in rows:
        by_id.setdefault(r["image_id"], r)
    out = []
    for src in ("folds.cal", "folds.head", "folds.test", "folds.test_ext", "probe1+probe2"):
        hit = sorted(i for i in by_source.get(src, ()) if i in by_id)
        out.append(dict(source=src, n_matched=len(hit), image_id=hit[0] if hit else None, sugarcrepe_filename=by_id[hit[0]]["filename"] if hit else None,
                        sugarcrepe_subset=by_id[hit[0]]["subset"] if hit else None, coco_file=f"val2017/{hit[0]:012d}.jpg" if hit else None))
    return out


def eligible_rows(rows: list[dict], excluded: set[int], n_tok_fn, tok_range=config.TOK_RANGE) -> tuple[list[dict], dict]:
    """Rows on images outside every pool with both captions in the token range and a negative that differs from the positive. Adds n_tok, n_tok_neg. Counts per reason are returned."""
    cache: dict[str, int] = {}

    def nt(c: str) -> int:
        if c not in cache:
            cache[c] = int(n_tok_fn(c))
        return cache[c]
    lo, hi = tok_range
    out, why = [], dict(total=len(rows), in_existing_pool=0, token_rule=0, same_caption=0)
    for r in rows:
        if r["image_id"] in excluded:
            why["in_existing_pool"] += 1
            continue
        a, b = nt(r["caption"]), nt(r["neg_caption"])
        if not (lo <= a <= hi and lo <= b <= hi):
            why["token_rule"] += 1
            continue
        if r["caption"] == r["neg_caption"]:
            why["same_caption"] += 1
            continue
        out.append(dict(r, n_tok=a, n_tok_neg=b))
    why["eligible_rows"] = len(out)
    return out, why


def quotas(n: int, rng: np.random.Generator, subsets=SUBSETS) -> dict[str, int]:
    """n split as evenly as possible over the subsets; the n % len(subsets) subsets that get one extra item are drawn with rng."""
    base, rem = divmod(n, len(subsets))
    extra = {subsets[int(i)] for i in rng.permutation(len(subsets))[:rem]}
    return {s: base + (1 if s in extra else 0) for s in subsets}


def select(rows: list[dict], n_h3: int = N_H3, n_h4: int = N_H4, seed=SELECT_SEED, subsets=SUBSETS) -> tuple[list[dict], list[dict], dict]:
    """-> (H3 rows, H4 rows, info). See the module docstring for the rule. Raises RuntimeError when a subset cannot fill its quota."""
    q3, q4 = quotas(n_h3, np.random.default_rng([*seed, 1]), subsets), quotas(n_h4, np.random.default_rng([*seed, 2]), subsets)
    by_sub: dict[str, dict[int, list[dict]]] = {s: {} for s in subsets}
    for r in rows:
        by_sub[r["subset"]].setdefault(r["image_id"], []).append(r)
    n_img = {s: len(by_sub[s]) for s in subsets}
    order = sorted(subsets, key=lambda s: (n_img[s], subsets.index(s)))            # scarcest first; ties by canonical order
    taken: set[int] = set()
    h3, h4 = [], []
    for s in order:
        need3, need4 = q3[s], q4[s]
        rng = np.random.default_rng([*seed, 10 + subsets.index(s)])
        avail = sorted(i for i in by_sub[s] if i not in taken)
        if len(avail) < need3 + need4:
            raise RuntimeError(f"subset {s}: {len(avail)} images left, quota {need3 + need4} (H3 {need3} + H4 {need4})")
        perm = [avail[int(j)] for j in rng.permutation(len(avail))[:need3 + need4]]
        for k, iid in enumerate(perm):
            cands = sorted(by_sub[s][iid], key=lambda r: r["key"])               # several rows of one image in one subset: the pick must not depend on the input order
            row = cands[int(rng.integers(0, len(cands)))] if len(cands) > 1 else cands[0]
            (h3 if k < need3 else h4).append(row)
            taken.add(iid)
    for lst, tag in ((h3, 3), (h4, 4)):
        lst[:] = [lst[int(j)] for j in np.random.default_rng([*seed, tag]).permutation(len(lst))]
    return h3, h4, dict(quota_h3=q3, quota_h4=q4, fill_order=order, eligible_images_per_subset=n_img)


def to_items(rows: list[dict], fold: str) -> list[dict]:
    return [dict(idx=i, gid=GID_OFFSET[fold] + i, image_id=int(r["image_id"]), caption=r["caption"], n_tok=int(r["n_tok"]), neg_caption=r["neg_caption"], n_tok_neg=int(r["n_tok_neg"]),
                 tok_diff=int(r["n_tok_neg"]) - int(r["n_tok"]), subset=r["subset"], neg_source="sugarcrepe") for i, r in enumerate(rows)]


def build(rows: list[dict], excluded: set[int], n_tok_fn, *, n_h3: int = N_H3, n_h4: int = N_H4, seed=SELECT_SEED, tok_range=config.TOK_RANGE, exclusion_report: dict | None = None,
          sha256: dict | None = None, foil_ids: set[int] | None = None) -> dict:
    """The folds-schema dict: head = H3, test = H4, cal and test_ext empty."""
    elig, why = eligible_rows(rows, excluded, n_tok_fn, tok_range)
    h3, h4, info = select(elig, n_h3, n_h4, seed)
    out = dict(meta=dict(seed=list(seed), sizes=[0, n_h3, n_h4], test_base=n_h4, tok_range=list(tok_range), family="H", neg_source="sugarcrepe", n_excluded=len(excluded),
                         annotations_used=False, gid_offset=GID_OFFSET, row_filter=why, selection=info, exclusion=exclusion_report, sugarcrepe_sha256=sha256,
                         per_subset={k: {s: sum(1 for it in lst if it["subset"] == s) for s in SUBSETS} for k, lst in (("head", h3), ("test", h4))}),
               cal=[], head=to_items(h3, "head"), test=to_items(h4, "test"), test_ext=[])
    out["meta"]["sha1"] = hashlib.sha1(json.dumps({k: out[k] for k in ("cal", "head", "test", "test_ext")}, sort_keys=True).encode()).hexdigest()[:16]
    folds.check_folds(out, excluded)                       # duplicates inside a fold, overlap between folds, overlap with any existing pool, duplicate gids
    out["meta"]["h_l4"] = h_l4(out["head"] + out["test"], foil_ids) if foil_ids is not None else dict(checked=False)      # the FOIL pool lies inside folds.json (0 outside), so this is normally 0 by construction
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help=f"default: runs/{RUN_ID}/folds_hardneg.json")
    ap.add_argument("--slow", action="store_true", help="use the slow SentencePiece tokenizer (UniDisc config use_slow_tokenizer)")
    ap.add_argument("--sugarcrepe-dir", default=str(SUGARCREPE_DIR))
    a = ap.parse_args(argv)
    out = Path(a.out) if a.out else Path(common.RUNS) / RUN_ID / "folds_hardneg.json"
    if out.exists():
        print(f"{out} exists; not overwriting (it is frozen once committed)", file=sys.stderr)
        return 2
    d = Path(a.sugarcrepe_dir)
    try:
        bad = verify_sha256(d)
        if bad:
            print(f"STOP: SHA-256 mismatch against SHA256SUMS.txt: {bad}", file=sys.stderr)
            return 2
        by_source: dict = {}
        excluded, rep = exclusion_ids(by_source=by_source)
        foil_ids = foil_pool_ids()
    except FileNotFoundError as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    sums = {s: sha256_lf(d / f"{s}.json") for s in SUBSETS}
    all_rows = load_sugarcrepe(d)
    l6 = h_l6(all_rows, excluded)
    if not l6["ok"]:
        print("STOP: H-L6 positive control failed: no SugarCrepe image id matches any excluded set (id format mismatch)", file=sys.stderr)
        return 2
    res = build(all_rows, excluded, folds.hf_token_counter(a.slow), exclusion_report=dict(rep, h_l6=l6), sha256=sums, foil_ids=foil_ids)
    folds.save_folds(res, out)
    print(json.dumps(dict(path=str(out), sha1=res["meta"]["sha1"], sha256=hashlib.sha256(out.read_bytes()).hexdigest(), sizes=dict(head=len(res["head"]), test=len(res["test"])),
                          per_subset=res["meta"]["per_subset"], row_filter=res["meta"]["row_filter"], missing_optional=rep["missing_optional"], h_l6=l6, h_l4=res["meta"]["h_l4"], h_l7=h_l7_samples(all_rows, by_source))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
