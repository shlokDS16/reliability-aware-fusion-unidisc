"""Sampler semantics: commit sets, confidence rule and ties, CRN, determinism and resume, probe isolation, P_rand, pooled rule,
value draws (float64 inverse CDF at temperature 1)."""
import numpy as np
import pytest
import torch

from exp001 import plan as P
from exp001 import rng
from exp001.network import ToyNet, to_prob
from exp001.sampler import run_sample, inverse_cdf, rank_positions


def make_net(**kw):
    return ToyNet(seed=kw.pop("seed", 1), L_T=8, L_I=16, V_T=12, V_I=20, **kw)


def toy_plan(arm, N=16, M=(), L_T=8, L_I=16):
    # W = 8 windows needs L_T, L_I divisible by 8; N=16 -> P_w=2
    return P.build(arm, N, L_I, M, L_T_=L_T) if arm in ("J", "Alt", "DA", "TFJ", "DA-low") else P.build(arm, N, L_I, M)


def uniforms(i=0, n=24):
    return rng.sampler_uniforms("D0", i, n)


def test_commit_counts_and_complete():
    net = make_net()
    for arm, M in (("J", ()), ("Alt", ()), ("DA", (1, 2, 7, 8)), ("TFJ", (1, 2))):
        plan = toy_plan(arm, 16, M)
        r = run_sample(net, plan, uniforms())
        assert [(len(x.text_pos), len(x.img_pos)) for x in r.records] == [(p.n_text, p.n_img) for p in plan.passes if p.total]
        assert (r.tail != net.mask_id).all() and (r.img >= 0).all()
        allt = sum((x.text_pos for x in r.records), [])
        alli = sum((x.img_pos for x in r.records), [])
        assert sorted(allt) == list(range(8)) and sorted(alli) == list(range(16))


def test_confidence_rule_matches_independent_recomputation():
    net = make_net()
    plan = toy_plan("J", 16)
    seen = []

    def hook(q, tail, img, ctx):
        seen.append((q, tail.clone(), img.clone(), ctx["sets"]))

    run_sample(net, plan, uniforms(), hook=hook)
    for q, tail, img, (st, si) in seen:
        lt, li = net.forward(tail, img)
        mt = (tail == net.mask_id).nonzero().flatten()
        mi = (img < 0).nonzero().flatten()
        ct = to_prob(lt, mt).max(-1).values.numpy()
        ci = to_prob(li, mi).max(-1).values.numpy()
        n_t, n_i = plan.passes[q - 1].n_text, plan.passes[q - 1].n_img
        exp_t = sorted(mt.numpy()[np.argsort(-ct, kind="stable")[:n_t]].tolist())
        exp_i = sorted(mi.numpy()[np.argsort(-ci, kind="stable")[:n_i]].tolist())
        assert st.tolist() == exp_t and si.tolist() == exp_i


def test_ties_break_to_lowest_index():
    conf = np.array([0.5, 0.9, 0.9, 0.9, 0.1])
    assert rank_positions(conf, 2).tolist() == [1, 2]
    assert rank_positions(conf, 4).tolist() == [1, 2, 3, 0]


def test_values_are_float64_inverse_cdf_of_marginal_at_commit():
    net = make_net()
    plan = toy_plan("J", 16)
    u = uniforms(3)
    log = []

    def hook(q, tail, img, ctx):
        log.append((tail.clone(), img.clone(), ctx))

    r = run_sample(net, plan, u, hook=hook)
    for (tail, img, ctx), rec in zip(log, r.records):
        assert ctx["p_text"].dtype == torch.float64 and ctx["p_img"].dtype == torch.float64
        row = {int(j): k for k, j in enumerate(ctx["masked_text_idx"])}
        for j, tok in zip(rec.text_pos, rec.text_tok):
            p = ctx["p_text"][row[j]]
            cdf = torch.cumsum(p, 0)
            exp = int(torch.searchsorted(cdf, torch.tensor([u[j] * float(cdf[-1])], dtype=torch.float64), right=True))
            assert tok == exp
        rowi = {int(j): k for k, j in enumerate(ctx["masked_img_idx"])}
        for j in rec.img_pos:
            p = ctx["p_img"][rowi[j]]
            cdf = torch.cumsum(p, 0)
            exp = int(torch.searchsorted(cdf, torch.tensor([u[8 + j] * float(cdf[-1])], dtype=torch.float64), right=True))
            assert int(r.img[j]) == exp


def test_inverse_cdf_matches_target_distribution():
    p = torch.tensor([[0.1, 0.2, 0.3, 0.4]], dtype=torch.float64)
    u = torch.as_tensor(np.random.default_rng(0).random(200000), dtype=torch.float64)
    draws = inverse_cdf(p.repeat(len(u), 1), u)
    freq = torch.bincount(draws, minlength=4).double() / len(u)
    assert torch.allclose(freq, p[0], atol=4e-3)
    # boundary: u -> 1 never leaves the support
    assert int(inverse_cdf(p, torch.tensor([1.0 - 1e-16], dtype=torch.float64))) == 3


def test_determinism_and_resume():
    net = make_net()
    plan = toy_plan("DA", 16, (1, 4, 5, 8))
    u = uniforms(5)
    a = run_sample(net, plan, u)
    b = run_sample(net, plan, u)
    assert torch.equal(a.tail, b.tail) and torch.equal(a.img, b.img)
    half = run_sample(net, plan, u, stop_pass=7)
    rest = run_sample(net, plan, u, state=(half.tail, half.img), start_pass=8)
    assert torch.equal(rest.tail, a.tail) and torch.equal(rest.img, a.img)
    assert [r.q for r in half.records] + [r.q for r in rest.records] == [r.q for r in a.records]


def test_probe_isolation_hook_does_not_change_samples():
    """G6 on the toy: the hook may call the network any number of times; tokens are identical (kernels are deterministic)."""
    net = make_net()
    plan = toy_plan("J", 16)
    u = uniforms(7)
    base = run_sample(net, plan, u)

    def hook(q, tail, img, ctx):
        t2, i2 = tail.clone(), img.clone()
        t2[ctx["sets"][0]] = 1
        for _ in range(3):
            net.forward(t2, i2)
        torch.rand(5)                                   # even a global RNG draw must not matter (sampler uses its own uniforms)

    probed = run_sample(net, plan, u, hook=hook)
    assert torch.equal(base.tail, probed.tail) and torch.equal(base.img, probed.img)


def test_identity_I3_tfj_empty_equals_j_samples():
    net = make_net()
    u = uniforms(11)
    a = run_sample(net, P.plan_TFJ(16, 16, (), L_T_=8), u)
    b = run_sample(net, P.plan_J(16, 16, L_T_=8), u)
    assert torch.equal(a.tail, b.tail) and torch.equal(a.img, b.img)


def test_identity_I2_alt_empty_text_equals_jd_samples():
    net = make_net()
    u = uniforms(12)
    a = run_sample(net, P.plan_Alt_empty_text(16, 16, L_T_=8), u)
    b = run_sample(net, P.plan_Jd(16, 16, L_T_=8), u)
    assert torch.equal(a.tail, b.tail) and torch.equal(a.img, b.img)
    assert a.n_forward == b.n_forward


def test_crn_same_position_same_uniform_across_arms():
    """A position committed at the same state in two arms gets the same value: J and DA share their joint windows."""
    net = make_net()
    u = uniforms(13)
    j = run_sample(net, P.plan_J(16, 16, L_T_=8), u)
    da = run_sample(net, P.plan_DA(16, 16, (8,), L_T_=8), u)
    # up to window 7 the plans are identical, so the states agree and so do the committed values
    n7 = 14
    assert [(r.text_pos, r.img_pos, r.text_tok) for r in j.records[:n7]] == [(r.text_pos, r.img_pos, r.text_tok) for r in da.records[:n7]]


def test_p_rand_uses_fixed_priorities_and_differs_from_confidence():
    net = make_net()
    u = uniforms(14)
    prio = rng.position_priorities("D0", 14, 24)
    plan = P.plan_J(16, 16, L_T_=8)
    a = run_sample(net, plan, u, rule="rand", prio=prio)
    b = run_sample(net, plan, u, rule="rand", prio=prio)
    c = run_sample(net, plan, u)
    assert torch.equal(a.tail, b.tail) and torch.equal(a.img, b.img)
    # random rule commits the lowest-priority masked positions first
    first = a.records[0]
    assert first.img_pos == sorted(np.argsort(prio[8:], kind="stable")[:len(first.img_pos)].tolist())
    assert [r.img_pos for r in a.records] != [r.img_pos for r in c.records]
    with pytest.raises(ValueError):
        run_sample(net, plan, u, rule="rand")


def test_pooled_rule_commits_global_top_counts():
    net = make_net()
    plan = P.plan_Jglobal(16, 16, L_T_=8)
    r = run_sample(net, plan, uniforms(15))
    assert sum(len(x.text_pos) + len(x.img_pos) for x in r.records) == 24
    assert [len(x.text_pos) + len(x.img_pos) for x in r.records] == [p.n_pooled for p in plan.passes]


def test_window_arm_fractions_equal_at_boundaries_in_sampled_state():
    net = make_net()
    plan = P.plan_DA(16, 16, (2, 3), L_T_=8)
    r = run_sample(net, plan, uniforms(16))
    cum_t = cum_i = 0
    by_w = {}
    for rec in r.records:
        cum_t += len(rec.text_pos)
        cum_i += len(rec.img_pos)
        by_w[rec.window] = (cum_t, cum_i)
    assert [by_w[w] for w in range(1, 9)] == [(w, 2 * w) for w in range(1, 9)]


def test_record_keeps_state_pad_flags():
    net = make_net(pad_boost=8.0)
    r = run_sample(net, P.plan_J(16, 16, L_T_=8), uniforms(17))
    flags = [f for rec in r.records for f in rec.text_state_pad]
    assert len(flags) == 8 and any(flags)
