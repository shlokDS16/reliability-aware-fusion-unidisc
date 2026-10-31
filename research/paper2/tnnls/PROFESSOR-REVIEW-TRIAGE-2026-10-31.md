# Expert triage of the professor's technical comments (2026-10-31)

The critique is in `PROFESSOR-REVIEW-2026-10-31.md` (verbatim). The triage was done by the red-team agent (Sonnet) acting as an expert
panel (statistician, ML experimentalist, TNNLS area chair). The lead saved the agent's returned text, condensed; no fact was changed.

**Counts (12 concerns + 9 questions = 21):**

| Class | Concerns | Questions | Total |
|---|---|---|---|
| A, already answered in the paper | 8 | 0 | 8 |
| B, fixable in the text now | 3 | 6 | 9 |
| C, needs a new experiment | 1 | 3 | 4 |
| D, invalid | 0 | 0 | 0 |

One clause is a misreading: "detection analyses explain why gating may be ineffective". The paper does not make that explanation, and
AB.1 forbids it.

## Verified facts
1. **PS (positive control) did not reject** (`runs/P2-GATE-M4/analysis.json` `ps`):
   - patch: b = 2, c = 2, n_d = 4, p = 1.0;
   - swap: b = 8, c = 5, n_d = 13, p = 0.581;
   - the A2.3 audit found no defect (0 mismatches in 500 items).
2. **Why PS could not reject** (`runs/P2-A23-AUDIT/a23_ps_audit.json`; not yet stated in the paper):
   - with no gate, the corruption changed only 5 (patch) and 9 (swap) of the 500 decisions;
   - a perfect gate that restored every clean decision gives b/c 5/0 (p = 0.0625) and 7/2 (p = 0.18);
   - the changed-code arm gives 4/2 (p = 0.69) and 7/4 (p = 0.55);
   - realised discordance was 0.008 and 0.026, against 0.05-0.20 assumed in AD.4;
   - so a power limit, not a defect. This answers Q1.
3. **u_j = D_j - B_j** is correct as stated.
4. **Detection AUROC** (`runs/P2-GATE-M1/analysis.json`): JPEG 0.561 [0.547, 0.575], noise 0.503 [0.493, 0.513]. "Weak" is more exact
   for JPEG, but "near chance" is fixed wording (D0074/K2).
5. **Timestamp:** the first push to GitHub was 2026-10-30 13:55 UTC (19:25 IST), after both studies. The Zenodo DOI is a draft, and a
   reserved DOI is not a timestamp. No independent record can predate the data.
6. **Oracle changed-code gate** (supplement Table S12, changed-code gate minus no gate):
   - JPEG -0.084 [-0.122, -0.046];
   - noise +0.070 [0.036, 0.104];
   - splice +0.004 [-0.010, 0.018].
   Detection is a bottleneck only under noise; under JPEG and splice even exact labels do not help. This answers Q7 without a run.
7. **Study 1 under noise:** GATE-M and no gate decided identically on all 500 items; the +-0.05 margin was reached with zero
   discordant items.
8. **Agent's own CPU computation, not stored** (store it under `runs/` before any use): LRF gain under noise minus gain on clean
   0.038 (-0.002 to 0.080).

## Classification
- **Class A (answered in the paper; possibly add a pointer):**
  - T1: the lemma is not validated on the model (IV-A says so);
  - T2: weak detection (contribution 2, IV-C4, Table S11);
  - T4: the preregistration is self-hosted (III-E, VI-C);
  - E1: trained on the tested corruption (VI-C, abstract);
  - E2: one backbone, one dataset (VI-C, VI-B);
  - E3: CLIP/SigLIP saturate (V-E, VI-C);
  - E4: linear logit and denoiser (V-H, VI-C);
  - R1: token-level alternatives are exploratory (attention-pooling MIL is in Table IV; dropout decoding is an autoregressive decoding
    method with no verification decision).
- **Class B (fix in the text):** T3/Q1 (F1), C1 (pointers), C2 (cuts, F9), Q3 (F3), Q5 (F5), Q7 (F4), Q8 (F6), Q9 (F2).
- **Class C (experiments):**
  - R2 and Q2: severity sweep, **GO**;
  - Q4: cross-backbone, **NO-GO**. The 4-bit Omni adapter was never checked on the GPU, quantisation confounds a likelihood score, and
    LRF would need refitting;
  - Q6: Flickr30K or hard negatives, **NO-GO**. Family H already failed on headroom, and a new builder plus leak test is too much for the
    window;
  - Q7 variant (a learned detector): **NO-GO**, the oracle bound already answers it;
  - Q5 (DUEL exact likelihood): **NO-GO**, future work. DUEL is an E1 summary only, so do not cite it until it is read.

## Text fixes (in priority order; respect the 15-page cap, AB.1 and A6.12)
- **F1 (high):** a labelled post hoc paragraph in IV-C3 giving the PS power diagnosis.
  - Numbers from item 2 above, with n_d = 4 and 13 printed (AD.4).
  - "this control does not separate a working pipeline from a defective one and is not read as validating it".
  - No mechanism claim about P. Extend the note under Table S10.
- **F2 (high):** replace "LRF adds no network row" in V-F with an itemised compute count.
  - The unweighted sum needs the 2 caption-visible passes.
  - The LRF features need the 8 complementary-mask passes plus 1 per condition (`exp_p2/run_gate_lrf_rescore.py` docstring); verify
    against the L1 runner and `items.jsonl` first.
  - Time the CPU scorer once on the stored arrays.
  - One hedged grid-size sentence.
- **F3 (medium-high):** V-H, Q3: "Nothing here favours the additive form over a linear logit; the confirmed object is the frozen
  weighting." Add that LRF was chosen by inner CV among four families on the design items (V-A), and that the learned shapes are
  descriptive (S-IV).
- **F4 (medium):** Q7 oracle sentence, Study 1 only (IV-C5 or VI-A), with the encoder-instability caveat and Table S12. Never put it
  beside LRF's 0.069 (A6.12).
- **F5 (medium):** III-B: "The sum of one-pass conditionals is a factorised surrogate for the joint log-likelihood ratio; an exact ordered
  likelihood was not computed."
- **F6 (medium):** III-E, after "no third-party timestamp exists": "The repository history was first pushed to a hosting service on
  30 October 2026, after both studies had been run; its push log is the only third-party record." Do not mention the Zenodo DOI as a
  timestamp.
- **F7 (low-medium):** the difference-in-differences sentence, only after a stored script and run under `runs/` reproduces it.
- **F8 (low):** VI-C Study 1 limitation: the +-0.05 margin was reached with no discordant item under noise. Check against A4.2.2 first.
- **F9 (cuts to pay for F1-F6, about 14 lines):**
  - move eqs. (8)-(10) and the three consequences of Lemma 1 to S-II, keeping a two-sentence statement;
  - consider cutting the qualitative figure (descriptive; Shlok asked for it, so the lead decides);
  - trim Table I to a pointer;
  - reword contribution 1 if needed.

## Experiments
- **E1, severity sweep: GO.** Frozen LRF and the unweighted sum on the 450 fold images at sigma 0.05 and 0.2 (0.3 if cheap).
  - Exploratory, intervals only, plan committed before the run.
  - About 1-1.5 h of GPU wall time; reuse the LG/DN driver pattern.
  - Value medium-high (Q2 is the most likely reviewer request).
  - Report a harm if found.
- **E2, CPU items: GO.** The difference-in-differences (F7) and scorer timing (F2), via stored scripts.
- **E3-E6: NO-GO** (see Class C above); state them as limitations.

## Calibrated assessment for TNNLS (judgement; no verified base rate)
| | Range |
|---|---|
| Desk-rejection risk | 25-40% |
| Acceptance as is | 6-14% overall (10-20% if it reaches review) |
| Acceptance after the text fixes and the severity sweep | 8-18% overall |
| Acceptance with a second backbone and a second dataset (not feasible in this window) | 15-30% overall |

The desk-rejection risk comes from the "not incremental" Full Paper criterion: a learned reweighting, one model, one dataset, a task
CLIP solves, and a negative first study. Scope fit is acceptable.

## Further points a hostile AC may raise
- The Study 1 negative is close to foreordained (F8).
- LRF's gain is positive on clean images too (+0.031), so the noise-specific part is marginal.
- Practical significance is limited next to the reference encoders, the denoiser and the linear logit.
