# D0052 RQ results (script-generated; do not edit)

extracted 29 of 80; by stratum {'G-long': 7, 'G-mm': 7, 'G-short': 8, 'S-seed': 7}; N_h {'G-mm': 52, 'G-short': 267, 'G-long': 265, 'S-seed': 1073.8488372093022}; missing ['M03150', 'M03633', 'M04407', 'M06272', 'M07646', 'M10526', 'M10840', 'M10855', 'M11180', 'M12084', 'M12879', 'M12960', 'M13371', 'M13884', 'M14280', 'M14293', 'M14326', 'M15033', 'M15781', 'M15792', 'M15840', 'M16080', 'M16154', 'M16269', 'M17249', 'M17285', 'M17725', 'M17834', 'M18059', 'M18141', 'M18735', 'M18994', 'M19012', 'M19013', 'M19021', 'M19099', 'M19293', 'R0021', 'R0171', 'R0188', 'R0214', 'R0291', 'R0588', 'R0631', 'R0677', 'R0717', 'R0738', 'R0865', 'R0958', 'R0963', 'R1004']

## RQ1
- study_type:
  - method: 24/29  weighted 0.819 [0.568, 0.94]
  - theory: 1/29  weighted 0.02 [0.0, 0.527]
  - analysis: 4/29  weighted 0.161 [0.048, 0.421]
  - benchmark: 0/29  weighted 0.0 [0, 0.117]
  - system: 0/29  weighted 0.0 [0, 0.117]
- state_space:
  - discrete-absorbing: 15/29  weighted 0.675 [0.415, 0.859]
  - discrete-uniform: 3/29  weighted 0.138 [0.035, 0.412]
  - discrete-flow: 1/29  weighted 0.093 [0.015, 0.408]
  - continuous-embedding: 2/29  weighted 0.043 [0.003, 0.394]
  - continuous-latent: 5/29  weighted 0.038 [0.002, 0.404]
  - hybrid: 2/29  weighted 0.009 [0.0, 0.695]
  - not_stated: 1/29  weighted 0.004 [0.0, 0.817]
- objective:
  - elbo-ce: 4/29  weighted 0.153 [0.044, 0.416]
  - weighted-ce: 1/29  weighted 0.093 [0.015, 0.408]
  - score-entropy: 0/29  weighted 0.0 [0, 0.117]
  - mse-x0: 2/29  weighted 0.025 [0.001, 0.485]
  - mse-eps-or-velocity: 1/29  weighted 0.004 [0.0, 0.817]
  - flow-matching: 3/29  weighted 0.029 [0.001, 0.452]
  - other: 9/29  weighted 0.29 [0.117, 0.557]
  - not_stated: 5/29  weighted 0.251 [0.09, 0.531]
  - NA: 4/29  weighted 0.156 [0.045, 0.418]
- position_rule:
  - left-to-right: 1/29  weighted 0.004 [0.0, 0.817]
  - random: 3/29  weighted 0.12 [0.027, 0.405]
  - confidence-ranked: 7/29  weighted 0.361 [0.159, 0.628]
  - threshold-adaptive: 1/29  weighted 0.093 [0.015, 0.408]
  - fixed-order: 1/29  weighted 0.093 [0.015, 0.408]
  - learned-planner: 0/29  weighted 0.0 [0, 0.117]
  - all-positions: 10/29  weighted 0.131 [0.04, 0.352]
  - other: 1/29  weighted 0.02 [0.0, 0.527]
  - not_stated: 5/29  weighted 0.178 [0.058, 0.433]
- blockwise:
  - yes: 9/29  weighted 0.297 [0.122, 0.563]
  - no: 15/29  weighted 0.454 [0.229, 0.7]
  - not_stated: 5/29  weighted 0.248 [0.088, 0.529]
- revision:
  - none: 10/29  weighted 0.465 [0.237, 0.708]
  - explicit-remasking-or-editing: 1/29  weighted 0.023 [0.001, 0.502]
  - corrector: 1/29  weighted 0.023 [0.001, 0.502]
  - implicit-channel: 11/29  weighted 0.224 [0.089, 0.461]
  - output-level: 0/29  weighted 0.0 [0, 0.117]
  - other: 1/29  weighted 0.004 [0.0, 0.817]
  - not_stated: 8/29  weighted 0.311 [0.131, 0.575]
- memory:
  - none: 15/29  weighted 0.54 [0.294, 0.768]
  - self-conditioning: 2/29  weighted 0.043 [0.003, 0.394]
  - exact-cache: 1/29  weighted 0.004 [0.0, 0.817]
  - approximate-cache: 1/29  weighted 0.093 [0.015, 0.408]
  - planner-state: 0/29  weighted 0.0 [0, 0.117]
  - other: 2/29  weighted 0.113 [0.023, 0.404]
  - not_stated: 8/29  weighted 0.208 [0.077, 0.451]
- training_free:
  - yes: 4/29  weighted 0.156 [0.045, 0.418]
  - no: 20/29  weighted 0.524 [0.282, 0.755]
  - not_stated: 5/29  weighted 0.321 [0.131, 0.596]
- training_stages:
  - pretraining: 5/29  weighted 0.144 [0.039, 0.411]
  - continued-pretraining: 0/29  weighted 0.0 [0, 0.117]
  - adaptation-from-ar: 2/29  weighted 0.027 [0.001, 0.466]
  - sft: 6/29  weighted 0.043 [0.003, 0.387]
  - rl: 3/29  weighted 0.208 [0.064, 0.503]
  - distillation: 2/29  weighted 0.027 [0.001, 0.466]
  - other: 10/29  weighted 0.162 [0.06, 0.37]
- credited_type:
  - model-or-architecture: 10/29  weighted 0.128 [0.039, 0.351]
  - objective-or-loss: 2/29  weighted 0.097 [0.017, 0.406]
  - training-recipe: 3/29  weighted 0.12 [0.027, 0.405]
  - sampler-or-decoding: 2/29  weighted 0.113 [0.023, 0.404]
  - caching-or-system: 1/29  weighted 0.093 [0.015, 0.408]
  - guidance-or-constraint: 2/29  weighted 0.185 [0.051, 0.491]
  - other: 3/29  weighted 0.063 [0.008, 0.357]
- F2_value_rule_stated: 12/27  weighted 0.626 [0.37, 0.826]

## RQ2
- has_ar_group: 17/29  weighted 0.492 [0.257, 0.731]
- abstract_claims_vs_ar_CT6: 4/29  weighted 0.156 [0.045, 0.418]
- ar_budget_matched_all: 0/17  weighted 0.0 [0, 0.184]
- ar_budget_not_reported_any: 16/17  weighted 0.991 [0.087, 1.0]
- ar_numbers_copied_any: 4/17  weighted 0.426 [0.15, 0.758]
- ar_variance_any: 2/17  weighted 0.093 [0.006, 0.619]
- diffusion_better_majority_of_units: 8/15  weighted 0.387 [0.111, 0.76]
- diffusion_worse_majority_of_units: 5/15  weighted 0.553 [0.206, 0.855]
- units_total: {"worse": 40, "better": 54, "tie": 2}

## RQ3
- has_training_group: 15/29  weighted 0.454 [0.229, 0.7]
- by_factor:
  - ar-initialisation: 1/29  weighted 0.004 [0.0, 0.817]
  - distillation: 2/29  weighted 0.027 [0.001, 0.466]
  - objective: 6/29  weighted 0.098 [0.022, 0.341]
  - pretraining-recipe: 3/29  weighted 0.032 [0.001, 0.437]
  - rl: 4/29  weighted 0.3 [0.117, 0.581]
  - sft: 3/29  weighted 0.047 [0.004, 0.38]
- credited_ablation_any: 4/15  weighted 0.308 [0.073, 0.717]
- held_fixed_stated_all: 3/15  weighted 0.417 [0.133, 0.769]
- variance_any: 3/15  weighted 0.11 [0.009, 0.639]
- anchor_better_majority: 7/11  weighted 0.782 [0.382, 0.954]
- units_total: {"anchor-better": 82, "anchor-worse": 44, "tie": 7}

## RQ4
- has_inference_group: 17/29  weighted 0.756 [0.524, 0.897]
- by_factor:
  - block-or-parallel: 2/29  weighted 0.04 [0.003, 0.405]
  - cache: 0/29  weighted 0.0 [0, 0.117]
  - gen-length: 2/29  weighted 0.043 [0.003, 0.394]
  - guidance: 6/29  weighted 0.255 [0.093, 0.534]
  - order-rule: 2/29  weighted 0.185 [0.051, 0.491]
  - remasking: 0/29  weighted 0.0 [0, 0.117]
  - steps-or-nfe: 10/29  weighted 0.483 [0.251, 0.723]
  - tokens-per-step: 2/29  weighted 0.097 [0.017, 0.406]
  - value-rule: 3/29  weighted 0.278 [0.102, 0.565]
- budget_reported_any: 13/17  weighted 0.723 [0.386, 0.915]
- variance_any: 6/17  weighted 0.546 [0.268, 0.798]
- dose_shapes_units: {"up": 18, "other": 2}
- any_nonmonotone_dose_curve: 1/6  weighted 0.366 [0.047, 0.872]

## RQ5
- n_mm_extracted: 7
- CT5_claim: {"no": 7}
- synergy_benchmark: {"no": 7}
- synergy_group: {"False": 4, "True": 3}
- claim_and_group: 0
- claim_without_group: []
- group_ids: {"M18816": [["shared-vs-decoupled", "Table 31", [1, 1, 1, 1]], ["shared-vs-decoupled", "Table 31", [1, 1, -1, 1]], ["shared-vs-decoupled", "Figure 34", []], ["shared-vs-decoupled", "Figure 34", []]], "M15992": [["task-or-modality-removal", "Table S7", [1, 1, 1, 1, 1]]], "M09294": [["task-or-modality-removal", "Figure 10", []]]}

## RQ6
- QA1: {"low": {"0": {"count": 17, "of": 29, "share": 0.549, "ci95": [0.301, 0.775], "by_stratum": {"G-long": "4/7", "G-mm": "6/7", "G-short": "3/8", "S-seed": "4/7"}}, "1": {"count": 12, "of": 29, "share": 0.451, "ci95": [0.225, 0.699], "by_stratum": {"G-long": "3/7", "G-mm": "1/7", "G-short": "5/8", "S-seed": "3/7"}}, "2": {"count": 0, "of": 29, "share": 0.0, "ci95": [0, 0.117], "by_stratum": {"G-long": "0/7", "G-mm": "0/7", "G-short": "0/8", "S-seed": "0/7"}}}, "high": {"0": {"count": 14, "of": 29, "share": 0.499, "ci95": [0.263, 0.735], "by_stratum": {"G-long": "2/7", "G-mm": "5/7", "G-short": "3
- QA2: {"low": {"0": {"count": 8, "of": 29, "share": 0.208, "ci95": [0.077, 0.451], "by_stratum": {"G-long": "2/7", "G-mm": "2/7", "G-short": "3/8", "S-seed": "1/7"}}, "1": {"count": 19, "of": 29, "share": 0.607, "ci95": [0.346, 0.819], "by_stratum": {"G-long": "5/7", "G-mm": "5/7", "G-short": "5/8", "S-seed": "4/7"}}, "2": {"count": 2, "of": 29, "share": 0.185, "ci95": [0.051, 0.491], "by_stratum": {"G-long": "0/7", "G-mm": "0/7", "G-short": "0/8", "S-seed": "2/7"}}}, "high": {"0": {"count": 2, "of": 29, "share": 0.027, "ci95": [0.001, 0.466], "by_stratum": {"G-long": "1/7", "G-mm": "1/7", "G-short"
- QA3: {"low": {"0": {"count": 11, "of": 29, "share": 0.288, "ci95": [0.116, 0.555], "by_stratum": {"G-long": "0/7", "G-mm": "5/7", "G-short": "4/8", "S-seed": "2/7"}}, "1": {"count": 13, "of": 29, "share": 0.477, "ci95": [0.245, 0.719], "by_stratum": {"G-long": "5/7", "G-mm": "1/7", "G-short": "4/8", "S-seed": "3/7"}}, "2": {"count": 5, "of": 29, "share": 0.235, "ci95": [0.08, 0.52], "by_stratum": {"G-long": "2/7", "G-mm": "1/7", "G-short": "0/8", "S-seed": "2/7"}}}, "high": {"0": {"count": 5, "of": 29, "share": 0.054, "ci95": [0.006, 0.367], "by_stratum": {"G-long": "0/7", "G-mm": "3/7", "G-short":
- QA4: {"low": {"0": {"count": 17, "of": 26, "share": 0.6, "ci95": [0.328, 0.821], "by_stratum": {"G-long": "3/6", "G-mm": "5/7", "G-short": "5/6", "S-seed": "4/7"}}, "1": {"count": 4, "of": 26, "share": 0.227, "ci95": [0.07, 0.531], "by_stratum": {"G-long": "1/6", "G-mm": "1/7", "G-short": "0/6", "S-seed": "2/7"}}, "2": {"count": 5, "of": 26, "share": 0.174, "ci95": [0.052, 0.444], "by_stratum": {"G-long": "2/6", "G-mm": "1/7", "G-short": "1/6", "S-seed": "1/7"}}}, "high": {"0": {"count": 17, "of": 26, "share": 0.6, "ci95": [0.328, 0.821], "by_stratum": {"G-long": "3/6", "G-mm": "5/7", "G-short": "5
- QA5: {"low": {"0": {"count": 14, "of": 26, "share": 0.378, "ci95": [0.174, 0.635], "by_stratum": {"G-long": "2/6", "G-mm": "5/7", "G-short": "5/6", "S-seed": "2/7"}}, "1": {"count": 6, "of": 26, "share": 0.424, "ci95": [0.199, 0.686], "by_stratum": {"G-long": "1/6", "G-mm": "1/7", "G-short": "0/6", "S-seed": "4/7"}}, "2": {"count": 6, "of": 26, "share": 0.198, "ci95": [0.068, 0.457], "by_stratum": {"G-long": "3/6", "G-mm": "1/7", "G-short": "1/6", "S-seed": "1/7"}}}, "high": {"0": {"count": 13, "of": 26, "share": 0.373, "ci95": [0.171, 0.632], "by_stratum": {"G-long": "2/6", "G-mm": "4/7", "G-short
- QA6: {"low": {"0": {"count": 11, "of": 26, "share": 0.233, "ci95": [0.092, 0.476], "by_stratum": {"G-long": "1/6", "G-mm": "5/7", "G-short": "4/6", "S-seed": "1/7"}}, "1": {"count": 9, "of": 26, "share": 0.4, "ci95": [0.179, 0.672], "by_stratum": {"G-long": "3/6", "G-mm": "2/7", "G-short": "1/6", "S-seed": "3/7"}}, "2": {"count": 6, "of": 26, "share": 0.367, "ci95": [0.155, 0.647], "by_stratum": {"G-long": "2/6", "G-mm": "0/7", "G-short": "1/6", "S-seed": "3/7"}}}, "high": {"0": {"count": 10, "of": 26, "share": 0.228, "ci95": [0.089, 0.473], "by_stratum": {"G-long": "1/6", "G-mm": "4/7", "G-short":
- QA7: {"low": {"0": {"count": 1, "of": 24, "share": 0.113, "ci95": [0.018, 0.472], "by_stratum": {"G-long": "0/4", "G-mm": "0/7", "G-short": "0/7", "S-seed": "1/6"}}, "1": {"count": 15, "of": 24, "share": 0.352, "ci95": [0.168, 0.595], "by_stratum": {"G-long": "3/4", "G-mm": "6/7", "G-short": "5/7", "S-seed": "1/6"}}, "2": {"count": 8, "of": 24, "share": 0.535, "ci95": [0.274, 0.777], "by_stratum": {"G-long": "1/4", "G-mm": "1/7", "G-short": "2/7", "S-seed": "4/6"}}}, "high": {"0": {"count": 1, "of": 24, "share": 0.113, "ci95": [0.018, 0.472], "by_stratum": {"G-long": "0/4", "G-mm": "0/7", "G-short"
- QA8: {"low": {"0": {"count": 2, "of": 26, "share": 0.029, "ci95": [0.001, 0.479], "by_stratum": {"G-long": "1/6", "G-mm": "1/6", "G-short": "0/7", "S-seed": "0/7"}}, "1": {"count": 13, "of": 26, "share": 0.465, "ci95": [0.228, 0.718], "by_stratum": {"G-long": "4/6", "G-mm": "3/6", "G-short": "3/7", "S-seed": "3/7"}}, "2": {"count": 11, "of": 26, "share": 0.506, "ci95": [0.262, 0.748], "by_stratum": {"G-long": "1/6", "G-mm": "2/6", "G-short": "4/7", "S-seed": "4/7"}}}, "high": {"0": {"count": 2, "of": 26, "share": 0.029, "ci95": [0.001, 0.479], "by_stratum": {"G-long": "1/6", "G-mm": "1/6", "G-short
- QA9: {"low": {"0": {"count": 1, "of": 29, "share": 0.093, "ci95": [0.015, 0.408], "by_stratum": {"G-long": "0/7", "G-mm": "0/7", "G-short": "0/8", "S-seed": "1/7"}}, "1": {"count": 8, "of": 29, "share": 0.239, "ci95": [0.1, 0.471], "by_stratum": {"G-long": "2/7", "G-mm": "0/7", "G-short": "5/8", "S-seed": "1/7"}}, "2": {"count": 20, "of": 29, "share": 0.669, "ci95": [0.411, 0.854], "by_stratum": {"G-long": "5/7", "G-mm": "7/7", "G-short": "3/8", "S-seed": "5/7"}}}, "high": {"0": {"count": 1, "of": 29, "share": 0.093, "ci95": [0.015, 0.408], "by_stratum": {"G-long": "0/7", "G-mm": "0/7", "G-short": 
- claims_status: {"direction": 33, "not-checkable": 20, "partial": 18, "match": 17, "unsupported": 4}

