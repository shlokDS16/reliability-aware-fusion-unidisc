"""F7: family PS (positive control, pipeline check) on its own canvas, same encoding as F6.
Reads runs/P2-GATE-M4/analysis.json keys ps.per_corruption.{patch,swap}."""
from __future__ import annotations

import json

import resultlib as R

a = R.jload("P2-GATE-M4/analysis.json")
pc = a["ps"]["per_corruption"]
rows = [pc["patch"], pc["swap"]]
R.effect_figure(rows, ["patch", "swap"], "F7_ps_result", lambda r: f"{r['label']}, $n={r['n']}$")
keys = ("b", "c", "n_d", "n", "acc_a", "acc_b", "delta", "ci90", "ci95", "p_holm")
print(json.dumps({k: {x: v[x] for x in keys} for k, v in pc.items()}))
print(a["ps"]["positive_control"])
