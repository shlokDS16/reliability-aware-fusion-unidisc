"""Table IV (cost), two files so that no table holds both studies' numbers (SPEC rule 3; the spec lists one table, this is flagged to the lead):
  tab4_cost_study1.tex  Study 1: network rows, compute time and peak GPU memory per item of the main-test stage (runs/P2-GATE-M4/items.jsonl).
  tab4_cost_study2.tex  Study 2: the same for the fresh-fold stages (runs/P2-LRF-L1, runs/P2-LRF-LG) plus the row for LRF scoring on stored arrays (CLIP and
                        SigLIP cost sits in Table III as "not measured").
Only measured values. The per-item record of a stage covers ALL arms computed in that pass (the arms share the network rows), so a per-arm network
count and a per-arm wall-clock do not exist in the runs; those cells say "not measured separately". CLIP, SigLIP and the CPU weight evaluation of LRF
have no timing in any committed run: "not measured". Nothing is estimated.
Fields (written by the runners, exp_p2/run_gate_m4.py and exp_p2/gate/runner.py): n_rows = network rows used by the item (sc.rows difference),
seconds = busy compute time of the item (excludes the runner's duty-cycle pauses), peak_gb = torch.cuda.max_memory_allocated() at the end of the item
(cumulative within a process, so the maximum over items is the stage's peak)."""
from __future__ import annotations

import json

import numpy as np

import figstyle as S
from tablib import row, write

NM = "not measured"
NS = "not measured separately"


def stage(run: str):
    rows = [json.loads(l) for l in open(S.RUNS / run / "items.jsonl", encoding="utf-8")]
    sec = np.array([r["seconds"] for r in rows], float)
    nr = np.array([r["n_rows"] for r in rows], float)
    pk = np.array([r["peak_gb"] for r in rows], float)
    cfg = S.jload(f"{run}/config.json")
    return dict(n=len(rows), rows_med=float(np.median(nr)), rows_rng=(int(nr.min()), int(nr.max())), sec_med=float(np.median(sec)),
                sec_q=(float(np.percentile(sec, 25)), float(np.percentile(sec, 75))), peak=float(pk.max()), conds=cfg.get("conds") or cfg.get("conditions"))


def fmt_stage(s):
    rr = f"{s['rows_med']:.0f}" if s["rows_rng"][0] == s["rows_rng"][1] else f"{s['rows_med']:.0f} ({s['rows_rng'][0]}--{s['rows_rng'][1]})"
    return [str(s["n"]), rr, f"{s['sec_med']:.1f} ({s['sec_q'][0]:.1f}--{s['sec_q'][1]:.1f})", f"{s['peak']:.1f}"]


def rrun(run):
    return f"runs/{run}/items.jsonl n_rows, seconds, peak_gb (one value per item: median, quartiles, max)"


HDR = ["Method (stage)", "Items", "Network rows per item", "Compute time per item, s", "Peak GPU memory, GB"]
COLS = "@{}lcccc@{}"

m4 = stage("P2-GATE-M4")
write("tab4_cost_study1.tex", COLS, HDR, script="tab4_cost.py", blocks=
      [[row(["NONE and GATE-M (main-test pass; all Study 1 arms share it)"] + fmt_stage(m4), [rrun("P2-GATE-M4")])]],
      preamble=["Study 1 only. Per-arm rows and time: not measured separately (the arms share the pass). Median (min--max) for rows; median (quartiles) for time; max for memory.",
                "Hardware per runs/P2-GATE-M4/telemetry-chunk*.csv: one laptop GPU (see paper2/sections/appendix.tex app:hardware for the card name; not re-measured here)"])

l1, lg = stage("P2-LRF-L1"), stage("P2-LRF-LG")
write("tab4_cost_study2.tex", COLS, HDR, script="tab4_cost.py", blocks=
      [[row(["NONE, all four conditions (fresh-fold pass; the same pass stores the inputs of LRF)"] + fmt_stage(l1), [rrun("P2-LRF-L1")]),
        row(["NONE, three other noise types (LG pass)"] + fmt_stage(lg), [rrun("P2-LRF-LG")]),
        row(["LRF: weights and decision from stored arrays (CPU)", "--", NM, NM, NM],
            ["no timing recorded in runs/P2-LRF-L1/lrf_score_meta.json or any committed LRF run"])]],
      preamble=["Study 2 only. LRF adds no network row: it reads stored arrays (A6.2). Per-arm rows and time of NONE versus the stored-array scoring: not measured separately.",
                "Median (min--max) for rows; median (quartiles) for time; max for memory."])
print(json.dumps(dict(P2_GATE_M4=m4, P2_LRF_L1=l1, P2_LRF_LG=lg), default=str))
