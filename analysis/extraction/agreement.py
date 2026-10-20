"""Agreement of two extraction sessions, form v0.5 (EXTRACTION-PLAN-v0.5 s10.2-s10.4, s10.7-s10.8, s11 on top of
EXTRACTION-PLAN-v0.4 s11.1 and EXTRACTION-PLAN-v0.3 s5, s10.3; red-team audit 5 MJ1). Not a result about any paper:
it computes what the plan defines on whatever record files it is given.

Run from the worktree root (numpy and scipy, through gate_rule_v05.py and icc_check.py):
  python -E -P analysis/extraction/agreement.py --mode {stage-a|gate-phase1|gate} --x <EA.jsonl> --y <EB.jsonl>
      --manifest <draw manifest .json> --lookups <dir> --validator <ex_validate report .jsonl>
      --config analysis/extraction/gate-config-v05.json --out <dir>
      [--grid analysis/extraction/bip-grid-v2.json --expect-config <sha256>]   (required in gate-phase1 and gate)
      [--phase1 <agreement-gate-phase1.json>]                                   (required in gate)
      [--replacements <jsonl>] [--regate] [--we analysis/extraction/we-expected.jsonl] [--ec <EC.jsonl>]
      [--texts research/sources/md/fulltext-pymupdf] [--boot-seed 20261800] [--icc-seed <int>]
  python -E -P analysis/extraction/agreement.py --self-test

Inputs (a missing or mismatched input stops the run before anything is written):
  --x, --y      one JSON record per line (schema v0.5); X is EA (G1 accept EA), Y is EB (G1 accept EB).
  --manifest    written by draw_pilot.py. stage-a: {"stage": "stage-a", "ids", "stratum": {id: pool},
                "strata_order", "worked_examples", "drawn"}; gate: {"stage": "gate", "lists": {stratum: [ordered
                ids]}, "spares": {stratum: [ids]}, "per_stratum_phase1", "strata_order", "stratum"}. Records whose
                ids are not in it are refused.
  --replacements  gate only: rows {"stratum", "failed", "replacement"} (plan s10.7 step 2); a replacement must be a
                spare of its stratum and takes the failed id's position.
  --lookups     benchmark-ids-v1.csv (printed, id) and metric-ids-v1.csv (printed, id, higher_is_better).
  --validator   ex_validate first-pass report, plan v0.2 s6.5 lines {id, extractor, check, ref, status,
                severity, detail}; every (id, extractor) of X and Y must appear at least once (a summary line).
                An evidence entry (prose E.., table T.., cell C..) fails first pass when a line with severity
                "fail" has ref equal to its id (or the id followed by ".", "[" or ":"); a cell is column-unverified
                when a line with check "column_unverified" refers to it. Lines with "pass" > 1 are ignored.
  --config/--grid  the declared inputs of s10.8; the grid's model_sha256 must equal gate_rule_v05.model_sha of the
                config, and in gate modes the config's sha256 must equal --expect-config.
  --we          stage-a: worked-example expected lists, one partial record per id ({"id", "groups": [{"group_id",
                "where", "second_factor_printed", "anchor_arm", "arms": [{"arm_id", "label_printed"}]}],
                "units_k": [{"unit_id", "group_id", "benchmark_printed", "metric_printed", "condition_printed",
                "split"}]}); missing fields count as ''.
  --ec          optional EC final records; used only for the final sign of s10.3 / MJ1.
  --texts       optional full texts; with them an abstract H unit is keyed by the character offset of its
                number in the normalised text (U14); without them by (normalised quote, number, occurrence).

Outputs in --out (refuses to overwrite): agreement-<mode>.json (per metric point, LB90, pooled numerator and
denominator, records used; ICC block; sign coverage; input sha256; parameters and their sha256; tool version;
seeds), per-record-<mode>.csv, matches-<mode>.jsonl (written after the metrics), verdict-table.md (gate),
we-comparison.md (stage-a), run-<mode>.log. gate-phase1 writes only agreement-gate-phase1.json with the 20 U_m
values, P_hat(n) per grid n, n, the step-6 flag, input hashes and seeds (s10.7 step 5), and the run log.

Spec gaps resolved here (each is also listed in the output under "spec_resolutions"):
  R1 Block items. S: S01-S08 whole fields, S09 and S10 per sub-field (S10.description excluded as free text),
     S13.type, S15, S16 (present, name), S17, S18, I1-I5. D: D01-D11 (D07 as rule and blockwise), D15, the twelve
     D16 entries. Strings compared after U11 normalisation; lists of strings as sets; Jaccard for S04, S05,
     S15, D01, D10, D11. NA = null or "NA"; NA-NA pairs are excluded, NA against a value is a disagreement.
  R2 Group arm-label Jaccard = matched arms (U11 equal, then label-core, one-to-one in reading order) / union.
  R3 Final sign (MJ1 fix as written by the red-team): (1) an arrow printed in metric_printed or a value's
     column_printed (script-visible KA1(a)) sets the sign; (2) else the lookup direction when the metric is
     mapped and the direction is non-null, unless an extractor value conflicts with it (a null extractor value is
     not a conflict); (3) else the unit is routed to EC and takes EC's value (KA1 under EC); (4) else unsigned
     (excluded from signed pooling). Without --ec, routed units are counted as "pending EC".
  R4 M-sign reader value for (matched group, metric key): the reader's higher_is_better on that group's units
     with that key; two different values in one reader count as a disagreement.
  R5 K-attr point = mean of the per-field ratios that have applicable pairs; bootstrap uses the same rule.
  R6 Undefined criterion (no applicable pair) fails in gate mode.
  R7 G5: F1 part identical when neither reader has an F1 unit, or the two F1 units are matched by the H match;
     S14 part identical when both are "NA"/null or (where, row_group, own_row, baseline_row) are equal under U11.
  R8 M-val excludes units that are figure-only in both readers.
  R9 v0.4 pooled ICC (comparison only): mean ANOVA ICC of the eight count metrics, K-attr as the sum of its four
     fields, bound by icc_check.upper80_neyman.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import importlib.util
import json
import math
import platform
import re
import sys
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TOOL_VERSION = "agreement.py 1.0.0 (extraction form v0.5)"
SELF_TEST_SEED = 20267000
BOOT_SEED = 20261800


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GR = _load("gate_rule_v05", HERE / "gate_rule_v05.py")          # bounds, theta, product rule (reference)
IC = GR.I                                                         # icc_check: icc_anova, upper80_neyman
QC = _load("quote_check", ROOT / "analysis" / "screening" / "quote_check.py")   # normalise (read-only)


class InputError(SystemExit):
    pass


def fail(msg):
    raise InputError(f"agreement.py: {msg} (nothing written)")


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha_obj(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def read_jsonl(p):
    try:
        with open(p, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]
    except (OSError, json.JSONDecodeError) as e:
        fail(f"cannot read {p}: {e}")


# =============================================================================================================
# Normalisation (U11, s5.4)
# =============================================================================================================
_CIT = re.compile(r"\s*[\(\[][^()\[\]]*?(?:19|20)\d{2}[a-z]?[^()\[\]]*[\)\]]\s*$")
_OURS = re.compile(r"\(\s*ours\s*\)", re.I)
_MARK = re.compile(r"[*†‡§¶✝⋆★]+")
_ARROW = re.compile(r"[↑↓⬆⬇]")
_DASH = str.maketrans({"−": "-", "–": "-", "—": "-"})


def _strip_tail(s):
    prev = None
    while prev != s:
        prev = s
        s = _OURS.sub("", s).strip()
        s = _CIT.sub("", s).strip()
    return s


def norm_label(s):
    """U11 key: quote_check.normalise, lower case, trailing citation with a year and "(ours)" removed, markers
    removed, all whitespace removed."""
    if s is None:
        return ""
    s = QC.normalise(_strip_tail(str(s))).lower()      # citations first: normalise drops square brackets
    s = _strip_tail(s)
    s = _MARK.sub("", s)
    return re.sub(r"\s+", "", s)


def label_core(key):
    """The label without one trailing parenthesis (keys carry no whitespace); None if there is none."""
    m = re.fullmatch(r"(.+?)\(([^()]*)\)", key or "")
    return m.group(1) if m else None


def norm_bm(s):
    """s5.4: quote_check.normalise, lower case, arrows and enclosing parentheses removed, a trailing citation
    with a year removed, all whitespace removed."""
    if s is None:
        return ""
    s = QC.normalise(_strip_tail(_ARROW.sub("", str(s)))).lower()
    s = _ARROW.sub("", s)
    s = _strip_tail(s).strip()
    while len(s) >= 2 and s[0] == "(" and s[-1] == ")" and _balanced(s[1:-1]):
        s = s[1:-1].strip()
    return re.sub(r"\s+", "", s)


def _balanced(s):
    d = 0
    for ch in s:
        d += (ch == "(") - (ch == ")")
        if d < 0:
            return False
    return d == 0


def norm_value(s):
    if s is None:
        return None
    return re.sub(r"\s+", "", QC.normalise(str(s)).translate(_DASH)).lower()


def isna(v):
    return v is None or v == "NA"


def canon(v):
    """Comparable form of a field value (strings by U11; lists as sorted sets; dicts by key)."""
    if isna(v):
        return None
    if isinstance(v, bool) or isinstance(v, (int, float)):
        return json.dumps(v)
    if isinstance(v, str):
        return norm_label(v)
    if isinstance(v, list):
        return json.dumps(sorted({canon(x) or "" for x in v}))
    if isinstance(v, dict):
        return json.dumps({k: canon(x) for k, x in sorted(v.items())}, sort_keys=True)
    return json.dumps(v)


def as_set(v):
    if isna(v):
        return None
    if isinstance(v, list):
        return {canon(x) or "" for x in v}
    return {canon(v)}


# =============================================================================================================
# Lookups (s5.4) and the validator report
# =============================================================================================================
class Lookups:
    def __init__(self, d):
        d = Path(d)
        self.files = {"benchmark": d / "benchmark-ids-v1.csv", "metric": d / "metric-ids-v1.csv"}
        for k, p in self.files.items():
            if not p.exists():
                fail(f"lookup file missing: {p}")
        self.bench, self.metric, self.direction = {}, {}, {}
        with open(self.files["benchmark"], encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                self.bench[norm_bm(row["printed"])] = row["id"].strip()
        with open(self.files["metric"], encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                mid = row["id"].strip()
                self.metric[norm_bm(row["printed"])] = mid
                d0 = parse_dir(row.get("higher_is_better", ""))
                if mid in self.direction and self.direction[mid] != d0:
                    fail(f"metric lookup gives two directions for {mid}")
                self.direction[mid] = d0
        self.sha = {k: sha_file(p) for k, p in self.files.items()}

    def bkey(self, s):
        n = norm_bm(s)
        return self.bench.get(n, "raw:" + n)

    def mkey(self, s):
        n = norm_bm(s)
        return self.metric.get(n, "raw:" + n)

    def mdir(self, mkey):
        return None if mkey.startswith("raw:") else self.direction.get(mkey)


def parse_dir(s):
    s = (s or "").strip().lower()
    return True if s in ("true", "1", "yes") else False if s in ("false", "0", "no") else None


class Validator:
    def __init__(self, path):
        self.seen, self.fails, self.unver = set(), defaultdict(set), defaultdict(set)
        for l in read_jsonl(path):
            if int(l.get("pass", 1) or 1) != 1:
                continue
            key = (l.get("id"), l.get("extractor"))
            self.seen.add(key)
            ref = str(l.get("ref") or "")
            if l.get("severity") == "fail" or l.get("status") == "fail":
                self.fails[key].add(ref)
            if l.get("check") == "column_unverified":
                self.unver[key].add(ref)
        self.sha = sha_file(path)

    @staticmethod
    def _hit(refs, eid):
        return any(r == eid or r.startswith((eid + ".", eid + "[", eid + ":")) for r in refs)

    def failed(self, rid, ext, eid):
        return self._hit(self.fails[(rid, ext)], eid)

    def verified(self, rid, ext, cid):
        return not self._hit(self.unver[(rid, ext)], cid)


# =============================================================================================================
# Matching (U11, U13, U9, U14 with s5.2 of v0.5)
# =============================================================================================================
def arm_match(ax, ay):
    """One-to-one arm match inside a matched group: equal U11 keys first, then label-core; reading order."""
    kx = [norm_label(a.get("label_printed")) for a in ax]
    ky = [norm_label(a.get("label_printed")) for a in ay]
    used_x, used_y, pairs = set(), set(), []
    for i, k in enumerate(kx):
        for j, l in enumerate(ky):
            if j not in used_y and k == l:
                pairs.append((i, j, "equal"))
                used_x.add(i), used_y.add(j)
                break
    for i, k in enumerate(kx):
        if i in used_x:
            continue
        for j, l in enumerate(ky):
            if j in used_y:
                continue
            ck, cl = label_core(k), label_core(l)
            if (ck is not None and ck == l) or (cl is not None and cl == k):
                pairs.append((i, j, "core"))
                used_x.add(i), used_y.add(j)
                break
    return sorted(pairs)


def gkey(g):
    return norm_label(g.get("where")), norm_label(g.get("second_factor_printed"))


def group_match(gx, gy):
    """U13: equal (where, second factor), arm Jaccard >= 0.5, one-to-one by highest Jaccard, ties to the lower
    group id. Returns ([(i, j, jaccard, arm_pairs)], x_only, y_only)."""
    cands = []
    for i, g in enumerate(gx):
        for j, h in enumerate(gy):
            if gkey(g) != gkey(h):
                continue
            am = arm_match(g.get("arms") or [], h.get("arms") or [])
            union = len(g.get("arms") or []) + len(h.get("arms") or []) - len(am)
            jac = len(am) / union if union else 1.0
            if jac >= 0.5 - 1e-12:
                cands.append((-jac, str(g.get("group_id")), str(h.get("group_id")), i, j, jac, am))
    cands.sort(key=lambda c: c[:3])
    ux, uy, out = set(), set(), []
    for _, _, _, i, j, jac, am in cands:
        if i in ux or j in uy:
            continue
        ux.add(i), uy.add(j)
        out.append((i, j, jac, am))
    out.sort()
    return out, [i for i in range(len(gx)) if i not in ux], [j for j in range(len(gy)) if j not in uy]


def one_to_one(keys_x, keys_y):
    """Match equal keys one-to-one in reading order. Returns [(i, j)]."""
    free = defaultdict(list)
    for j, k in enumerate(keys_y):
        free[k].append(j)
    out = []
    for i, k in enumerate(keys_x):
        if free.get(k):
            out.append((i, free[k].pop(0)))
    return out


def lenient(part):
    if not part.startswith("raw:"):
        return part
    s = re.sub(r"[^0-9a-z]", "", part[4:])
    s = re.sub(r"(v\d+(\d)*|test|val|valid|validation|dev|train)$", "", s) or s
    return "raw~" + s


def k_key(u, L, lenient_key=False):
    b, m = L.bkey(u.get("benchmark_printed")), L.mkey(u.get("metric_printed"))
    if lenient_key:
        b, m = lenient(b), lenient(m)
    return b, m, norm_label(u.get("condition_printed")), norm_label(u.get("split"))


def match_k(rx, ry, gm, L, lenient_key=False):
    """K units matched inside matched groups by the U9 key. Returns [(ux_index, uy_index, group pair index)]."""
    ux, uy = rx.get("units_k") or [], ry.get("units_k") or []
    gx, gy = rx.get("groups") or [], ry.get("groups") or []
    out = []
    for p, (i, j, _, _) in enumerate(gm):
        xi = [a for a, u in enumerate(ux) if u.get("group_id") == gx[i].get("group_id")]
        yj = [b for b, u in enumerate(uy) if u.get("group_id") == gy[j].get("group_id")]
        for a, b in one_to_one([k_key(ux[a], L, lenient_key) for a in xi], [k_key(uy[b], L, lenient_key) for b in yj]):
            out.append((xi[a], yj[b], p))
    return sorted(out)


def _index(r, field):
    return {e.get("id"): e for e in (r.get(field) or [])}


def _occurrence_index(q, v, occ):
    """Character index of the occ-th (1-based) occurrence of number v in q at number boundaries, or None."""
    if not v:
        return None
    starts = [m.start() for m in re.finditer(r"(?<![\d.])" + re.escape(v) + r"(?![\d])", q)]
    k = (occ or 1) - 1
    return starts[k] if 0 <= k < len(starts) else None


def h_info(r, u, val, texts):
    """Key material of an H unit."""
    origin = u.get("origin")
    cells, tables, prose = _index(r, "cell_evidence"), _index(r, "table_evidence"), _index(r, "evidence")
    if origin == "F1-table":
        c = cells.get(u.get("evidence_ref")) or {}
        t = tables.get(c.get("table")) or {}
        where = t.get("where") or (u.get("loc") or {}).get("where")
        return {"kind": "T", "k1": ("T", norm_label(where), norm_label(c.get("row_group")), norm_label(c.get("row_label"))),
                "verified": bool(c) and val.verified(r["id"], r.get("extractor"), c.get("id")),
                "col": u.get("col"),
                "leaf": tuple(norm_label(p) for p in (u.get("column_printed") or "").split(" / "))}
    if origin == "F1-figure":
        return {"kind": "F", "k1": ("F", norm_label((u.get("loc") or {}).get("where")))}
    e = prose.get(u.get("evidence_ref")) or {}
    q = QC.normalise(e.get("quote") or "")
    v = QC.normalise(u.get("value_printed") or "")
    occ = u.get("value_occurrence")
    if texts is not None:
        t = texts.get(r["id"])
        if t is not None:
            pos = t.find(q) if q else -1
            off = _occurrence_index(q, v, occ) if pos >= 0 else None
            if off is not None:
                return {"kind": "P", "k1": ("P", origin, pos + off)}
    return {"kind": "P", "k1": ("P", origin, "quote", q.lower(), v, occ or 1)}


def match_h(rx, ry, val, texts):
    """U14 as amended by v0.5 s5.2: inside each (where, row group, row label) key, (1) pairs of column-verified
    cells match on col, one-to-one in reading order; (2) the rest by the U11 leaf parts of column_printed."""
    hx, hy = rx.get("units_h") or [], ry.get("units_h") or []
    ix = [h_info(rx, u, val, texts) for u in hx]
    iy = [h_info(ry, u, val, texts) for u in hy]
    out, mx, my = [], set(), set()
    for k1 in dict.fromkeys(i["k1"] for i in ix):
        xs = [a for a, i in enumerate(ix) if i["k1"] == k1]
        ys = [b for b, i in enumerate(iy) if i["k1"] == k1]
        if not ys:
            continue
        if k1[0] == "T":
            vx = [a for a in xs if ix[a]["verified"] and ix[a]["col"] is not None]
            vy = [b for b in ys if iy[b]["verified"] and iy[b]["col"] is not None]
            for a, b in one_to_one([ix[a]["col"] for a in vx], [iy[b]["col"] for b in vy]):
                out.append((vx[a], vy[b], "col"))
                mx.add(vx[a]), my.add(vy[b])
            rx_ = [a for a in xs if a not in mx]
            ry_ = [b for b in ys if b not in my]
            for a, b in one_to_one([ix[a]["leaf"] for a in rx_], [iy[b]["leaf"] for b in ry_]):
                out.append((rx_[a], ry_[b], "leaf"))
                mx.add(rx_[a]), my.add(ry_[b])
        else:
            for a, b in one_to_one([0] * len(xs), [0] * len(ys)):
                out.append((xs[a], ys[b], "key"))
                mx.add(xs[a]), my.add(ys[b])
    return sorted(out)


# =============================================================================================================
# Fields of the M-raw blocks (R1)
# =============================================================================================================
def _get(r, path):
    """Dotted path; 'a[].b' maps over a list. Returns (present, value); a null parent gives (False, None)."""
    cur = r
    parts = path.split(".")
    for n, p in enumerate(parts):
        if p.endswith("[]"):
            lst = cur.get(p[:-2]) if isinstance(cur, dict) else None
            if lst is None:
                return False, None
            rest = ".".join(parts[n + 1:])
            return True, [(_get(x, rest)[1] if rest else x) for x in lst]
        if not isinstance(cur, dict) or cur.get(p) is None and p != parts[-1]:
            return False, None
        cur = cur.get(p)
    return True, cur


S_ITEMS = [("S01", "study.study_type", "eq"), ("S02", "study.modality", "eq"), ("S03", "study.text_generator", "eq"),
           ("S04", "study.state_space", "jac"), ("S05", "study.task_families[].family", "jac"),
           ("S06", "study.primary_task_family", "eq"), ("S07", "study.models[].name", "eq"),
           ("S08", "study.base_checkpoints", "eq"), ("S09.training_free", "study.training.training_free", "eq"),
           ("S09.stages", "study.training.stages", "eq"), ("S09.data", "study.training.data_named", "eq"),
           ("S09.tokens", "study.training.tokens_printed", "eq"), ("S09.compute", "study.training.compute_printed", "eq"),
           ("S10.steps", "study.main_sampler.steps_printed", "eq"), ("S10.nfe", "study.main_sampler.nfe_printed", "eq"),
           ("S10.gen_length", "study.main_sampler.gen_length_printed", "eq"),
           ("S10.tokens_per_step", "study.main_sampler.tokens_per_step_printed", "eq"),
           ("S13.type", "study.credited_component.type", "eq"), ("S15", "study.limitations.categories", "jac"),
           ("S16", "study.synergy_benchmark", "eq"), ("S17", "study.focal_model", "eq"),
           ("S18", "study.focal_config", "eq")] + [(f"I{i}", f"study.inventory.I{i}", "eq") for i in range(1, 6)]
D_ITEMS = [("D01", "design.c1_channel", "jac"), ("D02", "design.c2_reveal", "eq"), ("D03", "design.c2_multimodal", "eq"),
           ("D04", "design.c3_predictor", "eq"), ("D05", "design.c3_self_conditioning", "eq"),
           ("D06", "design.c3_head_layout", "eq"), ("D07.rule", "design.c4_position.rule", "eq"),
           ("D07.blockwise", "design.c4_position.blockwise", "eq"), ("D08", "design.c4_joint_draw", "eq"),
           ("D09", "design.c4_multimodal_schedule", "eq"), ("D10", "design.c5_revision", "jac"),
           ("D11", "design.memory", "jac"), ("D15", "design.objective", "eq")] + \
          [(f"D16.D{i:02d}", f"design.provenance.D{i:02d}", "eq") for i in list(range(1, 12)) + [15]]
F_ITEMS = [("F1_status", "census.F1_status", "eq"), ("F2_codes", "census.F2_codes", "codes")] + \
          [(f"F{i}", f"census.F{i}", "eq") for i in range(3, 7)]
QA_SUB = {"QA1": "abc", "QA2": "abc", "QA3": "abd", "QA4": "nabc", "QA5": "nab", "QA6": "nabcd", "QA7": "abc",
          "QA9": "ab"}
QS_ITEMS = [(f"{q}{L}", f"qa.{q}.sub.{L}", "eq") for q, ls in QA_SUB.items() for L in ls]
CT_ITEMS = [(f"CT{i}", f"claims.CT.CT{i}", "eq") for i in range(1, 7)]
BLOCKS = {"G3 raw S": S_ITEMS, "G3 raw D": D_ITEMS, "G3 raw F": F_ITEMS, "G3 raw QA-sub": QS_ITEMS,
          "G3 raw CT": CT_ITEMS}
QA_KAPPA_ITEMS = ["QA1", "QA2", "QA3", "QA4", "QA5", "QA6", "QA7", "QA9"]
W = 1 - np.abs(np.subtract.outer(np.arange(3), np.arange(3))) / 2.0
KATTR = ["held_fixed", "budget_across_arms", "credited_ablation", "scoring"]
U8 = {"model-class": "RQ2-vs-ar", "pretraining-recipe": "RQ3-pretraining", "ar-initialisation": "RQ3-adaptation-from-ar",
      "sft": "RQ3-sft", "rl": "RQ3-rl", "distillation": "RQ3-distillation",
      "objective": "RQ3-objective-or-architecture", "architecture": "RQ3-objective-or-architecture",
      "steps-or-nfe": "RQ4-steps", "tokens-per-step": "RQ4-steps", "order-rule": "RQ4-order",
      "remasking": "RQ4-remask", "cache": "RQ4-cache", "block-or-parallel": "RQ4-parallel-or-block",
      "value-rule": "RQ4-value-rule-or-guidance", "guidance": "RQ4-value-rule-or-guidance",
      "gen-length": "RQ4-other-inference", "other": "RQ4-other-inference",
      "task-or-modality-removal": "RQ5-task-removal", "shared-vs-decoupled": "RQ5-shared-vs-decoupled",
      "component-removal": "credited-other"}


def item_value(r, path, kind):
    present, v = _get(r, path)
    if not present:
        return None
    if kind == "jac":
        if isinstance(v, list) and v and isinstance(v[0], dict):
            v = [json.dumps(x, sort_keys=True) for x in v]
        return as_set(v)
    if kind == "codes":
        return None if isna(v) else canon(sorted(str(v).split("+")))
    return canon(v)


def credit(vx, vy, kind):
    """(applicable, credit) under the NA rule."""
    if vx is None and vy is None:
        return False, 0.0
    if vx is None or vy is None:
        return True, 0.0
    if kind == "jac":
        u = vx | vy
        return True, (len(vx & vy) / len(u)) if u else 1.0
    return True, float(vx == vy)


def rq_class(g):
    return g.get("rq_class") or U8.get(g.get("factor_type"))


def pool_flag(g):
    """Derived K15 matched flag of a group (s10.3 M-pool)."""
    ok = g.get("held_fixed") == "stated" and not (g.get("other_changes") or "").strip()
    if rq_class(g) == "RQ2-vs-ar":
        sc = [a.get("scoring") for a in g.get("arms") or []]
        ok = ok and g.get("budget_across_arms") == "matched" and bool(sc) and len(set(sc)) == 1 \
            and sc[0] not in (None, "not_stated")
    return bool(ok)


def arrow_dir(strings):
    s = " ".join(x for x in strings if x)
    up, dn = ("↑" in s or "⬆" in s), ("↓" in s or "⬇" in s)
    return True if up and not dn else False if dn and not up else None


def unit_strings(u):
    return [u.get("metric_printed")] + [v.get("column_printed") for v in u.get("values") or []]


def final_sign(vals, L, arrow, ec_given, ec_val):
    """R3. vals: the extractors' non-absent higher_is_better values. Returns (final, source, routed)."""
    if arrow is not None:
        return arrow, "KA1(a) printed arrow", False
    nonnull = [v for v in vals if v is not None]
    if L is not None and all(v == L for v in nonnull):
        return L, "lookup", False
    if not ec_given:
        return None, "pending EC", True
    if ec_val is not None:
        return ec_val, "EC", True
    return None, "unsigned", True


def ka1_step(v, arrow, L):
    if v is None:
        return "c"
    if arrow is not None and v == arrow:
        return "a"
    if L is not None and v == L:
        return "b"
    return "unverifiable"


# =============================================================================================================
# Per-record comparison
# =============================================================================================================
METRICS_RATIO = ["G1 accept EA", "G1 accept EB", "G3 raw S", "G3 raw D", "G3 raw F", "G3 raw QA-sub", "G3 raw CT",
                 "G3 raw H-attr"] + [f"G3 K-attr:{f}" for f in KATTR] + \
                ["G4 F1_H", "G4 F1_G", "G4 F1_K", "G4 M-val", "G4 M-class", "G4 M-anchorG", "G4 M-sign", "G4 M-pool"]
DIAG_RATIO = ["diag:M-pool K-unit-weighted", "diag:M-anchorG null-null share", "diag:anchor_rule agreement",
              "diag:label-core share of arm matches", "diag:raw key part share (K units)", "diag:F1_K fully mapped",
              "diag:M-val fully mapped", "diag:F1_K lenient", "diag:column_unverified share (K values)",
              "diag:figure-only share (groups)", "diag:shape unclear share (figure groups)",
              "diag:sign agreement where both non-null (K units)", "diag:stored id differs from lookup"]


def compare(rx, ry, L, val, texts, ec=None):
    nd = {k: [0.0, 0.0] for k in METRICS_RATIO + DIAG_RATIO}
    icc = {}
    pairs = []          # (field, cx, cy) for per-field kappa / AC1 / flags
    # ---- G1 first-pass acceptance ----------------------------------------------------------------------------
    for name, r in (("G1 accept EA", rx), ("G1 accept EB", ry)):
        ents = [e.get("id") for f in ("evidence", "table_evidence", "cell_evidence") for e in (r.get(f) or [])]
        acc = sum(1 for e in ents if not val.failed(r["id"], r.get("extractor"), e))
        nd[name] = [float(acc), float(len(ents))]
    # ---- M-raw blocks ---------------------------------------------------------------------------------------
    for name, items in BLOCKS.items():
        for code, path, kind in items:
            vx, vy = item_value(rx, path, kind), item_value(ry, path, kind)
            ok, c = credit(vx, vy, "jac" if kind == "jac" else "eq")
            if ok:
                nd[name][0] += c
                nd[name][1] += 1
                if kind != "jac":
                    pairs.append((f"{name.split()[-1]}:{code}", vx, vy))
    # ---- H units --------------------------------------------------------------------------------------------
    hm = match_h(rx, ry, val, texts)
    hx, hy = rx.get("units_h") or [], ry.get("units_h") or []
    nd["G4 F1_H"] = [2.0 * len(hm), float(len(hx) + len(hy))]
    icc["G4 F1_H"] = (len(hm), len(hx) + len(hy) - len(hm))
    for a, b, _ in hm:
        for f in ("value_type", "arm_role", "metric_kind"):
            ok, c = credit(canon(hx[a].get(f)), canon(hy[b].get(f)), "eq")
            if ok:
                nd["G3 raw H-attr"][0] += c
                nd["G3 raw H-attr"][1] += 1
                pairs.append((f"H-attr:{f}", canon(hx[a].get(f)), canon(hy[b].get(f))))
    # ---- groups, arms ---------------------------------------------------------------------------------------
    gx, gy = rx.get("groups") or [], ry.get("groups") or []
    gm, gxo, gyo = group_match(gx, gy)
    nd["G4 F1_G"] = [2.0 * len(gm), float(len(gx) + len(gy))]
    icc["G4 F1_G"] = (len(gm), len(gx) + len(gy) - len(gm))
    n_core = n_arm = 0
    for i, j, _, am in gm:
        g, h = gx[i], gy[j]
        n_arm += len(am)
        n_core += sum(1 for p in am if p[2] == "core")
        # M-class
        ok, c = credit(rq_class(g), rq_class(h), "eq")
        if ok:
            nd["G4 M-class"][0] += c
            nd["G4 M-class"][1] += 1
        # M-anchorG (mi1)
        pos_x = {(g.get("arms") or [])[p[0]].get("arm_id"): k for k, p in enumerate(am)}
        pos_y = {(h.get("arms") or [])[p[1]].get("arm_id"): k for k, p in enumerate(am)}
        ax, ay = g.get("anchor_arm"), h.get("anchor_arm")
        if ax is None and ay is None:
            cr = 1.0
            nd["diag:M-anchorG null-null share"][0] += 1
        elif ax is None or ay is None:
            cr = 0.0
        else:
            px, py = pos_x.get(ax), pos_y.get(ay)
            cr = float(px is not None and px == py)
        nd["G4 M-anchorG"][0] += cr
        nd["G4 M-anchorG"][1] += 1
        nd["diag:M-anchorG null-null share"][1] += 1
        ok, c = credit(canon(g.get("anchor_rule")), canon(h.get("anchor_rule")), "eq")
        if ok:
            nd["diag:anchor_rule agreement"][0] += c
            nd["diag:anchor_rule agreement"][1] += 1
        # M-pool (MA1: over matched groups)
        nd["G4 M-pool"][0] += float(pool_flag(g) == pool_flag(h))
        nd["G4 M-pool"][1] += 1
        # K-attr group fields
        for f in ("held_fixed", "budget_across_arms", "credited_ablation"):
            vx_, vy_ = canon(g.get(f)), canon(h.get(f))
            ok, c = credit(vx_, vy_, "eq")
            if ok:
                nd[f"G3 K-attr:{f}"][0] += c
                nd[f"G3 K-attr:{f}"][1] += 1
                pairs.append((f"K-attr:{f}", vx_, vy_))
        for p in am:
            vx_, vy_ = canon((g.get("arms") or [])[p[0]].get("scoring")), canon((h.get("arms") or [])[p[1]].get("scoring"))
            ok, c = credit(vx_, vy_, "eq")
            if ok:
                nd["G3 K-attr:scoring"][0] += c
                nd["G3 K-attr:scoring"][1] += 1
                pairs.append(("K-attr:scoring", vx_, vy_))
    nd["diag:label-core share of arm matches"] = [float(n_core), float(n_arm)]
    for r, gs in ((rx, gx), (ry, gy)):
        fig = [g for g in gs if g.get("orientation") == "figure" or str(g.get("source_kind", "")).endswith("figure")]
        nd["diag:figure-only share (groups)"][0] += len(fig)
        nd["diag:figure-only share (groups)"][1] += len(gs)
        nd["diag:shape unclear share (figure groups)"][0] += sum(1 for g in fig if g.get("shape") == "unclear")
        nd["diag:shape unclear share (figure groups)"][1] += len(fig)
    # ---- K units --------------------------------------------------------------------------------------------
    ux, uy = rx.get("units_k") or [], ry.get("units_k") or []
    km = match_k(rx, ry, gm, L)
    nd["G4 F1_K"] = [2.0 * len(km), float(len(ux) + len(uy))]
    icc["G4 F1_K"] = (len(km), len(ux) + len(uy) - len(km))
    kml = match_k(rx, ry, gm, L, lenient_key=True)
    nd["diag:F1_K lenient"] = [2.0 * len(kml), float(len(ux) + len(uy))]
    mapped = lambda u: not any(p.startswith("raw:") for p in k_key(u, L)[:2])
    nd["diag:raw key part share (K units)"] = [float(sum(1 for u in ux + uy if not mapped(u))), float(len(ux) + len(uy))]
    nd["diag:F1_K fully mapped"] = [2.0 * sum(1 for a, b, _ in km if mapped(ux[a])),
                                    float(sum(1 for u in ux + uy if mapped(u)))]
    for r, us in ((rx, ux), (ry, uy)):
        for u in us:
            if u.get("metric_id") is not None and u.get("metric_id") != L.mkey(u.get("metric_printed")):
                nd["diag:stored id differs from lookup"][0] += 1
            if u.get("benchmark_id") is not None and u.get("benchmark_id") != L.bkey(u.get("benchmark_printed")):
                nd["diag:stored id differs from lookup"][0] += 1
            nd["diag:stored id differs from lookup"][1] += 2
            for v in u.get("values") or []:
                if v.get("cell"):
                    nd["diag:column_unverified share (K values)"][1] += 1
                    if not val.verified(r["id"], r.get("extractor"), v.get("cell")):
                        nd["diag:column_unverified share (K values)"][0] += 1
    kpairs = []
    for a, b, p in km:
        i, j, _, am = gm[p]
        g, h = gx[i], gy[j]
        amap = {(g.get("arms") or [])[q[0]].get("arm_id"): (h.get("arms") or [])[q[1]].get("arm_id") for q in am}
        u, w = ux[a], uy[b]
        vy_ = {v.get("arm_id"): v for v in w.get("values") or []}
        both_fig = bool(u.get("figure_only")) and bool(w.get("figure_only"))
        eq_n = tot = 0
        for v in u.get("values") or []:
            yarm = amap.get(v.get("arm_id"))
            if yarm is None or yarm not in vy_ or both_fig:
                continue
            tot += 1
            eq_n += int(norm_value(v.get("value_printed")) == norm_value(vy_[yarm].get("value_printed")))
        nd["G4 M-val"][0] += eq_n
        nd["G4 M-val"][1] += tot
        if mapped(u):
            nd["diag:M-val fully mapped"][0] += eq_n
            nd["diag:M-val fully mapped"][1] += tot
        kpairs.append((a, b, p))
        if u.get("higher_is_better") is not None and w.get("higher_is_better") is not None:
            nd["diag:sign agreement where both non-null (K units)"][0] += int(u["higher_is_better"] == w["higher_is_better"])
            nd["diag:sign agreement where both non-null (K units)"][1] += 1
    # M-pool K-unit-weighted diagnostic
    for p, (i, j, _, _) in enumerate(gm):
        nk = sum(1 for _, _, q in km if q == p)
        nd["diag:M-pool K-unit-weighted"][0] += nk * float(pool_flag(gx[i]) == pool_flag(gy[j]))
        nd["diag:M-pool K-unit-weighted"][1] += nk
    # ---- M-sign over sign decisions (MA1; R4) ----------------------------------------------------------------
    for p, (i, j, _, _) in enumerate(gm):
        vals_x, vals_y = defaultdict(set), defaultdict(set)
        for u in ux:
            if u.get("group_id") == gx[i].get("group_id"):
                vals_x[L.mkey(u.get("metric_printed"))].add(u.get("higher_is_better"))
        for u in uy:
            if u.get("group_id") == gy[j].get("group_id"):
                vals_y[L.mkey(u.get("metric_printed"))].add(u.get("higher_is_better"))
        for mk in [k for k in vals_x if k in vals_y]:
            sx, sy = vals_x[mk], vals_y[mk]
            vx_ = next(iter(sx)) if len(sx) == 1 else "conflict"
            vy_ = next(iter(sy)) if len(sy) == 1 else "conflict"
            if vx_ is None and vy_ is None:
                continue
            nd["G4 M-sign"][1] += 1
            nd["G4 M-sign"][0] += float(vx_ is not None and vx_ != "conflict" and vx_ == vy_)
            pairs.append(("K:higher_is_better (decision)", json.dumps(vx_), json.dumps(vy_)))
    # ---- sign coverage (MJ1; R3) -----------------------------------------------------------------------------
    signs = sign_rows(rx, ry, gm, km, L, ec)
    # ---- G5 (R7) and QA kappa counts ---------------------------------------------------------------------------
    fx = [a for a, u in enumerate(hx) if u.get("is_F1")]
    fy = [b for b, u in enumerate(hy) if u.get("is_F1")]
    f1_same = (not fx and not fy) or (len(fx) == 1 and len(fy) == 1 and (fx[0], fy[0]) in {(a, b) for a, b, _ in hm})
    sx, sy = (rx.get("study") or {}).get("main_comparison"), (ry.get("study") or {}).get("main_comparison")
    if isna(sx) and isna(sy):
        s14_same = True
    elif isinstance(sx, dict) and isinstance(sy, dict):
        s14_same = all(norm_label(sx.get(k)) == norm_label(sy.get(k)) for k in ("where", "row_group", "own_row", "baseline_row"))
    else:
        s14_same = False
    g5 = int(f1_same and s14_same)
    kap = np.zeros((len(QA_KAPPA_ITEMS), 9))
    for t, q in enumerate(QA_KAPPA_ITEMS):
        lx = (((rx.get("qa") or {}).get(q) or {}).get("score") or {}).get("low")
        ly = (((ry.get("qa") or {}).get(q) or {}).get("score") or {}).get("low")
        if lx in (0, 1, 2) and ly in (0, 1, 2) and not isinstance(lx, bool) and not isinstance(ly, bool):
            kap[t, 3 * lx + ly] += 1
    # ---- ICC raw (x, m) for ratio metrics ---------------------------------------------------------------------
    for k in METRICS_RATIO:
        if k not in icc:
            icc[k] = (nd[k][0], nd[k][1])
    claims = claim_pairs(rx, ry)
    matches = {"id": rx["id"],
               "groups": {"matched": [[gx[i].get("group_id"), gy[j].get("group_id"), round(jac, 4)] for i, j, jac, _ in gm],
                          "x_only": [gx[i].get("group_id") for i in gxo], "y_only": [gy[j].get("group_id") for j in gyo]},
               "arms": {f"{gx[i].get('group_id')}|{gy[j].get('group_id')}":
                        [[(gx[i].get("arms") or [])[p[0]].get("arm_id"), (gy[j].get("arms") or [])[p[1]].get("arm_id"), p[2]]
                         for p in am] for i, j, _, am in gm},
               "k_units": {"matched": [[ux[a].get("unit_id"), uy[b].get("unit_id")] for a, b, _ in km],
                           "x_only": [ux[a].get("unit_id") for a in range(len(ux)) if a not in {a for a, _, _ in km}],
                           "y_only": [uy[b].get("unit_id") for b in range(len(uy)) if b not in {b for _, b, _ in km}]},
               "h_units": {"matched": [[hx[a].get("unit_id"), hy[b].get("unit_id"), how] for a, b, how in hm],
                           "x_only": [hx[a].get("unit_id") for a in range(len(hx)) if a not in {a for a, _, _ in hm}],
                           "y_only": [hy[b].get("unit_id") for b in range(len(hy)) if b not in {b for _, b, _ in hm}]},
               "claims": claims["matches"]}
    counts = {"x": unit_counts(rx), "y": unit_counts(ry)}
    return {"nd": nd, "icc": icc, "kappa": kap, "g5": g5, "pairs": pairs, "signs": signs, "matches": matches,
            "claims": claims["pairs"], "counts": counts, "gm": gm, "km": km}


def unit_counts(r):
    return {"H": len(r.get("units_h") or []), "groups": len(r.get("groups") or []), "K": len(r.get("units_k") or []),
            "K values": sum(len(u.get("values") or []) for u in r.get("units_k") or [])}


def sign_rows(rx, ry, gm, km, L, ec):
    ux, uy = rx.get("units_k") or [], ry.get("units_k") or []
    ec_given = ec is not None
    ec_rec = (ec or {}).get(rx["id"])
    ec_cache = {}

    def ec_value(r, u):
        if ec_rec is None:
            return None
        key = r.get("extractor")
        if key not in ec_cache:
            gm_e, _, _ = group_match(r.get("groups") or [], ec_rec.get("groups") or [])
            ec_cache[key] = (gm_e, match_k(r, ec_rec, gm_e, L))
        gm_e, km_e = ec_cache[key]
        idx = next(k for k, z in enumerate(r.get("units_k") or []) if z is u)
        for a, b, _ in km_e:
            if a == idx:
                return (ec_rec.get("units_k") or [])[b].get("higher_is_better")
        return None

    rows = []
    mx, my = {a: b for a, b, _ in km}, {b for _, b, _ in km}
    entries = [("pair", ux[a], uy[b]) for a, b in mx.items()] + \
              [("x", ux[a], None) for a in range(len(ux)) if a not in mx] + \
              [("y", None, uy[b]) for b in range(len(uy)) if b not in my]
    for kind, u, w in entries:
        ref = u if u is not None else w
        mk = L.mkey(ref.get("metric_printed"))
        Ld = L.mdir(mk)
        strings = (unit_strings(u) if u else []) + (unit_strings(w) if w else [])
        arrow = arrow_dir(strings)
        vals = ([u.get("higher_is_better")] if u else []) + ([w.get("higher_is_better")] if w else [])
        ecv = None
        if ec_given:
            ecv = ec_value(rx, u) if u is not None else None
            if ecv is None and w is not None:
                ecv = ec_value(ry, w)
        final, source, routed = final_sign(vals, Ld, arrow, ec_given, ecv)
        rows.append({"id": rx["id"], "kind": kind, "x_unit": u.get("unit_id") if u else None,
                     "y_unit": w.get("unit_id") if w else None, "metric_key": mk, "lookup_direction": Ld,
                     "arrow": arrow, "x_value": u.get("higher_is_better") if u else "absent",
                     "y_value": w.get("higher_is_better") if w else "absent",
                     "x_step": ka1_step(u.get("higher_is_better"), arrow_dir(unit_strings(u)), Ld) if u else None,
                     "y_step": ka1_step(w.get("higher_is_better"), arrow_dir(unit_strings(w)), Ld) if w else None,
                     "routed_to_EC": routed, "final": final, "source": source})
    return rows


def _toks(s):
    return set(re.findall(r"[a-z0-9]+", QC.normalise(s or "").lower()))


def claim_pairs(rx, ry):
    """M-CL (v0.3 s10.3 diagnostic): claims matched when their prose quotes overlap by at least half of the
    shorter quote's tokens; status 'missing' for a claim one reader did not list."""
    def claims(r):
        q = defaultdict(set)
        for e in r.get("evidence") or []:
            q[e.get("cond")] |= _toks(e.get("quote"))
        return [(c.get("claim_id"), c.get("status"), q.get(c.get("claim_id"), set()))
                for c in ((r.get("claims") or {}).get("list") or [])]
    cx, cy = claims(rx), claims(ry)
    cand = []
    for i, (_, _, tx) in enumerate(cx):
        for j, (_, _, ty) in enumerate(cy):
            if tx and ty:
                ov = len(tx & ty) / min(len(tx), len(ty))
                if ov >= 0.5:
                    cand.append((-ov, i, j))
    cand.sort()
    ux, uy, m = set(), set(), []
    for _, i, j in cand:
        if i not in ux and j not in uy:
            ux.add(i), uy.add(j)
            m.append((i, j))
    pairs = [(cx[i][1], cy[j][1]) for i, j in m] + [(cx[i][1], "missing") for i in range(len(cx)) if i not in ux] + \
            [("missing", cy[j][1]) for j in range(len(cy)) if j not in uy]
    return {"pairs": pairs, "matches": [[cx[i][0], cy[j][0]] for i, j in m]}


# =============================================================================================================
# Statistics
# =============================================================================================================
def wkappa(c):
    """Linear-weighted kappa of 3x3 count tables (..., 9) (gate_oc_v05.wkappa)."""
    c = np.asarray(c, float).reshape(np.shape(c)[:-1] + (3, 3))
    n = c.sum((-1, -2), keepdims=True)
    p = c / np.maximum(n, 1)
    po = (p * W).sum((-1, -2))
    pe = (p.sum(-1)[..., :, None] * p.sum(-2)[..., None, :] * W).sum((-1, -2))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(1 - pe > 1e-12, (po - pe) / np.where(1 - pe > 1e-12, 1 - pe, 1), np.nan)


def cat_kappa(pairs):
    """Unweighted Cohen's kappa and Gwet's AC1 over (a, b) category pairs."""
    n = len(pairs)
    if n == 0:
        return None, None
    cats = sorted({str(a) for a, _ in pairs} | {str(b) for _, b in pairs})
    po = sum(str(a) == str(b) for a, b in pairs) / n
    pa = {c: sum(str(a) == c for a, _ in pairs) / n for c in cats}
    pb = {c: sum(str(b) == c for _, b in pairs) / n for c in cats}
    pe = sum(pa[c] * pb[c] for c in cats)
    kappa = (po - pe) / (1 - pe) if 1 - pe > 1e-12 else None
    q = len(cats)
    if q < 2:
        return kappa, 1.0
    pi = {c: (pa[c] + pb[c]) / 2 for c in cats}
    pe2 = sum(pi[c] * (1 - pi[c]) for c in cats) / (q - 1)
    ac1 = (po - pe2) / (1 - pe2) if 1 - pe2 > 1e-12 else None
    return kappa, ac1


def binom_cdf(c, n, p):
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(0, c + 1))


def flag_line(nf):
    """flag_thresholds.py: largest c with P(X <= c | n_f, 0.85) <= 0.01; None if none or n_f < 15."""
    if nf < 15:
        return None
    cs = [c for c in range(nf + 1) if binom_cdf(c, nf, 0.85) <= 0.01]
    return max(cs) if cs else None


def c_min(n, bad):
    """G5 line (gate_oc_v05.c_min): smallest c with P(X >= c | n, bad) <= 0.05, exact binomial."""
    for c in range(n + 1):
        if 1 - binom_cdf(c - 1, n, bad) <= 0.05 + 1e-15:
            return c
    return n + 1


def boot_index(strata_rows, B, seed):
    rng = np.random.default_rng(seed)
    return np.concatenate([s[rng.integers(0, len(s), (B, len(s)))] for s in strata_rows if len(s)], 1)


def ratio_lb(num, den, idx, q=0.05):
    s, d = num[idx].sum(1), den[idx].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        r = np.where(d > 0, s / np.where(d > 0, d, 1), np.nan)
    return None if np.all(np.isnan(r)) else float(np.nanquantile(r, q))


def pooled(num, den):
    return None if den.sum() <= 0 else float(num.sum() / den.sum())


# =============================================================================================================
# Inputs
# =============================================================================================================
def load_records(path, label):
    rows = read_jsonl(path)
    out = {}
    for r in rows:
        if "id" not in r:
            fail(f"{label}: a record has no id")
        if r["id"] in out:
            fail(f"{label}: id {r['id']} appears twice")
        out[r["id"]] = r
    return out


def effective_lists(man, repl_rows):
    lists = {s: list(v) for s, v in man["lists"].items()}
    spares = {s: list(v) for s, v in (man.get("spares") or {}).items()}
    used = set()
    for row in repl_rows:
        s, f, rp = row.get("stratum"), row.get("failed"), row.get("replacement")
        if s not in lists or f not in lists[s]:
            fail(f"replacement row names an id that is not on its stratum's list: {row}")
        if rp not in spares.get(s, []) or rp in used:
            fail(f"replacement {rp} is not an unused spare of stratum {s}")
        used.add(rp)
        lists[s][lists[s].index(f)] = rp
    return lists


def analysis_ids(mode, man, X, Y, repl_rows):
    """Record ids the mode uses, their strata and the strata order; checks the manifest."""
    if mode == "stage-a":
        if man.get("stage") != "stage-a":
            fail("stage-a mode needs a stage-a manifest")
        ids = list(man["ids"])
        order = man.get("strata_order") or sorted(set(man["stratum"].values()))
    else:
        if man.get("stage") not in ("gate", "regate"):
            fail(f"{mode} mode needs a gate manifest")
        lists = effective_lists(man, repl_rows)
        order = man.get("strata_order") or sorted(lists)
        if mode == "gate-phase1":
            k = int(man.get("per_stratum_phase1", 20))
            ids = [i for s in order for i in lists[s][:k]]
        else:
            n = len(X)
            per = n // len(order)
            if per * len(order) != n:
                fail(f"gate mode: {n} records do not split evenly into {len(order)} strata")
            ids = [i for s in order for i in lists[s][:per]]
            if set(ids) != set(X) or set(X) != set(Y):
                fail("gate mode: the records are not positions 1..n/3 of every stratum's list (after replacements)")
    allowed = set(man.get("ids") or []) | set((man.get("stratum") or {}).keys())
    for side, R in (("x", X), ("y", Y)):
        bad = sorted(set(R) - allowed)
        if bad:
            fail(f"--{side} holds ids that are not in the manifest: {bad[:5]}")
    for i in ids:
        if i not in X or i not in Y:
            fail(f"record {i} of the manifest is missing in --x or --y")
    if mode == "stage-a":
        extra = sorted((set(X) | set(Y)) - set(ids))
        if extra:
            fail(f"stage-a records not listed as Stage A ids: {extra[:5]}")
    stratum = {i: man["stratum"][i] for i in ids}
    return ids, stratum, order


def load_texts(d, ids):
    if d is None:
        return None
    out = {}
    for i in ids:
        p = Path(d) / f"{i}.txt"
        if p.exists():
            out[i] = QC.normalise(p.read_text(encoding="utf-8", errors="replace"))
    return out


def load_config(cfg_path, grid_path, expect, need_grid):
    cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
    csha = sha_file(cfg_path)
    if expect is not None and csha != expect:
        fail(f"config sha256 {csha} differs from --expect-config {expect}")
    grid = gsha = None
    if need_grid:
        if grid_path is None:
            fail("--grid is required in this mode")
        if expect is None:
            fail("--expect-config is required in this mode")
        grid = json.loads(Path(grid_path).read_text(encoding="utf-8"))
        gsha = sha_file(grid_path)
        if grid.get("model_sha256") != GR.model_sha(cfg):
            fail(f"grid model hash {grid.get('model_sha256')} differs from the config's {GR.model_sha(cfg)}")
        missing = [k for k, q in cfg["criteria"].items() if not q.get("report_only") and k not in grid["marginal"]]
        if missing:
            fail(f"grid lacks marginals for {missing}")
    return cfg, csha, grid, gsha


# =============================================================================================================
# Run
# =============================================================================================================
SPEC_RESOLUTIONS = ["R1 block items", "R2 arm Jaccard via the arm match", "R3 final-sign rule (MJ1)",
                    "R4 M-sign reader value per (group, metric key)", "R5 K-attr mean of defined fields",
                    "R6 undefined criterion fails", "R7 G5 identity", "R8 M-val without figure-only pairs",
                    "R9 v0.4 pooled ICC for comparison"]


def run(a, argv):
    mode = a.mode
    need_grid = mode in ("gate-phase1", "gate")
    for f in ("x", "y", "manifest", "lookups", "validator", "config", "out"):
        if getattr(a, f) is None:
            fail(f"--{f} is required")
    if mode == "gate" and a.phase1 is None:
        fail("--phase1 (the gate-phase1 output) is required in gate mode")
    cfg, csha, grid, gsha = load_config(a.config, a.grid, a.expect_config, need_grid)
    X, Y = load_records(a.x, "--x"), load_records(a.y, "--y")
    man = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    repl = read_jsonl(a.replacements) if a.replacements else []
    if mode != "stage-a" and bool(man.get("regate")) != bool(a.regate):
        fail("--regate must be given exactly when the manifest is a re-gate draw (seed 20264902)")
    ids, stratum, order = analysis_ids(mode, man, X, Y, repl)
    L = Lookups(a.lookups)
    val = Validator(a.validator)
    for i in ids:
        for R, side in ((X, "x"), (Y, "y")):
            if (i, R[i].get("extractor")) not in val.seen:
                fail(f"validator report has no line for {i} / {R[i].get('extractor')} (--{side})")
    ec = load_records(a.ec, "--ec") if a.ec else None
    texts = load_texts(a.texts, ids)
    out = Path(a.out)
    targets = {"stage-a": ["agreement-stage-a.json", "per-record-stage-a.csv", "matches-stage-a.jsonl",
                           "we-comparison.md", "run-stage-a.log"],
               "gate-phase1": ["agreement-gate-phase1.json", "run-gate-phase1.log"],
               "gate": ["agreement-gate.json", "per-record-gate.csv", "matches-gate.jsonl", "verdict-table.md",
                        "run-gate.log"]}[mode]
    clash = [t for t in targets if (out / t).exists()]
    if clash:
        fail(f"output exists, refusing to overwrite: {clash}")
    seeds = {"boot": a.boot_seed,
             "icc": a.icc_seed if a.icc_seed is not None else
             (cfg["bound"]["seed_stage_a"] if mode == "stage-a" else
              cfg["bound"]["seed_regate_phase1"] if a.regate else cfg["bound"]["seed_phase1"])}
    params = {"mode": mode, "seeds": seeds, "bootstrap_B": cfg["bootstrap"]["B"], "lb_quantile": cfg["bootstrap"]["lb_quantile"],
              "bound": {k: v for k, v in cfg["bound"].items()}, "n_grid": cfg["design"]["n_grid"],
              "n_cap": cfg["design"]["n_cap"], "target": cfg["design"]["target"], "regate": bool(a.regate),
              "texts_used": a.texts is not None, "ec_used": a.ec is not None, "python": platform.python_version(),
              "numpy": np.__version__}
    inputs = {"x": sha_file(a.x), "y": sha_file(a.y), "manifest": sha_file(a.manifest),
              "lookups": L.sha, "validator": val.sha, "config": csha, "config_model": GR.model_sha(cfg),
              "grid": gsha, "phase1": sha_file(a.phase1) if a.phase1 else None,
              "replacements": sha_file(a.replacements) if a.replacements else None,
              "we": sha_file(a.we) if a.we else None, "ec": sha_file(a.ec) if a.ec else None,
              "agreement.py": sha_file(__file__), "gate_rule_v05.py": sha_file(HERE / "gate_rule_v05.py"),
              "icc_check.py": sha_file(HERE / "icc_check.py"),
              "quote_check.py": sha_file(ROOT / "analysis" / "screening" / "quote_check.py")}
    res = {i: compare(X[i], Y[i], L, val, texts, ec) for i in ids}
    icc_names = GR.icc_metrics(cfg)
    xm_all = {k: (np.array([res[i]["icc"][k][0] for i in ids], float), np.array([res[i]["icc"][k][1] for i in ids], float))
              for k in icc_names}
    log = [f"{TOOL_VERSION}; python {platform.python_version()}; numpy {np.__version__}",
           "command: " + " ".join(argv), f"mode {mode}; records {len(ids)}"]

    if mode == "gate-phase1":
        U = GR.phase1_bounds(xm_all, cfg, np.random.default_rng(seeds["icc"]))     # the reference, unchanged
        theta = GR.theta_by_criterion(U, cfg, grid)
        n, P, step6 = GR.n_product(theta, cfg, grid)
        doc = {"tool": TOOL_VERSION, "mode": mode, "U_m": U, "P_hat": {str(k): v for k, v in P.items()}, "n": n,
               "step6": step6, "inputs_sha256": inputs, "seeds": seeds, "parameters": params,
               "parameters_sha256": sha_obj(params), "n_records": len(ids)}
        out.mkdir(parents=True, exist_ok=True)
        (out / "agreement-gate-phase1.json").write_text(json.dumps(doc, indent=1, sort_keys=True), encoding="utf-8")
        (out / "run-gate-phase1.log").write_text("\n".join(log + [f"n {n}; step6 {step6}"]) + "\n", encoding="utf-8")
        return doc

    # ---- pooled metrics and LB90 ----------------------------------------------------------------------------
    names = METRICS_RATIO + DIAG_RATIO
    NUM = np.array([[res[i]["nd"][k][0] for k in names] for i in ids], float)
    DEN = np.array([[res[i]["nd"][k][1] for k in names] for i in ids], float)
    KAP = np.stack([res[i]["kappa"] for i in ids])
    G5 = np.array([res[i]["g5"] for i in ids])
    rows_by = [np.array([r for r, i in enumerate(ids) if stratum[i] == s], int) for s in order]
    idx = boot_index(rows_by, cfg["bootstrap"]["B"], seeds["boot"])
    q = cfg["bootstrap"]["lb_quantile"]
    metrics = {}
    for j, k in enumerate(names):
        metrics[k] = {"point": pooled(NUM[:, j], DEN[:, j]), "LB90": ratio_lb(NUM[:, j], DEN[:, j], idx, q),
                      "numerator": float(NUM[:, j].sum()), "denominator": float(DEN[:, j].sum()),
                      "records_used": int((DEN[:, j] > 0).sum())}
    fj = [names.index(f"G3 K-attr:{f}") for f in KATTR]
    with np.errstate(invalid="ignore", divide="ignore"):
        fr = [np.where(DEN[idx, j].sum(1) > 0, NUM[idx, j].sum(1) / np.maximum(DEN[idx, j].sum(1), 1e-300), np.nan) for j in fj]
    pts = [metrics[f"G3 K-attr:{f}"]["point"] for f in KATTR]
    defined = [p for p in pts if p is not None]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        kb = np.nanmean(np.stack(fr), 0) if defined else np.full(len(idx), np.nan)
    metrics["G3 K-attr"] = {"point": float(np.mean(defined)) if defined else None,
                            "LB90": None if np.all(np.isnan(kb)) else float(np.nanquantile(kb, q)),
                            "fields": {f: metrics[f"G3 K-attr:{f}"]["point"] for f in KATTR},
                            "records_used": int((DEN[:, fj].sum(1) > 0).sum())}
    npair = KAP.sum(0).sum(-1)
    inc = [t for t in range(len(QA_KAPPA_ITEMS)) if npair[t] >= 10]
    kfull = wkappa(KAP.sum(0))
    kboot = wkappa(KAP[idx].sum(1))
    inc = [t for t in inc if not np.isnan(kfull[t])]          # kappa undefined (one category only): left out
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        kb_mean = np.nanmean(kboot[:, inc], 1) if inc else None
    metrics["G3 QA kappa"] = {"point": float(np.mean(kfull[inc])) if inc else None,
                              "LB90": (None if kb_mean is None or np.all(np.isnan(kb_mean))
                                       else float(np.nanquantile(kb_mean, q))),
                              "items_used": [QA_KAPPA_ITEMS[t] for t in inc],
                              "items_left_out": [QA_KAPPA_ITEMS[t] for t in range(len(QA_KAPPA_ITEMS)) if t not in inc],
                              "per_item": {QA_KAPPA_ITEMS[t]: (None if np.isnan(kfull[t]) else float(kfull[t]))
                                           for t in range(len(QA_KAPPA_ITEMS))},
                              "pairs_per_item": {QA_KAPPA_ITEMS[t]: int(npair[t]) for t in range(len(QA_KAPPA_ITEMS))}}
    metrics["G5 anchors"] = {"count": int(G5.sum()), "records": len(ids)}
    metrics["D credited_ablation alone"] = dict(metrics["G3 K-attr:credited_ablation"])
    diag = diagnostics(res, ids, metrics)
    signs = sign_summary(res, ids)
    doc = {"tool": TOOL_VERSION, "mode": mode, "n_records": len(ids), "metrics": metrics, "diagnostics": diag,
           "sign_coverage": signs, "inputs_sha256": inputs, "seeds": seeds, "parameters": params,
           "parameters_sha256": sha_obj(params), "spec_resolutions": SPEC_RESOLUTIONS,
           "strata": {s: int(len(r)) for s, r in zip(order, rows_by)}}
    # ---- ICC block ------------------------------------------------------------------------------------------
    b = cfg["bound"]
    rng = np.random.default_rng(seeds["icc"])
    sets = [("all", list(range(len(ids))))]
    if mode == "stage-a":
        drawn = set(man.get("drawn") or [])
        sets.append(("drawn", [r for r, i in enumerate(ids) if i in drawn]))
    iccb = {}
    for lab, rows in sets:
        rows = np.array(rows, int)
        blk = {"records": int(len(rows)), "per_metric": {}}
        for conf in ((0.80, 0.50) if mode == "stage-a" else (b["conf"],)):
            for k in icc_names:
                x, m = xm_all[k][0][rows], xm_all[k][1][rows]
                u, obs = GR.neyman_upper(x, m, rng, R=b["R"], grid=b["theta_grid"], conf=conf)
                e = blk["per_metric"].setdefault(k, {"icc_anova": None if np.isnan(obs) else obs})
                e[f"U{int(round(conf * 100))}"] = u
        pool_names = cfg["count_metrics_v04_pooled_rule"]
        xs, ms = [], []
        for k in pool_names:
            if k == "G3 K-attr":
                xs.append(sum(xm_all[f"G3 K-attr:{f}"][0][rows] for f in KATTR))
                ms.append(sum(xm_all[f"G3 K-attr:{f}"][1][rows] for f in KATTR))
            else:
                xs.append(xm_all[k][0][rows]), ms.append(xm_all[k][1][rows])
        ms = [np.rint(m).astype(np.int64) for m in ms]          # unit counts are integers for these metrics
        un, pobs = IC.upper80_neyman(xs, ms, rng, R=b["R"])
        blk["v04_pooled"] = {"metrics": pool_names, "pooled_icc": None if np.isnan(pobs) else pobs, "U_N": un}
        iccb[lab] = blk
    doc["icc"] = iccb
    reports = []
    if mode == "stage-a":
        doc["stage_a"] = stage_a_tests(res, ids, man, metrics, signs, X, Y, L, val, texts, a.we)
        reports.append(("we-comparison.md", we_markdown(doc["stage_a"])))
    else:
        ph = json.loads(Path(a.phase1).read_text(encoding="utf-8"))
        n = len(ids)
        if ph.get("n") != n:
            fail(f"gate mode: {n} records but phase 1 set n = {ph.get('n')}")
        if ph.get("inputs_sha256", {}).get("config") != csha:
            fail("gate mode: phase-1 output was computed with another config")
        verdict = decide(cfg, metrics, n, ph, grid)
        doc["verdict"] = verdict
        reports.append(("verdict-table.md", verdict_markdown(verdict, metrics, diag, signs)))
    # ---- write -----------------------------------------------------------------------------------------------
    out.mkdir(parents=True, exist_ok=True)
    (out / f"agreement-{mode}.json").write_text(json.dumps(doc, indent=1, sort_keys=True, default=str), encoding="utf-8")
    with open(out / f"per-record-{mode}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "stratum", "metric", "numerator", "denominator"])
        for r, i in enumerate(ids):
            for j, k in enumerate(names):
                w.writerow([i, stratum[i], k, NUM[r, j], DEN[r, j]])
            w.writerow([i, stratum[i], "G5 anchors", int(G5[r]), 1])
            for t, qi in enumerate(QA_KAPPA_ITEMS):
                w.writerow([i, stratum[i], f"QA kappa pairs:{qi}", int(KAP[r, t].sum()), ""])
    with open(out / f"matches-{mode}.jsonl", "w", encoding="utf-8") as f:
        for i in ids:
            m = dict(res[i]["matches"])
            m["signs"] = res[i]["signs"]
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    for name, text in reports:
        (out / name).write_text(text, encoding="utf-8")
    (out / f"run-{mode}.log").write_text("\n".join(log) + "\n", encoding="utf-8")
    return doc


def diagnostics(res, ids, metrics):
    by_field = defaultdict(list)
    for i in ids:
        for f, vx, vy in res[i]["pairs"]:
            by_field[f].append((vx, vy))
    fields = {}
    for f, ps in sorted(by_field.items()):
        k, ac1 = cat_kappa([(str(a), str(b)) for a, b in ps])
        agree = sum(str(a) == str(b) for a, b in ps)
        line = flag_line(len(ps))
        fields[f] = {"n_f": len(ps), "agreement": agree / len(ps), "kappa": k, "AC1": ac1, "flag_line": line,
                     "flagged": line is not None and agree <= line,
                     "null_vs_value_share_of_disagreements":
                         (sum(1 for a, b in ps if str(a) != str(b) and ("None" in (str(a), str(b)) or "null" in (str(a), str(b))))
                          / max(1, sum(1 for a, b in ps if str(a) != str(b))))}
    cl = [p for i in ids for p in res[i]["claims"]]
    k, ac1 = cat_kappa(cl)
    return {"per_field": fields, "M-CL": {"pairs": len(cl), "kappa": k, "AC1": ac1},
            "unit_counts": {i: res[i]["counts"] for i in ids}}


def sign_summary(res, ids):
    rows = [s for i in ids for s in res[i]["signs"]]
    n = len(rows)
    src = defaultdict(int)
    for s in rows:
        src[s["source"]] += 1
    steps = {"x": defaultdict(int), "y": defaultdict(int)}
    for s in rows:
        for side in ("x", "y"):
            if s[f"{side}_step"] is not None:
                steps[side][s[f"{side}_step"]] += 1
    routed = sum(1 for s in rows if s["routed_to_EC"])
    null = sum(1 for s in rows if s["final"] is None)
    both = [s for s in rows if s["kind"] == "pair" and s["x_value"] is not None and s["y_value"] is not None]
    agree = sum(1 for s in both if s["x_value"] == s["y_value"])
    pending = src.get("pending EC", 0)
    return {"rule": "R3: printed arrow (KA1 a) > lookup direction unless an extractor value conflicts > EC > unsigned",
            "contrasts": n,
            "final_from": {"KA1(a) printed arrow": src.get("KA1(a) printed arrow", 0), "lookup": src.get("lookup", 0),
                           "EC": src.get("EC", 0), "pending EC": pending, "unsigned": src.get("unsigned", 0)},
            "routed_to_EC": routed, "routed_share": routed / n if n else None,
            "final_null": null, "final_null_share": null / n if n else None,
            "extractor_KA1_steps": {k: dict(v) for k, v in steps.items()},
            "sign_agreement_both_given": {"agree": agree, "pairs": len(both),
                                          "share": agree / len(both) if both else None},
            "redteam_MJ1_test": {"final_null_above_0.10": (null / n > 0.10) if n else None,
                                 "routed_above_0.30": (routed / n > 0.30) if n else None,
                                 "note": "with no EC file, pending-EC units count as final null"}}


def stage_a_tests(res, ids, man, metrics, signs, X, Y, L, val, texts, we_path):
    drawn = [i for i in ids if i in set(man.get("drawn") or [])]
    wes = [i for i in ids if i in set(man.get("worked_examples") or [])]

    def f1g(sub):
        num = sum(res[i]["nd"]["G4 F1_G"][0] for i in sub)
        den = sum(res[i]["nd"]["G4 F1_G"][1] for i in sub)
        return num / den if den else None
    f_drawn, f_we = f1g(drawn), f1g(wes)
    out = {"F1_G_drawn": f_drawn, "F1_G_worked_examples": f_we, "drawn": drawn, "worked_examples": wes,
           "falsifier_F1_G_drawn_below_0.6": (f_drawn < 0.6) if f_drawn is not None else None,
           "contamination_test_drawn_more_than_0.15_below_we":
               (f_we - f_drawn > 0.15) if (f_drawn is not None and f_we is not None) else None}
    m = metrics
    ka = {f: m[f"G3 K-attr:{f}"]["point"] for f in KATTR}
    msign = m["G4 M-sign"]["point"]
    out["redteam_MA2_test"] = {"M-sign": msign, "budget_across_arms": ka["budget_across_arms"],
                               "credited_ablation": ka["credited_ablation"],
                               "fails": bool((msign is not None and msign < 0.90) or
                                             any(ka[f] is not None and ka[f] < 0.70 for f in ("budget_across_arms", "credited_ablation")))}
    out["redteam_MJ3_test"] = {k: m[k]["point"] for k in ("G4 M-anchorG", "G4 M-pool", "G4 M-class")}
    out["redteam_MJ3_test"]["any_above_0.93"] = any(v is not None and v > 0.93 for v in out["redteam_MJ3_test"].values())
    out["sign_coverage"] = signs
    if we_path is None:
        out["worked_examples_comparison"] = "not computed: --we not given (we-expected.jsonl is precondition A11)"
        return out
    WE = load_records(we_path, "--we")
    comp = {}
    for side, R in (("EA", X), ("EB", Y)):
        g = k = a_n = a_d = 0
        gx = gy = kx = ky = 0
        for i in wes:
            if i not in WE:
                continue
            e = _we_record(WE[i], R[i])
            gm, _, _ = group_match(R[i].get("groups") or [], e.get("groups") or [])
            km = match_k(R[i], e, gm, L)
            g += len(gm)
            k += len(km)
            gx += len(R[i].get("groups") or [])
            gy += len(e.get("groups") or [])
            kx += len(R[i].get("units_k") or [])
            ky += len(e.get("units_k") or [])
            for ii, jj, _, am in gm:
                pg = {(R[i]["groups"][ii].get("arms") or [])[p[0]].get("arm_id"): t for t, p in enumerate(am)}
                pe = {(e["groups"][jj].get("arms") or [])[p[1]].get("arm_id"): t for t, p in enumerate(am)}
                ax, ay = R[i]["groups"][ii].get("anchor_arm"), e["groups"][jj].get("anchor_arm")
                a_d += 1
                a_n += int((ax is None and ay is None) or (ax is not None and ay is not None and pg.get(ax) is not None
                                                           and pg.get(ax) == pe.get(ay)))
        comp[side] = {"F1_G": 2 * g / (gx + gy) if gx + gy else None, "F1_K": 2 * k / (kx + ky) if kx + ky else None,
                      "anchor_agreement": a_n / a_d if a_d else None, "matched_groups": g}
    out["worked_examples_comparison"] = comp
    return out


def _we_record(e, r):
    """A worked-example entry as a partial record (missing fields as '')."""
    rec = {"id": e["id"], "extractor": "WE", "groups": [], "units_k": []}
    for g in e.get("groups") or []:
        rec["groups"].append({"group_id": g.get("group_id"), "where": g.get("where", ""),
                              "second_factor_printed": g.get("second_factor_printed", ""),
                              "anchor_arm": g.get("anchor_arm"),
                              "arms": [{"arm_id": x.get("arm_id"), "label_printed": x.get("label_printed", "")}
                                       for x in g.get("arms") or []]})
    for u in e.get("units_k") or []:
        rec["units_k"].append({k: u.get(k, "") for k in ("unit_id", "group_id", "benchmark_printed", "metric_printed",
                                                         "condition_printed", "split")})
    return rec


def decide(cfg, metrics, n, ph, grid):
    rows, ok_all = [], True
    for k, q in cfg["criteria"].items():
        if q["kind"] == "count":
            c = c_min(n, q["bad"])
            cnt = metrics["G5 anchors"]["count"]
            ok = cnt >= c
            rows.append({"criterion": k, "line": f"count >= c({n}) = {c}", "statistic": cnt, "pass": ok, "gated": True})
            ok_all &= ok
            continue
        m = metrics.get(k) or {}
        lb = m.get("LB90")
        ok = lb is not None and lb >= q["line"] - 1e-12
        gated = not q.get("report_only")
        rows.append({"criterion": k, "line": q["line"], "statistic": lb, "point": m.get("point"), "pass": ok,
                     "gated": gated, "undefined": lb is None})
        if gated:
            ok_all &= ok
    flags = {f: metrics[f"G3 K-attr:{f}"]["point"] for f in KATTR}
    line = cfg["criteria"]["G3 K-attr"]["line"]
    step6 = None
    if ph.get("step6"):
        theta = GR.theta_by_criterion(ph["U_m"], cfg, grid)
        top = sorted(theta.items(), key=lambda kv: -kv[1])[:3]
        step6 = {"P_hat_n_cap": ph["P_hat"].get(str(cfg["design"]["n_cap"])), "largest_theta": top}
    return {"decision": "PASS" if ok_all else "FAIL", "n": n, "rows": rows,
            "kattr_fields_below_line": [f for f, v in flags.items() if v is not None and v < line],
            "step6_statement": step6}


def verdict_markdown(v, metrics, diag, signs):
    L = [f"# Gate verdict ({v['decision']}, n = {v['n']})", "",
         "| Criterion | Line | LB90 or count | Point | Pass | Gated |", "|---|---|---|---|---|---|"]
    fmt = lambda x: "undefined" if x is None else (f"{x:.3f}" if isinstance(x, float) else str(x))
    for r in v["rows"]:
        L.append(f"| {r['criterion']} | {r['line']} | {fmt(r['statistic'])} | {fmt(r.get('point'))} | "
                 f"{'yes' if r['pass'] else 'no'} | {'yes' if r['gated'] else 'report-only'} |")
    L += ["", "K-attr per-field points (line 0.71): " + ", ".join(
        f"{f} {fmt(metrics[f'G3 K-attr:{f}']['point'])}" for f in KATTR),
          f"Flagged K-attr fields: {v['kattr_fields_below_line'] or 'none'}",
          f"Fallback (s5.4): raw key share {fmt(metrics['diag:raw key part share (K units)']['point'])}; F1_K fully mapped "
          f"{fmt(metrics['diag:F1_K fully mapped']['point'])}; M-val fully mapped {fmt(metrics['diag:M-val fully mapped']['point'])}; "
          f"lenient F1_K {fmt(metrics['diag:F1_K lenient']['point'])}",
          f"Sign coverage (MJ1): {json.dumps(signs['final_from'])}; routed to EC {signs['routed_to_EC']} of {signs['contrasts']}"]
    if v["step6_statement"]:
        L.append(f"Step-6 statement: no grid n reached the target; P_hat(n_cap) {v['step6_statement']['P_hat_n_cap']}; "
                 f"largest theta_c {v['step6_statement']['largest_theta']}")
    return "\n".join(L) + "\n"


def we_markdown(s):
    L = ["# Stage A: worked examples and falsifier", "",
         f"F1_G (EA vs EB) on the 7 drawn records: {s['F1_G_drawn']}; on the 5 worked examples: {s['F1_G_worked_examples']}",
         f"Falsifier (F1_G drawn below 0.6): {s['falsifier_F1_G_drawn_below_0.6']}",
         f"Contamination test (drawn more than 0.15 below worked examples): {s['contamination_test_drawn_more_than_0.15_below_we']}",
         f"Red-team MA2 test: {json.dumps(s['redteam_MA2_test'])}", f"Red-team MJ3 test: {json.dumps(s['redteam_MJ3_test'])}",
         f"Sign coverage (MJ1): {json.dumps(s['sign_coverage']['final_from'])}; routed share {s['sign_coverage']['routed_share']}; "
         f"final-null share {s['sign_coverage']['final_null_share']}", "",
         "Each extractor against the worked-example lists:", json.dumps(s["worked_examples_comparison"], indent=1)]
    return "\n".join(L) + "\n"


# =============================================================================================================
# Self-tests (--self-test, seed 20267000; plan v0.4 s11.1 and v0.5 s11)
# =============================================================================================================
def _st_records():
    sys.path.insert(0, str(HERE / "fixtures"))
    import synth                                       # noqa: E402  (synthetic records, no paper content)
    return synth


def self_test(verbose=True):
    import tempfile
    synth = _st_records()
    rng = np.random.default_rng(SELF_TEST_SEED)
    tmp = Path(tempfile.mkdtemp(prefix="agreement-selftest-"))
    L = Lookups(synth.write_lookups(tmp / "lookups"))
    results = []

    def check(name, cond):
        results.append((name, bool(cond)))
        if verbose:
            print(f"self-test {len(results):2d} {'ok  ' if cond else 'FAIL'} {name}")

    def val_for(*recs, **kw):
        p = synth.write_jsonl(tmp / f"v{len(results)}.jsonl", synth.validator_lines(recs, **kw))
        return Validator(p)

    x, y = synth.pair("M90001")
    r = compare(x, y, L, val_for(x, y), None)
    ratios = [k for k in METRICS_RATIO if r["nd"][k][1] > 0]
    check("identical X and Y: every agreement 1 and every F1 1",
          all(abs(r["nd"][k][0] - r["nd"][k][1]) < 1e-12 for k in ratios) and r["g5"] == 1 and len(ratios) >= 18)
    y2 = copy.deepcopy(y)
    y2["groups"] = y2["groups"][:1]
    y2["units_k"] = [u for u in y2["units_k"] if u["group_id"] == "G01"]
    r = compare(x, y2, L, val_for(x, y2), None)
    check("one group removed from Y: F1_G = 2*1/(2+1)", abs(r["nd"]["G4 F1_G"][0] / r["nd"]["G4 F1_G"][1] - 2 / 3) < 1e-12)
    y3 = copy.deepcopy(y)
    y3["groups"][0]["anchor_arm"] = "A2"
    r = compare(x, y3, L, val_for(x, y3), None)
    check("swapped anchor in one of two matched groups: M-anchorG = 1/2", r["nd"]["G4 M-anchorG"] == [1.0, 2.0])
    y4 = copy.deepcopy(y)
    y4["units_k"][1]["higher_is_better"] = True
    r = compare(x, y4, L, val_for(x, y4), None)
    check("flipped higher_is_better: M-sign below 1 by one decision (2 of 3)", r["nd"]["G4 M-sign"] == [2.0, 3.0])
    y5, x5 = copy.deepcopy(y), copy.deepcopy(x)
    y5["units_k"][1]["higher_is_better"] = None
    x5["units_k"][0]["higher_is_better"] = None
    y5["units_k"][0]["higher_is_better"] = None
    r = compare(x5, y5, L, val_for(x5, y5), None)
    check("null against value is a disagreement, null-null excluded (M-sign 1 of 2)", r["nd"]["G4 M-sign"] == [1.0, 2.0])
    check("label-core: 'Model (x)' matches 'Model' via core",
          arm_match([{"label_printed": "Model (x)"}], [{"label_printed": "Model"}]) == [(0, 0, "core")]
          and arm_match([{"label_printed": "Model (x)"}], [{"label_printed": "Model (y)"}]) == [])
    xr, yr = copy.deepcopy(x), copy.deepcopy(y)
    for rr in (xr, yr):
        rr["units_k"][0]["benchmark_printed"] = "Bench-Q (Smith et al., 2024)"
    xm, ym = copy.deepcopy(x), copy.deepcopy(y)
    ym["units_k"][0]["benchmark_printed"] = "Bench-Qx"          # unmapped, while X's Bench-A is mapped
    r1 = compare(xr, yr, L, val_for(xr, yr), None)
    r2 = compare(xm, ym, L, val_for(xm, ym), None)
    check("unmapped benchmark equal in both matches as raw; mapped against unmapped does not",
          r1["nd"]["G4 F1_K"] == [6.0, 6.0] and r2["nd"]["G4 F1_K"] == [4.0, 6.0]
          and L.bkey("Bench-Q (Smith et al., 2024)") == "raw:bench-q")
    xs_, ys_ = copy.deepcopy(x), copy.deepcopy(y)
    ys_["study"]["state_space"] = ["discrete-absorbing", "hybrid"]
    a_ = item_value(xs_, "study.state_space", "jac")
    b_ = item_value(ys_, "study.state_space", "jac")
    check("set field credits the Jaccard value (1/2)", credit(a_, b_, "jac") == (True, 0.5))
    rows = [np.arange(0, 5), np.arange(5, 12)]
    i1, i2 = boot_index(rows, 200, 123), boot_index(rows, 200, 123)
    check("stratified bootstrap reproducible with the same seed, and within strata",
          np.array_equal(i1, i2) and i1[:, :5].max() < 5 and i1[:, 5:].min() >= 5)
    t1 = np.isnan(IC.icc_anova(np.array([3, 3]), np.array([4, 4])))
    t2 = abs(IC.icc_anova(np.array([4] * 6), np.array([5] * 6))) < 1e-12
    t3 = IC.icc_anova(np.array([5, 0, 5, 0, 5, 0]), np.array([5] * 6)) > 0.9
    mm = rng.negative_binomial(1.5, 1.5 / (1.5 + 8), 4000)
    aa = 1 / 0.3 - 1
    est = float(IC.icc_anova(rng.binomial(mm, rng.beta(0.6 * aa, 0.4 * aa, 4000)), mm))
    check("icc_anova reproduces icc_check self-tests 1-2 (hand cases; recovery of ICC 0.30)",
          t1 and t2 and t3 and abs(est - 0.30) < 0.05)
    check("G5 line c(n): 43 of 60, 51 of 72, 63 of 90, 72 of 105, 82 of 120",
          [c_min(n, 0.60) for n in (60, 72, 90, 105, 120)] == [43, 51, 63, 72, 82])
    # gate_rule_v05 self-tests 1-2 (bisection; product rule on a hand grid)
    ok = all(GR.largest_true(n, lambda i, c=cut: i <= c) == cut for n, cut in ((30, -1), (30, 0), (30, 13), (30, 29), (1, 0), (2, 1)))
    g = {"theta": [0.05, 0.10, 0.20], "n": [60, 90, 120],
         "marginal": {"A": [[0.99, 1, 1], [0.95, 0.99, 1], [0.80, 0.93, 0.97]],
                      "B": [[0.99, 1, 1], [0.90, 0.97, 0.99], [0.70, 0.88, 0.95]]},
         "joint": [[0.98, 1, 1], [0.855, 0.96, 0.99], [0.56, 0.82, 0.92]]}
    c2 = {"design": {"n_cap": 120, "target": 0.85}, "criteria": {"A": {"icc_from": ["A"]}, "B": {"icc_from": ["B"]}}}
    ok &= GR.n_product({"A": 0.10, "B": 0.10}, c2, g)[0] == 60 and GR.n_product({"A": 0.20, "B": 0.10}, c2, g)[0] == 90
    ok &= GR.n_product({"A": 0.20, "B": 0.20}, {"design": {"n_cap": 90, "target": 0.85}, "criteria": c2["criteria"]}, g)[::2] == (90, True)
    check("gate_rule_v05 self-tests 1-2 (bisection, product rule, n_cap and step-6 flag)", ok)
    fx = HERE / "fixtures" / "phase1-bounds-fixture.json"
    if fx.exists():
        fxd = json.loads(fx.read_text(encoding="utf-8"))
        cfg = json.loads((HERE / "gate-config-v05.json").read_text(encoding="utf-8"))
        b = cfg["bound"]
        rr = np.random.default_rng(b["seed_phase1"])
        U = {k: GR.neyman_upper(np.array(fxd["xm"][k][0], float), np.array(fxd["xm"][k][1], float), rr,
                                R=b["R"], grid=b["theta_grid"], conf=b["conf"])[0] for k in GR.icc_metrics(cfg)}
        check("phase-1 bounds reproduce the stored fixture (20 metrics, config order, one Generator)", U == fxd["U"])
    else:
        check("phase-1 bounds fixture present (analysis/extraction/fixtures/phase1-bounds-fixture.json)", False)
    # v0.5 additions
    x6, y6 = copy.deepcopy(x), copy.deepcopy(y)
    x6["groups"][1]["arms"].append(synth.arm("A3", "Model-Z extra"))
    x6["groups"][1]["anchor_arm"] = "A3"
    y6["groups"][1]["anchor_arm"] = "A1"
    r = compare(x6, y6, L, val_for(x6, y6), None)
    gm = r["gm"]
    check("a mapped anchor that falls on an unmatched arm scores 0 (M-anchorG 1 of 2)",
          len(gm) == 2 and r["nd"]["G4 M-anchorG"] == [1.0, 2.0])
    x7, y7 = copy.deepcopy(x), copy.deepcopy(y)
    for rr_ in (x7, y7):
        rr_["groups"][1]["arms"] = [synth.arm("A1", "Twin"), synth.arm("A2", "Twin")]
    x7["groups"][1]["anchor_arm"], y7["groups"][1]["anchor_arm"] = "A1", "A2"
    r_a = compare(x7, y7, L, val_for(x7, y7), None)["nd"]["G4 M-anchorG"]
    y7["groups"][1]["anchor_arm"] = "A1"
    r_b = compare(x7, y7, L, val_for(x7, y7), None)["nd"]["G4 M-anchorG"]
    check("two arms sharing a label key score 0 unless both anchors map to one matched pair",
          r_a == [1.0, 2.0] and r_b == [2.0, 2.0])
    x8, y8 = copy.deepcopy(x), copy.deepcopy(y)
    y8["groups"][0]["held_fixed"] = "co-varied"                       # held_fixed 1/2
    y8["groups"][0]["arms"][1]["scoring"] = "likelihood"             # scoring 4/5
    r = compare(x8, y8, L, val_for(x8, y8), None)["nd"]
    rates = [r[f"G3 K-attr:{f}"][0] / r[f"G3 K-attr:{f}"][1] for f in KATTR]
    check("K-attr equals the mean of the four field rates on a hand case ((0.5 + 1 + 1 + 0.8) / 4)",
          rates == [0.5, 1.0, 1.0, 0.8] and abs(np.mean(rates) - 0.825) < 1e-12)
    x9, y9 = copy.deepcopy(x), copy.deepcopy(y)
    y9["groups"][1]["held_fixed"] = "stated"                          # flips G02's derived flag only (1 K unit)
    r = compare(x9, y9, L, val_for(x9, y9), None)["nd"]
    check("M-pool on a two-group record weights groups (1/2), not units (2/3 K-unit-weighted)",
          r["G4 M-pool"] == [1.0, 2.0] and r["diag:M-pool K-unit-weighted"] == [2.0, 3.0])
    x10, y10 = copy.deepcopy(x), copy.deepcopy(y)
    x10["units_k"][0]["metric_printed"] = "Acc ↑"                     # K01: arrow -> KA1(a)
    for rr_ in (x10, y10):
        rr_["units_k"][2]["metric_printed"] = "Cohesion index"        # K03: unmapped -> EC
        rr_["units_k"][2]["higher_is_better"] = None
    # K02 PPL: lookup false, extractors false -> lookup
    s = compare(x10, y10, L, val_for(x10, y10), None)["signs"]
    srcs = [z["source"] for z in s]
    ec10 = copy.deepcopy(y10)
    ec10["extractor"] = "EC-claude-fable-5-1"
    ec10["units_k"][2]["higher_is_better"] = True                      # EC rules K03 from a stated sentence
    s_ec = compare(x10, y10, L, val_for(x10, y10), None, {"M90001": ec10})["signs"]
    check("sign coverage (MJ1): arrow, lookup, routed to EC; EC value used when given",
          srcs == ["KA1(a) printed arrow", "lookup", "pending EC"] and [z["routed_to_EC"] for z in s] == [False, False, True]
          and s_ec[2]["source"] == "EC" and s_ec[2]["final"] is True)
    check("final-sign rule: extractor conflict with the lookup is routed; a null extractor value is not a conflict",
          final_sign([True], False, None, False, None)[1] == "pending EC" and final_sign([None], False, None, False, None)[1] == "lookup")
    n_ok = sum(1 for _, c in results if c)
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    if verbose:
        print(f"self-tests passed {n_ok}/{len(results)}")
    return n_ok, len(results), results


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mode", choices=["stage-a", "gate-phase1", "gate"])
    ap.add_argument("--x")
    ap.add_argument("--y")
    ap.add_argument("--manifest")
    ap.add_argument("--lookups")
    ap.add_argument("--validator")
    ap.add_argument("--config", default=str(HERE / "gate-config-v05.json"))
    ap.add_argument("--grid")
    ap.add_argument("--expect-config")
    ap.add_argument("--phase1")
    ap.add_argument("--replacements")
    ap.add_argument("--regate", action="store_true")
    ap.add_argument("--we")
    ap.add_argument("--ec")
    ap.add_argument("--texts")
    ap.add_argument("--out")
    ap.add_argument("--boot-seed", type=int, default=BOOT_SEED)
    ap.add_argument("--icc-seed", type=int)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        ok, n, _ = self_test()
        return 0 if ok == n else 1
    if a.mode is None:
        ap.error("--mode is required unless --self-test")
    run(a, ["agreement.py"] + list(argv))
    return 0


if __name__ == "__main__":
    sys.exit(main())
