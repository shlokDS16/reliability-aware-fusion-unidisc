```yaml
agent: lab-engineer
date: 2026-10-14/15
brief: Implement and unit-test EXP-001 (card v0.5 SIGNED) up to and including stage-0 gates; run PG-1, PG-V (and the old name PG-2 = PG-V) under the GPU-safety regime. No endpoint data generated.
sources_examined:
  - research/CONTRACT.md
  - research/preregistration/EXP-001-crossmodal-unidisc.md (v0.5; sections 0-9, 10-13, 14, Appendix A-B read; change logs only the v0.4-to-v0.5 table)
  - runs/env-2026-10-14/setup.md and scripts/ (unidisc_setup.py, unidisc_smoke.py, common.py, pardl.py)
  - tools/gpu_guard.py; analysis/framework/check_crossmodal_mixture.py
coverage: >
  Implemented and unit-tested: plan generator, sampler, S_theta estimator (stratified T->I, chunked I->T, floors, wrappers), gate
  pass rules, metric pipeline, H-A and H-C statistics, frozen analysis (label-scrambled), pilot analysis, caption-end and prefix rules,
  PG-V statistic. Run on the real checkpoint: PG-1 (both legs), PG-V (rung 1 and rung 2), PC-F, a train-versus-eval-mode check.
  NOT run: D0 and everything after, D-ref, I2/I3 on the real net, G1-G6, NC-1..NC-8 (other than the toy versions), PC-A, PC-B, PC-D,
  PC-D', the precision block, KID, GPT-2 perplexity. Not implemented: the NC-6' driver, KID pinning, PC-B driver, GPT-2 perplexity, text
  quality secondaries, official-sampler arm O, condition G (guided windows), the Ref-real/Ref-T2I generation drivers, the D3 arm runner
  (the sampler and plans exist; the per-stage runners for D0..D5 do not).
claims:
  - statement: "PG-1 passes at 512 px under condition P (both legs); resolution 512 and position rule P (confidence) are selected."
    status: supported
    evidence: runs/EXP-001/gates/verdict-pg1.json, verdict-pg1g.json, verdict-pg1p.json
    level: E4
    confidence: 0.8
  - statement: "PG-V FAILS at rung 1 (criterion c: m - s = -0.016 against >= 0.25) and at rung 2 (m - s = 0.151); by the card (4.4 ladder, stop rule 11.1) H-B and H-A2 are untestable on this checkpoint under prefix-conditioned completion; no D0 or later stage runs."
    status: supported
    evidence: runs/EXP-001/gates/verdict-pgv-rung1.json, verdict-pgv-rung2.json (24 prefixes x 2 seeds each, J at k0, 512 px, condition P)
    level: E4
    confidence: 0.75
  - statement: "PC-F (checker precondition) passes: m_real 1.00, s_real 0.474, V-lift(Ref-real) 0.893 with 95% interval [0.821, 0.954] (48 real COCO pairs, Qwen3-VL-2B-Instruct)."
    status: supported
    evidence: runs/EXP-001/gates/verdict-pcf.json
    level: E4
    confidence: 0.8
  - statement: "UniDisc's backbone is in eval mode after the repository loaders (config mode eval); a train-mode forward would change the marginals (mean TV 0.072 text, 0.024 image; top-1 agreement 0.78 text) and is guarded by an assertion before every forward."
    status: supported
    evidence: runs/EXP-001/gates/eval_mode_check.json, exp001/unidisc_net.py (assert_eval)
    level: E4
    confidence: 0.9
competing_explanations:
  - "The PG-V (c) failure reflects the coarse OR-over-all-completion-nouns rule with a lenient 2B VLM and shredded-texture images (matched OR-rate 0.71/0.77 against shuffled 0.72/0.62), not an absent text-image link; the per-noun rates (matched 0.307/0.350, cross-prefix 0.216/0.213) show a small positive gap. The registered gate is applied as written."
unknowns: [G1-G6 on the real network; I2/I3 on the real net; the precision block under eval mode; KID pin; whether the orchestrator amends the PG-V criterion or the checker]
next_test: {hypothesis: "none run", intervention: "orchestrator decision on the PG-V failure (stop rule 11.1: feasibility report, or an amendment)", primary_metric: "n/a", falsifier: "n/a", gpu_hours: "about 0.8 compute-hours used by all gates so far"}
```

# EXP-001 implementation and stage-0 gates

Status: **code done and tested (130 tests pass); PG-1 passes; PG-V fails at both rungs, so by the card nothing after the gates is to be run.** Nothing here touches endpoint data: no D0, no arm contrast, no H-A trace.

## 1. Layout

| Path | Content |
|---|---|
| `exp001/` (package, torch/numpy, importable from both venvs) | `config.py` constants; `rng.py` counter-based Philox generator (pool, seed, stream); `plan.py` plan generator; `network.py` Net interface and a toy network; `sampler.py` commit-plan sampler; `estimator.py` S_theta estimator and wrapper nets; `estimator_gates.py` pass rules of G1-G6, NC-3/4, PC-D'; `probe_run.py` probe schedules and a J trajectory with probes; `unidisc_net.py` UniDisc adapter; `gate_gen.py`, `gate_driver.py`, `runtools.py` guarded stage runner; `manifest.py`; `check_eval_mode.py`; `frozen.py` |
| `analysis/EXP-001/` (frozen lists and analysis, eval venv) | Appendix B: `prefix_rule.py`, `caption_end.py`, `nonvisual_nouns.txt`, `spatial_words.txt`, `debris_patterns.txt`, `vlm_prompt.txt`, `vlm_presence_prompt.txt`, `ha_source.py`; also `completion.py` (completion nouns, POS labels of tail tokens, PG-V statistic), `metrics.py`, `hastats.py`, `frozen_analysis.py`, `pilot_analysis.py`, `coco_draw.py`, `evalmodels.py`, `gates_eval.py`. `L_c.txt` is NOT written (it is computed only when PG-V passes) |
| `tests/exp001/` | 130 pytest tests. Command (repo root): `".venv-eval/Scripts/python.exe" -m pytest tests -q` gives **130 passed** (about 16 s, CPU only) |
| `runs/EXP-001/gates/` | manifest, COCO draw, per-stage outputs, telemetry CSVs, verdict files, failed and superseded runs |

Environments: the **generation venv** is the existing `.venv` (torch 2.11.0+cu130, transformers 4.49.0; UniDisc). The **eval venv** is new, `.venv-eval` next to it (same torch wheel, transformers 5.19.0, spaCy 3.8.16 with en_core_web_sm 3.8.0, scipy, pytest); evaluation runs there, offline, after generation (card 9 item 9). Unit tests run in the eval venv. The shim is `runs/env-2026-10-14/scripts/shims/flash_attn/layers/rotary.py` (v2, SHA-256 in the manifest).

## 2. Card section to code

| Card | Code | Tests |
|---|---|---|
| 4.1b caption-end rule incl. e2 | `caption_end.py` + `debris_patterns.txt` (frozen) | `test_caption_prefix.py` |
| 4.2 prefix rule, tagger | `prefix_rule.py` (spaCy en_core_web_sm 3.8.0, UPOS) | same |
| 4.3 PG-1 | `gate_gen.py` (stages pg1g, pg1p, realvq), `gates_eval.py` (pg1g, pg1p, decision table) | run on the checkpoint |
| 4.4 PG-V, PC-F | `gate_gen.py` (pgv), `completion.py`, `gates_eval.py` (pgv, pcf) | `test_completion_pgv.py`; run |
| 4.5 pools, CRN | `config.py`, `rng.py`, `coco_draw.py` | `test_runtools.py` |
| 5.1-5.2 plan generator and arms J, Alt, DA, DA-low, TFJ, Sep_w, TF, IF, J-global, Jd, I2 variant | `plan.py` | `test_plan.py` (54 tests: totals, per-window per-modality budgets at every window boundary, floor-rule counts 1/32, 4/0 then 42/43/43, TFJ 4/32 then 32s, k+ and k-, 256 px, invalid geometry, identities I2 and I3 at plan level) |
| 6 value rule (float64, T=1, no guidance), position rules P and P_rand | `sampler.py` | `test_sampler.py` (counts, confidence rule recomputed independently, ties to the lowest index, float64 inverse-CDF draws, determinism and resume from a mid-trajectory state, probe isolation, I2 and I3 on samples, CRN across arms, P_rand, pooled rule) |
| 7.1-7.3, 10.1-10.2 metrics | `metrics.py` (Lift, psi, C and B terms, paired bootstrap with in-replicate baselines and duplicate-seed exclusion, R5 p-values, Holm, fixed sequence, outcome classes, reading conditions R-a/R-b/R-c, guardrails (i)-(vii), derangements, V-lift) | `test_metrics_stats.py` |
| 8.2-8.4 estimator, probes, cost | `estimator.py`, `probe_run.py` | `test_estimator.py` (probe pass counts 8, 32, 16; D1 128/256 and D2 192/232 passes per trajectory as in 8.4) |
| 8.7 G0 | `test_estimator.py`: naive = I + KL(mbar to p1) to 1e-12 on 500 random models; block J naive 0.08109, mixture 0; finite-R below I_theta in 40/40; stratified identity total = between + within-pad + within-content to 1e-12; known-class toy: stratified (128 per class) and unstratified (R = 256) within 1 percent of the exact I, and both below it at R = 8 |
| 8.7 G2, G3, G3b, floors | `estimator.BlindNet`, `InjectionNet`, `noinfo_floor`; rules in `estimator_gates.py` | toy-network tests (blind gives 0 in both directions; injection: mixture < 1e-10, naive = I_inc; G3b: between-class share >= 0.9, within-content < 1e-10) |
| 8.7 G4, G5, G6, NC-3, NC-4, PC-D' | pass rules in `estimator_gates.py` | `test_estimator_gates.py` |
| 2, 10.3 H-A (composition-standardised pair, thin strata, h guard, condition R table), H-C (exact null) | `hastats.py`, `ha_source.py` | rho_strat null reproduces the card: critical 0.452 (P = 0.0479), P(>= 0.5) = 0.031, P(>= 0.440) = 0.0528, one stratum 0.643 |
| 9 item 11 freeze, 10.5 pilot firewall, 6 dynamic-range gate input | `frozen_analysis.py` (label-scrambled end-to-end, deterministic digest), `pilot_analysis.py` (writes only the allowed fields; sizing rule reproduces n_req = 596 and the chi-square factor 1.0861) | tests; NOT run on data |
| 12.2 GPU safety | `gate_driver.py` + `tools/gpu_guard.py` | see section 5 |
| Appendix B manifest | `exp001/manifest.py` -> `runs/EXP-001/gates/manifest.json` (generation 4) | |

## 3. Frozen lists, pins and the manifest

`runs/EXP-001/gates/manifest.json` (generation 4; generations 1-3 kept as `manifest.prev-N.json`) records SHA-256 of: prefix_rule.py `99920c67...`, caption_end.py, the three lists, the two VLM prompt files, ha_source.py, completion.py, the derangement generators (pi1, pi2 seeds 9101, 9102; PG-V cross-prefix base seed 4401; same-prefix pairing), all analysis and generation code, the COCO draw, shim, gpu_guard. Pins: spaCy en_core_web_sm 3.8.0 (wheel SHA-256 `1932429d...`); **CLIP** openai/clip-vit-large-patch14 rev `32bd6428...` (model.safetensors SHA-256 `a2bf730a...`, equals the HF LFS oid); **VLM** Qwen/Qwen3-VL-2B-Instruct rev `89644892...` (Apache-2.0; model.safetensors `7de1838c...`, equals the LFS oid), measured: loads in 34 s on CPU and runs at about 2.3 s per forward on CPU, 4.3 GB; the VQAScore template is the card's `Is this figure showing "{}"? Please answer yes or no.` and presence template `Is there a {noun} in this image? Please answer yes or no.`; **P(yes)** = two-way softmax of the Yes and No answer logits (case variants pooled), a choice of mine (the card says P(Yes)). **CLIP-IQA**: own implementation of the CLIP-IQA formulation on the pinned CLIP weights (prompts "Good photo." / "Bad photo.", scale 100); the torchmetrics class was not used. **KID/Inception: NOT pinned** (not needed before D3). COCO: val2017 and annotations downloaded from images.cocodataset.org (SHA-256 in the manifest), one caption per image, permuted with seed 777; 3,697 of 5,000 images (73.9 percent) are rung-1 eligible, 3,795 rung-2 eligible; all blocks of 4.5 are filled; `runs/EXP-001/gates/coco_draw.json`.

## 4. Gate results (all numbers are in files under runs/EXP-001/gates/)

**PG-1 (4.3): PASS, resolution 512, position rule P** (`verdict-pg1.json`).
- Guided leg (official sampler, 50 steps, CFG 3.0; 32 clean captions; 512 against 1,024 px; `verdict-pg1g.json`): mean raw matched CLIP 24.22 (512) against 24.64 (1,024); paired difference -0.42 (SE 0.75) >= -2.0; lift 15.36 against 16.34, ratio 0.940 >= 0.8. Pass.
- Condition-P leg (J at k0, unguided, confidence ranking, 16 gate prefixes at 512 and 1,024 px; `verdict-pg1p.json`): (i) median distinct VQ-code share 0.949 against 0.929 for 32 real COCO images at 512 px (threshold 0.465), pass; (ii) mean CLIP-IQA 0.665 (512) against 0.470 (1,024, SD 0.224), threshold 0.358, pass; (iii) near-uniform images: pixel-SD proxy 0 of 16; my visual count from `grid_pleg_512px.png` is **2 of 16** (tile 16 near-white, tile 1 low-contrast), at the registered limit (<= 2), pass. The unguided 512-px images are mostly shredded-texture collages with local structure; the registered screen is a feasibility check only.

**PG-V (4.4): FAIL at rung 1 and at rung 2** (`verdict-pgv-rung1.json`, `verdict-pgv-rung2.json`; J at k0, 512 px, condition P, 24 prefixes x 2 seeds, VLM Qwen3-VL-2B).

| | rung 1 (PG) | rung 2 (PG2) | threshold |
|---|---|---|---|
| (a) share with completion nouns | 0.979 | 0.938 | >= 0.60 |
| (b) m | 0.708 | 0.771 | >= 0.50 |
| (c) m - s (cross-prefix, 4 derangements) | **-0.016** | **0.151** | >= 0.25 |
| (d) median debris share | 0.25 | 0.0625 | < 0.5 |
| m - s_sp (same prefix), 90% cluster CI | 0.000 [-0.063, 0.063] | -0.021 [-0.125, 0.083] | reported |
| per-noun rate matched / cross / same-prefix | 0.307 / 0.216 / 0.265 | 0.350 / 0.213 / 0.279 | reported |
| caption end set by e2 / e1 / cap | 24 / 7 / 17 of 48 | 19 / 6 / 23 | reported |
| mean completion length (tokens), p90 | 22.6, 32 | 24.0, 32 | |
| pad share of the 32-token tail | 0.0 | 0.0 | |

Criterion (c) fails at both rungs; the common-cause line "no measurable co-generation dependence at this rung (PG-V, 24 prefixes)" is logged for both (lower 90% limit of m - s_sp <= 0). **By the card (4.4 ladder; stop rule 11.1) H-B and H-A2 are declared untestable on this checkpoint under prefix-conditioned completion, and no D0 or later stage runs; this is a feasibility result for the orchestrator.** I did not tune anything after seeing these numbers. A reading for the orchestrator (inference, not tested): the OR over about 7 completion nouns is saturated by a lenient 2B checker on collage-like images (shuffled OR-rate 0.72 and 0.62), while per-noun rates do show a gap of 0.09 and 0.14; whether to amend criterion (c) or the checker is an orchestrator decision needing an amendment. L_c: `L_c.txt` not written (written only when PG-V passes); both rungs give the provisional value 16 (the 90th percentile completion length is 32, bounded to 16).

**Reported alongside (descriptive; both rungs):** share of passes 2 and 6 whose committed text token is state-pad or post-caption: rung 1 0.125 and 0.208, rung 2 0.083 and 0.208 (the registered falsifier of v0.3: below 0.3, so the v0.3 source would have been adequate). Share of trajectories with an H-A source (L_c = 16) at passes 1, 2, 6, 26, 30: 1.00, 1.00, 1.00, 0.50, 0.33 (rung 1) and 1.00, 1.00, 1.00, 0.35, 0.27 (rung 2); mean w is at most 1.2e-3 everywhere. D-ref (the empty-prompt reference) was not run.

**PC-F (checker precondition): PASS** (`verdict-pcf.json`): m_real 1.000, s_real 0.474 (m - s 0.526 >= 0.40), V-lift(Ref-real) 0.893, 95% interval [0.821, 0.954]. Note the OR rule saturates for real captions too (shuffled 0.47), consistent with the PG-V reading above.

**Dynamic-range gate input:** `pilot_analysis.py` is ready (J's completion increment with its bootstrap SE, the fork at 1.0 point); it needs D0 data and was not run.

## 5. GPU safety, timing, telemetry

All GPU work ran as `exp001/gate_driver.py` chunks inside `tools/gpu_guard.py` (85 C, 3 strikes, 15-minute chunks, first chunk of each stage 5 minutes, telemetry CSV per chunk: `runs/EXP-001/gates/telemetry-*.csv`), with a per-unit duty sleep equal to the unit's compute time (busy equals idle in every stage log), batch size 1, a 2-minute pause between chunks, and a wait for no other compute process and temperature under 65 C before each chunk. **No exit 90 occurred** (maximum GPU temperature 83 C in the 64-sample guided stage, 73-75 C in the others; throttle share 0). The repro-engineer's MDLM jobs were on the GPU for long periods, so my stages started in gaps and waited otherwise; my driver cannot exclude that their next chunk started while mine ran (no overlap was observed in the telemetry memory columns of my chunks except as recorded, which I did not audit chunk by chunk).
- **Measured t_b (one executed J pass at 512 px, including all float64 sampler arithmetic and selection, passes 4-32): median 0.099-0.101 s, mean 0.099-0.101 s, p95 0.103 s, max 0.118 s** (PG-V rungs 1 and 2, 1,392 passes each; PG-1 condition-P leg 464 passes: 0.099 s). At 1,024 px: median 0.475 s. The planning values were 0.129 s (upper) and 0.09 s (expected); the planning t_b is therefore not binding. Official guided sampler (50 steps, CFG 3.0): 10.4 s per sample at 512 px, 51.4 s at 1,024 px.
- **Mean GPU power: 116-130 W over samples with utilisation above 20 percent; 60-64 W averaged over whole stages including the duty-cycle idle** (`telemetry_summary.json`). Mean SM clock while busy 2,377-2,559 MHz. Wall-to-compute ratio about 2.0 by construction of the duty cycle plus model loads (about 20 s per chunk).
- Total GPU compute spent on the gates: roughly 0.8 hours (guided stage 0.55 h of compute = 32 x 10.4 s + 32 x 51.4 s, plus about 0.25 h for the condition-P legs, PG-V rungs, the real-image encodes and the eval-mode checks; wall time about twice that).

## 6. Incidents, failed and superseded runs (all kept on disk)

1. **Coordinator message about dropout.** I checked UniDisc: the backbone has dropout 0.1 in its config and `Diffusion` is not an `nn.Module`; the loader sets `backbone.eval()` because the experiment list contains `eval_unified` (mode eval). `check_eval_mode.py` (`eval_mode_check.json`) shows `training` is False after the build, two eval forwards are bit-identical, and a train-mode forward would differ materially (max abs diff between two train-mode forwards 0.12 text and 0.019 image; mean TV against eval 0.072 and 0.024; text top-1 agreement 0.78). I added `assert_eval()` (every submodule of the backbone not in train mode) before every forward and around the official sampler. The first 28 condition-P-leg units (before the assertion existed) are in `_pre_eval_assert_runs/`; after the assertion the stage was rerun and **27 of 27 comparable units are token-identical**, so none of the earlier gate outputs was produced with dropout on. The setup.md figures for UniDisc bf16 against fp32 (0.96-0.97) remain unverified until the precision block of 8.7 is run in eval mode at the pilot (not run here). Tries 1 and 2 of the eval-mode check failed for code reasons (`Diffusion` has no `.eval`; the train-mode branch uses `compiled_flex_attention`, which the SDPA patch does not cover); logs in `_pre_eval_assert_runs/`.
2. **Layout bug, found through PG-V try 1.** The official demo layout `PROMPT + " " + <m>*32` is tokenised by Llama-2 SentencePiece as `[..., 'a', '▁', <m>...]`: a lone space token right before the tail, after which the model continues with a digit (try 1: non-empty share 0.375, m 0.29, m - s 0.07, median debris 0.97, FAIL; `_try1_lone_space_token/`). I verified the tokenisation directly (ids 263, 29871, 32000 against 263, 32000), changed `prompt_text` in the frozen `prefix_rule.py` to `PREFIX + "<m>"*32` (no space), reran the condition-P leg of PG-1 (also passes in try 1) and PG-V (results above). The change was made before looking at any rung-1 result of the corrected layout and for a reason found by token inspection, but it **is a second PG-V run and a change to a file hashed before PG-V**; manifest generations 2 and 3 record the hashes before and after. The orchestrator should decide whether this needs a note in the card (the card leaves the "leading space convention" to the pinned code).
3. **Killed and discarded.** I stopped the first pg1p/pg1g driver chain myself (item 1) and a pg1g attempt that failed on `n_txt = 0` in `unidisc_smoke.build_state` (retried by the driver three times, 55 s each; logs in `_pre_eval_assert_runs/pg1g_failed_n_txt0/`). I deleted `driver-all.log` once by mistake; its content was one line (`realvq` exit 0, `pg1p` exit 0 at 21:56:08), recreated by later runs. Smoke runs: `_pre_eval_assert_runs/pg1p_smoke`, `pg1g_smoke`.
4. Downloads: CLIP 1.71 GB and Qwen3-VL-2B 4.26 GB (about 1.5 MB/s with a parallel range downloader; the stock hub client stalled), COCO 0.25 + 0.82 GB. No ledger rows written.

## 7. Deviations, ambiguities, things to read before relying on this

- **Names.** The card v0.5 has PG-1 and PG-V only. "PG-2" in the brief is the v0.2 name that became PG-V (change log v0.2); "PG-3 plan-generator tests" I took to be the stage-0 plan-generator tests and identities I2 and I3 of 8.8 (no gate of that name exists).
- **Debris share counts the terminator.** By the literal rule 4.1b the terminating token sits at index e and is not in P, so it counts as debris; a clean caption therefore has debris share at least 1/32. I implemented the literal rule.
- **Tails are not padded.** Pad share of the 32-token tail is 0.0 in all 96 PG-V samples: the model fills the tail with caption-style text (web-caption flavour: place names, dates, photographer credits), so e0 never fires and the caption end is set by e2/e1/the cap. This is an observation about the card's assumption "most of the tail is post-caption [A]".
- **Completion nouns use word-initial tokens** via character alignment of the detokenised caption; punctuation attached to the previous word is a continuation (excluded from POS typing). The tail typing function exists and is tested but was not applied to any trajectory.
- **Probe resolution of toy tests.** G1a (batch composition) has a rule function but no real-net run; G2-G6, NC-1..NC-8 and PC-D' are unit-tested on a toy network only; their real-net execution belongs to D0 and was not run, as instructed.
- **Not implemented** (listed under `coverage`): KID pin, GPT-2 perplexity, the NC-6' driver, PC-B, arm runners for D0-D5, official-sampler arm O.
- **Sampler overhead is inside t_b** (float64 conversion of masked rows, selection, inverse CDF). The model forward itself is the larger part (setup.md 0.129 s was an upper bound).
- **Evaluation of the gates on CPU** for the CLIP legs of PG-1 and PC-F while the GPU was busy; PG-V's VLM scoring ran on the GPU under gpu_guard (`telemetry-pgv-*eval*.csv`).
