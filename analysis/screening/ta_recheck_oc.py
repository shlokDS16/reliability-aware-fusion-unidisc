"""Operating characteristics of the re-check reversal rule (criteria v1.3 section 5).

Frame: the N candidates in analysis/screening/ta-recheck-candidates-v1.2.jsonl (title/abstract exclusions
selected by ta_recheck_select.py). A simple random sample of n = 100 is screened at full text; K is the
number of sampled records included after blind adjudication ("flips"). F is the unknown number of flips
in the whole frame. K is hypergeometric(N, F, n).

Reversal rule (fixed before any re-check record is screened): screen the whole frame at full text if
K >= K_STAR. This script reports P(K >= k | F) for k = 1, 2, 3 and F in F_GRID, the point estimate
F_hat = K * N / n, and the exact one-sided 95 percent upper bound for F given K = 0..3.

    python analysis/screening/ta_recheck_oc.py

Writes analysis/screening/ta-recheck-oc-v1.3.txt.
"""
import json
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANDS = ROOT / "analysis" / "screening" / "ta-recheck-frame-v1.3-frozen.jsonl"
OUT = ROOT / "analysis" / "screening" / "ta-recheck-oc-v1.3.txt"
n = 100
K_STAR = 2
F_GRID = [0, 1, 2, 4, 8, 12, 16, 24, 32, 48]


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


def main():
    with open(CANDS, encoding="utf-8") as f:
        N = sum(1 for l in f if l.strip())
    lines = [f"ta_recheck_oc.py: N = {N} candidates, n = {n} sampled, reversal if K >= {K_STAR}", ""]
    lines.append("P(K >= k | F) for k = 1, 2, 3")
    lines.append("F\tk>=1\tk>=2\tk>=3")
    for F in F_GRID:
        lines.append(f"{F}\t{p_at_least(1, N, F, n):.3f}\t{p_at_least(2, N, F, n):.3f}\t{p_at_least(3, N, F, n):.3f}")
    lines.append("")
    lines.append("K\tF_hat = K*N/n\texact one-sided 95% upper bound for F")
    for k in range(4):
        lines.append(f"{k}\t{k * N / n:.1f}\t{upper_bound(k, N, n)}")
    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
