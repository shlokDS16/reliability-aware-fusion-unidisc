"""Model families F1-F4 and the detector (plan Sections 4, 5, 9). Inputs are caption-withheld features only; Delta is used
only as the training signal (O1 margin or O2 target) and never as an input to a weight model."""
from __future__ import annotations

import math

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

from .data import GRID, M, RAW

N_CODES = 16384


# ---------------------------------------------------------------- shared helpers
def o1_criterion(w: np.ndarray, delta: np.ndarray, T: float) -> float:
    """Mean softplus(-M/T), M = weighted mean of Delta per item-condition. w, delta: [..., M]."""
    s = w.sum(-1)
    m = np.where(s > 0, (w * delta).sum(-1) / np.maximum(s, 1e-12), 0.0)
    return float(np.mean(np.logaddexp(0.0, -m / T)))


def temperature(delta_train: np.ndarray) -> float:
    """T = median |NONE margin| over the training item-conditions (plan Section 4, O1)."""
    return float(np.median(np.abs(delta_train.mean(-1))))


def standardiser(X_train: np.ndarray):
    flat = X_train.reshape(-1, X_train.shape[-1])
    mu = flat.mean(0, dtype=np.float64).astype(np.float32)
    sd = flat.std(0, dtype=np.float64).astype(np.float32)
    sd[sd < 1e-6] = 1.0
    return mu, sd


def log_uniform(rng, lo, hi):
    return float(math.exp(rng.uniform(math.log(lo), math.log(hi))))


# ---------------------------------------------------------------- torch families (O1)
class GAMNet(nn.Module):
    """f = b + sum_k (a_k x_k + sum_m c_km relu(x_k - t_km)); zero init, so training starts at NONE."""

    def __init__(self, knots: torch.Tensor | None, n_feat: int):
        super().__init__()
        self.a = nn.Parameter(torch.zeros(n_feat))
        self.b = nn.Parameter(torch.zeros(()))
        self.register_buffer("knots", knots if knots is not None else torch.zeros(n_feat, 0))
        self.c = nn.Parameter(torch.zeros(n_feat, self.knots.shape[1]))

    def forward(self, x, codes=None):
        f = x @ self.a + self.b
        if self.knots.shape[1]:
            f = f + torch.einsum("bmfk,fk->bm", F.relu(x[..., None] - self.knots), self.c)
        return f

    def penalty(self):
        return (self.a ** 2).sum() + (self.c ** 2).sum()


class MLPNet(nn.Module):
    def __init__(self, n_feat, width, drop):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(n_feat, width), nn.ReLU(), nn.Dropout(drop), nn.Linear(width, width), nn.ReLU(),
                                 nn.Dropout(drop), nn.Linear(width, 1))
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def forward(self, x, codes=None):
        return self.net(x).squeeze(-1)


class GridNet(nn.Module):
    """Token embedding (raw scores + code embedding + learned position) -> 2 residual 3x3 convs (local) -> 4x4 pool to 64 patch
    tokens + item token -> 2 transformer layers (global) -> [local, patch, item] -> MLP head. Zero-init head: starts at NONE."""

    def __init__(self, n_in, d, drop):
        super().__init__()
        self.inp = nn.Linear(n_in, d)
        self.code = nn.Embedding(N_CODES, 8)
        self.code_p = nn.Linear(8, d, bias=False)
        self.pos = nn.Parameter(torch.randn(M, d) * 0.02)
        self.norm = nn.LayerNorm(d)
        self.conv1 = nn.Conv2d(d, d, 3, padding=1)
        self.conv2 = nn.Conv2d(d, d, 3, padding=1)
        self.item_tok = nn.Parameter(torch.zeros(1, 1, d))
        layer = nn.TransformerEncoderLayer(d, 4, 2 * d, drop, batch_first=True, norm_first=True)
        self.enc = nn.TransformerEncoder(layer, 2, enable_nested_tensor=False)
        self.head = nn.Sequential(nn.Linear(3 * d, d), nn.GELU(), nn.Dropout(drop), nn.Linear(d, 1))
        nn.init.zeros_(self.head[-1].weight)
        nn.init.zeros_(self.head[-1].bias)
        self.d = d

    def forward(self, x, codes):
        B, d = x.shape[0], self.d
        h = self.norm(self.inp(x) + self.code_p(self.code(codes)) + self.pos)
        g = h.transpose(1, 2).reshape(B, d, GRID, GRID)
        g = g + F.gelu(self.conv1(g))
        g = g + F.gelu(self.conv2(g))
        p = F.avg_pool2d(g, 4)                                                   # [B, d, 8, 8]
        t = p.flatten(2).transpose(1, 2)                                          # [B, 64, d]
        t = self.enc(torch.cat([self.item_tok.expand(B, -1, -1) + t.mean(1, keepdim=True), t], 1))
        item, patch = t[:, :1], t[:, 1:]
        up = patch.transpose(1, 2).reshape(B, d, 8, 8).repeat_interleave(4, 2).repeat_interleave(4, 3)
        z = torch.cat([g.flatten(2).transpose(1, 2), up.flatten(2).transpose(1, 2), item.expand(-1, M, -1)], -1)
        return self.head(z).squeeze(-1)


def _train_o1(net, Xt, Dt, Ct, T, epochs, lr, wd, seed, ridge=0.0, batch=32):
    g = torch.Generator().manual_seed(int(seed))
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=wd)
    n = Xt.shape[0]
    net.train()
    for _ in range(epochs):
        perm = torch.randperm(n, generator=g)
        for s in range(0, n, batch):
            b = perm[s:s + batch]
            w = torch.sigmoid(net(Xt[b], None if Ct is None else Ct[b]))
            d = Dt[b]
            m = (w * d).sum(-1) / w.sum(-1).clamp_min(1e-12)
            loss = F.softplus(-m / T).mean()
            if ridge:
                loss = loss + ridge * net.penalty()
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
    net.eval()
    return net


class TorchFamily:
    uses_codes = False
    cols = None                     # None = all engineered columns

    def __init__(self, name, rmax, n_configs=9):
        self.name, self.rmax, self.n_configs = name, rmax, n_configs

    def _x(self, ctx, items, mu, sd):
        X = ctx.X[items] if self.cols is None else ctx.X[items][..., self.cols]
        X = (X - mu) / sd
        return torch.from_numpy(np.ascontiguousarray(X.reshape(-1, M, X.shape[-1]), dtype=np.float32))

    def fit(self, ctx, cfg, train, resource, seed):
        torch.manual_seed(int(seed))
        Xtr = ctx.X[train] if self.cols is None else ctx.X[train][..., self.cols]
        mu, sd = standardiser(Xtr)
        Xt = self._x(ctx, train, mu, sd)
        Dt = torch.from_numpy(ctx.delta[train].reshape(-1, M))
        Ct = torch.from_numpy(ctx.codes[train].reshape(-1, M)) if self.uses_codes else None
        T = temperature(ctx.delta[train])
        net = self.build(cfg, Xt)
        ridge = cfg.get("ridge", 0.0)
        _train_o1(net, Xt, Dt, Ct, T, int(resource), cfg["lr"], cfg.get("wd", 0.0), seed, ridge=ridge)
        return dict(net=net, mu=mu, sd=sd)

    @torch.no_grad()
    def weights(self, ctx, model, items):
        Xt = self._x(ctx, items, model["mu"], model["sd"])
        Ct = torch.from_numpy(ctx.codes[items].reshape(-1, M)) if self.uses_codes else None
        out = []
        for s in range(0, Xt.shape[0], 64):
            out.append(torch.sigmoid(model["net"](Xt[s:s + 64], None if Ct is None else Ct[s:s + 64])).numpy())
        return np.concatenate(out).reshape(len(items), -1, M)


class F1GAM(TorchFamily):
    def sample(self, rng):
        return dict(knots=int(rng.choice([0, 4, 8])), ridge=log_uniform(rng, 1e-5, 1e-1), lr=log_uniform(rng, 3e-3, 3e-2))

    def build(self, cfg, Xt):
        K = cfg["knots"]
        knots = None
        if K:
            flat = Xt.reshape(-1, Xt.shape[-1])
            sub = flat[torch.randperm(flat.shape[0])[:200000]]
            qs = torch.tensor([(k + 1) / (K + 1) for k in range(K)])
            knots = torch.quantile(sub, qs, dim=0).T.contiguous()          # [F, K]
        return GAMNet(knots, Xt.shape[-1])


class F3MLP(TorchFamily):
    def sample(self, rng):
        return dict(width=int(rng.choice([32, 64, 128])), drop=float(rng.choice([0.0, 0.1, 0.3])),
                    wd=log_uniform(rng, 1e-6, 1e-2), lr=log_uniform(rng, 3e-4, 3e-3))

    def build(self, cfg, Xt):
        return MLPNet(Xt.shape[-1], cfg["width"], cfg["drop"])


class F4Grid(TorchFamily):
    uses_codes = True
    cols = list(range(len(RAW)))

    def sample(self, rng):
        return dict(d=int(rng.choice([16, 32, 48])), drop=float(rng.choice([0.0, 0.1, 0.2])),
                    wd=log_uniform(rng, 1e-5, 1e-2), lr=log_uniform(rng, 3e-4, 3e-3))

    def build(self, cfg, Xt):
        return GridNet(Xt.shape[-1], cfg["d"], cfg["drop"])


# ---------------------------------------------------------------- GBT SNR plug-in (O2)
def _extra(ctx, items, kind):
    """Extra columns for the labelled variants: 'cond' (condition one-hot) and 'z' (oracle: one-hot + z)."""
    n = len(items)
    if kind is None:
        return None
    oh = np.broadcast_to(np.eye(4, dtype=np.float32)[None, :, None, :], (n, 4, M, 4))
    if kind == "cond":
        return oh
    if kind == "z":
        return np.concatenate([oh, ctx.z[items][..., None].astype(np.float32)], -1)
    raise ValueError(kind)


class F2GBT:
    def __init__(self, name="F2", rmax=450, n_configs=9, extra=None):
        self.name, self.rmax, self.n_configs, self.extra = name, rmax, n_configs, extra

    def sample(self, rng):
        return dict(learning_rate=log_uniform(rng, 0.02, 0.2), max_leaf_nodes=int(rng.choice([15, 31, 63])),
                    min_samples_leaf=int(rng.choice([100, 400, 1600])), l2_regularization=log_uniform(rng, 1e-3, 10.0))

    def _X(self, ctx, items, mask=None):
        X = ctx.X[items]
        e = _extra(ctx, items, self.extra)
        if e is not None:
            X = np.concatenate([X, e], -1)
        return X[mask] if mask is not None else X.reshape(-1, X.shape[-1])

    def fit(self, ctx, cfg, train, resource, seed):
        mask = ctx.mask[train]
        Xr = self._X(ctx, train, mask)
        y = ctx.delta[train][mask]
        kw = dict(cfg, max_iter=int(resource), early_stopping=False, random_state=int(seed) % (2 ** 31))
        mu = HistGradientBoostingRegressor(loss="squared_error", **kw).fit(Xr, y)
        r2 = (y - mu.predict(Xr)) ** 2
        v = HistGradientBoostingRegressor(loss="poisson", **kw).fit(Xr, r2)
        return dict(mu=mu, v=v)

    def weights(self, ctx, model, items):
        Xa = self._X(ctx, items)
        w = np.maximum(model["mu"].predict(Xa), 0.0) / np.maximum(model["v"].predict(Xa), 1e-4)
        return w.reshape(len(items), -1, M)


# ---------------------------------------------------------------- detector (secondary)
def fit_detector(ctx, train, seed):
    mask = ctx.mask[train]
    clf = HistGradientBoostingClassifier(learning_rate=0.1, max_leaf_nodes=31, max_iter=300, early_stopping=True,
                                         validation_fraction=0.1, random_state=int(seed) % (2 ** 31))
    return clf.fit(ctx.X[train][mask], ctx.z[train][mask])


def detector_proba(ctx, clf, items):
    return clf.predict_proba(ctx.X[items].reshape(-1, ctx.X.shape[-1]))[:, 1].reshape(len(items), -1, M)
