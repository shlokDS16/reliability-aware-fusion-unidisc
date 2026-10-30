"""Added at writing (2026-10-30), descriptive only (SPEC v2 section 5, red-team RS-11, statistician concern 3): an exact
Clopper-Pearson 95 percent interval for the discordance rate n_d / n of each family-P corruption. Because |b - c| <= b + c, the
upper limit also bounds the absolute net accuracy change |b - c| / n in the population of paired decisions. Reads only the committed
runs/P2-GATE-M4/analysis.json; stdlib only; deterministic. Not a preregistered quantity; listed in the deviations box."""
import hashlib, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "runs/P2-GATE-M4/analysis.json"
OUT = ROOT / "runs/P2-PAPER-BOUNDS/p_exact_bounds.json"

def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k + 1))

def solve(f, lo=0.0, hi=1.0):
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    return (lo + hi) / 2

def clopper_pearson(k, n, alpha=0.05):
    lo = 0.0 if k == 0 else solve(lambda p: alpha / 2 - (1 - binom_cdf(k - 1, n, p)))   # P(X >= k) = alpha/2
    hi = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p) - alpha / 2)            # P(X <= k) = alpha/2
    return lo, hi

a = json.loads(SRC.read_text(encoding="utf8"))
res = {}
for corr, v in a["primary"]["per_corruption"].items():
    lo, hi = clopper_pearson(int(v["n_d"]), int(v["n"]))
    res[corr] = dict(n=v["n"], n_d=v["n_d"], b=v["b"], c=v["c"], cp95_discordance=[round(lo, 6), round(hi, 6)],
                     bound_abs_net_change_95=round(hi, 6))
meta = dict(label="added at writing, descriptive; not preregistered", source=str(SRC.relative_to(ROOT)),
            source_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest(),
            script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), method="Clopper-Pearson exact, two-sided 95 percent")
OUT.write_text(json.dumps(dict(meta=meta, per_corruption=res), indent=1, sort_keys=True), encoding="utf8")
print(json.dumps(res))
