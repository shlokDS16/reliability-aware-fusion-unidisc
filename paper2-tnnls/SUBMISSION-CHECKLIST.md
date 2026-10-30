# Paper 2 - IEEE TNNLS submission checklist (2026-10-30)

Files to upload (review stage; the review upload is the PDF):
- `paper2-tnnls/main.pdf` - manuscript, two columns, 15 pages, anonymous build, fonts embedded.
- `paper2-tnnls/supplement/supplement.pdf` - supplementary material (label it "supplementary" in the portal).
- Optional/if the portal or editor asks for Word: `paper2-tnnls/docx/Paper2_TNNLS_manuscript.docx` (two-column, IEEE Transactions
  Word template) and `paper2-tnnls/docx/Paper2_TNNLS_supplement.docx` (one column). Rebuild with `bash build.sh` then
  `python scripts/make_docx.py` in `paper2-tnnls/` after any change.

## Only the authors can do these (blocking)

1. **Declaration of Generative AI Use** (decision D0101). The PDF prints your interim text: "The authors used Claude (Anthropic) to
   improve the language and grammar of the manuscript. The authors reviewed and edited all content and take full responsibility for it."
   Frame the final text with your supervisor. IEEE's policy (checklist section 7) asks that AI-generated text, figures and code be
   disclosed with the sections and level of use; the earlier full draft is in `drafts/declaration-full-disclosure-draft.tex`. Once
   settled, tell me the text: I will align the body sentences that describe the audits (currently "automated audits run in the authors'
   own pipeline (not independent reviews)", D0103).
2. **Author details** for the portal and the camera-ready block: full names, affiliations, e-mails, postal address, ORCID for each
   author (ORCID is mandatory for every author), corresponding author, funding statement (or "no external funding").
3. **Confirm** the work is not under review elsewhere (Information Fusion, TMLR or any other venue) and choose the article type
   **Full Paper** (it cannot be changed after submission).
4. **Repository**: follow `drafts/REPOSITORY-SETUP-GUIDE.md` and send me the URL (and the Zenodo DOI at acceptance).

## Good to know

- Length: 15 pages = the hard cap for a Full Paper; over-length charge is USD 200 per page above 10 (USD 1,000 at 15 pages) if accepted.
- Index terms (4): Diffusion models; Hypothesis testing; Information fusion; Multimodal learning - not yet checked against the IEEE
  Thesaurus (free access by request form).
- Anonymous review: the PDF has no author names, no funding line, no "submitted to the IEEE" notice; the repository link is withheld.
- Do not post a preprint (arXiv/TechRxiv) before the review decision unless you choose to (it would break double-anonymous review).
- Quality record: red team SIGN WITH CONDITIONS (conditions above; its non-author conditions are met: DOCX regenerated and
  must-not scanned, family H contribution sentence fixed); number audits PASS WITH FIXES (fixes applied; about 660 + 1,800
  values traced to run files; incremental audit 2 findings F1 and N6 closed on 2026-10-30); Codex review round 2 found no arithmetic or statistical error. The hostile area-chair score is 4/10
  ("reject and resubmit"): the weaknesses are scope (one model, one dataset, one noise severity; the method was trained on the tested
  noise level), incremental novelty next to Petryk et al. (WACV 2024), and practical significance next to near-ceiling CLIP/SigLIP.
  These are stated in the paper's Limitations; they can only be removed by new confirmatory work (a second backbone or a corruption
  held out of training), which the preregistration's stop rule reserves for a future paper.
