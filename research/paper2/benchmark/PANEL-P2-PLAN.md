```yaml
agent: mdm-expert (domain expert on the benchmark panel)
date: 2026-10-28
brief: Concrete upgrade plan for Paper 2 (GATE, Information Fusion research article) against the quality bar of Moser et al., IEEE TNNLS 36(7), 2025
sources_examined:
  - research/paper2/benchmark/LENS-CRAFT.md (all)
  - research/paper2/benchmark/LENS-ARGUMENT.md (all; sections 7-8 used most)
  - paper2/main.tex; paper2/sections/{introduction,method,results,discussion,conclusion}.tex (all); protocol.tex lines 1-11, 37-152, 245-275 and headings; related.tex lines 81-125 and headings
  - research/paper2/prereg/PREREG-GATE-v4-2026-10-28.md lines 35-234 (sections 1-8)
  - research/paper2/prereg/SAP-GATE-2026-10-28.md sections 9, A2.2, AD.5, AB.1-AB.5, A3b.2 (headings of the rest)
  - research/paper2/prereg/PREREG-GATE-MUST-v3-2026-10-28.md lines 150-151, 174, 215 (K2 and expected status, by grep)
  - runs/P2-GATE-M1/analysis.json, tbv_verdict.json, detection_frozen.json (head); runs/P2-PROBE-01/summary.json (head)
  - runs/P2-GATE-M1/arrays, runs/P2-GATE-M2/arrays, runs/P2-PROBE-02/arrays (keys of item0000.npz only); runs/P2-GATE-M2/items.jsonl (line count)
  - research/paper2/CONFIRM-EVENING-2026-10-28.md items 7-11 and Shlok's answers
  - research/paper2/ideation/NOVELTY-CHECK-INFFUS-2026-10-28.md sections 0-6; NOVELTY-REAUDIT-GATE-2026-10-28.md section 7
  - research/paper2/related/INFFUS-CITATIONS-2026-10-28.md section 5; research/paper2/style/IF-METHOD-ANATOMY-2026-10-27.md sections 4, 6, 8
  - exp_p2/scoring.py:111 and :162; exp_p2/gate/detect.py:1-60; exp_p2/run_gate_s2.py:1-21, 205-213; output names in exp_p2/gate/analysis_*.py (grep)
coverage: >
  Did not read the PDF of the SR survey (the two lenses were sufficient for the plan); did not read related.tex lines 1-80 in full,
  protocol.tex lines 153-245 and 275-end in full, the SAP body beyond the cited clauses, the IDEAS.md idea text, or UniDisc's
  own code for the time input (see assumption A1). No GPU, no edits to manuscript, code, prereg or ledgers.
claims:
  - statement: "The manuscript's scope sentences describe the v3 run (re-infill, caption corruption, two-way fusion outside the main run); card v4 has 11 test families including S2 re-infill, FOIL family B and Omni family R."
    status: supported
    evidence: "paper2/sections/introduction.tex:84-86; protocol.tex:1-3 (sources v3 + SAP A1-A2); PREREG-GATE-v4 section 2"
    level: E2
    confidence: 0.95
  - statement: "Method plus protocol hold about 63 percent of the current words, before any result (the SR survey's analogous front is about 37 percent)."
    status: supported
    evidence: "wc -w paper2/sections/*.tex: method 3534 + protocol 3356 of 10990; LENS-ARGUMENT section 1"
    level: E2
    confidence: 0.8
  - statement: "On M1 the null-normalised score q has per-item mean AUROC 0.961 (patch) and 0.955 (swap) but 0.561 (JPEG) and 0.503 (noise); a texture rival chosen on the data reaches 0.756 and 0.768 on JPEG and noise."
    status: supported
    evidence: "runs/P2-GATE-M1/analysis.json table.*.q, falsifier.per_corruption.*.cheap_means.tex_neg"
    level: E5
    confidence: 0.95
  - statement: "Plain-B is slightly above q on patch and swap (paired differences q minus plain-B -0.0033 and -0.0053, intervals exclude 0)."
    status: supported
    evidence: "runs/P2-GATE-M1/analysis.json paired_q_vs_best_cheap.{patch,swap}"
    level: E5
    confidence: 0.95
competing_explanations:
  - "Detection near chance on JPEG/noise may reflect labels (changed codes where the tokenizer is unstable) rather than the score; the v3 card fixes that this is reported as the red team's label-circularity concern (v3 line 151)."
unknowns:
  - "Whether UniDisc's denoiser was trained with a time input; the project's scorer calls forward with sigma=None (exp_p2/scoring.py:111). Needed for assumption A1."
  - "Outcomes of M2-M5, S2, FOIL, Omni, suite (not run or not complete; M2 has 114 of 300 rows and is halted, CONFIRM-EVENING section 11)."
next_test: {hypothesis: "n/a (writing plan)", intervention: "n/a", primary_metric: "n/a", falsifier: "n/a", gpu_hours: 0}
```

# PANEL-P2-PLAN: upgrading Paper 2 (GATE) to and past the Moser et al. bar

Labels used below. **[now]** = data on disk today. **[stage X]** = produced by a pending GPU stage of card v4 section 3.
**[concept]** = drawn, no data. Every number quoted carries its file. Nothing here is a result that does not exist.

What we take from the benchmark (LENS-CRAFT section 5, LENS-ARGUMENT section 8): one unifying chain figure before the
derivations, one home-base glyph reused with one change per figure, the injected symbol boxed inside the kernel, captions
that read alone, one marking convention for all tables, a "where" sentence after every display. What we do not take: the
survey form, copied numbers, a decorative taxonomy, a theory-heavy front, an optimistic conclusion.

---

## 0. Diagnosis in five lines

1. **The paper is a protocol with a placeholder results section.** Method 3534 + protocol 3356 of 10990 words (wc -w of
   `paper2/sections/*.tex`, LaTeX-inclusive) = about 63 percent before any result; results.tex is 687 words of `\todo`.
   The benchmark's analogous fault is 37 percent of theory before its first SR method (LENS-ARGUMENT section 1, item 8).
   We are currently worse on this axis.
2. **The manuscript is one card behind.** introduction.tex:84-86 and discussion.tex:34-36 say re-infill, caption
   corruption, two-way fusion and a second model are outside the run; protocol.tex:1-3 cites v3 and SAP Addenda 1-2.
   Card v4 section 2 has 11 test families: P, PS, S2, B, R, E-dec, E-pred (descriptive), suite, and the v3 secondaries.
3. **One figure** (`paper2/figures/F1_probe1_accuracy.pdf`, an exploratory pilot). The benchmark has 8 figures and 4 tables
   (LENS-CRAFT section 0). IF anatomy rule 31 wants a motivation figure on p.1-2 and a framework figure on p.3-4
   (`research/paper2/style/IF-METHOD-ANATOMY-2026-10-27.md` section 8).
4. **Notation repeats the benchmark's own defect** (symbol overload, LENS-CRAFT section 3): 20 clashes listed in section 2.4.
5. **One real result already exists and is not in the paper**: the M1 detection table (section 5.0 below). It is the
   natural opening failure case (LENS-ARGUMENT research rule 1) and the seed of the "when does input gating help" framing
   (CONFIRM-EVENING item 7, Shlok's answer "All recommended").

---

## 1. Skeleton, contributions, fusion angle

### 1.1 Section skeleton and word share

Target body about 12,500 words (IF accepted method papers: 13-15k words with figures, anatomy section 4 item 1; limit
35 pages incl. references, 50 references, INFFUS-CITATIONS section 5). Shares are of body words, excluding tables,
algorithms, captions and appendices.

| # | Section | Target words | Share | Now (wc -w) | Job | Main display items |
|---|---|---|---|---|---|---|
| 1 | Introduction | 1,000 | 8% | 1,100 | failure case from M1, fusion angle, gap, numbered contributions, scope, roadmap checked against headings | Fig 1, Fig 2 |
| 2 | Related work | 1,000 | 8% | 1,166 | four axes + "source validation before fusion"; add Zhou & Lu 2027 (E1 wording) and Wang 2025 | Table 2 |
| 3 | Method | 2,800 | 22% | 3,534 | one primitive, one chain of equations (section 2 below), assumptions beside equations | Fig 3, Table 1, Alg 1-3 |
| 4 | Experimental protocol | 1,900 | 15% | 3,356 | model, data, corruptions, headroom, arms/controls, families and multiplicity, pins (detail to App. A) | Tables 3, 4, 5 |
| 5 | Results | 3,600 | 29% | 687 (todo) | ordered along the chain: detection, calibration, headroom, decision, mechanism, repair, fusion, second model, cost | Figs 4, 6, 7, 8, 9; Tables 6-10 |
| 6 | Discussion | 1,200 | 10% | 636 | 6.1 when does input gating help (map, ranked take-aways with mechanism, scope, falsifier); 6.2 place in information fusion; 6.3 limitations and failure cases | Fig 5 |
| 7 | Conclusion | 250 | 2% | 136 (todo) | ranked take-aways, one limits sentence, one future-work sentence; must not contradict 6.3 | none |
| - | Declarations (AI only here, master brief section 1) | as now | - | 375 | - | - |
| A | App. A: preregistration crosswalk | - | - | - | pins, 11-family map (card section 2), deviations box (card 4.2), spec-proposition-to-equation map | Table A1 |
| B | App. B: remaining algorithms | - | - | - | CalibrateThreshold, ImageEvidence, ReInfill, GeometryMatchedGate (move from main) | Alg B1-B4 |
| C | App. C: exploratory pilot | - | - | - | probe 1 (current F1 becomes Fig C1) | Fig C1 |
| D | App. D: imagecorruptions suite (exploratory) | - | - | - | CIs only, never in abstract (card section 2, row Suite) | Table D1 |

Cuts to reach the targets (CPU, now): move four of the eight algorithms to App. B (method.tex:186-199, 276-288,
349-366; protocol.tex alg:geo); move the pin and hash prose and the deviation detail to App. A; collapse the
"Wording and scope" and "What is not guaranteed" paragraphs (method.tex:163-184) into one assumptions list beside
Prop. 1 (section 2.3); keep the pilot to two sentences in Section 4 and the rest in App. C.

### 1.2 Numbered contributions (each tied to a section and a display item)

Wording respects must-not-claims 1-13 (NOVELTY-REAUDIT section 7; NOVELTY-CHECK-INFFUS section 4): no "first", no
"training-free" as the contribution, no "certified", no "decision-level".

- **C1. A reliability gate for the input tokens of a unified masked diffusion model, built from one masked-likelihood
  primitive.** Every quantity is the log-probability of an observed token under a different visible set; the gate uses
  only visible sets in which the other modality is masked (evidence-separation rule). Section 3.2-3.3; Fig 2 (pipeline),
  Fig 3 (one primitive, five visible sets), Table 1 (notation).
- **C2. A threshold with a stated, narrow guarantee and its empirical check.** Conformal risk control on clean pairs
  bounds the expected false-alarm proportion on clean inputs at alpha; nothing else is guaranteed (Prop. 1 is CRC applied,
  must-not 5). Section 3.4 and 5.2; Fig 7.
- **C3. A detection map of what a generative model can see.** Per-item AUROC of the within-modality score against changed
  codes across corruption families, beside cheap rivals and the non-finetuned TbV score. Section 5.1; Fig 4, Table 6.
  [now] (section 5.0 gives the pre-stated wording, which K2 constrains).
- **C4. A preregistered test of whether withholding flagged tokens changes a cross-modal decision**, with controls that
  remove three competing explanations (mask geometry, texture, pixel denoising). Section 4 and 5.3-5.5; Tables 4, 5, 8;
  Fig 6. [stage M3, M4]
- **C5. Repair, two-way fusion and a second model, each in its own family, none able to rescue C4** (AB.1). Section
  5.6-5.8; Table 9, Table 10, Figs 8 and 9. [stage S2, FOIL, Omni; each may be "not run"]
- **C6. A synthesis: when does input gating help.** One map that puts the conditions stated in advance (method.tex:233-247:
  conditions (i)-(iv); Eq. (snr)) beside every measured cell. Section 6.1; Fig 5. Descriptive only; E-pred wording (AB.3).

The roadmap paragraph is generated last from the actual `\section`/`\subsection` headings (benchmark fault: its roadmap
omits Section VI, LENS-ARGUMENT section 2).

### 1.3 The fusion angle, stated in the introduction (replaces introduction.tex:18-34, about 150 words)

Three sentences carry it; a reader with no project context must be able to say what is fused (discussion.tex:10-13 asks
for this test).

- **What is fused.** The 1,024 image tokens of one image are 1,024 sources; each contributes a per-token log-likelihood
  ratio Delta_j between two candidate captions, and the decision sums them (the naive-Bayes rule of distributed detection,
  `chair1986optimal`). A second, text-direction statistic can be fused with it at score level (Stouffer or a two-weight
  Fisher discriminant, method.tex:368-386; family B).
- **At what level.** Input level: the gate acts on the sources before the evidence sum, not on the output decision.
  Use "input-level source validation"; never "decision-level fusion" (must-not 13).
- **Where reliability enters.** As a 0/1 weight w_j = 1[u_j <= tau_hat] inside the evidence sum (GATE-M), or as
  replacement of the source value by a model sample with the caption masked (GATE-I). The weight is computed from
  within-modality evidence only, with the threshold set on clean data to a fixed false-alarm level, as in CFAR
  detection (`finn1968adaptive`, `rohling1983cfar`). This is the sentence the boxed w_j in Fig 2 and Fig 3 illustrates.

Then one sentence of what is not claimed: the fusion rule is standard; the contribution is the gate, its calibration and
the measurement (introduction.tex:33-34 already says this; keep).

---

## 2. Unified formalism (the benchmark's Fig. 1 move)

### 2.1 Idea

The benchmark unifies DDPM, SGM and SDE by drawing one chain with three rows of update rules (LENS-CRAFT section 1,
Fig. 1). Our unification is simpler and stronger: **every quantity in the paper is one function, the log-probability of
an observed token under a visible set V,**

  lambda_j(V) = log p_theta(x_j | x_V, all other positions = M),

evaluated at five kinds of V. The gate, the evidence, the text direction, the re-infill and the null are rows on one
token bar. Fig 3 draws exactly this (five rows, one bar, visible positions shaded, the target position outlined).

### 2.2 The chain of equations, with the assumption beside each

Symbols follow the renamed notation of section 2.4 (caption tokens w, image tokens v, schedule gamma_s, reliable set R,
kept indicator k_j).

| Eq | Content | Assumption needed (stated beside it in the paper) | Where tested or bounded |
|---|---|---|---|
| (1) forward | absorbing masking of the joint sequence: each position kept with prob. gamma_s, else set to M | **A0** UniDisc was trained with absorbing-state masking on the joint text-image sequence (cite `swerdlow2025unidisc`) | E1 unless the UniDisc code is re-read at a pinned SHA |
| (2) primitive | lambda_j(V) for any visible set V | **A1** the denoiser's conditional at a mask pattern needs no time input (time-free denoiser, `ou2025radd`). Our scorer calls UniDisc with `sigma=None` (exp_p2/scoring.py:111, :162); whether UniDisc was trained with sigma conditioning is **unknown here** | read UniDisc forward at its pinned SHA before writing A1 (work item W9) |
| (3) four levels | A = lambda(own minus S_k, other), B = lambda(own minus S_k), C = lambda(other), D = lambda(empty) | none beyond A1 (definitions) | - |
| (4) PMI split | A - D = (B - D) + (A - B) = (A - C) + (C - D) | algebra only | - |
| (5) gate statistic | u_j = -(B_j - D_j) | **design rule** (evidence separation): no term with the candidate caption visible. Optimality only under **A2**: corrupted value drawn from the position marginal independently of context (NP statistic); for uniform random codes plain B is the NP statistic (method.tex:109-111) | M1: on patch and swap (uniform codes) plain-B is slightly above q (section 5.0), consistent with the second clause |
| (6) CRC threshold | L_i(tau) = mean_j 1[u_ij > tau]; tau_hat = inf{tau: n/(n+1) F_hat(tau) + 1/(n+1) <= alpha} | **A3** calibration items and the clean test item exchangeable as items; **A4** no ties (jitter below the smallest gap); **A5** statistic, K, alpha, fold sizes fixed before scoring. Loss bounded and monotone holds by construction | Prop. 1; empirical check S-C (M2, M4 clean arm) |
| (7) gate | G = {j: u_j > tau_hat}, R = complement, k_j = 1[j in R] | none (definition); **not guaranteed**: power, false alarms on clean tokens of corrupted items, shift (method.tex:177-184) | measured in M4 |
| (8) GATE-M | Delta_j = lambda_j(c+) - lambda_j(c-) with image fully masked; Delta_bar_R = sum_j k_j Delta_j / sum_j k_j; Y_R = 1[Delta_bar_R > 0] | D_j cancels for a fixed image (algebra). Withholding = Bayes answer only under **A6 (i)-(iv)** of method.tex:235-241 (R clean; corrupted values uninformative; locations content-independent; flagged clean tokens uninformative) and **A7** coherent (Bayes-optimal) denoiser for Eq. (marginalise) | A7: coherence check M5; A6 (ii)/(iii) fail for JPEG/noise by construction (stated in advance) |
| (9) GATE-I | v_hat_G ~ p_theta(v_G | v_R, caption masked), best of n_draw = 4 by own chain likelihood; score Delta_bar on all m tokens | **A8** caption masked during re-infill, else the KL bonus of Eq. (leak) favours every candidate; unbiasedness for GATE-M holds in the probability domain under exact sampling only | S2 (I-GATE vs I-RAND4); leakage arm I-GATE-LEAK first to be cut |
| (10) when withholding helps | E S and Var S under independent tokens; for mu_c = 0: rho sigma_c^2 (beta - 2 alpha + alpha^2) > alpha(1-alpha)(1-rho)(sigma^2 + mu^2) | **A9** independent-token approximation; mu_c = 0 for the reduced form (method.tex:310-312 says both can fail) | E-pred (descriptive, "agreed in A of K", AB.3) |
| (11) two-way fusion | F(c) = omega_T E_T(c) + omega_I E_I(c), weights fitted on calibration pairs and frozen | **A10** for optimality of Fisher's discriminant: equal-covariance Gaussian margins; otherwise it is a fitted linear rule. Stouffer needs the calibration correlation r_hat | family B, ceiling rule (best single direction >= 0.95 makes B untestable) |

**Where reliability enters:** only at (7), as k_j inside (8), or as the replaced values in (9). Box k_j in Eq. (8) and in
Fig 2/Fig 3 and draw an arrow to the module that computes it (LENS-CRAFT craft rule 5).

**Equivalence statement to close the formalism (benchmark's III-D move, craft rule 3).** One line after (9): "With exact
sampling from p(v_G | v_R) and the caption masked, the expected probability-domain evidence of GATE-I equals that of
GATE-M; in the log domain an L-sample estimate is biased downward (Jensen)." This is already in method.tex:342-344; move
it directly after the two formulations it joins.

### 2.3 Prop. 1 block rewrite

Keep Prop. 1 with its proof line (CRC Theorem 1, B = 1). Replace the two paragraphs at method.tex:163-184 by a
two-column list "Assumed: A3, A4, A5" / "Not guaranteed: power; clean tokens of corrupted items; shift; iterated
gating". This shortens the method and puts each assumption next to its equation.

### 2.4 Notation clashes in method.tex (and where they leak into other sections)

| # | Symbol | Meanings now (file:line) | Proposed fix |
|---|---|---|---|
| 1 | t | caption tokens t = (t_1..t_n) (method.tex:17); diffusion time is needed for Eq. (1) | caption tokens **w** (words), image tokens **v**; time s or t only for the schedule |
| 2 | T | text modality label {T, I} (method.tex:18, 393: tau_I, E_{T<-I}); also the usual step count | modality labels in sans-serif \mathsf{T}, \mathsf{I}; no step count named T |
| 3 | alpha | CRC target level (method.tex:42, eq. crc); clean-token flag probability in the SNR analysis (method.tex:293-309); results.tex:60 alpha_obs | keep alpha for the target level only; SNR flag probabilities **a_0** (clean) and **a_1** (corrupted), observed a_0_hat, a_1_hat |
| 4 | beta | corrupted-token flag probability (method.tex:293); results.tex:60 beta_obs | **a_1** as above |
| 5 | S | partition group S_k (method.tex:39, 54); additive statistic S (method.tex:291); re-infill steps S_r (method.tex:47, 330); step index s (Alg reinfill); sample SD s_R (method.tex:272); uncertainty score s_3 (protocol.tex arms table) | groups **\mathcal{S}_k**; statistic **Sigma_R**; steps **N_r**; SD **sigma_hat_R**; uncertainty score **u^{unc}** (code name s3 kept only in App. A) |
| 6 | R | reliable set (method.tex:43); empirical risk R_hat(tau) (method.tex:147); n-rules R1-R3 (protocol.tex:73-79); Omni family R (card) | keep R for the reliable set; empirical calibration risk **F_hat_cal(tau)** (results.tex:15 already uses F_hat for the realised FAP); n-rules "rule 1-3" in prose, "R1-R3" only in tables; Omni family named "family Omni" in prose |
| 7 | L | per-item loss L_i(tau) (method.tex:143); number of re-infill samples L (method.tex:47, 330, 351) | samples **n_draw** (the SAP's name, AD.5) |
| 8 | C, D | context levels C_j, D_j (method.tex:40, 58-59); candidate caption c; calibration set D_cal (method.tex:138); headroom discordant counts D_c, D* (protocol.tex:73-79) | option 1 (minimal): rename headroom counts **n^{disc}_c**, **n^{disc}_\*** and calibration set **\mathcal{C}_{cal}**; option 2 (cleaner): levels as **lambda_j^{11}, lambda_j^{10}, lambda_j^{01}, lambda_j^{00}** (bits = own context visible, other modality visible), which makes Eq. (4) self-reading and matches Alg 1's lambda output |
| 9 | D_j | scalar log-prob of the observed token (eq. levels) and a vector over codes D_j[y] (method.tex:261, 283) | write D_j[y] for the vector and D_j = D_j[x_j] once in the notation table |
| 10 | rho | corrupted fraction (method.tex:293); max probability rho_j in Alg 1 (method.tex:85) | Alg 1 output **pi^max_j** |
| 11 | pi | log-softmax vector (Alg 1, method.tex:84); probability vector (Alg ReInfill, method.tex:358, 363) | log vector **ell_j**; probability vector **pi_j** |
| 12 | y, Y | code value y (method.tex:45); working sequence y (Alg ReInfill, method.tex:355); quantity to infer Y (method.tex:234); correctness indicator Y_R (eq. delta) | sequence **z**; quantity to infer **H** (hypothesis); keep Y_R as the correctness indicator (it is the SAP's endpoint name) |
| 13 | k | group index k(j); unmask count k_s (method.tex:330, 357); candidate index c_k; K groups; kill criteria K1-K7; K_eval (E-pred) | reveal count **r_s**; kill criteria written "K1-K7" only in App. A |
| 14 | m | image token count (method.tex:17); gating units of item i, m_i (method.tex:141); token count in the SNR model (method.tex:291); Holm size m (protocol, card) | m for image tokens; **m_i** stated as "units of item i (tokens or words)"; Holm size **m_H** |
| 15 | z | evidence z-score z_R (eq. dz); corrupted label Z_j (notation table) | z-score **zeta_R** |
| 16 | empty set | varnothing^a = "all of modality a masked" (notation table); G <- varnothing = empty set (Alg 8, method.tex:394) | all-masked as **M^a**; empty set stays varnothing |
| 17 | word score | "minimum of its piece scores" (method.tex:118, of q) vs "maximum over the pieces" (Alg 2, method.tex:132, of u) | state once in u: "a word's suspicion is the maximum of its pieces' suspicions" |
| 18 | E | evidence E_{I<-T}, E_{T<-I}; expectation \E; family names E-dec, E-pred | evidence **Ev** or keep E but write families "decomposition" and "sign agreement" in prose |
| 19 | Delta | per-token Delta_j; pair vector Delta^{pair}; direction margins Delta_T, Delta_I (method.tex:373) where T is the modality; SAP's Delta_hat_c (net accuracy) | direction margins **m_T, m_I**; net accuracy difference **theta_hat_c** (SAP 4 already uses theta) |
| 20 | Arm names | "marginalise arm", "impute arm", "arm M / I" (method.tex:219, 328, 390); GATE-M (protocol, results); I-GATE, I-RAND4, I-CHG (SAP AD.5, AB.4) | **GATE-M** and **GATE-I** throughout; one sentence "GATE-I is the arm the SAP calls I-GATE"; comparator "random-gate best-of-4 re-infill (I-RAND4)"; never "G.1" in titles, headers, figure titles (A3b.2 item 1) |

Proposition numbering crosswalk (App. A, Table A1): the SAP and card refer to "Prop. 4" (the SNR plug-in, SAP AD.3, AB.3),
"Prop. 1'" (v3 line 215) and the must-not list to "Prop. 1" (denoiser property) and "Prop. 5" (CRC). The manuscript has
one proposition (CRC, Prop. 1) and the SNR result as Eq. (snr). Map each spec label to the paper's equation number once,
in App. A, and never use the spec labels in the main text.

---

## 3. Figure plan (9 main figures + 1 appendix figure)

### 3.1 Shared visual identity (one module, `paper2/figures/style.py`, CPU, before any figure)

- **Home-base glyph.** A token bar: a short run of caption cells, a divider, then the image as a small 32 x 32 grid icon
  (1,024 tokens, protocol arms table). It appears in Figs 1, 2, 3, 8 with exactly one change per figure (craft rule 4).
- **Token colours, fixed for the paper** (Okabe-Ito, colour-blind safe; fill + outline so two properties show at once):
  clean token = light grey fill; ground-truth corrupted (Z_j = 1) = vermillion fill #D55E00; flagged (j in G) =
  blue outline #0072B2, 2 px; re-infilled = bluish-green fill #009E73; masked (M) = black cell with white M; caption
  tokens = orange #E69F00. A true positive is vermillion + blue outline; a false alarm is grey + blue outline. The legend
  is the same strip in every figure.
- **Arm colours, fixed:** none = black; GATE-M = blue #0072B2; GATE-I = bluish-green #009E73; random gates = mid grey
  (geometry-matched solid, scattered dashed); cheap rivals = reddish-purple #CC79A7 hollow markers; oracle (changed-code
  gate) = dashed black; pixel denoiser = yellow #F0E442 with black edge; TbV = sky blue #56B4E9.
- **Never reuse a colour for a second meaning** (the benchmark reverses forward/backward colours between its Fig. 1 and
  Fig. 6 and reuses green, LENS-CRAFT section 1 defects).
- **Typography:** sans-serif labels at or above caption size at column width (benchmark defect: figure text smaller than
  captions); math in the text's math font; symbols exactly as in Table 1.
- **Captions** (craft rule 7, research rule 6): what is shown, colours, run id, n, interval type, what is held fixed, the
  one finding, and the family label where a test is shown.

### 3.2 Figures

| Fig | One-line message | Type | Data source (exact) | Produced by | Fallback if the stage is cut |
|---|---|---|---|---|---|
| **1** (p.1-2, motivation) | "A damaged token is used as certain: local replacement is visible to the model's own likelihood, diffuse JPEG change is not." | 2 rows (patch, JPEG) x 4 panels: clean pixels, corrupted pixels, changed-code map Z on the 32 x 32 grid, suspicion map u with the flagged set at tau_hat; per-item AUROC printed under each row | **[now]** `runs/P2-PROBE-02/arrays/itemNNNN.npz` (`patch_z`, `patch_s1`, `patch_r_original`, `jpeg_*`) + `runs/P2-GATE-M1/arrays/itemNNNN.npz` (`patch_D`, `jpeg_D`); q via `exp_p2/gate/detect.py:48-56`; pixels via `detect.regen_pixels` (detect.py:35) from COCO val2017. **Item chosen by a rule written before viewing** (e.g. the item whose per-item q AUROC is the median for patch, and the same item for JPEG). The flagged overlay needs tau_hat **[stage M2: threshold.json]** | without tau_hat: show the top-|patch| suspicions, labelled "top-k, not the calibrated gate" |
| **2** (p.3-4, framework) | "GATE scores each image token with the caption withheld, flags it at a calibrated threshold, then drops (GATE-M) or re-infills (GATE-I) it before evidence fusion." | pipeline on the home-base glyph: observed pair -> caption masked, K complementary masks -> u map -> threshold from clean calibration pairs (side input, CRC) -> G -> two branches -> sum over k_j Delta_j for c+ and c- -> optional text-direction fusion -> decision. k_j boxed inside the sum | **[concept]** (TikZ) | always possible |
| **3** (Section 3.2, unification) | "One primitive, five visible sets: the gate uses only rows with the caption masked; the evidence uses only rows with the image masked." | 5 rows of the token bar (A, B, C, D, and the re-infill conditional), visible positions shaded, target outlined; right column: which equation consumes the row (gate, evidence, control, null, GATE-I). Eq. (4) under the rows | **[concept]** | always possible |
| **4** (Results 5.1) | "Within-modality masked likelihood detects random-code replacement almost perfectly and JPEG or noise barely; a texture score chosen on the data wins there." | dot-and-interval plot, facets = swap, patch, JPEG, noise; rows = q, plain-B, u^unc, TbV (non-finetuned), texture, neighbour, rarity, A-B control, random; chance line 0.5; rival markers hollow with "sign chosen on data" | **[now]** `runs/P2-GATE-M1/analysis.json` keys `table.*`, `falsifier.per_corruption.*` | always possible; splice detection added if M4 stores it [stage M4] |
| **5** (Discussion 6.1, the map) | "When does input gating help: a cell-by-cell map from conditions stated in advance to measured effects." | matrix: rows = corruption families (sanity: swap, patch; realistic: splice, JPEG, noise; suite cells marked exploratory); columns = (a) conditions (ii)/(iii) of method.tex:235-241 [stated in advance], (b) headroom T_1, T_2, (c) detection AUROC of q and best rival, (d) GATE-M net accuracy change [95% CI], (e) GATE-M vs geometry-matched random, (f) GATE-I vs I-RAND4, (g) second model. Cell shows the number and CI; colour only for sign with CI excluding 0; grey hatched = "not tested" with the reason (no operating point, cut at freeze, not in family) | (a) **[concept]** from method.tex; (b) `runs/P2-GATE-M3/family.json` + headroom output **[stage M3]**; (c) **[now]** M1 analysis.json; (d)(e) `runs/P2-GATE-M4/analysis.json` **[stage M4]**; (f) `runs/P2-GATE-S2/analysis.json` **[stage S2]**; (g) `runs/P2-OMNI-R-TEST/analysis.json` **[stage Omni]**; suite via `exp_p2.gate.suite analyze` **[stage suite]** | columns of cut stages stay, hatched "not run (cut at the freeze, card section 3 cut order)"; a cut family is never replaced |
| **6** (Results 5.4-5.5) | "Net accuracy change of GATE-M against no gate, beside the controls that share its evidence passes." | forest plot per corruption: GATE-M, geometry-matched random (seed 1; seeds 2-3 faint), scattered random, plain-B top-k, u^unc top-k, changed-code oracle, pixel denoise; x = (b - c)/n with 95% and 98.33% CIs; PS rows (patch, swap) below a rule, labelled "positive control". Under n-rule 3 the x axis is the paired change of d_R | `runs/P2-GATE-M4/analysis.json` **[stage M4]** | none: M4 is required; Shlok's D18 answer is to move the deadline rather than submit without M4 (CONFIRM-EVENING section 9 item 7) |
| **7** (Results 5.2) | "The realised clean false-alarm proportion stays at or below alpha; false alarms on clean tokens of corrupted items are measured, not bounded." | (a) realised F_hat vs alpha in {0.01, 0.05, 0.10} with item-clustered intervals, diagonal y = x; (b) 32 x 32 map of clean false-alarm frequency; (c) FAP on clean tokens of corrupted items per corruption | (a)(b) `runs/P2-GATE-M2/threshold.json` (from `fit_threshold`) + M4 clean arm in `runs/P2-GATE-M4/analysis.json`; (c) M4 **[stage M2 (114 of 300 rows, halted) and M4]** | without the M4 clean arm: the SAP section 6 exploratory 2,000-split check on M2 items only, labelled exploratory |
| **8** (Results 5.6, real outputs) | "What the flagged set and the re-infilled images look like, successes beside failures." | the AD.5 preregistered subset: per corruption (patch, splice) the first 8 items in list order with g_i >= 1 and the first 4 harm cases (Y(I-GATE) = 0, Y(NONE) = 1); panels: clean, corrupted, G overlay, I-GATE kept draw, I-GATE draw 1 (not selected, AB.4 item 5), I-RAND4 kept draw, I-CHG if not cut; Delta_bar for c+ vs c- printed under each. Caption: "best of 4 draws by own likelihood, caption masked; not typical samples" | `runs/P2-GATE-S2-FIG/` (decoded subset; `exp_p2/run_gate_s2.py --figures`, lines 205-213, 280-327) **[stage S2, then card row 9]** | if S2 is cut: Fig 1 style rows for M4 items (pixels + Z + u + G, no re-infill), and Results 5.6 says "not run". No claim on JPEG or noise either way (AD.5 "May not") |
| **9** (Results 5.7, two-way fusion) | "What is fused: the two directional margins per FOIL pair and the frozen fusion line." | scatter of (m_T, m_I) per test pair, foil vs true, the Stouffer and Fisher lines from `fusion_frozen.json`; marginal accuracies on the axes | `runs/P2-GATE-FOIL/fusion_frozen.json` + `runs/P2-GATE-FOIL/analysis.json` **[stage foil-fit, foil-test]** | if B is untestable at the ceiling: the scatter stays, captioned "untestable at ceiling" with the clean accuracy; if FOIL is cut: replace by a cost figure (passes and seconds per item by arm, peak GPU memory, from `runs/P2-GATE-M4` telemetry and config; IF anatomy rule 33) |
| C1 (App. C) | exploratory pilot | existing `paper2/figures/F1_probe1_accuracy.pdf` | `runs/P2-PROBE-01/summary.json` **[now]** | - |

Notes. (i) Fig 1 and Fig 4 can be built tonight from files that exist; they are the only result figures not waiting on
the GPU. (ii) Figs 1, 7b, 8 use real COCO images and real UniDisc token codes; decoded token images (what the model
"sees") need the VQ decoder; S2's `--figures` mode decodes on the GPU, so other decodes are optional. (iii) No figure is
drawn with a generative image tool (introduction.tex:88-90).

---

## 4. Table plan

### 4.1 Marking and reporting rules (one rule, stated in every caption)

- **Ranking tables (Table 6 detection only):** best point estimate per column **bold**, second underlined; ties to three
  decimals both bold (the benchmark's Table IV convention, LENS-CRAFT section 2, applied consistently). Rivals whose sign
  was chosen on the data carry a dagger and the footnote "sign chosen on the data among about nine candidates (sign
  oracle), which favours the rival".
- **Contrast tables (Tables 7-10):** no best-value bolding. **Bold a row only when its preregistered test rejects after
  its family's Holm correction in the direction the claim needs** (b > c). Never bold on an unadjusted p. A row with
  c > b that rejects is set in italics and labelled "harm".
- Every contrast carries: n, n_d, b, c, both accuracies, (b - c)/n with paired-bootstrap 95% CI (and 98.33% for P, the
  first Holm step), exact p, Holm p, the A2.2 label. Interval type in the caption: percentile bootstrap over items,
  10,000 resamples (`runs/P2-GATE-M1/analysis.json` meta), McNemar exact two-sided.
- "-" is split: "n/a" (not applicable) vs "not run" (cut, with the cut row of card section 3) vs "no op. point" (failed
  headroom). The benchmark uses a bare hyphen for all three (LENS-CRAFT section 2).
- Each caption ends with "Held fixed:" and the run id. Booktabs, no vertical rules (IF guide; the benchmark's Table IV has
  vertical rules).

### 4.2 Tables

| Table | Section | Columns | Held fixed (caption) | Source |
|---|---|---|---|---|
| 1 Notation | 3.1 | symbol, meaning, first equation | - | renamed per section 2.4 |
| 2 Positioning | 2 | work; tokens treated as suspect (input / generated); modalities; model and training; score; threshold and guarantee; action on flagged tokens; cross-modal decision; evidence level read (E1/E2/E3) | - | extend related.tex:81-102; add Zhou & Lu 2027 with "as described in the abstract" wording (NOVELTY-CHECK-INFFUS section 5) and Wang 2025. Reference budget: 49 of 50 now (INFFUS-CITATIONS section 5), so two additions displace two entries (authors decide) |
| 3 Corruptions | 4 | corruption, class (realistic / sanity), rungs, definition, family it enters | one realisation per image (protocol.tex:42-43) | exists (protocol.tex:44-61); add the family column |
| 4 Arms and controls | 4 | arm, kept set R, competing explanation it removes, family | the two caption-only evidence passes per item, shared by all arms (method.tex:263-265) | exists (protocol.tex:104-122); add the "explanation removed" and "family" columns |
| 5 Families and multiplicity | 4 | family, hypotheses, n planned, test, Holm m, allowed claim, forbidden claim | no cross-family adjustment (AD.11) | condensed from card v4 section 2 |
| 6 Detection | 5.1 | rows grouped: generative (q, plain-B, u^unc, TbV non-finetuned), cheap (texture, neighbour, rarity, each with sign), controls (A - B, random); columns: swap, patch, JPEG, noise, per-item mean AUROC [95% CI], n items; last rows: q minus best rival with CI and Holm p | model, tokenizer, K, mask seeds, 200 items (JPEG 197, noise 198 usable; `table.jpeg._n_excluded` = 3, `table.noise._n_excluded` = 2) | **[now]** `runs/P2-GATE-M1/analysis.json` |
| 7 Headroom | 5.3 | corruption, rung, n_v, T_1, T_2, pass, operating point, n^disc_c, n^disc_\*, n-rule, test-fold size | 100 headroom items, no gate flag computed on them (protocol.tex:65-66) | `runs/P2-GATE-M3/family.json` [stage M3] |
| 8 Primary + PS | 5.4 | as results.tex:32-40 plus n_d, 98.33% CI, label; PS rows (patch, swap) below a rule with their own Holm m = 2 | test fold ids, tau_hat, K, alpha, caption pair draws, evidence passes | `runs/P2-GATE-M4/analysis.json` [stage M4] |
| 9 Mechanism and secondaries | 5.5 | S-M (seed 1; seeds 2-3), S-Z (d_R, z), S-DN (denoiser; JPEG row worded "against an aggressive denoiser that harms the image", CONFIRM answer 5), E-dec (U "residual loss under the oracle gate", R, V "gap to the oracle gate", AB.2), E-pred (s_c, o_c, o_c\*, "agreed in A of K_eval", AB.3) | as Table 8 | M4 `analysis.json`, `edec.json`, E-pred output [stage M4] |
| 10 Repair, fusion, second model | 5.6-5.8 | S2: per cell (patch, splice) I-GATE vs I-RAND4 kept draw (test), draw-level and all-four-correct differences, I-GATE vs NONE (descriptive) in the same table (AB.4 item 2(ii), A3b.1), token-level agreement (descriptive); B: fusion vs best single direction or "untestable at ceiling"; R: per corruption in P+ | S2: same items, same g_i, sampler, n_draw = 4, selection rule (AD.5); R: "4-bit quantised", "same test images" if n-rule 2 (AB.5) | `runs/P2-GATE-S2/analysis.json`, `runs/P2-GATE-FOIL/analysis.json`, `runs/P2-OMNI-R-TEST/analysis.json` [stages S2, FOIL, Omni] |
| 11 Cost | 5.9 | stage, network passes per item (method.tex:413-431 formula), measured median seconds per item, peak GPU memory, steps for GATE-I | hardware (one 12 GB laptop GPU), batch, precision | `tab:cost` + telemetry CSVs and `config.json` of each run |

---

## 5. Findings framing per outcome

Binding sources: SAP section 9 table, A2.2 (three-way label), AB.1 (no rescue of a P null), AB.2-AB.5, A3b.2; v3 K2
consequences (v3 line 151); must-not-claims 1-13. Title, abstract, highlights and conclusion never carry a secondary
family's result without its family label, and never carry a causal clause for a P null.

### 5.0 Already observed: M1 detection (secondary family S-D; K2 met)

Numbers (all `runs/P2-GATE-M1/analysis.json`, per-item mean AUROC, 95% percentile bootstrap, 200 items):

- q: patch 0.961 [0.959, 0.963]; swap 0.955 [0.952, 0.957]; JPEG 0.561 [0.547, 0.575]; noise 0.503 [0.493, 0.513].
- plain-B: patch 0.964; swap 0.960; JPEG 0.560; noise 0.511. TbV (non-finetuned): JPEG 0.581, noise 0.607.
- Best cheap rival on JPEG and noise is texture with the sign flipped (`tex_neg`, chosen on the data): 0.756 and 0.768.
  q minus rival: JPEG -0.195 [-0.214, -0.175], noise -0.265 [-0.278, -0.253], Holm p 0.0004 each (`falsifier`); the same
  with the rival reselected in every resample, and excluding the dry-run items (n = 179).
- q minus plain-B on patch -0.0033 [-0.0042, -0.0026], swap -0.0053 [-0.0058, -0.0047] (`paired_q_vs_best_cheap`).
- Chance bar for the positive control: PASSED (`chance_bar_both.verdict`). TbV copy check: no item suspected
  (`tbv_verdict.json`).

Wording (fixed by v3 line 151, applied by ledger commit 79be7ad5): the paper does **not** say q detects corrupted codes
better than cheap methods; the rival, its sign and its AUROC with CI go in the main text (Table 6, Fig 4); the same
sentence says the rival was chosen on the data (sign oracle over about nine candidates, which biases q minus rival
downward); the texture win is reported as the red team's label-circularity concern, not as evidence that texture explains
the corruption effect; a later P pass is worded "a gate built on q helps".

Additional honest line the method needs: on the uniform-code sanity corruptions plain-B is slightly above q, which is
consistent with method.tex:110-111 (for a uniform alternative the plain likelihood is the Neyman-Pearson statistic). The
sentence at method.tex:109 ("Dividing by the position marginal D_j matters ...") must be scoped to the alternative it
names; no sentence may say the null normalisation improves detection on these data.

### 5.1 Family P (headline)

| Outcome | Title / abstract sentence | Body | Never |
|---|---|---|---|
| **Positive, S-M rejects** for the same corruption | "GATE-M improved image-direction verification over no gate on X, beyond what an equally shaped random mask gives" (one model, one corruption, one severity) | Table 8 bold row; Fig 6; mechanism in 5.5 | "detection caused" without S-M; generality beyond UniDisc (must-not 9) |
| **Positive, S-M not rejected** | "improvement, but not distinguishable from masking the same shape elsewhere" | same | any location or detection reading |
| **Harm** (c > b rejects) | "GATE-M reduced verification accuracy on X" | italics row, harm panels | softening |
| **Negative** (A2.2: no rejection, every corruption with an operating point has 90% CI inside (-0.05, +0.05), n >= 240) | "no improvement was detected; an improvement larger than 0.05 is excluded" (+ "and a loss larger than 0.05 is excluded" when both bounds hold) | sensitivity statement "with this n_d only theta >= theta\* would have been detectable"; not available under n-rule 3 | "GATE-M has no effect" |
| **Inconclusive** (everything else, including n < 240 and n-rule 3 nulls) | "no improvement was detected; the data are compatible with a net change between L and U (95% CI)" | same sensitivity statement; all secondary families in Results under their labels | any "predicted", "explained", "caused by detection" (AB.1) |
| **K1: no operating point** | "the corruptions studied left no measurable room for a gate at the preregistered rungs; the downstream claim is withdrawn" | detection, calibration, clean control only (protocol.tex:70-72) | S2, B or R as a substitute headline |

Title rule for the "when does input gating help" framing (CONFIRM answer 7): the question form is allowed for every
outcome because it claims nothing; e.g. "When does input-token gating help a masked diffusion model? A preregistered
measurement of calibrated source validation on UniDisc". "Fusion", "repair" or "robust" in the title only if a P
rejection with b > c exists (title comment main.tex:43-44, red-team C4).

### 5.2 Secondary families

| Family | Positive | Null / inconclusive | Mixed rule |
|---|---|---|---|
| **PS** (patch, swap) | "the pipeline is not broken" | "pipeline defect suspected, audit triggered" | never "the gate works where detection is easy" (AB.1(a)) |
| **S2** (re-infill) | A3b.2 item 3 sentence: repairing the GATE-M set gives higher image-direction accuracy than repairing equal-size random sets, best of four by chain likelihood, caption masked; I-GATE vs NONE printed beside it; the claim-bearing cell is splice (AD.5) | "no evidence that the flagged set is better placed than a random one under this sampler" (A3b.2 item 5); if I-GATE is not above NONE and splice is not rejected: no repair claim | patch-only rejection = positive control, "no realistic cell"; I-GATE below I-RAND4 with CI excluding 0 refutes the location claim; never "restores", never JPEG/noise |
| **B** (FOIL fusion) | the A3.4 item 3 sentence (triggered) | A3b.3 item 6 sentences (untriggered); "untestable at ceiling" with the clean accuracy | B is not a corruption test; no "up to 8.7 percent" or any foil-noise bound |
| **R** (Omni 8B, 4-bit; runs only if P+ is non-empty) | n-rules 1/2: "directional replication on a second model, 4-bit quantised; quantisation confounds a likelihood-based detector" (+ "same test images" under rule 2) | "not replicated; inconclusive at this n"; positive-control failure = "pipeline defect: not run" | never "generalises", never pooled with UniDisc, never "independently verified" adapter |
| **E-dec** | descriptive only: U "residual loss under the oracle gate", V "gap to the oracle gate" | V < 0 with CI excluding 0 voids any detection reading | never "treatment" or "detection" for U, V in abstract, highlights, conclusion |
| **E-pred** | "the sign of the plug-in SNR change agreed with the sign of the net accuracy difference in A of K_eval cells (CI)", P and PS cells separate, both signs shown | same sentence with the observed A | "predicted" only inside the E-pred table columns |
| **Suite** | descriptive, CIs, labelled exploratory, App. D | same | no p-value in a claim, never in abstract or highlights |

### 5.3 Abstract, prepared before results (three versions, written now)

Write three abstracts and three highlight sets now (positive / negative-or-inconclusive / K1), each with `[R]` slots and
the exact sentence of 5.1, and commit them before the first M4 analysis (they are wording, not tests; committing them
early removes any suspicion of outcome-shaped prose). Each abstract states the M1 detection result with its family label
in one sentence, and the scope in one sentence (one model for P; a second, 4-bit model only under R).

---

## 6. Where we beat the benchmark, and where we are below it today

### 6.1 Against LENS-ARGUMENT section 7 (the ten hostile-reviewer points) and LENS-CRAFT defects

| # | Benchmark weakness (lens reference) | Our answer | Status today |
|---|---|---|---|
| 1 | No search/selection protocol (LENS-ARG 7.1) | preregistered card v4, SAP with addenda, pinned code SHA 9c4e1e25 and hashes (card section 1) | **beats** (in place; must be reported compactly, App. A) |
| 2 | No synthesis table (7.2) | Fig 5 map + Table 5 families | **planned** (Fig 5 scaffold is CPU work now) |
| 3 | Decorative taxonomy, axes not used later (7.3) | the chain of equations (section 2) orders Results 5.1-5.8 and Fig 5's columns; each Results subsection names the equation it tests | **planned** |
| 4 | Comparability named, not fixed; copied numbers (7.4; research rule 3) | every arm shares the same two evidence passes per item (method.tex:263-265); one test fold; held-fixed line in every caption; no copied numbers | **beats** by design |
| 5 | Promise/delivery mismatch, roadmap errors (7.5) | roadmap generated from headings; contributions tied to display items | **below today**: intro and discussion promise a v3 scope that card v4 changed (section 0 item 2) |
| 6 | Closest work in bibliography, not discussed (7.6) | Table 2 compares TbV, Gomes, CO2Jump, FreeCorrection, UniDisc demo, dropout decoding | **partly below**: Zhou & Lu 2027 and Wang 2025 (Information Fusion) not yet cited or differentiated (NOVELTY-CHECK-INFFUS section 5 gives the sentences) |
| 7 | Unsupported causal talk; untestable future work (7.7) | AB.1 bans causal clauses for a P null; every Discussion take-away carries mechanism (marked hypothesis), scope, falsifier (style rule 26) | **beats** if written as planned |
| 8 | Theory-heavy front, 37% (7.8) | target 37% for method + protocol together (section 1.1) | **below today** (about 63%) |
| 9 | No limitations, no code or data (7.9) | discussion.tex:15-44 limitations; pins; Zenodo planned | **beats** (limitations drafted; repository and DOI still to do, anatomy rule 36) |
| 10 | Conclusion repeats, ends on optimism, contradicts discussion (7.10) | ranked take-aways; one limits sentence; checked against 6.3 | **planned** (conclusion is todo) |
| C1 | Inconsistent colours across figures (LENS-CRAFT 1, defects) | one palette module, fixed token and arm colours | **planned** |
| C2 | No notation table; symbol overload (LENS-CRAFT 3) | Table 1 exists (method.tex:23-50) | **below today**: 20 clashes (section 2.4) |
| C3 | Inconsistent bold/underline; bare hyphens; no intervals (LENS-CRAFT 2) | one marking rule (4.1); "n/a / not run / no op. point"; intervals and tests in every contrast | **beats** by design |
| C4 | Single photographs, no metric on the figure (LENS-CRAFT 1, Figs 6-7) | Fig 8 uses the preregistered subset with harm cases and printed Delta_bar | **planned** [stage S2] |

### 6.2 Where we are below the benchmark today (priority order)

1. Results empty except M1, which is not yet written in.
2. 1 figure vs the benchmark's 8; no unification figure, no pipeline figure, no real-output figure.
3. 63% of words before any result.
4. Scope sentences one card behind (v3 vs v4).
5. Notation clashes, including the benchmark's own sin (alpha with two meanings; LENS-CRAFT section 3 notes alpha_t with
   opposite meanings in the benchmark).
6. No Information Fusion papers differentiated in Related work (journal fit; anatomy and INFFUS-CITATIONS section 2).
7. The fusion angle is a framing paragraph, not a figure; Fig 2 and Fig 3 fix this.

---

## 7. Prioritised work list

Model and budget rules (CLAUDE.md token rules): implementers on Sonnet, mechanical checks on Haiku, explicit `model`
on every agent, at most 3 agents at once (project CLAUDE.md). **CPU work must not starve the GPU**: the second M2 stop
(idx 113) happened with free RAM at 4.15 GB while three CPU agents ran (CONFIRM-EVENING section 11). Run figure and
manuscript agents only while the GPU is idle, or one at a time with light memory use.

### 7.1 CPU-only, before results land (now to the freeze, Fri 30 Oct 18:00 IST)

| P | Item | Owner (model) | Output | Depends on |
|---|---|---|---|---|
| P0 | **W1** Bring scope sentences to card v4: intro:84-86, discussion:34-36, protocol:1-11 and the families paragraph; add Table 5 | manuscript-writer (sonnet) | edited .tex | card v4 section 2 |
| P0 | **W2** Notation pass per section 2.4 (one commit, with a symbol crosswalk in App. A) | method-architect (sonnet), checked by a Haiku grep pass | method.tex, protocol.tex, results.tex | - |
| P0 | **W3** Write Results 5.1 (detection) from M1 with the K2 wording of 5.0; Table 6 and Fig 4 from a committed script reading `runs/P2-GATE-M1/analysis.json` | figure-smith (sonnet) + manuscript-writer | `paper2/figures/F4_detection.pdf`, table .tex, script under `analysis/paper2/` | M1 analysis (done) |
| P0 | **W4** `paper2/figures/style.py` (palette, glyph, fonts) before any other figure | figure-smith (sonnet) | module + a one-page swatch PDF | - |
| P1 | **W5** Fig 2 (pipeline) and Fig 3 (one primitive, five visible sets), TikZ, with boxed k_j | figure-smith (sonnet) | two PDFs | W2 (symbols) |
| P1 | **W6** Introduction rewrite: M1 failure case first, fusion angle (1.3), numbered C1-C6, scope, roadmap from headings | manuscript-writer (sonnet) | introduction.tex | W1, W3 |
| P1 | **W7** Fig 1 motivation: write the item-selection rule into a dated note **before** opening any image; then build from probe-2 and M1 arrays; flagged overlay once `threshold.json` exists | figure-smith (sonnet) | F1 PDF + rule note | M2 threshold for the overlay |
| P1 | **W8** Fig 5 map and Tables 7-11 as generators that read run files and print "pending / not run / no op. point" until data exist (so filling them after the freeze is mechanical) | figure-smith (sonnet) | scripts + placeholder renders | W4 |
| P1 | **W9** Check UniDisc's forward for time conditioning at its pinned SHA (assumption A1); record E3 file:line | mdm-expert (sonnet is enough) | one-paragraph note | - |
| P1 | **W10** Related work: add Zhou & Lu 2027 (E1 wording) and Wang 2025 per NOVELTY-CHECK-INFFUS section 5; decide which 2 of 49 references to drop (authors) | manuscript-writer (sonnet); authors decide drops | related.tex, references.bib | Shlok/professor for the drop list; full-text read of Zhou & Lu needs the e-gateway |
| P1 | **W11** Three abstracts and highlight sets (5.3), committed before the first `analysis_m4` | manuscript-writer (sonnet) | `paper2/abstract-variants.md` | W1 |
| P2 | **W12** Shorten method and protocol to targets: algorithms to App. B, pins and deviations to App. A, Prop. 1 assumptions list (2.3) | manuscript-writer (sonnet) | .tex | W2 |
| P2 | **W13** Caption templates with run id, n, interval type, held-fixed line, family label | figure-smith (haiku is enough) | snippets | W8 |
| P2 | **W14** App. A crosswalk: spec propositions and card names to paper equation numbers; 11-family table; deviations box (card 4.2) | manuscript-writer (sonnet) | appendix .tex | W2 |

### 7.2 After the freeze (results frozen; nothing tuned)

| P | Item | Owner (model) |
|---|---|---|
| P0 | Fill Tables 7-11 and Figs 5-9 from run files only, through the W8 generators; every number gets a `% run:` comment (results.tex:3) | figure-smith (sonnet) |
| P0 | Pick the abstract variant of 5.3 that matches the A2.2 label; write Results 5.2-5.9 and Discussion 6.1 in the order of the chain | manuscript-writer (sonnet) |
| P0 | Number reconciliation of every number in the PDF against `runs/` | gate-auditor (sonnet) |
| P0 | Wording audit against SAP 9, A2.2, AB.1-AB.5, A3b.2 and must-not-claims 1-13 | red-team (opus, the one hard review) |
| P1 | Fig 8 from `runs/P2-GATE-S2-FIG` (or the fallback) with the AD.5 "May not" list in the caption | figure-smith (sonnet) |
| P1 | Conclusion: ranked take-aways that do not contradict 6.3 | manuscript-writer (sonnet) |
| P1 | Page count in the final `5p,twocolumn` layout (main.tex:3-4), 35-page limit; reference count at or below 50 | Haiku check |
| P1 | Citation validation (Crossref/arXiv; IF papers by DOI) | citation-validator (sonnet) |
| P2 | Clarity pass with research-humanizer; AI only in the Declaration | clarity-editor (sonnet) |
| P2 | Repository and DOI for code, run files and figures (no "available on request", anatomy rule 36) | lab-engineer (sonnet) |

### 7.3 Decisions that are Shlok's (or the professor's)

1. Which two references to drop to fit Zhou & Lu and Wang under the 50 cap (INFFUS-CITATIONS section 5).
2. Whether "Multimodal fusion" enters the keywords (main.tex:81, decision M7), after the "what is fused" test on the
   abstract and the Fig 2 caption.
3. The Fig 1 item-selection rule (W7), so that it is fixed by a human before images are viewed.

---

## 8. Concerns

1. The manuscript states a v3 scope while card v4 runs S2, B and R; until W1 lands, any section drafted from the current
   text inherits the wrong scope.
2. method.tex:109 can be read as claiming that null normalisation helps detection; M1 shows plain-B slightly above q on the
   uniform-code corruptions (section 5.0). Scope that sentence to the alternative it names.
3. Assumption A1 (time-free conditional) rests on `sigma=None` in our scorer (exp_p2/scoring.py:111); whether UniDisc was
   trained with time conditioning is not verified here (W9).
4. CPU-heavy figure work during GPU stages risks more slow-item stops (CONFIRM-EVENING section 11).
5. The Zhou & Lu comparison is E1 (closed access); Table 2 must use "as described in the abstract" until the e-gateway
   read is done.
