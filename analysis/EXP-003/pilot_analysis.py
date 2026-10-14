"""Pilot analysis with the firewall of EXP-003 card section 7 (eval venv, CPU). HASHED BEFORE THE PILOT IS GENERATED.

Writes runs/EXP-003/pilot/pilot_report.json and runs/EXP-003/n_conf.json. The report contains ONLY: costs, memory, telemetry, per-arm
completion counts, noun and discordant counts, failure and degeneracy counts, determinism and hook-check counts, the eligible-prefix share per
arm, and the SD of the paired per-prefix difference L_p(G) - L_p(P64). It computes no Lambda_b or Lambda_d, no arm mean of any link, no
contrast, and no CLIP lift. `design_rules` is a pure function of the report numbers: the n rule (7), stop rules 9.1, 9.2, 9.3, 9.6.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(HERE), str(ROOT / "analysis" / "EXP-001")]

import stats as S                                                   # noqa: E402
from exp003 import config as C                                      # noqa: E402

LOAD_S = 25.0            # model load per chunk [A, card 8]
CHUNK_EFF_S = 13 * 60.0  # useful seconds of compute+idle per chunk (15 min chunk, soft deadline 13)
MDE_STOP = 0.15
Z80, Z90 = 0.8416, 1.2816


def projected_wall_h(g, d, e=None):
    """Projected cumulative GPU wall-clock (hours) with the pilot's measured costs when g prefixes are generated for the main stage:
    pilot (actual) + controls + main generation + main scoring, each at the measured duty with chunk pauses and model loads."""
    gen_s = g * 2 * d["gen_s_per_sample_sum_main"]
    score_s = g * d["score_s_per_prefix_main"]
    ctrl_s = 48 * 2 * d["gen_s_per_sample_sum_ctrl"] + 48 * d["score_s_per_prefix_ctrl"] + d["pc2_s"]

    def wall(c):
        w = c / C.DUTY
        return w + math.ceil(w / CHUNK_EFF_S) * (C.PAUSE_S + LOAD_S)
    return (d["pilot_wall_s"] + wall(ctrl_s) + wall(gen_s) + wall(score_s)) / 3600.0


def design_rules(d: dict) -> dict:
    """d: share_elig e, sd_paired, gen_s_per_sample_sum_main, gen_s_per_sample_sum_ctrl, score_s_per_prefix_main, score_s_per_prefix_ctrl,
    pc2_s, pilot_wall_s, G32 and G50 degeneracy counts, determinism counts. Returns n_conf and the stop reasons (empty list = go)."""
    stops, e = [], d["share_elig"]
    sd = d["sd_paired"]
    sig_up, n_req = (S.sample_size(sd) if sd is not None and not math.isnan(sd) else (float("nan"), 0))
    out = dict(share_eligible=e, sd_paired=sd, sigma_d_up=sig_up, n_req_eligible=n_req)
    if math.isnan(sig_up):
        stops.append("n rule: the SD of the paired per-prefix difference is not computable (fewer than 3 prefixes eligible in both G and P64)")
    if not e or e <= 0:
        stops.append("9.3/n rule: no prefix is eligible in both G and P64 in the pilot (share 0)")
        out.update(stop_reasons=stops)
        return out
    g120 = math.ceil(120 / e)
    out["g_for_120_eligible"] = g120
    out["projected_wall_h_at_120_eligible"] = projected_wall_h(g120, d)
    if g120 > C.POOL_SIZE["E3-MAIN"]:
        stops.append(f"9.1: 120 eligible prefixes need {g120} generated prefixes > pool 150 (eligible share {e:.3f})")
    if out["projected_wall_h_at_120_eligible"] > C.BUDGET_H:
        stops.append(f"9.1: projected wall-clock {out['projected_wall_h_at_120_eligible']:.2f} h at 120 eligible prefixes exceeds {C.BUDGET_H} h")
    cap = 0
    for g in range(1, C.POOL_SIZE["E3-MAIN"] + 1):
        if projected_wall_h(g, d) <= C.BUDGET_H:
            cap = g
    out["n_cap_generated"] = cap
    n_e_cap = int(math.floor(e * cap))
    out["eligible_at_cap"] = n_e_cap
    if not math.isnan(sig_up) and n_e_cap > 0:
        out["mde80_at_cap"] = (2.8016 * sig_up) / math.sqrt(n_e_cap)
        if out["mde80_at_cap"] > MDE_STOP:
            stops.append(f"9.3: achieved MDE (80 percent power) {out['mde80_at_cap']:.3f} > {MDE_STOP} at the expected eligible count {n_e_cap}")
    if n_e_cap < 120:
        stops.append(f"9.1/n rule: no n >= 120 eligible prefixes fits (expected eligible {n_e_cap} at the cap of {cap} generated prefixes)")
        n_conf = n_e_cap
    else:
        n_conf = int(min(max(n_req, 120), n_e_cap))
    out["n_conf_eligible"] = n_conf
    out["n_generate"] = int(min(cap, C.POOL_SIZE["E3-MAIN"], math.ceil(n_conf / e))) if n_conf > 0 else 0
    out["power_at_MEI_expected"] = float(S.norm.cdf(0.10 * math.sqrt(max(n_conf, 1)) / sig_up - 1.96)) if (not math.isnan(sig_up) and sig_up > 0) else None
    # 9.2: G degenerate at 32 steps but not at 50
    g32, g50 = d["g32"], d["g50"]
    deg32 = g32["empty_or_padonly"] >= 0.5 * g32["n"] or g32["near_uniform"] >= 8
    ok50 = g50["n"] > 0 and (g50["empty_or_padonly"] + g50["near_uniform_only"]) <= 1
    out["g_degenerate_32"], out["g50_ok"] = bool(deg32), bool(ok50)
    if deg32 and ok50:
        stops.append("9.2: G is degenerate at 32 steps (empty/pad-only completions or near-uniform images) but not at 50; new card version needed")
    # 9.6 determinism and hooks
    if d["det_plain"][0] < d["det_plain"][1]:
        stops.append(f"9.6: plain arms token-identical on {d['det_plain'][0]} of {d['det_plain'][1]} rerun units (need all)")
    if d["det_official"][0] < 3 and d["det_official"][1] == 4:
        stops.append(f"9.6: official arms token-identical on {d['det_official'][0]} of 4 rerun units (below 3)")
    hc_ok, hc_n = d["hookcheck"]
    if hc_n and hc_ok < hc_n * (d["det_official"][0] / max(d["det_official"][1], 1)) - 1:
        stops.append(f"hook check: tokens identical with and without the read-only hooks on {hc_ok} of {hc_n} units")
    if d["failed_units"] > 0.1 * max(d["total_units"], 1):
        stops.append(f"{d['failed_units']} of {d['total_units']} pilot units failed (see failures.jsonl)")
    if d["guidance_failures"] > 0:
        stops.append(f"guidance-acted assertion failed on {d['guidance_failures']} G pilot units")
    out["stop_reasons"] = stops
    return out


# ---------------------------------------------------------------------------------------------------------------------- inputs
def telemetry_summary(paths):
    mx, thr, rows, pw = 0.0, 0, 0, []
    for p in paths:
        for r in csv.DictReader(open(p, encoding="utf8")):
            try:
                mx = max(mx, float(r["temperature.gpu"]))
                pw.append(float(r["power.draw"]))
                rows += 1
                thr += int(r["clocks_throttle_reasons.active"], 16) not in (0, 1, 4) if r["clocks_throttle_reasons.active"].startswith("0x") else 0
            except (ValueError, KeyError):
                pass
    return dict(n_files=len(paths), n_rows=rows, max_temp_c=mx, mean_power_w=float(np.mean(pw)) if pw else None, throttle_rows=thr)


def near_uniform_png(path, thr=6.0):
    from PIL import Image
    return bool(np.asarray(Image.open(path).convert("L"), dtype=np.float64).std() < thr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen-dir", default=str(C.RUNS / "gen"))
    ap.add_argument("--score-dir", default=str(C.RUNS / "score"))
    ap.add_argument("--out", default=str(C.RUNS / "pilot" / "pilot_report.json"))
    ap.add_argument("--n-conf-out", default=str(C.RUNS / "n_conf.json"))
    ap.add_argument("--clock", default=str(C.RUNS / "clock.json"))
    ap.add_argument("--n-prefix", type=int, default=16)
    a = ap.parse_args()
    import tables as T
    gen, score = Path(a.gen_dir), Path(a.score_dir)
    tools = T.Tools()
    n = a.n_prefix
    from exp003.units import load_pool_items
    items = load_pool_items("E3-PILOT")
    rep = dict(card="EXP-003 v0.3.2", firewall="costs, counts, SD of paired L_p difference only; no link mean, contrast or CLIP lift")
    arms, bundles, cost, counts = ("P64", "G", "O0", "P32", "Ind", "TF"), {}, {}, {}
    for arm in arms:
        b = T.arm_bundle("pilot", arm, n, items, tools, gen, score)
        bundles[arm] = b
        smp, sets, plac, recs = b
        flat = [s for pair in smp for s in pair if s is not None]
        mets = [s["meta"] for s in flat]
        cost[arm] = dict(n_samples=len(flat), seconds_median=float(np.median([m["seconds"] for m in mets])) if mets else None,
                         seconds_mean=float(np.mean([m["seconds"] for m in mets])) if mets else None,
                         calls_values=sorted({m.get("calls") for m in mets}), peak_gb_max=max([m["peak_gb"] for m in mets], default=None))
        el = [s for s in sets if s is not None and len(s["D"][0]) and len(s["D"][1])]
        counts[arm] = dict(
            n_prefix_both_seeds=int(sum(s is not None for s in sets)), n_eligible=len(el), share_eligible=len(el) / n,
            empty_completion=int(sum(s["cend"].completion_len == 0 for s in flat)),
            mean_completion_len=float(np.mean([s["cend"].completion_len for s in flat])) if flat else None,
            nouns_total=int(sum(len(s["nouns"]) for s in flat)),
            discordant_total=int(sum(len(x) for s in sets if s is not None for x in s["D"])),
            near_uniform_images=int(sum(near_uniform_png(s["png"]) for s in flat if s["png"].exists())))
    # eligibility in both G and P64, SD of the paired per-prefix difference (the only link-derived number)
    LG, LP = S.arm_L(bundles["G"][3]), S.arm_L(bundles["P64"][3])
    com = ~(np.isnan(LG) | np.isnan(LP))
    share = float(com.mean())
    sd = float(np.std((LG - LP)[com], ddof=1)) if com.sum() > 2 else float("nan")
    # G at 50 steps (8 samples)
    g50 = []
    for p in range(8):
        base = gen / "pilot" / "G50" / f"p{p:03d}_e0"
        s = T.load_sample(base, items[p], tools)
        if s is not None:
            g50.append(dict(empty=s["cend"].completion_len == 0, nu=near_uniform_png(s["png"])))
    g32 = [s for pair in bundles["G"][0] for s in pair if s is not None]
    g32_nu = [near_uniform_png(s["png"]) for s in g32]
    g32_empty = [s["cend"].completion_len == 0 for s in g32]
    # determinism and hook check
    def same(tag, ref_tag, ps):
        out = []
        for p in ps:
            f1, f2 = gen / "pilot" / tag / f"p{p:03d}_e0.npz", gen / "pilot" / ref_tag / f"p{p:03d}_e0.npz"
            if f1.exists() and f2.exists():
                z1, z2 = np.load(f1), np.load(f2)
                out.append(bool(np.array_equal(z1["tail"], z2["tail"]) and np.array_equal(z1["img"], z2["img"])))
        return out
    dp = same("rerun/P64", "P64", (0, 1)) + same("rerun/P32", "P32", (0, 1))
    do = same("rerun/O0", "O0", (0, 1)) + same("rerun/G", "G", (0, 1))
    hc = same("hookcheck/O0", "O0", range(4)) + same("hookcheck/G", "G", range(4))
    fails = [json.loads(l) for l in (gen / "pilot" / "failures.jsonl").read_text().splitlines()] if (gen / "pilot" / "failures.jsonl").exists() else []
    all_markers = list((gen / "pilot").rglob("p*_e*.json"))
    failed_units = sum(1 for f in all_markers if json.loads(f.read_text()).get("failed"))
    # scoring cost
    sc = {arm: [json.loads(f.read_text()) for f in sorted((score / "pilot" / arm).glob("p*.json"))] for arm in arms}
    vlm_calls = sum(j.get("vlm_calls", 0) for js in sc.values() for j in js)
    vlm_s = sum(j.get("vlm_s", 0.0) for js in sc.values() for j in js)
    unit_s = {}
    for line in (score / "pilot" / "stage_log.jsonl").read_text().splitlines() if (score / "pilot" / "stage_log.jsonl").exists() else []:
        r = json.loads(line)
        if r.get("event") == "unit":
            unit_s.setdefault(r["marker"].split("/")[0], []).append(r["busy_s"])
    spp = lambda names: float(sum(np.mean(unit_s.get(x, [0.0])) for x in names))
    sec = lambda arm: cost[arm]["seconds_mean"] or 0.0
    clock = json.loads(Path(a.clock).read_text()) if Path(a.clock).exists() else dict(by_stage={})
    d = dict(share_elig=share, sd_paired=sd,
             gen_s_per_sample_sum_main=sum(sec(x) for x in ("P64", "G", "O0", "P32")),
             gen_s_per_sample_sum_ctrl=sec("Ind") + sec("TF"),
             score_s_per_prefix_main=spp(("P64", "G", "O0", "P32")), score_s_per_prefix_ctrl=spp(("Ind", "TF")), pc2_s=60.0,
             pilot_wall_s=float(clock["by_stage"].get("pilot", 0.0) + clock["by_stage"].get("score-pilot", 0.0)),
             g32=dict(n=len(g32), empty_or_padonly=int(sum(g32_empty)), near_uniform=int(sum(g32_nu))),
             g50=dict(n=len(g50), empty_or_padonly=int(sum(x["empty"] for x in g50)), near_uniform_only=int(sum(x["nu"] and not x["empty"] for x in g50))),
             det_plain=(int(sum(dp)), len(dp)), det_official=(int(sum(do)), len(do)), hookcheck=(int(sum(hc)), len(hc)),
             failed_units=failed_units, total_units=len(all_markers),
             guidance_failures=int(sum("guidance-acted" in f.get("error", "") for f in fails)))
    rules = design_rules(d)
    rep.update(cost=cost, counts=counts, inputs_to_rules=d, rules=rules,
               vlm=dict(calls=vlm_calls, seconds=vlm_s, s_per_call=(vlm_s / vlm_calls if vlm_calls else None)),
               telemetry=telemetry_summary(sorted((C.RUNS / "pilot").glob("telemetry-*.csv")) + sorted((C.RUNS / "score-pilot").glob("telemetry-*.csv"))),
               guidance_checks=[json.loads(f.read_text()).get("guidance") for f in sorted((gen / "pilot" / "G").glob("p*_e*.json"))
                                if json.loads(f.read_text()).get("guidance")][:32])
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(rep, indent=1, default=float), encoding="utf8")
    Path(a.n_conf_out).write_text(json.dumps(dict(n_generate=rules.get("n_generate", 0), n_conf_eligible=rules.get("n_conf_eligible", 0),
                                                  stop_reasons=rules["stop_reasons"], n_cap_generated=rules.get("n_cap_generated"),
                                                  share_eligible=rules["share_eligible"]), indent=1), encoding="utf8")
    print(json.dumps(rules, indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
