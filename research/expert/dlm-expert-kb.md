# dlm-expert knowledge base

Date: 2026-10-15. Version 0.9 (partial: see "Status of this file"). Built by a deep-research subagent
for the `dlm-expert` agent (`tools/build_agents.py` ROSTER). Read `research/CONTRACT.md` first; this
file does not replace the ledgers, the primers or framework-v2, it indexes and distils them.

**Status of this file.** Sections A, D, E, F and C.8 are complete from disk. Section B is complete at
the primer layer [P] (full-text readings of 2026-10-13/14); the web-currency layer [W] for work posted
after the primers (2026-07-17 to 2026-10-15) was commissioned from three research agents whose results
had not returned when this version was written, so **B carries no NEW-90D items beyond those already
on disk** (B.9 lists them). Section C.1-C.7 gives the external standards as pointers with identifiers
that must be confirmed (E0) before citation. The first run that has these results must fill B.9 and C
and append a changelog entry.

**Evidence key.** E0 model suggestion; E1 abstract, snippet, README, model card; E2 named sections of
the full text read; E3 code at a pinned SHA; E4 reproduced here; E5 preregistered and repeated with
intervals. [P] primer layer, [W] web layer, [S] source fact, [I] inference, [H] hypothesis, [V] exact
enumeration. NEW-90D = first posted 2026-07-17 to 2026-10-15; RECENT = 2026-04-01 to 2026-07-16.

## Contents

- [A. Project position](#sec-a): [A.1 goals](#a1), [A.2 framework-v2](#a2), [A.3 contributions](#a3),
  [A.4 census](#a4), [A.5 experiments](#a5), [A.6 decisions](#a6), [A.7 pipeline](#a7),
  [A.8 manuscript](#a8), [A.9 primers and dossiers](#a9), [A.10 user items](#a10)
- [B. Field map](#sec-b): [B.1 masked/discrete](#b1), [B.2 continuous](#b2), [B.3 samplers](#b3),
  [B.4 training and scaling](#b4), [B.5 reasoning and RL](#b5), [B.6 unified multimodal](#b6),
  [B.7 evaluation pitfalls](#b7), [B.8 closest surveys](#b8), [B.9 newer than the primers](#b9)
- [C. Method standards](#sec-c): [C.1-C.7 external standards](#c1), [C.8 the project's protocol and departures](#c8)
- [D. Venue](#sec-d): [D.1 CSUR rules](#d1), [D.2 exemplars](#d2), [D.3 ACM AI policy](#d3),
  [D.4 preprints](#d4), [D.5 fallbacks](#d5)
- [E. Experiments on a 12 GB GPU](#sec-e): [E.1 machine](#e1), [E.2 what fits](#e2), [E.3 guarded runs](#e3),
  [E.4 preregistration](#e4), [E.5 lessons](#e5), [E.6 Paper 2 options](#e6)
- [F. Glossary](#sec-f)
- [Changelog](#changelog)

<a id="sec-a"></a>
## A. Project position (from disk, 2026-10-15)

Every statement in this section is read from a file in the worktree; the file is named in brackets.
Numbers are the project's own (census, experiments) or paper-reported numbers recorded in the
dossiers, never memory. "Decision Dxxxx" means a row of `research/ledgers/decisions.jsonl`.

<a id="a1"></a>
### A.1 Goals and order of work

- **Mission.** Find, test and publish one new, verified result on diffusion language models (DLMs)
  or unified multimodal discrete-diffusion models, for an A* venue (`CLAUDE.md`; `research/FRAMEWORK.md` s1).
- **Two papers, review first** (D0005, confirmed by the user on 2026-10-15 in the RESUME block of
  `research/progress.md`). Paper 1 = critical PRISMA systematic review for ACM Computing Surveys
  (CSUR). Paper 2 = research article (originally Nature Machine Intelligence, D0004; venue to be
  fixed at gate G7 from the evidence). The integrating framework (D0011) is the spine of Paper 1.
- **Paper 1 working title** (D0007): *Diffusion Language Models and Unified Multimodal Generation:
  A Critical Systematic Review of Discrete and Continuous Approaches*. "and Meta-Analysis" was in
  the professor-approved D0006 title; it returns only if the pooling threshold of protocol s7 is met
  (at least 8 matched within-paper contrasts from at least 5 groups per question). It is not met on
  current evidence (`research/review/feasibility/stage2/summary-*.md`; `paper/review/OUTLINE.md`).
  The professor has not yet been told of the D0007 change in writing (D0007 owner field).
- **Professor's requirements** (2026-10-13; protocol header; memory `professor-review-requirements`):
  critical review; full PRISMA detail with exact dates and database-specific strings; exclusion
  reasons; reviewer agreement; a quality appraisal table; consistent table categories; RQ1-RQ6
  answered from evidence; "check Discrete Diffusion too".
- **Research questions** (protocol s1): RQ1 formulations and what separates them; RQ2 comparison
  with autoregressive (AR) models and under which protocols; RQ3 contribution of training strategies
  (pretraining, instruction/reasoning fine-tuning, RL, distillation); RQ4 quality-compute trade-off at
  inference (steps, order, remasking, caching, parallel decoding); RQ5 evidence for or against
  understanding-generation synergy in unified models; RQ6 rigour of the evidence base.
- **Excluded topics** (CLAUDE.md, user's global list): conformal water-quality retrieval (GLORIA);
  evaluation protocol and battery state of health. Paper 2 must not repeat EXP-003's question
  (dlm-expert ROSTER rule in `tools/build_agents.py`).
- **Hardware:** one RTX 5070 Ti Laptop GPU, 12 GB VRAM (12.82 GB reported), 31 GB RAM
  (`research/CONTRACT.md` rule 6; `runs/env-2026-10-14/setup.md` s1). Downloads: no size limit
  (D0012, user 2026-10-14; overrides the 5 GB line of CLAUDE.md for checkpoints and datasets); cloud
  spend still needs a yes. GPU jobs need telemetry and the guarded regime (section E.3).
- **Process rules in force:** proposer is never validator; gates pass only on a gate-auditor
  verdict; at most 3 agents at once; ledgers are append-only via `tools/ledger.py`
  (`research/FRAMEWORK.md` s5-6). Evidence levels E0-E5 (`research/CONTRACT.md`): E0 model
  suggestion, E1 snippet/README/abstract, E2 paper read in full (in practice: the named sections),
  E3 code inspected at a pinned SHA, E4 reproduced here, E5 preregistered and repeated with intervals.

<a id="a2"></a>
### A.2 The integrating framework (framework-v2, decision D0011)

Source: `research/review/framework-v2.md` (supersedes v1 sections 2.4, 3 value rows, 4, 5);
`research/review/framework-v1.md` s1 for the C1-C5 table; `research/review/method/selection-term.md`.

**One object.** Generation is a *commitment process*. A sampler runs on a state s_n = (z_n, m_n):
the partially revealed or noised sequence z_n plus optional memory m_n (self-conditioning input,
cached activations, planner state). Each step commits a set A_n of positions with values. Two cost
quantities: parallelism k_n = |A_n| (AR k = 1; a T-step sampler has mean k = L/T) and compute reuse.

**Design space, five choices** (framework-v1 s1, with primer corrections G1-G14 and M1-M11):

| Choice | What it fixes | Main instances |
|---|---|---|
| C1 channel | per-position state space and corruption, or a probability path (source, coupling, scheduler) | erasure/absorbing mask; symmetric/uniform (P(z = x) = alpha_t + (1 - alpha_t)/K); erasure-uniform mixtures (DFM Eq. 10); Gaussian z = a_t e(x) + s_t eps, VP or VE, embedding learned or fixed, input map g(z) possibly nonlinear; per modality in unified models (continuous image latents have no committed set) |
| C2 reveal law | which positions are clean together in training, and the objective weight | independent Bernoulli(alpha_t) (masked diffusion); prefixes (AR); random-permutation prefixes (any-order); block prefix (BD3-LM); Gaussian counterpart = conditioning law + shared noise level + embedding geometry; multimodal = a joint law over per-modality reveal sets (shared t, clean-input/noised-output, whole-modality dropout, independent per-image levels, capped noise) |
| C3 predictor | what the network outputs from s_n | clean-token marginals; concrete score/ratio (= marginal x alpha/(1 - alpha) on masked positions, erasure only); x0 regression; posterior-mean embedding; probability denoiser with velocity as an affine map (DFM); self-conditioning puts the previous prediction in m_n; head layouts in unified models |
| C4 commitment policy | position rule (which A_n), value rule (how values are chosen), joint vs independent draws within A_n | AR; random sets; confidence/entropy/margin ranking; learned planners; couplings inside A_n (AR head, copula, energy, verifier); for Gaussian/uniform channels two levels (update all positions, then a final rounding that commits all L at once); multimodal k_n^T and k_n^I, joint vs sequential vs alternating |
| C5 revision | whether a committed token can change | never (plain absorbing); explicit remasking/editing (ReMDM; DFM corrector); implicit but qualified for symmetric and Gaussian channels (pinned by conditioning, frozen below an identifiability noise level); output-level revision (planning, reflection) |

**Error budget (identity credited, not claimed).** For a deterministic state-only position policy,
KL(q || p) = E_fact + E_learn, where E_fact = sum_n E[TC(x^{A_n} | z_n)] (conditional total
correlation of co-committed tokens) and E_learn = model error on the states the policy visits.
Published: EB-sampler arXiv:2505.24857 Eq. 7 and App. A.1 (adaptive, state-dependent policies;
equality for deterministic ones); random or fixed partitions in ParallelBench 2510.04767 Thm 1,
Feng et al. 2502.09622 Lemma D.2-D.3, Li and Cai 2505.21400 Eq. 17/23, Zhang et al. 2602.00286
Eq. 16/18; ARDM 2110.02037 Eq. 3-4 already contain E_fact for random orders
(`dossier/primer-samplers.md` s4(a); `primer-foundations.md` s2c; E2). Randomised policies give an
upper bound by convexity.

**The value slot V** (framework-v2 s B). Every step is a commit kernel kappa(A, y | s) = rho(A | s)
kappa(y | A, s). Along a data path with the same position law,
KL(Q || P) = E_fact[rho] + E_learn[rho; p_theta] + V[kappa], with
V = sum_n E_Q[ KL(q_A || kappa(. | A, s_n)) - KL(q_A || prod_{i in A} p_theta^i) ]
(chain-rule corollary; `method/selection-term.md` Thm 1; published two-term identity = the case V = 0).
V is **one signed slot** for every departure of committed values from the product of predicted
marginals: temperature, truncation (top-p/top-k), argmax, guidance, sample-then-filter selection,
and joint draws (for which V is negative and can cancel E_fact). The output law differs from the
path law by a coupling term G >= 0 (zero for deterministic state-only policies). For truncation and
argmax the forward V is infinite whenever data mass falls outside the kept set. The decomposition
is not unique: it depends on the data-path coupling (red-team F2) and any "selection share" depends
on a reference policy (M1). The review presents V as bookkeeping that locates where a value rule
acts, not as a quantity with a canonical size.

Mechanisms placed by their law: state-only tilts (temperature, top-p/k, argmax, CFG, which also
changes the conditioning and costs an extra pass); sample-then-filter (MaskGIT; LLaDA at
temperature > 0) is at k = 1 a position-dependent tilt that sharpens by majorisation
(2605.12522 App. C.1; project Prop. 5 extends to arbitrary marginals at k = 1) and at k >= 2 a
non-product value law (project Prop. 4, closed form, exact to 3e-16; tie-handling correction
pending); joint draws; sequence-level selection (best-of-N, MBR) is outside the commit-kernel form
(post-hoc reweighting; Beirami et al. 2401.01879 for k = 1). Gumbel-noised confidence (MaskGIT's
released sampler, noise scale 4.5(1 - step/steps)) makes every pair reachable; Hayakawa et al.
2510.04525 show it approaches a tilted sampler when N >> k^2 |S|^(1/tau).

**Other named terms.** E_approx (lossy caching; exact caching leaves quality-vs-passes unchanged);
memory (self-conditioning breaks "policy depends on z_n only"); G (path-vs-output coupling);
the cross-modal split.

**Propositions and their status** (framework-v2 s C):
- **P1** (step sweeps): for a deterministic state-only position rule vs its base, the gain equals the
  E_learn difference exactly only at k = 1. At k > 1 the E_learn difference is not identified from a
  step sweep (visited states change; red-team M6: 11 of 12 toy cases differ by > 25% or in sign).
- **P2 withdrawn**: "entropy below a reference indicates value sharpening" is false (with exact
  marginals and only factorisation error, output entropy can fall far below H(q) while KL < ln 2;
  `method/selection-term.md` T4(b)). Consequence: **no paper's reported entropy can attribute a gain
  to its value rule**; attribution needs controlled arms on one checkpoint.
- **P3** (revision): when T >= L, a revision sampler's gain over its base at matched passes comes
  through E_learn or V; ReMDM 2503.00307 Table 1 (MDLM MAUVE 0.042/0.037/0.035 vs ReMDM
  0.403/0.610/0.656 at T = 1024/2048/4096, nucleus 0.9 on both) does not separate them. Test: rerun
  with the value rule matched (top-p 0.9 on both arms, and off on both).
- **Remark (was P4)**: exact caching leaves quality vs passes unchanged; lossy caching adds E_approx.
- **P5** (cross-modal; split into P5a/P5b, D0010): TC of co-committed text set a and image set b
  splits as TC(a) + S_{T->I} + TC(b | a) with S_{T->I} = sum_j I(a; b_j | s) (and symmetrically);
  the symmetric cross term X = I(a; b | s) differs from both. P5a: model-side S_theta is
  concentrated early and on layout/object tokens. P5b: at matched passes and tokens per pass,
  schedules that avoid co-committing high-S_theta pairs score better on text-image consistency;
  modality-sequential schedules need not beat alternating ones. Estimator: draw a from the model's
  joint over the text set (k_T sequential passes per sample, R samples), re-query image marginals,
  I_theta(a; b_j | s) = E_a KL(p(b_j | s, a) || mbar_j) with mbar_j the mean over the R draws (the
  naive one-pass reference adds a marginal-inconsistency term, 0.081 nats/token at zero dependence
  in red-team block J). Toy-checked only (`analysis/framework/check_crossmodal_mixture.py`).

**What Paper 1 claims (framework-v2 s D), in order of weight:**
1. The design space in one notation, tested on 47 models: 36 fit, 11 partly, 0 do not; the partial
   fits define the stated limits (length-changing edit channels, stochastic memory, graded evidence
   at uncommitted positions, joint-over-set predictors, sequence-level selection)
   (`coverage/design-space-v1.md`, `.csv`; rows M01-M29 copied from primers, not re-read, E2 conf 0.6).
2. A critical finding about the evidence base: the value-rule and reporting census (A.4).
3. The budget as a taxonomy, identity credited, V one signed slot, G and E_approx named, lever table
   with value rows merged into one row keyed by mechanism.
4. Stated open problems with the evidence each needs: P1, P3, P5a/P5b, and the four-arm value-rule
   measurement (OP1-OP4 in `paper/review/sections/08-open-problems.tex`).
5. Smaller technical items credited as extensions: Prop. 4 (k >= 2 sample-then-filter law), the
   T4(b) counterexample, the corrected memory statement T7, the cross-modal split with its estimator.

**Not claimed:** E_sel or E_tilt as new error terms; any per-step impossibility; any size of V, G or
S_theta on a real model; the U-shape in steps (toy only, 20 of 32 variants, tie-sensitive).
**Withdrawn (D0011):** E_sel, E_tilt, P2. Reasons: at k = 1 sample-then-filter equals a state-only
tilt in law (difference 5.6e-17); per-step accounting is possible under a data-scored coupling (32 of
32); E_sel changes sign with the reference (27 of 480); the k = 1 commit law, majorisation and the
sample-select-resample fix are published in 2605.12522 (App. C.1 Eq. 22-26; code 8bafc9e), the
sample-then-choose vs choose-then-sample distinction in Hayakawa et al. 2510.04525 (TMLR 2026 per
2609.34509's bibliography), the confidence-remasking vs top-probability split in 2609.34509, and the
k = 1 best-of-N law and log N - 1 + 1/N bound in Beirami et al. 2401.01879 (Lemma 2.3, Thm 3.1).

<a id="a3"></a>
### A.3 Contributions as currently ordered (D0011, D0021, OUTLINE)

C1 design space tested on 47 models; C2 value-rule census (random sample, v2); C3 error budget as
a taxonomy; C4 open problems with the evidence each needs. EXP-003 (A.5) supports the reading of C2
and is explicitly "not a contribution of the review" (`paper/review/sections/09-exp003.tex`).
Credit to state with C2 (D0019): reported quality depending on the sampling or evaluation setting has
been argued before for other metrics and model families: OpenReview Gq4yt8pxRo (sampling-dependent
fairness in DLMs; abstract only, E1; anonymous, kept once and flagged), arXiv 2606.29228 (Evaluation
Illusion), 2606.20536 (FID Lottery), 2607.24763 (CaRE). The census quantifies the reporting gap for DLMs.

<a id="a4"></a>
### A.4 Census of value rules and reporting (result v2, decisions D0015, D0019-D0021)

Source: `research/review/coverage/census-result-v2.md`; numbers from `analysis/census/*.log`
(scripts `agreement_random.py`, `summary_random.py`, `gap_rulings.py`); codebook
`review/coverage/census-codebook-v1.2.md` (rules B-1 to B-28); gate audit
`review/audits/2026-10-15-gate-census-v2.md` (PASS WITH CORRECTIONS, C1-C12 applied).

- **Sample.** Ranks 1-176 of a random order (seed 20261015) over the 1,106-record census pool
  (records both title/abstract screeners passed, with an arXiv ID; `tools/census_sample.py`). Stop
  rule: coder B's 150th eligible paper (reached at rank 176; 19 extra ranks because Codex read
  failures were counted as ineligible; no bias). Ranks 23, 33, 90, 144 have no full text.
- **Coders.** Coder B = Codex (ranks 1-91, 86 rows) then Claude Opus (92-176 plus 19, 79) after the
  Codex limit (D0015); coder A = Claude Sonnet, blind, all ranks. Agreement computed under codebook
  v1.1 before reconciliation; v1.2 written afterwards by a separate adjudicator who did not open row
  files or papers; two Opus adjudicators (ranks 1-88, 89-176) plus one harmoniser; adjudicators not blind.
- **Agreement before reconciliation (v1.1).** Eligibility raw 0.87, kappa 0.05 (n 172; prevalence
  effect, nearly all eligible; 15 of the 22 disagreements were Codex read failures); excluding read
  failures raw 0.96, kappa 0.20. Non-plain value rule (yes/no/unknown) raw 0.81, kappa 0.65 (149);
  both determinable raw 0.97, kappa 0.73 (62). Letters: A 0.97, T 0.87, P 0.93, S 0.40 (after a
  script-bug fix, D0020; was 0.31), G 0.96, M 0.82. F3 diversity paired 0.83; F4 step sweep 0.72; F5
  rule held fixed 0.70. Raw disagreements: `review/census/disagreements-random.csv` (158 field rows, 88 ranks).
- **Result (final rows, v1.2).** Eligible 167 of 172 with text. Value rule counted on 153 rows (B-28
  includes the one samples-only row); F3-F6 on the 152 with a generated-sample metric.

| Quantity | Final | Sensitivity (agreed cells restored) |
|---|---|---|
| headline uses a non-plain value rule or does not state it | 147/153 = 0.961 [0.917, 0.982] | 148/154 = 0.961 [0.918, 0.982] |
| headline uses a stated non-plain value rule | 97/153 = 0.634 [0.555, 0.706] | 86/154 = 0.558 [0.480, 0.634] |
| plain sampling stated (U) | 6/153 | 6/154 |
| value rule not stated (NS) | 50/153 | 62/154 |
| diversity or entropy paired with the headline (F3) | 28/152 = 0.184 [0.131, 0.253] | 28/153 |
| headline at two or more step settings (F4) | 55/152 = 0.362 [0.290, 0.441] | 61/153 |
| among those, value rule stated as held fixed (F5) | 20/55 = 0.364 [0.249, 0.496] | 21/61 |

  95% Wilson intervals, ranks treated as a simple random sample of the pool. Letter counts among the
  153: A (argmax) 33, C (confidence-ranked or threshold unmasking, token rule unstated; new in v1.2
  B-15) 20, G (guidance) 22, M (sequence-level selection) 12, P (top-p/k) 12, S (sample-then-filter) 12,
  T (low temperature) 14; 15 carry "+NS". Largest exposure: B-15 (if C were read as "not stated",
  "stated non-plain" falls by at most 39; "non-plain or not stated" unaffected).
- **Draft wording** (census-result-v2 "What can be said"): 147 of 153 (96%, 92-98) either decode
  the headline with a value rule other than plain T = 1 sampling or do not state the rule; 18% of
  the 152 with a metric report diversity/entropy for the headline setting; of the 55 with a
  multi-step-setting headline, 20 state the value rule was held fixed. The manuscript narrows "most"
  to "50 of 153 do not state it" (commit 0233c01).
- **Limits to state:** all coders after the Codex share, both adjudicators and the harmoniser are
  Claude models (agreement may overstate independent human agreement); no human coder yet; 15
  read-failure ranks are in effect single-coded; blindness incident (D0019: coder A's ranks 1-40
  batch ran coder B's append script once and may have seen B's rows for ranks 92-128, which it did not
  code); v1.2 written after agreement; 15 rows carry F1 as a relative gain; harmonisation reading 2
  (ranks 91, 114, 120, 141 kept G+NS); census numbers live in `analysis/census/*.log`, not `runs/` (D0021).
- **Earlier pilot (record only):** 47-model purposive census v1 (`coverage/census-result-v1.md`):
  37 of 45 headlines non-plain or unstated, 12 report entropy, 10 of 37 sweeps state the rule fixed;
  the framework-v2 text still quotes the older 29/40, 5, 1-of-14 counts from the design-space table.
  Mention once as a pilot, not as evidence (OUTLINE s2 "6 Census").

<a id="a5"></a>
### A.5 Experiments and hypotheses (H0001-H0009, X0001-X0003)

| ID | Question | Status | Key numbers / files |
|---|---|---|---|
| G4 (gate for EXP-002) | reproduce MDLM-OWT likelihood bound | REPRODUCED, E4 | PPL bound 22.935 (bootstrap 95% 22.861-23.007) vs paper 23.05 (time-free checkpoint), gap -0.50%; fp32, autocast off, TF32 off, eval mode recommended; bf16 gap was dropout in train mode (`runs/G4-mdlm-repro-2026-10-14/report.md`) |
| EXP-001 (H0001-H0003, X0001) | P5a/P5b on frozen UniDisc 1.4B: per-step S_theta front-loaded (H-A); dependence-aware schedule beats joint (H-B); S_theta predicts separation gain (H-C) | **STOPPED at construct gate PG-V** under preregistered rule 11.1 (D0016) | PG-V rung 1 m - s = -0.016; rung 2 m - s = 0.151 (required 0.25); m - s_sp about 0; PC-F passed (m_real 1.00, s_real 0.47). Under plain T = 1 sampling without guidance UniDisc at 512 px gives texture-like images and web-caption tails; no completion-specific link beyond the prefix (`runs/EXP-001/gates/verdict-*.json`). Layout bug found and fixed (lone space token) and recorded as a deviation |
| EXP-002 | four-arm value-rule decomposition at k >= 2 on MDLM-OWT | **demoted** (D0013) to an optional final-steps check | red-team X2: under Prop. 4 the co-committed coupling is about 1e-11 nats or less at N = 1024 for k = 2, 8, 16, non-negligible only in roughly the last 8 steps |
| EXP-003 (H0004-H0009, X0002-X0003) | does the value rule carry joint text-image consistency on UniDisc? Arms P64, P32 (plain T = 1, within-modality confidence ranking, 64/32 passes), O0 (official maskgit sampler, CFG 0, 32 steps), G (official, CFG 3.0, 32 steps, 64 calls) on 138 fresh COCO-prefix prompts x 2 seeds | **Done, gate PASS WITH CORRECTIONS** (`review/audits/2026-10-15-gate-EXP-003.md`; D0025); E4 (preregistered, intervals, single run) | Primary Delta1 = Lambda_b(G) - Lambda_b(P64) = 0.126 [0.076, 0.177] (BCa 0.075-0.176; p = 0.0002, bootstrap floor; 123 prefixes); W1 CLIP concordance failed, so worded "not confirmed by CLIP", may include quality-mediated coupling (quality-matched half 0.131 [0.071, 0.184]). Delta2a (guidance alone, G - O0) = 0.023 [-0.032, 0.078], Holm p 0.43: **not detected, not readable as a null** (PC-1 failed, W2). Delta2b (official bundle without guidance, O0 - P32) = 0.077 [0.024, 0.131], Holm p 0.012: positive, not a value-rule claim. Identity on 118 common prefixes 0.126 = 0.026 + 0.072 + 0.029. Per-arm Lambda_b: P64 0.051, P32 0.085, O0 0.159, G 0.180 (descriptive). Controls: NC-1 pass (-0.0003), NC-2 pass all arms, PC-2 pass (0.77 vs 0.17), **PC-1 fail** (TF - Ind = 0.031, p 0.40). Clock 8.02 GPU-h (cap raised to 8.5 h, D0022). Results live in the other worktree `.claude/worktrees/dlm-discovery-resume-ca3357` (commit 077fb1d; `runs/EXP-003/analysis/confirmatory.json`, `postfreeze.json`); not yet archived with a DOI |

**EXP-003 wording rules** (card s4.5, D0019, D0025; must be followed in any sentence): W0 positive
= "a seed-specific noun-level dependence ... which may include quality-mediated class-level
coupling"; never "completion-specific link". W1 not confirmed by CLIP. W2 no null or "no guidance
effect" wording. W4 no share-of-effect statement. Do not state the effect is at least 0.10; do not say
plain sampling shows no link (plain arms' intervals exclude 0) or that EXP-001's null replicates.
Novelty (D0019, `audits/2026-10-15-novelty-EXP-003.md`): incremental, 0.65. Sampler effects on
joint consistency are already reported (CO2Jump 2607.13188; MMaDA-Parallel 2511.09611 App. I;
UniDisc 2503.20853 for CFG in conditional generation); the same-condition independent-draw control is
practised (MUNITE 2610.09866, CoDi 2305.11846, MMVAE 1911.03393); the new parts are matched network
calls on frozen weights, guidance separated from ordering, the seed-balanced sibling baseline and the
discordant-noun restriction. Re-check NeurIPS 2026 / ICLR 2027 submissions before submission.

<a id="a6"></a>
### A.6 Decision digest (D0005-D0027)

| ID | Date | One line |
|---|---|---|
| D0005 | 10-13 | two papers, review first; CSUR target; no model training for Paper 1 |
| D0006 | 10-13 | title "... Systematic Review and Meta-Analysis" approved by the professor; meta-analysis unit = matched within-paper contrast |
| D0007 | 10-13 | working title changed to "... Critical Systematic Review of Discrete and Continuous Approaches"; meta-analysis only if the pooling threshold is met |
| D0008 | 10-14 | claim-evaluability hypotheses E1-E3 suspended after red-team (reject without review) and statistician audits |
| D0009 | 10-14 | stay with CSUR; rebuild on the integrating framework |
| D0010 | 10-14 | two-week horizon for Paper 1 (to about 2026-10-28), must carry a significant result; P5 split into P5a/P5b |
| D0011 | 10-14 | E_sel/E_tilt/P2 withdrawn; V as one signed slot; contributions reordered (design space, census, budget taxonomy, open problems) |
| D0012 | 10-14 | no download size limit; experiments EXP-001 then EXP-002, both preregistered |
| D0013 | 10-14 | EXP-002 demoted (coupling negligible at N = 1024) |
| D0014 | 10-14 | EXP-001 redesigned to prefix-conditioned joint completion with construct gate PG-V |
| D0015 | 10-14 | Codex exhausted until 2026-11-10; Claude coders replace it, disclosed |
| D0016 | 10-15 | EXP-001 ends at PG-V (feasibility result); EXP-003 proposed |
| D0017 | 10-15 | EXP-003 continues after controls; PC-1 failed, so every null becomes "not measurable" (W2) |
| D0018 | 10-15 | EXP-003 engineer's interpretation calls accepted; card erratum (UniDisc's unconditional branch masks every observed position, not only the prefix) |
| D0019 | 10-15 | EXP-003 novelty incremental 0.65 and wording limits; census blindness incident recorded |
| D0020 | 10-15 | census agreement under v1.1, adjudication under v1.2; protocol s10 amendment (B-4 "unified" = one model; B-6 X1 widened) |
| D0021 | 10-15 | census v2 corrected after gate audit (147/153; sensitivity; harmoniser standard adopted) |
| D0022 | 10-15 | EXP-003 hard stop raised 7.0 -> 8.5 GPU-h with the user's yes, before outcomes |
| D0023 | 10-15 | EXP-003 pilot freeze re-recorded after a UTF-8 fix (user's yes) |
| D0024 | 10-15 | EXP-003 false crash-loop stop (wrong log path) patched; infrastructure only |
| D0025 | 10-15 | EXP-003 post-audit decisions: post-freeze computations labelled; E3-H4 untested; W3 not estimable; E4 |
| D0026 | 10-15 | pilot recall not met (470/540); strings revised to S1'/S2' (525/540; MM28 28/28; R50 47/50); snowball records string-filtered; DBLP not searched; two Claude screeners |
| D0027 | 10-15 | precision round 4 (S1''/S2''), automation filter on the whole queue with a validation sample (V1 200, V2 100); reversal if > about 2% of in-scope records lost |

Before re-opening any of these, bring new evidence (dlm-expert rule).

<a id="a7"></a>
### A.7 Review pipeline state (searches, screening, PRISMA numbers)

- **Protocol** `research/review/protocol.md`: DRAFT v0.1, **not frozen**, not registered. Amendments in
  s10: D0020 eligibility (unified = one model; other modality = image, video, audio/speech, 3D; AR-text
  unified models with a diffusion/flow component eligible; X1 widened), D0026 strings S1'/S2', D0027
  strings S1''/S2'' and the automation filter with validation.
- **First round** (manuscript Fig. 1 source, OUTLINE s3): 1,903 records identified (572 Awesome-DLMs
  at commit 194aa6bd + 1,158 arXiv S1 + 173 arXiv S2), 450 duplicates, 1,453 screened by screener A
  (Claude) and B (Codex): pass/exclude kappa 0.728 (three-way 0.673), 1,123 pass both, 210 both
  exclude, 120 disagreements (for a human), 1,106 with an arXiv ID = census pool.
- **Second round** (`corpus/search-v2-report-2026-10-15.md`): arXiv, Semantic Scholar bulk,
  OpenReview (search-based; listing endpoints blocked), ACL Anthology, OpenAlex (partly; free quota
  exhausted: S1' A3/B/C and S2' not run), backward and forward snowballing one level from seeds;
  DBLP not searched (bot challenge); six subscription databases (Scopus, WoS, IEEE Xplore, ACM DL,
  SpringerLink, ScienceDirect) await the user's VIT e-gateway session (`corpus/subscription-search-sheet.md`).
  19,328 new records; automation (string filter) marked 12,952 snowball + 4,534 queue records
  ineligible (17,486); **final title/abstract queue 1,842** (1,721 database + 121 snowball; tiers T1 1,084,
  T2 120, T3 512, T4 126; 171 without abstract). Estimated in scope after round 4: 647 (35.1%,
  stratified 95% about 25-45%; titles only, labels by the proposing agent).
- **Not done yet** (blockers for submission; OUTLINE s5, progress RESUME): human validation sample
  (218 records) and 120 disagreements; validation screening of V1/V2; dual screening of the 1,842
  (T1, T2 first); full-text screening of the included set; extraction and quality appraisal for RQ1-RQ6
  (gate R2; manuscript section 05 depends on it); subscription searches; protocol freeze; professor's
  details (name, school, e-mail, ORCIDs) and exact model IDs of all LLM screeners/coders.

<a id="a8"></a>
### A.8 Manuscript state (paper/review/)

- `acmart` acmsmall, `\acmJournal{CSUR}`; main **35 pp** (CSUR limit incl. references) plus an 8-page
  electronic supplement after the clarity edit and cut (commit 0233c01); 96 validated references
  (`references.bib`; `review/audits/2026-10-15-citations-paper1.md`; R0091-R0096 added 55c55f8).
- Sections (word counts of the .tex sources): 01 Introduction 2,163; 02 Method 3,655; 03 Notation
  1,844; 04 Design space 2,084; **05 RQ evidence 288 (stub; needs full-text extraction)**; 06 Census
  2,239; 07 Error budget 2,576; 08 Open problems 1,548 (OP1 step sweeps, OP2 revision vs value rule,
  OP3 cross-modal dependence, OP4 four-arm measurement, Reporting); 09 EXP-003 2,084 (audited wording);
  10 Limitations 627; 11 Conclusion 356. Figures 1-4 built by scripts with asserted counts.
- Rules for the writer (OUTLINE s4): `% src: path` beside every number; key = arXiv ID with an
  `arXiv` prefix; only source facts and verified counts stated as fact; interval-bound claims only
  ("most" written as the count with its interval); negative results stay (eligibility kappa 0.05, PC-1
  failure, pending human validation); the ACM AI-use statement lives in Methods s2.9.
- OUTLINE.md is labelled draft v1 and its s6 still describes the 18-page first compile; PLAN.md
  sections 3-4 and D0011 still cite the older title and 47-model counts (stale; noted by the writer).

<a id="a9"></a>
### A.9 Primers and dossiers (research/review/dossier/), one paragraph each

- **`primer-foundations.md`** (paper-reader, 2026-10-14; E2 per record). Nine foundations read in
  named sections: D3PM 2107.03006, Campbell CTMC 2205.14987, SEDD 2310.16834, MDLM 2406.07524, MD4
  2406.04329, RADD 2406.03736, Zheng et al. 2409.02908, ARDM 2110.02037, LLaDA 2502.09992 (objective
  and sampler). Gives one notation (erasure and uniform channels, SUBS predictor, CTMC rates, concrete
  score), the continuous-time bound as a weighted masked cross-entropy with its conditions, four
  distinct "time removal" statements, what is and is not equivalent to any-order AR (objective yes;
  sampler only in the exact event-driven limit; model class no), the ratio-marginal map
  s = [alpha/(1 - alpha)] mu (erasure only), and how the uniform channel differs (revisable, no
  cross-entropy collapse, time cannot be dropped, no AO-AR reading). Verdicts on framework-v0
  claims 1-3: correct with stated restrictions. Toy checks in `primer-foundations-checks.py`.
- **`primer-samplers.md`** (paper-reader, 2026-10-14). Sampling theory from ParallelBench, Zhang et
  al. 2602.00286, Feng et al., Li-Cai, EB-sampler, Kim et al., ReMDM, MaskGIT, LLaDA, Zheng et al.,
  plus 2604.00375, 2606.12232, 2604.02718, 2605.10518, Di4C, ReDi. Bottom line: the factorisation
  identity is published (EB-sampler for adaptive policies); it fails for sample-dependent selection
  (toy: KL 1.29 nats, entropy 3.50 -> 2.16 at k = 1 with exact marginals); P2 and P3 of v0 were wrong
  or incomplete; ordering levers also move E_learn; six chapter statements (parallel price = TC; 1/T
  decay for random orders; learned error additive for random order; order is a lever on both terms;
  value rules matter separately; revision does not repair factorisation error in general).
- **`primer-gaussian.md`** (paper-reader, 2026-10-14). Diffusion-LM 2205.14217, CDCD 2211.15089,
  Plaid 2305.18619, DFM 2407.15595, Duo 2506.10892, BD3-LM 2503.09573, SSD-LM 2210.17432 (method).
  Findings: Gaussian channel needs VP/VE, learned embeddings and nonlinear input maps; no Gaussian
  "reveal law" (replaced by conditioning law, shared noise level, embedding geometry); "revise every
  step" true of the state space but positions effectively freeze below an identifiability noise
  level; Gaussian samplers carry a final-rounding factorisation term TC(x | z_0); Duo's duality is
  per-position per-time only (not trajectories); BD3-LM's KV cache is exact across blocks; two printed
  proof steps flagged (BD3-LM App. B.5; Duo Thm 3.2 setup). 14 edits applied in framework-v1.
- **`primer-multimodal.md`** (paper-reader, 2026-10-14; sections-read level E2-, one sampler E3).
  Show-o, UniDisc, MMaDA, MMaDA-Parallel, FUDOKI, Lumina-DiMOO, Transfusion, BAGEL, Show-o2,
  LaViDa-O. Bottom line: no paper measures a cross-modal quantity per step; the only joint-vs-
  sequential contrast (MMaDA-Parallel Tables 3, 10) is confounded; the released MMaDA-Parallel-A
  sampler commits no image tokens in the first quarter of passes (E3), unlike the paper; guidance needs
  its own lever row; "no new machinery" fails in four places (guidance, per-modality weights and
  schedules, continuous image channels, output-level revision); only Show-o2 sweeps steps at fixed
  guidance. Design-space table for the unified models; P5 evidence table.
- **`competitor-anatomy.md`** (paper-reader, 2026-10-14). Full read of the two closest surveys:
  2506.13759 v5 (Yu, Li, Wang; 175 refs, cutoff Aug 2025; most mathematics; no evaluation section; no
  comparison table) and 2508.10875 v3 (Li, Chen, Guo, Shen; 228 refs, cutoff mid-May 2026; one coarse
  axis continuous/discrete/hybrid; Table I of 36 models with metadata columns; Sec VI performance
  scatter from reported numbers, no budget matching). Neither has a commitment-process definition, a
  TC/model-error decomposition, a lever-by-error taxonomy, caching as cost-only, or cross-modal
  dependence; neither uses "total correlation".
- **`csur.md`** (venue-intel, 2026-10-13). CSUR rules, ACM AI policy, cost, preprint rules, fallback
  journals; digested in section D.
- **`exemplar-anatomy.md`** (venue-intel, 2026-10-13; structure only, E1). Five CSUR surveys 2024-26:
  video diffusion (doi:10.1145/3696415), diffusion alignment (10.1145/3796982), multimodal learning
  (10.1145/3713070), LLM capabilities (10.1145/3735632), LLMs for combinatorial optimisation, a PRISMA
  systematic review (10.1145/3801961). Twelve rules and a page budget; digested in D.2.
- **`prior-art-selection.md`** (paper-reader, 2026-10-14; E2 with code at E3). Full-text check of
  2605.12522, 2609.34509, 2503.17076, 2608.25505/2603.22248/EB, 2401.01879, and the extra 2510.04525
  against the selection-term novelty rows N1-N8; the basis of the D0011 withdrawals.
- **`prior-art-2605.12522-experiments.md`** (E2/E3 at 8bafc9e). 2605.12522 runs sample-then-filter
  ("lcr") and its resample twin at k = 1 only (block lengths 2, 8, 32; N = B), on a 120M model trained
  from scratch (FineWeb, vocabulary 5,000), T = 1 only, one seed in the main figure, no intervals, no
  confidence-by-max-probability rank-then-sample arm, no tilted twin, no temperature or entropy-matched
  frontier, no image/unified model. Basis of OP4.
- **`prior-art-exp001-step-profiles.md`** (E2). VRCD 2605.25820, VIG-Sampler 2608.26580, PUNT
  2510.21961 do not report model-side cross-modal dependence against step; nearest are attention-overlap
  proxies (text-output models) and a within-step KL test (text only). Unread neighbours: 2511.15098,
  2603.12996 (DAPD), 2604.02560, 2604.05497 (all E1).
- Check scripts beside the primers: `primer-foundations-checks.py`, `primer-samplers-check.py`,
  `primer-gaussian-check.py`, `primer-multimodal-check.py` (toy algebra only).
- Other review files worth knowing: `survey-landscape.md` (lit-scout, 2026-10-13; section B.8),
  `conjectures.md` (H1-H7, E0; H2 slack conjecture moved to Paper 2 and then superseded),
  `novelty-H2-H5.md`, `feasibility-inventory.md` and `feasibility/stage2/summary-*.md` (pooling not
  supported for remasking or synergy, borderline for steps; variance almost never reported),
  `pilot/h2-pilot-summary.md`, `reliability/RESULTS.md` (evaluability rubric failed: kappa 0.33),
  `audits/` (red-team, statistician, novelty, gate, citation and clarity audits).

<a id="a10"></a>
### A.10 Open items needing the user (not workable around)

Subscription database searches through the VIT e-gateway (user logs in; per-download consent); human
screening sample (218) and 120 disagreements; validation sets V1/V2; professor's details and approval
of the D0007 title; protocol freeze decision; downloads of large checkpoints for Paper 2 are allowed
(D0012) but GPU runs need go-ahead and telemetry; cloud spend needs a yes.

<a id="sec-b"></a>
## B. Field map

How to read this section. Each cluster has: key papers (ID, one line), consensus, disputes, open
questions. Two layers are kept apart. **[P]** = distilled from the project's primers and dossiers
(paper-reader full-text reading of named sections, E2, or code at a pinned SHA, E3; 2026-10-13/14).
**[W]** = web check on 2026-10-15 by lit-scout-style agents (arXiv abs pages opened; almost all E1 =
abstract level). Items first posted 2026-07-17 to 2026-10-15 are tagged **NEW-90D**; 2026-04-01 to
2026-07-16 **RECENT**. A NEW-90D or RECENT tag means "newer than the primers' reading", not
"important". Everything [W] is a lead to read before it is cited for more than its existence and
abstract claim. IDs are arXiv unless prefixed.

<a id="b1"></a>
### B.1 Discrete and masked diffusion language models: foundations [P unless marked]

Key papers.
- 2107.03006 D3PM (Austin et al.): discrete-state forward chains with transition matrices (uniform,
  absorbing, discretised Gaussian, embedding); absorbing D3PM is a reweighted MLM loss; BERT is a
  one-step D3PM; AR is a deterministic-masking diffusion on a product space. text8 1.61 (uniform) vs
  1.45 (absorbing) bits/char.
- 2205.14987 Campbell et al.: continuous-time (CTMC) discrete diffusion; ELBO (Prop. 2); tau-leaping
  and predictor-corrector; TV error bound (Thm 1) under assumptions that plausibly fail for absorbing
  noise (unbounded neighbour ratio; inference [I]); shows discrete-time multi-dimensional kernels
  implicitly assume independence (App. G).
- 2310.16834 SEDD (Lou et al.): concrete score and score-entropy loss; likelihood bound DWDSE;
  Tweedie tau-leaping; absorbing beats uniform in every zero-shot perplexity column.
- 2406.07524 MDLM (Sahoo et al.), 2406.04329 MD4 (Shi et al.), 2406.03736 RADD (Ou et al.): the
  simplified masked-diffusion objective = continuous-time ELBO = weighted average of masked-LM losses,
  weight -alpha'/(1 - alpha); schedule-invariant except at the endpoints; RADD proves the concrete score
  is the clean conditional times alpha/(1 - alpha) at sequence level and that time can be removed.
- 2409.02908 Zheng et al.: time-agnostic optimal predictor; ELBO as sum over the number of masked
  tokens with weight 1/n; first-hitting sampler (exact event-driven simulation); **fp32 Gumbel
  truncation acts like lowering temperature**, which had made MDMs look competitive on generative
  perplexity (after the fp64 fix MDM gen-PPL about 100 vs AR below 40, as reported).
- 2110.02037 ARDM (Hoogeboom et al.): order-agnostic AR diffusion; equivalence with absorbing
  diffusion; parallel-generation cost k L_t - sum L_{t+i}, which equals the conditional TC for random
  orders (project check).
- 2502.09992 LLaDA (Nie et al.): 8B masked DLM trained from scratch; objective with weight 1/t; default
  sampler argmax plus low-confidence remasking (Alg. 5); semi-AR block decoding; no KV cache.
- 2407.15595 DFM (Gat et al.): discrete flow matching with source, coupling, probability path and
  velocity; mask or uniform source; corrector sampling (Thm 2.4).
- 2506.10892 Duo: uniform-state diffusion as the argmax of a Gaussian diffusion on one-hot vectors
  (per-position marginal duality only); consistency distillation for few-step sampling.
- 2503.09573 BD3-LM (block diffusion): AR over blocks, masked diffusion within a block; exact KV
  cache across blocks; interpolates AR and diffusion in likelihood (LM1B: AR 22.83, BD3-LM L' = 4
  <= 28.23, MDLM <= 31.78).

Consensus [P]. For the absorbing (erasure) channel, the continuous-time ELBO is a weighted masked
cross-entropy; the optimal predictor is time-free; the objective equals the any-order AR objective;
ratio and marginal parameterisations carry the same information (true score or constrained network).
Absorbing beats uniform on likelihood for text at equal scale (D3PM, SEDD). Masked DLMs remain behind AR
on likelihood at equal compute in the papers read (UniDisc reports AR 13.2x more training-efficient in
its IsoFLOP fit; Plaid states a 64x compute gap for its Gaussian model; MD4 says masked diffusion is not
yet competitive with AR on text8; SEDD states a large gap to modern LLMs).

Disputes [P]. SEDD's claim that mean parameterisation "breaks down in continuous time" is contradicted
for the absorbing case by MD4 and MDLM. SEDD's learned score is unconstrained (MD4 H.3: may be
incompatible with the forward process; RADD supplies the constraint). MDLM drops time empirically while
RADD and Zheng prove it. MD4/MDLM claim the continuous ELBO is tighter than any finite-T bound without a
monotonicity proof. Uniform-state models (Duo) argue self-correction gives a few-step advantage; this
is confounded with distillation and entropy in the sections read.

Open questions [P]. Exact likelihood of the order mixture (neither objective gives it); bounds for
finite-step parallel samplers (the ELBO is for the infinite-step model); variable length (fixed-L in
all foundations); whether the uniform channel's revisability buys sample quality at matched entropy.

<a id="b2"></a>
### B.2 Continuous, embedding and latent diffusion language models [P]

Key papers. 2205.14217 Diffusion-LM (VP Gaussian on learned embeddings, clamping, classifier-guided
control); 2211.15089 CDCD (VE score interpolation, time warping, self-conditioning; clamping and
renormalisation cut entropy; a simplex CIR diffusion was abandoned); 2305.18619 Plaid (likelihood-trained
Gaussian DLM; categorical reparameterisation, learned schedule; 1B model matches GPT-2 124M zero-shot;
64x compute gap stated); 2210.17432 SSD-LM (simplex-like logits, semi-AR blocks); 2305.08379 TESS and
2502.13917 TESS 2 (simplex-logit diffusion; abstract level); 2210.08933 DiffuSeq (seq2seq embedding
diffusion; abstract level); 2510.22510 CANDI and 2608.10615 Simplex relaxation (hybrid/continuous
relaxations of discrete diffusion; abstract level, not read).
Consensus [P]. Gaussian samplers commit nothing until a final rounding, which is itself a parallel
commitment with factorisation error TC(x | z_0) (Plaid's bound contains it). Learned embeddings make
the channel move during training. Most continuous papers report generative perplexity with entropy,
only Plaid a likelihood bound, so cross-branch comparisons mix metric types.
Disputes [P]. Clamping helps (Diffusion-LM) vs hurts (CDCD). Plaid's reimplementation of CDCD (4.23 vs
3.89 NLL bound) is not a common benchmark.
Open [P]. Per-step revision rate of Gaussian samplers (falls to about zero before the last step?);
whether summed per-step TC for Gaussian/uniform steps can be stated (toy: per-step TC scales as step
size squared).

<a id="b3"></a>
### B.3 Samplers and decoding: theory and practice [P]

Key papers. 2505.24857 EB-sampler (entropy-bounded adaptive unmasking; the two-term identity for
adaptive policies; experiments at temperature 0; 2-3x speed-up claimed); 2510.04767 ParallelBench
(lower bound on achievable KL = summed conditional TC; benchmark of tasks hard for parallel decoding);
2602.00286 Zhang et al. (order sensitivity plus parallelisation bias in both KL directions; exact
verification costs exp(TC)); 2502.09622 Feng et al. (token error rate fine with steps independent of L
for n-grams, sequence error needs steps linear in L for a constructed HMM; extends to ReMDM);
2505.21400 Li and Cai (KL <= (s_max/L) sum_i I(X^i; X^-i) + eps_train for random orders; 1/T decay);
2502.06768 Kim et al. (adaptive ordering avoids hard subproblems: Sudoku 6.88% vanilla to 89.49% top
margin); 2503.00307 ReMDM (remasking as a corrector; NELBO looser than MDLM's; large MAUVE gains at
T >= L with nucleus 0.9); 2202.04200 MaskGIT (sample-then-filter confidence decoding; FID sweet spot at
8-12 iterations); LLaDA Table 9 (low-confidence remasking BBH 45.0 vs random 32.1, GSM8K 70.0 vs
21.3; both arms argmax); 2505.22618 Fast-dLLM (threshold-based parallel decoding plus approximate
block KV cache; abstract level); 2410.08709 Di4C (distilling inter-token correlations; TV O(1/N) bound);
2507.15897 ReDi and 2605.10518 IMDM (per-step TC as the factorisation error; IMDM lower bound);
2604.00375 (low-confidence remasking raises pass@1 and limits pass@k; entropy cap for hard gating);
2606.12232 (WINO remasking worsens diversity collapse at non-greedy decoding); 2604.02718 Generative
Frontiers (GenPPL = KL + entropy; report frontiers); 2605.12522 (SF lowers entropy; resample fix;
k = 1 only); 2609.34509 (confidence remasking vs top-probability split); 2510.04525 Hayakawa et al.
(sample-then-choose vs choose-then-sample; noised MaskGIT approaches a tilt); 2401.01879 Beirami et
al. (best-of-N KL bound log N - 1 + 1/N, k = 1 law); 2603.12996 DAPD and 2510.21961 PUNT
(dependence-aware parallel unmasking; abstract or partial reading).
Consensus [P]. Parallel commitment costs the conditional total correlation of the co-committed set;
one token per step costs zero; for random orders the cost decays like 1/T; ordering helps mainly by
avoiding hard subproblems (an E_learn effect at k = 1); value rules (argmax, low temperature,
sample-then-filter, nucleus) lower entropy and generative perplexity together and can reverse model
rankings; revision does not repair factorisation error in general (Zhang Prop. C.5 under an assumption;
Feng App. E.3).
Disputes [P]. Is the confidence-remasking gain from reduced diversity (LLaDA's hypothesis) or from
avoiding hard subproblems (Kim et al.)? Both LLaDA arms are argmax, so value sharpening is common to
both. Is ReMDM's MAUVE gain a better distribution or entropy loss under nucleus sampling (entropy falls
5.38 to 5.20 with T)? EB-sampler's theory assumes sampled values, its experiments use temperature 0.
Open [P]. Whether the additive E_learn structure survives adaptive policies; the size of V on a real
checkpoint; the four-arm value-rule measurement (OP4); cross-modal TC per step (OP3); E_approx of lossy
caches (only abstract-level evidence, e.g. 2607.29079 content drift in accelerated dMLLMs).

<a id="b4"></a>
### B.4 Training and scaling [P, thin]

On disk: LLaDA 2502.09992 (8B from scratch; AR comparison below 10^23 FLOPs; no KV cache; no RL in v1);
AR-to-diffusion adaptation DiffuLLaMA 2410.17891, Dream 7B 2508.15487, DiffuCoder 2506.20639, Seed
Diffusion 2508.02193 (design-space rows; abstract or partial reading); block/semi-AR hybrids
BD3-LM 2503.09573 and, by name only in 2508.10875's taxonomy, SDAR, TiDAR, Fast-dLLM v2, LLaDA2.0,
LLaDA-MoE; Nemotron-Labs-Diffusion 2607.05722 (tri-mode AR/diffusion LM; seed list, title only);
2605.12522 (training objective barely moves entropy at 120M). UniDisc reports AR 13.2x more
training-efficient (IsoFLOP fit). Consensus [P]: masked DLMs need more compute than AR for equal
likelihood; adaptation from AR checkpoints and block hybrids are the main scaling routes. Open: scaling
laws under matched evaluation budgets; data-constrained regimes. **[W] layer pending** (B.9).

<a id="b5"></a>
### B.5 Reasoning and RL for DLMs [P, thin]

On disk: 2508.10875 Table II lists 13 post-training methods (DoT, DCoLT, SEPO, diffu-GRPO, coupled-GRPO,
UniGRPO, VRPO, IGPO, wd1, SAPO, SPG, BGPO, JustGRPO) (competitor-anatomy s2b; names only);
2601.15165 (abstract: forgoing arbitrary order with GRPO works better on maths/code); MMaDA UniGRPO,
MMaDA-Parallel ParaRL (trajectory-level CLIP reward: output alignment 53.6 vs 59.8), Lumina-DiMOO
Self-GRPO (primer-multimodal). Known issue [I]: policy ratios need sequence likelihoods that masked DLMs
only bound (ELBO), so RL methods differ mainly in the likelihood estimator. Census note: RL-trained
headlines often use non-plain value rules; settings stated only for training rollouts are not the
evaluation rule (codebook B-16). **[W] layer pending** (B.9).

<a id="b6"></a>
### B.6 Unified multimodal discrete diffusion and hybrids [P]

Key papers (design-space rows M20-M29, M43-M47). 2408.12528 Show-o (AR text + MaskGIT image tokens,
omni-attention, one vocabulary); 2503.20853 UniDisc (one absorbing mask over text and image tokens,
shared t, modality-dropout CFG, joint pool confidence ranking; AR 13.2x more training-efficient;
guidance concentrated early: CFG on steps 1-3 of 24 gives CLIP 0.301 vs 0.312 all steps, 0.283 steps
22-24); 2505.15809 MMaDA (LLaDA-8B initialised; separate calls per modality; UniGRPO); 2511.09611
MMaDA-Parallel (joint text-image decoding; ParaRL trajectory-level alignment reward; parallel 59.8 vs
semi-parallel 57.5 vs sequential 54.1 output alignment, confounded; released -A sampler text-only for
the first quarter, E3); 2505.20147 FUDOKI (metric-induced discrete flow on Janus-1.5B; two heads; one
target modality per call; revisable tokens); 2510.06308 Lumina-DiMOO (LLaDA-Base, aMUSEd-VQ tokens, one
masked CE; lossy max-logit cache 2.05x; Self-GRPO); 2408.11039 Transfusion (AR text + Gaussian
diffusion on VAE patches; strictly sequential across modalities); 2505.14683 BAGEL (MoT, rectified flow
on FLUX-VAE latents; thinking-first helps WISE by 0.18); 2506.15564 Show-o2 (AR + flow head; only step
sweep at fixed guidance); 2509.19244 LaViDa-O (layout planning and reflection; GenEval 0.77 to 0.85,
reflection plateau about 0.89); 2505.16839 LaViDa, 2505.23606 Muddit, 2604.00007 Dynin-Omni, 2501.00289
D-DiT, 2505.16990 Dimple (design-space rows, partly read).
Consensus [P]. Unified discrete models fit C1-C5 but need four extras: guidance (sharpens marginals and
edits the cross-modal conditioning), per-modality weights and schedulers, continuous image channels in
hybrids (no committed set), output-level revision. Only UniDisc and MMaDA-Parallel commit text and image
in the same pass; most others are sequential or use separate calls. Initialisation from an LLM-scale
DLM (LLaDA) is needed for the larger models (Lumina-DiMOO: from scratch fails).
Disputes [P]. Joint vs sequential decoding (MMaDA-Parallel favours joint; BAGEL thinking-first helps on
knowledge tasks, yet MMaDA-Parallel's re-run of BAGEL shows thinking hurts in Causal and Spatial edits).
Synergy is conditional: 2609.01607 ("possible but highly conditional", architecture-dependent),
2607.04423 (shared encoders transfer, decoupled ones weakly; joint training oscillates), RealUnify
2509.24897 (far from genuine synergy), UniG2U-Bench 2603.03241 (unified models generally underperform
their base VLMs; E1).
Open [P]. Per-step cross-modal dependence (P5a/P5b; none measured as of the primer); joint consistency
as a function of the value rule (EXP-003 is one data point); per-modality k in step sweeps; guidance
schedules interacting with step counts; licences of unified checkpoints.

<a id="b7"></a>
### B.7 Evaluation practice and known pitfalls [P]

- **Value rules move headline metrics.** Generative perplexity can be lowered by lowering entropy
  (Zheng et al. fp32 Gumbel; ReMDM App. E.2.2: eta_cap 0.008/0.05/0.2 gives GenPPL 27.7/12.9/3.1 with
  entropy 5.32/4.93/2.43 and a degenerate 1.5-GenPPL sample; SEDD: GenPPL "can easily be hacked"; MD4
  similar). GenPPL = KL + entropy (Generative Frontiers 2604.02718). Report a quality-diversity frontier
  or entropy-matched comparisons (project census: only 18% pair diversity with the headline).
- **Step budgets.** Step sweeps confound E_fact with the value rule and guidance unless both are held
  fixed (census: 20 of 55 state the value rule fixed; in the 47-model pilot 1 of 14 guided models swept
  steps with guidance fixed). The k = 1 point is the only one a sweep identifies (P1).
- **Matched compute.** State network calls per sample (CFG doubles them), tokens per pass, caching
  (exact vs lossy), and wall-clock separately; KV-cached AR has higher throughput at large batch
  (UniDisc App. J; 2510.18480, E1). Sampler-level speed-ups depend on prompt template and protocol
  (2606.29228 Evaluation Illusion, E1).
- **Numerical precision.** fp32 Gumbel truncation is a temperature (Zheng et al.); bf16 autocast changes
  marginals (project G4 / MDLM setup); evaluate likelihoods in fp32.
- **Judges and checkers.** GPT-4.1 judges (MMaDA-Parallel), GenEval detectors and VLM presence checkers
  are unvalidated for these settings; EXP-003's PC-1 failure shows a VLM checker can miss within-prompt
  differences. Seeds and intervals are almost never reported (feasibility stage 2).
- **Released code vs paper** differences (MMaDA-Parallel-A; LLaDA "random remasking" baseline is argmax).
- Precedent studies of sampling-dependent evaluation in other families: 2606.20536 FID Lottery,
  2607.24763 CaRE, 2406.10229 (seed and sampling variance of benchmark scores), OpenReview Gq4yt8pxRo
  (sampling-dependent fairness in DLMs).

<a id="b8"></a>
### B.8 Closest surveys and how Paper 1 differs [P: `survey-landscape.md`, `competitor-anatomy.md`]

| Survey | What it is | Gap Paper 1 fills |
|---|---|---|
| 2506.13759 v5 Discrete Diffusion in Large Language and Multimodal Models (Yu, Li, Wang; 175 refs; cutoff Aug 2025) | maths-heavy catalogue by technique type; no evaluation section, no comparison table | no protocol, no design-space notation across families, no error decomposition, no reporting audit |
| 2508.10875 v3 A Survey on Diffusion Language Models (Li, Chen, Guo, Shen; 228 refs; cutoff mid-May 2026) | paradigm axis continuous/discrete/hybrid; training; inference by goal; multimodal; Sec VI performance scatter of reported numbers (no budget matching) | as above; its "Parallel Decoding Curse" is qualitative only |
| 2505.02567 v6 unified multimodal understanding and generation (403 refs) | architecture paradigms; benchmark counts | not about the decoding/value rule or discrete diffusion design space |
| 2508.08712 v4 parallel text generation (270 refs) | AR and non-AR parallel decoding; inclusion criteria for one subsection; qualitative quality-speed trade-off | no systematic protocol for DLMs, no census |
| 2607.12829 masked-DLM inference efficiency (IJCAI-ECAI 2026 survey track; 58 refs) | latency decomposition and decision matrix | efficiency only, no protocol |
| 2609.04778 DLMs for edge and agentic AI | deployment | no protocol |
| 2605.25343 native multimodal roadmap; 2509.24435 alternatives to next-token prediction ("systematic review" with inclusion criteria, no strings or counts); 2409.14993 (TCSVT 2025); 2303.06574 (IJCAI 2023); 2303.07576; 2305.14671; 2512.05092 tutorial | partial overlaps | none has a PRISMA protocol, a reporting audit or quantitative synthesis of reporting |
| Tier-2 (E1 only): ACL 2026 Findings unified-MLLM survey; TechRxiv/Authorea/SSRN DLM and decoding-scheduler surveys; Vicinagearth discrete-diffusion overview (doi:10.1007/s44336-026-00040-5, 2026-09-30); KDD 2026 dLLM tutorial (doi:10.1145/3770855.3816476) | protocol not determined | must be opened and checked before submission |

Differentiators Paper 1 can claim (D0011, survey-landscape s3): a PRISMA systematic protocol with
LLM-assisted screening described per ACM policy; a single notation (C1-C5) tested on 47 models; the
budget as taxonomy with credited identity; a coded, agreement-reported census of value rules and
reporting; open problems with the evidence each needs. Methodological precedents outside DLMs
(E1): PRISMA review of LLM evaluation (doi:10.1007/s44196-026-01490-x), construct-validity audit of 445
benchmark papers (2511.04703, NeurIPS 2025 D&B), text-to-image human-evaluation reporting audit
(2304.01816, CVPR 2023), randomness-control audit of LLM-pipeline papers (doi:10.18653/v1/2026.acl-short.22).
Survey-landscape's 14 tier-1 scans are keyword-plus-heading scans; a referee-grade "no protocol" claim
for any single survey needs a human read of its introduction and appendices.

<a id="b9"></a>
### B.9 Newer than the primers (on disk, already known to the project)

These were posted after or outside the primers' reading and are recorded in audits or the seed list
(E1 unless stated): CO2Jump 2607.13188 (sampler effects on joint text-image consistency in a unified
masked-diffusion model; E2 sections, novelty audit), MUNITE 2610.09866 (independent-draw control for
co-generated targets; E2 sections), CoBit 2610.14349 (E2 sections), VIG-Sampler 2608.26580 and VRCD
2605.25820 (attention-proxy dependence in dMLLMs; E2), Evaluation Illusion 2606.29228, FID Lottery
2606.20536, CaRE 2607.24763, 2609.34509 (confidence remasking vs top-probability), 2609.01607 (synergy
conditional; E2 sections), 2609.04778 (edge-DLM survey), 2607.12829 (IJCAI-ECAI 2026 efficiency
survey), 2608.20743 (multimodal speculative decoding with diffusion drafters), Simplex relaxation
2608.10615, Nemotron-Labs-Diffusion 2607.05722, 2607.29079 (cache drift in accelerated dMLLMs), and the
Vicinagearth overview doi:10.1007/s44336-026-00040-5 (2026-09-30). Closest surveys re-checked on
arXiv 2026-10-15: 2508.10875 still v3, 2506.13759 still v5, 2505.02567 still v6 (abs pages).
**To do:** fill B.1-B.7 [W] with confirmed NEW-90D/RECENT items (date-sorted arXiv queries per cluster;
NeurIPS 2026 and ICLR 2027 OpenReview where visible).

<a id="sec-c"></a>
## C. Method standards

<a id="c1"></a>
### C.1-C.7 External standards (pointers; identifiers E0 until confirmed on the publisher page)

The protocol (s0) names PRISMA 2020 and Kitchenham and Charters (2007). Identifiers below are from
memory and must be confirmed (Crossref or the official site) before they enter `references.bib`.

- **C.1 PRISMA 2020** (Page et al., BMJ 2021; E0 doi:10.1136/bmj.n71) and its explanation-and-elaboration
  paper. Items a computing review most often misses: full strings per source with dates (items 6-7),
  number of reviewers and use of automation tools in selection and data collection (8-9), study-quality
  / risk-of-bias method (11), certainty (15), flow diagram incl. "records marked as ineligible by
  automation tools" and full-text exclusions with reasons (16), registration and protocol (24),
  availability of data and code (27). Abstract checklist separate.
- **C.2 PRISMA-S** (Rethlefsen et al., Systematic Reviews 2021; E0 doi:10.1186/s13643-020-01542-z):
  per-database names and platforms, full strings, limits and filters, citation searching, other
  methods, dates, peer review of the strategy, total records and deduplication method.
- **C.3 AI-assisted screening and extraction.** To confirm: whether a PRISMA extension for AI use
  ("PRISMA-trAIce") exists and its items; the RAISE recommendations (responsible use of AI in evidence
  synthesis, Cochrane/Campbell/JBI/CEE); empirical LLM-screening validation studies. Working rule the
  project already follows: human oversight, validation on a human-screened random sample in this review,
  reporting of recall and an interval for missed records, model IDs and prompts.
- **C.4 Kitchenham and Charters 2007** (EBSE technical report, E0 EBSE-2007-01) and SEGRESS (Kitchenham,
  Madeyski, Budgen, IEEE TSE 2023; DOI to confirm): research questions first, protocol before search,
  quality assessment of primary studies, search validation by known-paper recall (quasi-gold standard,
  Zhang, Babar and Tell 2011; the gold set should not be the set used to tune the strings).
- **C.5 Quality appraisal for ML papers.** Candidates to adapt for QA1-QA9: REFORMS (Kapoor et al.,
  Science Advances 2024; DOI to confirm), the NeurIPS paper checklist, the ML Reproducibility Checklist
  (Pineau et al., JMLR 2021); PROBAST+AI and TRIPOD+AI are clinical-prediction tools, adjacent only.
- **C.6 Agreement.** Report raw agreement and Cohen's kappa with prevalence and bias indices; positive
  and negative agreement or PABAK (Byrt, Bishop, Carlin 1993) where prevalence is extreme (the census
  eligibility kappa 0.05 at 0.87 raw is the textbook prevalence paradox, Feinstein and Cicchetti 1990);
  Gwet's AC1 as an alternative; Krippendorff's alpha for more than two coders; avoid Landis-Koch labels
  as thresholds. DOIs to confirm.
- **C.7 Automation tools.** PRISMA 2020 counts records excluded by automation in the flow diagram and
  asks how the tool was used and validated; the project's string filter is deterministic and validated
  by samples V1/V2 (C.8).
- **C.9 Status re-check of D.3/D.4** (ACM policy date 2026-05-14 and the arXiv CS survey rule of
  2025-10-31): pending; re-read both pages before submission.

<a id="c8"></a>
### C.8 The project's protocol and where it departs from the standards

Source: `research/review/protocol.md` (DRAFT v0.1, 2026-10-13, s1-s10), decisions D0020, D0026, D0027,
`corpus/search-v2-report-2026-10-15.md`, OUTLINE s5. Each row: what the protocol says, the current
state, the standard it touches, what the manuscript must do.

| Area | Protocol / current state | Standard touched | Required handling |
|---|---|---|---|
| Registration and freeze | freeze rule (git tag `protocol-v1` after statistician and red-team sign, before any screening decision) **not applied**; not registered; screening of round 1 (1,453 records) and the census were done before any freeze | PRISMA 2020 item 24a-c (registration, protocol access, amendments); Kitchenham (protocol before search) | state "not registered; protocol drafted 2026-10-13, amended (s10 list), frozen on <date>"; publish the protocol with its git history and amendments on Zenodo; freeze before the dual screening of the 1,842-record queue |
| Searches | free sources run (arXiv, Semantic Scholar bulk, OpenReview by search, ACL Anthology, OpenAlex partly, one-level snowballing from seeds); DBLP not searched; six subscription databases pending; strings revised four times after a pilot (S1 -> S1' -> S1''), with recall measured on the same 540 seeds that supplied the vocabulary | PRISMA 2020 items 6-7 (all sources, full strings, dates); PRISMA-S (per-database strings, limits, platform, dates, deduplication, citation searching, peer review of strategy); quasi-gold-standard practice (recall should be measured on a set not used to build the strings) | report every string verbatim per source with dates and hits (`search-log.jsonl`); say recall 525/540 is in-sample (seeds shaped the strings) and, if possible, measure recall on an independent known-paper set (e.g. included records from the subscription databases or a hand-built list not used in revision); report DBLP and OpenAlex gaps as limitations |
| Automation tool exclusion | 17,486 records marked ineligible by a string filter (12,952 snowball + 4,534 queue); validation samples V1 (200) and V2 (100) drawn, not yet screened; reversal if > about 2% of in-scope records lost | PRISMA 2020 item 8 and flow diagram box "records marked as ineligible by automation tools"; AI/automation guidance (C.3): validate the tool in this review and report its performance | describe the filter exactly (it is a deterministic boolean string, not an ML classifier); report V1/V2 results with an interval for lost in-scope records |
| Screening | title/abstract by two machine screeners (A Claude, B Codex/GPT), kappa 0.728 pass/exclude on 1,453; round 2 by two Claude screeners of different models (Codex unavailable, D0026); human validation of a 15% sample (at least 100; 218 drawn) and human resolution of 120 disagreements **not done** | PRISMA item 8 (how many reviewers, independence, automation); RAISE-type guidance (human oversight, validated performance); Kitchenham (two reviewers) | complete the human sample; report kappa of each machine screener against the human with confusion tables; disclose that later screeners are same-family models; protocol s4 rule: a machine screener below kappa 0.70 vs the human triggers revision and rerun |
| Full-text screening and extraction | not started for the included set; census sample (176) read at full text by LLM coders; extraction form s5 (one agent plus a 10% second-reader check) not applied | PRISMA items 9-10 (data collection process, data items), 16b (excluded at full text with reasons) | run full text with X1-X8 codes; report the field-level error rate of extraction |
| Census coding | two LLM coders (Codex then Opus as B; Sonnet as A), agreement before reconciliation under v1.1, codebook v1.2 written after agreement, non-blind Opus adjudicators, blindness incident disclosed (D0019, D0020, D0021) | inter-rater reporting (C.6): raw agreement, kappa with prevalence and bias; independence of coders | report raw agreement plus kappa (and PABAK or positive/negative agreement where prevalence is extreme, e.g. eligibility kappa 0.05 at 0.87 raw); state the same-family limitation; a human-coded replicate is the open check |
| Quality appraisal | QA1-QA10 defined (code, weights/data, protocol specified, variation, uncertainty, matched compute, isolating ablation, claims agree with tables, limitations, peer-review status); claim-evaluability rubric suspended (D0008: kappa 0.33 fails); appraisal **not yet applied** | PRISMA item 11 (risk of bias / study quality), Kitchenham quality assessment; ML checklists (C.5) | apply QA1-QA9 by two raters with weighted kappa; use scores only for sensitivity analyses, never to exclude (protocol s6) |
| Synthesis | narrative by RQ with verdict vocabulary (well supported / mixed / weakly supported / untested); meta-analysis only if >= 8 matched contrasts from >= 5 groups per question (not met) | PRISMA items 12-15 (effect measures, synthesis methods, reporting bias, certainty) | state that no pooling was done and why; vote counts with their limits; no certainty grading tool exists for ML method claims, so describe the verdict rules explicitly |
| Eligibility | I1-I4 and X1-X8; amended after census coding (D0020: unified = one model; X1 widened) | PRISMA item 5; amendments must be dated and justified | keep the amendment in the supplement with the date and the reason |
| Versions | latest arXiv version rated; published version resolved separately | PRISMA item 7 (dates), reference integrity | report the retrieval date per record; cite published versions where they exist |
| AI use | LLM screeners, coders, adjudicators, extraction, citation validation and figure scripts | ACM policy (D.3): detailed Methods description | Methods s2.9 table: tool, model ID and version, task, prompt location, human checks, agreement |

<a id="sec-d"></a>
## D. Venue: ACM Computing Surveys

<a id="d1"></a>
### D.1 CSUR rules that bind this paper (`dossier/csur.md`, official pages read 2026-10-13, E2)

- **Scope.** The Editorial Charter says CSUR does not publish "new" research; surveys must develop a
  framework or overall view that integrates the literature. The referee page allows a survey that
  includes a new result "to organize and convey the material in a better way". Hence the census and
  EXP-003 must be framed as results that organise the review, not as its main finding. The Charter,
  author guidelines and referee page never mention systematic reviews, PRISMA or meta-analysis; a
  PRISMA review has been published (doi:10.1145/3801961, no meta-analysis).
- **Length.** Long survey: at most **35 pages including references** in the acmsmall Surveys style;
  extra material only in a marked electronic supplement (the manuscript must mark which pages form the
  35); "manuscripts of excessive length may be rejected without review". Published CSUR surveys are
  often longer (6 of 7 checked had 37-53 pages), but plan for 35. About 600 words per page of running
  text and about 30 references per page in acmsmall (measured, E1).
- **Abstract** at most 100 words; no first person, displayed maths or citation numbers; do not start with
  "This paper". CCS concepts (2012 ACM CCS, via the DL tool) and keywords (not synonyms of CCS terms,
  no acronyms or catch-all words) required.
- **Format.** LaTeX acmart; review submission `\documentclass[manuscript]{acmart}` (single column);
  production and page counting in `acmsmall` with `\acmJournal{CSUR}`; Libertine fonts; no margin or
  font changes; TAPS-approved packages; `\Description{}` for every figure; greyscale-readable colour;
  `ACM-Reference-Format` BibTeX style. Template pinned in `paper/style/acm/` (acmart v2.20, 2026/08/16
  from CTAN; ACM page listed 2.19 on 2026-10-13; re-check at submission).
- **Authors.** Named (no anonymisation); ORCID for the submitting author at submission and for every
  author before production; one corresponding author.
- **Process.** ScholarOne (mc.manuscriptcentral.com/csur); referees judge technical quality,
  relevance, general interest and presentation ("a substandard level in any is sufficient ground for
  rejection"); outcomes publish / revise / reject-encourage-resubmission / reject; a rejected paper
  cannot be resubmitted for **12 months**. No official decision time (ACM-wide target 90 days per
  cycle). EiCs listed on 2026-10-13: My T. Thai and Hanghang Tong.
- **Cost.** All ACM publications fully open access from 2026; APC 0 if the corresponding author is at an
  ACM Open institution (VIT University Vellore was on the participant list on 2026-10-13; confirm with
  the VIT library); otherwise list 1,800 USD, India 50% discount. Authors keep copyright (CC-BY or
  CC-BY-NC-ND) and must grant ACM the right to license the work to third parties, including for LLM training.
- **Questions to settle with csur.admin@acm.org before submitting** (csur.md s8): 12-month bar after
  "reject but encourage resubmission"; supplement with its own references outside the 35 pages; page
  exceptions; pre-submission inquiry; ACM Open coverage via the corresponding author's affiliation.

<a id="d2"></a>
### D.2 Structure of strong recent CSUR surveys (`dossier/exemplar-anatomy.md`, E1 structure only)

Five exemplars: video diffusion (V, 42 pp, 312 refs), diffusion alignment (A, 37 pp, 263 refs),
multimodal learning (M, 34 pp, 169 refs), LLM capabilities (F, 42 pp, 296 refs), LLMs for combinatorial
optimisation, PRISMA (C, 53 pp, 255 refs). 3-7 figures and 3-7 tables each, no algorithms; references
take 26-28% of pages at 250-310 references.
Twelve observed rules: (1) differentiate from named surveys on a stated axis (C: "none is
systematic"; we cannot claim "first" on topic, so claim method and organising framework); (2) a dated,
sourced growth figure early (our PRISMA counts and a year histogram); (3) one master taxonomy tree with
citations at the leaves, at the roadmap; (4) end the introduction with contributions, numbered research
questions and a section guide; (5) short background with one notation table (only A has one); (6) let the
taxonomy generate the sections, close each with a challenge note; (7) comparison tables with fixed
columns, "-" for unreported, provenance per number and a short reading (none of the five pools numbers
or audits reporting, so our census is new for the journal: keep it self-contained and worded
"consistent with"); (8) a method section of about 8% of pages if systematic (date-stamped searches,
tabulated queries, coded inclusion rules, who screened what, a reconciling flow diagram, checklist in an
appendix); (9) a limitations section when selection could bias evidence; (10) a short open-problems
section tied to evidence with a candidate route (A's single explicit testable hypothesis is the closest
to our OP1-OP4 format); (11) budget pages from the reference list (30 references = 1 page); (12) put
per-paper detail in the supplement (M: about 120 datasets; C: 17 appendix pages).
Our manuscript follows rules 1-12 with 6 figures, 6-8 tables and at most 2 algorithms in the main text
(OUTLINE s3), which is at the upper edge of the exemplar range.

<a id="d3"></a>
### D.3 ACM authorship and AI-use policy (policy updated 2026-05-14, read 2026-10-13; status re-checked in C.9)

- AI used **to conduct the research** (design, data source selection, data collection, coding,
  analysis, validation, figures, archiving) must be described in detail in the **Methods** section,
  including artefacts such as code, datasets and figures that rely on AI tools. AI used only to assist
  writing need not be disclosed under ACM. A generative AI tool cannot be an author. All named
  authors are accountable; fabricated or unverifiable citations are named as a ground for rejection or
  retraction.
- Consequence here: the search tooling, LLM screeners A and B (Claude; Codex/GPT), Claude census
  coders, adjudicators and harmoniser, the agent extraction pipeline, the citation validator and the
  agent-built figures and analysis scripts all go into Methods s2.9 with model IDs and versions, the
  task each did, what humans checked, agreement and error rates, and disagreement handling. The
  research-humanizer clarity pass is writing assistance (no ACM disclosure), but the project rule keeps
  the venue's LLM-use statement in (CLAUDE.md). Model IDs of screener A and the Claude coders are not
  yet recorded (A.7 blocker).

<a id="d4"></a>
### D.4 Preprints and priority

arXiv's CS category (blog post 2025-10-31) no longer accepts review/survey or position papers unless
already accepted after peer review at a journal or conference, with documentation; workshop review is
not enough (E1, quoted completely in a search extract; status re-checked in C.9). ACM allows posting
pre-submission and accepted versions to a homepage, institutional repository or a non-profit no-fee
repository (Zenodo fits; ResearchGate and Academia.edu are not allowed). So: no arXiv posting of Paper 1
before acceptance; establish priority with a dated, versioned protocol and search log on Zenodo or the
VIT repository; post to arXiv with the ACM DOI after acceptance. Do not route around the rule by
choosing a non-CS primary category.

<a id="d5"></a>
### D.5 Fallbacks (csur.md s7)

Artificial Intelligence Review (Springer; JIF 18.8 for 2025; surveys in scope; LLM use documented in
Methods; median 12 days to first decision on the journal page) is the safer scope fit; Information
Fusion (Elsevier; surveys up to 50 pages and at most 300 references; generative-AI declaration at
submission; weaker scope fit). CSUR JIF 30.4 (2025), rank 1/146 in CS Theory and Methods.

<a id="sec-e"></a>
## E. Experiment design know-how for Paper 2 (12 GB laptop GPU)

<a id="e1"></a>
### E.1 Machine facts that change how jobs are written (E4, `runs/env-2026-10-14/setup.md` s0)

- GPU RTX 5070 Ti Laptop, 12.82 GB reported, sm_120 (Blackwell), driver 595.71; torch 2.11.0+cu130
  in the project venv (`.venv`, CPython 3.12.14 via uv; lock `runs/env-2026-10-14/env-lock.txt`).
  System Python 3.14 runs neither UniDisc (needs < 3.13) nor MDLM (transformers 5.x breaks the
  remote code; pin 4.49). No triton, no flash-attn wheel on Windows: a pure-PyTorch flash_attn shim is
  used (`runs/env-2026-10-14/scripts/shims/flash_attn`; validated against float64 references to
  round-off in G4: rotary fp32 max abs 8.3e-7, attention 2.1e-5). A separate `.venv-eval` holds the
  scoring stack (CLIP, Qwen3-VL-2B).
- **Windows commit charge, not VRAM, is often the binding limit.** Each GB of cudaMalloc consumed
  about 1 GB of free system commit; with stale MCP/node processes holding about 60 GB, a process could
  allocate only about 5 GB of "VRAM" while nvidia-smi showed 12 GB free. A CUDA "OOM" with GBs free is
  a commit failure. Gate heavy stages on free commit (`scripts/common.py::wait_commit`; EXP-003 required
  at least 6 GB free commit before each chunk). CPU allocations above about 5 GB crashed Python once.
- Network about 1-2 MB/s; hf-xet crashed; use the resumable range downloader `scripts/pardl.py`
  (keep to about 4 connections during GPU work) and check LFS SHA-256. Disk free space swings with
  Docker's vhdx. Windows Update restarted the machine once during a run (pause updates during runs).
- **Two hard crashes** on 2026-10-14 (bugcheck 0x20001 HYPERVISOR_ERROR) under sustained full GPU load
  (memory `laptop-gpu-crashes`): GPU runs need the user's go-ahead and telemetry; never change system
  power settings.

<a id="e2"></a>
### E.2 What fits, measured here vs estimated

| Checkpoint | Size / precision | Measured here (E4) or estimate | Licence (as recorded) |
|---|---|---|---|
| UniDisc 1.4B interleaved (`aswerdlow/unidisc_interleaved` @2b344ca; code `alexanderswerdlow/unidisc` @3ee3e47) | 5.63 GB fp32 file; 1,406,870,785 params; loaded bf16 2.82 GB | joint 1024 px, 50 steps, CFG 3.0: 49.8 s, peak 6.75 GB; plain pass 512 px batch 1 0.129 s / 3.13 GB; CFG pass 0.301 s / 3.42 GB; 1024 px batch 8 CFG OOM (logits 7.9 GB); EXP-001 executed pass at 512 px median 0.10 s; official guided sampler 10.4 s/sample at 512 px, 51.4 s at 1024 px. bf16 vs fp32: top-1 agreement 0.962-0.972 | **none stated** (no LICENSE, no HF tag): generated images withheld from release |
| MDLM-OWT (`kuleshov-group/mdlm-owt` @d0958fa; code @c112c52) | 169.6M params, fp32 0.68 GB | forward L = 1024: 0.021 s batch 1 (1.08 GB), 0.408 s batch 32 (7.28 GB); 128-step sample 3.5-4.5 s; PPL bound reproduced (G4). Hard-coded bf16 autocast changes marginals materially (top-1 agreement 0.785 on a 50%-masked state): use fp32 for any marginal work | Apache-2.0 |
| GPT-2 large evaluator (gen-PPL, as in MDLM/ReMDM) | 3.25 GB | one sample 4.5-5.4 s incl. load, peak 4.65 GB | MIT |
| LLaDA-8B-Instruct (`GSAI-ML/LLaDA-8B-Instruct` @08b83a6) | 16.04 GB bf16 | **not run**; bf16 does not fit 12 GB; plan was 4-bit bitsandbytes (0.50.2 has a Windows wheel); no full-precision reference fits, so the quantisation gap must be measured another way. Download status not verified in this KB | MIT |
| MMaDA-Parallel-M (`tyfeld/MMaDA-Parallel-M`) | 8.08B params, about 16 GB | not run; needs 8/4-bit, untested (`primer-multimodal.md` s5 Q5) | MIT (HF tag) |
| Qwen3-VL-2B (presence checker), CLIP (EXP-003 scoring) | 4.26 GB, 1.71 GB | ran under gpu_guard in `.venv-eval` | as on their cards (not re-checked here) |

Compute ladder (`research/FRAMEWORK.md` s8): A toy/derivations (< 50M params); B frozen-checkpoint
measurement (MDLM, SEDD, Duo about 130-170M; LLaDA-8B, Dream-7B, MMaDA-8B at 4-bit, reporting the
quantisation gap); C fine-tuning 100-400M or LoRA on quantised 8B with short sequences; D+ full 8B
fine-tuning or multi-seed RL = cloud only, after G5 with a written cost estimate and user approval.
Section B.9 lists further open checkpoints (parameter counts and licences from the HF API, E1).

<a id="e3"></a>
### E.3 The guarded-run regime (tools/gpu_guard.py; EXP-001/EXP-003 IMPLEMENTATION.md)

- Every GPU job runs as `python tools/gpu_guard.py --log runs/<exp>/telemetry-<stage>-<chunk>.csv
  --max-temp 85 --max-minutes M -- <python> <script> --resume`. The guard logs nvidia-smi fields
  (temperature, power, SM and memory clocks, utilisation, memory, p-state, throttle reasons) to CSV
  flushed per row; kills the child after 3 consecutive readings at or above 85 C (exit 90) or after
  M minutes (exit 91); otherwise returns the child's code.
- EXP-003 as implemented: first chunk of a stage M = 5, then 15 (10 after an exit 90, with duty 1/3 and
  doubled pause); a chunk starts only with GPU below 65 C, no other compute process, free commit >= 6
  GB; 30 s pause between chunks (EXP-001 used 2 min); batch size 1; per-unit idle equal to its compute
  time (duty about 0.5); atomic per-unit done markers (`.json` written last); three exit-90 stops or
  three chunks without progress stop the stage. Generation in `.venv`, scoring in `.venv-eval`.
- Driver pattern: idempotent stages with done markers; `clock.json` holds cumulative GPU wall-clock
  (the stop-rule quantity); `STOPPED.txt` (exit 3) with an `ACK_STOP_*.txt` file to continue after an
  orchestrator decision; `DONE.txt` at the end; restart with `Start-Process` of the venv python
  (`run_all.bat` failed under a WMI-created process: the uv trampoline). Kill with
  `taskkill /F /T /PID <pid>`. Python children exited 0xC0000409 at teardown after finishing (results
  written; watch for it).
- Observed: no exit 90 in EXP-001 (max 83 C in the guided stage); mean power 116-130 W while busy,
  60-64 W averaged with duty idle; wall-to-compute about 2.0 by design, and about 1.4x the pilot cost
  model in EXP-003 M1 (D0022), so budget caps need that margin.

<a id="e4"></a>
### E.4 Preregistration practice used here (cards in research/preregistration/)

- Card sections (EXP-003 v0.3.2): 0 summary; 1 claim contract (one-sentence claim with a scope
  sentence, mechanism [H], closest work and the exact distinction, competing explanations); 2
  conditions and pass accounting (matched network calls; which matching is primary and why); 3 pools,
  pairing, seeds (fresh pools; seeds fixed in advance); 4 endpoints (one primary, Holm-family
  secondaries, descriptive items flagged, guardrails, **wording rules W0-W5 that spend no alpha**); 5
  hypotheses, effect sizes (minimum effect of interest as a point-estimate descriptor), outcome classes,
  falsifiers; 6 controls (negative controls where the effect must vanish, positive controls where it
  must be recoverable, instrument checks); 7 statistics (cluster = prompt/prefix; percentile and BCa
  bootstrap, 10,000 replicates, same resampled clusters in every arm; one primary test, Holm for
  secondaries; null class needs an equivalence-type rule); 8 runs ordered by information per GPU-hour
  and budget; 9 stop rules (cost, failed units, controls, guidance assertions, budget caps); 10 what the
  paper states under each outcome (sentence templates per outcome); 11 deliverables, freeze, sign-off;
  12 change log with dated errata.
- Process: experiment-designer drafts; statistician and red-team review (several rounds; required
  changes applied as versions); both sign; ledger rows (hypotheses, experiments) added at signature;
  a pilot on a **separate pool** fixes only costs and variances (firewalled pilot report; sizing rule
  n_conf); analysis scripts hashed into `freeze-pilot.json` before the pilot and `freeze-analysis.json`
  before main scoring; a label-scrambled end-to-end analysis run before real outcomes; any change after
  a freeze needs a dated decision and, where it touches money or outcomes, the user's yes (D0022,
  D0023); post-freeze computations are labelled exploratory (D0025); gate-auditor reconciles every
  number against `runs/`; novelty-auditor sets wording limits before any claim (D0019).
- Agreement on the reading of "matched compute": EXP-003 matched network calls (guided steps count
  two calls) and reported steps-matched contrasts as secondaries; state both.

<a id="e5"></a>
### E.5 Lessons from G4, EXP-001 and EXP-003 (what to do differently in Paper 2)

1. **Run a construct gate before the expensive stage** (EXP-001 PG-V). It stopped a 27-GPU-hour plan
   after about 0.8 GPU-hours by showing that plain T = 1 sampling on UniDisc gives no measurable
   completion-image link at 512 px. Choose a regime in which the effect to be timed or decomposed is
   clearly present first (OP3: P5a needs a regime with a strong joint link before its timing can be
   measured).
2. **Positive controls decide what a null means.** EXP-003's PC-1 failed (an image generated after the
   whole completion showed no detectable noun-level dependence under plain sampling), so every null
   became "not measurable with this instrument" (W2) while the positive primary stayed readable. Size
   and pilot the positive control on the instrument before the main stage; a VLM presence checker may
   be insensitive to within-prompt differences.
3. **Tokenisation and layout bugs are construct bugs.** The demo layout `PROMPT + " " + <m>*32`
   produced a lone SentencePiece space token before the tail, after which the model continued with
   digits; found only through a failing gate (EXP-001 incident 2). Inspect token ids of every template.
4. **Eval mode and precision.** UniDisc's backbone has dropout 0.1: a train-mode forward changes text
   top-1 by 22% (assert eval before every forward). MDLM's hard-coded bf16 autocast changes marginals
   materially; the G4 "bf16 gap" was dropout. Use fp32 for marginal or likelihood work; fp64 Gumbel
   noise for sampling (Zheng et al. 2409.02908 showed fp32 Gumbel truncation acts as a temperature).
5. **Encoding on Windows.** Reading UTF-8 score files with the default code page mis-keyed non-ASCII
   nouns and crashed the controls stage (D0017); set `encoding="utf-8"` everywhere; line-ending changes
   alter file hashes used in freezes (D0025 correction).
6. **Infrastructure checks are part of the design.** A progress check read the wrong log path and
   triggered a false crash-loop stop (D0024); budget caps fired on a 1.4x wall-to-compute overrun
   (D0022). Test stop rules on a dry run.
7. **Bundled samplers confound.** The official UniDisc sampler bundles guidance, pooled cross-modal
   confidence ordering with Gumbel noise, arccos schedule, sample-then-filter selection and a final
   argmax pass; Delta2b showed the bundle without guidance moves the link, so a value-rule claim needs
   arms that change one element at a time (the four-arm design of OP4).
8. **Released code can differ from the paper** (MMaDA-Parallel-A sampler's text-only first quarter, E3;
   UniDisc's unconditional branch masks every observed position, D0018). Read the sampler code at a
   pinned SHA before designing arms.
9. **Licences.** UniDisc states none: outputs can be measured and reported, images withheld. Prefer
   MIT/Apache checkpoints for anything to be released.
10. **Agents and blindness.** Shared scratchpads broke coder blindness once (D0019); run independent
    coders or arms in private folders.

<a id="e6"></a>
### E.6 Paper 2: what is open and what is ruled out (from disk)

- Ruled out as Paper 2's question: EXP-003's (guided vs plain joint consistency on UniDisc).
  Excluded topics in A.1. E_sel/E_tilt as new terms are withdrawn (D0011).
- Candidates named on disk (framework-v2 s E5; OP1-OP4): (a) the **four-arm value-rule measurement**
  (sample-then-filter, its resampled twin, a max-probability rank-then-sample sampler, the tilted twin;
  matched passes; entropy-matched frontier via a temperature sweep; k > 1; a text model and preferably
  a unified one) - 2605.12522 covers only two arms at k = 1 on a 120M model; (b) **P5a/P5b** on a frozen
  unified model in a regime where the joint link is present (guided or a stronger model), with the
  mixture-reference S_theta estimator; (c) **OP2** revision vs value rule (ReMDM with top-p matched
  on both arms) on MDLM-OWT, which already runs here; (d) **OP1** cross-evaluation of position rules on
  the states each visits. Any of these needs a novelty check against the B-section NEW-90D items first.
- Feasibility notes: MDLM-OWT experiments are cheap here (0.02 s per pass); LLaDA/Dream/MMaDA need
  4-bit loading and a quantisation-gap measurement; UniDisc costs about 0.1 s per 512-px pass.

<a id="sec-f"></a>
## F. Glossary of the project's notation and terms

**Sequences and states.** x = (x^1..x^L) clean sequence over vocabulary V, |V| = K (a union of
per-modality vocabularies in unified models); q the data law; m the mask symbol; z_t the corrupted
state at time t in [0, 1] (t = 0 clean, t = 1 fully corrupted); s_n = (z_n, m_n) sampler state at step n
with optional memory m_n; U(z) unmasked set, M(z) masked set, n(z) = |M(z)|.

**Channel quantities.** alpha_t signal level (erasure: probability a position is still clean;
lambda_t = 1 - alpha_t, which is LLaDA's "t"); w(t) = -alpha'_t/(1 - alpha_t) the masked-diffusion
weight (1/t for the linear schedule; 1/n in the count form); alpha_t/(1 - alpha_t) the odds of being
unmasked (MD4's SNR); a_t, s_t Gaussian scale and noise (VP a^2 + s^2 = 1; VE a = 1); SNR(t) = a^2/s^2;
e(x) embedding; g(z) network input map; Duo's T(alpha~) Gaussian-to-uniform signal-level map.

**Predictor objects.** mu_theta^i(z_t, t) / p_theta(x^i | s) clean-token marginal at a masked
position; SUBS = zero mass on the mask, copy unmasked tokens (MDLM); concrete score s_t(z)_(i,v) =
p_t(z^{i<-v})/p_t(z) = [alpha_t/(1 - alpha_t)] p_0(v | z^U) on masked positions (erasure only);
probability denoiser and velocity u_t (DFM).

**Design choices.** C1 channel; C2 reveal law (with its objective weight); C3 predictor; C4
commitment policy = position rule rho(A | s) + value rule kappa(y | A, s) + joint or independent draws;
C5 revision. A_n committed set at step n; k_n = |A_n| tokens per step (k = 1 is one token per pass);
T number of steps; N network calls (NFE). "Matched passes" = equal network calls per sample (a CFG
step costs two calls).

**Budget terms.** TC(Y | Z) conditional total correlation = sum_j H(y_j | Z) - H(Y | Z) =
KL(joint || product of marginals). E_fact = sum_n E[TC(x^{A_n} | z_n)] factorisation term; E_learn
model error on the states the policy visits; V the signed value slot (departure of committed values
from the product of predicted marginals); G >= 0 coupling between path law and output law; E_approx
stale-computation (lossy cache) term; E_fact^X / S_{T->I}, S_{I->T}, X = I(a; b | s) cross-modal terms;
S_theta the model-side (re-query) version; mbar_j the mixture reference over R text draws.
**Withdrawn:** E_sel (selection bias) and E_tilt (tilt cost) as new terms; P2.

**Value-rule classes (census codebook v1.2).** U plain sampling at temperature 1 stated; A argmax /
greedy; T temperature below 1; P top-p or top-k truncation; S sample-then-filter (sample all masked
positions, keep the most confident sampled values; with a confidence-ranked sampler whose token rule is
stated as sampling); C confidence-, margin-, entropy-ranked or threshold unmasking with the token rule
unstated (B-15; non-plain); G any sampling-time change of the per-step distribution by an external score:
classifier-free or classifier guidance, reward/value/constraint gradients, hard per-step grammar or
validity masks (B-20); M selection among complete candidates by an inference-time score: best-of-N,
validity filtering, MBR, reranking, beam/best-first/tree search, particle/SMC resampling (B-17 to B-19;
oracle pass@k is not M); NS not stated; "+NS" a stated G or M with the base token rule unstated (B-21);
U requires the value distribution, the position rule and the absence of truncation, guidance and
selection all to be stated (B-14; "temperature 1.0" alone is NS); QL samples only. Census fields: F1 headline metric (NA none; QL samples),
F2 value rule, F3 diversity/entropy paired with the headline, F4 step sweep (steps, NFE or tokens per
step), F5 value rule stated as held fixed in the sweep, F6 guidance held fixed.

**Sampler vocabulary.** Rank-then-sample (RS; choose positions from the state, then sample values) vs
sample-then-filter (SF; sample values first, choose positions by the sampled values' confidence); the
**resampled twin** (sample-select-resample: SF positions, values redrawn fresh; 2605.12522's "bias
elimination"); the **tilted twin** (the state-only tilt whose law equals SF at k = 1); low-confidence
remasking (LLaDA default); first-hitting sampler (Zheng et al.); tau-leaping; predictor-corrector;
semi-autoregressive / block decoding; threshold (dynamic) unmasking; Greedy-Tail (argmax last step, Duo).

**EXP-003 terms.** Arms P64, P32 (plain, 64/32 passes), O0 (official sampler, CFG 0, 32 steps, 33
calls), G (official, CFG 3.0, 32 steps, 64 calls); Ind (image independent of the completion given the
prefix; NC-1) and TF (image generated after the whole completion; PC-1); D_pe discordant nouns of prefix
p, seed e; L_p seed-balanced link of a prefix; Lambda_b(a) mean link of arm a; Delta1 = G - P64,
Delta2a = G - O0, Delta2b = O0 - P32; MEI minimum effect of interest (0.10); W0-W5 wording rules; NC/PC
negative/positive controls; guardrails (i)-(iv). **EXP-001 terms.** Arms J (joint), T/I (modality first),
Alt (alternate), DA (dependence-aware), TFJ (text-front joint); gates PG-1, PG-V (construct), PC-F
(checker validity); m - s (matched minus shuffled presence), s_sp (same-prefix baseline).

**Review pipeline.** S1/S2 original strings; S1'/S2' (D0026) and S1''/S2'' (D0027) revisions; MM28 the
28 Awesome-DLMs multimodal seeds; R50 a random 50 other seeds; tiers T1-T5 of the screening queue; V1/V2
validation samples of automation exclusions; X1-X8 exclusion codes; I1-I4 inclusion criteria; QA1-QA10
quality items; RQ1-RQ6; gates R0-R6 (review) and G0-G9 (Paper 2).

**Evidence and process.** E0-E5 (A.1); [S] source fact, [I] inference, [H] hypothesis, [V] verified by
exact enumeration; NEW-90D first posted 2026-07-17 to 2026-10-15; RECENT 2026-04-01 to 2026-07-16;
"proposer is never validator"; gate-auditor, red-team, statistician, citation-validator, novelty-auditor
are the validators.

<a id="changelog"></a>
## Changelog

- 2026-10-15 v0.9 (deep-research subagent). Created from disk: CONTRACT, ROSTER entry, progress
  RESUME, framework-v1/v2, decisions D0005-D0027, hypotheses H0001-H0009, experiments X0001-X0003,
  census-result-v2 and codebook v1.2, protocol incl. s10, OUTLINE and section sources, all dossier
  files, search-v2 report, env setup, G4 report, EXP-001/EXP-003 IMPLEMENTATION and card. Web: arXiv abs
  pages of 2508.10875 (v3), 2506.13759 (v5), 2505.02567 (v6) confirmed unchanged. Not yet done: the
  [W] layer of B (NEW-90D items) and confirmation of C.1-C.7 identifiers; three research agents were
  dispatched for these and had not returned. Next run: fill B.1-B.7 [W], B.9, C.1-C.7, C.9 and append here.
