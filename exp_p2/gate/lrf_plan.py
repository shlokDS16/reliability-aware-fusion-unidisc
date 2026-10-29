"""A6.11 item 3 plan files (audit F5): writes the two `family.json` files that `run_gate_m4 --family-run` reads for Study 2, from committed inputs only. CPU, no model.

    python -m exp_p2.gate.lrf_plan [--n-rule runs/P2-LRF-PLAN/n_rule.json] [--m3-family runs/P2-GATE-M3/family.json]

  runs/P2-LRF-PLAN/family.json     L1: endpoint "d", the family of the committed M3 decision (it must be P's three operating points jpeg 10, noise 0.1, splice 128, in that order), `n_rule.test_fold` = n_L read from the
                                   n-rule record (lrf_nrule.py output, 400 <= n_L <= 533), so `run_gate_m4`'s n check passes only for --n n_L
  runs/P2-LRF-PLAN-LG/family.json  LG: endpoint "d", an EMPTY family (the LG stage holds clean + the extra cells only), `n_rule.test_fold` 300
Both refuse to overwrite. Each records the SHA-256 of its inputs. `check_consistent` verifies that n_L agrees between the n-rule record, the plan file (and with it `a6_analysis --n-rule`, which reads the same record's `n_L`)."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402

PLAN_RUN, PLAN_LG_RUN = "P2-LRF-PLAN", "P2-LRF-PLAN-LG"
P_OPERATING_POINTS = [("jpeg", 10), ("noise", 0.1), ("splice", 128)]      # family P, in the order of config.LADDERS
N_MIN, N_MAX, LG_N = 400, 533, 300


def _sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def plan_files(n_rule_path: Path, m3_family_path: Path) -> tuple[dict, dict]:
    n_rec = json.loads(Path(n_rule_path).read_text(encoding="utf8"))
    n_l = int(n_rec["n_L"])
    if not (N_MIN <= n_l <= N_MAX or n_l == 520):
        raise ValueError(f"n_L {n_l} outside [{N_MIN}, {N_MAX}] (and not the fallback 520)")
    m3 = json.loads(Path(m3_family_path).read_text(encoding="utf8"))
    if m3.get("endpoint") != "d":
        raise ValueError(f"{m3_family_path} does not record endpoint d")
    fam = [(f["corruption"], f["severity"]) for f in m3["family"]]
    if fam != P_OPERATING_POINTS:
        raise ValueError(f"{m3_family_path} family {fam} is not P's three operating points {P_OPERATING_POINTS}")
    src = dict(n_rule_record=str(Path(n_rule_path).as_posix()), n_rule_record_sha256=_sha(n_rule_path), m3_family=str(Path(m3_family_path).as_posix()), m3_family_sha256=_sha(m3_family_path))
    l1 = dict(endpoint="d", n_rule=dict(rule="SAP A6 r1 A6.3 n-rule (exp_p2/gate/lrf_nrule.py)", test_fold=n_l), family=m3["family"], sources=src, spec="exp_p2/gate/lrf_plan.py")
    lg = dict(endpoint="d", n_rule=dict(rule="SAP A6 r1 A6.5: the first 300 items", test_fold=LG_N), family=[], sources=src, spec="exp_p2/gate/lrf_plan.py")
    return l1, lg


def check_consistent(runs: Path, n_rule_path: Path | None = None) -> dict:
    """n_L of the n-rule record, of runs/P2-LRF-PLAN/family.json and (what the driver reads) of default_n; raises ValueError on any difference."""
    runs = Path(runs)
    n_rule_path = Path(n_rule_path) if n_rule_path else runs / PLAN_RUN / "n_rule.json"
    n_rec = int(json.loads(n_rule_path.read_text(encoding="utf8"))["n_L"])
    n_plan = int(json.loads((runs / PLAN_RUN / "family.json").read_text(encoding="utf8"))["n_rule"]["test_fold"])
    n_lg = int(json.loads((runs / PLAN_LG_RUN / "family.json").read_text(encoding="utf8"))["n_rule"]["test_fold"])
    if not (n_rec == n_plan) or n_lg != LG_N:
        raise ValueError(f"inconsistent n: n-rule record {n_rec}, plan {n_plan}, LG plan {n_lg} (expected {LG_N})")
    return dict(n_L=n_rec, lg_n=n_lg)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    runs = Path(common.RUNS)
    ap.add_argument("--n-rule", default=str(runs / PLAN_RUN / "n_rule.json"))
    ap.add_argument("--m3-family", default=str(runs / "P2-GATE-M3" / "family.json"))
    a = ap.parse_args(argv)
    targets = [runs / PLAN_RUN / "family.json", runs / PLAN_LG_RUN / "family.json"]
    if any(t.exists() for t in targets):
        print(f"STOP: {[str(t) for t in targets if t.exists()]} exist; not overwriting", file=sys.stderr)
        return 2
    try:
        l1, lg = plan_files(Path(a.n_rule), Path(a.m3_family))
    except (OSError, ValueError, KeyError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    for t, doc in zip(targets, (l1, lg)):
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(json.dumps(doc, indent=1, sort_keys=True), encoding="utf8")
    print(json.dumps(dict(plan=str(targets[0]), plan_lg=str(targets[1]), n_L=l1["n_rule"]["test_fold"], sha256=[_sha(t) for t in targets])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
