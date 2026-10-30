"""Pixel- and token-level corruptions and the denoise defence arm (v2 sections 4.3, 7.3). Pure PIL/numpy/OpenCV, no model.

Realistic (pixel level, then tokenised by the caller with `sc.encode`): jpeg (quality ladder 10, 5), noise (Gaussian sigma ladder 0.10, 0.20 on
[0,1] pixels), splice (a s x s pixel region copied from another COCO image to a uniformly random location; s = 128, 192).
Sanity (token level): patch (random codes in a block), swap (uniform random codes at a fraction of positions); both reuse `core`.
`jpeg` and `noise` reproduce `run_probe2.corrupt` exactly (same calls); tests/exp_p2/test_gate_corruptions.py checks this.
"""
from __future__ import annotations

import io

import numpy as np

from exp_p2 import core


def jpeg(pil512, quality: int):
    from PIL import Image
    buf = io.BytesIO()
    pil512.save(buf, format="JPEG", quality=int(quality))
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def gaussian_noise(pil512, sigma: float, rng: np.random.Generator):
    from PIL import Image
    a = np.asarray(pil512, dtype=np.float32) / 255.0
    a = np.clip(a + rng.normal(0.0, sigma, size=a.shape).astype(np.float32), 0.0, 1.0)
    return Image.fromarray(np.rint(a * 255.0).astype(np.uint8))


def splice(pil512, donor512, size: int, rng: np.random.Generator):
    """Copy a size x size region of `donor512` (taken at a uniformly random location) into `pil512` at another uniformly random location.
    Both images are 512 x 512 after `preprocess`. Returns (image, dict(src=(y,x), dst=(y,x), size))."""
    from PIL import Image
    a = np.asarray(pil512).copy()
    d = np.asarray(donor512)
    H, W = a.shape[:2]
    assert d.shape == a.shape and size <= min(H, W)
    sy, sx = int(rng.integers(0, H - size + 1)), int(rng.integers(0, W - size + 1))
    ty, tx = int(rng.integers(0, H - size + 1)), int(rng.integers(0, W - size + 1))
    a[ty:ty + size, tx:tx + size] = d[sy:sy + size, sx:sx + size]
    return Image.fromarray(a), dict(src=(sy, sx), dst=(ty, tx), size=int(size))


def apply_pixel(name: str, severity, pil512, rng: np.random.Generator, donor512=None):
    """Dispatch for the three realistic corruptions. Returns the corrupted PIL image."""
    if name == "jpeg":
        return jpeg(pil512, int(severity))
    if name == "noise":
        return gaussian_noise(pil512, float(severity), rng)
    if name == "splice":
        if donor512 is None:
            raise ValueError("splice needs a donor image")
        return splice(pil512, donor512, int(severity), rng)[0]
    raise ValueError(name)


TOKEN_RNG_TAG = {"patch": 190, "swap": 191}
"""Third entry of the per-item rng of the token-level sanity corruptions: `np.random.default_rng([config.SEED_GATE, gid, TOKEN_RNG_TAG[name]])`. 190 is the tag M4 has always used for patch
(unchanged, so the patch codes of a run made before swap existed are reproduced exactly); 191 is new for swap and collides with no other stream (M3 uses 100 to 125 and 150, M5 300, the pipeline 99)."""


def token_rng(seed: int, gid: int, name: str) -> np.random.Generator:
    return np.random.default_rng([seed, gid, TOKEN_RNG_TAG[name]])


def apply_token(name: str, clean: np.ndarray, rng: np.random.Generator, *, grid: int, patch: int, swap_frac: float, vocab: int) -> np.ndarray:
    if name == "patch":
        return core.patch_occlusion(clean, grid, patch, vocab, rng)
    if name == "swap":
        return core.token_swap(clean, swap_frac, vocab, rng)
    raise ValueError(name)


def denoise(pil512, params: dict | None = None):
    """Classical non-learned denoiser, one fixed setting for all corruptions (v2 4.3): OpenCV fastNlMeansDenoisingColored with `config.DENOISE_PARAMS` (h = hColor = 25.5 = sigma in grey levels
    of the preregistered noise, by the documented NLM rule of thumb; windows 7 and 21 are OpenCV defaults). The library default (h = 3) is NOT used: it removes a fraction of a percent of the
    noise power at this level (denoise_check.py). Applied before tokenisation. params=None uses the fixed setting."""
    import cv2
    from PIL import Image
    from exp_p2.gate import config
    p = dict(config.DENOISE_PARAMS if params is None else params)
    a = np.asarray(pil512.convert("RGB"))
    out = cv2.fastNlMeansDenoisingColored(cv2.cvtColor(a, cv2.COLOR_RGB2BGR), None, p["h"], p["hColor"], p["templateWindowSize"], p["searchWindowSize"])
    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))


def corruption_key(name: str, severity=None) -> str:
    """Stable condition name used in rows and arrays, e.g. 'jpeg10', 'noise0.1', 'splice128', 'patch'."""
    if severity is None:
        return name
    return f"{name}{severity:g}" if isinstance(severity, float) else f"{name}{severity}"
