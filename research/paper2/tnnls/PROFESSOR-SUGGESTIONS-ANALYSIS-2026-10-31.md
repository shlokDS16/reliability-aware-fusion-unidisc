# Professor's suggestions of 2026-10-31 (title, abstract, base paper, one study): analysis

Lead analysis, written before any change. Sources: `paper2-tnnls/main.tex` (title), `sections/abstract.tex`, SAP Addendum A6.12
(`research/paper2/prereg/SAP-ADDENDUM-A6-*.md`, branch titles and placement), `runs/P2-LRF-DN/dn_analysis.json`,
`runs/P2-LRF-L1/a6_analysis.json`, the UniDisc paper (`research/sources/md/2503.20853.md`).

## 1. "Pixel denoising" in the title: advise against
What the data say (fresh fold, n = 450; exploratory, specified after the confirmatory result):
- Gaussian noise 0.1: denoise then unweighted sum 0.844, denoise then LRF 0.856, LRF alone 0.802, unweighted sum 0.733.
- JPEG quality 10: denoise then LRF 0.813, against 0.864 for LRF alone (difference -0.051, 95% interval -0.089 to -0.013): the denoiser
  HURTS under JPEG.
Why it should not be in the title:
1. The only confirmed (preregistered, fresh-fold) result is LRF without denoising. Denoise+LRF was chosen after the result and tested on
   the same fold; a title claim needs the confirmatory test (A6.12, C6-5). A reviewer would call it a post hoc headline.
2. The denoiser is a classical method (non-local means, 2005), not our contribution, and it does most of the work under noise: denoise +
   unweighted sum (0.844) is already above LRF (0.802). A title on pixel denoising invites the question "then why LRF?".
3. It reverses under JPEG (harm), so a title naming it overstates its value.
4. To make "pixel denoising + reliability weighting" the paper's method, it would need its own preregistered test on new images (a new
   fold and about 2-3 GPU hours plus a new plan): possible later, not by relabelling.
What we do instead: the abstract states it qualitatively and honestly (a classical pixel denoiser before scoring did better under Gaussian
noise but worse under JPEG); Table IV and the Discussion keep the numbers.

## 2. Shorter title
The base paper calls itself "Unified Multimodal Discrete Diffusion"; "discrete diffusion" is its main term (about 38 uses; "denoising"
about 19, for the generation steps). Using it places the paper in the diffusion-language-model area.
- A (recommended): "Reliability-Aware Fusion of Token Evidence for Image-Text Verification in Unified Discrete Diffusion"
- B: "Learned Token Reliability Weighting for Noisy Image-Text Verification in Unified Discrete Diffusion"
Both keep the content of the preregistered branch-A title (A6.12) without its length; neither uses a word A6.12 forbids ("robust",
"first", "state of the art"). The shortening is reported as a deviation from A6.12 (claim unchanged, wording shorter).

## 3. Abstract without numbers: agree
Acceptable for TNNLS and easier to read. The qualifiers stay (one model, one dataset, one noise level, preregistered, fresh images,
clean-image non-inferiority) so that the words do not overstate; every number stays in Results. Reported as a deviation from the A6.12
sentence templates (numbers moved from the abstract to Results; no claim added).

## 4. One study per paper: agree, with a split
Why it helps: one problem (verification under image noise with a frozen unified discrete diffusion model), one method (LRF), one
confirmatory test. The negative gating study dilutes the contribution, was flagged as a desk-rejection factor in the triage, and uses
about four pages that the single-study paper can give to the severity sweep, baselines and analysis.
How, without hiding a null result: this paper reports Study 2 only; it states once, in Methods, that the 500 design images came from an
earlier preregistered study of the same model, reported separately (anonymised citation), with no result of that study (this also
satisfies C6-4: no Study 1 result as motivation). Study 1 becomes its own short paper (a preregistered null result), so it is published,
not dropped.
Cost: the largest change of the paper (title, abstract, introduction, setting, Study 1 section removed, discussion, conclusion, figures,
supplement, both Word files, package). Needs the supervisor's agreement because A6.12 placed Study 1's sentence in this paper's abstract;
the split is a reported deviation.
