"""Rebuild every Paper 2 (TNNLS) figure and table from committed runs/ files. CPU only. Run from anywhere:
    "<repo>/.venv/Scripts/python.exe" paper2-tnnls/scripts/build_all.py
fig4 also writes runs/P2-PAPER-FIGS/ (computed curves, token weights, script sha)."""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
for s in ("fig1_measurement", "fig2_theory", "fig3_study1_P", "fig4_study2_weights", "fig5_study2_results", "tab1_familyP", "tab_detection", "tab_H", "tab_status_map", "tab_glance", "tab_tests_full", "tab2_study2", "tab3_baselines", "tab_features", "tab4_cost"):
    print("==", s, flush=True)
    subprocess.run([sys.executable, str(HERE / f"{s}.py")], cwd=HERE, check=True)
