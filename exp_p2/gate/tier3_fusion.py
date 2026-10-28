"""Tier-3 fusion comparators of Paper 2 / GATE (SAP Addendum A4 r1, section A4.1; red-team conditions C4-9 and C4-10). Exploratory, CPU only, no model.

    python -m exp_p2.gate.tier3_fusion --run-id P2-GATE-M4 --cal-run P2-GATE-M2 --family-run P2-GATE-M3

Question (A4.1.1): on the same per-token evidence Delta_j and the same decision rule as family P, does the hard gate GATE-M give a different image-direction
verification accuracy from (a) detector-free robust combiners (MED, TM-G, TM20), (b) discounting of the gate-flagged tokens (SOFT-G) and (c) reliability weighting of
every token by the gate's own score (SOFT-A)?  Label: Tier 3, exploratory. Confidence intervals only: NO p-value is computed for any contrast; no multiplicity claim.

Order (A4.1.9): runs only after runs/<run>/analysis.json with the P section is committed (this module refuses before it opens items.jsonl or any array of the run),
after the consistency gate (A4.1.3) passed on every item of every cell. Output runs/<run>/tier3_fusion.json is write-once and byte-identical on a recomputation.
Seeds (A4.1.7, C4-10): seeds.py is NOT edited; the stream is SeedSequence(20261028, spawn_key=(32,)) spawned into 6 slots (clean, jpeg, noise, splice, patch, swap).
Specification section map: A4.1.2 load_cell / complete case, A4.1.3 consistency_problems, A4.1.4 item_margins, A4.1.5 CalPool, A4.1.6 accuracy_contrasts,
A4.1.7 bootstrap_interval / cell_seed_sequence, A4.1.8 d_control, A4.1.9 require_committed / run, A4.1.10 reading / counts_against."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                          # noqa: E402
from exp_p2.gate import analysis_m4, artifacts, calibrate as cal, config, evidence, fit_threshold, scores, seeds     # noqa: E402

OUT_NAME = "tier3_fusion.json"
ALPHA_KEY = f"{config.ALPHA_PRIMARY:g}"                      # "0.05": flag arrays are `<cond>_flag0.05`, summaries `img["gate0.05"]`, `gate["0.05"]`
M_TOKENS = 1024                                              # tokens per item (32 x 32 map); A4.1.2 complete case
TM20_FRACTION = 0.20                                         # A4.1.4 TM20: k = floor(0.20 m) = 204 per tail
N_BOOT = 10000                                               # A4.1.7
Z_MDD = 1.959964 + 0.841621                                  # A4.1.7: two-sided 5 percent, 80 percent power normal approximation = 2.801585
MEAN_TOL = 1e-9                                              # A4.1.3
MDD_DESIGN_MARGIN = 0.05                                     # A4.1.10 / SAP 4.3
SEED_SPAWN_KEY = (32,)                                       # A4.1.7: the child an append of `tier3_fusion` at position 32 of seeds.ANALYSES would give (A3.7)
SEED_SLOTS = ("clean", "jpeg", "noise", "splice", "patch", "swap")
SANITY_CONDS = analysis_m4.SANITY_CONDS                      # ("patch", "swap"): PS cells

ARMS = ("NONE", "GM", "MED", "TM-G", "TM20", "SOFT-G", "SOFT-A")
COMPARATORS = ("MED", "TM-G", "TM20", "SOFT-G", "SOFT-A")
DETECTOR_FREE = ("MED", "TM-G", "TM20")
D_ARMS = ("NONE", "GM", "TM-G", "TM20")                      # A4.1.8: MED, SOFT-G and SOFT-A have no d here
D_CONTRASTS = (("TM-G", "GM"), ("TM20", "GM"))

LABEL = "Tier 3, exploratory (SAP 7): confidence intervals only; no p-value is computed for any contrast; no multiplicity claim"
LIMITS = (
    "(a) no sign-aware detector-free estimator is computed: the direction in which a corruption moves Delta is defined relative to the true caption, so such a combiner would use the label (A4.1.4)",
    "(b) SOFT-G's weights lie token by token between GM's and NONE's; it is discounting of the gate-flagged tokens, not reliability weighting of every token (A4.1.5)",
    "(c) when the gate's score is near chance (runs/P2-GATE-M1/analysis.json, table.<corr>.q.mean) the flagged count is close to the false-alarm count, so TM-G approximates NONE trimmed at about that count and TM-G minus GM largely repeats P's own contrast",
    "(d) at the realised n many contrasts may be uninformative, shown by the minimum detectable difference printed beside every interval",
)
NOT_COMPUTED = ("denoised copies <cond>_dn (no B, D or flags stored, exp_p2/run_gate_m4.py:144-148)", "the text direction (no per-token text arrays are stored)")


class Refusal(RuntimeError):
    """A precondition of A4.1.9 / A4.1.2 is not met: nothing is written, exit code 2."""


class ConsistencyError(RuntimeError):
    """A4.1.3: a recomputed NONE / GM / flag count differs from the stored one. Part 1 stops, exit code 3."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__(f"{len(problems)} mismatch(es) between the recomputed and the stored summaries: " + "; ".join(problems[:10]) + (" ..." if len(problems) > 10 else ""))


# ------------------------------------------------------------------------------------------------ A4.1.5: calibration pool, survival function and the two weights
@dataclass(frozen=True)
class CalPool:
    """Clean calibration tokens' unjittered suspicion u^cal (sorted, float64 image of the float32 values) and tau of the primary alpha.
    S_cal(x) = #{u^cal > x} / N and P_cal(x) = (1 + #{u^cal >= x}) / (N + 1); all calibration items have the same token count, so the item-weighted pooled survival
    function of the CRC equals the token-pooled one (checked when the pool is built)."""
    u: np.ndarray
    tau: float

    @property
    def n(self) -> int:
        return int(self.u.size)

    def count_gt(self, x) -> np.ndarray:
        return self.n - np.searchsorted(self.u, np.asarray(x, np.float64), side="right")

    def count_ge(self, x) -> np.ndarray:
        return self.n - np.searchsorted(self.u, np.asarray(x, np.float64), side="left")

    def survival(self, x) -> np.ndarray:
        return self.count_gt(x) / self.n

    def p_value(self, x) -> np.ndarray:
        return (1.0 + self.count_ge(x)) / (self.n + 1.0)

    def weights_g(self, u, flag) -> np.ndarray:
        """SOFT-G: w = 1 off the flagged set; on it min{1, S_cal(u_j) / S_cal(tau)} (0 if S_cal(tau) = 0, then SOFT-G = GM)."""
        flag = np.asarray(flag, bool)
        w = np.ones(flag.shape, np.float64)
        if flag.any():
            s_tau = float(self.survival(self.tau))
            if s_tau <= 0.0:
                w[flag] = 0.0
            else:
                w[flag] = np.minimum(1.0, self.survival(np.asarray(u)[flag]) / s_tau)
        return w

    def weights_a(self, u) -> np.ndarray:
        """SOFT-A: w = P_cal(u_j), the conformal p-value of the token against the clean calibration tokens, in [1/(N+1), 1]."""
        return self.p_value(u)


def build_cal_pool(cal_dir: Path, threshold: dict) -> tuple[CalPool, dict]:
    """Pool from runs/<cal>/items.jsonl and arrays/ (clean pairs only), mirroring fit_threshold.main (all rows, ascending idx). Asserts the id hash against threshold.json."""
    cal_dir = Path(cal_dir)
    rows = sorted(common.read_jsonl(cal_dir / "items.jsonl"), key=lambda r: r["idx"])
    if not rows:
        raise Refusal(f"{cal_dir / 'items.jsonl'} has no rows")
    ids = [r["gid"] for r in rows]
    if cal.ids_hash(ids) != threshold["ids_hash"]:
        raise Refusal(f"ids_hash of the calibration items ({cal.ids_hash(ids)}) differs from threshold.json ({threshold['ids_hash']}): not the calibration fold that fixed tau")
    parts, shas = [], {}
    for r in rows:
        p = cal_dir / "arrays" / f"item{r['idx']:04d}.npz"
        if not p.exists():
            raise Refusal(f"{p} missing")
        raw = p.read_bytes()
        shas[p.name] = hashlib.sha256(raw).hexdigest()
        with np.load(io.BytesIO(raw)) as arr:
            parts.append(fit_threshold.suspicion_from_arrays(arr, "q"))
    if len({u.size for u in parts}) != 1:
        raise Refusal("calibration items have different token counts: the token-pooled survival function is not the item-weighted one (A4.1.5)")
    u = np.concatenate(parts)
    if not np.all(np.isfinite(u)):
        raise Refusal("non-finite calibration suspicion u")
    tau = cal.Threshold.from_json(threshold["thresholds"][ALPHA_KEY]).tau
    pool = CalPool(np.sort(u.astype(np.float64)), float(tau))
    return pool, dict(n_cal_items=len(rows), n_cal_tokens=pool.n, tau=_enc(pool.tau), s_cal_tau=float(pool.survival(pool.tau)), m2_npz_sha256=shas)


# ------------------------------------------------------------------------------------------------ A4.1.4: arms (one item)
def _trimmed(d: np.ndarray, srt: np.ndarray, k: int) -> tuple[float, bool]:
    """Mean after removing k values from each tail; k = 0 is the plain mean in the original order (so TM-G with g <= 1 is NONE bit for bit). Empty -> (0.0, True)."""
    m = d.size
    if k <= 0:
        return float(d.mean()), False
    if m - 2 * k <= 0:
        return 0.0, True
    return float(srt[k:m - k].mean()), False


def _weighted(d: np.ndarray, w: np.ndarray) -> tuple[float, bool]:
    sw = float(w.sum())
    if not sw > 0.0:
        return 0.0, True
    return float(np.sum(w * d) / sw), False


def item_margins(delta, flag, u, pool: CalPool) -> dict[str, tuple[float, bool]]:
    """Item margin M_i of every arm as (margin, empty). Sorting is in float64. An empty retained set or a zero weight sum gives margin 0.0 and empty = True (Y = 0, SAP 2.1)."""
    d = np.asarray(delta, np.float64)
    F = np.asarray(flag, bool)
    m, g = int(d.size), int(F.sum())
    srt = np.sort(d)
    keep = d[~F]
    return {
        "NONE": (float(d.mean()), False),
        "GM": (float(keep.mean()), False) if keep.size else (0.0, True),
        "MED": (float(np.median(d)), False),
        "TM-G": _trimmed(d, srt, g // 2),
        "TM20": _trimmed(d, srt, int(math.floor(TM20_FRACTION * m))),
        "SOFT-G": _weighted(d, pool.weights_g(u, F)),
        "SOFT-A": _weighted(d, pool.weights_a(u)),
    }


def retained_d(delta, flag) -> dict[str, float]:
    """Evidence ratio d = mean / sd (ddof 1, evidence.py) over the retained set of NONE, GM, TM-G and TM20; NaN when |R| < 2 or sd = 0 (A4.1.8)."""
    d = np.asarray(delta, np.float64)
    F = np.asarray(flag, bool)
    m, g = int(d.size), int(F.sum())
    srt = np.sort(d)

    def trimmed_set(k):
        return d if k <= 0 else srt[k:m - k]
    sets = {"NONE": d, "GM": d[~F], "TM-G": trimmed_set(g // 2), "TM20": trimmed_set(int(math.floor(TM20_FRACTION * m)))}
    return {a: evidence.evidence_from_delta(s)["d"] for a, s in sets.items()}


# ------------------------------------------------------------------------------------------------ A4.1.7: bootstrap
def cell_seed_sequence(slot: str) -> np.random.SeedSequence:
    """Child of SeedSequence(20261028, spawn_key=(32,)) for the cell's fixed slot; an absent cell leaves its slot unused, so no slot depends on which cells exist."""
    base = np.random.SeedSequence(seeds.ROOT_SEED, spawn_key=SEED_SPAWN_KEY)
    return base.spawn(len(SEED_SLOTS))[SEED_SLOTS.index(slot)]


def index_matrix(n: int, child, n_boot: int = N_BOOT) -> np.ndarray:
    """One matrix per cell, shared by every arm and contrast of the cell (items in ascending idx order)."""
    return np.random.default_rng(child).integers(0, n, size=(n_boot, n))


def bootstrap_interval(boots: np.ndarray) -> dict:
    """95 percent percentile interval (numpy.quantile default method) and MDD = (1.959964 + 0.841621) * SD (ddof 1) of the resampled statistics. Non-finite resamples are dropped and counted."""
    b = np.asarray(boots, np.float64)
    ok = np.isfinite(b)
    b = b[ok]
    if b.size < 2:
        return dict(lo=float("nan"), hi=float("nan"), se_boot=float("nan"), mdd=float("nan"), n_resamples=int(b.size), n_undefined_resamples=int((~ok).sum()))
    se = float(b.std(ddof=1))
    return dict(lo=float(np.quantile(b, 0.025)), hi=float(np.quantile(b, 0.975)), se_boot=se, mdd=Z_MDD * se, n_resamples=int(b.size), n_undefined_resamples=int((~ok).sum()))


def reading(lo: float, hi: float) -> str:
    """Three-way reading of 'comparator minus reference' (A4.1.10)."""
    if not (math.isfinite(lo) and math.isfinite(hi)):
        return "undefined"
    if lo > 0:
        return "above"
    if hi < 0:
        return "below"
    return "not_distinguishable"


def counts_against(comparator: str, read: str, mdd: float) -> str:
    """What the reading means for the method, 'comparator minus GM' on a P cell (A4.1.10, C4-9 / F7(d))."""
    if read == "undefined":
        return "undefined"
    if read == "below":
        return "gate_higher"
    if comparator in DETECTOR_FREE:
        if read == "above":
            return "finding_against_the_method"
        return "finding_against_added_value" if mdd <= MDD_DESIGN_MARGIN else "uninformative_at_this_n"
    if read == "above":
        return "finding_against_discarding"
    return "discarding_and_discounting_not_distinguishable" if comparator == "SOFT-G" else "discarding_and_weighting_not_distinguishable"


def accuracy_contrasts(Y: dict[str, np.ndarray], idx: np.ndarray, cell_kind: str) -> dict:
    """Fixed list of A4.1.7: MED, TM-G, TM20, SOFT-G, SOFT-A minus GM, and minus NONE. Accuracy difference = (b - c) / n."""
    out = {}
    for ref in ("GM", "NONE"):
        for k in COMPARATORS:
            diff = Y[k].astype(np.int8) - Y[ref].astype(np.int8)
            n = int(diff.size)
            b, c = int((diff == 1).sum()), int((diff == -1).sum())
            iv = bootstrap_interval(diff[idx].mean(axis=1))
            row = dict(comparator=k, reference=ref, n=n, acc_comparator=float(Y[k].mean()), acc_reference=float(Y[ref].mean()), b=b, c=c, n_d=b + c, diff=(b - c) / n,
                       ci95=[iv["lo"], iv["hi"]], se_boot=iv["se_boot"], mdd=iv["mdd"], n_undefined_resamples=iv["n_undefined_resamples"], reading=reading(iv["lo"], iv["hi"]))
            if ref == "GM" and cell_kind == "P":
                row["counts_against"] = counts_against(k, row["reading"], iv["mdd"])
            out[f"{k}_minus_{ref}"] = row
    return out


def d_control(dvals: dict[str, np.ndarray], idx: np.ndarray) -> dict:
    """A4.1.8: per-arm mean d and the paired bootstrap interval of the mean of d^TM-G - d^GM and d^TM20 - d^GM over the cell's index matrix. Items with |R| < 2 or sd = 0 in either
    arm are dropped and counted; the drop is applied inside each resample (valid-weighted mean over the resampled items) so that the index matrix stays the cell's own."""
    per_arm = {a: dict(n_valid=int(np.isfinite(v).sum()), n_dropped=int((~np.isfinite(v)).sum()), mean_d=(float(np.mean(v[np.isfinite(v)])) if np.isfinite(v).any() else float("nan")))
               for a, v in dvals.items()}
    contrasts = {}
    for a, ref in D_CONTRASTS:
        valid = np.isfinite(dvals[a]) & np.isfinite(dvals[ref])
        diff = np.where(valid, dvals[a] - dvals[ref], 0.0)
        cnt = valid[idx].sum(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            boots = np.where(cnt > 0, diff[idx].sum(axis=1) / cnt, np.nan)
        iv = bootstrap_interval(boots)
        contrasts[f"{a}_minus_{ref}"] = dict(n_valid=int(valid.sum()), n_dropped=int((~valid).sum()), mean_diff=(float(diff[valid].mean()) if valid.any() else float("nan")),
                                             ci95=[iv["lo"], iv["hi"]], se_boot=iv["se_boot"], mdd=iv["mdd"], n_undefined_resamples=iv["n_undefined_resamples"],
                                             reading=reading(iv["lo"], iv["hi"]), reading_wording="higher evidence ratio d")
    return dict(per_arm=per_arm, contrasts=contrasts, note="descriptive; symmetric trimming lowers the retained sd mechanically (A4.1.8); Tier 3, never qualifies P's sentence")


# ------------------------------------------------------------------------------------------------ A4.1.2: data, complete case
@dataclass
class CellData:
    cell: str
    idx: list[int]
    delta: np.ndarray         # [n, m] float32 as stored
    flag: np.ndarray          # [n, m] bool
    u: np.ndarray             # [n, m] float32, unjittered, recomputed from the stored B and D
    stored: list[dict]        # per item: the row's conds[cell]
    excluded: dict            # reason -> list of idx


def _complete_case(arr, cell: str, m: int):
    """Returns (delta, flag, u) or a reason string. An item enters iff its npz holds `<cell>_delta` with m finite values, `<cell>_flag0.05` and finite `<cell>_B`, `<cell>_D`."""
    keys = (f"{cell}_delta", f"{cell}_flag{ALPHA_KEY}", f"{cell}_B", f"{cell}_D")
    for k in keys:
        if k not in arr.files:
            return f"array {k} missing"
    delta, flag, B, D = (arr[k] for k in keys)
    if delta.shape != (m,) or not np.all(np.isfinite(delta)):
        return f"{cell}_delta is not {m} finite values"
    if flag.shape != (m,):
        return f"{cell}_flag{ALPHA_KEY} is not {m} values"
    if B.shape != (m,) or D.shape != (m,) or not (np.all(np.isfinite(B)) and np.all(np.isfinite(D))):
        return f"{cell}_B or {cell}_D is not {m} finite values"
    return delta, flag.astype(bool), scores.suspicion_q(B, D)


def load_cell(run_dir: Path, rows: list[dict], cell: str, m: int = M_TOKENS) -> CellData:
    """Complete-case items of one cell, ascending idx; exclusions are counted with their reason (SAP 8.1)."""
    run_dir = Path(run_dir)
    idx, D_, F_, U_, stored, excluded = [], [], [], [], [], {}
    for r in sorted(rows, key=lambda r: r["idx"]):
        why = None
        if cell not in r.get("conds", {}):
            why = f"cell {cell} absent from the item row"
        else:
            p = run_dir / "arrays" / f"item{r['idx']:04d}.npz"
            if not p.exists():
                why = "npz missing"
            else:
                with np.load(p) as arr:
                    got = _complete_case(arr, cell, m)
                if isinstance(got, str):
                    why = got
        if why is not None:
            excluded.setdefault(why, []).append(int(r["idx"]))
            continue
        idx.append(int(r["idx"]))
        D_.append(got[0])
        F_.append(got[1])
        U_.append(got[2])
        stored.append(r["conds"][cell])
    z = lambda xs, dt, shape: np.stack(xs) if xs else np.zeros(shape, dt)       # noqa: E731
    return CellData(cell, idx, z(D_, np.float32, (0, m)), z(F_, bool, (0, m)), z(U_, np.float32, (0, m)), stored, excluded)


# ------------------------------------------------------------------------------------------------ A4.1.3: consistency gate
def consistency_problems(cd: CellData) -> list[str]:
    """Recompute NONE and GM with evidence_from_delta and compare with the stored img.none and img['gate0.05'] (y equal, mean within 1e-9) and g_i with gate['0.05'].n_flag."""
    probs = []
    for i, st in enumerate(cd.stored):
        tag = f"{cd.cell} idx {cd.idx[i]}"
        delta, flag = cd.delta[i], cd.flag[i]
        for arm_key, included in (("none", None), (f"gate{ALPHA_KEY}", ~flag)):
            try:
                s = st["img"][arm_key]
                s_y, s_mean = int(s["y"]), float(s["mean"])
            except (KeyError, TypeError, ValueError):
                probs.append(f"{tag}: stored img.{arm_key} missing or unreadable")
                continue
            ev = evidence.evidence_from_delta(delta, included)
            if ev["y"] != s_y:
                probs.append(f"{tag}: y of {arm_key} recomputed {ev['y']} stored {s_y}")
            if not abs(ev["mean"] - s_mean) <= MEAN_TOL:
                probs.append(f"{tag}: mean of {arm_key} recomputed {ev['mean']!r} stored {s_mean!r}")
        try:
            n_flag = int(st["gate"][ALPHA_KEY]["n_flag"])
        except (KeyError, TypeError, ValueError):
            probs.append(f"{tag}: stored gate[{ALPHA_KEY}].n_flag missing or unreadable")
            continue
        if int(flag.sum()) != n_flag:
            probs.append(f"{tag}: g_i recomputed {int(flag.sum())} stored n_flag {n_flag}")
    return probs


# ------------------------------------------------------------------------------------------------ one cell
def cell_results(cd: CellData, pool: CalPool, kind: str, slot: str, n_boot: int = N_BOOT) -> dict:
    n = len(cd.idx)
    base = dict(kind=kind, seed_slot=slot, seed_slot_index=SEED_SLOTS.index(slot), n=n, excluded={k: dict(n=len(v), idx=v) for k, v in cd.excluded.items()}, n_excluded=sum(len(v) for v in cd.excluded.values()))
    if n == 0:
        return dict(base, arms={}, contrasts={}, d_control={}, note="no complete-case item: nothing computed")
    margins = [item_margins(cd.delta[i], cd.flag[i], cd.u[i], pool) for i in range(n)]
    Y = {a: np.array([int(mg[a][0] > 0 and not mg[a][1]) for mg in margins], np.int8) for a in ARMS}
    arm_rows = {a: dict(acc=float(Y[a].mean()), n_empty=int(sum(mg[a][1] for mg in margins)), n_ties=int(sum((mg[a][0] == 0.0 and not mg[a][1]) for mg in margins))) for a in ARMS}
    idx = index_matrix(n, cell_seed_sequence(slot), n_boot)
    d_items = [retained_d(cd.delta[i], cd.flag[i]) for i in range(n)]
    dv = {a: np.array([di[a] for di in d_items], np.float64) for a in D_ARMS}
    return dict(base, mean_flagged=float(cd.flag.sum(axis=1).mean()), arms=arm_rows, contrasts=accuracy_contrasts(Y, idx, kind), d_control=d_control(dv, idx))


def n_intervals(cell_res: dict) -> int:
    return len(cell_res.get("contrasts", {})) + len(cell_res.get("d_control", {}).get("contrasts", {}))


# ------------------------------------------------------------------------------------------------ A4.1.9: the order
def _git(cwd: Path, *args: str):
    try:
        return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    except OSError as e:
        raise Refusal(f"git cannot be run ({e}): the commit of analysis.json cannot be verified") from e


def require_committed(path: Path) -> None:
    """Refuses unless `path` is tracked by git and has no staged or unstaged change (same test as foil.require_committed, but in the repository that contains the file)."""
    p = Path(path)
    if not p.exists():
        raise Refusal(f"{p} does not exist: analysis_m4 must be run and its output committed first (A4.1.9)")
    if _git(p.parent, "ls-files", "--error-unmatch", "--", p.name).returncode != 0:
        raise Refusal(f"{p.name} is not tracked by git: commit analysis.json with the P section before the Tier-3 comparators run (A4.1.9)")
    st = _git(p.parent, "status", "--porcelain", "--", p.name)
    if st.returncode != 0 or st.stdout.strip():
        raise Refusal(f"{p.name} has uncommitted changes: commit analysis.json with the P section first (A4.1.9)")


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _enc(x: float):
    return "inf" if x == float("inf") else "-inf" if x == float("-inf") else float(x)


def _quote_p_contrast(analysis: dict, corr: str) -> dict | None:
    """GM minus NONE on the P cell, quoted from analysis.json (Y), not recomputed; the p-values of the P section are NOT copied."""
    src = analysis.get("secondary_y") if analysis.get("rule") == "R3" else analysis.get("primary")
    ent = ((src or {}).get("per_corruption") or {}).get(corr)
    if not ent or not ent.get("tested"):
        return None
    return {k: ent[k] for k in ("b", "c", "n_d", "n", "acc_a", "acc_b", "delta", "ci95") if k in ent} | dict(source="analysis.json " + ("secondary_y" if analysis.get("rule") == "R3" else "primary") + f".per_corruption.{corr} (quoted)")


def run(run_id: str, cal_run: str, family_run: str = "P2-GATE-M3", *, n_boot: int = N_BOOT, m: int = M_TOKENS) -> dict:
    """The whole of Part 1; returns the dict that is written. Raises Refusal (exit 2) or ConsistencyError (exit 3). Nothing of the M4 run is opened before the commit check."""
    runs = Path(common.RUNS)
    run_dir, cal_dir, fam_dir = runs / run_id, runs / cal_run, runs / family_run
    ap = run_dir / "analysis.json"
    require_committed(ap)                                                              # first: A4.1.9 (before items.jsonl or any array is touched)
    analysis = json.loads(ap.read_text(encoding="utf8"))
    if not isinstance((analysis.get("primary") or {}).get("per_corruption"), dict):
        raise Refusal("analysis.json has no P section (primary.per_corruption)")
    for need in (fam_dir / "family.json", cal_dir / "threshold.json"):
        if not need.exists():
            raise Refusal(f"{need} missing")
    fam = json.loads((fam_dir / "family.json").read_text(encoding="utf8"))
    threshold = json.loads((cal_dir / "threshold.json").read_text(encoding="utf8"))
    keys = [f["key"] for f in fam.get("family", [])]
    if keys != list(analysis.get("family", [])):
        raise Refusal(f"family.json keys {keys} differ from analysis.json family {analysis.get('family')}")
    rows, n_dup = analysis_m4.load_items(run_dir)
    if len(rows) != analysis.get("n_items"):
        raise Refusal(f"items.jsonl holds {len(rows)} items but analysis.json analysed {analysis.get('n_items')}: the items are exactly those analysis_m4 analysed (A4.1.2)")
    pool, pool_info = build_cal_pool(cal_dir, threshold)

    sanity = list(SANITY_CONDS)
    if (fam_dir / "ps_frozen.json").exists():
        sanity = list(json.loads((fam_dir / "ps_frozen.json").read_text(encoding="utf8"))["params"]["sanity_order"])
    present = {c for r in rows for c in r["conds"]}
    ps_cells = [c for c in sanity if c in present]
    plan = [("clean", "clean", "clean")] + [(f["key"], "P", f["corruption"]) for f in fam.get("family", [])] + [(c, "PS", c) for c in ps_cells]
    for _, _, slot in plan:
        if slot not in SEED_SLOTS:
            raise Refusal(f"no seed slot for {slot!r}; the 6 slots are fixed ({SEED_SLOTS})")

    data = {cell: load_cell(run_dir, rows, cell, m) for cell, _, _ in plan}
    problems = [p for cd in data.values() for p in consistency_problems(cd)]
    if problems:
        raise ConsistencyError(problems)

    cells = {cell: cell_results(data[cell], pool, kind, slot, n_boot) for cell, kind, slot in plan}
    for cell, kind, slot in plan:
        if kind == "P":
            cells[cell]["gm_minus_none_quoted"] = _quote_p_contrast(analysis, analysis_m4.corr_of(cell))
    n_int = sum(n_intervals(c) for c in cells.values())
    return dict(
        label=LABEL, spec="SAP Addendum A4 r1, section A4.1 (research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md)", rule=analysis.get("rule"),
        r3_note=("under R3 this part still uses Y (AB.3 item 3); these contrasts are not on P's R3 endpoint; the d-scale control is in d_control" if analysis.get("rule") == "R3" else None),
        multiplicity=dict(n_intervals=n_int, statement="no multiplicity adjustment (SAP 7)"),
        seed=dict(root=seeds.ROOT_SEED, spawn_key=list(SEED_SPAWN_KEY), slots=list(SEED_SLOTS), documented_fallback=True, numpy_version=np.__version__, n_boot=n_boot, interval="percentile, numpy.quantile 0.025 and 0.975",
                  note="seeds.py is not edited (A4.1.7, C4-10); this is the documented fallback seed"),
        inputs=dict(run_id=run_id, cal_run=cal_run, family_run=family_run, n_items_analysed=analysis.get("n_items"), n_duplicates_removed=n_dup, tokens_per_item=m,
                    analysis_json_sha256=_sha256(ap), family_json_sha256=_sha256(fam_dir / "family.json"), threshold_json_sha256=_sha256(cal_dir / "threshold.json"),
                    threshold_ids_hash=threshold["ids_hash"], alpha=config.ALPHA_PRIMARY, **pool_info),
        limits=list(LIMITS), not_computed=list(NOT_COMPUTED) + sorted(f"{c} (denoised copy)" for c in present if c.endswith("_dn")),
        not_run_ps_cells=[c for c in sanity if c not in present], cells={k: v for k, v in cells.items() if v["kind"] == "P"}, clean=cells["clean"],
        ps_cells={k: v for k, v in cells.items() if v["kind"] == "PS"}, ps_note="positive-control conditions; pipeline check only; never pooled with or plotted beside the P cells",
    )


def dumps(res: dict) -> str:
    return json.dumps(res, indent=1, default=float)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m exp_p2.gate.tier3_fusion", description=__doc__.split("\n")[0])
    ap.add_argument("--run-id", default="P2-GATE-M4")
    ap.add_argument("--cal-run", default="P2-GATE-M2")
    ap.add_argument("--family-run", default="P2-GATE-M3")
    a = ap.parse_args(argv)
    try:
        res = run(a.run_id, a.cal_run, a.family_run)
        out = Path(common.RUNS) / a.run_id / OUT_NAME
        artifacts.write_once(out, dumps(res), False)
    except (Refusal, artifacts.WriteOnceError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    except ConsistencyError as e:
        print("PIPELINE DISCREPANCY (A4.1.3), Part 1 stops:", e, file=sys.stderr)
        return 3
    print(json.dumps(dict(written=str(out), cells=list(res["cells"]) + ["clean"] + list(res["ps_cells"]), n_intervals=res["multiplicity"]["n_intervals"], multiplicity=res["multiplicity"]["statement"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
