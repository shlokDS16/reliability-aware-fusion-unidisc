"""M1 post-hoc job (v2 section 11.1): after probe 2 is completed UNCHANGED (existing driver, items 21-199), add what probe 2 did not store.

    python -m exp_p2.run_gate_m1 --resume --soft-minutes 12.5 [--limit N] [--tbv] [--run-id P2-GATE-M1]
    python -m exp_p2.analyze_gate_m1 --probe-run P2-PROBE-02 --m1-run P2-GATE-M1     # CPU: AUROC table, paired bootstrap vs best cheap baseline

For every probe-2 item that has arrays on disk (it reads runs/P2-PROBE-02/arrays/itemNNNN.npz and selection.json, writes nothing there):
  D at the stored codes of clean / swap / patch / jpeg / noise  (one null pass per caption length, cached on disk under runs/P2-GATE-DCACHE; at most 28 passes)
  with --tbv: the Trust-but-Verify-style observed-position log-probability for each of the 4 corrupted images (1 pass each; U7)
  once: the VQ codebook (best effort, runs/P2-GATE-M1/codebook.npy) for the neighbour-codebook-distance baseline.
q = B - D is then B (= s1 - r_original from probe 2, same masks, caption masked) minus D; the analysis assembles it."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common                                                  # noqa: E402
from exp_p2.gate import baselines, checks, config, pipeline, runner, scores   # noqa: E402

RUN_ID, PROBE_RUN = "P2-GATE-M1", "P2-PROBE-02"
NAMES = ("clean", "swap", "patch", "jpeg", "noise")
CONFIG = dict(stage="M1-posthoc", probe_run=PROBE_RUN, names=list(NAMES), duty=0.5,
              spec="research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md section 11.1 M1")


def probe_arrays_dir(runs: Path | None = None) -> Path:
    return (Path(runs) if runs is not None else Path(common.RUNS)) / PROBE_RUN / "arrays"


def get_items(sc, run, n=None, runs: Path | None = None):
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    sel = json.loads((runs / PROBE_RUN / "selection.json").read_text(encoding="utf8"))["items"]
    ad = probe_arrays_dir(runs)
    items = [dict(idx=i, image_id=it["image_id"], caption=it["caption"], n_tok=it["n_tok"]) for i, it in enumerate(sel) if (ad / f"item{i:04d}.npz").exists()]
    return items[:n] if n else items


def make_ctx_factory(tbv: bool, runs: Path | None = None):
    def make_ctx(sc, run):
        cb = run / "codebook.npy"
        if not (run / "codebook.json").exists():
            w = baselines.extract_codebook(sc.model.get_vae()) if hasattr(sc, "model") else None
            if w is not None:
                np.save(cb, w.astype(np.float32))
            (run / "codebook.json").write_text(json.dumps(dict(available=w is not None, shape=None if w is None else list(w.shape),
                                                               note=None if w is not None else "attribute path quantize.embedding.weight not found; neighbour-distance baseline will be NaN")), encoding="utf8")
        checks.l10_once(sc, run)
        return SimpleNamespace(run=run, dcache=pipeline.dcache_for(), tbv=tbv, arrays_dir=probe_arrays_dir(runs))
    return make_ctx


def process(sc, it, ctx):
    arr = np.load(ctx.arrays_dir / f"item{it['idx']:04d}.npz")
    cap_tok = sc.caption_ids(it["caption"])
    row, arrays = dict(image_id=it["image_id"], n_tok=len(cap_tok), tbv={}), {}
    for name in NAMES:
        codes = arr["clean"] if name == "clean" else arr[f"{name}_codes"]
        codes = np.asarray(codes, np.int64)
        st = sc.build(cap_tok, codes)
        arrays[f"{name}_D"] = ctx.dcache.image_logp(sc, st, len(cap_tok), codes)
        if ctx.tbv and name != "clean":
            tb = scores.observed_unmasked_logprob(sc, st)
            arrays[f"{name}_tbv"] = tb
            row["tbv"][name] = baselines.copy_through_stat(tb)
    return row, arrays


def main(argv=None):
    ap = runner.base_parser(RUN_ID)
    ap.add_argument("--tbv", action="store_true", help="also run the Trust-but-Verify-style pass on the 4 corrupted images per item")
    a = ap.parse_args(argv)
    n_avail = len(list(probe_arrays_dir().glob("item*.npz"))) if probe_arrays_dir().exists() else 0
    cfg = dict(CONFIG, n_items=a.n or n_avail, duty=a.duty, mem_frac=a.mem_frac, tbv=a.tbv)

    def load():
        from exp_p2.scoring import UniScorer
        return runner.Counting(UniScorer(common.load_net()))

    return runner.run_items(run_id=a.run_id, cfg=cfg, load=load, get_items=lambda sc, run: get_items(sc, run, a.n), process=process, make_ctx=make_ctx_factory(a.tbv),
                            soft_minutes=a.soft_minutes, duty=a.duty, limit=a.limit, guards=runner.guards_from_args(a), mem_frac=a.mem_frac, selfcheck=None, watchdog_factory=runner.default_watchdog)


if __name__ == "__main__":
    sys.exit(main())
