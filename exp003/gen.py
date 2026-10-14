"""EXP-003 GPU generation stage (generation venv). Run through exp003/chunks.py (every chunk inside tools/gpu_guard.py).

    python exp003/gen.py --stage pilot|ctrl|m1|m2|m3 --resume --soft-minutes 13 [--limit N]

Units are skipped when their .json done marker exists. Exit 0 = stage complete, 75 = soft deadline reached and work remains.
Batch size 1. Duty cycle: after each unit the process idles for as long as the unit ran (Duty, 0.5).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp001 import plan as P, rng                                    # noqa: E402
from exp001.estimator import _Wrap                                    # noqa: E402
from exp001.runtools import Duty, Deadline, atomic_save_npz, atomic_write_json, log_jsonl, EXIT_DONE, EXIT_MORE_WORK  # noqa: E402
from exp001.sampler import run_sample                                 # noqa: E402
from exp003 import config as C                                        # noqa: E402
from exp003.units import GEN, Unit, units_for, load_pool_items, STAGE_POOL  # noqa: E402


class IndNet(_Wrap):
    """NC-1 network (card 6): text marginals from a pass with all image positions masked; image marginals from a pass with all tail
    positions masked and the PREFIX KEPT. Two forwards per pass."""

    def forward(self, tail, img, drop_prefix=False):
        tmask, imask = self._masked(tail, img)
        lp_t, _ = self.net.forward(tail, imask)
        _, lp_i = self.net.forward(tmask, img)
        return lp_t, lp_i


def plain_commit_steps(records, L_T, L_I):
    cs = np.zeros(L_T + L_I, dtype=np.int16)
    for r in records:
        for j in r.text_pos:
            cs[j] = r.q
        for j in r.img_pos:
            cs[L_T + j] = r.q
    return cs


def run_plain(net, unit: Unit, prefix: str):
    net.set_prompt(prefix, n_txt=32, res=512)
    N = C.PLAIN_N[unit.arm]
    plan = P.plan_TF(N, net.L_I) if unit.arm == "TF" else P.plan_J(N, net.L_I)
    use = IndNet(net) if unit.arm == "Ind" else net
    u = rng.sampler_uniforms(C.RNG_POOL[unit.pool], unit.i, net.L_T + net.L_I)
    n0 = net.n_forward
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    r = run_sample(use, plan, u, rule="conf", keep_marginal_stats=False)
    torch.cuda.synchronize()
    secs = time.perf_counter() - t0
    arrays = dict(tail=r.tail.numpy().astype(np.int64), img=r.img.numpy().astype(np.int64),
                  commit_step=plain_commit_steps(r.records, net.L_T, net.L_I))
    meta = dict(seconds=secs, calls=net.n_forward - n0, passes=r.n_forward, plan=r.plan_name, n_passes_plan=N)
    return arrays, meta


def run_official(runner, unit: Unit, prefix: str):
    d = runner.run(prefix, unit.i, unit.steps, unit.cfg, instrument=unit.instrument)
    arrays = dict(tail=d["tail"], img=d["img"])
    meta = dict(seconds=d["seconds"], steps=d["steps"], cfg=d["cfg"], torch_seed=d["torch_seed"], n_masked_text=d["n_masked_text"],
                n_masked_img=d["n_masked_img"])
    if unit.instrument:
        arrays["commit_step"] = d["commit_step"]
        arrays["entries"] = d["entries"].astype(np.int32)
        meta.update(n_masked_before_final=d["n_masked_before_final"], calls=d["calls"], forwards=d["forwards"],
                    assert_calls=d["assert_calls"], guidance=d["guidance"])
    return arrays, meta


def do_unit(net, runner, unit: Unit, item: dict, gen_dir: Path):
    base = unit.base(gen_dir)
    torch.cuda.reset_peak_memory_stats()
    t0 = time.perf_counter()
    arrays, meta = (run_official(runner, unit, item["prefix"]) if unit.kind == "official" else run_plain(net, unit, item["prefix"]))
    atomic_save_npz(base.with_suffix(".npz"), **arrays)
    if unit.save_png:
        net.decode_image(arrays["img"]).save(base.with_suffix(".png"))
    meta.update(stage=unit.stage, arm=unit.arm, tag=unit.tag, pool=unit.pool, p=unit.p, e=unit.e, seed_index=unit.i, image_id=item["image_id"],
                prefix=item["prefix"], tail_text=net.decode_text(arrays["tail"]), peak_gb=torch.cuda.max_memory_allocated() / 1e9,
                eval_mode_asserted=True, wall_unit_s=time.perf_counter() - t0, failed=False)
    atomic_write_json(base.with_suffix(".json"), meta)               # done marker, written last
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=list(STAGE_POOL))
    ap.add_argument("--soft-minutes", type=float, default=13.0)
    ap.add_argument("--duty", type=float, default=C.DUTY)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--gen-dir", default=None, help="smoke runs only")
    a = ap.parse_args()
    C.register_pools()
    gen_dir = Path(a.gen_dir) if a.gen_dir else GEN
    units = units_for(a.stage)
    items = load_pool_items(STAGE_POOL[a.stage])
    stage_dir = gen_dir / a.stage
    stage_dir.mkdir(parents=True, exist_ok=True)
    dl, duty = Deadline(a.soft_minutes), Duty(a.duty)

    from exp001.unidisc_net import UniDiscNet, shim_info
    from exp003.official import OfficialRunner
    from common import commit_free_gb
    net = UniDiscNet(res=512)
    runner = OfficialRunner(net)
    log_jsonl(stage_dir / "stage_log.jsonl", dict(event="chunk_start", t=time.time(), free_commit_gb=commit_free_gb(), args=vars(a),
                                                 vram_gb=torch.cuda.memory_allocated() / 1e9, shim=shim_info()))
    todo = [u for u in units if not u.marker(gen_dir).exists()]
    done = 0
    for u in todo:
        if dl.reached(margin_s=60):
            log_jsonl(stage_dir / "stage_log.jsonl", dict(event="soft_deadline", remaining=len(todo) - done, t=time.time()))
            return EXIT_MORE_WORK
        t0 = time.perf_counter()
        ok, err = False, None
        for attempt in (1, 2):                                          # "rerun once, then logged as failed"
            try:
                do_unit(net, runner, u, items[u.p], gen_dir)
                ok = True
                break
            except Exception as ex:                                      # noqa: BLE001
                err = f"{type(ex).__name__}: {ex}"
                log_jsonl(stage_dir / "failures.jsonl", dict(unit=f"{u.tag}/p{u.p:03d}_e{u.e}", attempt=attempt, error=err,
                                                            trace=traceback.format_exc()[-1500:], t=time.time()))
                try:
                    torch.cuda.empty_cache()
                    net.set_eval()
                except Exception:                                        # noqa: BLE001
                    pass
        if not ok:
            atomic_write_json(u.marker(gen_dir), dict(stage=u.stage, arm=u.arm, tag=u.tag, p=u.p, e=u.e, seed_index=u.i, failed=True, error=err))
        busy = time.perf_counter() - t0
        duty.after_unit(busy)
        done += 1
        log_jsonl(stage_dir / "stage_log.jsonl", dict(event="unit", marker=f"{u.tag}/p{u.p:03d}_e{u.e}", ok=ok, busy_s=busy,
                                                     free_commit_gb=commit_free_gb()))
        if a.limit and done >= a.limit:
            return EXIT_DONE if done == len(todo) else EXIT_MORE_WORK
    log_jsonl(stage_dir / "stage_log.jsonl", dict(event="complete", t=time.time(), duty_busy_s=duty.busy, duty_idle_s=duty.idle))
    return EXIT_DONE


if __name__ == "__main__":
    sys.exit(main())
