# Subscription database search sheet (human run)

Prepared 2026-10-15 for protocol `research/review/protocol.md` section 3. The databases below need VIT eGateway access and cannot be run by an agent. Everything on this sheet is data to paste; nothing here has been run or tested against these databases (no access). Syntax was checked against the vendors' public help pages on 2026-10-15; anything marked **[unverified]** must be confirmed on screen and corrected in the log if the interface behaves differently.

## What to do, in order

1. Pick one **search date** (today or the day you start) and use it for all six databases. Write it in every `.meta.txt`. Date window: **2021-01-01 to the search date**, English (protocol section 3 filters).
2. For each database and each string (S1, S2): paste the string, apply the filters, read the hit count the site shows, export, then save the file as `research/sources/search-raw/<db-folder>/<db-folder>-<S1|S2>[-runN]-<YYYYMMDD>.<ext>` plus a sibling `.meta.txt` containing: search date and time (with time zone), the exact string as pasted, filters applied, hit count shown by the site, number of records in the export file, your name.
3. If the site rejects the full string (too long, too many operators, too many terms), use the **split runs** under that database. The union of the split runs equals the full string. Log each run as its own search and do not merge the export files.
4. If a result set exceeds the export cap, split by publication year (2021, 2022, ..., 2026) and keep the same string; note this in `.meta.txt`.
5. Do not edit the exports. Tell the orchestrator when they are in place; lit-scout then hashes them, adds one `search-log.jsonl` row per file, normalises IDs and deduplicates against `screening/records.jsonl` and `corpus/new-records-2026-10-15.jsonl`.

Export formats: CSV with abstracts where the database offers it (Scopus, IEEE Xplore); RIS with abstract otherwise (Web of Science full record, ACM, ScienceDirect). SpringerLink's CSV carries no abstracts; lit-scout fetches them by DOI afterwards.

## The protocol strings (verbatim, protocol.md section 3)

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
