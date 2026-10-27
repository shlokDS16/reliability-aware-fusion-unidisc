"""Masked log-likelihood scoring with UniDisc (batched). `masked_logprobs` is model-agnostic (takes a logits callable) and unit-tested with a
fake network; `UniScorer` binds it to the UniDisc 1.4B wrapper of exp001 (generation venv only).

Conventions (all fixed here, none tuned):
  * a masked position's distribution is a fp32 log-softmax of the raw bf16 logits restricted to the vocabulary of its modality:
    text ids [0, 32000) (the mask id 32000 excluded) and image ids [32001, 48385). This is the conditional given that the position
    holds a token of that modality (the layout fixes the modality of every position).
  * the backbone runs in eval mode, bf16 (the project standard, EXP-001), batch of up to `bs` rows.
"""
from __future__ import annotations

import io
from dataclasses import dataclass

import numpy as np
import torch

TEXT_LO, TEXT_HI = 0, 32000          # text vocabulary without the mask id (32000)
IMG_LO, IMG_HI = 32001, 48385        # image ids 32001 + code
MASK_ID = 32000
IMG_OFFSET = 32001
IMG_VOCAB = 16384
SDPA_BS = 4                          # measured best throughput at ~1.1k tokens (0.11 s per row; B=8 is not faster)


@dataclass
class Spec:
    """One forward row: mask `pos` (the scored positions) plus `extra` (positions masked in this row but not scored); scored with vocab [lo, hi)."""
    pos: torch.Tensor
    lo: int
    hi: int
    extra: torch.Tensor | None = None


@torch.no_grad()
def masked_logprobs(forward_logits, base: torch.Tensor, specs: list[Spec], bs: int = SDPA_BS, mask_id: int = MASK_ID):
    """Yield, for each spec in order, the fp32 log-softmax matrix [len(pos), hi - lo] at the scored positions.
    forward_logits(x [B, L] long) -> logits [B, L, V]. `base` [L] holds the observed tokens (also at the scored positions: it supplies
    the targets for the caller, it is replaced by the mask id in the row)."""
    for s0 in range(0, len(specs), bs):
        chunk = specs[s0:s0 + bs]
        x = base.unsqueeze(0).repeat(len(chunk), 1)
        for b, sp in enumerate(chunk):
            x[b, sp.pos] = mask_id
            if sp.extra is not None and len(sp.extra):
                x[b, sp.extra] = mask_id
        logits = forward_logits(x)
        for b, sp in enumerate(chunk):
            yield torch.log_softmax(logits[b, sp.pos, sp.lo:sp.hi].float(), dim=-1)


def gather_true(lp: torch.Tensor, base: torch.Tensor, pos: torch.Tensor, lo: int):
    """lp [n, V] from masked_logprobs -> (log p of the observed token, max probability) per scored position."""
    tgt = (base[pos] - lo).clamp(min=0)
    return lp.gather(1, tgt[:, None])[:, 0], lp.max(dim=1).values.exp()


# ----------------------------------------------------------------------------------------------------------------- UniDisc binding
class UniScorer:
    def __init__(self, net):
        from exp001.config import IMG_OFFSET as IO
        assert IO == IMG_OFFSET
        self.net = net
        self.model = net.model
        self.tok = net.model.tokenizer
        self.dev = torch.device("cuda")
        self.L_I = net.L_I                                       # 1024 at 512 px
        self._template()

    # ---- layout:  <s> system </s> <s> CAPTION </s> <s> <image-marker 811> [1024 image ids] </s>   (the demo layout, no masked tail)
    def _template(self):
        from demo.inference_utils import messages_to_batch
        from PIL import Image
        msgs = [dict(type="text", text="a", role="user"), dict(type="image_url", image_url=Image.new("RGB", (512, 512), (0, 0, 0)), role="assistant")]
        import contextlib
        import os
        with contextlib.redirect_stdout(io.StringIO()):
            b = messages_to_batch(self.net.cfg, self.tok, self.model, msgs, resolution=512)
        ids = b["input_ids"][0].cpu()
        bos = (ids == 1).nonzero().flatten().tolist()
        assert len(bos) == 3, bos
        self.sys_ids = ids[:bos[1]].tolist()                     # <s> system </s>
        assert self.sys_ids[0] == 1 and self.sys_ids[-1] == 2
        assert ids[bos[2] + 1].item() == 811
        self.marker = 811

    def caption_ids(self, caption: str) -> list[int]:
        return self.tok(caption, add_special_tokens=False)["input_ids"]

    def build(self, caption_tok: list[int], codes: np.ndarray | torch.Tensor):
        """Returns dict(base [L] long cuda, mod [L], cap_pos, img_pos (long cuda))."""
        codes = torch.as_tensor(np.asarray(codes), dtype=torch.long)
        assert codes.numel() == self.L_I
        head = self.sys_ids + [1] + list(caption_tok) + [2, 1, self.marker]
        cap0 = len(self.sys_ids) + 1
        i0 = len(head)
        ids = torch.cat([torch.tensor(head, dtype=torch.long), codes + IMG_OFFSET, torch.tensor([2], dtype=torch.long)])
        mod = torch.zeros_like(ids)
        mod[i0:i0 + self.L_I] = 1
        dev = self.dev
        return dict(base=ids.to(dev), mod=mod.to(dev)[None], sid=torch.zeros_like(ids).to(dev)[None],
                    cap_pos=torch.arange(cap0, cap0 + len(caption_tok), device=dev), img_pos=torch.arange(i0, i0 + self.L_I, device=dev))

    def logits_fn(self, st):
        mod, sid = st["mod"], st["sid"]

        def f(x):
            B = x.shape[0]
            return self.model.forward(x=x, sigma=None, modality=mod.expand(B, -1), sample_ids=sid.expand(B, -1), block_mask=True, return_logits=True)
        return f

    # ---- image tokeniser (the demo's own LlamaGen VQ-16 path, deterministic centre crop)
    @torch.no_grad()
    def preprocess(self, pil):
        w, h = pil.size
        s = min(w, h)
        l, t = (w - s) // 2, (h - s) // 2
        from PIL import Image
        return pil.convert("RGB").crop((l, t, l + s, t + s)).resize((512, 512), Image.BICUBIC)

    @torch.no_grad()
    def encode(self, pil512) -> np.ndarray:
        from unidisc.tokenizers.image_tokenizers import get_image_batch
        arr = torch.from_numpy(np.array(pil512.convert("RGB"))).permute(2, 0, 1)[None].float() / 255.0
        ids = get_image_batch(self.model.config, self.model.get_vae(), {"img": arr}, self.model.device)
        ids = ids.reshape(-1).cpu().numpy().astype(np.int64)
        return ids

    def decode(self, codes):
        return self.net.decode_image(np.asarray(codes))

    # ---- one-off validation of the hand-built layout, the tokeniser path and the fp32 restricted log-softmax against the repo's own path
    @torch.no_grad()
    def selfcheck(self, pil, caption: str) -> dict:
        import contextlib
        from demo.inference_utils import messages_to_batch
        img512 = self.preprocess(pil)
        codes = self.encode(img512)
        with contextlib.redirect_stdout(io.StringIO()):
            b = messages_to_batch(self.net.cfg, self.tok, self.model,
                                  [dict(type="text", text=caption, role="user"), dict(type="image_url", image_url=img512, role="assistant")], resolution=512)
        ref = b["input_ids"][0].cpu()
        st = self.build(self.caption_ids(caption), codes)
        mine = st["base"].cpu()
        same_len = bool(ref.shape == mine.shape)
        ids_equal = bool(same_len and (ref == mine).all())
        mod_equal = bool(same_len and (b["modality"][0].cpu() == st["mod"][0].cpu()).all())
        out = dict(ids_equal=ids_equal, modality_equal=mod_equal, len_ref=int(ref.shape[0]), len_mine=int(mine.shape[0]), n_cap=int(len(st["cap_pos"])))
        if not same_len:
            return out
        out["image_tokens_equal"] = bool((ref[st["img_pos"].cpu()] == mine[st["img_pos"].cpu()]).all())
        # compare my fp32 restricted log-probs with model.forward's own bf16 log-probs at masked positions
        g = torch.Generator().manual_seed(0)
        cp = st["cap_pos"][torch.randperm(len(st["cap_pos"]), generator=g)[:4].to(self.dev)]
        ip = st["img_pos"][torch.randperm(self.L_I, generator=g)[:64].to(self.dev)]
        pos = torch.cat([cp, ip])
        x = st["base"].clone()
        x[pos] = MASK_ID
        lp_ref = self.model.forward(x=x[None], sigma=None, modality=st["mod"], sample_ids=st["sid"], block_mask=True)[0].float()
        logits = self.logits_fn(st)(x[None])
        mine_t = torch.log_softmax(logits[0, cp, TEXT_LO:TEXT_HI].float(), -1).gather(1, (st["base"][cp])[:, None])[:, 0]
        mine_i = torch.log_softmax(logits[0, ip, IMG_LO:IMG_HI].float(), -1).gather(1, (st["base"][ip] - IMG_LO)[:, None])[:, 0]
        ref_t = lp_ref[cp, st["base"][cp]]
        ref_i = lp_ref[ip, st["base"][ip]]
        out.update(max_abs_diff_text=float((mine_t - ref_t).abs().max()), max_abs_diff_img=float((mine_i - ref_i).abs().max()),
                   mean_diff_text=float((mine_t - ref_t).mean()), mean_diff_img=float((mine_i - ref_i).mean()),
                   mean_lp_text=float(mine_t.mean()), mean_lp_img=float(mine_i.mean()))
        return out
