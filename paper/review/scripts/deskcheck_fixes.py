"""Fixes from the desk check of 2026-10-21 (research/review/audits/2026-10-21-desk-check.md). Run from paper/review.
Numbers: 79,963 = 1,903 + 66,891 + 11,169 (the table rows); the strata note repeats the earlier Section 2 text."""
import re
from pathlib import Path


def rd(f):
    return Path(f).read_text(encoding="utf-8")


def wr(f, t):
    Path(f).write_text(t, encoding="utf-8")


def edit(f, old, new, count=1):
    t = rd(f)
    if t.count(old) != count:
        raise SystemExit(f"{f}: anchor found {t.count(old)} times: {old[:90]}")
    wr(f, t.replace(old, new))


I, M, D, R, C, B, P, O, L = ("sections/01-introduction.tex", "sections/02-method.tex", "sections/04-design-space.tex",
                             "sections/05-rq-evidence.tex", "sections/06-census.tex", "sections/07-error-budget.tex",
                             "sections/075-practice.tex", "sections/08-open-problems.tex", "sections/10-limitations.tex")

# arithmetic: total identified
for f in ("main.tex", I):
    edit(f, "79,964 identified records", "79,963 identified records")
edit(M, "Total identified & & 79,964 \\\\", "Total identified & & 79,963 \\\\")

# introduction: duplicate paragraph, process text, contribution labels, page claim, scope sentence
t = rd(I)
t = "\n".join(l for l in t.split("\n") if not l.startswith("A diffusion language model (DLM) produces text by repeatedly predicting"))
wr(I, t)
t = rd(I)
a = t.index("An earlier feasibility pass over a different sample of papers")
b = t.index("quantitative statements are counts with intervals.") + len("quantitative statements are counts with intervals.")
t = t[:a] + "Too few comparisons in the literature share a task, a metric and a compute budget for a meta-analysis, so the review reports counts and weighted shares with intervals rather than a pooled estimate." + t[b:]
for n, title in ((1, "A design space in one notation, tested on 47 models."), (2, "A census of value rules and reporting."),
                 (3, "The error budget as a taxonomy."), (4, "Open problems with the evidence each needs.")):
    t = t.replace(f"\\paragraph{{C{n}. {title}}}", f"\\paragraph{{{title}}}")
t = t.replace("The test is weaker than it sounds:", "The test is less demanding than the count suggests:")
t = t.replace("We do not claim a selection error or tilt cost as new error terms; both were derived, attacked and withdrawn.",
              "The notation, the census and the error budget serve the survey: they organise and evaluate the published work rather than propose new methods. We do not claim a selection error or a tilt cost as new error terms; we examined both and set them aside.")
t = t.replace("the main text runs to 32 pages, followed by the references.", "the main text runs to 30 pages, followed by the references.")
wr(I, t)

# abstract: contributions consistent with Section 1
t = rd("main.tex")
a = t.index("\\begin{abstract}")
b = t.index("\\end{abstract}")
keep = "\n".join(l for l in t[a:b].split("\n") if l.startswith("%") or l.startswith("\\begin"))
ABS = (r"This article presents a systematic review of diffusion language models and unified multimodal diffusion models, conducted under PRISMA 2020. "
       r"From 79,963 identified records, 615 studies were included, and a stratified random sample of 59 of them was extracted in full and appraised for quality. "
       r"The review makes four contributions. It describes every generator by five design choices and tests this design space on 47 models, of which 36 fit fully and 11 partly. "
       r"A census of a random sample of papers finds that 147 of 153 report their headline result with a non-plain or unstated decoding rule. "
       r"It separates sampling error into factorisation, learning and decoding-rule terms, and it states open problems with the measurements that would settle them. "
       r"Across six research questions, comparisons with autoregressive models are split and only one of 25 is compute-matched, training gains are rarely isolated, more inference compute helps most curves in 9 of 15 sweeping studies, and synergy ablations are split. "
       r"A decision framework, decoding defaults and a reporting checklist translate these findings for practitioners.")
wr("main.tex", t[:a] + keep + "\n" + ABS + "\n" + t[b:])
edit("main.tex", "decision ledger,", "record of methodological decisions,")

# method: criterion labels and strata explanation
edit(M, "whose output includes natural-language text or code, or (b) a unified model",
     "whose output includes natural-language text or code (criterion I1(a)), or (b) a unified model")
edit(M, "with a diffusion, masked-generative or discrete-flow component.\n",
     "with a diffusion, masked-generative or discrete-flow component (criterion I1(b)).\n")
edit(M, "(52, 267 and 265 studies; 59 sampled).",
     "(52, 267 and 265 studies, 59 of them sampled). The 12 included studies whose output is not language, the 7 included on reassessment and 12 records reserved for a pilot of the extraction form fall outside the strata.")

# design space
edit(D, "Twenty-nine rows (M01 to M29) were copied", "The first 29 rows were copied")
edit(D, "29 rows were copied from earlier readings by one model reader,", "29 rows were transferred from earlier readings by a single reader,")
edit(D, "Figure~S1 in the supplement (Section~S5.1) shows the same models.", "\\suppFigDots{} in the supplement (Section~S5.1) shows the same models.")
edit(D, "they are listed in the supplement (Section~S8.2).", "they are listed in the supplement (Section~S8.3).")
edit(D, "are in the supplement (Section~S5.3).", "are in the supplement (Section~S5.4).")
edit("sections/03-notation.tex", "is Algorithm~S1 in the supplement (Section~S8.1).", "is Algorithm~S1 in the supplement (Section~S8.2).")
edit("sections/03-notation.tex", " (the last two are inference in the primer).", ".")

# evidence section
edit(R, "The control behind these contrasts is thin.", "Few of these contrasts are well controlled.")
edit(R, "the 27 records the validator still rejected are left out", "the 27 records with an entry that failed the check against the text are left out")

# census
edit(C, "(Section~S3.3, \\suppTabGap{})", "(Section~S3.5, \\suppTabGap{})")
edit(C, "is in the supplement (Section~S3.4).", "is in the supplement (Section~S3.7).")
edit(C, "no human coded the sample (a later blind author check", "the sample was coded by the review's two coders (a later blind check by the first author")
edit(C, "(X1 for 4 and X0 for 1)", "(four because their diffusion is over non-text data and one without a diffusion component)")
edit(C, "compounded by coder~B's read failures.", "compounded by papers that coder~B could not access.")
t = rd(C)
t = t.replace("(Section~\\ref{sec:budget}, withdrawn proposition P2)", "(Section~\\ref{sec:budget})")
wr(C, t)

# error budget
edit(B, "(Section~S8.6).", "(Section~S8.8).")
edit(B, "(Section~S8.7).", "(Section~S8.9).")
edit(B, "\\paragraph{What was withdrawn.} An earlier version of our framework proposed two new terms,", "\\paragraph{Terms considered and set aside.} We also considered two further terms,")
edit(B, "Both are withdrawn and not claimed. The reasons are in the supplement (Section~S8.4),", "Neither is claimed. The reasons are in the supplement (Section~S8.6),")
t = rd(B)
t = t.replace("\\subsection{Two corollaries, one withdrawn proposition, and what the census says}", "\\subsection{What a step sweep identifies}")
wr(B, t)

# practice tables
edit(P, "sample: RQ5 unresolved; one preregistered run", "sample: RQ5 mixed; one preregistered run")
edit(P, "Understanding and generation help each other in unified models & RQ5 unresolved \\\\",
     "Understanding and generation help each other in unified models & RQ5 mixed, five signed studies \\\\")
t = rd(P)
row = "On one frozen unified model, the official guided sampler raises the text--image link at matched network calls & one preregistered run (Section~\\ref{sec:exp003}) \\\\\n"
assert t.count(row) == 1
t = t.replace(row, "")
t = t.replace("\\multicolumn{2}{@{}l}{\\emph{Supported by single studies outside the sample}} \\\\\n",
              "\\multicolumn{2}{@{}l}{\\emph{Supported by single studies}} \\\\\n"
              "On one frozen unified model, a guided sampler gave a larger text--image dependence than plain sampling at matched network calls (not confirmed by CLIP) & our preregistered run (Section~\\ref{sec:exp003}) \\\\\n")
wr(P, t)

# open problems: evidence levels without internal wording
edit(O, "The levels are those of our evidence records: E0 is a derived expectation or a model suggestion, E1 an abstract or a summary read, E2 a paper read in full or at the sections named, E3 released code inspected at a stated commit, E4 reproduced here.",
     "Evidence levels run from E0 (a derived expectation) and E1 (an abstract or a summary read) to E2 (a paper read in full or at the sections named), E3 (released code inspected at a stated commit) and E4 (reproduced here).")
edit(O, "gives the map and the subsections the detail.", "gives the map and the Supplement the detail.")

# limitations
edit(L, "Extraction was read twice for 8 of the 80 sampled studies.", "Extraction was read twice for 8 of the sampled studies.")
edit(L, "A validation by human readers alone would apply the protocol's own standard:", "A further validation would apply the protocol's own standard:")

# supplement
S = "supplement.tex"
t = rd(S)
for o, n in [("two model screeners and a model adjudicator;", "two screeners and an adjudicator;"),
             ("by the first author, is in Section~S9.", "by the first author, is in Section~S11."),
             ("($\\kappa=0.79$; Section~S9)", "($\\kappa=0.79$; Section~S11)"),
             ("whose session had ended;", "whose assessment had closed;"),
             ("The search ran in three strands (Table~\\Mref{tab:sources}; Figure~\\Mref{fig:prisma}).",
              "The search ran in three strands (Table~\\Mref{tab:sources}). Figure~\\Mref{fig:prisma} shows the flow.")]:
    t = t.replace(o, n)
wr(S, t)

# supprefs: macro for the dot-matrix figure of the supplement
p = Path("scripts/supprefs.py")
s = p.read_text(encoding="utf-8")
if "suppFigDots" not in s:
    s = s.replace('"suppFigFormalism": "fig:formalism"}', '"suppFigFormalism": "fig:formalism", "suppFigDots": "fig:taxonomy"}')
    assert "suppFigDots" in s
    p.write_text(s, encoding="utf-8")
sp = Path("supprefs.tex")
st = sp.read_text(encoding="utf-8")
if "suppFigDots" not in st:
    sp.write_text(st + "\\newcommand{\\suppFigDots}{Figure~S?}\n", encoding="utf-8")

# PRISMA figure labels
f = Path("scripts/fig01_prisma.py")
s = f.read_text(encoding="utf-8")
for o, n in [('("Rescue screen of filtered", B)', '("Check of set-aside", B)'),
             ('e-gateway "', 'institutional access "'),
             ('f"triggered: {f(rc[\'frame\'])} candidates,"', 'f"flagged: {f(rc[\'frame\'])} records,"'),
             ('("exclusions: K = "', '("exclusions: eligible "'),
             ('"extraction and appraisal on a stratified random sample of 80, with a seed stratum"',
              '"extraction and appraisal: stratified random sample of 59 included and 20 seed-corpus studies"')]:
    if o not in s:
        print("figure label not found:", o)
    s = s.replace(o, n)
f.write_text(s, encoding="utf-8")
print("ok")
