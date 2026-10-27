"""Disk-backed cache of the null (D) log-probability matrices, keyed by caption length n (v1 section 3.3: D depends on the layout only).

Image null  D^I : [m, 16384] fp32 = 64 MiB per n, caption AND image fully masked.
Text null   D^T : [n, 32000] fp32 = n x 125 KiB per n, caption AND image fully masked.
At most 28 distinct n (captions of 5 to 32 tokens) -> at most 28 passes for each null in a whole campaign, and about 1.8 GB of disk for D^I.
Matrices are written atomically as .npy and read memory-mapped, so RAM use stays small (free RAM is about 8 GB with other sessions running).
`check_layout_only` is the L10 test (two different contents with the same n give equal nulls); it needs the real model once (4 passes).
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np

from exp_p2.gate import scores
from exp_p2.gate.evidence import gather_codes


class DCache:
    def __init__(self, root: Path | None):
        self.root = Path(root) if root is not None else None
        if self.root is not None:
            self.root.mkdir(parents=True, exist_ok=True)
        self._mem: dict[tuple[str, int], np.ndarray] = {}
        self.n_computed = 0                               # passes spent in this process (for the row's pass accounting)

    # ---- generic
    def _path(self, kind: str, n: int) -> Path | None:
        return None if self.root is None else self.root / f"{kind}_n{n:03d}.npy"

    def _load_or_compute(self, kind: str, n: int, compute) -> np.ndarray:
        key = (kind, n)
        if key in self._mem:
            return self._mem[key]
        p = self._path(kind, n)
        if p is not None and p.exists():
            try:
                arr = np.load(p, mmap_mode="r")
                self._mem = {k: v for k, v in self._mem.items() if k[0] != kind}          # keep one matrix per kind in memory
                self._mem[key] = arr
                return arr
            except (ValueError, OSError):                  # torn file after a crash: recompute
                pass
        arr = np.ascontiguousarray(compute().float().cpu().numpy())
        self.n_computed += 1
        if p is not None:
            tmp = p.with_name(p.name + ".tmp")
            with open(tmp, "wb") as fh:
                np.save(fh, arr)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, p)
            arr = np.load(p, mmap_mode="r")
        self._mem = {k: v for k, v in self._mem.items() if k[0] != kind}
        self._mem[key] = arr
        return arr

    # ---- image null
    def image_matrix(self, sc, st: dict, n: int) -> np.ndarray:
        return self._load_or_compute("DI", n, lambda: scores.full_image_lp(sc, st, caption_masked=True))

    def image_logp(self, sc, st: dict, n: int, codes) -> np.ndarray:
        """D_j at the observed codes (float32 [m]). `st` only supplies the layout of length n; its token values are masked anyway."""
        return gather_codes(self.image_matrix(sc, st, n), codes)

    # ---- text null
    def text_matrix(self, sc, st: dict, n: int) -> np.ndarray:
        return self._load_or_compute("DT", n, lambda: scores.full_text_lp(sc, st, image_all_masked=True))

    def text_logp(self, sc, st: dict, n: int, cap_tokens) -> np.ndarray:
        """D^T at the caption tokens (float32 [n]); cap_tokens are text ids (0..31999)."""
        return gather_codes(self.text_matrix(sc, st, n), np.asarray(cap_tokens))


def check_layout_only(sc, cap_tok_a: list[int], cap_tok_b: list[int], codes_a, codes_b, atol: float = 0.0) -> dict:
    """L10 on a real model: nulls for two different (caption, image) contents with the same caption length must be equal.
    cap_tok_a and cap_tok_b must have the same length. 4 passes (2 image nulls, 2 text nulls)."""
    assert len(cap_tok_a) == len(cap_tok_b)
    sa, sb = sc.build(cap_tok_a, codes_a), sc.build(cap_tok_b, codes_b)
    da = scores.full_image_lp(sc, sa, True)
    db = scores.full_image_lp(sc, sb, True)
    ta = scores.full_text_lp(sc, sa, image_all_masked=True)
    tb = scores.full_text_lp(sc, sb, image_all_masked=True)
    di = float((da - db).abs().max())
    dt = float((ta - tb).abs().max())
    return dict(max_abs_diff_image_null=di, max_abs_diff_text_null=dt, atol=atol, ok=bool(di <= atol and dt <= atol), n_passes=4)
