# D0052 RQ results (script-generated; do not edit)

extracted 80 of 80; by stratum {'G-long': 19, 'G-mm': 20, 'G-short': 20, 'S-seed': 20}; N_h {'G-mm': 52, 'G-short': 267, 'G-long': 265, 'S-seed': 1073.8488372093022}; missing []

## RQ1
- study_type:
  - method: 72/79  weighted 0.894 [0.766, 0.956]
  - theory: 1/79  weighted 0.008 [0.0, 0.243]
  - analysis: 5/79  weighted 0.066 [0.023, 0.172]
  - benchmark: 1/79  weighted 0.032 [0.005, 0.17]
  - system: 0/79  weighted 0.0 [0, 0.046]
- state_space:
  - discrete-absorbing: 42/79  weighted 0.695 [0.55, 0.809]
  - discrete-uniform: 4/79  weighted 0.082 [0.028, 0.217]
  - discrete-flow: 2/79  weighted 0.041 [0.009, 0.164]
  - continuous-embedding: 3/79  weighted 0.025 [0.004, 0.142]
  - continuous-latent: 18/79  weighted 0.085 [0.037, 0.182]
  - hybrid: 6/79  weighted 0.036 [0.009, 0.136]
  - not_stated: 4/79  weighted 0.037 [0.007, 0.164]
- objective:
  - elbo-ce: 5/79  weighted 0.089 [0.032, 0.221]
  - weighted-ce: 12/79  weighted 0.214 [0.113, 0.366]
  - score-entropy: 0/79  weighted 0.0 [0, 0.046]
  - mse-x0: 4/79  weighted 0.019 [0.002, 0.153]
  - mse-eps-or-velocity: 4/79  weighted 0.019 [0.002, 0.153]
  - flow-matching: 7/79  weighted 0.017 [0.002, 0.152]
  - other: 24/79  weighted 0.218 [0.128, 0.347]
  - not_stated: 7/79  weighted 0.106 [0.044, 0.233]
  - NA: 16/79  weighted 0.318 [0.194, 0.475]
- position_rule:
  - left-to-right: 4/79  weighted 0.02 [0.002, 0.152]
  - random: 9/79  weighted 0.134 [0.059, 0.275]
  - confidence-ranked: 15/79  weighted 0.261 [0.149, 0.416]
  - threshold-adaptive: 10/79  weighted 0.203 [0.105, 0.357]
  - fixed-order: 1/79  weighted 0.032 [0.005, 0.17]
  - learned-planner: 1/79  weighted 0.008 [0.0, 0.236]
  - all-positions: 22/79  weighted 0.125 [0.068, 0.219]
  - other: 5/79  weighted 0.058 [0.019, 0.168]
  - not_stated: 12/79  weighted 0.158 [0.077, 0.295]
- blockwise:
  - yes: 17/79  weighted 0.247 [0.141, 0.397]
  - no: 47/79  weighted 0.522 [0.375, 0.666]
  - not_stated: 15/79  weighted 0.23 [0.127, 0.381]
- revision:
  - none: 26/79  weighted 0.423 [0.285, 0.574]
  - explicit-remasking-or-editing: 7/79  weighted 0.082 [0.034, 0.184]
  - corrector: 1/79  weighted 0.008 [0.0, 0.236]
  - implicit-channel: 28/79  weighted 0.216 [0.125, 0.346]
  - output-level: 1/79  weighted 0.008 [0.0, 0.236]
  - other: 4/79  weighted 0.074 [0.023, 0.213]
  - not_stated: 17/79  weighted 0.247 [0.14, 0.396]
- memory:
  - none: 37/79  weighted 0.541 [0.394, 0.681]
  - self-conditioning: 3/79  weighted 0.025 [0.004, 0.142]
  - exact-cache: 6/79  weighted 0.06 [0.02, 0.168]
  - approximate-cache: 3/79  weighted 0.097 [0.034, 0.249]
  - planner-state: 1/79  weighted 0.008 [0.0, 0.236]
  - other: 7/79  weighted 0.081 [0.034, 0.184]
  - not_stated: 24/79  weighted 0.203 [0.114, 0.335]
- training_free:
  - yes: 18/79  weighted 0.31 [0.188, 0.466]
  - no: 55/79  weighted 0.544 [0.396, 0.684]
  - not_stated: 6/79  weighted 0.146 [0.064, 0.298]
- training_stages:
  - pretraining: 15/79  weighted 0.193 [0.101, 0.339]
  - continued-pretraining: 10/79  weighted 0.084 [0.03, 0.216]
  - adaptation-from-ar: 5/79  weighted 0.059 [0.019, 0.169]
  - sft: 22/79  weighted 0.184 [0.094, 0.329]
  - rl: 8/79  weighted 0.108 [0.045, 0.234]
  - distillation: 4/79  weighted 0.02 [0.002, 0.152]
  - other: 21/79  weighted 0.119 [0.068, 0.199]
- credited_type:
  - model-or-architecture: 24/79  weighted 0.183 [0.098, 0.315]
  - objective-or-loss: 6/79  weighted 0.091 [0.034, 0.222]
  - training-recipe: 7/79  weighted 0.069 [0.025, 0.173]
  - sampler-or-decoding: 11/79  weighted 0.205 [0.107, 0.359]
  - caching-or-system: 3/79  weighted 0.097 [0.034, 0.249]
  - guidance-or-constraint: 5/79  weighted 0.114 [0.045, 0.259]
  - other: 6/79  weighted 0.036 [0.009, 0.136]
- F2_value_rule_stated: 38/76  weighted 0.705 [0.569, 0.812]

## RQ2
- has_ar_group: 35/79  weighted 0.463 [0.321, 0.612]
- abstract_claims_vs_ar_CT6: 10/79  weighted 0.148 [0.07, 0.287]
- ar_budget_matched_all: 0/35  weighted 0.0 [0, 0.099]
- ar_budget_not_reported_any: 31/35  weighted 0.839 [0.59, 0.949]
- ar_numbers_copied_any: 7/35  weighted 0.2 [0.075, 0.434]
- ar_variance_any: 3/35  weighted 0.054 [0.009, 0.278]
- diffusion_better_majority_of_units: 15/32  weighted 0.34 [0.162, 0.578]
- diffusion_worse_majority_of_units: 14/32  weighted 0.564 [0.332, 0.77]
- units_total: {"worse": 132, "better": 146, "tie": 2}

## RQ3
- has_training_group: 33/79  weighted 0.351 [0.227, 0.498]
- by_factor:
  - ar-initialisation: 1/79  weighted 0.002 [0.0, 0.594]
  - distillation: 3/79  weighted 0.018 [0.002, 0.157]
  - objective: 22/79  weighted 0.183 [0.105, 0.3]
  - pretraining-recipe: 6/79  weighted 0.054 [0.016, 0.165]
  - rl: 7/79  weighted 0.13 [0.057, 0.272]
  - sft: 6/79  weighted 0.03 [0.006, 0.136]
- credited_ablation_any: 9/33  weighted 0.31 [0.133, 0.569]
- held_fixed_stated_all: 6/33  weighted 0.327 [0.142, 0.588]
- variance_any: 4/33  weighted 0.076 [0.012, 0.353]
- anchor_better_majority: 20/27  weighted 0.739 [0.417, 0.918]
- units_total: {"anchor-better": 301, "anchor-worse": 113, "tie": 16}

## RQ4
- has_inference_group: 47/79  weighted 0.748 [0.609, 0.849]
- by_factor:
  - block-or-parallel: 10/79  weighted 0.179 [0.089, 0.327]
  - cache: 7/79  weighted 0.148 [0.066, 0.3]
  - gen-length: 7/79  weighted 0.075 [0.03, 0.179]
  - guidance: 13/79  weighted 0.19 [0.098, 0.337]
  - order-rule: 10/79  weighted 0.204 [0.105, 0.357]
  - remasking: 5/79  weighted 0.041 [0.011, 0.139]
  - steps-or-nfe: 18/79  weighted 0.232 [0.133, 0.374]
  - tokens-per-step: 11/79  weighted 0.181 [0.091, 0.328]
  - value-rule: 5/79  weighted 0.114 [0.045, 0.26]
- budget_reported_any: 32/47  weighted 0.594 [0.414, 0.752]
- variance_any: 12/47  weighted 0.262 [0.138, 0.441]
- dose_shapes_units: {"up": 132, "other": 14, "down": 19, "peaked": 16}
- any_nonmonotone_dose_curve: 10/19  weighted 0.62 [0.34, 0.837]

## RQ5
- n_mm_extracted: 20
- CT5_claim: {"no": 17, "yes": 3}
- synergy_benchmark: {"no": 20}
- synergy_group: {"False": 12, "True": 8}
- claim_and_group: 2
- claim_without_group: ["R0963"]
- group_ids: {"M18816": [["shared-vs-decoupled", "Table 31", [1, 1, 1, 1]], ["shared-vs-decoupled", "Table 31", [1, 1, -1, 1]], ["shared-vs-decoupled", "Figure 34", []], ["shared-vs-decoupled", "Figure 34", []]], "M15992": [["task-or-modality-removal", "Table S7", [1, 1, 1, 1, 1]]], "M09294": [["task-or-modality-removal", "Figure 10", []]], "M19012": [["task-or-modality-removal", "Table 4", []]], "M19293": [["task-or-modality-removal", "Table 6", []], ["task-or-modality-removal", "Table 6", []], ["task-or-modality-removal", "Table 7", [-1, -1, -1, 0, -1, -1]]], "M15792": [["task-or-modality-removal", "Tabl

## RQ6
- QA1: {"low": {"0": {"count": 45, "of": 79, "share": 0.555, "ci95": [0.406, 0.696], "by_stratum": {"G-long": "9/19", "G-mm": "12/20", "G-short": "13/20", "S-seed": "11/20"}}, "1": {"count": 17, "of": 79, "share": 0.125, "ci95": [0.067, 0.22], "by_stratum": {"G-long": "7/19", "G-mm": "6/20", "G-short": "3/20", "S-seed": "1/20"}}, "2": {"count": 17, "of": 79, "share": 0.32, "ci95": [0.195, 0.476], "by_stratum": {"G-long": "3/19", "G-mm": "2/20", "G-short": "4/20", "S-seed": "8/20"}}}, "high": {"0": {"count": 39, "of": 79, "share": 0.526, "ci95": [0.379, 0.668], "by_stratum": {"G-long": "6/19", "G-mm":
- QA2: {"low": {"0": {"count": 21, "of": 79, "share": 0.198, "ci95": [0.11, 0.33], "by_stratum": {"G-long": "3/19", "G-mm": "7/20", "G-short": "8/20", "S-seed": "3/20"}}, "1": {"count": 54, "of": 79, "share": 0.697, "ci95": [0.545, 0.815], "by_stratum": {"G-long": "15/19", "G-mm": "13/20", "G-short": "12/20", "S-seed": "14/20"}}, "2": {"count": 4, "of": 79, "share": 0.106, "ci95": [0.039, 0.254], "by_stratum": {"G-long": "1/19", "G-mm": "0/20", "G-short": "0/20", "S-seed": "3/20"}}}, "high": {"0": {"count": 10, "of": 79, "share": 0.104, "ci95": [0.043, 0.23], "by_stratum": {"G-long": "1/19", "G-mm": 
- QA3: {"low": {"0": {"count": 27, "of": 79, "share": 0.206, "ci95": [0.119, 0.335], "by_stratum": {"G-long": "1/19", "G-mm": "13/20", "G-short": "10/20", "S-seed": "3/20"}}, "1": {"count": 37, "of": 79, "share": 0.537, "ci95": [0.389, 0.679], "by_stratum": {"G-long": "11/19", "G-mm": "5/20", "G-short": "10/20", "S-seed": "11/20"}}, "2": {"count": 15, "of": 79, "share": 0.256, "ci95": [0.146, 0.411], "by_stratum": {"G-long": "7/19", "G-mm": "2/20", "G-short": "0/20", "S-seed": "6/20"}}}, "high": {"0": {"count": 17, "of": 79, "share": 0.109, "ci95": [0.056, 0.203], "by_stratum": {"G-long": "0/19", "G-
- QA4: {"low": {"0": {"count": 51, "of": 74, "share": 0.736, "ci95": [0.592, 0.842], "by_stratum": {"G-long": "8/18", "G-mm": "15/20", "G-short": "12/16", "S-seed": "16/20"}}, "1": {"count": 12, "of": 74, "share": 0.165, "ci95": [0.081, 0.307], "by_stratum": {"G-long": "5/18", "G-mm": "2/20", "G-short": "2/16", "S-seed": "3/20"}}, "2": {"count": 11, "of": 74, "share": 0.099, "ci95": [0.046, 0.202], "by_stratum": {"G-long": "5/18", "G-mm": "3/20", "G-short": "2/16", "S-seed": "1/20"}}}, "high": {"0": {"count": 50, "of": 74, "share": 0.727, "ci95": [0.584, 0.835], "by_stratum": {"G-long": "8/18", "G-mm
- QA5: {"low": {"0": {"count": 49, "of": 74, "share": 0.668, "ci95": [0.514, 0.793], "by_stratum": {"G-long": "8/18", "G-mm": "15/20", "G-short": "12/16", "S-seed": "14/20"}}, "1": {"count": 15, "of": 74, "share": 0.227, "ci95": [0.121, 0.384], "by_stratum": {"G-long": "3/18", "G-mm": "4/20", "G-short": "3/16", "S-seed": "5/20"}}, "2": {"count": 10, "of": 74, "share": 0.105, "ci95": [0.051, 0.205], "by_stratum": {"G-long": "7/18", "G-mm": "1/20", "G-short": "1/16", "S-seed": "1/20"}}}, "high": {"0": {"count": 47, "of": 74, "share": 0.633, "ci95": [0.477, 0.765], "by_stratum": {"G-long": "8/18", "G-mm
- QA6: {"low": {"0": {"count": 20, "of": 74, "share": 0.145, "ci95": [0.073, 0.267], "by_stratum": {"G-long": "1/18", "G-mm": "11/20", "G-short": "6/16", "S-seed": "2/20"}}, "1": {"count": 28, "of": 74, "share": 0.354, "ci95": [0.223, 0.512], "by_stratum": {"G-long": "7/18", "G-mm": "9/20", "G-short": "5/16", "S-seed": "7/20"}}, "2": {"count": 26, "of": 74, "share": 0.501, "ci95": [0.351, 0.651], "by_stratum": {"G-long": "10/18", "G-mm": "0/20", "G-short": "5/16", "S-seed": "11/20"}}}, "high": {"0": {"count": 19, "of": 74, "share": 0.143, "ci95": [0.071, 0.266], "by_stratum": {"G-long": "1/18", "G-mm
- QA7: {"low": {"0": {"count": 7, "of": 72, "share": 0.111, "ci95": [0.044, 0.252], "by_stratum": {"G-long": "1/16", "G-mm": "1/20", "G-short": "3/18", "S-seed": "2/18"}}, "1": {"count": 39, "of": 72, "share": 0.363, "ci95": [0.24, 0.506], "by_stratum": {"G-long": "10/16", "G-mm": "14/20", "G-short": "11/18", "S-seed": "4/18"}}, "2": {"count": 26, "of": 72, "share": 0.527, "ci95": [0.379, 0.67], "by_stratum": {"G-long": "5/16", "G-mm": "5/20", "G-short": "4/18", "S-seed": "12/18"}}}, "high": {"0": {"count": 6, "of": 72, "share": 0.102, "ci95": [0.038, 0.245], "by_stratum": {"G-long": "1/16", "G-mm": 
- QA8: {"low": {"0": {"count": 10, "of": 74, "share": 0.146, "ci95": [0.067, 0.289], "by_stratum": {"G-long": "1/17", "G-mm": "2/19", "G-short": "4/18", "S-seed": "3/20"}}, "1": {"count": 26, "of": 74, "share": 0.363, "ci95": [0.231, 0.519], "by_stratum": {"G-long": "8/17", "G-mm": "5/19", "G-short": "6/18", "S-seed": "7/20"}}, "2": {"count": 38, "of": 74, "share": 0.491, "ci95": [0.342, 0.642], "by_stratum": {"G-long": "8/17", "G-mm": "12/19", "G-short": "8/18", "S-seed": "10/20"}}}, "high": {"0": {"count": 10, "of": 74, "share": 0.146, "ci95": [0.067, 0.289], "by_stratum": {"G-long": "1/17", "G-mm"
- QA9: {"low": {"0": {"count": 1, "of": 79, "share": 0.032, "ci95": [0.005, 0.17], "by_stratum": {"G-long": "0/19", "G-mm": "0/20", "G-short": "0/20", "S-seed": "1/20"}}, "1": {"count": 26, "of": 79, "share": 0.271, "ci95": [0.166, 0.41], "by_stratum": {"G-long": "8/19", "G-mm": "6/20", "G-short": "8/20", "S-seed": "4/20"}}, "2": {"count": 52, "of": 79, "share": 0.697, "ci95": [0.552, 0.811], "by_stratum": {"G-long": "11/19", "G-mm": "14/20", "G-short": "12/20", "S-seed": "15/20"}}}, "high": {"0": {"count": 1, "of": 79, "share": 0.032, "ci95": [0.005, 0.17], "by_stratum": {"G-long": "0/19", "G-mm": "
- claims_status: {"direction": 83, "not-checkable": 50, "partial": 46, "match": 63, "unsupported": 12}

## Sensitivity
rejected at final pass (S2 drops them): ['M04407', 'M06241', 'M06272', 'M07124', 'M08783', 'M09294', 'M10526', 'M10840', 'M10855', 'M12084', 'M12879', 'M12960', 'M13081', 'M13234', 'M13760', 'M13884', 'M14267', 'M15781', 'M15840', 'M16080', 'M16729', 'M17249', 'M17725', 'M19099', 'R0588', 'R0621', 'R0631', 'R0674', 'R1004', 'R1124']

| estimate | S0 main | S1 update strata only | S2 without rejected | S3 second-reader ids from EB |
|---|---|---|---|---|
| census_nonplain_or_unstated | 74/76  weighted 0.983 [0.832, 0.998] | 54/56  weighted 0.949 [0.818, 0.987] | 47/48  weighted 0.982 [0.714, 0.999] | 74/76  weighted 0.983 [0.832, 0.998] |
| RQ2_has_ar_group | 35/79  weighted 0.463 [0.321, 0.612] | 25/59  weighted 0.396 [0.27, 0.536] | 21/49  weighted 0.474 [0.303, 0.652] | 35/79  weighted 0.463 [0.321, 0.612] |
| RQ2_ar_budget_not_reported_any | 31/35  weighted 0.839 [0.59, 0.949] | 23/25  weighted 0.928 [0.673, 0.988] | 19/21  weighted 0.898 [0.556, 0.984] | 31/35  weighted 0.839 [0.59, 0.949] |
| RQ2_ar_numbers_copied_any | 7/35  weighted 0.2 [0.075, 0.434] | 5/25  weighted 0.198 [0.077, 0.425] | 3/21  weighted 0.139 [0.032, 0.443] | 7/35  weighted 0.2 [0.075, 0.434] |
| RQ2_ar_variance_any | 3/35  weighted 0.054 [0.009, 0.278] | 3/25  weighted 0.181 [0.064, 0.419] | 1/21  weighted 0.037 [0.002, 0.482] | 3/35  weighted 0.054 [0.009, 0.278] |
| RQ3_credited_ablation_any | 9/33  weighted 0.31 [0.133, 0.569] | 7/27  weighted 0.282 [0.137, 0.492] | 5/22  weighted 0.25 [0.083, 0.55] | 9/32  weighted 0.342 [0.148, 0.609] |
| RQ3_held_fixed_stated_all | 6/33  weighted 0.327 [0.142, 0.588] | 3/27  weighted 0.113 [0.032, 0.326] | 5/22  weighted 0.39 [0.167, 0.671] | 6/32  weighted 0.361 [0.166, 0.616] |
| RQ3_variance_any | 4/33  weighted 0.076 [0.012, 0.353] | 4/27  weighted 0.171 [0.061, 0.397] | 3/22  weighted 0.092 [0.012, 0.457] | 4/32  weighted 0.084 [0.013, 0.383] |
| RQ4_has_inference_group | 47/79  weighted 0.748 [0.609, 0.849] | 31/59  weighted 0.651 [0.522, 0.762] | 22/49  weighted 0.628 [0.458, 0.772] | 47/79  weighted 0.748 [0.609, 0.849] |
| RQ4_budget_reported_any | 32/47  weighted 0.594 [0.414, 0.752] | 24/31  weighted 0.806 [0.631, 0.91] | 13/22  weighted 0.524 [0.305, 0.734] | 33/47  weighted 0.637 [0.453, 0.788] |
| RQ4_variance_any | 12/47  weighted 0.262 [0.138, 0.441] | 8/31  weighted 0.29 [0.158, 0.471] | 6/22  weighted 0.26 [0.111, 0.498] | 12/47  weighted 0.262 [0.138, 0.441] |
| RQ4_any_nonmonotone_dose_curve | 10/19  weighted 0.62 [0.34, 0.837] | 7/15  weighted 0.467 [0.249, 0.699] | 4/7  weighted 0.602 [0.163, 0.922] | 9/18  weighted 0.56 [0.266, 0.818] |

