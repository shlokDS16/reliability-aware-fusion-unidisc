"""Red-team v0.5 scratch: re-apply the plan's rule-selection criterion (gate_bip_v05_summary.py part 3) with
'reach' replaced by the simulated pass probability of X80 (n = 120 in nearly every replicate) from the committed
gate_bip_v05-results.json. Run from the worktree root."""
import json
res = json.load(open("analysis/extraction/gate_bip_v05-results.json"))["scenarios"]
good = [k for k in res if not k.startswith("B")]
bad = [k for k in res if k.startswith("B")]
reach = {k: res[k]["X80"]["p_pass"] for k in good}
print("reach replaced by X80 P(pass):", {k: round(v, 3) for k, v in reach.items()})
print("X80 mean n:", {k: round(res[k]["X80"]["mean_n"], 1) for k in good})
for r in ("P80", "P50", "X80"):
    fails = []
    for k in good:
        x = res[k][r]
        if reach[k] >= 0.85 and x["p_pass"] < 0.85 - 2 * x["se"]:
            fails.append(f"{k} P {x['p_pass']:.3f}")
        if reach[k] < 0.85 and r != "X80" and x["p_step6"] < 0.80:
            fails.append(f"{k} step6 {x['p_step6']:.2f}")
    mb = max(res[k][r]["p_pass"] for k in bad)
    if mb > 0.08:
        fails.append(f"max one-bad {mb:.3f}")
    mn = sum(res[k][r]["mean_n"] for k in good) / len(good)
    print(f"{r}: {'meets' if not fails else 'fails ' + '; '.join(fails)}; max one-bad {mb:.3f}; mean n {mn:.1f}")
