"""CPU check that the pixel-domain denoise arm actually denoises at the preregistered noise level (red team N6 / condition C5). Classical denoiser, no model, no weights, no GATE flag.

    python -m exp_p2.gate.denoise_check [--n 20]          # writes the run directory runs/P2-GATE-CPU/denoise_check/

~20 COCO images (the first 20 of probe 1's selection; those ids are excluded from every new fold) are preprocessed exactly as the model sees them (centre crop, 512 px), corrupted with
the SAME code as the experiment (Gaussian noise sigma = 0.10 on [0,1], and JPEG q10), then denoised by (a) OpenCV `fastNlMeansDenoisingColored` with LIBRARY DEFAULTS (h = hColor = 3),
(b) the setting fixed for the experiment (config.DENOISE_PARAMS) and (c) h = 10, the value used in OpenCV's own tutorial, reported for transparency and NOT chosen. PSNR and SSIM of
noisy-vs-clean and denoised-vs-clean are written per image and summarised with paired bootstrap CIs.

Why the setting is not the library default: the default h = 3 is small against noise of sigma = 0.10 x 255 = 25.5 grey levels (measured below: it removes a fraction of a percent of the noise power).
The replacement is NOT tuned on our data: it is the rule of thumb documented in scikit-image's `denoise_nl_means` docstring, "for a Gaussian noise of standard deviation sigma, a rule of thumb is to choose
the value of h to be sigma of slightly less", with sigma = 25.5, so h = hColor = 25.5; the patch and search window sizes stay at the OpenCV defaults 7 and 21. Disclosure: the library-default gain, h = 10 and
h = 25.5 were all evaluated once on these 20 images in an exploratory run before the setting was written down; there was no grid and no later adjustment."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from exp_p2 import common, core                                            # noqa: E402
from exp_p2.gate import config, corruptions, data, detect, imgmetrics, seeds   # noqa: E402

RUN_ID = "P2-GATE-CPU/denoise_check"
NOISE_SIGMA, JPEG_Q = 0.10, 10


def _nlm(pil, h: float, hcolor: float, tw: int = 7, sw: int = 21) -> np.ndarray:
    a = cv2.cvtColor(np.asarray(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(cv2.fastNlMeansDenoisingColored(a, None, h, hcolor, tw, sw), cv2.COLOR_BGR2RGB)


def library_default(pil) -> np.ndarray:
    """OpenCV library defaults (h = hColor = 3, windows 7 and 21): parameters are deliberately not passed."""
    a = cv2.cvtColor(np.asarray(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    return cv2.cvtColor(cv2.fastNlMeansDenoisingColored(a), cv2.COLOR_BGR2RGB)


def chosen(pil) -> np.ndarray:
    return np.asarray(corruptions.denoise(pil))


def measure(clean: np.ndarray, noisy_pil, arms: dict) -> dict:
    n = np.asarray(noisy_pil)
    out = dict(noisy=dict(psnr=imgmetrics.psnr(clean, n), ssim=imgmetrics.ssim(clean, n)))
    for name, fn in arms.items():
        d = fn(noisy_pil)
        out[name] = dict(psnr=imgmetrics.psnr(clean, d), ssim=imgmetrics.ssim(clean, d))
    return out


def summarise(items: list[dict], cond: str, n_boot: int = 10000) -> dict:
    out = {}
    for arm in ("noisy", "library_default", "chosen", "tutorial_h10"):
        out[arm] = {m: float(np.mean([r[cond][arm][m] for r in items])) for m in ("psnr", "ssim")}
    for arm in ("library_default", "chosen", "tutorial_h10"):
        for m in ("psnr", "ssim"):
            d = np.array([r[cond][arm][m] - r[cond]["noisy"][m] for r in items])
            mean, lo, hi = core.bootstrap_mean_ci(d, n_boot, seeds.seed_for("denoise_check"))
            out[f"gain_{arm}_{m}"] = dict(mean=mean, ci95=[lo, hi])
    noise_power_removed = lambda g: float(1 - 10 ** (-g / 10))
    out["share_of_noise_power_removed"] = {a: noise_power_removed(out[f"gain_{a}_psnr"]["mean"]) for a in ("library_default", "chosen", "tutorial_h10")}
    return out


def run(n: int = 20, runs_dir: Path | None = None, force: bool = False) -> dict:
    ids = [it["image_id"] for it in json.loads((Path(common.RUNS) / "P2-PROBE-01" / "selection.json").read_text(encoding="utf8"))["items"][:n]]
    cfg = dict(purpose="check that the denoise arm denoises at the preregistered noise level (red team N6 / C5)", image_ids=ids, n=len(ids), noise_sigma=NOISE_SIGMA, jpeg_quality=JPEG_Q,
               image_source="first %d items of runs/P2-PROBE-01/selection.json (excluded from all new folds); COCO val2017 from common.load_image" % len(ids),
               preprocessing="detect.preprocess512 (centre crop, bicubic 512), as UniScorer.preprocess", corruption_code="exp_p2.gate.corruptions.gaussian_noise / jpeg (identical to the experiment)",
               rng="default_rng([20261028, 77, i]) per image for the noise draw", opencv=cv2.__version__, chosen_params=config.DENOISE_PARAMS,
               library_defaults=dict(h=3, hColor=3, templateWindowSize=7, searchWindowSize=21), tutorial_alternative=dict(h=10, hColor=10, note="OpenCV tutorial value, reported, not chosen"),
               rationale=__doc__)
    d = common.init_run(RUN_ID, cfg) if runs_dir is None else Path(runs_dir)
    d.mkdir(parents=True, exist_ok=True)
    if (d / "summary.json").exists() and not force:
        raise FileExistsError(f"{d / 'summary.json'} exists; the check is recorded once (use --force to amend)")
    if runs_dir is not None:
        (d / "config.json").write_text(json.dumps(cfg, indent=1, default=str), encoding="utf8")
    arms = dict(library_default=library_default, chosen=lambda p: chosen(p), tutorial_h10=lambda p: _nlm(p, 10, 10))
    items = []
    for i, iid in enumerate(ids):
        pil = detect.preprocess512(common.load_image(iid))
        clean = np.asarray(pil)
        noisy = corruptions.gaussian_noise(pil, NOISE_SIGMA, np.random.default_rng([20261028, 77, i]))
        jpg = corruptions.jpeg(pil, JPEG_Q)
        items.append(dict(idx=i, image_id=iid, noise=measure(clean, noisy, arms), jpeg=measure(clean, jpg, arms)))
    with open(d / "items.jsonl", "w", encoding="utf8") as fh:
        for r in items:
            fh.write(json.dumps(r) + "\n")
    noise, jq = summarise(items, "noise"), summarise(items, "jpeg")
    findings = dict(
        noise_library_default_gain_db=noise["gain_library_default_psnr"]["mean"], noise_chosen_gain_db=noise["gain_chosen_psnr"]["mean"],
        library_default_acts_on_noise=bool(noise["share_of_noise_power_removed"]["library_default"] > 0.05), chosen_acts_on_noise=bool(noise["share_of_noise_power_removed"]["chosen"] > 0.5),
        jpeg_chosen_gain_db=jq["gain_chosen_psnr"]["mean"], jpeg_library_default_gain_db=jq["gain_library_default_psnr"]["mean"],
        chosen_hurts_jpeg_psnr=bool(jq["gain_chosen_psnr"]["mean"] < 0),
        note=("ONE setting is used for all corruptions (spec v2 4.3). It is matched to the preregistered Gaussian noise; on JPEG q10 (no sigma exists to match) the same setting changes PSNR by the "
              "value above (negative = it over-smooths), so the JPEG denoise comparison (S-DN, JPEG) is against an aggressive denoiser. Reported, not tuned away."))
    summ = dict(n_images=len(items), noise_sigma=NOISE_SIGMA, noise_sigma_grey_levels=NOISE_SIGMA * 255, noise=noise, jpeg_q10=jq, findings=findings,
                chosen_params=config.DENOISE_PARAMS, opencv=cv2.__version__)
    (d / "summary.json").write_text(json.dumps(summ, indent=1), encoding="utf8")
    return summ


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    try:
        s = run(a.n, force=a.force)
    except FileExistsError as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    for cond in ("noise", "jpeg_q10"):
        t = s[cond]
        print(cond, {k: (round(v["psnr"], 2), round(v["ssim"], 3)) for k, v in t.items() if k in ("noisy", "library_default", "chosen", "tutorial_h10")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
