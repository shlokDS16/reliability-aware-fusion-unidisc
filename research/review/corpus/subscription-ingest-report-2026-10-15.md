```yaml
agent: lit-scout
date: 2026-10-15
brief: re-runnable ingest of subscription-database exports (D0031); first run on Scopus
sources_examined:
  - research/sources/search-raw/scopus/scopus-Q1..Q5-20261016.csv (4,046 rows)
  - research/sources/search-raw/web-of-science/wos-union-*.ris (2,267 rows, arrived while the tool was being finished)
  - research/sources/search-raw/ieee-xplore/ieee-I1-2021-2024-20261015.csv (230 rows, one year slice of I1, arrived the same way)
coverage: >
  Scopus, Web of Science and the IEEE slice parsed from the real files. Parsers for WoS plain text and tab-delimited,
  ACM BibTeX and RIS, SpringerLink CSV and ScienceDirect RIS were tested only on synthetic fixtures (scratchpad), not on real exports.
  SpringerLink DOI abstract fetch: Crossref and Semantic Scholar functions tested live on three DOIs; no real SpringerLink file yet.
  No abstract was fetched in this run (none needed). Nothing was screened; no existing file was changed except one append-only file (search-log.jsonl).
claims:
  - statement: Parsed row counts equal the logged hit counts for Scopus (876, 530, 134, 1,670, 836) and for the WoS union (2,267)
    status: supported
    evidence: research/review/corpus/subscription-ingest-2026-10-15.json, files[].rows_match_expected
    level: E4
    confidence: 0.95
  - statement: The IEEE I1 slice (230 rows) is not the full query (1,203 expected); the check will pass only when all slices are present
    status: supported
    evidence: warnings in the summary JSON
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - SpringerLink, ACM and ScienceDirect formats on real exports; WoS plain text and tab-delimited on real exports
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Subscription-database ingest, first run (2026-10-15)

Script: `tools/ingest_subscription.py` (sha256 of the final version `981a652a92e6e15e9f9d10920d8bed8834b53a18ed360dd2a0696eeaeb76896e`). Decision: D0031; queue rule: D0027 and D0028.

## Command to rerun when new exports arrive

```
python tools/ingest_subscription.py
```

It scans `research/sources/search-raw/{scopus,web-of-science,ieee-xplore,acm-dl,springerlink,sciencedirect}/`, skips folders with no export, rewrites the three outputs from the raw files, keeps record ids stable through the previous records file, and appends a search-log row only for an export file (path plus sha256) not yet logged. A rerun with unchanged exports reproduces the records and queue files byte for byte (checked: same sha256 twice). When a rerun adds new queued records it also writes `subscription-queue-delta-<run>.jsonl` with only those. Options: `--db scopus,wos`, `--no-fetch`, `--no-log`, `--fetch-all-missing`, `--raw-root/--out-dir/--queue-out` (dry runs), `--date`.

## What the run covers

The task named Scopus. While the tool was being finished the user's Web of Science export (three RIS files, 2,267 rows = the logged union count) and one IEEE Xplore slice (`I1`, 2021-2024, 230 of 1,203 rows) appeared in their folders, so the final run, which scans every folder, includes them. The Scopus numbers are reported separately below. The records and queue files therefore hold Scopus + WoS + the IEEE slice. Later exports go through the same command; ids of existing records do not change.

## Files and hashes

Raw exports (sha256, bytes, rows parsed / expected):

| file | sha256 | bytes | rows / expected |
|---|---|---|---|
| scopus-Q1-20261016.csv | 48c62d7ff8dc6375f7b4912486ae605eebf38feed52271404427ea58dc7cd2ff | 2,805,766 | 876 / 876 |
| scopus-Q2-20261016.csv | 6d6b816c6f3cdd43f6c54eb8ef13dc28017f77a69f39694e8c813faeb2e9e70e | 1,570,161 | 530 / 530 |
| scopus-Q3-20261016.csv | 564f30bd90893d7a26a06f548a14b7861eb61ab22887e66c7faf06b4c0df3d70 | 433,400 | 134 / 134 |
| scopus-Q4-20261016.csv | e06cb91831a0b5d4f8b18c922aa60c6de82fa02e43c6c9f823fb61b159a91ee8 | 5,225,244 | 1,670 / 1,670 |
| scopus-Q5-20261016.csv | 4bc5c79f3ada4a64b1c703704526354d1958d29ca4caa7e6c2b8bc066a89ffb3 | 2,751,667 | 836 / 836 |
| wos-union-0001-1000-20261015.ris | 996efef9a209278d4667bd15eb3843aaa5fc4fcfb65b01035654c8d73fab139a | 2,887,592 | 1,000 (union 2,267) |
| wos-union-1001-2000-20261015.ris | eaaa4e7c81dfb26b668353be88f790719c5219eb3acf35afe5937875c5189a5c | 2,843,713 | 1,000 |
| wos-union-2001-2267-20261015.ris | 67adb39c68f51ed9eb82fe26f3239a73ce4167339f39bab1a24601b3a9717d0f | 861,065 | 267 (sum 2,267 = union) |
| ieee-I1-2021-2024-20261015.csv | a984105c323637a7201ae5dd2466fcec5a88d1e8888e4caf8e9968e8eba906ac | 543,644 | 230 (query total 1,203: slice only) |

The Scopus files carry the label 20261016 but were exported on 2026-10-15 (file times 22:18-22:24 IST; see `web-of-science/wos-queries-20261015.md`); not renamed. Search-log rows (9 appended, one per file, original 9-key format, `executed_utc` = file modification time; for a multi-file query `hits_reported` is the site's count for the query and `records_retrieved` the rows in that file).

Outputs (run `20261015T183243Z`):

| file | rows | sha256 |
|---|---|---|
| research/review/corpus/subscription-records-2026-10-15.jsonl | 3,895 | 25b738dfbafef7f160b83d22dc23cb5b926fd7cf4b060dacf0e3809eb5f09751 |
| research/review/screening/v2/subscription-queue.jsonl | 170 | 1e77d1cd4f2d0ffbcdce338d5fa4b70270acaa89e733bd5aae324d9f7c7027f9 |
| research/review/corpus/subscription-ingest-2026-10-15.json | (counts) | changes with every run (carries run time); see the file |

Queue rows are `{id, title, abstract}` only, as in `screening/v2/batch-0*.jsonl`; ids are `U00001`...

## Scopus (the requested run)

| query | rows | front matter | dup in file | dup in db (earlier query) | dup of corpus | new unique | fail S1''/S2'' | pass, queued |
|---|---|---|---|---|---|---|---|---|
| Q1 (union) | 876 | 79 | 1 | 0 | 634 | 162 | 73 | 89 |
| Q2 (S1':A2-r2) | 530 | 2 | 3 | 100 | 266 | 159 | 153 | 6 |
| Q3 (S1':A3-r4) | 134 | 0 | 0 | 134 | 0 | 0 | 0 | 0 |
| Q4 (S1':B) | 1,670 | 175 | 1 | 136 | 876 | 482 | 444 | 38 |
| Q5 (S1':C) | 836 | 46 | 1 | 204 | 378 | 207 | 183 | 24 |
| total | 4,046 | 302 | 6 | 574 | 2,154 | 1,010 | 853 | 157 |

Each row is counted once, at the first file (Q1, then Q2, ...) in which its record appears, so the columns add up to the rows. Q3 adds nothing beyond Q1/Q2/Q4/Q5. Duplicates of the corpus by target (Scopus): records.jsonl 237, v2 screening batches 596, v2 rescue queue 1,298, v2 other (not queued) 23, title-resolved queue 0 (file empty at run time).

## All databases in the final files

Rows 6,543: Scopus 4,046, WoS 2,267, IEEE slice 230. Unique records 3,895 (3,643 documents plus 252 proceedings front-matter records).

| step (PRISMA) | n |
|---|---|
| records identified | 6,543 |
| proceedings front matter, not documents | 302 rows (252 records) |
| duplicates within a file | 7 |
| duplicates within a database | 574 |
| duplicates across databases | 2,017 (WoS 1,902, IEEE 115) |
| duplicates of the existing corpus | 2,251: records.jsonl 250, v2 screening batches 619, v2 rescue queue 1,353, v2 other 29 |
| new unique records | 1,392 (Scopus 1,010, WoS 277, IEEE 105) |
| excluded by the string filter S1''/S2'' (title + abstract) | 1,222 |
| passed to screening (subscription-queue) | 170 (Scopus 157, WoS 13, IEEE 0) |

Corpus duplicates by kind (unique records): DOI 1,702, exact normalised title 529, letters-and-digits title 7, token-set Jaccard >= 0.85 nine, abstract hash 4. Queue: tier T1 86, T2 6, T3 70, T4 8; 167 pass S1''/S2'', 3 pass only the original S1 or S2 (released as in D0028); none lacks an abstract.

Per-query counts for WoS and the IEEE slice are in the summary JSON (`per_db_query`).

## Spot checks of 15 dedup decisions, by eye

Seeded draw (20261015) from the corpus-duplicate records, stratified by rule. All 15 are the same work as their target.

1. DOI: cello emotion recognition (2026) = M14255.
2. DOI: Weak convergence for Markov processes on discrete state spaces = M19215 (2024 vs 2025 in the target).
3. DOI: AI-driven text-to-multimedia content generation (I-SMAC 2024) = M12346.
4. DOI: Pix2Video (ICCV 2023) = M01212.
5. Exact title: DiffUTE = M01383.
6. Exact title: Text-guided molecule generation with a diffusion language model (AAAI 2024) = R0098.
7. Exact title: Benchmarking diffusion models for machine translation = R1430.
8. Exact title: Bit-diffusion universal segmentation (2026) = M07727.
9. Exact title: Ensuring consistency for in-image translation (Mathematics 2026) = M04453 (2024 arXiv); journal version of the same title, two-year gap accepted.
10. Letters-and-digits: "D3 ToM" = "D$^{3}$ToM" (M07267).
11. Letters-and-digits: upper-case, hyphen-broken "BLOCK DIFFUSION ... AU-TOREGRESSIVE" = R0214.
12. Jaccard 0.909: SIR disaster-response paper (journal title adds "for resilient communities") = M01738; same paper.
13. Jaccard 0.875: "The role of interactional and cognitive mechanisms in the evolution of (proto)language(s)" (Lingua) = M15513, whose DOI is a PsyArXiv/OSF preprint; same paper, off topic either way.
14. Abstract hash: "Vision-Language Feature-Based Multimodal Semantic Communication System" = M07252 (VLF-MSC), same abstract.
15. Abstract hash: One-DM (2025) = M03695 (title without the acronym).

No false match found. Further checks over everything: all 9 Jaccard and 4 abstract matches read; the 13 DOI matches with the lowest title similarity (truncated, translated or re-titled versions) are the same record under one DOI; 141 title matches where the two DOIs differ were compared and all but 10 differ only as arXiv DOI against publisher DOI; the 10 others (journal against SSRN or repository preprint, translation, an IJCAI year typo, a book chapter reprint of a journal article, two EMNLP-2022 DOIs for one title, mis-keyed in the target) are the same work or off-topic. One title-only match was refused for a four-year gap (see decision 2) and stays a new record. Cross-database merges (WoS, IEEE against Scopus) differ only by case, spacing, "++" spelt "plus plus", ligatures and "RETRACTED:" prefixes; five DOI pairs inside one merged record are the same paper (preprint or proceedings DOI beside the journal DOI).

Uncertain: nothing that affects an in-scope record.

## Decisions I made, and why

1. **Proceedings front matter is not queued.** 302 Scopus "Conference review" rows (252 records) have no authors and an abstract that lists the titles of the whole volume ("The proceedings contain N papers..."). 89 of the 252 would pass S1''/S2'' only because some listed title contains a diffusion-language phrase. They are not documents. Kept in the records file with `proceedings_volume: true` and `volume_abstract_matches_S1pp_S2pp`; reversible by dropping the flag test in `main()`.
2. **Title-only matches need years within 3 of each other** (both known); DOI and arXiv-id matches do not. Reason: a false duplicate loses a paper, a missed duplicate costs one extra screening. One match refused (a statistics paper, 2025 against 2021, off topic).
3. **A match to a title-only snowball record does not count as a duplicate.** The 2,107 snowball records excluded on the title alone (D0029; no abstract, never tested against the strings) are never screened on content; a database record with a real abstract is kept as new. Nine new records match one (three of the 9 are queued); the title-resolution run may also produce them, so screen the subscription record and drop the other.
4. **Queue rule = D0027 + D0028 on title + abstract**: pass S1''/S2'', or match the original S1 or S2. Keywords are not used, as for the free sources. For information only: 17 records that fail the rule match the original S1 or S2 once author keywords are added, 22 with index keywords (`string_match_with_keywords`); Scopus searched keywords, so the orchestrator may want these 17 released.
5. **Abstract cleaning**: publisher copyright footers stripped (3,000+ rows; Scopus ends nearly every abstract with one), "[No abstract available]" emptied (5 Scopus rows, 0 queued). The string tests use all distinct abstracts of a merged record, so a shorter abstract in one database cannot hide a hit seen in another.
6. **Duplicates whose corpus target has no abstract** while this record has one and passes the strings (75: 36 against the rescue queue, 28 against screening batches, 11 against records.jsonl) are not queued; they are flagged `dup_gains_abstract` in the records file so the orchestrator can decide whether to re-screen them on content. One duplicate of an auto-excluded v2 record passes S1''/S2'' here (`dup_target_auto_excluded_but_passes`).
7. **Ids** `U#####` stay stable through the previous records file; `first_seen_run` marks when a record entered; a rerun writes a delta queue.
8. **No network lookups were needed** (all Scopus, WoS and IEEE rows carry abstracts); SpringerLink abstracts will be fetched by DOI (Crossref, then Semantic Scholar; 1 s and 2 s gaps; cache `research/sources/search-raw/_ingest-cache/doi-abstracts.jsonl`; definitive misses cached, transient errors retried next run) only for new records with no abstract.
9. **WoS RIS quirk**: the export loses some line breaks and glues the next tag to the previous value (`...USAC3  - ...`, `...(CPCI-S)AN  - WOS:...`); the parser splits before known tags, and `AN` becomes the WoS accession number.

## Concerns

- `screening/v2/title-resolved-queue.jsonl` was empty at run time (title resolution still running), so the check against it ran on nothing. Rerun the command once that file is filled. The title-resolved queue is not checked against the subscription queue by its own tool: screen duplicates once.
- IEEE: only the 2021-2024 slice of query I1 exists (230 of 1,203). The row-count check will show a warning until every slice is present; other queries (I2-I5) not yet exported.
- The queue contains the same noise the free-source queue has (for example "diffusion LMS" signal-processing papers pass part A1 through `diffusion lm*`); I applied S1''/S2'' as written in D0027 and did not change it.
- The 1,222 new records that fail S1''/S2'' are auto-excluded; D0029's rescue pass has not been run on them.
- `search-log.jsonl` was appended by 9 rows while exports were arriving; the WoS and IEEE rows are correct for their files. Nothing was committed.

## Not searched or not verified

SpringerLink, ACM DL and ScienceDirect exports do not exist yet; their parsers and the Springer abstract fetch are untested on real data. WoS plain-text and tab-delimited export formats were tested on a fixture only (the real WoS export was RIS).
