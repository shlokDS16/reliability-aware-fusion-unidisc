```yaml
agent: lab-engineer
date: 2026-10-28
brief: MUST-tier code of GATE-METHOD-SPEC-v2 section 11 (M1-M5) with CPU tests; no GPU, no model weights, no runner launched, HOLD file untouched
sources_examined:
  - research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md (full), GATE-METHOD-SPEC-2026-10-28.md (v1, sections 0-13 read)
  - research/paper2/probes/PROBE2-CRASH-DIAGNOSIS-2026-10-28.md (section 5, abort rules and staged plan)
  - exp_p2/{scoring,core,common,run_probe1,run_probe2,driver}.py, exp001/runtools.py, tools/gpu_guard.py (head)
coverage: all of v2 sections 4-11 that MUST needs; SHOULD/COULD items are listed under "Not built". Nothing was run on a GPU.
claims:
  - statement: "110 CPU tests in tests/exp_p2 pass (24 s), 96 of them new (test_gate_*.py; the other 14 are the existing probe tests), under the project .venv (Python 3.12, with a copied pytest shim) and under the default python"
    status: supported
    evidence: "command in section 5; output captured this session, not stored in runs/"
    level: E4 (code), not a research result
    confidence: 0.9
  - statement: "Every GPU path (UniScorer layout, tokenizer, VQ encode, real logits, memory, timing) is untested; only the fake network exercised it"
    status: supported
    evidence: section 4
    level: E0 for the GPU path
    confidence: 0.95
```

# GATE implementation notes (M0-M5)

Code is in `exp_p2/gate/` (library) and `exp_p2/run_gate_m{0..5}.py`, `exp_p2/analyze_gate_m1.py` (entry points); tests in `tests/exp_p2/test_gate_*.py` with the
CPU stand-in `tests/exp_p2/fake_gate.py`. Probe 1 and probe 2 code, tests and run directories are untouched (git shows only new files). Commits: c8d8e923,
5b295ee4, ae4d33ff, 9ef850f8 and the last one of this session.

## 1. Spec section to code

| Spec (v2 unless "v1") | What | Where |
|---|---|---|
| v1 3.1-3.3, v2 4.1 | B (K=8 masks, caption masked), C/Lambda (image fully masked, caption visible), D (everything masked, layout only), q = B - D, u = -q in float32, s3 from the B passes, TbV-style observed-position pass, caption-side B (S1) | `gate/scores.py` |
| v1 3.3 "D per n, at most 28" | disk-backed null cache `runs/P2-GATE-DCACHE/` (image null 64 MiB per n, text null), memory-mapped; L10 layout-only check | `gate/dcache.py`, `gate/checks.py: l10_once` |
| v1 5, v2 6, Alg. 3, 4' | CRC threshold, ties by jitter U(0, eps0) at calibration AND test with eps0 = half the smallest non-zero gap of the pooled calibration scores, strict `u > tau`, infeasible alpha (< 1/(n+1)) flags nothing, word units (min piece score) | `gate/calibrate.py`, CPU fit: `gate/fit_threshold.py` |
| v2 4.3, 7.4, Alg. 10 | no gate, geometry-matched random gate (random non-zero torus shift of GATE's own mask), scattered random, changed-code gate, plain-B top-k, s3 top-k, text-side random words | `gate/arms.py` |
| v2 Alg. 5', 7.2 | Delta_j = Lambda^{c+}[v] - Lambda^{c-}[v]; Y = 1[mean_R Delta > 0] (ties wrong); z_R; also d = mean/sd; empty R gives exactly 0; text-direction PMI (probe-1 `afull` layout with gated image tokens masked) | `gate/evidence.py`, `gate/pipeline.py` |
| v2 4.2 | patch texture, neighbour codebook distance, code rarity (leave-one-item-out), s3, plain-B, TbV-style (+ copy-through diagnostic for U7), random; sign-oracle copies (`*_neg`) | `gate/baselines.py`, `gate/detect.py`, `exp_p2/analyze_gate_m1.py` |
| v2 4.3, 7.3 | JPEG q10/q5 and Gaussian noise 0.10/0.20 (identical calls to `run_probe2.corrupt`, tested), splice 128/192, patch and swap (token level), OpenCV `fastNlMeansDenoisingColored` with library defaults | `gate/corruptions.py` |
| v2 7.5 | calibration 300 / headroom 100 / test 300, seeded, disjoint, excluding the 494 probe ids (300 + 200 - 6 shared), 5-32 tokens; deranged negatives restricted to images sharing no annotated COCO category; extension of the test fold to 500 | `gate/folds.py`, `gate/data.py` |
| v2 Alg. 11 | hard negatives: 80-category synonym table written once, same-supercategory replacement not annotated and not mentioned in the five references, number and article handling, skip counts, audit sheet, `apply_audit` with Wilson interval | `gate/hardneg.py` |
| v2 7.3, 9, Alg. 9 | headroom check (ladder walk, H1/H2 at 2 paired SE), `family.json`, discordance scaling and the n_d rule | `gate/headroom.py`, `gate/stats.py` |
| v2 5.3 | Prop. 4 general form, corrected special case, plug-in estimation from per-token Delta | `gate/theory.py` |
| v2 7.1, 7.4, 6 | M4 analysis: McNemar + Holm, mechanism contrasts, realised FAP, precision, FAP on clean tokens of corrupted items, Prop. 4 refutation flag | `gate/analysis_m4.py` |
| v2 7.6, 11.4 | per-item AUROC tables, paired bootstrap of q against the best cheap rival, falsifier; CPU fallback on partial probe-2 data | `gate/detect.py`, `exp_p2/analyze_gate_m1.py` |
| v2 8 | Stouffer and Fisher LDA weights (secondary) | `gate/fusion.py` |
| v2 Alg. 12 | coherence test: pairs, half masks, 3-pass gaps, noise floor, pre-stated reading | `gate/checks.py`, `exp_p2/run_gate_m5.py`, `gate/coherence_report.py` |
| v2 11.1 | M1 post-hoc, M2, M3, M4, M5 item functions; resumable loop (arrays written first, the row is the commit marker; torn tail repaired; failed items logged) | `exp_p2/run_gate_m{1..5}.py`, `gate/runner.py` |
| HOLD, crash diagnosis 5 | project-wide hold check (`runs/P2-PROBE-02/HOLD.txt`, `runs/<run>/HOLD.txt`, `runs/GATE-HOLD.txt`) in every runner and in the driver; per-item guards with the diagnosis thresholds; 1 s telemetry, `--max-temp 80`; M0 stage-1 script | `gate/hold.py`, `gate/guards.py`, `gate/gate_driver.py`, `exp_p2/run_gate_m0.py` |

Row and array budgets per item match the spec's itemisation and are asserted on the fake network: M2 12 passes, M3 2, M4 75 (70 without TbV) with a 3-member
family, M5 24 (+24 on every fourth item), `test_gate_runners_fake.py`.

## 2. Commands (all from the worktree root; GPU commands only after Shlok removes the hold file)

`PY` = `C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe`. Nothing below has been executed.

**M0 (crash-diagnosis stages; Shlok present, AC power, other GPU apps closed).**
```
:: stage 0 (CPU)
set CUDA_VISIBLE_DEVICES=
python -m pytest tests/exp_p2            (the .venv has no pytest; see section 5)
:: stage 1: load, one batch-4 forward, 5 min idle  (refuses while any hold file exists)
PY tools/gpu_guard.py --log runs/P2-M0-STAGE1/telemetry.csv --every 1 --max-temp 80 --max-minutes 12 -- PY -m exp_p2.run_gate_m0 --run-id P2-M0-STAGE1 --idle-minutes 5
:: stage 2: probe 1 control, 10 items into a NEW run dir; run_probe1 unchanged, wrapped by the new guards (hold, AC before load, memory/rise/slow-item rules, 1 s watchdog, cap 0.75, exit 76 on abort)
PY tools/gpu_guard.py --log runs/P2-M0-STAGE2/telemetry.csv --every 1 --max-temp 80 --max-minutes 12 -- PY -m exp_p2.gate.probe1_guarded --run-id P2-M0-STAGE2 --n 10 --limit 10 --soft-minutes 10
:: stage 3: probe 2 items 21-25 (run_probe2 unchanged, wrapped by the new guards: memory cap, AC, memory/rise/slow-item rules, 1 s watchdog; audit F2)
PY tools/gpu_guard.py --log runs/P2-PROBE-02/telemetry-m0s3.csv --every 1 --max-temp 80 --max-minutes 12 -- PY -m exp_p2.gate.probe2_guarded --run-id P2-PROBE-02 --n 200 --resume --limit 5 --soft-minutes 10
```
The diagnosis' source edits to `run_probe2.py` (first-item memory limit, power stop, `MEM_FRAC=0.60`) are NOT made: they change probe 2 and need Shlok's approval. The new
runners carry equivalent guards (`gate/guards.py`). Open point: `MEM_FRAC=0.60` caps PyTorch at about 7.2 GB, below the 8.2 GB peak the probe report measured at
batch 4; I kept the runners' default at 0.75 (`--mem-frac`).

**M1.**
```
PY -m exp_p2.gate.gate_driver --stage p2                      :: completes probe 2 (run_probe2 unchanged) via gate/probe2_guarded.py: new guards, hold check, 1 s telemetry, event-log check between chunks
PY -m exp_p2.gate.gate_driver --stage m1 --extra "--tbv"      :: D at stored codes (<= 28 null passes) + TbV-style pass on the 4 corrupted images; exports the VQ codebook if reachable
python -m exp_p2.analyze_gate_m1 --probe-run P2-PROBE-02 --m1-run P2-GATE-M1      :: CPU: AUROC table, paired q vs best cheap, falsifier, tbv_verdict.json
```
**M2.** `PY -m exp_p2.gate.gate_driver --stage m2` (builds `runs/P2-GATE-FOLDS/folds.json` with the real tokenizer on first use), then
`python -m exp_p2.gate.fit_threshold --run-id P2-GATE-M2` (CPU; writes `threshold.json`, `codefreq.npy`). Commit `folds.json` and `threshold.json` before M4.

**M3.** `PY -m exp_p2.gate.gate_driver --stage m3`, then `python -m exp_p2.gate.headroom --run-id P2-GATE-M3` (CPU; `family.json` with the endpoint decision). Commit
`family.json` before any M4 item is scored. If it says "UNDER-POWERED", decide (500-item test fold via `--n 500` on M4, or z-score primary) and record it before M4.

**M4.** `PY -m exp_p2.gate.gate_driver --stage m4 [--extra "--tbv on"]` (refuses to start without `threshold.json` and `family.json`; `--tbv auto` follows
`tbv_verdict.json`), then `python -m exp_p2.gate.analysis_m4 --run-id P2-GATE-M4 --family-run P2-GATE-M3`.

**M5.** `PY -m exp_p2.gate.gate_driver --stage m5`, then `python -m exp_p2.gate.coherence_report --run-id P2-GATE-M5 --mu <clean mean per-token paired evidence from M4>`.

CPU-only, any time: `python -m exp_p2.gate.cpu_dryrun` (section 5), `python -m exp_p2.analyze_gate_m1 ... --out-dir runs/P2-GATE-CPU/m1_fallback --no-pixels`.
Hard-negative audit: `hardneg.audit_sheet` / `apply_audit` are library calls (no CLI); the reviewer pass itself is not automated.

## 3. Ambiguities and how I resolved them

1. **z does not behave as the spec says under a random gate.** v2 7.2 says a random gate "leaves z unchanged in expectation". With z_R = mean/(sd/sqrt(|R|)) it scales by
   sqrt(1 - g) (tested). So H2 (changed-code gate versus none, which shrinks R) is biased against passing. I kept the spec's z as the default endpoint and also store
   d = mean/sd (size-invariant); `headroom --endpoint d` applies the rule to d. The choice must be fixed before any test item is scored (statistician). This affects the
   family, so it is the most consequential open point.
2. **Denoise arm count.** v2 11.1 counts 2 denoised encodes with a 3-member family. I denoise the jpeg and noise conditions only (`config.DENOISE_FOR`, `--denoise-for`); splice
   has no denoise arm. Denoised codes get the image-direction `none` arm only (no gate), as 4.3 lists denoise and "denoise + GATE-M" (S4) separately.
3. **D is not in the M2 itemisation (12 passes).** Resolved by the null cache: one pass per caption length n, on disk, shared by M1, M2, M4 (at most 28 image nulls and 28 text
   nulls in total). First-use cost is real: the first items of each new n spend 1-2 extra passes.
4. **Text-direction statistic.** Mean per-token PMI (probe-1 `a_full_pmi`, the 0.990 reference), not the sum of Alg. 5 step 3, because c+ and c- have different lengths. Caption
   lengths are stored (`n_tok`, `n_tok_neg`) so the analysis can recompute sums.
5. **Y on ties and NaN.** Y = 1 only if mean > 0 (ties wrong, as Appendix A). z/d are NaN when |R| < 2 or sd = 0; analyses drop non-finite items per test and report the count
   (M4d). Empty R gives exactly 0 with n = 0 (L2).
6. **Seeds.** New `SEED_GATE = 20261029`; per-item key = fold offset (cal 0, head 1000, test 2000) + index, so no two folds share mask partitions. M1 reuses probe 2's own seeds
   because it consumes probe 2's B. The partition seed rule is probe 2's `[SEED, item, 99]`.
7. **Geometry-matched random gate seeds.** 3 seeds for the image-direction arms; the text-direction conditioning arm uses the first seed ("geo seed 1" in v2 11.1).
8. **Text-direction conditioning for the patch sanity condition and denoised copies** is not run (v2 lists it for the 3 realistic corruptions and clean only).
9. **Falsifier (7.6).** "CI does not exclude 0 on JPEG and on noise" read with the intent "q must beat the best cheap baseline": a CI that excludes 0 on the negative side also counts as
   falsified; both lists are reported.
10. **Cheap rivals get a sign oracle.** The patch-texture sign is a free choice, so the analysis adds the negated copy of texture, neighbour distance and rarity and picks the best
    mean AUROC among all (generous to the rivals). Texture is NaN for token-level corruptions (no observed pixels).
11. **Rarity** is leave-one-item-out over the clean codes available (M1: the probe-2 items; M2 writes `codefreq.npy` from the 300 calibration items).
12. **Hard-negative noun choice:** leftmost matched noun whose category is annotated and has a same-supercategory alternative; ambiguous words (orange, plant, bag, bat) are not in
    the table; 'person' items are skipped (single-member supercategory). Replacement display names are written once in `hardneg.CATS`.
13. **Folds need the tokenizer** (5-32 tokens), so they are built inside the first GPU runner (M2) and then frozen; the CPU dry run uses 1.3 x words and is never used as the folds.
14. **Guards are proposals.** `Guards` defaults are the diagnosis thresholds (9,000 MiB; 10,000 MiB first item; +1.5 GB rise; 2x median item time; AC loss). Using them as
    defaults needs Shlok's approval; every value is a CLI flag (`--max-used-mib` etc., `--no-ac-check`).
15. **HOLD scope.** The existing `exp_p2.driver` only reads `runs/<run>/HOLD.txt`, which would not stop a gate run. The gate runners and `gate_driver` also read
    `runs/P2-PROBE-02/HOLD.txt` and `runs/GATE-HOLD.txt`. The hold file lives in the worktree's `runs/`; a run from another checkout has its own `runs/`.
16. **A latent bug in `common.append_jsonl` (not changed):** after a hard kill mid-row, the next append glues onto the partial line and that row is lost on read. The gate runner
    repairs the tail (adds a newline) before appending; probes 1 and 2 still have the issue.
17. **Prop. 1, 6, 7 enumerations (v1 L4, L9) are not tested**: they need the 3^7 toy joint and test the theory, not the code; the brief asked for the limiting cases L1, L2, L3, L5, L6,
    L7, L8, L10, calibration, geometry, resume and HOLD, all covered.

## 4. Not testable without the GPU (all untested)

- `UniScorer.build/encode/selfcheck`, the real tokenizer, `ensure_folds` with real token counts, the real VQ encoder, real bf16 logits.
- Whether `vae.quantize.embedding.weight` exists in UniDisc's VQ wrapper (guess from LlamaGen's layout; absence is logged to `codebook.json` and the neighbour baseline becomes NaN).
- U7: whether UniDisc's logits at unmasked positions are meaningful (the TbV diagnostic `copy_through_stat` runs in M1/M4).
- Real memory (two 64 MiB Lambda matrices on the GPU plus batch-4 logits), real time per row (the 0.15 s estimate), real tie structure of q (hence the real eps0; the `eps0_resolvable`
  flag in `threshold.json` must be True), real fraction of changed codes per rung (decides the family).
- `torch.cuda` guards (`gpu_used_mib`, `set_per_process_memory_fraction`), `gpu_guard.py --every 1`, the staged commands of M0, `run_gate_m0.py` beyond its hold exit.
- Not built (SHOULD/COULD): S1 caption-typo runner (the caption-side score and word-unit helpers exist), S2 re-infill sampler, S3 hard-negative runner (the builder exists), S4 denoise + GATE-M,
  S5 K ablations, S6, E7, T2I, Mondrian, iterated gate, fp32 head.

## 5. Tests and the CPU dry run

```
set CUDA_VISIBLE_DEVICES=
python -m pytest tests/exp_p2 -q                       -> 110 passed in about 24 s (default python 3.14, pytest 9.0.2, torch 2.11)
PY -m pytest tests/exp_p2 -q   with PYTHONPATH=<folder holding copies of _pytest, pytest, pluggy, iniconfig, py>   -> 110 passed (project .venv, Python 3.12)
```
The project `.venv` has no pytest and nothing was installed; the second run used a copy of the pure-Python pytest packages from the default interpreter on `PYTHONPATH` (scratchpad folder).
`tests/test_ex_validate.py` fails at collection on a CRLF hash of `validator-tests.jsonl`; it is unrelated to this work and was not touched.

What the tests pin: CRC threshold equals a brute-force search over every jittered candidate; realised false-alarm proportion of 2,000 calibrate-then-test repetitions is at most
alpha + 3 MC SE, with and without heavy ties (L1); uniform scores give a random gate (L5); jitter never reorders distinct calibration values; geometry-matched gates are non-zero torus
translations, uniform over the 15 shifts on a 4x4 grid; B masks exactly one group plus the whole caption per pass and equals a direct forward; K=1 refused and B == D (L6); K=m equals
leave-one-out (L7); alpha=0 gives the empty gate and bit-identical evidence (L8); independent joint gives A == B, C == D and zero image evidence (L3); all gated gives exactly 0 (L2) and
the text direction equals its null; nulls depend only on caption length (L10); resume appends each item once, arrays precede rows, a torn tail is repaired, failures are logged; a hold
file stops every runner and the driver before a model, a CUDA call or even a run directory exists; the real hold file is not modified; jpeg/noise/swap/patch reproduce `run_probe2.corrupt`
exactly; the power table of v2 section 9 is reproduced (47/29/20 and 63/39/27 with alpha' = 0.0167).

CPU dry runs on real local data, stored under `runs/P2-GATE-CPU/` (exploratory, not preregistered, not research results):
- `m1_fallback/analysis.json` (command: `python -m exp_p2.analyze_gate_m1 --probe-run P2-PROBE-02 --m1-run P2-GATE-M1-NOTHERE --out-dir runs/P2-GATE-CPU/m1_fallback --boot 2000`): 21 probe-2 items,
  no q yet. Mean per-item AUROC against changed-code labels: swap plain-B 0.962, patch plain-B 0.967, r_original 0.495/0.506/0.453/0.504 (swap/patch/jpeg/noise); **jpeg: plain-B 0.543
  (CI 0.495-0.597), s1 0.541, texture with the sign flipped 0.756 (0.704-0.792); noise: plain-B 0.515, s1 0.515, texture sign-flipped 0.774 (0.749-0.803)**. So on these 21 items a pixel-variance
  detector beats the model's own likelihood on the two realistic corruptions; this is the red team's M4 concern in miniature and bears on the v2 7.6 falsifier. n = 21, one seed.
- `cpu_dryrun.json` (command: `python -m exp_p2.gate.cpu_dryrun`): 80-category table equals the instances file; 494 probe ids excluded; folds of 300/100/300 built and disjoint; 100 percent of negatives
  restrictable by category; hard-negative yield 74 of 100 (head) and 228 of 300 (test) with the approximate token counts; skips: no known noun 10 / 37, only 'person'-like or no free
  same-supercategory alternative 14 / 29, noun not annotated 2 / 6. The first 100 of each fold are in `hardneg_audit_sheet_*_first100.jsonl` for the reviewer pass (not yet judged).

## 6. SAP addendum 1 changes (2026-10-28, after the first delivery)

Source: `research/paper2/prereg/SAP-GATE-2026-10-28.md`, "Addendum 1". Tests: 122 pass in `tests/exp_p2` (110 before; 12 net new, several older ones rewritten), under the default
python and under the project `.venv` with the pytest shim. CPU only; nothing was launched; the hold file is untouched.

| Addendum | Change | Where |
|---|---|---|
| A1.1 (a) | Headroom and S-Z endpoint is d (z* = sqrt(m) d = 32 d), default of `headroom --endpoint`; `family.json` records `"endpoint": "d"`; z is computed for every rung and logged under `sensitivity_other_endpoint` only, never changing the family. Rung passes iff n_v >= 90, T1 >= 2, T2 >= 2 on the n_v items with all three values finite. `assert_blind` fails if a row carries a gate/flag field. M4 refuses a `family.json` without endpoint d, and `analysis_m4` refuses it too; `analysis_m4 --endpoint` defaults to d (S-Z with Wilcoxon, z as sensitivity) | `gate/headroom.py`, `gate/analysis_m4.py`, `run_gate_m4.load_prereqs` |
| A1.3 check (b) | n-rule: exact N* = 43 (`stats.exact_sign_min_n(0.75, 0.0167)` reproduces 35/42/43 of SAP Table A), kappa = 0.5, D_c = Y flips between the changed-code gate and none (either direction), D* = max over corruptions with an operating point, scaled x3 (300) and x5 (500) from the 100 headroom items: R1 if D* >= 29, R2 if D* >= 18, else R3 (primary becomes the paired evidence change d, Wilcoxon); no operating point = NO-GO. The spec's normal-approximation `power_nd` stays in `stats` but is no longer used by the rule | `gate/headroom.py: sample_size_rule`, `gate/stats.py` |
| A1.2 / A1.3 N9-N11 (c) | `detect.py`: two-sided paired-bootstrap p, Holm over m = 2 (a corruption without q gets p = 1 and stays in m = 2), CIs at 95 and 97.5 percent; falsifier met if q beats the best rival (sign oracle) on neither corruption at Holm 0.05 with a positive difference; sensitivity (i) rival re-selected inside every resample, (ii) items 21-199 only (the 21 dry-run items excluded; 179 of 200 when M1 is complete). `detection_frozen.json` (rival, base, sign, mean AUROC per corruption) is written by `analyze_gate_m1` only from q and all 200 items. S-D2 on the M4 test items: per-item AUROC of q minus the frozen rival at the M4 rung, p = 1 for a corruption with no operating point or no usable rival, Holm m = 2; rarity uses `runs/P2-GATE-M2/codefreq.npy` | `gate/detect.py`, `exp_p2/analyze_gate_m1.py`, `gate/analysis_m4.py: s_d2` |
| A1.3 N2 (d) | S-DN: exact McNemar GATE-M versus the denoised codes for JPEG and noise only, Holm m = 2 (splice has no denoise arm). While there I also made family P exactly m = 3 with p = 1 for an untested corruption (SAP 2.4), which the earlier code did not do | `gate/analysis_m4.py: s_dn, primary` |
| A1.3 N13 (e) | `runs/P2-GATE-FOLDS/folds.json` generated now with the local Llama-2 tokenizer files (HF cache, offline, no model weights): 300 calibration, 100 headroom, test = ordered list of 500 (`test` = items 1-300, `test_ext` = 301-500), sha1 3dfed9ee90b340a9, 494 probe ids excluded, fast and slow tokenizer agree on all 900 captions. Negatives and splice donors are drawn inside each block, so `test300 == test500[:300]` holds including negatives (property test). `run_gate_m4 --n 500` uses the extension; the old `extend_test_fold` is gone. Runners compare the frozen counts with the runtime `UniScorer.caption_ids` and write `folds_check.json` | `gate/folds.py`, `run_gate_m3.donor_for`, `run_gate_m4` |
| A1.3 N16 (f) | `gate/jsonl.py`: tolerant reader recovers every complete `idx` row from a glued line, counts clean/glued/recovered/unparseable lines, and reports probe-2 items whose arrays exist but whose row is lost; `analyze_gate_m1` writes it as `rows_report`. The strict reader used by the probes is unchanged. Items with arrays and no row stay in the analysis (arrays are written first) | `gate/jsonl.py` |

The CPU fallback output `runs/P2-GATE-CPU/m1_fallback/analysis.json` was regenerated with the new analysis (21 items, no q, so no frozen file; rows report: 21 clean lines, 0 lost).
Run the M3 analysis as `python -m exp_p2.gate.headroom --run-id P2-GATE-M3 --endpoint d` (d is also the default now).


## 7. Code-audit fixes (GATE-CODE-AUDIT-2026-10-28, verdict PASS WITH FIXES)

Commits: SAFE = 5cee34a9, ANA = e03d76a3, MIN = 8704dd2f, plus the notes commit of this section. 166 tests in `tests/exp_p2` pass (144 after SAFE, 166 after MIN). `tools/gpu_guard.py`,
`exp_p2/run_probe2.py`, `run_probe1.py`, `scoring.py` and `driver.py` are unchanged (a test asserts an empty `git diff` for them).

| Finding | Fix | Commit | Tests |
|---|---|---|---|
| F1 guard abort = soft deadline | `runner.EXIT_GUARD = 76` for every guard stop (before-item, after-item, AC before load, watchdog); 75 stays the soft deadline. `gate_driver` stops with exit 8 after exit 76, or after any new `guard_stop` event in `chunks.jsonl` whatever the exit code, and never relaunches | SAFE | `test_gate_safety.py`: distinct codes; no relaunch after 76 even with progress; stop on a logged `guard_stop`; 75 still relaunches |
| F2 probe-2 stage on the old guards | new `gate/probe2_guarded.py` runs `run_probe2.main()` unchanged and installs the guards from outside: hold and AC before the model load (hook on `common.load_net`), memory cap and first-item limit set on probe 2's module globals, a before-item check on probe 2's per-item `torch.cuda.mem_get_info` call (hold, AC, memory 9,000 / 10,000 first item, rise), the slow-item rule on each committed `items.jsonl` row, and the 1 s watchdog. The driver's `p2` stage and the M0 stage-3 command use it. A bug found on the way: argparse prefix matching read `--n` as `--no-ac-check` (it would have switched the AC check off); `allow_abbrev=False` on the wrapper's parsers, with a test | SAFE | healthy pass-through and flag stripping, memory limit after the first item, rise, slow item, AC, AC again before the load, hold mid-run, hooks restored, `run_probe2.py` unmodified |
| F3 AC before the load; event log between chunks | AC checked before `load()` in `run_items`, in `run_gate_m0`, in `probe2_guarded` and before every chunk in the driver. `gate/eventlog.py` reads (read-only, `Get-WinEvent` through PowerShell) System Ids 41, 105, 117, 141, 4101 and Application 1001 only when its text names LiveKernelEvent / nvlddmkm / Bugcheck / BlueScreen, since the run started; the driver checks before every chunk and exits 9 on a hit or when the log cannot be read (fail closed; `--no-eventlog-check` overrides). The query was run once against this machine's real log for the last 3 days: it returned 38 events (the 2026-10-27 unclean reboots and power-source changes) and none since the query time | SAFE | parse and filter, script is read-only, failure reported, per-chunk check, battery refusal |
| M1 gpu_guard cannot enforce memory/power | enforced in our own code, `gpu_guard.py` untouched: `gate/watchdog.py`, a thread sampling whole-GPU memory and AC every second inside every runner and in the probe-2 wrapper; it ends the process with 76 after logging when memory exceeds the limit, rises by more than 1.5 GB between samples, or AC is lost; an unreadable sensor also trips it | SAFE | rules, thread trip, stop, sensor error, default kill path with `os._exit` patched, start/stop also on the abort path |
| M11 hold only at start | `hold.active_holds` before every item in `run_items` and in the probe-2 wrapper | SAFE | hold file created mid-chunk stops before the next item |
| F4 S-M, S-C, K5/K6 | `s_m` (exact McNemar, GATE-M vs `geo0` = seed 1, gatekept by P, m = 3, p = 1 elsewhere; `geo1`, `geo2` as separate unadjusted replications; K5 and K6 flags), `s_c` (clean, m = 1) | ANA | known-outcome synthetic runs in `test_gate_m4_analysis.py` |
| F5 Z_cal and K4 | `z_cal`, `fap_check` (pooled sigma_L over calibration and test items; the calibration losses are rebuilt from the stored jitter seed and reproduce the stored empirical risk exactly), violation iff Z_cal > 2.13 at any alpha, item-clustered CI, `split_replication` (2,000 splits by default, exploratory) | ANA | formula value, 2.13 rule, exact reproduction of the calibration risk, centring of the split replication |
| F6 reporting | `report.report_test`: b, c, n_d, n, both accuracies, (b-c)/n with 95 and 98.33 percent CIs, Clopper-Pearson of theta (checked against scipy), mid-p, 90 percent equivalence check; `completeness_report` (planned vs completed, prefix, covariates, per-arm NaN/empty-R, worst-case first Holm step); K7 raises `PipelineDefect`; `load_items` de-duplicates; `selftest()` runs before the real analysis | ANA | same file |
| M3 `--n` vs the n-rule | `check_n_against_rule`, called in `run_gate_m4.main` before anything is loaded | MIN | R1/R2/R3/NO-GO |
| M4 frozen file required | `pipeline.require_frozen` in the M3 and M4 mains and in the M4 context; `analysis_m4` refuses without it | MIN | mains return 2 before touching a model |
| M5 partial fold | `PartialRun` unless `--allow-partial` (recorded in the output meta) | ANA | tested |
| M6 write-once | `artifacts.write_once` for `family.json`, `threshold.json`, `detection_frozen.json`; `--force` keeps the old file as `.prev-<time>` and logs `amendments.jsonl` | MIN | each of the three CLIs |
| M7 empty R | `d` and `z` are NaN (y stays 0, sum 0) | ANA | `test_gate_scores.py` |
| M8 freeze needs q for all items | `detection_frozen.json` is written only when every one of the 200 items has all four `_D` arrays | MIN | 11 of 12 refuses, 12 of 12 writes, a second write is refused |
| M9 fold tokens | `check_fold_tokens` in M2, M3, M4 and M5; raises on any mismatch or any caption outside 5-32 tokens under the runtime tokenizer | MIN | tokenizer disagreement stops |
| M12 seeds | `seeds.py`: `SeedSequence(20261028)` spawned by analysis name; seed, spawn order and numpy version in every analysis output | ANA | determinism and uniqueness |
| Weak tests | the M4 analysis now has numeric assertions (b, c, p, Holm with p = 1 fill-in, direction, S-M gatekeeping, K5/K6, S-C, S-DN, S-Z, S-D2, completeness, K7); the driver chunk loop is tested with a fake child process | ANA, SAFE | |

Not fixed, by design or by limit:
- **M2** (memory cap and guard thresholds are proposals): needs Shlok's yes; defaults unchanged (0.75, 9,000 / 10,000 / 1,500 MiB, 2x).
- **M1 residual**: the throttle-reason rule and the "nvidia-smi returns NA or takes longer than 3 s" rule of the diagnosis are not enforced (they need nvidia-smi calls from a second process every second; `gpu_guard.py` still logs the throttle bits). **M10** (chunk-lengthening rule, busy threshold 2,500 MiB) is unchanged.
- The event-log check that can REFUSE to relaunch runs in `gate_driver` only. Hand-launched stages (M0 stage 1 `run_gate_m0`, stage 2 `probe1_guarded`, stage 3 `probe2_guarded`) print a one-line event-log summary of the last 12 hours at their start (`--eventlog-hours`, `--no-eventlog-check`); it is informational and does not stop the stage. M0 stage 2 now runs `run_probe1.main()` unchanged inside `gate/probe1_guarded.py` (same wrapper as probe 2; because probe 1 has no memory query per item the before-item check hooks its per-item `torch.cuda.reset_peak_memory_stats()` call, and the memory cap is set by the wrapper), covered by `test_gate_safety.py`.
- Everything that touches a real GPU is still untested: the monkeypatched hooks on the real `run_probe2` (checked by reading it: one `torch.cuda.mem_get_info()` per item, `common.append_jsonl(rows_path, row)` per row, `common.load_net()` once), the watchdog's real kill, the memory-fraction call.


## 8. Card v2 code gaps (F8 / D15, D14, D16) and the U7 fix

Commits: R3 = a1ac5f01, D14 = f16dda8c, D16 = e6e1c902 (the C1 and Wilson helpers `gate/c1.py` and `stats.wilson_ci` were first committed inside f16dda8c), U7 = 8f897235. 188 tests in
`tests/exp_p2` pass. Nothing was run on a GPU, no weights were loaded, no runner was launched, HOLD is untouched.

| Item | What the code does now | Commit | Tests |
|---|---|---|---|
| F8 / D15, rule R3 | `headroom.sample_size_rule` records, for every rule, `primary_endpoint_code` (`Y` for R1/R2, `d` for R3) and `negative_reading_available` (False for R3 and NO-GO) in `family.json`. `analysis_m4.run(..., rule=)` (the rule is read from `family.json` by `main`; `--rule` may not contradict it) routes: under R3 `primary_d` is the primary (Wilcoxon signed-rank on gate minus none of d, labels P1-P3, m = 3 always, p = 1 for a corruption without an operating point, a rejection counts toward the claim only with a POSITIVE mean difference), the McNemar-on-Y family is kept as `secondary_y`, and S-M is gatekept by the active primary. `outcome_reading` implements the SAP A2.2 reading (positive / negative / inconclusive; negative needs no rejection, a 90 percent CI inside (-0.05, 0.05) and n >= 240 for every corruption with an operating point, and is never printed under R3 or NO-GO). Output fields: `rule`, `primary_endpoint`, `negative_available`, `outcome` | R3 | `test_gate_m4_analysis.py`: rule record, d primary with Y flat, wrong-sign rejection does not count, identical data is `negative` under R1 and `inconclusive` under R3, NO-GO, n < 240 |
| D14, real-tokenizer rule | `folds.token_check` + `pipeline.check_fold_tokens`: an item whose RUNTIME count is outside 5-32 is excluded from every analysis, counted, not replaced, order unchanged; more than 10 percent of one fold excluded (or a systematic in-range count mismatch above 10 percent) raises `FoldDefect` (stop and report; the report is on disk first). M2-M5 `get_items` drop the excluded items; `token_exclusions.json` and `folds_check.json` are written per run; the runner writes `effective_n.json` (planned vs effective n) which the early-complete check, `gate_driver`, `fit_threshold` and `headroom` use, so a run with exclusions completes at the smaller n; the completeness report counts `n_excluded_token_rule` and removes them from the planned list. A within-range difference from the frozen count is reported, not excluded | D14 | exclusion, order, no replacement, exactly 10 percent allowed, 13 percent a defect, effective n through runner + driver + fit_threshold, completeness |
| D16, C1 | `gate/c1.py`: clean none-arm accuracy with Wilson 95 percent CI against probe 1's 253/300 and 0.798-0.880; `audit_trigger` = non-overlap (a value above the interval is also flagged, with `above_interval` set, because the SAP says it is "not alarming by itself" while defining the trigger as non-overlap; the operator reads both flags); only the sentence of A2.3 is produced; nothing is tuned. Look (i) after M2 `python -m exp_p2.gate.c1 --look cal`, look (ii) after M3 `--look head`, each recorded once (`c1_<look>.json`); look (iii) is part of `analysis_m4` (`c1_test`) | D16 | numbers, trigger low / high, the three reading paths, one record per look, analysis field |
| D16, chance bar | `detect.chance_bar` in `analyze_gate_m1` output: for plain-B and q on patch and swap, lower 95 percent bootstrap bound of the mean per-item AUROC > 0.5; `failed` / `audit_trigger` on any failure, `passes` None while q is unavailable; the level and the comparison with the rivals stay descriptive | D16 | pass, q missing, plain-B at chance, sign flipped, wide interval, M1 integration |
| U7, TbV-score (non-finetuned) | **Finding: our own TbV pass was already on the raw logits** (`scores` goes through `UniScorer.logits_fn`, i.e. `forward(..., return_logits=True)`, which returns the backbone logits before SUBS; `exp001/unidisc_net.py:134` is not used by any gate code). Renamed `scores.tbv_score_raw_logits` (old name kept as an alias), label `baselines.TBV_LABEL = "TbV-score (non-finetuned)"` carried in the M1 rows, the TbV verdict file, the analysis `labels` and the frozen file; same normalisation as GATE (fp32 log-softmax restricted to the image vocabulary); a result that is exactly 0 at every token is rejected as a SUBS-style output. The only other `forward(` call in `exp_p2` is `UniScorer.selfcheck`, which reads the SUBS reference only at positions it masked first. The caption-observed variant and the TbV-rule variant at a matched edit budget are NOT built: spec v2 4.2 and the SAP list one TbV-style baseline only, so they need a dated amendment first | U7 | `test_gate_tbv.py`: fake network whose SUBS output is exactly 0 at observed positions and whose raw logits vary; raw-logit equality; SUBS path never called; degenerate output raises; AST scan of every `.forward(` call and of the gate imports |

Commands added: `python -m exp_p2.gate.c1 --look cal` right after M2 (before M3 or M4), `--look head` after M3; the chance bar is printed by `python -m exp_p2.analyze_gate_m1 ...`.


## 9. Red-team conditions C2 and C5 (RED-TEAM-SIGNOFF-2026-10-28, N2 and N6)

- **C2 / N2 (commit 21067fe7).** `analysis_m4` now words every printed or recorded label by what was tested: normal route "higher matching accuracy (McNemar on Y)" (`WORDING_Y`), rule R3 "higher per-item mean/sd evidence ratio d (R3 primary)" (`WORDING_D`). The R3 outcome sentence says it tested d, not matching accuracy, and that a rise in d can come from trimming heavy-tailed tokens; the R3 analysis output contains neither "verification" nor "improved" (test-pinned on the whole JSON). The output records `tested_by_primary`, `caveats` (the d-trimming caveat, with the note that only plain-B top-k and s3 top-k, Tier 3, could separate detection from trimming, whenever d is reported; and "S-M under R3 is uninformative" under R3) and `s_m.uninformative_under_R3`. No new test of the caveat itself, as asked.
- **C5 / N6 (commit below).** `python -m exp_p2.gate.denoise_check` (20 COCO images = the first 20 of probe 1's selection, noise sigma 0.10 on [0,1] and JPEG q10 from the experiment's own corruption code) wrote the run directory `runs/P2-GATE-CPU/denoise_check/` (config.json with the rationale, items.jsonl, summary.json, env-lock.txt). Mean PSNR / SSIM against the clean image, noise 0.10: noisy 20.41 dB / 0.344; OpenCV library defaults (h = 3) 20.43 / 0.348 (+0.015 dB, 95 percent CI +0.003 to +0.029, i.e. 0.34 percent of the noise power removed: it does not act); fixed setting h = hColor = 25.5 25.75 dB / 0.689 (+5.34 dB, CI 4.15 to 6.49, 71 percent of the noise power removed); OpenCV tutorial h = 10, reported and not chosen, 24.23 / 0.608. The fixed setting is `config.DENOISE_PARAMS` (h = hColor = sigma in grey levels = 25.5, windows 7 and 21) and is what `corruptions.denoise` and the M4 denoise arm use. It follows the rule of thumb in scikit-image's `denoise_nl_means` documentation ("for a Gaussian noise of standard deviation sigma ... choose h to be sigma or slightly less"), not a grid. **Disclosure:** the library-default gain, h = 10 and h = 25.5 were evaluated once on these 20 images in an exploratory run before the setting was written down; no later adjustment. The card should say the denoise arm is "a sigma-matched non-local-means denoiser", not "library defaults" (spec v2 4.3 says library defaults).
- **Open finding for the coordinator.** The spec requires ONE setting for all corruptions. On JPEG q10 the same setting over-smooths: PSNR 26.82 dB (noisy) to 25.13 dB (-1.69 dB), SSIM 0.761 to 0.674 (library default +0.22 dB, h = 10 +0.27 dB). So the JPEG comparison in S-DN is against an aggressive denoiser; no sigma exists to match for JPEG, so a different a-priori setting is not available without a new rule. Recorded in the run's `summary.json` under `findings`; I did not change `DENOISE_FOR` or add a per-corruption setting.


## 10. Re-audit fixes (GATE-CODE-REAUDIT-2026-10-28, commit a2dda400)

- **W1.** The 1.5 GB rise rule is armed only after the first item of a chunk has completed (`Guards.rise_armed`, set by `after_item`, with a fresh baseline; the same flag gates the 1 s watchdog, which the probe wrappers start before the model load). During the load and the first item only the absolute ceilings (10,000 MiB), AC and (via gpu_guard) temperature apply. Tests: a scripted trace with a 4.2 GB load jump, a 2.6 GB first-item jump up to 9,611 MiB and steady items does not trip; a +2.15 GB jump after items 1 and 2 trips; ceilings still trip during the load; the same rule in the per-item guards and in the probe wrapper with the real hooks. The gate runners start the watchdog after the load and share the same flag. Residual: the later-item ceiling of 9,000 MiB is still a proposal; the stored probe-2 telemetry exceeds it only at the first-item peak (9,611 MiB) and at the 12,087 MiB crash sample.
- **N1.** `python -m exp_p2.gate.c1 --look test` refuses (exit 2, nothing written) unless the M4 fold is complete: expected n = the n-rule test fold from family.json (300 if absent) minus real-tokenizer exclusions (`effective_n.json`).
- **N4.** `gate/pins.py`: a pin check passes if the committed blob or the CRLF-normalised working copy hashes to the pin; `gate_driver` checks `tools/gpu_guard.py` against `runs/EXP-001/gates/manifest.json` before any launch and refuses with exit 10 on a mismatch. `gpu_guard.py` is not edited. `exp003/manifest.py` (Paper 1) still hashes raw working-tree bytes and reports a false mismatch on a CRLF checkout; it was not changed.
- The occasional unexplained test failure of earlier runs was found afterwards: the slow-item guard (2x the median of earlier items) tripped on sub-millisecond jitter in `test_run_items_starts_and_stops_the_watchdog`. The rule now also needs an absolute floor (`slow_min_s` = 1 s); real items take 7-10 s. Caught by looping the test 25 times; 30 clean loops and two full-suite runs afterwards.


## 11. Delta-audit N4 (commit 50f6d72e and the slow-item floor commit)

- `pins.check_pin` now needs BOTH: the committed blob hashes to the pin AND the CRLF-normalised working copy equals the committed blob; an uncommitted edit of `tools/gpu_guard.py` fails (test with a temporary git repository), as does a committed change, an untracked copy or a missing file.
- Runners (`run_items`), both probe wrappers, `run_gate_m0` and `gate_driver` refuse to start (exit 11) when `git status --porcelain -- exp_p2 tools` shows any uncommitted, staged, deleted or untracked file, printing the files; `--allow-dirty` overrides, and the run config (`allow_dirty`, `dirty_files`) and `chunks.jsonl` (`dirty_allowed`) record it; the driver passes the flag to the stage and logs it. A git failure counts as dirty (fail closed). The test suite runs with a conftest fixture that reports a clean tree, because the real checkout is legitimately dirty while code is edited; the guard has its own tests.
