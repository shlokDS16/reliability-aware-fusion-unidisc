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
