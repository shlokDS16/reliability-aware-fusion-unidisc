```yaml
agent: lab-engineer
date: 2026-10-15
brief: Implement EXP-003 (card v0.3.2 SIGNED) on top of the tested EXP-001 code, test it, and launch all GPU stages as one autonomous, resumable, guarded background driver.
sources_examined:
  - research/CONTRACT.md
  - research/preregistration/EXP-003-value-rule-consistency.md (v0.3.2, in full)
  - runs/EXP-001/IMPLEMENTATION.md (in full); exp001/{config,rng,runtools,gate_driver,gate_gen,network,unidisc_net,sampler,plan}.py, estimator.py (_Wrap, BlindNet); analysis/EXP-001/{prefix_rule,caption_end,completion,evalmodels,coco_draw,metrics (head),gates_eval (pgv)}.py; tools/gpu_guard.py
  - models/third_party/unidisc/model_eval.py L1734-1835 (get_cfg_weight, _ddpm_forward), L2109-2455 (_sample), L2964-3110 (adap_sche, _maskgit_update); runs/env-2026-10-14/setup.md section 2
coverage: >
  Implemented and unit-tested on CPU: nounkey, discordant sets, Lambda_b with eligibility, Lambda_d, NC-2 placebo, quality-matched
  sensitivity, cluster bootstrap (same indices in all arms, zero-denominator redraw), BCa, R5 p-value and rerun flag, Holm fixed sequence,
  outcome classes, four-arm identity, n rule and stop rules 9.1/9.2/9.3/9.6 (by script), controls decision (9.4), pools. Smoke-run on the real
  checkpoint and the real scoring models: units of all six arms for pilot prefixes 0-1, the scoring stage, pilot analysis, the confirmatory
  `analyse` function and `controls_decision` on those 2 prefixes (plumbing only; numbers not used). NOT covered: the full pilot, the controls
  and the main stage (running or pending); model-side tail-marginal entropy hook (4.3 item 7e, optional in the card); G-low and M4 (optional,
  need the orchestrator's yes); CLIP matched-minus-shuffled lift with cluster bootstrap (4.3 item 4: only the sibling link, the prefix-only
  and completion-only embeddings are produced; the lift itself is computable from the stored embeddings but is not in frozen_analysis.py).
claims:
  - statement: "G makes 64 network calls (batch-2 guided forward counted as 2), O0 33, P64 64, P32 32 on the real checkpoint; the guidance-acted assertion held at step 1 (t=0.96875) with max abs marginal difference 0.035 (text) and 0.36 (image)."
    status: supported
    evidence: smoke units (scratchpad, not in runs/); the real pilot units record calls, forwards and the assertion per unit in runs/EXP-003/gen/pilot/{G,O0,P64,P32}/p*_e*.json
    level: E4
    confidence: 0.8
competing_explanations: []
unknowns: [pilot costs, eligible share e, SD of the paired per-prefix difference, whether stop rules fire]
next_test: {hypothesis: "E3-H1, E3-H2a, E3-H2b", intervention: "driver runs pilot, controls, M1-M3, scoring", primary_metric: "Delta1 = Lambda_b(G) - Lambda_b(P64)", falsifier: "card section 5", gpu_hours: "about 2.8 compute, 5.8 wall-clock by the card's model"}
```

# EXP-003 implementation and launch

## 1. Layout

| Path | Content |
|---|---|
| `exp003/` | `config.py` (pools, seed bases 61000/62000/60000, Philox codes 31-33 registered at run time in `exp001.config.POOL_CODE`, no EXP-001 file edited), `units.py` (unit lists and paths), `official.py` (official maskgit sampler as a joint generator with read-only hooks), `gen.py` (generation stage; plain arms through `exp001.sampler.run_sample`, wrapper `IndNet`), `chunks.py` (guarded chunk runner, readiness wait, persistent GPU clock), `manifest.py` (SHA-256 manifest and freezes), `driver.py` (the pipeline) |
| `analysis/EXP-003/` | `nounkey.py`, `coco_object_nouns.txt`, `pools.py`, `stats.py` (all statistics), `tables.py` (completions, nouns, query plan, placebo sets, prefix records), `score.py` (GPU scoring: Qwen3-VL-2B presence, CLIP, CLIP-IQA), `pilot_analysis.py` (firewall + n rule + stop rules), `frozen_analysis.py` (confirmatory analysis, controls decision, label-scrambled end-to-end run) |
| `tests/exp003/` | 23 tests |
| `runs/EXP-003/` | `pools.json` (+ `.sha256`), `run_all.bat`, `driver.log`, `driver.out/err`, `DRIVER_PID.txt`, `clock.json`, `manifest.json`, `freeze-pilot.json`, `gen/<stage>/<arm>/p<PPP>_e<E>.{json,npz,png}`, `score/<scope>/<arm>/p<PPP>.{json,npz}`, `<stage>/telemetry-<stage>-<chunk>.csv`, `pilot/pilot_report.json`, `n_conf.json`, `ctrl/controls_decision.json`, `STOPPED.txt` / `DONE.txt` |

Tests (repo root): `".venv-eval/Scripts/python.exe" -m pytest tests/exp003 -q -p no:cacheprovider` gives **23 passed** (about 8 s, CPU). The driver runs them as its first step (`runs/EXP-003/tests_result.json`). The 29 reused EXP-001 files re-hash to the EXP-001 manifest with 0 mismatches (`runs/EXP-003/manifest.json`, `reused_exp001`).

## 2. Card section to code

| Card | Code | Test |
|---|---|---|
| 3 pools, 1303, disjointness, SHA-256 | `analysis/EXP-003/pools.py` -> `pools.json`: 2,200 left, 1,394 rung-2 eligible (both equal the card), 16/48/150, disjoint from `coco_draw.json` | `test_pools_json_disjoint_and_hash` |
| 2, 6 arms P64, P32, TF, Ind | `gen.py::run_plain` (plan_J 64/32, plan_TF 32, `IndNet`: prefix kept on the image side, 2 forwards per pass) | `test_plain_call_counts_and_ind_wrapper` (64, 32, 32, 64 forwards; Ind text marginals independent of the image) |
| 2 arms O0, G (32 steps, CFG 0/3.0, r_temp 4.5, noise removal on) | `official.py::OfficialRunner.run`: official `_sample`, torch/numpy seeded 7,000,000+i, `sampling.steps = max_sampling_steps = 32`, asserts predictor maskgit, r_temp 4.5, noise_removal | real smoke: G 64 calls (33 forwards, one of them batch 2... counted as 2 per guided step), O0 33 |
| 8 eval-mode assertion on every forward | backbone `register_forward_pre_hook` calling `assert_eval()` (plain arms: `UniDiscNet.forward` already asserts), plus assertions before and after `_sample` | smoke |
| 1.2 guidance-acted assertion (first step with t < 1) | wrapper of `model._ddpm_forward`: one extra conditional-only forward at that state (counted apart as `assert_calls`), max abs difference text and image above 1e-3; failure raises, the unit is rerun once then logged failed | smoke |
| 4.3 item 9 commit-order record, hook-neutrality | wrapper of `_maskgit_update` stores the token row at each entry; `commit_step` per position in the npz; `hookcheck/` pilot units re-run 8 official units with the bare `_sample` and the pilot analysis compares tokens | `test_commit_steps_and_order_summary`; pilot |
| 4.1 nounkey, discordant, Lambda_b, eligibility, Lambda_d, NC-2, quality-matched | `nounkey.py`, `stats.py`, `tables.py::placebo_sets` | `test_stats.py`, `test_placebo_and_queries` (link 0/0.1/0.3 recovered, seed swap invariance, additive image yes-bias cancels in Lambda_b but not in the v0.1 ratio) |
| 4.2, 5, 7 contrasts, identity, BCa agreement, p rule (R5 + B=100,000 rerun), Holm fixed sequence, classes | `stats.py`, `frozen_analysis.py::analyse` | `test_holm_and_classes`, `test_identity_on_common_set_and_bca`, `test_p_value_rule_and_rerun_flag`, `test_frozen_analysis_end_to_end_synthetic` |
| 4.3 descriptives | `frozen_analysis.py`: per-arm Lambda_b/Lambda_d/placebo/net-of-placebo/exact-surface/all-noun/COCO-noun, OR-rule m, s, s_sp, per-noun matched/same/cross, CLIP completion-only and full sibling link, CLIP-IQA in the quality-matched sensitivity, completion statistics, Jaccard, unigram entropy and distinct-2 at T_ref, image sibling cosine, commit-order summary | synthetic end-to-end |
| 6 NC-1, PC-1, PC-2 and 9.4 | `frozen_analysis.py::controls_decision`, `score.py::pc2` (EXP-001 PG-1 images `pg1g/item*_512px.png`) | `test_controls_decision_synthetic` |
| 7 pilot firewall, n rule, 9.1, 9.2, 9.3, 9.6 | `pilot_analysis.py` (hashed in `freeze-pilot.json` before the first pilot sample) | `test_design_rules` |
| 8 order, GPU regime | `driver.py`, `chunks.py` (below) | smoke chunks |

## 3. GPU regime as implemented

Every GPU stage (`pilot`, `score-pilot`, `ctrl`, `score-ctrl`, `m1`, `m2`, `m3`, `score-main`) is a loop of chunks `python tools/gpu_guard.py --log runs/EXP-003/<stage>/telemetry-<stage>-<chunk>.csv --max-temp 85 --max-minutes M -- <py> <script> --resume --soft-minutes M-2 --duty D`: M = 5 for a stage's first chunk, 15 afterwards, 10 after an exit 90 (duty then 1/3, pause doubled); a chunk starts only with GPU below 65 C, no other compute process and free commit at least 6 GB; 30 s pause between chunks; batch size 1; per-unit duty idle equal to the unit's compute time; done markers per unit (the `.json`, written last, atomically); three exit-90 stops, or three chunks without progress, stop the stage. Generation runs in the `.venv` python, scoring in `.venv-eval`.

## 4. Driver and how to check it

Order: tests -> pools/manifest check -> `freeze-pilot.json` (SHA-256 of `pilot_analysis.py`, `stats.py`, `tables.py`, `nounkey.py`, the COCO list) -> pilot generation (P64, G, O0, P32 on 16 prefixes x 2 seeds; G at 50 steps on prefixes 0-7 seed 0; Ind and TF on prefixes 0-3; 8 determinism reruns; 8 hook checks) -> pilot scoring -> `pilot_analysis.py` (firewalled report `pilot/pilot_report.json`, `n_conf.json`) -> label-scrambled end-to-end analysis (digest only, `pilot/scrambled_analysis_digest.json`) -> controls generation and scoring -> `ctrl/controls_decision.json` (stop on NC-1 failure; PC-1 and PC-2 failures are recorded, not stopping) -> M1 (P64 and G interleaved by prefix), M2 (O0), M3 (P32) -> `freeze-analysis.json` (hash of all analysis scripts before main scoring; the pilot freeze is re-verified) -> main scoring -> `DONE.txt`. The confirmatory analysis is not run by the driver.

Stops (`runs/EXP-003/STOPPED.txt`, driver exit 3): failed tests or reused-file hash mismatch; any stop reason of `n_conf.json` (9.1 projected wall-clock above 6.0 h at 120 eligible prefixes, or 120 eligible prefixes need more than 150 generated; 9.2; 9.3; 9.6 and the hook check; guidance assertion failures; more than 10 percent failed units); NC-1 failure; cumulative GPU wall-clock 6.0 h before M1 completes, 7.0 h hard stop; three exit-90 stops; GPU never ready.

Progress: `Get-Content runs\EXP-003\driver.log -Tail 20`; per-stage `runs/EXP-003/gen/<stage>/stage_log.jsonl`, `runs/EXP-003/score/<scope>/stage_log.jsonl`; `runs/EXP-003/clock.json` (cumulative GPU wall-clock, the quantity of stop rule 9.1: chunk wall time plus inter-chunk pauses, waiting for the GPU excluded); count done units with `(Get-ChildItem runs\EXP-003\gen\pilot -Recurse -Filter p*_e*.json).Count`; latest temperature `Get-Content runs\EXP-003\pilot\telemetry-pilot-*.csv -Tail 3`.

Resume after a crash or reboot: the driver is idempotent (each step checks its own done markers; `clock.json` persists). Restart with
`Start-Process -FilePath "C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv-eval\Scripts\python.exe" -ArgumentList "-u","-m","exp003.driver" -WorkingDirectory "<worktree root>" -WindowStyle Hidden -RedirectStandardOutput runs\EXP-003\driver.out -RedirectStandardError runs\EXP-003\driver.err`
(or `runs\EXP-003\run_all.bat`, which did not start under a WMI-created process on this machine: the uv venv trampoline failed there). The orchestrator logs a crash to the failures ledger. After a STOP: decide, `type nul > runs\EXP-003\ACK_STOP_PILOT.txt` (or `ACK_STOP_CONTROLS.txt`, `ACK_STOP_BUDGET.txt`), delete `STOPPED.txt`, restart; to change n, edit `runs/EXP-003/n_conf.json` (`n_generate`) first.

Stop the driver: the PID is in `runs/EXP-003/DRIVER_PID.txt`; `taskkill /F /T /PID <pid>` also ends the running chunk (gpu_guard, generation or scoring child). Units finished before the kill are kept; an unfinished unit is redone on resume.

## 5. Interpretations, ambiguities and things to read (none changes a number on the card)

1. **Noun key** `-s`/`-es`: the card gives one sentence. Implemented: strip `es` when the stem ends in s, x, z, ch or sh, otherwise strip a final `s`, never from `-ss`, only if at least three letters remain (`nounkey.py` docstring; frozen in `freeze-pilot.json`).
2. **Pool permutation order**: leftovers kept in image-id order before `default_rng(1303).permutation` (the counts 2,200 and 1,394 match the card; the order is my reading).
3. **Placebo**: the card draws placebo nouns "from the discordant nouns of a different prefix"; the pool is the union of both seeds' discordant nouns of the derangement partner (seed 5302), minus keys present in either completion of the prefix; if the pool is smaller than |D_pe| all of it is used (flag `short`), and a prefix with an empty placebo side drops out of Lambda_b^plac. Placebo is scored for P64, G, O0, P32 (the card requires P64 and G; the others are descriptive) and not for TF.
4. **PC-2 derangement seed**: the card says "one fixed derangement" without a seed; I used 5303.
5. **Quality-matched slope** is of L_p on the absolute sibling CLIP-IQA difference (L_p is symmetric in the seeds).
6. **Stop rule 9.2 "such samples"**: a degenerate sample = empty completion (including pad-only tail); G32 degenerate if at least 16 of 32 are empty or at least 8 of 32 images are near-uniform (pixel SD < 6 as EXP-001 PG-1); G50 passes if at most 1 of 8 is empty or near-uniform.
7. **n rule**: eligible share e from the pilot (prefixes eligible in both G and P64); sigma_up = 1.21 x pilot SD (the card's constant, not recomputed for fewer clusters); n_conf = clamp(n_req, 120, floor(e x n_cap)); generated = min(n_cap, 150, ceil(n_conf/e)); n_cap = largest generated count whose projected wall-clock (pilot actual + controls + generation + scoring, each at duty 0.5 with 25 s model loads and 30 s pauses per 13-minute chunk) is at most 6.0 h. The projection uses measured seconds per sample and measured scoring seconds per prefix.
8. **Network calls**: a guided step is one batch-2 forward, counted as 2 calls (as the card); the extra forward of the guidance assertion is excluded (`assert_calls`).
9. **Scoring is heavier than the card's cost model** (10.6 s per prefix): it adds the cross-prefix queries for the OR-rule gap, the placebo queries and CLIP; the pilot measures the real figure and stop rule 9.1 evaluates it.
10. **Card statement to check**: 1.2 says the unconditional branch removes only the prefix positions. In the code `x_uncond[x0_unmask] = mask` masks every observed position of the row (system prompt, markers, prefix) because `unmask` is true everywhere except the 32 tail and the image positions. The assertion that guidance acted holds either way.
11. **Firewall disclosure**: the smoke tests used pilot prefixes 0-1 (E3-PILOT, same seed indices) and I printed, among plumbing outputs, a 2-prefix Delta1 class and identity values. They are in the scratchpad, not in `runs/`, no pilot sample enters any test, and the main and control pools were not touched.
12. **Not implemented**: tail-marginal entropy hook (4.3 item 7e, optional), G-low/M4, CLIP matched-minus-shuffled lift bootstrap, GPT-style text-quality secondaries (none in this card).
