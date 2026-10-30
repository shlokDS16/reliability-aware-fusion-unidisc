"""Pure layout and id-space logic of the Omni adapter (torch + numpy only; no transformers, no model).

Source facts (all E3, Omni-Diffusion at c4f4625f84197a72d556ea00f10e5b2775524252; snapshot lijiang/Omni-Diffusion 2233ee1a...):
  * mask id 151666 = config.json mask_token_id = tokenizer "<|mask|>" = `mask_id = 151666` in omni_diffusion/data/dataset_qwen2.py:938;
  * image codes: tokens "<|image_0|>".."<|image_8191|>" = ids 168072..176263 (added_tokens.json), 8192 codes (MAGVIT-v2 LFQ, 13 bits);
  * the logit shift: models/dream/generation_utils.py `_sample`: `logits = torch.cat([logits[:, :1], logits[:, :-1]], dim=1)` right after `forward_dream`; i.e. the distribution of the
    token AT position i is read from the model output at position i - 1 (output 0 is reused for position 0). Training uses the same convention (modeling_dream.py `forward` ->
    `self.loss_function(logits, labels, ...)`, the standard causal-LM loss, which pairs logits[i] with labels[i + 1]);
  * the T2I training/inference layout: dataset_qwen2.py (user turn "Generate an image based on the provided text description.\\n" + caption; assistant turn
    "<|begin_of_image|>" + 256 image tokens at 256 px + "<|end_of_image|>", then "<|im_end|>", "\\n"); the official demo generates 260 = 1 + 256 + 1 + 2 tokens.
Training masks only assistant (label) positions (dataset_qwen2.py:932-942); the user turn is never masked. Masking the caption (what B and D need) is therefore OUT of the training
distribution; the adapter implements the contexts the SAP defines, the positive control (AB.5 item 2) is the only evidence that they still carry signal.
"""
from __future__ import annotations

import numpy as np
import torch

from exp_p2.scoring import MASK_ID as V_MASK, IMG_LO as V_IMG_LO, IMG_HI as V_IMG_HI, TEXT_HI as V_TEXT_HI

OMNI_MASK_ID = 151666
OMNI_IMG_OFFSET = 168072
OMNI_N_CODES = 8192
OMNI_VOCAB = 176264
OMNI_FIRST_SPECIAL = 151643            # "<|endoftext|>": every ordinary text id of a caption is below this
OMNI_GRID, OMNI_L_I = 16, 256          # 256 px / 16 = 16 x 16 tokens (the generation resolution; dataset_qwen2.py:759-766 uses 256 for assistant images)
T2I_INSTRUCTION = "Generate an image based on the provided text description.\n"
V_IMG_VALID_HI = V_IMG_LO + OMNI_N_CODES      # virtual columns [V_IMG_LO, V_IMG_VALID_HI) are real; [V_IMG_VALID_HI, V_IMG_HI) are -inf padding

STRUCT_KEYS = ("im_start", "im_end", "nl", "user", "assistant", "boi", "eoi")


def structural_ids(encode) -> dict[str, list[int]]:
    """encode: str -> list[int] (tokenizer without special tokens added). Returns the structural id lists; the seven specials must be single tokens except user/assistant/nl which are checked too."""
    s = {"im_start": encode("<|im_start|>"), "im_end": encode("<|im_end|>"), "nl": encode("\n"), "user": encode("user"), "assistant": encode("assistant"),
         "boi": encode("<|begin_of_image|>"), "eoi": encode("<|end_of_image|>"), "instr": encode(T2I_INSTRUCTION)}
    for k in STRUCT_KEYS:
        if len(s[k]) != 1:
            raise ValueError(f"structural token {k} is not a single id: {s[k]}")
    return s


def real_row(struct: dict, caption_real: list[int], codes) -> tuple[list[int], int, int, int]:
    """Real-id row of the T2I layout. Returns (ids, cap_start, img_start, n_cap):
        <|im_start|> user \\n INSTR CAPTION <|im_end|> \\n <|im_start|> assistant \\n <|begin_of_image|> [codes] <|end_of_image|> <|im_end|> \\n"""
    pre = struct["im_start"] + struct["user"] + struct["nl"] + struct["instr"]
    cap0 = len(pre)
    mid = struct["im_end"] + struct["nl"] + struct["im_start"] + struct["assistant"] + struct["nl"] + struct["boi"]
    img0 = cap0 + len(caption_real) + len(mid)
    codes = [int(c) for c in np.asarray(codes).reshape(-1)]
    if any(c < 0 or c >= OMNI_N_CODES for c in codes):
        raise ValueError("image code outside [0, 8192)")
    ids = pre + list(caption_real) + mid + [OMNI_IMG_OFFSET + c for c in codes] + struct["eoi"] + struct["im_end"] + struct["nl"]
    return ids, cap0, img0, len(caption_real)


class VirtualMap:
    """Injective map between real Omni ids of text/structure tokens and virtual ids in [0, 32000). The mask and the image codes are mapped arithmetically.
    The map only lives inside one process: nothing stored on disk contains a virtual text id (arrays hold image codes, scores and flags)."""

    def __init__(self):
        self.v2r: list[int] = []
        self.r2v: dict[int, int] = {}
        self._tables: dict[str, tuple[int, torch.Tensor]] = {}

    def v(self, real: int) -> int:
        real = int(real)
        if real == OMNI_MASK_ID or OMNI_IMG_OFFSET <= real < OMNI_IMG_OFFSET + OMNI_N_CODES:
            raise ValueError(f"real id {real} is the mask or an image code; it is not a text/structure token")
        got = self.r2v.get(real)
        if got is None:
            if len(self.v2r) >= V_TEXT_HI:
                raise OverflowError("more than 32000 distinct text ids in one process")
            got = len(self.v2r)
            self.r2v[real] = got
            self.v2r.append(real)
        return got

    def to_virtual_row(self, real_ids: list[int], img0: int, n_img: int) -> list[int]:
        out = []
        for i, r in enumerate(real_ids):
            if img0 <= i < img0 + n_img:
                out.append(V_IMG_LO + (r - OMNI_IMG_OFFSET))
            else:
                out.append(self.v(r))
        return out

    def to_real_row(self, virtual_ids) -> list[int]:
        """Inverse of `to_virtual_row` for a row without masks (used by the checks)."""
        out = []
        for x in (int(i) for i in virtual_ids):
            if x == V_MASK:
                out.append(OMNI_MASK_ID)
            elif V_IMG_LO <= x < V_IMG_VALID_HI:
                out.append(OMNI_IMG_OFFSET + (x - V_IMG_LO))
            elif 0 <= x < len(self.v2r):
                out.append(self.v2r[x])
            else:
                raise ValueError(f"virtual id {x} is not allocated")
        return out

    def table(self, device) -> torch.Tensor:
        """Lookup tensor [V_IMG_HI] virtual -> real id (unallocated text slots map to <|endoftext|>, which is never read because no row contains them)."""
        key = str(device)
        n = len(self.v2r)
        hit = self._tables.get(key)
        if hit is not None and hit[0] == n:
            return hit[1]
        t = torch.full((V_IMG_HI,), OMNI_FIRST_SPECIAL, dtype=torch.long)
        if n:
            t[:n] = torch.tensor(self.v2r, dtype=torch.long)
        t[V_MASK] = OMNI_MASK_ID
        t[V_IMG_LO:V_IMG_VALID_HI] = OMNI_IMG_OFFSET + torch.arange(OMNI_N_CODES)
        t[V_IMG_VALID_HI:V_IMG_HI] = OMNI_MASK_ID           # padding columns: never present in a row (asserted by the scorer)
        t = t.to(device)
        self._tables[key] = (n, t)
        return t


def shift_right(t: torch.Tensor, s: int = 1) -> torch.Tensor:
    """Dream read-off: out[:, i] = t[:, i - s] for i >= s, out[:, i] = t[:, 0] for i < s. s = 1 is exactly `torch.cat([t[:, :1], t[:, :-1]], dim=1)` of generation_utils.py. s = 0 is the identity."""
    if s == 0:
        return t
    return torch.cat([t[:, :1].expand(-1, s, -1), t[:, :-s]], dim=1)


def to_virtual_logits(lg: torch.Tensor, vmap: VirtualMap | None = None, *, shift: int = 1, text_logits: bool = False) -> torch.Tensor:
    """Omni logits [B, L, 176264] (output position i) -> virtual logits [B, L, V_IMG_HI] (distribution of the token at position i), after the one-position shift.
    Image columns: virtual 32001 + k <- Omni image column k for k < 8192, -inf beyond. Mask column and (unless text_logits) the text columns are -inf; with text_logits the allocated
    text slots get the real logits of their tokens (so the text direction would work too; the family R runner never uses it)."""
    B, L, _ = lg.shape
    out = torch.full((B, L, V_IMG_HI), float("-inf"), dtype=lg.dtype, device=lg.device)
    out[..., V_IMG_LO:V_IMG_VALID_HI] = shift_right(lg[..., OMNI_IMG_OFFSET:OMNI_IMG_OFFSET + OMNI_N_CODES], shift)
    if text_logits:
        if vmap is None or not vmap.v2r:
            raise ValueError("text_logits needs a VirtualMap with allocated text ids")
        cols = torch.tensor(vmap.v2r, dtype=torch.long, device=lg.device)
        out[..., :len(vmap.v2r)] = shift_right(lg[..., cols], shift)
    return out
