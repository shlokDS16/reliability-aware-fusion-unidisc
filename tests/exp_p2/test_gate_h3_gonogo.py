"""H3 go/no-go module (exp_p2/gate/h3_gonogo.py, SAP addendum A5.5 and A5.5a): every branch of the rule (R1, R2, NO-GO, pilot incomplete, time cut, n = 200), the bound examples, the
absence of any signed GATE-M quantity in the output, invariance to the gate arm outside the unsigned indicator, write-once files, and that run_gate_m4 / analysis_m4 read the written file.
CPU only; synthetic rows in a temp directory."""
import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exp_p2 import common, run_gate_m4                                       # noqa: E402
from exp_p2.gate import analysis_m4, artifacts, build_hardneg_items as bh, config, h3_gonogo as g, runner      # noqa: E402

EARLY = "2026-10-30T09:00:00+05:30"
KEYS = {"jpeg": ("jpeg", 10, "jpeg10"), "noise": ("noise", 0.1, "noise0.1"), "splice": ("splice", 128, "splice128")}


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    monkeypatch.setattr(runner, "_cuda", lambda: None)
    m3 = tmp_path / "P2-GATE-M3"
    m3.mkdir()
    (m3 / "family.json").write_text(json.dumps(dict(endpoint="d", endpoint_note="z* = sqrt(m) * d", n_rule=dict(rule="R2", test_fold=500), rungs={"x": 1}, family=[
        dict(corruption=c, severity=s, key=k, D_c=7) for c, s, k in KEYS.values()])))
    head = [dict(idx=i, gid=6000 + i, image_id=9000 + i, caption=f"a cat {i} sits here", n_tok=5, neg_caption=f"a dog {i} sits here", subset="add_att") for i in range(50)]
    test = [dict(idx=i, gid=7000 + i, image_id=9500 + i, caption=f"a cat {i} sits there", n_tok=5, neg_caption=f"a dog {i} sits there", subset="add_att") for i in range(300)]
    d = tmp_path / "P2-HARDNEG-ITEMS"
    d.mkdir()
    (d / "folds_hardneg.json").write_text(json.dumps(dict(meta={}, cal=[], head=head, test=test, test_ext=[])))
    return tmp_path


def _row(i, yc, per):
    conds = {"clean": {"img": {"none": {"y": yc}, "gate0.05": {"y": yc}}}}
    for k, (yn, yg, ych) in per.items():
        conds[k] = {"img": {"none": {"y": yn}, "gate0.05": {"y": yg}, "chg": {"y": ych}}}
    return dict(idx=i, gid=6000 + i, image_id=9000 + i, conds=conds)


def _rows(spec, n=50, yg_noise=None, invalid=()):
    """spec: corruption -> dict(fm=F-, fp=F+, g=G). Items 0..fm-1 have clean right / none wrong (F-); items 40..40+fp-1 have clean wrong / none right (F+); the first g items have yg != yn.
    `invalid` item indices get yc = NaN (so they are not valid for any corruption); `yg_noise` sets yg on those items."""
    rows = []
    nan = float("nan")
    fp_max = max([s["fp"] for s in spec.values()] + [0])
    for i in range(n):
        yc = 0.0 if 40 <= i < 40 + fp_max else 1.0
        per = {}
        for c, (_, _, k) in KEYS.items():
            s = spec.get(c, dict(fm=0, fp=0, g=0))
            yn = 0.0 if i < s["fm"] else (1.0 if 40 <= i < 40 + s["fp"] else yc)
            yg = (1.0 - yn) if i < s["g"] else yn
            per[k] = (yn, yg, yn)
        if i in invalid:
            yc = nan
            per = {k: (v[0], yg_noise if yg_noise is not None else v[1], v[2]) for k, v in per.items()}
        rows.append(_row(i, yc, per))
    return rows


def _write_rows(env, rows, run="P2-GATE-H3"):
    d = env / run
    d.mkdir(exist_ok=True)
    (d / "items.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def _decide(env, spec, now=EARLY, **kw):
    g.plan(env)
    _write_rows(env, _rows(spec, **kw))
    code, doc = g.decide("P2-GATE-H3", g.parse_now(now), env)
    return code, doc


GO3 = dict(jpeg=dict(fm=3, fp=0, g=9), splice=dict(fm=2, fp=0, g=4))


# ------------------------------------------------------------------------------------------------ plan
def test_plan_writes_the_derived_h3_file_and_the_plan_family_and_prints_the_deadline(env):
    out = g.plan(env)
    h3 = json.loads(Path(out["h3_folds"]).read_text())
    hard = json.loads((env / "P2-HARDNEG-ITEMS" / "folds_hardneg.json").read_text())
    assert h3 == dict(cal=[], head=[], test=hard["head"], test_ext=[])                     # the H3 items verbatim under `test`
    fam = json.loads((env / "P2-GATE-H3-PLAN" / "family.json").read_text())
    assert fam["endpoint"] == "d" and fam["endpoint_note"] == "z* = sqrt(m) * d" and fam["excluded"] == [] and fam["go"] is True
    assert fam["family"] == [dict(corruption=c, severity=s, key=k) for c, s, k in KEYS.values()]       # corruption, severity, key only; M3's D_c dropped
    assert fam["n_rule"] == dict(rule="H3-pilot", test_fold=50, primary_endpoint="Y") and set(fam["source"]) == {"m3_family_sha256", "folds_hardneg_sha256"}
    assert datetime.fromisoformat(out["h3_start_deadline"]) == datetime(2026, 10, 30, 12, 27, tzinfo=g.IST)      # Fri 30 Oct 12:27 IST


def test_plan_refuses_to_overwrite_either_file_and_writes_nothing_then(env):
    g.plan(env)
    with pytest.raises(artifacts.WriteOnceError):
        g.plan(env)
    (env / "P2-GATE-H3-PLAN" / "family.json").unlink()
    h3 = env / "P2-HARDNEG-ITEMS" / "folds_hardneg_h3.json"
    before = h3.read_bytes()
    with pytest.raises(artifacts.WriteOnceError):
        g.plan(env)
    assert h3.read_bytes() == before and not (env / "P2-GATE-H3-PLAN" / "family.json").exists()


def test_plan_needs_the_three_m3_corruptions_and_the_50_h3_items(env):
    p = env / "P2-GATE-M3" / "family.json"
    d = json.loads(p.read_text())
    d["family"] = d["family"][:2]
    p.write_text(json.dumps(d))
    with pytest.raises(ValueError, match="three corruptions"):
        g.plan(env)


# ------------------------------------------------------------------------------------------------ the rule
def test_bound_examples_of_a5_5():
    assert g.bound_p(2, 0) == pytest.approx(0.0005, abs=1e-4) and g.bound_p(2, 0) <= g.ALPHA_STEP1                  # (2, 0) passes
    assert g.bound_p(3, 1) == pytest.approx(0.0227, abs=1e-3) and g.bound_p(3, 1) > g.ALPHA_STEP1                  # (3, 1) fails
    assert g.bound_p(4, 1) == pytest.approx(0.00143, abs=1e-4) and g.bound_p(4, 1) <= g.ALPHA_STEP1                # (4, 1) passes
    assert g.bound_p(2, 0) < 0.001 and g.bound_p(0, 0) == 1.0


def test_r1_when_g_star_is_8_or_more_and_family_lists_only_the_tested_corruptions(env):
    code, doc = _decide(env, GO3)
    nr = doc["n_rule"]
    assert code == 0 and nr["rule"] == "R1" and nr["h_rule"] == "H-R1" and nr["G_star"] == 9 and nr["test_fold"] == 300 and doc["go"] is True and doc["downstream_claim_withdrawn"] is False
    assert [f["corruption"] for f in doc["family"]] == ["jpeg", "splice"] and [f["key"] for f in doc["family"]] == ["jpeg10", "splice128"]
    assert doc["family"][0]["G_c"] == 9 and doc["family"][0]["F_minus"] == 3 and doc["family"][1]["G_c"] == 4
    assert [e["corruption"] for e in doc["excluded"]] == ["noise"] and "G 0 < 3" in doc["excluded"][0]["reason"]
    assert nr["negative_reading_available"] is True and nr["time_rule"]["status"] == "ok" and nr["time_rule"]["n_by_rule"] == 300
    assert doc["endpoint"] == "d" and doc["n_headroom_items"] == 50 and nr["primary_endpoint"] == "Y" and nr["N_star"] == 43 and nr["min_G"] == 3 and nr["r1_G"] == 8
    assert nr["scale_50_to_300"] == 6 and nr["min_valid"] == 45 and nr["alpha_step1"] == 0.016667
    assert doc["clean_none_accuracy"]["n"] == 50 and set(doc["per_corruption"]["jpeg"]) >= {"n_valid", "F_minus", "F_plus", "bound_b", "bound_c", "bound_p", "headroom", "G", "chg_discordance", "tested", "reason"}
    assert doc["per_corruption"]["jpeg"]["bound_b"] == 18 and doc["per_corruption"]["jpeg"]["bound_c"] == 0
    assert set(doc["inputs"]) == {"h3_run", "items_sha256", "plan_family_sha256", "folds_h3_sha256", "code_commit"} and doc["spec"].startswith("SAP addendum A5")


def test_r2_when_g_star_is_3_to_7(env):
    code, doc = _decide(env, dict(jpeg=dict(fm=2, fp=0, g=7), noise=dict(fm=3, fp=0, g=3)))
    assert code == 0 and doc["n_rule"]["rule"] == "R2" and doc["n_rule"]["h_rule"] == "H-R2" and doc["n_rule"]["G_star"] == 7 and doc["n_rule"]["test_fold"] == 300
    assert [f["corruption"] for f in doc["family"]] == ["jpeg", "noise"]
    code, doc = _decide_fresh(env, dict(jpeg=dict(fm=2, fp=0, g=8)))
    assert doc["n_rule"]["rule"] == "R1"                                                   # 8 is the first R1 value


def _decide_fresh(env, spec, now=EARLY, **kw):
    for rel in ("P2-GATE-H3/family.json", "P2-GATE-H3/items.jsonl"):
        (env / rel).unlink(missing_ok=True)
    _write_rows(env, _rows(spec, **kw))
    return g.decide("P2-GATE-H3", g.parse_now(now), env)


def test_each_condition_of_the_tested_rule_is_necessary(env):
    # (a) fails: F- = 1 (bound (6, 0) p 0.031 > 0.0167); (b) fails: G = 2; both fine at G = 3 with F- = 2; F- <= F+ fails
    code, doc = _decide(env, dict(jpeg=dict(fm=1, fp=0, g=9), noise=dict(fm=2, fp=0, g=2), splice=dict(fm=3, fp=3, g=9)))
    assert doc["n_rule"]["rule"] == "NO-GO" and doc["n_rule"]["h_rule"] == "H-NOGO" and doc["family"] == [] and doc["go"] is False and doc["downstream_claim_withdrawn"] is True and code == 0
    pc = doc["per_corruption"]
    assert pc["jpeg"]["headroom"] is False and "bound p" in pc["jpeg"]["reason"] and pc["noise"]["headroom"] is True and "G 2 < 3" in pc["noise"]["reason"]
    assert pc["splice"]["headroom"] is False and pc["splice"]["F_plus"] == 3
    assert doc["n_rule"]["test_fold"] == 0 and doc["n_rule"]["time_rule"]["status"] == "not tested (NO-GO)" and doc["n_rule"]["negative_reading_available"] is False
    _, doc = _decide_fresh(env, dict(noise=dict(fm=2, fp=0, g=3)))
    assert [f["corruption"] for f in doc["family"]] == ["noise"] and doc["n_rule"]["rule"] == "R2"


def test_n_valid_below_45_means_not_tested_and_all_below_means_pilot_incomplete(env):
    g.plan(env)
    rows = _rows(GO3)
    for i in range(6):                                                                     # 6 invalid items -> 44 valid for every corruption
        rows[i]["conds"]["clean"]["img"]["none"]["y"] = float("nan")
    _write_rows(env, rows)
    code, doc = g.decide("P2-GATE-H3", g.parse_now(EARLY), env)
    assert code == 2 and doc["n_rule"]["rule"] == "NO-GO" and doc["n_rule"]["time_rule"]["status"] == "not run (pilot incomplete)" and doc["n_rule"]["test_fold"] == 0 and doc["go"] is False
    assert all("n_valid 44 < 45" in e["reason"] for e in doc["excluded"]) and len(doc["excluded"]) == 3
    assert json.loads((env / "P2-GATE-H3" / "family.json").read_text())["n_rule"]["h_rule"] == "H-NOGO"          # the file is still written


def test_one_corruption_with_few_valid_items_is_just_not_tested(env):
    g.plan(env)
    rows = _rows(dict(jpeg=dict(fm=3, fp=0, g=9), splice=dict(fm=3, fp=0, g=9)))
    for r in rows[:6]:
        r["conds"]["splice128"]["img"]["none"]["y"] = float("nan")
    _write_rows(env, rows)
    code, doc = g.decide("P2-GATE-H3", g.parse_now(EARLY), env)
    assert code == 0 and [f["corruption"] for f in doc["family"]] == ["jpeg"] and doc["per_corruption"]["splice"]["n_valid"] == 44


def test_missing_rows_is_a_pilot_incomplete_nogo(env):
    g.plan(env)
    code, doc = g.decide("P2-GATE-H3", g.parse_now(EARLY), env)
    assert code == 2 and doc["n_headroom_items"] == 0 and doc["n_rule"]["time_rule"]["status"] == "not run (pilot incomplete)" and doc["inputs"]["items_sha256"] is None


def test_a_row_outside_the_h3_items_is_refused(env):
    g.plan(env)
    rows = _rows(GO3)
    rows[3]["gid"] = 7003
    _write_rows(env, rows)
    with pytest.raises(ValueError, match="not an H3 item"):
        g.decide("P2-GATE-H3", g.parse_now(EARLY), env)
    rows[3]["gid"], rows[3]["image_id"] = 6003, 1
    _write_rows(env, rows)
    with pytest.raises(ValueError, match="not an H3 item"):
        g.decide("P2-GATE-H3", g.parse_now(EARLY), env)


# ------------------------------------------------------------------------------------------------ the time rule (A5.12)
@pytest.mark.parametrize("now,n,status", [("2026-10-30T09:00", 300, "ok"), ("2026-10-30T12:36", 300, "ok"), ("2026-10-30T12:37", 200, "n=200 by time"), ("2026-10-30T13:42", 200, "n=200 by time"),
                                          ("2026-10-30T13:43", 0, "cut by time"), ("2026-10-30T17:00", 0, "cut by time")])
def test_time_rule_boundaries(env, now, n, status):
    code, doc = _decide(env, GO3, now=now)
    nr = doc["n_rule"]
    assert nr["test_fold"] == n and nr["time_rule"]["status"] == status and nr["time_rule"]["n_by_rule"] == 300 and nr["time_rule"]["n_after_time"] == n
    assert doc["go"] is (n > 0) and doc["downstream_claim_withdrawn"] is (n == 0) and nr["rule"] == "R1" and nr["negative_reading_available"] is (n >= 240)
    assert nr["time_rule"]["freeze"] == "2026-10-30T18:00:00+05:30" and nr["time_rule"]["constants"] == dict(W_H3=0.75, A_H3=0.5, W_H4_300=2.9, W_H4_200=1.8, A_H4=0.5, M=2.0)
    assert nr["time_rule"]["now"].startswith(now[:16])


def test_a_naive_now_is_read_as_ist():
    assert g.parse_now("2026-10-30T12:36") == datetime(2026, 10, 30, 12, 36, tzinfo=g.IST)
    assert g.parse_now("2026-10-30T07:06:00+00:00") == datetime(2026, 10, 30, 12, 36, tzinfo=g.IST)


# ------------------------------------------------------------------------------------------------ no signed GATE-M quantity
def _keys(x, acc=None):
    acc = set() if acc is None else acc
    if isinstance(x, dict):
        for k, v in x.items():
            acc.add(k)
            _keys(v, acc)
    elif isinstance(x, list):
        for v in x:
            _keys(v, acc)
    return acc


def test_the_output_contains_no_signed_gate_quantity(env):
    _, doc = _decide(env, GO3)
    assert not (_keys(doc) & {"b", "c", "acc_gate", "gate_accuracy", "acc_a", "acc_b", "net", "delta", "theta", "yg", "gate_better"})
    text = json.dumps(doc)
    assert "gate0.05" not in text


def test_output_depends_on_the_gate_arm_only_through_the_unsigned_indicator(env):
    _, a = _decide(env, GO3, invalid=(45, 46), yg_noise=1.0)
    for rel in ("P2-GATE-H3/family.json", "P2-GATE-H3/items.jsonl"):
        (env / rel).unlink()
    _write_rows(env, _rows(GO3, invalid=(45, 46), yg_noise=0.0))                                  # yg differs on the invalid items only
    _, b = g.decide("P2-GATE-H3", g.parse_now(EARLY), env)
    strip = lambda d: {k: v for k, v in d.items() if k != "inputs"}                               # the input hash covers the raw rows, which do differ                   # noqa: E731
    assert strip(a) == strip(b) and a["inputs"]["items_sha256"] != b["inputs"]["items_sha256"]
    assert a["per_corruption"]["jpeg"]["n_valid"] == 48


# ------------------------------------------------------------------------------------------------ write-once and the readers
def test_decide_is_write_once(env):
    _decide(env, GO3)
    with pytest.raises(artifacts.WriteOnceError):
        g.decide("P2-GATE-H3", g.parse_now(EARLY), env)


def test_run_gate_m4_accepts_the_written_file_with_the_matching_n_and_refuses_otherwise(env):
    _decide(env, GO3)
    assert run_gate_m4.check_n_against_rule(300, env, "P2-GATE-H3") == 300 and run_gate_m4.check_n_against_rule(None, env, "P2-GATE-H3") == 300
    with pytest.raises(ValueError):
        run_gate_m4.check_n_against_rule(500, env, "P2-GATE-H3")
    for now, want in (("2026-10-30T13:00", 200), ("2026-10-30T16:00", 0)):
        _decide_fresh(env, GO3, now=now)
        if want:
            assert run_gate_m4.check_n_against_rule(200, env, "P2-GATE-H3") == 200
            with pytest.raises(ValueError, match="--n 300"):
                run_gate_m4.check_n_against_rule(300, env, "P2-GATE-H3")
        else:
            for n in (None, 300, 200, 0):                                               # test_fold 0 always refuses, --n 0 included
                with pytest.raises(ValueError, match="test fold 0"):
                    run_gate_m4.check_n_against_rule(n, env, "P2-GATE-H3")


def test_run_gate_m4_prereqs_take_the_tested_corruptions_from_the_written_file(env, monkeypatch):
    from fake_gate import fake_image
    from test_gate_runners_fake import _m4_prereqs, _sc
    monkeypatch.setattr(common, "load_image", lambda iid: fake_image(iid, 96))
    _m4_prereqs(env, _sc(), [("jpeg", 10), ("noise", 0.1), ("splice", 128)])
    _decide(env, GO3)
    thr, family, eps0 = run_gate_m4.load_prereqs(env, "P2-GATE-H3")
    assert family == [("jpeg", 10), ("splice", 128)] and set(thr) == {0.05, 0.01, 0.1}


def test_analysis_m4_reads_the_written_file(env, capsys):
    _decide(env, GO3)
    fam = json.loads((env / "P2-GATE-H3" / "family.json").read_text())
    assert analysis_m4._family_map(fam["family"]) == {"jpeg": "jpeg10", "splice": "splice128"}
    assert fam["n_rule"]["rule"] in ("R1", "R2", "NO-GO") and int(fam["n_rule"]["test_fold"]) == 300 and fam["endpoint"] == "d"
    (env / "P2-GATE-M1").mkdir(exist_ok=True)
    (env / "P2-GATE-M1" / "detection_frozen.json").write_text(json.dumps(dict(frozen={})))
    rc = analysis_m4.main(["--run-id", "P2-GATE-H4", "--family-run", "P2-GATE-H3", "--folds-path", str(env / "missing.json"), "--skip-selftest"])
    assert rc == 2 and "does not exist" in capsys.readouterr().err                          # the family file parsed; the next (missing folds) check is the one that stopped it
    prim = analysis_m4.primary([], fam["family"], n_boot=10)                                  # untested corruptions keep p = 1 and m = 3
    assert prim["holm_m"] == 3 and prim["per_corruption"]["noise"]["tested"] is False and prim["per_corruption"]["noise"]["p"] == 1.0


def test_constants_are_those_of_the_addendum():
    assert (g.N_STAR, g.MIN_G, g.R1_G, g.SCALE_50_TO_300, g.MIN_VALID) == (43, 3, 8, 6, 45) and g.ALPHA_STEP1 == pytest.approx(0.05 / 3)
    assert g.FREEZE == datetime(2026, 10, 30, 18, 0, tzinfo=g.IST) and (g.W_H3, g.A_H3, g.W_H4_300, g.W_H4_200, g.A_H4, g.MARGIN_H) == (0.75, 0.5, 2.9, 1.8, 0.5, 2.0)
    assert g.H3_GID_RANGE == (bh.GID_OFFSET["head"], bh.GID_OFFSET["head"] + bh.N_H3 - 1) and config.REALISTIC == ("jpeg", "noise", "splice")
