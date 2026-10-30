"""Clean mean per-token paired evidence from M4 (card v4 row 7 input to coherence_report --mu).
mu = mean over the 500 M4 test items of the per-item mean of clean_delta (all 1024 tokens; Delta_j as stored by run_gate_m4.py).
The pooled token mean is also recorded; with 1024 tokens per item the two are identical."""
import glob, json
import numpy as np
fs = sorted(glob.glob("runs/P2-GATE-M4/arrays/item*.npz"))
per_item = np.array([float(np.mean(np.load(f)["clean_delta"])) for f in fs])
out = dict(n_items=len(fs), mu_item_mean=float(per_item.mean()), sd_item=float(per_item.std(ddof=1)), source="runs/P2-GATE-M4/arrays/item*.npz key clean_delta")
json.dump(out, open("runs/P2-GATE-M5/mu_from_m4.json", "w"), indent=1)
print(json.dumps(out))
