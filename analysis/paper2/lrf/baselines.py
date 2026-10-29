"""A6.6 industry baselines CLIP and SigLIP (descriptive only; NO test against LRF). A6.11 item 6 specifies this as a separate script; this file holds the pinned constants, the decision rule and the descriptive summary
(all pure, CPU, tested on synthetic scores). The model loading, the pixel regeneration and the pixel-parity positive control are TODO markers: they need the GPU-free but download-requiring models (sizes not checked; the lead
confirms the download, A6.6) and are not part of the audited A6.11 deliverable of this branch.

Decision (A6.6): Y = 1[s(image, c+) > s(image, c-)], ties wrong. CLIP: cosine of the normalised embeddings; SigLIP: the pairwise logit (monotone in the cosine, so the same decision).
Reported, descriptive, no p-value: accuracy per model and condition and the clean-to-corrupted drop with a paired bootstrap CI, beside the drops of UniDisc NONE and LRF. Wording: "for reference", never "LRF is more robust than CLIP"."""
from __future__ import annotations

import numpy as np

MODELS = {
    "clip": dict(id="openai/clip-vit-large-patch14", revision="32bd64288804d66eefd0ccbe215aa642df71cc41"),
    "siglip": dict(id="google/siglip-so400m-patch14-384", revision="9fdffc58afc957d1a03a25b10dba0329ab15c2a3", licence="Apache-2.0"),
}                                                                            # ids and revisions as verified on the Hugging Face API 2026-10-29 (A6.6)
PARITY_MIN_AGREEMENT = 0.98                                                  # A6.6: VQ re-encode of the regenerated image vs the stored codes, on 5 items


def decide(s_pos, s_neg) -> np.ndarray:
    """Y = 1[s(image, c+) > s(image, c-)]; a tie is wrong."""
    return (np.asarray(s_pos, np.float64) > np.asarray(s_neg, np.float64)).astype(int)


def summarise(y_by_condition: dict[str, np.ndarray], rng: np.random.Generator, n_boot: int = 10000, clean: str = "clean") -> dict:
    """Accuracy per condition and the paired clean-to-corrupted drop (clean minus corrupted accuracy) with a 95 percent percentile bootstrap CI over items. Descriptive: no p-value."""
    out = {}
    yc = np.asarray(y_by_condition[clean], float)
    for cond, y in y_by_condition.items():
        y = np.asarray(y, float)
        row = dict(n=int(len(y)), acc=float(y.mean()))
        if cond != clean:
            d = yc - y
            idx = rng.integers(0, len(d), size=(n_boot, len(d)))
            lo, hi = np.quantile(d[idx].mean(axis=1), [0.025, 0.975])
            row.update(drop=float(d.mean()), drop_ci95=[float(lo), float(hi)])
        out[cond] = row
    return out


def pixel_parity_ok(agreement_per_image: list[float]) -> bool:
    """A6.6 positive control: every one of the checked images agrees with the stored codes on at least PARITY_MIN_AGREEMENT of the tokens."""
    return bool(len(agreement_per_image) > 0 and min(agreement_per_image) >= PARITY_MIN_AGREEMENT)


# TODO(A6.6, separate step, needs the lead's download go-ahead): load MODELS[...] at the pinned revisions through transformers with the model's own processor (fp32 CPU or fp16 GPU, recorded);
# regenerate the corrupted images with corruptions.apply_pixel(corr, sev, pil, rung_rng(gid, corr, rung), donor) and donor_for on the L fold (LG cells: suite.apply_corruption with the item-derived seed),
# run the parity check on 5 items with UniDisc's VQ, score the 520 items x conditions, and write a predictions file for `summarise`. Never during a GPU stage (A6.6).
