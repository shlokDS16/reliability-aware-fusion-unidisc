"""Synthetic extraction records, lookups, validator reports and manifests for the tests of agreement.py,
ex_dispatch.py and draw_pilot.py (EXTRACTION-PLAN-v0.5 s11; s14 A7, B3). Nothing here comes from a paper: every
label, number and benchmark name is invented ("Bench-A", "Model-Z"). Records follow extraction-schema-v0.5.json
(tests/extraction/test_agreement.py::test_synthetic_records_follow_schema_v05 validates them).

Use: import from tests; `python -E -P analysis/extraction/fixtures/synth.py --write` rewrites the static fixture
files beside this module (lookups/, phase1-bounds-fixture.json) from code.
"""
from __future__ import annotations

import copy
import csv
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTR = HERE.parent
FT = "pymupdf-1.27.2.3 text of the PDF, page markers '=== page N ==='"

# --- lookups (synthetic strings; the real lookups are analysis/extraction/lookups/*-v1.csv) -----------------
BENCH = [("bench-a", "B:bench-a"), ("bench-b", "B:bench-b"), ("bench-c", "B:bench-c")]
METRIC = [("acc", "M:acc", "true"), ("accuracy", "M:acc", "true"), ("ppl", "M:ppl", "false"),
          ("perplexity", "M:ppl", "false"), ("latency", "M:latency", "false"), ("score", "M:score", "")]


def write_lookups(d: Path) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "benchmark-ids-v1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["printed", "id"])
        w.writerows(BENCH)
    with open(d / "metric-ids-v1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["printed", "id", "higher_is_better"])
        w.writerows(METRIC)
    return d


# --- record template ----------------------------------------------------------------------------------------
def _qa():
    q = {}
    subs = {"QA1": "abcd", "QA2": "abc", "QA3": "abcd", "QA4": "nabc", "QA5": "nab", "QA6": "nabcd",
            "QA7": "nabc", "QA9": "ab"}
    for item, letters in subs.items():
        sub = {}
        for L in letters:
            sub[L] = "no" if L == "n" else "yes"
        if item == "QA1":
            sub["d"] = None
        if item == "QA3":
            sub["c"] = None
        if item == "QA7":
            sub["n"] = None
        q[item] = {"sub": sub, "score": {"low": 2, "high": 2}, "loc": "p.3, §4"}
    q["QA8"] = {"sub": {}, "score": None, "loc": ""}
    return q


def arm(aid, label, role="comparison", generator="diffusion", scoring="generated", level=""):
    return {"arm_id": aid, "label_printed": label, "role": role, "generator": generator, "level_printed": level,
            "level_num": None, "params_printed": "", "train_tokens_printed": "", "shots_printed": "",
            "scoring": scoring, "number_source": "run-by-authors", "steps_printed": "", "gen_length_printed": "",
            "ar_label_source": "NA"}


def group(gid, where, arms, anchor="A1", factor_type="steps-or-nfe", second="", held="stated", other="",
          budget="matched", credited=False, anchor_rule="focal-label", orientation="rows", shape="NA",
          source_kind="main-table"):
    return {"group_id": gid, "rq_class": None, "factor_type": factor_type, "factor_printed": "steps",
            "dose_unit": "steps", "where": where, "page": 5, "source_kind": source_kind, "orientation": orientation,
            "second_factor_printed": second, "anchor_arm": anchor, "anchor_rule": anchor_rule, "arms": arms,
            "credited_ablation": credited, "held_fixed": held, "other_changes": other,
            "budget_across_arms": budget, "shape": shape, "evidence_refs": []}


def kunit(uid, gid, bench, metric, values, hib=True, cond="", split="test", figure_only=False,
          metric_kind="generated-sample"):
    return {"unit_id": uid, "group_id": gid, "benchmark_printed": bench, "metric_printed": metric,
            "condition_printed": cond, "metric_kind": metric_kind, "higher_is_better": hib, "scale": "percent",
            "split": split, "task_family": "reasoning", "n_eval_printed": "not_stated", "figure_only": figure_only,
            "values": values}


def kval(arm_id, value, cell=None, col=None, column_printed=None, prose=None, occ=None):
    return {"arm_id": arm_id, "value_printed": value, "value_num": None, "cell": cell, "col": col, "prose": prose,
            "value_occurrence": occ, "variance": {"kind": "none", "value_printed": "", "n_runs": None},
            "column_printed": column_printed}


def hunit(uid, origin="F1-table", is_f1=True, ref="C01", col=1, column_printed="Bench-A / Acc", where="Table 2",
          value="41.7", value_type="level", arm_role="own", metric_kind="generated-sample", occ=None):
    return {"unit_id": uid, "is_F1": is_f1, "origin": origin, "value_type": value_type, "arm_role": arm_role,
            "reference_printed": "", "model_printed": "Model-Z", "metric_printed": "Acc",
            "metric_kind": metric_kind, "higher_is_better": True, "benchmark_printed": "Bench-A", "split": "test",
            "task_family": "reasoning", "value_printed": value, "value_num": None, "value_unit": "%",
            "scale": "percent",
            "setting": {k: "not_stated" for k in ("steps_printed", "nfe_printed", "tokens_per_step_printed",
                                                  "gen_length_printed", "sampler_printed", "value_rule_printed",
                                                  "guidance_printed")},
            "variance": {"kind": "none", "value_printed": "", "n_runs": None}, "evidence_ref": ref,
            "value_occurrence": occ, "column_printed": column_printed if origin == "F1-table" else "",
            "col": col if origin == "F1-table" else None, "trace": None, "trace_col": None,
            "loc": {"page": 5, "where": where if origin == "F1-table" else "abstract"}}


def base_record(rid: str, extractor: str = "EA-claude-opus-5-5") -> dict:
    """A complete, schema-valid synthetic record: 2 groups (3 and 2 arms), 3 K units, 2 H units."""
    r = {
        "id": rid, "form_version": "0.5", "extractor": extractor, "ft": FT, "blocks": ["L", "Q", "H", "K"],
        "meta": None,
        "study": {
            "study_type": "method", "modality": "text", "text_generator": "diffusion",
            "state_space": ["discrete-absorbing"],
            "task_families": [{"family": "reasoning", "generated_sample": True},
                              {"family": "code", "generated_sample": True}],
            "task_other": "", "primary_task_family": "reasoning", "focal_model": "Model-Z",
            "models": [{"name": "Model-Z", "params_printed": "7B", "params_b": 7}],
            "base_checkpoints": ["Base-Q"],
            "training": {"training_free": "no", "stages": ["sft"], "data_named": "Data-X", "tokens_printed": "1B",
                         "compute_printed": "not_stated"},
            "main_sampler": {"description": "confidence ranked", "steps_printed": "64", "nfe_printed": "64",
                             "gen_length_printed": "256", "tokens_per_step_printed": "4"},
            "venue_line_text": "none",
            "credited_component": {"text": "planner head", "type": "model-or-architecture"},
            "main_comparison": {"where": "Table 2", "page": 5, "own_row": "Model-Z", "baseline_row": "Base-Q",
                                "basis": "F1-table", "row_group": ""},
            "limitations": {"categories": ["compute-or-speed", "scale"]},
            "synergy_benchmark": {"present": "no", "name": ""},
            "inventory": {"I1": "yes", "I2": "no", "I3": "yes", "I4": "no", "I5": "no"},
            "focal_config": "Table 2: Model-Z",
        },
        "design": {
            "c1_channel": [{"modality": "text", "channel": "erasure"}], "c2_reveal": "independent-shared-level",
            "c2_multimodal": "NA", "c3_predictor": "clean-marginals", "c3_self_conditioning": "no",
            "c3_head_layout": "single-modality", "c4_position": {"rule": "confidence-ranked", "blockwise": "yes"},
            "c4_joint_draw": "independent", "c4_multimodal_schedule": "NA", "c5_revision": ["none"],
            "memory": ["none"], "objective": "elbo-ce", "other_detail": "",
            "provenance": {f"D{i:02d}": "contributed" for i in list(range(1, 12)) + [15]},
            "inherited_from": "", "levers": None,
        },
        "census": {"F1_status": "number", "F1_unit": "H02", "F2_codes": "A+T", "F2_detail": "", "F3": "yes",
                   "F4": "partial", "F5": "stated", "F6": "not stated"},
        "claims": {"CT": {f"CT{i}": ("yes" if i in (1, 3) else "no") for i in range(1, 7)},
                   "list": [{"claim_id": "CL1", "source": "abstract", "types": ["CT1"], "has_number": True,
                             "status": "match", "h_units": ["H01"], "trace": ["C01"]}]},
        "qa": _qa(),
        "units_h": [
            hunit("H01", origin="abstract", is_f1=False, ref="E01", value="41.7"),
            hunit("H02", origin="F1-table", is_f1=True, ref="C01", col=1, column_printed="Bench-A / Acc"),
        ],
        "groups": [
            group("G01", "Table 2", [arm("A1", "Model-Z", role="anchor"), arm("A2", "Model-Z (16 steps)"),
                                     arm("A3", "Model-Z (8 steps)")]),
            group("G02", "Table 3", [arm("A1", "Model-Z", role="anchor"), arm("A2", "w/o planner head")],
                  factor_type="component-removal", credited=True, anchor_rule="full-configuration",
                  budget="not reported", held="not stated"),
        ],
        "units_k": [
            kunit("K01", "G01", "Bench-A", "Acc", [kval("A1", "41.7", "C01", 1, "Bench-A / Acc"),
                                                    kval("A2", "40.2", "C02", 1, "Bench-A / Acc"),
                                                    kval("A3", "38.9", "C03", 1, "Bench-A / Acc")]),
            kunit("K02", "G01", "Bench-B", "PPL", [kval("A1", "12.1", "C01", 2, "Bench-B / PPL"),
                                                    kval("A2", "12.9", "C02", 2, "Bench-B / PPL"),
                                                    kval("A3", "13.4", "C03", 2, "Bench-B / PPL")], hib=False,
                  metric_kind="likelihood"),
            kunit("K03", "G02", "Bench-A", "Acc", [kval("A1", "41.7", "C04", 1, "Acc"),
                                                    kval("A2", "36.0", "C05", 1, "Acc")]),
        ],
        "evidence": [{"id": "E01", "cond": "H01", "quote": "Model-Z reaches 41.7 on the synthetic Bench-A test set",
                      "loc": "p.1, abstract"}],
        "table_evidence": [
            {"id": "T01", "where": "Table 2", "page": 5, "orientation": "rows", "header": "Model Bench-A Bench-B",
             "header_levels": 2, "columns": ["Bench-A / Acc", "Bench-B / PPL"], "column_roles": ["benchmark", "metric"],
             "row_groups": [], "row_group_role": "none", "caption": "Table 2: Synthetic main results on two benchmarks."},
            {"id": "T02", "where": "Table 3", "page": 6, "orientation": "rows", "header": "Variant Acc",
             "header_levels": 1, "columns": ["Acc"], "column_roles": ["metric"], "row_groups": [],
             "row_group_role": "none", "caption": "Table 3: Synthetic ablation of the planner head."},
        ],
        "cell_evidence": [
            {"id": "C01", "cond": "K01", "table": "T01", "page": 5, "row_label": "Model-Z", "row_group": "",
             "first_col": 1, "cells": ["41.7", "12.1"], "occurrence": None},
            {"id": "C02", "cond": "K01", "table": "T01", "page": 5, "row_label": "Model-Z (16 steps)",
             "row_group": "", "first_col": 1, "cells": ["40.2", "12.9"], "occurrence": None},
            {"id": "C03", "cond": "K01", "table": "T01", "page": 5, "row_label": "Model-Z (8 steps)",
             "row_group": "", "first_col": 1, "cells": ["38.9", "13.4"], "occurrence": None},
            {"id": "C04", "cond": "K03", "table": "T02", "page": 6, "row_label": "Model-Z", "row_group": "",
             "first_col": 1, "cells": ["41.7"], "occurrence": None},
            {"id": "C05", "cond": "K03", "table": "T02", "page": 6, "row_label": "w/o planner head",
             "row_group": "", "first_col": 1, "cells": ["36.0"], "occurrence": None},
        ],
        "searched": {"I2": "§4, Table 2"}, "doubt": [], "notes": "",
    }
    return r


def pair(rid: str):
    """Identical X (EA) and Y (EB) records."""
    x = base_record(rid, "EA-claude-opus-5-5")
    y = copy.deepcopy(x)
    y["extractor"] = "EB-claude-sonnet-5-5"
    return x, y


def perturb(rec: dict, rng, p: float) -> dict:
    """A second reader's copy with random disagreements: each of 12 kinds happens with probability p
    (rng is a random.Random). The record stays schema-valid."""
    r = copy.deepcopy(rec)
    if rng.random() < p:
        r["study"]["study_type"] = "analysis"
    if rng.random() < p:
        r["design"]["c2_reveal"] = "block"
    if rng.random() < p:
        r["census"]["F3"] = "no"
    if rng.random() < p:
        r["qa"]["QA2"]["sub"]["b"] = "unclear"
        r["qa"]["QA2"]["score"] = {"low": 1, "high": 2}
    if rng.random() < p:
        r["claims"]["CT"]["CT2"] = "yes"
    if rng.random() < p:
        r["groups"][0]["anchor_arm"] = "A2"
    if rng.random() < p:
        r["groups"][0]["held_fixed"] = "co-varied"
    if rng.random() < p:
        r["groups"][0]["arms"][2]["scoring"] = "likelihood"
    if rng.random() < p:
        r["units_k"][0]["values"][1]["value_printed"] = "40.3"
    if rng.random() < p:
        r["units_k"][1]["higher_is_better"] = None
    if rng.random() < p:
        r["groups"] = r["groups"][:1]
        r["units_k"] = [u for u in r["units_k"] if u["group_id"] == "G01"]
    if rng.random() < p:
        r["units_h"] = r["units_h"][1:]                       # the abstract unit is missed; F1 unit kept
    return r


def validator_lines(records, fails=(), unverified=()):
    """Validator report lines (plan v0.2 s6.5 shape): one summary line per record, plus a fail line for each
    (id, extractor, ref) in fails and a column_unverified warning for each (id, extractor, cell id)."""
    out = []
    for r in records:
        out.append({"id": r["id"], "extractor": r["extractor"], "check": "summary", "ref": "", "status": "ok",
                    "severity": "info", "detail": ""})
    for i, e, ref in fails:
        out.append({"id": i, "extractor": e, "check": "value_mismatch", "ref": ref, "status": "fail",
                    "severity": "fail", "detail": "synthetic"})
    for i, e, ref in unverified:
        out.append({"id": i, "extractor": e, "check": "column_unverified", "ref": ref, "status": "warn",
                    "severity": "warn", "detail": "synthetic"})
    return out


def stage_a_manifest(we_ids, drawn):
    """drawn: list of (id, pool)."""
    ids = list(we_ids) + [i for i, _ in drawn]
    stratum = {i: "WE" for i in we_ids}
    stratum.update({i: p for i, p in drawn})
    order = ["WE"] + list(dict.fromkeys(p for _, p in drawn))
    return {"stage": "stage-a", "ids": ids, "stratum": stratum, "strata_order": order,
            "worked_examples": list(we_ids), "drawn": [i for i, _ in drawn]}


def gate_manifest(per_stratum=40, spares=5, strata=("G-short", "G-long", "G-mm"), phase1=20):
    lists, sp, stratum = {}, {}, {}
    for h, s in enumerate(strata):
        lists[s] = [f"S{h}{j:03d}" for j in range(per_stratum)]
        sp[s] = [f"S{h}{j:03d}" for j in range(per_stratum, per_stratum + spares)]
        for i in lists[s] + sp[s]:
            stratum[i] = s
    return {"stage": "gate", "lists": lists, "spares": sp, "per_stratum_phase1": phase1,
            "strata_order": list(strata), "stratum": stratum,
            "ids": [i for s in strata for i in lists[s] + sp[s]]}


def write_jsonl(path: Path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


# --- phase-1 bound fixture (s11: fixture comparison of phase1_bounds on a stored (x, m) set) ---------------
def make_phase1_fixture(path: Path):
    import numpy as np
    spec = importlib.util.spec_from_file_location("gate_rule_v05", EXTR / "gate_rule_v05.py")
    gr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gr)
    cfg = json.loads((EXTR / "gate-config-v05.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(20267000)
    xm = {}
    for j, k in enumerate(gr.icc_metrics(cfg)):
        m = rng.poisson(4 + (j % 5) * 3, 60)
        p = 0.6 + 0.35 * ((j % 7) / 7)
        x = rng.binomial(m, rng.beta(p * 9, (1 - p) * 9, 60))
        xm[k] = ([int(v) for v in x], [int(v) for v in m])
    U = gr.phase1_bounds({k: (np.array(v[0]), np.array(v[1])) for k, v in xm.items()}, cfg,
                         np.random.default_rng(cfg["bound"]["seed_phase1"]))
    path.write_text(json.dumps({"note": "synthetic (x, m) per ICC metric, 60 records; U = gate_rule_v05."
                                        "phase1_bounds with seed_phase1 of gate-config-v05.json",
                                "seed_data": 20267000, "xm": xm, "U": U}, indent=1), encoding="utf-8")
    return path


if __name__ == "__main__":
    import sys
    if "--write" in sys.argv:
        write_lookups(HERE / "lookups")
        make_phase1_fixture(HERE / "phase1-bounds-fixture.json")
        print("wrote", HERE / "lookups", HERE / "phase1-bounds-fixture.json")
