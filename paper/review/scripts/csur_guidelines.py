"""CSUR author guidelines (read 2026-10-21 at dl.acm.org/journal/csur/author-guidelines): abstract at most 100 words,
short direct sentences, no first person, no mathematics, no citations, not starting "This paper". Plus closing
"In summary" paragraphs in the style of Yang et al. (CSUR 56(4)). Numbers repeat the body. Run from paper/review."""
from pathlib import Path

t = Path("main.tex").read_text(encoding="utf-8")
a = t.index("\\begin{abstract}")
b = t.index("\\end{abstract}")
keep = "\n".join(l for l in t[a:b].split("\n") if l.startswith("%") or l.startswith("\\begin"))
ABS = ("Diffusion language models generate text by refining many positions in parallel, and unified variants extend "
       "this to images. A PRISMA 2020 systematic review of 615 studies, with a stratified sample of 59 extracted in full, "
       "organises the field around five design choices, tested on 47 models. A census finds that 147 of 153 sampled papers "
       "report headline results with a non-plain or unstated decoding rule. Only 1 of 25 sampled studies comparing "
       "diffusion with autoregressive models matches compute, and repeated runs support the main comparison in 10 of 54. "
       "A decision framework, a reporting checklist and open problems follow.")
assert len(ABS.split()) <= 100, len(ABS.split())
Path("main.tex").write_text(t[:a] + keep + "\n" + ABS + "\n" + t[b:], encoding="utf-8")

SUM = {
    "sections/03-notation.tex": r"In summary, every generator in scope is described by five choices: the corruption channel (C1), the reveal law and objective (C2), the predictor (C3), the commitment policy (C4) and the revision rule (C5). The commit kernel separates which positions are committed at a step from how their values are chosen, which is the distinction the rest of the review relies on.",
    "sections/04-design-space.tex": r"In summary, the five choices place all 47 models: 36 fit fully and 11 fit with a stated extension. The partial fits mark the limits of the notation, namely edit channels that change length, predictors that output a joint distribution over a set, continuous image channels without a committed set, and sequence-level selection.",
    "sections/06-census.tex": r"In summary, the decoding rule behind a headline result is rarely plain and often unstated (147 of 153 papers), in every year and venue class sampled. A number reported without its decoding rule cannot be compared with one from another paper, which is why the reporting checklist of Section~\ref{sec:practice} puts the rule first.",
    "sections/07-error-budget.tex": r"In summary, the error budget assigns each method to the term it changes: fewer tokens per step, position order and joint draws act on the factorisation term, training choices on the learning term, and decoding rules on the value term $V$. The budget classifies methods; it does not measure how large each term is on a real model.",
}
for f, s in SUM.items():
    p = Path(f)
    x = p.read_text(encoding="utf-8").rstrip("\n")
    if s[:40] not in x:
        p.write_text(x + "\n\n" + s + "\n", encoding="utf-8")
print("abstract words:", len(ABS.split()))
