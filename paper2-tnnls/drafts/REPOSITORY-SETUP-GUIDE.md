# GitHub (private) and Zenodo (manual upload) for Paper 2, IEEE TNNLS

Updated 2026-10-30 (Shlok: manual Zenodo upload; repository private until acceptance; Zenodo DOI in Data Availability).
About 20 minutes of your time. You create the two objects (GitHub repository, Zenodo draft); I push the files, build the upload
zip and put the DOI into the paper.

## Why the DOI is printed only in the author version

TNNLS reviews double-anonymously (CIS Information for Authors: "the reviewers do not know the identities of the authors").
A Zenodo record lists the authors' names, so a DOI in the review copy would reveal them. The paper therefore has two builds
from one source:

| Build | Files | Data Availability says |
|---|---|---|
| Review copy (upload to the portal) | `main.pdf`, `docx/Paper2_TNNLS_manuscript.docx` | "A release of the repository is archived on Zenodo (DOI withheld for double-anonymous review)." |
| Author version (accepted / camera-ready, or a title page if the portal asks) | `main_camera.pdf`, `docx/Paper2_TNNLS_manuscript_authors.docx` | the same sentence with the DOI link |

Do not submit the review copy until the Zenodo draft with its reserved DOI exists (step 2), because the sentence says the
archive exists.

## Step 1. Create the private GitHub repository (2 minutes)

1. github.com, signed in as **shlokDS16**: **New repository**.
2. Repository name: **`reliability-aware-fusion-unidisc`**
   Description: `Code, preregistrations and results for "Learned Reliability-Aware Fusion of Token Evidence ... in UniDisc" (Paper 2)`
3. Visibility: **Private**.
4. Leave "Add a README", ".gitignore" and "license" all **unticked** (the repository must be empty, or the push is refused).
5. **Create repository**, then send me the URL (`https://github.com/shlokDS16/reliability-aware-fusion-unidisc`).

What I push when you send the URL:
- The project's full git history. It must be the full history: the paper and supplement S-I print commit identifiers
  (pins, freezes, analysis runs), and those identifiers exist only in this history. A cleaned copy would give new identifiers
  and break every pin the paper cites.
- A `README.md` for Paper 2 at the top level (folders, how to rerun each figure and table from `runs/`, hardware, pinned
  model revisions, licences).
- Note for later (before the repository goes public at acceptance): the history also holds Paper 1 and Paper 3 work and a few
  third-party PDFs (for example `Sample papers/`, IEEE template guides). They are fine in a private repository; before making it
  public I will list them and we decide together (remove from history and reprint the changed identifiers, or publish a Paper 2
  export and keep this repository private).

## Step 2. Zenodo: manual upload with a reserved DOI (10 minutes)

I will place the upload file at `paper2-tnnls/release/reliability-aware-fusion-unidisc-v1.0.0.zip` after the push (Paper 2 files
only: code, preregistration documents, the result files under `runs/` that the paper cites, the paper and supplement sources and
PDFs, README, licences; no model weights, no COCO images, no third-party PDFs).

1. zenodo.org, log in (GitHub or ORCID login is fine). Top right **+** (or **New upload**).
2. **Files**: skip for now if the zip is not ready yet (a draft can be saved without files). When I tell you it is ready,
   open the draft again (**My dashboard > Uploads**), drag in `reliability-aware-fusion-unidisc-v1.0.0.zip` and **Save draft**.
3. **Digital Object Identifier**: "Do you already have a DOI for this upload?" choose **No**, then click **Get a DOI now!**
   Zenodo shows the reserved DOI (`10.5281/zenodo.NNNNNNN`). **Copy it and send it to me.**
4. **Resource type**: Software.
5. **Title**: `Code and data for: Learned Reliability-Aware Fusion of Token Evidence Raised Image-Text Verification Accuracy Under Gaussian Noise in a Unified Masked Diffusion Model: A Preregistered Confirmation in UniDisc`
6. **Publication date**: today's date.
7. **Creators** (same order and details as the review paper; type each, add ORCID if you have it):
   1. Goenka, Shlok. Affiliation: Vellore Institute of Technology, School of Computer Science and Engineering, Vellore, India.
   2. Vairavasundaram, Subramaniyaswamy. Same affiliation.
   3. G N, Balaji. Same affiliation.
8. **Description** (paste):
   > Code, preregistration documents, hash pins, recorded predictions and analysis outputs for a paper that reports two
   > separately preregistered studies of image-text verification under image damage in the pretrained unified masked
   > diffusion model UniDisc on COCO val2017 image-caption pairs: a likelihood-based gate on image tokens (Study 1) and a frozen
   > learned reliability-aware weighting of per-token evidence tested on a fresh fold (Study 2). The README explains how every
   > table and figure of the paper and its supplement is recomputed from the committed result files. Model weights (UniDisc,
   > CLIP, SigLIP) and COCO images are not included; the README gives their pinned sources.
9. **Licences**: add **Creative Commons Attribution 4.0 International** (text, documents, results) and **MIT License** (code).
   (If your supervisor prefers others, tell me; the README states the same.)
10. **Keywords**: masked diffusion; unified multimodal models; image-text verification; information fusion; preregistration;
    hypothesis testing; UniDisc.
11. **Version**: `v1.0.0`. **Language**: English.
12. **Related works**: add `https://github.com/shlokDS16/reliability-aware-fusion-unidisc`, relation "Is supplement to"
    (it stays private for now; that is fine).
13. **Visibility / access**: leave the files **Restricted** if Zenodo asks.
14. Click **Save draft**. **Do not click Publish.** A saved draft keeps the reserved DOI; the DOI becomes live when you publish
    at acceptance (then also switch GitHub to public). Publishing now would put the authors' names online during
    double-anonymous review.

## Step 3. Send me

- The GitHub URL (step 1) and the reserved DOI (step 2.3).
- Corresponding author for Paper 2 (the review paper never named one; name and e-mail).
- Optional: ORCIDs (they go into the IEEE Author Portal, not the PDF) and a licence preference.

## What I do with them

- Push the history and README to the private repository (only after your URL).
- Put the URL into the `\anonlink` target and the DOI into Data Availability in `paper2-tnnls/sections/declaration.tex`
  (printed only in the author version), and the corresponding author into the first footnote in `main.tex`.
- Rebuild both versions (PDF and Word), check that each stays within 15 pages and that the review copy shows no names,
  repository URL or DOI, and commit.

## At acceptance (later)

Publish the Zenodo draft (the DOI goes live), make the GitHub repository public after the third-party-file decision above,
add biographies and photos (switch `\biostrue` in `main.tex`), and add the paper's own DOI to the Zenodo record under
Related works ("Is supplement to").
