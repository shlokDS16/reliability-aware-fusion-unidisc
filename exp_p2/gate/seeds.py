"""Analysis seeds as the SAP fixes them (8.4): numpy.random.SeedSequence(20261028) spawned by analysis name, in the order of the function list of SAP section 10.
`seed_for(name)` returns that child SequenceSeed; every bootstrap/permutation/split in the analysis code takes it where an int seed was accepted (np.random.default_rng
accepts a SeedSequence). `meta()` is written into every analysis output file (seed, numpy version)."""
from __future__ import annotations

import numpy as np

ROOT_SEED = 20261028
ANALYSES = ("load_items", "completeness_report", "arm_y_z", "exact_mcnemar", "paired_boot_diff", "primary", "s_m", "s_z", "s_dn", "s_d", "s_d2", "s_c", "headroom_check",
            "fap_check", "split_replication", "auroc", "detection_contrast", "wilcoxon_z", "fusion", "prop4_plugin", "mechanism", "calibration", "equivalence", "selftest", "denoise_check",
            "ps_family", "s2_family", "s2_descriptive",        # appended for family PS and S2 (SAP AD.13)
            "edec", "omni_gate", "omni_r", "suite")   # appended 2026-10-28 (integration); SAP A3.7 names edec, omni_gate, omni_r, then the integration engineer's further names; family B keeps the existing name "fusion" (A3.7);
#                                                                     appending leaves every earlier child seed unchanged (spawn child i has spawn_key (i,)); tests/exp_p2/test_gate_swap.py pins the first 28 states; positions: edec 28, omni_gate 29, omni_r 30, suite 31


def seed_for(name: str) -> np.random.SeedSequence:
    if name not in ANALYSES:
        raise KeyError(f"unknown analysis name {name!r}; add it to seeds.ANALYSES (appending only: the spawn order is part of the preregistration)")
    return np.random.SeedSequence(ROOT_SEED).spawn(len(ANALYSES))[ANALYSES.index(name)]


def meta() -> dict:
    return dict(root_seed=ROOT_SEED, spawn_order=list(ANALYSES), numpy_version=np.__version__, bootstrap_resamples=10000, interval="percentile")
