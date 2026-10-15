"""EXP-003 post-freeze descriptive supplement. EXPLORATORY, POST-FREEZE: nothing here was in the frozen analysis (card v0.3.2, gate audit
2026-10-15 open decisions 1, 3, 4, 6, 7). Reuses the frozen modules by import; modifies no frozen file and only READS confirmatory.json.

    C:/.../.venv-eval/Scripts/python.exe analysis/EXP-003-postfreeze/postfreeze.py
        -> R/runs/EXP-003/analysis/postfreeze.json   (and prints it)

R = the run worktree (data + frozen code). Items:
  1 guardrail (iv) near-uniform G images (and the other arms)      2 achieved MDE and power at the MEI, from the frozen sd and n_prefix
  3 placebo short-pool and dropped prefixes                        4 W3 composition shares and common-prefix contrast
  5 E3-H4 diversity with 95 percent cluster-bootstrap intervals    6 bootstrap B actually used versus the card's B
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
sys.dont_write_bytecode = True                      # leave no __pycache__ in the frozen directories

R = Path(r"C:\Users\Shlok\Downloads\Multi-Modality Language model\.claude\worktrees\dlm-discovery-resume-ca3357")
sys.path[:0] = [str(R), str(R / "analysis" / "EXP-003"), str(R / "analysis" / "EXP-001")]

import numpy as np                                                   # noqa: E402
from scipy.stats import norm                                         # noqa: E402
from PIL import Image                                                # noqa: E402

import frozen_analysis as FA                                         # noqa: E402  (frozen)
import nounkey                                                       # noqa: E402  (frozen)
import stats as S                                                    # noqa: E402  (frozen)
import tables as T                                                   # noqa: E402  (frozen)
from exp003 import config as C                                       # noqa: E402  (frozen)
from exp003.units import load_pool_items                             # noqa: E402  (frozen)

ARMS = ("P64", "G", "O0", "P32")
CONF = R / "runs" / "EXP-003" / "analysis" / "confirmatory.json"
OUT = R / "runs" / "EXP-003" / "analysis" / "postfreeze.json"
B_CARD = 10000                      # card section 7
SEED_H4 = 5304                      # task / card seed family (5301 cross, 5302 placebo, 5303 PC-2)
LABEL = "exploratory, post-freeze"
NU_THR = 6.0                        # pixel-SD threshold, EXP-001 PG-1 / card 9.2 / D0018 (6)
W3_MIN_COMMON = 20                  # NOT in the card (the card states no minimum for W3); this script's own threshold, stated in the output


# ------------------------------------------------------------------------------------------------------------------ 1 guardrail iv
def near_uniform_block(bundles):
    out = {}
    for arm in ARMS:
        flags_stored, sd_png, n_files = [], [], 0
        for p in range(len(bundles[arm][0])):
            f = T.score_dir("main", arm) / f"p{p:03d}.json"
            if f.exists():
                js = json.loads(f.read_text(encoding="utf-8"))
                if js.get("ok") and "near_uniform" in js:
                    flags_stored += [bool(x) for x in js["near_uniform"]]
                    n_files += 1
            for s in bundles[arm][0][p]:
                if s is not None:
                    sd_png.append(float(np.asarray(Image.open(s["png"]).convert("L"), dtype=np.float64).std()))
        sd = np.array(sd_png)
        out[arm] = dict(n_images_png=int(len(sd)), n_score_files=n_files, n_flags_stored=len(flags_stored),
                        n_near_uniform_stored=int(sum(flags_stored)),
                        fraction_stored=float(np.mean(flags_stored)) if flags_stored else None,
                        n_near_uniform_recomputed_png=int((sd < NU_THR).sum()), fraction_recomputed_png=float((sd < NU_THR).mean()),
                        pixel_sd_min=float(sd.min()), pixel_sd_median=float(np.median(sd)), pixel_sd_mean=float(sd.mean()),
                        smallest_5_pixel_sd=[float(x) for x in np.sort(sd)[:5]],
                        stored_equals_recomputed=bool(int(sum(flags_stored)) == int((sd < NU_THR).sum())))
    return dict(label=LABEL,
                definition=f"fraction of generated images (2 seeds x prefixes, no filtering) with grey-level pixel SD < {NU_THR} (PIL convert('L'), float64 std over all pixels); "
                           "guardrail (iv) passes when G's fraction is at most 0.15 (card 4.4)",
                threshold=0.15, G_passes_guardrail_iv=bool(out["G"]["fraction_stored"] <= 0.15 and out["G"]["fraction_recomputed_png"] <= 0.15),
                sources=["R/runs/EXP-003/score/main/<arm>/p*.json (field near_uniform, written by analysis/EXP-003/score.py near_uniform())",
                         "R/runs/EXP-003/gen/{m1,m2,m3}/<arm>/p*_e*.png (recomputed here with the same formula)"],
                per_arm=out)


# ------------------------------------------------------------------------------------------------------------------ 2 MDE and power
def mde_block(conf):
    z_a = norm.ppf(0.975)
    rows = {}
    for key in ("delta1", "delta2a", "delta2b"):
        c = conf["confirmatory"][key]
        se, n = c["sd"], c["n_prefix"]
        pw = lambda delta, a=z_a: float(norm.cdf(delta / se - a) + norm.cdf(-delta / se - a))
        rows[key] = dict(name=c["name"], n_prefix=n, sd_bootstrap_SE=se, implied_per_prefix_sd=se * np.sqrt(n), d_observed=c["d"],
                         mde_power_0p80=float((z_a + norm.ppf(0.80)) * se), mde_power_0p90=float((z_a + norm.ppf(0.90)) * se),
                         power_at_MEI_0p10=pw(0.10), power_at_observed_d=pw(abs(c["d"])),
                         note=("Holm second step uses alpha 0.05/2 = 0.025 for the smaller p; these figures use two-sided 0.05 as the card's Delta1 line does" if key != "delta1" else None))
    return dict(label=LABEL, source="R/runs/EXP-003/analysis/confirmatory.json confirmatory.<contrast>.{sd, n_prefix, d} (read only); sd = SD of the B = 10,000 bootstrap replicates of the contrast = its standard error",
                formula="card section 7: MDE_power = (z_{1-alpha/2} + z_{power}) x SE, alpha = 0.05 two-sided, z_{0.975} = 1.95996, z_{0.80} = 0.84162, z_{0.90} = 1.28155 "
                        "(the card's own line: SE 0.0367 -> MDE 0.119 at power 0.90 and 0.103 at 0.80); power at a true effect delta = Phi(delta/SE - z_{0.975}) + Phi(-delta/SE - z_{0.975}); "
                        "Wald/normal approximation, SE taken as known",
                card_planning_values=dict(se=0.0367, mde_0p90=0.119, mde_0p80=0.103, sigma_d_planning=0.45, n_planning=150),
                per_contrast=rows)


# ------------------------------------------------------------------------------------------------------------------ 3 placebo
def placebo_block(bundles, conf):
    out = {}
    for arm in ARMS:
        smp, sets, plac, recs = bundles[arm]
        L = S.arm_L(recs)
        Lp = S.arm_L(recs, "pown", "psib")
        n = len(recs)
        ok = [p for p in range(n) if sets[p] is not None]
        elig = [p for p in ok if not np.isnan(L[p])]
        short_any = [p for p in ok if plac[p] is not None and any(plac[p]["short"])]
        short_both = [p for p in ok if plac[p] is not None and all(plac[p]["short"])]
        seed_short = sum(int(sum(plac[p]["short"])) for p in ok if plac[p] is not None)
        empty_side = [p for p in elig if min(len(plac[p]["PL"][0]), len(plac[p]["PL"][1])) == 0]          # eligible for Lambda_b, empty placebo side
        elig_plac = [p for p in ok if not np.isnan(Lp[p])]
        pool_empty_seed = sum(int(len(plac[p]["PL"][e]) == 0 and len(sets[p]["D"][e]) > 0) for p in ok for e in (0, 1))
        fro = conf["arms"][arm]
        out[arm] = dict(n_prefix=n, n_prefix_both_seeds_ok=len(ok), n_eligible_lambda_b=len(elig),
                        n_prefix_with_short_placebo_pool_any_seed=len(short_any), n_prefix_short_both_seeds=len(short_both),
                        n_seed_units_short=int(seed_short),
                        n_short_among_lambda_b_eligible=int(sum(1 for p in short_any if p in set(elig))),
                        n_seed_units_with_discordant_nouns_but_empty_placebo=int(pool_empty_seed),
                        n_dropped_from_lambda_b_plac_among_eligible=len(empty_side),
                        n_eligible_lambda_b_plac=len(elig_plac),
                        n_eligible_in_plac_but_not_lambda_b=int(len(set(elig_plac) - set(elig))),
                        frozen_check=dict(n_eligible_frozen=fro["n_eligible"], placebo_n_eligible_frozen=fro.get("placebo_n_eligible"),
                                          recomputed_matches=bool(fro["n_eligible"] == len(elig) and fro.get("placebo_n_eligible") == len(elig_plac)),
                                          dropped_equals_eligible_minus_plac_eligible=bool(len(empty_side) == len(elig) - len(elig_plac))))
    return dict(label=LABEL,
                definition="IMPLEMENTATION.md section 5 item 3 / D0018 (3): placebo pool = both seeds' discordant nouns of the seed-5302 derangement partner minus the prefix's own keys; "
                           "if smaller than |D_pe| all of it is used (flag short = len(placebo_e) < len(D_e), per seed); a prefix with an empty placebo side (either seed) is not eligible for Lambda_b^plac. "
                           "short counts: prefixes with the flag set for at least one seed (all prefixes with both seeds generated); dropped: prefixes eligible for Lambda_b but not for Lambda_b^plac",
                sources=["analysis/EXP-003/tables.py placebo_sets / arm_bundle (frozen, imported; rebuilt from runs/EXP-003/gen)", "runs/EXP-003/score/main/*/p*.json (scores)",
                         "runs/EXP-003/analysis/confirmatory.json arms.*.{n_eligible, placebo_n_eligible} (read only, for the cross-check)"],
                per_arm=out)


# ------------------------------------------------------------------------------------------------------------------ 4 W3 composition
def w3_block(bundles, conf, coco):
    shares, lam, Lc = {}, {}, {}
    for arm in ARMS:
        recs = bundles[arm][3]
        Lc[arm] = FA.lam_coco(recs, coco)
        tot = sum(len(x) for r in recs if r.get("ok") for x in r["N"])
        hit = sum(nounkey.key(n) in coco for r in recs if r.get("ok") for x in r["N"] for n in x)
        pc = S.lam_parts(Lc[arm])
        shares[arm] = dict(coco_noun_share=hit / max(tot, 1), n_nouns=tot, n_coco_nouns=hit, n_eligible_prefix_lambda_b_coco=int(pc[1].sum()),
                           lambda_b_coco=S.point(pc) if pc[1].sum() else None,
                           frozen_share_check=conf["arms"][arm].get("coco_noun_share"), frozen_lambda_b_coco=conf["arms"][arm].get("lambda_b_coco_nouns"))
    parts = S.contrast_parts(Lc["G"], Lc["P64"])
    n_common = int(parts[1].sum())
    res = dict(n_common_eligible_G_P64=n_common)
    if n_common > 0:
        rep = S.contrast_report("W3 COCO-noun Lambda_b(G) - Lambda_b(P64)", parts, B_CARD, SEED_H4 + 100)
        res.update(d=rep["d"], pct95=rep["pct95"], pct90=rep["pct90"], bca90=rep["bca90"], B=rep["B"], sd=rep["sd"])
        res["w3_trigger_90_upper_limit_below_0p05"] = bool(rep["pct90"][1] < 0.05)
    est = n_common >= W3_MIN_COMMON
    res["estimable"] = est
    res["label"] = "estimable" if est else "not estimable"
    return dict(label=LABEL,
                definition="card 4.3 item 8 and 4.5 W3: composition shares = share of each arm's completion nouns whose noun key is on analysis/EXP-003/coco_object_nouns.txt (frozen); "
                           "sensitivity = Lambda_b recomputed on those nouns only (frozen_analysis.lam_coco), contrast G - P64 on the prefixes eligible in BOTH arms "
                           "(card 4.2 prefix-set rule), percentile cluster bootstrap B = 10,000. W3 wording is added only if the 90 percent upper limit is below 0.05",
                minimum_rule=f"the card states NO minimum eligible-prefix count for the W3 contrast; this script labels it 'not estimable' when fewer than {W3_MIN_COMMON} prefixes are eligible in both arms "
                             "(own threshold, not the card's; the count 2 reported by the gate audit is far below any reasonable threshold)",
                composition_shares_and_per_arm_sensitivity=shares, contrast_G_minus_P64=res)


# ------------------------------------------------------------------------------------------------------------------ 5 E3-H4 diversity
def _ent(c):
    c = c[c > 0]
    p = c / c.sum()
    return float(-(p * np.log(p)).sum())


def diversity_block(bundles, B=B_CARD, seed=SEED_H4, frac=0.8, n_sub_point=100):
    # words exactly as the frozen analysis (lower-cased completion text split on whitespace), per prefix (both seeds together = cluster)
    vocab, wid = {}, lambda w: vocab.setdefault(w, len(vocab))
    bvocab, bid = {}, lambda b: bvocab.setdefault(b, len(bvocab))
    W, Bg, jac = {}, {}, {}
    for arm in ARMS:
        smp, sets, _, _ = bundles[arm]
        wp, bp, jp = [], [], []
        for p, pair in enumerate(smp):
            if pair[0] is None or pair[1] is None:
                wp.append(np.array([], int)); bp.append(np.array([], int)); jp.append(np.nan)
                continue
            ws, bs = [], []
            for s in pair:
                toks = s["comp"].lower().split()
                ws += [wid(w) for w in toks]
                bs += [bid(b) for b in zip(toks[:-1], toks[1:])]                      # bigrams inside one completion only
            wp.append(np.array(ws, int)); bp.append(np.array(bs, int))
            a, b = nounkey.keys(sets[p]["N"][0]), nounkey.keys(sets[p]["N"][1])
            jp.append(len(a & b) / len(a | b) if (a | b) else np.nan)
        W[arm], Bg[arm], jac[arm] = wp, bp, np.array(jp, float)
    n = len(W["G"])
    Vw, Vb = len(vocab), len(bvocab)
    tot_w = {a: int(sum(len(x) for x in W[a])) for a in ARMS}
    tot_b = {a: int(sum(len(x) for x in Bg[a])) for a in ARMS}
    Tw, Tb = int(frac * min(tot_w.values())), int(frac * min(tot_b.values()))

    def stat(wcat, bcat, g):
        ew = np.bincount(g.permutation(wcat)[:Tw], minlength=Vw)
        db = np.bincount(g.permutation(bcat)[:Tb], minlength=Vb)
        return _ent(ew), float((db > 0).sum() / Tb)

    # point estimates: mean over 100 subsamples of the ORIGINAL pooled words
    gp = np.random.default_rng([seed, 1])
    point = {}
    for a in ARMS:
        wc, bc = np.concatenate(W[a]), np.concatenate(Bg[a])
        v = np.array([stat(wc, bc, gp) for _ in range(n_sub_point)])
        point[a] = dict(unigram_entropy_nats=float(v[:, 0].mean()), distinct2=float(v[:, 1].mean()), T_words=Tw, T_bigrams=Tb,
                        words_total=tot_w[a], bigrams_total=tot_b[a], vocab_words_used=int(len(np.unique(wc))))
    # frozen-definition comparison (T_ref = smallest arm total, 100 subsamples, mean) for the entropy only
    gf = np.random.default_rng([seed, 2])
    tref = min(tot_w.values())
    for a in ARMS:
        wc = np.concatenate(W[a])
        point[a]["unigram_entropy_nats_at_frozen_T_ref"] = float(np.mean([_ent(np.bincount(gf.permutation(wc)[:tref], minlength=Vw)) for _ in range(100)]))
        point[a]["T_ref_frozen"] = tref
    # bootstrap: same resampled prefix indices in every arm; one subsample per arm per replicate
    gi, gs = np.random.default_rng([seed, 0]), np.random.default_rng([seed, 3])
    names = [f"{a}.{k}" for a in ARMS for k in ("H", "D2", "J")]
    th = np.empty((B, len(names)))
    redraws, done = 0, 0
    while done < B:
        idx = gi.integers(0, n, n)
        cats = {a: (np.concatenate([W[a][i] for i in idx]), np.concatenate([Bg[a][i] for i in idx])) for a in ARMS}
        if min(len(c[0]) for c in cats.values()) < Tw or min(len(c[1]) for c in cats.values()) < Tb:
            redraws += 1
            continue
        row = []
        for a in ARMS:
            h, d2 = stat(cats[a][0], cats[a][1], gs)
            jv = jac[a][idx]
            row += [h, d2, float(np.nanmean(jv)) if np.isfinite(jv).any() else np.nan]
        th[done] = row
        done += 1
    col = {nm: th[:, i] for i, nm in enumerate(names)}
    ci = lambda v: [float(np.quantile(v, .025)), float(np.quantile(v, .975))]
    # the resampled pools contain duplicated prefixes, which lowers the rarefied entropy / distinct-2 of a REPLICATE below the point value for a
    # single arm (the point lies outside the raw percentile interval); the bias-centred interval point + (percentile - bootstrap mean) removes that shift
    cc = lambda v, pt: [float(pt + np.quantile(v, .025) - v.mean()), float(pt + np.quantile(v, .975) - v.mean())]
    res = {}
    for a in ARMS:
        res[a] = dict(unigram_entropy_nats=dict(point=point[a]["unigram_entropy_nats"], pct95_bias_centred=cc(col[f"{a}.H"], point[a]["unigram_entropy_nats"]), pct95_raw=ci(col[f"{a}.H"]), boot_mean=float(col[f"{a}.H"].mean())),
                      distinct2=dict(point=point[a]["distinct2"], pct95_bias_centred=cc(col[f"{a}.D2"], point[a]["distinct2"]), pct95_raw=ci(col[f"{a}.D2"]), boot_mean=float(col[f"{a}.D2"].mean())),
                      sibling_noun_jaccard=dict(point=float(np.nanmean(jac[a])), pct95_bias_centred=cc(col[f"{a}.J"], float(np.nanmean(jac[a]))), pct95_raw=ci(col[f"{a}.J"]), n_prefix_defined=int(np.isfinite(jac[a]).sum())),
                      detail=point[a])
    diff = {}
    for other in ("P64", "P32", "O0"):
        if True:
            for key, k in (("unigram_entropy_nats", "H"), ("distinct2", "D2"), ("sibling_noun_jaccard", "J")):
                v = col[f"G.{k}"] - col[f"{other}.{k}"]
                pt = res["G"][key]["point"] - res[other][key]["point"]
                c_ = cc(v, pt)
                diff[f"G_minus_{other}.{key}"] = dict(point=pt, pct95_bias_centred=c_, pct95_raw=ci(v), excludes_0_bias_centred=bool(not (c_[0] <= 0 <= c_[1])),
                                                      excludes_0_raw=bool(not (ci(v)[0] <= 0 <= ci(v)[1])), boot_mean=float(v.mean()))
    return dict(label=LABEL + "; descriptive only (card 4.3 item 7, E3-H4), no decision rule, no multiplicity correction",
                definition=("cluster = prefix (both seeds together); B = 10,000, seed 5304 (default_rng([5304,0]) draws the prefix indices, the SAME in every arm; default_rng([5304,3]) the subsamples); "
                            "percentile 95 percent intervals, reported raw (pct95_raw) and bias-centred (pct95_bias_centred = point + percentile - bootstrap mean; this is the one to quote, because duplicated prefixes in a resampled pool lower the rarefied entropy and distinct-2 of every replicate, so for a single arm the raw interval does not contain the point). Words = lower-cased completion text split on whitespace, as the frozen analysis. "
                            f"Unigram entropy = plug-in, nats, of exactly T_words = {Tw} words drawn without replacement from the arm's pooled words (0.8 x the smallest arm total {min(tot_w.values())}; "
                            "removes the sample-size bias; point = mean of 100 subsamples of the original pool, replicate = one subsample of the resampled pool; a replicate whose resampled pool is smaller than T is redrawn). "
                            f"Distinct-2 = distinct bigrams / T_bigrams = {Tb} bigrams drawn without replacement (0.8 x the smallest arm total {min(tot_b.values())}); bigrams are formed WITHIN each completion, never across completions. "
                            "Sibling noun Jaccard = mean over prefixes of |K0 & K1| / |K0 | K1| of the completion noun-key sets (frozen definition 4.3 item 7a; prefixes with both sets empty are skipped). "
                            "E3-H4 direction: G lower diversity than P64 = Jaccard higher, entropy lower; a claim needs BOTH 95 percent intervals to exclude 0."),
                caveats=["bootstrap pools contain duplicated prefixes, so the without-replacement subsample entropy is slightly lower than at the point estimate (compare boot_mean with point); the raw interval is shifted accordingly and the bias-centred interval corrects the shift but is a normal-shift approximation, not BCa",
                         "the frozen confirmatory.json diversity.distinct2 forms bigrams from a shuffled word subsample (np.random choice order), so it is not comparable with the distinct2 here and should not be quoted",
                         "frozen entropy used T_ref = smallest arm total; point.unigram_entropy_nats_at_frozen_T_ref reproduces that definition (with this script's seed) for comparison"],
                B=B, seed=seed, redraws=redraws, T_words=Tw, T_bigrams=Tb, per_arm=res, G_minus_other=diff,
                frozen_confirmatory_for_comparison={a: dict(unigram_entropy=conf_div(a, "unigram_entropy"), distinct2=conf_div(a, "distinct2")) for a in ARMS})


_CONF = None


def conf_div(arm, key):
    return _CONF["diversity"][arm][key]


# ------------------------------------------------------------------------------------------------------------------ 6 bootstrap B used
def b_block(conf):
    found = []

    def walk(o, path):
        if isinstance(o, dict):
            if "B" in o and isinstance(o["B"], int) and "name" in o:
                found.append(dict(path=path, name=o["name"], B=o["B"], redraws=o.get("redraws"), rerun_B100000=("rerun_B100000" in o),
                                  p=o.get("p")))
            for k, v in o.items():
                walk(v, f"{path}.{k}" if path else k)

    walk(conf["confirmatory"], "confirmatory")
    for row in found:
        row["card_B"] = B_CARD
        row["matches_card"] = bool(row["B"] == B_CARD)
    code = [
        dict(quantity="per-arm Lambda_b, Lambda_b^plac, Lambda_d (arms.*.lambda_*_pct95)", B=FA.B_MAIN, source="frozen_analysis.py arm_summary(B=B_MAIN)"),
        dict(quantity="quality-matched sensitivity: matched-half Lambda_b bootstrap", B=4000, source="frozen_analysis.py arm_summary: quality_matched(B=min(B, 4000))"),
        dict(quantity="quality-matched slope bootstrap", B=2000, source="stats.py quality_matched: range(min(B, 2000))"),
        dict(quantity="confirmatory contrasts delta1, delta2a, delta2b, G-P32, P64-P32", B=FA.B_MAIN, source="frozen_analysis.py analyse"),
        dict(quantity="exact-surface Delta1, Delta1 net of placebo, CLIP completion-only sibling link G - P64 (W1)", B=5000, source="frozen_analysis.py analyse: min(B, 5000)"),
        dict(quantity="B = 100,000 rerun when p within 2 sqrt(p(1-p)/B) of the threshold", B=100000, source="frozen_analysis.py analyse (needs_rerun)"),
    ]
    return dict(label=LABEL, card_B="card section 7: percentile cluster bootstrap, B = 10,000 (rerun at B = 100,000 if p lies near its threshold)",
                source="R/runs/EXP-003/analysis/confirmatory.json: every object under 'confirmatory' with fields name and B (read only); the code-side B values are read from the frozen source",
                recorded_in_confirmatory_json=found, n_below_card_B=int(sum(not r["matches_card"] for r in found)),
                below_card=[dict(name=r["name"], B=r["B"]) for r in found if not r["matches_card"]],
                from_frozen_code=code,
                not_recorded_in_json=["the CLIP-based and exact-surface/net-of-placebo contrasts are the ones below the card's B (5,000); the quality-matched pieces use 4,000 and 2,000; Delta1, Delta2a, Delta2b, G-P32, P64-P32 and every per-arm interval use 10,000"])


# ------------------------------------------------------------------------------------------------------------------------- main
def main():
    global _CONF
    conf = json.loads(CONF.read_text(encoding="utf-8"))
    _CONF = conf
    n = json.loads((C.RUNS / "n_conf.json").read_text(encoding="utf-8"))["n_generate"]
    coco = {nounkey.key(w) for w in (R / "analysis" / "EXP-003" / "coco_object_nouns.txt").read_text(encoding="utf-8").split()}
    tools = T.Tools()
    items = load_pool_items("E3-MAIN")
    bundles = {a: T.arm_bundle("main", a, n, items, tools) for a in ARMS}
    out = dict(label=LABEL, script="analysis/EXP-003-postfreeze/postfreeze.py (resume-dlm-discovery-exp-003-334706 worktree)",
               frozen_inputs_read_only=["runs/EXP-003/analysis/confirmatory.json", "analysis/EXP-003/{frozen_analysis,stats,tables,nounkey}.py", "analysis/EXP-003/coco_object_nouns.txt",
                                        "runs/EXP-003/gen/{m1,m2,m3}", "runs/EXP-003/score/main", "runs/EXP-003/n_conf.json"],
               n_generated_prefixes=n,
               item1_guardrail_iv_near_uniform=near_uniform_block(bundles),
               item2_achieved_mde_and_power=mde_block(conf),
               item3_placebo_short_and_dropped=placebo_block(bundles, conf),
               item4_w3_composition=w3_block(bundles, conf, coco),
               item5_e3h4_diversity=diversity_block(bundles),
               item6_bootstrap_B_used=b_block(conf))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    txt = json.dumps(out, indent=1, default=lambda x: x.tolist() if hasattr(x, "tolist") else str(x))
    OUT.write_text(txt, encoding="utf-8")
    print(txt)
    print("wrote", OUT, file=sys.stderr)


if __name__ == "__main__":
    main()
