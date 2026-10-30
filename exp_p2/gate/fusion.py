"""Two-way evidence fusion, secondary (v2 section 8; v1 section 7). Inputs are the paired margins of the two directions for each calibration pair:
    Delta_T = pmi(c+) - pmi(c-) (text direction), Delta_I = mean per-token paired image evidence (image direction).
Order of reporting: each direction alone; unfitted Stouffer; Fisher LDA with weights fitted on calibration pairs of the SAME negative type as the test contrast.
Wording in the paper: 'no network finetuning; two fusion weights fitted on clean labelled pairs'."""
from __future__ import annotations

import numpy as np


def stouffer_weights(cal: np.ndarray) -> dict:
    """cal [n, 2] paired margins (T, I) on calibration items. Standardise each direction by its SD over calibration items; combined statistic
    (z_T + z_I) / sqrt(2 + 2 r) with the calibration correlation r. Returns the linear weights on the raw margins and the scale."""
    cal = np.asarray(cal, float)
    sd = cal.std(axis=0, ddof=1)
    r = float(np.corrcoef(cal[:, 0], cal[:, 1])[0, 1])
    w = 1.0 / (sd * np.sqrt(2 + 2 * r))
    return dict(w=w, r=r, sd=sd)


def lda_weights(cal: np.ndarray) -> np.ndarray:
    """Fisher LDA on paired differences: w = Sigma^{-1} mu (v1 section 7). Two parameters up to scale; uses the correlation between the directions."""
    cal = np.asarray(cal, float)
    mu = cal.mean(axis=0)
    S = np.cov(cal, rowvar=False)
    return np.linalg.solve(S + 1e-12 * np.eye(2), mu)


def fused_accuracy(test: np.ndarray, w: np.ndarray) -> float:
    return float(np.mean(np.asarray(test, float) @ np.asarray(w, float) > 0))
