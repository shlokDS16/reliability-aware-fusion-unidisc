"""Page limit: the census figure (not referenced in the main text) moves to Supplement S3. Run from paper/review."""
import re
from pathlib import Path

C = Path("sections/06-census.tex")
t = C.read_text(encoding="utf-8")
a = t.rindex("\\begin{figure}", 0, t.index("\\label{fig:census}"))
b = t.index("\\end{figure}", a) + len("\\end{figure}")
fig = t[a:b]
C.write_text(t[:a] + t[b:], encoding="utf-8")
fig = re.sub(r"\\ref\{(sec|tab|eq):", r"\\Mref{\1:", fig).replace("\\begin{figure}[t]", "\\begin{figure}[h]")
S = Path("supplement.tex")
s = S.read_text(encoding="utf-8")
anchor = "\\subsection{Value-rule classes by year and venue}"
assert s.count(anchor) == 1
s = s.replace(anchor, r"\subsection{The census results as a figure (from Section~\Mref{sec:census-results})}" + "\n\\label{sec:s-census-fig}\n\n" + fig + "\n\n" + anchor)
S.write_text(s, encoding="utf-8")
print("moved", len(fig))
