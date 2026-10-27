"""GATE (Paper 2) MUST-tier code: scores, conformal-risk-control calibration, gate arms, evidence, corruptions, baselines,
folds, hard negatives, headroom check, runners' shared loop. Spec: research/paper2/method/GATE-METHOD-SPEC-v2-2026-10-28.md
(v1 for anything v2 leaves unchanged). Notes: research/paper2/method/GATE-IMPLEMENTATION-NOTES-2026-10-28.md.

Everything except the model passes in `scores`/`dcache`/`runner` is pure numpy and unit-tested on CPU (tests/exp_p2/test_gate_*.py);
the model passes take any object with the `UniScorer` interface (`caption_ids, preprocess, encode, build, logits_fn, L_I`)."""
