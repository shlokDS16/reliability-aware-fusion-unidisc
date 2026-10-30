"""Family B (SAP Addendum A2, AD.6 with AB.6): FOIL-COCO hard negatives. CPU only; no model, no GPU.

One pair is one COCO val2017 image with its original caption c+ and a published FOIL caption c- (one noun replaced). This module holds
  - the data access (the FOIL test file, verified by SHA-256 against the data-steward's manifest),
  - the pair construction (the pair key is the COCO caption `id`, which the original and the foil record share; see `build_pairs`),
  - the pool (`foil_pool`), the leakage check L1 to L5 with the id-matching positive control L0 and L6 to L8 (`foil_leak_check`, `selftest`),
  - the fusion analysis B1 (`fit_b1`, `fusion_b1`).
The GPU runner is `exp_p2/run_gate_foil.py`; the CPU analysis CLI is `exp_p2/gate/analysis_foil.py`.

    python -m exp_p2.gate.foil build-pool [--no-tokens]     # writes runs/P2-GATE-FOIL/{manifest,pool,leak_check}.json (commit them before any GPU use)
    python -m exp_p2.gate.foil check                       # re-runs the leak check on the committed pool
    python -m exp_p2.gate.foil selftest                    # L8 and the other known-bad cases

Everything about the data is the data-steward's note `research/paper2/related/DATA-CHECK-FOIL-CORRUPTIONS-2026-10-28.md` (E1/E4) plus what `build_pairs` asserts on the file itself.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import artifacts, config, data, folds as folds_mod, fusion, mde as mde_mod, report, seeds   # noqa: E402

FOIL_RUN_ID = "P2-GATE-FOIL"                       # family directory: manifest, pool, leak check, fusion_frozen.json, analysis.json
FIT_RUN_ID, TEST_RUN_ID = "P2-GATE-FOIL-FIT", "P2-GATE-FOIL-TEST"
FOIL_FILE = "foilv1.0_test_2017.json"
FOIL_SHA256 = "7b37ab2a4e3dc911d006d5941919245c47d1e67d2ee29b4f7a87d5ecc9284642"      # data-steward note, section 1 (recomputed here on every load)
FOIL_BYTES = 45_080_997
FOIL_URL = "https://www.dropbox.com/s/u4ntgo73szg6yai/foilv1.0_test_2017.json"         # project page https://foilunitn.github.io/ (steward)
SEED_POOL = 20261031                              # AD.6: fixed-seed permutation of the remaining eligible images
N_TEST_PLANNED = 300                              # ANONYMIZED approved n = 300 (AD.6 planned 150); the pool is the first 300 eligible pairs
N_FIT_MAX = 300                                   # fit pairs: FOIL pairs whose image is in folds.json "cal" (at most 300)
N_SENS = 150                                      # A3.1 item 3 / A3b.3 item 8: the recorded sensitivity is the first 150 pool positions
MIN_FIT, CEILING, MIN_COMPLETE, ALPHA = 100, 0.95, 120, 0.05           # AD.6 "rules before any B-test item", "completed n < 120 makes it descriptive", alpha 0.05
GID_FIT, GID_TEST = 4000, 5000                    # global ids for seeds/dcache bookkeeping; the folds use 0 to 2499
THRESHOLD_NOTE = "AD.6: rules (i) fit pairs >= 100, (ii) best single direction accuracy >= 0.95 on the fit pairs = untestable at ceiling, (iii) fusion_frozen.json committed"


class FoilFormatError(RuntimeError):
    """The FOIL file does not have the structure this module asserts (pair key, one original and one foil per id)."""


class LeakCheckFailed(RuntimeError):
    def __init__(self, msg: str, log: dict):
        super().__init__(msg)
        self.log = log


# ------------------------------------------------------------------------------------------------ data access
def foil_path() -> Path:
    return Path(common.COCO_DIR) / "foil" / FOIL_FILE        # outside the repository (the COCO cache); it cannot be committed


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_file(path: Path | None = None) -> dict:
    p = Path(path) if path else foil_path()
    if not p.exists():
        raise FileNotFoundError(f"{p} missing: copy foilv1.0_test_2017.json there (data-steward note; SHA-256 {FOIL_SHA256})")
    sha = sha256_file(p)
    if sha != FOIL_SHA256:
        raise FoilFormatError(f"{p}: SHA-256 {sha} differs from the manifest {FOIL_SHA256}")
    return dict(path=str(p), sha256=sha, bytes=p.stat().st_size)


def load_foil(path: Path | None = None) -> dict:
    verify_file(path)
    return json.loads(Path(path or foil_path()).read_text(encoding="utf8"))


def write_manifest(out: Path | None = None) -> dict:
    """runs/P2-GATE-FOIL/manifest.json: what the file is, where it came from (steward), its SHA-256 recomputed now. The file itself stays in the COCO cache, not in git."""
    v = verify_file()
    man = dict(dataset="FOIL-COCO (Shekhar et al., ACL 2017, FOIL it! Find One mismatch between Image and Language caption)", file=FOIL_FILE, sha256=v["sha256"], bytes=v["bytes"],
               expected_bytes=FOIL_BYTES, source_url=FOIL_URL, project_page="https://foilunitn.github.io/", licence="CC BY 4.0 (University of Trento); images: Flickr terms of use (data-steward, E1)",
               local_path=v["path"], in_git=False, why_not_in_git="45 MB and outside the repository (COCO cache directory); the SHA-256 above is verified on every load",
               steward_note="research/paper2/related/DATA-CHECK-FOIL-CORRUPTIONS-2026-10-28.md", copied_by="lab-engineer (implementer B) from the steward's scratchpad download", verified_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
               unknown="whether this file is the Oct 2018 revision (the JSON info block says 'July 2017'); stated in the paper if B is reported")
    out = Path(out) if out else Path(common.RUNS) / FOIL_RUN_ID / "manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(man, indent=1), encoding="utf8")
    return man


# ------------------------------------------------------------------------------------------------ ids (L0)
_ID_RE = re.compile(r"(\d+)(?:\.jpg)?$")


def normalise_image_id(x) -> int:
    """L0, the documented mapping from FOIL image ids to COCO integer ids. FOIL `images[].id` is the COCO integer id (e.g. 391895); `images[].file_name` is
    `COCO_val2014_000000391895.jpg` (zero-padded to 12 digits); the val2017 member is `val2017/000000391895.jpg`. COCO ids are unchanged between the 2014 and 2017 splits
    (steward: 712 of our 900 fold ids are in the FOIL test list, 0 in the train list). Accepts an int, an int-like string, or any file name ending in the id. The leak check uses
    ONLY this function on both sides, so a format mismatch cannot hide."""
    if isinstance(x, (int, np.integer)):
        return int(x)
    m = _ID_RE.search(str(x).strip().replace("\\", "/").rsplit("/", 1)[-1])
    if not m:
        raise ValueError(f"cannot read a COCO image id from {x!r}")
    return int(m.group(1))


def coco_member(image_id: int) -> str:
    return f"val2017/{int(image_id):012d}.jpg"


def check_id_mapping(foil: dict) -> dict:
    """L0 evidence on the whole file: for every FOIL image record, `id` equals the id read from `file_name`, and the name has the val2014 prefix."""
    n, bad, prefix_bad = 0, [], 0
    for im in foil["images"]:
        n += 1
        if normalise_image_id(im["file_name"]) != int(im["id"]):
            bad.append(im["id"])
        if not str(im["file_name"]).startswith("COCO_val2014_"):
            prefix_bad += 1
    return dict(n_images=n, n_id_filename_mismatch=len(bad), first_mismatches=bad[:5], n_not_val2014_prefix=prefix_bad)


# ------------------------------------------------------------------------------------------------ captions and pairs
def norm_caption(s: str) -> str:
    """Lower case, collapse white space. Applied to BOTH sides of every pair: the file has a case leak (0.0% of 99,480 foil captions start with a capital against 85.1% of the originals,
    steward) and the originals carry trailing blanks, so unnormalised captions would let the model separate foils by surface form."""
    return " ".join(str(s).lower().split())


def build_pairs(foil: dict) -> tuple[list[dict], dict]:
    """One pair per image: the first record for that image in the order of the released file (AD.6). The pair partner is the record with the same `id`: in the test file `id` is the COCO
    caption id and every id occurs exactly twice, once as the original (foil False) and once as the foil (True) (asserted for the whole file). [The steward's note says the file has no pair key because
    `foil_id` is unique per caption; `id` is shared and is the key. The replacement relation (target word -> foil word) is checked as a diagnostic.] Returns (pairs in file order of their first record, stats)."""
    anns = foil["annotations"]
    groups: dict[int, list[int]] = {}
    for i, r in enumerate(anns):
        groups.setdefault(int(r["id"]), []).append(i)
    bad = [k for k, v in groups.items() if len(v) != 2 or sorted(bool(anns[j]["foil"]) for j in v) != [False, True] or len({int(anns[j]["image_id"]) for j in v}) != 1]
    if bad:
        raise FoilFormatError(f"{len(bad)} caption ids are not exactly one original plus one foil on one image (first: {bad[:3]}); the pair key assumption fails")
    seen, pairs, n_first_is_foil, n_one_word = set(), [], 0, 0
    for i, r in enumerate(anns):
        img = int(r["image_id"])
        if img in seen:
            continue
        seen.add(img)
        g = groups[int(r["id"])]
        o = anns[next(j for j in g if not anns[j]["foil"])]
        f = anns[next(j for j in g if anns[j]["foil"])]
        n_first_is_foil += int(bool(r["foil"]))
        c_pos, c_neg = norm_caption(o["caption"]), norm_caption(f["caption"])
        one_word = sum(a != b for a, b in zip(c_pos.split(), c_neg.split())) == 1 and len(c_pos.split()) == len(c_neg.split())
        n_one_word += int(one_word)
        pairs.append(dict(pair_id=int(r["id"]), image_id=img, file_order=i, c_pos=c_pos, c_neg=c_neg, target_word=f["target_word"], foil_word=f["foil_word"], one_word_diff=bool(one_word)))
    return pairs, dict(n_records=len(anns), n_caption_ids=len(groups), n_images=len(pairs), n_first_record_is_foil=n_first_is_foil, n_pairs_one_word_difference=n_one_word,
                       n_identical_after_normalisation=sum(p["c_pos"] == p["c_neg"] for p in pairs))


# ------------------------------------------------------------------------------------------------ pool
def _ids(items) -> list[int]:
    return [normalise_image_id(it["image_id"]) for it in items]


def eligible_order(pairs: list[dict], folds: dict, probe_ids: set[int], val_ids: set[int], *, seed: int = SEED_POOL) -> tuple[list[dict], dict]:
    """The ordered list of eligible test pairs and the counts by reason (L5). Eligible: image in COCO val2017 and not in folds.json "cal"/"head" nor in the probe-1/probe-2 id lists.
    Order (AD.6): the images of folds.json "test" then "test_ext" in their stored order, then the remaining eligible images by a seeded permutation of their sorted ids."""
    cal, head = set(_ids(folds["cal"])), set(_ids(folds["head"]))
    probe = {normalise_image_id(i) for i in probe_ids}
    val = {normalise_image_id(i) for i in val_ids}
    reasons = Counter()
    ok: dict[int, dict] = {}
    for p in pairs:
        i = p["image_id"]
        if i not in val:
            reasons["not_in_val2017"] += 1
        elif i in cal:
            reasons["in_calibration_fold"] += 1
        elif i in head:
            reasons["in_headroom_fold"] += 1
        elif i in probe:
            reasons["in_probe1_or_probe2"] += 1
        else:
            ok[i] = p
    stored = _ids(folds["test"]) + _ids(folds.get("test_ext", []))
    first = [i for i in stored if i in ok]
    in_first = set(first)
    rest = sorted(i for i in ok if i not in in_first)
    perm = np.random.default_rng(seed).permutation(len(rest))
    order = first + [rest[int(j)] for j in perm]
    counts = dict(n_candidate_pairs=len(pairs), n_eligible=len(ok), excluded_by_reason=dict(reasons), n_eligible_in_folds_test=len([i for i in _ids(folds["test"]) if i in ok]),
                  n_eligible_in_folds_test_ext=len([i for i in _ids(folds.get("test_ext", [])) if i in ok]), n_eligible_from_permutation=len(rest))
    return [ok[i] for i in order], counts


def apply_token_rule(items: list[dict], n_tok_fn, tok_range=config.TOK_RANGE) -> Counter:
    """Mark (not drop, not replace) pairs whose c+ or c- has a token count outside 5 to 32 (A2.1 item 2). Sets it['n_tok_pos'], it['n_tok_neg'], it['excluded'] (reason or None)."""
    lo, hi = tok_range
    why = Counter()
    for it in items:
        a, b = n_tok_fn(it["c_pos"]), n_tok_fn(it["c_neg"])
        it["n_tok_pos"], it["n_tok_neg"] = int(a), int(b)
        pa, pb = not (lo <= a <= hi), not (lo <= b <= hi)
        it["excluded"] = "pos_and_neg_out_of_range" if (pa and pb) else "pos_out_of_range" if pa else "neg_out_of_range" if pb else None
        if it["excluded"]:
            why[it["excluded"]] += 1
    return why


def foil_pool(pairs: list[dict], folds: dict, probe_ids: set[int], val_ids: set[int], *, n_test: int = N_TEST_PLANNED, n_fit_max: int = N_FIT_MAX, seed: int = SEED_POOL,
              n_tok_fn=None, tok_range=config.TOK_RANGE, file_sha: str | None = None) -> dict:
    """Pool construction (AD.6). test = the first `n_test` eligible pairs in the order of `eligible_order`; fit = FOIL pairs whose image is in folds.json "cal", in the cal order, at most
    `n_fit_max`. The caption token rule is applied by marking (excluded, counted by reason, NOT replaced), so completed n can be below the planned n. idx is the position in the planned list
    (stable under exclusions); gid = GID_FIT + idx or GID_TEST + idx. The pool list is written and committed before any GPU use."""
    order, counts = eligible_order(pairs, folds, probe_ids, val_ids, seed=seed)
    by_img = {p["image_id"]: p for p in pairs}
    test = [dict(p) for p in order[:n_test]]
    fit = [dict(by_img[i]) for i in _ids(folds["cal"]) if i in by_img][:n_fit_max]
    in_p_fold = set(_ids(folds["test"])) | set(_ids(folds.get("test_ext", [])))
    tok = {}
    for name, lst, off in (("fit", fit, GID_FIT), ("test", test, GID_TEST)):
        for k, it in enumerate(lst):
            it["idx"], it["gid"], it["split"] = k, off + k, name
            it["in_P_test_fold"] = bool(it["image_id"] in in_p_fold)
        if n_tok_fn is not None:
            tok[name] = dict(apply_token_rule(lst, n_tok_fn, tok_range))
        else:
            for it in lst:
                it["excluded"] = None
    counts.update(n_fit_candidates=len(fit), n_test_planned=len(test), n_test_in_P_test_fold=int(sum(it["in_P_test_fold"] for it in test)),
                  token_rule_excluded_at_pool_time=tok if n_tok_fn is not None else "not applied at pool time (runtime tokenizer decides; no replacement)",
                  n_fit_after_pool_time_token_rule=sum(1 for it in fit if not it["excluded"]), n_test_after_pool_time_token_rule=sum(1 for it in test if not it["excluded"]))
    meta = dict(spec="SAP A2 AD.6 + AB.6", foil_sha256=file_sha, folds_sha1=folds.get("meta", {}).get("sha1"), seed=seed, n_test_planned=n_test, n_fit_max=n_fit_max, tok_range=list(tok_range),
                token_counter=("given" if n_tok_fn is not None else None), pair_key="annotations[].id (shared by the original and the foil record)", caption_normalisation="lower case, white space collapsed, both sides",
                created=time.strftime("%Y-%m-%dT%H:%M:%S"))
    return dict(meta=meta, counts=counts, fit=fit, test=test)


def pool_sha256(pool: dict) -> str:
    keys = ("image_id", "pair_id", "c_pos", "c_neg", "idx", "gid", "excluded")
    return hashlib.sha256(json.dumps([[{k: it.get(k) for k in keys} for it in pool[s]] for s in ("fit", "test")], sort_keys=True).encode("utf8")).hexdigest()


# ------------------------------------------------------------------------------------------------ leak check (L0-L8)
def _chk(log: dict, name: str, ok: bool, detail) -> bool:
    log["checks"].append(dict(name=name, ok=bool(ok), detail=detail))
    return bool(ok)


def foil_leak_check(pool: dict, folds: dict, probe_ids: set[int], *, foil_images: list[dict] | None = None, val_ids: set[int] | None = None, coco_names: set[str] | None = None,
                    n_test_planned: int | None = None) -> dict:
    """L1 to L5 of AD.6 and the id-matching positive control L0, L6, L7 of AB.6. Raises LeakCheckFailed (with the log attached) on any failed assertion: B stops.
      L0 every id is read through `normalise_image_id` (the documented FOIL -> COCO integer -> val2017 mapping); with `foil_images` the whole FOIL image list is checked for id/file-name agreement
         and every pool id must be in val2017
      L1 fit ids subset of folds "cal"          L2 fit ids and test ids disjoint
      L3 test ids disjoint from "cal", "head" and the probe-1/probe-2 ids       L4 no image id repeated in either set
      L5 counts (candidates, eligible, excluded by reason) are in the log
      L6 count of FOIL image ids matching ANY id of cal, head, test, test_ext or the probe lists after normalisation; must be > 0 for each of the five groups (zero = format mismatch = 'leak check vacuous')
      L7 the first matched id of each of cal, head, test, test_ext and one probe id, with the raw FOIL file name and the COCO member name (for the data-steward's hand check; their sign-off is NOT given here)
    Test images that are also in folds test/test_ext are allowed (P and B are then dependent in their data); the number is logged."""
    log = dict(checks=[], counts=pool.get("counts"), created=time.strftime("%Y-%m-%dT%H:%M:%S"))
    cal, head = set(_ids(folds["cal"])), set(_ids(folds["head"]))
    ptest, pext = _ids(folds["test"]), _ids(folds.get("test_ext", []))
    probe = {normalise_image_id(i) for i in probe_ids}
    fit_ids, test_ids = _ids(pool["fit"]), _ids(pool["test"])
    fs, ts = set(fit_ids), set(test_ids)
    # L0
    if foil_images is not None:
        m = check_id_mapping(dict(images=foil_images))
        _chk(log, "L0_id_mapping_whole_file", m["n_id_filename_mismatch"] == 0 and m["n_not_val2014_prefix"] == 0, m)
    if val_ids is not None:
        v = {normalise_image_id(i) for i in val_ids}
        _chk(log, "L0_pool_ids_in_val2017", (fs | ts) <= v, dict(n_not_in_val2017=len((fs | ts) - v)))
    _chk(log, "L0_ids_are_integers", all(isinstance(i, int) for i in fit_ids + test_ids), "pool ids normalised by normalise_image_id")
    # L1-L4
    _chk(log, "L1_fit_subset_of_cal", fs <= cal, dict(n_fit=len(fs), n_not_in_cal=len(fs - cal)))
    _chk(log, "L2_fit_test_disjoint", not (fs & ts), dict(n_shared=len(fs & ts)))
    _chk(log, "L3_test_disjoint_from_cal_head_probe", not (ts & cal) and not (ts & head) and not (ts & probe),
         dict(shared_with_cal=len(ts & cal), shared_with_head=len(ts & head), shared_with_probe=len(ts & probe)))
    _chk(log, "L4_no_repeated_image_id", len(fit_ids) == len(fs) and len(test_ids) == len(ts), dict(fit_repeats=len(fit_ids) - len(fs), test_repeats=len(test_ids) - len(ts)))
    _chk(log, "L4b_planned_size", len(test_ids) <= (n_test_planned or pool.get("meta", {}).get("n_test_planned", len(test_ids))), dict(n_test=len(test_ids)))
    # L5
    _chk(log, "L5_counts_logged", bool(pool.get("counts")) and "excluded_by_reason" in pool["counts"], pool.get("counts"))
    log["test_images_also_in_P_test_fold"] = int(len(ts & (set(ptest) | set(pext))))
    # L6, L7
    if foil_images is not None:
        foil_ids = {normalise_image_id(im["id"]) for im in foil_images}
        raw_name = {normalise_image_id(im["id"]): im.get("file_name") for im in foil_images}
        groups = dict(cal=_ids(folds["cal"]), head=_ids(folds["head"]), test=ptest, test_ext=pext, probe=sorted(probe))
        matched = {g: [i for i in ids if i in foil_ids] for g, ids in groups.items()}
        _chk(log, "L6_matched_ids_positive_control", all(len(v) > 0 for v in matched.values()), dict(counts={g: len(v) for g, v in matched.items()}, total=sum(len(v) for v in matched.values()),
                                                                                                    meaning="zero in a group = id format mismatch = leak check vacuous: B stops"))
        hand = []
        for g, v in matched.items():
            if v:
                i = v[0]
                hand.append(dict(group=g, image_id=i, foil_file_name=raw_name[i], coco_member=coco_member(i), member_exists=(coco_member(i) in coco_names) if coco_names is not None else None))
        _chk(log, "L7_hand_check_sample_printed", len(hand) == 5 and all(h["member_exists"] in (True, None) for h in hand), hand)
        log["L7_status"] = "printed; the data-steward's hand check is NOT recorded by this script"
    log["ok"] = all(c["ok"] for c in log["checks"])
    if not log["ok"]:
        raise LeakCheckFailed("FOIL leak check failed: " + ", ".join(c["name"] for c in log["checks"] if not c["ok"]), log)
    return log


def selftest() -> dict:
    """L8 and the other known-bad cases: the checker must FAIL on a synthetic pool built to share one id with 'cal' (and with 'head', a probe id, a repeated id, a fit id outside cal), must PASS on the
    clean synthetic pool, and must stop as vacuous when the FOIL ids use a different format from the fold ids."""
    rng = np.random.default_rng(1)
    ids = [int(x) for x in rng.permutation(np.arange(1000, 1400))]
    mk = lambda lst: [dict(image_id=i) for i in lst]
    fold = dict(cal=mk(ids[:30]), head=mk(ids[30:50]), test=mk(ids[50:80]), test_ext=mk(ids[80:100]))
    probe = set(ids[100:110])
    foil_images = [dict(id=i, file_name=f"COCO_val2014_{i:012d}.jpg") for i in ids[:300]]
    counts = dict(n_candidate_pairs=300, n_eligible=100, excluded_by_reason={})

    def pool(fit, test):
        return dict(meta=dict(n_test_planned=len(test)), counts=counts, fit=mk(fit), test=mk(test))
    good = pool(ids[:20], ids[150:180])
    out = {}
    log = foil_leak_check(good, fold, probe, foil_images=foil_images, val_ids=set(ids))
    out["clean_pool_passes"] = bool(log["ok"])

    def fails(p, name, **kw):
        try:
            foil_leak_check(p, fold, probe, foil_images=kw.pop("foil_images", foil_images), val_ids=set(ids), **kw)
        except LeakCheckFailed as e:
            out[name] = [c["name"] for c in e.log["checks"] if not c["ok"]]
            return True
        out[name] = None
        return False
    ok = [fails(pool(ids[:20], ids[150:180] + [ids[3]]), "L8_known_leak_with_cal_is_caught"),
          fails(pool(ids[:20], ids[150:180] + [ids[35]]), "shared_with_head_is_caught"),
          fails(pool(ids[:20], ids[150:180] + [ids[102]]), "shared_with_probe_is_caught"),
          fails(pool(ids[:20] + [ids[200]], ids[150:180]), "fit_outside_cal_is_caught"),
          fails(pool(ids[:20], ids[150:180] + [ids[150]]), "repeated_id_is_caught"),
          fails(pool(ids[:20], [ids[5]] + ids[150:180]), "fit_test_overlap_is_caught"),
          fails(good, "id_format_mismatch_is_vacuous_and_stops", foil_images=[dict(id=i + 10_000_000, file_name=f"COCO_val2014_{i + 10_000_000:012d}.jpg") for i in ids[:300]])]
    out["all_known_bad_cases_caught"] = bool(all(ok))
    out["normalise_image_id_examples"] = {repr(x): normalise_image_id(x) for x in (391895, "391895", "000000391895", "COCO_val2014_000000391895.jpg", "val2017/000000391895.jpg")}
    out["ok"] = bool(out["clean_pool_passes"] and out["all_known_bad_cases_caught"] and set(out["normalise_image_id_examples"].values()) == {391895})
    return out


# ------------------------------------------------------------------------------------------------ B1 fusion
def margins_from_rows(rows: list[dict]) -> np.ndarray:
    """[n, 2] paired margins (T, I) per pair: T = pmi(c+) - pmi(c-) (text direction, spec 8), I = mean per-token paired image evidence over all 1,024 tokens (image direction, no gate).
    Rows with a non-finite margin are dropped by the caller via `finite_rows`."""
    return np.array([[r["T"], r["I"]] for r in rows], float).reshape(-1, 2)


def finite_rows(X: np.ndarray) -> np.ndarray:
    return X[np.isfinite(X).all(axis=1)]


def fit_b1(X_fit: np.ndarray) -> dict:
    """Everything that is frozen before any B test pair is scored (AD.6): Fisher LDA weights on the fit pairs (fusion.lda_weights, no intercept: the margins are signed differences, label always +),
    the unfitted Stouffer weights (descriptive), accuracy of each direction on the fit pairs and the best single direction (tie goes to the text direction), and the status under rules (i) and (ii)."""
    X = finite_rows(np.asarray(X_fit, float).reshape(-1, 2))
    n = int(len(X))
    out = dict(n_fit=n, rule=THRESHOLD_NOTE)
    if n >= 3:
        acc_T, acc_I = float(np.mean(X[:, 0] > 0)), float(np.mean(X[:, 1] > 0))
        w = fusion.lda_weights(X)
        with np.errstate(all="ignore"):                       # constant margins make the correlation 0/0: recorded as None, never as NaN (audit m8); the confirmatory path (LDA) does not use it
            st = fusion.stouffer_weights(X)
            corr = float(np.corrcoef(X[:, 0], X[:, 1])[0, 1])
        fin = lambda v: float(v) if np.isfinite(v) else None            # noqa: E731
        best = "T" if acc_T >= acc_I else "I"
        out.update(acc_T=acc_T, acc_I=acc_I, best=best, best_acc=max(acc_T, acc_I), lda_w=[float(v) for v in w], acc_lda=fusion.fused_accuracy(X, w),
                   stouffer_w=[fin(v) for v in st["w"]], stouffer_r=fin(st["r"]), stouffer_sd=[float(v) for v in st["sd"]], acc_stouffer=fusion.fused_accuracy(X, st["w"]),
                   corr_T_I=fin(corr))
    if n < MIN_FIT:
        out["status"] = "not_estimable"                      # rule (i): p = 1 reported
    elif out["best_acc"] >= CEILING:
        out["status"] = "untestable_at_ceiling"              # rule (ii): p = 1, test pairs not run
    else:
        out["status"] = "ok"
    out["test_pairs_may_run"] = bool(out["status"] == "ok")
    return out


# ------------------------------------------------------------------------------------------------ B wording (A3.4 item 3, A3b.3 items 2, 3, 5 to 8): the only sentences B may emit
# Numbers: runs/P2-GATE-FOIL-L7/l7_out.json (data-steward rule counts) and research/paper2/related/FOIL-L7-SIGNOFF-2026-10-28.md (one reader, thumbnails, E1); the ball-to-racket counts are read from pool.json
# by `caveat_numbers_from_artifacts` (a test compares them with the constants below). No sentence says that FOIL tests, shows or supports fusion of image and text evidence (A3b.3 item 6).
MIX_SENTENCE = "(ball to racket 11 of 300 test against 1 of 240 fit; a/an 15 of 300 against 7 of 240)"
WEIGHTS_SENTENCE = "the combination weights were fitted on the same negative type but not the same mix of negatives"
WORDING_CEILING = "the best single direction met the preregistered ceiling on the fit pairs; text-only cues are not excluded as a cause"                                  # A3.4 item 3 (signed), A3b.3 item 5
WORDING_NOT_ESTIMABLE = "fewer than 100 usable fit pairs: B is not estimable (p = 1); there is no statement about the combination of the two scores"                    # AD.6 rule (i)
WORDING_REJECT = ("the combination of the two UniDisc scores beat the better single score on these FOIL pairs; part of the gain may come from text-only cues; no text-only baseline was run; "
                  + MIX_SENTENCE + "; " + WEIGHTS_SENTENCE)                                                                                                           # A3b.3 item 6
WORDING_NOT_REJECT = "the combination did not beat the better single score; {mde}"                                                                                  # A3b.3 item 6
WORDING_DESCRIPTIVE = "completed n {n} is below 120: descriptive only, no test statement; {mde}"                                                                    # AD.6, A3.1 item 2
LABEL_NOISE_STATEMENTS = [
    "(i) 26 of 300 test pairs (8.7 percent) are flagged by the COCO-instance rule (the foil's category is present in the image's COCO instances); this is a flag rate, not an error rate and not a bound",
    "(ii) of those, 12 of 300 (4.0 percent; 5 plausibly true, 7 ambiguous) were judged questionable by one reader (thumbnails, E1), and the other 14 of the 26 were judged wrong by role",
    "(iii) the rule fails to find the category of the original true noun in 26 of 300 test pairs (33 of 240 fit pairs); the rate of plausibly-true foils is not bounded by these data",
    "no judgement exists for the 240 fit pairs beyond the rule's own count (18 of 240 flagged); the ceiling rule and the choice of the best direction are decided on those pairs",
]
B_LIMITS = [
    "not a corruption test: a within-modality gate cannot see a fluent foil word (derivation, E0, untested)",
    "text-only cues (an a/an mismatch, a swap inside a compound noun, a duplicated word) can drive the text direction; no text-only baseline was run in this plan (adding one needs a dated addendum and is exploratory)",
    "the negative mix differs between the fit pairs and the test pairs " + MIX_SENTENCE + "; " + WEIGHTS_SENTENCE,
    *LABEL_NOISE_STATEMENTS,
    "no pair is excluded, relabelled or reweighted for foil validity in the confirmatory analysis; the descriptive recomputation without the 26 flagged pairs is exploratory and no p-value of it enters a claim",
    "label noise caps the attainable gain: the attainable net gain is at most 1 minus the better single accuracy minus the label-noise share, and the A3.1 power table does not include this cap; "
    "the sign of any bias on Delta_B is not established",
    "all test images are in folds.json test/test_ext, so P and B are dependent in their data (separate families, separate alpha)",
    "the COCO captions c+ are probably in UniDisc's training data (U8) and the text direction may be memorised; contamination of FOIL images (U8) is unmeasured",
    "a rejection needs b > c_cnt; the label 'negative' is not available at these n",
    "foil captions are lower-cased on both sides because of the case leak; the FOIL file revision (July 2017 vs Oct 2018) is unverified",
]


def caveat_numbers_from_artifacts(pool: dict | None = None) -> dict:
    """The ball-to-racket counts of MIX_SENTENCE recomputed from the committed pool (test and fit); a test compares them with the constants."""
    pool = pool or load_pool()
    cnt = lambda s: sum(1 for x in pool[s] if x.get("target_word") == "ball" and x.get("foil_word") == "racket")          # noqa: E731
    return dict(ball_to_racket_test=cnt("test"), n_test=len(pool["test"]), ball_to_racket_fit=cnt("fit"), n_fit=len(pool["fit"]))


def _partial_prefix(n_completed: int, n_nominal: int, fold_complete: bool) -> dict | None:
    """A3.1 item 2 / A3b.6 item 5 for B: a completed n from 120 to 239 of an unfinished plan is labelled 'partial prefix (under 80 percent of plan)' with the minimum detectable effect of the A3 table."""
    if fold_complete or n_completed < MIN_COMPLETE or n_completed >= 0.8 * n_nominal:
        return None
    return dict(label="partial prefix (under 80 percent of plan)", completed_n=int(n_completed), planned_n=int(n_nominal), mde=mde_mod.mde_table(int(n_completed), ALPHA),
                note=f"a prefix-based result is not described as an n = {n_nominal} result (A3b.6 item 5)")


def _sensitivity_first150(y_fus: np.ndarray, y_best: np.ndarray, pool_idx: np.ndarray | None, tested: bool, primary_rejects: bool, n_boot: int, seed) -> dict:
    """A3b.3 item 8: the first 150 POOL POSITIONS (the AD.6 pool order, `idx` of every row), the completed pairs among them (about 148 after the token rule), tested with the same exact McNemar and the same
    direction rule if the overall completed n is at least 120; its own completed count is printed; labelled 'sensitivity (first 150 pool positions), not confirmatory, not in the Holm set'. If the completed
    prefix covers fewer than 150 pool positions it coincides with the primary and is not shown separately. It can neither reject nor rescue the family hypothesis (A3.1 item 3)."""
    label = "sensitivity (first 150 pool positions), not confirmatory, not in the Holm set"
    if pool_idx is None:
        return dict(exists=False, label=label, reason="pool positions (idx) were not supplied")
    if not tested:
        return dict(exists=False, label=label, reason="the overall completed n is below 120: nothing is tested, so the sensitivity is not shown")
    pool_idx = np.asarray(pool_idx)
    if len(pool_idx) == 0 or int(pool_idx.max()) + 1 < N_SENS:
        return dict(exists=False, label=label, reason=f"the completed prefix covers fewer than {N_SENS} pool positions: the sensitivity coincides with the primary and is not shown separately")
    sel = pool_idx < N_SENS
    rep = report.report_test(y_fus[sel], y_best[sel], n_boot=n_boot, seed=seed)
    sens_rejects = bool(rep["p"] < ALPHA and rep["b"] > rep["c"])
    out = dict(exists=True, label=label, n_completed_in_prefix=int(sel.sum()), tested=True, b=rep["b"], c=rep["c"], n_d=rep["n_d"], p=rep["p"], delta=rep["delta"], ci95=rep["ci95"],
               sens_rejects=sens_rejects, primary_rejects=bool(primary_rejects), sensitive_to_n=bool(sens_rejects != bool(primary_rejects)),
               mde_at_this_n=mde_mod.mde_table(int(sel.sum()), ALPHA)["by_pi_d"])
    if out["sensitive_to_n"]:
        out["statement"] = "the primary and the sensitivity are on opposite sides of rejection: both are shown and the conclusion is sensitive to n (A3.1 item 3)"
    return out


def fusion_b1(X_fit: np.ndarray | None, X_test: np.ndarray, *, n_boot: int = 10000, seed=None, n_planned: int | None = None, frozen_fit: dict | None = None,
              pool_idx: np.ndarray | None = None, n_nominal: int = N_TEST_PLANNED) -> dict:
    """B1: Delta_B = Pr(Y_fus = 1) - Pr(Y_best = 1), exact two-sided McNemar of Y_fus against Y_best (alpha 0.05, m = 1), effect size and paired percentile bootstrap CI as in section 2.3
    (`report.report_test`). Y_fus = 1[w . (T, I) > 0] with the frozen LDA weights; Y_best = 1[margin of the best single direction > 0]; ties count wrong. `combination_beat_best_single` is true only with
    b > c_cnt and p < 0.05 and completed n >= 120 (a smaller completed n is descriptive). Statuses not_estimable / untestable_at_ceiling return p = 1, no test and their A3.4 / AD.6 wording (X_test may be empty:
    the runner never ran the test stage). The sentences are those of A3b.3 item 6 (`WORDING_*`): none says that FOIL tests, shows or supports fusion. `pool_idx` = the pool position (`idx`) of each row of X_test, in
    the same order; it feeds the first-150-pool-positions sensitivity (A3b.3 item 8)."""
    fit = frozen_fit if frozen_fit is not None else fit_b1(X_fit)            # the analysis passes the COMMITTED fusion_frozen.json fit, never a refit
    res = dict(fit=fit, family="B", m=1, alpha=ALPHA, estimand="Delta_B = Pr(Y_fus = 1) - Pr(Y_best = 1) on FOIL-COCO pairs, clean images, UniDisc")
    X_all = np.asarray(X_test, float).reshape(-1, 2)
    ok = np.isfinite(X_all).all(axis=1)
    X = X_all[ok]
    idx_ok = np.asarray(pool_idx)[ok] if pool_idx is not None else None
    n_all = int(X_all.shape[0])
    res.update(n_test_completed=int(len(X)), n_test_dropped_nonfinite=n_all - int(len(X)), n_test_planned=n_planned, weights_source=("fusion_frozen.json" if frozen_fit is not None else "fit on X_fit"))
    if frozen_fit is not None and X_fit is not None:
        refit = fit_b1(X_fit)
        res["refit_matches_frozen"] = bool(refit.get("status") == frozen_fit.get("status") and np.allclose(refit.get("lda_w", [0, 0]), frozen_fit.get("lda_w", [0, 0]), rtol=1e-6, atol=1e-12))
    if fit["status"] != "ok":
        wording = WORDING_CEILING if fit["status"] == "untestable_at_ceiling" else WORDING_NOT_ESTIMABLE
        res.update(status=fit["status"], tested=False, p=1.0, combination_beat_best_single=False, wording=wording, reason="AD.6 rule before any B-test item: " + fit["status"].replace("_", " "))
        return res
    w = np.array(fit["lda_w"], float)
    ix = 0 if fit["best"] == "T" else 1
    y_fus, y_best = (X @ w > 0).astype(float), (X[:, ix] > 0).astype(float)
    rep = report.report_test(y_fus, y_best, n_boot=n_boot, seed=seed if seed is not None else seeds.seed_for("fusion"))
    descriptive = bool(len(X) < MIN_COMPLETE)
    rejects = bool((not descriptive) and rep["p"] < ALPHA and rep["b"] > rep["c"])
    mde_here = mde_mod.mde_table(int(len(X)), ALPHA) if len(X) else None
    mde_text = mde_mod.mde_sentence(int(len(X)), ALPHA) if len(X) else "no pair completed"
    wording = (WORDING_REJECT if rejects else WORDING_DESCRIPTIVE.format(n=len(X), mde=mde_text) if descriptive else WORDING_NOT_REJECT.format(mde=mde_text))
    fold_complete = bool(n_planned is not None and len(X) >= n_planned)
    res.update(tested=not descriptive, descriptive_only=descriptive, test=rep, p=rep["p"], best_direction=fit["best"], combination_beat_best_single=rejects,
               status="descriptive_n_below_120" if descriptive else "tested", wording=wording, mde_at_achieved_n=mde_here,
               partial_prefix=_partial_prefix(int(len(X)), n_nominal, fold_complete) if not descriptive else None,
               sensitivity_first150_pool_positions=_sensitivity_first150(y_fus, y_best, idx_ok, not descriptive, rejects, n_boot, seed if seed is not None else seeds.seed_for("fusion")),
               max_net_gain_before_label_noise=float(1.0 - np.mean(y_best)), max_net_gain_note="1 minus the better single accuracy on the test pairs; the attainable gain is smaller by the label-noise share (A3b.3 item 7)")
    ys = (X @ np.array(fit["stouffer_w"], float) > 0).astype(float)
    res["descriptive"] = dict(acc_text_alone=float(np.mean(X[:, 0] > 0)), acc_image_alone=float(np.mean(X[:, 1] > 0)), acc_stouffer_unfitted=float(ys.mean()),
                              acc_lda=float(y_fus.mean()), stouffer_vs_best=report.report_test(ys, y_best, n_boot=2000, seed=seed if seed is not None else seeds.seed_for("fusion")) | dict(label="descriptive, no p enters a claim"),
                              note="the unfitted Stouffer statistic is reported first (spec 8) and is descriptive")
    return res



# ------------------------------------------------------------------------------------------------ git helpers (rule iii)
def require_committed(path: Path, repo: Path = ROOT) -> None:
    """AD.6 rule (iii) / SAP 8.2: the file must be tracked and have no uncommitted change, else RuntimeError (the GPU runner calls this before the test stage)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{p} missing")
    rel = str(p.resolve().relative_to(Path(repo).resolve())).replace("\\", "/")
    tr = subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", rel], capture_output=True, text=True)
    if tr.returncode != 0:
        raise RuntimeError(f"{rel} is not tracked by git: commit it before any B test pair (AD.6 rule iii)")
    st = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", rel], capture_output=True, text=True)
    if st.returncode != 0 or st.stdout.strip():
        raise RuntimeError(f"{rel} has uncommitted changes: commit it first (AD.6 rule iii)")


# ------------------------------------------------------------------------------------------------ CLI
def pool_dir() -> Path:
    return Path(common.RUNS) / FOIL_RUN_ID


def load_pool(path: Path | None = None) -> dict:
    return json.loads(Path(path or pool_dir() / "pool.json").read_text(encoding="utf8"))


def prepare_inputs() -> dict:
    """Everything the CPU steps need: the FOIL file, folds.json, probe ids, val2017 ids, the zip member names."""
    import zipfile
    foil = load_foil()
    folds = json.loads(folds_mod.folds_path().read_text(encoding="utf8"))
    val_ids = set(common.load_captions())
    names = set(zipfile.ZipFile(common.VAL_ZIP).namelist()) if Path(common.VAL_ZIP).exists() else None
    return dict(foil=foil, folds=folds, probe_ids=data.probe_image_ids(), val_ids=val_ids, coco_names=names)


def check_pool(pool: dict | None = None, inp: dict | None = None) -> dict:
    """Full leak check of the committed pool against the current folds.json and probe lists (CPU). Also runs the L8 self-test; raises LeakCheckFailed on any failure."""
    inp = inp or prepare_inputs()
    st = selftest()
    if not st["ok"]:
        raise LeakCheckFailed("selftest (L8) failed: the checker does not catch a known leak", dict(selftest=st, checks=[], ok=False))
    pool = pool or load_pool()
    log = foil_leak_check(pool, inp["folds"], inp["probe_ids"], foil_images=inp["foil"]["images"], val_ids=inp["val_ids"], coco_names=inp["coco_names"])
    log["L8_selftest"] = st
    log["pool_sha256"] = pool_sha256(pool)
    return log


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build-pool", "check", "selftest", "manifest"])
    ap.add_argument("--no-tokens", action="store_true", help="do not apply the 5-32 token rule at pool time (the runner applies it with the runtime tokenizer anyway)")
    ap.add_argument("--n", type=int, default=N_TEST_PLANNED)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        st = selftest()
        print(json.dumps(st, indent=1))
        return 0 if st["ok"] else 2
    if a.cmd == "manifest":
        print(json.dumps(write_manifest(), indent=1))
        return 0
    out = pool_dir()
    out.mkdir(parents=True, exist_ok=True)
    try:
        if a.cmd == "check":
            log = check_pool()
        else:
            man = write_manifest()
            inp = prepare_inputs()
            pairs, stats = build_pairs(inp["foil"])
            n_tok = None if a.no_tokens else folds_mod.hf_token_counter()
            pool = foil_pool(pairs, inp["folds"], inp["probe_ids"], inp["val_ids"], n_test=a.n, n_tok_fn=n_tok, file_sha=man["sha256"])
            pool["build_stats"] = stats | check_id_mapping(inp["foil"])
            artifacts.write_once(out / "pool.json", json.dumps(pool, indent=1), a.force)
            log = check_pool(pool, inp)
    except LeakCheckFailed as e:
        (out / ("leak_check_recheck.json" if a.cmd == "check" else "leak_check.json")).write_text(json.dumps(e.log, indent=1, default=str), encoding="utf8")
        print("STOP (leak check failed):", e, file=sys.stderr)
        return 2
    # build-pool writes the committed pre-GPU evidence; `check` re-runs on the committed pool and writes a separate file so that evidence is not overwritten (audit m7)
    (out / ("leak_check_recheck.json" if a.cmd == "check" else "leak_check.json")).write_text(json.dumps(log, indent=1, default=str), encoding="utf8")
    print(json.dumps({k: log[k] for k in ("ok", "pool_sha256", "test_images_also_in_P_test_fold")}, indent=1))
    print("counts:", json.dumps(log["counts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
