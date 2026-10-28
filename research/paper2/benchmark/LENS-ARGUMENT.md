```yaml
agent: paper-reader
date: 2026-10-28
brief: Argument, logic and writing lens on Moser et al., "Diffusion Models, Image Super-Resolution, and Everything: A Survey", IEEE TNNLS 36(7), 2025
sources_examined:
  - "Paper to refer/Diffusion_Models_Image_Super-Resolution_and_Everything_A_Survey.pdf (all 21 PDF pages read as images)"
  - "research/paper2/benchmark/sr-survey.md (grep only: counts of 'explainab', '[65]', 'criteria', 'benchmark')"
coverage: >
  Every page read: pp. 1-17 body (journal pages 11793-11809), pp. 17-21 references [1]-[185] and
  author bios skimmed for structure only (reference contents not audited). Not covered: whether any
  cited number in Tables I-IV matches the source papers; whether each reference supports its sentence.
  WebFetch of the IEEE TNNLS issue page returned HTTP 418 (blocked); journal scope NOT checked.
claims:
  - statement: "The survey has no stated literature-search method, inclusion criteria or screening procedure."
    status: supported
    evidence: "Whole text read; grep for 'criteria' returns 0; Section I p1-2 describes scope only in prose"
    level: E2
    confidence: 0.9
  - statement: "The abstract lists 'lack of explainability' as an open challenge, but no section of the body or Discussion develops it."
    status: supported
    evidence: "Abstract p1; Section VIII headings p16-17 (A-G); only passing remark on I2SB transparency p12"
    level: E2
    confidence: 0.85
  - statement: "The roadmap paragraph on p2 omits Section VI (zero-shot) and places null-space models under Section V."
    status: supported
    evidence: "p2 (11794) roadmap list vs. headings p13 (11805) and DDNM on p14 (11806)"
    level: E2
    confidence: 0.9
  - statement: "Classifier and classifier-free guidance are presented as an organising axis of the survey while the authors say they have not been applied to image SR."
    status: supported
    evidence: "Fig. 3 p9; Section V-B p9 (11801), sentence beginning 'To the authors' knowledge'"
    level: E2
    confidence: 0.8
competing_explanations:
  - "The thin evaluation material (4 small tables, none newly computed) may be an editorial choice for a TNNLS survey, not an oversight."
unknowns:
  - "Whether TNNLS survey submissions require a search protocol (journal page not retrievable)."
  - "Whether the tables copy numbers from the cited sources without change."
next_test: {hypothesis: "n/a (reading task)", intervention: "n/a", primary_metric: "n/a", falsifier: "n/a", gpu_hours: 0}
```

# LENS-ARGUMENT: how the SR survey argues, and how we beat it

Page convention: "p." is the PDF page (1 to 21); journal page = 11792 + p. Body runs to the middle of p.17. Numbers in the paper are the paper's reports (E2 for "the paper says", never for "it is true").

Size facts counted from the pages: 9 sections, 8 figures, 4 tables, numbered equations (1) to (47), 185 references, no appendix, no code or data release, no author-stated limitations of the survey itself.

---

## 1. Skeleton (page, job in the argument, length share)

Length shares are visual estimates of body space (about 16.8 body pages, accuracy about 0.3 page).

| Section | Pages | Job in the argument | Share |
|---|---|---|---|
| Abstract | 1 | Problem (DMs disrupt SR, but costs, comparability, explainability, colour shift, flood of papers); promise (unified theory, SR-specific analysis, five topic areas, future directions) | 1 page incl. intro start |
| I Introduction | 1-2 | Why SR is hard (ill-posed), why DMs matter, why a survey is needed now, how it differs from two prior surveys, roadmap | 8% |
| II Image SR | 2-4 | Problem statement and shared vocabulary. A Datasets (p2). B SR models: 1 traditional, 2 regression DL, 3 GAN, 4 flow (p2-3). C Quality assessment: PSNR, SSIM, MOS, consistency, LPIPS, no-reference (p3-4) | 14% |
| III DMs Basics | 4-7 | Theory spine. A DDPM, B score-based, C SDE (each: forward, backward, optimisation), D relation between the three, E relation to GAN, VAE, ARM, NF (p7) | 16% |
| IV Improvements for DMs | 7-8 | Generic DM tricks relevant to SR: A efficient sampling (training-based vs training-free), B improved likelihood | 7% |
| V DMs for Image SR | 8-13 | Core of the survey. A concrete realisation (SR3, SRDiff), B guidance, C state domains (latent, frequency, residual), D conditioning (LR, SR reference, feature, text), E corruption space, F colour shifting, G architecture | 26% |
| VI Diffusion-based zero-shot SR | 13-15 | A second axis (training requirement): projection, decomposition, posterior; Table IV | 12% |
| VII Domain-specific applications | 15-16 | Medical, blind face restoration, atmospheric turbulence, remote sensing; one paragraph per group of methods | 7% |
| VIII Discussion and Future Work | 16-17 | Seven open problems A to G | 8% |
| IX Conclusion | 17 | One-paragraph recap | 2% |
| References, bios | 17-21 | 185 entries | 4 pages beyond the body |

Argument shape: problem (II) then theory (III, IV) then method catalogue by axis (V, VI) then applications (VII) then open problems (VIII). Theory plus background (II to IV) takes about 37% of the body before the first SR-specific method appears (p8). This is a textbook order. A reader who knows DMs spends five pages on material they already have.

Mirror observation: the seven Discussion items mostly re-open earlier sections (A re V-F, B re IV-A and V-C, C re IV-A, D re V-E, E re II-C). Items F (image manipulation, p17) and G (cascaded generation, p17) introduce material that has no earlier section. Cascaded SR is named as a challenge in the introduction (p1) but gets one paragraph in VIII-G and a passing mention in V-B.

## 2. Positioning

- **Gap statement (abstract, p1).** Three moves: (1) DMs closed the gap between quality and human preference; (2) they bring new problems (computation, comparability, explainability, colour shifts); (3) "entry into this field is overwhelming" because of publication volume (abstract). The gap is a reader's problem (orientation), not a missing piece of knowledge.
- **Introduction (p1-2).** Order: SR is ill-posed; prior generative families each fail in some way (ARMs expensive, flows and VAEs lower quality, GANs unstable); DMs beat GANs; the literature is now too big; this article "bridges" foundations and the frontier. It then promises a critical analysis of strengths and weaknesses (p1). Whether that promise is kept: see section 4.
- **Comparison with other surveys.** Prose only, one paragraph on p1, no table. Two surveys named: the authors' own Hitchhiker's Guide [16] (broad SR) and Li et al. [17] (restoration, DMs). Stated overlap: DDPM, SGM, SDE foundations, conditioning, zero-shot. Stated difference: more detail on SR, SR-specific challenges (colour shifting, cascaded SR), relation to VAEs, GANs and flows, frequency-based DMs, alternative corruption spaces, applications. The Yang et al. ACM Computing Surveys paper [65] is in the reference list; I found no in-text citation of it (grep of the dump shows the number only in the reference list). So the closest general DM survey is not positioned against.
- **Stated contributions.** Not numbered. Four, spread over abstract and intro: (i) unified theoretical recount of DMs for SR; (ii) SR-specific analysis separate from broader reviews; (iii) coverage of input domains, conditioning, guidance, corruption space and zero-shot; (iv) evolution, trends, challenges and future directions.
- **Reader path.** One roadmap paragraph (p2) with one line per section. It has two faults: Section VI is missing from the list, and null-space models are attributed to Section V although they appear in VI (p14). Fig. 3 (p9) is the only visual map and it covers only Section V.
- **Overclaim check.** The abstract promises "a detailed examination of the evolution". The body has no timeline figure or table and no dated chronology. Evolution is implied by the order of sub-sections only.

## 3. Taxonomy logic

- **Axes (Fig. 3, p9, "Topology of this work").** Four questions about a DM for SR:
  1. Conditioning: what information guides sampling (LR reference, SR reference, feature reference, T2I information). Section V-D, p10-11.
  2. Guidance: how conditioning is strengthened during training or sampling (classifier, classifier-free). Section V-B, p9.
  3. State domain: how states are represented (pixel, latent, frequency, residual). V-C, p9-10.
  4. Corruption space: what is the target of the forward diffusion or the start of the backward one (Gaussian noise, Cold Diffusion, I2SB, InDI). V-E, p12.
  Plus a fifth axis outside the figure: training requirement (zero-shot), Section VI, p13-15, with its own three-way split (projection, decomposition, posterior) which the authors say is taken from Li et al. [17] (p13).
- **Orthogonality.** The figure frames axes as different questions, which is good, but nothing is tabulated. Methods are placed in prose, so one method appears under several axes: SRDiff in V-A, V-C3 (residual) and V-D3 (feature reference); ResDiff in V-C3 and V-D2; StableSR in V-D4, V-F (colour correction) and later; ILVR in V-D1 (LR conditioning) and again as a zero-shot method in VI-A. The reader has no method-by-axis matrix to see which combinations exist and which are empty.
- **Empty axis.** V-B says, to the authors' knowledge, classifier and classifier-free guidance have not been applied to image SR (p9). The axis is therefore populated by theory and not by SR methods. The figure presents it as equal to the others.
- **Order of presentation does not follow the figure.** Section V text order is guidance, state domain, conditioning, corruption space (then colour shift, architecture). Fig. 3 reads conditioning first.
- **Use of the taxonomy later.** Weak. Section VII (applications) is organised by domain and does not map back to the axes. Section VIII mostly follows problems, not axes (it revisits corruption space and sampling only). The taxonomy organises Section V and then stops working. No finding is stated in the form "axis X is crowded, axis Y is empty".
- **Roadmap items that are not axes.** Colour shifting (V-F) and architecture (V-G) are topics, not axes, but sit at the same heading level as the four axes with no marker.

## 4. Critical voice

The survey judges often, but in short, mostly general statements. Instances (one short phrase each, page):

| Where | Judgement | Specificity |
|---|---|---|
| p1 abstract | Names five problems of DMs | Named, not measured |
| p3 (II-B2) | Regression CNNs produce overly smooth textures at s > 4 | Specific scale threshold; cites [16] |
| p4 (II-C1) | PSNR does not match human perception; a slight pixel shift can lower it | Concrete mechanism |
| p4 (II-C) | MOS is "time-consuming and cumbersome" and susceptible to bias | Generic |
| p7 (III-E) | Each rival generative family given one weakness (flows hard to train, ARMs slow) | One-liners |
| p8 (V-A) | DDPM dominance partly explained by familiarity: adoption creates a self-reinforcing cycle (text reads "virtual cycle") | Sociological claim, no evidence |
| p9 (V-B) | Classifier guidance depends on a classifier robust to noisy inputs; CFG costs two models | Specific trade-off |
| p11 (Table I caption) | Regression methods "generally produce better PSNR and SSIM" than generative | Data-backed in Table I |
| p12 (V-E) | A quantitative analysis of corruption types is "an exciting and open research avenue" | Vague; no proposed protocol |
| p12-13 (V-F) | Properly defined architecture and diffusion design are "crucial" to avoid colour shift | Hypothesis, no evidence |
| p13 (V-G) | Optimal denoising networks "will vary based on the task" | Non-claim |
| p14 (VI-B) | DDNM needs a hand-set A, assumes linear degradation, costs more than task-trained DDPMs | Most specific critique in the paper |
| p14 | Few later studies build on CDPMSR | Observation about the field |
| p16 (VIII-B) | Cites a 300,000-fold compute rise and an industry-academia gap | One external figure [174] |
| p16 (VIII-C) | "A systematic method for determining inference schedules" is missing | Specific, checkable |
| p17 (VIII-E) | Comparability: datasets differ in resolution, content, noise; a standard benchmark is "essential" | Names the need; proposes nothing |
| p17 (VIII-G) | Cascaded approach underperforms BigGAN for cascaded generation | Specific |

**Comparability and evaluation.** Treated twice: II-C (p3-4, metrics with equations, perception versus fidelity) and VIII-E (p17). The authors observe that DMs score lower on PSNR/SSIM yet are preferred by humans, and point to LPIPS, TID2013, DeepQA, NIMA. They do not say which metric to use for which claim, and they do not define a protocol. The tables are themselves not comparable with each other: Table I (4x DIV2K validation, PSNR 26.70 to 32.82), Table III (resized DIV2K validation, 128 to 512, PSNR 20.88 to 23.41) and Table IV (ImageNet 1K, CelebA 1K) use different data and ranges. The page gives the dataset names in captions but no discussion of why Table III values sit about 5 dB below Table I. Table IV is "derived from Li et al." and Tables I to III are small excerpts; the captions of II and III cite no source. No new measurement anywhere.

**Open problems (Section VIII).** Seven. Specificity ranking, best first: VIII-C (no systematic way to set inference schedules), VIII-E (no standard benchmark), VIII-B (cost and academic access), VIII-A (why does colour shift arise, theory missing). Weakest: VIII-D (corruption spaces "demand further investigation"), VIII-F (manipulation "greatly needed"), VIII-G (cascading a research opportunity). None states a testable hypothesis, a metric or a falsifier. "Lack of explainability" from the abstract has no item at all.

**Does it keep the "critically analyzes" promise (p1)?** Partly. Judgement is present as one clause per method group. There is no cross-method synthesis such as "among N methods, X wins on metric Y under protocol Z" (only Tables I to IV).

## 5. Findings and take-home messages; conclusion

- **No labelled findings.** The survey has no "key findings" box or numbered take-aways. Candidate findings, taken from the text: DDPMs dominate over SGMs and SDEs in SR (V-A, p8); regression nets beat generative ones on PSNR/SSIM (Table I); DMs win on human preference (p1, p17); colour shift appears with small batch or short training (V-F); the wavelet domain is under-explored (V-C2, VIII-A); zero-shot methods trade quality for flexibility and cost (Table IV).
- **Conclusion (IX, p17).** A single paragraph: recaps topics in the order covered ("We introduced... We explored..."), restates that DMs do not suffer typical convergence problems, and ends on an optimistic line that the future of SR "looks more promising than ever" (paraphrased end sentence). No open problems repeated, no limitation of the survey, no ranked agenda, no pointer to a first experiment.
- **Contradiction inside the conclusion.** It says DMs "do not suffer typical convergence issues", yet VIII-B and V-F describe heavy compute and colour shift under limited hardware.

## 6. Writing style

- **Paragraphs.** Long (8 to 12 sentences in V and VII). Typical unit: method name, citation, one-sentence mechanism, one-sentence advantage. Little structure inside a paragraph; the method catalogue reads as a chain of "X [n] does A. Y [m] does B."
- **Sentences.** Mix of long technical sentences (30 to 45 words) with short summarising ones. Equations are embedded and explained symbol by symbol (eqs 12 to 28 in III).
- **Hedging.** Standard: "often", "typically", "can", "promising avenue". Only one explicit epistemic hedge of the "to the authors' knowledge" form (V-B, p9). Claims about causes (colour shift, DDPM dominance) are asserted with a citation or none.
- **Citation density.** About 185 references over about 16 pages; method lists carry 3 to 6 numbers per sentence (p10, p12, p13). Citations support existence ("Y did A") rather than a judged comparison.
- **Signposting.** Good at the local level: each section ends by pointing to the next ("which are discussed next", p5); "Hitchhiker's Guide" is used as an off-ramp in several places (p2, p4) instead of explaining. Roadmap present at p2. Fig. 3 plus Table IV give the only synthesising visuals.
- **Transitions.** Numbered subsections (1) to (4) carry transitions; between big sections there is often none (VI to VII are abrupt; p15).
- **Language slips visible on the page.** "virtual cycle" for virtuous cycle (p8); the roadmap error noted in section 2. Minor, but a reviewer notices them.

## 7. Weaknesses a hostile reviewer would raise (and how we beat each)

1. No search protocol, no inclusion or exclusion criteria, no count of papers considered. We cannot say how the 185 references were chosen. We beat it: PRISMA 2020 (already planned), with flow counts.
2. No synthesis table. Only four small tables of copied numbers, none a method-by-axis matrix. Beat it: a method-by-design-choice table covering all included systems, and a coverage map showing empty cells.
3. Taxonomy decorative. Axes are not used after Section V; one axis (guidance) is empty by the authors' own statement; zero-shot sub-taxonomy borrowed from Li et al. [17]. Beat it: use the design space to generate findings and tests.
4. Comparability named, not fixed. Tables mix protocols. Beat it: state a protocol and report only like-for-like.
5. Promise and delivery mismatch: "evolution" without a chronology; "explainability" without a section; roadmap omits VI.
6. Closest survey (Yang et al. [65]) in the bibliography but not discussed. Beat it: a positioning table against every prior survey.
7. Unsupported causal talk (colour shift, DDPM popularity) and a vague future-work list with no testable items.
8. Theory-heavy front (37%) duplicates standard texts; the survey's SR-specific contribution starts at p8.
9. No limitations section for the survey itself. No data or checklist for reproducibility; no code or sheet of extracted data.
10. Conclusion repeats and does not conclude: no ranked take-aways.

## 8. Transferable rules

### Twelve for a review in Information Fusion

1. State the gap as a missing capability, not as reader overload (the SR abstract, p1, uses overload). Then name the one question the review answers.
2. Number the contributions (the SR paper has none, p1-2) and tie each to a section and a table or figure.
3. Put a comparison table of prior surveys in the introduction (SR p1 does this only in prose); include the closest general survey (SR omits [65] in text).
4. Give the reader a roadmap that is checked against the headings (SR p2 omits Section VI).
5. Show the taxonomy as a figure in the introduction and use it at the end: a coverage matrix of methods against axes, with empty cells discussed (SR Fig. 3, p9, only appears at p9 and stops at Section V).
6. Keep axes orthogonal and say where a method sits on each; do not let a method appear under several headings without a table (SRDiff, ResDiff, ILVR, StableSR across V-A to VI).
7. Cut background to what the reader needs; push standard theory to a short primer (SR spends about 37% before the first SR method, pp. 2-7).
8. Make every judgement a sentence with a mechanism and a scope, as in the best SR examples (PSNR vs perception, p4; DDNM limits, p14), and avoid the vague ones ("promising avenue", pp. 10, 12).
9. Treat comparability as a finding: list protocol differences with numbers, and report only like-for-like results (SR Tables I, III and IV mix protocols, pp. 11, 12, 14; VIII-E asks for a benchmark and defines none, p17).
10. Make open problems testable: each with a hypothesis, a metric and a falsifier (SR VIII A to G, pp. 16-17, none has these).
11. End with ranked take-aways and the review's own limitations; do not close on optimism (SR IX, p17). The conclusion should not contradict the discussion (SR IX vs VIII-B).
12. Report the method: search, screening, appraisal, counts (SR has none, whole text) and release the extraction sheet. Information Fusion readers expect a protocol and the fusion angle (what is fused, at what level) stated up front.

### Six for a research article

1. Open with a single failure case from measurement, then the method; the SR survey shows its strongest pages when it ties a claim to a table (Table I, p11).
2. State every assumption next to the equation that needs it and every symbol once (the SR theory run, eqs 12-28, pp. 5-7, does this and reads cleanly).
3. Compare against baselines under one protocol and say what was held fixed; copied numbers from other papers (SR Tables I, III, IV, pp. 11-14) are a weakness we should not reproduce.
4. Report colour-shift-style side effects as measured quantities: in SR, V-F (p12) offers a fix (eq. 34) and a hypothesis but no measurement.
5. Put limitations and failure modes in the paper (SR has none for itself; it does list limits of other methods, p14, which is the right form).
6. Use captions that carry the source, dataset and protocol (SR Tables II and III captions cite no source, pp. 11-12; Table IV caption does, p14).

---

## Journal scope check

WebFetch on `https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=5962385` returned HTTP 418, body not retrieved. TNNLS scope not verified; nothing here depends on it.

## Contract notes

No ledger rows added: the brief names no ledger. Quotes kept under 15 words; the other statements are paraphrase.
