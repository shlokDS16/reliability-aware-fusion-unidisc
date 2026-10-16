agent: lit-scout
date: 2026-10-16
brief: map failed full-text routes (403 openreview, not_pdf/error oa_url, 1 arxiv error) to arXiv versions by title agreement; no PDFs downloaded
sources_examined: [DataCite arXiv index (client arxiv.content), arXiv API (export.arxiv.org), Crossref works, Zenodo records API, publisher PDF URLs via HEAD only]
coverage: all 472 failed records (last fetch-log row per id). OpenReview never contacted. OpenAlex and Semantic Scholar not used. Not searched: Google Scholar, DBLP, ACL Anthology search, author pages, GitHub READMEs, titles that differ by more than the thresholds.
claims:
  - statement: 30 of 472 failed records have a usable alternate route (17 arXiv, 13 direct PDF); 442 are unmapped
    status: supported
    evidence: arxiv-map.jsonl, unmapped.jsonl, arxiv-map-summary.json
    level: E1
    confidence: 0.8
unknowns: [PDF content of every mapped URL (nothing downloaded, so title agreement is metadata-level only), whether near-miss candidates are the same papers]

# Counts
failed total 472: openreview 403, oa_url 68, arxiv 1
mapped to arXiv: 17 (openreview 16, arxiv-error 1); loose flags: 0
mapped to direct PDF (not arXiv): 13 (all oa_url): 3 publisher/OJS PDFs (HEAD 200 application/pdf: M12084, M14797, M15138), 1 CDN PDF (M12531, HEAD 200 octet-stream), 9 Zenodo file links via records API (HEAD 200 octet-stream; check %PDF magic on download)
unmapped: 442 (openreview 387, oa_url 55)

# Method
1. DataCite REST (client-id arxiv.content): AND of first 12 title tokens (10 hits), then OR of 14 longest tokens (25 hits); a phrase query for titles of <=7 tokens or with LaTeX. Validation on 40 random records whose arXiv route is known: 38/40 recovered (misses: a 3-word generic title, one very new paper).
2. arXiv API ti: query (first 8 non-stopword tokens, 10 results, 4 s gap, backoff on 429): 456 queries, 0 additional matches.
3. Crossref works/<doi> for the 67 oa_url records with a DOI: no has-preprint relation anywhere; used only to obtain the publisher PDF link.
4. HEAD (no body) on derived PDF links: AEM, AAAI OJS, IJICTT = application/pdf; MDPI, Wiley, IJASEIT = 403; Springer, IOP, Nature = HTML (bot page); IOS Press = 200 without content type (not mapped).
5. Acceptance: normalised exact or token Jaccard >= 0.85; OpenReview also prefix-extension with Jaccard >= 0.75 flagged loose (none occurred).

# Notes on mapped rows
- M04571 (arxiv error): arXiv 2501.15405 v2 is a 1 KB withdrawn stub (arXiv Admin, disputed and unverifiable authorship per the abs page), hence 404 on /pdf/2501.15405. v1 (HEAD 200 application/pdf) mapped as 2501.15405v1. Flag: withdrawn paper; screening decision may want to reflect that.
- Jaccard 0.89 to 0.93 arXiv matches are renamed titles (M12766 Muddit, M13849 'Thought' vs 'Thoughts', M14177 EPIC prefix, M15652 Jump Your Steps, M17640 R3, M18345 TAD prefix, M19253 subtitle). Same-paper is likely but unproven without reading.
- Zenodo links are API /content URLs under the record id the DOI resolved to (differs from the DOI number by 1 for several); title agreement exact against the Zenodo record title.
- Several arXiv ids are 2610.* (this month); they exist in DataCite, so they are real as of today.

# Near-misses NOT mapped (below the stated rule, probably the same paper; orchestrator decides). All in near-miss.jsonl
- M12175 2607.00773v1 J=0.778: record 'Accelerating Discrete Diffusion Models with Parallel Sampling' vs arXiv 'Accelerating Discrete Diffusion Models with Parallel-In-Time Sampling'
- M14200 2606.14792v1 J=0.818: record 'Efficient Reinforcement for Visual-Textual Thinking with Discrete Diffusion Mode' vs arXiv 'Efficient Reinforcement for Visual-Textual Thinking with Discrete Diffusion Mode'
- M15091 2606.08417v2 J=0.818: record 'Hacking Generative Perplexity: Why Unconditional Text Evaluation Needs New Metri' vs arXiv 'Hacking Generative Perplexity: Why Unconditional Text Evaluation Needs Distribut'
- M17835 2510.04147v1 J=0.778: record 'Self Speculative Decoding for Diffusion Large Language Model' vs arXiv 'Self Speculative Decoding for Diffusion Large Language Models'
- M18445 2605.29123v2 J=0.833: record 'The Confidence Shortcut: A Reasoning Failure Mode in Masked Diffusion Models' vs arXiv 'The Confidence Shortcut: A Reasoning Failure Mode of Masked Diffusion Models'
- M18918 2606.00023v1 J=0.75: record 'TrustLDM: Benchmarking Trustworthiness in Language Diffusion Model' vs arXiv 'TrustLDM: Benchmarking Trustworthiness in Language Diffusion Models'
- M19293 2604.09059v1 J=0.778: record 'World-Language-Action Models for Autonomous Driving' vs arXiv 'Learning Vision-Language-Action World Models for Autonomous Driving'
- M16269 2410.10798 J=0.8: record 'MMAR: Towards Lossless Multi-Modal Auto-Regressive Prababilistic Modeling' vs arXiv 'MMAR: Towards Lossless Multi-Modal Auto-Regressive Probabilistic Modeling'
- M17647 2610.17590 J=0.846: record 'Revisiting the 16× Pretraining Compute Gap between Diffusion and Autoregressive ' vs arXiv 'Revisiting the 16x Pretraining Compute Gap between Diffusion and Autoregressive '

# Unmapped
oa_url (55): paywalled or bot-blocked publishers (ACM, Elsevier, IEEE, Springer, Nature, Wiley, MDPI, IOP), repositories without a derivable file link (hdl, UT TSW, NTU DR-NTU, ETH, VT, UMD, ResearchGate, Authorea, SSRN), Zenodo M17317 (410 gone) and M18015 (files are json/docx only). Full list with reasons in unmapped.jsonl.
openreview (387): no arXiv version found in DataCite or the arXiv API at the thresholds. These are probably not on arXiv under the same title (or renamed); no other open route was found. Network dropped at the end of the session, so the final near-miss recheck used cached DataCite responses only.
