import torch
import torch.nn.functional as F


def flash_attn_func(q, k, v, dropout_p=0.0, softmax_scale=None, causal=False, **kw):
    """q,k,v: (b, s, h, d) -> (b, s, h, d)."""
    assert dropout_p == 0.0
    o = F.scaled_dot_product_attention(q.transpose(1, 2), k.transpose(1, 2), v.transpose(1, 2),
                                       is_causal=causal, scale=softmax_scale)
    return o.transpose(1, 2)


def flash_attn_qkvpacked_func(qkv, dropout_p=0.0, softmax_scale=None, causal=False, **kw):
    q, k, v = qkv.unbind(dim=2)
    return flash_attn_func(q, k, v, dropout_p, softmax_scale, causal)


def flash_attn_varlen_qkvpacked_func(qkv, cu_seqlens, max_seqlen, dropout_p=0.0, softmax_scale=None, causal=False, **kw):
    """qkv: (total, 3, h, d) with equal-length sequences of length max_seqlen -> (total, h, d)."""
    total = qkv.shape[0]
    assert total % max_seqlen == 0 and bool((cu_seqlens[1:] - cu_seqlens[:-1] == max_seqlen).all()), "shim supports equal lengths only"
    b = total // max_seqlen
    o = flash_attn_qkvpacked_func(qkv.view(b, max_seqlen, *qkv.shape[1:]), dropout_p, softmax_scale, causal)
    return o.reshape(total, *o.shape[2:])


def flash_attn_varlen_func(*a, **kw):
    raise NotImplementedError("shim")
