# Web of Science Core Collection queries run 2026-10-15 (Chrome, VIT institutional access; D0031)

Platform: webofscience.com, Advanced Search, Web of Science Core Collection, Editions: All.
Run 2026-10-15, about 23:05-23:15 IST, in the user's Chrome (Claude in Chrome), no personal sign-in.

Date note: the system clock read Thu 2026-10-15 23:16 IST when these ran. The Scopus files are named
`...-20261016` but their file times are 2026-10-15 22:18-22:24 IST, so Scopus was also run on 2026-10-15;
the 20261016 label is a naming error (files not renamed: their hashes are logged). Search date for the
subscription databases: 2026-10-15.

Plan (D0031): Q1 = union of S1, S2, S1':A1, S1':A2-r1, S1':A3-r1..r3, S2':M, S2':VLA (language clause
widened to S1':A2's word list), the same text as Scopus Q1 in WoS syntax; Q2-Q5 = the parts that carry NOT
clauses, verbatim from `research/review/corpus/subscription-search-sheet.md` (Web of Science, S1' section),
plus `AND LA=(English)` (protocol section 3 filter; Scopus used LANGUAGE(english)). WoS precedence is
NOT > AND > OR, so the sheet's WoS NOT forms are equivalent to the Scopus parts. S1''/S2'' are applied
locally after export. The union of the five sets was formed in the session history (#6) for one
deduplicated export.

Q1 (#1):
TS=(("diffusion language model*" OR "language diffusion model*" OR "diffusion llm*" OR "diffusion lm*" OR dllm OR dllms OR "diffusion-based language model*" OR "diffusion-based llm*" OR "diffusion large language model*" OR "diffusion-based large language model*" OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR "diffusion mllm*" OR "diffusion vlm*" OR "diffusion vision-language model*" OR dmllm OR dmllms OR dvlm OR dvlms OR "non-autoregressive language model*") OR (("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*" OR "absorbing state" OR "any-order" OR "discrete flow matching" OR "diffusion LLM" OR ("non-autoregressive" AND diffusion)) AND (language OR text OR token* OR "language model*" OR llm* OR vocabulary OR autoregressive OR reasoning)) OR (("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR "mixed-modal*" OR "mixed-modality") AND (diffusion OR "masked generative" OR "discrete flow*" OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")) OR (("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR "diffusion language model*" OR dllm OR dllms))) AND PY=(2021-2026) AND LA=(English)

Q2 (#2, S1p-A2-r2):
TS=(("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)) AND PY=(2021-2026) AND LA=(English)

Q3 (#3, S1p-A3-r4):
TS=("non-autoregressive" AND diffusion NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) AND PY=(2021-2026) AND LA=(English)

Q4 (#4, S1p-B):
TS=(diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR "discrete sequence*" OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR "topic model*" OR "triple extraction" OR "information extraction") NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) AND PY=(2021-2026) AND LA=(English)

Q5 (#5, S1p-C):
TS=(diffusion AND ("language model*" OR llm*) NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)) AND PY=(2021-2026) AND LA=(English)

Union (#6): #1 OR #2 OR #3 OR #4 OR #5

Hit counts shown by the site:
- Q1 combined: 599
- Q2 S1p-A2-r2: 376
- Q3 S1p-A3-r4: 105
- Q4 S1p-B: 1,012
- Q5 S1p-C: 543
- Union #6: 2,267 (sum of parts 2,635; overlap 368)

Note: an earlier Q2 attempt failed with "Search Error: Missing Boolean operator" because the query box still
held Q1 and the two strings were joined; it created no set. Q2 was rerun alone.

Exports (user approved 2026-10-15): union #6, sorted by Relevance, RIS (other reference software), Record
Content "Full Record", record ranges 1-1000, 1001-2000, 2001-2267; downloaded 23:52-23:55 IST as savedrecs.ris
and renamed (content unchanged; the first file starts with a UTF-8 BOM):
- wos-union-0001-1000-20261015.ris sha256 996efef9a209278d4667bd15eb3843aaa5fc4fcfb65b01035654c8d73fab139a bytes 2887592 records 1000
- wos-union-1001-2000-20261015.ris sha256 eaaa4e7c81dfb26b668353be88f790719c5219eb3acf35afe5937875c5189a5c bytes 2843713 records 1000
- wos-union-2001-2267-20261015.ris sha256 67adb39c68f51ed9eb82fe26f3239a73ce4167339f39bab1a24601b3a9717d0f bytes 861065 records 267
Records 2,267 = hit count. Titles: 2,267 lines, 2,266 distinct (case-folded); one DOI (10.1109/TCSS.2025.3649053)
appears on two records inside file 1 (WoS lists the paper twice, early-access and issue dates), not a range
overlap. The RIS has no WoS accession number (no UT/AN tag); dedup uses DOI and title.
