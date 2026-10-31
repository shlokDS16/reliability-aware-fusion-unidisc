"""Supplement table: Gaussian-noise severity sweep of the frozen LRF and the unweighted sum (exploratory; plan research/paper2/tnnls/EXPLORATORY-PLAN-SEVERITY-2026-10-31.md).
Source: runs/P2-LRF-SEV/sev_analysis.json levels.<sigma>.{NONE, LRF, LRF_minus_NONE.{diff,ci95,b,c}, gain_minus_clean_gain.{diff,ci95}, source}. Output: tables/supp_severity.tex.
    python scripts/tab_severity.py      (from paper2-tnnls/)"""
from __future__ import annotations

import json

import figstyle as S
import tablib as T

SRC = "P2-LRF-SEV/sev_analysis.json"
ORDER = ("0", "0.05", "0.1", "0.2", "0.3")


def main():
    res = json.loads((S.RUNS / SRC).read_text(encoding="utf-8"))
    pc = res["positive_control"]
    if not pc.get("ok"):
        raise SystemExit(f"positive control not ok: {pc}")
    rows = []
    for lv in ORDER:
        c = res["levels"][lv]
        d = c["LRF_minus_NONE"]
        g = c.get("gain_minus_clean_gain")
        lab = "0 (clean)" if lv == "0" else (lv + (" (fitted level)" if lv == "0.1" else ""))
        runs = [f"runs/{SRC} levels.{lv}.{{NONE,LRF,LRF_minus_NONE.{{diff,ci95,b,c}}}}" + (f",gain_minus_clean_gain.{{diff,ci95}}" if g else "") + f" (cells from {c['source']})"]
        rows.append(T.row([lab, T.num(c["NONE"]), T.num(c["LRF"]), T.num(d["diff"], plus=True), T.iv(*d["ci95"]), f"{d['b']}/{d['c']}",
                           (T.num(g["diff"], plus=True) + " " + T.iv(*g["ci95"])) if g else "--"], runs))
    T.write("supp_severity.tex", "@{}lcccccc@{}",
            [r"$\sigma$", "Unweighted", "LRF", "LRF $-$ unw.", "95\\% interval", "$b/c$", "Gain $-$ clean gain [95\\%]"], [rows],
            preamble=[res["label"], f"n = {res['levels']['0']['n']} fresh-fold images per level; positive control token agreement {pc['token_equal_fraction']:.6f} (run: runs/{SRC} positive_control)",
                      "levels 0 and 0.1 from runs/P2-LRF-L1; 0.05, 0.2, 0.3 from runs/P2-LRF-SEV (same noise draw scaled by sigma)"],
            script="tab_severity.py")


if __name__ == "__main__":
    main()
