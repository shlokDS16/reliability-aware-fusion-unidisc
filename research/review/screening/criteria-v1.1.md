# Full-text screening criteria v1.1 (Paper 1; written before any full text is screened)

```yaml
agent: dlm-expert
date: 2026-10-15
brief: full-text screening criteria v1.1 settling every title/abstract ambiguity class (D0030)
sources_examined:
  - research/review/screening/v2/screening-ambiguities.md (all sections)
  - research/review/protocol.md (s1 RQ1-RQ6, s2 I1-I4 and X1-X8, s4, s5, s10 amendments D0020, D0026, D0027)
  - research/review/screening/v2/SCREENER-BRIEF.md; research/review/screening/criteria-v1.md
  - research/ledgers/decisions.jsonl rows D0020, D0026-D0031
  - research/review/coverage/census-codebook-v1.2.md B-1 to B-9 (eligibility rulings used in the census)
  - research/expert/dlm-expert-kb.md A.7, C.8
  - titles, abstracts and screener A/B/V/R decisions of every record id named in the ambiguity file
    (batch-0*.jsonl, rescue/, validation-autoexcl-2026-10-15.jsonl, screener-*.jsonl)
coverage: >
  No full text was read. Every example below is chosen from the title and abstract (E1); the
  "expected" outcome says what the rule gives if the full text confirms what the abstract suggests.
  It is not a decision on that record. Re-open counts in section 5 come from a script over the
  1,953 dual-screened records (scratch script, not committed); the per-record readings in 5.2 are
  title-level (E1).
status: draft for gate-auditor / red-team; not frozen; protocol.md, ledgers and screening files untouched
```

Scope. These criteria govern full-text screening of every record that passed title and abstract
screening (round 1 records that passed, the 954 round-2 records that pass under D0030, and rescue
positives). They replace criteria v1 for this stage only. Title and abstract decisions stand
(D0030). Census codebook v1.2 stays the census coding document; where this file departs from it,
section 5 says so.

Notation. "Text" means natural-language text or code as defined in R6. "DLM" means a diffusion
language model: a model in which a diffusion, masked-generative or discrete-flow component
generates text. "Paper's own method" means the model, algorithm or analysis the paper contributes,
with its ablations, not its baselines.

---

## 1. One rule per ambiguity class

Each rule is a short test. A screener applies it to the full text and records the rule number.
Rules feed the code order of section 2: a rule that ends in "exclude Xn" gives the code only if no
earlier code in that order applies.

### R1. Records decided at title/abstract on the title alone, or on a truncated abstract
- **Raised in:** V practice; A batch 1 item 3; A batch 2 item 5; A batch 4 item 5; rescue batches 1-2; disclosure in A batch 3 (about 20 records read at full text during title/abstract screening).
- **Rule:** Ignore how the record was decided at title/abstract. Screen the full text like any other record. If the record cannot be linked to any document (a bare title fragment), use X6 after the retrieval steps in section 3. A document whose own stated contribution is a survey, review, tutorial, position or perspective, with no new method, theory or experiment of its own, is X3. A survey that also reports new experiments of its own (for example a benchmark run by the authors) is a primary study.
- **Positive:** none named with an id in the ambiguity file (the "about 40 DLM-pointing titles" of A batch 1 item 3 are the positive cases).
- **Negative:** M14799 (A X3 by title, B unclear) is expected X3 if its body is a survey with no experiments of its own; M15918 (A X1 on the title, B unclear) is expected X2 by R9 if its diffusion model only generates images from LLM-written prompts.
- **Reason:** protocol s4 step 5 repeats screening at full text with an exclusion code from s2; PRISMA item 16b needs a reason per full-text exclusion, which a title cannot give.

### R2. Language of the record
- **Raised in:** A batch 1 note (M13102 Catalan title, English abstract; M11407, M11397 Ukrainian titles, English abstracts).
- **Rule:** Exclude X8 if the main body (method and results sections) is not in English, whatever the language of the title or abstract. An English abstract or an English summary attached to a non-English body does not count. If the body is English, apply the other rules.
- **Positive:** M13102 if its body is in English (no record in the file is known to be).
- **Negative:** M13102 is expected X8 if its body is in Catalan.
- **Reason:** protocol I3 requires the full text in English; X8 covers "not in English".

### R3. Duplicates and versions of one study
- **Raised in:** A batch 1 note (M18918 and M09530, TrustLDM); B batch 3 item 3 (M08950 and M17772, dWorldEval).
- **Rule:** Two records are one study if they share the method or benchmark name and at least one author, and one text is a revision, extension or published version of the other (the same arXiv ID, a statement such as "an earlier version appeared as", or a journal paper that names the conference paper as its basis). Retain one record: the peer-reviewed version if it is retrievable, else the latest arXiv version; if both are equally recent, the one with more results tables. Both screeners screen both records and fill `dup_of`. The non-retained record takes X5 if the retained record is included; otherwise it takes the retained record's code. Different method names, or no shared author, means two studies.
- **Positive (retain):** M18918 or M09530, whichever text is retained by the rule; the pair is expected to be one study (same title apart from a plural).
- **Negative (X5):** the other record of that pair. M08950 and M17772 are one study only if the full texts meet the test (titles differ; both name dWorldEval).
- **Reason:** protocol X5; PRISMA counts studies, not reports, and RQ2-RQ5 contrasts must not be counted twice.

### R4. Is there a diffusion component at all? (X0)
- **Raised in:** A batch 3 item 5 (diffusion as metaphor or non-generative role); V item 5 (M03972); A batch 2 item 5 (M17320); V item 3 (M07984).
- **Rule:** The paper's own method has a diffusion component if some output is produced by a learned reverse of a stated corruption process (masking or absorbing state, uniform token noise, Gaussian noise on embeddings, the simplex or latents), by discrete or continuous flow matching (including rectified flow), or by masked-generative iterative decoding (census B-5). Latent diffusion whose latents are decoded to text, even by an autoregressive decoder, counts and is I1(a). If no such component exists in the paper's own method or its own experiments, exclude X0. "Diffusion" meaning spread of information, innovation, heat or particles, cryptographic diffusion, graph diffusion kernels or diffusion imaging is not a diffusion component. A one-pass "refinement" step in an autoregressive model with no stated corruption process is not one. If the paper's experiments include an image or audio diffusion model (for example a general method tested on "LLMs and diffusion models"), it has a diffusion component; go to R9.
- **Positive:** M07984 (LaDi-RL, latent diffusion decoded to text for reasoning) is expected include under I1(a).
- **Negative:** M17320 (an encryption technique with "block diffusion") is expected X0.
- **Reason:** I1 requires a diffusion, masked-generative or discrete-flow component; X0 is the code criteria v1 already uses for failing I1 on that ground (formalised in section 2).

### R5. Non-diffusion methods that use DLMs only as baselines
- **Raised in:** B batch 3 item 5 (M09782 JetSpec, M12594 pcLLM).
- **Rule:** Include if any results table or figure (main text or appendix) reports the paper's own method applied to, or trained as, a diffusion text model or an eligible unified model (census B-5), for example a drafter trained with a masked denoising objective. Exclude X0 if diffusion models appear only as baselines, comparators or related work. For such an X0 record, add `"RQ2-context"` to `rq` when the paper reports its own runs of a DLM against an autoregressive method on the same task; it is cited in the RQ2 discussion but not counted as an included study.
- **Positive:** M09782 if its drafter is trained with a block or masked denoising objective (the abstract names "bidirectional block-diffusion drafters" as prior art; the full text decides).
- **Negative:** M12594 (pcLLM turns autoregressive models into parallel decoders and compares them with dLLMs) is expected X0 with `RQ2-context`.
- **Reason:** I1 is about the paper's own model or analysis; a baseline row is evidence the paper did not produce under its own design. RQ2 synthesis uses DLM studies with an AR baseline (protocol s1), and the context tag keeps the mirror-image evidence visible without double counting.

### R6. What counts as text output
- **Raised in:** B batch 1 item 1 (M14484, M13889, M13881, M03416); A batch 2 item 4 (M17653, M11849, M09557, M12328, M01553); B batch 3 item 3 (dWorldEval progress or success token); rescue (text rendered in images); A batch 3 item 4 (captions, transcripts).
- **Rule:** The diffusion component generates text if the variable it denoises or predicts is a sequence of tokens or characters of a natural language in an open vocabulary (words, sub-words, characters: answers, reasoning traces, captions, transcripts, translations, OCR or scene-text strings, slot values, entity strings), or code (source in a programming, query, markup or proof language). Length does not matter (census B-7). Not text: indices or continuous positions of spans, tags or labels from a fixed set (NER or sequence tags, sentiment polarity, class names, success, failure or progress tokens), embeddings or denoised hidden states, text drawn as pixels inside an image, and speech or audio-codec tokens. If the diffusion output is not text, go to R9 (and R10 for unified models).
- **Positive:** M13234 (a DLM regenerates slot values such as dates and names) produces text; R14 then decides between include and X7.
- **Negative:** M13881 (DiffusionSL denoises tag sequences) and M14484 (Gaussian noise on entity boundaries) are not text; both are expected X2 by R9 (the sentence is the conditioning input). M08950 / M17772: a progress or success token is a label, not text.
- **Reason:** I1(a) requires output that "includes natural-language text"; a fixed label set or a span index is a classification output, and RQ1-RQ4 concern text generation.

### R7. Symbolic strings that are not language
- **Raised in:** B batch 4 items 1 and 4 (M15835, M12848, M19094; M14279, M16987, M12789); rescue (tabular, symbolic music, graphs, molecules).
- **Rule:** SMILES or SELFIES, protein, DNA or RNA sequences, phylogenetic trees (Newick), chess positions or moves, Sudoku, maze or ARC grids, symbolic music, graphs and tabular records are not text (census B-7). A record whose diffusion output is only of this kind is included only if (a) the same model is a text model by R6 elsewhere in the paper (it is trained on natural language or code, or reports a natural-language or code task), or (b) R8(b) holds. Otherwise go to R9 (X2 if text or code is an input, else X1). Design choices predicted for a program (for example pragma settings chosen from a menu) are not code unless the model emits them as source tokens.
- **Positive:** M12848 (the abstract calls its models "Draft Refinement Language Models" trained to repair uniformly corrupted drafts) is expected include by R8(b), or by (a) if it reports natural-language reasoning tasks.
- **Negative:** M14279 (SMILES generation) is expected X1; M16987 (Newick trees from DNA matrices) X1; M12789 (pragma designs conditioned on the program) X2.
- **Reason:** I1(a) is about natural-language text or code; puzzle and symbol tasks matter to the review only as tasks of a language model (RQ4 sweeps are often reported on them).

### R8. Generic discrete-diffusion or flow theory and methods
- **Raised in:** V item 2 (M02995); A batch 1 item 2; B batch 1 item 3; A batch 2 item 1; A batch 3 item 2; B batch 3 item 2; A batch 4 item 3 (inconsistent X1 versus unclear across batches); B batch 4 item 3.
- **Rule:** Include if (a) any results table or figure, main text or appendix, reports the paper's own method on a natural-language or code dataset or task (for example text8, OpenWebText, LM1B, WikiText, a code benchmark, any natural-language benchmark), or (b) the title, or the abstract's statement of what the paper contributes, names language models, LLMs, text generation or code generation as the object of the result. A list of possible application domains, or a motivating sentence before the contribution, does not satisfy (b). If neither holds, exclude X1 (or X2 if text is a conditioning input).
- **Positive:** M12793 (Binary Discrete Diffusion; screener note: Text8 and OpenWebText language-modelling results) by (a); M11387 (theory whose abstract mentions text generation) by (b) if the mention is in the contribution statement.
- **Negative:** M18900 (exact unmasking in ferromagnetic Ising models; no text in the abstract; both screeners X1) is expected X1 unless its full text has a text experiment.
- **Reason:** I2 admits theory, but I1 requires output that includes text; census B-3 used the abstract framing only, and the full text adds a checkable test (a) that two screeners can verify from the tables. Theory with text experiments feeds RQ1 and RQ4.

### R9. Non-text diffusion output: X2 or X1
- **Raised in:** A batch 1 item 4 (TTS, text-to-image, text-to-motion, text-to-molecule); A batch 3 item 4 (masked-diffusion TTS, ASR, captioning); rescue (pipelines, text rendered in images coded X2).
- **Rule:** Apply only after R6, R10 and R11 show that the record is not eligible. Exclude X2 if (i) no component of the paper's model outputs text (R6) and (ii) natural-language text or code is an input of the diffusion component (prompt, caption, instruction, transcript, lyrics, description, source sentence, program). Class labels and category ids are not text inputs. Otherwise exclude X1. A model that generates text autoregressively and uses diffusion only for a non-text output that is not an I1(b) modality is X1 (D0020: robot actions, molecules and other non-text domains with autoregressive text). ASR, captioning or OCR whose transcript or caption is produced by the diffusion component is text output: include under I1(a).
- **Positive:** none named with an id in the file; the class is masked-diffusion ASR or captioning (A batch 3 item 4).
- **Negative:** M15918 (LLM-written prompts to an image diffusion model for detection data) is expected X2; M12807 (images generated by diffusion to augment multimodal translation; both X1 at title/abstract) is expected X2.
- **Reason:** protocol X2 ("text is used only as a conditioning input"); D0020 widened X1 to every non-text diffusion model, which makes X2 a subset of X1. Checking X2 first keeps the protocol's own X2 category informative in the flow diagram and makes the X1/X2 boundary one yes/no question.

### R10. Unified models: one model or a pipeline?
- **Raised in:** A batch 1 item 5 (M15137, M06731, M13195, M03951); A batch 2 item 2 (M19015, M15989, M16043, M18394, M14797, M08935; M04162 included); A batch 3 item 1 and B batch 3 item 1 (M15792, M09294, M07750); A batch 4 item 2 and B batch 4 item 5 (M03150, M17285, M14249, M03633, M06272; M19019, M15184 included); rescue (LLM plus separate image generator coded X2).
- **Rule:** Include under I1(b) only if all three hold:
  (b1) *Understanding:* the paper shows the system producing text (R6) from an input in an R11 modality, in at least one table, figure or worked example. The text may be autoregressive.
  (b2) *Generation:* the system generates an R11 modality, and that output comes from a diffusion, masked-generative, discrete-flow or flow-matching (including rectified-flow) component.
  (b3) *One model:* either understanding and generation share parameters (one backbone; mixture-of-transformers with shared attention counts), or the generator, or a connector feeding it, is trained or fine-tuned in this paper on the understanding model's hidden states, learned query tokens or output embeddings (frozen understanding model allowed). It is a pipeline, not one model, if what passes from the understanding model to the generator is decoded text (a prompt, caption, plan, layout or tool call written as text), or if released models are combined without training any interface between them.
  If (b1), (b2) or (b3) fails, judge the components separately: a diffusion component that generates text is I1(a) (include); otherwise R9 (usually X2). How the paper names itself ("unified", "any-to-any", "omni") does not count.
- **Positive:** M04162 (JanusFlow, autoregressive text with rectified-flow image generation in one model) and M15792 (LayerBridge, a pixel-diffusion decoder trained on features of a frozen VLM) are expected include if (b1) is shown. M03150 (X-VILA, diffusion decoders aligned to LLM outputs) is expected include if the alignment is trained in the paper.
- **Negative:** M17285 (Qwen-Image-Omni, VLM and DiT connected "through structured skill calls") is expected X2 if the full text confirms the interface is a decoded instruction.
- **Reason:** D0020 defines "unified" as one model or one jointly trained system, not a pipeline of separately trained models; census B-4 excludes models joined only at inference. Frozen-backbone designs with a trained connector are the "decoupled" arm of RQ5's shared-versus-decoupled contrasts, so excluding them would remove RQ5 evidence. The interface test is a fact stated in every method section.

### R11. Which modalities count for I1(b)
- **Raised in:** V item 1 (M19014); A batch 1 item 1 and B batch 1 item 5 (M15992, M12951); A batch 4 item 1 and B batch 4 item 2 (M15235, M15236, M12859).
- **Rule:** The other modality for I1(b) is image (including edited images), video, audio (including speech and music audio), or 3D object or scene geometry (mesh, point cloud, voxels, implicit fields, 3D Gaussians). Human motion, pose, gesture and facial-animation parameter sequences, robot actions and trajectories, cell expression profiles, molecules, proteins, graphs, tables and time series do not count. A record whose only other modality is one of these is eligible only under I1(a) (a diffusion component generates text, for example motion captioning by a text DLM); otherwise R9.
- **Positive:** M12859 (PoseDLLM, a masked discrete diffusion LM for multimodal 3D human pose) is expected include under I1(a) if its dLLM generates text in a reported result; pose alone would not qualify. M19014 (UniTMGE) is include under I1(a) only if its motion captions come from the diffusion component.
- **Negative:** M12951 (CellUMM, flow generates expression profiles; both screeners X1) is expected X1; M15236 (HuMoGPT) is expected X1 if motion is the only diffusion output and its text is autoregressive.
- **Reason:** D0020 lists image, video, audio or speech, and 3D; reading "3D" as object or scene geometry keeps the list closed and decidable. Widening it to motion would need a protocol amendment and would add a separate literature with its own benchmarks to RQ5.

### R12. Vision-language-action, driving, navigation and world models
- **Raised in:** A batch 1 item 1 (M08652); B batch 1 item 2 (M15897, M08652); A batch 2 item 3 (M15330, M09851, M09916); A batch 3 item 3; B batch 3 item 3 (M08950, M17772).
- **Rule:** Actions, trajectories, waypoints and progress or success tokens are neither text (R6) nor an R11 modality. Include only if (a) a diffusion component generates text (reasoning, answers, captions, plans written as text) in a reported result (I1(a)), or (b) R10 holds (text from an image input and an image or video generated by a diffusion component in one model). Otherwise exclude: X2 if a language instruction is an input and no component outputs text; X1 if the model also generates text autoregressively (D0020) or takes no text input.
- **Positive:** M08652 (MMaDA-VLA) is include only if the full text reports text generated by the model (it jointly denoises a goal image and actions; goal images alone do not satisfy (b1) of R10).
- **Negative:** M15897 (LLaDA-Nav, navigation actions from a diffusion VLM) is expected X2 if a language instruction is its input and it outputs no text.
- **Reason:** D0020 names robot actions as X1 for unified models with autoregressive text; I1(b) requires understanding that produces text (census B-4), which an action decoder does not show.

### R13. DLMs used as encoders, embedding backbones, estimators or scorers
- **Raised in:** B batch 1 item 4 (M16168, M15450); B batch 3 item 4 (M08140); V item 4 (M04871).
- **Rule:** Include if the paper (a) trains or fine-tunes a model with a diffusion objective over text at any stage, including diffusion pretraining of an embedding backbone, (b) reports a result about a text diffusion model's likelihoods, internals, outputs or robustness (census B-2), or (c) compares a diffusion-pretrained text backbone with a non-diffusion one. Exclude X7 if an existing text diffusion model is used unchanged as an instrument (scorer, estimator, feature extractor) and no result is about it. Exclude X0 if the paper only fine-tunes, as a non-generative model, a backbone whose diffusion pretraining was done elsewhere and reports none of (b) or (c). Exclude X1 if the diffusion model is over non-text data.
- **Positive:** M08140 / M16168 (pplx-embed, contrastive training "on a diffusion-pretrained language model backbone") are expected include if the paper performs the diffusion pretraining or compares with a causal backbone; they are also checked under R3 (same name, possibly one study).
- **Negative:** M04871 (INFO-SEDD as an information estimator on synthetic and Ising data) is expected X1.
- **Reason:** I1 includes "analyses"; census B-2 already uses X7 for instrument use. Diffusion pretraining as a route to bidirectional encoders is a training-strategy finding (RQ3).

### R14. Applications and systems built on an existing DLM or unified model
- **Raised in:** B batch 1 X7 practice (M17603, M13234, M14428, M15731); A batch 2 item 4 (M12807, M14235 coded X7).
- **Rule:** Include if any of: (a) the paper trains, fine-tunes or modifies the model (weights, objective, sampler, decoding, caching, schedule, remasking, guidance) or proposes an inference, serving or hardware method for an eligible model (census B-1; X7 is never used for these); (b) a results table compares the DLM or unified model with another generator (an autoregressive model or another DLM) on the same task and data; (c) a results table varies a setting specific to the diffusion model (number of steps, unmasking order, remasking, block length). Exclude X7 if the model is used with its released weights and sampler as one part of a pipeline or as a tool, and none of (a)-(c) holds. A with-versus-without ablation of the whole module is not (b) or (c).
- **Positive:** M14428 (LLaDA-Mutate, "a hybrid decoding strategy" for LLaDA) is expected include by (a); M15731 (six models including a DLM evaluated on veterinary ICD-11 coding) is expected include by (b).
- **Negative:** M17603 (a DLM generates an intent snippet inside a retrieval pipeline) is expected X7 if the full text has no comparison of the DLM step against another generator and no sweep of its settings.
- **Reason:** protocol X7 ("uses an existing model unchanged and reports no model-level finding"); (b) and (c) define "model-level finding" by the RQ2 and RQ4 evidence they produce.

---

## 2. Full-text exclusion codes and the order they are applied

One code per excluded record: the first that applies in this order. A screener stops at the first
code that applies and records it.

| Order | Code | Definition (full text) | Rules |
|---|---|---|---|
| 1 | X8 | First public version before 2021-01-01 or after the search date (metadata), or main body not in English (full text) | R2 |
| 2 | X5 | Duplicate or superseded report of a study retained in the review (assigned from `dup_of` by script) | R3 |
| 3 | X6 | Full text not retrievable after the steps in section 3, including the user's VIT e-gateway attempt | R1, s3 |
| 4 | X3 | Secondary study (survey, review, tutorial, position, perspective) with no new method, theory or experiment of its own; listed separately for positioning | R1 |
| 5 | X4 | No method, theory or empirical result (abstract-only publication, poster or slides, demo description, blog, editorial, proposal) | s3 |
| 6 | **X0 (new)** | No diffusion, masked-generative or discrete-flow component in the paper's own method or its own experiments | R4, R5, R13 |
| 7 | X2 | Diffusion output is not text, no component outputs text, and natural-language text or code is an input; checked before X1 | R6, R7, R9, R12 |
| 8 | X1 | Diffusion output is not text, text is not an input or the text is generated autoregressively, and I1(b) does not hold (D0020 widening) | R7, R8, R9, R11, R12, R13 |
| 9 | X7 | An eligible model is used unchanged as a component or instrument and the paper reports no model-level finding about it | R13, R14 |

Notes.
- **X0 is a protocol amendment.** Criteria v1 and census B-8 use it, but protocol s2 does not list it. It needs a dated s10 entry before the protocol freeze (proposed text at the end).
- **Order differs from census B-8** (X8, X3, X5, X4, X0, X1, X2, X7) in three places: X6 is added because full-text screening retrieves full texts and the census did not; X5 is moved before X3, which changes no outcome because X5 applies only to a report of a retained study; X2 is placed before X1 (R9). Under D0020 X1 contains every X2 case, so with X1 first X2 would never be used. The order is part of the proposed amendment.
- X6 versus X4: X6 when the evidence shows that a full paper exists (page range, article DOI, thesis record) but no copy can be obtained; X4 when the only document is an abstract, poster, slides, demo or blog post.
- No "unclear" at full text. When a screener remains in doubt after the rule, the decision follows the rule's default (the "otherwise" branch). Disagreements go to the human author (protocol s4 steps 4-5).

---

## 3. What the screeners read, and "no full text retrievable"

**Version screened (protocol s3).** The latest arXiv version available on the retrieval date; if
there is no arXiv version, the published version; if neither, another open copy (thesis
repository, OpenReview, ACL Anthology, CVF, PMLR, author page). The orchestrator retrieves one file
per record before screening starts, stores it with its SHA-256 and version string, and gives both
screeners the same file. Screeners do not look for other versions themselves.

**Sections both screeners must read.**
1. Title, abstract and the contribution list of the introduction.
2. Method section(s): what is generated, by which component, from which inputs, and how components are trained or connected (R4, R6, R10, R13).
3. Experiments: dataset names, every results table and figure caption, and the ablation tables (R5, R8, R14, RQ tags).
4. Conclusion and limitations.

**Appendix, only when needed:** read or keyword-search the appendix if the main text does not
settle one of these: a natural-language or code experiment (R8a); training of the interface or the
connector (R10 b3); whether the DLM's weights, sampler or settings were changed or varied (R14);
the output format of the diffusion component (R6). Record the appendix location if it decides.

**Evidence.** Every decision carries one verbatim quote of at most 40 words from the screened file
that supports the decision or the code, with its location: `p.<PDF page>, §<section number or
heading>` (PDF) or `§<heading>, Table <n>` (HTML).

**"No full text retrievable" (X6)** means no complete copy of the paper (method and results
sections) could be obtained after all of these, each logged with source, date and outcome in the
retrieval log:
1. arXiv by identifier, then by exact title;
2. OpenReview, ACL Anthology, PMLR, CVF Open Access, NeurIPS proceedings, by title;
3. the DOI landing page, and the open-access locations given by Semantic Scholar (`openAccessPdf`), OpenAlex and Unpaywall;
4. the publisher through the user's VIT e-gateway session (the user runs this step; agents list the records and stop);
5. institutional or thesis repositories for theses and dissertations.

Not full text: the abstract alone, a preview of the first pages, a table of contents, or a
machine translation of the abstract. An arXiv record withdrawn by its authors is screened on its
last full version, if there is one, with `note: "withdrawn"`; otherwise X6. A non-English full text
is retrieved and coded X8, not X6.

---

## 4. Screener brief (full-text screening; give to Screener A, Claude Sonnet, and Screener B, Claude Opus)

```text
FULL-TEXT SCREENING, Paper 1 (criteria v1.1). Read research/CONTRACT.md first.
You are blind: do not open other screeners' files, title/abstract decisions, disagreements files
or research/review/corpus/. Use only research/review/screening/criteria-v1.1.md (rules R1-R14,
section 2 codes) and the full-text file your dispatch gives for each record.

READ: title, abstract, introduction contributions, method, experiments (all results tables, figure
captions, ablations), conclusion/limitations. Appendix only for R8(a), R10(b3), R14, R6 questions.

DECIDE each record include or exclude (no "unclear"). Go through the codes in this order and stop
at the first that applies:
 X8 date out of 2021-01-01..search date, or body not in English (R2)
 X5 report of the same study as another record: fill dup_of, decide on content; X5 is set by script (R3)
 X6 file says no full text retrievable (section 3)
 X3 survey/review/tutorial/position with no new method, theory or experiment of its own
 X4 abstract-only, poster, slides, demo, blog, editorial
 X0 no diffusion, masked-generative or discrete-flow component in the paper's own method (R4, R5, R13)
Then test eligibility:
 I1(a) a diffusion component of the paper's own method generates text (R6: open-vocabulary
       natural language or code; not labels, spans, tags, embeddings, pixels, SMILES, grids)
       - generic theory: R8 (text/code experiment in any table, or contribution named as LM/text/code)
       - symbolic domains: R7; encoders/estimators: R13
 I1(b) R10 b1 text produced from image/video/audio/3D input is shown, b2 that modality is generated by
       a diffusion/masked/flow component, b3 one model (shared parameters, or a generator/connector
       trained here on the understanding model's hidden states; decoded-text interface = pipeline).
       Modalities: R11 (motion, pose, actions, cells, molecules do not count). VLA/driving: R12.
If not eligible: X2 if no component outputs text and text/code is an input (R9), else X1.
If eligible: X7 only if R14 says the model is used unchanged with no model-level finding
(no modification, no comparison with another generator, no sweep of DLM settings). Else include.

RQ TAGS (included records): always "RQ1" and "RQ6"; add
 "RQ2" own results table with an autoregressive baseline on the same task;
 "RQ3" within-paper contrast of a training choice (pretraining recipe, SFT, RL, distillation);
 "RQ4" within-paper contrast of an inference setting (steps, unmasking order, remasking, caching,
       parallel or block decoding);
 "RQ5" i1 includes b AND (a task-removal, shared-vs-decoupled ablation, synergy benchmark, or a
       claim that understanding and generation help each other).
 Excluded: [] except "RQ2-context" for an R5 X0 paper with its own DLM-vs-AR runs.
MULTIMODAL FLAG mm: true if the included model takes or generates image, video, audio/speech or 3D
(R11); false if text only; null if excluded. i1: "a", "b", "ab" or "" if excluded.

EVIDENCE: one verbatim quote <= 40 words that supports the decision or code, plus location
"p.<pdf page>, §<section>" or "§<heading>, Table <n>".

OUTPUT: append one JSON object per record (UTF-8, one line, in chunks of at most 10) to the file
your dispatch names; every id exactly once; on resume skip ids already present:
{"id": "M04162", "decision": "include", "code": "", "rule": "R10", "i1": "b",
 "evidence": "<verbatim quote>", "loc": "p.4, §3.2", "rq": ["RQ1", "RQ5", "RQ6"], "mm": true,
 "dup_of": "", "ft": "<version string from dispatch>", "note": "",
 "screener": "FA-claude-sonnet" | "FB-claude-opus"}
code: one of X8 X5 X6 X3 X4 X0 X2 X1 X7, empty for include. rule: R1-R14 that decided, or "" when
no ambiguity rule was needed. note: at most 20 words (e.g. "withdrawn", "appendix decided").
FINAL MESSAGE: counts by decision and code, ids whose rule you found hard (id + rule + one
sentence), up to five gaps in the criteria. Never edit criteria or other files.
```

(The brief is 53 lines inside the block.)

---

## 5. Changes from the title/abstract rules, and their effect on title/abstract decisions

Title and abstract decisions are not re-opened (D0030). The table says whether a change would
have changed a title/abstract decision had it applied then.

| # | Change (v1 / SCREENER-BRIEF to v1.1) | Would it change a title/abstract decision? |
|---|---|---|
| 1 | Decisions are binary; "unclear" is removed | No; it only applies at full text. |
| 2 | X8 language is read from the full-text body, not the title (R2) | Possibly for 2 records excluded by both screeners on a non-English title with an English abstract (M11407 A X0 / B X8; M11397 A X3 / B X8). Only if their bodies are in English. See 5.2. |
| 3 | X0 becomes a listed code with the census B-5 test (R4) | No; criteria v1 already used X0. |
| 4 | X2 is checked before X1 (R9) | No decision changes; only the code of non-text records changes (for example both-X1 NLP-tagging records become X2). Title/abstract codes do not enter the PRISMA flow (only full-text reasons do). Departs from census B-8. |
| 5 | Generic theory: a text or code experiment anywhere in the paper is enough (R8a); the abstract test (R8b, census B-3) stays | **Yes, possibly.** Records both screeners excluded as X1 on an abstract with no text framing may have text experiments in the body. 5.2 lists the candidates. More inclusive than census B-3; census eligibility of its own sample is not recomputed. |
| 6 | Unified models: the interface test (R10 b3) replaces criteria v1's note that frozen-LLM systems are X2 "unless presented as unified" | **Yes, possibly**, for a few both-X2 records with a frozen VLM and a trained diffusion decoder, if they show understanding output (5.2). Records that passed are unaffected. |
| 7 | I1(b) needs text produced from another-modality input (R10 b1, census B-4) and R11's closed modality list (motion, pose, actions, cells excluded) | No re-open. It can turn title/abstract includes into full-text exclusions (for example M08652, included by B on its goal images). |
| 8 | What counts as text (R6) and symbolic strings (R7) | No. Both-excluded tagging, span and SMILES records stay excluded; their code may change to X2. |
| 9 | Encoders and estimators (R13) | No; the named records were unclear and passed. |
| 10 | DLMs as baselines only: X0 plus `RQ2-context` (R5) | No. |
| 11 | X7 narrowed: comparison with another generator or a sweep of DLM settings is a model-level finding; inference, serving and hardware methods are never X7 (R14, census B-1) | **Yes, possibly**, for serving systems excluded by both screeners (M07991 vLLM-Omni A X7 / B X1; M09949 Omni-Flow A X7 / B X1) if they serve an eligible unified model and report results on it. Not in the ambiguity file; found by the check in 5.2. |
| 12 | X5 rule for versions (R3); X6 and X4 separated (section 3) | No. |
| 13 | Title-only and truncated-abstract records are judged on the full text (R1) | No; the disclosures (A batch 3 full-text reads; rescue batch 2 partial reading) stay in Methods as written in the ambiguity file. |

### 5.1 Recommendation
Do not re-open title/abstract screening. Changes 2, 5, 6 and 11 make the full-text rules more
inclusive than the rules applied at title/abstract, so a few records excluded by both screeners
might have passed under v1.1. Two options for the orchestrator, either to be disclosed in Methods:
(a) accept the asymmetry and state it as a limitation with the counts below; or (b) give the named
candidates in 5.2 to both full-text screeners as a separate, pre-declared consistency check,
reported in its own flow-diagram box ("excluded at title/abstract, checked at full text after
criteria v1.1"), never merged into the title/abstract counts. I recommend (b) because the list is
short and fixed now, before any full text is read.

### 5.2 Candidate records (from the 999 records both screeners excluded; title-level reading, E1)
- Change 2 (language): M11407, M11397 (M13906 also has a B X8 code; A coded it X0, no diffusion model; if that reading holds, it stays excluded under R4 whatever its language).
- Change 5 (generic method or theory, both X1, no language word in the abstract): M15208, M15627, M16235, M10096, M08266, M10858, M04723, M05453, M06388, M13950, M13654, M09101. Script count: 307 both-excluded records contain a discrete or masked diffusion or flow term; these 12 are the ones whose titles name a general method rather than an application domain (my reading of titles).
- Change 6 (frozen VLM or MLLM plus diffusion decoder, both X2): M19004, M10697, M08147.
- Change 11 (serving systems for any-to-any models): M07991, M09949.

Total: 19 records. None of them is in the full-text set now.

---

## 6. For the orchestrator: proposed protocol s10 amendment and ledger row

Proposed text for protocol section 10 (to be added by the orchestrator, dated on entry; this file
does not edit the protocol):

```text
- <date> (D0032; full-text screening criteria v1.1, research/review/screening/criteria-v1.1.md).
  Made before any full-text screening decision and before the freeze rule is applied. Eligibility
  I1-I4 is unchanged; the following readings and codes govern full-text screening.
  (1) New exclusion code X0: no diffusion, masked-generative or discrete-flow component in the
  paper's own method or its own experiments (a component exists when some output is produced by a
  learned reverse of a stated corruption process, by discrete or continuous flow matching, or by
  masked-generative iterative decoding). Criteria v1 and the census (codebook v1.2 B-5, B-8)
  already used X0; s2 did not list it.
  (2) One code per excluded record, the first that applies in the order X8, X5, X6, X3, X4, X0, X2,
  X1, X7. X2 (no component outputs text and natural-language text or code is an input) is checked
  before X1 because the 2026-10-15 widening of X1 (D0020) contains every X2 case.
  (3) I1(b) requires that the paper shows the system producing text from an input in another
  modality, that the other modality is generated by a diffusion, masked-generative or flow
  component, and that understanding and generation are one model: shared parameters, or a
  generator or connector trained in the paper on the understanding model's hidden states, query
  tokens or embeddings. A decoded-text interface is a pipeline. "3D" in the D0020 list means 3D
  object or scene geometry; human motion, pose, gesture, robot actions and trajectories, cell
  profiles, molecules and other non-perceptual outputs do not count as another modality.
  (4) I3 and X8: the language of the main body decides; an English abstract on a non-English body
  is X8.
  (5) X6 is used only after the retrieval steps of criteria v1.1 section 3, including the
  e-gateway attempt; an abstract-only, poster, slide or demo publication is X4.
  Reason: title/abstract screening of the 2026-10-15 search update recorded ambiguity classes that
  the protocol does not settle (screening-ambiguities.md); D0030 requires them to be settled by a
  criteria amendment before full-text screening. Title/abstract decisions are not changed; 19
  records excluded by both screeners that the full-text rules might have passed are listed in
  criteria-v1.1 section 5.2 and handled as decided in D0032.
```

Proposed ledger row (`python tools/ledger.py add decisions --file row.json`; id and timestamp to
be set by the orchestrator):

```json
{
  "id": "D0032",
  "decision": "Full-text screening uses criteria v1.1 (research/review/screening/criteria-v1.1.md), written before any full text is screened: (1) rules R1-R14, one per title/abstract ambiguity class in screening-ambiguities.md, each decidable from the full text; (2) X0 added as a full-text exclusion code (protocol s10 amendment) and one code per record in the order X8, X5, X6, X3, X4, X0, X2, X1, X7, with X2 checked before X1; (3) I1(b) read as text produced from another-modality input, that modality generated by a diffusion, masked-generative or flow component, and one model by an interface test (shared parameters, or a generator or connector trained on the understanding model's hidden states; decoded-text interfaces are pipelines); 3D means object or scene geometry, so motion, pose, actions and cell profiles are not another modality; (4) I3/X8 read on the language of the main body; (5) dual blind full-text screening by Screener A (Claude Sonnet) and Screener B (Claude Opus) with the section 4 brief, binary decisions, verbatim evidence with page and section, RQ tags and a multimodal flag; disagreements to the human author (protocol s4); (6) title/abstract decisions are not re-opened; the 19 both-excluded records that v1.1 might have passed (section 5.2) are [option a: reported as a limitation | option b: checked by both full-text screeners as a separate, pre-declared box in the PRISMA flow].",
  "options": ["keep criteria v1 at full text and adjudicate ambiguities case by case", "criteria v1.1 with a protocol amendment, no re-open (limitation)", "criteria v1.1 with a protocol amendment and a pre-declared consistency check of 19 records"],
  "evidence": "research/review/screening/criteria-v1.1.md; research/review/screening/v2/screening-ambiguities.md; research/review/protocol.md s2, s4, s10; research/review/coverage/census-codebook-v1.2.md B-1 to B-8; decisions D0020, D0030",
  "owner": "orchestrator (user delegated expert judgement)",
  "reversal": "gate-auditor or red-team finds a rule that two screeners cannot apply without discussion (rule rewritten before screening starts), or the professor requires motion or pose to count as another modality (protocol amendment and rescreen of R11 exclusions)"
}
```
