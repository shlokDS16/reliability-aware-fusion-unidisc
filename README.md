# Learned Reliability-Aware Fusion of Token Evidence in UniDisc (Paper 2)

Code, preregistration documents, hash pins, recorded predictions and analysis outputs for the paper

> Learned Reliability-Aware Fusion of Token Evidence Raised Image-Text Verification Accuracy Under Gaussian Noise in a
> Unified Masked Diffusion Model: A Preregistered Confirmation in UniDisc (submitted to IEEE Transactions on Neural Networks
> and Learning Systems).

The paper reports two separately preregistered studies of image-text verification under image damage in the pretrained
unified masked diffusion model UniDisc on COCO val2017 image-caption pairs: a likelihood-based gate on image tokens
(Study 1) and a frozen learned reliability-aware weighting of per-token evidence tested on a fresh fold (Study 2).

This repository is private during review. It holds the project's full git history because the paper and its supplement
(Section S-I) cite commit identifiers for every pin, freeze and analysis run; those identifiers exist only in this history.

## Where things are

| Path | Contents |
|---|---|
| `paper2-tnnls/` | LaTeX sources of the paper (`main.tex` = anonymous review copy, `main_camera.tex` = author version) and the supplement (`supplement/`), figure and table scripts (`scripts/`), generated tables and figures, Word versions (`docx/`). |
| `research/paper2/prereg/` | Preregistration cards, statistical analysis plans and their dated addenda, red-team sign-offs and audit reports. |
| `exp_p2/` | Experiment code: scorers, gate (Study 1), learned reliability-aware fusion (Study 2), run drivers with GPU memory and slow-item guards. |
| `analysis/paper2/`, `analysis_posthoc/` | Analysis code for both studies, baselines (CLIP, SigLIP) and the exploratory ablation. |
| `runs/P2-*` | Committed result files of every run the paper cites (configs, item records, predictions, analysis JSON, telemetry). Per-item arrays are not tracked; their SHA-256 manifests are. |
| `runs/P2-LRF-PINS/pins.json` | Scorer pins of Study 2. |
| `runs/P2-ENV/pip-freeze-2026-10-30.txt` | Software environment (recorded after the runs). |
| `tests/` | Unit tests (`python -m pytest tests`). |
| `research/ledgers/` | Append-only decision and experiment ledgers. |

Other folders (`paper/`, `paper2/`, `paper2-tmlr/`, `exp001/`, `exp003/`, parts of `research/`) belong to related work of
the same project and are kept because they share the history.

## Rebuilding the paper's numbers, figures and tables

Every figure and table of the paper and supplement is computed by a script in `paper2-tnnls/scripts/` from the committed
files under `runs/`; supplement Section S-VIII lists, for each figure and table, the script and the exact JSON keys it
reads. Typical use (Python 3, the packages in the environment file, a LaTeX installation):

```bash
cd paper2-tnnls
bash build.sh                       # main.pdf (review copy), main_camera.pdf (author version), supplement.pdf, checks
python scripts/make_docx.py         # Word versions of the review copy (needs pandoc; Word for the layout pass)
```

Re-running the GPU stages needs the model weights, which are not included: UniDisc, CLIP ViT-L/14 and SigLIP so400m at the
revisions pinned in supplement Section S-I, and the public COCO val2017 images and captions. The runs used one 12 GB laptop
GPU (RTX 5070 Ti) with the guards described in the supplement.

## Archive and licence

A release of this repository is archived on Zenodo (doi: 10.5281/zenodo.23810711; draft until acceptance). Licence: set at public release
(planned: MIT for code; CC BY 4.0 for text, documents and results).

## Authors

Shlok Goenka (ORCID 0009-0002-8581-5657), Subramaniyaswamy Vairavasundaram (corresponding author, subramaniyaswamy.v@vit.ac.in;
ORCID 0000-0001-5328-7672), and Balaji G N (ORCID 0000-0002-5346-0989),
School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, India.
