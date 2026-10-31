"""Table: comparison with baselines on the Study 2 fresh fold (exploratory plan E3, research/paper2/tnnls/EXPLORATORY-PLAN-BASELINES-2026-10-30.md).
Outputs (complete tabular environments, booktabs; caption drafts are `% CAPTION DRAFT` comments at the end of each file):
  paper2-tnnls/tables/tab_baselines.tex       compact main version: accuracy only, n = 450, noise 0.1 / JPEG 10 / splice 128 / clean (one column)
  paper2-tnnls/tables/tab_baselines_full.tex  supplement version: accuracy and difference against NONE with its 95% interval (two-column width)
Every number is read from a committed file, never typed:
  NONE and LRF   runs/P2-LRF-L1/a6_analysis.json family_L.{L1 (noise), L3 (jpeg10), L4 (splice128), L-NI (clean)}.{acc_b, acc_a, net, ci95, n}
  A-UNL, A-SF, A-LIN, A-S-BD, A-MIL   runs/P2-LRF-ABL-SCORE/ablation_analysis.json rows[id].cells.<L1 cell>.{acc, vs_NONE.{d, ci95}}  (NONE/LRF accuracies asserted equal to the a6 file)
  MED, TM20   runs/P2-LRF-E2/combiners.json cells.<cond>.arms.<arm>.{acc, vs_NONE.{diff, ci95}}   (E2, CPU; the file also holds a third arm, TM-G, that is not read: removed from the paper's Table IV by ruling D0108)
  DN+NONE, DN+LRF  runs/P2-LRF-DN/dn_analysis.json cells.<cond>.arms.{"DN+NONE","DN+LRF"}.{acc, vs_NONE.{diff, ci95}}, conditions noise0.1 and jpeg10 only (E1, GPU);
                   the same layout as combiners.json. If the file is absent, or a cell is absent from it, the cell is printed as "pending". No other layout is read.
Emphasis (ruling D0109, 2026-10-31): italics = highest accuracy in the column (ties share the mark), over all rows that have a number in that column; no bold, no underline, no
second-best mark (bold means "null rejected" in this paper). This is a descriptive reading of one sample, not a test. Intervals: 95% paired percentile bootstrap over items, 10,000 resamples, unadjusted; they come from three
different runs (a6_analysis, ablation_analysis, E2), each with its own resampling seed. Not in this table (Addendum A6.4, A6.6): CLIP, SigLIP, the fresh-fold GATE-M arm.
Run: "<repo>/.venv/Scripts/python.exe" -I paper2-tnnls/scripts/tab_baselines.py   (CPU)"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import figstyle as S                                       # noqa: E402
from tablib import bold, iv, num, row                      # noqa: E402

N = 450
A6, ABL, E2, DN = "P2-LRF-L1/a6_analysis.json", "P2-LRF-ABL-SCORE/ablation_analysis.json", "P2-LRF-E2/combiners.json", "P2-LRF-DN/dn_analysis.json"
E4 = "P2-LRF-E4/evidential.json"          # plan E4 (EXPLORATORY-PLAN-EVIDENTIAL-2026-10-31.md); primary arm DS-l1-disc only
_E4: dict | None = None
# column key -> (header, a6 family_L key, ablation cell, E2/DN condition)
COLS = [("noise", "Noise 0.1", "L1", "L1_noise0.1", "noise0.1"),
        ("jpeg", "JPEG 10", "L3", "L1_jpeg10", "jpeg10"),
        ("splice", "Splice 128", "L4", "L1_splice128", "splice128"),
        ("clean", "Clean", "L-NI", "L1_clean", "clean")]
DAG = r"$^{\dagger}$"
# (id, compact name, source), in the order of the plan; blocks separated by a rule
# Row labels are plain method names (the names Fig. 7 / fig_ablation.py uses; red-team F12); the ids are only dictionary keys of the run files.
BLOCKS = [
    [("NONE", r"Unweighted sum" + DAG, "a6")],
    [("A-UNL", "Unlearned rank weight", "abl"), ("MED", "Median", "e2"), ("TM20", r"20\% trimmed mean", "e2"), ("DS-l1-disc", "Dempster combination", "e4")],
    [("A-SF", "Single feature (selected)", "abl"), ("A-LIN", "Linear logit, 35 features", "abl"), ("A-S-BD", r"Additive, from $B$ and $D$ only", "abl"),
     ("A-MIL", "Attention pooling (MIL style)", "abl")],
    [("LRF", r"LRF (frozen)" + DAG, "a6")],
    [("DN+NONE", "Denoise, then unweighted sum", "dn"), ("DN+LRF", "Denoise, then LRF", "dn")],
]


def load():
    a6 = S.jload(A6)["family_L"]
    abl = S.jload(ABL)
    e2 = S.jload(E2)
    global _E4
    _E4 = S.jload(E4)
    dn = None
    p = S.RUNS / DN
    if p.exists():
        dn = json.loads(p.read_text(encoding="utf-8"))
    return a6, abl, e2, dn


def cell_value(rid: str, src: str, col, a6, abl, e2, dn):
    """-> dict(acc, diff, ci, run) or None (pending / not applicable). diff and ci are None for the reference row."""
    key, _h, fam, acell, cond = col
    if src == "a6":
        r = a6[fam]
        assert r["n"] == N and r["alpha"] == 0.05
        if rid == "NONE":
            return dict(acc=r["acc_b"], diff=None, ci=None, run=f"runs/{A6} family_L.{fam}.acc_b")
        return dict(acc=r["acc_a"], diff=r["net"], ci=r["ci95"], run=f"runs/{A6} family_L.{fam}.{{acc_a,net,ci95}}")
    if src == "abl":
        assert abl["n_per_cell"][acell] == N
        c = next(x for x in abl["rows"] if x["id"] == rid)["cells"][acell]
        return dict(acc=c["acc"], diff=c["vs_NONE"]["d"], ci=c["vs_NONE"]["ci95"], run=f"runs/{ABL} rows[id={rid}].cells.{acell}.{{acc,vs_NONE.d,vs_NONE.ci95}}")
    if src == "e2":
        c = e2["cells"][cond]
        assert c["n"] == N
        a = c["arms"][rid]
        return dict(acc=a["acc"], diff=a["vs_NONE"]["diff"], ci=a["vs_NONE"]["ci95"], run=f"runs/{E2} cells.{cond}.arms.{rid}.{{acc,vs_NONE.diff,vs_NONE.ci95}}")
    if src == "e4":
        c = _E4["cells"][cond]
        assert c["n"] == N and _E4["primary"] == rid
        a = c["arms"][rid]
        return dict(acc=a["acc"], diff=a["vs_NONE"]["diff"], ci=a["vs_NONE"]["ci95"], run=f"runs/{E4} cells.{cond}.arms.{rid}.{{acc,vs_NONE.diff,vs_NONE.ci95}}")
    if src == "dn":
        if dn is None or cond not in dn.get("cells", {}) or rid not in dn["cells"][cond].get("arms", {}):
            return None
        c = dn["cells"][cond]
        assert c["n"] == N
        a = c["arms"][rid]
        return dict(acc=a["acc"], diff=a["vs_NONE"]["diff"], ci=a["vs_NONE"]["ci95"], run=f"runs/{DN} cells.{cond}.arms.{rid}.{{acc,vs_NONE.diff,vs_NONE.ci95}}")
    raise ValueError(src)


def marks(values: dict) -> dict:
    """values: {(rid, colkey): cell or None} -> {(rid, colkey): 1 (highest in the column) | 0}. By the integer number of correct items (acc * n); ties share the mark (D0109)."""
    out = {}
    for col in COLS:
        ks = {k[0]: round(v["acc"] * N) for k, v in values.items() if k[1] == col[0] and v is not None}
        for rid, k in ks.items():
            assert abs(k / N - values[(rid, col[0])]["acc"]) < 1e-9, (rid, col[0])
        top = max(ks.values())
        for rid, k in ks.items():
            out[(rid, col[0])] = 1 if k == top else 0
    return out


def fmt_acc(v, mk):
    if v is None:
        return "pending"
    s = f"{v['acc']:.3f}"
    return r"\textit{" + s + "}" if mk == 1 else s


def fmt_diff(v):
    if v is None:
        return "pending"
    if v["diff"] is None:
        return "--"
    return f"{num(v['diff'], plus=True)} {iv(*v['ci'])}"


CAPTION_MAIN = (r"Accuracy of the image-direction rule on the 450 fresh-fold images when the per-token evidence is combined in different ways "
                r"(exploratory comparison). $^{\dagger}$Fixed before the fold was opened (unweighted sum and the frozen LRF); every other row was specified and scored "
                r"after the preregistered Study~2 results. Italics: highest accuracy in the column (ties share the mark). The marks are descriptive, mark one sample, and are not a test; "
                r"only the unweighted rule and LRF were fixed before the fold was opened. 4 of the 9 learned refits of the exploratory ablation are shown, chosen after the fold was scored; "
                r"all 10 are in supplement S-VII, with differences and intervals. Median: the median of the per-token evidence is positive; 20\% trimmed mean: the mean of the evidence "
                r"after the lowest and highest 0.2m values are removed is positive (m tokens). Unlearned rank weight: weight 1 minus the within-image percentile rank of the token's uncertainty "
                r"(one minus the largest predicted probability with the caption masked). Denoise: non-local-means denoising before scoring (setting fixed in advance), noise and JPEG only.")
CAPTION_FULL = (r"As the comparison table, with the difference from the unweighted sum (accuracy minus the unweighted sum, 95\% paired percentile bootstrap interval, 10\,000 "
                r"resamples). Intervals are marginal and unadjusted; the rows other than the unweighted sum and LRF are exploratory, and the intervals of the ablation rows, the median "
                r"and trimmed mean, and the denoise rows come from separate runs with their own resampling seeds. $^{\dagger}$Fixed before the fold was opened.")


def build():
    a6, abl, e2, dn = load()
    ids = [(rid, name, src) for blk in BLOCKS for rid, name, src in blk]
    values = {}
    for rid, _n, src in ids:
        for col in COLS:
            values[(rid, col[0])] = (cell_value(rid, src, col, a6, abl, e2, dn) if not (src == "dn" and col[0] in ("splice", "clean")) else "na")
    # consistency of duplicates: NONE and LRF accuracy in the ablation file equal the a6 values
    for col in COLS:
        for rid in ("NONE", "LRF"):
            assert abs(abl["references_accuracy"][rid][col[3]] - values[(rid, col[0])]["acc"]) < 1e-12, (rid, col[0])
        assert abs(e2["cells"][col[4]]["arms"]["NONE"]["acc"] - values[("NONE", col[0])]["acc"]) < 1e-12, col[0]
    na = {k for k, v in values.items() if isinstance(v, str)}
    ranked = marks({k: v for k, v in values.items() if k not in na})
    return ids, values, na, ranked, dn is not None


def main():
    ids, values, na, ranked, have_dn = build()
    srcs = {rid: src for rid, _n, src in ids}
    # ------------------------------------------------------------------ compact
    head = ["Method"] + [c[1] for c in COLS]
    lines = [f"% tab_baselines.tex: generated by paper2-tnnls/scripts/tab_baselines.py from committed runs/ files. Do not edit by hand.",
             "% exploratory (plan E3); n = 450 fresh-fold images per column; accuracy only; italics = highest in the column (descriptive, not a test; D0109)",
             "% dagger: fixed before the fold was opened (unweighted sum, frozen LRF); all other rows post hoc.",
             f"% DN rows: {'read from runs/' + DN if have_dn else 'runs/' + DN + ' absent: printed as pending'}; DN covers noise 0.1 and JPEG 10 only",
             r"\begin{tabular}{@{}lcccc@{}}", r"\toprule", " & ".join(head) + r" \\", r"\midrule"]
    full = [f"% tab_baselines_full.tex: generated by paper2-tnnls/scripts/tab_baselines.py from committed runs/ files. Do not edit by hand.",
            "% exploratory (plan E3); n = 450; accuracy and accuracy minus the unweighted sum with its 95% paired percentile bootstrap interval (unadjusted); italic marks as in tab_baselines.tex",
            f"% DN rows: {'read from runs/' + DN if have_dn else 'runs/' + DN + ' absent: printed as pending'}; DN covers noise 0.1 and JPEG 10 only",
            r"\begin{tabular}{@{}lcrcrcrcr@{}}", r"\toprule",
            " & " + " & ".join(rf"\multicolumn{{2}}{{c}}{{{c[1]}}}" for c in COLS) + r" \\",
            r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}",
            "Method & " + " & ".join("Acc. & Diff.\\ from unweighted (95\\% interval)" for _ in COLS) + r" \\", r"\midrule"]
    for bi, blk in enumerate(BLOCKS):
        if bi:
            lines.append(r"\midrule")
            full.append(r"\midrule")
        for rid, name, src in blk:
            cc, cf, runs = [name], [name], []
            for col in COLS:
                k = (rid, col[0])
                if k in na:
                    cc.append("--")
                    cf += ["--", "--"]
                    continue
                v = values[k]
                if v is not None:
                    runs.append(v["run"])
                else:
                    runs.append(f"runs/{DN} cells.{col[4]}.arms.{rid} (pending: file or cell absent)")
                cc.append(fmt_acc(v, ranked.get(k, 0)))
                cf += [fmt_acc(v, ranked.get(k, 0)), fmt_diff(v)]
            lines.append(row(cc, runs))
            full.append(row(cf, runs))
    for out, ls, cap in (("tab_baselines.tex", lines, CAPTION_MAIN), ("tab_baselines_full.tex", full, CAPTION_FULL)):
        ls += [r"\bottomrule", r"\end{tabular}", "% CAPTION DRAFT: " + cap]
        (S.TABDIR / out).write_text("\n".join(ls) + "\n", encoding="utf-8")
        print("wrote", S.TABDIR / out)


if __name__ == "__main__":
    main()
