"""Tests for the Stage A gap closures (analysis/extraction/stageA-gaps-log.txt): the shared sign rules of
tools/ex_validate.py and analysis/extraction/agreement.py (cross-tool), the draft lookups, the batch driver
tools/ex_validate_batch.py and the --self-test flags. Synthetic records and texts only; every write goes to a pytest
tmp folder."""
import copy
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ROOT = Path(__file__).resolve().parents[2]
LOOKUPS = ROOT / "analysis" / "extraction" / "lookups"
EV = load("ex_validate_gaps", ROOT / "tools" / "ex_validate.py")
BATCH = load("ex_validate_batch_gaps", ROOT / "tools" / "ex_validate_batch.py")
SCHEMA = json.loads(EV.DEFAULT_SCHEMA.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------------- self-test flags
@pytest.mark.parametrize("script", ["tools/ex_validate.py", "tools/ex_dispatch.py", "analysis/extraction/draw_pilot.py",
                                    "tools/ex_validate_batch.py"])
def test_self_test_flags_exit_zero(script):
    r = subprocess.run([sys.executable, "-I", str(ROOT / script), "--self-test"], capture_output=True, text=True,
                       encoding="utf-8", timeout=600)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    last = r.stdout.strip().splitlines()[-1]
    n, total = last.split()[-1].split("/")
    assert last.startswith("self-tests passed") and n == total and int(total) >= 10


def test_self_test_failure_gives_exit_one(monkeypatch):
    monkeypatch.setattr(EV, "self_test", lambda verbose=True: 1)
    assert EV.main(["--self-test"]) == 1
    with pytest.raises(SystemExit) as e:                    # neither --self-test nor --record/--text: usage error
        EV.main([])
    assert e.value.code == 2


# ---------------------------------------------------------------------------------------------- cross-tool signs
# (name, metric_printed, column_printed, col, hib, leaf arrows in columns, orientation, row label, expected
#  (routed, final sign)) -- expected values derived by hand from KA1, plan v0.5 s10.3 and agreement R3.
CASES = [
    ("qualifier, header arrow agrees", "Avg. acc", "Acc.", 1, True, False, "rows", None, (False, True)),
    ("qualifier, header arrow against the value", "Avg. acc", "Acc.", 1, False, False, "rows", None, (True, None)),
    ("top-1 qualifier, null value", "Top-1 accuracy", "Acc.", 1, None, False, "rows", None, (False, True)),
    ("pass@1 null value", "pass@1", "Cohesion", 3, None, False, "rows", None, (False, True)),
    ("pass@10 against the lookup", "pass@10", "Cohesion", 3, False, False, "rows", None, (True, None)),
    ("column arrow agrees", "FID", "FID ↓", 2, False, True, "rows", None, (False, False)),
    ("column arrow against the value (rejected, arrow sets the sign)", "FID", "FID ↓", 2, True, True, "rows", None, (False, False)),
    ("header arrow only, null value", "FID", "FID", 2, None, False, "rows", None, (False, False)),
    ("unmapped metric", "Cohesion", "Cohesion", 3, True, False, "rows", None, (True, None)),
    ("arrow in metric_printed", "Cohesion ↑", "Cohesion", 3, True, False, "rows", None, (False, True)),
    ("PPL null value, no arrow", "PPL", "Cohesion", 3, None, False, "rows", None, (False, False)),
    ("both arrows printed: ambiguous, lookup decides", "Acc. ↑", "FID ↓", 1, True, True, "rows", None, (False, True)),
    ("columns orientation: row-label arrow against the value", "Cohesion", "Cohesion", 3, True, False, "columns", "Base ↓", (False, False)),
    ("columns orientation: row-label arrow agrees", "Cohesion", "Cohesion", 3, False, False, "columns", "Base ↓", (False, False)),
    ("COMET from the draft lookup: no direction", "COMET", "Cohesion", 3, True, False, "rows", None, (True, None)),
]


def _case_record(metric, column, col, hib, leaf_arrows, orientation, row_label, extractor):
    cols = ("Acc. ↑", "FID ↓", "Cohesion") if leaf_arrows else ("Acc.", "FID", "Cohesion")
    rec = EV._st_sign_record([EV._st_kunit("K01", col, metric, column, hib)], cols)
    rec["extractor"] = extractor
    rec["groups"][0]["orientation"] = orientation
    if row_label:
        for c in rec["cell_evidence"]:
            c["row_label"] = row_label if c["id"] == "C01" else row_label.replace("Base", "Ours")
        rec["groups"][0]["arms"][0]["label_printed"] = row_label
        rec["groups"][0]["arms"][1]["label_printed"] = row_label.replace("Base", "Ours")
    return rec


@pytest.mark.parametrize("case", CASES, ids=[c[0] for c in CASES])
def test_cross_tool_same_sign(agreement, case):
    name, metric, column, col, hib, leaf_arrows, orientation, row_label, (exp_routed, exp_final) = case
    lk_path = LOOKUPS / "metric-ids-v1.csv"
    table = EV.load_metric_lookup(lk_path)
    rx = _case_record(metric, column, col, hib, leaf_arrows, orientation, row_label, "EA-claude-opus-5-5")
    ry = copy.deepcopy(rx)
    ry["extractor"] = "EB-claude-sonnet-5-5"
    # ex_validate (with text; its sign lines do not depend on the text)
    items = EV.validate_record(rx, EV.Text(EV._SIGN_LINES), SCHEMA, table)[0].items
    ev_routed = any(x["check"] == "sign_route" and x["ref"] == "K01" for x in items)
    # agreement (records only, same lookup folder)
    L = agreement.Lookups(LOOKUPS)
    gm, _, _ = agreement.group_match(rx["groups"], ry["groups"])
    km = agreement.match_k(rx, ry, gm, L)
    rows = agreement.sign_rows(rx, ry, gm, km, L, None)
    assert len(rows) == 1 and rows[0]["kind"] == "pair", rows
    row = rows[0]
    assert row["metric_key"] == EV.metric_key(metric, table), "one metric key in both tools"
    assert L.mdir(row["metric_key"]) == (EV.metric_lookup(metric, table) or (None, None))[1], "one direction list"
    assert ev_routed == row["routed_to_EC"] == exp_routed, (name, items)
    assert row["final"] == exp_final, (name, row)
    if not exp_routed and hib is not None and not any(x["status"] == "arrow_conflict" for x in items):
        assert row["final"] == hib


def test_cross_tool_group_key_and_conflict(agreement):
    """'Avg. acc' and 'Acc.' share one metric key in both tools: ex_validate rejects two directions in one group,
    and agreement scores the two units under one M-sign decision key."""
    table = EV.load_metric_lookup(LOOKUPS / "metric-ids-v1.csv")
    L = agreement.Lookups(LOOKUPS)
    assert EV.metric_key("Avg. acc", table) == EV.metric_key("Acc.", table) == L.mkey("Avg. acc") == L.mkey("Acc.") == "accuracy"
    u1 = EV._st_kunit("K01", 1, "Avg. acc", "Acc.", True)
    u2 = dict(EV._st_kunit("K02", 1, "Acc.", "Acc.", False), benchmark_printed="toy-2")
    rec = EV._st_sign_record([u1, u2], ("Acc.", "FID", "Cohesion"))
    items = EV.validate_record(rec, EV.Text(EV._SIGN_LINES), SCHEMA, table)[0].items
    assert [x["status"] for x in items if x["check"] == "sign_group"] == ["sign_conflict_in_group"] * 2


def test_record_arrows_equal_check_signs_inputs():
    rec = _case_record("FID", "FID", 2, True, False, "rows", None, "EA-x")
    rep, infos, cells = EV.check_evidence(EV.Text(EV._SIGN_LINES), rec["table_evidence"], rec["cell_evidence"], [], [])
    _, signs = EV.record_values(rec)
    assert EV.record_arrows(rec) == {("K", 0): EV.unit_arrows(signs[0], infos, cells)} == {("K", 0): (set(), {"down"})}


# ---------------------------------------------------------------------------------------------- draft lookups
def _rows(name):
    with open(LOOKUPS / name, encoding="utf-8", newline="") as f:
        return list(csv.reader(f))


def test_lookup_drafts_format_and_readers(agreement):
    m, b = _rows("metric-ids-v1.csv"), _rows("benchmark-ids-v1.csv")
    assert m[0] == ["printed", "id", "higher_is_better"] and b[0] == ["printed", "id"]
    assert not any(r[0].startswith("#") for r in m + b), "no comment rows"
    assert all(r[2] in ("true", "false", "") for r in m[1:])
    L = agreement.Lookups(LOOKUPS)                       # agreement accepts both files
    table = EV.load_metric_lookup(LOOKUPS / "metric-ids-v1.csv")
    assert L.mtable == table
    keys = {EV.metric_norm(r[0]) for r in m[1:]}
    ka1 = EV.ka1_table()
    assert set(ka1) <= keys and all(table[k] == v for k, v in ka1.items()), "built-in KA1(b) list adds nothing"
    directed = {EV.metric_norm(r[0]) for r in m[1:] if r[2]}
    assert directed == set(ka1) | {"pass@k"}, "directions only for KA1(b) names (plan v0.5 s5.4)"
    assert (LOOKUPS / "README.md").read_text(encoding="utf-8").startswith("# Lookups v1: DRAFT for Stage A")


def test_lookup_drafts_cover_worked_example_names():
    we = [json.loads(l) for l in (ROOT / "analysis/extraction/we-expected.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    table = EV.load_metric_lookup(LOOKUPS / "metric-ids-v1.csv")
    bench = {EV.metric_norm(r[0]) for r in _rows("benchmark-ids-v1.csv")[1:]}
    unmapped_by_design = {"average", "corpus", "fairness", "fairnessbenchmark", "privacy", "privacybenchmark"}
    for r in we:
        if r.get("metric"):
            assert EV.metric_lookup(r["metric"], table) is not None, r["metric"]
        if r.get("benchmark"):
            assert EV.metric_norm(r["benchmark"]) in bench | unmapped_by_design, r["benchmark"]


@pytest.mark.parametrize("bad", ["printed,id,higher_is_better\nscore,score,yes\n", "# v1 draft\nprinted,id,higher_is_better\n",
                                 "printed,id,higher_is_better\n# note,x,\n", "printed,id,higher_is_better\nPPL,perplexity,true\n"])
def test_lookup_readers_refuse_bad_files(agreement, tmp_path, bad):
    (tmp_path / "metric-ids-v1.csv").write_text(bad, encoding="utf-8")
    (tmp_path / "benchmark-ids-v1.csv").write_text("printed,id\n", encoding="utf-8")
    with pytest.raises(ValueError):
        EV.load_metric_lookup(tmp_path / "metric-ids-v1.csv")
    with pytest.raises(SystemExit):
        agreement.Lookups(tmp_path)
    rec = tmp_path / "r.json"
    rec.write_text(json.dumps(EV._st_sign_record([])), encoding="utf-8")
    txt = tmp_path / "t.txt"
    txt.write_text("\n".join(EV._SIGN_LINES), encoding="utf-8")
    assert EV.main(["--record", str(rec), "--text", str(txt), "--metric-lookup", str(tmp_path / "metric-ids-v1.csv")]) == 2


# ---------------------------------------------------------------------------------------------- batch driver
@pytest.fixture()
def sessions(tmp_path, ex_dispatch):
    """EA and EB dispatch folders made by ex_dispatch on synthetic texts, with extractor outputs."""
    texts = tmp_path / "texts"
    texts.mkdir()
    for i in ("S00001", "S00002"):
        (texts / f"{i}.txt").write_text("\n".join(EV._SIGN_LINES) + "\n", encoding="utf-8")
    ids = tmp_path / "ids.txt"
    ids.write_text("S00001\nS00002\n", encoding="utf-8")
    folders = {}
    for role, plan_role, ext in (("E1", "EA", "EA-claude-opus-5-5"), ("E2", "EB", "EB-claude-sonnet-5-5")):
        d = ex_dispatch.build(type("A", (), dict(role=role, batch="g1", ids=str(ids), root=str(tmp_path / "root"),
                                                 blocks="K", blocks_json=None, manifest=None, records_x=None, records_y=None,
                                                 lookups=None, texts=str(texts), log=str(tmp_path / "log.jsonl"),
                                                 dry_run=False))())
        recs = []
        for i, hib in (("S00001", True), ("S00002", plan_role == "EB")):          # EA S00002: arrow conflict
            r = EV._st_sign_record([EV._st_kunit("K01", 1, "Acc.", "Acc. ↑", hib)])
            r.update(id=i, extractor=ext)
            recs.append(r)
        (d / f"{plan_role}-g1.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), encoding="utf-8")
        folders[plan_role] = d
    return folders


def test_batch_report_feeds_agreement(agreement, sessions, tmp_path):
    out = tmp_path / "validator.jsonl"
    code = BATCH.main(["--session", str(sessions["EA"]), "--session", str(sessions["EB"]), "--lookups", str(LOOKUPS),
                       "--out", str(out)])
    assert code == 1                                                        # EA S00002 is rejected
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()]
    summ = {(r["id"], r["extractor"]): r for r in rows if r.get("summary")}
    assert set(summ) == {(i, e) for i in ("S00001", "S00002") for e in ("EA-claude-opus-5-5", "EB-claude-sonnet-5-5")}
    assert summ[("S00002", "EA-claude-opus-5-5")]["status"] == "rejected" and summ[("S00001", "EB-claude-sonnet-5-5")]["status"] == "accepted"
    assert all(r["pass"] == 1 for r in rows) and all(r["metric_lookup_sha256"] for r in summ.values())
    assert all(any(r.get("check") == "blocks" and r["status"] == "pass" and r["id"] == i for r in rows) for i in ("S00001", "S00002"))
    val = agreement.Validator(out)
    assert set(summ) <= val.seen and "K01" in val.fails[("S00002", "EA-claude-opus-5-5")]
    fails_before = copy.deepcopy(dict(val.fails))
    # the one return: EA fixes S00002; the re-run is appended as pass 2 and agreement keeps the first pass
    r = EV._st_sign_record([EV._st_kunit("K01", 1, "Acc.", "Acc. ↑", True)])
    r.update(id="S00002", extractor="EA-claude-opus-5-5")
    first = json.loads((sessions["EA"] / "EA-g1.jsonl").read_text(encoding="utf-8").splitlines()[0])
    (sessions["EA"] / "EA-g1.jsonl").write_text(json.dumps(first) + "\n" + json.dumps(r) + "\n", encoding="utf-8")
    assert BATCH.main(["--session", str(sessions["EA"]), "--lookups", str(LOOKUPS), "--out", str(out), "--append", "--pass", "2"]) == 0
    rows2 = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()]
    assert rows2[:len(rows)] == rows and {x["pass"] for x in rows2[len(rows):]} == {2}
    assert dict(agreement.Validator(out).fails) == fails_before
    with pytest.raises(SystemExit):                                         # no second return
        BATCH.main(["--session", str(sessions["EA"]), "--lookups", str(LOOKUPS), "--out", str(out), "--append", "--pass", "2"])


def test_batch_blocks_and_extractor_checked(sessions, tmp_path):
    p = sessions["EB"] / "EB-g1.jsonl"
    recs = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()]
    recs[0]["blocks"] = ["H", "K"]
    recs[1]["extractor"] = "EB-other-model"
    p.write_text("".join(json.dumps(r) + "\n" for r in recs), encoding="utf-8")
    out = tmp_path / "v.jsonl"
    assert BATCH.main(["--session", str(sessions["EB"]), "--lookups", str(LOOKUPS), "--out", str(out)]) == 1
    rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()]
    st = {(r["id"], r.get("check"), r.get("status")) for r in rows}
    assert ("S00001", "blocks", "blocks_mismatch") in st and ("S00002", "session", "extractor_mismatch") in st


def test_batch_refuses_bad_inputs_and_writes_nothing(sessions, tmp_path):
    out = tmp_path / "v.jsonl"
    bad_lk = tmp_path / "lk"
    bad_lk.mkdir()
    (bad_lk / "metric-ids-v1.csv").write_text("printed,id,higher_is_better\nFID,fid,true\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        BATCH.main(["--session", str(sessions["EA"]), "--lookups", str(bad_lk), "--out", str(out)])
    schema_copy = next(sessions["EA"].glob("extraction-schema-*.json"))
    schema_copy.write_bytes(schema_copy.read_bytes() + b" ")
    with pytest.raises(SystemExit):
        BATCH.main(["--session", str(sessions["EA"]), "--lookups", str(LOOKUPS), "--out", str(out)])
    assert not out.exists()
