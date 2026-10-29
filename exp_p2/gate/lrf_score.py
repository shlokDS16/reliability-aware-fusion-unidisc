"""A6.9 / A6.11 item 5: apply the FROZEN LRF model to stored M4-runner item arrays (CPU, numpy, no GPU, no model download) and write the per-item predictions file the A6 analysis reads.

    python -m exp_p2.gate.lrf_score --run-id P2-LRF-L1 [--frozen-dir runs/P2-LRF-FROZEN] [--pins PATH] [--conds clean,jpeg10,noise0.1,splice128] [--out PATH] [--force] [--crosscheck]

The frozen object (A6.2) is `runs/P2-LRF-FROZEN/` (written by analysis_posthoc/learned_ceiling/lrf.py --freeze): `spec.json` (name, features, preprocessing, `model_sha256`, `code_sha256` of data.py, families.py, lrf.py),
`model.npz` (a, b, c, knots, mu, sd, feature_names). The scorer REFUSES TO RUN (HashMismatch) if any of these differ:
  (a) the SHA-256 of model.npz against spec.json (and against the pins file, if one is given)
  (b) the SHA-256 of every file named in spec.json `code_sha256` (the feature code data.py among them) against the file found in --code-dir (default analysis_posthoc/learned_ceiling), raw bytes or LF-normalised
  (c) the feature list of spec.json, of model.npz and of the loaded feature code
  (d) `pins` (optional JSON the lead writes when A6.0 item 2 is met): model_sha256, code_sha256 {file: sha}, scoring_code_sha256 (this file), decision_rule; each key given must match what is loaded
Features are built by the frozen feature code (data.engineer, loaded from the verified file by path); the GAM weights are evaluated here in numpy (same formula as lrf.weights_from_raw, `--crosscheck` compares against it
when analysis_posthoc.learned_ceiling.lrf is importable).

Decision rule (A6.2): w_j = sigmoid(f(x_j)); Y_LRF = 1[sum_j w_j * Delta_j > 0]; a tie (sum exactly 0) counts as wrong. Any non-finite feature, weight, Delta, score or margin (an all-zero weight vector included) raises NonFinite and stops the scorer (A6 r1, C6-2): it is never a "wrong" decision. Delta is the stored `<cond>_delta` (the primary negative); with the
length-matched negative of A6.7 the stored `<cond>_deltaL` is scored with the SAME weights (they never see a negative).

Output `runs/<run-id>/predictions.jsonl`, one line per item and condition (items in committed order): idx, gid, image_id, condition, n_tok, n_tok_neg, y_none, y_gatem, y_lrf, m_none, m_gatem, m_lrf (the margins), and with
`<cond>_deltaL` present also y_none_L, y_gatem_L, y_lrf_L, m_*_L, n_tok_neg_len, neg_len_diff, neg_len_exact. Y_NONE and Y_GATE-M are recomputed from the arrays and must equal the runner's row (positive control, AssertionError otherwise).
A sidecar `lrf_score_meta.json` records the hashes, the number of items, and the positive-control counts."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import config, evidence                                    # noqa: E402

FROZEN_DIR = ROOT / "runs" / "P2-LRF-FROZEN-LFIX"           # A6 r1: the object is the LRF re-frozen at L_FIX = 13; model ca5c4e2f (runs/P2-LRF-FROZEN) is retired and never scored on fresh items
CODE_DIR = ROOT / "analysis_posthoc" / "learned_ceiling"
DECISION_RULE = "Y = 1[sum_j w_j * Delta_j > 0]; tie = wrong; non-finite feature, weight, score or margin = error"
L1_CONDS = ("clean", "jpeg10", "noise0.1", "splice128")
LG_CONDS = ("clean", "shot_noise3", "impulse_noise3", "speckle_noise3")
GATE_ARM = f"gate{config.ALPHA_PRIMARY:g}"                                  # "gate0.05"
NEEDED = ("B", "D", "s3", "tbv", "tex", "nbr", "delta", f"flag{config.ALPHA_PRIMARY:g}")


class HashMismatch(RuntimeError):
    """A pinned hash of the frozen object differs: A6.2 forbids scoring."""


class NonFinite(ValueError):
    """A non-finite feature, weight, score or margin (A6.2, C6-2): the scorer stops; it is never counted as a wrong decision. The cause is a pipeline defect (card v3 section 17); nothing is refitted."""


# A6.2 hash table (r1), raw bytes. The re-frozen model.npz / spec.json hashes come from the A6.0 item 2 row (--pins); lrf.py may be the re-freeze version (also via --pins).
EXPECTED_CODEBOOK_SHA256 = "ff15b9b5b362dc80f8a18f6e852e6e99478c0e8885646735ed16d1d80e3ae50b"      # runs/P2-GATE-M1/codebook.npy (nbr; untracked)
EXPECTED_DI_N013_SHA256 = "f7744253a1b997b8b9f28d9b91348e8371f1ea1e3564f6c8bfc2f10aa5b42176"        # runs/P2-GATE-DCACHE/DI_n013.npy (D at L_FIX; untracked)
DEFAULT_PINS = dict(code_sha256={"data.py": "14421ffb1061947a8408406750e8417282188efeccf07cac3142179fed9f429b", "families.py": "1c49827d723ea17017f84ba283fcfa681bf24e10c0a0e7d62b6a83064f850a7e"},
                    codebook_sha256=EXPECTED_CODEBOOK_SHA256, di_sha256=EXPECTED_DI_N013_SHA256, di_file="DI_n013.npy", decision_rule=DECISION_RULE)
ENTRY_POINTS = ("exp_p2/run_gate_m4.py", "exp_p2/run_gate_lrf_rescore.py", "exp_p2/gate/lrf_score.py")      # "the L_FIX scoring entry points" of the A6.2 table; their hashes are recorded in the meta for the pin row


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha256_lf(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def this_code_sha256() -> str:
    return sha256_lf(Path(__file__))


def _matches(p: Path, want: str) -> str | None:
    """'raw' or 'lf' if the file hashes to `want` that way, else None."""
    if sha256_file(p) == want:
        return "raw"
    return "lf" if sha256_lf(p) == want else None


def load_frozen(frozen_dir: Path | str = FROZEN_DIR, code_dir: Path | str = CODE_DIR, pins: dict | None = None) -> dict:
    """Load and verify the frozen model. Returns dict(a, b, c, knots, mu, sd, spec, engineer (callable), feature_names, hashes). Raises HashMismatch / FileNotFoundError / ValueError."""
    frozen_dir, code_dir = Path(frozen_dir), Path(code_dir)
    spec = json.loads((frozen_dir / "spec.json").read_text(encoding="utf8"))
    model = frozen_dir / "model.npz"
    got = sha256_file(model)
    if got != spec["model_sha256"]:
        raise HashMismatch(f"model.npz sha256 {got} != spec.json {spec['model_sha256']}")
    hashes = dict(model_sha256=got, code_sha256={}, scoring_code_sha256=this_code_sha256(), decision_rule=DECISION_RULE)
    for name, want in spec["code_sha256"].items():
        p = code_dir / name
        if not p.exists():
            raise FileNotFoundError(f"{p} missing: spec.json pins {name}")
        how = _matches(p, want)
        if how is None:
            raise HashMismatch(f"{p} differs from the pinned {name} sha256 {want} (raw {sha256_file(p)}, LF-normalised {sha256_lf(p)})")
        hashes["code_sha256"][name] = want
    if pins:
        if "model_sha256" in pins and pins["model_sha256"] != got:
            raise HashMismatch(f"pins model_sha256 {pins['model_sha256']} != loaded {got}")
        for name, want in (pins.get("code_sha256") or {}).items():
            if hashes["code_sha256"].get(name) != want:
                raise HashMismatch(f"pins code_sha256[{name}] {want} != loaded {hashes['code_sha256'].get(name)}")
        if "scoring_code_sha256" in pins and pins["scoring_code_sha256"] != hashes["scoring_code_sha256"]:
            raise HashMismatch(f"pins scoring_code_sha256 {pins['scoring_code_sha256']} != this file {hashes['scoring_code_sha256']}")
        if "decision_rule" in pins and pins["decision_rule"] != DECISION_RULE:
            raise HashMismatch(f"pins decision_rule {pins['decision_rule']!r} != {DECISION_RULE!r}")
        hashes["pinned_externally"] = True
    else:
        hashes["pinned_externally"] = False
    if "data.py" not in spec["code_sha256"]:
        raise ValueError("spec.json does not pin the feature code data.py")
    mod_spec = importlib.util.spec_from_file_location("lrf_frozen_features", code_dir / "data.py")
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    z = np.load(model)
    names = [str(x) for x in z["feature_names"]]
    if not (names == list(spec["features"]) == list(mod.feature_names())):
        raise HashMismatch("feature list differs between model.npz, spec.json and the feature code")
    fz = {k: z[k].astype(np.float64) for k in ("a", "b", "c", "knots", "mu", "sd")}
    return dict(fz, spec=spec, engineer=mod.engineer, feature_names=names, hashes=hashes)


def verify_run_inputs(run_dir: Path, runs_dir: Path, pins: dict) -> dict:
    """A6.2 hash set, the untracked inputs: the M1 codebook (nbr) and the D-cache file of the fixed slot (D). Both are hashed on disk in this checkout AND compared with what the GPU run recorded in its config.json
    (`codebook_sha256`, `dcache_di_sha256`); a missing file, a missing record or any difference raises HashMismatch. Returns the verified values."""
    runs_dir, run_dir = Path(runs_dir), Path(run_dir)
    out = {}
    files = {"codebook_sha256": runs_dir / "P2-GATE-M1" / "codebook.npy", "di_sha256": runs_dir / config.DCACHE_RUN_ID / pins["di_file"]}
    for key, p in files.items():
        if not p.exists():
            raise HashMismatch(f"{p} missing: LRF's features need it (A6.2 hash set)")
        got = sha256_file(p)
        if got != pins[key]:
            raise HashMismatch(f"{p} sha256 {got} != pinned {pins[key]}")
        out[key] = got
    cfgp = run_dir / "config.json"
    rec = json.loads(cfgp.read_text(encoding="utf8")) if cfgp.exists() else {}
    for key, rk in (("codebook_sha256", "codebook_sha256"), ("di_sha256", "dcache_di_sha256")):
        if rec.get(rk) != out[key]:
            raise HashMismatch(f"{cfgp}: recorded {rk} {rec.get(rk)!r} != verified {out[key]} (the run must record the hashes of its inputs, runs run with --layout-fix do)")
    return out


def entry_point_hashes() -> dict:
    return {rel: sha256_lf(ROOT / rel) for rel in ENTRY_POINTS if (ROOT / rel).exists()}


# ---------------------------------------------------------------- inference (numpy)
def raw_from_arrays(d, cond: str) -> dict:
    """The 7 raw caption-withheld scores of one condition, shapes [1, 1, 1024] (as the frozen feature code expects)."""
    B, D = np.asarray(d[f"{cond}_B"], np.float32), np.asarray(d[f"{cond}_D"], np.float32)
    raw = dict(B=B, D=D, q=B - D, s3=np.asarray(d[f"{cond}_s3"], np.float32), tbv=np.asarray(d[f"{cond}_tbv"], np.float32),
               ltex=np.log1p(np.maximum(np.asarray(d[f"{cond}_tex"]), 0)).astype(np.float32), nbr=np.asarray(d[f"{cond}_nbr"], np.float32))
    for k, v in raw.items():
        if not np.isfinite(v).all():
            raise NonFinite(f"non-finite values in {cond}_{k}")
    return {k: v.reshape(1, 1, -1) for k, v in raw.items()}


def gam_f(fz: dict, Xs: np.ndarray) -> np.ndarray:
    """f = b + sum_k a_k x_k + sum_km c_km relu(x_k - t_km) on standardised features Xs [..., F]."""
    f = Xs @ fz["a"] + fz["b"]
    if fz["knots"].shape[1]:
        f = f + np.einsum("...fk,fk->...", np.maximum(Xs[..., None] - fz["knots"], 0.0), fz["c"])
    return f


def weights(fz: dict, d, cond: str) -> np.ndarray:
    """w_j in (0, 1) for the 1024 tokens of one stored condition."""
    X = fz["engineer"](raw_from_arrays(d, cond))
    Xs = ((X - fz["mu"]) / fz["sd"]).astype(np.float64)
    if not np.isfinite(Xs).all():
        raise NonFinite(f"non-finite engineered feature for {cond}")
    w = (1.0 / (1.0 + np.exp(-gam_f(fz, Xs))))[0, 0]
    if not np.isfinite(w).all():
        raise NonFinite(f"non-finite weight for {cond}")
    return w


def decide(w: np.ndarray, delta: np.ndarray) -> dict:
    """Y_LRF and its margin. A tie (score exactly 0) is wrong. Any non-finite weight, Delta, score or margin (an all-zero weight vector included: its margin is 0/0) raises NonFinite (C6-2)."""
    w, d = np.asarray(w, np.float64), np.asarray(delta, np.float64)
    if not (np.isfinite(w).all() and np.isfinite(d).all()):
        raise NonFinite("non-finite weight or Delta")
    s = float((w * d).sum())
    sw = float(w.sum())
    margin = s / sw if sw > 0 else float("nan")
    if not (np.isfinite(s) and np.isfinite(margin)):
        raise NonFinite(f"non-finite score or margin (score {s}, weight sum {sw})")
    return dict(score=s, y=int(s > 0), margin=margin)


def arm_y(delta: np.ndarray, flag: np.ndarray | None) -> tuple[int, float]:
    """(Y, margin) of NONE (flag None: all tokens) and of GATE-M (unflagged tokens), as the runner computes them (evidence.evidence_from_delta; mean > 0)."""
    ev = evidence.evidence_from_delta(delta, None if flag is None else ~np.asarray(flag, bool))
    return int(ev["y"]), float(ev["mean"])


def score_item(fz: dict, d, cond: str, with_L: bool = False) -> dict:
    """Predictions of one stored item and condition (the array dict `d` as written by run_gate_m4)."""
    missing = [k for k in NEEDED if f"{cond}_{k}" not in d]
    if missing:
        raise KeyError(f"condition {cond}: arrays {missing} not stored (LRF needs {NEEDED}; run the stage with --tbv on)")
    w = weights(fz, d, cond)
    flag = d[f"{cond}_flag{config.ALPHA_PRIMARY:g}"]
    out = {}
    for tag, key in (("", "delta"),) + ((("_L", "deltaL"),) if with_L else ()):
        delta = d[f"{cond}_{key}"]
        if not np.isfinite(np.asarray(delta, np.float64)).all():
            raise NonFinite(f"non-finite values in {cond}_{key}")
        yn, mn = arm_y(delta, None)
        yg, mg = arm_y(delta, flag)
        r = decide(w, delta)
        out.update({f"y_none{tag}": yn, f"y_gatem{tag}": yg, f"y_lrf{tag}": r["y"], f"m_none{tag}": mn, f"m_gatem{tag}": mg, f"m_lrf{tag}": r["margin"]})
    out["w_sum"], out["w_mean"] = float(w.sum()), float(w.mean())
    return out


def crosscheck(fz: dict, d, cond: str):
    """Max |w| difference to analysis_posthoc.learned_ceiling.lrf.weights_from_raw (the code that wrote the freeze); None if that module is not importable here (torch, or the file, absent)."""
    try:
        from analysis_posthoc.learned_ceiling import lrf
    except Exception:                                                         # noqa: BLE001  (ImportError, or torch missing)
        return None
    fl = {k: np.asarray(fz[k]) for k in ("a", "b", "c", "knots", "mu", "sd")}
    return float(np.abs(lrf.weights_from_raw(fl, lrf.raw_from_npz(d, cond))[0, 0] - weights(fz, d, cond)).max())


# ---------------------------------------------------------------- run
def committed_rows(run_dir: Path) -> list[dict]:
    seen, out = set(), []
    for r in common.read_jsonl(Path(run_dir) / "items.jsonl"):
        if r["idx"] not in seen:
            seen.add(r["idx"])
            out.append(r)
    return sorted(out, key=lambda r: r["idx"])


def score_run(run_dir: Path, fz: dict, conds=L1_CONDS, *, with_L: bool | None = None, n_items: int | None = None) -> tuple[list[dict], dict]:
    """-> (prediction lines, meta). `with_L` None = automatic (the length-matched negative is scored for the items whose arrays hold `<cond>_deltaL`). Items without a row or arrays are skipped (complete case).
    Positive control: y_none and y_gatem equal the runner's row (img.none.y, img.gate0.05.y); a difference raises AssertionError."""
    run_dir = Path(run_dir)
    out, n_checked, n_skipped, absent = [], 0, 0, set()
    rows = committed_rows(run_dir)
    rows = rows[:n_items] if n_items else rows
    for r in rows:
        p = run_dir / "arrays" / f"item{r['idx']:04d}.npz"
        if not p.exists():
            n_skipped += 1
            continue
        d = dict(np.load(p))
        for c in conds:
            if c not in r["conds"]:
                absent.add(c)
                continue
            L = with_L if with_L is not None else (f"{c}_deltaL" in d)
            s = score_item(fz, d, c, L)
            cr = r["conds"][c]
            assert s["y_none"] == cr["img"]["none"]["y"], f"item {r['idx']} {c}: recomputed Y_NONE {s['y_none']} != runner row {cr['img']['none']['y']}"
            assert s["y_gatem"] == cr["img"][GATE_ARM]["y"], f"item {r['idx']} {c}: recomputed Y_GATE-M {s['y_gatem']} != runner row {cr['img'][GATE_ARM]['y']}"
            n_checked += 1
            line = dict(idx=r["idx"], gid=r["gid"], image_id=r["image_id"], condition=c, n_tok=r["n_tok"], n_tok_neg=r["n_tok_neg"], **s)
            if L:
                line.update(n_tok_neg_len=r.get("n_tok_neg_len"), neg_len_diff=(r["n_tok_neg_len"] - r["n_tok"]) if r.get("n_tok_neg_len") is not None else None,
                            neg_len_exact=(r["n_tok_neg_len"] == r["n_tok"]) if r.get("n_tok_neg_len") is not None else None)
            out.append(line)
    meta = dict(run_dir=str(run_dir), n_items_rows=len(rows), n_items_skipped_no_arrays=n_skipped, conds=list(conds), conds_absent_in_rows=sorted(absent), n_lines=len(out), positive_control=dict(n_checked=n_checked, ok=True),
                hashes=fz["hashes"], model_name=fz["spec"].get("name"), decision_rule=DECISION_RULE)
    return out, meta


def write_predictions(lines: list[dict], meta: dict, out: Path, *, force: bool = False) -> Path:
    out = Path(out)
    if out.exists() and not force:
        raise FileExistsError(f"{out} exists; pass --force to overwrite")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(l, sort_keys=True) + "\n" for l in lines), encoding="utf8")
    meta = dict(meta, predictions_sha256=sha256_file(out))
    (out.parent / "lrf_score_meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True), encoding="utf8")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--frozen-dir", default=str(FROZEN_DIR))
    ap.add_argument("--code-dir", default=str(CODE_DIR))
    ap.add_argument("--pins", default=None, help="JSON with model_sha256 / code_sha256 / scoring_code_sha256 / decision_rule copied from the A6.0 item 2 row")
    ap.add_argument("--conds", default=",".join(L1_CONDS))
    ap.add_argument("--n", type=int, default=None, help="score the first n committed items only (LG prefix of 300)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--crosscheck", action="store_true")
    a = ap.parse_args(argv)
    run_dir = Path(common.RUNS) / a.run_id
    try:
        pins = json.loads(Path(a.pins).read_text(encoding="utf8")) if a.pins else {}
        user = pins
        pins = dict(DEFAULT_PINS, **{k: v for k, v in user.items() if k != "code_sha256"})                                     # the r1 table unless the A6.0 item 2 row says otherwise
        pins["code_sha256"] = dict(DEFAULT_PINS["code_sha256"], **(user.get("code_sha256") or {}))
        fz = load_frozen(a.frozen_dir, a.code_dir, pins)
        verified = verify_run_inputs(run_dir, Path(common.RUNS), pins)
        conds = tuple(c for c in a.conds.split(",") if c)
        lines, meta = score_run(run_dir, fz, conds, n_items=a.n)
    except (HashMismatch, FileNotFoundError, NonFinite, ValueError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    meta["hashes"] = dict(meta["hashes"], codebook_sha256=verified["codebook_sha256"], di_sha256=verified["di_sha256"], entry_points=entry_point_hashes())
    if a.crosscheck:
        d = dict(np.load(run_dir / "arrays" / f"item{lines[0]['idx']:04d}.npz"))
        meta["crosscheck_max_abs_w_diff"] = crosscheck(fz, d, lines[0]["condition"])
    try:
        out = write_predictions(lines, meta, Path(a.out) if a.out else run_dir / "predictions.jsonl", force=a.force)
    except FileExistsError as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    print(json.dumps(dict(out=str(out), n_lines=len(lines), positive_control=meta["positive_control"], hashes=meta["hashes"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
