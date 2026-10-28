```yaml
agent: statistician
date: 2026-10-28
brief: >
  SAP Addendum A4 for Paper 2 (GATE on UniDisc; Information Fusion). Part 1 pre-specifies the Tier-3 fusion comparators of
  red-team M-e (detector-free robust combiners, a soft reliability weight, the hard gate). Part 2 is the outcome book
  (red-team M-c, A1, A3, A4): title, highlight 1, abstract result sentence, Discussion 6.1 opening, contribution list and
  figure layout for every A2.2 label, K1 and R3, and the D18 / AB.1 reconciliation. Part 3 has two dated rules (time input of
  the released UniDisc configuration; FOIL before S2). To be committed before `analysis_m4` is first run (card v4 row 6).
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (sections 1-3, 4.6-11 and the addenda A1, A2 (A2.x), A2-debate (AD.x), A2b (AB.x), A3, A3b, A3b.12 read; Appendix A and sections 4.1-4.5 not re-read)
  - research/paper2/prereg/PREREG-GATE-v4-2026-10-28.md (sections 1-9 read in full)
  - research/paper2/ideation/NOVELTY-CHECK-INFFUS-2026-10-28.md (sections 0-6); research/paper2/ideation/NOVELTY-REAUDIT-GATE-2026-10-28.md (section 7, must-not 1-9)
  - research/paper2/CONFIRM-EVENING-2026-10-28.md (full)
  - research/paper2/benchmark/REDTEAM-P2-PLAN.md (sections 0, A1-A11, B, C, D, concerns)
  - research/paper2/prereg/PREREG-GATE-MUST-v3-2026-10-28.md lines 197-219 (section 12, R3 wording)
  - research/ledgers/decisions.jsonl row D0074 (K2 applied)
  - runs/P2-GATE-M1/analysis.json (keys table, falsifier, frozen, chance_bar_both; already analysed and committed, D0074)
  - code read at HEAD 768e40ed (no edit, nothing executed except one json read): exp_p2/run_gate_m4.py, exp_p2/run_gate_m2.py lines 30-62, exp_p2/gate/fit_threshold.py, exp_p2/gate/calibrate.py, exp_p2/gate/pipeline.py lines 30-73, exp_p2/gate/scores.py lines 108-110, exp_p2/gate/evidence.py lines 29-46, exp_p2/gate/analysis_m4.py lines 40-105 and 220-258, exp_p2/gate/seeds.py, exp_p2/gate/arms.py lines 17-60, exp_p2/run_gate_foil.py lines 1-75, exp_p2/run_gate_s2.py (grep)
coverage: >
  Not read: the paper sources (main.tex, method.tex, protocol.tex), PANEL-P2-PLAN, INFFUS-CITATIONS, spec v2, IMPL reports.
  Outcome firewall: I opened no M2, M3 or M4 value. For M2 I read only the row count of items.jsonl (300) and the existence of
  threshold.json (contents not read). For M3 I listed the run directory (config, driver log, telemetry, 0 arrays, no items.jsonl,
  no family.json). No M4 directory exists. The only outcome numbers used are M1's, which were analysed and committed before this
  addendum (D0074, commit ace6dbe3 per the ledger).
claims:
  - statement: "Every array the Tier-3 comparators need is stored per M4 item: per-token Delta (`<cond>_delta`), B and D (`<cond>_B`, `<cond>_D`) and the flags at each alpha (`<cond>_flag0.05` etc.); the suspicion u itself is not stored but is a deterministic function of the stored B and D."
    status: supported
    evidence: "exp_p2/run_gate_m4.py:144, 149-157; exp_p2/gate/pipeline.py:30-35; exp_p2/gate/scores.py:108-110 (read at HEAD 768e40ed)"
    level: E3
    confidence: 0.9
  - statement: "Denoised conditions (`<cond>_dn`) store Delta and codes but no B, D or flags, so no gate-dependent comparator can be computed on them."
    status: supported
    evidence: "exp_p2/run_gate_m4.py:144-148 (the `continue` before the gate scores)"
    level: E3
    confidence: 0.9
  - statement: "FOIL family B has no input from M2-M4 or S2 and uses no random stream, so running it before S2 changes no number of either family."
    status: supported
    evidence: "exp_p2/run_gate_foil.py:1-75 (prerequisites: FOIL file, committed pool, leak check, fusion_frozen.json); S2 streams keyed by item and ARM_TAG, exp_p2/gate/arms.py:58-60"
    level: E3
    confidence: 0.8
competing_explanations: []
unknowns:
  - every M3, M4, S2, FOIL, Omni and suite outcome
  - whether Shlok accepts the D18 reading of A4.2.6 (needs Shlok)
  - the 85-character highlight limit is quoted from memory of Elsevier's guide (E0); the venue scout verifies it
next_test: {hypothesis: "none (plan only)", intervention: "commit this addendum before analysis_m4; audit the Tier-3 code before it runs", primary_metric: "none", falsifier: "none", gpu_hours: 0}
```

# SAP Addendum A4 (2026-10-28, before any M3 or M4 outcome)

Author: statistician. Written 2026-10-28, clock 22:22 IST at the start of writing. A separate file beside the SAP, because the brief
forbids edits to the SAP text. **Precedence:** A4 > A3b > A3 > A2b > A2 > A1 > SAP body (card v4 "Precedence"), and only on the
points listed here; family P and every earlier rule stand. Sections are **A4.1 to A4.6**.

**Status and firewall.** M2 has 300 rows and a `threshold.json` (contents not read by me). M3 has started (run directory with
`config.json`, logs and telemetry; 0 arrays, no `items.jsonl`, no `family.json` at 22:22 IST). No M4 directory exists. No S2,
FOIL, Omni or suite item exists. Nothing below was chosen with knowledge of any M2, M3 or M4 value. The only outcome numbers quoted
are those of M1 (`runs/P2-GATE-M1/analysis.json`, SHA-256 `bdc3fda3be5a36b763338c3695857e4b45ae330c40eee3c3389ffeb79aa22295`),
analysed and committed earlier (ledger D0074).

**Pins (before A4).** SAP at HEAD `768e40ed`: LF `e33f078c45b92b94cbf658192e2fd815f8c6eafbffe53ba39bc0dd728982afb7`, CRLF working tree
`d95fb87b22c8eb713d35b07a0a066c56cb250a7578e590691cdb983609ec6da6` (both equal to card v4 section 1.3). Red-team plan review
`research/paper2/benchmark/REDTEAM-P2-PLAN.md` SHA-256 `38e1b85a575379724bd0ab840e9e4cac1d891e8d0ae26590145ec2a461ff2169` (commit `768e40ed`).
`exp_p2/run_gate_m4.py` CRLF working tree `0050fbf9d2f84085b5ec289692ebad93fa3d10cefccbea979098c3f16b6735df`. The SHA-256 of this file is
recorded by the lead at commit time (it cannot be written inside the file).

**Binding condition.** A4 binds when (i) it is committed before `analysis_m4` is first run on M4 data (card v4 row 6), (ii) the red team
has read it, and (iii) the gate-auditor has matched the Tier-3 code of A4.1.11 to the text before that code is run. If (i) fails, Part 1
is void (forking paths, red-team concern 5) and the comparators may not be reported at all, not even as exploratory; Parts 2 and 3 then
need a new dated addendum that says they were written after P was visible.

Provenance tags as in the SAP: **derived** (arithmetic shown), **ASSUMED**, **design** (a rule chosen now), E-levels as in the contract.

---

## A4.1 Part 1: Tier-3 fusion comparators (red-team M-e)

### A4.1.1 Question, label, and what it is not

Question: on the same per-token evidence $\Delta_j$ and the same decision rule as family P, does the hard gate GATE-M give a
different image-direction matching accuracy from (a) detector-free robust combiners of $\Delta_j$ and (b) a soft reliability weight
built from the same suspicion score $u_j$ that the gate thresholds?

**Label: Tier 3, exploratory (SAP 7).** Confidence intervals only. **No p-value is computed for any contrast in this part** (stricter than
SAP 7, which would allow unadjusted p-values labelled exploratory; reason: with 12 or more intervals and an obvious "beats the method"
reading, a printed p invites selection). No multiplicity statement. It is not a family, cannot enter P or any secondary family, cannot
rescue or explain a P result (AB.1), and its comparators are never presented as "our method", "an improved gate" or a variant of GATE
(red-team C.3, last bullet).

### A4.1.2 Data: run, fold, cells, items, arrays

**Run and fold.** `runs/P2-GATE-M4`, the M4 test fold as fixed by the committed n-rule (`runs/P2-GATE-M3/family.json`): the first
300 ids (R1, R3, NO-GO) or 500 (R2). The analysed items are exactly the items that `analysis_m4` analysed for P (de-duplicated rows,
`analysis_m4.load_items`, SAP 8.1). Nothing is added, dropped or re-run for this part.

**Cells (fixed now; the set present follows mechanically from `family.json` and `ps_frozen.json`).** One cell per M4 condition key:
- **P cells:** the family conditions at their operating points (`corruptions.corruption_key(corr, sev)`, built at
  `exp_p2/run_gate_m4.py:108-125`, line 119). These carry the M-e question.
- **Clean cell** `clean`: cost of each combiner on clean pairs (no corruption).
- **PS cells** `patch`, `swap`: reported in a separate table labelled "positive-control conditions; pipeline check only", never pooled
  with or plotted beside the P cells (A4.2.5).
- **Not computed:** the denoised copies `<cond>_dn` (no B, D or flags are stored for them, `run_gate_m4.py:144-148`); the text
  direction (no per-token text arrays are stored; only summaries in `cr["txt"]`).
Under K1 (NO-GO) there are no P cells; the part then has only the clean and PS cells and the paper says "no realistic cell".

**Arrays used, per item `runs/P2-GATE-M4/arrays/item<idx:04d>.npz` (written by `runner.run_items`, `exp_p2/gate/runner.py:208-209`; read
the same way by `analysis_m4.py:368, 484`).** All are stored; nothing needed is missing.

| Quantity | Key in the npz | Where written | Note |
|---|---|---|---|
| per-token paired evidence $\Delta_j$, 1,024 float32 | `<cond>_delta` | `run_gate_m4.py:141, 144` | $\Lambda^{c^+}_j[v_j]-\Lambda^{c^-}_j[v_j]$, same deranged $c^-$ as P (`pipeline.py:44-46`) |
| GATE-M flags at alpha 0.05 (bool, 1,024) | `<cond>_flag0.05` | `run_gate_m4.py:150-152, 156-157` | key format `f"{al:g}"`; jittered $u$ compared with $\tau$ (strict) |
| B, D (1,024 each) | `<cond>_B`, `<cond>_D` | `run_gate_m4.py:149, 154` | **$u$ is not stored**; it is recomputed exactly as `scores.suspicion_q(B, D)` = $-(B-D)$ in float32 (`scores.py:108-110`), the same call as `pipeline.gate_scores` (`pipeline.py:30-35`); D is stored as float32 and `suspicion_q` casts to float32, so the recomputation is bit-identical. The jittered $u$ is not stored and is not needed |
| stored arm summaries (cross-check) | `items.jsonl` `conds[<cond>].img.none` and `.img["gate0.05"]` (`n`, `mean`, `sd`, `z`, `d`, `y`) | `run_gate_m4.py:173`; `pipeline.compact`, `evidence.evidence_from_delta` | used only for the consistency gate of A4.1.3 |
| flagged count | `conds[<cond>].gate["0.05"].n_flag` | `run_gate_m4.py:158` | cross-check of $g_i$ |
| calibration pool for the soft weight | `runs/P2-GATE-M2/arrays/item<idx:04d>.npz` keys `B`, `D` | `run_gate_m2.py:60` | clean calibration pairs only |
| threshold | `runs/P2-GATE-M2/threshold.json` `thresholds["0.05"].tau`, `ids_hash` | `fit_threshold.py:34-38` | committed before M4 (card v4 row 3) |

**Complete case per cell (SAP 8.1).** An item enters a cell if and only if its npz holds `<cond>_delta` with 1,024 finite values,
`<cond>_flag0.05`, and finite `<cond>_B` and `<cond>_D`. The same item set is used for every arm and comparator of that cell (paired).
Excluded items are counted per cell with the reason.

### A4.1.3 Consistency gate (before any comparator is computed)

For every item of every cell, recompute the NONE and GATE-M margins from the npz with `evidence.evidence_from_delta` (all tokens; tokens with
`flag0.05` false) and compare with the stored `img.none` and `img["gate0.05"]`: `y` must be equal and `mean` equal within 1e-9 absolute,
and $g_i$ = `flag0.05.sum()` must equal `gate["0.05"].n_flag`. **Any mismatch stops Part 1** before a comparator is computed: it is
reported as a pipeline discrepancy, investigated against the unit tests, and Part 1 runs only after a bug fix with a dated row (card
v4 section 7). No comparator number exists until the gate passes.

### A4.1.4 The arms (all on the same $\Delta_j$ of the same item and cell; $m=1{,}024$)

Notation: $\Delta_{(1)}\le\dots\le\Delta_{(m)}$ the sorted values in float64; $F_j\in\{0,1\}$ the stored flag `<cond>_flag0.05`; $g_i=\sum_jF_j$.

| Arm | Item margin $M_i$ | Origin |
|---|---|---|
| **NONE** (reference) | $\frac1m\sum_j\Delta_j$ | P's "none" arm |
| **GM** (hard gate, as preregistered) | mean of $\Delta_j$ over $\{j:F_j=0\}$ | P's GATE-M arm (alpha 0.05, $K=8$, CRC threshold from M2, jitter as stored). Not recomputed with any other alpha, K or seed |
| **MED** | `numpy.median` of the 1,024 values (mean of $\Delta_{(512)}$ and $\Delta_{(513)}$) | detector-free |
| **TM-G** (trimmed mean at the gate's realised flag count) | $k_i=\lfloor g_i/2\rfloor$ removed from **each** tail; mean of $\Delta_{(k_i+1)},\dots,\Delta_{(m-k_i)}$ | detector-free in its choice of tokens; only the count $g_i$ comes from the gate |
| **TM20** (fixed trim fraction) | $k=\lfloor0.20\cdot1024\rfloor=204$ per tail (derived), mean of the 616 central values | detector-free |
| **SOFT** (soft reliability weight) | $\sum_jw_j\Delta_j/\sum_jw_j$, $w_j$ of A4.1.5 | same detector as GM |

**Why TM-G removes $\lfloor g_i/2\rfloor$ per tail (design).** "Trim fraction equal to the gate's realised flag rate" has two readings: the
fraction $g_i/m$ removed in total (half from each tail) or from each tail (twice the gate's count). The first is adopted because it
**matches the number of removed tokens** to the gate item by item, so TM-G versus GM isolates *which* tokens are removed (the extremes of
$\Delta$ against the tokens with high $u$) at equal count. The retained set has $m-2k_i\in\{m-g_i,\,m-g_i+1\}$ tokens, never fewer than
GM's. $g_i\le1$ gives $k_i=0$ (TM-G equals NONE). The other reading is not computed.

**Why 20 percent per tail for TM20 (design, fixed without data).** It is the conventional default trimming for a robust location estimate
(the 20 percent trimmed mean of Tukey and McLaughlin, recommended as a default in Wilcox's robust-statistics texts; **citations E0 from
memory, to be checked by the citation checker before the paper cites them**). It also completes a fixed ladder of trimming with no free
choice: TM-G (about the gate's count, near alpha on clean pairs if the guarantee holds), TM20 (a fixed heavy trim), MED (the limit: the
median is the trimmed mean with 511 per tail, an identity used as a self-test). No $\Delta$ distribution from M1-M4 was looked at; the
SAP's probe-1 skewness (section 2.5) is of item margins, not tokens, and was not used.

**Ties and empty sets.** $Y_i=\mathbb 1[M_i>0]$; $M_i=0$, an empty retained set or $\sum_jw_j=0$ give $Y_i=0$ (SAP 2.1). Counts per arm and
cell are reported.

### A4.1.5 The soft reliability weight (fixed now; parameters from M2 clean pairs only)

Let $u_j=$ `scores.suspicion_q(B_j, D_j)` (unjittered) for the test token, and let the **clean calibration pool** be all tokens of the M2
calibration items listed in `runs/P2-GATE-M2/items.jsonl` (the items `fit_threshold` used; the script asserts that `calibrate.ids_hash` of
their `gid` list equals `threshold.json` `ids_hash`), with $u^{\rm cal}$ = `fit_threshold.suspicion_from_arrays(arr, "q")` unjittered.
Every calibration item has 1,024 image tokens, so the item-weighted pooled survival function of CRC (`calibrate.fit_threshold`, the
`tail` array) equals the token-pooled one:
$$S_{\rm cal}(x)=\frac{1}{N}\#\{u^{\rm cal}>x\},\qquad N=\text{number of pooled calibration tokens}.$$
With $\tau=$ `threshold.json` `thresholds["0.05"].tau`:
$$w_j=\begin{cases}1 & F_j=0\\ \min\{1,\;S_{\rm cal}(u_j)/S_{\rm cal}(\tau)\} & F_j=1\end{cases}\qquad(\text{if }S_{\rm cal}(\tau)=0,\ w_j=0\text{ for flagged }j,\ \text{SOFT}=\text{GM}).$$

**Justification (first principles; no corrupted image, no M3 or M4 value, no free scale parameter).**
1. **Evidential discounting.** $S_{\rm cal}(u_j)$ is the conformal p-value of token $j$ against clean calibration tokens: the share of clean
   tokens at least as suspicious. Dividing by its value at the threshold makes $w_j$ the relative plausibility that a flagged token is a
   clean token, used as a reliability that discounts rather than discards the source, the analogue of reliability discounting in evidence
   theory that the red team names (`huang2025evidential` in the project's citation list; I have not read it, E0).
2. **It touches only the gate's flagged set.** $\{j:w_j<1\}\subseteq\{j:F_j=1\}$, so on a clean test pair exchangeable with the calibration
   pairs the expected share of **discounted** tokens is at most alpha, by the same CRC statement as GATE-M (it says nothing about how much
   weight is lost). SOFT versus GM therefore isolates one design choice, discount versus discard, with the same detector, the same
   threshold and the same flagged set.
3. **Limits.** $w_j$ is non-increasing in $u_j$ among flagged tokens; $w_j$ is near 1 for a token just above $\tau$ and is 0 only when $u_j$
   is at least the maximum of the calibration pool. As $S_{\rm cal}$ is a step function, $w$ has at most $N+1$ distinct values.
4. **Parameters:** alpha 0.05 (preregistered primary; no other alpha is used here), $\tau$ and $S_{\rm cal}$ from M2 clean pairs. Nothing is
   tuned, and no alternative $f$ (logistic, full-range p-value weight) is computed.

**Freeze (design).** Preferred: after `threshold.json` is committed and **before the first M4 item**, the lead commits
`runs/P2-GATE-M2/soft_weight_frozen.npz` holding the sorted pooled $u^{\rm cal}$ (float32), $\tau$, $N$, `ids_hash`, the SHA-256 of
`threshold.json` and of the writer script. If that file does not exist when Part 1 runs, $S_{\rm cal}$ is computed from the M2 arrays at
analysis time and the SHA-256 of every M2 npz used is written into the output; because $S_{\rm cal}$ is a deterministic function of the
calibration fold, no choice is involved either way. M2 arrays are not modified.

### A4.1.6 Decision rule and metric

Decision rule: as P (SAP 2.1): sign of the item margin, image direction, same true caption and same deranged negative caption, ties and
empty sets wrong. **Metric:** paired matching accuracy $A^{\rm arm}=\frac1n\sum_iY^{\rm arm}_i$ on the cell's complete-case items, and the
paired net difference $\hat\Delta=A^{\rm a}-A^{\rm b}=(b-c)/n$ with $b=\#\{Y^{\rm a}=1,Y^{\rm b}=0\}$, $c=\#\{Y^{\rm a}=0,Y^{\rm b}=1\}$.
Reported with every contrast: $n$, both accuracies, $b$, $c$, $n_d$, $\hat\Delta$, the 95 percent interval.
**Under R3** (P's endpoint is $d$) this part still uses $Y$ (stored in every case, AB.3 item 3), plus the $d$-scale trimming control of
A4.1.8. The paper says that the Tier-3 accuracy contrasts are not on P's R3 endpoint.

### A4.1.7 Contrasts, intervals, seeds

**Contrasts (fixed list, per cell; all reported, whatever their direction):**
- versus the hard gate: **MED - GM, TM-G - GM, TM20 - GM, SOFT - GM** (the M-e question);
- versus no gate, descriptive context: **MED - NONE, TM-G - NONE, TM20 - NONE, SOFT - NONE**. GM - NONE is P's own contrast and is quoted
  from `analysis.json`, never recomputed as a new result.

**Interval:** paired percentile bootstrap over items, 10,000 resamples, 95 percent (2.5th and 97.5th percentiles). Within a cell one
resample-index matrix is shared by every arm and contrast (so the contrasts are coherent). **Seeds:** a new analysis name
`tier3_fusion` appended to `exp_p2/gate/seeds.ANALYSES` after `suite` (position 32; appending leaves the 32 earlier children unchanged,
A3.7). Until it is appended, the documented fallback `numpy.random.SeedSequence(20261028, spawn_key=(32,))` is used and recorded (it
equals the appended child). That child is spawned into 6 fixed slots in the order `clean, jpeg, noise, splice, patch, swap`; an absent
cell leaves its slot unused, so no cell's stream depends on which others exist.

**Multiplicity, stated, not corrected.** With up to 3 P cells x 4 contrasts against GM = 12 intervals, about 0.6 would exclude 0 by
chance if every true difference were 0 and the intervals were independent (derived: 12 x 0.05; they are not independent). The paper
prints this sentence beside the table.

### A4.1.8 Trimming control on the size-free evidence ratio $d$ (descriptive; answers red-team D question 5)

For every cell, also report $d=\bar\Delta_R/s_R$ (ddof 1, `evidence.py:37-41`) over the retained set $R$ of NONE, GM, TM-G and TM20, and
the paired bootstrap 95 percent interval of the mean of **$d^{\rm TM\text{-}G}-d^{\rm GM}$** and $d^{\rm TM20}-d^{\rm GM}$ (same index matrix).
Items with $|R|<2$ or $s_R=0$ in either arm are dropped from that contrast and counted. MED and SOFT have no $d$ in this plan (not defined
consistently); stated. **Reason:** symmetric trimming of the extremes lowers $s_R$ mechanically, so a GM rise in $d$ may be trimming, not
detection (v3 line 213, the caveat "trimming heavy-tailed tokens can raise d"). TM-G is a detector-free trimming of the same count; it is
the only empirical handle on that caveat in this plan. It is Tier 3 and does not test P.

### A4.1.9 Order (binding; adds a step to AD.12)

Part 1 is **AD.12 step 5a**: it runs after `analysis.json` with the P section is committed (step 3), after the step-4 secondary families
and after step 5 (PS, E-dec, E-pred), and **before** steps 6 to 9 (S2, B, R, the rest of Tier 3). Reason: it needs only stored M4 arrays
and should not wait on later GPU stages; it cannot change steps 3 to 5, and nothing in steps 6 to 9 depends on it (cut and go decisions
are time-only, AB.9). Its output `runs/P2-GATE-M4/tier3_fusion.json` is committed at once. It is run **once**; a rerun on the same inputs
must be byte-identical (SAP 10). A later bug fix follows card v4 section 7 (pre-fix output kept, both printed).

### A4.1.10 Reading and wording rules (binding)

**Reading of a contrast "comparator k minus GM" on a cell (95 percent interval, fixed now):**
- **above GM:** lower bound > 0. Wording: "on {cell}, the {comparator} of the same per-token evidence gave higher matching accuracy than
  the hard gate ({Delta}, 95% CI {L} to {U}; exploratory)".
- **not distinguishable:** the interval contains 0. Wording: "the data do not show that the hard gate adds anything beyond the
  {comparator} on {cell} ({Delta}, 95% CI {L} to {U}; n_d = {n_d}; exploratory)". Never "equivalent", never "as good as".
- **below GM:** upper bound < 0. Wording: "the hard gate gave higher matching accuracy than the {comparator} on {cell} ({Delta}, 95% CI;
  exploratory)".

**Findings against the method.** For MED, TM-G and TM20 (detector-free), "above GM" and "not distinguishable" on a P cell are **findings
against the method** and are reported as such in Results and Discussion, in the same paragraph as P. For SOFT, "above GM" is a finding
against the hard-gate design (discarding), not against the detector; "not distinguishable" reads "discounting and discarding the flagged
tokens were not distinguishable".

**Where they may appear.**
1. **Never** in the title, highlights or conclusion, under any label.
2. **Abstract:** under a P-null label (negative, inconclusive, harm, K1, R3-inconclusive) Part 1 does **not** appear in the abstract (any
   mention there would read as an explanation or a substitute headline, AB.1). Under a positive label (POS-M, POS-G, MIXED, R3-POS) the
   abstract **must** carry one limiting clause when any detector-free comparator is "above GM" or "not distinguishable" on a P cell that
   P rejected: "a detector-free {median / trimmed mean} of the same evidence was not shown to do worse (exploratory)". This is a limit on
   the positive, never a gain.
3. Never as a gain of "our approach"; the comparators are named by what they are (median, trimmed mean at the gate's flag count,
   20 percent trimmed mean, soft reliability weight), never "robust GATE", "soft GATE" or "improved gate".
4. **AB.1:** no sentence uses Part 1 to explain, predict or rescue a P result ("the gate failed because robust aggregation suffices",
   "the gate failed because the detector misses", "a soft gate would have worked"). A detector-free combiner beating NONE when GM did not
   is reported as a property of mean aggregation under this corruption, in Results under the Tier-3 label, and is not a result about GATE.
5. **R3-POS:** if $d^{\rm TM\text{-}G}-d^{\rm GM}$ has an upper bound $\ge0$ on a P cell that P rejected, the R3 positive sentence in Results and
   Discussion adds "a detector-free trimmed mean of the same size raised $d$ at least as much (exploratory)".
6. All cells and all four comparators are reported in one table (PS cells in their own table); none is dropped for its result.

### A4.1.11 Code specification (for the lead; this addendum edits no code)

New module `exp_p2/gate/tier3_fusion.py` (CLI `PY -m exp_p2.gate.tier3_fusion --run-id P2-GATE-M4 --family-run P2-GATE-M3 --cal-run
P2-GATE-M2`), CPU only, reading only the files of A4.1.2 and writing `runs/P2-GATE-M4/tier3_fusion.json`; plus
`tests/exp_p2/test_tier3_fusion.py` on synthetic data (nothing under `runs/` read). It refuses to run unless `runs/P2-GATE-M4/analysis.json`
is committed (step 3) and its P section exists. Self-tests: (a) NONE and GM recomputation equals `evidence_from_delta`; (b) TM-G with
$g=0$ or 1 equals NONE; (c) TM with 511 per tail equals MED; (d) SOFT with no flags equals NONE and with $S_{\rm cal}\equiv0$ equals GM;
(e) $w\in[0,1]$, $w=1$ off the flagged set, $w$ non-increasing in $u$ on it; (f) ties and empty sets give $Y=0$; (g) the consistency gate
stops on an injected mismatch; (h) the seed slot of a cell does not change when another cell is absent; (i) byte-identical rerun.
The module and the `seeds.ANALYSES` append are new files in the card's pin scope (A3b.7 item 1): a dated pin row and a gate-auditor match
to this section are required **before it is run**; they are not required before `analysis_m4` runs, because the specification, not
the code, is what must precede the P outcome.

---

## A4.2 Part 2: outcome book (red-team M-c, A1, A3, A4)

### A4.2.1 Labels (determined mechanically from committed files; no judgement)

Inputs: `runs/P2-GATE-M3/family.json` (`n_rule.rule` in R1, R2, R3, NO-GO; operating points) and the P section of
`runs/P2-GATE-M4/analysis.json` (`primary.per_corruption.*.gate_better`, `p_holm`, `b`, `c`; `outcome_reading.label`), plus the S-M
section for the POS split. A "harm rejection" is a Holm-adjusted p below 0.05 with $c>b$.

| Code | Condition |
|---|---|
| **POS-M** | R1/R2; at least one P rejection with $b>c$; S-M rejected for **every** such corruption (K5 and K6 not triggered for it) |
| **POS-G** | R1/R2; at least one P rejection with $b>c$; S-M not rejected (K5) or K6 for at least one such corruption |
| **MIXED** | R1/R2; at least one rejection with $b>c$ **and** at least one harm rejection. Title and highlights of MIXED; the POS-M or POS-G sentences apply to the $b>c$ corruptions |
| **NEG** | A2.2 negative (no rejection; every corruption with an operating point has its 90 percent CI inside (-0.05, 0.05) and completed $n\ge240$) |
| **INC** | A2.2 inconclusive under R1/R2 with no harm rejection and at least one operating point |
| **HARM** | R1/R2; at least one harm rejection, no rejection with $b>c$ (A2.2 label "inconclusive"; SAP 9 wording "reduced") |
| **K1** | `family.json` rule NO-GO: no corruption has an operating point; P not tested |
| **R3-POS** | R3; at least one rejection on $d$ after Holm with the $d$ difference favouring GATE-M (`gate_better`) |
| **R3-INC** | R3; no such rejection (negative is not available under R3) |

**Modifiers (apply on top of the label).** *Partial headroom:* when one or two corruptions have no operating point, every sentence names
the tested corruptions and adds "({Y}: no operating point at either severity; not tested)". *Partial fold:* a corruption with completed
$n<240$ gives INC (A2.2) and every sentence adds "partial fold (n = {n} of {planned})". *M4 not finished at the freeze:* no label is
assigned; by Shlok's D18 the deadline moves rather than a paper without M4 being submitted.

### A4.2.2 Rules common to every label

1. **Numbers.** Every `{...}` placeholder is filled only from the committed `analysis.json`, `family.json`, `tier3_fusion.json` or
   `runs/P2-GATE-M1/analysis.json`. "Matching accuracy" means the SAP's image-direction verification accuracy (`analysis_m4.WORDING_Y`).
2. **Detector wording (K2, D0074): the detector is a measured object, not the asset.** In every label: the score is "the gate's
   masked-likelihood score", never "our detector"; no sentence says it detects corrupted codes better than cheap methods; a positive is
   worded "a gate built on the masked-likelihood score raised ...", never "the detector finds corrupted tokens"; the M1 rival (texture,
   sign chosen on the data), its sign and its AUROC with CI appear in the main text; its win is reported as the label-circularity concern,
   not as evidence that texture explains anything (A1.2 rule 4).
3. **Must-not list (NOVELTY-REAUDIT section 7 items 1-9, NOVELTY-CHECK-INFFUS section 4 items 10-13).** In particular: one model only
   (UniDisc 1.4B; no "generalises", item 9); no "first" claim of items 1-4, 10, 11; no guarantee beyond "the expected flagged share of a
   clean pair's tokens is at most alpha" (item 6); "calibrated" is not a selling word in title, abstract or highlights (item 10 note);
   GATE is "input-level source validation", never "decision-level fusion" (item 13).
4. **Words reserved for a positive.** "fusion", "repair", "robust", "improves" do not appear in a title without a P rejection with $b>c$
   (red-team C.3). Under R3 neither "verification" nor "improved" appears for the primary (v3 line 213).
5. **AB.1 under every P-null label (NEG, INC, HARM, K1, R3-INC):** no clause in title, abstract, highlights, conclusion **or the opening of
   Discussion 6.1** draws on PS, S2, B, R, E-dec, E-pred, the suite, detection (S-D, S-D2, M1) or Part 1 to explain, qualify or predict
   the P result. These results appear in Results under their family label, and later in the Discussion only as separate findings.
   Never "predicted", "explained", "caused by detection", "because the detector".
6. **Highlights:** at most 85 characters each (Elsevier's limit, quoted from memory, E0; the venue scout verifies). If a filled highlight
   exceeds it, `{X}` is replaced by "{k} of 3 corruptions" and the names move to highlight 2. Highlights 2 to 5 are written later but
   obey rules 2 to 5; none of them states a secondary or Tier-3 result as a gain.
7. **Scope phrase** `{S}` = "in one pretrained unified masked diffusion model (UniDisc, 1.4B parameters) on COCO image-caption pairs with
   a random other caption as the negative".

### A4.2.3 Title, highlight 1, abstract result sentence, opening of Discussion 6.1

`{X}` = tested corruption(s) of that clause, short form "JPEG", "Gaussian noise", "splice" (severity in the abstract: "JPEG quality
{q}", "noise sigma {s}", "a {p}-pixel splice"). `{A0}`, `{A1}` accuracies of none and gate; `{D}` net difference; `{L}`, `{U}` 95 percent CI.

**POS-M**
- Title: "Masked-likelihood token gating before image-text evidence fusion: a preregistered gain under {X} in a unified masked diffusion model"
- Highlight 1: "Gating flagged image tokens raised image-text matching accuracy under {X}"
- Abstract result sentence: "In the preregistered test (exact McNemar, Holm over three corruptions), a gate built on the masked-likelihood score raised matching accuracy over no gate under {X} from {A0} to {A1} (net {D}, 95% CI {L} to {U}; n = {n}), more than an equally shaped random mask did; {for the other tested corruptions: no change was detected ({their D and CI})}. This is {S}, at one severity per corruption." Plus the Part 1 limiting clause when A4.1.10 item 2 requires it.
- Discussion 6.1 opens: "Under {X}, removing the tokens the gate flagged raised matching accuracy, and a random mask of the same shape did not; the random-mask control rules out the shape of the mask as the cause, but not the removal of low-likelihood tokens in general, and the gate's score did not beat cheap rivals at finding changed codes on JPEG and noise."

**POS-G**
- Title: "Masked-likelihood token gating raised image-text matching accuracy under {X}, but no more than a same-shape random mask: a preregistered test in a unified masked diffusion model"
- Highlight 1: "Gating raised matching accuracy under {X}, as did a same-shape random mask"
- Abstract: "... a gate built on the masked-likelihood score raised matching accuracy over no gate under {X} from {A0} to {A1} (net {D}, 95% CI {L} to {U}; n = {n}), but the gain was not distinguishable from that of a random mask of the same shape, so it is not attributed to the flagged positions. This is {S}." Plus the Part 1 clause when required.
- 6.1 opens: "Gating raised matching accuracy under {X}, but a random mask of the same shape did as well, so the gain belongs to removing a set of that shape, not to the positions the score flagged."

**MIXED**
- Title: "Masked-likelihood token gating raised image-text matching accuracy under {X} and lowered it under {Y}: a preregistered test in a unified masked diffusion model"
- Highlight 1: "Token gating raised matching accuracy under {X}, lowered it under {Y}"
- Abstract: the POS-M or POS-G sentence for {X}, followed by "and lowered it under {Y} (net {D_Y}, 95% CI {L_Y} to {U_Y})."
- 6.1 opens: "The same gate raised matching accuracy under {X} and lowered it under {Y}; the preregistered test counts both."

**NEG**
- Title: "Does masked-likelihood token gating help image-text matching under image corruption? A preregistered test in a unified masked diffusion model"
- Highlight 1: "Token gating moved matching accuracy by under 5 points under {X}"
- Abstract: "In the preregistered test, gating did not change matching accuracy detectably under {X}; for each, the 90% CI of the net difference lay inside plus or minus 0.05 ({D}, {L90} to {U90}; n = {n}), so a gain or a loss larger than 5 percentage points is excluded at this severity. This is not evidence that gating has no effect. This is {S}."
- 6.1 opens: "The preregistered test bounds the effect of gating on matching accuracy under {X} to less than five percentage points in either direction, for this model and these severities; it does not say that gating has no effect."

**INC**
- Title: as NEG.
- Highlight 1: "No detectable change in matching accuracy from token gating under {X}"
- Abstract: "In the preregistered test, no change in matching accuracy from gating was detected under {X} (net {D}, 95% CI {L} to {U}; n = {n}); the intervals are too wide to exclude a gain or a loss of 5 percentage points, so the test is inconclusive. This is {S}."
- 6.1 opens: "The preregistered test did not detect a change in matching accuracy from gating under {X}, and it cannot exclude a gain or a loss of five percentage points; we read it as inconclusive, not as evidence that gating has no effect."

**HARM**
- Title: "Masked-likelihood token gating reduced image-text matching accuracy under {X}: a preregistered test in a unified masked diffusion model"
- Highlight 1: "Gating flagged image tokens lowered image-text matching accuracy under {X}"
- Abstract: "In the preregistered test, gating reduced matching accuracy under {X} from {A0} to {A1} (net {D}, 95% CI {L} to {U}; n = {n}); {no gain was detected for the other tested corruptions}. This is {S}."
- 6.1 opens: "Under {X}, gating lowered matching accuracy relative to no gate; the preregistered test counts this against the gate."

**K1 (NO-GO)**
- Title: "Masked-likelihood token gating in a unified masked diffusion model: corruption headroom, token detection and clean false-alarm control in a preregistered measurement"
- Highlight 1: "No preregistered corruption left headroom, so the gating test was not run"
- Abstract: "No preregistered corruption met the headroom rule at either severity on separate items (headroom statistics T1 and T2 in Table {t}), so the preregistered test of gating against no gate was not run and no statement about gating and matching accuracy under corruption is made. This is {S}." The detection and calibration measurements follow as their own sentences, labelled.
- 6.1 opens: "No preregistered corruption met the headroom rule, so this paper makes no statement about whether gating changes matching accuracy under corruption; what it reports is whether the corruptions lowered the evidence, how well the gate's score finds changed codes, and whether the clean false-alarm statement held."

**R3-POS**
- Title: "Does masked-likelihood token gating strengthen image-text evidence under image corruption? A preregistered test in a unified masked diffusion model"
- Highlight 1: "Token gating raised the evidence ratio d under {X}; not an accuracy result"
- Abstract: "Too few items changed their decision under corruption for an accuracy test, so the preregistered primary endpoint switched to the per-item evidence ratio d (mean over spread of the per-token evidence). Gating raised d under {X} ({D_d}, 95% CI {L} to {U}; Wilcoxon, Holm over three; n = {n}); trimming heavy-tailed tokens raises d whatever their corruption status, so this is not a result about matching accuracy. This is {S}." Plus the Part 1 clause of A4.1.10 item 5 when required.
- 6.1 opens: "Gating raised the evidence ratio d under {X}; because d is a mean-to-spread ratio, removing heavy-tailed tokens raises it whether or not they are corrupted, and the result says nothing about matching accuracy."

**R3-INC**
- Title: as R3-POS.
- Highlight 1: "No detectable change in the evidence ratio d from token gating under {X}"
- Abstract: "Too few items changed their decision under corruption for an accuracy test, so the preregistered primary endpoint switched to the per-item evidence ratio d; gating did not change d detectably under {X} ({D_d}, 95% CI {L} to {U}; n = {n}). This says nothing about matching accuracy. This is {S}."
- 6.1 opens: "Under the preregistered switch to the evidence ratio d, gating did not detectably change d under {X}; the result says nothing about matching accuracy and is not evidence that gating has no effect."

### A4.2.4 Numbered contribution list (Introduction)

Only bullets whose cell is delivered whenever M4 is analysed (Shlok's D18: no submission without M4). Bullets 1, 2, 4, 5 and 6 are the
same for every label; bullet 3 takes the label's sentence.
1. **The measured object.** "We specify, and treat as the object of measurement, an input-level source-validation gate for a pretrained
   unified masked diffusion model: each image token is scored by the model's own masked likelihood with the caption withheld, and the
   flag threshold is set by conformal risk control on clean pairs so that the expected flagged share of a clean pair's tokens is at most
   alpha." (K2, M-b; no "first", must-not 3, 4, 10.)
2. **A closed-form condition** (theory, no data): "Under an independent-token approximation, we give the condition on the false-alarm and
   hit rates under which discarding flagged tokens raises the signal-to-noise ratio of an additive evidence sum; we state it as an
   approximation because image tokens are dependent." Never linked to a P result (AB.1).
3. **The preregistered test** (exact McNemar, Holm over three realistic corruptions, n fixed by a headroom-based rule). Label sentence:
   POS-M / POS-G / MIXED / HARM: the label's 6.1 opening, first clause; NEG: "bounds the effect to under five percentage points in either
   direction under {X}"; INC: "did not detect a change and is inconclusive under {X}"; K1: "found that no preregistered corruption left
   headroom, so the test was not run"; R3-POS / R3-INC: the R3 sentence with "evidence ratio d" and "not matching accuracy".
4. **Token detection, measured.** "At the token level the gate's score separates code-level random replacements (AUROC 0.961 for a patch
   and 0.955 for swapped codes) but is near chance on JPEG and Gaussian noise (0.561 and 0.503), below a one-pass score without
   fine-tuning (0.581 and 0.607) and a texture score whose sign was chosen on the same items (0.756 and 0.768); the preregistered
   falsifier for the score was met." Source: `runs/P2-GATE-M1/analysis.json` `table.<corr>.{q, tbv, tex_neg}.mean`; CIs in the text
   (q JPEG 0.547 to 0.575, noise 0.493 to 0.513). Splice detection is added only where splice has an operating point (it is measured
   only in M4).
5. **Calibration and fusion baselines.** "We check the clean false-alarm statement on held-out clean pairs, and compare the hard gate,
   as preregistered exploratory analyses, with a median, trimmed means and a soft reliability weight of the same per-token evidence."
   Under K1 the second half reads "... on clean pairs and on the positive-control corruptions only (no realistic cell)".
6. **Secondary families, reported as run or not run:** "re-infilling the flagged tokens (S2), combining the two directions on FOIL-COCO
   hard negatives (B), and a second, 4-bit model (run only after a positive main test)". This bullet stays true whatever is cut.

Not a bullet under any label: PS (pipeline check only, AB.1(a)), E-pred, E-dec, the suite, Omni as "generalisation", S2 or B as a
gain, Part 1 as a gain, the second mask-seed check.

### A4.2.5 Layout rule for the summary figure (and the figures around it)

1. **Summary figure = family P only**, under every label. R1/R2: one row per P1-P3, net accuracy difference GATE-M minus none with the
   95 percent (thin) and 98.33 percent (thick) bootstrap intervals, a solid line at 0 and dashed lines at plus and minus 0.05. R3: the
   mean difference in d with its 95 percent interval, **no** plus or minus 0.05 lines (the margin is defined for accuracy), and the
   trimming caveat in the caption. Rows with completed n < 240 carry an open marker and "partial (n = ...)".
2. **Hatched "not tested"** on the summary figure: a P row without an operating point ("no operating point; headroom T1 = ..., T2 = ...").
   Under K1 all three rows are hatched and a table may replace the figure.
3. **PS never shares a canvas with P**, under any label (red-team A1). PS has its own table or figure titled "Positive control (pipeline
   check)", with the AB.1(a) wording only.
4. **No detection quantity on the P canvas**, under any label: no AUROC, no rival, no "conditions (ii)/(iii)" row labels, no E-pred
   sign, no E-dec part, no Tier-3 comparator. E-pred is a table only (AB.3).
5. **Part 1** has its own figure or table titled "Exploratory: hard gate against detector-free and soft combiners of the same evidence",
   P cells and PS cells in separate panels, GM as the reference line. Never on the P canvas.
6. **Family status map (optional figure or table):** one row per family in the AD.11 order (fixed), **status only, no estimates**:
   "run, formal", "run, descriptive (n < 120)", "partial prefix", "not run (cut by time)", "not run (gatekept: P+ empty)", "untestable at
   ceiling", "pipeline defect: not run", "undecided". Every status other than "run" is **hatched "not run"** or with its status text. No
   arrows, no ordering by result.
7. **Theory frontier (red-team M-d), if made:** theory only, in the Method section, with no measured (alpha_obs, beta_obs) point on it in any
   label; a measured overlay is E-pred content and may only appear as the E-pred table.

### A4.2.6 D18 against AB.1 (needs Shlok)

**What each says.** D18 (Shlok, "All recommended", 19:14 IST, `CONFIRM-EVENING-2026-10-28.md` "Shlok's answer" item 7): "if P is null but
S2, PS and FOIL are informative, submit to Information Fusion as a 'when does input gating help' article with the null in the abstract;
if M4 cannot finish by the freeze, move the deadline rather than submit without M4." AB.1 (signed by the red team): under a P null, no
causal clause from PS, E-pred, E-dec, S2, B, R or the suite in title, abstract, highlights or conclusion; AB.1(a) bars "the gate works where
detection is easy" whether PS is met or not; AB.1(b) bars "predicted" or "explained" for any P result.

**Compatible parts:** the venue (Information Fusion), the null in the abstract, and moving the deadline rather than submitting without M4.
The outcome book above keeps all three.

**Conflict:** the framing "when does input gating help". Under a P null (NEG, INC, HARM, K1, R3-INC) the only data that could say *when*
gating helps are PS (patch and swap), S2, B, detection and E-pred, and AB.1 forbids using exactly these to explain or qualify the P result.
A title, abstract question or 6.1 opening that asks "when" would be answered either by a forbidden inference or not at all (red-team A1,
fatal-conditional). D18's own condition "S2, PS and FOIL are informative" is also unusable as a rule: under AB.1 none of them can inform P,
and "informative" is not defined.

**Reading I recommend (needs Shlok):** D18 is read as a **submission decision** (venue, null in the abstract, deadline over a paper without
M4), not as a framing decision. Under every P-null label the phrase "when does input gating help" does not appear in the title, abstract,
highlights, conclusion or the opening of Discussion 6.1; the title is the label's title of A4.2.3 (a "does ... help?" question that P itself
answers, or the K1 measurement title). The "when" question may be discussed after 6.1 only through (i) the closed-form condition (theory,
no data) and (ii) which corruptions P itself showed a change for, never through PS, S2, B, detection, E-pred or Part 1. The decision to
submit depends only on the P label and on M4 being complete, not on S2, PS or FOIL outcomes (otherwise the venue decision itself becomes
outcome-dependent). Under POS-M, POS-G and MIXED, D18 does not apply and there is no conflict; "when" may still not appear in the title
(must-not 9: one model, one severity).

**If Shlok prefers the literal D18 framing**, it needs a dated SAP addendum that amends AB.1, signed by the red team, committed before
`analysis_m4` is first run; after the P result is visible it cannot be done. I do not recommend it.

---

## A4.3 Part 3: two dated rules (2026-10-28, before any M3, M4, S2 or FOIL outcome)

### A4.3.1 (a) "No time input in the released configuration"

**Rule (binding on the paper's Method section and App. A).** The paper states, as a property of the released configuration and
checkpoint and not of UniDisc in general: "UniDisc's denoiser has no time input in the released configuration: time conditioning is off,
the official inference configuration passes a null noise level, the backbone builds no timestep embedder without time conditioning, and the
released checkpoint contains no time-embedding weights; the scorer uses the authors' null-sigma inference path." The wording "in the
released configuration" is mandatory; "UniDisc is time-free" or "time-free in general" is not allowed. App. A carries the file:line table
of REDTEAM-P2-PLAN section B, at UniDisc SHA `3ee3e47a9e64bac2fdca59957726f14723371ced`:

| Claim | Evidence (REDTEAM-P2-PLAN section B row) |
|---|---|
| time conditioning off by default; absorbing state; `subs` parameterisation; no experiment overrides it | `configs/config.yaml:12,14,15` (row 1) |
| the project composes the official demo experiments and loads `unidisc_interleaved.pt` | `runs/env-2026-10-14/scripts/unidisc_setup.py:17,30-35`; `exp001/unidisc_net.py:46-47` (row 2) |
| official inference sets `force_null_sigma` and `allow_null_sigma`; the authors' samplers pass `None` | `configs/experiments/large_scale_high_res_interleaved_inference.yaml:30-31`; `model_eval.py:2057,2086,3019,3060,3186` (row 3) |
| `forward` accepts `sigma=None` only with `allow_null_sigma` | `model.py:660-662, 691, 729` (row 4) |
| no timestep embedder or adaLN time modulation without time conditioning | `models/dit.py:1105, 1186-1188, 1377-1379`; `models/dit.py:1064-1090` (rows 5, 6) |
| `scale_by_sigma` stored, never read | `configs/model/extra_large.yaml:8`; `models/dit.py:1290` (row 7) |
| no `sigma_map`, no `adaLN_modulation` key; "sigma" absent from the checkpoint pickle | HF snapshot `2b344ca856bd108b52a2d022a3463dace131249f` (row 8) |
| `return_logits=True` returns raw backbone logits before the SUBS step | `model.py:784-788` (row 9) |

Evidence level: **E3 by the red team's code reading**, not by this author and not reproduced here. Two limits go beside it: (i) the
weight of the training mask patterns (`mask_entire_modality` 0.15 or 0.2) is not recoverable from the code (E1, section B); (ii) the
state dict is loaded non-strictly (`model_setup.py:665`, `configs/config.yaml:188`), so a silent partial load is not excluded by reading;
until a key-diff print closes it, the paper says "loaded non-strictly; missing keys not checked". The rule changes no test.

### A4.3.2 (b) FOIL (rows 10-11) before S2 (rows 8a-9)

**Assessment under AB.9.** Moving FOIL ahead of S2 is a change of **run order**, not a cut and not a go decision. AB.9 allows run and cut
decisions on time, GPU-hours and pre-written technical criteria only, and forbids reordering on a visible P result. It is therefore allowed
if (i) it is fixed now, before any S2 or FOIL outcome and before `analysis_m4` runs, (ii) its trigger is time only, (iii) it does not invert
the AD.8 priority (S2 is cut last, FOIL before it) when time is short, and (iv) no FOIL outcome can reach an S2 decision. By code reading,
FOIL has no input from M2-M4 or S2 and draws no random numbers (`exp_p2/run_gate_foil.py:1-75`), and the S2 streams are keyed by item
and `ARM_TAG` (`exp_p2/gate/arms.py:58-60`), so the order changes no number of either family. The cost to S2 is about 0.3 wall-h (CONFIRM
section 8, FOIL n = 300, estimate), about 11 S2 items at about 37.5 items per wall-h (derived from 300 items in about 8 wall-h, the same
source; an estimate, not measured).

**Rule (binding; design).**
1. **When:** at the boundary after row 7 (M5) and before row 8a, once.
2. **Before the check:** the S2 arm set (with or without I-CHG) is decided by time only and logged (A3b.2 item 6), so that no FOIL output can
   reach it.
3. **Check (time only):** FOIL goes first iff
   $t_{\rm now}+0.3\,{\rm h}+W_{\rm S2}+2\,{\rm h}\le$ the results freeze (Fri 30 Oct 2026 18:00 IST, CONFIRM "Shlok's answer" item 4), with
   $W_{\rm S2}$ = 8 wall-h for three arms or 5.2 wall-h for two arms (derived: IMPL-E's 2.6 busy GPU-h quoted in card v4 section 3, times 2
   for the 0.5 duty cycle; CONFIRM section 8 shows the same factor of about 2 for three arms, 3.9 busy against about 8 wall). If the S2 smoke
   (row 8a) has run first, $W_{\rm S2}$ may instead be 300 x the median smoke seconds per item x 2 / 3600, chosen before the smoke prints
   (state which in the log row). The 2 h margin is a design choice: it covers one guard stop and relaunch of the longest length seen so far
   (20:07 to 21:40 IST on 28 Oct, about 1.6 h; CONFIRM sections 10-11).
4. **If the check passes:** rows 10 and 11, then 8a (if not yet run), 8, 9. **If it fails:** the card order stands (8a, 8, 9, 10, 11) and the
   AD.8 cut order applies unchanged. Either way the decision, its inputs ($t_{\rm now}$, $W_{\rm S2}$ and its source, the freeze) and the result
   of the inequality are logged with the time in the ledger before row 8a or 10 starts.
5. **Analysis order unchanged:** `analysis_foil freeze` (fit pairs) may run as soon as row 10 ends (AD.12 step 2); `analysis_foil analyze`
   (the B test) stays at AD.12 step 7, after the S2 table (step 6), or at the freeze if S2 is still running or was cut. So the B outcome is
   not visible while S2 runs.
6. Nothing here changes a family, n, test, ceiling rule or wording of B or S2.

---

## A4.4 Assumptions and concerns (statistician)

1. Part 1 is meaningful only if committed before `analysis_m4`; M3 has started, so the window is open now and closes at card v4 row 6.
2. The soft weight is one fixed choice (discount the flagged tokens by their relative clean tail probability). A reviewer may want a weight
   on every token; that alternative is not computed and must not be added after M4 (it would be forking paths).
3. TM20's 20 percent default and the evidence-discounting analogy rest on citations I have not read (E0); the citation checker verifies
   them before they are cited. The rule does not depend on them.
4. Under R3 the Tier-3 accuracy contrasts will have few discordant items, so most will be "not distinguishable"; under A4.1.10 that reads as
   "no evidence the gate adds anything", which is honest but uninformative. The $d$-scale trimming control is the useful part under R3.
5. The D18 reading of A4.2.6 is a recommendation and needs Shlok's words before `analysis_m4`; until he answers, the outcome book as written
   binds (it is the AB.1-consistent reading).
6. A p-value says nothing about novelty or practical importance; with the most probable labels being INC or R3-INC (v3 section 12), the
   outcome book is mostly about saying a null well.

## A4.5 Disclosure additions (Methods and deviations box; substance binding, wording editable)

(1) The Tier-3 comparators of Part 1, their parameters and the time this addendum was committed relative to `analysis_m4`; (2) that no
p-value was computed for them; (3) the outcome book was fixed before the P result, with the D18 reading and Shlok's answer or its absence;
(4) the time-input statement with its evidence level and the non-strict-load limit; (5) whether FOIL ran before S2, with the logged check.

## A4.6 Amendment log row (for the lead to append to the SAP log by a dated row; this file does not edit the SAP)

| Date | Change | Reason | Before/after outcome data? |
|---|---|---|---|
| 2026-10-28 | Addendum A4 (separate file): Tier-3 fusion comparators MED, TM-G (floor(g_i/2) per tail), TM20 (204 per tail), SOFT (flagged tokens discounted by S_cal(u)/S_cal(tau) from M2 clean pairs) against GM and NONE, Y with paired bootstrap 95% CIs only, no p-value, d-scale trimming control, consistency gate, AD.12 step 5a, wording rules (A4.1); outcome book for POS-M, POS-G, MIXED, NEG, INC, HARM, K1, R3-POS, R3-INC with titles, highlight 1, abstract sentence, 6.1 opening, contribution list and figure layout; D18 read as a submission decision (needs Shlok) (A4.2); "no time input in the released configuration" with REDTEAM section B evidence; FOIL before S2 by a time-only check (A4.3) | red-team review REDTEAM-P2-PLAN (A1, A3, A4, A5, A8, A9, C.1 M-b to M-e, D) | before any M3, M4, S2, FOIL, Omni or suite outcome; M2 complete (values not read by the author); M1 analysed earlier (D0074); commit SHA to be added |
