---
agent: venue-intel
date: 2026-10-29
brief: Journal options for Paper 2 (preregistered NEGATIVE result on reliability-gated conditioning in UniDisc 1.4B, plus a correlated-token fusion theory); official pages only
sources_examined: [URLs per journal below, all accessed 2026-10-29]
coverage: >
  Read in full or by keyword extraction: Guide for Authors / Open-access pages (ScienceDirect, 5 Elsevier journals),
  TMLR editorial policies + acceptance criteria + author guide + accepted-papers page, JAIR submissions + formatting pages,
  Machine Learning (Springer) submission guidelines + aims and scope + journal home, IEEE CIS pages for TNNLS and TAI,
  IEEE Computer Society author-resources page, ACM TOMM author guidelines + ACM authorship/APC policy pages.
  NOT covered: reviewer-form text for any journal; Elsevier journal "insights" pages (time to first decision is not on the
  pages I could read); the current TPAMI information-for-authors page (JS-rendered, empty to my fetchers; limits below come
  from IEEE-hosted Information for Authors documents of 2021-2022); the current TMM information-for-authors page.
claims:
  - statement: No Elsevier journal in the candidate set (Information Fusion, Pattern Recognition, Neural Networks, Neurocomputing, Knowledge-Based Systems) is on Elsevier's Registered Reports participating-journals list
    status: supported
    evidence: https://www.elsevier.com/researcher/author/policies-and-guidelines/registered-reports (keyword check of the page text, 2026-10-29)
    level: E1
    confidence: 0.9
  - statement: None of the 13 journals states a policy for negative results or preregistered studies; TMLR and Machine Learning state criteria that do not require a positive result
    status: supported
    evidence: author guides listed per journal; keyword checks for negative / replication / preregist / registered
    level: E1
    confidence: 0.8
competing_explanations: []
unknowns:
  - Time to first decision for Information Fusion, PR, NN, KBS, Neurocomputing, TMLR, TNNLS, TPAMI (not officially stated on pages read)
  - Neurocomputing APC amount (page lists the option, no amount rendered)
  - Whether VIT Vellore participates in ACM Open (matters only for TOMM)
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
---

# Venue options for Paper 2 (journals), 2026-10-29

Evidence tags: **[OFFICIAL]** read on the journal or publisher page named; **[SUMMARY]** page text came back through a summarising
fetcher (WebFetch), so wording is paraphrase, check before relying; **[OLD DOC]** an older IEEE-hosted PDF/DOI copy of the
journal's information for authors, not the live page. "Not stated" means I looked and the page does not say.

## 0. What the venue has to carry

Paper 2 is a preregistered NEGATIVE measurement (net accuracy change within +/-0.05 under JPEG, noise and splice at n = 500; the
positive control not met; detector near chance on realistic corruptions) plus a correlated-token theory of when gating raises the
evidence SNR, plus an exploratory hard-gate vs robust-fusion vs soft-weighting comparison, with code and data released. Consequences
for venue choice:

1. The venue must accept "claims supported by the evidence, including a null" and must not demand a new method. Draft intro says
   "The paper proposes no new fusion rule".
2. Length: the current `paper2/main.pdf` is **73 pages** (preprint, 12 pt, single column) with **52 bibliography entries** and about
   24,400 words in `paper2/sections/*.tex`. I did not compile the 5p two-column layout, so the final Information Fusion page count is
   unknown. Information Fusion caps research articles at 35 pages and 50 references; the draft already has 52 references.
3. Shlok's rule (AI mentioned only in a "Declaration of generative AI use" section) fits some venues' rules and collides with others
   (flagged per journal).

## 1. Information Fusion (Elsevier) - current target

- URLs: https://www.sciencedirect.com/journal/information-fusion/publish/guide-for-authors ; open access
  https://www.sciencedirect.com/journal/information-fusion/publish/open-access-options ; AI policy
  https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals . Accessed 2026-10-29. [OFFICIAL]
- **Scope.** "Multi-sensor, multi-source information fusion"; lists multi-classifier/decision systems, decision fusion, "fusion learning in
  imperfect, imprecise and incomplete environments". Articles "expected to emphasize one or more of ... architectures, algorithms, and
  applications"; "fundamental theoretical analyses" welcome. Fit: topic is a direct match (source reliability, fault detection before
  fusion); the risk is that a null measurement with no new rule is neither of the three facets.
- **Negative/replication/registered reports:** not stated. Journal not on Elsevier's Registered Reports list. The submission declaration
  says prior publication as a "registered report" does not count against novelty.
- **Article types and limits.** Research article 10-35 pages including figures, tables, references, appendices, biosketches; **max 50
  references**. Survey up to 50 pages, 300 references. Limits apply "to the final formatted version using the journal template";
  non-compliance "may result in desk rejection". Abstract max 250 words; 1-7 keywords; 3-5 highlights; data statement required.
- **Template.** Elsevier `elsarticle` (LaTeX template mandatory for LaTeX submissions, source files required). The guide does not name a
  class option.
- **AI policy.** "Declaration of generative AI use" heading in the guide; disclosure statement required at submission; AI may not be an
  author; basic grammar/spelling tools exempt. Fits Shlok's rule exactly.
- **Open access.** Hybrid. Subscription route: no fee. Gold OA APC **USD 4,130** (excl. taxes; "personalized" price shown at submission).
  No-fee route exists (subscription).
- **Review model.** Single anonymized; at least two reviewers; editors decide. Time to first decision: not stated on pages read.
- **Impact indicators (official header, year not stated on page):** Impact Factor 17.4, CiteScore 26.7.
- **Overlap note.** Same authors' review paper is going to this journal; no rule forbids two papers, but one editor pool will see both.

## 2. Transactions on Machine Learning Research (TMLR)

- URLs: https://jmlr.org/tmlr/editorial-policies.html ; https://www.jmlr.org/tmlr/acceptance-criteria.html ;
  https://jmlr.org/tmlr/author-guide.html ; https://jmlr.org/tmlr/papers/ (certifications). Accessed 2026-10-29. [OFFICIAL; acceptance-criteria and
  author-guide text via SUMMARY, editorial-policies and certifications read verbatim]
- **Scope.** "Experimental and/or theoretical studies yielding new insight into the design and behavior of learning in intelligent systems",
  "reproducibility studies of previously published results or claims", new analysis/understanding approaches. Emphasises "technical
  correctness over subjective significance". Fit: good for a preregistered measurement plus theory; vision-language masked diffusion is plain ML.
- **Negative results / replication / preregistration:** no dedicated policy on negative results or preregistration. Acceptance rests on
  (1) whether claims are supported by accurate, convincing, clear evidence (authors may "narrow their claims" to meet this) and (2) whether some of the audience
  would be interested; works are not to be rejected for lacking significance, novelty or state-of-the-art numbers. This is the closest explicit
  statement of tolerance for a null among the 13 journals.
- **Length.** No page limit; very long main texts may delay review; appendix after references allowed; supplementary up to 100 MB (PDF/ZIP).
- **Template.** TMLR style file (`tmlr-style-file`), anonymized PDF.
- **AI policy.** LLMs usable as general-purpose assistive tools; authors responsible; LLMs cannot be authors; papers that look largely
  LLM-generated "will be closely examined". No disclosure section required. Compatible with Shlok's rule (a Declaration section is extra, not forbidden).
- **Cost.** None: no fees for authors, reviewers or editors; all content free to read. Fully no-fee.
- **Review model.** Double-blind, **open reviewing** (reviews and discussion public once a third review is in, or two at recommendation stage);
  action editor assigned within about a week; at least three reviewers; reviewers recommend after at least two weeks from the third review. No
  overall time to decision stated. A **rejected submission stays public on OpenReview** (anonymous unless authors reveal themselves, which bars resubmission).
- **Certifications (relevant to "best paper in the journal's history").** Featured (oral/spotlight equivalent), Reproducibility (for papers
  whose primary purpose is reproducing published work; ours is not), Outstanding ("equivalent to a best paper award at a top-tier conference",
  can be given a year or more after publication), J2C (NeurIPS/ICLR/ICML journal-to-conference track).
- **Originality rule.** No reuse of text, figures or results with any archival paper under submission elsewhere; arXiv preprints are fine.
- **Impact indicators:** none official on pages read.

## 3. Machine Learning (Springer)

- URLs: https://link.springer.com/journal/10994/submission-guidelines ; https://link.springer.com/journal/10994/aims-and-scope ;
  https://link.springer.com/journal/10994 . Accessed 2026-10-29. [OFFICIAL]
- **Scope.** Includes "issues of research methodology" ("research methodology papers improve how machine learning research is conducted"); claims
  must have solid empirical or theoretical support and "supporting evidence in ways that can be verified or replicated". Fit: good for the
  methodology/measurement side; masked-diffusion multimodal work is less typical for the journal.
- **Negative/replication/preregistration:** not stated. Each submission needs a 1-2 page **Contribution Information Sheet** (main claim and why it matters,
  evidence, closest work); "we are the first" is not accepted as importance; sheets judged uninformative are returned without review.
- **Length.** No page or reference limit found; abstract 150-250 words; 4-6 keywords.
- **Template.** Springer Nature LaTeX template (recommended; source files required); Word accepted.
- **AI policy.** LLM use "should be properly documented in the Methods section"; AI-assisted copy editing need not be declared. **Conflicts with
  Shlok's rule** if AI was used for code or analysis (Methods placement); a Declaration section alone would not satisfy it.
- **Cost.** No submission or publication fee; Open Choice OA optional with APC (amount per journal list, not read).
- **Review model.** Not stated on this page beyond editorial procedure. Journal home: median submission to first decision **5 days**
  (a median this short implies it is dominated by desk decisions; do not read it as time to reviews). Text says decisions typically in under three months.
- **Impact indicators (official, journal home):** Journal Impact Factor 4.9 (2025), 5-year 8.0 (2025).

## 4. Journal of Artificial Intelligence Research (JAIR)

- URLs: https://www.jair.org/index.php/jair/about/submissions ; https://www.jair.org/index.php/jair/formatting . Accessed 2026-10-29.
  [SUMMARY for submissions page; formatting page read]
- **Scope.** "All areas of AI"; must matter to the wider AI community or a well-established subcommunity; incremental work, known techniques
  without methodological insight, and summary-only surveys "likely to be rejected". Papers should focus on what was learned.
- **Negative/replication/preregistration:** not addressed; mandatory **reproducibility checklist**; a "Reproducibility Initiative" is mentioned, no details.
- **Types/length.** Full articles, research notes (very short), surveys, special tracks. No page limit; "be concise".
- **Template.** New JAIR style (ACM-based, since spring 2025; JAIR now appears in the ACM library); the template includes the checklist.
- **AI policy.** AI may assist with editing, language, idea generation or analysis; core contributions must be the authors'; AI cannot be an
  author or cited as a source. No separate disclosure section stated on the page. Compatible with Shlok's rule.
- **Cost.** None: no submission, publication or reader fee (funded by grants and donations).
- **Review model.** Decisions usually in about 8-12 weeks; reviewer identities confidential; one resubmission allowed; minor revisions due in two months.
- **Impact indicators:** none official on pages read.

## 5. Pattern Recognition (Elsevier)

- URLs: https://www.sciencedirect.com/journal/pattern-recognition/publish/guide-for-authors ; .../publish/open-access-options . Accessed 2026-10-29. [OFFICIAL]
- **Scope.** Original contributions to "theory, methodology and application of pattern recognition", provided the context is "grounded in the
  pattern recognition literature"; routine applications of known methods are redirected elsewhere. Fit: moderate (image-token fault
  detection and verification is recognisable, but a null on one pretrained model is not "methodology").
- **Negative/replication/preregistration:** not stated; not on Registered Reports list.
- **Length.** Single column, double spaced, **20 to 35 pages** (40 for a review), numbered pages. Minimum of 20 is binding. Abstract 250 words.
- **Template.** `elsarticle` (encouraged); source files required.
- **AI policy.** Same Elsevier "Declaration of generative AI use" as Information Fusion. Fits Shlok's rule.
- **Cost.** Subscription route no fee; OA APC **USD 3,120**.
- **Review model.** Single anonymized; at least two reviewers. Time to first decision not stated.
- **Impact (official header):** Impact Factor 9.1, CiteScore 17.3.
- **Overlap note.** First author's other paper targets Pattern Recognition (different topic): avoid two live submissions to one editorial office.

## 6. Neural Networks (Elsevier; INNS/APNNS/JNNS)

- URLs: https://www.sciencedirect.com/journal/neural-networks/publish/guide-for-authors ; .../open-access-options . Accessed 2026-10-29. [OFFICIAL]
- **Scope.** Learning systems, mathematical and computational analysis, cognitive science, neuroscience, engineering; "neural networks should be
  central to submissions". Five sections; the author must pick one (Learning Systems or Mathematical and Computational Analysis would apply).
- **Negative/replication/preregistration:** not stated. Letters to the Editor exist for disagreement with published papers (not applicable).
- **Types/length.** Articles (no page limit found), Letters (up to 2,500 words, 25 references, abstract 100 words, no major revision), reviews/tutorials.
- **Template.** `elsarticle`; source files required.
- **AI policy.** Same Elsevier declaration. Fits Shlok's rule.
- **Cost.** Subscription no fee; OA APC **USD 2,760**.
- **Review model.** Single anonymized, at least two reviewers; time not stated.
- **Impact (official header):** Impact Factor 7.2, CiteScore 10.9.

## 7. IEEE Transactions on Neural Networks and Learning Systems (TNNLS)

- URL: https://cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls . Accessed 2026-10-29. [OFFICIAL]
- **Scope.** Theory, design and applications of neural networks and related learning systems. Full Papers must be "novel contributions of
  archival nature"; "not of incremental nature, but ... a well-founded and conclusive treatment of a problem". A null measurement does not match this wording.
- **Negative/replication/preregistration:** not stated.
- **Types/length.** Full paper 10 pages, survey 15, brief 6; mandatory over-length charge USD 200/page beyond those; max 15 pages for a full
  paper (excluding supplementary material). Voluntary page charge USD 110/page (not obligatory). Papers are not moved between categories after submission.
- **Template.** IEEE article template (IEEE Author Center templates page, linked from the journal page); PDF, single-spaced double column.
- **AI policy.** AI-generated text must be disclosed in the **Acknowledgements section** with a citation to the AI system for the sections concerned.
  **Conflicts with Shlok's rule** (location is Acknowledgements, not a Declaration section).
- **Cost.** Hybrid. Traditional route has no APC (page charges may apply). OA APC **USD 2,800** for 2026 submissions (member discounts; low-income-country discount).
- **Review model.** "Double-anonymous" described on the page; at least two reviewers. Time not stated.
- **Overlap note.** First author's other paper targets TNNLS/TPAMI/PR.

## 8. IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)

- URLs: https://www.computer.org/publications/author-resources ; https://www.computer.org/digital-library/journals/tp/cfp-ieee-pattern-analysis-machine-intelligence ;
  https://doi.org/10.1109/tpami.2022.3202290 (Information for Authors). Accessed 2026-10-29. [OFFICIAL for the first two; **OLD DOC** for page limits]
- **Scope.** Computer vision, pattern analysis and recognition, "machine learning for pattern analysis". Fit: partial (vision-language tokens; no new method).
- **Negative/replication/preregistration:** not stated. The IEEE Computer Society page states only about 25 % of all submitted manuscripts are accepted.
- **Length.** Regular 12 double-column pages incl. references (2022 document; earlier 14); short 8; survey 20. Mandatory over-length charge USD 220/page
  beyond the regular limit (Computer Society policy). Verify current limit before any submission.
- **Template.** IEEE Computer Society journal template via IEEE Template Selector.
- **AI policy.** IEEE rule: disclose AI-generated text in Acknowledgements (see TNNLS). Conflicts with Shlok's rule.
- **Cost.** Hybrid; OA available, amount not read. **Review.** Single-anonymous by default, double-anonymous on request (Computer Society page); minimum of two (2022 document) to three reviewers.
- **Overlap note.** The other first-author paper targets TPAMI.

## 9. Neurocomputing (Elsevier)

- URLs: https://www.sciencedirect.com/journal/neurocomputing/publish/guide-for-authors ; .../open-access-options . Accessed 2026-10-29. [OFFICIAL]
- **Scope.** Neural networks and learning systems; "does NOT accept ... pure image processing or pure combination of existing algorithms" not relevant to learning systems.
- **Article types (7).** Regular, survey, tutorial/case study, **replication study** ("close, clear and valid replications of the original methodology"),
  software, special issue article, editorial preface. This is the only journal read that has a replication article type; our paper is not a replication of a
  published result, so it would go in as a Regular article.
- **Negative/preregistration:** not stated. Page limit not found. Template `elsarticle`. AI: Elsevier declaration. Fits Shlok's rule.
- **Cost.** Subscription no fee; OA option exists, **APC amount not shown** on the page I could read. **Review:** single anonymized, two reviewers, time not stated.
- **Impact (official header):** Impact Factor 6.7, CiteScore 10.8.

## 10. Screened out before full comparison

| Journal | Why dropped (official evidence) |
|---|---|
| Knowledge-Based Systems (Elsevier) https://www.sciencedirect.com/journal/knowledge-based-systems/publish/guide-for-authors | Preferably no more than 20 double-spaced pages, tables and figures included (short communication 10); scope is knowledge-based and AI systems with business/government applications; OA APC USD 3,240 (short articles USD 700); IF 8.0, CiteScore 13.7. Too short for this draft, weaker scope fit than IF or PR. |
| IEEE Transactions on Multimedia https://signalprocessingsociety.org/publications-resources/information-authors | Initial regular submission may not exceed 10 pages (revised 14), IEEE SPS page. Multimedia-systems scope; technical-contribution culture. [IEEE SPS generic page; TMM-specific current page not read] |
| ACM TOMM https://dl.acm.org/journal/tomm/author-guidelines | Two submission types only: technical contributions (regular) or surveys; regular limit 23 pages plus 5-page online appendix; double-anonymous; fully open access since 2026-01-01, 2026 subsidised APC USD 1,450 (USD 950 with an ACM/SIG member; lower-middle-income country half: USD 725 / 475; free if the institution is in ACM Open or the country is low-income; https://authors.acm.org/open-access/initiatives-services-authors-site). AI used in conducting research must be described in the Methods section (https://www.acm.org/publications/policies/new-acm-policy-on-authorship), which conflicts with Shlok's rule. Also already used for Paper 6. |
| IEEE Transactions on Artificial Intelligence https://cis.ieee.org/publications/ieee-transactions-on-artificial-intelligence/information-for-authors-tai | Regular 10 pages (+5 extra at USD 200/page, max 15); double-anonymous; asks for an Impact Statement and states papers "by default" offer significant novel contributions; OA USD 2,800. A null with no new method is a poor match; IEEE AI disclosure in Acknowledgements conflicts with Shlok's rule. |

## 11. Comparison matrix

| | Scope fit | Tolerates a preregistered null (stated) | Length headroom | AI rule vs Shlok's | No-fee route | Review | Official indicator |
|---|---|---|---|---|---|---|---|
| Information Fusion | Highest (decision fusion, imperfect data) | Not stated | 35 pp / 50 refs: tight (draft 73 pp, 52 refs) | Fits | Yes (subscription) | Single anon., 2+ reviewers | IF 17.4 |
| TMLR | High | Criteria do not need a positive result; not explicit on nulls | No limit | Compatible | Yes (no fees at all) | Double-blind, open, 3+ reviewers | none read |
| Machine Learning | Medium-high (methodology) | Not stated; information-sheet gate | No limit found | Conflicts (Methods) | Yes (no fee unless OA) | not stated | JIF 4.9 / 8.0 (5-yr) |
| JAIR | Medium-high | Not stated; "what was learned" | No limit | Compatible | Yes (no fees) | 8-12 weeks stated | none read |
| Pattern Recognition | Medium | Not stated | 20-35 pp | Fits | Yes | Single anon. | IF 9.1 |
| Neural Networks | Medium | Not stated | No limit found | Fits | Yes | Single anon. | IF 7.2 |
| Neurocomputing | Medium-low | Replication type only | Not found | Fits | Yes | Single anon. | IF 6.7 |
| TNNLS | Medium, wording against | Wording against ("conclusive", "not incremental") | 10 pp (15 max) | Conflicts | Yes (traditional) | Double-anon. | none read |
| TPAMI | Medium-low | Not stated; about 25 % accepted | 12 pp (old doc) | Conflicts | Hybrid | Single/double on request | none read |

## 12. Honest ranking for THIS paper

Ranking criteria in order: (a) the venue's stated criteria survive a null result; (b) the paper's contribution type is on the venue's list; (c) length and
format fit without destroying the preregistration detail; (d) policies that Shlok's rules already satisfy; (e) prestige signal, official only.

1. **TMLR.** Only venue whose published criteria are about evidence for the claims made, with explicit permission to narrow claims, and which
   says significance and state-of-the-art are not rejection grounds. No page cap (the 73-page draft, the preregistration trail and the audits can stay
   in main text or appendix), no fees, open reviewing suits a heavily preregistered paper, and the certification ladder (Featured, Outstanding, J2C)
   is the only mechanism read that lets this paper be marked as a best-paper-level article in the journal. Costs: no stated null policy; no official
   impact indicator; double-blind, so the code and data links (GitHub, Zenodo) and author identity must be anonymised for review; a rejection stays public
   on OpenReview.
2. **Information Fusion.** Best topical match and strongest official indicator, free via subscription, declaration section matches Shlok's rule, template
   already in use. Against: no stated tolerance for nulls; "architectures, algorithms, applications" framing while the paper "proposes no new fusion
   rule"; hard 35-page and 50-reference caps against a 73-page, 52-reference draft; same editorial office as the review paper.
3. **Machine Learning (Springer).** Aims and scope explicitly include research-methodology papers and require verifiable evidence; no length cap,
   no fee, JIF 4.9 (5-year 8.0). Against: the Contribution Information Sheet gate (needs a stated importance, not "first"); Methods-section AI
   documentation conflicts with Shlok's rule; less natural audience for multimodal masked diffusion.

Next: JAIR (4), Pattern Recognition (5), Neural Networks (6), Neurocomputing (7), TNNLS (8), TPAMI (9). JAIR is the closest alternative to place 3 (no fees, no limit,
rule-compatible); I put Machine Learning first only because its scope text names methodology explicitly and it publishes an official indicator.

**Recommendation: TMLR**, with Information Fusion as the fallback if Shlok prioritises the Impact Factor over fit. Submit to one venue at a time.
I would not choose Information Fusion first because the evidence on the page is silent about nulls while the length and reference caps would force cutting
the preregistration and audit material that is this paper's main strength.

## 13. Template URLs for the top 3 (nothing downloaded)

- TMLR: https://github.com/JmlrOrg/tmlr-style-file/archive/refs/heads/main.zip (URL given on the TMLR author guide); repository https://github.com/JmlrOrg/tmlr-style-file
- Information Fusion: `elsarticle` package https://assets.ctfassets.net/o78em1y1w4i4/4MpsJHO0MOJ2xZuwGTAbOZ/7bc64af36477c5d6cfce335a1f872363/elsarticle.zip ,
  documentation https://assets.ctfassets.net/o78em1y1w4i4/3ro3yQff1q67JHmLi1sAqV/1348e3852f277867230fc4b84a801734/elsdoc-1.pdf , from
  https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions (the project already uses `elsarticle`).
- Machine Learning: Springer Nature LaTeX template (December 2024 version) https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12 ;
  Overleaf https://www.overleaf.com/latex/templates/springer-nature-latex-template/gsvvftmrppwq ; from https://www.springernature.com/gp/authors/campaigns/latex-author-support
- For reference, JAIR Author Kit: https://www.jair.org/index.php/jair/libraryFiles/downloadPublic/6

## 14. Concerns and open items

1. Draft size versus Information Fusion caps: 73 preprint pages, 52 bibitems (limit 50 references, 35 pages including appendices). Not measured in the 5p layout.
2. Shlok's AI rule conflicts with Machine Learning, ACM and IEEE disclosure locations; Elsevier journals and TMLR/JAIR do not force a different location.
3. TMLR anonymisation and public rejection (see section 2).
4. Fetch limits: ScienceDirect reachable only through the browser pane; summarising fetcher used for three TMLR and JAIR pages; TPAMI limits are from older IEEE documents.
5. Elsevier registered-report check is keyword-based on the page text, not a manual read of the whole list.
