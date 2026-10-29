"""A6 r1 A6.3 n-rule (pre-written, outcome-blind): n_L is a PREFIX of the 533-item fold, chosen from the cross-fitted noise0.1 result of the L_FIX protocol. CPU, scipy only.

    python -m exp_p2.gate.lrf_nrule --delta-cf 0.10 --pi-cf 0.24 [--out runs/P2-LRF-PLAN/n_rule.json]
    python -m exp_p2.gate.lrf_nrule --cf-results runs/P2-LRF-CF-LFIX/results.json ...      # not implemented: the cross-fit output format does not exist yet; pass --delta-cf and --pi-cf = (b + c) / 500 by hand
    python -m exp_p2.gate.lrf_nrule --not-committed                                       # the cross-fit was not committed by Mon 2 Nov 10:00 IST: n_L = 520

Rule: Delta_plan = Delta_cf / 2. If Delta_cf <= 0.02: n_L = 533. Otherwise n_req = the smallest n on a step-10 grid with exact one-sided McNemar power >= 0.8 at alpha 0.05 for (pi_cf, Delta_plan); n_L = min(533, max(400, n_req)).
Power model (Appendix A6): n_d ~ Bin(n, pi), b | n_d ~ Bin(n_d, theta), theta = 0.5 + Delta / (2 pi); rejection iff the exact one-sided p = P(Bin(n_d, 0.5) >= b) <= alpha. The output record carries the inputs, n_req, n_L and the power
at one-sided 0.05 and 0.025 for Delta_plan, and is committed before the first L item."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

N_CAP, N_MIN, N_FALLBACK, GRID_STEP = 533, 400, 520, 10
DELTA_FLOOR, POWER_TARGET, ALPHA = 0.02, 0.8, 0.05


def power(n: int, pi_d: float, delta: float, alpha: float = ALPHA) -> float:
    """Exact one-sided McNemar power under the Appendix A6 model."""
    import numpy as np
    from scipy.stats import binom
    theta = 0.5 + delta / (2.0 * pi_d)
    if not 0.0 < theta < 1.0:
        raise ValueError(f"theta {theta} outside (0, 1): Delta {delta} is not compatible with pi {pi_d}")
    nd = np.arange(0, n + 1)
    w = binom.pmf(nd, n, pi_d)
    crit = binom.isf(alpha, nd, 0.5) + 1                               # smallest b with P(Bin(n_d, .5) >= b) <= alpha
    return float(np.sum(w * binom.sf(crit - 1, nd, theta)))            # zero where crit > n_d


def n_rule(delta_cf: float, pi_cf: float) -> dict:
    out = dict(delta_cf=float(delta_cf), pi_cf=float(pi_cf), rule="n_L = 533 if Delta_cf <= 0.02 else min(533, max(400, smallest n on a step-10 grid with one-sided exact power >= 0.8 at 0.05 for Delta_cf / 2))")
    if delta_cf <= DELTA_FLOOR:
        out.update(delta_plan=None, n_req=None, n_L=N_CAP, reason="Delta_cf <= 0.02: the cap")
    else:
        dp = delta_cf / 2.0
        n_req = next((n for n in range(GRID_STEP, 3001, GRID_STEP) if power(n, pi_cf, dp) >= POWER_TARGET), None)
        out.update(delta_plan=dp, n_req=n_req, n_L=int(min(N_CAP, max(N_MIN, n_req if n_req is not None else N_CAP))), reason="power rule")
    dp = out["delta_plan"] if out["delta_plan"] is not None else delta_cf / 2.0
    try:
        out["power_at_n_L"] = {"one_sided_0.05": power(out["n_L"], pi_cf, dp, 0.05), "one_sided_0.025": power(out["n_L"], pi_cf, dp, 0.025), "delta_used": dp}
    except ValueError as e:
        out["power_at_n_L"] = f"not computable: {e}"
    return out


def fallback_record() -> dict:
    return dict(n_L=N_FALLBACK, reason="cross-fit not committed by Mon 2 Nov 10:00 IST: the rule's fallback", delta_cf=None, pi_cf=None, delta_plan=None, n_req=None)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta-cf", type=float, default=None, help="cross-fitted noise0.1 net difference (SEL minus NONE) of the L_FIX protocol")
    ap.add_argument("--pi-cf", type=float, default=None, help="cross-fitted discordance rate (b + c) / 500")
    ap.add_argument("--not-committed", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.not_committed:
        rec = fallback_record()
    elif a.delta_cf is not None and a.pi_cf is not None and 0 < a.pi_cf <= 1:
        rec = n_rule(a.delta_cf, a.pi_cf)
    else:
        ap.error("give --delta-cf and --pi-cf (0 < pi <= 1), or --not-committed")
    if a.out:
        out = Path(a.out)
        if out.exists():
            print(f"{out} exists; not overwriting", file=sys.stderr)
            return 2
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rec, indent=1, sort_keys=True), encoding="utf8")
    print(json.dumps(rec, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
