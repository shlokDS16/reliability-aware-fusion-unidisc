"""Estimator tests: G0 (toy tables of analysis/framework/check_crossmodal_mixture.py), stratified identity and accuracy,
probe pass counts, wrappers (G2 blind, G3 injection, G3b non-semantic injection), floors, I->T chunk machinery, source rule."""
import numpy as np
import pytest
import torch

from exp001 import estimator as E
from exp001 import frozen, plan as P, rng
from exp001.network import ToyNet, to_prob
from exp001.sampler import run_sample, draw_from_class

D = torch.float64


def kl_np(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    m = p > 0
    return float(np.sum(p[m] * (np.log(p[m]) - np.log(q[m]))))


# ---------------------------------------------------------------------------------------------------------------- G0
def test_g0_naive_identity_to_1e12():
    g = np.random.default_rng(0)
    worst = 0.0
    for _ in range(500):
        na, nb = int(g.integers(2, 6)), int(g.integers(2, 6))
        pa = g.dirichlet(np.ones(na))
        pb_a = g.dirichlet(np.ones(nb), size=na)
        p1 = g.dirichlet(np.ones(nb))
        R = int(g.integers(2, 20))
        idx = g.choice(na, size=R, p=pa)
        M = torch.as_tensor(pb_a[idx], dtype=D).unsqueeze(1)
        out = E.mixture_estimate(M, torch.as_tensor(p1, dtype=D).unsqueeze(0))
        worst = max(worst, abs(float(out["naive"][0] - out["I_hat"][0] - out["I_inc"][0])))
        # exact population identity by enumeration (the check script's identity A)
        mbar = pa @ pb_a
        naive = sum(pa[i] * kl_np(pb_a[i], p1) for i in range(na))
        mi = sum(pa[i] * kl_np(pb_a[i], mbar) for i in range(na))
        assert abs(naive - (mi + kl_np(mbar, p1))) < 1e-12
    assert worst < 1e-12


def test_g0_block_j_naive_0_08109_mixture_0():
    pb = torch.tensor([0.6, 0.2, 0.2], dtype=D)
    M = pb.expand(8, 1, 3).clone()
    p1 = torch.tensor([[0.4, 0.3, 0.3]], dtype=D)
    out = E.mixture_estimate(M, p1)
    assert abs(float(out["I_hat"][0])) < 1e-12
    assert abs(float(out["naive"][0]) - 0.08109) < 1e-4 and abs(float(out["I_inc"][0]) - 0.08109) < 1e-4


def test_g0_finite_r_below_i_theta_40_of_40():
    g = np.random.default_rng(1)
    below = 0
    for _ in range(40):
        na, nb = int(g.integers(2, 6)), int(g.integers(2, 6))
        pa = g.dirichlet(np.ones(na))
        pb_a = g.dirichlet(np.ones(nb) * 0.7, size=na)
        mbar = pa @ pb_a
        mi = sum(pa[i] * kl_np(pb_a[i], mbar) for i in range(na))
        ok = True
        for R in (4, 16, 64):
            vals = []
            for _ in range(400):
                idx = g.choice(na, size=R, p=pa)
                vals.append(float(E.mixture_estimate(torch.as_tensor(pb_a[idx], dtype=D).unsqueeze(1))["I_hat"][0]))
            se = np.std(vals) / np.sqrt(len(vals))
            ok &= np.mean(vals) <= mi + 3 * se + 1e-9
        below += ok
    assert below == 40


def test_g0_stratified_identity_1e12():
    g = torch.Generator().manual_seed(3)
    worst = 0.0
    for _ in range(100):
        R, J, V = 8, 5, 9
        M = torch.softmax(torch.randn(R, J, V, generator=g, dtype=D), -1)
        pad = torch.tensor([True] * 4 + [False] * 4)[torch.randperm(R, generator=g)]
        w = float(torch.rand(1, generator=g, dtype=D))
        p1 = torch.softmax(torch.randn(J, V, generator=g, dtype=D), -1)
        o = E.stratified_estimate(M, pad, w, p1)
        worst = max(worst, float((o["total"] - o["between"] - o["within_pad"] - o["within_content"]).abs().max()))
        # naive identity against a direct class-weighted computation
        direct = w * E.kl(M[pad], p1.unsqueeze(0)).mean(0) + (1 - w) * E.kl(M[~pad], p1.unsqueeze(0)).mean(0)
        assert float((direct - o["naive"]).abs().max()) < 1e-12
    assert worst < 1e-12


def _toy_known_class():
    """Text variable a in {0, 2} (pad class P) and {5, 7} (content); image variable with 4 values, strong dependence."""
    ids = [0, 2, 5, 7]
    pa = np.array([0.15, 0.15, 0.4, 0.3])
    pb = np.array([[0.70, 0.10, 0.10, 0.10], [0.55, 0.25, 0.10, 0.10], [0.05, 0.10, 0.75, 0.10], [0.05, 0.10, 0.15, 0.70]])
    mbar = pa @ pb
    exact = sum(pa[i] * kl_np(pb[i], mbar) for i in range(4))
    return ids, pa, pb, exact


def test_g0_known_class_structure_stratified_and_unstratified_within_1pct_and_below_at_r8():
    ids, pa, pb, exact = _toy_known_class()
    g = np.random.default_rng(7)
    w = pa[:2].sum()
    pP, pC = pa[:2] / pa[:2].sum(), pa[2:] / pa[2:].sum()

    def strat(nper):
        iP, iC = g.choice(2, size=nper, p=pP), 2 + g.choice(2, size=nper, p=pC)
        M = torch.as_tensor(pb[np.concatenate([iP, iC])], dtype=D).unsqueeze(1)
        pad = torch.tensor([True] * nper + [False] * nper)
        return float(E.stratified_estimate(M, pad, w)["total"][0])

    def unstrat(R):
        return float(E.mixture_estimate(torch.as_tensor(pb[g.choice(4, size=R, p=pa)], dtype=D).unsqueeze(1))["I_hat"][0])

    s256 = np.mean([strat(128) for _ in range(60)])
    u256 = np.mean([unstrat(256) for _ in range(60)])
    assert abs(s256 - exact) / exact < 0.01, (s256, exact)
    assert abs(u256 - exact) / exact < 0.01, (u256, exact)
    s8 = np.mean([strat(4) for _ in range(2000)])
    u8 = np.mean([unstrat(8) for _ in range(2000)])
    assert s8 < exact and u8 < exact


def test_class_mass_below_threshold_zeroes_that_class():
    M = torch.softmax(torch.randn(8, 3, 6, generator=torch.Generator().manual_seed(2), dtype=D), -1)
    pad = torch.zeros(8, dtype=torch.bool)
    o = E.stratified_estimate(M, pad, w=1e-9)
    assert not o["avail_pad"] and float(o["within_pad"].abs().max()) == 0.0
    assert float((o["total"] - o["within_content"]).abs().max()) < 1e-15
    assert float(o["total"].max()) <= np.log(8) + 1e-12            # plug-in bound ln R


def test_plug_in_bound_ln_r():
    M = torch.softmax(torch.randn(8, 50, 30, generator=torch.Generator().manual_seed(4), dtype=D) * 20, -1)
    assert float(E.mixture_estimate(M)["I_hat"].max()) <= np.log(8) + 1e-9


# ------------------------------------------------------------------------------------------- probes on a toy network
def toy(**kw):
    return ToyNet(seed=kw.pop("seed", 2), L_T=16, L_I=64, V_T=12, V_I=20, pad_boost=kw.pop("pad_boost", 6.0), **kw)


def probe_hook_factory(net, store, which, passes_to_probe, **kw):
    def hook(q, tail, img, ctx):
        if q not in passes_to_probe:
            return
        rg = rng.probe_generator("D0", 0, q, 0)
        if "t2i" in which:
            src = frozen.load("ha_source").select_source(ctx["masked_text_idx"], ctx["conf_text"], ctx["pad_mass_text"], 16)
            store.setdefault(("t2i", q), E.probe_t2i(net, tail, img, ctx, [src[0]] if src else [int(ctx["sets"][0][0])], rg, R=8))
        if "i2t" in which:
            store[("i2t", q)] = E.probe_i2t(net, tail, img, ctx, ctx["sets"][1], rng.probe_generator("D0", 0, q, 1), R=8, g=kw.get("g", 4))
        store[("ctx", q)] = ctx
    return hook


def test_probe_pass_counts_and_classes():
    net = toy()
    plan = P.plan_J(16, 64, L_T_=16)
    store = {}
    before = None

    def hook(q, tail, img, ctx):
        nonlocal before
        if q == 2:
            n0 = net.n_forward
            r = E.probe_t2i(net, tail, img, ctx, [int(ctx["sets"][0][0])], rng.probe_generator("D0", 0, q, 0), R=8)
            assert net.n_forward - n0 == 8 == r.passes
            pm = float(ctx["pad_mass_text"][list(ctx["masked_text_idx"]).index(int(ctx["sets"][0][0]))])
            ok_p = [t in net.pad_ids for t in r.tokens]
            if 1e-6 <= pm <= 1 - 1e-6:
                assert sum(ok_p) == 4 and ok_p[:4] == [True] * 4
            n0 = net.n_forward
            r2 = E.probe_i2t(net, tail, img, ctx, ctx["sets"][1], rng.probe_generator("D0", 0, q, 1), R=8, g=4)
            assert net.n_forward - n0 == 32 == r2.passes
            n0 = net.n_forward
            r3 = E.probe_t2i(net, tail, img, ctx, [int(x) for x in ctx["masked_text_idx"][:2]], rng.probe_generator("D0", 0, q, 2), R=8)
            assert net.n_forward - n0 == 16 == r3.passes             # k+: 2 sequential sources, 2 passes per draw
            store["done"] = True

    run_sample(net, plan, rng.sampler_uniforms("D0", 0, 80), hook=hook)
    assert store["done"]


def test_stratified_probe_matches_direct_recomputation():
    net = toy(pad_boost=3.0)
    plan = P.plan_J(16, 64, L_T_=16)
    seen = {}

    def hook(q, tail, img, ctx):
        if q != 3:
            return
        src = int(ctx["sets"][0][0])
        r = E.probe_t2i(net, tail, img, ctx, [src], rng.probe_generator("D0", 0, q, 0), R=8)
        mi = torch.as_tensor(ctx["masked_img_idx"])
        Ms = []
        for tok in r.tokens:
            tr = tail.clone(); tr[src] = tok
            Ms.append(to_prob(net.forward(tr, img)[1], mi))
        M = torch.stack(Ms)
        pad = torch.tensor([t in net.pad_ids for t in r.tokens])
        d = E.stratified_estimate(M, pad, r.w, ctx["p_img"])
        seen["diff"] = float(np.abs(d["total"].numpy() - r.arrays["total"]).max())
        seen["ident"] = float(np.abs(r.arrays["naive"] - r.arrays["I_inc"] - r.arrays["total"]).max())
        seen["sum"] = float(np.abs(r.arrays["total"] - r.arrays["between"] - r.arrays["within_pad"] - r.arrays["within_content"]).max())
        seen["pos"] = float(r.arrays["total"].mean())

    run_sample(net, plan, rng.sampler_uniforms("D0", 0, 80), hook=hook)
    assert seen["diff"] < 1e-12 and seen["ident"] < 1e-12 and seen["sum"] < 1e-12
    assert seen["pos"] > 0                                    # the toy is coupled, so the dependence is detected


def _first_probe(net, builder, q=3, plan=None):
    out = {}

    def hook(qq, tail, img, ctx):
        if qq == q:
            out["r"] = builder(tail, img, ctx)

    run_sample(net, plan or P.plan_J(16, 64, L_T_=16), rng.sampler_uniforms("D0", 0, 80), hook=hook)
    return out["r"]


def test_g2_blind_wrapper_gives_zero_in_both_directions():
    base = toy(c_ti=2.0, c_it=2.0)
    blind = E.BlindNet(base)

    def b(tail, img, ctx):
        s = int(ctx["sets"][0][0])
        t2i = E.probe_t2i(blind, tail, img, ctx, [s], rng.probe_generator("D0", 0, 3, 0), R=8)
        i2t = E.probe_i2t(blind, tail, img, ctx, ctx["sets"][1], rng.probe_generator("D0", 0, 3, 1), R=8, g=4)
        return t2i, i2t

    t2i, i2t = _first_probe(blind, b)
    assert np.abs(t2i.arrays["total"]).max() < 1e-12 and np.abs(t2i.arrays["I_inc"]).max() < 1e-12
    assert np.abs(i2t.arrays["total"]).max() < 1e-12 and np.abs(i2t.arrays["I_inc"]).max() < 1e-12
    # and the unwrapped, coupled network is far above that
    def b2(tail, img, ctx):
        return E.probe_t2i(base, tail, img, ctx, [int(ctx["sets"][0][0])], rng.probe_generator("D0", 0, 3, 0), R=8)
    assert _first_probe(base, b2).arrays["total"].mean() > 1e-3


def test_g3_injection_mixture_zero_naive_equals_inc():
    base = toy(c_ti=2.0)
    inj = E.InjectionNet(base, "any")

    def b(tail, img, ctx):
        inj.set_reference(tail)
        return E.probe_t2i(inj, tail, img, ctx, [int(ctx["sets"][0][0])], rng.probe_generator("D0", 0, 3, 0), R=8)

    r = _first_probe(inj, b)
    a = r.arrays
    assert np.abs(a["total"]).max() < 1e-10                           # mixture estimator: true dependence is zero
    assert np.abs(a["naive"] - a["I_inc"]).max() < 1e-6                # naive equals I_inc
    assert a["naive"].mean() > 1e-3                                    # and is large (the false dependence)


def test_g3b_non_semantic_injection_routed_to_between_class():
    base = toy(c_ti=2.0, pad_boost=1.0)
    inj = E.InjectionNet(base, "pad")
    res = {}

    def b(tail, img, ctx):
        inj.set_reference(tail)
        # choose a source with both classes present
        pm = np.asarray(ctx["pad_mass_text"])
        k = int(np.argmin(np.abs(pm - 0.3)))
        res["pm"] = pm[k]
        return E.probe_t2i(inj, tail, img, ctx, [int(ctx["masked_text_idx"][k])], rng.probe_generator("D0", 0, 3, 0), R=8)

    r = _first_probe(inj, b)
    a = r.arrays
    assert 1e-6 < r.w < 1 - 1e-6
    assert a["between"].sum() >= 0.9 * a["total"].sum() and a["total"].mean() > 1e-3
    assert np.abs(a["within_content"]).max() < 1e-10


def test_noinfo_floor_machinery():
    base = toy(c_ti=0.0, c_it=0.0, pad_boost=60.0)
    floors = {}

    def b(tail, img, ctx):
        floors["t2i"] = E.noinfo_floor(base, tail, img, ctx, "t2i")
        floors["i2t"] = E.noinfo_floor(base, tail, img, ctx, "i2t")
        return None

    _first_probe(base, b, q=1)
    f = floors["t2i"]
    assert f is not None and f["n_reveals"] >= 6 and f["threshold"] == 0.999
    assert np.abs(f["floor"]).max() < 1e-12                            # decoupled toy: no-information reveal gives zero
    assert floors["i2t"] is None                                       # no near-deterministic image positions: "floor unmeasured"


def test_i2t_chunk_granularity_close_to_exact_and_reverse_order():
    net = toy(c_it=1.0)
    out = {}

    def b(tail, img, ctx):
        big = [int(j) for j in ctx["masked_img_idx"][:32]]
        for g in (4, 8, 32):
            out[g] = E.probe_i2t(net, tail, img, ctx, big, rng.probe_generator("D0", 0, 3, 1), R=8, g=g)
        out["rev"] = E.probe_i2t(net, tail, img, ctx, big, rng.probe_generator("D0", 0, 3, 1), R=8, g=4, order="reverse")
        return None

    _first_probe(net, b)
    assert out[4].passes == 32 and out[8].passes == 64 and out[32].passes == 256
    assert out["rev"].img_set == out[4].img_set[::-1]
    assert out[4].arrays["total"].mean() > 0 and out[32].arrays["total"].mean() > 0


def test_source_rule():
    hs = frozen.load("ha_source")
    # positions 0..5 masked; position 1 is the most confident but state-pad; position 3 is beyond L_c = 3
    sel = hs.select_source([0, 1, 2, 3, 4, 5], [0.4, 0.99, 0.6, 0.95, 0.5, 0.3], [0.1, 0.9, 0.2, 0.0, 0.0, 0.0], L_c=3)
    assert sel[0] == 2 and sel[1] == 0.2
    assert hs.select_source([1], [0.99], [0.9], 8) is None                 # only a state-pad candidate: no source
    sel = hs.select_source([4, 2, 6], [0.5, 0.5, 0.5], [0.0, 0.0, 0.0], 8)  # tie: lowest index
    assert sel[0] == 2
    assert hs.compute_L_c([5] * 10) == 8 and hs.compute_L_c([20] * 10) == 16 and hs.compute_L_c(list(range(1, 11))) == 10
    assert hs.state_pad_flags([0.49, 0.5, 0.9]) == [False, True, True]


# ------------------------------------------------------------------------------------------ probe schedules and cost (8.3, 8.4)
def test_probe_schedule_cost_formulas_match_card_8_4():
    from exp001 import probe_run as PR
    # D1 k0: 32 + 8 x 8 + 4 x 8 = 128 (+ 4 x 32 = 128 on the first 64 trajectories)
    assert 32 + PR.expected_extra_passes(PR.schedule("D1", 100)) == 128
    assert 32 + PR.expected_extra_passes(PR.schedule("D1", 10)) == 256
    # D2 k0: 32 + 4 x 40 = 192 (+ 40 for the pass-1 probe on the first 128)
    assert 32 + PR.expected_extra_passes(PR.schedule("D2", 200)) == 192
    assert 32 + PR.expected_extra_passes(PR.schedule("D2", 5)) == 232
    assert sorted(PR.schedule("D2", 200)) == [2, 6, 26, 30]
    assert sorted(PR.schedule("R", 10, n_traj=64)) == [1, 2, 6, 26, 30] and sorted(PR.schedule("R", 40, n_traj=64)) == [2, 6, 26, 30]


def test_run_with_probes_counts_isolation_and_no_source_weight():
    from exp001 import probe_run as PR
    net = ToyNet(seed=5, L_T=32, L_I=128, V_T=12, V_I=20, pad_boost=6.0)
    plan = P.plan_J(32, 128, L_T_=32)
    sch = PR.schedule("D1", 10)
    n0 = net.n_forward
    res, rows = PR.run_with_probes(net, plan, "D1", 10, sch, L_c=16)
    extra = net.n_forward - n0 - res.n_forward
    kinds = [r["kind"] for r in rows]
    assert kinds.count("price_t2i") == 8 and kinds.count("i2t") == 4
    assert extra == sum(r["passes"] for r in rows) == PR.expected_extra_passes(sch) - 8 * sum(1 for r in rows if r.get("no_source"))
    base = run_sample(net, plan, rng.sampler_uniforms("D1", 10, 160))
    assert torch.equal(base.tail, res.tail) and torch.equal(base.img, res.img)           # G6: probes on = probes off
    for r in rows:
        if r["kind"] == "price_t2i":
            assert r["price_total"] >= -1e-12 and np.isfinite(r["price_total"])
