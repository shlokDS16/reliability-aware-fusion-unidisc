# Worked examples for the v0.4 unit rules (five red-team test papers; reference file)

Status: a specification check, not extraction output. **Reference file: no extraction or adjudication
session ever sees it** (nor worked-examples-v0.3.md). The extractor brief v0.4 and schema v0.4 carry only
synthetic examples (EXTRACTION-PLAN-v0.4 s10.2; red-team audit 3, M4; checked by
analysis/extraction/brief_contamination.py). The method-architect applied the rules (EXTRACTION-PLAN-v0.3 s5
as amended by v0.4 s5: U3 clauses renamed and rewritten, U10 conditions in figures, U14 column index) by
hand to the five papers of the red-team's 2026-10-20 audit 2, reading only the sections listed under each
paper in the screened PyMuPDF text (E2 for those sections only; no paper was read in full). v0.4 changes
against worked-examples-v0.3.md are marked "v0.4". Stage A compares the extractors with these lists; the
rejection test (F1_G below 0.6) is computed on the 7 drawn Stage A records only (plan v0.4 s10.2), and these
five records are reported separately.

U3 clause names (v0.4, brief block K): focal-label; other-own-model; stated-default; value-identity (any
earlier results table that contains the reference arm); full-configuration (removal groups); first-own-arm.

| Paper | Id | T1 i1 | Stratum (strata.py) | Text sha256 (first 16) |
|---|---|---|---|---|
| Decoding Large Language Diffusion Models with Foreseeing Movement (FDM) | M07474 | a | frame R | 3a65e81519b49c3e |
| Muddit: Liberating Generation Beyond Text-to-Image with a Unified Discrete Diffusion Model | M12766 | ab | C1 | c0051304cc6e5438 |
| TrustLDM: Benchmarking Trustworthiness in Language Diffusion Models | M09530 | a | frame R | 5ae8c6aad53ab82d |
| Diffusion vs Autoregression: An Empirical Study on Code Comment Translation | M13864 | a | frame R | cdc9398eb2896360 |
| LLaDA2.1: Speeding Up Text Diffusion via Token Editing | M08100 | a | frame R | b42020f73dc5c64c |

Ids from `analysis/screening/ft-t1/t1-decisions-all.jsonl` (sha256 962e3171...); titles from
`research/review/corpus/new-records-2026-10-15-v2.jsonl`. Notation: G = comparison group, K = contrast
unit, "fig-only" = a figure-only unit (U10). "Second factor" = the level of U7 that splits groups.

Every list below gives one reading. Where a judgement remains, it is on an attribute that is outside
every alignment key (factor_type and the rq_class derived from it, credited_ablation) and is measured
by M-class on matched groups; those places are marked "attribute".

---

## 1. M07474, FDM (method; training-free decoding method; four base models)

Sections read: abstract; Table 1 (p.1); s5.1 setup and results (p.7-8); Table 2 (p.8); Table 3 (p.9);
s5.2 and Figures 4-7 (p.9-10); Appendix D Figures 8-11 (p.17).

**Focal model and configuration.** The abstract presents FDM as the paper's method first ("we propose the
Foreseeing Decoding Method (FDM)"); FDM-A is a second own method. FDM is training-free, so (U2b) the focal
system is FDM on the base model of the first own arm of the main-results table. Table 1 sits in the
introduction and is not the main-results table (U2d); Table 2 is. Its first own arm is "FDM (K=2)" in the
LLaDA column group. No default width is stated for FDM (the setup states one for FDM-A only), so the focal
configuration is FDM (K=2) on LLaDA (U2e ii).

**H units.** The abstract prints no number: no H-1 unit. H-2 (C-F1a: an introduction table is not the
"first main-text results table" when an experiments-section table reports the final method): Table 2. The
first cell the text quotes is "on the LLaDA model and ARC benchmarks ... FDM with the search width 2 is
86.00%" (C-F1c: the benchmark row group of the quoted cell). **H01 = 86.00**, origin F1-table, Table 2,
row group ARC, row FDM (K=2), column "LLaDA / Accuracy". One unit.

**S14.** Table 2; own row FDM (K=2) (row group ARC, column LLaDA / Accuracy); no CT6 claim, so the baseline
is the first other arm of the ARC row group: **Probability (T=256)**.

**Groups** (U1: every results table and figure in reading order, wherever placed):

| G | Where | Second factor | Arms (anchor first) | factor_type (attribute) | Rule | K units |
|---|---|---|---|---|---|---|
| G01 | Table 1 (p.1, columns orientation) | none | FDM-A; Random; Margin | order-rule, credited | U1, U3 i, U6a | 2: ARC Accuracy; ARC Tokens/Seconds |
| G02-G05 | Table 2 | LLaDA; LLaDA-1.5; MMaDA-MixCoT; LLaDA-MoE | FDM (K=2); Probability (T=256); Margin (T=256); Entropy (T=256) | order-rule, credited | U6a replacement, U7 | 8 each: {GSM8K, HumanEval, Countdown, ARC} x {Accuracy, TPS} |
| G06-G09 | Table 2 | same four | FDM (K=2); FDM (K=3); FDM (K=4) | other (search width) | U6a parameter, U7 | 8 each |
| G10-G13 | Table 3 | same four | FDM-A (Ours); Probability (T=128); Margin (T=128); Entropy (T=128); EB; WINO | order-rule, credited | U3 i, U6a, U7 | 8 each |
| G14-G15 | Figure 4 | series FDM; FDM-A | K = 2 (anchor) ... 12 | other | U10, U3 stated-default (FDM-A default 2) and first-own-arm (FDM) | 2 fig-only each: GSM8K, Countdown (Accuracy) |
| G16-G17 | Figure 5 | series K = 2; K = 4 | gamma = 0.5 (anchor, setup "0.5 for FDM-A") ... | other | U10, U3 stated-default | 2 fig-only each |
| G18 | Figure 6 | none | eta1 = 0.8 (anchor, setup) ... | tokens-per-step (attribute) | U10, U3 stated-default | 4 fig-only: {GSM8K, Countdown} x {Accuracy, TPS} |
| G19 | Figure 7 | none | eta2 = 0.7 (anchor, setup) ... | other | U10, U3 stated-default | 4 fig-only |
| G20-G21 | Figure 8 (App. D) | series FDM; FDM-A | as G14-G15 | other | U10 | 2 fig-only each: HumanEval, ARC |
| G22-G23 | Figure 9 | series K = 2; K = 4 | as G16-G17 | other | U10 | 2 fig-only each |
| G24 | Figure 10 | none | as G18 | tokens-per-step | U10 | 4 fig-only |
| G25 | Figure 11 | none | as G19 | other | U10 | 4 fig-only |

Totals: **25 groups; 98 table units (2 + 32 + 32 + 32) and 32 fig-only units = 130 K units.** Anchors in
the Table 2 and 3 groups for the non-LLaDA levels are found by U3's main clause (the normalised label
"fdm(k=2)", resp. the own method FDM-A, is the same in every column group).

How the red-team's readings resolve: reading A (heuristic decoders as baselines) is excluded by U6a
("never baselines"); reading B (replacement only) misses the parameter groups U6a requires; reading C is
the only compliant reading. The anchor K = 2 follows from U2e ii and U3 first-own-arm (v0.3: "iv"), not
from the s5 analysis sentence on l.423. v0.4 shape: the figure groups G14-G25 get shape only where a
sentence of s5.2 or the caption states the trend (U10, m7); this list does not fix shape. Script de-duplication (U12) flags nothing here: the Table 1 pairs (FDM-A 86.30 against
Random 79.06 and Margin 82.55) occur in no later table.

Workload: 130 units is far above the median ceiling of 30 (s5.7); this record is a long-tail case, and
the ceiling is a median over records (G7 is a budget check, s10.4).

## 2. M12766, Muddit (method; unified; several AR baselines)

Sections read: abstract; s3 setup (p.6-7, l.416-422); Tables 1-5 (p.8-9); s3.5; Tables 6-7 (p.10);
Table 8 (p.19); Appendix D-E, Tables 9-10, Figure 12 (p.20-27).

**Focal model and configuration.** Own model: Muddit (abstract "We introduce ... Muddit"). Main-results
table: Table 1; first own arm "Muddit (512 × 512)" (U2e ii). The setup names inference defaults for it:
64 sampling steps, CFG 9.0 (text-to-image) and 1.5 (image-to-text).

**H units.** No abstract number. H-2: the abstract sentence about the paper's own model names generation
"across both text and image modalities"; text output from an image input (captioning, VQA) is
understanding under S05, so text-to-image comes first (C-F1b; the opening sentence about "unified
generation models" in general does not count). Table 1, first metric column Overall (descriptor columns
are not metrics), row Muddit (512 × 512): **H01 = 0.61**, origin F1-table. One unit.

**S14.** Table 1; own row Muddit (512 × 512); the abstract claims "competitive or superior performance
compared to significantly larger autoregressive models" (CT6), so the baseline is the first arm Table 1
labels autoregressive for its scored (image) output: **LWM (Liu et al., 2024c)**.

| G | Where | Arms (anchor first) | factor_type (attribute) | Rule | K units |
|---|---|---|---|---|---|
| G01 | Table 1 | Muddit (512 × 512); LWM; SEED-X; Chameleon (Image Gen Arch = AR) | model-class (RQ2) | U4, U5 (Show-O and Transfusion generate images by diffusion: not AR) | 1: GenEval Overall (sub-score rule) |
| G02 | Table 2 | Muddit (512×512) (U3: whitespace-free label equals the focal label); InternVL-2.0; LLaVA-Next; BLIP-2; QWEN-VL; OpenFlamingo; Flamingo; Chameleon; LWM; Show-O (256×256); Show-O (512×512); Transfusion (Text Gen Arch = AR, 11 arms) | model-class | U1 (no skipping of rows seen in Table 1), U4, U5 | 5: MS-COCO / CIDEr; VQAv2 / Acc.; MME / Acc.; GQA / Acc.; MMMU / Acc. |
| G03 | Table 3 (columns) | 0.6 (anchor); 0.2; 0.4; 0.8; 1.0 | objective (loss weight) | U3 value-identity (v0.4 wording, derivation below) | 3: GenEval; MS-COCO; VQAv2 |
| G04 | Table 4 (columns) | Joint training (anchor); T2I only; I2T only | task-or-modality-removal (RQ5) | U1 (the v0.2 "first appearance wins" clause is deleted), U3 value-identity; full-configuration gives the same arm | 3: GenEval (3 arms); MS-COCO (2 arms); VQAv2 (2 arms) |
| G05 | Table 5 | T=64 (anchor, setup "64 sampling steps"); T=8; T=16; T=24; T=32; T=40 | steps-or-nfe | U3 ii (Figure 12's "32 inference steps" is a caption for that figure only) | 3: GenEval; CIDEr; VQAv2 |
| G06 | Table 7 | Muddit (512×512); Show-O (512×512) (Xie et al., 2024) | model-class | U5: Table 7 labels Show-O "AR + Discrete Diff"; Table 2 labels its text generator AR, so it is AR for the text columns only | 3: VQAv2; MME; MMMU (all three flagged duplicate of G02 by U12) |
| G07 | Table 9 (columns) | CFG = 1.5 (anchor, setup "1.5 for image-to-text"); CFG = 1; 2; 2.5; 3 | guidance | U3 ii | 2: MS-COCO; VQAv2 |
| G08 | Figure 12 (App. E) | Muddit (only own arm, 32 steps); Qwen-2.5-VL; Show-o; BLIP-2; LLaVA-1.6 | model-class | U10, U5 (the figure's paragraph calls them "autoregressive multimodal models"); values are ratios in the text, so fig-only | 1 fig-only: latency |

**v0.4 anchor derivation for G03 and G04 (red-team audit 3, M3).** The red-team showed that v0.3's clause
(iii) ("an earlier main-results table") read strictly against G1d's single main-results table (Table 1)
fails, so that clause (iv) gives 0.2 for Table 3 and "T2I only" for Table 4. v0.4's value-identity clause
looks at every earlier results table that contains the reference arm Muddit (512 × 512) (M12766 l.528-900):
- Table 1 (l.528 ff.): GenEval Overall 0.61. Table 3 prints GenEval 58.3-61.6: the values differ by far more
  than a factor of 2, so GenEval is not a shared column.
- Table 2 (l.741 ff.): MS-COCO CIDEr 59.9 and VQAv2 Acc. 68.2 (l.889-890). Table 3's MS-COCO row prints no
  metric (a metric printed in only one of the two tables still gives a shared column) and VQAv2 is shared.
- Table 3 (l.903-929): level 0.6 prints MS-COCO 59.9 and VQAv2 68.2: equal on 2 shared columns, different on
  none. Levels 0.2 (51.4, 62.7), 0.4 (52.1, 66.2), 0.8 (58.8, 68.4) and 1.0 (59.4, 69.2) differ on both.
  **Anchor 0.6**, one reading. The 0.3 of s3.5 is the scaled model's setting (stated-default is per table).
- Table 4 (l.930-949): Joint training prints 59.9 and 68.2: equal on 2, different on none. T2I only prints
  "-" on both (not a value: no shared column, does not qualify); I2T only prints 60.1 and 69.1 (differs).
  **Anchor Joint training**, one reading; the full-configuration clause, were it reached, gives the same arm
  (the other two labels carry "only").

Not groups: Muddit (1024×1024) (differs from the anchor in resolution, data and loss weights: U6a, U6b);
Table 6 (hyperparameters), Table 8 (one model), Table 10 (no AR arm, no one-factor variant), Figures 3-11
(qualitative).

Totals: **8 groups; 21 K units recorded (20 table, 1 fig-only); 3 flagged duplicates; 18 counted.** The
red-team's range 17-21 came from the anchor of Table 2 (now U3's label rule), the 9-or-11 AR arms ("already
recorded", now removed by U1), the Table 4 anchor (U1 plus U3 iii), the Table 5 anchor (U3 ii) and Table 7
(U5 cross-table label). column_printed is no longer in the K key; "VQAv2 / Acc." is the composed leaf of
the two-level header and the key uses benchmark_id and metric_id (U9).

## 3. M09530, TrustLDM (benchmark; no AR model)

Sections read: abstract; s3 "Models and Hyperparameters" and "Factors and Variations" (p.4); Tables 1-6
and Figures 2-4 (p.4-7); Tables 7-9 (p.10); Table 10 and the captions of Tables 11-26 (appendix).

**Focal model.** Benchmark paper (U2c). LLaDA, LLaDA 1.5, LLaDA MoE and Dream are arms of the same
main-text tables (Tables 1, 3, 5, 7, 8): a tie. The abstract names no model, so the focal model is the
first model of the first main-results table: **LLaDA**. Stated defaults: "Unless otherwise specified, we
report results with a 256 generation length, 256 step size and 64 block size"; temperature 0.

**H units.** No abstract number. H-2 (harmonisation note item 4: for a study with no method of its own the
studied system stands in for the own method): Table 1; HR is the only metric; the text quotes a bound over
all models ("≤3%"), not a row, so the row is the first row, LLaDA; the first value column of the first
sub-table is Empty (C-F1d). **H01 = 3%**, Table 1(a) TrustLDM-Adv, LLaDA, Empty. One unit.

**S14.** Table 1; own row LLaDA; no AR arm; first other arm: **LLaDA 1.5**.

**RQ2.** No arm is labelled autoregressive anywhere: no RQ2 group (agreed with the red-team).

**Factor groups** (U6c: main-text tables and figures; an appendix item only for a factor absent from the
main text; anchors only where a default is stated; contexts are conditions, not second factors, U7):

| G | Where | Arms | Anchor | factor_type (attribute) | K units |
|---|---|---|---|---|---|
| G01 | Table 2 (averaged over LDMs) | Random; L2R; R2L; Entropy; Confidence; Margin | null (no default order stated) | order-rule | 12: {TrustLDM-Adv, TrustLDM-JBB} x {Empty; Suffix / Safe; Suffix / Short; Suffix / Long; Suffix+Prefix / Short; Suffix+Prefix / Long} |
| G02 | Table 4 | Random; L2R; R2L; Confidence; Margin; Entropy | null | order-rule | 6: privacy benchmark x 6 conditions |
| G03 | Table 6 | as G02 | null | order-rule | 6: fairness benchmark x 6 conditions |
| G04 | Figure 2 | block size 16; 32; 64; 128 | 64 (stated default) | block-or-parallel | 2 fig-only: (TrustLDM-Adv, HR); (TrustLDM-JBB, HR) |
| G05 | Figure 2 | generation length 128; 256; 512; 1024 | 256 | gen-length | 2 fig-only |
| G06 | Figure 3 | block size | 64 | block-or-parallel | 1 fig-only: (privacy, LR) |
| G07 | Figure 3 | generation length | 256 | gen-length | 1 fig-only |
| G08 | Figure 4 | block size | 64 | block-or-parallel | 1 fig-only: (fairness, EOD) |
| G09 | Figure 4 | generation length | 256 | gen-length | 1 fig-only |

Not groups: Tables 1, 3, 5, 7 (diffusion models compared with each other: no RQ class); Table 8 (components
of TrustLDM-Auto, an evaluation tool: U6b); Table 9 (one model across contexts); Tables 10-26 (per-model
decoding order: the factor is in G01-G03, U6c; Tables 16 and 20 are qualitative). The condition labels are
composed from the two-level header; Figure 2's legend prints the same composed names ("Suffix (Safe)" etc.).

Totals: **9 groups; 24 table units and 8 fig-only units = 32 K units.** The red-team's range 0 to about 90
came from the appendix per-model tables (U6c) and from the missing anchor rule (U3 benchmark clause).

## 4. M13864, dLLM vs AR for code-comment translation (analysis)

Sections read: abstract; s4.1-4.4 with Tables 1-2 and Figures 3-5 (p.5-7).

**Focal model.** Analysis paper (U2c). Dream-v0-Instruct-7B is an arm in Table 1, Table 2 and Figures 3,
4 and 5; DiffuCoder-7B-Instruct only in Table 1. Focal model: **Dream-v0-Instruct-7B** (v0.2's G1 gave
DiffuCoder, a model the paper does not analyse beyond Table 1). No default configuration is stated.

**H units.** No abstract number. H-2: Table 1; the text quotes "Dream-v0-Instruct-7B achieves the strongest
performance overall (BLEU: 0.215 for Russian ...": **H01 = 0.215**, Table 1, row Dream-v0-Instruct-7B,
column "BLEU / ru". One unit.

**S14.** Table 1; own row Dream-v0-Instruct-7B; analysis study with an AR-labelled arm (the caption
separates "Diffusion models and autoregressive models"; the text calls Qwen2.5-7B "the autoregressive
baseline"), so the baseline is **Qwen2.5-7B**.

| G | Where | Arms | Anchor | factor_type (attribute) | Rule | K units |
|---|---|---|---|---|---|---|
| G01 | Table 1 | Dream-v0-Instruct-7B; Dream-Coder-v0-Instruct-7B; DiffuCoder-7B-Instruct; DiffuCoder-7B-cpGRPO; LLaDa 1.5; Qwen2.5-7B | null | model-class | U4 analysis clause | 4: BLEU / ru; BLEU / en; COMET / ru; COMET / en |
| G02 | Table 2 | Dream-v0-Instruct-7B (rate=1); Dream-v0-Instruct-7B (rate=4); Qwen2.5-7B | null | model-class | U4; U11 row label = both lines | 5: the four of G01 plus Time (sec.) |
| G03 | Table 2 | Dream-v0-Instruct-7B (rate=1); Dream-v0-Instruct-7B (rate=4) | null (no default stated) | tokens-per-step | U6c | 5 |
| G04 | Figure 3 | rate 1 ... 8 | null | tokens-per-step | U10; Russian and English series are conditions | 1 fig-only: (corpus, BLEU) |
| G05 | Figure 4 | rate 1 ... 8 | null | tokens-per-step | U10 | 1 fig-only: (corpus, COMET) |
| G06 | Figure 5 | Origin; MaskGIT+; TopK Margin; Entropy | null | order-rule (attribute: the paper calls these "remasking" algorithms; under U8 they choose which masked positions to commit) | U10: data labels inside the figure are not extracted; v0.4: the x-axis categories Ru BLEU, En BLEU, Ru COMET, En COMET (l.697-700) combine a condition with a metric, and a condition never splits units in a figure | 2 fig-only: BLEU; COMET |

Totals: **6 groups; 14 table units and 4 fig-only units = 18 K units.** U12 flags the G02 contrasts whose
printed values equal G01's (Dream 0.215 / 0.328 / 0.681 / 0.826 against Qwen 0.180 / 0.193 / 0.576 on
BLEU ru, BLEU en and COMET en); COMET ru is not a duplicate because the paper prints Qwen as 0.532 in
Table 1 and 0.531 in Table 2 (two printed values, two contrasts). The red-team's "ru occurs twice" is
resolved by the composed leaves "BLEU / ru" and "COMET / ru" (U9); the label-extent case is caught by the
validator (validator-tests V26-V28) and by label-core matching (U11).

## 5. M08100, LLaDA2.1 (method; columns orientation; several AR baselines)

Sections read: abstract; s4-5 text (p.4-5, l.396-481); Table 1 (p.6); Table 2 (p.7); Tables 3-4 and
Figure 3 (p.5, p.8).

**Focal model and configuration.** The abstract names LLaDA2.0 first, but as earlier work; the first own
model is LLaDA2.1 ("we unveil LLaDA2.1", U2a). Main-results table: Table 1 (models are columns). First own
arm, left to right: **LLaDA2.1-flash (S Mode)** (U2e ii; the paper presents S and Q Mode as "two distinct
personas" and names no default).

**H units.** H-1: **892** (TPS, HumanEval+), **801** (BigCodeBench), **663** (LiveCodeBench); "100B",
"16B" and "33 rigorous benchmarks" are sizes and counts, not units (agreed with the red-team). Traces: Table
3, w/ Quant TPS cells 891.74, 801.48, 663.39 (a trace is the cell that equals the abstract number after
rounding to the abstract's printed precision, s5.2). H-2: the abstract numbers are speed only, so F1 comes
from Table 1. C-F1e: in a table whose arms are columns, the F1 rule's "row" is the arm column and its
"column" the outcome row. The text quotes no Table 1 cell, so the outcome is the first generated-sample
row, "Average" (an average over named benchmarks is a valid F1 setting, harmonisation note item 5), and the
arm is the first own column: **H04 = 72.34**, Table 1, row Average, column "LLaDA2.1-flash (S Mode) /
Score". Four units.

**S14.** Table 1; own LLaDA2.1-flash (S Mode); no CT6 claim; first other arm left to right with an Average
value: **Qwen3-30B-A3B-Inst-2507**.

| G | Where | Second factor | Arms (anchor first) | factor_type (attribute) | Rule | K units |
|---|---|---|---|---|---|---|
| G01 | Table 1 | none | LLaDA2.1-flash (S Mode); Qwen3-30B-A3B-Inst-2507; Ling-flash-2.0 | model-class | U5: the caption defines score-only columns as AR ("for AR model, we report its scores only"); LLaDA2.0-flash is diffusion | 1: Average / Score (suite rule: 33 benchmark rows and a printed Average) |
| G02 | Table 1 | none | S Mode; Q Mode (LLaDA2.1-flash) | tokens-per-step (threshold) | U6a parameter | 2: Average / Score; Average / TPF |
| G03 | Table 2 | none | LLaDA2.1-mini (S Mode) (U3 i: other own model, focal setting); Qwen3-8B (no think); Ling-mini-2.0 | model-class | U3 i, U5 | 1: Average / Score |
| G04 | Table 2 | none | S Mode; Q Mode (LLaDA2.1-mini) | tokens-per-step | U6a | 2 |
| G05-G06 | Table 3 | LLaDA2.1-flash; LLaDA2.1-mini | w/o Quant (anchor: caption "serves as the baseline"); w/ Quant | other (quantisation) | U3 ii, U7 | 9 each: TPS on HumanEval+, MBPP+, CRUXEval-O, BigCodeBench-Full, LiveCodeBench, GSM-Plus, GPQA-Diamond, IFEval, PrOntoQA (∆Score has one arm and is a difference: no unit) |
| G07-G08 | Table 4 | LLaDA2.1-flash; LLaDA2.1-mini | w/o MBE (anchor, U3 value-identity, below); w/ MBE | remasking (editing), not credited (sub-component) | U3 value-identity, U7 | 20 each: 10 benchmark rows (MMLU-Pro, TriviaQA, bbh-zh, ZebraLogic, LiveCodeBench, CRUXEval-O, BigCodeBench-Full, Spider, AIME 2025, IFEval-strict-prompt) x {Score, TPF}; 10 rows is not above the suite threshold, so the printed Average is not recorded |
| G09-G10 | Figure 3 | Mini Series; Flash Series panels | LLaDA2.1-mini (S mode), resp. -flash (S mode); LLaDA2.1-* (S w/ quant) is not an arm of an RQ2 group; AR: Ling-mini-2.0, Qwen3-8B (label-core match to "Qwen3-8B (no think)", U5, U11); Ling-flash-2.0 (Qwen3-30B-A3B does not label-core match "Qwen3-30B-A3B-Inst-2507", so it is not an arm) | model-class | U10 | 1 fig-only each: TPS over "nine benchmarks" |

v0.4 anchor derivation for G07-G08 (value-identity; reference arm per second-factor level). G07 (flash):
reference arm LLaDA2.1-flash (S Mode) of Table 1; w/o MBE equals it on MMLU-Pro 75.31 | 4.43 and TriviaQA
72.55 | 4.30 (M08100 l.521-544, l.1046-1052). G08 (mini): the level is another own model, so the reference
arm is LLaDA2.1-mini (S Mode) of Table 2; w/o MBE equals it on MMLU-Pro 63.42 | 4.22, TriviaQA 53.33 | 3.21,
bbh-zh 67.65 | 3.89, ZebraLogic 68.50 | 5.38, LiveCodeBench 28.85 | 6.42, CRUXEval-O 70.62 | 5.85 and
BigCodeBench-Full 30.18 | 7.33 (l.720-948, l.1046-1110; the rows after BigCodeBench-Full were not
compared). w/ MBE equals the S Mode score on CRUXEval-O (70.62) but differs on its TPF (5.02) and elsewhere,
so it does not qualify. v0.3 cited the flash values for both groups; the anchor is the same, the basis is now
per level. full-configuration does not apply (remasking is not a removal factor).

Not groups: LLaDA2.0 against LLaDA2.1 (two or more factors, U6a).

Totals: **10 groups; 64 table units and 2 fig-only units = 66 K units.** Without the suite rule Tables 1-2
alone would give 33 + 66 units per table (the red-team's "66 from RQ2 alone"); the suite rule records the
printed Average instead (decision row, s13 row 3). The anchor ambiguity (S or Q) is settled by U2e ii; the
"|" separators are dropped before counting columns (validator N4, tests V21-V23).

---

## 6. Summary (unchanged in counts by v0.4)

| Paper | Red-team range under v0.2 | v0.3 groups | v0.3 K units (fig-only) | H units | S14 baseline |
|---|---|---|---|---|---|
| FDM M07474 | 32, 32 or 64 units (readings A-C) plus 4-8 figure groups | 25 | 130 (32) | 1 | Probability (T=256) |
| Muddit M12766 | 17-21 units | 8 | 21 (1); 18 after U12 | 1 | LWM |
| TrustLDM M09530 | 0 to about 90 groups | 9 | 32 (8) | 1 | LLaDA 1.5 |
| M13864 | focal model in dispute; ru column undefined | 6 | 18 (4); U12 flags 3 | 1 | Qwen2.5-7B |
| LLaDA2.1 M08100 | anchor S or Q; about 66 RQ2 units | 10 | 66 (2) | 4 | Qwen3-30B-A3B-Inst-2507 |

Remaining judgement, all on attributes outside the keys: factor_type for search widths and thresholds
(FDM eta1, LLaDA2.1 modes, M13864 Figure 5), and whether a figure's paragraph labels its bars as
autoregressive (Muddit Figure 12). These enter M-class, not F1_G or F1_K.

What these examples do not show: that two extractors converge (Stage A measures it, on the 7 drawn records
for the falsifier), and the workload distribution (FDM's 130 units is one record; G7 is a budget check).

## 7. v0.4 attributes now gated (C1), as these lists give them

M-anchorG compares anchor_arm on matched groups. Expected anchors: FDM G01-G13 by focal-label or
other-own-model, G14-G25 by stated-default or first-own-arm (table above); Muddit G01-G02 focal-label, G03-G04
value-identity, G05 and G07 stated-default, G06 focal-label, G08 first-own-arm (the only own arm); TrustLDM
G01-G03 null (none), G04-G09 stated-default (benchmark clause); M13864 every group null (no default stated);
LLaDA2.1 G01-G02 focal-label, G03-G04 other-own-model, G05-G06 stated-default ("serves as the baseline"),
G07-G08 value-identity, G09 other-own-model (mini panel), G10 focal-label (flash panel). higher_is_better, held_fixed,
budget_across_arms, scoring and credited_ablation (K-attr, M-sign, M-pool) are not fixed by this file; Stage A
measures their agreement between extractors.
