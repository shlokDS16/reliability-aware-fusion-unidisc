# GitHub and Zenodo for Paper 1 (DLM review): exact steps (updated 2026-10-21)

You create the repository yourself (your decision of 2026-10-21). Everything to upload is already built.

## What you upload

Folder (local, ready): `C:\Users\Shlok\Downloads\Multi-Modality Language model\release\dlm-review-prisma-v1`
- About 2,475 files, 185 MB; the largest file is 36 MB (GitHub limit 100 MB per file, so no Git LFS is needed).
- Root files already in it: `README.md`, `LICENSE` (MIT, code), `LICENSE-DATA` (CC BY 4.0, data and text),
  `.zenodo.json` (pre-fills the Zenodo record), `CITATION.cff` (citation box on GitHub), `MANIFEST.sha256`,
  `SECRET-SCAN.txt` (no secrets found).
- Not in it (on purpose): full texts and PDFs of reviewed papers, raw database exports, generated images,
  your private notes, abstracts of the bibliographic records.

## Step 1. Create the GitHub repository (about 3 minutes)

At https://github.com/new, signed in as **shlokDS16**:

| Field | Enter |
|---|---|
| Repository name | `dlm-review-prisma` |
| Description | `Data and code for "Diffusion Language Models and Unified Multimodal Generation: A Critical Systematic Review of Discrete and Continuous Approaches" (PRISMA 2020; ACM Computing Surveys submission)` |
| Visibility | **Public** (Zenodo archives only public repositories). If you prefer to wait, choose Private now and switch to Public in Step 3. |
| Add a README / .gitignore / licence | **Leave all unticked** (the folder already has them) |

Click **Create repository**. Then, in **Settings > General > Topics** (gear icon next to "About" on the repo page),
add: `systematic-review`, `prisma`, `diffusion-language-models`, `multimodal`, `reproducibility`.

## Step 2. Upload the folder (about 5 minutes)

The browser upload takes at most 100 files at a time, so use the terminal. Paste these one at a time:

```bash
cd "C:/Users/Shlok/Downloads/Multi-Modality Language model/release/dlm-review-prisma-v1"
```
```bash
git init -b main
```
```bash
git add -A
```
```bash
git commit -m "Paper 1 data and code, version 1.0.0"
```
```bash
git remote add origin https://github.com/shlokDS16/dlm-review-prisma.git
```
```bash
git push -u origin main
```

(Alternatively: GitHub Desktop > File > Add local repository > choose that folder > Publish repository.)
Check on the repository page that `README.md` shows and that the file count looks right.

## Step 3. Connect Zenodo (about 3 minutes, once)

1. Go to https://zenodo.org and **Log in with GitHub** (same account, shlokDS16).
2. Top-right menu (your name) > **GitHub**.
3. Click **Sync now**; find `shlokDS16/dlm-review-prisma` and switch its toggle **On**.
   (If the repository is still private, make it public first: repo **Settings > General > Danger Zone > Change
   visibility > Public**, then Sync again.)

## Step 4. Make the release that Zenodo archives (about 2 minutes)

On the GitHub repository page: **Releases** (right side) > **Create a new release**:

| Field | Enter |
|---|---|
| Choose a tag | type `v1.0.0` > **Create new tag** |
| Release title | `Version 1.0.0: submission version` |
| Description | `Data, code and LaTeX sources of the review as submitted to ACM Computing Surveys.` |

Click **Publish release**. Within a few minutes Zenodo creates the record; it appears under Zenodo > menu > **GitHub**
with a DOI badge (`10.5281/zenodo.NNNNNNNN`).

## Step 5. Check the Zenodo record (about 5 minutes)

Open the record on Zenodo > **Edit**. `.zenodo.json` already fills title, description, authors, affiliations,
keywords, licence (CC BY 4.0), version 1.0.0 and language. Check and add:

| Field | Value |
|---|---|
| Resource type | Dataset |
| Creators (order) | Goenka, Shlok; Vairavasundaram, Subramaniyaswamy; G N, Balaji (all: School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, India) |
| ORCID | add each author's ORCID in the creator entry (not in the file because I don't have them) |
| Related works | leave empty now; after acceptance add "Is supplement to" + the paper's DOI |

Click **Save**, then **Publish**.

## Step 6. Send me two things

1. The GitHub link: `https://github.com/shlokDS16/dlm-review-prisma` (or whatever name you used).
2. The Zenodo DOI (`10.5281/zenodo.NNNNNNNN`).

I then replace the two highlighted placeholders in the PDF and in the Word file (Data and code availability
statement, just before the Acknowledgments), rebuild both, and send them back.

## If something goes wrong

- `git push` asks for a password: GitHub needs a personal access token or GitHub Desktop; easiest is GitHub Desktop.
- Zenodo does not show the repository: make sure it is public, then **Sync now** again.
- No DOI after 10 minutes: Zenodo > GitHub page shows the release status; a failed one can be retried there.
