"""Cost additions of form v0.4 (EXTRACTION-PLAN-v0.4 s2.8): the certainty second reading of column_unverified
units (red-team audit 3, m6), gate sizes chosen by the ICC rule (M1, s10.7), and the split gate design (m8).
cost_options.py (v0.3) is unchanged and its log stays valid; this script adds components to its totals. Every
per-record figure is an inference (E0); Stage A replaces them with measured means (plan s14 B1).
Run: python -I analysis/extraction/cost_options_v04.py
"""
# ---- per-record table of cost_options.py (thousand tokens, low-high), copied --------------------------
EA_LQH, EA_K, EC = (38, 55), (40, 80), (20, 40)
FULLREC = (EA_LQH[0] + EA_K[0], EA_LQH[1] + EA_K[1])                 # 78-135
GATEREC = (2 * FULLREC[0] + EC[0], 2 * FULLREC[1] + EC[1])            # 176-310
# split design: a K-only gate record = EA and EB extract block K plus the F1 unit and S14 (needed by G5),
# EC adjudicates; F1 and S14 reading 10-15k per extractor (E0)
F1S14 = (10, 15)
KREC = (2 * (EA_K[0] + F1S14[0]) + EC[0], 2 * (EA_K[1] + F1S14[1]) + EC[1])
# certainty second reading of column_unverified units: share f of K units (E0: 0.10-0.30; Stage A measures it);
# the second reader re-reads those units (f x EA-K) and EC adjudicates what differs (f x EC)
F_UNVER = (0.10, 0.30)
RQ = 53 + 108 + 120                    # records with block K under the v0.3 multimodal rule (option b)
ER_K = 29                              # of them already double-read in the 10 percent second reading


def tok(x):
    return f"{x[0]:.1f}M-{x[1]:.1f}M"


def main():
    print(f"per-record (k tokens): all blocks {FULLREC}, gate record {GATEREC}, K-only gate record {KREC}")
    k_single = RQ - ER_K
    cu = (k_single * F_UNVER[0] * (EA_K[0] + EC[0]) / 1000, k_single * F_UNVER[1] * (EA_K[1] + EC[1]) / 1000)
    print(f"\nm6 certainty second reading of column_unverified units on the {k_single} K records read once "
          f"(share {F_UNVER[0]:.2f}-{F_UNVER[1]:.2f}): {tok(cu)}  (same under Option 1 and Option 2; add to MIN, REC, FULL)")
    print("\nGate size (ICC rule, plan s10.7): gate component and change against n = 60")
    base = (60 * GATEREC[0] / 1000, 60 * GATEREC[1] / 1000)
    for n in (60, 72, 90, 105, 120):
        c = (n * GATEREC[0] / 1000, n * GATEREC[1] / 1000)
        print(f"  n {n:3d}: {tok(c)}   change {tok((c[0] - base[0], c[1] - base[1]))}")
    sp = ((30 * GATEREC[0] + 30 * KREC[0]) / 1000, (30 * GATEREC[1] + 30 * KREC[1]) / 1000)
    print(f"\nm8 split design (30 full gate records + 30 K-only gate records): {tok(sp)}   change against n = 60 "
          f"{tok((sp[0] - base[0], sp[1] - base[1]))}")
    sp90 = ((30 * GATEREC[0] + 60 * KREC[0]) / 1000, (30 * GATEREC[1] + 60 * KREC[1]) / 1000)
    print(f"   split with K criteria on 90 (30 full + 60 K-only): {tok(sp90)}   change against n = 60 "
          f"{tok((sp90[0] - base[0], sp90[1] - base[1]))}")


if __name__ == "__main__":
    main()
