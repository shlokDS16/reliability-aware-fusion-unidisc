---
agent: citation-validator
date: 2026-10-15
brief: Validate paper/review/references.bib (90 entries) and the \cite support in paper/review/sections/*.tex for Paper 1
sources_examined: [arXiv API (85 IDs), Crossref (DOIs listed below), OpenAlex (title search), OpenReview (venue field, notes search), arXiv PDFs of 33 cited papers converted with markitdown, arXiv abstracts of 70 cited papers, Keele/Durham EBSE report via web search (secondary records only)]
coverage: All 90 bib entries checked for metadata. All 76 distinct cited keys read in context (sections 01 to 08). Converted full text (markitdown) searched for the numbers, equations and sections named in the sentences for 33 papers (keyword checks, not whole-paper reads). Not covered: Kitchenham report PDF; DBLP (blocked by a bot challenge, HTTP 202); OpenReview search for authors of anonymous submissions; code-level claims (released samplers, E3); the 36-model table of 2508.10875; reference-list counts beyond the two surveys.
claims: []
competing_explanations: []
unknowns: [openreview:Gq4yt8pxRo authors (anonymous submission); 2107.03006, 2110.02037, 2211.15089, 2506.10892 published venue not confirmed by OpenReview/OpenAlex/Crossref (2110.02037 and 2210.08933 confirmed from the arXiv PDF venue header)]
---

# Citation validation, Paper 1 review manuscript (2026-10-15)

Scope: `paper/review/references.bib` (90 entries: 85 arXiv keys, 4 classic, 1 OpenReview) and every `\cite` in `paper/review/sections/*.tex`. The `.tex` prose was not edited. Keys were not renamed.

## 1. Counts

- Metadata verified: 90 of 90 entries. 85 arXiv entries match the arXiv API on title, first-version year and author list (last names). PRISMA 2020 matches Crossref. Wilson 1927 and Cohen 1960 were checked against Crossref. Kitchenham and Charters were checked against bibliographic records and the Keele/Durham report identifier.
- Fixed in `references.bib`: 4 metadata edits (DOI added to Wilson and Cohen; "Version 2.3" added to Kitchenham and Charters; OpenReview author set to Anonymous). Also 85 comment lines added above the arXiv entries, recording the published version, and the validation comments in the header and above the classic entries were updated. No keys changed. No arXiv entry's title, author or year needed correction.
- Published versions found: 53 of 85 arXiv entries have a published version (venue recorded; DOI where Crossref confirmed it). The other 32 are preprint-only in every source checked. Entries are still the preprint records; switching an entry to its published version is an author decision (keys would stay).
- Retracted or withdrawn: 0 found. OpenAlex `is_retracted` is false for every matched record. Crossref `update-to` is empty for all 33 DOIs checked. One ICLR 2026 submission (2509.24897, RealUnify) is listed by OpenReview as a withdrawn submission; the arXiv preprint is still available, so it is recorded as a preprint with a note.
- Unverifiable: 1 (openreview:Gq4yt8pxRo, anonymous submission, no authors via the OpenReview API; its content is cited for three claims and cannot be checked).
- Support problems (cited sentence does not support, or only partly supports, its citation): 1 does-not-support, 9 partial or overstated, 7 unverified sub-claims. Details in section 3.

## 2. Per-entry status table

Columns: bib key | arXiv record (verified fields) | published version (source) | status | cited in sections.

| bib key | arXiv record | published version (source) | status | cited |
|---|---|---|---|---|
| `arXiv:2107.03006` | arXiv 2107.03006, 2021, title/authors/year match | none found (OpenReview, OpenAlex, Crossref; DBLP unavailable) | verified (preprint; no published version found) | cited |
| `arXiv:2202.04200` | arXiv 2202.04200, 2022, title/authors/year match | CVPR 2022, doi:10.1109/CVPR52688.2022.01103 (Crossref) | verified; published version recorded | cited |
| `arXiv:2205.14217` | arXiv 2205.14217, 2022, title/authors/year match | NeurIPS 2022, doi:10.52202/068431-0313 (Crossref) | verified; published version recorded | cited |
| `arXiv:2303.06574` | arXiv 2303.06574, 2023, title/authors/year match | IJCAI 2023 (survey), doi:10.24963/ijcai.2023/750 (Crossref) | verified; published version recorded | cited |
| `arXiv:2310.16834` | arXiv 2310.16834, 2023, title/authors/year match | ICML 2024 oral (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2401.01879` | arXiv 2401.01879, 2024, title/authors/year match | ICML 2025 poster (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2406.03736` | arXiv 2406.03736, 2024, title/authors/year match | ICLR 2025 poster (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2406.04329` | arXiv 2406.04329, 2024, title/authors/year match | NeurIPS 2024, doi:10.52202/079017-3277 (Crossref) | verified; published version recorded | cited |
| `arXiv:2406.07524` | arXiv 2406.07524, 2024, title/authors/year match | NeurIPS 2024, doi:10.52202/079017-4135 (Crossref) | verified; published version recorded | cited |
| `arXiv:2408.11039` | arXiv 2408.11039, 2024, title/authors/year match | ICLR 2025 oral (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2408.12528` | arXiv 2408.12528, 2024, title/authors/year match | ICLR 2025 poster (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2409.14993` | arXiv 2409.14993, 2024, title/authors/year match | IEEE Trans. Circuits Syst. Video Technol., doi:10.1109/TCSVT.2025.3635224 (Crossref; issued 2026, arXiv journal_ref says 2025) | verified; published version recorded | cited |
| `arXiv:2410.13848` | arXiv 2410.13848, 2024, title/authors/year match | CVPR 2025, doi:10.1109/CVPR52734.2025.01210 (Crossref) | verified; published version recorded | NOT cited |
| `arXiv:2502.09992` | arXiv 2502.09992, 2025, title/authors/year match | NeurIPS 2025, doi:10.52202/085713-1689 (Crossref) | verified; published version recorded | cited |
| `arXiv:2503.00307` | arXiv 2503.00307, 2025, title/authors/year match | NeurIPS 2025, doi:10.52202/085713-4927 (Crossref); ICLR 2025 DeLTa workshop poster (OpenReview) | verified; published version recorded | cited |
| `arXiv:2503.20853` | arXiv 2503.20853, 2025, title/authors/year match | none verified (OpenReview: submitted to ICLR 2025) | verified (preprint; no published version found) | cited |
| `arXiv:2505.02567` | arXiv 2505.02567, 2025, title/authors/year match | none found | verified (preprint; no published version found) | cited |
| `arXiv:2505.15809` | arXiv 2505.15809, 2025, title/authors/year match | NeurIPS 2025, doi:10.52202/085713-4636 (Crossref) | verified; published version recorded | cited |
| `arXiv:2505.24857` | arXiv 2505.24857, 2025, title/authors/year match | NeurIPS 2025, doi:10.52202/085713-1874 (Crossref) | verified; published version recorded | cited |
| `arXiv:2506.13759` | arXiv 2506.13759, 2025, title/authors/year match | TMLR (OpenReview: accepted); no DOI | verified; published version recorded | cited |
| `arXiv:2508.08712` | arXiv 2508.08712, 2025, title/authors/year match | none found | verified (preprint; no published version found) | cited |
| `arXiv:2508.10875` | arXiv 2508.10875, 2025, title/authors/year match | none; under review at TMLR (OpenReview) | verified (preprint; no published version found) | cited |
| `arXiv:2509.24435` | arXiv 2509.24435, 2025, title/authors/year match | none found | verified (preprint; no published version found) | cited |
| `arXiv:2509.24897` | arXiv 2509.24897, 2025, title/authors/year match | none confirmed (OpenReview search lists CVPR 2026; Crossref/OpenAlex none; ICLR 2026 submission withdrawn) | verified (preprint; no published version found) | cited |
| `arXiv:2510.04525` | arXiv 2510.04525, 2025, title/authors/year match | TMLR 2026 (arXiv journal_ref; OpenReview: accepted by TMLR); no DOI | verified; published version recorded | cited |
| `arXiv:2510.04767` | arXiv 2510.04767, 2025, title/authors/year match | ICLR 2026 poster (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2510.18480` | arXiv 2510.18480, 2025, title/authors/year match | none found | verified (preprint; no published version found) | cited |
| `arXiv:2601.15593` | arXiv 2601.15593, 2026, title/authors/year match | ACL Findings 2026, doi:10.18653/v1/2026.findings-acl.357 (Crossref) | verified; published version recorded | NOT cited |
| `arXiv:2602.00286` | arXiv 2602.00286, 2026, title/authors/year match | none; ICLR 2027 / ICML 2026 submission (OpenReview) | verified (preprint; no published version found) | cited |
| `arXiv:2604.02718` | arXiv 2604.02718, 2026, title/authors/year match | none found | verified (preprint; no published version found) | cited |
| `arXiv:2605.12522` | arXiv 2605.12522, 2026, title/authors/year match | COLM 2026 (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2605.25343` | arXiv 2605.25343, 2026, title/authors/year match | none found | verified (preprint; no published version found) | cited |
| `arXiv:2606.19475` | arXiv 2606.19475, 2026, title/authors/year match | none found | verified (preprint; no published version found) | NOT cited |
| `arXiv:2606.20536` | arXiv 2606.20536, 2026, title/authors/year match | none; ICLR 2027 submission; OpenReview also lists an ECCV 2026 workshop oral (ET), not confirmed | verified (preprint; no published version found) | cited |
| `arXiv:2606.29228` | arXiv 2606.29228, 2026, title/authors/year match | none found | verified (preprint; no published version found) | cited |
| `arXiv:2607.04423` | arXiv 2607.04423, 2026, title/authors/year match | Lecture Notes in Computer Science 2026, doi:10.1007/978-3-032-37132-4_35 (Crossref; venue not identified) | verified; published version recorded | cited |
| `arXiv:2607.12829` | arXiv 2607.12829, 2026, title/authors/year match | IJCAI 2026, doi:10.24963/ijcai.2026/873 (Crossref) | verified; published version recorded | cited |
| `arXiv:2607.13188` | arXiv 2607.13188, 2026, title/authors/year match | none found | verified (preprint; no published version found) | NOT cited |
| `arXiv:2607.24763` | arXiv 2607.24763, 2026, title/authors/year match | none found | verified (preprint; no published version found) | cited |
| `arXiv:2609.01607` | arXiv 2609.01607, 2026, title/authors/year match | none; ICLR 2027 submission (OpenReview) | verified (preprint; no published version found) | cited |
| `arXiv:2609.04778` | arXiv 2609.04778, 2026, title/authors/year match | none journal; Research Square preprint doi:10.21203/rs.3.rs-10410801/v1 (OpenAlex) | verified (preprint; no published version found) | cited |
| `arXiv:2609.34509` | arXiv 2609.34509, 2026, title/authors/year match | none; ICLR 2027 submission; BeNTo workshop NeurIPS 2026 (OpenReview) | verified (preprint; no published version found) | cited |
| `arXiv:2610.09866` | arXiv 2610.09866, 2026, title/authors/year match | none; ICLR 2027 submission (OpenReview) | verified (preprint; no published version found) | NOT cited |
| `%s` | BMJ 2021;372:n71 | 2021 | Crossref title, volume, article number match | BMJ, doi:10.1136/bmj.n71 (Crossref) | verified (no change needed) | cited |
| `%s` | EBSE-2007-01, Keele/Durham, 2007 | 2007 | title, authors, institution, number match; version 2.3 added | technical report (not a journal) | verified against bibliographic records; PDF not opened | cited |
| `%s` | JASA 22(158):209-212 | 1927 | match; DOI added | JASA, doi:10.1080/01621459.1927.10502953 (Crossref) | verified, fixed (DOI added) | cited |
| `%s` | Educ. Psychol. Meas. 20(1):37-46 | 1960 | match; DOI added | Educ. Psychol. Meas., doi:10.1177/001316446002000104 (Crossref) | verified, fixed (DOI added) | cited |
| `%s` | ICLR 2027 double-blind submission (OpenReview) | 2026 | title matches; no authors visible via API | none (under review) | unverifiable as to authors; author set to Anonymous | cited |
| `arXiv:2110.02037` | arXiv 2110.02037, 2021, title/authors/year match | ICLR 2022 (venue header of arXiv PDF) | verified; published version recorded | cited |
| `arXiv:2205.14987` | arXiv 2205.14987, 2022, title/authors/year match | NeurIPS 2022, doi:10.52202/068431-2049 (Crossref) | verified; published version recorded | cited |
| `arXiv:2210.08933` | arXiv 2210.08933, 2022, title/authors/year match | ICLR 2023 (venue header of arXiv PDF) | verified; published version recorded | cited |
| `arXiv:2210.17432` | arXiv 2210.17432, 2022, title/authors/year match | ACL 2023, doi:10.18653/v1/2023.acl-long.647 (Crossref) | verified; published version recorded | cited |
| `arXiv:2211.15089` | arXiv 2211.15089, 2022, title/authors/year match | none found (OpenReview, OpenAlex) | verified (preprint; no published version found) | cited |
| `arXiv:2305.08379` | arXiv 2305.08379, 2023, title/authors/year match | EACL 2024, doi:10.18653/v1/2024.eacl-long.144 (Crossref) | verified; published version recorded | NOT cited |
| `arXiv:2305.18619` | arXiv 2305.18619, 2023, title/authors/year match | NeurIPS 2023, doi:10.52202/075280-0730 (Crossref; OpenReview poster) | verified; published version recorded | cited |
| `arXiv:2407.15595` | arXiv 2407.15595, 2024, title/authors/year match | NeurIPS 2024, doi:10.52202/079017-4239 (Crossref) | verified; published version recorded | cited |
| `arXiv:2409.02908` | arXiv 2409.02908, 2024, title/authors/year match | ICLR 2025 poster (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2410.01949` | arXiv 2410.01949, 2024, title/authors/year match | ICLR 2025 poster (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2410.08709` | arXiv 2410.08709, 2024, title/authors/year match | ICML 2025 poster (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2410.17891` | arXiv 2410.17891, 2024, title/authors/year match | ICLR 2025 poster (OpenReview); no DOI | verified; published version recorded | NOT cited |
| `arXiv:2412.10193` | arXiv 2412.10193, 2024, title/authors/year match | ICLR 2025 poster (OpenReview); no DOI | verified; published version recorded | NOT cited |
| `arXiv:2501.00289` | arXiv 2501.00289, 2024, title/authors/year match | CVPR 2025, doi:10.1109/CVPR52734.2025.00265 (Crossref) | verified; published version recorded | cited |
| `arXiv:2502.06768` | arXiv 2502.06768, 2025, title/authors/year match | ICML 2025 oral (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2502.09622` | arXiv 2502.09622, 2025, title/authors/year match | NeurIPS 2025, doi:10.52202/085713-0825 (Crossref) | verified; published version recorded | cited |
| `arXiv:2502.13917` | arXiv 2502.13917, 2025, title/authors/year match | ACL 2025, doi:10.18653/v1/2025.acl-long.1029 (Crossref) | verified; published version recorded | NOT cited |
| `arXiv:2503.09573` | arXiv 2503.09573, 2025, title/authors/year match | ICLR 2025 oral (OpenReview; venue header of arXiv PDF); no DOI | verified; published version recorded | cited |
| `arXiv:2503.17076` | arXiv 2503.17076, 2025, title/authors/year match | ICLR 2025 poster (OpenReview; venue header of arXiv PDF); no DOI | verified; published version recorded | cited |
| `arXiv:2505.14683` | arXiv 2505.14683, 2025, title/authors/year match | none found (OpenReview: CoRR only) | verified (preprint; no published version found) | cited |
| `arXiv:2505.16839` | arXiv 2505.16839, 2025, title/authors/year match | NeurIPS 2025 spotlight, doi:10.52202/085713-3511 (Crossref) | verified; published version recorded | cited |
| `arXiv:2505.16990` | arXiv 2505.16990, 2025, title/authors/year match | none found (OpenReview: submitted to ICLR 2026) | verified (preprint; no published version found) | NOT cited |
| `arXiv:2505.20147` | arXiv 2505.20147, 2025, title/authors/year match | NeurIPS 2025 spotlight, doi:10.52202/085713-2720 (Crossref) | verified; published version recorded | cited |
| `arXiv:2505.21400` | arXiv 2505.21400, 2025, title/authors/year match | NeurIPS 2025 poster (OpenReview); DOI not confirmed | verified; published version recorded | cited |
| `arXiv:2505.22618` | arXiv 2505.22618, 2025, title/authors/year match | ICLR 2026 poster (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2505.23606` | arXiv 2505.23606, 2025, title/authors/year match | none found (OpenReview: CoRR only) | verified (preprint; no published version found) | NOT cited |
| `arXiv:2506.10892` | arXiv 2506.10892, 2025, title/authors/year match | none verified (OpenAlex record ambiguous) | verified (preprint; no published version found) | cited |
| `arXiv:2506.15564` | arXiv 2506.15564, 2025, title/authors/year match | NeurIPS 2025, doi:10.52202/085713-1584 (Crossref) | verified; published version recorded | cited |
| `arXiv:2506.20639` | arXiv 2506.20639, 2025, title/authors/year match | ICLR 2026 poster (OpenReview); no DOI | verified; published version recorded | NOT cited |
| `arXiv:2507.15897` | arXiv 2507.15897, 2025, title/authors/year match | NeurIPS 2025, doi:10.52202/085713-2727 (Crossref) | verified; published version recorded | cited |
| `arXiv:2508.02193` | arXiv 2508.02193, 2025, title/authors/year match | none found | verified (preprint; no published version found) | cited |
| `arXiv:2508.15487` | arXiv 2508.15487, 2025, title/authors/year match | none found | verified (preprint; no published version found) | NOT cited |
| `arXiv:2509.19244` | arXiv 2509.19244, 2025, title/authors/year match | ICLR 2026 poster (OpenReview); no DOI | verified; published version recorded | NOT cited |
| `arXiv:2510.06308` | arXiv 2510.06308, 2025, title/authors/year match | none found | verified (preprint; no published version found) | cited |
| `arXiv:2510.22510` | arXiv 2510.22510, 2025, title/authors/year match | ICML 2026 (OpenReview: accepted, arXiv version) | verified; published version recorded | cited |
| `arXiv:2511.09611` | arXiv 2511.09611, 2025, title/authors/year match | ICLR 2026 poster (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2603.22248` | arXiv 2603.22248, 2026, title/authors/year match | none found | verified (preprint; no published version found) | cited |
| `arXiv:2604.00007` | arXiv 2604.00007, 2026, title/authors/year match | none; ICLR 2027 submission (OpenReview) | verified (preprint; no published version found) | NOT cited |
| `arXiv:2604.00375` | arXiv 2604.00375, 2026, title/authors/year match | COLM 2026 (OpenReview); no DOI; arXiv PDF header still says under review | verified; published version recorded | cited |
| `arXiv:2605.10518` | arXiv 2605.10518, 2026, title/authors/year match | ICML 2026 (OpenReview); no DOI | verified; published version recorded | cited |
| `arXiv:2608.10615` | arXiv 2608.10615, 2026, title/authors/year match | none; ICLR 2027 submission (OpenReview) | verified (preprint; no published version found) | cited |
| `arXiv:2608.25505` | arXiv 2608.25505, 2026, title/authors/year match | none found | verified (preprint; no published version found) | cited |

## 3. Support problems

Each item gives the file and line in `paper/review/sections/`, the cited key, the sentence fragment, and the finding. Sentences were read in context. Sources: arXiv abstracts for all cited keys; converted PDFs for the keys named in the items.

### 3a. Does not support

1. `03-notation.tex:41`, `arXiv:2210.17432` (SSD-LM). The list says "Gaussian corruption of learned embeddings or of logits" and includes SSD-LM. SSD-LM's abstract describes simplex-based diffusion on the vocabulary space "rather than a learned latent space". It does not use Gaussian corruption. Remove the key from this list. The following sentence ("a genuine simplex diffusion was tried and abandoned by one of these works") is supported by `arXiv:2211.15089` (CDCD, appendix B.3), which should be cited for it directly.

### 3b. Partial or overstated

2. `07-error-budget.tex:23`, `arXiv:2603.22248`. "two more papers give the total-correlation form for exact predictors". The converted PDF expresses the sampling-error bound as sums of mutual-information terms (around lines 949 to 1006 of its text). No total-correlation form was found. `arXiv:2608.25505` does give the conditional total-correlation identity. Either reword this key's role to "a mutual-information form" or add the check.
3. `07-error-budget.tex:23`, `arXiv:2110.02037` (ARDM). "For random orders it is in the autoregressive diffusion models paper (Eq. 3 and 4)". Eq. 3 and 4 state that, under a uniform permutation, the expected log-likelihood terms are equal across positions, which justifies parallel steps. The total-correlation identity itself is not written there. Partial.
4. `07-error-budget.tex:57`, `arXiv:2410.01949` and `arXiv:2410.08709`. "Joint draws: autoregressive heads, copulas, energy reweighting, verifiers". The copula and mixture papers support the joint-predictor part. "Energy reweighting" and "verifiers" are not in either source. Partial.
5. `07-error-budget.tex:26`, `arXiv:2605.10518` (IMDM). "The per-step total correlation is defined for discrete flows and few-step distillation" cites IMDM together with ReDi. ReDi (`arXiv:2507.15897`) supports the conditional total correlation. IMDM's abstract concerns a stochastic infinite-state mask and a factorization-error lower bound; a total-correlation definition was not confirmed. Partial.
6. `07-error-budget.tex:66`, `arXiv:2505.16839` (LaViDa). "LaViDa's prefix mask makes its cache exact and reports CIDEr 117.3 against 121.0". The numbers are correct (Table 3a: full-attention 121.0, Prefix-DLM 117.3). The paper does not describe its cache as exact; "exact" is the manuscript's inference. Mark it as an inference, or add a source for exactness.
7. `01-introduction.tex:18`, `arXiv:2508.10875`. "version 3, 228 references". Version 3 is the current arXiv version. The converted PDF's reference list runs to label [227] (225 distinct labels found), so the count is off by one or two. Check the count against v3 before submission.
8. `07-error-budget.tex:61`, `arXiv:2510.04525`. "the noised sampler approaches a tilted one when the number of masked positions is large against the square of the number committed times a power of the vocabulary size". Theorem 2's regime N much greater than k squared is confirmed. The vocabulary factor was not checked. Partial (minor).
9. `07-error-budget.tex:56`, `arXiv:2502.09992` (LLaDA). "LLaDA above temperature zero" is given as an example of sample-then-filter. LLaDA's text describes low-confidence and random remasking (Algorithms 4 and 5). The temperature behaviour was not checked in the converted text. Unverified detail. The 1/t weight used at `03-notation.tex:60` is supported (Eq. 3: 1/t-weighted masked cross-entropy).
10. `07-error-budget.tex:26`, `arXiv:2505.24857` (EB-sampler), in "Elearn ... an ordering policy moves it". The EB-sampler paper is about a sampler's error decomposition, not ordering effects on model error. Partial; the other two keys in this list (`arXiv:2502.06768`, `arXiv:2602.00286`) are the better support.

### 3c. Unverified sub-claims (cited paper not checked for this claim)

11. `03-notation.tex:43`, `arXiv:2503.20853` (UniDisc) and `arXiv:2505.15809` (MMaDA), for "one shared level". The UniDisc text read in this audit does not state a shared timestep across modalities; MMaDA was not converted. Not checked.
12. `03-notation.tex:43`, `arXiv:2511.09611` (MMaDA-Parallel), for "clean input with noised output". Not checked.
13. `03-notation.tex:59` and `03-notation.tex:60`: equation numbers for MD4 (Eq. 5), MDLM (Eq. 13), Zheng et al. (Eq. 6, Prop. 3.1). The equations were not located in this audit. MDLM's time-independent network (Section 4.1) was confirmed.
14. `03-notation.tex:46`, `arXiv:2407.15595` (DFM), for "token editing". DFM's paths were read (uniform-noise mixture); token editing was not confirmed. Partial.
15. `08-open-problems.tex:44`, `arXiv:2511.09611`. The numbers 59.8, 57.5 and 54.1 are present in the paper. "one run, a language-model judge and no interval": the GPT-4.1 judge is confirmed; the single run and absence of intervals were not checked. "Its released sampler commits no image tokens in the first quarter of the steps" is a code-level (E3) claim that cannot be checked from the PDF.
16. `08-open-problems.tex:53`, `arXiv:2605.12522`. Code and experiment-design claims (one token per step, three block lengths, one seed, no intervals) are marked E3 in the manuscript and were not checked here. Its Theorem 1 (majorisation) and the resample variants were confirmed.
17. `01-introduction.tex:25` and `04-design-space.tex:91`, `arXiv:2508.10875` ("36-model table") and `arXiv:2506.13759` ("no comparison table"). Not checked.

### 3d. Unverifiable

18. `01-introduction.tex:11`, `01-introduction.tex:60`, `06-census.tex:128`, `openreview:Gq4yt8pxRo`. The entry is an anonymous ICLR 2027 double-blind submission under review. Its authors are not available through the OpenReview API, and the ledger holds only its abstract (E1). The claim that "the size and ordering of a measured bias depend on block length and remasking" cannot be checked. Recommend removing these three citations before submission, or replacing them with a published source. The bib comment already says the same.

### 3e. Supported (checked against source)

- `01-introduction.tex:9`: all five sentence-level citations (`arXiv:2107.03006`, `arXiv:2310.16834`, `arXiv:2406.07524`, `arXiv:2406.04329`, `arXiv:2406.03736`, `arXiv:2205.14217`, `arXiv:2502.09992`, `arXiv:2503.20853`, `arXiv:2505.15809`, `arXiv:2408.12528`).
- `01-introduction.tex:11`: `arXiv:2606.29228` (ranking depends on prompt template), `arXiv:2510.18480` (efficiency evaluation), `arXiv:2604.02718` (benchmark choice, generative perplexity).
- `01-introduction.tex:19`, `:20`, `:23`: survey descriptions. `arXiv:2508.08712` inclusion criteria for one subsection (confirmed); `arXiv:2509.24435` systematic-review wording (confirmed; "no search strings or counts" is consistent with the converted text); `arXiv:2506.13759` version 5 and 175 references (confirmed).
- `01-introduction.tex:63`: `arXiv:2505.24857` two-term identity (Eq. 7); `arXiv:2605.12522` majorisation (Theorem 1) and the resample variant; `arXiv:2510.04525` (choose-then-sample); `arXiv:2609.34509` (low-confidence remasking against top-probability selection); `arXiv:2401.01879` (one-token best-of-N bound).
- `03-notation.tex:42`, `:43`: `arXiv:2110.02037` (any-order AR), `arXiv:2503.09573` (clean block prefix), `arXiv:2503.20853` (whole-modality dropout, 10 percent).
- `03-notation.tex:60`: `arXiv:2502.09992` 1/t weight (Eq. 3) and linear masking; `arXiv:2406.03736` any-order objective.
- `03-notation.tex:62`: `arXiv:2409.02908` first-hitting sampler; `arXiv:2107.03006` deterministic forward process.
- `03-notation.tex:63`: `arXiv:2406.03736` and `arXiv:2406.04329` concrete-score ratio for absorbing noise.
- `03-notation.tex:65`: `arXiv:2506.10892` Gaussian-to-uniform map.
- `04-design-space.tex:65` to `:69`: Seed Diffusion edit-based corruption (`arXiv:2508.02193`); Simplax auxiliary Dirichlet variable (`arXiv:2608.10615`); CANDI (`arXiv:2510.22510`); Di4C and copula joint predictors (`arXiv:2410.08709`, `arXiv:2410.01949`); DiffuSeq MBR over 10 candidates (`arXiv:2210.08933`); FUDOKI judge-based selection (`arXiv:2505.20147`).
- `04-design-space.tex:72`: continuous image channels of Transfusion, BAGEL (rectified flow on VAE latents), Show-o2 and D-DiT.
- `04-design-space.tex:74`: `arXiv:2505.16839` prefix mask (described in Section 3 of the paper).
- `05-rq-evidence.tex:12`: `arXiv:2609.01607`, `arXiv:2607.04423` (synergy conditional on architecture); `arXiv:2509.24897` (models struggle to achieve effective synergy; "largely absent" is a paraphrase).
- `06-census.tex:55`: `wilson1927probable` (Wilson score interval, the source of the 1927 paper).
- `06-census.tex:128`: `arXiv:2606.29228`, `arXiv:2606.20536` (FID randomness), `arXiv:2607.24763` (compute-aware remasking protocol).
- `07-error-budget.tex:23`: `arXiv:2505.21400` (random mask sets, training error term); `arXiv:2510.04767` (equality when committed conditionals match the data); `arXiv:2502.09622` (chain-rule steps); `arXiv:2602.00286` (both KL directions); `arXiv:2507.15897`, `arXiv:2608.25505` (total-correlation identity) as listed.
- `07-error-budget.tex:43`, `:45`: `arXiv:2505.24857` Eq. 7 and App. A.1 (equality for deterministic policies).
- `07-error-budget.tex:61`: `arXiv:2503.17076` (linear Gumbel decay in the released MaskGIT code, footnote 1); `arXiv:2510.04525` regime N much greater than k squared.
- `07-error-budget.tex:66`: `arXiv:2503.09573` block-causal KV caching; `arXiv:2406.03736` (time-free network caching) and `arXiv:2406.07524` (time-independent network, Section 4.1); `arXiv:2505.22618` (approximate KV cache); `arXiv:2510.06308` (approximate cached logits and keys).
- `07-error-budget.tex:68`: `arXiv:2602.00286` Prop. C.5 (under a residual-support assumption); `arXiv:2502.09622` App. E.3 (remasking extension).
- `07-error-budget.tex:118`: `arXiv:2503.00307` MAUVE for ReMDM 0.403, 0.610, 0.656 and for MDLM 0.042, 0.037, 0.035 at T = 1024, 2048, 4096; nucleus top-p 0.9 (confirmed).
- `08-open-problems.tex:44`: `arXiv:2503.20853` CLIP 0.301 (steps 1 to 3), 0.312 (all), 0.283 (steps 22 to 24); the shrinking conditional-unconditional logit distance (Appendix, Fig. 24).
- `07-error-budget.tex:56` and `:58` for MaskGIT (`arXiv:2202.04200`) and best-of-N (`arXiv:2401.01879`): supported at the level of the sampler description.
- `07-error-budget.tex:48`: `arXiv:2605.12522`, `arXiv:2510.04525`, `arXiv:2609.34509`, `arXiv:2604.00375` (sample-then-filter and rank-then-sample), `arXiv:2401.01879`.

## 4. Uncited entries and missing keys

- Keys cited in the text with no entry: none. (`acmnumeric` appears in `main.tex` line 10 as a `\citestyle` argument. It is a false positive of the key check, not a missing key.)
- Entries in `references.bib` never cited (15, all arXiv): `arXiv:2305.08379`, `arXiv:2410.13848`, `arXiv:2410.17891`, `arXiv:2412.10193`, `arXiv:2502.13917`, `arXiv:2505.16990`, `arXiv:2505.23606`, `arXiv:2506.20639`, `arXiv:2508.15487`, `arXiv:2509.19244`, `arXiv:2601.15593`, `arXiv:2604.00007`, `arXiv:2606.19475`, `arXiv:2607.13188`, `arXiv:2610.09866`. They were left in the file, since removing them is a manuscript decision. Two have a published version worth citing if the author adds them: `arXiv:2601.15593` (ACL 2026 Findings) and `arXiv:2410.13848` (CVPR 2025).

## 5. Fixes applied to references.bib

- `page2021prisma`: validation comment updated (Crossref DOI 10.1136/bmj.n71 resolves; fields match). No field change.
- `kitchenham2007guidelines`: `note = {Version 2.3}` added; validation comment updated. Verified against bibliographic records; the report PDF itself was not opened.
- `wilson1927probable`: `doi = {10.1080/01621459.1927.10502953}` added (Crossref: JASA 22(158), 209 to 212, 1927).
- `cohen1960coefficient`: `doi = {10.1177/001316446002000104}` added (Crossref: Educ. Psychol. Meas. 20(1), 37 to 46, 1960).
- `openreview:Gq4yt8pxRo`: `author = {Anonymous}` replaces the placeholder; the comment records that the OpenReview record is an anonymous ICLR 2027 submission under review.
- All 85 arXiv entries: a comment line "checked 2026-10-15: arXiv metadata OK. Published version: ..." added above each entry (venue, DOI, and source: Crossref, OpenReview, OpenAlex, arXiv journal_ref, or the arXiv PDF venue header).
- File header comment updated; the "NOT yet validated" and "UNVERIFIED" markers were removed.

Keys unchanged. Brace balance checked (90 entries, none unbalanced). `main.bbl` was not rebuilt; a LaTeX build is needed to confirm the rendered reference list after the DOI and note additions.

## 6. Method and limits

- arXiv metadata: arXiv API `id_list` (85 IDs, batches of 30). Comparison by normalised title, first-version year, and author last names.
- Published versions: OpenReview search (venue field), OpenAlex title search (type, DOI, retraction flag), Crossref `works/<doi>` for each DOI listed (title, container, year, `update-to`), arXiv `journal_ref` and `doi` fields, and the venue header of the arXiv PDF where present. DBLP returned a bot challenge and could not be used.
- Support: arXiv abstracts for all cited keys; converted PDFs (markitdown) for 33 keys, searched for the numbers, equations and sections named in the sentences. Searches were keyword-based, not whole-paper reads.
- Working files are in the session scratchpad (`arxiv.json`, `openalex.json`, `ort.json`, the converted PDFs). None are in the repository.

## 7. Section 9 additions (six entries; citation-validator, 2026-10-15)

Scope: the six keys added to `paper/review/references.bib` for `paper/review/sections/09-exp003.tex` (lines 37 and 73). Ledger rows R0091 to R0096. Only `references.bib` was edited (comments only, so the typeset list is unchanged); no `.tex` file was touched.

| Key | arXiv metadata (API) | Published version | DOI | Support |
|---|---|---|---|---|
| 2305.11846 CoDi | title, 5 authors, 2023 match (v1) | NeurIPS 2023 (Crossref, NeurIPS 36) | 10.52202/075280-0707 | supports (line 37) |
| 2305.10355 POPE | match (v3) | EMNLP 2023 main (Crossref; arXiv comment) | 10.18653/v1/2023.emnlp-main.20 | supports (line 37) |
| 2303.11897 TIFA | match (v3; "Noah A Smith" without period) | ICCV 2023 (Crossref; arXiv comment) | 10.1109/ICCV51070.2023.01866 | supports (line 37) |
| 2310.18235 DSG | match (v4), 9 authors | ICLR 2024 poster (arXiv comment; iclr.cc/virtual/2024/poster/18963) | none | supports (line 37) |
| 2207.12598 CFG | match (v1) | NeurIPS 2021 Workshop DGMs and Downstream Applications, short version (arXiv comment; neurips.cc/virtual/2021/33972; mlanthology). The arXiv text is the longer version. | none | supports (line 73) |
| 1911.03393 MMVAE | match (v1) | NeurIPS 2019 (proceedings.neurips.cc page, title and authors match) | none | supports (line 37) |

Retraction check: Crossref `works/<doi>` returned no `updated-by` and no `update-to` for the three DOIs, and the filter `updates:<doi>` for POPE returned zero items. The three non-DOI items have no Crossref record to test; no retraction notice was found, but that search was limited to the venue pages and one Crossref title query.

Support, from converted PDFs (keyword search of the sections named, not whole-paper reads):
- CoDi: Section 5.3 and Table 10 compare SIM of two outputs generated separately ({P to A, P to B}) against jointly. The separate generation from the same prompt is the independent-draw control. Fits the sentence. Note that CoDi's control is separate generation per modality from one prompt; the sentence says "same-condition independent-draw", which is a fair reading, though CoDi does not use seed balancing or a sibling draw of the same modality.
- POPE: polling questions "Is there a X in the image?" with Yes/No answers.
- TIFA: questions are binary yes/no (17,226) and multiple-choice (8,603). Yes/no presence probes are part of its question set, not all of it.
- DSG: questions have an expected binary yes/no answer; entity questions of the form "is there a motorcycle?".
- MMVAE: Section 4, Table 2: joint-generation coherence scored by off-the-shelf MNIST and SVHN digit classifiers. The sentence says "the criterion of multimodal VAEs"; this holds for MMVAE, and the generalisation to the whole family was not checked.
- CFG: abstract and text state that guidance trades sample quality against diversity and decreases diversity. It is cited only for the direction expected, not for the measured numbers on line 73, which are labelled exploratory in the text.

No does-not-support entry. Gate: pass for these six. Limits: OpenReview (blocked by a challenge page) was not usable for the CFG workshop record; the workshop venue rests on the arXiv comment, the neurips.cc listing and mlanthology, which agree.
