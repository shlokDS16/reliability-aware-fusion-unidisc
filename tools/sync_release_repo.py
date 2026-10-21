"""Mirror the built release folder into the local clone of shlokDS16/dlm-review-prisma, commit and push.

    python -I tools/sync_release_repo.py "<commit message>"

Build folder (made by tools/build_release_paper1.py, deleted and rebuilt on every build):
    C:/Users/Shlok/Downloads/Multi-Modality Language model/release/dlm-review-prisma-v1
Clone (kept between builds; holds the .git history):
    C:/Users/Shlok/Downloads/Multi-Modality Language model/release/dlm-review-prisma-git
The clone is created on first use. Every file in the clone except .git is replaced by the build folder's content,
so removed files are removed in the repository too. Refuses to run if the build folder's secret scan is not clean.
"""
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(r"C:/Users/Shlok/Downloads/Multi-Modality Language model/release")
BUILD = BASE / "dlm-review-prisma-v1"
CLONE = BASE / "dlm-review-prisma-git"
REMOTE = "https://github.com/shlokDS16/dlm-review-prisma.git"
msg = sys.argv[1] if len(sys.argv) > 1 else "Update release"


def git(*a, check=True):
    r = subprocess.run(["git", "-C", str(CLONE), *a], capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode:
        sys.exit(f"git {' '.join(a)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


assert (BUILD / "SECRET-SCAN.txt").read_text(encoding="utf-8").strip() == "no hits", "secret scan not clean"
if not (CLONE / ".git").exists():
    CLONE.mkdir(parents=True, exist_ok=True)
    git("init", "-b", "main")
    git("remote", "add", "origin", REMOTE)
for p in CLONE.iterdir():
    if p.name == ".git":
        continue
    shutil.rmtree(p) if p.is_dir() else p.unlink()
for p in BUILD.iterdir():
    (shutil.copytree if p.is_dir() else shutil.copy2)(p, CLONE / p.name)
git("add", "-A")
if not git("status", "--porcelain"):
    print("nothing to commit")
    sys.exit(0)
git("commit", "-m", msg)
out = subprocess.run(["git", "-C", str(CLONE), "push", "-u", "origin", "main"], capture_output=True, text=True,
                     encoding="utf-8")
if out.returncode:
    sys.exit("push failed: " + out.stderr.strip()[-500:])
print("pushed:", git("log", "-1", "--format=%h %s"), "| files:", len(git("ls-files").splitlines()))
