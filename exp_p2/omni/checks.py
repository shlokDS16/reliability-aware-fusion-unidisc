"""Adapter checks of the Omni family R pipeline (SAP AB.5 item 1): to be RUN AND SIGNED BY THE GATE-AUDITOR, not by the author of the adapter or of the run card.

Each check returns dict(id, ok, detail). Checks marked CPU need no GPU (tokenizer, layout, a tiny Dream model or fakes); GPU checks need the real 4-bit model and run inside the timing stage's
self-check (`run_omni_timing.py`). Thresholds are design choices written HERE, before any run (E0); the auditor may tighten them before signing.

  A1 mask_id            CPU  mask id round trip: tokenizer "<|mask|>" == config.mask_token_id == 151666 == layout constant; virtual 32000 -> 151666 -> back; a text/structure
                             token can never take the mask or an image id.
  A2 image_range        CPU  image ids: "<|image_k|>" == 168072 + k for ALL k in [0, 8192); 168072 + 8192 == vocab size == len(tokenizer); the id below 168072 is not an image token;
                             the virtual image slice padding (codes >= 8192) is refused by the scorer.
  A3 layout_roundtrip   CPU  (a) tokens(INSTR + caption) == tokens(INSTR) + tokens(caption) on the given captions; (b) decode(caption ids) == caption; (c) the hand-built row equals the
                             training route (tokenizer on the assembled strings) and `apply_chat_template` for the prompt part; (d) codes -> "<|image_k|>" strings -> ids -> codes exact;
                             (e) encode twice gives identical codes. MAGVIT reconstruction PSNR is REPORTED, not gated.
  A4 shift_code_path    CPU  the scorer's logits_fn equals, exactly, the literal generation read-off `torch.cat([l[:, :1], l[:, :-1]], dim=1)` of generation_utils.py applied to
                             `forward_dream(inputs_embeds=embed_tokens(x))`, on the image columns, with caption and image positions masked; the read-off with shift 0 differs (the
                             check is not vacuous). Tolerance 0 on CPU float32; `atol` on the GPU.
  A5 shift_behaviour    GPU  teacher-forcing identity on the real model, shift s in {0, 1, 2} applied to the SAME logits: on masked image tokens of real rows (caption visible, 25 percent of the
                             image masked) the mean log-probability of the true code is highest at s = 1 by a margin of at least MARGIN_NATS = 1.0 nat over the best other shift, and top-1
                             accuracy at s = 1 exceeds that of both other shifts. (On visible tokens the copy fraction per shift is reported.)
  A6 audio_stub_inert   both the model's audio_model is the stub, the stub was never called, `audios` is None in every forward the scorer makes; audio_projection holds parameters
                             (kept, untouched); a forward with a hook that raises on any audio path completes.
  A7 layout_only_null   GPU  the cached nulls are valid: image null (caption and image fully masked) of two different (caption, codes) with the same caption length are equal (atol 1e-5,
                             the value `checks.l10_once` uses for UniDisc).
"""
from __future__ import annotations

import numpy as np
import torch

from exp_p2.omni import layout as L
from exp_p2.scoring import MASK_ID as V_MASK, IMG_LO as V_IMG_LO

MARGIN_NATS = 1.0
FRAC_MASKED = 0.25


def _r(cid: str, ok: bool, **detail) -> dict:
    return dict(id=cid, ok=bool(ok), detail=detail)


# ------------------------------------------------------------------------------------------------ A1, A2
def check_mask_id(scorer, cfg=None) -> dict:
    tok = scorer.tok
    cfg = cfg if cfg is not None else getattr(scorer.model, "config", None)
    vals = dict(tokenizer_mask=int(tok.convert_tokens_to_ids("<|mask|>")), config_mask=int(getattr(cfg, "mask_token_id", -1)), layout_const=L.OMNI_MASK_ID,
                id_to_token=tok.convert_ids_to_tokens(L.OMNI_MASK_ID))
    table = scorer.vmap.table("cpu")
    x = torch.tensor([V_MASK, V_IMG_LO, V_IMG_LO + 5])
    rt = [int(t) for t in table[x]]
    refused = 0
    for bad in (L.OMNI_MASK_ID, L.OMNI_IMG_OFFSET, L.OMNI_IMG_OFFSET + 8191):
        try:
            scorer.vmap.v(bad)
        except ValueError:
            refused += 1
    ok = (len({vals["tokenizer_mask"], vals["config_mask"], vals["layout_const"]}) == 1 and vals["id_to_token"] == "<|mask|>"
          and rt == [L.OMNI_MASK_ID, L.OMNI_IMG_OFFSET, L.OMNI_IMG_OFFSET + 5] and refused == 3)
    gcm = getattr(getattr(scorer.model, "generation_config", None), "mask_token_id", "n/a")
    return _r("A1", ok, **vals, virtual_roundtrip=rt, text_ids_refused=refused, note=f"generation_config.mask_token_id in the snapshot is {gcm!r} (the sampler is not used here)")


def check_image_range(scorer, cfg=None) -> dict:
    tok = scorer.tok
    cfg = cfg if cfg is not None else getattr(scorer.model, "config", None)
    ids = list(range(L.OMNI_IMG_OFFSET, L.OMNI_IMG_OFFSET + L.OMNI_N_CODES))
    names = tok.convert_ids_to_tokens(ids)
    all_ok = all(n == f"<|image_{k}|>" for k, n in enumerate(names))
    below = tok.convert_ids_to_tokens(L.OMNI_IMG_OFFSET - 1)
    vocab = int(getattr(cfg, "vocab_size", -1))
    try:
        scorer.logits_fn(None)(torch.full((1, 4), L.V_IMG_VALID_HI, dtype=torch.long))
        padding_refused = False
    except ValueError:
        padding_refused = True
    ok = all_ok and L.OMNI_IMG_OFFSET + L.OMNI_N_CODES == vocab == len(tok) and not str(below).startswith("<|image_") and padding_refused
    return _r("A2", ok, all_8192_names_match=all_ok, vocab_size=vocab, len_tokenizer=len(tok), id_below_first_image=below, padding_columns_refused=padding_refused)


# ------------------------------------------------------------------------------------------------ A3
def check_layout_roundtrip(scorer, pils: list, captions: list[str]) -> dict:
    tok = scorer.tok
    enc = lambda s: [int(i) for i in tok(s, add_special_tokens=False)["input_ids"]]                       # noqa: E731
    concat_ok = all(enc(L.T2I_INSTRUCTION + c) == scorer.struct["instr"] + enc(c) for c in captions)
    decode_ok = all(tok.decode(enc(c)) == c for c in captions)
    sc_res, rt_ok, det_ok, psnr = [], True, True, []
    for pil, cap in zip(pils, captions):
        sc_res.append(scorer.selfcheck(pil, cap))
        img = scorer.preprocess(pil)
        c1, c2 = scorer.encode(img), scorer.encode(img)
        det_ok &= bool(np.array_equal(c1, c2))
        strs = "".join(f"<|image_{int(c)}|>" for c in c1)
        back = [i - L.OMNI_IMG_OFFSET for i in enc(strs)]
        rt_ok &= bool(back == [int(c) for c in c1])
        try:
            rec = scorer.decode(c1).astype(np.float64)
            from PIL import Image
            ref = np.asarray(img.convert("RGB").resize((rec.shape[1], rec.shape[0]), Image.BICUBIC), np.float64)
            mse = float(((rec - ref) ** 2).mean())
            psnr.append(10 * np.log10(255.0 ** 2 / mse) if mse > 0 else float("inf"))
        except Exception:                                                                                  # noqa: BLE001 (reporting only)
            pass
    layout_ok = all(r["ids_equal"] and r["modality_equal"] and r["image_tokens_frac_equal"] == 1.0 and r.get("chat_template_prompt_equal", True) and r["mask_row_roundtrip"] for r in sc_res)
    return _r("A3", concat_ok and decode_ok and layout_ok and rt_ok and det_ok, instruction_plus_caption_tokenises_as_concatenation=concat_ok, caption_decode_roundtrip=decode_ok,
              layout_equals_training_route_and_chat_template=layout_ok, code_string_roundtrip=rt_ok, encode_deterministic=det_ok, n_images=len(pils), n_captions=len(captions),
              magvit_psnr_db_reported_not_gated=[round(float(p), 2) for p in psnr])


# ------------------------------------------------------------------------------------------------ A4, A5 helpers
def _masked_row(scorer, st, rng: np.random.Generator, frac: float = FRAC_MASKED, mask_caption: bool = True):
    x = st["base"].clone()
    if mask_caption:
        x[st["cap_pos"]] = V_MASK
    n = len(st["img_pos"])
    pick = np.sort(rng.choice(n, size=max(1, int(round(frac * n))), replace=False))
    x[st["img_pos"][torch.as_tensor(pick, device=x.device)]] = V_MASK
    return x, pick


@torch.no_grad()
def check_shift_code_path(scorer, st: dict, seed: int = 0, atol: float = 0.0) -> dict:
    """A4. The reference is the generation read-off written out literally (generation_utils.py `_sample`, non-CFG branch)."""
    rng = np.random.default_rng(seed)
    x, pick = _masked_row(scorer, st, rng)
    mine = scorer.logits_fn(st)(x[None])[..., V_IMG_LO:L.V_IMG_VALID_HI].float()
    xr = scorer.vmap.table(x.device)[x][None]
    emb = scorer.model.model.embed_tokens(xr)
    lg = scorer.model.forward_dream(None, None, None, inputs_embeds=emb).logits
    lg = torch.cat([lg[:, :1], lg[:, :-1]], dim=1)                                                       # the literal line of the sampler
    ref = lg[..., L.OMNI_IMG_OFFSET:L.OMNI_IMG_OFFSET + L.OMNI_N_CODES].float()
    d = float((mine - ref).abs().max())
    ref0 = scorer.raw_logits(xr)[..., L.OMNI_IMG_OFFSET:L.OMNI_IMG_OFFSET + L.OMNI_N_CODES].float()
    d0 = float((mine - ref0).abs().max())                                                                 # shift-0 read-off must differ: the check can fail
    pad_ok = bool(torch.isinf(scorer.logits_fn(st)(x[None])[..., L.V_IMG_VALID_HI:]).all())
    return _r("A4", d <= atol and d0 > 0 and pad_ok, max_abs_diff_vs_generation_readoff=d, atol=atol, max_abs_diff_vs_shift0=d0, padding_columns_all_minus_inf=pad_ok)


@torch.no_grad()
def check_shift_behaviour(scorer, items: list[tuple[str, np.ndarray]], seed: int = 0, margin: float = MARGIN_NATS) -> dict:
    """A5 on the real model. items = [(caption, codes)]. The same raw logits are read off with s = 0, 1, 2."""
    stats = {s: dict(lp=[], hit=[], copy=[]) for s in (0, 1, 2)}
    rng = np.random.default_rng(seed)
    for cap, codes in items:
        st = scorer.build(scorer.caption_ids(cap), codes)
        x, pick = _masked_row(scorer, st, rng, mask_caption=False)                                       # caption visible: the in-distribution T2I context
        xr = scorer.vmap.table(x.device)[x][None]
        img = scorer.raw_logits(xr)[..., L.OMNI_IMG_OFFSET:L.OMNI_IMG_OFFSET + L.OMNI_N_CODES].float()
        ip = st["img_pos"]
        true = torch.as_tensor(np.asarray(codes), dtype=torch.long, device=img.device)
        vis = np.setdiff1d(np.arange(len(ip)), pick)
        for s in (0, 1, 2):
            ro = L.shift_right(img, s)[0, ip]                                                            # [256, 8192]
            lp = torch.log_softmax(ro, -1)
            pj = torch.as_tensor(pick, device=img.device)
            stats[s]["lp"].append(lp[pj, true[pj]].cpu().numpy())
            stats[s]["hit"].append((ro[pj].argmax(-1) == true[pj]).float().cpu().numpy())
            vj = torch.as_tensor(vis, device=img.device)
            stats[s]["copy"].append((ro[vj].argmax(-1) == true[vj]).float().cpu().numpy())
    res = {s: dict(mean_logp=float(np.concatenate(v["lp"]).mean()), top1=float(np.concatenate(v["hit"]).mean()), visible_copy_frac=float(np.concatenate(v["copy"]).mean()),
                   n_masked_tokens=int(np.concatenate(v["lp"]).size)) for s, v in stats.items()}
    best_other = max(res[0]["mean_logp"], res[2]["mean_logp"])
    ok = res[1]["mean_logp"] - best_other >= margin and res[1]["top1"] > max(res[0]["top1"], res[2]["top1"])
    return _r("A5", ok, per_shift={str(k): v for k, v in res.items()}, margin_nats=margin, margin_observed=res[1]["mean_logp"] - best_other, n_rows=len(items))


# ------------------------------------------------------------------------------------------------ A6, A7
@torch.no_grad()
def check_audio_stub_inert(scorer, stub, st: dict) -> dict:
    am = scorer.model.model.audio_model
    calls0 = getattr(stub, "calls", 0)
    n_params = sum(p.numel() for p in am.parameters())
    proj = scorer.model.model.audio_projection
    proj_params = sum(p.numel() for p in proj.parameters())
    hooked = []
    h = am.register_forward_hook(lambda m, i, o: hooked.append(1))
    try:
        x = st["base"].clone()
        x[st["cap_pos"]] = V_MASK
        scorer.logits_fn(st)(x[None])
    finally:
        h.remove()
    ok = isinstance(am, stub) and n_params == 0 and getattr(stub, "calls", 0) == calls0 == 0 and not hooked and proj_params > 0
    return _r("A6", ok, audio_model_is_stub=isinstance(am, stub), stub_params=n_params, stub_calls=getattr(stub, "calls", 0), forward_hook_fired=bool(hooked), audio_projection_params=proj_params)


@torch.no_grad()
def check_layout_only_null(scorer, cap_a: str, cap_b: str, atol: float = 1e-5) -> dict:
    from exp_p2.gate import scores
    ia, ib = scorer.caption_ids(cap_a), scorer.caption_ids(cap_b)
    n = min(len(ia), len(ib))
    ca, cb = np.zeros(scorer.L_I, np.int64), (np.arange(scorer.L_I) * 7) % L.OMNI_N_CODES
    da = scores.full_image_lp(scorer, scorer.build(ia[:n], ca), True)
    db = scores.full_image_lp(scorer, scorer.build(ib[:n], cb), True)
    d = float((da[:, :L.OMNI_N_CODES] - db[:, :L.OMNI_N_CODES]).abs().max())            # the -inf padding columns would give nan
    return _r("A7", d <= atol, max_abs_diff_image_null=d, atol=atol, caption_length=n, n_passes=2)


def summarize(results: list[dict]) -> dict:
    return dict(all_ok=all(r["ok"] for r in results), failed=[r["id"] for r in results if not r["ok"]], results=results)
