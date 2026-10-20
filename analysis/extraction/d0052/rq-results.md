# D0052 RQ results (script-generated; do not edit)

extracted 9 of 80; by stratum {'G-long': 4, 'G-mm': 3, 'G-short': 2, 'S-seed': 0}; N_h {'G-mm': 50, 'G-short': 268, 'G-long': 266, 'S-seed': 1073.8488372093022}; missing ['M01553', 'M03150', 'M03633', 'M04407', 'M05881', 'M06241', 'M06272', 'M07124', 'M07646', 'M08783', 'M09246', 'M09294', 'M10526', 'M10840', 'M10855', 'M11180', 'M12084', 'M12476', 'M12879', 'M12960', 'M13371', 'M13397', 'M13760', 'M13884', 'M14000', 'M14267', 'M14280', 'M14293', 'M14326', 'M15033', 'M15781', 'M15792', 'M15840', 'M15992', 'M16080', 'M16154', 'M16269', 'M17249', 'M17285', 'M17725', 'M17834', 'M18059', 'M18141', 'M18735', 'M18994', 'M19012', 'M19013', 'M19021', 'M19099', 'M19293', 'R0021', 'R0121', 'R0171', 'R0188', 'R0193', 'R0214', 'R0291', 'R0588', 'R0621', 'R0631', 'R0674', 'R0677', 'R0717', 'R0738', 'R0865', 'R0958', 'R0963', 'R1004', 'R1087', 'R1124', 'R1319']

## RQ1
- study_type:
  - method: 8/9  weighted 0.886 [0.264, 0.994]
  - theory: 0/9  weighted 0.0 [0, 0.299]
  - analysis: 1/9  weighted 0.114 [0.006, 0.736]
  - benchmark: 0/9  weighted 0.0 [0, 0.299]
  - system: 0/9  weighted 0.0 [0, 0.299]
- state_space:
  - discrete-absorbing: 3/9  weighted 0.573 [0.206, 0.874]
  - discrete-uniform: 2/9  weighted 0.228 [0.032, 0.725]
  - discrete-flow: 0/9  weighted 0.0 [0, 0.299]
  - continuous-embedding: 1/9  weighted 0.114 [0.006, 0.736]
  - continuous-latent: 1/9  weighted 0.029 [0.0, 0.875]
  - hybrid: 1/9  weighted 0.029 [0.0, 0.875]
  - not_stated: 1/9  weighted 0.029 [0.0, 0.875]
- objective:
  - elbo-ce: 0/9  weighted 0.0 [0, 0.299]
  - weighted-ce: 0/9  weighted 0.0 [0, 0.299]
  - score-entropy: 0/9  weighted 0.0 [0, 0.299]
  - mse-x0: 0/9  weighted 0.0 [0, 0.299]
  - mse-eps-or-velocity: 0/9  weighted 0.0 [0, 0.299]
  - flow-matching: 1/9  weighted 0.029 [0.0, 0.875]
  - other: 5/9  weighted 0.399 [0.111, 0.78]
  - not_stated: 2/9  weighted 0.343 [0.071, 0.781]
  - NA: 1/9  weighted 0.229 [0.031, 0.734]
- position_rule:
  - left-to-right: 1/9  weighted 0.029 [0.0, 0.875]
  - random: 1/9  weighted 0.029 [0.0, 0.875]
  - confidence-ranked: 1/9  weighted 0.229 [0.031, 0.734]
  - threshold-adaptive: 0/9  weighted 0.0 [0, 0.299]
  - fixed-order: 0/9  weighted 0.0 [0, 0.299]
  - learned-planner: 0/9  weighted 0.0 [0, 0.299]
  - all-positions: 4/9  weighted 0.37 [0.096, 0.765]
  - other: 1/9  weighted 0.229 [0.031, 0.734]
  - not_stated: 1/9  weighted 0.114 [0.006, 0.736]
- blockwise:
  - yes: 4/9  weighted 0.601 [0.22, 0.889]
  - no: 5/9  weighted 0.399 [0.111, 0.78]
  - not_stated: 0/9  weighted 0.0 [0, 0.299]
- revision:
  - none: 2/9  weighted 0.057 [0.001, 0.797]
  - explicit-remasking-or-editing: 1/9  weighted 0.114 [0.006, 0.736]
  - corrector: 1/9  weighted 0.114 [0.006, 0.736]
  - implicit-channel: 4/9  weighted 0.37 [0.096, 0.765]
  - output-level: 0/9  weighted 0.0 [0, 0.299]
  - other: 0/9  weighted 0.0 [0, 0.299]
  - not_stated: 3/9  weighted 0.573 [0.206, 0.874]
- memory:
  - none: 4/9  weighted 0.285 [0.053, 0.74]
  - self-conditioning: 1/9  weighted 0.114 [0.006, 0.736]
  - exact-cache: 0/9  weighted 0.0 [0, 0.299]
  - approximate-cache: 0/9  weighted 0.0 [0, 0.299]
  - planner-state: 0/9  weighted 0.0 [0, 0.299]
  - other: 1/9  weighted 0.229 [0.031, 0.734]
  - not_stated: 3/9  weighted 0.372 [0.084, 0.793]
- training_free:
  - yes: 1/9  weighted 0.229 [0.031, 0.734]
  - no: 8/9  weighted 0.771 [0.266, 0.969]
  - not_stated: 0/9  weighted 0.0 [0, 0.299]
- training_stages:
  - pretraining: 1/9  weighted 0.114 [0.006, 0.736]
  - continued-pretraining: 0/9  weighted 0.0 [0, 0.299]
  - adaptation-from-ar: 1/9  weighted 0.114 [0.006, 0.736]
  - sft: 3/9  weighted 0.086 [0.003, 0.747]
  - rl: 1/9  weighted 0.114 [0.006, 0.736]
  - distillation: 2/9  weighted 0.142 [0.011, 0.72]
  - other: 4/9  weighted 0.486 [0.133, 0.853]
- credited_type:
  - model-or-architecture: 4/9  weighted 0.285 [0.053, 0.74]
  - objective-or-loss: 0/9  weighted 0.0 [0, 0.299]
  - training-recipe: 2/9  weighted 0.142 [0.011, 0.72]
  - sampler-or-decoding: 1/9  weighted 0.229 [0.031, 0.734]
  - caching-or-system: 0/9  weighted 0.0 [0, 0.299]
  - guidance-or-constraint: 0/9  weighted 0.0 [0, 0.299]
  - other: 1/9  weighted 0.229 [0.031, 0.734]
- F2_value_rule_stated: 4/9  weighted 0.571 [0.181, 0.889]

## RQ2
- has_ar_group: 6/9  weighted 0.744 [0.269, 0.958]
- abstract_claims_vs_ar_CT6: 1/9  weighted 0.114 [0.006, 0.736]
- ar_budget_matched_all: 0/6  weighted 0.0 [0, 0.39]
- ar_budget_not_reported_any: 5/6  weighted 0.962 [0.09, 1.0]
- ar_numbers_copied_any: 1/6  weighted 0.038 [0.0, 0.91]
- ar_variance_any: 1/6  weighted 0.153 [0.008, 0.811]
- diffusion_better_majority_of_units: 4/6  weighted 0.809 [0.197, 0.986]
- diffusion_worse_majority_of_units: 0/6  weighted 0.0 [0, 0.39]
- units_total: {"worse": 7, "better": 16, "tie": 2}

## RQ3
- has_training_group: 6/9  weighted 0.513 [0.183, 0.832]
- by_factor:
  - ar-initialisation: 0/9  weighted 0.0 [0, 0.299]
  - distillation: 2/9  weighted 0.142 [0.011, 0.72]
  - objective: 3/9  weighted 0.256 [0.042, 0.731]
  - pretraining-recipe: 1/9  weighted 0.114 [0.006, 0.736]
  - rl: 1/9  weighted 0.114 [0.006, 0.736]
  - sft: 1/9  weighted 0.029 [0.0, 0.875]
- credited_ablation_any: 2/6  weighted 0.278 [0.054, 0.723]
- held_fixed_stated_all: 0/6  weighted 0.0 [0, 0.39]
- variance_any: 2/6  weighted 0.444 [0.117, 0.829]
- anchor_better_majority: 4/5  weighted 0.928 [0.206, 0.998]
- units_total: {"anchor-better": 33, "anchor-worse": 16}

## RQ4
- has_inference_group: 5/9  weighted 0.715 [0.26, 0.947]
- by_factor:
  - block-or-parallel: 1/9  weighted 0.229 [0.031, 0.734]
  - cache: 0/9  weighted 0.0 [0, 0.299]
  - gen-length: 1/9  weighted 0.114 [0.006, 0.736]
  - guidance: 2/9  weighted 0.343 [0.071, 0.781]
  - order-rule: 0/9  weighted 0.0 [0, 0.299]
  - remasking: 0/9  weighted 0.0 [0, 0.299]
  - steps-or-nfe: 2/9  weighted 0.142 [0.011, 0.72]
  - tokens-per-step: 1/9  weighted 0.029 [0.0, 0.875]
  - value-rule: 0/9  weighted 0.0 [0, 0.299]
- budget_reported_any: 4/5  weighted 0.679 [0.153, 0.961]
- variance_any: 1/5  weighted 0.321 [0.039, 0.847]
- dose_shapes_units: {"up": 1}
- any_nonmonotone_dose_curve: 0/1  weighted 0.0

## RQ5
- n_mm_extracted: 3
- CT5_claim: {"no": 3}
- synergy_benchmark: {"no": 3}
- synergy_group: {"False": 2, "True": 1}
- claim_and_group: 0
- claim_without_group: []
- group_ids: {"M18816": [["shared-vs-decoupled", "Table 31", [1, 1, 1, 1]], ["shared-vs-decoupled", "Table 31", [1, 1, -1, 1]], ["shared-vs-decoupled", "Figure 34", []], ["shared-vs-decoupled", "Figure 34", []]]}

## RQ6
- QA1: {"low": {"0": {"count": 7, "of": 9, "share": 0.858, "ci95": [0.28, 0.989], "by_stratum": {"G-long": "3/4", "G-mm": "2/3", "G-short": "2/2"}}, "1": {"count": 2, "of": 9, "share": 0.142, "ci95": [0.011, 0.72], "by_stratum": {"G-long": "1/4", "G-mm": "1/3", "G-short": "0/2"}}, "2": {"count": 0, "of": 9, "share": 0.0, "ci95": [0, 0.299], "by_stratum": {"G-long": "0/4", "G-mm": "0/3", "G-short": "0/2"}}}, "high": {"0": {"count": 6, "of": 9, "share": 0.744, "ci95": [0.269, 0.958], "by_stratum": {"G-long": "2/4", "G-mm": "2/3", "G-short": "2/2"}}, "1": {"count": 3, "of": 9, "share": 0.256, "ci95": [0
- QA2: {"low": {"0": {"count": 4, "of": 9, "share": 0.486, "ci95": [0.133, 0.853], "by_stratum": {"G-long": "2/4", "G-mm": "1/3", "G-short": "1/2"}}, "1": {"count": 5, "of": 9, "share": 0.514, "ci95": [0.147, 0.867], "by_stratum": {"G-long": "2/4", "G-mm": "2/3", "G-short": "1/2"}}, "2": {"count": 0, "of": 9, "share": 0.0, "ci95": [0, 0.299], "by_stratum": {"G-long": "0/4", "G-mm": "0/3", "G-short": "0/2"}}}, "high": {"0": {"count": 1, "of": 9, "share": 0.114, "ci95": [0.006, 0.736], "by_stratum": {"G-long": "1/4", "G-mm": "0/3", "G-short": "0/2"}}, "1": {"count": 6, "of": 9, "share": 0.628, "ci95": 
- QA3: {"low": {"0": {"count": 4, "of": 9, "share": 0.315, "ci95": [0.063, 0.758], "by_stratum": {"G-long": "0/4", "G-mm": "3/3", "G-short": "1/2"}}, "1": {"count": 4, "of": 9, "share": 0.571, "ci95": [0.181, 0.889], "by_stratum": {"G-long": "3/4", "G-mm": "0/3", "G-short": "1/2"}}, "2": {"count": 1, "of": 9, "share": 0.114, "ci95": [0.006, 0.736], "by_stratum": {"G-long": "1/4", "G-mm": "0/3", "G-short": "0/2"}}}, "high": {"0": {"count": 1, "of": 9, "share": 0.029, "ci95": [0.0, 0.875], "by_stratum": {"G-long": "0/4", "G-mm": "1/3", "G-short": "0/2"}}, "1": {"count": 7, "of": 9, "share": 0.858, "ci9
- QA4: {"low": {"0": {"count": 6, "of": 9, "share": 0.543, "ci95": [0.161, 0.88], "by_stratum": {"G-long": "2/4", "G-mm": "3/3", "G-short": "1/2"}}, "1": {"count": 1, "of": 9, "share": 0.114, "ci95": [0.006, 0.736], "by_stratum": {"G-long": "1/4", "G-mm": "0/3", "G-short": "0/2"}}, "2": {"count": 2, "of": 9, "share": 0.343, "ci95": [0.071, 0.781], "by_stratum": {"G-long": "1/4", "G-mm": "0/3", "G-short": "1/2"}}}, "high": {"0": {"count": 6, "of": 9, "share": 0.543, "ci95": [0.161, 0.88], "by_stratum": {"G-long": "2/4", "G-mm": "3/3", "G-short": "1/2"}}, "1": {"count": 1, "of": 9, "share": 0.114, "ci9
- QA5: {"low": {"0": {"count": 4, "of": 9, "share": 0.4, "ci95": [0.097, 0.806], "by_stratum": {"G-long": "1/4", "G-mm": "2/3", "G-short": "1/2"}}, "1": {"count": 2, "of": 9, "share": 0.142, "ci95": [0.011, 0.72], "by_stratum": {"G-long": "1/4", "G-mm": "1/3", "G-short": "0/2"}}, "2": {"count": 3, "of": 9, "share": 0.457, "ci95": [0.12, 0.839], "by_stratum": {"G-long": "2/4", "G-mm": "0/3", "G-short": "1/2"}}}, "high": {"0": {"count": 4, "of": 9, "share": 0.4, "ci95": [0.097, 0.806], "by_stratum": {"G-long": "1/4", "G-mm": "2/3", "G-short": "1/2"}}, "1": {"count": 2, "of": 9, "share": 0.142, "ci95": 
- QA6: {"low": {"0": {"count": 4, "of": 9, "share": 0.4, "ci95": [0.097, 0.806], "by_stratum": {"G-long": "1/4", "G-mm": "2/3", "G-short": "1/2"}}, "1": {"count": 3, "of": 9, "share": 0.256, "ci95": [0.042, 0.731], "by_stratum": {"G-long": "2/4", "G-mm": "1/3", "G-short": "0/2"}}, "2": {"count": 2, "of": 9, "share": 0.343, "ci95": [0.071, 0.781], "by_stratum": {"G-long": "1/4", "G-mm": "0/3", "G-short": "1/2"}}}, "high": {"0": {"count": 4, "of": 9, "share": 0.4, "ci95": [0.097, 0.806], "by_stratum": {"G-long": "1/4", "G-mm": "2/3", "G-short": "1/2"}}, "1": {"count": 3, "of": 9, "share": 0.256, "ci95"
- QA7: {"low": {"0": {"count": 0, "of": 8, "share": 0.0, "ci95": [0, 0.324], "by_stratum": {"G-long": "0/3", "G-mm": "0/3", "G-short": "0/2"}}, "1": {"count": 7, "of": 8, "share": 0.871, "ci95": [0.232, 0.993], "by_stratum": {"G-long": "2/3", "G-mm": "3/3", "G-short": "2/2"}}, "2": {"count": 1, "of": 8, "share": 0.129, "ci95": [0.007, 0.768], "by_stratum": {"G-long": "1/3", "G-mm": "0/3", "G-short": "0/2"}}}, "high": {"0": {"count": 0, "of": 8, "share": 0.0, "ci95": [0, 0.324], "by_stratum": {"G-long": "0/3", "G-mm": "0/3", "G-short": "0/2"}}, "1": {"count": 5, "of": 8, "share": 0.711, "ci95": [0.235
- QA8: {"low": {"0": {"count": 0, "of": 9, "share": 0.0, "ci95": [0, 0.299], "by_stratum": {"G-long": "0/4", "G-mm": "0/3", "G-short": "0/2"}}, "1": {"count": 6, "of": 9, "share": 0.628, "ci95": [0.207, 0.916], "by_stratum": {"G-long": "3/4", "G-mm": "2/3", "G-short": "1/2"}}, "2": {"count": 3, "of": 9, "share": 0.372, "ci95": [0.084, 0.793], "by_stratum": {"G-long": "1/4", "G-mm": "1/3", "G-short": "1/2"}}}, "high": {"0": {"count": 0, "of": 9, "share": 0.0, "ci95": [0, 0.299], "by_stratum": {"G-long": "0/4", "G-mm": "0/3", "G-short": "0/2"}}, "1": {"count": 6, "of": 9, "share": 0.628, "ci95": [0.207
- QA9: {"low": {"0": {"count": 0, "of": 9, "share": 0.0, "ci95": [0, 0.299], "by_stratum": {"G-long": "0/4", "G-mm": "0/3", "G-short": "0/2"}}, "1": {"count": 3, "of": 9, "share": 0.457, "ci95": [0.12, 0.839], "by_stratum": {"G-long": "2/4", "G-mm": "0/3", "G-short": "1/2"}}, "2": {"count": 6, "of": 9, "share": 0.543, "ci95": [0.161, 0.88], "by_stratum": {"G-long": "2/4", "G-mm": "3/3", "G-short": "1/2"}}}, "high": {"0": {"count": 0, "of": 9, "share": 0.0, "ci95": [0, 0.299], "by_stratum": {"G-long": "0/4", "G-mm": "0/3", "G-short": "0/2"}}, "1": {"count": 3, "of": 9, "share": 0.457, "ci95": [0.12, 0
- claims_status: {"direction": 13, "not-checkable": 9, "partial": 5, "match": 8, "unsupported": 4}

