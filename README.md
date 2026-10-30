# Review snapshot (anonymized)

Anonymized copy of the code, preregistration documents, hash pins, recorded predictions and analysis outputs behind the
submitted manuscript on learned reliability-aware fusion of token evidence in UniDisc. Names, e-mails, usernames and the
institution are replaced by ANONYMIZED; the full repository with its commit history is released after review.

| Path | Contents |
|---|---|
| `paper2-tnnls/` | LaTeX sources of the paper (`main.tex`) and the supplement, figure and table scripts (`scripts/`), generated tables and figures. |
| `research/paper2/prereg/` | Preregistration cards, statistical analysis plans and dated addenda, sign-offs and audit reports. |
| `exp_p2/` | Experiment code (scorers, gate of Study 1, learned reliability-aware fusion of Study 2, guarded run drivers). |
| `analysis/paper2/`, `analysis_posthoc/` | Analysis code, CLIP/SigLIP baselines and the exploratory ablation. |
| `runs/P2-*` | Committed result files of every run the paper cites; per-item arrays are not included (SHA-256 manifests are). |
| `tests/` | Unit tests. |

Every figure and table is recomputed by a script in `paper2-tnnls/scripts/` from the files under `runs/`; supplement
Section S-VIII lists the script and the JSON keys for each. Model weights (UniDisc, CLIP, SigLIP) and COCO images are not
included; their pinned revisions are in supplement Section S-I.
