"""Headroom check (v2 section 7.3, Alg. 9) and the pre-registered endpoint decision (section 9). CPU only; reads runs/P2-GATE-M3/items.jsonl.

    python -m exp_p2.gate.headroom --run-id P2-GATE-M3 [--endpoint z|d] [--out family.json]

For each realistic corruption walk its ladder in order and stop at the first rung where BOTH hold on the continuous endpoint (default: the spec's z-score):
  H1  clean minus corrupted-none      >= 2 paired SE   (there is a drop)
  H2  changed-code-gate minus none    >= 2 paired SE   (removing the changed codes recovers some of it)
GATE's own flags are never used here (the decision is blind to the method). Items with a non-finite endpoint on either side are dropped per test and counted.
NOTE on the endpoint: the spec's z_R scales with sqrt(|R|), so H2 (which shrinks R) is biased against passing; the size-invariant effect size d = mean/sd is reported
alongside. The default stays the spec's z; the choice is recorded in family.json and may be changed to d only BEFORE any test item is scored.
The output family.json must be committed before the first M4 item is scored."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import config, corruptions, stats                          # noqa: E402

THETA_REF, N_TEST_SCALE = 0.75, config.N_TEST


def _col(rows, getter):
    return np.array([getter(r) for r in rows], float)


def evaluate_rung(rows: list[dict], key: str, endpoint: str = "z", min_se_mult: float = 2.0) -> dict:
    clean = _col(rows, lambda r: r["clean"][endpoint])
    none = _col(rows, lambda r: r["rungs"][key]["none"][endpoint])
    chg = _col(rows, lambda r: r["rungs"][key]["chg"][endpoint])
    h1, h2 = stats.paired_diff(clean, none), stats.paired_diff(chg, none)
    p1 = bool(h1["n"] >= 2 and h1["se"] > 0 and h1["diff"] >= min_se_mult * h1["se"])
    p2 = bool(h2["n"] >= 2 and h2["se"] > 0 and h2["diff"] >= min_se_mult * h2["se"])
    y_none = _col(rows, lambda r: r["rungs"][key]["none"]["y"])
    y_chg = _col(rows, lambda r: r["rungs"][key]["chg"]["y"])
    mc = stats.mcnemar_exact(y_chg, y_none)
    n_changed = _col(rows, lambda r: r["rungs"][key]["n_changed"])
    return dict(key=key, H1=h1, H2=h2, H1_pass=p1, H2_pass=p2, passes=p1 and p2, discordance_chg_vs_none=mc,
                mean_n_changed=float(np.mean(n_changed)))


def decide(rows: list[dict], endpoint: str = "z", theta: float = THETA_REF, n_test: int = N_TEST_SCALE) -> dict:
    """family.json content. `rows` are M3 item rows."""
    family, excluded, rungs = [], [], {}
    for corr in config.REALISTIC:
        chosen = None
        for sev in config.LADDERS[corr]:
            key = corruptions.corruption_key(corr, sev)
            ev = evaluate_rung(rows, key, endpoint)
            rungs[key] = ev
            if ev["passes"] and chosen is None:
                chosen = (sev, ev)
        if chosen:
            family.append(dict(corruption=corr, severity=chosen[0], key=corruptions.corruption_key(corr, chosen[0])))
        else:
            excluded.append(dict(corruption=corr, reason="failed H1 and H2 on every rung of its ladder", rungs=[corruptions.corruption_key(corr, s) for s in config.LADDERS[corr]]))
    scale = n_test / len(rows)
    holm_alpha = 0.05 / max(1, len(family))
    need = stats.power_nd(theta, holm_alpha)
    decisions = []
    for f in family:
        mc = rungs[f["key"]]["discordance_chg_vs_none"]
        scaled = mc["n_discordant"] * scale
        decisions.append(dict(key=f["key"], discordant_headroom=mc["n_discordant"], b=mc["b"], c=mc["c"], scaled_to_test=scaled, n_d_required=need,
                              enough=bool(scaled >= need)))
    action = ("keep McNemar on the image-direction accuracy as the primary endpoint" if decisions and all(d["enough"] for d in decisions) else
              "no family member" if not decisions else
              "UNDER-POWERED for at least one member: raise the test fold to 500 items or make the z-score endpoint primary; record the choice BEFORE any test item is scored")
    return dict(endpoint=endpoint, n_headroom_items=len(rows), family=family, excluded=excluded, rungs=rungs,
                endpoint_decision=dict(theta=theta, holm_alpha_prime=holm_alpha, n_test=n_test, per_member=decisions, action=action),
                downstream_claim_withdrawn=not family,
                spec="GATE-METHOD-SPEC-v2 sections 7.3, 9, Alg. 9")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="P2-GATE-M3")
    ap.add_argument("--endpoint", choices=["z", "d"], default="z")
    ap.add_argument("--out", default="family.json")
    a = ap.parse_args(argv)
    run = Path(common.RUNS) / a.run_id
    rows = common.read_jsonl(run / "items.jsonl")
    if len(rows) < 20:
        print(f"only {len(rows)} headroom items in {run}; the rule needs the full 100", file=sys.stderr)
        return 2
    res = decide(rows, a.endpoint)
    (run / a.out).write_text(json.dumps(res, indent=1), encoding="utf8")
    print(json.dumps(dict(family=res["family"], excluded=[e["corruption"] for e in res["excluded"]], action=res["endpoint_decision"]["action"]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
