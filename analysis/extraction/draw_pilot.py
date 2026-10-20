"""Seeded draws of the extraction pilot (EXTRACTION-PLAN-v0.5 s10.2, s10.7, s11; v0.4 s10.2; v0.3 s10.2-s10.3;
red-team audit 5 mn1). Frames as analysis/extraction/strata.py (same files and rules, overrides and confirmed
duplicates applied) under the multimodal option the human author chose (v0.4 s2.3, options a-d of
multimodal_options.py). Stdlib only.

Run from the worktree root:
  python -I analysis/extraction/draw_pilot.py --stage {stage-a|gate|mi4|regate} --option {a|b|c|d} --dry-run
  python -I analysis/extraction/draw_pilot.py --stage <stage> --option <o> --i-have-the-decision-row D00xx
      [--stage-a-manifest P] [--gate-manifest P] [--mi4-manifest P] [--spares K] [--out P]
  python -I analysis/extraction/draw_pilot.py --self-test     (built-in synthetic fixtures; exit 0 if all pass)

--dry-run prints counts only (frame sizes, pool sizes, how many would be drawn), draws nothing and writes nothing.
Without --dry-run the tool refuses to write a draw unless --i-have-the-decision-row names a row that exists in
research/ledgers/decisions.jsonl, Python is 3.14.3 (random.sample is pinned by version), every manifest it
depends on is given and was drawn on the same frames and option, and the output file does not exist.

Draws (seeds: plan v0.5 s2.10):
  stage-a  random.Random(20261100), one generator over the pools in this order, without replacement across pools,
           the five worked-example ids excluded from every pool (v0.4 s10.2): C1 i1=ab 1, C1 i1=b 1, C2 2, frame-R
           benchmark/analysis-title pool 1, frame R + C2 above 133,280 bytes 1, frame R 1. The 12 Stage A ids are the
           five worked examples plus these seven.
  gate     strata G-short, G-long (the i1 = a, non-nonlang-only frame split at its median text size) and G-mm (C1),
           h = 0, 1, 2; Stage A ids excluded; random.Random(20261200 + h).sample(sorted(pool), L + K): positions
           1..L are the ordered list (L = per_stratum_list of gate-config-v05.json, phase 1 = its first
           per_stratum_phase1), positions L+1..L+K are spares reserved for the replacement rule of s10.7 step 2
           (mn1). The tool checks that the first L ids equal sample(sorted(pool), L), so the spares never change the list.
  mi4      random.Random(20266200).sample(sorted(frame R minus Stage A ids minus every gate list and spare id), 5).
  regate   as gate with seeds 20261300 + h, excluding Stage A ids, mi4 ids and every id of the first gate's lists and
           spares (s10.7 step 8).

Spec gaps resolved (also written into each manifest under "resolutions"):
  P1 "Frame R + C2" (gate strata, Stage A size pool) = every i1 = a, non-nonlang-only include (FR + C2 + C2b), the
     same 543 records under every option; the option moves records between C2, C2b and FR only.
  P2 Under option (a) C2 is empty; Stage A's two "C2" draws then use the mm-rule C2 (records that sit in frame R
     under (a)), labelled "C2 (mm rule)".
  P3 Options (c) and (d) need analysis/extraction/mm-construct.jsonl (the human check of OQ4-04/OQ5-04); without it a
     dry run uses the provisional inputs of multimodal_options.py (SIDE list; confirmed joint record only) and a
     real draw is refused.
  P4 Spares K per gate stratum come from --spares (required for a gate or re-gate draw) because the config holds no
     spare count; K <= 45 keeps CPython's sampling method unchanged (checked).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TOOL = "draw_pilot.py 1.0.1 (extraction form v0.5)"
PY_PINNED = "3.14.3"
WORKED_EXAMPLES = ["M07474", "M12766", "M09530", "M13864", "M08100"]
SEED_STAGE_A, SEED_GATE, SEED_REGATE, SEED_MI4 = 20261100, 20261200, 20261300, 20266200
LARGE_BYTES = 133280
BENCH_TITLE = re.compile(r"benchmark|evaluat|analy[sz]|empirical|revisit|rethink|investigat|probing|understanding", re.I)
STAGE_A_POOLS = [("C1-ab", 1), ("C1-b", 1), ("C2", 2), ("FR-bench-title", 1), ("FRC2-large", 1), ("FR", 1)]
GATE_STRATA = ["G-short", "G-long", "G-mm"]
MI4_N = 5
RESOLUTIONS = ["P1 frame R + C2 = all i1=a non-nonlang-only includes under every option",
               "P2 option (a): Stage A C2 draws from the mm-rule C2",
               "P3 options (c), (d) need mm-construct.jsonl for a real draw",
               "P4 spares per gate stratum from --spares (<= 45)"]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


STRATA = _load("strata_v03", HERE / "strata.py")                    # KW rule (unchanged)
MMO = _load("multimodal_options_v04", HERE / "multimodal_options.py")  # SIDE, JOINT_CONFIRMED (provisional inputs)


class Refused(SystemExit):
    pass


def refuse(msg):
    raise Refused(f"draw_pilot.py: {msg} (nothing written)")


def sha_ids(ids):
    return hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def jl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


# =============================================================================================================
# Frames (strata.py rules)
# =============================================================================================================
def paths(root):
    root = Path(root)
    return {"dec": root / "analysis/screening/ft-t1/t1-decisions-all.jsonl", "ft1": root / "analysis/screening/ft-t1",
            "corpus": [(root / "research/review/corpus/new-records-2026-10-15-v2.jsonl", "nid"),
                       (root / "research/review/corpus/subscription-records-2026-10-15.jsonl", "id"),
                       (root / "research/review/screening/records.jsonl", "sid")],
            "texts": root / "research/sources/md/fulltext-pymupdf",
            "overrides": root / "analysis/extraction/strata-overrides.jsonl",
            "dups": root / "analysis/extraction/duplicate-works.jsonl",
            "construct": root / "analysis/extraction/mm-construct.jsonl",
            "config": root / "analysis/extraction/gate-config-v05.json"}


def load_records(root):
    """Per include: i1, nonlang_only, mm_final, KW hits, title, text size (strata.py)."""
    P = paths(root)
    dec = {r["id"]: r for r in jl(P["dec"])}
    inc = sorted(i for i, r in dec.items() if r["decision"] == "include")
    A, B, C = {}, {}, {}
    for d in sorted(P["ft1"].glob("t1b0*")):
        for role, st in (("A", A), ("B", B)):
            for r in jl(d / f"F{role}-{d.name}.jsonl"):
                st[r["id"]] = r
    sup = {(r["id"], r["group"]) for r in jl(P["ft1"] / "c-superseded.jsonl")}
    for f in sorted(P["ft1"].glob("c/c-t1-*/FC-*.jsonl")):
        for r in jl(f):
            if (r["id"], f.parent.name) not in sup:
                C[r["id"]] = r
    meta = {}
    for path, key in P["corpus"]:
        if not path.exists():
            continue
        for r in jl(path):
            i = r.get(key)
            if i in dec and i not in meta and (r.get("title") or "").strip():
                meta[i] = {"title": r.get("title") or "", "abstract": r.get("abstract") or ""}

    def mm_final(i):
        if i in C and C[i].get("mm"):
            return C[i]["mm"]
        ma, mb = A.get(i, {}).get("mm"), B.get(i, {}).get("mm")
        if ma and mb:
            return ma if ma == mb else "split:" + "/".join(sorted([ma, mb]))
        return ma or mb or "none"

    recs = {}
    for i in inc:
        t, ab = meta.get(i, {}).get("title", ""), meta.get(i, {}).get("abstract", "")
        recs[i] = {"i1": dec[i]["i1"], "nl": bool(dec[i]["nonlang_only"]), "mm": mm_final(i),
                   "kw": bool(STRATA.KW.search(t)) or bool(STRATA.KW.search(ab)), "title": t,
                   "size": os.path.getsize(P["texts"] / f"{i}.txt")}
    return recs, sha_file(P["dec"])


def base_frames(recs, overrides, drop):
    """strata.py: C1, NL, C2 (mm rule), FR; overrides applied last; confirmed duplicates leave C1, C2, FR."""
    C1, NL, C2, FR = [], [], [], []
    for i in sorted(recs):
        x = recs[i]
        if x["i1"] in ("b", "ab"):
            C1.append(i)
            continue
        if x["nl"]:
            NL.append(i)
            continue
        m = x["mm"]
        mmc = x["kw"] if (m.startswith("split:") and "multimodal" in m) else (m == "multimodal")
        if i in overrides:
            mmc = overrides[i] == "multimodal"
        (C2 if mmc else FR).append(i)
    keep = lambda v: [i for i in v if i not in drop]
    return {"C1": keep(C1), "NL": NL, "C2": keep(C2), "FR": keep(FR)}


def option_frames(base, option, construct):
    """Options a-d of multimodal_options.py. construct: None (provisional) or {id: class}."""
    C2, FR = base["C2"], base["FR"]
    if construct is None:
        side = sorted(set(MMO.SIDE) & set(C2))
        joint = sorted(set(MMO.JOINT_CONFIRMED) & set(FR))
    else:
        side = sorted(i for i in C2 if construct.get(i) == "side-experiment")
        joint = sorted(i for i in FR if construct.get(i) == "joint")
    if option == "a":
        c2, c2b, fr = [], [], sorted(FR + C2)
    elif option == "b":
        c2, c2b, fr = list(C2), [], list(FR)
    elif option == "c":
        c2 = sorted((set(C2) - set(side)) | set(joint))
        c2b, fr = [], sorted((set(FR) - set(joint)) | set(side))
    elif option == "d":
        c2 = sorted((set(C2) - set(side)) | set(joint))
        c2b, fr = list(side), sorted(set(FR) - set(joint))
    else:
        refuse(f"unknown option {option}")
    union = sorted(set(c2) | set(c2b) | set(fr))
    assert union == sorted(set(C2) | set(FR)), "option frames must partition FR + C2 (P1)"
    return {"C1": base["C1"], "NL": base["NL"], "C2": c2, "C2b": c2b, "FR": fr, "RC2": union, "C2_mm_rule": C2}


def median(v):
    s = sorted(v)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def stage_a_pools(fr, recs, option):
    c2 = fr["C2"] if fr["C2"] else fr["C2_mm_rule"]                      # P2
    return {"C1-ab": [i for i in fr["C1"] if recs[i]["i1"] == "ab"],
            "C1-b": [i for i in fr["C1"] if recs[i]["i1"] == "b"],
            "C2": c2,
            "FR-bench-title": [i for i in fr["FR"] if BENCH_TITLE.search(recs[i]["title"])],
            "FRC2-large": [i for i in fr["RC2"] if recs[i]["size"] > LARGE_BYTES],
            "FR": fr["FR"]}


def gate_strata(fr, recs):
    med = median([recs[i]["size"] for i in fr["RC2"]])
    return ({"G-short": [i for i in fr["RC2"] if recs[i]["size"] <= med],
             "G-long": [i for i in fr["RC2"] if recs[i]["size"] > med],
             "G-mm": list(fr["C1"])}, med)


# =============================================================================================================
# Draws (pure functions on id lists; tested on synthetic frames)
# =============================================================================================================
def draw_stage_a(pools, exclude=WORKED_EXAMPLES, seed=SEED_STAGE_A):
    rng = random.Random(seed)
    taken, out = set(exclude), []
    for name, k in STAGE_A_POOLS:
        avail = sorted(set(pools[name]) - taken)
        if len(avail) < k:
            refuse(f"Stage A pool {name} has {len(avail)} ids, needs {k}")
        pick = rng.sample(avail, k)
        out += [(i, name) for i in pick]
        taken |= set(pick)
    return out


def draw_gate(strata, exclude, list_len, spares, seed0):
    if not 0 <= spares <= 45:
        refuse("--spares must be between 0 and 45 (P4)")
    lists, sp, seeds = {}, {}, {}
    for h, name in enumerate(GATE_STRATA):
        avail = sorted(set(strata[name]) - set(exclude))
        if len(avail) < list_len + spares:
            refuse(f"gate stratum {name} has {len(avail)} ids, needs {list_len + spares}")
        full = random.Random(seed0 + h).sample(avail, list_len + spares)
        if full[:list_len] != random.Random(seed0 + h).sample(avail, list_len):
            refuse("spares changed the ordered list (sampling method switch); use fewer spares")
        lists[name], sp[name], seeds[name] = full[:list_len], full[list_len:], seed0 + h
    return lists, sp, seeds


def draw_mi4(frame_r, exclude, seed=SEED_MI4, n=MI4_N):
    avail = sorted(set(frame_r) - set(exclude))
    if len(avail) < n:
        refuse(f"mi4 pool has {len(avail)} ids, needs {n}")
    return random.Random(seed).sample(avail, n)


# =============================================================================================================
# Self-test (built-in synthetic frames and a synthetic data tree in a temporary folder; no real frame is read and
# nothing is written outside the temporary folder)
# =============================================================================================================
def _st_jw(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def _st_tree(root, n_c1=60, n_a=240):
    """Synthetic decisions, screener rows, corpus, texts (sparse files for sizes), config copy and ledger."""
    rng = random.Random(7)
    root = Path(root)
    dec, fa, fb, corpus, ids = [], [], [], [], []
    texts = root / "research/sources/md/fulltext-pymupdf"
    texts.mkdir(parents=True)
    for k in range(n_c1):
        i = "M12766" if k == 0 else f"C{k:05d}"
        dec.append({"id": i, "decision": "include", "i1": "ab" if k % 2 == 0 else "b", "nonlang_only": False})
        ids.append(i)
    for k in range(n_a):
        i = "M09530" if k == 0 else f"A{k:05d}"
        mm = "multimodal" if k % 5 == 1 else "text"
        fa.append({"id": i, "mm": "multimodal" if k == 2 else mm})
        fb.append({"id": i, "mm": "text" if k == 2 else mm})
        dec.append({"id": i, "decision": "include", "i1": "a", "nonlang_only": k % 40 == 39})
        ids.append(i)
    dec.append({"id": "X00001", "decision": "exclude", "i1": None, "nonlang_only": False})
    for n, i in enumerate(ids):
        title = "A benchmark of synthetic decoding" if n % 9 == 0 else "Synthetic diffusion model " + i
        corpus.append({"nid": i, "title": "Image captioning with a synthetic model" if i == "A00002" else title,
                       "abstract": "synthetic"})
        with open(texts / f"{i}.txt", "wb") as f:
            f.truncate(140000 if n % 13 == 0 else 20000 + rng.randrange(100000))
    ft1 = root / "analysis/screening/ft-t1"
    _st_jw(ft1 / "t1-decisions-all.jsonl", dec)
    _st_jw(ft1 / "t1b001" / "FA-t1b001.jsonl", fa)
    _st_jw(ft1 / "t1b001" / "FB-t1b001.jsonl", fb)
    _st_jw(ft1 / "c-superseded.jsonl", [])
    _st_jw(ft1 / "c" / "c-t1-01" / "FC-c-t1-01.jsonl", [{"id": "A00003", "mm": "multimodal"}])
    _st_jw(root / "research/review/corpus/new-records-2026-10-15-v2.jsonl", corpus)
    (root / "analysis/extraction").mkdir(parents=True, exist_ok=True)
    (root / "analysis/extraction/gate-config-v05.json").write_bytes((HERE / "gate-config-v05.json").read_bytes())
    _st_jw(root / "research/ledgers/decisions.jsonl", [{"id": "D0099", "decision": "synthetic self-test row"}])
    return root


def self_test(verbose=True):
    """Returns the number of failed checks (0 = all passed)."""
    import io  # noqa: PLC0415
    import tempfile  # noqa: PLC0415
    from contextlib import redirect_stdout  # noqa: PLC0415
    results = []

    def check(desc, fn):
        try:
            ok = bool(fn())
        except Exception as exc:  # noqa: BLE001 -- a crashing check is a failed check
            ok, desc = False, f"{desc} [{type(exc).__name__}: {exc}]"
        results.append(ok)
        if verbose:
            print(f"self-test {len(results):2d} {'ok  ' if ok else 'FAIL'} {desc}")

    def refused(fn):
        try:
            fn()
        except Refused:
            return True
        return False

    pools = {"C1-ab": [f"a{i}" for i in range(10)] + ["M12766"], "C1-b": [f"b{i}" for i in range(10)],
             "C2": [f"c{i}" for i in range(20)], "FR-bench-title": [f"f{i}" for i in range(5)] + ["M09530"],
             "FRC2-large": [f"c{i}" for i in range(3)] + [f"f{i}" for i in range(4)], "FR": [f"f{i}" for i in range(30)]}

    def stage_a_rule():
        out = draw_stage_a(pools)
        rng, taken, exp = random.Random(SEED_STAGE_A), set(WORKED_EXAMPLES), []
        for name, k in STAGE_A_POOLS:
            pick = rng.sample(sorted(set(pools[name]) - taken), k)
            exp += pick
            taken |= set(pick)
        ids = [i for i, _ in out]
        return (ids == exp and len(set(ids)) == 7 and not set(ids) & set(WORKED_EXAMPLES)
                and [p for _, p in out] == [p for p, k in STAGE_A_POOLS for _ in range(k)] and draw_stage_a(pools) == out)
    check("stage-a: one seeded generator over the pools in order, no replacement, worked examples excluded", stage_a_rule)
    check("stage-a: a pool with too few ids is refused",
          lambda: refused(lambda: draw_stage_a(dict(pools, C2=["c0"]))))
    strata = {"G-short": [f"s{i:03d}" for i in range(80)], "G-long": [f"l{i:03d}" for i in range(80)],
              "G-mm": [f"m{i:03d}" for i in range(53)]}

    def gate_rule():
        lists, sp, seeds = draw_gate(strata, ["s001", "m000"], 40, 5, SEED_GATE)
        ok = seeds == {s: SEED_GATE + h for h, s in enumerate(GATE_STRATA)}
        for h, s in enumerate(GATE_STRATA):
            avail = sorted(set(strata[s]) - {"s001", "m000"})
            ok = ok and len(sp[s]) == 5 and lists[s] == random.Random(SEED_GATE + h).sample(avail, 40) \
                and not set(lists[s] + sp[s]) & {"s001", "m000"}
        return ok and draw_gate(strata, ["s001", "m000"], 40, 0, SEED_GATE)[0] == lists
    check("gate: ordered lists of 40 per stratum, seeds 20261200 + h, spares leave the list unchanged", gate_rule)
    check("gate: more than 45 spares, or a stratum too small for list + spares, is refused",
          lambda: refused(lambda: draw_gate(strata, [], 40, 46, SEED_GATE))
          and refused(lambda: draw_gate(strata, [], 40, 14, SEED_GATE)))
    fr = [f"f{i:03d}" for i in range(20)]
    check("mi4: five ids from frame R minus every excluded id, seed 20266200",
          lambda: draw_mi4(fr, fr[:14]) == random.Random(SEED_MI4).sample(fr[14:], 5) and refused(lambda: draw_mi4(fr, fr[:16])))
    base = {"C1": ["c1"], "NL": ["n1"], "C2": ["m1", "m2", "s1"], "FR": ["r1", "r2", "j1"]}
    construct = {"s1": "side-experiment", "j1": "joint", "m1": "joint"}

    def options():
        f = {o: option_frames(base, o, construct) for o in "abcd"}
        return (f["a"]["C2"] == [] and f["b"]["C2"] == base["C2"] and f["c"]["C2"] == ["j1", "m1", "m2"]
                and f["c"]["FR"] == ["r1", "r2", "s1"] and f["d"]["C2b"] == ["s1"] and f["d"]["FR"] == ["r1", "r2"]
                and all(x["RC2"] == sorted(base["C2"] + base["FR"]) for x in f.values()))
    check("options a-d move records between C2, C2b and FR only (P1)", options)
    recs = {"c1": {"i1": "ab", "nl": False, "mm": "text", "kw": False}, "n1": {"i1": "a", "nl": True, "mm": "text", "kw": False},
            "m1": {"i1": "a", "nl": False, "mm": "multimodal", "kw": False},
            "s1": {"i1": "a", "nl": False, "mm": "split:multimodal/text", "kw": True},
            "s2": {"i1": "a", "nl": False, "mm": "split:multimodal/text", "kw": False},
            "o1": {"i1": "a", "nl": False, "mm": "text", "kw": False}}
    check("frames: C1, NL, mm rule (split decided by KW), overrides last, confirmed duplicates dropped",
          lambda: base_frames(recs, {"o1": "multimodal"}, {"s1"}) == {"C1": ["c1"], "NL": ["n1"], "C2": ["m1", "o1"], "FR": ["s2"]})
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        tree = _st_tree(tmp / "data")
        common = ["--data-root", str(tree), "--ledger", str(tree / "research/ledgers/decisions.jsonl")]

        def cli(*args):
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(list(args) + common)
            return code, buf.getvalue()

        def listing(p):
            return sorted(str(q.relative_to(p)) for q in p.rglob("*") if q.is_file())
        before = listing(tmp)

        def dry():
            outs = [cli("--stage", st, "--option", "b", "--dry-run") for st in ("stage-a", "gate", "mi4", "regate")]
            return all(c == 0 and "DRY RUN" in o and "M12766" not in o for c, o in outs) and listing(tmp) == before
        check("dry runs print counts only and write nothing", dry)
        sa = tmp / "sa.json"
        check("a real draw without an existing decision row is refused and writes nothing",
              lambda: refused(lambda: cli("--stage", "stage-a", "--option", "b", "--out", str(sa)))
              and refused(lambda: cli("--stage", "stage-a", "--option", "b", "--out", str(sa), "--i-have-the-decision-row", "D0100"))
              and not sa.exists())
        row = ["--i-have-the-decision-row", "D0099"]
        if platform.python_version() == PY_PINNED:
            def sequence():
                cli("--stage", "stage-a", "--option", "b", "--out", str(sa), *row)
                m = json.loads(sa.read_text(encoding="utf-8"))
                cli("--stage", "stage-a", "--option", "b", "--out", str(tmp / "sa2.json"), *row)
                m2 = json.loads((tmp / "sa2.json").read_text(encoding="utf-8"))
                gt = tmp / "gate.json"
                cli("--stage", "gate", "--option", "b", "--stage-a-manifest", str(sa), "--spares", "4", "--out", str(gt), *row)
                g = json.loads(gt.read_text(encoding="utf-8"))
                gids = [i for s in g["lists"] for i in g["lists"][s] + g["spares"][s]]
                return (m["ids"][:5] == WORKED_EXAMPLES and len(m["drawn"]) == 7 and m["ids"] == m2["ids"]
                        and refused(lambda: cli("--stage", "stage-a", "--option", "b", "--out", str(sa), *row))
                        and len(set(gids)) == 132 and not set(gids) & set(m["ids"]))
            check("synthetic sequence: stage-a manifest (5 worked examples + 7 drawn, reproducible, no overwrite), "
                  "gate lists disjoint from Stage A", sequence)
        else:
            check(f"a real draw under Python {platform.python_version()} (not {PY_PINNED}) is refused",
                  lambda: refused(lambda: cli("--stage", "stage-a", "--option", "b", "--out", str(sa), *row)))
    n_fail = results.count(False)
    if verbose:
        print(f"self-tests passed {len(results) - n_fail}/{len(results)}")
    return n_fail


# =============================================================================================================
# CLI
# =============================================================================================================
def read_manifest(p, stage, option, frames_sha):
    if p is None:
        return None
    m = json.loads(Path(p).read_text(encoding="utf-8"))
    if m.get("stage") != stage:
        refuse(f"{p} is a {m.get('stage')} manifest, expected {stage}")
    if option is not None and m.get("option") != option:
        refuse(f"{p} was drawn under option {m.get('option')}, not {option}")
    if frames_sha is not None and m.get("frames_sha256") != frames_sha:
        refuse(f"{p} was drawn on other frames (frames_sha256 differs)")
    return m


def gate_ids(m):
    return [i for v in list(m["lists"].values()) + list((m.get("spares") or {}).values()) for i in v]


def check_decision_row(row, ledger):
    if not row:
        refuse("a draw is written only with --i-have-the-decision-row <row id>")
    if not re.fullmatch(r"D\d{4,}", row):
        refuse(f"decision row id {row!r} is not of the form D0000")
    lp = Path(ledger)
    if not lp.exists():
        refuse(f"decision ledger {lp} not found")
    if not any(r.get("id") == row for r in jl(lp)):
        refuse(f"decision row {row} is not in {lp}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Seeded draws of the extraction pilot (plan v0.5 s10.2, s10.7).")
    ap.add_argument("--stage", choices=["stage-a", "gate", "mi4", "regate"])
    ap.add_argument("--option", choices=["a", "b", "c", "d"],
                    help="multimodal construct chosen by the human author (plan v0.4 s2.3)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--i-have-the-decision-row", dest="row")
    ap.add_argument("--ledger", default=str(ROOT / "research/ledgers/decisions.jsonl"))
    ap.add_argument("--stage-a-manifest")
    ap.add_argument("--gate-manifest")
    ap.add_argument("--mi4-manifest")
    ap.add_argument("--spares", type=int)
    ap.add_argument("--out")
    ap.add_argument("--data-root", default=str(ROOT))
    ap.add_argument("--self-test", action="store_true",
                    help="built-in synthetic frames and tree in a temporary folder; exit 0 if all pass, else 1")
    a = ap.parse_args(argv)
    if a.self_test:
        return 1 if self_test() else 0
    if not (a.stage and a.option):
        ap.error("--stage and --option are required (or --self-test)")

    P = paths(a.data_root)
    cfg = json.loads(P["config"].read_text(encoding="utf-8"))
    L, L1, nstrata = (cfg["design"]["per_stratum_list"], cfg["design"]["per_stratum_phase1"], cfg["design"]["strata"])
    if nstrata != len(GATE_STRATA):
        refuse(f"config declares {nstrata} gate strata; this tool draws {len(GATE_STRATA)}")
    recs, dec_sha = load_records(a.data_root)
    overrides = {r["id"]: r["mm"] for r in jl(P["overrides"])} if P["overrides"].exists() else {}
    drop = {r["drop"] for r in jl(P["dups"])} if P["dups"].exists() else set()
    construct = {r["id"]: r["class"] for r in jl(P["construct"])} if P["construct"].exists() else None
    provisional = a.option in ("c", "d") and construct is None
    base = base_frames(recs, overrides, drop)
    fr = option_frames(base, a.option, construct)
    frames_sha = hashlib.sha256(json.dumps({k: sha_ids(v) for k, v in sorted(fr.items())}, sort_keys=True).encode()).hexdigest()
    sa = read_manifest(a.stage_a_manifest, "stage-a", a.option, None if a.dry_run else frames_sha)
    gm = read_manifest(a.gate_manifest, "gate", a.option, None if a.dry_run else frames_sha)
    mi = read_manifest(a.mi4_manifest, "mi4", a.option, None if a.dry_run else frames_sha)
    sa_ids = list(sa["ids"]) if sa else []

    if a.dry_run:
        print(f"{TOOL}; python {platform.python_version()} (pinned {PY_PINNED}); option ({a.option}); DRY RUN: counts only, "
              f"nothing drawn, nothing written")
        print("frames: " + "  ".join(f"{k} {len(fr[k])}" for k in ("C1", "C2", "C2b", "FR", "NL", "RC2")) +
              f"  (overrides {len(overrides)}, duplicates dropped {len(drop)}, construct "
              f"{'file' if construct is not None else 'provisional' if a.option in ('c', 'd') else 'not used'})")
        if provisional:
            print("  options (c)/(d) without mm-construct.jsonl: provisional inputs; a real draw is refused (P3)")
        if a.stage == "stage-a":
            pools = stage_a_pools(fr, recs, a.option)
            print(f"stage-a: seed {SEED_STAGE_A}; worked examples excluded {len(WORKED_EXAMPLES)}; would draw 7")
            for name, k in STAGE_A_POOLS:
                avail = len(set(pools[name]) - set(WORKED_EXAMPLES))
                print(f"  pool {name:<15} size {len(pools[name]):4d}  available {avail:4d}  draw {k}")
        elif a.stage in ("gate", "regate"):
            strata, med = gate_strata(fr, recs)
            excl = set(sa_ids) | (set(gate_ids(gm)) | set(mi["ids"]) if a.stage == "regate" and gm and mi else set())
            k = a.spares or 0
            print(f"{a.stage}: seeds {(SEED_GATE if a.stage == 'gate' else SEED_REGATE)} + h; list {L} per stratum "
                  f"(phase 1 {L1}), spares {k}; median {med:,.0f} bytes; excluded ids {len(excl)}"
                  + ("" if sa else " (no Stage A manifest given: counts are upper bounds)"))
            for name in GATE_STRATA:
                print(f"  stratum {name:<8} size {len(strata[name]):4d}  available {len(set(strata[name]) - excl):4d}  "
                      f"would draw {L + k}")
        else:
            excl = set(sa_ids) | (set(gate_ids(gm)) if gm else set())
            print(f"mi4: seed {SEED_MI4}; frame R {len(fr['FR'])}; available {len(set(fr['FR']) - excl)}; would draw {MI4_N}"
                  + ("" if (sa and gm) else " (Stage A or gate manifest not given: counts are upper bounds)"))
        return 0

    # ---- real draw ---------------------------------------------------------------------------------------------
    check_decision_row(a.row, a.ledger)
    if platform.python_version() != PY_PINNED:
        refuse(f"Python {platform.python_version()} is not the pinned {PY_PINNED}")
    if provisional:
        refuse("options (c) and (d) need analysis/extraction/mm-construct.jsonl (P3)")
    out = Path(a.out) if a.out else ROOT / "analysis/extraction/draws" / f"{a.stage}-option-{a.option}-manifest.json"
    if out.exists():
        refuse(f"{out} exists")
    common = {"tool": TOOL, "tool_sha256": sha_file(__file__), "python": platform.python_version(),
              "decision_row": a.row, "option": a.option, "frames_sha256": frames_sha,
              "frame_sizes": {k: len(v) for k, v in fr.items()}, "frame_list_sha256": {k: sha_ids(v) for k, v in fr.items()},
              "inputs_sha256": {"decisions": dec_sha, "gate_config": sha_file(P["config"]),
                                "strata.py": sha_file(HERE / "strata.py"),
                                "multimodal_options.py": sha_file(HERE / "multimodal_options.py"),
                                "overrides": sha_file(P["overrides"]) if P["overrides"].exists() else None,
                                "duplicates": sha_file(P["dups"]) if P["dups"].exists() else None,
                                "construct": sha_file(P["construct"]) if P["construct"].exists() else None},
              "resolutions": RESOLUTIONS}
    if a.stage == "stage-a":
        drawn = draw_stage_a(stage_a_pools(fr, recs, a.option))
        ids = WORKED_EXAMPLES + [i for i, _ in drawn]
        stratum = {i: "WE" for i in WORKED_EXAMPLES}
        stratum.update(dict(drawn))
        man = {"stage": "stage-a", "seed": SEED_STAGE_A, "ids": ids, "stratum": stratum,
               "strata_order": ["WE"] + [p for p, _ in STAGE_A_POOLS], "worked_examples": WORKED_EXAMPLES,
               "drawn": [i for i, _ in drawn],
               "pools": {n: {"size": len(v), "sha256": sha_ids(v)} for n, v in stage_a_pools(fr, recs, a.option).items()}}
    elif a.stage in ("gate", "regate"):
        if sa is None:
            refuse("a gate draw needs --stage-a-manifest")
        if a.spares is None:
            refuse("a gate draw needs --spares (P4)")
        excl = set(sa_ids)
        seed0 = SEED_GATE
        if a.stage == "regate":
            if gm is None or mi is None:
                refuse("a re-gate draw needs --gate-manifest and --mi4-manifest")
            excl |= set(gate_ids(gm)) | set(mi["ids"])
            seed0 = SEED_REGATE
        strata, med = gate_strata(fr, recs)
        lists, sp, seeds = draw_gate(strata, excl, L, a.spares, seed0)
        stratum = {i: s for s in GATE_STRATA for i in lists[s] + sp[s]}
        man = {"stage": a.stage, "seeds": seeds, "lists": lists, "spares": sp, "per_stratum_list": L,
               "per_stratum_phase1": L1, "strata_order": GATE_STRATA, "stratum": stratum,
               "ids": [i for s in GATE_STRATA for i in lists[s] + sp[s]], "median_bytes": med,
               "excluded": {"n": len(excl), "sha256": sha_ids(excl)},
               "strata": {s: {"size": len(v), "sha256": sha_ids(v)} for s, v in strata.items()}}
        if a.stage == "regate":
            man["stage"] = "gate"            # agreement.py reads re-gate lists as a gate manifest
            man["regate"] = True
    else:
        if sa is None or gm is None:
            refuse("the mi4 draw needs --stage-a-manifest and --gate-manifest (gate lists are drawn first)")
        excl = set(sa_ids) | set(gate_ids(gm))
        ids = draw_mi4(fr["FR"], excl)
        man = {"stage": "mi4", "seed": SEED_MI4, "ids": ids, "excluded": {"n": len(excl), "sha256": sha_ids(excl)}}
    man.update(common)
    man["depends_on"] = {k: sha_file(v) for k, v in (("stage_a_manifest", a.stage_a_manifest),
                                                    ("gate_manifest", a.gate_manifest),
                                                    ("mi4_manifest", a.mi4_manifest)) if v}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(man, indent=1, sort_keys=True), encoding="utf-8")
    print(f"wrote {out} (sha256 {sha_file(out)}); add a ledger row citing it before any session")
    return 0


if __name__ == "__main__":
    sys.exit(main())
