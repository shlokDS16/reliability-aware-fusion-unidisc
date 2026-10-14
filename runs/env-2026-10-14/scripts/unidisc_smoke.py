"""C1 smoke test for UniDisc (interleaved 1.4B): (a) joint text+image generation with the official maskgit sampler,
(b) per-position marginals on a partially masked interleaved state, (c) forward timing / peak VRAM at batch 1, 4, 8,
(ii) a custom commit-order helper with a functional test. Run: python unidisc_smoke.py [--stage a,b,c,d] [--res 1024].
Writes runs/env-2026-10-14/smoke_unidisc/* and merges timing.json (section 'unidisc')."""
import argparse, json, os, sys, time, copy
from common import *  # noqa
import unidisc_setup as U
import torch, numpy as np
import torch.nn.functional as F
from PIL import Image

DEV = "--dev-random" in sys.argv   # plumbing test with random weights; outputs go to _dev/ and are meaningless
SU = OUT / "smoke_unidisc" / ("_dev" if DEV else ""); SU.mkdir(parents=True, exist_ok=True)
PROMPT = "a photo of a red bicycle leaning against a brick wall"   # fixed prompt (smoke test only)
N_TXT = 32                                                       # masked text tokens generated jointly with the image


def patch_attention():
    """Compat patch (Windows, no triton): the repo calls torch flex_attention with a block mask built from `sample_ids`.
    For one document per row (sample_ids all 0, no padding) that mask is full attention, so use SDPA instead; the
    eager flex_attention fallback would materialise B*H*L*L scores. Equivalence is checked in stage `d` (flex_vs_sdpa)."""
    import models.dit as dit, model_eval
    from torch.nn.functional import scaled_dot_product_attention as sdpa
    dit.flex_attention = lambda q, k, v, block_mask=None, **kw: sdpa(q, k, v)
    model_eval.get_interleaved_block_mask = lambda *a, **k: True  # sentinel: dit.Attention maps True -> block_mask=None


def build_state(model, cfg, res, prompt=PROMPT, n_txt=N_TXT, joint=True):
    """Same construction as the official demo (demo/inference.py) for 'text with <m> mask tokens + <image>': the user turn is
    `prompt` followed by n_txt mask tokens ('<m>' = mask id 32000), the assistant turn is a blank image whose tokens are masked.
    Row layout: <s> system </s><s> prompt <m>*n_txt </s><s> ' ' <image>(id 811) [HxW/256 image tokens] </s>.
    joint=True: only the prompt (and system prompt / markers) are observed; the n_txt text tokens AND all image tokens are masked."""
    from demo.inference_utils import messages_to_batch
    tok = model.tokenizer
    if "<m>" not in {x.content for x in tok.added_tokens_decoder.values()}:   # demo/inference.py adds this mask string token
        tok.add_special_tokens({"additional_special_tokens": ["<m>"]}, replace_additional_special_tokens=False)
    assert len(tok) - 1 == model.mask_index
    msgs = [dict(type="text", text=prompt + " " + "<m>" * n_txt, role="user"),
            dict(type="image_url", image_url=Image.new("RGB", (res, res), (0, 0, 0)), role="assistant")]
    b = messages_to_batch(cfg, tok, model, msgs, resolution=res)
    ids, mod = b["input_ids"], b["modality"]
    assert (b["sample_ids"] == 0).all() and b["attention_mask"].all(), "single-document rows expected (see patch_attention)"
    bos = (ids[0] == tok.bos_token_id).nonzero().flatten().tolist()
    img_pos = (mod[0] == 1).nonzero().flatten(); i0, i1 = int(img_pos[0]), int(img_pos[-1]) + 1
    marker = int((ids[0] == 811).nonzero().flatten()[-1])         # '<image>' marker token (id 811) before the image tokens
    txt_masked = ((ids[0] == model.mask_index) & (mod[0] == 0)).nonzero().flatten()
    assert txt_masked.numel() == n_txt, txt_masked.numel()
    unmask = torch.ones_like(ids, dtype=torch.bool)
    unmask[0, i0:i1] = False                                       # image tokens masked
    if joint:
        unmask[0, txt_masked] = False                              # the <m> text positions masked (already mask id in x0)
    x0 = ids.clone()
    layout = dict(length=ids.shape[1], bos_positions=bos, masked_text_positions=[int(txt_masked[0]), int(txt_masked[-1])], image_marker_position=marker,
                  image_positions=[i0, i1 - 1], n_image_tokens=i1 - i0, eos_position=ids.shape[1] - 1, n_observed=int(unmask.sum()), n_masked=int((~unmask).sum()),
                  image_token_id_offset=int(cfg.data.img_token_shift), text_vocab_size=int(model.text_vocab_size), mask_index=int(model.mask_index),
                  image_vocab_size=int(model.image_vocab_size), total_vocab=int(model.vocab_size),
                  special={"bos": tok.bos_token_id, "eos": tok.eos_token_id, "pad": tok.pad_token_id, "image_marker": 811, "mask": int(model.mask_index)})
    return dict(x0=x0, unmask=unmask, modality=mod, sample_ids=b["sample_ids"], attention_mask=b["attention_mask"], layout=layout)


def prior(model, st):
    x = torch.full_like(st["x0"], model.mask_index)
    return torch.where(st["unmask"], st["x0"], x)


@torch.no_grad()
def marginals_raw(model, x, st, return_log=False):
    """p(x^i | s) without guidance. model.forward = backbone + SUBS parameterisation: masked text positions are
    softmax over the text vocab (ids 0..32000 with the mask id forced out), masked image positions over the 16384 image ids
    (32001..48384); observed positions are one-hot on the observed token."""
    lp = model.forward(x=x, sigma=None, modality=st["modality"], sample_ids=st["sample_ids"], block_mask=True)
    return lp if return_log else lp.exp()


@torch.no_grad()
def marginals_guided(model, x, st, t):
    """Marginals exactly as the sampler sees them (classifier-free guidance applied if config.eval.cfg > 0 and something is observed):
    (1+w)*logit_cond - w*logit_uncond with w = cfg*(1-t); the unconditional pass replaces every observed token by the mask id."""
    return model._ddpm_forward(x, torch.full((x.shape[0], 1), float(t), device=x.device), None, x0=st["x0"], x0_unmask=st["unmask"],
                               modality=st["modality"], sample_ids=st["sample_ids"], block_mask=True)


@torch.no_grad()
def ordered_commit(model, st, order, k_per_step, guided=False, seed=0, trace=None):
    """Custom commit order for UniDisc. order: LongTensor of positions (all currently masked) in commit order; k_per_step: ints.
    One network call per step; the chosen positions are sampled from their marginals (multinomial, temperature 1, no top-p);
    all other positions stay masked. guided=True uses the sampler's CFG marginals (adds the unconditional pass)."""
    g = torch.Generator(device=st["x0"].device).manual_seed(seed)
    x = prior(model, st); pos = 0; n_total = int(order.numel())
    for k in k_per_step:
        t = 1.0 - pos / n_total
        p = marginals_guided(model, x, st, t) if guided else marginals_raw(model, x, st)
        idx = order[pos:pos + k].to(x.device); pos += k
        x[:, idx] = torch.multinomial(p[0, idx].float(), 1, generator=g).squeeze(-1)[None]
        if trace is not None:
            trace.append(sorted((x[0] != model.mask_index).nonzero().flatten().tolist()))
    return x


def decode(model, x, st):
    """Split a final token row into text string and PIL image using the repo's own decoders."""
    from unidisc.tokenizers.image_tokenizers import decode_latents
    from image_utils import Im
    mod = st["modality"][0]; tok = model.tokenizer
    L = st["layout"]
    txt_ids = x[0, :L["image_positions"][0]][mod[:L["image_positions"][0]] == 0]
    text = tok.decode(txt_ids[txt_ids != tok.pad_token_id], skip_special_tokens=False)
    a0, a1 = L["masked_text_positions"]
    gen_text = tok.decode(x[0, a0:a1 + 1], skip_special_tokens=False)
    img_ids = x[0, L["image_positions"][0]:L["image_positions"][1] + 1] - L["text_vocab_size"]
    img_ids = img_ids.clamp(0, L["image_vocab_size"] - 1)
    img = decode_latents(model.config, model.get_vae(), img_ids[None])
    return text, gen_text, Im(img[0]).pil


def stage_a(model, cfg, res, seed):
    st = build_state(model, cfg, res, joint=True)
    (SU / f"layout_{res}px.json").write_text(json.dumps(st["layout"], indent=2))
    rec = {}
    orig_decode = model.decode_sampling
    def grab(x, *a, **k):   # keep the raw final tokens; the repo's decode_sampling needs a Linux font path (text-on-image visualisation), we decode ourselves
        rec["x"] = x.clone(); return [], []
    model.decode_sampling = grab
    torch.manual_seed(seed); np.random.seed(seed)
    torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize(); t0 = time.time()
    model._sample(text_only=False, num_steps=int(cfg.sampling.steps), batch_size_per_gpu=1, example_batch=dict(input_ids=st["x0"], attention_mask=st["attention_mask"]),
                  sample_batch_idx=0, modality=st["modality"], sample_ids=st["sample_ids"], allow_interleaved_conditional=True,
                  x0_unmask=st["unmask"], x0=st["x0"])
    torch.cuda.synchronize(); secs = time.time() - t0
    model.decode_sampling = orig_decode
    x = rec["x"]
    text, gen_text, img = decode(model, x, st)
    img.save(SU / f"joint_image_{res}px.png"); (SU / f"joint_text_{res}px.txt").write_text(f"PROMPT: {PROMPT}\nGENERATED({N_TXT} masked text tokens, positions {st["layout"]["masked_text_positions"]}): {gen_text}\nFULL ROW TEXT: {text}\n", encoding="utf-8")
    torch.save(dict(x=x.cpu(), x0=st["x0"].cpu(), unmask=st["unmask"].cpu()), SU / f"joint_tokens_{res}px.pt")
    out = dict(resolution=res, seed=seed, steps=int(cfg.sampling.steps), sampler=cfg.sampling.predictor, cfg_scale=float(cfg.eval.cfg), maskgit_r_temp=float(cfg.eval.maskgit_r_temp),
               seconds=secs, peak_alloc_gb=torch.cuda.max_memory_allocated() / 1e9, generated_text=gen_text, n_masked_after=int((x == model.mask_index).sum()), image_file=f"joint_image_{res}px.png")
    return out


def stage_b(model, cfg, res):
    st = build_state(model, cfg, res, joint=True); L = st["layout"]
    x = prior(model, st)
    # partially masked: reveal a random 25% of the (initially masked) text+image positions from a reference row if available
    ref = SU / f"joint_tokens_{res}px.pt"
    if ref.exists():
        full = torch.load(ref, weights_only=True)["x"].to(x.device)
        g = torch.Generator(device=x.device).manual_seed(0)
        reveal = (torch.rand(x.shape, device=x.device, generator=g) < 0.25) & (~st["unmask"])
        x = torch.where(reveal, full, x); src = "revealed 25% of masked positions from the stage-a sample"
    else:
        src = "only the prompt observed (stage-a sample not available)"
    p = marginals_raw(model, x, st).float()
    m = x == model.mask_index; txt = st["modality"] == 0; img = ~txt
    V = L["text_vocab_size"]
    def stats(sel):
        q = p[sel]
        return dict(n=int(sel.sum()), mass_on_text_ids=float(q[:, :V].sum(-1).mean()), mass_on_image_ids=float(q[:, V:].sum(-1).mean()), mass_on_mask_id=float(q[:, model.mask_index].max()),
                    mean_top1=float(q.max(-1).values.mean()), mean_entropy_nats=float(-(q * q.clamp_min(1e-30).log()).sum(-1).mean()))
    res_ = dict(state=src, shape=list(p.shape), dtype_returned="bfloat16 log-probs from model.forward (cast to float here)", vocab=L["total_vocab"], text_vocab=V, image_vocab=L["image_vocab_size"],
                mask_token_id=L["mask_index"], image_token_id_offset=L["image_token_id_offset"], n_masked=int(m.sum()),
                masked_text=stats(m & txt), masked_image=stats(m & img),
                observed_are_onehot=bool((p[~m].max(-1).values > 0.999).all()))
    g_ = marginals_guided(model, x, st, 0.5).float()
    res_["guided_cfg_marginals"] = dict(cfg=float(cfg.eval.cfg), t=0.5, shape=list(g_.shape), masked_image_mean_top1=float(g_[m & img].max(-1).values.mean()),
                                         masked_text_mean_top1=float(g_[m & txt].max(-1).values.mean()))
    (SU / f"marginals_summary_{res}px.json").write_text(json.dumps(res_, indent=2))
    return res_


def stage_c(model, cfg, res):
    """Forward timing on synthetic rows of the full length (text then image, 50% masked), batch 1/4/8, plain and CFG (=2x batch)."""
    out = {}
    for tag, n_img in (("L1536_512px", 1024), ("L5120_1024px", 4096)):
        n_txt = 1024 if n_img == 4096 else 512
        L = n_txt + n_img
        for B in (1, 4, 8):
            for guided in (False, True):
                key = f"{tag}_batch{B}_{'cfg_double_batch' if guided else 'plain'}"
                Beff = 2 * B if guided else B
                def run():
                    torch.cuda.empty_cache()
                    mod = torch.cat([torch.zeros(n_txt), torch.ones(n_img)]).long().cuda()[None].repeat(Beff, 1)
                    x = torch.where(mod == 0, torch.randint(0, 32000, (Beff, L), device="cuda"), torch.randint(32001, 48385, (Beff, L), device="cuda"))
                    x = torch.where(torch.rand(Beff, L, device="cuda") < 0.5, x, torch.full_like(x, model.mask_index))
                    sid = torch.zeros(Beff, L, dtype=torch.long, device="cuda")
                    def fwd():
                        with torch.no_grad():
                            model.forward(x=x, sigma=None, modality=mod, sample_ids=sid, block_mask=True)
                    r = timeit_cuda(fwd, 1, 3); r.update(seq_len=L, effective_batch=Beff); return r
                out[key] = try_oom(run)
                torch.cuda.empty_cache()
    return out


def stage_d(model, cfg, res):
    """Functional checks: (1) flex_attention(block_mask from sample_ids) == SDPA for single-document rows; (2) ordered_commit respects order; (3) bf16 forward is finite."""
    from torch.nn.attention.flex_attention import flex_attention, create_block_mask
    from model_utils import _interleaved_attn_mask
    out = {}
    q, k, v = (torch.randn(1, 4, 384, 64, device="cuda", dtype=torch.float32) for _ in range(3))
    sid = torch.zeros(1, 384, dtype=torch.long, device="cuda")
    bm = create_block_mask(_interleaved_attn_mask(sid), B=1, H=None, Q_LEN=384, KV_LEN=384, device="cuda")
    a = flex_attention(q, k, v, block_mask=bm); b = F.scaled_dot_product_attention(q, k, v)
    out["flex_vs_sdpa_max_abs_diff"] = float((a - b).abs().max())
    st = build_state(model, cfg, 256, joint=True)
    masked = (~st["unmask"][0]).nonzero().flatten()
    order = masked[torch.randperm(masked.numel(), generator=torch.Generator().manual_seed(0), device="cpu").to(masked.device)][:48]
    trace = []; xo = ordered_commit(model, st, order, [4] * 12, guided=False, trace=trace)
    exp = [sorted(set(st["unmask"][0].nonzero().flatten().tolist()) | set(order[:4 * (i + 1)].tolist())) for i in range(12)]
    out["ordered_commit_sets_match_prescribed"] = all(t == e for t, e in zip(trace, exp))
    out["ordered_commit_modalities_of_first_8_committed"] = [int(st["modality"][0, i]) for i in order[:8]]
    lp = marginals_raw(model, prior(model, st), st)
    out["forward_finite"] = bool(torch.isfinite(lp.float()).all())
    return out


def stage_e(model, cfg, res):
    """CFG switch test: count network calls / batch sizes in the sampler's guided marginal for eval.cfg = 3.0, 0.0, null."""
    from omegaconf import open_dict
    st = build_state(model, cfg, 256, joint=True); x = prior(model, st); orig_cfg = float(cfg.eval.cfg)
    calls = []; orig = model.forward
    def spy(*a, **k):
        calls.append(list(k["x"].shape)); return orig(*a, **k)
    model.forward = spy
    out = {}
    try:
        for name, w in (("cfg_3.0", 3.0), ("cfg_0.0", 0.0), ("cfg_null", None)):
            with open_dict(model.config): model.config.eval.cfg = w
            calls.clear(); p = marginals_guided(model, x, st, 0.5).float()
            out[name] = dict(forward_calls_x_shapes=list(calls), max_abs_diff_to_unguided=float((p - marginals_raw(model, x, st).float()).abs().max()))
    finally:
        model.forward = orig
        with open_dict(model.config): model.config.eval.cfg = orig_cfg
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stage", default="a,b,c,d"); ap.add_argument("--res", type=int, default=1024)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--fp32", action="store_true", help="keep fp32 weights (bf16 autocast) instead of casting to bf16")
    ap.add_argument("--steps", type=int, default=None); ap.add_argument("--dev-random", action="store_true"); a = ap.parse_args()
    extra = ["eval.visualize_sample=false"]
    if a.steps: extra += [f"sampling.steps={a.steps}", f"sampling.max_sampling_steps={a.steps}"]
    cfg = U.make_config(extra, load_ckpt=not a.dev_random); patch_attention()
    t0 = time.time(); model, cfg = U.build_model(cfg, bf16=not a.fp32); load_s = time.time() - t0
    info = dict(env=env_info(), load_s=load_s, weights_dtype=str(next(model.backbone.parameters()).dtype), n_params=sum(p.numel() for p in model.backbone.parameters()),
                vram_after_load_gb=torch.cuda.memory_allocated() / 1e9, free_system_commit_gb_after_load=commit_free_gb())
    import gc; gc.collect(); torch.cuda.empty_cache(); info['free_system_commit_gb_after_gc'] = commit_free_gb(); print(info, flush=True)
    res = {}
    tag = f"{'fp32' if a.fp32 else 'bf16'}_{a.res}px"
    for s in a.stage.split(","):
        import gc; gc.collect(); torch.cuda.empty_cache()   # the caching allocator's reserved blocks count as system commit
        info.setdefault("free_commit_gb_before_stage", {})[s] = wait_commit(6.0)
        res[s] = dict(a=stage_a, b=stage_b, c=stage_c, d=stage_d, e=stage_e)[s](model, cfg, a.res, *([a.seed] if s == "a" else []))
        print(s, json.dumps(res[s], indent=1)[:2500], flush=True)
        out = dict(info=info, **res)   # saved after every stage so a later crash keeps earlier results
        (SU / f"smoke_unidisc_{tag}_stages_{a.stage.replace(',', '')}.json").write_text(json.dumps(out, indent=2))
        if not a.dev_random:
            merge_json(OUT / "timing.json", f"unidisc_{tag}", out)

if __name__ == "__main__":
    main()
