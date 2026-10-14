"""C2 smoke test: MDLM-OWT through the official repo class (backbone=hf_dit), official sampler, timing, marginals, ordered sampler.
Run: python mdlm_smoke.py [--steps 128] [--skip-ppl]. Writes runs/env-2026-10-14/smoke_mdlm/* and merges timing.json."""
import argparse, json, os, sys, time
from common import *  # noqa
add_shims()
stub_modules("causal_conv1d", "mamba_ssm.ops.selective_scan_interface", "mamba_ssm.ops.triton.layernorm",
             "mamba_ssm.ops.triton.selective_state_update")
import torch, omegaconf, hydra
REPO = THIRD / "mdlm"
sys.path.insert(0, str(REPO))
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
for name, fn in dict(cwd=os.getcwd, device_count=torch.cuda.device_count, eval=eval, div_up=lambda x, y: (x + y - 1) // y).items():
    if not omegaconf.OmegaConf.has_resolver(name):
        omegaconf.OmegaConf.register_new_resolver(name, fn)
import transformers
import diffusion as mdlm_diffusion  # official repo module

SM = OUT / "smoke_mdlm"; SM.mkdir(exist_ok=True)
CKPT = "kuleshov-group/mdlm-owt"


def build(steps=128, bs=1):
    with hydra.initialize_config_dir(config_dir=str(REPO / "configs"), version_base=None):
        cfg = hydra.compose(config_name="config", overrides=[
            "mode=sample_eval", f"loader.batch_size={bs}", f"loader.eval_batch_size={bs}", "loader.num_workers=0",
            "data=openwebtext-split", "model=small", "parameterization=subs", "backbone=hf_dit", "model.length=1024",
            "time_conditioning=false", f"eval.checkpoint_path={CKPT}", "sampling.predictor=ddpm_cache",
            f"sampling.steps={steps}", f"eval.perplexity_batch_size={bs}", "seed=1"])
    tok = transformers.AutoTokenizer.from_pretrained("gpt2")  # data.tokenizer_name_or_path
    m = mdlm_diffusion.Diffusion(cfg, tokenizer=tok).to("cuda")
    m.ema = None  # == eval.disable_ema, as in main.generate_samples
    m.backbone.eval(); m.noise.eval()
    return cfg, tok, m


def marginals(m, x):
    """p(x^i | s) for every position: exp of Diffusion.forward (SUBS: masked positions get softmax over the 50257 real
    tokens with the mask id forced to -inf; unmasked positions are one-hot on the observed token)."""
    sigma = torch.zeros(x.shape[0], device=x.device)  # time_conditioning=false -> sigma ignored
    with torch.no_grad():
        return m.forward(x, sigma).exp()


def marginals_fp32(m, x):
    """Same marginals with every autocast in the model disabled (the DIT blocks and output layer hard-code bf16 autocast, so the default
    marginals are bf16-rounded). Costs more time and memory; use when 1e-2 relative error in p is not acceptable."""
    import contextlib, unittest.mock as um
    sigma = torch.zeros(x.shape[0], device=x.device)
    with torch.no_grad(), um.patch("torch.cuda.amp.autocast", lambda *a, **k: contextlib.nullcontext()):
        return m.forward(x, sigma).exp()


@torch.no_grad()
def ordered_unmask(m, order, k_per_step, x=None, seed=0, trace=None):
    """Custom commit order. order: LongTensor [n] (positions in commit order); k_per_step: ints summing to n.
    Each step: one network call on the current state, sample the chosen positions from their marginals (Gumbel-max in fp32,
    as the official _sample_categorical), leave every other masked position masked."""
    g = torch.Generator(device="cuda").manual_seed(seed)
    x = torch.full((1, 1024), m.mask_index, device="cuda", dtype=torch.long) if x is None else x
    pos = 0
    for k in k_per_step:
        p = marginals(m, x)
        idx = order[pos:pos + k].to("cuda"); pos += k
        gum = 1e-10 - (torch.rand(p[:, idx].shape, device="cuda", generator=g) + 1e-10).log()
        x[:, idx] = (p[:, idx] / gum).argmax(-1)
        if trace is not None:
            trace.append((x != m.mask_index).nonzero()[:, 1].tolist())
    return x


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--steps", type=int, default=128); ap.add_argument("--skip-ppl", action="store_true")
    ap.add_argument("--long-steps", type=int, default=1000); a = ap.parse_args()
    res = dict(env=env_info(), checkpoint=CKPT, repo=str(REPO))
    wait_commit(6.0)
    t0 = time.time(); cfg, tok, m = build(a.steps); res["load_s"] = time.time() - t0
    res["mask_index"] = m.mask_index; res["vocab_size_with_mask"] = m.vocab_size
    res["n_params_backbone"] = sum(p.numel() for p in m.backbone.parameters())
    res["backbone_param_dtype"] = str(next(m.backbone.parameters()).dtype)
    res["sampler_defaults"] = dict(predictor=cfg.sampling.predictor, steps_default_in_repo=128, noise_removal=bool(cfg.sampling.noise_removal),
                                   temperature=None, top_p=None, cfg=None,
                                   gumbel_dtype="float32 (official MDLM repo); the ReMDM repo uses float64 and optional nucleus p")
    # (a) official sampler, one sample L=1024
    torch.manual_seed(1); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
    with torch.no_grad():
        samples = m.restore_model_and_sample(num_steps=a.steps)
    torch.cuda.synchronize(); gen_s = time.time() - t0
    text = tok.batch_decode(samples)
    (SM / "sample_L1024.txt").write_text(text[0], encoding="utf-8")
    torch.save(samples.cpu(), SM / "sample_L1024_tokens.pt")
    res["sample"] = dict(steps=a.steps, shape=list(samples.shape), seconds=gen_s, peak_alloc_gb=torch.cuda.max_memory_allocated() / 1e9,
                         seed=1, text_file="sample_L1024.txt")
    # paper-style T, cost only
    torch.manual_seed(1); torch.cuda.synchronize(); t0 = time.time()
    with torch.no_grad():
        m.restore_model_and_sample(num_steps=a.long_steps)
    torch.cuda.synchronize(); res["sample_long"] = dict(steps=a.long_steps, seconds=time.time() - t0)
    # generative perplexity (gpt2-large, repo evaluator)
    if not a.skip_ppl:
        wait_commit(8.0)
        m.gen_ppl_metric.reset(); torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
        m.compute_generative_perplexity(text); torch.cuda.synchronize()
        res["gen_ppl"] = dict(evaluator=m.gen_ppl_eval_model_name_or_path, value_one_sample=float(m.gen_ppl_metric.compute()),
                              seconds_incl_model_load=time.time() - t0, peak_alloc_gb=torch.cuda.max_memory_allocated() / 1e9,
                              note="single sample; a plumbing check, NOT a measurement of model quality")
        torch.cuda.empty_cache()
    # (b) marginals on a partially masked state
    x = samples.clone()
    keep = torch.rand(x.shape, device="cuda", generator=torch.Generator(device="cuda").manual_seed(0)) < 0.5
    xm = torch.where(keep, x, torch.full_like(x, m.mask_index))
    p = marginals(m, xm); mk = xm == m.mask_index
    res["marginals"] = dict(shape=list(p.shape), dtype=str(p.dtype), n_masked=int(mk.sum()),
                            rowsum_masked_min=float(p[mk].sum(-1).min()), rowsum_masked_max=float(p[mk].sum(-1).max()),
                            mask_id_prob_max=float(p[..., m.mask_index].max()), unmasked_is_onehot=bool((p[~mk].max(-1).values == 1).all()),
                            mean_top1_prob_masked=float(p[mk].max(-1).values.mean()),
                            mean_entropy_nats_masked=float(-(p[mk] * p[mk].clamp_min(1e-30).log()).sum(-1).mean()))
    p32 = marginals_fp32(m, xm)
    res["marginals_fp32_check"] = dict(dtype=str(p32.dtype), rowsum_masked_min=float(p32[mk].sum(-1).min()), rowsum_masked_max=float(p32[mk].sum(-1).max()),
                                       max_abs_diff_vs_bf16=float((p32 - p.float()).abs().max()), top1_agreement_masked=float((p32[mk].argmax(-1) == p[mk].argmax(-1)).float().mean()),
                                       mean_abs_diff_entropy_nats=float(((-(p32[mk] * p32[mk].clamp_min(1e-30).log()).sum(-1)) - (-(p[mk].float() * p[mk].float().clamp_min(1e-30).log()).sum(-1))).abs().mean()))
    xb1 = xm[:1]; tf = timeit_cuda(lambda: marginals_fp32(m, xb1), 2, 5); res["marginals_fp32_check"]["batch1_seconds"] = tf["median_s"]; res["marginals_fp32_check"]["batch1_peak_gb"] = tf["peak_alloc_gb"]
    del p, p32
    # (c) forward timing at L=1024
    tim = {}
    for bs in (1, 8, 32):
        import gc; gc.collect(); torch.cuda.empty_cache(); wait_commit(8.0)   # CUDA allocations are charged to system commit here (setup.md)
        xb = torch.where(torch.rand(bs, 1024, device="cuda") < 0.5, torch.randint(0, 50257, (bs, 1024), device="cuda"),
                         torch.full((bs, 1024), m.mask_index, device="cuda"))
        sg = torch.zeros(bs, device="cuda")

        def full():
            with torch.no_grad():
                m.forward(xb, sg)

        def bb():
            with torch.no_grad():
                m.backbone(xb, sg)
        tim[f"batch{bs}_full_forward"] = try_oom(lambda: timeit_cuda(full, 2, 5))
        torch.cuda.empty_cache()
        tim[f"batch{bs}_backbone_only"] = try_oom(lambda: timeit_cuda(bb, 2, 5))
        del xb
    res["timing_forward_L1024"] = tim
    # (ii) functional test of a custom commit order (64 of 1024 positions, 16 steps x 4); not an experiment
    order = torch.randperm(1024, generator=torch.Generator().manual_seed(0))[:64]
    trace = []
    out = ordered_unmask(m, order, [4] * 16, trace=trace)
    exp_sets = [sorted(order[:4 * (i + 1)].tolist()) for i in range(16)]
    res["ordered_sampler_test"] = dict(steps=16, k=4, committed_sets_match_prescribed=all(sorted(t) == e for t, e in zip(trace, exp_sets)),
                                       n_unmasked_end=int((out != m.mask_index).sum()))
    (SM / "smoke_mdlm.json").write_text(json.dumps(res, indent=2))
    merge_json(OUT / "timing.json", "mdlm", dict(forward_L1024=tim, sample=res["sample"], sample_long=res["sample_long"],
                                                   gen_ppl=res.get("gen_ppl"), load_s=res["load_s"]))
    print(json.dumps(res, indent=2)[:3500])


if __name__ == "__main__":
    main()
