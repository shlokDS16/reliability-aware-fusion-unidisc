"""SAP addendum A7.4 analysis (Flickr30K transfer test of the frozen LRF): reads ONLY the predictions file written by exp_p2/gate/lrf_score.py and writes f30k_analysis.json. CPU, numpy + stdlib.

    python -m exp_p2.gate.lrf_score --run-id P2-LRF-F30K --pins runs/P2-LRF-PINS/pins.json --conds clean,noise0.1
    python -m analysis.paper2.lrf.f30k_analysis [--run runs/P2-LRF-F30K] [--out runs/P2-LRF-F30K/f30k_analysis.json]

Three hypotheses, each its own family at its own level, no adjustment across families (A7.4):
  F1     (primary) LRF (`y_lrf`) against the unweighted sum (`y_none`) on `noise0.1`, exact ONE-sided McNemar, H1: b > c, alpha 0.05. "confirmed" iff p <= 0.05 and b > c, else "not confirmed".
         A gain claim in the title or abstract needs p <= 0.025 (`headline_gain_claim_allowed`, as C6-5).
  F-NI   non-inferiority on `clean`, margin -0.03: `non_inferior` is true iff the lower bound of the 90 percent paired percentile bootstrap interval of the net accuracy change (LRF minus NONE) exceeds -0.03.
  F-LEN  (secondary) F1 repeated with the length-matched wrong captions (`y_lrf_L`, `y_none_L`), items whose length-matched caption differs in token count (`neg_len_exact` false) excluded and counted; exact one-sided McNemar at 0.05.
Every block reports n, b, c, net change (b - c) / n, both accuracies, the 90 and 95 percent paired percentile bootstrap intervals (10,000 resamples of items; a fresh numpy.random.SeedSequence(0) generator per block) and the
exact one- and two-sided p, with the McNemar, Clopper-Pearson and bootstrap code of analysis/paper2/lrf/a6_analysis.py imported unchanged. Also reported, descriptive: the accuracy of both rules in both conditions and
the gain on clean images. A7.6: fewer than 800 scored items -> `underpowered (n of 1,000)`, the result is still reported and no headline gain claim is allowed. Complete case: noise0.1 and clean must hold the same items."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.paper2.lrf import a6_analysis as A6                                     # noqa: E402

ALPHA, HEADLINE_ALPHA, NI_MARGIN = 0.05, 0.025, 0.03
N_TEST_SPLIT, MIN_SCORED = 1000, 800
N_BOOT = A6.N_BOOT
BOOT_SEED = 0
CONDS = ("clean", "noise0.1")
SPEC = "research/paper2/prereg/SAP-ADDENDUM-A7-F30K-2026-10-31.md A7.4"


def boot_rng() -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence(BOOT_SEED))


def paired_block(y_lrf, y_none) -> dict:
    """The block of A7.4 for LRF (first arm) against the unweighted sum: counts, accuracies, net change, exact p (one- and two-sided), 90 and 95 percent paired percentile bootstrap intervals."""
    a, b_ = np.asarray(y_lrf, float), np.asarray(y_none, float)
    n = len(a)
    b, c = A6.mcnemar_counts(a, b_)
    p = A6.mcnemar_p(b, c)
    diff = a - b_
    ci = A6.boot_ci(diff, boot_rng(), levels=(0.90, 0.95), n_boot=N_BOOT)
    return dict(n=n, b=b, c=c, n_d=b + c, acc_lrf=float(a.mean()) if n else None, acc_none=float(b_.mean()) if n else None, net=float(diff.mean()) if n else None,
                p_one=p["p_one"], p_two=p["p_two"], p_mid_one=p["p_mid_one"], cp95_b_over_nd=A6.clopper_pearson(b, b + c), **ci)


def by_condition(lines: list[dict]) -> dict[str, dict[int, dict]]:
    out: dict[str, dict[int, dict]] = {}
    for l in lines:
        rows = out.setdefault(l["condition"], {})
        if int(l["idx"]) in rows:
            raise RuntimeError(f"duplicate row for condition {l['condition']} idx {l['idx']}")
        rows[int(l["idx"])] = l
    return out


def check_meta(run: Path) -> dict:
    """The scorer's own record: the two planned conditions, no skipped item or condition, its positive control passed, input hashes recorded."""
    meta = json.loads((Path(run) / "lrf_score_meta.json").read_text(encoding="utf8"))
    bad = []
    if meta.get("conds") != list(CONDS):
        bad.append(f"scorer conds {meta.get('conds')} != {list(CONDS)}")
    if meta.get("conds_absent_in_rows") or meta.get("n_items_skipped_no_arrays"):
        bad.append("scorer skipped conditions or items")
    if not (meta.get("positive_control") or {}).get("ok"):
        bad.append("scorer positive control not ok")
    if not meta.get("hashes"):
        bad.append("scorer recorded no input hashes (run it with --pins runs/P2-LRF-PINS/pins.json)")
    if bad:
        raise RuntimeError("; ".join(bad))
    return dict(ok=True, n_items_rows=meta.get("n_items_rows"), predictions_sha256=meta.get("predictions_sha256"))


def analyse(run: Path, need_meta: bool = True) -> dict:
    run = Path(run)
    lines = A6.load_predictions(run / "predictions.jsonl")
    by = by_condition(lines)
    for c in CONDS:
        if c not in by:
            raise RuntimeError(f"no prediction rows for condition {c}")
    ids = sorted(by["noise0.1"])
    if sorted(by["clean"]) != ids:
        raise RuntimeError(f"clean ({len(by['clean'])} rows) and noise0.1 ({len(ids)} rows) hold different items")
    for i in ids:
        if (by["clean"][i]["gid"], by["clean"][i]["image_id"]) != (by["noise0.1"][i]["gid"], by["noise0.1"][i]["image_id"]):
            raise RuntimeError(f"idx {i}: gid or image_id differ between conditions")
    n = len(ids)
    underpowered = n < MIN_SCORED
    under_label = f"underpowered ({n} of {N_TEST_SPLIT:,})" if underpowered else None
    # audit F2: a run stopped before the planned fold size is flagged, whatever n is (planned n from the committed family file)
    fam = Path(run).parent / "P2-LRF-PLAN-F30K" / "family.json"
    n_planned = int(json.loads(fam.read_text(encoding="utf-8"))["n_rule"]["test_fold"]) if fam.exists() else None
    complete = None if n_planned is None else (n == n_planned)                          # None: no committed plan file next to the run (synthetic tests only)
    partial_label = f"partial ({n} of {n_planned})" if complete is False else None
    if partial_label:
        under_label = "; ".join(x for x in (under_label, partial_label) if x)
    nz, cl = [by["noise0.1"][i] for i in ids], [by["clean"][i] for i in ids]
    col = lambda rows, k: np.array([int(r[k]) for r in rows])                         # noqa: E731

    f1 = paired_block(col(nz, "y_lrf"), col(nz, "y_none"))
    f1["rejected"] = bool(f1["p_one"] <= ALPHA and f1["b"] > f1["c"])
    f1.update(sided="one", alpha=ALPHA, condition="noise0.1", confirmed=f1["rejected"], label=("confirmed" if f1["rejected"] else "not confirmed"),
              headline_gain_claim_allowed=bool(f1["rejected"] and f1["p_one"] <= HEADLINE_ALPHA and not underpowered), headline_alpha=HEADLINE_ALPHA)
    if under_label:
        f1["label"] = f"{f1['label']}; {under_label}"
        f1["headline_gain_claim_allowed"] = False
    d, ci = f1["net"], f1["ci95"]
    f1["wording"] = ("On a second dataset, the frozen weighting, unchanged, raised accuracy under Gaussian noise (preregistered one-sided test)" if f1["rejected"]
                     else f"On a second dataset the frozen weighting did not confirm (net {d:+.3f}, 95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}], one-sided p = {f1['p_one']:.3g})")
    if under_label:                                                                     # audit F3: the qualifier travels with the wording
        f1["wording"] += f" [{under_label}]"

    ni = paired_block(col(cl, "y_lrf"), col(cl, "y_none"))
    lo90 = ni["ci90"][0]
    ni.update(condition="clean", margin=-NI_MARGIN, lower90=lo90, non_inferior=bool(lo90 is not None and lo90 > -NI_MARGIN), label=("non-inferior" if (lo90 is not None and lo90 > -NI_MARGIN) else "not shown"),
              note="lower bound of the 90% paired percentile bootstrap interval of the net accuracy change (LRF minus NONE) must exceed -0.03")

    have_L = [r for r in nz if r.get("y_lrf_L") is not None and r.get("y_none_L") is not None]
    if have_L:
        keep = [r for r in have_L if r.get("neg_len_exact")]
        ln = paired_block(col(keep, "y_lrf_L"), col(keep, "y_none_L"))
        ln["rejected"] = bool(ln["p_one"] <= ALPHA and ln["b"] > ln["c"])
        ln.update(sided="one", alpha=ALPHA, condition="noise0.1", n_with_length_matched_negative=len(have_L), n_excluded_length_mismatch=len(have_L) - len(keep),
                  n_without_length_matched_score=len(nz) - len(have_L), confirmed=ln["rejected"],                # audit F4
                  label=("confirmed" if ln["rejected"] else "not confirmed"))
        if under_label:
            ln["label"] = f"{ln['label']}; {under_label}"
    else:
        ln = dict(status="not run", label="not run: no length-matched scores in the predictions")

    desc = {c: dict(n=n, acc_none=float(col(rows, "y_none").mean()), acc_lrf=float(col(rows, "y_lrf").mean())) for c, rows in (("clean", cl), ("noise0.1", nz))}
    desc["gain_on_clean"] = ni["net"]
    desc["gain_on_noise0.1"] = f1["net"]
    desc["descriptive_only"] = True
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()                    # noqa: E731
    res = dict(label="preregistered confirmatory test (SAP addendum A7); three separate families, no adjustment across families", spec=SPEC, run=str(run.name), n_scored=n, n_test_split=N_TEST_SPLIT,
               underpowered=underpowered, underpowered_label=under_label, min_scored=MIN_SCORED, n_planned=n_planned, complete=complete,
               definitions="NONE = y_none (unweighted sum of per-token evidence), LRF = y_lrf (frozen weights, unchanged); b = LRF right and NONE wrong, c = LRF wrong and NONE right; net = (b - c) / n; positive favours LRF",
               bootstrap=dict(n_boot=N_BOOT, seed="a fresh numpy.random.SeedSequence(0) generator per block", interval="percentile, numpy.quantile at (1-level)/2 and 1-(1-level)/2", unit="items", code="analysis/paper2/lrf/a6_analysis.py boot_ci"),
               F1=f1, F_NI=ni, F_LEN=ln, descriptive=desc, inputs=dict(predictions_sha256=sha(run / "predictions.jsonl"), numpy=np.__version__))
    if need_meta:
        res["scorer_meta"] = check_meta(run)
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=str(ROOT / "runs" / "P2-LRF-F30K"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    out = Path(a.out) if a.out else Path(a.run) / "f30k_analysis.json"
    try:
        res = analyse(Path(a.run))
    except (RuntimeError, FileNotFoundError, KeyError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf-8")
    f1, ni, ln = res["F1"], res["F_NI"], res["F_LEN"]
    print(json.dumps(dict(out=str(out), n_scored=res["n_scored"], F1=dict(label=f1["label"], net=f1["net"], b=f1["b"], c=f1["c"], p_one=f1["p_one"], ci95=f1["ci95"]),
                          F_NI=dict(non_inferior=ni["non_inferior"], lower90=ni["lower90"]), F_LEN=dict(label=ln.get("label"), p_one=ln.get("p_one")))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
