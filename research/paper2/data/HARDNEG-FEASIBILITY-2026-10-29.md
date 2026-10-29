```yaml
agent: data-steward
date: 2026-10-29
brief: Feasibility (no GPU, no experiment) of a hard-negative family built on SugarCrepe for Paper 2 GATE on UniDisc 1.4B
sources_examined:
  - https://github.com/RAIVNLab/sugar-crepe (commit 0047054b243992f0fad63d6f64f7544862daf846, 2024-02-13; README, LICENSE, data/*.json)
  - arXiv:2306.14610 (Hsieh et al., SugarCrepe; PDF converted with markitdown, Sec. 4, App. B.2, App. D)
  - https://github.com/mertyg/vision-language-models-are-bows (ARO README only)
  - runs/P2-GATE-FOLDS/folds.json, runs/P2-GATE-M{1,2,3,4,5}/items.jsonl (image ids ONLY read), runs/P2-GATE-M3/family.json (n_rule), runs/P2-GATE-M2/threshold.json (keys only)
  - exp_p2/run_gate_m4.py, exp_p2/run_gate_m3.py, exp_p2/gate/{folds,pipeline,data,config,evidence,dcache,fit_threshold,analysis_m4}.py, exp_p2/scoring.py
  - runs/P2-GATE-M4/driver.log, runs/P2-GATE-M4.driver.out (timestamps only)
coverage: >
  Metadata and the seven data JSONs of SugarCrepe (1.7 MB total) were downloaded and only parsed as JSON, never executed. No outcome
  (y, d, z, flips) of any M-run was read. NOT covered: SugarCrepe data_card.pdf and data_unrefined/ (not fetched); the paper's own per-subset
  count table (not located in the converted text; counts below are computed from the released files); ARO/CREPE/VALSE/Winoground are
  one-line fit notes from the ARO README and recollection, not full reads; UniDisc's training-set contents were not re-read here.
claims:
  - statement: SugarCrepe is MIT licensed, built on COCO image-caption pairs, images are COCO val2017, negatives written by ChatGPT then filtered by text-only plausibility models (adversarial refinement).
    status: supported
    evidence: repo LICENSE (MIT, "Copyright (c) 2023 RAIVN Lab"); GitHub API license key mit; README "We use images of COCO-2017 validation set"; paper Sec. 4, 4.1 (stages 1 and 3), App. D licensing
    level: E2 (README and paper sections read; repo data files parsed)
    confidence: 0.9
  - statement: The seven data files hold 7,511 (image, positive, negative) rows over 1,560 distinct COCO val2017 images; every image file is present in our local val2017.zip.
    status: supported
    evidence: research/paper2/data/sugarcrepe-probe/*.json + SHA256SUMS.txt; scratch scripts counted rows, ids, zip membership
    level: E4
    confidence: 0.95
  - statement: SugarCrepe images overlap our calibration, headroom and test pools only partially (95, 36, 83 and 137 images for cal, head, test-300, test-500), and on those images the SugarCrepe positive caption is usually not the caption stored in folds.json.
    status: supported
    evidence: runs/P2-GATE-FOLDS/folds.json (sha1 3dfed9ee90b340a9); id sets equal the image ids of runs/P2-GATE-M2, M3, M4 items.jsonl (checked)
    level: E4
    confidence: 0.95
  - statement: The pinned M4 runner cannot take an external negative-caption file without a code change, and a 300-item run is refused by the committed n-rule (R2 = 500).
    status: supported
    evidence: exp_p2/run_gate_m4.py:61-70, 94, 101, 193, 215-217; runs/P2-GATE-M3/family.json n_rule.test_fold = 500
    level: E3
    confidence: 0.95
competing_explanations: []
unknowns:
  - Whether UniDisc's training data contain COCO val2017 captions or SugarCrepe text (SAP U8, unmeasured).
  - Decision headroom of hard negatives on UniDisc (requires a GPU run).
  - SugarCrepe's own per-subset counts as printed in the paper (not located here).
next_test: {hypothesis: "Hard negatives raise the share of decisions that a token-level gate can flip", intervention: "family H: 300 SugarCrepe pairs on fresh val2017 images, M4 stage reused with gate threshold from M2", primary_metric: "paired Y^GM vs Y^none (as SAP section 2), plus the share of flipped decisions under corruption", falsifier: "flip share under corruption stays at or below the 1-2 percent seen on random negatives", gpu_hours: "2.2 wall-h (range 2.0-2.6)"}
```

# Hard-negative family on COCO images for Paper 2: SugarCrepe feasibility

Verdict: **feasible, with a small code change and a new committed items file; best on fresh images, not on the M4 test images.**

Tags: SF = source fact, INF = inference, OURS = our verified result (E4, from files in this repo), HYP = hypothesis.

## 1. SugarCrepe: download, licence, split, subsets, counts

- SF: Hsieh, Zhang, Ma, Kembhavi, Krishna, "SugarCrepe: Fixing Hackable Benchmarks for Vision-Language Compositionality", arXiv:2306.14610. The task: each COCO image has a positive caption and an LLM-written hard negative. The NeurIPS 2023 Datasets and Benchmarks citation is given in the repo README (BibTeX key hsieh2023sugarcrepe); the arXiv page itself lists no venue. (Brief calls it NeurIPS 2023 D&B; consistent with the README.)
- SF: Repo https://github.com/RAIVNLab/sugar-crepe, default branch main, last commit `0047054b243992f0fad63d6f64f7544862daf846` (2024-02-13). Retrieved 2026-10-29. Licence: MIT (LICENSE file, "Copyright (c) 2023 RAIVN Lab"; the paper's App. D says all source data are publicly released by prior work, i.e. COCO).
- SF: Download is the `data/` folder of the repo: seven JSON files, no separate archive. Sizes (bytes): add_att 158,863; add_obj 484,593; replace_att 176,843; replace_obj 361,126; replace_rel 312,629; swap_att 154,665; swap_obj 57,569. Total about 1.7 MB. Schema per row: `{"filename": "000000085329.jpg", "caption": ..., "negative_caption": ...}`, keys "0", "1", ... Also in the repo, not fetched: `data_unrefined/` and `data_card.pdf`. SHA-256 of the seven files: `research/paper2/data/sugarcrepe-probe/SHA256SUMS.txt`.
- SF: Images are COCO-2017 validation (README: "We use images of COCO-2017 validation set"). The filename is the zero-padded val2017 id, so `int(filename.split('.')[0])` is our `image_id`. OURS: all 1,560 distinct ids exist in the local `val2017.zip` (no image download needed).
- SF: Negatives: ChatGPT generates them (paper Sec. 4.1 stage 1), then "adversarial refinement" subsamples so that text-only commonsense and grammar models cannot separate positive from negative (stage 3). Humans validated a sample (README); details are in the paper and data card, not re-read here.
- OURS (counted from the released files): rows per subset, distinct images, rows whose positive and negative both have 5 to 32 UniDisc tokens (our fold rule, runtime tokenizer path `NousResearch/Llama-2-7b-hf`):

| subset | rows | distinct images | in 5-32 tokens |
|---|---|---|---|
| replace_obj | 1,652 | 823 | 1,649 |
| replace_att | 788 | 524 | 784 |
| replace_rel | 1,406 | 777 | 1,401 |
| swap_obj | 245 | 224 | 242 |
| swap_att | 666 | 593 | 657 |
| add_obj | 2,062 | 908 | 2,058 |
| add_att | 692 | 497 | 692 |
| total | 7,511 | 1,560 (union) | 7,483 |

  28 rows exceed 32 tokens in the positive or the negative (max 57; per subset: replace_obj 3, replace_att 4, replace_rel 5, swap_obj 3, swap_att 9, add_obj 4, add_att 0); none is under 5. The same image (and often the same positive) recurs across subsets and within a subset, so one row per image must be sampled.
- OURS: every one of the 7,511 positives is a COCO val2017 caption of its own image after whitespace normalisation as in `common.load_captions` (6,353 match byte for byte; the rest differ only in whitespace). So the positives are original COCO captions, not LLM rewrites.

## 2. Overlap with our pools (image ids only)

Id sets: `folds.json` cal (300) = runs/P2-GATE-M2 items, head (100) = M3 items, test (300) + test_ext (200) = M4 items (all three set-equalities checked). M1 (200) and M5 (100) items come from the probe id lists (200 of them) and folds (100 of them).

| pool | SugarCrepe images in pool (distinct) | SugarCrepe rows on those images |
|---|---|---|
| M2 calibration (cal, 300 images) | 95 | 105+50+82+16+32+126+49 = 460 |
| M3 headroom (head, 100 images) | 36 | n/a (not tabulated per row) |
| M4 test base (test, 300 images) | **83** | 433 |
| M4 test, all 500 (test + test_ext) | **137** | 707 |
| probe 1 + 2 images (494) | 160 | not tabulated |

Per subset, distinct SugarCrepe images inside the M4 test-300: replace_obj 43, replace_att 30, replace_rel 45, swap_obj 13, swap_att 26, add_obj 53, add_att 27 (inside test-500: 77, 49, 70, 22, 44, 88, 45).

- OURS: **overlap with the test-300 fold is 83 images, with test-500 137 images** (positive control: counts are non-zero in every subset, so the id format matches, as in SAP AB.6 L6). A hand check of five matched ids (SAP L7 style) is NOT done.
- OURS: on overlapping images the SugarCrepe positive equals the caption we drew into folds.json in only a minority (test 68 rows, test_ext 34, cal 84, head 33 rows, against 365, 240, 376, 154 with a different positive). INF: even on the M4 test images, a SugarCrepe item is a new (image, c+, c-) triple, so no M4 outcome can be reused.
- INF: 83 or 137 images are too few for 300 items and they were already used as the final holdout. Pool for a 300-item hard-negative family, excluding cal, head, test, test_ext, probe 1 and 2 and the M1/M5 items, rows with both captions in 5-32 tokens: **5,343 rows on 1,132 distinct images** (replace_obj 595 images, replace_att 367, replace_rel 556, swap_obj 156, swap_att 440, add_obj 651, add_att 355). Enough for about 40 to 43 images per subset (swap_obj is the smallest, 156).
- Role of the data: a fresh-image family is a new hold-out disjoint from tuning folds; the M4 test images stay the final holdout of the preregistered main task.

## 3. Alternatives on COCO images (one line each)

- ARO COCO-Order (Yuksekgonul et al. 2023): README confirms it is built on the COCO retrieval set, MIT repo licence; negatives are word-order shuffles (not confirmed from the README), which SugarCrepe's own paper reports as exploitable by text-only models. Poor fit: a blind-text cue would confound the image direction.
- ARO VG-Relation and VG-Attribution: images are a subset of GQA per README, not COCO. No.
- CREPE (Ma et al. 2023): Visual Genome-based (recollection, not re-read here). No.
- Winoground: non-COCO images (brief states it; consistent with UniDisc using it only for its own retrieval check, CLOSEST-WORK 2026-10-28 line 203). No.
- FOIL-COCO: already family B (one-word noun foils, clean images only, no corruption). Differs from the proposal because B has no gate.
- VALSE and other benchmarks: not examined.

## 4. Can the pinned M4 runner take per-item negatives from a file?

Item schema consumed by `process` (run_gate_m4.py): `idx, gid, image_id, caption, neg_caption`; `n_tok` is checked by `folds.token_check`. The negative caption is already an item field, so **the per-item `neg_caption` needs no change**. What blocks a file-driven run:

1. Items are built only from `runs/P2-GATE-FOLDS/folds.json`: `folds.ensure_folds(...)` at **run_gate_m4.py:94** (make_ctx) and **:215** (get_items), plus `test_items(f, 500)` at **:101** (the splice donor pool, `run_gate_m3.donor_for`, uses `ctx.fold`) and **:217**. `ensure_folds` takes a `path` argument already (folds.py:146), but M4 does not pass one. Minimal change: add `--folds-path` to `main` (line ~188) and pass `path=` at 94 and 215; set `fold=` at 101 from the same file. `check_fold_tokens` only needs the keys it finds (`folds.get(k, [])`), so a JSON with `test` (300 items), empty `cal`, `head`, `test_ext` works.
2. **n-rule guard**: `check_n_against_rule` (run_gate_m4.py:61-70, called at :193) reads runs/P2-GATE-M3/family.json, whose `n_rule.test_fold` is **500** (rule R2). A 300-item run is refused ("--n 300 does not match the committed n-rule"), and `--n 500` would fail at :218 (the file has only 300). Needs an explicit bypass when `--folds-path` is given, with n = 300 stated in the new prereg addendum. Not a data issue but a preregistration one.
3. `gid` is stored per item, not computed from the fold name, so a new range (for example 3000 + idx) avoids reusing mask and jitter streams of the 2000-range test fold (`FOLD_GID_OFFSET` in config.py:18 is used only when building folds). No code change if the items file carries the gids.
4. Run id: `--run-id` exists in `base_parser`; use a new id (for example P2-GATE-M4H) so that nothing overwrites P2-GATE-M4.
5. Analysis: `exp_p2/gate/analysis_m4.py:640` reads `folds.folds_path()` for the planned items and defaults to P2-GATE-M4; it needs the same `--folds-path` option (its `--run-id` and `--family-run` options exist).
6. The family file `runs/P2-GATE-M3/family.json` (jpeg 10, noise 0.1, splice 128; endpoint d) and `runs/P2-GATE-M2/threshold.json` are reused unchanged as prerequisites; `ps_frozen.json` (patch, swap) is reused.

So: roughly 10 to 20 lines in run_gate_m4.py and analysis_m4.py, no change to scoring, items, or the model; plus tests, a builder script for the items file, and a committed prereg addendum before any GPU use. Per rule 2, the implementation is not done here.

Tokenizer and length: the fold rule is 5 to 32 caption tokens (config.TOK_RANGE = (5, 32), `UniScorer.caption_ids` path). Both c+ and c- are tokenised; the text-direction null is cached per length n (DCACHE has DI for n = 7-29, 31 and DT for n = 8-29, 31; other lengths in 5-32 are built on demand, 2 to 3 extra passes each, about 65 MB per length). **7,483 of 7,511 SugarCrepe rows fit (99.6 percent)**; the 28 that do not are excluded and counted, not replaced (SAP A2.1 item 2). The negative is longer than the positive by 4.5 tokens on average in add_obj and 2.5 in add_att, 0 to 0.1 in the other subsets (computed).

## 5. GPU-time estimate for 300 items (no GPU used for this)

- OURS: M4 took 500 items from 2026-10-28 23:10:06 to 2026-10-29 02:53:50 (runs/P2-GATE-M4/driver.log) = 3 h 43 m 44 s wall = 26.8 s per item, including chunk restarts (12.5 min soft deadline per chunk, duty 0.5, 38 chunk records), model load per chunk (about 34 to 48 s), and one manual resume after "max chunks reached" at 01:34. Pass count per item is unchanged by a different negative (the hard negative replaces `neg_caption` in the 2 caption-lambda passes and the text-direction arms).
- Estimate for 300 items on the same stage: **about 2.2 wall-h (range 2.0 to 2.6)**; add about 10 to 15 minutes for the on-demand null-cache lengths. Dropping the patch and swap conditions would save perhaps 20 percent, but ps_frozen.json fixes the condition order, so I do not recommend it. The 12 GB laptop GPU is shared with S2: run after S2, one GPU job at a time, with the usual go-ahead, telemetry and memory cap.
- **Calibration can be reused.** B is computed with the caption masked (pipeline.gate_scores: image_B, caption masked; null D from the cached layout-only matrices), so the M2 threshold (`threshold.json`, fitted from per-item B and D arrays of 300 clean cal images) depends on the caption only through its length. No new calibration run is needed. Caveat (INF): SugarCrepe image selection is not a random draw from val2017, so exchangeability with the calibration images is an assumption; state it as a limit and report calibration risk on the clean hard-negative images as a check.

## 6. Leakage and contamination

- SF: SugarCrepe positives are COCO captions and the images are COCO val2017. The earlier SAP statement stands (AB.6): COCO captions are probably in UniDisc's training data and this is unmeasured (U8). INF: the same holds for the positives here; the LLM-written negatives are new text, but the model's score of the positive may be memorised, so any gain in "accuracy" is not evidence of grounding. Report next to the family.
- Train-test overlap with our own folds: none by construction if the fresh pool above is used; checked against folds.json (cal, head, test, test_ext), probe-1/2 ids, M1/M5 items. A SAP-style leak check (L0 to L8, with a hand-checked sample) needs to be run on the final pool before GPU use.
- Benchmark artefacts: the negatives were generated and filtered with text-only models, which reduces but does not remove text-only cues (the SugarCrepe paper's point). Remaining concerns that matter for our statistic: (a) length asymmetry in add_obj and add_att changes the caption layout seen by the image-direction pass (the cached D null depends on length) and the text pmi is a mean over caption tokens; report the equal-length subsets separately; (b) a gate that flips decisions on a bi-modal (accuracy near 100 percent or near chance) dataset says little; headroom is HYP until run; (c) same image and positive reappear in several subsets, so sample one row per image; (d) ChatGPT-generated negatives may share phrasing patterns across items (not tested here).
- Licence: MIT for annotations; COCO images keep their own terms (CC BY 2.0 per image on COCO, annotations CC BY 4.0 per COCO's site, not re-checked here), already in use in this project.

## 7. Recommendation

1. Use SugarCrepe as a **new family (H)** on 300 fresh val2017 images from the 1,132 above, one row per image, stratified over the seven subsets (about 43 each), selected with a fixed seed before any GPU use. Do not use the 83 or 137 overlapping test images as the family.
2. Write a prereg addendum (hypothesis, n = 300, rows, analysis, how it enters the multiplicity count) and commit the items file with SHA-256 before the run.
3. The first useful check is cheap and needs no GPU on the new data: the clean-image accuracy of the existing "none" arm on SugarCrepe is unknown (HYP: lower than on random negatives, hence more headroom). That can be read after the run only; a pilot of 50 items (about 25 wall-min) would answer it earlier, if the lead wants to spend GPU time before committing 2.2 h.

## Files

- `research/paper2/data/sugarcrepe-probe/` (7 data JSONs, `SHA256SUMS.txt`, `LICENSE.txt` (MIT, from the repo at the pinned commit), GitHub API metadata `repo_meta.json`, `contents_data.json`, `commit_main.json`)
- scratch scripts (not committed): the counting scripts are in the session scratchpad; they read only image ids of runs and the JSON files.
