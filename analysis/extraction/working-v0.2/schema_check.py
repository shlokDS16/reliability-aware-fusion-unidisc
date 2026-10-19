import json, copy, sys
import jsonschema
P = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706/research/review/extraction/extraction-schema-v0.2.json"
schema = json.load(open(P, encoding="utf-8"))
jsonschema.Draft202012Validator.check_schema(schema)
V = jsonschema.Draft202012Validator(schema)
setting = {k: "not_stated" for k in ["steps_printed", "nfe_printed", "tokens_per_step_printed", "gen_length_printed", "sampler_printed", "value_rule_printed", "guidance_printed"]}
var0 = {"kind": "none", "value_printed": "", "n_runs": None}
arm = lambda i, lab, role: {"arm_id": i, "label_printed": lab, "role": role, "generator": "diffusion", "level_printed": lab, "level_num": None,
                            "params_printed": "not_stated", "train_tokens_printed": "not_stated", "shots_printed": "not_stated", "scoring": "generated",
                            "number_source": "run-by-authors", "steps_printed": "not_stated", "gen_length_printed": "not_stated"}
rec = {
    "id": "M03416", "form_version": "0.2", "extractor": "EA-claude-opus-5-5", "ft": "pymupdf", "blocks": ["L", "Q", "H", "K"], "meta": None,
    "study": {"study_type": "method", "modality": "text", "text_generator": "diffusion", "state_space": ["continuous-embedding"],
              "task_families": [{"family": "understanding", "generated_sample": False}], "task_other": "", "primary_task_family": "NA",
              "focal_model": "DiffuseDef", "models": [{"name": "DiffuseDef", "params_printed": "not_stated", "params_b": None}], "base_checkpoints": [],
              "training": {"training_free": "no", "stages": ["other"], "data_named": "AGNews", "tokens_printed": "not_stated", "compute_printed": "not_stated"},
              "main_sampler": {"description": "", "steps_printed": "not_stated", "nfe_printed": "not_stated", "gen_length_printed": "not_stated", "tokens_per_step_printed": "not_stated"},
              "venue_line_text": "none", "credited_component": {"text": "diffusion denoiser layer", "type": "model-or-architecture"},
              "main_comparison": {"where": "Table 1", "page": 6, "own_row": "DiffuseDef", "baseline_row": "x", "basis": "F1-table"},
              "limitations": {"categories": ["compute-or-speed"]}, "synergy_benchmark": {"present": "no", "name": ""},
              "inventory": {"I1": "no", "I2": "yes", "I3": "yes", "I4": "no", "I5": "yes"}},
    "design": {"c1_channel": [{"modality": "text", "channel": "gaussian-embedding"}], "c2_reveal": "gaussian-shared-level", "c2_multimodal": "NA",
               "c3_predictor": "noise-or-velocity", "c3_self_conditioning": "no", "c3_head_layout": "single-modality",
               "c4_position": {"rule": "all-positions", "blockwise": "no"}, "c4_joint_draw": "independent", "c4_multimodal_schedule": "NA",
               "c5_revision": ["implicit-channel"], "memory": ["none"], "objective": "mse-eps-or-velocity", "other_detail": "",
               "provenance": {k: "contributed" for k in ["D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10", "D11", "D15"]},
               "inherited_from": "", "levers": None},
    "census": {"F1_status": "NA", "F1_unit": "NA", "F2_codes": "NA", "F2_detail": "", "F3": "NA", "F4": "NA", "F5": "NA", "F6": "NA"},
    "claims": {"CT": {f"CT{i}": "no" for i in range(1, 7)}, "list": []},
    "qa": {"QA1": {"sub": {"a": "no", "b": "no", "c": "no", "d": None}, "score": None, "loc": ""},
           "QA2": {"sub": {"a": "no", "b": "yes", "c": "no"}, "score": None, "loc": ""},
           "QA3": {"sub": {"a": "unclear", "b": "no", "c": None, "d": "no"}, "score": None, "loc": ""},
           "QA4": {"sub": {"n": "no", "a": "no", "b": "no", "c": "no"}, "score": None, "loc": ""},
           "QA5": {"sub": {"n": "no", "a": "no", "b": "no"}, "score": None, "loc": ""},
           "QA6": {"sub": {"n": "no", "a": "no", "b": "no", "c": "no", "d": "no"}, "score": None, "loc": ""},
           "QA7": {"sub": {"n": None, "a": "yes", "b": "unclear", "c": "no"}, "score": None, "loc": "p.7, Table 3"},
           "QA8": {"sub": {}, "score": None, "loc": ""},
           "QA9": {"sub": {"a": "yes", "b": "no"}, "score": None, "loc": ""}},
    "units_h": [],
    "groups": [{"group_id": "G01", "rq_class": "credited-other", "factor_type": "component-removal", "factor_printed": "remove one component", "dose_unit": "NA",
                "where": "Table 3", "page": 7, "source_kind": "main-table", "orientation": "rows", "second_factor_printed": "", "anchor_arm": "A1",
                "arms": [arm("A1", "DiffuseDef", "anchor"), arm("A2", "w/o diffusion denoising", "comparison")], "credited_ablation": True,
                "held_fixed": "not stated", "other_changes": "", "budget_across_arms": "not reported", "shape": "NA", "evidence_refs": ["C01"]}],
    "units_k": [{"unit_id": "K01", "group_id": "G01", "benchmark_printed": "AGNews", "metric_printed": "accuracy under attack", "column_printed": "TF",
                 "metric_kind": "other", "higher_is_better": True, "scale": "percent", "split": "not_stated", "task_family": "understanding",
                 "n_eval_printed": "not_stated", "figure_only": False,
                 "values": [{"arm_id": "A1", "value_printed": "84.5", "cell": "C01", "col": 1, "prose": None, "value_occurrence": None, "variance": var0},
                            {"arm_id": "A2", "value_printed": "57.1", "cell": "C02", "col": 1, "prose": None, "value_occurrence": None, "variance": var0}]}],
    "evidence": [{"id": "E01", "cond": "S13", "quote": "we conduct an ablation analysis on the AGNews dataset by disabling ensembling", "loc": "p.7, §5.3"}],
    "cell_evidence": [
        {"id": "C01", "cond": "K01", "page": 7, "where": "Table 3", "row_label": "DiffuseDef", "first_col": 1, "cells": "84.5 86.0 84.6",
         "header": "Method TF TB BA", "caption": "Table 3: Ablation results for DiffuseDef's accuracy under attack on AGNews datasets.", "occurrence": None},
        {"id": "C02", "cond": "K01", "page": 7, "where": "Table 3", "row_label": "w/o diffusion denoising", "first_col": 1, "cells": "57.1 58.4 47.7",
         "header": "Method TF TB BA", "caption": "Table 3: Ablation results for DiffuseDef's accuracy under attack on AGNews datasets.", "occurrence": None}],
    "searched": {"QA1a": "§1, §5, App.", "F2": "all"}, "doubt": ["QA7b"], "notes": ""}
errs = list(V.iter_errors(rec))
print("valid record errors:", len(errs))
for e in errs[:10]:
    print(" ", list(e.path), e.message[:200])
bad = copy.deepcopy(rec)
del bad["qa"]["QA9"]["sub"]["b"]
print("missing QA9b rejected:", len(list(V.iter_errors(bad))) > 0)
bad2 = copy.deepcopy(rec)
bad2["cell_evidence"][0]["cond"] = "U07"
print("old unit id cond rejected:", len(list(V.iter_errors(bad2))) > 0)
bad3 = copy.deepcopy(rec)
bad3["groups"][0]["arms"] = bad3["groups"][0]["arms"][:1]
print("one-arm group rejected:", len(list(V.iter_errors(bad3))) > 0)
light = copy.deepcopy(rec)
light["blocks"] = ["L", "Q", "H"]; light["groups"] = []; light["units_k"] = []
print("light record errors:", len(list(V.iter_errors(light))))
