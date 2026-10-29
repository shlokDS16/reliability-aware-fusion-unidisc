"""Family H strata, identity checks and outcome label (SAP addendum A5: A5.7, A5.8, A5.9). CPU only; reads runs/P2-GATE-H4/items.jsonl, analysis.json and runs/P2-GATE-H3/family.json.

    python -m exp_p2.gate.h_strata --run-id P2-GATE-H4 --folds-path runs/P2-HARDNEG-ITEMS/folds_hardneg.json [--family-run P2-GATE-H3]

Not run on H4 data before H4 is complete or the freeze arrives (A5.8, SAP 8.2); analysis_m4 is run first and committed.
Descriptive and sensitivity only (nothing here is a family): for every corruption of H3's family
  * length strata: LM = replace_obj, replace_att, replace_rel, swap_obj, swap_att (negative about as long as the positive); LA = add_obj, add_att (negative longer by 2.6 to 4 tokens, A5.7);
  * per subset (about 43 items each);
  each with b, c, n, net difference (b - c) / n of GATE-M (gate0.05) minus none, its 95 percent percentile-bootstrap CI and the exact McNemar p, UNADJUSTED and labelled exploratory;
  * the stratified bootstrap (items resampled within the seven subsets) of the net difference, 95 and 90 percent CIs: a sensitivity to the unstratified CIs of analysis_m4;
  * decision headroom on H4: clean-versus-corrupted none-arm flips F-, F+ and the exact McNemar p of (F-, F+) (descriptive).
Identity checks (A5.8) raise IdentityError. `h_label` maps analysis.json and H3's family.json to the label of A5.9 and carries the length rule (A5.7, binding wording)."""
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
from exp_p2.gate import analysis_m4, config, seeds, stats                   # noqa: E402

SEED_SPAWN_KEY = (33,)       # A5.8: tier3_fusion uses (32,); seeds.py is not edited; one child per corruption of config.REALISTIC, used in a fixed order
LM_SUBSETS = ("replace_obj", "replace_att", "replace_rel", "swap_obj", "swap_att")
LA_SUBSETS = ("add_obj", "add_att")
SUBSETS = LM_SUBSETS + LA_SUBSETS
H4_GID_RANGE = (7000, 7299)
Z_CAL_NOTE = 2.13
A0 = analysis_m4.A0         # "gate0.05"


class IdentityError(AssertionError):
    """An A5.8 identity check failed: the H4 run does not match the committed items file."""


def _child(corr: str) -> np.random.Generator:
    kids = np.random.SeedSequence(seeds.ROOT_SEED, spawn_key=SEED_SPAWN_KEY).spawn(len(config.REALISTIC))
    return np.random.default_rng(kids[list(config.REALISTIC).index(corr)])


def sha256_pair(path: Path) -> tuple[str, str]:
    b = Path(path).read_bytes()
    return hashlib.sha256(b).hexdigest(), hashlib.sha256(b.replace(b"\r\n", b"\n")).hexdigest()


# ------------------------------------------------------------------------------------------------ identity checks (A5.8)
def identity_checks(rows: list[dict], test_items: list[dict], *, run_dir: Path | None = None, folds_path: Path | None = None, m4_items: list[dict] | None = None) -> dict:
    """Every H4 row's idx, gid (7000-7299), image_id (and caption, neg_caption where the row stores them) equal the `test` list of folds_hardneg.json; caption differs from neg_caption in
    the items file; no image id shared with the M4 items (`m4_items`, None = not available, recorded); the run's config.json `folds_sha256` equals the committed file's hash."""
    by_idx = {int(it["idx"]): it for it in test_items}
    bad = []
    for r in rows:
        it = by_idx.get(int(r["idx"]))
        if it is None or int(r["gid"]) != int(it["gid"]) or int(r["image_id"]) != int(it["image_id"]) or not (H4_GID_RANGE[0] <= int(r["gid"]) <= H4_GID_RANGE[1]):
            bad.append(int(r["idx"]))
            continue
        if ("caption" in r and r["caption"] != it["caption"]) or ("neg_caption" in r and r["neg_caption"] != it["neg_caption"]):
            bad.append(int(r["idx"]))
    if bad:
        raise IdentityError(f"rows {sorted(set(bad))[:10]} differ from the committed H4 items (idx, gid, image_id or captions)")
    same = [it["idx"] for it in test_items if it["caption"] == it["neg_caption"]]
    if same:
        raise IdentityError(f"items {same[:10]}: caption equals neg_caption in the items file")
    out = dict(n_rows=len(rows), n_items_file=len(test_items), caption_differs_from_neg=True)
    if m4_items is None:
        out["m4_image_overlap"] = dict(checked=False, reason="M4 items not available")
    else:
        shared = {int(r["image_id"]) for r in m4_items} & {int(it["image_id"]) for it in test_items}
        if shared:
            raise IdentityError(f"{len(shared)} H4 image ids are also M4 test images, e.g. {sorted(shared)[:5]}")
        out["m4_image_overlap"] = dict(checked=True, n_shared=0)
    if run_dir is not None and folds_path is not None:
        cfgp = Path(run_dir) / "config.json"
        if not cfgp.exists():
            raise IdentityError(f"{cfgp} missing")
        cfg_hash = json.loads(cfgp.read_text(encoding="utf8")).get("folds_sha256")
        raw, lf = sha256_pair(folds_path)
        if cfg_hash not in (raw, lf):
            raise IdentityError(f"config.json folds_sha256 {cfg_hash} differs from the committed file ({lf})")
        out["folds_sha256"] = dict(config=cfg_hash, file_lf=lf, match=True)
    return out


# ------------------------------------------------------------------------------------------------ strata
def _boot_ci(d: np.ndarray, rng: np.random.Generator, n_boot: int, levels=(95.0,)) -> dict:
    if d.size < 2:
        return {f"ci{int(l)}": [float("nan")] * 2 for l in levels}
    m = d[rng.integers(0, d.size, size=(n_boot, d.size))].mean(axis=1)
    return {f"ci{int(l)}": [float(np.percentile(m, (100 - l) / 2)), float(np.percentile(m, 100 - (100 - l) / 2))] for l in levels}


def net_test(yg: np.ndarray, yn: np.ndarray, rng: np.random.Generator, n_boot: int) -> dict:
    """GATE-M minus none on the items with both finite: b, c, n, net (b - c) / n, 95 percent percentile CI, exact two-sided McNemar p (unadjusted)."""
    ok = np.isfinite(yg) & np.isfinite(yn)
    mc = stats.mcnemar_exact(yg[ok], yn[ok])
    d = (yg - yn)[ok]
    n = int(ok.sum())
    return dict(b=mc["b"], c=mc["c"], n_d=mc["n_discordant"], n=n, net=float((mc["b"] - mc["c"]) / n) if n else float("nan"), p_unadjusted=mc["p"], **_boot_ci(d, rng, n_boot), exploratory=True)


def stratified_boot(d: np.ndarray, labels: np.ndarray, rng: np.random.Generator, n_boot: int) -> dict:
    """Net difference with items resampled within the subsets (the design's strata); 95 and 90 percent percentile CIs."""
    n = int(d.size)
    tot = np.zeros(n_boot)
    for s in SUBSETS:
        x = d[labels == s]
        if x.size:
            tot += x[rng.integers(0, x.size, size=(n_boot, x.size))].sum(axis=1)
    m = tot / n if n else np.full(n_boot, np.nan)
    return dict(net=float(d.mean()) if n else float("nan"), n=n, ci95=[float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))], ci90=[float(np.percentile(m, 5)), float(np.percentile(m, 95))], sensitivity=True)


def strata_for(rows: list[dict], test_items: list[dict], family, n_boot: int = 10000) -> dict:
    """Per corruption of `family` (list of family.json entries or keys): length strata, subsets, stratified bootstrap and the decision-headroom flips."""
    sub_of = {int(it["idx"]): it["subset"] for it in test_items}
    labels = np.array([sub_of[int(r["idx"])] for r in rows])
    yc = analysis_m4._arm(rows, "clean", "none", "y")
    out = {}
    for corr, k in analysis_m4._family_map(family).items():
        rng = _child(corr)
        yg, yn = analysis_m4._arm(rows, k, A0, "y"), analysis_m4._arm(rows, k, "none", "y")
        ok = np.isfinite(yg) & np.isfinite(yn)
        lm = np.isin(labels, LM_SUBSETS)
        la = np.isin(labels, LA_SUBSETS)
        ent = dict(key=k, all=net_test(yg, yn, rng, n_boot), stratified_bootstrap=stratified_boot((yg - yn)[ok], labels[ok], rng, n_boot),
                   LM=net_test(yg[lm], yn[lm], rng, n_boot), LA=net_test(yg[la], yn[la], rng, n_boot),
                   per_subset={s: net_test(yg[labels == s], yn[labels == s], rng, n_boot) for s in SUBSETS})
        v = np.isfinite(yc) & np.isfinite(yn)
        c1, n1 = yc[v] > 0.5, yn[v] > 0.5
        fm, fp = int((c1 & ~n1).sum()), int((~c1 & n1).sum())
        ent["decision_headroom"] = dict(n_valid=int(v.sum()), F_minus=fm, F_plus=fp, restore_clean_bound_p=stats.mcnemar_exact(np.array([1] * fm + [0] * fp, float), np.array([0] * fm + [1] * fp, float))["p"], descriptive=True)
        out[corr] = ent
    return out


# ------------------------------------------------------------------------------------------------ label (A5.9) and length rule (A5.7)
def length_rule(strata: dict | None, analysis: dict | None) -> dict:
    """Binding wording: if an H rejection with b > c is reported and the LM estimate of that corruption has the opposite sign with a 95 percent CI excluding 0, every sentence about that
    rejection adds 'not present on the length-matched subsets'."""
    out = {}
    if not strata or not analysis:
        return out
    for c, e in strata.items():
        pc = analysis["primary"]["per_corruption"].get(c, {})
        rej = bool(pc.get("gate_better"))
        lm = e["LM"]
        opposite = bool(rej and lm["net"] < 0 and lm["ci95"][1] < 0)
        out[c] = dict(rejected_b_gt_c=rej, lm_net=lm["net"], lm_ci95=lm["ci95"], add_clause=opposite, clause="not present on the length-matched subsets" if opposite else None)
    return out


def h_label(analysis: dict | None, h3_family: dict) -> dict:
    """The label of A5.9, mechanically. `analysis` = analysis_m4's analysis.json of P2-GATE-H4 (None when H4 was not run), `h3_family` = runs/P2-GATE-H3/family.json."""
    nr = h3_family.get("n_rule", {})
    status = nr.get("time_rule", {}).get("status")
    if status == "not run (pilot incomplete)":
        return dict(label=None, status="not run (pilot incomplete)", reasons=["deviations box only"])
    if nr.get("rule") == "NO-GO" and not h3_family.get("family"):
        return dict(label="H-NOGO", status="H3 rule: no corruption tested", G_star=nr.get("G_star"), reasons=[e.get("reason") for e in h3_family.get("excluded", [])])
    if analysis is None or int(nr.get("test_fold", 0)) <= 0:
        return dict(label=None, status="not run (cut by time)" if status == "cut by time" else "not run", reasons=["deviations box only"])
    per = analysis["primary"]["per_corruption"]
    tested = [c for c in config.REALISTIC if per[c].get("tested")]
    pos = [c for c in tested if per[c].get("gate_better")]
    harm = [c for c in tested if per[c]["p_holm"] < 0.05 and per[c]["c"] > per[c]["b"]]
    sm = analysis.get("s_m", {}).get("per_corruption", {})
    split = {c: ("M" if sm.get(c, {}).get("rejected") else "G") for c in pos}
    cal = bool(analysis.get("calibration", {}).get("fap_check", {}).get("K4_violation_evidence"))
    if pos and harm:
        lab = "H-MIXED"
    elif pos:
        lab = "H-POS-M" if all(v == "M" for v in split.values()) else "H-POS-G"
    elif harm:
        lab = "H-HARM"
    elif analysis.get("outcome", {}).get("label") == "negative":
        lab = "H-NEG"
    else:
        lab = "H-INC"
    return dict(label=lab, status="run", positive=pos, harm=harm, positive_split=split, h_cal_clause_required=bool(cal and lab.startswith("H-POS")), z_cal_critical=Z_CAL_NOTE)


# ------------------------------------------------------------------------------------------------ main
def run(run_dir: Path, folds_path: Path, family_run_dir: Path, *, analysis_path: Path | None = None, m4_items_path: Path | None = None, n_boot: int = 10000) -> dict:
    run_dir, folds_path = Path(run_dir), Path(folds_path)
    fam = json.loads((Path(family_run_dir) / "family.json").read_text(encoding="utf8"))
    test_items = json.loads(folds_path.read_text(encoding="utf8"))["test"]
    rows, n_dup = analysis_m4.load_items(run_dir)
    m4_items = common.read_jsonl(m4_items_path) if m4_items_path is not None and Path(m4_items_path).exists() else None
    ident = identity_checks(rows, test_items, run_dir=run_dir, folds_path=folds_path, m4_items=m4_items)
    ap = Path(analysis_path) if analysis_path is not None else run_dir / "analysis.json"
    analysis = json.loads(ap.read_text(encoding="utf8")) if ap.exists() else None
    strata = strata_for(rows, test_items, fam["family"], n_boot)
    return dict(meta=dict(seeds.meta(), h_strata_spawn_key=list(SEED_SPAWN_KEY), n_boot=n_boot, spec="SAP addendum A5, A5.7 to A5.9"), n_items=len(rows), n_duplicates_removed=n_dup, identity=ident,
                family=[f["key"] for f in fam["family"]], strata=strata, length_rule=length_rule(strata, analysis), label=h_label(analysis, fam))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-GATE-H4")
    ap.add_argument("--family-run", default="P2-GATE-H3")
    ap.add_argument("--folds-path", default=str(Path(common.RUNS) / "P2-HARDNEG-ITEMS" / "folds_hardneg.json"))
    ap.add_argument("--boot", type=int, default=10000)
    a = ap.parse_args(argv)
    runs = Path(common.RUNS)
    try:
        res = run(runs / a.run_id, Path(a.folds_path), runs / a.family_run, m4_items_path=runs / "P2-GATE-M4" / "items.jsonl", n_boot=a.boot)
    except (IdentityError, FileNotFoundError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    (runs / a.run_id / "h_strata.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf8")
    print(json.dumps(dict(label=res["label"], n_items=res["n_items"]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
