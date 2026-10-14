```yaml
agent: general-purpose (acting as screener A, continuation instance)
date: 2026-10-14
brief: Title-and-abstract screening of batches 12-15 (R1101-R1453) with criteria-v1.md, following screener-A/notes.md rules, blind to screener B.
sources_examined: [research/review/screening/criteria-v1.md, research/review/screening/screener-A/notes.md, research/review/screening/screener-A/batch-01.jsonl, research/review/screening/screener-A/batch-05.jsonl, research/review/screening/batches/batch-01.jsonl, research/review/screening/batches/batch-05.jsonl, research/review/screening/batches/batch-12.jsonl .. batch-15.jsonl]
coverage: all 353 records of batches 12-15 screened from title and abstract (abstracts read up to the first 1300 characters; the remainder was read for 10 borderline records). Nothing under screener-B/ or any other file was opened. No ledger writes; notes.md and earlier outputs not edited.
claims: []
competing_explanations: []
unknowns: [decisions for records with no abstract (R1424-R1453) rest on titles only]
next_test: {hypothesis: n/a, intervention: n/a, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

## Counts (353 records)

| Batch | records | include | exclude | unclear |
|---|---|---|---|---|
| 12 | 100 | 78 | 13 | 9 |
| 13 | 100 | 75 | 11 | 14 |
| 14 | 100 | 80 | 9 | 11 |
| 15 | 53 | 21 | 13 | 19 |
| Total | 353 | 254 | 46 | 53 |

Exclusion codes: X0 = 4, X1 = 19, X2 = 9, X3 = 14, X4 = 0, X7 = 0, X8 = 0. Checks run by the writer script before each file was written: one line per batch sid in batch order; every exclude has a code and no include or unclear has one; every reason is at most 15 words. Every decision was made by reading the record; the script only converted my decision lines to JSONL.

## Rules applied (continuing notes.md rules 1 to 8; new or sharpened points only)

1. **Missing abstracts (R1424 to R1453, 30 records, all in batch 15).** All have an empty abstract, a class that did not occur in batches 01 and 05, so notes.md gives no precedent. Following the criteria text ("abstract is missing"), records whose title suggests a primary study or software were marked unclear (19 records: R1424, R1425, R1430, R1431, R1432, R1435, R1436, R1437, R1438, R1439, R1440, R1442, R1444, R1445, R1447, R1448, R1450, R1451, R1453). Records whose title alone names a survey, overview, explainer or a curated paper list ("awesome", "papers", "survey" repositories) were excluded X3 (11 records: R1426, R1427, R1428, R1429, R1433, R1434, R1441, R1443, R1446, R1449, R1452). The X3 call for GitHub list titles and for R1434 (explainer) rests on the title only; a screener could code these X4 or unclear instead.
2. **Rule 1 (X1 versus X2) kept.** Text-conditioned non-text output coded X2: R1103, R1117, R1142, R1173, R1174, R1192, R1364, R1403, R1368 (video-action generated under language conditioning). Output with no text input mentioned coded X1.
3. **Rule 3 (unified model) applied.** Included when the abstract presents unified understanding and generation with a diffusion or flow component: R1106, R1154, R1184, R1242, R1291, R1342, R1349, R1351, R1389, R1422. Marked unclear when the unified framing or the diffusion link is weak: R1129 (MLLM reward model for text-to-image RL), R1144 (attack on unified editing models), R1254 (frozen DLM understanding module plus image DiT, generation only), R1387 (any-to-any latent flow).
4. **Rule 5 (theory papers) applied.** Discrete-diffusion theory with no text stated: unclear (R1122, R1222, R1236, R1283, R1286, R1359, R1379, R1392). Theory that names diffusion LMs or reports a language experiment: include (R1109, R1128, R1188, R1263, R1282).
5. **Rule 6 and 8 applied.** Molecule models framed as language models: unclear (R1121, R1318). Semantic-ID recommendation: unclear (R1152, R1230, R1253). Robot or driving action models on diffusion LM backbones: unclear (R1127, R1178); R1266 and R1291 were included because the abstracts state language-token or understanding-and-generation outputs.
6. **Rule 7 applied.** Classification, extraction or label-scoring uses of diffusion LMs: unclear (R1215, R1252, R1314). R1381 (generative retrieval producing document identifiers) unclear for the same reason.
7. **Evaluation on non-text data only.** Generic discrete-diffusion methods whose abstract reports only DNA, protein or molecule benchmarks were excluded X1 (R1240, R1371, R1391), although the abstracts say such models work on text. This is a judgement call; a screener could mark them unclear.
8. **Non-diffusion models.** Coded X0: R1166 (decoder-only any-to-any), R1202 (VLM hallucination), R1393 (edit-chain causal model), R1396 (count-based masked-text predictor). R1158 (MLLM plus next-scale AR image decoder) coded X1 because its outputs are images only. R1399 (VQ coarse-to-fine text generation compared with DLMs) was left unclear because parallel prediction of codes may be a masked-generative component.
9. **Application records.** Records that adapt a diffusion LM to a domain and report model-level comparisons with AR models were included (R1111 radiology, R1233 radiology reports, R1300 counselling, R1181 change captioning). No record was coded X7.
10. **Non-natural structured sequences.** Chess puzzles (R1341) and passwords (R1347) with masked diffusion were marked unclear; Sokoban grids (R1218) and travel diaries (R1408) were coded X1 because the abstracts do not frame them as text or language models.

## Ambiguities met (criteria text not changed)

- I1 does not say whether speech-token or codec-token "diffusion language models" for TTS (R1117, R1174, R1364) count; they were coded X2 under rule 1, which treats them as text-conditioned non-text output.
- ASR with a discrete-diffusion LM (R1131) was included because the output is a transcript, as in notes.md rule 7.
- The criteria give no instruction for records with an empty abstract; see rule 1 above.
- Several included records study diffusion LMs only as one of several model families (R1168 was marked unclear for this reason; R1407 and R1313 were included because diffusion LMs are a stated evaluation target).
- Records with "diffusion-inspired" or denoising framing (R1415, R1224): R1415 included (code LM with denoising framing), R1224 unclear.

## Concerns

- The unclear rate in batch 15 (19 of 53) is driven entirely by the 30 empty-abstract records.
- Judgement calls under points 3, 4, 6 and 7 are the most likely places for disagreement with screener B.
