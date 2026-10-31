"""SAP addendum A7.2 item list for the Flickr30K transfer test of the frozen LRF: builds runs/P2-LRF-F30K-FOLD/{folds_f30k.json, builder_report.json, exclusions.json, leak_check.json, manifest.json}
and runs/P2-LRF-PLAN-F30K/family.json. CPU only, no model, no GPU. Spec: research/paper2/prereg/SAP-ADDENDUM-A7-F30K-2026-10-31.md.

    python -I exp_p2/gate/build_f30k_fold.py [--out-dir PATH] [--plan-dir PATH] [--f30k-dir PATH]        # refuses to overwrite

Inputs (untrusted data, read only by this script; nothing in them is ever executed): `<f30k-dir>/hf/flickr_annotations_30k.csv` (Hugging Face dataset nlphuji/flickr30k, column `split`) and
`<f30k-dir>/hf/flickr30k-images.zip`. Only the 1,000 `test`-split images are extracted, by basename, to `<f30k-dir>/test_images/<file name>` (the repository stores identifiers, never images).

A7.2, as implemented
  items      every test-split image in ASCENDING ORDER OF FILE NAME (Python string order of the `filename` column, e.g. '1000092795.jpg' < '10002456.jpg'), minus
             (a) the file does not decode (PIL open + full load + convert RGB), (b) dHash (64 bit, see `dhash`) Hamming distance <= 4 to any of the 500 COCO design images (the M4 items = runs/P2-GATE-FOLDS test + test_ext)
             or the 450 COCO fold images (the first 450 items of runs/P2-LRF-FOLD/folds_lrf.json, the n-rule's n_L), (c) no admissible negative in the pool. Every exclusion is listed with its reason in exclusions.json.
             The pool for the negatives is the set of items that survive (a) and (b); if (c) removes an item the pool and the indices are recomputed (fixpoint, deterministic).
  caption    the first caption of the image (caption index 0 of the `raw` list), whitespace-normalised as the COCO loader does (' '.join(c.split())).
  wrong      generator numpy.random.default_rng([2026, 1031, idx]) where idx is the item's position in the final list: draw j uniformly from the pool and redraw until j != idx and the two captions share
             no content word. Content word = a lower-case alphabetic word (re '[a-z]+') of three or more letters that is not in STOP_WORDS (fixed in this file before any draw).
  wrong_len  same generator, continued: among the items with no shared content word, those with exactly the same UniDisc caption token count; if none, those with the nearest token count (ties and sets: one drawn uniformly
             with rng.integers). The signed difference is stored (neg_len_diff), neg_len_exact = (difference == 0).
  gid        9000 + idx (disjoint from the COCO folds 0-2999, FOIL 4000/5000, H 6000/7000 and the LRF fold 8000-8532).
OPTION (off by default, NOT in A7.2): `--token-range-rule` adds exclusion (d) = the SAP A2.1 rule applied at build time (true caption outside 5 to 32 UniDisc tokens), before the pool of the negatives is formed. Reason: the pinned runner
stops the run (FoldDefect) when more than 10 percent of a fold fails that rule at run time, and 128 of the 1,000 Flickr30K first captions are longer than 32 tokens. Whether to use it is the lead's decision (an amendment of A7.2).
Token counts use folds.hf_token_counter (local tokenizer cache, identical to UniScorer.caption_ids). The 5 to 32 token rule of SAP A2.1 is NOT a selection step here (A7.2 lists no such step): the pinned runner applies it at run time
(pipeline.check_fold_tokens: such items are excluded, counted, not replaced; a defect above 10 percent stops the run). The builder only COUNTS them (builder_report.token_range) so that the scored n is known in advance."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import time
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import config, folds                                       # noqa: E402

RUN_ID = "P2-LRF-F30K-FOLD"
PLAN_RUN_ID = "P2-LRF-PLAN-F30K"
EVAL_RUN_ID = "P2-LRF-F30K"
GID_OFFSET = 9000
SEED_PREFIX = (2026, 1031)
HAMMING_MAX = 4
N_COCO_DESIGN, N_COCO_FOLD = 500, 450
MIN_SCORED = 800                                                            # A7.6
F30K_DIR = common.COCO_DIR.parent / "flickr30k"                             # sibling of the COCO folder: C:\Users\ANONYMIZED\.cache\dlm_dl\flickr30k
HF_REVISION = "2b239befc81b6e3f035ce6bd52f5f4d60f5625f7"                      # nlphuji/flickr30k, last_modified 2023-01-19
CSV_NAME, ZIP_NAME, HF_SUBDIR, IMAGE_SUBDIR = "flickr_annotations_30k.csv", "flickr30k-images.zip", "hf", "test_images"
SPEC = "research/paper2/prereg/SAP-ADDENDUM-A7-F30K-2026-10-31.md"

# Fixed English stop-word list (written before any draw; A7.2). Words of three or more letters only matter, shorter ones never count as content words anyway.
STOP_WORDS = frozenset("""
about above after again against all also and any are because been before being below between both but can could did does doing down during each few for from further had has have having her here hers herself him himself his
how into its itself just more most much must myself nor not now off once only other our ours ourselves out over own same she should some such than that the their theirs them themselves then there these they this those through
too under until upon very was were what when where which while who whom why will with would you your yours yourself yourselves one two""".split())

_WORD = re.compile(r"[a-z]+")


def norm_caption(c: str) -> str:
    return " ".join(str(c).split())


def content_words(caption: str) -> frozenset:
    return frozenset(w for w in _WORD.findall(caption.lower()) if len(w) >= 3 and w not in STOP_WORDS)


# ------------------------------------------------------------------------------------------------ images
def dhash(img) -> int:
    """64-bit difference hash: grey, resize to 9 x 8 (LANCZOS), bit (8 * row + col) = pixel[row, col] > pixel[row, col + 1]."""
    from PIL import Image
    a = np.asarray(img.convert("L").resize((9, 8), Image.LANCZOS), dtype=np.int16)
    bits = (a[:, :-1] > a[:, 1:]).astype(np.uint8).ravel()
    return int("".join(map(str, bits.tolist())), 2)


def hamming(a: int, b: int) -> int:
    return bin(int(a) ^ int(b)).count("1")


def decode_image(data: bytes):
    """PIL decode of the full file; None if it does not decode (exclusion a)."""
    from PIL import Image
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
        return im.convert("RGB")
    except Exception:                                                       # any decoder failure is exclusion (a)
        return None


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 22), b""):
            h.update(blk)
    return h.hexdigest()


def image_id_of(filename: str) -> int:
    stem = filename[:-4] if filename.lower().endswith(".jpg") else filename
    if not stem.isdigit() or f"{int(stem)}.jpg" != filename:
        raise ValueError(f"file name {filename!r} is not '<numeric Flickr id>.jpg'; the loader maps image_id back to the file name")
    return int(stem)


# ------------------------------------------------------------------------------------------------ annotations
def read_annotations(csv_path: Path, split: str = "test") -> list[dict]:
    """The rows of one split, ascending by file name (string order). Each: filename, image_id, caption0 (normalised), n_captions."""
    rows = []
    with open(csv_path, encoding="utf8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["split"] != split:
                continue
            caps = json.loads(r["raw"])
            if not isinstance(caps, list) or not caps or not all(isinstance(c, str) for c in caps):
                raise ValueError(f"row {r['filename']}: `raw` is not a non-empty list of strings")
            rows.append(dict(filename=r["filename"], image_id=image_id_of(r["filename"]), caption0=norm_caption(caps[0]), n_captions=len(caps)))
    rows.sort(key=lambda r: r["filename"])
    if len({r["filename"] for r in rows}) != len(rows):
        raise ValueError("duplicate file names in the split")
    return rows


def extract_test_images(zip_path: Path, filenames: list[str], image_dir: Path) -> dict[str, dict]:
    """Copy the named members (matched by basename; the zip path is never used to build a path) into `image_dir`. Returns filename -> {sha256, bytes, member}. Existing files are verified by re-reading, not trusted."""
    image_dir.mkdir(parents=True, exist_ok=True)
    want = set(filenames)
    out: dict[str, dict] = {}
    with zipfile.ZipFile(zip_path) as z:
        members = {}
        for info in z.infolist():
            base = info.filename.replace("\\", "/").rsplit("/", 1)[-1]
            if base in want and not info.is_dir() and not base.startswith("._"):          # skip macOS resource forks
                members.setdefault(base, info)
        missing = sorted(want - set(members))
        if missing:
            raise FileNotFoundError(f"{len(missing)} test images not in the zip, first: {missing[:5]}")
        for fn in sorted(want):
            data = z.read(members[fn])
            dest = image_dir / fn
            if not (dest.exists() and dest.read_bytes() == data):
                tmp = dest.with_name(dest.name + ".tmp")
                tmp.write_bytes(data)
                tmp.replace(dest)
            out[fn] = dict(sha256=sha256_bytes(data), bytes=len(data), member=members[fn].filename)
    return out


# ------------------------------------------------------------------------------------------------ the pure builder
def draw_negatives(caps: list[str], ntok: list[int]) -> tuple[list[dict], list[int]]:
    """A7.2 wrong and length-matched wrong captions for a list of c+ (the pool is the list itself). Returns (per-item dicts, indices without an admissible negative). The draws of index i use
    default_rng([2026, 1031, i]); the dicts are only complete when the second list is empty."""
    n = len(caps)
    W = [content_words(c) for c in caps]
    out, none_adm = [], []
    for i in range(n):
        adm = [j for j in range(n) if j != i and not (W[i] & W[j])]
        if not adm:
            none_adm.append(i)
            out.append(dict())
            continue
        rng = np.random.default_rng([*SEED_PREFIX, i])
        for _ in range(10_000_000):
            j = int(rng.integers(0, n))
            if j != i and not (W[i] & W[j]):
                break
        else:                                                               # pragma: no cover  (probability of reaching this is zero for any non-empty `adm`)
            raise RuntimeError(f"item {i}: no draw found")
        exact = [k for k in adm if ntok[k] == ntok[i]]
        if exact:
            cands = exact
        else:
            d = min(abs(ntok[k] - ntok[i]) for k in adm)
            cands = [k for k in adm if abs(ntok[k] - ntok[i]) == d]
        jl = int(cands[int(rng.integers(0, len(cands)))])
        out.append(dict(neg_idx=j, neg_len_idx=jl, n_adm=len(adm), n_cands_len=len(cands)))
    return out, none_adm


def build(rows: list[dict], decoded: dict[str, bool], coco_dist: dict[str, tuple[int, int]], n_tok_fn, *, hamming_max: int = HAMMING_MAX, token_range_rule: bool = False) -> dict:
    """rows: the ascending-file-name test rows (read_annotations). decoded: filename -> does it decode. coco_dist: filename -> (min Hamming distance to the COCO design + fold images, the COCO image id).
    Returns dict(fold=<folds-schema dict>, exclusions=[...], report=<counts>)."""
    excl: list[dict] = []
    alive = []
    for r in rows:
        fn = r["filename"]
        if not decoded.get(fn, False):
            excl.append(dict(filename=fn, image_id=r["image_id"], reason="a_undecodable"))
        elif coco_dist[fn][0] <= hamming_max:
            excl.append(dict(filename=fn, image_id=r["image_id"], reason="b_near_duplicate_of_coco", hamming=coco_dist[fn][0], coco_image_id=coco_dist[fn][1]))
        else:
            alive.append(r)
    cache: dict[str, int] = {}

    def nt(c: str) -> int:
        if c not in cache:
            cache[c] = int(n_tok_fn(c))
        return cache[c]
    if token_range_rule:                                                    # optional exclusion (d); not part of A7.2 as written
        lo_, hi_ = config.TOK_RANGE
        keep = []
        for r in alive:
            m = nt(r["caption0"])
            if lo_ <= m <= hi_:
                keep.append(r)
            else:
                excl.append(dict(filename=r["filename"], image_id=r["image_id"], reason="d_token_range_5_32", n_tok=m))
        alive = keep
    iterations = 0
    while True:
        iterations += 1
        caps = [r["caption0"] for r in alive]
        ntok = [nt(c) for c in caps]
        neg, none_adm = draw_negatives(caps, ntok)
        if not none_adm:
            break
        for i in none_adm:
            excl.append(dict(filename=alive[i]["filename"], image_id=alive[i]["image_id"], reason="c_no_admissible_negative"))
        alive = [r for i, r in enumerate(alive) if i not in set(none_adm)]
    items = []
    for i, (r, d) in enumerate(zip(alive, neg)):
        j, jl = d["neg_idx"], d["neg_len_idx"]
        items.append(dict(idx=i, gid=GID_OFFSET + i, image_id=r["image_id"], caption=caps[i], n_tok=ntok[i],
                          neg_idx=j, neg_image_id=alive[j]["image_id"], neg_caption=caps[j], neg_restricted=False, n_tok_neg=ntok[j],
                          neg_caption_len=caps[jl], neg_len_idx=jl, neg_len_image_id=alive[jl]["image_id"], n_tok_neg_len=ntok[jl], neg_len_diff=int(ntok[jl] - ntok[i]),
                          neg_len_exact=bool(ntok[jl] == ntok[i]), neg_len_restricted=False, filename=r["filename"]))
    lo, hi = config.TOK_RANGE
    n = len(items)
    outside = [it["idx"] for it in items if not (lo <= it["n_tok"] <= hi)]
    d = np.array([abs(it["neg_len_diff"]) for it in items]) if items else np.zeros(0)
    report = dict(n_test_split=len(rows), n_excluded_a_undecodable=sum(e["reason"] == "a_undecodable" for e in excl), n_excluded_b_near_duplicate=sum(e["reason"] == "b_near_duplicate_of_coco" for e in excl),
                  n_excluded_c_no_admissible_negative=sum(e["reason"] == "c_no_admissible_negative" for e in excl),
                  n_excluded_d_token_range=sum(e["reason"] == "d_token_range_5_32" for e in excl), token_range_rule_applied=bool(token_range_rule), n_kept=n, c_fixpoint_iterations=iterations,
                  token_range=dict(rule="SAP A2.1 5 to 32 UniDisc caption tokens; applied by the pinned runner at run time (excluded, counted, not replaced), only COUNTED here", n_outside=len(outside), outside_idx=outside,
                                   fraction_outside=(len(outside) / n if n else None), defect_threshold=folds.MAX_FAIL_FRACTION, n_expected_scored=n - len(outside),
                                   would_stop_run=bool(n and len(outside) / n > folds.MAX_FAIL_FRACTION)),
                  length_matching=dict(n=n, n_exact=int(sum(it["neg_len_exact"] for it in items)), n_not_exact=int((d > 0).sum()), mean_abs_diff=(float(d.mean()) if n else None), max_abs_diff=(int(d.max()) if n else None)),
                  primary_negative=dict(mean_abs_token_diff=(float(np.mean([abs(it["n_tok_neg"] - it["n_tok"]) for it in items])) if n else None)),
                  n_adm_min=(min(x["n_adm"] for x in neg) if n else None))
    fold = dict(meta=dict(seed_prefix=list(SEED_PREFIX), sizes=[0, 0, n], test_base=n, tok_range=[lo, hi], family="F30K", annotations_used=False, gid_offset=GID_OFFSET, dataset="Flickr30K test split (Karpathy), HF nlphuji/flickr30k",
                          spec=SPEC, token_range_rule_applied=bool(token_range_rule), length_matching=report["length_matching"]), cal=[], head=[], test=items, test_ext=[])
    fold["meta"]["sha1"] = hashlib.sha1(json.dumps({k: fold[k] for k in ("cal", "head", "test", "test_ext")}, sort_keys=True).encode()).hexdigest()[:16]
    return dict(fold=fold, exclusions=excl, report=report)


# ------------------------------------------------------------------------------------------------ checks
class LeakCheckFailed(RuntimeError):
    def __init__(self, msg: str, log: dict):
        super().__init__(msg)
        self.log = log


def _chk(log: dict, name: str, ok: bool, detail) -> bool:
    log["checks"].append(dict(name=name, ok=bool(ok), detail=detail))
    return bool(ok)


def leak_check(fold: dict, coco_dist: dict[str, tuple[int, int]], rows: list[dict], *, hamming_max: int = HAMMING_MAX, expected_n: int | None = None) -> dict:
    """F0 to F6 on a built fold; raises LeakCheckFailed (with the log) on a failure.
      F0 ids are the integers of '<id>.jpg', unique; items are in ascending file-name order; idx = position; gid = 9000 + idx
      F1 the gid range is free (the COCO ranges, FOIL, H and the LRF fold 8000-8532 are not touched)
      F2 every kept image has dHash distance > hamming_max to all 950 COCO images (re-checked from the stored distances)
      F3 each primary and length-matched negative is another item's c+, shares no content word with c+, and the length fields are consistent
      F4 only the test fold is filled"""
    log = dict(checks=[], created=time.strftime("%Y-%m-%dT%H:%M:%S"))
    items = fold["test"]
    fns = [it["filename"] for it in items]
    ids = [it["image_id"] for it in items]
    _chk(log, "F0_ids_are_integers_unique_and_match_file_names", all(isinstance(i, int) and not isinstance(i, bool) for i in ids) and len(set(ids)) == len(ids) and all(f == f"{i}.jpg" for f, i in zip(fns, ids)), dict(n=len(ids)))
    _chk(log, "F0_ascending_file_name_order_and_idx_is_position", fns == sorted(fns) and [it["idx"] for it in items] == list(range(len(items))) and [it["gid"] for it in items] == [GID_OFFSET + i for i in range(len(items))], dict(first=fns[:2]))
    _chk(log, "F0_items_subset_of_test_split", set(fns) <= {r["filename"] for r in rows}, dict(n_test_split=len(rows)))
    if expected_n is not None:
        _chk(log, "F0_item_count", len(items) == expected_n, dict(n=len(items), expected=expected_n))
    from exp_p2.gate import build_lrf_fold as blf
    taken = dict(blf.used_gid_ranges())
    taken["lrf_fold"] = (blf.GID_OFFSET, blf.GID_OFFSET + blf.N_L)
    gids = [it["gid"] for it in items]
    clash = {k: sum(lo <= g < hi for g in gids) for k, (lo, hi) in taken.items()}
    _chk(log, "F1_gid_free_and_distinct", len(set(gids)) == len(gids) and not any(clash.values()), dict(min=min(gids), max=max(gids), clashes=clash))
    d = [coco_dist[f][0] for f in fns]
    _chk(log, "F2_min_hamming_to_coco_above_threshold", all(x > hamming_max for x in d), dict(threshold=hamming_max, min_distance_kept=min(d), n_kept_within_8=int(sum(x <= 8 for x in d)), n_kept=len(d)))
    bad = []
    for it in items:
        for pre, key in (("neg_", "neg_caption"), ("neg_len_", "neg_caption_len")):
            j = it[pre + "idx"]
            ok = items[j]["caption"] == it[key] and items[j]["image_id"] == it[pre + "image_id"] and j != it["idx"] and it[key] != it["caption"] and not (content_words(it["caption"]) & content_words(it[key]))
            if not ok:
                bad.append((it["idx"], pre))
        if it["neg_len_diff"] != it["n_tok_neg_len"] - it["n_tok"] or it["neg_len_exact"] != (it["neg_len_diff"] == 0) or it["n_tok_neg"] != items[it["neg_idx"]]["n_tok"]:
            bad.append((it["idx"], "diff"))
    _chk(log, "F3_negatives_consistent_and_word_disjoint", not bad, dict(n_bad=len(bad), first=bad[:5]))
    _chk(log, "F4_only_test_fold_filled", not fold.get("cal") and not fold.get("head") and not fold.get("test_ext"), dict())
    log["ok"] = all(c["ok"] for c in log["checks"])
    if not log["ok"]:
        raise LeakCheckFailed("F30K fold check failed: " + ", ".join(c["name"] for c in log["checks"] if not c["ok"]), log)
    return log


def dhash_positive_control(coco_images: list) -> dict:
    """The exclusion rule must catch a known near-duplicate: re-encode COCO images (JPEG quality 70, 90 percent resize) and require distance <= HAMMING_MAX for nearly all; and two different COCO images must be far apart."""
    from PIL import Image
    ds, far = [], []
    for k, im in enumerate(coco_images):
        w, h = im.size
        buf = io.BytesIO()
        im.resize((max(1, int(w * 0.9)), max(1, int(h * 0.9))), Image.BILINEAR).save(buf, "JPEG", quality=70)
        ds.append(hamming(dhash(im), dhash(Image.open(io.BytesIO(buf.getvalue())).convert("RGB"))))
        far.append(hamming(dhash(im), dhash(coco_images[(k + 1) % len(coco_images)])))
    return dict(n=len(ds), max_distance_recompressed_copy=int(max(ds)), n_caught=int(sum(x <= HAMMING_MAX for x in ds)), min_distance_between_different_images=int(min(far)),
                ok=bool(ds and sum(x <= HAMMING_MAX for x in ds) >= 0.95 * len(ds) and sum(x <= HAMMING_MAX for x in far) <= 0.02 * len(far)))


# ------------------------------------------------------------------------------------------------ the CLI
def coco_reference_ids(runs: Path) -> tuple[list[int], list[int]]:
    """(500 COCO design image ids = test + test_ext of runs/P2-GATE-FOLDS/folds.json = the M4 items; 450 COCO fold ids = the first n_L of runs/P2-LRF-FOLD/folds_lrf.json)."""
    f = json.loads((runs / config.FOLDS_RUN_ID / "folds.json").read_text(encoding="utf8"))
    design = [int(it["image_id"]) for it in f["test"] + f["test_ext"]]
    lrf = json.loads((runs / "P2-LRF-FOLD" / "folds_lrf.json").read_text(encoding="utf8"))
    fold = [int(it["image_id"]) for it in lrf["test"][:N_COCO_FOLD]]
    if len(design) != N_COCO_DESIGN or len(fold) != N_COCO_FOLD or len(set(design)) != len(design) or len(set(fold)) != len(fold):
        raise ValueError(f"COCO reference sets have {len(design)} / {len(fold)} ids (expected {N_COCO_DESIGN} / {N_COCO_FOLD}, unique)")
    return design, fold


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--f30k-dir", default=str(F30K_DIR))
    ap.add_argument("--out-dir", default=None, help=f"default: runs/{RUN_ID}")
    ap.add_argument("--plan-dir", default=None, help=f"default: runs/{PLAN_RUN_ID}")
    ap.add_argument("--slow", action="store_true", help="slow SentencePiece tokenizer")
    ap.add_argument("--token-range-rule", action="store_true", help="NOT in A7.2: also exclude items whose true caption is outside 5 to 32 UniDisc tokens (SAP A2.1) at build time; lead's decision")
    a = ap.parse_args(argv)
    f30k = Path(a.f30k_dir)
    runs = Path(common.RUNS)
    out_dir = Path(a.out_dir) if a.out_dir else runs / RUN_ID
    plan_dir = Path(a.plan_dir) if a.plan_dir else runs / PLAN_RUN_ID
    targets = [out_dir / n for n in ("folds_f30k.json", "builder_report.json", "exclusions.json", "leak_check.json", "manifest.json")] + [plan_dir / "family.json"]
    if any(t.exists() for t in targets):
        print(f"{[str(t) for t in targets if t.exists()]} exist; not overwriting (frozen once committed)", file=sys.stderr)
        return 2
    csv_path, zip_path, image_dir = f30k / HF_SUBDIR / CSV_NAME, f30k / HF_SUBDIR / ZIP_NAME, f30k / IMAGE_SUBDIR
    try:
        rows = read_annotations(csv_path)
        design_ids, fold_ids = coco_reference_ids(runs)
        info = extract_test_images(zip_path, [r["filename"] for r in rows], image_dir)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    if len(rows) != 1000:
        print(f"STOP: the test split has {len(rows)} rows, A7.2 says 1,000", file=sys.stderr)
        return 2
    decoded, f30k_hash, bad_files = {}, {}, []
    for r in rows:
        im = decode_image((image_dir / r["filename"]).read_bytes())
        decoded[r["filename"]] = im is not None
        if im is not None:
            f30k_hash[r["filename"]] = dhash(im)
        else:
            bad_files.append(r["filename"])
    coco_imgs = {iid: common.load_image(iid) for iid in sorted(set(design_ids) | set(fold_ids))}
    coco_hash = {iid: dhash(im) for iid, im in coco_imgs.items()}
    coco_dist = {}
    for fn, h in f30k_hash.items():
        iid, dist = min(((i, hamming(h, ch)) for i, ch in coco_hash.items()), key=lambda t: (t[1], t[0]))
        coco_dist[fn] = (dist, iid)
    for fn in bad_files:
        coco_dist[fn] = (64, -1)
    res = build(rows, decoded, coco_dist, folds.hf_token_counter(a.slow), token_range_rule=a.token_range_rule)
    fold, rep = res["fold"], res["report"]
    try:
        log = leak_check(fold, coco_dist, rows)
    except LeakCheckFailed as e:
        print("STOP:", e, file=sys.stderr)
        print(json.dumps(e.log, indent=1), file=sys.stderr)
        return 2
    log["dhash_positive_control"] = pc = dhash_positive_control([coco_imgs[i] for i in design_ids[:100]])
    if not pc["ok"]:
        print("STOP: dHash positive control failed:", pc, file=sys.stderr)
        return 2
    dists = sorted(d for d, _ in coco_dist.values())
    log["hamming_distribution_all_decoded_test_images"] = dict(min=dists[0], n_le_4=sum(d <= 4 for d in dists), n_5_to_8=sum(5 <= d <= 8 for d in dists), n_9_to_12=sum(9 <= d <= 12 for d in dists), median=float(np.median(dists)))
    out_dir.mkdir(parents=True, exist_ok=True)
    plan_dir.mkdir(parents=True, exist_ok=True)
    folds.save_folds(fold, targets[0])
    rep.update(dataset=dict(name="nlphuji/flickr30k", revision=HF_REVISION, split="test (standard Karpathy split, 1,000 images)", csv_sha256=sha256_file(csv_path), zip_sha256=sha256_file(zip_path), image_dir=str(image_dir)),
               licence=dict(hf_dataset_card="no licence field in the dataset card (README.md has the paper reference and the homepage link only; card_data is empty)",
                            homepage_https_shannon_cs_illinois_edu_DenotationGraph="images offered for non-commercial research and/or educational purposes; use must abide by the Flickr Terms of Use; the authors do not own the image copyright; access is by request form; no separate caption terms stated; redistribution not addressed (read 2026-10-31 via WebFetch summary)",
                            repository_rule="identifiers only; no image is stored in the repository"),
               coco_reference=dict(n_design=len(design_ids), n_fold=len(fold_ids), design_source="runs/P2-GATE-FOLDS/folds.json test + test_ext (= the 500 M4 items)", fold_source="runs/P2-LRF-FOLD/folds_lrf.json test[:450]"),
               tokenizer="folds.hf_token_counter (fast, local cache)", stop_words=sorted(STOP_WORDS), hamming_max=HAMMING_MAX, undecodable_files=bad_files)
    targets[1].write_text(json.dumps(rep, indent=1), encoding="utf8")
    targets[2].write_text(json.dumps(dict(n=len(res["exclusions"]), items=res["exclusions"]), indent=1), encoding="utf8")
    targets[3].write_text(json.dumps(log, indent=1), encoding="utf8")
    manifest = dict(meta=fold["meta"], folds_f30k_sha256=sha256_file(targets[0]), image_sha256={fn: v["sha256"] for fn, v in sorted(info.items())}, image_members={fn: v["member"] for fn, v in sorted(info.items())},
                    csv_sha256=rep["dataset"]["csv_sha256"], zip_sha256=rep["dataset"]["zip_sha256"], code="exp_p2/gate/build_f30k_fold.py", spec=SPEC, created=time.strftime("%Y-%m-%dT%H:%M:%S"))
    targets[4].write_text(json.dumps(manifest, indent=1), encoding="utf8")
    fam = json.loads((runs / "P2-LRF-PLAN" / "family.json").read_text(encoding="utf8"))
    noise = [f for f in fam["family"] if f["corruption"] == "noise" and f["key"] == "noise0.1"]
    if len(noise) != 1:
        print("STOP: runs/P2-LRF-PLAN/family.json has no single noise0.1 cell", file=sys.stderr)
        return 2
    plan = dict(endpoint=fam["endpoint"], family=noise, n_rule=dict(rule="all kept items, A7.2", test_fold=len(fold["test"])),
                sources=dict(l1_family="runs/P2-LRF-PLAN/family.json", l1_family_sha256=sha256_file(runs / "P2-LRF-PLAN" / "family.json"), folds_f30k_sha256=manifest["folds_f30k_sha256"]), spec="exp_p2/gate/build_f30k_fold.py")
    targets[5].write_text(json.dumps(plan, indent=1), encoding="utf8")
    print(json.dumps(dict(path=str(targets[0]), sha1=fold["meta"]["sha1"], n_kept=rep["n_kept"], excluded=dict(a=rep["n_excluded_a_undecodable"], b=rep["n_excluded_b_near_duplicate"], c=rep["n_excluded_c_no_admissible_negative"], d=rep["n_excluded_d_token_range"]),
                          token_range=dict(n_outside=rep["token_range"]["n_outside"], n_expected_scored=rep["token_range"]["n_expected_scored"], would_stop_run=rep["token_range"]["would_stop_run"]),
                          length_matching=rep["length_matching"], min_hamming_overall=dists[0])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
