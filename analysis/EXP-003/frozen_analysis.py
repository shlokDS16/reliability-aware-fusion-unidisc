"""Frozen analysis of EXP-003 (card v0.3.2 sections 4, 5, 7). Eval venv, CPU. Hashed before the first main-stage sample is scored.

    python analysis/EXP-003/frozen_analysis.py main            -> runs/EXP-003/analysis/confirmatory.json   (run by the ORCHESTRATOR)
    python analysis/EXP-003/frozen_analysis.py controls        -> runs/EXP-003/ctrl/controls_decision.json  (run by the driver, stop rule 9.4)
    python analysis/EXP-003/frozen_analysis.py pilot-scrambled -> digest only (end-to-end freeze with arm labels scrambled; prints no number)

`analyse` is a pure function of the arm bundles (tables.arm_bundle) and the CLIP files; the confirmatory numbers are Delta1 (G - P64),
Delta2a (G - O0), Delta2b (O0 - P32) of the seed-balanced link Lambda_b with the outcome classes of section 5, and everything of 4.3 that
does not need a further model call.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(HERE), str(ROOT / "analysis" / "EXP-001")]

import nounkey                                                      # noqa: E402
import stats as S                                                   # noqa: E402
from exp003 import config as C                                      # noqa: E402

B_MAIN = 10000
SEED = 20261015


# --------------------------------------------------------------------------------------------------------------------- helpers
def lam_exact(recs):
    """Sensitivity: discordance by the exact lower-cased surface instead of the key (uses the all-noun presence arrays)."""
    L = []
    for r in recs:
        if not r.get("ok"):
            L.append(np.nan)
            continue
        own, sib = [], []
        for e in (0, 1):
            sibset = {nounkey.exact(n) for n in r["N"][1 - e]}
            m = np.array([nounkey.exact(n) not in sibset for n in r["N"][e]], bool)
            own.append(r["all_own"][e][m] if len(m) else r["all_own"][e])
            sib.append(r["all_sib"][e][m] if len(m) else r["all_sib"][e])
        L.append(S.L_p(own, sib))
    return np.array(L)


def lam_all(recs):
    """All-noun link (descriptive 4.3 item 2): seed-balanced matched minus sibling over every completion noun."""
    return np.array([S.L_p(r["all_own"], r["all_sib"]) if r.get("ok") else np.nan for r in recs])


def lam_coco(recs, coco_set):
    L = []
    for r in recs:
        if not r.get("ok"):
            L.append(np.nan)
            continue
        own, sib = [], []
        for e in (0, 1):
            m = np.array([nounkey.key(n) in coco_set for n in r["D"][e]], bool)
            own.append(r["own"][e][m] if len(m) else r["own"][e])
            sib.append(r["sib"][e][m] if len(m) else r["sib"][e])
        L.append(S.L_p(own, sib))
    return np.array(L)


def or_rule(recs):
    """OR-rule rates m, s, s_sp (EXP-001 4.4, one cross-prefix derangement): a sample counts 1 if any of its completion nouns is present."""
    m = s = sp = n = 0.0
    for r in recs:
        if not r.get("ok") or "all_cross" not in r:
            continue
        for e in (0, 1):
            if len(r["N"][e]) == 0:
                n += 1
                continue
            m += float(r["all_own"][e].max()); sp += float(r["all_sib"][e].max()); s += float(r["all_cross"][e].max()); n += 1
    return dict(m=m / max(n, 1), s=s / max(n, 1), s_sp=sp / max(n, 1), m_minus_s_sp=(m - sp) / max(n, 1), n_samples=int(n))


def per_noun_rates(recs):
    own = np.concatenate([x for r in recs if r.get("ok") for x in r["all_own"]] or [np.array([])])
    sib = np.concatenate([x for r in recs if r.get("ok") for x in r["all_sib"]] or [np.array([])])
    cr = np.concatenate([x for r in recs if r.get("ok") and "all_cross" in r for x in r["all_cross"]] or [np.array([])])
    return dict(matched=float(own.mean()) if len(own) else None, same_prefix=float(sib.mean()) if len(sib) else None,
                cross_prefix=float(cr.mean()) if len(cr) else None, n_nouns=int(len(own)))


def arm_summary(arm, bundle, B, seed, coco_set):
    smp, sets, plac, recs = bundle
    L = S.arm_L(recs)
    parts = S.lam_parts(L)
    res = dict(n_prefix=len(recs), n_eligible=int(parts[1].sum()), share_eligible=float(parts[1].mean()))
    if parts[1].sum() > 0:
        th, red = S.bootstrap([parts], B, seed)
        d = S.point(parts)
        res.update(lambda_b=d, lambda_b_pct95=S.percentile_ci(th[:, 0]), lambda_b_bca95=S.bca_ci(th[:, 0], d, S.jackknife(parts)),
                   lambda_b_pct90=S.percentile_ci(th[:, 0], .90), lambda_b_bca90=S.bca_ci(th[:, 0], d, S.jackknife(parts), .90), redraws=red)
        nm, dn = S.arm_ratio(recs)
        thd, _ = S.bootstrap([(nm, dn)], B, seed + 1)
        res.update(lambda_d=S.point((nm, dn)), lambda_d_pct95=S.percentile_ci(thd[:, 0]))
        Lp = S.arm_L(recs, "pown", "psib")
        pp = S.lam_parts(Lp)
        if pp[1].sum() > 0:
            thp, _ = S.bootstrap([pp], B, seed + 2)
            ci = S.percentile_ci(thp[:, 0])
            res.update(lambda_b_placebo=S.point(pp), placebo_pct95=ci, placebo_n_eligible=int(pp[1].sum()), nc2_pass=S.nc_pass(ci),
                       lambda_b_net_of_placebo=res["lambda_b"] - S.point(pp))
        for nm_, f in (("exact_surface", lam_exact), ("all_noun", lam_all)):
            pe = S.lam_parts(f(recs))
            res[f"lambda_{nm_}"] = S.point(pe) if pe[1].sum() else None
        if coco_set:
            pc = S.lam_parts(lam_coco(recs, coco_set))
            res["lambda_b_coco_nouns"] = S.point(pc) if pc[1].sum() else None
            tot = sum(len(x) for r in recs if r.get("ok") for x in r["N"])
            res["coco_noun_share"] = sum(nounkey.key(n) in coco_set for r in recs if r.get("ok") for x in r["N"] for n in x) / max(tot, 1)
        res["quality_matched"] = S.quality_matched(L, [r.get("iqa") if r.get("ok") else None for r in recs], B=min(B, 4000), seed=seed + 3)
    res.update(or_rule=or_rule(recs), per_noun=per_noun_rates(recs))
    flat = [s for pair in smp for s in pair if s is not None]
    res["completion"] = dict(n=len(flat), length_mean=float(np.mean([s["cend"].completion_len for s in flat])) if flat else None,
                             empty_rate=float(np.mean([s["cend"].completion_len == 0 for s in flat])) if flat else None,
                             nouns_per_sample=float(np.mean([len(s["nouns"]) for s in flat])) if flat else None,
                             discordant_total=int(sum(len(x) for s in sets if s for x in s["D"])),
                             discordant_share=float(sum(len(x) for s in sets if s for x in s["D"]) / max(sum(len(x) for s in sets if s for x in s["N"]), 1)),
                             debris_share=float(np.mean([s["cend"].debris_share for s in flat])) if flat else None,
                             e2_share=float(np.mean([s["cend"].e2_set for s in flat])) if flat else None,
                             words=[w for s in flat for w in s["comp"].lower().split()])
    jac = []
    for s in sets:
        if s:
            a, b = nounkey.keys(s["N"][0]), nounkey.keys(s["N"][1])
            jac.append(len(a & b) / len(a | b) if (a | b) else np.nan)
    res["sibling_noun_jaccard"] = float(np.nanmean(jac)) if jac else None
    cs = [s["commit_step"] for s in flat if s["commit_step"] is not None]
    if cs:
        from exp003.official import tail_vs_image_order
        o = [tail_vs_image_order(c.astype(float) / max(float(c.max()), 1.0)) for c in cs]
        res["commit_order"] = {k: float(np.mean([x[k] for x in o])) for k in o[0]}
    return res, L


def clip_link(scope, arm, n, root, which="comp"):
    """Per-prefix CLIP sibling link 100 [cos(x_i, c_i) - cos(x_sib, c_i)] averaged over the two seeds; NaN when the file is missing."""
    out = np.full(n, np.nan)
    for p in range(n):
        f = Path(root) / scope / arm / f"p{p:03d}.npz"
        if f.exists():
            z = np.load(f)
            I, Tt = z["img"], z[which]
            out[p] = 100.0 * float(np.mean([I[e] @ Tt[e] - I[1 - e] @ Tt[e] for e in (0, 1)]))
    return out


def diversity(arm_res, words_by_arm):
    t_ref = min(len(w) for w in words_by_arm.values())
    g = np.random.default_rng(SEED)
    out = {}
    for arm, w in words_by_arm.items():
        H, D2 = [], []
        for _ in range(100):
            sub = [w[i] for i in g.choice(len(w), t_ref, replace=False)]
            _, c = np.unique(sub, return_counts=True)
            pr = c / c.sum()
            H.append(float(-(pr * np.log(pr)).sum()))
            bg = list(zip(sub[:-1], sub[1:]))
            D2.append(len(set(bg)) / max(len(bg), 1))
        out[arm] = dict(unigram_entropy=float(np.mean(H)), distinct2=float(np.mean(D2)), t_ref=t_ref)
    return out


def analyse(bundles: dict, B=B_MAIN, seed=SEED, coco_set=None, score_root=None, scope="main", n=None):
    arms = {}
    Ls = {}
    for arm, b in bundles.items():
        arms[arm], Ls[arm] = arm_summary(arm, b, B, seed, coco_set)
    words = {a: arms[a]["completion"].pop("words") for a in arms}
    res = dict(arms=arms, diversity=diversity(arms, words))
    need = {"G", "P64", "O0", "P32"}
    if need <= set(Ls):
        conf = {}
        c1 = S.contrast_report("Delta1 = Lambda_b(G) - Lambda_b(P64)", S.contrast_parts(Ls["G"], Ls["P64"]), B, seed + 10)
        c2a = S.contrast_report("Delta2a = Lambda_b(G) - Lambda_b(O0)", S.contrast_parts(Ls["G"], Ls["O0"]), B, seed + 11)
        c2b = S.contrast_report("Delta2b = Lambda_b(O0) - Lambda_b(P32)", S.contrast_parts(Ls["O0"], Ls["P32"]), B, seed + 12)
        for c, (a_, b_), th in ((c1, ("G", "P64"), 0.05), (c2a, ("G", "O0"), 0.025), (c2b, ("O0", "P32"), 0.025)):
            if S.needs_rerun(c["p"], th, c["B"]) or S.needs_rerun(c["p"], 0.05, c["B"]):
                big = S.contrast_report(c["name"], S.contrast_parts(Ls[a_], Ls[b_]), 100000, 777 + int(th * 1000))
                c["rerun_B100000"] = dict(p=big["p"], seed=777 + int(th * 1000), pct95=big["pct95"])
                c["p"] = big["p"]
        c1["class"] = S.outcome_class(c1["d"], c1["pct95"], c1["bca95"], c1["p"], c1["pct90"], c1["bca90"])
        primary_rejects = c1["p"] <= 0.05
        hp = S.holm({"2a": c2a["p"], "2b": c2b["p"]})
        for c, k in ((c2a, "2a"), (c2b, "2b")):
            c["p_holm"] = hp[k]
            c["holm_family_level"] = 0.05 if primary_rejects else None
            c["exploratory"] = not primary_rejects
            c["class"] = ("positive" if (hp[k] <= 0.05 and c["d"] > 0) else "reversed" if (hp[k] <= 0.05 and c["d"] < 0) else
                          "null (unadjusted 90 percent, no family-wise claim)" if (c["pct90"][0] > -.1 and c["pct90"][1] < .1 and c["bca90"][0] > -.1 and c["bca90"][1] < .1)
                          else "inconclusive")
        halved = dict(primary_at_0025=bool(c1["p"] <= 0.025), holm_at_0025={k: bool(v <= 0.025) for k, v in hp.items()})
        conf.update(delta1=c1, delta2a=c2a, delta2b=c2b, sensitivity_halved_levels=halved,
                    steps_matched_G_minus_P32=S.contrast_report("G - P32", S.contrast_parts(Ls["G"], Ls["P32"]), B, seed + 13),
                    plain_doubling_P64_minus_P32=S.contrast_report("P64 - P32", S.contrast_parts(Ls["P64"], Ls["P32"]), B, seed + 14),
                    identity=S.identity_four_arm(Ls["G"], Ls["P64"], Ls["O0"], Ls["P32"]),
                    delta1_net_of_placebo=None)
        # exact-surface sensitivity of Delta1
        conf["delta1_exact_surface"] = S.contrast_report("Delta1 exact surface", S.contrast_parts(lam_exact(bundles["G"][3]), lam_exact(bundles["P64"][3])), min(B, 5000), seed + 15)
        # Delta1 net of placebo: Lambda_b - Lambda_b^plac per arm
        netG = S.arm_L(bundles["G"][3]) - S.arm_L(bundles["G"][3], "pown", "psib")
        netP = S.arm_L(bundles["P64"][3]) - S.arm_L(bundles["P64"][3], "pown", "psib")
        conf["delta1_net_of_placebo"] = S.contrast_report("Delta1 net of placebo", S.contrast_parts(netG, netP), min(B, 5000), seed + 16)
        # guardrails (point estimates)
        g, p64 = arms["G"]["completion"], arms["P64"]["completion"]
        nu = None
        conf["guardrails"] = dict(
            i_length_ratio_within_0p5_2=bool(0.5 <= g["length_mean"] / max(p64["length_mean"], 1e-9) <= 2.0),
            ii_empty_rate_lt_0p25=bool(g["empty_rate"] < 0.25),
            iii_discordant_ge_0p4_of_P64=bool(g["discordant_total"] >= 0.4 * p64["discordant_total"]), near_uniform_fraction_G=nu)
        # CLIP sibling link (W1) and image-side diversity
        if score_root is not None:
            n = n or len(Ls["G"])
            cl = {a: clip_link(scope, a, n, score_root, "comp") for a in arms}
            clf = {a: clip_link(scope, a, n, score_root, "full") for a in arms}
            conf["clip_sibling_link_completion_only"] = {a: float(np.nanmean(v)) for a, v in cl.items()}
            conf["clip_sibling_link_full"] = {a: float(np.nanmean(v)) for a, v in clf.items()}
            conf["clip_sibling_link_G_minus_P64_completion_only"] = S.contrast_report(
                "CLIP sibling link comp-only G - P64", S.contrast_parts(cl["G"], cl["P64"]), min(B, 5000), seed + 17)
            conf["W1_concordant"] = bool(conf["clip_sibling_link_G_minus_P64_completion_only"]["pct90"][0] > 0)
            for a in arms:
                cos = []
                for p in range(n):
                    f = Path(score_root) / scope / a / f"p{p:03d}.npz"
                    if f.exists():
                        z = np.load(f)["img"]
                        cos.append(float(z[0] @ z[1]))
                arms[a]["image_sibling_cosine"] = float(np.mean(cos)) if cos else None
        res["confirmatory"] = conf
    return res


# ------------------------------------------------------------------------------------------------------------------------- CLI
def controls_decision(bundles, pc2_path, B=B_MAIN, seed=SEED):
    """Stop rule 9.4: NC-1 (Ind: 95 percent interval of Lambda_b contains 0, half-width <= 0.10); PC-1 (TF - Ind >= 0.10 with 90 percent
    lower limit > 0); PC-2 (guided T2I images: matched >= 0.60 and matched - cross >= 0.25)."""
    LI, LT = S.arm_L(bundles["Ind"][3]), S.arm_L(bundles["TF"][3])
    pi = S.lam_parts(LI)
    th, _ = S.bootstrap([pi], B, seed)
    ci = S.percentile_ci(th[:, 0])
    c = S.contrast_report("PC-1 Lambda_b(TF) - Lambda_b(Ind)", S.contrast_parts(LT, LI), B, seed + 1)
    pc2 = json.loads(Path(pc2_path).read_text()) if Path(pc2_path).exists() else None
    return dict(nc1=dict(lambda_b_ind=S.point(pi), pct95=ci, n_eligible=int(pi[1].sum()), passes=S.nc_pass(ci)),
                pc1=dict(contrast=c, passes=bool(c["d"] >= 0.10 and c["pct90"][0] > 0)),
                pc2=None if pc2 is None else {k: pc2[k] for k in ("matched", "cross", "matched_minus_cross", "passes", "n_nouns")},
                ind_per_noun=per_noun_rates(bundles["Ind"][3]), tf_per_noun=per_noun_rates(bundles["TF"][3]))


def _bundles(scope, arms, n, items, tools):
    import tables as T
    return {a: T.arm_bundle(scope, a, n, items, tools) for a in arms}


def _jsonable(o):
    return json.loads(json.dumps(o, default=lambda x: x.tolist() if hasattr(x, "tolist") else str(x)))


def main():
    which = sys.argv[1]
    import tables as T
    from exp003.units import load_pool_items
    tools = T.Tools()
    if which == "controls":
        b = _bundles("ctrl", ("Ind", "TF"), 48, load_pool_items("E3-CTRL"), tools)
        out = controls_decision(b, T.SCORE / "ctrl" / "pc2.json")
        p = C.RUNS / "ctrl" / "controls_decision.json"
    elif which == "pilot-scrambled":
        n = 16
        b = _bundles("pilot", ("P64", "G", "O0", "P32"), n, load_pool_items("E3-PILOT"), tools)
        perm = dict(zip(("P64", "G", "O0", "P32"), ("O0", "P32", "G", "P64")))          # fixed scramble of the arm labels
        res = analyse({perm[a]: v for a, v in b.items()}, B=500, seed=SEED, score_root=T.SCORE, scope="pilot", n=n)
        dig = hashlib.sha256(json.dumps(_jsonable(res), sort_keys=True).encode()).hexdigest()
        out = dict(digest_sha256=dig, ran_end_to_end=True, B=500, scrambled=True, note="numbers deliberately not stored (pilot firewall)")
        p = C.RUNS / "pilot" / "scrambled_analysis_digest.json"
    else:
        n = json.loads((C.RUNS / "n_conf.json").read_text())["n_generate"]
        coco = {nounkey.key(w) for w in Path(HERE / "coco_object_nouns.txt").read_text().split()} if (HERE / "coco_object_nouns.txt").exists() else None
        b = _bundles("main", ("P64", "G", "O0", "P32"), n, load_pool_items("E3-MAIN"), tools)
        out = analyse(b, coco_set=coco, score_root=T.SCORE, scope="main", n=n)
        p = C.RUNS / "analysis" / "confirmatory.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(_jsonable(out), indent=1), encoding="utf8")
    print("wrote", p)


if __name__ == "__main__":
    main()
