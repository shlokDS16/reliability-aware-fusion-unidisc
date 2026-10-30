"""imagecorruptions exploratory suite (SAP A2 AD.9, AB.8): corruption cells, seeded application, CPU smoke test and the cell analysis. Exploratory, Tier 3: no p-value enters a claim.

Source: the `imagecorruptions` package (Michaelis et al. 2019, arXiv:1907.07484; Apache-2.0) installed from the GitHub commit c959e659c9713837d2acd7ce785a81202d4be799 (PyPI 1.1.2 is broken on current
scikit-image, data-steward note). Types (fixed by kind, researcher choice, AB.8): pixelate, defocus_blur, fog, impulse_noise; severities 2 and 4 of the package's 1 to 5 scale: 8 cells. A type absent under its
name is dropped, never replaced. The corruption seed is derived from the item id (8.3).

    python -m exp_p2.gate.suite smoke [--n 5]          # 5-image CPU smoke test -> runs/P2-SUITE-SMOKE/smoke.json (+ a determinism check of every cell)
    python -m exp_p2.gate.suite analyze                # CPU: cell table and the E-pred suite block from runs/P2-GATE-SUITE (after the GPU run)

Per cell the analysis reports (image direction): arms none, GATE-M, chg; b, c_cnt, net difference with a 95 percent paired-bootstrap CI; the E-dec split; and, if the plug-in signs are supplied, the E-pred
sign agreement over the cells with a Clopper-Pearson interval, produced by `analyze` from the headroom items of the same run, reported separately from AD.3 and never pooled with the P or PS cells."""
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
from exp_p2.gate import config, edec as edec_mod, epred, epred_fit, report, seeds   # noqa: E402     (E-dec and E-pred are computed by the audited modules, not by copies)

SUITE_RUN_ID = "P2-GATE-SUITE"
SMOKE_RUN_ID = "P2-SUITE-SMOKE"
PACKAGE = dict(name="imagecorruptions", repo="https://github.com/bethgelab/imagecorruptions", commit="c959e659c9713837d2acd7ce785a81202d4be799", licence="Apache-2.0",
               paper="Michaelis et al. 2019, arXiv:1907.07484", note="installed from the commit because PyPI 1.1.2 calls gaussian(multichannel=True), removed from scikit-image (issue #30)")
TYPES = ("pixelate", "defocus_blur", "fog", "impulse_noise")
SEVERITIES = (2, 4)
CELLS = tuple((t, s) for t in TYPES for s in SEVERITIES)          # 8 cells, order fixed now
HEAD_N, TEST_N = 100, 100                                         # the 100 headroom items (fit fold for E-pred) and the first 100 items of the test list
SUITE_ARMS = ("none", "gm", "chg")
SEED_NAME = "suite"                                               # seeds.ANALYSES position 31 (appended 2026-10-28); the bootstrap stream of every suite interval


def cell_key(name: str, severity: int) -> str:
    return f"{name}{int(severity)}"


CELL_KEYS = tuple(cell_key(t, s) for t, s in CELLS)


def corruption_seed(gid: int, cell_index: int) -> int:
    """Item-id-derived 32-bit seed (8.3): SeedSequence([gate seed, item gid, cell index, tag]); one realisation per item and cell."""
    return int(np.random.SeedSequence([config.SEED_GATE, int(gid), int(cell_index), 8001]).generate_state(1)[0])


# ------------------------------------------------------------------------------------------------ application
class PinnedCommitMismatch(ImportError):
    """The installed imagecorruptions is not the pinned commit (an ImportError subclass so that every prerequisite check that stops on a missing package also stops on this)."""


def installed_commit() -> str | None:
    """The git commit the installed `imagecorruptions` distribution was built from, read at run time from its PEP 610 metadata (direct_url.json, vcs_info.commit_id); None if the package is not installed or
    was not installed from a VCS URL (e.g. the broken PyPI 1.1.2, whose version string is the same)."""
    import importlib.metadata as md
    try:
        raw = md.distribution(PACKAGE["name"]).read_text("direct_url.json")
    except md.PackageNotFoundError:
        return None
    if raw is None:
        return None
    return json.loads(raw).get("vcs_info", {}).get("commit_id")


def verify_pinned_commit() -> str:
    """Stop (PinnedCommitMismatch) unless the installed package is the pinned commit; returns the commit read from the metadata. Called by `load_package`, so every run and every smoke checks it (audit m4)."""
    got = installed_commit()
    if got != PACKAGE["commit"]:
        raise PinnedCommitMismatch(f"imagecorruptions was installed from commit {got!r}, not the pinned {PACKAGE['commit']} (PyPI 1.1.2 is broken on current scikit-image); reinstall: "
                                   f"uv pip install --python <venv python> \"git+{PACKAGE['repo']}@{PACKAGE['commit']}\"")
    return got


def load_package():
    """Import imagecorruptions (needs numba, scikit-image, opencv, scipy, setuptools' pkg_resources). Returns the module; raises ImportError with the install command, and PinnedCommitMismatch (an ImportError)
    if the installed distribution is not the pinned commit."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import imagecorruptions as ic
    except ImportError as e:
        raise ImportError(f"imagecorruptions is not installed in this interpreter ({e}); install the pinned commit: uv pip install --python <venv python> \"git+{PACKAGE['repo']}@{PACKAGE['commit']}\" "
                          "plus numba and scikit-image") from e
    verify_pinned_commit()
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
    out["imagecorruptions_commit"] = installed_commit()               # read from the installed metadata, not the constant (the version string 1.1.2 is the same as the broken PyPI release)
    out["python"] = sys.version.split()[0]
    return out


# ------------------------------------------------------------------------------------------------ analysis
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


def epred_signs(head_arrays: dict[str, list[dict]], *, n_boot: int = epred_fit.N_BOOT) -> dict:
    """Plug-in sign s_c per suite cell from the HEADROOM items (the fit fold of AD.3), computed by the audited `epred_fit.epred_fit` (pooled token-level inputs, `sign_of_gating`, tie and undefined handling,
    stability bootstrap with the seed of `prop4_plugin`). head_arrays[cell] is a list (one per headroom item, fixed order) of dicts with the per-token 'delta', the changed-code labels 'z' and GATE-M's
    'flag'. `epred_fit` only accepts the five labels of AD.3, so each suite cell is passed under the label "P1" in a call of its own and the result is re-keyed to the suite cell: the label is mechanical
    and enters no computation. Returns cell -> the cell of the fit result (sign +1 / -1 / 0 tie / None undefined, inputs, stability) with 'cell' set to the suite key. These suite signs are NOT the
    committed AD.3 signs and are not part of the frozen AD.3 file; the suite block is exploratory and is never pooled with AD.3 (AB.3 item 2)."""
    out = {}
    for cell, lst in head_arrays.items():
        if not lst:
            out[cell] = dict(cell=cell, sign=None, sign_text="none (undefined)", reason_no_sign="no headroom items", n_items=0)
            continue
        fit = epred_fit.epred_fit({"P1": [dict(delta=x["delta"], z=x["z"]) for x in lst]}, {"P1": [x["flag"] for x in lst]}, n_boot=n_boot)
        out[cell] = dict(fit["cells"]["P1"], cell=cell)
    return out


def load_head_arrays(run_dir: Path, rows: list[dict]) -> dict[str, list[dict]]:
    """Per suite cell, the headroom items' per-token inputs of `epred_signs` (delta, z, flag), read from runs/<run>/arrays/itemNNNN.npz in the fixed item order of the rows (fold == 'head')."""
    out: dict[str, list[dict]] = {}
    for r in sorted((r for r in rows if r["fold"] == "head"), key=lambda r: r["idx"]):
        path = Path(run_dir) / "arrays" / f"item{r['idx']:04d}.npz"
        if not path.exists():
            continue
        a = np.load(path)
        for k in r["cells"]:
            out.setdefault(k, []).append(dict(delta=a[f"{k}_delta"].astype(float), z=a[f"{k}_z"].astype(bool), flag=a[f"{k}_flag"].astype(bool)))
    return out


def analyze_run(run_dir: Path, *, n_boot: int = 10000, n_boot_epred: int | None = None) -> dict:
    """The CLI analysis: the cell table on the test items and, from the headroom items of the same run, the E-pred block (plug-in signs by the audited `epred_fit`, agreement by the audited `epred`;
    AD.9, A3b.7 item 2). If no headroom array exists the block is declared 'not produced' with the reason, never silently absent."""
    rows, seen = [], set()
    for r in common.read_jsonl(Path(run_dir) / "items.jsonl"):
        if r["idx"] not in seen:
            seen.add(r["idx"])
            rows.append(r)
    df = suite_frame(rows)
    head = load_head_arrays(run_dir, rows)
    signs = epred_signs(head, n_boot=n_boot_epred or epred_fit.N_BOOT) if head else None
    res = suite_cells(df, fold="test", n_boot=n_boot, s_c=signs)
    if signs is None:
        res["epred_suite"] = dict(produced=False, reason="no headroom arrays found under arrays/ for the head-fold rows: the plug-in signs cannot be computed (AD.9)")
    else:
        res["epred_suite_signs"] = {c: {k: v for k, v in sg.items() if k in ("sign", "sign_text", "n_items", "stability", "reason_no_sign")} for c, sg in signs.items()}
        res["epred_suite"]["produced"] = True
    return res


def suite_cells(df, *, fold: str = "test", n_boot: int = 10000, seed=None, s_c: dict | None = None) -> dict:
    """The cell table of AD.9 from the long frame `df` (columns SUITE_COLS): for each of the cells present, on the items of `fold`: b, c_cnt, n_d, net difference (GATE-M minus none on Y) with a 95 percent paired
    percentile bootstrap CI, accuracies of none / GATE-M / chg, flag statistics, and the E-dec split on d (`edec.edec_cell`, the audited function: identity asserted per item and per
    resample, complete case, shares rule, accuracy-scale companion). No exact p-value, no Holm, no multiplicity statement: Tier 3 exploratory. If `s_c` (cell -> output of `epred_signs`, a dict with 'sign',
    or a bare sign) is given, the agreement over the evaluable cells is added by `epred.epred_agreement` (A of K_eval, Clopper-Pearson, o_c*, rival rules; own block, never pooled with AD.3). Items are
    matched by (fold, idx); an item missing a cell is simply absent from that cell. Seed: `seeds.seed_for("suite")` unless `seed` is given."""
    import pandas as pd
    d = df[df["fold"] == fold]
    sd = seed if seed is not None else seeds.seed_for(SEED_NAME)
    cells, p_cells = {}, {}
    for k in [c for c in CELL_KEYS if c in set(d["cell"])] + sorted(set(d["cell"]) - set(CELL_KEYS)):
        g = d[d["cell"] == k].sort_values("idx")
        y_gm, y_none, y_chg, y_cl = (g[c].to_numpy(float) for c in ("y_gm", "y_none", "y_chg", "y_clean"))
        rep = report.report_test(y_gm, y_none, n_boot=n_boot, seed=sd)
        rep = {kk: v for kk, v in rep.items() if kk not in ("p", "p_mid", "ci9833", "ci90", "equivalent_within_0p05", "theta_cp95")}        # Tier 3: no p-value
        cells[k] = dict(n_items=int(len(g)), gm_vs_none=rep, net_difference=rep["delta"], acc_clean=float(np.nanmean(y_cl)), acc_none=float(np.nanmean(y_none)), acc_gm=float(np.nanmean(y_gm)),
                        acc_chg=float(np.nanmean(y_chg)), mean_n_changed=float(g["n_changed"].mean()), mean_n_flag=float(g["n_flag"].mean()),
                        flag_precision=(float(g["n_tp"].sum() / g["n_flag"].sum()) if g["n_flag"].sum() > 0 else None), flag_recall=(float(g["n_tp"].sum() / g["n_changed"].sum()) if g["n_changed"].sum() > 0 else None),
                        edec=edec_mod.edec_cell(k, tuple(g[f"d_{a}"].to_numpy(float) for a in edec_mod.ARMS), tuple(g[f"y_{a}"].to_numpy(float) for a in edec_mod.ARMS), n_boot=n_boot, seed=sd),
                        sign_observed=int(np.sign(rep["b"] - rep["c"])))
        p_cells[k] = dict(b=rep["b"], c=rep["c"], n=rep["n"], net_difference=rep["delta"], ci95=rep["ci95"])
    out = dict(fold=fold, n_cells=len(cells), cells=cells, label="Tier 3, exploratory. No p-value enters a claim; no multiplicity statement (AD.9)", meta=seeds.meta(),
               choice="the four types and two severities were chosen by kind from a package of fifteen types with no recorded rationale: researcher choice (AB.8)")
    if s_c is not None:
        out["epred_suite"] = epred.epred_agreement({k: (v if isinstance(v, dict) else dict(sign=v)) for k, v in s_c.items()}, p_cells)
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
    res = analyze_run(run_dir, n_boot=a.boot)
    (run_dir / "analysis.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf8")
    for k, c in res["cells"].items():
        print(k, "n", c["n_items"], "b", c["gm_vs_none"]["b"], "c", c["gm_vs_none"]["c"], "net", round(c["net_difference"], 3), "ci95", [round(x, 3) for x in c["gm_vs_none"]["ci95"]])
    e = res["epred_suite"]
    print("E-pred (suite block):", f"A {e['A']} of K_eval {e['K_eval']}" if e.get("produced") else e["reason"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
