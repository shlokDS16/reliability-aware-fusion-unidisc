"""Corrections to s6-refs.bib from the citation-validator report of 2026-10-21 (run after s6_bib.py and
s6_bib_local.py; idempotent).

    python -E -P paper/review/scripts/s6_bib_fix.py

Report: side-session notes, s6-citation-validation.md (78 entries: 73 OK, 4 FIX, 1 FAIL). Fixes:
- R0963: record title added to s6-keys.json (from analysis/screening/ta-recheck-candidates-v1.2.jsonl).
- doi:10.1109/fmsys72110.2026.00015: Crossref's "&amp;" in the venue name.
- openreview:UUcPqCJLiM (M13397) and openreview:TreNQ0xS5A (M19293): titles as printed on page 1 of the screened text
  ("D-MINER: EXTRACTING ...", "DOE-3: WORLD-LANGUAGE-ACTION MODELS ...").
- openreview:3oLO4KQuhU (M19013, the FAIL: page 1 names no venue): venue and date from the review's own OpenReview record
  (research/review/corpus: venue "ICLR 2027 Conference Submission", published 2026-09-19).
"""
import json
from pathlib import Path

P = Path(__file__).resolve().parents[1]
bib = (P / "s6-refs.bib").read_text(encoding="utf-8")
K = json.loads((P / "tables/s6-keys.json").read_text(encoding="utf-8"))
REPL = [
    ("\\&amp; Internet of Things", "\\& Internet of Things"),
    ("{{D-Miner: Extract Alignment Data", "{{D-Miner: Extracting Alignment Data"),
    ("{{World-Language-Action Models for Autonomous Driving}}", "{{DOE-3: World-Language-Action Models for Autonomous Driving}}"),
    ("Post-Training Quantization for Unified Multimodal Models}},\n  year = {2026},\n  howpublished = {Paper under double-blind review, OpenReview}",
     "Post-Training Quantization for Unified Multimodal Models}},\n  year = {2026},\n  howpublished = {Submitted to ICLR 2027 (under double-blind review), OpenReview}"),
]
for old, new in REPL:
    if new in bib:
        continue
    assert bib.count(old) == 1, old
    bib = bib.replace(old, new)
(P / "s6-refs.bib").write_text(bib, encoding="utf-8")
K["record_titles"]["R0963"] = "Bernini: Latent Semantic Planning for Video Diffusion"
K["record_titles"]["M13397"] = K["record_titles"]["M13397"].replace("D-Miner: Extract ", "D-Miner: Extracting ")
if not K["record_titles"]["M19293"].startswith("DOE-3"):
    K["record_titles"]["M19293"] = "DOE-3: " + K["record_titles"]["M19293"]
K["validation"] = {"date": "2026-10-21", "by": "citation-validator", "entries": 78, "ok": 73, "fix": 4, "fail": 1,
                   "all_fixes_applied": True, "script": "scripts/s6_bib_fix.py"}
(P / "tables/s6-keys.json").write_text(json.dumps(K, indent=1), encoding="utf-8")
print("fixed")
