# Response to the supervising professor's technical assessment (2026-10-21)

Paper 1, "Diffusion Language Models and Unified Multimodal Generation: A Critical Systematic Review".
Revision commits on branch `claude/resume-dlm-discovery-exp-003-334706`, from b2ef278 onward (decision D0069).
Outputs: `paper/review/main.pdf` (37 pages: text to page 32, references 5 pages), `paper/review/supplement.pdf`
(52 pages), `paper/review/docx/main.docx`. Section numbers below are those of the revised main text (a new
Section 8 was inserted, the old EXP-003 section is now a short subsection of Section 9, and Limitations is Section 10).

New numbers come from committed scripts only:
`analysis/extraction/d0052/revision_sensitivity.py` (output `revision-sensitivity.json`),
`analysis/census/census_by_year_venue.py` (`census-by-year-venue.json`), `paper/review/scripts/revision_tables.py`
(exemplar and partial-fit tables), `paper/review/scripts/revision_refs.py` (reference check, log
`research/review/audits/2026-10-21-revision-refs.json`).

## Changes made at the author's request

| Request | What changed | Where |
|---|---|---|
| AI model names out of the paper, including the supplement | Names appear only in the Declaration on the use of AI. The supplement now names roles (automated coder, a system from a second provider, automated adjudicator, separate AI assistant). | main.tex Declaration; supplement S1, S3, S4, S7, S9 |
| AI use portrayed positively | The Declaration now opens with what AI made possible (independent double screening and extraction at scale) under the authors' direction, then lists the models and the checks: verbatim quotes matched against each paper, isolated sessions with recorded models, independent readers, a validator on every extracted value, and number-to-source audits. It closes with the correlated-error caveat, stated as a reason for the reported agreement statistics. | main.tex, before the references |
| No repository-file pointers (circled in the old Methods) | Every `research/...`, `analysis/...` and script path removed from main and supplement prose, including the author-checks pointer; the data availability statement is the only pointer. The search-string table generator now prints "the archived search log". | Sections 2, 5; supplement S1, S3, S5, S6, S7, S9 |
| Old Section 2.8 and its Table 2 of model names | Already removed in D0067; confirmed absent. | none |

`paper/review/scripts/final_checks.py` scans main.pdf, supplement.pdf and main.docx and reports 0 model names outside the
Declaration, 0 repository paths and 0 hidden Unicode carriers. EXP-003's measurement instruments (Qwen3-VL-2B, CLIP)
and the diffusion models under review are method content and stay.

## Weaknesses

**Technical limitations: protocol departures, AI screeners without human validation, screening freeze.**
The departures are still stated, but no longer as a 12-item list in Section 2. A summary paragraph groups them
(protocol status, selection, extraction and synthesis), and the full list moved to Supplement S1. A new paragraph in
Section 10 (Limitations), "What would close the validation gap", sets the human-only validation standard (see Q5).
The freeze and the landmark tranche are unchanged; Section 10 now also says that compute-matched studies outside the
sample may be under-represented and that Section 5 reconciles them.

**Design-space table only partly re-validated; 11 partial fits.** Supplement S5 has a new table of the 11 partial
fits, giving each one's row provenance (copied from an earlier reading, 4 of them, or read at section level, 7), its
evidence level and the extension it needs. Section 4 points to it and to the released 47-row table with per-row
provenance (Q6).

**V is bookkeeping with no magnitude.** New open problem OP5 (Section 9) gives a protocol that brackets V's effect on
one frozen model (Q2). Section 7 has a new paragraph, "Independent evidence, and sizing V", which ties the
factorisation term to the HMM-oracle study and to dependency-aware selection, and says why V gets no magnitude.

**No meta-analysis; sparse matched compute; post-hoc thresholds.** Section 5 now reports a 60-setting joint threshold
grid and robustness to the stratum design (Q3, Q4), and closes with the sentence "the verdicts summarise the sample under
a stated rule; they are not tests". The compute-matched studies are integrated in RQ2 (Q1).

**Extraction reliability, missing human validation, validator-rejected entries.** These are unchanged and still
disclosed (Section 2 summary, Supplement S4 in full). Estimates without the rejected entries are in Supplement S6.
The leave-one-out analysis shows that dropping any single sampled study changes only RQ5 (to untested), and only when
the dropped study is one of its five signed studies.

**Freeze before the seed corpus; landmark tranche; possible under-counting of compute-matched studies.** The new
Limitations paragraph "Studies outside the sample" covers the under-counting. The design limits are unchanged.

**Dense, heavy cross-referencing; Section 2 reads like an audit report.**
- Section 2 opens with "The method at a glance".
- Search, deduplication and filter detail (about 650 words) and the extraction procedure (about 880 words) moved to
  Supplement S1 and S4, with short summaries in Section 2. The departures list moved too.
- The census coder-agreement table moved to Supplement S3, with a summary left in Section 6.

**More top-level summaries: design-space figure, exemplar mappings, decoding recommendations.**
- New Section 8, "What the evidence means for practice":
  - A table of twelve canonical models (MDLM, SEDD, LLaDA, Dream 7B, Fast-dLLM, BD3-LM, ReMDM, Duo, Plaid, MMaDA,
    UniDisc, Show-o2) mapped onto C1, the position and value rules (C4), revision (C5) and fit. Rows are copied by
    script from the 47-model table.
  - Five decoding defaults, each tied to its evidence.
  - A seven-item reporting checklist, with the census and sample counts that show how often each item is missing.
- A new table at the start of Section 5 states each RQ's answer, evidence and verdict.
- The compact design-space figure is the taxonomy tree (Section 1) and the dot matrix (Supplement S5).

**Missing related work (compute-matched and sampler-centric).** Thirteen references were added. Each was verified to
exist on arXiv with a matching title, and each citing sentence was checked against the abstract:
- isoFLOP and scaling: 2410.18514, 2602.15014.
- Data-constrained crossover: 2507.15857, 2511.03276.
- Continuous and flow text models: 2604.11748 (LangFlow), 2603.02547 (CoDAR).
- Parallelism theory: 2609.20539.
- Dependency-aware selection: 2604.02560 (DEMASK).
- Trace-based controller: 2605.24697 (TraceLock).
- Remasking re-evaluation: 2606.12232.
- HMM oracle: 2602.19619.
- Speed-quality Pareto: 2605.15609. It was verified and added to the bibliography but is not cited in the text, so
  it does not appear in the reference list.
- Chunk-causal flow unified model: 2609.40362 (Multimodal Flow).

Where they are integrated:
- RQ1 context: continuous and flow models.
- RQ2: compute-matched studies.
- RQ4: sampler-centric studies.
- RQ5: a fully continuous unified model.
- Section 6: the HMM oracle and generative perplexity.
- Section 7: the factorisation term.
- Section 8: defaults.

## Questions

1. **Sensitivity of RQ2-RQ5 to compute-matched studies.** Answered by qualitative reconciliation (Section 5, RQ2,
   RQ4 and RQ5 paragraphs; Section 10). No verdict changes, because each verdict describes the sampled studies. The
   matched studies change the reading:
   - The RQ2 split reflects unmatched budgets.
   - Diffusion pays a compute gap on likelihood under single-pass training, overtakes autoregressive training when
     data is scarce, and can win on the speed-quality frontier.
   - RQ4's non-monotone curves have a sampler-side explanation (the HMM oracle) and practical levers (DEMASK,
     TraceLock).
   - Remasking is a remedy whose value depends on stochasticity and block size.
2. **Operationalising V.** OP5 (Section 9) gives the protocol, stated as future work with no GPU runs:
   - Arms at matched network calls and matched entropy: plain sampling (V = 0), rank-then-sample,
     sample-then-filter with its resampled twin, and best-of-N.
   - The quality gap to plain sampling brackets what the value rule buys.
   - The per-step divergence between the rule's value law and the marginals, computable from the logits for argmax,
     temperature and truncation rules, gives a model-side size that does not depend on the data coupling.
3. **Weights, effective n, robustness to stratum misclassification and post-hoc exclusions.** Answered in Section 5
   (Verdicts paragraph) and Supplement S6:
   - Kish effective n is 46.1 for the 59 included studies. For the signed studies behind RQ2 to RQ5 it is 15.6, 18.2,
     13.7 and 5.0.
   - Merging the two language strata changes no verdict.
   - Moving each language-only study to the other language stratum with probability 0.2 (1,000 draws) turns RQ4
     weakly supported in 8 draws and changes nothing else.
   - Leave-one-out changes only RQ5, in 5 of 59 runs.
   - Stratum weights N_h/n_h are in `revision-sensitivity.json`.
4. **Verdicts under alternative thresholds.** In the 60-setting joint grid (direction share 0.55 to 0.80, control
   share 0.30 to 0.60, minimum 3 to 8 signed studies):
   - No verdict is well supported in any setting.
   - RQ2 is mixed in all 60.
   - RQ3 is weakly supported in 48 and mixed in 12.
   - RQ4 is mixed in 36 and weakly supported in 24.
   - RQ5 is mixed in 24, untested in 20 and weakly supported in 16.
   - 16 settings reproduce all four main verdicts.

   This adds to the earlier one-at-a-time analysis (Section 5, Supplement S6).
5. **Human validation plan.** Section 10, "What would close the validation gap":
   - Readers: two human readers, blind to the model decisions and to each other.
   - Sample: at least 100 full-text decisions (the protocol's own size), stratified by model decision, plus 20 extracted
     studies.
   - Acceptance: Cohen's kappa of 0.70 or more for inclusion and for each direction flag, and group-matching F1 of 0.6
     or more (the plan's warning line).
   - Below either threshold, the criteria or form are revised and the affected set redone.

   The existing author checks are reported as a first step, not a substitute. They are the first author's own blind
   checks; the reviewed sheets (D0070) give kappa 0.50 on the 24 of 40 screening records decided (16 unclear because
   the full text could not be opened), 0.82 on extraction flags and 0.79 on the census value-rule class.
6. **Design-space table with provenance; 11 partial fits.** The new Supplement S5 table lists the 11 partial fits
   with provenance and the extension each needs. The full 47-row table, with per-row provenance, version read and
   sections read, is released with the data (Section 4 says so).
7. **Preregistered four-arm experiment.** OP4 (Section 9) now has "A preregistrable design":
   - Checkpoints: the UniDisc checkpoint plus a text model.
   - Arms: four arms at 1, 2 and 4 tokens per step, at matched network calls.
   - Entropy matching: each arm's temperature is calibrated on held-out prompts before any outcome is seen.
   - Endpoints and contrasts: the EXP-003 dependence statistic is primary and S_theta secondary. The primary contrast
     is sample-then-filter against its resampled twin, with Holm correction across contrasts.
   - Sample size: set by a power calculation from the EXP-003 variance.
   - Gate: plain sampling must first show the joint link (the gate where the earlier attempt stopped).
8. **Census by year and venue.** Section 6 and Supplement S3 (new table). Headlines that are non-plain or unstated:
   - By year: 44 of 44 papers first posted in 2025, 88 of 93 in 2026, and 15 of 16 earlier.
   - By venue: 32 of 33 papers at a peer-reviewed venue (per Semantic Scholar) and 115 of 120 preprints.

   Generalisation is now worded cautiously: these are counts in the seed corpus under a codebook amended after coding.

## Overall points

- (i) Integration of compute-matched and sampler-aware studies: done in RQ2, RQ4 and RQ5 and in Sections 6 to 8.
- (ii) A targeted human-validated audit: specified as a plan with sample size and acceptance thresholds (Section 10).
  It has not been run; it needs two human readers and is the main remaining gap.
- (iii) Practitioner synthesis: the new Section 8 and the per-RQ summary table.

## Not done

- Page length: at the author's request the EXP-003 section became a short subsection of Section 9 (full text in
  Supplement S7), and the step-sweep corollary and census-lever paragraph of Section 7 moved to Supplement S8.
  The formalism figure of Section 3 and the lever table of Section 7 then moved to Supplement S8 (Figure S2,
  Table S15), with prose summaries in place. main.pdf is now 37 pages (text to page 32, references 5) against the
  35-page target recorded in D0068; the remaining 2 pages are the reference list.
- The human-only validation pass (Q5) and the four-arm and V measurements (Q2, Q7) are designs, not results.
- Clarity editing with research-humanizer was not run on the new text, to stay within the weekly budget.
- The release (GitHub and Zenodo) was not rebuilt or pushed.

---

# Second review (2026-10-21, evening): changes made

Decision D0072. main.pdf is now 34 pages including references (CSUR limit: 35 including references); the
supplement is 58 pages. Section numbers below are those of this version.

| Point raised | What changed | Where |
|---|---|---|
| (a) Reference format: "arXiv:2605.25343 [cs.CV]" repeated | eprint, archivePrefix and primaryClass removed from every entry, so each preprint prints once as "arXiv preprint arXiv:…" | references.bib, s6-refs.bib |
| (b) Abstract should state the contributions | Rewritten: scope, numbers, four contributions, findings, practical outputs | Abstract |
| (c) Text needed after the Introduction heading | Two opening paragraphs before 1.1 (what DLMs are, how the field grew, what this review does) | Section 1 |
| (d) Specific subsection names | 1.1 Decoding choices and the comparability of reported results; 1.2 Prior surveys of diffusion language and unified multimodal models; 1.3 Research questions and evidence base; 1.5 Scope of the claims; 1.6 Organisation of the article | Section 1 |
| (e) No paper titles in running text | Titles replaced by author citations (Li et al., Yu et al.) | 1.2 |
| Reference paper (Yang et al. 2023) and a CSUR systematic review (Ali and Molla 2025) | Their structure followed: unnumbered opening, short planning and protocol, bulleted criteria, selection summary with a flow figure, topical sections | Sections 1-2 |
| 4. Design space | Comparison table of 13 representative discrete, continuous and unified models; wording for 36 full and 11 partial fits made consistent; provenance and the extension each partial fit needs in Supplement S5.2. Reassessing all 29 transferred rows from the primary papers was not possible in this round | Section 4, Table 2 |
| 5. Reliability of the synthesis | New subsection 5.6 "How firm the conclusions for RQ2 to RQ5 are": matched compute (1 of 25), repeated runs (10 of 54), RQ5 threshold sensitivity | Section 5.6 |
| 6. Decision framework; supported vs hypotheses | Table "Choosing a formulation and decoding strategy by requirement" and table "Status of the main conclusions" | Section 8 |
| 1. Awkward wording in the abstract and 1.1 | Rewritten ("The line began", "615 included studies, 59 extracted…") | Abstract, Section 1 |
| 2. "Around them sit surveys", "none could not be placed", "We use V as bookkeeping" | Rewritten | Section 1 |
| 3. Table 1 labels "S1, S2, S1, S2" | The primes were lost in text extraction; the row now reads "strings S1 and S2 and their revisions" | Table 1 |
| 3. Agreement statistics in 2.4; [11] (Cohen) placement; screening vs PRISMA consistency | Section 2.4 rewritten with κ values in words and symbols; Cohen cited at the first κ; the counts match the PRISMA figure; the total is corrected to 79,963 (the sum of Table 1) | Section 2.4, Figure 2 |
| 4. / 6. Missing symbols in Sections 3, 6, 7, Table 6 | Present in the PDF and in the DOCX (192 Word equations); the extraction used for the review dropped inline math. Sentences that read badly without symbols were rewritten | various |
| 5. Claims for [26] Di4C, [43] Discrete Copula Diffusion, [53] CANDI | Checked against each paper's abstract: joint outputs over a set (Di4C, DCD) and a hybrid continuous-discrete channel (CANDI) are what those papers propose | Section 4.4 |
| 6. "agrees on the value-rule class for 21, ;" | Rewritten in full | Section 6.6 |
| 6. Equation (5); attribution to [28] (ARDM) and [36] (Li and Cai) | Checked: [28] introduces the any-order objective we credit; [36] gives the information-theoretic KL bound we credit | Sections 3, 7 |
| 7. "20 of the 55 … say that the value rule was" | Completed: "…state that the value rule was held fixed" | Section 8.5 |
| 8. "The evidence by research question is thin" | Rewritten: "The evidence for the research questions is weakest where…" | Section 11 |
| 8. Zenodo DOI of [19] | 10.5281/zenodo.23524470, the published v1.0.0 record of the data and code | References |
| (f) AI only in the Declaration | All mentions of AI, automated screeners and model names removed from the main text and supplement; AI appears only in the Declaration on the use of AI | whole paper |
| Not citing a table and a figure in one place | Separated (Section 2.2, Supplement S1.3) | Section 2 |
| (g) Screening section reads like a low-quality audit | Section 2 rewritten as a conventional SLR method: protocol, search strategy, eligibility criteria, two-stage study selection, scope of the screened set, extraction and appraisal, census, synthesis, deviations. Decision identifiers, internal set names (T1, R797), session checks and exclusion-code tallies removed from the text; the full procedure is in Supplement S1. PRISMA labels rewritten in plain terms | Section 2, Figure 2 |
| (h) Large empty spaces | PRISMA figure placed directly under the Study selection heading with a shorter caption; Word export checked: no part-empty page | DOCX |
| Statements and Declarations | Funding and competing-interests text as supplied | end matter |
| Page limit about 34 | 34 pages including references: open problems in full, landmark column, census figure, census agreement table, lever table and formalism figure moved to the supplement; limitations rewritten | whole paper |

Also fixed after an independent desk check (research/review/audits/2026-10-21-desk-check.md):
- the duplicated introduction paragraph;
- the internal process text (feasibility pass, "withdrawn", evidence-level wording);
- the strata explanation (584 of 615);
- the supplement pointers (author checks are now S11; the other S-numbers corrected);
- the criterion labels I1(a) and I1(b), now defined in Section 2.3.

Two items remain open:
- The 1,242 seed records outside the screened set are stated as the main threat to validity. Screening them would need a further screening round.
- ACM's authorship policy asks for AI used to conduct research to be described in the Methods section. At the author's instruction, AI is described only in the Declaration.
