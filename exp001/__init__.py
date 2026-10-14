"""EXP-001 implementation (card research/preregistration/EXP-001-crossmodal-unidisc.md, v0.5 SIGNED).

Layout (one choice, documented in runs/EXP-001/IMPLEMENTATION.md):
  exp001/            generation + estimator + gate code (torch/numpy; importable from both the generation venv and the eval venv)
  analysis/EXP-001/  frozen lists and rules of Appendix B, and the frozen analysis scripts (hashed in runs/EXP-001/gates/manifest.json)
  tests/exp001/      pytest unit tests (no GPU needed unless marked)
"""
