"""E-pred FIT CODE (SAP Addendum A2 AD.3 as demoted by A2b AB.3 item 5): the Prop. 4 sign function (spec v2 5.3, general form with mu_c not 0), the pooled token-level fit on the headroom
items and its stability bootstrap, and the self-test. This module, `theory.py` and `tests/exp_p2/test_gate_epred_fit.py` are the fit code whose SHA-256 is written into `epred_frozen.json`
(`epred.FIT_CODE_FILES`); they are committed and gate-auditor-checked BEFORE the fit chunk runs and are not edited afterwards. Loading, the CLI, scoring and the hashing live in `epred.py`
and may still be fixed after the freeze without touching the fit. CPU only; no model; no test, no p-value.

Per cell c in P1, P2, P3 (only those with an operating point), PS1 (patch), PS2 (swap): s_c = sign(SNR_after - SNR_before) of the additive image-direction statistic, from the inputs rho, mu,
sigma^2, mu_c, sigma_c^2, alpha_obs, beta_obs measured POOLED over the 100 headroom items at token level (classes from the changed-code labels Z; GATE flags from the fit chunk). The sign does not
depend on the number of tokens m. The stability figure (share of 10,000 headroom-ITEM bootstrap resamples with the same sign, seed of `prop4_plugin`) is reported beside s_c and never changes it."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2.gate import config, seeds, theory                              # noqa: E402

CELLS = ("P1", "P2", "P3", "PS1", "PS2")
P_CELLS = ("P1", "P2", "P3")
PS_CELLS = ("PS1", "PS2")
P_CORRUPTION = dict(zip(P_CELLS, config.REALISTIC))
PS_KEY = {"PS1": "patch", "PS2": "swap"}
N_BOOT = 10000
TIE_TOL = 1e-12                                       # |SNR_after - SNR_before| <= TIE_TOL is a tie: no sign (counted, excluded)
SEED_NAME = "prop4_plugin"                            # existing analysis name in seeds.ANALYSES (position 19): the stability bootstrap of the Prop. 4 plug-in; no new child seed is needed
LABEL = ("secondary, descriptive; no test, no p-value, no alpha (family E withdrawn, AB.3 item 1); never pooled with the suite cells; no P result is called predicted, explained or caused (AB.1); "
         "Prop. 4 is not said to predict, explain or be supported (AB.3 item 4)")


def seed_fingerprint() -> dict:
    """What the fit takes from seeds.py: the root seed, the analysis names up to and including SEED_NAME (their order fixes the spawn position) and the first words of the child's state. Appending
    names to seeds.ANALYSES after the freeze (as other families do) leaves this unchanged, so seeds.py itself need not be hashed."""
    pos = seeds.ANALYSES.index(SEED_NAME)
    return dict(root_seed=seeds.ROOT_SEED, name=SEED_NAME, position=pos, analyses_prefix=list(seeds.ANALYSES[:pos + 1]), child_state=[int(x) for x in seeds.seed_for(SEED_NAME).generate_state(4)])


# ------------------------------------------------------------------------------------------------ the Prop. 4 sign function (spec v2 5.3, general form)
def sign_of_gating(rho: float, alpha: float, beta: float, mu: float, sigma2: float, mu_c: float, sigma2_c: float, m: int = 1) -> dict:
    """sign(SNR_after - SNR_before) with SNR = E S / sqrt(Var S) from `theory.snr` (no gate: alpha = beta = 0; gate: alpha, beta). +1 gating raises the SNR, -1 lowers it, 0 a tie within
    TIE_TOL, None undefined (an input is not finite, or a variance is not positive). The sign does not depend on m > 0 (E and Var are both proportional to m)."""
    args = (rho, alpha, beta, mu, sigma2, mu_c, sigma2_c)
    if not all(isinstance(x, (int, float, np.floating)) and math.isfinite(x) for x in args):
        return dict(sign=None, snr_before=None, snr_after=None, reason="an input is not finite (a class has fewer than 2 tokens, or no token)")
    before = theory.snr(m, rho, 0.0, 0.0, mu, sigma2, mu_c, sigma2_c)
    after = theory.snr(m, rho, alpha, beta, mu, sigma2, mu_c, sigma2_c)
    if not (math.isfinite(before) and math.isfinite(after)):
        return dict(sign=None, snr_before=None if not math.isfinite(before) else float(before), snr_after=None if not math.isfinite(after) else float(after), reason="a variance is not positive")
    diff = after - before
    s = 0 if abs(diff) <= TIE_TOL else (1 if diff > 0 else -1)
    return dict(sign=s, snr_before=float(before), snr_after=float(after), delta_snr=float(diff), reason=("tie: no sign" if s == 0 else None))


def _sign_vec(rho, a, b, mu, s2, muc, s2c, valid) -> np.ndarray:
    """Vectorised `sign_of_gating` for the bootstrap: int8 array, 2 = undefined, 0 = tie, +-1."""
    with np.errstate(all="ignore"):
        e0 = (1 - rho) * mu + rho * muc
        v0 = (1 - rho) * s2 + rho * s2c
        e1 = (1 - rho) * (1 - a) * mu + rho * (1 - b) * muc
        v1 = (1 - rho) * ((1 - a) * s2 + a * (1 - a) * mu ** 2) + rho * ((1 - b) * s2c + b * (1 - b) * muc ** 2)
        diff = e1 / np.sqrt(v1) - e0 / np.sqrt(v0)
    good = valid & (v0 > 0) & (v1 > 0) & np.isfinite(diff)
    out = np.full(diff.shape, 2, np.int8)
    out[good] = np.where(np.abs(diff[good]) <= TIE_TOL, 0, np.where(diff[good] > 0, 1, -1)).astype(np.int8)
    return out


# ------------------------------------------------------------------------------------------------ fit
def _item_stats(delta, z, flag, c0: float) -> np.ndarray:
    """Per-item sufficient statistics for the pooled class moments, with the deltas centred at c0 (numerical stability): n0, n1, s0, s1, q0, q1, f0, f1."""
    x = np.asarray(delta, np.float64) - c0
    z, f = np.asarray(z, bool), np.asarray(flag, bool)
    c, k = ~z, z
    return np.array([c.sum(), k.sum(), x[c].sum(), x[k].sum(), (x[c] ** 2).sum(), (x[k] ** 2).sum(), (f & c).sum(), (f & k).sum()], np.float64)


def _validate_cell(cell: str, toks: list, flg: list):
    if len(toks) != len(flg):
        raise ValueError(f"cell {cell}: {len(toks)} token records but {len(flg)} flag arrays (the order and number of items must match)")
    D, Z, F = [], [], []
    for i, (t, f) in enumerate(zip(toks, flg)):
        d, z, f = np.asarray(t["delta"], np.float64), np.asarray(t["z"], bool), np.asarray(f, bool)
        if not (d.shape == z.shape == f.shape and d.ndim == 1):
            raise ValueError(f"cell {cell}, item {i}: delta {d.shape}, z {z.shape}, flag {f.shape} must be the same 1-d shape")
        if not np.all(np.isfinite(d)):
            raise ValueError(f"cell {cell}, item {i}: non-finite Delta")
        D.append(d), Z.append(z), F.append(f)
    return D, Z, F


def epred_fit(headroom_tokens: dict, flags: dict, *, n_boot: int = N_BOOT, seed=None, absent: dict | None = None) -> dict:
    """SAP AD.13 `epred_fit(headroom_tokens, flags)`. headroom_tokens[cell] = list (one per headroom item, in a fixed order) of dicts with the per-token image-direction `delta` (true minus deranged
    caption) and the changed-code labels `z` (True = changed) of the CORRUPTED headroom image; flags[cell] = list of GATE-M flag arrays (bool, same length) in the same item order. Cells are
    labels of CELLS; a cell that is not in the dict is absent and counted (`absent` may carry the reason). Pooled over items at token level: rho = share with Z = 1; (mu, sigma^2) over Z = 0;
    (mu_c, sigma_c^2) over Z = 1; alpha_obs = share of Z = 0 tokens flagged; beta_obs = share of Z = 1 tokens flagged (variances with ddof = 1, as `theory.plug_in_from_deltas`).
    Returns per cell the inputs, SNR before and after, the sign s_c (+1, -1, 0 tie, None undefined) and the stability share. The stability bootstrap resamples headroom ITEMS (n_boot resamples,
    percentile-free: it only counts signs) with the seed of `prop4_plugin`; it is reported beside s_c and never changes it."""
    if set(headroom_tokens) != set(flags):
        raise ValueError(f"headroom_tokens and flags must name the same cells: {sorted(headroom_tokens)} versus {sorted(flags)}")
    bad = sorted(set(headroom_tokens) - set(CELLS))
    if bad:
        raise ValueError(f"unknown cell(s) {bad}; allowed {CELLS}")
    sd = seed if seed is not None else seeds.seed_for(SEED_NAME)
    cells, gone = {}, dict(absent or {})
    for cell in CELLS:
        if cell not in headroom_tokens or len(headroom_tokens[cell]) == 0:
            gone.setdefault(cell, "no headroom tokens or flags (cell absent)")
            continue
        D, Z, F = _validate_cell(cell, headroom_tokens[cell], flags[cell])
        d_all, z_all, f_all = np.concatenate(D), np.concatenate(Z), np.concatenate(F)
        pi = theory.plug_in_from_deltas(d_all, z_all, f_all)                    # the pooled point estimates (the audited plug-in); m = number of pooled tokens
        sg = sign_of_gating(pi["rho"], pi["alpha_obs"], pi["beta_obs"], pi["mu"], pi["sigma2"], pi["mu_c"], pi["sigma2_c"]) if all(k in pi for k in ("rho", "alpha_obs", "beta_obs", "mu", "sigma2", "mu_c", "sigma2_c")) else dict(sign=None, snr_before=None, snr_after=None, reason="no pooled estimate")
        if sg["sign"] in (1, -1) and "predicted_helps" in pi:
            assert (sg["sign"] == 1) == pi["predicted_helps"], "sign function and theory.gating_helps disagree"
        c0 = float(d_all.mean())
        st = np.stack([_item_stats(d, z, f, c0) for d, z, f in zip(D, Z, F)])
        n_items = st.shape[0]
        idx = np.random.default_rng(sd).integers(0, n_items, size=(n_boot, n_items))
        tot = st[idx].sum(axis=1)
        N0, N1, S0, S1, Q0, Q1, F0, F1 = (tot[:, i] for i in range(8))
        valid = (N0 >= 2) & (N1 >= 2)
        with np.errstate(all="ignore"):
            rho, mu, muc = N1 / (N0 + N1), c0 + S0 / N0, c0 + S1 / N1
            s2, s2c = (Q0 - S0 ** 2 / N0) / (N0 - 1), (Q1 - S1 ** 2 / N1) / (N1 - 1)
            a, b = F0 / N0, F1 / N1
        bs = _sign_vec(rho, a, b, mu, s2, muc, s2c, valid)
        pt = sg["sign"]
        stability = dict(n_boot=int(n_boot), unit="headroom items", share_defined=float((bs != 2).mean()), share_plus=float((bs == 1).mean()), share_minus=float((bs == -1).mean()),
                         share_tie=float((bs == 0).mean()), share_same_sign=(float((bs == pt).mean()) if pt in (1, -1) else None),
                         note="share of resamples whose sign equals s_c; undefined and tie resamples count as different; it never changes s_c")
        cells[cell] = dict(cell=cell, sign=pt, sign_text={1: "+", -1: "-", 0: "none (tie)"}.get(pt, "none (undefined)"), snr_before=sg["snr_before"], snr_after=sg["snr_after"], delta_snr=sg.get("delta_snr"),
                           reason_no_sign=sg.get("reason") if pt not in (1, -1) else None, n_items=int(n_items), n_tokens=int(d_all.size), n_tokens_changed=int(z_all.sum()), n_tokens_flagged=int(f_all.sum()),
                           inputs={k: pi[k] for k in ("rho", "mu", "sigma2", "mu_c", "sigma2_c", "alpha_obs", "beta_obs") if k in pi}, stability=stability)
    return dict(cells=cells, absent={c: gone.get(c, "no headroom tokens or flags (cell absent)") for c in CELLS if c not in cells}, n_boot=int(n_boot),
                s_c={c: v["sign"] for c, v in cells.items()}, method="pooled token-level point estimates over the headroom items; sign of SNR_after - SNR_before from Prop. 4 (spec v2 5.3, general form)",
                seed=dict(name=SEED_NAME, position=seeds.ANALYSES.index(SEED_NAME)), label=LABEL)




# ------------------------------------------------------------------------------------------------ reachability of the withdrawn test (used by the self-test)
def reachability(k_eval: int, alpha: float = 0.05) -> dict:
    """What the withdrawn AD.3 test (exact one-sided binomial, H0 agreement probability 0.5) could have reached: the smallest attainable p = 0.5**K at A = K. K_eval = 5 gives 0.03125,
    K_eval = 4 gives 0.0625 (cannot reject), K <= 4 never rejects. A DERIVED fact about a test that is no longer run (AB.3 item 1); it is not a result."""
    p = 0.5 ** k_eval if k_eval > 0 else 1.0
    return dict(K_eval=int(k_eval), min_attainable_p=float(p), could_reject_at_alpha=bool(p <= alpha), status="family E withdrawn by AB.3: no test is run")



# ------------------------------------------------------------------------------------------------ self-test (AD.13 and AB.3 item 5: part of the fit code, hashed with it)
def selftest(seed: int = 7) -> dict:
    """Synthetic checks that must pass before the fit is written: (1) the sign function against the closed forms of Prop. 4 (mu_c = 0 inequality; the sign is independent of m; a gate that flags
    nothing is a tie; a perfect gate on a corrupted class helps); (2) the vectorised bootstrap sign equals the scalar one; (3) a planted synthetic world with known sign is recovered by `epred_fit`;
    (4) the stability share is deterministic given the seed; (5) reachability: K_eval = 5 can reject at 0.05, K <= 4 never."""
    rng = np.random.default_rng(seed)
    ok = {}
    cases = [(0.2, 0.05, 0.6, 0.15, 0.4, 0.0, 0.5), (0.05, 0.10, 0.1, 0.2, 0.3, 0.0, 0.6), (0.3, 0.02, 0.9, 0.1, 0.2, -0.1, 0.8), (0.1, 0.2, 0.2, 0.3, 0.5, 0.1, 0.2)]
    agree = []
    for rho, a, b, mu, s2, muc, s2c in cases:
        s1, s2_ = sign_of_gating(rho, a, b, mu, s2, muc, s2c, m=1), sign_of_gating(rho, a, b, mu, s2, muc, s2c, m=1024)
        agree.append(s1["sign"] == s2_["sign"])
        if muc == 0.0:
            closed = rho * s2c * (b - 2 * a + a * a) > a * (1 - a) * (1 - rho) * (s2 + mu ** 2)
            agree.append((s1["sign"] == 1) == closed)
    ok["sign_matches_closed_form_and_is_m_free"] = bool(all(agree))
    ok["no_flags_is_a_tie"] = bool(sign_of_gating(0.2, 0.0, 0.0, 0.1, 0.3, 0.0, 0.4)["sign"] == 0)
    ok["perfect_gate_helps_when_corrupted_class_is_noisy"] = bool(sign_of_gating(0.2, 0.0, 1.0, 0.2, 0.3, 0.0, 2.0)["sign"] == 1)
    ok["nonfinite_input_has_no_sign"] = bool(sign_of_gating(0.2, 0.0, 1.0, 0.2, 0.3, float("nan"), 2.0)["sign"] is None)
    # (2) vector == scalar
    n = 50
    v = [rng.uniform(0.05, 0.4, n), rng.uniform(0, 0.2, n), rng.uniform(0.1, 0.9, n), rng.normal(0.2, 0.1, n), rng.uniform(0.1, 0.5, n), rng.normal(0, 0.1, n), rng.uniform(0.1, 1.0, n)]
    vec = _sign_vec(*v, valid=np.ones(n, bool))
    sca = np.array([sign_of_gating(*(float(x[i]) for x in v))["sign"] for i in range(n)])
    ok["vector_sign_equals_scalar_sign"] = bool(np.array_equal(vec, sca))
    # (3) planted world: corrupted tokens are pure noise (mean 0, sd 3) in 15 percent of positions; the gate flags 70 percent of them and 3 percent of clean ones -> gating helps (+)
    def world(helps: bool, n_items=40, m=256):
        toks, fl = [], []
        for _ in range(n_items):
            z = rng.random(m) < 0.15
            d = np.where(z, rng.normal(0.0, 3.0, m), rng.normal(0.3, 0.5, m))
            f = (z & (rng.random(m) < (0.7 if helps else 0.0))) | (~z & (rng.random(m) < (0.03 if helps else 0.30)))
            toks.append(dict(delta=d, z=z)), fl.append(f)
        return toks, fl
    th, fh = world(True)
    tl, fl_ = world(False)
    fit = epred_fit({"P1": th, "P2": tl}, {"P1": fh, "P2": fl_}, n_boot=300, seed=np.random.SeedSequence(5))
    ok["planted_helpful_gate_gets_plus"] = bool(fit["cells"]["P1"]["sign"] == 1 and (fit["cells"]["P1"]["stability"]["share_same_sign"] or 0) > 0.9)
    ok["planted_harmful_gate_gets_minus"] = bool(fit["cells"]["P2"]["sign"] == -1 and (fit["cells"]["P2"]["stability"]["share_same_sign"] or 0) > 0.9)
    ok["absent_cells_are_counted"] = bool(set(fit["absent"]) == {"P3", "PS1", "PS2"})
    fit2 = epred_fit({"P1": th}, {"P1": fh}, n_boot=300, seed=np.random.SeedSequence(5))
    ok["stability_is_deterministic"] = bool(fit2["cells"]["P1"]["stability"] == fit["cells"]["P1"]["stability"])
    r5, r4 = reachability(5), reachability(4)
    ok["reachability_K5_can_reject_K4_cannot"] = bool(r5["could_reject_at_alpha"] and abs(r5["min_attainable_p"] - 0.03125) < 1e-12 and not r4["could_reject_at_alpha"] and abs(r4["min_attainable_p"] - 0.0625) < 1e-12
                                                      and not any(reachability(k)["could_reject_at_alpha"] for k in range(0, 5)))
    ok["all_ok"] = bool(all(ok.values()))
    return ok

