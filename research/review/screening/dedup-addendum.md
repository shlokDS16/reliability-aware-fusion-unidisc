# Dedup addendum (2026-10-14)

Found after screening, by exact match of normalised abstracts and by the screeners' notes. The
records keep their sids; at full-text screening the later record of each pair is coded X5
(duplicate) once the full texts confirm it.

| Pair | arXiv IDs | How found |
|---|---|---|
| R0117 / R0831 | 2405.06535 / 2604.05730 | identical normalised abstract |
| R0713 / R0931 | 2602.16169 / 2605.12836 | identical normalised abstract; screener A note |
| R0343 / R0600 | see records.jsonl | screener A note (abstracts identical by reading; not by exact hash) |

Fix for the next run of `tools/build_screening_set.py`: add a third dedup key on the normalised
abstract.
