"""Build the anonymized Paper 2 review snapshot (double-anonymous review at IEEE TNNLS).

Copies only the Paper 2 files tracked in git into OUT, replaces every author name, e-mail, username, institution and
place with ANONYMIZED, writes an anonymous README, and fails if any identifier is left in a text file or found in a binary.
Usage: python tools/make_review_snapshot.py OUT_DIR
The author version (main_camera.tex), biographies, submission drafts and Word files are not included.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]).resolve()

INCLUDE = ["exp_p2/", "analysis/paper2/", "analysis_posthoc/", "research/paper2/prereg/", "tests/exp_p2/",
           "tests/analysis_lrf/", "tools/gpu_guard.py", "paper2-tnnls/"]
INCLUDE_GLOB = [re.compile(r"^runs/P2-[^/]+/")]
EXCLUDE = [re.compile(p) for p in [
    r"__pycache__/", r"\.pyc$",
    r"^paper2-tnnls/main_camera\.", r"^paper2-tnnls/back/", r"^paper2-tnnls/drafts/", r"^paper2-tnnls/docx/",
    r"^paper2-tnnls/PORTAL-STATEMENTS\.md$", r"^paper2-tnnls/SUBMISSION-CHECKLIST\.md$", r"^paper2-tnnls/SPEC\.md$",
    r"\.log$", r"\.synctex\.gz$", r"\.fdb_latexmk$", r"\.fls$"]]

# longest first; case-sensitive except where noted
TERMS = [
    "shlok.goenka2023@vitstudent.ac.in", "subramaniyaswamy.v@vit.ac.in", "balaji.gn@vit.ac.in", "shlokgoenka77@gmail.com",
    "shlokDS16", "Shlok Kumar Goenka", "Shlok Goenka", "Goenka", "Shlok", "shlok",
    "Subramaniyaswamy Vairavasundaram", "Vairavasundaram", "Subramaniyaswamy", "Balaji~G~N", "Balaji G N", "Balaji",
    "Ganesh Khekare", "Khekare", "Thenmozhi", "Manjula",
    "Vellore Institute of Technology", "Vellore", "Tamil Nadu", "vitstudent", "vit.ac.in",
]
WORD_TERMS = ["VIT", "SCSE"]   # whole-word, uppercase only (ViT, the vision transformer, is untouched)
TEXT_EXT = {".py", ".md", ".tex", ".bib", ".bbl", ".json", ".jsonl", ".csv", ".txt", ".sh", ".cfg", ".toml", ".yaml",
            ".yml", ".sty", ".cls", ".bst", ".aux", ".out", ".blg", ".ps1", ".ini", ".rc", ""}
MASK = "ANONYMIZED"
README = """# Review snapshot (anonymized)

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
"""


def wanted(p: str) -> bool:
    if any(e.search(p) for e in EXCLUDE):
        return False
    return any(p.startswith(i) for i in INCLUDE) or any(g.search(p) for g in INCLUDE_GLOB)


def mask(s: str) -> str:
    for t in TERMS:
        s = s.replace(t, MASK)
    for t in WORD_TERMS:
        s = re.sub(r"\b" + t + r"\b", MASK, s)
    return s


def leftover(s: str) -> list[str]:
    hits = [t for t in TERMS if t.lower() in s.lower() and t.lower() not in MASK.lower()]
    hits += [t for t in WORD_TERMS if re.search(r"\b" + t + r"\b", s)]
    return hits


files = [p for p in subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True,
                                   encoding="utf-8").stdout.splitlines() if wanted(p)]
problems, n_masked = [], 0
for rel in files:
    src = ROOT / rel
    if not src.exists():
        continue
    dst = OUT / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    data = src.read_bytes()
    if src.suffix.lower() in TEXT_EXT:
        try:
            txt = data.decode("utf-8")
        except UnicodeDecodeError:
            txt = None
        if txt is not None:
            new = mask(txt)
            n_masked += new != txt
            left = leftover(new)
            if left:
                problems.append(f"text {rel}: {left}")
            dst.write_bytes(new.encode("utf-8"))
            continue
    low = data.lower()
    for t in TERMS:
        if t.lower().encode() in low and len(t) > 4:
            problems.append(f"binary {rel}: contains {t!r}")
    dst.write_bytes(data)
(OUT / "README.md").write_text(README, encoding="utf-8")
print(f"files {len(files)}, text files masked {n_masked}, problems {len(problems)}")
for p in problems[:40]:
    print("  ", p)
sys.exit(1 if problems else 0)
