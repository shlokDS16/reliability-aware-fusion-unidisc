"""T1a: unit test of the flash_attn stand-in against references written from the definitions.

Rotary references (independent of the shim's concat formula):
  R1 complex product  (x1 + i x2) * (cos + i sin)   (float64)
  R2 flash-attn's own pure-PyTorch function `apply_rotary_emb_torch` + `rotate_half`, retyped from
     Dao-AILab/flash-attention @ v2.5.6 (6c9e60de), flash_attn/layers/rotary.py L20-: the version MDLM pins (requirements.yaml: flash-attn==2.5.6)
  R3 explicit Python loop on a tiny shape (validates R1/R2 themselves)
  R4 MDLM repo's own un-fused form  qkv*cos_full + rotate_half(qkv)*sin_full  using the repo's `Rotary` module cos/sin cache
Attention references: explicit float64 softmax(QK^T/sqrt(d))V (causal and non-causal); the shim's three entry points are tested.
bf16: the real kernels read bf16, compute in fp32 and round once on store (flash_attn/ops/triton/rotary.py @ v2.5.6 L82-100;
attention accumulates in fp32). Emulation of that = float64 compute from the same bf16 inputs, one rounding to bf16.
Run: G4_SHIM=v1|v2 python t1a_shim_unit.py   -> t1a_shim_unit_<shim>.json
"""
import itertools, math, sys
from g4_common import *  # noqa
import torch
import importlib

dev = "cuda"
import flash_attn  # noqa: E402  (the shim)
from flash_attn.layers import rotary as rot
from flash_attn import flash_attn_interface as fai

res = dict(shim=SHIM, shim_file=str(rot.__file__), torch=torch.__version__, device=torch.cuda.get_device_name(0), cases=[])


# ---------------- references ----------------
def rotate_half_fa(x):  # flash-attn v2.5.6 rotate_half(interleaved=False)
    x1, x2 = x.chunk(2, dim=-1)
    return torch.cat((-x2, x1), dim=-1)


def ref_fa_torch(x, cos, sin):  # flash-attn v2.5.6 apply_rotary_emb_torch(interleaved=False); x (b,s,h,d); cos (s, rd/2)
    ro = cos.shape[-1] * 2
    c = cos.repeat(1, 2)[None, :, None, :]   # "... d -> ... 1 (2 d)"
    s = sin.repeat(1, 2)[None, :, None, :]
    return torch.cat([x[..., :ro] * c + rotate_half_fa(x[..., :ro]) * s, x[..., ro:]], dim=-1)


def ref_complex(x, cos, sin):
    rd2 = cos.shape[-1]
    x = x.double()
    z = torch.complex(x[..., :rd2], x[..., rd2:2 * rd2])
    r = torch.complex(cos.double(), sin.double())[None, :, None, :]
    w = z * r
    return torch.cat([w.real, w.imag, x[..., 2 * rd2:]], -1)


def ref_loop(x, cos, sin):  # x (b,s,h,d) tiny
    b, s, h, d = x.shape; rd2 = cos.shape[-1]
    out = x.clone().double()
    for bi, si, hi in itertools.product(range(b), range(s), range(h)):
        for i in range(rd2):
            x1, x2 = float(x[bi, si, hi, i]), float(x[bi, si, hi, i + rd2])
            c, sn = float(cos[si, i]), float(sin[si, i])
            out[bi, si, hi, i] = x1 * c - x2 * sn
            out[bi, si, hi, i + rd2] = x1 * sn + x2 * c
    return out


def ref_attn(q, k, v, causal, scale=None):  # (b,s,h,d) -> float64
    q, k, v = q.double(), k.double(), v.double()
    d = q.shape[-1]
    sc = (d ** -0.5) if scale is None else scale
    s = torch.einsum("bqhd,bkhd->bhqk", q, k) * sc
    if causal:
        m = torch.triu(torch.ones(s.shape[-2], s.shape[-1], dtype=torch.bool, device=s.device), 1)
        s = s.masked_fill(m, float("-inf"))
    return torch.einsum("bhqk,bkhd->bqhd", s.softmax(-1), v)


def errs(a, ref):
    a = a.double(); ref = ref.double()
    d = (a - ref).abs()
    rms = ref.pow(2).mean().sqrt()
    mask = ref.abs() > 1e-2 * rms
    return dict(max_abs=float(d.max()), max_abs_over_max_ref=float(d.max() / ref.abs().max()),
                max_elem_rel=float((d[mask] / ref.abs()[mask]).max()), ref_rms=float(rms))


def bf16_ulp_units(a, ref_exact):
    """error in units of the bf16 spacing at |ref| (2^-7 relative at the bottom of a binade): max |a-ref| / (2^-8 * max(|ref|, tiny))"""
    d = (a.double() - ref_exact.double()).abs()
    spacing = ref_exact.double().abs().clamp_min(2.0 ** -20) * 2.0 ** -8
    m = ref_exact.double().abs() > 1e-2 * ref_exact.double().pow(2).mean().sqrt()
    return float((d[m] / spacing[m]).max())


def cossin(s, rd2, device, dtype):  # same construction as the MDLM Rotary module (inv_freq base 10000 over head dim 2*rd2)
    inv = 1.0 / (10000 ** (torch.arange(0, 2 * rd2, 2, device=device).float() / (2 * rd2)))
    fr = torch.einsum("i,j->ij", torch.arange(s, device=device).float(), inv)
    return fr.cos().to(dtype), fr.sin().to(dtype)


torch.manual_seed(0)

# ---------------- R3 validates R1, R2 ----------------
x = torch.randn(2, 5, 3, 8, dtype=torch.float64); c, s_ = cossin(5, 4, "cpu", torch.float64)
res["reference_self_check"] = dict(
    complex_vs_loop=errs(ref_complex(x, c, s_), ref_loop(x, c, s_))["max_abs"],
    flashattn_torch_vs_loop=errs(ref_fa_torch(x, c, s_), ref_loop(x, c, s_))["max_abs"],
    partial_rotary_rd4_of_d8=errs(ref_complex(x, c[:, :2], s_[:, :2]), ref_fa_torch(x, c[:, :2], s_[:, :2]))["max_abs"])

# ---------------- rotary: shim vs references ----------------
shapes_rot = [(1, 1024, 12, 64, 32), (2, 257, 12, 64, 32), (3, 64, 4, 32, 16), (1, 7, 1, 16, 8), (4, 128, 12, 64, 32), (2, 100, 4, 64, 16)]  # (b,s,h,d,rd/2)
for dt, dname in ((torch.float32, "fp32"), (torch.float64, "fp64")):
    for device in ("cpu", "cuda"):
        for (b, s, h, d, rd2) in shapes_rot:
            qkv = torch.randn(b, s, 3, h, d, dtype=dt, device=device) * 2
            cos, sin = cossin(s, rd2, device, dt)
            out = rot.apply_rotary_emb_qkv_(qkv.clone(), cos, sin)
            ref_q = ref_complex(qkv[:, :, 0], cos, sin); ref_k = ref_complex(qkv[:, :, 1], cos, sin)
            r2 = ref_fa_torch(qkv[:, :, 0].double(), cos.double(), sin.double())
            e = dict(op="rotary_qkv_", dtype=dname, device=device, shape=[b, s, h, d], rd=2 * rd2,
                     q=errs(out[:, :, 0], ref_q), k=errs(out[:, :, 1], ref_k),
                     v_unchanged=bool(torch.equal(out[:, :, 2], qkv[:, :, 2])),
                     ref_complex_vs_flashattn_torch=float((ref_q - r2).abs().max()))
            # single-tensor entry point too
            o1 = rot.apply_rotary_emb(qkv[:, :, 0], cos, sin)
            e["apply_rotary_emb_q"] = errs(o1, ref_q)
            res["cases"].append(e)

# R4: the MDLM repo's own un-fused rotary on the repo's Rotary cache, fp32, includes the "v is identity" trick
sys.path.insert(0, str(REPO)); setup_repo_import()
from models import dit as mdlm_dit  # noqa
rt = mdlm_dit.Rotary(64).to(dev)
qkv = torch.randn(2, 1024, 3, 12, 64, device=dev)
cos_full, sin_full = rt(qkv[:, :, 0])           # (1, s, 3, 1, 64): cat(freqs, freqs); v channel cos=1, sin=0
unfused = qkv * cos_full + mdlm_dit.rotate_half(qkv) * sin_full
fused = mdlm_dit.apply_rotary_pos_emb(qkv, cos_full, sin_full)
res["rotary_vs_repo_unfused_fp32"] = dict(shape=list(qkv.shape), **errs(fused, unfused))
res["rotary_vs_repo_unfused_fp32"]["v_channel_equal"] = bool(torch.equal(fused[:, :, 2], qkv[:, :, 2]))

# bf16 (what MDLM actually feeds in, because Linear output is bf16 under autocast and cos/sin are cast to qkv.dtype)
for (b, s, h, d, rd2) in [(1, 1024, 12, 64, 32), (4, 1024, 12, 64, 32)]:
    qkv = (torch.randn(b, s, 3, h, d, device=dev) * 2).bfloat16()
    cos, sin = cossin(s, rd2, dev, torch.float32)
    cosb, sinb = cos.bfloat16(), sin.bfloat16()      # MDLM does cos.to(qkv.dtype)
    out = rot.apply_rotary_emb_qkv_(qkv.clone(), cosb, sinb)
    exact_q = ref_complex(qkv[:, :, 0], cosb, sinb)  # kernel semantic: exact math on the bf16 inputs ...
    kern_q = exact_q.bfloat16()                      # ... rounded once to bf16
    res["cases"].append(dict(op="rotary_qkv_", dtype="bf16", device="cuda", shape=[b, s, h, d],
                             max_abs_vs_exact=float((out[:, :, 0].double() - exact_q).abs().max()),
                             max_abs_kernel_emulation_vs_exact=float((kern_q.double() - exact_q).abs().max()),
                             shim_vs_kernel_emulation_max_abs=float((out[:, :, 0].double() - kern_q.double()).abs().max()),
                             shim_vs_kernel_emulation_frac_elements_different=float((out[:, :, 0] != kern_q).float().mean()),
                             max_err_in_bf16_spacings=bf16_ulp_units(out[:, :, 0], exact_q),
                             rms_err=float((out[:, :, 0].double() - exact_q).pow(2).mean().sqrt()),
                             rms_err_kernel_emulation=float((kern_q.double() - exact_q).pow(2).mean().sqrt())))

# ---------------- attention: shim vs explicit float64 ----------------
shapes_att = [(1, 1024, 12, 64), (2, 257, 12, 64), (3, 64, 4, 32), (1, 7, 1, 16), (4, 128, 12, 64), (8, 1024, 12, 64)]
for dt, dname in ((torch.float32, "fp32"), (torch.float64, "fp64")):
    for device in ("cpu", "cuda"):
        for causal in (False, True):
            for (b, s, h, d) in shapes_att:
                if device == "cpu" and b * s > 2100: continue
                for sharp in (1.0, 3.0):   # sharp = larger q,k scale -> peaky softmax
                    q, k, v = [torch.randn(b, s, h, d, dtype=dt, device=device) * (sharp if i < 2 else 1) for i in range(3)]
                    ref = ref_attn(q, k, v, causal)
                    e = dict(op="attention", dtype=dname, device=device, causal=causal, shape=[b, s, h, d], qk_scale=sharp)
                    e["flash_attn_func"] = errs(fai.flash_attn_func(q, k, v, causal=causal), ref)
                    qkv = torch.stack([q, k, v], dim=2)
                    e["qkvpacked"] = errs(fai.flash_attn_qkvpacked_func(qkv, causal=causal), ref)
                    cu = torch.arange(0, (b + 1) * s, s, dtype=torch.int32, device=device)   # exactly what dit.py builds
                    o = fai.flash_attn_varlen_qkvpacked_func(qkv.reshape(b * s, 3, h, d), cu, s, 0., causal=causal)
                    e["varlen_qkvpacked_as_in_mdlm"] = errs(o.reshape(b, s, h, d), ref)
                    res["cases"].append(e)

# bf16 attention vs kernel emulation
for causal in (False,):
    for (b, s, h, d) in [(1, 1024, 12, 64), (4, 1024, 12, 64)]:
        q, k, v = [(torch.randn(b, s, h, d, device=dev) * (3 if i < 2 else 1)).bfloat16() for i in range(3)]
        exact = ref_attn(q, k, v, causal)
        cu = torch.arange(0, (b + 1) * s, s, dtype=torch.int32, device=dev)
        o = fai.flash_attn_varlen_qkvpacked_func(torch.stack([q, k, v], 2).reshape(b * s, 3, h, d), cu, s, 0., causal=causal).reshape(b, s, h, d)
        res["cases"].append(dict(op="attention", dtype="bf16", device="cuda", causal=causal, shape=[b, s, h, d],
                                 max_abs_vs_exact=float((o.double() - exact).abs().max()),
                                 rms_err=float((o.double() - exact).pow(2).mean().sqrt()),
                                 kernel_emulation_rms_err=float((exact.bfloat16().double() - exact).pow(2).mean().sqrt()),
                                 max_err_in_bf16_spacings=bf16_ulp_units(o, exact)))

# ---------------- summary ----------------
def collect(pred, keyf):
    vals = []
    for c in res["cases"]:
        if pred(c):
            for kk in keyf(c): vals.append(kk)
    return max(vals) if vals else None

res["summary"] = dict(
    rotary_fp32_max_abs=collect(lambda c: c["op"] == "rotary_qkv_" and c["dtype"] == "fp32", lambda c: [c["q"]["max_abs"], c["k"]["max_abs"], c["apply_rotary_emb_q"]["max_abs"]]),
    rotary_fp64_max_abs=collect(lambda c: c["op"] == "rotary_qkv_" and c["dtype"] == "fp64", lambda c: [c["q"]["max_abs"], c["k"]["max_abs"], c["apply_rotary_emb_q"]["max_abs"]]),
    rotary_fp32_max_elem_rel=collect(lambda c: c["op"] == "rotary_qkv_" and c["dtype"] == "fp32", lambda c: [c["q"]["max_elem_rel"], c["k"]["max_elem_rel"]]),
    rotary_fp64_max_elem_rel=collect(lambda c: c["op"] == "rotary_qkv_" and c["dtype"] == "fp64", lambda c: [c["q"]["max_elem_rel"], c["k"]["max_elem_rel"]]),
    attention_fp32_max_abs=collect(lambda c: c["op"] == "attention" and c["dtype"] == "fp32", lambda c: [c[k]["max_abs"] for k in ("flash_attn_func", "qkvpacked", "varlen_qkvpacked_as_in_mdlm")]),
    attention_fp64_max_abs=collect(lambda c: c["op"] == "attention" and c["dtype"] == "fp64", lambda c: [c[k]["max_abs"] for k in ("flash_attn_func", "qkvpacked", "varlen_qkvpacked_as_in_mdlm")]),
    attention_fp32_max_elem_rel=collect(lambda c: c["op"] == "attention" and c["dtype"] == "fp32", lambda c: [c[k]["max_elem_rel"] for k in ("flash_attn_func", "qkvpacked", "varlen_qkvpacked_as_in_mdlm")]),
    attention_fp64_max_elem_rel=collect(lambda c: c["op"] == "attention" and c["dtype"] == "fp64", lambda c: [c[k]["max_elem_rel"] for k in ("flash_attn_func", "qkvpacked", "varlen_qkvpacked_as_in_mdlm")]),
    n_cases=len(res["cases"]))
jdump(res, G4 / f"t1a_shim_unit_{SHIM}.json")
print(json.dumps(dict(shim=SHIM, summary=res["summary"], self_check=res["reference_self_check"],
                      rotary_vs_repo_unfused_fp32=res["rotary_vs_repo_unfused_fp32"]), indent=1))
for c in res["cases"]:
    if c.get("dtype") == "bf16":
        print({k: v for k, v in c.items()})
