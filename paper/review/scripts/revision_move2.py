"""Revision 2026-10-21: census coder-agreement detail and table to the supplement (page limit). Run from paper/review."""
from pathlib import Path

M = Path("sections/06-census.tex")
S = Path("supplement.tex")
t = M.read_text(encoding="utf-8")
a = t.index("Table~\\ref{tab:census-agree} gives agreement")
b = t.index("\\end{table}", a) + len("\\end{table}")
block = t[a:b]
SUM = (r"Agreement before any reconciliation (codebook v1.1, the 172 ranks with a full text) is good for the value-rule classes: $\kappa$ is 0.82 to 0.97 for A, T, P, G and M among the 62 papers where both coders could determine a rule, and 0.40 for S (sample-then-filter), the confusion that led codebook v1.2 to add a code for confidence-ranked unmasking whose token rule is not stated. "
       r"Whether a rule can be determined at all is weaker ($\kappa=0.65$ on 149 papers), and the low eligibility $\kappa$ (0.05 at raw agreement 0.87) is a prevalence effect compounded by coder~B's read failures. The full table is in the Supplement (Section~S3).")
M.write_text(t[:a] + SUM + t[b:], encoding="utf-8")
s = S.read_text(encoding="utf-8")
anchor = "\\subsection{Value-rule classes by year and venue}"
assert s.count(anchor) == 1
moved = block.replace("\\ref{", "\\Mref{").replace("Table~\\Mref{tab:census-agree}", "Table~\\ref{tab:census-agree}").replace("\\begin{table}[t]", "\\begin{table}[h]")
s = s.replace(anchor, r"\subsection{Agreement between the two coders, in full (from Section~\Mref{sec:census-agreement})}" + "\n\\label{sec:s-census-agree}\n\n" + moved + "\n\n" + anchor)
S.write_text(s, encoding="utf-8")
print("ok", len(block.split()))
