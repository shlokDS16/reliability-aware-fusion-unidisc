```yaml
agent: citation-validator
date: 2026-10-29
brief: Validate every reference of Paper 2 (paper2/references.bib; cited from paper2/main.tex and paper2/sections/*.tex; TMLR copy paper2-tmlr/ has the same bib content)
sources_examined:
  - Crossref REST api.crossref.org/works/<doi> for the 33 bib entries that carry a DOI (title, authors, container, volume, issue, pages, issued date, update-to, updated-by); saved scratchpad crossref.json
  - DataCite api.datacite.org/dois/10.48550/arxiv.<id> and OpenAlex api.openalex.org/works/doi:10.48550/arxiv.<id> for the 34 arXiv ids in the bib plus 2603.06577, 1705.01359, 1907.07484, 1903.12261, 2605.26436 (title, authors, versions, is_retracted, venue locations); saved scratchpad oa_dc.json
  - arXiv abs pages via WebFetch (comments, journal-ref, version history): 2603.06577, 2505.23606, 2310.16834, 2503.20853, 2602.11590, 2510.01384, 2602.02927, 2607.13188, 2602.22246, 2610.22380, 2604.18738, 2509.23653, 2602.04096, 2406.06525, 2505.16839, 2404.18947
  - Publisher/proceedings pages: proceedings.neurips.cc (D3PM, LaViDa), proceedings.iclr.cc (RADD, CRC), proceedings.mlr.press (CLIP v139, SEDD v235, Omni-Diffusion v306), aclanthology.org (uChecker, FOIL via search), github.com/bethgelab/imagecorruptions README
  - Full texts read this session: arXiv 2504.01225 (Gomes), 2305.16397 (Krojer), 2209.07068 (uChecker), 2406.06525 (LlamaGen), 2208.02814 (CRC); local files research/sources/md/{2503.20853,2412.06474,2602.02927,2602.22246}.md and 2607.13188.txt grepped for the specific sentences
  - Earlier E2 reads relied on (not repeated): research/paper2/related/TRUST-BUT-VERIFY-READ-2026-10-28.md, CLOSEST-WORK-2026-10-28.md, REFERENCES-DRAFT-2026-10-28.md
coverage: >
  All 54 bib entries: existence and metadata against a primary or index record; retraction/correction status; cite-key usage by grep
  of paper2/main.tex and paper2/sections/*.tex (comment lines skipped) and of paper2-tmlr/sections. Every citation sentence was read in
  context (introduction.tex, related.tex, and the cite lines of method.tex, protocol.tex, discussion.tex). Claim basis per entry is
  coded F (full text read), A (abstract read), T (title and metadata consistent; abstract not re-read this session), X (not
  verifiable without access). NOT covered: ScienceDirect/IEEE/JSTOR full texts and abstracts for the five Information Fusion
  papers and several classical papers (no access; Cloudflare/redirect pages); the arXiv export API (HTTP 429 for the whole
  session, so DataCite+OpenAlex+abs pages were used instead); the content of the two corrigenda; TMLR sentence-level differences
  (the bib is identical to paper2 apart from the header comment; cite keys match).
claims:
  - statement: "Every one of the 54 bib entries exists and its authors, title, venue, year and pages agree with Crossref/DataCite/OpenAlex."
    status: supported
    evidence: "scripted comparison of 33 Crossref records (cmp.py): all titles, author family names and counts, volumes, issues, pages and years match (one false alarm, Denoeux, is a diacritic encoding artefact); 34 arXiv ids all resolve with the same title and author count"
    level: E2
    confidence: 0.95
  - statement: "No entry is retracted or withdrawn; two have a corrigendum."
    status: supported
    evidence: "Crossref update-to/updated-by empty for 31 DOIs; khaleghi2013multisensor -> 10.1016/j.inffus.2012.10.004 (Information Fusion 14(4):562); wang2025multistage -> 10.1016/j.inffus.2025.103287 (vol 122, art. 103287). OpenAlex is_retracted=false for all arXiv ids. Content of the two corrigenda not read."
    level: E1
    confidence: 0.85
  - statement: "No cited source contradicts the sentence that cites it, but eight sentences are only partly supported or cannot be checked without access."
    status: mixed
    evidence: "sections 3 and 4 below"
    level: E1-E2
    confidence: 0.8
  - statement: "The three \\todo citation placeholders can be filled with verified entries."
    status: supported
    evidence: "section 5: Omni-Diffusion (PMLR 306), FOIL (ACL 2017, Crossref), imagecorruptions (Michaelis et al. 2019 plus Hendrycks and Dietterich ICLR 2019)"
    level: E2
    confidence: 0.9
competing_explanations: []
unknowns:
  - "Abstract of Zhou and Lu (Information Fusion 139, 104860): only a secondary web listing was reachable; the Clopper-Pearson phrase cannot be confirmed from a primary record."
  - "Whether Wang et al. use split conformal prediction and prediction sets (abstract says only 'conformal prediction method')."
  - "Primary record for Finn and Johnson 1968 (RCA Review 29(3)); only CiNii/OpenAlex index records seen."
  - "Venues stated only in arXiv comments (Muddit ICLR 2026, ProSeCo NeurIPS 2026, Trust but Verify NeurIPS 2026 workshop) have no proceedings record yet."
next_test: n/a (citation audit)
gate: FAIL (three open \todo citations; Zhou and Lu claim unverified at primary level; see section 6)
ledger_rows_added: 0 (brief limits the commit to this report; ledger rows left to the lead)
```

# Paper 2 citation audit, 2026-10-29

Bib: `paper2/references.bib`, 54 entries, no duplicate key, DOI, arXiv id or title. `paper2-tmlr/references.bib` is identical except the header comment, so every finding applies to both. Cited in the text: 52 entries. The same 52 keys are cited in `paper2-tmlr/sections`. Every key cited in the text exists in the bib. The header comment ("49 entries", "references-draft.bib") is stale.

## 1. Summary

| Item | Result |
|---|---|
| Wrong metadata | 0 hard errors. 5 improvements (published version available or pages missing), section 2 |
| Non-existent or unverifiable | 0 non-existent. 1 weakly verified (finn1968adaptive: index record only, no DOI exists) |
| Retracted or withdrawn | 0. Two corrigenda (khaleghi2013multisensor, wang2025multistage), neither a retraction. The withdrawn arXiv 2605.26436 is correctly not cited; yao2026remask cites its superseding id 2604.18738 (confirmed v3, 2026-08-20) |
| Unsupported sentences | 0 contradicted. 8 partial or not verifiable (section 4) |
| Duplicates | 0 |
| Never cited | 2: `hessel2021clipscore`, `radford2021clip` (delete from the .bib) |
| `\todo` citation placeholders | 3 (protocol.tex:235 Omni-Diffusion, protocol.tex:280 FOIL, and the imagecorruptions suite, which has no `\todo` in the text yet; the suite is in protocol.tex:238 and results.tex:460). Verified entries in section 5 |
| Information Fusion papers | 6, all confirmed by Crossref container-title "Information Fusion" (section 7) |
| Cap | 52 cited now; 55 after adding the three entries below (56 if Hendrycks is also added); 5 drops needed (6), section 8 |

## 2. Metadata corrections and upgrades (apply in both bibs)

Checked against Crossref (DOI entries) or DataCite+OpenAlex+arXiv abs page (arXiv entries). Fields not listed here matched.

| Key | Finding | Correction |
|---|---|---|
| lou2024sedd | `@misc` arXiv v3, year 2023 under a 2024 key. A published version exists: ICML 2024, PMLR 235, pp. 32819-32848 (proceedings.mlr.press/v235/lou24a.html; arXiv comment "ICML 2024 Oral") | Elsevier rule is to cite the published version: `@inproceedings`, booktitle "Proceedings of the 41st International Conference on Machine Learning", series PMLR, volume 235, year 2024, pages 32819--32848, url https://proceedings.mlr.press/v235/lou24a.html. Not needed if the entry is dropped (section 8) |
| austin2021d3pm | OK. Pages missing | Add pages 17981--17993 (proceedings page metadata) |
| ou2025radd | OK. Pages missing | Add pages 64972--65009 (proceedings page metadata) |
| li2025lavida | OK. Pages missing | Add pages 105101--105134 (NeurIPS 2025 page metadata). Crossref has no DOI record seen for it; keep the url |
| angelopoulos2024crc | OK. Pages missing | Add pages 55198--55218 (ICLR 2024 proceedings metadata) |
| swerdlow2025unidisc | arXiv v1 only, abs page lists no journal reference, OpenAlex shows no published location | Keep as preprint. Re-check before submission |
| shi2025muddit | `@misc`, ICLR 2026 stated only in the arXiv comment (v5, 2026-05-26) | Keep as is (the note says so) or switch to ICLR 2026 once a proceedings record exists |
| schiff2026proseco | NeurIPS 2026 only in the arXiv comment (v4, 2026-10-20) | Keep as is |
| zhou2027burden | Crossref: vol 139, issued 2027-03 (print), article 104860; Semantic Scholar publicationDate 2026-10-01. Key and year say 2027 | Correct for the volume year. Confirm on ScienceDirect whether the style should show the online-first year 2026 |
| vovk2005algorithmic | OK (Springer, New York, 2005, DOI 10.1007/b106715). A second edition (Springer, 2022, DOI 10.1007/978-3-031-06649-8) exists | Keep 2005 if that is the edition read; otherwise cite the 2022 edition |
| holm1979sequentially | OK: Scand. J. Statist. 6(2):65-70 (OpenAlex). The DOI 10.2307/4615733 is on the OpenAlex record | Optional: add `doi = {10.2307/4615733}`. JSTOR page itself blocked (Cloudflare) |
| finn1968adaptive | Only CiNii/OpenAlex index records seen (OpenAlex pages 414-463, bib 414-464 per CiNii). No DOI exists, none guessed | Keep the note. Weakest-verified entry of the bib |
| header comments | "this file: 49 entries" and "references-draft.bib" are stale | Update to 54 (then 50 or fewer) |

Minor, harmless: Crossref prints Gomes as "Goncalo Emanuel Cavaco"; bib "Gonçalo" is fine. Krojer's fifth author is "Christopher Pal" in arXiv and "Chris Pal" in Crossref; bib uses "Christopher", fine.

## 3. Per-entry table

Basis codes: F full text read, A abstract read this session, T title/metadata consistent only (abstract not re-read), X not verifiable without access. Status = supports / partial / does-not-support. "Cited at" gives file:line.

### A. Masked diffusion, unified models, tokenizer

| Key | Verified against | Basis | Status | Cited at / comment |
|---|---|---|---|---|
| austin2021d3pm | proceedings.neurips.cc page; DataCite 5 authors v3 | T | supports | intro:13, related:10 |
| lou2024sedd | arXiv abs (ICML 2024 Oral); PMLR v235 page | T | supports | related:10. Upgrade to ICML 2024 (section 2) |
| sahoo2024mdlm | Crossref 10.52202/079017-4135, pp. 130136-130184, 8 authors | T | supports | intro:13, related:11 |
| ou2025radd | proceedings.iclr.cc page; arXiv 2406.03736 | T | supports | intro:13, method:247, related:12. The title is the property cited ("models the conditional distributions of clean data") |
| nie2025llada | Crossref 10.52202/085713-1689 | T | supports | related:11 ("scaled") |
| chang2022maskgit | Crossref 10.1109/CVPR52688.2022.01103 | T | supports | related:14 |
| swerdlow2025unidisc | arXiv abs v1; local text research/sources/md/2503.20853.md | A, F | supports | intro:18,67; protocol:19,154; related:14,17,96. Whole-modality dropout at 10% in training (md line 377); App. G.1 overlays COCO objects, LLM-made wrong captions, "randomly mask the image and text inputs and unmask", best-of-n "own likelihood" (md lines 1735-1739), no metric. 1.4B size confirmed by earlier E2 read |
| yang2025mmada | Crossref 10.52202/085713-4636 | T | supports | intro:18, related:14 |
| li2025lavida | proceedings.neurips.cc page; arXiv abs | A | partial | intro:18, related:14. Cited as a model that puts "two or more modalities in one token sequence" and as a "unified text-image model". LaViDa is an understanding-only VLM ("equipping DMs with a vision encoder"); DiSP's text (md line 167) records continuous visual embeddings for LaViDa. Fix: move it out of the unified group or say "multimodal diffusion language models" |
| shi2025muddit | arXiv abs v5 | T | supports | intro:18, related:14 |
| sun2024llamagen | arXiv full text | F | supports | protocol:21. Text states codebook size 16384 and downsample ratio 16; 512 px / 16 = 32x32 = 1024 tokens as the paper says. The name "VQ-16" does not occur in the paper text; it is the repository's label. Say "the downsample-16 VQ tokenizer of LlamaGen (codebook 16 384)" |

### B. Remasking and self-correction

| Key | Verified against | Basis | Status | Cited at / comment |
|---|---|---|---|---|
| wang2025remdm | Crossref 10.52202/085713-4927 | T | supports | intro:55, related:24 |
| kim2025prism | arXiv abs v4 (2026-05-22), no venue, no journal-ref | T (abstract read in the 10-28 check) | supports | intro:55, related:25 |
| schiff2026proseco | arXiv abs v4; comment NeurIPS 2026 | T | supports | intro:55, related:25 |
| huang2025remedi | arXiv abs v1 (comments "24 pages, 11 figures", no venue) | T | supports | intro:55, related:25 |
| zhai2026core | arXiv abs v3 (2026-03-13; comments empty) | T | supports | intro:55, related:24 |
| yao2026remask | arXiv abs v3 (2026-08-20); abstract: training-free T2M remasking of low-confidence tokens | A | supports | intro:55, related:24. The note about the withdrawn 2605.26436 is right |
| lezama2022tokencritic | Crossref 10.1007/978-3-031-20050-2_5; local text 2209.04439.txt | F (10-28 read) | supports | intro:55, protocol:161, related:26 |

### C. Closest work

| Key | Verified against | Basis | Status | Cited at / comment |
|---|---|---|---|---|
| ouyang2026freecorrection | arXiv abs v1; local text 2602.02927.md | A, F | supports | intro:57, protocol:161, related:28,95. Training-free; remasks by predicted probability of the committed token with that position re-masked (md line 419); "schedule tuned on a validation set" (Table row) rests on the earlier E2 read, only a "validation set" line (md line 600) was re-found |
| jhingran2026trustverify | arXiv abs v1; E2 read in TRUST-BUT-VERIFY-READ-2026-10-28.md | A, F | supports | intro:59, protocol:149, related:38,92. 170M model, uniform-mixing finetune, annealed threshold, clean false-edit below 0.4% all in the abstract. The note "NeurIPS 2026 workshop AI for Stochastic Dynamics" is in the comment field. related:39-40 "finetuned with substituted context tokens" is incomplete (hard-negative mixture too) but not wrong |
| gomes2025crc | Crossref 10.18653/v1/2025.findings-acl.638; full text | F | supports | intro:62, related:72,93. Hoeffding and Bentkus bounds (text lines 381, 392, Proposition 3), FOIL-it benchmark, FDR/FPR control confirmed |
| le2026co2jump | arXiv abs v1; local text 2607.13188.txt | A, F | supports | intro:57, protocol:161, related:30,94. "Remasking jump retracts commitments when cross-modal evidence contradicts"; "death quota" and self-confidence plus cross-modal term in the text (lines 541, 235-256) |
| fang2025dropout | Crossref 10.52202/085713-4991; local text 2412.06474.md | F | supports | related:57,97. Hand-fixed dropout probabilities (section 7.2) and majority voting over K masked inputs confirmed |
| wan2026disp | arXiv abs v1; local text 2602.22246.md | A, F | partial | related:58. Text: "masks visual tokens of high saliency at inference to remove backdoor behaviour". The method masks the highest-saliency visual tokens to purify the model's own responses to poisoned training inputs and then fine-tunes; the inference-time masking is the observation behind it. Reword: "masks the visual tokens of highest saliency to purify poisoned training responses before finetuning" |

### D. Conformal prediction

| Key | Verified against | Basis | Status | Cited at / comment |
|---|---|---|---|---|
| angelopoulos2024crc | arXiv full text; proceedings.iclr.cc | F | supports | method:181, related:71. Theorem 1 is the bounded, non-increasing, right-continuous loss result with bound B; the paper's indicator loss is right-continuous. Proposition proof sentence omits "right-continuous" and "exchangeable" but both are in the proposition |
| angelopoulos2023gentle | Crossref 10.1561/2200000101, FnT ML 16(4):494-591 | T | supports | related:69 |
| bates2023outliers | Crossref 10.1214/22-AOS2244, Ann. Stat. 51(1):149-178 | T | supports | related:70. Sole support for the conformal p-value / FDR sentence |
| vovk2005algorithmic | Crossref 10.1007/b106715 | T | supports | related:69 |

### E. Matching metrics, datasets, masked-likelihood scoring

| Key | Verified against | Basis | Status | Cited at / comment |
|---|---|---|---|---|
| hessel2021clipscore | Crossref 10.18653/v1/2021.emnlp-main.595 | T | n/a | never cited. Delete |
| radford2021clip | proceedings.mlr.press v139 page | T | n/a | never cited. Delete |
| lin2014coco | Crossref 10.1007/978-3-319-10602-1_48 | T | supports | protocol:20. The paper cites the 2014 dataset paper for the val2017 split; standard practice |
| krojer2023diffusionitm | Crossref 10.52202/075280-0367; full text | F | supports | related:66. "Normalised by the unconditional (no text) error" (text lines 107-108, 130, 352) |
| salazar2020mlm | Crossref 10.18653/v1/2020.acl-main.240 | T | supports | related:62 |
| kauf2023plwl2r | Crossref 10.18653/v1/2023.acl-short.80 | T (10-28 abstract check) | supports | method:138, related:63. Sole support for the word-level score sentence |
| li2022uchecker | arXiv full text; aclanthology.org/2022.coling-1.248 (search result: COLING 2022, pp. 2812-2822) | F | supports | related:64. Eq. 5 flags a token when its predicted probability is below a threshold; the MLM is fine-tuned with confusion-set-guided masking |

The bib has `@misc` arXiv for uChecker with the note "no Crossref record or DOI was found". The ACL Anthology record exists: upgrade to `@inproceedings`, booktitle "Proceedings of the 29th International Conference on Computational Linguistics", pages 2812--2822, url https://aclanthology.org/2022.coling-1.248/ (the proceedings page itself was not opened; volume number and pages come from a search result, so open the page before applying; no DOI is claimed).

### F. Classical fusion

| Key | Verified against | Basis | Status | Cited at / comment |
|---|---|---|---|---|
| finn1968adaptive | CiNii/OpenAlex index only | X | supports (title) | intro:34, related:106. See section 2 |
| rohling1983cfar | Crossref 10.1109/TAES.1983.309350; OpenAlex abstract | A | supports | intro:34, related:106. Abstract: adaptive threshold to obtain constant false-alarm rate |
| diao2024radar | Crossref 10.1109/MAES.2022.3177395 (IEEE AESM 39(9):4-24) | T | supports | related:106 (triple) |
| willsky1976survey | Crossref 10.1016/0005-1098(76)90041-8 | T | supports | intro:32, related:106 |
| gao2015survey | Crossref 10.1109/TIE.2015.2417501; OpenAlex abstract | A | supports | intro:32, related:106 |
| chair1986optimal | Crossref 10.1109/TAES.1986.310699; OpenAlex abstract | A | supports | intro:26, method:475, protocol:257, related:107. Abstract: "decisions are weighted according to the reliability of the detector and then a threshold comparison" matches intro:25-26 almost verbatim |
| tenney1981detection | Crossref 10.1109/TAES.1981.309178; OpenAlex abstract | A | supports | intro:26 |
| vempaty2013byzantine | Crossref 10.1109/MSP.2013.2262116; OpenAlex abstract | A | partial | intro:28. Cited with Khaleghi for "imperfect and spurious data are a first-order difficulty". The review treats malicious data falsification at a fusion centre; it supports "falsified data" more than "spurious data" |
| kittler1998combining | Crossref 10.1109/34.667881; OpenAlex abstract | A | partial | related:107. Cited for "decision fusion with weighted reliabilities". The abstract develops sum/product combination rules and finds the sum rule best; it does not weight sources by reliability. Chair and Varshney carry the sentence |
| khaleghi2013multisensor | Crossref 10.1016/j.inffus.2011.08.001 (Information Fusion 14(1):28-44); corrigendum 14(4):562 | T (no abstract retrieved) | supports | intro:28. Information Fusion paper |
| rubin1976inference | Crossref 10.1093/biomet/63.3.581 | T | partial (wording) | method:262, related:109. Rubin defines when missingness is ignorable. A gate that selects by the values of the very tokens it then withholds is the non-ignorable case. method:262 says "The gate selects on the observed values, so the missingness is informative": selection on values that remain observed is ignorable in Rubin's sense. Say "selects on the values of the tokens it withholds" |

### G. Statistics

| Key | Verified against | Basis | Status | Cited at |
|---|---|---|---|---|
| mcnemar1947 | Crossref 10.1007/BF02295996 | T | supports | protocol:169 |
| holm1979sequentially | OpenAlex (vol 6, pp. 65-70, DOI 10.2307/4615733) | T | supports | protocol:175 |
| clopper1934 | Crossref 10.1093/biomet/26.4.404 | T | supports | protocol:178 |

### H. Information Fusion papers

| Key | Verified against | Basis | Status | Cited at / comment |
|---|---|---|---|---|
| zhou2027burden | Crossref (Information Fusion 139, 104860, issued 2027-03, 2 authors); no update notice | X (partial) | partial, unverified at primary level | intro:63, related:118, discussion:130,151,191,195. Only a Chinese-language listing (ebiotrade.com, mis-numbered "volume 17") was reachable. It supports: default VLM kept unless a calibrated evidence score clears a threshold; Dempster-Shafer masses combined by Dempster's rule; Clopper-Pearson bounds used to pick a coverage-accuracy operating point; the challenger evidence comes from a CLIP text-matching channel and a DINOv3 visual channel; 18-46% of conflicts are harmful overrides. It does not support, and I could not confirm, the exact wording "a Clopper-Pearson bound on harmful overwrites" (intro:64, related:119) or "two vision-language recognisers" (the challenger is two frozen channels, one of them a purely visual encoder). Read the real abstract on ScienceDirect before submission (the existing `\todo` already asks for the full text) |
| huang2025evidential | Crossref (113, 102648); arXiv 2309.05919 abstract via search | A | supports | intro:31, discussion:134, protocol:257, related:114. Mass functions per modality, contextual discounting with learned reliability coefficients, Dempster's rule. The arXiv version has a different title; the abstract was read on that version |
| shao2024ddef | Crossref (103, 102113); OpenAlex abstract | A | supports (partial on "discount") | intro:31, discussion:134, related:114. Abstract: varying importance of modalities, Dirichlet/BBA, Dempster-Shafer dual-level fusion. The word "discount" is not in the abstract; "attach a reliability to each modality and discount it" is true of Huang et al., not shown for Shao et al. |
| wang2025multistage | Crossref (120, 103068); corrigendum 10.1016/j.inffus.2025.103287 (content unread) | A | partial | discussion:134, related:120. Abstract: multistage multimodal fusion network with "conformal prediction method" that flags unreliable predictions for physician intervention. "Split" conformal and "prediction sets" are not in the abstract. related:123-124 and discussion:134 also speak of Wang et al.'s "conformal-prediction section"; if that section was not read, remove the phrase |
| zhang2026lowquality | Crossref (135, 104437); arXiv 2404.18947 abstract | A | supports | intro:30, related:116. Four settings: noisy, incomplete, imbalanced, quality-varying data |

## 4. Sentences needing a change (ordered by importance)

1. related.tex:118-120 and intro:63-65 (Zhou and Lu). "Keep-or-override gate between two vision-language recognisers whose threshold is chosen with a Clopper-Pearson bound on harmful overwrites". Not confirmed at primary level. Reword to what the secondary listing supports until the abstract is read: "replaces a default vision-language prediction by a challenger's only when a Dempster-Shafer evidence score clears a calibrated threshold, with Clopper-Pearson bounds used to set the operating point". discussion:151 "selective-risk bound on the harm of an action, as described for Zhou and Lu" is not confirmed at all. Mark: not verifiable without access.
2. related.tex:120 and discussion:134 (Wang et al.). Remove "split" and "sets", or confirm from the article. Remove "conformal-prediction section" unless it was read.
3. related.tex:58 (DiSP). Reword as in section 3C.
4. intro:18 / related:14 (LaViDa). Not a unified text-image model with discrete tokens in one sequence.
5. method.tex:262 (Rubin). Wording of "selects on the observed values".
6. related.tex:107 (Kittler). Delete the cite from "decision fusion with weighted reliabilities" or change the sentence ("combination rules for classifiers").
7. intro:28 (Vempaty). Sentence is "imperfect and spurious data"; Vempaty covers falsified data. Keep Khaleghi only, or reword.
8. intro:23-27 and method:475 (Chair and Varshney). The paper sums per-token log-likelihood ratios; Chair and Varshney fuse local binary decisions with reliability weights. The additive form is the same; the sentence "that is the rule used to fuse local decisions" is an analogy. The intro itself says the gate is not decision-level, so word it as "the same additive form as the optimal fusion of independent local decisions".

## 5. The `\todo` citation placeholders: verified entries

All fields below were seen on the cited record on 2026-10-29.

1. Omni-Diffusion (protocol.tex:235, family R). The model named in the text is "an 8B unified masked diffusion model quantised to 4 bits".
```bibtex
@inproceedings{li2026omnidiffusion,
  author    = {Li, Lijiang and Long, Zuwei and Shen, Yunhang and Gao, Heting and Cao, Haoyu and Sun, Xing and Shan, Caifeng and He, Ran and Fu, Chaoyou},
  title     = {Omni-Diffusion: Unified multimodal understanding and generation with masked discrete diffusion},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning},
  series    = {Proceedings of Machine Learning Research},
  volume    = {306},
  year      = {2026},
  pages     = {68853--68867},
  url       = {https://proceedings.mlr.press/v306/li26dv.html},
  note      = {arXiv:2603.06577}
}
```
Seen: arXiv abs page (9 authors; v1 2026-03-06, v2 2026-07-03; comment "Accepted to ICML 2026"; the abstract names it as built on mask-based discrete diffusion for text, speech and images) and the PMLR page (v306, pp. 68853-68867). The PMLR page does not mention "8B"; the paper's 8B size and 4-bit quantisation come from the project's own setup, not from this source, so the sentence should not cite the paper for the size. Relevance: its abstract says it is built on a pre-trained Dream-7B language model, which is a different parameter count from "8B" (the project's own `.venv-omni` checkpoint should be checked and the size wording matched to that checkpoint, not to the paper).

2. FOIL (protocol.tex:280, "hard-negative set built from FOIL-COCO").
```bibtex
@inproceedings{shekhar2017foil,
  author    = {Shekhar, Ravi and Pezzelle, Sandro and Klimovich, Yauhen and Herbelot, Aur{\'e}lie and Nabi, Moin and Sangineto, Enver and Bernardi, Raffaella},
  title     = {{FOIL} it! {Find} one mismatch between image and language caption},
  booktitle = {Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)},
  year      = {2017},
  pages     = {255--265},
  doi       = {10.18653/v1/P17-1024},
  note      = {arXiv:1705.01359}
}
```
Seen: Crossref 10.18653/v1/P17-1024 (7 authors, pp. 255-265, no update notice) and arXiv 1705.01359 (DataCite: same title, 7 authors, 2017-05-03). It introduces FOIL-COCO (a COCO extension with one-word foil captions). Gomes et al. cite the same benchmark (Shekhar et al. 2017), so the reference is also consistent with related.tex.

3. imagecorruptions suite (protocol.tex:238 and results.tex:460; the text does not yet cite a source). The package README (github.com/bethgelab/imagecorruptions, Apache-2.0) asks users to cite Michaelis et al.; it credits Hendrycks and Dietterich for the original corruptions. The project installed commit c959e659c9 (IMPL-B-FOIL-SUITE-2026-10-28.md section 5).
```bibtex
@misc{michaelis2019imagecorruptions,
  author        = {Michaelis, Claudio and Mitzkus, Benjamin and Geirhos, Robert and Rusak, Evgenia and Bringmann, Oliver and Ecker, Alexander S. and Bethge, Matthias and Brendel, Wieland},
  title         = {Benchmarking robustness in object detection: Autonomous driving when winter is coming},
  year          = {2019},
  eprint        = {1907.07484},
  archivePrefix = {arXiv},
  note          = {arXiv:1907.07484v2; the imagecorruptions package, commit c959e659c9}
}

@inproceedings{hendrycks2019corruptions,
  author    = {Hendrycks, Dan and Dietterich, Thomas},
  title     = {Benchmarking neural network robustness to common corruptions and perturbations},
  booktitle = {International Conference on Learning Representations (ICLR 2019)},
  year      = {2019},
  url       = {https://openreview.net/pdf?id=HJz6tiCqYm},
  note      = {arXiv:1903.12261}
}
```
Seen: DataCite/OpenAlex for both ids (Michaelis: 8 authors, v1 2019-07-17, v2 2020-04-01, arXiv only; Hendrycks: 2 authors, ICLR location with the OpenReview pdf url from OpenAlex). The eight author names of Michaelis et al. were checked against the README BibTeX (Michaelis, Mitzkus, Geirhos, Rusak, Bringmann, Ecker, Bethge, Brendel). The OpenReview page itself was behind a browser check; the url comes from the OpenAlex record. The README points to arXiv 1807.01697 for the original corruptions, which is the earlier version of the same work; I did not check that record and cite the ICLR version instead. Minimum for the cap: Michaelis only (it is what the package requests); add Hendrycks only if the suite description names the ImageNet-C corruptions.

## 6. Gate

Fail (mission rule: fail on any `unverified` or `does-not-support` entry). Blocking items:
- Three open citation placeholders (section 5; entries ready).
- Zhou and Lu: the specific abstract phrases are unverified (X). The paper's own `\todo` already says this.
- Wang et al.: "split", "sets" and "conformal-prediction section" unverified.
Not blocking but should be fixed: sentences 3-8 of section 4, the five metadata upgrades of section 2, deletion of the two uncited entries.
No entry is `does-not-support`; 8 are `partial` (li2025lavida, wan2026disp, vempaty2013byzantine, kittler1998combining, rubin1976inference wording, shao2024ddef on "discount", wang2025multistage, zhou2027burden).

## 7. Information Fusion papers (Crossref container-title "Information Fusion")

| Key | DOI | Volume, article | Relevance | Cited |
|---|---|---|---|---|
| khaleghi2013multisensor | 10.1016/j.inffus.2011.08.001 | 14(1), 28-44 | multisensor fusion review; spurious and imperfect data | intro:28 |
| shao2024ddef | 10.1016/j.inffus.2023.102113 | 103, 102113 | evidential fusion with modality importance | intro:31, related:114, discussion:134 |
| huang2025evidential | 10.1016/j.inffus.2024.102648 | 113, 102648 | evidential fusion with reliability discounting | intro:31, protocol:257, related:114, discussion:134 |
| wang2025multistage | 10.1016/j.inffus.2025.103068 | 120, 103068 | conformal flagging on a fusion network | related:120, discussion:134 |
| zhang2026lowquality | 10.1016/j.inffus.2026.104437 | 135, 104437 | survey of fusion on low-quality data | intro:30, related:116 |
| zhou2027burden | 10.1016/j.inffus.2026.104860 | 139, 104860 | closest decision-level fusion gate | intro:63, related:118, discussion:130,151,191,195 |

All six are real and in the journal; none is retracted. The two corrigenda (Khaleghi, Wang) are noted in the bib. Not one of the six is padding: each is cited with a sentence that states what it does. Wang et al. is the weakest on relevance (a clinical referral model); it is cited once as a conformal-on-fusion example and could be dropped without orphaning a claim if a fourth drop is ever needed beyond section 8, but it is one of only six journal papers, so dropping it costs the journal-fit argument.

## 8. Ranked drop list for the 50-reference cap

Count: 52 cited today. Adding Omni-Diffusion, FOIL and Michaelis gives 55 (56 with Hendrycks). Five drops reach 50; a sixth is needed only if Hendrycks is added. The two uncited entries cost nothing in the printed list (bibtex omits them) but should be deleted from the .bib.

Weakest first. For each: the sentence that keeps its support after the drop. None below is the only support for a claim.

| Rank | Key | Reason | What keeps the sentence supported | Edit |
|---|---|---|---|---|
| 1 | diao2024radar | Radar-detection review, cited once inside a three-way CFAR cite; no claim is specific to it | finn1968adaptive and rohling1983cfar (related:106 keeps both) | delete the key from related:106 |
| 2 | tenney1981detection | Second source for the distributed-detection rule; Chair and Varshney's abstract states the cited rule and cites Tenney and Sandell | chair1986optimal (intro:26) | delete the key from intro:26 |
| 3 | kittler1998combining | Partial support: classifier-combination rules, no reliability weights (section 4, item 6) | chair1986optimal (related:107) | delete the key from related:107 |
| 4 | vempaty2013byzantine | Partial support: falsified-data review used for "spurious data" (section 4, item 7) | khaleghi2013multisensor, an Information Fusion paper (intro:28) | delete the key from intro:28 |
| 5 | lou2024sedd | Background citation; absorbing-state diffusion is already introduced by D3PM, which is cited in the same group | austin2021d3pm (related:10) | delete the key from related:10; no need to upgrade its metadata |

Reserve, in order, if a sixth is needed (Hendrycks added) or a different drop is preferred:

| Rank | Key | Reason | Constraint |
|---|---|---|---|
| 6 | finn1968adaptive | Weakest verification in the bib (index record only, no DOI); the CFAR sentence is carried by rohling1983cfar | intro:34 and related:106 would then cite Rohling alone |
| 7 | vovk2005algorithmic | Canonical conformal book, but angelopoulos2023gentle covers "distribution-free guarantees under exchangeability" | related:69 |
| 8 | wan2026disp | Tangential backdoor defence; a closest-work baseline in the plan but not run in the paper | It is the only support for the DiSP sentence (related:58-59), so dropping it means deleting that sentence ("Neither evaluates..." would then name only Dropout Decoding). Allowed only if the sentence goes too |

Do not drop: the six Information Fusion papers; any key that is the sole support for its sentence (bates2023outliers, kauf2023plwl2r, li2022uchecker, krojer2023diffusionitm, salazar2020mlm, gomes2025crc, angelopoulos2024crc, lezama2022tokencritic and the closest-work set); the three new entries; rubin1976inference (sole support for the informative-missingness sentence).

TMLR has no cap: keep all 52 plus the new entries there, apply the corrections in section 2 and the wording changes of section 4, and delete only the two uncited entries.

## 9. What the lead should apply

1. Add `li2026omnidiffusion`, `shekhar2017foil`, `michaelis2019imagecorruptions` (and optionally `hendrycks2019corruptions`); replace the two `\todo{AUTHOR: cite ...}` strings and add a cite to the suite sentence in protocol.tex:238. Do not cite the Omni-Diffusion paper for "8B".
2. Delete `hessel2021clipscore` and `radford2021clip`.
3. Apply the five drops of section 8 and the matching cite deletions.
4. Section 2 metadata upgrades (lou2024sedd if kept, uChecker to COLING 2022 after opening the Anthology page, pages for four NeurIPS/ICLR entries).
5. Sentence changes 1-8 of section 4.
6. Someone with ScienceDirect access: abstract of Zhou and Lu, abstract and conformal section of Wang et al., contents of both corrigenda, Finn and Johnson's primary record.
7. Re-run the venue check just before submission for swerdlow2025unidisc, shi2025muddit, schiff2026proseco, jhingran2026trustverify, kim2025prism, zhai2026core, huang2025remedi, le2026co2jump, ouyang2026freecorrection, wan2026disp (all preprints today).
