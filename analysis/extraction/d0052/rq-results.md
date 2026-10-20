# D0052 RQ results (script-generated; do not edit)

extracted 1 of 81; by stratum {'G-long': 0, 'G-mm': 1, 'G-short': 0}; N_h {'G-mm': 50, 'G-short': 268, 'G-long': 266}; missing ['M01553', 'M03150', 'M03633', 'M04407', 'M05881', 'M06241', 'M06272', 'M06731', 'M06840', 'M07124', 'M07646', 'M07813', 'M07842', 'M07875', 'M08783', 'M09246', 'M09294', 'M10526', 'M10710', 'M10840', 'M10855', 'M10988', 'M11180', 'M12084', 'M12210', 'M12476', 'M12879', 'M12904', 'M12960', 'M13081', 'M13196', 'M13198', 'M13234', 'M13371', 'M13397', 'M13760', 'M13884', 'M14000', 'M14267', 'M14280', 'M14293', 'M14326', 'M14365', 'M14664', 'M15033', 'M15135', 'M15184', 'M15457', 'M15672', 'M15781', 'M15792', 'M15840', 'M15992', 'M16043', 'M16080', 'M16154', 'M16269', 'M16729', 'M17249', 'M17283', 'M17285', 'M17323', 'M17469', 'M17718', 'M17725', 'M17834', 'M17985', 'M18059', 'M18141', 'M18735', 'M18850', 'M18990', 'M18994', 'M19012', 'M19013', 'M19021', 'M19099', 'M19293', 'R0963', 'U04280']

## RQ1
- study_type:
  - method: 1/1  weighted 1.0
  - theory: 0/1  weighted 0.0
  - analysis: 0/1  weighted 0.0
  - benchmark: 0/1  weighted 0.0
  - system: 0/1  weighted 0.0
- state_space:
  - discrete-absorbing: 0/1  weighted 0.0
  - discrete-uniform: 0/1  weighted 0.0
  - discrete-flow: 0/1  weighted 0.0
  - continuous-embedding: 0/1  weighted 0.0
  - continuous-latent: 0/1  weighted 0.0
  - hybrid: 0/1  weighted 0.0
  - not_stated: 1/1  weighted 1.0
- objective:
  - elbo-ce: 0/1  weighted 0.0
  - weighted-ce: 0/1  weighted 0.0
  - score-entropy: 0/1  weighted 0.0
  - mse-x0: 0/1  weighted 0.0
  - mse-eps-or-velocity: 0/1  weighted 0.0
  - flow-matching: 0/1  weighted 0.0
  - other: 1/1  weighted 1.0
  - not_stated: 0/1  weighted 0.0
  - NA: 0/1  weighted 0.0
- position_rule:
  - left-to-right: 1/1  weighted 1.0
  - random: 0/1  weighted 0.0
  - confidence-ranked: 0/1  weighted 0.0
  - threshold-adaptive: 0/1  weighted 0.0
  - fixed-order: 0/1  weighted 0.0
  - learned-planner: 0/1  weighted 0.0
  - all-positions: 0/1  weighted 0.0
  - other: 0/1  weighted 0.0
  - not_stated: 0/1  weighted 0.0
- blockwise:
  - yes: 0/1  weighted 0.0
  - no: 1/1  weighted 1.0
  - not_stated: 0/1  weighted 0.0
- revision:
  - none: 1/1  weighted 1.0
  - explicit-remasking-or-editing: 0/1  weighted 0.0
  - corrector: 0/1  weighted 0.0
  - implicit-channel: 0/1  weighted 0.0
  - output-level: 0/1  weighted 0.0
  - other: 0/1  weighted 0.0
  - not_stated: 0/1  weighted 0.0
- memory:
  - none: 0/1  weighted 0.0
  - self-conditioning: 0/1  weighted 0.0
  - exact-cache: 0/1  weighted 0.0
  - approximate-cache: 0/1  weighted 0.0
  - planner-state: 0/1  weighted 0.0
  - other: 0/1  weighted 0.0
  - not_stated: 1/1  weighted 1.0
- training_free:
  - yes: 0/1  weighted 0.0
  - no: 1/1  weighted 1.0
  - not_stated: 0/1  weighted 0.0
- training_stages:
  - pretraining: 0/1  weighted 0.0
  - continued-pretraining: 0/1  weighted 0.0
  - adaptation-from-ar: 0/1  weighted 0.0
  - sft: 1/1  weighted 1.0
  - rl: 0/1  weighted 0.0
  - distillation: 0/1  weighted 0.0
  - other: 0/1  weighted 0.0
- credited_type:
  - model-or-architecture: 1/1  weighted 1.0
  - objective-or-loss: 0/1  weighted 0.0
  - training-recipe: 0/1  weighted 0.0
  - sampler-or-decoding: 0/1  weighted 0.0
  - caching-or-system: 0/1  weighted 0.0
  - guidance-or-constraint: 0/1  weighted 0.0
  - other: 0/1  weighted 0.0
- F2_value_rule_stated: 0/1  weighted 0.0

## RQ2
- has_ar_group: 1/1  weighted 1.0
- abstract_claims_vs_ar_CT6: 0/1  weighted 0.0
- ar_budget_matched_all: 0/1  weighted 0.0
- ar_budget_not_reported_any: 0/1  weighted 0.0
- ar_numbers_copied_any: 1/1  weighted 1.0
- ar_variance_any: 0/1  weighted 0.0
- diffusion_better_majority_of_units: 0/1  weighted 0.0
- diffusion_worse_majority_of_units: 0/1  weighted 0.0
- units_total: {"worse": 1, "better": 2, "tie": 1}

## RQ3
- has_training_group: 0/1  weighted 0.0
- by_factor:
  - ar-initialisation: 0/1  weighted 0.0
  - distillation: 0/1  weighted 0.0
  - objective: 0/1  weighted 0.0
  - pretraining-recipe: 0/1  weighted 0.0
  - rl: 0/1  weighted 0.0
  - sft: 0/1  weighted 0.0
- credited_ablation_any: 0/0  weighted None
- held_fixed_stated_all: 0/0  weighted None
- variance_any: 0/0  weighted None
- anchor_better_majority: 0/0  weighted None
- units_total: {}

## RQ4
- has_inference_group: 0/1  weighted 0.0
- by_factor:
  - block-or-parallel: 0/1  weighted 0.0
  - cache: 0/1  weighted 0.0
  - gen-length: 0/1  weighted 0.0
  - guidance: 0/1  weighted 0.0
  - order-rule: 0/1  weighted 0.0
  - remasking: 0/1  weighted 0.0
  - steps-or-nfe: 0/1  weighted 0.0
  - tokens-per-step: 0/1  weighted 0.0
  - value-rule: 0/1  weighted 0.0
- budget_reported_any: 0/0  weighted None
- variance_any: 0/0  weighted None
- dose_shapes_units: {}
- any_nonmonotone_dose_curve: 0/0  weighted None

## RQ5
- n_mm_extracted: 1
- CT5_claim: {"no": 1}
- synergy_benchmark: {"no": 1}
- synergy_group: {"True": 1}
- claim_and_group: 0
- claim_without_group: []
- group_ids: {"M18816": [["shared-vs-decoupled", "Table 31", [1, 1, 1, 1]], ["shared-vs-decoupled", "Table 31", [1, 1, -1, 1]], ["shared-vs-decoupled", "Figure 34", []], ["shared-vs-decoupled", "Figure 34", []]]}

## RQ6
- QA1: {"low": {"0": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "high": {"0": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "NA": 0}
- QA2: {"low": {"0": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "1": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "high": {"0": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "1": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "NA": 0}
- QA3: {"low": {"0": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "high": {"0": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "NA": 0}
- QA4: {"low": {"0": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "high": {"0": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "NA": 0}
- QA5: {"low": {"0": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "1": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "high": {"0": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "1": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "NA": 0}
- QA6: {"low": {"0": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "high": {"0": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "NA": 0}
- QA7: {"low": {"0": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "1": {"count": 1, "of": 1, "share": 1.0, "ci95": null}, "2": {"count": 0, "of": 1, "share": 0.0, "ci95": null}}, "high": {"0": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 1, "of": 1, "share": 1.0, "ci95": null}}, "NA": 0}
- QA8: {"low": {"0": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 1, "of": 1, "share": 1.0, "ci95": null}}, "high": {"0": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 1, "of": 1, "share": 1.0, "ci95": null}}, "NA": 0}
- QA9: {"low": {"0": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 1, "of": 1, "share": 1.0, "ci95": null}}, "high": {"0": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "1": {"count": 0, "of": 1, "share": 0.0, "ci95": null}, "2": {"count": 1, "of": 1, "share": 1.0, "ci95": null}}, "NA": 0}
- claims_status: {"direction": 2, "not-checkable": 3}

