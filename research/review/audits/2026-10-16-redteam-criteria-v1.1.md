```yaml
agent: red-team
date: 2026-10-16
brief: Attack full-text screening criteria v1.1 (Paper 1, PRISMA review) before adoption as D0032 option (b)
sources_examined:
  - research/CONTRACT.md
  - research/review/screening/criteria-v1.1.md (all 363 lines)
  - research/review/screening/v2/screening-ambiguities.md (all)
  - research/review/screening/v2/SCREENER-BRIEF.md (all)
  - research/review/screening/criteria-v1.md (all)
  - research/review/protocol.md s1, s2, s4, s5, s10 (D0020, D0026, D0027 entries)
  - research/review/coverage/census-codebook-v1.2.md B-1 to B-8
  - research/ledgers/decisions.jsonl D0020, D0026-D0031
  - research/review/screening/v2/batch-0*.jsonl, screener-A/B-batch-0*.jsonl (titles, abstracts, codes; read by script)
  - research/review/screening/v2/rescue/screener-R-rescue-0*.jsonl (decision counts only)
  - research/review/screening/v2/subscription-queue.jsonl, title-resolved-queue.jsonl (line counts only)
coverage: >
  Every rule R1-R14, section 2 (code order), section 3, the section 4 brief, section 5 table, 5.1, 5.2
  and the section 6 amendment text. Record-level checks are title/abstract level (E1) from the v2
  batch files; no full text was read. Scratch scripts (not committed, scratchpad rt_check*.py) were
  used for counts; the exact regexes are given where a number is used. NOT covered: census-codebook
  B-9 to B-28, protocol s3, s6-s9, criteria v1 round-1 records, the rescue records' titles.
claims:
  - statement: "Two independent screeners can apply each of R1-R14 to a full text without discussion"
    status: contradicted
    evidence: "criteria-v1.1.md R4 l.67 vs R6 l.81; R4 l.67 vs R5 l.74; R13 l.134 vs R14 l.141; R9 l.102 vs R10/R9 examples l.104, l.115"
    level: E1
    confidence: 0.85
  - statement: "Eligibility I1-I4 is unchanged by v1.1 (amendment text l.322-323)"
    status: contradicted
    evidence: "Notation l.31-33 and R4 l.67 (masked-generative and continuous flow components for I1(a)); R7 l.88 with R8(b) l.95 (non-text outputs admitted on naming); R10 b3 l.112; R11 l.120"
    level: E1
    confidence: 0.8
  - statement: "The 5.2 list (19 records) is a reproducible, complete set of both-excluded records v1.1 might pass"
    status: contradicted
    evidence: "l.307 (title reading; 307 from an uncommitted script); recount 282 or 315 depending on regex; v2 batch files list both-excluded titles that v1.1 rules plausibly flip and that are absent (finding M12)"
    level: E1
    confidence: 0.85
  - statement: "Screeners using the section 4 brief are blind to title/abstract decisions"
    status: contradicted
    evidence: "brief l.216-218 sends screeners to criteria-v1.1.md, which names 93 distinct record ids and states screener A/B title/abstract codes for many of them (e.g. l.48, l.97, l.122, l.282, l.291)"
    level: E1
    confidence: 0.95
competing_explanations:
  - "If full-text agreement under v1.1 is high, the cheapest explanation is shared priors of two Claude-family screeners plus the per-record 'expected' outcomes they both read in the criteria file, not rule clarity."
  - "If the 5.2 box yields few includes, the cheapest explanation is that the rule author picked the 19 by title, so the box measures the author's title intuition, not the loss caused by the rule change."
unknowns:
  - "How many passed records fall under each contested rule (R6 continuous/latent, R7/R8(b) bio 'language models', R11 motion/pose, R12 VLA) at full text."
  - "Whether records included through the 5.2 box enter the synthesis."
  - "Which criteria the 170 subscription-queue records will be screened under at title/abstract."
next_test: {hypothesis: "v1.1 rules are applied identically by two blind screeners", intervention: "blind dual pilot on a stratified sample of passed records drawn from the contested classes, with the criteria file stripped of record ids", primary_metric: "code-level agreement per rule", falsifier: "disagreements concentrated in the rule pairs named in F1, M1, M3, M4, M5", gpu_hours: 0}
```

# Red-team audit of full-text screening criteria v1.1

Severity counts: **fatal 2, major 15, minor 11.** Fatal findings block the gate until the
orchestrator records a resolution in the decision ledger.

Note on fixes: the red-team role does not propose fixes; the orchestrator's brief asks for a minimal
fix per finding, so each finding ends with a one-line "Minimal fix" and nothing more.

Line numbers refer to `research/review/screening/criteria-v1.1.md` as of 2026-10-16.

---

## Fatal

### F1. R4 and R6 contradict each other on continuous and latent diffusion text models; the brief repeats the exclusion
- **Where:** R4 l.67 ("Gaussian noise on embeddings, the simplex or latents ... Latent diffusion whose latents are decoded to text ... counts and is I1(a)"); R6 l.81 ("The diffusion component generates text if the variable it denoises or predicts is a sequence of tokens ... Not text: ... embeddings or denoised hidden states"); brief l.232-233 ("not labels, spans, tags, embeddings, pixels").
- **Problem:** Embedding-space diffusion (Diffusion-LM type, rounding from denoised embeddings) and latent diffusion decoded to text denoise exactly the variable R6 says is not text. A screener applying R6 literally excludes R4's own positive example M07984 (LaDi-RL) and the whole continuous-embedding and continuous-latent classes that protocol s5 lists as state-space categories for RQ1. The brief contains only the R6 wording, so a screener who follows the brief has no route to the R4 clause. Two careful screeners will split by which rule they read as governing.
- **Forces rejection of the claim "every rule is decidable":** any pair of screeners giving different decisions on a continuous or latent text-diffusion paper.
- **Minimal fix:** in R6 and the brief, test what the diffusion component's output is decoded to, not the variable it denoises.

### F2. R7(b) via R8(b) admits non-text outputs on the authors' naming, contradicting I1, census B-7 and R10's own principle
- **Where:** R7 l.88 ("included only if (a) ... or (b) R8(b) holds"); R8(b) l.95 ("the title, or the abstract's statement ..., names language models, LLMs, text generation or code generation as the object of the result"); R7 positive M12848 l.89; R10 l.113 ("How the paper names itself ... does not count").
- **Problem:** A SMILES, protein, DNA or RNA generator called a "diffusion language model" or "protein language model" satisfies R8(b) on its title and is then included by R7(b), although its output is not natural-language text (protocol I1; R7's own first sentence; census B-7). The amendment text (l.322-323) says I1 is unchanged, so this widening is undisclosed. The test also turns on author wording, which R10 forbids for unified models: text-side records are admitted on naming, multimodal ones are not. Whether "protein language model" counts as "language models" is itself undecidable between screeners.
- **Evidence (E1, titles):** passed and therefore in the full-text set: M16270 "MMCP-GEN: A Modality-Extensible Diffusion Language Model for Conditional Protein Sequence Generation". Both-excluded, not in 5.2, plausibly flipped by R7(b): M17218 ProtoBind-Diff ("A Structure-Free Diffusion Language Model ... Ligand Design"), M17195 Prot2RNA ("A Diffusion Language Model for ... mRNA"), M17462 RegJEDI ("Joint-Embedding Diffusion Language Model for Regulatory DNA"), M16164 MeMDLM, M14933, M19299, M14419.
- **Forces rejection:** one included record whose only diffusion output is a biological or chemical sequence.
- **Minimal fix:** R8(b) must name natural-language or code data; delete R7(b).

---

## Major

### M1. R4 and R5 give different codes to papers that run DLM baselines themselves
- **Where:** R4 l.67 ("If no such component exists in the paper's own method **or its own experiments**, exclude X0"); R5 l.74 ("Exclude X0 if diffusion models appear only as baselines").
- **Problem:** A DLM baseline that the authors ran is in "its own experiments", so R4 says there is a diffusion component (not X0). The paper then fails I1(a) ("of the paper's own method"), and R9 (i) fails because the AR model outputs text, which gives X1. R5 gives X0 with `RQ2-context`. The include/exclude decision is the same, but the code and the RQ2-context tag differ by reading. Named case: M12594 pcLLM.
- **Minimal fix:** in R4, change "or its own experiments" to "or experiments on the paper's own method".

### M2. R4 and the notation widen I1(a) to masked-generative, MLM and continuous-flow text models while claiming I1 is unchanged
- **Where:** Notation l.31-33 ("a diffusion, masked-generative or discrete-flow component generates text"); R4 l.67 ("learned reverse of a stated corruption process (masking ...)", "masked-generative iterative decoding", "continuous flow matching (including rectified flow)"); R13(c) l.134; amendment l.322-328.
- **Problem:** Protocol I1(a) says "a diffusion model whose output includes natural-language text". "Masked-generative" appears only in the I1(b) clause. R4's test has no multi-level noise schedule and no iterative generation requirement for masking, so a BERT-style MLM objective is literally "a learned reverse of masking". CMLM, Mask-Predict and other non-autoregressive iterative-refinement text models also pass. R13(c) ("compares a diffusion-pretrained text backbone with a non-diffusion one") then admits MLM-versus-causal comparisons. Screeners will split on MLM and non-autoregressive translation papers. This is an eligibility change under an amendment that says eligibility is unchanged.
- **Minimal fix:** for I1(a), require training over a range of corruption levels and multi-step generation, and state the masked-generative and continuous-flow inclusion in the amendment.

### M3. R6 does not say whether "text" is the model's output vocabulary or the task's output format
- **Where:** R6 l.81 ("open vocabulary ... Not text: ... tags or labels from a fixed set ..., class names, success, failure or progress tokens"); R14 positive M15731 l.142 (a DLM among six models on veterinary ICD-11 coding); R12 l.127; dWorldEval l.83.
- **Problem:** A general DLM (LLaDA-type) that answers a classification or coding task emits open-vocabulary tokens whose content is a label from a fixed set. On the vocabulary reading this is text; on the task reading it is a label. M15731 (ICD-11 codes) is the positive example of R14 but is a label under R6's list. dWorldEval's progress tokens raise the same question in R12. Extractive outputs (aspect or entity terms copied from the input) are a third undecided case: "entity strings" are text (l.81) but "indices ... of spans" are not.
- **Minimal fix:** state that the test is the vocabulary of the denoised variable, and correct the examples to match.

### M4. R9's literal test contradicts the X2 examples for LLM-to-diffusion pipelines
- **Where:** R9 l.102 ("X2 if (i) no component of the paper's model outputs text ... Otherwise exclude X1"); R9 negative M15918 l.104 (LLM-written prompts to an image diffusion model, "expected X2"); R10 l.113 ("otherwise R9 (usually X2)") and negative M17285 l.115 (VLM to DiT through skill calls, "expected X2"); R1 l.48.
- **Problem:** In each of these pipelines an LLM or VLM component outputs text (prompts, instructions). Applied literally, R9 (i) fails and the code is X1, not X2. Screeners following the text get X1; screeners following the examples get X2. The rescue screener's practice ("LLM plus separate image generator coded X2") will be repeated by some screeners and not by others.
- **Minimal fix:** define whether "the paper's model" in R9 (i) includes upstream text-writing components, and make the examples agree.

### M5. R13 and R14 conflict on fine-tuning an existing diffusion-pretrained model
- **Where:** R13 l.134 ("Exclude X0 if the paper only fine-tunes, as a non-generative model, a backbone whose diffusion pretraining was done elsewhere"); R14(a) l.141 ("Include if ... the paper trains, fine-tunes or modifies the model (weights ...)").
- **Problem:** A paper that fine-tunes LLaDA or Dream as an embedding model or classifier is X0 under R13 and include under R14(a). X0 comes earlier in the order, but R14(a) is an include rule with no exception. Labelling a diffusion-pretrained backbone X0 ("no diffusion component") also contradicts the plain meaning of the code. pplx-embed (M08140/M16168) sits on this boundary.
- **Minimal fix:** R14(a) should state "except non-generative fine-tuning (R13)".

### M6. R10(b3) widens and narrows D0020 at the same time; (b1) is undecidable for frozen backbones
- **Where:** R10 l.110-116; D0020 (protocol s10 l.82-84: "one model (shared weights or one jointly trained system), not a pipeline of separately trained models"); census B-4 ("components trained or fine-tuned jointly and presented as one model").
- **Widening:** a frozen VLM plus a frozen or separately pretrained diffusion model joined by a connector trained in the paper is, literally, "a pipeline of separately trained models" with a trained interface. b3 admits it. The justification (l.116: "the 'decoupled' arm of RQ5's shared-versus-decoupled contrasts") misreads RQ5: protocol s1 means within-paper ablations, not separate studies of decoupled systems.
- **Narrowing:** a system trained end to end in which the generator is conditioned on text the understanding model decodes (for example, RL through a generated prompt) is "one jointly trained system" under D0020 but a "pipeline" under b3.
- **(b1) undecidable:** "shows the system producing text ... in at least one table, figure or worked example". Frozen-VLM papers often reprint the backbone's understanding scores from its own paper. Whether a reprinted number "shows" anything will split screeners.
- **Minimal fix:** quote D0020 verbatim as the test and add b3 only as a disclosed amendment; define "shows" as output produced in this paper's experiments.

### M7. R11's closed modality list is a post hoc narrowing of B-4 that removes motion and pose from RQ5, and its boundary cannot be decided
- **Where:** R11 l.120-123; census B-4 ("another perceptual signal such as 3D shape"); D0020 ("or 3D"); amendment l.336-338.
- **Post hoc:** B-4, which D0020 made protocol-level, uses an open category ("perceptual signal"). D0020 says "3D" without restriction. R11 closes the list after title/abstract screening included motion and pose records (M12859 PoseDLLM included by A; M19014, M15992, M15235, M15236 marked unclear). The stated reason (l.123: it "would add a separate literature with its own benchmarks to RQ5") concerns workload, not construct validity. A referee will read this as shrinking the RQ5 evidence base after seeing it. About 16 passed records mention motion, pose, gesture, humanoid or dance in title or abstract (regex `\b(motion|pose|gesture|humanoid|dance)\b`, E1, upper bound).
- **Boundary:** "mesh, point cloud ... 3D Gaussians" count, but human motion and pose do not. SMPL body models are meshes, and motion is often output as mesh sequences or 3D joint point sets. Talking-head video counts while facial-animation parameters do not, even when the paper renders both. Screeners cannot decide from the method section alone.
- **Minimal fix:** keep D0020's "3D" unqualified, or declare the closure as an amendment with its reason and its count of affected records.

### M8. Checking X2 before X1, with one code per record, hides two scope boundaries the review must report
- **Where:** section 2 l.161-162, l.167; R9 l.105; change 4 l.284.
- **Problem:** With X2 first, X2 holds text-to-image, TTS and NLP label or span diffusion (NER, ABSA, sentiment; R6 negatives M13881, M14484) together. X1 holds unconditional non-text diffusion, the D0020 class (autoregressive text plus a non-text diffusion output) and, by the literal R9 (M4), LLM-to-diffusion pipelines. The two boundaries a referee will probe can no longer be counted from the flow diagram: NLP structured-prediction diffusion, which the strings target on purpose (protocol s10 l.127-128: "whether they meet I1 ... is decided at full text"), and "unified-looking" pipelines (the RQ5 boundary). The order also departs from census B-8 (X1 before X2), which D0020 binds to future full-corpus coding, so the same record can carry X1 in the census and X2 in screening within one paper.
- **Defensibility of the order itself:** X2-first is logically defensible (X1 contains X2 after D0020). The information loss and the mismatch with B-8 are the problem.
- **Minimal fix:** record a secondary sub-reason field (NLP-label, pipeline, AR-text plus non-text) and align census B-8.

### M9. With "no unclear", doubt defaults to exclusion and never reaches the human
- **Where:** section 2 l.169 ("the decision follows the rule's default (the 'otherwise' branch)"); brief l.223.
- **Problem:** The "otherwise" branches of R4, R7, R8, R9, R10, R11 and R12 are exclusions. If both screeners are in doubt they both exclude, there is no disagreement, and the record never reaches the human author (protocol s4 step 4). This reverses the title/abstract convention (D0030) at the stage where the review's final set is decided, and it is invisible in the agreement statistics. Rules without an "otherwise" branch (R3, R6, R13, R14 between include and X7) have no default at all.
- **Minimal fix:** a `doubt: true` field that routes the record to the human whatever the decision.

### M10. Protocol s4 steps 3 and 4 at full text are missing
- **Where:** protocol s4 step 5 ("Full-text screening repeats steps 2 to 4"); step 3 (human screens a random 15 percent, at least 100 records, Cohen's kappa for each screener against the human, prompt revised and stage rerun if kappa is below 0.70). criteria-v1.1 section 4 and proposed D0032 item (5) mention neither the human validation sample nor full-text agreement reporting.
- **Minimal fix:** add the step 3 sample, the kappa threshold and the agreement report to D0032.

### M11. The brief breaks its own blinding
- **Where:** brief l.216-218 ("do not open ... title/abstract decisions ... Use only research/review/screening/criteria-v1.1.md"). The criteria file names 93 distinct record ids (`grep -o "M[0-9]\{5\}" | sort -u`). For many it states the expected full-text outcome. For many it states the title/abstract codes: l.48 "A X3 by title, B unclear", "A X1 on the title, B unclear"; l.97 "both screeners X1"; l.104 "both X1 at title/abstract"; l.122 "both screeners X1"; l.282, l.291 A and B codes; l.306-309 the 19 candidates and their T/A status.
- **Problem:** Agreement on these records is not blind. The 5.2 box is reviewed by screeners who know that both earlier screeners excluded the records and why the rule author expects them to flip.
- **Cheapest alternative explanation for high agreement on named records:** both screeners copied the stated expectation.
- **Minimal fix:** give screeners a copy of sections 1-4 with record ids and expected outcomes removed.

### M12. The 5.2 candidate list is neither rule-based nor reproducible, and it is incomplete by v1.1's own rules
- **Where:** l.20-21 ("scratch script, not committed"), l.305-311.
- **Not reproducible:** the 12 change-5 records were "my reading of titles" from 307. The 307 cannot be recomputed: on the same 999 both-excluded records, `(discrete|masked)[ -]?(diffusion|flow)` gives 282 and `(discrete|masked)[ -](diffusion|flow)|discrete flow|flow matching|absorbing` gives 315. The project's hard rule (CLAUDE.md: "No number in any document unless it is in a runs/<exp-id>/ directory") is not met. The proposer of the rules also chose the test set.
- **Incomplete (title-level, E1; both-excluded, absent from 5.2):** M16907 "Parallel Language Models via Variational Decoding" (X0/X0; title names language models, so R8(b) applies); M17608 "Return-Weighted ELBO Fine-Tuning Degrades Masked Diffusion Planners", M09922 "Flow Reasoning Models", M14963 "Gentoo: Draft Continuously, Decode Discretely" (X1/X1, generic, R7/R8); M08480 EndoCoT (X2/X2), M13010 CITA-Net ("captioning" plus diffusion editing, X1/X2), M14003 "DLM-3D: Diffusion Language Models for 3D Point Clouds Generation" (X1/X1; point cloud is an R11 modality); the bio "diffusion language model" titles of F2. Changes 8 (entity strings, OCR and captions are now text) and 9 (R13) are declared "No" (l.288-289) without any check.
- **Frame too narrow:** the frame is the 999 dual-screened both-excluded records only. The 4,073 single-screener rescue exclusions (Haiku, D0029; decision counts from screener-R-rescue-0*.jsonl) faced the same narrower rules and are not considered.
- **A referee would demand** a list defined by a stated, committed query over all excluded records, or a random sample with an estimate. A list chosen by title reading would not be accepted.
- **Minimal fix:** a committed script with a declared query over all title/abstract exclusions (dual and rescue), or a seeded random sample, and report its count.

### M13. Option (b) re-opens hand-picked exclusions; R5's RQ2-context brings excluded records into synthesis
- **Where:** 5.1 l.299-303; R5 l.74, l.77; brief l.251.
- **Problem:** Option (b) gives 19 title/abstract exclusions a second, full-text chance. They were chosen because the author expected them to flip, and section 5.1 does not say whether records included through the box enter the synthesis. If they do, this is a selective re-open of title/abstract decisions in the inclusive direction only. If they do not, the box measures nothing usable. The `RQ2-context` tag puts excluded, un-appraised records into the RQ2 discussion, against protocol s1 ("studies reporting a comparison", meaning included studies) and s6 (appraisal of every included study). The tag is available only on the R5 path.
- **Minimal fix:** state that box includes enter the review with appraisal, or that they are reported only; drop the RQ2-context use in synthesis.

### M14. The criteria were written with knowledge of the title/abstract decisions, and the amendment misstates the timing
- **Where:** header l.14 ("titles, abstracts and screener A/B/V/R decisions of every record id named"); per-record "expected" outcomes throughout section 1; amendment l.322 ("before the freeze rule is applied"); protocol header l.10-11 ("frozen ... before any screening decision is recorded"); `git tag -l` returns no `protocol-v1` tag.
- **Problem:** Title/abstract decisions on 1,953 records are recorded, so the freeze point in the protocol has already passed. The rules for R10, R11 and R12 were fitted to named records whose decisions the author had seen. A PRISMA-literate referee will treat R11 and R10 b1/b3 as post hoc eligibility changes, not readings.
- **Minimal fix:** state the timing in the amendment ("after title/abstract decisions were seen, before any full text") and list the rules that change eligibility.

### M15. One unverified quote cannot evidence multi-condition decisions; RQ tags and `mm` carry no evidence
- **Where:** section 3 l.192-194; brief l.255.
- **Problem:** The evidence requirement is one quote of at most 40 words. An I1(b) include needs b1, b2 and b3 together, and R8(a) needs a table location; one quote cannot evidence all of these. No step checks that the quote exists in the file, so an LLM screener can paraphrase or invent a "verbatim" quote and the error goes undetected. RQ tags and `mm` carry no evidence, although they route records to RQ2-RQ5 synthesis.
- **Minimal fix:** one quote per satisfied condition, and a string-match check of quotes against the file.

---

## Minor

- **m1. X6 inside the exclusion order (l.157).** PRISMA 2020 reports "reports not retrieved" in its own box before eligibility assessment. Counting X6 among eligibility exclusions mixes retrieval with eligibility. Fix: report X6 in the retrieval box.
- **m2. X3 before relevance codes (l.158).** Off-topic surveys (for example both-excluded M04752 "A Survey on LLM-based News Recommender Systems", M17821) land on the X3 "positioning" list. Fix: send X3 to the positioning list only if the survey covers DLMs or unified models.
- **m3. X5 and R3 (l.60, l.156, l.226).** X5 depends on another record's final decision, so its position at 2 in the order is nominal. Disagreement on `dup_of` is not handled. The retention rule ("peer-reviewed version if retrievable") conflicts with section 3, where the latest arXiv version is the one screened. PRISMA 2020 links reports to studies rather than excluding them. Fix: one sentence each.
- **m4. X8 date (l.155, brief l.225).** The first-version date is not in the screened file, which is the latest version. "Search date" is undefined across several dates (free sources 2026-10-15, Scopus 2026-10-16, other databases later). Fix: set by script from metadata, with per-source search dates.
- **m5. R1/X3 (l.46).** A survey that "proposes a taxonomy" or "framework" can be called new method or theory. Fix: say whether a taxonomy counts.
- **m6. `mm` flag (l.252-253).** Undefined for I1(a) models that take motion, pose or action inputs: they are not "text only", and R11 says these are not modalities. Fix: add a third value or define the case.
- **m7. `rule` is single-valued (l.264).** Decisions chain rules (R12 to R10 to R11 to R9). Fix: allow a list.
- **m8. Brief omissions.** No instruction on the doubt default (l.169); no R3 retention rule; no R5 include branch (drafters trained with a masked objective); no screener model version string (protocol s4: "version recorded"). Fix: add four lines.
- **m9. Scope (l.25-27).** The 170 records in `subscription-queue.jsonl` still need title/abstract screening, and the scope does not say whether criteria v1 or v1.1 applies to them. This creates an asymmetry across parts of the corpus. Fix: state it.
- **m10. Reversal clause of the proposed D0032 (l.360).** It names only motion and pose. It omits the other contested readings (continuous/latent R6, bio "language models", VLA, NLP labels, frozen-backbone b3). Fix: list them.
- **m11. Unverifiable counts in the disclosure text (l.45: "about 20 records"; A batch 1 "about 40").** These rest on screener self-reports with no ids. Fix: mark them as screener statements without ids.

Totals: fatal 2, major 15, minor 11.

---

## Answers to the six questions

1. **Decidability and conflicts.** Rule pairs in conflict: R4/R6 (F1), R4/R5 (M1), R13/R14 (M5), R9 against its own and R10's examples (M4), R7/R8(b) against R10's naming principle (F2), R3 against section 3 (m3). Undecidable tests: R6 vocabulary versus task output (M3), R10 b1 "shows" (M6), R11 mesh versus motion (M7), R8(b) "protein language model" (F2), R4 MLM (M2).
2. **Code order.** X0 and X2-before-X1 are logically defensible. A referee will object to X6 as an eligibility exclusion (m1) and to the loss of the NLP-label and pipeline counts (M8). X2-first hides both of these and departs from census B-8.
3. **I1(b) and R11.** D0020 is not respected verbatim. b3 widens it (frozen backbones), b3 narrows it (jointly trained text interfaces), and R11 narrows B-4's open "perceptual signal". The R11 reason is workload, and the rule was written after seeing the records. A referee would call it post hoc (M6, M7, M14).
4. **5.2 list.** Not reproducible, not complete by v1.1's own rules, and the frame leaves out the rescue exclusions. A referee would demand a rule-based or random list (M12).
5. **Re-opening and asymmetry.** Option (b) is a selective, inclusive-only re-open of title/abstract decisions (M13). Doubt defaults to exclusion at full text (M9). Naming counts on the text side but not on the multimodal side (F2). RQ2-context brings excluded records into synthesis (M13).
6. **Brief.** The row format is complete in fields. It breaks blinding (M11), repeats the F1 error, has under-specified evidence (M15), and has omissions (m6-m8).

## Result that would force rejection of "v1.1 is ready for full-text screening"
Run a blind dual pilot with the record-id-free criteria on passed records from the contested classes:
continuous or latent text diffusion, bio "diffusion language models", frozen-VLM decoders,
motion/pose, VLA, NLP-label diffusion, and DLM-as-baseline. Any code-level disagreement traced to
the rule pairs above, or any include of a record whose only diffusion output is a non-text
sequence, rejects the claim.
