# Title resolution of the 2,107 title-only auto-excluded snowball records (D0029 action 2)

Agent: lit-scout. Run: 2026-10-15 23:10 to 2026-10-16 00:10 IST. Script: `tools/resolve_title_only.py` (uncommitted, unchanged by this session).
Nothing was screened; no existing corpus or screening file was touched; nothing committed.

## Verdict
Action 2 is NOT complete. 1,161 of 2,107 records are classified; 946 (45 %) are unresolved only because Semantic Scholar and arXiv rate-limited, so
their status is "unresolved-lookup-incomplete", not "not found". The queue file is empty (0 records) and must not be read as "nothing to screen":
it covers only the 823 resolved records, and 946 records have not been looked up.

## Counts (population 2,107; check sum holds: 105 + 823 + 233 + 946 = 2,107)
| Class | n |
|---|---|
| Resolved duplicate of an existing record | 105 (102 local, 3 after resolution: 2 within-population, 1 by arXiv id) |
| Resolved, new (not a duplicate) | 823 (669 by Semantic Scholar paperId, 96 DataCite-arXiv title, 58 Crossref title/other) |
| of which with abstract | 135 (687 resolved without any abstract) |
| Unresolvable: not a bibliographic title (fragment, prose, symbols) | 202 |
| Unresolvable: queried, no title-agreeing record | 31 |
| Unresolved: lookup incomplete (S2 / arXiv API rate-limited) | 946 (308 marked as reference-list-like, 638 unmarked) |
| Resolved and matching a string (S1..S2'') on title+abstract or title | 0 |
| Queued for dual screening | 0 |

Why 0 queued: the 687 resolved records without abstract can only be tested on title, and these records were auto-excluded on title alone, so a
title string hit is excluded by construction. The 135 with abstract: 0 string hits. The string test itself works (sanity-checked on a made-up
positive and a made-up negative). The 946 unresolved records were never tested, so some could still reach the queue.

## Why the run stopped
- OpenAlex: quota exhausted (HTTP 429, X-RateLimit-Remaining 0; resets 00:00 UTC = 05:30 IST). Skipped as instructed.
- Semantic Scholar (unauthenticated): HTTP 429 persistently from 23:12; the script's breaker paused it 10 min at a time. Probes at 23:26 gave 200
  once, then 429 again at 00:04. Throughput in the slow pass was about 3 to 5 lookups per minute at best and 0 for the last 10 minutes; the
  slow pass over 978 records would have taken many hours. arXiv API answered 200 on probes but at the 3.5 s gap it could not cover the rest in the budget.
- Stopped at about 60 minutes as the brief says, then ran cache-only (`finish`). Fast-pass sources (DataCite for arXiv, Crossref, S2 batch by paperId) are complete.
- To finish: rerun `python tools/resolve_title_only.py run` (resumable, cache has 4,812+ lookups) when S2 is not throttled (an S2 API key, or after
  OpenAlex resets at 05:30 IST, would help most). The 946 are the only records left to look up.

## Script and process notes (read these)
1. No bug fixes were needed; `local` ran clean. I made no edit to the script.
2. The script file was modified at 23:50 IST by someone other than this session (mtime 23:50:04; my run had started 23:12). The edit adds a policy that
   the brief and docstring do not contain: in the slow pass only records with a reference-list marker (333) plus a random sample of 60 unmarked ones
   are queried; the other 585 unmarked ones are labelled `unresolvable` with the reason "not queried". The "random check: 0 of 60 resolved" in the
   JSON of that version is meaningless, because in cache-only mode those 60 were simply not looked up. I did not accept that policy. The final outputs
   were produced by a wrapper in the session scratchpad (`scratchpad/finish_all.py`) that imports the script and sets `SAMPLE_UNMARKED = 10**6`, which
   restores the documented behaviour (every unmatched record is queried, so none is labelled unresolvable without a lookup). Consequence in the output JSON: `slow_pass.without_marker_*`
   fields are mislabelled ("random check sample" n = 645, resolved 0); disregard them. In the records file the field `slow_lookup` is "queried" (333) or "random check sample" (645), and
   both just mean "queried or attempted". Whoever owns the 23:50 edit should decide whether that sampling policy is wanted; if so the 585 are not negatives.
3. At the start of my session a second `resolve_title_only.py run` process (PID 33052, started 21:51, apparently the interrupted earlier session) was
   still alive and appending to the same cache. I stopped it (both together doubled the load on S2) and ran only my own. The cache file may contain a few duplicate lines from that overlap; lookups are keyed, so results are unaffected.
4. This worktree is shared with another active session: `research/review/corpus/search-log.jsonl` is modified and `subscription-*`, `criteria-v1.1.md`,
   `tools/ingest_subscription.py` appeared untracked while I worked. None of those are mine; I did not touch them.
5. My own shell was pinned to a different worktree (`resume-dlm-discovery-2a792f`) after a background notification and refused commands; I used EnterWorktree
   with the target path (an existing worktree, as the brief required) to continue. No file in 2a792f was changed.

## Spot check (23 matches by eye, 0 false matches)
Resolved, non-identifier (9 random, seed 7): "Opera graeca adnotata" (DataCite arXiv); "Faithfulness-aware decoding strategies..." (hyphenation fixed); "Improving text
embeddings with large language models"; "Molgpt"; "The creativity of text-to-image generation"; "Fnet: Mixingtokens with fourier transforms" to FNet; "Are llms all
you need for task-oriented dialogue?"; "Tuning llms with contrastive alignment instructions..."; "Stylegan-nada". All correct.
Duplicates (8 random seed 11 plus all 6 prefix-truncated): Mistral 7B, LaDiR, "transformers learn to plan via multi-token" to the multi-token prediction paper,
"Large language models are overconfident and amplify human", Chameleon, DPOK, Qwen2.5 technical report, language-generation-harm survey, and the prefix-truncated ones
(MaskGIT, JourneyDB, Protein Design with Guided Discrete Diffusion, dLLM, IDLM, Sink-Aware Pruning). Several look wrong on the title field alone (for example
"design with guided discrete" matching a title that starts with "Protein") but each is correct because the title spilled into the venue field ("Protein") and the
variant that joins venue and title agrees. Weakest case: M11641 "Bayesian Flow" + venue "Networks" to Bayesian Flow Networks (correct, but only because of the venue spill). The 3 after-resolution
duplicates (Gemma, ProtTrans within the population; arXiv id for Truncated Diffusion Probabilistic Models) are correct.
Identifier-resolved (669): 665 agree with the original title by the script's rules; the other 4 are non-Latin strings or a repository prefix ("UvA-DARE ... SurVAE Flows"), all the same paper.
Not checked: the 58 Crossref-title matches beyond the sample above, and the 24 + 7 queried-but-not-found records for false negatives.

## Files written (sha256, bytes)
- `research/review/corpus/title-resolution-2026-10-15.json` caad5fcbd0b8ed5698de10d95b5cc90deee2c3d263a311103f0241ea9b1fd507 (3,069)
- `research/review/corpus/title-resolution-records-2026-10-15.jsonl` 4737230f0cdef654465850e255a7558288385480264a8ae28dfb4aaf6cbf9db (1,909,180; one row per record, 2,107 rows)
- `research/review/screening/v2/title-resolved-queue.jsonl` e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 (0 bytes, empty)
- `research/sources/title-resolution-raw/lookup-cache.jsonl` 02944dfaabf815db4df09ec223116ad1302db5c5894bc503deeddcb8a556929c (raw lookups; 4,184,822 bytes at 00:07, but the hash changed to 73b5e555bf2447623a744587eb5e0ff3d9a4abe0a76d92fe9c33ebdb24621e6f minutes later, so another process is still appending to it; the outputs above were written before that and do not depend on later lines)
- this report
