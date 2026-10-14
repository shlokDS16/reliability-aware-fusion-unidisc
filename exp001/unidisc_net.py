"""UniDisc 1.4B adapter for the Net interface (card 3 items 1-5, setup.md 2.2-2.5). Generation venv only.

Reuses the loaders of runs/env-2026-10-14/scripts (unidisc_setup, unidisc_smoke): bf16 weights, SDPA attention patch (exact for
single-document rows), the official demo layout `<s> system </s><s> PROMPT <m>*32 </s><s> ' ' <image> [image tokens] </s>`.
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "runs" / "env-2026-10-14" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
    sys.path.insert(0, str(SCRIPTS / "shims"))      # pure-PyTorch flash_attn stand-in (rotary shim)

from .config import MASK_ID, IMG_OFFSET, TEXT_VOCAB, IMG_VOCAB, image_tokens


def shim_info() -> dict:
    p = SCRIPTS / "shims" / "flash_attn" / "layers" / "rotary.py"
    txt = p.read_bytes()
    ver = next((l.strip() for l in txt.decode("utf8", "ignore").splitlines() if "version" in l.lower()), "")
    return {"file": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(txt).hexdigest(), "version_line": ver}


class UniDiscNet:
    pad_ids = (0, 2)

    def __init__(self, res: int = 512, wait_commit_gb: float = 6.0):
        import unidisc_setup as U
        import unidisc_smoke as S
        from common import wait_commit
        self.U, self.S = U, S
        self.res = res
        self.V_T, self.V_I = TEXT_VOCAB, IMG_VOCAB
        self.mask_id = MASK_ID
        self.L_I = image_tokens(res)
        self.L_T = 32
        self.free_commit_at_load = wait_commit(wait_commit_gb)
        cfg = U.make_config(["eval.visualize_sample=false"])
        S.patch_attention()
        self.model, self.cfg = U.build_model(cfg, bf16=True)
        import gc
        gc.collect()
        torch.cuda.empty_cache()
        self.n_forward = 0
        self.st = None
        # Dropout (config model.dropout = 0.1) is active whenever the backbone is in train mode, and UniDisc's loaders leave it
        # there (only the validation-epoch hook calls backbone.eval()). Marginals and samples must come from eval mode.
        self.was_training_after_build = bool(self.model.backbone.training)
        self.set_eval()

    def set_eval(self):
        self.model.backbone.eval()
        self.model.backbone.requires_grad_(False)
        self.assert_eval()

    def assert_eval(self):
        bad = [n for n, m in self.model.backbone.named_modules() if m.training]
        assert not self.model.backbone.training and not bad, f"UniDisc backbone is in train mode (dropout on): {bad[:3]}"

    # ------------------------------------------------------------------ state
    def set_prompt(self, prompt: str, n_txt: int = 32, res: int | None = None):
        """prompt: prefix text (or full caption for T2I with n_txt = 0 or the empty string for D-ref). The prompt slot is
        PROMPT + ' ' + '<m>' * n_txt (setup.md 2.2)."""
        if res is not None and res != self.res:
            self.res, self.L_I = res, image_tokens(res)
        st = self._build_state(prompt, n_txt)
        L = st["layout"]
        self.st = st
        self.L_T = n_txt
        self.a0 = L["masked_text_positions"][0] if n_txt else None
        if n_txt:
            assert L["masked_text_positions"][1] - self.a0 + 1 == n_txt, "tail must be contiguous"
        self.i0, self.i1 = L["image_positions"]
        assert self.i1 - self.i0 + 1 == self.L_I, (self.i1 - self.i0 + 1, self.L_I)
        self.bos2 = L["bos_positions"][1]
        self.pre0 = self.bos2 + 1
        self.x0 = st["x0"].clone().cuda()
        self.modality = st["modality"].cuda()
        self.sample_ids = st["sample_ids"].cuda()
        self.layout = L
        return st

    def _build_state(self, prompt: str, n_txt: int):
        """Row of the official demo layout (unidisc_smoke.build_state) with the prompt-slot text  PROMPT + '<m>' * n_txt  (no space
        before the masks, see prefix_rule.py) or a clean caption for T2I (n_txt = 0)."""
        from demo.inference_utils import messages_to_batch
        from PIL import Image
        tok = self.model.tokenizer
        if "<m>" not in {x.content for x in tok.added_tokens_decoder.values()}:
            tok.add_special_tokens({"additional_special_tokens": ["<m>"]}, replace_additional_special_tokens=False)
        msgs = [dict(type="text", text=prompt + "<m>" * n_txt, role="user"),
                dict(type="image_url", image_url=Image.new("RGB", (self.res, self.res), (0, 0, 0)), role="assistant")]
        b = messages_to_batch(self.cfg, tok, self.model, msgs, resolution=self.res)
        ids, mod = b["input_ids"], b["modality"]
        assert (b["sample_ids"] == 0).all() and b["attention_mask"].all()
        bos = (ids[0] == tok.bos_token_id).nonzero().flatten().tolist()
        img_pos = (mod[0] == 1).nonzero().flatten()
        i0, i1 = int(img_pos[0]), int(img_pos[-1]) + 1
        marker = int((ids[0] == 811).nonzero().flatten()[-1])
        txt_masked = ((ids[0] == self.model.mask_index) & (mod[0] == 0)).nonzero().flatten()
        assert txt_masked.numel() == n_txt, txt_masked.numel()
        unmask = torch.ones_like(ids, dtype=torch.bool)
        unmask[0, i0:i1] = False
        if n_txt:
            unmask[0, txt_masked] = False
        layout = dict(length=ids.shape[1], bos_positions=bos, masked_text_positions=[int(txt_masked[0]), int(txt_masked[-1])] if n_txt else None,
                      image_marker_position=marker, image_positions=[i0, i1 - 1], n_image_tokens=i1 - i0)
        return dict(x0=ids.clone(), unmask=unmask, modality=mod, sample_ids=b["sample_ids"], attention_mask=b["attention_mask"], layout=layout)

    def prefix_token_ids(self):
        end = self.a0 if self.a0 is not None else self.layout["image_marker_position"]
        return self.x0[0, self.pre0:end].tolist()

    # ---------------------------------------------------------------- forward
    @torch.no_grad()
    def forward(self, tail, img, drop_prefix: bool = False):
        self.assert_eval()
        x = self.x0.clone()
        if self.L_T:
            x[0, self.a0:self.a0 + self.L_T] = tail.to(x.device)
        code = img.to(x.device)
        x[0, self.i0:self.i1 + 1] = torch.where(code >= 0, code + IMG_OFFSET, torch.full_like(code, MASK_ID))
        if drop_prefix:
            end = self.a0 if self.a0 is not None else self.layout["image_marker_position"]
            x[0, self.pre0:end] = MASK_ID
        lp = self.model.forward(x=x, sigma=None, modality=self.modality, sample_ids=self.sample_ids, block_mask=True)
        self.n_forward += 1
        lp_t = lp[0, self.a0:self.a0 + self.L_T, :TEXT_VOCAB] if self.L_T else lp.new_zeros(0, TEXT_VOCAB)
        return lp_t, lp[0, self.i0:self.i1 + 1, IMG_OFFSET:IMG_OFFSET + IMG_VOCAB]

    # ----------------------------------------------------------------- decode
    def decode_text(self, ids) -> str:
        return self.model.tokenizer.decode([int(i) for i in ids], skip_special_tokens=False)

    def decode_image(self, codes):
        from unidisc.tokenizers.image_tokenizers import decode_latents
        from image_utils import Im
        c = torch.as_tensor(codes).long().clamp(0, IMG_VOCAB - 1).cuda()[None]
        img = decode_latents(self.model.config, self.model.get_vae(), c)
        return Im(img[0]).pil

    def encode_image(self, pil):
        """VQ codes of a real image at this resolution (the demo's own encoder path: messages_to_batch). Returns LongTensor [L_I]."""
        from demo.inference_utils import messages_to_batch
        tok = self.model.tokenizer
        msgs = [dict(type="text", text="a photo", role="user"), dict(type="image_url", image_url=pil.convert("RGB").resize((self.res, self.res)), role="assistant")]
        b = messages_to_batch(self.cfg, tok, self.model, msgs, resolution=self.res)
        ids, mod = b["input_ids"], b["modality"]
        pos = (mod[0] == 1).nonzero().flatten()
        codes = ids[0, int(pos[0]):int(pos[-1]) + 1] - IMG_OFFSET
        assert codes.numel() == self.L_I, codes.numel()
        return codes.cpu()

    # --------------------------------------------------------- official sampler
    def official_t2i(self, caption: str, seed: int, steps: int = 50, cfg: float = 3.0, res: int | None = None):
        """Official maskgit sampler (50 steps, CFG 3.0, r_temp 4.5) for T2I: caption observed, image masked. Returns codes."""
        import numpy as _np
        from omegaconf import open_dict
        st = self.set_prompt(caption, n_txt=0, res=res)
        with open_dict(self.model.config):
            self.model.config.eval.cfg = cfg
        rec = {}
        orig = self.model.decode_sampling

        def grab(x, *a, **k):
            rec["x"] = x.clone()
            return [], []

        self.model.decode_sampling = grab
        torch.manual_seed(seed)
        _np.random.seed(seed)
        self.assert_eval()
        try:
            self.model._sample(text_only=False, num_steps=steps, batch_size_per_gpu=1,
                               example_batch=dict(input_ids=st["x0"], attention_mask=st["attention_mask"]), sample_batch_idx=0,
                               modality=st["modality"], sample_ids=st["sample_ids"], allow_interleaved_conditional=True,
                               x0_unmask=st["unmask"], x0=st["x0"])
        finally:
            self.model.decode_sampling = orig
        self.assert_eval()                       # the sampler must not have switched the backbone back to train mode
        x = rec["x"][0]
        codes = x[self.i0:self.i1 + 1] - IMG_OFFSET
        return codes.clamp(0, IMG_VOCAB - 1).cpu(), int((x == MASK_ID).sum())
