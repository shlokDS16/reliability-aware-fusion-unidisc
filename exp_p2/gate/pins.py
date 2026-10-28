"""Hash pins that survive the checked-out line endings, and the dirty-tree guard (delta audit N4). `tools/gpu_guard.py` is pinned by the EXP-001 manifest (SHA-256 of the committed bytes) and must
not be edited. With `core.autocrlf=true` the working-tree copy has CRLF endings, so a pin check passes only if BOTH the committed blob (`git show <rev>:<path>`) hashes to the pin AND the working copy,
CRLF normalised to LF, equals that blob: a CRLF checkout passes, an uncommitted edit, a committed change or a missing file fails. `require_clean` / `git_dirty` make the runners and the driver refuse
to start when `git status --porcelain -- exp_p2 tools` shows uncommitted changes (unless --allow-dirty, which is recorded). Read-only. (`exp003/manifest.py: reused_check`, which hashes raw working-tree
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
    """ok only if BOTH hold: the committed blob hashes to `expected`, AND the working copy (CRLF normalised to LF) equals the committed blob. So a CRLF checkout of the pinned bytes
    passes, while an uncommitted edit of a pinned file fails (delta audit N4), as does a committed change or a missing file."""
    blob, work = committed_sha256(rel_path, rev, repo), working_sha256(Path(repo) / rel_path)
    blob_ok, work_ok = blob == expected, (work is not None and work == blob)
    return dict(path=rel_path, expected=expected, ok=bool(blob_ok and work_ok), via=("committed blob == pin, working copy (CRLF normalised) == blob" if blob_ok and work_ok else None),
                committed_matches_pin=blob_ok, working_matches_committed=work_ok, committed_blob=blob, working_normalised=work, working_raw=working_sha256(Path(repo) / rel_path, False))


def git_dirty(repo: Path = ROOT, paths=("exp_p2", "tools")) -> list[str]:
    """`git status --porcelain -- <paths>`: every line is an uncommitted change (modified, staged, deleted or untracked). If git cannot be run the answer is a single error line (fail closed)."""
    r = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", *paths], capture_output=True, text=True)
    if r.returncode != 0:
        return [f"git status failed: {r.stderr.strip()[:200]}"]
    return [l for l in r.stdout.splitlines() if l.strip()]


def dirty_files() -> list[str]:
    """Uncommitted changes under exp_p2 and tools of this checkout (the code that produces results)."""
    return git_dirty(ROOT, ("exp_p2", "tools"))


EXIT_DIRTY = 11


def require_clean(allow_dirty: bool = False, *, label: str = "") -> tuple[bool, list[str]]:
    """(ok, files). Prints the uncommitted files when there are any. ok is False when there are some and --allow-dirty was not given; with --allow-dirty it is True and the caller must record
    `allow_dirty` and the file list in the run config."""
    files = dirty_files()
    if files:
        import sys
        print(f"{label or 'code'} has uncommitted changes under exp_p2/ or tools/:" + "".join("\n  " + l for l in files)
              + ("\n  --allow-dirty given: continuing, recorded in the run config" if allow_dirty else "\n  STOP: commit first (or pass --allow-dirty, which is recorded)"), file=sys.stderr)
    return (not files) or bool(allow_dirty), files


def gpu_guard_pin(repo: Path = ROOT) -> dict:
    """tools/gpu_guard.py against the pin recorded in runs/EXP-001/gates/manifest.json (gpu_guard.sha256)."""
    mp = Path(repo) / "runs" / "EXP-001" / "gates" / "manifest.json"
    if not mp.exists():
        return dict(path="tools/gpu_guard.py", ok=None, via=None, note="manifest not found; not checked")
    return check_pin("tools/gpu_guard.py", json.loads(mp.read_text(encoding="utf8"))["gpu_guard"]["sha256"], repo=repo)
