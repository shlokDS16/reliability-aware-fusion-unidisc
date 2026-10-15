# Web digest: review method standards, LLM screening, agreement, ACM/CSUR, arXiv, registration (2026-10-15)

Condensed by the orchestrator from the final report of a web-research subagent (spawned for the
dlm-expert KB). Evidence levels as reported: E2 = official text read (section named), E1 = abstract
or snippet, Crossref = metadata only. Spot-check E&E details against the BMJ text before quoting.

## 1. PRISMA 2020
- Page et al., BMJ 2021;372:n71, doi 10.1136/bmj.n71 (E2): 27 items in 7 sections; abstract checklist 12 items. E&E: Page et al., BMJ 2021;372:n160, doi 10.1136/bmj.n160 (E2 via summariser).
- Items computing reviews usually fail: 6 (every source + last-searched date), 7 (full strategies for all sources with filters/limits), 8 (number of screeners per record and report, independence, automation details), 9 (same for extraction), 11 (risk-of-bias/quality method and number of appraisers), 15 (certainty), 16b (near-miss exclusions with reasons), 23c (limitations of the review process), 24a-c (registration, protocol, amendments with stage), 26 (competing interests), 27 (data, code, materials).
- Automation: items 8, 9, 11 ask for tool details; E&E 8: say whether records were excluded on machine assessment alone; flow-diagram box "records marked as ineligible by automation tools"; internally derived classifiers: report software, version, use, training, validation; E&E 16a: separate human and automation exclusions. No LLM-specific items.
- Unregistered: 24a state not registered; 24b protocol location or none; 24c each amendment, reason and stage.

## 2. PRISMA-S
- Rethlefsen et al., Syst Rev 2021, doi 10.1186/s13643-020-01542-z (E2): 16 items: database name and platform; multi-database platforms; registries; online resources/browsing; citation searching; contacts; other methods; full strategy per source exactly as run; limits with justification; published filters; adapted prior strategies; updates; last-search date per strategy; search peer review (e.g. PRESS); total records per source; deduplication method and software.

## 3. LLM/AI in evidence synthesis
- PRISMA-trAIce: Holst et al., JMIR AI 2025;4:e80247, doi 10.2196/80247 (E2): proposed, not validated (no Delphi); items on AI in title/abstract, tool identity, stage, inputs/outputs, prompts and parameters, human oversight, performance evaluation, AI vs human decisions per stage, modified flow diagram. Item count unclear (14 in text vs 17 IDs). Not endorsed: Moher et al., "PRISMA-trAIce: A Name Without Endorsement", JMIR AI 2026;5:e104210, doi 10.2196/104210 (E1). Use as a reporting aid only.
- Joint position statement (Cochrane, Campbell, JBI, CEE): Flemyng et al. 2025; JBI Evid Synth doi 10.11124/jbies-25-00480; Cochrane doi 10.1002/14651858.ED000178; Campbell doi 10.1002/cl2.70074; Environ Evid doi 10.1186/s13750-025-00374-5 (E2, PMC12594113). RAISE 1-3 drafts on OSF https://osf.io/fwaud/ (draft v4, 23 Sep 2026; not yet published).
  Requirements: authors accountable; justify AI use with evidence it does not undermine reliability; audit trail and prompt documentation; AI never an author; declare AI that makes or suggests judgements (eligibility, appraisal, extraction, synthesis); report tool name, version, date, stage, validation in this review, limitations; share prompts, outputs, code; report AI use at protocol stage.
  RAISE 2: gold-standard set; recall and precision/burden; development records not reused for evaluation; held-out testing after modification; in-review ("context-specific") validation; for generative AI test run-to-run stability and caching.
  RAISE 3: stopping rules for prioritised screening are overconfident; validate before use; version-control prompts.
- Cochrane: RevMan mandatory "Disclosure of artificial intelligence use" subheading (from 5 Jan 2026 interventions, 4 May 2026 all) (E2, Author Digest March 2026).
- Empirical LLM screening (E1): Tran et al., Ann Intern Med 2024, doi 10.7326/M23-3389 (GPT-3.5; sensitive rule 94.6-99.8 percent sensitivity); Matsui et al., JMIR 2024, doi 10.2196/52758; Dai et al., JMIR 2025, doi 10.2196/67488 (pooled sensitivity 0.73); Delgado-Chaves et al., PNAS 2025, doi 10.1073/pnas.2411962122 (lost evidence 14-100 percent on reanalysis); Huotala et al., ESEM 2025, doi 10.1109/ESEM64174.2025.00053 (24 SE reviews; did not recommend LLM screening); Nawrath et al., Information 2026, doi 10.3390/info17050501 (low-prevalence kappa artefact); Xie et al., J Evid Based Med 2026, doi 10.1111/jebm.70166 (meta-analysis: sensitivity 0.92, specificity 0.94); Gartlehner et al., J Clin Epidemiol 2020, doi 10.1016/j.jclinepi.2020.01.005 (single human screener misses 13 percent).
- Validation design: Madeyski, Kitchenham, Shepperd, LLM4SCREENLIT, Inf Softw Technol 2026, doi 10.1016/j.infsof.2026.108204; arXiv 2511.12635 (E2): human-screened random sample independent of prompt development; full confusion matrix; lost evidence (1 - recall) with CI; unclassifiable output as positive; non-LLM baseline; run-to-run stability; MCC or cost-weighted MCC (weight 10); accuracy/specificity mislead at low prevalence. Exact-binomial note: zero misses in n relevant gives a 95 percent upper bound near 3/n (about 60 relevant records to bound at 5 percent). Stopping rule: Callaghan and Mueller-Hansen, Syst Rev 2020, doi 10.1186/s13643-020-01521-4.

## 4. Software-engineering review guidance
- Kitchenham and Charters, EBSE-2007-01 v2.3, 9 July 2007 (E2): protocol with independent evaluation and piloting; trial strings against known studies; quality instrument; two or more extractors with agreement.
- SEGRESS: Kitchenham, Madeyski, Budgen, IEEE TSE 49(3):1273-1298, 2023, doi 10.1109/TSE.2022.3174092 (E2): PRISMA 2020 plus SE lessons; "risk of bias" replaces "quality assessment", "limitations" replaces generic "threats to validity"; state why quality assessment is done.
- Quasi-gold standard: Zhang, Babar, Tell, IST 53(6), 2011, doi 10.1016/j.infsof.2010.12.010 (E2): quasi-sensitivity threshold 70-80 percent.
- Snowballing: Wohlin 2014, doi 10.1145/2601248.2601268. Mapping: Petersen et al. 2015, doi 10.1016/j.infsof.2015.03.007.
- GUEST (GenAI use and evaluation in SLR tasks): Kitchenham, Pizard, Madeyski et al., arXiv 2607.24991 (preprint, E2 partial): human oversight, validation before replacing a human reviewer, confusion matrices, model versions, parameters, prompts, contamination handling.

## 5. Quality appraisal for ML method papers
- REFORMS: Kapoor et al., Sci Adv 2024, doi 10.1126/sciadv.adk3452 (E2): 32 items in 8 modules; scope ML-based science (method research out of scope but parts usable).
- NeurIPS paper checklist (guide page, E2): claims, limitations, theory, reproducibility, open data/code, settings, statistical significance (what error bars capture), compute.
- Pineau et al., JMLR 22(164), 2021 (E2 text).
- PROBAST+AI (doi 10.1136/bmj-2024-082505) and TRIPOD+AI (doi 10.1136/bmj-2023-078378): clinical prediction models; do not apply directly.
- Recommended form for DLM method papers (synthesis): code and weights with version; seeds and variance; matched compute, parameters and decoding budget; ablations; evaluation protocol and splits; leakage and contamination; comparable baseline tuning; uncertainty and tests; yes/no/not reported per item; number of appraisers and agreement; no single score; descriptor, not exclusion filter.

## 6. Agreement statistics
- Cohen 1960, doi 10.1177/001316446002000104; Feinstein and Cicchetti 1990 I and II, doi 10.1016/0895-4356(90)90158-L and 10.1016/0895-4356(90)90159-M (report p_pos and p_neg); Byrt, Bishop, Carlin 1993, doi 10.1016/0895-4356(93)90018-V (bias and prevalence indices); Gwet 2008, doi 10.1348/000711006X126600 (AC1); Landis and Koch 1977, doi 10.2307/2529310; McHugh 2012, doi 10.11613/bm.2012.031 (stricter bands; kappa below 0.60 inadequate); Sim and Wright 2005, doi 10.1093/ptj/85.3.257; Hayes and Krippendorff 2007, doi 10.1080/19312450709336664.
- Practice: confusion matrix, raw agreement, kappa with CI, bias and prevalence indices, p_pos and p_neg, AC1 or Krippendorff's alpha as sensitivity; for LLM vs human, recall and lost evidence against an adjudicated reference; do not mix gold-standard metrics and kappa on the same matrix (LLM4SCREENLIT).

## 7. ACM, CSUR, arXiv
- ACM Policy on Authorship (updated 2026-05-14; E2 via Exa): AI used in conducting research described in detail in the Methods section; writing-assistance disclosure no longer required; authors are humans; arXiv preprint is not prior publication.
- CSUR author guidelines (E2): long surveys at most 35 pages including references in Surveys style, extra material in an online supplement with the 35-page version marked; abstract at most 100 words, no first person, no displayed maths, no citations; CCS 2012 concepts and keywords; ORCID for submitting author at submission and all authors before production; supplement needs a short readme; rejected papers not resubmittable for 12 months; ACM fully open access from 2026-01-01. Charter: surveys integrate literature, not new research (E1).
- arXiv cs: review and survey papers accepted only after peer-reviewed acceptance with journal reference (blog 2025-10-31, E2; no repeal found). Use OSF or Zenodo for a preprint.

## 8. Registration
- PROSPERO: not eligible (health outcome required) (E2, 2023 guidance PDF).
- OSF Registries "Generalized Systematic Review" template (van den Akker et al., Syst Rev 2023, doi 10.1186/s13643-023-02281-7): time-stamped, embargo up to 4 years. A registration after screening began is retrospective and must be stated with its date.

## Actions for Paper 1 (orchestrator, from this digest)
1. Abstract to at most 100 words (current 237; a 100-word version exists as a LaTeX comment).
2. No arXiv posting before acceptance; plan an OSF or Zenodo preprint.
3. Register the protocol on OSF (retrospective, dated, with all section 10 amendments) and report PRISMA 24a-c accordingly.
4. LLM screening validation against a human-screened random sample independent of prompt development (the 218-record human sample is the instrument; it needs the user); report confusion matrix, lost evidence with CI, MCC; run-to-run stability check on a small rerun.
5. Agreement reporting: add p_pos, p_neg, bias and prevalence indices, AC1 to the screening and census agreement scripts.
6. Quality appraisal: pre-specified form from REFORMS, NeurIPS and Pineau items; two appraisers; descriptor only.
7. Methods section: model identifiers, dates, prompts (versioned, shared), stage of each LLM, human oversight; flow diagram separating automation and human exclusions; PRISMA-S items for every source.
8. CCS concepts, ORCIDs, supplement readme.
