"""Abstract led by the technical contributions (supervisor: PRISMA itself is not a contribution). CSUR rules: at most
100 words, no first person, no mathematics, no citations, not starting with "This paper". Numbers repeat the body."""
from pathlib import Path

t = Path("main.tex").read_text(encoding="utf-8")
a = t.index("\\begin{abstract}")
b = t.index("\\end{abstract}")
keep = "\n".join(l for l in t[a:b].split("\n") if l.startswith("%") or l.startswith("\\begin"))
ABS = ("Diffusion language models generate text by refining many positions in parallel, and unified variants extend this "
       "to images. This survey contributes a unified notation that describes every generator by five design choices and "
       "places 47 discrete, continuous and multimodal models; an error budget that separates factorisation, learning and "
       "decoding-rule error and classifies methods by the term they change; and a census showing that 147 of 153 sampled "
       "papers report headline results with a non-plain or unstated decoding rule. Synthesising 615 studies, it finds "
       "compute-matched comparisons with autoregressive models rare and derives a decision framework and reporting checklist.")
n = len(ABS.split())
assert n <= 100, n
Path("main.tex").write_text(t[:a] + keep + "\n" + ABS + "\n" + t[b:], encoding="utf-8")
print("abstract words:", n)
