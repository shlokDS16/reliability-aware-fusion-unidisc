"""CRC calibration (v2 section 6, v1 Prop. 5 / limiting cases L1, L5), arms (Alg. 10), HOLD check and resource guards. numpy only."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2 import common                                            # noqa: E402
from exp_p2.gate import arms, calibrate as cal, hold, guards          # noqa: E402


# ------------------------------------------------------------------------------------------------ CRC: formula against brute force
def _brute_tau(J, alpha):
    """inf{tau : n/(n+1) Rhat(tau) + 1/(n+1) <= alpha}, tau searched over every jittered value (flag u > tau)."""
    n = len(J)
    cands = np.unique(np.concatenate(J))
    best = None
    for t in cands:
        R = np.mean([np.mean(u > t) for u in J])
        if n / (n + 1) * R + 1 / (n + 1) <= alpha:
            best = t if best is None else min(best, t)
    return best


@pytest.mark.parametrize("seed,alpha", [(0, 0.05), (1, 0.10), (2, 0.03)])
def test_threshold_matches_brute_force(seed, alpha):
    rng = np.random.default_rng(seed)
    U = [rng.standard_t(4, size=int(rng.integers(20, 40))) + rng.normal() for _ in range(40)]
    eps0 = cal.eps0_from(U)
    thr = cal.fit_threshold(U, alpha, eps0, seed=7)
    rng2 = np.random.default_rng(7)
    J = [cal.jitter(u, eps0, rng2) for u in U]
    assert thr.feasible
    assert thr.tau == _brute_tau(J, alpha)
    n = len(U)
    assert n / (n + 1) * thr.r_hat + 1 / (n + 1) <= alpha + 1e-12


def test_infeasible_alpha_flags_nothing_and_alpha_one_flags_all():
    U = [np.random.default_rng(i).normal(size=30) for i in range(20)]            # n = 20 -> 1/(n+1) = 0.0476
    t = cal.fit_threshold(U, 0.02, cal.eps0_from(U), seed=1)
    assert not t.feasible and t.tau == float("inf")
    assert not cal.flag(U[0], t, np.random.default_rng(0)).any()
    t1 = cal.fit_threshold(U, 1.0, cal.eps0_from(U), seed=1)
    assert t1.tau == float("-inf") and cal.flag(U[0], t1, np.random.default_rng(0)).all()


def test_threshold_json_roundtrip_with_inf():
    t = cal.Threshold(float("inf"), 0.01, 10, 0.1, "q", 8, 3, "abc", False, 0.0, True)
    t2 = cal.Threshold.from_json(__import__("json").loads(__import__("json").dumps(t.to_json())))
    assert t2 == t


def test_jitter_scale_below_smallest_gap_keeps_order_of_distinct_values():
    rng = np.random.default_rng(3)
    U = [np.round(rng.normal(size=60), 2) for _ in range(10)]                    # heavy ties, smallest gap 0.01
    gap = cal.min_positive_gap(U)
    assert gap == pytest.approx(0.01, abs=1e-9)
    eps0 = cal.eps0_from(U)
    assert 0 < eps0 < gap
    allv = np.concatenate(U)
    j = cal.jitter(allv, eps0, np.random.default_rng(0))
    vals = np.unique(allv)
    for a, b in zip(vals[:-1], vals[1:]):                                        # every element of a lower distinct value stays below every element of a higher one
        assert j[allv == a].max() < j[allv == b].min()
    assert (j >= allv).all() and (j < allv + eps0).all()


# ------------------------------------------------------------------------------------------------ L1: calibration guarantee on exchangeable scores
def _item(rng, mu, df, ties):
    u = mu + rng.standard_t(df, size=len(mu))
    return np.round(u * 2) / 2 if ties else u                                    # ties: half-unit grid


@pytest.mark.parametrize("ties", [False, True])
def test_realised_false_alarm_proportion_is_at_most_alpha(ties):
    """L1: n_cal = 100, 2000 repetitions of calibrate-then-test with position-heterogeneous exchangeable items; mean FAP <= alpha + 3 MC SE."""
    alpha, n_cal, reps, m = 0.05, 100, 2000, 40
    rng = np.random.default_rng(11)
    mu = np.linspace(-1.5, 1.5, m)                                              # heterogeneous per position
    faps = np.empty(reps)
    for r in range(reps):
        U = [_item(rng, mu, 5, ties) for _ in range(n_cal)]
        thr = cal.fit_threshold(U, alpha, cal.eps0_from(U), seed=int(rng.integers(1 << 31)))
        faps[r] = cal.flag(_item(rng, mu, 5, ties), thr, rng).mean()
    se = faps.std(ddof=1) / np.sqrt(reps)
    assert faps.mean() <= alpha + 3 * se, (faps.mean(), se)
    assert faps.mean() > alpha / 3                                              # not vacuous: the gate does flag tokens


def test_uniform_scores_give_a_random_gate_with_fap_near_alpha():
    """L5: all scores identical (uniform predictions): eps0 falls back to 1.0 and the gate is a random gate."""
    alpha, n_cal, reps, m = 0.1, 100, 1500, 30
    U = [np.zeros(m) for _ in range(n_cal)]
    assert cal.eps0_from(U) == 1.0
    rng = np.random.default_rng(5)
    faps = []
    for r in range(reps):
        thr = cal.fit_threshold(U, alpha, 1.0, seed=int(rng.integers(1 << 31)))
        faps.append(cal.flag(np.zeros(m), thr, rng).mean())
    faps = np.array(faps)
    se = faps.std(ddof=1) / np.sqrt(reps)
    assert abs(faps.mean() - alpha) < 0.35 * alpha + 3 * se                     # near alpha (finite-sample conservative, never above)
    assert faps.mean() <= alpha + 3 * se


# ------------------------------------------------------------------------------------------------ text units
def test_word_units():
    pieces = ["The", "▁quick", "▁br", "own", "▁fox"]
    w = cal.word_ids_from_pieces(pieces)
    assert w.tolist() == [0, 1, 2, 2, 3]
    u = np.array([0.1, 0.5, 0.2, 0.9, -1.0])
    wu = cal.word_suspicion(u, w)
    assert wu.tolist() == [0.1, 0.5, 0.9, -1.0]                                  # max piece suspicion = min piece score
    assert cal.expand_word_flags(wu > 0.4, w).tolist() == [False, True, True, True, False]


# ------------------------------------------------------------------------------------------------ arms
def test_geometry_matched_gate_is_a_nonzero_torus_translation():
    grid = 8
    G = np.zeros((grid, grid), bool)
    G[1:4, 2:7] = True                                                           # 3 x 5 block
    G = G.reshape(-1)
    seen = set()
    for s in range(3000):
        g = arms.geometry_matched_gate(G, grid, np.random.default_rng(s))
        assert g.sum() == G.sum()                                                # same size
        found = [(dy, dx) for dy in range(grid) for dx in range(grid) if (dy, dx) != (0, 0)
                 and np.array_equal(np.roll(G.reshape(grid, grid), (dy, dx), (0, 1)).reshape(-1), g)]
        assert len(found) == 1                                                   # exactly one non-zero shift reproduces it (this block is aperiodic)
        seen.add(found[0])
    assert len(seen) == grid * grid - 1                                          # every non-zero shift occurs, (0,0) never
    # determinism per seed
    assert np.array_equal(arms.geometry_matched_gate(G, grid, np.random.default_rng(9)), arms.geometry_matched_gate(G, grid, np.random.default_rng(9)))


def test_geometry_matched_gate_shift_is_uniform_and_empty_gate_stays_empty():
    grid, n = 4, 30000
    G = np.zeros(grid * grid, bool)
    G[5] = True                                                                  # single token: the shifted position reveals the shift
    cnt = np.zeros(grid * grid)
    for s in range(n):
        cnt += arms.geometry_matched_gate(G, grid, np.random.default_rng(s))
    assert cnt[5] == 0
    others = np.delete(cnt, 5) / n
    assert np.all(np.abs(others - 1 / 15) < 0.01)
    assert not arms.geometry_matched_gate(np.zeros(grid * grid, bool), grid, np.random.default_rng(0)).any()


def test_scattered_topk_changed_and_text_gates():
    rng = np.random.default_rng(0)
    g = arms.scattered_gate(7, 64, rng)
    assert g.sum() == 7
    assert arms.scattered_gate(0, 64, rng).sum() == 0 and arms.scattered_gate(99, 10, rng).sum() == 10
    s = np.array([0.1, 0.9, 0.3, 0.9, 0.5])
    assert arms.topk_gate(s, 2).tolist() == [False, True, False, True, False]    # ties by position
    assert arms.topk_gate(s, 0).sum() == 0
    clean, obs = np.array([1, 2, 3, 4]), np.array([1, 9, 3, 8])
    assert arms.changed_code_gate(clean, obs).tolist() == [False, True, False, True]
    assert arms.random_word_gate(10, 3, rng).sum() == 3 and arms.no_gate(5).sum() == 0


# ------------------------------------------------------------------------------------------------ HOLD
def test_hold_blocks_on_global_run_and_stage_files(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    hold.require_clear("P2-GATE-M2")                                             # nothing there: passes
    (tmp_path / "P2-PROBE-02").mkdir()
    g = tmp_path / "P2-PROBE-02" / "HOLD.txt"
    g.write_text("on hold")
    assert hold.active_holds("P2-GATE-M2") == [g]
    with pytest.raises(hold.HoldActive):
        hold.require_clear("P2-GATE-M2")
    g.unlink()
    (tmp_path / "P2-GATE-M2").mkdir()
    (tmp_path / "P2-GATE-M2" / "HOLD.txt").write_text("x")
    (tmp_path / "GATE-HOLD.txt").write_text("y")
    assert len(hold.active_holds("P2-GATE-M2")) == 2
    assert len(hold.active_holds("P2-GATE-M3")) == 1                             # only the project-wide file applies to another stage
    assert hold.EXIT_HOLD == 7


def test_real_runs_dir_hold_is_untouched_by_the_check():
    """The check only reads; the shipped hold file (if present in this worktree) must still be there after calling it."""
    p = Path(common.RUNS) / "P2-PROBE-02" / "HOLD.txt"
    before = p.exists()
    hold.active_holds("P2-GATE-M2")
    assert p.exists() == before


# ------------------------------------------------------------------------------------------------ guards
def test_guards_memory_ac_rise_and_slow_item():
    g = guards.Guards(used_fn=lambda: 9500.0, ac_fn=lambda: True)
    assert g.before_item(0) is None                                              # 9500 <= 10000 (first-item limit)
    assert "9500" in g.before_item(1)                                            # 9500 > 9000 (later items)
    g = guards.Guards(used_fn=lambda: 10500.0, ac_fn=lambda: True)
    assert "10500" in g.before_item(0)
    g = guards.Guards(used_fn=iter([5000.0, 5100.0, 5200.0, 6900.0]).__next__, ac_fn=lambda: True)
    assert g.before_item(0) is None and g.after_item(2.0) is None              # the rise rule is armed by the first completed item (re-audit W1)
    assert g.before_item(1) is None and g.after_item(2.0) is None and g.before_item(2) is None and g.after_item(2.0) is None
    assert "rise 1700" in g.before_item(3).replace("_", " ")                  # +1.7 GB after the baseline items
    g = guards.Guards(used_fn=lambda: 100.0, ac_fn=lambda: False)
    assert g.before_item(0) == "ac_lost"
    g = guards.Guards(used_fn=lambda: 100.0, ac_fn=lambda: None)                 # unknown power state does not stop
    assert g.before_item(0) is None
    g = guards.Guards(used_fn=lambda: 100.0, ac_fn=lambda: True)
    assert [g.after_item(t) for t in (2.0, 2.2, 1.8)] == [None, None, None]
    assert g.after_item(3.0) is None                                             # 3.0 <= 2 * median(2.0, 2.2, 1.8) = 4.0
    assert "slow_item" in g.after_item(9.0)


if __name__ == "__main__":                                                        # plain run without pytest: the parametrised/tmp_path tests need pytest
    sys.exit(pytest.main([__file__, "-q"]))
