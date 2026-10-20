# For you tonight (20 Oct 2026, after dinner): Paper 1 build

Session 0839c9f4 is building the manuscript under your D0051 (screening frozen, finish by Thursday 22 Oct).
Reply with item numbers, for example "P1 A, P2 ok, P3 ok".

**P1 needs your own answer, in this session.** The starting session relayed your 17:30 "go with your recommended
decision" for P1, but a decision that changes D0051's scope is recorded only on your own words. Option A is fully
prepared (seed draw of 20 done, texts copied, 11 sessions batched; `analysis/extraction/d0052/seed-sample.json`) and
nothing has been dispatched. The update strata (positions 1-20) run in the meantime; they are needed under A and C.

## Decisions (only you can make these)

| # | Decision | Options | Recommended | Time |
|---|---|---|---|---|
| P1 | **The 615 included studies contain none of the field's core papers.** LLaDA (R0205), MDLM (R0128), Dream 7B (R0350) and MMaDA (R0246) are in the seed tranche S1243 (1,242 records that passed title/abstract), which D0051 left unscreened. The 615 come from the search update (596), the subscription databases (13) and the re-check (6). A referee will very likely call this fatal for a review of diffusion language models. | **A** add a seed stratum of 20 to the extraction sample, drawn at random from the census sample's 167 full-text-eligible seed records (themselves a random sample of the seed pool; texts already on disk, no screening, no download); update strata cut from 27 to 20 each, total 80; seed-strand RQ1 counts estimated from the census sample with weights; disclosed. **B** lift the freeze and screen S1243 at full text (about 35 hours of screening, about 50 percent of a week's usage, about 940 downloads): misses Thursday. **C** keep D0051 as it is and state it as a major limitation. | **A** | 2 min |
| P2 | **Extraction sample (D0052), applied under your "go with the recommended decision"; please confirm.** draw_pilot.py gate draw, 27 per stratum (unified multimodal 53, shorter text 272, longer text 271), 81 records; one extractor (Opus 5.5), second extractor (Sonnet 5.5) on 8 with Fable adjudicating those 8; the 7 R797 includes and the 12 non-language includes get RQ1 counts only; quality appraisal (QA1-QA9) on the 81 only. Your professor asked for a quality table covering every included study: this is a disclosed shortfall. | ok / change | **ok** | 1 min |
| P3 | **Fix to the PRISMA counts, FYI.** analysis/prisma/prisma_flow.py took the 15 Oct arXiv rerun (1,286 and 190) as the seed search; the seed search of 14 Oct retrieved 1,158 and 173 (1,903 with the list, minus 450 duplicates = 1,453). Fixed and asserted. | ok | **ok** | 0 min |

## Hands-on (each sheet has a "Start here" tab)

1. **4 papers screener B could not read (D0041, D0046)**: `research/review/screening/human-p4/human-p4-sheet.xlsx` (M13184,
   M15873, M17195) and `research/review/screening/human-p4/human-p4-sheet-R0308.xlsx` (R0308). Blind: do not open any
   screener file for them first. About 15 minutes.
2. **9 field choices (D0039)**: `research/review/screening/d0039-fields/d0039-fields-sheet.xlsx`. A and B agreed on the
   decision but not on one field (code, I1 basis or non-language flag); pick the value. About 15 minutes.
3. **Author details**: the second author's name, school, e-mail; ORCIDs for both; who is corresponding. The manuscript
   has an [AUTHOR] placeholder (paper/review/main.tex).
4. **Which human checked what** (for the AI-use table, Section 2.8): one line, e.g. "Shlok read the T1 validation
   sample; both authors read the final manuscript".
5. **Final read-through** of the PDF on Thursday morning (I will send the path).

## Status (updated by the session)

- 19:00: extraction sample drawn (D0052); RQ1 counts for all 615; PRISMA figure rebuilt; method section rewritten
  for the current state (it described 15 Oct); first two extraction sessions running (RAM was below 5 GB until 19:50).
