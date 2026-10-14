import torch


def _rot(x, cos, sin):
    # GPT-NeoX style (interleaved=False): x = [x1 | x2], rotate over rd = 2*cos.shape[-1] leading dims
    rd2 = cos.shape[-1]
    x1, x2 = x[..., :rd2], x[..., rd2:2 * rd2]
    c, s = cos[None, :, None, :].to(x.dtype), sin[None, :, None, :].to(x.dtype)
    return torch.cat([x1 * c - x2 * s, x1 * s + x2 * c, x[..., 2 * rd2:]], dim=-1)


def apply_rotary_emb_qkv_(qkv, cos, sin, cos_k=None, sin_k=None, interleaved=False, seqlen_offsets=0):
    """qkv: (b, s, 3, h, d); cos/sin: (s, rd/2). Rotates q and k, leaves v. Returns new tensor (not in place)."""
    assert not interleaved and seqlen_offsets == 0
    q, k, v = qkv.unbind(dim=2)
    return torch.stack([_rot(q, cos, sin), _rot(k, cos, sin), v], dim=2)


def apply_rotary_emb(x, cos, sin, interleaved=False, inplace=False, seqlen_offsets=0, cu_seqlens=None, max_seqlen=None):
    assert not interleaved and cu_seqlens is None and seqlen_offsets == 0
    return _rot(x, cos, sin)
