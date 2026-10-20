# D0052 RQ results (script-generated; do not edit)

extracted 0 of 81; by stratum {'G-long': 0, 'G-mm': 0, 'G-short': 0}; N_h {'G-mm': 50, 'G-short': 268, 'G-long': 266}; missing ['M01553', 'M03150', 'M03633', 'M04407', 'M05881', 'M06241', 'M06272', 'M06731', 'M06840', 'M07124', 'M07646', 'M07813', 'M07842', 'M07875', 'M08783', 'M09246', 'M09294', 'M10526', 'M10710', 'M10840', 'M10855', 'M10988', 'M11180', 'M12084', 'M12210', 'M12476', 'M12879', 'M12904', 'M12960', 'M13081', 'M13196', 'M13198', 'M13234', 'M13371', 'M13397', 'M13760', 'M13884', 'M14000', 'M14267', 'M14280', 'M14293', 'M14326', 'M14365', 'M14664', 'M15033', 'M15135', 'M15184', 'M15457', 'M15672', 'M15781', 'M15792', 'M15840', 'M15992', 'M16043', 'M16080', 'M16154', 'M16269', 'M16729', 'M17249', 'M17283', 'M17285', 'M17323', 'M17469', 'M17718', 'M17725', 'M17834', 'M17985', 'M18059', 'M18141', 'M18735', 'M18816', 'M18850', 'M18990', 'M18994', 'M19012', 'M19013', 'M19021', 'M19099', 'M19293', 'R0963', 'U04280']

## RQ1
- study_type:
  - method: 0/0  weighted None
  - theory: 0/0  weighted None
  - analysis: 0/0  weighted None
  - benchmark: 0/0  weighted None
  - system: 0/0  weighted None
- state_space:
  - discrete-absorbing: 0/0  weighted None
  - discrete-uniform: 0/0  weighted None
  - discrete-flow: 0/0  weighted None
  - continuous-embedding: 0/0  weighted None
  - continuous-latent: 0/0  weighted None
  - hybrid: 0/0  weighted None
  - not_stated: 0/0  weighted None
- objective:
  - elbo-ce: 0/0  weighted None
  - weighted-ce: 0/0  weighted None
  - score-entropy: 0/0  weighted None
  - mse-x0: 0/0  weighted None
  - mse-eps-or-velocity: 0/0  weighted None
  - flow-matching: 0/0  weighted None
  - other: 0/0  weighted None
  - not_stated: 0/0  weighted None
  - NA: 0/0  weighted None
- position_rule:
  - left-to-right: 0/0  weighted None
  - random: 0/0  weighted None
  - confidence-ranked: 0/0  weighted None
  - threshold-adaptive: 0/0  weighted None
  - fixed-order: 0/0  weighted None
  - learned-planner: 0/0  weighted None
  - all-positions: 0/0  weighted None
  - other: 0/0  weighted None
  - not_stated: 0/0  weighted None
- blockwise:
  - yes: 0/0  weighted None
  - no: 0/0  weighted None
  - not_stated: 0/0  weighted None
- revision:
  - none: 0/0  weighted None
  - explicit-remasking-or-editing: 0/0  weighted None
  - corrector: 0/0  weighted None
  - implicit-channel: 0/0  weighted None
  - output-level: 0/0  weighted None
  - other: 0/0  weighted None
  - not_stated: 0/0  weighted None
- memory:
  - none: 0/0  weighted None
  - self-conditioning: 0/0  weighted None
  - exact-cache: 0/0  weighted None
  - approximate-cache: 0/0  weighted None
  - planner-state: 0/0  weighted None
  - other: 0/0  weighted None
  - not_stated: 0/0  weighted None
- training_free:
  - yes: 0/0  weighted None
  - no: 0/0  weighted None
  - not_stated: 0/0  weighted None
- training_stages:
  - pretraining: 0/0  weighted None
  - continued-pretraining: 0/0  weighted None
  - adaptation-from-ar: 0/0  weighted None
  - sft: 0/0  weighted None
  - rl: 0/0  weighted None
  - distillation: 0/0  weighted None
  - other: 0/0  weighted None
- credited_type:
  - model-or-architecture: 0/0  weighted None
  - objective-or-loss: 0/0  weighted None
  - training-recipe: 0/0  weighted None
  - sampler-or-decoding: 0/0  weighted None
  - caching-or-system: 0/0  weighted None
  - guidance-or-constraint: 0/0  weighted None
  - other: 0/0  weighted None
- F2_value_rule_stated: 0/0  weighted None

## RQ2
- has_ar_group: 0/0  weighted None
- abstract_claims_vs_ar_CT6: 0/0  weighted None
- ar_budget_matched_all: 0/0  weighted None
- ar_budget_not_reported_any: 0/0  weighted None
- ar_numbers_copied_any: 0/0  weighted None
- ar_variance_any: 0/0  weighted None
- diffusion_better_majority_of_units: 0/0  weighted None
- diffusion_worse_majority_of_units: 0/0  weighted None
- units_total: {}

## RQ3
- has_training_group: 0/0  weighted None
- by_factor:
  - ar-initialisation: 0/0  weighted None
  - distillation: 0/0  weighted None
  - objective: 0/0  weighted None
  - pretraining-recipe: 0/0  weighted None
  - rl: 0/0  weighted None
  - sft: 0/0  weighted None
- credited_ablation_any: 0/0  weighted None
- held_fixed_stated_all: 0/0  weighted None
- variance_any: 0/0  weighted None
- anchor_better_majority: 0/0  weighted None
- units_total: {}

## RQ4
- has_inference_group: 0/0  weighted None
- by_factor:
  - block-or-parallel: 0/0  weighted None
  - cache: 0/0  weighted None
  - gen-length: 0/0  weighted None
  - guidance: 0/0  weighted None
  - order-rule: 0/0  weighted None
  - remasking: 0/0  weighted None
  - steps-or-nfe: 0/0  weighted None
  - tokens-per-step: 0/0  weighted None
  - value-rule: 0/0  weighted None
- budget_reported_any: 0/0  weighted None
- variance_any: 0/0  weighted None
- dose_shapes_units: {}
- any_nonmonotone_dose_curve: 0/0  weighted None

## RQ5
- n_mm_extracted: 0
- CT5_claim: {}
- synergy_benchmark: {}
- synergy_group: {}
- claim_and_group: 0
- claim_without_group: []
- group_ids: {}

## RQ6
- QA1: {"low": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "high": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "NA": 0}
- QA2: {"low": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "high": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "NA": 0}
- QA3: {"low": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "high": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "NA": 0}
- QA4: {"low": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "high": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "NA": 0}
- QA5: {"low": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "high": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "NA": 0}
- QA6: {"low": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "high": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "NA": 0}
- QA7: {"low": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "high": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "NA": 0}
- QA8: {"low": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "high": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "NA": 0}
- QA9: {"low": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "high": {"0": {"count": 0, "of": 0, "share": null, "ci95": null}, "1": {"count": 0, "of": 0, "share": null, "ci95": null}, "2": {"count": 0, "of": 0, "share": null, "ci95": null}}, "NA": 0}
- claims_status: {}

