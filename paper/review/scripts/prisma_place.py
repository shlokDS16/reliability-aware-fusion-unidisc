"""DOCX layout: the PRISMA figure goes right after the Study selection heading (no half-empty page in Word) and gets
a shorter caption. LaTeX float placement is unaffected. Run from paper/review."""
import re
from pathlib import Path

p = Path("sections/02-method.tex")
t = p.read_text(encoding="utf-8")
a = t.index("\\begin{figure}[tbp]")
b = t.index("\\end{figure}", a) + len("\\end{figure}")
fig = t[a:b]
t = t[:a] + t[b:]
t = re.sub(r"\n{3,}", "\n\n", t)
cap_a = fig.index("\\caption{")
cap_b = fig.index("\\label{fig:prisma}")
fig = fig[:cap_a] + (r"\caption{PRISMA 2020 flow diagram of the review. The three identification strands are screened separately and meet at full-text assessment. Grey boxes are records removed or excluded, and dashed boxes are records identified but not assessed when screening stopped; X0 to X7 are the exclusion reasons of Section~\ref{sec:method-eligibility}. The bottom row is the targeted set of landmark studies.}" + "\n") + fig[cap_b:]
anchor = "\\label{sec:method-screening}\n"
assert t.count(anchor) == 1
t = t.replace(anchor, anchor + fig + "\n")
p.write_text(t, encoding="utf-8")
print("ok")
