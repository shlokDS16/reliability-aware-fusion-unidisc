"""Tests that need the omni stack (transformers 4.51.3 + omni_diffusion + bitsandbytes): CPU only, no weights. They SKIP in any venv without `omni_diffusion` (so the existing suite is unaffected).

Run in the omni venv (which has no pytest; the functions are plain asserts):
    see the report for the one-line harness command (the omni venv has no pytest; every test_* function is a plain function)
or `python -m pytest` in an environment that has both pytest and omni_diffusion.

What they cover that the fakes cannot: the REAL tokenizer (ids, chat template, regex split at the newline), a tiny randomly initialised REAL `DreamModel` (so `forward_dream`, the one-position
read-off and the audio-stub path are the repo's own code), and the quantisation plan on the real-size meta skeleton (module names to skip). They do NOT cover: weights, bitsandbytes kernels,
the bf16 numerics of the 4-bit model, memory (all GPU)."""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import pytest
except ImportError:                                                     # the omni venv
    pytest = None

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _need_omni():
    from exp_p2.omni import loader
    try:
        loader.ensure_import_paths()
        import omni_diffusion.models.dream  # noqa: F401
        snap = loader.snapshot(loader.OMNI_REPO_ID)
    except Exception as e:                                              # noqa: BLE001
        if pytest is not None:
            pytest.skip(f"omni stack not available here: {type(e).__name__}")
        raise
    return loader, snap


def _tiny(loader, snap):
    import torch
    stub = loader.install_audio_stub()
    from omni_diffusion.models.dream import DreamConfig, DreamModel
    from test_omni_fakes import FakeMagvit
    from exp_p2.omni.scorer import OmniScorer
    cfg = DreamConfig(vocab_size=176264, hidden_size=32, intermediate_size=64, num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2, max_position_embeddings=2048,
                      rope_theta=10000.0, mask_token_id=151666, pad_token_id=151643)
    cfg._attn_implementation = "sdpa"
    torch.manual_seed(0)
    model = DreamModel(cfg).eval()
    tok = loader.load_tokenizer(snap)
    return OmniScorer(model, tok, FakeMagvit(16), grid=16, device="cpu"), stub


def test_real_tokenizer_layout_equals_training_route_and_chat_template():
    loader, snap = _need_omni()
    import numpy as np
    from PIL import Image
    from exp_p2.omni import checks
    sc, stub = _tiny(loader, snap)
    pils = [Image.fromarray(np.random.default_rng(i).integers(0, 255, (90, 120, 3), dtype=np.uint8)) for i in range(2)]
    caps = ["A man riding a wave on top of a surfboard.", "Two dogs play with a red frisbee in the park."]
    r = checks.check_layout_roundtrip(sc, pils, caps)
    assert r["ok"], r
    assert checks.check_mask_id(sc, sc.model.config)["ok"] and checks.check_image_range(sc, sc.model.config)["ok"]
    assert len(sc.caption_ids(caps[0])) == 12                                  # measured with the real tokenizer on 2026-10-28 (explore1)


def test_tiny_real_dream_model_scorer_equals_the_generation_readoff_and_the_stub_is_inert():
    loader, snap = _need_omni()
    import numpy as np
    from exp_p2.omni import checks
    sc, stub = _tiny(loader, snap)
    st = sc.build(sc.caption_ids("A man riding a wave on top of a surfboard."), np.random.default_rng(0).integers(0, 8192, 256))
    a4 = checks.check_shift_code_path(sc, st, seed=0, atol=0.0)
    assert a4["ok"], a4
    a6 = checks.check_audio_stub_inert(sc, stub, st)
    assert a6["ok"], a6
    a7 = checks.check_layout_only_null(sc, "A man riding a wave on top of a surfboard.", "Two dogs play with a red frisbee in the park.")
    assert a7["ok"], a7


def test_micro_batch_equals_single_rows_on_the_real_model_class():
    loader, snap = _need_omni()
    import numpy as np
    import torch
    from exp_p2.scoring import MASK_ID
    sc, _ = _tiny(loader, snap)
    st = sc.build(sc.caption_ids("A man riding a wave."), np.random.default_rng(1).integers(0, 8192, 256))
    xs = torch.stack([st["base"].clone() for _ in range(3)])
    for i in range(3):
        xs[i, st["img_pos"][5 * i:5 * i + 5]] = MASK_ID
    single = torch.cat([sc.logits_fn(st)(xs[i:i + 1]) for i in range(3)])
    sc.micro_bs = 3
    batched = sc.logits_fn(st)(xs)
    # padding rows in a batch are not an issue (same length); results agree to float32 round-off (batched GEMM may reorder sums)
    f = torch.isfinite(single)
    assert torch.allclose(single[f], batched[f], atol=1e-4)


def test_quantisation_plan_on_the_real_size_meta_skeleton():
    loader, snap = _need_omni()
    m = loader.meta_skeleton(snap)
    plan = loader.quantisation_plan(m)
    assert plan["n_linear4bit"] == 196 and plan["all_decoder_layers"], plan
    assert sorted(plan["plain_linear"]) == ["lm_head", "model.audio_projection.mlp.0", "model.audio_projection.mlp.2"]
    assert abs(plan["params_in_4bit"] - 6.525417472e9) < 1e6 and abs(plan["params_total"] - 7.8037632e9) < 1e6


def test_loader_call_path_on_a_tiny_saved_checkpoint_with_unexpected_audio_keys():
    """`loader.load_model(..., quantize=False)` is the production call minus bitsandbytes: PreTrainedModel.from_pretrained reached past DreamPreTrainedModel's double-loading override, the audio
    stub in place, sdpa attention, bf16, and 'model.audio_model.*' tensors in the checkpoint that have no module (they must be ignored, as in the real snapshot where 917 such tensors exist)."""
    loader, snap = _need_omni()
    import tempfile
    import torch
    from safetensors.torch import load_file, save_file
    sc, stub = _tiny(loader, snap)
    with tempfile.TemporaryDirectory() as d:
        sc.model.save_pretrained(d, safe_serialization=True)
        f = Path(d) / "model.safetensors"
        sd = load_file(str(f))
        sd["model.audio_model.model.fake.weight"] = torch.zeros(3, 3)
        save_file(sd, str(f), metadata={"format": "pt"})
        model, stub2 = loader.load_model(Path(d), quantize=False)
    assert type(model).__name__ == "DreamModel" and not model.training and next(model.parameters()).dtype == torch.bfloat16
    assert model.config._attn_implementation == "sdpa" and type(model.model.layers[0].self_attn).__name__ == "DreamSdpaAttention"
    assert isinstance(model.model.audio_model, stub2) and stub2.calls == 0
    assert torch.equal(model.lm_head.weight.float(), sc.model.lm_head.weight.to(torch.bfloat16).float())          # weights arrived (bf16 round trip)
