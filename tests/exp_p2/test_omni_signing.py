"""Code audit part 3 fixes (2026-10-28 PM): the T1 signing check, T2 record, T3 gate on the load and self-check peak, the realised 4-bit module count (m-4), a failed self-check stopping later chunks
(m-1), HF offline for the Omni driver stages. CPU only; fakes only; nothing signs anything."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT, Path(__file__).resolve().parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from exp_p2 import common, run_omni_timing as T                              # noqa: E402
from exp_p2.gate import analysis_omni as ao, gate_driver, runner               # noqa: E402
from exp_p2.omni import build, signing                                        # noqa: E402
from test_gate_integration import driver as _driver, env                       # noqa: E402,F401


def _a5(mean_logp=-3.0, top1=0.2, ok=True):
    return dict(id="A5", ok=ok, detail=dict(per_shift={"0": dict(mean_logp=-12.0, top1=0.0), "1": dict(mean_logp=mean_logp, top1=top1), "2": dict(mean_logp=-12.5, top1=0.0)}, margin_observed=9.0, n_rows=6))


def _sel(**over):
    res = [dict(id=f"A{i}", ok=True, detail={}) for i in range(1, 8)]
    res[4] = _a5()
    s = dict(ids_equal=True, adapter=dict(all_ok=True, failed=[], results=res), peak_alloc_mib_during_checks=6100.0, peak_gate=dict(ok=True, limit_mib=7000.0),
             quantisation=dict(n_linear4bit=196, n_plain_linear=3, expected_linear4bit=196, matches=True))
    s.update(over)
    return s


ENV = dict(pins_match=dict(omni_sha=True, snapshot=True, magvit=True), skip_modules=list(signing.T2_SKIP_MODULES), versions=dict(transformers="4.51.3", bitsandbytes="0.50.2"), mem_frac=0.62,
           guard_cap_mib=7581.0, allocated_after_load_mib=5940.0)
ROWS = [dict(idx=i, fwd_s=0.3, peak_alloc_mib=6100.0, finite=True) for i in range(20)]


# ------------------------------------------------------------------------------------------------ T1
def test_t1_floors_on_the_a5_numbers():
    assert signing.t1_check(_sel())["ok"]
    assert not signing.t1_check(_sel(adapter=dict(all_ok=True, failed=[], results=[dict(id="A5", ok=True, detail=dict(per_shift={"1": dict(mean_logp=-8.5, top1=0.3)}))])))["ok"]    # near uniform (-9.011)
    assert not signing.t1_check(dict(adapter=dict(results=[dict(id="A5", ok=True, detail=dict(per_shift={"1": dict(mean_logp=-3.0, top1=0.004)}))])))["ok"]                       # top-1 below 0.005
    edge = signing.t1_check(dict(adapter=dict(results=[dict(id="A5", ok=True, detail=dict(per_shift={"1": dict(mean_logp=-8.011, top1=0.005)}))])))
    assert edge["ok"] and edge["floors"] == dict(mean_logp=-8.011, top1=0.005)                      # the floors themselves pass (>=)
    assert not signing.t1_check(dict(adapter=dict(results=[_a5(ok=False)])))["ok"] and not signing.t1_check(None)["ok"] and not signing.t1_check(dict(adapter=dict(results=[])))["a5_present"]


def test_omni_gate_rule_b_includes_t1_but_checks_py_is_untouched():
    kw = dict(timing_log=[dict(idx=i, fwd_s=(5.0 if i < 5 else 0.3), peak_alloc_mib=6400.0, finite=True) for i in range(20)], m2_log=[dict(idx=i, n_rows=12) for i in range(10)],
              m4_log=[dict(idx=i, n_rows=75, conds={"clean": {"kind": "clean"}, "jpeg10": {"kind": "pixel"}, "patch": {"kind": "token"}}) for i in range(10)])
    sig = dict(signed_by="gate-auditor", verdict="PASS")
    good = ao.omni_gate(kw["timing_log"], kw["m2_log"], kw["m4_log"], n_plus=1, time_left_h=10.0, adapter_signature=sig, selfcheck=_sel(), guard_cap_mib=7500.0)
    assert good["go"] and good["conditions"]["b"]["t1_a5_floors"]["ok"]
    weak = _sel()
    weak["adapter"]["results"][4] = _a5(mean_logp=-8.9, top1=0.0001)
    bad = ao.omni_gate(kw["timing_log"], kw["m2_log"], kw["m4_log"], n_plus=1, time_left_h=10.0, adapter_signature=sig, selfcheck=weak, guard_cap_mib=7500.0)
    assert not bad["go"] and not bad["conditions"]["b"]["ok"] and bad["conditions"]["b"]["t1_a5_floors"]["ok"] is False
    import hashlib
    assert hashlib.sha256((ROOT / "exp_p2" / "omni" / "checks.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest() == "9e397f2a3dedcd4a8edf133214d30ed25ee9170ca80a089238435c2217f6c48f"      # SAP A3b.4 item 2


# ------------------------------------------------------------------------------------------------ the signing check as a whole
def test_signing_check_reads_s1_s3_s4_s6_s7_s8_and_the_quantisation_count():
    ok = signing.signing_check(_sel(), ENV, ROWS, [dict(event="chunk_start")])
    assert ok["all_ok"] and set(ok["conditions"]) == {"S-1", "S-3_T1", "S-4_T2", "S-6_T3", "S-7", "S-8", "m-4_quantisation"} and "S-2" in ok["not_checked_here"]
    assert not signing.signing_check(_sel(adapter=dict(all_ok=True, failed=[], results=[dict(id=f"A{i}", ok=True) for i in (1, 2, 3)])), ENV, ROWS, [])["conditions"]["S-1"]["ok"]
    assert signing.signing_check(_sel(adapter=dict(all_ok=True, failed=[], results=[dict(id=f"A{i}", ok=True) for i in (1, 2, 3)])), ENV, ROWS, [])["conditions"]["S-1"]["missing"] == ["A4", "A5", "A6", "A7"]
    assert not signing.signing_check(_sel(), dict(ENV, pins_match=dict(omni_sha=True, snapshot=False, magvit=True)), ROWS, [])["conditions"]["S-4_T2"]["ok"]
    assert not signing.signing_check(_sel(), dict(ENV, versions=dict(transformers="4.52.0", bitsandbytes="0.50.2")), ROWS, [])["conditions"]["S-4_T2"]["ok"]
    assert not signing.signing_check(_sel(peak_alloc_mib_during_checks=7100.0), ENV, ROWS, [])["conditions"]["S-6_T3"]["ok"]
    assert not signing.signing_check(_sel(), ENV, ROWS[:-1] + [dict(idx=19, fwd_s=0.3, peak_alloc_mib=7001.0, finite=True)], [])["conditions"]["S-6_T3"]["ok"]
    assert not signing.signing_check(_sel(), dict(ENV, allocated_after_load_mib=3000.0), ROWS, [])["conditions"]["S-7"]["ok"]
    assert not signing.signing_check(_sel(), ENV, ROWS, [dict(event="selfcheck_failed_earlier")])["conditions"]["S-8"]["ok"]
    assert not signing.signing_check(_sel(quantisation=dict(n_linear4bit=150, expected_linear4bit=196, matches=False)), ENV, ROWS, [])["conditions"]["m-4_quantisation"]["ok"]
    assert not signing.signing_check(None, None, [], [])["all_ok"]


def test_signing_cli_writes_a_write_once_file_and_never_a_signature(env):
    d = env / "P2-OMNI-TIMING"
    d.mkdir()
    (d / "selfcheck.json").write_text(json.dumps(_sel()))
    (d / "omni_env.json").write_text(json.dumps(ENV))
    for r in ROWS:
        common.append_jsonl(d / "items.jsonl", r)
    assert signing.main(["--runs-dir", str(env)]) == 0
    assert (d / "signing_check.json").exists() and not (d / "adapter_signature.json").exists()
    with pytest.raises(FileExistsError):
        signing.main(["--runs-dir", str(env)])
    (d / "signing_check.json").unlink()
    (d / "selfcheck.json").write_text(json.dumps(_sel(peak_alloc_mib_during_checks=7500.0)))
    assert signing.main(["--runs-dir", str(env)]) == 3


# ------------------------------------------------------------------------------------------------ T2 and m-4 records
def test_t2_record_in_omni_env():
    from exp_p2.omni import loader
    base = dict(pins_match=dict(omni_sha=True, snapshot=True, magvit=True), skip_modules=list(loader.SKIP_MODULES), versions=dict(transformers="4.51.3", bitsandbytes="0.50.2"), mem_frac=0.62, guard_cap_mib=7581.0)
    assert build.t2_record(base)["all_ok"] and build.t2_record(base)["versions_expected"] == dict(transformers="4.51.3", bitsandbytes="0.50.2")
    for k, v in (("pins_match", dict(omni_sha=False, snapshot=True, magvit=True)), ("versions", dict(transformers="4.52", bitsandbytes="0.50.2")), ("mem_frac", 0.75), ("skip_modules", ["audio_model"])):
        assert not build.t2_record(dict(base, **{k: v}))["all_ok"], k
    assert signing.T2_SKIP_MODULES == tuple(loader.SKIP_MODULES) and signing.T2_MEM_FRAC == build.PROPOSED["mem_frac"] and signing.PEAK_LIMIT_MIB == build.PROPOSED["max_peak_alloc_mib"]


def test_realised_quantisation_counts_linear4bit_modules():
    class Linear4bit:
        pass

    class Linear:
        pass
    fake = SimpleNamespace(modules=lambda: [Linear4bit() for _ in range(196)] + [Linear(), Linear(), Linear()])
    q = build.realised_quantisation(fake)
    assert q == dict(n_linear4bit=196, n_plain_linear=3, expected_linear4bit=196, matches=True) and build.EXPECTED_LINEAR4BIT == 196
    assert build.realised_quantisation(SimpleNamespace(modules=lambda: [Linear4bit()] * 100))["matches"] is False


# ------------------------------------------------------------------------------------------------ T3: the load and self-check peak is gated
@pytest.mark.parametrize("peak,stops", [(6100.0, False), (7000.0, False), (7100.0, True)])
def test_the_load_and_selfcheck_peak_above_7000_is_a_guard_stop(peak, stops, env, monkeypatch):
    import torch
    from exp_p2.omni import checks
    r = lambda cid: (lambda *a, **k: dict(id=cid, ok=True, detail={}))
    for name, cid in (("check_mask_id", "A1"), ("check_image_range", "A2"), ("check_layout_roundtrip", "A3"), ("check_shift_code_path", "A4"), ("check_shift_behaviour", "A5"), ("check_audio_stub_inert", "A6"),
                      ("check_layout_only_null", "A7")):
        monkeypatch.setattr(checks, name, r(cid))
    monkeypatch.setattr(torch.cuda, "is_available", lambda: True)
    monkeypatch.setattr(torch.cuda, "max_memory_allocated", lambda *a, **k: peak * 2 ** 20)
    monkeypatch.setattr(common, "load_image", lambda iid: None)
    (env / "P2-OMNI-TIMING").mkdir()                                                            # run_items has created the run directory before the self-check

    class Mod:
        def modules(self):
            return []
    raw = SimpleNamespace(selfcheck=lambda pil, cap: dict(ids_equal=True, modality_equal=True, image_tokens_frac_equal=1.0), model=Mod(), dev=SimpleNamespace(type="cpu"),
                          build=lambda *a, **k: {}, caption_ids=lambda c: [1], encode=lambda p: None, preprocess=lambda p: p)
    items = [dict(image_id=i, caption="a b c d e f") for i in range(6)]
    a = SimpleNamespace(skip_gpu_adapter_checks=False, max_peak_alloc_mib=7000.0, run_id="P2-OMNI-TIMING")
    out = T.adapter_selfcheck(raw, items, {"stub": None}, a)
    assert out["peak_alloc_mib_during_checks"] == peak and out["peak_gate"]["ok"] is (not stops) and out["ids_equal"] is (not stops)
    assert out["quantisation"]["n_linear4bit"] == 0
    ev = common.read_jsonl(env / "P2-OMNI-TIMING" / "chunks.jsonl") if (env / "P2-OMNI-TIMING" / "chunks.jsonl").exists() else []
    assert bool([e for e in ev if e.get("event") == "guard_stop" and "load_and_selfcheck_peak_alloc" in e["reason"]]) is stops


# ------------------------------------------------------------------------------------------------ m-1: a failed self-check stops later chunks
def test_a_self_check_that_failed_in_an_earlier_chunk_stops_every_later_chunk(env):
    calls = []
    kw = dict(run_id="P2-OMNI-T", cfg=dict(n_items=3), load=lambda: calls.append("load") or object(), get_items=lambda sc, r: [dict(idx=i) for i in range(3)], process=lambda sc, it, c: (dict(v=1), {}),
              duty=1.0, soft_minutes=30)
    bad = lambda sc, items: dict(ids_equal=False, modality_equal=True, image_tokens_frac_equal=1.0)
    assert runner.run_items(selfcheck=bad, **kw) == runner.EXIT_SELFCHECK == 2 and calls == ["load"]
    assert runner.run_items(selfcheck=lambda sc, items: dict(ids_equal=True, modality_equal=True, image_tokens_frac_equal=1.0), **kw) == 2        # the earlier failure stands; the check is not re-run to pass
    assert calls == ["load"]                                                                    # the model was not loaded again
    assert any(e.get("event") == "selfcheck_failed_earlier" for e in common.read_jsonl(env / "P2-OMNI-T" / "chunks.jsonl"))
    good = dict(kw, run_id="P2-OMNI-U")
    ok = lambda sc, items: dict(ids_equal=True, modality_equal=True, image_tokens_frac_equal=1.0)
    assert runner.run_items(selfcheck=ok, limit=1, **good) == runner.EXIT_MORE_WORK
    assert runner.run_items(selfcheck=ok, **good) == 0 and runner.selfcheck_passed(dict(ids_equal=True, modality_equal=True, image_tokens_frac_equal=0.99))
    assert not runner.selfcheck_passed(dict(ids_equal=True, modality_equal=True, image_tokens_frac_equal=0.98))


# ------------------------------------------------------------------------------------------------ HF offline for the Omni driver stages
def test_omni_stages_get_hf_offline_in_the_child_environment_and_other_stages_do_not(_driver, monkeypatch):
    envs = {}

    def fake_run(cmd, **kw):
        envs[len(envs)] = kw.get("env")
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(gate_driver.subprocess, "run", fake_run)
    monkeypatch.setenv("HF_HUB_OFFLINE", "0")
    for st in ("omni-timing", "omni-r-test", "m2"):
        gate_driver.main(["--stage", st, "--max-chunks", "1", "--n", "5"])
    assert envs[0]["HF_HUB_OFFLINE"] == "1" and envs[0]["TRANSFORMERS_OFFLINE"] == "1" and envs[1]["HF_HUB_OFFLINE"] == "1"       # assigned, a shell's 0 cannot win
    assert envs[2] is None                                                                      # UniDisc stages inherit the environment unchanged
    assert set(gate_driver.STAGE_ENV) == set(gate_driver.STAGE_PY)
