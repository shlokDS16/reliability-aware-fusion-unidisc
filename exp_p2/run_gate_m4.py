"""M4 (v2 sections 4.3, 7, 11.1): main test on 300 held-out items. GATE-M versus no gate on the image-direction statistic (primary), with the mechanism
controls, the text-direction conditioning arms, the cheap baselines' inputs and the denoise defence arm.

Prerequisites (the runner refuses to start without them; no defaults are invented):
    runs/P2-GATE-M2/threshold.json   from  python -m exp_p2.gate.fit_threshold --run-id P2-GATE-M2
    runs/P2-GATE-M3/family.json      from  python -m exp_p2.gate.headroom --run-id P2-GATE-M3 --endpoint d   (committed before the first test item is scored)

    python -m exp_p2.run_gate_m4 --resume --soft-minutes 12.5 [--limit N] [--tbv auto|on|off] [--run-id P2-GATE-M4]

Per item (75 passes + 6 encodes with a 3-corruption family and patch only, v2 11.1 itemised; +8 B passes, +1 with TbV, per extra token-level sanity condition): conditions = clean,
each family corruption (pixel level, tokenised), the token-level sanity conditions of family PS (SAP AD.4: patch = 8 x 8 block of random codes, swap = 15 percent of positions replaced
by uniform random codes; `--sanity patch,swap`, the default; swap added 2026-10-28 after the red-team finding AB.7), and a denoised copy of the jpeg and noise conditions (encode only,
no gate). Swap is appended AFTER patch, so every earlier condition index (and with it every arm seed) is unchanged; its own corruption stream is `corruptions.TOKEN_RNG_TAG["swap"]`.
  gate input   B (K=8, caption masked) = 8 per gated condition (clean, family, patch) -> 40; cached null D; u = -(B - D); one jitter draw per condition
  TbV-style    1 pass per gated condition if enabled (5)
  image dir.   Lambda^{c+}, Lambda^{c-} = 2 passes; every arm below is a gather
  text dir.    clean x {none, GATE-M} and each family corruption x {none, GATE-M, geo seed 0, changed-code}, x2 captions = 4 + 24
Image-direction arms: none; GATE-M at alpha 0.05 / 0.01 / 0.10; geo (3 seeds) and scattered (3 seeds) gates the size and shape of GATE-M(0.05);
changed-code gate (corrupted conditions); plain-B top-k and s3 top-k of equal size; denoised codes (no gate)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                          # noqa: E402
from exp_p2.scoring import IMG_VOCAB                                                # noqa: E402
from exp_p2.gate import arms, baselines, calibrate as cal, checks, config, corruptions, evidence, folds, pipeline, ps_freeze, runner, scores   # noqa: E402
from exp_p2.run_gate_m3 import load_folds, rung_rng                                  # noqa: E402  (load_folds: default folds.json, or an explicit family-H file that must exist)

RUN_ID = "P2-GATE-M4"
M2_RUN, M3_RUN, M1_RUN = "P2-GATE-M2", "P2-GATE-M3", "P2-GATE-M1"
SANITY_ALL = ("patch", "swap")            # family PS (SAP AD.4); order = condition order, patch first so that its condition index does not change
CONFIG = dict(stage="M4", fold="test", n_items=config.N_TEST, seed=config.SEED_GATE, K=config.K, alphas=list(config.ALPHAS), n_geo_seeds=config.N_GEO_SEEDS,
              denoise_for=list(config.DENOISE_FOR), sanity=list(SANITY_ALL), duty=0.5, spec="research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md sections 4.3, 7, 11.1 M4")


def load_prereqs(runs: Path | None = None, family_run: str = M3_RUN) -> tuple[dict, list[tuple[str, object]], float]:
    """-> (alpha -> Threshold for statistic q, family [(corruption, severity)], eps0). Raises FileNotFoundError with the command to run if missing.
    `family_run` (default M3) names the headroom run whose family.json is read; only family H (hard negatives, `--family-run P2-GATE-H3`) passes another one."""
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    tp, fp = runs / M2_RUN / "threshold.json", runs / family_run / "family.json"
    for p, cmd in ((tp, "python -m exp_p2.gate.fit_threshold --run-id P2-GATE-M2"), (fp, f"python -m exp_p2.gate.headroom --run-id {family_run}")):
        if not p.exists():
            raise FileNotFoundError(f"{p} missing; create it with: {cmd}")
    fam = pipeline.load_json(fp)
    if fam.get("endpoint") != "d":
        raise ValueError(f"{fp} does not record \"endpoint\": \"d\"; it is invalid for the SAP (Addendum 1). Re-run: python -m exp_p2.gate.headroom --run-id {family_run} --endpoint d")
    t = pipeline.load_json(tp)
    thr = {float(k): cal.Threshold.from_json(v) for k, v in t["thresholds"].items()}
    assert len({round(v.eps0, 15) for v in thr.values()}) == 1, "thresholds must share one eps0 (one calibration set)"
    family = [(f["corruption"], f["severity"]) for f in fam["family"]]
    return thr, family, next(iter(thr.values())).eps0


def check_n_against_rule(n: int | None, runs: Path | None = None, family_run: str = M3_RUN) -> int:
    """--n must equal the committed n-rule (family.json n_rule.test_fold: R1 and R3 300, R2 500, NO-GO 300); a forgotten --n 500 under R2 would run a test fold that SAP 4.6 says is too
    small (audit M3). Returns the effective n. The rule is read from `family_run`'s family.json (M3 unless family H names its own headroom run); the check cannot be skipped."""
    fam = pipeline.load_json(Path(runs if runs is not None else common.RUNS) / family_run / "family.json")
    want = int(fam.get("n_rule", {}).get("test_fold", 300))
    eff = n if n is not None else CONFIG["n_items"]
    if eff != want:
        raise ValueError(f"--n {eff} does not match the committed n-rule ({fam.get('n_rule', {}).get('rule')}: test fold {want}); run with --n {want}")
    return eff


def tbv_enabled(mode: str, runs: Path | None = None) -> bool:
    if mode in ("on", "off"):
        return mode == "on"
    p = (Path(runs) if runs is not None else Path(common.RUNS)) / M1_RUN / "tbv_verdict.json"
    return bool(p.exists() and not pipeline.load_json(p).get("copy_suspected", True))


def parse_sanity(text: str) -> tuple[str, ...]:
    """'patch,swap' -> ('patch', 'swap'). Only names of SANITY_ALL, in their fixed order (a different order would change the condition indices and with them the seeds)."""
    names = [t.strip() for t in str(text).split(",") if t.strip()]
    bad = [t for t in names if t not in SANITY_ALL]
    if bad:
        raise ValueError(f"unknown sanity condition(s) {bad}; allowed {SANITY_ALL}")
    if "swap" in names and "patch" not in names:                           # code audit part 1, m-5: swap alone would take patch's condition index and with it a different jitter stream
        raise ValueError("--sanity swap without patch is not allowed: swap's condition index (and its jitter stream) must equal the one of the full run; drop swap or keep patch")
    return tuple(t for t in SANITY_ALL if t in names)


def make_ctx_factory(a, runs: Path | None = None):
    def make_ctx(sc, run):
        runs_ = Path(runs) if runs is not None else Path(common.RUNS)
        thr, family, eps0 = load_prereqs(runs_, getattr(a, "family_run", None) or M3_RUN)
        f = load_folds(lambda c: len(sc.caption_ids(c)), getattr(a, "folds_path", None))
        pipeline.check_fold_tokens(sc, f, run)                                              # exclusions were applied in get_items; this repeats the check for the record
        pipeline.require_frozen(runs_)
        cbp = runs_ / M1_RUN / "codebook.npy"
        checks.l10_once(sc, run)
        grid = int(round(sc.L_I ** 0.5))
        ps_freeze.assert_runtime(grid, max(2, grid // 4))                                   # SAP AB.7 item 2 / A3.3 item 3: token map 32 and patch 8 at run time (code audit part 1, M-2)
        return SimpleNamespace(run=run, dcache=pipeline.dcache_for(), thr=thr, family=family, eps0=eps0, fold=folds.test_items(f, 500), grid=grid,
                               patch=max(2, grid // 4), codebook=(np.load(cbp) if cbp.exists() else None), tbv=tbv_enabled(a.tbv, runs_),
                               denoise_for=tuple(a.denoise_for.split(",")) if a.denoise_for else (),
                               sanity=parse_sanity(getattr(a, "sanity", "patch")))     # main() always sets --sanity (default patch,swap); a bare namespace keeps the pre-swap behaviour
    return make_ctx


def build_conditions(sc, it, pil, clean, ctx) -> list[dict]:
    from exp_p2.run_gate_m3 import donor_for
    gid = it["gid"]
    conds = [dict(name="clean", kind="clean", codes=clean, pix=np.asarray(pil), corr=None)]
    donor = None
    for corr, sev in ctx.family:
        r = list(config.LADDERS[corr]).index(sev)
        if corr == "splice" and donor is None:
            donor = donor_for(SimpleNamespace(fold=ctx.fold), sc, it)
        img = corruptions.apply_pixel(corr, sev, pil, rung_rng(gid, corr, r), donor if corr == "splice" else None)
        key = corruptions.corruption_key(corr, sev)
        conds.append(dict(name=key, kind="pixel", codes=sc.encode(img), pix=np.asarray(img), corr=corr))
        if corr in ctx.denoise_for:
            conds.append(dict(name=key + "_dn", kind="denoise", src=key, codes=sc.encode(corruptions.denoise(img)), pix=None, corr=corr))
    for name in getattr(ctx, "sanity", ("patch",)):
        tc = corruptions.apply_token(name, clean, corruptions.token_rng(config.SEED_GATE, gid, name), grid=ctx.grid, patch=ctx.patch, swap_frac=config.SWAP_FRAC, vocab=IMG_VOCAB)
        conds.append(dict(name=name, kind="token", codes=tc, pix=None, corr=name))
    return conds


def process(sc, it, ctx):
    gid, K = it["gid"], config.K
    rows0 = getattr(sc, "rows", None)
    cap_tok, neg_tok = sc.caption_ids(it["caption"]), sc.caption_ids(it["neg_caption"])
    pil, clean = pipeline.prep_image(sc, it["image_id"])
    conds = build_conditions(sc, it, pil, clean, ctx)
    lam_pos, lam_neg = pipeline.caption_lambdas(sc, cap_tok, neg_tok, clean)                          # 2 passes
    groups = pipeline.item_groups(sc, gid, K)
    a0 = config.ALPHA_PRIMARY
    row, arrays = dict(gid=gid, image_id=it["image_id"], caption=it["caption"], neg_caption=it["neg_caption"], n_tok=len(cap_tok), n_tok_neg=len(neg_tok), conds={}), {}
    G_of: dict[str, np.ndarray] = {}
    for ci, c in enumerate(conds):
        name, codes = c["name"], c["codes"]
        delta = pipeline.image_delta(lam_pos, lam_neg, codes)
        z = np.zeros(sc.L_I, bool) if c["kind"] == "clean" else arms.changed_code_gate(clean, codes)
        cr = dict(kind=c["kind"], n_changed=int(z.sum()), img={}, txt={}, gate={})
        arrays[f"{name}_codes"], arrays[f"{name}_z"], arrays[f"{name}_delta"] = codes.astype(np.int16), z, delta
        if c["kind"] == "denoise":
            cr["img"]["denoised"] = pipeline.compact(evidence.evidence_from_delta(delta))
            row["conds"][name] = cr
            continue
        gs = pipeline.gate_scores(sc, cap_tok, codes, groups, ctx.dcache, K)                           # 8 passes (+ cached null)
        uj = cal.jitter(gs["u"], ctx.eps0, arms.arm_rng(config.SEED_GATE, gid, ci, arms.ARM_TAG["jitter"], 0))
        flags = {al: uj > t.tau for al, t in ctx.thr.items()}
        G = flags[a0]
        G_of[name] = G
        arrays.update({f"{name}_B": gs["B"], f"{name}_D": gs["D"].astype(np.float32), f"{name}_s3": gs["s3"], f"{name}_tex": baselines.patch_texture(c["pix"], ctx.grid).astype(np.float32),
                       f"{name}_nbr": baselines.neighbour_codebook_distance(codes, ctx.codebook, ctx.grid).astype(np.float32)})
        for al, f in flags.items():
            arrays[f"{name}_flag{al:g}"] = f
            cr["gate"][f"{al:g}"] = dict(n_flag=int(f.sum()), n_tp=int((f & z).sum()), n_corrupted=int(z.sum()), n_fp_on_clean_tokens=int((f & ~z).sum()))
        if ctx.tbv:                                                                                     # 1 pass
            tb = scores.tbv_score_raw_logits(sc, sc.build(cap_tok, codes))
            arrays[f"{name}_tbv"] = tb
            cr["tbv"] = baselines.copy_through_stat(tb)
        k = int(G.sum())
        arm_G = {"none": arms.no_gate(sc.L_I)}
        for al, f in flags.items():
            arm_G[f"gate{al:g}"] = f
        for r in range(config.N_GEO_SEEDS):
            arm_G[f"geo{r}"] = arms.geometry_matched_gate(G, ctx.grid, arms.arm_rng(config.SEED_GATE, gid, ci, arms.ARM_TAG["geo"], r))
            arm_G[f"scat{r}"] = arms.scattered_gate(k, sc.L_I, arms.arm_rng(config.SEED_GATE, gid, ci, arms.ARM_TAG["scattered"], r))
        arm_G["topkB"], arm_G["topks3"] = arms.topk_gate(-gs["B"].astype(np.float64), k), arms.topk_gate(gs["s3"], k)
        if c["kind"] != "clean":
            arm_G["chg"] = z
        cr["img"] = {an: pipeline.compact(evidence.arm_summary(delta, g)) for an, g in arm_G.items()}
        if c["kind"] in ("clean", "pixel"):                                                             # text direction: clean + family only
            names = ["none", "gate"] + ([] if c["kind"] == "clean" else ["geo0", "chg"])
            gate_list = [None, G] + ([] if c["kind"] == "clean" else [arm_G["geo0"], z])
            cr["txt"] = dict(zip(names, pipeline.text_direction(sc, cap_tok, neg_tok, codes, gate_list, ctx.dcache)))
        row["conds"][name] = cr
    if isinstance(rows0, int):
        row["n_rows"] = int(sc.rows) - rows0
    return row, arrays


def main(argv=None):
    ap = runner.base_parser(RUN_ID, CONFIG["n_items"])
    ap.add_argument("--tbv", choices=["auto", "on", "off"], default="auto", help="TbV-score (non-finetuned) pass, raw logits; auto = on only if M1 found no copy-through (U7)")
    ap.add_argument("--denoise-for", default=",".join(config.DENOISE_FOR), help="comma list of family corruptions that get a denoised copy ('' = none)")
    ap.add_argument("--sanity", default=",".join(SANITY_ALL), help="token-level sanity conditions of family PS (SAP AD.4: both are always tested, m = 2); dropping one makes its PS cell 'not run', p = 1")
    ap.add_argument("--folds-path", default=None, help="family H only: folds file to take the test items from (default: runs/P2-GATE-FOLDS/folds.json); must exist, is never built")
    ap.add_argument("--family-run", default=M3_RUN, help="family H only: headroom run whose family.json gives the corruption family and the n-rule (default P2-GATE-M3); the n check is never skipped")
    a = ap.parse_args(argv)
    try:                                                                  # all prerequisites are checked BEFORE the model is touched
        load_prereqs(None, a.family_run)
        pipeline.require_frozen()
        check_n_against_rule(a.n, None, a.family_run)
        if a.folds_path and not Path(a.folds_path).exists():
            raise FileNotFoundError(f"--folds-path {a.folds_path} does not exist")
        sanity = parse_sanity(a.sanity)
        ps_doc = None
        if sanity:                                                        # ps_frozen.json is written and committed before the first M4 item (AD.4, AD.12 step 2, A3.3 item 1, AB.8)
            ps_doc = ps_freeze.check(Path(common.RUNS))
            dn = tuple(t for t in a.denoise_for.split(",") if t)
            if dn != tuple(ps_doc["params"]["denoise_for"]):
                raise ValueError(f"--denoise-for {dn} differs from the frozen {tuple(ps_doc['params']['denoise_for'])}: it fixes the condition indices and with them the PS jitter streams (ps_frozen.json)")
    except (FileNotFoundError, ValueError, ps_freeze.PsFrozenError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    cfg = dict(CONFIG, n_items=a.n, duty=a.duty, mem_frac=a.mem_frac, tbv=a.tbv, denoise_for=a.denoise_for.split(",") if a.denoise_for else [], sanity=list(sanity),
               ps_params=ps_freeze.params(), ps_frozen_sha256=(ps_freeze.sha256(Path(common.RUNS)) if ps_doc else None), ps_frozen_code_commit=(ps_doc or {}).get("code_commit"))
    if a.folds_path or a.family_run != M3_RUN:                            # recorded only for family H, so the config of every existing run id is unchanged
        import hashlib
        cfg.update(folds_path=a.folds_path, folds_sha256=(hashlib.sha256(Path(a.folds_path).read_bytes()).hexdigest() if a.folds_path else None), family_run=a.family_run)

    def load():
        from exp_p2.scoring import UniScorer
        return runner.Counting(UniScorer(common.load_net()))

    def selfcheck(sc, items):
        return sc.selfcheck(common.load_image(items[0]["image_id"]), items[0]["caption"])

    def get_items(sc, run):
        f = load_folds(lambda c: len(sc.caption_ids(c)), a.folds_path)
        rep = pipeline.check_fold_tokens(sc, f, run)                                        # SAP A2.1: out-of-range captions are excluded, counted, not replaced
        items = folds.test_items(f, a.n if a.n and a.n > len(f["test"]) else None)         # base 300; the extension (items 301-500) only if --n asks for it (SAP R2)
        if a.n and a.n > len(items):
            raise RuntimeError(f"folds.json holds {len(items)} test items, --n {a.n} asked for more")
        items = items[:a.n] if a.n else items
        bad = set(rep["excluded"].get("test", [])) | set(rep["excluded"].get("test_ext", []))
        return [it for it in items if it["idx"] not in bad]

    return runner.run_items(run_id=a.run_id, cfg=cfg, load=load, get_items=get_items, process=process, make_ctx=make_ctx_factory(a),
                            soft_minutes=a.soft_minutes, duty=a.duty, limit=a.limit, guards=runner.guards_from_args(a), mem_frac=a.mem_frac, selfcheck=selfcheck, watchdog_factory=runner.default_watchdog, allow_dirty=a.allow_dirty)


if __name__ == "__main__":
    sys.exit(main())
