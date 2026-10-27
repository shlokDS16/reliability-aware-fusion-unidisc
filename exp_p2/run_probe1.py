"""Probe 1 (likelihood signal): true vs mismatched COCO caption, both directions, K=8 complementary masks, common random numbers.

    python -m exp_p2.run_probe1 --resume --soft-minutes 12.5 [--limit N] [--run-id P2-PROBE-01] [--smoke]

Per item (image i, true caption c_i, mismatched caption c_pi(i)), for each caption c:
  a8      mean log p(caption token | image, rest of caption)  over all caption tokens, each masked once in K=8 passes (image visible)   [PRIMARY a]
  b8      mean log p(image token | caption, rest of image)    over all 1024 image tokens, each masked once in K=8 passes                  [PRIMARY b]
  supplementary (labelled exploratory in the report):
  a8null  as a8 with the whole image masked (same text masks)  -> a8 - a8null = text-side PMI with the image
  afull / afull_null   all caption tokens masked in one pass, image visible / image masked
  b2      K=2 complementary passes over the image (50 percent masked per pass); bfull = all 1024 image tokens masked in one pass
Same masks for both captions: image groups are shared; text groups use one shared priority vector u (group = rank of u[j] mod K).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import core, common                                            # noqa: E402
from exp_p2.scoring import (Spec, masked_logprobs, gather_true, UniScorer, TEXT_LO, TEXT_HI, IMG_LO, IMG_HI)   # noqa: E402

SEED = 20261027
MIS_SEED = 1303
K = 8
CONFIG = dict(probe="probe1", n_items=300, seed=SEED, mismatch_seed=MIS_SEED, K=K, k_alt=2, tok_range=[5, 32], resolution=512,
              scoring="fp32 log-softmax of bf16 logits restricted to the modality vocabulary; batch 4; backbone eval bf16",
              duty=0.5, kill_criterion="both directions (a8, b8) <= 55 percent matching accuracy")


def score_caption(sc: UniScorer, codes: np.ndarray, cap_tok: list[int], u_text: np.ndarray, g_img8: np.ndarray, g_img2: np.ndarray) -> dict:
    st = sc.build(cap_tok, codes)
    base, cap, img = st["base"], st["cap_pos"], st["img_pos"]
    n = len(cap_tok)
    specs: list[Spec] = []
    tags: list[str] = []

    def add(tag, pos, lo, hi, extra=None):
        specs.append(Spec(pos, lo, hi, extra))
        tags.append(tag)

    for m in core.masks_from_groups(core.groups_from_priority(u_text[:n], K), K):
        pos = cap[torch.as_tensor(m, device=cap.device)]
        add("a8", pos, TEXT_LO, TEXT_HI)
        add("a8null", pos, TEXT_LO, TEXT_HI, img)
    add("afull", cap, TEXT_LO, TEXT_HI)
    add("afull_null", cap, TEXT_LO, TEXT_HI, img)
    for tag, g, kk in (("b8", g_img8, K), ("b2", g_img2, 2)):
        for m in core.masks_from_groups(g, kk):
            add(tag, img[torch.as_tensor(m, device=img.device)], IMG_LO, IMG_HI)
    add("bfull", img, IMG_LO, IMG_HI)

    sums: dict[str, float] = {}
    cnt: dict[str, int] = {}
    for tag, sp, lp in zip(tags, specs, masked_logprobs(sc.logits_fn(st), base, specs)):
        lpt, _ = gather_true(lp, base, sp.pos, sp.lo)
        sums[tag] = sums.get(tag, 0.0) + float(lpt.sum())
        cnt[tag] = cnt.get(tag, 0) + int(len(sp.pos))
    out = {t: sums[t] / cnt[t] for t in sums}
    assert cnt["a8"] == n and cnt["a8null"] == n and cnt["afull"] == n and cnt["b8"] == sc.L_I and cnt["b2"] == sc.L_I and cnt["bfull"] == sc.L_I, cnt
    out["n_tok"] = n
    out["n_passes"] = len(specs)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-PROBE-01")
    ap.add_argument("--soft-minutes", type=float, default=12.5)
    ap.add_argument("--duty", type=float, default=CONFIG["duty"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--n", type=int, default=CONFIG["n_items"])
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    from exp001.runtools import Duty, Deadline, EXIT_DONE, EXIT_MORE_WORK
    dl, duty = Deadline(a.soft_minutes), Duty(a.duty)
    cfg = dict(CONFIG, n_items=a.n, duty=a.duty)
    run = common.init_run(a.run_id, cfg)
    rows_path = run / "items.jsonl"
    done = {r["idx"] for r in common.read_jsonl(rows_path)}
    if len(done) >= a.n:
        print("complete")
        return EXIT_DONE

    t_load = time.perf_counter()
    net = common.load_net()
    sc = UniScorer(net)
    load_s = time.perf_counter() - t_load

    sel_path = run / "selection.json"
    if sel_path.exists():
        sel = json.loads(sel_path.read_text(encoding="utf8"))
    else:
        items = common.select_items(a.n, SEED, lambda c: len(sc.caption_ids(c)), tuple(CONFIG["tok_range"]))
        perm = core.derangement(len(items), np.random.default_rng(MIS_SEED)).tolist()
        sel = dict(items=items, mismatch_of=perm, note="item i is scored with its own caption and with the caption of item mismatch_of[i]")
        sel_path.write_text(json.dumps(sel, indent=1), encoding="utf8")
    items, perm = sel["items"], sel["mismatch_of"]

    if not (run / "selfcheck.json").exists():
        it = items[0]
        chk = sc.selfcheck(common.load_image(it["image_id"]), it["caption"])
        (run / "selfcheck.json").write_text(json.dumps(chk, indent=1), encoding="utf8")
        print("selfcheck", chk)
        if not (chk.get("ids_equal") and chk.get("modality_equal")):
            print("SELF-CHECK FAILED: hand-built layout differs from the demo path", file=sys.stderr)
            return 2

    common.append_jsonl(run / "chunks.jsonl", dict(event="chunk_start", t=time.time(), load_s=load_s, done=len(done), mem=common.mem_status(), gpu=common.gpu_state()))
    n_new = 0
    for i in range(a.n):
        if i in done:
            continue
        if dl.reached(margin_s=45):
            common.append_jsonl(run / "chunks.jsonl", dict(event="soft_deadline", t=time.time(), remaining=a.n - len(done) - n_new))
            return EXIT_MORE_WORK
        t0 = time.perf_counter()
        torch.cuda.reset_peak_memory_stats()
        it, mi = items[i], items[perm[i]]
        rng = np.random.default_rng([SEED, i])
        pil = sc.preprocess(common.load_image(it["image_id"]))
        codes = sc.encode(pil)
        g8 = core.complementary_groups(sc.L_I, K, rng)
        g2 = core.complementary_groups(sc.L_I, 2, rng)
        u_text = rng.random(64)
        t_tr = score_caption(sc, codes, sc.caption_ids(it["caption"]), u_text, g8, g2)
        t_mi = score_caption(sc, codes, sc.caption_ids(mi["caption"]), u_text, g8, g2)
        torch.cuda.synchronize()
        busy = time.perf_counter() - t0
        row = dict(idx=i, image_id=it["image_id"], mismatch_image_id=mi["image_id"], caption=it["caption"], mismatch_caption=mi["caption"],
                   true=t_tr, mis=t_mi, seconds=busy, peak_gb=torch.cuda.max_memory_allocated() / 1e9, free_ram_gb=common.mem_status()["free_ram_gb"])
        common.append_jsonl(rows_path, row)
        n_new += 1
        duty.after_unit(busy)
        if a.limit and n_new >= a.limit:
            return EXIT_DONE if len(done) + n_new >= a.n else EXIT_MORE_WORK
    common.append_jsonl(run / "chunks.jsonl", dict(event="complete", t=time.time()))
    return EXIT_DONE


if __name__ == "__main__":
    sys.exit(main())
