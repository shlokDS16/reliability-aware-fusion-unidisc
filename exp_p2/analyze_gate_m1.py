"""CPU analysis of M1 (and the CPU fallback of v2 section 11.4): per-item AUROC of every score against the changed-code map, per corruption, plus the paired
bootstrap of q against the best cheap baseline. Reads only; writes runs/<m1-run>/analysis.json and tbv_verdict.json (if TbV arrays exist).

    python -m exp_p2.analyze_gate_m1 --probe-run P2-PROBE-02 --m1-run P2-GATE-M1 [--no-pixels] [--codebook runs/P2-GATE-M1/codebook.npy]

Without M1 arrays there is no q and no TbV: the table covers s1, s2, s3, r_original, plain-B, random and the cheap baselines, and the output says
'exploratory' with the item count. No model is loaded and no GPU is touched."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import artifacts, baselines, detect, jsonl, seeds                                   # noqa: E402


DRY_RUN_N, N_M1 = 21, 200          # the first 21 probe-2 items were seen in the CPU dry run (SAP A1.2); the complete M1 set is 200
MIN_N_PARTIAL = 100                # SAP A3b.12a: the one floor of the partial M1 pool (rival eligibility, S-D, K2) ...
MIN_N_CHANCE_BAR = MIN_N_PARTIAL   # ... and of the chance bar (A3b.5 item 4): the red team's number, a design choice, not derived
CHANCE_CELLS = ("patch/plainB", "patch/q", "swap/plainB", "swap/q")


def _cell_status(table: dict | None, key: str, min_n: int) -> str:
    """decided_pass / decided_fail / undecided for one cell in one pool, from the per-cell n and lower95 only (the `passes` field of the input is ignored)."""
    v = (table or {}).get("per_score", {}).get(key)
    if not v or not v.get("available") or v.get("n", 0) < min_n or v.get("lower95") is None:
        return "undecided"
    return "decided_pass" if v["lower95"] > 0.5 else "decided_fail"


def combine_chance_bars(cb_all: dict, cb_late: dict | None, n_all: int, n_late: int, min_n: int = MIN_N_CHANCE_BAR) -> dict:
    """SAP AB.7 item 3 as completed by A3b.5 and A3b.5a. The chance bar has two pools: all items of the closed prefix (pool A) and the items after the 21 dry-run items (pool L). It is recomputed
    HERE from the per-cell tables (`per_score[cell]` with `available`, `n`, `mean`, `lower95`); the `passes` and `failed` fields of the inputs are ignored. A cell-pool is decided only if it is
    available and n >= `min_n` (100): lower95 > 0.5 is decided_pass, otherwise decided_fail; anything else (n below the floor, a missing key, no late pool) is undecided. A cell fails if either
    pool is decided_fail, passes if both are decided_pass, else is undecided. Verdict: PASSED iff all four cells pass; FAILED iff any cell fails (a decided failure is not hidden by an undecided
    cell); else UNDECIDED, which is never read as a pass and triggers no audit. `passes` is True / False / None for PASSED / FAILED / UNDECIDED. Pure function: no data are read here."""
    per, fail_cells, pass_cells, flag = {}, [], [], []
    for key in CHANCE_CELLS:
        sa, sl = _cell_status(cb_all, key, min_n), _cell_status(cb_late, key, min_n)
        res = "fail" if "decided_fail" in (sa, sl) else ("pass" if (sa, sl) == ("decided_pass", "decided_pass") else "undecided")
        va = (cb_all or {}).get("per_score", {}).get(key)
        vl = (cb_late or {}).get("per_score", {}).get(key) if cb_late else None
        per[key] = dict(all=va, late=vl, n_all_cell=(va or {}).get("n"), n_late_cell=(vl or {}).get("n"), status_all=sa, status_late=sl, result=res,
                        passes_both=(True if res == "pass" else False if res == "fail" else None))
        (fail_cells if res == "fail" else pass_cells if res == "pass" else []).append(key)
        if res != "fail" and any(v and v.get("available") and v.get("mean") is not None and v["mean"] <= 0.5 for v in (va, vl)):
            flag.append(key)
    verdict = "FAILED" if fail_cells else ("PASSED" if len(pass_cells) == len(CHANCE_CELLS) else "UNDECIDED")
    return dict(verdict=verdict, passes=(True if verdict == "PASSED" else False if verdict == "FAILED" else None), failed=verdict == "FAILED", audit_trigger=verdict == "FAILED",
                min_n=min_n, n_all=n_all, n_late=n_late, complete=bool(n_all == N_M1), per_score=per, audit_flag_point_estimate=flag,
                rule="SAP A3b.5 / A3b.5a: a cell-pool is decided only if n >= 100; PASSED iff all four cells pass in both pools; FAILED iff any cell fails; otherwise UNDECIDED (never a pass); "
                     "failure = pipeline audit, nothing tuned; a point estimate <= 0.5 in a cell that has not failed is a descriptive flag only")


def run_analysis(probe_dir: Path, m1_dir: Path | None, *, pixels: bool = True, codebook: np.ndarray | None = None, n_boot: int = 10000, min_n: int | None = None) -> dict:
    """`min_n` (SAP A3b.12a item 5; None = the 200-item behaviour) is the floor of the partial pool for rival eligibility, S-D and K2 (`detect` functions); the chance bar always uses MIN_N_CHANCE_BAR."""
    sel = json.loads((probe_dir / "selection.json").read_text(encoding="utf8"))["items"]
    files = sorted((probe_dir / "arrays").glob("item*.npz"))
    idxs = [int(f.stem[4:]) for f in files]
    if idxs != list(range(len(idxs))):                                                    # A3b.5a item 4(a): the pool is a contiguous prefix 0..k-1
        raise ValueError(f"the probe-2 arrays are not a contiguous prefix: found item indices {idxs}, expected {list(range(len(idxs)))}")
    arrs = {i: np.load(f) for i, f in zip(idxs, files)}
    clean_codes = {i: np.asarray(a["clean"], np.int64) for i, a in arrs.items()}
    total = np.zeros(16384)
    for c in clean_codes.values():
        total += np.bincount(c, minlength=16384)
    per_item, have_m1, n_with_q = [], False, 0
    for i in idxs:
        a = arrs[i]
        mp = (m1_dir / "arrays" / f"item{i:04d}.npz") if m1_dir is not None else None
        m1 = np.load(mp) if mp is not None and mp.exists() else None
        have_m1 = have_m1 or m1 is not None
        n_with_q += int(m1 is not None and all(f"{c}_D" in m1 for c in detect.P2_CORRS))
        freq = baselines.CodeFreq(total - np.bincount(clean_codes[i], minlength=16384))          # leave-one-item-out clean-code frequencies
        raw = common.load_image(sel[i]["image_id"]) if pixels else None
        rec = {}
        for corr in detect.P2_CORRS:
            codes = np.asarray(a[f"{corr}_codes"], np.int64)
            extra = dict(rarity=freq.rarity(codes), nbr=baselines.neighbour_codebook_distance(codes, codebook, detect.GRID),
                         tex=baselines.patch_texture(detect.regen_pixels(raw, i, corr) if pixels else None, detect.GRID))
            extra = {k: v for k, v in extra.items() if not np.isnan(v).any()}
            extra |= {k + "_neg": -v for k, v in list(extra.items())}          # sign-oracle rivals: the cheap baselines get the better of both orientations
            sus = detect.suspicions(a, corr, i, m1, extra)
            rec[corr] = detect.item_aurocs(sus, np.asarray(a[f"{corr}_z"], bool))
        per_item.append(rec)
    late = [r for r, i in zip(per_item, idxs) if i >= DRY_RUN_N]                      # excludes the 21 dry-run items (179 of 200 when M1 is complete)
    cb_all = dict(detect.chance_bar(per_item, n_boot=n_boot), note="descriptive, no minimum n; the binding bar is chance_bar_both (SAP A3b.5)")
    cb_late = dict(detect.chance_bar(late, n_boot=n_boot), note="descriptive, no minimum n; the binding bar is chance_bar_both (SAP A3b.5)") if late else None      # the pool without the 21 dry-run items (SAP AB.7 item 3)
    out = dict(labels=dict(tbv=baselines.TBV_LABEL), meta=seeds.meta(), n_items=len(idxs), n_items_with_q=n_with_q, item_idx=idxs, has_q=have_m1, label="exploratory (not preregistered)" if len(idxs) < N_M1 or not have_m1 else "M1 detection table",
               pool=dict(n_items=len(idxs), n_late=len(late), last_idx=(idxs[-1] if idxs else None), complete=bool(len(idxs) >= N_M1),
                         item_idx_sha256=hashlib.sha256(json.dumps(idxs).encode()).hexdigest()), min_n=min_n,
               table=detect.aggregate(per_item, n_boot=n_boot), paired_q_vs_best_cheap={c: detect.paired_vs_best_cheap(per_item, c, "q", n_boot=n_boot, min_n=min_n) for c in detect.P2_CORRS},
               falsifier=detect.falsifier(per_item, "q", n_boot=n_boot, min_n=min_n),
               falsifier_rival_reselected_in_each_resample=detect.falsifier(per_item, "q", n_boot=n_boot, reselect=True, min_n=min_n),
               falsifier_excluding_dry_run_items=dict(n_items=len(late), **detect.falsifier(late, "q", n_boot=n_boot, min_n=min_n)) if late else None,
               chance_bar=cb_all, chance_bar_after_dry_run=cb_late, chance_bar_both=combine_chance_bars(cb_all, cb_late, len(per_item), len(late)),
               frozen=detect.freeze_rivals(per_item, min_n=min_n), rows_report=jsonl.probe2_row_report(probe_dir, idxs))
    if m1_dir is not None and (m1_dir / "items.jsonl").exists():
        rows = [r for r in common.read_jsonl(m1_dir / "items.jsonl") if r.get("tbv")]
        if rows:
            frac = float(np.mean([np.mean([v["copy_suspected"] for v in r["tbv"].values()]) for r in rows]))
            out["tbv"] = dict(label=baselines.TBV_LABEL, n_items=len(rows), frac_items_copy_suspected=frac, copy_suspected=bool(frac > 0.5))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-run", default="P2-PROBE-02")
    ap.add_argument("--m1-run", default="P2-GATE-M1")
    ap.add_argument("--no-pixels", action="store_true", help="skip regenerating jpeg/noise pixels (texture baseline becomes NaN and is dropped)")
    ap.add_argument("--codebook", default=None)
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--force", action="store_true", help="overwrite an existing detection_frozen.json / analysis.json (kept as .prev-<time>, logged as an amendment)")
    ap.add_argument("--closed-k", type=int, default=None, help="SAP A3b.12: k of the M1 closing row (items with probe-2 arrays); with --closed-nq it enables the partial detection_frozen.json")
    ap.add_argument("--closed-nq", type=int, default=None, help="SAP A3b.12: n_q of the M1 closing row (items with all four D arrays)")
    ap.add_argument("--out-dir", default=None, help="where to write analysis.json (default: the M1 run dir); use runs/P2-GATE-CPU for the partial-data fallback")
    a = ap.parse_args(argv)
    probe, m1 = Path(common.RUNS) / a.probe_run, Path(common.RUNS) / a.m1_run
    cbp = Path(a.codebook) if a.codebook else m1 / "codebook.npy"
    closed = a.closed_k is not None and a.closed_nq is not None
    if (a.closed_k is None) != (a.closed_nq is None):
        print("STOP: --closed-k and --closed-nq go together (the two numbers of the closing row)", file=sys.stderr)
        return 2
    res = run_analysis(probe, m1 if m1.exists() else None, pixels=not a.no_pixels, codebook=np.load(cbp) if cbp.exists() else None, n_boot=a.boot, min_n=MIN_N_PARTIAL if closed else None)
    complete = res["n_items_with_q"] >= N_M1 and res["n_items"] >= N_M1
    if closed and (res["n_items"] != a.closed_k or res["n_items_with_q"] != a.closed_nq):
        print(f"STOP: the closing row says k = {a.closed_k}, n_q = {a.closed_nq} but the run directories hold k = {res['n_items']}, n_q = {res['n_items_with_q']}; nothing is written (SAP A3b.12 rule 8)", file=sys.stderr)
        return 2
    closed_partial = bool(closed and not complete)
    out = Path(a.out_dir) if a.out_dir else m1
    out.mkdir(parents=True, exist_ok=True)
    (out / "analysis.json").write_text(json.dumps(res, indent=1), encoding="utf8")
    if "tbv" in res:
        (out / "tbv_verdict.json").write_text(json.dumps(res["tbv"], indent=1), encoding="utf8")
    if complete or closed_partial:                      # complete: q for ALL 200 items (SAP A1.2 rule 5; audit M8); partial: only with the closing row's k and n_q (SAP A3b.12 rules 2 and 8)
        doc = dict(meta=res["meta"], frozen=res["frozen"], n_items=res["n_items"], dry_run_items=DRY_RUN_N, source="analyze_gate_m1 on the complete M1 set")
        if closed_partial:
            doc.update(partial=True, closed_k=a.closed_k, closed_nq=a.closed_nq, min_n=MIN_N_PARTIAL, source="analyze_gate_m1 on the closed partial M1 pool")
        try:
            artifacts.write_once(out / "detection_frozen.json", json.dumps(doc, indent=1), a.force)
        except artifacts.WriteOnceError as e:
            print("STOP:", e, file=sys.stderr)
            return 2
        print("wrote detection_frozen.json" + (f" (PARTIAL: closed k = {a.closed_k}, n_q = {a.closed_nq}, min_n = {MIN_N_PARTIAL})" if closed_partial else "") + ": commit it before M3/M4")
    else:
        why = f"needs q for all {N_M1} items; have {res['n_items_with_q']} of {res['n_items']}"
        if not closed:
            why += "; a partial freeze needs --closed-k K --closed-nq Q equal to the M1 closing row (SAP A3b.12 rule 8)"
        print(f"detection_frozen.json NOT written ({why})")
    print(json.dumps({k: res[k] for k in ("n_items", "has_q", "label")}, indent=1))
    cb = res["chance_bar_both"]
    print(f"chance bar (patch/swap, plain-B and q; decided only at n >= {cb['min_n']} per cell and pool; lower 95% bound > 0.5 on the closed prefix AND on items 21 and later): {cb['verdict']}",
          f"n_all={cb['n_all']} n_late={cb['n_late']}" + ("" if cb["complete"] else f" (computed on the completed prefix of k = {cb['n_all']} items, not {N_M1})"))
    for k, v in cb["per_score"].items():
        print("  ", k, "n_all", v["n_all_cell"], "n_late", v["n_late_cell"], "lower95", [round(x["lower95"], 3) if x and x.get("available") else None for x in (v["all"], v["late"])], v["status_all"], v["status_late"], "->", v["result"])
    if cb["verdict"] == "FAILED":
        print("  FAILED: run the pipeline audit (A2.3); nothing is tuned")
    elif cb["verdict"] == "UNDECIDED":
        print(f"  UNDECIDED: n below {cb['min_n']} in at least one cell-pool; not a pass")
    if cb["audit_flag_point_estimate"]:
        print("  descriptive flag (point estimate <= 0.5, cell not failed):", cb["audit_flag_point_estimate"])
    print("probe-2 rows report:", {k: v for k, v in res["rows_report"].items() if k != "rows_without_arrays"})
    for corr, t in res["table"].items():
        print(corr, {k: round(v["mean"], 3) for k, v in t.items() if not k.startswith("_")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
