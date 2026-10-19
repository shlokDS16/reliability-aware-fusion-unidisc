"""Prototype of the s6.3 cell check, only to confirm the unit-test expectations of the plan."""
import re, sys, hashlib
sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706"
sys.path.insert(0, ROOT + "/analysis/screening")
import quote_check as qc

VAL = re.compile(r"^[-+−±]?(\d[\d.,]*|\.\d+)(%|x|×)?[↑↓*†‡]*$")
VAL_WORDS = {"-", "–", "—", "n/a", "N/A", "✓", "✗", "×", "*"}


def pages(text):
    out = {}
    cur = 1
    for line in text.split("\n"):
        m = re.match(r"^=== page (\d+) ===$", line)
        if m:
            cur = int(m.group(1)); out.setdefault(cur, []); continue
        out.setdefault(cur, []).append(line)
    return out


def tokens(lines):
    toks = []
    i = 0
    norm = [qc.normalise(l) for l in lines]
    joined = []
    while i < len(norm):
        l = norm[i]
        while re.search(r"[A-Za-z]-$", l) and i + 1 < len(norm) and re.match(r"^[a-z]", norm[i + 1]):
            l = l[:-1] + norm[i + 1]; i += 1
        joined.append(l); i += 1
    for ln, l in enumerate(joined):
        for k, t in enumerate(l.split()):
            toks.append((t, k == 0))
    return toks


def valuelike(t):
    return bool(VAL.match(t)) or t in VAL_WORDS


def cell_check(text, page, row_label, first_col, cells, occurrence=None):
    P = pages(text)
    if page not in P:
        return "row_not_found", None
    T = tokens(P[page])
    tt = [t for t, _ in T]
    L = qc.normalise(row_label).split(); C = qc.normalise(cells).split()
    if len(L) + len(C) > 40:
        return "too_long", None
    starts = [p for p in range(len(tt) - len(L) + 1) if tt[p:p + len(L)] == L and (T[p][1] or (p > 0 and valuelike(tt[p - 1])))]
    if not starts:
        return "row_not_found", None
    hits = [p for p in starts if tt[p + len(L) + first_col - 1: p + len(L) + first_col - 1 + len(C)] == C]
    if not hits:
        return "cells_mismatch", None
    if len(hits) > 1 and not occurrence:
        return "ambiguous_row", None
    p = hits[(occurrence or 1) - 1]
    return "pass", tt[p + len(L):]


txt = open(ROOT + "/research/sources/md/fulltext-pymupdf/M03416.txt", encoding="utf-8").read()
print("sha", hashlib.sha256(open(ROOT + "/research/sources/md/fulltext-pymupdf/M03416.txt", "rb").read()).hexdigest()[:16])
print("T01", cell_check(txt, 7, "w/o diffusion denoising", 1, "57.1 58.4 47.7")[0])
print("T02", cell_check(txt, 7, "w/o ensembling", 1, "57.1 58.4 47.7")[0])
print("T03", cell_check(txt, 7, "diffusion denoising", 1, "57.1 58.4 47.7")[0])
print("T08", cell_check(txt, 8, "w/o diffusion denoising", 1, "57.1 58.4 47.7")[0])
print("T09", cell_check(txt, 7, "w/o diffusion denoising", 2, "58.4 47.7")[0])
st, rest = cell_check(txt, 7, "w/o diffusion denoising", 1, "57.1 58.4 47.7"); print("T05 col2 token", rest[1])
print("DiffuseDef row", cell_check(txt, 7, "DiffuseDef", 1, "84.5 86.0 84.6")[0])
print("T04 qc 6tok", qc.quote_status("w/o diffusion denoising 57.1 58.4 47.7", txt))
print("T04 qc long", qc.quote_status("w/o ensembling 64.2 65.8 54.9 w/o diffusion denoising 57.1 58.4 47.7", txt))
print("T04 qc from DiffuseDef", qc.quote_status("DiffuseDef 84.5 86.0 84.6 w/o ensembling 64.2 65.8 54.9", txt))
pt = "\n".join(pages(txt)[7]);
print("header found", "Method TF TB BA" in qc.normalise(pt))
cap = "Table 3: Ablation results for DiffuseDef's accuracy under attack on AGNews datasets."
print("caption found", qc.normalise(cap) in qc.normalise(pt), len(qc.normalise(cap).split()))
# T14 synthetic wide table
rows = ["=== page 1 ===", "Model", "A", "B", "C", "D", "E", "F", "G", "Ours"] + [f"{90 + i}.0" for i in range(7)]
for r in range(1, 7):
    rows += [f"w/o c{r}"] + [f"{80 - r}.{i}" for i in range(7)]
syn = "\n".join(rows)
print("T14 cell", cell_check(syn, 1, "w/o c5", 1, " ".join(f"75.{i}" for i in range(7)))[0])
row5 = "w/o c5 " + " ".join(f"75.{i}" for i in range(7))
words = qc.normalise(syn).split()
# all prose quotes ending at row 5's last value, starting at different positions, <= 40 words
end = words.index("75.6") + 1
res = {}
for s in range(end - 6, max(-1, end - 41), -1):
    q = " ".join(words[s:end]); res[len(q.split())] = qc.quote_status(q, syn)
print("T14 prose statuses by length", sorted(set(res.values())), "found lengths", [k for k, v in res.items() if v == "found"])
# T15
syn2 = "=== page 1 ===\nModel\nX\nY\nOurs\n1.0\n2.0\nText line here.\nModel\nX\nY\nOurs\n1.0\n2.0"
print("T15", cell_check(syn2, 1, "Ours", 1, "1.0 2.0")[0], cell_check(syn2, 1, "Ours", 1, "1.0 2.0", occurrence=2)[0])
# T20
syn3 = "=== page 1 ===\nModel\nA\nB\nDiffu-\nsion-LM\n1.0\n2.0"
print("T20", cell_check(syn3, 1, "Diffusion-LM", 1, "1.0 2.0")[0])
# T21 Muddit
mt = open(ROOT + "/research/sources/md/fulltext-pymupdf/M12766.txt", encoding="utf-8").read()
st, rest = cell_check(mt, 8, "PixArt-α (Chen et al., 2024b)", 1, "- Diffusion 0.6 0.48 0.98 0.50 0.44 0.80 0.08 0.07")
print("T21", st, rest[4] if rest else None)
pm = qc.normalise("\n".join(pages(mt)[8]))
hdr = "Overall ↑Objects ↑Counting ↑Colors ↑Position ↑ Color ↑ Attribution Single Two"
print("T21 header found", qc.normalise(hdr) in pm)
print("numbers-only qc", qc.quote_status("0.61 0.98 0.72 0.54 0.82 0.19", mt))
