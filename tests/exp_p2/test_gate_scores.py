"""Gate scores and evidence with the fake network (v1 limiting cases L2, L3, L6, L7, L8, L10; v2 4.1, Alg. 5'). CPU only, tiny sequences."""
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from fake_gate import FakeScorer                                                      # noqa: E402
from exp_p2 import core                                                              # noqa: E402
from exp_p2.scoring import Spec, masked_logprobs, MASK_ID, IMG_LO, IMG_HI, TEXT_LO, TEXT_HI   # noqa: E402
from exp_p2.gate import scores, evidence, dcache, calibrate as cal, arms            # noqa: E402

GRID = 4                                  # 16 image tokens: tiny, but the real layout and vocabulary ranges
CAP = [101, 202, 303, 404, 505, 606]      # 6 caption tokens


def _codes(seed=0, m=GRID * GRID):
    return np.random.default_rng(seed).integers(0, 16384, size=m)


def _setup(**kw):
    sc = FakeScorer(grid=GRID, **kw)
    codes = _codes()
    return sc, codes, sc.build(CAP, codes)


def _groups(sc, K=4, seed=1):
    return core.complementary_groups(sc.L_I, K, np.random.default_rng(seed))


# ------------------------------------------------------------------------------------------------ B: masks and values
def test_B_masks_caption_and_one_group_per_pass_and_matches_direct_forward():
    sc, codes, st = _setup()
    g = _groups(sc, 4)
    sc.rows.clear()
    out = scores.image_B(sc, st, g, 4)
    rows = list(sc.rows)
    assert len(rows) == 4                                                             # K passes
    img = st["img_pos"].numpy()
    cap = st["cap_pos"].numpy()
    f = sc.logits_fn(st)
    for k, row in enumerate(rows):
        masked = (row == MASK_ID).numpy()
        assert masked[cap].all()                                                      # caption masked (evidence-separation rule)
        grp = np.nonzero(g == k)[0]
        expect = np.zeros(len(row), bool)
        expect[cap] = True
        expect[img[grp]] = True
        assert (masked == expect).all()                                               # exactly caption + group k
        lp = torch.log_softmax(f(row[None])[0, img[grp], IMG_LO:IMG_HI].float(), -1)
        direct = lp.gather(1, torch.as_tensor(codes[grp])[:, None])[:, 0].numpy()
        assert np.allclose(out["B"][grp], direct, atol=1e-6)
        assert np.allclose(out["maxp"][grp], lp.max(1).values.exp().numpy(), atol=1e-6)
    assert (out["maxp"] > 0).all() and (out["B"] <= 0).all()


def test_L6_K1_is_refused_and_degenerate_B_equals_D():
    sc, codes, st = _setup()
    with pytest.raises(ValueError):
        scores.image_B(sc, st, np.zeros(sc.L_I, int), 1)
    b1 = scores.image_B(sc, st, np.zeros(sc.L_I, int), 1, allow_degenerate=True)["B"]
    D = evidence.gather_codes(scores.full_image_lp(sc, st, caption_masked=True), codes)
    assert np.allclose(b1, D, atol=1e-6)                                              # one group = everything masked => B == D, q == 0
    assert np.allclose(scores.suspicion_q(b1, D), 0, atol=1e-6)


def test_L7_K_equals_m_is_leave_one_out():
    sc, codes, st = _setup()
    m = sc.L_I
    g = np.arange(m)                                                                  # one position per group
    out = scores.image_B(sc, st, g, m)
    f = sc.logits_fn(st)
    img, cap = st["img_pos"], st["cap_pos"]
    for j in range(m):
        x = st["base"].clone()
        x[cap] = MASK_ID
        x[img[j]] = MASK_ID
        lp = torch.log_softmax(f(x[None])[0, img[j], IMG_LO:IMG_HI].float(), -1)
        assert abs(float(lp[codes[j]]) - out["B"][j]) < 1e-6


# ------------------------------------------------------------------------------------------------ D / C / nulls
def test_full_image_lp_shapes_and_masks():
    sc, codes, st = _setup()
    sc.rows.clear()
    C = scores.full_image_lp(sc, st, caption_masked=False)
    D = scores.full_image_lp(sc, st, caption_masked=True)
    assert C.shape == D.shape == (sc.L_I, IMG_HI - IMG_LO)
    r_c, r_d = sc.rows
    assert (r_c[st["img_pos"]] == MASK_ID).all() and (r_c[st["cap_pos"]] != MASK_ID).all()    # caption visible
    assert (r_d[st["img_pos"]] == MASK_ID).all() and (r_d[st["cap_pos"]] == MASK_ID).all()    # layout only
    assert torch.allclose(C.exp().sum(1), torch.ones(sc.L_I), atol=1e-4)


def test_C_does_not_depend_on_image_content_and_D_only_on_caption_length():
    sc = FakeScorer(grid=GRID)
    s1, s2 = sc.build(CAP, _codes(1)), sc.build(CAP, _codes(2))
    assert torch.equal(scores.full_image_lp(sc, s1, False), scores.full_image_lp(sc, s2, False))        # C never sees the image
    s3 = sc.build([9, 8, 7, 6, 5, 4], _codes(3))                                                         # other caption, same length
    assert torch.equal(scores.full_image_lp(sc, s1, True), scores.full_image_lp(sc, s3, True))          # D: layout only
    s4 = sc.build(CAP + [1], _codes(1))                                                                  # longer caption: different layout
    assert not torch.equal(scores.full_image_lp(sc, s1, True), scores.full_image_lp(sc, s4, True))
    r = dcache.check_layout_only(sc, CAP, [9, 8, 7, 6, 5, 4], _codes(1), _codes(5))
    assert r["ok"] and r["n_passes"] == 4                                                                # L10 on the fake (by construction)


def test_dcache_memory_and_disk_roundtrip_and_pass_count(tmp_path):
    sc = FakeScorer(grid=GRID)
    codes = _codes()
    st = sc.build(CAP, codes)
    dc = dcache.DCache(tmp_path)
    d1 = dc.image_logp(sc, st, len(CAP), codes)
    assert dc.n_computed == 1
    d1b = dc.image_logp(sc, sc.build(CAP, _codes(9)), len(CAP), codes)                    # same n: cache hit, no new pass
    assert dc.n_computed == 1 and np.array_equal(d1, d1b)
    dc2 = dcache.DCache(tmp_path)                                                         # new process: loaded from disk
    d2 = dc2.image_logp(sc, st, len(CAP), codes)
    assert dc2.n_computed == 0 and np.array_equal(d1, d2)
    assert (tmp_path / "DI_n006.npy").exists() and not list(tmp_path.glob("*.tmp"))
    t1 = dc.text_logp(sc, st, len(CAP), CAP)
    assert t1.shape == (len(CAP),) and (t1 <= 0).all()
    other = tmp_path / "other"                                                            # (a mapped file cannot be overwritten on Windows)
    other.mkdir()
    (other / "DI_n006.npy").write_bytes(b"torn")                                          # torn file: recomputed, not crashed
    dc3 = dcache.DCache(other)
    assert np.array_equal(dc3.image_logp(sc, st, len(CAP), codes), d1) and dc3.n_computed == 1


# ------------------------------------------------------------------------------------------------ L3: uninformative other modality
def test_L3_independent_joint_gives_A_equals_B_and_C_equals_D_and_zero_evidence():
    sc, codes, st = _setup(cross=0.0)
    img, cap = st["img_pos"], st["cap_pos"]
    g = _groups(sc, 4)
    masks = core.masks_from_groups(g, 4)
    for m in masks:
        pos = img[torch.as_tensor(m)]
        a = next(iter(masked_logprobs(sc.logits_fn(st), st["base"], [Spec(pos, IMG_LO, IMG_HI)])))
        b = next(iter(masked_logprobs(sc.logits_fn(st), st["base"], [Spec(pos, IMG_LO, IMG_HI, extra=cap)])))
        assert torch.allclose(a, b, atol=1e-6)                                            # A == B  -> r_original == 0
    C = scores.full_image_lp(sc, st, False)
    D = scores.full_image_lp(sc, st, True)
    assert torch.allclose(C, D, atol=1e-6)                                                # C == D  -> w == 0
    st2 = sc.build([5, 6, 7, 8, 9, 10], codes)
    delta = evidence.gather_codes(scores.full_image_lp(sc, st, False), codes) - evidence.gather_codes(scores.full_image_lp(sc, st2, False), codes)
    assert np.allclose(delta, 0, atol=1e-6)                                               # captions cannot be told apart by an independent model
    ev = evidence.evidence_from_delta(np.zeros(16))
    assert ev["mean"] == 0 and ev["y"] == 0 and np.isnan(ev["z"])                         # zero spread: z undefined (counted by the analysis), never inf


def test_with_coupling_captions_differ():
    sc, codes, st = _setup(cross=1.0)
    st2 = sc.build([5, 6, 7, 8, 9, 10], codes)
    d = evidence.gather_codes(scores.full_image_lp(sc, st, False), codes) - evidence.gather_codes(scores.full_image_lp(sc, st2, False), codes)
    assert np.abs(d).max() > 1e-3


# ------------------------------------------------------------------------------------------------ L2: all corrupted / gated
def test_L2_all_gated_gives_exactly_zero_evidence():
    d = np.random.default_rng(0).normal(size=16)
    ev = evidence.arm_summary(d, np.ones(16, bool))
    assert ev["n"] == 0 and ev["sum"] == 0.0 and ev["mean"] == 0.0 and ev["y"] == 0
    assert np.isnan(ev["z"]) and np.isnan(ev["d"])                              # undefined, not a finite zero (audit M7)
    one = evidence.evidence_from_delta(np.array([0.3]))
    assert one["n"] == 1 and np.isnan(one["z"]) and np.isnan(one["d"]) and one["y"] == 1
    sc, codes, st = _setup()
    n = len(CAP)
    Dt = sc.build(CAP, codes)
    null = evidence.gather_codes(scores.full_text_lp(sc, Dt, image_all_masked=True), np.asarray(CAP))
    allg = np.ones(sc.L_I, bool)
    lp_all, lp_none = scores.text_arms_lp(sc, st, [allg, None])
    cond_all = evidence.gather_codes(lp_all, np.asarray(CAP))
    assert evidence.text_pmi(cond_all, null) == 0.0                                      # image fully withdrawn: text direction equals its null exactly
    cond_none = evidence.gather_codes(lp_none, np.asarray(CAP))
    assert abs(evidence.text_pmi(cond_none, null)) > 1e-6                                # with the image it differs (coupling on)


def test_text_arms_mask_exactly_the_gated_image_tokens():
    sc, codes, st = _setup()
    G = np.zeros(sc.L_I, bool)
    G[[1, 5, 6]] = True
    sc.rows.clear()
    out = scores.text_arms_lp(sc, st, [None, G, G.copy(), np.zeros(sc.L_I, bool)])
    assert len(out) == 4 and len(sc.rows) == 4
    img, cap = st["img_pos"].numpy(), st["cap_pos"].numpy()
    for row, g in zip(sc.rows, [None, G, G, None]):
        m = (row == MASK_ID).numpy()
        exp = np.zeros(len(row), bool)
        exp[cap] = True
        if g is not None:
            exp[img[g]] = True
        assert (m == exp).all()
    assert torch.equal(out[0], out[3]) and torch.equal(out[1], out[2])


def test_L8_alpha_zero_gate_is_empty_and_every_arm_equals_none_bit_for_bit():
    sc, codes, st = _setup()
    U = [np.random.default_rng(i).normal(size=16) for i in range(30)]
    thr = cal.fit_threshold(U, 0.0, cal.eps0_from(U), seed=0)                             # alpha = 0 -> infeasible -> flag nothing
    G = cal.flag(np.random.default_rng(1).normal(size=16), thr, np.random.default_rng(2))
    assert not G.any()
    delta = np.random.default_rng(3).normal(size=16)
    assert evidence.arm_summary(delta, G) == evidence.evidence_from_delta(delta)
    assert evidence.arm_summary(delta, arms.no_gate(16)) == evidence.arm_summary(delta, G)


def test_oracle_removal_raises_z_and_random_removal_scales_z_by_sqrt_of_the_kept_fraction():
    """Prop. 4 flavour (v2 5.3). The spec says a random gate 'leaves z unchanged in expectation'; with z = mean / (sd / sqrt(|R|)) that is false:
    random removal of a fraction g scales z by sqrt(1 - g). The size-invariant effect size d = mean / sd IS unchanged (recorded for the analysis)."""
    rng = np.random.default_rng(0)
    m, rho, mu = 1024, 0.3, 0.2
    z_none, z_chg, z_rand, d_none, d_rand = [], [], [], [], []
    for _ in range(300):
        Z = rng.random(m) < rho
        d = np.where(Z, rng.normal(0, 1.0, m), rng.normal(mu, 0.5, m))
        z_none.append(evidence.evidence_from_delta(d)["z"])
        z_chg.append(evidence.arm_summary(d, Z)["z"])
        er = evidence.arm_summary(d, arms.scattered_gate(int(Z.sum()), m, rng))
        z_rand.append(er["z"])
        d_none.append(evidence.evidence_from_delta(d)["d"])
        d_rand.append(er["d"])
    assert np.mean(z_chg) > np.mean(z_none) * 1.1
    assert np.mean(z_rand) / np.mean(z_none) == pytest.approx(np.sqrt(1 - rho), abs=0.03)
    assert np.mean(d_rand) == pytest.approx(np.mean(d_none), rel=0.03)


# ------------------------------------------------------------------------------------------------ other scores
def test_text_B_masks_image_and_one_group():
    sc, codes, st = _setup()
    gT = core.complementary_groups(len(CAP), 3, np.random.default_rng(0))
    sc.rows.clear()
    out = scores.text_B(sc, st, gT, 3)
    assert len(sc.rows) == 3 and out["B"].shape == (len(CAP),)
    for row in sc.rows:
        assert (row[st["img_pos"]] == MASK_ID).all()


def test_observed_unmasked_logprob_masks_only_the_caption():
    sc, codes, st = _setup()
    sc.rows.clear()
    v = scores.tbv_score_raw_logits(sc, st)
    (row,) = sc.rows
    assert (row[st["cap_pos"]] == MASK_ID).all() and (row[st["img_pos"]] != MASK_ID).all()
    assert v.shape == (sc.L_I,) and (v <= 0).all()


def test_gather_codes_torch_equals_numpy():
    lp = torch.log_softmax(torch.randn(10, 50), -1)
    codes = np.random.default_rng(0).integers(0, 50, 10)
    assert np.array_equal(evidence.gather_codes(lp, codes), evidence.gather_codes(lp.numpy(), codes))


def test_suspicion_q_is_float32_negative_B_minus_D():
    B, D = np.array([-3.0, -1.0], np.float32), np.array([-2.0, -2.0], np.float32)
    u = scores.suspicion_q(B, D)
    assert u.dtype == np.float32 and u.tolist() == [1.0, -1.0]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
