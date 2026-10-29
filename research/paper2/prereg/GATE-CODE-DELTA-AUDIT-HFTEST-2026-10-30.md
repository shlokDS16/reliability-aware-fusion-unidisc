# Gate-auditor code delta audit: HF-scorer offline test, pin 1871fe7d -> 84be25c4 (2026-10-30)

Auditor: gate-auditor (CPU only, no network, nothing committed; the auditor fixed nothing). Card: `research/paper2/prereg/PREREG-GATE-v4-2026-10-28.md` section 9, row A-8.
Worktree HEAD at audit: 69fc2755 (tracked files under exp_p2, tools, analysis, analysis_posthoc, tests clean).

## Verdict: PASS (no fixes required; one wording note for the card, item 5)

## 1. Diff is test-only (met)
- `git diff --stat 1871fe7d 84be25c4 -- exp_p2 tools tests analysis analysis_posthoc`: one file, `tests/exp_p2/test_gate_a6_r1.py`, 5 insertions, 0 deletions.
- `git log 1871fe7d..84be25c4 -- exp_p2 tools analysis analysis_posthoc tests` lists only 84be25c4. `git diff --quiet 1871fe7d HEAD -- exp_p2 tools analysis analysis_posthoc` returns 0 (production code byte-identical at HEAD 69fc2755 too).
- The five lines (test lines 264-268): a comment, `import transformers.utils.hub as th`, and a loop that does `monkeypatch.setattr(th, name, str(hub), raising=False)` for `TRANSFORMERS_CACHE`, `PYTORCH_TRANSFORMERS_CACHE`, `PYTORCH_PRETRAINED_BERT_CACHE`. monkeypatch restores them at teardown. No production import path is touched.
- Mechanism confirmed in the venv: `transformers/utils/hub.py` lines 95-97 set the three globals at import (from `constants.HF_HUB_CACHE`), and line 322 uses `cache_dir = TRANSFORMERS_CACHE` when none is passed.

## 2. The test still asserts what it was written for (met; one caveat stated)
Assertions unchanged (test lines 275-277): `pytest.raises(BL.WeightsNotCached)` on `BL.HFScorer("clip")`; the socket-connect guard raises `AssertionError("network access attempted")`; no `*.json` appears in the empty tmp hub. The change only makes the empty cache the cache that transformers actually looks in.

Scratch copy (tests, exp_p2, tools, analysis/paper2/lrf copied into the session scratchpad `...\scratchpad\mut`; repo untouched; the test imports `analysis/paper2/lrf/baselines.py` from ROOT = the scratch tree, so the mutations are live). Production reference: `baselines.py` lines 146-155 (`force_offline`), 165 (call), 169 (`local_files_only=not download_approved`), 173-174 (`WeightsNotCached`).

| Scratch variant | Result |
|---|---|
| M0 unmutated production, new test | passed |
| M1 `force_offline()` call removed (line 165), `local_files_only` kept | passed |
| M2 `local_files_only=False`, `force_offline()` kept | passed |
| M3 both removed (scratch) | FAILED: `AssertionError: network access attempted` |
| M4 unmutated production, old test (from 1871fe7d) | FAILED: `DID NOT RAISE WeightsNotCached` (confirms the A-8 failure and that the 5 lines are what cure it) |

Reading: the two guards in `HFScorer` are redundant defences (either one alone keeps the process off the Hub when the cache is empty). The test detects the loss of both together, not of either one alone. This is the design of the test before and after the delta (the old test had the same property whenever it ran with an empty effective cache), not a weakening introduced by 84be25c4. The test would not catch dropping only one guard; this is noted, not a defect of the delta. Scratch files are outside the repo and were reverted to the originals after the runs.

## 3. Passes now with the real cache populated (met)
- Real HF cache holds `models--openai--clip-vit-large-patch14` and `models--google--siglip-so400m-patch14-384` (`~/.cache/huggingface/hub`).
- `pytest tests/exp_p2/test_gate_a6_r1.py::test_the_hf_scorer_does_not_touch_the_network_without_approval` in the worktree: `1 passed` (9.6 s).
- Full-suite record `runs/P2-LRF-L1.try2/pytest-full-84be25c4.txt`: `806 passed, 5 skipped` (305.6 s). Comparison file `pytest-full-1871fe7d.txt`: `1 failed, 805 passed, 5 skipped`, the one failure being this test. 805 + 1 = 806: the delta fixes exactly that test and changes no other outcome. (I did not re-run the full suite; the count is read from the committed log.)

## 4. No committed run is affected (met)
Production code at 1871fe7d equals that at 84be25c4 (item 1), so nothing a run executed changed. Run provenance checked from the `git_sha` fields and commits (each descends from 1871fe7d and `git diff --quiet 1871fe7d <sha> -- exp_p2 tools analysis analysis_posthoc tests` returns 0 for each):
- L1: `runs/P2-LRF-L1/config.json` git_sha e169282a.
- LG: `runs/P2-LRF-LG/config.json` git_sha 4b7c1f8c.
- Suite: `runs/P2-GATE-SUITE/config.json` git_sha 938f2272.
- Baselines (CPU, 89423704) and pixel-parity (2db50b5f): no git_sha field in their JSON; their commits descend from 1871fe7d with the same zero diff, and `analysis/paper2/lrf/baselines.py` is unchanged across 1871fe7d..84be25c4.
- The baselines/parity runs use `HFScorer` with the real cache and `local_files_only`, which this test never executes (it uses an empty tmp cache); the delta changes only test setup.
- (`c959e659` in the suite config is the imagecorruptions library commit, not a repo commit.)

## 5. Card row text for the lead
Suggested row (append after A-8; wording is the lead's to adjust):

| A-9 | 2026-10-30 (time of the lead's entry) | **Code pin moves from `1871fe7d` to `84be25c4`** (test-only). One change: `tests/exp_p2/test_gate_a6_r1.py::test_the_hf_scorer_does_not_touch_the_network_without_approval` also points transformers' import-time cache globals (`TRANSFORMERS_CACHE`, `PYTORCH_TRANSFORMERS_CACHE`, `PYTORCH_PRETRAINED_BERT_CACHE`, `transformers/utils/hub.py` lines 95-97, 322) at the test's empty tmp cache, by monkeypatch (5 added lines). Closes the A-8 residual (env-dependent failure since the pinned CLIP/SigLIP weights entered the real HF cache). `git diff 1871fe7d 84be25c4 -- exp_p2 tools analysis analysis_posthoc` is empty, so production code is byte-identical and no run (L1, LG, baselines, pixel parity, suite) is affected. tests/exp_p2 at 84be25c4: 806 passed, 5 skipped (`runs/P2-LRF-L1.try2/pytest-full-84be25c4.txt`). Limit: the test fails only if both `force_offline` and `local_files_only` are dropped, not either alone (design property, unchanged). Pre-launch check for any later stage: `git diff --quiet 84be25c4 HEAD -- exp_p2 tools tests`. | GATE-CODE-DELTA-AUDIT-HFTEST-2026-10-30.md |

Note for the lead: A-8's pre-launch check (`git diff --quiet 1871fe7d HEAD -- exp_p2 tools tests`) now returns 1 because of this test delta (verified: `tests` diff rc=1, production rc=0). Use the 84be25c4 form above, or keep 1871fe7d and drop `tests`. Also fill in the true time of the A-9 entry; I did not assume one.

## Criteria table
| Criterion | Status | Evidence |
|---|---|---|
| Diff test-only, no production path | met | git diff --stat above |
| Test still guards no-network / WeightsNotCached / no cache writes | met | mutation table; test lines 275-277 |
| Passes with populated real cache | met | single-test run; pytest-full-84be25c4.txt |
| No committed run affected | met | git_sha provenance, zero production diff |
| Card row text | provided | item 5 |

Progress.md gate tick: none (this is a code-delta audit; the lead records A-9).
