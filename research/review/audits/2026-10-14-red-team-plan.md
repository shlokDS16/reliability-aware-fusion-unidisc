# Red-team review of the review plan (2026-10-14)

Saved by the orchestrator from the red-team agent's hand-back. The agent read all eleven named
artifacts and acted as the ACM Computing Surveys associate editor and as the most sceptical
referee. It was told to find problems only.

## Editor's decision: reject without review, as planned
The only content not already in arXiv 2508.10875 and 2506.13759 is a hypothesis-testing audit of
the field's evidence (RQ6, E1 to E3), which is new research that the journal's charter excludes as
a paper's main purpose. With the audit removed, what remains is a 10.5-page catalogue on the same
axes as those two surveys, by authors with no record in the area.

## Fatal
- **F1 Scope trap.** The charter says the journal "does not publish new research" and that
  exposing needed research is "not its major purpose" (`dossier/csur.md` sections 0 and 1). The
  plan is organised around claim evaluability with three pre-registered hypotheses. If the audit
  is made subordinate, nothing separates the paper from 2508.10875.
- **F2 The evaluability construct is neither reliable nor shown valid.** Criterion agreement 0.29
  then 0.33; both raters are language models; no human rating exists. Raters see abstract,
  captions and tables only, so "not evaluable" means "not in a table"; several items need facts
  papers put in setup text; figure-only results are frequent.
- **F3 No expert human reads the corpus.** Human effort is about 100 abstracts plus adjudication.
  Extraction, QA1 to QA9 and the rubric are model-on-model and produce negative judgements on
  named papers. ACM holds authors accountable. The artifacts already record wrong titles and a
  wrong venue from a search agent, a flag that fired on 534 of 535 pages, and inferred labels.

## Major
M1 E1 was written the day the pilots on the same corpus showed its direction; protocol unfrozen
and unregistered; up to 157 of 572 records already used in development. M2 E1's outcome is set by
author-chosen strictness thresholds, and types are dropped after the fact. M3 "claim
identification passed" is a pooling artefact: three of six types are under 0.60 and cells within a
paper are not independent. M4 E2 cannot be decided at a 10-point margin with 23 to 90 claims per
cell; peer-review status is confounded with age. M5 E3 is close to tautological (a headline is the
selected best case) and its only pilot data go the other way. M6 The quantitative synthesis is
empty (about 4 papers for steps, 1 to 2 for remasking, 3 mixed-sign for synergy, none for RQ2).
M7 The corpus is circular: seeded from the repository of the competing survey, recall tested
against it, samples stratified by its sections. M8 The multimodal half of the title has no
evidence base (28 seed records; hybrid unified models missing and covered by 2505.02567 with 403
references). M9 Database searches are planned, not done. M10 The gap claim against existing
surveys rests on keyword scans; 18 surveys undetermined, two of them peer-reviewed; 2506.13759
already calls itself a "systematic survey". M11 Insiders have already published evaluation
critiques with re-runs (2606.29228, 2609.33947, 2607.24763, 2606.19475, 2601.15593); a
table-reading count adds little. M12 It will read as an attack by outsiders. M13 The 35-page
budget is already full and has no room for the rubric, reliability tables or the AI-methods
description; coverage is 10.5 pages against 15 to 17 in exemplars. M14 Most included studies
cannot be cited within a 270-reference budget. M15 No integrating framework exists yet, though the
charter requires one. M16 The review will be stale on arrival (about 27 new records a month, 9 to
15 months to acceptance, no preprint, one attempt per 12 months). M17 Screening validation on a
near-all-include seed is unsound. M18 Plan documents contradict each other.

## Minor
m1 Search string S1 has ambiguous AND/OR precedence. m2 The 2506.13759 authors' own list is not a
source. m3 The 32 non-arXiv records are in no feasibility pass. m4 QA1 "usable" cannot be checked
for 500 repositories; QA1 to QA9 have had no reliability pilot. m5 The pilot script was edited
after the rules were frozen (before any result was seen; recorded in the pilot summary).

## Single missing element most likely to cause rejection
A human, domain-expert, full-text rating of a sample, including running text and figures, against
which the model raters and the table-only rubric are scored.

## What would withdraw each fatal finding
- F1: a written answer from the journal's editors that a survey carrying pre-specified hypotheses
  and a reporting audit is in scope; or a drafted taxonomy that classifies the corpus on axes
  shown, by a full read, to be absent from the two existing surveys.
- F2: on a fresh sample, per-type kappa of at least 0.60 for the evaluable flag, human against
  human and model against human, plus evidence that full-text reading overturns only a small
  share of table-only "not evaluable" verdicts.
- F3: a measured, low error rate of model extraction and appraisal against an expert human read,
  and a named author or adviser with discrete-diffusion expertise who has read the included studies.

Caveat from the agent: no official text on author expertise was found; that is a referee risk,
not a stated rule.
