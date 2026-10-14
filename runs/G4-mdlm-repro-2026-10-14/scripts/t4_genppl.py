"""T4: generative perplexity sanity check. 16 samples, L=1024, batch 1, ~1000 steps, GPT-2 Large evaluator (official compute_generative_perplexity,
called per sample exactly like main.generate_samples; GPT-2 Large is loaded once through a caching wrapper of AutoModelForCausalLM.from_pretrained, which
does not change numerics). Unigram entropy as in the ReMDM repo (main.py L116-120): entropy (nats) of the token-id histogram of each 1024-token sample, averaged.
Settings (G4_REPO selects the code):
  G4_REPO=mdlm  : official MDLM sampler, ddpm_cache, 1000 steps, no nucleus, fp32 Gumbel  (README sample command)
  G4_REPO=remdm : ReMDM repo code, sampling.sampler=mdlm, ddpm_cache, 1024 steps, nucleus_p=0.9, fp64 Gumbel  (remdm/scripts/mdlm.sh; the setting of ReMDM Table 1 row 'MDLM' with dagger)
Usage: python t4_genppl.py --n 16 --seed 1 [--steps 1000] [--nucleus 1.0]
"""
import argparse, math
from g4_common import *  # noqa
ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=16); ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--steps", type=int, default=None); ap.add_argument("--nucleus", type=float, default=None)
args = ap.parse_args()
which = os.environ.get("G4_REPO", "mdlm")
steps = args.steps or (1000 if which == "mdlm" else 1024)
nucleus = args.nucleus if args.nucleus is not None else (1.0 if which == "mdlm" else 0.9)


def main():
    setup_repo_import()
    import lightning as L, transformers, numpy as np
    import dataloader, diffusion as D
    extra = [f"seed={args.seed}", "eval.perplexity_batch_size=1"]
    if which == "remdm":
        extra += [f"sampling.nucleus_p={nucleus}", "sampling.sampler=mdlm"]
    cfg = make_cfg(extra, bs=1, steps=steps)
    L.seed_everything(cfg.seed)
    tok = dataloader.get_tokenizer(cfg)
    wait_commit(10.0)
    model = load_diffusion(cfg, tok)
    model.gen_ppl_metric.reset()
    if cfg.eval.disable_ema: model.ema = None
    # cache GPT-2 large across the per-sample calls
    _orig = transformers.AutoModelForCausalLM.from_pretrained
    _cache = {}
    def cached(name, *a, **k):
        if name not in _cache: _cache[name] = _orig(name, *a, **k)
        return _cache[name]
    transformers.AutoModelForCausalLM.from_pretrained = cached
    tag = f"{which}_steps{cfg.sampling.steps}_n{args.n}_seed{args.seed}" + (f"_nuc{nucleus}" if which == "remdm" else "")
    ck = G4 / f"t4_samples_{tag}.jsonl"                       # one JSON line per finished sample => resumable
    done = [json.loads(l) for l in open(ck)] if ck.exists() else []
    for i in range(len(done), args.n):
        torch.manual_seed(args.seed * 1000 + i)
        t0 = time.time()
        sample = model.restore_model_and_sample(num_steps=cfg.sampling.steps)
        secs_i = time.time() - t0
        row = sample[0]
        counts = torch.unique(row, return_counts=True, sorted=True)[1]
        ent = torch.special.entr(counts.float() / counts.sum()).sum().item()
        text = tok.batch_decode(row.unsqueeze(0))[0]
        m_before = (model.gen_ppl_metric.mean_value.clone(), model.gen_ppl_metric.weight.clone())
        model.compute_generative_perplexity([text])           # official function, one sample per call, as main.generate_samples
        dv = float(model.gen_ppl_metric.mean_value - m_before[0]); dw = float(model.gen_ppl_metric.weight - m_before[1])
        rec = dict(i=i, text=text, ids=row.tolist(), entropy=ent, secs=secs_i, nll_sum=dv, weight=dw, gen_ppl=math.exp(dv / dw), distinct=int(len(counts)))
        with open(ck, "a") as f: f.write(json.dumps(rec) + chr(10))
        print(f"sample {i}: {secs_i:.1f}s  gen-ppl {rec['gen_ppl']:.2f}  unigram-entropy {ent:.3f}  distinct {rec['distinct']}", flush=True)
        time.sleep(secs_i)                                    # duty cycle ~50%
    done = [json.loads(l) for l in open(ck)]
    texts = [r["text"] for r in done]; ids = [r["ids"] for r in done]; ents = [r["entropy"] for r in done]
    per_sample_ppl = [r["gen_ppl"] for r in done]; secs = [r["secs"] for r in done]
    gen_ppl = math.exp(sum(r['nll_sum'] for r in done) / sum(r['weight'] for r in done))     # = Perplexity.compute() over all samples
    pp = np.array(per_sample_ppl); rng = np.random.default_rng(0)
    lw = []   # bootstrap over samples of the token-weighted metric is not available per sample; report bootstrap of the per-sample geometric/arith mean instead
    boots = [np.exp(np.log(pp[rng.integers(0, len(pp), len(pp))]).mean()) for _ in range(2000)]
    res = dict(repo=which, repo_sha=git_sha(REPO), seed=args.seed, n_samples=args.n, steps=cfg.sampling.steps, predictor=cfg.sampling.predictor,
               nucleus_p=nucleus if which == "remdm" else None, gen_ppl_official_metric=gen_ppl, gen_ppl_per_sample=per_sample_ppl,
               gen_ppl_per_sample_geomean=float(np.exp(np.log(pp).mean())), geomean_bootstrap_95=[float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
               unigram_entropy_mean=float(np.mean(ents)), unigram_entropy_sd=float(np.std(ents, ddof=1)), unigram_entropy_per_sample=ents,
               seconds_per_sample=secs, evaluator=cfg.eval.gen_ppl_eval_model_name_or_path, env=env_info(), shim=SHIM)
    jdump(res, G4 / f"t4_genppl_{tag}.json")
    jdump(dict(texts=texts, token_ids=ids), G4 / f"t4_samples_{tag}.json")
    print(json.dumps({k: v for k, v in res.items() if k not in ("env", "gen_ppl_per_sample", "unigram_entropy_per_sample", "seconds_per_sample")}, indent=1))


if __name__ == "__main__":
    main()
    sys.stdout.flush(); sys.stderr.flush(); os._exit(0)   # skip interpreter teardown crash (0xC0000409) seen after results were written
