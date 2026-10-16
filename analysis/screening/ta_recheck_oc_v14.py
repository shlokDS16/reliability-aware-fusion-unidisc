"""Operating characteristics of the re-check reversal rule (criteria v1.4 section 5.2).

Same logic as analysis/screening/ta_recheck_oc.py (hypergeometric K given F; exact one-sided 95 percent upper
bound), with three changes for v1.4: the reversal rule is K >= 1 (acceptance number 0); the F grid adds the
tolerable loss L = 13 and its neighbours; a second table gives P(K >= k) when no title/abstract decision is
wrong (F = 0) but full-text screening includes sampled records in error at a per-record rate r (K ~ Binomial(n, r);
r is a hypothetical value, not an estimate).

The frozen frame is read, never written:
    python -I ta_recheck_oc_v14.py --frame <repo>/analysis/screening/ta-recheck-frame-v1.3-frozen.jsonl --out <file>
The frame digest is checked against the frozen value before anything is computed.
"""
import argparse
import hashlib
from math import comb
from pathlib import Path

FRAME_SHA256 = "a9180fe4bdb7956b8d8e6c4340559c94ac4f877cbc6376d1dad99995bb32d79a"
n = 100
K_STAR = 1
L = 13
F_GRID = [0, 1, 2, 4, 8, 10, 12, 13, 14, 16, 24, 32, 48]
R_GRID = [0.0, 0.0025, 0.005, 0.01, 0.02]


def pmf(k, N, F, n):
    if k < 0 or k > F or n - k > N - F:
        return 0.0
    return comb(F, k) * comb(N - F, n - k) / comb(N, n)


def p_at_least(k, N, F, n):
    return 1.0 - sum(pmf(j, N, F, n) for j in range(k))


def upper_bound(kobs, N, n, alpha=0.05):
    """Largest F with P(K <= kobs | F) > alpha (exact one-sided 1 - alpha upper bound)."""
    best = kobs
    for F in range(kobs, N + 1):
        if sum(pmf(j, N, F, n) for j in range(kobs + 1)) > alpha:
            best = F
        else:
            break
    return best


def binom_at_least(k, n, r):
    return 1.0 - sum(comb(n, j) * r ** j * (1 - r) ** (n - j) for j in range(k))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    raw = Path(a.frame).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != FRAME_SHA256:
        raise SystemExit(f"frame sha256 {digest} is not the frozen {FRAME_SHA256}; stopping")
    N = sum(1 for l in raw.decode("utf-8").splitlines() if l.strip())
    lines = [f"ta_recheck_oc_v14.py: N = {N} candidates (frozen frame sha256 {digest}), n = {n} sampled,"
             f" reversal if K >= {K_STAR}; tolerable loss L = {L}", ""]
    lines.append("P(K >= k | F), hypergeometric, for k = 1, 2, 3")
    lines.append("F\tk>=1\tk>=2\tk>=3")
    for F in F_GRID:
        lines.append(f"{F}\t{p_at_least(1, N, F, n):.3f}\t{p_at_least(2, N, F, n):.3f}\t{p_at_least(3, N, F, n):.3f}")
    lines.append("")
    lines.append("K\tF_hat = K*N/n\texact one-sided 95% upper bound for F")
    for k in range(4):
        lines.append(f"{k}\t{k * N / n:.1f}\t{upper_bound(k, N, n)}")
    lines.append("")
    lines.append("F = 0, full-text false inclusions at hypothetical per-record rate r: P(K >= k), K ~ Binomial(n, r)")
    lines.append("r\tk>=1\tk>=2\tk>=3")
    for r in R_GRID:
        lines.append(f"{r}\t{binom_at_least(1, n, r):.3f}\t{binom_at_least(2, n, r):.3f}\t{binom_at_least(3, n, r):.3f}")
    text = "\n".join(lines) + "\n"
    Path(a.out).write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
