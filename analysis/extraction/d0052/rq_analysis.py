"""RQ1-RQ6 estimates from the D0052 extraction sample (stratified; weights N_h / n_h).

    python -E -P analysis/extraction/d0052/rq_analysis.py      (numpy, for the D0060 bootstrap)

Inputs: analysis/extraction/d0052/sample.json and gate-manifest.json (strata), stage-a-manifest.json (ids left out of the
frame), batch-log.jsonl (usable sessions), the extractor records analysis/extraction/d0052/EA/<batch>/*.jsonl (the
pass-2 file when a session was returned once, else pass 1), and for the second-reader ids the adjudicated records in
analysis/extraction/d0052/EC/<batch>/*.jsonl when present (D0052: EC values are used for those ids).
D0054 design: update strata at positions 1-20 of each gate list and a seed stratum of 20 drawn from the census
sample's eligible records (seed-sample.json), weight N = 1,106 x 167 / 172 (an estimate, not a count).
Stratum sizes N_h of the update strata are the gate strata minus the stage-a ids, recomputed here from the T1 decisions and text sizes with
the gate manifest's median (asserted against the manifest's stratum sizes before the exclusion).
Output: analysis/extraction/d0052/rq-results.json and rq-results.md; per-study QA table qa-table.jsonl.

Estimator: stratified proportion p = sum_h W_h p_h, W_h = N_h / N; variance sum_h W_h^2 (1 - n_h/N_h) p_h (1-p_h) / (n_h - 1);
95 percent interval by the Wilson formula on the effective sample size p(1-p)/var (Korn-Graubard style; for p_h in
{0, 1} the variance of that stratum uses p_h = 0.5/n_h to stay positive). Counts are unweighted numbers of studies.
Nothing is imputed: a field a record leaves null or 'not_stated' is counted as not stated.
QA scores follow EXTRACTION-PLAN-v0.2 s7.1 (low: unclear = no; high: unclear = yes). QA1 uses the full rule with the
dated link check d from qa1-links.jsonl (qa1_link_check.py) when that file exists: 2 if a and (b or d); 1 if a or c;
else 0; without it, the text-only rule 2 if a and b; 1 if a or c; else 0.
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
seed = json.load(open(D / "seed-sample.json", encoding="utf-8"))           # D0054: 80-record design
STRATA = {h: v[:20] for h, v in sample["strata"].items()}                 # update strata, positions 1-20
STRATA["S-seed"] = seed["seed_ids"]                                      # seed stratum (census eligible)
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
    assert set(sample["strata"][h]) <= set(ids), h
# D0059: D0039 records follow the resolved basis (D0050 S5); recompute stratum membership with the overrides
OVR = {}
for x in jl(SCR / "d0039-resolved.jsonl") if (SCR / "d0039-resolved.jsonl").exists() else []:
    OVR.setdefault(x["id"], {})[x["field"]] = x["value"]
inc_r = [{**r, **{k: v for k, v in OVR.get(r["id"], {}).items() if k in ("i1", "nonlang_only")}} for r in inc]
mm_r = {r["id"] for r in inc_r if r["i1"] in ("b", "ab")}
rc2_r = {r["id"] for r in inc_r if r["i1"] == "a" and not r["nonlang_only"]}
size_r = {i: (MD / f"{i}.txt").stat().st_size for i in rc2_r}
full_r = {"G-mm": mm_r, "G-short": {i for i in rc2_r if size_r[i] <= med}, "G-long": {i for i in rc2_r if size_r[i] > med}}
LEFT_FRAME = sorted(i for h in ("G-mm", "G-short", "G-long") for i in sample["strata"][h][:20] if i not in full_r[h])
N_h = {h: len(set(ids) - stage_a) for h, ids in full_r.items()}
# seed stratum: estimated eligible seed records = pool x eligible / judged (census: 1,106 x 167 / 172)
N_h["S-seed"] = seed["census_pool"] * seed["census_eligible"] / (seed["census_ranks"] - seed["census_no_text"])
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
        if r.get("id") in seed["second_reader_ids"]:
            recs[r["id"]] = r
            ec_used.append(r["id"])
done = {h: [i for i in STRATA[h] if i in recs and i not in LEFT_FRAME] for h in STRATA}
n_h = {h: len(v) for h, v in done.items()}
IN_FRAME = [recs[i] for h in done for i in done[h]]     # unit totals use in-frame records only (not LEFT_FRAME)


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


def est_in(pred, strata):
    """est() over a subset of strata (strand-level estimates: update strata only, or the seed stratum only)."""
    keep = done
    globals()["done"] = {h: v for h, v in keep.items() if h in strata}
    try:
        return est(pred)
    finally:
        globals()["done"] = keep


UPD = ("G-long", "G-mm", "G-short")


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
QA1D = {x["id"]: x["d"] for x in jl(D / "qa1-links.jsonl")} if (D / "qa1-links.jsonl").exists() else {}


def yes(v, high):
    return v == "yes" or (high and v == "unclear")


def qa_scores(r, high):
    q = r.get("qa") or {}
    s = lambda k: (q.get(k) or {}).get("sub") or {}
    out = {}
    a = s("QA1")
    if QA1D:     # full rule once the dated link check exists: 2 if a and (b or d); 1 if a or c; else 0
        d = QA1D.get(r["id"]) == "yes"
        out["QA1"] = 2 if yes(a.get("a"), high) and (yes(a.get("b"), high) or d) else 1 if yes(a.get("a"), high) or yes(a.get("c"), high) else 0
    else:
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
     "N_by_stratum": N_h, "N_frame": N, "left_frame_D0059": LEFT_FRAME, "ec_used": sorted(ec_used),
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
# Census replication (C2 on an independent sample): 'non-plain or unstated' = any F2 code other than plain 'U'
# (census definition, sections/06-census.tex); domain = records with a codable value rule (F2 not empty or NA).
def nonplain(r):
    f2 = str(g(r, "census", "F2_codes") or "").strip()
    if f2 in ("", "NA", "None"):
        return None
    return f2 != "U"


R["census_replication"] = {"all": est(nonplain), "update_strata": est_in(nonplain, UPD),
                           "seed_stratum": est_in(nonplain, ("S-seed",)),
                           "F2_codes": Counter(str(g(r, "census", "F2_codes")) for r in recs.values())}
R["claims_vs_tables_QA8"] = {"any_contradicted_or_unsupported": est(lambda r: None if not [c for c in (g(r, "claims", "list") or []) if c.get("status") not in (None, "not-checkable")] else any(c.get("status") in ("unsupported", "contradicted") for c in g(r, "claims", "list"))),
                             "update_strata": est_in(lambda r: None if not [c for c in (g(r, "claims", "list") or []) if c.get("status") not in (None, "not-checkable")] else any(c.get("status") in ("unsupported", "contradicted") for c in g(r, "claims", "list")), UPD)}
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
R["RQ2"]["units_total"] = Counter("better" if x > 0 else "worse" if x < 0 else "tie" for r in IN_FRAME for x in sg(r))
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
R["RQ3"]["units_total"] = Counter("anchor-better" if x > 0 else "anchor-worse" if x < 0 else "tie" for r in IN_FRAME for x in ts(r))
inf = lambda r: groups(r, INFER)
R["RQ4"] = {
    "has_inference_group": est(lambda r: bool(inf(r))),
    "by_factor": {f: est(lambda r, f=f: bool(groups(r, {f}))) for f in sorted(INFER)},
    "budget_reported_any": est(lambda r: None if not inf(r) else any(gr.get("budget_across_arms") in ("matched", "reported") for gr in inf(r))),
    "variance_any": est(lambda r: None if not inf(r) else any(any_var(r, gr) for gr in inf(r))),
}
# shapes along increasing compute: a steps/NFE sweep as printed; a tokens-per-step sweep reversed (more tokens per step
# is fewer network calls), so 'up' always means quality rises with compute
FLIP = {"up": "down", "down": "up"}
sh = lambda r: ([s for gr in groups(r, {"steps-or-nfe"}) for s in monotone(r, gr)]
                + [FLIP.get(s, s) for gr in groups(r, {"tokens-per-step"}) for s in monotone(r, gr)])
R["RQ4"]["dose_shapes_units"] = Counter(s for r in IN_FRAME for s in sh(r))
R["RQ4"]["dose_shapes_by_factor"] = {f: Counter((FLIP.get(s, s) if f == "tokens-per-step" else s) for r in IN_FRAME
                                                for gr in groups(r, {f}) for s in monotone(r, gr))
                                     for f in ("steps-or-nfe", "tokens-per-step")}
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
R["RQ6"]["claims_status"] = Counter(c.get("status") for r in IN_FRAME for c in (g(r, "claims", "list") or []))

# ---------------------------------------------------------------- sensitivity (Codex debate round 2 asks)
# S1 update strata only (no seed stratum); S2 without records the validator still rejects at their final pass (any
# fail-severity line for that id and session); S3 the second-reader ids from EB instead of EC/EA (extractor swap).
HEAD = {
    "census_nonplain_or_unstated": nonplain,
    "RQ2_has_ar_group": lambda r: bool(ar(r)),
    "RQ2_ar_budget_not_reported_any": lambda r: None if not ar(r) else any(gr.get("budget_across_arms") == "not reported" for gr in ar(r)),
    "RQ2_ar_numbers_copied_any": lambda r: None if not ar(r) else any(a.get("number_source") == "copied-stated" for gr in ar(r) for a in gr.get("arms") or [] if a.get("generator") == "autoregressive"),
    "RQ2_ar_variance_any": lambda r: None if not ar(r) else any(any_var(r, gr) for gr in ar(r)),
    "RQ3_credited_ablation_any": lambda r: None if not tr(r) else any(gr.get("credited_ablation") for gr in tr(r)),
    "RQ3_held_fixed_stated_all": lambda r: None if not tr(r) else all(gr.get("held_fixed") == "stated" for gr in tr(r)),
    "RQ3_variance_any": lambda r: None if not tr(r) else any(any_var(r, gr) for gr in tr(r)),
    "RQ4_has_inference_group": lambda r: bool(inf(r)),
    "RQ4_budget_reported_any": lambda r: None if not inf(r) else any(gr.get("budget_across_arms") in ("matched", "reported") for gr in inf(r)),
    "RQ4_variance_any": lambda r: None if not inf(r) else any(any_var(r, gr) for gr in inf(r)),
    "RQ4_any_nonmonotone_dose_curve": lambda r: None if not sh(r) else any(s in ("peaked", "other") for s in sh(r)),
}
final_pass = {}
for l in log:
    if l["role"] == "EA":
        final_pass[l["basename"]] = l["pass"]
rejected = set()
for p in (1, 2):
    vf = D / f"validate-pass{p}.jsonl"
    for x in (jl(vf) if vf.exists() else []):
        if x.get("severity") == "fail" and final_pass.get(x.get("session")) == p:
            rejected.add(x["id"])
rejected -= set(ec_used)
eb_recs = {}
for folder in sorted((D / "EB").glob("*")):
    files = sorted(folder.glob("EB-*.jsonl"))
    p2 = [f for f in files if f.stem.endswith("-pass2")]
    for f in (p2 or [f for f in files if not f.stem.endswith("-pass2")]):
        for r in jl(f):
            eb_recs[r["id"]] = r


def run_variant(keep=None, swap=None):
    old_done, old_recs = done, recs
    nd = {h: [i for i in v if keep is None or i in keep] for h, v in done.items()}
    nr = {**recs, **(swap or {})}
    globals()["done"], globals()["recs"] = nd, nr
    globals()["n_h"] = {h: len(v) for h, v in nd.items()}
    try:
        return {k: est(f) for k, f in HEAD.items()}
    finally:
        globals()["done"], globals()["recs"] = old_done, old_recs
        globals()["n_h"] = {h: len(v) for h, v in old_done.items()}


all_ids = {i for v in done.values() for i in v}
R["sensitivity"] = {
    "rejected_at_final_pass": sorted(rejected),
    "S0_main": run_variant(),
    "S1_update_strata_only": {k: est_in(f, UPD) for k, f in HEAD.items()},
    "S2_without_rejected": run_variant(keep=all_ids - rejected),
    "S3_second_reader_ids_from_EB": run_variant(swap={i: eb_recs[i] for i in seed["second_reader_ids"] if i in eb_recs}),
}
# ================================================================ D0060 (response to the 2026-10-21 red-team audit)
# Primary estimand: the included studies (update strata). The seed stratum is a separate column; the combined frame
# is kept above (R["RQ*"], R["sensitivity"]) for the supplement only. Intervals: stratified bootstrap over studies
# within strata (percentile, B = 4000, seed 20261021); a zero or full cell gets the exact binomial bound on the Kish
# effective n of its domain. Verdicts: thresholds of D0060, applied to RQ2-RQ5 only.
import numpy as np

B, BOOT_SEED = 4000, 20261021


def tol_shapes(r, gr, tol=0.01):
    """monotone() with dips or rises within tol of the larger neighbour ignored (red-team M2 sensitivity)."""
    arms = {a["arm_id"]: a.get("level_num") if a.get("level_num") is not None else num(a.get("level_printed")) for a in gr.get("arms") or []}
    out = []
    for u in units(r, gr["group_id"]):
        hib = u.get("higher_is_better")
        if hib is None or u.get("metric_kind") != "generated-sample":
            continue
        pts = sorted((arms[x["arm_id"]], num(x.get("value_printed"))) for x in u.get("values") or []
                     if arms.get(x["arm_id"]) is not None and num(x.get("value_printed")) is not None)
        if len(pts) < 3:
            continue
        q = [y if hib else -y for _, y in pts]
        d = [b - a if abs(b - a) > tol * max(abs(a), abs(b), 1e-12) else 0.0 for a, b in zip(q, q[1:])]
        if all(x >= 0 for x in d) and any(x > 0 for x in d):
            out.append("up")
        elif all(x <= 0 for x in d) and any(x < 0 for x in d):
            out.append("down")
        elif all(x == 0 for x in d):
            out.append("flat")
        elif max(q) > max(q[0], q[-1]) and d[0] > 0:
            out.append("peaked")
        else:
            out.append("other")
    return out


sh_tol = lambda r: ([s for gr in groups(r, {"steps-or-nfe"}) for s in tol_shapes(r, gr)]
                    + [FLIP.get(s, s) for gr in groups(r, {"tokens-per-step"}) for s in tol_shapes(r, gr)])
ctrl = lambda gs, r: (any(gr.get("budget_across_arms") in ("matched", "reported") for gr in gs)
                      and any(any_var(r, gr) for gr in gs))
# RQ5 signs oriented as joint (shared, fuller) arm against the reduced (decoupled) arm, not anchor against the rest:
# rq5-orientation.jsonl gives, per synergy group, whether the anchor is the joint arm (gate audit 2026-10-21 finding 2)
ORIENT = {(x["id"], x["group_id"]): (1 if x["anchor_is_joint"] else -1) for x in jl(D / "rq5-orientation.jsonl")}


def syn(r):
    out = []
    for gr in groups(r, SYN):
        s_ = direction(r, gr)
        if s_:
            assert (r["id"], gr["group_id"]) in ORIENT, ("RQ5 group without orientation", r["id"], gr["group_id"])
            out += [x * ORIENT[(r["id"], gr["group_id"])] for x in s_]
    return out
maj = lambda xs, sgn: None if not xs else (sum(1 for x in xs if x == sgn) > len(xs) / 2)
VARS = {
    # RQ2
    "RQ2_has_ar": lambda r: bool(ar(r)),
    "RQ2_matched_any": lambda r: None if not ar(r) else any(gr.get("budget_across_arms") == "matched" for gr in ar(r)),
    "RQ2_matched_all": lambda r: None if not ar(r) else all(gr.get("budget_across_arms") == "matched" for gr in ar(r)),
    "RQ2_budget_not_reported_any": lambda r: None if not ar(r) else any(gr.get("budget_across_arms") == "not reported" for gr in ar(r)),
    "RQ2_copied_stated_any": lambda r: None if not ar(r) else any(a.get("number_source") == "copied-stated" for gr in ar(r) for a in gr.get("arms") or [] if a.get("generator") == "autoregressive"),
    "RQ2_variance_any": lambda r: None if not ar(r) else any(any_var(r, gr) for gr in ar(r)),
    "RQ2_control": lambda r: None if not ar(r) else ctrl(ar(r), r),
    "RQ2_signed": lambda r: bool(sg(r)),
    "RQ2_better_majority": lambda r: maj(sg(r), 1),
    "RQ2_worse_majority": lambda r: maj(sg(r), -1),
    "RQ2_abstract_claim": lambda r: None if g(r, "claims", "CT") is None else g(r, "claims", "CT", "CT6") == "yes",
    # RQ3
    "RQ3_has_training": lambda r: bool(tr(r)),
    "RQ3_credited_ablation_any": lambda r: None if not tr(r) else any(gr.get("credited_ablation") for gr in tr(r)),
    "RQ3_held_fixed_all": lambda r: None if not tr(r) else all(gr.get("held_fixed") == "stated" for gr in tr(r)),
    "RQ3_variance_any": lambda r: None if not tr(r) else any(any_var(r, gr) for gr in tr(r)),
    "RQ3_control": lambda r: None if not tr(r) else ctrl(tr(r), r),
    "RQ3_signed": lambda r: bool(ts(r)),
    "RQ3_anchor_better_majority": lambda r: maj(ts(r), 1),
    "RQ3_anchor_worse_majority": lambda r: maj(ts(r), -1),
    # RQ4
    "RQ4_has_inference": lambda r: bool(inf(r)),
    "RQ4_budget_reported_any": lambda r: None if not inf(r) else any(gr.get("budget_across_arms") in ("matched", "reported") for gr in inf(r)),
    "RQ4_variance_any": lambda r: None if not inf(r) else any(any_var(r, gr) for gr in inf(r)),
    "RQ4_control": lambda r: None if not inf(r) else ctrl(inf(r), r),
    "RQ4_has_sweep": lambda r: bool(sh(r)),
    "RQ4_sweep_up_majority": lambda r: None if not sh(r) else sum(s == "up" for s in sh(r)) > len(sh(r)) / 2,
    "RQ4_sweep_down_majority": lambda r: None if not sh(r) else sum(s == "down" for s in sh(r)) > len(sh(r)) / 2,
    "RQ4_sweep_all_up": lambda r: None if not sh(r) else all(s == "up" for s in sh(r)),
    "RQ4_any_nonmonotone": lambda r: None if not sh(r) else any(s in ("peaked", "other") for s in sh(r)),
    "RQ4_any_nonmonotone_tol1pct": lambda r: None if not sh_tol(r) else any(s in ("peaked", "other") for s in sh_tol(r)),
    "RQ4_sweep_control": lambda r: None if not sh(r) else ctrl(groups(r, {"steps-or-nfe", "tokens-per-step"}), r),
    # RQ5 (G-mm only; other strata give None through the domain)
    "RQ5_claim": lambda r: None if of_id.get(r["id"]) != "G-mm" else g(r, "claims", "CT", "CT5") == "yes",
    "RQ5_has_ablation": lambda r: None if of_id.get(r["id"]) != "G-mm" else bool(groups(r, SYN)),
    "RQ5_signed": lambda r: None if of_id.get(r["id"]) != "G-mm" else bool(syn(r)),
    "RQ5_joint_better_majority": lambda r: None if of_id.get(r["id"]) != "G-mm" else maj(syn(r), 1),
    "RQ5_joint_worse_majority": lambda r: None if of_id.get(r["id"]) != "G-mm" else maj(syn(r), -1),
    "RQ5_benchmark": lambda r: None if of_id.get(r["id"]) != "G-mm" else str(g(r, "study", "synergy_benchmark", "present")) == "yes",
    "RQ5_control": lambda r: None if of_id.get(r["id"]) != "G-mm" or not groups(r, SYN) else ctrl(groups(r, SYN), r),
    # claims
    "claims_any_unsupported": lambda r: None if not [c for c in (g(r, "claims", "list") or []) if c.get("status") not in (None, "not-checkable")] else any(c.get("status") in ("unsupported", "contradicted") for c in g(r, "claims", "list")),
}
for k in [f"QA{j}" for j in range(1, 10)]:
    for s_ in (0, 1, 2):
        VARS[f"{k}_low_eq{s_}"] = (lambda r, k=k, s_=s_: None if qa_by[r["id"]]["low"][k] == "NA" else qa_by[r["id"]]["low"][k] == s_)
        VARS[f"{k}_high_eq{s_}"] = (lambda r, k=k, s_=s_: None if qa_by[r["id"]]["high"][k] == "NA" else qa_by[r["id"]]["high"][k] == s_)
# RQ1 descriptive shares
for fld, path, cats in (("state_space", ("study", "state_space"), SS),
                        ("position_rule", ("design", "c4_position", "rule"), ["left-to-right", "random", "confidence-ranked", "threshold-adaptive", "fixed-order", "learned-planner", "all-positions", "other", "not_stated"]),
                        ("blockwise", ("design", "c4_position", "blockwise"), ["yes", "no", "not_stated"]),
                        ("revision", ("design", "c5_revision"), ["none", "explicit-remasking-or-editing", "corrector", "implicit-channel", "output-level", "other", "not_stated"]),
                        ("memory", ("design", "memory"), ["none", "self-conditioning", "exact-cache", "approximate-cache", "planner-state", "other", "not_stated"]),
                        ("training_free", ("study", "training", "training_free"), ["yes", "no", "not_stated"])):
    for c in cats:
        def f_(r, path=path, c=c):
            v = g(r, *path)
            v = v if isinstance(v, list) else [v]
            return c in [x if x is not None else "not_stated" for x in v]
        VARS[f"RQ1_{fld}={c}"] = f_


def boot_est(var, strata, keep=None):
    """Domain proportion over the given strata, weights N_h * (domain count / n_h); stratified bootstrap percentile CI."""
    ids = {h: [i for i in done[h] if keep is None or i in keep] for h in strata if h in done}
    vals = {h: np.array([(-1 if v is None else int(v)) for v in (VARS[var](recs[i]) for i in L_)], int) for h, L_ in ids.items()}
    count = int(sum((a == 1).sum() for a in vals.values()))
    of = int(sum((a >= 0).sum() for a in vals.values()))
    if of == 0:
        return {"count": 0, "of": 0, "share": None, "ci95": None}

    def share(arrs):
        num_, den_ = 0.0, 0.0
        for h, a in arrs.items():
            n_ = len(a)
            dom = (a >= 0).sum()
            if n_ == 0 or dom == 0:
                continue
            w = N_h[h] * dom / n_
            num_ += w * (a == 1).sum() / dom
            den_ += w
        return num_ / den_ if den_ > 0 else np.nan
    p = share(vals)
    rng = np.random.default_rng(BOOT_SEED)
    bs = np.empty(B)
    for b in range(B):
        bs[b] = share({h: a[rng.integers(0, len(a), len(a))] for h, a in vals.items() if len(a)})
    lo, hi = np.nanquantile(bs, [0.025, 0.975])
    if p in (0.0, 1.0):        # zero or full cell: exact binomial bound on the Kish effective n of the domain
        w = [N_h[h] / len(a) for h, a in vals.items() for x in a if x >= 0]
        kish = sum(w) ** 2 / sum(x * x for x in w)
        bound = 1 - 0.025 ** (1 / kish)
        lo, hi = (0.0, bound) if p == 0.0 else (1 - bound, 1.0)
    by = {h: f"{int((a == 1).sum())}/{int((a >= 0).sum())}" for h, a in vals.items()}
    return {"count": count, "of": of, "share": round(float(p), 3), "ci95": [round(float(lo), 3), round(float(hi), 3)], "by_stratum": by}


SEED = ("S-seed",)
P = {"population_primary": "included studies (update strata G-mm, G-short, G-long)", "N_primary": sum(N_h[h] for h in UPD),
     "n_primary": sum(n_h[h] for h in UPD), "N_seed": N_h["S-seed"], "n_seed": n_h["S-seed"],
     "bootstrap": {"B": B, "seed": BOOT_SEED, "method": "stratified percentile"}}
P["included"] = {v: boot_est(v, UPD) for v in VARS}
P["seed"] = {v: boot_est(v, SEED) for v in VARS}
P["combined"] = {v: boot_est(v, UPD + SEED) for v in VARS}
P["included_without_rejected"] = {v: boot_est(v, UPD, keep=all_ids - rejected) for v in VARS}
old_recs = recs
recs = {**recs, **{i: eb_recs[i] for i in seed["second_reader_ids"] if i in eb_recs}}
qa_rows_eb = {i: {"low": qa_scores(recs[i], False), "high": qa_scores(recs[i], True)} for i in seed["second_reader_ids"] if i in eb_recs}
_qa_saved = dict(qa_by)
for i, x in qa_rows_eb.items():
    qa_by[i] = {**qa_by.get(i, {}), **x}
P["included_EB_on_8"] = {v: boot_est(v, UPD) for v in VARS}
qa_by.clear(); qa_by.update(_qa_saved)
recs = old_recs


def verdict(rq, E):
    """D0060 thresholds on the included-study estimates E (weighted shares)."""
    if rq == "RQ4":
        up, down, n_sig = E["RQ4_sweep_up_majority"], E["RQ4_sweep_down_majority"], E["RQ4_has_sweep"]["count"]
        control = E["RQ4_sweep_control"]
    elif rq == "RQ5":
        up, down, n_sig = E["RQ5_joint_better_majority"], E["RQ5_joint_worse_majority"], E["RQ5_signed"]["count"]
        control = E["RQ5_control"]
    elif rq == "RQ3":
        up, down, n_sig = E["RQ3_anchor_better_majority"], E["RQ3_anchor_worse_majority"], E["RQ3_signed"]["count"]
        control = E["RQ3_control"]
    else:
        up, down, n_sig = E["RQ2_better_majority"], E["RQ2_worse_majority"], E["RQ2_signed"]["count"]
        control = E["RQ2_control"]
    if n_sig < 5:
        v = "untested"
    elif max(up["share"] or 0, down["share"] or 0) < 2 / 3:
        v = "mixed"
    elif (control["share"] or 0) < 0.5:
        v = "weakly supported"
    else:
        v = "well supported"
    return {"verdict": v, "n_signed": n_sig, "share_one_way": max(up["share"] or 0, down["share"] or 0),
            "direction": "positive" if (up["share"] or 0) >= (down["share"] or 0) else "negative",
            "control_share": control["share"]}


for col in ("included", "seed", "combined", "included_without_rejected", "included_EB_on_8"):
    P.setdefault("verdicts", {})[col] = {rq: verdict(rq, P[col]) for rq in ("RQ2", "RQ3", "RQ4", "RQ5")}
# extra agreement measures for S4 (red-team M4): factor type, claim status, QA item scores, study-level flags
AG = json.load(open(D / "agreement-8-texts/agreement-stage-a.json", encoding="utf-8"))
ea_p = {r["id"]: r for r in jl(D / "ec-input/EA-pairs.jsonl")}
eb_p = {r["id"]: r for r in jl(D / "ec-input/EB-pairs.jsonl")}
qa_pairs = [(qa_scores(ea_p[i], False)[k], qa_scores(eb_p[i], False)[k]) for i in ea_p for k in [f"QA{j}" for j in range(1, 10)]]
FLAGS = ["RQ2_has_ar", "RQ2_matched_any", "RQ2_budget_not_reported_any", "RQ2_better_majority", "RQ3_has_training",
         "RQ3_held_fixed_all", "RQ3_anchor_better_majority", "RQ4_has_inference", "RQ4_budget_reported_any",
         "RQ4_variance_any", "RQ4_sweep_up_majority", "RQ4_any_nonmonotone", "RQ5_has_ablation", "claims_any_unsupported"]
flag_pairs = {}
for k in FLAGS:
    pr = [(VARS[k](ea_p[i]), VARS[k](eb_p[i])) for i in ea_p]
    pr = [(a, b) for a, b in pr if not (a is None and b is None)]
    flag_pairs[k] = {"agree": sum(a == b for a, b in pr), "of": len(pr)}
P["agreement_extra"] = {
    "factor_type_matched_groups": {"agree": AG["metrics"]["G4 M-class"]["numerator"], "of": AG["metrics"]["G4 M-class"]["denominator"]},
    "claim_status": AG["diagnostics"]["M-CL"],
    "qa_item_scores_low": {"agree": sum(a == b for a, b in qa_pairs), "of": len(qa_pairs)},
    "study_level_flags": flag_pairs,
    "study_level_flags_total": {"agree": sum(v["agree"] for v in flag_pairs.values()), "of": sum(v["of"] for v in flag_pairs.values())},
    "units_both_found_studies": AG["metrics"]["G4 M-val"].get("records_used"),
}
P["kish_n_included"] = {}
for v in ("RQ2_has_ar", "RQ2_signed", "RQ3_has_training", "RQ4_has_inference", "RQ4_has_sweep"):
    w = []
    for h in UPD:
        for i in done[h]:
            if VARS[v](recs[i]):
                w.append(N_h[h] / n_h[h])
    P["kish_n_included"][v] = round(sum(w) ** 2 / sum(x * x for x in w), 1) if w else 0
UPD_IDS = [i for h in UPD for i in done[h]]
P["group_counts_included"] = {
    "ar_groups_by_budget": dict(Counter(gr.get("budget_across_arms") for i in UPD_IDS for gr in ar(recs[i]))),
    "sweep_curves": dict(Counter(s for i in UPD_IDS for s in sh(recs[i]))),
    "sweep_curves_by_study": {i: len(sh(recs[i])) for i in UPD_IDS if sh(recs[i])},
    "rq5_signed_by_study": {i: syn(recs[i]) for i in done["G-mm"] if syn(recs[i])},
    "claims_status": dict(Counter(c.get("status") for i in UPD_IDS for c in (g(recs[i], "claims", "list") or []))),
    "rq3_anchor_rules_signed_groups": dict(Counter(gr.get("anchor_rule") for i in UPD_IDS for gr in tr(recs[i]) if direction(recs[i], gr))),
}
R["D0060"] = P

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
S = R["sensitivity"]
L += ["## Sensitivity", f"rejected at final pass (S2 drops them): {S['rejected_at_final_pass']}", "",
      "| estimate | S0 main | S1 update strata only | S2 without rejected | S3 second-reader ids from EB |", "|---|---|---|---|---|"]
for k in HEAD:
    L.append(f"| {k} | " + " | ".join(fmt(S[v][k]) for v in ("S0_main", "S1_update_strata_only", "S2_without_rejected", "S3_second_reader_ids_from_EB")) + " |")
L.append("")
(D / "rq-results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[:6]))
