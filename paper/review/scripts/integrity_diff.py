"""Compare numbers, citation keys, labels, refs and equations of each section file between a git revision and the
working tree. Prose may change; these may not. Usage (from the repository root):
    python paper/review/scripts/integrity_diff.py [REV]      (default REV = HEAD)
"""
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REV = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
FILES = sorted(str(p).replace("\\", "/") for p in Path("paper/review/sections").glob("*.tex")) + ["paper/review/main.tex"]
NUM = re.compile(r"(?<![A-Za-z0-9_:.-])[-+]?\d[\d,]*(?:\.\d+)?(?![A-Za-z0-9_-])")


def body(t):
    out = []
    for l in t.split("\n"):
        if l.lstrip().startswith("%"):
            continue
        m = re.search(r"(?<!\\)%", l)
        out.append(l[:m.start()] if m else l)
    return "\n".join(out)


def facets(t):
    t = body(t)
    t_noref = re.sub(r"\\(cite[tp]?|ref|eqref|label|Mref|input|includegraphics)(\[[^\]]*\])?\{[^}]*\}", " ", t)
    return {"numbers": Counter(n.replace(",", "") for n in NUM.findall(t_noref)),
            "cites": Counter(k.strip() for g in re.findall(r"\\cite[tp]?\{([^}]*)\}", t) for k in g.split(",")),
            "labels": Counter(re.findall(r"\\label\{([^}]*)\}", t)),
            "refs": Counter(re.findall(r"\\(?:ref|eqref)\{([^}]*)\}", t)),
            "math": Counter(re.sub(r"\s+", "", m) for m in re.findall(r"\$([^$]+)\$", t))}


bad = 0
for f in FILES:
    try:
        old = subprocess.run(["git", "show", f"{REV}:{f}"], capture_output=True, text=True, encoding="utf-8").stdout
    except Exception:
        old = ""
    if not old:
        continue
    new = Path(f).read_text(encoding="utf-8")
    a, b = facets(old), facets(new)
    for k in a:
        lost, added = a[k] - b[k], b[k] - a[k]
        if lost or added:
            bad += 1
            print(f"{f} [{k}] lost={dict(lost)} added={dict(added)}")
    wa, wb = len(body(old).split()), len(body(new).split())
    print(f"{f}: words {wa} -> {wb}")
print("files with changed facets:", bad)
