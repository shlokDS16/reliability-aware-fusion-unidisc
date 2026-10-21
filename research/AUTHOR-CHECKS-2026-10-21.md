# Author checks for Paper 1 (2026-10-21)

**What this is.** Twelve short yes/no checks. The adjudicating model (Claude Fable) could not settle them from the
paper alone, or a script needed a human eye. Each check names the paper, where to look, and the model's answer.

**What to do.** Open the link, look at the place named, and reply in the chat with either
"all agree" or the numbers you disagree with (for example "4 no, 9 no"). About 20 to 30 minutes in all.
Nothing else is needed. If you skip a check, the model's answer stays and the paper says it was not confirmed.

**Why it matters.** Checks 1 to 6 change one quality score each in the per-study table (supplement S6). Checks 7 to 9
change whether a code link counts as working (QA1). Checks 10 to 12 are minor.

| # | Paper (link) | Where to look | Question | Model's answer |
|---|---|---|---|---|
| 1 | R0171, Conditional [MASK] Discrete Diffusion Language Model, https://arxiv.org/abs/2411.06438 | Introduction, list of contributions | Is the paper's main contribution a new **method** (the EAGS sampler), rather than an analysis? | Yes, a method |
| 2 | R0588, Deferred Commitment Decoding for Diffusion Language Models, https://arxiv.org/abs/2601.02076 | Introduction, first contribution bullet | Is the main contribution the **DCD decoding method** (not only the finding that motivates it)? | Yes, the method |
| 3 | R0738, https://arxiv.org/abs/2602.23792 | Introduction, the paragraph headed "Motivation" and the contributions | The model took the first listed contribution ("Motivation", an analysis of parallel decoding) as what the paper credits, so the paper gets no ablation score. Should the credited contribution instead be the **new decoding method** the paper proposes? | No: the analysis is credited |
| 4 | M15033, GRAFT: Restoring the Missing Sampling Interface in Continuous Diffusion Language Models, https://openreview.net/pdf?id=TDqycsDdqm | Introduction, contributions | The model coded it as an **analysis** paper (its credited finding: a lexical long-tail collapse), not a method paper (GRAFT). Do you agree? | Analysis (close call) |
| 5 | M15033 (same link) | Table 2 and its caption | Does Table 2 **state the compute budget** (steps or network calls) of each compared row? | Yes, reported |
| 6 | M19021, Unlearning bias in text diffusion models based on decoupled adapter, https://aei.ewapub.com/article/view/31209.pdf | End of the paper | (a) Is there a **limitations** section or paragraph? (b) Does the paper show a **failure case** or a setting where its method is worse? (c) Is the **data** used for the main comparison public and named? | (a) unclear, (b) yes, (c) unclear |
| 7 | R0188, https://arxiv.org/abs/2501.06848 | Abstract, last sentence ("Code is available here") | Click "here" on the arXiv page: does it lead to the **authors' own code**, and does it open? | Not counted: the text holds no URL |
| 8 | R0588 (link above) | Abstract or first page | Is **github.com/shuyingte/DCD** the authors' own code? | Yes (opens on 2026-10-21) |
| 9 | R0674, https://arxiv.org/abs/2602.05000 | Abstract ("Our code is available at ...") | Is **atutej.github.io/entrgi-rgrl** the authors' own code page? | Yes (opens on 2026-10-21) |
| 10 | M08783, DiffVC, https://doi.org/10.48550/arxiv.2604.08084 | Experimental settings | Is "sequence length 30 / 20" the **output caption length**? | Yes |
| 11 | M15840, Learning When to Commit: Schedule Distillation for Fast Diffusion Language Models, https://openreview.net/pdf?id=zEN2tdHWyN | Table 4 | Does the row "None" mean the component is **removed** (an ablation row)? | Left undecided |
| 12 | R0738 (link above) | The TPS definition | Is **higher throughput (tokens per second) better**? | Yes |

**Not asked of you** (recorded in analysis/extraction/d0052/agent-map.txt, kept as the adjudicator decided): design
provenance codes (D03, D08, D10, D11, D15), arm membership in figures, and about 40 proposed new entries for the
benchmark and metric look-up lists. The look-up entries change no reported number: units without a mapped benchmark
are still counted and only left out of matching across papers, which the review does not do.

---

## Part 2: blind check of 12 studies (the one item a referee will insist on)

**Why.** Two audits of the draft said the same thing: no human ever made a recorded screening or extraction decision,
and a CSUR referee is likely to ask for one before acceptance. A small recorded check fixes that: you answer six yes/no
questions for 12 randomly drawn included studies, without seeing the model's answers, and the paper reports how often
you and the model agree.

**What to do.**
1. Open `research/HUMAN-CHECK-2026-10-21.xlsx` (sheet "check"; the full wording of Q1 to Q6 is on sheet "questions").
2. For each row, open the link, skim the experiments and the end of the paper, and pick yes / no / unclear / NA in
   columns Q1 to Q6. Use Notes for anything odd. About 8 to 10 minutes per paper, so 1.5 to 2 hours in all; doing
   only some rows still helps (the paper reports how many were done).
3. Save the file and tell me in the chat. Please do not open `analysis/extraction/d0052/human-check-model-answers.json`
   before you finish: the check only counts if it is blind.

The six questions: (1) diffusion and autoregressive model side by side? (2) if so, compute budget of both stated or
matched? (3) a comparison of training choices? (4) a comparison of inference settings? (5) main comparison repeated
over two or more runs? (6) a limitations section or paragraph?

## Part 3. Landmark tranche items (added 2026-10-21, decisions D0061, D0063)

These come from the landmark screening and extraction. Each is a yes/no or pick-one confirmation of a model reading.

1. **R0523 (MMaDA-Parallel), eligibility basis.** Screener A read I1(a) (diffusion model with text output); screener B
   read I1(a) and (b) (also a unified understanding-and-generation model). Rule D0039: the counts use A's value and give
   B's as a range (Section 5 RQ1 and RQ5 say so). Which is right: a, or ab?
2. **R0326 (Seed Diffusion), adjudicator EC.** (a) Headline table: EC chose Table 2 (MBXP Python 79.4) because Table 1
   is printed inside Section 3.4; the second extractor chose Table 1 (Aider 44.4). Agree with EC? (b) EC kept no
   diffusion-versus-autoregressive groups, because the only autoregressive label is one collective sentence that also
   names diffusion baselines. Agree?
3. **R0268 (EB-sampler), adjudicator EC.** (a) Is the future-work sentence a stated limitation (QA9a, S15)? (b) CT1 and
   F4 were left in doubt by EC; see analysis/extraction/lmk/EC/ecl001/EC-ecl001.jsonl, field "doubt".
4. **Proposed lookup entries** (benchmark and metric names the extractors met): MBXP -> mbxp; "Relative Time Per
   Forward" -> relative-time-per-forward (lower is better); "inference speed" -> tps; "Accuracy (%)" -> accuracy;
   "Speed-Up" -> speed-up; "Maze navigation" -> maze-navigation; "Sudoku solving" -> sudoku. Accept all?

## Part 4: blind screening check (40 records)

**Why.** All full-text screening was done by language models. This check records a human decision on a random 40 of
the 885 tranche-T1 records (20 the models included, 20 they excluded; you are not told which), and the paper reports
how often you and the models agree (Cohen's kappa with a 95 percent interval).

**The file.**
`C:\Users\Shlok\Downloads\Multi-Modality Language model\.claude\worktrees\resume-dlm-discovery-exp-003-334706\research\HUMAN-CHECK-SCREENING.xlsx`
Sheet "check" has one row per record; sheet "rules" has the screening rules (criteria v1.6) in plain language on one
screen.

**What to do.**
1. Open the file and read the sheet "rules" once. Keep it open in a second window while you work.
2. For each row, open the **Link** (the open-access copy the models screened) or, if it does not open, the **Local
   text copy** (a plain-text file of the same paper; the PDF is in
   `...\research\sources\pdfs\fulltext\<Record id>.pdf`). Six links are IEEE DOIs and need VIT access; off campus,
   use the local copy.
3. Read the title and abstract, then skim the method and the results tables (and the appendix if the output type is
   unclear).
4. In **Decision** pick include, exclude or unclear from the drop-down. Use unclear only if you cannot decide, and say
   why in **Notes**.
5. If you pick exclude, pick the **first** code that applies in **Exclusion code** (order X8, X3, X5, X4, X0, X1, X2,
   X7; meanings on sheet "rules"). For X1 versus X2 follow the three steps on the rules sheet. Leave the code blank for
   include and unclear.
6. Type your initials in **Reader**. Use **Notes** for anything odd.
7. Save the file under the same name and tell Claude in the chat. Doing only some rows still helps: the paper reports
   how many were filled.

About 4 to 5 minutes per record, so about 3 hours in all.

**Two readers.** Two people may split the rows (for example rows 1-20 and 21-40); each types their own initials in
Reader. If you both want to read the same record (this gives a human-to-human agreement figure as well), the second
person adds a new row at the bottom with the same Record id, or saves a copy named
`HUMAN-CHECK-SCREENING-<initials>.xlsx` in the same folder; the script reads both.

**Keep it blind.** Do not open `analysis\screening\human-check-screening-model-answers.json` before you finish, and do
not look the papers up in the review's own lists of included studies (the supplement tables, the release files or
the screening folders). Records you have already seen with a decision (CONFIRM-2026-10-20, the items of Parts 1 and 3
above, and the 12 studies of Part 2) were left out of the draw.
