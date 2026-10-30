"""A6 r1 A6.6 industry baselines CLIP ViT-L/14 and SigLIP so400m: DESCRIPTIVE ONLY (no test, no comparison with LRF, own table). Standalone script; CPU by default; never run during a GPU stage.

    python -m analysis.paper2.lrf.baselines --folds-path runs/P2-LRF-FOLD/folds_lrf.json --family-run P2-LRF-PLAN --n 533 [--extra-cells shot_noise3,impulse_noise3,speckle_noise3 --extra-n 300]
           [--models clip,siglip] [--device cpu] [--parity-run P2-LRF-L1 --parity] [--download-approved] [--out-dir runs/P2-LRF-BASELINES]

Models (Hugging Face API 2026-10-29; sizes to be confirmed by the lead): `openai/clip-vit-large-patch14` at revision 32bd64288804d66eefd0ccbe215aa642df71cc41 and `google/siglip-so400m-patch14-384` at revision
9fdffc58afc957d1a03a25b10dba0329ab15c2a3 (Apache-2.0). Weights are NOT downloaded by default: `from_pretrained(..., local_files_only=True)`; without `--download-approved` a model that is not already cached stops the script
(exit 2). The flag is for the lead's download go-ahead only.

Items and pixels. The same items as the L fold (the first --n of `test` + `test_ext` of --folds-path) and the SAME corrupted pixels as the M4 stage: for each item, the 512 px centre-crop image (`suite.center_crop_512`, the code of
`UniScorer.preprocess`), then `corruptions.apply_pixel(corr, sev, pil, rung_rng(gid, corr, rung), donor)` for the corruptions of --family-run (splice donor: `run_gate_m3.donor_for` on the whole list), and `suite.apply_corruption`
with `suite.corruption_seed(gid, run_gate_m4.extra_cell_index(...))` for --extra-cells (the pinned imagecorruptions commit is checked by `suite.load_package`). Parity with `run_gate_m4.build_conditions` is tested.
Decision: Y = 1[s(image, c+) > s(image, c-)], ties wrong; c- is the item's primary negative `neg_caption`. s = the model's image-text similarity: CLIP, the cosine of the normalised embeddings; SigLIP, the pairwise logit
`logits_per_image` (monotone in the cosine, so the same decision).
Pixel-parity positive control (--parity, needs UniDisc's VQ, so GPU-heavy: run it alone, outside the GPU stages): 5 items x conditions are re-encoded and compared with the stored codes of --parity-run
(`<cond>_codes`); every image must agree on at least 0.98 of its tokens, else the baseline numbers are labelled "pixel parity not shown" and are not for the main text.
Output (--out-dir): `predictions.jsonl` (idx, gid, image_id, model, condition, s_pos, s_neg, y), `baselines.json`: per model and condition the accuracy and n, and for every non-clean condition the paired clean-to-corrupted drop with a 95 percent
percentile bootstrap CI (10,000 resamples, SeedSequence(20261028, spawn_key=(34, 13)), the BASELINES slot of a6_analysis). No p-value, no LRF or UniDisc number, no ranking."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

MODELS = {
    "clip": dict(id="openai/clip-vit-large-patch14", revision="32bd64288804d66eefd0ccbe215aa642df71cc41", licence="MIT (OpenAI CLIP release)"),
    "siglip": dict(id="google/siglip-so400m-patch14-384", revision="9fdffc58afc957d1a03a25b10dba0329ab15c2a3", licence="Apache-2.0"),
}                                                                            # ids and revisions as verified on the Hugging Face API 2026-10-29 (A6.6)
PARITY_MIN_AGREEMENT = 0.98                                                  # A6.6: VQ re-encode of the regenerated image vs the stored codes, on 5 items
PARITY_ITEMS = 5
SEED_ROOT, SEED_SPAWN_KEY = 20261028, (34, 13)                               # child 13 of the (34,) stream = the BASELINES slot of a6_analysis.SEED_SLOTS
RUN_ID = "P2-LRF-BASELINES"


class WeightsNotCached(RuntimeError):
    """The model is not in the local Hugging Face cache and the lead has not approved a download."""


# ------------------------------------------------------------------------------------------------ pure parts
def decide(s_pos, s_neg) -> np.ndarray:
    """Y = 1[s(image, c+) > s(image, c-)]; a tie is wrong."""
    return (np.asarray(s_pos, np.float64) > np.asarray(s_neg, np.float64)).astype(int)


def summarise(y_by_condition: dict[str, np.ndarray], rng: np.random.Generator, n_boot: int = 10000, clean: str = "clean") -> dict:
    """Accuracy per condition and the paired clean-to-corrupted drop (clean minus corrupted accuracy) with a 95 percent percentile bootstrap CI over items. Descriptive: no p-value. All arrays are aligned item by item."""
    out = {}
    yc = np.asarray(y_by_condition[clean], float)
    for cond, y in y_by_condition.items():
        y = np.asarray(y, float)
        row = dict(n=int(len(y)), acc=float(y.mean()))
        if cond != clean:
            d = yc - y
            idx = rng.integers(0, len(d), size=(n_boot, len(d)))
            lo, hi = np.quantile(d[idx].mean(axis=1), [0.025, 0.975])
            row.update(drop=float(d.mean()), drop_ci95=[float(lo), float(hi)])
        out[cond] = row
    return out


def pixel_parity_ok(agreement_per_image: list[float]) -> bool:
    """A6.6 positive control: every one of the checked images agrees with the stored codes on at least PARITY_MIN_AGREEMENT of the tokens."""
    return bool(len(agreement_per_image) > 0 and min(agreement_per_image) >= PARITY_MIN_AGREEMENT)


def baseline_rng() -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence(SEED_ROOT, spawn_key=SEED_SPAWN_KEY))


# ------------------------------------------------------------------------------------------------ the M4 pixels, regenerated
def family_from(runs: Path, family_run: str) -> list[tuple[str, object]]:
    p = Path(runs) / family_run / "family.json"
    fam = json.loads(p.read_text(encoding="utf8"))
    if fam.get("endpoint") != "d":
        raise ValueError(f"{p} does not record endpoint d")
    return [(f["corruption"], f["severity"]) for f in fam["family"]]


def condition_images(it: dict, fold_all: list[dict], family, extra_cells=(), ic=None, preprocess=None) -> dict:
    """name -> 512 px PIL image of every pixel condition of the M4 stage for this item: clean, each family corruption (run_gate_m4.build_conditions' own calls and seeds), then the extra imagecorruptions cells.
    `fold_all` is the whole ordered fold (the splice donor is another item of the same block of 300)."""
    from exp_p2 import common, run_gate_m4
    from exp_p2.gate import config, corruptions, suite
    from exp_p2.run_gate_m3 import donor_for, rung_rng
    pre = preprocess or suite.center_crop_512
    pil = pre(common.load_image(it["image_id"]))
    out = {"clean": pil}
    donor = None
    for corr, sev in family:
        r = list(config.LADDERS[corr]).index(sev)
        if corr == "splice" and donor is None:
            donor = donor_for(SimpleNamespace(fold=fold_all), SimpleNamespace(preprocess=pre), it)
        out[corruptions.corruption_key(corr, sev)] = corruptions.apply_pixel(corr, sev, pil, rung_rng(it["gid"], corr, r), donor if corr == "splice" else None)
    for key, ename, esev in extra_cells:
        out[key] = suite.apply_corruption(ename, esev, pil, suite.corruption_seed(it["gid"], run_gate_m4.extra_cell_index(ename, esev)), ic)
    return out


def score_items(items: list[dict], images_of, scorers: dict, extra_n: int | None = None, extra_keys=()) -> list[dict]:
    """Rows (idx, gid, image_id, model, condition, s_pos, s_neg, y) for every item, condition and scorer. `images_of(it)` -> {condition: image}; a scorer has `.pair(image, pos, neg) -> (s_pos, s_neg)`.
    The extra cells are only scored for the first `extra_n` items (the LG prefix of 300)."""
    rows = []
    for k, it in enumerate(items):
        for cond, img in images_of(it).items():
            if cond in extra_keys and extra_n is not None and k >= extra_n:
                continue
            for name, sc in scorers.items():
                sp, sn = sc.pair(img, it["caption"], it["neg_caption"])
                rows.append(dict(idx=it["idx"], gid=it["gid"], image_id=it["image_id"], model=name, condition=cond, s_pos=float(sp), s_neg=float(sn), y=int(sp > sn)))
    return rows


def table(rows: list[dict], rng: np.random.Generator | None = None, n_boot: int = 10000) -> dict:
    """The baselines' OWN table: per model, accuracy and n per condition (complete case over the items that have the clean score and the condition) and each non-clean condition's own clean-to-corrupted drop with CI."""
    rng = rng if rng is not None else baseline_rng()
    out = {}
    for model in sorted({r["model"] for r in rows}):
        by: dict[str, dict[int, int]] = {}
        for r in rows:
            if r["model"] == model:
                by.setdefault(r["condition"], {})[r["idx"]] = r["y"]
        clean = by.get("clean", {})
        res = {}
        for cond, d in by.items():
            if cond == "clean":
                res[cond] = dict(n=len(d), acc=float(np.mean(list(d.values()))))
                continue
            ids = sorted(i for i in d if i in clean)
            res[cond] = summarise({"clean": np.array([clean[i] for i in ids]), cond: np.array([d[i] for i in ids])}, rng, n_boot)[cond]
        out[model] = res
    return out


def parity_agreement(stored_codes: np.ndarray, reencoded: np.ndarray) -> float:
    return float((np.asarray(stored_codes) == np.asarray(reencoded)).mean())


# ------------------------------------------------------------------------------------------------ the models (lazy; nothing is downloaded without approval)
def force_offline() -> None:
    """No network call to the Hugging Face Hub in this process: the environment switches (read at import) and the constant of an already imported huggingface_hub."""
    import os
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    try:
        import huggingface_hub.constants as hc
        hc.HF_HUB_OFFLINE = True
    except ImportError:
        pass


class HFScorer:
    """Image-text similarity of a pinned Hugging Face model. `pair(image, pos, neg)` -> (s_pos, s_neg). CLIP: cosine of the normalised embeddings; SigLIP: `logits_per_image`."""

    def __init__(self, kind: str, device: str = "cpu", download_approved: bool = False):
        spec = MODELS[kind]
        self.kind, self.spec, self.device = kind, spec, device
        if not download_approved:
            force_offline()                                                  # `local_files_only` alone does not stop every Hub call in every transformers version (a test fetched two small config files): the Hub is switched off
        try:
            import torch
            from transformers import AutoModel, AutoProcessor
            kw = dict(revision=spec["revision"], local_files_only=not download_approved)
            self.processor = AutoProcessor.from_pretrained(spec["id"], **kw)
            self.model = AutoModel.from_pretrained(spec["id"], **kw).to(device).eval()
            self.torch = torch
        except (OSError, ValueError) as e:
            raise WeightsNotCached(f"{spec['id']}@{spec['revision']} is not in the local cache ({str(e)[:200]}); a download needs the lead's approval (--download-approved)") from e

    def pair(self, image, pos: str, neg: str):
        torch = self.torch
        kw = dict(padding="max_length", max_length=64) if self.kind == "siglip" else dict(padding=True, truncation=True, max_length=77)
        inp = self.processor(text=[pos, neg], images=image, return_tensors="pt", **kw).to(self.device)
        with torch.no_grad():
            out = self.model(**inp)
            if self.kind == "siglip":
                s = out.logits_per_image[0]
            else:
                s = (out.image_embeds / out.image_embeds.norm(dim=-1, keepdim=True) @ (out.text_embeds / out.text_embeds.norm(dim=-1, keepdim=True)).T)[0]
        return float(s[0]), float(s[1])


# ------------------------------------------------------------------------------------------------ CLI
def main(argv=None, scorer_factory=None, encoder=None) -> int:
    """`scorer_factory(kind, device, download_approved)` and `encoder` (PIL -> codes, for --parity) are injectable for the tests; production loads the models and UniDisc's VQ."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--folds-path", required=True)
    ap.add_argument("--family-run", default="P2-LRF-PLAN")
    ap.add_argument("--n", type=int, default=None, help="first n items of the fold (the n_L of the n-rule record)")
    ap.add_argument("--extra-cells", default="", help="e.g. shot_noise3,impulse_noise3,speckle_noise3 (the LG cells)")
    ap.add_argument("--extra-n", type=int, default=300, help="items scored for the extra cells (A6.5: the first 300)")
    ap.add_argument("--models", default="clip,siglip")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--download-approved", action="store_true", help="the lead approved the download of the pinned weights (A6.6); without it only cached weights are used")
    ap.add_argument("--parity", action="store_true", help="pixel-parity positive control with UniDisc's VQ (GPU-heavy; run alone)")
    ap.add_argument("--parity-run", default=None, help="run id whose arrays hold the stored <cond>_codes")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--n-boot", type=int, default=10000)
    a = ap.parse_args(argv)
    from exp_p2 import common, run_gate_m4
    from exp_p2.gate import suite
    runs = Path(common.RUNS)
    out_dir = Path(a.out_dir) if a.out_dir else runs / RUN_ID
    if (out_dir / "baselines.json").exists():
        print(f"STOP: {out_dir / 'baselines.json'} exists; not overwriting", file=sys.stderr)
        return 2
    try:
        family = family_from(runs, a.family_run)
        extra = run_gate_m4.parse_extra_cells(a.extra_cells)
        f = json.loads(Path(a.folds_path).read_text(encoding="utf8"))
        fold_all = f["test"] + f.get("test_ext", [])
        items = fold_all[:a.n] if a.n else fold_all
        ic = suite.load_package() if extra else None
        kinds = [k for k in a.models.split(",") if k]
        bad = [k for k in kinds if k not in MODELS]
        if bad or (a.parity and not a.parity_run):
            raise ValueError(f"unknown model(s) {bad}" if bad else "--parity needs --parity-run")
        factory = scorer_factory or (lambda k, d, ok: HFScorer(k, d, ok))
        scorers = {k: factory(k, a.device, a.download_approved) for k in kinds}
    except (FileNotFoundError, ValueError, ImportError, WeightsNotCached) as e:
        print("STOP:", e, file=sys.stderr)
        return 2

    def images_of(it):
        return condition_images(it, fold_all, family, extra, ic)
    keys = {k for k, _, _ in extra}
    rows = score_items(items, images_of, scorers, a.extra_n, keys)
    parity = None
    if a.parity:
        enc = encoder or _unidisc_encoder()
        agreements = {}
        for it in items[:PARITY_ITEMS]:
            arr = dict(np.load(runs / a.parity_run / "arrays" / f"item{it['idx']:04d}.npz"))
            for cond, img in images_of(it).items():
                if f"{cond}_codes" in arr:
                    agreements[f"{it['idx']}:{cond}"] = parity_agreement(arr[f"{cond}_codes"], enc(img))
        parity = dict(agreement=agreements, min=min(agreements.values()) if agreements else None, ok=pixel_parity_ok(list(agreements.values())), threshold=PARITY_MIN_AGREEMENT)
    res = dict(models={k: MODELS[k] for k in kinds}, table=table(rows, baseline_rng(), a.n_boot), n_items=len(items), conditions=sorted({r["condition"] for r in rows}), pixel_parity=parity or "not run: baselines are labelled \"pixel parity not shown\"",
               note="descriptive only: different models trained on different data; no test, no comparison with LRF; own table (A6.6)")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "predictions.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf8")
    (out_dir / "baselines.json").write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf8")
    print(json.dumps(dict(out=str(out_dir), n_rows=len(rows), parity_ok=(parity or {}).get("ok"))))
    return 0


def _unidisc_encoder():
    from exp_p2 import common
    from exp_p2.scoring import UniScorer
    sc = UniScorer(common.load_net())
    return sc.encode


if __name__ == "__main__":
    sys.exit(main())
