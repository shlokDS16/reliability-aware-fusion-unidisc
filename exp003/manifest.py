"""Manifest and freezes of EXP-003 (card 8 item 0, 11). Pure Python.

  manifest()          re-hash every reused EXP-001 file against runs/EXP-001/gates/manifest.json and hash the new files -> runs/EXP-003/manifest.json
  freeze(name, files) write runs/EXP-003/freeze-<name>.json (SHA-256 of the listed files); check_freeze(name) verifies them later
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from exp003.config import ROOT, RUNS

M1 = ROOT / "runs" / "EXP-001" / "gates" / "manifest.json"
AN3 = ROOT / "analysis" / "EXP-003"
PILOT_FILES = ["pilot_analysis.py", "stats.py", "tables.py", "nounkey.py", "coco_object_nouns.txt"]
FROZEN_ANALYSIS_FILES = PILOT_FILES + ["score.py", "frozen_analysis.py"]


def sha(p: Path):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).exists() else None


def reused_check():
    m = json.loads(M1.read_text(encoding="utf8"))
    bad, n = [], 0
    for sec, base in (("appendix_b_frozen", ROOT / "analysis" / "EXP-001"), ("analysis_code", ROOT / "analysis" / "EXP-001"),
                      ("generation_code", ROOT / "exp001")):
        for fn, h in m[sec].items():
            if isinstance(h, str) and len(h) == 64:
                n += 1
                if sha(base / fn) != h:
                    bad.append(f"{sec}/{fn}")
    n += 1
    if sha(ROOT / "tools" / "gpu_guard.py") != m["gpu_guard"]["sha256"]:
        bad.append("tools/gpu_guard.py")
    return dict(n_checked=n, mismatches=bad, exp001_manifest_generation=m["generation"], exp001_manifest_sha256=sha(M1))


def new_files():
    out = {}
    for d in (ROOT / "exp003", AN3, ROOT / "tests" / "exp003"):
        for p in sorted(d.glob("*")):
            if p.is_file() and p.suffix in (".py", ".txt"):
                out[str(p.relative_to(ROOT)).replace("\\", "/")] = sha(p)
    return out


def manifest():
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=str(ROOT)).stdout.strip()
    out = dict(card="EXP-003 v0.3.2", git_head=git, reused_exp001=reused_check(), new_files=new_files(), pools_json_sha256=sha(RUNS / "pools.json"))
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / "manifest.json").write_text(json.dumps(out, indent=1), encoding="utf8")
    return out


def freeze(name: str, files=PILOT_FILES):
    d = {f: sha(AN3 / f) for f in files}
    RUNS.mkdir(parents=True, exist_ok=True)
    p = RUNS / f"freeze-{name}.json"
    if p.exists():
        raise FileExistsError(p)
    p.write_text(json.dumps(dict(name=name, files=d, combined_sha256=hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()), indent=1))
    return d


def check_freeze(name: str):
    p = RUNS / f"freeze-{name}.json"
    d = json.loads(p.read_text())["files"]
    return [f for f, h in d.items() if sha(AN3 / f) != h]
