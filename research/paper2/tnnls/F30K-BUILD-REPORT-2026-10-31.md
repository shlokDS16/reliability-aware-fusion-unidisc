# Flickr30K transfer test (SAP addendum A7): build report, 2026-10-31

agent: lab-engineer (build half only; no GPU used, nothing committed, no pinned file and no existing runs/ directory touched)
binding plan: `research/paper2/prereg/SAP-ADDENDUM-A7-F30K-2026-10-31.md`

## STOP: one point of A7.2 cannot run as written (decision needed before any GPU time)

The fold built exactly as A7.2 reads (all 1,000 test images, caption index 0, exclusions a, b, c only) has **128 of 1,000 true captions longer than 32 UniDisc tokens** (none shorter than 5; max 99, median 22). The pinned runner applies the SAP A2.1 rule at run time
(`pipeline.check_fold_tokens`): out-of-range items are excluded, and **more than 10 percent of a fold failing it raises `FoldDefect` and stops the run before item 0**. 128/1000 = 12.8 percent. I confirmed this by calling
`folds.token_check` on the built file (defect = true, mismatch with the frozen counts = 0). `run_gate_m4.py` is pinned and may not be edited, and patching the 10 percent check inside the wrapper would change the pinned pipeline, so I did not.
A second effect of the same fact: 111 of the 1,000 primary wrong captions and 128 length-matched wrong captions are longer than 32 tokens (up to 99), a regime the COCO folds never contained (all COCO captions are 5 to 32 tokens).

Decision for the lead (an amendment of A7.2 before any scoring; it uses caption lengths only, no model output):
- **Option D (prepared, recommended):** add exclusion (d) "true caption outside 5 to 32 UniDisc tokens (SAP A2.1)", applied at build time before the negative pool is formed. Result (dry run in the scratchpad, not in runs/): **n = 872 kept**, a=0, b=0, c=0, d=128;
  every item and both wrong captions in range; length-matched negative exact for 872/872; 872 >= 800, so not "underpowered" under A7.6. Build: delete the five files of `runs/P2-LRF-F30K-FOLD/` and `runs/P2-LRF-PLAN-F30K/family.json` (the builder refuses to overwrite), then run
  `"C:/Users/Shlok/Downloads/Multi-Modality Language model/.venv/Scripts/python.exe" -I exp_p2/gate/build_f30k_fold.py --token-range-rule`. The dry run is at `C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\7c923a60-3ca1-49ad-be26-24621fa0e61a\scratchpad\alt-fold\` (fold sha1 ea5ec4c2cb4d16bb).
- **Option A (as written, currently in runs/):** keep the 1,000-item fold; the runner refuses it. Not runnable without editing a pinned file.
The files now in `runs/P2-LRF-F30K-FOLD/` and `runs/P2-LRF-PLAN-F30K/` are the as-written build (n_kept = 1000, family `n_rule.test_fold` = 1000). They are untracked; replace them if Option D is chosen. Image hashes in manifest.json are the same for both.

## Files (all new; nothing committed)
- `exp_p2/gate/build_f30k_fold.py` fold builder (CPU; `--token-range-rule` optional, off by default; refuses to overwrite).
- `exp_p2/run_gate_lrf_f30k.py` thin entry point: swaps `common.load_image` (used by `pipeline.prep_image` and the runner self-check) for a loader reading `flickr30k/test_images/<id>.jpg` with a SHA-256 check against manifest.json, plus a config record (dataset, revision, image_dir, manifest hash, licence note, conditions) via `runner.run_items`; restores both on exit and on error; run id whitelist `P2-LRF-F30K`; flag checks (L1 set with `--family-run P2-LRF-PLAN-F30K`, `--folds-path` must be the F30K fold, no extra cells, no gate-true-layout). Nothing else is patched.
- `exp_p2/gate/gate_driver.py` (not pinned; edited): stage `lrf-f30k`, `F30K_FOLD`, `PLAN_RUN` map (default_n now reads the n of the stage's own plan family file; lrf-l1/dn/sev still read `P2-LRF-PLAN`, tested), `STAGE_MAX_CHUNKS["lrf-f30k"] = 24`.
- `analysis/paper2/lrf/f30k_analysis.py` F1, F-NI, F-LEN exactly as A7.4; imports `mcnemar_counts`, `mcnemar_p`, `boot_ci`, `clopper_pearson`, `load_predictions` unchanged from `analysis/paper2/lrf/a6_analysis.py`; a fresh `SeedSequence(0)` generator per block, 10,000 resamples, 90 and 95 percent percentile intervals; labels confirmed / not confirmed, `non_inferior` true/false, `headline_gain_claim_allowed` (p <= 0.025), "underpowered (n of 1,000)" below 800; checks `lrf_score_meta.json`.
- `tests/exp_p2/test_lrf_f30k.py` 30 tests. Run: `test_lrf_f30k.py` + `test_lrf_sev.py` + `test_lrf_dn.py` = 56 passed; also `test_gate_integration`, `test_gate_a6_options`, `test_gate_build_lrf_fold`, `test_a6_analysis` = 110 passed together with sev/dn.
- Outputs (as-written build): `runs/P2-LRF-F30K-FOLD/{folds_f30k.json, builder_report.json, exclusions.json, leak_check.json, manifest.json}`, `runs/P2-LRF-PLAN-F30K/family.json`.

## Data and licence (read before use)
- Source: Hugging Face dataset `nlphuji/flickr30k`, revision `2b239befc81b6e3f035ce6bd52f5f4d60f5625f7` (last modified 2023-01-19). Downloaded: `README.md`, `flickr_annotations_30k.csv` (12.9 MB, sha256 395990db603a...), `flickr30k-images.zip` (4,390,240,817 bytes, sha256 2ce2420c0d17...; under the 5 GB rule). The repo's `flickr30k.py` loading script was NOT downloaded or run.
- Folder (outside the repository, sibling of the COCO data): `C:\Users\Shlok\.cache\dlm_dl\flickr30k\` with `hf\` (the three files) and `test_images\` (the 1,000 test-split images, 138 MB, extracted by file basename only). Files were read only by my scripts (`python -I`); nothing in the folder was executed.
- Split: CSV column `split`: train 29,000, val 1,014, test 1,000 (the standard Karpathy split, as A7.2 says).
- Licence/terms: the HF dataset card has **no licence field** (the README holds only the paper reference and the homepage link). The homepage cited by the card, https://shannon.cs.illinois.edu/DenotationGraph/ (read 2026-10-31 through a page summary, not the raw page): access is by request form; images are offered "for non-commercial research and/or educational purposes"; "use of the images must abide by the Flickr Terms of Use"; the authors state they do not own the image copyright; no separate caption terms; redistribution not addressed. Consistent with A7.2: research use, images not redistributed, the repository stores identifiers only. The lead should note that the form-based access on the homepage was not used by me (the HF mirror was downloaded as the plan says).

## Decisions where A7.2 is silent (all fixed in code before any draw or model output)
1. "Ascending order of file name" = Python string order of the CSV `filename` (e.g. `1000092795.jpg` before `10002456.jpg`); `idx` = position in the final list; `gid = 9000 + idx`; `image_id` = the numeric Flickr id (`<id>.jpg` is checked to be canonical).
2. True caption: `raw[0]`, whitespace-normalised like the COCO loader.
3. Content words: `re '[a-z]+'` on the lower-cased caption, length >= 3, minus the `STOP_WORDS` frozenset written in the builder (it includes the number words "one", "two"). Digits are not letters; hyphenated words split.
4. Wrong caption: per item `default_rng([2026, 1031, idx])`, `j = rng.integers(0, n)` redrawn until `j != idx` and no shared content word. Length-matched: the SAME generator continued; candidates = items with no shared content word and exactly the same token count, else the nearest token count (ties uniform); one drawn with `rng.integers`; signed difference stored (`neg_len_diff`, `neg_len_exact`). Neither wrong caption is restricted to a different category (no annotations exist), so `neg_restricted = neg_len_restricted = False`.
5. Pool of the negatives = items that survive (a) and (b) (and (d) if used). If (c) removes an item, idx and draws are recomputed (fixpoint; here zero removals, one iteration).
6. (b) reference sets: the 500 COCO design images = `runs/P2-GATE-FOLDS/folds.json` test + test_ext (identical to the 500 M4 items, checked); the 450 COCO fold images = `runs/P2-LRF-FOLD/folds_lrf.json` test[:450]. dHash = grey, resize 9x8 LANCZOS, bit = left > right (64 bit), threshold <= 4.
7. Family file: copy of the L1 noise0.1 cell (`D_c` 18), `n_rule = {rule: "all kept items, A7.2", test_fold: <n kept>}`.

## Build results (as written; Option D in brackets)
- Test split 1,000; excluded a (undecodable) 0, b (dHash <= 4) 0, c (no admissible negative) 0 [d token range 128]; **kept 1,000 [872]**. Fewest admissible negatives for any item: 305.
- dHash: minimum distance of any test image to the 950 COCO images = 6; 3 images at distance 5 to 8, 26 at 9 to 12, median 18; nothing within 4. Positive control: 100 re-compressed (JPEG q70, 90 percent size) COCO copies, all caught (max distance 2); different images >= 21 apart.
- Length-matched wrong caption: 968 of 1,000 exact, 32 nearest (mean absolute difference 0.149, max 45) [872 of 872 exact]. Primary wrong caption mean absolute token difference 9.2.
- Leak/consistency check F0 to F4 passed (ids and file names, order, gid range free of COCO folds, FOIL, H and the LRF fold 8000-8532, kept images > 4 from COCO, negatives word-disjoint and consistent).
- Conditions: with the single-cell family and `--sanity ""`, `--denoise-for ""` each item has exactly `clean` and `noise0.1` (tested through `m4.process` with the fake network: no patch, swap, denoised or extra condition; arrays `clean_*` and `noise0.1_*` incl. `deltaL`). The noise image is the L1 call with stream `rung_rng(gid, "noise", 0)` and the new gids 9000+; it differs from the stream of gid 8000.

## GPU launch (lead; after the decision above, after the code audit and the commit, the driver refuses a dirty `exp_p2/` or `tools/`)
Guard flags are the S2/L1 values (`LRF_MEM_SLOW`); the first author's go-ahead and the project hold files apply as for L1. Memory notes: first author's rule "no unattended GPU".

    "C:/Users/Shlok/Downloads/Multi-Modality Language model/.venv/Scripts/python.exe" -m exp_p2.gate.gate_driver --stage lrf-f30k --extra "--max-used-first-mib 11000 --max-used-mib 11000 --max-rise-mib 4500 --mem-frac 0.75 --slow-factor 3 --slow-min-s 2"

Then, on CPU:

    ... -m exp_p2.gate.lrf_score --run-id P2-LRF-F30K --pins runs/P2-LRF-PINS/pins.json --conds clean,noise0.1
    ... -m analysis.paper2.lrf.f30k_analysis            # writes runs/P2-LRF-F30K/f30k_analysis.json

(The driver's `--n` default is read from `runs/P2-LRF-PLAN-F30K/family.json`; any other `--n` is refused by the runner's n-rule check.)

## Expected runtime
The brief assumed about 3 s per item. Measured on this laptop: P2-LRF-DN (2 conditions, no text-direction passes, 450 items) 58 min = 7.7 s per item; P2-LRF-SEV (3 conditions) 73 min = 9.7 s per item; P2-LRF-L1 (4 conditions, text direction) about 2.4 h for 450 items = about 19 s per item.
Clean + noise0.1 with text-direction passes should cost about 10 s per item (guess from those three runs; the first 5-minute chunk will measure it): **about 2.4 h for 872 items, about 2.8 h for 1,000**, plus a model load of 35 to 90 s per chunk. Sizing to 3 s per item would have given 6 chunks and a stop at about half the items (the run is resumable); I set `STAGE_MAX_CHUNKS["lrf-f30k"] = 24` (as lrf-dn; 15-minute chunks, about 5.5 h of room, 1.5x slack on the measured estimate). Deviation from the brief, reported.

## Concerns
1. The 10 percent token-rule defect (above) blocks the run as written; Option D needs an A7.2 amendment (still before any scoring).
2. If Option D is used the wording of A7.2 "every test-split image ... minus (a), (b), (c)" and "1,000 images" changes to 872 (A7.6's 800 floor is still met with 72 items to spare; a build-time or run-time difference in the tokenizer cannot occur, mismatch with the runtime counter was 0).
3. Three test images are within 5 to 8 bits of a COCO image (nearest 6); not excluded under the preregistered threshold 4. The lead may want to look at them by eye (ids in `leak_check.json` are counts only; ask me for the list).
4. `gate_driver.py` was edited (stage + `PLAN_RUN` map); it is not pinned but the gate-auditor should read the 14-line diff.
5. Flickr30K images are Flickr user photographs; COCO also comes from Flickr, so the dHash screen is the only duplicate control; it screens against 950 images, not all 5,000 COCO val images.
