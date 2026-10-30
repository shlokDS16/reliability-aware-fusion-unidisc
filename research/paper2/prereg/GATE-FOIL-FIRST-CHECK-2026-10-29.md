```yaml
agent: gate-auditor
date: 2026-10-29
brief: Confirm or reject the statistician's E3 reading in SAP A4.3.2 (b) (r3) that running FOIL (card v4 rows 10-11) before S2 (rows 8a-9) cannot change any S2 item, draw or decision
sources_examined:
  - exp_p2/run_gate_foil.py (1-149)
  - exp_p2/gate/foil.py (1-598), exp_p2/gate/analysis_foil.py (1-152)
  - exp_p2/run_gate_s2.py (1-338), exp_p2/run_gate_s2_smoke.py (1-68), exp_p2/gate/reinfill.py (1-122), exp_p2/gate/arms.py (1-61)
  - exp_p2/gate/gate_driver.py (1-221), exp_p2/gate/runner.py (1-236), exp_p2/gate/pipeline.py, dcache.py, checks.py, pins.py, hold.py, seeds.py, data.py, artifacts.py, config.py, common.py
  - grep over exp_p2/ and exp001/ for dcache, RNG seeding, foil references, HF settings
  - research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md (A4.3.2 (b), lines 633-655), research/paper2/prereg/S2-RUN-CARD-2026-10-29.md (sections 2 and 6, by grep)
  - ls of runs/P2-GATE-DCACHE (file names only)
coverage: Code paths listed above at the working tree, which equals the pin d81858c0 for exp_p2/, tools/ and exp001/ (git diff d81858c0..HEAD shows no change there; HEAD is 697af03a, a docs/runs commit). git status of exp_p2/ is clean. NOT covered - no run was started; no file under runs/ of M4, M5 or FOIL was opened (FOIL has none); analysis_s2.py and analysis_m4.py were only grepped for "foil" (no hit), not read; scoring.py and exp001/unidisc_net.py were read only where RNG, cache or environment settings are set (grep plus lines 150-160, 165-195), not in full; the UniDisc tokenizer and VQ loader were not traced for network or cache writes.
```

# Verdict: CONFIRMED, with two wording corrections

Evidence level for every claim below: E3 (code inspected at the pin; nothing run).

The operative conclusion holds. Running FOIL (rows 10-11) before S2 (rows 8a-9) cannot change any S2 item, any S2 draw, or any S2 decision. No FOIL output can reach an S2 input.

Two statements in A4.3.2 (b) are not literally exact. The conclusion does not depend on either, but the deviations box must not repeat them as written (section 6).

## 1. What FOIL reads and writes

Reads (all, by code path):
- FOIL data file `COCO_DIR/foil/foilv1.0_test_2017.json`, checked against SHA-256 (`foil.py:63-82`, `run_gate_foil.py:46`).
- `runs/P2-GATE-FOIL/pool.json` and `leak_check.json` (`run_gate_foil.py:47-59`).
- `runs/P2-GATE-FOLDS/folds.json` (`foil.py:539`).
- `runs/P2-PROBE-01|02/selection.json` (`data.py:42-47`).
- COCO val2017 captions, images and zip member names (`foil.py:540-541`, `common.py:99-136`).
- Test stage only: `runs/P2-GATE-FOIL/fusion_frozen.json`, which must be committed with status ok (`run_gate_foil.py:61-67`).
- The model, loaded by `common.load_net()` (`run_gate_foil.py:137-139`).
- The shared null cache `runs/P2-GATE-DCACHE` (see section 3).

It reads no file of `P2-GATE-M3`, `P2-GATE-M4`, `P2-GATE-M5`, `P2-GATE-S2` or `P2-GATE-EPRED-FIT`. It does not read `family.json` or any M4 flag.

Writes (all, by code path):
- `runs/P2-GATE-FOIL-FIT|TEST/`: config.json, env-lock.txt, items.jsonl, chunks.jsonl, arrays/, selfcheck.json, l10.json, leak_check.json, token_exclusions.json, effective_n.json, telemetry and driver logs (`runner.py:114,127,150-162,209-210`; `checks.py:30`; `run_gate_foil.py:53,95`).
- `runs/P2-GATE-FOIL/fusion_frozen.json` and `analysis.json`, from the CPU analysis (`analysis_foil.py:137,141`). Write-once via `artifacts.py`.
- `runs/P2-GATE-DCACHE/DT_n*.npy`, only when a caption length is not yet cached (`dcache.py:45-57`).
- It never rewrites the committed `runs/P2-GATE-FOIL/leak_check.json` (`run_gate_foil.py:51-54`).

## 2. What S2 reads (every input)

S2 (`run_gate_s2.py`):
- `runs/P2-GATE-M3/family.json` (`:62-75`).
- `runs/P2-GATE-FOLDS/folds.json` and `runs/P2-GATE-M4/token_exclusions.json` (`:78-95`).
- `runs/P2-GATE-M4/items.jsonl` and `arrays/item*.npz` (`:98-111`, `:154-166`).
- COCO captions and images, and the model.
- Figure mode: its own `runs/P2-GATE-S2/items.jsonl` and `arrays/` (`:297,326`).
- It does not use `DCache` or `dcache_for`. The item function calls `pipeline.caption_lambdas` (`:158`), which is a direct pass and not a cached null (`pipeline.py:38-41`).
- The only config constants are `config.SEED_GATE` and `ALPHA_PRIMARY`.

S2 smoke (`run_gate_s2_smoke.py:58`): calls `run_gate_s2.main` under a separate run id. It adds no input and keeps only `n_rows`.

`reinfill.py` takes only its arguments plus `scoring` constants. It has no file access and no cache.

`arms.py` is pure functions. No file access, no state.

None of these paths names a FOIL file, a FOIL run id, or `P2-GATE-DCACHE`. A grep for "foil" in `run_gate_s2.py`, `run_gate_s2_smoke.py`, `reinfill.py`, `arms.py`, `analysis_s2.py`, `run_gate_m4.py` and `run_gate_m5.py` returns no hit.

Elsewhere in `exp_p2/`, `foil` appears only in these modules:
- `ps_freeze.py:84-86`, `run_gate_epred_chunk.py:87` and `run_gate_suite.py:57` call `foil.require_committed`, a git helper.
- `tier3_fusion.py:431` mentions it only in a docstring.
- `run_gate_epred_chunk.py:36` and `run_gate_suite.py:27` import the module.

## 3. Shared cache (runs/P2-GATE-DCACHE) - correction 1

FOIL calls `pipeline.dcache_for()` (`run_gate_foil.py:103`) and, per pair, `pipeline.text_direction(..., ctx.dcache)` (`:113`), which calls `dcache.text_logp` (`pipeline.py:56`). That reads `DT_n<len>.npy`, or computes and writes it if absent (`dcache.py:32-57`). So FOIL does depend on a file that M2/M4 wrote. The statement "FOIL takes no M2-M4 input" is not literally exact.

- Directory listing now (names only): DI_n007..n029 and n031; DT_n008..n024, n026..n029 and n031. DT is absent for lengths 5-7, 25, 30 and 32. FOIL may therefore write some DT files.
- S2 has no reader of this directory (section 2), so a file FOIL adds there cannot reach S2.
- Other stages that do read it: M1, M2, M4, epred-fit, suite and omni (its own cache). M1, M2, M4 and epred-fit are finished. The suite is exploratory and ranks behind S2 in the AD.8 cut order. M5 does not use it (no hit in `run_gate_m5.py`).
- A value read or written is a layout-only null checked by L10 (`checks.py:22-33`, atol 1e-5). It does not depend on which process computed it.
- Writes are atomic (temp file then `os.replace`, `dcache.py:47-53`). They do not collide with S2, which never opens the directory.

## 4. Random numbers - correction 2 (partial)

The statement "FOIL draws no random numbers" is true for the item path and the statistics, but not for every line it executes. Exact inventory:
- FOIL item path (`run_gate_foil.py:106-117`, `pipeline.caption_lambdas`, `image_delta`, `text_direction`, `scores.py`, `evidence.py`): no RNG (grep of `scores.py`, `evidence.py`, `core.py` shows only seeded `Generator` arguments).
- Start-up checks: `foil.selftest()` uses `np.random.default_rng(1)` (`foil.py:322`) and the layout self-check uses a local `torch.Generator().manual_seed(0)` (`scoring.py:156-158`). Both are local generator objects. Neither touches global state.
- Pool building (`foil.py:202`, `default_rng(SEED_POOL)`) runs in `build-pool`, not in a FOIL stage; the pool is already committed.
- FOIL analysis: `seeds.seed_for("fusion")`, a `SeedSequence` child (`seeds.py:20-28`, `analysis_foil.py:104,116`). S2 analysis uses the separate children "s2_family" and "s2_descriptive" (`seeds.py:20-21`). Spawn children are indexed by position, so they do not interact.
- Global RNG calls in all of `exp_p2/` and `exp001/`:
  - `np.random.seed` and `torch.manual_seed` occur only in `exp001/unidisc_net.py:178-179` (`official_t2i`, which neither FOIL nor S2 calls).
  - `np.random.get_state/seed/set_state` occur only in `suite.py:108-119`, saved and restored.
  - Neither FOIL nor S2 calls any of them.
- S2 streams: `np.random.default_rng([seed, gid, cond_index, ARM_TAG, rep])` (`arms.py:53-55`, tags 6-11 for S2 at `arms.py:58-59`) for sets and orders, and a per-draw `torch.Generator(device).manual_seed(seed_b)` (`reinfill.py:75,91`). The sample seed comes from `arm_rng` (`run_gate_s2.py:146`). Every S2 stream is a pure function of (`SEED_GATE`, item gid, condition index, arm tag, draw), so no earlier process can alter it.
- Each chunk is a new subprocess (`gate_driver.py:184-189`), so no in-process state crosses a stage boundary.
- FOIL's gids are 4000+ and 5000+ (`foil.py:48`). S2 items use fold gids below 2500 (`config.py:18`), and FOIL does not use its gid for any random stream at run time anyway.

## 5. Driver order fences (gate_driver.py)

- `STAGES` holds `s2` (`:41`) and `foil-fit`, `foil-test` (`:43-44`) as independent entries. There is no cross-stage dependency table, no check of another stage's run directory, and no ordering code in the driver.
- The driver would not refuse FOIL before S2, nor S2 after FOIL.
- Every refusal is in the stage runner:
  - S2: M3 `family.json` and M4 completeness (`run_gate_s2.py:286-294`).
  - foil-fit and foil-test: committed pool and leak check (`run_gate_foil.py:47-59`).
  - foil-test only: committed `fusion_frozen.json` with status ok (`:61-67`).
  Neither stage checks the other.
- Run-independent fences that apply equally in either order:
  - Hold files: the global `runs/P2-PROBE-02/HOLD.txt` and per-run files (`hold.py:19-25`, `gate_driver.py:132-152`).
  - Dirty-tree check on `exp_p2/` and `tools/` only (`pins.py:52,58`). `fusion_frozen.json` and `pool.json` live under `runs/`, so committing them does not trip it.
  - The `gpu_guard.py` pin (`gate_driver.py:142-145`).
  - The per-driver event-log check, `new_events(started)` with `started` set at each driver start (`:147,153-160`).
  - Battery and temperature gates.
- A hold file or crash-signature event created during FOIL would block a later S2 launch. That is the stop case of A4.3.2 (b) item 5, a scheduling effect and not a content effect.
- Committing `fusion_frozen.json` moves HEAD, which `init_run` records as `git_sha` in S2's `config.json` (`common.py:67`). It is metadata and enters no S2 computation.
- `analysis_foil analyze` has no code fence against running before S2. Rule 6 of A4.3.2 (b) (analyze after the S2 table) is procedural only. It is not enforced by code.
- `analysis_foil freeze` needs only the fit run (`analysis_foil.py:64-80`).

## 6. Corrections to carry into the deviations box (A4.5 item 5) and the card

1. The pointer `run_gate_foil.py:1-75` covers the docstring, imports, `check_prereqs` and `stage_items`. The per-item path and the model load are at `:77-145`. Cite `:1-149`.
2. Replace "FOIL takes no M2-M4 input" with: "FOIL reads no M2-M5, S2 or epred output; it reads and may add layout-only null files in `runs/P2-GATE-DCACHE`, which S2 never reads". Replace "draws no random numbers" with: "FOIL's scored path uses no random numbers; its only generators are local ones (selfcheck, selftest) and the bootstrap seed child 'fusion'".

## 7. Limits of this check

- It is a code reading. It shows no data flow by FOIL into S2. It does not show that GPU kernel results are bitwise reproducible across processes, but that does not depend on run order: S2's inputs and seeds are fixed by item and arm, and no state is shared across processes except files S2 does not open.
- Whether the tokenizer or the VQ loader write to a Hugging Face cache or contact the Hub was not traced. FOIL and S2 use the same loader (`common.load_net`), already exercised by M1-M5. The S2 card (section 2) records the same gap.
- Code pin: HEAD is 697af03a and the brief said d81858c0; `exp_p2/`, `tools/` and `exp001/` are identical between the two. Any later change to those paths voids this confirmation until a delta check.
- Rule 5 (a stop during rows 10-11 ends the FOIL-first order) and the time inequality (rule 3) are procedural and were not audited here.

## Ledger rows added
None.
