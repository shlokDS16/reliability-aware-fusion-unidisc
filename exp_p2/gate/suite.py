"""imagecorruptions exploratory suite (SAP A2 AD.9, AB.8): corruption cells, seeded application, CPU smoke test and the cell analysis. Exploratory, Tier 3: no p-value enters a claim.

Source: the `imagecorruptions` package (Michaelis et al. 2019, arXiv:1907.07484; Apache-2.0) installed from the GitHub commit c959e659c9713837d2acd7ce785a81202d4be799 (PyPI 1.1.2 is broken on current
scikit-image, data-steward note). Types (fixed by kind, researcher choice, AB.8): pixelate, defocus_blur, fog, impulse_noise; severities 2 and 4 of the package's 1 to 5 scale: 8 cells. A type absent under its
name is dropped, never replaced. The corruption seed is derived from the item id (8.3).

    python -m exp_p2.gate.suite smoke [--n 5]          # 5-image CPU smoke test -> runs/P2-SUITE-SMOKE/smoke.json (+ a determinism check of every cell)
    python -m exp_p2.gate.suite analyze                # CPU: cell table from runs/P2-GATE-SUITE (after the GPU run)

Per cell the analysis reports (image direction): arms none, GATE-M, chg; b, c_cnt, net difference with a 95 percent paired-bootstrap CI; the E-dec split; and, if the plug-in signs are supplied, the E-pred
sign agreement over the cells with a Clopper-Pearson interval, reported separately from AD.3 and never pooled with the P or PS cells."""
from __future__ import annotations

import argparse
import contextlib
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import config, report, seeds, stats, theory               # noqa: E402

SUITE_RUN_ID = "P2-GATE-SUITE"
SMOKE_RUN_ID = "P2-SUITE-SMOKE"
PACKAGE = dict(name="imagecorruptions", repo="https://github.com/bethgelab/imagecorruptions", commit="c959e659c9713837d2acd7ce785a81202d4be799", licence="Apache-2.0",
               paper="Michaelis et al. 2019, arXiv:1907.07484", note="installed from the commit because PyPI 1.1.2 calls gaussian(multichannel=True), removed from scikit-image (issue #30)")
TYPES = ("pixelate", "defocus_blur", "fog", "impulse_noise")
SEVERITIES = (2, 4)
CELLS = tuple((t, s) for t in TYPES for s in SEVERITIES)          # 8 cells, order fixed now
HEAD_N, TEST_N = 100, 100                                         # the 100 headroom items (fit fold for E-pred) and the first 100 items of the test list
SUITE_ARMS = ("none", "gm", "chg")
CI_LEVEL = 95.0


def cell_key(name: str, severity: int) -> str:
    return f"{name}{int(severity)}"


CELL_KEYS = tuple(cell_key(t, s) for t, s in CELLS)


def corruption_seed(gid: int, cell_index: int) -> int:
    """Item-id-derived 32-bit seed (8.3): SeedSequence([gate seed, item gid, cell index, tag]); one realisation per item and cell."""
    return int(np.random.SeedSequence([config.SEED_GATE, int(gid), int(cell_index), 8001]).generate_state(1)[0])


# ------------------------------------------------------------------------------------------------ application
def load_package():
    """Import imagecorruptions (needs numba, scikit-image, opencv, scipy, setuptools' pkg_resources). Returns the module; raises ImportError with the install command."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import imagecorruptions as ic
    except ImportError as e:
        raise ImportError(f"imagecorruptions is not installed in this interpreter ({e}); install the pinned commit: uv pip install --python <venv python> \"git+{PACKAGE['repo']}@{PACKAGE['commit']}\" "
                          "plus numba and scikit-image") from e
    return ic


def available_types(ic=None) -> list[str]:
    """The suite's types that exist in the installed package under their names (a missing one is dropped, not replaced)."""
    ic = ic or load_package()
    names = set(ic.get_corruption_names("all"))
    return [t for t in TYPES if t in names]


@contextlib.contextmanager
def _seeded(seed: int):
    """Make the package's randomness a function of `seed`. fog draws from the legacy global numpy RNG, which is seeded and restored; impulse_noise calls skimage.util.random_noise without a seed
    (a fresh default_rng each call in scikit-image >= 0.19), so that function is wrapped to pass rng=default_rng(seed) for the duration of the call. Nothing else is touched."""
    import skimage.util as sku
    state = np.random.get_state()
    orig = sku.random_noise
    np.random.seed(seed % (2 ** 32))

    def wrapped(image, mode="gaussian", rng=None, clip=True, **kw):
        return orig(image, mode=mode, rng=np.random.default_rng(seed), clip=clip, **kw)
    sku.random_noise = wrapped
    try:
        yield
    finally:
        sku.random_noise = orig
        np.random.set_state(state)


def apply_corruption(name: str, severity: int, pil512, seed: int, ic=None):
    """Corrupt a 512 x 512 RGB PIL image (the image the model sees after `preprocess`) with one imagecorruptions type at integer severity 1 to 5. Deterministic given `seed`. Returns a PIL image of the same size."""
    from PIL import Image
    ic = ic or load_package()
    arr = np.asarray(pil512.convert("RGB"))
    assert arr.dtype == np.uint8 and arr.ndim == 3 and arr.shape[2] == 3
    with _seeded(seed), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        out = ic.corrupt(arr, severity=int(severity), corruption_name=name)
    assert out.shape == arr.shape and out.dtype == np.uint8
    return Image.fromarray(out)


def center_crop_512(pil):
    """Model-free copy of UniScorer.preprocess (centre crop, bicubic resize to 512), for the CPU smoke test only; the GPU runner uses sc.preprocess."""
    from PIL import Image
    w, h = pil.size
    s = min(w, h)
    left, top = (w - s) // 2, (h - s) // 2
    return pil.convert("RGB").crop((left, top, left + s, top + s)).resize((512, 512), Image.BICUBIC)


# ------------------------------------------------------------------------------------------------ smoke test
def smoke(out_dir: Path | None = None, n: int = 5, save_images: bool = True) -> dict:
    """CPU smoke test of all cells on `n` head-fold images (COCO images; no model): shapes, dtypes, seconds, change vs the clean image, determinism (the same call twice is byte-identical), and a
    different seed gives a different result for the random types (fog, impulse_noise). Writes smoke.json (+ PNGs, which are COCO images and are not committed)."""
    from exp_p2.gate import folds as folds_mod
    out = Path(out_dir) if out_dir else Path(common.RUNS) / SMOKE_RUN_ID
    out.mkdir(parents=True, exist_ok=True)
    f = json.loads(folds_mod.folds_path().read_text(encoding="utf8"))
    items = f["head"][:n]
    t0 = time.perf_counter()
    ic = load_package()
    import_s = time.perf_counter() - t0
    types = available_types(ic)
    dropped = [t for t in TYPES if t not in types]
    rows = []
    for it in items:
        pil = center_crop_512(common.load_image(it["image_id"]))
        clean = np.asarray(pil)
        for ci, (t, s) in enumerate(CELLS):
            if t not in types:
                continue
            seed = corruption_seed(it["gid"], ci)
            t1 = time.perf_counter()
            a = apply_corruption(t, s, pil, seed, ic)
            sec = time.perf_counter() - t1
            b = apply_corruption(t, s, pil, seed, ic)
            c = apply_corruption(t, s, pil, seed + 1, ic)
            aa = np.asarray(a)
            rows.append(dict(image_id=it["image_id"], gid=it["gid"], cell=cell_key(t, s), name=t, severity=s, seed=seed, in_shape=list(clean.shape), in_dtype=str(clean.dtype), out_shape=list(aa.shape),
                             out_dtype=str(aa.dtype), seconds=sec, mean_abs_diff_grey=float(np.abs(aa.astype(np.int16) - clean.astype(np.int16)).mean()), changed_pixel_share=float((aa != clean).any(axis=2).mean()),
                             deterministic_same_seed=bool(np.array_equal(aa, np.asarray(b))), differs_with_other_seed=bool(not np.array_equal(aa, np.asarray(c))),
                             sha1=__import__("hashlib").sha1(aa.tobytes()).hexdigest()[:16]))
            if save_images:
                a.save(out / f"{it['image_id']:012d}_{cell_key(t, s)}.png")
    random_types = {"fog", "impulse_noise"}
    res = dict(package=PACKAGE, versions=_versions(), import_seconds=import_s, types_available=types, types_dropped=dropped, cells=[cell_key(t, s) for t, s in CELLS], n_images=len(items),
               image_ids=[it["image_id"] for it in items], rows=rows,
               summary=dict(n_calls=len(rows), all_uint8_same_shape=all(r["out_dtype"] == "uint8" and r["out_shape"] == r["in_shape"] for r in rows), all_deterministic=all(r["deterministic_same_seed"] for r in rows),
                            random_types_vary_with_seed=all(r["differs_with_other_seed"] for r in rows if r["name"] in random_types), all_change_the_image=all(r["mean_abs_diff_grey"] > 0 for r in rows),
                            seconds_per_call_mean=float(np.mean([r["seconds"] for r in rows])) if rows else None, seconds_per_call_max=float(np.max([r["seconds"] for r in rows])) if rows else None,
                            seconds_per_cell={k: float(np.mean([r["seconds"] for r in rows if r["cell"] == k])) for k in CELL_KEYS if any(r["cell"] == k for r in rows)}),
               note="CPU only, no model; images are COCO val2017 head-fold images (PNGs are not committed: COCO/Flickr licences)", created=time.strftime("%Y-%m-%dT%H:%M:%S"))
    (out / "smoke.json").write_text(json.dumps(res, indent=1), encoding="utf8")
    return res


def _versions() -> dict:
    import importlib.metadata as md
    out = {}
    for p in ("imagecorruptions", "numpy", "scipy", "scikit-image", "numba", "llvmlite", "opencv-python-headless", "opencv-python", "pillow", "setuptools"):
        try:
            out[p] = md.version(p)
        except md.PackageNotFoundError:
            pass
    out["python"] = sys.version.split()[0]
    return out


# ------------------------------------------------------------------------------------------------ analysis
def edec_split(d_clean, d_none, d_chg, d_gm) -> dict:
    """AD.2 on the size-free evidence d, item by item: T = d_clean - d_none, U = d_clean - d_chg, R = d_gm - d_none, V = d_chg - d_gm, and T = U + R + V holds item by item (asserted to 1e-9).
    Complete case: an item enters only if all four d are finite. Returns the four arrays and the number dropped."""
    a = [np.asarray(x, float) for x in (d_clean, d_none, d_chg, d_gm)]
    ok = np.all([np.isfinite(x) for x in a], axis=0)
    c, n, g, m = (x[ok] for x in a)
    T, U, R, V = c - n, c - g, m - n, g - m
    if T.size:
        assert np.allclose(T, U + R + V, atol=1e-9, rtol=0), "E-dec identity T = U + R + V violated"
    return dict(T=T, U=U, R=R, V=V, n=int(ok.sum()), n_dropped=int((~ok).sum()))


def _boot_means(parts: dict[str, np.ndarray], n_boot: int, seed) -> dict:
    """Joint paired bootstrap over items (the same resample for T, U, R, V so the identity holds in every resample); 95 percent percentile intervals."""
    n = len(next(iter(parts.values())))
    out = {}
    if n < 2:
        return {k: dict(mean=float(v.mean()) if n else float("nan"), ci95=[float("nan")] * 2) for k, v in parts.items()} | dict(_identity_in_resamples=None)
    idx = np.random.default_rng(seed).integers(0, n, size=(n_boot, n))
    boots = {k: v[idx].mean(axis=1) for k, v in parts.items()}
    ident = bool(np.allclose(boots["T"], boots["U"] + boots["R"] + boots["V"], atol=1e-9))
    lo, hi = (100 - CI_LEVEL) / 200, 1 - (100 - CI_LEVEL) / 200
    for k, v in parts.items():
        out[k] = dict(mean=float(v.mean()), ci95=[float(np.quantile(boots[k], lo)), float(np.quantile(boots[k], hi))])
    out["_identity_in_resamples"] = ident
    return out


def edec_cell(d_clean, d_none, d_chg, d_gm, *, n_boot: int = 10000, seed=None) -> dict:
    """E-dec for one cell (AB.2 names: U = residual loss under the oracle gate, V = gap to the oracle gate). Shares U/T, R/T, V/T are reported only if the lower 95 percent bound of tau_T exceeds 0."""
    sp = edec_split(d_clean, d_none, d_chg, d_gm)
    parts = {k: sp[k] for k in ("T", "U", "R", "V")}
    est = _boot_means(parts, n_boot, seed if seed is not None else np.random.SeedSequence([seeds.ROOT_SEED, 9102]))
    res = dict(n=sp["n"], n_dropped_incomplete=sp["n_dropped"], tau=est, identity_per_item="asserted to 1e-9", label="secondary, descriptive; no test, no p-value (AD.2, AB.2)")
    t_lo = est["T"]["ci95"][0]
    if np.isfinite(t_lo) and t_lo > 0:
        tm = est["T"]["mean"]
        res["shares"] = {k: est[k]["mean"] / tm for k in ("U", "R", "V")}
    else:
        res["shares"] = "undefined (lower 95 percent bound of tau_T does not exceed 0)"
    return res


SUITE_COLS = ("fold", "idx", "cell", "y_clean", "y_none", "y_gm", "y_chg", "d_clean", "d_none", "d_gm", "d_chg", "n_changed", "n_flag", "n_tp")


def suite_frame(rows: list[dict]):
    """Run rows (items.jsonl of P2-GATE-SUITE) -> the long DataFrame `suite_cells` expects: one line per (item, cell) with the binary Y and the evidence d of the clean image and of the three arms."""
    import pandas as pd
    recs = []
    for r in rows:
        cl = r["clean"]
        for k, c in r["cells"].items():
            recs.append(dict(fold=r["fold"], idx=r["idx"], cell=k, y_clean=cl["y"], y_none=c["img"]["none"]["y"], y_gm=c["img"]["gm"]["y"], y_chg=c["img"]["chg"]["y"],
                             d_clean=cl["d"], d_none=c["img"]["none"]["d"], d_gm=c["img"]["gm"]["d"], d_chg=c["img"]["chg"]["d"], n_changed=c["n_changed"], n_flag=c["n_flag"], n_tp=c["n_tp"]))
    return pd.DataFrame.from_records(recs, columns=list(SUITE_COLS))


def epred_signs(head_arrays: dict[str, list[dict]]) -> dict:
    """Plug-in sign s_c per cell from the HEADROOM items (the fit fold of AD.3), pooled over items at token level through `theory.plug_in_from_deltas`: head_arrays[cell] is a list of dicts with the
    per-token 'delta', the changed-code labels 'z' and GATE-M's 'flag' of one headroom item. s_c = +1 if the plug-in SNR rises with gating, -1 otherwise, None if an input is not finite.
    This is the suite-local plug-in; the audited, frozen `epred_fit` of AB.3 (not available to this file's author) is what a claim-bearing E-pred uses, and it should replace this."""
    out = {}
    for cell, lst in head_arrays.items():
        if not lst:
            out[cell] = dict(sign=None, reason="no headroom items")
            continue
        d, z, f = (np.concatenate([np.asarray(x[k]) for x in lst]) for k in ("delta", "z", "flag"))
        pi = theory.plug_in_from_deltas(d, z, f)
        out[cell] = dict(sign=(None if "predicted_helps" not in pi else (1 if pi["predicted_helps"] else -1)), inputs=pi, n_items=len(lst))
    return out


def epred_agreement(s_c: dict, observed: dict) -> dict:
    """A = number of evaluable cells with s_c == o_c out of K_eval, with a Clopper-Pearson 95 percent interval. o_c = sign(b_c - c_cnt); a cell with b = c (or without a plug-in sign) is excluded and counted.
    Descriptive only (family E is withdrawn, AB.3); suite cells are never pooled with the P or PS cells."""
    ev, skipped, agree = {}, {}, 0
    for k, s in s_c.items():
        sg = s["sign"] if isinstance(s, dict) else s
        o = observed.get(k)
        if sg is None or o is None or o == 0:
            skipped[k] = "no plug-in sign" if sg is None else "b = c_cnt (no observed sign)" if o == 0 else "no observed sign"
            continue
        ev[k] = dict(s=int(sg), o=int(o), agree=bool(sg == o))
        agree += int(sg == o)
    K = len(ev)
    lo, hi = stats.clopper_pearson(agree, K, 0.95) if K else (float("nan"), float("nan"))
    rival_plus = sum(1 for v in ev.values() if v["o"] == 1)
    return dict(A=agree, K_eval=K, cp95=[lo, hi], cells=ev, skipped=skipped, rival_always_plus_agreement=rival_plus, label="exploratory, suite cells only; never pooled with AD.3; no p-value, no test",
                note="the observed sign is sign(b - c_cnt) of GATE-M against none on Y; a plug-in sign that disagrees with a cell whose interval excludes 0 refutes the independent-token model for that cell only")


def suite_cells(df, *, fold: str = "test", n_boot: int = 10000, seed=None, s_c: dict | None = None) -> dict:
    """The cell table of AD.9 from the long frame `df` (columns SUITE_COLS): for each of the cells present, on the items of `fold`: b, c_cnt, n_d, net difference (GATE-M minus none on Y) with a 95 percent paired
    percentile bootstrap CI, accuracies of none / GATE-M / chg, flag statistics, and the E-dec split on d. No exact p-value, no Holm, no multiplicity statement: Tier 3 exploratory. If `s_c` (cell -> plug-in sign
    or dict with 'sign') is given, the E-pred agreement over the evaluable cells is added. Items are matched by (fold, idx); an item missing a cell is simply absent from that cell."""
    import pandas as pd
    d = df[df["fold"] == fold]
    sd = seed if seed is not None else np.random.SeedSequence([seeds.ROOT_SEED, 9101])
    cells, observed = {}, {}
    for k in [c for c in CELL_KEYS if c in set(d["cell"])] + sorted(set(d["cell"]) - set(CELL_KEYS)):
        g = d[d["cell"] == k].sort_values("idx")
        y_gm, y_none, y_chg, y_cl = (g[c].to_numpy(float) for c in ("y_gm", "y_none", "y_chg", "y_clean"))
        rep = report.report_test(y_gm, y_none, n_boot=n_boot, seed=sd)
        rep = {kk: v for kk, v in rep.items() if kk not in ("p", "p_mid", "ci9833", "ci90", "equivalent_within_0p05", "theta_cp95")}        # Tier 3: no p-value
        cells[k] = dict(n_items=int(len(g)), gm_vs_none=rep, net_difference=rep["delta"], acc_clean=float(np.nanmean(y_cl)), acc_none=float(np.nanmean(y_none)), acc_gm=float(np.nanmean(y_gm)),
                        acc_chg=float(np.nanmean(y_chg)), mean_n_changed=float(g["n_changed"].mean()), mean_n_flag=float(g["n_flag"].mean()),
                        flag_precision=(float(g["n_tp"].sum() / g["n_flag"].sum()) if g["n_flag"].sum() > 0 else None), flag_recall=(float(g["n_tp"].sum() / g["n_changed"].sum()) if g["n_changed"].sum() > 0 else None),
                        edec=edec_cell(g["d_clean"], g["d_none"], g["d_chg"], g["d_gm"], n_boot=n_boot, seed=sd), sign_observed=int(np.sign(rep["b"] - rep["c"])))
        observed[k] = cells[k]["sign_observed"]
    out = dict(fold=fold, n_cells=len(cells), cells=cells, label="Tier 3, exploratory. No p-value enters a claim; no multiplicity statement (AD.9)", meta=seeds.meta(),
               choice="the four types and two severities were chosen by kind from a package of fifteen types with no recorded rationale: researcher choice (AB.8)")
    if s_c is not None:
        out["epred_suite"] = epred_agreement(s_c, observed)
    return out


# ------------------------------------------------------------------------------------------------ CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["smoke", "analyze"])
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--run", default=SUITE_RUN_ID)
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "smoke":
        r = smoke(n=a.n, save_images=not a.no_images)
        print(json.dumps(dict(types_available=r["types_available"], types_dropped=r["types_dropped"], versions=r["versions"], summary=r["summary"]), indent=1))
        s = r["summary"]
        return 0 if (s["all_uint8_same_shape"] and s["all_deterministic"] and s["random_types_vary_with_seed"] and s["all_change_the_image"] and not r["types_dropped"]) else 2
    run_dir = Path(common.RUNS) / a.run
    rows = []
    seen = set()
    for r in common.read_jsonl(run_dir / "items.jsonl"):
        if r["idx"] not in seen:
            seen.add(r["idx"])
            rows.append(r)
    df = suite_frame(rows)
    res = suite_cells(df, fold="test", n_boot=a.boot)
    (run_dir / "analysis.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf8")
    for k, c in res["cells"].items():
        print(k, "n", c["n_items"], "b", c["gm_vs_none"]["b"], "c", c["gm_vs_none"]["c"], "net", round(c["net_difference"], 3), "ci95", [round(x, 3) for x in c["gm_vs_none"]["ci95"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
