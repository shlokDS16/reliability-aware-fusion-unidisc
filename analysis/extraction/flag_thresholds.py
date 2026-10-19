"""Per-field diagnostic flag thresholds for the gate and the production second reading (EXTRACTION-PLAN-v0.3
s10.3; fix for F-CR1 item 2 and F-mi6). A field with n_f applicable pairs and binary credit (equal / not equal)
is flagged when its agreements are <= c(n_f), the largest c with P(X <= c | n_f, 0.85) <= 0.01 (false-flag
rate at most 0.01 for a field at the 'good' level 0.85). Set-valued (Jaccard-credited) fields are not flagged;
they are reported with a bootstrap interval. Flags are diagnostic: they trigger rule revision and
re-measurement, never a gate failure. Exact binomial; no simulation.
Run: python -E -P analysis/extraction/flag_thresholds.py
"""
from scipy import stats

print(" n_f   c   false-flag at 0.85   detection at 0.70   at 0.60")
for nf in (15, 20, 25, 30, 40, 45, 50, 60):
    c = max((x for x in range(nf + 1) if stats.binom.cdf(x, nf, 0.85) <= 0.01), default=-1)
    if c < 0:
        print(f"{nf:4d}   -   no threshold with false-flag <= 0.01")
        continue
    print(f"{nf:4d} {c:3d}   {stats.binom.cdf(c, nf, 0.85):.4f}               "
          f"{stats.binom.cdf(c, nf, 0.70):.3f}               {stats.binom.cdf(c, nf, 0.60):.3f}")
