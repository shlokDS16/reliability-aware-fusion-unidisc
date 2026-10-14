import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))
from synth import make_arm, S, nounkey, ROOT      # noqa: E402


def test_nounkey():
    k = nounkey.key
    assert k("Dogs") == "dog" and k("dog") == "dog" and k("boxes") == "box" and k("glasses") == "glass" and k("glass") == "glass"
    assert k("giraffes") == "giraffe" and k("bus") == "bus" and k("buses") == "bus" and k("sandwiches") == "sandwich" and k("skis") == "ski"
    assert k("is") == "is" and k("gas") == "gas"


def test_discordant_and_Lp():
    D0, D1 = S.discordant(["dog", "cat", "table"], ["dogs", "chair"], nounkey.key)
    assert D0 == ["cat", "table"] and D1 == ["chair"]
    assert math.isnan(S.L_p([np.array([]), np.array([1.0])], [np.array([]), np.array([0.0])]))
    assert S.L_p([np.array([1, 1]), np.array([1.0])], [np.array([0, 1]), np.array([0.0])]) == pytest.approx(0.5 * (0.5 + 1.0))


@pytest.mark.parametrize("link", [0.0, 0.1, 0.3])
def test_injected_link_recovered(link):
    recs = make_arm(400, link=link, seed=11)[3]
    L = S.arm_L(recs)
    parts = S.lam_parts(L)
    d = S.point(parts)
    th, _ = S.bootstrap([parts], 2000, 1)
    lo, hi = S.percentile_ci(th[:, 0])
    assert lo <= link <= hi and abs(d - link) < 0.06


def test_seed_swap_invariance():
    recs = make_arm(60, link=0.2, seed=2)[3]
    sw = [dict(r, D=r["D"][::-1], own=r["own"][::-1], sib=r["sib"][::-1]) for r in recs]
    assert np.allclose(S.arm_L(recs), S.arm_L(sw))


def test_additive_image_bias_cancels_in_lambda_b_not_in_ratio():
    kw = dict(link=0.1, bias=(0.35, -0.05), seed=5, couple_count_to_bias=True)
    recs = make_arm(800, **kw)[3]
    lb = S.point(S.lam_parts(S.arm_L(recs)))
    ld = S.point(S.arm_ratio(recs))
    assert abs(lb - 0.1) < 0.04
    assert abs(ld - 0.1) > 0.05           # the v0.1 ratio does not cancel it when the discordant count tracks the bias
    # placebo nouns carry the bias but no link
    lp = S.point(S.lam_parts(S.arm_L(recs, "pown", "psib")))
    assert abs(lp) < 0.05


def test_bootstrap_same_indices_zero_denominator_redraw():
    num = np.array([0.5, 0.0, 0.0, 0.0, 0.0])
    den = np.array([1.0, 0.0, 0.0, 0.0, 0.0])          # a replicate without prefix 0 has a zero denominator -> redrawn
    th, red = S.bootstrap([(num, den), (num * 2, den)], 400, 3)
    assert red > 0 and np.all(np.isfinite(th)) and np.allclose(th[:, 1], 2 * th[:, 0])


def test_p_value_rule_and_rerun_flag():
    th = np.concatenate([np.full(95, 0.5), np.full(5, -0.1)])
    assert S.two_sided_p(th) == pytest.approx(2 * (1 + 5) / 101)
    assert S.two_sided_p(np.zeros(10)) == 1.0
    assert S.needs_rerun(0.0505, 0.05, 10000) and not S.needs_rerun(0.2, 0.05, 10000)


def test_holm_and_classes():
    h = S.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert h["a"] == pytest.approx(0.03) and h["c"] == pytest.approx(0.06) and h["b"] == pytest.approx(0.06)
    c = lambda d, p95, b95, p, p90, b90: S.outcome_class(d, p95, b95, p, p90, b90)
    assert c(0.15, (0.05, 0.25), (0.04, 0.26), 0.01, (0.06, .24), (.05, .25)) == "positive_at_or_above_MEI"
    assert c(0.06, (0.01, 0.11), (0.01, 0.12), 0.03, (0.02, .1), (.02, .1)) == "positive"
    assert c(0.06, (0.01, 0.11), (-0.01, 0.12), 0.03, (0.02, .1), (.02, .1)) == "inconclusive"     # BCa disagrees with the percentile interval
    assert c(-0.1, (-0.2, -0.01), (-0.2, -0.02), 0.02, (-.18, -.03), (-.18, -.03)) == "reversed"
    assert c(0.0, (-0.09, 0.08), (-0.09, 0.08), 0.9, (-0.07, 0.06), (-0.08, 0.07)) == "null"
    assert c(0.0, (-0.12, 0.1), (-0.12, 0.1), 0.9, (-0.11, 0.09), (-0.1, 0.09)) == "inconclusive"


def test_identity_on_common_set_and_bca():
    g = np.random.default_rng(0)
    L = {k: np.where(g.random(100) < 0.2, np.nan, g.normal(0.1, 0.3, 100)) for k in ("G", "P64", "O0", "P32")}
    idn = S.identity_four_arm(L["G"], L["P64"], L["O0"], L["P32"])
    assert abs(idn["residual"]) < 1e-12 and idn["n_common"] < 100
    parts = S.contrast_parts(L["G"], L["P64"])
    th, _ = S.bootstrap([parts], 3000, 4)
    lo, hi = S.bca_ci(th[:, 0], S.point(parts), S.jackknife(parts))
    plo, phi = S.percentile_ci(th[:, 0])
    assert abs(lo - plo) < 0.08 and abs(hi - phi) < 0.08


def test_sample_size_rule_and_nc():
    up, n = S.sample_size(0.45 / 1.21)
    assert up == pytest.approx(0.45) and n == 213
    assert S.nc_pass((-0.05, 0.08)) and not S.nc_pass((0.01, 0.1)) and not S.nc_pass((-0.2, 0.2))


def test_quality_matched_runs():
    recs = make_arm(120, link=0.2, seed=8)[3]
    r = S.quality_matched(S.arm_L(recs), [x["iqa"] for x in recs], B=300, seed=1)
    assert r["n_matched"] > 10 and "slope" in r
