"""Page limit (CSUR: 35 pages including references; target about 34): the detailed open problems OP1-OP5 and the
landmark-column paragraphs of Section 5 move to the supplement, with summaries in place. Run from paper/review."""
import re
from pathlib import Path


def rd(f):
    return Path(f).read_text(encoding="utf-8")


def wr(f, t):
    Path(f).write_text(t, encoding="utf-8")


def to_supp(b):
    b = re.sub(r"\\(ref|eqref)\{(sec|eq|tab|fig):", lambda m: ("\\Mref{" if m.group(1) == "ref" else "(\\Mref{") + m.group(2) + ":", b)
    return b.replace("(\\Mref{eq:", "(\\Mref{eq:")


O = "sections/08-open-problems.tex"
t = rd(O)
a = t.index("\\subsection{OP1.")
e0 = t.index("\\subsection{A preregistered check on one frozen unified model}")
e1 = t.index("\\subsection{OP4.")
tail_marker = "Reporting, the most immediate of these needs"
e2 = t.index(tail_marker)
op123 = t[a:e0]
exp = t[e0:e1]
op45 = t[e1:e2]
closing = t[e2:]
BRIEF = r"""\subsection{The problems in brief}
\label{sec:open-op1}\label{sec:open-op2}\label{sec:open-op3}\label{sec:open-op4}\label{sec:open-v}
OP1 asks what a step sweep identifies: at one token per step the gain of a position rule over its base is a difference of learning terms, but at more tokens per step it also moves the factorisation term. OP2 asks whether a revision sampler's gain over its base survives when the value rule is matched on both arms. OP3 asks whether a unified model's own cross-modal dependence is concentrated in early steps, and whether schedules that avoid committing dependent text and image positions together score better at matched cost. OP4 is a four-arm measurement on one frozen checkpoint that separates sample-then-filter from its resampled and tilted twins, for which a preregistrable design is given. OP5 brackets the effect of the value term on one model by comparing plain sampling, rank-then-sample, sample-then-filter and best-of-$N$ at matched network calls and matched entropy. The Supplement sets out each problem in full, with the evidence now, the measurement that would settle it and what would refute it.

"""
wr(O, t[:a] + BRIEF + exp + closing)

L = re.compile(r"\n(In the landmark column[^\n]*|The landmark column is graded[^\n]*|Four of the 16 extracted landmark studies[^\n]*)")
R = "sections/05-rq-evidence.tex"
r = rd(R)
moved = [m.group(1).strip() for m in L.finditer(r)]
r = L.sub("", r)
r = r.replace("A third column gives the landmark tranche: the first 16 of its 42 included studies in a seeded random order; it describes those well-known papers and enters no included-study estimate.",
              "A third column, for 16 of the 42 landmark studies, describes those well-known papers and enters no included-study estimate; its results by question are in the Supplement (Section~S6).")
wr(R, r)

S = "supplement.tex"
s = rd(S)
anchor = "\\section{Author checks of screening, extraction and census}"
assert s.count(anchor) == 1
block = (r"\section{Open problems in full (from Section~\Mref{sec:open})}" + "\n\\label{sec:s-open}\n\n"
         + to_supp(op123 + op45).replace("\\subsection{", "\\subsection{").replace("\\label{sec:open-", "\\label{sec:s-open-")
         + "\n\\section{The landmark column by research question (from Section~\\Mref{sec:rq})}\n\\label{sec:s-landmark-rq}\n\n"
         + "\n\n".join(to_supp(x) for x in moved) + "\n\n")
s = s.replace(anchor, block + anchor)
wr(S, s)
print("moved landmark paragraphs:", len(moved), "| open-problem words:", len((op123 + op45).split()))
