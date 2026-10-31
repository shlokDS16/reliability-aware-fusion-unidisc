```yaml
agent: citation-validator
date: 2026-10-31
brief: Verify six new bib entries (du2026dymo, han2026aemrl, guo2026dmmf, qiu2024benchmarking, buades2005nonlocal, huber2009robust) and their citing sentences in paper2-tnnls; no file edits
sources_examined:
  - paper2-tnnls/references.bib lines 868-921
  - paper2-tnnls/sections/related.tex lines 44-91
  - paper2-tnnls/tables/tab_baselines.tex
  - paper2-tnnls/sections/study2.tex line 312 and supplement/supplement.tex lines 537-538 (context for the buades use)
  - Crossref api.crossref.org/works/10.24963/ijcai.2026/128, 10.1109/TCSVT.2026.3727902, 10.1109/CVPR.2005.38, 10.1002/9780470434697 (metadata and update fields)
  - Crossref filter updates:<doi> for the four DOIs (0 notices each)
  - arxiv.org/abs/2601.22853 (DyMo)
  - arxiv.org/abs/2212.08044 (Qiu, arXiv metadata incl. DMLR 2024 journal line)
  - arxiv.org/html/2212.08044v3 (Qiu Sec. 3.1, 4.1; via WebFetch summary, secondary extraction)
  - mlanthology.org/dmlr/2024/qiu2024dmlr-benchmarking (BibTeX-derived volume and pages, aggregator)
  - ieeexplore.ieee.org/document/11667659 (DMMF; no abstract returned)
  - openreview.net/forum?id=Vc1fXQ8mJg (challenge page, no record); api2.openreview.net (403 challenge)
  - data.mlr.press/v1/v01-2.html (404); data.mlr.press/assets/pdf/v01-2.pdf (too large, not read)
coverage: All six entries checked for authors, title, venue, year, pages, DOI resolution and update notices. Citing sentences checked at the abstract or metadata level; no full text was read for any entry. Not covered: DMMF full text; Qiu publisher page; Huber book contents; OpenReview ICLR record for DyMo.
claims:
  - statement: All six bib entries match their primary or publisher record on authors, title, venue and year
    status: mixed
    evidence: see per-entry table; Qiu has no DOI and its volume/pages rest on an aggregator only
    level: E3
    confidence: 0.85
  - statement: No retraction or correction notice exists for the four DOIs
    status: supported
    evidence: Crossref filter updates:<doi> returned total 0 for 10.24963/ijcai.2026/128, 10.1109/TCSVT.2026.3727902, 10.1109/CVPR.2005.38, 10.1002/9780470434697; no update-to field in any of the four records
    level: E3
    confidence: 0.9
  - statement: related.tex:52-53 (DyMo) describes the cited work
    status: supported
    evidence: arXiv 2601.22853 abstract (adaptive selection of recovered modalities at inference; reward from a task-loss proxy)
    level: E2
    confidence: 0.85
  - statement: related.tex:47 (AEMRL) lists it among evidential methods that attach reliability per modality
    status: supported
    evidence: DOI 10.24963/ijcai.2026/128 abstract (D-EUE per-modality reliability; AFCAC weights evidence streams)
    level: E2
    confidence: 0.85
  - statement: related.tex:49-50 (DMMF) sets modality weights from data and model uncertainty, and leaves token-level uncertainty open
    status: mixed
    evidence: title and Crossref metadata support the first clause; abstract not retrieved for the second clause
    level: E1
    confidence: 0.5
  - statement: related.tex:87-88 (Qiu) 17 corruptions at five severities, COCO retrieval, no unified masked diffusion model among the tested models
    status: supported
    evidence: arXiv 2212.08044v3 Sec. 3.1 (17 image perturbations, five levels per category) and Sec. 4.1 (COCO-IP, COCO-TP for retrieval; 12-model list with no masked or discrete diffusion model)
    level: E2
    confidence: 0.75
  - statement: tab_baselines.tex:65,68 (Buades) cites the non-local means method used for the denoise rows
    status: supported
    evidence: supplement.tex:538 uses OpenCV fastNlMeansDenoisingColored; the cited CVPR 2005 paper introduces non-local means (grayscale)
    level: E2
    confidence: 0.8
  - statement: tab_baselines.tex:24,29 (Huber) cites the book for the median and 20% trimmed mean
    status: unknown
    evidence: book record verified; chapter contents not retrieved
    level: E1
    confidence: 0.5
competing_explanations: []
unknowns:
  - DMMF token-level claim needs the full text (research/paper2/sources note named in related.tex:48 was not in my brief and was not read)
  - Qiu volume and pages: publisher page not retrievable; OpenReview forum id not confirmed
  - Huber 2nd edition contents: which section covers median and trimmed mean
  - DyMo ICLR 2026 venue confirmed from the arXiv page only, not from the ICLR/OpenReview record
next_test: {hypothesis: none, intervention: none, primary_metric: none, falsifier: none, gpu_hours: 0}
```

# Citation check, 2026-10-31

Scope: the six new entries in `paper2-tnnls/references.bib`, and each citing sentence in `sections/*.tex` and `tables/tab_baselines.tex`. No file was edited. Ledger rows were not added, because the brief said not to edit any file.

## Per-entry verdicts

| Key | Verdict | Checked against | Notes |
|---|---|---|---|
| du2026dymo | OK | arXiv 2601.22853 (abstract page): title, authors (Du, Luo, O'Regan, Qin), "ICLR 2026" | No DOI (arXiv-era ICLR paper). Pages not needed. The ICLR/OpenReview record was not reachable (challenge page), so the venue rests on the arXiv page. |
| han2026aemrl | OK | Crossref 10.24963/ijcai.2026/128 | Title exact. Six authors in order (Han, Zhang, Wang, Pan, Liu, He). Pages 1143-1151 match. Year 2026. No update notice. |
| guo2026dmmf | OK (metadata); sentence UNVERIFIABLE in part | Crossref 10.1109/TCSVT.2026.3727902 | Title exact. Nine authors in order, all match. Journal abbreviation matches Crossref short title. Early access: Crossref has no volume or issue, only page "1-1", so none was added. The IEEE Xplore abstract could not be retrieved, so the clause "whose authors leave token-level uncertainty open" (related.tex:49-50) is unverified. |
| qiu2024benchmarking | UNVERIFIABLE (volume, pages, url) | arXiv 2212.08044 (author list, title, DMLR 2024); MLAnthology DMLR 2024 entry | No DOI in Crossref, and no Crossref record for the DMLR paper. Title, eight authors in order, and year 2024 match. MLAnthology gives volume 1, pages 1-56 (a BibTeX-derived aggregator), but the publisher page (data.mlr.press) returned 404 and its PDF was too large to read. Per the brief, these are not filled. The OpenReview forum URL could not be confirmed (challenge-gated). |
| buades2005nonlocal | OK | Crossref 10.1109/CVPR.2005.38 | Title exact. Volume 2, pages 60-65 match. Year 2005. Crossref gives initials only (A., B., J.-M.); the full forenames in the bib are not contradicted, but were not checked against the PDF. No update notice. |
| huber2009robust | OK (metadata) | Crossref 10.1002/9780470434697; publisher listing (Wiley 2nd ed., 2009) | Authors and title match. Crossref has `edition-number: 1`, which conflicts with `edition = {2nd}`. The 2nd edition is supported by the Wiley listing (print ISBN 978-0-470-12990-6) and the 2009 date, so keep `2nd` after checking the Wiley edition statement. The use for the median and trimmed mean is not verified at chapter level. |

## FIX entries

None. No bib field is wrong on the evidence available. The changes the brief allowed (volume or pages) are not verified for Qiu, so none is applied.

## UNVERIFIABLE items

1. guo2026dmmf, related.tex:49-50: the token-level clause needs the full text or the IEEE abstract.
2. qiu2024benchmarking: volume 1 and pages 1-56 are reported only by MLAnthology. Verify them against the DMLR publisher page or the PDF before adding. Also confirm the OpenReview URL or replace it with the publisher URL.
3. huber2009robust, tab_baselines.tex:24,29: the book is a standard reference for these estimators, but the section that covers them was not checked. Add a page or section pinpoint if the authors have the book.

## Citing sentences (summary)

- du2026dymo, related.tex:52-53: supported (abstract).
- han2026aemrl, related.tex:47: supported (abstract).
- guo2026dmmf, related.tex:49-50: first clause supported by title and metadata; second clause unverified.
- qiu2024benchmarking, related.tex:87-88: supported. arXiv v3 Sec. 3.1 (17 image perturbations, five levels per category) and Sec. 4.1 (COCO-IP and COCO-TP for retrieval; no masked or discrete diffusion model in the 12-model list). The fetch was a summary of the HTML, not a direct read. The Qiu paper itself gives 9 models in its conclusion and 12 in Sec. 4.1, so the sentence avoids a model count.
- buades2005nonlocal, tab_baselines.tex:65,68: supported as the method citation. The supplement (line 538) uses OpenCV `fastNlMeansDenoisingColored`, a colour variant; the 2005 CVPR paper is the grayscale non-local means algorithm. Acceptable, but a reviewer may ask for the colour-mode reference.
- huber2009robust, tab_baselines.tex:24,29: unverified at section level.

## Retractions and corrections

Crossref `filter=updates:<doi>` returned zero notices for the four DOIs (han2026aemrl, guo2026dmmf, buades2005nonlocal, huber2009robust). No `update-to` field is present. No withdrawal note was seen on the arXiv pages (du2026dymo, qiu2024benchmarking).

## Concerns (for the orchestrator)

1. Qiu: volume and pages not verified from the publisher; OpenReview URL unconfirmed.
2. DMMF: "leave token-level uncertainty open" needs a full-text check (the source note named in related.tex:48 was out of brief and was not read).
3. Huber: Crossref `edition-number` says 1; confirm the 2nd edition on the Wiley page.
4. Ledger rows were not added, because the brief said not to edit any file. Add them with `tools/ledger.py` if wanted.
