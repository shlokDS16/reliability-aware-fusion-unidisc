"""Token cost of the scope options of EXTRACTION-PLAN-v0.3 s2.8 from ONE per-record table (fix F-MA7).

Every per-record figure is an inference (E0, from the red-team's v0.1 estimates, widened for the v0.3 K
rules); none is measured. Stage A measures them; the table is recomputed from Stage A means before
Stage B (plan s10.5). Counts come from strata-log.txt (strata.py). Run: python -I analysis/extraction/cost_options.py
"""
import math

# ---- per-record table (thousands of tokens, low-high) -------------------------------------------
PER = {
    "EA-LQH": (38, 55),   # light blocks + appraisal + headline units, one record (red-team 35-50 + H 3-5)
    "EA-K":   (40, 80),   # block K on one record (v0.2 basis 33-53, widened: v0.3 records every qualifying table)
    "EC":     (20, 40),   # adjudication of one double-extracted record
    "EQ":     (5, 10),    # public-version QA1/QA2 session, one anonymous record
    "F2":     (31, 45),   # second extraction of block F alone (25-33) plus EC on 30% of records (0.3 x 20-40)
    "QA2":    (36, 57),   # second QA rater session (30-45) plus EC on 30% of records
    "EA-F":   (15, 25),   # block F alone as the only extraction of a record (option 2+F)
}
FULLREC = tuple(a + b for a, b in zip(PER["EA-LQH"], PER["EA-K"]))           # all blocks, one extractor
GATEREC = tuple(2 * f + e for f, e in zip(FULLREC, PER["EC"]))                 # EA + EB all blocks + EC

# ---- counts (strata-log.txt, T1) ------------------------------------------------------------------
INC, C1, C2, NL, FR, SAMPLE = 608, 53, 108, 12, 435, 120
ANON_ALL, ANON_C1, ANON_C2, ANON_SAMPLE = 287, 27, 29, 44 + 18     # sample: anonymous strata allocations
RQ = C1 + C2 + SAMPLE                                                # records with block K
STAGE_A, GATE_N = 12, 60


def m(k, per):
    return (k * per[0] / 1000, k * per[1] / 1000)


def add(*xs):
    return (sum(x[0] for x in xs), sum(x[1] for x in xs))


def fmt(x):
    return f"{x[0]:6.1f}M-{x[1]:5.1f}M"


def option(name, lqh_n, k_n, er_k, er_l, anon):
    comp = [
        (f"EA: L+Q+H on {lqh_n} records", m(lqh_n, PER["EA-LQH"])),
        (f"EA: block K on {k_n} records (C1 {C1} + C2 {C2} + sample {SAMPLE})", m(k_n, PER["EA-K"])),
        (f"ER: 10% second reading, {er_k} with K + {er_l} without", add(m(er_k, FULLREC), m(er_l, PER["EA-LQH"]))),
        (f"EC: adjudication of the {er_k + er_l} ER records", m(er_k + er_l, PER["EC"])),
        (f"EQ: public-version QA1/QA2, at most {anon} anonymous records", m(anon, PER["EQ"])),
        (f"Pilot: Stage A {STAGE_A} + gate {GATE_N}, EA+EB all blocks + EC", m(STAGE_A + GATE_N, GATEREC)),
    ]
    print(f"\n== {name} ==")
    for lab, v in comp:
        print(f"  {lab:<70} {fmt(v)}")
    tot = add(*[v for _, v in comp])
    print(f"  {'MIN (sum)':<70} {fmt(tot)}")
    rest = lqh_n - er_k - er_l
    rec = add(tot, m(rest, PER["F2"]))
    full = add(rec, m(rest, PER["QA2"]))
    print(f"  {'+ block F second extraction on the other ' + str(rest) + ' records (REC)':<70} {fmt(rec)}")
    print(f"  {'+ block F and QA second rater on the other ' + str(rest) + ' (FULL)':<70} {fmt(full)}")
    print(f"  {'a re-gate adds':<70} {fmt(m(GATE_N, GATEREC))}")
    return tot


def main():
    print("Per-record table (thousand tokens):", ", ".join(f"{k} {v[0]}-{v[1]}" for k, v in PER.items()),
          f"| all blocks one extractor {FULLREC[0]}-{FULLREC[1]} | gate record (EA+EB+EC) {GATEREC[0]}-{GATEREC[1]}")
    er_k = math.ceil(0.10 * RQ)
    # Option 1: user's words read as "RQ data = contrast data (block K)": light blocks on every include
    o1 = option("Option 1: L+Q+H on every include; block K on all multimodal + the stratified sample",
                INC, RQ, er_k, math.ceil(0.10 * (INC - RQ)), ANON_ALL)
    # Option 2: "RQ data = everything the RQs use": every block on all multimodal + the sample only
    o2 = option("Option 2: every block (L, Q, H, K) on all multimodal + the stratified sample only",
                RQ, RQ, er_k, 0, ANON_C1 + ANON_C2 + ANON_SAMPLE)
    rest = INC - RQ
    print(f"\n  Option 2 leaves {rest} includes (frame-R non-sampled {FR - SAMPLE} + nonlang_only {NL}) with screening data only.")
    print(f"  Variant 2+F (keeps D0011's census on every include): + block F alone on those {rest}: {fmt(m(rest, PER['EA-F']))}"
          f" -> MIN {fmt(add(o2, m(rest, PER['EA-F'])))}")
    print(f"\nDifference Option 1 - Option 2 (MIN): {fmt((o1[0] - o2[0], o1[1] - o2[1]))}")
    print("\nVariants of the sample size (block K and L+Q+H change together in option 2, K only in option 1):")
    for n in (90, 150):
        d = n - SAMPLE
        word = "adds" if d > 0 else "saves"
        print(f"  n = {n}: option 1 {word} {fmt(m(abs(d), PER['EA-K']))}; option 2 {word} {fmt(m(abs(d), FULLREC))}")
    print(f"\nGate size: each 15 gate records cost {fmt(m(15, GATEREC))} (n 45 vs 60).")
    print("G7 (budget check, plan s10.4): projected total from Stage A + Stage B means, with the component counts above,"
          " must not exceed the budget the user approves in the scope row.")


if __name__ == "__main__":
    main()
