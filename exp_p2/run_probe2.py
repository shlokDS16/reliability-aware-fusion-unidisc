"""Probe 2 (token reliability detection): per-token scores for corrupted image tokens, UniDisc 1.4B, true caption present.

    python -m exp_p2.run_probe2 --resume --soft-minutes 12.5 [--limit N] [--run-id P2-PROBE-02]

Corruptions of the 32x32 token map (fixed seeds, per image): swap (15 percent of tokens replaced by uniform random codes), patch (one 8x8 token
block replaced by random codes), jpeg (JPEG quality 10 on the 512-px pixels, then tokenised), noise (Gaussian pixel noise sigma 0.1 on [0,1]
pixels, clipped and rounded to 8 bit, then tokenised). 'Corrupted token' = code differs from the clean image's code.
Scores per token i (K=8 complementary masks over the 1024 image tokens, caption visible unless stated):
  s1 = log p(x_i | other unmasked image tokens, caption)                      plain masked log-likelihood
  s2 = s1 - log p(x_i | all image tokens masked, caption)                     prior-normalised
  s3 = 1 - max_v p(v | same pass)                                             'model disagrees' confidence baseline
  r_original = s1 - log p(x_i | same image masks, caption masked)             the original Idea 1 formula (red team: should cancel the signal)
  random                                                                      control
Suspicion used for AUROC: -s1, -s2, s3, -r_original, random (higher = more suspicious).
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import core, common                                            # noqa: E402
from exp_p2.scoring import (Spec, masked_logprobs, UniScorer, IMG_LO, IMG_HI, IMG_VOCAB)   # noqa: E402

SEED = 20261028
K = 8
GRID, PATCH, SWAP_FRAC = 32, 8, 0.15
JPEG_Q, NOISE_SIGMA = 10, 0.1
MEM_FRAC, MAX_GPU_USED_MIB = 0.75, 10750.0    # safeguards after the 2026-10-27 crash (see main)
CORRS = ("swap", "patch", "jpeg", "noise")
SCORES = ("s1", "s2", "s3", "r_original", "random")
EXAMPLE_CORR = ("swap", "patch", "jpeg", "noise", "swap", "patch")      # fixed before the run: example j uses item j and this corruption
CONFIG = dict(probe="probe2", n_items=200, seed=SEED, K=K, corruptions=list(CORRS), swap_frac=SWAP_FRAC, patch=PATCH, jpeg_quality=JPEG_Q,
              noise_sigma=NOISE_SIGMA, tok_range=[5, 32], resolution=512, duty=0.5, example_rule=list(EXAMPLE_CORR),
              scoring="fp32 log-softmax of bf16 logits restricted to the image vocabulary; batch 4; backbone eval bf16")


def corrupt(name: str, sc: UniScorer, pil512, clean: np.ndarray, rng: np.random.Generator):
    """Returns (codes, pixel image shown for pixel-level corruptions or None)."""
    if name == "swap":
        return core.token_swap(clean, SWAP_FRAC, IMG_VOCAB, rng), None
    if name == "patch":
        return core.patch_occlusion(clean, GRID, PATCH, IMG_VOCAB, rng), None
    from PIL import Image
    if name == "jpeg":
        buf = io.BytesIO()
        pil512.save(buf, format="JPEG", quality=JPEG_Q)
        buf.seek(0)
        img = Image.open(buf).convert("RGB")
    elif name == "noise":
        a = np.asarray(pil512, dtype=np.float32) / 255.0
        a = np.clip(a + rng.normal(0.0, NOISE_SIGMA, size=a.shape).astype(np.float32), 0.0, 1.0)
        img = Image.fromarray(np.rint(a * 255.0).astype(np.uint8))
    else:
        raise ValueError(name)
    return sc.encode(img), img


def per_token_scores(sc: UniScorer, cap_tok: list[int], codes: np.ndarray, groups: np.ndarray, lp0_true: np.ndarray) -> dict:
    """lp0_true [1024]: log p(x_i | all image masked, caption) of this image's codes (from the shared prior pass)."""
    st = sc.build(cap_tok, codes)
    base, cap, img = st["base"], st["cap_pos"], st["img_pos"]
    masks = core.masks_from_groups(groups, K)
    specs, plan = [], []
    for m in masks:
        pos = img[torch.as_tensor(m, device=img.device)]
        specs.append(Spec(pos, IMG_LO, IMG_HI))
        plan.append(("main", m))
        specs.append(Spec(pos, IMG_LO, IMG_HI, extra=cap))
        plan.append(("capmask", m))
    s1 = np.zeros(sc.L_I)
    s3 = np.zeros(sc.L_I)
    s_cm = np.zeros(sc.L_I)
    for (kind, m), sp, lp in zip(plan, specs, masked_logprobs(sc.logits_fn(st), base, specs)):
        tgt = (base[sp.pos] - IMG_LO)
        v = lp.gather(1, tgt[:, None])[:, 0].cpu().numpy()
        if kind == "main":
            s1[m] = v
            s3[m] = 1.0 - lp.max(dim=1).values.exp().cpu().numpy()
        else:
            s_cm[m] = v
    s2 = s1 - lp0_true
    return dict(s1=s1, s2=s2, s3=s3, r_original=s1 - s_cm)


def suspicion(sc_: dict, rand: np.ndarray) -> dict:
    return dict(s1=-sc_["s1"], s2=-sc_["s2"], s3=sc_["s3"], r_original=-sc_["r_original"], random=rand)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-PROBE-02")
    ap.add_argument("--soft-minutes", type=float, default=12.5)
    ap.add_argument("--duty", type=float, default=CONFIG["duty"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--n", type=int, default=CONFIG["n_items"])
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    from exp001.runtools import Duty, Deadline, EXIT_DONE, EXIT_MORE_WORK
    dl, duty = Deadline(a.soft_minutes), Duty(a.duty)
    run = common.init_run(a.run_id, dict(CONFIG, n_items=a.n, duty=a.duty))
    rows_path = run / "items.jsonl"
    done = {r["idx"] for r in common.read_jsonl(rows_path)}
    if len(done) >= a.n:
        print("complete")
        return EXIT_DONE
    (run / "arrays").mkdir(exist_ok=True)
    (run / "examples").mkdir(exist_ok=True)

    # Safeguards added after the 2026-10-27 20:20 crash (bugcheck 0x116 with GPU memory full; approved by Shlok 21:20):
    # cap this process at 75% of GPU memory so an over-allocation raises OutOfMemoryError instead of filling the card.
    torch.cuda.set_per_process_memory_fraction(MEM_FRAC)
    t_load = time.perf_counter()
    net = common.load_net()
    sc = UniScorer(net)
    load_s = time.perf_counter() - t_load
    sel_path = run / "selection.json"
    if sel_path.exists():
        sel = json.loads(sel_path.read_text(encoding="utf8"))
    else:
        sel = dict(items=common.select_items(a.n, SEED, lambda c: len(sc.caption_ids(c)), tuple(CONFIG["tok_range"])))
        sel_path.write_text(json.dumps(sel, indent=1), encoding="utf8")
    items = sel["items"]
    if not (run / "selfcheck.json").exists():
        chk = sc.selfcheck(common.load_image(items[0]["image_id"]), items[0]["caption"])
        (run / "selfcheck.json").write_text(json.dumps(chk, indent=1), encoding="utf8")
        print("selfcheck", chk)
        if not (chk.get("ids_equal") and chk.get("modality_equal") and chk.get("image_tokens_frac_equal", 0) >= 0.99):
            print("SELF-CHECK FAILED", file=sys.stderr)
            return 2
    common.append_jsonl(run / "chunks.jsonl", dict(event="chunk_start", t=time.time(), load_s=load_s, done=len(done), mem=common.mem_status(), gpu=common.gpu_state()))

    n_new = 0
    for i in range(a.n):
        if i in done:
            continue
        if dl.reached(margin_s=45):
            common.append_jsonl(run / "chunks.jsonl", dict(event="soft_deadline", t=time.time(), remaining=a.n - len(done) - n_new))
            return EXIT_MORE_WORK
        free_b, total_b = torch.cuda.mem_get_info()                     # whole-GPU, all processes
        if (total_b - free_b) / 2**20 > MAX_GPU_USED_MIB:
            common.append_jsonl(run / "chunks.jsonl", dict(event="gpu_memory_stop", t=time.time(), used_mib=(total_b - free_b) / 2**20))
            print(f"STOP: whole-GPU memory {(total_b - free_b) / 2**20:.0f} MiB > {MAX_GPU_USED_MIB}", file=sys.stderr)
            return EXIT_MORE_WORK
        t0 = time.perf_counter()
        torch.cuda.reset_peak_memory_stats()
        it = items[i]
        cap_tok = sc.caption_ids(it["caption"])
        pil = sc.preprocess(common.load_image(it["image_id"]))
        clean = sc.encode(pil)
        g8 = core.complementary_groups(sc.L_I, K, np.random.default_rng([SEED, i, 99]))
        # prior pass: every image token masked, caption visible (independent of the image content); gathered per corruption below
        st0 = sc.build(cap_tok, clean)
        lp_all = next(iter(masked_logprobs(sc.logits_fn(st0), st0["base"], [Spec(st0["img_pos"], IMG_LO, IMG_HI)])))      # [1024, 16384] fp32
        row = dict(idx=i, image_id=it["image_id"], caption=it["caption"], corr={})
        arrays = dict(clean=clean.astype(np.int16))
        recon = {}
        for ci, name in enumerate(CORRS):
            rng = np.random.default_rng([SEED, i, ci])
            cc, pix = corrupt(name, sc, pil, clean, rng)
            z = core.corrupted_mask(clean, cc)
            lp0 = lp_all.gather(1, torch.as_tensor(cc, device=lp_all.device)[:, None])[:, 0].cpu().numpy()
            s = per_token_scores(sc, cap_tok, cc, g8, lp0)
            rnd = np.random.default_rng([SEED, i, 50 + ci]).random(sc.L_I)
            sus = suspicion(s, rnd)
            n_c = int(z.sum())
            au = {k: (core.auroc(v, z) if 5 <= n_c <= sc.L_I - 5 else float("nan")) for k, v in sus.items()}
            row["corr"][name] = dict(n_corrupted=n_c, frac=n_c / sc.L_I, auroc=au, mean_s1_clean=float(s["s1"][~z].mean()),
                                     mean_s1_corrupted=float(s["s1"][z].mean()) if n_c else float("nan"))
            for k in ("s1", "s2", "s3", "r_original"):
                arrays[f"{name}_{k}"] = s[k].astype(np.float32)
            arrays[f"{name}_codes"] = cc.astype(np.int16)
            arrays[f"{name}_z"] = z
            if i < 6 and name == EXAMPLE_CORR[i]:
                pix_show = pix if pix is not None else sc.decode(cc)
                pix_show.save(run / "examples" / f"ex{i}_{name}_corrupted.png")
                pil.save(run / "examples" / f"ex{i}_{name}_original.png")
                sc.decode(clean).save(run / "examples" / f"ex{i}_{name}_vqrecon.png")
        buf = io.BytesIO()
        np.savez_compressed(buf, **arrays)
        (run / "arrays" / f"item{i:04d}.npz").write_bytes(buf.getvalue())
        torch.cuda.synchronize()
        busy = time.perf_counter() - t0
        row.update(seconds=busy, peak_gb=torch.cuda.max_memory_allocated() / 1e9, free_ram_gb=common.mem_status()["free_ram_gb"])
        del lp_all
        common.append_jsonl(rows_path, row)
        n_new += 1
        duty.after_unit(busy)
        if a.limit and n_new >= a.limit:
            return EXIT_DONE if len(done) + n_new >= a.n else EXIT_MORE_WORK
    common.append_jsonl(run / "chunks.jsonl", dict(event="complete", t=time.time()))
    return EXIT_DONE


if __name__ == "__main__":
    sys.exit(main())
