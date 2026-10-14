"""Plan-generator tests (card stage 0: J, Alt, DA, TFJ, Sep; identities I2, I3; totals, window budgets, floor rule)."""
import pytest

from exp001 import plan as P

L_I = 1024  # 512 px


def test_floor_rule_sums():
    for c in (4, 32, 128, 1024, 1056):
        for m in (2, 3, 4, 7, 8, 24, 32):
            assert sum(P.f(q, c, m) for q in range(1, m + 1)) == c


def test_joint_k0_counts():
    p = P.plan_J(32, L_I)
    assert all(x == (1, 32) for x in p.counts())
    assert p.totals() == (32, 1024) and len(p.passes) == 32 and p.n_forward_passes() == 32


def test_pure_window_k0_counts():
    p = P.plan_Sep(32, L_I, 3)
    w3 = [x for x in p.passes if x.window == 3]
    assert [(x.n_text, x.n_img) for x in w3] == [(4, 0), (0, 42), (0, 43), (0, 43)]
    assert all((x.n_text, x.n_img) == (1, 32) for x in p.passes if x.window != 3)


def test_tfj_window_k0_counts():
    p = P.plan_TFJ(32, L_I, (2, 5))
    w2 = [(x.n_text, x.n_img) for x in p.passes if x.window == 2]
    assert w2 == [(4, 32), (0, 32), (0, 32), (0, 32)]
    assert [(x.n_text, x.n_img) for x in p.passes if x.window == 1] == [(1, 32)] * 4


@pytest.mark.parametrize("N", [16, 32, 64])
@pytest.mark.parametrize("L_I_", [1024, 256])
@pytest.mark.parametrize("arm,M", [("J", ()), ("Alt", ()), ("DA", (1, 2, 7, 8)), ("DA-low", (3, 4, 5, 6)), ("TFJ", (1, 2, 7, 8)),
                                  ("Sep1", ()), ("Sep8", ())])
def test_totals_and_window_budgets(N, L_I_, arm, M):
    p = P.build(arm, N, L_I_, M)
    assert p.totals() == (32, L_I_)
    # matched per-window per-modality budgets: masked fractions agree at every window boundary (card 5.2)
    c_I = L_I_ // 8
    assert P.boundary_fractions(p) == [(4 * w, c_I * w) for w in range(1, 9)]
    assert len(p.passes) == N  # pure windows replace P_w joint passes by one text pass + (P_w - 1) image passes


def test_k_plus_and_k_minus_pure_window():
    p = P.plan_Sep(16, L_I, 4)
    assert [(x.n_text, x.n_img) for x in p.passes if x.window == 4] == [(4, 0), (0, 128)]
    assert [(x.n_text, x.n_img) for x in p.passes if x.window == 1] == [(2, 64), (2, 64)]
    q = P.plan_Sep(64, L_I, 4)
    img = [x.n_img for x in q.passes if x.window == 4 and x.n_img]
    assert len(img) == 7 and sum(img) == 128 and max(img) - min(img) <= 1
    tf = P.plan_TFJ(16, L_I, (1,))
    assert [(x.n_text, x.n_img) for x in tf.passes if x.window == 1] == [(4, 64), (0, 64)]


def test_alt_has_eight_text_passes():
    a = P.plan_Alt(32, L_I)
    assert sum(1 for x in a.passes if x.kind == "text") == 8
    assert sum(1 for x in a.passes if x.n_text == 4 and x.n_img == 0) == 8
    assert sum(1 for x in a.passes if x.n_img) == 24


def test_da_is_joint_outside_m():
    p = P.plan_DA(32, L_I, (1, 2, 7, 8))
    for w in range(1, 9):
        ws = [(x.n_text, x.n_img) for x in p.passes if x.window == w]
        assert ws == ([(4, 0), (0, 42), (0, 43), (0, 43)] if w in (1, 2, 7, 8) else [(1, 32)] * 4)


def test_invalid_geometry():
    with pytest.raises(ValueError):
        P.plan_J(12, L_I)       # W does not divide N
    with pytest.raises(ValueError):
        P.plan_J(8, L_I)        # P_w = 1 < 2
    with pytest.raises(ValueError):
        P.plan_Sep(32, L_I, 9)


def test_tf_if_jglobal_jd():
    tf, iff = P.plan_TF(32, L_I), P.plan_IF(32, L_I)
    assert [(x.n_text, x.n_img) for x in tf.passes[:8]] == [(4, 0)] * 8 and len(tf.passes) == 32
    assert sum(x.n_img for x in tf.passes[8:]) == L_I
    assert [(x.n_text, x.n_img) for x in iff.passes[-8:]] == [(4, 0)] * 8 and sum(x.n_img for x in iff.passes[:24]) == L_I
    jg = P.plan_Jglobal(32, L_I)
    assert sum(x.n_pooled for x in jg.passes) == 32 + L_I and all(x.pooled for x in jg.passes)
    jd = P.plan_Jd(32, L_I)
    assert len(jd.passes) == 24 and jd.totals() == (32, L_I)
    assert [x.n_img for x in jd.passes[:3]] == [42, 43, 43]
    assert [x.n_text for x in jd.passes] == [P.f(q, 32, 24) for q in range(1, 25)]


def test_identity_I3_tfj_empty_equals_j():
    assert P.plan_TFJ(32, L_I, ()).passes == P.plan_J(32, L_I).passes
    assert P.plan_TFJ(16, L_I, ()).passes == P.plan_J(16, L_I).passes


def test_identity_I2_alt_empty_text_equals_jd():
    a = P.plan_Alt_empty_text(32, L_I)
    assert len(a.passes) == 32 and sum(1 for x in a.passes if x.kind == "noop") == 8
    d = P.drop_noops(a)
    assert d.counts() == P.plan_Jd(32, L_I).counts()
    assert a.totals() == (32, L_I)


def test_window_centres():
    assert P.window_centres(4) == [2, 6, 10, 14, 18, 22, 26, 30]
    assert P.window_centres_kplus() == [1, 3, 5, 7, 9, 11, 13, 15]
