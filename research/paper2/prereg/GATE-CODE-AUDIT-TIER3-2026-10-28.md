```yaml
agent: gate-auditor
date: 2026-10-28
brief: Spec-conformance audit of the Tier-3 fusion module (SAP A4 r1 section A4.1; red-team C4-9, C4-10) at 00b92d4d
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md (lines 53-297, A4.1.1-A4.1.11)
  - research/paper2/prereg/RED-TEAM-SIGNOFF-2026-10-28.md (C4-9, C4-10, lines 470-471)
  - worktree agent-a42dc73cfa4f09bb9 at 00b92d4d: exp_p2/gate/tier3_fusion.py (502 lines), tests/exp_p2/test_gate_tier3_fusion.py (535 lines), research/paper2/method/IMPL-I-TIER3-FUSION-2026-10-28.md
  - code read for behaviour: exp_p2/gate/evidence.py, scores.py:108-110, fit_threshold.py:28-33 and main, calibrate.py (ids_hash, Threshold), artifacts.py, seeds.py, analysis_m4.py (load_items, corr_of, run, main), pipeline.py (compact, gate_scores, image_delta), run_gate_m4.py:100-185, run_gate_m2.py:50-66, report.py report_test
  - data (structure or M2 only): runs/P2-GATE-M3/family.json (keys), ps_frozen.json (key names), runs/P2-GATE-M2/threshold.json (key names), runs/P2-GATE-M2 items.jsonl and arrays (pool build check)
coverage: >
  NOT opened: runs/P2-GATE-M4 items.jsonl, arrays, analysis.json (blind). No M3/M4 outcome value read. The module was not run on M4; its behaviour on the real M4
  arrays is unverified (E3 by inspection, E4 only on synthetic fixtures and on the M2 pool). Only the one named test file was run (CPU shared with the GPU stage).
claims:
  - statement: "Module at 00b92d4d matches A4.1.2-A4.1.11 on arms, weights, rule, metric, contrasts, interval, seeds, MDD, d-control, consistency gate, order rule"
    status: supported
    evidence: "section 1 below, file:line"
    level: E3
    confidence: 0.9
  - statement: "31 tests pass; arm values equal an independent loop-based recomputation; the M2 calibration pool builds on the real M2 fold"
    status: supported
    evidence: "pytest log (31 passed in 15.86 s); scratchpad hand.py; scratchpad chk.py"
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - behaviour on real M4 arrays (never read, by design)
  - whether analysis_m4 will have been committed with git autocrlf side effects that make `git status --porcelain` non-empty (same test as foil.require_committed, so same behaviour)
next_test: {hypothesis: none, intervention: "lead records the pin row (card v4 section 7) then runs the CLI once after analysis.json and steps 4-5", primary_metric: none, falsifier: none, gpu_hours: 0}
```

# Gate-code audit: Tier-3 fusion comparators (A4.1)

**Audited SHA: `00b92d4d`** (branch `worktree-agent-a42dc73cfa4f09bb9`; parent chain f2f7b2e1 -> afe680fd -> 04b80687 -> d8c6c4fa -> 00b92d4d).
Blob ids: `tier3_fusion.py` 7a504df6fdae524ef035fe5e96f3a28b4aa7b8f3 (SHA-256 of committed bytes `70db8dbccb787e286ff6955bbf26d7408eee85aa6e8321f8f287c7ac72e63862`);
`test_gate_tier3_fusion.py` 7eab053de3396f41636cc6c373a437be73cd176a (SHA-256 `b97bad2b0cebeac1dbe2efe0aca7454bd1f917ed215c8abee8d243706ba92ab6`).

## Verdict: PASS

No required fix. The module matches A4.1 on every point I checked. Four non-blocking notes (section 8) go to the lead for the pin row. The audit
gates only the running of the code (A4 r1 C4-1); the pin row and the run order stay the lead's.

## 1. Spec conformance, item by item (`tier3_fusion.py` line numbers)

| Spec | Verdict | Evidence |
|---|---|---|
| A4.1.4 NONE = mean of all Delta, float64 | met | l.170 `d.mean()`; same operation as `evidence_from_delta` (evidence.py:36-37) |
| GM = mean over F=0; empty -> margin 0, Y=0 | met | l.164-171 (`keep.mean()`, `(0.0, True)` when empty) |
| MED = `numpy.median` of the 1,024 values | met | l.172 |
| TM-G: k = floor(g/2) per tail, g = flag sum; g<=1 equals NONE; retained m-g or m-g+1 | met | l.166 `g // 2`, l.145-152 `_trimmed` (k<=0 -> plain mean in original order, so bit-equal to NONE), empty when m-2k<=0 |
| TM20: k = floor(0.20 m) = 204, 616 central values | met | l.37, l.174; `math.floor(0.2*1024)` = 204; test l.58-64 |
| Sorting in float64 | met | l.164-167 |
| SOFT-G: w=1 off F; min{1, S_cal(u)/S_cal(tau)} on F; S_cal(tau)=0 -> 0 on F (= GM) | met | l.99-109; S_cal = #{u^cal > x}/N via `searchsorted(side="right")` l.87-94 |
| SOFT-A: w = (1 + #{u^cal >= x})/(N+1) | met | l.90-97, l.111-113 (`side="left"`) |
| u unjittered = `scores.suspicion_q(B, D)` from stored B, D | met | l.303; scores.py:108-110 |
| u^cal = `fit_threshold.suspicion_from_arrays(arr, "q")` unjittered, M2 clean pairs, ids_hash asserted, equal token count asserted | met | l.116-141 (mirrors `fit_threshold.main`: all rows, ascending idx) |
| Decision rule Y = 1[M>0]; M=0, empty, zero weight sum -> Y=0, counted | met | l.158 `_weighted`, l.371-372 (`n_empty`, `n_ties`) |
| Metric: paired accuracy, Delta = (b-c)/n, n, both accuracies, b, c, n_d, CI, MDD | met | l.242-256 |
| Contrast list: MED, TM-G, TM20, SOFT-G, SOFT-A minus GM, and minus NONE; GM-NONE quoted, not recomputed | met | l.245-246, l.411-417 (p keys not copied) |
| Interval: paired percentile bootstrap, 10,000, `numpy.quantile` 0.025/0.975 default method | met | l.38, l.213; l.250 `diff[idx].mean(axis=1)` (int8 mean accumulates in float64) |
| Index matrix `default_rng(child).integers(0, n, size=(10000, n))`, ascending idx, one per cell, shared by arms and contrasts | met | l.200-202 (matrix), l.310 (sorted by idx), l.373 (built once), used at l.376 by both `accuracy_contrasts` and `d_control` |
| MDD = 2.801585 x SD (ddof 1) of the 10,000 resampled differences | met | l.39, l.212-213 (`b.std(ddof=1)`) |
| Seeds: `SeedSequence(20261028, spawn_key=(32,))` spawned into 6 slots clean, jpeg, noise, splice, patch, swap; `seeds.py` not edited | met | l.42-43, l.194-197; slot by name so an absent cell moves nothing; `seeds.ANALYSES` has 32 entries (seeds.py:11-16), so position 32 is the next one; test l.170-181 |
| A4.1.8 d-control: d = mean/sd ddof 1 over retained set of NONE, GM, TM-G, TM20; |R|<2 or sd=0 dropped and counted; contrasts TM-G-GM, TM20-GM, same index matrix, MDD; MED, SOFT-G, SOFT-A have no d | met | l.49-50, l.180-190 (via `evidence_from_delta(...)["d"]`, NaN when n<2 or sd=0), l.259-275 |
| A4.1.10 three-way reading (lower > 0 above; upper < 0 below; else not distinguishable) | met | l.216-224 |
| A4.1.10 what counts against: detector-free above = against; not distinguishable = against only if MDD <= 0.05 (inclusive) else "uninformative at this n"; SOFT: above = against discarding, never the detector | met | l.227-239, emitted for "minus GM" on P cells only l.253-254 |
| A4.1.10 limits (a)-(d) written to the output; names only the five sanctioned names | met | l.53-58, l.471 |
| A4.1.2 cells: P (family.json keys), clean, PS patch/swap in own block; denoised copies and text direction listed as not computed | met | l.447, l.471-473 |
| A4.1.2 complete case: `<cond>_delta` 1,024 finite, `<cond>_flag0.05`, finite `<cond>_B`, `<cond>_D`; one item set per cell; exclusions counted with reason | met | l.290-303, l.306-332 |
| Multiplicity: count of intervals plus "no multiplicity adjustment (SAP 7)" only | met | l.461, l.465, l.497 |

Hand recomputation (mine, independent loop-based numpy, not the module's code): m=1,024 fixture, cal pool of 5,000, tau at the 0.95 quantile, g=66, k=33.
NONE 0.048368697407568106, GM 0.049606856024806585, MED 0.06427587196230888, TM-G 0.05877954253464129, TM20 0.06503818494376618 (616 values),
SOFT-G 0.05661380912280284, SOFT-A 0.04687254585644076: all equal to `item_margins` to better than 1e-12 (scratchpad `hand.py`). The module's own
hand cases (test l.40-55, l.87-101; m=8, 10-token pool) I re-derived: median (1+2)/2=1.5, TM20 sorted[1:7] = 7/6, TM-G g=4 -> 1.25, w^G = 1, 2/3, 1/3, 0, 1, SOFT-G = 5/2.

## 2. Order rule A4.1.9 and write-once

- `run` calls `require_committed(analysis.json)` first (l.425), before `items.jsonl`, any array, `family.json` or `threshold.json` is opened. Test l.488-495 asserts `read_jsonl` is never called before the refusal.
- `require_committed` (l.391-400): refuses if the file is absent, not tracked (`ls-files --error-unmatch`), or has a staged or unstaged change (`status --porcelain`). It then refuses if `primary.per_corruption` is not a dict (l.427-428). Tests l.449-485 cover absent, untracked, staged, modified after commit, no P section.
- Write-once: `artifacts.write_once(out, text, False)` (l.490); `force` is never passed; a second run exits 2 and leaves the bytes unchanged (test l.509-516). No timestamp or SHA in the output, so a rerun is byte-identical (test l.382-385; the CLI writes with `Path.write_text`).
- Limit, stated by the implementer and confirmed: "after steps 4 and 5 (PS, E-dec, E-pred)" cannot be enforced in code, and A4.1.11 asks only for "refuses unless analysis.json with the P section is committed". Procedural; the lead's run sheet must keep the order.

## 3. Consistency gate A4.1.3

`consistency_problems` (l.336-361) runs over every complete-case item of every cell (clean, P, PS; l.452-455) before any comparator is computed (`cell_results` at l.457 comes after). It recomputes NONE (all tokens) and GM (`~flag`) with `evidence.evidence_from_delta`, compares `y` exactly and `mean` within 1e-9 (NaN-safe: `not abs(...) <= tol`), and compares `flag.sum()` with `gate["0.05"].n_flag`. A missing or unreadable stored field is a mismatch. Any mismatch raises `ConsistencyError`, exit 3, no file written (tests l.224-245, l.436-445). The stored summaries are `pipeline.compact(...)` of float64 values with no rounding (pipeline.py:65-67), so the 1e-9 tolerance is not binding.

## 4. No p-value can be produced

No `scipy` import; no call to `mcnemar`, `wilcoxon`, `holm`, `report_test` or a permutation routine (AST test l.350-356, which I re-read: it also checks every called name). The output contains only point estimates, percentile intervals, `se_boot`, `mdd`, counts and readings. The quoted GM-minus-NONE copies only `b, c, n_d, n, acc_a, acc_b, delta, ci95` (l.417), not `p`, `p_mid`, `p_holm` (test l.337). The test also scans every output key for p-value names (l.343-344). The module imports `analysis_m4` (for `load_items`, `corr_of`, `SANITY_CONDS`), which itself imports test code, but none of it is called.

## 5. Inputs

Read from the M4 run: `analysis.json` (n_items, family, rule, `primary` or `secondary_y` per_corruption, for the order gate and the quote only), `items.jsonl` (via `analysis_m4.load_items`, `conds[cell].img.none`, `img["gate0.05"]`, `gate["0.05"].n_flag`), and per item the four arrays `<cell>_delta`, `_flag0.05`, `_B`, `_D` (l.292-296; `np.load` is lazy, so no other key is read). From M3: `family.json` and `ps_frozen.json` (`params.sanity_order`; key present in the real file, checked by key name only). From M2: `threshold.json` (tau, ids_hash) and `items.jsonl`/`arrays` B and D only (l.116-141). The soft weights are therefore fixed by the M2 calibration fold alone: nothing is fitted on M3 or M4.

Real-data check on M2 only (no outcome): `build_cal_pool` on `runs/P2-GATE-M2` returned 300 items, 307,200 tokens, `ids_hash` equal to `threshold.json`, tau = -0.09846870147599458, S_cal(tau) = 0.04683 (<= alpha 0.05, as the CRC statement requires). This confirms the pool code against the real fold. SHA-256 of every M2 npz and of `threshold.json` go into the output (l.131, l.141, l.469), which is the "otherwise" branch of the A4.1.5 freeze clause.

## 6. The 13 ambiguities in the implementer's report

| # | Reading chosen | Right? |
|---|---|---|
| 1 | Names: module, output, CLI as in A4.1.11; test file `test_gate_tier3_fusion.py` | Module, output and CLI: yes (A4.1.11 l.286-288). Test file: A4.1.11 prints `tests/exp_p2/test_tier3_fusion.py`; the report says the SAP names were followed but the test name is not the SAP's. It is the name in the lead's brief. Note N1 |
| 2 | "Committed" = tracked and clean in the containing repo; P-section check on `primary.per_corruption` | Yes; same test as `foil.require_committed`; the only reading A4.1.11 allows |
| 3 | Extra refusals on `n_items` and family keys | Yes and safe: `analysis.json` carries `n_items = len(rows)` from `load_items` and `family = keys` (analysis_m4.py:591), and `family.json` entries have `key` (checked), so a real run passes. Both follow from "exactly those analysis_m4 analysed" |
| 4 | P cells from family.json; PS cells from `ps_frozen.json` sanity_order, fall back to (patch, swap) if absent; slot of a P cell = its `corruption` | Yes (A4.1.2 "follows mechanically from family.json and ps_frozen.json"). The fallback never fires (file exists) |
| 5 | GM minus NONE quoted on P cells only; under R3 from `secondary_y` | Yes. Part 1 uses Y under R3 (A4.1.6, AB.3 item 3) and the output says so (l.464) |
| 6 | d-control: drops applied inside each resample over the cell's own index matrix | Yes. The only reading that keeps "same index matrix" literal; resamples with no valid item are NaN and counted |
| 7 | TM-G with g=m: empty, Y=0, counted | Yes (A4.1.4 "empty retained set") |
| 8 | Consistency failure: stderr, exit 3, no file | Yes. A4.1.3 says "stops Part 1 ... reported as a pipeline discrepancy". The lead must capture the stderr (note N3) |
| 9 | `counts_against` for "minus GM" on P cells only, inclusive MDD <= 0.05, mechanical labels | Yes; "only if MDD <= 0.05" is inclusive |
| 10 | Pre-frozen `soft_weight_frozen.npz` not used; pool recomputed with SHA-256 of every M2 npz | Yes; A4.1.5 allows it ("Otherwise ... computed from the M2 arrays at analysis time with the SHA-256 of every M2 npz written into the output") |
| 11 | tau float64; float32 u promoted exactly to float64 before `searchsorted` | Yes; the comparisons are the float32 comparisons, exact |
| 12 | n_boot = 10,000 constant, not a CLI option | Yes (A4.1.7); the CLI cannot change the preregistered value |
| 13 | m = 1,024 constant; functions take m for tests; TM20 k = floor(0.20 m) | Yes; the complete-case rule needs 1,024 values (l.297) |

## 7. Existing files, frozen files, tests

- `git diff f2f7b2e1 00b92d4d --stat -- exp_p2 tools tests`: 2 files, both added (`exp_p2/gate/tier3_fusion.py` +502, `tests/exp_p2/test_gate_tier3_fusion.py` +535); 0 modified, 0 deleted. `git diff --name-status afe680fd 00b92d4d` over the whole tree: three added files (those two plus the IMPL report). In the main worktree `git diff f2f7b2e1 HEAD -- exp_p2 tools tests` is empty (HEAD afe680fd), so f2f7b2e1 is still the current pinned code. `seeds.py`, `analysis_m4.py`, `run_gate_m4.py`, `fit_threshold.py`, `epred_fit.py`, `theory.py`, `tools/gpu_guard.py` and the frozen run files (`threshold.json`, `family.json`, `ps_frozen.json`, `epred_frozen.json`) are byte-untouched by these commits. Worktree status clean before and after the test run.
- `C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe -m pytest tests/exp_p2/test_gate_tier3_fusion.py -q -p no:cacheprovider` in the worktree (CUDA_VISIBLE_DEVICES empty): **31 passed, 1 warning (pynvml deprecation) in 15.86 s**.
- A4.1.11 self-test list: all items have a test (arms, TM-G g<=1, 511-per-tail = MED, SOFT-G limits, weight ranges and monotonicity, ties and empty sets, consistency stop, seed-slot independence, byte-identical rerun, MDD on a known SD).

## 8. Notes for the lead (non-blocking; none is a required fix)

- **N1. Test file name.** A4.1.11 prints `tests/exp_p2/test_tier3_fusion.py`; the file is `tests/exp_p2/test_gate_tier3_fusion.py` (the name in the brief). Name the actual file in the dated pin row, and say it is a naming deviation from A4.1.11 text with no effect on content. Renaming is optional; if done, the audited SHA changes and a delta check is needed.
- **N2. Degenerate MDD.** If a comparator's Y vector equals GM's on every item (n_d = 0), the bootstrap SD is 0, MDD = 0, and `counts_against` returns `finding_against_added_value` for MED, TM-G, TM20 although there is no information. This is the literal A4.1.7/A4.1.10 rule, so it is not a code defect, but every sentence built from it must carry n_d (A4.1.10 already requires it) and a statistician should say how n_d = 0 is worded before the output is read. Same, to a lesser degree, for very small n_d.
- **N3. Where a consistency failure is recorded.** It goes to stderr only (exit 3). If it happens, save the stderr to a file under `runs/P2-GATE-M4/` before anything else is done, as the card's "pipeline discrepancy" row needs the text.
- **N4. Weak test.** `test_slot_of_a_cell_does_not_change_when_another_cell_is_absent` (l.402-412) asserts the slot index, not the draws. The property holds by construction (`cell_seed_sequence` depends only on the name, l.194-197), so no fix is needed.
- Order of steps 4 and 5 before running (A4.1.9) is procedural and stays on the run sheet.
- Pin rule (C4-10): the files are inside the card's pre-launch scope; they may be merged only with the dated pin row and this delta check (delta = the two added files above). This audit is the delta check for the module against A4.1; the row itself is the lead's.

## 9. Not covered

Behaviour on the real M4 arrays and the real `analysis.json` (blind); the full test suite (CPU shared with the GPU stage); the spec text of A4.1.10 wording (the module emits mechanical labels, the writer's sentences are outside this audit); the red-team's signature on A4.2 and A4.3 (other parts of A4).

---

# Delta r3 (2026-10-29): `00b92d4d` -> `32f02836` against SAP A4.1.12 items 1-8 and A4.1.10 r3

**Audited SHA: `32f02836`** (branch `worktree-agent-a42dc73cfa4f09bb9`, on top of the audited `00b92d4d`; SAP r3 at main-worktree commit `2305d64a`).
Blob ids: `tier3_fusion.py` 91e45945977ed94f2d32e95fa9d449939a816f16 (SHA-256 of committed bytes `1ff4e5b9a87be858af43cd885895cfc4763286c1a409f99ce44087fdbca3f457`);
`test_gate_tier3_fusion.py` 695b24275968014b4da6cd72f92214dadf81d521 (SHA-256 `2ecf5ee9f64a81db2af3bce7071d3a68a6bc95fe0f7728f32d5490c27c01ae26`).
`runs/P2-GATE-M4` not opened.

## Verdict: PASS (no required fix)

## Items (against `git diff 00b92d4d 32f02836`)
| A4.1.12 item | Verdict | Evidence |
|---|---|---|
| 1 import `scipy.stats.beta`; `N_D_MDD_MIN = 10`, `ALPHA_EXACT = 0.05` | met | import and constants added after `MDD_DESIGN_MARGIN` |
| 2 `exact_theta_interval` (NaN pair if n_d=0; lower 0 if b=0 else `beta.ppf(0.025, b, n_d-b+1)`; upper 1 if b=n_d else `beta.ppf(0.975, b+1, n_d-b)`) | met | identical to the text |
| 3 `exact_reading` (identical; lower > 0.5 above; upper < 0.5 below; else not_distinguishable) | met | strict inequalities as specified |
| 4 `discordance_bound` (1.0 if n_d >= n else `beta.ppf(0.975, n_d+1, n-n_d)`) | met | |
| 5 `counts_against(comparator, read, mdd, n_d, B)` | met | `bound = B if n_d < N_D_MDD_MIN else mdd`, inclusive `<= 0.05`; below -> gate_higher; SOFT stems with "_identical" suffix |
| 6 row fields `theta_ci95_exact`, `discordance_bound_B`, `reading` (exact), `reading_bootstrap`, `mdd_used`; `ci95`, `se_boot`, `mdd` unchanged | met | `counts_against` still only on "minus GM" rows of P cells |
| 7 `d_control` all-zero valid differences -> `identical_on_every_item` | met | `valid.any() and np.all(diff[valid] == 0.0)`; other contrasts keep the bootstrap reading (r3 item 6) |
| 8 tests | met | all listed cases present: (4,0) nd, (6,0) above, (0,6) below, (0,0) identical, (5,0) nd; B(0,300), B(0,500) within 1e-4; MED identical n=500 n_d=0 -> finding_against_added_value; MED nd n_d=12 mdd 0.06 -> uninformative; bootstrap "above" with exact "nd" yields no `finding_against_*` (b=4, c=0, n=40) |
| A4.1.10 r3 items 1-6 | met | labels from the exact interval; bootstrap kept as description; `mdd_used` flags n_d < 10; the module emits fields only, sentences stay the writer's |

## Hand recomputation of exact cases (mine: closed forms and an independent bisection on binomial tails)
- b=4, c=0 (n_d=4): lower = 0.025^(1/4) = 0.39764 < 0.5, upper = 1 -> not_distinguishable. Module 0.3976353643835253 equals the bisection value.
- n_d=0: identical; interval (NaN, NaN); `discordance_bound(0,500)` = 1 - 0.025^(1/500) = 0.0073506 (spec 0.0074 within 1e-4), `(0,300)` = 0.0122210 (spec 0.0122), `(15,500)` = 0.04900 <= 0.05 (as r3 item 4 states). MED with "identical", n_d=0, n=500 -> finding_against_added_value; at n=40, B = 0.088 -> uninformative (test).
- Also (6,0): lower 0.54074 -> above (so n_d >= 6 is the one-sided threshold of r3 item 2); (5,0): lower 0.47818 -> not distinguishable; (0,6): upper 0.45926 -> below; (3,1): (0.1941, 0.9937); (12,5): (0.4404, 0.8969). Module and bisection agree to 1e-15.

## Ambiguities 14-20
| # | Reading | Right? |
|---|---|---|
| 14 | SOFT label = stem + "_identical" (stem already contains "not_distinguishable") | Yes, literal; cosmetic oddity, the writer must not quote the label string |
| 15 | "minus NONE" rows get the exact fields and reading | Yes (item 6 "per row"); no `counts_against` there |
| 16 | n_d >= 10 and MDD NaN -> `uninformative_at_this_n` | Yes, conservative: NaN comparison is False, no "against" label |
| 17 | `ALPHA_EXACT` defined, literals 0.025 / 0.975 in formulas | Yes (items 2 and 4 write the literals) |
| 18 | NaN in JSON for n_d = 0; "MDD not used" text left to the writer, `mdd_used` flag in JSON | Yes (r3 item 3) |
| 19 | `discordance_bound` returns 1.0 for n_d >= n including n = n_d = 0 | Yes (item 4) |
| 20 | Sentences not generated | Yes |

## Existing files and tests
- `git diff --stat f2f7b2e1 32f02836 -- exp_p2 tools tests`: only the two new files (+541, +603); no existing file modified. `git diff 00b92d4d 32f02836` touches only those two and the IMPL report. Worktree clean after the test run.
- `.venv python -m pytest tests/exp_p2/test_gate_tier3_fusion.py -q -p no:cacheprovider`: **35 passed in 18.65 s** (one pynvml warning).
- Everything audited at `00b92d4d` is unchanged except the import, two constants, `counts_against`, `accuracy_contrasts` and `d_control`. The no-p-value rule holds: only `scipy.stats.beta` is imported (AST test `scipy_names == {"beta"}`), and the output has no p-value key; `beta.ppf` gives interval limits, not tests.

## Non-blocking notes
- N5. Cosmetic: the diff changes `ROOT = Path(...)` to `ROOT =Path(...)` (a deleted space). No effect.
- N6. The pin row replaces `00b92d4d` by `32f02836` (A4.1.12); record the two SHA-256 values above.
