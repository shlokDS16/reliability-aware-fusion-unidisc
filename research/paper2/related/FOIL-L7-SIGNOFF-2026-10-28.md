```yaml
agent: data-steward
date: 2026-10-28
brief: L7 hand-checked sample (SAP AB.6) and pair-integrity check for family B (FOIL-COCO hard negatives); sign off or block B before any GPU use
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (AD.6 lines 1008-1024; AB.6 lines 1171-1179; amendment log line 1115 for n_B)
  - research/paper2/method/IMPL-B-FOIL-SUITE-2026-10-28.md
  - research/paper2/related/DATA-CHECK-FOIL-CORRUPTIONS-2026-10-28.md (earlier steward note, by reference only)
  - exp_p2/gate/foil.py (existence only; the checks below do not import it)
  - runs/P2-GATE-FOIL/{manifest,pool,leak_check}.json
  - runs/P2-GATE-FOLDS/folds.json (cal 300, head 100, test 300, test_ext 200)
  - FOIL test JSON C:\Users\Shlok\.cache\dlm_dl\coco\foil\foilv1.0_test_2017.json (SHA-256 recomputed, equals the manifest)
  - COCO cache: ann_extract/annotations/captions_val2017.json; annotations_trainval2017.zip -> instances_val2017.json; val2017.zip (images)
  - runs/P2-PROBE-01/selection.json and runs/P2-PROBE-02/selection.json (the image_id field only; see concern 5)
coverage: >-
  L7 as written (five matched ids, one per group cal, head, test, test_ext, probe) checked by hand, with the raw FOIL name,
  the COCO file name and the image opened from val2017.zip. Extended by the brief to 29 pairs (pixels viewed) and, by script,
  to every pair of the committed pool (240 fit, 300 test) for pairing, same-image, one-swap and COCO-caption identity, and to
  COCO instance-category evidence for the foil word. NOT covered: the other 274 test pairs and 222 fit pairs were not viewed
  (the 274 have the foil category absent from COCO instances; absence is weak evidence because instance annotations are
  incomplete); no check of images beyond val2017; no check of FOIL train/val files (only the test file is used); the FOIL
  file revision (July 2017 info block versus the Oct 2018 revision) is unresolved.
claims:
  - statement: "FOIL annotations[].id is a valid pair key: all 99,480 ids have exactly one original and one foil on the same image; foil_id is a per-record key (198,960 unique, none repeated) and is NOT a pair key. The earlier steward statement 'no pair key' is superseded."
    status: supported
    evidence: "runs/P2-GATE-FOIL-L7/l7_out.json (n_ids 99480, n_ids_bad_pairing 0, n_foil_id_unique 198960, n_foil_id_repeated 0); script l7_check.py"
    level: E4
    confidence: 0.95
  - statement: "L0 id mapping holds: for all 32,150 FOIL images, the integer id equals the number in the COCO_val2014_<12 digits>.jpg name; every pool image id is in COCO val2017 (captions_val2017 image list) and its val2017/<12 digits>.jpg exists and opens; all 240 + 300 pool originals are verbatim (after lower-casing and white-space collapse) one of the image's COCO val2017 captions."
    status: supported
    evidence: "l7_out.json (n_filename_mismatch 0; test_in_val2017 300; fit_in_val2017 240; orig_in_coco_val2017_caps 240 and 300); sheets A to E viewed"
    level: E4
    confidence: 0.95
  - statement: "L6/L7 matched-id counts are reproduced independently: cal 240, head 75, test 238, test_ext 159, probe 383; first matched ids cal 458755, head 172617, test 239537, test_ext 273642 equal those printed by the script author's leak_check.json."
    status: supported
    evidence: "l7_out.json out.matched_counts, out.first_matched; runs/P2-GATE-FOIL/leak_check.json L6, L7"
    level: E4
    confidence: 0.95
  - statement: "The B pool is leak-free against the GATE folds and probes: test ids disjoint from cal, head, probe-1 and probe-2 ids (0, 0, 0 shared of 300); fit ids a subset of cal, disjoint from test, head and probes; no repeated image id; pool order equals (eligible test-fold images, then eligible test_ext images) in stored order for all 300 positions. The 300 test images are all on P test-list images (238 test + 62 test_ext), which AD.6 allows (P and B dependent in data, separate families)."
    status: supported
    evidence: "l7_out.json (test_in_cal 0, test_in_head 0, test_in_probe 0, fit_subset_of_cal true, fit_test_disjoint true, fit_in_head_or_probe 0, test_pool_unique 300, fit_pool_unique 240); l7_sample.py prints 'pool order == (test elig + test_ext elig)[:300]: True'"
    level: E4
    confidence: 0.9
  - statement: "Each of the 240 fit and 300 test pool pairs differs by exactly one token position after lower-casing, and that position equals the file's target_word -> foil_word; the pair is the first record of its image in file order, an original, and its partner is the foil with the same id."
    status: supported
    evidence: "l7_out.json (exactly_one_swap 240/300, swap_matches_fields 240/300, first_record_is_orig 240/300, file_order_ok 240/300, pool_caps_match_raw 240/300)"
    level: E4
    confidence: 0.95
  - statement: "The foil word is wrong for the image in 28 of 29 hand-viewed pairs; in 1 of 29 (142790) the foil object is in the image and the caption is plausibly true; in 2 of the 28 (239537, 473869) the foil object is in the image but the caption is wrong by role. Across all 300 test pairs the foil category is present in the image's COCO instances in 26 (8.7 percent); on my reading of those 26 images, 5 are plausibly true and 7 ambiguous (12 of 300, 4.0 percent), 14 wrong by role."
    status: mixed
    evidence: "l7_rows.json; l7_out.json (foil_cat_present 26 of 300 test, 18 of 240 fit); sheets A to E and flag0/flag1 viewed (eyeball judgement on thumbnails, not a second annotator)"
    level: E4 for counts, E1 for the pixel judgements
    confidence: 0.7
competing_explanations:
  - "A 4 percent plausibly-true or ambiguous foil rate is an eyeball estimate by one reader on thumbnails; a second reader could move it by a few points."
unknowns:
  - "FOIL file revision (July 2017 info block versus the Oct 2018 revision)."
  - "Whether UniDisc or LlamaGen training data contain these images (U8, unmeasured)."
  - "Foil validity of the 274 test pairs whose foil category is absent from COCO instances but that I did not view."
next_test: {hypothesis: "B1 fusion beats the better single direction", intervention: "none from this check", primary_metric: "n/a", falsifier: "n/a", gpu_hours: 0}
```

# L7 sign-off for family B (FOIL-COCO hard negatives)

## 1. What L7 requires, read literally

AB.6 item L7: five matched ids (the first matched id of each of cal, head, test, test_ext and one probe id) are printed with
the raw FOIL name and the COCO file name, and **checked by the data-steward, not the script author**. AD.6 L1 to L5 and AB.6 L0,
L6, L8 are the script author's checks (read here, re-derived below where they bear on L7). The brief adds a wider pair-quality
sample. The pass rule in AB.6 is implicit: each printed id must map from the raw FOIL name to the COCO integer id and to an
existing val2017 file, and the count of matched ids in every group must be above zero (L6), so the checker cannot be vacuous.

## 2. L7 proper: the five matched ids

All five were recomputed from the raw files without importing `exp_p2/gate/foil.py` (script `runs/P2-GATE-FOIL-L7/l7_check.py`).
"First matched" is the first image in the stored order of the fold list that is also a FOIL image.

| Group | Matched count (L6) | First matched id | Raw FOIL name | COCO member | Opens | Image shows | Verdict |
|---|---|---|---|---|---|---|---|
| cal | 240 | 458755 | COCO_val2014_000000458755.jpg | val2017/000000458755.jpg | yes | girl petting sheep, straw floor | PASS |
| head | 75 | 172617 | COCO_val2014_000000172617.jpg | val2017/000000172617.jpg | yes | woman on steps, suitcase of books | PASS |
| test | 238 | 239537 | COCO_val2014_000000239537.jpg | val2017/000000239537.jpg | yes | tennis player, ball and racket | PASS |
| test_ext | 159 | 273642 | COCO_val2014_000000273642.jpg | val2017/000000273642.jpg | yes | dog with remote control | PASS |
| probe | 383 | 564127 (first in probe-1 order); the script printed 2587, also checked | COCO_val2014_000000564127.jpg; ..._000000002587.jpg | val2017/000000564127.jpg; val2017/000000002587.jpg | yes | toilet; banana and doughnut in a bag | PASS |

Findings: raw name -> integer -> val2017 name is a pure zero-pad of the same integer for all 32,150 FOIL images (0 mismatches);
the 2014 and 2017 numbering is the same for these images (val2017 is a subset of val2014 and keeps the ids), and the captions
confirm it: the FOIL original of every pool pair is a COCO val2017 caption of the same integer id (240 of 240, 300 of 300).
Zero-count in any group would have meant a format mismatch; none is zero. The script author's printed first matched ids equal mine
for cal, head, test and test_ext.

## 3. Wider sample: 29 pairs, pixels viewed

Columns: pair integrity (same image and pair id) / exactly one swap equal to target -> foil (after lower-casing) / foil category
in the image's COCO instances. Image verdicts are my reading of the opened val2017 image.

| # | Why sampled | image id | file | pool | swap | integrity | one swap | foil cat in COCO | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 0 | L7-cal | 458755 | ...000000458755.jpg | fit | `sheep` -> `cow` | Y | Y | absent | OK; sheep in image, cow absent |
| 1 | L7-head | 172617 | ...000000172617.jpg | not in pool | `suitcase` -> `umbrella` | Y | Y | absent | OK; suitcase and books, no umbrella |
| 2 | L7-test | 239537 | ...000000239537.jpg | pool-test | `ball` -> `racket` | Y | Y | present | swap OK; racket IS in the image, caption wrong by role (hit the racket) |
| 3 | L7-test_ext | 273642 | ...000000273642.jpg | pool-test | `dog` -> `bear` | Y | Y | absent | OK; dog, no bear |
| 4 | L7-probe | 564127 | ...000000564127.jpg | not in pool | `toilet` -> `bed` | Y | Y | absent | OK; toilet, no bed |
| 5 | L7-probe (id printed by the script) | 2587 | ...000000002587.jpg | not in pool | `banana` -> `sandwich` | Y | Y | absent | OK; banana and doughnut, no sandwich |
| 6 | test-pool-pos1 | 483050 | ...000000483050.jpg | pool-test | `bed` -> `couch` | Y | Y | absent | OK |
| 7 | test-pool-pos2 | 197796 | ...000000197796.jpg | pool-test | `sink` -> `refrigerator` | Y | Y | absent | OK |
| 8 | test-pool-pos3 | 519208 | ...000000519208.jpg | pool-test | `elephant` -> `horse` | Y | Y | absent | OK |
| 9 | test-pool-pos4 | 257566 | ...000000257566.jpg | pool-test | `boat` -> `truck` | Y | Y | absent | OK |
| 10 | test-pool-pos5 | 137246 | ...000000137246.jpg | pool-test | `dog` -> `bird` | Y | Y | absent | OK; swap sits inside the compound 'hot dog' (hot bird) |
| 11 | test-pool-pos6 | 401446 | ...000000401446.jpg | pool-test | `umbrella` -> `tie` | Y | Y | absent | OK |
| 12 | test-pool-pos7 | 569972 | ...000000569972.jpg | pool-test | `surfboard` -> `kite` | Y | Y | absent | OK; compound 'wind surfboard' (wind kite) |
| 13 | test-pool-pos8 | 94185 | ...000000094185.jpg | pool-test | `bear` -> `horse` | Y | Y | absent | OK; compound 'teddy bear' (teddy horse) |
| 14 | test-pool-pos9 | 281447 | ...000000281447.jpg | pool-test | `horse` -> `cow` | Y | Y | absent | OK |
| 15 | test-pool-rand-pos295 | 558073 | ...000000558073.jpg | pool-test | `cat` -> `dog` | Y | Y | absent | OK |
| 16 | test-pool-rand-pos33 | 113235 | ...000000113235.jpg | pool-test | `carrot` -> `pizza` | Y | Y | absent | OK |
| 17 | test-pool-rand-pos118 | 142790 | ...000000142790.jpg | pool-test | `skis` -> `snowboard` | Y | Y | present | swap OK; snowboard IS in the image (left), foil plausibly TRUE |
| 18 | test-pool-rand-pos29 | 416269 | ...000000416269.jpg | pool-test | `train` -> `bus` | Y | Y | absent | OK |
| 19 | test-pool-rand-pos265 | 33104 | ...000000033104.jpg | pool-test | `skis` -> `snowboard` | Y | Y | absent | OK |
| 20 | test-pool-rand-pos286 | 580418 | ...000000580418.jpg | pool-test | `car` -> `train` | Y | Y | absent | OK |
| 21 | test-pool-rand-pos82 | 579091 | ...000000579091.jpg | pool-test | `table` -> `chair` | Y | Y | absent | OK |
| 22 | test-pool-rand-pos144 | 311394 | ...000000311394.jpg | pool-test | `toothbrush` -> `drier` | Y | Y | absent | OK |
| 23 | test-pool-rand-pos13 | 335450 | ...000000335450.jpg | pool-test | `horse` -> `cow` | Y | Y | absent | OK |
| 24 | test-pool-rand-pos245 | 301061 | ...000000301061.jpg | pool-test | `elephant` -> `dog` | Y | Y | absent | OK |
| 25 | fit-pos1 | 337498 | ...000000337498.jpg | fit | `pizza` -> `sandwich` | Y | Y | absent | OK (deep-dish pizza, not a sandwich) |
| 26 | fit-pos2 | 296231 | ...000000296231.jpg | fit | `tv` -> `remote` | Y | Y | absent | OK |
| 27 | fit-pos3 | 361506 | ...000000361506.jpg | fit | `skateboard` -> `kite` | Y | Y | absent | OK |
| 28 | fit-pos4 | 473869 | ...000000473869.jpg | fit | `bowl` -> `bottle` | Y | Y | present | swap OK; bottle IS in the image, but man holds a bowl: wrong by role |

Sample rule: the L7 ids; the first 10 pool test pairs in pool order; 10 pool test pairs drawn with `random.Random(20261028)`
from positions 10 to 299; the first 5 fit pairs (duplicates removed, so 29 distinct images).

Result for the 29: pairing and one-swap hold in 29 of 29; the foil word is wrong for the image in 28 of 29 (2 of those 28 have the
foil object present but the caption wrong by its role); 1 of 29 (142790, skis -> snowboard with a snowboard on the snow) is
plausibly true.

### Pool-wide scripted checks (all 240 fit and 300 test pairs)

| Check | fit | test |
|---|---|---|
| pair id equals the original's id equals the foil's id | 240 / 240 | 300 / 300 |
| both captions on the same image id; image in FOIL images list | 240 / 240 | 300 / 300 |
| pair is first record of the image and is an original | 240 / 240 | 300 / 300 |
| pool captions equal the raw FOIL captions after lower-casing and white-space collapse | 240 / 240 | 300 / 300 |
| original is one of the image's COCO val2017 captions | 240 / 240 | 300 / 300 |
| exactly one differing token position (punctuation stripped) | 240 / 240 | 300 / 300 |
| that position equals target_word -> foil_word of the file | 240 / 240 | 300 / 300 |
| foil category present in the image's COCO instances | 18 | 26 |
| foil introduces an a/an mismatch the original did not have | 7 | 15 |

## 4. Foil words that are possibly not wrong (26 test pairs with the foil category in COCO instances)

Two of these are in the section 3 sample (239537, 142790); the other 24 were viewed separately.

| image id | swap | reading |
|---|---|---|
| 16958 | table->chair | PLAUSIBLY TRUE (wooden chairs visible) |
| 543047 | table->chair | PLAUSIBLY TRUE (dining chairs visible) |
| 255165 | laptop->mouse | PLAUSIBLY TRUE (mouse on desk) |
| 485027 | ball->racket | wrong by role (serving a racket) |
| 70774 | motorcycle->bicycle | wrong by role (the small vehicle is a motorcycle) |
| 159977 | zebra->giraffe | wrong ('a giraffe and a giraffe', one giraffe) |
| 152686 | ball->racket | wrong by role |
| 571893 | book->clock | wrong (clock tiny, books fill the sill) |
| 412286 | ball->racket | AMBIGUOUS ('racquet towards a racket', synonym) |
| 44877 | racket->ball | wrong by role (swinging a ball) |
| 375278 | cat->dog | AMBIGUOUS (black animal, annotations list cat and dog) |
| 496854 | umbrella->tie | wrong by role (holds a tie) |
| 13177 | motorcycle->bicycle | PLAUSIBLY TRUE (bicycle in background) |
| 127530 | ball->racket | wrong by role |
| 78915 | ball->racket | wrong by role |
| 55950 | ball->racket | wrong by role |
| 277020 | table->chair | AMBIGUOUS (seated at a table, chairs present) |
| 83172 | ball->racket | wrong by role |
| 173004 | knife->fork | AMBIGUOUS ('a fork and fork', forks and a knife present) |
| 130579 | ball->glove | AMBIGUOUS (pitcher wears a glove) |
| 248616 | ball->racket | wrong by role |
| 356424 | table->chair | AMBIGUOUS (man seated at a table) |
| 57149 | train->bus | wrong by role (bus waits, train passes) |
| 343524 | ball->racket | AMBIGUOUS ('racket and racket', racket held) |

Counting the 26 (adding 239537 as wrong by role and 142790 as plausibly true): 5 plausibly true, 7 ambiguous, 14 wrong by role.
Plausibly true or ambiguous: 12 of 300 (4.0 percent); upper bound if every category-present pair were not a valid negative:
26 of 300 (8.7 percent). Category-absent pairs are not proof of validity (instance annotations are incomplete: 'table' maps to
'dining table', which is often unannotated), but all 26 category-absent images among the 29 viewed were genuinely wrong.

## 5. Gate rules checked on the committed pool

- AD.6 (i) fit pairs >= 100: 239 expected after the pool-time token rule (240 in the pool, 1 marked), satisfied before GPU.
- L1 fit subset of cal, L2 fit and test disjoint, L3 test disjoint from cal, head, probe-1 and probe-2, L4 no repeated image
  id, L5 counts: reproduced (section 3 table, claims above); pool order reproduced.
- B images are on P test-list images: allowed by AD.6; separate family.

## 6. Verdict and conditions

**L7: PASS** for the ID mapping and the leak-check non-vacuity: the five matched ids map correctly, every group matches, and the
pool is disjoint from the GATE calibration, headroom and probe folds. Concerns (none changes the verdict; the first two need a
decision from the orchestrator before the paper reports B):

1. **n_B mismatch with the preregistration.** AD.6 and the Addendum A2 row of the amendment log (line 1115) fix n_B = 150 (power at n = 150 derived in AD.6); the committed pool and
   the implementer's plan use 300 (the implementer's report says "Shlok's n"). The first 150 pool positions are exactly the
   AD.6 pool (order verified), so the prespecified analysis can be recovered, but the SAP has no amendment row recording
   n = 300. Add one before the freeze, or analyse n = 150 as primary.
2. **Foil label noise, 4.0 percent plausibly-true or ambiguous in the test pool (up to 8.7 percent).** Some "foils" name an object that is in the image
   (chair in a room, mouse on a desk, bicycle in the background, snowboard on the snow). A model that is right about the image is scored wrong.
   The paper must say B is a noisy negative with an estimated 4 percent label noise.
3. **Text-only cues.** In the test pool 15 of 300 foils create an article mismatch that the original did not have (an horse, a
   umbrella); several swaps sit inside a compound noun (hot dog -> hot bird, teddy bear -> teddy horse, wind surfboard ->
   wind kite) or duplicate a word (fork and fork, racket and racket). 11 of 300 test pairs are ball -> racket
   (a likely easy text-direction negative) against 1 of 240 fit pairs, so the fit and test negative mix differ; if the text direction reaches
   0.95 on fit, B is untestable at ceiling (AD.6 rule ii), which is a legitimate outcome, not a failure.
4. **File revision unknown** (info block says July 2017; the Oct 2018 revision may differ). Stated in the paper if B is reported.
5. **Probe-2 selection file.** To check L3 for all 494 probe ids I loaded `runs/P2-PROBE-01|02/selection.json` and kept only the
   `image_id` field (script `l7_check.py`); no item content, caption, index or outcome beyond ids was printed or viewed, and no array or
   items.jsonl was opened. If the orchestrator reads "never open PROBE-02 items with idx > 25" as covering selection.json,
   treat that part of L3 as the script author's check (leak_check.json L3) and my reproduction as extra.

Reproduction: `python -I runs/P2-GATE-FOIL-L7/l7_check.py` (system Python), then `l7_sample.py` and `l7_flag.py` with the project
`.venv` Python (they need Pillow); outputs `l7_out.json`, `l7_rows.json`. The contact sheets (png) were not committed.

L7: PASS
