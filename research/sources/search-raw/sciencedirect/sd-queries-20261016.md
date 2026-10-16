# ScienceDirect queries 2026-10-16 (user's Chrome, D0031)

Field Title, abstract or author-specified keywords (tak=), years 2021-2026. Strings: sd_queries_20261016.py
(23 runs; page sha256 equalled the script for all 23).

Platform facts found today (they replace the sheet's [unverified] notes):
- 'Use fewer boolean connectors (max 8 per field)': a 9-connector string and the sheet's S2p-M-r1
  (11 connectors) were refused. The sheet's ScienceDirect runs are therefore not usable as written.
- "Wildcards '*' are not supported" (diffusion AND llm* refused).
- Plurals are matched automatically: "discrete diffusion" 39 = "discrete diffusions" 39;
  diffusion AND llm 131 = diffusion AND llms 131 (about 09:55 IST).

Counts: not read. After about 15 rapid page loads ScienceDirect answered 'There was a problem providing the
content you requested' (reference CPE00002, 2026-10-16 03:59 UTC) to automated loads from the campus IP.
Automation was stopped at once to protect the institution's access. Next: run the 23 strings slowly
(about one per minute) or by hand in the advanced-search form, with the user present.

## Exports (user, by hand from sd-download-links.html, 2026-10-16 ~14:15-15:00 IST)

ScienceDirect's export holds one result page (default 25; the user then set 100 per page). Files of exactly 100
records may be the first page of a larger run; byte-identical files are re-exports (dedup drops them). Some runs
returned no results. Which run each file came from is not recorded in the file (RIS carries no query);
records are attributed to ScienceDirect, not to a run.

| File | records | sha256 |
|---|---|---|
| ScienceDirect_citations_1792140421402.ris | 10 | 9fa98f1f0f7d80df3aaa4a6faa2ab0e9b7f28474983f7fa817a9d097df10bf64 |
| ScienceDirect_citations_1792140439189.ris | 25 | 03972d3d365fc8a858a3cc58fd18c26c5039ca331895efa67bd2586e3f752a1b |
| ScienceDirect_citations_1792140456756.ris | 25 | 6ad82469459ae748e4b853899e851cd4419a102d815cb0229d0745ac9a42dcd0 |
| ScienceDirect_citations_1792140469226.ris | 2 | eff91cfb1d2f23519b64ef60d1f4378f5d7deb6a69abe8132567a05f1cdc9bf6 |
| ScienceDirect_citations_1792140485149.ris | 25 | 05410d6b7d5decb6e97984d8ed89ec2a60e2a6abc7a0f5e323d6fdad9b161403 |
| ScienceDirect_citations_1792140501642.ris | 25 | 4bb953458c28536f4fc0e5a5f0a336b973d55bacf0a89660ac6e7c6c044ee54a |
| ScienceDirect_citations_1792140517375.ris | 25 | 16937f5768b69b9164e0c4ffa631861b7c9d09adeb151bacb8b8daf2e60f8966 |
| ScienceDirect_citations_1792140787524.ris | 100 | 942f2e627c94dca6f10cd7c9053cc98694b5e5de52216ff10717d1a442d92f54 |
| ScienceDirect_citations_1792140835921.ris | 10 | 9fa98f1f0f7d80df3aaa4a6faa2ab0e9b7f28474983f7fa817a9d097df10bf64 |
| ScienceDirect_citations_1792140869785.ris | 37 | 9eefb7e42c9f7c5264deca4d5070df3e5bc0357aa9d6cb46e1fae9cded17033c |
| ScienceDirect_citations_1792140889983.ris | 100 | 11bc15e046ace31fd21dfc4977ade2b101973dc9a8810aef9b8f85838c06827e |
| ScienceDirect_citations_1792140916695.ris | 2 | eff91cfb1d2f23519b64ef60d1f4378f5d7deb6a69abe8132567a05f1cdc9bf6 |
| ScienceDirect_citations_1792140944287.ris | 100 | fab039894a9e778b426448f380581ed9d2a48175bc241b9c92f0772d5b997b6f |
| ScienceDirect_citations_1792140973482.ris | 100 | fab039894a9e778b426448f380581ed9d2a48175bc241b9c92f0772d5b997b6f |
| ScienceDirect_citations_1792141076289.ris | 52 | 210814457c5e3921b180600bd8c1ed58a5398fe38779caca27122402aa6582a8 |
| ScienceDirect_citations_1792141110021.ris | 100 | 823892dd22f6dbd4fd76bf56e9dd8b15d08ad16aea9850118527ab2a00a55527 |
| ScienceDirect_citations_1792141132501.ris | 100 | 942f2e627c94dca6f10cd7c9053cc98694b5e5de52216ff10717d1a442d92f54 |
| ScienceDirect_citations_1792141190382.ris | 100 | f2c8c4b1c838668cb3a0cb42302fb0b57a5f0e0f900e569dce5b4d12ca6b33e0 |
| ScienceDirect_citations_1792141253230.ris | 9 | cc902e7c8a97bd8db324e9f967031f01347af157aa04e3af49953b7754743125 |
| ScienceDirect_citations_1792141273095.ris | 9 | cc902e7c8a97bd8db324e9f967031f01347af157aa04e3af49953b7754743125 |
| ScienceDirect_citations_1792141292717.ris | 1 | cd2434d256a9be494806943cd682e7bb0bdbe42fd8826710ca2a4a32ca0d98fa |
| ScienceDirect_citations_1792141358643.ris | 2 | b3b70b8715b3643f7dd23f51baf335a0b2c61deb3e6f73683e50c5405bd1a715 |

## Removed from the working tree 2026-10-16 (user's instruction; still in git history, commit d7c7676)

- ScienceDirect_citations_1792140439189.ris: 25-record first-page export, redone at 100 per page by the user
- ScienceDirect_citations_1792140456756.ris: 25-record first-page export, redone at 100 per page by the user
- ScienceDirect_citations_1792140485149.ris: 25-record first-page export, redone at 100 per page by the user
- ScienceDirect_citations_1792140501642.ris: 25-record first-page export, redone at 100 per page by the user
- ScienceDirect_citations_1792140517375.ris: 25-record first-page export, redone at 100 per page by the user
- ScienceDirect_citations_1792140835921.ris: byte-identical duplicate of ScienceDirect_citations_1792140421402.ris
- ScienceDirect_citations_1792140916695.ris: byte-identical duplicate of ScienceDirect_citations_1792140469226.ris
- ScienceDirect_citations_1792140973482.ris: byte-identical duplicate of ScienceDirect_citations_1792140944287.ris
- ScienceDirect_citations_1792141132501.ris: byte-identical duplicate of ScienceDirect_citations_1792140787524.ris
- ScienceDirect_citations_1792141273095.ris: byte-identical duplicate of ScienceDirect_citations_1792141253230.ris
