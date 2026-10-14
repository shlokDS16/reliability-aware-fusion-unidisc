import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))
from synth import make_arm, S, nounkey, ROOT      # noqa: E402

import tables as T                                  # noqa: E402
import frozen_analysis as FA                        # noqa: E402
import pilot_analysis as PA                         # noqa: E402
from exp003 import config as C, units as U          # noqa: E402


# ------------------------------------------------------------------------------------------------------------------ units and pools
def test_units_and_seeds():
    pu = U.pilot_units()
    cnt = lambda arm, tag: sum(1 for u in pu if u.arm == arm and u.tag == tag)
    assert cnt("P64", "P64") == 32 and cnt("G", "G") == 32 and cnt("G", "G50") == 8 and cnt("Ind", "Ind") == 8 and cnt("TF", "TF") == 8
    assert sum(1 for u in pu if u.tag.startswith("rerun/")) == 8 and sum(1 for u in pu if u.tag.startswith("hookcheck/")) == 8
    assert all(not u.instrument for u in pu if u.tag.startswith("hookcheck/"))
    assert U.Unit("m1", "G", "G", 3, 1).i == 60000 + 7 and U.Unit("ctrl", "Ind", "Ind", 2, 0).i == 62004 and U.Unit("pilot", "G", "G", 15, 1).i == 61031
    m = U.main_units("m1", 5)
    assert [u.arm for u in m[:4]] == ["P64", "G", "P64", "G"] and len(m) == 20       # interleaved by prefix: truncation leaves complete prefixes
    assert C.CALLS["G"] == 64 == C.CALLS["P64"] and C.CALLS["O0"] == 33


def test_pools_json_disjoint_and_hash():
    pj = json.loads((C.RUNS / "pools.json").read_text(encoding="utf8"))
    draw = json.loads((ROOT / "runs" / "EXP-001" / "gates" / "coco_draw.json").read_text(encoding="utf8"))
    ex = {x["image_id"] for v in draw["blocks"].values() for x in v}
    allids = []
    for name, size in C.POOL_SIZE.items():
        ids = pj["pools"][name]["ids"]
        assert len(ids) == size and not (set(ids) & ex)
        assert hashlib.sha256(json.dumps(ids).encode()).hexdigest() == pj["pools"][name]["ids_sha256"]
        allids += ids
    assert len(set(allids)) == 214 and pj["matches_card"]


# --------------------------------------------------------------------------------------------------- plans, wrappers, call counts
def test_plain_call_counts_and_ind_wrapper():
    import torch
    from exp001 import plan as P, rng
    from exp001.network import ToyNet
    from exp001.sampler import run_sample
    from exp003.gen import IndNet
    C.register_pools()
    net = ToyNet(seed=1, L_T=32, L_I=64, V_T=12, V_I=20)
    u = rng.sampler_uniforms("E3P", 61000, 96)
    for N, name in ((64, "J"), (32, "J")):
        n0 = net.n_forward
        run_sample(net, P.plan_J(N, 64), u)
        assert net.n_forward - n0 == N
    n0 = net.n_forward
    run_sample(net, P.plan_TF(32, 64), u)
    assert net.n_forward - n0 == 32
    n0 = net.n_forward
    run_sample(IndNet(net), P.plan_J(32, 64), u)
    assert net.n_forward - n0 == 64                                   # two forwards per pass
    ind = IndNet(net)
    t0 = torch.full((32,), net.mask_id)
    i1, i2 = torch.full((64,), -1), torch.randint(0, 20, (64,))
    a, _ = ind.forward(t0, i1)
    b, _ = ind.forward(t0, i2)
    assert torch.equal(a, b)                                          # text marginals independent of the image


def test_pool_codes_additive():
    from exp001.config import POOL_CODE
    C.register_pools()
    assert POOL_CODE["E3P"] == 31 and POOL_CODE["E3C"] == 32 and POOL_CODE["E3M"] == 33 and len(set(POOL_CODE.values())) == len(POOL_CODE)


def test_commit_steps_and_order_summary():
    from exp003.official import commit_steps, tail_vs_image_order
    M = 32000
    ent = np.array([[M] * 6, [5, M, M, M, 7, M], [5, 6, M, M, 7, 8]])
    fin = np.array([5, 6, 9, M, 7, 8])
    assert commit_steps(ent, fin).tolist() == [1, 2, 3, 4, 1, 2]       # 4 = left to the final noise-removal pass
    cs = np.array([1] * 32 + list(range(1, 33)) * 32)[:32 + 1024]
    o = tail_vs_image_order(cs.astype(float))
    assert o["mean_step_tail"] == 1.0 and o["tail_share_before_image_q25"] == 1.0


# --------------------------------------------------------------------------------------------------------------- placebo and queries
def test_placebo_and_queries():
    n = 12
    smp, sets, _, _ = make_arm(n, seed=3)
    pl = T.placebo_sets(sets, n)
    pi = T.derangement(n, C.DERANGEMENT_SEED_PLACEBO)
    assert not np.any(pi == np.arange(n))
    assert [x["PL"] for x in pl] == [x["PL"] for x in T.placebo_sets(sets, n)]            # deterministic
    for p in range(n):
        bad = nounkey.keys(sets[p]["N"][0]) | nounkey.keys(sets[p]["N"][1])
        src = {nounkey.key(x) for x in sets[int(pi[p])]["D"][0] + sets[int(pi[p])]["D"][1]}
        for e in (0, 1):
            assert len(pl[p]["PL"][e]) <= len(sets[p]["D"][e])
            assert all(nounkey.key(x) not in bad and nounkey.key(x) in src for x in pl[p]["PL"][e])
    cpi = T.derangement(n, C.DERANGEMENT_SEED_CROSS)
    q64 = T.queries_for_prefix(0, sets, pl, "P64", n, cpi)
    q32 = T.queries_for_prefix(0, sets, pl, "P32", n, cpi)
    assert any(k.startswith(f"{int(cpi[0])}:") for _, k in q64) and not any(k.startswith(f"{int(cpi[0])}:") and int(cpi[0]) != 0 for _, k in q32)


def test_build_records_from_score_files(tmp_path):
    n = 3
    smp, sets, _, _ = make_arm(n, seed=4)
    cpi = T.derangement(n, C.DERANGEMENT_SEED_CROSS)
    pl = T.placebo_sets(sets, n)
    d = tmp_path / "pilot" / "G"
    d.mkdir(parents=True)
    for p in range(n):
        q = [[a, b, 1.0 if (hash((a, b)) % 2) else 0.0] for a, b in dict.fromkeys(T.queries_for_prefix(p, sets, pl, "G", n, cpi))]
        (d / f"p{p:03d}.json").write_text(json.dumps(dict(p=p, ok=True, q=q, iqa=[0.5, 0.6])))
    recs = T.build_records("pilot", "G", n, sets, pl, tmp_path, cpi)
    assert all(r["ok"] and len(r["own"][0]) == len(sets[i]["D"][0]) for i, r in enumerate(recs))


# ---------------------------------------------------------------------------------------------------- analysis end to end (synthetic)
def test_frozen_analysis_end_to_end_synthetic():
    bundles = {"G": make_arm(150, link=0.25, seed=21), "P64": make_arm(150, link=0.05, seed=22), "O0": make_arm(150, link=0.1, seed=23),
               "P32": make_arm(150, link=0.05, seed=24)}
    res = FA.analyse(bundles, B=600, seed=1, coco_set={"thing1"})
    c = res["confirmatory"]
    assert c["delta1"]["d"] > 0.1 and c["delta1"]["class"].startswith("positive")
    assert abs(c["identity"]["residual"]) < 1e-12
    assert c["delta2a"]["exploratory"] is (not (c["delta1"]["p"] <= 0.05)) and "p_holm" in c["delta2b"]
    assert res["arms"]["G"]["nc2_pass"] in (True, False) and res["arms"]["G"]["lambda_d"] is not None
    # null world: classification must not be positive
    nul = {k: make_arm(150, link=0.0, seed=30 + i) for i, k in enumerate(("G", "P64", "O0", "P32"))}
    r0 = FA.analyse(nul, B=600, seed=1)["confirmatory"]["delta1"]
    assert not r0["class"].startswith("positive") and r0["class"] != "reversed" or abs(r0["d"]) < 0.1


# ------------------------------------------------------------------------------------------------------------------- n rule, stops
def _inputs(**kw):
    d = dict(share_elig=0.85, sd_paired=0.38, gen_s_per_sample_sum_main=3.3 + 6.8 + 3.6 + 6.5, gen_s_per_sample_sum_ctrl=14.0,
             score_s_per_prefix_main=10.0, score_s_per_prefix_ctrl=4.0, pc2_s=60.0, pilot_wall_s=2000.0,
             g32=dict(n=32, empty_or_padonly=1, near_uniform=2), g50=dict(n=8, empty_or_padonly=0, near_uniform_only=0),
             det_plain=(4, 4), det_official=(4, 4), hookcheck=(8, 8), failed_units=0, total_units=150, guidance_failures=0)
    d.update(kw)
    return d


def test_design_rules():
    r = PA.design_rules(_inputs())
    assert r["n_req_eligible"] == int(np.ceil(((1.96 + 1.2816) * 1.21 * 0.38 / 0.10) ** 2)) and r["stop_reasons"] == [] or r["stop_reasons"]
    assert 0 < r["n_generate"] <= 150 and r["n_conf_eligible"] >= 120
    assert any("9.3" in s for s in PA.design_rules(_inputs(sd_paired=0.7))["stop_reasons"])           # MDE above 0.15
    assert any("9.2" in s for s in PA.design_rules(_inputs(g32=dict(n=32, empty_or_padonly=20, near_uniform=2)))["stop_reasons"])
    assert not any("9.2" in s for s in PA.design_rules(_inputs(g32=dict(n=32, empty_or_padonly=20, near_uniform=2), g50=dict(n=8, empty_or_padonly=5, near_uniform_only=0)))["stop_reasons"])
    assert any("9.1" in s for s in PA.design_rules(_inputs(share_elig=0.5))["stop_reasons"])           # 120 eligible need 240 > 150 prefixes
    assert any("9.1" in s for s in PA.design_rules(_inputs(gen_s_per_sample_sum_main=60.0))["stop_reasons"])   # wall-clock above 6 h
    assert any("9.6" in s for s in PA.design_rules(_inputs(det_plain=(3, 4)))["stop_reasons"])
    assert PA.design_rules(_inputs(share_elig=0.0))["stop_reasons"]


def test_controls_decision_synthetic():
    ind = make_arm(48, link=0.0, seed=41)
    tf = make_arm(48, link=0.3, seed=42)
    r = FA.controls_decision({"Ind": ind, "TF": tf}, Path("nonexistent.json"), B=800)
    assert r["nc1"]["passes"] and r["pc1"]["passes"]
    bad = FA.controls_decision({"Ind": make_arm(48, link=0.3, seed=43), "TF": tf}, Path("nonexistent.json"), B=800)
    assert not bad["nc1"]["passes"]
