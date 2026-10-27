"""PSNR and SSIM for the denoise check, in numpy/OpenCV (scikit-image is not installed in the project venv). SSIM follows Wang et al. 2004 with the Gaussian window of the reference
implementation (11 x 11, sigma 1.5, K1 = 0.01, K2 = 0.03, population covariance), computed per channel on the 8-bit range, borders of 5 pixels cropped, mean over pixels and channels;
tests compare it with scikit-image where that is installed."""
from __future__ import annotations

import cv2
import numpy as np


def psnr(a: np.ndarray, b: np.ndarray, data_range: float = 255.0) -> float:
    mse = float(np.mean((np.asarray(a, np.float64) - np.asarray(b, np.float64)) ** 2))
    return float("inf") if mse == 0 else float(10 * np.log10(data_range ** 2 / mse))


def ssim(a: np.ndarray, b: np.ndarray, data_range: float = 255.0) -> float:
    x, y = np.asarray(a, np.float64), np.asarray(b, np.float64)
    if x.ndim == 2:
        x, y = x[..., None], y[..., None]
    C1, C2 = (0.01 * data_range) ** 2, (0.03 * data_range) ** 2
    blur = lambda im: cv2.GaussianBlur(im, (11, 11), 1.5, borderType=cv2.BORDER_REFLECT)
    vals = []
    for c in range(x.shape[2]):
        xc, yc = np.ascontiguousarray(x[..., c]), np.ascontiguousarray(y[..., c])
        mx, my = blur(xc), blur(yc)
        vx, vy, cxy = blur(xc * xc) - mx * mx, blur(yc * yc) - my * my, blur(xc * yc) - mx * my
        s = ((2 * mx * my + C1) * (2 * cxy + C2)) / ((mx * mx + my * my + C1) * (vx + vy + C2))
        vals.append(s[5:-5, 5:-5].mean())
    return float(np.mean(vals))
