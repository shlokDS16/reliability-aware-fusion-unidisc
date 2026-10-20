"""Tests of tools/ex_validate.py.

1. Every case of analysis/extraction/validator-tests.jsonl (35; plan v0.3 s6.6), with the expected status and
   the expected per-check statuses. A case whose tool status differs is reported, never edited.
2. The v0.2 tests T01-T22 rewritten in the v0.3 entry shape (plan v0.4 s14 A7).
3. Rules the 35 cases miss: the v0.5 sign checks (four cases, plan v0.5 s11), schema validation, record-level
   checks, the CLI and determinism.

Run with pytest (python -E -P -m pytest tests/test_ex_validate.py) or without it
(python -I tests/test_ex_validate.py), which runs every test function and prints passed/total.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "analysis" / "extraction" / "validator-tests.jsonl"
CASES_SHA256 = "9991a1f7e60de3852c0948c95fff0561c9b071ba8afda09f96b9f88d4a12e2d2"
SCHEMA = ROOT / "research" / "review" / "extraction" / "extraction-schema-v0.5.json"
QC_SHA256 = "e7d2b6ee55b794e211e63a2d27404334a90a51876acc1d05d303c704c4a2c45b"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


EV = _load("ex_validate_under_test", ROOT / "tools" / "ex_validate.py")


# ------------------------------------------------------------------------------------------------ harness
def fixture_text(fx):
    """Inline text, or lines a..b (1-based, split at '\\n') of a pinned screened text, with an optional page marker."""
    if "text" in fx:
        return fx["text"].split("\n")
    data = (ROOT / fx["file"]).read_bytes()
    assert hashlib.sha256(data).hexdigest() == fx["sha256"], f"fixture hash changed: {fx['file']}"
    lines = data.decode("utf-8").split("\n")
    a, b = fx["lines"]
    out = [ln.rstrip("\r") for ln in lines[a - 1:b]]
    if fx.get("prepend_page"):
        out = [f"=== page {fx['prepend_page']} ==="] + out
    return out


def citing_to_value(c):
    """A validator-tests 'citing' item -> the validator's value context."""
    return {"ref": c["ref"], "kind": c.get("unit", "K"), "group": c.get("group", c["ref"]),
            "cell": c.get("cell"), "prose": c.get("prose"), "col": c.get("col"),
            "value_printed": c.get("value_printed", ""), "value_occurrence": c.get("value_occurrence"),
            "column_printed": c.get("column_printed"), "figure_only": c.get("figure_only", False),
            "arm_label": c.get("arm_label"), "orientation": c.get("group_orientation"),
            "benchmark_printed": c.get("benchmark_printed"), "metric_printed": c.get("metric_printed"),
            "condition_printed": c.get("condition_printed"),
            "second_factor_printed": c.get("second_factor_printed"), "origin": c.get("origin")}


def run_case(case):
    text = EV.Text(fixture_text(case["fixture"]))
    tables = [case["table"]] if case["table"] else []
    rep, _, _ = EV.check_evidence(text, tables, case["cells"], [citing_to_value(c) for c in case["citing"]])
    return rep.items


def status_of(items):
    return "fail" if any(x["severity"] == "fail" for x in items) else "pass"


_NUM_EQ = re.compile(r"^(\d+) = (\d+)")


def expectation_errors(case, items):
    """Differences between the tool's findings and the case's expected status and checks."""
    exp = case["expected"]
    errs = []
    got = status_of(items)
    if got != exp["status"]:
        fails = [f"{x['check']}:{x['status']}" for x in items if x["severity"] == "fail"]
        errs.append(f"status {got} (expected {exp['status']}); fails {fails}")
    for check, want in exp.get("checks", {}).items():
        mine = [x for x in items if x["check"] == check]
        statuses = [x["status"] for x in mine]
        if want is True:
            want_status = "complete"
        else:
            m = _NUM_EQ.match(want)
            want_status = "pass" if m else re.split(r"[ (]", want, maxsplit=1)[0]
        if want_status not in statuses:
            errs.append(f"check {check}: expected {want_status!r}, got {statuses}")
            continue
        if want_status in ("pass", "column_verified", "complete") and any(x["severity"] == "fail" for x in mine):
            errs.append(f"check {check}: expected {want_status!r} but has failures {statuses}")
        if want is not True and _NUM_EQ.match(want):
            nums = _NUM_EQ.match(want).group(0)
            if not any(x["detail"].startswith(nums) for x in mine if x["status"] == "pass"):
                errs.append(f"check {check}: expected detail {nums!r}, got {[x['detail'] for x in mine]}")
    warns = {x["status"] for x in items if x["severity"] == "warn"}
    for w in exp.get("warnings", []):
        if w not in warns:
            errs.append(f"warning {w} missing (warnings {sorted(warns)})")
    if exp["status"] == "pass" and "warnings" not in exp and "column_unverified" in warns:
        errs.append("unexpected warning column_unverified")
    return errs


def load_cases():
    data = CASES.read_bytes()
    assert hashlib.sha256(data).hexdigest() == CASES_SHA256, "validator-tests.jsonl changed"
    return [json.loads(ln) for ln in data.decode("utf-8").splitlines() if ln.strip()]


CASE_LIST = load_cases()


# ------------------------------------------------------------------------------------------------ 1. the 35 cases
def _case_test(case):
    def test():
        errs = expectation_errors(case, run_case(case))
        assert not errs, f"{case['test_id']} ({case['purpose']}): " + " | ".join(errs)
    test.__name__ = f"test_case_{case['test_id']}"
    return test


for _c in CASE_LIST:
    globals()[f"test_case_{_c['test_id']}"] = _case_test(_c)


def test_case_count():
    assert len(CASE_LIST) == 35
    assert len({c["test_id"] for c in CASE_LIST}) == 35


# ------------------------------------------------------------------------------------------------ 2. v0.2 T01-T22 (v0.3 shape)
M03416 = CASE_LIST[0]["fixture"]
T_M03416 = CASE_LIST[0]["table"]


def cell(cid, label, cells, first_col=1, row_group="", occurrence=None, page=7, table="T01"):
    return {"id": cid, "cond": "K01", "table": table, "page": page, "row_label": label, "row_group": row_group,
            "first_col": first_col, "cells": cells, "occurrence": occurrence}


def val(ref, cid, col, value, column, **kw):
    d = {"ref": ref, "kind": kw.pop("kind", "H"), "group": kw.pop("group", ref), "cell": cid, "col": col,
         "value_printed": value, "column_printed": column}
    d.update(kw)
    return d


def run(lines, tables, cells, values, prose=()):
    rep, _, _ = EV.check_evidence(EV.Text(lines), tables, cells, values, prose)
    return rep.items


def find(items, check, ref=None):
    return [x["status"] for x in items if x["check"] == check and (ref is None or x["ref"] == ref)]


WDD = cell("C01", "w/o diffusion denoising", ["57.1", "58.4", "47.7"])
DIF = cell("C02", "DiffuseDef", ["84.5", "86.0", "84.6"])


def test_T01_correct_row():
    items = run(fixture_text(M03416), [T_M03416], [WDD], [])
    assert status_of(items) == "pass" and find(items, "row") == ["pass"]


def test_T02_wrong_label_cells_mismatch():
    items = run(fixture_text(M03416), [T_M03416], [dict(WDD, row_label="w/o ensembling")], [])
    assert find(items, "row") == ["cells_mismatch"]


def test_T03_label_not_at_row_start():
    items = run(fixture_text(M03416), [T_M03416], [dict(WDD, row_label="diffusion denoising")], [])
    assert find(items, "row") == ["row_not_found"]


def test_T04_prose_row_negation_and_cell_kind():
    text = EV.Text(fixture_text(M03416))
    six = {"id": "E01", "cond": "K01", "quote": "w/o diffusion denoising 57.1 58.4 47.7", "loc": "p.7, §5.3"}
    ten = {"id": "E02", "cond": "K01", "quote": "w/o ensembling 64.2 65.8 54.9 w/o diffusion denoising 57.1 58.4 47.7",
           "loc": "p.7, §5.3"}
    rep = EV.Report()
    EV.check_prose(text, [six, ten], rep)
    assert find(rep.items, "prose_quote", "E01") == ["negation_before"]
    assert find(rep.items, "prose_quote", "E02") == ["found"]


def test_T05_value_position():
    lines = fixture_text(M03416)
    assert find(run(lines, [T_M03416], [WDD], [val("H01", "C01", 2, "58.4", "TB")]), "value") == ["pass"]
    assert find(run(lines, [T_M03416], [WDD], [val("H01", "C01", 3, "58.4", "BA")]), "value") == ["value_mismatch"]
    assert find(run(lines, [T_M03416], [WDD], [val("H01", "C01", 4, "58.4", "BA")]), "value") == ["value_outside_cells"]


def test_T06_rows_group_pass():
    vals = [val("K01.A1", "C02", 1, "84.5", "TF", kind="K", group="G01", arm_label="DiffuseDef", orientation="rows"),
            val("K01.A2", "C01", 1, "57.1", "TF", kind="K", group="G01", arm_label="w/o diffusion denoising", orientation="rows")]
    items = run(fixture_text(M03416), [T_M03416], [DIF, WDD], vals)
    assert status_of(items) == "pass", [x for x in items if x["severity"] == "fail"]
    assert find(items, "column") == ["column_verified", "column_verified"]


def test_T07_label_row_mismatch():
    vals = [val("K01.A1", "C01", 1, "57.1", "TF", kind="K", group="G01", arm_label="DiffuseDef", orientation="rows")]
    items = run(fixture_text(M03416), [T_M03416], [WDD], vals)
    assert find(items, "label_row") == ["label_row_mismatch"]


def test_T08_wrong_page():
    items = run(fixture_text(M03416), [T_M03416], [dict(WDD, page=8)], [])
    assert find(items, "row") == ["row_not_found"]


def test_T09_continuation_entry():
    cont = cell("C03", "w/o diffusion denoising", ["58.4", "47.7"], first_col=2)
    items = run(fixture_text(M03416), [T_M03416], [WDD, cont], [val("H01", "C03", 2, "58.4", "TB")])
    assert status_of(items) == "pass", [x for x in items if x["severity"] == "fail"]
    assert find(items, "row") == ["pass", "pass"] and find(items, "value") == ["pass"]


def test_T10_header_not_found():
    items = run(fixture_text(M03416), [dict(T_M03416, header="Method TF TB XX")], [WDD], [])
    assert "header_not_found" in find(items, "table")


def test_T12_caption_length():
    items = run(fixture_text(M03416), [dict(T_M03416, caption="Table 3: Ablation results")], [WDD], [])
    assert "caption_length" in find(items, "table")


T14_LINES = (["=== page 1 ===", "Table 5: Synthetic seven-column ablation table used for the cell-kind test.",
              "Model", "A", "B", "C", "D", "E", "F", "G", "Ours", "1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0"]
             + [x for i in range(1, 7) for x in [f"w/o c{i}"] + [f"{i}.{k}" for k in range(1, 8)]])
T14_TABLE = {"id": "T01", "where": "Table 5", "page": 1, "orientation": "rows", "header_levels": 1,
             "header": "Model A B C D E F G", "columns": list("ABCDEFG"), "column_roles": ["metric"],
             "row_groups": [], "row_group_role": "none",
             "caption": "Table 5: Synthetic seven-column ablation table used for the cell-kind test."}


def test_T14_cell_kind_wide_row():
    c5 = cell("C01", "w/o c5", [f"5.{k}" for k in range(1, 8)], page=1)
    items = run(T14_LINES, [T14_TABLE], [c5], [val("H01", "C01", 3, "5.3", "C")])
    assert status_of(items) == "pass" and find(items, "column") == ["column_verified"]
    rep = EV.Report()
    EV.check_prose(EV.Text(T14_LINES), [{"id": "E01", "cond": "K01", "quote": "w/o c5 5.1 5.2 5.3 5.4 5.5 5.6 5.7",
                                         "loc": "p.1, §4"}], rep)
    assert find(rep.items, "prose_quote") == ["negation_before"]


T15_LINES = ["=== page 1 ===", "Table 9: Synthetic table with the identical row printed twice on one page.",
             "Model", "A", "B", "Ours", "1.0", "2.0", "Ours", "1.0", "2.0"]
T15_TABLE = {"id": "T01", "where": "Table 9", "page": 1, "orientation": "rows", "header_levels": 1, "header": "Model A B",
             "columns": ["A", "B"], "column_roles": ["metric"], "row_groups": [], "row_group_role": "none",
             "caption": "Table 9: Synthetic table with the identical row printed twice on one page."}


def test_T15_occurrence_two_passes():
    items = run(T15_LINES, [T15_TABLE], [cell("C01", "Ours", ["1.0", "2.0"], occurrence=2, page=1)], [])
    assert find(items, "row") == ["pass"]


PROSE_TEXT = ["=== page 1 ===",
              "In our runs the model reaches 45.21 accuracy on the test set after tuning.",
              "The gain is 7.56 points on split A and 7.56 points on split B of the benchmark.",
              "0.61 0.98 0.72 0.54 0.82 0.19",
              " ".join(f"word{i}" for i in range(41)) + "."]


def _prose(eid, quote, loc="p.1, §4.2"):
    return {"id": eid, "cond": "H01", "quote": quote, "loc": loc}


def test_T16_prose_too_long():
    rep = EV.Report()
    EV.check_prose(EV.Text(PROSE_TEXT), [_prose("E01", " ".join(f"word{i}" for i in range(41)))], rep)
    assert find(rep.items, "prose_length") == ["too_long"]


def test_T17_prose_numeric_only():
    rep = EV.Report()
    EV.check_prose(EV.Text(PROSE_TEXT), [_prose("E01", "0.61 0.98 0.72 0.54 0.82 0.19")], rep)
    assert find(rep.items, "prose_letters") == ["numeric_only"]


def test_T18_value_not_in_quote():
    e = _prose("E01", "the model reaches 45.21 accuracy on the test set")
    items = run(PROSE_TEXT, [], [], [{"ref": "H01", "kind": "H", "group": "H01", "prose": "E01", "value_printed": "45.2"}], [e])
    assert find(items, "value") == ["value_not_in_quote"] and find(items, "prose_quote") == ["found"]


def test_T19_value_ambiguous_then_occurrence():
    e = _prose("E01", "The gain is 7.56 points on split A and 7.56 points on split B")
    v = {"ref": "H01", "kind": "H", "group": "H01", "prose": "E01", "value_printed": "7.56"}
    assert find(run(PROSE_TEXT, [], [], [v], [e]), "value") == ["value_ambiguous"]
    assert find(run(PROSE_TEXT, [], [], [dict(v, value_occurrence=2)], [e]), "value") == ["pass"]


def test_T20_hyphen_split_label():
    lines = ["=== page 1 ===", "Table 4: Synthetic table with a label split by line-end hyphenation here.",
             "Model", "A", "B", "Diffu-", "sion-LM 1.0 2.0"]
    t = dict(T15_TABLE, where="Table 4", caption="Table 4: Synthetic table with a label split by line-end hyphenation here.")
    items = run(lines, [t], [cell("C01", "Diffusion-LM", ["1.0", "2.0"], page=1)], [])
    assert find(items, "row") == ["pass"]


def test_T21_two_values_on_one_line():
    m12766 = next(c for c in CASE_LIST if c["test_id"] == "V06")
    pix = cell("C01", "PixArt-α (Chen et al., 2024b)",
               ["-", "Diffusion", "0.6", "0.48", "0.98", "0.50", "0.44", "0.80", "0.08", "0.07"], page=8)
    items = run(fixture_text(m12766["fixture"]), [m12766["table"]], [pix], [val("H01", "C01", 5, "0.98", "Objects / Single")])
    assert status_of(items) == "pass", [x for x in items if x["severity"] == "fail"]
    assert find(items, "row_width") == ["pass"] and find(items, "column") == ["column_unverified"]


def test_T22_quote_check_unchanged():
    path = ROOT / "analysis" / "screening" / "quote_check.py"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == QC_SHA256
    buf = io.StringIO()
    with redirect_stdout(buf):
        fails = EV.qc.self_test()
    assert fails == 0, buf.getvalue()[-500:]


# ------------------------------------------------------------------------------------------------ 3. rules the cases miss
def test_N6_footer_only_nearest_integer_dropped():
    page = EV.Text(["=== page 3 ===", "row", "7", "12", "17", ""]).page(3)
    assert page.footer == 3 and page.lines[3] == "" and page.lines[1] == "7" and page.lines[2] == "12"


def test_no_page_markers_warning():
    items = run(["Table 1: a b c d e f", "Model", "A", "Ours", "1.0"], [], [], [])
    assert find(items, "text") == ["no_page_markers"]


def test_map_not_in_header_and_order_mismatch():
    items = run(fixture_text(M03416), [dict(T_M03416, columns=["TF", "TB", "AUA"])], [WDD], [])
    assert "map_not_in_header" in find(items, "table")
    items = run(fixture_text(M03416), [dict(T_M03416, columns=["TB", "TF", "BA"])], [WDD], [])
    assert "column_order_mismatch" in find(items, "table")


def test_caption_not_found():
    items = run(fixture_text(M03416), [dict(T_M03416, caption="Table 3: Results of a different ablation on another dataset.")], [WDD], [])
    assert "caption_not_found" in find(items, "table")


def test_cell_too_long():
    lines = ["=== page 1 ===", "Table 6: Synthetic wide table for the forty-token cap on cell entries."] + \
            ["Model"] + [f"c{i}" for i in range(45)] + ["Ours"] + [f"{i}.0" for i in range(45)]
    t = {"id": "T01", "where": "Table 6", "page": 1, "orientation": "rows", "header_levels": 1,
         "header": "Model " + " ".join(f"c{i}" for i in range(45)), "columns": [f"c{i}" for i in range(45)],
         "column_roles": ["metric"], "row_groups": [], "row_group_role": "none",
         "caption": "Table 6: Synthetic wide table for the forty-token cap on cell entries."}
    items = run(lines, [t], [cell("C01", "Ours", [f"{i}.0" for i in range(45)], page=1)], [])
    assert find(items, "length") == ["too_long"]


FDM = next(c for c in CASE_LIST if c["test_id"] == "V14")


def test_row_group_not_found_and_unknown():
    t = dict(FDM["table"], row_groups=["GSM8K", "MBPP", "Countdown", "ARC"])
    items = run(fixture_text(FDM["fixture"]), [t], [dict(FDM["cells"][0], row_group="MBPP")], [])
    assert "row_group_not_found" in find(items, "row_group")
    items = run(fixture_text(FDM["fixture"]), [FDM["table"]], [dict(FDM["cells"][0], row_group="MATH")], [])
    assert "row_group_unknown" in find(items, "row_group")


LLADA = next(c for c in CASE_LIST if c["test_id"] == "V22")


def test_ungrouped_row_before_first_row_group_accepted():
    avg = cell("C01", "Average", ["73.09", "71.52", "72.43", "3.08", "72.34", "5.93", "73.54", "3.64"], page=6)
    v = val("H04", "C01", 5, "72.34", "LLaDA2.1-flash (S Mode) / Score")
    items = run(fixture_text(LLADA["fixture"]), [LLADA["table"]], [avg], [v])
    assert status_of(items) == "pass", [x for x in items if x["severity"] == "fail"]
    assert "row_group_missing" not in find(items, "row_group")


def test_occurrence_out_of_range():
    items = run(T15_LINES, [T15_TABLE], [cell("C01", "Ours", ["1.0", "2.0"], occurrence=3, page=1)], [])
    assert find(items, "row") == ["occurrence_mismatch"]


def test_cell_value_unreadable_needs_no_value_check():
    v = val("H01", "C01", 2, "unreadable", "TB")
    items = run(fixture_text(M03416), [T_M03416], [WDD], [v])
    assert find(items, "value") == ["no_value_check"] and status_of(items) == "pass"


def test_prose_value_unreadable_rejected_and_h_figure_only_exempt():
    e = _prose("E01", "the model reaches 45.21 accuracy on the test set")
    bad = {"ref": "H01", "kind": "H", "group": "H01", "prose": "E01", "value_printed": "unreadable"}
    assert find(run(PROSE_TEXT, [], [], [bad], [e]), "value") == ["unreadable_needs_cell"]
    fig = {"ref": "H01", "kind": "H", "group": "H01", "prose": "E01", "value_printed": "figure-only", "origin": "F1-figure"}
    assert find(run(PROSE_TEXT, [], [], [fig], [e]), "value") == ["exempt"]


def test_loc_format_warning():
    rep = EV.Report()
    EV.check_prose(EV.Text(PROSE_TEXT), [_prose("E01", "the model reaches 45.21 accuracy on the test set", loc="page 1")], rep)
    assert find(rep.items, "loc") == ["loc_format"]


def test_condition_and_metric_checks():
    m13864 = next(c for c in CASE_LIST if c["test_id"] == "V28")
    c = m13864["cells"][0]
    base = citing_to_value(m13864["citing"][0])
    ok = run(fixture_text(m13864["fixture"]), [m13864["table"]], [c], [base])
    assert find(ok, "condition") == ["pass"] and find(ok, "metric") == ["pass"]
    bad = run(fixture_text(m13864["fixture"]), [m13864["table"]], [c], [dict(base, condition_printed="en", metric_printed="COMET")])
    assert find(bad, "condition") == ["condition_mismatch"] and find(bad, "metric") == ["metric_column_mismatch"]


# ---- v0.5 sign checks (plan v0.5 s10.3 item 2-3; four cases) ----
SIGN_TEXT = ["=== page 1 ===",
             "Abstract. We study a synthetic masked diffusion model on two toy benchmarks in this note.",
             "Table 1: Synthetic results of two decoding variants on the toy benchmark.",
             "Variant", "Acc. ↑", "FID ↓", "Cohesion", "Base", "61.2", "12.5", "0.30", "Ours", "64.8", "10.1", "0.35",
             "The text continues after the table with more prose."]


def _arm(aid, label, role):
    return {"arm_id": aid, "label_printed": label, "role": role, "generator": "diffusion", "level_printed": label,
            "level_num": None, "params_printed": "", "train_tokens_printed": "", "shots_printed": "",
            "scoring": "generated", "number_source": "run-by-authors", "steps_printed": "", "gen_length_printed": "",
            "ar_label_source": "NA"}


def _kunit(uid, col, metric, column, hib, vals=("61.2", "64.8")):
    return {"unit_id": uid, "group_id": "G01", "benchmark_printed": "toy", "metric_printed": metric,
            "condition_printed": "", "metric_kind": "generated-sample", "higher_is_better": hib, "scale": "raw",
            "split": "test", "task_family": "other", "n_eval_printed": "not_stated", "figure_only": False,
            "values": [{"arm_id": "A1", "value_printed": vals[0], "value_num": None, "cell": "C01", "col": col,
                        "prose": None, "value_occurrence": None, "variance": {"kind": "none", "value_printed": "", "n_runs": None},
                        "column_printed": column},
                       {"arm_id": "A2", "value_printed": vals[1], "value_num": None, "cell": "C02", "col": col,
                        "prose": None, "value_occurrence": None, "variance": {"kind": "none", "value_printed": "", "n_runs": None},
                        "column_printed": column}],
            "matched": None, "metric_id": None, "benchmark_id": None, "duplicate": None}


def sign_record(units):
    return {
        "id": "S00001", "form_version": "0.5", "extractor": "EA-test-model", "ft": "pymupdf-v1", "blocks": ["K"],
        "meta": None, "study": None, "design": None, "census": None, "claims": None, "qa": None, "units_h": [],
        "groups": [{"group_id": "G01", "rq_class": None, "factor_type": "order-rule", "factor_printed": "decoding variant",
                    "dose_unit": "NA", "where": "Table 1", "page": 1, "source_kind": "main-table", "orientation": "rows",
                    "second_factor_printed": "", "anchor_arm": "A2", "anchor_rule": "focal-label",
                    "arms": [_arm("A1", "Base", "comparison"), _arm("A2", "Ours", "anchor")], "credited_ablation": True,
                    "held_fixed": "not stated", "other_changes": "", "budget_across_arms": "not reported", "shape": "NA",
                    "evidence_refs": ["C01"], "duplicate": None}],
        "units_k": units, "evidence": [],
        "table_evidence": [{"id": "T01", "where": "Table 1", "page": 1, "orientation": "rows",
                            "header": "Variant Acc. ↑ FID ↓ Cohesion", "header_levels": 1,
                            "columns": ["Acc. ↑", "FID ↓", "Cohesion"], "column_roles": ["metric"], "row_groups": [],
                            "row_group_role": "none",
                            "caption": "Table 1: Synthetic results of two decoding variants on the toy benchmark."}],
        "cell_evidence": [{"id": "C01", "cond": "K01", "table": "T01", "page": 1, "row_label": "Base", "row_group": "",
                           "first_col": 1, "cells": ["61.2", "12.5", "0.30"], "occurrence": None},
                          {"id": "C02", "cond": "K01", "table": "T01", "page": 1, "row_label": "Ours", "row_group": "",
                           "first_col": 1, "cells": ["64.8", "10.1", "0.35"], "occurrence": None}],
        "searched": {}, "doubt": [], "notes": ""}


def _schema():
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def validate(rec, lines=SIGN_TEXT):
    rep, engine = EV.validate_record(rec, EV.Text(lines), _schema())
    return rep.items


def test_sign_1_arrow_conflict_rejected():
    items = validate(sign_record([_kunit("K01", 2, "FID", "FID ↓", True, ("12.5", "10.1"))]))
    assert find(items, "sign_arrow", "K01") == ["arrow_conflict"] and status_of(items) == "fail"


def test_sign_2_arrow_agrees_accepted():
    items = validate(sign_record([_kunit("K01", 2, "FID", "FID ↓", False, ("12.5", "10.1"))]))
    assert status_of(items) == "pass", [x for x in items if x["severity"] == "fail"]
    assert find(items, "sign_arrow", "K01") == ["pass"] and "sign_route" not in [x["check"] for x in items]


def test_sign_3_same_metric_key_two_directions_rejected():
    units = [_kunit("K01", 1, "Acc.", "Acc. ↑", True), _kunit("K02", 1, "acc", "Acc. ↑", None)]
    units[1]["benchmark_printed"] = "toy-2"
    items = validate(sign_record(units))
    assert find(items, "sign_group", "K01") == ["sign_conflict_in_group"]
    assert find(items, "sign_group", "K02") == ["sign_conflict_in_group"]


def test_sign_4_ec_routing_not_a_rejection():
    unmapped = validate(sign_record([_kunit("K01", 3, "Cohesion", "Cohesion", True, ("0.30", "0.35"))]))
    assert find(unmapped, "sign_route", "K01") == ["sign_extractor_only"] and status_of(unmapped) == "pass"
    conflict = validate(sign_record([_kunit("K01", 3, "PPL", "Cohesion", True, ("0.30", "0.35"))]))
    assert "sign_lookup_conflict" in find(conflict, "sign_route", "K01")
    assert not [x for x in conflict if x["severity"] == "fail" and x["check"].startswith("sign")]


def test_sign_header_arrow_routed():
    rec = sign_record([_kunit("K01", 2, "FID", "FID", True, ("12.5", "10.1"))])
    rec["table_evidence"][0]["columns"] = ["Acc.", "FID", "Cohesion"]
    items = validate(rec)
    assert find(items, "sign_header_arrow", "K01") == ["header_arrow_conflict"]
    assert "header_arrow_conflict" in find(items, "sign_route", "K01")


def test_ka1_lookup_qualifiers():
    lk = EV.load_metric_lookup()
    assert EV.metric_lookup("Avg. acc", lk) == ("accuracy", True)
    assert EV.metric_lookup("pass@1", lk) == ("pass@k", True)
    assert EV.metric_lookup("FID ↓", lk) == ("fid", False)
    assert EV.metric_lookup("Cohesion index", lk) is None


# ---- schema and record level ----
def test_schema_valid_record_and_engines_agree():
    rec = sign_record([_kunit("K01", 1, "Acc.", "Acc. ↑", True)])
    schema = _schema()
    assert EV.MiniValidator(schema).errors(rec) == []
    bad = copy.deepcopy(rec)
    bad["form_version"] = "0.4"
    bad["units_k"][0]["values"] = bad["units_k"][0]["values"][:1]
    bad["groups"][0]["arms"][0]["role"] = "baseline"
    bad["extra"] = 1
    mini = EV.MiniValidator(schema).errors(bad)
    assert len({p for p, _ in mini}) >= 4
    try:
        import jsonschema
        js = list(jsonschema.Draft202012Validator(schema).iter_errors(bad))
        assert bool(js) and not list(jsonschema.Draft202012Validator(schema).iter_errors(rec))
    except Exception:  # jsonschema not importable under -I: the built-in validator is the engine
        pass


def _mutations(rec):
    """Deterministic single-keyword violations of the v0.5 schema (and two harmless edits)."""
    muts = []

    def m(fn):
        r = copy.deepcopy(rec)
        fn(r)
        muts.append(r)
    m(lambda r: r.pop("notes"))                                              # required
    m(lambda r: r.update(extra=1))                                           # additionalProperties false
    m(lambda r: r.update(form_version="0.4"))                                # const
    m(lambda r: r.update(extractor="XX-model"))                              # pattern
    m(lambda r: r.update(blocks=[]))                                         # minItems
    m(lambda r: r.update(blocks=["K", "Z"]))                                 # enum in items
    m(lambda r: r["groups"][0].update(page=0))                               # minimum
    m(lambda r: r["groups"][0].update(page=1.5))                             # integer
    m(lambda r: r["groups"][0].update(credited_ablation="yes"))              # boolean
    m(lambda r: r["groups"][0]["arms"].pop())                                # minItems 2
    m(lambda r: r["units_k"][0].update(higher_is_better="true"))             # type list
    m(lambda r: r["table_evidence"][0].update(header_levels=True))           # enum [1, 2] is not boolean
    m(lambda r: r["table_evidence"][0].update(column_roles=["metric"] * 3))  # maxItems
    m(lambda r: r["cell_evidence"][0].update(row_label=""))                  # minLength
    m(lambda r: r.update(searched={"BAD": "x"}))                             # propertyNames
    m(lambda r: r.update(doubt=["K01", "K01"]))                              # possible uniqueItems
    m(lambda r: r.update(notes="free text is fine"))                         # valid edit
    m(lambda r: r["units_k"][0].update(higher_is_better=None))               # valid edit
    return muts


def test_schema_engines_agree_on_mutations():
    try:
        import jsonschema
        jsonschema.Draft202012Validator
    except Exception:  # jsonschema absent under -I; nothing to compare against
        return
    schema = _schema()
    rec = sign_record([_kunit("K01", 1, "Acc.", "Acc. ↑", True)])
    js = jsonschema.Draft202012Validator(schema)
    mini = EV.MiniValidator(schema)
    for i, r in enumerate(_mutations(rec)):
        assert bool(list(js.iter_errors(r))) == bool(mini.errors(r)), f"mutation {i}"


def test_we_expected_count_check_detects_a_dropped_unit():
    we = _load("build_we_expected_under_test", ROOT / "analysis" / "extraction" / "build_we_expected.py")
    md = we.MD.read_text(encoding="utf-8")
    rows = we.build_rows()
    errs, _ = we.count_check(rows, md)
    assert errs == []
    errs, _ = we.count_check(rows[:-1], md)
    assert errs, "dropping a unit must fail the count check"
    out = ROOT / "analysis" / "extraction" / "we-expected.jsonl"
    written = [json.loads(ln) for ln in out.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert [{k: v for k, v in r.items() if k != "source_sha256"} for r in written] == rows


def test_schema_if_then_qa_nulls():
    schema = _schema()
    qa4 = schema["properties"]["qa"]["properties"]["QA4"]
    ok = {"sub": {"n": "yes", "a": None, "b": None, "c": "no"}, "score": None, "loc": ""}
    bad = {"sub": {"n": "yes", "a": "yes", "b": None, "c": "no"}, "score": None, "loc": ""}
    v = EV.MiniValidator(schema)
    assert v.errors(ok, qa4) == [] and v.errors(bad, qa4) != []


def test_record_level_refs_and_anchor():
    rec = sign_record([_kunit("K01", 1, "Acc.", "Acc. ↑", True)])
    rec["groups"][0]["anchor_arm"] = "A1"
    rec["units_k"][0]["values"][1]["arm_id"] = "A9"
    rec["groups"][0]["evidence_refs"] = ["E07"]
    items = validate(rec)
    assert "anchor_count" in find(items, "anchor")
    assert "arm_missing" in find(items, "refs") and "evidence_missing" in find(items, "refs")


def test_record_level_where_and_reuse():
    rec = sign_record([_kunit("K01", 1, "Acc.", "Acc. ↑", True), _kunit("K02", 1, "Acc.", "Acc. ↑", True)])
    rec["units_k"][1]["benchmark_printed"] = "toy-2"
    rec["groups"][0]["where"] = "Table 2"
    items = validate(rec)
    assert "where_mismatch" in find(items, "where") and "cell_reused" in find(items, "reuse")


def test_missing_figure_only_in_record():
    u = _kunit("K01", 1, "Acc.", "Acc. ↑", True)
    for v in u["values"]:
        v.update(value_printed="figure-only", cell=None, col=None, column_printed=None)
    items = validate(sign_record([u]))
    assert find(items, "value") == ["missing_evidence", "missing_evidence"]
    u["figure_only"] = True
    items = validate(sign_record([u]))
    assert find(items, "value") == ["exempt", "exempt"]


def _run_cli(rec, lines):
    with tempfile.TemporaryDirectory() as d:
        rp, tp = Path(d) / "rec.json", Path(d) / "text.txt"
        rp.write_text(json.dumps(rec), encoding="utf-8")
        tp.write_bytes("\n".join(lines).encode("utf-8"))
        r = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "ex_validate.py"), "--record", str(rp),
                            "--text", str(tp)], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout


def test_cli_accept_reject_and_determinism():
    good = sign_record([_kunit("K01", 1, "Acc.", "Acc. ↑", True)])
    code, out1 = _run_cli(good, SIGN_TEXT)
    assert code == 0, out1[-2000:]
    rows = [json.loads(ln) for ln in out1.splitlines()]
    assert rows[-1]["summary"] and rows[-1]["status"] == "accepted" and rows[-1]["fail"] == 0
    assert all(set(r) == {"id", "extractor", "check", "ref", "status", "severity", "detail"} for r in rows[:-1])
    code2, out2 = _run_cli(good, SIGN_TEXT)
    assert out1 == out2 and code2 == 0
    bad = sign_record([_kunit("K01", 1, "Acc.", "Acc. ↑", False)])
    code, out = _run_cli(bad, SIGN_TEXT)
    assert code == 1 and json.loads(out.splitlines()[-1])["status"] == "rejected"


def test_cli_usage_error_exit_2():
    with tempfile.TemporaryDirectory() as d:
        r = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "ex_validate.py"), "--record",
                            str(Path(d) / "missing.json"), "--text", str(Path(d) / "missing.txt")],
                           capture_output=True, text=True)
    assert r.returncode == 2


# ------------------------------------------------------------------------------------------------ runner without pytest
def _all_tests():
    return [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]


if __name__ == "__main__":
    passed, failed = 0, []
    for name, fn in _all_tests():
        try:
            fn()
            passed += 1
        except Exception as exc:  # noqa: BLE001
            failed.append((name, f"{type(exc).__name__}: {exc}"))
    for name, msg in failed:
        print(f"FAIL {name}: {msg}")
    print(f"tests passed: {passed}/{passed + len(failed)}")
    sys.exit(1 if failed else 0)
