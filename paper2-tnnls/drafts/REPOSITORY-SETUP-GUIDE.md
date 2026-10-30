# Repository and archive setup for Paper 2 (IEEE TNNLS)

Purpose: give the paper a code-and-data link (withheld in the anonymous review PDF, printed in the camera-ready version) and an
archive DOI. Same pattern as your earlier papers (GitHub + Zenodo). About 30 minutes. Nothing here is done for you: you create the
accounts' objects; I prepare the files and fill the paper once you send the details at the end.

## 1. Decide two things first (with your supervisor)

1. **Visibility during review.** TNNLS is double-anonymous on its CIS pages. Options:
   - (a) Keep the repository private until acceptance; the paper says the link is withheld and the code is available to reviewers on
     request through the editor. Simplest; this is what the current text says.
   - (b) Make an anonymised copy for reviewers (for example through anonymous.4open.science, which mirrors a GitHub repo without the
     author name). Note: this is a copy, not the git history, so it cannot show commit times or hashes.
2. **What goes public at acceptance.** Recommended: code (exp_p2/, analysis/, analysis_posthoc/learned_ceiling/, tools/, tests/),
   preregistration documents (research/paper2/prereg/), the committed runs/ result files used by the paper, the paper sources
   (paper2-tnnls/), and a README. Not included: the UniDisc, CLIP and SigLIP weights (download links in the README), COCO images
   (public), the untracked item arrays (SHA-256 manifests are committed; they can be regenerated on a GPU).

## 2. GitHub repository (at acceptance, or now as private)

1. github.com -> New repository. Suggested name: `reliability-fusion-unidisc-tnnls` (any name works). Owner: shlokDS16. Private for now
   (option a) or public at acceptance.
2. Tell me the name; I will prepare a clean export branch with only the files of section 1.2, a README (what each folder holds, how to
   rerun every table and figure from the committed runs files, hardware used, the pinned model revisions) and a LICENSE (MIT for code,
   CC BY 4.0 for text and results, unless your supervisor prefers otherwise). You push it (I do not push without your yes).

## 3. Zenodo DOI (at acceptance)

1. zenodo.org -> log in with GitHub -> Settings -> GitHub -> switch the repository ON.
2. On GitHub, create a release (for example `v1.0.0`, title "Paper 2, IEEE TNNLS camera-ready"). Zenodo archives it and mints a DOI
   within minutes.
3. On the Zenodo record, check title, authors (both, with ORCIDs), licence and description (I will draft the description; it follows
   the paper's placement rules: no family H, no link between the two studies).

## 4. Send me these details

- Repository URL (and whether it is private or public now).
- Zenodo DOI (when it exists; until then I keep the camera-ready placeholder).
- Licence choice (code; text and results).
- Authors as they should appear (full names, affiliations, ORCIDs, corresponding author and e-mail) - the camera-ready title block and
  the IEEE Author Portal also need these.

## 5. Where these go in the paper

- `paper2-tnnls/sections/declaration.tex`, "Reproducibility and Data Availability": the `\anonlink{...}` target (printed only in the
  camera-ready build, `\anonfalse` in main.tex) and the archive DOI.
- `paper2-tnnls/main.tex`, the non-anonymous author block (names, affiliations, e-mails, corresponding author, funding line).
