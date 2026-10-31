# Paper 2: submit to IEEE TNNLS (step by step)

Requirements checked on 2026-10-30 against the journal's official pages: TNNLS Information for Authors
(cis.ieee.org/publications/t-neural-networks-and-learning-systems/tnnls), Guidelines for Paper Submission, and the IEEE preprint
policy page. The portal's own upload screens sit behind your login and could not be read; if a screen asks for something not
listed here, tell me what it says.

## 0. Before you click Submit (four checks)

1. **AI sentence in the Acknowledgment.** It now reads: "The authors used Claude (Anthropic) to improve the language and grammar of
   the manuscript. The authors reviewed and edited all content and take full responsibility for it." If your professor changes it,
   send me the new text: I rebuild the PDF and Word files (both versions) in one go. **The red team flags this sentence as too
   narrow (finding F9):** besides language editing, Claude helped produce figures, Algorithm 1, the comparison table, analysis
   scripts and much of the text under your direction, and IEEE asks that AI use be disclosed with the sections and level of use.
   Settle a wording that covers this with your professor; a fuller draft is in `drafts/declaration-full-disclosure-draft.tex`.
2. **Anonymized code link** (repository guide, step 4: anonymous.4open.science on branch `review-snapshot`). Send me the link and I
   put it into the review copy. If the site cannot read the private repository, upload `optional/04_Anonymized_code_and_data.zip`
   as supplementary material instead (it is the same anonymized snapshot) and tell me, so the sentence says so.
3. **Zenodo DOI reserved: done** (10.5281/zenodo.23810711, draft; do not Publish before acceptance). Printed only in the author version.
4. **Confirm** that the paper is not under review anywhere else (the portal asks; TNNLS disqualifies duplicate submissions).

## 1. Files to upload (this folder)

| Upload as (portal file type) | File | Notes |
|---|---|---|
| Main document / Manuscript (PDF) | `01_Manuscript_anonymous.pdf` | 13 pages, two-column IEEE format, all pages numbered, all fonts embedded, no author names, no funding, no institution thanks, PDF metadata "Anonymous". |
| Supplementary material (for review) | `02_Supplementary_Material_anonymous.pdf` | 11 pages, anonymous. |
| Cover letter | `03_Cover_Letter.pdf` | One page, to the Editor-in-Chief; names the authors (editors only, not reviewers). |
| Only if the anonymized link fails: supplementary material | `optional/04_Anonymized_code_and_data.zip` | Same files as the `review-snapshot` branch; names replaced by ANONYMIZED. |

Do **not** upload anything in `at-acceptance/` now (it names the authors).
Word files are not needed at review (TNNLS reviews the PDF); review-copy Word files are in `optional/` in case an editor asks.

## 2. Portal fields (IEEE Author Portal: https://ieee.atyponrex.com/journal/tnnls)

- **Article type:** Full Paper (it cannot be changed after submission).
- **Title:** Reliability-Aware Fusion of Token Evidence for Image-Text Verification in Unified Discrete Diffusion
  (single-study version of 2026-10-31; package PDFs and Word files rebuilt from it on 2026-10-31)
- **Abstract** (paste; 249 words, limit 250; same as the PDF, no numbers):

  Image-text verification, choosing the true caption of an image from two candidates, becomes harder when the image is damaged. We
  study it in one frozen unified discrete diffusion model, UniDisc. Each image token's log-probability ratio between the true and
  a wrong caption is evidence, and the standard rule sums it with equal weights. We learn a per-token reliability weighting of
  this evidence from caption-free features, fit it on design images that include the noise level later tested, and freeze it.
  Preregistered one-sided exact paired tests confirmed that the frozen weighting raised verification accuracy under Gaussian
  noise, on fresh Common Objects in Context validation images and, with the weighting unchanged, on a second dataset, also with
  length-matched wrong captions. On clean images it was non-inferior on both datasets within a preregistered margin, fixed after
  an exploratory clean-image interval had been seen. In exploratory comparisons, a pixel denoiser before scoring did better under
  Gaussian noise but, combined with the weighting, worse under Joint Photographic Experts Group compression, and a linear logit on
  the same features did about as well under noise and better under compression. A sweep on the same validation images found the
  gain at milder and stronger noise, but at the tested level it did not clearly exceed the clean-image gain. The confirmatory
  evidence covers one model, two datasets, and one tested noise level; it does not show that the weights track token reliability
  (the name describes the design) or that the gain transfers to other models or corruptions.

- **Keywords / Index Terms** (5; TNNLS asks for 4-5): Denoising diffusion; Discrete diffusion; Information fusion; Masked diffusion; Multimodal learning.
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

- Mandatory over-length charge: 3 pages above 10 at USD 200 = **USD 600** (13-page paper). The USD 110/page charge is optional.
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

Update 2026-10-31 (presentation pass modelled on Mask-DiFuser, TPAMI 2026): the paper now has a real-image qualitative figure,
Algorithm 1 and an exploratory comparison table (Table IV) against alternative aggregation rules and a pixel denoiser, all on the
450 fresh-fold images. Two results there will draw reviewer attention, and the paper states both plainly: a classical
non-local-means denoiser applied before scoring reached 0.844 under Gaussian noise (0.856 combined with LRF) against LRF's 0.802,
and a linear logit refitted on the same features was at or above LRF in three of four conditions. The preregistered result (LRF
above the unweighted rule) is unchanged; the paper does not claim LRF is the best defence against this noise. Red team: SIGN WITH
CONDITIONS (conditions: the AI wording above, and the rebuilt files, now done); number audit 4: PASS WITH FIXES (fixes applied).
