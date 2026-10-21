"""Revision 2026-10-21 (author's request, page limit): the formalism figure of Section 3 and the lever table of
Section 7 move to the supplement, with short summaries in the main text. The lever summary restates the table rows;
it adds no number. Run from paper/review."""
import re
from pathlib import Path


def edit(f, old, new):
    p = Path(f)
    t = p.read_text(encoding="utf-8")
    if t.count(old) != 1:
        raise SystemExit(f"{f}: anchor found {t.count(old)} times: {old[:80]}")
    p.write_text(t.replace(old, new), encoding="utf-8")


def cut(f, start, end):
    p = Path(f)
    t = p.read_text(encoding="utf-8")
    a = t.index(start)
    b = t.index(end, a) + len(end)
    p.write_text(t[:a] + t[b:], encoding="utf-8")
    return t[a:b]


def for_supp(block):
    block = re.sub(r"\\ref\{(sec|eq):", r"\\Mref{\1:", block)
    return block.replace("\\suppTabDesign{}", "Table~\\ref{tab:design}").replace("\\begin{figure}[t]", "\\begin{figure}[h]") \
        .replace("\\begin{table}[t]", "\\begin{table}[h]")


# 1. formalism figure
fig = cut("sections/03-notation.tex", "\\begin{figure}[t]\n\\centering\n\\includegraphics[width=\\linewidth]{figures/fig02-formalism.pdf}", "\\end{figure}\n")
edit("sections/03-notation.tex", "a final rounding commits all $L$ positions at once; in the notation this is a last step with $k=L$.",
     "a final rounding commits all $L$ positions at once; in the notation this is a last step with $k=L$. "
     r"\suppFigFormalism{} in the supplement draws the process: training fixes C1 and C2 and fits C3, and each sampling step passes the state through the network (C3), the position and value laws (C4), a commit and an optional revision (C5).")

# 2. lever table
tab = cut("sections/07-error-budget.tex", "\\begin{table}[t]\n\\caption{Lever table.", "\\end{table}\n")
edit("sections/07-error-budget.tex", "Table~\\ref{tab:levers} places each method by the term it acts on and what it pays,",
     r"\suppTabLevers{} in the supplement places each method by the term it acts on and what it pays. In brief, fewer tokens per step, position order, joint draws inside a set, block-wise generation and modality-ordered schedules act on the factorisation term and pay in forward passes, planning or parallelism; training choices, self-conditioning and distillation act on the learning term and pay in training compute; token-level and output-level revision repair realised errors at the cost of extra passes or generations; value rules act on $V$ and pay in diversity, extra passes or extra samples; and compute reuse saves wall-clock time, exactly or at the cost of an approximation error. The table lists the methods")

s = Path("supplement.tex")
st = s.read_text(encoding="utf-8")
a1 = "\\subsection{The commit-kernel sampler (from Section~\\Mref{sec:notation-alg})}"
a2 = "\\subsection{Memory in the error budget (from Section~\\Mref{sec:budget-other})}"
assert st.count(a1) == 1 and st.count(a2) == 1
st = st.replace(a1, r"\subsection{The commitment process at a glance (from Section~\Mref{sec:notation})}" + "\n\\label{sec:s-formalism}\n\n" + for_supp(fig) + "\n" + a1)
st = st.replace(a2, r"\subsection{The lever table (from Section~\Mref{sec:budget-levers})}" + "\n\\label{sec:s-levers}\n\n" + for_supp(tab) + "\n" + a2)
st = st.replace("\\Mref{tab:levers}", "\\ref{tab:levers}")
s.write_text(st, encoding="utf-8")

# 3. supprefs: figure macro and lever-table macro
p = Path("scripts/supprefs.py")
t = p.read_text(encoding="utf-8")
if "suppTabLevers" not in t:
    t = t.replace('"suppTabExp": "tab:exp003-arms"}', '"suppTabExp": "tab:exp003-arms", "suppTabLevers": "tab:levers",\n       "suppFigFormalism": "fig:formalism"}')
    t = t.replace(r'num = dict(re.findall(r"\\newlabel\{(tab:[^}]*)\}\{\{(S\d+)\}", aux))',
                  r'num = dict(re.findall(r"\\newlabel\{((?:tab|fig):[^}]*)\}\{\{(S\d+)\}", aux))')
    t = t.replace('lines.append(f"\\\\newcommand{{\\\\{cmd}}}{{Table~{num[lab]}}}")',
                  'lines.append(f"\\\\newcommand{{\\\\{cmd}}}{{{\'Figure\' if lab.startswith(\'fig:\') else \'Table\'}~{num[lab]}}}")')
    assert "suppFigFormalism" in t and "(?:tab|fig)" in t and "'Figure'" in t, "supprefs patch failed"
    p.write_text(t, encoding="utf-8")
# placeholders so main compiles before supprefs.py runs again
sp = Path("supprefs.tex")
st = sp.read_text(encoding="utf-8")
for c, txt in (("suppTabLevers", "Table~S?"), ("suppFigFormalism", "Figure~S?")):
    if c not in st:
        st += f"\\newcommand{{\\{c}}}{{{txt}}}\n"
sp.write_text(st, encoding="utf-8")
print("ok", len(fig.split()), len(tab.split()))
