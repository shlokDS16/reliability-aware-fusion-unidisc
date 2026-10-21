"""Revision 2026-10-21 (assessment: Section 2 reads like an audit report; page limit): move the search,
filter and extraction-procedure detail of Section 2 to the supplement, leaving short summaries.
Numbers in the summaries are copied from the moved text. Run from paper/review."""
from pathlib import Path

M = Path("sections/02-method.tex")
S = Path("supplement.tex")
t = M.read_text(encoding="utf-8")


def cut(start, end):
    global t
    a = t.index(start)
    b = t.index(end, a)
    block = t[a:b]
    return a, b, block


SRC_SUM = (r"The search ran in three strands (Table~\ref{tab:sources}; Figure~\ref{fig:prisma}). The \emph{seed corpus} joined a curated list of diffusion language model papers with two logged arXiv searches of 2026-10-14. "
           r"The \emph{search update} of 2026-10-15 ran revised strings on five free sources and snowballed citations from the seed; the strings were revised after the protocol's recall pilot failed, and the final strings kept seed recall at 525 of 540. "
           r"The \emph{subscription strand} searched six databases on 2026-10-15 and 2026-10-16 through institutional access. Every query, date and hit count is logged; the strings, the recall checks and the export limits are in the Supplement (Section~S1)." + "\n\n")
a, b, src_block = cut("The search ran in three strands", "\\begin{table}[t]\n\\caption{Sources searched")
t = t[:a] + SRC_SUM + t[b:]

DED_SUM = (r"\paragraph{Deduplication and automation filters.} Records were merged on shared identifiers and normalised titles, leaving 1,453 seed records, 19,328 new update records and 4,380 new subscription records. "
           r"The final strings were then applied locally and excluded 17,486 update and 4,201 subscription records by automation; a validation of that filter crossed its preset reversal threshold, so a single-screener rescue pass read every filtered record with an abstract (Supplement, Section~S1)." + "\n\n")
a, b, ded_block = cut("\\paragraph{Deduplication and automation filters.}", "\\subsection{Eligibility}")
t = t[:a] + DED_SUM + t[b:]

EXT_SUM = (r"\paragraph{Stratified sample (RQ2 to RQ6).} Evidence for RQ2 to RQ5 and the quality appraisal (RQ6) come from a stratified random sample of 80 studies (decisions D0051, D0052, D0054). "
           r"Three strata cover the included studies: unified multimodal studies, and language-only studies split at the median text length into shorter and longer ones (52, 267 and 265 studies after later field resolutions; 59 sampled). "
           r"A fourth stratum of 20 seed-corpus studies, drawn from those the census found eligible, is reported apart, as is the landmark tranche (decisions D0060, D0063). "
           r"Shares are weighted to the stratum sizes, with 95\% bootstrap intervals; the estimator was chosen after extraction. "
           r"The form (153 fields) records each paper's own comparisons as matched groups with their arms, metric, direction and budget, and nine appraisal items, QA1 to QA9: code, weights or data, evaluation protocol, run-to-run variation, uncertainty for the main comparison, baselines at matched or reported budget, an ablation of the credited component, claims that agree with the paper's own tables, and stated limitations. "
           r"One automated extractor read each study and cited a page for every value; a validator checked every value against the text; a second extractor read 8 studies, and an adjudicator settled their differences from the full text. "
           r"The two extractors agree on the values (616 of 616) and metric directions (75 of 76) of the contrast units both found and on most appraisal scores and study-level flags, but on only 5 of 8 direction flags, and they cut the same tables into comparison groups very differently (36 of 245 groups found by both, F1 0.29). Section~\ref{sec:rq} therefore draws no unit totals and makes its statements about studies. "
           r"Twenty-seven records kept an entry the validator rejected; Supplement~S6 repeats the estimates without them. The full procedure is in the Supplement (Section~S4)." + "\n\n")
a, b, ext_block = cut("\\paragraph{Stratified sample (RQ2 to RQ6).}", "\\paragraph{Synthesis.}")
t = t[:a] + EXT_SUM + t[b:]
M.write_text(t, encoding="utf-8")


def to_supp(block):
    block = block.replace("\\ref{", "\\Mref{")
    block = block.replace("research/AUTHOR-CHECKS-2026-10-21.md in the repository; ", "")
    return block.strip()


s = S.read_text(encoding="utf-8")
anchor = "\\subsection{Every logged search}"
assert s.count(anchor) == 1
s = s.replace(anchor, r"\subsection{Searches and automation filters in full (from Section~\Mref{sec:method-sources})}" + "\n\\label{sec:s-sources}\n\n"
              + to_supp(src_block) + "\n\n" + to_supp(ded_block) + "\n\n" + anchor)
anchor = "\\section{The design-space table of the 47 models}"
assert s.count(anchor) == 1
s = s.replace(anchor, r"\subsection{Extraction procedure in full (from Section~\Mref{sec:method-extraction})}" + "\n\\label{sec:s-extraction}\n\n"
              + to_supp(ext_block).replace("\\paragraph{Stratified sample (RQ2 to RQ6).}", "").strip() + "\n\n" + anchor)
S.write_text(s, encoding="utf-8")
print("moved words:", len(src_block.split()) + len(ded_block.split()) + len(ext_block.split()))
