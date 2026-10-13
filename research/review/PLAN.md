# Paper 1: review article plan (v1, 2026-10-13)

Paper 1 is a review, written first. Paper 2 is the research article (plan at the end).

## 1. What a review demands (and what it does not)

Checked against ACM Computing Surveys' own referee instructions (dl.acm.org/journal/csur/reviewers):
a survey is judged on technical quality, relevance, general interest and presentation. The journal
"does not accept papers primarily devoted to presentation of new technical results", but a paper
that is primarily a survey and "include[s] a new result to organize and convey the material in a
better way" is in scope.

| A research paper is judged on | A review is judged on |
|---|---|
| a new method or finding | **coverage**: nothing important missing, no cherry-picking |
| experiments that could fail | **organisation**: a taxonomy that makes the field easier to think about |
| baselines and ablations | **synthesis**: what the body of work shows collectively, where papers disagree |
| reproducible runs | **critical assessment**: which claims are well supported and which are not |
| | **outlook**: open problems stated precisely enough to work on |
| | **method transparency**: how papers were found and selected |

So: **no model training is needed**, and none would help acceptance. What takes the time is
reading. The rigour moves from GPU runs to (a) a documented search and selection protocol,
(b) accurate extraction of what each paper reports, and (c) honest statistics over those reports.

Two cautions on the brief:
- "Reviews are easier to accept" does not hold at the top. The target is ranked 1 of 146 in its
  category, and a rejected paper reportedly cannot be resubmitted for 12 months (to confirm). There
  is one attempt.
- A conjecture in a review can be **supported**, not proven. Wording will be "we conjecture ...;
  the published evidence is consistent with it in N of M comparisons; these observations would
  refute it". Calling it validated would be the first thing a referee strikes.

## 2. Target journal

| Rank | Journal | 2025 JIF | Format | Cost | Status |
|---|---|---|---|---|---|
| 1 | **ACM Computing Surveys** | 30.4, rank 1/146 | long survey, 35 pages including references, plus electronic supplement | fully OA since 2026; APC reported as 1,450 USD (lower for lower-middle-income countries), to confirm | JIF, page limit and scope from official pages |
| 2 | IEEE TPAMI (survey) | 20.4 | regular paper | free route exists | JIF from a third-party page |
| 3 | Artificial Intelligence Review or Information Fusion | not verified | | APC | to be checked by venue-intel |

Not chosen: a Nature Machine Intelligence Review or Perspective (3,000 to 4,000 words, at most 100
references, "minimal new supporting data", no presubmission enquiries). That format cannot hold a
systematic review with a meta-analysis.

## 3. What makes this review different from the two that exist

"A Survey on Diffusion Language Models" (arXiv 2508.10875, the Awesome-DLMs authors) and "Discrete
Diffusion in Large Language and Multimodal Models: A Survey" (arXiv 2506.13759, to verify) are
narrative taxonomies. A third one of the same kind would be rejected as redundant. Ours differs on
four counts, each of which the project's ledgers already support:

1. **Systematic protocol** (PRISMA 2020 style): registered search strings, databases, inclusion
   rules, a flow diagram, dual screening (Claude agent plus Codex, disagreements adjudicated).
2. **Quantitative synthesis**: every included paper's reported numbers, protocols and compute go
   into the claims ledger; the review reports meta-analytic estimates, not "X et al. improve".
3. **Reporting audit**: what share of papers report seeds, intervals, compute-matched baselines,
   released code, and a claim that matches their own tables (MMaDA's Table 4 is the seed example).
4. **One organising conjecture**, stated formally, with its supporting and refuting evidence.

## 4. Conjecture candidates (all E0 until audited and debated)

- **CA, conditional synergy (lead).** In unified understanding-and-generation models, cross-task
  benefit is not a consequence of unification. It appears only when both tasks read and write one
  visual token space under one likelihood, it is bounded by the information rate of that
  tokenisation, and at matched scale models with decoupled visual pathways are not worse. Test
  without training: meta-regression of published understanding and generation scores on design
  factors across all unified models found, controlling for backbone size and data; plus a census
  of how many synergy claims rest on a task-removal ablation. Paper 2 then tests CA causally.
- **CB, commitment trilemma.** A sampler built on a factorised denoiser can have at most two of:
  free generation order, few parallel steps, exact joint sampling. Test: published speed and
  quality numbers collapse onto one frontier when re-expressed per function evaluation per token;
  exact computation on small synthetic distributions (minutes of CPU, no training).
- **CC, fallback without a conjecture.** The reporting audit alone as the organising result.

Selection: novelty-auditor plus a recorded Claude-Codex debate (`tools/debate.py`), then your
approval.

**Title and journal approved by the professor on 2026-10-13 (D0006):**

> **Diffusion Language Models and Unified Multimodal Generation: A Systematic Review and
> Meta-Analysis** (ACM Computing Surveys)

The title commits the paper to a real meta-analysis. After Codex round 2 (accepted): the unit of
analysis is the **matched within-paper contrast** (an ablation or controlled comparison inside one
paper), pooled across papers; cross-paper regression of raw scores is descriptive only. CA is
split into separately testable parts and worded as a conjecture. CB is parked until it has formal
definitions.

## 5. How the agents become competent ("training")

Subagents cannot be trained; they start empty each time. What can be built is the material an
expert would have absorbed, kept as files and named in every brief:

| Pack | Built by | From | Used by |
|---|---|---|---|
| `dossier/csur.md` | venue-intel | author guidelines, editorial charter, referee instructions, authorship and AI policy | everyone who writes or reviews |
| `dossier/exemplar-anatomy.md` | venue-intel, paper-reader | 5 to 6 recent highly cited CSUR surveys read in full: section map, page budget, taxonomy figure, comparison tables, how gaps and open problems are argued | manuscript-writer, figure-smith, red-team |
| `dossier/domain-primer.md` | paper-reader | the 15 to 20 foundational papers, equations in one notation | every reading agent |
| `protocol.md` | experiment-designer, statistician | PRISMA 2020, meta-analysis plan | lit-scout, statistician, gate-auditor |
| referee simulation | red-team, Codex | CSUR referee form | applied to every draft |

An agent is treated as competent on a task only after it passes a check on it: reading agents are
scored on two papers whose extraction the orchestrator has verified by hand.

## 6. Pipeline and gates

| Gate | Work | Output |
|---|---|---|
| R0 | journal dossier, survey landscape, protocol frozen | `dossier/`, `survey-landscape.md`, `protocol.md` |
| R1 | search and screening: Awesome-DLMs links, arXiv, OpenReview, Semantic Scholar, OpenAlex, citation snowballing; dual screening | papers ledger with include or exclude reason; PRISMA counts |
| R2 | full-text extraction in batches of 3 agents | claims ledger; extraction accuracy check on a 10 percent sample |
| R3 | taxonomy, conjecture selection (debate), meta-analysis and reporting audit | `analysis/`, figures from scripts |
| R4 | drafting in the ACM template, staged algorithms, equations in one notation | `paper/review/` |
| R5 | clarity edit, reference validation, referee simulation by red-team and Codex, number audit | audit files |
| R6 | submission package and cover letter | your approval |

Display items, revised after the dossier (`dossier/exemplar-anatomy.md`): recent surveys in the
journal carry 3 to 7 figures, 3 to 7 tables and no algorithms, and references take about a quarter
of the pages. Main text: **6 to 7 figures and 5 to 6 tables** (taxonomy, PRISMA flow, unifying
formalism, forest plot of matched contrasts, reporting-audit heatmap, design-space map, open
problems) and at most two short algorithms giving the canonical training and sampling procedures in
one notation. The remaining figures, to reach the 13 to 14 requested, the staged algorithm
build-up, the full extraction tables and the search protocol go in the **electronic supplement**,
which is published with the article. Hard limit 35 pages including references.

Corpus seed (done 2026-10-13): `tools/ingest_awesome.py` parsed VILA-Lab/Awesome-DLMs at commit
194aa6bd (2026-10-02) into `corpus/awesome-dlms@194aa6bd.jsonl`: 572 unique works, 540 with arXiv
IDs, 245 with code. This is one source. A curated list reflects its curators' choices, so database
searches and citation snowballing are still required, and the repo's own survey (arXiv 2508.10875)
is the main work ours must differ from.

Estimated effort: 150 to 250 papers at full text is the bulk. That is roughly 60 to 80 agent
batches, more than one weekly token window; three to four weeks is realistic, two is not.

## 7. Integrity
ACM's authorship policy (updated 2026-05-14, see `dossier/csur.md`) requires the Methods section
to describe in detail any AI used to conduct the research. Screening, extraction, analysis code
and figures here are AI-assisted, so the protocol section will state exactly which steps used
which model, how each was checked by a human or a second model, and the measured agreement.
arXiv's cs category has refused surveys that are not yet accepted since 2025-10-31, so there is no
preprint before acceptance. VIT Vellore is on the ACM Open list, so the publication charge is
probably zero if the corresponding author is at VIT (to confirm with the library). A rejection
bars resubmission for 12 months.
The clarity pass uses `research-humanizer`; `hidden-unicode` only strips stray invisible
characters from our own files. Nothing is done to defeat detectors. Every citation is verified
against Crossref or arXiv, because fabricated references are the usual reason machine-assisted
surveys are rejected.

## Paper 2: research article (after Paper 1)

- **Journal:** Nature Machine Intelligence (JIF 29.8), then IEEE TPAMI (decision D0004).
- **Relation to Paper 1:** allowed and common. The review states the conjecture and its
  meta-analytic support; the research article tests it with interventions. No text, figure or
  result is reused, and the article cites the review.
- **Working title if the lead result holds:** "Shared features causally couple understanding and
  generation in unified multimodal diffusion models".
- **Datasets, open:** POPE, GQA, VQAv2, MMMU, MMBench or MME (understanding); GenEval, WISE,
  DPG-Bench (generation); CLEVR and synthetic probes (controls). **Restricted, optional:**
  MIMIC-CXR on PhysioNet for a real-world domain check; training corpora of the studied models if
  the memorisation backup is used. Final list after the review's extraction shows what each model
  was trained and evaluated on.
- **Compute:** frozen checkpoints on the 12 GB GPU; rented GPU time for full-precision confirmation.
