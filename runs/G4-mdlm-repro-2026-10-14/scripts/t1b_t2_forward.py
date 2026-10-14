"""T1b (full MDLM forward through independent attention/rotary paths) and T2 (precision decomposition, paired ELBO, fp32 timing).
Needs the tokenised validation set from t3_prep_data.py. Run (always under tools/gpu_guard.py; resumable; duty-cycled 1:1): python t1b_t2_forward.py --stage state|t1b|elbo|timing ; writes t2_<stage>.json (+ .jsonl checkpoints)
All variants are evaluated on IDENTICAL inputs (same x0, same mask / same t draw), so differences are paired.
"""
import argparse, contextlib, importlib.util, math, types, unittest.mock as um
from g4_common import *  # noqa
setup_repo_import()
import torch, torch.nn.functional as F, datasets, transformers
import dataloader, diffusion as D
import flash_attn
from flash_attn import flash_attn_interface as fai
from flash_attn.layers import rotary as rot
from torch.nn.attention import sdpa_kernel, SDPBackend

ap = argparse.ArgumentParser()
ap.add_argument("--n-state", type=int, default=32)
ap.add_argument("--n-elbo", type=int, default=2000)
ap.add_argument("--stage", required=True, choices=["state", "t1b", "elbo", "timing", "engineer"])
ap.add_argument("--elbo-bs", type=int, default=8)
args = ap.parse_args()

dev = "cuda"
cfg = make_cfg()
tok = dataloader.get_tokenizer(cfg)
valid = datasets.load_from_disk(str(OWT_CACHE / "openwebtext-valid_validation_bs1024_wrapped.dat")).with_format("torch")
perm = torch.randperm(len(valid), generator=torch.Generator().manual_seed(1))
wait_commit(8.0)
m = load_diffusion(cfg, tok); m.ema = None; m.backbone.eval(); m.noise.eval()
bm = sys.modules[type(m.backbone).__module__]       # the HF remote-code module (modeling_mdlm)
MASK = m.mask_index
res = dict(env=env_info(), shim=SHIM, shim_file=str(rot.__file__), repo_sha=git_sha(REPO), ckpt=CKPT, n_valid_sequences=len(valid))

# v1 rotary (original shim) loaded under another name, for the A/B
_spec = importlib.util.spec_from_file_location("rot_v1", str(G4 / "scripts" / "shim_v1" / "flash_attn" / "layers" / "rotary.py"))
rot_v1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(rot_v1)
rot_v2_fn = rot.apply_rotary_emb_qkv_
if SHIM == "v1":
    rot_v2_fn = None


@contextlib.contextmanager
def no_autocast():
    with um.patch("torch.cuda.amp.autocast", lambda *a, **k: contextlib.nullcontext()):
        yield


@contextlib.contextmanager
def patched(obj, name, new):
    old = getattr(obj, name); setattr(obj, name, new)
    try: yield
    finally: setattr(obj, name, old)


def final_layer_fp32(self, x, c):                    # variant B: output projection and its modulation in fp32 on the bf16 trunk
    with torch.cuda.amp.autocast(enabled=False):
        x = x.float(); c = c.float()
        shift, scale = self.adaLN_modulation(c)[:, None].chunk(2, dim=2)
        x = bm.modulate_fused(self.norm_final(x), shift, scale)
        return self.linear(x)


orig_attn = fai.flash_attn_varlen_qkvpacked_func
def attn_fp32(qkv, cu, max_s, dropout_p=0.0, softmax_scale=None, causal=False, **kw):   # variant G: attention in fp32 on bf16 inputs
    return orig_attn(qkv.float(), cu, max_s, dropout_p, softmax_scale, causal).to(qkv.dtype)


def attn_math_backend(qkv, cu, max_s, dropout_p=0.0, softmax_scale=None, causal=False, **kw):   # T1b path M: forced SDPA MATH backend, explicit scale
    b = qkv.shape[0] // max_s; q, k, v = qkv.view(b, max_s, 3, *qkv.shape[2:]).unbind(2)
    with sdpa_kernel(SDPBackend.MATH):
        o = F.scaled_dot_product_attention(q.transpose(1, 2).contiguous(), k.transpose(1, 2).contiguous(), v.transpose(1, 2).contiguous(),
                                           attn_mask=None, dropout_p=0.0, is_causal=False, scale=q.shape[-1] ** -0.5)
    return o.transpose(1, 2).reshape(b * max_s, *o.shape[1:2], o.shape[-1]).contiguous().view(b * max_s, q.shape[2], q.shape[3])


def attn_explicit(qkv, cu, max_s, dropout_p=0.0, softmax_scale=None, causal=False, **kw):    # T1b path X: explicit float64 softmax(QK^T/sqrt(d))V
    b = qkv.shape[0] // max_s; q, k, v = [t.double() for t in qkv.view(b, max_s, 3, *qkv.shape[2:]).unbind(2)]
    s = torch.einsum("bqhd,bkhd->bhqk", q, k) * (q.shape[-1] ** -0.5)
    o = torch.einsum("bhqk,bkhd->bqhd", s.softmax(-1), v)
    return o.reshape(b * max_s, q.shape[2], q.shape[3]).to(qkv.dtype)


def rotary_complex(qkv, cos, sin, cos_k=None, sin_k=None, interleaved=False, seqlen_offsets=0):    # independent: complex multiplication in float64
    rd2 = cos.shape[-1]; out = []
    for i in range(2):
        x = qkv[:, :, i].double()
        z = torch.complex(x[..., :rd2], x[..., rd2:2 * rd2]) * torch.complex(cos.double(), sin.double())[None, :, None, :]
        out.append(torch.cat([z.real, z.imag, x[..., 2 * rd2:]], -1).to(qkv.dtype))
    return torch.stack([out[0], out[1], qkv[:, :, 2]], dim=2)


def subs(lg, xt):          # the repo's own SUBS function (in-place on its argument)
    return m._subs_parameterization(lg.clone(), xt)


class Variant:
    """name -> (context-manager factory, normaliser dtype). logp(x, ...) returns SUBS log-probs [B,L,V]."""
    def __init__(self, name, patches, norm32, autocast_off=False, model=None, desc=""):
        self.name, self.patches, self.norm32, self.autocast_off, self.model, self.desc = name, patches, norm32, autocast_off, model, desc

    @contextlib.contextmanager
    def ctx(self):
        with contextlib.ExitStack() as st:
            if self.autocast_off: st.enter_context(no_autocast())
            for p in self.patches: st.enter_context(p())
            yield

    def logits(self, x):
        net = self.model if self.model is not None else m.backbone
        sigma = torch.zeros(x.shape[0], device=x.device, dtype=torch.float64 if self.model is not None else torch.float32)
        with self.ctx(), torch.no_grad():
            return net(x, sigma)

    def logp(self, x):
        lg = self.logits(x)
        if self.norm32 and lg.dtype != torch.float64: lg = lg.float()
        with torch.no_grad():
            return subs(lg, x)

    def forward_for_loss(self, x, sigma):     # replaces Diffusion.forward inside the official _forward_pass_diffusion
        return self.logp(x)


P = lambda obj, name, new: (lambda: patched(obj, name, new))
V_A = Variant("A_official_bf16", [], False, desc="bf16 trunk + bf16 output layer + SUBS normalisation on bf16 logits (what the repo does)")
V_C = Variant("C_bf16_trunk_fp32_normalise", [], True, desc="as A but logits upcast to fp32 before the SUBS log-sum-exp")
V_B = Variant("B_bf16_trunk_fp32_output_layer", [P(bm.DDitFinalLayer, "forward", final_layer_fp32)], True, desc="bf16 blocks; final modulation+linear in fp32; fp32 normalisation")
V_D = Variant("D_bf16_with_v1_shim_rotary", [P(rot, "apply_rotary_emb_qkv_", rot_v1.apply_rotary_emb_qkv_)], False, desc="A with the ORIGINAL shim rotary (bf16 arithmetic)")
V_G = Variant("G_bf16_attention_in_fp32", [P(fai, "flash_attn_varlen_qkvpacked_func", attn_fp32)], False, desc="A but SDPA attention computed in fp32")
V_E = Variant("E_fp32_all", [], True, autocast_off=True, desc="no autocast anywhere, fp32 weights and activations (TF32 off)")
# fp64 'truth': deep copy of the model in double; LayerNorm in double; time embedding input cast
truth_net = None


def build_truth():
    global truth_net
    truth_net = copy.deepcopy(m.backbone).double().eval()
    truth_net.backbone.sigma_map.mlp.register_forward_pre_hook(lambda mod, a: (a[0].double(),))
    return truth_net


import copy
def ln_double(self, x):
    return F.layer_norm(x, [self.dim]) * self.weight[None, None, :]
V_T = Variant("T_fp64_truth", [P(bm.LayerNorm, "forward", ln_double)], True, autocast_off=True, desc="whole model in float64 (autocast off, fp64 LayerNorm); reference")


def stats_vs(ref_lp, lp, x0, mk):
    """masked-position statistics of log-probs lp against reference log-probs ref_lp (both [1,L,V]); fp64 inside."""
    r = ref_lp[mk].double(); v = lp[mk].double()
    ok = torch.ones(r.shape[-1], dtype=torch.bool, device=r.device); ok[MASK] = False
    r = r[:, ok]; v = v[:, ok]
    pr = r.exp(); pv_raw = v.exp()
    sum_raw = pv_raw.sum(-1)
    vn = v - torch.logsumexp(v, -1, keepdim=True); pv = vn.exp()
    Hr = -(pr * r).sum(-1)
    H_raw = -(pv_raw * v).sum(-1)                          # entropy exactly as the engineer computed it (no renormalisation)
    H_n = -(pv * vn).sum(-1)
    kl = (pr * (r - vn)).sum(-1)
    tgt = x0[mk]; tgt_idx = tgt - (tgt > MASK).long()      # index inside the reduced vocab (MASK id is the last column here)
    lt_r = r.gather(-1, tgt_idx[:, None])[:, 0]; lt_v = v.gather(-1, tgt_idx[:, None])[:, 0]
    return dict(n=int(mk.sum()), top1_agree=float((r.argmax(-1) == v.argmax(-1)).double().sum()),
                ent_abs_diff_raw=float((H_raw - Hr).abs().sum()), ent_abs_diff_renorm=float((H_n - Hr).abs().sum()),
                ent_signed_raw=float((H_raw - Hr).sum()), kl_ref_to_var=float(kl.sum()),
                true_token_lp_abs_diff=float((lt_v - lt_r).abs().sum()), true_token_lp_signed=float((lt_v - lt_r).sum()),
                max_abs_p_diff=float((pv_raw - pr).abs().max()), rowsum_min=float(sum_raw.min()), rowsum_max=float(sum_raw.max()),
                mean_ent_ref=float(Hr.sum()))


def agg(rows):
    n = sum(r["n"] for r in rows)
    out = dict(n_masked=n)
    for k in ("top1_agree", "ent_abs_diff_raw", "ent_abs_diff_renorm", "ent_signed_raw", "kl_ref_to_var", "true_token_lp_abs_diff", "true_token_lp_signed", "mean_ent_ref"):
        out[k] = sum(r[k] for r in rows) / n
    out["max_abs_p_diff"] = max(r["max_abs_p_diff"] for r in rows)
    out["rowsum_min"] = min(r["rowsum_min"] for r in rows); out["rowsum_max"] = max(r["rowsum_max"] for r in rows)
    return out



def duty(t_start):
    """sleep as long as the work took (target ~50% GPU utilisation, thermal guard rule)"""
    torch.cuda.synchronize(); time.sleep(max(0.0, time.time() - t_start))


def read_jsonl(path):
    return [json.loads(l) for l in open(path)] if Path(path).exists() else []


build_truth()
V_T.model = truth_net
variants = [V_A, V_C, V_B, V_D, V_G, V_E]
if SHIM == "v1":
    variants = [v for v in variants if v is not V_D]

# =========================== T2 part 1: state-level numerics vs fp64 truth ===========================
if args.stage == "state":
    ck = G4 / "t2_state.jsonl"
    done = {r["si"]: r for r in read_jsonl(ck)}
    for si in range(args.n_state):
        gseq = torch.Generator(device="cpu").manual_seed(100 + si)       # per-sequence mask => resumable
        if si in done: continue
        t0 = time.time()
        x0 = valid[int(perm[si])]["input_ids"][None].to(dev)
        keep = (torch.rand(x0.shape, generator=gseq) < 0.5).to(dev)
        xt = torch.where(keep, x0, torch.full_like(x0, MASK)); mk = xt == MASK
        lp_T = V_T.logp(xt); lps = {}; row = dict(si=si, vs_truth={})
        for v in variants:
            lps[v.name] = v.logp(xt); row["vs_truth"][v.name] = stats_vs(lp_T, lps[v.name], x0, mk)
        row["A_vs_E"] = stats_vs(lps[V_E.name], lps[V_A.name], x0, mk)
        del lp_T, lps
        with open(ck, "a") as f: f.write(json.dumps(row) + "\n")
        print(f"state-level {si+1}/{args.n_state}", flush=True)
        duty(t0)
    rows = read_jsonl(ck)
    assert len(rows) == args.n_state, len(rows)
    out = dict(env=env_info(), shim=SHIM, repo_sha=git_sha(REPO), n_sequences=args.n_state, mask_rate=0.5,
               variants={v.name: dict(desc=v.desc, vs_fp64_truth=agg([r["vs_truth"][v.name] for r in rows])) for v in variants},
               official_bf16_vs_fp32_all=agg([r["A_vs_E"] for r in rows]))
    jdump(out, G4 / "t2_state.json")
    print(json.dumps(out["official_bf16_vs_fp32_all"], indent=1))
    for k, v in out["variants"].items(): print(k, {a: round(b, 5) for a, b in v["vs_fp64_truth"].items()})

# =========================== T1b: full forward, independent attention + rotary paths ===========================
elif args.stage == "t1b":
    def t1b(mode):
        """mode 'fp32' (autocast off) or 'bf16' (the model's own). Paths: S = shim default (SDPA auto backend + shim rotary),
        M = SDPA MATH backend with explicit scale + shim rotary, X = explicit float64 softmax attention + complex-product rotary (nothing from the shim)."""
        rows = {}
        for si in range(4):
            t0 = time.time()
            gseq = torch.Generator(device="cpu").manual_seed(900 + si)
            x0 = valid[int(perm[si])]["input_ids"][None].to(dev)
            keep = (torch.rand(x0.shape, generator=gseq) < 0.5).to(dev)
            xt = torch.where(keep, x0, torch.full_like(x0, MASK)); mk = (xt == MASK)[0]
            outs = {}
            for pname, patches in dict(S=[], M=[P(fai, "flash_attn_varlen_qkvpacked_func", attn_math_backend)],
                                       X=[P(fai, "flash_attn_varlen_qkvpacked_func", attn_explicit), P(rot, "apply_rotary_emb_qkv_", rotary_complex)]).items():
                vv = Variant("t1b_" + pname, patches, False, autocast_off=(mode == "fp32"))
                outs[pname] = vv.logits(xt).float()
            for a, b in (("S", "X"), ("M", "X"), ("S", "M")):
                d = (outs[a] - outs[b]).abs()
                lpA = F.log_softmax(outs[a][0][mk][:, :MASK], -1); lpB = F.log_softmax(outs[b][0][mk][:, :MASK], -1)
                rows.setdefault(f"{a}_vs_{b}", []).append(dict(
                    logit_max_abs=float(d.max()), logit_mean_abs=float(d.mean()), logit_rms=float(outs[b].pow(2).mean().sqrt()),
                    logp_masked_max_abs=float((lpA - lpB).abs().max()), top1_agree=float((lpA.argmax(-1) == lpB.argmax(-1)).float().mean())))
            del outs; duty(t0)
        return {k: dict(logit_max_abs=max(r["logit_max_abs"] for r in v), logit_mean_abs=sum(r["logit_mean_abs"] for r in v) / len(v),
                        logit_rms=v[0]["logit_rms"], logp_masked_max_abs=max(r["logp_masked_max_abs"] for r in v),
                        top1_agree_min=min(r["top1_agree"] for r in v), n_sequences=len(v)) for k, v in rows.items()}
    out = dict(env=env_info(), shim=SHIM, shim_file=str(rot.__file__), fp32=t1b("fp32"), bf16=t1b("bf16"))
    jdump(out, G4 / "t1b_full_forward.json")
    print(json.dumps(out, indent=1))

# =========================== T2 part 2: paired ELBO (official _forward_pass_diffusion) ===========================
elif args.stage == "elbo":
    del truth_net; V_T.model = None; torch.cuda.empty_cache()
    names = [v.name for v in variants]
    ck = G4 / "t2_elbo.jsonl"
    done = {r["bi"] for r in read_jsonl(ck)}
    bs = args.elbo_bs; nb = args.n_elbo // bs
    orig_forward = m.forward
    for bi in range(nb):
        if bi in done: continue
        t0 = time.time()
        idx = perm[1000 + bi * bs: 1000 + (bi + 1) * bs]
        x0 = torch.stack([valid[int(i)]["input_ids"] for i in idx]).to(dev)
        row = dict(bi=bi, loss={})
        for v in variants:
            m.forward = (lambda x, sigma, _v=v: _v.logp(x))
            torch.manual_seed(7000 + bi)                           # same t draw and same mask for every variant
            with torch.no_grad():
                loss = m._forward_pass_diffusion(x0)               # [B, L] : -log p(x0) * dsigma/expm1(sigma)
            row["loss"][v.name] = loss.double().mean(-1).tolist()
        m.forward = orig_forward
        with open(ck, "a") as f: f.write(json.dumps(row) + "\n")
        if bi % 25 == 0: print(f"elbo {bi+1}/{nb}", flush=True)
        duty(t0)
    rows = read_jsonl(ck)
    assert len({r["bi"] for r in rows}) == nb
    S = {n: torch.tensor([x for r in sorted(rows, key=lambda r: r["bi"]) for x in r["loss"][n]], dtype=torch.float64) for n in names}
    ref = S[V_E.name]; res_v = {}
    for n in names:
        d = S[n] - ref
        res_v[n] = dict(mean_nll=float(S[n].mean()), ppl=float(S[n].mean().exp()),
                        paired_diff_vs_fp32_all_nats=float(d.mean()), paired_diff_se=float(d.std() / math.sqrt(len(d))),
                        rel_ppl_diff_pct=float(100 * (d.mean().exp() - 1)))
    out = dict(env=env_info(), shim=SHIM, n_sequences=int(len(ref)), batch=bs, note="identical x0, t and mask per sequence across variants; nll in nats/token", variants=res_v)
    jdump(out, G4 / "t2_elbo.json"); print(json.dumps(out, indent=1))

# =========================== replicate the lab engineer's precision test (model-sampled sequence, 50% mask, cuda generator seed 0) ===========================
elif args.stage == "engineer":
    toks = torch.load(str(G4.parent / "env-2026-10-14" / "smoke_mdlm" / "sample_L1024_tokens.pt"))
    x = toks.to(dev)[:1]
    keep = torch.rand(x.shape, device=dev, generator=torch.Generator(device=dev).manual_seed(0)) < 0.5
    xm = torch.where(keep, x, torch.full_like(x, MASK)); mk = xm == MASK
    lp_T = V_T.logp(xm); out = dict(n_masked=int(mk.sum()), note="same tokens and mask as runs/env-2026-10-14/scripts/mdlm_smoke.py; sequence is a MODEL SAMPLE (128 steps), not OWT text")
    lps = {v.name: v.logp(xm) for v in variants}
    out["A_vs_E"] = stats_vs(lps[V_E.name], lps[V_A.name], x, mk)
    out["vs_truth"] = {n: stats_vs(lp_T, l, x, mk) for n, l in lps.items()}
    for d in [out["A_vs_E"]] + list(out["vs_truth"].values()):
        for k in ("top1_agree", "ent_abs_diff_raw", "ent_abs_diff_renorm", "kl_ref_to_var", "mean_ent_ref"): d[k] = d[k] / d["n"]
    jdump(out, G4 / "t2_engineer_replication.json"); print(json.dumps(out, indent=1)[:3000])

# =========================== T2 part 3: fp32 vs bf16 timing ===========================
elif args.stage == "timing":
    del truth_net; V_T.model = None; torch.cuda.empty_cache()
    timing = {}
    for bs in (1, 8):
        torch.cuda.empty_cache()
        xb = torch.where(torch.rand(bs, 1024, device=dev) < 0.5, torch.randint(0, MASK, (bs, 1024), device=dev), torch.full((bs, 1024), MASK, device=dev))
        sg = torch.zeros(bs, device=dev)
        def fwd():
            with torch.no_grad(): m.forward(xb, sg)
        def fwd32():
            with no_autocast(), torch.no_grad(): m.forward(xb, sg)
        timing[f"bf16_official_batch{bs}"] = timeit_cuda(fwd, 2, 8); time.sleep(5)
        timing[f"fp32_all_batch{bs}"] = timeit_cuda(fwd32, 2, 8); time.sleep(5)
        torch.backends.cuda.matmul.allow_tf32 = True; torch.backends.cudnn.allow_tf32 = True
        timing[f"fp32_all_tf32_batch{bs}"] = timeit_cuda(fwd32, 2, 8); time.sleep(5)
        torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    out = dict(env=env_info(), shim=SHIM, note="median of 8 after 2 warm-up; 5 s sleeps between measurements", timing_L1024=timing)
    jdump(out, G4 / "t2_timing.json")
    print({k: (round(v["median_s"], 4), round(v["peak_alloc_gb"], 2)) for k, v in timing.items()})

sys.stdout.flush(); sys.stderr.flush(); os._exit(0)   # skip interpreter teardown (it exited with 0xC0000409 after the results were written)
