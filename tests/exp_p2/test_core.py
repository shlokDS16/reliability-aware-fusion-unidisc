"""Unit tests of masking, corruption, AUROC and matching logic for the Paper 2 probes (numpy only)."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2 import core as C  # noqa: E402


def test_each_position_masked_exactly_once():
    rng = np.random.default_rng(1)
    for n, k in [(1024, 8), (13, 8), (5, 8), (64, 3)]:
        g = C.complementary_groups(n, k, rng)
        masks = C.masks_from_groups(g, k)
        cover = np.zeros(n, int)
        for m in masks:
            cover[m] += 1
        assert (cover == 1).all()
        sizes = [len(m) for m in masks]
        assert max(sizes) - min(sizes) <= 1
        assert len(masks) == min(n, k)          # groups beyond n are empty and skipped


def test_priority_groups_common_random_numbers():
    u = np.random.default_rng(3).random(30)
    g_a = C.groups_from_priority(u[:12], 8)
    g_b = C.groups_from_priority(u[:12], 8)
    assert (g_a == g_b).all()                    # same priorities -> identical masks
    g_c = C.groups_from_priority(u[:17], 8)      # a longer text: still a complete partition
    cover = np.zeros(17, int)
    for m in C.masks_from_groups(g_c, 8):
        cover[m] += 1
    assert (cover == 1).all()


def test_token_swap_fraction_and_range():
    rng = np.random.default_rng(0)
    codes = np.arange(1024) % 16384
    out = C.token_swap(codes, 0.15, 16384, rng)
    assert (out != codes).sum() <= round(0.15 * 1024)       # a random code may equal the old one (prob 1/16384)
    assert (out != codes).sum() >= round(0.15 * 1024) - 3
    assert out.min() >= 0 and out.max() < 16384
    # non-swapped positions untouched: at most round(0.15 n) changed positions
    assert len(np.nonzero(out != codes)[0]) <= 154


def test_patch_occlusion_is_a_block():
    rng = np.random.default_rng(5)
    codes = np.zeros(1024, dtype=np.int64)
    out = C.patch_occlusion(codes, 32, 8, 16384, rng)
    m = (out != codes).reshape(32, 32)
    assert m.sum() <= 64
    ys, xs = np.nonzero(m)
    # the changed tokens lie inside an 8x8 window (a random code can equal 0 with prob 1/16384, so use the bounding box)
    assert ys.max() - ys.min() < 8 and xs.max() - xs.min() < 8


def test_corrupted_mask_defined_by_code_difference():
    a = np.array([1, 2, 3, 4])
    b = np.array([1, 9, 3, 7])
    assert C.corrupted_mask(a, b).tolist() == [False, True, False, True]


def test_auroc_matches_bruteforce_with_ties():
    rng = np.random.default_rng(7)
    s = rng.integers(0, 6, size=200).astype(float)          # many ties
    y = rng.random(200) < 0.3
    pos, neg = s[y], s[~y]
    brute = np.mean([(p > q) + 0.5 * (p == q) for p in pos for q in neg])
    assert abs(C.auroc(s, y) - brute) < 1e-12


def test_auroc_extremes():
    y = np.array([0, 0, 0, 1, 1, 1], bool)
    assert C.auroc(np.array([0, 1, 2, 3, 4, 5.0]), y) == 1.0
    assert C.auroc(np.array([5, 4, 3, 2, 1, 0.0]), y) == 0.0
    assert C.auroc(np.ones(6), y) == 0.5
    assert np.isnan(C.auroc(np.arange(6.0), np.zeros(6, bool)))


def test_auroc_random_score_near_half():
    rng = np.random.default_rng(11)
    y = rng.random(20000) < 0.15
    assert abs(C.auroc(rng.random(20000), y) - 0.5) < 0.02


def test_match_indicator_ties_and_order():
    assert C.match_indicator([1, 2, 3], [0, 2, 4]).tolist() == [1.0, 0.5, 0.0]


def test_bootstrap_ci_contains_mean_and_is_ordered():
    x = np.random.default_rng(2).random(300)
    m, lo, hi = C.bootstrap_mean_ci(x, n_boot=2000, seed=1)
    assert lo < m < hi and hi - lo < 0.2
    assert C.bootstrap_mean_ci(x, n_boot=2000, seed=1) == (m, lo, hi)   # deterministic


def test_derangement_has_no_fixed_point():
    rng = np.random.default_rng(4)
    for n in (2, 3, 10, 300):
        p = C.derangement(n, rng)
        assert sorted(p.tolist()) == list(range(n)) and not np.any(p == np.arange(n))
