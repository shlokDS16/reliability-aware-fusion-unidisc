"""`OmniScorer`: the Omni-Diffusion binding with the interface of `exp_p2.scoring.UniScorer` that GATE needs for the IMAGE direction:
    L_I, caption_ids, build, logits_fn, preprocess, encode, decode, selfcheck, plus the proxy-friendly `rows` bookkeeping done by `runner.Counting`.

Contract with the gate stack (see exp_p2/omni/__init__.py): `build` and `logits_fn` live in the VIRTUAL id space (mask 32000, image 32001 + code, restricted slice [32001, 48385)), the
model sees real Omni ids. `logits_fn(st)(x)` returns logits [B, L, 48385] in which image columns 32001..40192 hold the Omni image-code logits already shifted by Dream's one-position
read-off (distribution of the token at position i = model output at i - 1) and every other column is -inf; so `scoring.masked_logprobs(..., lo=32001, hi=48385)` gives the log-softmax
over the 8192 valid codes. The text direction is NOT supported unless `text_logits=True` (not used by family R).

Layout (T2I, verified against the tokenizer string route and `apply_chat_template` by `selfcheck`; no system turn, as in tools/inference.py `default_system_message = []`):
  <|im_start|>user\\nGenerate an image based on the provided text description.\\n{caption}<|im_end|>\\n<|im_start|>assistant\\n<|begin_of_image|>{256 codes}<|end_of_image|><|im_end|>\\n
The caption is the contiguous cap_pos block; the image block is img_pos (256 positions at 256 px). Caption masked = those positions set to the mask id (OOD for Omni, see layout.py)."""
from __future__ import annotations

import numpy as np
import torch

from exp_p2.omni import layout as L
from exp_p2.scoring import MASK_ID as V_MASK, IMG_LO as V_IMG_LO


class OmniScorer:
    def __init__(self, model, tokenizer, magvit, *, grid: int = L.OMNI_GRID, micro_bs: int = 1, text_logits: bool = False, shift: int = 1, device=None, magvit_device: str = "cpu"):
        self.model, self.tokenizer, self.magvit = model, tokenizer, magvit
        self.tok = tokenizer
        self.grid, self.L_I = int(grid), int(grid) ** 2
        self.micro_bs, self.text_logits, self.shift = int(micro_bs), bool(text_logits), int(shift)
        self.magvit_device = magvit_device
        self.dev = torch.device(device) if device is not None else next(model.parameters()).device
        self.vmap = L.VirtualMap()
        self.struct = L.structural_ids(lambda s: list(tokenizer(s, add_special_tokens=False)["input_ids"]))
        for k in list(L.STRUCT_KEYS) + ["instr"]:                                  # stable low virtual ids for the structure tokens (debugging aid only)
            for r in self.struct[k]:
                self.vmap.v(r)
        mid = getattr(getattr(model, "config", None), "mask_token_id", L.OMNI_MASK_ID)
        if mid != L.OMNI_MASK_ID:
            raise ValueError(f"model.config.mask_token_id {mid} != {L.OMNI_MASK_ID}")
        self.n_forward_rows = 0

    # ------------------------------------------------------------------------------------------------ text front end
    def caption_ids(self, caption: str) -> list[int]:
        """Virtual ids of the caption tokens (the Omni tokenizer, no special tokens added). A caption that contains a special-token string is refused (ValueError)."""
        real = [int(i) for i in self.tok(caption, add_special_tokens=False)["input_ids"]]
        if any(r >= L.OMNI_FIRST_SPECIAL for r in real):
            raise ValueError("caption tokenises to a special or image token")
        return [self.vmap.v(r) for r in real]

    # ------------------------------------------------------------------------------------------------ layout
    def build(self, caption_tok: list[int], codes) -> dict:
        """Returns dict(base [L] long, mod [1, L], sid [1, L], cap_pos, img_pos) on the scorer's device, in the virtual id space."""
        codes = np.asarray(codes).reshape(-1)
        assert codes.size == self.L_I, (codes.size, self.L_I)
        cap_real = self.vmap.to_real_row(caption_tok)
        ids_real, cap0, img0, n_cap = L.real_row(self.struct, cap_real, codes)
        virt = self.vmap.to_virtual_row(ids_real, img0, self.L_I)
        base = torch.tensor(virt, dtype=torch.long)
        mod = torch.zeros_like(base)
        mod[img0:img0 + self.L_I] = 1
        d = self.dev
        return dict(base=base.to(d), mod=mod.to(d)[None], sid=torch.zeros_like(base).to(d)[None],
                    cap_pos=torch.arange(cap0, cap0 + n_cap, device=d), img_pos=torch.arange(img0, img0 + self.L_I, device=d))

    # ------------------------------------------------------------------------------------------------ the network
    @torch.no_grad()
    def raw_logits(self, real_ids: torch.Tensor) -> torch.Tensor:
        """Omni logits [B, L, 176264] for a REAL id batch, no shift. `forward_dream` is the path generation uses (attention_mask is ignored inside it: full bidirectional attention)."""
        out = self.model.forward_dream(input_ids=real_ids, attention_mask=None, use_cache=False, return_dict=True)
        return out.logits

    def logits_fn(self, st: dict):
        vmap = self.vmap

        @torch.no_grad()
        def f(x: torch.Tensor) -> torch.Tensor:
            if bool((x >= L.V_IMG_VALID_HI).any()):
                raise ValueError("virtual id in the padding columns of the image slice (code >= 8192)")
            table = vmap.table(x.device)
            parts = []
            for i in range(0, x.shape[0], self.micro_bs):
                xr = table[x[i:i + self.micro_bs]]
                lg = self.raw_logits(xr)
                parts.append(L.to_virtual_logits(lg, vmap, shift=self.shift, text_logits=self.text_logits))
                del lg
            self.n_forward_rows += int(x.shape[0])
            return parts[0] if len(parts) == 1 else torch.cat(parts)
        return f

    # ------------------------------------------------------------------------------------------------ image tokeniser
    def preprocess(self, pil):
        """Deterministic centre crop and 512 px resize, identical to UniScorer.preprocess, so that pixel corruptions (and their seeds) act on the same 512 px image as in family P."""
        from PIL import Image
        w, h = pil.size
        s = min(w, h)
        l, t = (w - s) // 2, (h - s) // 2
        return pil.convert("RGB").crop((l, t, l + s, t + s)).resize((512, 512), Image.BICUBIC)

    @torch.no_grad()
    def encode(self, pil) -> np.ndarray:
        """MAGVIT-v2 codes [L_I] of an image: resize to 256 px with torchvision's bicubic (the repo's `image_transform`, exactly), normalise to [-1, 1], `get_code`. A 512 px input
        is therefore the two-stage path crop-512 -> 256, which gives different codes from the repo's one-stage path (about 60 percent of codes agree, measured on 8 images,
        2026-10-28); clean and corrupted images always take the same path, which is what the changed-code labels need."""
        from torchvision import transforms
        im = pil.convert("RGB")
        res = self.grid * 16
        if im.size != (res, res):
            im = transforms.Resize(res, interpolation=transforms.InterpolationMode.BICUBIC)(im)
            im = transforms.CenterCrop((res, res))(im)
        x = transforms.Normalize([0.5] * 3, [0.5] * 3)(transforms.ToTensor()(im))[None].to(self.magvit_device)
        codes = self.magvit.get_code(x).reshape(-1).cpu().numpy().astype(np.int64)
        assert codes.size == self.L_I and codes.min() >= 0 and codes.max() < L.OMNI_N_CODES
        return codes

    @torch.no_grad()
    def decode(self, codes):
        z = torch.as_tensor(np.asarray(codes), dtype=torch.long)[None].to(self.magvit_device)
        img = self.magvit.decode_code(z)
        return ((img.clamp(-1, 1) + 1) / 2 * 255).round().byte()[0].permute(1, 2, 0).cpu().numpy()

    # ------------------------------------------------------------------------------------------------ one-off validation of the layout against the tokenizer routes
    def reference_row(self, caption: str, codes) -> list[int]:
        """Real ids by the training route (dataset_qwen2.py): tokenize(content) between the chat markers, image placeholder replaced by the id strings."""
        enc = lambda s: [int(i) for i in self.tok(s, add_special_tokens=False)["input_ids"]]            # noqa: E731
        S = self.struct
        user = S["im_start"] + S["user"] + S["nl"] + enc(L.T2I_INSTRUCTION + caption) + S["im_end"] + S["nl"]
        content = "<|begin_of_image|>" + "".join(f"<|image_{int(c)}|>" for c in np.asarray(codes).reshape(-1)) + "<|end_of_image|>"
        return user + S["im_start"] + S["assistant"] + S["nl"] + enc(content) + S["im_end"] + S["nl"]

    @torch.no_grad()
    def selfcheck(self, pil, caption: str) -> dict:
        """Same keys as UniScorer.selfcheck (the runner requires ids_equal, modality_equal, image_tokens_frac_equal >= 0.99) plus Omni-specific ones."""
        codes = self.encode(self.preprocess(pil))
        st = self.build(self.caption_ids(caption), codes)
        mine = self.vmap.to_real_row(st["base"].cpu().tolist())
        ref = self.reference_row(caption, codes)
        ids_equal = bool(mine == ref)
        out = dict(ids_equal=ids_equal, len_ref=len(ref), len_mine=len(mine), n_cap=int(len(st["cap_pos"])))
        isimg = [L.OMNI_IMG_OFFSET <= r < L.OMNI_IMG_OFFSET + L.OMNI_N_CODES for r in ref]
        out["modality_equal"] = bool(len(ref) == len(mine) and [int(m) for m in st["mod"][0].cpu().tolist()] == [int(v) for v in isimg])
        rc = [r - L.OMNI_IMG_OFFSET for r, v in zip(ref, isimg) if v]
        out["image_tokens_frac_equal"] = float(np.mean(np.asarray(rc) == codes)) if len(rc) == codes.size else 0.0
        if hasattr(self.tok, "apply_chat_template"):
            chat = self.tok.apply_chat_template([{"role": "user", "content": L.T2I_INSTRUCTION + caption}], tokenize=True, add_generation_prompt=True)
            out["chat_template_prompt_equal"] = bool(list(chat) == mine[:len(chat)])
        out["mask_row_roundtrip"] = bool(self._mask_roundtrip(st))
        return out

    def _mask_roundtrip(self, st) -> bool:
        x = st["base"].clone()
        x[st["cap_pos"]] = V_MASK
        x[st["img_pos"][:3]] = V_MASK
        real = self.vmap.table(x.device)[x].cpu().tolist()
        cap0, img0 = int(st["cap_pos"][0]), int(st["img_pos"][0])
        return all(real[p] == L.OMNI_MASK_ID for p in list(range(cap0, cap0 + len(st["cap_pos"]))) + [img0, img0 + 1, img0 + 2]) and real[img0 + 3] != L.OMNI_MASK_ID
