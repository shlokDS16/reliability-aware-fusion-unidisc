import json, sys
from jsonschema import Draft202012Validator
S = json.load(open(sys.argv[1], encoding="utf-8"))
Draft202012Validator.check_schema(S)
v = Draft202012Validator(S)
setting = {k: "not_stated" for k in ["steps_printed", "nfe_printed", "tokens_per_step_printed", "gen_length_printed", "sampler_printed", "value_rule_printed", "guidance_printed"]}
var = {"kind": "none", "value_printed": "", "n_runs": None}
loc = {"page": 7, "where": "Table 1", "row": "OA-ARDM (ours)", "column": "NLL"}
qa = lambda: {"sub": {"a": "no", "b": "no"}, "score": None, "loc": ""}
rec = {"id": "X1", "form_version": "0.1", "extractor": "EA-claude-opus-5-5", "ft": "pymupdf", "meta": None,
 "study": {"study_type": "method", "modality": "text", "text_generator": "diffusion", "state_space": ["discrete-absorbing"],
   "task_families": ["language modelling"], "task_other": "", "primary_task_family": "language modelling",
   "models": [{"name": "OA-ARDM", "params_printed": "not_stated", "params_b": None}], "base_checkpoints": [],
   "training": {"training_free": "no", "stages": ["pretraining"], "data_named": "text8", "tokens_printed": "not_stated", "compute_printed": "not_stated"},
   "main_sampler": {"description": "x", "steps_printed": "250", "nfe_printed": "not_stated", "gen_length_printed": "not_stated", "tokens_per_step_printed": "not_stated"},
   "affiliations": ["Google"], "venue_line_text": "Published as a conference paper at ICLR 2022", "credited_component": "x", "main_comparison": "U02"},
 "design": {"c1_channel": [{"modality": "text", "channel": "erasure"}], "c2_reveal": "any-order", "c2_multimodal": "NA", "c3_predictor": "clean-marginals",
   "c3_self_conditioning": "no", "c3_head_layout": "single-modality", "c4_position": {"rule": "random", "blockwise": "no"}, "c4_joint_draw": "independent",
   "c4_multimodal_schedule": "NA", "c5_revision": ["none"], "memory": ["none"], "levers": ["L1", "L6"], "other_detail": "", "design_fit": None},
 "census": {"F1_status": "number", "F1_unit": "U01", "F2_codes": "G+NS", "F2_detail": "", "F3": "no", "F4": "yes", "F5": "not stated", "F6": "NA"},
 "claims": {"CT": {f"CT{i}": "no" for i in range(1, 7)}, "list": [{"claim_id": "CL1", "source": "abstract", "types": ["CT4"], "has_number": True, "status": "match", "units": ["U01"]}]},
 "qa": {f"QA{i}": qa() for i in range(1, 10)},
 "units": [
  {"unit_id": "U01", "unit_type": "H", "is_F1": True, "source_kind": "main-table", "model": "OA-ARDM (ours)", "own_method": True, "metric": "NLL", "metric_kind": "likelihood",
   "higher_is_better": False, "dataset": "text8", "split": "test", "task_family": "language modelling", "value_printed": "1.43", "value_num": 1.43, "value_unit": "bpc",
   "setting": setting, "params_printed": "not_stated", "variance": {"kind": "plusminus-undefined", "value_printed": "±0.001", "n_runs": None}, "loc": loc},
  {"unit_id": "U02", "unit_type": "K", "rq_class": "RQ4-steps", "credited_ablation": False, "factor": "steps", "levels": ["250", "20"], "values_printed": ["1.43", "1.51"], "values_num": [1.43, 1.51],
   "metric": "NLL", "metric_kind": "likelihood", "higher_is_better": False, "dataset": "text8", "split": "test", "task_family": "language modelling", "model": "OA-ARDM",
   "held_fixed": "not stated", "other_changes": "parallelized variant", "budget_across_arms": "reported", "arm_params_printed": [], "ar_baseline_source": "NA",
   "setting": setting, "variance": var, "loc": loc, "matched": None}],
 "evidence": [{"cond": "U01", "quote": "D3PM-absorbing 256 1.47 OA-ARDM (ours) 250 1.43 ±0.001", "loc": "p.7, Table 1"}, {"cond": "QA3d", "quote": "x", "loc": "p.1"}],
 "searched": {"F2": "§4, App. B"}, "notes": ""}
errs = list(v.iter_errors(rec))
print("errors:", len(errs))
for e in errs[:10]:
    print(list(e.path), e.message[:200])
bad = json.loads(json.dumps(rec))
bad["census"]["F2_codes"] = "NS+G"
bad["evidence"][0]["cond"] = "Z9"
bad["units"][0]["unit_type"] = "Q"
print("bad errors:", len(list(v.iter_errors(bad))))
