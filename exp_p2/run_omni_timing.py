"""Omni family R, timing and fit stage (SAP AD.7, as amended by AB.5; debate DECISION-R1 item 6). GPU: ONLY with Shlok's go-ahead, through tools/gpu_guard.py, in the omni venv.

    <omni python> -m exp_p2.run_omni_timing --resume --soft-minutes 20 [--limit N] [--run-id P2-OMNI-TIMING]

What it does (all inside `runner.run_items`: hold files, clean-tree rule, AC check, per-process memory cap, per-item guards, in-process watchdog, resumable rows):
  1. pre-load check: whole-GPU memory in use must be <= --max-used-before-load-mib (nvidia-smi, no CUDA context yet), else exit 76;
  2. load tokenizer, 4-bit Omni-Diffusion (audio-encoder stub, no remote code, offline), MAGVIT-v2 (CPU by default);
  3. self-check (written to selfcheck.json): layout equals the training route and the chat template; adapter checks A1-A7 (exp_p2/omni/checks.py) on the real model. The author does not sign them: the
     gate-auditor re-runs / audits them and writes runs/<run-id>/adapter_signature.json (AB.5 item 1);
  4. 20 timed passes: pass i = ONE forward row of a real calibration item (first 20 calibration items that satisfy the Omni token rule), the B-pass context (caption masked, one of K = 8
     complementary image groups masked), batch size 1. Per pass: forward wall seconds (CUDA-synchronised), peak allocated and reserved MiB, whole-GPU MiB. No score is stored. t of the SAP = the
     median of `fwd_s` over passes 6 to 20 (`analysis_omni.omni_gate`).
Extra GPU rows beyond the 20 passes: A5 (one row per item, 6 items), A4 (3), A6 (1), A7 (2) and the layout self-check (0): at most 12 rows, outside the timed set.

Nothing about Omni quality is computed: only times, memory and structural checks."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, core                                                   # noqa: E402
from exp_p2.gate import config, folds, guards as gmod, pipeline, runner           # noqa: E402
from exp_p2.omni import build, checks                                             # noqa: E402
from exp_p2.scoring import MASK_ID                                                # noqa: E402

RUN_ID = "P2-OMNI-TIMING"
N_PASSES, WARMUP = 20, 5
CONFIG = dict(stage="OMNI-TIMING", n_items=N_PASSES, warmup_passes=WARMUP, K=config.K, seed=config.SEED_GATE, duty=0.5, batch_rows=1,
              spec="research/paper2/prereg/SAP-GATE-2026-10-28.md AD.7, AB.5; research/paper2/method/IMPL-C-OMNI-2026-10-28.md")


def get_items(sc, run, n=N_PASSES):
    p = folds.folds_path()
    if not p.exists():
        raise FileNotFoundError(f"{p} missing (the frozen folds; the timing stage does not build folds)")
    f = json.loads(p.read_text(encoding="utf8"))
    kept, rep = build.omni_token_filter(sc, f["cal"][:4 * n], need_neg=False)           # candidates: the first 4n calibration items; the first n that satisfy the rule
    build.write_exclusions(run, rep)
    return kept[:n]


def make_ctx(sc, run):
    return SimpleNamespace(run=run, proc_pass=0, info=getattr(sc, "_omni_info", {}))


def process(sc, it, ctx):
    """One timed pass. The row is not written to arrays (no outcome is stored)."""
    import torch
    cap = sc.caption_ids(it["caption"])
    t_enc = time.perf_counter()
    pil, codes = pipeline.prep_image(sc, it["image_id"])
    enc_s = time.perf_counter() - t_enc
    st = sc.build(cap, codes)
    groups = pipeline.item_groups(sc, it["gid"], config.K)
    m = core.masks_from_groups(groups, config.K)[0]
    x = st["base"].clone()
    x[st["cap_pos"]] = MASK_ID
    x[st["img_pos"][torch.as_tensor(m, device=x.device)]] = MASK_ID
    f = sc.logits_fn(st)
    cuda = x.is_cuda
    if cuda:
        torch.cuda.synchronize()
    t0 = time.perf_counter()
    out = f(x[None])
    if cuda:
        torch.cuda.synchronize()
    fwd_s = time.perf_counter() - t0
    lp = torch.log_softmax(out[0, st["img_pos"][torch.as_tensor(m, device=x.device)], 32001:32001 + 8192].float(), dim=-1)
    finite = bool(torch.isfinite(lp).all())
    ctx.proc_pass += 1
    row = dict(gid=it["gid"], image_id=it["image_id"], n_cap=len(cap), seq_len=int(x.shape[0]), n_masked=int((x == MASK_ID).sum()), fwd_s=fwd_s, encode_s=enc_s, proc_pass=ctx.proc_pass, finite=finite)
    if cuda:
        row.update(peak_alloc_mib=torch.cuda.max_memory_allocated() / 2 ** 20, peak_reserved_mib=torch.cuda.max_memory_reserved() / 2 ** 20, gpu_used_mib=gmod.gpu_used_mib())
    if not finite:
        raise RuntimeError("non-finite log-probabilities in a timed pass (pipeline defect); stopping")
    if isinstance(getattr(sc, "rows", None), int):
        row["n_rows_total"] = sc.rows
    return row, {}


def adapter_selfcheck(sc, items, info: dict, a):
    """Layout self-check (the keys the runner gates on) plus A1-A7 on the real model. `ids_equal` here means: layout equal AND every adapter check ok (the per-check results are all in the file)."""
    from exp_p2.omni import loader  # noqa: F401
    import torch
    raw = sc._sc if isinstance(sc, runner.Counting) else sc
    pil0 = common.load_image(items[0]["image_id"])
    lay = raw.selfcheck(pil0, items[0]["caption"])
    cfg = getattr(raw.model, "config", None)
    results = [checks.check_mask_id(raw, cfg), checks.check_image_range(raw, cfg)]
    sample = items[:6]
    pils = [common.load_image(it["image_id"]) for it in sample[:3]]
    results.append(checks.check_layout_roundtrip(raw, pils, [it["caption"] for it in sample[:3]]))
    if not getattr(a, "skip_gpu_adapter_checks", False):
        st0 = raw.build(raw.caption_ids(items[0]["caption"]), raw.encode(raw.preprocess(pil0)))
        atol = 2e-2 if raw.dev.type == "cuda" else 0.0                                      # both sides call the same kernels on the same row, so 0 is expected; 2e-2 (design choice, E0) only allows for kernel non-determinism
        results.append(checks.check_shift_code_path(raw, st0, seed=0, atol=atol))
        shift_items = [(it["caption"], raw.encode(raw.preprocess(common.load_image(it["image_id"])))) for it in sample]
        results.append(checks.check_shift_behaviour(raw, shift_items, seed=0))
        results.append(checks.check_audio_stub_inert(raw, info["stub"], st0))
        results.append(checks.check_layout_only_null(raw, items[0]["caption"], items[1]["caption"]))
    summ = checks.summarize(results)
    out = dict(lay, layout_ids_equal=lay["ids_equal"], adapter=summ, ids_equal=bool(lay["ids_equal"] and summ["all_ok"]),
               note="ids_equal = layout equal AND all adapter checks ok; signed by the gate-auditor in adapter_signature.json (AB.5 item 1), not by the author")
    out["quantisation"] = build.realised_quantisation(raw.model)                          # audit part 3, m-4
    if torch.cuda.is_available():
        peak = torch.cuda.max_memory_allocated() / 2 ** 20                                # includes the load (the statistics are reset per item only)
        limit = float(getattr(a, "max_peak_alloc_mib", build.PROPOSED["max_peak_alloc_mib"]))
        out["peak_alloc_mib_during_checks"] = peak
        out["peak_gate"] = dict(limit_mib=limit, ok=bool(peak <= limit), rule="lead decision T3: the load plus self-check peak is held to the per-item peak rule")
        if peak > limit:                                                                  # T3 and audit part 3, m-2: stop, as a guard stop (never relaunched by the driver)
            out["ids_equal"] = False
            common.append_jsonl(Path(common.RUNS) / a.run_id / "chunks.jsonl", dict(event="guard_stop", t=time.time(), reason=f"load_and_selfcheck_peak_alloc {peak:.0f} MiB > {limit:.0f}"))
    return out


def main(argv=None, *, scorer_factory=None, guards_factory=None):
    ap = build.omni_parser(RUN_ID, N_PASSES)
    ap.add_argument("--skip-gpu-adapter-checks", action="store_true", help="debug only: skip A4-A7; omni_gate then finds A4-A7 missing in selfcheck.json and can never return GO (audit part 3, M-2)")
    a = ap.parse_args(argv)
    if scorer_factory is None:
        rc = build.preload_check(a)
        if rc is not None:
            return rc
    info: dict = {}
    load = scorer_factory or build.production_loader(a, info)
    cfg = dict(CONFIG, n_items=a.n, duty=a.duty, mem_frac=a.mem_frac, micro_bs=a.micro_bs, magvit_device=a.magvit_device, max_peak_alloc_mib=a.max_peak_alloc_mib,
               max_used_mib=a.max_used_mib, max_used_first_mib=a.max_used_first_mib, max_rise_mib=a.max_rise_mib)

    def load_and_tag():
        sc = load()
        sc._omni_info = info
        return sc

    def selfcheck(sc, items):
        return adapter_selfcheck(sc, items, info, a)

    def ctx_factory(sc, run):
        if scorer_factory is None:
            build.stop_load_watchdog(info)
            build.write_env(run, sc, info, a)
        return make_ctx(sc, run)

    return runner.run_items(run_id=a.run_id, cfg=cfg, load=load_and_tag, get_items=lambda sc, run: get_items(sc, run, a.n or N_PASSES), process=process, make_ctx=ctx_factory,
                            soft_minutes=a.soft_minutes, duty=a.duty, limit=a.limit, guards=(guards_factory(a) if guards_factory else build.omni_guards_from_args(a)), mem_frac=a.mem_frac, selfcheck=selfcheck,
                            watchdog_factory=runner.default_watchdog, allow_dirty=a.allow_dirty)


if __name__ == "__main__":
    sys.exit(main())
