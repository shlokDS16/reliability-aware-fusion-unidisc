```yaml
agent: data-steward
date: 2026-10-28
brief: Verify FOIL-COCO, imagecorruptions and up to two other COCO image-corruption/caption benchmarks for GATE (primary sources only; no download >50 MB; nothing installed; no GPU; runs/P2-PROBE-02 untouched)
sources_examined:
  - https://foilunitn.github.io/ (raw HTML, retrieved 2026-10-28)
  - https://foilunitn.github.io/content/annotation.txt (retrieved 2026-10-28)
  - foilv1.0_test_2017.json (full, 45,080,997 B) and the first 30,000,000 B of foilv1.0_train_2017.json (Dropbox links on the project page)
  - https://aclanthology.org/P17-1024.pdf (Shekhar et al., ACL 2017; converted with markitdown, Table 1 and Section 3 read)
  - PyPI JSON for imagecorruptions, scikit-image, numba, scipy, opencv-python; wheel imagecorruptions-1.1.2-py3-none-any.whl (2.09 MB, inspected, not installed)
  - GitHub bethgelab/imagecorruptions master c959e659c9 (2025-05-06): LICENSE, README, setup.py, requirements.txt, __init__.py, corruptions.py, issues #28 and #30
  - GitHub Jielin-Qiu/MM_Robustness (Apache-2.0) README, image_perturbation/, requirements.txt; mmrobustness.github.io
  - GitHub sail-sg/MMCBench README; Hugging Face dataset javyduck/MMCBench (API metadata, card, file sizes)
  - W\runs\P2-GATE-FOLDS\folds.json (read only)
coverage: FOIL test split read in full; FOIL train split read only up to the end of the "images" array (65,697 images, ends at byte 17,954,530 of 86,553,565); train annotations not read. imagecorruptions not installed or run. MMRobustness and MMCBench read at README/metadata level only (E1), papers not read.
claims:
  - statement: FOIL-COCO dataset licence is CC BY 4.0; underlying COCO images are under Flickr terms of use, COCO annotations CC BY 4.0
    status: supported
    evidence: foilunitn.github.io, "License" section (raw HTML)
    level: E1
    confidence: 0.95
  - statement: FOIL test image ids are all COCO val2014 ids and FOIL train ids are all train2014 ids; our fold image ids are disjoint from FOIL train
    status: supported
    evidence: file_name prefixes COCO_val2014 (32,150 of 32,150, test) and COCO_train2014 (65,697 of 65,697, train); overlap computed against folds.json
    level: E4
    confidence: 0.95
  - statement: imagecorruptions 1.1.2 from PyPI works with current scikit-image
    status: contradicted
    evidence: PyPI wheel corruptions.py lines 188, 198, 210 call gaussian(..., multichannel=True); open issue #30 reports the TypeError
    level: E3
    confidence: 0.9
  - statement: imagecorruptions runs on Python 3.12 on Windows
    status: unknown
    evidence: not installed or executed (brief forbids install); static risks listed below
    level: E1
    confidence: 0.3
competing_explanations: []
unknowns: [which FOIL file revision Dropbox serves today (page says Oct 2018 is current; the JSON info block says "1st version, July 2017" and cannot distinguish), FOIL train annotation count read from file, imagecorruptions behaviour on py3.12/Windows, source image dataset and licence of MMCBench image2text, severity grid of MMRobustness]
next_test: {hypothesis: n/a (data check), intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Data check: FOIL-COCO, imagecorruptions, alternatives (2026-10-28)

Legend: VERIFIED = read in the primary source or recomputed from a file I fetched (source given). UNVERIFIED = not checked or taken from a secondary summary. INFERENCE and HYPOTHESIS are labelled. Local copies are in the session scratchpad (not in the repo): `...\scratchpad\foil\foilv1.0_test_2017.json`, `...\scratchpad\ic\`, `...\scratchpad\cand\`.

## 1. FOIL-COCO (Shekhar et al., ACL 2017, "FOIL it! Find One mismatch between Image and Language caption")

| Fact | Status | Source |
|---|---|---|
| Paper: ACL 2017 long paper, 7 authors, pages 255-265, DOI 10.18653/v1/P17-1024 | VERIFIED | project page citation block; arXiv 1705.01359 abstract page ("To appear at ACL 2017") |
| Dataset licence: CC BY 4.0, held by University of Trento. Images: Flickr terms of use. COCO annotations: CC BY 4.0. Page states "authors of MS-COCO do not in any form endorse this work" | VERIFIED | foilunitn.github.io, section "License" (raw HTML) |
| Official download: Dropbox `https://www.dropbox.com/s/bsmowpgz43pwkyd/foilv1.0_train_2017.json` (train), `https://www.dropbox.com/s/u4ntgo73szg6yai/foilv1.0_test_2017.json` (test). No validation split on the page | VERIFIED | project page links |
| File sizes (HTTP Content-Length, `?dl=1`, 2026-10-28): train 86,553,565 B (86.6 MB, NOT fully downloaded); test 45,080,997 B (45.1 MB, downloaded) | VERIFIED | curl response headers |
| Test file SHA-256 | VERIFIED (recorded, not yet in a manifest) | `7b37ab2a4e3dc911d006d5941919245c47d1e67d2ee29b4f7a87d5ecc9284642` |
| Page warns that copies downloaded before Sep 2018 had a language bias (Madhyastha et al. 2018) and tells users to use the Oct 2018 version | VERIFIED (page text) | project page. Whether the current Dropbox file is the Oct 2018 version is UNVERIFIED: the JSON `info` block reads "1st version of the FOIL dataset", "July, 2017" |
| Splits and sizes: train 197,788 pairs / 65,697 images / 395,576 captions / 256 target-foil pairs; test 99,480 pairs / 32,150 images / 198,960 captions / 216 pairs (73 target, 71 foil words in test) | VERIFIED for test (counted from the file: 32,150 images, 198,960 annotations, 99,480 foil + 99,480 original, 215 distinct target-foil pairs and 72 target words by my count against 216 and 73 in the paper, a small discrepancy of 1 each); train images count 65,697 VERIFIED from the file, other train totals taken from paper Table 1 only | paper Table 1 (markitdown of the ACL PDF); file counts |
| Foil construction: one noun in the original COCO caption is replaced by a visually similar word from the same COCO supercategory; "hardest" foil chosen with a captioning model (NeuralTalk) | VERIFIED (paper Section 3) | ACL PDF |
| Fields per annotation (MS-COCO caption format plus extras): `id`, `foil_id`, `image_id`, `caption`, `target_word`, `foil_word`, `foil` (bool). In the test set `target_word`/`foil_word` = "ORIG" for original captions; in train they are empty strings. Image records: `id`, `width`, `height`, `file_name`, `license`, `flickr_url`, `coco_url`, `date_captured` | VERIFIED | annotation.txt and the JSON itself (all 198,960 test annotations carry exactly these 7 keys) |
| Pairing: there is no explicit pair key. `foil_id` is unique per caption (198,960 groups of size 1). An original and a foil are linked only by sharing `image_id` and the caption text. Per image, foil count equals original count (1 to 6 each) | VERIFIED (computed) | test JSON |
| Image id space: test file names are all `COCO_val2014_*` (32,150 of 32,150); train file names are all `COCO_train2014_*` (65,697 of 65,697). Train and test image ids are disjoint | VERIFIED | JSON `images[].file_name` |
| Mapping to val2017: COCO image ids are unchanged between 2014 and 2017, and val2017 (5,000 images) is a subset of val2014 | INFERENCE, supported by data: of the 900 distinct image ids in folds.json, 712 (79.1%) are in the FOIL test image list, 0 are in the FOIL train list, 188 are in neither. 79.1% matches 32,150/40,504 = 79.4% expected if val2017 is a subset of val2014 and FOIL test covers a random-looking 79% of it. I did not fetch the COCO documentation to confirm the subset statement | computed against W\runs\P2-GATE-FOLDS\folds.json |

### Overlap with W\runs\P2-GATE-FOLDS\folds.json (by image id, from metadata only; 45 MB test file + 30 MB header range of train, both under 50 MB)

| Fold | rows | images in FOIL test | images in FOIL train | fold caption equals a FOIL original caption (case/punctuation-normalised) | FOIL foil captions available on those images |
|---|---|---|---|---|---|
| cal | 300 | 240 | 0 | 152 | 723 |
| head | 100 | 75 | 0 | 42 | 204 |
| test | 300 | 238 | 0 | 147 | 747 |
| test_ext | 200 | 159 | 0 | 96 | 502 |
| all (distinct ids) | 900 | 712 | 0 | | |

The `neg_image_id` values in folds.json are a subset of the `image_id` values in each fold, so they add no new ids. The caption-equality column is lower than the image column because folds.json captions come from one COCO reference per image and FOIL keeps only some of the five.

### Fit for GATE (inference, not result)
- FOIL is a text-side benchmark: one noun in the caption is wrong, the image is clean. It has no image-side corruption. It can serve only as a paired mismatch control (original versus foil caption on the same clean image), not as the corruption set.
- Artefact found in the test file: 0.0% of the 99,480 foil captions start with a capital letter, against 85.1% of the original captions; both end with a full stop 75.7% of the time. A model or probe can separate foil from original on casing alone. Any use needs lowercasing of both sides. This is a different surface cue from the language bias that the Oct 2018 revision claims to fix, and I did not check whether it is documented.
- Image licences: the `licenses` array lists the usual nine Flickr licences (includes NonCommercial and NoDerivs ones). Relevant if corrupted copies of images are ever redistributed. UNVERIFIED which licence ids our 900 images carry.
- Only 79% of our images are covered, so FOIL would need its own fold built from its 32,150-image test list rather than a reuse of folds.json.

## 2. imagecorruptions (Michaelis et al. 2019)

| Fact | Status | Source |
|---|---|---|
| Licence: Apache-2.0 (full text in LICENSE, 11,558 B; PyPI classifier "Apache Software License"; PyPI `license` field empty, METADATA says "License: UNKNOWN") | VERIFIED | GitHub LICENSE; PyPI JSON; wheel METADATA |
| Citation: Michaelis, Mitzkus, Geirhos, Rusak, Bringmann, Ecker, Bethge, Brendel, arXiv:1907.07484 (README bibtex), "Benchmarking Robustness in Object Detection: Autonomous Driving when Winter is Coming". Lineage: ImageNet-C of Hendrycks and Dietterich (arXiv 1807.01697) | VERIFIED against the README bibtex (arXiv page itself not opened); README cites 1807.01697 as the origin of the corruptions | README |
| Latest PyPI version 1.1.2, uploaded 2020-12-03. Wheel `py3-none-any` 2,094,054 B, sha256 `d0e4bf529ba6fbb27d8aba1bde7c5db43bf2b969b2c767c11419e939e3e365b8`; sdist 2,092,862 B, sha256 `044e173f24d5934899bdbf3596bfbec917e8083e507eed583ab217abebbe084d`. Earlier: 0.1.0, 0.1.1, 1.0.0, 1.1.0, 1.1.1 | VERIFIED | PyPI JSON |
| PyPI declares no `requires_python`. requires_dist: Pillow>=5.4.1, numpy>=1.16, opencv-python>=3.4.5, scikit-image>=0.15, scipy>=1.2.1 | VERIFIED | PyPI JSON; wheel METADATA |
| GitHub master (c959e659c9, 2025-05-06, no tag/PyPI release since 1.1.2) differs from PyPI: setup.py still says version 1.1.2 but adds numba>=0.53.0 (requirements.txt also tqdm, matplotlib>=3.6, filetype); corruptions.py replaces `multichannel=True` with `channel_axis=-1` and imports `numba.njit` | VERIFIED | raw files from master vs wheel contents |
| 19 corruptions: common 15 = gaussian_noise, shot_noise, impulse_noise, defocus_blur, glass_blur, motion_blur, zoom_blur, snow, frost, fog, brightness, contrast, elastic_transform, pixelate, jpeg_compression; validation 4 = speckle_noise, gaussian_blur, spatter, saturate | VERIFIED | `__init__.py` `corruption_tuple`, `get_corruption_names` |
| Severities: integer 1 to 5 (code raises AttributeError otherwise). README usage line shows `-se` choices {1,2,3,4}, which contradicts its own "1-5" text (README inconsistency, not a code limit) | VERIFIED | `__init__.py`; README |
| API: `corrupt(image, severity, corruption_name=... or corruption_number=...)`; input must be uint8 numpy array, H and W at least 32, 1 or 3 channels; returns uint8 same shape; arbitrary image sizes are allowed (no 224 crop) | VERIFIED | `__init__.py` docstring and checks |
| Randomness: corruptions call the global `np.random` (e.g. normal, poisson, uniform) and `corrupt` has no seed argument, so determinism needs `np.random.seed` set per image before each call; open PR #27 title mentions "corruption determinism" | VERIFIED (grep of wheel corruptions.py); not every corruption's RNG use was audited | `__init__.py`; PR title #27 |
| Python 3.12 / Windows: PyPI 1.1.2 breaks with scikit-image >= 0.21 (`gaussian(..., multichannel=True)` in `gaussian_blur` and twice in `glass_blur`, wheel lines 188, 198, 210, raises TypeError; open issue #30, 2025-05-08, reports this for `gaussian_blur`). It also imports `pkg_resources` (absent from fresh Python 3.12 venvs without setuptools; issue/PR #28 describes this and is closed, but master c959e659c9 still contains `from pkg_resources import resource_filename`). Both PyPI and master import `scipy.ndimage.interpolation.map_coordinates`, a deprecated namespace; whether it still exists in the scipy version we would use was NOT checked | The failure with PyPI 1.1.2 is VERIFIED statically (E3); the claim that master runs on 3.12/Windows is UNVERIFIED (not installed or executed, as instructed) | wheel/master source; issues #28, #30 |
| Dependency wheels for cp312 win_amd64 exist: scikit-image (0.22.0 onwards), numba 0.68.1, scipy 1.18.1, opencv-python (abi3 win_amd64 wheel); the repo's pinned-old numpy limits (none declared) do not block | VERIFIED (file names in PyPI JSON) | PyPI JSON |
| Frost textures ship inside the wheel (6 files, about 1.9 MB); the frost images' own licence not checked | VERIFIED presence; licence UNVERIFIED | wheel file list |

Recommendation for GATE (inference): do not `pip install imagecorruptions` blindly. Either (a) install the git commit c959e659c9 plus setuptools, run the 19 functions on a 5-image smoke set on CPU, and pin the commit in the manifest, or (b) vendor `corruptions.py` from that commit (Apache-2.0 allows it with the notice) and replace `pkg_resources` and `scipy.ndimage.interpolation`. Both are one-hour jobs but need the orchestrator's go-ahead to install.

## 3. Alternatives (at most two)

### 3a. MMRobustness (Qiu et al., "Benchmarking Robustness of Multimodal Image-Text Models under Distribution Shift", DMLR 2024; arXiv 2212.08044)
- Repository `Jielin-Qiu/MM_Robustness`: Apache-2.0 (LICENSE and GitHub metadata), last push 2024-01-25. VERIFIED.
- Content: code that builds COCO-IP/COCO-TP (also Flickr30K, NLVR2, SNLI-VE) from the original datasets: 17 image perturbations (noise 4, blur 4, weather 4, digital 4, stylize 1) and 16 text perturbations. VERIFIED (project page, repo tree).
- No perturbed images are released ("Due to the size of the perturbed data, we didn't provide the perturbed images", image_perturbation/README.md); only generated text-to-image images are shared via Google Drive. VERIFIED.
- Image corruptions are a copy of the ImageNet-C code (`imagenet_c/` folder with the same frost files), so it adds nothing new over imagecorruptions for image-side shifts. `perturb_COCO_IP.py` uses `wand` (ImageMagick) and `np.float_`; `requirements.txt` pins numpy 1.17.1, tensorflow 1.14, torch 1.7.1, scikit-image 0.17.2, scipy 1.4.1. Will not run on Python 3.12 without edits. VERIFIED (files). Severity grid and COCO split used: UNVERIFIED (script and paper not read past the header).
- Verdict: not a better fit than imagecorruptions; useful only as prior art and as a citation for "image corruptions on COCO with captions".

### 3b. MMCBench ("Benchmarking Large Multimodal Models against Common Corruptions", arXiv 2401.11943)
- Repository `sail-sg/MMCBench`: Apache-2.0, last push 2024-01-23. Dataset `javyduck/MMCBench` on Hugging Face: card states Apache 2.0, last modified 2024-01-23, total storage about 60.7 GB. VERIFIED (README, HF API).
- `image2text/` has four parquet files (light/heavy corruption, hard/random 1k selection) of 5.62, 6.04, 5.84 and 6.31 GB (VERIFIED by HF tree API). These are above the 5 GB threshold; NOT downloaded, orchestrator approval needed for any of them.
- Task design: self-consistency between model outputs on clean versus corrupted inputs, 1k selected examples per setting, across text, image and speech. The source image dataset and licence of the images in `image2text` are UNVERIFIED (not stated in README or card).
- Verdict: weaker fit. It tests consistency of generated captions, not text-image link of a unified discrete-diffusion model, uses 1k examples, and the images are not COCO val2017 ids as far as I could verify. Treat as related work.

### Conclusion for the orchestrator
No published benchmark found that fits GATE better than generating image-side corruptions with imagecorruptions on our own COCO val2017 folds. FOIL-COCO is a usable text-side control (CC BY 4.0, 45 MB test file, 79% image overlap with our folds, but with a casing artefact).

## Not done (by design or by limit)
- Nothing installed, no corruption function executed, no GPU, no download above 50 MB, runs/P2-PROBE-02 not opened.
- FOIL train annotations not read (train file only range-read to the end of the images array).
- No ledger rows added (brief did not request any).
- COCO documentation not fetched to confirm the val2017-subset-of-val2014 statement; the claim stands as inference with the overlap numbers above.
