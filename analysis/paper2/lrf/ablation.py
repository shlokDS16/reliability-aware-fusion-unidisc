"""Tier-3 exploratory ablation of the frozen LRF (Study 2). Plan: research/paper2/tnnls/ABLATION-PLAN-2026-10-30.md (commit 506818c7, with the statistician's changes SC-1..SC-9 applied).

    exploratory; added after the primary, family H and Study 2 results

Subcommands (CPU only; torch and BLAS at 4 threads):

    fit      fit every variant of plan section 3a on the 500 DESIGN items only (runs/P2-LRF-RESCORE/arrays), run the R0 harness reproduction FIRST, the design-item KO-ALL control, the seed-spread refits
             and write the frozen variant files plus HASHES.json to the fit run directory (runs/P2-LRF-ABL-FIT). No accuracy, decision count or margin of any variant is computed or stored on design items.
    score    (STAGE 2, after a gate-auditor code audit; not run in stage 1) fresh arrays only: positive controls first (controls.json), then every weighting; writes predictions_ablation.jsonl
    analyse  (STAGE 2) ablation_analysis.json: accuracies, paired differences against NONE and the frozen LRF with 95 percent percentile bootstrap intervals on shared per-cell resamples, K read from the output

    python -m analysis.paper2.lrf.ablation fit --src runs/P2-LRF-RESCORE --frozen runs/P2-LRF-FROZEN-LFIX --out runs/P2-LRF-ABL-FIT

Reuse by import, not copy: `data.engineer`, `families` (TorchFamily, F1GAM, standardiser, temperature, o1_criterion), `run.successive_halving` and `run.ss` (the learned-ceiling stream, root 20261029), and from `exp_p2.gate.lrf_score`
the decision rule `decide` (Y = 1[sum_j w_j Delta_j > 0], tie = wrong, NonFinite on any non-finite feature, weight, score or margin), `arm_y` (NONE), `raw_from_arrays`, `load_frozen`, `gam_f`.
No Study 1 object appears here: no GATE flag, no `y_gatem`/`m_gatem`, no threshold, no suspicion score. The array reader is an allow-list (B, D, s3, tbv, tex, nbr, delta) and raises on anything else (`GateFieldRefused`)."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as imd
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np  # noqa: E402
import torch  # noqa: E402
import torch.nn as nn  # noqa: E402
import torch.nn.functional as F  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from analysis_posthoc.learned_ceiling import data, families as fam, run as lrun       # noqa: E402
from exp_p2.gate import lrf_score as LS                                                # noqa: E402
from exp_p2.gate.lrf_score import HashMismatch, NonFinite, arm_y, decide, gam_f       # noqa: E402

torch.set_num_threads(4)
M = data.M
FEATURES = data.feature_names()
N_FEAT = len(FEATURES)
FROZEN_KEY = 99                                                  # learned-ceiling seed-spawn key of the frozen fit (lrf.py FROZEN_KEY)
PLAN = "research/paper2/tnnls/ABLATION-PLAN-2026-10-30.md"
LABEL = "exploratory; added after the primary, family H and Study 2 results"
FIT_DIR = ROOT / "runs" / "P2-LRF-ABL-FIT"
SCORE_DIR = ROOT / "runs" / "P2-LRF-ABL-SCORE"
FROZEN_DIR = ROOT / "runs" / "P2-LRF-FROZEN-LFIX"
CODE_FILES = ("analysis/paper2/lrf/ablation.py", "exp_p2/gate/lrf_score.py")
PINNED_FILES = ("data.py", "families.py", "lrf.py", "run.py")


class FitRefused(RuntimeError):
    """A precondition of the fit stage does not hold; nothing was fitted."""


class R0Failed(RuntimeError):
    """The harness did not reproduce the frozen LRF (plan section 6 item 1). Nothing is scored; section 3 is unchanged."""


class ControlMismatch(RuntimeError):
    """A positive control failed (plan section 6 item 5). No variant output exists."""


class GateFieldRefused(RuntimeError):
    """The scorer was asked for a GATE field or any array outside the allow-list (plan section 0 item 2)."""


# ================================================================================================ section 2: partitions (by formula)
PARTITION_S = {
    "S-BD": ["B", "D", "q", "nb3mean_q", "nb3mean_B", "nb3min_q", "nb5mean_q", "rank_q", "rank_B", "itemmean_q", "itemmean_B", "itemsd_q", "itemsd_B", "itemz_q"],
    "S-s3": ["s3", "nb3mean_s3", "rank_s3", "itemmean_s3", "itemsd_s3"],
    "S-tbv": ["tbv", "nb3mean_tbv", "rank_tbv", "itemmean_tbv", "itemsd_tbv"],
    "S-ltex": ["ltex", "nb3mean_ltex", "itemmean_ltex", "itemsd_ltex"],
    "S-nbr": ["nbr", "nb3mean_nbr", "itemmean_nbr", "itemsd_nbr"],
    "S-pos": ["row", "col", "rad"],
}
PARTITION_F = {
    "F-token": ["B", "D", "q", "s3", "tbv", "ltex", "nbr"],
    "F-position": ["row", "col", "rad"],
    "F-neighbourhood": ["nb3mean_q", "nb3mean_B", "nb3mean_s3", "nb3mean_tbv", "nb3mean_ltex", "nb3mean_nbr", "nb3min_q", "nb5mean_q"],
    "F-rank": ["rank_q", "rank_B", "rank_s3", "rank_tbv"],
    "F-item": ["itemmean_q", "itemmean_B", "itemmean_s3", "itemmean_tbv", "itemmean_ltex", "itemmean_nbr",
               "itemsd_q", "itemsd_B", "itemsd_s3", "itemsd_tbv", "itemsd_ltex", "itemsd_nbr", "itemz_q"],
}


def cols_of(names) -> list[int]:
    return [FEATURES.index(n) for n in names]


def check_partition(part: dict) -> None:
    flat = [n for v in part.values() for n in v]
    if sorted(flat) != sorted(FEATURES) or len(flat) != len(set(flat)):
        raise ValueError("partition does not cover the 35 features exactly once")


check_partition(PARTITION_S)
check_partition(PARTITION_F)

# ================================================================================================ section 3: the variant list (fixed)
REFERENCES = ("NONE", "LRF")
BLOCK_3A = ("A-LIN", "A-S-BD", "A-S-s3", "A-S-tbv", "A-S-ltex", "A-S-nbr", "A-S-pos", "A-SF", "A-MIL", "A-UNL")
BLOCK_3B = ("KO-S-BD", "KO-S-s3", "KO-S-tbv", "KO-S-ltex", "KO-S-nbr", "KO-S-pos",
            "KO-F-token", "KO-F-position", "KO-F-neighbourhood", "KO-F-rank", "KO-F-item", "KO-ALL")
VARIANTS = BLOCK_3A + BLOCK_3B
FITTED = tuple(v for v in BLOCK_3A if v != "A-UNL")                 # 9 fitted variants
INTERVAL_ROWS = tuple(v for v in VARIANTS if v != "KO-ALL")         # 21 rows with intervals (SC-2)
HARNESS_LRF = "LRF-H"                                               # the LRF refit by the same harness (R0 and seed-spread)
SINGLE_SOURCE = {"A-S-BD": "S-BD", "A-S-s3": "S-s3", "A-S-tbv": "S-tbv", "A-S-ltex": "S-ltex", "A-S-nbr": "S-nbr", "A-S-pos": "S-pos"}
KNOCKOUT_GROUPS = {"KO-S-BD": PARTITION_S["S-BD"], "KO-S-s3": PARTITION_S["S-s3"], "KO-S-tbv": PARTITION_S["S-tbv"], "KO-S-ltex": PARTITION_S["S-ltex"],
                   "KO-S-nbr": PARTITION_S["S-nbr"], "KO-S-pos": PARTITION_S["S-pos"],
                   "KO-F-token": PARTITION_F["F-token"], "KO-F-position": PARTITION_F["F-position"], "KO-F-neighbourhood": PARTITION_F["F-neighbourhood"],
                   "KO-F-rank": PARTITION_F["F-rank"], "KO-F-item": PARTITION_F["F-item"], "KO-ALL": list(FEATURES)}
UNL_FEATURE = "rank_s3"                                             # A-UNL: w_j = 1 - rank_s3_j (plan 3a), fixed by the plan's author
assert len(VARIANTS) == 22 and len(FITTED) == 9 and len(INTERVAL_ROWS) == 21 and set(BLOCK_3B) == set(KNOCKOUT_GROUPS)

# ================================================================================================ section 4: cells and the seed slot
CELLS = (("L1", "clean"), ("L1", "jpeg10"), ("L1", "noise0.1"), ("L1", "splice128"),
         ("LG", "clean"), ("LG", "shot_noise3"), ("LG", "impulse_noise3"), ("LG", "speckle_noise3"))
CELL_NAMES = tuple(f"{r}_{c}" for r, c in CELLS)
ROOT_SEED_ANALYSIS, SPAWN_KEY = 20261028, (35,)
N_BOOT, LEVEL, LG_N = 10000, 0.95, 300


def cell_children() -> list[np.random.SeedSequence]:
    """One child per cell in the fixed cell order; spawn keys (35, 0..7)."""
    return np.random.SeedSequence(ROOT_SEED_ANALYSIS, spawn_key=SPAWN_KEY).spawn(len(CELLS))


def cell_index_matrix(cell: str, n: int, n_boot: int = N_BOOT) -> np.ndarray:
    """The cell's single n_boot x n index matrix (SC-3): drawn once, used for every row and both contrasts of that cell."""
    child = cell_children()[CELL_NAMES.index(cell)]
    return np.random.default_rng(child).integers(0, n, size=(n_boot, n))


def boot_ci_shared(diff: np.ndarray, idx: np.ndarray, level: float = LEVEL) -> list[float]:
    """Paired percentile bootstrap of the mean of per-item differences on a PRECOMPUTED index matrix (new function; a6_analysis.boot_ci draws its own indices). np.quantile at (1-level)/2 and 1-(1-level)/2."""
    diff = np.asarray(diff, float)
    means = diff[idx].mean(axis=1)
    lo, hi = np.quantile(means, [(1 - level) / 2, 1 - (1 - level) / 2])
    return [float(lo), float(hi)]


class CellBoot:
    """Common resamples for one cell: every call of `ci` in the cell uses the same index matrix."""

    def __init__(self, cell: str, n: int, n_boot: int = N_BOOT):
        self.cell, self.n = cell, n
        self.idx = cell_index_matrix(cell, n, n_boot)

    def ci(self, diff: np.ndarray) -> list[float]:
        if len(diff) != self.n:
            raise ValueError(f"cell {self.cell}: diff has {len(diff)} items, resamples were drawn for {self.n}")
        return boot_ci_shared(diff, self.idx)


# ================================================================================================ hashing, env record
def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha256_lf(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _code_record(rel: str) -> dict:
    p = ROOT / rel
    return dict(sha256=sha256_file(p), sha256_lf=sha256_lf(p))


def _code_matches(rel: str, rec: dict) -> bool:
    p = ROOT / rel
    return sha256_file(p) == rec["sha256"] or sha256_lf(p) == rec["sha256_lf"]


def arrays_digest(arr_dir: Path, n_items: int) -> str:
    """SHA-256 over the per-file SHA-256 values of item0000..item{n-1}.npz, in order (the formula of refreeze.arrays_digest)."""
    h = hashlib.sha256()
    for i in range(n_items):
        h.update(sha256_file(Path(arr_dir) / f"item{i:04d}.npz").encode())
    return h.hexdigest()


def write_env_lock(path: Path) -> None:
    """Environment record from importlib.metadata (the venv has no pip): every installed distribution with its version, then interpreter and thread facts."""
    dists = sorted({(d.metadata["Name"] or "").lower() + "==" + d.version for d in imd.distributions() if d.metadata["Name"]})
    head = [f"# python {sys.version.split()[0]} {platform.platform()}", f"# executable {sys.executable}",
            f"# torch {torch.__version__} numpy {np.__version__} threads torch={torch.get_num_threads()} OMP={os.environ.get('OMP_NUM_THREADS')} MKL={os.environ.get('MKL_NUM_THREADS')} OPENBLAS={os.environ.get('OPENBLAS_NUM_THREADS')}",
            f"# CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')!r}"]
    Path(path).write_text("\n".join(head + dists) + "\n", encoding="utf8")


def _git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


def git_head() -> str:
    return _git("rev-parse", "HEAD").stdout.strip()


def git_tracked_clean(path: Path) -> bool:
    """`path` is tracked and has no staged or unstaged change."""
    try:
        rel = os.path.relpath(Path(path).resolve(), ROOT).replace("\\", "/")
    except ValueError:                                                  # different drive: not in this repository
        return False
    if rel.startswith(".."):
        return False
    if _git("ls-files", "--error-unmatch", "--", rel).returncode != 0:
        return False
    return _git("status", "--porcelain", "--", rel).stdout.strip() == ""


# ================================================================================================ guarded array reader (no GATE field is ever read)
ALLOWED_FIELDS = ("B", "D", "s3", "tbv", "tex", "nbr", "delta")


class FieldGuard:
    """Mapping view of a stored item array that serves only `<cond>_<field>` with field in ALLOWED_FIELDS; anything else (flag*, z, codes, deltaL, y_gatem, ...) raises GateFieldRefused."""

    def __init__(self, npz):
        self._npz = npz
        self.accessed: list[str] = []

    @staticmethod
    def field_of(key: str) -> str:
        return key.rpartition("_")[2]

    def __getitem__(self, key: str):
        if self.field_of(key) not in ALLOWED_FIELDS:
            raise GateFieldRefused(f"field {key!r} is outside the allow-list {ALLOWED_FIELDS}: the ablation never reads GATE or any other field")
        self.accessed.append(key)
        return self._npz[key]

    def __contains__(self, key: str) -> bool:
        return self.field_of(key) in ALLOWED_FIELDS and key in self._npz


PRED_FIELDS = ("idx", "condition", "y_none", "y_lrf")


def read_prediction_controls(path: Path) -> dict[tuple[int, str], dict]:
    """predictions.jsonl of a fresh run: only idx, condition, y_none, y_lrf are retained (plan section 6 item 4)."""
    out = {}
    for line in Path(path).read_text(encoding="utf8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        out[(int(r["idx"]), r["condition"])] = {k: r[k] for k in PRED_FIELDS}
    return out


# ================================================================================================ families (subclass TorchFamily)
class GAMCols(fam.F1GAM):
    """F1 logistic-GAM on a column subset (the `cols` hook of TorchFamily); cols None = all 35. Same sample() as F1, so the 9 configuration draws are LRF's."""

    def __init__(self, name, cols=None, rmax=40, n_configs=9):
        super().__init__(name, rmax, n_configs)
        self.cols = None if cols is None else [int(c) for c in cols]


class GAMLin(GAMCols):
    """Linear logistic weight, 35 features: F1 with knots forced to 0 after the same draw (knots, ridge, lr)."""

    def sample(self, rng):
        return dict(super().sample(rng), knots=0)


class AttnNet(nn.Module):
    """Gated attention pooling in the style of Ilse et al. (ICML 2018): h = dropout(ReLU(W1 x + b1)); e = v^T (tanh(V h) * sigmoid(U h)); weights = softmax_j e. v is zero-initialised: training starts at NONE."""

    def __init__(self, n_feat: int, width: int, drop: float):
        super().__init__()
        self.enc = nn.Linear(n_feat, width)
        self.drop = nn.Dropout(drop)
        self.V = nn.Linear(width, width, bias=False)
        self.U = nn.Linear(width, width, bias=False)
        self.v = nn.Parameter(torch.zeros(width))

    def forward(self, x, codes=None):
        h = self.drop(F.relu(self.enc(x)))
        return (torch.tanh(self.V(h)) * torch.sigmoid(self.U(h))) @ self.v


def _train_attn(net, Xt, Dt, T, epochs, lr, wd, seed, batch=32):
    """`families._train_o1` with one change: the weight transform is a softmax over the tokens of the item-condition instead of a sigmoid."""
    g = torch.Generator().manual_seed(int(seed))
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=wd)
    n = Xt.shape[0]
    net.train()
    for _ in range(epochs):
        perm = torch.randperm(n, generator=g)
        for s in range(0, n, batch):
            b = perm[s:s + batch]
            w = torch.softmax(net(Xt[b]), dim=-1)
            d = Dt[b]
            m = (w * d).sum(-1) / w.sum(-1).clamp_min(1e-12)
            loss = F.softplus(-m / T).mean()
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
    net.eval()
    return net


class AttnMIL(fam.TorchFamily):
    """Attention-weighted pooling over the 35 caption-withheld features, in the style of gated attention MIL (an adaptation: the instance score is the fixed evidence Delta_j and the objective is O1)."""

    def __init__(self, name="A-MIL", rmax=40, n_configs=9):
        super().__init__(name, rmax, n_configs)

    def sample(self, rng):
        return dict(width=int(rng.choice([32, 64, 128])), drop=float(rng.choice([0.0, 0.1, 0.3])),
                    wd=fam.log_uniform(rng, 1e-6, 1e-2), lr=fam.log_uniform(rng, 3e-4, 3e-3))

    def build(self, cfg, Xt):
        return AttnNet(Xt.shape[-1], cfg["width"], cfg["drop"])

    def fit(self, ctx, cfg, train, resource, seed):
        torch.manual_seed(int(seed))
        mu, sd = fam.standardiser(ctx.X[train])
        Xt = self._x(ctx, train, mu, sd)
        Dt = torch.from_numpy(ctx.delta[train].reshape(-1, M))
        T = fam.temperature(ctx.delta[train])
        net = self.build(cfg, Xt)
        _train_attn(net, Xt, Dt, T, int(resource), cfg["lr"], cfg.get("wd", 0.0), seed)
        return dict(net=net, mu=mu, sd=sd)

    @torch.no_grad()
    def weights(self, ctx, model, items):
        Xt = self._x(ctx, items, model["mu"], model["sd"])
        out = [torch.softmax(model["net"](Xt[s:s + 64]), dim=-1).numpy() for s in range(0, Xt.shape[0], 64)]
        return np.concatenate(out).reshape(len(items), -1, M)


def make_family(vid: str, rmax: int = 40, n_cfg: int = 9, col: int | None = None):
    if vid == HARNESS_LRF:
        return GAMCols(vid, list(range(N_FEAT)), rmax, n_cfg)
    if vid == "A-LIN":
        return GAMLin(vid, None, rmax, n_cfg)
    if vid in SINGLE_SOURCE:
        return GAMCols(vid, cols_of(PARTITION_S[SINGLE_SOURCE[vid]]), rmax, n_cfg)
    if vid == "A-SF":
        if col is None:
            raise ValueError("A-SF needs the candidate column")
        return GAMCols(f"A-SF[{FEATURES[col]}]", [col], rmax, n_cfg)
    if vid == "A-MIL":
        return AttnMIL(vid, rmax, n_cfg)
    raise ValueError(f"no fitted family for {vid}")


# ================================================================================================ numpy models (inference; the form that is frozen)
def export_model(family, tm: dict) -> dict:
    """Torch fit -> plain-array model dict (kind 'gam' or 'attn'). float32 arrays as trained; cols are indices into the 35 engineered features."""
    cols = np.array(list(range(N_FEAT)) if family.cols is None else family.cols, dtype=np.int64)
    base = dict(mu=np.asarray(tm["mu"]), sd=np.asarray(tm["sd"]), cols=cols)
    net = tm["net"]
    if isinstance(net, AttnNet):
        return dict(base, kind="attn", W1=net.enc.weight.detach().numpy().copy(), b1=net.enc.bias.detach().numpy().copy(), V=net.V.weight.detach().numpy().copy(),
                    U=net.U.weight.detach().numpy().copy(), v=net.v.detach().numpy().copy())
    return dict(base, kind="gam", a=net.a.detach().numpy().copy(), b=net.b.detach().numpy().copy(), c=net.c.detach().numpy().copy(), knots=net.knots.numpy().copy())


def save_model(path: Path, model: dict) -> None:
    arrs = {k: np.asarray(v) for k, v in model.items() if k != "kind"}
    np.savez(path, kind=np.array(model["kind"]), feature_names=np.array([FEATURES[i] for i in model["cols"]]), **arrs)


def load_model(path: Path) -> dict:
    z = np.load(path)
    kind = str(z["kind"])
    keys = ("a", "b", "c", "knots", "mu", "sd", "cols") if kind == "gam" else ("W1", "b1", "V", "U", "v", "mu", "sd", "cols")
    out = {k: z[k] for k in keys}
    return dict({k: (v.astype(np.float64) if k != "cols" else v.astype(np.int64)) for k, v in out.items()}, kind=kind)


def frozen_model(fz: dict) -> dict:
    """The frozen LRF (from lrf_score.load_frozen) as a model dict over all 35 columns."""
    return dict(kind="gam", cols=np.arange(N_FEAT), **{k: np.asarray(fz[k], np.float64) for k in ("a", "b", "c", "knots", "mu", "sd")})


def _standardised(model: dict, Xc: np.ndarray, zero_cols=()) -> np.ndarray:
    cols = list(model["cols"])
    Xs = ((Xc[..., cols] - np.asarray(model["mu"], np.float64)) / np.asarray(model["sd"], np.float64)).astype(np.float64)
    pos = {c: i for i, c in enumerate(cols)}
    zi = [pos[z] for z in zero_cols if z in pos]
    if zi:
        Xs[..., zi] = 0.0                                               # a knocked-out feature is set to its design-item mean (zero after standardisation)
    return Xs


def model_weights(model: dict, X: np.ndarray, zero_cols=(), chunk: int = 16) -> np.ndarray:
    """Weights [..., M] (float64) of a model dict on engineered features X [..., M, 35]. zero_cols (indices into the 35) are set to the design-item mean after standardisation (knockouts)."""
    lead = X.shape[:-2]
    Xf = X.reshape(-1, X.shape[-2], X.shape[-1])
    out = np.empty(Xf.shape[:2], np.float64)
    for s in range(0, Xf.shape[0], chunk):
        Xs = _standardised(model, Xf[s:s + chunk], zero_cols)
        if model["kind"] == "gam":
            out[s:s + chunk] = 1.0 / (1.0 + np.exp(-gam_f(model, Xs)))
        else:
            h = np.maximum(Xs @ model["W1"].T + model["b1"], 0.0)
            gate = np.tanh(h @ model["V"].T) * (1.0 / (1.0 + np.exp(-(h @ model["U"].T))))
            e = gate @ model["v"]
            e = e - e.max(-1, keepdims=True)
            w = np.exp(e)
            out[s:s + chunk] = w / w.sum(-1, keepdims=True)
    return out.reshape(lead + (Xf.shape[1],))


def unl_weights(X: np.ndarray) -> np.ndarray:
    """A-UNL: w_j = 1 - rank_s3_j (within-item percentile rank of s3 from data._rank); weight 0 for the single rank-1 token, the sum is always positive."""
    return 1.0 - X[..., FEATURES.index(UNL_FEATURE)].astype(np.float64)


class Weighting:
    """One weighting of the tokens: NONE, the frozen LRF, a refitted model, A-UNL or a knockout of the frozen LRF."""

    def __init__(self, wid: str, kind: str, model: dict | None = None, zero_cols=()):
        self.id, self.kind, self.model, self.zero_cols = wid, kind, model, tuple(zero_cols)

    def weights(self, X: np.ndarray) -> np.ndarray:
        if self.kind == "none":
            return np.ones(X.shape[:-1], np.float64)
        if self.kind == "unl":
            return unl_weights(X)
        return model_weights(self.model, X, self.zero_cols)


# ================================================================================================ design-item loading (allow-listed fields only)
def raw_stack(arr_dir: Path, idxs, conds, items_cache=None) -> tuple[dict, np.ndarray]:
    """Raw caption-withheld scores [N, C, M] (built by lrf_score.raw_from_arrays per item and condition) and Delta [N, C, M] float32, read through the FieldGuard."""
    N, C = len(idxs), len(conds)
    raw = {k: np.zeros((N, C, M), np.float32) for k in data.RAW}
    delta = np.zeros((N, C, M), np.float32)
    for i, ix in enumerate(idxs):
        with np.load(Path(arr_dir) / f"item{int(ix):04d}.npz") as npz:
            g = FieldGuard(npz)
            for c, name in enumerate(conds):
                r = LS.raw_from_arrays(g, name)
                for k in data.RAW:
                    raw[k][i, c] = r[k][0, 0]
                delta[i, c] = np.asarray(g[f"{name}_delta"])
    if not np.isfinite(delta).all():
        raise NonFinite("non-finite Delta in the design arrays")
    return raw, delta


def load_design(arr_dir: Path, n_items: int = 500) -> SimpleNamespace:
    raw, delta = raw_stack(arr_dir, range(n_items), data.COND)
    return SimpleNamespace(X=data.engineer(raw), delta=delta)


# ================================================================================================ R0 and the design-item control
def _cfg_equal(a: dict, b: dict) -> bool:
    return set(a) == set(b) and all((int(a[k]) == int(b[k])) if isinstance(a[k], (int, np.integer)) and not isinstance(a[k], bool) else bool(np.isclose(a[k], b[k], rtol=1e-9, atol=0)) for k in a)


def r0_check(spec: dict, cfg: dict, inner_o1: float, w_harness: np.ndarray, w_frozen: np.ndarray, *, w_tol: float = 1e-5, o1_tol: float = 1e-6) -> dict:
    """R0 (plan section 6 item 1): same selected configuration and inner O1 as spec.json, and max |w_harness - w_frozen| <= w_tol over all design items x 4 conditions x tokens."""
    maxdiff = float(np.abs(np.asarray(w_harness, np.float64) - np.asarray(w_frozen, np.float64)).max())
    cfg_ok = _cfg_equal(cfg, spec["selected_cfg"])
    o1_diff = abs(float(inner_o1) - float(spec["inner_cv_o1"]))
    return dict(ok=bool(cfg_ok and o1_diff <= o1_tol and maxdiff <= w_tol), cfg_equal=cfg_ok, selected_cfg_harness=cfg, selected_cfg_frozen=spec["selected_cfg"],
                inner_o1_harness=float(inner_o1), inner_o1_frozen=float(spec["inner_cv_o1"]), inner_o1_abs_diff=o1_diff, o1_tol=o1_tol,
                max_abs_weight_diff=maxdiff, weight_tol=w_tol, n_weights=int(np.size(w_harness)))


def tie_tolerance_ok(delta: np.ndarray) -> bool:
    """KO-ALL float-tie rule (SC-4): a decision may differ from NONE's only if |sum_j Delta_j| <= 1e-9 * sum_j |Delta_j|."""
    d = np.asarray(delta, np.float64)
    return bool(abs(float(d.sum())) <= 1e-9 * float(np.abs(d).sum()))


def ko_all_control(frozen: dict, X: np.ndarray, delta: np.ndarray) -> dict:
    """KO-ALL (all 35 features at their design-item mean) against NONE on [N, C, M] arrays. The weights are constant within an item-condition, so the decision equals NONE's up to float rounding of a sum that is zero in
    exact arithmetic. Only counts of differing decisions are returned (no accuracy, no decision count, no margin)."""
    W = model_weights(frozen, X, zero_cols=range(N_FEAT))
    spread = float((W.max(-1) - W.min(-1)).max())
    n_diff = n_tie = n_bad = 0
    for i in range(W.shape[0]):
        for c in range(W.shape[1]):
            yk = decide(W[i, c], delta[i, c])["y"]
            yn = decide(np.ones(M), delta[i, c])["y"]
            if yk != yn:
                n_diff += 1
                if tie_tolerance_ok(delta[i, c]):
                    n_tie += 1
                else:
                    n_bad += 1
    return dict(n_item_conditions=int(W.shape[0] * W.shape[1]), max_within_item_condition_weight_spread=spread, n_decisions_differing_from_none=n_diff,
                n_differing_within_tie_tolerance=n_tie, n_differing_beyond_tolerance=n_bad, tolerance="|sum Delta| <= 1e-9 * sum |Delta|", ok=bool(n_bad == 0))


# ================================================================================================ fit stage
def select_column(scores: list[float]) -> int:
    """A-SF: the column with the smallest inner-fold O1; ties go to the first in feature order."""
    best = 0
    for j, s in enumerate(scores):
        if s < scores[best]:
            best = j
    return best


def _strip_acc(hl: dict) -> dict:
    for e in hl["log"]:
        e.pop("acc", None)                                              # inner-fold accuracy: computed inside successive_halving, never stored
    return hl


def _seed(s: int) -> int:
    return int(lrun.ss(4, FROZEN_KEY, 0, s).generate_state(1)[0])


def _jdump(path: Path, obj) -> None:
    Path(path).write_text(json.dumps(obj, indent=1), encoding="utf8")


def fit_variant(ctx, family, allit, vdir: Path, vid: str, extra_spec: dict, log, *, search=None) -> dict:
    """Search (successive halving, LRF's keys), final fits at seeds 0, 1, 2 with the seed-0 configuration, numpy-versus-torch weight check, files. `search` = (cfg, score, hl) when the search was already run (A-SF)."""
    t0 = time.time()
    cfg, score, hl = search if search is not None else lrun.successive_halving(ctx, family, allit, FROZEN_KEY, 0)
    t_search = time.time() - t0
    vdir.mkdir(parents=True, exist_ok=True)
    models, fit_secs = [], []
    chk = np.arange(0, ctx.X.shape[0], max(1, ctx.X.shape[0] // 20))
    maxdiff = 0.0
    for s in range(3):
        t1 = time.time()
        tm = family.fit(ctx, cfg, allit, family.rmax, _seed(s))
        models.append(export_model(family, tm))
        if s == 0:
            wt = family.weights(ctx, tm, chk)
            maxdiff = float(np.abs(model_weights(models[0], ctx.X[chk]) - wt).max())
        fit_secs.append(round(time.time() - t1, 1))
    save_model(vdir / "model.npz", models[0])
    save_model(vdir / "model_seed1.npz", models[1])
    save_model(vdir / "model_seed2.npz", models[2])
    T = fam.temperature(ctx.delta)
    _jdump(vdir / "selfcheck.json", dict(selfcheck_max_abs_diff_numpy_vs_torch=maxdiff, note="weights only on 20 design items x 4 conditions; no accuracy computed"))
    spec = dict(id=vid, label=LABEL, plan=PLAN, kind=models[0]["kind"], family=family.__class__.__name__, features=[FEATURES[i] for i in models[0]["cols"]], cols=[int(i) for i in models[0]["cols"]],
                n_features=int(len(models[0]["cols"])), n_items=int(ctx.X.shape[0]), T=T, selected_cfg=cfg, inner_cv_o1=float(score), epochs=int(family.rmax),
                seeds=dict(seed0=_seed(0), seed1=_seed(1), seed2=_seed(2), keys=dict(final_fit=[[4, FROZEN_KEY, 0, 0], [4, FROZEN_KEY, 0, 1], [4, FROZEN_KEY, 0, 2]])),
                hpo=dict(method="random search + synchronous successive halving, eta 3, %d configs, 3 inner folds over all %d design items; selection by mean inner-fold O1" % (family.n_configs, ctx.X.shape[0]),
                         seed_keys=dict(configs=[2, FROZEN_KEY, 0], inner_folds=[1, FROZEN_KEY], inner_fits=[3, FROZEN_KEY, 0, "ci", "ii"]), root_seed=lrun.ROOT_SEED),
                preprocessing="data.engineer on the design arrays -> columns of this variant -> (X - mu) / sd with mu, sd from the design items (restricted to the variant's columns)",
                inputs_never_used=["Delta", "Lambda", "captions", "z", "GATE flags", "condition identity"],
                selfcheck_max_abs_diff_numpy_vs_torch=maxdiff, sec=dict(search=round(t_search, 1), final_fits=fit_secs),
                model_sha256=sha256_file(vdir / "model.npz"), seed_models_sha256=dict(seed1=sha256_file(vdir / "model_seed1.npz"), seed2=sha256_file(vdir / "model_seed2.npz")),
                torch=torch.__version__, numpy=np.__version__, **extra_spec)
    _jdump(vdir / "hpo.json", _strip_acc(hl) if "log" in hl else hl)
    _jdump(vdir / "spec.json", spec)                                    # written last: its presence marks the variant as complete (--resume)
    log(f"[{time.strftime('%H:%M:%S')}] {vid}: inner O1 {score:.5f}, cfg {cfg}, search {t_search:.0f}s, final fits {fit_secs}s, numpy-vs-torch {maxdiff:.2e}")
    return dict(cfg=cfg, score=float(score), model=models[0], sec=round(time.time() - t0, 1))


def variants_record() -> dict:
    return dict(label=LABEL, plan=PLAN, order=list(VARIANTS), references=list(REFERENCES), fitted=list(FITTED), interval_rows=list(INTERVAL_ROWS), harness_lrf=HARNESS_LRF,
                n_variants=len(VARIANTS), n_intervals_K=len(INTERVAL_ROWS) * len(CELLS) * 2, features=FEATURES,
                partition_S={k: dict(features=v, cols=cols_of(v)) for k, v in PARTITION_S.items()}, partition_F={k: dict(features=v, cols=cols_of(v)) for k, v in PARTITION_F.items()},
                single_source={k: PARTITION_S[v] for k, v in SINGLE_SOURCE.items()}, knockouts={k: dict(features=v, cols=cols_of(v)) for k, v in KNOCKOUT_GROUPS.items()},
                a_unl=dict(rule="w_j = 1 - rank_s3_j", feature=UNL_FEATURE, col=FEATURES.index(UNL_FEATURE)), cells=list(CELL_NAMES),
                seed_slot=dict(root=ROOT_SEED_ANALYSIS, spawn_key=list(SPAWN_KEY), child_keys=[list(c.spawn_key) for c in cell_children()], n_boot=N_BOOT, level=LEVEL),
                fit_seed_keys=dict(root=lrun.ROOT_SEED, inner_folds=[1, FROZEN_KEY], configs=[2, FROZEN_KEY, 0], inner_fits=[3, FROZEN_KEY, 0, "ci", "ii"], final_fits=[[4, FROZEN_KEY, 0, s] for s in range(3)]))


def hash_dir(fit_dir: Path, spec_frozen: dict) -> dict:
    files = {str(p.relative_to(fit_dir)).replace("\\", "/"): sha256_file(p) for p in sorted(fit_dir.rglob("*")) if p.is_file() and p.name != "HASHES.json"}
    code = {rel: _code_record(rel) for rel in CODE_FILES}
    pinned = {f: spec_frozen["code_sha256"][f] for f in PINNED_FILES}
    return dict(label=LABEL, plan=PLAN, git_head_at_hash_time=git_head(), files=files, code=code, pinned_learned_ceiling=pinned,
                frozen=dict(model_sha256=spec_frozen["model_sha256"], rescored_arrays_digest=spec_frozen["rescored_arrays_digest"]),
                note="HASHES.json must be committed (code pin recorded) before the score stage; the score stage refuses unless it is tracked, unmodified and every hash matches")


def fit(src: Path, frozen: Path, out: Path, *, n_items: int = 500, rmax: int = 40, n_cfg: int = 9, resume: bool = False, log=print, only: tuple | None = None) -> dict:
    """The fit stage. `n_items`, `rmax` and `n_cfg` are the protocol's 500, 40 and 9 (the tests shrink them). `only` restricts the fitted variants (debugging; never for the real run)."""
    t_all = time.time()
    src, frozen, out = Path(src), Path(frozen), Path(out)
    fz = LS.load_frozen(frozen)                                         # verifies model.npz, the pinned code files, the feature list, caption_slot_len 13
    spec_f = fz["spec"]
    arr = src / "arrays"
    digest = arrays_digest(arr, n_items)
    if digest != spec_f["rescored_arrays_digest"]:
        raise FitRefused(f"the design arrays {arr} have digest {digest}, not the frozen LRF's rescored_arrays_digest {spec_f['rescored_arrays_digest']}")
    if out.exists() and not resume:
        raise FitRefused(f"{out} exists; the fit is written once (a defect is handled by a rerun beside it, plan section 0 item 1)")
    out.mkdir(parents=True, exist_ok=resume)
    write_env_lock(out / "env-lock.txt")
    cfg_rec = dict(label=LABEL, plan=PLAN, argv=sys.argv, src=str(src), frozen=str(frozen), out=str(out), n_items=n_items, rmax=rmax, n_cfg=n_cfg, resume=resume, only=list(only) if only else None,
                   git_head=git_head(), code=dict((rel, _code_record(rel)) for rel in CODE_FILES), plan_sha256=sha256_file(ROOT / PLAN) if (ROOT / PLAN).exists() else None,
                   rescored_arrays_digest=digest, torch=torch.__version__, numpy=np.__version__, python=sys.version.split()[0], torch_threads=torch.get_num_threads(),
                   started=time.strftime("%Y-%m-%d %H:%M:%S"))
    if not (out / "config.json").exists():
        _jdump(out / "config.json", cfg_rec)
    _jdump(out / "variants.json", variants_record())
    timing = json.loads((out / "timing.json").read_text()) if (out / "timing.json").exists() else {}

    def stamp(key, t0):
        timing[key] = round(time.time() - t0, 1)
        _jdump(out / "timing.json", timing)

    t0 = time.time()
    ctx = load_design(arr, n_items)
    stamp("load_and_engineer", t0)
    allit = np.arange(n_items)
    log(f"[{time.strftime('%H:%M:%S')}] design items loaded: X {ctx.X.shape}, {timing['load_and_engineer']}s")

    # ---- R0 first (plan section 6 item 1): the harness LRF (all 35 features, F1 space) against the frozen object
    r0_path = out / "R0.json"
    if not (out / HARNESS_LRF / "spec.json").exists():
        t0 = time.time()
        fam0 = make_family(HARNESS_LRF, rmax, n_cfg)
        cfg0, sc0, hl0 = lrun.successive_halving(ctx, fam0, allit, FROZEN_KEY, 0)
        tm0 = fam0.fit(ctx, cfg0, allit, fam0.rmax, _seed(0))
        w_h = fam0.weights(ctx, tm0, allit)
        w_f = model_weights(frozen_model(fz), ctx.X)
        r0 = r0_check(spec_f, cfg0, sc0, w_h, w_f)
        r0["seed_key"] = [4, FROZEN_KEY, 0, 0]
        r0["frozen_seed"] = spec_f["seed"]
        r0["harness_seed"] = _seed(0)
        _jdump(r0_path, r0)
        stamp("R0_search_and_fit", t0)
        log(f"[{time.strftime('%H:%M:%S')}] R0: ok={r0['ok']} cfg_equal={r0['cfg_equal']} inner O1 diff {r0['inner_o1_abs_diff']:.2e} max |w diff| {r0['max_abs_weight_diff']:.2e}")
        if not r0["ok"]:
            raise R0Failed(f"the harness did not reproduce the frozen LRF: {r0}")
        fit_variant(ctx, fam0, allit, out / HARNESS_LRF, HARNESS_LRF, dict(role="harness LRF refit (R0 and seed-spread); not the frozen LRF", r0=r0), log, search=(cfg0, sc0, hl0))
        stamp("LRF-H_total", t0)
    else:
        log("R0 / LRF-H already complete (resume)")

    # ---- the design-item control (KO-ALL = NONE), before any variant is fitted: counts only
    t0 = time.time()
    ko = ko_all_control(frozen_model(fz), ctx.X, ctx.delta)
    _jdump(out / "controls_design.json", dict(label=LABEL, KO_ALL_vs_NONE_design_items=ko, note="counts of differing decisions only; no accuracy, decision count or margin is stored on design items (plan section 6 item 2); "
                                              "the fresh-item controls (NONE = y_none, LRF = y_lrf, KO-ALL = NONE) are computed by the score stage before any variant weighting"))
    stamp("design_control_KO_ALL", t0)
    log(f"[{time.strftime('%H:%M:%S')}] design control KO-ALL vs NONE: {ko}")
    if not ko["ok"]:
        raise ControlMismatch(f"KO-ALL differs from NONE beyond the float-tie tolerance on design items: {ko}")

    # ---- the fitted variants (plan section 3a)
    todo = [v for v in BLOCK_3A if v != "A-UNL"]
    if only:
        todo = [v for v in todo if v in only]
    for vid in todo:
        vdir = out / vid
        if (vdir / "spec.json").exists():
            log(f"{vid}: complete (resume)")
            continue
        t0 = time.time()
        if vid == "A-SF":
            scores, searches = [], []
            for j in range(N_FEAT):
                famj = make_family("A-SF", rmax, n_cfg, col=j)
                res = lrun.successive_halving(ctx, famj, allit, FROZEN_KEY, 0)
                searches.append(res)
                scores.append(float(res[1]))
            j = select_column(scores)
            famj = make_family("A-SF", rmax, n_cfg, col=j)
            cand = {FEATURES[k]: dict(inner_cv_o1=scores[k], selected_cfg=searches[k][0], best=searches[k][2]["best"], rungs=searches[k][2]["rungs"], configs=searches[k][2]["configs"], log=_strip_acc(searches[k][2])["log"])
                    for k in range(N_FEAT)}
            vdir.mkdir(parents=True, exist_ok=True)
            hl = dict(candidates=cand, chosen=FEATURES[j], chosen_col=j, rule="smallest inner-fold O1 of the column's own successive-halving run; ties: first in feature order", n_searches=N_FEAT)
            _jdump(vdir / "candidates.json", hl)
            fit_variant(ctx, famj, allit, vdir, vid, dict(chosen_feature=FEATURES[j], candidate_inner_cv_o1={FEATURES[k]: scores[k] for k in range(N_FEAT)},
                                                           selection_budget="35 searches (35 times the frozen LRF's); no fresh item used"), log, search=(searches[j][0], searches[j][1], searches[j][2]))
        else:
            fit_variant(ctx, make_family(vid, rmax, n_cfg), allit, vdir, vid, {}, log)
        stamp(f"{vid}_total", t0)
    # A-UNL: no fitting; the rule is the whole object
    unl_dir = out / "A-UNL"
    unl_dir.mkdir(exist_ok=True)
    _jdump(unl_dir / "spec.json", dict(id="A-UNL", label=LABEL, plan=PLAN, kind="unlearned", rule="w_j = 1 - rank_s3_j", feature=UNL_FEATURE, col=FEATURES.index(UNL_FEATURE),
                                        note="no fitting, no standardisation, no design-item statistic; direction and rank transform fixed by the plan's author (plan 3a, SC-6 item 6); no model.npz"))
    timing["total_fit_stage_sec"] = round(time.time() - t_all, 1)
    _jdump(out / "timing.json", timing)
    H = hash_dir(out, spec_f)
    _jdump(out / "HASHES.json", H)
    log(f"[{time.strftime('%H:%M:%S')}] fit stage complete in {timing['total_fit_stage_sec']}s; HASHES.json lists {len(H['files'])} files")
    return dict(timing=timing, hashes=H)


# ================================================================================================ score stage (STAGE 2; code only in stage 1)
def verify_fit(fit_dir: Path, *, require_git: bool = True) -> dict:
    """HASHES.json: tracked and unmodified in git (unless require_git is off, tests only), every file hash, the code hashes (ablation.py, lrf_score.py) and the pinned learned-ceiling files must match."""
    fit_dir = Path(fit_dir)
    hp = fit_dir / "HASHES.json"
    if not hp.exists():
        raise HashMismatch(f"{hp} missing")
    if require_git and not git_tracked_clean(hp):
        raise HashMismatch(f"{hp} is not tracked and unmodified in git: commit it (code pin recorded) before the score stage")
    H = json.loads(hp.read_text(encoding="utf8"))
    for rel, want in H["files"].items():
        p = fit_dir / rel
        if not p.exists() or sha256_file(p) != want:
            raise HashMismatch(f"{p} does not match HASHES.json")
    for rel, rec in H["code"].items():
        if not _code_matches(rel, rec):
            raise HashMismatch(f"{rel} differs from the hash recorded at fit time")
    for f, want in H["pinned_learned_ceiling"].items():
        p = ROOT / "analysis_posthoc" / "learned_ceiling" / f
        if want not in (sha256_file(p), sha256_lf(p)):
            raise HashMismatch(f"{p} differs from the pinned {f}")
    return H


def verify_manifest(run_dir: Path) -> int:
    """Fresh arrays against arrays_manifest.json (n and every file's SHA-256). Reads the arrays' bytes (hashing only)."""
    run_dir = Path(run_dir)
    man = json.loads((run_dir / "arrays_manifest.json").read_text(encoding="utf8"))
    files = man["files"]
    if len(files) != man["n"]:
        raise HashMismatch(f"{run_dir}: manifest lists {len(files)} files for n = {man['n']}")
    for fn, want in files.items():
        p = run_dir / "arrays" / fn
        if not p.exists() or sha256_file(p) != want:
            raise HashMismatch(f"{p} does not match arrays_manifest.json")
    return int(man["n"])


def load_weightings(fit_dir: Path, fz: dict) -> tuple[list[Weighting], list[Weighting]]:
    """(the 24 weightings in plan order: NONE, LRF, 3a, 3b; the seed-spread weightings LRF-H s0..s2 then each fitted variant's s1, s2)."""
    fit_dir = Path(fit_dir)
    frozen = frozen_model(fz)
    main = [Weighting("NONE", "none"), Weighting("LRF", "gam", frozen)]
    for v in BLOCK_3A:
        if v == "A-UNL":
            main.append(Weighting(v, "unl"))
        else:
            m = load_model(fit_dir / v / "model.npz")
            main.append(Weighting(v, m["kind"], m))
    for v in BLOCK_3B:
        main.append(Weighting(v, "ko", frozen, cols_of(KNOCKOUT_GROUPS[v])))
    spread = [Weighting(f"{HARNESS_LRF}_s{s}", "gam", load_model(fit_dir / HARNESS_LRF / ("model.npz" if s == 0 else f"model_seed{s}.npz"))) for s in range(3)]
    for v in FITTED:
        for s in (1, 2):
            m = load_model(fit_dir / v / f"model_seed{s}.npz")
            spread.append(Weighting(f"{v}_s{s}", m["kind"], m))
    return main, spread


def _load_cell(run_dir: Path, cond: str, rows: list[dict], engineer) -> dict:
    idxs = [r["idx"] for r in rows if cond in r["conds"] and (run_dir / "arrays" / f"item{r['idx']:04d}.npz").exists()]
    raw, delta = raw_stack(run_dir / "arrays", idxs, (cond,))
    return dict(idx=np.array(idxs), X=engineer(raw)[:, 0], delta=delta[:, 0])


def image_overlap(l1_dir: Path, lg_dir: Path) -> dict:
    l1 = LS.committed_rows(l1_dir)
    lg = LS.committed_rows(lg_dir)[:LG_N]
    a, b = [r["image_id"] for r in l1], [r["image_id"] for r in lg]
    return dict(n_l1_items=len(a), n_lg_items=len(b), n_image_overlap=len(set(a) & set(b)), lg_image_ids_equal_first_n_of_l1=bool(a[:len(b)] == b),
                sentence="the eight cells are not independent samples")


def compute_controls(cells: dict, frozen: dict, preds: dict, out_dir: Path, overlap: dict) -> dict:
    """Plan section 6 item 5 / SC-4: recomputed NONE = y_none; LRF recomputed by this scorer = y_lrf; KO-ALL = NONE (float-tie tolerance). `preds[(cell, idx)]` holds y_none and y_lrf only.
    Written to controls.json BEFORE any variant weighting. A mismatch raises (after controls.json is written)."""
    res = dict(label=LABEL, NONE_vs_y_none=dict(n=0, n_mismatch=0), LRF_vs_y_lrf=dict(n=0, n_mismatch=0),
               KO_ALL_vs_NONE=dict(n=0, n_differing=0, n_differing_within_tie_tolerance=0, n_differing_beyond_tolerance=0), lg_l1_image_overlap=overlap, per_cell={})
    bad = []
    for cell, cd in cells.items():
        wl = model_weights(frozen, cd["X"])
        wk = model_weights(frozen, cd["X"], zero_cols=range(N_FEAT))
        res["per_cell"][cell] = dict(n=int(len(cd["idx"])))
        for k, ix in enumerate(cd["idx"]):
            delta = cd["delta"][k]
            yn = arm_y(delta, None)[0]
            yl = decide(wl[k], delta)["y"]
            yk = decide(wk[k], delta)["y"]
            p = preds.get((cell, int(ix)))
            if p is None:
                bad.append(f"{cell} item {ix}: no predictions row")
                continue
            res["NONE_vs_y_none"]["n"] += 1
            res["LRF_vs_y_lrf"]["n"] += 1
            res["KO_ALL_vs_NONE"]["n"] += 1
            if yn != p["y_none"]:
                res["NONE_vs_y_none"]["n_mismatch"] += 1
                bad.append(f"{cell} item {ix}: recomputed NONE {yn} != y_none {p['y_none']}")
            if yl != p["y_lrf"]:
                res["LRF_vs_y_lrf"]["n_mismatch"] += 1
                bad.append(f"{cell} item {ix}: scorer LRF {yl} != y_lrf {p['y_lrf']}")
            if yk != yn:
                res["KO_ALL_vs_NONE"]["n_differing"] += 1
                if tie_tolerance_ok(delta):
                    res["KO_ALL_vs_NONE"]["n_differing_within_tie_tolerance"] += 1
                else:
                    res["KO_ALL_vs_NONE"]["n_differing_beyond_tolerance"] += 1
                    bad.append(f"{cell} item {ix}: KO-ALL {yk} != NONE {yn} beyond the float-tie tolerance")
    res["ok"] = not bad
    res["mismatches"] = bad[:50]
    _jdump(Path(out_dir) / "controls.json", res)
    if bad:
        raise ControlMismatch(f"{len(bad)} control mismatches (first: {bad[0]}); controls.json written, no variant output exists")
    return res


def compute_variant_predictions(cells: dict, weightings: list[Weighting], out_path: Path) -> int:
    """predictions_ablation.jsonl: one line per item x cell x weighting with y and margin (decision rule imported from lrf_score)."""
    n = 0
    with open(out_path, "w", encoding="utf8") as f:
        for cell, cd in cells.items():
            for wt in weightings:
                W = wt.weights(cd["X"])
                for k, ix in enumerate(cd["idx"]):
                    if wt.kind == "none":
                        yn, mn = arm_y(cd["delta"][k], None)
                        y, margin = yn, mn
                    else:
                        r = decide(W[k], cd["delta"][k])
                        y, margin = r["y"], r["margin"]
                    f.write(json.dumps(dict(idx=int(ix), cell=cell, weighting=wt.id, y=int(y), margin=float(margin))) + "\n")
                    n += 1
    return n


def score(fit_dir: Path, l1_dir: Path, lg_dir: Path, out_dir: Path, *, frozen_dir: Path = FROZEN_DIR, require_git: bool = True, log=print) -> dict:
    fit_dir, l1_dir, lg_dir, out_dir = Path(fit_dir), Path(l1_dir), Path(lg_dir), Path(out_dir)
    if out_dir.exists():
        raise FitRefused(f"{out_dir} exists; the score stage runs once (plan section 6 item 6)")
    out_dir.mkdir(parents=True)
    write_env_lock(out_dir / "env-lock.txt")
    t0 = time.time()
    H = verify_fit(fit_dir, require_git=require_git)
    fz = LS.load_frozen(frozen_dir)
    n1, n2 = verify_manifest(l1_dir), verify_manifest(lg_dir)
    rows = {"L1": LS.committed_rows(l1_dir), "LG": LS.committed_rows(lg_dir)[:LG_N]}
    dirs = {"L1": l1_dir, "LG": lg_dir}
    cells = {f"{r}_{c}": _load_cell(dirs[r], c, rows[r], fz["engineer"]) for r, c in CELLS}
    empty = [k for k, v in cells.items() if len(v["idx"]) == 0]
    if empty:
        raise FitRefused(f"cells with no items: {empty}")
    log(f"cells loaded in {time.time() - t0:.0f}s: " + ", ".join(f"{k}={len(v['idx'])}" for k, v in cells.items()))
    preds = {}
    for r, d in dirs.items():                                           # y_none and y_lrf only; L1 and LG share item indices, so rows are keyed by cell
        for (i, c), v in read_prediction_controls(d / "predictions.jsonl").items():
            preds[(f"{r}_{c}", i)] = v
    controls = compute_controls(cells, frozen_model(fz), preds, out_dir, image_overlap(l1_dir, lg_dir))
    main, spread = load_weightings(fit_dir, fz)
    t1 = time.time()
    n_lines = compute_variant_predictions(cells, main + spread, out_dir / "predictions_ablation.jsonl")
    meta = dict(label=LABEL, fit_hashes_sha256=sha256_file(fit_dir / "HASHES.json"), n_manifest=dict(L1=n1, LG=n2), l1_dir=str(l1_dir), lg_dir=str(lg_dir), n_lines=n_lines,
                predictions_sha256=sha256_file(out_dir / "predictions_ablation.jsonl"), sec=dict(load=round(t1 - t0, 1), weightings=round(time.time() - t1, 1)), controls_ok=controls["ok"])
    _jdump(out_dir / "score_meta.json", meta)
    return meta


# ================================================================================================ analyse stage (STAGE 2)
def _expected_n(a6_l1: dict, a6_lg: dict, cell: str) -> int:
    run, cond = cell.split("_", 1)
    if run == "L1":
        key = {"clean": "L-NI", "jpeg10": "L3", "noise0.1": "L1", "splice128": "L4"}[cond]
        return int(a6_l1["family_L"][key]["n"])
    if cond == "clean":
        cells = a6_lg["family_LG"]["cells"]
        return int(next(c["clean_to_corrupted_drop_of_none"]["n"] for c in cells.values() if c.get("clean_to_corrupted_drop_of_none")))
    return int(a6_lg["family_LG"]["cells"][cond]["n"])


def load_ablation_predictions(path: Path) -> dict:
    """{weighting: {cell: (idx array, y array, margin array)}} sorted by idx."""
    tmp: dict = {}
    for line in Path(path).read_text(encoding="utf8").splitlines():
        if line.strip():
            r = json.loads(line)
            tmp.setdefault(r["weighting"], {}).setdefault(r["cell"], []).append((r["idx"], r["y"], r["margin"]))
    out = {}
    for w, cs in tmp.items():
        out[w] = {}
        for c, lst in cs.items():
            lst.sort()
            out[w][c] = (np.array([a for a, _, _ in lst]), np.array([b for _, b, _ in lst], float), np.array([m for _, _, m in lst], float))
    return out


def _contrast(yv: np.ndarray, yr: np.ndarray, boot: CellBoot) -> dict:
    d = yv - yr
    b, c = int(((yv > 0.5) & (yr < 0.5)).sum()), int(((yv < 0.5) & (yr > 0.5)).sum())
    return dict(d=float(d.mean()), ci95=boot.ci(d), b=b, c=c)


def analyse(score_dir: Path, a6_l1: Path | None = None, a6_lg: Path | None = None, out_path: Path | None = None) -> dict:
    """ablation_analysis.json in the section 3 row order; no sorting, no ranking, no interval-above/below-zero flag. d = variant minus reference; (b - c) / n."""
    score_dir = Path(score_dir)
    P = load_ablation_predictions(score_dir / "predictions_ablation.jsonl")
    controls = json.loads((score_dir / "controls.json").read_text(encoding="utf8"))
    if not controls["ok"]:
        raise ControlMismatch("controls.json is not ok: no analysis")
    meta_s = json.loads((score_dir / "score_meta.json").read_text(encoding="utf8"))
    a6 = None
    if a6_l1 is not None and a6_lg is not None:
        a6 = (json.loads(Path(a6_l1).read_text(encoding="utf8")), json.loads(Path(a6_lg).read_text(encoding="utf8")))
    n_cell = {}
    for cell in CELL_NAMES:
        ids = P["NONE"][cell][0]
        for wid, cs in P.items():
            if not np.array_equal(cs[cell][0], ids):
                raise ValueError(f"weighting {wid} cell {cell}: item set differs from NONE's")
        n_cell[cell] = int(len(ids))
        if a6 is not None and n_cell[cell] != _expected_n(a6[0], a6[1], cell):
            raise ValueError(f"cell {cell}: n = {n_cell[cell]} differs from a6_analysis.json ({_expected_n(a6[0], a6[1], cell)})")
    rows = {v: dict(id=v, block="3a" if v in BLOCK_3A else "3b", cells={}) for v in INTERVAL_ROWS}
    refs = {r: {} for r in REFERENCES}
    for cell in CELL_NAMES:
        boot = CellBoot(cell, n_cell[cell])
        yn, yl = P["NONE"][cell][1], P["LRF"][cell][1]
        refs["NONE"][cell] = float(yn.mean())
        refs["LRF"][cell] = float(yl.mean())
        for v in INTERVAL_ROWS:
            yv = P[v][cell][1]
            rows[v]["cells"][cell] = dict(acc=float(yv.mean()), vs_NONE=_contrast(yv, yn, boot), vs_LRF=_contrast(yv, yl, boot))
        del boot
    K = sum(2 for v in rows.values() for _ in v["cells"])
    spread = {}
    for v in (HARNESS_LRF,) + FITTED:
        ids = [f"{v}_s{s}" for s in range(3)] if v == HARNESS_LRF else [v, f"{v}_s1", f"{v}_s2"]
        spread[v] = {}
        for cell in CELL_NAMES:
            accs = [float(P[i][cell][1].mean()) for i in ids]
            spread[v][cell] = dict(acc_seed0_seed1_seed2=accs, mean=float(np.mean(accs)), sd_ddof1=float(np.std(accs, ddof=1)), range=float(max(accs) - min(accs)))
    max_range = max(s[c]["range"] for s in spread.values() for c in s)
    disagree = {cell: int((P[f"{HARNESS_LRF}_s0"][cell][1] != P["LRF"][cell][1]).sum()) for cell in CELL_NAMES}
    res = dict(meta=dict(label=LABEL, plan=PLAN, root_seed=ROOT_SEED_ANALYSIS, spawn_key=list(SPAWN_KEY), child_keys=[list(c.spawn_key) for c in cell_children()], cell_order=list(CELL_NAMES),
                         n_boot=N_BOOT, levels=[LEVEL], interval="paired percentile bootstrap, items resampled, shared per-cell index matrix", numpy_version=np.__version__,
                         sign="differences are variant minus reference; positive favours the variant", predictions_sha256=meta_s["predictions_sha256"]),
               n_per_cell=n_cell, K=K, K_expected=len(INTERVAL_ROWS) * len(CELLS) * 2, references_accuracy=refs, rows=list(rows.values()),
               ko_all_control=dict(note="exact-equality control, no interval", decisions_identical=bool(controls["KO_ALL_vs_NONE"]["n_differing"] == 0), **controls["KO_ALL_vs_NONE"]), controls_ok=controls["ok"], lg_l1_image_overlap=controls["lg_l1_image_overlap"],
               seed_spread=dict(rows=spread, max_range_over_variants_and_cells=max_range, seed0_is_prefixed=True, note="seed 0 is ss(4, 99, 0, 0), the pre-fixed seed, not the best of three; the extra seeds repeat only the final fit",
                                harness_lrf_seed0_vs_frozen_lrf_items_deciding_differently=disagree),
               mandatory_text_sc1="Each interval is a marginal 95% interval. {K} intervals were computed from the same images (variants x cells x two contrasts); they are positively dependent and no familywise or false-discovery adjustment was made. "
                                  "If every true difference were zero, about 5% of them (about {0.05 K}) would still exclude zero, and the count of intervals that exclude zero is not a calibrated tally because of the dependence. "
                                  "An interval that excludes zero is therefore a descriptive observation, not a finding; patterns across rows and cells are described, single intervals are not claims. "
                                  "The intervals cover item sampling only: refit-seed variation and design-item sampling are not in them.")
    out_path = Path(out_path) if out_path else score_dir / "ablation_analysis.json"
    _jdump(out_path, res)
    return res


# ================================================================================================ command line
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=LABEL)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit")
    f.add_argument("--src", default=str(ROOT / "runs" / "P2-LRF-RESCORE"))
    f.add_argument("--frozen", default=str(FROZEN_DIR))
    f.add_argument("--out", default=str(FIT_DIR))
    f.add_argument("--resume", action="store_true", help="skip variants whose spec.json exists (a variant is deterministic and independent of the others)")
    s = sub.add_parser("score")
    s.add_argument("--fit", default=str(FIT_DIR))
    s.add_argument("--l1", default=str(ROOT / "runs" / "P2-LRF-L1"))
    s.add_argument("--lg", default=str(ROOT / "runs" / "P2-LRF-LG"))
    s.add_argument("--out", default=str(SCORE_DIR))
    s.add_argument("--frozen", default=str(FROZEN_DIR))
    a_ = sub.add_parser("analyse")
    a_.add_argument("--score", default=str(SCORE_DIR))
    a_.add_argument("--a6-l1", default=None)
    a_.add_argument("--a6-lg", default=None)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "fit":
            fit(Path(a.src), Path(a.frozen), Path(a.out), resume=a.resume)
        elif a.cmd == "score":
            print(json.dumps(score(Path(a.fit), Path(a.l1), Path(a.lg), Path(a.out), frozen_dir=Path(a.frozen))))
        else:
            r = analyse(Path(a.score), a.a6_l1, a.a6_lg)
            print(json.dumps(dict(K=r["K"], n_per_cell=r["n_per_cell"])))
    except (FitRefused, R0Failed, ControlMismatch, GateFieldRefused, HashMismatch, NonFinite, FileNotFoundError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
