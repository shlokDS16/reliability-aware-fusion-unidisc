# Edit brief: publication-level pass for ACM Computing Surveys (2026-10-21)

Paper: "Diffusion Language Models and Unified Multimodal Generation: A Critical Systematic Review" (PRISMA systematic
review, target ACM Computing Surveys, the top survey journal; desk rejection is the risk). Sources: paper/review/main.tex
and paper/review/sections/*.tex. Compiled reference: paper/review/main.pdf (34 pages incl. references; limit 35).

## Hard constraints
- Do NOT change any number, citation key, \label, \ref target, equation, table cell value or claim strength. Do not add
  new claims, numbers or citations. Keep every `% src` comment and every comment line exactly as it is.
- Do NOT make the text longer. Aim for equal or shorter length per paragraph; the paper is at its page limit.
- AI, language models, automated screeners/coders, model names (Claude, Codex, ChatGPT, GPT, Opus, Sonnet, Fable,
  Haiku), "agent", "session", "transcript" must not appear anywhere except the unnumbered "Declaration on the use of AI"
  in main.tex. Do NOT edit that Declaration (the author edits it by hand).
- Do NOT run latexmk or any build (several editors work in parallel and the build is shared). Keep LaTeX valid by eye:
  balanced braces, ~ before \ref and \cite, $...$ math intact, escaped % and &.
- Edit only the files assigned to you.

## Issue classes to fix everywhere in your files (the supervisor found instances; fix ALL instances)
1. Awkward or informal phrasing, e.g. "The line began", "Around them sit surveys", "none could not be placed",
   "is thin", "weaker than it sounds", "says more about the baselines than". Use formal academic register, varied
   sentence openings, active voice where natural. No defensive or apologetic tone; state limits plainly once.
2. Audit-log or internal-process prose: decision numbers (D0001-style), internal set names (T1, R797, "tranche",
   "rescue pass"), "red team", "primer", "ledger", "withdrawn", "our evidence records", row ids such as M01-M29,
   "awaits", notes to self, version strings of internal files, counts of internal sessions. Replace with what a reader
   of a survey needs, or delete if it serves only the authors.
3. Paper titles quoted in running text: cite by author instead (\citet{key} prints "Author et al. [n]").
4. A table and a figure cited together in one parenthesis, e.g. "(Table 1; Figure 2)": split.
5. Incomplete sentences, dangling parentheticals, sentences that only make sense with a symbol: make each sentence
   complete; where a symbol is essential, keep it and say in words what it denotes at first use in your section.
6. Jargon undefined for a survey reader: define at first use in plain words or replace (e.g. "value rule", "commit
   kernel", "tilted twin", "signed study", criteria labels I1(a)/I1(b), census codes A, T, P, S, G, M, C, U, NS, F3-F6).
7. Inconsistent terms: use "fit fully" / "fit partly" for the design-space test; verdict names exactly "well
   supported", "weakly supported", "mixed", "untested"; "included studies", "seed corpus", "landmark set".
8. Section and subsection headings must be specific to this review, not generic (e.g. "Results" -> "What the census
   finds"); paragraph headings likewise.
9. Citations used as nouns must read naturally: "Austin et al.~\cite{...} introduced" (\citet{} gives "Austin et al. [3]").
10. Supplement pointers must say "the Supplement (Section S#)" consistently.

## Style model (published CSUR surveys)
Yang et al. 2023, "Diffusion Models: A Comprehensive Survey", CSUR 56(4); Ali and Molla 2025, "A Systematic Literature
Review on Multimodal Text Summarization", CSUR 58(3). Their prose: topic sentence first, short paragraphs, each
claim followed by its citations, methods described in a few plain sentences, no process diary, summaries at the end of
long subsections ("In summary, ...").

## Report
Return a short list of what you changed per file (one line per change class with counts) and anything you could not fix
without changing a number or claim.
