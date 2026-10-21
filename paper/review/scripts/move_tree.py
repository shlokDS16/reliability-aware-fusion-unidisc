"""Page limit: the taxonomy tree of the 47 design-space models moves from Section 1 to Supplement S5 (label fig:tree).
Run from paper/review."""
import re
from pathlib import Path

I = Path("sections/01-introduction.tex")
t = I.read_text(encoding="utf-8")
a = t.rindex("\\begin{figure}", 0, t.index("\\input{tables/taxonomy-tree.tex}"))
b = t.index("\\end{figure}", a) + len("\\end{figure}")
fig = t[a:b]
t = t[:a] + t[b:]
old = "Figure~\\ref{fig:taxonomy} places the 47 models of the design space (Section~\\ref{sec:design}) in a taxonomy by state space and model family, and gives an entry point to the literature: each leaf cites the model's paper."
assert t.count(old) == 1
t = t.replace(old, "\\suppFigTree{} in the Supplement places the 47 models of the design space (Section~\\ref{sec:design}) in a taxonomy by state space and model family, and gives an entry point to the literature: each leaf cites the model's paper.")
I.write_text(t, encoding="utf-8")

fig = fig.replace("\\label{fig:taxonomy}", "\\label{fig:tree}").replace("\\begin{figure}[t]", "\\begin{figure}[h]")
fig = re.sub(r"\\ref\{(sec|tab):", r"\\Mref{\1:", fig).replace("\\suppTabDesign{}", "Table~\\ref{tab:design}")
S = Path("supplement.tex")
s = S.read_text(encoding="utf-8")
anchor = "\\subsection{Condensed table and code key}"
assert s.count(anchor) == 1
s = s.replace(anchor, "\\subsection{Taxonomy of the 47 models (from Section~\\Mref{sec:intro})}\n\\label{sec:s-tree}\n\n" + fig + "\n\n" + anchor)
S.write_text(s, encoding="utf-8")

p = Path("scripts/supprefs.py")
q = p.read_text(encoding="utf-8")
if "suppFigTree" not in q:
    q = q.replace('"suppFigDots": "fig:taxonomy"}', '"suppFigDots": "fig:taxonomy", "suppFigTree": "fig:tree"}')
    assert "suppFigTree" in q
    p.write_text(q, encoding="utf-8")
sp = Path("supprefs.tex")
st = sp.read_text(encoding="utf-8")
if "suppFigTree" not in st:
    sp.write_text(st + "\\newcommand{\\suppFigTree}{Figure~S?}\n", encoding="utf-8")
print("ok")
