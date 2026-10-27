"""CPU analysis of M1 (and the CPU fallback of v2 section 11.4): per-item AUROC of every score against the changed-code map, per corruption, plus the paired
bootstrap of q against the best cheap baseline. Reads only; writes runs/<m1-run>/analysis.json and tbv_verdict.json (if TbV arrays exist).

    python -m exp_p2.analyze_gate_m1 --probe-run P2-PROBE-02 --m1-run P2-GATE-M1 [--no-pixels] [--codebook runs/P2-GATE-M1/codebook.npy]

Without M1 arrays there is no q and no TbV: the table covers s1, s2, s3, r_original, plain-B, random and the cheap baselines, and the output says
'exploratory' with the item count. No model is loaded and no GPU is touched."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import artifacts, baselines, detect, jsonl, seeds                                   # noqa: E402


DRY_RUN_N, N_M1 = 21, 200          # the first 21 probe-2 items were seen in the CPU dry run (SAP A1.2); the complete M1 set is 200


def run_analysis(probe_dir: Path, m1_dir: Path | None, *, pixels: bool = True, codebook: np.ndarray | None = None, n_boot: int = 10000) -> dict:
    sel = json.loads((probe_dir / "selection.json").read_text(encoding="utf8"))["items"]
    files = sorted((probe_dir / "arrays").glob("item*.npz"))
    idxs = [int(f.stem[4:]) for f in files]
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
    out = dict(meta=seeds.meta(), n_items=len(idxs), n_items_with_q=n_with_q, item_idx=idxs, has_q=have_m1, label="exploratory (not preregistered)" if len(idxs) < N_M1 or not have_m1 else "M1 detection table",
               table=detect.aggregate(per_item, n_boot=n_boot), paired_q_vs_best_cheap={c: detect.paired_vs_best_cheap(per_item, c, "q", n_boot=n_boot) for c in detect.P2_CORRS},
               falsifier=detect.falsifier(per_item, "q", n_boot=n_boot),
               falsifier_rival_reselected_in_each_resample=detect.falsifier(per_item, "q", n_boot=n_boot, reselect=True),
               falsifier_excluding_dry_run_items=dict(n_items=len(late), **detect.falsifier(late, "q", n_boot=n_boot)) if late else None,
               frozen=detect.freeze_rivals(per_item), rows_report=jsonl.probe2_row_report(probe_dir, idxs))
    if m1_dir is not None and (m1_dir / "items.jsonl").exists():
        rows = [r for r in common.read_jsonl(m1_dir / "items.jsonl") if r.get("tbv")]
        if rows:
            frac = float(np.mean([np.mean([v["copy_suspected"] for v in r["tbv"].values()]) for r in rows]))
            out["tbv"] = dict(n_items=len(rows), frac_items_copy_suspected=frac, copy_suspected=bool(frac > 0.5))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-run", default="P2-PROBE-02")
    ap.add_argument("--m1-run", default="P2-GATE-M1")
    ap.add_argument("--no-pixels", action="store_true", help="skip regenerating jpeg/noise pixels (texture baseline becomes NaN and is dropped)")
    ap.add_argument("--codebook", default=None)
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--force", action="store_true", help="overwrite an existing detection_frozen.json / analysis.json (kept as .prev-<time>, logged as an amendment)")
    ap.add_argument("--out-dir", default=None, help="where to write analysis.json (default: the M1 run dir); use runs/P2-GATE-CPU for the partial-data fallback")
    a = ap.parse_args(argv)
    probe, m1 = Path(common.RUNS) / a.probe_run, Path(common.RUNS) / a.m1_run
    cbp = Path(a.codebook) if a.codebook else m1 / "codebook.npy"
    res = run_analysis(probe, m1 if m1.exists() else None, pixels=not a.no_pixels, codebook=np.load(cbp) if cbp.exists() else None, n_boot=a.boot)
    out = Path(a.out_dir) if a.out_dir else m1
    out.mkdir(parents=True, exist_ok=True)
    (out / "analysis.json").write_text(json.dumps(res, indent=1), encoding="utf8")
    if "tbv" in res:
        (out / "tbv_verdict.json").write_text(json.dumps(res["tbv"], indent=1), encoding="utf8")
    if res["n_items_with_q"] >= N_M1 and res["n_items"] >= N_M1:                      # frozen only when q exists for ALL 200 items (SAP A1.2 rule 5; audit M8)
        try:
            artifacts.write_once(out / "detection_frozen.json", json.dumps(dict(meta=res["meta"], frozen=res["frozen"], n_items=res["n_items"], dry_run_items=DRY_RUN_N,
                                                                                  source="analyze_gate_m1 on the complete M1 set"), indent=1), a.force)
        except artifacts.WriteOnceError as e:
            print("STOP:", e, file=sys.stderr)
            return 2
        print("wrote detection_frozen.json: commit it before M3/M4")
    else:
        print(f"detection_frozen.json NOT written (needs q for all {N_M1} items; have {res['n_items_with_q']} of {res['n_items']})")
    print(json.dumps({k: res[k] for k in ("n_items", "has_q", "label")}, indent=1))
    print("probe-2 rows report:", {k: v for k, v in res["rows_report"].items() if k != "rows_without_arrays"})
    for corr, t in res["table"].items():
        print(corr, {k: round(v["mean"], 3) for k, v in t.items() if not k.startswith("_")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
