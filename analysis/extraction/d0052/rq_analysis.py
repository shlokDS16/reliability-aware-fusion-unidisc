"""RQ1-RQ6 estimates from the D0052 extraction sample (stratified; weights N_h / n_h).

    python -I analysis/extraction/d0052/rq_analysis.py

Inputs: analysis/extraction/d0052/sample.json and gate-manifest.json (strata), stage-a-manifest.json (ids left out of the
frame), batch-log.jsonl (usable sessions), the extractor records analysis/extraction/d0052/EA/<batch>/*.jsonl (the
pass-2 file when a session was returned once, else pass 1), and for the second-reader ids the adjudicated records in
analysis/extraction/d0052/EC/<batch>/*.jsonl when present (D0052: EC values are used for those ids).
Stratum sizes N_h are the gate strata minus the stage-a ids, recomputed here from the T1 decisions and text sizes with
the gate manifest's median (asserted against the manifest's stratum sizes before the exclusion).
Output: analysis/extraction/d0052/rq-results.json and rq-results.md; per-study QA table qa-table.jsonl.

Estimator: stratified proportion p = sum_h W_h p_h, W_h = N_h / N; variance sum_h W_h^2 (1 - n_h/N_h) p_h (1-p_h) / (n_h - 1);
95 percent interval by the Wilson formula on the effective sample size p(1-p)/var (Korn-Graubard style; for p_h in
{0, 1} the variance of that stratum uses p_h = 0.5/n_h to stay positive). Counts are unweighted numbers of studies.
Nothing is imputed: a field a record leaves null or 'not_stated' is counted as not stated.
QA scores follow EXTRACTION-PLAN-v0.2 s7.1 (low: unclear = no; high: unclear = yes). QA1 uses the text-only two-level
rule because the dated link check (QA1 d) needs web access, which D0051 rules out: 2 if a and b; 1 if a or c; else 0.
QA3 c (value rule determinable) is computed from census F2_codes (not NS, not NA, not ending '+NS').
QA8 from the claim list statuses (s7.3): NA if no checkable claim; 2 if every checkable claim is match or direction;
1 if at least one is and none contradicted; else 0. QA7 n is set by script when study_type is theory or benchmark or
an analysis-only study (s7.1 m5): here study_type in {theory, benchmark, analysis}.
"""
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "analysis/extraction/d0052"
SCR = ROOT / "analysis/screening"
MD = ROOT / "research/sources/md/fulltext-pymupdf"


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip().startswith("{")]


sample = json.load(open(D / "sample.json", encoding="utf-8"))
gate = json.load(open(D / "gate-manifest.json", encoding="utf-8"))
stage_a = set(json.load(open(D / "stage-a-manifest.json", encoding="utf-8"))["ids"])
STRATA = sample["strata"]                       # {G-long: [...27], G-mm: [...], G-short: [...]}
of_id = {i: h for h, ids in STRATA.items() for i in ids}

# ---------------------------------------------------------------- stratum sizes after the stage-a exclusion
t1 = {r["id"]: r for r in jl(SCR / "ft-t1/t1-decisions-all.jsonl")}
inc = [r for r in t1.values() if r["decision"] == "include"]
mm = [r["id"] for r in inc if r["i1"] in ("b", "ab")]
rc2 = [r["id"] for r in inc if r["i1"] == "a" and not r["nonlang_only"]]
med = gate["median_bytes"]
size = {i: (MD / f"{i}.txt").stat().st_size for i in rc2}
short = [i for i in rc2 if size[i] <= med]
long_ = [i for i in rc2 if size[i] > med]
full = {"G-mm": mm, "G-short": short, "G-long": long_}
for h, ids in full.items():
    assert len(ids) == gate["strata"][h]["size"], (h, len(ids), gate["strata"][h]["size"])
    assert set(STRATA[h]) <= set(ids), h
N_h = {h: len(set(ids) - stage_a) for h, ids in full.items()}
N = sum(N_h.values())

# ---------------------------------------------------------------- records
log = jl(D / "batch-log.jsonl") if (D / "batch-log.jsonl").exists() else []
usable = {}
for l in log:                                   # later lines (pass 2, reruns) override earlier ones
    if l["role"] == "EA":
        if l.get("usable"):
            usable[l["batch"]] = l
        else:
            usable.pop(l["batch"], None)
recs = {}
for b, l in usable.items():
    folder = D / "EA" / b
    files = sorted(folder.glob("EA-*.jsonl"))
    p2 = [f for f in files if f.stem.endswith("-pass2")]
    f = (p2 or [f for f in files if not f.stem.endswith("-pass2")])[0]
    for r in jl(f):
        recs[r["id"]] = r
ec_used = []
for f in sorted((D / "EC").glob("*/*.jsonl")) if (D / "EC").exists() else []:
    for r in jl(f):
        if r.get("id") in sample["second_reader_ids"]:
            recs[r["id"]] = r
            ec_used.append(r["id"])
done = {h: [i for i in STRATA[h] if i in recs] for h in STRATA}
n_h = {h: len(v) for h, v in done.items()}


# ---------------------------------------------------------------- estimator
def est(pred):
    """pred(record) -> True/False/None (None = not in the domain). Returns counts and weighted share with CI."""
    num, den, p_h, nn = 0, 0, {}, {}
    for h, ids in done.items():
        vals = [pred(recs[i]) for i in ids]
        vals = [v for v in vals if v is not None]
        nn[h] = len(vals)
        num += sum(vals)
        den += len(vals)
        p_h[h] = (sum(vals) / len(vals)) if vals else None
    hs = [h for h in p_h if p_h[h] is not None]
    if not hs:
        return {"count": 0, "of": 0, "share": None, "ci95": None}
    # domain estimation: weight each stratum by its estimated domain size N_h * nn_h / n_h
    Wd = {h: N_h[h] * nn[h] / n_h[h] for h in hs}
    Wt = sum(Wd.values())
    p = sum(Wd[h] / Wt * p_h[h] for h in hs)
    var = 0.0
    for h in hs:
        ph = p_h[h] if 0 < p_h[h] < 1 else (0.5 / nn[h] if p_h[h] == 0 else 1 - 0.5 / nn[h])
        if nn[h] > 1:
            var += (Wd[h] / Wt) ** 2 * (1 - nn[h] / max(Wd[h], nn[h])) * ph * (1 - ph) / (nn[h] - 1)
    if var <= 0:
        return {"count": num, "of": den, "share": round(p, 3), "ci95": None}
    neff = p * (1 - p) / var if 0 < p < 1 else den
    z = 1.959964
    c = (p + z * z / (2 * neff)) / (1 + z * z / neff)
    hw = z * math.sqrt(p * (1 - p) / neff + z * z / (4 * neff * neff)) / (1 + z * z / neff)
    return {"count": num, "of": den, "share": round(p, 3), "ci95": [round(max(0, c - hw), 3), round(min(1, c + hw), 3)],
            "by_stratum": {h: f"{sum(1 for i in done[h] if pred(recs[i]))}/{nn[h]}" for h in hs}}


def dist(field_fn, cats):
    return {c: est(lambda r, c=c: (None if field_fn(r) is None else (c in field_fn(r) if isinstance(field_fn(r), list) else field_fn(r) == c))) for c in cats}


def g(r, *path):
    x = r
    for p in path:
        if x is None:
            return None
        x = x.get(p) if isinstance(x, dict) else None
    return x


NUM = re.compile(r"[-+]?\d+(?:\.\d+)?")


def num(s):
    if s is None:
        return None
    m = NUM.search(str(s).replace(",", "").replace("−", "-"))
    return float(m.group()) if m else None


# ---------------------------------------------------------------- QA scoring (plan v0.2 s7.1)
def yes(v, high):
    return v == "yes" or (high and v == "unclear")


def qa_scores(r, high):
    q = r.get("qa") or {}
    s = lambda k: (q.get(k) or {}).get("sub") or {}
    out = {}
    a = s("QA1")
    out["QA1"] = 2 if yes(a.get("a"), high) and yes(a.get("b"), high) else 1 if yes(a.get("a"), high) or yes(a.get("c"), high) else 0
    a = s("QA2")
    out["QA2"] = 2 if yes(a.get("a"), high) and yes(a.get("b"), high) else 1 if any(yes(a.get(k), high) for k in "abc") else 0
    a = s("QA3")
    f2 = str(g(r, "census", "F2_codes") or "")
    c_ok = bool(f2) and f2 not in ("NS", "NA") and not f2.endswith("+NS")
    k = sum(yes(a.get(x), high) for x in ("a", "b", "d")) + c_ok
    out["QA3"] = 2 if k == 4 else 1 if k >= 2 else 0
    a = s("QA4")
    out["QA4"] = "NA" if a.get("n") == "yes" else 2 if yes(a.get("b"), high) else 1 if yes(a.get("a"), high) or yes(a.get("c"), high) else 0
    a = s("QA5")
    out["QA5"] = "NA" if a.get("n") == "yes" else 2 if yes(a.get("a"), high) else 1 if yes(a.get("b"), high) else 0
    a = s("QA6")
    out["QA6"] = ("NA" if a.get("n") == "yes" else 2 if yes(a.get("a"), high) and yes(a.get("c"), high)
                  and (yes(a.get("b"), high) or yes(a.get("d"), high)) else 1
                  if any(yes(a.get(x), high) for x in ("a", "c", "d")) else 0)
    a = s("QA7")
    st = g(r, "study", "study_type")
    out["QA7"] = ("NA" if st in ("theory", "benchmark", "analysis") or a.get("n") == "yes" else 2
                  if yes(a.get("a"), high) and yes(a.get("b"), high) else 1 if yes(a.get("a"), high) or yes(a.get("c"), high) else 0)
    cl = [c for c in (g(r, "claims", "list") or []) if c.get("status") not in (None, "not-checkable")]
    if not cl:
        out["QA8"] = "NA"
    else:
        ok = [c["status"] in ("match", "direction") for c in cl]
        bad = any(c["status"] == "contradicted" for c in cl)
        out["QA8"] = 2 if all(ok) else 1 if any(ok) and not bad else 0
    a = s("QA9")
    out["QA9"] = 2 if yes(a.get("a"), high) and yes(a.get("b"), high) else 1 if yes(a.get("a"), high) or yes(a.get("b"), high) else 0
    return out


# ---------------------------------------------------------------- contrast helpers
TRAIN = {"pretraining-recipe", "ar-initialisation", "sft", "rl", "distillation", "objective"}
INFER = {"steps-or-nfe", "tokens-per-step", "order-rule", "remasking", "cache", "block-or-parallel", "value-rule",
         "guidance", "gen-length"}
SYN = {"task-or-modality-removal", "shared-vs-decoupled"}


def groups(r, types=None, pred=None):
    out = []
    for gr in r.get("groups") or []:
        if gr.get("duplicate"):
            continue
        if types and gr.get("factor_type") not in types:
            continue
        if pred and not pred(gr):
            continue
        out.append(gr)
    return out


def units(r, gid):
    return [u for u in (r.get("units_k") or []) if u.get("group_id") == gid and not u.get("duplicate")]


def ar_group(gr):
    gens = {a.get("generator") for a in gr.get("arms") or []}
    return "autoregressive" in gens and "diffusion" in gens


def direction(r, gr, own_gen=None, other_gen=None):
    """Per unit with a known direction: +1 if the anchor (or the own-generator arm) beats the comparison, -1 if worse,
    0 if equal. With own_gen/other_gen the arms are picked by generator; otherwise anchor versus every comparison."""
    arms = {a["arm_id"]: a for a in gr.get("arms") or []}
    if own_gen:
        A = [a for a, x in arms.items() if x.get("generator") == own_gen]
        B = [a for a, x in arms.items() if x.get("generator") == other_gen]
    else:
        A = [gr.get("anchor_arm")] if gr.get("anchor_arm") in arms else []
        B = [a for a in arms if a not in A]
    signs = []
    for u in units(r, gr["group_id"]):
        hib = u.get("higher_is_better")
        if hib is None or u.get("metric_kind") not in ("generated-sample", "likelihood"):
            continue
        v = {x["arm_id"]: num(x.get("value_printed")) for x in u.get("values") or []}
        best = lambda ids, f: f([v[i] for i in ids if v.get(i) is not None], default=None)
        a = best(A, max if hib else min)
        b = best(B, max if hib else min)
        if a is None or b is None:
            continue
        d = (a - b) if hib else (b - a)
        signs.append(1 if d > 0 else -1 if d < 0 else 0)
    return signs


def any_var(r, gr):
    return any((x.get("variance") or {}).get("kind") not in (None, "none") for u in units(r, gr["group_id"]) for x in u.get("values") or [])


def monotone(r, gr):
    """Numeric-dose groups: per unit, quality along increasing dose: 'up', 'down', 'peaked' (interior best), 'flat'."""
    arms = {a["arm_id"]: a.get("level_num") if a.get("level_num") is not None else num(a.get("level_printed")) for a in gr.get("arms") or []}
    shapes = []
    for u in units(r, gr["group_id"]):
        hib = u.get("higher_is_better")
        if hib is None or u.get("metric_kind") != "generated-sample":
            continue
        pts = sorted((arms[x["arm_id"]], num(x.get("value_printed"))) for x in u.get("values") or []
                     if arms.get(x["arm_id"]) is not None and num(x.get("value_printed")) is not None)
        if len(pts) < 3:
            continue
        q = [y if hib else -y for _, y in pts]
        diffs = [b - a for a, b in zip(q, q[1:])]
        if all(d >= 0 for d in diffs) and any(d > 0 for d in diffs):
            shapes.append("up")
        elif all(d <= 0 for d in diffs) and any(d < 0 for d in diffs):
            shapes.append("down")
        elif max(q) > max(q[0], q[-1]):
            shapes.append("peaked")
        else:
            shapes.append("other")
    if not shapes and gr.get("shape") not in (None, "NA", "unclear"):
        shapes.append({"monotone-up": "up", "monotone-down": "down", "peaked": "peaked", "flat": "other"}[gr["shape"]])
    return shapes


# ---------------------------------------------------------------- results
R = {"n_sampled": sum(len(v) for v in STRATA.values()), "n_extracted": len(recs), "n_by_stratum": n_h,
     "N_by_stratum": N_h, "N_frame": N, "ec_used": sorted(ec_used),
     "missing": sorted(i for h in STRATA for i in STRATA[h] if i not in recs)}
SS = ["discrete-absorbing", "discrete-uniform", "discrete-flow", "continuous-embedding", "continuous-latent", "hybrid", "not_stated"]
R["RQ1"] = {
    "study_type": dist(lambda r: g(r, "study", "study_type"), ["method", "theory", "analysis", "benchmark", "system"]),
    "state_space": dist(lambda r: g(r, "study", "state_space"), SS),
    "objective": dist(lambda r: g(r, "design", "objective"), ["elbo-ce", "weighted-ce", "score-entropy", "mse-x0", "mse-eps-or-velocity", "flow-matching", "other", "not_stated", "NA"]),
    "position_rule": dist(lambda r: g(r, "design", "c4_position", "rule"), ["left-to-right", "random", "confidence-ranked", "threshold-adaptive", "fixed-order", "learned-planner", "all-positions", "other", "not_stated"]),
    "blockwise": dist(lambda r: g(r, "design", "c4_position", "blockwise"), ["yes", "no", "not_stated"]),
    "revision": dist(lambda r: g(r, "design", "c5_revision"), ["none", "explicit-remasking-or-editing", "corrector", "implicit-channel", "output-level", "other", "not_stated"]),
    "memory": dist(lambda r: g(r, "design", "memory"), ["none", "self-conditioning", "exact-cache", "approximate-cache", "planner-state", "other", "not_stated"]),
    "training_free": dist(lambda r: g(r, "study", "training", "training_free"), ["yes", "no", "not_stated"]),
    "training_stages": dist(lambda r: g(r, "study", "training", "stages"), ["pretraining", "continued-pretraining", "adaptation-from-ar", "sft", "rl", "distillation", "other"]),
    "credited_type": dist(lambda r: g(r, "study", "credited_component", "type"), ["model-or-architecture", "objective-or-loss", "training-recipe", "sampler-or-decoding", "caching-or-system", "guidance-or-constraint", "other"]),
    "F2_value_rule_stated": est(lambda r: None if g(r, "census", "F2_codes") in (None, "", "NA") else not (str(g(r, "census", "F2_codes")) == "NS" or str(g(r, "census", "F2_codes")).endswith("+NS"))),
}
ar = lambda r: groups(r, pred=ar_group)
R["RQ2"] = {
    "has_ar_group": est(lambda r: bool(ar(r))),
    "abstract_claims_vs_ar_CT6": est(lambda r: None if g(r, "claims", "CT") is None else g(r, "claims", "CT", "CT6") == "yes"),
    "ar_budget_matched_all": est(lambda r: None if not ar(r) else all(gr.get("budget_across_arms") == "matched" for gr in ar(r))),
    "ar_budget_not_reported_any": est(lambda r: None if not ar(r) else any(gr.get("budget_across_arms") == "not reported" for gr in ar(r))),
    "ar_numbers_copied_any": est(lambda r: None if not ar(r) else any(a.get("number_source") == "copied-stated" for gr in ar(r) for a in gr.get("arms") or [] if a.get("generator") == "autoregressive")),
    "ar_variance_any": est(lambda r: None if not ar(r) else any(any_var(r, gr) for gr in ar(r))),
}
sg = lambda r: [s for gr in ar(r) for s in direction(r, gr, "diffusion", "autoregressive")]
R["RQ2"]["diffusion_better_majority_of_units"] = est(lambda r: None if not sg(r) else sum(x > 0 for x in sg(r)) > len(sg(r)) / 2)
R["RQ2"]["diffusion_worse_majority_of_units"] = est(lambda r: None if not sg(r) else sum(x < 0 for x in sg(r)) > len(sg(r)) / 2)
R["RQ2"]["units_total"] = Counter("better" if x > 0 else "worse" if x < 0 else "tie" for r in recs.values() for x in sg(r))
tr = lambda r: groups(r, TRAIN)
R["RQ3"] = {
    "has_training_group": est(lambda r: bool(tr(r))),
    "by_factor": {f: est(lambda r, f=f: bool(groups(r, {f}))) for f in sorted(TRAIN)},
    "credited_ablation_any": est(lambda r: None if not tr(r) else any(gr.get("credited_ablation") for gr in tr(r))),
    "held_fixed_stated_all": est(lambda r: None if not tr(r) else all(gr.get("held_fixed") == "stated" for gr in tr(r))),
    "variance_any": est(lambda r: None if not tr(r) else any(any_var(r, gr) for gr in tr(r))),
}
ts = lambda r: [s for gr in tr(r) for s in direction(r, gr)]
R["RQ3"]["anchor_better_majority"] = est(lambda r: None if not ts(r) else sum(x > 0 for x in ts(r)) > len(ts(r)) / 2)
R["RQ3"]["units_total"] = Counter("anchor-better" if x > 0 else "anchor-worse" if x < 0 else "tie" for r in recs.values() for x in ts(r))
inf = lambda r: groups(r, INFER)
R["RQ4"] = {
    "has_inference_group": est(lambda r: bool(inf(r))),
    "by_factor": {f: est(lambda r, f=f: bool(groups(r, {f}))) for f in sorted(INFER)},
    "budget_reported_any": est(lambda r: None if not inf(r) else any(gr.get("budget_across_arms") in ("matched", "reported") for gr in inf(r))),
    "variance_any": est(lambda r: None if not inf(r) else any(any_var(r, gr) for gr in inf(r))),
}
sh = lambda r: [s for gr in groups(r, {"steps-or-nfe", "tokens-per-step"}) for s in monotone(r, gr)]
R["RQ4"]["dose_shapes_units"] = Counter(s for r in recs.values() for s in sh(r))
R["RQ4"]["any_nonmonotone_dose_curve"] = est(lambda r: None if not sh(r) else any(s in ("peaked", "other") for s in sh(r)))
mmr = {i: recs[i] for i in done.get("G-mm", [])}
R["RQ5"] = {
    "n_mm_extracted": len(mmr),
    "CT5_claim": Counter(str(g(r, "claims", "CT", "CT5")) for r in mmr.values()),
    "synergy_benchmark": Counter(str(g(r, "study", "synergy_benchmark", "present")) for r in mmr.values()),
    "synergy_group": Counter(str(bool(groups(r, SYN))) for r in mmr.values()),
    "claim_and_group": sum(1 for r in mmr.values() if g(r, "claims", "CT", "CT5") == "yes" and groups(r, SYN)),
    "claim_without_group": sorted(i for i, r in mmr.items() if g(r, "claims", "CT", "CT5") == "yes" and not groups(r, SYN)),
    "group_ids": {i: [(gr.get("factor_type"), gr.get("where"), direction(r, gr)) for gr in groups(r, SYN)] for i, r in mmr.items() if groups(r, SYN)},
}
qa_rows = []
for i, r in sorted(recs.items()):
    lo, hi = qa_scores(r, False), qa_scores(r, True)
    qa_rows.append({"id": i, "stratum": of_id[i], "low": lo, "high": hi, "study_type": g(r, "study", "study_type")})
(D / "qa-table.jsonl").write_text("".join(json.dumps(x) + "\n" for x in qa_rows), encoding="utf-8")
qa_by = {x["id"]: x for x in qa_rows}
R["RQ6"] = {}
for k in [f"QA{j}" for j in range(1, 10)]:
    R["RQ6"][k] = {lvl: {s: est(lambda r, k=k, lvl=lvl, s=s: None if qa_by[r["id"]][lvl][k] == "NA" else qa_by[r["id"]][lvl][k] == s) for s in (0, 1, 2)}
                   for lvl in ("low", "high")}
    R["RQ6"][k]["NA"] = sum(1 for x in qa_rows if x["low"][k] == "NA")
R["RQ6"]["claims_status"] = Counter(c.get("status") for r in recs.values() for c in (g(r, "claims", "list") or []))
(D / "rq-results.json").write_text(json.dumps(R, indent=1, default=dict) + "\n", encoding="utf-8")


def fmt(e):
    if not isinstance(e, dict) or "count" not in e:
        return json.dumps(e)
    ci = e.get("ci95")
    return f"{e['count']}/{e['of']}  weighted {e['share']}" + (f" [{ci[0]}, {ci[1]}]" if ci else "")


L = ["# D0052 RQ results (script-generated; do not edit)", "", f"extracted {R['n_extracted']} of {R['n_sampled']}; by stratum {n_h}; N_h {N_h}; missing {R['missing']}", ""]
for rq in ("RQ1", "RQ2", "RQ3", "RQ4", "RQ5", "RQ6"):
    L.append(f"## {rq}")
    for k, v in R[rq].items():
        if isinstance(v, dict) and v and all(isinstance(x, dict) and "count" in x for x in v.values()):
            L.append(f"- {k}:")
            L += [f"  - {c}: {fmt(x)}" for c, x in v.items()]
        elif isinstance(v, dict) and "count" in v:
            L.append(f"- {k}: {fmt(v)}")
        else:
            L.append(f"- {k}: {json.dumps(v, default=dict)[:600]}")
    L.append("")
(D / "rq-results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:6]))
