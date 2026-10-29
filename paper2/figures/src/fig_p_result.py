"""F6: family P, the preregistered test. Reads runs/P2-GATE-M4/analysis.json keys primary.per_corruption.{jpeg,noise,splice} and outcome.sentence.
F7 is a separate script and canvas (SAP A4.2.5 item 3). Nothing else is drawn on this canvas (A4.2.5 item 4)."""
from __future__ import annotations

import json

import resultlib as R

a = R.jload("P2-GATE-M4/analysis.json")
pc = a["primary"]["per_corruption"]
rows = [pc["jpeg"], pc["noise"], pc["splice"]]
names = ["JPEG", "noise", "splice"]
R.effect_figure(rows, names, "F6_p_result", lambda r: f"{r['label']}, $n={r['n']}$")
keys = ("b", "c", "n_d", "n", "acc_a", "acc_b", "delta", "ci90", "ci95", "p_holm")
print(json.dumps({k: {x: v[x] for x in keys} for k, v in pc.items()}))
print(a["outcome"]["label"], "|", a["outcome"]["sentence"])
