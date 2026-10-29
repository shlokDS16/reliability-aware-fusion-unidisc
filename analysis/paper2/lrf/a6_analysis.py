"""SAP addendum A6 analysis (A6.4 to A6.9, A6.12 labels): reads ONLY the predictions files written by exp_p2/gate/lrf_score.py and writes a6_analysis.json. CPU, numpy + stdlib (+ scipy for the Clopper-Pearson interval).

    python -m analysis.paper2.lrf.a6_analysis --l1 runs/P2-LRF-L1/predictions.jsonl [--lg runs/P2-LRF-LG/predictions.jsonl] [--out runs/P2-LRF-L1/a6_analysis.json]
    python -m analysis.paper2.lrf.a6_analysis --selftest

Tests (item = the unit; complete case: an item enters a test only if both arms of the test have a prediction for it):
  L1     LRF vs NONE on noise0.1, exact ONE-sided McNemar, alpha 0.05, confirmed iff p <= 0.05 and b > c (also reported: passes one-sided 0.025 = "would also pass a two-sided 0.05 test")
  L2     LRF vs GATE-M on noise0.1, one-sided exact, alpha 0.05, only if L1 is confirmed (fixed sequence)
  L3,L4  LRF vs NONE on jpeg10 and splice128, exact TWO-sided, Holm over m = 2 at 0.05, only if L2 is rejected with b > c
  L-NI   clean, LRF minus NONE, non-inferiority margin 0.03: shown iff the lower bound of the two-sided 90 percent paired percentile bootstrap CI exceeds -0.03 (always computed)
  L-LEN  noise0.1 with the length-matched negative (y_*_L), LRF vs NONE, one-sided exact, alpha 0.05, items whose c-_L differs in token count excluded and counted (always computed)
  LG     held-out noise cells (shot, impulse, speckle at severity 3), LRF vs NONE per cell, one-sided exact, Holm over the PREREGISTERED m = 3 (an absent cell enters as p = 1), first 300 items; completed n < 240: descriptive only
A not-reached test is "not tested (gatekept)" and is still printed descriptively. Descriptive additions: GATE-M vs NONE per LG cell, the clean-to-corrupted drop of NONE per cell, and the preregistered length-stratum secondary (LRF-FROZEN report
section 3 item 5: LRF minus NONE on noise0.1 by true caption shorter / equal / longer than the negative, and the longer-minus-shorter difference with a 95 percent CI).
Every test reports b, c, n_d, n, both accuracies, the net difference with paired percentile bootstrap CIs at 90 and 95 percent (10,000 resamples), the Clopper-Pearson CI of b/n_d, exact one- and two-sided p and mid-p.
Seeds: numpy.random.SeedSequence(20261028, spawn_key=(34,)) spawned into the fixed SEED_SLOTS (33 is h_strata's, 32 tier3_fusion's); the output is byte-identical on rerun. Labels follow A6.12: partial prefix when the completed n is below 416 of 520."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

ROOT_SEED, SPAWN_KEY = 20261028, (34,)
SEED_SLOTS = ("L1", "L2", "L3", "L4", "LNI", "LLEN", "LG_shot_noise3", "LG_impulse_noise3", "LG_speckle_noise3", "LG_drop", "LEN_STRATA", "LEN_STRATA_DIFF", "DESC")
N_BOOT = 10000
N_PLANNED, N_PARTIAL = 520, 416              # A6.4: below 416 (80 percent of 520) the result is labelled "partial prefix"
LG_CELLS = ("shot_noise3", "impulse_noise3", "speckle_noise3")
LG_N, LG_MIN_N = 300, 240
NI_MARGIN = 0.03
ALPHA = 0.05


def _slots() -> dict:
    kids = np.random.SeedSequence(ROOT_SEED, spawn_key=SPAWN_KEY).spawn(len(SEED_SLOTS))
    return dict(zip(SEED_SLOTS, kids))


def _rng(slot: str) -> np.random.Generator:
    return np.random.default_rng(_slots()[slot])


# ------------------------------------------------------------------------------------------------ statistics
def _tail_ge(n: int, k: int) -> float:
    """P(Bin(n, 1/2) >= k), exact."""
    if k <= 0:
        return 1.0
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2.0 ** n


def mcnemar_counts(y_a, y_b) -> tuple[int, int]:
    a, b = np.asarray(y_a) > 0.5, np.asarray(y_b) > 0.5
    return int((a & ~b).sum()), int((~a & b).sum())


def mcnemar_p(b: int, c: int) -> dict:
    """Exact McNemar on the discordant pairs (b: first arm right and second wrong; c: the reverse). One-sided: H1 first arm better, p = P(Bin(n_d, .5) >= b). Two-sided: min(1, 2 min tail). mid-p versions for sensitivity."""
    n = b + c
    if n == 0:
        return dict(p_one=1.0, p_two=1.0, p_mid_one=1.0, p_mid_two=1.0)
    one = _tail_ge(n, b)
    other = _tail_ge(n, c)
    at = math.comb(n, b) / 2.0 ** n
    return dict(p_one=float(one), p_two=float(min(1.0, 2.0 * min(one, other))), p_mid_one=float(one - 0.5 * at), p_mid_two=float(min(1.0, 2.0 * min(one - 0.5 * at, other - 0.5 * (math.comb(n, c) / 2.0 ** n)))))


def clopper_pearson(k: int, n: int, level: float = 0.95) -> list:
    if n == 0:
        return [None, None]
    from scipy.stats import beta
    a = (1 - level) / 2
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))
    return [lo, hi]


def boot_ci(diff: np.ndarray, rng: np.random.Generator, levels=(0.90, 0.95), n_boot: int = N_BOOT) -> dict:
    """Paired percentile bootstrap of the mean of per-item differences (items resampled). Chunked so that 520 x 10,000 indices never sit in memory at once."""
    n = len(diff)
    if n == 0:
        return {f"ci{int(l * 100)}": [None, None] for l in levels}
    means = np.empty(n_boot)
    step = 1000
    for s in range(0, n_boot, step):
        idx = rng.integers(0, n, size=(min(step, n_boot - s), n))
        means[s:s + step] = diff[idx].mean(axis=1)
    out = {}
    for l in levels:
        lo, hi = np.quantile(means, [(1 - l) / 2, 1 - (1 - l) / 2])
        out[f"ci{int(round(l * 100))}"] = [float(lo), float(hi)]
    return out


def paired_test(y_a, y_b, slot: str, *, sided: str = "one", alpha: float = ALPHA) -> dict:
    """The block reported with every test (A6.4). Arm A is the first argument (LRF); positive net difference favours A."""
    a, b_ = np.asarray(y_a, float), np.asarray(y_b, float)
    n = len(a)
    b, c = mcnemar_counts(a, b_)
    p = mcnemar_p(b, c)
    diff = a - b_
    res = dict(n=n, b=b, c=c, n_d=b + c, acc_a=float(a.mean()) if n else None, acc_b=float(b_.mean()) if n else None, net=float(diff.mean()) if n else None,
               cp95_b_over_nd=clopper_pearson(b, b + c), **p, **boot_ci(diff, _rng(slot)))
    p_main = p["p_one"] if sided == "one" else p["p_two"]
    res.update(sided=sided, alpha=alpha, p=p_main, rejected=bool(p_main <= alpha and b > c), harm=bool(sided == "two" and p_main <= alpha and c > b),
               passes_two_sided_005=bool(p["p_one"] <= alpha / 2 and b > c))
    return res


def holm(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj, run = [0.0] * m, 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * pvals[i]))
        adj[i] = run
    return adj


# ------------------------------------------------------------------------------------------------ loading
def load_predictions(path: Path) -> list[dict]:
    return [json.loads(l) for l in Path(path).read_text(encoding="utf8").splitlines() if l.strip()]


def by_condition(lines: list[dict]) -> dict[str, dict[int, dict]]:
    out: dict[str, dict[int, dict]] = {}
    for l in lines:
        out.setdefault(l["condition"], {})[int(l["idx"])] = l
    return out


def arms(cond_rows: dict[int, dict], a: str, b: str, idx: list[int] | None = None):
    ids = sorted(cond_rows) if idx is None else [i for i in idx if i in cond_rows]
    return ids, np.array([cond_rows[i][a] for i in ids], float), np.array([cond_rows[i][b] for i in ids], float)


def label_partial(n: int) -> str | None:
    return f"partial prefix ({n} of {N_PLANNED})" if n < N_PARTIAL else None


# ------------------------------------------------------------------------------------------------ the analysis
def not_tested(reason: str, desc: dict | None) -> dict:
    return dict(status="not tested (gatekept)", reason=reason, descriptive=desc)


def analyse_l(lines: list[dict]) -> dict:
    by = by_condition(lines)
    out: dict = dict(n_items_by_condition={c: len(v) for c, v in by.items()})
    n1 = len(by.get("noise0.1", {}))
    partial = label_partial(n1)
    # L1
    if "noise0.1" not in by:
        out["L1"] = dict(status="not run", label="not run")
        return out
    _, ya, yb = arms(by["noise0.1"], "y_lrf", "y_none")
    l1 = paired_test(ya, yb, "L1", sided="one")
    l1["label"] = ("confirmed" if l1["rejected"] else "not confirmed") if not partial else (("confirmed, " if l1["rejected"] else "inconclusive, ") + partial)
    out["L1"] = l1
    # L2 (gatekept by L1)
    _, ya, yb = arms(by["noise0.1"], "y_lrf", "y_gatem")
    l2 = paired_test(ya, yb, "L2", sided="one")
    out["L2"] = dict(l2, status="tested") if l1["rejected"] else not_tested("L1 not confirmed", l2)
    # L3, L4 (gatekept by L2)
    l34 = {}
    for name, cond, slot in (("L3", "jpeg10", "L3"), ("L4", "splice128", "L4")):
        if cond in by:
            _, ya, yb = arms(by[cond], "y_lrf", "y_none")
            l34[name] = dict(paired_test(ya, yb, slot, sided="two"), condition=cond)
        else:
            l34[name] = dict(condition=cond, status="not run")
    ps = [l34[k]["p_two"] for k in ("L3", "L4") if "p_two" in l34[k]]
    if ps:
        adj = holm(ps + [1.0] * (2 - len(ps)))
        for k, h in zip([k for k in ("L3", "L4") if "p_two" in l34[k]], adj):
            l34[k]["p_holm"] = h
            l34[k]["rejected"] = bool(h <= ALPHA and l34[k]["b"] > l34[k]["c"])
            l34[k]["harm"] = bool(h <= ALPHA and l34[k]["c"] > l34[k]["b"])
    reached = bool(l1["rejected"] and out["L2"].get("rejected"))
    for k, v in l34.items():
        out[k] = dict(v, status="tested") if reached else not_tested("L1 or L2 not rejected", v)
    # L-NI (always)
    if "clean" in by:
        _, ya, yb = arms(by["clean"], "y_lrf", "y_none")
        ni = paired_test(ya, yb, "LNI", sided="one")
        lo90 = ni["ci90"][0]
        ni.update(margin=NI_MARGIN, lower90=lo90, non_inferior=bool(lo90 is not None and lo90 > -NI_MARGIN), label=("shown" if (lo90 is not None and lo90 > -NI_MARGIN) else "not shown"))
        out["L-NI"] = ni
    else:
        out["L-NI"] = dict(status="not run")
    # L-LEN (always)
    if "noise0.1" in by and any(r.get("y_lrf_L") is not None for r in by["noise0.1"].values()):
        rows = {i: r for i, r in by["noise0.1"].items() if r.get("y_lrf_L") is not None}
        keep = [i for i, r in rows.items() if r.get("neg_len_exact")]
        _, ya, yb = arms(rows, "y_lrf_L", "y_none_L", keep)
        ll = paired_test(ya, yb, "LLEN", sided="one")
        ll.update(n_excluded_length_mismatch=len(rows) - len(keep), n_with_length_matched_negative=len(rows), label="rejected" if ll["rejected"] else "not rejected")
        out["L-LEN"] = ll
    else:
        out["L-LEN"] = dict(status="not run", label="not run: a caption-length channel was not tested on fresh data")
    out["length_strata"] = length_strata(by.get("noise0.1", {}))
    out["partial_label"] = partial
    return out


def length_strata(rows: dict[int, dict]) -> dict:
    """Preregistered secondary (LRF-FROZEN report section 3 item 5), descriptive: LRF minus NONE (primary negative) on noise0.1 by the sign of n_tok_neg - n_tok: the true caption is shorter / equal / longer
    than the negative, plus longer-minus-shorter with a 95 percent bootstrap CI (items resampled within the strata)."""
    if not rows:
        return dict(status="not run")
    ids = sorted(rows)
    d = np.array([rows[i]["y_lrf"] - rows[i]["y_none"] for i in ids], float)
    lens = np.array([rows[i]["n_tok"] - rows[i]["n_tok_neg"] for i in ids])
    strata = {"true_shorter": lens < 0, "equal": lens == 0, "true_longer": lens > 0}
    out = {}
    for k, m in strata.items():
        x = d[m]
        yl = np.array([rows[i]["y_lrf"] for i in np.array(ids)[m]], float)
        yn = np.array([rows[i]["y_none"] for i in np.array(ids)[m]], float)
        b, c = mcnemar_counts(yl, yn)
        out[k] = dict(n=int(m.sum()), net=(float(x.mean()) if len(x) else None), b=b, c=c)
    long_, short = d[strata["true_longer"]], d[strata["true_shorter"]]
    if len(long_) and len(short):
        rng = _rng("LEN_STRATA_DIFF")
        bs = np.empty(N_BOOT)
        for s in range(0, N_BOOT, 1000):
            k = min(1000, N_BOOT - s)
            bs[s:s + k] = long_[rng.integers(0, len(long_), (k, len(long_)))].mean(1) - short[rng.integers(0, len(short), (k, len(short)))].mean(1)
        lo, hi = np.quantile(bs, [0.025, 0.975])
        out["longer_minus_shorter"] = dict(diff=float(long_.mean() - short.mean()), ci95=[float(lo), float(hi)])
    out["descriptive_only"] = True
    return out


def analyse_lg(lines: list[dict]) -> dict:
    by = by_condition(lines)
    clean = by.get("clean", {})
    out: dict = dict(cells={})
    pvals, present = [], []
    first = sorted(clean)[:LG_N] if clean else None
    for cell in LG_CELLS:
        rows = by.get(cell)
        if not rows:
            out["cells"][cell] = dict(status="absent (dropped and counted)")
            continue
        idx = sorted(rows)[:LG_N]
        _, ya, yb = arms(rows, "y_lrf", "y_none", idx)
        t = paired_test(ya, yb, f"LG_{cell}", sided="one")
        _, ga, gb = arms(rows, "y_gatem", "y_none", idx)
        gm = dict(n=len(ga), net=float((ga - gb).mean()) if len(ga) else None, b=mcnemar_counts(ga, gb)[0], c=mcnemar_counts(ga, gb)[1])
        drop = None
        if clean:
            ids_c = [i for i in idx if i in clean]
            _, cn, _ = arms(clean, "y_none", "y_none", ids_c)
            _, xn, _ = arms(rows, "y_none", "y_none", ids_c)
            dd = cn - xn
            drop = dict(n=len(dd), drop_none=float(dd.mean()) if len(dd) else None, **boot_ci(dd, _rng("LG_drop")))
        t.update(descriptive_gatem_vs_none=gm, clean_to_corrupted_drop_of_none=drop, descriptive_only=bool(len(idx) < LG_MIN_N))
        out["cells"][cell] = t
        pvals.append(t["p_one"])
        present.append(cell)
    adj = holm(pvals + [1.0] * (len(LG_CELLS) - len(pvals)))
    for cell, h in zip(present, adj):
        t = out["cells"][cell]
        t["p_holm"] = h
        t["rejected"] = bool(h <= ALPHA and t["b"] > t["c"] and not t["descriptive_only"])
        t["harm"] = bool(h <= ALPHA and t["c"] > t["b"] and not t["descriptive_only"])
    out["m_preregistered"] = len(LG_CELLS)
    out["n_cells_present"] = len(present)
    out["all_three_rejected_with_b_gt_c"] = bool(len(present) == len(LG_CELLS) and all(out["cells"][c]["rejected"] for c in present))
    return out


def run(l1_path: Path, lg_path: Path | None = None) -> dict:
    res = dict(meta=dict(spec="research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md A6.4 to A6.9 (DRAFT)", root_seed=ROOT_SEED, spawn_key=list(SPAWN_KEY), seed_slots=list(SEED_SLOTS), n_boot=N_BOOT, interval="percentile",
                      numpy_version=np.__version__, l1_predictions_sha256=hashlib.sha256(Path(l1_path).read_bytes()).hexdigest()))
    res["family_L"] = analyse_l(load_predictions(l1_path))
    if lg_path is not None:
        res["meta"]["lg_predictions_sha256"] = hashlib.sha256(Path(lg_path).read_bytes()).hexdigest()
        res["family_LG"] = analyse_lg(load_predictions(lg_path))
    res["multiplicity_note"] = "no multiplicity adjustment across families; the family of every claim is stated beside it (A6.8)"
    return res


# ------------------------------------------------------------------------------------------------ self-test
def selftest(n_sim: int = 2000) -> dict:
    """(1) exact one-sided McNemar size on simulated nulls stays at or below alpha; (2) the fixed-sequence logic; (3) the L-NI bound on synthetic data; (4) the exact tail against a direct sum."""
    rng = np.random.default_rng(1)
    out = {}
    for pi_d in (0.1, 0.24):
        rej = 0
        for _ in range(n_sim):
            n_d = int(rng.binomial(520, pi_d))
            b = int(rng.binomial(n_d, 0.5))
            rej += mcnemar_p(b, n_d - b)["p_one"] <= ALPHA
        out[f"size_pi_d_{pi_d}"] = rej / n_sim
    out["size_ok"] = all(out[f"size_pi_d_{p}"] <= ALPHA + 0.012 for p in (0.1, 0.24))
    out["tail_ok"] = abs(mcnemar_p(7, 3)["p_one"] - sum(math.comb(10, i) for i in range(7, 11)) / 1024) < 1e-15 and mcnemar_p(0, 0)["p_one"] == 1.0
    # fixed sequence on synthetic predictions: strong LRF gain on noise0.1, none elsewhere
    r = np.random.default_rng(2)

    def lines(gain: bool, n: int = 400) -> list[dict]:
        ls = []
        for i in range(n):
            for c in ("clean", "jpeg10", "noise0.1", "splice128"):
                yn = int(r.random() < 0.7)
                yl = yn if not (gain and c == "noise0.1" and yn == 0 and r.random() < 0.5) else 1
                ls.append(dict(idx=i, gid=i, image_id=i, condition=c, n_tok=10, n_tok_neg=10 + (i % 3) - 1, y_none=yn, y_gatem=yn, y_lrf=yl, y_none_L=yn, y_gatem_L=yn, y_lrf_L=yl, n_tok_neg_len=10, neg_len_diff=0, neg_len_exact=True))
        return ls
    a_gain, a_null = analyse_l(lines(True)), analyse_l(lines(False))
    out["seq_gain_L1_confirmed"] = bool(a_gain["L1"]["rejected"])
    out["seq_gain_L2_tested"] = a_gain["L2"].get("status") == "tested"
    out["seq_null_L2_gatekept"] = a_null["L2"].get("status") == "not tested (gatekept)" and a_null["L3"].get("status") == "not tested (gatekept)"
    # L-NI on synthetic data: LRF = NONE except a 1-point loss -> bound above -0.03; a 6-point loss -> below
    def ni(loss: float, n: int = 520) -> bool:
        yn = (r.random(n) < 0.8).astype(int)
        yl = yn.copy()
        yl[r.random(n) < loss] = 0
        ls = [dict(idx=i, gid=i, image_id=i, condition="clean", n_tok=10, n_tok_neg=10, y_none=int(yn[i]), y_gatem=int(yn[i]), y_lrf=int(yl[i])) for i in range(n)]
        return analyse_l(ls + [dict(l, condition="noise0.1") for l in ls])["L-NI"]["non_inferior"]
    out["ni_small_loss_shown"], out["ni_large_loss_not_shown"] = ni(0.01), (not ni(0.12))
    out["ok"] = bool(out["size_ok"] and out["tail_ok"] and out["seq_gain_L1_confirmed"] and out["seq_gain_L2_tested"] and out["seq_null_L2_gatekept"] and out["ni_small_loss_shown"] and out["ni_large_loss_not_shown"])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--l1", default=None)
    ap.add_argument("--lg", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        st = selftest()
        print(json.dumps(st))
        return 0 if st["ok"] else 1
    if not a.l1:
        ap.error("--l1 is required")
    res = run(Path(a.l1), Path(a.lg) if a.lg else None)
    out = Path(a.out) if a.out else Path(a.l1).with_name("a6_analysis.json")
    out.write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf8")
    print(json.dumps(dict(out=str(out), L1=res["family_L"].get("L1", {}).get("label"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
