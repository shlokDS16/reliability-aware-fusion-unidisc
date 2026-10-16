# SpringerLink queries run 2026-10-16 (user's Chrome, D0031)

Platform: link.springer.com advanced search, date range 2021-2026, all content types, sorted by relevance.
Strings from springer_queries_20261016.py (this folder); the sha256 computed in the page equalled the
script output for every string. NOT clauses dropped, as in the sheet's SpringerLink section (excluded
topics go out at screening).

Run A (primary): Title field. Run B (supplementary sample): Keywords box, which SpringerLink matches in
the full text; the export cap is 1,000 per search, so Run B is reported as a sample, not a complete search.
Counts read about 09:40 IST with in-page requests to the same search URL.

| Query | Parts of the sheet | chars | sha256 (first 12) | Run A title | Run B keywords |
|---|---|---|---|---|---|
| S1 | S1p-A1 (all names) | 752 | 62859a742fa5 | 17 | 757 |
| S2 | S1p-A2-r3 (superset of r1, r2) | 136 | 04766f7ce8b0 | 44 | 1,944 |
| S3 | S1p-A3-r1..r4 | 305 | f22ca3b62191 | 10 | 10,548 |
| S4 | S1p-B-r1..r4 | 513 | 20d0c4f99b35 | 26 | 25,376 |
| S5 | S1p-C | 63 | 70e7bd13ed8c | 19 | 9,200 |
| S6 | S2p-M-r1, r2 | 501 | e9d71f649a46 | 2 | 659 |
| S7 | S2p-VLA-r1, r2 | 238 | c2a75f981c34 | 3 | 92 |
| U | union S1 OR ... OR S7 | 2,532 | f391096f6a14 | 106 | not read (throttled) |

Sum of Run A part counts 121; union 106 (overlaps).

In-page requests for S6, S7 and U in the Keywords box returned a 3 KB loading page (throttling or a
client-side render); S6 and S7 were read by loading the search page in the tab (about 09:50 IST).

Export plan (needs the user's yes per file): Run A union U (106, title field, complete). Run B complete
where under the 1,000 cap: S1 (757), S6 (659), S7 (92); S2 (1,944) as the top 1,000 by relevance
(a sample). S3, S4 and S5 in the Keywords box (10,548, 25,376 and 9,200 full-text matches) are not
exported: their title-field forms are in Run A, and a relevance-ranked 1,000 of a full-text match set is
not a usable sample.

## Files (user approved all five exports, 2026-10-16)

Run A was saved from the tab (in-page fetch of /search/csv after the user signed in to a Springer Nature
account; CSV export requires a login). Chrome then silently refused further script-made saves from the
site, so the user downloaded the four Run B CSVs with the site's own "Download results (.csv)" button from
springer-download-links.html (this folder) about 10:14-10:15 IST; renamed here by row count and order.

| File | data rows | bytes | sha256 |
|---|---|---|---|
| springerlink-runA-title-union-20261016.csv | 106 | 31,449 | a2866d4a7f71d75551e3cf10a11232e4a89f27441f41e439d5aec4a4e68040a6 |
| springerlink-runB-kw-S1-20261016.csv | 757 | 224,564 | 89702203cbed74bd9ab1e29e07017aead68a65b65d929734115f462f51e270ac |
| springerlink-runB-kw-S6-20261016.csv | 659 | 198,726 | c6ccf8c4be7a49a121dc18bfe1bd521748caf0a52360f08e05c5968e8402b953 |
| springerlink-runB-kw-S7-20261016.csv | 92 | 29,710 | 9be39a988ab87e6b86c560e8cf99b8d601ca48447ca92eedf665e4960ff64a6c |
| springerlink-runB-kw-S2-top1000-20261016.csv | 1,000 (of 1,944; sample) | 290,696 | ab95c7a1d442551354142b1e752a148a03992654f3b54bcedc37df3d7b3153d7 |

SpringerLink CSVs carry no abstracts; tools/ingest_subscription.py fetches them by DOI.
