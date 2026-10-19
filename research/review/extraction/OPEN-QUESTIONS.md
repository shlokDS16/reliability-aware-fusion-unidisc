# Open questions for the human author: extraction and appraisal form v0.1 (2026-10-20)

Each item names where the protocol, the decision ledger or the framework is ambiguous or in conflict, the
options, and a recommendation. Items marked **decision row** change or narrow the protocol and need a row
in `research/ledgers/decisions.jsonl` (and, where noted, a protocol s10 amendment) before the pilot.
Nothing here was decided by the drafting agent; the form implements the recommendation provisionally so
the pilot can test it.

## A. Scope and protocol status

**OQ-01 Which studies get the full form (decision row).**
Conflict: protocol s5 extracts "per study" (every included study). `research/progress.md` records a user
decision of 2026-10-16: "full-text screen ALL records, extract RQ data on a stratified sample + all
multimodal". It is not in the decision ledger.
Options: (a) full form on every included study (protocol as written); (b) blocks S, D, F, claims and QA on
every study, and the unit blocks H and K on a stratified random sample plus every study with i1 b or ab,
with sampling weights in the RQ2-RQ5 synthesis; (c) the whole form on a sample only.
Recommendation: (b). RQ1, RQ6, the design-space counts and the census extension need every study, and
those blocks are the cheaper part; units are the expensive part. Fix strata, sample size and seed after the
pilot has measured cost per study and before any production row; state in the paper that RQ2-RQ5 counts are
sample estimates. Option (c) would make RQ6 a sample estimate too, against s6 ("every included study").

**OQ-02 Hypotheses E1-E3 and the evaluability paragraph (decision row and s10 amendment).**
Conflict: protocol s6 still describes claim evaluability and hypotheses E1-E3 as part of the appraisal;
D0008 suspended them and D0009 kept them suspended, but protocol s10 has no amendment saying so (only
OUTLINE.md row 2.10 notes it). The form therefore omits every evaluability field.
Options: (a) add a s10 amendment recording the suspension and that the extraction form has no
evaluability field; (b) reinstate them with a rubric v0.3 and a fresh reliability round (the statistician's
audit put validation at about 160 papers); (c) withdraw them for good.
Recommendation: (a) now. Also record that the H and K units would allow a headline-versus-controlled
comparison like hypothesis E3; while D0008 stands such an analysis is not run, or is run only as a
descriptive count under its own decision row.

**OQ-03 Claim-type coding CT1-CT6 (rubric v0.2 step 1).**
Ambiguity: protocol s5 asks for "claims made in the abstract"; rubric v0.2 step 1 passed its line pooled
(kappa 0.71) but by type CT5 unification was 0.00 and CT3 and CT6 were 0.53 (`reliability/RESULTS.md`), and
the rubric belongs to the suspended theme.
Options: (a) keep all six, descriptive, and publish counts only for types that reach kappa 0.60 in the
production second reading; (b) keep only CT1, CT2, CT4; (c) drop CT and keep only the claim list used for
QA8.
Recommendation: (a). It mirrors next step 3 of RESULTS.md and loses nothing if a type fails.

**OQ-04 What "verified by a second reader" means (decision row).**
Ambiguity: protocol s5 says extraction is "verified by a second reader"; it does not say whether the reader
checks the first record or extracts independently.
Options: (a) independent double extraction, blind, then compare; (b) verification of the first record field
by field.
Recommendation: (a). A reader who sees the first record anchors on it, so (b) overstates accuracy;
unit omissions are also invisible to a verifier. Cost: one more extraction on the sample.

**OQ-05 Who adjudicates extraction disagreements.**
Gap: the protocol names no adjudicator for extraction. D0034 shows the human author had no time for the
108-record screening validation; the screening harness uses claude-fable-5-1 (Route F, first line of
`analysis/screening/c-run-log.jsonl`, which records no extra spend on 2026-10-16).
Options: (a) claude-fable-5-1 as EC, the human author only for what EC lists as unresolved; (b) the human
author adjudicates everything; (c) no adjudication, disagreements reported.
Recommendation: (a), after the user re-confirms that Fable still draws no extra spend (the 2026-10-16
statement may be out of date). See OQ-22 for a minimal human check.

**OQ-06 "Every within-paper contrast" narrowed (decision row).**
Conflict: protocol s5 asks for every within-paper contrast. The form records contrasts in the RQ2-RQ5
classes plus every ablation of the credited component, and skips optimisation-hyperparameter tuning not
presented as an ablation.
Options: (a) narrow as drafted; (b) every contrast (the stage-two inventory recorded 623 contrast rows from
29 papers of one 30-paper stratum, `feasibility/stage2/summary-steps.md`).
Recommendation: (a). Contrasts outside RQ2-RQ5 feed no synthesis, and each one costs quotes and second
reading.

**OQ-07 Definition of a "headline number".**
Ambiguity: protocol s5 says "every reported headline number" without defining headline.
Options: (a) abstract numbers only; (b) abstract numbers plus every cell of the final method's default row
in each main results table (drafted); (c) every cell of every table.
Recommendation: (b), with the pilot's workload check (median at most 40 H units per study, s10.4 P8).

## B. Categories

**OQ-08 Task-family categories (protocol s5 list is fixed).**
Gaps: common tasks fit none of {language modelling, reasoning, code, understanding, text-to-image, editing,
other} cleanly: instruction following and chat benchmarks, translation, summarisation, image captioning,
knowledge multiple-choice (MMLU-type), text infilling; and "editing" does not say image or text.
Options: (a) keep the seven, with the brief's reading: captioning and knowledge multiple-choice under
understanding, editing = image or other-modality editing, everything else under other with task_other
naming it; (b) add "instruction following" and "conditional text generation" (deviation).
Recommendation: (a). Units record the benchmark name, so "other" can be split later without re-extraction
if a decision adds categories.

**OQ-09 State-space edge cases.**
Ambiguity: protocol s5's six classes do not say how to code (i) unified models whose text is
autoregressive and whose image component is a continuous diffusion or flow (eligible under D0020);
(ii) mixtures of mask and uniform noise; (iii) simplex or logit diffusion; (iv) analysis papers covering
several models.
Options for (i): continuous-latent with text_generator = autoregressive (drafted) or hybrid. For (ii):
discrete-uniform (drafted), discrete-absorbing, or hybrid. For (iii): continuous-embedding (drafted).
For (iv): a list (drafted) or the first model only.
Recommendation: as drafted; hybrid is kept for models with diffusion components in two state spaces,
because S03 and D01 already carry the autoregressive and mixture details.

**OQ-10 Study type as one value.**
Ambiguity: a method paper that also releases a benchmark, or a caching paper (system or method).
Options: (a) one value, first listed contribution decides, exact output-preserving engineering = system
(drafted); (b) multiple values.
Recommendation: (a), because the protocol lists fixed single categories for tables.

**OQ-21 The 12 nonlang_only includes.**
Gap: these are eligible only through criteria v1.6 R14 (a text-pretrained diffusion model used on
non-language strings) and are "reported separately" (D0032 item 3); the form's text-oriented fields fit
them loosely.
Options: (a) extract fully, modality text, text_generator none, task family other, reported in a separate
row of every table; (b) study-level fields only.
Recommendation: (a).

## C. Quality appraisal

**OQ-11 QA1 "usable" and QA2 "weights or data" cannot be read the same way offline.**
Ambiguity: extractor sessions have no web access, so a repository's existence and its releases cannot be
checked (QA1 "usable"); QA2 says "weights or data needed", which can be read as either or both.
Options for QA1: (a) score from the paper text, with a later web link check filling sub-item d and both
scores reported (drafted); (b) text only; (c) a web pass by every extractor (breaks isolation).
For QA2: (a) both weights and data needed for 2 (drafted); (b) either suffices.
Recommendation: QA1 (a), the link check run once by the orchestrator with a date and logged as evidence
level E1; QA2 (a), because reproducing a trained model's result needs both.

**OQ-12 NA scores for QA6 and QA7 (decision row).**
Conflict: protocol s6 scores 0, 1, 2 only. A theory paper has no main comparison (QA6) and a benchmark or
analysis paper has no credited component (QA7).
Options: (a) NA, excluded from that item's distribution and counted separately (drafted); (b) 0.
Recommendation: (a); scoring 0 would make theory and benchmark papers look less rigorous for a reason
that is not about rigour.

**OQ-13 Anchors and sub-item scoring are new.**
Gap: protocol s6 gives one criterion line per item. The form adds 0/1/2 anchors and computes scores from
yes/no sub-items (lesson of rubric v0.2). Points that need the authors' approval: QA3 gives hardware the
same weight as steps and sampler; QA4 requires three runs for 2; QA8 includes the introduction's
contribution list, not only the abstract (protocol says "abstract and introduction claims"); "main
comparison" is defined by the first comparative claim of the abstract.
Recommendation: approve as drafted or edit before the pilot; after the pilot only failing items change.

**OQ-14 Two raters for the appraisal of every study, or 10 percent (decision row).**
Conflict: protocol s6 says "Appraisal by two raters as in section 4, weighted kappa reported" (both raters
on every study, and by s4 a human validation sample), while s5 puts the second reader on 10 percent plus
pooled studies.
Options: (a) a second model rater does the QA block of every included study (about one more reading per
study, QA only) and the 10 percent sample gets the full form; (b) QA second rating on the 10 percent sample
only, kappa reported there; (c) (a) plus a human rater on a 15 percent sample, as s4 asks for screening.
Recommendation: (a) if the pilot's cost allows; otherwise (b) with a decision row. (c) is what the
protocol implies, but D0034 shows the human time is not available; if (c) is not done, state it as a
deviation the way D0034 does.

## D. Census, pilot and reporting

**OQ-15 Census coding of studies already in the random census sample.**
Ambiguity: D0020 item 2 says v1.2 governs the "future full-corpus coding". Some included studies are among
the 176 random-sample ranks already coded and adjudicated (`census/census-random-final.jsonl`). The
existing result is on the title/abstract-passed pool; the extension is on full-text includes, a different
population.
Options: (a) code every included study fresh and blind, report agreement with the earlier final rows as a
test-retest check, keep the random-sample result as published and add the included-set census as a second
table; (b) import the adjudicated rows for those studies.
Recommendation: (a). Importing would mix two codings and two populations.

**OQ-16 Pilot composition.**
Issue: a simple random sample of 12 from the 608 T1 includes (53 with i1 b or ab) contains no multimodal
study with probability 0.33 (hypergeometric, computed 2026-10-20), so D03, D06, D09 and the RQ5 classes may
go untested.
Options: (a) accept; (b) if the sample has no i1 b or ab study, add 2 drawn with the same seed from that
stratum, extracted by both extractors but reported outside the agreement metrics; (c) stratify the pilot.
Recommendation: (b). The brief asked for a simple random sample; (b) keeps it intact.

**OQ-17 Which version of a paper is extracted.**
Conflict: protocol s3 ("Version rated") says the latest arXiv version available on the retrieval date;
extraction uses the same PyMuPDF text that full-text screening read (the open-access PDF in
`research/review/fulltext/fetch-log.jsonl`), which may be an older arXiv version or a published version.
Options: (a) extract from the screened file and record its version (drafted); (b) fetch the latest arXiv
version for extraction.
Recommendation: (a), so screening and extraction read the same text; where a number enters a pooled
estimate and the versions differ, the latest version is checked, as s3 already provides for published
versions.

**OQ-18 "Independent groups" for the pooling threshold.**
Gap: protocol s7 needs contrasts "from at least 5 independent groups"; no definition exists.
Options: (a) same group if the studies share the last author or a named lab; (b) same institution;
(c) also same base checkpoint.
Recommendation: the statistician fixes the rule before any pooling; the form records affiliations (S11),
base checkpoints (S08) and, through metadata, authors, so every option stays computable.

**OQ-19 Freezing the form while the protocol is not frozen.**
Gap: the protocol is DRAFT v0.1 with no `protocol-v1` tag, though its freeze rule ("before any screening
decision") has passed.
Options: (a) freeze the form at v1.0 after the pilot with a git tag, the SHA-256 of brief and schema in a
decision row, and a protocol s10 amendment that cites it; (b) freeze the protocol first.
Recommendation: (a), and ask the professor whether the protocol should now be frozen as amended.

**OQ-20 Pilot thresholds.**
Gap: P1 to P8 (EXTRACTION-PLAN s10.4) are new. The kappa lines reuse the protocol's (0.70 in s4, 0.60 in s6
and the rubric); unit-identification and workload lines have no precedent.
Recommendation: approve before the pilot; they must not change after the first pilot row.

**OQ-22 Minimum human reading.**
Issue: D0008 cited "no expert human reading" as a fatal weakness and proposed fixing a minimum of human
author reading; the form as drafted needs the human author only for EC's unresolved list.
Options: (a) the human author checks 2 random pilot records against the PDF (about one hour) and the
production 10 percent sample's adjudications by spot check; (b) none.
Recommendation: (a), recorded with an attestation of the files opened, as human adjudication sessions are
under criteria v1.6 section F.

**OQ-23 Model family of the second reader.**
Issue: EA, EB/ER and EC are all Claude models (D0015, D0021 note this as weaker independence). Codex is
unavailable until 2026-11-10 (D0015).
Options: (a) Claude models now, stated as a limit; (b) wait for Codex as the second reader; (c) Claude now,
and if time allows re-run the 10 percent agreement sample with Codex after 2026-11-10 as a sensitivity check.
Recommendation: (c), given the two-week horizon in D0010.

## Draft decision rows (for the orchestrator to enter after the author answers; not entered)

- Extraction scope (OQ-01), with strata, sample size and seed.
- Evaluability suspension amendment to protocol s10 (OQ-02).
- Second reading by independent double extraction (OQ-04) and adjudicator route (OQ-05).
- Contrast and headline definitions (OQ-06, OQ-07).
- QA anchors, NA rule and dual-rating scope (OQ-12, OQ-13, OQ-14).
- Form v1.0 freeze with hashes (OQ-19) and pilot thresholds (OQ-20).
