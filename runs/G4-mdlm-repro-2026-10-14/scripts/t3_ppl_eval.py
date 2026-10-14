"""T3: MDLM-OWT test perplexity bound, resumable + duty-cycled version (run under tools/gpu_guard.py in 15-minute chunks).

Official pieces used unchanged: Diffusion (backbone=hf_dit, kuleshov-group/mdlm-owt, repo SHA in the output), dataloader.get_dataloaders(valid_seed=seed)
(the repo's shuffled validation DataLoader), Diffusion._loss -> _forward_pass_diffusion (continuous time T=0, loglinear noise, antithetic t within a batch,
SUBS). The Lightning Trainer.validate wrapper of main._ppl_eval is NOT used (it cannot resume); the metric is the same quantity,
val/ppl = exp(sum nll / sum tokens) (Perplexity metric in diffusion.py), accumulated here in float64. _loss is run under torch.autocast(cuda, bf16),
which is what Lightning's precision='bf16' (bf16-mixed) does around validation_step.
Deviations: batch 8 instead of 16 (thermal rule; t is antithetic over 8 sequences instead of 16); the RNG is re-seeded per batch (seed*100000+batch) so a
resumed run draws the same t / masks; loader order = the official shuffled order for this seed.
Checkpoint: one JSON line per batch in t3_batches_<tag>.jsonl (sum_nll, count); resume skips completed batches. Sleeps as long as each batch took.
Usage: python t3_ppl_eval.py --seed 1 [--max-seqs N] [--fp32]
"""
import argparse, itertools, math
from g4_common import *  # noqa

ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--max-seqs", type=int, default=None, help="stated subset: first N sequences of the shuffled order")
ap.add_argument("--fp32", action="store_true")
ap.add_argument("--bs", type=int, default=8)
ap.add_argument("--no-duty", action="store_true")
args = ap.parse_args()
tag = f"seed{args.seed}_{SHIM}{'_fp32' if args.fp32 else ''}{'_n%d' % args.max_seqs if args.max_seqs else ''}_bs{args.bs}"


def main():
    setup_repo_import()
    import contextlib, numpy as np, unittest.mock as um
    import dataloader
    cfg = make_cfg([f"seed={args.seed}"], bs=args.bs)
    tok = dataloader.get_tokenizer(cfg)
    _, valid_ds = dataloader.get_dataloaders(cfg, tok, skip_train=True, valid_seed=cfg.seed)
    n_seq = len(valid_ds.dataset)
    total_batches = math.ceil((min(args.max_seqs, n_seq) if args.max_seqs else n_seq) / args.bs)
    ck = G4 / f"t3_batches_{tag}.jsonl"
    done = [json.loads(l) for l in open(ck)] if ck.exists() else []
    n_done = len(done)
    print(f"{tag}: {n_seq} sequences, {total_batches} batches, {n_done} already done", flush=True)
    if n_done < total_batches:
        model = load_diffusion(cfg, tok)
        model.ema = None            # EMA object holds a copy of the loaded weights; copy_to would be a no-op, so skip the copy
        model.backbone.eval(); model.noise.eval()
        cm = um.patch("torch.cuda.amp.autocast", lambda *a, **k: contextlib.nullcontext()) if args.fp32 else contextlib.nullcontext()
        t_chunk = time.time()
        with cm, torch.no_grad(), open(ck, "a") as fh:
            for bi, batch in enumerate(itertools.islice(valid_ds, total_batches)):
                if bi < n_done:
                    continue
                t0 = time.time()
                torch.manual_seed(cfg.seed * 100000 + bi)
                x0 = batch["input_ids"].to("cuda"); am = batch["attention_mask"].to("cuda")
                with (contextlib.nullcontext() if args.fp32 else torch.autocast("cuda", dtype=torch.bfloat16)):
                    out = model._loss(x0, am)
                row = dict(bi=bi, n=int(x0.shape[0]), sum_nll=float(out.nlls.double().sum()), count=float(out.token_mask.double().sum()))
                fh.write(json.dumps(row) + "\n"); fh.flush()
                done.append(row)
                if (bi + 1) % 200 == 0:
                    s = sum(r["sum_nll"] for r in done); c = sum(r["count"] for r in done)
                    print(f"batch {bi+1}/{total_batches}: running ppl {math.exp(s/c):.4f}", flush=True)
                torch.cuda.synchronize()
                if not args.no_duty:
                    time.sleep(time.time() - t0)
    rows = [json.loads(l) for l in open(ck)]
    assert [r["bi"] for r in rows] == list(range(total_batches)), "checkpoint gap"
    s = np.array([r["sum_nll"] for r in rows]); c = np.array([r["count"] for r in rows])
    nll = s.sum() / c.sum()
    rng = np.random.default_rng(0)
    boots = []
    for _ in range(2000):        # bootstrap over batches (t is stratified within a batch; batches are independent draws)
        i = rng.integers(0, len(s), len(s)); boots.append(math.exp(s[i].sum() / c[i].sum()))
    res = dict(tag=tag, seed=cfg.seed, shim=SHIM, fp32_ablation=args.fp32, ppl=math.exp(nll), nll=nll, n_batches=len(s), batch_size=args.bs,
               n_sequences=int(sum(r["n"] for r in rows)), n_tokens=int(c.sum()), ppl_bootstrap_95=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
               nll_per_batch_sd=float(np.std(s / c, ddof=1)), nll_se=float(np.std(s / c, ddof=1) / math.sqrt(len(s))),
               repo_sha=git_sha(REPO), ckpt=CKPT, env=env_info(), torch=torch.__version__,
               config=dict(T=cfg.T, noise=cfg.noise.type, time_conditioning=cfg.time_conditioning, parameterization=cfg.parameterization,
                           backbone=cfg.backbone, model_length=cfg.model.length, antithetic=cfg.training.antithetic_sampling, sampling_eps=cfg.training.sampling_eps))
    jdump(res, G4 / f"t3_ppl_{tag}.json")
    print(json.dumps({k: v for k, v in res.items() if k != "env"}, indent=1))


if __name__ == "__main__":
    main()
    sys.stdout.flush(); sys.stderr.flush(); os._exit(0)   # skip interpreter teardown crash (0xC0000409) seen after results were written
