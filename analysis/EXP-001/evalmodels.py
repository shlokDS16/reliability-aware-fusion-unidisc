"""Evaluation models, loaded one at a time from pinned local copies, offline, in the EVAL venv (card 9 item 9; 7.1, 7.2, 7.3).

CLIP ViT-L/14: openai/clip-vit-large-patch14 at the revision recorded in the manifest; text truncated at 77 tokens (rate reported);
the checkpoint's own image preprocessing. CLIP-IQA: Wang et al. 2023 formulation with the same pinned CLIP weights (prompt pair
'Good photo.' / 'Bad photo.', logit scale 100, score = softmax probability of the first prompt). VLM: Qwen3-VL-2B-Instruct;
P(Yes) is the two-way softmax of the 'Yes' and 'No' answer logits at the first answer position (case variants pooled by
logsumexp); the template is frozen in vlm_prompt.txt.
"""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import numpy as np
import torch

HF_EVAL = Path(r"C:\Users\Shlok\.cache\dlm_dl\hf_eval")
CLIP_REV = "32bd64288804d66eefd0ccbe215aa642df71cc41"      # openai/clip-vit-large-patch14
VLM_REV = "89644892e4d85e24eaac8bacfd4f463576704203"       # Qwen/Qwen3-VL-2B-Instruct (Apache-2.0)
CLIP_DIR = HF_EVAL / "models--openai--clip-vit-large-patch14" / "snapshots" / CLIP_REV
VLM_DIR = HF_EVAL / "models--Qwen--Qwen3-VL-2B-Instruct" / "snapshots" / VLM_REV
HERE = Path(__file__).resolve().parent


DEFAULT_DEVICE = os.environ.get("EXP001_EVAL_DEVICE", "cuda")


class ClipScorer:
    def __init__(self, path=CLIP_DIR, device=DEFAULT_DEVICE):
        from transformers import CLIPModel, CLIPProcessor
        self.proc = CLIPProcessor.from_pretrained(str(path))
        self.dtype = torch.float16 if device == "cuda" else torch.float32
        self.model = CLIPModel.from_pretrained(str(path), torch_dtype=self.dtype).to(device).eval()
        self.device = device
        self.truncated = 0

    @torch.no_grad()
    def images(self, pils, bs=16):
        out = []
        for i in range(0, len(pils), bs):
            px = self.proc(images=pils[i:i + bs], return_tensors="pt")["pixel_values"].to(self.device, self.dtype)
            f = self.model.get_image_features(pixel_values=px)
            f = f.pooler_output if hasattr(f, "pooler_output") else f
            out.append(torch.nn.functional.normalize(f.float(), dim=-1).cpu())
        return torch.cat(out).numpy().astype(np.float64)

    @torch.no_grad()
    def texts(self, caps, bs=64):
        out = []
        tok = self.proc.tokenizer
        for i in range(0, len(caps), bs):
            chunk = caps[i:i + bs]
            ids = tok(chunk, padding=True, truncation=False)["input_ids"]
            self.truncated += sum(len(x) > 77 for x in ids)
            enc = tok(chunk, padding="max_length", truncation=True, max_length=77, return_tensors="pt").to(self.device)
            f = self.model.get_text_features(**enc)
            f = f.pooler_output if hasattr(f, "pooler_output") else f
            out.append(torch.nn.functional.normalize(f.float(), dim=-1).cpu())
        return torch.cat(out).numpy().astype(np.float64)

    @torch.no_grad()
    def iqa(self, pils, bs=16):
        """CLIP-IQA score per image in [0, 1] (probability of 'Good photo.' against 'Bad photo.')."""
        t = self.texts(["Good photo.", "Bad photo."])
        te = torch.tensor(t, dtype=torch.float32)
        out = []
        for i in range(0, len(pils), bs):
            e = torch.tensor(self.images(pils[i:i + bs]), dtype=torch.float32)
            logits = 100.0 * e @ te.T
            out.append(logits.softmax(-1)[:, 0])
        return torch.cat(out).numpy().astype(np.float64)


class VlmScorer:
    def __init__(self, path=VLM_DIR, device=DEFAULT_DEVICE, max_pixels=512 * 512):
        from transformers import AutoProcessor, AutoModelForImageTextToText
        self.proc = AutoProcessor.from_pretrained(str(path), min_pixels=64 * 32 * 32, max_pixels=max_pixels)
        self.model = AutoModelForImageTextToText.from_pretrained(str(path), torch_dtype=torch.bfloat16).to(device).eval()
        self.device = device
        tok = self.proc.tokenizer
        self.yes = sorted({tok.encode(w, add_special_tokens=False)[0] for w in ("Yes", "yes", " Yes", " yes")})
        self.no = sorted({tok.encode(w, add_special_tokens=False)[0] for w in ("No", "no", " No", " no")})
        self.template = (HERE / "vlm_prompt.txt").read_text(encoding="utf8").rstrip("\n")
        self.presence_template = (HERE / "vlm_presence_prompt.txt").read_text(encoding="utf8").rstrip("\n")

    @torch.no_grad()
    def p_yes(self, pil, question: str) -> float:
        msgs = [{"role": "user", "content": [{"type": "image", "image": pil}, {"type": "text", "text": question}]}]
        inp = self.proc.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors="pt")
        inp = {k: (v.to(self.device) if hasattr(v, "to") else v) for k, v in inp.items()}
        logits = self.model(**inp).logits[0, -1].float()
        ly = torch.logsumexp(logits[self.yes], 0)
        ln = torch.logsumexp(logits[self.no], 0)
        return float(torch.sigmoid(ly - ln))

    def vqa_score(self, pil, caption: str) -> float:
        return self.p_yes(pil, self.template.replace("{}", caption))

    def presence(self, pil, noun: str) -> float:
        return self.p_yes(pil, self.presence_template.replace("{noun}", noun))
