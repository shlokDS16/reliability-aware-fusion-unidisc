# GitHub and Zenodo for Paper 1 (DLM review): what happens and what you do

CSUR asks for the data and code behind a review to be available, and the paper's "Data and code
availability" line needs a permanent link (a Zenodo DOI). This repository is 9.1 GB and holds
copyrighted PDFs and full texts, so we do **not** publish it as it is. We publish a curated copy.

## What goes in the public release (I build it; nothing is uploaded until you say so)

| In | Out (never published) |
|---|---|
| `tools/`, `analysis/` (every script that makes a number), `tests/` | `research/sources/pdfs/`, `research/sources/md/`, `research/sources/html/` (publisher full texts: copyright) |
| `paper/review/` (LaTeX, figure scripts, figures, tables) | the census HTML texts, any PDF |
| protocol, criteria v1.6, extraction form v0.5, codebooks | `.venv/`, model checkpoints, generated images (UniDisc has no licence) |
| ledgers (decisions, references), screening rows (A, B, C), PRISMA counts, RQ1 counts, extraction records and validator reports | private notes: `research/EVENING-*`, `USER-ACTIONS-*`, chat-derived pages |
| search log with every query and the SHA-256 of each export | raw database exports (`research/sources/search-raw/`): licence terms of Scopus, WoS etc. |

Licences (my default; tell me if you want others): code MIT, data and text CC BY 4.0.

## Your steps (about 15 minutes, after I say the release folder is ready)

1. **GitHub repository.** Either tell me "create the GitHub repo" (I run `gh repo create
   shlokDS16/dlm-review-prisma --private` and push the release folder; you make it public when the
   paper is submitted), or create it yourself at https://github.com/new with that name, private, no
   README, and tell me the name.
2. **Connect Zenodo to GitHub (once).** Go to https://zenodo.org, log in with GitHub, open your
   profile menu > **GitHub**, click **Sync now**, and switch the toggle **on** for
   `shlokDS16/dlm-review-prisma`. Zenodo only archives public repositories, so make the repository
   public at this step (or when you submit).
3. **Make a release.** On the repository page: **Releases > Draft a new release**, tag `v1.0.0`,
   title "Paper 1 submission version", **Publish release**. Zenodo archives it within a few minutes
   and shows a DOI under **GitHub** in your Zenodo profile (10.5281/zenodo.NNNNNNN).
4. **Send me the DOI.** I put it in the paper (Data and code availability, Section 2.8) and in the
   repository README badge, and file it in the references ledger.
5. **Zenodo record details** (on the Zenodo record page, **Edit**): add the three authors in the
   paper's order with the affiliation, your ORCIDs, licence CC BY 4.0, and a link to the paper once
   it has one. Save and publish.

Earlier papers used the same route (conformal-water-quality-gloria, Zenodo 10.5281/zenodo.22791749).

## What I still need from you for this

- Go-ahead to build the release folder (it is local only).
- Whether I create the GitHub repository (step 1) or you do.
- ORCIDs for the three authors and who is the corresponding author (the paper needs both).
