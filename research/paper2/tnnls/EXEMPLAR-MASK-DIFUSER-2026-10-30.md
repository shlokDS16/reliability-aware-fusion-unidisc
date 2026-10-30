---
agent: paper-reader
date: 2026-10-30
brief: read one exemplar (Mask-DiFuser, IEEE TPAMI 2026) end to end and write a blueprint for upgrading the Paper 2 TNNLS manuscript
status: report only; nothing in the project was edited except this file
evidence level: E2 for "the paper reports X" (never for "X is true"). Every exemplar number below was read from rendered page images, not from a text layer; re-check against the PDF before quoting. The README was read through WebFetch (a summarised fetch, E1, not a raw read).
page convention: "p.N" is the PDF page (1 to 18); journal page = PDF page + 590 (p.1 = 591, p.18 = 608).
our paper: paper2-tnnls/main.pdf, 15 pages, read in full (pp.1-15). Page shares for it are my estimates from the page images; compile to confirm.
exemplar PDF: C:\Users\Shlok\Downloads\Language models papers\Mask-DiFuser_A_Masked_Diffusion_Model_for_Unified_Unsupervised_Image_Fusion.pdf
---

# 1. Bibliographic facts

| Item | Value | Where |
|---|---|---|
| Title | Mask-DiFuser: A Masked Diffusion Model for Unified Unsupervised Image Fusion | p.1 |
| Venue | IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI), vol. 48, no. 1, January 2026, pp. 591-608 | p.1 header |
| Pages | 18 PDF pages: 15.7 of text and figures, then references (p.16 bottom to p.18), then three author biographies with photos (p.18) | pp.1-18 |
| Authors | Linfeng Tang, Chunyu Li (equal contribution), Jiayi Ma (Senior Member IEEE, corresponding); Electronic Information School, Wuhan University | p.1 footnote |
| Dates | received 12 Feb 2025; revised 14 Aug 2025; accepted 9 Sep 2025; published 12 Sep 2025; current version 3 Dec 2025 | p.1 footnote |
| DOI | 10.1109/TPAMI.2025.3609323 | p.1 |
| Funding | National Natural Science Foundation of China, grant 62276192 | p.1 |
| Code | github.com/Linfeng-Tang/Mask-DiFuser (given in the front-page footnote, not in a data-availability section) | p.1 |
| Index terms | image fusion; unified model; masked image modeling; diffusion model | p.1 |
| Counts | 18 figures, 12 tables, 1 algorithm box, 18 numbered equations, 76 references, no appendix or supplement in this PDF, no limitations section, no acknowledgment or AI-use statement seen | whole paper |
| Task | image fusion with no ground truth: infrared-visible (IVIF), near-infrared-visible, multi-polarization, medical, multi-exposure (MEF), multi-focus (MFF); one model trained on DIV2K natural images, applied without fine-tuning | IV-A, p.6-7 |

Experimental scale (IV-A, p.6-7): 8 test datasets (361 MSRS pairs, 100 RoadScene, 100 Nirscene, 40 Polarization, 100 Harvard, 360 SICE, 100 MEFB, 20 Lytro); 4 task-specific plus 7 unified baselines per task (11 columns of rivals in every table); six no-reference metrics (EN, AG, SF, SD, SCD, PI); public pretrained rival models with no retraining; training 3,500 epochs, 128x128 crops, batch 8, AdamW 5e-5, one RTX 4090 class GPU (p.6-7). No seeds, repeated runs, confidence intervals or significance tests appear anywhere in the 18 pages (this is my reading of the PDF; there is no supplement to check).

# 2. Structure and page shares

Body text and floats run p.1 to p.16 (about 15.7 pages). Shares below are of that body.

| Section | Pages | Approx. pages | Share | Content |
|---|---|---|---|---|
| Abstract, index terms | p.1 | 0.4 | 3% | single paragraph, about 190 words, ends "significantly outshines SOTA" |
| I. Introduction | p.1-3 | 1.7 | 11% | three paragraphs of context, then the ground-truth problem, then Fig. 1, then a four-bullet contribution list (p.2-3) |
| II. Related Work (A fusion, B diffusion models, C masked image modeling) | p.3 | 0.9 | 6% | ends each subsection by naming the gap |
| III. Methodology (A overview, B dual masking / masked diffusion model / loss / inference) | p.3-6 | 3.3 | 21% | Figs. 2-3, Eqs. (1)-(18), Algorithm 1 (p.6) |
| IV-A, IV-B. Setup and the first task | p.6-7 | 1.0 | 6% | datasets, baselines, metrics, fairness statement, then Fig. 4 |
| IV-C to IV-G. Six fusion tasks, one subsection each | p.7-12 | 5.0 | 32% | per task: figure, one qualitative paragraph, one quantitative paragraph, one table |
| IV-H. Extended experiments (generative prior, detection, segmentation, grid size, mask ratio, sampling steps, cost) | p.12-15 | 3.2 | 20% | Figs. 13-17, Tables VII-XI |
| IV-I. Ablation | p.15-16 | 1.2 | 8% | six variants, Fig. 18, Table XII |
| V. Conclusion | p.16 | 0.3 | 2% | one paragraph, no limitations or future work |
| References, biographies | p.16-18 | 2.3 | outside body | 76 references; biographies with photos |

Shape: the method takes one fifth of the body; the evidence takes about two thirds. Every claim of superiority is a figure plus a table plus two paragraphs.

# 3. Every figure

Layout convention for all the qualitative grids (Figs. 4-12): inputs first, then baselines in a fixed order, then ours last; two rows of seven panels; each panel labelled "(a) Name" in bold below the image; one green box and one red box drawn on the same two regions in every panel, with the zoomed crop of each box inset in the bottom corners of the panel. The same method order is used in all nine grids, so a reader learns the layout once. Extra colour marks (red or blue ellipses) are added only where a rival visibly fails.

| Fig. | Page | Type | What it shows and how it is laid out | Why it persuades |
|---|---|---|---|---|
| 1 | p.2 | composite: three workflow diagrams plus a result strip | (a) end-to-end with a complex loss; (b) dual-stage with hand-crafted rules; (c) their self-supervised masked diffusion scheme; (d) five-column visual comparison (IR/Under, VI/Over, TC-MoA, DeFusion, Mask-DiFuser) with red and green circles on differences. Dashed coloured frames separate the three paradigms; ours is framed in red. | Puts the problem, the three families of prior work, the proposed route and a first look at the quality on page 2, before any equation. |
| 2 | p.4 | framework diagram | (a) the full model: diffusion chain on top, dual masking at left, content branch (feature extractor, APFM, reinforcement block) and semantic branch (transformer encoder) feeding a denoising U-Net through cross-attention; legend bottom left. (b) detail of the attention parallel feature mixer in its own dashed frame. Branch names in red and pink italics; symbols x_t, F_f, S_A, S_B carried through to Eqs. (9)-(11). | Every symbol in the text sits at a place in the picture; the caption names the training idea in one line. |
| 3 | p.4 | schematic of masking | (a) a clean image with a four-colour legend for M1 to M4; (b) the vanilla scheme (two complementary 8x8 masks, Mask A and B, and the two masked images); (c) the dual scheme with the extra degradation patches. Same image, same grid, side by side. | The new idea is shown as a difference between two adjacent panels. |
| 4 | p.7 | qualitative grid (14 panels), IVIF, MSRS night scenes | the layout above; infrared and visible inputs, 11 baselines, ours; pedestrian zoomed in red, a lawn or building in green. | Shows the hard case (night) first, where the claim "most prominent pedestrians" is checkable by eye. |
| 5 | p.8 | qualitative grid, MSRS day scenes | same order and colours. | Second regime of the same dataset. |
| 6 | p.8 | qualitative grid, RoadScene | same, with over-exposed visible input. | Targets the exposure failure the text names for five rivals. |
| 7 | p.8 | qualitative grid, near-infrared and visible, Nirscene | same. | Haze and colour claims. |
| 8 | p.9 | qualitative grid, polarization (DoLP and S0 inputs) | two baselines swapped for polarization-specific ones (PAPIF, CPIFuse). | The baseline set is adapted per task but the order rule holds. |
| 9 | p.10 | qualitative grid, medical CT-MRI, Harvard | zoom boxes on soft tissue; task-specific rivals EMFusion, ALMFNet, MMIF-INet. | Shows the specialised rivals are not ignored. |
| 10 | p.10 | qualitative grid, multi-exposure, SICE | under- and over-exposed inputs, then task-specific MEF rivals and unified rivals. | Exposure correction is visible in one glance. |
| 11 | p.11 | qualitative grid, MEFB | same. | Second dataset for the same task. |
| 12 | p.12 | qualitative grid, multi-focus, Lytro | a blue ellipse marks halo artifacts in GIFNet, the one rival that wins on sharpness metrics. | The figure is used to explain why a rival's higher sharpness number is not a better image. |
| 13 | p.12 | input/output pairs | four columns (dual infrared, dual under-exposed, dual over-exposed, dual unfocused); inputs on the top row, outputs below. | Demonstrates the learned prior with a one-line test: feed it two copies of a bad image. |
| 14 | p.13 | downstream detection overlay | YOLOv5 boxes drawn on each method's fused image, same 14-panel layout. | Moves the argument from "looks better" to "works better downstream". |
| 15 | p.14 | downstream segmentation | night and day scenes, each a grid of class maps per method plus ground truth; a nine-class colour legend bar across the top. | Uses real labels, the only place with ground truth in the paper. |
| 16 | p.14 | sensitivity panels | (I) three grid sizes on a blue background; (II) four mask ratios on a green background; red ellipses mark block artifacts or colour cast. Background colour separates the two studies. | Each design choice shows its failure mode when changed. |
| 17 | p.15 | violin plots plus a line | 12 small panels (6 metrics x 2 datasets) of the metric distribution at 2, 5, 10, 15, 20 sampling steps (5 steps chosen); a red dashed line is inference time on a second axis; white triangles mean, black lines median. | The only place a distribution rather than a point is shown; justifies the 5-step choice. |
| 18 | p.16 | ablation grid | top row on SICE (source, variants I to IV, ours), bottom row on MSRS (infrared, visible, variants V, VI, ours); blue box marks the patch artifact when the content branch is removed. | Every removed component has a visible symptom. |

# 4. Every table

Common conventions: all tables are 12 rows (11 baselines plus "Mask-DiFuser" in bold). Metrics EN, AG, SF, SD, SCD (higher is better) and PI (lower is better), with arrows in the header. Best cell in each column: bold on a light-red fill; second best: light-purple fill. The colour key sits in the caption. In Tables I and VIII the key leaked raw LaTeX (`\colorbox[HTML]{FFC7CE}` visible in the caption) on pp.8 and 13; a polish error to avoid. Captions are in IEEE small caps ("Quantitative Results of Mask-DiFuser vs. SOTA Methods on the ... Dataset").

| Table | Page | Dataset | Baselines (count, names) | Metrics | Notes |
|---|---|---|---|---|---|
| I | p.8 | MSRS and RoadScene (IVIF), two blocks side by side | 11: LRRNet, DDFM, KDFuse, TDFusion, SDNet, U2Fusion, DeFusion, SwinFusion, TC-MoA, GIFNet, CCF | EN, AG, SF, SD, SCD, PI | ours is best or second in each column read by me (for example MSRS SCD 1.860 against TDFusion 1.864 first; the text still says "consistently demonstrates top-tier") |
| II | p.9 | Nirscene | same 11 | same 6 | text: best on five metrics, second on SF (16.715 against GIFNet 17.210) |
| III | p.9 | Polarization | 11, with PAPIF and CPIFuse replacing KDFuse and TDFusion | same | text admits SCD "slightly lags behind DDFM" |
| IV | p.10 | Harvard (medical) | 11, with EMFusion, ALMFNet, MMIF-INet replacing the IVIF-only rivals | same | GIFNet best on AG and SF; text: "competitive" there |
| V | p.11 | SICE and MEFB, side by side | 11, with HSDS-MEF, SAMT-MEF, CRMEF, EAT as MEF rivals | same | text admits SF and PI "not optimal" on MEFB |
| VI | p.12 | Lytro (MFF) | 11, with ZMFF, DB-MFIF, Fusion2Void, MDLSR_RFM | same | Fusion2Void best PI; GIFNet best AG and SF; ours best EN, SD, SCD |
| VII | p.13 | MSRS detection (YOLOv5) | 11 | AP@0.50, 0.65, 0.80, 0.95 and mAP[0.5:0.95], each split Person / Car / Average | text says only "comparable"; ours is best at AP@0.50 and AP@0.80 averages (0.963, 0.794) |
| VIII | p.13 | MFNet segmentation (SegNeXt retrained) | 11 | IoU for nine classes and mIoU | ours 57.69 mIoU; SDNet and TC-MoA tie second at 56.71 |
| IX | p.14 | grid size (4x4, 8x8, 16x16) on MSRS and SICE | not a baseline table | six metrics | default 8x8 is not the best on every column; the text says "balanced" |
| X | p.15 | mask ratio M1:M2:M3:M4, four settings, MSRS and SICE | not a baseline table | six metrics | default 4:1:4:1 highlighted |
| XI | p.15 | computational cost | 11 plus ours | parameters (M), FLOPs (G), time (s) | ours 171.26 M, 4667.4 G, 1.655 s; the text concedes it "may lag behind lightweight methods" |
| XII | p.16 | ablation, MSRS and SICE | variants I-VI (w/o content, w/o semantic, w/o APFM, w CNN, w diffusion loss only, w/o degradations) plus ours | six metrics, best/second highlight | text concedes "a slight decline in the PI metric" |

Ablation tables are IX, X (design sweeps) and XII (component removal); Fig. 18 pairs XII with pictures, Fig. 16 pairs IX and X, Fig. 17 stands in for a sampling-steps table.

# 5. Results and discussion

Pattern for each task subsection (IV-B to IV-G, pp.7-12):
1. Qualitative paragraph first. It lists rivals by name in one sentence, gives the failure mode they share (for example haze, overexposure, texture blur), and then switches with "In contrast" to the proposed method with the same zoomed region.
2. Quantitative paragraph second. It goes metric by metric, says what each metric measures in a few words ("highest SD strongly demonstrates the optimal contrast"), and names exceptions when they exist.
3. A closing synthesis sentence ties both to the claim ("capable of learning high-quality prior information").

Weaving: every number is introduced as confirming something the reader just saw in the figure ("consistent with the qualitative observations", p.9). When a rival wins a number, the text uses the figure to argue the number misleads (GIFNet's sharpness comes with halos, Fig. 12 blue ellipses, p.11-12; "may not fully align with human visual preferences", p.12). That is the exemplar's best rhetorical device.

Why the method wins: the text gives one mechanism per claim, tied to a design choice: dual masking simulates degradations, so robustness; the generative prior learned from clean natural images, so natural exposure and colour; the semantic branch, so global colour. These are backed by the ablation (Fig. 18, Table XII) and the sensitivity sweeps (Figs. 16-17), but the causal "this is because" sentences in the task subsections themselves are not tested.

Limitations and failure cases: there is no limitations section and no failure-case figure. Limitations appear only as concessions inside results paragraphs (second place on SCD, SF, PI; slower and larger than lightweight rivals, Table XI) and the conclusion is purely positive (p.16). The hyperparameters (grid size, mask ratio, sampling steps) are chosen by comparing on the same test datasets used to report the headline results, with no held-out selection set; there are no repeats or intervals.

Added evidence beyond fusion quality: object detection and semantic segmentation as downstream tasks (Figs. 14-15, Tables VII-VIII), a prior-visualisation test (Fig. 13), a computational-cost table, and sensitivity sweeps. Together they answer the usual reviewer questions in-paper.

# 6. Writing style

Contribution statements (p.2-3): four dash bullets, one to three lines each. Pattern: "We propose X, termed Y, which ..."; "A novel Z is devised to ..."; "A ... model integrating A and B is developed to ..."; "Extensive experiments demonstrate ...". Each bullet is a named design object, not a measured result, except the last.

Abstract: one paragraph; problem (no ground truth), gap in prior work (hand-crafted rules, subjective losses), method in four clauses, result in one sentence. Claim strength: high. Words such as "ingeniously", "remarkable", "significantly outshines SOTA fusion alternatives" (abstract, p.1) and "consistently demonstrates top-tier performance across all evaluation metrics" (p.7) are used, though Table I shows second place on some cells and no test supports "significantly".

Sentence patterns: "It is evident that ...", "Notably, ...", "In contrast, Mask-DiFuser ...", "Although X ..., Y ...", "Moreover, ...". Failure statements about rivals are specific and local ("lawns, roads, and buildings"), which makes them checkable.

Captions: one line, topic only ("Visual comparison of infrared-visible image fusion results on the MSRS dataset", p.7). They carry no interpretation and no n; interpretation lives in the text. Table captions carry the colour key.

Equations: all numbered, introduced with where-clauses; one algorithm box for training and inference together (p.6). Sections use the IEEE style "III-B" numbering with italic sub-headings.

# 7. README (https://github.com/Linfeng-Tang/Mask-DiFuser/blob/main/README.md, via WebFetch)

Order of content as reported by the fetch:
1. Title linking to the IEEE Xplore record; authors with an equal-contribution mark; venue and year.
2. Badges: an ESI Highly Cited label and a Google Scholar citation count.
3. News: six dated entries, newest first.
4. Method Overview: three images (concept comparison, framework figure, vanilla versus dual masking), each under a short heading.
5. Installation: clone, conda environment (Python 3.8), pip install from requirements.txt.
6. Inference: step 1 download pretrained weights (Baidu Drive or Google Drive) into `checkpoint/`; step 2 one `test.py` command with task type, two input folders, output path and GPU ids.
7. Train: step 1 download DIV2K and the expected folder layout; step 2 a `torchrun` launch on four GPUs.
8. Results: one heading per task and dataset (IVIF night on MSRS, RoadScene, MEF on SICE and MEFB, medical, Nirscene, polarization, MFF), each with a single clickable image copied from the paper's qualitative grids.
9. Detection and Segment: one image each.
10. Citation: BibTeX block, plus a request to cite and star.
11. Contact: two author emails; maintenance "in spare time".
12. Acknowledgments: code borrowed from two diffusion repositories.
Gaps in that README: only DIV2K has a download link; the eight evaluation datasets are named only in image headings; no results table; no seeds or expected metric values.

# 8. Gap analysis against our paper (ranked)

Our paper now (main.pdf, 15 pages): abstract p.1; introduction with Fig. 1 (conceptual, "no data") p.1-2 (about 1.5 pages); related work p.2-3 (0.9); Section III shared setting with Table I p.3-4 (1.4); Study 1 (Section IV, Figs. 2-5, Lemma 1, Propositions 1-2) p.4-9 (about 5.0); Study 2 (Section V, Figs. 6-8, Tables II-III) p.9-12 (about 3.1); discussion, limitations, deviations p.12-13 (1.3); conclusion and reproducibility p.13 (0.5); references p.13-15 (1.5). No figure shows a real image, a real caption or a real per-token map with the image beside it; all of Figs. 1, 3 and 6(a) are labelled "no data", Fig. 6(c) shows weight maps without the images.

Hard constraints: 15-page cap (we are at it, so every addition needs an equal cut); preregistered results are frozen; anything added now is exploratory and labelled so; no invented numbers. Page costs are my estimates.

| Rank | Change | Where in our paper | Page cost and what moves to the supplement | New experiments? | Risk |
|---|---|---|---|---|---|
| 1 | **Real-image qualitative figure** (the analogue of exemplar Figs. 4-13): one row per item showing the clean image, the Gaussian-noise image, the per-token weight map w_j, the per-token evidence map Delta_j, the true and wrong caption text, and the verdict of the unweighted rule against LRF. Keep the existing rule that items are the first in the fold file by position, and add the rule for any extra rows in advance (for example first discordant item of each kind in file order). | Replace Fig. 6(c) (p.10), which already shows weight maps for three items with no image. | +0.1 to +0.3 page if Fig. 6 grows; pay by moving Fig. 6(b) (partial-dependence curves, already descriptive) to the supplement (about -0.2 page). | No new experiment. Needs rendering from stored per-item arrays and the regenerated corrupted images (supplement S-VI says the corruption seeds are re-runnable). | Cherry-picking charge: fix the selection rule in writing and label "descriptive, not evidence" (Fig. 6 caption already does). COCO image licences need attribution; check the supplement note on image reuse. Do not imply the weight maps show reliability. |
| 2 | **Algorithm box** for the frozen LRF: inputs (features, frozen weights, margin T), steps for score, weight, sum, sign; one side box for the conformal threshold of Study 1 (Eq. 6). The exemplar's Algorithm 1 (p.6) is the model. | New box in Section V-B (p.9) after Eq. (14); optionally one in IV-A for Eq. (6). | +0.25 page. Pay by shortening the "Weight model and decision" paragraph (about -0.15) and moving the full feature list (7 groups, already in supplement S-IV) to the supplement. | None. | None, as long as it restates the pinned frozen specification (hash db7fdb4e...) and adds no step that was not in the plan. |
| 3 | **Compress the four contributions** to 2-3 lines each, leading with the object and the bounded result; move the details (Proposition 2 wording, 17 families, family H, hash pins) to the sections that already hold them. Exemplar bullets are 1-3 lines (pp.2-3). | Introduction p.1-2, the numbered list (currently about 0.5 page). | -0.25 page. Nothing moves; the text is in Sections III-E, IV, V. | None. | The statement "Each item was delivered regardless of the outcome" and the "does not show" wording must survive; do not let compression turn a bounded null into "no effect". |
| 4 | **Cost table** like exemplar Table XI (p.15) but for our setting: rows for the UniDisc scoring pass (network rows per item, seconds per item, peak memory) for Study 1 and Study 2, one row stating LRF adds no network row, one row for CLIP and SigLIP marked "not measured" (the Table III note already says so). | Merge text of IV-C10 and V-F (p.9, p.11) into one small table in Section V-F. | +0.15 page, minus about 0.2 page of prose cut from IV-C10 and V-F: net about -0.05. | None; numbers already in the text and supplement S-II, S-IV. | Quote only the measured figures; leave the unmeasured cell empty. |
| 5 | **Result-first Fig. 1 or a one-panel headline figure.** Exemplar Fig. 1 puts a data strip on page 2. Option A: add to Fig. 1 a second panel with the Table II L1 estimate (0.733 to 0.802, interval) and the Study 1 null (three intervals inside the margin), each in its own panel and colour. Option B: leave Fig. 1 as the mechanism and move Fig. 7(a) up to page 2. | Fig. 1, p.2; Fig. 7(a), p.11. | Option A: +0.2 page on p.2, minus Fig. 7(a) (about -0.25 page) if its content is folded in. | None. | Conflicts with the project rule "no figure holds both Study 1 and Study 2 numbers" (figure captions file, header). Decide that rule on purpose. Showing only the Study 2 result on page 2 would misrepresent the pair of studies. Keep the same intervals as Table II and Fig. 4; recompute none. |
| 6 | **Rebalance pages**: Study 1 (null) takes about 5 pages, Study 2 (positive) about 3.1. Move Proposition 2 with its Fig. 3 and the token-detection Fig. 5 to the supplement, keep Lemma 1 (Eqs. 8-10) and a one-sentence pointer. This pays for ranks 1, 2, 4, 5. | Section IV-A (p.5-6) and Figs. 3 and 5 (pp.6, 8). | -0.55 page (Proposition 2 column plus Fig. 3) and -0.3 page (Fig. 5 plus its paragraph IV-C4) | None. Existing results only. | Contribution 1 (a closed-form condition) rests on Lemma 1 and Proposition 2; rewrite contribution 1 to match, and do not alter any statement of the theory. Fig. 5 carries the preregistered falsifier for the gate score (the score is below a texture score); the one sentence stating that falsifier must stay in the main text. |
| 7 | **Figure-then-table-then-takeaway paragraphs** in Section V-D and IV-C: open each result with what the figure shows, then the table numbers with a plain-language reading ("a gain of x points on n items, interval a to b"), then one sentence that states the bounded takeaway. This is the exemplar's per-task pattern (Section 5 above), minus the adjectives. | Section V-D (p.10-11) and the end of each Study 1 result item (p.7-8). | 0 pages, only reordering; may save a few lines. | None. | Keep every verdict word fixed by the preregistered reading rules (confirmed, not rejected, rejected under Holm, not run). |
| 8 | **Colour-blind-safe decision shading** in Tables I-III in addition to bold: one fill for "rejected at the preregistered level", none otherwise, with the key in the caption. Mirrors exemplar tables' fills but encodes decisions, not rank. | Tables I and II (p.4, p.10); caption of Fig. 7. | 0 pages. | None. | Do not shade by rank or by smaller p. Fill only where the test rejected at its preregistered level; in Table II that is L1 (one-sided), L-LEN and L4 (Holm p = 0.049, borderline, keep the paper's own wording), not L3. |
| 9 | **Optional exploratory sweep**: Gaussian noise at a few extra sigma values on the same frozen LRF (analogue of exemplar Figs. 16-17 and Tables IX-X). | A small forest plot in Section V-G or the supplement. | +0.2 page if in the main text; put it in the supplement. | Yes: new scoring on GPU (12 GB laptop, crash history); the fresh fold is already used for the confirmatory test, so every sweep point is exploratory, descriptive only, with the same label as Fig. 8. No selection may follow from it. | High: new scoring on the confirmatory items; a post-hoc look at the same fold; claims about "robustness" are not licensed. Recommended last, only if time and GPU allow, and in the supplement. |

What is already at parity or better than the exemplar and needs no change: the ablation (Fig. 8, forest plot with intervals; exemplar Table XII has no intervals), the limitations section (VI-C), the deviation list (VI-D), the exact paired tests with multiplicity control, the reference-encoder table (III) and the cost reporting.

Suggested net page budget (estimate): moves out about -1.2 pages (ranks 3, 6 and part of 1); moves in about +0.9 pages (ranks 1, 2, 4, 5 option B); net about -0.3 pages, enough margin to compile at 15 pages. Compile after each step; do not rely on these estimates.

# 9. What we should NOT copy and why

1. Superiority adjectives and "significantly" without a test ("outshines", "consistently top-tier across all metrics", abstract p.1 and p.7). Our claims are bounded by preregistered intervals and the paper says what is not shown; keep that wording.
2. Best and second-best highlighting by rank. Our bold rule is "null rejected at the preregistered level"; ranking cells would turn a confirmatory design into a leaderboard. Use shading only for decisions (rank 8).
3. Selecting hyperparameters (grid size, mask ratio, sampling steps) on the same test sets that report the headline (Tables IX-X, Fig. 17). We froze LRF before any test item; no choice may be made on fresh-fold items. Any sweep (rank 9) is descriptive only.
4. Causal "this is because" explanations of why the method wins or rivals fail. Our Discussion lists five open readings and states that the learned weights do not show reliability or corruption tracking; do not replace that with a mechanism story. Fig. 8 knockouts do not support one.
5. A wall of 11 baselines per table. Adding rivals now would be exploratory, unregistered and outside the studied question; the paper already says it does not claim a verifier that ranks against dedicated encoders. If a comparison is added, it goes in the supplement, labelled exploratory, with no tests.
6. No uncertainty reporting (single run, no seeds, intervals or tests across the 18 pages). Ours is the opposite and must stay so.
7. A conclusion with no limitations. Ours has Section VI-C and VI-D; keep them in the main text (the exemplar admits shortcomings only in passing).
8. Hand-picked panels with highlight ellipses on rival failures. Our qualitative figure (rank 1) needs a selection rule fixed in writing, and no ellipses that imply a result.
9. Method branding and downstream-task add-ons (detection, segmentation): LRF is already a named object, and there is no downstream label task on the same pairs; adding one would be a new study.
10. Layout slips: the raw `\colorbox` text left in two table captions (Tables I and VIII); a figure caption with a typo ("Visiual", Fig. 15). Grep our captions for backslashes and typos before submission.
11. Very short titles of the form "Name: descriptor". Our long title pins the claim to the tested condition (Gaussian noise, one model, preregistered); shorten only if every qualifier stays in the abstract's first sentence.
