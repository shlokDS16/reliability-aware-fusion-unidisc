# Pure-PyTorch stand-in for flash_attn.layers.rotary (no Windows wheel).
# v2 (2026-10-14, G4 gate): arithmetic is done in float32 for bf16/fp16 inputs and rounded ONCE on output, like the Triton kernel in
# flash-attn 2.5.6 (flash_attn/ops/triton/rotary.py loads x, cos, sin, converts to fp32, computes x0*cos - x1*sin and x0*sin + x1*cos,
# stores in x.dtype). v1 multiplied and subtracted in bf16 (two extra roundings, about 1.4x the rms error, 31% of elements differ
# from the single-rounding result by one or two bf16 steps; see runs/G4-mdlm-repro-2026-10-14/t1a_shim_unit_v1.json). fp32/fp64 inputs are
# computed in their own dtype (unchanged from v1). The original v1 file is kept verbatim at runs/G4-mdlm-repro-2026-10-14/scripts/shim_v1/.
import torch


def _rot(x, cos, sin):
    # GPT-NeoX style (interleaved=False): x = [x1 | x2], rotate over rd = 2*cos.shape[-1] leading dims
    rd2 = cos.shape[-1]
    ct = torch.float32 if x.dtype in (torch.bfloat16, torch.float16) else x.dtype   # compute dtype
    x1, x2 = x[..., :rd2].to(ct), x[..., rd2:2 * rd2].to(ct)
    c, s = cos[None, :, None, :].to(ct), sin[None, :, None, :].to(ct)
    return torch.cat([(x1 * c - x2 * s).to(x.dtype), (x1 * s + x2 * c).to(x.dtype), x[..., 2 * rd2:]], dim=-1)


def apply_rotary_emb_qkv_(qkv, cos, sin, cos_k=None, sin_k=None, interleaved=False, seqlen_offsets=0):
    """qkv: (b, s, 3, h, d); cos/sin: (s, rd/2). Rotates q and k, leaves v. Returns new tensor (not in place)."""
    assert not interleaved and seqlen_offsets == 0
    q, k, v = qkv.unbind(dim=2)
    return torch.stack([_rot(q, cos, sin), _rot(k, cos, sin), v], dim=2)


def apply_rotary_emb(x, cos, sin, interleaved=False, inplace=False, seqlen_offsets=0, cu_seqlens=None, max_seqlen=None):
    assert not interleaved and cu_seqlens is None and seqlen_offsets == 0
    return _rot(x, cos, sin)
