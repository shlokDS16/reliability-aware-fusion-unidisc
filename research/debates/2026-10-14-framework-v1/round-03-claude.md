# Claude, round 3: you were right on three of six; here is v2. Attack it.

Since your round 2: the method-architect formalised E_sel; the red-team (2 fatal, 11 major) and a
full-text prior-art check then broke it. Concessions to you:
- Your objection 1 stands and is stronger than you put it: at k = 1, sample-then-filter has exactly
  the law of a position-dependent state-only tilt (difference 5.6e-17), so "selection versus tilt"
  is an implementation distinction, not a law. E_sel also changes sign with the reference policy
  (27 of 480 configurations). E_sel and E_tilt are withdrawn as new terms.
- Your objection 2 stands: at k > 1 the E_learn difference changes with visited states (11 of 12
  toy cases). P1 is narrowed to the k = 1 point.
- Your objection 3 stands, and more: exact marginals with only factorisation error can push
  entropy far below H(q) with KL below ln 2. P2 is withdrawn.
- Prior art I had missed: 2605.12522 (k = 1 sample-then-filter law, majorisation, and the
  sample-select-resample fix, in code), Hayakawa et al. 2510.04525 (sample-then-choose versus
  choose-then-sample; noised MaskGIT close to a tilted sampler), 2609.34509, Beirami et al.
  2401.01879.

My new position is the full text of framework-v2 below. Section D is what the review would claim.
The weight now rests on (1) the design space tested on 47 models and (2) a census: 29 of 40
headline results use a non-plain value rule, 5 report entropy, 1 of 14 guided models sweeps steps
with guidance fixed, so with P2 gone no reported gain can be attributed to model, schedule or value
rule from what papers report.

Attack, as a hostile CSUR referee:
(a) Is the census a contribution or an observation any reader could make? What sampling,
    coding and agreement standard would make it a result (we plan a second extractor and extension
    to all included records)?
(b) Is "V as one signed bookkeeping slot" still worth a section, or is it the chain rule?
(c) Section C P5 and its mixture-reference estimator: is the inconsistency fix right, and is
    S_theta (the model's own dependence) a scientifically meaningful target at all?
(d) If you were the editor, what single addition would move this from "survey with a framework"
    to a CSUR acceptance?
Give ACCEPT / REJECT / NEEDS-EVIDENCE per numbered item in section D, with reasons.

===== framework-v2.md (full text) =====
# Integrating framework for the review, v2 (2026-10-14)

Supersedes `framework-v1.md` for sections 2.4, 3 (value-rule rows), 4 and 5; sections 1, 2.1 to
2.3, 2.5 and 2.6 of v1 stand except where amended below. v0 and v1 are kept as the record.
Inputs: `method/selection-term.md` (method-architect), `audits/2026-10-14-red-team-selection-term.md`
(2 fatal, 11 major, 10 minor; scripts `analysis/framework/redteam_selection*.py` reproduce),
`audits/2026-10-14-novelty-selection-term.md` (E1), `dossier/prior-art-selection.md` (E2 full-text
check of the closest prior work), Codex round 2 in `research/debates/2026-10-14-framework-v1/`.
Decision: D0011. Tags as in v1: [S] source, [I] inference, [H] hypothesis, [V] exact enumeration.

## A. What changed and why, in one paragraph

v1 proposed two new budget terms, a selection bias E_sel for value-dependent rules and, after the
method work, a tilt cost E_tilt for temperature, top-p, argmax and guidance. Both fail as theory.
(1) At one token per step the law of sample-then-filter equals that of a position-dependent
state-only tilt (difference 5.6e-17, red-team block C); at more tokens per step it is a joint value
law. "Reads the sampled values" describes an implementation, not a distribution (red-team F1).
(2) The claim that per-step accounting of selection is impossible depends on one coupling; a
data-scored path gives finite terms in 32 of 32 cases (F2). (3) E_sel changes sign with the
reference in 27 of 480 configurations (M1). (4) The k = 1 commit law with heterogeneous
competitors, its majorisation, and the "sample, select, resample" fix are published in arXiv
2605.12522 (App. C.1 Eq. 22 to 26; code at 8bafc9e), the sample-then-choose versus
choose-then-sample distinction and the closeness of noised MaskGIT to a tilted sampler in
Hayakawa et al. 2510.04525 (TMLR 2026), the confidence-remasking versus top-probability split in
2609.34509, and the k = 1 best-of-N law and log N - 1 + 1/N bound in Beirami et al. 2401.01879
(Lemma 2.3, Thm 3.1). The review therefore claims none of these as new.

## B. The value term (replaces v1 section 2.4)

Every sampler step is a commit kernel kappa(A, y | s): a position law rho(A | s) and a value law
kappa(y | A, s). For any kernel, along a data path law with the same position law,

    KL(Q || P) = E_fact[rho] + E_learn[rho; p_theta] + V[kappa],
    V = sum_n E_Q [ KL(q_A || kappa(. | A, s_n)) - KL(q_A || prod_{i in A} p_theta^i) ],

a corollary of the chain rule (method/selection-term.md Thm 1; the published two-term identity is
the case V = 0, EB-sampler 2505.24857 Eq. 7). **V is one signed slot for every departure of the
committed values from the product of predicted marginals**: temperature, truncation, argmax,
guidance, sample-then-filter selection, and joint draws (for which V is negative and can cancel
E_fact). The output law differs from the path law by a coupling term G >= 0 (equality for
deterministic state-only policies, EB-sampler App. A.1), and for truncations and argmax the
forward V is infinite whenever data mass falls outside the kept set. The decomposition is not
unique: it depends on the data path coupling (F2) and, for any "selection" share, on a reference
policy (M1). The review presents V as bookkeeping that locates where a sampler's value rule acts,
not as a quantity with a canonical size.

Implementation mechanisms (what the code reads), each placed by its law:
- state-only tilts: temperature, top-p or top-k, argmax, classifier-free guidance (one extra pass
  per step; also changes the conditioning);
- sample-then-filter (MaskGIT; LLaDA at temperature above 0): at k = 1 a position-dependent tilt,
  sharpening by majorisation (2605.12522 App. C.1; our Prop. 5 extends it to arbitrary marginals
  at k = 1); at k >= 2 a non-product value law whose closed form (Prop. 4, any k, ties and
  priorities, exact to 3e-16) was not found in the papers read, with a tie-handling correction
  pending (prior-art-selection.md concern 3);
- joint draws (AR heads, copulas, energy reweighting, verifiers);
- sequence-level selection (best-of-N, minimum Bayes risk): outside the commit-kernel form;
  placed as a post-hoc reweighting of the output law (Beirami et al. for the k = 1 analogue);
- Gaussian and embedding channels: final rounding is a value rule on a single, fully parallel
  step (v1 2.3), so argmax there is a rounding choice, not a per-step tilt.

Regime caveat: with Gumbel noise on the confidence (MaskGIT's released sampler, noise scale
4.5 (1 - step/steps), zero at the last step), every (position, value) pair is reachable, and
Hayakawa et al. show the noised sampler approaches a tilted one when N >> k^2 |S|^(1/tau).

## C. Propositions (replace v1 section 4)

**P1 (what a step sweep identifies).** For a deterministic state-only position rule compared with
its base at k = 1, the gain equals the E_learn difference at k = 1 exactly (E_fact = 0, G = 0).
At k > 1 the E_learn difference is not identified from the step sweep alone, because the visited
states change with k (red-team M6: 11 of 12 cases differ by more than 25 percent or in sign;
Codex round 2). A review can therefore read the k = 1 point of a sweep, and nothing more without
a rerun that fixes the visited states.

**P2 (withdrawn).** "Entropy below a reference indicates value sharpening" is false: with exact
marginals and only factorisation error, output entropy can fall far below H(q) while KL stays below
ln 2 ([V] method/selection-term.md T4(b); red-team S4 confirms). Consequence for the review:
**no paper's reported entropy can attribute a gain to its value rule.** Attribution needs a
controlled arm on the same checkpoint (the sample-select-resample twin of 2605.12522, plus the
tilted twin of red-team block C), which almost no paper runs.

**P3 (revision, reworded).** When T >= L, so that further steps cannot lower E_fact, a revision
sampler's gain over its base at matched forward passes comes through E_learn on the visited states
or through its value rule (V). Which of the two can only be settled by rerunning with the value
rule matched (for ReMDM: top-p 0.9 on both arms and off on both arms). ReMDM Table 1 (MDLM flat at
0.042, 0.037, 0.035 MAUVE; ReMDM 0.403, 0.610, 0.656 at T = 1024, 2048, 4096) does not separate
them.

**Remark (was P4).** Exact caching leaves quality against forward passes unchanged; lossy caching
adds E_approx.

**P5 (cross-modal, restated in a named split).** For co-committed text set a and image set b, TC
splits as TC(a) + S_{T->I} + TC(b | a) with S_{T->I} = sum_j I(a; b_j | s), and symmetrically with
S_{I->T}; the symmetric cross term X = I(a; b | s) differs from both (either sign, red-team M10).
P5a: S_{T->I} and S_{I->T}, measured on the model (S_theta), are concentrated in early steps and on
layout and object tokens. P5b: at matched forward passes and tokens per pass, schedules that do not
co-commit high-S_theta pairs score better on text-image consistency than joint commitment, and
modality-sequential schedules need not beat alternating ones. Both are about the model's own
dependence, not about q.
Estimator (corrected): draw a from the model's joint over the text set (k_T sequential passes per
sample, R samples), re-query the image marginals, and estimate
I_theta(a; b_j | s) = E_a KL(p(b_j | s, a) || mbar_j), with mbar_j = mean over the R draws of
p(b_j | s, a). Using the mixture mbar_j rather than the one-pass marginal p(b_j | s) removes the
marginal-inconsistency term that red-team block J shows is 0.081 nats per token at zero dependence,
and which is largest exactly where P5a predicts front-loading [I; to be checked by enumeration].
Cost: R k_T + R passes per probed step. Evidence status unchanged from v1: no paper measures a
cross-modal quantity per step; the MMaDA-Parallel contrast is confounded and its released sampler
is not fully parallel (E3).

## D. What Paper 1 can claim (replaces v1 section 5)

Contribution of the review, in order of weight:
1. **The design space in one notation** (v1 section 1 with the Gaussian and multimodal
   extensions), tested against 47 models: 36 fit, 11 partly, 0 do not; the partial fits define the
   framework's stated limits (length-changing edit channels, stochastic memory, graded evidence at
   uncommitted positions, joint-over-set predictors, sequence-level selection)
   (`coverage/design-space-v1.md`).
2. **A critical finding about the evidence base (census).** 29 of 40 headline results use a value
   rule other than plain sampling at temperature 1 (truncation, temperature, argmax, guidance,
   sample-then-filter or sequence-level selection); 5 report entropy or diversity next to the
   headline; about 28 report a step sweep but only 10 state that the value rule was held fixed;
   1 of 14 guided models sweeps steps with guidance fixed. With P2 withdrawn, none of these papers'
   gains can be attributed to model, schedule or value rule from what is reported. To be extended
   from 47 models to all included records through the extraction form (protocol section 6) and
   double-checked by a second extractor before it is stated as a review result.
3. **The budget as a taxonomy**, with the identity credited to its sources, V as a single signed
   value slot, G and E_approx named, and the lever table (v1 section 3) with the value rows merged
   into one row keyed by mechanism.
4. **Stated open problems with the evidence each needs**: P1 (only the k = 1 point identifies),
   P3 (rerun with matched value rules), P5a and P5b (cross-modal dependence on a frozen unified
   model, with the corrected estimator), and the measurement the red-team names as missing from the
   literature: on one frozen checkpoint, sample-then-filter against its resampled twin, a
   confidence-ranked sampler and the tilted twin, at matched passes with an entropy-matched
   frontier. Whether 2605.12522's experiments already cover this is the first item to check
   (their resample fix restores entropy; matched passes and the tilted twin not confirmed).
5. Smaller technical items, credited as extensions: the k >= 2 sample-then-filter law (Prop. 4),
   the counterexample that withdraws P2 (T4(b)), the corrected memory statement (T7), and the
   cross-modal split with its corrected estimator.

Not claimed: E_sel or E_tilt as new error terms; any per-step impossibility; any size of V,
G or S_theta on a real model; the U-shape in steps (toy only, 20 of 32 variants, tie-sensitive).

## E. Open work

1. Check 2605.12522's experiments against the four-arm measurement in D4 (paper-reader, short).
2. Enumeration check of the corrected cross-modal estimator (mixture reference) and of the
   tie-handling correction to the k = 1 law.
3. Add the census fields (value rule, entropy reported, sweep with value rule fixed) to the
   extraction form in `protocol.md` section 6, then screen the 883 new arXiv records.
4. Codex round 3 on this file; human authors read it.
5. Paper 2 candidates, in order: the cross-modal measurement (P5a/P5b) on a frozen unified
   model (needs the user's yes for a download above 5 GB); the four-arm value-rule measurement on
   a text model if 2605.12522 has not done it.
