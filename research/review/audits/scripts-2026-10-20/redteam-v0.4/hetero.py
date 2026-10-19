"""Red-team scratch: design B-IP and fixed-n gates when the ICC differs between metrics. Imports committed code read-only.
Run from the worktree root: python -u -E -P hetero.py <scenario> <reps>"""
import importlib.util, sys, time
import numpy as np
from scipy import stats
ROOT = "analysis/extraction/"


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT + name + ".py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = load("gate_adaptive_v04")
G = A.G
I = A.I


NBK = [1.5]


def gen(rng, levels, icc, nb_k=None):
    nb_k = NBK[0] if nb_k is None else nb_k
    ic = (lambda k: icc.get(k, icc.get("_", 0.10))) if isinstance(icc, dict) else (lambda k: icc)
    n = 3 * A.PER_MAX
    D, matched, raw = {}, {}, {}
    for name in G.ORDER_G + [k for k in G.NAMES if k not in G.ORDER_G]:
        kind, size, _, bad, block = G.Q[name]
        p = levels[name]
        u = stats.norm.cdf(rng.standard_normal(n))
        if kind == "ratio":
            m = G.counts(rng, size, n, nb_k)
            x = rng.binomial(m, G.beta_from_u(u, p, ic(name)))
            D[name], raw[name] = (x.astype(float), m.astype(float)), (x, m)
        elif kind == "f1":
            U = G.counts(rng, size, n, nb_k)
            both = rng.binomial(U, G.beta_from_u(u, p / (2 - p), ic(name)))
            matched[name] = both
            D[name], raw[name] = (2.0 * both, (U + both).astype(float)), (both, U)
        elif kind in ("onG", "onK"):
            m = matched["G4 F1_G" if kind == "onG" else "G4 F1_K"]
            x = rng.binomial(m, G.beta_from_u(u, p, ic(name)))
            D[name], raw[name] = (x.astype(float), m.astype(float)), (x, m)
        elif kind == "kappa":
            a = G.beta_from_u(u, np.sqrt(p), ic(name))[:, None]
            T = (rng.random((n, size, 1)) > G.QA_MARG.cumsum(1)[None]).sum(-1)

            def rate():
                e = (rng.random((n, size, 1)) > G.QA_MARG.cumsum(1)[None]).sum(-1)
                return np.where(rng.random((n, size)) < a, T, e)
            X, Y = rate(), rate()
            oh = np.zeros((n, size, 9), np.int16)
            np.put_along_axis(oh, (3 * X + Y)[..., None], 1, -1)
            D[name] = ("kappa", oh)
        elif kind == "count":
            D[name] = ("count", u < p)
    return D, raw


def run(levels, icc, reps, seed, grid, rn, fixed=None, crit=None):
    rng = np.random.default_rng(seed)
    passed, cpass, ns, uns = [], [], [], []
    for r in range(reps):
        D, raw = gen(rng, levels, icc)
        if fixed is None:
            S1 = A.sel(A.PER_1)
            xs = [raw[k][0][S1] for k in A.ICC_METRICS]
            ms = [raw[k][1][S1] for k in A.ICC_METRICS]
            un, _ = I.upper80_neyman(xs, ms, rng, R=rn)
            n = I.n_required(un, grid) or 120
            uns.append(un)
        else:
            n = fixed
        ns.append(n)
        o = A.evaluate(D, n // 3, rng)
        passed.append(o.all())
        if crit:
            cpass.append(o[G.NAMES.index(crit)])
    return np.mean(passed), (np.mean(cpass) if crit else None), np.array(ns), (np.median(uns) if uns else None)


if __name__ == "__main__":
    grid = I.read_grid(ROOT + "gate_oc_v04-log.txt")
    which = sys.argv[1]
    reps = int(sys.argv[2])
    if len(sys.argv) > 3:
        NBK[0] = float(sys.argv[3])
        print('NB shape', NBK[0])
    t0 = time.time()
    lv = G.levels_with
    LQ = {k: 0.4 for k in G.NAMES if G.Q[k][4] == "LQ" or k.startswith("G1")}
    S = {
        "H1": ("good; M-sign, M-pool ICC 0.5, others 0.10", lv(), {"G4 M-sign": 0.5, "G4 M-pool": 0.5, "_": 0.10}, None),
        "H2": ("good; F1_G ICC 0.40, others 0.10", lv(), {"G4 F1_G": 0.4, "_": 0.10}, None),
        "H3": ("good; M-anchorG ICC 0.40, others 0.05", lv(), {"G4 M-anchorG": 0.4, "_": 0.05}, None),
        "H4": ("M-sign bad, ICC 0.5 on M-sign and M-pool, others 0.10", lv(bad="G4 M-sign"),
               {"G4 M-sign": 0.5, "G4 M-pool": 0.5, "_": 0.10}, "G4 M-sign"),
        "H5": ("M-pool bad, ICC 0.5 on M-sign and M-pool, others 0.10", lv(bad="G4 M-pool"),
               {"G4 M-sign": 0.5, "G4 M-pool": 0.5, "_": 0.10}, "G4 M-pool"),
        "H7": ("F1_G bad, ICC 0.10 all", lv(bad="G4 F1_G"), 0.10, "G4 F1_G"),
        "H8": ("M-val bad, ICC 0.10 all", lv(bad="G4 M-val"), 0.10, "G4 M-val"),
        "H9": ("F1_K bad, ICC 0.10 all", lv(bad="G4 F1_K"), 0.10, "G4 F1_K"),
        "H10": ("good; M-sign, M-pool 0.6, M-anchorG 0.3, others 0.10", lv(), {"G4 M-sign": 0.6, "G4 M-pool": 0.6, "G4 M-anchorG": 0.3, "_": 0.10}, None),
        "H11": ("good; ICC 0.10 all (use NB shape arg)", lv(), 0.10, None),
        "H12": ("F1_K bad; ICC 0.10 all (use NB shape arg)", lv(bad="G4 F1_K"), 0.10, "G4 F1_K"),
        "H6": ("good; L/Q/H and G1 criteria ICC 0.40, eight count metrics 0.05", lv(), {**LQ, "_": 0.05}, None),
    }
    SEEDS = {"H1": 20269100, "H2": 20269200, "H3": 20269300, "H4": 20269400, "H5": 20269500, "H6": 20269600, "H7": 20269700, "H8": 20269800, "H9": 20269900, "H10": 20268000, "H11": 20268100, "H12": 20268200}
    lab, levels, icc, crit = S[which]
    for mode in ("bip", 60, 120):
        p, cp, ns, um = run(levels, icc, reps, SEEDS[which] + (0 if mode == "bip" else mode), grid, 200,
                            fixed=None if mode == "bip" else mode, crit=crit)
        dist = " ".join(f"{n}:{np.mean(ns == n):.2f}" for n in (60, 72, 90, 105, 120))
        print(f"{which} [{lab}] mode {mode}: P(pass) {p:.3f}" + (f"; P({crit} passes) {cp:.3f}" if crit else "")
              + f"; n dist {dist}; mean n {ns.mean():.1f}" + (f"; median U_N {um:.2f}" if um is not None else ""), flush=True)
    print("elapsed", round(time.time() - t0))
