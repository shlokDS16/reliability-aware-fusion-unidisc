---
agent: data-steward
date: 2026-10-29
time: 21:05 IST (local system clock; the machine runs on IST)
brief: L7 sign-off of SAP addendum A6 r1 section A6.3 and red-team condition C6-10 for the Study 2 fresh fold (runs/P2-LRF-FOLD)
sources_examined:
  - runs/P2-LRF-FOLD/folds_lrf.json (test list only: image_id, neg_image_id, neg_len_image_id, idx, gid, neg_idx, neg_len_idx)
  - runs/P2-LRF-FOLD/manifest.json, runs/P2-LRF-FOLD/builder_report.json, runs/P2-LRF-FOLD/leak_check.json (metadata only)
  - research/paper2/prereg/SAP-ADDENDUM-A6-LRF-2026-10-29.md lines 146-165 (A6.3, C6-10)
  - exp_p2/gate/build_lrf_fold.py (docstring, discover_sources, collect_sources, leak_check)
  - the 34 builder-scope files and 1 extra file listed in section 2, and the seven SugarCrepe JSONs in research/paper2/data/sugarcrepe-probe/
coverage: >
  Image-id-type fields only (image_id, image_ids, neg_image_id, neg_len_image_id, mismatch_image_id) in items.jsonl,
  selection.json, pool.json, folds*.json, and in runs/P2-HARDNEG-ITEMS/*.json. Name fields (coco_file, sugarcrepe_filename)
  in the 5 h_l7 rows of the extra leak_check.json. Key-name inventories of every file. The three non-image SugarCrepe
  release JSONs (commit_main, contents_data, repo_meta) were opened for key structure only (0 image-id fields).
  NOT opened: model outputs, arrays, telemetry, stdout logs, and the 162 other JSON/JSONL files under runs/P2-* that
  fall outside the C6-10 file classes (names listed, contents unread). mismatch_of (int list in selection.json files)
  was not value-checked, because it is not an image-id-type field.
claims:
  - statement: "The exclusion union (C6-10) has 2526 image ids, the same size the builder recorded."
    status: supported
    evidence: "check script (section 6); manifest exclusion.n_union = 2526"
    level: E4
    confidence: 0.97
  - statement: "No fold image_id (533 ids) is in the exclusion union."
    status: supported
    evidence: "0 overlaps with the builder-equivalent union and with the extended union; 0 overlaps per source"
    level: E4
    confidence: 0.97
  - statement: "All 533 fold image_ids are unique; negatives are fold items and differ from their item's image."
    status: supported
    evidence: "533 unique; neg_image_id == image_id: 0; neg_len_image_id == image_id: 0"
    level: E4
    confidence: 0.98
  - statement: "The five L7 sample rows are in their named groups, are the smallest matched id, and their coco_member names are well formed and present in val2017.zip."
    status: supported
    evidence: "builder_report.json l7; all five rows pass every check (section 5)"
    level: E4
    confidence: 0.97
  - statement: "The manifest's file list equals the file list found independently."
    status: mixed
    evidence: "34 of 34 builder-scope files agree with counts; one file (runs/P2-HARDNEG-ITEMS/leak_check.json) is in the brief's enumeration but not in the C6-10 classes, so the builder did not read it. Its 5 ids are already in the union, so the union size is unchanged."
    level: E4
    confidence: 0.9
  - statement: "idx runs 0..532 in order, gid = 8000 + idx, and every negative points to another fold item."
    status: supported
    evidence: "idx sequence exact; gid violations 0; neg_idx and neg_len_idx point to other items with the stated image ids"
    level: E4
    confidence: 0.98
competing_explanations:
  - "The union might be incomplete because of files outside the C6-10 classes (162 JSON/JSONL run files, not opened). This is a scope question, not a check failure: C6-10 defines the classes, and it is the spec that governs the fold."
  - "mismatch_of (int lists, same length as items) might hold image ids rather than per-item indices. Not verified (not an image-id-type field). If it held image ids, they could be outside the union. The mismatch_image_id values (which are image-id-type and were read) are fully inside the union."
unknowns:
  - "Whether any of the 162 out-of-class run files (for example chunks.jsonl, l7_rows.json, hardneg_audit_sheet_*.jsonl, codebook.json, results.json) holds image ids of images that the fold could contain."
  - "Semantics of mismatch_of in the probe, smoke and M0 selection files."
next_test: {hypothesis: none (sign-off only), intervention: "none", primary_metric: "n/a", falsifier: "n/a", gpu_hours: 0}
---

# L7 sign-off: LRF fresh fold (A6.3, C6-10)

Verdict: **L7: SIGNED (data-steward)**, on the checks defined by A6.3 and C6-10 as written. Residual scope items are in section 7; they do not change any check result.

## 1. Checks run (CPU only; no model, no GPU, no outputs opened)

| # | Check | Result |
|---|---|---|
| 1 | Union of image ids over the enumerated sources (C6-10 classes plus the HARDNEG *.json files) | 2526 (manifest 2526) |
| 2 | Fold image_ids in the union | 0 (builder-equivalent union and extended union); 0 per source |
| 2 | Fold image_ids unique | 533 of 533 |
| 3 | L7 rows: image_id in named group; smallest matched id; coco_member form; name in val2017.zip | 5 of 5 pass |
| 4 | idx = 0..532 in order; gid = 8000 + idx | pass, 0 violations |
| 4 | neg_image_id != image_id; neg_len_image_id != image_id | 0 violations each |
| extra | neg_idx and neg_len_idx point to items with the stated image ids; neg ids are fold ids | 0 violations |
| extra | folds_lrf.json SHA-256 equals manifest folds_lrf_sha256 | match |
| extra | the seven SugarCrepe files match SHA256SUMS.txt | 7 of 7 match |

## 2. File lists (union inputs)

Enumerated with the C6-10 classes (`runs/P2-*/` items.jsonl, selection.json, pool.json, folds*.json; the output directory P2-LRF-FOLD is excluded by design). 34 files. The same set as `manifest.json` `exclusion.discovered_files` (34 entries), and the same per-file counts (34 of 34).

| File (relative to runs/) | Image ids |
|---|---|
| P2-GATE-CPU/denoise_check/items.jsonl | 20 |
| P2-GATE-EPRED-FIT/items.jsonl | 100 |
| P2-GATE-FOIL/pool.json | 540 |
| P2-GATE-FOIL-FIT/items.jsonl | 239 |
| P2-GATE-FOIL-TEST/items.jsonl | 298 |
| P2-GATE-FOLDS/folds.json | 900 |
| P2-GATE-H3/folds_check.json | 0 |
| P2-GATE-H3/items.jsonl | 50 |
| P2-GATE-M1/items.jsonl | 200 |
| P2-GATE-M2/folds_check.json | 0 |
| P2-GATE-M2/items.jsonl | 300 |
| P2-GATE-M3/folds_check.json | 0 |
| P2-GATE-M3/items.jsonl | 100 |
| P2-GATE-M4/folds_check.json | 0 |
| P2-GATE-M4/items.jsonl | 500 |
| P2-GATE-M5/folds_check.json | 0 |
| P2-GATE-M5/items.jsonl | 100 |
| P2-GATE-S2/items.jsonl | 300 |
| P2-GATE-S2-FIG/items.jsonl | 0 (file names only, no 12-digit ids) |
| P2-GATE-S2-SMOKE/items.jsonl | 0 |
| P2-HARDNEG-ITEMS/folds_hardneg.json | 350 |
| P2-HARDNEG-ITEMS/folds_hardneg_h3.json | 50 |
| P2-LRF-RESCORE/items.jsonl | 500 |
| P2-M0-STAGE2/items.jsonl | 10 |
| P2-M0-STAGE2/selection.json | 10 |
| P2-PROBE-01/items.jsonl | 300 |
| P2-PROBE-01/selection.json | 300 |
| P2-PROBE-02/items.jsonl | 200 |
| P2-PROBE-02/selection.json | 200 |
| P2-SMOKE-01/items.jsonl | 3 (6 with mismatch_image_id; the 3 extra are inside the union) |
| P2-SMOKE-01/selection.json | 300 |
| P2-SMOKE-01.failed-selfcheck/selection.json | 300 |
| P2-SMOKE-02/items.jsonl | 3 |
| P2-SMOKE-02/selection.json | 200 |

Extra, read by me, not in the builder's C6-10 classes (so the manifest did not read it): `P2-HARDNEG-ITEMS/leak_check.json` (5 ids in `h_l7`; all 5 already in the union; no change to the union size).

Also in the union: the seven SugarCrepe JSONs (add_att 692 entries, add_obj 2062, replace_att 788, replace_obj 1652, replace_rel 1406, swap_att 666, swap_obj 245) give **1560** unique image ids (every filename is `NNNNNNNNNNNN.jpg`; int(stem) parses for all entries).

**Union size: 2526 image ids.** Identical under the builder's definition (image_id and image_ids only) and under the extended definition (adds neg_image_id, neg_len_image_id, mismatch_image_id, and the 12-digit names of the extra file). The extended definition adds 0 ids.

Group sizes against `manifest.files_read` (all match): folds.cal 300, folds.head 100, folds.test 300, folds.test_ext 200, probe1+probe2 494, P2-GATE-M1 200, P2-GATE-M5 100, foil.pool 540, sugarcrepe 1560, hardneg.h 350.

## 3. Manifest vs independent list

- Manifest files that I did not find: none.
- Files I found that the manifest did not read: `P2-HARDNEG-ITEMS/leak_check.json` (brief enumeration; outside the C6-10 classes). Recommendation: include `runs/P2-*/*.json` in the class for future folds (see section 7).
- Names in the manifest's `files_read` that are groups, not files: mapped to their files as above.

## 4. Fold checks (folds_lrf.json, test list)

- n = 533; cal, head and test_ext are empty.
- image_id unique: 533.
- Overlap with the union: 0. Overlap with each source file: 0 (the per-source table is empty).
- Negatives: neg_image_id and neg_len_image_id are fold ids (533 of 533 each), differ from the item's own image, and equal the image_id of the item at neg_idx and neg_len_idx.
- idx 0..532 in list order; gid = 8000 + idx (no violations).

## 5. L7 sample rows (builder_report.json)

| group | image_id | group size | smallest id in group | coco_member | in val2017.zip | not in fold |
|---|---|---|---|---|---|---|
| folds.cal | 1296 | 300 | yes | val2017/000000001296.jpg | yes | yes |
| folds.head | 885 | 100 | yes | val2017/000000000885.jpg | yes | yes |
| folds.test | 1490 | 300 | yes | val2017/000000001490.jpg | yes | yes |
| folds.test_ext | 1532 | 200 | yes | val2017/000000001532.jpg | yes | yes |
| probe1+probe2 | 1761 | 494 | yes | val2017/000000001761.jpg | yes | yes |

The probe group is the id union of P2-PROBE-01 and P2-PROBE-02 (items and selection). The h_l7 rows in the extra file have coco_file and sugarcrepe_filename that contain their image_id, and none of them is in the fold.

## 6. Check script

`C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\f9e01f26-3b7f-40af-a381-11d4b248c68b\scratchpad\l7_union_check.py` (run with `-I`). It prints counts and ids only, never values of other fields. Its output is the source of every number above.

## 7. Residual items (not failures; for the orchestrator)

1. **Scope of C6-10.** The union covers the C6-10 classes plus `P2-HARDNEG-ITEMS/*.json`. Another 162 JSON/JSONL files under `runs/P2-*` (for example `chunks.jsonl`, `l7_rows.json`, `hardneg_audit_sheet_*.jsonl`, `codebook.json`, `results.json`, `family.json`) are outside the classes and were not opened, so whether they hold image ids is unverified. For this fold they fall outside the spec, which governs; for the next fold, the class should be widened to every `runs/P2-*` file that carries image ids.
2. **mismatch_of.** The selection files (PROBE-01, SMOKE-01, SMOKE-01.failed-selfcheck, M0-STAGE2) have an int list `mismatch_of` the same length as `items`. The name suggests a per-item index. Not checked (not an image-id-type field). The `mismatch_image_id` fields (image-id-type, read) are fully inside the union.
3. **Builder definition.** `build_lrf_fold.py` `_collect_ids` reads only `image_id` and `image_ids`. `mismatch_image_id`, `neg_image_id` and `neg_len_image_id` are not collected. The effect here is 0 extra ids, so the union is unchanged, but the definition should match the C6-10 wording (every image id) for future builds.
4. **Extra file.** `P2-HARDNEG-ITEMS/leak_check.json` is not in the builder's classes. It adds no ids here.
5. **Ledger.** The brief asked for read-only work except this report, so no ledger row was added.

L7: SIGNED (data-steward)
