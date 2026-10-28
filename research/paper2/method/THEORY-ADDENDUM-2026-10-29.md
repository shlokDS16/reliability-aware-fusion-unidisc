```yaml
agent: method-architect
date: 2026-10-29
brief: >
  Theory addendum for Paper 2 (GATE, UniDisc 1.4B, Information Fusion), answering red-team plan review A8 and C.2 N-a / N-b:
  (1) a detectability limit for within-modality self-consistency validation, with a quantitative two-sided AUROC-TV bound;
  (2) the gating SNR of method.tex (Eqs. mean/var/snr, lines 308-334) generalised to correlated tokens, with the soft-weight analogue.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/benchmark/REDTEAM-P2-PLAN.md (A8, lines 180-189; C.1 M-d, M-e and C.2 N-a, N-b, lines 285-299)
  - paper2/sections/method.tex (whole file, 430 lines; working tree at commit eadfa00b)
  - exp_p2/gate/theory.py (whole file; git blob 4d2b550016e4563eb3506eaf5ccfda4b6b168748; read and imported read-only, not edited)
  - research/paper2/prereg/SAP-GATE-2026-10-28.md (section 7, lines 330-349; AD.3, lines 950-975; AB.1 and AB.3, lines 1132-1154)
  - research/paper2/prereg/SAP-ADDENDUM-A4-2026-10-28.md (A4.1.4 and A4.1.5, lines 159-216; A4.4 item 2, line 585)
  - research/paper2/ideation/NOVELTY-CHECK-INFFUS-2026-10-28.md (section 4, items 10-13)
  - research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md (section 2.2, must-not-claim items 1-9 only)
  - research/ledgers/decisions.jsonl (row D0074 only)
coverage: >
  The files above, at the line ranges given. NOT read: anything under runs/P2-GATE-M4 or any M4 output, analysis_m4, epred_frozen.json,
  the M1 arrays, NOVELTY-REAUDIT section 7 (Trust but Verify is mentioned only through the red-team plan's sentence), and the
  sources of the standard results cited as "standard" below (Neyman-Pearson lemma, Pinsker's inequality, Sherman-Morrison,
  invariance of Gibbs updates); a citation check is needed before any of them is cited in the paper.
claims:
  - statement: "Prop. 1(a,b): for any score that is a function of (observed token, visible within-modality context), |AUROC - 1/2| <= v(1 - v/2), v = TV(Q_0, Q_1); the bound is attained; the best score has AUROC >= 1/2 + v/2; AUROC = 1/2 for every score iff Q_0 = Q_1."
    status: supported
    evidence: "proof in section 1.3; numerical check A1, A2 (theory_check_2026-10-29.py, output in section 5)"
    level: E0
    confidence: 0.95
  - statement: "Prop. 1(e): a corruption that applies a law-invariant kernel at a content-independent hit set with a constant hit rate gives pooled AUROC 1/2 and per-item expected AUROC 1/2 for every within-modality score, under the hit label."
    status: supported
    evidence: "proof in section 1.3; toy-model check A3 (section 5)"
    level: E0
    confidence: 0.9
  - statement: "Under the changed-code label Z of the paper, resampling from the clean conditional is NOT exactly undetectable; the excess is bounded by a collision-probability term that is small only for diffuse conditionals."
    status: supported
    evidence: "Corollary 1.1(iii); check A4 (exact TV 0.3396 below the bound in the toy; exact AUROC of the LR score 0.7202, toy values only)"
    level: E0
    confidence: 0.85
  - statement: "Prop. 2(b): with exchangeable evidence correlation and mu_c = 0, hard gating raises the SNR of S iff the design-effect-corrected inequality (2.5) holds; it reduces to method.tex Eq. (snr) at zero correlation; gamma_0 drops out."
    status: supported
    evidence: "derivation in section 2.3; checks B1-B4 (0 sign mismatches against the direct SNR comparison in 31,434 random cases; 0 mismatches against theory.special_case_inequality at zero correlation)"
    level: E0
    confidence: 0.95
  - statement: "Prop. 2(c): positive correlation among corrupted tokens (gamma_1) or between clean and corrupted tokens (gamma_01) moves the gating-helps frontier in the (phi_0, phi_1) = (alpha, beta) plane toward the diagonal phi_1 = phi_0, and never across it; negative values move it away."
    status: supported
    evidence: "section 2.3 (derivatives); check B4 (closed-form boundary equals bisection to 4e-15)"
    level: E0
    confidence: 0.9
  - statement: "Prop. 3: the SNR-optimal reliability weight is the matched filter mu(u)/sigma^2(u) for independent tokens, and a soft-thresholded weight (mu(u) - xi)_+ / d(u) with xi > 0 increasing in the correlation for non-negative weights under exchangeable correlation."
    status: supported
    evidence: "derivation in section 3.2; checks C2 (QP optimum equals the fixed-point form to 5e-16)"
    level: E0
    confidence: 0.9
  - statement: "None of the above is validated on UniDisc; none enters E-pred, P, PS or any preregistered family."
    status: supported
    evidence: "SAP AB.3 items 4-6; this file section 4"
    level: E0
    confidence: 1.0
competing_explanations: []
unknowns:
  - "The values of the correlations gamma_0, gamma_1, gamma_01 of the per-token evidence Delta_j on UniDisc are not estimated anywhere; no plan estimates them."
  - "Whether JPEG or noise codes are on-manifold (Prop. 1(d) holds for them) is not measured and is not asserted."
  - "Whether the AUROC-TV constant v(1 - v/2) is already in the literature was not searched; the paper must not call it new without a check."
next_test: {hypothesis: "none (theory addendum; no new test is proposed before M4)", intervention: "red-team review of sections 1-3", primary_metric: "n/a", falsifier: "an error in a proof or a failed check", gpu_hours: 0}
```

# Theory addendum: detectability limit of self-consistency validation, and the gating SNR with correlated tokens

**Dated 2026-10-29, 00:24 IST (file written 00:24-00:28 IST), before any M4 value has been read.** M4 is running. I did not open `runs/P2-GATE-M4/` or any file written by
M4, did not run `analysis_m4`, and did not read `epred_frozen.json`. The two propositions below were written from the files listed in the
header only. The only numbers in this file are (i) derived constants, (ii) values from toy models produced by
`research/paper2/method/theory_check_2026-10-29.py` and labelled as such, and (iii) parameter values marked ILLUSTRATIVE. No number in this file is
an estimate from UniDisc.

**Status of every statement:** theory, derived here, checked numerically on toy models (section 5), not validated on UniDisc (E0 in the
project's scale). Nothing in this file changes `exp_p2/gate/theory.py`, `epred_fit.py`, the SAP, Addendum A4, the card, the manuscript or a
ledger.

## 0. Notation

Symbols of method.tex and theory.py are kept. In particular $\rho$ is the **corrupted fraction**, and the flag probabilities are
$\phi_0,\phi_1$ in the paper ($\alpha,\beta$ in theory.py and the SAP; $\hat\phi_0,\hat\phi_1$ = `alpha_obs`, `beta_obs`). New symbols, chosen
not to collide with method.tex, the SAP or Addendum A4:

| Symbol | Meaning | Note |
|---|---|---|
| $O_j$ | visible context of token $j$ used by a score: the position $j$, the partition $\Pi_K$, the visible tokens of the own modality, the masked other modality, and any independent randomisation (jitter) | for $B_j$: $O_j=(j,\Pi_K,\tilde x^a_{-\Gamma_{k(j)}},\varnothing^b,\epsilon_j)$ |
| $Q_z$ | law of $(\tilde x_j,O_j)$ given $Z_j=z$, under the AUROC's sampling of tokens | $z\in\{0,1\}$ |
| $\vartheta$ | $\mathrm{TV}(Q_0,Q_1)=\sup_A|Q_1(A)-Q_0(A)|$ | not $t$ (caption) or $\tau$ (threshold) |
| $H$, $h$ | hit set of a corruption (positions it acts on), and $P(j\in H)$ | $Z^{\rm hit}_j=\ind[j\in H]$ differs from the paper's $Z_j=\ind[\tilde v_j\ne v^\circ_j]$ |
| $\pi_0(\cdot\mid o)$ | law of the clean value of a token given its context $O_j=o$ | the "clean conditional" |
| $\bar s$ | $\E_O\sum_y\pi_0(y\mid O)^2$, mean collision probability of the clean conditional | |
| $\gamma_0,\gamma_1,\gamma_{01}$ | exchangeable correlation of $\Delta_j,\Delta_k$ ($j\ne k$) for two clean tokens, two corrupted tokens, one of each | the brief's $\rho_{\rm in}$ is $\gamma_0=\gamma_1$; renamed because $\rho$ is the corrupted fraction |
| $m_0,m_1$; $k_0,k_1$ | $(1-\rho)m$ and $\rho m$; keep probabilities $1-\phi_0$, $1-\phi_1$ | |
| $\chi$ | $\rho\sigma_c^2/\{(1-\rho)(\sigma^2+\mu^2)\}$ | the red team's $\kappa$ (plan M-d); renamed because $\kappa$ is the hybrid re-infill threshold in method.tex line 355 |
| $w_j$, $\bar w_z$, $\overline{w^2}_z$ | non-negative token weight, its class mean and class second moment | not $\omega$, which is the LDA weight of Eq. (lda) |
| $\pi_1(u)$, $\mu(u)$, $\sigma^2(u)$ | $P(Z_j=1\mid u_j=u)$; $\E[\Delta_j\mid u_j=u]$; $\Var(\Delta_j\mid u_j=u)$ | |
| $\xi$ | threshold of the optimal non-negative weight (Prop. 3(b)) | |

AUROC of a score $f$ is $\mathrm{AUROC}(f)=P\{f(X_1)>f(X_0)\}+\tfrac12P\{f(X_1)=f(X_0)\}$ with $X_1\sim Q_1$, $X_0\sim Q_0$ independent; this is the
mid-rank AUROC of SAP section 7 in the population.

---

## 1. Proposition 1: detectability limit of self-consistency validation

### 1.1 Setting

Fix the scored modality $a$. An evaluation population of tokens is drawn: an item, then a position $j$ in it, by any rule that does not look at
the scores (pooled token AUROC draws all positions of all items; per-item AUROC is treated in (e)). For the drawn token we observe
$\tilde x_j$ and the context $O_j$ (section 0), and the label $Z_j$. The **within-modality score class** $\mathcal F_a$ is the set of measurable
functions $f(\tilde x_j,O_j)$. Under the evidence-separation rule (method.tex lines 110-119) the gate's statistic $u_j=-(B_j-D_j)$, plain $B$, the
position marginal $D$, and any score that a network computes from the own modality with the other masked, belong to $\mathcal F_a$. A score
that uses pixels, the other modality, or a different model's view of information outside $(\tilde x_j,O_j)$ does not.

### 1.2 Statement

**Proposition 1.** Let $Q_0,Q_1$ and $\vartheta=\mathrm{TV}(Q_0,Q_1)$ be as above.

(a) *Upper limit.* For every $f\in\mathcal F_a$, $\;\big|\mathrm{AUROC}(f)-\tfrac12\big|\le\vartheta\big(1-\tfrac{\vartheta}{2}\big)$. The constant is
sharp: for every $\vartheta\in[0,1]$ there are $Q_0,Q_1$ at total variation $\vartheta$ and a score attaining it.

(b) *Lower limit for the best score, and characterisation.* $\sup_{f\in\mathcal F_a}\mathrm{AUROC}(f)\ge\tfrac12+\tfrac{\vartheta}{2}$. Hence every
$f\in\mathcal F_a$ has AUROC $\tfrac12$ **if and only if** $Q_0=Q_1$.

(c) *Optimal score.* The supremum in (b) is attained by the likelihood ratio $\Lambda=dQ_1/dQ_0$ (with ties broken by mid-ranks). If
**(A1)** the law of $O_j$ does not depend on $Z_j$, and the corrupted value has conditional law $k(\cdot\mid o)$ given $O_j=o$, then
$\log\Lambda=\log k(\tilde x_j\mid O_j)-\log\pi_0(\tilde x_j\mid O_j)$.

(d) *On-manifold corruption is invisible.* If (A1) holds and **(A2)** $k(\cdot\mid o)=\pi_0(\cdot\mid o)$ for almost every $o$ (the corrupted value is
distributed as the clean value given the visible context), then $Q_0=Q_1$ and every $f\in\mathcal F_a$ has AUROC $\tfrac12$.

(e) *A constructive sufficient condition, pooled and per item.* Let the clean items have law $P_a$ (law of modality $a$). Suppose
**(C1)** the hit set $H$ is independent of the clean item and of the score's randomisation, and $P(j\in H)=h$ is the same for every position
of every item; **(C2)** for every fixed $H$ the corruption is a Markov kernel $K_H$ on the item that leaves $P_a$ invariant
($X^\circ\sim P_a\Rightarrow\tilde X\sim P_a$). Then, with the hit label $Z^{\rm hit}$: the pooled AUROC of every $f\in\mathcal F_a$ is $\tfrac12$; and
if in addition the law of $H$ given $|H|$ is uniform over subsets of that size, the expected per-item AUROC of every $f\in\mathcal F_a$, over
items with $0<|H|<m$, is $\tfrac12$. Examples of (C2): sequential Gibbs updates of the positions in $H$ from the full conditionals of $P_a$;
a block redraw of $x_H$ from $P_a(x_H\mid x_{-H})$; replacing the whole item by an independent draw from $P_a$.

### 1.3 Proof

*(a)* Write $\nu=\min(Q_0,Q_1)$, which has mass $1-\vartheta$. Then $Q_z=(1-\vartheta)C+\vartheta A_z$ with $C=\nu/(1-\vartheta)$ and
$A_z=(Q_z-\nu)/\vartheta$ probability measures, $A_0$ and $A_1$ mutually singular (if $\vartheta\in\{0,1\}$ the argument degenerates and the
claim is immediate). The pushforward of a mixture by $f$ is the mixture of the pushforwards, and $\mathrm{AUROC}(P,Q)$, viewed as a function of
the two score laws, is bilinear. So
$$\mathrm{AUROC}(f)=(1-\vartheta)^2\,\mathrm{AU}(C,C)+(1-\vartheta)\vartheta\,[\mathrm{AU}(C,A_0)+\mathrm{AU}(A_1,C)]+\vartheta^2\,\mathrm{AU}(A_1,A_0),$$
where $\mathrm{AU}(P,Q)$ is the AUROC with positives from $P$ and negatives from $Q$. For identical laws, $P\{f(X)>f(X')\}=P\{f(X')>f(X)\}$, so
$\mathrm{AU}(C,C)=\tfrac12$; every other term is at most 1. Hence
$\mathrm{AUROC}(f)\le\tfrac12(1-\vartheta)^2+2\vartheta(1-\vartheta)+\vartheta^2=\tfrac12+\vartheta-\tfrac{\vartheta^2}{2}$.
Applying this to $-f$ and using $\mathrm{AUROC}(-f)=1-\mathrm{AUROC}(f)$ gives the lower side. *Sharpness:* on $\{0,1,2\}$ take
$Q_1=(0,1-\vartheta,\vartheta)$, $Q_0=(\vartheta,1-\vartheta,0)$, $f=\mathrm{id}$; then $\mathrm{TV}=\vartheta$ and
$\mathrm{AUROC}=1-(1-\vartheta)^2+\tfrac12(1-\vartheta)^2=\tfrac12+\vartheta-\tfrac{\vartheta^2}{2}$.

*(b)* Let $A=\{dQ_1>dQ_0\}$ (densities with respect to $Q_0+Q_1$), so $Q_1(A)-Q_0(A)=\vartheta$. For the indicator score $f=\ind_A$,
$\mathrm{AUROC}=Q_1(A)(1-Q_0(A))+\tfrac12[Q_1(A)Q_0(A)+(1-Q_1(A))(1-Q_0(A))]=\tfrac12+\tfrac12[Q_1(A)-Q_0(A)]=\tfrac12+\tfrac{\vartheta}{2}$.
If $Q_0=Q_1$ every score has identical laws in both classes and AUROC $\tfrac12$ (as for $\mathrm{AU}(C,C)$); if $Q_0\ne Q_1$ then $\vartheta>0$ and
$\ind_A$ has AUROC $>\tfrac12$.

*(c)* By the Neyman-Pearson lemma (standard; to be cited) the test that thresholds $\Lambda$, randomised at ties, has the largest true-positive
rate at every false-positive rate, so its ROC curve lies above that of any $f$ and its area is the largest. Under (A1) both classes share the
law $\mu_O$ of $O_j$, so $dQ_z(x,o)=\mu_O(do)\,k_z(x\mid o)$ with $k_0=\pi_0$, $k_1=k$, which gives the stated ratio.

*(d)* Under (A1)-(A2), $dQ_1=\mu_O\,k=\mu_O\,\pi_0=dQ_0$; apply (b).

*(e)* *Pooled.* By (C1) and (C2), for every fixed $H$ the observed item $\tilde X$ has law $P_a$, so $\tilde X$ is independent of $H$. Hence for
each position $j$, the law $L_j$ of $(\tilde x_j,O_j)$ is the same given $j\in H$ and given $j\notin H$ (the partition and jitter in $O_j$ are
independent of everything by (C1)). The pooled class laws are $Q_1=\sum_j h\,L_j/\sum_j h$ and $Q_0=\sum_j(1-h)L_j/\sum_j(1-h)$, both equal to
the uniform mixture of the $L_j$ because $h$ does not depend on $j$. Apply (b). (If $h$ depended on $j$, the position, which is part of $O_j$,
would itself be a detector.)
*Per item.* Given $\tilde X$, the scores $f_1,\dots,f_m$ are fixed (up to independent randomisation) and, by the independence just shown, $H$
given $|H|=n_1$ is uniform over subsets of size $n_1$. With $n_0=m-n_1$ and $g(a,b)=\ind[a>b]+\tfrac12\ind[a=b]$,
$\E[\mathrm{AUROC}_{\rm item}\mid\tilde X,n_1]=\frac1{n_1n_0}\sum_{j\ne k}P(j\in H,k\notin H)\,g(f_j,f_k)=\frac{1}{n_1n_0}\cdot\frac{n_1n_0}{m(m-1)}\cdot\frac{m(m-1)}2=\tfrac12$,
because $g(f_j,f_k)+g(f_k,f_j)=1$ for each unordered pair. $\square$

### 1.4 Corollary 1.1 (corruption drawn from the model's own conditional)

Let $p_\theta(\cdot\mid o)$ be the network's conditional at context $o$ (for $B_j$: own modality partly visible, other modality masked).

(i) *Bayes-optimal model.* If $p_\theta(\cdot\mid o)=\pi_0(\cdot\mid o)$ and the corrupted value is drawn from $p_\theta(\cdot\mid O_j)$ with (A1),
then (d) applies: with the hit label every within-modality score, $u$ included, has AUROC $\tfrac12$. This is the precise form of the red team's
N-a sentence. It needs (A1), which fails when corrupted tokens cluster, because then a corrupted token's context contains more corrupted
neighbours than a clean token's, and the context alone can be informative.

(ii) *Real model.* If the corrupted value is drawn from $p_\theta(\cdot\mid O_j)$ and (A1) holds, then $\vartheta=\E_O\,\mathrm{TV}\big(p_\theta(\cdot\mid O),\pi_0(\cdot\mid O)\big)\le\sqrt{\tfrac12\E_O\mathrm{KL}(\pi_0\|p_\theta)}$
(Jensen and Pinsker), so by (a) no within-modality score, including the model's own, separates such corruption from clean tokens by more
than $\vartheta(1-\vartheta/2)$: the advantage is bounded by the model's misfit to the clean conditional.

(iii) *The paper's changed-code label.* The paper labels $Z_j=\ind[\tilde v_j\ne v^\circ_j]$, not the hit indicator. Suppose $Z^{\rm hit}$ is
independent of the clean item with rate $h$, (A1) holds for the full context $O_j=\tilde x_{-j}$, and for a hit token the clean and the new
value are independent draws from $\pi_0(\cdot\mid O_j)$ (exact for one hit per item, $h=1/m$, by Gibbs invariance). Then, writing
$\pi=\pi_0(\cdot\mid o)$, the changed tokens have conditional law $\pi(1-\pi)/(1-s(o))$ and the unchanged ones a mixture of $\pi$ and
$\pi^2/s(o)$, $s(o)=\sum_y\pi(y)^2$. Averaging over $o$ and using the triangle inequality through the reference law $\mu_O\pi$:
$$\vartheta\;\le\;\frac{\bar s}{1-\bar s}+\frac{h\,\bar s}{1-h+h\,\bar s}.$$
(Proof: $\mathrm{TV}(Q_1,\mu_O\pi)=\tfrac12\E_O\sum_y\pi|\pi-\bar s|/(1-\bar s)\le\bar s/(1-\bar s)$ and
$\mathrm{TV}(Q_0,\mu_O\pi)=\tfrac12h\,\E_O\sum_y\pi|\pi-\bar s|/(1-h+h\bar s)\le h\bar s/(1-h+h\bar s)$, using $\sum_y\pi|\pi-\bar s|\le s(o)+\bar s$.)
For coarser contexts (such as $\tilde x^a_{-\Gamma}$) the same bound holds by the data-processing inequality. The likelihood ratio is
decreasing in $\pi_0(\tilde x_j\mid O_j)$: **under the changed-code label, a perfectly on-manifold resample is partly detectable, because the
label selects low-probability values** (a resample that lands on the clean value is labelled clean). The bound is informative only when the
clean conditionals are diffuse ($\bar s$ small); in the toy of check A4, with $\bar s=0.6272$, it is vacuous (1.76) while the exact
$\vartheta$ is 0.3396 and the exact AUROC of the likelihood-ratio score is 0.7202 (toy values, not UniDisc). Whether UniDisc's image conditionals
are diffuse is not measured here.

### 1.5 Corollary 1.2 (within-modality validation sees only off-manifold damage)

(i) *Necessary shift.* If some $f\in\mathcal F_a$ has population AUROC $a^\ast\ne\tfrac12$, then by (a)
$\vartheta\ge1-\sqrt{1-2|a^\ast-\tfrac12|}$; and by (b) the best score has AUROC between $\tfrac12+\vartheta/2$ and $\tfrac12+\vartheta-\vartheta^2/2$.
So a within-modality validator can only see a corruption to the extent that it moves the joint law of (token, own-modality context) away from
the clean law; a corruption that keeps that law (on the manifold of the own modality) is invisible to all of them, the gate's $u$ included.

(ii) *Cross-modal blind spot.* Let $P_{ab}$ be the joint law of the two modalities and $P_a$ its marginal. If a corruption satisfies (C1) and
(C2) for $P_a$ but not for $P_{ab}$ (for example, a redraw of image tokens from the image-only conditional $P_a(v_H\mid v_{-H})$, which ignores the
caption), then every within-modality score has AUROC $\tfrac12$ while the cross-modal relation can be destroyed: in the item-level toy of
check A5, the mean per-token cross-modal evidence (true minus wrong caption, image fully masked, the analogue of $\Delta_j$) is $+0.0986$ on
clean items and $-0.0006$ on redrawn items, while within-modality scores stay at AUROC $\tfrac12$ and a caption-using score does not (toy
values). This is the price of the evidence-separation rule: the rule forbids exactly the information (the other modality) that would reveal
damage which is plausible inside the own modality. The rule is kept for the reason method.tex gives (lines 110-113); the corollary states what
it costs.

### 1.6 Remarks

- **Consistency with method.tex lines 120-122.** By (c), with (A1) and a Bayes model the optimal suspicion is
  $\log k(\tilde x_j\mid O_j)-B_j$. For $k$ = the position marginal this is $D_j-B_j=u_j$; for $k$ uniform it is $-B_j$ up to a constant; for
  $k=\pi_0$ it is constant (Prop. 1(d)). The two idealised cases stated in method.tex are the first two instances of one formula.
- **Re-infilling.** An exact draw from $p(v_G\mid v_R)$ at a set $G$ chosen independently of the content would be invisible to every
  within-modality score by (e). GATE-I's set $G$ is chosen from the observed values, so (C1) fails and (e) says nothing about it. No statement
  about GATE-I follows.
- **Prior statements.** The red-team plan (C.2 N-a) links this to the Trust-but-Verify observation that plausible corruptions are barely
  detectable, as summarised in NOVELTY-REAUDIT section 7; I did not re-read that source (E1). Whether the constant $\vartheta(1-\vartheta/2)$
  appears in the AUROC literature was not searched.

### 1.7 What Proposition 1 does NOT license

1. **No claim that JPEG or noise codes are on-manifold.** Prop. 1(d) is a statement about an idealised corruption law. Whether the JPEG or noise
   corruptions of the protocol satisfy (A1)-(A2), or (C1)-(C2), was not measured. The low M1 detection AUROCs of $q$ on JPEG and noise
   (quoted in method.tex lines 126-129 from run `runs/P2-GATE-M1/`) are consistent with several explanations that this proposition does not
   separate: on-manifold damage, off-manifold damage that the score family expresses poorly, the changed-code label (Corollary 1.1(iii)), label
   instability of the tokenizer (red-team label-circularity concern), or model misfit. The paper must not write "JPEG damage is on-manifold" or
   "Prop. 1 explains the M1 detection result".
2. **No explanation of any P result (SAP AB.1).** No P result, null or positive, may be called predicted, explained or caused by
   detectability, in any text. Prop. 1 may not appear in the title, abstract, highlights or conclusion as an account of P.
3. **K2 wording binds (decisions ledger D0074).** No sentence may say or imply that $q$ detects corrupted codes better than cheap methods, or
   that the rival's advantage on JPEG and noise is explained by Prop. 1. The M1 rival (a sign-flipped pixel-variance statistic, D0074) may not
   be a member of $\mathcal F_a$ at all, since it may use information outside $(\tilde x_j,O_j)$; this file does not decide whether it is. The
   texture result stays worded as the label-circularity concern, not as evidence for any mechanism.
4. **Not a guarantee and not a power bound for GATE.** Prop. 1 is an impossibility statement (an upper limit) about an idealised data model. It
   gives no lower bound on GATE's detection power and does not extend the only guarantee the paper states (method.tex Prop. 1, CRC). Must-not-claim
   item 6 ("no bound on detection power") is respected only if the paper words Prop. 1 as "a limit that holds for any within-modality score
   under stated conditions", never as a property GATE has been shown to have. See concern 2 in the reply.
5. **No novelty claim** for the characterisation in (b) or the construction in (e), which are elementary; the possible contribution is the
   framing for fusion (Corollary 1.2(ii)) and the changed-label caveat (Corollary 1.1(iii)), and both need a literature check.

---

## 2. Proposition 2: the gating SNR with correlated tokens

### 2.1 Model and assumptions (each is used where marked)

The statistic is $S=\sum_{j=1}^mI_j\Delta_j$ as in method.tex Eq. (mean)-(var). Assumptions:

- **(M1) Fixed class counts.** Conditional on the labels, $m_0=(1-\rho)m$ tokens are clean and $m_1=\rho m$ are corrupted. (method.tex's formula
  has no between-class mixing term, so it is also conditional on the labels.)
- **(M2) Class moments.** Clean $\Delta_j$: mean $\mu$, variance $\sigma^2$; corrupted: $\mu_c$, $\sigma_c^2$ (as in method.tex).
- **(M3) Exchangeable correlation.** For $j\ne k$: $\mathrm{Corr}(\Delta_j,\Delta_k)=\gamma_0$ (both clean), $\gamma_1$ (both corrupted),
  $\gamma_{01}$ (one of each). Positive semi-definiteness requires $\gamma_0\ge-1/(m_0-1)$, $\gamma_1\ge-1/(m_1-1)$,
  $\gamma_0,\gamma_1\le1$, and $\gamma_{01}^2\,m_0m_1\le\{1+(m_0-1)\gamma_0\}\{1+(m_1-1)\gamma_1\}$.
- **(M4) Flags.** $I_j\sim\mathrm{Bernoulli}(k_z)$ in class $z$, independent of all $\Delta$ and of each other (exactly method.tex's implicit
  assumption: its $\Var(I_j\Delta_j)=(1-\phi)\sigma^2+\phi(1-\phi)\mu^2$ holds only if $I_j\perp\Delta_j$).
- **(M5) Sign.** $\E S>0$ before and after gating, so a larger $\E S/\sqrt{\Var S}$ means a larger SNR (as in method.tex).

### 2.2 Lemma 1 (mean and variance)

Under (M1)-(M4), with $k_z=1-\phi_z$,
$$\E S=m_0k_0\mu+m_1k_1\mu_c,\tag{2.1}$$
$$\begin{aligned}\Var S={}&m_0k_0(\sigma^2+\phi_0\mu^2)+m_1k_1(\sigma_c^2+\phi_1\mu_c^2)\\&+m_0(m_0-1)k_0^2\gamma_0\sigma^2+m_1(m_1-1)k_1^2\gamma_1\sigma_c^2+2m_0m_1k_0k_1\gamma_{01}\sigma\sigma_c.\end{aligned}\tag{2.2}$$
*Proof.* $\Var(I_j\Delta_j)=k(\sigma^2+\mu_z^2)-k^2\mu_z^2=k\sigma_z^2+k\phi\mu_z^2$. For $j\ne k$, by (M4)
$\mathrm{Cov}(I_j\Delta_j,I_k\Delta_k)=\E I_j\,\E I_k\,\E[\Delta_j\Delta_k]-\E I_j\,\E I_k\,\E\Delta_j\,\E\Delta_k=k_{z_j}k_{z_k}\mathrm{Cov}(\Delta_j,\Delta_k)$; count
$m_0(m_0-1)$, $m_1(m_1-1)$ and $2m_0m_1$ ordered pairs. $\square$
At $\gamma_0=\gamma_1=\gamma_{01}=0$ (2.1)-(2.2) are method.tex Eqs. (mean)-(var) term by term (check B2: maximum relative difference from
`theory.mean_var` $1.2\times10^{-13}$). No gate is $\phi_0=\phi_1=0$:
$\Var S_0=m_0\sigma^2\{1+(m_0-1)\gamma_0\}+m_1\sigma_c^2\{1+(m_1-1)\gamma_1\}+2m_0m_1\gamma_{01}\sigma\sigma_c$, which shows the design effects
$1+(m_z-1)\gamma_z$.

### 2.3 Proposition 2 (when hard gating raises the SNR)

Under (M1)-(M5), write $E_g,V_g$ for (2.1)-(2.2) at $(\phi_0,\phi_1)$ and $E_0,V_0$ at $(0,0)$.

(a) *General condition.* Gating raises the SNR iff $E_g^2V_0>E_0^2V_g$. (Immediate from (M5).)

(b) *Closed form for $\mu_c=0$.* Then $E_g=k_0E_0$, and the condition $k_0^2V_0>V_g$ is, after division by $m$,
$$\rho\,\sigma_c^2\Big[(\phi_1-2\phi_0+\phi_0^2)+(\rho m-1)\,\gamma_1\,(\phi_1-\phi_0)(2-\phi_0-\phi_1)\Big]+2\rho(1-\rho)\,m\,\gamma_{01}\,\sigma\sigma_c\,(1-\phi_0)(\phi_1-\phi_0)\;>\;(1-\rho)\,\phi_0(1-\phi_0)\,(\sigma^2+\mu^2).\tag{2.5}$$
$\gamma_0$ does not appear. At $\gamma_1=\gamma_{01}=0$, (2.5) is method.tex Eq. (snr) exactly.

*Proof.* Subtract (2.2) from $k_0^2V_0$ class by class. Clean terms: $k_0^2m_0\sigma^2\{1+(m_0-1)\gamma_0\}-m_0k_0(\sigma^2+\phi_0\mu^2)-m_0(m_0-1)k_0^2\gamma_0\sigma^2=-m_0k_0\phi_0(\sigma^2+\mu^2)$
(the $\gamma_0$ terms cancel because gating scales both the clean mean and the clean pairwise covariance by $k_0$ and $k_0^2$). Corrupted terms:
$m_1\sigma_c^2[(k_0^2-k_1)+(m_1-1)\gamma_1(k_0^2-k_1^2)]$ with $k_0^2-k_1=\phi_1-2\phi_0+\phi_0^2$ and
$k_0^2-k_1^2=(\phi_1-\phi_0)(2-\phi_0-\phi_1)$. Cross terms: $2m_0m_1\gamma_{01}\sigma\sigma_ck_0(k_0-k_1)$ with $k_0-k_1=\phi_1-\phi_0$. Divide by $m$
and use $m_0=(1-\rho)m$, $m_1=\rho m$. $\square$
Check B3: the sign of (2.5) agreed with the sign of the direct SNR change in all 31,434 random valid parameter draws (0 mismatches); check B2:
at zero correlation it agreed with `theory.special_case_inequality` in all 20,000 draws.

(c) *The frontier and the direction in which correlation moves it.* Let $L(\phi_0,\phi_1)$ be the left minus the right side of (2.5). Then
$\partial L/\partial\gamma_1=\rho\sigma_c^2(\rho m-1)(\phi_1-\phi_0)(2-\phi_0-\phi_1)$ and
$\partial L/\partial\gamma_{01}=2\rho(1-\rho)m\sigma\sigma_c(1-\phi_0)(\phi_1-\phi_0)$, both with the sign of $\phi_1-\phi_0$, and
$\partial L/\partial\gamma_0=0$. Consequences:

1. Above the diagonal ($\phi_1>\phi_0$), raising $\gamma_1$ or $\gamma_{01}$ can only turn "gating lowers the SNR" into "gating raises it",
   never the reverse; lowering them (negative correlation) does the opposite. Clean-clean correlation has no effect when $\mu_c=0$.
2. With $\gamma_1,\gamma_{01}\ge0$, gating at or below the diagonal ($\phi_1\le\phi_0$, $0<\phi_0<1$) always lowers the SNR: the bracket is at most
   $\phi_0^2-\phi_0<0$ and the correlation terms are $\le0$. In particular **a random gate still hurts**, whatever the correlation.
3. The necessary condition of method.tex, $\phi_1>2\phi_0-\phi_0^2$, is replaced by $\phi_1>\phi_0$ when $\gamma_1,\gamma_{01}\ge0$; it is
   recovered at zero correlation.
4. *Explicit boundary* ($\mu_c=0$, $\gamma_{01}=0$). With $G=(\rho m-1)\gamma_1$, $\chi=\rho\sigma_c^2/\{(1-\rho)(\sigma^2+\mu^2)\}$ and
   $x=\phi_1-\phi_0$, (2.5) reads $Gx^2-x\{1+2G(1-\phi_0)\}+\phi_0(1-\phi_0)(1+1/\chi)<0$, so gating helps iff $\phi_1>b(\phi_0)$ with
   $$b(\phi_0)=\phi_0+\frac{1+2G(1-\phi_0)-\sqrt{\{1+2G(1-\phi_0)\}^2-4G\,\phi_0(1-\phi_0)(1+1/\chi)}}{2G},$$
   and no gate helps at that $\phi_0$ if the root is complex or $b(\phi_0)>1$. As $G\to0$, $b(\phi_0)\to2\phi_0-\phi_0^2+\phi_0(1-\phi_0)/\chi$ (the
   red team's M-d frontier). For $\phi_1>\phi_0$ the left side of (2.5) increases in $\phi_1$ (derivative $\rho\sigma_c^2[1+G(2-2\phi_1)]>0$), so
   the helping region is $\{\phi_1>b(\phi_0)\}$; $b$ decreases in $G$ and $b(\phi_0)\to\phi_0$ as $G\to\infty$. Check B4: the closed form equals
   bisection on the direct SNR comparison to $3.6\times10^{-15}$; the ILLUSTRATIVE table in section 5 shows the boundary falling toward the
   diagonal as $\gamma_1$ grows.

(d) *Large-$m$ limit (general $\mu_c$).* If $\gamma_0>0$ and $m\to\infty$ with $\rho$, $\phi$ and $\gamma$ fixed, then with retained shares
$a=(1-\rho)k_0$, $b=\rho k_1$ and $A=\gamma_0\sigma^2$, $B=\gamma_{01}\sigma\sigma_c$, $C=\gamma_1\sigma_c^2$,
$$\frac{\E S}{\sqrt{\Var S}}\;\to\;\frac{a\mu+b\mu_c}{\sqrt{a^2A+2abB+b^2C}}=:g(r)^{1/2},\quad r=b/a,\qquad g(r)=\frac{(\mu+r\mu_c)^2}{A+2rB+r^2C}.$$
The SNR no longer grows like $\sqrt m$ and depends on the gate only through the retained corrupted-to-clean mass ratio $r$. The stationarity
equation of $g$ is linear in $r$, so $g$ has one maximiser,
$$r^\ast=\frac{\mu_cA-\mu B}{\mu C-\mu_cB},$$
which is the ratio of the Fisher weights of the two class sums. Gating helps in the limit iff $g(r_g)>g(r_0)$, $r_0=\rho/(1-\rho)$. For
$\mu_c=0$ and $B,C\ge0$ (not both zero) $g$ is decreasing on $r\ge0$, so the limit condition is simply $\phi_1>\phi_0$. When $\mu_c$ has the sign
of $\mu$, $r^\ast$ can be positive, and a gate that removes too many corrupted tokens can lower the SNR (corrupted tokens still carry
evidence). Checks B5.

(e) *The sign now depends on $m$.* Under independence the sign of the SNR change does not depend on $m$ (SAP AD.3). With $\gamma_1\ne0$ or
$\gamma_{01}\ne0$ it does, through $(\rho m-1)$ and $m$ in (2.5). A sign fitted at one image size does not transfer to another.

### 2.4 Remark: SNR of the sum, or SNR given the flags

The decision is $Y=\ind[S>0]$. Given the flags, $S$ is a sum over the retained set, and for Gaussian $\Delta$ it is exactly normal with the
retained counts $N_0,N_1$ in place of $m_0k_0,m_1k_1$. Evaluating that conditional SNR at the expected counts $n_z=k_zm_z$ gives
$\Var_{\rm cond}=n_0\sigma^2\{1+(n_0-1)\gamma_0\}+n_1\sigma_c^2\{1+(n_1-1)\gamma_1\}+2n_0n_1\gamma_{01}\sigma\sigma_c$, and
$$\Var S-\Var_{\rm cond}=m_0k_0\phi_0(\mu^2+\gamma_0\sigma^2)+m_1k_1\phi_1(\mu_c^2+\gamma_1\sigma_c^2)$$
(check B5): the unconditional variance (2.2) also counts the fluctuation of the retained count. For $\mu_c=0$ the conditional version of
(2.5) has right side $(1-\rho)\phi_0(1-\phi_0)(1-\gamma_0)\sigma^2$ and an extra left term $\rho\phi_1(1-\phi_1)\gamma_1\sigma_c^2$. The two versions
coincide when $\mu^2$, $\gamma_0\sigma^2$ and $\gamma_1\sigma_c^2$ are small against $\sigma^2$; in the ILLUSTRATIVE accuracy table of section 5
they differ in the fourth decimal. method.tex and the frozen E-pred use the unconditional form; this remark does not change that.

### 2.5 Remark: what (M4) leaves out

Flags that are correlated with each other (contiguous flagged regions) enter the unconditional variance through $\mathrm{Cov}(I_j,I_k)$ times
$\E[\Delta_j\Delta_k]$, and enter the conditional version only through the realised counts. Flags that depend on $\Delta$ within a class (a gate
that removes clean tokens with unusual evidence) violate (M4) and change the retained class means; this is the composition effect that SAP
AB.2 names in the oracle-gate residual $U$. Neither is modelled here.

### 2.6 Remark: Chair-Varshney under exchangeable dependence (answers plan review A8 in part)

The per-token sum is the naive-Bayes (Chair-Varshney) rule, optimal for sources independent given the hypothesis (method.tex lines 409-411).
Image tokens are dependent. But if the clean $\Delta_j$ are jointly Gaussian with a common mean and exchangeable covariance
$\Sigma=\sigma^2\{(1-\gamma_0)I+\gamma_0\mathbf 1\mathbf 1^\top\}$, then $\Sigma^{-1}\mathbf 1\propto\mathbf 1$ (Sherman-Morrison), so the equal-weight
sum is still the Fisher and Neyman-Pearson statistic for the sign of the common mean (check B6). Under this model dependence does not change
which linear combination is optimal on clean tokens; it changes its SNR (by the design effect) and, by Prop. 2, the trade-off of gating. This
is a statement under a model and does not make the sum optimal for UniDisc's actual dependence, which is not exchangeable (neighbouring tokens
are more correlated than distant ones). The method.tex sentence "used here as a standard statistic and not as an optimal one" stays correct.

---

## 3. Proposition 3: reliability weights (theory reference for the A4 Tier-3 SOFT arms)

### 3.1 Lemma 2 (weighted statistic)

Let $S_w=\sum_jw_j\Delta_j$ with $w_j\ge0$. The A4 arms report $\sum_jw_j\Delta_j/\sum_jw_j$, which has the sign of $S_w$, so the decision and
the SNR comparison are the same. Assume (M1)-(M3) and **(W)**: within a class the $w_j$ are i.i.d. with mean $\bar w_z$ and second moment
$\overline{w^2}_z$, independent of all $\Delta$. Then
$$\E S_w=m_0\bar w_0\mu+m_1\bar w_1\mu_c,$$
$$\begin{aligned}\Var S_w={}&m_0\{\overline{w^2}_0(\sigma^2+\mu^2)-\bar w_0^2\mu^2\}+m_1\{\overline{w^2}_1(\sigma_c^2+\mu_c^2)-\bar w_1^2\mu_c^2\}\\&+m_0(m_0-1)\bar w_0^2\gamma_0\sigma^2+m_1(m_1-1)\bar w_1^2\gamma_1\sigma_c^2+2m_0m_1\bar w_0\bar w_1\gamma_{01}\sigma\sigma_c.\end{aligned}$$
The proof is that of Lemma 1 with $I_j$ replaced by $w_j$. Hard gating is $w=I$, $\bar w_z=\overline{w^2}_z=k_z$, and returns (2.2). Checks C1.

### 3.2 Proposition 3 (SNR-optimal weights as a function of the score)

Condition on the scores $u_1,\dots,u_m$ and treat the weights as fixed functions $w_j=w(u_j)$. Assume **(W1)** $\Delta_j$ is independent of
$u_j$ given $Z_j$; **(W2)** the labels $Z_j$ are independent across tokens given the scores; **(W3)** $\sigma_c=\sigma$ and a single
exchangeable correlation $\gamma$ for all pairs (so that the shared component does not depend on the unknown classes). Then
$\E[\Delta_j\mid u]=\mu(u_j)=(1-\pi_1(u_j))\mu+\pi_1(u_j)\mu_c$, $\Var(\Delta_j\mid u)=\sigma^2(u_j)=\sigma^2+\pi_1(1-\pi_1)(\mu-\mu_c)^2$, and
$\mathrm{Cov}(\Delta_j,\Delta_k\mid u)=\gamma\sigma^2$, so $\Sigma=D+\gamma\sigma^2\mathbf 1\mathbf 1^\top$ with $d_j=\sigma^2(u_j)-\gamma\sigma^2$.
The SNR is $\sum_jw_j\mu(u_j)/\sqrt{w^\top\Sigma w}$.

(a) *Independent tokens ($\gamma=0$).* The maximiser over all real weights is the matched filter $w^\ast(u)\propto\mu(u)/\sigma^2(u)$
(Cauchy-Schwarz). With non-negative weights it is $(\mu(u))_+/\sigma^2(u)$. If $\mu_c=0$ and $\mu^2\ll\sigma^2$, then
$w^\ast(u)\propto1-\pi_1(u)$: **the optimal reliability weight is the posterior probability that the token is clean.** It is soft; a hard gate
is optimal only when $\pi_1(u)\in\{0,1\}$ (an oracle).

(b) *Exchangeable correlation, non-negative weights ($\gamma>0$).* The maximiser over $w\ge0$ is
$$w^\ast(u_j)\propto\frac{(\mu(u_j)-\xi)_+}{d_j},\qquad\xi=\gamma\sigma^2\sum_k\frac{(\mu(u_k)-\xi)_+}{d_k},$$
and the fixed-point equation has a unique solution $\xi\ge0$, with $\xi=0$ iff $\gamma=0$. *Proof.* Maximising the ratio over the cone $w\ge0$ is
equivalent, up to scale, to the convex problem $\min_{w\ge0}\tfrac12w^\top\Sigma w-w^\top\mu(u)$. Its KKT conditions are
$d_jw_j+\gamma\sigma^2\sum_kw_k-\mu(u_j)=\eta_j\ge0$ with $\eta_jw_j=0$. On the support, $w_j=(\mu(u_j)-\xi)/d_j$ with $\xi=\gamma\sigma^2\sum_kw_k$;
off it, $\mu(u_j)\le\xi$. The right side of the fixed-point equation is continuous and non-increasing in $\xi$ and the left side is increasing,
so the solution is unique. $\square$
So **correlation turns the optimal soft weight into a gated soft weight**: tokens whose expected evidence $\mu(u)$ is below $\xi$ get weight
zero, the others a weight that still varies with $u$. The threshold grows with $\gamma$ and with the number of tokens. Check C2: the
fixed-point form equals a numerical QP optimum to $5\times10^{-16}$; in the ILLUSTRATIVE run the number of zero-weight tokens rises with
$\gamma$. At $\gamma=0$ a few tokens get zero weight only because $\mu(u)\le0$ when $\mu_c<0$.

(c) *Unconstrained, $\gamma>0$.* Without $w\ge0$ the optimum is $\Sigma^{-1}\mu(u)$, which subtracts a multiple of the shared component and gives
negative weights to tokens with low $\mu(u)$ (control variates). This uses only population constants, not per-item labels, but it is not a
weighting and it is outside every A4 arm.

### 3.3 Corollary 3.1 (cost on a clean pair)

On a clean pair ($\rho=0$) the optimal weight is constant, so any non-constant weight loses SNR. Conditional on the weights, with
$\nu=m\sum_jw_j^2/(\sum_jw_j)^2$ and exchangeable clean correlation $\gamma_0$,
$$\frac{\mathrm{SNR}^2_w}{\mathrm{SNR}^2_{\rm none}}=\frac{(1-\gamma_0)+\gamma_0m}{(1-\gamma_0)\,\nu+\gamma_0m}.$$
For weights spread uniformly over the conformal p-value grid $\{1,\dots,N+1\}/(N+1)$ (what SOFT-A gives a clean token whose score has the
calibration distribution), $\nu=2(2N+3)/\{3(N+2)\}$, so at $\gamma_0=0$ the ratio is $3(N+2)/\{2(2N+3)\}\to3/4$, and it tends to 1 as
$\gamma_0m\to\infty$. For a hard gate with retained fraction $k_0$, $\nu=1/k_0$ and the ratio is
$\{(1-\gamma_0)+\gamma_0m\}/\{(1-\gamma_0)/k_0+\gamma_0m\}$. Checks C3. These are derived constants under the model, not predictions of an M4 value.

### 3.4 How Proposition 3 relates to the A4 Tier-3 arms (theory reference only)

- GM is the hard 0/1 weight $\ind[u_j\le\hat\tau]$. It is optimal in (a) only for an oracle, and in (b) it has the right shape (a cut) but not
  the soft part above the cut.
- SOFT-A uses $w^A_j=P_{\rm cal}(u_j)$ (A4.1.5). Under monotone likelihood ratio both $P_{\rm cal}(u)$ and $1-\pi_1(u)$ decrease in $u$, but
  $P_{\rm cal}$ uses only the clean score distribution: it ignores $\rho$, the corrupted score distribution and $\mu,\mu_c$, so it is a surrogate of
  $w^\ast$, not $w^\ast$. Its clean-pair cost is Corollary 3.1.
- SOFT-G discounts flagged tokens only; its weights lie between GM's and NONE's (A4.1.5, F7(b)).
- Which arm wins on M4 depends on $\gamma$'s and on $\pi_1(u)$, which no plan estimates. **This file makes no prediction of the ranking of the
  A4 arms.** By A4.4 item 2 no weight may be added after M4, so $w^\ast$ is **not an arm** and must not be computed on M4 data as a comparator.
  A later reader may use Prop. 3 only to say what the arms approximate under a model.

---

## 4. How this enters the paper

1. **Placement.** Method, as two short subsections after the existing SNR paragraph (method.tex `par:snr`, lines 308-334): (i) Prop. 1 with
   Corollaries 1.1 and 1.2 as "a limit of within-modality validation", next to the evidence-separation rule it qualifies; (ii) Prop. 2(b)-(d)
   and Prop. 3 as "correlated tokens and reliability weights". Statements in Method, proofs in an appendix (new appendix section after the
   crosswalk), with the toy checks named as such. The notation table gains $\gamma_0,\gamma_1,\gamma_{01},\vartheta,\chi,w_j$; nothing is renamed.
2. **Labels.** Every statement is labelled "theory under stated assumptions; not validated on UniDisc". Prop. 1 is "a limit that holds for any
   within-modality score", never "GATE's detection is limited by" (must-not-claim 6, and section 1.7). Prop. 2 and 3 are "a model of when
   withholding helps an additive statistic", never "predicts".
3. **E-pred is untouched.** The frozen E-pred (`theory.py` blob `4d2b5500`, `epred_fit.py`, `epred_frozen.json`; SAP AB.3, card v4 1.2) uses the
   independent-token form; none of the formulas here is used by it, by any sign, cell or table of E-pred, or by P, PS, S2, B, R or the suite. If
   the paper shows the correlated frontier, it is a theory figure with no measured points (red-team M-d's low-risk form); overlaying
   $(\hat\phi_0,\hat\phi_1)$ points would be E-pred content and is governed by AB.3 wording.
4. **No result clause.** Neither proposition may be used in the title, abstract, highlights or conclusion as an account of any P, PS, S2, B,
   R, E-dec, E-pred or Tier-3 result (AB.1). In Discussion it may appear only as context after the P result is stated, per A4.1.10's placement
   rule for Tier-3 material.
5. **Dating.** This file and its check script are committed before any M4 value is read (the commit time is the evidence). If the content is
   revised after M4 is read, the revision is labelled post hoc.
6. **Before use.** Hand to `red-team` for the derivations (contract: proposer is never validator), and to `citation-validator` for the
   standard results named in the header (Neyman-Pearson, Pinsker, Sherman-Morrison, Gibbs invariance) and for a search on the AUROC-TV constant.

---

## 5. Numerical check (`research/paper2/method/theory_check_2026-10-29.py`)

CPU only, about 20 s on the laptop CPU while the GPU stage was running; seed 20261029; numpy 2.4.2, scipy 1.17.1, Python 3.14.3. It imports
`exp_p2/gate/theory.py` read-only to check the reductions. Every value below is from toy models or ILLUSTRATIVE parameters, not from UniDisc.
Output of the final run (2026-10-29, 00:23 IST), verbatim:

```
theory_check_2026-10-29.py  seed=20261029  numpy=2.4.2

=== A. Proposition 1: detectability limit ===
[PASS] A1 |AUROC(f)-1/2| <= v - v^2/2 for random laws and scores  (max excess -2.18e-04)
[PASS] A1 AUROC(LR) >= AUROC(f) (LR is AUROC-optimal)  (max excess 0.00e+00)
[PASS] A1 AUROC(LR) >= 1/2 + v/2  (max shortfall 2.22e-16)
[PASS] A2 bound attained by the three-point example  (max |err| 2.2e-16)
  toy: V=3, L=8, items=40000, hit rate h=0.25; AUROC s.e. at 1/2 approx 0.0012
  Gibbs (law-invariant) corruption, hit label, pooled AUROC - 1/2: B_full (K=m) -0.0007, B_grp (K=2) -0.0009, q=B_grp-D -0.0005, u=-q +0.0005, -B_grp +0.0009, D -0.0004, random -0.0009
[PASS] A3 every within-modality score has pooled AUROC 1/2 (within 4 s.e.) under law-invariant corruption  (max |dev| 0.0009)
[PASS] A3 per-item mean AUROC of u has expectation 1/2  (0.5005 +/- 0.0014)
  uniform replacement (off-manifold), hit label, pooled AUROC: -B_grp 0.6111, u=-q 0.5978, random 0.5011
[PASS] A3 positive control: uniform replacement is detected (AUROC of -B well above 1/2)
  changed-code label, single-site resample: mean collision prob sbar=0.6272, exact TV=0.3396, bound=1.7648
[PASS] A4 exact TV <= sbar/(1-sbar) + h sbar/(1-h+h sbar)
  exact AUROC of the LR score (-pi_j(x_j | x_-j)) = 0.7202; limits [1/2 + v/2, 1/2 + v - v^2/2] = [0.6698, 0.7819]
[PASS] A4 exact AUROC(LR) within the two-sided bound of Prop. 1(a,b)
[PASS] A4 Monte Carlo AUROC(-pi) under changed label matches the exact value  (MC 0.7189 vs exact 0.7202)
[PASS] A4 same corruption, hit label: AUROC 1/2  (0.4974)
[PASS] A5 within-modality scores blind to caption-blind (P_a-invariant) corruption  (max |AUROC-1/2| 0.0007)
  per-token caption-blind Gibbs: cross-modal evidence mean on unhit tokens +0.0980, on hit tokens +0.0929 (s.e. 0.0016); small here because the unhit neighbours still carry the caption
  item-level independent redraw from P_a: max |AUROC-1/2| of within-modality scores 0.0030; cross-modal evidence mean on clean items +0.0986, on hit items -0.0006
[PASS] A5 item-level law-invariant redraw: within-modality scores at 1/2  (0.0030 vs 4 s.e. 0.0115)
[PASS] A5 item-level law-invariant redraw: cross-modal evidence on hit items falls to about 0
  cross-modal suspicion -(log p(v_j|v_-j,c) - log p(v_j|v_-j)) pooled AUROC 0.5187
[PASS] A5 a caption-using score detects what within-modality scores cannot

=== B. Proposition 2: correlated-token SNR of hard gating ===
[PASS] B1 Lemma 1 mean (Monte Carlo)  (MC 7.7016 vs 7.7000)
[PASS] B1 Lemma 1 variance (Monte Carlo)  (MC 144.238 vs 144.516)
[PASS] B2 Lemma 1 at gamma=0 equals theory.mean_var  (max rel diff 1.2e-13)
[PASS] B2 closed form at gamma=0 equals theory.special_case_inequality  (0 mismatches in 20000)
[PASS] B3 closed form (mu_c=0, correlated) has the sign of the direct SNR change  (0 mismatches in 31434)
  ILLUSTRATIVE frontier (not estimates): m=1024, rho=0.1, mu=0.1, sigma2=sigma2_c=1, gamma_01=0, chi (red-team kappa)=0.1100
  phi0   g1=0        g1=0.0001   g1=0.001    g1=0.01     g1=0.05   
  0.01   0.1099      0.1080      0.0938      0.0436      0.0191    
  0.05   0.5293      0.5224      0.4666      0.2243      0.0961    
  0.1    none        0.9999      0.9265      0.4708      0.1941    
  0.2    none        none        none        none        0.3993    
[PASS] B4 closed-form boundary equals bisection on the direct SNR comparison  (max |diff| 3.6e-15)
[PASS] B4 boundary decreases with gamma_1 and stays above the diagonal phi1 = phi0
[PASS] B4 boundary tends to the diagonal as (rho m - 1) gamma_1 grows  (b(0.05) = 0.050000)
[PASS] B4 gamma_0 does not enter k0^2 Var S_0 - Var S_g when mu_c = 0  (40.780000 vs 40.780000)
[PASS] B4 a random gate (phi1 = phi0) lowers the SNR for any gamma_1, gamma_01 >= 0
[PASS] B5 large-m limit of the SNR depends only on the retained shares  (0.34227 vs 0.34227)
[PASS] B5 r* maximises the large-m SNR^2 over the retained-mass ratio  (max rel excess of grid max over g(r*) 1.7e-14)
[PASS] B6 exchangeable Sigma: Sigma^{-1} 1 is proportional to 1  (max cv 5.8e-13)
[PASS] B5 Var_uncond - Var_cond = m0 k0 phi0 (mu^2 + g0 s2) + m1 k1 phi1 (muc^2 + g1 s2c)  (gap 8.73e-13)
  ILLUSTRATIVE accuracy check, common random numbers across rows (m0=360, m1=40, mu=0.05, sigma2=sigma2_c=1, mu_c=0, g0=0.01, g1=0.05, g01=0):
    phi0  phi1   P(S>0) MC   Phi(SNR_uncond)  Phi(SNR_cond)
    0.0   0.0    0.6654      0.6656           0.6656
    0.05  0.05   0.6636      0.6647           0.6647
    0.05  0.5    0.6656      0.6681           0.6681
    0.05  0.9    0.6684      0.6699           0.6699
    0.2   0.9    0.6648      0.6665           0.6666
    (MC s.e. of one P(S>0) is about 0.0024; differences between rows share the random numbers)

=== C. Proposition 3: reliability weights ===
[PASS] C1 Lemma 2 mean (Monte Carlo)  (MC 6.9406 vs 6.9500)
[PASS] C1 Lemma 2 variance (Monte Carlo)  (MC 97.504 vs 97.391)
[PASS] C1 Lemma 2 with w = I equals Lemma 1
[PASS] C2 gamma=0: matched filter mu(u)/sigma^2(u) attains the optimal SNR  (max rel loss 0.0e+00)
[PASS] C2 w >= 0 with exchangeable correlation: soft-threshold fixed point equals the QP optimum  (max rel diff 5.0e-16)
  ILLUSTRATIVE (n=60 tokens): gamma -> mean threshold xi, mean number of tokens given weight 0
    gamma=0.0    xi=0.0000  zero-weight tokens=0.1
    gamma=0.002  xi=0.0173  zero-weight tokens=0.8
    gamma=0.02   xi=0.0889  zero-weight tokens=5.9
    gamma=0.1    xi=0.1498  zero-weight tokens=21.7
[PASS] C2 threshold xi is 0 at gamma=0 and increases with gamma
[PASS] C3 nu = E w^2 / (E w)^2 on the p-value grid equals 2(2N+3)/(3(N+2)), N=10
[PASS] C3 nu = E w^2 / (E w)^2 on the p-value grid equals 2(2N+3)/(3(N+2)), N=1000
[PASS] C3 nu = E w^2 / (E w)^2 on the p-value grid equals 2(2N+3)/(3(N+2)), N=1000000
  clean-pair SNR^2 ratio (weights / none), conditional on weights, uniform p-value weights, by gamma_0:
    gamma_0=0.0    direct 0.75037  formula 0.75037
    gamma_0=0.001  direct 0.85890  formula 0.85890
    gamma_0=0.01   direct 0.97151  formula 0.97151
    gamma_0=0.1    direct 0.99711  formula 0.99711
[PASS] C3 clean-pair efficiency formula [(1-g)+g m]/[(1-g) nu + g m] matches the quadratic form

SUMMARY: ALL CHECKS PASSED
```

Notes on the checks. (1) A first version of check A5 asserted that per-token caption-blind Gibbs lowers the cross-modal evidence by more than
4 s.e.; in this toy the drop (0.0980 to 0.0929) is smaller than that because unhit neighbours still carry the caption, so the size of the
per-token damage is reported as information only and the corollary is checked with the item-level redraw. Corollary 1.2(ii) says the damage
*can* be destroyed, not that it always is. (2) A first version of the $r^\ast$ check compared grid argmaxes and failed on flat maxima; it now
compares $g(r^\ast)$ with the grid maximum. (3) In the accuracy table the Monte Carlo accuracies sit 0.001 to 0.003 below $\Phi(\mathrm{SNR})$
with shared random numbers; this is within about one s.e. of one cell and is not interpreted.

## 6. Concerns

1. Prop. 1 is close to elementary; its value for the paper is the fusion corollary (1.2(ii)) and the changed-label caveat (1.1(iii)). A reviewer
   may still call it padding (red-team N-a). Keep it short in Method.
2. Must-not-claim item 6 says "no bound on detection power". Prop. 1 is an upper limit under an idealised model, not a power guarantee; the
   lead should decide whether item 6 needs a clarifying sentence before Prop. 1 is placed in Method.
3. Corollary 1.1(iii) shows the changed-code label alone can make an on-manifold resample look detectable. This bears on the label-circularity
   concern for JPEG and noise, and is exactly the kind of statement K2 restricts: it may describe the label, not explain the M1 rival's win.
4. Prop. 2 and 3 use exchangeable correlation; UniDisc's dependence is spatial. The direction results (frontier moves toward the diagonal with
   positive $\gamma_1,\gamma_{01}$; correlation induces a cut in the optimal weight) are the robust content; the closed forms are model-bound.
5. Neither proposition has been red-teamed. Hand to `red-team` before any manuscript text is drafted from this file.

---

# Revision r1 (2026-10-29)

**Written 2026-10-29, 00:48-01:00 IST, before any M4 value has been read.** I did not open `runs/P2-GATE-M4/` or any M4 output. Inputs:
the red-team review `research/paper2/method/THEORY-REDTEAM-2026-10-29.md` (commit 29b5d41b) and the lead's decision D0078 (last row of
`research/ledgers/decisions.jsonl`, commit 27e7c63e). Sections 0-6 above are kept unchanged as the r0 record (commit 1fed4d2f). **Where r1
contradicts r0, r1 governs.** The manuscript, code, preregistration files and ledgers were not edited.

## R1.1 Status of each item after r1

| Item (r0 section) | r1 status | Where it may appear |
|---|---|---|
| Prop. 1(a)-(d) (1.2-1.3) | **Withdrawn as a contribution.** Background only: a known result, Li et al., arXiv 2102.08504, App. A.3 (proof of Thm. 1, eqs. 5-11, read by the red team at E2 from a garbled conversion; citation-validator must confirm the reference before use). Holds for the **pooled** population token AUROC only | At most one background sentence (R1.2), subject to the lead's ruling on must-not-claim 6 |
| Prop. 1(e) (1.2-1.3) | Correct under (C1)-(C2) and a uniform hit set given its size; elementary; not a contribution | Not proposed for the manuscript |
| Cor. 1.1(i)-(iii) (1.4) | **Withdrawn as a contribution.** (iii) has a false premise (R1.3) and is **not for manuscript use** (K2, D0074; D0078) | Nowhere in the manuscript |
| Cor. 1.2 (1.5) | (i) falls with Prop. 1 (pooled only); (ii) is a toy existence statement. Not proposed for the manuscript | Not proposed |
| Prop. 2 (2.1-2.5) | **Enters Method with the fixes of R1.4**; manuscript-ready text in R1.8 | Method (statement, sketch) and appendix (proof) |
| Remark 2.6 | **Replaced** by R1.5. It does not restore Chair-Varshney optimality and does not answer A8 beyond "independence is an approximation" | One sentence at most, as in R1.5 |
| Prop. 3, Cor. 3.1 (3.1-3.4) | Theoretical reference for the A4 soft arms only, with the corrections of R1.6; w* is not an A4 arm | Beside the A4 Tier-3 table, as a reference; not in Method as a contribution |

## R1.2 Proposition 1 and Corollary 1.1: background only

1. **Known result.** The inequality $|\mathrm{AUROC}-\tfrac12|\le\vartheta(1-\vartheta/2)$ is the core step of Li et al. (arXiv 2102.08504, App. A.3):
   $\mathrm{TPR}-\mathrm{FPR}\le\vartheta$ at every threshold, so the ROC area is at most $\int_0^1\min(\mathrm{FPR}+\vartheta,1)\,d\mathrm{FPR}=\tfrac12+\vartheta-\vartheta^2/2$.
   The lower limit $\tfrac12+\vartheta/2$ for the likelihood-ratio score and the characterisation in (b) are textbook (Youden index and
   Kolmogorov-Smirnov distance). r0's "whether the constant appears in the literature was not searched" is superseded: it does. **No
   sentence may call any part of Prop. 1 new or say "we prove" it.** The text of sections 1.1-1.7 is kept as a record and is withdrawn as a
   contribution.
2. **Pooled, not per item.** Prop. 1(a)-(b) and Cor. 1.2(i) bound only the pooled population AUROC $P\{f(X_1)>f(X_0)\}$ with $X_z\sim Q_z$. The
   per-item mean AUROC, which method.tex lines 126-129 quote, compares tokens within an item and weights items equally; the item grouping is
   information outside $(\tilde x_j,O_j)$. Check D1 reproduces the red team's counterexample: the pooled class laws are equal ($\vartheta=0$,
   pooled AUROC 0.500), and the per-item mean AUROC is 0.625. Only Prop. 1(e) makes a per-item statement, and only under (C1)-(C2) with a
   uniform hit set given its size. **No sentence may apply $\vartheta(1-\vartheta/2)$, or "AUROC $=\tfrac12$", to a per-item AUROC.**
3. **Wording corrections kept for the record.** "On-manifold" is replaced by **"law-preserving"** throughout sections 1.2-1.7 (a corruption to
   another value in the support with a different frequency stays in the support and is detectable). Cor. 1.1(i)-(ii) are well posed only for
   one hit per item or for sequential (Gibbs) updates, which is case (e); with several simultaneous hits the score sees a context that
   contains other new values. "Bayes-optimal model $p_\theta=\pi_0$" means a model trained on clean data only when the context is clean. The
   class $\mathcal F_a$ contains every own-modality score only if $O_j$ is taken as the full own-modality context; with $O_j$ as the context
   outside the token's group (section 0), scores that read other tokens of the same group are outside the class.
4. **The single permitted background sentence** (red-team wording, section 6.3 of the review; usable only if the lead's ledger ruling on
   must-not-claim 6 allows it, since an impossibility limit on AUROC is still a bound on detection power): "For the pooled token AUROC
   against the hit indicator, any score computed from a token and its own-modality context satisfies $|\mathrm{AUROC}-\tfrac12|\le\vartheta(1-\vartheta/2)$,
   where $\vartheta$ is the total variation between the class laws of (token, context) [Li et al., arXiv 2102.08504, App. A.3]; if the
   corruption preserves the law of the own modality given the context, $\vartheta=0$. This is a property of an idealised data model and is
   not evaluated for the corruptions studied here." Never next to the M1 table, the rival, or a P result; never in the title, abstract,
   highlights or conclusion; never "on-manifold", never "$q$'s detection is limited by".

## R1.3 Corollary 1.1(iii): corrected premise, not for manuscript use

The r0 text says that (A1) holds for the full context. **Under the changed-code label it does not:** for a hit token
$P(Z_j=1\mid o)=1-s(o)$, so the context law given $Z_j=1$ is $\mu_O(do)(1-s(o))/(1-\bar s)$, not $\mu_O$. The joint laws $Q_1,Q_0$ used in
the r0 proof are correct as joint laws, and so are the total variation computation and the monotonicity of the likelihood ratio in
$\pi_0(\tilde x_j\mid O_j)$. The triangle step is tight (the two deviations from $\mu_O\pi$ have opposite signs at every point), so the
total variation is exactly
$$\vartheta=\tfrac12\,\E_O\sum_y\pi(y\mid O)\,\big|\pi(y\mid O)-\bar s\big|\,\Big[\frac1{1-\bar s}+\frac{h}{1-h+h\bar s}\Big].$$
Check A6 confirms the identity to $10^{-12}$ in the toy (0.339555 both ways; the r0 check A4 of the loose bound could not fail and is
superseded). Under this label the **context alone is a detector**: the context-only score $-s(o)$, which never reads the token value, has
exact pooled AUROC 0.6597 in the toy (check A6; the red team found 0.68-0.69 in three other toys).

**Not for manuscript use (K2, D0074; D0078).** Read next to the M1 table, this statement would supply a mechanism for the texture or
pixel-variance rival's advantage on JPEG and noise. K2 forbids presenting that advantage as evidence for any mechanism, and AB.1 forbids
explanation clauses. The direction of the toy effect has not been shown to match the rival's sign, and whether the rival is in $\mathcal F_a$
is undecided. It is kept here only as a record.

## R1.4 Proposition 2: fixes

1. **Negative $\gamma_{01}$ (r0 section 2.3(c) item 1 and the YAML claim "negative values move it away" are wrong).** For
   $\gamma_{01}<0$ the cross term of (2.5) is positive below the diagonal, so a helping region can open **below** the diagonal: a gate that
   flags only clean tokens can raise the SNR, because it shifts weight toward corrupted tokens whose evidence is negatively correlated with
   the clean evidence. Check D4: with $m_0=900$, $m_1=100$, $\gamma_0=\gamma_1=0.05$, $\gamma_{01}=-0.045$ (minimum eigenvalue of the
   correlation matrix 0.9500), $\mu=0.1$, $\mu_c=0$, $\sigma^2=\sigma_c^2=1$, the gate $(\phi_0,\phi_1)=(0.3,0)$ raises the SNR from 0.4892 to 0.5080
   (ILLUSTRATIVE parameters, the red team's R4). Negative $\gamma_1$ alone cannot do this. **Corrected statement:** if $\gamma_{01}\ge0$, every
   gate with $\phi_1\le\phi_0$ lowers the SNR, for every admissible $\gamma_0$ and $\gamma_1$. *Proof:* positive semi-definiteness gives
   $G=(\rho m-1)\gamma_1\ge-1$. With $\phi_1\le\phi_0$ the bracket of (2.5), $(\phi_1-2\phi_0+\phi_0^2)+G(\phi_1-\phi_0)(2-\phi_0-\phi_1)$, is linear in
   $G$, equals $\phi_1-2\phi_0+\phi_0^2\le-\phi_0(1-\phi_0)$ at $G=0$, equals $-\phi_1(1-\phi_1)\le0$ at $G=-1$, and decreases in $G$ for $G\ge0$; so it is
   $\le0$. The cross term is $\le0$ when $\gamma_{01}\ge0$, and the right side is $>0$ for $0<\phi_0<1$. Check D4 (0 counterexamples in 20,000 random
   draws with $\gamma_1\in[-1/(m_1-1),0]$). A random gate ($\phi_1=\phi_0$) lowers the SNR for every correlation, because all correlation terms
   vanish on the diagonal. Above the diagonal the r0 derivative statements stand. The monotonicity of the left side in $\phi_1$ (r0 item 4)
   needs $G\ge-1/(2(1-\phi_1))$; the root formula for $b(\phi_0)$ does not.
2. **Large-$m$ limit (r0 2.3(d)).** $g(r)$ has two critical points: $r=-\mu/\mu_c$ (the zero of the numerator, the global minimum $g=0$; check
   D8) and $r^\ast$. $r^\ast$ is the maximiser over directions $(1,r)$ when $AC>B^2$ and $\mu C\ne\mu_cB$. The feasible range of the retained
   ratio is $r\in[0,\infty)$; if $r^\ast<0$ the best feasible value is $r=0$.
3. **SNR is not accuracy under non-Gaussian correlation (red-team M5).** Prop. 2 is a statement about $\E S/\sqrt{\Var S}$. Under independence the
   central limit theorem ties it to $P(S>0)$. With exchangeable correlation, $S/m$ converges to a random shared component, and $P(S>0)$
   depends on that component's law, not only on its variance. Check D5 (red team's R5, computed exactly over binomial retained counts and the
   factor): a rare non-Gaussian shared factor among corrupted tokens ($\gamma_1=0.074$), $\mu=0.05$, $\mu_c=0$, $m_0=900$, $m_1=100$; the gate
   $(0.1,0.5)$ raises the SNR from 1.081 to 1.254 and **lowers** the exact accuracy from 0.9149 to 0.9088 (ILLUSTRATIVE). With Gaussian shared
   factors the exact accuracy and $\Phi(\mathrm{SNR})$ agree in the sign of every change on the illustrative rows (check B8, which replaces the
   r0 Monte Carlo table that could not resolve these differences). **Rule:** the manuscript says "signal-to-noise ratio of the sum"; it says
   "accuracy" only together with "if the per-token terms are jointly Gaussian".
4. **(M4) is violated by construction in GATE.** The flags come from $u_j=D_j-B_j$, a function of the same token value as $\Delta_j$; the
   manuscript says that independence of flags and evidence is an approximation.
5. **Check-script wording (red-team m8).** B3 and B4 share Lemma 1's code with the closed form, so they check the algebra from Lemma 1 to (2.5),
   not Lemma 1; Lemma 1 is now checked by Monte Carlo at a second point with $\gamma_{01}<0$ (D3) and (2.5) by a symbolic identity (D3, sympy
   residual 0). The B3 draws do not enforce positive semi-definiteness; the word "valid" was removed.
6. **Illustrative numbers (red-team M8).** The illustrative frontier table, the toy values and every number in sections 1-3 and R1 come from
   `research/paper2/method/theory_check_2026-10-29.py`, which is not a `runs/<id>/` directory. **None of them may appear in the manuscript**
   (project rule: no number unless it is in `runs/`).

## R1.5 Remark 2.6, replaced

What the remark shows, exactly: **if** (1) the per-token terms $\Delta_j$ are jointly Gaussian under each caption hypothesis, (2) their mean
vector is proportional to $\mathbf 1$, (3) their covariance is the same under both hypotheses, (4) that covariance is fully exchangeable,
$\sigma^2\{(1-\gamma)I+\gamma\mathbf 1\mathbf 1^\top\}$, and (5) the decision threshold is the equal-prior threshold 0, **then** the equal-weight
sum $\mathbf 1^\top\Delta$ is the optimal (Fisher and Neyman-Pearson) statistic **among functions of the vector $\Delta$**, because
$\Sigma^{-1}\mathbf 1\propto\mathbf 1$ (Sherman-Morrison; check B6 verifies only this identity). Condition (2) fails with position-dependent means
and whenever $\rho>0$ with $\mu_c\ne\mu$ and unknown labels (then $\Delta$ is a non-Gaussian mixture); condition (4) fails for block-exchangeable
covariance ($\gamma_0,\gamma_1,\gamma_{01}$ not all equal).

What it does **not** show: Chair-Varshney optimality means that the sum of local log-likelihood ratios equals the global log-likelihood ratio
$\log p(v\mid c^+)-\log p(v\mid c^-)$, which requires the observations to be conditionally independent given the hypothesis. Under dependence the
global ratio is not $\sum_j\Delta_j$, whatever $\Sigma$ is. The remark is optimality within a data reduction, not optimality of the test on the
image; it does not restore Chair-Varshney optimality, and it answers plan review A8 only to the extent of stating that independence is an
approximation. The section title "Chair-Varshney under exchangeable dependence" and the phrase "answers plan review A8 in part" are
withdrawn. The method.tex sentence (lines 409-411) "used here as a standard statistic and not as an optimal one" stays as written. Permitted
manuscript sentence, if any: "If the per-token terms were jointly Gaussian with a common mean and the same exchangeable covariance under both
caption hypotheses, the equal-weight sum would be the optimal linear statistic of those terms; this does not make the sum the likelihood
ratio of the image, and the sum is used as a standard statistic."

## R1.6 Proposition 3 and Corollary 3.1: corrections (reference for the soft arms only)

1. **Prop. 3(a), corrected.** r0's sentence "a hard gate is optimal only when $\pi_1(u)\in\{0,1\}$ (an oracle)" is false. Correct statement:
   with independent tokens ($\gamma=0$) and $w\ge0$, the optimal weight is $(\mu(u))_+/\sigma^2(u)$, and **a hard (0/1) gate is optimal if and only if
   $(\mu(u))_+/\sigma^2(u)$ takes at most one non-zero value on the support of $u$** (up to scale). Example (check D6, the red team's R7): $\pi_1(u)$
   takes the values 0.3 and 1, $\mu_c=0$; the optimal weights are 0.1388 and 0, a 0/1 gate with no oracle. With two distinct non-zero values
   the optimum is not a 0/1 gate (check D6). The special case "$w^\ast\propto1-\pi_1(u)$ when $\mu_c=0$, $\sigma_c=\sigma$, $\mu^2\ll\sigma^2$" stands
   as an approximation. The r0 check C2 at $\gamma=0$ compared a vector with itself; it now compares the matched filter with a generic BFGS
   optimiser.
2. **Prop. 3(b).** "$\xi=0$ iff $\gamma=0$" holds only if some $\mu(u_k)>0$; if every $\mu(u_k)\le0$, $\xi=0$ for every $\gamma$ (check D7). The cut
   comes from the constraint $w\ge0$ together with correlation; the unconstrained optimum (c) has no cut. So the reading is "correlation plus
   non-negativity induces a cut", not "correlation favours gating".
3. **Assumption (W3)** forces $\gamma_0=\gamma_1=\gamma_{01}$ (and $\sigma_c=\sigma$), which is not the case in which Prop. 2's frontier moves (it depends
   on $\gamma_1,\gamma_{01}$, not $\gamma_0$, relative to each other). Props. 2 and 3 are therefore not jointly applicable, and no sentence may
   combine them.
4. **Lemma 2** also needs the weights to be independent across classes, not only within a class.
5. **Corollary 3.1, scope.** The 3/4 is an $\mathrm{SNR}^2$ ratio (an SNR ratio of about 0.866). It assumes (W1), scores independent of
   evidence, and weights i.i.d. uniform over the grid **within the item**. Within an item the scores are clustered (item-level shifts in
   suspicion), so a clean item's weights need not be spread over the grid, and the per-item cost can be smaller or larger. **3/4 is not
   SOFT-A's expected clean-cell cost, and it must not be compared with the M4 clean cell** (AB.1 spirit; A4.4 item 2).
6. Unchanged from r0 section 3.4: $w^\ast$ is not an A4 arm, may not be computed on M4 data, and no ranking of the A4 arms is predicted.

## R1.7 Binding rule: Prop. 2 never explains an E-pred disagreement

1. Proposition 2, its frontier and its large-$m$ limit are **never used to explain, account for, excuse or reinterpret an E-pred
   disagreement** (a cell where the committed independent-token sign differs from the observed sign), nor any agreement, in any text: paper,
   response to reviewers, supplement or internal report. The refutation rule of spec 5.3 and SAP AB.3 item 4 stand unchanged: a plug-in sign
   that disagrees with a cell whose observed interval excludes 0 refutes the independent-token model for that cell, and that is all that may
   be said.
2. No $\gamma_0,\gamma_1,\gamma_{01}$ is estimated on M4 arrays (or any test-fold array) to adjust, re-score or annotate E-pred, and no correlated
   frontier is overlaid with measured $(\hat\phi_0,\hat\phi_1)$ points. Such a step would be a post hoc rescue and a forking path (red-team
   M8; SAP AB.1 item 3, AB.3 items 4-6).
3. The words "predicts", "explains", "accounts for", "is consistent with" are not used for Prop. 2 about any E-pred, P, PS, S2, B, R, E-dec or
   Tier-3 cell. The word "predicted" appears only inside the E-pred table (AB.1 item 4).
4. E-pred itself is unchanged: `theory.py` (blob `4d2b5500`), `epred_fit.py` and `epred_frozen.json` use the independent-token form, and
   nothing in this file is used by them.

## R1.8 Manuscript-ready text for Proposition 2 (method.tex notation)

Symbols are those of method.tex (`\phi_0`, `\phi_1`, `\rho`, `\mu`, `\sigma^2`, `\mu_c`, `\sigma_c^2`, `m`, `S`, `I_j`, `\Delta_j`, macros `\E`, `\Var`);
new symbols are $\gamma_0,\gamma_1,\gamma_{01}$ only, to be added to Table `tab:notation`. Labels `prop:snrcorr`, `eq:varcorr`, `eq:snrcorr`,
`app:snrcorr` are new and do not collide with existing ones. No number appears in the block. It is a draft for the lead and the
manuscript-writer; this revision does not edit method.tex. The design-effect phrase may need a citation (Kish); `citation-validator` decides.

**Main text (Method, directly after the paragraph that ends with Eq. `eq:snr` and its three consequences):**

```latex
\paragraph{Correlated tokens.}
Neighbouring image tokens are correlated, so Eq.~\eqref{eq:var} is an approximation. The following statement replaces independence by an
exchangeable correlation; it is theory under stated assumptions and is not evaluated on the model.

\begin{proposition}[withholding with exchangeably correlated tokens]\label{prop:snrcorr}
Condition on the corruption labels, so that $(1-\rho)m$ tokens are clean and $\rho m$ are corrupted, with the moments $\mu,\sigma^2,\mu_c,\sigma_c^2$
and the keep probabilities $1-\phi_0$, $1-\phi_1$ of Eqs.~\eqref{eq:mean}--\eqref{eq:var}.
Assume (a) that for $j\neq k$ the correlation of $\Delta_j$ and $\Delta_k$ is $\gamma_0$ if both tokens are clean, $\gamma_1$ if both are
corrupted and $\gamma_{01}$ otherwise, with values for which the covariance matrix is positive semi-definite; and (b) that the keep indicators
$I_j$ are independent of each other and of every $\Delta_k$.
Then $\E S$ is given by Eq.~\eqref{eq:mean}, and, under (a) and (b),
\begin{equation}
\begin{aligned}
\Var S={}&V+(1-\rho)m\big((1-\rho)m-1\big)(1-\phi_0)^2\gamma_0\sigma^2+\rho m(\rho m-1)(1-\phi_1)^2\gamma_1\sigma_c^2\\
&+2\rho(1-\rho)m^2(1-\phi_0)(1-\phi_1)\gamma_{01}\sigma\sigma_c,
\end{aligned}
\label{eq:varcorr}
\end{equation}
where $V$ is the right side of Eq.~\eqref{eq:var}.
If moreover $\mu_c=0$ and $\E S>0$ with and without the gate, the gate raises $\E S/\sqrt{\Var S}$ if and only if
\begin{equation}
\begin{aligned}
&\rho\,\sigma_c^2\Big[(\phi_1-2\phi_0+\phi_0^2)+(\rho m-1)\,\gamma_1\,(\phi_1-\phi_0)(2-\phi_0-\phi_1)\Big]
+2\rho(1-\rho)\,m\,\gamma_{01}\,\sigma\sigma_c\,(1-\phi_0)(\phi_1-\phi_0)\\
&\qquad>\;(1-\rho)\,\phi_0(1-\phi_0)\,(\sigma^2+\mu^2).
\end{aligned}
\label{eq:snrcorr}
\end{equation}
Consequently:
(i) $\gamma_0$ does not enter Eq.~\eqref{eq:snrcorr}, and at $\gamma_1=\gamma_{01}=0$ it is Eq.~\eqref{eq:snr};
(ii) a gate with $\phi_1=\phi_0$, such as a random gate, lowers the ratio for every admissible correlation, and if $\gamma_{01}\ge0$ every gate
with $\phi_1\le\phi_0$ lowers it;
(iii) where $\phi_1>\phi_0$, a larger $\gamma_1$ or $\gamma_{01}$ can only turn a decrease of the ratio into an increase, so positive correlation
among corrupted tokens, or between clean and corrupted tokens, enlarges the region of $(\phi_0,\phi_1)$ in which the gate raises the ratio,
and as $(\rho m-1)\gamma_1\to\infty$ that region tends to $\{\phi_1>\phi_0\}$;
(iv) if $\gamma_{01}<0$, a gate that flags only clean tokens can raise the ratio;
(v) unlike Eq.~\eqref{eq:snr}, the condition depends on $m$.
\end{proposition}

\noindent\emph{Proof sketch.} Each of the $m(m-1)$ ordered pairs of distinct tokens adds $\E I_j\,\E I_k\,\mathrm{Cov}(\Delta_j,\Delta_k)$ to
$\Var S$, which gives the three correlation terms of Eq.~\eqref{eq:varcorr}. With $\mu_c=0$ the gate multiplies $\E S$ by $1-\phi_0$, so it
raises the ratio if and only if $(1-\phi_0)^2\,\Var S|_{\phi_0=\phi_1=0}>\Var S$; the clean-pair terms scale by $(1-\phi_0)^2$ on both sides and
cancel, and the remaining terms, divided by $m$, give Eq.~\eqref{eq:snrcorr}. Appendix~\ref{app:snrcorr} gives the full proof. \qed

The ratio in Proposition~\ref{prop:snrcorr} is the signal-to-noise ratio of the sum. If the per-token terms are jointly Gaussian, the
accuracy $P(S>0)$ given the flags is $\Phi$ of the conditional ratio, which the unconditional ratio approximates; without joint
Gaussianity no statement about accuracy follows, and a gate can raise the ratio while lowering the accuracy. Assumption (b) is an
approximation for GATE, whose flags are computed from the same token values as the evidence. With correlation the ratio no longer grows
like $\sqrt m$: it tends to a limit set by the shared component of the per-token terms. The descriptive family E-pred uses
Eqs.~\eqref{eq:mean}--\eqref{eq:var} as preregistered; Proposition~\ref{prop:snrcorr} is not used by it and is not used to interpret it.
```

**Appendix (new subsection after the symbol crosswalk):**

```latex
\subsection{Proof of Proposition~\ref{prop:snrcorr}}\label{app:snrcorr}
Write $m_0=(1-\rho)m$ and $m_1=\rho m$ for the numbers of clean and corrupted tokens, $k_0=1-\phi_0$ and $k_1=1-\phi_1$ for the keep
probabilities, and $z_j\in\{0,1\}$ for the label of token $j$, so that $\E\Delta_j$ is $\mu$ or $\mu_c$ and $\Var\Delta_j$ is $\sigma^2$ or
$\sigma_c^2$. Positive semi-definiteness of the exchangeable block covariance holds if and only if $\gamma_0\ge-1/(m_0-1)$,
$\gamma_1\ge-1/(m_1-1)$, $\gamma_0,\gamma_1\le1$ and $\gamma_{01}^2\,m_0m_1\le\{1+(m_0-1)\gamma_0\}\{1+(m_1-1)\gamma_1\}$.

\emph{Variance.} By assumption (b), $I_j$ is independent of $\Delta_j$, so
$\Var(I_j\Delta_j)=k(\sigma_z^2+\mu_z^2)-k^2\mu_z^2=k\sigma_z^2+k(1-k)\mu_z^2$ with $k=k_{z_j}$, which are the terms of Eq.~\eqref{eq:var}.
For $j\neq k$, again by (b),
$\mathrm{Cov}(I_j\Delta_j,I_k\Delta_k)=\E I_j\,\E I_k\,\E[\Delta_j\Delta_k]-\E I_j\,\E I_k\,\E\Delta_j\,\E\Delta_k=k_{z_j}k_{z_k}\,\mathrm{Cov}(\Delta_j,\Delta_k)$.
There are $m_0(m_0-1)$ ordered clean pairs with covariance $\gamma_0\sigma^2$, $m_1(m_1-1)$ ordered corrupted pairs with covariance
$\gamma_1\sigma_c^2$ and $2m_0m_1$ ordered mixed pairs with covariance $\gamma_{01}\sigma\sigma_c$, which gives Eq.~\eqref{eq:varcorr}.

\emph{Condition.} Let $V_g$ be Eq.~\eqref{eq:varcorr} at $(\phi_0,\phi_1)$ and $V_0$ its value at $\phi_0=\phi_1=0$. With $\mu_c=0$,
$\E S=m_0k_0\mu$ with the gate and $m_0\mu$ without it, so, both being positive, the gate raises the ratio if and only if $k_0^2V_0>V_g$.
Collect $k_0^2V_0-V_g$ by type of term. Clean terms:
$k_0^2m_0\sigma^2\{1+(m_0-1)\gamma_0\}-m_0k_0(\sigma^2+\phi_0\mu^2)-m_0(m_0-1)k_0^2\gamma_0\sigma^2=-m_0k_0\phi_0(\sigma^2+\mu^2)$; the $\gamma_0$ terms cancel.
Corrupted terms: $m_1\sigma_c^2\{(k_0^2-k_1)+(m_1-1)\gamma_1(k_0^2-k_1^2)\}$, with $k_0^2-k_1=\phi_1-2\phi_0+\phi_0^2$ and
$k_0^2-k_1^2=(\phi_1-\phi_0)(2-\phi_0-\phi_1)$. Mixed terms: $2m_0m_1\gamma_{01}\sigma\sigma_c\,k_0(k_0-k_1)$, with $k_0-k_1=\phi_1-\phi_0$.
Dividing the sum by $m$ gives Eq.~\eqref{eq:snrcorr}.

\emph{Consequences.} (i) is read off Eq.~\eqref{eq:snrcorr}. (ii) At $\phi_1=\phi_0\in(0,1)$ every correlation term vanishes and the left side
is $\rho\sigma_c^2(\phi_0^2-\phi_0)<0$, below the positive right side. For $\phi_1\le\phi_0$, let $G=(\rho m-1)\gamma_1$, so that $G\ge-1$ by
positive semi-definiteness. The bracket $(\phi_1-2\phi_0+\phi_0^2)+G(\phi_1-\phi_0)(2-\phi_0-\phi_1)$ is linear in $G$; it equals
$\phi_1-2\phi_0+\phi_0^2\le-\phi_0(1-\phi_0)$ at $G=0$, equals $-\phi_1(1-\phi_1)\le0$ at $G=-1$, and does not increase for $G\ge0$; hence it is at
most $0$. If $\gamma_{01}\ge0$ the mixed term is at most $0$ as well, while the right side is positive for $\phi_0\in(0,1)$.
(iii) The derivatives of the left side with respect to $\gamma_1$ and $\gamma_{01}$ are $\rho\sigma_c^2(\rho m-1)(\phi_1-\phi_0)(2-\phi_0-\phi_1)$ and
$2\rho(1-\rho)m\sigma\sigma_c(1-\phi_0)(\phi_1-\phi_0)$, both positive when $\phi_1>\phi_0$ and $\rho m>1$, and the right side does not depend on
$\gamma_1$ or $\gamma_{01}$. For fixed $\phi_1>\phi_0$ the $\gamma_1$ term grows without bound with $(\rho m-1)\gamma_1$, which gives the limit.
With $\gamma_{01}=0$, $x=\phi_1-\phi_0$ and $\chi=\rho\sigma_c^2/\{(1-\rho)(\sigma^2+\mu^2)\}$, Eq.~\eqref{eq:snrcorr} reads
$Gx^2-x\{1+2G(1-\phi_0)\}+\phi_0(1-\phi_0)(1+1/\chi)<0$, so for $G>0$ the gate raises the ratio if and only if $\phi_1$ exceeds
$\phi_0+\big[1+2G(1-\phi_0)-\sqrt{\{1+2G(1-\phi_0)\}^2-4G\phi_0(1-\phi_0)(1+1/\chi)}\big]/(2G)$ (and $\phi_1\le1$); as $G\to0$ this tends to the
boundary $2\phi_0-\phi_0^2+\phi_0(1-\phi_0)/\chi$ of Eq.~\eqref{eq:snr}.
(iv) For $\gamma_{01}<0$ and $\phi_1<\phi_0$ the mixed term is positive and grows with $m$, so it can exceed the remaining terms; a numerical
instance with a positive definite covariance is given in the supplementary check script.
(v) $m$ enters Eq.~\eqref{eq:snrcorr} through $\rho m-1$ and $m$ whenever $\gamma_1\neq0$ or $\gamma_{01}\neq0$. \qed
```

Notes for the lead on the block: (1) item (iv) points to the check script (D4) instead of quoting its numbers, because the script is not a
`runs/` artifact; if the lead wants the instance in the paper it must be produced under `runs/` first or stated with symbols only.
(2) `\mathrm{Cov}` is written out because `paper2/main.tex` defines `\E` (line 22) and `\Var` (line 25) but no `\Cov`. (3) The boundary formula in the
appendix proof of (iii) may be cut if space is short; nothing else depends on it.

## R1.9 Script changes in r1 and output

Changes to `research/paper2/method/theory_check_2026-10-29.py` (same file, r0 checks kept unless listed):
- A6 (new): exact total variation under the changed-code label, and the context-only AUROC (R1.3).
- B3: comment and label say "algebra, shared code"; "valid" removed. B4 random-gate comment corrected ($\gamma_{01}=0.01$ in that check).
  B6 relabelled "Sherman-Morrison only". The Remark 2.4 check is relabelled B7.
- B8 (new, replaces the r0 Monte Carlo accuracy table): exact accuracy with Gaussian shared factors, summed over binomial retained counts.
- C2: the $\gamma=0$ check now compares the matched filter with a generic BFGS optimiser (r0 compared a vector with itself). Because this
  draws from the same random stream, the illustrative zero-weight counts of C2 differ from r0's; the checks are unaffected.
- D1, D3-D8 (new): pooled vs per-item counterexample; sympy identity for (2.5) and a second Monte Carlo point for Lemma 1 with
  $\gamma_{01}<0$; negative $\gamma_{01}$ below-diagonal example and the corrected (ii) scan; non-Gaussian SNR-vs-accuracy; corrected Prop. 3(a);
  $\xi=0$ when all $\mu(u)\le0$; the second critical point of $g$.
- The r0 check A4 of the loose changed-label bound cannot fail (red-team m8); it is kept for the record and superseded by A6.

Output of the r1 run (2026-10-29, 00:47 IST; CPU, about 25 s; GPU not used), verbatim. All values are toy or ILLUSTRATIVE, none from UniDisc:

```
theory_check_2026-10-29.py  seed=20261029  numpy=2.4.2

=== A. Proposition 1: detectability limit ===
[PASS] A1 |AUROC(f)-1/2| <= v - v^2/2 for random laws and scores  (max excess -2.18e-04)
[PASS] A1 AUROC(LR) >= AUROC(f) (LR is AUROC-optimal)  (max excess 0.00e+00)
[PASS] A1 AUROC(LR) >= 1/2 + v/2  (max shortfall 2.22e-16)
[PASS] A2 bound attained by the three-point example  (max |err| 2.2e-16)
  toy: V=3, L=8, items=40000, hit rate h=0.25; AUROC s.e. at 1/2 approx 0.0012
  Gibbs (law-invariant) corruption, hit label, pooled AUROC - 1/2: B_full (K=m) -0.0007, B_grp (K=2) -0.0009, q=B_grp-D -0.0005, u=-q +0.0005, -B_grp +0.0009, D -0.0004, random -0.0009
[PASS] A3 every within-modality score has pooled AUROC 1/2 (within 4 s.e.) under law-invariant corruption  (max |dev| 0.0009)
[PASS] A3 per-item mean AUROC of u has expectation 1/2  (0.5005 +/- 0.0014)
  uniform replacement (off-manifold), hit label, pooled AUROC: -B_grp 0.6111, u=-q 0.5978, random 0.5011
[PASS] A3 positive control: uniform replacement is detected (AUROC of -B well above 1/2)
  changed-code label, single-site resample: mean collision prob sbar=0.6272, exact TV=0.3396, bound=1.7648
[PASS] A4 exact TV <= sbar/(1-sbar) + h sbar/(1-h+h sbar)
  exact AUROC of the LR score (-pi_j(x_j | x_-j)) = 0.7202; limits [1/2 + v/2, 1/2 + v - v^2/2] = [0.6698, 0.7819]
[PASS] A4 exact AUROC(LR) within the two-sided bound of Prop. 1(a,b)
[PASS] A4 Monte Carlo AUROC(-pi) under changed label matches the exact value  (MC 0.7189 vs exact 0.7202)
[PASS] A4 same corruption, hit label: AUROC 1/2  (0.4974)
[PASS] A6 changed-code label: TV = (1/2) E sum pi|pi - sbar| [1/(1-sbar) + h/(1-h+h sbar)] (exact)  (0.339555 vs enumerated 0.339555)
  changed-code label: context-only score -s(o) (never reads the token value) has exact pooled AUROC 0.6597 (toy)
[PASS] A6 under the changed-code label the context law depends on Z: a context-only score has AUROC > 1/2
[PASS] A5 within-modality scores blind to caption-blind (P_a-invariant) corruption  (max |AUROC-1/2| 0.0007)
  per-token caption-blind Gibbs: cross-modal evidence mean on unhit tokens +0.0980, on hit tokens +0.0929 (s.e. 0.0016); small here because the unhit neighbours still carry the caption
  item-level independent redraw from P_a: max |AUROC-1/2| of within-modality scores 0.0030; cross-modal evidence mean on clean items +0.0986, on hit items -0.0006
[PASS] A5 item-level law-invariant redraw: within-modality scores at 1/2  (0.0030 vs 4 s.e. 0.0115)
[PASS] A5 item-level law-invariant redraw: cross-modal evidence on hit items falls to about 0
  cross-modal suspicion -(log p(v_j|v_-j,c) - log p(v_j|v_-j)) pooled AUROC 0.5187
[PASS] A5 a caption-using score detects what within-modality scores cannot

=== B. Proposition 2: correlated-token SNR of hard gating ===
[PASS] B1 Lemma 1 mean (Monte Carlo)  (MC 7.7016 vs 7.7000)
[PASS] B1 Lemma 1 variance (Monte Carlo)  (MC 144.238 vs 144.516)
[PASS] B2 Lemma 1 at gamma=0 equals theory.mean_var  (max rel diff 1.2e-13)
[PASS] B2 closed form at gamma=0 equals theory.special_case_inequality  (0 mismatches in 20000)
[PASS] B3 closed form (mu_c=0) has the sign of the direct SNR change (algebra, shared code)  (0 mismatches in 31434)
  ILLUSTRATIVE frontier (not estimates): m=1024, rho=0.1, mu=0.1, sigma2=sigma2_c=1, gamma_01=0, chi (red-team kappa)=0.1100
  phi0   g1=0        g1=0.0001   g1=0.001    g1=0.01     g1=0.05   
  0.01   0.1099      0.1080      0.0938      0.0436      0.0191    
  0.05   0.5293      0.5224      0.4666      0.2243      0.0961    
  0.1    none        0.9999      0.9265      0.4708      0.1941    
  0.2    none        none        none        none        0.3993    
[PASS] B4 closed-form boundary equals bisection on the direct SNR comparison  (max |diff| 3.6e-15)
[PASS] B4 boundary decreases with gamma_1 and stays above the diagonal phi1 = phi0
[PASS] B4 boundary tends to the diagonal as (rho m - 1) gamma_1 grows  (b(0.05) = 0.050000)
[PASS] B4 gamma_0 does not enter k0^2 Var S_0 - Var S_g when mu_c = 0  (40.780000 vs 40.780000)
[PASS] B4 a random gate (phi1 = phi0) lowers the SNR (grid of gamma_1, gamma_01 = 0.01)
[PASS] B5 large-m limit of the SNR depends only on the retained shares  (0.34227 vs 0.34227)
[PASS] B5 r* maximises the large-m SNR^2 over the retained-mass ratio  (max rel excess of grid max over g(r*) 1.7e-14)
[PASS] B6 Sherman-Morrison only: exchangeable Sigma^{-1} 1 is proportional to 1 (not an NP statement about the image)  (max cv 5.8e-13)
[PASS] B7 (Remark 2.4) Var_uncond - Var_cond = m0 k0 phi0 (mu^2 + g0 s2) + m1 k1 phi1 (muc^2 + g1 s2c)  (gap 8.73e-13)
  ILLUSTRATIVE accuracy, Gaussian shared factors, exact (m0=360, m1=40, mu=0.05, sigma2=sigma2_c=1, mu_c=0, g0=0.01, g1=0.05, g01=0):
    phi0  phi1   P(S>0) exact   Phi(SNR_uncond)  sign agrees with 'none' row
    0.0   0.0    0.665600       0.665600         -
    0.05  0.05   0.664687       0.664680         True
    0.05  0.5    0.668095       0.668085         True
    0.05  0.9    0.669891       0.669882         True
    0.2   0.9    0.666539       0.666501         True
[PASS] B8 Gaussian shared factors: sign of the accuracy change equals sign of the Phi(SNR) change (illustrative rows)

=== C. Proposition 3: reliability weights ===
[PASS] C1 Lemma 2 mean (Monte Carlo)  (MC 6.9406 vs 6.9500)
[PASS] C1 Lemma 2 variance (Monte Carlo)  (MC 97.504 vs 97.391)
[PASS] C1 Lemma 2 with w = I equals Lemma 1
[PASS] C2 gamma=0: matched filter mu(u)/sigma^2(u) attains the SNR found by a generic optimiser (BFGS)  (max rel loss 0.0e+00)
[PASS] C2 w >= 0 with exchangeable correlation: soft-threshold fixed point equals the QP optimum  (max rel diff 6.3e-16)
  ILLUSTRATIVE (n=60 tokens): gamma -> mean threshold xi, mean number of tokens given weight 0
    gamma=0.0    xi=0.0000  zero-weight tokens=0.9
    gamma=0.002  xi=0.0173  zero-weight tokens=0.2
    gamma=0.02   xi=0.0907  zero-weight tokens=4.3
    gamma=0.1    xi=0.1509  zero-weight tokens=17.3
[PASS] C2 threshold xi is 0 at gamma=0 and increases with gamma
[PASS] C3 nu = E w^2 / (E w)^2 on the p-value grid equals 2(2N+3)/(3(N+2)), N=10
[PASS] C3 nu = E w^2 / (E w)^2 on the p-value grid equals 2(2N+3)/(3(N+2)), N=1000
[PASS] C3 nu = E w^2 / (E w)^2 on the p-value grid equals 2(2N+3)/(3(N+2)), N=1000000
  clean-pair SNR^2 ratio (weights / none), conditional on weights, uniform p-value weights, by gamma_0:
    gamma_0=0.0    direct 0.75037  formula 0.75037
    gamma_0=0.001  direct 0.85890  formula 0.85890
    gamma_0=0.01   direct 0.97151  formula 0.97151
    gamma_0=0.1    direct 0.99711  formula 0.99711
[PASS] C3 clean-pair efficiency formula [(1-g)+g m]/[(1-g) nu + g m] matches the quadratic form

=== D. Revision r1 checks ===
  pooled class laws equal (TV = 0): pooled AUROC 0.500; per-item mean AUROC 0.625
[PASS] D1 Prop. 1 bounds the pooled AUROC only: TV = 0 with per-item mean AUROC != 1/2
[PASS] D3 sympy: (k0^2 V0 - Vg)/m - [LHS - RHS of (2.5)] == 0  (residual 0)
[PASS] D3 Lemma 1 by Monte Carlo at a second point (gamma_01 < 0)  (mean 3.4347 vs 3.4400; var 61.381 vs 61.221)
  gamma_01 = -0.045 (min eigenvalue 0.9500): SNR none 0.4892, gate (phi0, phi1) = (0.3, 0) 0.5080
[PASS] D4 with gamma_01 < 0 a gate that flags only clean tokens can raise the SNR (PSD example)
[PASS] D4 with gamma_1 in [-1/(m1-1), 0] and gamma_01 >= 0 no gate at or below the diagonal raises the SNR  (0 of 20000)
  rare non-Gaussian shared factor (gamma_1 = 0.074): SNR 1.081 -> 1.254; exact accuracy 0.9149 -> 0.9088
[PASS] D5 non-Gaussian correlation: gating raises the SNR of S but lowers P(S > 0)
  pi_1 in {0.3, 1}, mu_c = 0: optimal weights 0.1388 (pi_1 = 0.3) and 0.0e+00 (pi_1 = 1): a 0/1 gate with no oracle
[PASS] D6 hard gate optimal without an oracle when mu(u)_+/sigma^2(u) has one non-zero value
[PASS] D6 with two distinct non-zero values of mu(u)/sigma^2(u) the optimum is not a 0/1 gate
[PASS] D7 xi = 0 at gamma > 0 when every mu(u_k) <= 0
[PASS] D8 r = -mu/mu_c is a critical point with g = 0 (second critical point besides r*)  (max |g'|, g 1.4e-10)

SUMMARY: ALL CHECKS PASSED
```

## R1.10 Concerns after r1

1. The background sentence of R1.2 item 4 is usable only after a ledger ruling on the scope of must-not-claim 6; D0078 says "subject to
   must-not #6" but does not rule.
2. D0078 is timestamped 2026-10-29T01:05:00, while this machine's clock read 00:47 IST when the r1 check ran; the lead may want to check the
   ledger timestamp, since dating before M4 is part of the evidence.
3. Li et al. (arXiv 2102.08504) was read by the red team from a garbled PDF conversion; `citation-validator` must confirm the reference and
   the equation location before it is cited.
4. Proposition 2(iv) in R1.8 relies on a numerical instance that lives in the check script, not in `runs/`; the paper states it with symbols
   only, or the instance is regenerated under `runs/`.
