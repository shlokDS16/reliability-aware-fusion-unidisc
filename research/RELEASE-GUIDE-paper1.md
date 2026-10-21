# GitHub and Zenodo for Paper 1 (DLM review): exact steps (updated 2026-10-21, manual Zenodo route)

## GitHub: done by Claude, repository stays private

- Repository: https://github.com/shlokDS16/dlm-review-prisma (private, created by you on 2026-10-21).
- First push done on 2026-10-21 (2,476 files, pre-review draft). Claude pushes the final version after fixes A-D with
  `python -I tools/sync_release_repo.py "<message>"`, which mirrors the build folder into the local clone
  `C:\Users\Shlok\Downloads\Multi-Modality Language model\release\dlm-review-prisma-git` and pushes.
- Because the repository is private, Zenodo cannot archive it automatically (its GitHub link works only for public
  repositories). So the DOI comes from a **manual Zenodo upload**, below. Nothing else on GitHub is needed from you.
- The paper's data availability statement currently says the archive is "mirrored at [GitHub link]". With a private
  repository readers cannot open that link, so before submission either make the repository public, or tell Claude
  to cite only the Zenodo DOI (recommended while it stays private).

## Zenodo: manual upload (about 15 minutes)

**File to upload** (rebuilt by Claude after fixes A-D; upload only after Claude says the final version is ready):
`C:\Users\Shlok\Downloads\Multi-Modality Language model\release\dlm-review-prisma-v1.0.0.zip`
(about 22 MB; one zip holds all 2,476 files, because Zenodo allows at most 100 files per record).

### Step 1. Start a new upload
1. Go to https://zenodo.org and log in (GitHub or ORCID login both work).
2. Click **+ New upload** (top bar, or "Upload" in your profile menu).

### Step 2. Files
- Drag in `dlm-review-prisma-v1.0.0.zip` and wait until it shows 100 %.

### Step 3. Reserve the DOI first
- Under **Digital Object Identifier**: "Do you already have a DOI for this upload?" choose **No**, then click
  **Get a DOI now!**. Zenodo shows a reserved DOI such as `10.5281/zenodo.NNNNNNNN`.
- **Send this DOI to Claude now.** It goes into the paper before you publish, so the paper and the record match.
  The record stays a private draft until Step 6.

### Step 4. Basic information (fill exactly)

| Field | Enter |
|---|---|
| Resource type | **Dataset** |
| Title | `Data and code for: Diffusion Language Models and Unified Multimodal Generation: A Critical Systematic Review of Discrete and Continuous Approaches` |
| Publication date | today's date (the default) |
| Creators | Add three persons, in this order. 1) Family name `Goenka`, given name `Shlok`. 2) `Vairavasundaram`, `Subramaniyaswamy`. 3) `G N`, `Balaji`. For each: **ORCID** (type it in the identifier box), **Affiliation** `Vellore Institute of Technology` (pick it from the list; it is in ROR), **Role** leave empty or "Researcher". |
| Description | `Protocol, search log with every query and export checksum, screening records of two model screeners and the adjudicator, extraction records and validator reports, decision ledger, analysis scripts, figure and table scripts, and LaTeX sources of a PRISMA 2020 systematic review of diffusion language models and unified multimodal diffusion models (submitted to ACM Computing Surveys). Full texts of the reviewed papers and raw database exports are not included; abstracts were removed from the bibliographic records. Code is under the MIT licence (LICENSE), data and text under CC BY 4.0 (LICENSE-DATA).` |
| Licenses | **Creative Commons Attribution 4.0 International** (add **MIT** as a second licence for the code) |

### Step 5. Recommended information

| Field | Enter |
|---|---|
| Keywords and subjects | `diffusion language models`, `masked diffusion`, `discrete diffusion`, `unified multimodal models`, `decoding strategies`, `systematic review`, `PRISMA 2020` (press Enter after each) |
| Languages | English |
| Version | `1.0.0` |
| Publisher | Zenodo (default) |
| Related works | leave empty now; after the paper is accepted add "Is supplement to" + the paper's DOI (Zenodo lets you edit metadata after publishing) |
| Funding | add the grant only if the paper's funding statement names one |

Leave **Visibility** as **Public** and access **Open** (the zip holds no full texts or private notes).

### Step 6. Publish
- Click **Save draft**, check the preview, then **Publish**. After publishing, the files cannot be changed; a later
  correction is a **New version** on the same record (it gets its own DOI, and the concept DOI stays the same).

### Step 7. After publishing
- Tell Claude "published". Claude checks that the DOI resolves (https://doi.org/10.5281/zenodo.NNNNNNNN) and that the
  paper, the Word file and the repository README carry it.

## If something goes wrong
- Upload stalls: reload the page; the draft keeps the reserved DOI.
- ORCID not found: check the 16-digit ORCID at https://orcid.org; every author needs one before ACM production.
- Published the wrong file: use **New version**, upload the right zip, publish; send Claude the new version DOI.
