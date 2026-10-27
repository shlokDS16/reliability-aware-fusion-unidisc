```yaml
agent: method-architect
date: 2026-10-28
brief: Implementable specification of GATE (reliability-gated conditioning for unified multimodal masked discrete diffusion) with two-way evidence fusion (idea C) inside, for an Information Fusion research article; UniDisc 1.4B on one 12 GB laptop GPU.
sources_examined:
  - research/CONTRACT.md
  - research/paper2/IDEAS.md
  - research/paper2/ideation/IDEAS-RAW-2026-10-27.md (Idea 1 lines 117-209, Idea 3 lines 288-344)
  - research/paper2/ideation/RED-TEAM-2026-10-27.md (sections 0, Idea 1, Idea 3, overall)
  - research/paper2/ideation/NOVELTY-AUDIT-2026-10-27.md (summary, Idea 1, Idea 3)
  - research/paper2/style/IF-METHOD-ANATOMY-2026-10-27.md (sections 4-8)
  - research/paper2/probes/PROBE-REPORT-2026-10-27.md (all)
  - exp_p2/scoring.py (all), exp_p2/run_probe2.py (all)
coverage: >
  Read in full: CONTRACT, IDEAS, PROBE-REPORT, scoring.py, run_probe2.py. Read the GATE and two-way-fusion sections of the
  ideas, red-team and novelty files, and sections 4-8 of the IF anatomy. NOT read: the probe-1 driver (so how probe 1's
  null pass was built is inferred, see U3), runs/P2-PROBE-01/summary.json itself (numbers are taken from the probe report,
  which says it copies them from that file), runs/P2-SMOKE-02 (untracked, not in brief), the three cited papers
  themselves (their content is taken from the novelty audit, E2 there, E1 here), and the UniDisc code beyond the calls
  made in scoring.py.
claims:
  - statement: "For a Bayes-optimal absorbing-state denoiser, putting a gated token back to [MASK] gives exactly the marginal over its value (Proposition 1)."
    status: supported
    evidence: derivation, section 4.1 (follows from the MDM training objective; needs a perfect denoiser and a mask pattern in the training support)
    level: E0
    confidence: 0.9
  - statement: "The original Idea-1 score r = A - B cancels the token's own-context surprise and keeps only its cross-modal informativeness (Proposition 3)."
    status: supported
    evidence: derivation, section 4.3; matches red-team F1.1
    level: E0
    confidence: 0.85
  - statement: "Conformal risk control on clean items bounds the expected false-alarm proportion of a clean test item by alpha (Proposition 5)."
    status: supported
    evidence: section 5; standard result (reference to be verified by citation-validator)
    level: E0
    confidence: 0.85
  - statement: "Hypothesis-free intra-modal masked PMI detects corrupted image tokens on realistic corruptions (JPEG, noise, occlusion) above random and above max-probability uncertainty."
    status: unknown
    evidence: untested; probe 2 stopped at 20/200 items by a system crash (runs/P2-PROBE-02/HOLD.txt)
    level: E0
    confidence: 0.5
  - statement: "Gate-then-marginalise restores cross-modal verification under corruption more than a random gate of equal size."
    status: unknown
    evidence: untested
    level: E0
    confidence: 0.4
competing_explanations:
  - masking acts as regularisation, not detection (red-team M2): predicts equal gains from GATE on clean inputs and from a random gate
  - the detector is a texture/position-frequency detector (red-team M3): predicts clean-image false alarms clustered on textured or border tokens
  - any gain comes from the PMI null term alone, not the gate: predicts the no-gate PMI statistic equals the gated one
unknowns:
  - U1 whether probe 2's crash cause is resolved; every GPU item here is blocked by runs/P2-PROBE-02/HOLD.txt
  - U2 per-pass time in this scoring layout (estimates below divide the probe-1 median item time by its pass count)
  - U3 how probe 1's "image-masked null" was built (caption also masked or not); decides whether the null is cacheable per layout
  - U4 whether CLIP weights for CLIPScore and COCO instance annotations (hard negatives) are on disk
  - U5 whether UniDisc's final logits can be produced in fp32 (bf16 resolution versus the per-token margins)
  - U6 Omni-Diffusion 8B 4-bit per-pass time and memory (never measured)
next_test:
  hypothesis: "q (hypothesis-free intra-modal PMI) separates corrupted from clean image tokens on patch, JPEG q10 and noise sigma 0.1"
  intervention: "E1 below: complete probe 2 with the added B and D passes on 200 tuning items, after HOLD is lifted"
  primary_metric: "per-item AUROC of -q against the code-change map Z, averaged over items, per corruption"
  falsifier: "AUROC of -q not above the random score (paired bootstrap 95% CI includes 0) on all three realistic corruptions"
  gpu_hours: "about 0.75 (estimate, not measured)"
```

# GATE: method specification (for implementation and red team)

Status of this document: a specification and a set of predictions. **It contains no results.** Every number is one of:
(a) copied from `research/paper2/probes/PROBE-REPORT-2026-10-27.md` (marked "probe 1"), (b) a constant read from
`exp_p2/scoring.py` or `exp_p2/run_probe2.py` (marked with the file), (c) arithmetic derived from (a) or (b) (marked
"derived"), (d) a design choice to be frozen by `experiment-designer` (marked "design choice"), or (e) a GPU-hour
**estimate** (always marked "estimate"). Hand this to `red-team` before `lab-engineer` implements it (method-architect
hard rule). No ledger rows were added: the brief allows one new file only.

Contents: 0 one-paragraph method; 1 notation; 2 problem setup; 3 scores and their cost; 4 theory (propositions);
5 calibration; 6 algorithms; 7 two-way evidence fusion; 8 limiting cases and unit tests; 9 failure modes; 10 complexity;
11 what is new; 12 ablation map; 13 experiments E0-E8; 14 decisions needed.

---

## 0. The method in one paragraph

A unified masked discrete diffusion model (MDM) was trained to predict any masked token from any visible subset of a
text-image sequence, with [MASK] meaning "unknown". GATE uses this to treat the *input* tokens of a pair as sensors of
uneven reliability. (i) **Score**: each input token gets a masked log-likelihood score computed with its own modality's
other tokens as context and the other modality withheld (so the score does not depend on the hypothesis being tested).
(ii) **Gate**: a threshold set on clean data by conformal risk control flags tokens whose score is improbable for clean
inputs, with the expected false-alarm proportion bounded by a chosen alpha. (iii) **Fuse**: flagged tokens are put back
to [MASK] (marginalise, M) or re-infilled by the model (impute, I), and the downstream decision fuses two cross-modal
evidence statistics, text-given-image and image-given-text, each a full-mask pointwise mutual information, with weights
fitted on clean calibration pairs. One rule organises the design: **evidence that is tested must not be used to gate**
(section 4.4). Probe 1 shows that the full-mask PMI evidence is strong on clean COCO pairs; whether per-token scores
find corrupted tokens (the gate) is untested.

---

## 1. Notation (used everywhere below; the paper reuses it)

| Symbol | Meaning |
|---|---|
| $x=(t,v)$ | one pair: caption tokens $t=(t_1,\dots,t_n)$, image tokens $v=(v_1,\dots,v_m)$ |
| $n$ | caption length in text tokens; probe configs select captions with 5 to 32 tokens (`run_probe2.py`, `tok_range`) |
| $m$ | image tokens; $m=1024$ for a 32x32 VQ grid at 512 px (`scoring.py`, `L_I`) |
| $\mathcal V_T,\mathcal V_I$ | text vocabulary (ids 0..31999) and image vocabulary (16384 codes, ids 32001..48384) (`scoring.py`) |
| $\mathsf M$ | the mask token (id 32000) |
| $a,b$ | a modality and the other one, $a,b\in\{T,I\}$, $a\ne b$ |
| $x^a_S$ | tokens of modality $a$ at positions $S$; $x^a_{-S}$ the rest of modality $a$ |
| $\varnothing^a$ | all of modality $a$ masked |
| $p_\theta(x_j=\cdot\mid \tilde x)$ | the network's categorical at masked position $j$ for a partly masked input $\tilde x$, fp32 log-softmax of the logits restricted to the vocabulary of $j$'s modality (`scoring.py` convention) |
| $\tilde x$ | the observed (possibly corrupted) pair; $\tilde v$, $\tilde t$ its parts |
| $v^\circ$ | the tokenisation of the clean image; $Z_j=\mathbb 1[\tilde v_j\ne v^\circ_j]$ the corrupted-token label (as `core.corrupted_mask` in `run_probe2.py`) |
| $\Pi_K=\{S_1,\dots,S_K\}$ | a random partition of the positions of modality $a$ into $K$ groups (complementary masks); $k(j)$ the group of $j$ |
| $A_j,B_j,C_j,D_j$ | the four context levels of section 3.1 |
| $u_j$ | suspicion of token $j$ (higher = more suspicious), $u_j=-(\text{score})$ |
| $\alpha$ | target false-alarm level; $\tau_a$ the calibrated threshold of modality $a$ |
| $G$, $R$ | gated (flagged) set and reliable set, $R=\{1..m\}\setminus G$ (or the caption analogue) |
| $c$ | a candidate caption (verification or matching hypothesis); $c^+$ true, $c^-$ wrong |
| $E_{T\leftarrow I}, E_{I\leftarrow T}$ | the two directional evidence statistics of section 7 |
| $P$ | one network pass (one forward over the full sequence, one row of a batch) |
| $S_r, L$ | re-infill steps and number of re-infill samples |

Units: log-likelihoods in nats. "Pass" counts rows; `scoring.py` batches 4 rows per forward.

---

## 2. Problem setup

**Model.** A unified MDM with absorbing-state masking. Inference treats the network as a map from a partly masked
sequence to per-position categoricals. In `scoring.py` the forward is called with `sigma=None`, i.e. no time input
(E3 for the call; whether the network is truly time-independent is inferred, not verified).

**Input.** An observed pair $\tilde x=(\tilde t,\tilde v)$. Either part may be corrupted: image corruptions act on pixels
before tokenisation (JPEG, Gaussian noise) or on the token map (swap, patch occlusion) as in `run_probe2.py`; caption
corruptions are character-level typos or word substitutions (section 13).

**Tasks.**
- **T-det (token detection).** Rank or flag corrupted input tokens. Ground truth $Z$.
- **T-ver (verification).** Decide whether $\tilde t$ describes $\tilde v$. Paired form (probe 1): for each image, does
  the true caption score above a deranged wrong caption. Unpaired form: AUROC over matched versus mismatched pairs.
- **T-match (matching).** Choose the true caption among $N$ candidates (secondary).
- **T-rep (repair and generation, secondary).** Produce a repaired image (re-infill) or generate an image from a
  gated typo prompt.

**Two regimes, fixed per task before any run.**
- **R1, no trusted reference** (T-det, T-ver, T-match). Neither modality may be used to judge the other, because the
  cross-modal relation is what is being tested.
- **R2, trusted reference** (T-rep with a known clean caption; T2I where the image side is generated). The trusted
  modality may be used in the gate, like a predicted state in a Kalman innovation gate.

---

## 3. Scores and their cost

### 3.1 The four context levels

For token $j$ of modality $a$, observed value $x_j$, partition $\Pi_K$:

$$A_j=\log p_\theta(x_j\mid x^a_{-S_{k(j)}},\,x^b)\qquad\text{(own-modality context and the other modality)}$$
$$B_j=\log p_\theta(x_j\mid x^a_{-S_{k(j)}},\,\varnothing^b)\qquad\text{(own-modality context only)}$$
$$C_j=\log p_\theta(x_j\mid \varnothing^a,\,x^b)\qquad\text{(other modality only)}$$
$$D_j=\log p_\theta(x_j\mid \varnothing^a,\,\varnothing^b)\qquad\text{(nothing: the position marginal)}$$

Identity (exact, by subtraction):
$$\underbrace{A_j-D_j}_{\text{total PMI}}=\underbrace{(B_j-D_j)}_{\text{intra-modal PMI }q_j}+\underbrace{(A_j-B_j)}_{\text{cross-modal PMI given own context}}=\underbrace{(A_j-C_j)}_{\text{intra-modal PMI given }b}+\underbrace{(C_j-D_j)}_{\text{cross-modal PMI }w_j}.$$

### 3.2 Score menu (names match `run_probe2.py` where implemented)

| Name | Definition | Role | Implemented |
|---|---|---|---|
| s1 | $A_j$ | plain masked log-likelihood, other modality visible | yes (`s1`) |
| s_cm | $B_j$ | plain, other modality masked | yes (inside `r_original`, `s_cm`) |
| s2 | $A_j-C_j$ | prior-normalised given $b$ | yes (`s2`) |
| r_original | $A_j-B_j$ | original Idea-1 score; **control only** (Prop. 3) | yes |
| s3 | $1-\max_y p_\theta(y\mid\cdot)$ in the $A$ pass | model-uncertainty baseline (Dropout-Decoding-style ranking) | yes (`s3`) |
| **q** | $B_j-D_j$ | **hypothesis-free intra-modal PMI: primary gate statistic in R1** | needs $D$ |
| w | $C_j-D_j$ | cross-modal full-mask PMI per token: **decision evidence**, never a gate in R1 | needs $D$ |
| tot | $A_j-D_j=q_j+(A_j-B_j)$ | total PMI: gate statistic allowed in R2 only | needs $D$ |
| plain-B | $B_j$ | hypothesis-free plain likelihood (LR against a uniform alternative, Prop. 2) | yes |
| random | uniform | control | yes |

Suspicion is $u_j=-\text{score}$ for every likelihood-type score and $u_j=$ s3 for s3.

**Text side.** The same menu with $a=T$, $b=I$. The gating unit is a *word*: a SentencePiece word-initial token and
its continuation pieces; word score = minimum of its piece scores (design choice; sum as ablation), and gating a word
masks all its pieces.

### 3.3 Variants and their cost in passes

| Quantity | Passes | Depends on | Cache |
|---|---|---|---|
| $A$ over all $m$ image tokens, K masks | $K$ | image and caption | none |
| $B$ over all image tokens | $K$ | image only (caption masked) | per image, shared across candidate captions |
| $C$ for image tokens (image fully masked, caption visible) | 1 | **caption only**: the image is fully masked, so the logits do not see it; the image enters only through which entries are gathered | per caption, shared across all images and corruptions |
| $D$ for image or caption tokens (everything masked) | 1 | **layout only** (caption length $n$) | per $n$, at most 28 values for 5-32 tokens (derived) |
| $C$ for caption tokens (caption fully masked, image visible) | 1 | image | per image-caption-length |
| $A^T,B^T$ over caption tokens | $K_T=\min(K,n)$ each | caption (+ image for $A^T$) | $B^T$ per caption |
| leave-one-out (Salazar et al. PLL, arXiv:1910.14659) | $m$ image / $n$ text | | image: infeasible at $m=1024$ for a gate; text: feasible ablation |

Probe-1 facts bearing on the K-mask versus full-mask choice (probe 1, exploratory): text direction 0.730 with K=8 versus
0.943 with full masking; image direction 0.783 (K=8), 0.827 (K=2), 0.843 (full). Inference (not established; the
image-direction intervals overlap): accuracy rises as less of the scored modality is visible, consistent with own-modality
context diluting the cross-modal term. **Design consequence: the decision evidence uses full-mask scores ($C-D$), the
gate uses K-mask own-context scores ($B-D$).** They answer different questions: the gate asks "is this token consistent
with its own modality", the evidence asks "how much does the other modality support it".

Two further facts that cut cost: $C$ for image tokens does not depend on the image, and $D$ does not depend on content
at all. So the image-direction evidence for $N$ candidate captions costs $N$ passes in total, whatever the number of
images or corruption arms, and gating it costs nothing (drop terms).

---

## 4. Theory

Each statement lists its assumptions and when it is exact. The derivations are short and are meant for the paper's
Method section (one "analysis" subsection, as IF-METHOD-ANATOMY section 5 allows).

### 4.1 Proposition 1 (masking is marginalising for a Bayes-optimal denoiser)

*Assumptions.* (a1) The network equals the Bayes-optimal denoiser of the absorbing-state MDM objective: for every mask
pattern with positive training probability and every masked position $j$, $p_\theta(x_j\mid\tilde x)=p(x_j\mid x_{\text{unmasked}})$.
(a2) The gate pattern lies in the training support of mask patterns.

*Statement.* For any gate $G$ and any masked target position $j\notin G$ (e.g. a caption token),
$$p_\theta(x_j\mid x_R,\,x_G=\mathsf M)=\sum_{x_G}p(x_j\mid x_R,x_G)\,p(x_G\mid x_R)=p(x_j\mid x_R).$$

*Proof.* (a1) applied to the pattern "G and j masked", then the law of total probability. $\square$

*Where it stops being exact.* (i) Amortisation error: a real network approximates (a1), and structured patterns
(an 8x8 block plus a fully masked caption) are low-density under random per-token masking, so the error there is
expected to be larger (inference). (ii) Several targets at once: the full-mask score $\sum_j\log p_\theta(t_j\mid v_R)$
is a mean-field product, equal to $\log p(t\mid v_R)$ only if caption tokens are conditionally independent given $v_R$.
GATE never needs the exact joint; it needs the same approximation on both sides of every comparison, which holds
because every arm uses the same scoring rule. (iii) bf16 logits (section 9, F7).

### 4.2 Proposition 2 (which score is the likelihood-ratio test)

*Model.* Token $j$ is corrupted with prior probability $\rho$; a corrupted value is drawn from an alternative density
$h(\cdot)$ that does not depend on the context; an uncorrupted value follows the model's conditional given a context
$\kappa$ that is itself clean.

*Statement.* The posterior log-odds that $j$ is corrupted is
$$\log\frac{\rho}{1-\rho}+\log h(x_j)-\log p_\theta(x_j\mid\kappa),$$
so the Neyman-Pearson statistic is $\log p_\theta(x_j\mid\kappa)-\log h(x_j)$.
- $h$ uniform over $\mathcal V_a$ (token swap and patch occlusion with uniform random codes, as coded in `run_probe2.py`):
  the statistic is the plain likelihood ($B_j$ in R1). Plain-B is the optimal ranking for those corruptions.
- $h$ = the model's own position marginal, $h(x_j)=p_\theta(x_j\mid\varnothing)$ ("the corrupted token looks like a
  typical token, but ignores context"): the statistic is $q_j=B_j-D_j$. This is closer to JPEG and noise, which yield
  plausible codes, and to typos that yield common sub-word pieces.

*Exact when* the context is clean and the model is correct. *Approximate when* neighbours are corrupted (context
contamination, F4). This proposition is why the paper reports both plain-B and q, and why the primary statistic is
chosen on a tuning fold (section 13), not assumed.

### 4.3 Proposition 3 (the cancellation in the original score)

$r_j=A_j-B_j=\log\dfrac{p_\theta(x^b\mid x_j,\,x^a_{-S})}{p_\theta(x^b\mid x^a_{-S})}$ (Bayes, exact for a coherent model):
it is the evidence that token $j$ carries about the other modality. The own-context surprise of a corrupted token,
$\log p(x_j\mid x^a_{-S})$, appears in both $A_j$ and $B_j$ and cancels. A corrupted token is uninformative about $x^b$,
so $r_j\approx 0$; but most clean image tokens are also nearly uninformative about the caption (probe 1: mean
per-token image margin +0.005 nats between true and wrong caption). Hence $r$ can separate the two classes only through
the small cross-modal informativeness of clean tokens. When $x^b$ is the caption being generated (masked in both terms),
$A_j=B_j$ and $r_j\equiv 0$ exactly (red-team F1.1). **Prediction:** AUROC of $-r$ near 0.5 on token swap while
plain-B is high; r_original stays in the experiments only as this control.

### 4.4 The evidence-separation rule (design principle, follows from 4.3)

In R1 the gate may use only statistics computed with the other modality masked ($B$, $D$). Reason: the per-token
cross-modal terms ($w_j$, $A_j-B_j$) are the verification evidence. A gate that removed low-$w$ caption words would remove
exactly the words that make a wrong caption wrong, and would turn mismatches into matches. A gate that used $A$ with the
candidate caption visible would give each candidate a different evidence set, so candidates would no longer be compared
on the same image tokens. In R2 the reference is trusted and tot $=A-D$ (or $w$) is allowed: this is the innovation
gate of tracking, where a measurement that disagrees with a trusted prediction is rejected.

This rule is the paper's answer to the red team's cancellation issue: the corruption signal lives in the intra-modal
term, and the cross-modal term is kept for the decision rather than subtracted away.

### 4.5 Proposition 4 (when gating helps an additive evidence statistic)

*Model* (for the image-direction statistic $E_{I\leftarrow T}=\sum_{j\in R}w_j$, which is additive over tokens).
Paired comparison $\Delta_j=w_j(c^+)-w_j(c^-)$. Clean tokens: mean $\mu>0$, variance $\sigma^2$. Corrupted tokens:
mean 0, variance $\sigma_c^2$. Corruption fraction $\rho$; terms independent (approximation: neighbouring tokens are
correlated). The gate has false-alarm rate $\alpha$ on clean tokens and detection rate $\beta$ on corrupted ones.

*Statement.* The signal-to-noise ratio of $\sum_{j\in R}\Delta_j$ increases under gating iff
$$\rho\,\sigma_c^2\,(\beta-2\alpha+\alpha^2)\;>\;\alpha(1-\alpha)(1-\rho)\,\sigma^2 .$$

*Proof.* Before: $\mathrm{SNR}^2=\dfrac{m(1-\rho)^2\mu^2}{(1-\rho)\sigma^2+\rho\sigma_c^2}$. After:
$\dfrac{m(1-\alpha)^2(1-\rho)^2\mu^2}{(1-\alpha)(1-\rho)\sigma^2+(1-\beta)\rho\sigma_c^2}$. Compare and rearrange. $\square$

*Consequences (predictions).* (i) A necessary condition is $\beta>2\alpha-\alpha^2$. (ii) A random gate ($\beta=\alpha$)
gives $\beta-2\alpha+\alpha^2=\alpha^2-\alpha<0$ and always lowers SNR. (iii) An oracle gate ($\beta=1,\alpha=0$)
always helps when $\rho\sigma_c^2>0$. (iv) On a clean item ($\rho=0$) any gate with $\alpha>0$ lowers SNR slightly:
"GATE on clean inputs" should cost a little, never help, under mechanism M1. A gain on clean inputs would point to M2
(regularisation). The text-direction statistic is not additive over image tokens (the image enters as conditioning), so
for it this proposition gives only the qualitative ordering, oracle > GATE > none > random.

### 4.6 Proposition 5 (calibration guarantee): see section 5.

### 4.7 Proposition 6 (marginalise versus impute)

*Assumptions.* (a1), (a2), and re-infill samples $\hat v_G\sim p(v_G\mid v_R)$ exactly (the sampler draws from the
joint over $G$; finite $S_r$ adds factorisation error).

*Statement.* $\mathbb E_{\hat v_G}\big[p(c\mid v_R,\hat v_G)\big]=p(c\mid v_R)$: the I-arm is unbiased for the M-arm in
the probability domain. In the log domain the $L$-sample I-arm,
$\log\frac1L\sum_\ell p(c\mid v_R,\hat v^{(\ell)}_G)$, is biased downward (Jensen) with the gap going to 0 as
$L\to\infty$, and it adds sampling variance. *Prediction:* at equal expected value, M has the higher SNR and costs
$S_rL$ fewer passes, so M $\ge$ I on T-ver; I is kept because it yields a repaired image that can be shown and used
by downstream models that cannot read [MASK].

### 4.8 Proposition 7 (hypothesis leakage in re-infill)

If the gated tokens are re-infilled with the candidate caption $c$ visible, $\hat v_G\sim p(v_G\mid v_R,c)$, then
$$\mathbb E\big[\log p(c\mid v_R,\hat v_G)\big]=\log p(c\mid v_R)+\mathrm{KL}\big(p(v_G\mid v_R,c)\,\|\,p(v_G\mid v_R)\big)\;\ge\;\log p(c\mid v_R).$$
*Proof.* Bayes: $\log p(c\mid v_R,\hat v)=\log p(c\mid v_R)+\log\frac{p(\hat v\mid v_R,c)}{p(\hat v\mid v_R)}$; take the
expectation under $p(\cdot\mid v_R,c)$. $\square$ Every candidate gets a non-negative bonus equal to how strongly it
constrains the gated region, which need not favour the true caption. **Rule:** in R1, re-infill with the caption
masked; the caption-visible re-infill is run once as a leakage control (section 12).

---

## 5. Calibration (CFAR in conformal form)

**Data.** A calibration set $\mathcal D_{\rm cal}$ of $n_{\rm cal}$ clean pairs (tokenised clean image, its own COCO
caption), disjoint by image id from the tuning and test sets. Design choice: $n_{\rm cal}=500$ (finite-sample slack
$1/(n_{\rm cal}+1)\approx0.002$, derived).

**Per-item loss.** For item $i$ with $m_i$ gating units (image tokens, or caption words) and suspicions $u_{ij}$, the
false-alarm proportion at threshold $\tau$ is $L_i(\tau)=\frac1{m_i}\sum_j\mathbb 1[u_{ij}>\tau]\in[0,1]$, non-increasing in $\tau$.

**Threshold (conformal risk control, token-level gate).**
$$\hat\tau_a=\inf\Big\{\tau:\ \frac{n_{\rm cal}}{n_{\rm cal}+1}\,\widehat R(\tau)+\frac1{n_{\rm cal}+1}\le\alpha\Big\},\qquad \widehat R(\tau)=\frac1{n_{\rm cal}}\sum_{i}L_i(\tau).$$

**Proposition 5 (guarantee).** If the calibration items and a clean test item are exchangeable *as items*, then
$\mathbb E\,[L_{\rm test}(\hat\tau_a)]\le\alpha$: the expected false-alarm proportion on a clean test input is at most
$\alpha$. Source: Angelopoulos et al., "Conformal Risk Control" (ICLR; arXiv id to be checked by `citation-validator`
before it is cited, it is from memory). Tokens inside an item need not be exchangeable or independent; positions may
have different score distributions. Ties (bf16, F7) are broken by an independent uniform jitter below the score
resolution, which keeps the guarantee.

**Item-level alarm (optional, family-wise).** Score each item by $M_i=\max_j u_{ij}$ and take $\hat\tau^{\max}_a$ as the
$\lceil(n_{\rm cal}+1)(1-\alpha)\rceil$-th smallest $M_i$. Then $\Pr(\text{any false alarm on a clean test item})\le\alpha$
(split conformal). Used to answer "is this input corrupted at all"; it is far more conservative per token.

**Per-class (Mondrian) variant.** Run the same rule separately within position classes (image border ring versus
interior) or token classes (word-initial versus continuation; frequency tercile). Guarantee holds within each class.
Use it if the clean false-alarm map in E2 is not spatially flat (failure mode F6).

**Per modality.** Separate thresholds $\hat\tau_I$ and $\hat\tau_T$. When both modalities are gated, the bound holds per
modality; no joint correction is needed because the two losses are reported separately.

**What is not guaranteed.** (i) Power: nothing bounds detection on corrupted inputs (CFAR controls false alarms under H0
only). (ii) False alarms on the *clean tokens of a corrupted item*: the guarantee is for clean items; neighbours of
corrupted tokens see contaminated context and can be flagged more often (swamping, F4). Report this rate. (iii) Any
shift between calibration and test (another dataset, caption style, resolution, tokenizer) voids the bound; E2 measures
the size of the violation under a deliberate within-COCO shift. (iv) Iterated gating (re-score after masking) breaks
monotonicity in $\tau$, so CRC does not apply; it is an ablation with empirical FAP only (a Learn-then-Test calibration
would restore a high-probability bound; not planned). (v) Choosing the statistic, $K$ or $\alpha$ by looking at the
calibration or test items breaks exchangeability; they are chosen on the tuning fold.

Design choices: $\alpha\in\{0.01,0.05,0.10\}$ reported, $\alpha=0.05$ primary. On a clean 1024-token image that is
about 51 tokens expected to be flagged (derived), which sets the size of the random-gate control.

---

## 6. Algorithms (each builds on the previous ones)

Conventions: all passes go through `masked_logprobs(forward_logits, base, specs)` of `exp_p2/scoring.py`; a `Spec(pos,
lo, hi, extra)` masks `pos` (scored) and `extra` (masked, not scored). Line numbers are for the paper's algorithm boxes.

### Algorithm 1: MaskedScore (primitive)
Input: sequence $x$ (layout of `UniScorer.build`), target positions $P$, extra masked positions $X$, modality vocabulary
$[lo,hi)$. Output: $\log p_\theta(x_j\mid\cdot)$ and $\max_y p_\theta(y\mid\cdot)$ for $j\in P$.
1. $\tilde x\leftarrow x$; $\tilde x_P\leftarrow\mathsf M$; $\tilde x_X\leftarrow\mathsf M$.
2. $\ell\leftarrow$ logits of $\tilde x$ (one pass, batched with others).
3. For $j\in P$: $\lambda_j\leftarrow\mathrm{logsoftmax}_{fp32}(\ell_{j,[lo,hi)})$; return $\lambda_j[x_j-lo]$ and $\exp\max\lambda_j$.
Cost: 1 pass. Already implemented as `masked_logprobs` + `gather_true`.

### Algorithm 2: ReliabilityScores (uses 1)
Input: pair $(t,v)$, modality $a$, $K$, seed, regime. Output: $A,B,C,D$ vectors for modality $a$ and the suspicion $u$.
1. Draw partition $\Pi_K$ of the positions of $a$ (`core.complementary_groups`, seed $(\text{SEED},i,99)$ as in probe 2).
2. For $k=1..K$: $B_{S_k}\leftarrow$ MaskedScore$(x,\ S_k,\ X=\text{positions of }b)$. [hypothesis-free]
3. If regime = R2 or the run is a detection study: for $k=1..K$: $A_{S_k}\leftarrow$ MaskedScore$(x,\ S_k,\ X=\varnothing)$.
4. $C\leftarrow$ MaskedScore$(x,\ \text{all of }a,\ X=\varnothing)$; reuse from cache keyed by the content of $b$.
5. $D\leftarrow$ MaskedScore$(x,\ \text{all of }a,\ X=\text{all of }b)$; reuse from cache keyed by layout $n$.
6. Gate statistic: R1: $u_j\leftarrow-(B_j-D_j)$ (or $-B_j$ if plain-B wins on the tuning fold). R2: $u_j\leftarrow-(A_j-D_j)$.
7. Text side: aggregate $u$ to words, $u_{\rm word}=\max$ over its pieces (= minimum score).
Cost: R1 $K$ passes (+1 for $C$, +1 for $D$, both cached); R2 $2K$ (+ caches).

### Algorithm 3: CalibrateThreshold (uses 2)
Input: $\mathcal D_{\rm cal}$, modality $a$, regime, $\alpha$, optional class map. Output: $\hat\tau_a$ (per class).
1. For each clean item $i$: $u_i\leftarrow$ ReliabilityScores$(t_i,v_i,a)$; add jitter $\epsilon_{ij}\sim U(0,10^{-6})$ (design choice; below score resolution).
2. Build $\widehat R(\tau)$ on the sorted pooled suspicions (it is a step function; evaluate at every distinct value).
3. Return the smallest $\tau$ with $\frac{n}{n+1}\widehat R(\tau)+\frac1{n+1}\le\alpha$ (per class if Mondrian).
4. Store $\hat\tau_a$ with the hash of the calibration id list, $K$, seed and statistic name. Thresholds are frozen
   before any test item is scored.
Cost: $n_{\rm cal}$ calls of Algorithm 2; no extra passes.

### Algorithm 4: Gate (uses 2, 3)
Input: observed pair, modality $a$, $\hat\tau_a$. Output: $G_a$, $R_a$, $u$.
1. $u\leftarrow$ ReliabilityScores$(\tilde t,\tilde v,a)$ (same $K$, seed rule, statistic as calibration).
2. $G_a\leftarrow\{j:u_j>\hat\tau_a\}$; $R_a\leftarrow$ complement.
3. (Ablation only) iterate once: re-run step 1 with $G_a$ added to the extra-masked set $X$ in every pass; $G_a\leftarrow G_a\cup\{j\in R_a:u_j'>\hat\tau_a\}$.
Cost: as Algorithm 2 (+K for the iteration).

### Algorithm 5: GatedEvidence, marginalise arm M (uses 1, 4)
Input: image $\tilde v$ with gate $(G_I,R_I)$, candidate caption $c$ with gate $(G_T,R_T)$. Output: $E_{T\leftarrow I}(c)$, $E_{I\leftarrow T}(c)$.
1. Text direction: $\lambda^{T}\leftarrow$ MaskedScore$(x=(c,\tilde v),\ P=\text{caption }R_T,\ X=G_T\cup G_I)$ [caption fully masked, gated image tokens masked].
2. $\lambda^{T,0}\leftarrow D^T$ restricted to $R_T$ (cache, layout $n$).
3. $E_{T\leftarrow I}(c)\leftarrow\sum_{j\in R_T}(\lambda^T_j-\lambda^{T,0}_j)$.
4. Image direction: $\lambda^{I}\leftarrow$ MaskedScore$(x=(c,\cdot),\ P=\text{all image},\ X=G_T)$ (cache per gated caption; image-independent).
5. $E_{I\leftarrow T}(c)\leftarrow\sum_{j\in R_I}\big(\lambda^I_j[\tilde v_j]-D^I_j[\tilde v_j]\big)$.
6. Return both, plus $|R_T|$, $|R_I|$ for normalised variants.
Cost per candidate: 1 pass (step 1) + 1 pass (step 4, cached per caption) ; gating the image direction costs 0 passes.
Note: with no caption gate (the image-corruption experiments), steps 2 and 4 are unchanged from probe 1's a_full_pmi and
b_full except that gated image tokens are masked (step 1) or dropped (step 5).

### Algorithm 6: ReInfill, impute arm I and hybrid M+I (uses 1, 4)
Input: $\tilde v$, $G_I$, regime, $S_r$, $L$, order rule, $\kappa$. Output: $L$ repaired images $\hat v^{(\ell)}$ and, for M+I, a residual gate.
1. For $\ell=1..L$:
2. $y\leftarrow\tilde v$ with $y_{G}\leftarrow\mathsf M$; caption: masked (R1) or the trusted caption visible (R2).
3. For $s=1..S_r$: $U\leftarrow$ still-masked positions of $G$; $k_s\leftarrow\lceil |U|/(S_r-s+1)\rceil$.
4. One pass: $\pi_j\leftarrow p_\theta(\cdot\mid y)$ for $j\in U$.
5. Choose $k_s$ positions of $U$ by the order rule (max-probability primary; random as ablation); sample $y_j\sim\pi_j$ (temperature 1); record $\pi_j(y_j)$.
6. $\hat v^{(\ell)}\leftarrow y$.
7. M+I: keep $\hat v_j$ where the recorded $\pi_j(y_j)\ge\kappa$, re-mask the rest (residual gate $G'$).
Cost: $S_rL$ passes per image (R1 re-infill is shared by all candidate captions). Design choices: $S_r=16$, $L=1$,
$\kappa=0.5$, unguided sampler; $L=4$, $S_r\in\{8,32\}$ and the guided sampler (2 passes per step) are ablations.
I-arm evidence: Algorithm 5 on $\hat v$ with $G=\varnothing$; for $L>1$ combine by log-mean-exp of $E_{T\leftarrow I}$ (Prop. 6).

### Algorithm 7: GATE for verification and matching (R1; composes 2-6 and the fusion of section 7)
Input: $\tilde v$, candidates $\{c_1..c_N\}$, frozen $\hat\tau_I,\hat\tau_T$, fusion weights $\hat\omega$, arm $\in\{$none, M, I, M+I$\}$.
Output: a score per candidate; decision (argmax, or threshold for unpaired verification).
1. $G_I\leftarrow$ Gate$(\tilde v, I)$ with the caption masked (once per image; hypothesis-free).
2. For each $c_k$: $G_T(c_k)\leftarrow$ Gate$(c_k, T)$ with the image masked (once per caption; cacheable).
3. If arm uses I: $\hat v\leftarrow$ ReInfill$(\tilde v,G_I,\text{R1})$ (once per image).
4. For each $c_k$: $(E_{T\leftarrow I},E_{I\leftarrow T})\leftarrow$ GatedEvidence on $\tilde v$ (M), $\hat v$ (I) or $\hat v$ with $G'$ (M+I).
5. $F(c_k)\leftarrow$ Fuse$(E_{T\leftarrow I},E_{I\leftarrow T};\hat\omega)$ (section 7).
6. Return $\{F(c_k)\}$; decide.
Cost: $K$ (image gate) $+\ N K_T$ (caption gates, cached per caption) $+\ S_rL$ (I only) $+\ 2N$ (evidence; the
image-direction half is cached per caption) passes. Relative to the ungated two-way baseline ($2N$ passes),
GATE-M adds $K$ passes per image when only the image is gated.

### Algorithm 8: GATE for repair and generation (R2)
Input: corrupted $\tilde v$ and trusted caption $c$ (repair), or a corrupted prompt $\tilde t$ (T2I). Output: repaired image or generated image.
1. Repair: $G_I\leftarrow$ Gate with statistic tot (caption visible, R2 threshold calibrated with the same statistic); $\hat v\leftarrow$ ReInfill$(\tilde v,G_I,\text{R2})$; decode with the VQ decoder (`UniScorer.decode`).
2. T2I: $G_T\leftarrow$ Gate$(\tilde t,T)$ with the image absent (all image tokens masked, which is the generation start state, so this is hypothesis-free); arm M: generate with the gated words left as [MASK] in the prompt (the sampler must not unmask them; it unmasks only image positions); arm I: re-infill the gated words first (text re-infill with the caption's own context), then generate.
3. Known limitation: the masked span keeps the typo's piece count, so re-infill must produce a word of that many pieces (F11). Ablation: try lengths $\{k-1,k,k+1\}$ and keep the most likely (3x cost).

---

## 7. Two-way evidence fusion (idea C inside GATE)

**What is fused.** For candidate $c$: $E_{T\leftarrow I}(c)$ (text-given-image PMI) and $E_{I\leftarrow T}(c)$
(image-given-text PMI), both from Algorithm 5 with the same gates.

**Why not plain inverse-variance weighting.** Inverse-variance weighting is the best linear unbiased combiner of
independent unbiased estimates *of the same quantity*. Here: (i) the two statistics estimate different quantities on
different scales (a sum over about $n$ caption terms versus about $m=1024$ image terms, each a mean-field product, not the
symmetric sequence PMI); (ii) they come from one network on one pair, so their errors are correlated (red-team F3.1);
(iii) with full-mask scoring there is no Monte Carlo variance at all: both statistics are deterministic for a given
input, so per-mask sampling variance is zero and the original idea-C weights are undefined. The variance that matters
for a decision is the between-item variance of the statistic under each hypothesis.

**Fusion rule (primary): Fisher's linear discriminant on paired differences.**
For paired decisions, $\Delta=(\Delta_T,\Delta_I)^\top$ with $\Delta_d=E_d(c^+)-E_d(c^-)$. On the calibration pairs
(clean images, true caption versus one deranged wrong caption, disjoint from test):
$$\hat\omega=\hat\Sigma_\Delta^{-1}\hat\mu_\Delta,\qquad F(c)=\hat\omega_T E_{T\leftarrow I}(c)+\hat\omega_I E_{I\leftarrow T}(c).$$
This is the optimal linear rule for Gaussian $\Delta$ with known moments; it uses the correlation between directions
and their different scales; it reduces to inverse-variance weighting exactly when $\Sigma_\Delta$ is diagonal and the two
directions have equal mean shifts. Two parameters (up to scale) are fitted once, on clean calibration pairs, and frozen
for all arms and corruptions (no refit per corruption, which would tune on the test condition).

**Reported alternatives (ablation).** (a) Plain sum. (b) Stouffer: standardise each direction by its mean and SD on
calibration mismatches, then $(z_T+z_I)/\sqrt{2+2\hat r}$ with the calibration correlation $\hat r$. (c) Inverse-variance
with between-item variances (the idea-C rule, labelled as a special case). (d) Each single direction at equal total
passes (red-team requirement for idea C): the text direction given $2\times$ its passes (two independent partitions for
K-mask; for full-mask there is nothing to repeat, so the equal-pass control is the single direction plus $K$ extra
passes spent on a second text-direction variant, a_pmi with K=8). (e) An oracle refit of $\hat\omega$ on each test
condition (upper bound, labelled).

**Gate-aware down-weighting (ablation).** When the gate removes a fraction $g=|G_I|/m$ of image tokens, the text
direction loses conditioning information. Rule: $\omega_T(g)=\hat\omega_T(1-g)$ (design choice, untested). Limit: at
$g=1$ the text direction is exactly 0 (section 8, L2) and the rule returns the image direction only.

**Matching ($N$-way).** Argmax of $F$. Note that for a fixed image the null term $D^I$ is identical for all
candidates, so the image direction's PMI and raw ranking coincide; for the text direction the null term differs per
caption. Probe 1 is consistent with this: PMI raised the text direction from 0.943 to 0.990 (full mask), and the image
direction was not PMI-normalised.

**Headroom problem (must be fixed before the fusion claim is tested).** On clean probe-1 pairs, a_full_pmi alone and
a_full_pmi + b_full are both 0.990. At that ceiling neither fusion nor gating can show a gain on clean pairs, and a
modest corruption may not move it. E3 therefore uses hard negatives and reports unpaired AUROC as well (section 13).

---

## 8. Limiting cases and the unit test for each

All tests use a fake network on a small synthetic joint so that every quantity has a brute-force value. The joint:
$n=3$ text tokens and $m=4$ image tokens over vocabularies of size 3 each, given by an explicit probability table
(enumerable: $3^7$ states). The "perfect denoiser" fake returns the exact conditional given the unmasked tokens.
`masked_logprobs` already takes a logits callable (`scoring.py` docstring says it is unit-tested with a fake network),
so the tests plug into it directly. Tolerance $10^{-9}$ in fp64.

| # | Case | What must hold | Unit test |
|---|---|---|---|
| L1 | No corruption | Realised FAP over clean test items $\le\alpha$ in expectation; GATE-M on a clean item changes the decision statistic about as much as a random gate of equal size (Prop. 4 iv) | Synthetic exchangeable item scores (heterogeneous per position): 2,000 repetitions of calibrate-then-test with $n_{\rm cal}=100$; mean realised FAP $\le\alpha+$ 3 Monte Carlo SE |
| L2 | All corrupted / $\alpha\to1$ ($G=$ all of $a$) | Image fully masked: the text direction equals its null, $E_{T\leftarrow I}=0$ exactly; image direction sum is empty, $E_{I\leftarrow T}=0$; fused decision has no image evidence | Fake network: gate everything, assert both statistics are exactly 0 and the fused score of every candidate is equal |
| L2b | All corrupted, detection | Intra-modal context is all corrupt, so $q$ loses power as $\rho\to1$ (prediction, not a test of the code) | Synthetic: corrupt every token of the toy joint; assert AUROC of $q$ is undefined (single class) and the code returns NaN, as `run_probe2.py` does for fewer than 5 corrupted or clean tokens |
| L3 | Uninformative other modality ($b$ masked, or $b$ independent of $a$ in the joint) | $A=B$ hence r_original $\equiv0$; $C=D$ hence $w\equiv0$; LDA weight of that direction $\to0$ | Fake network with an independent joint $p(t)p(v)$: assert $A=B$, $C=D$ elementwise; assert fitted $\hat\omega_d\approx0$ for the uninformative direction on 1,000 synthetic pairs |
| L4 | Perfect denoiser | Prop. 1 exact; Prop. 6 unbiasedness in the probability domain; Prop. 7 identity | (a) prediction with $G$ masked equals the brute-force marginal; (b) average of $p(c\mid v_R,\hat v)$ over all $\hat v$ weighted by $p(\hat v\mid v_R)$ equals $p(c\mid v_R)$; (c) $\mathbb E\log p(c\mid v_R,\hat v)-\log p(c\mid v_R)$ equals the KL, enumerated |
| L5 | Uniform predictions | All likelihood scores equal $-\log|\mathcal V_a|$; AUROC 0.5; with jittered ties the gate is a random gate with expected FAP $\approx\alpha$ | Fake network returning zeros as logits: assert AUROC $=0.5\pm$ MC error and realised FAP within MC error of the CRC bound |
| L6 | One mask ($K=1$) | For $A$: $A=C$, so s2 $\equiv0$. For $B$: $B=D$, so $q\equiv0$ (no own context: degenerate gate) | Assert identities; the code must refuse $K=1$ for the gate statistic |
| L7 | All masks ($K=m$) | $A$ and $B$ become leave-one-out pseudo-log-likelihoods | Assert equality with a direct per-position loop |
| L8 | $\alpha=0$ | $G=\varnothing$; every arm equals the no-gate baseline bit for bit | Assert identical statistics |
| L9 | Leakage control | Caption-visible re-infill adds $\ge0$ to every candidate's expected text-direction score (Prop. 7) | Enumerated on the toy joint |
| L10 | Cache validity | $C^I$ is independent of image content and $D$ of all content | On UniDisc, once, CPU or GPU: two different images with the same caption give bitwise-equal $C^I$ logits; two different pairs with the same $n$ give equal $D$. On the fake network: assert by construction |

L10 is the only test that touches the real model; it costs 4 passes and should run inside the first E1 chunk.

---

## 9. Failure modes (what can go wrong, how it shows, what the spec does about it)

| ID | Failure | Signature | Mitigation in this spec |
|---|---|---|---|
| F1 | Cancellation in r = A − B (red-team F1.1) | AUROC of r near 0.5 while plain-B is high | Prop. 3; r kept as a labelled control only |
| F2 | Gating the evidence | Wrong captions accepted after gating; verification accuracy falls on mismatched pairs | Evidence-separation rule (4.4): R1 gates use $B,D$ only; E4 measures gate-induced false acceptance |
| F3 | Hypothesis leakage in re-infill | Caption-visible re-infill raises scores of wrong captions | Prop. 7; R1 re-infill masks the caption; leakage arm as control |
| F4 | Context contamination (masking and swamping) at high corruption fraction or for spatially coherent corruption (JPEG blocks support each other) | AUROC falls with severity; clean neighbours of corrupted regions are flagged | Severity sweep in E1; report FAP on clean tokens of corrupted items; iterated gate as ablation |
| F5 | Label ambiguity: a changed VQ code is not necessarily a meaningful corruption (noise and JPEG flip many codes to near-equivalent ones) | AUROC ceiling well below 1 on noise/JPEG even for a good detector | Secondary graded label: codebook-embedding distance $\|e(\tilde v_j)-e(v^\circ_j)\|$; AUROC on the upper half of that distance |
| F6 | The detector is a texture or position-frequency detector (red-team M3) | Clean-image false alarms cluster on borders or textured regions | Spatial FAP map on clean calibration items (E2); Mondrian calibration by position class |
| F7 | bf16 resolution. Logits are bf16; for a logit in [8, 16) the bf16 spacing is $2^{-4}=0.0625$ (derived from bf16's 7 explicit mantissa bits), coarser than the probe-1 per-token image margin (+0.005 nats). The actual logit magnitudes are not measured (U5) | Many tied scores; unstable per-token ranks | Jitter tie-breaking keeps the guarantee; ask `lab-engineer` whether the final projection can run in fp32; per-token *cross-modal* image terms are never thresholded (they enter only as sums) |
| F8 | Ceiling: clean full-mask PMI accuracy 0.990 (probe 1) | No measurable corruption-induced drop; no room for gating | Hard negatives, unpaired AUROC, headroom check before E3's main contrast (red-team probe 3 rule) |
| F9 | Exchangeability fails (calibration ≠ test distribution) | Realised FAP above $\alpha$ | E2 shift test; claim the bound only for the stated split |
| F10 | Gate patterns are low-density mask patterns (structured blocks plus fully masked caption) | M arm worse than predicted; oracle M below oracle I | Report oracle-gate M versus I; note under Prop. 1 (a2) |
| F11 | Text masking keeps piece count; typos change it | Text re-infill produces wrong-length words | Length-search ablation; text-side M arm does not need re-infill |
| F12 | Machine instability: two 0x116 crashes during probe 2 with whole-GPU memory jumping to 12,087 MiB (probe report); cause unknown | Crash, lost chunk | No GPU work until HOLD is lifted; keep the probe-2 safeguards (75% PyTorch cap, per-item stop above 10,750 MiB, `run_probe2.py`); chunks resumable |
| F13 | Forking paths (red-team F1.4) | Many arms, statistics, $\alpha$, $K$ | One primary contrast and family declared in section 13; statistic and $K$ chosen on the tuning fold only |
| F14 | Fusion premise (red-team F3.1) | Inverse-variance weights put almost all weight on one direction | Section 7: LDA with correlation; IV only as a labelled special case |
| F15 | One small backbone (red-team X1, X3) | Reviewer asks for a second model | E7 measure-first protocol on Omni-Diffusion 8B 4-bit; claim scope stated as "one 1.4B model" if E7 fails |

---

## 10. Complexity

Let $P$ be the time of one pass (one row, ~1.1k tokens: about 1024 image tokens plus the caption and layout tokens,
derived from `UniScorer.build`). Estimate of $P$: probe 1's median 7.0 s per item over 58 passes gives about 0.12 s per
pass including overhead (derived; this is an **estimate**, U2). Memory: the probe-1 and probe-2 passes at batch 4 peaked
at 8.2 GB PyTorch allocation (probe report). One fp32 matrix of image log-probabilities $[1024,16384]$ is 64 MiB
(derived); GATE holds at most two ($C^I$, $D^I$) per item. Time is linear in passes; no step is quadratic in $m$ beyond
the network's own attention.

| Arm (per image, $N$ candidate captions, image gated only) | Passes | Extra over ungated two-way baseline |
|---|---|---|
| Ungated two-way baseline (probe-1 a_full_pmi + b_full) | $2N$ (+ cached nulls) | 0 |
| GATE-M | $K+2N$ | $K$ |
| GATE-I | $K+S_rL+2N$ | $K+S_rL$ |
| GATE-M+I | $K+S_rL+2N$ | $K+S_rL$ |
| Random / oracle gate (controls) | $2N$ (gate given) | 0 |
| Dropout-Decoding-style (uncertainty ranking from an $A$ pass, ensemble of $E$ drop sets) | $K+2NE$ | $K+2N(E-1)$ |
| Caption gate added | $+NK_T$ (cached per caption) | $+NK_T$ |
| Detection study (A and B both) | $2K+1$ | n/a |

With the design choices $K=8$, $N=2$, $S_r=16$, $L=1$: baseline 4 passes, GATE-M 12, GATE-I 28 (derived). GATE-M
therefore costs about 3x the baseline per image for paired verification and tends to $1+K/(2N)$ times as $N$ grows.
Per-image time at the $P$ estimate: GATE-M about 1.4 s, GATE-I about 3.4 s (estimates). Gradients: none (DiSP needs
backward passes; GATE does not).

---

## 11. What is new relative to the closest work

Content of the three papers is taken from the novelty audit (E2 there); not re-read here.

| | Dropout Decoding (arXiv 2412.06474) | DiSP (arXiv 2602.22246) | UniDisc's corrupted-pair repair (arXiv 2503.20853, App. G.1) | GATE |
|---|---|---|---|---|
| Model class | autoregressive LVLM | diffusion VLMs (LLaDA-V, LaViDa) with continuous projector inputs | unified discrete MDM | unified discrete MDM |
| What is masked | continuous visual tokens | continuous visual embeddings replaced by the mask embedding | random subset of both inputs | scored input tokens of either modality |
| How tokens are chosen | epistemic uncertainty via projection to text space | Fisher-Jacobian saliency, gradient-based | at random | the model's own masked likelihood of the observed token, hypothesis-free (Prop. 2, rule 4.4) |
| Threshold | none calibrated | none calibrated | none | conformal risk control on clean data, expected false-alarm proportion $\le\alpha$ |
| Use of masked tokens | ensemble vote for decoding | rewrite responses, then fine-tune | re-unmask, select best of $n$ by own likelihood | marginalise (Prop. 1) or impute (Prop. 6), compared at matched passes |
| Text-side inputs | no | no | captions corrupted by an LLM, qualitative | yes (typos, word-level gate) |
| Evidence | hallucination benchmarks | backdoor attack success rate, MMMU | qualitative figure | detection AUROC against known corrupted-token maps, calibrated FAP, verification/matching accuracy, repair metrics |
| Fusion | none | none | none | two-way cross-modal evidence fused with LDA weights |

**The delta in one sentence (for the Introduction).** A unified MDM can gate its own input evidence: a hypothesis-free
masked PMI score, a clean-calibrated false-alarm guarantee, a proof that re-masking marginalises for a Bayes-optimal
denoiser, the evidence-separation rule that prevents gating from destroying the cross-modal signal, and a measured
comparison of marginalising and imputing. Novelty audit verdict: narrow delta, confidence 0.60; the cluster is active
and a concurrent "input remasking" paper is possible.

**Baselines built from these works (labelled adaptations, not reimplementations).** "DD-style": rank image tokens by
s3 (model uncertainty) from the same $A$ passes, mask the top $|G|$ (equal size), ensemble over $E=3$ random halves of
that set, average the evidence. "UniDisc-G.1-style": random gate of equal size followed by re-infill (I-arm with a
random $G$). DiSP is not run (gradient-based, continuous inputs); it is discussed.

---

## 12. Ablation map

| Ablation | Component removed or changed | Theory prediction |
|---|---|---|
| No gate | all of GATE | baseline; under corruption below GATE-M if Prop. 4 condition holds |
| Random gate, equal size (3 seeds) | the score | Prop. 4 (ii): lowers or leaves SNR; below no gate on average |
| Oracle gate ($G=\{Z=1\}$) | detection error | Prop. 4 (iii): upper bound for M; gap to GATE = cost of detection error |
| GATE on clean inputs | corruption | Prop. 4 (iv): small loss, never a gain under M1; a gain means M2 |
| s3 / DD-style ranking | likelihood of the observed token (uses uncertainty instead) | weaker than plain-B on swap/patch (Prop. 2: s3 ignores the observed value) |
| r_original as gate | hypothesis-free intra-modal term | Prop. 3: near-random detection |
| A-based gate in R1 (caption visible) | evidence separation | gate differs per candidate; mismatched pairs gain spuriously (F2) |
| plain-B versus q | the null term $D$ | Prop. 2: plain-B better on swap/patch, q better on JPEG/noise/typos |
| $K\in\{2,4,8,16\}$ | own-context fraction | more context helps detection until context contamination dominates (F4); $K=1$ degenerate (L6) |
| Full-mask versus K-mask for the evidence | dilution | full-mask better for the evidence (probe-1 pattern, inference) |
| M versus I versus M+I | marginalisation | Prop. 6: M $\ge$ I on T-ver; M+I between them |
| I with caption visible | leakage control | Prop. 7: inflated scores for all candidates, true-versus-wrong margin not reliably improved |
| $L=4$, $S_r\in\{8,32\}$, guided sampler | re-infill quality | I approaches M as $L$ grows (Prop. 6) |
| Fusion: sum, Stouffer, IV, single direction at equal passes, oracle refit | LDA fusion | LDA $\ge$ sum and IV; single direction near LDA at the clean ceiling (F8) |
| Gate-aware $\omega_T(g)$ | fixed weights | helps only at large $g$ (L2) |
| Mondrian versus pooled calibration | class-conditional thresholds | flatter clean FAP map; similar AUROC |
| Iterated gate (2 rounds) | single-pass gate | higher TPR on patch, no FAP guarantee |
| Word versus piece gating; min versus sum aggregation | gating unit | word-level fewer partial-word masks; effect on typos only |

---

## 13. Experiments E0-E8 (UniDisc 1.4B, one 12 GB laptop GPU)

**Gating condition for all GPU items:** `runs/P2-PROBE-02/HOLD.txt` must be removed by Shlok's decision (probe report:
two 0x116 crashes, cause unknown). Every GPU-hour figure below is an **estimate** from the derived $P\approx0.12$ s per
pass, item time only; wall time is about double at the configured duty 0.5 (`run_probe2.py` CONFIG `duty=0.5`).

**Data splits (design choice, disjoint by COCO val2017 image id, fixed seed).** Tuning fold: the 200 items of probe 2's
`selection.json` (statistic, $K$ and aggregation are chosen here). Calibration fold: 500 clean items. Test fold: 300
items, not overlapping probe 1's items unless those are excluded from tuning and calibration (check `selection.json` of
both runs). Corruption seeds as in `run_probe2.py` (`SEED=20261028`, per item and corruption).

**Corruptions.** Image, pixel side: JPEG quality {30, 10}; Gaussian noise sigma {0.05, 0.10} on [0, 1] pixels. Image,
token side: patch occlusion with random codes, block {4x4, 8x8, 16x16} tokens; token swap {5%, 15%, 30%} uniform random
codes (sanity check only, red-team F1.2). Caption: character typos in $k\in\{1,2\}$ words (insert, delete, substitute,
transpose, uniformly; content words only), fixed seed. Primary severities (bold in tables): JPEG 10, noise 0.10, patch
8x8, swap 15% (as probe 2), typos $k=1$.

**Pre-declared primary contrast (for `experiment-designer` and `statistician` to freeze).** E3, paired verification
accuracy of the LDA-fused GATE-M statistic minus the same statistic with a random gate of equal size, on the hard-negative
test pairs, one test per realistic corruption (JPEG 10, noise 0.10, patch 8x8): family of 3, Holm, paired bootstrap
10,000 resamples. Everything else is secondary or exploratory.

| ID | Question | Design | Metrics | Controls | Passes per item | GPU-h (estimate) |
|---|---|---|---|---|---|---|
| E0 | Do the propositions and code agree? | Unit tests L1-L9 on CPU; L10 on the model inside the first E1 chunk | pass/fail | n/a | 0 (L10: 4 once) | 0 |
| E1 | Does any per-token score find corrupted tokens? (completes probe 2) | Tuning fold 200 items; clean + 4 primary image corruptions + typo caption; scores s1, s_cm, s2, q, w, tot, plain-B, s3, r_original, random | per-item AUROC and AUPRC vs $Z$, averaged over items with bootstrap CI; graded-label AUROC (F5) | random score; r_original (F1) | image: $5\times2K+1=81$; caption: about 32 | 0.54 + 0.21 = 0.75 |
| E1b | Severity curves | 100 tuning items, the non-primary severities (8 corrupted images per item) | AUROC vs severity | as E1 | $8\times2K=128$ | 0.43 |
| E2 | Does the calibration hold? | Calibration fold 500 clean items (B, A, C; caption side); thresholds for $\alpha\in\{0.01,0.05,0.10\}$; realised FAP on clean test items (from E3's clean arm) | realised FAP with CI vs $\alpha$; spatial FAP map; FAP on clean tokens of corrupted items; shift test: calibrate on items whose captions mention a person, test on the rest (CPU reuse) | none needed | about 33 | 0.55 |
| E3 | Does gating restore verification under corruption? (primary) | Test fold 300 items; clean + 4 corruptions; true caption and one hard negative (the caption of another test image sharing at least one COCO category, U4; fallback: deranged); arms none, GATE-M, random (3 seeds), oracle, GATE on clean, DD-style ($E=3$), GATE-I, GATE-M+I, UniDisc-G.1-style | paired accuracy and unpaired AUROC per direction and fused; headroom check first: corrupted-no-gate below clean by at least 2 paired SE, else the corruption is reported as "no headroom" and excluded from the primary family | random, oracle, clean-gate, DD-style, single directions at equal passes | about 204 | 2.0 |
| E3b | Matching, $N=5$ | 150 test items, 3 more hard-negative captions | top-1 accuracy | as E3 | about 150 | 0.75 |
| E4 | Text-side gate | Test fold 300 items; captions: clean, typo $k=1$, typo $k=2$, wrong, wrong+typo; arms none, GATE-M, random (3), oracle | verification accuracy; **gate-induced false acceptance** (wrong captions accepted after gating, must not rise: F2); word-level detection AUROC | random, oracle | about 100 | 1.0 |
| E5 | Repair and generation (secondary, qualitative plus metrics) | 100 items x {patch 8x8, swap 15%}: R2 re-infill vs R1 vs oracle-gate vs random-gate re-infill; T2I: 100 typo prompts x {clean, typo, gated-M, re-infilled}, 64 network calls per image (EXP-003 measured about 6.6 s per joint sample, IDEAS.md) | CLIPScore vs the clean caption (needs CLIP weights, U4); codebook distance to clean codes on $G$; figures: heat-map, gated mask, re-infill strip, decoded images | oracle, random | about 128; T2I 4 samples | 0.45 + 0.73 = 1.2 |
| E6 | Ablations (section 12) | 100 tuning items x {JPEG 10, patch 8x8}: $K\in\{2,4,16\}$ for B; re-infill $L=4$, $S_r\in\{8,32\}$, guided; iterated gate; fusion rules and Mondrian on CPU | as E1/E3 | as E3 | about 44 (K) + 272 (re-infill) | 1.2 |
| E7 | Second model (optional, unverified) | Omni-Diffusion 8B 4-bit in `.venv-omni`: first a measure-only chunk (20 passes: time, peak memory, under the same memory guards); only then size E1 (100 items, JPEG and patch) and E3 (100 items) | as E1/E3 | as E1/E3 | unknown | unknown until the 20-pass measurement exists |
| E8 | Statistics and figures | paired bootstrap, Holm on the primary family; figures per IF-METHOD-ANATOMY section 6 (heat-maps on the 32x32 grid, ROC per corruption, recovery vs severity, re-infill strip, FAP vs $\alpha$) | n/a | n/a | 0 | 0 |

Total for E1-E6: about 7.9 GPU-hours of item time (estimate), about 16 hours wall at duty 0.5 (estimate). The red team's
realistic range for this idea was 8-14 GPU-hours (their estimate). Order of execution and stop rules: E0 → E1 → (stop if
the E1 falsifier in the YAML header is met: the paper becomes a negative-result note) → E2 → E3 (stop the downstream claim
if no realistic corruption passes the headroom check) → E4 → E5 → E6 → E7 if time remains.

Figures this yields (all real outputs): Fig. 1 motivation, a corrupted image with its suspicion heat-map and the gated
mask; Fig. 2 framework (score, gate, M/I, two-way fusion); Fig. 3 ROC per corruption; Fig. 4 realised FAP vs $\alpha$
and the clean FAP map; Fig. 5 verification accuracy vs severity for none/random/DD-style/GATE-M/GATE-I/oracle; Fig. 6
re-infill strip (S_r snapshots, decoded); Fig. 7 T2I typo grid with CLIPScore labels; Fig. 8 failure cases (JPEG
coherent blocks, F4/F5).

---

## 14. Decisions and checks needed before implementation

1. Shlok: lift or keep `runs/P2-PROBE-02/HOLD.txt` (all GPU items depend on it).
2. `lab-engineer`: U3 (probe 1's null pass: caption masked too?), U5 (fp32 final projection possible?), L10 cache test.
3. `data-steward`: COCO instances annotations for hard negatives and CLIP weights for CLIPScore (U4); split files.
4. `experiment-designer` and `statistician`: freeze the primary contrast and family (section 13), the falsifiers, and
   the design choices marked here ($\alpha$, $K$, $S_r$, $L$, $\kappa$, $n_{\rm cal}$).
5. `red-team`: attack Props. 1-7, the evidence-separation rule and the LDA fusion before code is written.
6. `citation-validator`: Conformal Risk Control (id from memory, not given here), a CFAR reference, Rubin on missing
   data, a Kalman innovation-gating reference, Fisher LDA; Salazar et al. (arXiv:1910.14659) is already checked by the
   novelty audit.
