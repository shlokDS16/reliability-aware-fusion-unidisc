```yaml
agent: figure-smith
date: 2026-10-30
brief: Paper 2 TNNLS figure set v3 - four new figures (gate method + calibration check, detection, LRF margins, LRF ablation), Fig. 4 redesigned with a method schematic, Fig. 5 tidied
sources_examined: [paper2-tnnls/SPEC.md v2.2 rules 0,3,4,5 and sections 4-6, decisions D0090-D0104, SAP A4.2.2 and A4.2.5, ABLATION-PLAN-2026-10-30.md sections 2,3,8, sections/study1.tex, sections/study2.tex, tables/tab_features_main.tex, runs/P2-GATE-M4/analysis.json, runs/P2-GATE-M2/threshold.json, runs/P2-GATE-M1/analysis.json, runs/P2-LRF-L1/{predictions.jsonl,a6_analysis.json}, runs/P2-LRF-ABL-SCORE/ablation_analysis.json, runs/P2-LRF-FROZEN-LFIX/{spec.json,HASHES.json,model.npz}]
coverage: every new or changed PNG inspected at 300 dpi; fonts checked with pdffonts; not checked inside the typeset PDF (editor integrates)
claims:
  - statement: discordant counts of the margins figure equal a6_analysis family_L L1 (b=58, c=27, n=450) and L-NI (b=27, c=13); margin sign equals stored y on every point
    status: supported
    evidence: assertions in paper2-tnnls/scripts/fig_margins.py; runs/P2-PAPER-FIGS/fig_margins.json
    level: E4
    confidence: 0.99
  - statement: the frozen rival of S-D2 is the same score (tex_neg) as the M1 same-item rival
    status: supported
    evidence: assertion in paper2-tnnls/scripts/fig_detection.py
    level: E4
    confidence: 0.99
competing_explanations: []
unknowns: [page count after integration (not built)]
next_test: {hypothesis: n/a, intervention: editor integrates and builds, primary_metric: page count <= 15 and check_column_gaps.py clean, falsifier: overflow, gpu_hours: 0}
```

Outputs: scripts `paper2-tnnls/scripts/{fig_gate_method,fig_detection,fig_margins,fig_ablation,schem}.py`, rewritten figure part of
`fig4_study2_weights.py`, label tidy of `fig5_study2_results.py`, `figstyle.trace()`, `build_all.py` list. Traces in
`runs/P2-PAPER-FIGS/fig_{gate_method,detection,margins,ablation}.json` and `fig4_meta.json` (script SHA-256 in each).
Captions, labels and placement notes: `paper2-tnnls/figures/CAPTIONS.md` (figure set v3 table and sections). No .tex edited; nothing committed;
new PDFs are git-ignored by `paper2-tnnls/.gitignore` (`*.pdf`) and need `git add -f`.
