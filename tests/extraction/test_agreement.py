"""Tests of analysis/extraction/agreement.py on synthetic records (plan v0.5 s11; s14 A7 and B3)."""
import copy
import csv
import hashlib
import json
import random
from pathlib import Path

import pytest

import ex_synth as synth

ROOT = Path(__file__).resolve().parents[2]
EXTR = ROOT / "analysis" / "extraction"
CFG = EXTR / "gate-config-v05.json"
GRID = EXTR / "bip-grid-v2.json"
CFG_SHA = hashlib.sha256(CFG.read_bytes()).hexdigest()
WE = ["W0001", "W0002", "W0003", "W0004", "W0005"]
DRAWN = [("D0001", "C1-ab"), ("D0002", "C1-b"), ("D0003", "C2"), ("D0004", "C2"), ("D0005", "FR-bench"),
         ("D0006", "FRC2-large"), ("D0007", "FR")]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write_inputs(tmp, ids, p=0.25, seed=5, manifest=None, extra_x=None):
    rng = random.Random(seed)
    xs, ys = [], []
    for i in ids:
        x, _ = synth.pair(i)
        y = synth.perturb(x, rng, p)
        y["extractor"] = "EB-claude-sonnet-5-5"
        xs.append(x)
        ys.append(y)
    if extra_x:
        xs += extra_x
    d = {"x": synth.write_jsonl(tmp / "x.jsonl", xs), "y": synth.write_jsonl(tmp / "y.jsonl", ys),
         "val": synth.write_jsonl(tmp / "val.jsonl", synth.validator_lines(xs + ys)),
         "lookups": synth.write_lookups(tmp / "lookups")}
    if manifest is not None:
        d["manifest"] = tmp / "manifest.json"
        d["manifest"].write_text(json.dumps(manifest), encoding="utf-8")
    return d, xs, ys


def argv(mode, d, out, *extra):
    a = ["--mode", mode, "--x", str(d["x"]), "--y", str(d["y"]), "--manifest", str(d["manifest"]),
         "--lookups", str(d["lookups"]), "--validator", str(d["val"]), "--config", str(CFG), "--out", str(out)]
    if mode != "stage-a":
        a += ["--grid", str(GRID), "--expect-config", CFG_SHA]
    return a + list(extra)


@pytest.fixture(scope="module")
def stage_a_run(tmp_path_factory, agreement):
    tmp = tmp_path_factory.mktemp("stagea")
    man = synth.stage_a_manifest(WE, DRAWN)
    d, xs, ys = write_inputs(tmp, man["ids"], manifest=man)
    we = [{"id": i, "groups": [{"group_id": "G01", "where": "Table 2", "second_factor_printed": "", "anchor_arm": "A1",
                                "arms": [{"arm_id": "A1", "label_printed": "Model-Z"},
                                         {"arm_id": "A2", "label_printed": "Model-Z (16 steps)"},
                                         {"arm_id": "A3", "label_printed": "Model-Z (8 steps)"}]}],
           "units_k": [{"unit_id": "K01", "group_id": "G01", "benchmark_printed": "Bench-A", "metric_printed": "Acc",
                        "condition_printed": "", "split": "test"}]} for i in WE]
    wep = synth.write_jsonl(tmp / "we.jsonl", we)
    out = tmp / "out"
    agreement.main(argv("stage-a", d, out, "--we", str(wep)))
    return tmp, d, out, json.loads((out / "agreement-stage-a.json").read_text(encoding="utf-8"))


def test_self_test_passes(agreement):
    ok, n, _ = agreement.self_test(verbose=False)
    assert ok == n and n >= 19


def test_stage_a_outputs(stage_a_run):
    tmp, d, out, doc = stage_a_run
    for f in ("agreement-stage-a.json", "per-record-stage-a.csv", "matches-stage-a.jsonl", "we-comparison.md",
              "run-stage-a.log"):
        assert (out / f).exists(), f
    assert doc["n_records"] == 12 and doc["strata"]["WE"] == 5
    for k in ("G4 F1_G", "G4 F1_K", "G4 M-val", "G4 M-anchorG", "G4 M-pool", "G4 M-sign", "G3 K-attr", "G3 QA kappa"):
        assert k in doc["metrics"]
    m = doc["metrics"]["G4 F1_G"]
    assert m["LB90"] <= m["point"] <= 1.0
    # ICC block: 20 metrics with the 80 and 50 percent bounds on all 12 and on the 7 drawn, plus the v0.4 pooled value
    for lab, n in (("all", 12), ("drawn", 7)):
        blk = doc["icc"][lab]
        assert blk["records"] == n and len(blk["per_metric"]) == 20
        assert all("U80" in v and "U50" in v and v["U50"] <= v["U80"] + 1e-12 for v in blk["per_metric"].values())
        assert "U_N" in blk["v04_pooled"]
    s = doc["stage_a"]
    assert s["drawn"] == [i for i, _ in DRAWN] and s["worked_examples"] == WE
    assert set(s["worked_examples_comparison"]) == {"EA", "EB"}
    assert s["worked_examples_comparison"]["EA"]["F1_G"] == pytest.approx(2 * 5 / (10 + 5))
    assert isinstance(s["falsifier_F1_G_drawn_below_0.6"], bool)


def test_stage_a_sign_coverage_mj1(stage_a_run):
    doc = stage_a_run[3]
    sc = doc["sign_coverage"]
    assert sum(sc["final_from"].values()) == sc["contrasts"] > 0
    assert sc["final_null"] == sc["final_from"]["pending EC"] + sc["final_from"]["unsigned"]
    assert 0 <= sc["routed_share"] <= 1 and sc["sign_agreement_both_given"]["pairs"] > 0
    # no arrow in the synthetic strings; Acc and PPL are in the lookup: every contrast is signed by the lookup unless an
    # extractor value conflicts with it
    assert sc["final_from"]["KA1(a) printed arrow"] == 0 and sc["final_from"]["lookup"] > 0


def test_stage_a_pooling_matches_per_record_csv(stage_a_run):
    out, doc = stage_a_run[2], stage_a_run[3]
    tot = {}
    with open(out / "per-record-stage-a.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["metric"].startswith("G4 M-val"):
                tot.setdefault("n", 0.0)
                tot.setdefault("d", 0.0)
                tot["n"] += float(row["numerator"])
                tot["d"] += float(row["denominator"])
    assert tot["n"] == doc["metrics"]["G4 M-val"]["numerator"] and tot["d"] == doc["metrics"]["G4 M-val"]["denominator"]


def test_parameters_and_inputs_hashed(stage_a_run, agreement):
    tmp, d, out, doc = stage_a_run
    assert doc["parameters_sha256"] == agreement.sha_obj(doc["parameters"])
    assert doc["inputs_sha256"]["x"] == sha(d["x"]) and doc["inputs_sha256"]["config"] == CFG_SHA
    assert doc["seeds"] == {"boot": 20261800, "icc": 20264900}
    assert doc["inputs_sha256"]["agreement.py"] == sha(EXTR / "agreement.py")


def test_deterministic(stage_a_run, agreement, tmp_path):
    tmp, d, out, doc = stage_a_run
    out2 = tmp_path / "again"
    agreement.main(argv("stage-a", d, out2, "--we", str(tmp / "we.jsonl")))
    assert (out2 / "agreement-stage-a.json").read_bytes() == (out / "agreement-stage-a.json").read_bytes()


def test_identical_records_give_one(agreement, tmp_path):
    man = synth.stage_a_manifest(WE, DRAWN)
    d, xs, ys = write_inputs(tmp_path, man["ids"], p=0.0, manifest=man)
    agreement.main(argv("stage-a", d, tmp_path / "o"))
    doc = json.loads((tmp_path / "o" / "agreement-stage-a.json").read_text(encoding="utf-8"))
    for k in agreement.METRICS_RATIO:
        assert doc["metrics"][k]["point"] == 1.0 and doc["metrics"][k]["LB90"] == 1.0, k
    assert doc["metrics"]["G5 anchors"]["count"] == 12


@pytest.mark.parametrize("case", ["id_not_in_manifest", "missing_validator_line", "output_exists", "missing_lookup"])
def test_refusals_write_nothing(agreement, tmp_path, case):
    man = synth.stage_a_manifest(WE, DRAWN)
    extra = [synth.base_record("Z9999")] if case == "id_not_in_manifest" else None
    d, xs, ys = write_inputs(tmp_path, man["ids"], manifest=man, extra_x=extra)
    out = tmp_path / "o"
    if case == "missing_validator_line":
        synth.write_jsonl(d["val"], synth.validator_lines(xs + ys[1:]))
    if case == "output_exists":
        out.mkdir()
        (out / "agreement-stage-a.json").write_text("{}", encoding="utf-8")
    if case == "missing_lookup":
        (d["lookups"] / "metric-ids-v1.csv").unlink()
    with pytest.raises(SystemExit):
        agreement.main(argv("stage-a", d, out))
    left = sorted(p.name for p in out.glob("*")) if out.exists() else []
    assert left == (["agreement-stage-a.json"] if case == "output_exists" else [])


def _gate_inputs(tmp, man, ids, p=0.15, seed=11):
    d, xs, ys = write_inputs(tmp, ids, p=p, seed=seed, manifest=man)
    return d


def test_gate_phase1_output_restricted(agreement, tmp_path):
    man = synth.gate_manifest()
    ids = [i for s in man["strata_order"] for i in man["lists"][s][:20]]
    d = _gate_inputs(tmp_path, man, ids)
    out = tmp_path / "p1"
    agreement.main(argv("gate-phase1", d, out))
    assert sorted(p.name for p in out.iterdir()) == ["agreement-gate-phase1.json", "run-gate-phase1.log"]
    doc = json.loads((out / "agreement-gate-phase1.json").read_text(encoding="utf-8"))
    assert set(doc) == {"tool", "mode", "U_m", "P_hat", "n", "step6", "inputs_sha256", "seeds", "parameters",
                        "parameters_sha256", "n_records"}
    assert len(doc["U_m"]) == 20 and doc["n"] in (60, 72, 90, 105, 120) and doc["n_records"] == 60
    assert doc["seeds"]["icc"] == 20264901 and set(doc["P_hat"]) == {"60", "72", "90", "105", "120"}
    # the decision equals gate_rule_v05 applied to the reported bounds
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    grid = json.loads(GRID.read_text(encoding="utf-8"))
    n, P, step6 = agreement.GR.n_product(agreement.GR.theta_by_criterion(doc["U_m"], cfg, grid), cfg, grid)
    assert (n, step6) == (doc["n"], doc["step6"])


def test_gate_phase1_uses_only_phase1_ids_and_replacements(agreement, tmp_path):
    man = synth.gate_manifest()
    ids = [i for s in man["strata_order"] for i in man["lists"][s][:25]] + [man["spares"]["G-short"][0]]
    d = _gate_inputs(tmp_path, man, ids)
    repl = synth.write_jsonl(tmp_path / "repl.jsonl", [{"stratum": "G-short", "failed": man["lists"]["G-short"][3],
                                                        "replacement": man["spares"]["G-short"][0]}])
    agreement.main(argv("gate-phase1", d, tmp_path / "p1", "--replacements", str(repl)))
    doc = json.loads((tmp_path / "p1" / "agreement-gate-phase1.json").read_text(encoding="utf-8"))
    assert doc["n_records"] == 60
    bad = synth.write_jsonl(tmp_path / "bad.jsonl", [{"stratum": "G-short", "failed": man["lists"]["G-short"][3],
                                                      "replacement": man["lists"]["G-short"][30]}])
    with pytest.raises(SystemExit):
        agreement.main(argv("gate-phase1", d, tmp_path / "p2", "--replacements", str(bad)))


def test_gate_refuses_wrong_config_and_grid(agreement, tmp_path):
    man = synth.gate_manifest()
    ids = [i for s in man["strata_order"] for i in man["lists"][s][:20]]
    d = _gate_inputs(tmp_path, man, ids)
    a = argv("gate-phase1", d, tmp_path / "o")
    a[a.index("--expect-config") + 1] = "0" * 64
    with pytest.raises(SystemExit):
        agreement.main(a)
    g = json.loads(GRID.read_text(encoding="utf-8"))
    g["model_sha256"] = "f" * 64
    bad = tmp_path / "grid.json"
    bad.write_text(json.dumps(g), encoding="utf-8")
    a = argv("gate-phase1", d, tmp_path / "o")
    a[a.index("--grid") + 1] = str(bad)
    with pytest.raises(SystemExit):
        agreement.main(a)
    a = argv("gate-phase1", d, tmp_path / "o")
    i = a.index("--expect-config")
    del a[i:i + 2]
    with pytest.raises(SystemExit):
        agreement.main(a)
    assert not (tmp_path / "o").exists()


def _sub(tmp, name):
    p = tmp / name
    p.mkdir()
    return p


def test_gate_full_run_and_verdict(agreement, tmp_path):
    man = synth.gate_manifest()
    ids1 = [i for s in man["strata_order"] for i in man["lists"][s][:20]]
    d = _gate_inputs(_sub(tmp_path, "a"), man, ids1)
    agreement.main(argv("gate-phase1", d, tmp_path / "p1"))
    ph = tmp_path / "p1" / "agreement-gate-phase1.json"
    n = json.loads(ph.read_text(encoding="utf-8"))["n"]
    ids = [i for s in man["strata_order"] for i in man["lists"][s][:n // 3]]
    d2 = _gate_inputs(_sub(tmp_path, "b"), man, ids)
    agreement.main(argv("gate", d2, tmp_path / "g", "--phase1", str(ph)))
    doc = json.loads((tmp_path / "g" / "agreement-gate.json").read_text(encoding="utf-8"))
    v = doc["verdict"]
    assert v["n"] == n and v["decision"] in ("PASS", "FAIL")
    gated = [r for r in v["rows"] if r["gated"]]
    assert len(gated) == 18 and (v["decision"] == "PASS") == all(r["pass"] for r in gated)
    ro = {r["criterion"] for r in v["rows"] if not r["gated"]}
    assert ro == {"G4 M-sign", "D credited_ablation alone"}
    g5 = next(r for r in v["rows"] if r["criterion"] == "G5 anchors")
    assert g5["line"].endswith(str(agreement.c_min(n, 0.60)))
    assert (tmp_path / "g" / "verdict-table.md").read_text(encoding="utf-8").startswith("# Gate verdict")
    # wrong record set for that n: refused
    ids_bad = ids[:-1] + [man["lists"]["G-mm"][39]]
    d3 = _gate_inputs(_sub(tmp_path, "c"), man, ids_bad)
    with pytest.raises(SystemExit):
        agreement.main(argv("gate", d3, tmp_path / "g2", "--phase1", str(ph)))


def test_h_two_pass_matching(agreement, tmp_path):
    """v0.5 s5.2: column-verified cells match on col; unverified cells fall back to the leaf parts."""
    L = agreement.Lookups(synth.write_lookups(tmp_path / "lk"))
    # same col, different leaf: both cells verified -> matched on col in pass 1
    x, y = synth.pair("M90002")
    y["units_h"][1]["column_printed"] = "Bench-B / PPL"
    v1 = agreement.Validator(synth.write_jsonl(tmp_path / "v1.jsonl", synth.validator_lines([x, y])))
    r = agreement.compare(x, y, L, v1, None)
    assert r["nd"]["G4 F1_H"] == [4.0, 4.0]
    assert sorted(m[2] for m in r["matches"]["h_units"]["matched"]) == ["col", "key"]
    # the same pair with Y's cell column-unverified -> pass 2 by leaf parts, which differ -> no match
    v2 = agreement.Validator(synth.write_jsonl(tmp_path / "v2.jsonl", synth.validator_lines(
        [x, y], unverified=[("M90002", y["extractor"], "C01")])))
    assert agreement.compare(x, y, L, v2, None)["nd"]["G4 F1_H"] == [2.0, 4.0]
    # different col, same leaf, verified: no col match, then matched by leaf in pass 2
    x3, y3 = synth.pair("M90003")
    y3["units_h"][1]["col"] = 2
    v3 = agreement.Validator(synth.write_jsonl(tmp_path / "v3.jsonl", synth.validator_lines([x3, y3])))
    r3 = agreement.compare(x3, y3, L, v3, None)
    assert r3["nd"]["G4 F1_H"] == [4.0, 4.0]
    assert sorted(m[2] for m in r3["matches"]["h_units"]["matched"]) == ["key", "leaf"]


def test_first_pass_acceptance(agreement, tmp_path):
    x, y = synth.pair("M90004")
    L = agreement.Lookups(synth.write_lookups(tmp_path / "lk"))
    lines = synth.validator_lines([x, y], fails=[("M90004", x["extractor"], "C02"), ("M90004", x["extractor"], "E01")])
    lines.append({"id": "M90004", "extractor": x["extractor"], "check": "value_mismatch", "ref": "C03", "status": "fail",
                  "severity": "fail", "pass": 2})
    v = agreement.Validator(synth.write_jsonl(tmp_path / "v.jsonl", lines))
    r = agreement.compare(x, y, L, v, None)
    assert r["nd"]["G1 accept EA"] == [6.0, 8.0] and r["nd"]["G1 accept EB"] == [8.0, 8.0]


def test_abstract_offset_key_with_texts(agreement, tmp_path):
    x, y = synth.pair("M90005")
    y["evidence"][0]["quote"] = "reaches 41.7 on the synthetic Bench-A test set"   # shorter quote, same number
    L = agreement.Lookups(synth.write_lookups(tmp_path / "lk"))
    v = agreement.Validator(synth.write_jsonl(tmp_path / "v.jsonl", synth.validator_lines([x, y])))
    r0 = agreement.compare(x, y, L, v, None)
    texts = {"M90005": agreement.QC.normalise("Abstract. Model-Z reaches 41.7 on the synthetic Bench-A test set.")}
    r1 = agreement.compare(x, y, L, v, texts)
    assert r0["nd"]["G4 F1_H"] == [2.0, 4.0] and r1["nd"]["G4 F1_H"] == [4.0, 4.0]


def test_normalisation(agreement):
    n = agreement.norm_label
    assert n("Model-Z (ours)") == n("Model-Z") == "model-z"
    assert n("LLM-Q [Doe et al., 2023]") == "llm-q" and n("Model-Z†") == "model-z"
    assert agreement.norm_bm("(Acc ↑)") == "acc" and agreement.norm_bm("Bench A (Doe, 2021)") == "bencha"
    assert agreement.lenient("raw:bench-q-v2") == agreement.lenient("raw:benchq")


def test_synthetic_records_follow_schema_v05():
    """The fixtures are schema-shaped: base records and perturbed second readers validate against schema v0.5."""
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((ROOT / "research/review/extraction/extraction-schema-v0.5.json").read_text(encoding="utf-8"))
    v = jsonschema.Draft202012Validator(schema)
    rng = random.Random(1)
    x, y = synth.pair("M90009")
    recs = [x, y] + [synth.perturb(x, rng, 0.5) for _ in range(20)]
    errs = [e.message for r in recs for e in v.iter_errors(r)]
    assert errs == []


def test_qa_kappa_and_flags(agreement):
    c = [0] * 9
    c[0], c[4], c[8] = 4, 3, 3
    assert agreement.wkappa(c) == pytest.approx(1.0)
    assert agreement.flag_line(15) == 8 and agreement.flag_line(60) == 43 and agreement.flag_line(10) is None
    k, ac1 = agreement.cat_kappa([("a", "a"), ("b", "b"), ("a", "b"), ("b", "b")])
    assert k == pytest.approx(0.5) and ac1 is not None
