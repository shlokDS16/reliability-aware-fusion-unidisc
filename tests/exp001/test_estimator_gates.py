import numpy as np
import torch

from exp001 import estimator_gates as G


def test_pass_rules():
    assert G.g1_floor(2.0e-3, 1e-5)["pass"] and not G.g1_floor(1.5e-4, 1e-5)["pass"]
    assert G.g3_injection(1e-12, 0.05, 0.05, 1e-5)["pass"] and not G.g3_injection(1e-3, 0.05, 0.05, 1e-5)["pass"]
    assert G.g3b_nonsemantic(0.1, 0.099, 1e-8, 1e-5)["pass"] and not G.g3b_nonsemantic(0.1, 0.05, 1e-8, 1e-5)["pass"]
    assert G.g4_bias(2.0, 2.4)["pass"] and not G.g4_bias(2.0, 3.0)["pass"]
    assert G.g6_rate(0, 0, 16)["pass"] and not G.g6_rate(3, 1, 16)["pass"]
    assert G.nc4_padding(0.01, 0.05)["pass"] and not G.nc4_padding(0.2, 0.05)["pass"]
    assert G.pc_d_prime(1e-3, 1e-5, None, None, 14)["pass"] and not G.pc_d_prime(1e-3, 1e-5, None, None, 11)["pass"]
    assert G.pc_d_prime(1e-3, 1e-5, 1e-6, 1e-5, 16)["pass"] is False


def test_g5_decision():
    by = {4: dict(r_p2=0.95, r_p30=1.1, early_late=2.1), 8: dict(r_p2=1.0, r_p30=1.0, early_late=2.0), 32: dict(early_late=2.0)}
    assert G.g5_choose_g(by)["g"] == 4
    by[4]["r_p2"] = 0.6
    assert G.g5_choose_g(by)["g"] == 8
    by[8]["early_late"] = 3.0
    r = G.g5_choose_g(by)
    assert r["chunk_dependent"] and r["wording"] == "T->I only"
    assert G.g5_order(1.0, 1.4)["f_ord"] == 2 and G.g5_order(1.0, 1.1)["f_ord"] == 1


def test_nc3_permutation_centred():
    g = np.random.default_rng(0)
    types = [list(g.choice(["noun", "function", "other"], 12)) for _ in range(60)]
    Q = [list(g.random(12)) for _ in range(60)]
    assert G.nc3_permutation(types, Q, n_perm=200)["pass"]


def test_information_fraction_and_batch_invariance():
    I = np.array([0.1, 0.5, 0.02]); H = np.array([1.0, 0.8, 0.01])
    q, keep = G.information_fraction(I, H)
    assert keep.tolist() == [True, True, False] and np.isnan(q[2]) and q[0] == 0.1
    f = lambda s: s * 2.0
    fb = lambda ss: [s * 2.0 for s in ss]
    r = G.batch_invariance(f, fb, [torch.ones(3), torch.zeros(3)], tol=1e-12)
    assert r["pass"]
