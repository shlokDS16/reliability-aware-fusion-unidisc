```yaml
agent: statistician
date: 2026-10-28
brief: >
  SAP Addendum A4 for Paper 2 (GATE on UniDisc; Information Fusion). Part 1 pre-specifies the Tier-3 fusion comparators of
  red-team M-e (detector-free robust combiners, discounting of the gate-flagged tokens, reliability weighting of every token,
  the hard gate). Part 2 is the outcome book (red-team M-c, A1, A3, A4): title, highlight 1, abstract result sentence,
  Discussion 6.1 opening, contribution list and figure layout for every label of P, K1 and R3, and the D18 / AB.1 question
  for ANONYMIZED. Part 3 has two dated rules (time input of the released UniDisc configuration; FOIL before S2). Revision r1
  answers the red-team A4 signature (conditions C4-1 to C4-11).
sources_examined:
  - research/CONTRACT.md
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (sections 1-3, 4.6-11 and addenda A1, A2 (A2.x), A2-debate (AD.x), A2b (AB.x), A3, A3b, A3b.12)
  - research/paper2/prereg/PREREG-GATE-v4-2026-10-28.md (sections 1-9)
  - research/paper2/prereg/RED-TEAM-SIGNOFF-2026-10-28.md lines 382-492 ("A4 signature", commit b3504aa3) (r1)
  - research/paper2/ideation/NOVELTY-CHECK-INFFUS-2026-10-28.md (sections 0-6); research/paper2/ideation/NOVELTY-REAUDIT-GATE-2026-10-28.md (section 7)
  - research/paper2/CONFIRM-EVENING-2026-10-28.md (full)
  - research/paper2/benchmark/REDTEAM-P2-PLAN.md (sections 0, A1-A11, B, C, D)
  - research/paper2/prereg/PREREG-GATE-MUST-v3-2026-10-28.md lines 197-219
  - research/ledgers/decisions.jsonl row D0074
  - runs/P2-GATE-M1/analysis.json (table, falsifier, frozen, chance_bar_both; analysed and committed before A4, D0074)
  - runs/P2-UNIDISC-KEYCHECK/README.md (commit e954217e) (r1)
  - code read at HEAD (no edit; nothing executed except a json read and character counts): exp_p2/run_gate_m4.py, exp_p2/run_gate_m2.py 30-62, exp_p2/gate/fit_threshold.py, exp_p2/gate/calibrate.py, exp_p2/gate/pipeline.py 30-73, exp_p2/gate/scores.py 108-110, exp_p2/gate/evidence.py 29-46, exp_p2/gate/analysis_m4.py 40-150 and 220-258, exp_p2/gate/seeds.py, exp_p2/gate/arms.py 17-60, exp_p2/run_gate_foil.py 1-75, exp_p2/run_gate_s2.py (grep)
coverage: >
  Not read: the paper sources, PANEL-P2-PLAN, INFFUS-CITATIONS, spec v2, IMPL reports, Wilcox, Tukey-McLaughlin, huang2025evidential.
  Outcome firewall (author's assertion, not an attestation): no M2, M3 or M4 value was opened. For M2 I read the row count (300)
  and the existence of threshold.json. For M3 I listed file names only (at 22:41 IST: no family.json, no ps_frozen.json; no
  runs/P2-GATE-EPRED-FIT directory). No M4 directory exists. The only outcome numbers quoted are M1's (D0074).
claims:
  - statement: "Every array the Tier-3 comparators need is stored per M4 item; u is not stored but is a deterministic function of the stored B and D."
    status: supported
    evidence: "exp_p2/run_gate_m4.py:144, 149-157; exp_p2/gate/pipeline.py:30-35; exp_p2/gate/scores.py:108-110; confirmed by the red team (A4 signature, 'What I checked')"
    level: E3
    confidence: 0.9
  - statement: "Denoised conditions store Delta and codes but no B, D or flags."
    status: supported
    evidence: "exp_p2/run_gate_m4.py:144-148"
    level: E3
    confidence: 0.9
  - statement: "FOIL family B takes no input from M2-M4 or S2 and draws no random numbers."
    status: supported
    evidence: "exp_p2/run_gate_foil.py:1-75 (author's reading, not audited; E1 for the red team)"
    level: E3
    confidence: 0.75
competing_explanations: []
unknowns:
  - every M3, M4, S2, FOIL, Omni and suite outcome
  - ANONYMIZED's answer on D18 (A4.2.6; required before analysis_m4)
  - the 85-character highlight limit (E0, from memory of Elsevier's guide; the venue scout verifies)
next_test: {hypothesis: "none (plan only)", intervention: "commit A4 r1 and the C4 rows before analysis_m4; audit the Tier-3 code before it runs", primary_metric: "none", falsifier: "none", gpu_hours: 0}
```

# SAP Addendum A4 (2026-10-28, before any M3 or M4 outcome), revision r1

Author: statistician. Draft written from 22:22 IST and committed as `40828e96` (committer time 22:27:23 +0530). Revision r1 written
from 22:41 IST in answer to the red-team signature on A4 (`RED-TEAM-SIGNOFF-2026-10-28.md` lines 382-492, commit `b3504aa3`); the diff
against `40828e96` is the record of what changed. A separate file beside the SAP (the brief forbids SAP edits). **Precedence:** A4 >
A3b > A3 > A2b > A2 > A1 > SAP body (card v4 "Precedence"), only on the points listed; family P and every earlier rule stand.

## Revision r1: how each red-team condition is met

| Condition | Change in r1 | Where |
|---|---|---|
| C4-1 (F1) binding and commit order | A4 binds for its specification from its commit; the auditor's match gates only the running of the Tier-3 code. Commit-order row recorded: A4 `40828e96` (22:27:23 IST) and r1 precede `family.json`, `ps_frozen.json` and `epred_frozen.json`, none of which existed at 22:41 IST (file listing). Per the coordinator: M3 finished at 22:27 IST, the headroom script has not run, nobody has read M3 rows (the coordinator's statement; I cannot verify it). Rule: if r1 or the C4 rows are committed after any of the three files, the row lists which of their values were visible | Status block, A4.0 |
| C4-2 (F10) D18 | D18's condition restored verbatim; my rewrite of the submission condition withdrawn; "binds by default" (old A4.4 item 5) struck. ANONYMIZED's own sentence, or a dated row "no answer; the AB.1 reading binds and the submission condition of D18 is unchanged", is required **before `analysis_m4`**. A status-only definition of "informative" is proposed for his row; he may adopt or drop it | A4.2.6, A4.4 |
| C4-3 (F2) contributions | Part 1 is removed from the contribution list (it can be "not run"); bullet 6 lists only families whose status is "run"; bullet 4's one-pass comparison is limited to noise (non-overlapping marginal intervals), JPEG stated as overlapping, no paired test | A4.2.4 |
| C4-4 (F3) c > b claims | Dated reading: SAP 9 ("reduced") outranks card v4 section 2 (card precedence clause); the card's "forbidden: any claim from a rejection with c > b" is read as "no claim in favour of the gate". HARM and MIXED titles carry no claim (question title); the SAP 9 sentence appears in highlight 1, abstract and 6.1. These sentences need the red team's re-signature | A4.2.1, A4.2.3 |
| C4-5 (F4) POS-G | SAP 9 / K5 wording only: "not distinguishable from masking the same shape elsewhere", "not attributable to detection beyond mask geometry"; "no more than", "as did", "did as well", "belongs to" removed | A4.2.3 |
| C4-6 (F5) R3 harm and mixed | New labels R3-HARM and R3-MIXED; R3-INC now requires no Holm rejection in either direction | A4.2.1, A4.2.3 |
| C4-7 (F6) fusion, scope | "fusion" removed from every title (stricter than C4-7: family B is never a title result, AD.1); every title names UniDisc | A4.2.2, A4.2.3 |
| C4-8 (F8) abstract clause | The mandatory abstract clause (old A4.1.10 item 2) and the R3 Results clause (old item 5) are **struck**, not reworded: no Tier-3 result changes any P sentence, so AD.12's last sentence is not amended. The R3 trimming control is reported with the three-way reading of A4.1.10, its trigger matching its sentence | A4.1.10 |
| C4-9 (F7, F9) placement, SOFT, power, comparator set | One placement rule (own Results subsection after the preregistered families; in Discussion only after 6.1's opening, never in the paragraph that states P, never as an account of P); "property of mean aggregation" sentence struck. SOFT renamed "discounting of the gate-flagged tokens" (SOFT-G). Comparator set widened by one fully specified arm, **reliability weighting of every token** (SOFT-A, conformal p-value weight), which answers plan review A8; a sign-aware detector-free estimator is **not** added, with the reason (label leakage). Every "not distinguishable" carries n_d and the minimum detectable difference; it counts against the method only when that difference is at most 0.05; limits F7(a)-(d) disclosed beside the table | A4.1.4, A4.1.5, A4.1.10 |
| C4-10 (F13, F14) pins, seeds, FOIL rule | No `seeds.py` append (fallback seed only); the module and test file are committed only with a dated pin row moving the card's pin (card section 7) and an auditor delta check. FOIL rule: freeze fixed at Fri 30 Oct 2026 18:00 IST (a moved freeze never enters), W_S2 is a named constant, no smoke option, a stop during FOIL ends the FOIL-first order, inversion risk in the deviations box | A4.1.7, A4.1.11, A4.3.2 |
| C4-11 (F11, F12, F15) minor | Highlights rebuilt with short names and a counted fallback (all at most 85 characters); NEG: summary figure shows the 90 percent interval that carries the claim, highlight states the bound as a bound; the printed multiplicity sentence replaced by a count with "no multiplicity adjustment (SAP 7)"; bootstrap index matrix fully specified; the "no Delta distribution looked at" sentence labelled as my assertion | A4.1.7, A4.2.3, A4.2.5 |
| (not a condition) A4.3.1 limit (ii) | The non-strict load is now closed by `runs/P2-UNIDISC-KEYCHECK` (commit e954217e: 0 missing, 0 unexpected, 0 shape mismatches of 342 tensors) | A4.3.1 |
| **r2** (2026-10-29, 00:00 IST; gate-auditor note N2 of `GATE-CODE-AUDIT-TIER3-2026-10-28.md`, commit 1b9f09d9; before any Tier-3 output exists, no M4 value seen by the author) | Reading for n_d = 0 and small n_d: below 10 discordant items the bootstrap MDD is not used and the exact Clopper-Pearson bound on the discordance rate replaces it; n_d = 0 is worded "same decision on all n items" with that bound. Plus r2 notes N1 (test file name) and N3 (stop file). Nothing else in A4 changes | A4.1.10 "r2 rule for few discordant items"; "r2 notes" below |
| **r3** (2026-10-29, from 00:15 IST; red-team re-signature C4r-1 to C4r-5, `RED-TEAM-SIGNOFF-2026-10-28.md` lines 498-567; after `family.json` (R2, test fold 500) was committed and read by me, see "r3 notes"; before any M4 value or Tier-3 output exists) | G3/C4r-3: direction labels ("above", "below") and every "finding" label now come from the exact Clopper-Pearson interval of the discordant split, not from the percentile bootstrap; the bootstrap interval of the net difference stays as a description; r2 items 1-3 and 5 are superseded for labelling, a code delta is specified (A4.1.12). G1/C4r-1: POS-G sentences per corruption (S-M-rejected and S-M-unrejected corruptions named separately). G2/C4r-2: "counts this against the gate" removed; the motive phrase removed from A4.2.1; a fixed scope highlight for every label; MIXED qualifier fixed. G4/C4r-5: the n = 300 branch of r2 declared moot (n = 500 in force); how `mdd` = 0.0 is reported. G6: K1, partial headroom and all R3 labels moot under R2, R3-HARM/R3-MIXED unsigned. G7/C4r-5: partial-fold sentence made consistent with A2.2 | A4.1.10 "r3 rule"; A4.1.12; A4.2.1; A4.2.2 item 6; A4.2.3; "r3 notes" below |

I object to no condition. Two points where r1 goes beyond the letter: C4-7 (no "fusion" in any title, even if B is formal) and C4-8 (the
clause is struck rather than reworded). Both are stricter readings; the red team may relax them by a dated row.

**r2 notes (2026-10-29, gate-auditor notes N1 and N3; no rule changes).** N1: the test file is `tests/exp_p2/test_gate_tier3_fusion.py`, not
the `tests/exp_p2/test_tier3_fusion.py` printed in A4.1.11; a naming deviation with no effect on content, recorded under the actual name in
the dated pin row. N3: on a consistency-gate stop (A4.1.3; the module exits with code 3 and writes the reason to stderr only), the lead saves
the stderr to `runs/P2-GATE-M4/tier3_fusion_stop.txt` before doing anything else; that file is the text of the "pipeline discrepancy" row.

**r3 notes (2026-10-29, from 00:15 IST).** *Firewall, stated for C4r-4.* r2 (00:00 IST) postdates `family.json`, `ps_frozen.json` and
`epred_frozen.json` and edits only A4.1.10; it quoted n = 500 from the coordinator's brief, so rule R2 was known to me then. For r3 I read
`runs/P2-GATE-M3/family.json` (coordinator's permission; a frozen design file): rule R2, endpoint `d` for headroom, operating points JPEG
quality 10, noise sigma 0.1 and splice 128 px, and the headroom statistics it carries (T1, T2, D_c, the changed-code-gate discordance). No P,
PS, S-M, E-dec, E-pred or M4 value was read; nothing under `runs/P2-GATE-M4` was opened (my assertion). Consequences used in r3, all
mechanical: every corruption has an operating point, so K1 and the partial-headroom modifier cannot occur; R2 is in force, so all R3 labels
cannot occur and n = 500 (A2.2's n >= 240 threshold is unchanged). No sentence of A4.2 was chosen with knowledge of a headroom value beyond
these three facts. *Rows that are the lead's* (C4r-4): the C4-1 commit-order row with the file birth times of the re-signature; the D0076
correction (times, "explicit", who fixed "informative", what becomes of D18's "when does input gating help" frame under reading 1: it is
not used in title, abstract, highlights, conclusion or the 6.1 opening, and the D18 submission condition is otherwise unchanged); the pin
row naming `tests/exp_p2/test_gate_tier3_fusion.py`; and the route for r2 item 5, which r3 fixes as the code delta of A4.1.12 (no hand
application).

## A4.0 Status, firewall, pins, binding

**Status and firewall.** At the draft (22:22 IST) M2 had 300 rows and `threshold.json` (contents not read by me); M3 had started with 0
arrays. At r1 (22:41 IST) the M3 directory listing shows no `family.json` and no `ps_frozen.json`; no M4 or EPRED-FIT directory exists.
Nothing in A4 or r1 was chosen with knowledge of any M2, M3 or M4 value (my assertion, not an attestation). The only outcome numbers
quoted are M1's (`runs/P2-GATE-M1/analysis.json`, SHA-256 `bdc3fda3be5a36b763338c3695857e4b45ae330c40eee3c3389ffeb79aa22295`; D0074).

**Pins (before the draft).** SAP at HEAD `768e40ed`: LF `e33f078c45b92b94cbf658192e2fd815f8c6eafbffe53ba39bc0dd728982afb7`, CRLF
`d95fb87b22c8eb713d35b07a0a066c56cb250a7578e590691cdb983609ec6da6` (card v4 section 1.3). `REDTEAM-P2-PLAN.md` SHA-256
`38e1b85a575379724bd0ab840e9e4cac1d891e8d0ae26590145ec2a461ff2169`. `exp_p2/run_gate_m4.py` CRLF working tree
`0050fbf9d2f84085b5ec289692ebad93fa3d10cefccbea979098c3f16b6735df`. The SHA-256 of this file is recorded by the lead at commit time.

**Binding (C4-1).** A4 binds for its specification (Parts 1 to 3) from its commit. The gate-auditor's match of the Tier-3 code to A4.1
gates only the **running** of that code. The red-team signature binds when the C4 rows are recorded before `analysis_m4` is first run on M4
data. **Commit-order row (for the lead to record):** draft `40828e96` at 22:27:23 IST and r1 (at its commit) precede `family.json`,
`ps_frozen.json` and `epred_frozen.json`. If r1 or any C4 row is committed after one of those files, the row names the file and lists which
of its values (n-rule, operating points, PS parameters, E-pred signs) were visible to the person who finished A4.2.1 to A4.2.5. If A4 r1 is
not committed before `analysis_m4`, Part 1 is void and is not reported at all (forking paths).

Provenance tags as in the SAP: **derived**, **ASSUMED**, **design**; E-levels as in the contract.

---

## A4.1 Part 1: Tier-3 fusion comparators (red-team M-e)

### A4.1.1 Question, label, and what it is not

Question: on the same per-token evidence $\Delta_j$ and the same decision rule as family P, does the hard gate GATE-M give a different
image-direction verification accuracy from (a) detector-free robust combiners of $\Delta_j$, (b) discounting the gate-flagged tokens
instead of discarding them, and (c) reliability weighting of every token by the gate's own score?

**Label: Tier 3, exploratory (SAP 7).** Confidence intervals only; **no p-value is computed** for any contrast in this part. No multiplicity
claim (SAP 7); the output prints only the number of intervals with "no multiplicity adjustment (SAP 7)". Not a family; cannot enter P or any
secondary family; cannot rescue, explain or qualify a P result (AB.1); its comparators are never presented as "our method", "an improved
gate" or a variant of GATE (red-team C.3).

### A4.1.2 Data: run, fold, cells, items, arrays

**Run and fold.** `runs/P2-GATE-M4`, the M4 test fold of the committed n-rule (`runs/P2-GATE-M3/family.json`): 300 ids (R1, R3, NO-GO) or 500
(R2). The items are exactly those `analysis_m4` analysed for P (de-duplicated rows, `analysis_m4.load_items`, SAP 8.1).

**Cells (fixed now; which are present follows mechanically from `family.json` and `ps_frozen.json`).**
- **P cells:** the family conditions at their operating points (`corruptions.corruption_key(corr, sev)`, `exp_p2/run_gate_m4.py:108-125`,
  line 119). These carry the M-e question.
- **Clean cell** `clean`: cost of each combiner on clean pairs.
- **PS cells** `patch`, `swap`: own table, "positive-control conditions; pipeline check only"; never pooled with or plotted beside P cells.
- **Not computed:** denoised copies `<cond>_dn` (no B, D or flags stored, `run_gate_m4.py:144-148`); the text direction (no per-token text
  arrays are stored).
Under K1 (NO-GO) there are no P cells and the paper says "no realistic cell".

**Arrays, per item `runs/P2-GATE-M4/arrays/item<idx:04d>.npz`** (`exp_p2/gate/runner.py:208-209`; read the same way by `analysis_m4.py:368, 484`).
All needed arrays are stored.

| Quantity | Key | Where written | Note |
|---|---|---|---|
| per-token evidence $\Delta_j$, 1,024 float32 | `<cond>_delta` | `run_gate_m4.py:141, 144` | same deranged $c^-$ as P (`pipeline.py:44-46`) |
| GATE-M flags, alpha 0.05 | `<cond>_flag0.05` | `run_gate_m4.py:150-152, 156-157` | jittered $u$ against $\tau$, strict |
| B, D | `<cond>_B`, `<cond>_D` | `run_gate_m4.py:149, 154` | **$u$ is not stored**; recomputed bit-identically as `scores.suspicion_q(B, D)` (`scores.py:108-110`, `pipeline.py:30-35`). The jittered $u$ is not stored and not needed |
| stored arm summaries | `items.jsonl` `conds[<cond>].img.none`, `.img["gate0.05"]` | `run_gate_m4.py:173` | consistency gate only |
| flagged count | `conds[<cond>].gate["0.05"].n_flag` | `run_gate_m4.py:158` | cross-check of $g_i$ |
| calibration pool | `runs/P2-GATE-M2/arrays/item<idx:04d>.npz` `B`, `D` | `run_gate_m2.py:60` | clean pairs only |
| threshold | `runs/P2-GATE-M2/threshold.json` `thresholds["0.05"].tau`, `ids_hash` | `fit_threshold.py:34-38` | |

**Complete case per cell (SAP 8.1).** An item enters a cell iff its npz holds `<cond>_delta` with 1,024 finite values, `<cond>_flag0.05`,
and finite `<cond>_B` and `<cond>_D`. One item set per cell for every arm (paired); exclusions counted with the reason.

### A4.1.3 Consistency gate (before any comparator is computed)

For every item of every cell, recompute NONE and GM with `evidence.evidence_from_delta` (all tokens; tokens with `flag0.05` false) and compare
with the stored `img.none` and `img["gate0.05"]`: `y` equal, `mean` equal within 1e-9, and $g_i$ = `flag0.05.sum()` equal to `gate["0.05"].n_flag`.
**Any mismatch stops Part 1**; it is reported as a pipeline discrepancy and investigated against the unit tests; Part 1 runs only after a bug
fix with a dated row (card v4 section 7).

### A4.1.4 The arms (same $\Delta_j$, same item and cell; $m=1{,}024$)

Notation: $\Delta_{(1)}\le\dots\le\Delta_{(m)}$ sorted in float64; $F_j$ the stored flag; $g_i=\sum_jF_j$.

| Arm | Item margin $M_i$ | Origin |
|---|---|---|
| **NONE** (reference) | $\frac1m\sum_j\Delta_j$ | P's "none" arm |
| **GM** (hard gate, as preregistered) | mean of $\Delta_j$ over $\{F_j=0\}$ | P's GATE-M arm; no other alpha, K or seed |
| **MED** | `numpy.median` of the 1,024 values (mean of $\Delta_{(512)}$, $\Delta_{(513)}$) | detector-free |
| **TM-G** (trimmed mean at the gate's flag count) | $k_i=\lfloor g_i/2\rfloor$ removed from **each** tail | detector-free in which tokens it removes; only the count comes from the gate |
| **TM20** | $k=\lfloor0.20\cdot1024\rfloor=204$ per tail; mean of the 616 central values (derived) | detector-free |
| **SOFT-G** (discounting of the gate-flagged tokens) | $\sum_jw^{G}_j\Delta_j/\sum_jw^{G}_j$, A4.1.5 | same detector and flagged set as GM |
| **SOFT-A** (reliability weighting of every token) | $\sum_jw^{A}_j\Delta_j/\sum_jw^{A}_j$, A4.1.5 | same score as GM, no threshold |

**TM-G removes $\lfloor g_i/2\rfloor$ per tail (design)**, so the number of removed tokens matches the gate item by item and TM-G versus GM
isolates *which* tokens are removed. Retained: $m-g_i$ or $m-g_i+1$ tokens. $g_i\le1$ gives TM-G = NONE. The reading "$g_i/m$ per tail" is
not computed.

**TM20 (design, fixed without data).** The conventional default trimming of a robust location estimate (Tukey and McLaughlin; Wilcox's
robust-statistics texts; **citations E0, checked by the citation checker before use**). With TM-G and MED (= trimmed mean with 511 per tail) it
forms a fixed trimming ladder. I did not look at any M1-M4 $\Delta$ distribution (my assertion).

**Why no sign-aware detector-free estimator (C4-9, F7(a)).** The direction in which a corruption moves $\Delta_j$ is defined relative to the
**true** caption ($\Delta_j=\Lambda^{c^+}_j-\Lambda^{c^-}_j$). A combiner that uses that direction (for example, trimming only the lower tail)
raises the margin of every item towards "correct" whether or not anything is corrupted: it uses the label, which a deployable combiner does
not know. It would be label leakage, not a rival, so it is not computed. A detector-free, label-free estimator that targets the expected
**shrinkage** of $|\Delta_j|$ on corrupted tokens would rest on an untested assumption (**ASSUMED**, no data) and is not added.

**Ties and empty sets.** $Y_i=\mathbb 1[M_i>0]$; $M_i=0$, an empty retained set or a zero weight sum give $Y_i=0$ (SAP 2.1). Counted per arm and cell.

### A4.1.5 The two weights (fixed now; parameters from M2 clean pairs only)

$u_j=$ `scores.suspicion_q(B_j, D_j)` (unjittered). Clean calibration pool: all tokens of the M2 calibration items in
`runs/P2-GATE-M2/items.jsonl` (the script asserts `calibrate.ids_hash` of their `gid` list equals `threshold.json` `ids_hash`), with
$u^{\rm cal}$ = `fit_threshold.suspicion_from_arrays(arr, "q")` unjittered. All calibration items have 1,024 tokens, so the item-weighted
pooled survival function of CRC equals the token-pooled one:
$$S_{\rm cal}(x)=\tfrac1N\#\{u^{\rm cal}>x\},\qquad P_{\rm cal}(x)=\frac{1+\#\{u^{\rm cal}\ge x\}}{N+1}.$$

**SOFT-G (discounting of the gate-flagged tokens).** With $\tau$ = `thresholds["0.05"].tau`:
$w^{G}_j=1$ if $F_j=0$; $w^{G}_j=\min\{1,S_{\rm cal}(u_j)/S_{\rm cal}(\tau)\}$ if $F_j=1$ (if $S_{\rm cal}(\tau)=0$, $w^G_j=0$ for flagged $j$ and SOFT-G = GM).
Properties: $\{w^G<1\}\subseteq\{F=1\}$, so on a clean pair exchangeable with calibration the expected share of **discounted** tokens is at most
alpha (the CRC statement; nothing about the weight lost). SOFT-G versus GM isolates discount against discard with the same detector,
threshold and flagged set. **Limit (F7(b), stated wherever SOFT-G is reported):** its weights lie token by token between GM's and NONE's; it
is not reliability weighting of every token.

**SOFT-A (reliability weighting of every token; added in r1, answers plan review A8).** $w^{A}_j=P_{\rm cal}(u_j)$, the conformal p-value of
token $j$ against the clean calibration tokens (the +1 form keeps every weight in $[1/(N+1),1]$, so no token is discarded and the weight sum
is positive). No threshold, no alpha, no free parameter. Properties: on a clean token exchangeable with the pool $w^A$ is uniform on its grid,
so SOFT-A pays an efficiency cost on clean pairs (shown by the clean cell) and no bias if $u$ is unrelated to $\Delta$; on a token more
suspicious than every clean token $w^A=1/(N+1)$. It is the evidential-discounting analogue the red team names (`huang2025evidential`, unread,
E0). No other weight function is computed.

**Freeze (design).** Preferred: after `threshold.json` is committed and before the first M4 item, the lead commits
`runs/P2-GATE-M2/soft_weight_frozen.npz` (sorted pooled $u^{\rm cal}$ float32, $\tau$, $N$, `ids_hash`, SHA-256 of `threshold.json` and of the
writer). Otherwise $S_{\rm cal}$ and $P_{\rm cal}$ are computed from the M2 arrays at analysis time with the SHA-256 of every M2 npz written into
the output; both are deterministic functions of the calibration fold. Note that `runs/P2-GATE-M2` is outside the card's code pin scope;
the freeze file is a data artifact, not code.

### A4.1.6 Decision rule and metric

As P (SAP 2.1): sign of the item margin, image direction, same true and same deranged negative caption, ties and empty sets wrong.
Metric: paired accuracy $A^{\rm arm}$ on the cell's complete-case items and $\hat\Delta=A^{\rm a}-A^{\rm b}=(b-c)/n$. Reported with every
contrast: $n$, both accuracies, $b$, $c$, $n_d$, $\hat\Delta$, its 95 percent interval and its minimum detectable difference (A4.1.7).
**Under R3** this part still uses $Y$ (AB.3 item 3), plus the $d$-scale control of A4.1.8; the paper says these contrasts are not on P's R3 endpoint.

### A4.1.7 Contrasts, intervals, seeds

**Contrasts (fixed list, per cell; all reported whatever their direction):** against GM: **MED, TM-G, TM20, SOFT-G, SOFT-A minus GM**;
against NONE (context): **MED, TM-G, TM20, SOFT-G, SOFT-A minus NONE**. GM - NONE is P's contrast, quoted from `analysis.json`, not recomputed.

**Interval.** Paired percentile bootstrap, 10,000 resamples, 95 percent (`numpy.quantile` at 0.025 and 0.975, default method). For a cell with
$n$ complete items, the index matrix is `rng.integers(0, n, size=(10000, n))` with `rng = numpy.random.default_rng(child)`, items in
ascending `idx` order; one matrix per cell, shared by every arm and contrast of that cell.

**Minimum detectable difference (MDD), printed beside every interval:** $\mathrm{MDD}=(1.959964+0.841621)\cdot\mathrm{SE}_{\rm boot}=2.801585\cdot\mathrm{SE}_{\rm boot}$,
with $\mathrm{SE}_{\rm boot}$ the SD (ddof 1) of the 10,000 resampled differences (the two-sided 5 percent, 80 percent power normal
approximation; derived). It is a design sensitivity at the realised spread, not an observed power.

**Seeds (C4-10).** `seeds.py` is **not** edited. The stream is `numpy.random.SeedSequence(20261028, spawn_key=(32,))` (equal to the child an
append of `tier3_fusion` at position 32 would give, A3.7), spawned into 6 fixed slots in the order `clean, jpeg, noise, splice, patch, swap`;
an absent cell leaves its slot unused. The output records the seed and states that it is the documented fallback.

**Multiplicity (C4-11).** The output and the paper print the number of intervals reported and "no multiplicity adjustment (SAP 7)"; no
expected-false-exclusion figure is printed.

### A4.1.8 Trimming control on the evidence ratio $d$ (descriptive)

For every cell, $d=\bar\Delta_R/s_R$ (ddof 1, `evidence.py:37-41`) over the retained set of NONE, GM, TM-G and TM20, and the paired bootstrap 95
percent interval (same index matrix) of the mean of $d^{\rm TM\text{-}G}-d^{\rm GM}$ and $d^{\rm TM20}-d^{\rm GM}$, with the MDD. Items with $|R|<2$
or $s_R=0$ in either arm are dropped and counted. MED, SOFT-G and SOFT-A have no $d$ here (not defined consistently). Reason: symmetric trimming
lowers $s_R$ mechanically, so a GM rise in $d$ may be trimming (v3 line 213); TM-G is a detector-free trimming of the same count. Read with
the three-way rule of A4.1.10; it is Tier 3 and never qualifies P's sentence.

### A4.1.9 Order (binding; adds step 5a to AD.12)

Part 1 is **AD.12 step 5a**: after `analysis.json` with the P section is committed (step 3), after step 4 and step 5 (PS, E-dec, E-pred), before
steps 6 to 9. It changes no wording of step 3 (no Tier-3 clause enters a P sentence, A4.1.10), so the last sentence of AD.12 stands
unamended. Output `runs/P2-GATE-M4/tier3_fusion.json`, committed at once, run once, byte-identical on rerun; a later bug fix follows card v4
section 7 (pre-fix output kept, both printed).

### A4.1.10 Reading, placement and wording (binding)

**Three-way reading of "comparator k minus GM" on a cell (95 percent interval, fixed now):**
- **above GM:** lower bound > 0. "On {cell}, {k} gave higher verification accuracy than the hard gate ({Delta}, 95% CI {L} to {U}; exploratory)."
- **below GM:** upper bound < 0. "The hard gate gave higher verification accuracy than {k} on {cell} ({Delta}, 95% CI; exploratory)."
- **not distinguishable:** the interval contains 0. "The data do not show a difference between the hard gate and {k} on {cell} ({Delta},
  95% CI {L} to {U}; n_d = {n_d}; minimum detectable difference {MDD}; exploratory)." Never "equivalent", "as good as", "did as well".
The same rule reads the $d$ contrasts of A4.1.8, with "higher evidence ratio d" in place of "higher verification accuracy".

**What counts against the method (C4-9, F7(d)).** For MED, TM-G, TM20 (detector-free) on a P cell: "above GM" is a finding against the method;
"not distinguishable" is a finding against the method's added value **only if MDD <= 0.05** (the SAP's design margin, section 4.3); with
MDD > 0.05 it is reported as "uninformative at this n". For SOFT-G and SOFT-A: "above GM" is a finding against discarding (hard gating),
never against the detector; "not distinguishable" reads "discarding and discounting (or weighting) were not distinguishable", with n_d and MDD.

**r2 rule for few discordant items (2026-10-29, answers auditor note N2; replaces the MDD test above only when n_d < 10).** With n_d = 0
every bootstrap resample gives a difference of 0, so the interval is [0, 0] and MDD = 0: degenerate, not informative. With fewer than about
10 discordant items the resampled difference takes few values in steps of 1/n and its SD is unstable (the 10 is a design choice). Rule:
1. For every Y contrast with **n_d < 10**, the MDD is printed but labelled "not used (n_d < 10)", and the exact bound $B$ = Clopper-Pearson
   two-sided 95 percent upper limit of $n_d/n$ (`scipy.stats.beta.ppf(0.975, n_d + 1, n - n_d)`) is printed beside it. $B$ is a valid bound on
   the net difference because $|A^{k}-A^{\rm GM}|\le\pi_d$, the discordance probability.
2. **Against added value (MED, TM-G, TM20):** with n_d < 10, "not distinguishable" counts as a finding against the method's added value iff
   $B\le0.05$, otherwise it is "uninformative at this n". (Derived: $B=0.0122$ for n_d = 0 at n = 300 and $0.0074$ at n = 500; $B\le0.05$ holds
   for n_d up to 7 at n = 300 and up to 15 at n = 500, so at n = 300 an n_d of 8 or 9 is "uninformative".)
3. **Wording for n_d = 0:** "{k} and the hard gate made the same decision on all {n} items (n_d = 0); the net difference in accuracy is at most
   {B} (Clopper-Pearson 95% bound on the discordance rate; exploratory)". Never "equivalent". For SOFT-G and SOFT-A the same sentence is read
   against discarding, not against the detector. For 0 < n_d < 10 the three-way sentence above is used with {B} in place of {MDD}.
4. **$d$ contrasts (A4.1.8):** the against-method rule does not apply to them. If every paired difference is exactly 0, the output prints
   "identical on every item", a description, not a finding.
5. Where the module's `counts_against` field (MDD rule only) disagrees with this rule, this rule governs: the lead applies it from the printed
   n_d and n in the results text, or adds it to the code with a gate-auditor delta check before the output is read.

**r3 rule: exact labels for every contrast (2026-10-29; answers red-team G3, G4, C4r-3, C4r-5; supersedes r2 items 1, 2, 3 and 5 for
labelling and the bootstrap-based labels above; Tier 3 stays CIs only).** The percentile bootstrap is not a valid interval at small n_d
(red-team synthetic check: b = 4, c = 0 gives a bootstrap lower bound above 0). The labels therefore come from an exact interval
conditional on the discordant pairs, which is an interval statement, not a p-value:
1. **Exact discordant-split interval.** For "comparator k minus GM" with $b$ items where only $k$ is correct and $c$ where only GM is correct,
   $n_d=b+c$, let $\theta=b/n_d$ and $[\theta_L,\theta_U]$ its Clopper-Pearson two-sided 95 percent interval ($\theta_L=0$ if $b=0$, else
   `beta.ppf(0.025, b, n_d - b + 1)`; $\theta_U=1$ if $b=n_d$, else `beta.ppf(0.975, b + 1, n_d - b)`).
2. **Direction (replaces the bootstrap reading for labels):** **identical** if $n_d=0$; **above GM** iff $\theta_L>0.5$; **below GM** iff
   $\theta_U<0.5$; otherwise **not distinguishable**. An exact consequence (derived): with all discordant pairs on one side, "above" or
   "below" needs $n_d\ge6$ ($0.025^{1/5}=0.478$, $0.025^{1/6}=0.541$); b = 4, c = 0 is "not distinguishable".
3. **Size, printed beside every contrast:** $n$, $b$, $c$, $n_d$, the net difference $(b-c)/n$, its percentile bootstrap 95 percent interval
   (labelled "descriptive"), and the discordance bound $B$ of r2 (Clopper-Pearson 95 percent upper limit of $n_d/n$, which bounds the absolute net
   difference). The MDD is printed only for $n_d\ge10$; for $n_d<10$ the text writes "MDD not used ($n_d<10$)" in place of the `mdd` value
   (for $n_d=0$ the output's `mdd` is 0.0, which is degenerate and is never quoted as a number).
4. **What counts against the method (replaces the MDD rule and r2 item 2):** for MED, TM-G, TM20 on a P cell: "above GM" (exact) is a
   finding against the method; "identical" or "not distinguishable" is a finding against the method's added value iff the bound on GM's
   advantage is at most 0.05, where that bound is $B$ for $n_d<10$ and the MDD for $n_d\ge10$; otherwise "uninformative at this n". For SOFT-G and
   SOFT-A the same reading is "against discarding" / "discarding and discounting (or weighting) identical or not distinguishable". "below GM"
   (exact) is "the hard gate gave higher verification accuracy". **At the fold in force (n = 500)** $B\le0.05$ for every $n_d\le15$ and $B=0.0074$
   at $n_d=0$ (r2, verified by the red team), so the switch at $n_d=10$ is monotone there; the n = 300 branch of r2 (the $n_d$ = 8, 9 cliff) is
   **moot** under R2 and is not used.
5. **Wording.** "identical": the r2 item 3 sentence with {B}. "not distinguishable": the A4.1.10 sentence with n_d and {B} or {MDD} per item 4.
   "above"/"below": the A4.1.10 sentences with "(exact 95% interval for the discordant split {theta_L} to {theta_U})" added.
6. The $d$ contrasts of A4.1.8 keep the bootstrap reading (they carry no "finding" label); a contrast whose paired differences are all 0 is
   printed "identical on every item".
7. **Before the code delta of A4.1.12 is audited, Part 1 is not run** (no hand application; this fixes the route of r2 item 5 before any
   Tier-3 output exists). If the output nevertheless exists without the delta, its `reading` and `counts_against` fields are not quoted;
   cells are reported with n_d, b, c and B only (C4r-3).

**Placement (one rule; C4-8, C4-9; consistent with AB.1 item 2 and A4.2.2 item 5).**
1. Part 1 is reported in its own Results subsection, titled as exploratory, after the preregistered families; PS cells in their own table.
2. In the Discussion it may appear only after the opening of 6.1, as a separate finding, never in the paragraph that states the P result and
   never as an account of it.
3. It never appears in the title, abstract, highlights, conclusion or contribution list, under any label (the draft's mandatory abstract
   clause and its R3 Results clause are struck).
4. No sentence uses it to explain, predict, qualify or rescue a P result. A comparator that beats NONE where GM did not is reported under the
   Tier-3 label as a property of that comparator on that cell, not as an account of the P result.
5. Comparators are named only as above (median, trimmed mean at the gate's flag count, 20 percent trimmed mean, discounting of the
   gate-flagged tokens, reliability weighting of every token), never "robust GATE", "soft GATE" or "improved gate".
6. All cells and all five comparators are reported; none is dropped for its result.

**Limits printed beside the Part 1 table (F7):** (a) no sign-aware estimator, for the reason in A4.1.4; (b) SOFT-G's weights lie between GM's and
NONE's; (c) when the gate's score is near chance (M1: JPEG 0.561, noise 0.503, `runs/P2-GATE-M1/analysis.json` `table.<corr>.q.mean`) the
flagged count is close to the false-alarm count, so TM-G approximates NONE trimmed at about that count and TM-G minus GM largely repeats P's
own contrast; (d) at the realised n many contrasts may be uninformative, shown by the MDD.

### A4.1.11 Code specification (for the lead; this addendum edits no code)

Module `exp_p2/gate/tier3_fusion.py` (CLI `PY -m exp_p2.gate.tier3_fusion --run-id P2-GATE-M4 --family-run P2-GATE-M3 --cal-run P2-GATE-M2`),
CPU only, reading only the files of A4.1.2, writing `runs/P2-GATE-M4/tier3_fusion.json`; tests `tests/exp_p2/test_tier3_fusion.py` on
synthetic data. It refuses unless `runs/P2-GATE-M4/analysis.json` with the P section is committed. Self-tests: NONE and GM equal
`evidence_from_delta`; TM-G with $g\le1$ equals NONE; trimmed mean with 511 per tail equals MED; SOFT-G with no flags equals NONE and with
$S_{\rm cal}\equiv0$ equals GM; $w^G\in[0,1]$, 1 off the flagged set, non-increasing in $u$ on it; $w^A\in[1/(N+1),1]$ non-increasing in $u$; ties
and empty sets give $Y=0$; the consistency gate stops on an injected mismatch; a cell's seed slot does not change when another cell is
absent; byte-identical rerun; MDD formula on a known SD.
**Pin rule (C4-10, F13).** Both files are in the card's pre-launch scope (`exp_p2`, `tests`). They are committed **only together with a dated
pin row** that moves the card's pin to that commit after a gate-auditor delta check (card v4 section 7, as rows A-1/A-2 did), or after the
last GPU stage that runs the pre-launch check. The auditor matches the module to A4.1 before it runs. Neither is needed before
`analysis_m4`: the specification, not the code, must precede the P outcome. `seeds.py` is not changed (A4.1.7).

### A4.1.12 Code delta for r3 (for the lead; this addendum edits no code)

Against `exp_p2/gate/tier3_fusion.py` at the audited commit `00b92d4d` (read: lines 205-262). A gate-auditor delta check and a dated pin row
are required before the module runs (card v4 section 7); the new SHA replaces `00b92d4d` in the pin row.
1. Import `from scipy.stats import beta` (scipy is already used by `analysis_m4`). Constants `N_D_MDD_MIN = 10`, `ALPHA_EXACT = 0.05`.
2. New `exact_theta_interval(b: int, c: int) -> tuple[float, float]`: $n_d=b+c$; $(\text{nan},\text{nan})$ if $n_d=0$; lower $0.0$ if $b=0$ else
   `float(beta.ppf(0.025, b, n_d - b + 1))`; upper $1.0$ if $b=n_d$ else `float(beta.ppf(0.975, b + 1, n_d - b))`.
3. New `exact_reading(b: int, c: int) -> str`: "identical" if $b+c=0$; "above" if lower > 0.5; "below" if upper < 0.5; else "not_distinguishable".
4. New `discordance_bound(n_d: int, n: int) -> float`: $1.0$ if $n_d\ge n$ else `float(beta.ppf(0.975, n_d + 1, n - n_d))`.
5. `counts_against(comparator, read, mdd, n_d, B)`: `read` is the exact reading; "below" gives "gate_higher"; for `DETECTOR_FREE`: "above" gives
   "finding_against_the_method"; "identical" or "not_distinguishable" gives "finding_against_added_value" iff `(B if n_d < N_D_MDD_MIN else mdd) <=
   MDD_DESIGN_MARGIN`, else "uninformative_at_this_n"; for SOFT-G / SOFT-A: "above" gives "finding_against_discarding"; otherwise
   "discarding_and_discounting_not_distinguishable" / "discarding_and_weighting_not_distinguishable" (suffix "_identical" when `read ==
   "identical"`). "undefined" only if n = 0.
6. `accuracy_contrasts`: add per row `theta_ci95_exact` = item 2, `discordance_bound_B` = item 4, `reading` = `exact_reading(b, c)`, new key
   `reading_bootstrap` = the old `reading(lo, hi)` value, `mdd_used` = `n_d >= N_D_MDD_MIN`; pass `n_d` and `B` to `counts_against`. Keys
   `ci95`, `se_boot`, `mdd` unchanged (the text follows r3 item 3 for `mdd`).
7. `d_control`: unchanged except a contrast whose valid paired differences are all exactly 0 gets `reading = "identical_on_every_item"`.
8. Tests (`tests/exp_p2/test_gate_tier3_fusion.py`, synthetic): (b, c) = (4, 0) "not_distinguishable"; (6, 0) "above"; (0, 6) "below"; (0, 0)
   "identical"; (5, 0) "not_distinguishable"; `discordance_bound(0, 300)` = 0.0122 and `(0, 500)` = 0.0074 within 1e-4; `counts_against` for MED
   with "identical", n = 500, n_d = 0 gives "finding_against_added_value"; MED "not_distinguishable" with n_d = 12 and mdd 0.06 gives
   "uninformative_at_this_n"; a case where the bootstrap says "above" and the exact rule says "not_distinguishable" yields no "finding_against"
   label; existing tests updated for the new `reading` semantics.

---

## A4.2 Part 2: outcome book (red-team M-c, A1, A3, A4)

### A4.2.1 Labels (mechanical from committed files)

Inputs: `runs/P2-GATE-M3/family.json` (`n_rule.rule`, operating points) and the P section of `runs/P2-GATE-M4/analysis.json`
(`primary.per_corruption.*`: `p_holm`, `b`, `c` under R1/R2; `p_holm`, `mean_diff` under R3, `analysis_m4.py:119-140`), plus S-M for the
POS split. A **harm rejection** is $p_{\rm Holm}<0.05$ with $c>b$ (R1/R2) or with `mean_diff` < 0 (R3).
**Per-corruption sets (r3, C4r-1):** $X_M$ = corruptions rejected with $b>c$ for which S-M rejected (K5, K6 not triggered); $X_G$ = corruptions
rejected with $b>c$ for which K5 or K6 holds; $X_H$ = corruptions with a harm rejection. Every S-M limitation sentence names only $X_G$, and
no sentence about $X_M$ carries it.

| Code | Condition |
|---|---|
| **POS-M** | R1/R2; >= 1 rejection with $b>c$; no harm rejection; S-M rejected for every such corruption (K5, K6 not triggered); {X} = $X_M$ |
| **POS-G** | R1/R2; >= 1 rejection with $b>c$; no harm rejection; K5 or K6 for at least one such corruption. Variant **G-only** if $X_M$ is empty, **M+G** otherwise (r3, C4r-1) |
| **MIXED** | R1/R2; >= 1 rejection with $b>c$ and >= 1 harm rejection |
| **NEG** | A2.2 negative |
| **INC** | R1/R2; no rejection in either direction; not NEG; at least one operating point |
| **HARM** | R1/R2; >= 1 harm rejection; no rejection with $b>c$ |
| **K1** | rule NO-GO: no operating point; P not tested |
| **R3-POS** | R3; >= 1 Holm rejection on $d$ with `mean_diff` > 0 (`gate_better`); no harm rejection |
| **R3-HARM** | R3; >= 1 harm rejection; none with `mean_diff` > 0 |
| **R3-MIXED** | R3; at least one of each |
| **R3-INC** | R3; no Holm rejection in either direction |

**Moot under the committed rule R2 (r3, G6):** K1 and all four R3 labels cannot occur (`family.json`: rule R2, three operating points).
Their sentences stay in A4.2.3 as history, are unsigned (R3-HARM, R3-MIXED) or signed but unused, and are not used.

**C4-4 reading (dated; needs the red team's re-signature of the HARM, MIXED and R3-HARM, R3-MIXED sentences).** Card v4 section 2 forbids "any
claim from a rejection with c > b"; SAP 9 prescribes "GATE-M reduced verification accuracy" and makes the full P table required content. The
card's precedence clause ("a disagreement between this card and the SAP is a card defect") decides it: SAP 9 governs, and the card's cell is
read as "no claim in favour of the gate, and no improvement claim, from a rejection with c > b". **Title rule (r3, neutral form; C4r-2):**
a title states only the preregistered headline claim (an improvement with $b>c$, SAP 2.4); every other P result, including the SAP 9 sentence
"GATE-M reduced verification accuracy", is reported content and goes in highlight 1, the abstract and 6.1, so HARM and MIXED use the question
title QT. No evaluative verdict beyond the SAP 9 sentence is attached to a harm. The dated row settling card section 2 against SAP 9 is the
lead's (red team: SAP 9 governs). The R3 analogue is moot under R2.

**Modifiers.** *Partial headroom (moot under R2, r3):* every sentence names the tested corruptions and adds "({Y}: no operating point at
either severity; not tested)". *Partial fold (r3, G7, as A2.2):* a corruption with completed $n<240$ cannot contribute to NEG; a rejection with
$b>c$ at $n<240$ still makes the label positive (POS-M, POS-G or MIXED); a harm rejection at $n<240$ still counts as a harm rejection; with no
rejection the label is INC. Every sentence about such a corruption adds "partial fold (n = {n} of {planned})".
*M4 not finished at the freeze:* no label; per D18 the deadline moves rather than a paper without M4 being submitted.

### A4.2.2 Rules common to every label

1. **Numbers** only from committed `analysis.json`, `family.json` or `runs/P2-GATE-M1/analysis.json`. Wording follows SAP 9: "image-direction
   verification accuracy" ("verification accuracy" where space is short).
2. **Detector wording (K2, D0074): the detector is a measured object, not the asset.** "the gate's masked-likelihood score", never "our
   detector"; no "detects corrupted codes better than cheap methods"; a positive reads "a gate built on the masked-likelihood score raised
   ..."; the M1 rival (texture, sign chosen on the data), its sign and AUROC with CI are in the main text; its win is the label-circularity
   concern, not an explanation.
3. **Must-not 1-13.** One model (UniDisc 1.4B, named in every title); no "first" claims; no guarantee beyond "the expected flagged share of a
   clean pair's tokens is at most alpha"; "calibrated" is not a selling word; "input-level source validation", never "decision-level fusion".
4. **Reserved words.** "fusion" appears in **no title** (C4-7; B is never a title result, AD.1). "repair", "robust", "improves" appear in no title
   without a rejection with $b>c$. Under R3 neither "verification" nor "improved" is used for the primary (v3 line 213).
5. **AB.1 under every label without a $b>c$ rejection** (NEG, INC, HARM, K1, R3-HARM, R3-INC): no clause in title, abstract, highlights,
   conclusion or the opening of 6.1 draws on PS, S2, B, R, E-dec, E-pred, the suite, detection (S-D, S-D2, M1) or Part 1 to explain, qualify or
   predict the P result. Never "predicted", "explained", "caused by detection".
6. **Highlights** at most 85 characters (E0 limit, verified by the venue scout). Corruption names in highlights are "JPEG", "noise",
   "splice"; when a slot holds two or more corruptions it reads "{k} corruptions" with a digit ("2 corruptions"). With these substitutions every
   highlight 1 below is at most 85 characters (counted for every combination of single names and the fallback; derived). **Highlight 2 is fixed
   for every label (r3, C4r-2 scope):** "Preregistered test in one model (UniDisc 1.4B), one severity per corruption" (75 characters). Highlights
   3-5 obey items 2-5 and state no secondary or Tier-3 result as a gain.
7. **Scope** `{S}` = "in one pretrained unified masked diffusion model (UniDisc, 1.4B parameters) on COCO image-caption pairs with a random
   other caption as the negative".

### A4.2.3 Title, highlight 1, abstract result sentence, opening of Discussion 6.1

`{X}`, `{Y}`: corruption names (abstract: "JPEG quality {q}", "Gaussian noise sigma {s}", "a {p}-pixel splice"). `{A0}`, `{A1}`: accuracy of no gate
and gate; `{D}` net difference; `{L}`, `{U}` 95 percent CI; `{L90}`, `{U90}` 90 percent CI.
**Question title QT** (all labels without a $b>c$ rejection under R1/R2): "Does masked-likelihood token gating help image-direction
verification under image corruption? A preregistered test in UniDisc". **Question title QT-d** (R3-HARM, R3-INC): "Does masked-likelihood
token gating strengthen image-text evidence under image corruption? A preregistered test in UniDisc".

**POS-M** ({X} = $X_M$)
- Title: "Masked-likelihood token gating raised image-direction verification accuracy under {X} in UniDisc: a preregistered test"
- Highlight 1: "Gating raised verification accuracy under {X}, beyond a same-shape mask"
- Abstract: "In the preregistered test (exact McNemar, Holm over three corruptions), a gate built on the masked-likelihood score raised image-direction verification accuracy over no gate under {X} from {A0} to {A1} (net {D}, 95% CI {L} to {U}; n = {n}), beyond what an equally shaped random mask gives; {for the other tested corruptions: no improvement was detected ({D}, {L} to {U})}. This is {S}, at one severity per corruption."
- 6.1 opens: "Under {X}, the gate improved image-direction verification over no gate beyond what an equally shaped random mask gives; this control rules out the shape of the mask, not the removal of low-likelihood tokens in general, and the gate's score did not beat cheap rivals at finding changed codes on JPEG and noise."

**POS-G** (r3, C4r-1: the S-M limitation is attached to $X_G$ only)
- *G-only* ($X_M$ empty, {X} = $X_G$): title "Masked-likelihood token gating raised image-direction verification accuracy under {X} in UniDisc, not distinguishably from a same-shape random mask: a preregistered test"; highlight 1 "Gain from token gating under {X} not distinguishable from a same-shape mask"; abstract "... a gate built on the masked-likelihood score raised image-direction verification accuracy over no gate under {X} from {A0} to {A1} (net {D}, 95% CI {L} to {U}; n = {n}): an improvement, but not distinguishable from masking the same shape elsewhere, and therefore not attributable to detection beyond mask geometry. This is {S}."; 6.1 opens "Under {X} the gate improved image-direction verification over no gate, but the improvement was not distinguishable from masking the same shape elsewhere, so it is not attributable to detection beyond mask geometry."
- *M+G* ($X_M$ and $X_G$ both non-empty): title = the POS-M title with {X} = $X_M$; highlight 1 = the POS-M highlight with {X} = $X_M$; highlight 3 = the G-only highlight 1 with {X} = $X_G$; abstract = the POS-M sentence for $X_M$, then "Under {X_G} the gate also raised verification accuracy ({D}, 95% CI {L} to {U}), but not distinguishably from masking the same shape elsewhere, so that gain is not attributable to detection beyond mask geometry."; 6.1 opens = the POS-M sentence for $X_M$ followed by the G-only sentence for $X_G$.

**MIXED**
- Title: QT.
- Highlight 1: "Gating: verification accuracy rose under {X}, fell under {Y}"
- Abstract: the POS-M or POS-G abstract sentence for {X} (by the S-M result for {X}), then "Under {Y}, GATE-M reduced verification accuracy (net {D_Y}, 95% CI {L_Y} to {U_Y})." Then {S}.
- Qualifier (r3, C4r-2): {X} is the set rejected with $b>c$, {Y} = $X_H$. If $X_G$ is non-empty, highlight 3 is the G-only highlight 1 with {X} = $X_G$, and the abstract and 6.1 use the M+G split for {X}; "rose" in highlight 1 states the P result, and the attribution limit is in highlight 3.
- 6.1 opens: "The same gate improved image-direction verification under {X} and reduced verification accuracy under {Y}; the preregistered test reports both."

**NEG**
- Title: QT.
- Highlight 1: "Gains or losses above 5 points from token gating excluded under {X}"
- Abstract: "In the preregistered test no improvement was detected under {X}; for each tested corruption the 90% CI of the net accuracy change lay inside plus or minus 0.05 ({D}, {L90} to {U90}; n = {n}), so an improvement larger than 0.05 is excluded and a loss larger than 0.05 is excluded. This is not 'GATE-M has no effect'. This is {S}."
- 6.1 opens: "The preregistered test excludes an improvement or a loss of more than five percentage points in image-direction verification accuracy from gating under {X}, for this model and these severities; it does not show that gating has no effect."

**INC**
- Title: QT.
- Highlight 1: "No detectable change in verification accuracy from token gating under {X}"
- Abstract: "In the preregistered test no improvement was detected under {X}; the data are compatible with a net accuracy change between {L} and {U} (95% CI; n = {n}), too wide to exclude a gain or a loss of 0.05, so the test is inconclusive. This is {S}."
- 6.1 opens: "The preregistered test detected no improvement in image-direction verification accuracy from gating under {X}, and its intervals cannot exclude a gain or a loss of five percentage points; we read it as inconclusive, not as evidence that gating has no effect."

**HARM**
- Title: QT.
- Highlight 1: "Token gating reduced image-direction verification accuracy under {X}"
- Abstract: "In the preregistered test, GATE-M reduced verification accuracy under {X} from {A0} to {A1} (net {D}, 95% CI {L} to {U}; n = {n}); {no improvement was detected for the other tested corruptions}. This is {S}."
- 6.1 opens (r3, C4r-2; SAP 9 sentence only): "Under {X}, GATE-M reduced image-direction verification accuracy relative to no gate, in one model at one severity."

**K1 (NO-GO)** (moot under R2, r3; kept as history)
- Title: "Masked-likelihood token gating in UniDisc: corruption headroom, token detection and clean false-alarm control in a preregistered measurement"
- Highlight 1: "No preregistered corruption left headroom, so the gating test was not run"
- Abstract: "No preregistered corruption met the headroom rule at either severity on separate items (T1 and T2 in Table {t}), so the preregistered test of gating against no gate was not run and no statement about gating and verification accuracy under corruption is made. This is {S}." Detection and calibration follow as their own labelled sentences.
- 6.1 opens: "No preregistered corruption met the headroom rule, so this paper makes no statement about whether gating changes verification accuracy under corruption; it reports whether the corruptions lowered the evidence, how well the gate's score finds changed codes, and whether the clean false-alarm statement held."

*R3 blocks below: moot under the committed rule R2 (r3, G6); R3-HARM and R3-MIXED unsigned; none is used. Their known defects ("raises d whatever" where v3 says "can"; "verification" in the R3-POS title and abstract; "counts against the gate" in R3-HARM) are not corrected because they cannot be used.*

**R3-POS**
- Title: "Masked-likelihood token gating raised the per-item evidence ratio under {X} in UniDisc, not a verification-accuracy result: a preregistered test"
- Highlight 1: "Token gating raised the evidence ratio d under {X}; not an accuracy result"
- Abstract: "Too few items changed their decision under corruption for an accuracy test, so the preregistered primary endpoint switched to the per-item evidence ratio d (mean over spread of the per-token evidence). Gating increased the evidence ratio d under {X} ({D_d}, 95% CI {L} to {U}; Wilcoxon, Holm over three; n = {n}); trimming heavy-tailed tokens raises d whatever their corruption status, so this is not a result about verification or matching accuracy. This is {S}."
- 6.1 opens: "Gating increased the evidence ratio d under {X}; because d is a mean-to-spread ratio, removing heavy-tailed tokens raises it whether or not they are corrupted, and the result says nothing about matching accuracy."

**R3-HARM**
- Title: QT-d.
- Highlight 1: "Token gating lowered the evidence ratio d under {X}; not an accuracy result"
- Abstract: the R3 switch sentence, then "Gating lowered the evidence ratio d under {X} ({D_d}, 95% CI {L} to {U}; Wilcoxon, Holm over three; n = {n}); this is not a result about matching accuracy. This is {S}."
- 6.1 opens: "Under the preregistered switch to the evidence ratio d, gating lowered d under {X}; the result says nothing about matching accuracy and counts against the gate."

**R3-MIXED**
- Title: QT-d.
- Highlight 1: "Gating raised evidence ratio d under {X}, lowered it under {Y}"
- Abstract: the R3 switch sentence, then "Gating increased the evidence ratio d under {X} ({D_d}, CI) and lowered it under {Y} ({D_dY}, CI); trimming heavy-tailed tokens raises d whatever their corruption status; neither is a result about matching accuracy. This is {S}."
- 6.1 opens: "Under the preregistered switch to the evidence ratio d, gating increased d under {X} and lowered it under {Y}; neither says anything about matching accuracy."

**R3-INC**
- Title: QT-d.
- Highlight 1: "No detectable change in evidence ratio d from token gating under {X}"
- Abstract: the R3 switch sentence, then "No change in d from gating was detected under {X} ({D_d}, 95% CI {L} to {U}; n = {n}); this says nothing about matching accuracy and is not evidence that gating has no effect. This is {S}."
- 6.1 opens: "Under the preregistered switch to the evidence ratio d, no change in d from gating was detected under {X}; the result says nothing about matching accuracy and is not evidence that gating has no effect."

### A4.2.4 Numbered contribution list (Introduction)

Only bullets whose cell is delivered whenever M4 is analysed (D18: no submission without M4). Part 1 is in no bullet (C4-3).
1. **The measured object.** "We specify, and treat as the object of measurement, an input-level source-validation gate for a pretrained
   unified masked diffusion model: each image token is scored by the model's own masked likelihood with the caption withheld, and the flag
   threshold is set by conformal risk control on clean pairs so that the expected flagged share of a clean pair's tokens is at most alpha."
2. **A closed-form condition** (theory): "Under an independent-token approximation, we give the condition on the false-alarm and hit rates
   under which discarding flagged tokens raises the signal-to-noise ratio of an additive evidence sum; we state it as an approximation because
   image tokens are dependent." Never linked to a P result (AB.1).
3. **The preregistered test** (exact McNemar, Holm over three realistic corruptions, n fixed by a headroom rule). Label sentence: the first
   clause of the label's 6.1 opening (A4.2.3), with K1 "found that no preregistered corruption left headroom, so the test was not run".
4. **Token detection, measured.** "At the token level the gate's score separates code-level random replacements (AUROC 0.961 for a patch,
   0.955 for swapped codes) but is near chance on JPEG and Gaussian noise (0.561 and 0.503). On noise it is below a one-pass score without
   fine-tuning (0.607; marginal 95% intervals 0.493-0.513 and 0.597-0.618 do not overlap; no paired test was run); on JPEG the two overlap
   (0.561, 0.547-0.575, against 0.581, 0.569-0.593). In the preregistered comparison it is below a texture score whose sign was chosen on the
   same items (0.756 and 0.768), so the preregistered falsifier for the score was met." Source: `runs/P2-GATE-M1/analysis.json`
   `table.<corr>.{q, tbv, tex_neg}` and `falsifier`. Splice detection is added only where splice has an operating point (M4 only).
5. **Calibration, checked.** "We check the clean false-alarm statement on held-out clean test pairs." (SAP 6; computed inside `analysis_m4`.)
6. **Secondary families (status-conditional, C4-3).** The bullet names only the families among S2, B and R whose AD.11 status is "run, formal"
   or "run, descriptive", with that status; if none ran, the bullet is omitted. Families not run appear only in the deviations box. The
   status is read from the status map, never from an estimate.

Not a bullet under any label: PS, E-pred, E-dec, the suite, Part 1, Omni as "generalisation", S2 or B as a gain, the second mask-seed check.

### A4.2.5 Layout rule for the summary figure

1. **Summary figure = family P only**, every label. R1/R2: one row per P1-P3, net accuracy difference GATE-M minus none with the **90
   percent (thick)** and **95 percent (thin)** bootstrap intervals, a solid line at 0 and dashed lines at plus and minus 0.05 (C4-11: the 90
   percent interval carries the NEG claim; the 98.33 percent interval is in the P table). Fixed for every label, so the figure is not chosen by
   the result. R3: mean $d$ difference with its 95 percent interval, no plus or minus 0.05 lines, trimming caveat in the caption. Rows with
   completed n < 240: open marker, "partial (n = ...)".
2. **Hatched "not tested":** a P row without an operating point ("no operating point; headroom T1 = ..., T2 = ..."). Under K1 all three rows
   are hatched and a table may replace the figure.
3. **PS never shares a canvas with P**, any label; own table or figure "Positive control (pipeline check)".
4. **Nothing else on the P canvas**: no AUROC, rival, "conditions (ii)/(iii)" labels, E-pred sign, E-dec part or Tier-3 comparator.
5. **Part 1**: own figure or table "Exploratory: hard gate against detector-free combiners, discounting and reliability weighting of the
   same evidence", P and PS cells in separate panels, GM as reference, the F7 limits in the caption.
6. **Family status map (optional):** one row per family in AD.11 order, status only, no estimates; every status other than "run" hatched
   with its text ("not run (cut by time)", "not run (gatekept: P+ empty)", "untestable at ceiling", "pipeline defect: not run", "undecided",
   "partial prefix", "run, descriptive (n < 120)").
7. **Theory frontier (M-d), if made:** theory only, in the Method section; no measured point on it under any label.

### A4.2.6 D18 against AB.1 (needs ANONYMIZED before `analysis_m4`)

**D18 verbatim** (CONFIRM-EVENING "ANONYMIZED's answer", item 7, read from his "All recommended" at 19:14 IST): "if P is null but S2, PS and FOIL
are informative, submit to Information Fusion as a 'when does input gating help' article with the null in the abstract; if M4 cannot finish
by the freeze, move the deadline rather than submit without M4." The alternatives offered in CONFIRM section 7 were "a short CPU-only
feasibility note, or another venue". **D18's condition stands as his decision**; the draft's rewrite of it is withdrawn.

**AB.1 (signed):** under a P null, no causal clause from PS, E-pred, E-dec, S2, B, R or the suite in title, abstract, highlights or conclusion;
AB.1(a) bars "the gate works where detection is easy" whether PS is met or not; AB.1(b) bars "predicted" or "explained" for any P result.

**Where they meet.** Compatible: the venue, the null in the abstract, moving the deadline rather than submitting without M4. In tension: the
framing "when does input gating help". Under a P null the data that could say *when* are PS, S2, B, detection and E-pred, which AB.1 bars from
explaining or qualifying P. Two readings are admissible under the signed rules (red team, F10(c)):
- **Reading 1 (stricter; the one the outcome book above is written to):** the phrase does not appear in the title, abstract, highlights,
  conclusion or the opening of 6.1 under a P-null label; the "when" question is discussed after 6.1 only through the closed-form condition
  (theory) and the P table itself.
- **Reading 2:** a question-form framing ("when does input gating help?") whose answer is a set of separately labelled family results, with no
  causal clause and no use of PS as a demonstration. This is allowed by AB.1's letter; the red team notes it as admissible.
Which one is wanted is ANONYMIZED's call.

**Definition of "informative" offered for his row (status only, no estimate):** S2, PS and FOIL are each "informative" iff their AD.11 status
is "run, formal" (S2 and B: completed n >= 120 and tested; PS: both cells tested); "run, descriptive", "partial prefix", "untestable at
ceiling", "not run" and "pipeline defect" are not. He may adopt it, change it, or drop the condition.

**Required before `analysis_m4` (C4-2).** A dated row with ANONYMIZED's own sentence choosing reading 1 or 2 and recording the D18 condition (with
the definition of "informative", or its removal), **or** a dated row by the lead: "no answer; the AB.1 reading binds and the submission
condition of D18 is unchanged". Under "no answer", reading 1 governs the wording (it is the reading that is certainly inside AB.1), and D18's
submission condition stands as recorded. "All recommended" is not an answer to this question (it predates it). Under POS-M, POS-G and MIXED,
D18 does not apply; "when" does not appear in a title under any label (must-not 9). Changing AB.1 itself would need a dated SAP addendum signed
by the red team before `analysis_m4`; I do not recommend it.

---

## A4.3 Part 3: two dated rules (2026-10-28, before any M3, M4, S2 or FOIL outcome)

### A4.3.1 (a) "No time input in the released configuration" (signed as written; limit (ii) updated in r1)

**Rule.** The paper states, as a property of the released configuration and checkpoint, not of UniDisc in general: "UniDisc's denoiser has no
time input in the released configuration: time conditioning is off, the official inference configuration passes a null noise level, the
backbone builds no timestep embedder without time conditioning, and the released checkpoint contains no time-embedding weights; the scorer
uses the authors' null-sigma inference path." "In the released configuration" is mandatory; "UniDisc is time-free" is not allowed. App. A
carries the file:line table of REDTEAM-P2-PLAN section B at UniDisc SHA `3ee3e47a9e64bac2fdca59957726f14723371ced`:

| Claim | Evidence (REDTEAM-P2-PLAN section B row) |
|---|---|
| time conditioning off; absorbing state; `subs`; no experiment overrides it | `configs/config.yaml:12,14,15` (row 1) |
| project composes the official demo experiments, loads `unidisc_interleaved.pt` | `runs/env-2026-10-14/scripts/unidisc_setup.py:17,30-35`; `exp001/unidisc_net.py:46-47` (row 2) |
| official inference sets `force_null_sigma`, `allow_null_sigma`; samplers pass `None` | `configs/experiments/large_scale_high_res_interleaved_inference.yaml:30-31`; `model_eval.py:2057,2086,3019,3060,3186` (row 3) |
| `forward` accepts `sigma=None` only with `allow_null_sigma` | `model.py:660-662, 691, 729` (row 4) |
| no timestep embedder or adaLN time modulation without time conditioning | `models/dit.py:1105, 1186-1188, 1377-1379`; `models/dit.py:1064-1090` (rows 5, 6) |
| `scale_by_sigma` stored, never read | `configs/model/extra_large.yaml:8`; `models/dit.py:1290` (row 7) |
| no `sigma_map` or `adaLN_modulation` key; "sigma" absent from the pickle | HF snapshot `2b344ca856bd108b52a2d022a3463dace131249f` (row 8) |
| `return_logits=True` returns raw logits before the SUBS step | `model.py:784-788` (row 9) |

Evidence level E3 by the red team's code reading, not reproduced by me. Limits beside it: (i) the weight of the training mask patterns
(`mask_entire_modality` 0.15 or 0.2) is not recoverable from the code (E1); (ii) **updated in r1:** the non-strict load is closed for the DiT
backbone by `runs/P2-UNIDISC-KEYCHECK` (commit e954217e, E4 per its README: 342 of 342 tensors matched, 0 missing, 0 unexpected, 0 shape
mismatches); the VQ tokenizer is loaded by another path and is not covered, and key equality does not show the values are the intended final
weights. The paper says so in those words. The rule changes no test.

### A4.3.2 (b) FOIL (rows 10-11) before S2 (rows 8a-9), revised in r1 (C4-10, F14)

**Assessment under AB.9.** A change of run order, not a cut and not a go decision; allowed if fixed now, time-only, without discretion, not
inverting the AD.8 priority when time is short, and with no FOIL outcome able to reach an S2 decision. By my reading of
`exp_p2/run_gate_foil.py:1-75` FOIL takes no M2-M4 or S2 input and draws no random numbers, and S2 streams are keyed by item and `ARM_TAG`
(`exp_p2/gate/arms.py:58-60`); this reading is E3 by me and unaudited (E1 for the red team), so the gate-auditor confirms it before row 10 runs
early; if the auditor does not confirm it, the card order stands. Cost to S2: about 0.3 wall-h (CONFIRM section 8, estimate).

**Rule (binding; design; no free choice left).**
1. **When:** once, at the boundary after row 7 (M5) ends and before row 8a starts.
2. **First:** the S2 arm set (with or without I-CHG) is decided by time only and logged (A3b.2 item 6).
3. **Inequality:** FOIL goes first iff $t_{\rm now}+0.3\,{\rm h}+W_{\rm S2}+2\,{\rm h}\le$ **Fri 30 Oct 2026 18:00 IST** (fixed here; a freeze moved
   later, under D18 or otherwise, never enters this inequality). $W_{\rm S2}$ is the named constant **8.0 wall-h** if the logged arm set has
   three arms, **5.2 wall-h** if two (5.2 derived as 2 x 2.6 busy GPU-h, IMPL-E row 8 as quoted in card v4 section 3, at the 0.5 duty cycle;
   8.0 from CONFIRM section 8). The S2 smoke is not an input. The 2 h margin (design) covers one guard stop and relaunch of the longest length
   seen so far (20:07 to 21:40 IST on 28 Oct, about 1.6 h, CONFIRM sections 10-11); it does not cover a crash, see item 5.
4. **If true:** rows 10, 11, then 8a, 8, 9. **If false:** card order (8a, 8, 9, 10, 11), AD.8 cut order unchanged. The decision, $t_{\rm now}$, the
   arm set, $W_{\rm S2}$ and the result are logged with the time before row 8a or 10 starts.
5. **Stops and crashes:** if any guard stop or crash-log event occurs while row 10 or 11 runs, the FOIL-first order ends: on relaunch S2 (8a,
   8, 9) runs next, and the unfinished FOIL rows wait behind S2 in the AD.8 cut order. A stop during S2 after FOIL finished changes nothing.
   The **inversion risk** (FOIL complete, S2 partial after a later stop) is declared in the deviations box whenever FOIL ran first.
6. **Analysis order unchanged:** `analysis_foil freeze` may run when row 10 ends (AD.12 step 2); `analysis_foil analyze` stays at AD.12 step 7,
   after the S2 table or at the freeze if S2 is unfinished or cut.
7. No family, n, test, ceiling rule or wording of B or S2 changes.

---

## A4.4 Assumptions and concerns (statistician)

1. Part 1 is close to non-discriminative at n = 300 when the gate's score is near chance (F7); the MDD column makes that visible, and the
   reading rule stops low power being reported as a finding against the method.
2. SOFT-A adds one comparator in r1 (before any M3/M4 value); no other weight or estimator may be added after M4.
3. The TM20 default and the evidential-discounting analogy rest on unread citations (E0).
4. The C4-4 reading (SAP 9 over the card for a c > b rejection) needs the red team's re-signature of the HARM, MIXED, R3-HARM and R3-MIXED sentences
   before `analysis_m4`; until then, under C4-4's own rule, no title or highlight may be drawn from a harm and only the P table with the SAP 9
   sentence stands.
5. D18 needs ANONYMIZED's sentence or the lead's dated "no answer" row before `analysis_m4` (C4-2). (The draft's item 5, "binds by default", is struck.)
6. The FOIL-order rule depends on an unaudited reading of the FOIL runner; the auditor's confirmation is a precondition.
7. A p-value says nothing about novelty or practical importance; the most probable labels are INC or R3-INC (v3 section 12).

## A4.5 Disclosure additions (Methods and deviations box; substance binding, wording editable)

(1) The Tier-3 comparators, their parameters, the fallback seed, and the commit times of A4 and r1 relative to `family.json` and
`analysis_m4`; (2) no p-value computed for them, number of intervals, no multiplicity adjustment; (3) the outcome book fixed before the P
result, ANONYMIZED's D18 answer or the lead's "no answer" row, and the C4-4 reading; (4) the time-input statement with its evidence level and the
key-check result; (5) whether FOIL ran before S2, the logged inequality, and the inversion risk.

## A4.6 Amendment log rows (for the lead to append by dated rows; this file does not edit the SAP)

| Date | Change | Reason | Before/after outcome data? |
|---|---|---|---|
| 2026-10-28 | Addendum A4 draft (`40828e96`): Tier-3 comparators, outcome book, time-input and FOIL-order rules | red-team plan review REDTEAM-P2-PLAN | before any M3, M4, S2, FOIL, Omni or suite outcome; commit 22:27:23 IST |
| 2026-10-28 | A4 revision r1: binding clause and commit-order row (C4-1); D18 restored verbatim, ANONYMIZED's sentence or a "no answer" row before analysis_m4 (C4-2); contribution list without Part 1, status-conditional secondary bullet, TbV claim limited to noise (C4-3); SAP 9 over card for c > b, no harm in titles (C4-4); POS-G in SAP 9 / K5 words (C4-5); R3-HARM and R3-MIXED labels (C4-6); no "fusion" in any title, UniDisc named (C4-7); abstract and R3 Tier-3 clauses struck (C4-8); one placement rule, SOFT-G renamed, SOFT-A added, sign-aware estimator excluded with reason, MDD and the 0.05 rule (C4-9); no seeds.py append, pin row before the module, fixed FOIL inequality with named W_S2 and stop handling (C4-10); highlights at most 85 characters, 90 percent interval on the summary figure, multiplicity count only, bootstrap matrix specified (C4-11); key-check result in A4.3.1 | red-team A4 signature, conditions C4-1 to C4-11 (`b3504aa3`) | before `family.json`, `ps_frozen.json`, `epred_frozen.json` and any M4 item (none existed at 22:41 IST); M3 finished 22:27 IST with headroom not run and no M3 row read (coordinator's statement); commit SHA to be added |
