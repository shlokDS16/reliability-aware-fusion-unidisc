# Census coding brief for Claude coders (2026-10-15)

Written by the orchestrator. Applies to coder B (Claude Opus, ranks 92 onward, continuing
Codex coder B, which coded ranks 1 to 91 before its limit; D0015) and coder A (Claude Sonnet,
blind, all ranks). Read `research/CONTRACT.md` first.

## What you code
Papers in `research/review/census/census-order.csv`, in rank order, for the rank range your
dispatch message gives. Full texts: `C:\Users\Shlok\Downloads\Multi-Modality Language model\research\sources\census-text\<arxiv>.txt`
(main checkout; read only). Ranks 23, 33, 90 and 144 have no text: write a row with
"eligible": "NA", "exclusion_code": "NO_TEXT" and all F fields "NA".

## Rules
- Codebook: `research/review/coverage/census-codebook-v1.md`, as amended by
  `research/review/coverage/census-codebook-v1.1.md`. Apply it literally, from the paper's text only.
- Eligibility first (protocol I1 to I4). Eligible if all hold: I1 the paper proposes, analyses,
  evaluates or benchmarks (a) a diffusion model (discrete or continuous, including masked or
  absorbing diffusion, discrete flow matching, diffusion on embeddings or the simplex) whose output
  includes natural-language text or code, or (b) a unified model that both understands and
  generates across text and another modality using a diffusion, masked-generative or discrete-flow
  component; I2 primary study with a method, theory or empirical result; I3 English full text;
  I4 first version from 2021-01-01. If not eligible, one exclusion code: X0 no diffusion component,
  X1 non-text diffusion only, X2 text only as conditioning, X3 secondary study, X4 no result,
  X5 duplicate, X7 application of an unchanged model with no model-level finding, X8 date or language.
- F2_codes: letters joined by + from A, T, P, S, G, M, or "U", "NS", "NA" as the codebook defines.
  F1 may be "QL" (v1.1 A-10) or "NA". Quotes in notes at most 15 words.
- Read efficiently: abstract and the introduction's contribution list, then Grep the text for
  `temperature|top-k|top-p|nucleus|greedy|argmax|guidance|cfg|remask|confiden|steps|NFE|entropy|diversity|MAUVE|Self-BLEU|recall`
  and read the experiment section, captions and hyperparameter tables you need. Do not read a
  paper end to end unless the value rule cannot be located otherwise.
- **Blindness.** Do not open any other coder's output: `research/review/census/coder-B*.jsonl`,
  `coder-B-run*`, any `coder-*-claude-*.jsonl` other than your own, and
  `research/review/coverage/census-*.csv`, `census-adjudication-notes.md`, `census-coder2-notes.md`,
  `census-result-v1.md`. The two codebook files are allowed.

## Output (save as you go)
One JSON object per line, appended to your own file **after each paper** (so work survives an
interruption): `research/review/census/coder-<B|A>-claude-r<first>-r<last>.jsonl` (paths relative
to `C:\Users\Shlok\Downloads\Multi-Modality Language model\.claude\worktrees\resume-dlm-discovery-exp-003-334706`),
keys in order:
`rank` (int), `sid`, `arxiv`, `eligible`, `exclusion_code`, `F0_version`, `F1_task`, `F1_metric`,
`F1_value`, `F1_location`, `F2_codes`, `F2_detail`, `F2_location`, `F3`, `F3_location`, `F4`,
`F4_location`, `F5`, `F6`, `notes`, `coder` ("B-claude-opus" or "A-claude-sonnet").
Use UTF-8. If the file already has rows (a resumed batch), skip the ranks already present.
If writing is refused, return the JSON lines in your final message instead.

Final message: number coded, number eligible, any rank you could not code and why, and up to five
codebook ambiguities you met (rank and one sentence each). No other commentary.
