"""GPU generation for the pre-pilot gates (card 4.3 PG-1, 4.4 PG-V). Generation venv only. Run through exp001/gate_driver.py
(which wraps each chunk in tools/gpu_guard.py). Stages:

  pg1g   guided leg: official sampler (50 steps, CFG 3.0), T2I with the clean captions of the 32 GATE_GUIDED items at 512 and 1024 px
  pg1p   condition-P leg: J at k0, unguided, deterministic confidence ranking (or P_rand), rung-1 prefixes of the first 16 gate items,
         at 512 and 1024 px on the same prefixes
  pgv    PG-V: J at k0 on pool PG (24 prefixes x 2 seeds) at --res with --rule; --rung 2 uses pool PG2 and rung-2 prefixes
  realvq VQ codes of real COCO images (32 gate images) at --res for the screen (i)

Per-unit outputs are written atomically; a restart skips finished units. Exit 0 = stage complete, 75 = soft deadline, work remains.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp001 import plan as P, rng
from exp001.config import POOLS, image_tokens
from exp001.runtools import Duty, Deadline, atomic_save_npz, atomic_write_json, log_jsonl, EXIT_DONE, EXIT_MORE_WORK
from exp001.sampler import run_sample

OUT = ROOT / "runs" / "EXP-001" / "gates"
COCO_CACHE = Path(r"C:\Users\Shlok\.cache\dlm_dl\coco")


def load_draw():
    return json.loads((OUT / "coco_draw.json").read_text(encoding="utf8"))


def run_j(net, prefix: str, pool: str, i: int, res: int, rule: str, N: int = 32, prompt_override=None):
    net.set_prompt(prefix if prompt_override is None else prompt_override, n_txt=32, res=res)
    plan = P.plan_J(N, net.L_I)
    u = rng.sampler_uniforms(pool, i, net.L_T + net.L_I)
    prio = rng.position_priorities(pool, i, net.L_T + net.L_I) if rule == "rand" else None
    t0 = time.perf_counter()
    r = run_sample(net, plan, u, rule=rule, prio=prio)
    torch.cuda.synchronize()
    return r, time.perf_counter() - t0


def save_j(path_base: Path, net, r, secs, meta):
    tail = r.tail.numpy()
    img = r.img.numpy()
    atomic_save_npz(path_base.with_suffix(".npz"), tail=tail, img=img)
    pil = net.decode_image(img)
    pil.save(path_base.with_suffix(".png"))
    rec = [asdict(x) for x in r.records]
    meta = dict(meta, seconds=secs, n_forward=r.n_forward, tail_text=net.decode_text(tail), prefix_ids=net.prefix_token_ids(), records=rec)
    atomic_write_json(path_base.with_suffix(".json"), meta)       # the .json is written last: it is the done marker


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["pg1g", "pg1p", "pgv", "realvq"])
    ap.add_argument("--res", type=int, default=512)
    ap.add_argument("--rule", default="conf", choices=["conf", "rand"])
    ap.add_argument("--rung", type=int, default=1)
    ap.add_argument("--soft-minutes", type=float, default=13.0)
    ap.add_argument("--duty", type=float, default=0.5)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--tag", default="")
    ap.add_argument("--limit", type=int, default=None, help="smoke runs: stop after this many units")
    a = ap.parse_args()

    draw = load_draw()
    dl, duty = Deadline(a.soft_minutes), Duty(a.duty)
    stage_dir = OUT / (a.stage + (f"_{a.tag}" if a.tag else ""))
    stage_dir.mkdir(parents=True, exist_ok=True)

    from exp001.unidisc_net import UniDiscNet, shim_info
    from common import commit_free_gb
    net = UniDiscNet(res=a.res)
    log_jsonl(stage_dir / "stage_log.jsonl", dict(event="chunk_start", t=time.time(), free_commit_gb=commit_free_gb(), args=vars(a),
                                                 vram_gb=torch.cuda.memory_allocated() / 1e9, shim=shim_info()))

    units = []                       # (done_marker_path, callable)
    if a.stage == "pg1g":
        items = draw["blocks"]["GATE_GUIDED"]
        for k, it in enumerate(items):
            for res in (512, 1024):
                base = stage_dir / f"item{k:02d}_{res}px"
                units.append((base.with_suffix(".json"), (lambda it=it, k=k, res=res, base=base: _guided(net, it, k, res, base))))
    elif a.stage == "pg1p":
        items = draw["blocks"]["GATE_GUIDED"][:16]
        for k, it in enumerate(items):
            for res in (512, 1024):
                base = stage_dir / f"item{k:02d}_{res}px"
                units.append((base.with_suffix(".json"), (lambda it=it, k=k, res=res, base=base: _pleg(net, it, k, res, base, a.rule))))
    elif a.stage == "pgv":
        pool = "PG" if a.rung == 1 else "PG2"
        items = draw["blocks"][pool]
        lo = POOLS[pool][0]
        for p, it in enumerate(items):
            for e in (0, 1):
                seed = lo + 2 * p + e
                base = stage_dir / f"seed{seed}"
                units.append((base.with_suffix(".json"), (lambda it=it, p=p, e=e, seed=seed, base=base, pool=pool: _pgv(net, it, p, e, seed, base, pool, a))))
    elif a.stage == "realvq":
        from PIL import Image
        import zipfile
        items = draw["blocks"]["GATE_GUIDED"]
        zf = zipfile.ZipFile(COCO_CACHE / "val2017.zip")
        for k, it in enumerate(items):
            base = stage_dir / f"real{k:02d}_{a.res}px"
            units.append((base.with_suffix(".json"), (lambda it=it, base=base: _realvq(net, zf, it, base, a.res))))

    done = 0
    todo = [(m, f) for m, f in units if not m.exists()]
    for marker, fn in todo:
        if dl.reached(margin_s=90):          # keep a margin for the largest unit (a guided 1024-px sample is about 1.5 minutes)
            log_jsonl(stage_dir / "stage_log.jsonl", dict(event="soft_deadline", remaining=len(todo) - done, t=time.time()))
            return EXIT_MORE_WORK
        t0 = time.perf_counter()
        fn()
        busy = time.perf_counter() - t0
        duty.after_unit(busy)
        done += 1
        log_jsonl(stage_dir / "stage_log.jsonl", dict(event="unit", marker=marker.name, busy_s=busy, free_commit_gb=commit_free_gb()))
        if a.limit and done >= a.limit:
            return EXIT_DONE if done == len(todo) else EXIT_MORE_WORK
    log_jsonl(stage_dir / "stage_log.jsonl", dict(event="complete", t=time.time(), duty_busy_s=duty.busy, duty_idle_s=duty.idle))
    return EXIT_DONE


def _guided(net, it, k, res, base):
    t0 = time.perf_counter()
    codes, n_masked = net.official_t2i(it["caption"], seed=777000 + k, res=res)
    secs = time.perf_counter() - t0
    atomic_save_npz(base.with_suffix(".npz"), img=codes.numpy())
    net.decode_image(codes).save(base.with_suffix(".png"))
    atomic_write_json(base.with_suffix(".json"), dict(item=it["image_id"], caption=it["caption"], res=res, seconds=secs, n_masked_after=n_masked,
                                                       steps=50, cfg=3.0, seed=777000 + k, peak_gb=torch.cuda.max_memory_allocated() / 1e9))


def _pleg(net, it, k, res, base, rule):
    r, secs = run_j(net, it["prefix"], "GATE", k, res, rule)
    save_j(base, net, r, secs, dict(item=it["image_id"], prefix=it["prefix"], res=res, rule=rule, pool="GATE", i=k, caption=it["caption"]))


def _pgv(net, it, p, e, seed, base, pool, a):
    r, secs = run_j(net, it["prefix"], pool, seed, a.res, a.rule)
    save_j(base, net, r, secs, dict(item=it["image_id"], prefix=it["prefix"], res=a.res, rule=a.rule, pool=pool, i=seed, prefix_index=p,
                                    seed_in_prefix=e, caption=it["caption"], rung=a.rung))


def _realvq(net, zf, it, base, res):
    from PIL import Image
    import io
    pil = Image.open(io.BytesIO(zf.read("val2017/" + it["file"])))
    net.res = res
    net.L_I = image_tokens(res)
    codes = net.encode_image(pil)
    atomic_save_npz(base.with_suffix(".npz"), img=codes.numpy())
    atomic_write_json(base.with_suffix(".json"), dict(item=it["image_id"], file=it["file"], res=res, n_distinct=int(len(set(codes.tolist()))), n=int(codes.numel())))


if __name__ == "__main__":
    sys.exit(main())
