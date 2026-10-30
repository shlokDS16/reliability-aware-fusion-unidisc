"""Constants of the GATE experiments. Every value is a design choice fixed by the spec (section noted); none is tuned on data."""
from __future__ import annotations

SEED_GATE = 20261029          # new seed for the gate experiments (design choice); probe 2 keeps its own SEED = 20261028
K = 8                         # complementary masks for the gate statistic (v2 4.1)
ALPHA_PRIMARY = 0.05          # v2 4.1
ALPHAS = (0.05, 0.01, 0.10)   # primary first; 0.01 and 0.10 are sensitivity, not selected (v2 4.1, 6)
N_CAL, N_HEAD, N_TEST = 300, 100, 300          # v2 6, 7.5
TOK_RANGE = (5, 32)
GRID = 32                     # 32x32 token map at 512 px
PATCH = 8                     # sanity corruption: 8x8 token block (as probe 2)
SWAP_FRAC = 0.15
LADDERS = {"jpeg": (10, 5), "noise": (0.10, 0.20), "splice": (128, 192)}      # v2 7.3, walked in this order
REALISTIC = ("jpeg", "noise", "splice")
SANITY = ("patch",)
DENOISE_FOR = ("jpeg", "noise")   # v2 11.1 M4 counts 2 denoised encodes; one flag changes it (see implementation notes)
N_GEO_SEEDS = 3
FOLD_GID_OFFSET = {"cal": 0, "head": 1000, "test": 2000}   # global item id = offset + idx; used in every seed so folds never share masks
FOLDS_RUN_ID = "P2-GATE-FOLDS"
DCACHE_RUN_ID = "P2-GATE-DCACHE"      # shared disk cache of the layout-only null matrices (about 1.8 GB for all 28 caption lengths)
STAT_NAME = "q"               # u_j = -(B_j - D_j); v2 4.1
GLOBAL_HOLD = ("P2-PROBE-02", "HOLD.txt")      # v2 11 / v1 13: every GPU item is blocked by this file

# Pixel-domain denoise arm (spec v2 4.3, red team N6 / C5). The OpenCV library default (h = hColor = 3) barely acts on sigma = 0.10 x 255 = 25.5 grey-level noise (exp_p2/gate/denoise_check.py,
# runs/P2-GATE-CPU/denoise_check/). Fixed a priori from the scikit-image `denoise_nl_means` documentation, "for a Gaussian noise of standard deviation sigma, a rule of thumb is to choose the
# value of h to be sigma of slightly less": h = hColor = sigma in grey levels = 0.10 * 255 = 25.5; patch 7 and search window 21 are the OpenCV defaults. One setting for all corruptions.
DENOISE_NOISE_SIGMA = 0.10
DENOISE_PARAMS = dict(h=DENOISE_NOISE_SIGMA * 255, hColor=DENOISE_NOISE_SIGMA * 255, templateWindowSize=7, searchWindowSize=21)
