"""S2 re-infill (SAP AD.5 and AB.4; MUST experiment, secondary family S2, m = 2): does repairing the positions GATE-M flagged help image-direction verification more than repairing the same
number of RANDOMLY placed positions with the same sampler? It tests the LOCATION of the repaired set, nothing else.

    python -m exp_p2.gate.gate_driver --stage s2 --n 300            # production: chunks under tools/gpu_guard.py, one hold-file check per chunk
    python -m exp_p2.run_gate_s2 --resume --soft-minutes 12.5 [--limit N] [--n 300] [--arms igate,irand,ichg] [--leak]
    python -m exp_p2.run_gate_s2 --figures --run-id P2-GATE-S2-FIG   # AFTER the S2 fold is complete: decodes the preregistered figure subset only (AD.5)

Prerequisites (checked before the model is touched; nothing is defaulted):
    runs/P2-GATE-M4/ complete for every item of the S2 list (items.jsonl rows and arrays/itemNNNN.npz with clean_codes, <cond>_codes, <cond>_z, <cond>_flag0.05)  (G is READ, never recomputed)
    runs/P2-GATE-M3/family.json (endpoint d)   -> conditions: patch (parameters of PS1) and, if P3 has an operating point, the splice key; no splice operating point -> that cell is not run

Per item (S2 list = the first n items of the ordered test list; M4 order and token-rule exclusions, SAP AD.5 prefix rule):
    2 passes       Lambda^{c+}, Lambda^{c-} (caption-only tables, every arm below is a gather; same two passes M4 uses)
    per condition  I-GATE   n_draw = 4 draws re-infilling G (GATE-M flags, alpha 0.05)          } the kept draw = highest own caption-masked chain likelihood
                   I-RAND4  4 draws, each a NEW uniformly random set of g_i = |G| positions    }   (comparator "random-gate best-of-4 re-infill (G.1-inspired)", AB.4)
                   I-CHG    4 draws re-infilling the truly changed positions (oracle, descriptive)
                   [ I-LEAK 1 draw, G re-infilled with the true caption VISIBLE (leakage demonstration, off unless --leak) ]
                   NONE and M (GATE-M drop) are gathers on the corrupted codes
    S_r = 16 steps per draw, so at most 4 x 16 = 64 rows per arm per condition (fewer if g_i < 16; none if g_i = 0).
Y is the image-direction decision on ALL 1,024 repaired tokens, ties wrong. Every row stores the Y of each of the 4 draws (AB.4 item 4), the kept draw, the chain likelihoods, the token-level agreement
with the clean codes (descriptive, never 'restoration'), peak_gb and seconds (runner), n_rows. Repaired codes of every draw are saved in arrays/ (int16); images are decoded only in `--figures` mode."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                          # noqa: E402
from exp_p2.gate import arms, config, evidence, folds, pipeline, reinfill, runner   # noqa: E402

RUN_ID, FIG_RUN_ID = "P2-GATE-S2", "P2-GATE-S2-FIG"
M3_RUN, M4_RUN = "P2-GATE-M3", "P2-GATE-M4"
N_S2 = 300                    # Shlok's decision 2026-10-28 (brief); SAP AD.5 text says n_S2 = 150 and needs a dated addendum row before outcomes are read (see the report)
N_SAP_TEXT = 150
ALPHA = config.ALPHA_PRIMARY
A0 = f"gate{ALPHA:g}"
FLAG_KEY = "flag{:g}".format(ALPHA)
ARMS_ALL = ("igate", "irand", "ichg")
ARM_ID = dict(igate=0, irand=1, ichg=2, ileak=3)
ORDER_TAG = dict(igate="s2_gate_order", irand="s2_rand_order", ichg="s2_chg_order", ileak="s2_leak_order")
COND_INDEX = dict(patch=0, splice=1)      # fixed numbers (not list positions) so that a cut cell cannot change the seeds of the other
FIG_FIRST, FIG_HARM = 8, 4
CONFIG = dict(stage="S2", fold="test", n_items=N_S2, n_sap_text=N_SAP_TEXT, seed=config.SEED_GATE, S_r=reinfill.S_R, n_draw=reinfill.N_DRAW, alpha=ALPHA, arms=list(ARMS_ALL), leak=False,
              m4_run=M4_RUN, duty=0.5, spec="research/paper2/prereg/SAP-GATE-2026-10-28.md AD.5, AB.4; research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md 11.2 S2, v1 Algorithm 6",
              comparator="I-RAND4: random-gate best-of-4 re-infill (G.1-inspired)", selection="highest own caption-masked chain log-likelihood (sum of log pi_j(y_j)); ties to the lowest draw",
              sampler="S_r unmask steps in a fixed random order, unguided, temperature 1, image vocabulary, caption masked (R1)")


def corr_of(cond: str) -> str:
    import re
    return re.match(r"[a-z]+", cond).group(0)


# ------------------------------------------------------------------------------------------------ prerequisites and the item list
def s2_conditions(runs: Path | None = None) -> list[str]:
    """['patch'] plus the splice key of family.json if P3 has an operating point (AD.5). Raises FileNotFoundError / ValueError like M4's prerequisites."""
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    fp = runs / M3_RUN / "family.json"
    if not fp.exists():
        raise FileNotFoundError(f"{fp} missing; create it with: python -m exp_p2.gate.headroom --run-id P2-GATE-M3 --endpoint d")
    fam = pipeline.load_json(fp)
    if fam.get("endpoint") != "d":
        raise ValueError(f"{fp} does not record \"endpoint\": \"d\"; invalid for the SAP (Addendum 1)")
    conds = ["patch"]
    for f in fam["family"]:
        if f["corruption"] == "splice":
            conds.append(f["key"])
    return conds


def plan_items(n: int | None, runs: Path | None = None, m4_run: str = M4_RUN) -> tuple[list[dict], dict]:
    """The S2 list without a model: M4's ordered test list cut at n, minus the items M4 excluded under the real-tokenizer rule (excluded, counted, not replaced; token_exclusions.json is M4's
    own record). Returns (items, info). Raises FileNotFoundError if folds.json or M4's token_exclusions.json are missing."""
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    fpath = runs / config.FOLDS_RUN_ID / "folds.json"
    xp = runs / m4_run / "token_exclusions.json"
    for p in (fpath, xp):
        if not p.exists():
            raise FileNotFoundError(f"{p} missing (S2 reads M4's list and exclusions; run and complete M4 first)")
    f = json.loads(fpath.read_text(encoding="utf8"))
    ex = json.loads(xp.read_text(encoding="utf8"))["excluded"]
    items = folds.test_items(f, n if n and n > len(f["test"]) else None)
    if n and n > len(items):
        raise ValueError(f"folds.json holds {len(items)} test items, --n {n} asked for more")
    items = items[:n] if n else items
    bad = set(ex.get("test", [])) | set(ex.get("test_ext", []))
    kept = [it for it in items if it["idx"] not in bad]
    return kept, dict(planned=len(items), excluded=len(items) - len(kept), n_requested=n)


def m4_complete_for(items: list[dict], runs: Path | None = None, m4_run: str = M4_RUN, conds=("patch",)) -> dict:
    """Every S2 item must have an M4 row and an array file with the keys S2 reads. Returns dict(rows={idx: row}, missing=[idx...], bad_keys=[(idx, key)...])."""
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    rows = {r["idx"]: r for r in common.read_jsonl(runs / m4_run / "items.jsonl")}
    missing, bad = [], []
    for it in items:
        ap = runs / m4_run / "arrays" / f"item{it['idx']:04d}.npz"
        if it["idx"] not in rows or not ap.exists():
            missing.append(it["idx"])
    if items and not missing:
        a = np.load(runs / m4_run / "arrays" / f"item{items[0]['idx']:04d}.npz")
        need = ["clean_codes"] + [f"{c}_{k}" for c in conds for k in ("codes", "z", FLAG_KEY)]
        bad = [(items[0]["idx"], k) for k in need if k not in a.files]
    return dict(rows=rows, missing=missing, bad_keys=bad)


# ------------------------------------------------------------------------------------------------ one item
def make_ctx_factory(a, runs: Path | None = None):
    def make_ctx(sc, run):
        runs_ = Path(runs) if runs is not None else Path(common.RUNS)
        m4 = runs_ / a.m4_run
        conds = s2_conditions(runs_)
        items, _ = plan_items(a.n, runs_, a.m4_run)
        chk = m4_complete_for(items, runs_, a.m4_run, conds)
        if chk["missing"] or chk["bad_keys"]:
            raise FileNotFoundError(f"M4 is not complete for the S2 list: missing {chk['missing'][:10]} ({len(chk['missing'])} items), bad keys {chk['bad_keys']}")
        arms_ = tuple(x for x in a.arms.split(",") if x)
        return SimpleNamespace(run=run, conds=conds, m4=m4, m4_rows=chk["rows"], arms=arms_, leak=bool(a.leak), n_draw=reinfill.N_DRAW, S_r=reinfill.S_R)
    return make_ctx


def _ev(delta, included=None):
    return evidence.evidence_from_delta(delta, included)


def _arm_sets(arm: str, gid: int, ci: int, G: np.ndarray, z: np.ndarray, n_draw: int, m: int) -> tuple[list[np.ndarray], list[np.random.Generator], list[int]]:
    """Position sets, order generators and sampling seeds of one arm. Deterministic in (SEED_GATE, item gid, condition index, arm, draw)."""
    g = int(G.sum())
    S = config.SEED_GATE
    if arm in ("igate", "ileak"):
        sets = [np.flatnonzero(G)] * n_draw
    elif arm == "irand":                                       # equal size, new uniformly random set per draw, independent of the content and of G
        sets = [np.flatnonzero(arms.scattered_gate(g, m, arms.arm_rng(S, gid, ci, arms.ARM_TAG["s2_rand_set"], b))) for b in range(n_draw)]
    elif arm == "ichg":
        sets = [np.flatnonzero(z)] * n_draw
    else:
        raise ValueError(arm)
    orders = [arms.arm_rng(S, gid, ci, arms.ARM_TAG[ORDER_TAG[arm]], b) for b in range(n_draw)]
    seeds = [int(arms.arm_rng(S, gid, ci, arms.ARM_TAG["s2_sample"], ARM_ID[arm] * 100 + b).integers(0, 2 ** 31 - 1)) for b in range(n_draw)]
    return sets, orders, seeds


def process(sc, it, ctx):
    gid, idx = it["gid"], it["idx"]
    rows0 = getattr(sc, "rows", None)
    cap_tok, neg_tok = sc.caption_ids(it["caption"]), sc.caption_ids(it["neg_caption"])
    m4 = np.load(ctx.m4 / "arrays" / f"item{idx:04d}.npz")
    m4row = ctx.m4_rows[idx]
    clean = m4["clean_codes"].astype(np.int64)
    m = sc.L_I
    lam_pos, lam_neg = pipeline.caption_lambdas(sc, cap_tok, neg_tok, clean)                      # 2 passes, shared by every arm of every condition
    row = dict(gid=gid, image_id=it["image_id"], caption=it["caption"], neg_caption=it["neg_caption"], n_tok=len(cap_tok), n_tok_neg=len(neg_tok), conds={})
    arrays = {"clean_codes": clean.astype(np.int16)}
    for cond in ctx.conds:
        t0 = time.perf_counter()
        ci = COND_INDEX[corr_of(cond)]
        codes = m4[f"{cond}_codes"].astype(np.int64)
        z = m4[f"{cond}_z"].astype(bool)
        G = m4[f"{cond}_{FLAG_KEY}"].astype(bool)
        if not np.array_equal(z, clean != codes):
            raise ValueError(f"item {idx} {cond}: M4's changed-code labels disagree with clean_codes != {cond}_codes")
        g = int(G.sum())
        st = sc.build(cap_tok, codes)
        d_none = pipeline.image_delta(lam_pos, lam_neg, codes)
        ev_none, ev_m = _ev(d_none), evidence.evidence_from_delta(d_none, ~G)                      # M = GATE-M drop: included set R = ~G
        m4c = m4row["conds"][cond]["img"]
        cr = dict(g=g, n_changed=int(z.sum()), n_tp=int((G & z).sum()), recall=float((G & z).sum() / z.sum()) if z.any() else float("nan"),
                  precision=float((G & z).sum() / g) if g else float("nan"),
                  m4_y=dict(none=m4c["none"]["y"], gate=m4c[A0]["y"]), s2_y_matches_m4=dict(none=bool(ev_none["y"] == m4c["none"]["y"]), gate=bool(ev_m["y"] == m4c[A0]["y"])),
                  arms=dict(none=pipeline.compact(ev_none), m=pipeline.compact(ev_m)))
        arrays[f"{cond}_codes"], arrays[f"{cond}_z"], arrays[f"{cond}_G"] = codes.astype(np.int16), z, G
        todo = list(ctx.arms) + (["ileak"] if ctx.leak else [])
        for arm in todo:
            n_draw = 1 if arm == "ileak" else ctx.n_draw
            sets, orders, seeds = _arm_sets(arm, gid, ci, G, z, n_draw, m)
            rf = reinfill.reinfill(sc, st, codes, sets, orders, seeds, caption_visible=(arm == "ileak"), S_r=ctx.S_r)
            evs = [_ev(pipeline.image_delta(lam_pos, lam_neg, rf["codes"][b])) for b in range(n_draw)]
            kept = reinfill.keep_best(rf["logp"]) if arm != "ileak" else 0
            masks = np.zeros((n_draw, m), bool)
            for b in range(n_draw):
                masks[b, sets[b]] = True
            agree = [reinfill.token_agreement(rf["codes"][b], clean, codes, masks[b]) for b in range(n_draw)]
            cr["arms"][arm] = dict(y=evs[kept]["y"], d=evs[kept]["d"], mean=evs[kept]["mean"], kept=kept, y_draws=[e["y"] for e in evs], d_draws=[e["d"] for e in evs],
                                   logp=[float(v) for v in rf["logp"]], n_steps=int(rf["n_steps"]), n_set=int(len(sets[0])),
                                   agree_changed=agree[kept]["agree_changed"], agree_set=agree[kept]["agree_set"],
                                   agree_changed_mean=float(np.nanmean([a["agree_changed"] for a in agree])) if z.any() else float("nan"))
            arrays[f"{cond}_codes_{arm}"] = rf["codes"].astype(np.int16)
            arrays[f"{cond}_set_{arm}"] = masks
            arrays[f"{cond}_logp_{arm}"] = rf["logp"].astype(np.float32)
        cr["seconds_cond"] = time.perf_counter() - t0
        row["conds"][cond] = cr
    del lam_pos, lam_neg
    if isinstance(rows0, int):
        row["n_rows"] = int(sc.rows) - rows0
    return row, arrays


# ------------------------------------------------------------------------------------------------ figures (AD.5, AB.4 item 5): a separate decode stage, after the fold is complete
def select_figure_items(rows: list[dict], conds: list[str]) -> dict:
    """The preregistered figure subset. `rows` = S2 rows in list order. Per condition: the first FIG_FIRST items in list order with g_i >= 1 (selection uses no outcome) and the first FIG_HARM
    items in list order with Y(I-GATE) = 0 and Y(NONE) = 1 (harm cases, if any). Returns {cond: dict(first=[idx...], harm=[idx...])}."""
    out = {}
    for c in conds:
        first = [r["idx"] for r in rows if c in r["conds"] and r["conds"][c]["g"] >= 1][:FIG_FIRST]
        harm = [r["idx"] for r in rows if c in r["conds"] and r["conds"][c]["arms"]["igate"]["y"] == 0 and r["conds"][c]["arms"]["none"]["y"] == 1][:FIG_HARM]
        out[c] = dict(first=first, harm=harm)
    return out


def overlay(pil, G: np.ndarray, tint=(255, 0, 0), alpha: float = 0.45):
    """The decoded corrupted image with the flagged token cells tinted (grid x grid cells)."""
    from PIL import Image
    a = np.asarray(pil.convert("RGB"), np.float32).copy()
    grid = int(round(len(G) ** 0.5))
    H, W = a.shape[:2]
    cell = np.kron(np.asarray(G, bool).reshape(grid, grid), np.ones((H // grid, W // grid), bool))
    a[cell] = (1 - alpha) * a[cell] + alpha * np.asarray(tint, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _free_gpu():
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def process_fig(sc, it, ctx):
    """Decode and save the PNGs of one figure item: clean (once), and per condition the corrupted image, the G overlay, I-GATE and I-RAND4 (kept draw and 'draw 1, not selected'), I-CHG (kept)."""
    idx = it["idx"]
    out_dir = Path(ctx.run) / "png"
    out_dir.mkdir(exist_ok=True)
    a = np.load(Path(ctx.s2) / "arrays" / f"item{idx:04d}.npz")
    s2row = ctx.s2_rows[idx]
    files, meta = [], {}

    def save(pil, role, cond=None):
        name = f"item{idx:04d}_{role}.png" if cond is None else f"item{idx:04d}_{cond}_{role}.png"
        pil.save(out_dir / name)
        files.append(name)

    _free_gpu()                                           # full-vocabulary logits of the scoring stage are long gone; this is a separate process with the VQ decoder only
    save(sc.decode(a["clean_codes"].astype(np.int64)), "clean")
    for cond, why in it["roles"].items():
        cr = s2row["conds"][cond]
        cor = sc.decode(a[f"{cond}_codes"].astype(np.int64))
        save(cor, "corrupted", cond)
        save(overlay(cor, a[f"{cond}_G"]), "overlay_G", cond)
        for arm in ("igate", "irand"):
            if f"{cond}_codes_{arm}" not in a.files:
                continue
            kept = cr["arms"][arm]["kept"]
            cs = a[f"{cond}_codes_{arm}"].astype(np.int64)
            save(sc.decode(cs[kept]), f"{arm}_selected", cond)
            save(sc.decode(cs[0]), f"{arm}_draw1_not_selected" if kept != 0 else f"{arm}_draw1_is_selected", cond)
        if f"{cond}_codes_ichg" in a.files:
            save(sc.decode(a[f"{cond}_codes_ichg"].astype(np.int64)[cr["arms"]["ichg"]["kept"]]), "ichg_selected", cond)
        meta[cond] = dict(why=why, g=cr["g"], y_igate=cr["arms"]["igate"]["y"], y_none=cr["arms"]["none"]["y"], y_irand=cr["arms"].get("irand", {}).get("y"),
                          caption="best of 4 draws by own likelihood, caption masked; not typical samples. Not restoration: samples from the model's prior decoded by the VQ decoder.")
    _free_gpu()
    return dict(files=files, roles=meta), {}


# ------------------------------------------------------------------------------------------------ main
def main(argv=None):
    ap = runner.base_parser(RUN_ID, N_S2)
    ap.add_argument("--m4-run", default=M4_RUN)
    ap.add_argument("--arms", default=",".join(ARMS_ALL), help="re-infill arms; igate and irand are required (the confirmatory contrast); ichg is the descriptive oracle and the first thing to cut")
    ap.add_argument("--leak", action="store_true", help="optional I-LEAK demonstration (G re-infilled with the true caption visible, 1 draw); first to be cut (AD.5)")
    ap.add_argument("--figures", action="store_true", help="decode the preregistered figure subset of a COMPLETE S2 run (default run id P2-GATE-S2-FIG, reads --s2-run)")
    ap.add_argument("--s2-run", default=RUN_ID)
    a = ap.parse_args(argv)
    if a.figures and a.run_id == RUN_ID:
        a.run_id = FIG_RUN_ID                  # figure mode: --n stays the S2 list size (the driver passes it); the runner records the smaller effective n (= number of figure items) in effective_n.json
    arms_ = tuple(x for x in a.arms.split(",") if x)
    try:                                                                  # all prerequisites are checked BEFORE the model is touched
        if not set(("igate", "irand")) <= set(arms_) or not set(arms_) <= set(ARMS_ALL):
            raise ValueError(f"--arms must contain igate and irand and be a subset of {ARMS_ALL}")
        runs = Path(common.RUNS)
        conds = s2_conditions(runs)
        items, info = plan_items(a.n, runs, a.m4_run)
        chk = m4_complete_for(items, runs, a.m4_run, conds)
        if chk["missing"] or chk["bad_keys"]:
            raise FileNotFoundError(f"M4 is not complete for the S2 list: {len(chk['missing'])} items missing (first {chk['missing'][:10]}), bad keys {chk['bad_keys']}; S2 runs after M4 (AD.5)")
        fig_items = None
        if a.figures:
            s2rows = {r["idx"]: r for r in common.read_jsonl(runs / a.s2_run / "items.jsonl")}
            n_plan = len(items)
            eff = runs / a.s2_run / "effective_n.json"
            if eff.exists():
                n_plan = min(n_plan, json.loads(eff.read_text(encoding="utf8"))["effective"])
            if len(s2rows) < n_plan:
                raise ValueError(f"S2 run {a.s2_run} has {len(s2rows)} of {n_plan} rows; the figure subset uses outcomes (harm cases) and waits for the complete fold (SAP 8.2)")
            ordered = [s2rows[it["idx"]] for it in items if it["idx"] in s2rows]
            sel = select_figure_items(ordered, conds)
            by_idx = {it["idx"]: it for it in items}
            roles: dict[int, dict] = {}
            for c, v in sel.items():
                for why, ids in v.items():
                    for i in ids:
                        roles.setdefault(i, {}).setdefault(c, []).append(why)
            fig_items = [dict(by_idx[i], roles={c: "+".join(w) for c, w in roles[i].items()}) for i in sorted(roles, key=lambda i: [x["idx"] for x in items].index(i))]
    except (FileNotFoundError, ValueError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    cfg = dict(CONFIG, n_items=a.n, duty=a.duty, mem_frac=a.mem_frac, arms=list(arms_), leak=bool(a.leak), m4_run=a.m4_run, conds=conds, figures=bool(a.figures),
               n_vs_sap_text=dict(n=a.n, sap_ad5=N_SAP_TEXT))

    def load():
        from exp_p2.scoring import UniScorer
        return runner.Counting(UniScorer(common.load_net()))

    if a.figures:
        def make_fig_ctx(sc, run):
            return SimpleNamespace(run=run, s2=runs / a.s2_run, s2_rows={r["idx"]: r for r in common.read_jsonl(runs / a.s2_run / "items.jsonl")})
        return runner.run_items(run_id=a.run_id, cfg=cfg, load=load, get_items=lambda sc, run: fig_items, process=process_fig, make_ctx=make_fig_ctx, soft_minutes=a.soft_minutes, duty=a.duty,
                                limit=a.limit, guards=runner.guards_from_args(a), mem_frac=a.mem_frac, selfcheck=None, watchdog_factory=runner.default_watchdog, allow_dirty=a.allow_dirty)

    def selfcheck(sc, items_):
        return sc.selfcheck(common.load_image(items_[0]["image_id"]), items_[0]["caption"])

    return runner.run_items(run_id=a.run_id, cfg=cfg, load=load, get_items=lambda sc, run: items, process=process, make_ctx=make_ctx_factory(a), soft_minutes=a.soft_minutes, duty=a.duty,
                            limit=a.limit, guards=runner.guards_from_args(a), mem_frac=a.mem_frac, selfcheck=selfcheck, watchdog_factory=runner.default_watchdog, allow_dirty=a.allow_dirty)


if __name__ == "__main__":
    sys.exit(main())
