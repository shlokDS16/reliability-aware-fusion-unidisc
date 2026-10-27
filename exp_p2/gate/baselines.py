"""Cheap detection baselines of v2 section 4.2. Suspicion convention: higher = more suspicious (so AUROC against Z is oriented).

  patch texture      pixel luminance variance of the (H/grid) x (W/grid) pixel patch of token j in the OBSERVED image  [CPU]
  neighbour codebook mean L2 distance between the codebook vector of token j and those of its (up to 8) grid neighbours [CPU, needs codebook]
  code rarity        -log frequency of the observed code among the calibration fold's clean codes (Laplace smoothed)    [CPU]
  s3                 1 - max_y p(y) from the B passes (Dropout-Decoding-inspired only; not called Dropout Decoding)       [from B passes]
  plain-B top-k      -B_j, flag the top |G| (GATE without calibration, equal size)                                        [from B passes]
  TbV-score (non-finetuned)  -log p(observed code | nothing masked in the image, caption masked), from the RAW logits  [1 pass; scores.tbv_score_raw_logits]
  random             uniform noise (floor)
For token-level corruptions (patch, swap) there is no observed pixel image; callers pass pix=None and get NaN for the texture baseline.
"""
from __future__ import annotations

import numpy as np


def patch_texture(pix: np.ndarray | None, grid: int) -> np.ndarray:
    """pix: uint8 [H, W, 3] (or None). Returns [grid*grid] luminance variance per patch (Rec. 601 weights), NaN if pix is None."""
    if pix is None:
        return np.full(grid * grid, np.nan)
    a = np.asarray(pix, np.float64)
    lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    H, W = lum.shape
    ph, pw = H // grid, W // grid
    t = lum[:ph * grid, :pw * grid].reshape(grid, ph, grid, pw).transpose(0, 2, 1, 3).reshape(grid * grid, ph * pw)
    return t.var(axis=1)


def neighbour_codebook_distance(codes: np.ndarray, codebook: np.ndarray | None, grid: int) -> np.ndarray:
    """Mean L2 distance from e(code_j) to e(code_k) over the existing 8-neighbourhood k of j (edges have fewer neighbours). NaN without codebook."""
    if codebook is None:
        return np.full(grid * grid, np.nan)
    e = np.asarray(codebook, np.float64)[np.asarray(codes, np.int64)].reshape(grid, grid, -1)
    tot = np.zeros((grid, grid))
    cnt = np.zeros((grid, grid))
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ys, ye = max(0, -dy), grid - max(0, dy)
            xs, xe = max(0, -dx), grid - max(0, dx)
            a = e[ys:ye, xs:xe]
            b = e[ys + dy:ye + dy, xs + dx:xe + dx]
            tot[ys:ye, xs:xe] += np.linalg.norm(a - b, axis=-1)
            cnt[ys:ye, xs:xe] += 1
    return (tot / cnt).reshape(-1)


class CodeFreq:
    """Code frequencies of clean images (calibration fold). `rarity(codes)` = -log((count + 1) / (total + vocab))."""

    def __init__(self, counts: np.ndarray):
        self.counts = np.asarray(counts, np.float64)
        self.total = float(self.counts.sum())

    @staticmethod
    def fit(code_arrays, vocab: int, exclude: int | None = None) -> "CodeFreq":
        """Fit on a list of clean code arrays. `exclude` drops one array by position (leave-one-item-out, used when the same items are scored)."""
        c = np.zeros(vocab)
        for i, a in enumerate(code_arrays):
            if exclude is not None and i == exclude:
                continue
            c += np.bincount(np.asarray(a, np.int64), minlength=vocab)
        return CodeFreq(c)

    def rarity(self, codes) -> np.ndarray:
        v = len(self.counts)
        return -np.log((self.counts[np.asarray(codes, np.int64)] + 1.0) / (self.total + v))


def s3_from_maxp(maxp: np.ndarray) -> np.ndarray:
    return 1.0 - np.asarray(maxp, np.float64)


def tbv_suspicion(obs_logp: np.ndarray | None, m: int) -> np.ndarray:
    return np.full(m, np.nan) if obs_logp is None else -np.asarray(obs_logp, np.float64)


TBV_LABEL = "TbV-score (non-finetuned)"          # the only name this arm may carry in outputs; never 'the Trust but Verify baseline' (TbV needs its own finetune)


def copy_through_stat(obs_logp: np.ndarray) -> dict:
    """U7 diagnostic for the TbV-score (non-finetuned): if the network copies visible inputs, exp(obs_logp) is near 1 for (almost) every token."""
    p = np.exp(np.asarray(obs_logp, np.float64))
    return dict(label=TBV_LABEL, mean_p_obs=float(p.mean()), frac_p_obs_gt_0p99=float((p > 0.99).mean()), copy_suspected=bool((p > 0.99).mean() > 0.9))


def extract_codebook(vae) -> np.ndarray | None:
    """Best effort: LlamaGen-style VQ models keep the codebook at `quantize.embedding.weight`. UNVERIFIED for UniDisc's wrapper (no model is loaded
    in the CPU session that wrote this); returns None if the attribute path is absent so the baseline becomes NaN and the reason is logged."""
    try:
        w = vae.quantize.embedding.weight
        return w.detach().float().cpu().numpy()
    except AttributeError:
        return None
