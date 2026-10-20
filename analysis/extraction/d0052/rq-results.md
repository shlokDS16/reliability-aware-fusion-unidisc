# D0052 RQ results (script-generated; do not edit)

extracted 57 of 80; by stratum {'G-long': 11, 'G-mm': 12, 'G-short': 14, 'S-seed': 20}; N_h {'G-mm': 52, 'G-short': 267, 'G-long': 265, 'S-seed': 1073.8488372093022}; missing ['M03150', 'M03633', 'M04407', 'M06272', 'M10855', 'M12960', 'M13371', 'M13884', 'M14293', 'M15033', 'M15781', 'M15840', 'M16080', 'M16269', 'M17249', 'M17285', 'M17725', 'M17834', 'M18059', 'M18994', 'M19013', 'M19021', 'M19099']

## RQ1
- study_type:
  - method: 51/57  weighted 0.88 [0.747, 0.948]
  - theory: 1/57  weighted 0.012 [0.0, 0.223]
  - analysis: 4/57  weighted 0.076 [0.028, 0.192]
  - benchmark: 1/57  weighted 0.032 [0.005, 0.18]
  - system: 0/57  weighted 0.0 [0, 0.063]
- state_space:
  - discrete-absorbing: 32/57  weighted 0.703 [0.551, 0.819]
  - discrete-uniform: 4/57  weighted 0.094 [0.034, 0.232]
  - discrete-flow: 2/57  weighted 0.047 [0.011, 0.173]
  - continuous-embedding: 2/57  weighted 0.026 [0.004, 0.157]
  - continuous-latent: 12/57  weighted 0.079 [0.032, 0.183]
  - hybrid: 3/57  weighted 0.017 [0.001, 0.179]
  - not_stated: 2/57  weighted 0.035 [0.006, 0.176]
- objective:
  - elbo-ce: 5/57  weighted 0.099 [0.038, 0.235]
  - weighted-ce: 9/57  weighted 0.217 [0.114, 0.374]
  - score-entropy: 0/57  weighted 0.0 [0, 0.063]
  - mse-x0: 4/57  weighted 0.028 [0.005, 0.155]
  - mse-eps-or-velocity: 1/57  weighted 0.003 [0.0, 0.512]
  - flow-matching: 6/57  weighted 0.025 [0.004, 0.151]
  - other: 13/57  weighted 0.192 [0.102, 0.331]
  - not_stated: 7/57  weighted 0.128 [0.058, 0.26]
  - NA: 12/57  weighted 0.308 [0.184, 0.468]
- position_rule:
  - left-to-right: 1/57  weighted 0.003 [0.0, 0.512]
  - random: 6/57  weighted 0.129 [0.054, 0.277]
  - confidence-ranked: 13/57  weighted 0.284 [0.165, 0.443]
  - threshold-adaptive: 7/57  weighted 0.185 [0.089, 0.344]
  - fixed-order: 1/57  weighted 0.032 [0.005, 0.18]
  - learned-planner: 1/57  weighted 0.015 [0.001, 0.199]
  - all-positions: 17/57  weighted 0.146 [0.08, 0.251]
  - other: 4/57  weighted 0.058 [0.017, 0.176]
  - not_stated: 7/57  weighted 0.149 [0.069, 0.295]
- blockwise:
  - yes: 13/57  weighted 0.239 [0.132, 0.393]
  - no: 34/57  weighted 0.538 [0.387, 0.683]
  - not_stated: 10/57  weighted 0.222 [0.119, 0.378]
- revision:
  - none: 18/57  weighted 0.407 [0.268, 0.563]
  - explicit-remasking-or-editing: 5/57  weighted 0.087 [0.035, 0.2]
  - corrector: 1/57  weighted 0.015 [0.001, 0.199]
  - implicit-channel: 21/57  weighted 0.227 [0.131, 0.365]
  - output-level: 0/57  weighted 0.0 [0, 0.063]
  - other: 3/57  weighted 0.067 [0.019, 0.216]
  - not_stated: 13/57  weighted 0.26 [0.149, 0.414]
- memory:
  - none: 32/57  weighted 0.578 [0.423, 0.719]
  - self-conditioning: 2/57  weighted 0.026 [0.004, 0.157]
  - exact-cache: 4/57  weighted 0.049 [0.013, 0.171]
  - approximate-cache: 3/57  weighted 0.097 [0.033, 0.253]
  - planner-state: 0/57  weighted 0.0 [0, 0.063]
  - other: 4/57  weighted 0.07 [0.024, 0.184]
  - not_stated: 12/57  weighted 0.18 [0.092, 0.322]
- training_free:
  - yes: 13/57  weighted 0.305 [0.181, 0.466]
  - no: 38/57  weighted 0.54 [0.387, 0.685]
  - not_stated: 6/57  weighted 0.156 [0.07, 0.31]
- training_stages:
  - pretraining: 10/57  weighted 0.175 [0.085, 0.326]
  - continued-pretraining: 3/57  weighted 0.067 [0.019, 0.216]
  - adaptation-from-ar: 4/57  weighted 0.064 [0.021, 0.182]
  - sft: 13/57  weighted 0.174 [0.085, 0.323]
  - rl: 6/57  weighted 0.117 [0.05, 0.25]
  - distillation: 3/57  weighted 0.02 [0.002, 0.17]
  - other: 17/57  weighted 0.142 [0.083, 0.235]
- credited_type:
  - model-or-architecture: 18/57  weighted 0.205 [0.113, 0.343]
  - objective-or-loss: 3/57  weighted 0.067 [0.019, 0.216]
  - training-recipe: 5/57  weighted 0.076 [0.028, 0.189]
  - sampler-or-decoding: 8/57  weighted 0.203 [0.103, 0.361]
  - caching-or-system: 3/57  weighted 0.097 [0.033, 0.253]
  - guidance-or-constraint: 4/57  weighted 0.112 [0.043, 0.262]
  - other: 5/57  weighted 0.043 [0.011, 0.151]
- F2_value_rule_stated: 29/54  weighted 0.71 [0.566, 0.821]

## RQ2
- has_ar_group: 28/57  weighted 0.484 [0.335, 0.636]
- abstract_claims_vs_ar_CT6: 6/57  weighted 0.135 [0.058, 0.281]
- ar_budget_matched_all: 0/28  weighted 0.0 [0, 0.121]
- ar_budget_not_reported_any: 24/28  weighted 0.831 [0.587, 0.944]
- ar_numbers_copied_any: 5/28  weighted 0.187 [0.067, 0.425]
- ar_variance_any: 2/28  weighted 0.06 [0.01, 0.296]
- diffusion_better_majority_of_units: 12/25  weighted 0.337 [0.158, 0.579]
- diffusion_worse_majority_of_units: 10/25  weighted 0.552 [0.32, 0.764]
- units_total: {"worse": 101, "better": 109, "tie": 2}

## RQ3
- has_training_group: 23/57  weighted 0.355 [0.226, 0.508]
- by_factor:
  - ar-initialisation: 1/57  weighted 0.003 [0.0, 0.512]
  - distillation: 2/57  weighted 0.017 [0.001, 0.182]
  - objective: 12/57  weighted 0.162 [0.084, 0.291]
  - pretraining-recipe: 5/57  weighted 0.055 [0.016, 0.173]
  - rl: 6/57  weighted 0.138 [0.06, 0.284]
  - sft: 4/57  weighted 0.043 [0.011, 0.155]
- credited_ablation_any: 6/23  weighted 0.296 [0.119, 0.567]
- held_fixed_stated_all: 6/23  weighted 0.346 [0.152, 0.609]
- variance_any: 3/23  weighted 0.089 [0.015, 0.382]
- anchor_better_majority: 11/17  weighted 0.724 [0.385, 0.916]
- units_total: {"anchor-better": 114, "anchor-worse": 71, "tie": 8}

## RQ4
- has_inference_group: 34/57  weighted 0.732 [0.587, 0.84]
- by_factor:
  - block-or-parallel: 8/57  weighted 0.182 [0.089, 0.335]
  - cache: 4/57  weighted 0.13 [0.052, 0.289]
  - gen-length: 4/57  weighted 0.07 [0.024, 0.184]
  - guidance: 10/57  weighted 0.199 [0.102, 0.35]
  - order-rule: 8/57  weighted 0.203 [0.103, 0.361]
  - remasking: 3/57  weighted 0.041 [0.01, 0.156]
  - steps-or-nfe: 12/57  weighted 0.228 [0.126, 0.376]
  - tokens-per-step: 7/57  weighted 0.158 [0.072, 0.312]
  - value-rule: 5/57  weighted 0.126 [0.052, 0.275]
- budget_reported_any: 23/34  weighted 0.611 [0.424, 0.77]
- variance_any: 9/34  weighted 0.272 [0.141, 0.459]
- dose_shapes_units: {"up": 21, "other": 6, "down": 7, "peaked": 5}
- any_nonmonotone_dose_curve: 5/12  weighted 0.561 [0.271, 0.815]

## RQ5
- n_mm_extracted: 12
- CT5_claim: {"no": 11, "yes": 1}
- synergy_benchmark: {"no": 12}
- synergy_group: {"False": 6, "True": 6}
- claim_and_group: 0
- claim_without_group: ["R0963"]
- group_ids: {"M18816": [["shared-vs-decoupled", "Table 31", [1, 1, 1, 1]], ["shared-vs-decoupled", "Table 31", [1, 1, -1, 1]], ["shared-vs-decoupled", "Figure 34", []], ["shared-vs-decoupled", "Figure 34", []]], "M15992": [["task-or-modality-removal", "Table S7", [1, 1, 1, 1, 1]]], "M09294": [["task-or-modality-removal", "Figure 10", []]], "M19012": [["task-or-modality-removal", "Table 4", []]], "M19293": [["task-or-modality-removal", "Table 6", []], ["task-or-modality-removal", "Table 6", []], ["task-or-modality-removal", "Table 7", [-1, -1, -1, 0, -1, -1]]], "M15792": [["task-or-modality-removal", "Tabl

## RQ6
- QA1: {"low": {"0": {"count": 33, "of": 57, "share": 0.556, "ci95": [0.401, 0.701], "by_stratum": {"G-long": "6/11", "G-mm": "8/12", "G-short": "8/14", "S-seed": "11/20"}}, "1": {"count": 24, "of": 57, "share": 0.444, "ci95": [0.299, 0.599], "by_stratum": {"G-long": "5/11", "G-mm": "4/12", "G-short": "6/14", "S-seed": "9/20"}}, "2": {"count": 0, "of": 57, "share": 0.0, "ci95": [0, 0.063], "by_stratum": {"G-long": "0/11", "G-mm": "0/12", "G-short": "0/14", "S-seed": "0/20"}}}, "high": {"0": {"count": 30, "of": 57, "share": 0.525, "ci95": [0.373, 0.672], "by_stratum": {"G-long": "4/11", "G-mm": "7/12"
- QA2: {"low": {"0": {"count": 13, "of": 57, "share": 0.192, "ci95": [0.102, 0.332], "by_stratum": {"G-long": "2/11", "G-mm": "3/12", "G-short": "5/14", "S-seed": "3/20"}}, "1": {"count": 41, "of": 57, "share": 0.711, "ci95": [0.554, 0.83], "by_stratum": {"G-long": "9/11", "G-mm": "9/12", "G-short": "9/14", "S-seed": "14/20"}}, "2": {"count": 3, "of": 57, "share": 0.097, "ci95": [0.033, 0.253], "by_stratum": {"G-long": "0/11", "G-mm": "0/12", "G-short": "0/14", "S-seed": "3/20"}}}, "high": {"0": {"count": 6, "of": 57, "share": 0.096, "ci95": [0.036, 0.23], "by_stratum": {"G-long": "1/11", "G-mm": "2/
- QA3: {"low": {"0": {"count": 19, "of": 57, "share": 0.213, "ci95": [0.121, 0.347], "by_stratum": {"G-long": "1/11", "G-mm": "8/12", "G-short": "7/14", "S-seed": "3/20"}}, "1": {"count": 28, "of": 57, "share": 0.546, "ci95": [0.392, 0.692], "by_stratum": {"G-long": "7/11", "G-mm": "3/12", "G-short": "7/14", "S-seed": "11/20"}}, "2": {"count": 10, "of": 57, "share": 0.241, "ci95": [0.13, 0.401], "by_stratum": {"G-long": "3/11", "G-mm": "1/12", "G-short": "0/14", "S-seed": "6/20"}}}, "high": {"0": {"count": 11, "of": 57, "share": 0.103, "ci95": [0.048, 0.207], "by_stratum": {"G-long": "0/11", "G-mm": 
- QA4: {"low": {"0": {"count": 39, "of": 53, "share": 0.752, "ci95": [0.601, 0.859], "by_stratum": {"G-long": "4/10", "G-mm": "9/12", "G-short": "10/11", "S-seed": "16/20"}}, "1": {"count": 7, "of": 53, "share": 0.151, "ci95": [0.068, 0.303], "by_stratum": {"G-long": "3/10", "G-mm": "1/12", "G-short": "0/11", "S-seed": "3/20"}}, "2": {"count": 7, "of": 53, "share": 0.097, "ci95": [0.041, 0.212], "by_stratum": {"G-long": "3/10", "G-mm": "2/12", "G-short": "1/11", "S-seed": "1/20"}}}, "high": {"0": {"count": 38, "of": 53, "share": 0.74, "ci95": [0.589, 0.849], "by_stratum": {"G-long": "4/10", "G-mm": "
- QA5: {"low": {"0": {"count": 34, "of": 53, "share": 0.654, "ci95": [0.496, 0.783], "by_stratum": {"G-long": "3/10", "G-mm": "8/12", "G-short": "9/11", "S-seed": "14/20"}}, "1": {"count": 11, "of": 53, "share": 0.221, "ci95": [0.114, 0.384], "by_stratum": {"G-long": "2/10", "G-mm": "3/12", "G-short": "1/11", "S-seed": "5/20"}}, "2": {"count": 8, "of": 53, "share": 0.125, "ci95": [0.063, 0.235], "by_stratum": {"G-long": "5/10", "G-mm": "1/12", "G-short": "1/11", "S-seed": "1/20"}}}, "high": {"0": {"count": 32, "of": 53, "share": 0.617, "ci95": [0.458, 0.754], "by_stratum": {"G-long": "3/10", "G-mm": 
- QA6: {"low": {"0": {"count": 16, "of": 53, "share": 0.166, "ci95": [0.087, 0.293], "by_stratum": {"G-long": "1/10", "G-mm": "8/12", "G-short": "5/11", "S-seed": "2/20"}}, "1": {"count": 18, "of": 53, "share": 0.347, "ci95": [0.212, 0.511], "by_stratum": {"G-long": "4/10", "G-mm": "4/12", "G-short": "3/11", "S-seed": "7/20"}}, "2": {"count": 19, "of": 53, "share": 0.487, "ci95": [0.334, 0.643], "by_stratum": {"G-long": "5/10", "G-mm": "0/12", "G-short": "3/11", "S-seed": "11/20"}}}, "high": {"0": {"count": 15, "of": 53, "share": 0.163, "ci95": [0.085, 0.291], "by_stratum": {"G-long": "1/10", "G-mm":
- QA7: {"low": {"0": {"count": 5, "of": 51, "share": 0.103, "ci95": [0.037, 0.256], "by_stratum": {"G-long": "0/8", "G-mm": "1/12", "G-short": "2/13", "S-seed": "2/18"}}, "1": {"count": 26, "of": 51, "share": 0.361, "ci95": [0.233, 0.512], "by_stratum": {"G-long": "5/8", "G-mm": "9/12", "G-short": "8/13", "S-seed": "4/18"}}, "2": {"count": 20, "of": 51, "share": 0.536, "ci95": [0.381, 0.685], "by_stratum": {"G-long": "3/8", "G-mm": "2/12", "G-short": "3/13", "S-seed": "12/18"}}}, "high": {"0": {"count": 4, "of": 51, "share": 0.09, "ci95": [0.029, 0.246], "by_stratum": {"G-long": "0/8", "G-mm": "1/12"
- QA8: {"low": {"0": {"count": 8, "of": 54, "share": 0.153, "ci95": [0.071, 0.3], "by_stratum": {"G-long": "1/10", "G-mm": "1/11", "G-short": "3/13", "S-seed": "3/20"}}, "1": {"count": 18, "of": 54, "share": 0.349, "ci95": [0.215, 0.511], "by_stratum": {"G-long": "4/10", "G-mm": "3/11", "G-short": "4/13", "S-seed": "7/20"}}, "2": {"count": 28, "of": 54, "share": 0.498, "ci95": [0.344, 0.652], "by_stratum": {"G-long": "5/10", "G-mm": "7/11", "G-short": "6/13", "S-seed": "10/20"}}}, "high": {"0": {"count": 8, "of": 54, "share": 0.153, "ci95": [0.071, 0.3], "by_stratum": {"G-long": "1/10", "G-mm": "1/11
- QA9: {"low": {"0": {"count": 1, "of": 57, "share": 0.032, "ci95": [0.005, 0.18], "by_stratum": {"G-long": "0/11", "G-mm": "0/12", "G-short": "0/14", "S-seed": "1/20"}}, "1": {"count": 14, "of": 57, "share": 0.245, "ci95": [0.14, 0.393], "by_stratum": {"G-long": "3/11", "G-mm": "1/12", "G-short": "6/14", "S-seed": "4/20"}}, "2": {"count": 42, "of": 57, "share": 0.723, "ci95": [0.569, 0.837], "by_stratum": {"G-long": "8/11", "G-mm": "11/12", "G-short": "8/14", "S-seed": "15/20"}}}, "high": {"0": {"count": 1, "of": 57, "share": 0.032, "ci95": [0.005, 0.18], "by_stratum": {"G-long": "0/11", "G-mm": "0/
- claims_status: {"direction": 60, "not-checkable": 39, "partial": 33, "match": 42, "unsupported": 7}

