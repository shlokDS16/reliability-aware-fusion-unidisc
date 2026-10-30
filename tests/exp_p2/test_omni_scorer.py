"""CPU tests of the Omni adapter's id-space, layout, logit shift and scorer plumbing on fakes (no transformers, no weights). The real-model paths are not covered here (see test_omni_stack.py,
which needs the omni venv, and the GPU timing stage)."""
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from test_omni_fakes import FakeOmniTokenizer, make_scorer                                 # noqa: E402
from exp_p2.omni import checks, layout as L                                               # noqa: E402
from exp_p2.gate import dcache, pipeline, scores                                          # noqa: E402
from exp_p2.scoring import IMG_LO, IMG_HI, MASK_ID, masked_logprobs, Spec                  # noqa: E402

CAP = "a red cat sits on a soft old mat"


def test_shift_right_matches_the_sampler_line_and_is_identity_at_zero():
    t = torch.randn(2, 7, 5)
    assert torch.equal(L.shift_right(t, 1), torch.cat([t[:, :1], t[:, :-1]], dim=1))          # the literal line of generation_utils.py
    assert torch.equal(L.shift_right(t, 0), t)
    s2 = L.shift_right(t, 2)
    assert torch.equal(s2[:, 2:], t[:, :-2]) and torch.equal(s2[:, 0], t[:, 0]) and torch.equal(s2[:, 1], t[:, 0])


def test_virtual_map_is_injective_invertible_and_refuses_mask_and_image_ids():
    m = L.VirtualMap()
    a = [m.v(r) for r in (151644, 872, 198, 5, 872)]
    assert a == [0, 1, 2, 3, 1] and m.v2r == [151644, 872, 198, 5]
    for bad in (L.OMNI_MASK_ID, L.OMNI_IMG_OFFSET, L.OMNI_IMG_OFFSET + 8191):
        with pytest.raises(ValueError):
            m.v(bad)
    real = [151644, 5, L.OMNI_IMG_OFFSET + 7, L.OMNI_IMG_OFFSET + 8191, 198]
    virt = m.to_virtual_row(real, 2, 2)
    assert virt == [0, 3, IMG_LO + 7, IMG_LO + 8191, 2]
    assert m.to_real_row(virt) == real
    t = m.table("cpu")
    assert int(t[MASK_ID]) == L.OMNI_MASK_ID and int(t[IMG_LO + 3]) == L.OMNI_IMG_OFFSET + 3 and int(t[0]) == 151644
    with pytest.raises(ValueError):
        m.to_real_row([31999])                                                               # unallocated virtual text id


def test_real_row_layout_and_positions():
    S = L.structural_ids(lambda s: FakeOmniTokenizer()(s)["input_ids"])
    codes = np.arange(16)
    ids, cap0, img0, n = L.real_row(S, [11, 12, 13], codes)
    assert ids[:4] == [151644, 872, 198, ids[3]] and ids[cap0:cap0 + n] == [11, 12, 13]
    assert ids[cap0 + n:img0] == [151645, 198, 151644, 77091, 198, 151667]                    # <|im_end|> \n <|im_start|> assistant \n <|begin_of_image|>
    assert ids[img0:img0 + 16] == [L.OMNI_IMG_OFFSET + c for c in range(16)] and ids[img0 + 16:] == [151668, 151645, 198]
    with pytest.raises(ValueError):
        L.real_row(S, [1], [8192] + [0] * 15)


def test_to_virtual_logits_columns_shift_and_padding():
    B, T = 2, 9
    lg = torch.randn(B, T, L.OMNI_VOCAB).to(torch.bfloat16)
    out = L.to_virtual_logits(lg, None, shift=1)
    img = lg[..., L.OMNI_IMG_OFFSET:L.OMNI_IMG_OFFSET + 8192]
    assert out.shape == (B, T, IMG_HI)
    assert torch.equal(out[:, 1:, IMG_LO:IMG_LO + 8192], img[:, :-1])                        # position i reads output i - 1
    assert torch.equal(out[:, 0, IMG_LO:IMG_LO + 8192], img[:, 0])
    assert torch.isinf(out[..., IMG_LO + 8192:]).all() and torch.isinf(out[..., :IMG_LO]).all()      # padding, mask and text columns are -inf
    m = L.VirtualMap()
    for r in (5, 6, 7):
        m.v(r)
    o2 = L.to_virtual_logits(lg, m, shift=1, text_logits=True)
    assert torch.equal(o2[:, 1:, 2], lg[:, :-1, 7]) and torch.isinf(o2[..., 3:MASK_ID + 1]).all()
    with pytest.raises(ValueError):
        L.to_virtual_logits(lg, None, text_logits=True)


def test_build_masking_and_the_rows_the_model_actually_sees():
    sc = make_scorer()
    cap = sc.caption_ids(CAP)
    codes = np.arange(16) * 3
    st = sc.build(cap, codes)
    assert len(st["img_pos"]) == 16 and len(st["cap_pos"]) == len(cap) == 9
    assert int(st["img_pos"][0]) == int(st["cap_pos"][-1]) + 1 + 6 and (st["mod"][0].nonzero().flatten() == st["img_pos"]).all()
    base = st["base"]
    assert (base[st["img_pos"]] == IMG_LO + torch.as_tensor(codes)).all() and not (base == MASK_ID).any()
    x = base.clone()
    x[st["cap_pos"]] = MASK_ID
    x[st["img_pos"][[2, 5]]] = MASK_ID
    sc.logits_fn(st)(x[None])
    seen = sc.model.seen[-1]
    assert (seen == L.OMNI_MASK_ID).nonzero().flatten().tolist() == sorted(st["cap_pos"].tolist() + st["img_pos"][[2, 5]].tolist())
    keep = (x != MASK_ID)
    assert (sc.vmap.table("cpu")[x][keep] == seen[keep]).all()
    with pytest.raises(ValueError):
        sc.caption_ids("a <|mask|> b")                                                        # a special token inside a caption is refused
    with pytest.raises(ValueError):
        sc.build(cap, np.full(16, 8192))                                                      # code outside the 8192 codebook


def test_logits_fn_is_micro_batch_invariant_counts_rows_and_refuses_padding_ids():
    a, b = make_scorer(micro_bs=1), make_scorer(micro_bs=4)
    cap, codes = a.caption_ids(CAP), np.arange(16) % 8192
    b.caption_ids(CAP)
    sta, stb = a.build(cap, codes), b.build(b.caption_ids(CAP), codes)
    xs = torch.stack([sta["base"].clone() for _ in range(3)])
    for i in range(3):
        xs[i, sta["img_pos"][i]] = MASK_ID
    la, lb = a.logits_fn(sta)(xs), b.logits_fn(stb)(xs)
    assert torch.equal(la, lb) and a.n_forward_rows == 3 and a.model.forward_calls == 3 and b.model.forward_calls == 1
    bad = xs.clone()
    bad[0, 0] = IMG_LO + 8192
    with pytest.raises(ValueError):
        a.logits_fn(sta)(bad)


def test_restricted_log_softmax_is_over_the_8192_valid_codes_and_the_gate_stack_runs_unchanged(tmp_path):
    sc = make_scorer()
    cap = sc.caption_ids(CAP)
    codes = np.random.default_rng(0).integers(0, 8192, 16)
    st = sc.build(cap, codes)
    lam = scores.full_image_lp(sc, st, caption_masked=False)
    assert lam.shape == (16, 16384) and torch.isfinite(lam[:, :8192]).all() and torch.isinf(lam[:, 8192:]).all()
    assert torch.allclose(lam[:, :8192].exp().sum(1), torch.ones(16), atol=1e-4)
    groups = pipeline.item_groups(sc, 5, 8)
    dc = dcache.DCache(tmp_path / "dc")
    gs = pipeline.gate_scores(sc, cap, codes, groups, dc, 8)
    assert gs["B"].shape == (16,) and (gs["B"] <= 0).all() and np.isfinite(gs["u"]).all() and (gs["s3"] >= 0).all()
    neg = sc.caption_ids("a loud small dog")
    lp, ln = pipeline.caption_lambdas(sc, cap, neg, codes)
    d = pipeline.image_delta(lp, ln, codes)
    assert d.shape == (16,) and np.isfinite(d).all()
    r0 = sc.n_forward_rows
    pipeline.gate_scores(sc, cap, codes, groups, dc, 8)
    assert sc.n_forward_rows - r0 == 8                                                        # K = 8 passes, the null is cached
    assert (tmp_path / "dc" / f"DI_n{len(cap):03d}.npy").exists()
    # B conditions on the other image tokens only: masking the caption means the caption does not change B
    st2 = sc.build(sc.caption_ids("quiet wide tall bright warm hard thin new old"), codes)
    assert np.allclose(scores.image_B(sc, st, groups, 8)["B"], scores.image_B(sc, st2, groups, 8)["B"])


def test_selfcheck_keys_for_the_runner_gate():
    from PIL import Image
    sc = make_scorer()
    pil = Image.fromarray(np.random.default_rng(1).integers(0, 255, (80, 100, 3), dtype=np.uint8))
    r = sc.selfcheck(pil, CAP)
    assert r["ids_equal"] and r["modality_equal"] and r["image_tokens_frac_equal"] == 1.0 and r["mask_row_roundtrip"]
    assert sc.encode(sc.preprocess(pil)).shape == (16,)


def test_adapter_checks_a1_a2_on_the_fake_tokenizer():
    sc = make_scorer()
    a1 = checks.check_mask_id(sc, sc.model.config)
    assert a1["ok"], a1
    a2 = checks.check_image_range(sc, sc.model.config)
    assert a2["ok"], a2
    sc.model.config.mask_token_id = 3                                                         # an inconsistent config must fail the check
    assert not checks.check_mask_id(sc, sc.model.config)["ok"]


def test_a7_layout_only_null_on_the_fake():
    sc = make_scorer()
    r = checks.check_layout_only_null(sc, "a red cat sits on a soft old mat", "quiet wide tall bright warm hard thin new old")
    assert r["ok"] and r["detail"]["max_abs_diff_image_null"] == 0.0 and r["detail"]["caption_length"] == 9


def test_a6_stub_check_logic_with_a_fake_stub():
    class Stub(torch.nn.Module):
        calls = 0
    sc = make_scorer()
    sc.model.model = type("M", (), {})()
    sc.model.model.audio_model = Stub()
    sc.model.model.audio_projection = torch.nn.Linear(2, 2)
    st = sc.build(sc.caption_ids(CAP), np.arange(16))
    assert checks.check_audio_stub_inert(sc, Stub, st)["ok"]
    sc.model.model.audio_model = torch.nn.Linear(2, 2)                                        # not the stub: fails
    assert not checks.check_audio_stub_inert(sc, Stub, st)["ok"]
