"""End-to-end synthetic pipeline test of the Stage A extraction tools (form v0.5): ex_dispatch -> two extractor
records per id -> ex_validate (CLI, one record per call) -> agreement.py --mode stage-a.

The two ids are real includes (analysis/screening/ft-t1/t1-decisions-all.jsonl: decision include) with real full
texts in research/sources/md/fulltext-pymupdf/:
  M03416  DiffuseDef, Table 3 (page 7, lines 845-887): single-level header "Method TF TB BA", four rows; a prose
          sentence on page 6 (lines 758-759: "...difference can be reduced to less than 10% AUA.").
  M13864  Diffusion vs Autoregression (code comment translation), Table 2 (page 7): two-level header
          "Models Metrics Time / BLEU COMET (sec.) / ru en ru en", rows Dream-v0-Instruct-7B (rate=1) and Qwen2.5-7B.
The records are synthetic (not an extraction: no claim is made about either paper); every cell and quote they
cite is copied from those texts. Every folder, report and output goes to a pytest tmp folder; the real dispatch
log (research/review/extraction/dispatch-log.jsonl) is never written (ex_dispatch --log points to tmp).

Designed differences between EA (X) and EB (Y), and what the agreement output must therefore show:
  M03416  EB misses the BA unit (K03) and splits the row "w/o adv training" into two entries, C04 (first_col 2)
          and C05 (first_col 3), with no first_col 1 entry: the validator fails row_start for ref "C04+C05" and
          EB's TF unit has no value for that arm.
  M13864  EB gives COMET ru higher_is_better false (lookup: true), so the sign goes to EC; the Time (sec.) unit's
          metric is not in the lookup, so its sign goes to EC in both readers. The header is two-level, so the
          validator marks every value of this table column_unverified (plan v0.3 s6.3 item 9).
Run: python -E -P -m pytest tests/extraction/test_pipeline.py
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

import ex_synth as synth

ROOT = Path(__file__).resolve().parents[2]
TEXTS = ROOT / "research" / "sources" / "md" / "fulltext-pymupdf"
REAL_LOG = ROOT / "research" / "review" / "extraction" / "dispatch-log.jsonl"
SCHEMA = ROOT / "research" / "review" / "extraction" / "extraction-schema-v0.5.json"
EXV = ROOT / "tools" / "ex_validate.py"
CFG = ROOT / "analysis" / "extraction" / "gate-config-v05.json"
IDS = ["M03416", "M13864"]
TEXT_SHA = {"M03416": "ae6f033f5823bee4160343ba0a77e3ab57c8861e831180306fa7e6ab405369cc"}
EA, EB = "EA-claude-opus-5-5", "EB-claude-sonnet-5-5"

# lookups written for this test only (the real analysis/extraction/lookups/*-v1.csv do not exist yet)
BENCH = [("agnews", "B:agnews"), ("codecommenttranslation", "B:cct")]
METRIC = [("accuracy", "M:acc", "true"), ("bleu", "M:bleu", "true"), ("comet", "M:comet", "true")]


# ------------------------------------------------------------------------------------------------ records
def _table(tid, where, page, header, levels, columns, roles, caption):
    return {"id": tid, "where": where, "page": page, "orientation": "rows", "header": header, "header_levels": levels,
            "columns": columns, "column_roles": roles, "row_groups": [], "row_group_role": "none", "caption": caption}


def _cell(cid, cond, label, cells, page=7, first_col=1):
    return {"id": cid, "cond": cond, "table": "T01", "page": page, "row_label": label, "row_group": "",
            "first_col": first_col, "cells": cells, "occurrence": None}


def _h(uid, cell, col, column, value, metric, bench, where, page=7, family="understanding"):
    u = synth.hunit(uid, origin="F1-table", is_f1=True, ref=cell, col=col, column_printed=column, where=where,
                    value=value)
    u.update({"metric_printed": metric, "benchmark_printed": bench, "task_family": family, "model_printed": "own"})
    u["loc"] = {"page": page, "where": where}
    return u


def m03416(extractor):
    r = synth.base_record("M03416", extractor)
    labels = ["DiffuseDef", "w/o ensembling", "w/o diffusion denoising", "w/o adv training"]
    rows = [["84.5", "86.0", "84.6"], ["64.2", "65.8", "54.9"], ["57.1", "58.4", "47.7"], ["80.3", "80.9", "80.5"]]
    r["table_evidence"] = [_table("T01", "Table 3", 7, "Method TF TB BA", 1, ["TF", "TB", "BA"], ["condition"],
                                  "Table 3: Ablation results for DiffuseDef's accuracy under attack on AGNews datasets.")]
    r["cell_evidence"] = [_cell(f"C{k + 1:02d}", "K01", labels[k], rows[k]) for k in range(4)]
    r["evidence"] = [{"id": "E01", "cond": "CL1",
                      "quote": "accuracy and accuracy under attack, and such a difference can be reduced to less than 10% AUA.",
                      "loc": "p.6, §5.1"}]
    r["units_h"] = [_h("H01", "C01", 1, "TF", "84.5", "accuracy", "AGNews", "Table 3")]
    arms = [synth.arm("A1", labels[0], role="anchor")] + [synth.arm(f"A{k + 1}", labels[k]) for k in range(1, 4)]
    r["groups"] = [synth.group("G01", "Table 3", arms, factor_type="component-removal", credited=True,
                               anchor_rule="full-configuration", budget="not reported", held="stated")]
    r["groups"][0]["page"] = 7
    r["units_k"] = []
    for j, cond in enumerate(["TF", "TB", "BA"]):
        vals = [synth.kval(f"A{k + 1}", rows[k][j], f"C{k + 1:02d}", j + 1, cond) for k in range(4)]
        r["units_k"].append(synth.kunit(f"K{j + 1:02d}", "G01", "AGNews", "accuracy", vals, cond=cond))
    for u in r["units_k"]:
        u["task_family"] = "understanding"
    r["study"]["primary_task_family"] = "understanding"
    r["study"]["task_families"] = [{"family": "understanding", "generated_sample": False}]
    r["study"]["focal_model"] = "DiffuseDef"
    r["study"]["main_comparison"] = {"where": "Table 3", "page": 7, "own_row": "DiffuseDef",
                                     "baseline_row": "w/o adv training", "basis": "F1-table", "row_group": ""}
    r["claims"]["list"][0].update({"h_units": ["H01"], "trace": ["C01"]})
    r["census"]["F1_unit"] = "H01"
    return r


def m03416_eb():
    r = m03416(EB)
    r["units_k"] = r["units_k"][:2]                                    # BA unit missed
    r["cell_evidence"][3] = _cell("C04", "K02", "w/o adv training", ["80.9"], first_col=2)
    r["cell_evidence"].append(_cell("C05", "K02", "w/o adv training", ["80.5"], first_col=3))
    r["units_k"][0]["values"] = r["units_k"][0]["values"][:3]           # TF: no entry for 80.3
    return r


def m13864(extractor):
    r = synth.base_record("M13864", extractor)
    cols = ["BLEU / ru", "BLEU / en", "COMET / ru", "COMET / en", "Time (sec.)"]
    labels = ["Dream-v0-Instruct-7B (rate=1)", "Qwen2.5-7B"]
    rows = [["0.215", "0.328", "0.681", "0.826", "9.48"], ["0.180", "0.193", "0.531", "0.576", "1.85"]]
    r["table_evidence"] = [_table("T01", "Table 2", 7, "Models Metrics Time BLEU COMET (sec.) ru en ru en", 2, cols,
                                  ["metric", "condition"],
                                  "Table 2. Table comparing the diffusion-based model Dream and the autoregressive "
                                  "model Qwen in terms of generation quality and speed.")]
    r["cell_evidence"] = [_cell(f"C{k + 1:02d}", "K01", labels[k], rows[k]) for k in range(2)]
    r["evidence"] = []
    r["units_h"] = [_h("H01", "C01", 1, "BLEU / ru", "0.215", "BLEU", "not stated", "Table 2", family="code")]
    arms = [synth.arm("A1", labels[0], role="anchor"), synth.arm("A2", labels[1], generator="autoregressive")]
    r["groups"] = [synth.group("G01", "Table 2", arms, factor_type="model-class", credited=False,
                               anchor_rule="focal-label", budget="matched", held="stated")]
    r["groups"][0]["page"] = 7
    r["units_k"] = []
    for j, leaf in enumerate(cols):
        metric, cond = (leaf.split(" / ") + [""])[:2]
        vals = [synth.kval(f"A{k + 1}", rows[k][j], f"C{k + 1:02d}", j + 1, leaf) for k in range(2)]
        u = synth.kunit(f"K{j + 1:02d}", "G01", "not stated", metric, vals, cond=cond, hib=(j < 4))
        u["task_family"] = "code"
        r["units_k"].append(u)
    r["study"]["primary_task_family"] = "code"
    r["study"]["task_families"] = [{"family": "code", "generated_sample": True}]
    r["study"]["focal_model"] = "Dream-v0-Instruct-7B"
    r["study"]["main_comparison"] = {"where": "Table 2", "page": 7, "own_row": labels[0], "baseline_row": labels[1],
                                     "basis": "F1-table", "row_group": ""}
    r["claims"]["list"][0].update({"h_units": ["H01"], "trace": ["C01"]})
    r["census"]["F1_unit"] = "H01"
    return r


def m13864_eb():
    r = m13864(EB)
    r["units_k"][2]["higher_is_better"] = False                        # COMET ru: against the lookup
    return r


def build_records():
    return {"x": {"M03416": m03416(EA), "M13864": m13864(EA)},
            "y": {"M03416": m03416_eb(), "M13864": m13864_eb()}}


BUILD = {("EA", "M03416"): lambda: m03416(EA), ("EA", "M13864"): lambda: m13864(EA),
         ("EB", "M03416"): m03416_eb, ("EB", "M13864"): m13864_eb}


# ------------------------------------------------------------------------------------------------ pipeline
def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _jsonl(p):
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def _write_lookups(d):
    d.mkdir(parents=True)
    with open(d / "benchmark-ids-v1.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([("printed", "id")] + BENCH)
    with open(d / "metric-ids-v1.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([("printed", "id", "higher_is_better")] + METRIC)
    return d


@pytest.fixture(scope="module")
def pipe(tmp_path_factory, ex_dispatch, agreement):
    for i in IDS:
        if not (TEXTS / f"{i}.txt").is_file():
            pytest.skip(f"full text {i}.txt not present (full texts are not in git)")
    assert _sha(TEXTS / "M03416.txt") == TEXT_SHA["M03416"]
    real_log_before = _sha(REAL_LOG) if REAL_LOG.exists() else None
    tmp = tmp_path_factory.mktemp("pipeline")
    lookups = _write_lookups(tmp / "lookups")
    man = synth.stage_a_manifest(["M13864"], [("M03416", "FR")])
    (tmp / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
    (tmp / "ids.txt").write_text("\n".join(IDS) + "\n", encoding="utf-8")
    log = tmp / "dispatch-log.jsonl"
    # 1. dispatch: E1 and E2 folders in tmp; the log goes to tmp through --log
    for role in ("E1", "E2"):
        assert ex_dispatch.main(["--role", role, "--batch", "pipe01", "--ids", str(tmp / "ids.txt"),
                                 "--root", str(tmp / "dispatch"), "--manifest", str(tmp / "manifest.json"),
                                 "--log", str(log)]) == 0
    folders = {d.name.split("-")[0]: d for d in (tmp / "dispatch").iterdir()}
    # 2. two synthetic records per id, written as each session's output file
    recs = {}
    for plan_role, d in folders.items():
        disp = json.loads((d / "dispatch.json").read_text(encoding="utf-8"))
        rows = []
        for i in disp["ids"]:
            r = BUILD[(plan_role, i)]()
            assert r["extractor"] == disp["extractor"]
            rows.append(r)
            recs[(plan_role, i)] = r
        synth.write_jsonl(d / disp["output_file"], rows)
    # 3. ex_validate, one record and its dispatched full text per call (the CLI takes one record)
    exits, reports = {}, []
    (tmp / "val").mkdir()
    for (plan_role, i), r in sorted(recs.items()):
        rp = tmp / "val" / f"{plan_role}-{i}.json"
        rp.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
        out = tmp / "val" / f"{plan_role}-{i}.report.jsonl"
        cp = subprocess.run([sys.executable, "-I", str(EXV), "--record", str(rp), "--text",
                             str(folders[plan_role] / "fulltext" / f"{i}.txt"), "--metric-lookup",
                             str(lookups / "metric-ids-v1.csv"), "--out", str(out)],
                            capture_output=True, text=True, encoding="utf-8")
        exits[(plan_role, i)] = cp.returncode
        reports += _jsonl(out)
    val = synth.write_jsonl(tmp / "validator.jsonl", reports)
    # 4. agreement, stage-a, without and with EC finals (EC = the EA records under an EC extractor string)
    xp = tmp / "x.jsonl"
    yp = tmp / "y.jsonl"
    synth.write_jsonl(xp, [recs[("EA", i)] for i in IDS])
    synth.write_jsonl(yp, [recs[("EB", i)] for i in IDS])
    ec = [dict(copy.deepcopy(recs[("EA", i)]), extractor="EC-claude-fable-5-1") for i in IDS]
    ecp = synth.write_jsonl(tmp / "ec.jsonl", ec)
    base = ["--mode", "stage-a", "--x", str(xp), "--y", str(yp), "--manifest", str(tmp / "manifest.json"),
            "--lookups", str(lookups), "--validator", str(val), "--config", str(CFG),
            "--texts", str(folders["EA"] / "fulltext"),
            "--we", str(ROOT / "analysis" / "extraction" / "we-expected.jsonl")]
    agreement.main(base + ["--out", str(tmp / "out")])
    agreement.main(base + ["--ec", str(ecp), "--out", str(tmp / "out-ec")])
    doc = json.loads((tmp / "out" / "agreement-stage-a.json").read_text(encoding="utf-8"))
    doc_ec = json.loads((tmp / "out-ec" / "agreement-stage-a.json").read_text(encoding="utf-8"))
    matches = {m["id"]: m for m in _jsonl(tmp / "out" / "matches-stage-a.jsonl")}
    return {"tmp": tmp, "folders": folders, "log": log, "real_log_before": real_log_before, "exits": exits,
            "reports": reports, "recs": recs, "doc": doc, "doc_ec": doc_ec, "matches": matches}


def _metric(doc, k):
    m = doc["metrics"][k]
    return m["numerator"], m["denominator"]


def test_dispatch_folders_and_log_stay_in_tmp(pipe):
    assert set(pipe["folders"]) == {"EA", "EB"}
    for d in pipe["folders"].values():
        assert pipe["tmp"] in d.parents
        for i in IDS:
            assert (d / "fulltext" / f"{i}.txt").read_bytes() == (TEXTS / f"{i}.txt").read_bytes()
    rows = _jsonl(pipe["log"])
    assert [r["role"] for r in rows] == ["EA", "EB"] and all(r["n"] == 2 for r in rows)
    assert (_sha(REAL_LOG) if REAL_LOG.exists() else None) == pipe["real_log_before"]


def test_records_follow_schema_v05(pipe):
    for (role, i), r in pipe["recs"].items():
        lines = [x for x in pipe["reports"] if x.get("id") == i and x.get("extractor") == r["extractor"]]
        assert any(x.get("check") == "schema" and x.get("severity") == "pass" for x in lines), (role, i)


def test_validator_findings_are_the_designed_ones(pipe):
    ex, rep = pipe["exits"], pipe["reports"]
    assert ex == {("EA", "M03416"): 0, ("EA", "M13864"): 0, ("EB", "M03416"): 1, ("EB", "M13864"): 1}
    fails = sorted((x["id"], x["extractor"][:2], x["check"], x["ref"]) for x in rep if x.get("severity") == "fail")
    assert fails == [("M03416", "EB", "row_start", "C04+C05"),
                     ("M13864", "EB", "sign_group", "K03"), ("M13864", "EB", "sign_group", "K04")]
    for ext in (EA, EB):
        unver = [x["ref"] for x in rep if x.get("status") == "column_unverified" and x["extractor"] == ext]
        assert sorted(unver) == ["H01"] + [f"K{j:02d}.A{k}" for j in range(1, 6) for k in (1, 2)]
        assert all(x["id"] == "M13864" for x in rep if x.get("status") == "column_unverified")
    summaries = [x for x in rep if x.get("summary")]
    assert len(summaries) == 4


def test_agreement_g1_counts_entry_failures_including_joined_row_refs(pipe):
    # EA: M03416 E01 T01 C01-C04, M13864 T01 C01 C02 -> 9 of 9; EB: M03416 E01 T01 C01-C05 (C04, C05 fail row_start
    # under the joined ref "C04+C05"), M13864 3 of 3 -> 8 of 10. Sign-group fails name units, not entries.
    assert _metric(pipe["doc"], "G1 accept EA") == (9.0, 9.0)
    assert _metric(pipe["doc"], "G1 accept EB") == (8.0, 10.0)


def test_agreement_unit_metrics(pipe):
    d = pipe["doc"]
    assert _metric(d, "G4 F1_G") == (4.0, 4.0)
    assert _metric(d, "G4 F1_H") == (4.0, 4.0)
    assert _metric(d, "G4 F1_K") == (14.0, 15.0)                  # 2 x (2 + 5) over (3 + 2) + (5 + 5)
    assert _metric(d, "G4 M-val") == (17.0, 17.0)                 # TF 3 shared arms, TB 4, M13864 10
    assert _metric(d, "G4 M-sign") == (3.0, 4.0)                  # acc, bleu, time agree; comet: EB holds two values
    # every K value of the two-level M13864 table is column_unverified in both readers: 20 of 39 K values
    assert _metric(d, "diag:column_unverified share (K values)") == (20.0, 39.0)
    assert d["stage_a"]["F1_G_drawn"] == 1.0 and d["stage_a"]["F1_G_worked_examples"] == 1.0
    assert d["stage_a"]["falsifier_F1_G_drawn_below_0.6"] is False


def test_h_match_uses_col_only_for_column_verified_cells(pipe):
    assert pipe["matches"]["M03416"]["h_units"]["matched"] == [["H01", "H01", "col"]]
    assert pipe["matches"]["M13864"]["h_units"]["matched"] == [["H01", "H01", "leaf"]]


def test_sign_coverage_mj1(pipe):
    s = pipe["doc"]["sign_coverage"]
    assert s["contrasts"] == 8                                    # M03416 K01, K02 pairs + K03 EA only; M13864 5 pairs
    assert s["final_from"] == {"KA1(a) printed arrow": 0, "lookup": 6, "EC": 0, "pending EC": 2, "unsigned": 0}
    assert s["routed_to_EC"] == 2 and s["final_null"] == 2
    assert s["routed_share"] == 0.25 and s["final_null_share"] == 0.25
    assert s["sign_agreement_both_given"] == {"agree": 6, "pairs": 7, "share": 6 / 7}
    assert s["extractor_KA1_steps"] == {"x": {"b": 7, "unverifiable": 1}, "y": {"b": 5, "unverifiable": 2}}
    assert s["redteam_MJ1_test"]["final_null_above_0.10"] is True
    assert s["redteam_MJ1_test"]["routed_above_0.30"] is False
    rows = {(r["id"], r["x_unit"]): r for r in pipe["matches"]["M13864"]["signs"]}
    assert rows[("M13864", "K03")]["source"] == "pending EC" and rows[("M13864", "K05")]["metric_key"] == "raw:time(sec.)"
    se = pipe["doc_ec"]["sign_coverage"]
    assert se["final_from"] == {"KA1(a) printed arrow": 0, "lookup": 6, "EC": 2, "pending EC": 0, "unsigned": 0}
    assert se["final_null"] == 0 and se["routed_to_EC"] == 2


def test_worked_example_comparison_reads_we_expected(pipe):
    # we-expected.jsonl (one row per unit) for M13864: 6 groups, 18 K units. The record's group (Table 2: Dream
    # rate=1, Qwen2.5-7B) matches WE G02 (arm Jaccard 2/3); its 5 units match G02's 5 on the parts WE gives.
    comp = pipe["doc"]["stage_a"]["worked_examples_comparison"]
    for side in ("EA", "EB"):
        assert comp[side]["matched_groups"] == 1
        assert comp[side]["F1_G"] == pytest.approx(2 / 7)
        assert comp[side]["F1_K"] == pytest.approx(10 / 23)
        assert comp[side]["anchor_agreement"] == 0.0              # WE G02 names no anchor; the records name A1


def test_ec_dispatch_takes_the_pipeline_records_and_lookups(pipe, ex_dispatch):
    # EC folder from the same X/Y files and lookup dir agreement.py read; the X/Y key stays in the tmp log
    tmp = pipe["tmp"]
    assert ex_dispatch.main(["--role", "EC", "--batch", "pipe01", "--ids", str(tmp / "ids.txt"), "--root",
                             str(tmp / "dispatch-ec"), "--records-x", str(tmp / "x.jsonl"), "--records-y",
                             str(tmp / "y.jsonl"), "--lookups", str(tmp / "lookups"), "--log", str(pipe["log"])]) == 0
    (d,) = list((tmp / "dispatch-ec").iterdir())
    row = _jsonl(pipe["log"])[-1]
    for i in IDS:
        pair = _jsonl(d / f"records-{i}.jsonl")
        assert [r["extractor"] for r in pair] == ["X", "Y"]
        for lab, r in zip("XY", pair):
            src = pipe["recs"][(row["xy"][i][lab], i)]
            assert dict(r, extractor=src["extractor"]) == src
    assert sorted(p.name for p in (d / "lookups").iterdir()) == ["benchmark-ids-v1.csv", "metric-ids-v1.csv"]
    assert (_sha(REAL_LOG) if REAL_LOG.exists() else None) == pipe["real_log_before"]
