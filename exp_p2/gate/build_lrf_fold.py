"""A6.3 fresh fold for the confirmatory test of LRF (SAP addendum A6, DRAFT): builds runs/P2-LRF-FOLD/{folds_lrf.json, manifest.json, leak_check.json}. CPU only, no model, no GPU.

    python -m exp_p2.gate.build_lrf_fold [--out-dir PATH] [--slow] [--n 533]        # refuses to overwrite; build it in the main worktree so that every runs/P2-* file is read (A6 r1: 533-list, n_L is a prefix chosen by the n-rule)

Output `folds_lrf.json` has the schema of folds.json (`test` = the ordered list of n_L items; `cal`, `head`, `test_ext` empty) so the pinned runners read it with --folds-path.
Per item: idx, gid (8000 + idx), image_id, caption (c+), n_tok, the primary negative of the M4 rule (neg_idx, neg_image_id, neg_caption, neg_restricted, n_tok_neg) and the length-matched negative c-_L of A6.7:
neg_caption_len (caption TEXT, read by run_gate_m4 --neg-len), neg_len_idx, neg_len_image_id, n_tok_neg_len, neg_len_diff (= n_tok_neg_len - n_tok), neg_len_exact, neg_len_restricted.

Selection (deterministic given the seed and the input files; no model outcome is read):
  universe   COCO val2017 images with a caption, an instance annotation and (in the CLI) a file in val2017.zip
  excluded   (C6-10) the UNION of image ids in every runs/P2-*/items.jsonl, selection.json, pool.json and folds*.json present at build time (folds.json cal, head, test, test_ext; probes 1 and 2; M1, M5, S2, FOIL, the suite and its smoke,
             H if present), plus every image of the SugarCrepe release; the manifest lists every file read and its count
  c+         per image, one caption chosen uniformly (seeded) among its captions with 5 to 32 UniDisc tokens; images with none are excluded and counted
  order      a seeded permutation of the eligible images; the first n_L are the fold (idx 0 to n_L - 1)
  c-         folds.assign_negatives, unchanged, with the whole list as one block (a caption of another item whose image shares no annotated category; fallback as in folds.py)
  c-_L       among the c+ captions of other items on category-disjoint images, uniformly one with the same token count as c+; if none, the smallest |difference| (ties uniform); fallback: any other item
Seeds: the permutation and the c+ draws use default_rng([SEED_GATE, 10]) (folds.py uses stream 7 and 8, family H stream 9); c- uses [SEED_GATE, 10, 1], c-_L uses [SEED_GATE, 10, 2].
Leak check L0 to L8 (as AB.6 / H-L0 to H-L8): disjointness from every excluded set, positive control L6 (the id format matches: the universe must contain ids of every non-empty excluded set), L7 matched ids for the data-steward,
L8 an injected-leak self-test the checker must fail."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import build_hardneg_items as bh, config, data, foil, folds   # noqa: E402

RUN_ID = "P2-LRF-FOLD"
N_L = 533                                         # A6 r1 A6.3: the list holds the budget cap; the n-rule (exp_p2/gate/lrf_nrule.py) picks a prefix n_L in [400, 533]
GID_OFFSET = 8000                                  # folds 0-2499, family B (FOIL) 4000/5000, family H 6000/7000, this fold 8000+
SELECT_SEED = [config.SEED_GATE, 10]
CATEGORY_GROUPS = ("folds.cal", "folds.head", "folds.test", "folds.test_ext", "probe1+probe2")      # the five groups of L7 (as FOIL L6/L7 and H-L7)


class LeakCheckFailed(RuntimeError):
    def __init__(self, msg: str, log: dict):
        super().__init__(msg)
        self.log = log


def used_gid_ranges() -> dict[str, tuple[int, int]]:
    """gid ranges already taken (half-open [lo, hi)): the three folds (offset + idx, idx < 1000), FOIL, family H. Read from the modules that own them."""
    r = {f"folds.{k}": (v, v + 1000) for k, v in config.FOLD_GID_OFFSET.items()}
    r["foil.fit"], r["foil.test"] = (foil.GID_FIT, foil.GID_FIT + 1000), (foil.GID_TEST, foil.GID_TEST + 1000)
    r["hardneg.head"], r["hardneg.test"] = (bh.GID_OFFSET["head"], bh.GID_OFFSET["head"] + 1000), (bh.GID_OFFSET["test"], bh.GID_OFFSET["test"] + 1000)
    return r


def assign_length_matched(items: list[dict], image_cats: dict[int, set[str]] | None, rng: np.random.Generator) -> None:
    """A6.3 c-_L for every item, drawn from the c+ captions of the OTHER items of the list (the caption must differ from c+). Candidates are the items whose image shares no annotated category with this
    one; if there is none, any other item (neg_len_restricted False). Among the candidates the ones with the smallest |token difference| to c+ (0 when an exact match exists) are kept and one is drawn
    uniformly. Sets neg_caption_len, neg_len_idx, neg_len_image_id, n_tok_neg_len, neg_len_diff (signed), neg_len_exact, neg_len_restricted."""
    n = len(items)
    cats = [(image_cats or {}).get(it["image_id"], set()) for it in items]
    for i, it in enumerate(items):
        base = [j for j in range(n) if j != i and items[j]["caption"] != it["caption"]]
        cand = [j for j in base if not (cats[i] & cats[j])] if image_cats is not None else []
        pool, restricted = (cand, True) if cand else (base, False)
        diff = [abs(items[j]["n_tok"] - it["n_tok"]) for j in pool]
        best = min(diff)
        tied = [j for j, d in zip(pool, diff) if d == best]
        j = int(tied[int(rng.integers(0, len(tied)))])
        it.update(neg_caption_len=items[j]["caption"], neg_len_idx=j, neg_len_image_id=items[j]["image_id"], n_tok_neg_len=items[j]["n_tok"],
                  neg_len_diff=int(items[j]["n_tok"] - it["n_tok"]), neg_len_exact=bool(best == 0), neg_len_restricted=restricted)


def build(captions: dict[int, list[str]], image_cats: dict[int, set[str]], excluded: set[int], n_tok_fn, *, n: int = N_L, seed=SELECT_SEED, tok_range=config.TOK_RANGE,
          available: set[int] | None = None) -> dict:
    """The folds-schema dict. `available` (optional) limits the universe to ids with an image file. Raises RuntimeError if fewer than n images are eligible."""
    lo, hi = tok_range
    counts = dict(n_captioned=len(captions), n_not_available=0, n_no_instance_annotation=0, n_in_excluded_pools=0, n_no_caption_in_token_range=0)
    cache: dict[str, int] = {}

    def nt(c: str) -> int:
        if c not in cache:
            cache[c] = int(n_tok_fn(c))
        return cache[c]
    elig, valid = [], {}
    for iid in sorted(captions):
        if available is not None and iid not in available:
            counts["n_not_available"] += 1
        elif iid not in image_cats:
            counts["n_no_instance_annotation"] += 1
        elif iid in excluded:
            counts["n_in_excluded_pools"] += 1
        else:
            v = [c for c in captions[iid] if lo <= nt(c) <= hi]
            if v:
                elig.append(iid)
                valid[iid] = v
            else:
                counts["n_no_caption_in_token_range"] += 1
    counts["n_eligible_images"] = len(elig)
    if len(elig) < n:
        raise RuntimeError(f"only {len(elig)} eligible images for a fold of {n}")
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(elig))[:n]
    items = []
    for k, j in enumerate(order):
        iid = elig[int(j)]
        c = valid[iid][int(rng.integers(0, len(valid[iid])))]
        items.append(dict(idx=k, gid=GID_OFFSET + k, image_id=int(iid), caption=c, n_tok=nt(c)))
    folds.assign_negatives(items, image_cats, np.random.default_rng([*seed, 1]))
    for it in items:
        it["n_tok_neg"] = items[it["neg_idx"]]["n_tok"]
    assign_length_matched(items, image_cats, np.random.default_rng([*seed, 2]))
    out = dict(meta=dict(seed=list(seed), sizes=[0, 0, n], test_base=n, tok_range=[lo, hi], family="L", n_excluded=len(excluded), annotations_used=True, gid_offset=GID_OFFSET,
                         universe=counts, length_matching=length_stats(items)),
               cal=[], head=[], test=items, test_ext=[])
    out["meta"]["sha1"] = hashlib.sha1(json.dumps({k: out[k] for k in ("cal", "head", "test", "test_ext")}, sort_keys=True).encode()).hexdigest()[:16]
    return out


def length_stats(items: list[dict]) -> dict:
    d = np.array([abs(it["neg_len_diff"]) for it in items])
    dp = np.array([abs(it["n_tok_neg"] - it["n_tok"]) for it in items])
    return dict(n=len(items), n_exact=int(sum(it["neg_len_exact"] for it in items)), n_not_exact=int((d > 0).sum()), mean_abs_diff=float(d.mean()), max_abs_diff=int(d.max()),
                n_unrestricted=int(sum(not it["neg_len_restricted"] for it in items)), primary_negative_mean_abs_diff=float(dp.mean()), primary_negative_n_equal_length=int((dp == 0).sum()),
                primary_negative_n_unrestricted=int(sum(not it["neg_restricted"] for it in items)))


def _chk(log: dict, name: str, ok: bool, detail) -> bool:
    log["checks"].append(dict(name=name, ok=bool(ok), detail=detail))
    return bool(ok)


def leak_check(fold: dict, sources: dict[str, set[int]], universe: set[int], *, image_cats: dict[int, set[str]] | None = None, val_ids: set[int] | None = None) -> dict:
    """L0 to L7 on a built fold; raises LeakCheckFailed (with the log) on any failure. `sources` maps a source name (folds.cal, folds.head, folds.test, folds.test_ext, probe1+probe2, P2-GATE-M1, P2-GATE-M5,
    foil.pool, sugarcrepe, ...) to its image ids.
      L0 ids are integers of the documented form (COCO integer id; file val2017/<12 digits>.jpg); if `val_ids` is given every id is in it
      L1 disjoint from folds cal, head, test, test_ext   L2 disjoint from probe-1 and probe-2   L3 disjoint from M1, M5, the FOIL pool and every other named source (sugarcrepe, family H)
      L4 no image repeated; the gid range is free and the gids are distinct; test is the only non-empty fold
      L5 negatives: each primary and length-matched negative is another item's c+, its image is category-disjoint when the item says restricted, and neg_len_diff is consistent
      L6 positive control: every non-empty source has at least one id inside the universe (a zero means the id format does not match and the disjointness proves nothing)
      L7 the smallest matched id of each of the five groups with its COCO file name, for the data-steward (not signed here)"""
    log = dict(checks=[], created=time.strftime("%Y-%m-%dT%H:%M:%S"))
    items = fold["test"]
    ids = [it["image_id"] for it in items]
    ids_set = set(ids)
    _chk(log, "L0_ids_are_integers", all(isinstance(i, int) and not isinstance(i, bool) for i in ids), "COCO integer ids; coco_member = val2017/<id:012d>.jpg")
    if val_ids is not None:
        _chk(log, "L0_ids_in_val2017", ids_set <= val_ids, dict(n_not_in_val2017=len(ids_set - val_ids)))
    for name, group in (("L1", ("folds.cal", "folds.head", "folds.test", "folds.test_ext")), ("L2", ("probe1+probe2",))):
        shared = {g: len(ids_set & sources.get(g, set())) for g in group}
        _chk(log, f"{name}_disjoint_from_" + "_".join(group), not any(shared.values()), shared)
    others = [g for g in sources if g not in CATEGORY_GROUPS]
    shared = {g: len(ids_set & sources[g]) for g in others}
    _chk(log, "L3_disjoint_from_" + "_".join(others), not any(shared.values()), shared)
    gids = [it["gid"] for it in items]
    taken = used_gid_ranges()
    clash = {k: sum(lo <= g < hi for g in gids) for k, (lo, hi) in taken.items()}
    _chk(log, "L4_no_repeated_image_id", len(ids) == len(ids_set), dict(n=len(ids), n_unique=len(ids_set)))
    _chk(log, "L4_gid_free_and_distinct", len(set(gids)) == len(gids) and not any(clash.values()), dict(n_gids=len(gids), min=min(gids), max=max(gids), clashes=clash))
    _chk(log, "L4_only_test_fold_filled", not fold.get("cal") and not fold.get("head") and not fold.get("test_ext"), dict(cal=len(fold.get("cal", [])), head=len(fold.get("head", [])), test_ext=len(fold.get("test_ext", []))))
    bad = []
    for it in items:
        for pre, key in (("neg_", "neg_caption"), ("neg_len_", "neg_caption_len")):
            j = it[pre + "idx"]
            ok = items[j]["caption"] == it[key] and items[j]["image_id"] == it[pre + "image_id"] and j != it["idx"] and it[key] != it["caption"]
            if image_cats is not None and it[pre + "restricted"]:
                ok = ok and not (image_cats.get(it["image_id"], set()) & image_cats.get(items[j]["image_id"], set()))
            if not ok:
                bad.append((it["idx"], pre))
        if it["neg_len_diff"] != it["n_tok_neg_len"] - it["n_tok"] or it["neg_len_exact"] != (it["neg_len_diff"] == 0):
            bad.append((it["idx"], "diff"))
    _chk(log, "L5_negatives_consistent", not bad, dict(n_bad=len(bad), first=bad[:5]))
    inside = {g: len(s & universe) for g, s in sources.items()}
    _chk(log, "L6_positive_control_ids_match_universe", all(v > 0 for g, v in inside.items() if sources[g]), dict(n_ids_in_universe=inside, meaning="zero for a non-empty source = id format mismatch = leak check vacuous"))
    hand = []
    for g in CATEGORY_GROUPS:
        hit = sorted(sources.get(g, set()) & universe)
        hand.append(dict(group=g, n_matched=len(hit), image_id=hit[0] if hit else None, coco_member=(f"val2017/{hit[0]:012d}.jpg" if hit else None)))
    _chk(log, "L7_hand_check_sample_printed", len(hand) == len(CATEGORY_GROUPS) and all(h["image_id"] is not None for h in hand), hand)
    log["L7_status"] = "printed; the data-steward's hand check is NOT recorded by this script"
    log["ok"] = all(c["ok"] for c in log["checks"])
    if not log["ok"]:
        raise LeakCheckFailed("LRF fold leak check failed: " + ", ".join(c["name"] for c in log["checks"] if not c["ok"]), log)
    return log


def selftest(fold: dict, sources: dict[str, set[int]], universe: set[int]) -> dict:
    """L8: the checker must PASS on the fold as built and FAIL on copies with an injected leak (one id from cal, from the FOIL pool or any other source; a repeated id; a colliding gid; a wrong negative)."""
    def fails(f: dict) -> bool:
        try:
            leak_check(f, sources, universe)
            return False
        except LeakCheckFailed:
            return True
    import copy
    res = {}
    try:
        leak_check(fold, sources, universe)
        res["clean_fold_passes"] = True
    except LeakCheckFailed:
        res["clean_fold_passes"] = False
    for name, ids in sources.items():
        pick = sorted(ids)
        if not pick:
            continue
        f = copy.deepcopy(fold)
        f["test"][0]["image_id"] = int(pick[0])
        res[f"L8_injected_leak_with_{name}_is_caught"] = fails(f)
    f = copy.deepcopy(fold)
    f["test"][1]["image_id"] = f["test"][0]["image_id"]
    res["L8_repeated_image_is_caught"] = fails(f)
    f = copy.deepcopy(fold)
    f["test"][0]["gid"] = 2001
    res["L8_gid_collision_is_caught"] = fails(f)
    f = copy.deepcopy(fold)
    f["test"][0]["neg_caption_len"] = "a caption that is nobody's"
    res["L8_wrong_length_matched_negative_is_caught"] = fails(f)
    res["ok"] = all(res.values())
    return res


def zip_image_ids() -> set[int]:
    import zipfile
    with zipfile.ZipFile(common.VAL_ZIP) as z:
        return {int(Path(n).stem) for n in z.namelist() if n.startswith("val2017/") and n.endswith(".jpg")}


DISCOVER_NAMES = ("items.jsonl", "selection.json", "pool.json")
OWN_RUN_DIRS = (RUN_ID,)                           # this builder's own output directory is never an exclusion source


def _collect_ids(obj, out: set) -> None:
    """Every integer under a key `image_id` (and every integer in a list under `image_ids`), at any depth."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "image_id" and isinstance(v, int) and not isinstance(v, bool):
                out.add(int(v))
            elif k == "image_ids" and isinstance(v, list):
                out.update(int(x) for x in v if isinstance(x, int) and not isinstance(x, bool))
            else:
                _collect_ids(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect_ids(v, out)


def discover_sources(runs: Path) -> dict[str, set[int]]:
    """C6-10: every `runs/P2-*/**/{items.jsonl, selection.json, pool.json}` and `folds*.json` file -> its image ids, keyed by the path relative to `runs` (forward slashes). Files without ids (empty or other formats) map to an empty set
    and are listed in the manifest all the same. This builder's own output directory is skipped."""
    runs = Path(runs)
    found: dict[str, set[int]] = {}
    for d in sorted(runs.glob("P2-*")):
        if not d.is_dir() or d.name in OWN_RUN_DIRS:
            continue
        for f in sorted(d.rglob("*")):
            if not f.is_file() or not (f.name in DISCOVER_NAMES or (f.name.startswith("folds") and f.suffix == ".json")):
                continue
            ids: set[int] = set()
            try:
                if f.suffix == ".jsonl":
                    for line in f.read_text(encoding="utf8").splitlines():
                        if line.strip():
                            _collect_ids(json.loads(line), ids)
                else:
                    _collect_ids(json.loads(f.read_text(encoding="utf8")), ids)
            except (OSError, ValueError):
                ids = set()
            found[f.relative_to(runs).as_posix()] = ids
    return found


def collect_sources(runs: Path, sugarcrepe_dir: Path, allow_missing_optional: bool = False) -> tuple[dict[str, set[int]], dict]:
    """Every excluded image set, by name (folds.cal ... probe1+probe2, P2-GATE-M1, P2-GATE-M5, foil.pool, sugarcrepe, hardneg.h if its file exists) plus the report. M1 and M5 item files and the FOIL pool are required
    unless allow_missing_optional (tests); a missing required folds.json or probe file always raises FileNotFoundError."""
    by_source: dict[str, set[int]] = {}
    ids, rep = bh.exclusion_ids(runs, by_source=by_source)
    if rep["missing_optional"] and not allow_missing_optional:
        raise FileNotFoundError(f"M1/M5 item files missing: {rep['missing_optional']}; build in the main worktree where they exist (A6.3), or pass --allow-missing-optional for a dry run")
    try:
        by_source["foil.pool"] = bh.foil_pool_ids(runs)
    except FileNotFoundError:
        if not allow_missing_optional:
            raise
        rep["missing_optional"].append("P2-GATE-FOIL/pool.json")
    bad = bh.verify_sha256(sugarcrepe_dir)
    if bad:
        raise ValueError(f"SugarCrepe SHA-256 mismatch against SHA256SUMS.txt: {bad}")
    rows = bh.load_sugarcrepe(sugarcrepe_dir)
    by_source["sugarcrepe"] = {r["image_id"] for r in rows}
    hp = runs / bh.RUN_ID / "folds_hardneg.json"
    if hp.exists():
        h = json.loads(hp.read_text(encoding="utf8"))
        by_source["hardneg.h"] = {int(it["image_id"]) for k in ("head", "test") for it in h.get(k, [])}
    rep["sugarcrepe_n_images"] = len(by_source["sugarcrepe"])
    disc = discover_sources(runs)
    rep["discovered_files"] = {k: len(v) for k, v in disc.items()}
    for k, v in disc.items():
        by_source[f"file:{k}"] = v
    rep["n_ids_per_source"] = {k: len(v) for k, v in by_source.items()}
    rep["n_union"] = len(set().union(*by_source.values()))
    return by_source, rep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=None, help=f"default: runs/{RUN_ID}")
    ap.add_argument("--slow", action="store_true", help="use the slow SentencePiece tokenizer (UniDisc config use_slow_tokenizer)")
    ap.add_argument("--n", type=int, default=N_L)
    ap.add_argument("--sugarcrepe-dir", default=str(bh.SUGARCREPE_DIR))
    ap.add_argument("--allow-missing-optional", action="store_true", help="dry run: do not stop when the M1/M5 item files or the FOIL pool are missing (the manifest records it)")
    a = ap.parse_args(argv)
    out_dir = Path(a.out_dir) if a.out_dir else Path(common.RUNS) / RUN_ID
    targets = [out_dir / n for n in ("folds_lrf.json", "manifest.json", "leak_check.json")]
    if any(t.exists() for t in targets):
        print(f"{[str(t) for t in targets if t.exists()]} exist; not overwriting (frozen once committed)", file=sys.stderr)
        return 2
    try:
        sources, rep = collect_sources(Path(common.RUNS), Path(a.sugarcrepe_dir), a.allow_missing_optional)
        _, image_cats = data.load_instances()
        available = zip_image_ids()
    except (FileNotFoundError, ValueError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    excluded = set().union(*sources.values())
    fold = build(common.load_captions(), image_cats, excluded, folds.hf_token_counter(a.slow), n=a.n, available=available)
    universe = set(available)                                                   # L6/L7 match ids against every image of val2017.zip (some excluded files hold ids without an instance annotation)
    try:
        log = leak_check(fold, sources, universe, image_cats=image_cats, val_ids=available)
    except LeakCheckFailed as e:
        print("STOP:", e, file=sys.stderr)
        print(json.dumps(e.log, indent=1), file=sys.stderr)
        return 2
    log["L8_selftest"] = st = selftest(fold, sources, universe)
    if not st["ok"]:
        print("STOP: L8 self-test failed: the checker does not catch a known leak", st, file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)
    folds.save_folds(fold, targets[0])
    manifest = dict(meta=fold["meta"], exclusion=rep, files_read={k: len(v) for k, v in sources.items()}, folds_lrf_sha256=hashlib.sha256(targets[0].read_bytes()).hexdigest(), code="exp_p2/gate/build_lrf_fold.py", created=time.strftime("%Y-%m-%dT%H:%M:%S"),
                    spec="research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md r1 A6.3")
    targets[1].write_text(json.dumps(manifest, indent=1), encoding="utf8")
    targets[2].write_text(json.dumps(log, indent=1), encoding="utf8")
    print(json.dumps(dict(path=str(targets[0]), sha1=fold["meta"]["sha1"], sha256=manifest["folds_lrf_sha256"], n=len(fold["test"]), universe=fold["meta"]["universe"], length_matching=fold["meta"]["length_matching"],
                          l7=[c for c in log["checks"] if c["name"].startswith("L7")][0]["detail"], l8=st["ok"], missing_optional=rep["missing_optional"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
