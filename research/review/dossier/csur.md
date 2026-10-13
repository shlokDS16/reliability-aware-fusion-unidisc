```yaml
agent: venue-intel
date: 2026-10-13
brief: Journal dossier on ACM Computing Surveys (CSUR) for the planned systematic review of diffusion language models and unified multimodal diffusion models (Part A)
sources_examined:
  - https://dl.acm.org/journal/csur  (home; JIF line, announcements)
  - https://dl.acm.org/journal/csur/author-guidelines
  - https://dl.acm.org/journal/csur/editorial-charter
  - https://dl.acm.org/journal/csur/reviewers
  - https://www.acm.org/publications/authors/submissions
  - https://www.acm.org/publications/policies/new-acm-policy-on-authorship  (updated May 14, 2026)
  - https://www.acm.org/publications/policies/frequently-asked-questions  (authorship FAQ)
  - https://www.acm.org/publications/policies/pre-publication-evaluation
  - https://www.acm.org/publications/policies/peer-review  (search extract only)
  - https://www.acm.org/publications/openaccess
  - https://libraries.acm.org/acmopen/apc-list-pricing
  - https://www.acm.org/publications/policies/policy-on-geographic-apc-waivers-and-discounts
  - https://www.acm.org/publications/policies/waiver-countries
  - https://www.acm.org/publications/policies/policy-on-discretionary-open-access-apc-waivers  (search extract only)
  - https://libraries.acm.org/acmopen/open-participants  (saved: research/sources/md/acm-open-participants-2026-10-13.txt)
  - https://authors.acm.org/author-resources/author-rights
  - https://blog.arxiv.org/2025/10/31/attention-authors-updated-practice-for-review-articles-and-position-papers-in-arxiv-cs-category/  (search extract only)
  - https://link.springer.com/journal/10462  (+ /submission-guidelines first ~9k chars, /how-to-publish-with-us extract)
  - https://www.sciencedirect.com/journal/information-fusion  (+ /publish/guide-for-authors, /about/insights, /publish/open-access-options)
  - CTAN acmart.zip (template), https://api.crossref.org (page counts, used in Part B)
coverage: >
  Official CSUR author-guidelines, editorial charter, reviewers page and the ACM authorship policy and FAQ were read in full
  (page text, via the Exa fetch tool; direct curl to acm.org and libraries.acm.org is blocked by a Cloudflare challenge,
  HTTP 403). NOT covered: dl.acm.org/journal/csur/about (fetch timed out), ACM Peer Review Policy full text, the
  discretionary-waiver policy full text, the arXiv blog post full text (search extract only, but it quotes the rule
  completely), the full Springer AIR submission-guidelines page (first ~9,000 characters only), ACM Open contract terms.
claims:
  - statement: CSUR 2025 JIF is 30.4, rank 1/146 in Computer Science Theory and Methods
    status: supported
    evidence: https://dl.acm.org/journal/csur (home page line, read 2026-10-13)
    level: E2
    confidence: 0.95
  - statement: Long survey limit is 35 pages including references in the Surveys style, with extra material allowed in an electronic supplement if the manuscript marks which pages form the 35
    status: supported
    evidence: author-guidelines, section "Paper Length"
    level: E2
    confidence: 0.95
  - statement: Papers rejected by CSUR cannot be resubmitted to the journal for 12 months after the rejection date
    status: supported
    evidence: author-guidelines, section "How to Submit" (NOTE sentence)
    level: E2
    confidence: 0.95
  - statement: ACM no longer requires disclosure of AI used to help write a paper, but requires a detailed description in the Methods section of any AI used to conduct the research (data collection, analysis, coding, figures)
    status: supported
    evidence: ACM Policy on Authorship (updated May 14, 2026), section "Use of Artificial Intelligence"; authorship FAQ
    level: E2
    confidence: 0.95
  - statement: VIT University Vellore appears in the ACM Open participant list (India block) on 2026-10-13
    status: supported
    evidence: libraries.acm.org/acmopen/open-participants, saved copy research/sources/md/acm-open-participants-2026-10-13.txt line 1604
    level: E2
    confidence: 0.85
  - statement: India is in the World Bank lower-middle-income 50 percent APC discount column of ACM's waiver country list
    status: supported
    evidence: https://www.acm.org/publications/policies/waiver-countries (row India)
    level: E2
    confidence: 0.9
  - statement: arXiv cs no longer accepts review, survey or position papers unless already accepted after peer review at a journal or conference (blog dated 2025-10-31)
    status: supported
    evidence: arXiv blog post, 2025-10-31
    level: E1
    confidence: 0.9
  - statement: A CSUR-specific first-decision time is not published by ACM; ACM-wide target is at most 90 days on average per review cycle
    status: supported
    evidence: https://www.acm.org/publications/policies/pre-publication-evaluation; author-guidelines (no figure)
    level: E2
    confidence: 0.85
  - statement: The 35-page limit is not a good predictor of published length; 6 of 7 CSUR surveys from 2024 to 2026 checked had 37 to 53 pages in the DL page range
    status: supported
    evidence: Crossref page fields (see Part B, exemplar-anatomy.md) plus two DL pages (39 and 41 pp)
    level: E1
    confidence: 0.8
competing_explanations:
  - The long published page counts may include an editor-approved electronic supplement or appendix that the DL page range counts, or may reflect editorial exceptions; ACM publishes no rule on how often the limit is waived.
unknowns:
  - Whether the 12-month bar applies to the referee outcome "reject but encourage resubmission after revision" (not stated; ask csur.admin@acm.org).
  - Whether ACM Open coverage applies to this paper (depends on the corresponding author's affiliation at eRights time and on the paper being APC-eligible).
  - Whether Information Fusion accepts unsolicited surveys (scope text says invited reviews; article-type table lists survey articles).
  - Information Fusion APC: 4,130 USD on two pages, 4,740 USD on the Journal Insights page, same day.
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# ACM Computing Surveys (CSUR): journal dossier

Prepared 2026-10-13. Tags: **[OFF]** read on an official ACM, Springer or Elsevier page; **[E1]** non-official page or
search snippet; **[INF]** inference by this agent. Quotes are kept to short fragments; the exact text sits at the URL
named in each item. All dates are as shown on the page on the access date.

## 0. What the project must do differently because of this dossier

| # | Finding | Consequence |
|---|---|---|
| 1 | arXiv cs now refuses survey/review papers that have not passed peer review (item 6) | No arXiv preprint before acceptance. Priority needs another route (item 6). |
| 2 | ACM's AI policy (updated 2026-05-14) requires the *Methods section* to describe AI used to conduct the research; AI used only for writing need not be disclosed (item 3) | PLAN section 7 ("AI assistance is declared") is too broad on one side and too narrow on the other: the agent screening, extraction and analysis pipeline must be described in detail in Methods. |
| 3 | The 12-month resubmission bar is confirmed (item 5) | One attempt, as the plan says. |
| 4 | APC: probably 0 USD if the corresponding author is at VIT (ACM Open); otherwise 725 USD (2026, non-member, India discount) or 900 USD (2027 list, India discount) (item 4) | Cost is not a constraint. Timing could matter only if VIT is not the corresponding affiliation. |
| 5 | Published CSUR surveys are usually longer than 35 pages (Part B), but the stated limit is 35 including references, and excessive length "may be rejected without review" (item 2) | Plan for 35 including references, with a marked electronic supplement. Do not rely on an exception. |
| 6 | The Charter says CSUR does not publish new research; the referee page allows a survey that includes a new result to organise the material (item 1) | Keep the meta-analysis subordinate to the survey. Framing matters more than statistics. |
| 7 | The 100-word abstract rule is in the guidelines but not followed in published abstracts (item 2) | Write a 100-word abstract. |

## 1. Editorial charter [OFF]

Source: https://dl.acm.org/journal/csur/editorial-charter ; https://dl.acm.org/journal/csur/author-guidelines (section
"Types of Papers") ; https://dl.acm.org/journal/csur/reviewers.

**Definitions.**
- *Survey* (Charter): assumes general knowledge of the area; emphasises "classification of the existing literature,
  developing a perspective on the area, and evaluating trends".
- *Tutorial* (Charter): assumes an inexpert audience; emphasises basic concepts with concrete examples.
- *Long Survey Paper* (guidelines): summarises and organises recent research "in a novel way that integrates and adds
  understanding"; limit 35 pages including references in the Surveys style.
- *Short Survey* (guidelines): a perspective piece or essay by a leader in the field, a personal point of view; limit 15
  pages including references. Not our type.
- *Tutorial Paper* (guidelines): organises and introduces work for an inexpert audience.

**What the Charter demands of every paper.** Both surveys and tutorials "must develop a framework or overall view of an
area that integrates the existing literature". The test question the Charter gives is what is currently known about the
area and what it means to researchers and practitioners. The paper should let new researchers enter the area, current
researchers continue, and practitioners apply the results. Exposing needed research is described as frequent but "not
its major purpose".

**New results.** Charter: CSUR "does not publish 'new' research". Referee page: papers primarily devoted to new technical
results are out of scope, but "this is not to say no new results may be included"; a paper devoted primarily to a survey
or tutorial that includes a new result "to organize and convey the material in a better way" is within scope.

**Systematic reviews and quantitative synthesis.** The Charter, the author guidelines and the referee page, all read in
full, never use the words systematic review, PRISMA, meta-analysis or quantitative synthesis. So the venue has no stated
requirement for, or objection to, an explicit protocol. [INF] A meta-analysis is defensible only under the "new result
that organises the material" clause: it must serve the taxonomy and the synthesis, not be the main finding. Observed
practice: CSUR published a PRISMA-reported review in 2026 (doi:10.1145/3801961, see Part B), so the format is accepted
in the journal; that paper has no meta-analysis.

**Referee form.** Four ingredients: technical quality, relevance to significant areas of research or practice, level of
general interest, effectiveness of presentation. "A substandard level in any is sufficient ground for rejection."
Referees write an anonymous report plus a cover letter to the editor with one of four recommendations: publish, publish
after revision, reject but encourage resubmission after revision, reject. Process: an associate editor chooses referees;
after refereeing the AE rejects or recommends acceptance to the Editor-in-Chief, who decides. Authors may name
non-preferred reviewers. ACM's general rule for refereed material is at least three independent reviewers (acm.org
pre-publication-evaluation page). Editors-in-Chief on the home page: My T. Thai and Hanghang Tong. Broad audience
point: the Charter says the paper should serve readers "outside their specialties", so jargon must be defined.

## 2. Manuscript requirements [OFF unless marked]

Sources: author-guidelines; https://www.acm.org/publications/authors/submissions ; template compiled here.

**Length and supplement.** Long survey at most 35 pages including references in the Surveys style. When justified,
additional material may be considered or published in an electronic supplement; then the manuscript must mark which
pages form the 35 and which form the supplement. Both are published together. "Manuscripts of excessive length may be
rejected without review." Short survey at most 15 pages. Supplement needs a short description, and a short readme.txt
appears in the DL with it.

**Abstract.** At most 100 words, short direct sentences; state objectives, summarise results, give principal conclusions;
no first person, no displayed mathematics, no citation numbers; avoid starting with "This paper".
[E1/INF] Published CSUR abstracts exceed this: 203 words (video diffusion survey), 135 (alignment survey), 123 (LLM
combinatorial optimisation review), counted from arXiv copies. The template does not enforce a limit. Follow the
100-word rule in the submission; the page is the only stated authority.

**Content indicators.** Three types: general terms and subject descriptors (both from the 2012 ACM Computing
Classification System) and keywords. Keywords must not be synonyms of CCS terms, should be specific nouns or noun
combinations, avoid catch-all words ("system", "discussion" and similar) and acronyms, and avoid negative terms.
Generate the CCS XML with the ACM DL indexing tool; the Submissions page says CCS concepts and keywords are required for
articles over two pages. Observed on two exemplars (first pages): CCS lines such as "General and reference ->
Surveys and overviews" with "Computing methodologies -> Machine learning / Computer vision / Natural language
generation".

**Authors and affiliations.** Names without titles; first-page footnote for funding and prior presentations. Submitting
authors must give an ORCID at submission; every author needs a valid ORCID before production. Single corresponding
author (authorship FAQ). Authors are named (no double-blind; the CSUR page does not mention anonymisation).

**Submission.** ScholarOne Manuscript Central, https://mc.manuscriptcentral.com/csur ; contact csur.admin@acm.org (the
home page prints csur-admin@acm.org). Submit LaTeX (or Word). All review submissions in single-column format.

**Reference style.** "Citations must follow the guidelines found within the ACM templates information"; the
Submissions page warns a paper may be returned for wrong reference format. LaTeX: `\bibliographystyle{ACM-Reference-Format}`
with BibTeX (BibTeX examples at acm.org/publications/authors/bibtex-formatting, not fetched). Compiled output uses
numeric citations ([1]) in acmsmall. ACM copy-edits to Chicago Manual of Style and Merriam-Webster and sends proofs.

**LaTeX class and options.**
- Current template per the Submissions page: "Primary Article Template - LaTeX (2.19; published June 28, 2026)".
- For review submission the same page says: use `\documentclass[manuscript]{acmart}` (single column).
- Format used for CSUR in production and for page counting: `acmsmall` (page: all journals use acmsmall except DGOV,
  DLT, DTRAP, HEALTH, IMWUT, JOCCH, TAP (acmlarge) and TOG (acmtog); CSUR is not listed, so acmsmall).
- Journal selection: `\acmJournal{CSUR}` (supported by the class; verified in acmart.cls: name "ACM Computing Surveys",
  short "ACM Comput. Surv.", ISSN codes 0360-0300 / 1557-7341). Volume, number, article and date macros
  (`\acmVolume`, `\acmNumber`, `\acmArticle`, `\acmMonth`, `\acmYear`) are filled by ACM at production.
- Hard constraints from the page: fonts cannot be substituted, margin adjustments are not allowed, restrict packages to
  the approved list (TAPS), Libertine font set required. Figure descriptions for accessibility (`\Description{}`) are
  requested, and colour must stay readable in greyscale (ColourBrewer or ACE suggested).
- Accepted source goes to the TAPS production system; the file uploaded to TAPS is the one to be corrected there.

**Template download and build test (done here).**
- Direct download from acm.org returned the Cloudflare challenge (HTTP 403 "Just a moment"). Used CTAN instead:
  `https://mirrors.ctan.org/macros/latex/contrib/acmart.zip`, SHA-256
  `93933ce58fbeffa13e23398bb523fcb68275ecc73369c6bc73b421eeef2c10de` (zip removed after unpacking).
  Class header after `latex acmart.ins`: `2026/08/16 v2.20`. The README in the zip says "The production version is the one
  on CTAN and ACM sites" and lists 2.20 with a date written 2028-08-16 (an upstream typo, [INF]); the ACM page still
  names 2.19 as current. Neither matters for layout, but pin the version used in `paper/style/acm/` and re-check at
  submission.
- Files: `paper/style/acm/acmart/` (full distribution with `acmguide.pdf` and `samples/`),
  `paper/style/acm/minimal-csur/` (acmart.cls generated, ACM-Reference-Format.bst, `csur-min.tex`, `refs.bib`, PDFs).
- Build: `cd paper/style/acm/minimal-csur && latexmk -pdf csur-min.tex` (MiKTeX, latexmk 4.88) exited 0, one page, with
  CCS block, keywords, ACM Reference Format line and bibliography. `csur-manuscript.tex` (`[manuscript,review]`) also
  builds.

**Page geometry measured from the builds** (1 pt = 1/72.27 in):

| Setting | Paper (pdf box) | Text width | Text height | Notes |
|---|---|---|---|---|
| `acmsmall` (CSUR layout, use for the 35-page count) | 6.75 x 10 in (486 x 720 pt) | 395.82 pt = 5.48 in | 574 pt = 7.94 in | baseline 12 pt; Libertine; single column |
| `manuscript,review` (review submission) | US letter | 430.00 pt = 5.95 in | 560 pt = 7.75 in | different geometry, so its page count is not the CSUR count |

Measured text density in a published acmsmall survey (arXiv copy of the video diffusion survey, same box): 540 to 620
words on a text-only page, about 600 words per page averaged over body pages with floats; reference lists about 30
entries per page (312 references took 10.4 of 37 pages). [E1, measured by this agent; used in the budget in Part B].

## 3. ACM Policy on Authorship and generative AI [OFF]

Source: https://www.acm.org/publications/policies/new-acm-policy-on-authorship (updated May 14, 2026), section "Use of
Artificial Intelligence"; FAQ https://www.acm.org/publications/policies/frequently-asked-questions. The CSUR home page
and author guidelines point to this policy.

**What is required.**
1. AI used *to conduct research* (the policy lists design and methodology, creation and selection of data sources,
   designing experiments, generation and collection of data, coding, implementing models, simulations, data analysis,
   testing, validating results, deploying software, archiving data and code, and other lifecycle steps directly
   relevant to the conclusions) "must be described in detail in the methods section of the Work". This explicitly
   includes artifacts "such as code, datasets, and charts or figures that rely on the AI tools".
2. AI used to *assist with writing*: ACM "no longer requires the disclosure" of it (as distinct from item 1).
3. Accountability: all named authors are responsible for any problematic content whatever its source. If integrity issues
   from AI use are found before publication, ACM may reject the submission in full and add penalties; after publication
   it may retract the whole work. The policy names fabricated or unverifiable citations among the risks.
4. A generative AI tool cannot be listed as an author (FAQ).
5. Policy applies to abstracts too (FAQ). Non-author helpers who only edit text may be acknowledged before the
   Bibliography (policy and FAQ), no disclosure needed.

**Where it goes:** the Methods section. CSUR has no separate declaration field in the pages read.

**What it means here [INF].** The review's pipeline (agent-assisted search, screening, full-text extraction, number
audit, meta-analysis code, figure scripts) is AI used to conduct research, so Methods must describe it in detail: tools
and versions, each task they did, what humans checked, the extraction accuracy sample, and disagreement handling. The
clarity pass with `research-humanizer` falls under writing assistance, which needs no disclosure under ACM (other
venues differ: Springer AIR and Elsevier Information Fusion both ask for some declaration, see item 7). The citation
validation gate is not optional: fabricated references are an explicit ground for rejection or retraction.

## 4. Cost [OFF unless marked]

Sources: https://libraries.acm.org/acmopen/apc-list-pricing ;
https://www.acm.org/publications/policies/policy-on-geographic-apc-waivers-and-discounts ;
https://www.acm.org/publications/policies/waiver-countries ; https://libraries.acm.org/acmopen/open-participants ;
https://www.acm.org/publications/openaccess .

All ACM publications are fully open access from 2026-01-01; an author needs ACM Open coverage, an APC, or a waiver.

| Case | 2026 (articles processed in eRights in 2026) | 2027 (processed after 2027-01-01 US Eastern) |
|---|---|---|
| List price, journal article | 1,800 USD | 1,800 USD |
| ACM or SIG member price (at least one named co-author a member) | 1,300 USD | 1,300 USD |
| Temporary subsidised price, non-member | 1,450 USD | none: journals return to list pricing |
| Temporary subsidised price, member | 950 USD | none |
| India: 50% lower-middle-income discount [INF: applied to the price that applies] | 725 / 475 USD | 900 / 650 USD |
| Corresponding author at an ACM Open institution | 0 | 0 |

- 2027: the pricing page says subsidised rates in 2027 apply only to conference proceedings and Proceedings of the ACM;
  journal articles processed through eRights after 12:00 am US Eastern on 2027-01-01 return to list price.
- Lower-middle-income discount: 50 percent for authors in World Bank lower-middle-income countries; 100 percent for
  EIFL and Research4Life countries. **India qualifies**: it is in the 50 percent column of the waiver-country list
  (not in the 100 percent columns). The policy text says "corresponding authors affiliated with institutions in" those
  countries; the 2026 text applies the discount "to the applicable subsidized rate".
- Financial-hardship waivers exist but are unlikely for authors at institutions that should be ACM Open participants.
- **ACM Open and VIT.** The participant list (3,053 institutions, fetched 2026-10-13) contains "VIT University Vellore"
  under India (saved copy line 1604; the Exa fetch is the only route, curl is blocked). ACM Open lets "corresponding
  authors from participating institutions" publish open access without APCs. Caveats: (a) it is the corresponding
  author's affiliation that counts; (b) the page gives no agreement dates; (c) APC-eligibility of a CSUR article is
  assumed, not stated; (d) the list is a snapshot. Confirm with the VIT library or through the ACM Open pages on libraries.acm.org before acceptance.
- Rights (relevant for sign-off): authors keep copyright, choose CC-BY or CC-BY-NC-ND, and must grant ACM the right to
  license the work to third parties "such as for training by LLMs". Authors-rights page.
- The PLAN table figure "1,450 USD" is the 2026 non-member subsidised rate, not a general price.

## 5. Resubmission, decision time, prior publication and preprints

**Resubmission after rejection [OFF].** Author guidelines, "How to Submit": papers rejected by CSUR "are not eligible for
resubmission to the journal for 12 months following the rejection date". Confirms the plan's "to confirm". The page does
not say how the bar treats the referee outcome "reject but encourage resubmission after revision" (item 1); unknown, ask
the editorial office before submitting. Appeals go first to the Editors-in-Chief, then to ACM's Director of Publications.

**Decision time.** [OFF] CSUR publishes no first-decision figure. The only official number is ACM-wide: each review cycle
(submission to each accept, revise or reject decision) should take "no more than 90 days on average"
(https://www.acm.org/publications/policies/pre-publication-evaluation, EIC duties). [E1] Third-party estimates, none
official: SciRev lists 28 days for immediate rejection from one review; a site that scraped 20 CSUR papers reports a median
of 455 days (mean 537) from received to accepted (crushsci.com, small sample); a submission-guide blog gives 2 to 4
months to first decision as an unofficial planning range (manusights.com, 2026). Planning value [INF]: 3 to 4 months to
a first decision, 9 to 15 months to acceptance, so a submission before the end of 2026 would be accepted in 2027, which is
the year APC list pricing returns.

**Prior publication [OFF].** Author guidelines: ACM journal papers are "normally original contributions" not published
elsewhere; republication of a widely disseminated paper is allowed only if the editor judges it adds significant
amplification or benefit, and prior appearance must be noted on the title page. The authorship policy: a paper may not be
under review elsewhere, and "posting a pre-print version of the Work to arXiv or a similar pre-print venue is not
considered a prior or current publication venue".

**Preprint rights [OFF].** https://authors.acm.org/author-resources/author-rights : authors may post pre-submitted,
submitted, accepted and peer-reviewed versions to their homepage, institutional repository, a funder-mandated repository, or
a non-commercial repository (owned by a non-profit, no fee, no advertising). arXiv is named as an example; ACM asks
authors to add the published DOI. ResearchGate, Academia.edu, Mendeley and Sci-Hub are named as not allowed. After
acceptance ACM posts the accepted manuscript under "Just Accepted" with a citable DOI.
[INF] Zenodo (CERN) fits the non-profit, no-fee, no-ads definition; SSRN (Elsevier) probably does not.

## 6. arXiv rule for review, survey and position papers [E1: blog read via search extract; arXiv-official]

Source: https://blog.arxiv.org/2025/10/31/attention-authors-updated-practice-for-review-articles-and-position-papers-in-arxiv-cs-category/
(dated 2025-10-31, News from arXiv).

- Review (survey) articles and position papers must now be accepted at a journal or conference and complete successful
  peer review before they are considered for submission to arXiv's CS category.
- Submit documentation of peer review (the journal reference and DOI metadata); without it the paper is "likely to be
  rejected" and not appear.
- Workshop review is not enough.
- Reason given: an "unmanageable influx" of such papers. arXiv says these types were never a listed content type and had
  been accepted at moderator discretion.
- Scope: the post applies to the CS category; it says other categories may change their practice independently.
- Consequence for the project: no arXiv posting of the review before CSUR acceptance. Permitted routes under ACM policy:
  author homepage, VIT institutional repository, Zenodo (item 5). Use Zenodo or the repo with a dated, versioned protocol
  and search log for priority. [INF] After acceptance, post to arXiv with the ACM DOI. Do not try to route around the rule
  by choosing a non-CS primary category; moderators decide what counts as a review and a meta-analysis with new estimates
  might be classified either way (unknown).

## 7. Fallback journals (official metrics pages only)

| | CSUR (reference) | Artificial Intelligence Review (Springer) | Information Fusion (Elsevier) |
|---|---|---|---|
| JIF | 30.4 (2025), rank 1/146 [OFF] | 18.8 (2025); 5-year 19.1 (2025) [OFF] | 15.5 shown on the journal page; the page does not state the year [OFF, year unverified]; CiteScore 24.1 |
| Review type and size | long survey 35 pp incl. refs | survey and tutorial articles are in scope; no page or reference limit found in the part of the guidelines read (first ~9,000 characters) | "Survey article": up to 50 pages, at most 300 references (guide for authors, article types and the formatting notice; failure to comply may mean desk rejection) |
| APC | 1,800 USD list (0 if ACM Open) | 2,490 GBP / 3,390 USD / 2,790 EUR, set at acceptance; fully open access since January 2024 [OFF: how-to-publish page extract] | 4,130 USD on the guide and open-access options pages; 4,740 USD on the Journal Insights page, same day (conflict; "amount may be reduced during submission") |
| First decision | not published | median 12 days submission to first decision [OFF journal page] | not seen |
| Review model | referees via associate editor | not read | single anonymised; at least two reviewers |
| AI-use rule | Methods description if AI used in research; no disclosure for writing help | LLM use documented in Methods; "AI assisted copy editing" need not be declared; LLMs cannot be authors | generative AI use in manuscript preparation must be declared at submission |
| Preprints | arXiv itself blocks CS surveys; ACM allows posting | not read | sharing a preprint is not prior publication; free SSRN posting offered |
| Scope fit [INF] | strong: surveys integrating a field | strong: refereed surveys in AI | weak to moderate: scope is multi-sensor, multi-source fusion (architectures, algorithms, applications); multimodal fusion models are adjacent, discrete diffusion language models are not. The scope text also says "invited review articles" while the article-type table lists survey articles; check before choosing it. |

Notes: (1) Springer AIR abstract 150 to 250 words, 4 to 6 keywords; Information Fusion abstract up to 250 words. (2) The
reference cap of 300 in Information Fusion would bind a systematic review of 150 to 250 included papers plus method
citations; CSUR has no cap but the 35 pages do. (3) AIR is the safer scope fit; Information Fusion has the larger
length but a weaker fit and the highest APC.

## 8. Open questions to settle with the CSUR office (csur.admin@acm.org) before submission

1. Does the 12-month bar apply after "reject but encourage resubmission after revision"?
2. Is an electronic supplement with the per-paper extraction table, search logs and its own reference list accepted for a
   systematic review, and are its references excluded from the 35 pages?
3. Are published page counts above 35 granted on request, and how is that justified (Part B shows 6 of 7 checked
   surveys above 35)?
4. Is a pre-submission inquiry welcome? The Charter says the Editor-in-Chief "welcomes suggestions for topics and
   questions about contemplated submissions".
5. Is the corresponding author's VIT affiliation enough for ACM Open coverage of a CSUR article?

## 9. Reproduction log

- Official page text fetched with the Exa `web_fetch_exa` tool on 2026-10-13; saved raw: ACM Open participant list only.
- Template: `paper/style/acm/` (see item 2). Build command above. No data downloaded other than the template zip.
- Ledger rows: `python tools/ledger.py list claims --last 12` (rows added by this run).
