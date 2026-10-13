# Q1 Journal Writing Style

The house style of a strong Q1 paper. Apply the `/humanizer` skill on top of every
one of these rules — they are complementary. These rules come from what actually
survived Q1 peer review.

## Voice and person

- **Third person, impersonal.** No "we", "our", "I". Convert "we run CORAL for 40
  generations" → "CORAL is run for 40 generations". "Our method" → "the proposed
  method" or just the method's name.
- Exception: some journals now accept limited first person. Default to impersonal
  unless the author says the target journal prefers otherwise.
- Present tense for established facts and what the paper does ("Table 1 reports...").
  Past tense for the specific experiments that were run ("the router was trained on...").

## The abstract (4-part structure)

A Q1 abstract has four moves, in order, with no citations and no first person:

1. **Purpose** — the problem and why it matters (1-2 sentences).
2. **Design/Methodology** — what was built and how it was evaluated (2-3 sentences).
3. **Findings** — the concrete headline results, with baselines named (2-3 sentences).
4. **Originality/Value** — what is new and who benefits (1-2 sentences).

Keep it ~200-250 words. Every number in the abstract must appear identically in the
results and tables. Do NOT overclaim in the last sentence ("marks a new way for..."
gets flagged as promotional).

## Sentences and paragraphs

- **Shorten long sentences.** Reviewers explicitly ask for this. If a sentence runs
  past ~35 words or has three or more clauses, split it.
- **No 2-3 line orphan paragraphs.** Merge short fragments into the preceding
  paragraph so the prose flows. Reviewers flag choppy structure.
- **Consistent terminology.** Pick one term and one symbol for each concept and never
  alternate (e.g. always "NACU", never switch to "cost units"; always the pair
  (m_weak, m_strong), never switch subscript/inline forms).
- **One idea per paragraph**, topic sentence first.

## Claims and hedging

- State the mechanism, then the evidence. "CORAL reduces cost because prompt
  adaptation lets the weak model clear the threshold on medium-difficulty queries"
  is stronger than "CORAL is better".
- **Never overstate Pareto/dominance claims.** "Pareto-dominates across the entire
  frontier" is almost always false and a technical reviewer will catch it. Say where
  the method wins and where the margin narrows. Honesty reads as rigour.
- Acknowledge limitations explicitly, including where the method gives NO benefit.
  This satisfies reviewers and strengthens credibility.

## Promotional language to delete (AI/overclaim tells)

- "marks a new way", "a new paradigm", "revolutionary", "significantly", "substantial"
  (unless quantified), "cutting-edge", "seamlessly", "robust" (unless defined),
  "leverage" as a verb, "delve", "underscore", "pivotal".
- Rule-of-three lists everywhere, over-parallel structure, and the em-dash pile-up are
  classic AI tells — see the `/humanizer` skill.

## Dashes and punctuation

- When the author asks for no dashes, replace every em-dash (—) and en-dash (–):
  - Number ranges "182–197" → "182 to 197".
  - Parenthetical em-dash → comma, or split the sentence.
- Check the RAW docx for dashes, not the pandoc text — pandoc silently converts them.
  `python3 -c "import zipfile;x=zipfile.ZipFile('p.docx').read('word/document.xml').decode();print('em',x.count('\u2014'),'en',x.count('\u2013'))"`

## Section-boundary discipline (Results vs Discussion vs Conclusion)

Reviewers penalise repetition across these three. Keep them distinct:
- **Results**: what the numbers are. No interpretation.
- **Discussion**: what the numbers mean, why, and their limits.
- **Conclusion**: the single concrete takeaway + future work. Not a re-list of results.
Do not repeat the same headline finding in all of abstract + results + discussion +
visual summary + conclusion. State it once precisely, reference it after.

## Practitioner-facing content

If the paper has a "Recommendations for Practitioners" section, it must contain
clearly separated, distinct pieces of advice (label them: "First, on X:"), not one
dense paragraph. A single recommendation reads as thin.
