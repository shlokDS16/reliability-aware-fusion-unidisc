# Subscription database search sheet (human run)

Prepared 2026-10-15 for protocol `research/review/protocol.md` section 3. The databases below need VIT eGateway access and cannot be run by an agent. Everything on this sheet is data to paste; nothing here has been run or tested against these databases (no access). Syntax was checked against the vendors' public help pages on 2026-10-15; anything marked **[unverified]** must be confirmed on screen and corrected in the log if the interface behaves differently.

## What to do, in order

1. Pick one **search date** (today or the day you start) and use it for all six databases. Write it in every `.meta.txt`. Date window: **2021-01-01 to the search date**, English (protocol section 3 filters).
2. For each database and each string (S1, S2): paste the string, apply the filters, read the hit count the site shows, export, then save the file as `research/sources/search-raw/<db-folder>/<db-folder>-<S1|S2>[-runN]-<YYYYMMDD>.<ext>` plus a sibling `.meta.txt` containing: search date and time (with time zone), the exact string as pasted, filters applied, hit count shown by the site, number of records in the export file, your name.
3. If the site rejects the full string (too long, too many operators, too many terms), use the **split runs** under that database. The union of the split runs equals the full string. Log each run as its own search and do not merge the export files.
4. If a result set exceeds the export cap, split by publication year (2021, 2022, ..., 2026) and keep the same string; note this in `.meta.txt`.
5. Do not edit the exports. Tell the orchestrator when they are in place; lit-scout then hashes them, adds one `search-log.jsonl` row per file, normalises IDs and deduplicates against `screening/records.jsonl` and `corpus/new-records-2026-10-15.jsonl`.

Export formats: CSV with abstracts where the database offers it (Scopus, IEEE Xplore); RIS with abstract otherwise (Web of Science full record, ACM, ScienceDirect). SpringerLink's CSV carries no abstracts; lit-scout fetches them by DOI afterwards.

<!-- BEGIN S1p-S2p (D0026) -->
## Revised strings S1' and S2' (decision D0026, protocol section 10 amendment of 2026-10-15): run these first

The pilot (all 28 multimodal and a random 50 other seed papers) found that S1 and S2 miss seed papers whose abstracts use other words (`dLLM`, `diffusion-based LLM`, `large language diffusion model`, discrete or masked diffusion without a language word, diffusion drafters for speculative decoding, continuous or latent diffusion language models, NLP-task diffusion models, vision-language-action). The revised strings S1' and S2' replace S1 and S2 as the **primary run**. **Keep the original strings S1 and S2 (sections 1 to 6 below) as a second run** in the same databases, same search date: their results go in files named `...-S1-...` and `...-S2-...` as before; the revised ones in `...-S1p-...` and `...-S2p-...` (`.meta.txt`: string label `S1'` or `S2'`). The two result sets overlap and are deduplicated afterwards.

Date window and language are those of section 3 of the protocol (2021-01-01 to the search date, English). Everything below is generated from one specification (`tools/search_sources.py`, `S1P_PARTS` and `S2P_PARTS`), so the strings cannot drift from what the agents ran on arXiv, Semantic Scholar, OpenAlex, OpenReview and the ACL Anthology. A string is run **part by part**; the union of the parts is the string. Log each part as its own search (`S1p-A1`, `S1p-A2`, ...); do not merge the export files. Where a database cannot hold a part in one query, the part is cut into runs (`-r1`, `-r2`, ...) whose union is the part.

### The revised strings in database-neutral form (verbatim)

Reading rule: AND binds tighter than OR; a trailing `*` is a word-prefix wildcard; `NOT (...)` excludes any of the listed words.

S1':
```
("diffusion language model*" OR "language diffusion model*" OR "diffusion llm*" OR "diffusion lm*" OR dllm OR dllms OR "diffusion-based language model*" OR "diffusion-based llm*" OR "diffusion large language model*" OR "diffusion-based large language model*" OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR "diffusion mllm*" OR "diffusion vlm*" OR "diffusion vision-language model*" OR dmllm OR dmllms OR dvlm OR dvlms) OR ((("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND (language OR text OR token* OR "language model*" OR llm* OR vocabulary OR autoregressive OR reasoning)) OR (("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation))) OR (("absorbing state" AND (language OR text OR token* OR "language model*")) OR ("any-order" AND (language OR text OR token* OR "language model*")) OR "non-autoregressive language model*" OR ("non-autoregressive" AND diffusion AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*))) OR (diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR "discrete sequence*" OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR "topic model*" OR "triple extraction" OR "information extraction") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) OR (diffusion AND ("language model*" OR llm*) AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation))
```

S2':
```
(("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR "mixed-modal*" OR "mixed-modality") AND (diffusion OR "masked generative" OR "discrete flow*" OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")) OR (("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR "diffusion language model*" OR dllm OR dllms))
```

Parts (each is a string on its own; S1' = A1 OR A2 OR A3 OR B OR C; S2' = M OR VLA):

- `S1':A1` (names of diffusion language models (no context clause)):
  ```
  "diffusion language model*" OR "language diffusion model*" OR "diffusion llm*" OR "diffusion lm*" OR dllm OR dllms OR "diffusion-based language model*" OR "diffusion-based llm*" OR "diffusion large language model*" OR "diffusion-based large language model*" OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR "diffusion mllm*" OR "diffusion vlm*" OR "diffusion vision-language model*" OR dmllm OR dmllms OR dvlm OR dvlms
  ```
- `S1':A2` (discrete diffusion, masked diffusion, discrete flow, discrete state space: with a language word, or, in the dialects that keep NOT, without a biochemical or visual word):
  ```
  (("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND (language OR text OR token* OR "language model*" OR llm* OR vocabulary OR autoregressive OR reasoning)) OR (("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation))
  ```
- `S1':A3` (absorbing state, any-order generation, non-autoregressive language models, non-autoregressive with diffusion):
  ```
  ("absorbing state" AND (language OR text OR token* OR "language model*")) OR ("any-order" AND (language OR text OR token* OR "language model*")) OR "non-autoregressive language model*" OR ("non-autoregressive" AND diffusion AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*))
  ```
- `S1':B` (diffusion with text-generation or NLP-task vocabulary):
  ```
  diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR "discrete sequence*" OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR "topic model*" OR "triple extraction" OR "information extraction") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)
  ```
- `S1':C` (diffusion with a language model or LLM, outside biochemical and visual contexts):
  ```
  diffusion AND ("language model*" OR llm*) AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)
  ```
- `S2':M` (unified multimodal understanding and generation with diffusion, masked-generative or flow):
  ```
  ("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR "mixed-modal*" OR "mixed-modality") AND (diffusion OR "masked generative" OR "discrete flow*" OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")
  ```
- `S2':VLA` (vision-language-action models with discrete or unified diffusion):
  ```
  ("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR "diffusion language model*" OR dllm OR dllms)
  ```

Biochemical exclusion list: `protein*`, `molecul*`, `antibod*`, `peptide*`, `rna`, `dna`, `drug*`, `crystal*`, `chemi*`, `genom*`, `biolog*`, `graph generation`, `traveling salesman`, `recommend*`. Visual exclusion list: `image*`, `video*`, `3d`, `audio`, `visual*`, `pixel*`, `photo*`, `segmentation`. These implement exclusion X1 of the protocol (diffusion for molecules, proteins, images, video or audio without text) and keep the export sizes manageable; a paper that has a language word in the abstract is not removed by them in A2.

### Scopus (folder `scopus`; file names `scopus-S1p-<part>[-rN]-<YYYYMMDD>` and `scopus-S2p-<part>[-rN]-<YYYYMMDD>`)

Advanced document search. NOT is written `AND NOT`. Wildcards inside quoted phrases are the same **[unverified]** as in section 1; if Scopus warns, use the plural-expanded form of section 1's fallback.

S1p-A1:
```
TITLE-ABS-KEY("diffusion language model*" OR "language diffusion model*" OR "diffusion llm*" OR "diffusion lm*" OR dllm OR dllms OR "diffusion-based language model*" OR "diffusion-based llm*" OR "diffusion large language model*" OR "diffusion-based large language model*" OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR "diffusion mllm*" OR "diffusion vlm*" OR "diffusion vision-language model*" OR dmllm OR dmllms OR dvlm OR dvlms) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```
S1p-A2-r1:
```
TITLE-ABS-KEY(("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND (language OR text OR token* OR "language model*" OR llm* OR vocabulary OR autoregressive OR reasoning)) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```
S1p-A2-r2:
```
TITLE-ABS-KEY(("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```
S1p-A3-r1:
```
TITLE-ABS-KEY("non-autoregressive language model*") AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```
S1p-A3-r2:
```
TITLE-ABS-KEY("absorbing state" AND (language OR text OR token* OR "language model*")) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```
S1p-A3-r3:
```
TITLE-ABS-KEY("any-order" AND (language OR text OR token* OR "language model*")) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```
S1p-A3-r4:
```
TITLE-ABS-KEY("non-autoregressive" AND diffusion AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```
S1p-B:
```
TITLE-ABS-KEY(diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR "discrete sequence*" OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR "topic model*" OR "triple extraction" OR "information extraction") AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```
S1p-C:
```
TITLE-ABS-KEY(diffusion AND ("language model*" OR llm*) AND NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) AND NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```
S2p-M:
```
TITLE-ABS-KEY(("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR "mixed-modal*" OR "mixed-modality") AND (diffusion OR "masked generative" OR "discrete flow*" OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```
S2p-VLA:
```
TITLE-ABS-KEY(("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR "diffusion language model*" OR dllm OR dllms)) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```

### Web of Science Core Collection (folder `web-of-science`; file names `web-of-science-S1p-<part>[-rN]-<YYYYMMDD>` and `web-of-science-S2p-<part>[-rN]-<YYYYMMDD>`)

Advanced Search. Topic (`TS=`) as in section 2; replace `TS=(X)` by `(TI=(X) OR AB=(X) OR AK=(X))` for the strict title-abstract-keyword reading. Wildcards in phrases **[unverified]**.

S1p-A1:
```
TS=("diffusion language model*" OR "language diffusion model*" OR "diffusion llm*" OR "diffusion lm*" OR dllm OR dllms OR "diffusion-based language model*" OR "diffusion-based llm*" OR "diffusion large language model*" OR "diffusion-based large language model*" OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR "diffusion mllm*" OR "diffusion vlm*" OR "diffusion vision-language model*" OR dmllm OR dmllms OR dvlm OR dvlms) AND PY=(2021-2026)
```
S1p-A2-r1:
```
TS=(("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") AND (language OR text OR token* OR "language model*" OR llm* OR vocabulary OR autoregressive OR reasoning)) AND PY=(2021-2026)
```
S1p-A2-r2:
```
TS=(("discrete diffusion" OR "masked diffusion" OR "discrete flow*" OR "discrete state-space*") NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)) AND PY=(2021-2026)
```
S1p-A3-r1:
```
TS=("non-autoregressive language model*") AND PY=(2021-2026)
```
S1p-A3-r2:
```
TS=("absorbing state" AND (language OR text OR token* OR "language model*")) AND PY=(2021-2026)
```
S1p-A3-r3:
```
TS=("any-order" AND (language OR text OR token* OR "language model*")) AND PY=(2021-2026)
```
S1p-A3-r4:
```
TS=("non-autoregressive" AND diffusion NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) AND PY=(2021-2026)
```
S1p-B:
```
TS=(diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR "discrete sequence*" OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR "topic model*" OR "triple extraction" OR "information extraction") NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) AND PY=(2021-2026)
```
S1p-C:
```
TS=(diffusion AND ("language model*" OR llm*) NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)) AND PY=(2021-2026)
```
S2p-M:
```
TS=(("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR "mixed-modal*" OR "mixed-modality") AND (diffusion OR "masked generative" OR "discrete flow*" OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")) AND PY=(2021-2026)
```
S2p-VLA:
```
TS=(("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR "diffusion language model*" OR dllm OR dllms)) AND PY=(2021-2026)
```

### IEEE Xplore (folder `ieee-xplore`; file names `ieee-xplore-S1p-<part>[-rN]-<YYYYMMDD>` and `ieee-xplore-S2p-<part>[-rN]-<YYYYMMDD>`)

Command Search. Each term is written in the three fields as in section 3. The NOT clauses are **dropped** here (term budget); the runs are broader than S1'/S2' and the excluded topics go out at screening (X1). Phrases are written with singular and plural instead of `*`. The term limit **[unverified]** is taken as 6 per OR list; shorten the lists if IEEE refuses a run.

S1p-A1-r1:
```
(("Document Title":"diffusion language model" OR "Abstract":"diffusion language model" OR "Author Keywords":"diffusion language model") OR ("Document Title":"diffusion language models" OR "Abstract":"diffusion language models" OR "Author Keywords":"diffusion language models")) OR (("Document Title":"language diffusion model" OR "Abstract":"language diffusion model" OR "Author Keywords":"language diffusion model") OR ("Document Title":"language diffusion models" OR "Abstract":"language diffusion models" OR "Author Keywords":"language diffusion models")) OR (("Document Title":"diffusion llm" OR "Abstract":"diffusion llm" OR "Author Keywords":"diffusion llm") OR ("Document Title":"diffusion llms" OR "Abstract":"diffusion llms" OR "Author Keywords":"diffusion llms"))
```
S1p-A1-r2:
```
(("Document Title":"diffusion lm" OR "Abstract":"diffusion lm" OR "Author Keywords":"diffusion lm") OR ("Document Title":"diffusion lms" OR "Abstract":"diffusion lms" OR "Author Keywords":"diffusion lms")) OR ("Document Title":dllm OR "Abstract":dllm OR "Author Keywords":dllm) OR ("Document Title":dllms OR "Abstract":dllms OR "Author Keywords":dllms) OR (("Document Title":"diffusion-based language model" OR "Abstract":"diffusion-based language model" OR "Author Keywords":"diffusion-based language model") OR ("Document Title":"diffusion-based language models" OR "Abstract":"diffusion-based language models" OR "Author Keywords":"diffusion-based language models"))
```
S1p-A1-r3:
```
(("Document Title":"diffusion-based llm" OR "Abstract":"diffusion-based llm" OR "Author Keywords":"diffusion-based llm") OR ("Document Title":"diffusion-based llms" OR "Abstract":"diffusion-based llms" OR "Author Keywords":"diffusion-based llms")) OR (("Document Title":"diffusion large language model" OR "Abstract":"diffusion large language model" OR "Author Keywords":"diffusion large language model") OR ("Document Title":"diffusion large language models" OR "Abstract":"diffusion large language models" OR "Author Keywords":"diffusion large language models")) OR (("Document Title":"diffusion-based large language model" OR "Abstract":"diffusion-based large language model" OR "Author Keywords":"diffusion-based large language model") OR ("Document Title":"diffusion-based large language models" OR "Abstract":"diffusion-based large language models" OR "Author Keywords":"diffusion-based large language models"))
```
S1p-A1-r4:
```
("Document Title":"text diffusion" OR "Abstract":"text diffusion" OR "Author Keywords":"text diffusion") OR ("Document Title":"block diffusion" OR "Abstract":"block diffusion" OR "Author Keywords":"block diffusion") OR ("Document Title":"absorbing diffusion" OR "Abstract":"absorbing diffusion" OR "Author Keywords":"absorbing diffusion") OR (("Document Title":"diffusion mllm" OR "Abstract":"diffusion mllm" OR "Author Keywords":"diffusion mllm") OR ("Document Title":"diffusion mllms" OR "Abstract":"diffusion mllms" OR "Author Keywords":"diffusion mllms"))
```
S1p-A1-r5:
```
(("Document Title":"diffusion vlm" OR "Abstract":"diffusion vlm" OR "Author Keywords":"diffusion vlm") OR ("Document Title":"diffusion vlms" OR "Abstract":"diffusion vlms" OR "Author Keywords":"diffusion vlms")) OR (("Document Title":"diffusion vision-language model" OR "Abstract":"diffusion vision-language model" OR "Author Keywords":"diffusion vision-language model") OR ("Document Title":"diffusion vision-language models" OR "Abstract":"diffusion vision-language models" OR "Author Keywords":"diffusion vision-language models")) OR ("Document Title":dmllm OR "Abstract":dmllm OR "Author Keywords":dmllm) OR ("Document Title":dmllms OR "Abstract":dmllms OR "Author Keywords":dmllms)
```
S1p-A1-r6:
```
("Document Title":dvlm OR "Abstract":dvlm OR "Author Keywords":dvlm) OR ("Document Title":dvlms OR "Abstract":dvlms OR "Author Keywords":dvlms)
```
S1p-A2-r1:
```
(("Document Title":"discrete diffusion" OR "Abstract":"discrete diffusion" OR "Author Keywords":"discrete diffusion") OR ("Document Title":"masked diffusion" OR "Abstract":"masked diffusion" OR "Author Keywords":"masked diffusion") OR (("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"discrete flows" OR "Abstract":"discrete flows" OR "Author Keywords":"discrete flows")) OR (("Document Title":"discrete state-space" OR "Abstract":"discrete state-space" OR "Author Keywords":"discrete state-space") OR ("Document Title":"discrete state-spaces" OR "Abstract":"discrete state-spaces" OR "Author Keywords":"discrete state-spaces"))) AND (("Document Title":language OR "Abstract":language OR "Author Keywords":language) OR ("Document Title":text OR "Abstract":text OR "Author Keywords":text) OR ("Document Title":token* OR "Abstract":token* OR "Author Keywords":token*) OR (("Document Title":"language model" OR "Abstract":"language model" OR "Author Keywords":"language model") OR ("Document Title":"language models" OR "Abstract":"language models" OR "Author Keywords":"language models")) OR ("Document Title":llm* OR "Abstract":llm* OR "Author Keywords":llm*))
```
S1p-A2-r2:
```
(("Document Title":"discrete diffusion" OR "Abstract":"discrete diffusion" OR "Author Keywords":"discrete diffusion") OR ("Document Title":"masked diffusion" OR "Abstract":"masked diffusion" OR "Author Keywords":"masked diffusion") OR (("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"discrete flows" OR "Abstract":"discrete flows" OR "Author Keywords":"discrete flows")) OR (("Document Title":"discrete state-space" OR "Abstract":"discrete state-space" OR "Author Keywords":"discrete state-space") OR ("Document Title":"discrete state-spaces" OR "Abstract":"discrete state-spaces" OR "Author Keywords":"discrete state-spaces"))) AND (("Document Title":vocabulary OR "Abstract":vocabulary OR "Author Keywords":vocabulary) OR ("Document Title":autoregressive OR "Abstract":autoregressive OR "Author Keywords":autoregressive) OR ("Document Title":reasoning OR "Abstract":reasoning OR "Author Keywords":reasoning))
```
S1p-A2-r3:
```
(("Document Title":"discrete diffusion" OR "Abstract":"discrete diffusion" OR "Author Keywords":"discrete diffusion") OR ("Document Title":"masked diffusion" OR "Abstract":"masked diffusion" OR "Author Keywords":"masked diffusion") OR (("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"discrete flows" OR "Abstract":"discrete flows" OR "Author Keywords":"discrete flows")) OR (("Document Title":"discrete state-space" OR "Abstract":"discrete state-space" OR "Author Keywords":"discrete state-space") OR ("Document Title":"discrete state-spaces" OR "Abstract":"discrete state-spaces" OR "Author Keywords":"discrete state-spaces")))
```
S1p-A3-r1:
```
(("Document Title":"non-autoregressive language model" OR "Abstract":"non-autoregressive language model" OR "Author Keywords":"non-autoregressive language model") OR ("Document Title":"non-autoregressive language models" OR "Abstract":"non-autoregressive language models" OR "Author Keywords":"non-autoregressive language models"))
```
S1p-A3-r2:
```
("Document Title":"absorbing state" OR "Abstract":"absorbing state" OR "Author Keywords":"absorbing state") AND (("Document Title":language OR "Abstract":language OR "Author Keywords":language) OR ("Document Title":text OR "Abstract":text OR "Author Keywords":text) OR ("Document Title":token* OR "Abstract":token* OR "Author Keywords":token*) OR (("Document Title":"language model" OR "Abstract":"language model" OR "Author Keywords":"language model") OR ("Document Title":"language models" OR "Abstract":"language models" OR "Author Keywords":"language models")))
```
S1p-A3-r3:
```
("Document Title":"any-order" OR "Abstract":"any-order" OR "Author Keywords":"any-order") AND (("Document Title":language OR "Abstract":language OR "Author Keywords":language) OR ("Document Title":text OR "Abstract":text OR "Author Keywords":text) OR ("Document Title":token* OR "Abstract":token* OR "Author Keywords":token*) OR (("Document Title":"language model" OR "Abstract":"language model" OR "Author Keywords":"language model") OR ("Document Title":"language models" OR "Abstract":"language models" OR "Author Keywords":"language models")))
```
S1p-A3-r4:
```
("Document Title":"non-autoregressive" OR "Abstract":"non-autoregressive" OR "Author Keywords":"non-autoregressive") AND ("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion)
```
S1p-B-r1:
```
("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) AND (("Document Title":"text generation" OR "Abstract":"text generation" OR "Author Keywords":"text generation") OR ("Document Title":"language generation" OR "Abstract":"language generation" OR "Author Keywords":"language generation") OR ("Document Title":"natural language generation" OR "Abstract":"natural language generation" OR "Author Keywords":"natural language generation") OR ("Document Title":"sequence-to-sequence" OR "Abstract":"sequence-to-sequence" OR "Author Keywords":"sequence-to-sequence") OR ("Document Title":seq2seq OR "Abstract":seq2seq OR "Author Keywords":seq2seq))
```
S1p-B-r2:
```
("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) AND ((("Document Title":"discrete sequence" OR "Abstract":"discrete sequence" OR "Author Keywords":"discrete sequence") OR ("Document Title":"discrete sequences" OR "Abstract":"discrete sequences" OR "Author Keywords":"discrete sequences")) OR ("Document Title":"speculative decoding" OR "Abstract":"speculative decoding" OR "Author Keywords":"speculative decoding") OR ("Document Title":"categorical data" OR "Abstract":"categorical data" OR "Author Keywords":"categorical data") OR ("Document Title":"discrete data" OR "Abstract":"discrete data" OR "Author Keywords":"discrete data") OR ("Document Title":paraphras* OR "Abstract":paraphras* OR "Author Keywords":paraphras*))
```
S1p-B-r3:
```
("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) AND (("Document Title":"textual diffusion" OR "Abstract":"textual diffusion" OR "Author Keywords":"textual diffusion") OR ("Document Title":"text modeling" OR "Abstract":"text modeling" OR "Author Keywords":"text modeling") OR ("Document Title":"named entity" OR "Abstract":"named entity" OR "Author Keywords":"named entity") OR ("Document Title":sentiment OR "Abstract":sentiment OR "Author Keywords":sentiment) OR ("Document Title":summarization OR "Abstract":summarization OR "Author Keywords":summarization) OR ("Document Title":dialog* OR "Abstract":dialog* OR "Author Keywords":dialog*))
```
S1p-B-r4:
```
("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) AND (("Document Title":dialogue OR "Abstract":dialogue OR "Author Keywords":dialogue) OR ("Document Title":"machine translation" OR "Abstract":"machine translation" OR "Author Keywords":"machine translation") OR ("Document Title":"text style" OR "Abstract":"text style" OR "Author Keywords":"text style") OR ("Document Title":commonsense OR "Abstract":commonsense OR "Author Keywords":commonsense) OR (("Document Title":"topic model" OR "Abstract":"topic model" OR "Author Keywords":"topic model") OR ("Document Title":"topic models" OR "Abstract":"topic models" OR "Author Keywords":"topic models")))
```
S1p-B-r5:
```
("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) AND (("Document Title":"triple extraction" OR "Abstract":"triple extraction" OR "Author Keywords":"triple extraction") OR ("Document Title":"information extraction" OR "Abstract":"information extraction" OR "Author Keywords":"information extraction"))
```
S1p-C:
```
("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) AND ((("Document Title":"language model" OR "Abstract":"language model" OR "Author Keywords":"language model") OR ("Document Title":"language models" OR "Abstract":"language models" OR "Author Keywords":"language models")) OR ("Document Title":llm* OR "Abstract":llm* OR "Author Keywords":llm*))
```
S2p-M-r1:
```
(("Document Title":"unified multimodal" OR "Abstract":"unified multimodal" OR "Author Keywords":"unified multimodal") OR ("Document Title":"unified multi-modal" OR "Abstract":"unified multi-modal" OR "Author Keywords":"unified multi-modal") OR ("Document Title":"unified understanding and generation" OR "Abstract":"unified understanding and generation" OR "Author Keywords":"unified understanding and generation") OR ("Document Title":"understanding and generation" OR "Abstract":"understanding and generation" OR "Author Keywords":"understanding and generation") OR ("Document Title":"any-to-any" OR "Abstract":"any-to-any" OR "Author Keywords":"any-to-any")) AND (("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) OR ("Document Title":"masked generative" OR "Abstract":"masked generative" OR "Author Keywords":"masked generative") OR (("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"discrete flows" OR "Abstract":"discrete flows" OR "Author Keywords":"discrete flows")) OR ("Document Title":"flow matching" OR "Abstract":"flow matching" OR "Author Keywords":"flow matching") OR ("Document Title":"rectified flow" OR "Abstract":"rectified flow" OR "Author Keywords":"rectified flow")) AND (("Document Title":multimodal OR "Abstract":multimodal OR "Author Keywords":multimodal) OR ("Document Title":"multi-modal" OR "Abstract":"multi-modal" OR "Author Keywords":"multi-modal") OR ("Document Title":"vision-language" OR "Abstract":"vision-language" OR "Author Keywords":"vision-language") OR ("Document Title":"text-to-image" OR "Abstract":"text-to-image" OR "Author Keywords":"text-to-image") OR ("Document Title":"image generation" OR "Abstract":"image generation" OR "Author Keywords":"image generation") OR ("Document Title":mllm OR "Abstract":mllm OR "Author Keywords":mllm))
```
S2p-M-r2:
```
(("Document Title":"unified multimodal" OR "Abstract":"unified multimodal" OR "Author Keywords":"unified multimodal") OR ("Document Title":"unified multi-modal" OR "Abstract":"unified multi-modal" OR "Author Keywords":"unified multi-modal") OR ("Document Title":"unified understanding and generation" OR "Abstract":"unified understanding and generation" OR "Author Keywords":"unified understanding and generation") OR ("Document Title":"understanding and generation" OR "Abstract":"understanding and generation" OR "Author Keywords":"understanding and generation") OR ("Document Title":"any-to-any" OR "Abstract":"any-to-any" OR "Author Keywords":"any-to-any")) AND (("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) OR ("Document Title":"masked generative" OR "Abstract":"masked generative" OR "Author Keywords":"masked generative") OR (("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"discrete flows" OR "Abstract":"discrete flows" OR "Author Keywords":"discrete flows")) OR ("Document Title":"flow matching" OR "Abstract":"flow matching" OR "Author Keywords":"flow matching") OR ("Document Title":"rectified flow" OR "Abstract":"rectified flow" OR "Author Keywords":"rectified flow")) AND (("Document Title":mllms OR "Abstract":mllms OR "Author Keywords":mllms) OR ("Document Title":"visual understanding" OR "Abstract":"visual understanding" OR "Author Keywords":"visual understanding") OR ("Document Title":"image understanding" OR "Abstract":"image understanding" OR "Author Keywords":"image understanding"))
```
S2p-M-r3:
```
(("Document Title":"unified multimodal" OR "Abstract":"unified multimodal" OR "Author Keywords":"unified multimodal") OR ("Document Title":"unified multi-modal" OR "Abstract":"unified multi-modal" OR "Author Keywords":"unified multi-modal") OR ("Document Title":"unified understanding and generation" OR "Abstract":"unified understanding and generation" OR "Author Keywords":"unified understanding and generation") OR ("Document Title":"understanding and generation" OR "Abstract":"understanding and generation" OR "Author Keywords":"understanding and generation") OR ("Document Title":"any-to-any" OR "Abstract":"any-to-any" OR "Author Keywords":"any-to-any")) AND ("Document Title":"discrete denoising" OR "Abstract":"discrete denoising" OR "Author Keywords":"discrete denoising") AND (("Document Title":multimodal OR "Abstract":multimodal OR "Author Keywords":multimodal) OR ("Document Title":"multi-modal" OR "Abstract":"multi-modal" OR "Author Keywords":"multi-modal") OR ("Document Title":"vision-language" OR "Abstract":"vision-language" OR "Author Keywords":"vision-language") OR ("Document Title":"text-to-image" OR "Abstract":"text-to-image" OR "Author Keywords":"text-to-image") OR ("Document Title":"image generation" OR "Abstract":"image generation" OR "Author Keywords":"image generation") OR ("Document Title":mllm OR "Abstract":mllm OR "Author Keywords":mllm))
```
S2p-M-r4:
```
(("Document Title":"unified multimodal" OR "Abstract":"unified multimodal" OR "Author Keywords":"unified multimodal") OR ("Document Title":"unified multi-modal" OR "Abstract":"unified multi-modal" OR "Author Keywords":"unified multi-modal") OR ("Document Title":"unified understanding and generation" OR "Abstract":"unified understanding and generation" OR "Author Keywords":"unified understanding and generation") OR ("Document Title":"understanding and generation" OR "Abstract":"understanding and generation" OR "Author Keywords":"understanding and generation") OR ("Document Title":"any-to-any" OR "Abstract":"any-to-any" OR "Author Keywords":"any-to-any")) AND ("Document Title":"discrete denoising" OR "Abstract":"discrete denoising" OR "Author Keywords":"discrete denoising") AND (("Document Title":mllms OR "Abstract":mllms OR "Author Keywords":mllms) OR ("Document Title":"visual understanding" OR "Abstract":"visual understanding" OR "Author Keywords":"visual understanding") OR ("Document Title":"image understanding" OR "Abstract":"image understanding" OR "Author Keywords":"image understanding"))
```
S2p-M-r5:
```
((("Document Title":"mixed-modal" OR "Abstract":"mixed-modal" OR "Author Keywords":"mixed-modal") OR ("Document Title":"mixed-modals" OR "Abstract":"mixed-modals" OR "Author Keywords":"mixed-modals")) OR ("Document Title":"mixed-modality" OR "Abstract":"mixed-modality" OR "Author Keywords":"mixed-modality")) AND (("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) OR ("Document Title":"masked generative" OR "Abstract":"masked generative" OR "Author Keywords":"masked generative") OR (("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"discrete flows" OR "Abstract":"discrete flows" OR "Author Keywords":"discrete flows")) OR ("Document Title":"flow matching" OR "Abstract":"flow matching" OR "Author Keywords":"flow matching") OR ("Document Title":"rectified flow" OR "Abstract":"rectified flow" OR "Author Keywords":"rectified flow")) AND (("Document Title":multimodal OR "Abstract":multimodal OR "Author Keywords":multimodal) OR ("Document Title":"multi-modal" OR "Abstract":"multi-modal" OR "Author Keywords":"multi-modal") OR ("Document Title":"vision-language" OR "Abstract":"vision-language" OR "Author Keywords":"vision-language") OR ("Document Title":"text-to-image" OR "Abstract":"text-to-image" OR "Author Keywords":"text-to-image") OR ("Document Title":"image generation" OR "Abstract":"image generation" OR "Author Keywords":"image generation") OR ("Document Title":mllm OR "Abstract":mllm OR "Author Keywords":mllm))
```
S2p-M-r6:
```
((("Document Title":"mixed-modal" OR "Abstract":"mixed-modal" OR "Author Keywords":"mixed-modal") OR ("Document Title":"mixed-modals" OR "Abstract":"mixed-modals" OR "Author Keywords":"mixed-modals")) OR ("Document Title":"mixed-modality" OR "Abstract":"mixed-modality" OR "Author Keywords":"mixed-modality")) AND (("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) OR ("Document Title":"masked generative" OR "Abstract":"masked generative" OR "Author Keywords":"masked generative") OR (("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"discrete flows" OR "Abstract":"discrete flows" OR "Author Keywords":"discrete flows")) OR ("Document Title":"flow matching" OR "Abstract":"flow matching" OR "Author Keywords":"flow matching") OR ("Document Title":"rectified flow" OR "Abstract":"rectified flow" OR "Author Keywords":"rectified flow")) AND (("Document Title":mllms OR "Abstract":mllms OR "Author Keywords":mllms) OR ("Document Title":"visual understanding" OR "Abstract":"visual understanding" OR "Author Keywords":"visual understanding") OR ("Document Title":"image understanding" OR "Abstract":"image understanding" OR "Author Keywords":"image understanding"))
```
S2p-M-r7:
```
((("Document Title":"mixed-modal" OR "Abstract":"mixed-modal" OR "Author Keywords":"mixed-modal") OR ("Document Title":"mixed-modals" OR "Abstract":"mixed-modals" OR "Author Keywords":"mixed-modals")) OR ("Document Title":"mixed-modality" OR "Abstract":"mixed-modality" OR "Author Keywords":"mixed-modality")) AND ("Document Title":"discrete denoising" OR "Abstract":"discrete denoising" OR "Author Keywords":"discrete denoising") AND (("Document Title":multimodal OR "Abstract":multimodal OR "Author Keywords":multimodal) OR ("Document Title":"multi-modal" OR "Abstract":"multi-modal" OR "Author Keywords":"multi-modal") OR ("Document Title":"vision-language" OR "Abstract":"vision-language" OR "Author Keywords":"vision-language") OR ("Document Title":"text-to-image" OR "Abstract":"text-to-image" OR "Author Keywords":"text-to-image") OR ("Document Title":"image generation" OR "Abstract":"image generation" OR "Author Keywords":"image generation") OR ("Document Title":mllm OR "Abstract":mllm OR "Author Keywords":mllm))
```
S2p-M-r8:
```
((("Document Title":"mixed-modal" OR "Abstract":"mixed-modal" OR "Author Keywords":"mixed-modal") OR ("Document Title":"mixed-modals" OR "Abstract":"mixed-modals" OR "Author Keywords":"mixed-modals")) OR ("Document Title":"mixed-modality" OR "Abstract":"mixed-modality" OR "Author Keywords":"mixed-modality")) AND ("Document Title":"discrete denoising" OR "Abstract":"discrete denoising" OR "Author Keywords":"discrete denoising") AND (("Document Title":mllms OR "Abstract":mllms OR "Author Keywords":mllms) OR ("Document Title":"visual understanding" OR "Abstract":"visual understanding" OR "Author Keywords":"visual understanding") OR ("Document Title":"image understanding" OR "Abstract":"image understanding" OR "Author Keywords":"image understanding"))
```
S2p-VLA-r1:
```
(("Document Title":"vision-language-action" OR "Abstract":"vision-language-action" OR "Author Keywords":"vision-language-action") OR ("Document Title":vla OR "Abstract":vla OR "Author Keywords":vla) OR ("Document Title":vlas OR "Abstract":vlas OR "Author Keywords":vlas)) AND (("Document Title":"discrete diffusion" OR "Abstract":"discrete diffusion" OR "Author Keywords":"discrete diffusion") OR ("Document Title":"discrete denoising" OR "Abstract":"discrete denoising" OR "Author Keywords":"discrete denoising") OR ("Document Title":"masked diffusion" OR "Abstract":"masked diffusion" OR "Author Keywords":"masked diffusion") OR ("Document Title":"diffusion-based" OR "Abstract":"diffusion-based" OR "Author Keywords":"diffusion-based") OR ("Document Title":"unified diffusion" OR "Abstract":"unified diffusion" OR "Author Keywords":"unified diffusion"))
```
S2p-VLA-r2:
```
(("Document Title":"vision-language-action" OR "Abstract":"vision-language-action" OR "Author Keywords":"vision-language-action") OR ("Document Title":vla OR "Abstract":vla OR "Author Keywords":vla) OR ("Document Title":vlas OR "Abstract":vlas OR "Author Keywords":vlas)) AND ((("Document Title":"diffusion language model" OR "Abstract":"diffusion language model" OR "Author Keywords":"diffusion language model") OR ("Document Title":"diffusion language models" OR "Abstract":"diffusion language models" OR "Author Keywords":"diffusion language models")) OR ("Document Title":dllm OR "Abstract":dllm OR "Author Keywords":dllm) OR ("Document Title":dllms OR "Abstract":dllms OR "Author Keywords":dllms))
```

### ACM Digital Library (folder `acm-dl`; file names `acm-dl-S1p-<part>[-rN]-<YYYYMMDD>` and `acm-dl-S2p-<part>[-rN]-<YYYYMMDD>`)

Advanced Search, query-syntax box as in section 4. NOT is written `NOT`; Title, Abstract and Keyword fields repeat the expression. Wildcards in phrases are not assumed (singular and plural written out) **[unverified]**.

S1p-A1:
```
(Title:(("diffusion language model" OR "diffusion language models") OR ("language diffusion model" OR "language diffusion models") OR ("diffusion llm" OR "diffusion llms") OR ("diffusion lm" OR "diffusion lms") OR dllm OR dllms OR ("diffusion-based language model" OR "diffusion-based language models") OR ("diffusion-based llm" OR "diffusion-based llms") OR ("diffusion large language model" OR "diffusion large language models") OR ("diffusion-based large language model" OR "diffusion-based large language models") OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR ("diffusion mllm" OR "diffusion mllms") OR ("diffusion vlm" OR "diffusion vlms") OR ("diffusion vision-language model" OR "diffusion vision-language models") OR dmllm OR dmllms OR dvlm OR dvlms) OR Abstract:(("diffusion language model" OR "diffusion language models") OR ("language diffusion model" OR "language diffusion models") OR ("diffusion llm" OR "diffusion llms") OR ("diffusion lm" OR "diffusion lms") OR dllm OR dllms OR ("diffusion-based language model" OR "diffusion-based language models") OR ("diffusion-based llm" OR "diffusion-based llms") OR ("diffusion large language model" OR "diffusion large language models") OR ("diffusion-based large language model" OR "diffusion-based large language models") OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR ("diffusion mllm" OR "diffusion mllms") OR ("diffusion vlm" OR "diffusion vlms") OR ("diffusion vision-language model" OR "diffusion vision-language models") OR dmllm OR dmllms OR dvlm OR dvlms) OR Keyword:(("diffusion language model" OR "diffusion language models") OR ("language diffusion model" OR "language diffusion models") OR ("diffusion llm" OR "diffusion llms") OR ("diffusion lm" OR "diffusion lms") OR dllm OR dllms OR ("diffusion-based language model" OR "diffusion-based language models") OR ("diffusion-based llm" OR "diffusion-based llms") OR ("diffusion large language model" OR "diffusion large language models") OR ("diffusion-based large language model" OR "diffusion-based large language models") OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR ("diffusion mllm" OR "diffusion mllms") OR ("diffusion vlm" OR "diffusion vlms") OR ("diffusion vision-language model" OR "diffusion vision-language models") OR dmllm OR dmllms OR dvlm OR dvlms))
```
S1p-A2-r1:
```
(Title:(("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows") OR ("discrete state-space" OR "discrete state-spaces")) AND (language OR text OR token* OR ("language model" OR "language models") OR llm* OR vocabulary OR autoregressive OR reasoning)) OR Abstract:(("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows") OR ("discrete state-space" OR "discrete state-spaces")) AND (language OR text OR token* OR ("language model" OR "language models") OR llm* OR vocabulary OR autoregressive OR reasoning)) OR Keyword:(("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows") OR ("discrete state-space" OR "discrete state-spaces")) AND (language OR text OR token* OR ("language model" OR "language models") OR llm* OR vocabulary OR autoregressive OR reasoning)))
```
S1p-A2-r2:
```
(Title:(("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows") OR ("discrete state-space" OR "discrete state-spaces")) NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)) OR Abstract:(("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows") OR ("discrete state-space" OR "discrete state-spaces")) NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)) OR Keyword:(("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows") OR ("discrete state-space" OR "discrete state-spaces")) NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)))
```
S1p-A3-r1:
```
(Title:(("non-autoregressive language model" OR "non-autoregressive language models")) OR Abstract:(("non-autoregressive language model" OR "non-autoregressive language models")) OR Keyword:(("non-autoregressive language model" OR "non-autoregressive language models")))
```
S1p-A3-r2:
```
(Title:("absorbing state" AND (language OR text OR token* OR ("language model" OR "language models"))) OR Abstract:("absorbing state" AND (language OR text OR token* OR ("language model" OR "language models"))) OR Keyword:("absorbing state" AND (language OR text OR token* OR ("language model" OR "language models"))))
```
S1p-A3-r3:
```
(Title:("any-order" AND (language OR text OR token* OR ("language model" OR "language models"))) OR Abstract:("any-order" AND (language OR text OR token* OR ("language model" OR "language models"))) OR Keyword:("any-order" AND (language OR text OR token* OR ("language model" OR "language models"))))
```
S1p-A3-r4:
```
(Title:("non-autoregressive" AND diffusion NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) OR Abstract:("non-autoregressive" AND diffusion NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) OR Keyword:("non-autoregressive" AND diffusion NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)))
```
S1p-B:
```
(Title:(diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR ("discrete sequence" OR "discrete sequences") OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR ("topic model" OR "topic models") OR "triple extraction" OR "information extraction") NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) OR Abstract:(diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR ("discrete sequence" OR "discrete sequences") OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR ("topic model" OR "topic models") OR "triple extraction" OR "information extraction") NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)) OR Keyword:(diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR ("discrete sequence" OR "discrete sequences") OR "speculative decoding" OR "categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization OR dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR ("topic model" OR "topic models") OR "triple extraction" OR "information extraction") NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*)))
```
S1p-C:
```
(Title:(diffusion AND (("language model" OR "language models") OR llm*) NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)) OR Abstract:(diffusion AND (("language model" OR "language models") OR llm*) NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)) OR Keyword:(diffusion AND (("language model" OR "language models") OR llm*) NOT (protein* OR molecul* OR antibod* OR peptide* OR rna OR dna OR drug* OR crystal* OR chemi* OR genom* OR biolog* OR "graph generation" OR "traveling salesman" OR recommend*) NOT (image* OR video* OR 3d OR audio OR visual* OR pixel* OR photo* OR segmentation)))
```
S2p-M:
```
(Title:(("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR ("mixed-modal" OR "mixed-modals") OR "mixed-modality") AND (diffusion OR "masked generative" OR ("discrete flow" OR "discrete flows") OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")) OR Abstract:(("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR ("mixed-modal" OR "mixed-modals") OR "mixed-modality") AND (diffusion OR "masked generative" OR ("discrete flow" OR "discrete flows") OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")) OR Keyword:(("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR ("mixed-modal" OR "mixed-modals") OR "mixed-modality") AND (diffusion OR "masked generative" OR ("discrete flow" OR "discrete flows") OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding" OR "image understanding")))
```
S2p-VLA:
```
(Title:(("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR ("diffusion language model" OR "diffusion language models") OR dllm OR dllms)) OR Abstract:(("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR ("diffusion language model" OR "diffusion language models") OR dllm OR dllms)) OR Keyword:(("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR ("diffusion language model" OR "diffusion language models") OR dllm OR dllms)))
```

### SpringerLink (folder `springerlink`; file names `springerlink-S1p-<part>[-rN]-<YYYYMMDD>` and `springerlink-S2p-<part>[-rN]-<YYYYMMDD>`)

Main keyword box (full text, relevance sorted, 1,000-record cap) as Run B of section 5 and title box as Run A. NOT clauses are **dropped**; run the parts in the *title* box (Run A form) first, since the text cannot be limited to the abstract. Record which box each file came from.

S1p-A1-r1:
```
("diffusion language model" OR "diffusion language models") OR ("language diffusion model" OR "language diffusion models") OR ("diffusion llm" OR "diffusion llms") OR ("diffusion lm" OR "diffusion lms")
```
S1p-A1-r2:
```
dllm OR dllms OR ("diffusion-based language model" OR "diffusion-based language models") OR ("diffusion-based llm" OR "diffusion-based llms") OR ("diffusion large language model" OR "diffusion large language models")
```
S1p-A1-r3:
```
("diffusion-based large language model" OR "diffusion-based large language models") OR "text diffusion" OR "block diffusion" OR "absorbing diffusion" OR ("diffusion mllm" OR "diffusion mllms")
```
S1p-A1-r4:
```
("diffusion vlm" OR "diffusion vlms") OR ("diffusion vision-language model" OR "diffusion vision-language models") OR dmllm OR dmllms OR dvlm OR dvlms
```
S1p-A2-r1:
```
("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows") OR ("discrete state-space" OR "discrete state-spaces")) AND (language OR text OR token* OR ("language model" OR "language models") OR llm* OR vocabulary OR autoregressive)
```
S1p-A2-r2:
```
("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows") OR ("discrete state-space" OR "discrete state-spaces")) AND reasoning
```
S1p-A2-r3:
```
("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows") OR ("discrete state-space" OR "discrete state-spaces"))
```
S1p-A3-r1:
```
("non-autoregressive language model" OR "non-autoregressive language models")
```
S1p-A3-r2:
```
"absorbing state" AND (language OR text OR token* OR ("language model" OR "language models"))
```
S1p-A3-r3:
```
"any-order" AND (language OR text OR token* OR ("language model" OR "language models"))
```
S1p-A3-r4:
```
"non-autoregressive" AND diffusion
```
S1p-B-r1:
```
diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence" OR seq2seq OR ("discrete sequence" OR "discrete sequences") OR "speculative decoding")
```
S1p-B-r2:
```
diffusion AND ("categorical data" OR "discrete data" OR paraphras* OR "textual diffusion" OR "text modeling" OR "named entity" OR sentiment OR summarization)
```
S1p-B-r3:
```
diffusion AND (dialog* OR dialogue OR "machine translation" OR "text style" OR commonsense OR ("topic model" OR "topic models") OR "triple extraction")
```
S1p-B-r4:
```
diffusion AND "information extraction"
```
S1p-C:
```
diffusion AND (("language model" OR "language models") OR llm*)
```
S2p-M-r1:
```
("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR ("mixed-modal" OR "mixed-modals") OR "mixed-modality") AND (diffusion OR "masked generative" OR ("discrete flow" OR "discrete flows") OR "flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image" OR "image generation" OR mllm OR mllms OR "visual understanding")
```
S2p-M-r2:
```
("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any" OR ("mixed-modal" OR "mixed-modals") OR "mixed-modality") AND (diffusion OR "masked generative" OR ("discrete flow" OR "discrete flows") OR "flow matching" OR "rectified flow" OR "discrete denoising") AND "image understanding"
```
S2p-VLA-r1:
```
("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based" OR "unified diffusion" OR ("diffusion language model" OR "diffusion language models") OR dllm)
```
S2p-VLA-r2:
```
("vision-language-action" OR vla OR vlas) AND dllms
```

### ScienceDirect (folder `sciencedirect`; file names `sciencedirect-S1p-<part>[-rN]-<YYYYMMDD>` and `sciencedirect-S2p-<part>[-rN]-<YYYYMMDD>`)

Field *Title, abstract or author-specified keywords* as in section 6. The reported cap of 8 Boolean operators per field **[unverified]** is met by cutting OR lists to 4 terms; NOT clauses are **dropped** (excluded topics go out at screening, X1).

S1p-A1-r1:
```
("diffusion language model" OR "diffusion language models") OR ("language diffusion model" OR "language diffusion models")
```
S1p-A1-r2:
```
("diffusion llm" OR "diffusion llms") OR ("diffusion lm" OR "diffusion lms")
```
S1p-A1-r3:
```
dllm OR dllms OR ("diffusion-based language model" OR "diffusion-based language models")
```
S1p-A1-r4:
```
("diffusion-based llm" OR "diffusion-based llms") OR ("diffusion large language model" OR "diffusion large language models")
```
S1p-A1-r5:
```
("diffusion-based large language model" OR "diffusion-based large language models") OR "text diffusion" OR "block diffusion"
```
S1p-A1-r6:
```
"absorbing diffusion" OR ("diffusion mllm" OR "diffusion mllms")
```
S1p-A1-r7:
```
("diffusion vlm" OR "diffusion vlms") OR ("diffusion vision-language model" OR "diffusion vision-language models")
```
S1p-A1-r8:
```
dmllm OR dmllms OR dvlm OR dvlms
```
S1p-A2-r1:
```
("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows")) AND (language OR text OR token*)
```
S1p-A2-r2:
```
("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows")) AND (("language model" OR "language models") OR llm* OR vocabulary)
```
S1p-A2-r3:
```
("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows")) AND (autoregressive OR reasoning)
```
S1p-A2-r4:
```
("discrete state-space" OR "discrete state-spaces") AND (language OR text OR token*)
```
S1p-A2-r5:
```
("discrete state-space" OR "discrete state-spaces") AND (("language model" OR "language models") OR llm* OR vocabulary)
```
S1p-A2-r6:
```
("discrete state-space" OR "discrete state-spaces") AND (autoregressive OR reasoning)
```
S1p-A2-r7:
```
("discrete diffusion" OR "masked diffusion" OR ("discrete flow" OR "discrete flows"))
```
S1p-A2-r8:
```
("discrete state-space" OR "discrete state-spaces")
```
S1p-A3-r1:
```
("non-autoregressive language model" OR "non-autoregressive language models")
```
S1p-A3-r2:
```
"absorbing state" AND (language OR text OR token*)
```
S1p-A3-r3:
```
"absorbing state" AND ("language model" OR "language models")
```
S1p-A3-r4:
```
"any-order" AND (language OR text OR token*)
```
S1p-A3-r5:
```
"any-order" AND ("language model" OR "language models")
```
S1p-A3-r6:
```
"non-autoregressive" AND diffusion
```
S1p-B-r1:
```
diffusion AND ("text generation" OR "language generation" OR "natural language generation" OR "sequence-to-sequence")
```
S1p-B-r2:
```
diffusion AND (seq2seq OR ("discrete sequence" OR "discrete sequences") OR "speculative decoding")
```
S1p-B-r3:
```
diffusion AND ("categorical data" OR "discrete data" OR paraphras* OR "textual diffusion")
```
S1p-B-r4:
```
diffusion AND ("text modeling" OR "named entity" OR sentiment OR summarization)
```
S1p-B-r5:
```
diffusion AND (dialog* OR dialogue OR "machine translation" OR "text style")
```
S1p-B-r6:
```
diffusion AND (commonsense OR ("topic model" OR "topic models") OR "triple extraction")
```
S1p-B-r7:
```
diffusion AND "information extraction"
```
S1p-C:
```
diffusion AND (("language model" OR "language models") OR llm*)
```
S2p-M-r1:
```
("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation") AND (diffusion OR "masked generative" OR ("discrete flow" OR "discrete flows")) AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image")
```
S2p-M-r2:
```
("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation") AND (diffusion OR "masked generative" OR ("discrete flow" OR "discrete flows")) AND ("image generation" OR mllm OR mllms OR "visual understanding")
```
S2p-M-r3:
```
("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation") AND (diffusion OR "masked generative" OR ("discrete flow" OR "discrete flows")) AND "image understanding"
```
S2p-M-r4:
```
("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation") AND ("flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image")
```
S2p-M-r5:
```
("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation") AND ("flow matching" OR "rectified flow" OR "discrete denoising") AND ("image generation" OR mllm OR mllms OR "visual understanding")
```
S2p-M-r6:
```
("unified multimodal" OR "unified multi-modal" OR "unified understanding and generation" OR "understanding and generation") AND ("flow matching" OR "rectified flow" OR "discrete denoising") AND "image understanding"
```
S2p-M-r7:
```
("any-to-any" OR ("mixed-modal" OR "mixed-modals") OR "mixed-modality") AND (diffusion OR "masked generative" OR ("discrete flow" OR "discrete flows")) AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image")
```
S2p-M-r8:
```
("any-to-any" OR ("mixed-modal" OR "mixed-modals") OR "mixed-modality") AND (diffusion OR "masked generative" OR ("discrete flow" OR "discrete flows")) AND ("image generation" OR mllm OR mllms OR "visual understanding")
```
S2p-M-r9:
```
("any-to-any" OR ("mixed-modal" OR "mixed-modals") OR "mixed-modality") AND (diffusion OR "masked generative" OR ("discrete flow" OR "discrete flows")) AND "image understanding"
```
S2p-M-r10:
```
("any-to-any" OR ("mixed-modal" OR "mixed-modals") OR "mixed-modality") AND ("flow matching" OR "rectified flow" OR "discrete denoising") AND (multimodal OR "multi-modal" OR "vision-language" OR "text-to-image")
```
S2p-M-r11:
```
("any-to-any" OR ("mixed-modal" OR "mixed-modals") OR "mixed-modality") AND ("flow matching" OR "rectified flow" OR "discrete denoising") AND ("image generation" OR mllm OR mllms OR "visual understanding")
```
S2p-M-r12:
```
("any-to-any" OR ("mixed-modal" OR "mixed-modals") OR "mixed-modality") AND ("flow matching" OR "rectified flow" OR "discrete denoising") AND "image understanding"
```
S2p-VLA-r1:
```
("vision-language-action" OR vla OR vlas) AND ("discrete diffusion" OR "discrete denoising" OR "masked diffusion" OR "diffusion-based")
```
S2p-VLA-r2:
```
("vision-language-action" OR vla OR vlas) AND ("unified diffusion" OR ("diffusion language model" OR "diffusion language models") OR dllm)
```
S2p-VLA-r3:
```
("vision-language-action" OR vla OR vlas) AND dllms
```

After the exports are in place the checks of the section at the end of this sheet apply unchanged. lit-scout evaluates each part again locally on title and abstract with the specification above before merging, so a database that ignores part of a string does not change what enters screening.
<!-- END S1p-S2p (D0026) -->

---

## Original strings S1 and S2 (second run): the protocol strings, verbatim from protocol.md section 3

S1, language:
```
("diffusion language model*" OR "discrete diffusion" OR "masked diffusion" OR "absorbing diffusion" OR "absorbing state" OR "discrete flow matching" OR "diffusion LLM" OR "diffusion large language model*" OR "text diffusion" OR "non-autoregressive" AND diffusion) AND (language OR text OR token* OR "language model*")
```

S2, unified multimodal:
```
("unified multimodal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any") AND (diffusion OR "masked generative" OR "discrete flow" OR "flow matching") AND (multimodal OR "vision-language" OR "text-to-image")
```

Reading rule used in every adaptation below: AND binds tighter than OR, so `"non-autoregressive" AND diffusion` is one OR-term, written with explicit parentheses. Fields: title, abstract, keywords (author keywords; Scopus also searches index keywords inside TITLE-ABS-KEY).

## 1. Scopus (folder `scopus`, export CSV)

Advanced document search. Language and year are in the query, so no sidebar filters are needed. Document type: leave unrestricted.

S1:
```
TITLE-ABS-KEY(("diffusion language model*" OR "discrete diffusion" OR "masked diffusion" OR "absorbing diffusion" OR "absorbing state" OR "discrete flow matching" OR "diffusion LLM" OR "diffusion large language model*" OR "text diffusion" OR ("non-autoregressive" AND diffusion)) AND (language OR text OR token* OR "language model*")) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```

S2:
```
TITLE-ABS-KEY(("unified multimodal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any") AND (diffusion OR "masked generative" OR "discrete flow" OR "flow matching") AND (multimodal OR "vision-language" OR "text-to-image")) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)
```

Field restriction: `TITLE-ABS-KEY` (title, abstract, author keywords, index keywords). Date: `PUBYEAR > 2020 AND PUBYEAR < 2027` (calendar years 2021 to 2026; Scopus cannot cut inside a year, so the extraction date bounds the end). Language: `LANGUAGE(english)`.

**[unverified]** Wildcards inside a quoted phrase (`"diffusion language model*"`). If Scopus warns, ignores them or returns fewer hits than the unstarred phrase, replace `"diffusion language model*"` by `"diffusion language model" OR "diffusion language models"` and `"diffusion large language model*"` by `"diffusion large language model" OR "diffusion large language models"`, and write that substitution in `.meta.txt`.

Export: select all, Export, **CSV**, tick *Citation information*, *Bibliographical information*, *Abstract & keywords*. If the hit count is above the export limit shown in the dialog **[unverified, check on screen]**, split by `PUBYEAR = 2021` ... `PUBYEAR = 2026`.

## 2. Web of Science Core Collection (folder `web-of-science`, export RIS or tab-delimited, full record)

Advanced Search, database *Web of Science Core Collection* (record the editions your licence includes in `.meta.txt`).

S1:
```
TS=(("diffusion language model*" OR "discrete diffusion" OR "masked diffusion" OR "absorbing diffusion" OR "absorbing state" OR "discrete flow matching" OR "diffusion LLM" OR "diffusion large language model*" OR "text diffusion" OR ("non-autoregressive" AND diffusion)) AND (language OR text OR token* OR "language model*")) AND PY=(2021-2026)
```

S2:
```
TS=(("unified multimodal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any") AND (diffusion OR "masked generative" OR "discrete flow" OR "flow matching") AND (multimodal OR "vision-language" OR "text-to-image")) AND PY=(2021-2026)
```

Field restriction: `TS=` (Topic). Clarivate's Core Collection help lists Topic as title, abstract and author keywords; some Clarivate pages also list Keywords Plus **[unverified for your edition]**. To keep the protocol's "title, abstract, keywords" strictly, use the explicit form instead: replace `TS=(X)` by `(TI=(X) OR AB=(X) OR AK=(X))`, where X is the whole bracketed string up to `AND PY`. Date: `PY=(2021-2026)`. Language: after the search, left panel *Languages*, tick English, or append `AND LA=English` **[unverified tag; the panel filter is certain]**. Record which you used.

Export: Export, **RIS (other reference software)** or **Tab delimited file**, record content **Full Record** (includes the abstract). Maximum 1,000 records per file in the export dialog; use record ranges 1-1000, 1001-2000, and so on (Clarivate release notes; the dialog shows the live limit).

## 3. IEEE Xplore (folder `ieee-xplore`, export CSV)

Command Search (Advanced Search, *Command Search* tab). Year range is set with the *Year* filter after the search: **2021 to 2026**. IEEE's command search has no language field; the English filter is not available, so non-English records are removed at screening (code X8) and `.meta.txt` says so.

Field restriction: `"Document Title"`, `"Abstract"`, `"Author Keywords"` (IEEE field names in double quotes, a colon, then the quoted phrase; operators in capitals). Phrases are written without the `*` wildcard, with the singular and plural listed (IEEE's wildcard rules for quoted phrases are **[unverified]**); `token*` keeps its star.

S1, full string:
```
(("Document Title":"diffusion language model" OR "Abstract":"diffusion language model" OR "Author Keywords":"diffusion language model") OR ("Document Title":"diffusion language models" OR "Abstract":"diffusion language models" OR "Author Keywords":"diffusion language models") OR ("Document Title":"discrete diffusion" OR "Abstract":"discrete diffusion" OR "Author Keywords":"discrete diffusion") OR ("Document Title":"masked diffusion" OR "Abstract":"masked diffusion" OR "Author Keywords":"masked diffusion") OR ("Document Title":"absorbing diffusion" OR "Abstract":"absorbing diffusion" OR "Author Keywords":"absorbing diffusion") OR ("Document Title":"absorbing state" OR "Abstract":"absorbing state" OR "Author Keywords":"absorbing state") OR ("Document Title":"discrete flow matching" OR "Abstract":"discrete flow matching" OR "Author Keywords":"discrete flow matching") OR ("Document Title":"diffusion LLM" OR "Abstract":"diffusion LLM" OR "Author Keywords":"diffusion LLM") OR ("Document Title":"diffusion large language model" OR "Abstract":"diffusion large language model" OR "Author Keywords":"diffusion large language model") OR ("Document Title":"diffusion large language models" OR "Abstract":"diffusion large language models" OR "Author Keywords":"diffusion large language models") OR ("Document Title":"text diffusion" OR "Abstract":"text diffusion" OR "Author Keywords":"text diffusion") OR (("Document Title":"non-autoregressive" OR "Abstract":"non-autoregressive" OR "Author Keywords":"non-autoregressive") AND ("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion))) AND (("Document Title":language OR "Abstract":language OR "Author Keywords":language) OR ("Document Title":text OR "Abstract":text OR "Author Keywords":text) OR ("Document Title":token* OR "Abstract":token* OR "Author Keywords":token*) OR ("Document Title":"language model" OR "Abstract":"language model" OR "Author Keywords":"language model") OR ("Document Title":"language models" OR "Abstract":"language models" OR "Author Keywords":"language models"))
```

S2, full string:
```
(("Document Title":"unified multimodal" OR "Abstract":"unified multimodal" OR "Author Keywords":"unified multimodal") OR ("Document Title":"unified understanding and generation" OR "Abstract":"unified understanding and generation" OR "Author Keywords":"unified understanding and generation") OR ("Document Title":"understanding and generation" OR "Abstract":"understanding and generation" OR "Author Keywords":"understanding and generation") OR ("Document Title":"any-to-any" OR "Abstract":"any-to-any" OR "Author Keywords":"any-to-any")) AND (("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) OR ("Document Title":"masked generative" OR "Abstract":"masked generative" OR "Author Keywords":"masked generative") OR ("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"flow matching" OR "Abstract":"flow matching" OR "Author Keywords":"flow matching")) AND (("Document Title":multimodal OR "Abstract":multimodal OR "Author Keywords":multimodal) OR ("Document Title":"vision-language" OR "Abstract":"vision-language" OR "Author Keywords":"vision-language") OR ("Document Title":"text-to-image" OR "Abstract":"text-to-image" OR "Author Keywords":"text-to-image"))
```

IEEE limits the number of terms in a command search (one help source says 15, another 25 per clause) **[unverified]**. If the full strings above are refused, run the split runs; their union is the full string.

S1-run1:
```
(("Document Title":"diffusion language model" OR "Abstract":"diffusion language model" OR "Author Keywords":"diffusion language model") OR ("Document Title":"diffusion language models" OR "Abstract":"diffusion language models" OR "Author Keywords":"diffusion language models") OR ("Document Title":"diffusion LLM" OR "Abstract":"diffusion LLM" OR "Author Keywords":"diffusion LLM") OR ("Document Title":"diffusion large language model" OR "Abstract":"diffusion large language model" OR "Author Keywords":"diffusion large language model") OR ("Document Title":"diffusion large language models" OR "Abstract":"diffusion large language models" OR "Author Keywords":"diffusion large language models")) AND (("Document Title":language OR "Abstract":language OR "Author Keywords":language) OR ("Document Title":text OR "Abstract":text OR "Author Keywords":text) OR ("Document Title":token* OR "Abstract":token* OR "Author Keywords":token*) OR ("Document Title":"language model" OR "Abstract":"language model" OR "Author Keywords":"language model") OR ("Document Title":"language models" OR "Abstract":"language models" OR "Author Keywords":"language models"))
```

S1-run2:
```
(("Document Title":"discrete diffusion" OR "Abstract":"discrete diffusion" OR "Author Keywords":"discrete diffusion") OR ("Document Title":"masked diffusion" OR "Abstract":"masked diffusion" OR "Author Keywords":"masked diffusion") OR ("Document Title":"absorbing diffusion" OR "Abstract":"absorbing diffusion" OR "Author Keywords":"absorbing diffusion")) AND (("Document Title":language OR "Abstract":language OR "Author Keywords":language) OR ("Document Title":text OR "Abstract":text OR "Author Keywords":text) OR ("Document Title":token* OR "Abstract":token* OR "Author Keywords":token*) OR ("Document Title":"language model" OR "Abstract":"language model" OR "Author Keywords":"language model") OR ("Document Title":"language models" OR "Abstract":"language models" OR "Author Keywords":"language models"))
```

S1-run3:
```
(("Document Title":"absorbing state" OR "Abstract":"absorbing state" OR "Author Keywords":"absorbing state") OR ("Document Title":"discrete flow matching" OR "Abstract":"discrete flow matching" OR "Author Keywords":"discrete flow matching") OR ("Document Title":"text diffusion" OR "Abstract":"text diffusion" OR "Author Keywords":"text diffusion")) AND (("Document Title":language OR "Abstract":language OR "Author Keywords":language) OR ("Document Title":text OR "Abstract":text OR "Author Keywords":text) OR ("Document Title":token* OR "Abstract":token* OR "Author Keywords":token*) OR ("Document Title":"language model" OR "Abstract":"language model" OR "Author Keywords":"language model") OR ("Document Title":"language models" OR "Abstract":"language models" OR "Author Keywords":"language models"))
```

S1-run4:
```
(("Document Title":"non-autoregressive" OR "Abstract":"non-autoregressive" OR "Author Keywords":"non-autoregressive") AND ("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion)) AND (("Document Title":language OR "Abstract":language OR "Author Keywords":language) OR ("Document Title":text OR "Abstract":text OR "Author Keywords":text) OR ("Document Title":token* OR "Abstract":token* OR "Author Keywords":token*) OR ("Document Title":"language model" OR "Abstract":"language model" OR "Author Keywords":"language model") OR ("Document Title":"language models" OR "Abstract":"language models" OR "Author Keywords":"language models"))
```

S2-run1:
```
("Document Title":"unified multimodal" OR "Abstract":"unified multimodal" OR "Author Keywords":"unified multimodal") AND (("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) OR ("Document Title":"masked generative" OR "Abstract":"masked generative" OR "Author Keywords":"masked generative") OR ("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"flow matching" OR "Abstract":"flow matching" OR "Author Keywords":"flow matching")) AND (("Document Title":multimodal OR "Abstract":multimodal OR "Author Keywords":multimodal) OR ("Document Title":"vision-language" OR "Abstract":"vision-language" OR "Author Keywords":"vision-language") OR ("Document Title":"text-to-image" OR "Abstract":"text-to-image" OR "Author Keywords":"text-to-image"))
```

S2-run2:
```
("Document Title":"unified understanding and generation" OR "Abstract":"unified understanding and generation" OR "Author Keywords":"unified understanding and generation") AND (("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) OR ("Document Title":"masked generative" OR "Abstract":"masked generative" OR "Author Keywords":"masked generative") OR ("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"flow matching" OR "Abstract":"flow matching" OR "Author Keywords":"flow matching")) AND (("Document Title":multimodal OR "Abstract":multimodal OR "Author Keywords":multimodal) OR ("Document Title":"vision-language" OR "Abstract":"vision-language" OR "Author Keywords":"vision-language") OR ("Document Title":"text-to-image" OR "Abstract":"text-to-image" OR "Author Keywords":"text-to-image"))
```

S2-run3:
```
("Document Title":"understanding and generation" OR "Abstract":"understanding and generation" OR "Author Keywords":"understanding and generation") AND (("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) OR ("Document Title":"masked generative" OR "Abstract":"masked generative" OR "Author Keywords":"masked generative") OR ("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"flow matching" OR "Abstract":"flow matching" OR "Author Keywords":"flow matching")) AND (("Document Title":multimodal OR "Abstract":multimodal OR "Author Keywords":multimodal) OR ("Document Title":"vision-language" OR "Abstract":"vision-language" OR "Author Keywords":"vision-language") OR ("Document Title":"text-to-image" OR "Abstract":"text-to-image" OR "Author Keywords":"text-to-image"))
```

S2-run4:
```
("Document Title":"any-to-any" OR "Abstract":"any-to-any" OR "Author Keywords":"any-to-any") AND (("Document Title":diffusion OR "Abstract":diffusion OR "Author Keywords":diffusion) OR ("Document Title":"masked generative" OR "Abstract":"masked generative" OR "Author Keywords":"masked generative") OR ("Document Title":"discrete flow" OR "Abstract":"discrete flow" OR "Author Keywords":"discrete flow") OR ("Document Title":"flow matching" OR "Abstract":"flow matching" OR "Author Keywords":"flow matching")) AND (("Document Title":multimodal OR "Abstract":multimodal OR "Author Keywords":multimodal) OR ("Document Title":"vision-language" OR "Abstract":"vision-language" OR "Author Keywords":"vision-language") OR ("Document Title":"text-to-image" OR "Abstract":"text-to-image" OR "Author Keywords":"text-to-image"))
```

Export: *Export* above the results, **Results** tab, **CSV** (includes the abstract; community reports a cap of 2,000 records per export **[unverified]**; if a run exceeds the cap shown, split by year with the *Year* filter).

## 4. ACM Digital Library (folder `acm-dl`, export RIS or BibTeX with abstracts)

Advanced Search. Easiest route: build one row each for Title, Abstract and Keyword in the form, join with OR, run it once, then open *Edit Search* then *View Query Syntax* and paste the string shown there into `.meta.txt`; it must match what is below up to formatting. Field prefixes `Title:` and `Abstract:` appear in ACM's own examples; `Keyword:` **[unverified]**. Boolean operators must be capitals. Date: *Publication Date* filter, custom range **01/2021 to the month of the search**. ACM has no language filter; non-English records go out at screening (X8).

S1:
```
(Title:("diffusion language model" OR "diffusion language models" OR "discrete diffusion" OR "masked diffusion" OR "absorbing diffusion" OR "absorbing state" OR "discrete flow matching" OR "diffusion LLM" OR "diffusion large language model" OR "diffusion large language models" OR "text diffusion" OR ("non-autoregressive" AND diffusion)) OR Abstract:("diffusion language model" OR "diffusion language models" OR "discrete diffusion" OR "masked diffusion" OR "absorbing diffusion" OR "absorbing state" OR "discrete flow matching" OR "diffusion LLM" OR "diffusion large language model" OR "diffusion large language models" OR "text diffusion" OR ("non-autoregressive" AND diffusion)) OR Keyword:("diffusion language model" OR "diffusion language models" OR "discrete diffusion" OR "masked diffusion" OR "absorbing diffusion" OR "absorbing state" OR "discrete flow matching" OR "diffusion LLM" OR "diffusion large language model" OR "diffusion large language models" OR "text diffusion" OR ("non-autoregressive" AND diffusion))) AND (Title:(language OR text OR token* OR "language model" OR "language models") OR Abstract:(language OR text OR token* OR "language model" OR "language models") OR Keyword:(language OR text OR token* OR "language model" OR "language models"))
```

S2:
```
(Title:("unified multimodal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any") OR Abstract:("unified multimodal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any") OR Keyword:("unified multimodal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any")) AND (Title:(diffusion OR "masked generative" OR "discrete flow" OR "flow matching") OR Abstract:(diffusion OR "masked generative" OR "discrete flow" OR "flow matching") OR Keyword:(diffusion OR "masked generative" OR "discrete flow" OR "flow matching")) AND (Title:(multimodal OR "vision-language" OR "text-to-image") OR Abstract:(multimodal OR "vision-language" OR "text-to-image") OR Keyword:(multimodal OR "vision-language" OR "text-to-image"))
```

Split runs for S1 (if the editor refuses the length):

S1-run1:
```
(Title:("diffusion language model" OR "diffusion language models" OR "diffusion LLM" OR "diffusion large language model" OR "diffusion large language models") OR Abstract:("diffusion language model" OR "diffusion language models" OR "diffusion LLM" OR "diffusion large language model" OR "diffusion large language models") OR Keyword:("diffusion language model" OR "diffusion language models" OR "diffusion LLM" OR "diffusion large language model" OR "diffusion large language models")) AND (Title:(language OR text OR token* OR "language model" OR "language models") OR Abstract:(language OR text OR token* OR "language model" OR "language models") OR Keyword:(language OR text OR token* OR "language model" OR "language models"))
```

S1-run2:
```
(Title:("discrete diffusion" OR "masked diffusion" OR "absorbing diffusion") OR Abstract:("discrete diffusion" OR "masked diffusion" OR "absorbing diffusion") OR Keyword:("discrete diffusion" OR "masked diffusion" OR "absorbing diffusion")) AND (Title:(language OR text OR token* OR "language model" OR "language models") OR Abstract:(language OR text OR token* OR "language model" OR "language models") OR Keyword:(language OR text OR token* OR "language model" OR "language models"))
```

S1-run3:
```
(Title:("absorbing state" OR "discrete flow matching" OR "text diffusion") OR Abstract:("absorbing state" OR "discrete flow matching" OR "text diffusion") OR Keyword:("absorbing state" OR "discrete flow matching" OR "text diffusion")) AND (Title:(language OR text OR token* OR "language model" OR "language models") OR Abstract:(language OR text OR token* OR "language model" OR "language models") OR Keyword:(language OR text OR token* OR "language model" OR "language models"))
```

S1-run4:
```
(Title:(("non-autoregressive" AND diffusion)) OR Abstract:(("non-autoregressive" AND diffusion)) OR Keyword:(("non-autoregressive" AND diffusion))) AND (Title:(language OR text OR token* OR "language model" OR "language models") OR Abstract:(language OR text OR token* OR "language model" OR "language models") OR Keyword:(language OR text OR token* OR "language model" OR "language models"))
```

Export: select all results (raise the page size first), *Export Citations*, format **RIS** or **BibTeX**; the abstract is included only if the dialog offers it **[unverified]**, otherwise lit-scout fetches abstracts by DOI. ACM caps how many records one export holds **[unverified, check on screen]**; split by publication year if needed.

## 5. SpringerLink (folder `springerlink`, export CSV)

Advanced search. **Deviation to record:** SpringerLink searches full text and cannot be limited to the abstract or to keywords. The closest field is *Where the title contains*. Run A (primary, title only) approximates the protocol; Run B (all fields, full text, relevance-sorted) is supplementary and its export is truncated at 1,000, so it is a sample, not a complete search. Report both honestly in the PRISMA text.

Date: *Show documents published between* **2021** and **2026**. Content type: Article and Conference paper (note others if you keep them).

Run A, S1 (paste in *Where the title contains*):
```
("diffusion language model" OR "diffusion language models" OR "discrete diffusion" OR "masked diffusion" OR "absorbing diffusion" OR "absorbing state" OR "discrete flow matching" OR "diffusion LLM" OR "diffusion large language model" OR "diffusion large language models" OR "text diffusion" OR ("non-autoregressive" AND diffusion))
```

Run A, S2 (paste in *Where the title contains*):
```
("unified multimodal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any") AND (diffusion OR "masked generative" OR "discrete flow" OR "flow matching")
```

Run B, S1 (paste in the main keyword box, full text):
```
("diffusion language model" OR "diffusion language models" OR "discrete diffusion" OR "masked diffusion" OR "absorbing diffusion" OR "absorbing state" OR "discrete flow matching" OR "diffusion LLM" OR "diffusion large language model" OR "diffusion large language models" OR "text diffusion" OR ("non-autoregressive" AND diffusion)) AND (language OR text OR token* OR "language model" OR "language models")
```

Run B, S2 (paste in the main keyword box, full text):
```
("unified multimodal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any") AND (diffusion OR "masked generative" OR "discrete flow" OR "flow matching") AND (multimodal OR "vision-language" OR "text-to-image")
```

AND, OR, NOT and phrase quotes work in the fields; type them in capitals. Because Run A's title field cannot hold the second clause of S1, the clause `(language OR text OR token*)` is dropped in Run A for S1 and the title restriction stands in for it **[deviation]**; likewise Run A for S2 drops the third clause. Export: *Download results (.csv)* requires a personal login and holds at most 1,000 results; the file has no abstracts (title, authors, DOI, URL, year). Some sources say export exists only in the legacy search view **[unverified]**.

## 6. ScienceDirect (folder `sciencedirect`, export RIS)

Advanced search. Put the string in the field **Title, abstract or author-specified keywords** (this is exactly the protocol's field set; do not use *Find articles with these terms*, which searches the full text). Years: **2021-2026**. Article type: leave all (record what you choose). No language filter is offered; non-English go out at screening (X8). Operators in capitals; quotes make exact phrases; proximity is not supported.

S1, full string:
```
("diffusion language model" OR "diffusion language models" OR "discrete diffusion" OR "masked diffusion" OR "absorbing diffusion" OR "absorbing state" OR "discrete flow matching" OR "diffusion LLM" OR "diffusion large language model" OR "diffusion large language models" OR "text diffusion" OR ("non-autoregressive" AND diffusion)) AND (language OR text OR token* OR "language model" OR "language models")
```

S2, full string:
```
("unified multimodal" OR "unified understanding and generation" OR "understanding and generation" OR "any-to-any") AND (diffusion OR "masked generative" OR "discrete flow" OR "flow matching") AND (multimodal OR "vision-language" OR "text-to-image")
```

ScienceDirect is reported to limit Boolean operators per field (figures such as eight appear in library guides) **[unverified]**. If the full string is refused, use these split runs. In the S1 runs the second clause is shortened to `(language OR text OR token*)`, because `"language model"` and `"language models"` are already covered by `language`; this changes nothing in the result set.

S1-run1:
```
("diffusion language model" OR "diffusion language models" OR "diffusion LLM" OR "diffusion large language model" OR "diffusion large language models") AND (language OR text OR token*)
```

S1-run2:
```
("discrete diffusion" OR "masked diffusion" OR "absorbing diffusion") AND (language OR text OR token*)
```

S1-run3:
```
("absorbing state" OR "discrete flow matching" OR "text diffusion") AND (language OR text OR token*)
```

S1-run4:
```
("non-autoregressive" AND diffusion) AND (language OR text OR token*)
```

S2-run1:
```
"unified multimodal" AND (diffusion OR "masked generative" OR "discrete flow" OR "flow matching") AND (multimodal OR "vision-language" OR "text-to-image")
```

S2-run2:
```
"unified understanding and generation" AND (diffusion OR "masked generative" OR "discrete flow" OR "flow matching") AND (multimodal OR "vision-language" OR "text-to-image")
```

S2-run3:
```
"understanding and generation" AND (diffusion OR "masked generative" OR "discrete flow" OR "flow matching") AND (multimodal OR "vision-language" OR "text-to-image")
```

S2-run4:
```
"any-to-any" AND (diffusion OR "masked generative" OR "discrete flow" OR "flow matching") AND (multimodal OR "vision-language" OR "text-to-image")
```

Export: select all, *Export*, **Export citation to RIS**, choosing the option that includes the abstract **[unverified label]**. Check the per-export cap shown in the dialog; split by year if a run exceeds it.

## After the exports are in place

Folder names to create under `research/sources/search-raw/`: `scopus`, `web-of-science`, `ieee-xplore`, `acm-dl`, `springerlink`, `sciencedirect`. The search-log row lit-scout will append per file has the keys `database, string, query, filters, executed_utc, hits_reported, records_retrieved, export, sha256`, taken from the `.meta.txt` and the file. `hits_reported` is the count the site displayed; `records_retrieved` is the number of records in the exported file. If the two differ, say why in `.meta.txt`.
