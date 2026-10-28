```yaml
agent: red-team
date: 2026-10-29
brief: >
  Adversarial mathematical review of THEORY-ADDENDUM-2026-10-29.md and theory_check_2026-10-29.py (commit 1fed4d2f,
  committed 2026-10-29 00:27:32 +0530): Props 1-3, the numeric script, novelty, and the manuscript wording each proposition allows
  under SAP AB.1/AB.3, K2 (D0074) and the must-not-claims.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/method/THEORY-ADDENDUM-2026-10-29.md (whole file)
  - research/paper2/method/theory_check_2026-10-29.py (whole file; run once on CPU)
  - exp_p2/gate/theory.py (whole file, read-only)
  - paper2/sections/method.tex lines 100-135, 280-345, 400-415
  - research/paper2/benchmark/REDTEAM-P2-PLAN.md A8 (lines 180-189) and C.1/C.2 (lines 280-302)
  - research/paper2/prereg/SAP-GATE-2026-10-28.md section 7 (lines 330-349), AB.1-AB.3 (lines 1132-1154)
  - research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md lines 216-222 (SOFT-A definition only)
  - research/ledgers/decisions.jsonl row D0074
  - research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md section 2.2 (must-not 1-9)
  - research/paper2/ideation/NOVELTY-CHECK-INFFUS-2026-10-28.md section 4 (items 10-13)
  - arXiv 2102.08504 (Li et al., "Label Leakage and Protection in Two-party Split Learning"), Appendix A.3, read from a markitdown
    conversion of the arXiv PDF (text partly garbled; equations 5-11 legible enough to confirm the constant)
  - arXiv 0901.0356 (Reid and Williamson, JMLR 12, 2011), section 6.1, via ar5iv (fetched with a summarising tool; E1)
coverage: >
  Every proposition, lemma, corollary and remark in addendum sections 1-3, its section 4 placement rules and its section 5 output.
  NOT covered: runs/P2-GATE-M4 (not opened, as the brief requires), the M1 rival's code path (whether it is in F_a), NOVELTY-REAUDIT
  section 7 (Trust but Verify), Pepe (2003) (seen only as a quoted snippet, E1), any literature search beyond the three web
  queries listed in section 6.
claims:
  - statement: "Prop. 1(a)-(e) are correct for the POOLED population token AUROC with mid-rank ties; they do not bound the per-item mean AUROC that method.tex quotes (counterexample R1: TV = 0, per-item mean AUROC 0.625)."
    status: supported
    evidence: "hand proof check; scratchpad redteam_checks.py R1"
    level: E0
    confidence: 0.95
  - statement: "The constant |AUROC - 1/2| <= v - v^2/2 is not new: TPR - FPR <= TV and AUC <= integral of min(FPR + TV, 1) = 1/2 + TV - TV^2/2 is the core step of Li et al. (arXiv 2102.08504) Appendix A.3, Theorem 1 proof."
    status: supported
    evidence: "arXiv 2102.08504 App. A.3 eqs (5)-(11), converted PDF"
    level: E2
    confidence: 0.85
  - statement: "Corollary 1.1(iii) misstates (A1): under the changed-code label the law of the context depends on Z; a context-only score -s(o) has AUROC 0.68-0.69 in three toys. The TV formula and the LR monotonicity are correct, and the TV has an exact closed form (the triangle step is tight)."
    status: supported
    evidence: "scratchpad redteam_checks.py R2 (exact enumeration)"
    level: E0
    confidence: 0.9
  - statement: "Lemma 1, Eq. (2.5), the zero-correlation reduction, Remark 2.4 and r* are algebraically correct."
    status: supported
    evidence: "sympy residual 0 (R3); script B1-B5 reproduced"
    level: E0
    confidence: 0.97
  - statement: "Under exchangeable but non-Gaussian correlation, a gate can raise the SNR while lowering accuracy, so Prop. 2 says nothing about accuracy without joint Gaussianity."
    status: supported
    evidence: "R5: SNR 1.081 -> 1.254, MC accuracy 0.9148 -> 0.9094 (s.e. about 0.0008 each)"
    level: E0
    confidence: 0.9
  - statement: "Remark 2.6 (Chair-Varshney under exchangeable dependence) proves only that 1'Delta is the optimal function of the Delta vector under a Gaussian common-mean model; it does not restore Chair-Varshney (likelihood-ratio) optimality relative to the image."
    status: supported
    evidence: "argument in section 3.6 below"
    level: E0
    confidence: 0.9
competing_explanations: []
unknowns:
  - "Whether the sharpness example or the per-item statement of Prop. 1(e) appears in prior work (only three web queries run)."
  - "Whether the D0074 rival (sign-flipped pixel variance) is a member of F_a (depends on whether it reads pixels decoded from tokens or the corrupted source pixels)."
  - "Signs and sizes of gamma_0, gamma_1, gamma_01 on UniDisc (not estimated anywhere; must not be estimated on M4 data for this purpose)."
next_test: {hypothesis: "n/a (review)", intervention: "n/a", primary_metric: "n/a", falsifier: "n/a", gpu_hours: 0}
```

# Red-team review of the theory addendum (Paper 2, GATE), 2026-10-29

**Status: no fatal finding in the mathematics. Nine major findings, of which two (M6, M7) block any use of Prop. 1 or Corollary 1.1(iii)
in the manuscript until the orchestrator records a resolution in the decision ledger.** I did not open `runs/P2-GATE-M4`. I did not
edit the addendum, the script, the manuscript, the code or any ledger, and I committed nothing. No ledger row was added because
the brief forbids it.

Reproduction. `python research/paper2/method/theory_check_2026-10-29.py` on CPU took 23.7 s (GPU idle at 0 % utilisation, 6986 MiB
held by another process). The output is byte-identical to the verbatim block in addendum section 5 (diff after stripping CR). Saved
at `C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad\theory_check_run.txt`.
I wrote independent checks (constructed examples only, no run data):
`C:\Users\Shlok\AppData\Local\Temp\claude\C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-frosty-clarke-209639\859c4d92-4b84-49ba-bcb9-d1cabe9c75dc\scratchpad\redteam_checks.py`,
with output in `redteam_checks_out.txt` in the same folder (2.7 s, CPU). They are cited below as R1-R7. Every number below comes from
a toy or from constructed parameters. None is a UniDisc estimate.

---

## 1. Verdict table

| Item | Verdict | Novelty | Severity of open issues |
|---|---|---|---|
| Prop. 1(a) TV bound, sharpness | VERIFIED for the pooled population AUROC; ties handled correctly | **Known** (Li et al., arXiv 2102.08504, App. A.3). Sharpness example elementary | major (M1 scope, M3 novelty) |
| Prop. 1(b) lower limit and iff | VERIFIED (pooled) | folklore (Youden index = KS; concave ROC) | major (M1 scope) |
| Prop. 1(c) LR optimal | VERIFIED | standard (Neyman-Pearson) | none |
| Prop. 1(d) law-invariant gives 1/2 | VERIFIED | elementary | minor (m4, "on-manifold") |
| Prop. 1(e) pooled and per-item | VERIFIED under (C1)-(C2) and a uniform H given abs(H) | elementary | minor (m5) |
| Cor. 1.1(i)-(ii) | VERIFIED WITH FIXES (well-posed only for one hit per item or sequential updates) | elementary | minor (m3) |
| Cor. 1.1(iii) changed-code label | VERIFIED WITH FIXES (the TV formula and the LR are right; the (A1) premise is false; the bound can be exact) | possibly new as a caveat; not searched | **major (M2, M7)** |
| Cor. 1.2(i) | VERIFIED (pooled only) | elementary | major (M1) |
| Cor. 1.2(ii) cross-modal blind spot | VERIFIED as a toy existence statement | obvious | minor |
| Lemma 1, Prop. 2(b) | VERIFIED (by hand; sympy residual 0; B1 Monte Carlo) | the design-effect algebra is standard | none |
| Prop. 2(c) direction | VERIFIED for gamma_1, gamma_01 >= 0. **The sentence "negative values move it away" is WRONG** for gamma_01 (R4) | -- | minor (m1) |
| Prop. 2(d) large-m, r* | VERIFIED WITH FIXES (two critical points, not one) | standard (Fisher direction of a 2x2 problem) | minor (m2) |
| Prop. 2(e) m-dependence | VERIFIED | -- | none |
| Remark 2.4 conditional SNR | VERIFIED (sympy residual 0) | -- | none |
| Remark 2.6 Chair-Varshney | **Linear algebra right; optimality claim overreaches** | Sherman-Morrison is textbook | **major (M4)** |
| SNR as an accuracy proxy under correlation | not claimed by the addendum, but implied by E-pred's use | -- | **major (M5)** |
| Lemma 2 | VERIFIED (it also needs independence of the weights across classes) | -- | none |
| Prop. 3(a) | VERIFIED WITH FIXES. **"A hard gate is optimal only when pi_1(u) is in {0,1}" is WRONG** (R7) | matched filter, textbook | minor (m6) |
| Prop. 3(b) | VERIFIED WITH FIXES ("xi = 0 iff gamma = 0" needs some mu(u_k) > 0) | KKT, standard | minor (m6) |
| Prop. 3(c) | VERIFIED | -- | none |
| Cor. 3.1 clean-pair cost | VERIFIED (formula and nu); scope fix needed | -- | minor (m7) |
| Script | runs and reproduces; four checks are tautological or vacuous | -- | minor (m8) |

---

## 2. Proposition 1: detailed attack

### 2.1 What is right
- (a) The mixture decomposition, bilinearity, AU(C,C) = 1/2 under the mid-rank convention, and AUROC(-f) = 1 - AUROC(f) are all
  correct. So 1/2 + v - v^2/2 = 1 - (1 - v)^2/2 holds, the degenerate cases v in {0,1} are fine, and ties are handled by the definition.
  The three-point example attains the bound (checked by hand: AUROC = 1 - (1 - v)^2/2).
- An independent route gives the same constant. For any score and any threshold, including randomised thresholds (the linear
  segments of a mid-rank ROC), TPR - FPR <= TV. So AUC <= integral of min(FPR + v, 1) dFPR = 1/2 + v - v^2/2.
- (b) The indicator of {dQ_1 > dQ_0} gives exactly 1/2 + v/2 (checked). The iff statement is correct.
- (c), (d), and the per-item algebra of (e) are correct. Corollary 1.2(i) is the correct inversion v >= 1 - sqrt(1 - 2|a* - 1/2|).

### 2.2 M1 (major): the bounds are for the pooled population AUROC, but the paper reports per-item mean AUROC
method.tex lines 126-128 quote **mean per-item AUROC** (0.964/0.961, 0.560/0.561, 0.511/0.503), and SAP section 7 reports both the
pooled and the per-item AUROC. Prop. 1(a)-(b) and Corollary 1.2(i) bound only P{f(X_1) > f(X_0)} for independent draws from the
pooled class laws. The per-item mean AUROC compares tokens *within* an item, weights items equally, and uses the item grouping,
which is information outside (x_j, O_j) when O_j is coarser than the whole item.
**Counterexample (R1).** f = token value, O = empty. Item A: one corrupted token at 1 and one clean token at 0. Item B: two corrupted
tokens at {0,0} and two clean tokens at {1,0}. The two items are equally likely. The pooled class laws are both {0,0,1}, so v = 0 and
the pooled AUROC is 0.5. The per-item AUROCs are 1.0 and 0.25, with mean **0.625**. So "every within-modality score has AUROC 1/2 iff
Q_0 = Q_1" is false for the paper's headline detection metric. Only (e) makes a per-item statement, and only under its own
uniform-hit-set conditions.
*Fix:* every statement of (a), (b) and Cor. 1.2(i) must say "pooled token AUROC (population)". No sentence may apply v(1 - v/2) to a
per-item AUROC.
*What forces rejection of the claim as worded for the paper:* the counterexample above.

### 2.3 M2 (major): Corollary 1.1(iii) uses a false premise, and the corrected statement is stronger
The corollary says that "(A1) holds for the full context". Under the changed-code label Z, (A1) is false. For a hit token,
P(Z = 1 | o) = 1 - s(o), so the context law under Z = 1 is mu_O(do)(1 - s(o))/(1 - s-bar), not mu_O. The joint formulas the addendum
then uses, Q_1 = mu_O pi(1 - pi)/(1 - s-bar) and Q_0 = mu_O[(1 - h)pi + h pi^2]/(1 - h + h s-bar), are correct as **joint** laws. The
TV computation and the claim that the LR is decreasing in pi_0(x_j | O_j) are both correct (I verified them by exact enumeration).
The premise is wrong, and the consequence it hides matters:
- **The context alone is a detector.** In three random toys (V = 3, L = 4, one Gibbs hit per item, R2), the context-only score
  -s(o), which never looks at the token value, has an exact pooled AUROC of **0.688, 0.679 and 0.685**. The LR score reaches
  0.758, 0.742 and 0.760. The TV of the context marginals alone is 0.27-0.29.
- **The bound can be exact.** The two deviations from the reference mu_O pi have opposite signs at every point, so the triangle
  inequality is tight:
  TV(Q_1, Q_0) = (1/2) E_O sum_y pi |pi - s-bar| * [1/(1 - s-bar) + h/(1 - h + h s-bar)].
  This equals the enumerated TV to 4 decimals in all three toys (R2). The only slack in the addendum's bound is the final step
  sum_y pi |pi - s-bar| <= s(o) + s-bar, and that step is what makes check A4 vacuous (bound 1.76).
*Fix:* drop "(A1) holds". State that the hit indicator is independent of the item and that the context is the full own-modality
context. Replace the bound with the exact expression, and say explicitly that the context itself is informative under Z.

### 2.4 M3 (major): novelty
- The constant is in print. Li et al., "Label Leakage and Protection in Two-party Split Learning" (arXiv 2102.08504), Appendix A.3,
  proof of Theorem 1, eqs. (5)-(11): TPR_r(t) - FPR_r(t) <= TV, then AUC(r) <= integral of min(FPR_r(t) + sqrt(eps)/2, 1) dFPR,
  evaluated to 1/2 + sqrt(eps)/2 - eps/8. With v = sqrt(eps)/2 this is exactly 1/2 + v - v^2/2. (Read from a converted PDF with
  garbled typesetting; the venue was not verified; cite the arXiv ID until citation-validator confirms it.)
- The lower limit 1/2 + v/2 for the LR score (a concave ROC through the Youden point) and "Youden index = KS distance" are textbook
  (a Pepe 2003, p. 80 attribution was seen only as a snippet, E1).
- Reid and Williamson (JMLR 2011), section 6.1, give AUC as a variational divergence between product measures (Torgersen). I
  found no AUC-TV inequality there (E1).
- The sharpness example and the per-item statement of (e) were not found in these three sources. Both are elementary.
**Novelty status: Prop. 1(a)-(d) is a known result restated. Calling it new, or giving it a "Proposition" number without a
citation, is a novelty defect.** The only candidates for non-trivial content are Corollary 1.1(iii) as corrected in M2 and the
fusion framing of Cor. 1.2(ii). Neither was searched.

### 2.5 Minor findings on Prop. 1
- **m3** Cor. 1.1(i)-(ii): "the corrupted value is drawn from p_theta(. | O_j)" is not well defined when several tokens are hit at
  once. A parallel draw conditions on the *clean* context, but the score sees a context that contains the other new values.
  The statement holds for one hit per item or for sequential (Gibbs) updates, which is case (e). Also, pi_0 at a corrupted
  context is the clean-value law *given that context*, not P_a's conditional, so "Bayes-optimal model p_theta = pi_0" is not "a
  model trained on clean data" unless the context is clean.
- **m4** "On-manifold" conflates support with law. (A2) is preservation of the law. A corruption to another in-support value with a
  different frequency stays on the support and is detectable. Use "law-preserving" (Cor. 1.2(i), section 1.7, Remark 1.6).
- **m5** Section 0 defines O_j for B_j as the context outside the token's group, while 1.1 says "any score that a network computes
  from the own modality" is in F_a. That is true only if O_j is the full own-modality context, which gives a larger, still valid v.
  Scores that use other tokens of the same group are outside the class as defined.

---

## 3. Proposition 2: detailed attack

### 3.1 Independent re-derivation
I re-derived Lemma 1 by hand: Var(I Delta) = k sigma_z^2 + k phi mu_z^2, and Cov(I_j Delta_j, I_k Delta_k) = k_j k_k Cov(Delta_j, Delta_k)
under (M4). With sympy (R3) I confirmed:
- (k_0^2 V_0 - V_g)/m minus [LHS - RHS of (2.5)] = 0 identically;
- E_g = k_0 E_0 at mu_c = 0;
- the conditional-on-flags variant of Remark 2.4 has residual 0.
At zero correlation, (2.5) equals method.tex Eq. (snr) term by term. theory.py's `special_case_inequality` is the same inequality,
and B2 confirms the numeric agreement. The positive semi-definiteness condition on gamma_01 is correct: it is the determinant of
the 2x2 matrix of block means.

### 3.2 Direction of the frontier (c)
The derivatives are correct. Consequences 1-3 are correct as stated, because they assume gamma_1, gamma_01 >= 0 and rho m >= 1.
"A random gate still hurts whatever the correlation" is correct for any sign, because every correlation term vanishes at
phi_1 = phi_0. The explicit boundary b(phi_0) is the right root for both signs of G, and its G -> 0 and G -> infinity limits are
correct. The monotonicity argument d/d(phi_1) = rho sigma_c^2[1 + G(2 - 2 phi_1)] > 0 holds only for G >= -1/(2(1 - phi_1)). The
root formula does not need it.
- **m1 (WRONG sentence).** The YAML claim and (c) say that negative correlation "moves it away", which implies that helping stays
  above the diagonal. Negative gamma_01 opens a helping region **below** the diagonal. R4 uses m_0 = 900, m_1 = 100,
  gamma_0 = gamma_1 = 0.05, gamma_01 = -0.045 (PSD, minimum eigenvalue 0.95), mu = 0.1, mu_c = 0 and sigma^2 = sigma_c^2 = 1. A gate
  (phi_0, phi_1) = (0.3, 0.0), which removes only clean tokens, raises the SNR from 0.4892 to 0.5080. Negative gamma_1 cannot do this:
  G >= -1, and the bracket stays <= 0 below the diagonal.

### 3.3 Large-m limit (d)
- **m2.** The text says "the stationarity equation of g is linear in r, so g has one maximiser". In fact g has two critical points
  (sympy): r = -mu/mu_c, the zero of the numerator and the global minimum g = 0, and r*. r* is the maximiser over directions
  (1, r) only if AC > B^2 and mu C != mu_c B. Whether r* is feasible (r* >= 0, reachable by some gate) is not addressed. The
  "Fisher weights" reading is right when [[A, B], [B, C]] is positive definite.

### 3.4 M5 (major): SNR is not accuracy once tokens are exchangeably correlated
Under independence the CLT links the SNR to P(S > 0). With gamma > 0, S/m converges to a random limit, which is the shared
component. P(S > 0) then depends on the law of that component, not on its variance alone. **Counterexample (R5).** Corrupted
tokens share a rare large factor (zero with probability 0.98, +/-L otherwise), so gamma_1 = 0.074; gamma_0 = gamma_01 = 0; mu = 0.05;
mu_c = 0; m_0 = 900, m_1 = 100. The gate (0.1, 0.5) raises the SNR from 1.081 to 1.254 (Phi(SNR) from 0.860 to 0.895), while the
Monte Carlo accuracy **falls from 0.9148 to 0.9094** (400,000 items per arm; s.e. about 0.0008 each). E-pred compares the sign of
the SNR change with the sign of the accuracy change, so Prop. 2 cannot carry any accuracy statement unless the shared components
are jointly Gaussian.
With Gaussian shared factors, the exact accuracy (summed over binomial retained counts, R6) agrees in sign and to 4 decimals with
Phi(SNR_uncond) on all five rows of the addendum's accuracy table. The addendum's Monte Carlo table cannot resolve these
differences: its row (0.2, 0.9) shows accuracy below "none" (0.6648 vs 0.6654), while the exact change is +0.00094. The note's
"within one s.e. of one cell" uses the wrong s.e. for a common-random-numbers difference, though the conclusion (no
interpretation) stands.

### 3.5 M8 (major): Prop. 2 shows the frozen E-pred model is fragile, and invites a post hoc rescue
The addendum's own illustrative table (m = 1024, rho = 0.1) moves the boundary at phi_0 = 0.05 from 0.529 (gamma_1 = 0) to 0.467
(gamma_1 = 0.001) and to 0.224 (gamma_1 = 0.01). Correlations of order 1/(rho m), which nobody estimates, can flip the
independent-token sign that E-pred commits. This is legitimate theory, but it is the exact explanation a writer will reach for if
E-pred disagrees. SAP AB.1.3 and AB.3.4 bind: "explains" is banned, and the refutation rule of spec 5.3 stands. Any sentence that
attributes an E-pred disagreement to correlation, or any gamma estimated on M4 arrays to "correct" E-pred, is a post hoc rescue
and a forking path. The illustrative values (m = 1024, rho = 0.1, gamma grid) also break the project rule that no number appears
in a document unless it is in `runs/<exp-id>/`. The script lives under `research/`, not `runs/`.

### 3.6 M4 (major): Remark 2.6 does not answer A8
Sherman-Morrison is correct: Sigma^{-1} 1 is proportional to 1 (B6 checks only this). But Chair-Varshney optimality means that
the sum of local LLRs **equals the global LLR** log p(v | c+) - log p(v | c-), which needs the raw observations to be conditionally
independent. Under dependence the global LLR is not sum_j Delta_j, whatever Sigma is. Remark 2.6 proves something else: that
1'Delta is the optimal (Fisher/NP) **function of the Delta vector** when Delta is treated as the data. **Exact conditions for that
weaker statement:**
1. Delta is jointly Gaussian under each hypothesis.
2. The mean vector is proportional to 1. This fails with position-dependent per-token means. It also fails whenever rho > 0 with
   mu_c != mu and unknown labels, since Delta is then a non-Gaussian mixture.
3. The covariance is identical under both caption hypotheses. Antisymmetry Delta -> -Delta under a caption swap gives this only
   if the pair law is symmetric under the swap.
4. The covariance is fully exchangeable. A block-exchangeable Sigma (gamma_0, gamma_1, gamma_01 not all equal, rho > 0) does not
   have Sigma^{-1} 1 proportional to 1.
5. The threshold 0 is the equal-prior Bayes threshold for the means +/- theta 1.
Even then, the statement is optimality within a data reduction, not NP optimality of the test on the image. The section title
"Chair-Varshney under exchangeable dependence" and "answers plan review A8 in part" overstate it.

### 3.7 Other notes on Prop. 2
(M4) is violated by construction in GATE. The flags come from u_j = D_j - B_j, a function of the same token value as Delta_j, so
I_j and Delta_j are dependent within a class. The addendum acknowledges this (2.5; SAP AB.2 composition). It means the "robust
direction content" (concern 4) is robust only inside (M4). The B3 sampler calls its draws "valid", but gamma_0 can be drawn as low
as -25/(m_0 - 1), which is not PSD. This is harmless for an algebraic identity, but the word is wrong.

---

## 4. Proposition 3 and the SOFT-A clean-pair cost
- Lemma 2: correct. Independence of the weights across classes is needed as well as within a class.
- (a): the matched filter and the non-negative form are correct. **m6 (WRONG sentence).** "A hard gate is optimal only when
  pi_1(u) is in {0,1} (an oracle)" is false. If pi_1(u) takes the values {0.3, 1}, the optimal weights are (0.1388, 0) (R7), which
  is a 0/1 gate up to scale, with no oracle. Correct statement: a hard gate is optimal iff mu(u)_+/sigma^2(u) takes at most one
  non-zero value on the support.
- (b): the KKT derivation, the fixed point, uniqueness and the monotonicity of xi in gamma and in the token count are all correct.
  "xi = 0 iff gamma = 0" also needs some mu(u_k) > 0; if all mu(u_k) <= 0, then xi = 0 for every gamma. The "gated soft weight"
  is caused by the w >= 0 constraint. The unconstrained optimum (c) has no cut, so the reading is "correlation plus
  non-negativity induces a cut", not "correlation favours gating". Assumption (W3) forces gamma_0 = gamma_1 = gamma_01, which is
  exactly the case Prop. 2 shows to be uninformative (the frontier depends on gamma_1 and gamma_01, not gamma_0). So Props. 2 and 3
  are not jointly applicable.
- Cor. 3.1: the formula and nu = 2(2N+3)/(3(N+2)) are correct (verified by hand), and the SOFT-A definition matches A4 lines
  218-222. **m7.** (i) The 3/4 is an **SNR^2** ratio (SNR ratio 0.866). (ii) It assumes (W1), u independent of Delta, and weights
  i.i.d. uniform *within the item*. Within an item, u is clustered (item-level shifts in suspicion), so a given clean item's
  weights are not spread over the grid, and the realised nu per item differs from the pool value. The per-item cost can be smaller
  or larger. So 3/4 is not "SOFT-A's expected clean-cell cost", and comparing it with the M4 clean cell would be a post hoc
  confirmation (AB.1 spirit; A4.4 item 2).

---

## 5. The script: does it test the claims?
It runs and reproduces exactly. Non-tautological checks: A1 (random laws and scores), A3/A5 Monte Carlo on a toy with a positive
control, the A4 Monte Carlo against exact enumeration, B1 and C1 (Monte Carlo of Lemmas 1 and 2), B2 (against the pinned
theory.py), and C2 (L-BFGS-B against the fixed point). **m8, the weak, vacuous or tautological checks:**
- A4 "exact TV <= bound": the bound is 1.76 and TV <= 1 always, so the check cannot fail.
- C2 "gamma = 0 matched filter attains the optimum" compares mvec/s2u with Sigma^{-1} mvec for a diagonal Sigma. These are the same
  vector.
- B6 checks Sherman-Morrison, not the NP claim it is cited for.
- B3/B4 "direct" SNR uses the same `mean_var_corr` as the closed form. They check the algebra from Lemma 1 to (2.5), not Lemma 1;
  Lemma 1 is checked by Monte Carlo at one parameter point only (B1).
- The B5 r* check searches only r* +/- 5 and never tests feasibility.
- The accuracy table cannot resolve the sign of differences of 0.001 (section 3.4).
- Comment and label slips: the B4 random-gate comment says gamma_1 = gamma_01 = 0, but the code uses gamma_01 = 0.01; the
  Remark 2.4 check is labelled B5.
- No check covers M1 (per-item vs pooled), M2 (context detectability), m1 (negative gamma_01) or M5 (non-Gaussian accuracy).

---

## 6. Overclaim: what the paper may and may not say

### 6.1 M6 (major, blocks manuscript use of Prop. 1): conflict with must-not-claim #6
GATE-METHOD-SPEC-v2 2.2 item 6 says: "No bound on detection power." Prop. 1(a) is literally an upper bound on the detection power
(AUROC) of every within-modality score, GATE's u included. The addendum's proposed wording, "a limit that holds for any
within-modality score", is still a bound on detection power. Because the bound is expressed through an unobservable v, it bounds
nothing the paper measures. The item-6 text does not distinguish a guarantee from an impossibility limit, so placement in Method
violates the list as written. **This blocks use until the orchestrator records a ledger decision on item 6's scope.** The
rejection condition: any manuscript sentence that states v(1 - v/2) or "AUROC = 1/2" about u without such a row.

### 6.2 M7 (major): the changed-label caveat against K2 (D0074)
Corrected as in M2, Cor. 1.1(iii) says that under the changed-code label a context-only statistic (how diffuse the token's
conditional is given its surroundings, which is texture-like) detects a perfectly law-preserving resample (AUROC about 0.68 in toys).
It also says the token's own conditional probability detects it further. Read next to the M1 table, this is a ready-made mechanism
for "the texture/pixel-variance rival beats q on JPEG and noise". K2 forbids presenting the texture win as evidence for any
mechanism, and AB.1 forbids explanation clauses. The direction of the toy effect (diffuse context means more often changed) is not
shown to match the rival's sign. The rival's membership of F_a is undecided. Neither may be argued in the paper.

### 6.3 Permitted wording (if M6 is resolved), by proposition
**Prop. 1 (Method or appendix only, cited as known):**
- Allowed: "For the pooled token AUROC against the hit indicator, any score computed from a token and its own-modality context
  satisfies |AUROC - 1/2| <= v(1 - v/2), where v is the total variation between the class laws of (token, context) [Li et al.,
  arXiv 2102.08504, App. A.3]; if the corruption preserves the law of the own modality given the context, v = 0. This is a
  property of an idealised data model; it is not evaluated for the corruptions studied here."
- Not allowed:
  - "new" or "we prove" without the citation;
  - "on-manifold";
  - any per-item AUROC statement;
  - "GATE's / q's detection is limited by";
  - "JPEG/noise damage is on-manifold";
  - "explains / is consistent with the M1 result";
  - anything in the title, abstract, highlights or conclusion;
  - any use next to the M1 rival result or a P result.

**Cor. 1.1(iii):**
- Allowed in Method or appendix only, as a property of the label: "Under the changed-code label, even a law-preserving resample is
  partly detectable, both from the token's conditional probability and from its context alone, because the label selects
  low-probability values and diffuse contexts."
- Not allowed: in Results or Discussion beside the M1 table; "label artefact accounts for"; any sentence linking it to texture,
  pixel variance or the rival.

**Cor. 1.2(ii):**
- Allowed: "A corruption that preserves the image-only law but not the image-caption law is invisible to every image-only score
  (toy example)".
- Not allowed: a claim that any studied corruption is of this type.

**Prop. 2:**
- Allowed: "Under exchangeable correlation of the per-token terms and flags independent of the evidence, the condition for
  withholding to raise the SNR of the sum becomes Eq. (2.5); positive correlation among corrupted tokens, or between clean and
  corrupted tokens, enlarges the region where withholding raises this SNR, and Eq. (snr) is the zero-correlation case. With
  correlation the SNR of the sum no longer grows like sqrt(m)."
- Required qualifiers: "SNR of the sum" (never accuracy) unless "jointly Gaussian" is stated (M5); "(M4) excludes flags that
  depend on the evidence".
- Not allowed:
  - "predicts", "explains", "accounts for" about any E-pred, P, PS or Tier-3 cell;
  - any gamma estimated from M4 data;
  - overlaying measured (phi_0, phi_1) points on the correlated frontier;
  - the illustrative numbers;
  - "UniDisc tokens are exchangeably correlated".

**Remark 2.6:**
- Allowed: "If the per-token terms were jointly Gaussian with a common mean and the same exchangeable covariance under both
  caption hypotheses, the equal-weight sum would be the optimal linear statistic of those terms; this does not make the sum the
  likelihood ratio of the image, and the sum is used as a standard statistic."
- Not allowed: "Chair-Varshney optimality survives dependence", "answers the independence objection".

**Prop. 3 / Cor. 3.1:**
- Allowed: "Under (W1)-(W3), the SNR-optimal non-negative weight is a soft weight with a cut; GM approximates the cut and SOFT-A
  the soft part; under i.i.d. uniform weights independent of the evidence, reliability weighting costs a factor 3/4 in SNR^2 on
  clean items at zero correlation."
- Not allowed: any ranking of the A4 arms; "the clean-cell cost agrees with/confirms the theory"; "optimal reliability weighting"
  for any arm; computing w* on M4 data (A4.4 item 2, as the addendum says).

**All propositions:** no causal clause on any P result (AB.1); the word "predicted" only inside the E-pred table (AB.1.4).

---

## 7. Rejection conditions (what result would force rejection of each claim)
| Claim | Rejected by |
|---|---|
| Prop. 1 as a novel result | Li et al. arXiv 2102.08504 App. A.3 (already met) |
| Prop. 1 applied to the reported detection AUROCs | the R1 counterexample (already met) for per-item; for pooled, only with a stated O and label |
| Cor. 1.1(iii) premise "(A1) holds" | R2: the context marginals differ (TV 0.27-0.29) (already met) |
| Prop. 2(b)/(c) for gamma >= 0 | a PSD parameter set violating the sympy identity; none exists (identity holds) |
| "negative correlation moves the frontier away" | R4 (already met) |
| Prop. 2 read as an accuracy statement | R5 (already met) |
| Remark 2.6 as a Chair-Varshney answer | any dependent model where 1'Delta != global LLR (all of them) |
| Prop. 3(a) "only oracle" sentence | R7 (already met) |
| Cor. 3.1 as SOFT-A's expected cost | any item-clustered u (not yet measured; must not be measured on M4 for this purpose) |

## 8. Competing explanations for the addendum's positive checks
- A3 and A5 "blind at 1/2": true by construction (law-invariant kernels on a toy whose scores are exact conditionals). They test
  the code, not the relevance of the proposition to UniDisc.
- B3's 0 mismatches in 31,434: an algebraic identity checked against itself through shared code. The independent evidence is B1
  and the symbolic check (R3).
- B4 "boundary falls toward the diagonal": guaranteed by the sign of dL/dgamma_1 under gamma >= 0. It says nothing about
  real-data gamma.
- C2 threshold rising with gamma: guaranteed by the KKT structure under w >= 0 and (W3).

## 9. Searches run (section 2.4 evidence)
1. Web search "AUC Kolmogorov-Smirnov bound ... Youden index AUC upper bound": found Youden = KS (Pepe 2003 p. 80, as quoted in
   arXiv 2003.13111), no AUC-TV constant.
2. Web search and ar5iv fetch of Reid and Williamson arXiv 0901.0356: AUC as V(P x Q, Q x P) in section 6.1, no inequality found (E1).
3. Web search "AUC bounded by total variation ...": led to arXiv 2102.08504; PDF fetched and converted; App. A.3 read (E2, garbled).
