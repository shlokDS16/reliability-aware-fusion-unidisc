```yaml
agent: novelty-auditor
date: 2026-10-28
brief: Check whether Zhou & Lu 2027 (Inf. Fusion 139:104860, "Burden of proof ...") or Wang 2025 (Inf. Fusion 120:103068, corrigendum 103287) reduce GATE's novelty delta; list sentences to add and claims to soften.
sources_examined:
  - "doi:10.1016/j.inffus.2026.104860 Zhou & Lu 2027 - NO full text obtained (closed access). Read: Crossref record (title, authors, 35-entry reference list, license, issued 2027-03; no abstract field); OpenAlex record (no abstract, is_oa=false, no repository copy); Unpaywall (closed); ebiotrade.com mirror (mojibake, only English fragments readable); the scout's earlier ScienceDirect-preview notes in research/paper2/related/INFFUS-CITATIONS-2026-10-28.md (abstract, highlights, introduction, contributions, first conclusion paragraph; second-hand here, my own re-fetch of the ScienceDirect page returned HTTP 403)"
  - "doi:10.1016/j.inffus.2025.103068 Wang et al. 2025 - open access (hybrid, CC BY-NC); PDF from the University of Reading repository https://centaur.reading.ac.uk/121660/3/1-s2.0-S1566253525001411-main.pdf, converted with markitdown to the session scratchpad; read abstract and Sec. 3.3 (conformal method, Algorithms 1-2, Theorem 1) fully, rest by grep"
  - "doi:10.1016/j.inffus.2025.103287 corrigendum - Crossref and OpenAlex records only (title, authors, update-to, issued 2025-10); body NOT retrieved"
  - "research/paper2/ideation/NOVELTY-REAUDIT-GATE-2026-10-28.md, research/paper2/related/CLOSEST-WORK-2026-10-28.md (header), research/paper2/related/INFFUS-CITATIONS-2026-10-28.md (context)"
coverage: >
  Zhou & Lu: bibliographic metadata and reference list (E1) plus the scout's preview-level reading (E1+). Method, theorem statements, experiments, appendix, limitations
  were NOT read by me and not by anyone in this project, so every statement about Zhou & Lu's method is E1. No attempt was made to bypass the paywall (no use of the
  Elsevier text-mining API links listed in Crossref, which need an API key and are licensed for text mining from 2027-03-01). Wang: abstract and Sec. 3.3 read; Sec. 2, 4, 5
  and supplementary material not read; corrigendum content unknown. Search for other IF concurrent work was not repeated (scout covered it); only the queries below were run.
claims:
  - statement: "Zhou & Lu decide, per test instance, whether a challenger's whole prediction replaces a default's prediction in few-shot vision-language recognition; the unit of decision is a prediction, not an input token of a generative model."
    status: supported
    evidence: "scout's preview notes (INFFUS-CITATIONS rows 1 and section 3); ebiotrade English fragments (keywords 'Few-shot recognition', 'Decision-level fusion', 'Dempster-Shafer'); Crossref title 'asymmetric decision-level fusion in vision-language recognition'"
    level: E1
    confidence: 0.85
  - statement: "Zhou & Lu's reliability signal is Dempster-Shafer mass built from frozen CLIP (text alignment) and DINOv3 (visual support) channels and combined with Dempster's rule, conflict mass K kept as a diagnostic; no generative likelihood is used."
    status: supported
    evidence: "scout's preview notes; ebiotrade fragments ('Calibrated Evidential Arbitration, CEA', 'CLIP', 'DINOv3', 'a photo of a {class}'); reference list contains evidential and DS papers (Sensoy 2018, Han 2023 TPAMI, Shao 2024, Huang 2025) and no masked-LM, PLL or diffusion paper"
    level: E1
    confidence: 0.8
  - statement: "Zhou & Lu's threshold is selected with a Clopper-Pearson upper bound on a selective-risk proportion (harmful overwrites), which needs correctness labels on a calibration set; its reference list cites Conformal Risk Control (Angelopoulos et al. 2024) and a second Angelopoulos et al. 2025 AOAS paper (doi 10.1214/24-AOAS1998, title not retrieved by me)."
    status: supported
    evidence: "scout's preview notes for the Clopper-Pearson step; Crossref reference list entries 27 and 28 for the citations"
    level: E1
    confidence: 0.75
  - statement: "Zhou & Lu mention no corrupted, noisy or missing-modality scenario, no token-level gating, no masked or diffusion model, and no conformal prediction beyond citing CRC."
    status: unknown
    evidence: "Absent from the abstract, highlights, introduction, contributions and first conclusion paragraph as the scout read them, and absent from the 35 references. The ebiotrade mirror is mojibake, so its silence is not evidence. Experiments and appendix unread."
    level: E1
    confidence: 0.6
  - statement: "Wang et al. 2025 attach split conformal prediction (prediction sets, marginal coverage 1 - alpha under i.i.d., Theorem 1) to a multi-stage text-plus-tabular fusion network for rheumatic-disease risk stratification; empty or multiple-label sets are flagged for clinician review. The unit is the patient-level prediction. Nothing token-level, no corrupted-modality test, no diffusion or generative likelihood."
    status: supported
    evidence: "Wang abstract and Sec. 3.3 (Algorithms 1-2, Theorem 1); grep for token/diffusion/corrupt/missing modality/risk control/exchangeab found only the 512-token text truncation in the text encoder"
    level: E2 (abstract and Sec. 3.3), rest unread
    confidence: 0.85
  - statement: "Wang's corrigendum (Inf. Fusion 122, 103287, 2025-10) exists; what it corrects is unknown."
    status: unknown
    evidence: "Crossref: title and update-to (type erratum) only; OpenAlex: no abstract, no PDF URL"
    level: E1
    confidence: 0.95
  - statement: "Neither paper reduces GATE's novelty delta as defined in the 2026-10-28 re-audit (input-token reliability from within-modality masked likelihood in a pretrained unified masked-diffusion model, with a conformal-risk-control clean false-alarm threshold and cross-modal verification). Zhou & Lu narrows one framing sentence."
    status: supported
    evidence: "difference table below; every cell for Zhou & Lu is E1"
    level: E1 for Zhou & Lu, E2-partial for Wang
    confidence: 0.75
competing_explanations:
  - "A reviewer who knows Information Fusion may read Zhou & Lu as 'calibrated, risk-bounded gate on whether to trust a source in a vision-language decision', and GATE as the same idea at token level. The difference is real in unit, score and guarantee, but the sentence 'a risk-calibrated gate for source trust in vision-language fusion' is no longer ours."
unknowns:
  - "Zhou & Lu Sections 3-5: exact risk definition, whether the calibration is CRC-like or Learn-then-Test-like, calibration set sizes, whether labels are used, benchmarks, any noise or corruption experiment, limitations."
  - "Wang corrigendum content."
  - "Whether Zhou & Lu has a preprint or code (none found)."
next_test: n/a
```

# Novelty check: Zhou & Lu 2027 and Wang 2025 (Information Fusion) against GATE

## 0. Verdict

**Per the project's vocabulary: no change to the standing verdict (`incremental`, narrow delta still open, 0.50 for the composed delta, from NOVELTY-REAUDIT-GATE-2026-10-28).**
- **Zhou & Lu 2027: related, not a scoop.** Confidence 0.75 that it does not reduce the delta; **E1 only** because the paper is closed access and nobody on the project has read past the preview. It does remove one framing sentence (see section 3).
- **Wang et al. 2025: related, no overlap with the delta.** Confidence 0.85 (E2 for the conformal method; corrigendum content unknown).
- Paper most likely to be cited against us among the two: **Zhou & Lu**. Paper most likely to be cited against us overall remains **Trust but Verify, arXiv 2610.22380** (unchanged).
- Residual risk: Zhou & Lu's experiments and appendix are unread. A single corruption or token-level experiment in them would change this. Read it before submission (section 5).

## 1. Full-text status

| Paper | Open access? | What I could read | Level |
|---|---|---|---|
| Zhou & Lu, Inf. Fusion 139 (2027) 104860, online 2026-10-13 | **No.** Crossref/OpenAlex/Unpaywall: closed, no repository copy, no arXiv/preprint found, no code link. ScienceDirect page returned 403 to my fetch. | Metadata, 35-entry reference list, scout's preview notes, a mojibake mirror | E1 |
| Wang et al., Inf. Fusion 120 (2025) 103068 | **Yes** (hybrid, CC BY-NC); University of Reading repository copy | Abstract, Sec. 3.3 in full; grep of the rest | E2-partial |
| Wang corrigendum, Inf. Fusion 122 (2025) 103287 | Hybrid per OpenAlex, but no PDF URL; body not retrieved | Title, authors, update-to type erratum | E1 |

**Paywall:** Zhou & Lu is on ScienceDirect only. Shlok can provide access through the VIT library e-gateway (ScienceDirect often blocks automated saves, so the PDF may need to be downloaded by hand in the browser). I did not use the Elsevier text-mining links in the Crossref record and did not try to bypass the paywall.

## 2. Comparison table

S = same, P = partial, D = different, relative to GATE. Zhou & Lu cells are E1 (abstract, preview, references). Wang cells are E2 for the conformal method.

| Axis | GATE | Zhou & Lu 2027 | Wang et al. 2025 |
|---|---|---|---|
| Unit of decision | Each **input token** (image code or caption word) of an observed pair | One **whole prediction** per test instance: keep default or override with challenger (**D**) | One **patient-level prediction**; empty or multi-label set flagged for review (**D**) |
| Source of reliability score | Masked likelihood of the token within its own modality, other modality withheld, from a generative masked-diffusion model | Dempster-Shafer masses built from frozen CLIP and DINOv3 similarity outputs, Dempster's rule, conflict mass K (**D**) | Classifier softmax nonconformity scores of a trained fusion network (**D**) |
| Calibration guarantee | Conformal risk control: expected clean false-alarm proportion at most alpha, calibrated on clean pairs, no corruption labels | Clopper-Pearson upper bound on proportion of harmful overwrites (selective risk); needs correctness labels on calibration conflicts; cites CRC and a second Angelopoulos 2025 paper, so the method is in the same distribution-free family (**P**: same family, different risk, different bound type) | Split conformal, marginal coverage 1 - alpha under i.i.d. (Theorem 1) (**P**: conformal, different quantity) |
| Model class | Pretrained unified text-image masked discrete diffusion model (UniDisc 1.4B), no training | Frozen CLIP + DINOv3 (and per the mirror InternVL3-8B, Qwen2.5-VL as models); trains nothing (**P**: pretrained, frozen, but discriminative VLMs) | Trained text encoders (BERT-type, 512-token inputs) plus tabular branch (**D**) |
| Task | Two-way image-text verification, matching and repair under input corruption | Few-shot recognition on four benchmarks (**D**) | Clinical risk stratification (**D**) |
| Corruption of an input source | Central (JPEG, noise, splice, patch, swap) | Not mentioned in anything read; E1 only; **unknown** | Incomplete records are a motivation; no corruption experiment found in the parts read (**D**) |
| Action after flag | Drop, re-mask (marginalise) or re-infill the token | Replace the default's prediction with the challenger's (**D**) | Defer to a human (**D**) |
| Evidence-theory content | None (PMI fusion, not DS) | Core (**D**) | None |
| Overlap with our must-not-claim list | none directly | #3 in spirit (risk-controlled threshold in vision-language) but at prediction level; see section 3 | none |

Net: of the six axes in the brief, Zhou & Lu matches GATE on none exactly; it is partial only on calibration family and on "pretrained, frozen, no training". Wang is partial only on "conformal".

## 3. Does either paper reduce the delta?

**Zhou & Lu: reduces one framing claim, not the delta.**
- Delta as defined in the re-audit: input-token reliability from within-modality masked likelihood in a pretrained unified masked-diffusion model, plus CRC clean false-alarm control, plus cross-modal verification. None of the three is in Zhou & Lu as far as E1 shows.
- What it removes: any sentence that says or implies that a **calibrated, risk-bounded decision about whether to trust a source** is new in vision-language fusion, or that **pretrained, no-training, threshold-from-held-out-data gating** is new. A reviewer from Information Fusion will have it in mind.
- It also strengthens the existing must-not-claim #3 and #7: Gomes et al. (2504.01225) were the prior art for CRC with masking scores in vision-language; Zhou & Lu is now the prior art for a risk-bounded keep-or-override gate between vision-language sources.
- Risks that I cannot close at E1: (a) its calibration may be CRC- or Learn-then-Test-like with a search over thresholds, in which case "calibration by risk control" is thoroughly established in the journal; (b) it may contain a noisy-channel or corrupted-image experiment, which would put its task closer to ours than the abstract suggests. Neither is indicated by anything read, and the 35 references contain no corruption-robustness, masked-LM or diffusion paper.

**Wang et al.: does not reduce the delta.** It shows only that conformal prediction is accepted in Information Fusion and gives a prediction-level medical example. Do not rely on its numbers (75.71 %, 66.67 %) given the unread corrigendum.

## 4. Claims to soften or avoid (additions to the must-not-claim list)

10. "First risk-calibrated or risk-bounded gate for deciding whether to trust a source or modality in vision-language fusion" (Zhou & Lu 2027). Also avoid "first to use a Clopper-Pearson or distribution-free bound to set a keep-or-override threshold for pretrained vision-language models".
11. "First use of conformal methods in Information Fusion / in a multimodal fusion network" (Wang 2025; Zhou & Lu cites CRC; the scout also lists Yumlembam 2024). Not a claim we need, but scope-fit text must not suggest it.
12. Any sentence that contrasts GATE with Zhou & Lu on points that only the full text can confirm (no corruption experiment, labels required, risk definition) unless worded "as described in the abstract" or checked in full text.
13. Wording "decision-level fusion" for GATE without qualification. Zhou & Lu uses that phrase for prediction-level arbitration; GATE acts before fusion, on inputs. Use "input-level source validation" or similar.
Existing #3 (Gomes) stays; extend its text to name Zhou & Lu alongside.

## 5. Sentences the paper must add (cite and differentiate)

All are written so they hold at E1 for Zhou & Lu. Upgrade the starred phrases after a full-text read.

**Related work, "Source validation before fusion":**
1. "Recent work in this journal bounds the risk of trusting a source at the level of a whole decision: Zhou and Lu [N] replace a default vision-language prediction by a challenger's only when a Dempster-Shafer evidence score clears a threshold chosen with a Clopper-Pearson bound on harmful overwrites*, and Wang et al. [N] attach conformal prediction sets to a text-and-tabular fusion network to flag predictions for human review."
2. "Both act on the output of a recogniser or classifier and calibrate on labelled predictions*; neither scores the individual input tokens of one modality, and neither uses the likelihood of a generative model."
3. "GATE differs in the unit (an input token, before any fusion), the score (the masked likelihood of the token inside its own modality with the other modality withheld), and the guarantee (a conformal-risk-control threshold calibrated on clean pairs that bounds the expected false-alarm proportion on clean inputs, with no corruption labels)."

**Discussion, "Where the work sits in information fusion":**
4. "The calibrated gate of Zhou and Lu [N] and ours answer different questions: theirs decides which of two recognisers to believe for one test instance; ours decides which input tokens to withhold before two directions of image-text evidence are combined. The two could be stacked, but we do not test this."
5. (Limitation) "Our guarantee covers false alarms on clean inputs only; unlike a selective-risk bound on the harm of an action [N], it says nothing about the harm or the power of the gate on corrupted inputs."

**Claims to soften in the draft:** replace "risk-calibrated" or "calibrated gate" as a selling point in the abstract and introduction by the specific property ("expected clean false-alarm proportion at most alpha, by conformal risk control"). Do not use "decision-level" for GATE.

Cite: Zhou & Lu [doi 10.1016/j.inffus.2026.104860]; Wang et al. [doi 10.1016/j.inffus.2025.103068]. Cite the corrigendum only if the correction affects what is cited (unknown). Budget: the reference cap is 50 and the bib is at 49, so each addition displaces an entry (decision belongs to the authors).

## 6. Actions needed before the paper relies on this check

1. **Full-text read of Zhou & Lu** through the VIT e-gateway (Shlok to download the PDF manually; ScienceDirect blocks automated saves). Checklist for the paper-reader: definition of the risk and of the selected set; whether labels are needed and calibration set sizes; whether the bound is per-threshold or with a multiple-testing correction; any noise, corruption or missing-evidence experiment; the four benchmarks; limitations; whether any token-, patch- or region-level analysis appears. Until then, every Zhou & Lu statement stays E1 and uses "as described in the abstract" phrasing.
2. **Corrigendum 103287**: open from the ScienceDirect link when the e-gateway is in use; one page.
3. Re-run this check if the full text shows a corruption experiment or a masked-likelihood-style score.

## 7. Search log (this run)

1. `Burden of proof: Calibrated evidential arbitration for asymmetric decision-level fusion in vision-language recognition` (web search: only the ebiotrade mirror and unrelated CARGO-VL 2608.04509, which is a different work; not read)
2. `Zhou Lu "Calibrated evidential arbitration" Clopper-Pearson Dempster-Shafer CLIP DINOv3 default challenger` (no hit)
3. `Guichao Zhou Yuwu Lu arXiv calibrated evidential arbitration vision-language few-shot Dempster-Shafer overwrite default prediction` (no hit; unrelated evidential VLM hallucination papers 2506.19513, 2602.05535 appeared; not read)
4. `Wang 2025 Information Fusion "Multi-stage multimodal fusion network with language models and uncertainty evaluation" rheumatic conformal prediction` (repository listing only)
5. API/page fetches: doi.org and ScienceDirect (redirect, 403); Crossref works for 104860, 103287; OpenAlex for 104860, 103068, 103287; Unpaywall for 104860; ebiotrade mirror (two prompts); Reading CentAUR PDF for Wang.

Last-90-days check for these two works: Zhou & Lu is 15 days old; no citations or preprint found. Not repeated for the wider field (see the re-audit, section 6). Absence of search results is weak evidence.

Ledger rows added: 0 (not requested). Candidate rows: Zhou & Lu 2027 (E1), Wang 2025 (E2-partial), corrigendum (E1).
