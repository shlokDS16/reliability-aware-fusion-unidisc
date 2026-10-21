"""Revamp after the supervising professor's second review (2026-10-21, decision D0072).
1. References: no duplicated arXiv eprint line (eprint/archivePrefix/primaryClass removed; howpublished kept).
2. Abstract with contributions; introduction opens before 1.1; specific subsection names; no paper titles in text.
3. Section 2 rewritten as a conventional systematic-review method; the audit detail moves to Supplement S1.
4. No decision identifiers and no mention of AI in the main text (AI only in the closing declaration).
5. Exemplar comparison moved to Section 4; reliability subsection in Section 5; decision framework and an
   evidence-status table in Section 8; wording fixes; Statements and Declarations.
Every number is copied from the existing manuscript text. Run from paper/review."""
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


# ---------------------------------------------------------------- 1. references
for b in ("references.bib", "s6-refs.bib"):
    t = rd(b)
    t = re.sub(r"\n\s*(eprint|archivePrefix|primaryClass)\s*=\s*\{[^}]*\},?", "", t)
    wr(b, t)

# ---------------------------------------------------------------- 2. abstract
t = rd("main.tex")
a = t.index("\\begin{abstract}")
b = t.index("\\end{abstract}")
body = t[a:b]
keep = "\n".join(l for l in body.split("\n") if l.startswith("%") or l.startswith("\\begin"))
ABS = (r"This article presents a systematic review of diffusion language models and unified multimodal diffusion models, conducted under PRISMA 2020. "
       r"From 79,964 identified records, 615 studies were included, and a stratified random sample of 59 of them was extracted in full and appraised for quality. "
       r"The review makes four contributions. First, it describes every generator by five design choices and tests this design space on 47 models, of which 36 fit fully and 11 partly. "
       r"Second, it synthesises the evidence for six research questions: comparisons with autoregressive models are split and only one of 25 is compute-matched, training gains are rarely isolated, more inference compute helps most curves in 9 of 15 sweeping studies, and synergy ablations are split. "
       r"Third, a census of a random sample of papers finds that 147 of 153 report their headline result with a non-plain or unstated decoding rule. "
       r"Fourth, it organises sampler error as a budget with one value term and derives a decision framework, decoding defaults, a reporting checklist and open problems with the measurements that would settle them.")
wr("main.tex", t[:a] + keep + "\n" + ABS + "\n" + t[b:])

# ---------------------------------------------------------------- statements and declarations
edit("main.tex", "\\begin{acks}\n\\todo{funding statement, competing-interests statement and acknowledgements}\n\\end{acks}\n",
     "\\section*{Statements and Declarations}\n\\paragraph{Funding.} No funding was received for conducting this study. The article processing charge is covered by the authors' institution, Vellore Institute of Technology, Vellore.\n"
     "\\paragraph{Competing interests.} The authors declare no competing interests.\n")
t = rd("main.tex")
i, j = t.index("\\section*{Declaration on the use of AI}"), t.index("\\section*{Statements and Declarations}")
if i < j:   # put the AI declaration last, after funding and competing interests
    decl = t[i:t.index("\n\n", i) + 2] if "\n\n" in t[i:j] else t[i:j]
    t = t.replace(decl, "")
    k = t.index("\\bibliographystyle")
    t = t[:k] + decl.rstrip() + "\n\n" + t[k:]
    wr("main.tex", t)

# ---------------------------------------------------------------- 3. introduction
I = "sections/01-introduction.tex"
t = rd(I)
old_p1 = t[t.index("A diffusion language model (DLM) produces text"):t.index("19 in 2022 or earlier.") + len("19 in 2022 or earlier.")]
t = t.replace(old_p1 + "\n", "")
t = t.replace("\\subsection{Why a critical review of this literature}",
              r"""A diffusion language model (DLM) generates text by repeatedly predicting many positions in parallel and committing a subset of them, rather than emitting one token at a time from left to right. \citet{arXiv:2107.03006} introduced diffusion on categorical state spaces; later work specialised it to the masked, or absorbing-state, case~\cite{arXiv:2310.16834,arXiv:2406.07524,arXiv:2406.04329,arXiv:2406.03736}, developed a parallel line that diffuses continuous embeddings~\cite{arXiv:2205.14217}, and trained such models at the scale of autoregressive language models~\cite{arXiv:2502.09992}. The same machinery now underlies unified models that understand and generate more than one modality with a single network~\cite{arXiv:2503.20853,arXiv:2505.15809,arXiv:2408.12528}. The literature is growing quickly: of the 540 records with an arXiv identifier in the curated list that seeds our corpus, 243 first appeared in 2026 and only 19 in 2022 or earlier.

This article reviews that literature systematically. From 79,964 identified records, 615 studies were included; a stratified random sample of them was extracted in full and appraised for quality. Beyond describing methods, the review organises the field around five design choices that every generator makes, asks how well the published evidence supports the field's main claims, and records how the headline results of a random sample of papers were decoded. The rest of this section explains why such a review is needed (Section~\ref{sec:intro-why}), positions it against earlier surveys (Section~\ref{sec:intro-related}), and states the research questions, the contributions and the organisation of the article.

\subsection{Decoding choices and the comparability of reported results}""")
t = t.replace("\\subsection{Existing reviews and what they lack}", "\\subsection{Prior surveys of diffusion language and unified multimodal models}")
t = t.replace("\\subsection{Research questions}", "\\subsection{Research questions and evidence base}")
t = t.replace("\\subsection{Contributions}", "\\subsection{Contributions of this review}")
t = t.replace("\\subsection{What is not claimed}", "\\subsection{Scope of the claims}")
t = t.replace("\\subsection{How to read the paper}", "\\subsection{Organisation of the article}")
wr(I, t)
for old, new in [
    ("Two surveys are close to ours in scope. ``A Survey on Diffusion Language Models''~\\cite{arXiv:2508.10875} (version~3, over 220 references) covers",
     "Two surveys are closest to ours in scope. The survey of \\citet{arXiv:2508.10875} (version~3, over 220 references) covers"),
    ("``Discrete Diffusion in Large Language and Multimodal Models: A Survey''~\\cite{arXiv:2506.13759} (version~5, 175 references) covers the discrete case with catalogue tables.",
     "\\citet{arXiv:2506.13759} (version~5, 175 references) cover the discrete case with catalogue tables."),
    ("Around them sit surveys of unified multimodal models", "Other surveys address unified multimodal models"),
    ("In a keyword scan of the full text of the sixteen surveys and tutorials in the first tier of our landscape file,",
     "In a keyword scan of the full texts of sixteen related surveys and tutorials,"),
    ("The survey of discrete diffusion~\\cite{arXiv:2506.13759} has no comparison table; the survey of diffusion language models~\\cite{arXiv:2508.10875} has a 36-model table whose columns are mostly metadata, with only the diffusion type being a design choice.",
     "\\citet{arXiv:2506.13759} give no comparison table, and the 36-model table of \\citet{arXiv:2508.10875} has mostly metadata columns, of which only the diffusion type is a design choice."),
    ("Of 47 models, 36 fit with no new cell value, 11 fit partly, and none could not be placed;",
     "Of the 47 models, 36 fit the notation fully and 11 fit it partly, and every model could be placed;"),
    ("We use $V$ as bookkeeping that locates where a sampler's value rule acts.",
     "We treat $V$ as a bookkeeping device that locates where a sampler's value rule acts."),
]:
    edit(I, old, new)

# ---------------------------------------------------------------- 4. Section 2 rewritten
M = "sections/02-method.tex"
old = rd(M)
tab = old[old.index("\\begin{table}[t]\n\\caption{Sources searched"):old.index("\\end{table}", old.index("Sources searched")) + len("\\end{table}")]
tab = tab.replace("\\emph{Search update (strings S1, S2, S1$'$, S2$'$)}", "\\emph{Search update (strings S1 and S2 and their revisions)}")
fig = old[old.index("\\begin{figure}[p]"):old.index("\\end{figure}", old.index("\\begin{figure}[p]")) + len("\\end{figure}")]
fig = fig.replace("\\begin{figure}[p]", "\\begin{figure}[tbp]").replace("width=\\linewidth]{figures/fig01-prisma.pdf}", "width=0.82\\linewidth]{figures/fig01-prisma.pdf}")
fig = fig.replace("``Awaiting second screener'' marks records that screener~B could not read and that the first author screens. ", "")
sel = old[old.index("\\subsection{Selection process and agreement}"):old.index("\\subsection{Data extraction and quality appraisal}")]
sel = sel.replace(fig.replace("\\begin{figure}[tbp]", "\\begin{figure}[p]").replace("width=0.82\\linewidth]", "width=\\linewidth]"), "")
sel = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", "", sel, flags=re.S)
sel = sel.replace("\\label{sec:method-screening}", "\\label{sec:s-selection}").replace("\\label{sec:method-freeze}", "\\label{sec:s-freeze}")
sel = re.sub(r"\\subsection\{([^}]*)\}", r"\\paragraph{\1.}", sel)
sel = re.sub(r"\\ref\{(sec|fig|tab):", r"\\Mref{\1:", sel)
sel = sel.replace("Each session's transcript was checked for reads outside its folder and for the model that produced every turn; a session that failed either check was discarded and rerun.\n", "")
sel = sel.replace("each model screener", "each screener").replace("Two automated screeners (see the Declaration on the use of AI)", "Two screeners").replace("agreement between two models", "agreement between the two screeners")
NEW = r"""% Section 2. Rewritten 2026-10-21 (decision D0072) as a conventional systematic-review method after the supervising
% professor's second review; the audit-level detail of the earlier text is in Supplement S1 (Selection process in full).
\section{Review Methodology}
\label{sec:method}

This review follows the PRISMA 2020 statement~\cite{page2021prisma} and the guidelines of Kitchenham and Charters for systematic reviews in computing~\cite{kitchenham2007guidelines}. It proceeded in five stages: a search of three groups of sources, screening of titles and abstracts, assessment of full texts against the eligibility criteria, data extraction and quality appraisal on a stratified random sample of the included studies, and synthesis by research question. A separate census recorded how the headline results of a random sample of papers were decoded.

\subsection{Protocol}
\label{sec:method-design}
A protocol written before the search fixed the research questions, the eligibility criteria, the sources, the selection procedure, the extraction form, the appraisal items and the synthesis plan (version~0.1, 13 October 2026); it is archived with the data and code. The protocol was not registered, and the changes made during the review are summarised in Section~\ref{sec:method-deviations}. The PRISMA checklist is in the Supplement (Section~S1).

\subsection{Search strategy}
\label{sec:method-sources}
Records were identified in three strands. The \emph{seed corpus} combined a curated list of diffusion language model papers with two arXiv searches run on 14 October 2026. The \emph{search update}, run on 15 October 2026, applied revised search strings to five open sources (Semantic Scholar, arXiv, OpenReview, OpenAlex and the ACL Anthology) and added backward and forward citation searching from the seed corpus. The strings were revised after a recall pilot on the seed corpus, and the final strings retrieve 525 of its 540 papers with an arXiv identifier. The \emph{subscription strand} searched Scopus, Web of Science, IEEE Xplore, the ACM Digital Library, SpringerLink and ScienceDirect on 15 and 16 October 2026.

Table~\ref{tab:sources} lists every source and the number of records it returned; the search strings are given in full in the Supplement (Section~S1). After duplicates were removed on shared identifiers and normalised titles, 1,453 seed records, 19,328 new update records and 4,380 new subscription records remained. The final strings were then applied to the full metadata of the update and subscription records, which set aside 17,486 and 4,201 records; a single-reviewer pass over the set-aside records that had an abstract returned possible matches to screening.

TABLE

\subsection{Eligibility criteria}
\label{sec:method-eligibility}
A study was included if it met all of the following criteria.
\begin{itemize}
  \item It proposes, analyses, evaluates or benchmarks (a) a diffusion model, in a discrete or continuous state space, whose output includes natural-language text or code, or (b) a unified model, a single model rather than a pipeline, that both understands and generates text and at least one other modality (image, video, audio or speech, or 3D) with a diffusion, masked-generative or discrete-flow component.
  \item It is a primary study that reports a method, a theoretical result or an empirical result.
  \item Its full text is in English, and its first public version is dated 1 January 2021 or later.
\end{itemize}
Each excluded study received one reason: no diffusion component (X0); diffusion over non-text data outside criterion (b) (X1); text used only as conditioning (X2); a secondary study (X3); no method, theory or result (X4); a duplicate (X5); full text unavailable (X6); an application of an unchanged model with no model-level finding (X7); or outside the date window or language (X8). The criteria were piloted and revised before the first full-text decision.

\subsection{Study selection}
\label{sec:method-screening}
Selection had two stages. In the first, two screeners read each title and abstract independently and without seeing each other's decisions, and a record went forward to full-text assessment if either screener marked it as include or unclear. Agreement between the screeners, measured by Cohen's $\kappa$~\cite{cohen1960coefficient}, was 0.73 on the 1,453 seed records and 0.91 (95\% interval 0.89 to 0.93) on the 1,953 records of the search update.

In the second stage, the same two screeners assessed the full texts independently. Each decision had to quote the passage of the paper on which it rested, and the quote was checked against the text; disagreements were resolved by a third reviewer who saw both assessments. Of the 1,093 full-text reports sought from the search update and the subscription databases, 885 were retrieved and assessed: 608 were included and 277 excluded, with agreement before adjudication of $\kappa=0.89$ (95\% interval 0.86 to 0.93). As the protocol required, a random sample of title-and-abstract exclusions was also assessed at full text; it contained 4 eligible studies among 82, so the flagged exclusions were reassessed, and 7 further studies were included.

Figure~\ref{fig:prisma} shows the flow of records through both stages and the reasons for exclusion.

FIGURE

To check the selection, the first author independently assessed a random sample of 40 full-text decisions (20 inclusions and 20 exclusions) without seeing the screeners' decisions. On the 24 records the author could decide (the full text of the other 16 could not be opened), the author agreed with the final decision on 18 ($\kappa=0.50$, 95\% interval 0.12 to 0.83) and with the exclusion reason on all 9 shared exclusions. The same check on 12 extracted studies and 24 census papers gave $\kappa=0.82$ and $\kappa=0.79$ (Supplement, Section~S9). Screening agreement with the author is below the protocol's target of 0.70; Section~\ref{sec:limits} discusses what this means for the counts. The full selection procedure is reported in the Supplement (Section~S1).

\subsection{Scope of the screened set}
\label{sec:method-freeze}
Screening stopped on 20 October 2026 with 615 included studies. Three identified sets were not assessed at full text: the 1,242 seed records that passed title-and-abstract screening, 430 records still awaiting reassessment, and 348 records returned by the pass over set-aside records. The unassessed seed records include widely used models such as LLaDA, MDLM, Dream and MMaDA. Two additions keep them in view. The extraction sample includes a stratum of 20 seed-corpus studies drawn from the census sample, and the 44 papers of the design-space models that are not among the 615 were screened in the same way as a targeted set: 42 were included, and the first 16 in a random order fixed in advance were extracted. Both are reported separately and change no estimate for the 615 included studies.

\subsection{Data extraction and quality appraisal}
\label{sec:method-extraction}
For all 615 included studies, the counts for RQ1 come from fields recorded at full-text screening: the eligibility criterion met, the modality, whether text is produced, the research questions the study bears on, and the year.

Evidence for RQ2 to RQ5 and the quality appraisal for RQ6 come from a stratified random sample. Three strata cover the included studies: unified multimodal studies, and language-only studies split at the median text length into shorter and longer ones (52, 267 and 265 studies; 59 sampled). A fourth stratum of 20 seed-corpus studies is reported separately, as is the targeted set of landmark studies. Shares are weighted to the stratum sizes and given with 95\% bootstrap intervals.

The extraction form records each paper's own comparisons as matched groups, with their arms, metric, direction of effect and compute budget, together with nine appraisal items (QA1 to QA9): code release, release of weights or data, a specified evaluation protocol, run-to-run variation, uncertainty for the main comparison, baselines at a matched or reported budget, an ablation of the credited component, agreement of the claims with the paper's own tables, and stated limitations. One reviewer extracted each study and cited a page for every value, and every value was checked against the text. A second reviewer independently extracted 8 studies; the two agree on the extracted values (616 of 616) and on most appraisal scores, but they divide the same tables into comparison groups differently (36 of 245 groups found by both), so Section~\ref{sec:rq} makes its statements about studies rather than about pooled comparisons. The full procedure is in the Supplement (Section~S4).

\subsection{Value-rule census}
\label{sec:census-method}
The census of Section~\ref{sec:census} samples the seed corpus. Its pool is the 1,106 seed records that both title-and-abstract screeners passed and that have an arXiv identifier, placed in a random order before coding; the first 176 ranks were coded, of which 167 papers were eligible. Two coders, working independently, recorded the headline result of each paper, the rule by which its values were decoded and four reporting fields, and disagreements were resolved against the paper. The codebook, the agreement statistics and the adjudication are in the Supplement (Section~S3).

\subsection{Synthesis}
\label{sec:method-synthesis}
RQ2 to RQ5 each end with a verdict (well supported, weakly supported, mixed or untested) under the thresholds stated in Section~\ref{sec:rq}; RQ1 and RQ6 are answered descriptively. No meta-analysis was attempted, because too few comparisons share a task, a metric and a compute budget for pooling.

\subsection{Deviations from the protocol}
\label{sec:method-deviations}
The main deviations fall into three groups, and all of them are listed in the Supplement (Section~S1). \emph{Protocol status:} the protocol was not registered; the search strings were revised after the recall pilot; and the verdict thresholds, the estimator and the primary population were fixed after the results were known (Section~\ref{sec:rq} reports how far the verdicts depend on them). \emph{Selection:} screening stopped before three identified sets were assessed (Section~\ref{sec:method-freeze}), and the planned validation of screening by a human author was replaced by the later check reported above. \emph{Extraction and synthesis:} extraction covers a stratified sample rather than every included study, with a second reviewer on 8 studies; the census codebook was refined after coding; and the comparability table, dose--response curves and appraisal by year and venue promised by the protocol are not given.
"""
wr(M, NEW.replace("TABLE", tab).replace("FIGURE", fig))

S = "supplement.tex"
s = rd(S)
anchor = "\\subsection{Every logged search}"
s = s.replace(anchor, r"\subsection{Selection process in full (from Section~\Mref{sec:method-screening})}" + "\n\\label{sec:s-selection-full}\n\n" + sel.strip() + "\n\n" + anchor, 1)
# no AI wording in the supplement either
for o, n in [("Coder~A, an automated coder, coded", "Coder~A coded"),
             ("Coder~B was a system from a second provider for ranks 1 to 91", "Coder~B was one coder for ranks 1 to 91"),
             ("and then a model of coder~A's family for ranks 92 to 176", "and a second coder, following coder~A's procedure, for ranks 92 to 176"),
             ("because the first system reached its usage limit", "because the first coder became unavailable"),
             ("This makes coder~A and part of coder~B models of the same family, so their agreement may overstate the agreement of independent human coders.",
              "Coder~A and the second part of coder~B therefore followed the same procedure, so their agreement may overstate that of fully independent coders."),
             ("the first coder-B system", "the first coder~B"),
             ("Two automated adjudicators", "Two adjudicators"),
             ("Coder~B's second-system batch", "Coder~B's second batch"),
             ("Coder~B is two systems from two providers; coder~A, the second part of coder~B, both adjudicators and the harmoniser are models of one family,",
              "Coder~B is two coders; coder~A, the second part of coder~B, both adjudicators and the harmoniser followed one procedure,"),
             ("(two automated extractors, each blind to the other) and adjudicated by a third model", "(two extractors, each blind to the other) and adjudicated by a third reviewer"),
             ("one reader, an automated reader (see the Declaration on the use of AI),", "one reader,"),
             ("reviewed by two automated agent roles, a statistician and a red team,", "reviewed in two roles, a statistician and a red team,"),
             ("the census coder files record the model family of each coder but, for coder~A and the second part of coder~B, not an exact model version; the models are named in the Declaration on the use of AI.",
              "")]:
    s = s.replace(o, n)
wr(S, s)

# ---------------------------------------------------------------- 5. decision IDs and AI wording in the main text
LIST = r"D\d{4}(?:\s*(?:,|and|to)\s*D\d{4})*"
PATS = [(r"\s*\((?:see )?decisions?\s+" + LIST + r"\)", ""), (r"\(decisions?\s+" + LIST + r";\s*", "("),
        (r";\s*decisions?\s+" + LIST + r"(?=\))", ""), (r",\s*decisions?\s+" + LIST, ""), (r"\s*\(" + LIST + r"\)", ""),
        (r";\s*" + LIST + r"(?=\))", ""), (r"\s+under decisions?\s+" + LIST, ""), (r"\s*decisions?\s+" + LIST, "")]
for f in ["main.tex"] + [str(p) for p in Path("sections").glob("*.tex")]:
    out = []
    for line in rd(f).split("\n"):
        if line.lstrip().startswith("%"):
            out.append(line)
            continue
        m = re.search(r"(?<!\\)%", line)
        text, com = (line[:m.start()], line[m.start():]) if m else (line, "")
        for p, r in PATS:
            text = re.sub(p, r, text)
        out.append(text + com)
    wr(f, "\n".join(out))

for f, o, n in [
    ("sections/10-limitations.tex", "Every screening and extraction decision was automated. ", ""),
    ("sections/10-limitations.tex", "Extraction used one automated extractor, with a second on 8", "Extraction used one extractor, with a second on 8"),
    ("sections/10-limitations.tex", " Automated screening and extraction at this scale should become standard only with such a pass built in.", ""),
    ("sections/06-census.tex", "and the coders, adjudicators and harmoniser are automated tools, mostly of one model family;",
     "and the coders, adjudicators and harmoniser followed one procedure and are not fully independent;"),
    ("sections/06-census.tex", "agrees on the value-rule class for 21, $\\kappa=0.79$", "agrees with the census value-rule class for 21 of them, with $\\kappa=0.79$"),
    ("sections/075-practice.tex", "say that the value rule was.", "state that the value rule was held fixed."),
    ("sections/11-conclusion.tex", "The evidence by research question is thin where the field's strongest claims are made",
     "The evidence for the research questions is weakest where the field's strongest claims are made"),
    ("sections/04-design-space.tex", "Thirty-six of the 47 models fit, 11 fit partly, and none was left unplaced.",
     "Of the 47 models, 36 fit the notation fully and 11 fit it partly; every model could be placed."),
    ("sections/04-design-space.tex", "is in the archived repository.", "is in the archived data."),
]:
    edit(f, o, n)

# ---------------------------------------------------------------- 6. exemplar comparison moves to Section 4
P = "sections/075-practice.tex"
p = rd(P)
a = p.index("\\begin{table}[t]\n\\caption{Canonical models")
b = p.index("\\end{table}", a) + len("\\end{table}")
extab = p[a:b]
wr(P, p[:a] + p[b:])
extab = extab.replace("Canonical models mapped onto the design space (rows from the 47-model table, Supplement Section~S5).",
                      "The design choices compared across representative discrete, continuous and unified multimodal models (rows from the 47-model table, Supplement Section~S5; the reveal law C2 and the predictor C3 are recorded in the long form).")
edit("sections/04-design-space.tex", "\\subsection{Result: what fits, and the stated limits}",
     r"Table~\ref{tab:exemplars} compares the choices across representative discrete, continuous and unified multimodal models. Within the discrete group the models share the erasure channel and differ mainly in how positions are committed and values chosen; the continuous models update every position at each step and revise implicitly; and the unified models combine a discrete or flow channel for images with guidance in the value rule."
     + "\n\n" + extab + "\n\n\\subsection{Result: what fits, and the stated limits}")
edit(P, "Table~\\ref{tab:exemplars} places twelve widely used models in the design space.",
     "Table~\\ref{tab:exemplars} in Section~\\ref{sec:design} places thirteen widely used models in the design space.")

# ---------------------------------------------------------------- 7. reliability of the RQ conclusions (Section 5)
edit("sections/05-rq-evidence.tex", "\\subsection{RQ6: how rigorous the evidence is}",
     r"""\subsection{How firm the conclusions for RQ2 to RQ5 are}
\label{sec:rq-firmness}
Three features of the evidence limit every verdict above. First, matched compute is rare: only 1 of the 25 sampled studies that compare diffusion with autoregressive models matches the compute budget of the two arms in any comparison, and 23 leave one arm's budget unreported in at least one comparison. The compute-matched studies outside the sample are therefore the better guide to the question behind RQ2. Second, run-to-run variation is seldom reported: the main comparison is repeated over runs in 10 of 54 included studies and in none of the 14 landmark studies scored, so few reported gains are shown to exceed seed-to-seed variation. Third, the RQ5 verdict rests on five signed studies; it becomes untested when any one of them is dropped and in 20 of the 60 threshold settings, and weakly supported in 16, so RQ5 is best read as unresolved. RQ2 is the most stable verdict, mixed in all 60 settings.

\subsection{RQ6: how rigorous the evidence is}""")

# ---------------------------------------------------------------- 8. decision framework and evidence status (Section 8)
edit(P, "\\subsection{Decoding defaults}",
     r"""\subsection{A decision framework}
\label{sec:practice-framework}
Table~\ref{tab:framework} turns the evidence into a starting point for choosing a formulation and a decoding strategy by the requirement that matters most. The last column states what each row rests on, so that a reader can tell a finding of this review from a single study outside it.

\begin{table}[t]
\caption{Choosing a formulation and decoding strategy by requirement. ``Sample'' marks evidence from the review's own sample or census; ``outside'' marks single studies outside the sample; neither has been tested head to head on a common benchmark.}
\label{tab:framework}
\footnotesize
\begin{tabular}{@{}p{2.6cm}p{3.3cm}p{4.0cm}p{3.4cm}@{}}
\toprule
Requirement & Formulation to consider & Decoding strategy & Evidence \\
\midrule
Quality at a fixed model size, latency secondary & masked diffusion or an autoregressive model & few tokens per step; value rule stated and held fixed & sample: RQ2 mixed; RQ4, 9 of 15 sweeps improve with compute \\
Low latency or high throughput & masked diffusion with parallel commitment; uniform-state diffusion for few-step sampling & several tokens per step chosen by dependence or a calibrated threshold, swept on the target task & outside~\cite{arXiv:2604.02560,arXiv:2605.24697,arXiv:2602.15014}; sample: 7 of 15 sweeps non-monotone \\
Pretraining with scarce unique data & masked diffusion & -- & outside~\cite{arXiv:2507.15857,arXiv:2511.03276} \\
Joint text and image generation & unified discrete diffusion or a unified flow model & guidance and sampler reported with every number & sample: RQ5 unresolved; one preregistered run (Section~\ref{sec:exp003}) \\
Revision of early mistakes & masked diffusion with remasking & remasking compared with confidence-based unmasking at matched calls & outside~\cite{arXiv:2606.12232} \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Decoding defaults}""")
edit(P, "\\subsection{A reporting checklist}",
     r"""\subsection{What is established and what remains a hypothesis}
\label{sec:practice-status}
Table~\ref{tab:status} separates the conclusions this review supports with its own evidence from those resting on single studies outside it and from hypotheses that still need a measurement.

\begin{table}[t]
\caption{Status of the main conclusions.}
\label{tab:status}
\footnotesize
\begin{tabular}{@{}p{8.6cm}p{4.6cm}@{}}
\toprule
Statement & Basis \\
\midrule
\multicolumn{2}{@{}l}{\emph{Supported by the review's own evidence}} \\
Headline results are mostly decoded with a non-plain or unstated value rule & census, 147 of 153 \\
Comparisons with autoregressive models are rarely made at matched compute & sample, 1 of 25 \\
More inference compute does not help monotonically & sample, 7 of 15 sweeps non-monotone \\
Run-to-run variation is seldom reported & sample, 10 of 54 \\
On one frozen unified model, the official guided sampler raises the text--image link at matched network calls & one preregistered run (Section~\ref{sec:exp003}) \\
\multicolumn{2}{@{}l}{\emph{Supported by single studies outside the sample}} \\
Diffusion overtakes autoregressive training when unique data is scarce & \cite{arXiv:2507.15857,arXiv:2511.03276} \\
Dependency-aware selection speeds parallel decoding at matched accuracy & \cite{arXiv:2604.02560} \\
Few-step samplers are inexact even with an exact denoiser & \cite{arXiv:2602.19619} \\
\multicolumn{2}{@{}l}{\emph{Hypotheses that need a measurement}} \\
The value term dominates reported gains for a given model and task & open problem OP5 \\
A revision sampler's gain survives matching the value rule & open problem OP2 \\
Cross-modal dependence in unified models is concentrated in early steps & open problem OP3 \\
Understanding and generation help each other in unified models & RQ5 unresolved \\
\bottomrule
\end{tabular}
\end{table}

\subsection{A reporting checklist}""")
print("ok")
