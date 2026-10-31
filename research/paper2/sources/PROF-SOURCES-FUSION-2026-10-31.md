# Professor's three fusion papers (2026-10-31): readings, verdicts, citation sentences, baseline plan

Read in full from the converted text in `research/sources/md/prof-2026-10-31/` (0128.md, 2603.26629v2.md, Data-and-Model_Uncertainty-Aware_Multimodal_Dynamic_Fusion.md). The folder also holds `2212.08044v3.md`, which was not part of this request and was not read.
Page numbers below are the numbers printed in each PDF; the two-column conversion can shift a locator by one page. No manuscript file was edited and nothing was computed.
Bibliographic status: P1 verified on ijcai.org (proceedings page, pages, DOI 10.24963/ijcai.2026/128); P2 verified on arxiv.org (v1 27 Mar 2026, v2 26 Jun 2026, no venue field); P3 the DOI is printed in the file ("accepted for publication", author's version) and a web search did not index the paper, so volume, issue and pages are unverified (early access).

## 0. Bibliographic data (IEEE-style BibTeX)

```bibtex
@inproceedings{han2026aemrl,
  author    = {Han, Yupeng and Zhang, Kai and Wang, Xianquan and Pan, Zhihong and Liu, Ze and He, Jiyuan},
  title     = {Trust, but Verify: Uncertainty-Driven Evidential Multimodal Representation Learning},
  booktitle = {Proc. 35th Int. Joint Conf. Artif. Intell. (IJCAI-26)},
  year      = {2026},
  pages     = {1143--1151},
  doi       = {10.24963/ijcai.2026/128}
}

@misc{tenali2026c2mf,
  author        = {Tenali, Pranuthi and Sidheekh, Sahil and Mathur, Saurabh and Blasch, Erik and Kersting, Kristian and Natarajan, Sriraam},
  title         = {Context-specific Credibility-aware Multimodal Fusion with Conditional Probabilistic Circuits},
  year          = {2026},
  howpublished  = {arXiv preprint arXiv:2603.26629v2},
  eprint        = {2603.26629},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG}
}

@article{guo2026dmmf,
  author  = {Guo, Jie and Liu, Yue and Ma, Yuling and Liu, Meng and Qiu, Lanting and Zhang, Yanhui and Nie, Xiushan and Guo, Ying and Yin, Yilong},
  title   = {Data-and-Model Uncertainty-Aware Multimodal Dynamic Fusion},
  journal = {IEEE Transactions on Circuits and Systems for Video Technology},
  year    = {2026},
  note    = {early access, accepted},
  doi     = {10.1109/TCSVT.2026.3727902}
}
```

Title clash to fix in the Related Work: the paper at P1 has the same title as the already cited `jhingran2026trustverify` ("Trust but verify: Designing region-inhomogeneous forward dynamics for discrete diffusion", arXiv 2610.22380), which is a different paper. A reviewer who knows both will confuse them. Cite P1 by key `han2026aemrl` and by the acronym AEMRL, and name the other one by its topic ("region-inhomogeneous forward dynamics"), never by "Trust but Verify" alone (related.tex:36-37).

## 1. What each paper weights, and how

| | P1 AEMRL (IJCAI-26) | P2 C2MF (arXiv) | P3 DMMF (IEEE TCSVT) |
|---|---|---|---|
| Unit weighted | modality (2 to 3: image, text, IMU, audio, video) | modality (2: image/audio; RGB/depth) | modality (2 to 3) |
| Object fused | Dirichlet evidence vectors of each modality (class evidence), then conflict-scaled | unimodal predictive distributions p_m, fused by a Conditional Probabilistic Circuit | unimodal predictions y^(b) (Eq. 20) |
| Reliability source | learned: evidence head per class (D-EUE); U_m = C / S_m, reliability 1 - U_m (Eqs. 1-2, p.1145); weight alpha_m = R_m (1 - U_m) / sum (Eq. 12, p.1146), R_m = MI lower bounds (Eq. 11) | learned: joint context z = M(h_1..h_M, l_1..l_M) (embeddings plus corruption embeddings l_m = E_m(k_m)), hypernetwork g sets the circuit's sum-node weights (Sec. III-B/C, Alg. 1); per-instance credibility CSIC_i = KL(P(Y given x, z) to P(Y given x without x_i, z)), computed exactly in the circuit (Sec. III-D) | learned: data (aleatoric) uncertainty from a sparse variational GP on modality features (Eqs. 6-12, Sec. III-B); model (epistemic) uncertainty from feedback-adjusted MC dropout, T = 70 samples (Eqs. 13-17, Sec. III-C); u_total = gamma u_data + (1 - gamma) u_model with gamma learnable (Eq. 18), w_b = (1/(u_total + eps)) / sum (Eq. 19) |
| Data vs model split | no (intrinsic, relational, aggregated levels) | no | yes, the core of the paper |
| Training | end to end with the task loss (+ MI, orthogonality, KL terms) | end to end (joint) or decoupled, class-supervised | end to end, cross-entropy + ELBO (Eq. 23) |
| Datasets | MIMIC-CXR, Drive&Act, VGG-Sound, Hateful Memes, MM-IMDb (Sec. 4.1) | Conflict-AV-MNIST (55k/5k/10k), Conflict-NYUD (10 classes, 1,863 pairs) (Sec. IV-A) | SUN RGB-D, NYUD v2, UPMC Food-101, MVSA-Single, Micro Scene10 (TikTok and Vine, 7,236 videos) (Sec. IV-A to IV-C) |
| Corruption tested | Gaussian blur on the image modality of MIMIC-CXR (Sec. 4.5, Fig. 4, pp.1148-1149); missing modality (Sec. 4.6, Fig. 5); semantic conflict bins (Sec. 4.4, Fig. 3) | class-aligned replacement of one modality by another example's content, conflict ratio 0 to 1 (Sec. IV-A, Table I, Fig. 2); metric RMIS (Sec. IV-C) | Gaussian noise on 50 % of modality inputs, average and worst case (Table I, Sec. IV-A); salt-and-pepper (Fig. 6, Sec. IV-D) |
| Generative model, likelihood ratios, tokens | none; classification | none; classification | none; the only mention of "token" is the limitations paragraph |

Extra facts for a rebuttal.
- P1: all weights are normalised across modalities (Eq. 12) and the fused evidence is then scaled by 1/(1 + 2.5 x symmetric KL) (Eqs. 13-14). The paper reports averages over five seeds (Sec. 4.1).
- P2: the corruption mask k_m is an input of the encoder; the text says it "can be estimated from the data" (Sec. III-A) but the experiments use the known synthetic corruptions. Headline: up to 29 % accuracy over static-credibility baselines (abstract). The static predecessor is Sidheekh et al., AISTATS 2025 (cited as [7] in P2, not read).
- P3: its conclusion states that modelling "is at the modality level" and lists "feature, token, or region level" uncertainty as a limitation and future direction (conclusion, p.12-13). P3 also admits it does not always win under heavy Gaussian noise because noise hits several modalities at once (p.12-13). Training is on clean data and the test is noisy, which is the same pattern as our Study 2.

## 2. Closest point of contact with our work

- P1: Sec. 3.4 Eqs. 11-14 (reliability times relevance weights applied to a sum of evidence), Sec. 4.5 Fig. 4 (image corrupted at test, image weight alpha_img falls). Same idea: down-weight an unreliable image source in an evidence sum. Different: unit is a modality, evidence is a Dirichlet class belief from a trained head, weights come from the same trained network.
- P2: Sec. III-B/C and Fig. 1 (weights set from a learned context of the input features, including a corruption code). Closest in spirit to "weights as a function of features of the unit" and to the preregistered-style corruption benchmark. Different: modality unit, probabilistic circuit, synthetic class-aligned conflict, no pixel corruption.
- P3: Eqs. 18-20 (u_total mixing data and model uncertainty, inverse-uncertainty weights), Table I (Gaussian noise protocol). Closest in test protocol (train clean, test noisy, report mean and worst). Different: modality unit and uncertainty from MC dropout and a GP.
- None reads or combines log-likelihood ratios of a generative model, none uses caption-withheld (or any withheld-condition) scores as reliability features, none works on tokens.

## 3. Verdicts (hostile TNNLS reviewer who knows these papers)

(a) Novelty threat. None of the three threatens the claim as it is worded in related.tex:58-60 ("per-token, caption-withheld weights for the log-likelihood-ratio evidence of a unified masked diffusion model ... fresh images under image corruption"). Granularity (token), evidence type (log-likelihood ratio of a generative scorer) and weight inputs (withheld-condition features, never the evidence) are all absent from them. P3 even names token level as open.
What they do remove: the generic claims. "Reliability-weighted fusion under noise" and "uncertainty-derived weights" are established; the novelty sentence must stay on granularity, evidence type, frozen scorer, and confirmation on a fresh fold. Do not write "first to weight evidence by reliability" anywhere.
Likely reviewer attacks and answers.
1. "All three train the weighting jointly with the task head; yours is a post-hoc stacked combiner." Answer: true, by design (the scorer is a frozen published model; the paper's point is that no retraining is needed); the weighting is preregistered and confirmed on fresh images. Say "stacked on a frozen scorer" once, in Study 2.
2. "Evidential fusion (P1, Han 2023) is the standard answer; where is it?" See Section 5; this is the only addition worth considering.
3. "Their weights are normalised across sources." The decision rule sign(sum w_j Delta_j) is invariant to any positive per-image constant, so normalisation (Eq. 12 of P1, Eq. 19 of P3) changes nothing for the decision here; only the shape of w as a function of uncertainty matters. This is worth one sentence if asked, not in the paper.
4. Title confusion with `jhingran2026trustverify` (Section 0).

(b) What to cite, and where (Related Work is near full; one clause each, all in the paragraph "Reliability-aware and dynamic fusion", related.tex:40-60).
- P1 `han2026aemrl`: attach to the evidential sentence (related.tex:46-47), next to `shao2024ddef,huang2025evidential`. It is the closest evidential work that tests an image-corruption sweep. Cite.
- P3 `guo2026dmmf`: attach to the sentence on dynamic weighting (related.tex:44-45), next to `zhang2023provable`; also supports the sentence "At a finer grain" because it names token-level uncertainty as open. Cite. It is an IEEE Transactions paper (TCSVT), not TNNLS, so it does not count toward the "cite target-journal papers" rule; keep it only because it is the paper the professor sent and is on topic.
- P2 `tenali2026c2mf`: attach to the closing precedent sentence (related.tex:55-56) and to the first sentence of Sec. "The Frozen Weighting" (study2.tex ~line 35, cite list `chair1986optimal,kittler1998combining,zhang2023provable,han2023trusted,li2026tcpfmc`). It is a preprint (no venue); cite it as such, and cite it only once. Weakest of the three; the one to drop if space runs out.
Order of priority if only two fit: P1 and P3.

Proposed sentences (each at most 30 words; insert after the existing citations of the same kind).
1. P1: "AEMRL derives a Dirichlet reliability for each modality and keeps its accuracy as the image is blurred~\cite{han2026aemrl}, but its weights belong to whole modalities of a trained classifier." (28 words)
2. P3: "Separate data and model uncertainties of each modality set its weight, with robustness to Gaussian and salt-and-pepper noise~\cite{guo2026dmmf}; its authors name token-level uncertainty as open." (28 words)
3. P2: "Context-specific credibility, conditioned on a learned embedding of the input and its corruption, is the closest idea to feature-driven weights~\cite{tenali2026c2mf}, applied to modalities of a classifier." (26 words)
Disambiguation edit for related.tex:36: replace "Trust but Verify detects corrupted context tokens in a finetuned text-only masked diffusion model~\cite{jhingran2026trustverify}" by "a region-inhomogeneous forward process detects corrupted context tokens in a finetuned text-only masked diffusion model~\cite{jhingran2026trustverify}" (no new numbers; wording only).

## 4. Candidates considered and rejected

- DMMF data-versus-model uncertainty split (Eqs. 18-19). Not constructible faithfully from the stored arrays: the aleatoric term needs a GP head and the epistemic term needs MC-dropout or ensemble variance, and neither was stored (B is one value per token from one random partition, no spread over passes). Any relabelling of s3 as "model" and nbr or tex as "data" is a relabelled feature subset. The model-uncertainty-only inverse weight is already covered by A-UNL (w_j = 1 - rank_s3_j), A-S-s3 and A-S-nbr/A-S-ltex (supplement S-VII, analysis/paper2/lrf/ablation.py:421-436). The only new thing would be the inverse form 1/(s3 + eps) in place of the rank, which is a shape change of an existing row. Not worth a row.
- C2MF credibility (CSIC) from the evidence alone. With p = sigmoid(S) and the leave-one-out posterior sigmoid(S - Delta_j), a parameter-free credibility C_j = KL(Bernoulli(sigmoid(S)) to Bernoulli(sigmoid(S - Delta_j))) is computable. But it is an influence measure that grows with |Delta_j|; it makes the weight depend on the evidence, which LRF excludes by design ("No feature uses Delta_j", study2.tex), and for small Delta_j it gives roughly a cubic-power sum, which is a different thing from reliability. In C2MF itself the credibility only tracks reliability because training aligns it. Rejected as misleading.
- AEMRL weight R_m (1 - U_m). Needs a relevance score from learned MI critics; no analogue without fitting. Rejected.

## 5. One cheap exploratory baseline worth adding: Dempster combination of evidence-derived token opinions (E4)

Why a reviewer would ask: the Related Work names evidential and Dempster-Shafer fusion (`han2023trusted`, `shao2024ddef`, `huang2025evidential`, now `han2026aemrl`) as the nearest family, and Table IV has no evidential row. It differs from every existing row: it is an unlearned combination whose per-token influence comes from the evidence magnitude and an optional discount, not from a rank, a location statistic, or a fitted model.

Honest limits to state in the paper if the row is added: TMC and AEMRL obtain opinions from trained evidential heads with an evidential loss. A frozen generative scorer has no such head, so the opinions below are constructed from Delta_j. The row is "Dempster combination of evidence-derived opinions", not a reproduction of TMC or AEMRL. The nats-to-evidence scale is arbitrary, so one scale is fixed in advance and two others are shown only as a sensitivity check.

Definition (frame {c+, c-}, K = 2, Dirichlet prior a = 2, standard in evidential deep learning; no fitting; inputs only `<cond>_delta` and, for the discounted variant, `<cond>_s3`).
1. Per token j: e+_j = lam * max(Delta_j, 0), e-_j = lam * max(-Delta_j, 0), S_j = e+_j + e-_j + 2, belief b+_j = e+_j / S_j, b-_j = e-_j / S_j, uncertainty u_j = 2 / S_j. Primary scale lam = 1 (Delta in nats). Sensitivity: lam in {0.1, 10}, supplement only.
2. Reliability discount r_j in [0, 1] (Shafer discounting): m(+) = r_j b+_j, m(-) = r_j b-_j, m(Omega) = 1 - r_j (1 - u_j). Primary row: r_j = 1 - rank_s3_j, the same unlearned weight as A-UNL (the project's `data._rank`, within-image percentile rank of s3, as in `unl_weights`). Reference row: r_j = 1 for all j (no discount).
3. Combine the 1,024 token masses with Dempster's rule. Because Dempster's rule multiplies commonality functions, the decision needs no sequential combination: with q_j(+) = 1 - r_j b-_j and q_j(-) = 1 - r_j b+_j (the commonalities after discounting; for r_j = 1 these are b+_j + u_j and b-_j + u_j), choose c+ if D = sum_j [ log q_j(+) - log q_j(-) ] > 0, else c-; a tie counts as wrong, as in all other rows. Derivation checked by hand on two tokens (Delta = +2, -1): the sequential Dempster result b+/b- = 2 equals the commonality route (q(+) - q(Omega)) / (q(-) - q(Omega)) = 2, and the sign of the log product ratio agrees.
4. Closed form without discount: D = sum_j sgn(Delta_j) log(1 + lam |Delta_j| / 2). So the undiscounted rule is a log-compressed sum of the evidence; it equals the unweighted sum as lam goes to 0 and a majority vote of token signs as lam goes to infinity. With discount and small |Delta_j|, D is about (lam / 2) sum_j r_j Delta_j, i.e. A-UNL; the rows differ only through tokens with |Delta_j| of order 1 or larger. This predictable behaviour is stated now so the result cannot be read as a surprise: the expected outcome is a row within noise of A-UNL and of the unweighted sum, which is itself the useful answer to "why not evidential fusion".

Protocol (exploratory, no test, no tuning, identical in format to E2).
- Data: the 450 fresh-fold items x 4 conditions (clean, jpeg10, noise0.1, splice128) in `runs/P2-LRF-L1/arrays/item*.npz`. No design-item data, no refit, no change of any frozen object.
- Consistency gate before writing anything: recompute the unweighted rule from `<cond>_delta` and match the stored `y_none`; recompute A-UNL from `<cond>_s3` and match the stored A-UNL cell of `runs/P2-LRF-ABL-SCORE` (the code route of `analysis/paper2/lrf/e2_combiners.py`, which already does this for NONE).
- Reported: accuracy per condition; paired difference against NONE, against A-UNL and against LRF with discordant counts and the same unadjusted 95 % interval as the other Table IV rows; ties and empty sets wrong. Also report, descriptively, the median and the 95th percentile of |Delta_j| over the fold so that the compression regime is visible (this is read after the accuracies are fixed and does not feed any choice).
- Outputs: a new `runs/P2-LRF-E4/` directory from a script modelled on `analysis/paper2/lrf/e2_combiners.py`, with a plan file `research/paper2/tnnls/EXPLORATORY-PLAN-EVIDENTIAL-<date>.md` committed before the first run. Cost: CPU only, seconds; no GPU.
- Placement: one row group in supplement S-VII (the page cap is nearly reached) plus one clause in Sec. "Comparison With Alternative Aggregation Rules (Exploratory)" and one sentence in the Limitations that the opinions are constructed, not learned. Label it exploratory, specified after the Study 2 results, with no test.
- Stop rule: no variant beyond the three scales and the two discount settings listed above; no choice of lam by accuracy; the primary row is lam = 1 with the A-UNL discount, fixed here.

Call: worth doing only because it is minutes of CPU and removes a predictable reviewer question. If the plan cannot be committed before the next compile, the alternative is no computation and one sentence in the Limitations: "Evidential opinions need a trained head per source; the frozen scorer provides none, so we did not construct them." The data-versus-model uncertainty split and the CSIC credibility are not worth computing.

## 6. Unverified items
- P3 volume, issue, pages and publication date (IEEE Xplore not reachable here; DOI from the file).
- P2 has no venue; check on submission day whether a venue has been added to arXiv.
- P1 DOI and page range were read from the proceedings page by web search, not from the DOI resolver.
- Sidheekh et al. AISTATS 2025 (static credibility, reference [7] of P2) was not read; do not cite it from this file.
- The scale of Delta_j is unknown to this note by design (not computed); the claim that the Dempster rule is close to the unweighted sum depends on |Delta_j| being mostly below 1.
