"""C1: clean-image recovery check (SAP Addendum 2 A2.3). Descriptive pipeline check; it tests nothing and carries no alpha.

The statistic is the clean-pair NONE-arm accuracy of the image direction (all tokens, deranged negative), the same statistic as probe-1 b_full: 253 of 300 = 0.8433, Wilson 95 percent
CI 0.798 to 0.880 (SAP Appendix A.1). The audit trigger is that the new Wilson interval does NOT overlap 0.798-0.880; the action is a pipeline audit against the unit tests (L1-L10,
tokenizer, VQ encode, layout) and nothing else: no rule, score, K, alpha, fold, rung or arm changes, and a defect gives an amended rerun beside the original. Three looks, none
pooled: (i) the clean calibration items right after M2, (ii) the clean headroom items after M3, (iii) the clean test items at the analysis step after the planned fold is complete.

    python -m exp_p2.gate.c1 --look cal   [--run-id P2-GATE-M2]
    python -m exp_p2.gate.c1 --look head  [--run-id P2-GATE-M3]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import stats                                               # noqa: E402

PROBE1_K, PROBE1_N = 253, 300                    # SAP Appendix A.1, probe-1 b_full on 300 clean pairs
PROBE1_CI = (0.798, 0.880)                       # Wilson 95 percent interval of 253/300 as printed in the SAP
LOOKS = {"cal": ("P2-GATE-M2", "calibration"), "head": ("P2-GATE-M3", "headroom"), "test": ("P2-GATE-M4", "test")}


def c1(ys, look: str = "") -> dict:
    """ys: 0/1 clean none-arm outcomes (NaN dropped). Returns the numbers, the audit trigger and the sentence that may be printed (nothing stronger)."""
    ys = [float(y) for y in ys if y == y]
    n, k = len(ys), int(sum(ys))
    lo, hi = stats.wilson_ci(k, n)
    overlap = bool(n and lo <= PROBE1_CI[1] and hi >= PROBE1_CI[0])
    return dict(look=look, n=n, k=k, accuracy=(k / n if n else float("nan")), wilson95=[lo, hi], probe1=dict(k=PROBE1_K, n=PROBE1_N, accuracy=PROBE1_K / PROBE1_N, wilson95=list(PROBE1_CI)),
                overlaps_probe1_interval=overlap, audit_trigger=bool(n and not overlap),
                above_interval=bool(n and lo > PROBE1_CI[1]),
                sentence=(f"the clean none-arm accuracy was {k / n:.3f} (95 percent CI {lo:.3f} to {hi:.3f}), against 0.843 (0.798 to 0.880) in probe 1" if n else "no items"),
                rule="descriptive; trigger = Wilson interval does not overlap 0.798-0.880; action = pipeline audit only, nothing is tuned (SAP A2.3)")


def ys_from_rows(rows: list[dict], look: str) -> list[float]:
    if look == "cal":
        return [r["img"]["y"] for r in rows]
    if look == "head":
        return [r["clean"]["y"] for r in rows]
    if look == "test":
        return [r["conds"]["clean"]["img"]["none"]["y"] for r in rows if "clean" in r["conds"]]
    raise ValueError(look)


def expected_test_n(runs: Path | None = None) -> int:
    """Items the M4 test fold must contain before look (iii) may be read: the n-rule's test fold (family.json; 300 if absent) minus the items excluded by the real-tokenizer rule."""
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    want = 300
    fj = runs / "P2-GATE-M3" / "family.json"
    if fj.exists():
        want = int(json.loads(fj.read_text(encoding="utf8")).get("n_rule", {}).get("test_fold", 300))
    eff = runs / "P2-GATE-M4" / "effective_n.json"
    if eff.exists():
        want = min(want, int(json.loads(eff.read_text(encoding="utf8"))["effective"]))
    return want


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--look", choices=sorted(LOOKS), required=True)
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args(argv)
    rid = a.run_id or LOOKS[a.look][0]
    run = Path(common.RUNS) / rid
    rows = common.read_jsonl(run / "items.jsonl")
    if a.look == "test":                                           # look (iii) only at the analysis step after the planned fold is complete (SAP 8.2, A2.3)
        done, want = len({r["idx"] for r in rows}), expected_test_n()
        if done < want:
            print(f"STOP: the M4 test fold is not complete ({done} of {want} items); look (iii) is read only after the planned fold is complete (SAP 8.2)", file=sys.stderr)
            return 2
    res = c1(ys_from_rows(rows, a.look), LOOKS[a.look][1])
    out = run / f"c1_{a.look}.json"
    if out.exists():
        print(f"{out} exists: each look is recorded once", file=sys.stderr)
        return 2
    out.write_text(json.dumps(res, indent=1), encoding="utf8")
    print(res["sentence"] + ("   AUDIT TRIGGER: the interval does not overlap probe 1's; run the pipeline audit (nothing is tuned)" if res["audit_trigger"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
