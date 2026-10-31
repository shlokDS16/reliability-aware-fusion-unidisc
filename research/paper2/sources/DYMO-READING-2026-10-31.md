---
agent: paper-reader
date: 2026-10-31
brief: Read DyMo (arXiv 2601.22853) to support at most one Related Work sentence in the Paper 2 TNNLS submission.
sources_examined: [arXiv:2601.22853v3 (PDF, local copy research/sources/pdfs/2601.22853.pdf; text research/sources/md/2601.22853.md)]
coverage: >
  Abstract, Sec. 1 (p1-2), Sec. 2 (p3), Sec. 3.1-3.3 (p3-6), Sec. 4.1-4.2 and Sec. 5 (p7-10),
  Table 1 and Table 2 headers, Appendix A.1 (opening), A.2 (subset prototypes), C.2-C.4, D.
  NOT covered: remaining Appendix B (data and implementation details), Appendix C.1 and C.5-C.6,
  the full numbers of Table 1 and Fig. 3 (figure data was not extracted), and the released code
  (github.com/siyi-wind/DyMo was not opened; nothing below is E3).
claims:
  - statement: "DyMo selects among recovered (imputed) modalities per test sample at inference, at modality level."
    status: supported
    evidence: "Abstract; Sec. 1 p2; Sec. 3.2 and Algorithm 1 p6 (XO, XC are sets of modalities)"
    level: E2
    confidence: 0.95
  - statement: "The selection criterion is a loss-decrease reward (MTIR), computed in prototype space and calibrated by an intra-class similarity (ICS) ratio."
    status: supported
    evidence: "Sec. 3.2, Eq. 4 and 6 (p5), Eq. 7-9 (p5-6)"
    level: E2
    confidence: 0.9
  - statement: "Selection needs no extra trained parameters or labels at inference, but depends on a network trained with DyMo's own training recipe."
    status: supported
    evidence: "Sec. 1 p2 (no added architecture overhead); Sec. 3.2 p5 (predicted labels replace y); Sec. 3.3 p6; App. A.2"
    level: E2
    confidence: 0.8
competing_explanations: []
unknowns: ["Whether the released code matches Eq. 7-9 and Algorithm 1 (not inspected).", "Exact ICLR 2026 proceedings pagination and location (not found in the PDF)."]
next_test: {hypothesis: none, intervention: none, primary_metric: none, falsifier: none, gpu_hours: 0}
---

# DyMo reading for the Paper 2 Related Work sentence

Evidence level for everything below: E2 for "the paper reports X", never for "X is true". Short quotes only.

## 1. Bibliographic data (verified)

- Title: Inference-Time Dynamic Modality Selection for Incomplete Multimodal Classification
- Authors (PDF title block and arXiv metadata agree): Siyi Du, Xinzhe Luo, Declan P. O'Regan, Chen Qin.
  Affiliations: Imperial College London (EEE and I-X; MRC Laboratory of Medical Sciences).
- Venue: ICLR 2026. PDF header on every page: "Published as a conference paper at ICLR 2026".
- arXiv: 2601.22853. v1 submitted 30 Jan 2026; the PDF read here is v3 (arXiv metadata online date 13 May 2026).
- Code: github.com/siyi-wind/DyMo (stated in the abstract; not opened).
- Not found in the PDF: proceedings page range, DOI, city. Do not put these in the BibTeX.

## 2. What DyMo selects (modality level)

- Setting: incomplete multimodal classification where missing modalities are first recovered (imputed)
  by an external generator; DyMo then chooses which recovered modalities to fuse. Abstract: it
  "adaptively identifies and fuses reliable recovered modalities".
- Unit of selection: whole modalities. Algorithm 1 (p6) keeps an observed set XO and a candidate
  set XC of recovered modalities and moves one at a time into XO. Modalities in the paper are image,
  text and structured table (Sec. 4, p7). There is no token-level selection.
- Recovery methods used: MoPoE (a multimodal VAE) for PolyMNIST, MST, CelebA; TIP (image-tabular
  reconstruction) for DVM and UKBB (Sec. 4 "Implementation Details", p7). An iterative multivariate
  imputer is used in an extra check (App. C.2).
- Network: modality-specific encoders, a multimodal transformer over the concatenated tokens with
  a [CLS] token, attention masks and dummy tokens for missing modalities, linear softmax classifier
  (Sec. 3.1, p3-4). Tokens exist inside the model, but the gate acts on modalities, not tokens.

## 3. Selection criterion: the MTIR reward and the ICS score

- MTIR (Multimodal Task-Relevant Information Reward), Eq. 4 (p5): the drop in cross-entropy when a
  recovered modality is added to the observed set, R = CE[f(XO)] minus CE[f(XO, recovered)].
  Since the true label is unknown at test time, the predicted labels replace it (p5).
- Motivation: Eq. 2 (p4) lower-bounds the mutual information I(Y;Z) by H(Y) minus the empirical
  test CE loss minus a concentration term (derivation in App. A.1). Lower loss therefore raises the
  bound. The paper calls the loss decrease a "tractable proxy" for information gain (p5).
- Prototype form: Eq. 5-6 (p5) rewrite the posterior as a softmax over negative distances to class
  prototypes c_k (class means of training representations), with a Bregman-type distance (squared
  Euclidean) or cosine distance. The reward is large when the representation moves closer to the
  predicted class prototype after adding the recovered modality.
- ICS score (intra-class similarity), Eq. 8 (p5): ICS(y=k, z) = 2(1 - Phi(d(z, c_k))) with Phi the
  standard normal CDF, after modelling training distances to the prototype as a truncated normal
  with a per-class sigma_k estimated from training data. It measures how representative the
  representation z is within its predicted class cluster (higher = closer to training samples of
  that class). Caveat: as printed, Eq. 8 applies Phi to the raw distance, with sigma_k implicit
  (the text says the distribution is N(0, sigma_k^2)); I did not check whether the code divides by sigma_k.
- Calibration, Eq. 9 and Eq. 7 (p5-6): lambda = 1 if ICS(recovered) <= ICS(observed), otherwise the
  inverse ratio; the second CE term in the reward is multiplied by lambda (asymmetric, "conservative"
  when the recovered representation looks more typical than the observed one).
- Loop (Algorithm 1, p6): compute the calibrated reward for all candidates, add the best if positive,
  drop all non-positive candidates, repeat until no candidates remain. Mean iterations are 1.38 on
  PolyMNIST with 80% missing (App. C.3, p22-23).
- At inference the paper uses subset-specific prototypes c_{k,S}, one set per modality subset S (App. A.2, Eq. S16).
- The paper says positive reward means added task information, zero means low fidelity, negative
  means "task-relevant but semantically inconsistent" content (p4). This is the paper's
  interpretation, not something it tests separately.

## 4. Is selection training-free at inference?

- Training-free in the narrow sense: no gradient step, no new parameters and no labels at test time.
  Sec. 1 (p2) claims "readily deployable without additional architecture overhead"; labels are replaced by
  predictions (p5). Prototypes and sigma_k come from the training set (Eq. 5, Eq. 8, App. A.2).
- Not training-free in the broader sense: (a) the reward relies on representation shifts, so f is trained
  with incomplete-modality simulation (Eq. 10) and a missing-agnostic contrastive loss (Eq. 11),
  and the paper says proper training is "essential" for the dynamic process (Sec. 3.3, p6);
  (b) the recovery generator (MoPoE, TIP) is a separate trained model; (c) the models are trained on
  complete data and tested under simulated missingness (Sec. 4, p7).
- Cost: extra forward passes per candidate per iteration; the paper calls the cost "moderate" (App. C.3).

## 5. Datasets and metrics (Sec. 4, p7)

PolyMNIST, MST, bimodal CelebA (simulated benchmarks from Sutter et al., 2021); DVM (natural images
plus tabular data, car-related); UK Biobank (cardiac MR images plus tabular features; CAD and
myocardial infarction tasks). Accuracy for all but UKBB, AUC for UKBB. Missingness: PolyMNIST
rho in {0, 0.2, 0.4, 0.6, 0.8}; MST and CelebA modality combinations; DVM and UKBB tabular rates
{0, 0.1, ..., 1}. No language-model, diffusion or captioning task is evaluated.

## 6. Claim-evidence list

| # | Paper reports | Location | Note |
|---|---|---|---|
| C1 | Naively fusing all recovered modalities can be worse than using only the observed ones (the "discarding-imputation dilemma"). | Sec. 1 p1-2; App. C.2 Fig. S1(b); Table 2 "Baseline" row | Table 2 shows Baseline below S, I and I+C on most columns, but not all. |
| C2 | Modality-level reward selection raises accuracy: PolyMNIST at rho = 0.8 goes from 84.21 (fuse all) to 96.61 (full DyMo, I + C). | Table 2, p9 | Parsed from extracted table text; confirm the column order against the PDF image before quoting the numbers. |
| C3 | The calibration term is not uniformly helpful: on CAD and Infarction, I (without C) scores higher than I + C, which the authors attribute to conservatism. | Sec. 4.2 p9; Table 2 | Paper's explanation, untested. |
| C4 | Against dynamic-fusion baselines (QMF, DynMM, PDF) and incomplete-MDL baselines, DyMo is better, for example +13.12% accuracy on PolyMNIST at 80% missing, +4.11% on DVM with the full table missing. | Sec. 4.1 p7-8, Fig. 3, Table 1 | Headline gaps from the text; the Fig. 1 caption quotes 1.61, 1.68 and 3.88 points against other baselines. I did not re-derive them from Table 1. |
| C5 | The selection is robust to the recovery generator and to recovery quality (MoPoE, MMVAE+, CMVAE; a controlled "correct recovery rate" stress test). | Sec. 4.2 p9-10, Table 3; App. C.2 Fig. S2 | Results are mostly shown in figures; the stress test uses ground-truth versus zero-noise recoveries, a synthetic setting. |
| C6 | The theory links loss decrease to a lower bound on mutual information. | Eq. 2 p4; App. A.1 | The bound uses true labels and the full test set size; inference uses predicted labels per sample, so the per-sample reward is a heuristic proxy. Table S6 gives the G-term as below 0.006, though its caption says 80% missing and the text says 60% (App. C.4). |

## 7. Stated and unstated limitations

- Stated: recovery quality limits gains; some correct predictions turn wrong after selection (Sec. 4.2 p10);
  extension to other tasks and modalities is future work (Sec. 5, App. D); calibration may need a
  dataset-specific scale (p9).
- Unstated or only implied: classification only; modality-level units (no sub-modality or token gate);
  prototype-based rewards need a representation space with class structure, so they do not transfer
  directly to generative or masked-diffusion models; simulated missingness on benchmarks; reliability
  is judged from model confidence and class-cluster fit, not from any external signal.
- Appendix search: no "reliability score" is defined as such. The only per-sample quality quantities are
  the MTIR reward and the ICS score (and the lambda ratio).

## 8. Proposed Related Work sentence (one sentence, 36 words)

> DyMo [X] selects, at inference, which recovered modalities to fuse in incomplete multimodal classification, using a loss-derived, prototype-based reward on whole modalities; we study token-level gating and learned weighting inside one unified masked diffusion model.

Why this wording is accurate: "recovered modalities" (it never gates observed ones), "at inference" (selection step), "loss-derived, prototype-based reward" (Eq. 4 and 6), "whole modalities" (Algorithm 1), "classification" (scope). It makes no claim that DyMo is unreliable or that our gate is better.

## 9. BibTeX (IEEE style, inproceedings; fields verified against the PDF header and arXiv metadata)

```bibtex
@inproceedings{du2026dymo,
  author    = {S. Du and X. Luo and D. P. O'Regan and C. Qin},
  title     = {Inference-Time Dynamic Modality Selection for Incomplete Multimodal Classification},
  booktitle = {Proc. Int. Conf. Learn. Represent. (ICLR)},
  year      = {2026},
  note      = {arXiv:2601.22853}
}
```

Pages, city and DOI are left out because the PDF does not give them. If the IEEE template renders
the arXiv note awkwardly, drop the `note` field or replace it with the ICLR/OpenReview record once
looked up.
