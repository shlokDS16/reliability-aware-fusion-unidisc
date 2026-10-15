# Codebook ambiguities reported by the Claude census coders (2026-10-15)

Compiled by the orchestrator from the coders' final messages, verbatim in substance. Input to
adjudication and to codebook v1.2. Coder A's reports for ranks 121-176 are appended when they arrive.

## Coder B (Claude Opus)

### Ranks 92-128
1. Rank 116 (2501.06848): abstract names text-to-image before text; F1 taken literally from the
   Stable Diffusion image results although eligibility rests on the text-diffusion experiments
   (SSD-LM, MDLM). Codebook silent on whether F1 must come from the in-scope (text) modality.
2. Ranks 123 (EO-1, flow-matching robot actions) and 128 (synthetic ScanAndAdd token task):
   borderline eligible. EO-1 qualifies under I1(b) only if robot actions are "another modality",
   else X1; 128 has no natural text or code.
3. Ranks 96, 109: step count changes as a side effect of generation length or thresholds; F4 Yes
   under A-8 (table with NFE/steps). Rank 98 (commit threshold plotted against throughput, not
   steps): F4 No. Codebook does not separate adaptive from set step counts.
4. Ranks 111 (EntRGi), 125 (DiffLM): M added where the headline is Top@1 = best reward of 4
   samples, or generated outputs are filtered for validity. Whether best-of-N metrics or validity
   rejection count as M is unclear.
5. Ranks 107, 110: temperature 1.0 stated (107) or low-confidence remasking named without a
   temperature (110), truncation/remasking not both specified: NS rather than U or S. A-3 does
   not say how much must be stated for U.

### Ranks 129-176
1. A-2 main task (145, 153, 159): abstract names a non-text task first (images 145, synthetic toy
   153, molecules 159); for 145 the image result is a figure only, so fell back to the first
   results table (Text8).
2. Multi-task models with a speech or image diffusion part (150, 154, 172): took the
   diffusion-produced output or the task named first; alternative in notes.
3. Eligible versus X7/X0 (157 hallucination detector, 162 likelihood-based metric, 169
   diffusion-style operator denoiser on an AR model, 170 representation probe): coded eligible,
   alternative in notes.
4. Steps-per-token sweeps (152 block sizes across separately trained models; 166 NFE rises with
   guidance compute, F6 Co-varied; 176 two settings static greedy vs dynamic T=1.0, F4 Partial,
   F5 Co-varied).
5. Argmax stated only at method level or outside the headline section (129 "greedy unmasking",
   139, 154 A under A-3(b)); 132 NS (headline matches the 2D-beam-search row of an ablation but
   the main text does not state the rule); 163 grammar-constrained rejection and 164 P2-self
   planning have no F2 letter, recorded in F2_detail.
- Missing table cells in extracted text: rank 161 used Table 3 (Sudoku) instead of Table 2;
  rank 166 used ablation Table 2 "Evenly" column.
- Rank 151 (Twins) X1: diffusion generates class-conditional ImageNet only.

### Gap-fill (ranks 19, 79)
1. Rank 19 F1: no abstract number; Table 1 is the paper's attack on unmodified models; took the
   first row of the proposed alignment method (RA) in Table 2.
2. Rank 19 F2: T 0.7 and random remasking stated only for training rollouts (App. D.4.2);
   evaluation decoding unstated: NS.
3. Rank 79 eligibility: main experiments on AR Janus-Pro; I1(b) only via Lumina-DiMOO and BAGEL
   applications; stricter reading X0.
4. Rank 79 F1: literal A-2 gives the AR model (Table 2 WISE); diffusion alternative Lumina-DiMOO
   GenEval (Table 4a) in notes.
5. Rank 79 F2: CFG 5 and T 1.0 stated for RL rollouts only: NS rather than G+U. Rule used:
   training-only sampler settings are not the evaluation value rule under A-3.

## Coder A (Claude Sonnet, blind)

### Ranks 1-40
Conventions: eligible "Y"/"NA"; F1 = NA rows have F2-F6 NA; missing Table 1 cells (34, 36, 37,
40) taken from prose or abstract.
1. Ranks 27, 28, 38 (Sangam, CaDDTree, OLED-MoE): serving, lossless speculative decoding, expert
   offloading; speed only; coded eligible with F1 = NA; X7 the alternative.
2. Rank 12 (MaskGIT sampler paper): abstract names images first (MAGE FID, Table 1); took F1 from
   the OpenWebText Gen. PPL vs entropy figures (no numeric headline).
3. Rank 34 (JoT): method says argmax, Table 1 caption says Dream at T = 0.1; coded A+T. Rank 9:
   greedy stated only in preliminaries (A-3(b) borderline).
4. A-8 sweeps on another task or axis: ranks 7, 16, 39 (other task); 22, 17 (particle count, not
   steps); coded F4 Yes with a note.
5. Ranks 2 (EasyGen: text from an AR LLM, images from diffusion) and 35 (DiffuPlex, full-duplex
   speech) eligible via I1(b), borderline.

### Ranks 41-80
- F1 = NA: 52 (membership inference), 56 (latency profiling). F1 = QL: 71 (Plaid; F2 T, score
  temperature 0.9).
1. Rank 42 (2502.00234): abstract names GSM8K first, Table 1 is RADD text generation; coded GSM8K
   (Table 2, T = 0.5).
2. Rank 44 (DiffuCOMET): "# Clusters" diversity metric not in the F3 list; coded F3 Yes, flagged.
3. Ranks 48 (SMC particle resampling, coded M), 57 (relevance-score position selection, coded S):
   no matching F2 letter.
4. Rank 60 (2503.09573): NFE 1K/2K only because sample length changes; F4 Partial (literal A-8);
   a step-sweep reading gives No.
5. Rank 79 (PairUni): main experiments AR Janus-Pro; eligibility via Lumina-DiMOO Table 4a; F1
   taken literally from Table 1 (AR model).
- exclusion_code is "" on eligible rows.

### Ranks 81-120
1. Rank 116 (FK steering): coded the text task (MDLM Table 4, Gen PPL 49.0) rather than literal
   A-2 (GenEval, SD v2.1, Table 1).
2. Ranks 114 (Orthus), 119 (Emu3.5), 120 (LatentLM): AR unified models with a diffusion head or
   DiDA; eligible under I1(b); text output AR. Ranks 83 (watermark attack), 85 (diffusion drafter
   for speculative decoding), 104 (attention analysis) borderline (X7 or X2).
3. A-8 for a multi-benchmark LM: rank 82 (Dream 7B) sweep only on Countdown, F1 MMLU (probably
   likelihood-scored, not stated); F4 No.
4. Threshold or hyperparameter changing NFE (84, 86, 89, 96, 97, 98, 109): F4 Yes. F5: a blanket
   "all experiments greedy / zero temperature" sentence = Stated (84, 86, 96, 97); a method-level
   definition alone = Not stated (98, 109).
5. U versus NS: 112 (MDLM) U under A-3(b); 93, 108 (tau-leaping) NS; 107 (T 1.0, no truncation
   statement) NS; 92 (tuned temperatures, values not stated) NS.
- Rank 99 (Coffee): F1 Dyck-repair column of Table 1; F2 G; F5, F6 "Co-varied" (selection
  inside each denoising budget). Rank 100: F1_value "curves only".

## Process notes
- Coder B is Codex for ranks 1-91 (86 rows; 19 and 79 failed, 23, 33, 90 no text) and Claude
  Opus from rank 92 plus ranks 19 and 79 (D0015). Coder B's eligible count reached 151 over
  ranks 1-176; the sample is ranks 1-176.
- Blindness incident D0019: coder A batch 1-40 ran coder B's append script once; B's scratch rows
  for 92-128 were in the shared scratchpad until 09:00.
- Value vocabularies differ across files ("Y"/"yes", "" / "NA" exclusion codes, "Co-varied");
  `analysis/census/agreement_random.py` normalises eligibility; F5/F6 categories need a mapping.
