"""Hash pins that survive the checked-out line endings (re-audit N4). `tools/gpu_guard.py` is pinned by the EXP-001 manifest (SHA-256 of the committed bytes) and must not be edited, but with
`core.autocrlf=true` the working-tree copy has CRLF endings and hashes differently. A pin check therefore passes if EITHER the committed blob (`git show <rev>:<path>`) OR the working copy with
CRLF normalised to LF matches. A real content change fails both. Read-only; nothing here writes to the pinned file. (`exp003/manifest.py: reused_check`, which hashes raw working-tree
bytes, belongs to Paper 1 and is not changed; on this checkout it reports a false mismatch for the same reason.)"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def working_sha256(path: Path, normalise_crlf: bool = True) -> str | None:
    p = Path(path)
    if not p.exists():
        return None
    b = p.read_bytes()
    return sha256_bytes(b.replace(b"\r\n", b"\n") if normalise_crlf else b)


def committed_sha256(rel_path: str, rev: str = "HEAD", repo: Path = ROOT) -> str | None:
    r = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{rel_path}"], capture_output=True)
    return sha256_bytes(r.stdout) if r.returncode == 0 else None


def check_pin(rel_path: str, expected: str, *, repo: Path = ROOT, rev: str = "HEAD") -> dict:
    """ok if the committed blob or the CRLF-normalised working copy hashes to `expected`; `via` says which."""
    blob, work = committed_sha256(rel_path, rev, repo), working_sha256(Path(repo) / rel_path)
    via = "committed blob" if blob == expected else ("working copy (CRLF normalised)" if work == expected else None)
    return dict(path=rel_path, expected=expected, ok=via is not None, via=via, committed_blob=blob, working_normalised=work, working_raw=working_sha256(Path(repo) / rel_path, False))


def gpu_guard_pin(repo: Path = ROOT) -> dict:
    """tools/gpu_guard.py against the pin recorded in runs/EXP-001/gates/manifest.json (gpu_guard.sha256)."""
    mp = Path(repo) / "runs" / "EXP-001" / "gates" / "manifest.json"
    if not mp.exists():
        return dict(path="tools/gpu_guard.py", ok=None, via=None, note="manifest not found; not checked")
    return check_pin("tools/gpu_guard.py", json.loads(mp.read_text(encoding="utf8"))["gpu_guard"]["sha256"], repo=repo)
