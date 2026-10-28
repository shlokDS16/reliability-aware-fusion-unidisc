"""E-pred FIT CODE tests (SAP AD.3 as demoted by AB.3, AD.13): the Prop. 4 sign function against its closed forms, the fit on planted worlds with a known sign, stability, input validation,
the reachability self-test (K = 4 never rejects), the module self-test and the seed fingerprint. This file is part of the hashed fit code (AB.3 item 5): it is committed with `epred_fit.py` and
`theory.py` before the fit chunk runs and is not edited afterwards. It imports nothing from the other test files. CPU only."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2.gate import epred_fit as E, seeds, theory                     # noqa: E402


def world(rng, helps: bool, n_items=30, m=128, rho=0.15):
    """Planted world: changed tokens carry pure noise (mean 0, sd 3), clean tokens a signal (mean 0.3, sd 0.5). helps: the gate flags 70 percent of changed and 3 percent of clean tokens;
    otherwise it flags 30 percent of clean tokens and none of the changed ones."""
    toks, fl = [], []
    for _ in range(n_items):
        z = rng.random(m) < rho
        d = np.where(z, rng.normal(0.0, 3.0, m), rng.normal(0.3, 0.5, m))
        f = (z & (rng.random(m) < (0.7 if helps else 0.0))) | (~z & (rng.random(m) < (0.03 if helps else 0.30)))
        toks.append(dict(delta=d, z=z)), fl.append(f)
    return toks, fl


# ------------------------------------------------------------------------------------------------ the sign function
def test_sign_matches_the_closed_form_inequality_when_mu_c_is_zero():
    rng = np.random.default_rng(0)
    n_checked = 0
    for _ in range(400):
        rho, a, b = rng.uniform(0.02, 0.6), rng.uniform(0.005, 0.3), rng.uniform(0.0, 1.0)
        mu, s2, s2c = rng.uniform(-0.2, 0.6), rng.uniform(0.05, 1.0), rng.uniform(0.05, 4.0)
        r = E.sign_of_gating(rho, a, b, mu, s2, 0.0, s2c)
        if mu <= 0 or r["sign"] == 0:
            continue                                                         # the closed form is for the SNR of a positive mean (mu > 0): the sign of the SNR change then equals the inequality
        closed = theory.special_case_inequality(rho, a, b, mu, s2, s2c)
        assert (r["sign"] == 1) == closed, (rho, a, b, mu, s2, s2c)
        n_checked += 1
    assert n_checked > 200


def test_sign_does_not_depend_on_the_number_of_tokens_m():
    rng = np.random.default_rng(1)
    for _ in range(100):
        args = (rng.uniform(0.02, 0.5), rng.uniform(0.0, 0.3), rng.uniform(0.0, 1.0), rng.normal(0.2, 0.2), rng.uniform(0.05, 1.0), rng.normal(0, 0.2), rng.uniform(0.05, 3.0))
        assert E.sign_of_gating(*args, m=1)["sign"] == E.sign_of_gating(*args, m=1024)["sign"] == E.sign_of_gating(*args, m=7)["sign"]


def test_edge_cases_tie_undefined_and_perfect_gate():
    assert E.sign_of_gating(0.2, 0.0, 0.0, 0.1, 0.3, 0.0, 0.4)["sign"] == 0                    # a gate that flags nothing: a tie, no sign
    assert E.sign_of_gating(0.2, 0.0, 1.0, 0.2, 0.3, 0.0, 2.0)["sign"] == 1                    # removes exactly the noisy corrupted class
    assert E.sign_of_gating(0.2, 0.0, 1.0, 0.2, 0.3, float("nan"), 2.0)["sign"] is None
    assert E.sign_of_gating(0.2, 1.0, 1.0, 0.2, 0.3, 0.0, 2.0)["sign"] is None                 # everything flagged: variance 0, undefined
    assert E.sign_of_gating(0.2, 0.3, 0.0, 0.3, 0.3, 0.0, 0.3)["sign"] == -1                   # flags only clean tokens that carry the signal


def test_vectorised_bootstrap_sign_equals_scalar_sign():
    rng = np.random.default_rng(2)
    n = 300
    v = [rng.uniform(0.05, 0.4, n), rng.uniform(0, 0.3, n), rng.uniform(0.0, 1.0, n), rng.normal(0.2, 0.15, n), rng.uniform(0.1, 0.8, n), rng.normal(0, 0.2, n), rng.uniform(0.1, 2.0, n)]
    vec = E._sign_vec(*v, valid=np.ones(n, bool))
    sca = np.array([E.sign_of_gating(*(float(x[i]) for x in v))["sign"] for i in range(n)])
    assert np.array_equal(vec, sca)
    assert np.all(E._sign_vec(*v, valid=np.zeros(n, bool)) == 2)


# ------------------------------------------------------------------------------------------------ the fit
def test_fit_inputs_equal_the_pooled_plug_in_and_the_item_stats_reproduce_them():
    rng = np.random.default_rng(3)
    toks, fl = world(rng, True, n_items=25)
    fit = E.epred_fit({"P1": toks}, {"P1": fl}, n_boot=200, seed=np.random.SeedSequence(1))
    d, z, f = np.concatenate([t["delta"] for t in toks]), np.concatenate([t["z"] for t in toks]), np.concatenate(fl)
    pi = theory.plug_in_from_deltas(d, z, f)
    c = fit["cells"]["P1"]
    for k in ("rho", "mu", "sigma2", "mu_c", "sigma2_c", "alpha_obs", "beta_obs"):
        assert c["inputs"][k] == pytest.approx(pi[k], rel=1e-12)
    assert c["n_tokens"] == d.size and c["n_tokens_changed"] == int(z.sum()) and c["n_tokens_flagged"] == int(f.sum())
    # the sufficient statistics used by the bootstrap give the same pooled inputs
    c0 = float(d.mean())
    tot = np.stack([E._item_stats(t["delta"], t["z"], g, c0) for t, g in zip(toks, fl)]).sum(axis=0)
    N0, N1, S0, S1, Q0, Q1, F0, F1 = tot
    assert c0 + S0 / N0 == pytest.approx(pi["mu"], rel=1e-12) and c0 + S1 / N1 == pytest.approx(pi["mu_c"], rel=1e-12)
    assert (Q0 - S0 ** 2 / N0) / (N0 - 1) == pytest.approx(pi["sigma2"], rel=1e-9) and (Q1 - S1 ** 2 / N1) / (N1 - 1) == pytest.approx(pi["sigma2_c"], rel=1e-9)
    assert F0 / N0 == pytest.approx(pi["alpha_obs"]) and F1 / N1 == pytest.approx(pi["beta_obs"]) and N1 / (N0 + N1) == pytest.approx(pi["rho"])


def test_planted_worlds_recover_the_known_sign_with_high_stability():
    rng = np.random.default_rng(4)
    th, fh = world(rng, True)
    tl, fl = world(rng, False)
    fit = E.epred_fit({"P1": th, "PS1": tl}, {"P1": fh, "PS1": fl}, n_boot=500)
    assert fit["cells"]["P1"]["sign"] == 1 and fit["cells"]["P1"]["sign_text"] == "+"
    assert fit["cells"]["PS1"]["sign"] == -1 and fit["cells"]["PS1"]["sign_text"] == "-"
    assert fit["cells"]["P1"]["snr_after"] > fit["cells"]["P1"]["snr_before"] and fit["cells"]["PS1"]["snr_after"] < fit["cells"]["PS1"]["snr_before"]
    for c in ("P1", "PS1"):
        st = fit["cells"][c]["stability"]
        assert st["share_same_sign"] > 0.95 and st["n_boot"] == 500 and st["unit"] == "headroom items"
    assert fit["s_c"] == {"P1": 1, "PS1": -1}
    assert set(fit["absent"]) == {"P2", "P3", "PS2"} and all(isinstance(v, str) for v in fit["absent"].values())      # absent cells are counted with a reason


def test_stability_never_changes_the_committed_sign_and_is_seed_deterministic():
    rng = np.random.default_rng(5)
    # a nearly balanced world: the point sign is whatever it is, the share is near 0.5 and the sign is not re-decided by the bootstrap
    toks, fl = world(rng, True, n_items=12, m=64, rho=0.04)
    a = E.epred_fit({"P1": toks}, {"P1": fl}, n_boot=400)
    b = E.epred_fit({"P1": toks}, {"P1": fl}, n_boot=400)
    c = E.epred_fit({"P1": toks}, {"P1": fl}, n_boot=900)
    assert a == b                                                         # default seed = seeds.seed_for("prop4_plugin"): fixed
    assert a["cells"]["P1"]["sign"] == c["cells"]["P1"]["sign"]            # the number of resamples cannot move s_c
    assert a["seed"] == dict(name="prop4_plugin", position=seeds.ANALYSES.index("prop4_plugin"))
    d = E.epred_fit({"P1": toks}, {"P1": fl}, n_boot=400, seed=np.random.SeedSequence(99))
    assert d["cells"]["P1"]["sign"] == a["cells"]["P1"]["sign"]


def test_cells_without_two_changed_tokens_get_no_sign_and_the_reason():
    rng = np.random.default_rng(6)
    toks = [dict(delta=rng.normal(0.3, 0.5, 50), z=np.zeros(50, bool)) for _ in range(5)]
    fl = [rng.random(50) < 0.05 for _ in range(5)]
    fit = E.epred_fit({"P2": toks}, {"P2": fl}, n_boot=100)
    c = fit["cells"]["P2"]
    assert c["sign"] is None and c["sign_text"] == "none (undefined)" and "not finite" in c["reason_no_sign"] and c["stability"]["share_same_sign"] is None
    none = [np.zeros(50, bool) for _ in range(5)]
    toks2, _ = world(rng, True, n_items=5, m=50)
    tie = E.epred_fit({"P2": toks2}, {"P2": none}, n_boot=100)["cells"]["P2"]
    assert tie["sign"] == 0 and tie["sign_text"] == "none (tie)"


def test_fit_input_validation():
    rng = np.random.default_rng(7)
    toks, fl = world(rng, True, n_items=4)
    with pytest.raises(ValueError):
        E.epred_fit({"P1": toks}, {"P1": fl[:3]})                                        # item counts differ
    with pytest.raises(ValueError):
        E.epred_fit({"P1": toks}, {"P2": fl})                                            # cell names differ
    with pytest.raises(ValueError):
        E.epred_fit({"Q1": toks}, {"Q1": fl})                                            # unknown cell
    bad = [dict(delta=np.full(128, np.nan), z=np.zeros(128, bool))]
    with pytest.raises(ValueError):
        E.epred_fit({"P1": bad}, {"P1": [np.zeros(128, bool)]})


# ------------------------------------------------------------------------------------------------ reachability and the self-test (AD.13)
def test_reachability_K5_can_reject_K4_never_can():
    assert E.reachability(5)["min_attainable_p"] == pytest.approx(0.03125) and E.reachability(5)["could_reject_at_alpha"]
    assert E.reachability(4)["min_attainable_p"] == pytest.approx(0.0625) and not E.reachability(4)["could_reject_at_alpha"]
    for k in range(0, 5):
        assert not E.reachability(k)["could_reject_at_alpha"]
    # the exact one-sided binomial p of A = K agreements: 0.5 ** K
    for k in range(1, 6):
        p = sum(math.comb(k, i) for i in range(k, k + 1)) / 2 ** k
        assert p == pytest.approx(E.reachability(k)["min_attainable_p"])


def test_module_selftest_passes():
    st = E.selftest()
    assert st["all_ok"], st


def test_seed_fingerprint_survives_appending_names_but_not_reordering():
    fp = E.seed_fingerprint()
    assert fp["name"] == "prop4_plugin" and fp["position"] == seeds.ANALYSES.index("prop4_plugin") == 19 and fp["analyses_prefix"][-1] == "prop4_plugin" and len(fp["child_state"]) == 4
    ref = np.random.SeedSequence(seeds.ROOT_SEED).spawn(20)[19]
    assert fp["child_state"] == [int(x) for x in ref.generate_state(4)]
    assert fp["analyses_prefix"] == list(seeds.ANALYSES[:20])               # names after position 19 (ps_family, s2_family, ... and later appends) are not part of the fingerprint
