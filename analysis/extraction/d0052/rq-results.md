# D0052 RQ results (script-generated; do not edit)

extracted 27 of 80; by stratum {'G-long': 7, 'G-mm': 7, 'G-short': 8, 'S-seed': 5}; N_h {'G-mm': 52, 'G-short': 267, 'G-long': 265, 'S-seed': 1073.8488372093022}; missing ['M03150', 'M03633', 'M04407', 'M06272', 'M07646', 'M10526', 'M10840', 'M10855', 'M11180', 'M12084', 'M12879', 'M12960', 'M13371', 'M13884', 'M14280', 'M14293', 'M14326', 'M15033', 'M15781', 'M15792', 'M15840', 'M16080', 'M16154', 'M16269', 'M17249', 'M17285', 'M17725', 'M17834', 'M18059', 'M18141', 'M18735', 'M18994', 'M19012', 'M19013', 'M19021', 'M19099', 'M19293', 'R0021', 'R0121', 'R0171', 'R0188', 'R0214', 'R0291', 'R0588', 'R0621', 'R0631', 'R0677', 'R0717', 'R0738', 'R0865', 'R0958', 'R0963', 'R1004']

## RQ1
- study_type:
  - method: 22/27  weighted 0.782 [0.463, 0.937]
  - theory: 1/27  weighted 0.02 [0.0, 0.676]
  - analysis: 4/27  weighted 0.198 [0.052, 0.527]
  - benchmark: 0/27  weighted 0.0 [0, 0.125]
  - system: 0/27  weighted 0.0 [0, 0.125]
- state_space:
  - discrete-absorbing: 14/27  weighted 0.73 [0.433, 0.906]
  - discrete-uniform: 2/27  weighted 0.046 [0.002, 0.525]
  - discrete-flow: 1/27  weighted 0.13 [0.021, 0.512]
  - continuous-embedding: 2/27  weighted 0.043 [0.002, 0.533]
  - continuous-latent: 5/27  weighted 0.038 [0.001, 0.55]
  - hybrid: 2/27  weighted 0.009 [0.0, 0.814]
  - not_stated: 1/27  weighted 0.004 [0.0, 0.896]
- objective:
  - elbo-ce: 4/27  weighted 0.19 [0.048, 0.523]
  - weighted-ce: 1/27  weighted 0.13 [0.021, 0.512]
  - score-entropy: 0/27  weighted 0.0 [0, 0.125]
  - mse-x0: 2/27  weighted 0.025 [0.0, 0.636]
  - mse-eps-or-velocity: 1/27  weighted 0.004 [0.0, 0.896]
  - flow-matching: 3/27  weighted 0.029 [0.001, 0.602]
  - other: 8/27  weighted 0.234 [0.073, 0.543]
  - not_stated: 5/27  weighted 0.325 [0.111, 0.649]
  - NA: 3/27  weighted 0.063 [0.005, 0.477]
- position_rule:
  - left-to-right: 1/27  weighted 0.004 [0.0, 0.896]
  - random: 3/27  weighted 0.157 [0.032, 0.513]
  - confidence-ranked: 7/27  weighted 0.472 [0.211, 0.749]
  - threshold-adaptive: 0/27  weighted 0.0 [0, 0.125]
  - fixed-order: 0/27  weighted 0.0 [0, 0.125]
  - learned-planner: 0/27  weighted 0.0 [0, 0.125]
  - all-positions: 10/27  weighted 0.131 [0.029, 0.435]
  - other: 1/27  weighted 0.02 [0.0, 0.676]
  - not_stated: 5/27  weighted 0.215 [0.061, 0.536]
- blockwise:
  - yes: 8/27  weighted 0.242 [0.077, 0.549]
  - no: 14/27  weighted 0.436 [0.185, 0.724]
  - not_stated: 5/27  weighted 0.322 [0.11, 0.647]
- revision:
  - none: 9/27  weighted 0.484 [0.219, 0.758]
  - explicit-remasking-or-editing: 1/27  weighted 0.023 [0.0, 0.652]
  - corrector: 1/27  weighted 0.023 [0.0, 0.652]
  - implicit-channel: 10/27  weighted 0.131 [0.029, 0.435]
  - output-level: 0/27  weighted 0.0 [0, 0.125]
  - other: 1/27  weighted 0.004 [0.0, 0.896]
  - not_stated: 8/27  weighted 0.385 [0.15, 0.69]
- memory:
  - none: 14/27  weighted 0.558 [0.27, 0.812]
  - self-conditioning: 2/27  weighted 0.043 [0.002, 0.533]
  - exact-cache: 1/27  weighted 0.004 [0.0, 0.896]
  - approximate-cache: 0/27  weighted 0.0 [0, 0.125]
  - planner-state: 0/27  weighted 0.0 [0, 0.125]
  - other: 2/27  weighted 0.15 [0.029, 0.512]
  - not_stated: 8/27  weighted 0.245 [0.078, 0.552]
- training_free:
  - yes: 3/27  weighted 0.063 [0.005, 0.477]
  - no: 19/27  weighted 0.505 [0.234, 0.774]
  - not_stated: 5/27  weighted 0.432 [0.184, 0.718]
- training_stages:
  - pretraining: 4/27  weighted 0.052 [0.003, 0.501]
  - continued-pretraining: 0/27  weighted 0.0 [0, 0.125]
  - adaptation-from-ar: 2/27  weighted 0.027 [0.0, 0.616]
  - sft: 6/27  weighted 0.043 [0.002, 0.53]
  - rl: 3/27  weighted 0.282 [0.086, 0.621]
  - distillation: 2/27  weighted 0.027 [0.0, 0.616]
  - other: 10/27  weighted 0.162 [0.045, 0.444]
- credited_type:
  - model-or-architecture: 10/27  weighted 0.128 [0.027, 0.435]
  - objective-or-loss: 1/27  weighted 0.004 [0.0, 0.896]
  - training-recipe: 3/27  weighted 0.157 [0.032, 0.513]
  - sampler-or-decoding: 2/27  weighted 0.15 [0.029, 0.512]
  - caching-or-system: 0/27  weighted 0.0 [0, 0.125]
  - guidance-or-constraint: 2/27  weighted 0.259 [0.073, 0.608]
  - other: 3/27  weighted 0.063 [0.005, 0.477]
- F2_value_rule_stated: 10/25  weighted 0.548 [0.256, 0.811]

## RQ2
- has_ar_group: 16/27  weighted 0.473 [0.211, 0.752]
- abstract_claims_vs_ar_CT6: 4/27  weighted 0.193 [0.049, 0.525]
- ar_budget_matched_all: 0/16  weighted 0.0 [0, 0.194]
- ar_budget_not_reported_any: 15/16  weighted 0.991 [0.039, 1.0]
- ar_numbers_copied_any: 3/16  weighted 0.326 [0.056, 0.796]
- ar_variance_any: 2/16  weighted 0.096 [0.003, 0.775]
- diffusion_better_majority_of_units: 8/14  weighted 0.489 [0.11, 0.881]
- diffusion_worse_majority_of_units: 4/14  weighted 0.447 [0.093, 0.865]
- units_total: {"worse": 36, "better": 53, "tie": 2}

## RQ3
- has_training_group: 15/27  weighted 0.565 [0.277, 0.816]
- by_factor:
  - ar-initialisation: 1/27  weighted 0.004 [0.0, 0.896]
  - distillation: 2/27  weighted 0.027 [0.0, 0.616]
  - objective: 6/27  weighted 0.098 [0.015, 0.439]
  - pretraining-recipe: 3/27  weighted 0.032 [0.001, 0.586]
  - rl: 4/27  weighted 0.411 [0.171, 0.704]
  - sft: 3/27  weighted 0.047 [0.002, 0.515]
- credited_ablation_any: 4/15  weighted 0.313 [0.066, 0.745]
- held_fixed_stated_all: 3/15  weighted 0.466 [0.145, 0.818]
- variance_any: 3/15  weighted 0.089 [0.004, 0.692]
- anchor_better_majority: 7/11  weighted 0.782 [0.382, 0.954]
- units_total: {"anchor-better": 82, "anchor-worse": 44, "tie": 7}

## RQ4
- has_inference_group: 16/27  weighted 0.849 [0.56, 0.961]
- by_factor:
  - block-or-parallel: 2/27  weighted 0.04 [0.001, 0.545]
  - cache: 0/27  weighted 0.0 [0, 0.125]
  - gen-length: 2/27  weighted 0.043 [0.002, 0.533]
  - guidance: 6/27  weighted 0.329 [0.114, 0.652]
  - order-rule: 2/27  weighted 0.259 [0.073, 0.608]
  - remasking: 0/27  weighted 0.0 [0, 0.125]
  - steps-or-nfe: 10/27  weighted 0.631 [0.366, 0.836]
  - tokens-per-step: 1/27  weighted 0.004 [0.0, 0.896]
  - value-rule: 3/27  weighted 0.389 [0.156, 0.687]
- budget_reported_any: 13/16  weighted 0.818 [0.427, 0.965]
- variance_any: 6/16  weighted 0.661 [0.352, 0.875]
- dose_shapes_units: {"up": 18, "other": 2}
- any_nonmonotone_dose_curve: 1/6  weighted 0.397 [0.05, 0.892]

## RQ5
- n_mm_extracted: 7
- CT5_claim: {"no": 7}
- synergy_benchmark: {"no": 7}
- synergy_group: {"False": 4, "True": 3}
- claim_and_group: 0
- claim_without_group: []
- group_ids: {"M18816": [["shared-vs-decoupled", "Table 31", [1, 1, 1, 1]], ["shared-vs-decoupled", "Table 31", [1, 1, -1, 1]], ["shared-vs-decoupled", "Figure 34", []], ["shared-vs-decoupled", "Figure 34", []]], "M15992": [["task-or-modality-removal", "Table S7", [1, 1, 1, 1, 1]]], "M09294": [["task-or-modality-removal", "Figure 10", []]]}

## RQ6
- QA1: {"low": {"0": {"count": 16, "of": 27, "share": 0.567, "ci95": [0.277, 0.818], "by_stratum": {"G-long": "4/7", "G-mm": "6/7", "G-short": "3/8", "S-seed": "3/5"}}, "1": {"count": 11, "of": 27, "share": 0.433, "ci95": [0.182, 0.723], "by_stratum": {"G-long": "3/7", "G-mm": "1/7", "G-short": "5/8", "S-seed": "2/5"}}, "2": {"count": 0, "of": 27, "share": 0.0, "ci95": [0, 0.125], "by_stratum": {"G-long": "0/7", "G-mm": "0/7", "G-short": "0/8", "S-seed": "0/5"}}}, "high": {"0": {"count": 13, "of": 27, "share": 0.517, "ci95": [0.242, 0.782], "by_stratum": {"G-long": "2/7", "G-mm": "5/7", "G-short": "3
- QA2: {"low": {"0": {"count": 8, "of": 27, "share": 0.245, "ci95": [0.078, 0.552], "by_stratum": {"G-long": "2/7", "G-mm": "2/7", "G-short": "3/8", "S-seed": "1/5"}}, "1": {"count": 17, "of": 27, "share": 0.496, "ci95": [0.227, 0.767], "by_stratum": {"G-long": "5/7", "G-mm": "5/7", "G-short": "5/8", "S-seed": "2/5"}}, "2": {"count": 2, "of": 27, "share": 0.259, "ci95": [0.073, 0.608], "by_stratum": {"G-long": "0/7", "G-mm": "0/7", "G-short": "0/8", "S-seed": "2/5"}}}, "high": {"0": {"count": 2, "of": 27, "share": 0.027, "ci95": [0.0, 0.616], "by_stratum": {"G-long": "1/7", "G-mm": "1/7", "G-short": 
- QA3: {"low": {"0": {"count": 11, "of": 27, "share": 0.362, "ci95": [0.136, 0.672], "by_stratum": {"G-long": "0/7", "G-mm": "5/7", "G-short": "4/8", "S-seed": "2/5"}}, "1": {"count": 12, "of": 27, "share": 0.458, "ci95": [0.2, 0.741], "by_stratum": {"G-long": "5/7", "G-mm": "1/7", "G-short": "4/8", "S-seed": "2/5"}}, "2": {"count": 4, "of": 27, "share": 0.18, "ci95": [0.042, 0.52], "by_stratum": {"G-long": "2/7", "G-mm": "1/7", "G-short": "0/8", "S-seed": "1/5"}}}, "high": {"0": {"count": 5, "of": 27, "share": 0.054, "ci95": [0.003, 0.497], "by_stratum": {"G-long": "0/7", "G-mm": "3/7", "G-short": "
- QA4: {"low": {"0": {"count": 15, "of": 24, "share": 0.481, "ci95": [0.206, 0.768], "by_stratum": {"G-long": "3/6", "G-mm": "5/7", "G-short": "5/6", "S-seed": "2/5"}}, "1": {"count": 4, "of": 24, "share": 0.306, "ci95": [0.093, 0.653], "by_stratum": {"G-long": "1/6", "G-mm": "1/7", "G-short": "0/6", "S-seed": "2/5"}}, "2": {"count": 5, "of": 24, "share": 0.213, "ci95": [0.056, 0.553], "by_stratum": {"G-long": "2/6", "G-mm": "1/7", "G-short": "1/6", "S-seed": "1/5"}}}, "high": {"0": {"count": 15, "of": 24, "share": 0.481, "ci95": [0.206, 0.768], "by_stratum": {"G-long": "3/6", "G-mm": "5/7", "G-short
- QA5: {"low": {"0": {"count": 12, "of": 24, "share": 0.18, "ci95": [0.054, 0.46], "by_stratum": {"G-long": "2/6", "G-mm": "5/7", "G-short": "5/6", "S-seed": "0/5"}}, "1": {"count": 6, "of": 24, "share": 0.582, "ci95": [0.321, 0.804], "by_stratum": {"G-long": "1/6", "G-mm": "1/7", "G-short": "0/6", "S-seed": "4/5"}}, "2": {"count": 6, "of": 24, "share": 0.238, "ci95": [0.07, 0.565], "by_stratum": {"G-long": "3/6", "G-mm": "1/7", "G-short": "1/6", "S-seed": "1/5"}}}, "high": {"0": {"count": 11, "of": 24, "share": 0.175, "ci95": [0.051, 0.458], "by_stratum": {"G-long": "2/6", "G-mm": "4/7", "G-short": 
- QA6: {"low": {"0": {"count": 11, "of": 24, "share": 0.273, "ci95": [0.091, 0.582], "by_stratum": {"G-long": "1/6", "G-mm": "5/7", "G-short": "4/6", "S-seed": "1/5"}}, "1": {"count": 7, "of": 24, "share": 0.242, "ci95": [0.072, 0.567], "by_stratum": {"G-long": "3/6", "G-mm": "2/7", "G-short": "1/6", "S-seed": "1/5"}}, "2": {"count": 6, "of": 24, "share": 0.485, "ci95": [0.209, 0.77], "by_stratum": {"G-long": "2/6", "G-mm": "0/7", "G-short": "1/6", "S-seed": "3/5"}}}, "high": {"0": {"count": 10, "of": 24, "share": 0.268, "ci95": [0.088, 0.58], "by_stratum": {"G-long": "1/6", "G-mm": "4/7", "G-short":
- QA7: {"low": {"0": {"count": 0, "of": 22, "share": 0.0, "ci95": [0, 0.149], "by_stratum": {"G-long": "0/4", "G-mm": "0/7", "G-short": "0/7", "S-seed": "0/4"}}, "1": {"count": 15, "of": 22, "share": 0.416, "ci95": [0.164, 0.721], "by_stratum": {"G-long": "3/4", "G-mm": "6/7", "G-short": "5/7", "S-seed": "1/4"}}, "2": {"count": 7, "of": 22, "share": 0.584, "ci95": [0.279, 0.836], "by_stratum": {"G-long": "1/4", "G-mm": "1/7", "G-short": "2/7", "S-seed": "3/4"}}}, "high": {"0": {"count": 0, "of": 22, "share": 0.0, "ci95": [0, 0.149], "by_stratum": {"G-long": "0/4", "G-mm": "0/7", "G-short": "0/7", "S-
- QA8: {"low": {"0": {"count": 2, "of": 24, "share": 0.029, "ci95": [0.001, 0.628], "by_stratum": {"G-long": "1/6", "G-mm": "1/6", "G-short": "0/7", "S-seed": "0/5"}}, "1": {"count": 13, "of": 24, "share": 0.581, "ci95": [0.277, 0.835], "by_stratum": {"G-long": "4/6", "G-mm": "3/6", "G-short": "3/7", "S-seed": "3/5"}}, "2": {"count": 9, "of": 24, "share": 0.39, "ci95": [0.147, 0.703], "by_stratum": {"G-long": "1/6", "G-mm": "2/6", "G-short": "4/7", "S-seed": "2/5"}}}, "high": {"0": {"count": 2, "of": 24, "share": 0.029, "ci95": [0.001, 0.628], "by_stratum": {"G-long": "1/6", "G-mm": "1/6", "G-short":
- QA9: {"low": {"0": {"count": 1, "of": 27, "share": 0.13, "ci95": [0.021, 0.512], "by_stratum": {"G-long": "0/7", "G-mm": "0/7", "G-short": "0/8", "S-seed": "1/5"}}, "1": {"count": 7, "of": 27, "share": 0.146, "ci95": [0.037, 0.436], "by_stratum": {"G-long": "2/7", "G-mm": "0/7", "G-short": "5/8", "S-seed": "0/5"}}, "2": {"count": 19, "of": 27, "share": 0.724, "ci95": [0.43, 0.901], "by_stratum": {"G-long": "5/7", "G-mm": "7/7", "G-short": "3/8", "S-seed": "4/5"}}}, "high": {"0": {"count": 1, "of": 27, "share": 0.13, "ci95": [0.021, 0.512], "by_stratum": {"G-long": "0/7", "G-mm": "0/7", "G-short": "
- claims_status: {"direction": 27, "not-checkable": 19, "partial": 18, "match": 16, "unsupported": 4}

