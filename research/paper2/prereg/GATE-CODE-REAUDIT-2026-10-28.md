```yaml
agent: gate-auditor
date: 2026-10-28
brief: Re-audit of the GATE MUST-tier code at HEAD 857673b0 (red-team condition C1): F1-F6 and M-findings of GATE-CODE-AUDIT-2026-10-28.md, the new code (R3 routing, D14, C1, chance bar, U7 raw-logit path, guards, watchdog, probe wrappers, event log, exit 76), early outcome reads, gpu_guard pin, suite x3. No GPU, no weights, no runner launched, no code changed.
sources_examined:
  - research/CONTRACT.md; research/paper2/prereg/{GATE-CODE-AUDIT, SAP-GATE (Addenda 1-2), PREREG-GATE-MUST-v2, RED-TEAM-SIGNOFF}-2026-10-28.md
  - research/paper2/method/GATE-IMPLEMENTATION-NOTES-2026-10-28.md (sections 7-9 read in full)
  - exp_p2/gate/{analysis_m4,report,seeds,c1,artifacts,stats,headroom,evidence,runner,guards,watchdog,eventlog,gate_driver,probe1_guarded,probe2_guarded,pipeline,folds,fit_threshold,scores,detect,baselines,corruptions,config,denoise_check}.py
  - exp_p2/{run_gate_m0..m5,analyze_gate_m1}.py, exp_p2/run_probe1.py and run_probe2.py (grep of the hooked calls only), tools/gpu_guard.py, exp003/manifest.py
  - tests/exp_p2/{test_gate_safety,test_gate_m4_analysis,test_gate_tbv,test_gate_denoise}.py (test names and selected bodies)
  - runs/P2-GATE-CPU/denoise_check/summary.json; runs/EXP-001/gates/manifest.json; runs/P2-PROBE-0{1,2}/telemetry-chunk*.csv, chunks.jsonl; models/third_party/unidisc/model.py lines 621-660, 674-690, 780-788
coverage: >
  Not covered: hardneg.py, theory.py, coherence_report.py, cpu_dryrun.py, imgmetrics.py internals; the real-GPU behaviour of every hook, the watchdog and the memory-fraction call
  (untestable on CPU); the card text beyond sections 3, 6, 7, 9, 14 (grep-level elsewhere); novelty and citation files. I did not re-run Appendix A of the SAP.
claims:
  - statement: "The suite passes three times at HEAD: 194 passed in 62.3 s, 194 passed in 59.7 s, 194 passed in 57.7 s (CUDA_VISIBLE_DEVICES empty)."
    status: supported
    evidence: "run in this session, foreground, one after the other. The three background runs I started first wrote an empty output file (shell redirect issue), so I discarded them and re-ran in the foreground"
    level: E4
    confidence: 0.95
  - statement: "tools/gpu_guard.py is unchanged since its only commit (ddbb6e9e) and its committed bytes hash to the pin of the EXP-001 manifest (5ddf7d09...), but the working-tree copy does not (dff4b96c...) because of CRLF line endings."
    status: supported
    evidence: "git show HEAD:tools/gpu_guard.py | sha256sum = 5ddf7d09f1ea830a6a1049b5958974c342cd37a2817e1063e1dbf797d855aa6d = runs/EXP-001/gates/manifest.json gpu_guard.sha256; sha256sum of the checked-out file = dff4b96c56b1aa229699bf056ff37dc893389ba701bedb2bc508fec5a0d1ea50; replacing CRLF by LF in the file gives 5ddf7d09; core.autocrlf=true; git diff fe1f51a7 HEAD -- tools is empty"
    level: E4
    confidence: 0.95
  - statement: "The card v2 pre-launch check still fails against its pin: git diff --quiet 2ab42a6e HEAD -- exp_p2 tools tests runs/P2-GATE-FOLDS exits 1 (29 files, +990/-80). Against 857673b0 it exits 0. SAP, folds and spec v2 SHA-256 equal the card pins."
    status: supported
    evidence: "run in this session; sha256sum b4e0bf57..., 450edb54..., 04470bef..."
    level: E4
    confidence: 0.95
  - statement: "In the two probe wrappers the 1 s watchdog starts before the model load, and the rise rule (1.5 GB between samples) applies to the first item; the stored telemetry shows rises of 4 to 6 GB within one 5 s sample at both moments, so a false trip is likely."
    status: supported (inference from telemetry; not observed on the wrapper)
    evidence: "probe2_guarded.py:121-128 (wd.start() then probe_main()); watchdog.py:34-38; runs/P2-PROBE-02/telemetry-chunk01.csv rows at 20.3 s 1416 MiB, 25.4 s 6997, 30.4 s 4869, 35.5 s 9611, 40.5 s 6239"
    level: E3
    confidence: 0.7
competing_explanations: []
unknowns:
  - "Whether the watchdog, the rise rule and the hooked calls behave on the real GPU as the fakes do."
  - "Whether the crash cause is environmental (the diagnosis' H1/H2); no code can settle it."
next_test: {hypothesis: "W1-W3 below are fixed and card v3 pins the final SHA", intervention: "re-check W1-W3 and the pre-launch command", primary_metric: "all criteria met", falsifier: "any missing criterion", gpu_hours: 0}
```

# Re-audit of the GATE code at HEAD 857673b0 (2026-10-28)

## Verdict: PASS WITH FIXES for "freeze at 857673b0 and run M0 once the GPU is released"

No BLOCKER. Every finding of my first audit (F1 to F6, M1 to M12) is fixed, with a tested change, except three that are decisions or operator rules and are
listed as such (M2, M10, M1 residual). The new code (R3 routing, D14, C1, chance bar, U7, guards, watchdog, wrappers, event log, exit 76) matches the signed rules as far as I
can read it on CPU, and I found no path that reads test outcomes before the planned fold is complete except one CLI (N1). The suite passes three times (194 each).

"Freeze at 857673b0" is **not yet** possible as the card is written. Three things stand between this commit and M0:
- **W1 (MAJOR, code):** the probe wrappers (M0 stage 2 and 3, M1 part 1) start the 1 s watchdog before the model load, and the rise rule applies to the first item of every chunk. The stored telemetry shows 4 to 6 GB jumps inside one 5 s sample at both moments, so a healthy run will probably trip rule `gpu_memory_rise`, exit 76, and the driver will stop with exit 8 (never relaunched). It fails closed, but M0 stage 2 is the run whose outcome decides "environmental or not"; a false trip there would be misread. It needs a code change, hence a new SHA, so fix it before the freeze.
- **W2 (procedural):** card v3 must pin the final SHA, log the 29 changed files since 2ab42a6e as dated amendment rows and drop D14/D15/D16 from "open" (red-team C1). Today the card's own pre-launch command exits 1.
- **W3 (procedural, red team C5):** the denoise arm is not "library defaults" any more, and on JPEG the fixed setting makes the image worse. Card v3 and the S-DN wording must say so.

What this PASS covers: the code as a measurement instrument and its safety wiring. It does not cover the research claim, the card text beyond what is listed, or any real-GPU behaviour.

## 1. Closure of my first audit

| Finding | State | Evidence at HEAD |
|---|---|---|
| F1 guard abort retried | **fixed** | `watchdog.EXIT_GUARD = 76`; `runner._loop` returns it for every guard stop (`runner.py` before-item, after-item, AC before load); `gate_driver.py` stops with exit 8 after 76 or after any new `guard_stop` event whatever the exit code; 75 still relaunches. Tests: `test_gate_safety.py:51,90,97,103` |
| F2 probe-2 stage on old guards | **fixed, with W1** | `STAGES["p2"]` runs `exp_p2.gate.probe2_guarded`, which runs `run_probe2.main()` unchanged: hold and AC before `common.load_net`, cap and first-item limit on probe 2's own globals, before-item hook on its per-item `torch.cuda.mem_get_info`, slow-item rule on each committed row, watchdog. I read `run_probe2.py` (lines 121, 123, 149, 195): the hooked calls are all made through the `torch.cuda` / `common` attributes at call time, so the hooks bind. `test_run_probe2_file_is_not_modified_by_this_work` (git diff on probe 1/2, scoring, driver, gpu_guard) |
| F3 AC before load; event log | **fixed** | AC before `load()` in `run_items`, `run_gate_m0`, wrappers, and before every chunk in the driver; `eventlog.py` (read-only PowerShell; Ids 41, 105, 117, 141, 4101; Application 1001 only if it names LiveKernelEvent/nvlddmkm/Bugcheck/BlueScreen); driver exit 9 on a hit or an unreadable log (fail closed). Hand-launched stages print a one-line summary only (informational) |
| F4 S-M, S-C, K5/K6 | **fixed** | `analysis_m4.s_m` (exact McNemar GATE-M vs `geo0` = seed 1, gatekept by the active primary, m = 3, p = 1 elsewhere, `geo1`/`geo2` as unadjusted replications, K5, K6), `s_c` (m = 1). Numeric tests `test_gate_m4_analysis.py:211,236` |
| F5 Z_cal, K4 | **fixed** | `z_cal`, `fap_check` (pooled sigma_L over calibration and test, violation iff Z_cal > 2.13 at any of three alphas), `cal_losses` recreates the calibration losses from the stored jitter seed in the same order as `fit_threshold` (I checked the draw order), `split_replication` |
| F6 reporting | **fixed** | `report.report_test`: b, c, n_d, n, accuracies, (b-c)/n, 95/98.33/90 percent bootstrap, Clopper-Pearson, mid-p; `completeness_report` (planned vs completed, prefix, covariates, worst case, K7 raises); `load_items` de-duplicates; `selftest()` runs in `main` before real data |
| M1 gpu_guard enforces only temperature | **partly** | memory above limit, rise, AC loss, unreadable sensor are enforced by the in-process watchdog (`gpu_guard.py` untouched, as its pin demands). Throttle-reason and `nvidia-smi` NA/slow rules are still operator-enforced (card 11b, D10). See W1 for the rise rule |
| M2 mem-frac and thresholds | **open: decision** | defaults unchanged (0.75; 9,000/10,000/1,500 MiB; 2x). They need Shlok's yes and a change-log row before M0 (red team C6) |
| M3 `--n` vs rule | **fixed** | `run_gate_m4.check_n_against_rule` before anything loads |
| M4 frozen file required | **fixed** | `pipeline.require_frozen` in M3, M4 mains and M4 context; `analysis_m4.main` refuses without it |
| M5 partial fold | **fixed** | `PartialRun` unless `--allow-partial` (recorded in `meta`); K7 checked first |
| M6 write-once | **fixed** | `artifacts.write_once` for `family.json`, `threshold.json`, `detection_frozen.json`; `--force` keeps `.prev-<time>` and logs `amendments.jsonl` |
| M7 empty R | **fixed** | `evidence.py`: d and z NaN, y = 0 (I ran it: `d` of an empty set is `nan`) |
| M8 freeze needs q for all items | **fixed** | `analyze_gate_m1.py`: `n_items_with_q >= 200` required |
| M9 fold tokens | **fixed, superseded by D14** | `pipeline.check_fold_tokens` in M2 to M5 (see section 2) |
| M10 chunk lengthening, busy threshold 2,500 MiB | **open (unchanged)** | `gate_driver` still 5 then 15 min; `driver.MEM_BUSY_MIB = 2500` vs the diagnosis' 700. Set `--first-chunk-min`/`--chunk-min` and check `nvidia-smi` by hand, or accept |
| M11 hold only at start | **fixed** | `hold.active_holds` before every item (runner and wrapper hook); test `test_hold_created_mid_chunk_stops_before_the_next_item` |
| M12 seeds | **fixed** | `seeds.py`: `SeedSequence(20261028)` spawned by analysis name; seed list and numpy version in every analysis output; appending-only spawn order |
| Weak tests | **fixed** | numeric M4 analysis tests; driver chunk loop with a fake child; hook restoration tests. Still mocked: `runner._cuda`, so the memory-fraction call and `peak_gb` are not executed |

## 2. The new code against the signed rules

**R3 routing (SAP 4.6, A2.2; card D15).** `headroom.sample_size_rule` records `primary_endpoint_code` and `negative_reading_available` in `family.json`; `analysis_m4.main` takes the rule from `family.json` and refuses a contradicting `--rule`. `primary_d`: Wilcoxon signed-rank on gate minus none of d, labels P1 to P3, m = 3, p = 1 for a corruption without an operating point, rejection counts only with a positive mean difference. Y moves to `secondary_y`; S-M is gatekept by the active primary and marked `uninformative_under_R3`. I ran synthetic cases: d up, Y flat gives P1 p_holm 1.8e-50, `positive`; d down gives no claim and `inconclusive` (not `negative`); identical data gives `negative` under R1 and `inconclusive` under R3; an empty family gives `inconclusive` under NO-GO. `outcome_reading`'s negative rule (no rejection, 90 percent CI inside (-0.05, 0.05), n >= 240 for every corruption with an operating point) matches A2.2. Red-team C2 wording: the R3 sentence says it tested d, not matching accuracy, and that trimming heavy tails can raise d; the d-trimming caveat is recorded whenever d is reported; test-pinned that the R3 output has no "verification" or "improved". **Matches.**

**D14 (A2.1 item 2).** `folds.token_check` excludes items whose runtime count is outside 5 to 32, counts them, does not replace, keeps order; a fold with more than 10 percent excluded (or in-range mismatches above 10 percent) is a `FoldDefect`. I ran it: 10 of 100 allowed, 11 of 100 a defect. The runner writes `effective_n.json`, which the early-complete test, driver, `fit_threshold` and `headroom` use; `completeness_report` removes excluded ids from the planned list and counts them. **Matches.**

**C1 and the chance bar (A2.3, A2.5).** `c1.c1`: Wilson interval (253/300 reproduces 0.7979 to 0.8801), trigger = non-overlap with 0.798 to 0.880, only the A2.3 sentence is produced; looks (i) and (ii) by CLI, recorded once each; look (iii) inside `analysis_m4.run`. `detect.chance_bar`: lower 95 percent bootstrap bound of the mean per-item AUROC above 0.5 for plain-B and q on patch and swap, `passes` None while q is missing, failure only triggers the audit. **Matches**, with N1 and N2 below.

**U7.** I read the UniDisc source: `forward(..., return_logits=True)` returns the backbone logits before `_subs_parameterization` (model.py 780-788); `scoring.UniScorer.logits_fn` passes `return_logits=True` (scoring.py:111). `scores.tbv_score_raw_logits` reads those logits, normalises as GATE does, rejects an all-zero output, and the arm carries the label "TbV-score (non-finetuned)" in rows, verdict and frozen file. The AST test asserts that no other `forward(` call in `exp_p2` reads the SUBS output. **Matches** (E3: source read, not run).

**Guards, watchdog, wrappers, event log, exit 76.** As in section 1, plus: watchdog rules (absolute limit with the first-item allowance, rise, AC, unreadable sensor fails closed) and the default trip (`os._exit(76)` after an fsynced `guard_stop` event) are unit-tested with injected readers; a torn row after `os._exit` is handled by `repair_torn_tail`. `probe1_guarded` reuses the wrapper with the hook on `reset_peak_memory_stats` (probe 1 has no memory query) and sets the cap itself. `--n` can no longer be read as `--no-ac-check` (`allow_abbrev=False`; good catch by the engineer).

**Early outcome reads.** None in the runners, driver, watchdog or `chunks.jsonl`. `analysis_m4.main` refuses an incomplete planned fold (K7 first, then `PartialRun`); the only way round is `--allow-partial`, which is written into `meta`. One exception: N1.

## 3. Findings

### BLOCKER
None.

### MAJOR

**W1. Watchdog false trips at the model load and at the first item (fix before the freeze).**
- `probe2_guarded.py:121-128`: `wd.start()` is called, then `probe_main()` (which loads the model through the hooked `common.load_net`). The first sample is the idle GPU (1,416 MiB in the stored telemetry), the load moves it to about 5.6 GB. `watchdog.py:34-38` applies the rise rule (`max_rise_mib` 1,500) at every sample, including this one.
- `runner.default_watchdog` is started after `load()` in `run_items` (fine), but the rise rule also applies during the first item of every chunk. The stored 5 s telemetry has 4,869 to 9,611 MiB inside one 5 s window at the first item (probe 2 chunk 1, rows 30.4 s and 35.5 s). With 1 s samples a +1.5 GB step is likely, and the first-item allowance (`first_item_active`) relaxes only the absolute limit, not the rise.
- Effect: exit 76, driver exit 8, never relaunched; at M0 stage 2 this would be reported as a guard abort on the control run.
- Not tested: the wrapper tests inject a no-op watchdog, and the watchdog tests use scripted readings.
- Fix: (a) in the wrappers, start the watchdog from a hook on `common.load_net` after it returns (or reset `_last` after the load); (b) in `Watchdog.check_once`, skip the rise rule while `first_item_active` (the absolute 10,000 MiB limit still applies), or allow a first-item rise up to the first-item limit; (c) add a test with a scripted load (0, 5,600 MiB) and a first-item (5,000, 8,200 MiB) sequence that must not trip, and one with a 12,000 MiB jump that must. If the team prefers not to change code, the alternative is an explicit change-log row with `--max-rise-mib 6000` for M0 stages 2 and 3 and M1, which weakens the rule for all items; I do not recommend it.

### MINOR

**N1.** `c1.py` `LOOKS` includes `test`, so `python -m exp_p2.gate.c1 --look test` can read the clean none-arm Y of a partial M4 run. A2.3 says look (iii) only at the analysis step after the fold is complete. Fix: remove `test` from the CLI choices (the analysis path already computes it).

**N2.** `c1.audit_trigger` is true for a Wilson interval entirely above 0.880 as well; A2.3 says such a value "is not alarming by itself". The code sets `above_interval` and the notes say the operator reads both. Acceptable; say it in the operator checklist.

**N3.** `gate_driver` checks the event log "since the driver started" (`started = datetime.now()`), not since the last launch or since the last crash, and the hand-launched M0 stage 1, 2, 3 print only an informational line over 12 hours. So an event that happened before the driver started is not a stop condition. Card 11b already says the hand-launched stages are operator-checked; keep that sentence.

**N4. gpu_guard pin.** The committed file is byte-identical to the pinned one (blob SHA-256 5ddf7d09... = `runs/EXP-001/gates/manifest.json`; no commit touches it since ddbb6e9e). The checked-out copy in this worktree has CRLF line endings (`core.autocrlf=true`) and hashes to dff4b96c.... Anything that hashes the working-tree bytes (for example `exp003.manifest.reused_check()` on this checkout) will report a mismatch that is not a content change. Fix: hash `git show HEAD:tools/gpu_guard.py` in the pre-launch check, or add `tools/gpu_guard.py text eol=lf` to `.gitattributes`.

**N5. Denoise arm (red-team C5, partly met).** `runs/P2-GATE-CPU/denoise_check/summary.json` reproduces the notes: at noise 0.10 PSNR 20.41 dB (noisy), 20.43 (library default, 0.34 percent of the noise power removed), 25.75 (fixed h = hColor = 25.5, 71 percent removed). At JPEG q10 the same fixed setting lowers PSNR from 26.82 to 25.13 dB and SSIM from 0.761 to 0.674 (library default +0.22 dB). So (i) N6's condition "acts at both corruptions" is met for noise only, and was measured by PSNR/SSIM, not by the changed-code fraction or evidence gap; (ii) the setting was chosen after one exploratory evaluation of three candidates on 20 images (disclosed in the notes); (iii) spec v2 4.3 and card text still say "library defaults". S-DN on JPEG compares GATE-M with an aggressive denoiser that harms the image, which favours GATE-M. Fix in card v3 (W3): call it "a sigma-matched non-local-means denoiser (h = 25.5)", state the JPEG finding next to S-DN, and add an amendment row for the change of the spec's parameter. No code change.

**N6.** `run_gate_m0` (stage 1) has no watchdog and no per-second memory rule (only `gpu_guard` temperature and the operator's eye). It is a load, one forward and an idle; accept, but say it in the checklist.

**N7.** `chunks.jsonl` has no torn-tail repair (only `items.jsonl` has). Harmless: events are read leniently.

## 4. Pre-freeze checklist (what I would check again)

1. W1 fixed with the three tests; suite green three times.
2. Card v3: pin = the final SHA; `git diff --quiet <pin> HEAD -- exp_p2 tools tests runs/P2-GATE-FOLDS` exits 0; dated amendment rows for the commits after 2ab42a6e (a1ac5f01, f16dda8c, e6e1c902, 8f897235, cd861649, 21067fe7, 857673b0, plus the W1 fix), each saying: test-pinned, no outcome path touched; D14/D15/D16 closed; denoise wording (N5); gpu_guard hash done on the committed blob (N4); SAP, folds, spec SHA-256 re-computed (they equal the current pins).
3. Shlok's yes on D2/D3 (mem-frac 0.75, guard thresholds, 80 versus 75 C) as a change-log row before M0 (M2, red-team C6).
4. N1 removed or documented.
5. HOLD.txt is still present (`runs/P2-PROBE-02/HOLD.txt`); I did not touch it.

I changed no code. I did not edit `research/progress.md` and ticked no gate: this is a code re-audit, not the MUST gate. The re-audit covers the code at 857673b0 only; any later code commit (including the W1 fix) needs a short delta check.


## Delta audit 164a18a5 (2026-10-28)

Scope: commits 857673b0..164a18a5 (code in a2dda400; 164a18a5 is notes only). `git diff --stat 857673b0 164a18a5 -- exp_p2 tests tools` touches exactly 9 files: `exp_p2/gate/{c1,gate_driver,guards,pins,watchdog}.py` and four test files. Nothing else under `exp_p2`, `tools` or `tests` changed, so no other behaviour changed. `tools/gpu_guard.py` is still untouched. HEAD is now 38116efd (card v3 only; `git diff 164a18a5 HEAD` is that one file). Suite at HEAD, one run: **202 passed in 66 s** (`CUDA_VISIBLE_DEVICES=""`). Code directories have no uncommitted changes.

| Fix | Correct? | Tested? |
|---|---|---|
| **W1 rise rule** | Yes. `Guards.rise_armed` starts False; `after_item` of the first item arms it and clears `_last_used`, so the first armed reading only sets the baseline; `Watchdog.check_once` does the same with `_armed_seen`. Until then only the absolute ceilings apply (10,000 MiB via `first_item_active`, which is True from construction, so the model load in the probe wrappers is under the first-item ceiling and AC is still checked). After item 1 both the 9,000 MiB ceiling and the 1.5 GB rise rule apply. The probe-wrapper path arms through the hooked `append_jsonl` row, the runner path through `after_item`. | Yes: a 0 -> 5.6 GB load jump and an 8.2 GB first-item spike do not trip; a +2 GB jump after a completed item does; an 11,000 MiB breach during load still trips; per-item guards and the runner share the rule; wrapper test with the watchdog started before the load does not trip. |
| **N1 c1 `--look test`** | Yes. Refuses (exit 2) unless `done >= expected_test_n()`, i.e. the n-rule's `test_fold` from `family.json` (300 if absent) lowered to `effective_n.json` after real-tokenizer exclusions; it counts distinct `idx`. | Yes (`test_gate_m4_analysis.py`, +21 lines: partial refused, complete accepted). |
| **N4 gpu_guard pin** | Partly. `pins.check_pin` passes if the committed blob OR the CRLF-normalised working copy matches; the driver stops with exit 10 on a mismatch. It fixes the false CRLF mismatch (the real file passes: blob 5ddf7d09...). **Hole:** because either side is enough, an uncommitted edit to the working-tree `gpu_guard.py` still passes (I reproduced it in a temporary repo: working copy edited, `ok = True via committed blob`). The test even records this ("the pin check reads the blob"). The docstring "a real content change fails both" is true only for committed changes. The card's pre-launch check has the same property: `git diff --quiet <pin> HEAD` compares commits, not the working tree. | The CRLF, blob and driver-exit-10 paths are tested; the working-tree-edit case is not. |

### Verdict: PASS for freezing at 164a18a5

W1 and N1 are fixed and tested. N4 solves the problem it was raised for (false mismatch on CRLF) and the freeze is clean today, so it does not block. Recommended before M0, none of which changes measurement code:
- Operator step (or card line): run `git status --porcelain -- exp_p2 tools tests runs/P2-GATE-FOLDS` (or `git diff --quiet HEAD -- exp_p2 tools tests`) as a fifth pre-launch command, so that an uncommitted edit cannot run under the frozen SHA.
- If `pins.py` is touched again: make `ok` depend on the normalised working copy matching the pin (the file that actually runs), and report the blob only as information. That is a new SHA and needs a card row.
- Still open from the re-audit and not code: D2/D3 values as a change-log row (M2), N2 and N3 wording, N5 denoise wording in the card (the v3 card should carry it; I did not re-read v3 beyond sections 14 and 17).


## Delta audit 623faaff (2026-10-28)

Scope: 164a18a5..623faaff. Code files changed (`git diff --name-only 164a18a5 623faaff -- exp_p2 tools`): `gate/{gate_driver,guards,pins,probe2_guarded,runner}.py` and `run_gate_m0..m5.py`; tests: `test_gate_safety.py` and a new `conftest.py`. HEAD is d24d033e, but `git diff 623faaff HEAD` touches only the card (research/), so the code is the same. The code directories and `runs/P2-GATE-FOLDS` have no uncommitted changes (`git status --porcelain` empty). Suite, one foreground run: **209 passed in 69.8 s**.

| Check | Result |
|---|---|
| **Pin check needs blob and working copy (N4)** | **Correct.** `pins.check_pin`: `ok = (committed blob == pin) and (CRLF-normalised working copy == committed blob)`. A CRLF checkout of the pinned bytes passes; an uncommitted edit, a committed change, an untracked copy and a missing file fail. My earlier hole (uncommitted edit passes) is closed; the test now asserts exactly that case, plus "restored: passes again". `tools/gpu_guard.py` is untouched. |
| **Dirty-tree refusal (exit 11)** | **Correct.** `git status --porcelain -- exp_p2 tools` (modified, staged, deleted, untracked; any git failure returns one error line, so it fails closed). `runner.run_items` checks it after the hold check and before `init_run` (nothing is created, no model touched); `probe2_guarded` (and through it `probe1_guarded`), `run_gate_m0` and `gate_driver` check it too; the driver passes `--allow-dirty` on to the stage, and every runner main forwards it. `--allow-dirty` is recorded: `allow_dirty` and `dirty_files` in the run config, a `dirty_allowed` event in `chunks.jsonl` (stage-0/driver/wrapper variants likewise); a clean run records nothing extra. Tested: file listing on a temporary repo, runner, driver (both with and without the flag), wrappers, M0. Limits, not defects: the guard covers `exp_p2/` and `tools/` only (`tests/`, `runs/P2-GATE-FOLDS` and the SAP stay under the card's pre-launch check); `tests/exp_p2/conftest.py` makes every test see a clean tree by patching `pins.dirty_files`, and the tests that exercise the guard patch it back explicitly, so the real-checkout state is never what a test depends on. |
| **Slow-item 1 s floor** | **Changes nothing for real items.** The rule is now `n_prior >= 3 and busy >= 1.0 and busy > 2 x median(prior)`. For items of 7-10 s (and for any item of 1 s or more) the added term is true, so the decision is the old one; only items under 1 s can no longer trip. The new test keeps a real slowdown (2, 2, 2 then 9 s) tripping and shows sub-second jitter (0.0004 to 0.0031 s) not tripping. The floor is a guard-threshold change that the card assigns to D3 (Shlok). |
| **No measurement, scoring or analysis code changed** | **Confirmed.** None of `scores`, `evidence`, `pipeline`, `calibrate`, `arms`, `corruptions`, `headroom`, `analysis_m4`, `detect`, `folds`, `fit_threshold`, `c1`, `report`, `stats`, `seeds`, `analyze_gate_m1` is in the diff; the `run_gate_m*` changes are the added `allow_dirty=a.allow_dirty` argument (M0 additionally logs the dirty list). |

### Verdict: PASS for 623faaff

The three requested properties hold and are tested. Remaining operator points, unchanged: Shlok's D2/D3 values (now including the 1 s floor) as a change-log row before M0; the pre-launch check must pin 623faaff and be run with a clean tree.
