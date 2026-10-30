"""Omni family R runner (SAP AD.7 as amended by AB.5): the gatekept replication of GATE-M versus no gate on Omni-Diffusion 8B (4-bit), image direction only. GPU: only with ANONYMIZED's go-ahead.

Three stages, three run ids, each resumable, each through `runner.run_items` (hold files, clean-tree rule, memory cap, per-item guards, watchdog), each refusing to start without its prerequisites:

    <omni python> -m exp_p2.run_gate_omni_r --stage cal  --resume --soft-minutes 20     # run P2-OMNI-R-CAL : 100 clean calibration items: B, D, codes  (8 passes + cached null per item)
    <omni python> -m exp_p2.gate.analysis_omni fit --run-id P2-OMNI-R-CAL                  # CPU: CRC threshold at alpha 0.05 on this 4-bit model -> threshold.json (write-once)
    <omni python> -m exp_p2.run_gate_omni_r --stage pos  --resume --soft-minutes 20     # run P2-OMNI-R-POS : first 50 R items, code-level patch, plain-B (8 passes per item)
    <omni python> -m exp_p2.gate.analysis_omni pos --run-id P2-OMNI-R-POS                  # CPU: AUROC lower bound > 0.5 -> pos_control.json; failing = 'pipeline defect: not run'
    <omni python> -m exp_p2.run_gate_omni_r --stage test --resume --soft-minutes 20     # run P2-OMNI-R-TEST: positions 301..300+n_R of the ordered test list, arms none and GATE-M(0.05)
    <omni python> -m exp_p2.gate.analysis_omni r --run-id P2-OMNI-R-TEST                   # CPU: omni_r -> analysis.json

Prerequisites (checked before the model is touched; exit 2 with the command to run):
    cal : runs/P2-OMNI-TIMING/omni_gate.json with go = true (from `analysis_omni gate`), and the gate-auditor's adapter_signature.json bound to selfcheck.json (AB.5 item 1);
    pos : cal's threshold.json;
    test: threshold.json, pos_control.json with passed = true, runs/P2-GATE-M4/analysis.json (P+ non-empty), runs/P2-GATE-M3/family.json, and the n_R of omni_gate.json (--n, if given, must equal it).

Items (AB.5 item 3): R uses positions 301 to 300 + n_R of the ordered test list (folds.test_items(f, 500)), disjoint from the P test fold when the n-rule is R1; own calibration uses the first 100
calibration items; the caption token rule 5-32 is applied with the OMNI tokenizer to c+ and c-, excluded and counted (omni_token_exclusions.json), never replaced.
Pixel corruptions: by default applied to the 512 px image with the P-run seeds (so Omni sees the very same corrupted pixels as UniDisc) and then tokenised at 256 px (--corrupt-at 512);
--corrupt-at 256 applies the same parameters at the model's native resolution. The choice is recorded in the run config; see the report (ambiguity A1)."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                                 # noqa: E402
from exp_p2.gate import arms, calibrate as cal, config, corruptions, evidence, folds, pipeline, runner      # noqa: E402
from exp_p2.omni import build                                                             # noqa: E402
from exp_p2.omni.layout import OMNI_N_CODES                                               # noqa: E402
from exp_p2.run_gate_m3 import rung_rng, donor_for                                        # noqa: E402

TIMING_RUN, M3_RUN, M4_RUN = "P2-OMNI-TIMING", "P2-GATE-M3", "P2-GATE-M4"
CAL_RUN, POS_RUN, TEST_RUN = "P2-OMNI-R-CAL", "P2-OMNI-R-POS", "P2-OMNI-R-TEST"
DCACHE_RUN = "P2-OMNI-DCACHE"                       # the nulls of THIS model; never share them with the UniDisc cache
N_CAL, N_POS = 100, 50
A0 = f"gate{config.ALPHA_PRIMARY:g}"
STAGE_DEFAULTS = {"cal": (CAL_RUN, N_CAL), "pos": (POS_RUN, N_POS), "test": (TEST_RUN, 150)}
CONFIG = dict(spec="research/paper2/prereg/SAP-GATE-2026-10-28.md AD.7, AB.5; research/paper2/method/IMPL-C-OMNI-2026-10-28.md", K=config.K, seed=config.SEED_GATE, alpha=config.ALPHA_PRIMARY,
              duty=0.5, statistic=config.STAT_NAME, model="Omni-Diffusion 8B NF4 (bf16 compute)")


# ------------------------------------------------------------------------------------------------ prerequisites
def _sha256(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _need(p: Path, cmd: str) -> Path:
    if not Path(p).exists():
        raise FileNotFoundError(f"{p} missing; create it with: {cmd}")
    return Path(p)


def load_gate(runs: Path) -> dict:
    g = pipeline.load_json(_need(runs / TIMING_RUN / "omni_gate.json", "python -m exp_p2.gate.analysis_omni gate --n-plus K --time-left-h H"))
    if not g.get("go"):
        raise ValueError(f"{runs / TIMING_RUN / 'omni_gate.json'} says {g.get('status')}: family R is not run (AD.7: no substitute model, no shrinking below n = 120)")
    return g


def require_signature(runs: Path) -> dict:
    """AB.5 item 1: no Omni item enters R before the gate-auditor's signature on the adapter checks, and the signature must name the self-check file it was given."""
    tdir = runs / TIMING_RUN
    sig = pipeline.load_json(_need(tdir / "adapter_signature.json", "the gate-auditor runs/audits the adapter checks and writes it (signed_by, verdict, selfcheck_sha256)"))
    if sig.get("signed_by") != "gate-auditor" or sig.get("verdict") != "PASS":
        raise ValueError(f"{tdir / 'adapter_signature.json'} is not a PASS signed by the gate-auditor")
    if sig.get("selfcheck_sha256") != _sha256(_need(tdir / "selfcheck.json", "run_omni_timing")):
        raise ValueError("adapter_signature.json does not match the current selfcheck.json (hash differs)")
    from exp_p2.gate import analysis_omni
    if not analysis_omni.selfcheck_ok(json.loads((tdir / "selfcheck.json").read_text(encoding="utf8"))):                    # audit part 3, m-1 / M-2: a failed or partial self-check stops every later stage
        raise ValueError("selfcheck.json does not record a passing self-check with A1..A7 all present and ok: no Omni stage runs")
    return sig


def load_threshold(runs: Path):
    t = pipeline.load_json(_need(runs / CAL_RUN / "threshold.json", "python -m exp_p2.gate.analysis_omni fit --run-id P2-OMNI-R-CAL"))
    return cal.Threshold.from_json(t["thresholds"][f"{config.ALPHA_PRIMARY:g}"]), t["thresholds"][f"{config.ALPHA_PRIMARY:g}"]["eps0"]


def load_pos(runs: Path) -> dict:
    p = pipeline.load_json(_need(runs / POS_RUN / "pos_control.json", "python -m exp_p2.gate.analysis_omni pos --run-id P2-OMNI-R-POS"))
    if not p.get("passed"):
        raise ValueError("positive control failed (AB.5 item 2): R is 'pipeline defect: not run'; no R item is scored")
    return p


def load_family_plus(runs: Path) -> tuple[list[tuple[str, object]], dict]:
    """-> ([(corruption, severity)] for c in P+, family.json). P+ from the M4 analysis.json via analysis_omni.p_plus."""
    from exp_p2.gate import analysis_omni
    P = pipeline.load_json(_need(runs / M4_RUN / "analysis.json", "python -m exp_p2.gate.analysis_m4 --run-id P2-GATE-M4"))
    fam = pipeline.load_json(_need(runs / M3_RUN / "family.json", "python -m exp_p2.gate.headroom --run-id P2-GATE-M3 --endpoint d"))
    plus = analysis_omni.p_plus(P)
    if not plus:
        raise ValueError("P+ is empty: family R is not run (AD.7)")
    chosen = [(f["corruption"], f["severity"]) for f in fam["family"] if f["corruption"] in plus]
    if len(chosen) != len(plus):
        raise ValueError(f"P+ {plus} has a corruption without an operating point in family.json: inconsistent inputs")
    return chosen, fam


def check_prereqs(stage: str, runs: Path | None = None, n: int | None = None) -> dict:
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    out: dict = {}
    if stage == "cal":
        out["gate"] = load_gate(runs)
        out["signature"] = require_signature(runs)
    elif stage == "pos":
        require_signature(runs)
        load_threshold(runs)
        out["gate"] = load_gate(runs)
    elif stage == "test":
        require_signature(runs)
        out["gate"] = load_gate(runs)
        out["threshold"], out["eps0"] = load_threshold(runs)
        out["pos"] = load_pos(runs)
        out["family"], out["family_json"] = load_family_plus(runs)
        want = int(out["gate"]["n_R"])
        if n is not None and n != want:
            raise ValueError(f"--n {n} does not match the n_R of omni_gate.json ({want})")
        out["n_R"] = want
    else:
        raise ValueError(stage)
    return out


def n_rule_name(fam: dict) -> str:
    r = fam.get("n_rule", "R1")
    return r.get("rule", "R1") if isinstance(r, dict) else str(r)


# ------------------------------------------------------------------------------------------------ items
def load_folds_frozen() -> dict:
    p = folds.folds_path()
    if not p.exists():
        raise FileNotFoundError(f"{p} missing (the frozen folds); R does not build folds")
    return json.loads(p.read_text(encoding="utf8"))


def get_items(stage: str, sc, run: Path, n_R: int | None = None) -> list[dict]:
    f = load_folds_frozen()
    test = folds.test_items(f, 500)
    if stage == "cal":
        raw, need_neg = f["cal"][:N_CAL], False
    elif stage == "pos":
        raw, need_neg = test[300:300 + N_POS], True
    else:
        raw, need_neg = test[300:300 + int(n_R)], True
    kept, rep = build.omni_token_filter(sc, raw, need_neg=need_neg)
    build.write_exclusions(run, rep)
    return kept


# ------------------------------------------------------------------------------------------------ per-item functions
def process_cal(sc, it, ctx):
    gid = it["gid"]
    cap_tok = sc.caption_ids(it["caption"])
    rows0 = getattr(sc, "rows", None)
    pil, codes = pipeline.prep_image(sc, it["image_id"])
    gs = pipeline.gate_scores(sc, cap_tok, codes, pipeline.item_groups(sc, gid, config.K), ctx.dcache, config.K)               # 8 passes + the cached null
    row = dict(gid=gid, image_id=it["image_id"], caption=it["caption"], n_tok=len(cap_tok))
    if isinstance(rows0, int):
        row["n_rows"] = int(sc.rows) - rows0
    return row, dict(codes=codes.astype(np.int16), B=gs["B"], D=gs["D"].astype(np.float32), s3=gs["s3"])


def process_pos(sc, it, ctx):
    """Code-level patch (as probe 2 and the PS family): a patch x patch block of the token map replaced by uniform random codes from the 8192 codebook; no re-encoding. plain-B only."""
    gid = it["gid"]
    cap_tok = sc.caption_ids(it["caption"])
    rows0 = getattr(sc, "rows", None)
    pil, clean = pipeline.prep_image(sc, it["image_id"])
    patched = corruptions.apply_token("patch", clean, np.random.default_rng([config.SEED_GATE, gid, 190]), grid=ctx.grid, patch=ctx.patch, swap_frac=config.SWAP_FRAC, vocab=OMNI_N_CODES)
    z = arms.changed_code_gate(clean, patched)
    gs = pipeline.gate_scores(sc, cap_tok, patched, pipeline.item_groups(sc, gid, config.K), ctx.dcache, config.K)
    row = dict(gid=gid, image_id=it["image_id"], n_tok=len(cap_tok), n_changed=int(z.sum()))
    if isinstance(rows0, int):
        row["n_rows"] = int(sc.rows) - rows0
    return row, dict(codes=clean.astype(np.int16), codes_patched=patched.astype(np.int16), z=z, B=gs["B"], D=gs["D"].astype(np.float32))


def build_conditions(sc, it, pil512, ctx) -> list[dict]:
    from PIL import Image
    base = pil512 if ctx.corrupt_at == 512 else pil512.resize((ctx.corrupt_at, ctx.corrupt_at), Image.BICUBIC)
    clean = sc.encode(base)
    conds = [dict(name="clean", kind="clean", codes=clean, corr=None)]
    donor = None
    for corr, sev in ctx.family:
        r = list(config.LADDERS[corr]).index(sev)
        if corr == "splice" and donor is None:
            donor = donor_for(SimpleNamespace(fold=ctx.fold), sc, it)
            if ctx.corrupt_at != 512:
                donor = donor.resize((ctx.corrupt_at, ctx.corrupt_at), Image.BICUBIC)
        img = corruptions.apply_pixel(corr, sev, base, rung_rng(it["gid"], corr, r), donor if corr == "splice" else None)
        conds.append(dict(name=corruptions.corruption_key(corr, sev), kind="pixel", codes=sc.encode(img), corr=corr))
    return conds


def process_test(sc, it, ctx):
    """Arms: none and GATE-M(alpha 0.05, own Omni threshold), image direction. Per item: encodes (CPU) + 2 lambda passes + 8 B passes per condition + cached nulls."""
    gid, K = it["gid"], config.K
    rows0 = getattr(sc, "rows", None)
    cap_tok, neg_tok = sc.caption_ids(it["caption"]), sc.caption_ids(it["neg_caption"])
    pil512 = sc.preprocess(common.load_image(it["image_id"]))
    conds = build_conditions(sc, it, pil512, ctx)
    clean = conds[0]["codes"]
    lam_pos, lam_neg = pipeline.caption_lambdas(sc, cap_tok, neg_tok, clean)                                              # 2 passes
    groups = pipeline.item_groups(sc, gid, K)
    row = dict(gid=gid, image_id=it["image_id"], caption=it["caption"], neg_caption=it["neg_caption"], n_tok=len(cap_tok), n_tok_neg=len(neg_tok), corrupt_at=ctx.corrupt_at, conds={})
    arrays = {}
    for ci, c in enumerate(conds):
        name, codes = c["name"], c["codes"]
        delta = pipeline.image_delta(lam_pos, lam_neg, codes)
        z = np.zeros(sc.L_I, bool) if c["kind"] == "clean" else arms.changed_code_gate(clean, codes)
        gs = pipeline.gate_scores(sc, cap_tok, codes, groups, ctx.dcache, K)                                               # 8 passes
        uj = cal.jitter(gs["u"], ctx.eps0, arms.arm_rng(config.SEED_GATE, gid, ci, arms.ARM_TAG["jitter"], 0))
        G = uj > ctx.thr.tau
        cr = dict(kind=c["kind"], n_changed=int(z.sum()), n_tokens=int(sc.L_I),
                  img={"none": pipeline.compact(evidence.arm_summary(delta, arms.no_gate(sc.L_I))), A0: pipeline.compact(evidence.arm_summary(delta, G))},
                  gate={f"{config.ALPHA_PRIMARY:g}": dict(n_flag=int(G.sum()), n_tp=int((G & z).sum()), n_corrupted=int(z.sum()), n_fp_on_clean_tokens=int((G & ~z).sum()))})
        arrays.update({f"{name}_codes": codes.astype(np.int16), f"{name}_z": z, f"{name}_delta": delta, f"{name}_B": gs["B"], f"{name}_D": gs["D"].astype(np.float32), f"{name}_flag": G})
        row["conds"][name] = cr
    if isinstance(rows0, int):
        row["n_rows"] = int(sc.rows) - rows0
    return row, arrays


# ------------------------------------------------------------------------------------------------ contexts and main
def make_ctx_factory(stage: str, a, pre: dict, runs: Path | None = None):
    def make_ctx(sc, run):
        grid = int(sc.L_I ** 0.5)
        common_ = dict(run=run, grid=grid, patch=max(2, grid // 4), dcache=pipeline.dcache_for(Path(runs if runs is not None else common.RUNS) / DCACHE_RUN), corrupt_at=int(a.corrupt_at))
        if stage == "test":
            test = folds.test_items(load_folds_frozen(), 500)
            common_.update(thr=pre["threshold"], eps0=pre["eps0"], family=pre["family"], fold=test)
        return SimpleNamespace(**common_)
    return make_ctx


def main(argv=None, *, scorer_factory=None, runs: Path | None = None, guards_factory=None):
    import argparse
    pre_ap = argparse.ArgumentParser(add_help=False)
    pre_ap.add_argument("--stage", required=True, choices=sorted(STAGE_DEFAULTS))
    st, _ = pre_ap.parse_known_args(argv)
    run_id, n_default = STAGE_DEFAULTS[st.stage]
    ap = build.omni_parser(run_id, None)
    ap.add_argument("--stage", required=True, choices=sorted(STAGE_DEFAULTS))
    ap.add_argument("--corrupt-at", type=int, choices=[512, 256], default=512, help="resolution at which the pixel corruptions are applied (see the module docstring)")
    a = ap.parse_args(argv)
    stage = a.stage
    try:                                                                                   # all prerequisites BEFORE the model is touched
        pre = check_prereqs(stage, runs, a.n if stage == "test" else None)
    except (FileNotFoundError, ValueError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    n_items = {"cal": N_CAL, "pos": N_POS, "test": pre.get("n_R")}[stage]
    if scorer_factory is None:
        rc = build.preload_check(a)
        if rc is not None:
            return rc
    info: dict = {}
    load = scorer_factory or build.production_loader(a, info)
    cfg = dict(CONFIG, stage=f"OMNI-R-{stage.upper()}", n_items=n_items, duty=a.duty, mem_frac=a.mem_frac, micro_bs=a.micro_bs, magvit_device=a.magvit_device, corrupt_at=a.corrupt_at,
               max_peak_alloc_mib=a.max_peak_alloc_mib, max_used_mib=a.max_used_mib, max_used_first_mib=a.max_used_first_mib, max_rise_mib=a.max_rise_mib,
               p_plus=[c for c, _ in pre.get("family", [])], n_rule=n_rule_name(pre["family_json"]) if "family_json" in pre else None,
               timing_selfcheck_sha256=pre.get("signature", {}).get("selfcheck_sha256"))
    process = {"cal": process_cal, "pos": process_pos, "test": process_test}[stage]
    make_ctx = make_ctx_factory(stage, a, pre, runs)

    def ctx_factory(sc, run):
        if scorer_factory is None:
            build.stop_load_watchdog(info)
            build.write_env(run, sc, info, a)
        return make_ctx(sc, run)

    def selfcheck(sc, items):                                                              # layout check of the first item (the full adapter checks are the timing stage's job)
        raw = sc._sc if isinstance(sc, runner.Counting) else sc
        return raw.selfcheck(common.load_image(items[0]["image_id"]), items[0]["caption"])

    return runner.run_items(run_id=a.run_id, cfg=cfg, load=load, get_items=lambda sc, run: get_items(stage, sc, run, n_items), process=process, make_ctx=ctx_factory,
                            soft_minutes=a.soft_minutes, duty=a.duty, limit=a.limit, guards=(guards_factory(a) if guards_factory else build.omni_guards_from_args(a)), mem_frac=a.mem_frac, selfcheck=selfcheck,
                            watchdog_factory=runner.default_watchdog, allow_dirty=a.allow_dirty)


if __name__ == "__main__":
    sys.exit(main())
