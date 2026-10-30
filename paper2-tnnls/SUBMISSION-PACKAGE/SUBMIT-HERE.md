# Paper 2: submit to IEEE TNNLS (step by step)

Requirements checked on 2026-10-30 against the journal's official pages: TNNLS Information for Authors
(cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls), Guidelines for Paper Submission, and the IEEE preprint
policy page. The portal's own upload screens sit behind your login and could not be read; if a screen asks for something not
listed here, tell me what it says.

## 0. Before you click Submit (four checks)

1. **AI sentence in the Acknowledgment.** It now reads: "The authors used Claude (Anthropic) to improve the language and grammar of
   the manuscript. The authors reviewed and edited all content and take full responsibility for it." If your professor changes it,
   send me the new text: I rebuild the PDF and Word files (both versions) in one go. IEEE asks that sections with AI-generated text
   cite the AI system; language editing alone does not need that.
2. **Anonymized code link** (repository guide, step 4: anonymous.4open.science on branch `review-snapshot`). Send me the link and I
   put it into the review copy. If the site cannot read the private repository, upload `optional/04_Anonymized_code_and_data.zip`
   as supplementary material instead (it is the same anonymized snapshot) and tell me, so the sentence says so.
3. **Zenodo DOI reserved: done** (10.5281/zenodo.23810711, draft; do not Publish before acceptance). Printed only in the author version.
4. **Confirm** that the paper is not under review anywhere else (the portal asks; TNNLS disqualifies duplicate submissions).

## 1. Files to upload (this folder)

| Upload as (portal file type) | File | Notes |
|---|---|---|
| Main document / Manuscript (PDF) | `01_Manuscript_anonymous.pdf` | 15 pages, two-column IEEE format, all pages numbered, all fonts embedded, no author names, no funding, no institution thanks, PDF metadata "Anonymous". |
| Supplementary material (for review) | `02_Supplementary_Material_anonymous.pdf` | 18 pages, anonymous. |
| Cover letter | `03_Cover_Letter.pdf` | One page, to the Editor-in-Chief; names the authors (editors only, not reviewers). |
| Only if the anonymized link fails: supplementary material | `optional/04_Anonymized_code_and_data.zip` | Same files as the `review-snapshot` branch; names replaced by ANONYMIZED. |

Do **not** upload anything in `at-acceptance/` now (it names the authors).
Word files are not needed at review (TNNLS reviews the PDF); review-copy Word files are in `optional/` in case an editor asks.

## 2. Portal fields (IEEE Author Portal: https://ieee.atyponrex.com/journal/tnnls)

- **Article type:** Full Paper (it cannot be changed after submission).
- **Title:** Learned Reliability-Aware Fusion of Token Evidence Raised Image-Text Verification Accuracy Under Gaussian Noise in a
  Unified Masked Diffusion Model: A Preregistered Confirmation in UniDisc
- **Abstract** (paste; 248 words, limit 250; same as the PDF):

  We report two separately preregistered studies of image-text verification under image damage in one pretrained unified masked
  diffusion model (UniDisc, 1.4 billion parameters) on Common Objects in Context image-caption pairs. In the first, a gate discards
  low-likelihood image tokens. In the preregistered test no improvement was detected under Joint Photographic Experts Group
  compression at quality 10, Gaussian noise with standard deviation 0.1, and a 128-pixel splice; for each tested corruption the 90
  percent confidence interval of the net accuracy change lay inside plus or minus 0.05 (-0.002, -0.006 to 0.000; 0.000, 0.000 to
  0.000; -0.004, -0.010 to 0.002; 500 pairs each), so an improvement or a loss larger than 0.05 is excluded. This does not show that
  the gate has no effect. Each negative is a random caption of an image sharing no annotated object category with the test image. In
  the second, on a fresh preregistered fold, a frozen learned reliability-aware fusion of token evidence raised image-direction
  verification accuracy under Gaussian noise with standard deviation 0.1 from 0.733 without reliability weighting to 0.802 (net
  0.069, 95 percent confidence interval 0.029 to 0.109; exact one-sided McNemar test, probability value 0.0005), including with
  length-matched negatives. On clean images it lost no more than three percentage points (90 percent confidence interval of the net
  change 0.009 to 0.053); the margin was fixed after an exploratory clean interval had been seen. This result holds on 450
  validation-split images not used to design or fit the frozen weighting, at that one severity.

- **Keywords / Index Terms** (4; TNNLS asks for 4-5): Diffusion models; Hypothesis testing; Information fusion; Multimodal learning.
- **Authors** (this order; TNNLS returns papers without review if any author's contact details are missing or wrong; ORCID is
  mandatory for every author):

| # | Name | Affiliation | E-mail | ORCID |
|---|---|---|---|---|
| 1 | Shlok Goenka | School of Computer Science and Engineering, Vellore Institute of Technology, Vellore 632014, Tamil Nadu, India | shlok.goenka2023@vitstudent.ac.in | https://orcid.org/0009-0002-8581-5657 |
| 2 | Subramaniyaswamy Vairavasundaram (**corresponding author**) | same | subramaniyaswamy.v@vit.ac.in | https://orcid.org/0000-0001-5328-7672 |
| 3 | Balaji G N | same | balaji.gn@vit.ac.in | https://orcid.org/0000-0002-5346-0989 |

  Each co-author may receive a portal e-mail to confirm authorship and link the ORCID; ask them to accept it.
- **Funding:** This work was supported by Vellore Institute of Technology (VIT), Vellore, India.
- **Competing interests:** The authors declare that they have no known competing financial interests or personal relationships that
  could have appeared to influence the work reported in this paper.
- **Previously published / under review elsewhere:** No.
- **Human or animal subjects / ethics:** Not applicable (public COCO val2017 images and captions and a released pretrained model; no
  human participants, no personal data).
- **Data and code availability** (if asked): Code, preregistrations, pins, predictions and analysis outputs are in a version-controlled
  repository, available to reviewers in anonymized form and released with a Zenodo archive at acceptance.
- **Use of AI** (if asked): language and grammar editing with Claude (Anthropic); disclosed in the Acknowledgment.
- **Open access:** optional (USD 2,800 in 2026). Traditional (no fee at submission) is fine.
- **Suggested or excluded reviewers:** optional; leave empty unless your professor wants to name people.
- **Preprint:** IEEE allows arXiv/TechRxiv, but a preprint with your names would undo the anonymity of review; do not post one now.

## 3. After acceptance (not now)

- Mandatory over-length charge: 5 pages above 10 at USD 200 = **USD 1,000** (15-page paper). The USD 110/page charge is optional.
- Final files: one zip with all LaTeX sources of the accepted version, built from `main_camera.tex` (author version in
  `at-acceptance/`), plus biographies and head-and-shoulder photos of all three authors (I switch them on with `\biostrue`).
- Signed IEEE copyright form (sent by IEEE after acceptance).
- Publish the Zenodo draft (the DOI goes live), make the GitHub repository public (after we decide on the third-party files in its
  history), add the paper's DOI to the Zenodo record.

## 4. What reviewers will likely raise (internal hostile review)

The internal area-chair style review scored the paper 4/10 (reject and resubmit) on scope: one model, one dataset, one confirmed
noise severity, the weighting was trained on the tested noise level, closeness to Petryk et al. (WACV 2024), and CLIP/SigLIP near
ceiling on the same items. These are stated in the paper's Limitations; removing them needs new confirmatory work (a second model or
a held-out corruption), which is reserved for a later paper. Numbers, statistics and the preregistration record passed all audits.
