"""SAP-GATE Addendum A3: power / minimum detectable effect at n = 300 for S2 and family B, beside the SAP's n = 150.
CPU only, no data files read. Run: python a3_power.py > runs/P2-GATE-A3/a3_power_output.txt
Reuses the exact-McNemar machinery of a2_power.py unchanged (imported, not copied); the SHA-256 of a2_power.py is checked
against the value recorded in SAP AD.13 and printed. Every number is a calculation under stated assumptions
(pi_d = discordance rate, theta = share of discordant items favouring the first arm), NOT a result.
theta is searched on a grid of step 0.005, so a net gain Delta = pi_d*(2*theta-1) is resolved to about +-0.0025*2*pi_d.
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a2_power as a2  # noqa: E402

A2_SHA = '78fc0fb8f5973e9363de6d1edf5db76dd87563c230051d02d317be7793686f7e'   # SAP AD.13


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def mde_row(nn, pid, a):
    t = a2.theta_min(nn, pid, a)
    return None if t is None else (round(t, 3), round(pid * (2 * t - 1), 3))


if __name__ == '__main__':
    got = sha(os.path.join(HERE, 'a2_power.py'))
    print('a2_power.py sha256', got, 'matches SAP AD.13:', got == A2_SHA)
    assert got == A2_SHA, 'a2_power.py differs from the version recorded in AD.13'

    PID = (0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30)
    print('\nA) (theta_min, net gain) for power 0.8, exact two-sided McNemar, favourable tail. None = unreachable even at theta = 1')
    print("   alpha' 0.025 = Holm threshold of a two-cell family at 0.05 (S2: m = 2; PS: m = 2); alpha' 0.05 = family B (m = 1)")
    for nm in ('0.025', '0.05'):
        for nn in (120, 150, 240, 300):
            print('n', nn, "alpha'", nm, [(p, mde_row(nn, p, a2.AL[nm])) for p in PID])

    print("\nB) Ratio of the minimum net gain, n = 150 over n = 300 (same pi_d, same alpha); None where n = 150 is unreachable")
    for nm in ('0.025', '0.05'):
        out = []
        for p in PID:
            r150, r300 = mde_row(150, p, a2.AL[nm]), mde_row(300, p, a2.AL[nm])
            out.append((p, None if (r150 is None or r300 is None) else round(r150[1] / r300[1], 2)))
        print("alpha'", nm, out)

    print('\nC) POWER side by side at selected (pi_d, theta): n = 150 vs n = 300')
    for nm, who in (('0.025', 'S2 (and PS)'), ('0.05', 'B')):
        for nn in (150, 300):
            print(who, 'n', nn, "alpha'", nm, [(p, t, round(a2.power(nn, p, t, a2.AL[nm]), 3)) for p, t in
                                               ((0.05, 0.80), (0.10, 0.70), (0.10, 0.75), (0.10, 0.80), (0.15, 0.75), (0.20, 0.70), (0.20, 0.80))])

    print('\nD) Size check (theta = 0.5): one-tail rejection probability, pi_d = 0.10 (conservatism of the exact test)')
    for nn in (150, 300):
        print('n', nn, [(nm, round(a2.power(nn, 0.10, 0.5, a2.AL[nm]), 4)) for nm in ('0.05', '0.025')])

    print('\nE) Reproduction check against SAP AD.4 (n = 300, alpha 0.025): net gain 0.040/0.057/0.071/0.082 at pi_d 0.05/0.10/0.15/0.20; power 0.658 at (0.10, 0.75)')
    print([(p, mde_row(300, p, a2.AL['0.025'])) for p in (0.05, 0.10, 0.15, 0.20)], round(a2.power(300, 0.10, 0.75, a2.AL['0.025']), 3))

    print('\nF) S2 only: items with g_i = 0 are concordant by construction. If a share s0 of the n items has g_i = 0, the overall pi_d is pi_d_flagged * (1 - s0).')
    print('   ASSUMED illustration (no g_i distribution exists yet): pi_d_flagged 0.15 with s0 = 0, 0.2, 0.4, 0.6 gives overall pi_d:',
          [round(0.15 * (1 - s), 3) for s in (0, 0.2, 0.4, 0.6)])
    print("   MDE at n = 300, alpha' 0.025 for those overall pi_d (theta_min, net gain on the all-items scale):",
          [(round(0.15 * (1 - s), 3), mde_row(300, round(0.15 * (1 - s), 3), a2.AL['0.025'])) for s in (0, 0.2, 0.4, 0.6)])
