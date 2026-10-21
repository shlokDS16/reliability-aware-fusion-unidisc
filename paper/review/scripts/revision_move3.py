"""Revision 2026-10-21 (author's request, page limit): Section EXP-003 becomes a short subsection of the open
problems (full text already in Supplement S7); the step-sweep corollary and the census-lever paragraph of
Section 7 move to Supplement S8. Numbers in the summaries are copied from the moved text. Run from paper/review."""
from pathlib import Path


def edit(f, old, new):
    p = Path(f)
    t = p.read_text(encoding="utf-8")
    if t.count(old) != 1:
        raise SystemExit(f"{f}: anchor found {t.count(old)} times: {old[:80]}")
    p.write_text(t.replace(old, new), encoding="utf-8")


# 1. EXP-003: drop the section, add a short subsection before OP4 carrying the label sec:exp003
edit("main.tex", "\\input{sections/09-exp003}\n", "")
EXP = (r"\subsection{A preregistered check on one frozen unified model}" "\n\\label{sec:exp003}\n\n"
       r"One preregistered run checks, at matched network calls on the released UniDisc 1.4B weights~\cite{arXiv:2503.20853}, what earlier work reports for unified masked-diffusion models~\cite{arXiv:2607.13188,arXiv:2511.09611}: that the sampler changes joint text--image agreement. "
       r"On 138 prefixes from COCO val2017 captions with two seeds each, a 32-step variant of the official guided sampler (guidance weight 3.0) gives a larger seed-specific, noun-level dependence between a generated caption tail and its image than plain sampling at the same 64 network calls ($\Delta_1=0.126$, 95\% interval 0.076 to 0.177, on the 123 prefixes eligible in both arms). "
       r"The dependence is measured by a vision-language checker and is not confirmed by CLIP; the checker's positive control failed, so no null can be read, and the positive term bundles selection with ordering and schedule. "
       r"The run therefore shows only that, on this model, a joint-consistency number reported without its sampler is not attributable to the model, which is how the census is read (Section~\ref{sec:census-reading}). It is not a contribution of the review; the arms, statistic, controls, deviations and secondary results are in the Supplement (Section~S7)."
       "\n\n")
edit("sections/08-open-problems.tex", "\\subsection{OP4. A four-arm value-rule measurement on one checkpoint}",
     EXP + "\\subsection{OP4. A four-arm value-rule measurement on one checkpoint}")
edit("sections/01-introduction.tex",
     r"Section~\ref{sec:budget} the error budget, Section~\ref{sec:open} the open problems, Section~\ref{sec:exp003} a preregistered measurement on a frozen unified model, and",
     r"Section~\ref{sec:budget} the error budget, Section~\ref{sec:practice} what the evidence means for practice, Section~\ref{sec:open} the open problems with a preregistered check on a frozen unified model (Section~\ref{sec:exp003}), and")

# 2. Section 7 corollaries: keep heading and label, summary in place, detail to the supplement
p = Path("sections/07-error-budget.tex")
t = p.read_text(encoding="utf-8")
a = t.index("\\label{sec:budget-props}\n") + len("\\label{sec:budget-props}\n")
moved = t[a:].strip()
SUM = (r"A step sweep identifies less than it seems. At one token per step the gain of a position rule over its base is the difference of their learning terms; at more tokens per step the visited states change, so the gain mixes a change in the factorisation term with a change in the learning term, and a sweep identifies the one-token point only without a rerun that fixes the visited states. "
       r"The derivation, a toy enumeration, the second corollary on revision gains, the withdrawn statements and what the census says about each lever are in the Supplement (Section~S8)." "\n")
p.write_text(t[:a] + "\n" + SUM, encoding="utf-8")

s = Path("supplement.tex")
st = s.read_text(encoding="utf-8")
anchor = "\\subsection{Where a revision gain comes from, and withdrawn statements (from"
assert st.count(anchor) == 1
moved_s = (moved.replace("The second corollary, on where a revision sampler's gain comes from, and two withdrawn statements are in the supplement (Section~S8.8).",
                         "The second corollary, on where a revision sampler's gain comes from, and two withdrawn statements follow in the next subsection.")
           .replace("Equation~\\eqref{eq:identity}", "Equation~(\\Mref{eq:identity})")
           .replace("Table~\\ref{tab:levers}", "Table~\\Mref{tab:levers}")
           .replace("\\ref{", "\\Mref{"))
st = st.replace(anchor, r"\subsection{What a step sweep identifies, and the census against the levers (from Section~\Mref{sec:budget-props})}"
                + "\n\\label{sec:s-budget-props}\n\n" + moved_s + "\n\n" + anchor)
s.write_text(st, encoding="utf-8")
print("ok; moved corollary words", len(moved.split()))
