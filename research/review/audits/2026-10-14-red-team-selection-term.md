```yaml
agent: red-team
date: 2026-10-14
brief: Hostile CSUR-referee and mathematical attack on the E_sel / E_tilt / E_fact^X derivations of research/review/method/selection-term.md that Paper 1 would present as its own contribution
sources_examined:
  - research/CONTRACT.md
  - research/review/method/selection-term.md (full, T1-T10 and the 15 edits)
  - analysis/framework/check_selection.py (full) and check_selection.log (rerun here, byte-identical)
  - research/review/framework-v1.md sections 1-4
  - research/debates/2026-10-14-framework-v1/round-02-codex.md
  - research/review/coverage/design-space-v1.md sections 4 (b) and 5 (c), plus table rows M09, M20, M21 for the value-rule cells
  - analysis/framework/redteam_selection.py, redteam_selection.log (written here)
  - analysis/framework/redteam_selection2.py, redteam_selection2.log (written here)
coverage: >
  Every proposition, lemma and edit of selection-term.md was checked against its proof and against
  the check script. Reproduced the 61-check log exactly (python analysis/framework/check_selection.py,
  13 s, diff empty). Wrote two red-team scripts (about 75 s in total) that import the report's own
  kernels unchanged. NOT covered: 2604.00375 (the report's reading of its Prop. 2 and App. H was not
  re-checked); the primers and the EB-sampler, Zheng et al. and MaskGIT sources (taken as cited);
  framework-v1 sections 5 to 7; the design-space table rows other than M09, M20 and M21; no real model.
claims:
  - statement: "SF is outside the identity, state-only tilts are inside it (T1.5, edits 3, 12, 13) is a property of the sampler's law"
    status: contradicted
    evidence: redteam_selection.log block C (SF k=1 and its V1 twin have identical output laws, max diff 5.6e-17; the twin's forward E_tilt is inf)
    level: E4
    confidence: 0.95
  - statement: "Per-step forward accounting of E_sel is impossible for SF (Prop. 2 conclusion, edits 4 and 14)"
    status: contradicted
    evidence: redteam_selection.log block A (data-scored path law gives a finite forward path KL in 32 of 32 SF configs; framework toy 2.2358 against output 1.2881)
    level: E4
    confidence: 0.9
  - statement: "Matched RS is the canonical reference; E_sel is reference-free in substance"
    status: contradicted
    evidence: redteam_selection2.log S1 (sign of E_sel differs across four RS references in 27 of 480 configs); redteam_selection.log block D (spread up to 0.472 nats, a factor 3.3)
    level: E4
    confidence: 0.85
  - statement: "E_sel charges only value selection (no double counting)"
    status: contradicted
    evidence: redteam_selection2.log S2, S6 (exact model, k=3, E_sel = -0.0866 against mRS and -0.1511 against RS-conf, unchanged under random ties and 1e-4 jitter)
    level: E4
    confidence: 0.9
  - statement: "E_fact falls and E_sel rises with T, so SF has an interior optimum in T"
    status: mixed
    evidence: redteam_selection.log block E (interior minimum in 20 of 32 variants; argmin at T=1 in 10 and T=L in 2; the tie rule alone moves SF KL at T=2,3 from 1.025/0.836 to 0.543/0.204)
    level: E4
    confidence: 0.85
  - statement: "T4(a): SF output entropy can exceed matched-RS output entropy"
    status: mixed
    evidence: true on the tie set only; redteam_selection.log block E (1e-4 jitter reverses it) and redteam_selection2.log S3 (0 of 200 perturbed and 0 of 600 random gated q)
    level: E4
    confidence: 0.8
  - statement: "T4(b) kills P2's diagnostic, not only its premise"
    status: supported
    evidence: redteam_selection2.log S4 (at fixed T=2 a better partition lowers KL 0.617 to 0.368 through E_fact alone while H(p) falls from 4.131 to 2.773, below H(q)=3.514)
    level: E4
    confidence: 0.95
  - statement: "D <= KL_cont(N,k) for any marginal under random ties (T2 limit (b))"
    status: contradicted
    evidence: redteam_selection2.log S5 (k=1, non-identical marginals: 255 of 3000 violate; D=0.367 against 0.193); redteam_selection.log block H (k<=2: 489 of 3000)
    level: E4
    confidence: 0.95
  - statement: "P1 with edit 11: the k=1 gain estimates the E_learn part of a position lever's gain"
    status: contradicted
    evidence: redteam_selection.log block I (dE_learn at k=2 differs from the k=1 gain by more than 25 % or in sign in 11 of 12 cases)
    level: E4
    confidence: 0.9
  - statement: "Delta below 1e-3 nats per token implies E_sel is negligible (falsifier F2)"
    status: contradicted
    evidence: redteam_selection.log block G (p=(0.999,6e-4,4e-4), N=128: Delta 9.9e-4 per token, E_sel 4.3e-3 per token; the ratio grows with N)
    level: E4
    confidence: 0.85
  - statement: "The reveal-and-requery S^ measures the model's cross-modal dependence"
    status: mixed
    evidence: redteam_selection.log block J (zero dependence, inconsistent marginals, S^ = 0.081 nats per image token)
    level: E4
    confidence: 0.85
  - statement: "G > 0 for randomised position laws (Theorem 1 text)"
    status: contradicted
    evidence: redteam_selection.log block K (uniform random order, k=1, exact marginals, G = 3.5e-16)
    level: E4
    confidence: 0.95
competing_explanations:
  - Every positive toy result about SF (sharpening, U-shape, entropy loss) has the same cheapest explanation, a state-dependent temperature, because at k=1 SF is in law a state-only tilt with a randomised position law (block C).
  - E_sel values with an imperfect model mix value selection with E_learn repair (T1.8 of the report) and with E_fact repair (S2 here); a nonzero E_sel does not identify a selection cost.
  - The U-shape and the T4(a) counterexample depend on exact score ties (binary Markov data with symmetric start; uniform x2 and identical x3/x4 marginals).
unknowns:
  - Whether a tie-free q exists with H(p_SF) > H(p_mRS) at the output (none found in 800 tries).
  - Whether E_sel can change sign between references with an exact model (0 cases found; all 27 flips involve an imperfect model).
  - What 2604.00375 Prop. 2 actually assumes (not re-read here).
next_test: {hypothesis: "On a frozen MDLM checkpoint the SF-minus-mRS gap in unigram entropy and GenPPL equals the gap between mRS and mRS with a state-only tilt fitted to SF's per-state value law (block C twin)", intervention: "add a fifth arm, rank by rho_SF and sample from the closed-form kappa_i, at T in {64, 256, 1024}", primary_metric: "paired difference SF minus twin, which must be zero in law at k=1", falsifier: "a nonzero SF-minus-twin difference at k=1 beyond the bootstrap interval would indicate an implementation bug, not a selection effect", gpu_hours: "not estimated"}
```

# Red-team audit: the selection term (E_sel), tilts (E_tilt) and the cross-modal term (E_fact^X)

Target: `research/review/method/selection-term.md` (method-architect, 2026-10-14, commit 49b6a29) and
its check script. Scope: problems only. Severity: **fatal** (the claim as worded is false and would go
into the paper), **major** (the claim survives only after restriction, or the evidence does not
support the wording), **minor** (precision, scope or coverage). Each finding gives the location, the
problem, a counterexample or the broken step with a command and its output, the result that would
reject the claim, and the minimal fix the brief asked for (scoping or wording only).

Reproduction. `python analysis/framework/check_selection.py` reproduces
`analysis/framework/check_selection.log` byte for byte (61 checks, 13 s). The red-team numbers come
from

    python analysis/framework/redteam_selection.py  > analysis/framework/redteam_selection.log    (about 67 s)
    python analysis/framework/redteam_selection2.py > analysis/framework/redteam_selection2.log   (about 9 s)

Both import the report's kernels (`k_sf`, `k_rs`, `k_matched`, `budget`, `sf_closed`) unchanged.
Logs are natural throughout; the report and the scripts agree on natural logs.

---

## Findings, ranked

### FATAL

**F1. The V1/V2 split (tilts "inside the identity", selection "outside it") is not a property of the
sampler's law.** Location: T1.2 (V1, V2, V3 definitions), T1.5, Summary (4), edits 3, 12, 13, and by
inheritance edit 10 and the census reclassification.

- Broken step. A path law depends only on the kernel kappa(A, y | s). By Proposition 4 (the report's
  own result), at k = 1 the SF kernel is kappa_SF(i, v | s) = rho(i | s) * kappa_i(v | s), with
  rho(i | s) = sum_v p^i(v) Pi_i(p^i(v)) and kappa_i(v | s) = p^i(v) Pi_i(p^i(v)) / rho(i). Both are
  functions of the marginals at s. So "draw i from rho(. | s) with fresh noise, then draw v from the
  state-only transform p~^i := kappa_i" is a V1 sampler under the report's own definition (T1.2 V1:
  "p~^i = T_s(p^i) is a state-only transform"; CFG already needs T to depend on i through the state).
  It has exactly SF's law. At k >= 2 the SF value law kappa(y | A, s) is a non-product, state-only law.
  That is the V3 definition ("rho ⊗ kappa_joint(y|A,s) with a non-product value law"). As a class of
  laws V2 is therefore empty. "Reads the sampled values" describes an implementation, not a law.
- Check: block C, `redteam_selection.log` lines 69-70:
  `noise=0.0: max |p_SF(x) - p_V1(x)| = 5.6e-17; KL(q||p_SF) = 1.288069; forward per-step tilt term E_tilt of the V1 twin = inf`
  (and the same at noise 0.4). The SF twin, classed as V1, has the same +inf forward term that
  Proposition 2 attributes to selection. The report concedes (T1.3, T5.6) that top-p and argmax also
  have +inf forward E_tilt. "Inside versus outside the identity" therefore separates nothing: Theorem 1
  holds for every kernel, and the forward value term is +inf for argmax, for top-p with any data token
  outside the nucleus, and for SF with a blocked pair alike.
- Consequence. Edit 3 ("Only value-dependent selection ... breaks the precondition") is false under
  either reading of the precondition. Under the strict reading (values drawn from p_theta), every tilt
  breaks it. Under the loose reading (identity with p~ in place of p), SF at k = 1 satisfies it.
  Edits 12 and 13 install a four-class taxonomy whose stated mathematical justification is wrong. A
  CSUR referee needs only the two lines above to refute it.
- The claim is rejected if any SF kernel at k = 1 has a law that no rho ⊗ prod p~ with state-only p~
  can reproduce. Proposition 4 rules this out.
- Minimal fix: present V1, V2 and V3 as implementation mechanisms (what the code reads) and drop
  every sentence that ties the classes to "inside or outside the identity". At the level of the law
  the only distinctions are whether the value law equals prod p and whether it is a product.

**F2. "Per-step forward accounting of E_sel is impossible for SF" is false; it is a property of one
chosen data path law.** Location: T1.3 Proposition 2 and the sentence after it ("This is the clean
negative"), Summary (1), T5 table row "Forward per-step SF term", edit 4 (the quoted sentence), edit
14 ("per-step-impossibility result" placed under "Claim").

- Broken step. Theorem 1 couples q with the sampler through one data path law, Q_kappa, in which
  positions are drawn from SF's marginal position law and are independent of the data values. Any
  path law Q whose output marginal is q gives KL(q||p) = KL(Q||P) - G_Q. Take Q', the
  **data-scored** path: rank the masked positions by the SF score of the *data* value,
  g_j(x^j) = p^j(x^j), with the same tie rule, and commit the data values. If Q' commits (i, v) at s,
  then SF commits the same pair with probability at least prod_j p^j(x^j) > 0 (the event that every
  draw equals the data value). So Q' ≪ P_SF, and every per-step term is finite. This is the path
  that Lemma 3's proof already builds ("follow its own-score greedy order"), so the report holds the
  counterexample in its own proof.
- Check: block A, `redteam_selection.log` lines 6-39. KL(Q'||P_SF) is finite in 32 of 32 SF
  configurations (k = 1, k = 2, margin score, tau = 0.7; exact and perturbed predictors). Examples:
  `L=4 seed=0 noise=0.0 SF k=1  1.32216  inf (report)  2.53097  1.20881  0`. The framework toy gives
  `KL(q||p_SF)=1.288069 KL(Q'||P_SF)=2.235811 G'=0.947742 blocked x: 0`.
- What remains true is narrow: the value term V of Theorem 1, under Q_kappa, is +inf. That supports
  "the published E_fact + E_learn form, evaluated on Q_kappa, cannot absorb SF", not "impossible".
- The claim is rejected by any finite forward per-step decomposition with output marginal q. Block A
  supplies one.
- Minimal fix: restate Proposition 2 as "under the data path law with SF's position law (Q_kappa),
  the value term is +inf", and remove "impossible" from edits 4 and 14 and from the Summary.

### MAJOR

**M1. E_sel depends materially on the reference, including its sign. "Canonical" rests on a
direction choice and a class restriction.** Location: T1.4 ("Why this reference is canonical", items
1-3), yaml claim 3.

- Sign. Over 480 imperfect-model configurations (L = 3 or 4, V = 2 or 3, model = exact marginal^beta
  with beta in {0.4, 0.7, 1.0, 1.5}, plus a log-normal tilt), the sign of
  E_sel = KL(q||p_SF) - KL(q||p_ref) differs across four RS references (mRS; RS-conf, ranked by
  max p; RS-E, ranked by the expected SF score sum_v p(v)^2; RS-uniform) in **27 of 480**
  (`redteam_selection2.log`, S1). Two flips between mRS and the "intended" RS-conf alone:
  `(40, L4, V2, k2, beta 0.7, noise 0.3): mRS +0.1461, RS-conf -0.0332`;
  `(0, L4, V2, k2, beta 0.4): mRS -0.0166, RS-conf +0.0752`.
- Size. In the report's own 24 SF configurations (block D), the spread across references reaches
  0.472 nats: `L=4 s=0 n=0.5 SF k=2: mRS +0.5986, RS-conf +0.2064, RS-E +0.4133, RS-unif +0.6787`,
  a factor of 3.3. At k = 1 with exact marginals all references agree, because every RS reproduces q.
  The reference matters exactly where E_sel would be reported, with imperfect models and k >= 2.
- Projection argument (item 1). (a) It is the M-projection argmin_rho' KL(kappa || rho' ⊗ prod p).
  The I-projection argmin_rho' KL(rho' ⊗ prod p || kappa) gives
  rho'(A) ∝ rho(A) exp(-KL(prod_{i in A} p^i || kappa(.|A))), a different matched reference that
  gives zero weight to any A containing a blocked value. Neither is privileged, and E_sel itself uses
  the forward direction KL(q || .), the opposite of the projection used to pick its reference.
  (b) The projection is onto {rho' ⊗ prod p} only. Onto RS ∪ V1, which the report places inside the
  identity, the projection of SF at k = 1 is SF itself (F1), and E_sel = 0.
- No double counting (item 2) holds by construction, because E_sel is defined as the residual. It
  does not show that the residual is "which values": see M2.
- The claim is rejected if a review reader can choose another defensible RS reference and get a
  different sign. S1 shows such readers exist.
- Minimal fix: drop "canonical". Write "E_sel relative to reference R", always name R, and report
  E_sel against at least two references (mRS and RS-conf) when giving a value.

**M2. With an exact model, SF's selection can lower KL below its matched twin. E_sel absorbs
factorisation repair, so "which values is charged to E_sel only" and "selection creates dependence ...
that has nothing to do with q" are false.** Location: T1.4 item 2; T2 "At k >= 2 the committed
values are coupled ... nothing to do with q"; T1.4 "positive in all 32 random SF configurations".

- Counterexample (`redteam_selection2.log`, S2 and S6): q drawn by rng seed 5, draw t = 389,
  L = 4, V = 3, Dirichlet 0.05, exact marginals, k = 3:
  `KL_SF=0.98630 KL_mRS=1.07293 E_sel[mRS]=-0.08663 KL_RSconf=1.13736 E_sel[RS-conf]=-0.15107`.
  The values are identical under random ties and under 1e-4 jitter. E_learn = 0, so the negative part
  can only come from SF's in-set and position-value coupling, which partly matches q's dependence:
  it repairs E_fact. The "positive in 32 of 32" statistic is a sample property, not a sign result.
  T1.8 already showed E_sel < 0 through E_learn repair. S2 shows the same through E_fact repair with a
  perfect model.
- The claim is rejected by one exact-model configuration with E_sel < 0. S6 is one.
- Minimal fix: describe E_sel as "the output-level effect of the value rule relative to R, which
  includes interaction with E_fact and E_learn", and delete "nothing to do with q".

**M3. The definition charges temperature, top-p and guidance used inside SF to E_sel, which
contradicts T1.5.** Location: T1.2 (kappa° := rho_kappa ⊗ prod p, untilted), T1.4, log lines for
`SF k=1 tau=0.7`, edit 12.

- In `check_selection.py`, `k_sf(..., tau=0.7)` draws from p~ while `k_matched` draws from p. The
  reported E_sel of tempered SF (2.04569 at seed 0, noise 0) therefore contains the temperature tilt.
  With the tilted matched reference rho_SF ⊗ prod p~ it is 1.9690. With a perturbed model the
  differences are 0.17 to 0.20 nats, e.g. `L=3 s=3 n=0.5 SF k=1 tau=0.7: +1.5871 (mRS) vs +1.3906
  (mRS tilted)` (block D). UniDisc, row M21, uses "MaskGIT confidence with top-p and temperature; CFG
  w=1.5". Under the definition all three tilts become E_sel, and top-p makes the SF draw law lose
  full support, which takes Lemma 3's finiteness away. E_sel can then be +inf from truncation alone.
- The claim is rejected if E_sel of an SF sampler changes when only a state-only tilt of its draws
  changes. Block D shows that it does.
- Minimal fix: define kappa° with the same draw law as the sampler (rho_kappa ⊗ prod p~), and state
  that E_sel is computed after the tilt.

**M4. E_tilt is "the cost of the tilt" only when the ranking uses untilted marginals. It is +inf for
argmax and top-p, so placing them "inside the identity" carries no information. Edit 10 applies it to
a revision sampler that Theorem 1 does not cover.** Location: T1.3 Consequences (V1), T1.5, T5 row
E_tilt, check T5.7, edits 3, 10, 12.

- Ranking. T5.7 builds the tempered sampler as `k_rs(p, rho_conf(p, 2), 3, transform=tr)`, ranking
  by the *untilted* p. In that case rho does not move, and the whole change is E_tilt. If confidence
  is computed from tilted probabilities, the ranking moves. Hand example: p1 = (0.6, 0.4) and
  p2 = (0.55, 0.15, 0.15, 0.15) have max p 0.60 > 0.55 at tau = 1, but 0.692 < 0.818 at tau = 0.5.
  The tempered sampler then has a different rho, and the change in KL against the untempered sampler
  includes Delta E_fact[rho] and Delta E_learn[rho], not E_tilt alone. The report says this for CFG
  (T1.5) but not for temperature or top-p. Whether particular released samplers compute confidence
  after temperature or top-p was not verified here (E0). The check covers only the case that passes.
- Infinity. For argmax, E_tilt = +inf unless q is deterministic on visited states (T5.6). For top-p
  0.9 it is +inf as soon as one data token falls outside the nucleus. So for LLaDA at temperature 0,
  ReMDM top-p 0.9, BD3-LM top-p 0.9 and DiffuLLaMA the identity reads inf = inf, and the only finite
  measurable quantity is a reverse self-distortion, the same type of object the report uses for SF
  (T5 "Argmax: D = sum -log max p"). That is a further reason the V1/V2 line is empty (F1).
- Revision. ReMDM remasks committed tokens. Theorem 1 is stated for commit kernels on the erasure
  channel with no revision (T1.1), so "reclassify ReMDM's top-p 0.9 as E_tilt" (edit 10) assigns a
  term that the theorem does not define for that sampler. P3's first clause still lists only E_learn
  and E_sel, so E_tilt is missing from P3 even after edit 10.
- Minimal fix: state "E_tilt = Delta KL at fixed rho; when the tilt also feeds the ranking, the
  change also moves E_fact and E_learn"; mark argmax and truncation rows "+inf, no finite forward
  cost"; restrict edit 10 to non-revising samplers or extend Theorem 1 first.

**M5. The U-shape (E_fact falls, E_sel rises, so there is an interior optimum in T) is a non sequitur,
it is parameter-dependent, and its toy magnitudes depend on the tie rule.** Location: T3 "Steps at
fixed length", yaml claim 8, edit 6, T9 H5.

- Logic. A decreasing function plus an increasing one has an interior minimum only under extra
  conditions on their rates. The minimum can sit at either end.
- Check: block E, `redteam_selection.log` lines 110-141. Binary Markov chains, L in {6, 8},
  flip in {0.05, 0.1, 0.2, 0.3}, start P(x1 = 0) in {0.5, 0.7}, with exact, 1e-4-jittered or
  noise-0.3 predictors. An interior minimum appears in **20 of 32** variants. The argmin is T = 1 in
  10 (e.g. `L=6 flip=0.30 p0=0.5 exact: 0.4114 0.4837 0.4919 1.8992 argmin T=1`, so more steps only
  hurt SF) and T = L in 2 (`L=6 flip=0.05 p0=0.5 jitter 1e-4: ... argmin T=6`).
- Ties. The report's toy (flip 0.1, p0 = 0.5) starts with every marginal at (0.5, 0.5), so every
  score ties. Under random ties SF's KL at T = 2 and 3 is 0.5430 and 0.2037, against the quoted
  1.0249 and 0.8355. The quoted E_sel values (+0.451, +0.652) are artefacts of the tie rule in
  magnitude.
- The claim "SF has an interior optimum in T" is rejected by any dependent-data toy with argmin at
  T = 1 or T = L. Block E has 12.
- Minimal fix: report the U-shape as "can occur" (20 of 32 toy variants) with the tie rule stated,
  and delete the causal "so there is an interior optimum".

**M6. Codex objection 2 (P1 identification) still stands after edit 11.** Location: framework-v1 P1
and edit 11.

- Broken step. For deterministic RS rules at k = 1, gain = Delta E_learn(k = 1) exactly (E_fact = 0,
  G = 0). The states visited at k = 2 differ from those at k = 1, so
  Delta E_learn(k = 2) != Delta E_learn(k = 1), and "growth with k estimates the E_fact part" mixes
  the two.
- Check: block I, `redteam_selection.log` lines 180-204, confidence-ranked against left-to-right,
  perturbed predictors, L = 4, k in {1, 2}. Delta E_learn at k = 2 differs from the k = 1 gain by more
  than 25 % or in sign in **11 of 12** cases. Sign flip: q-seed 2, noise 0.3: Delta E_learn = -0.0068
  at k = 1, +0.0289 at k = 2. Size: q-seed 0, noise 0.3: the k = 1 gain is -0.0402, the true
  Delta E_fact(2) is +0.1743, and P1's estimate gain(2) - gain(1) = +0.1155.
- Edit 11 adds only an SF caveat and does not touch this.
- The claim is rejected if Delta E_learn depends on k. Block I shows it does.
- Minimal fix: reword P1 as "the k = 1 gain is the E_learn difference at k = 1; at k > 1 the E_learn
  difference is unidentified from the step sweep alone".

**M7. Falsifier F2 is invalid, and the T9 programme never measures E_sel.** Location: T9 F2, yaml
next_test falsifier, H1, H4; T1.4 "Relation to E_sel: neither equal nor a bound".

- The report states that Delta neither equals nor bounds E_sel, then uses "Delta < 1e-3 nats per
  token" to declare E_sel negligible. Block G (iid data, exact marginals, SF k = 1, so
  E_sel = KL(q||p_SF)): for p = (0.999, 6e-4, 4e-4) and N = 128, Delta = 9.926e-4 per token (below
  the threshold) while E_sel = 4.258e-3 per token. The ratio rises with N (2.01, 2.68, 3.42, 4.29 for
  N = 16 to 128). In the report's own flat example it reaches 18.7 at N = 128. At L = 1024 F2 would
  pass with E_sel an unbounded multiple of Delta.
- The primary metrics (unigram entropy, GenPPL) are not KL(q || .) and are not sign-guaranteed
  (T4(a)). E_sel as defined is not computable on any real model (T5, last row). So the experiment can
  falsify H2 to H5 but cannot measure the quantity the review names.
- Minimal fix: delete F2 or reword it as a statement about Delta only; write T9 as a test of the SF
  versus mRS contrast on proxies, not a measurement of E_sel.

**M8. "D <= KL_cont(N, k) for any marginal under random ties" is false for non-identical
marginals.** Location: T2 limit (b) (proof sentence "by data processing D <= KL_cont for any
marginal"), T3 "Answer ...", T5 "KL_cont(N, k) is the diffuse-vocabulary reference", T9 H1 ("far
below the diffuse-vocabulary curve"), edit 6.

- Broken step. The quantile-bin argument needs one monotone map from U_j to score that is common to
  all positions. With different marginals each position has its own map, the selection is not by U,
  and data processing does not apply. Check T3.7 tests only iid marginals (`iid_random_D(p, N, k)`
  with one p).
- Check: S5 (k = 1): **255 of 3000** random heterogeneous states violate it; worst
  `N=2: D=0.3672 > KL_cont(2,1)=0.1931`. Block H (k <= 2): 489 of 3000, worst
  `N=3 k=2 D=0.52854 > KL_cont=0.26528`. Language-model states are heterogeneous, so as a bound the
  curve says nothing about a checkpoint.
- Minimal fix: restrict to "identical marginals" everywhere; use H(rho) or log C(N, k) as the only
  general bounds.

**M9. The output-level counterexample of T4(a) exists only on the tie set.** Location: T4(a) "At the
output: false", yaml claim 7, edit 9 ("but not always at the output [V T4.2]").

- In the construction x2 is uniform (all values tie at 1/3) and x3 and x4 have identical marginals.
  Block E: `exact, random ties: H(p_SF)=3.34388 > 3.24753` (it survives a fair tie rule), but
  `ties broken by 1e-4 log-normal jitter: H(p_SF)=3.18736 < 3.24753`, and the same with a second seed.
  S3: 0 of 200 multiplicative perturbations of q (1e-3 to 5e-2) and 0 of 600 random "gated" q
  reproduce it. The SF kernel is discontinuous at ties, and the counterexample sits on the
  discontinuity.
- Mathematically it remains a counterexample (q and the tie rule are admissible). As evidence that
  the entropy diagnostic fails for continuous-logit models it is degenerate. P3's entropy diagnosis is
  weakened less than the report says.
- Minimal fix: state "counterexample requires exact score ties; no tie-free counterexample found"
  and keep "typical but not guaranteed" only with that rider.

**M10. The cross-modal estimator: model inconsistency biases it, the cheap version has uncontrolled
bias, and it does not measure the framework's E_fact^X.** Location: T6 estimator, "When p_theta is not
exact", T9 Algorithm 5, edit 8.

- Inconsistency bias. With a drawn from the model's own joint,
  E_a KL(p(b_j|s,a) || p(b_j|s)) = I_theta(a; b_j) + KL(mean_a p(b_j|s,a) || p(b_j|s)). The second
  term is nonzero whenever the masked model is not marginally consistent. Block J: a model whose
  image marginal does not depend on the text at all, but shifts from (0.4, 0.3, 0.3) to
  (0.6, 0.2, 0.2) when any text is revealed, gives S^ = 0.08109 nats per image token with zero
  dependence. The shift is plausibly largest at early steps, where the masking ratio changes most.
  That is the same place P5a predicts front-loading, so the confound points the same way as the
  hypothesis.
- Cost and bias. "R extra passes, whatever k_I is" holds only for the product-of-marginals draw of a.
  Its bias bound ||f||_inf sqrt(TC(a|s)/2) has an unbounded ||f||_inf (f is a sum of KLs) and grows
  with the within-text TC, which is largest at early steps. The unbiased version needs a joint draw of
  a: k_T sequential passes per sample, so R k_T passes. Algorithm 5 specifies the biased version.
- Target. Framework 2.2 defines E_fact^X = X = I(a; b | s). The estimator targets S. X - S takes
  either sign (388 of 500 in T6.2) and in the toy differs by 30 % (X = 0.804, S = 0.615). S_{T->I}
  and S_{I->T} differ as well. So "the cross-modal term" is split-dependent, the same
  non-uniqueness as E_sel. P5b is stated in X, and a measurement of S cannot test it.
- It says nothing about q: S_theta is computed on sampler states, and no inequality links
  |S - S_theta| to E_learn.
- Minimal fix: name the split in every sentence ("text-first S_theta"); add the inconsistency term
  to the estimator's description; state the cost of the unbiased version as R k_T passes; restate P5b
  in S or keep X unmeasured.

**M11. After the reclassification the census cannot support "29 of 40 headline results use an
E_sel-type rule", and the reclassification has no defined target for about half its rows.**
Location: design-space-v1.md section 4 (b), and section 5 (c) where it cites P2.

- Under the new taxonomy only the S class is E_sel: 4 rows (MaskGIT, Show-o, UniDisc, Dynin-Omni).
  The 9 guidance-only rows move to E_tilt. Under F1, even the 4 are E_tilt in law at k = 1.
- No term defined: (i) Gaussian or embedding channels, whose "argmax" is final rounding (Diffusion-LM,
  CDCD, Plaid, SSD-LM, TESS, TESS 2, DiffuSeq); (ii) the uniform-state channel (Duo Greedy-Tail);
  (iii) CFG on continuous image channels (Transfusion, BAGEL, Show-o2); (iv) sequence-level selection
  (DiffuSeq MBR, FUDOKI best-of-n), which is not a commit kernel. Theorem 1 is stated for the erasure
  channel with commit kernels (T1.1), so neither E_sel nor E_tilt is defined for these rows.
- "For the other 24 an E_sel component cannot be diagnosed from the paper (P2 needs entropy)" rests
  on P2, which T4(b) refutes (S4 here). No diagnosis from a paper's reported numbers is possible under
  the replacement diagnosis either, because it needs the SF versus mRS arm that no paper runs.
- What the census can still support: "29 of 40 headline numbers use a value rule other than plain
  sampling at temperature 1 (truncation, temperature, argmax, guidance, sample-then-filter or
  sequence-level selection); 5 report entropy next to the headline; 1 of 14 guided models sweeps
  steps with guidance fixed."

### MINOR

- **m1. "G > 0 for randomised position laws" (T1.3) is false in general.** Block K:
  `noise=0.0: path KL=-0.000000 output KL=-0.000000 G=3.54e-16` for a uniform random order, k = 1,
  exact marginals. G = 0 whenever Q(path | x) = P(path | x). T1.5 tests one case. Fix: "G >= 0, and
  strictly positive in the cases checked".
- **m2. Subtractive form and integrability.** KL(q||p) = KL(Q||P) - G (T1.3) and the E_sel split
  (T1.4) are inf - inf for SF (KL(Q_kappa||P_SF) = G = +inf). V in Theorem 1 is a difference of
  expectations that can also be inf - inf when E_learn = +inf (top-p, argmax, non-full-support
  predictors). Fix: use KL(Q||P) = KL(q||p) + G and state finiteness conditions for V.
- **m3. "32 of 32 SF configurations" is a V = 3 statistic.** Block B (exact model, continuous
  scores): the probability that a data pair is blocked falls from 0.19 (V = 3, N = 8) to 4e-6
  (V = 1e4, N = 8, logit sd 1) and 1.7e-10 (sd 3). The forward value term is still +inf in expectation
  whenever that mass is positive, and its finite part is large (about 59 nats per step at N = 64, sd 1).
  The substance holds; the 32 of 32 frequency overstates how common blocking is on real vocabularies.
- **m4. "E_sel grows about quadratically in L" comes from one flat marginal.** With p = (0.99, 0.006,
  0.004), E_sel per token goes from 0.0212 to 0.0647 for N = 16 to 128 (block G), roughly N^0.54 per
  token, so N^1.54 in total. Fix: "superlinear in the cases computed".
- **m5. T7.** Case (a2) mixes memory with a random rho: block K shows G = 0.151 for a random rho with
  no memory at all. The correction "a function of the revealed path is not enough" is a statement
  about randomised rho, which framework-v1 already makes. Edit 1's "iff E_q KL(Q(path|x)||P(path|x))
  = 0" restates the definition of G (a tautology).
- **m6. Lemma 3** is an upper bound. "That matches the roughly quadratic growth" explains nothing,
  because an upper bound's order does not set the observed order.
- **m7. T6 P <= S.** The displayed step "I(a; b_j) = sum_i I(a_i; b_j, a_<i)" holds only with
  mutually independent text tokens. The condition is in the sentence but not at the step.
- **m8. Novelty column (T10).** "Not found in the files read" covers files only, not a literature
  search; only 2604.00375 was re-read. The k = 1 iid law is best-of-N with the token's own probability
  as the reward. The log N - 1 + 1/N KL value is known from best-of-n alignment work (my
  recollection: Beirami et al., 2024, "Theoretical guarantees on the best-of-n alignment policy"; E0,
  identifier not verified), as the report itself suspects.
- **m9. Coverage of the check script versus the text.** (i) T1.1 never tests Theorem 1 on a finite,
  non-product, non-oracle kernel: every SF case is inf = inf and the only finite non-RS kernel is the
  oracle joint draw. (ii) T1.7 tests Gibbs' inequality at one state with 200 perturbations. (iii) T3.7
  tests iid marginals only, though the text says "any marginal" (M8). (iv) T5.7 uses untilted ranking
  (M4). (v) T4.2 and T3.16 rely on exact ties (M5, M9). (vi) `r_max` assumes distinct probabilities
  (docstring) and gives the wrong law for tied values (for two equal-probability values it returns
  2[(F+p)^N - F^N] instead of (F+2p)^N - F^N). The quoted cases avoid ties, but T3.8's "300 random p"
  would not catch the error, and anyone reusing the function on an LM row with ties would get wrong
  numbers. Check: `cd analysis/framework; python -c "import numpy as np, check_selection as cs; print(cs.r_max(np.array([0.5,0.5]),2), cs.r_max(np.array([0.4,0.3,0.3]),2))"` gives `[0.25 0.25]` (sum 0.5) and `[0.64 0.09 0.09]` (sum 0.82): with ties the returned law does not sum to 1. The 61 PASS lines check what the code computes; they do not cover the general wording
  attached to them.
- **m10. T9 design.** Common random numbers couple SF and mRS only at the first selection, and the
  trajectories diverge after step 1. GenPPL falls with entropy, so "lower GenPPL" is not "better"
  without an entropy-matched frontier (CANDI App. D.3 reports that a temperature grid search
  reproduces step effects, as cited in design-space section 4). The cost figures and the checkpoint
  identifiers are E0.

### Codex round-2 objections against the report

| Codex objection | Answered by selection-term.md? |
|---|---|
| 1. E_sel conflates distinct changes; is it uniquely defined? | Partly. Tilts were split off, but the split is not a law property (F1) and E_sel is reference-dependent in sign (M1). Still stands in substance. |
| 2. P1: changed state visitation makes the k = 1 gain differ from the E_learn part | Not answered; edit 11 adds an unrelated SF caveat. Stands (M6, block I). |
| 3. P2: entropy below a reference does not identify E_sel | Answered: P2 deleted (T4(b)); S4 here shows the diagnostic itself misfires at fixed steps. Codex was right. |
| 4. P3: T >= L does not make the gain E_learn or E_sel only | Partly. Entropy diagnosis replaced; but P3's first clause omits E_tilt, and revision is outside Theorem 1 (M4). Stands. |
| 5. P5a/P5b: estimation and attribution of the cross-modal term | Partly. An estimator is given, but it targets S not X, is biased by inconsistency, and its cheap form has uncontrolled bias (M10). Stands. |
| 6. Memory: exact projection condition | Answered (T7), with the tautology and confound in m5. |

---

## Answers to Q1-Q8

**Q1 (Theorem 1).** As a formal identity it is correct. The position factor cancels because Q_kappa
is *defined* with rho_kappa(A | s) = sum_y kappa(A, y | s), the law of positions after the sampled
values are integrated out. The dependence of SF's positions on its sampled values is pushed entirely
into kappa(y | A, s), so "same rho" holds by construction, not as a property of SF. The cost of that
choice is that Q_kappa is one coupling among many. Under the data-scored coupling Q' the forward path
KL is finite (F2), so every consequence drawn from the +inf value term belongs to Q_kappa, not to SF.
G = 0 for deterministic state-only policies is correct (the path is a function of x under both laws);
it needs a deterministic tie rule and deterministic memory. The companion claim "G > 0 for randomised
position laws" is false in general (m1). The subtractive form is inf - inf for SF (m2).

**Q2 (is matched RS canonical?).** No. The KL-projection argument picks the M-projection, while the
I-projection gives a different matched reference (rho' ∝ rho exp(-KL(prod p || kappa(.|A)))). E_sel
itself uses the opposite (forward) direction. Projecting onto RS ∪ V1 instead of untilted RS makes
SF at k = 1 its own projection, with E_sel = 0. "No double counting" is true only because E_sel is the
residual, and that residual includes E_fact repair (M2) and tilts (M3). Other references give
materially different values: up to a factor of 3.3 in the report's own configurations (block D), and
a different sign in 27 of 480 imperfect-model configurations (S1), including mRS against the
"intended" RS-conf. The reference ranking by the expected score coincided with RS-conf in most small
cases, so the material alternative is RS-conf. A review should write "E_sel relative to R", name R
every time, give values against at least mRS and RS-conf, and avoid "canonical".

**Q3 (the reclassification).** As kernels, temperature, top-p, argmax and CFG are state-only and
fall under Theorem 1 with p~. That part is right. But: (i) the justification "inside versus outside
the identity" separates nothing, because SF at k = 1 is in law a state-only tilt with randomised
rho (F1). (ii) "E_tilt is its cost" holds only at fixed rho. When guided or tempered marginals drive
the ranking, as with CFG plus confidence ranking and temperature applied before the confidence,
rho moves and the cost includes Delta E_fact and Delta E_learn (M4; hand example in M4). (iii)
LLaDA at temperature 0 (argmax value, ranked by argmax probability) is a deterministic state-only
kernel with G = 0, so it is V1 as the report says. Its E_tilt is +inf for any non-degenerate q,
however, so "inside the identity" reads inf = inf, and the only finite diagnostic is the reverse
quantity sum -log max p, the same type as SF's Delta. (iv) For Gaussian, uniform-state and
continuous-image channels, and for sequence-level selection, neither E_tilt nor E_sel is defined
(M11).

**Q4 (T4 counterexamples).** T4(b) is valid. The closed forms check out (H(p) = 2 ln 2 + ln V',
H(q) = ln 2 + h(eps) + 2(1 - eps) ln V', KL = ln 2 - h(eps)). It kills more than the premise: at
fixed T = 2, moving from partition {x3,x4},{x1,x2} to {x1,x2},{x3,x4} lowers KL from 0.617 to 0.368
through E_fact alone, while entropy falls from 4.131 to 2.773, below H(q) = 3.514 (S4). That is
exactly the pattern P2 attributes to E_sel or mode-seeking E_learn, so P2's diagnostic, not only its
"from above" premise, is refuted. T4(a) is valid only on the tie set: a 1e-4 jitter reverses it, and
800 tie-free attempts found no counterexample (M9). So T4(a) kills a "guaranteed" version of P3's
entropy diagnosis only formally. For continuous-logit models a weaker version ("SF lowers output
entropy relative to mRS") is neither proved nor refuted.

**Q5 (U-shape).** In the toys it is more than one artefact but less than a mechanism. It appears in
20 of 32 variants and fails in 12, with argmin at T = 1 in 10 and at T = L in 2. The quoted
magnitudes move by a factor of 2 to 4 with the tie rule (M5). A real-model test needs to rule out:
(a) E_learn on visited states, since SF and mRS visit different states after step 1, so the contrast
includes Delta E_learn(visited), which the report concedes; (b) ties, since bf16 confidences tie often
and top-k tie-breaking is implementation-defined, which index versus random ties shows can matter by a
factor of 2 to 4; (c) float precision, since 32-bit Gumbel draws sharpen all arms (Zheng et al., via
the primer) and interact with SF, which selects high-probability draws; (d) the schedule, since k_n
profiles (cosine against linear) change the selection pressure per step; (e) MaskGIT-type annealed
noise in the selection, which randomises rho in a T-dependent way; (f) entropy confounding of
"quality", which needs an entropy-matched frontier; and (g) a state-only tilt twin fitted to SF's
per-state value law (block C). If SF equals its twin in law at k = 1, any SF-specific U-shape must
come from k >= 2 coupling or from implementation error.

**Q6 (P1 after edit 11).** Codex's objection stands (M6). In 11 of 12 toy cases the k = 1 gain
does not equal the E_learn part at k = 2, and one case flips sign. Edit 11 adds an SF caveat and does
not address the state-visitation interaction.

**Q7 (cross-modal term).** The two splits are correct; the algebra was re-derived and T6.1 passes at
1.3e-15. S is estimable with R extra passes only in the product-draw form, whose bias has no usable
bound; the unbiased form needs R k_T sequential passes (M10). Under an imperfect model the estimator
returns I_theta plus a nonnegative marginal-inconsistency term, which can be positive with zero
dependence (block J: 0.081 nats per token). It cannot say anything about q: it is computed on sampler
states with p_theta, and no inequality links S_theta to S through E_learn. It also targets S, not the
framework's E_fact^X = X, and X - S takes either sign.

**Q8 (what a CSUR referee would call trivial or overreaching).**
- Trivial (chain rule or definitions restated): Theorem 1 (the report itself calls it "a
  corollary"); E_tilt (definitional); the T6 splits (textbook chain rule); T7 and edit 1 ("iff G = 0"
  is the definition of G); D <= H(rho) (conditioning on an event); Proposition 5's entropy step
  (Schur concavity); the k = 1 iid law and log N - 1 + 1/N (best-of-N, m8).
- Overreaching: "impossible" in Proposition 2 (F2); the V1/V2 taxonomy as mathematics (F1);
  "canonical" (M1); "which values only" (M2); the U-shape as a mechanism (M5); KL_cont as a bound
  (M8); F2 and the T9 framing as a measurement of E_sel (M7); S as "the" cross-modal term (M10); the
  census after reclassification (M11). More generally, toys with L <= 8 and V <= 4 carry every claim,
  and the novelty column rests on files read, not a search.
- Referee verdict on the framework section as it would stand after the 15 edits: major revision
  leaning to reject for the "new terms" part, confidence 4/5. **The experiment whose absence would
  cause rejection:** on one frozen checkpoint, SF against matched RS against RS-conf against the
  block-C tilt twin, at matched passes and with an entropy-matched frontier. Without it E_sel is a
  named residual with no measured size and no shown difference from a state-dependent temperature.

---

## What survives

1. Proposition 4 (closed-form SF commit law, any k, ties, priorities): exact, checked at 3e-16.
2. Proposition 5 (k = 1 majorisation, so the per-state entropy falls) and the per-state inequality
   H(SF step) <= H(mRS step) at k = 1.
3. Lemma 3 (KL(q||p_SF) finite for full-support predictors) and D <= H(rho) <= log C(N, k).
4. T4(b): exact marginals with only E_fact can push entropy below H(q). It refutes P2's diagnostic
   at fixed steps.
5. Matched RS ("sample, select, resample") as an experimental control arm, not as a definition.
6. The self-distortion Delta as a model-only diagnostic of the SF versus mRS kernel gap, without F2.
7. The T6 splits as bookkeeping, with the split named, and S_theta as a model-side quantity.
8. T7's correction of "only when", in its non-tautological part (deterministic augmented path is
   sufficient, not necessary).
