```yaml
agent: gate-auditor
date: 2026-10-28
brief: Independent code audit of the MUST-tier GATE code against SAP-GATE-2026-10-28 (incl. Addendum 1) and GATE-METHOD-SPEC-v2; readiness for M0 once the GPU hold is lifted. No GPU, no weights, no runner launched, no code changed.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (sections 1-9 and Addendum 1 read; Appendix A power script not re-run)
  - research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md (sections 4-8, 10, 11)
  - research/paper2/method/GATE-IMPLEMENTATION-NOTES-2026-10-28.md (full)
  - research/paper2/probes/PROBE2-CRASH-DIAGNOSIS-2026-10-28.md (sections 1-5)
  - exp_p2/gate/{stats,headroom,evidence,analysis_m4,detect,folds,calibrate,fit_threshold,arms,pipeline,scores,runner,guards,hold,gate_driver,jsonl,corruptions,dcache,checks,baselines,fusion,data,config}.py
  - exp_p2/{run_gate_m0..m5,analyze_gate_m1,driver}.py, exp_p2/run_probe2.py (grep only), exp_p2/common.py (init_run, read/append_jsonl), tools/gpu_guard.py
  - tests/exp_p2/test_gate_analysis.py (1-150), test_gate_runner.py (full), test_gate_calibrate.py (guards), test_gate_runners_fake.py (183-246), test names of all other test files
  - runs/P2-GATE-FOLDS/folds.json
coverage: >
  Not covered: hardneg.py, theory.py (Prop. 4 plug-in), coherence_report.py, cpu_dryrun.py (SHOULD/secondary or exploratory); the GPU path of
  exp_p2/scoring.py (UniScorer) which is unchanged and untestable on CPU; SAP Appendix A power numbers (not recomputed, only the exact N*=43 check);
  the Prop. 1/6/7 theory tests. I did not rebuild folds.json (needs the tokenizer); I checked the file independently and relied on the
  existing test for the test300 == test500[:300] property.
claims:
  - statement: "The primary test (exact two-sided McNemar, Y with ties wrong, Holm over a fixed m=3 with p=1 for untested corruptions, rejection only with b>c) is implemented as preregistered."
    status: supported
    evidence: "stats.py:10-32, analysis_m4.py:57-74; recomputed here: 300 random paired datasets, 0 mismatches against scipy.stats.binomtest; Holm hand cases; primary() on synthetic b=0,c=30 gives gate_better False, b=30,c=0 gives True; Holm [0.001,1,1] -> [0.003,1,1]"
    level: E4
    confidence: 0.9
  - statement: "Headroom rule, endpoint d, n_v>=90, T1,T2>=2, exact N*=43, kappa=0.5 and the R1/R2/R3 boundaries (D*>=29 / >=18) are implemented as preregistered."
    status: supported
    evidence: "headroom.py:30-110; stats.exact_sign_min_n(0.75,0.0167)=43 recomputed; tests test_gate_analysis.py:90-138"
    level: E4
    confidence: 0.9
  - statement: "Several preregistered analyses have no implementation: S-M (exact McNemar vs geometry-matched seed 1, gatekept), S-C clean-control McNemar, the Z_cal calibration check with the 2.13 rule, split replication, the 98.33 percent and Clopper-Pearson intervals, mid-p, completeness/prefix report."
    status: supported
    evidence: "grep for z_cal|2.13|split_replication|clopper|98.33|midp over exp_p2 and tests returns nothing; analysis_m4.py:178-218"
    level: E3
    confidence: 0.95
  - statement: "Folds are disjoint, fixed by seed and image id, exclude the 494 probe ids, and the negatives stay inside their block."
    status: supported
    evidence: "folds.json: 300/100/300/200, 900 unique ids, 0 overlap with the 494 probe ids (recomputed from P2-PROBE-01/items.jsonl and P2-PROBE-02/selection.json), negatives in-block, no self or same-caption negatives, tokens 8-31; file is tracked in git (b18129f9)"
    level: E4
    confidence: 0.9
  - statement: "Tests: 122 passed in 24 s with CUDA_VISIBLE_DEVICES empty."
    status: supported
    evidence: "command in the brief, run this session (output not stored in runs/)"
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - "Whether UniScorer, the VQ encoder, real tie structure of q and real memory behave as the fake network does (all GPU paths untested; the notes say so too)."
  - "Whether the diagnosis' H1/H2 are the cause; no code can remove a driver fault."
next_test: {hypothesis: "fixes F1-F9 below close the gaps", intervention: "re-audit after fixes", primary_metric: "all criteria met", falsifier: "any missing criterion", gpu_hours: 0}
```

# Audit of the MUST-tier GATE code (2026-10-28)

## Verdict: PASS WITH FIXES for "ready for M0 once the GPU is released"

Reasoning in one paragraph. The statistics that carry the headline (family P, headroom rule, n-rule, S-DN, S-D, S-D2, the folds and the CRC
threshold) are implemented as preregistered, and I recomputed the McNemar, Holm and N* pieces independently. The folds are leak-free on
every check I could run on CPU. The resumable loop, hold check and per-item guards exist and are tested. There is no BLOCKER for M0 itself
(M0 stage 1 is a load, one forward and an idle; stages 2 and 3 run the old probe code by hand). But "ready" is not "complete": (a) the
M1-onward driver does not treat a guard abort as an abort, and the probe-2 completion stage runs the old guards that were in force when the
laptop crashed; (b) three preregistered secondary analyses and the K4 calibration check are not implemented. I tick no gate: this is a code
audit, not the MUST gate. The M0 PASS is conditional on F1 to F3 below being done or accepted by ANONYMIZED. The M4 analysis is NOT ready until F4 to F6 are done.

Does not count as a waiver: nothing here waives a criterion.

## Criteria table (checks 1 to 5 of the brief)

| # | Criterion | State | Evidence |
|---|---|---|---|
| 1a | Exact two-sided McNemar, b = GATE-M right and none wrong, ties/empty R wrong | met | `stats.py:10-21`, `evidence.py:40` (`y=int(mean>0)`), `analysis_m4.py:65`; scipy cross-check, 0 of 300 mismatches |
| 1b | Family P m=3 always, untested p=1, claim only with b>c | met | `analysis_m4.py:57-74` |
| 1c | n-rule N*=43, kappa 0.5, D* over passing corruptions, 3x and 5x scaling, R3 | met (rule), partly (R3 routing, see F8) | `headroom.py:74-84`, `stats.py:68-73` |
| 1d | Headroom endpoint d, `--endpoint d` default, `"endpoint": "d"` in family.json, M4 refuses otherwise, n_v>=90, T>=2, blind | met | `headroom.py:35-71,87-109,115`; `run_gate_m4.py:49-50`; `analysis_m4.py:247-249` |
| 1e | Sign-oracle rival, Holm m=2 for S-D, frozen rival and S-D2 m=2, S-DN m=2, S-Z Wilcoxon m=3 on d | met | `detect.py:100-158`, `analysis_m4.py:77-175,96-118` |
| 1f | S-M (exact McNemar GATE-M vs geo seed 1, gatekept, m=3, seeds 2,3 as replications) | **missing** | F4 |
| 1g | S-C clean-control exact McNemar (m=1) | **missing** | F4 |
| 1h | Section 6 calibration check: Z_cal, three alpha levels, 2.13 rule (K4), split replication, precision/FAP reports | **partly** (FAP and precision reported; Z_cal and the rule absent) | F5; `analysis_m4.py:198-218` |
| 1i | CIs at 95 and 98.33 percent, Clopper-Pearson of theta, mid-p, accuracies | **partly** (95 percent bootstrap of the diff only) | F6 |
| 2 | Folds disjoint, seed and id fixed, no early outcome reads | met with minor gaps | folds check above; F7, M3 |
| 3 | Arms and CRC match the spec | met | `arms.py`, `calibrate.py:74-95`, `run_gate_m4.py:121-145` |
| 4 | Safety: HOLD, gpu_guard, resume, memory cap, AC and memory guards | **partly** | F1, F2, F3, M1, M2 |
| 5 | Tests exercise behaviours | met for core logic, weak for M4 analysis and driver | section 5 |

## 1. SAP tests, line by line

Checked and correct:
- `stats.mcnemar_exact` (`stats.py:10-21`): p = min(1, 2 P(Bin(n_d,1/2) <= min(b,c))); NaN pairs dropped; n_d = 0 gives p = 1. Cross-check against scipy on 300 random paired datasets (n = 300): 0 mismatches.
- `stats.holm` (`stats.py:24-32`): monotone step-down, hand cases correct ([0.01,0.04,0.03] -> [0.03,0.06,0.06]; [0.016,0.03,0.04] -> [0.048,0.06,0.06]).
- `analysis_m4.primary`: loops over the fixed triple (jpeg, noise, splice), untested gets `p=1.0` and stays in the Holm list, `gate_better` needs `b>c` and Holm p < 0.05.
- `headroom.evaluate_rung`: T1 = clean - none, T2 = chg - none, over items with all three endpoint values finite; `n_v >= 90`; NaN T (sd 0) fails. `decide` walks the ladder in config order and records all rungs; `D_c` = discordant count chg vs none; D* = max over family.
- n-rule boundaries: 0.5 x 3 x 29 = 43.5 >= 43 and 0.5 x 3 x 28 = 42 < 43; 0.5 x 5 x 18 = 45, x 17 = 42.5; the code and the tests agree.
- Detection: `detect.CHEAP` has texture, neighbour, rarity each in both signs, s3, plain-B, TbV; r_original and random excluded; best = highest mean (sign included); bootstrap p two-sided with +1; Holm over m = 2 with p = 1 for a corruption without q; reselect and 179-item sensitivities exist; `freeze_rivals` writes name, base, sign; `s_d2` uses the frozen rival, 5-token class floor, Holm m = 2, p = 1 stays in family.

Deviations from the SAP (findings F4, F5, F6, M3-M6 below):
- Geometry contrast averages y over the three seeds (`analysis_m4.py:186`), which is the v2 7.4 wording, but SAP 2.5 and 8.3 replace it by seed 1 only with an exact McNemar. There is no McNemar for S-M, S-C, and no K5/K6 flag.
- `calibration()` reports `at_most_alpha_plus_se` (2 SE of the item-level FAP, `analysis_m4.py:209`), not `Z_cal = (F-alpha)/(sigma_L sqrt(1/n_cal + 1/n_test))` with the 2.13 threshold over three alphas.
- Bootstrap seed is `0` everywhere (`analysis_m4.py:37,167`, `detect.py` seed 0); SAP 8.4 says `SeedSequence(20261028)` spawned by analysis name, with the seed and NumPy version written into every output file. Results are deterministic but not as preregistered.

## 2. Leakage and ordering

Verified on the real `folds.json` (CPU, recomputed): calibration 300, headroom 100, test 300, extension 200; 900 distinct image ids; zero overlap with the
494 probe-1 and probe-2 ids; each negative lies in its own block (cal, head, test base, extension), none is its own image or has the same caption;
all 900 captions have 8 to 31 tokens; gids are unique (offsets 0, 1000, 2000, extension continues at 2300). `folds.json` is tracked in git (commit b18129f9,
before M3 as Addendum N13 requires). `build_folds` consumes the RNG per image id regardless of the token filter, so the first 300 test items do not depend on the total (and
`test_gate_data.py:180` pins the property including negatives).

Outcome reads: M3 rows contain no gate fields (`assert_blind`, `headroom.py:35-38`; M3 never computes a flag, `run_gate_m3.py:50-70`). M4 reads only M2's `threshold.json` and M3's `family.json`.
M5 uses calibration items. Jitter seeds come from `(SEED_GATE, gid, condition index, tag, rep)`, so reruns are identical and independent of the test outcomes.
CRC is correct (`calibrate.py:85-95`: r* = (alpha(n+1)-1)/n, strict tail, first feasible value; brute-force test in `test_gate_calibrate.py:30`).

Gaps are in M3, M4, M5 and F7 below.

## 3. Findings

### BLOCKER
None.

### MAJOR (fix before the stage named)

**F1. Guard aborts are retried by the driver (before M1).** `runner.py:130,135,161` all return `EXIT_MORE_WORK` (75): soft deadline and guard stop look the same. `gate_driver.py:98-115` treats only exit 90 specially and counts "no progress" as the only failure. A `slow_item`
stop (row committed, so progress was made) or a memory-rise stop after several items is relaunched after 30 s, up to `--max-chunks 12`. The diagnosis (section 5) says: abort rules stop the process and "do not retry the same stage until reviewed".
Fix: return a distinct code for a guard stop (for example 76) from `run_items`, and make `gate_driver` stop with that code; also make the driver read `chunks.jsonl` for `guard_stop` after every chunk. Add a driver test where a fake child returns 76 and assert no relaunch.

**F2. The probe-2 completion stage runs the old guards (before M0 stage 3 and M1).** `gate_driver.py:26` runs `exp_p2.run_probe2` unchanged: `MEM_FRAC=0.75`, `MAX_GPU_USED_MIB=10750` (`run_probe2.py:38,149-152`), no first-item allowance, no AC check, no slow-item rule, no rise rule. This is the code that crashed twice, and
the one stage the diagnosis most wanted guarded. The notes (section 2) say the edits were deliberately not made because they need ANONYMIZED's approval. That is correct process, but it leaves the highest-risk stage with the weakest guards.
Fix: get ANONYMIZED's yes, then either port probe 2's item function into a runner that uses `gate/runner.run_items` (all guards, same arrays and seeds, same row schema), or apply the diagnosis diff to `run_probe2.py`. Until then, run stage 3 and M1 part 1 only with the operator watching, and record that the guards differ.

**F3. No AC or power-flap check before the model load, and no event-log check between chunks (before M0).** `runner.py:104-108` loads the model before the first `guards.before_item` (the AC check at `guards.py:47` happens only there); `run_gate_m0.py:44-52` has no AC check at all.
`on_ac()` samples the state at one instant, so a flap that ends before the next item is invisible. The diagnosis' H2 (crash 1 came 106 s after an AC change) and its section 4 ("refuse to relaunch if System log has Id 105 within 30 min or a 116/117 since the last launch") are not implemented anywhere.
Fix: (i) call `guards.on_ac()` at the top of `run_gate_m0.main` and `run_items` (before `load()`); (ii) in `gate_driver`, before each chunk, query `Get-WinEvent` (System Id 105, 117, Display 4101, Application WER 1001 with the Blackwell bucket) since the last launch and stop on a hit.

**F4. S-M, S-C and K5/K6 are not implemented (before M4 analysis, not GPU-blocking).** SAP 2.5 fixes S-M as exact McNemar on y, GATE-M vs geometry-matched random seed 1, gatekept on P rejections, m = 3 with p = 1 for the others, seeds 2 and 3 as separate replications; S-C as exact McNemar on clean images, m = 1.
`analysis_m4.mechanism` (`:178-195`) gives only paired bootstrap CIs of mean y, with the three geo seeds averaged (`:186`), so a McNemar cannot even be applied to its output. The data are stored per seed (`arm_G["geo0..2"]`, `run_gate_m4.py:139-141`), so the fix is CPU-only: add `s_m()` (per-seed McNemar, gate arm first, Holm m = 3 gatekept by `primary()["gate_better"]`),
`s_c()` (McNemar on `clean` gate0.05 vs none), and the K5 and K6 flags (K6: |b - c| <= 2 for GATE-M vs geo on every P-rejected corruption).

**F5. The K4 calibration check is not implemented (before M4 analysis).** SAP section 6 steps 1-3 and 5: `Z_cal`, `sigma_L` pooled, violation iff `Z_cal > 2.13` at any of alpha in {0.01, 0.05, 0.10}, item-clustered bootstrap CI, and the 2,000-split exploratory replication.
`calibration()` (`analysis_m4.py:198-218`) has none of it; `at_most_alpha_plus_se` (`:209`) is a different, looser rule. Without it K4 cannot be applied as written.

**F6. Reporting items required "with every test" are absent (before M4 analysis).** SAP 2.3: 98.33 percent bootstrap CI beside the 95 percent one, Clopper-Pearson CI of theta = b/n_d, the mid-p sensitivity, both accuracies and n_d in one record. Also section 8.1: planned vs completed n, prefix check, caption-length covariates of missing vs completed, worst-case missing-item sensitivity, K7 (more than 5 percent NaN or empty R stops the analysis);
section 10: `selftest()`, de-duplication by (item, arm, corruption) (`analysis_m4.run` reads rows with `common.read_jsonl` and does not de-duplicate), the equivalence statement (90 percent CI against +/-0.05 in section 9).

### MINOR

**M1.** `gpu_guard.py:58-70` only kills on temperature (3 consecutive readings) and time. The diagnosis' other abort rules are logged but not enforced there: whole-GPU memory above 9,000 MiB or a rise above 1.5 GB between 1 s samples, throttle reason other than 0x0/0x4, `nvidia-smi` NA or slower than 3 s. The per-item check in `guards.py` cannot catch a rise inside an item (the crash happened within 5 s, an item takes 7 to 10 s). Add `--max-mem-mib`, `--allowed-throttle`, and an NA-streak rule to `gpu_guard.py` (it is a project tool, outside the audited gate package).

**M2.** Memory cap: runners default to `--mem-frac 0.75` (`runner.py:31`) although the diagnosis proposes 0.60; the notes explain why (0.60 is about 7.2 GiB, below the 8.2 GB first-item peak). Keep 0.75 but get ANONYMIZED's explicit yes, since the 0.75 cap did not prevent crash 2. The guard thresholds (9,000/10,000/1,500 MiB, 2x) are also proposals and are the defaults.

**M3.** `run_gate_m4.py:157,172-175`: nothing ties `--n` to `family.json["n_rule"]["test_fold"]`. Default is 300; under R2 an operator who forgets `--n 500` runs a 300-item test that SAP 4.6 says must be 500. Fix: in `make_ctx`, compare `a.n` with the committed rule and refuse on mismatch (R1/R3: 300, R2: 500; NO-GO: 300).

**M4.** `analysis_m4.main` (`:237-257`) defaults `--frozen` to `runs/P2-GATE-M1/detection_frozen.json` and, if it is missing, silently gives S-D2 p = 1 (`:149-151`). SAP A1.2 rule 5 says the file is committed before M3 or M4 runs. Also `run_gate_m4.load_prereqs` (`:41-55`) checks `threshold.json` and `family.json` but not the frozen file. Fix: M4 (and M3) runner refuse to start without `detection_frozen.json`; `analysis_m4.main` errors if it is missing.

**M5.** `analysis_m4.main` and `headroom.main` can be run on a partial fold with no warning (`analysis_m4.run` reports `n_items` only). SAP 8.2 forbids running the outcome analysis before the planned fold is complete or the freeze. Add `--planned-n` (default from `family.json` n_rule) and refuse to compute `primary` when rows < planned unless `--allow-partial` is given and logged.

**M6.** Write-once artifacts are overwritten silently: `headroom.py:125` (`family.json`; SAP 8 "run once per rung set"), `fit_threshold.py:60` (`threshold.json`), `detection_frozen.json` (`analyze_gate_m1.py:87`). Refuse if the file exists unless `--force` (and then log it as an amended run).

**M7.** `evidence.py:34-35`: an empty R returns `d = 0.0`, `z = 0.0`; SAP N5 says d and z are NaN when |R| < 2. Only matters for an item whose gate flags everything (not possible at alpha 0.05 unless infeasible) but it would enter S-Z and the headroom rule as a finite zero. Return NaN for both and keep `y = 0`.

**M8.** `analyze_gate_m1.py:36,41,55,86`: `detection_frozen.json` is written when any item has M1 arrays (`have_m1`) and `n_items >= 200`, i.e. possibly with q missing for many items. Require q (the M1 `_D` arrays) for all 200 items before freezing.

**M9.** `folds.verify_tokens` (`run_gate_m4.py:70-71`) is called only in M4 and only written to `folds_check.json`; a mismatch with the runtime tokenizer does not stop anything. Call it in M2, M3 and M5 as well and fail if `n_mismatch > 0` or `n_outside_range > 0`.

**M10.** Stopping rules of the diagnosis that the driver does not apply: lengthen chunks only after four clean 5-minute chunks (`gate_driver.py:44-45` defaults 5 then 15 min); GPU-busy threshold `MEM_BUSY_MIB = 2500` (`driver.py:22`) versus the diagnosis' "under 700 MiB used"; the diagnosis itself is inconsistent on the temperature limit (75 C in the abort list, 80 in "always"); the code follows 80.

**M11.** HOLD is checked once at process start (`runner.py:90`) and per chunk in `gate_driver`; a hold file created mid-chunk is not seen for up to 15 minutes. A per-item `hold.active_holds` call is cheap. The M0 stage 2 and 3 commands call the old probe modules directly and do not check holds (acceptable because the hold is lifted by then, but say so in the M0 checklist).

**M12.** Seeds not as preregistered: bootstrap seed 0 (see section 1). No `numpy` version or seed in output files.

## 4. Safety checklist against the crash diagnosis

| Requirement | Where | State |
|---|---|---|
| Check `runs/P2-PROBE-02/HOLD.txt` (and run-level, `GATE-HOLD.txt`) before any model or CUDA call | `hold.py:18-30`, `runner.py:90`, `run_gate_m0.py:44`, `gate_driver.py:66,72` | met (once per process, once per chunk) |
| Run under `gpu_guard` with 1 s telemetry, `--max-temp 80` | `gate_driver.py:32-35`; M0 commands in the notes | met when launched through the driver; direct `python -m exp_p2.run_gate_m*` bypasses it (cannot be enforced in code; put it in the checklist) |
| Resumable, append per item, arrays before the row, torn tail repair | `runner.py:62-73,151-153` | met; tested (`test_gate_runner.py:54-95`) |
| Memory cap | `runner.py:104-106` | met (0.75, see M2) |
| Whole-GPU memory guard, first-item allowance, rise rule | `guards.py:34-56` | met per item only (M1) |
| AC guard | `guards.py:47` | partly (F3) |
| Slow-item rule | `guards.py:58-63` | met, but the driver retries after it (F1) |
| Throttle, NA, event-log (117, 4101, 105) abort rules | none | missing (M1, F3) |
| Stage plan (0 CPU tests, 1 load/forward/idle, 2 probe-1 control, 3 probe-2 items 21-25) | `run_gate_m0.py`, notes section 2 | stage 1 met; stages 2 and 3 are the old modules (F2) |
| No unattended use | `gate_driver` defaults | procedural; spec 11.5 says ANONYMIZED present |

## 5. Do the tests exercise the behaviours?

Run: `CUDA_VISIBLE_DEVICES="" python -m pytest tests/exp_p2 -q` gives **122 passed in 24 s**.

Strong: CRC threshold equals a brute-force search; empirical false-alarm proportion over 2,000 repetitions with and without ties; geometry gate is a uniform non-zero torus shift; B pass masks and equality with direct forward; K=1 refusal; the nulls depend only on caption length; torn-tail repair and no-gluing; hold stops before a model load; guard logic with injected readings; folds disjoint and the 300/500 prefix property; headroom boundaries (89 vs 90 valid items, T below 2, D* boundaries, blindness assertion).

Weak (tests that run but do not pin the behaviour):
- The M4 analysis test (`test_gate_runners_fake.py:212-244`) asserts keys and shapes (`{"b","c","p","p_holm"} <= set(...)`, `holm_m == 3`), not values. There is no test that a GATE-M loss (c > b) is not counted, that Holm uses p = 1 for an untested member numerically, or of S-Z and S-D2 outputs. I verified the first two by hand (section 1), but a regression would pass the suite.
- `test_slow_item_guard_stops_after_the_item_is_committed` replaces `after_item` with a lambda feeding fixed times, so it tests the runner's reaction, not the median rule (the rule itself is covered in `test_guards_memory_ac_rise_and_slow_item`, which is fine).
- `runner._cuda` is monkeypatched to `None` in every runner test (`test_gate_runner.py:23`), so `set_per_process_memory_fraction`, `reset_peak_memory_stats` and the `peak_gb` row field are never executed. This is a CPU limit, but the call order (cap before load) is unverified.
- No test for the driver's chunk loop (relaunch after exit 75, temperature stop, no-progress stop); only the hold refusal and the command line are tested.
- No test for `--n` vs the n-rule (M3), or for the absence of S-M, S-C and Z_cal (F4, F5).
- Everything that touches the real model (UniScorer layout, VQ encoder, real logits, `l10_once` tolerance 1e-5 in bf16, the codebook attribute path) runs only on the fake network; `l10_once` can raise on the real model and stop M1/M2/M4 at start (it is a deliberate fail-closed).

## 6. What must happen, in order

Before M0 (GPU released, ANONYMIZED present): F3 (AC check in `run_gate_m0` and `run_items` before load; event-log check by hand until coded), confirm M2 with ANONYMIZED (mem-frac and guard thresholds), operator checklist in the notes: AC adapter, other GPU apps closed, launch through `gpu_guard --every 1 --max-temp 80`.
Before M0 stage 3 and M1: F1, F2.
Before M3 or M4 is launched: M3, M4 (frozen file, `--n` vs n-rule), M6 (write-once artifacts), M9.
Before any M4 outcome is analysed: F4, F5, F6, M5, M7, M12, plus numeric tests for `primary`, `s_dn`, `s_z`, `s_m`, `s_c`, calibration and K7.

Re-audit requested after F1 to F6; I will check them against the same SAP sections. I changed no code and did not edit `research/progress.md` (the brief limits the deliverable to this file; the MUST gate is not ticked).
