"""SAP addendum A7 (research/paper2/prereg/SAP-ADDENDUM-A7-F30K-2026-10-31.md): the frozen LRF on the Flickr30K test split, conditions clean and Gaussian noise sigma 0.1 only. CONFIRMATORY.

    python -m exp_p2.run_gate_lrf_f30k --run-id P2-LRF-F30K <the lrf-f30k flags> [--limit N] [--soft-minutes M]
    python -m exp_p2.gate.gate_driver --stage lrf-f30k --extra "<guard flags>"          # the production route (chunked, resumable, telemetry)

A thin entry point around the pinned L1 runner `exp_p2/run_gate_m4.py`, which it does NOT edit (pattern of `exp_p2/run_gate_lrf_sev.py`). The ONLY thing it changes, for the duration of the call and restored on exit
(also on error), is where images come from: `common.load_image` (used by `pipeline.prep_image` and by the runner's self-check) reads `<flickr30k>/test_images/<image_id>.jpg` instead of the COCO zip. The
bytes of every file are checked against the SHA-256 in `runs/P2-LRF-F30K-FOLD/manifest.json` (a mismatch stops the run). Nothing else is patched: build_conditions, process, the guards, the D-cache, the codebook
and the n check are those of L1. The family file `runs/P2-LRF-PLAN-F30K/family.json` holds the single cell noise0.1, so each item has exactly two conditions, `clean` and `noise0.1` (corruption call and stream
rung_rng(gid, "noise", 0) of L1, with the new gids 9000 + idx); `--sanity ""`, `--denoise-for ""` and no extra cells add none. The run config records the dataset, the image folder, the manifest hash and the licence note.
Required flags (checked before the model is touched): `--run-id P2-LRF-F30K --folds-path runs/P2-LRF-F30K-FOLD/folds_f30k.json --family-run P2-LRF-PLAN-F30K --sanity "" --denoise-for "" --tbv on --layout-fix 13 --neg-len`.
Score afterwards with `python -m exp_p2.gate.lrf_score --run-id P2-LRF-F30K --pins runs/P2-LRF-PINS/pins.json --conds clean,noise0.1`, then `python -m analysis.paper2.lrf.f30k_analysis`."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, run_gate_m4 as m4                                       # noqa: E402
from exp_p2.gate import build_f30k_fold as bf, runner                               # noqa: E402

RUN_ID = bf.EVAL_RUN_ID
FAMILY_RUN = bf.PLAN_RUN_ID
L_FIX = 13
FOLDS_REL = Path("runs") / bf.RUN_ID / "folds_f30k.json"
MANIFEST_REL = Path("runs") / bf.RUN_ID / "manifest.json"
CONDITIONS = ("clean", "noise0.1")


def manifest_hashes(manifest_path: Path | None = None) -> dict[str, str]:
    p = Path(manifest_path) if manifest_path else ROOT / MANIFEST_REL
    return json.loads(p.read_text(encoding="utf8"))["image_sha256"]


def make_loader(image_dir: Path, sha256_by_file: dict[str, str]):
    """common.load_image replacement: image_id -> RGB PIL from `image_dir/<id>.jpg`, after checking the SHA-256 of the bytes against the manifest."""
    image_dir = Path(image_dir)

    def load_image(image_id: int):
        from PIL import Image
        import io
        fn = f"{int(image_id)}.jpg"
        if fn not in sha256_by_file:
            raise KeyError(f"{fn} is not in the F30K manifest")
        data = (image_dir / fn).read_bytes()
        if hashlib.sha256(data).hexdigest() != sha256_by_file[fn]:
            raise ValueError(f"{fn}: SHA-256 differs from the manifest; stopping")
        return Image.open(io.BytesIO(data)).convert("RGB")
    return load_image


def f30k_record(image_dir: Path, manifest_path: Path) -> dict:
    return dict(dataset="Flickr30K test split (Karpathy), Hugging Face nlphuji/flickr30k", dataset_revision=bf.HF_REVISION, image_dir=str(image_dir), image_source="exp_p2.run_gate_lrf_f30k.make_loader (common.load_image swapped for the call)",
                image_manifest=str(manifest_path), image_manifest_sha256=bf.sha256_file(Path(manifest_path)), conditions=list(CONDITIONS), addendum=bf.SPEC,
                licence_note="images for non-commercial research and educational use under the Flickr Terms of Use; not redistributed; identifiers only in the repository",
                l1_runner="exp_p2/run_gate_m4.py (unchanged); score with exp_p2.gate.lrf_score --conds clean,noise0.1")


@contextlib.contextmanager
def f30k_patched(loader, record: dict | None = None):
    """Install the Flickr30K image loader on `common` and the config record on `runner.run_items` for the duration of the block; restore both on exit (also on error)."""
    saved = dict(load_image=common.load_image, run_items=runner.run_items)

    def run_items(**kw):
        return saved["run_items"](**dict(kw, cfg=dict(kw["cfg"], **(record or {}))))

    common.load_image = loader
    runner.run_items = run_items
    try:
        yield
    finally:
        common.load_image = saved["load_image"]
        runner.run_items = saved["run_items"]


def check_flags(rest: list[str]) -> list[str]:
    """Problems with the flags (empty = fine): the run id is the single whitelisted P2-LRF-F30K, and the L1 set with this addendum's fold and family."""
    ap = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--tbv", default=None)
    ap.add_argument("--sanity", default=None)
    ap.add_argument("--denoise-for", default=None)
    ap.add_argument("--folds-path", default=None)
    ap.add_argument("--family-run", default=None)
    ap.add_argument("--layout-fix", "--caption-slot-len", dest="slot", type=int, default=None)
    ap.add_argument("--neg-len", action="store_true")
    ap.add_argument("--extra-cells", default="")
    ap.add_argument("--gate-true-layout", action="store_true")
    a, _ = ap.parse_known_args(rest)
    bad = []
    if a.run_id != RUN_ID:
        bad.append(f"--run-id must be {RUN_ID!r} (whitelist; got {a.run_id!r})")
    for flag, val, want in (("--tbv", a.tbv, "on"), ("--sanity", a.sanity, ""), ("--denoise-for", a.denoise_for, ""), ("--layout-fix", a.slot, L_FIX), ("--family-run", a.family_run, FAMILY_RUN)):
        if val != want:
            bad.append(f"{flag} must be {want!r} (got {val!r})")
    if not a.neg_len:
        bad.append("--neg-len is required")
    if not a.folds_path or Path(a.folds_path).resolve() != (ROOT / FOLDS_REL).resolve():
        bad.append(f"--folds-path must be {FOLDS_REL.as_posix()} (got {a.folds_path!r})")
    if a.extra_cells or a.gate_true_layout:
        bad.append("--extra-cells and --gate-true-layout are not allowed")
    return bad


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    bad = check_flags(argv)
    if bad:
        print("STOP: " + "; ".join(bad), file=sys.stderr)
        return 2
    image_dir, manifest = bf.F30K_DIR / bf.IMAGE_SUBDIR, ROOT / MANIFEST_REL
    try:
        hashes = manifest_hashes(manifest)
        fold = json.loads((ROOT / FOLDS_REL).read_text(encoding="utf8"))
        missing = [it["image_id"] for it in fold["test"] if f"{it['image_id']}.jpg" not in hashes or not (image_dir / f"{it['image_id']}.jpg").exists()]
        if missing:
            raise FileNotFoundError(f"{len(missing)} fold images missing from the manifest or from {image_dir}, first: {missing[:5]}")
        record = f30k_record(image_dir, manifest)
    except (OSError, KeyError, ValueError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    with f30k_patched(make_loader(image_dir, hashes), record):
        return m4.main(argv)


if __name__ == "__main__":
    sys.exit(main())
