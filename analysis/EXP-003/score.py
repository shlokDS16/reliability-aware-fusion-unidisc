"""Scoring stage of EXP-003 (eval venv, GPU, offline). Run through exp003/chunks.py inside tools/gpu_guard.py.

    python analysis/EXP-003/score.py --scope pilot|ctrl|main --resume --soft-minutes 13 --duty 0.5

For every (arm, prefix) with both seeds present it writes runs/EXP-003/score/<scope>/<arm>/p<PPP>.json (done marker, written last) and .npz:
  q          [[noun, 'p:e', P(yes)], ...] the Qwen3-VL-2B presence queries of the query plan (tables.queries_for_prefix)
  iqa        CLIP-IQA of the two images; near_uniform pixel-SD proxy; embeddings (CLIP ViT-L/14) of both images and of the full caption,
             completion-only and prefix-only text of both samples (npz)
The ctrl scope also scores PC-2 (score/ctrl/pc2.json). No result of this script is used to choose anything.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(HERE), str(ROOT / "analysis" / "EXP-001")]

import tables as T                                                  # noqa: E402
from exp001.runtools import Duty, Deadline, atomic_save_npz, atomic_write_json, log_jsonl  # noqa: E402
from exp003 import config as C                                       # noqa: E402
from exp003.units import load_pool_items                             # noqa: E402

N_PREFIX = {"pilot": 16, "ctrl": 48}
SPOOL = {"pilot": "E3-PILOT", "ctrl": "E3-CTRL", "main": "E3-MAIN"}


def n_prefix(scope):
    return N_PREFIX.get(scope) or json.loads((C.RUNS / "n_conf.json").read_text(encoding="utf-8"))["n_generate"]


def near_uniform(pil, thr=6.0) -> bool:
    return bool(np.asarray(pil.convert("L"), dtype=np.float64).std() < thr)


def pc2(vlm, tools, out: Path):
    """PC-2 (card 6): per-noun presence of the clean caption's nouns in the own guided-T2I image (EXP-001 PG-1, 512 px) and in the image of
    another caption (one fixed derangement, seed 5303)."""
    from PIL import Image
    draw = json.loads((ROOT / "runs" / "EXP-001" / "gates" / "coco_draw.json").read_text(encoding="utf8"))["blocks"]["GATE_GUIDED"]
    imgs = [Image.open(ROOT / "runs" / "EXP-001" / "gates" / "pg1g" / f"item{k:02d}_512px.png").convert("RGB") for k in range(len(draw))]
    pi = T.derangement(len(draw), C.DERANGEMENT_SEED_PC2)
    rows = []
    for k, it in enumerate(draw):
        toks = tools.tagger(it["caption"].lower())
        nouns = [w for w, pos, _ in toks if pos in ("NOUN", "PROPN") and w not in tools.stop and any(c.isalpha() for c in w)]
        for n in dict.fromkeys(nouns):
            rows.append([n, k, int(pi[k]), vlm.presence(imgs[k], n), vlm.presence(imgs[int(pi[k])], n)])
    m = float(np.mean([r[3] >= 0.5 for r in rows]))
    x = float(np.mean([r[4] >= 0.5 for r in rows]))
    atomic_write_json(out, dict(rows=rows, n_nouns=len(rows), matched=m, cross=x, matched_minus_cross=m - x,
                                passes=bool(m >= 0.60 and (m - x) >= 0.25), derangement_seed=C.DERANGEMENT_SEED_PC2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", required=True, choices=list(SPOOL))
    ap.add_argument("--soft-minutes", type=float, default=13.0)
    ap.add_argument("--duty", type=float, default=C.DUTY)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--gen-dir", default=None)
    ap.add_argument("--score-dir", default=None)
    ap.add_argument("--n-prefix", type=int, default=None)
    a = ap.parse_args()
    gen_dir = Path(a.gen_dir) if a.gen_dir else T.GEN
    root = Path(a.score_dir) if a.score_dir else T.SCORE
    n = a.n_prefix or n_prefix(a.scope)
    arms = T.SCOPE_ARMS[a.scope]
    items = load_pool_items(SPOOL[a.scope])
    log_path = root / a.scope / "stage_log.jsonl"
    (root / a.scope).mkdir(parents=True, exist_ok=True)
    dl, duty = Deadline(a.soft_minutes), Duty(a.duty)
    tools = T.Tools()
    data = {}
    cross_pi = T.derangement(n, C.DERANGEMENT_SEED_CROSS)
    for arm in arms:
        smp = T.load_arm(a.scope, arm, n, items, tools, gen_dir)
        sets = T.noun_sets(smp)
        plac = None if arm in T.NO_PLACEBO else T.placebo_sets(sets, n)
        data[arm] = (smp, sets, plac)
    todo = [(p, arm) for p in range(n) for arm in arms if not (T.score_dir(a.scope, arm, root) / f"p{p:03d}.json").exists()]
    pc2_out = root / "ctrl" / "pc2.json"
    need_pc2 = a.scope == "ctrl" and not pc2_out.exists()
    if not todo and not need_pc2:
        log_jsonl(log_path, dict(event="complete", t=time.time()))
        return 0
    from evalmodels import ClipScorer, VlmScorer
    from PIL import Image
    clip, vlm = ClipScorer(), VlmScorer()
    log_jsonl(log_path, dict(event="chunk_start", t=time.time(), args=vars(a), todo=len(todo)))
    if need_pc2:
        pc2(vlm, tools, pc2_out)
    cache = {}

    def img(arm, key):
        if (arm, key) not in cache:
            p, e = map(int, key.split(":"))
            cache[(arm, key)] = Image.open(data[arm][0][p][e]["png"]).convert("RGB")
            if len(cache) > 64:
                cache.pop(next(iter(cache)))
        return cache[(arm, key)]

    for p, arm in todo:
        if dl.reached(margin_s=90):
            log_jsonl(log_path, dict(event="soft_deadline", remaining=len(todo), t=time.time()))
            return 75
        t0 = time.perf_counter()
        smp, sets, plac = data[arm]
        d = T.score_dir(a.scope, arm, root)
        d.mkdir(parents=True, exist_ok=True)
        if sets[p] is None:
            atomic_write_json(d / f"p{p:03d}.json", dict(p=p, ok=False))
        else:
            qs = list(dict.fromkeys(T.queries_for_prefix(p, sets, plac, arm, n, cross_pi)))
            tv = time.perf_counter()
            out = [[nn, k, float(vlm.presence(img(arm, k), nn))] for nn, k in qs]
            vlm_s = time.perf_counter() - tv
            pils = [img(arm, f"{p}:0"), img(arm, f"{p}:1")]
            ims = clip.images(pils)
            s = smp[p]
            texts = [s[e]["caption"] for e in (0, 1)] + [s[e]["comp"] for e in (0, 1)] + [s[e]["prefix"] for e in (0, 1)]
            tx = clip.texts(texts)
            iqa = clip.iqa(pils)
            atomic_save_npz(d / f"p{p:03d}.npz", img=ims, full=tx[0:2], comp=tx[2:4], pref=tx[4:6])
            atomic_write_json(d / f"p{p:03d}.json", dict(p=p, ok=True, q=out, iqa=[float(x) for x in iqa], near_uniform=[near_uniform(x) for x in pils],
                                                         vlm_calls=len(qs), vlm_s=vlm_s))
        busy = time.perf_counter() - t0
        duty.after_unit(busy)
        log_jsonl(log_path, dict(event="unit", marker=f"{arm}/p{p:03d}", busy_s=busy))
    log_jsonl(log_path, dict(event="complete", t=time.time(), duty_busy_s=duty.busy, duty_idle_s=duty.idle, clip_truncated=clip.truncated))
    return 0


if __name__ == "__main__":
    sys.exit(main())
