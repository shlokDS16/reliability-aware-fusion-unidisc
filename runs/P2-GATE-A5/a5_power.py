"""A5 (family H) power and GO-rule arithmetic. Exact binomial, stdlib only. Derived, not results."""
from math import comb, sqrt


def pmf(n, k, p):
    return comb(n, k) * p**k * (1 - p)**(n - k)


def mcnemar_p(b, c):
    nd = b + c
    if nd == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(nd, i) for i in range(k + 1)) / 2**nd)


BMIN = {}


def bmin(nd, alpha):
    """smallest b (c = nd - b) that rejects two-sided at alpha with b > c; None if unreachable"""
    key = (nd, alpha)
    if key not in BMIN:
        BMIN[key] = None
        for b in range(nd // 2 + 1, nd + 1):
            if mcnemar_p(b, nd - b) <= alpha:
                BMIN[key] = b
                break
    return BMIN[key]


def power(n, pid, theta, alpha):
    tot = 0.0
    for nd in range(0, n + 1):
        w = pmf(n, nd, pid)
        if w < 1e-12:
            continue
        bm = bmin(nd, alpha)
        if bm is None:
            continue
        tot += w * sum(pmf(nd, b, theta) for b in range(bm, nd + 1))
    return tot


def nd_req(theta, alpha, run=5, hi=400):
    for nd in range(1, hi):
        ok = True
        for x in range(nd, nd + run + 1):
            bm = bmin(x, alpha)
            if bm is None or sum(pmf(x, b, theta) for b in range(bm, x + 1)) < 0.8:
                ok = False
                break
        if ok:
            return nd
    return None


A1 = 0.05 / 3
print("== required discordant n_d for conditional power 0.8 (exact; stays >= 0.8 for the next 5 values), Holm step 1 alpha' = 0.05/3")
for th in (0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95):
    print(f"theta {th:.2f}: n_d {nd_req(th, A1)}")

print("\n== smallest b with c = 0 that rejects at Holm step 1:", "n_d=7 ->", bmin(7, A1), "; n_d=8 ->", bmin(8, A1))

print("\n== unconditional power, Holm step 1 (0.0167)")
for n in (300, 200):
    for pid in (0.02, 0.04, 0.06, 0.10, 0.15, 0.20, 0.30):
        row = [f"{power(n, pid, th, A1):.2f}" for th in (0.65, 0.75, 0.85, 0.95)]
        print(f"n {n} pi_d {pid:.2f} E[n_d] {n * pid:5.1f}  theta .65/.75/.85/.95: {' '.join(row)}")

print("\n== MDE at n = 300 and 200, Holm step 1: smallest theta (0.005 grid) with power >= 0.8; Delta = pi_d (2 theta - 1)")
for n in (300, 200):
    for pid in (0.04, 0.06, 0.10, 0.15, 0.20, 0.30):
        th = 0.5
        while th <= 1.0001 and power(n, pid, th, A1) < 0.8:
            th += 0.005
        if th <= 1.0001:
            print(f"n {n} pi_d {pid:.2f}: theta_min {th:.3f}  Delta_min {pid * (2 * th - 1):.3f}")
        else:
            print(f"n {n} pi_d {pid:.2f}: unreachable")

print("\n== H3 rule, 50 items, one corruption: P(G >= 3), P(G >= 8), G ~ Bin(50, pi_d)")
for pid in (0.002, 0.008, 0.02, 0.04, 0.06, 0.10, 0.15, 0.20):
    p3 = sum(pmf(50, k, pid) for k in range(3, 51))
    p8 = sum(pmf(50, k, pid) for k in range(8, 51))
    print(f"pi_d {pid:.3f}: P(G>=3) {p3:.3f}  P(G>=8) {p8:.3f}")

print("\n== H3 decision-headroom rule: P(F- >= 2), F- ~ Bin(50, q)")
for q in (0.01, 0.02, 0.04, 0.08, 0.20):
    print(f"q {q:.2f}: {sum(pmf(50, k, q) for k in range(2, 51)):.3f}")
print("perfect-restoration bound at n = 300 (F- scaled x6, c = 0): b = 12 -> p =", round(mcnemar_p(12, 0), 5), "; b = 6 -> p =", round(mcnemar_p(6, 0), 4))

print("\n== H3 clean-signal rule: one-sided exact P(X >= k | 0.5), 50 items")
for k in (30, 31, 32, 33):
    print(k, round(sum(pmf(50, j, 0.5) for j in range(k, 51)), 4))
print("P(k >= 32 | true accuracy):", {a: round(sum(pmf(50, j, a) for j in range(32, 51)), 3) for a in (0.55, 0.60, 0.65, 0.70, 0.80)})

print("\n== NEG reachability: 90 percent half-width about 1.645 sqrt(pi_d / n)")
for n in (300, 200):
    print(n, {pid: round(1.645 * sqrt(pid / n), 3) for pid in (0.05, 0.10, 0.20, 0.30)})

print("\n== 1 - 0.95^k for k = 11, 13:", round(1 - 0.95**11, 3), round(1 - 0.95**13, 3))
