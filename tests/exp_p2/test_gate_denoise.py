"""Denoise arm (red team N6 / C5): the fixed setting actually denoises at the preregistered noise level, the library default does not; PSNR/SSIM helpers; the check's run directory. CPU only."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT, Path(__file__).resolve().parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from fake_gate import fake_image                                              # noqa: E402
from exp_p2 import common                                                     # noqa: E402
from exp_p2.gate import config, corruptions, denoise_check, imgmetrics         # noqa: E402


def _smooth(size=256, seed=0):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:size, 0:size] / size
    img = np.stack([120 + 80 * np.sin(3 * x + c) * np.cos(2 * y) for c in (0.0, 1.0, 2.0)], -1) + rng.normal(0, 2, (size, size, 3))
    from PIL import Image
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def test_the_fixed_setting_is_the_documented_rule_sigma_in_grey_levels():
    p = config.DENOISE_PARAMS
    assert config.DENOISE_NOISE_SIGMA == 0.10 and p["h"] == p["hColor"] == pytest.approx(25.5) and (p["templateWindowSize"], p["searchWindowSize"]) == (7, 21)


def test_fixed_setting_denoises_gaussian_noise_and_the_library_default_barely_does():
    clean = _smooth()
    noisy = corruptions.gaussian_noise(clean, 0.10, np.random.default_rng(1))
    c, n = np.asarray(clean), np.asarray(noisy)
    d_fixed = np.asarray(corruptions.denoise(noisy))
    d_lib = denoise_check.library_default(noisy)
    p_noisy, p_fixed, p_lib = imgmetrics.psnr(c, n), imgmetrics.psnr(c, d_fixed), imgmetrics.psnr(c, d_lib)
    assert p_fixed - p_noisy > 3.0                                                # the fixed setting removes most of the noise power
    assert p_lib - p_noisy < 0.5                                                  # the library default (h = 3) removes a fraction of a percent: the red team's concern
    assert imgmetrics.ssim(c, d_fixed) > imgmetrics.ssim(c, n) + 0.1
    assert np.array_equal(d_fixed, np.asarray(corruptions.denoise(noisy, config.DENOISE_PARAMS)))
    assert not np.array_equal(d_fixed, d_lib)


def test_psnr_and_ssim_basics_and_agreement_with_scikit_image():
    rng = np.random.default_rng(0)
    a = rng.integers(0, 256, (80, 90, 3)).astype(np.uint8)
    b = np.clip(a + rng.normal(0, 20, a.shape), 0, 255).astype(np.uint8)
    assert imgmetrics.psnr(a, a) == float("inf") and imgmetrics.ssim(a, a) == pytest.approx(1.0)
    assert imgmetrics.psnr(a, np.clip(a.astype(int) + 10, 0, 255).astype(np.uint8)) > imgmetrics.psnr(a, b) and imgmetrics.ssim(a, b) < 1
    assert imgmetrics.psnr(np.zeros((4, 4), np.uint8), np.full((4, 4), 255, np.uint8)) == pytest.approx(0.0)
    sk = pytest.importorskip("skimage.metrics")
    assert imgmetrics.ssim(a, b) == pytest.approx(sk.structural_similarity(a, b, gaussian_weights=True, sigma=1.5, use_sample_covariance=False, data_range=255, channel_axis=2), abs=1e-6)
    assert imgmetrics.psnr(a, b) == pytest.approx(sk.peak_signal_noise_ratio(a, b, data_range=255), abs=1e-9)


def test_denoise_check_writes_a_run_directory_with_config_and_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    monkeypatch.setattr(common, "load_image", lambda iid: fake_image(iid, 128))
    (tmp_path / "P2-PROBE-01").mkdir()
    (tmp_path / "P2-PROBE-01" / "selection.json").write_text(json.dumps(dict(items=[dict(image_id=i) for i in range(100, 105)])))
    out = tmp_path / "dc"
    s = denoise_check.run(3, runs_dir=out)
    assert {"config.json", "items.jsonl", "summary.json"} <= {f.name for f in out.iterdir()}
    cfg = json.loads((out / "config.json").read_text())
    assert cfg["image_ids"] == [100, 101, 102] and cfg["noise_sigma"] == 0.10 and cfg["chosen_params"]["h"] == 25.5 and "rule of thumb" in cfg["rationale"]
    items = [json.loads(l) for l in (out / "items.jsonl").read_text().splitlines()]
    assert len(items) == 3 and set(items[0]["noise"]) == {"noisy", "library_default", "chosen", "tutorial_h10"} and set(items[0]["noise"]["chosen"]) == {"psnr", "ssim"}
    assert s["findings"]["chosen_acts_on_noise"] and not s["findings"]["library_default_acts_on_noise"] and s["noise"]["gain_chosen_psnr"]["mean"] > 3
    assert s["noise"]["share_of_noise_power_removed"]["library_default"] < 0.05 < 0.5 < s["noise"]["share_of_noise_power_removed"]["chosen"]
    assert items[0]["noise"]["noisy"]["psnr"] < items[0]["noise"]["chosen"]["psnr"]
    with pytest.raises(FileExistsError):
        denoise_check.run(3, runs_dir=out)                                          # recorded once
    assert denoise_check.run(3, runs_dir=out, force=True)["n_images"] == 3


def test_the_committed_check_run_shows_the_default_does_not_act_and_the_fixed_setting_does():
    d = ROOT / "runs" / "P2-GATE-CPU" / "denoise_check"
    if not (d / "summary.json").exists():
        pytest.skip("run directory not present")
    s = json.loads((d / "summary.json").read_text())
    assert s["n_images"] == 20 and s["noise"]["gain_chosen_psnr"]["ci95"][0] > 3 and s["findings"]["library_default_acts_on_noise"] is False
    assert json.loads((d / "config.json").read_text())["chosen_params"]["h"] == 25.5 and (d / "items.jsonl").exists()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
