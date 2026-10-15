# Title-and-abstract screening, search update 2026-10-15 (D0026-D0028)

Read `research/CONTRACT.md`, then apply the fixed criteria in
`research/review/screening/criteria-v1.md` exactly, with one clarification from the protocol
amendment of 2026-10-15 (`research/review/protocol.md` section 10, D0020):

- I1(b) "unified" means one model (shared weights or one jointly trained system), not a pipeline of
  separately trained models; "another modality" means image, video, audio or speech, or 3D. A
  unified model whose text is autoregressive and whose diffusion or flow component generates one of
  these is eligible. Robot actions, molecules and other non-text domains with autoregressive text
  are X1. X1 covers every diffusion model whose diffusion component produces no natural-language
  text or code and is not covered by I1(b).

Rules:
- Decide from the title and abstract only; no outside knowledge of the paper. Missing abstract or
  not decidable: "unclear".
- You are blind: do not open any other screener's output (`research/review/screening/v2/screener-*`
  other than your own file, `screener-A/`, `screener-B/`, `disagreements.csv`), and do not open
  `research/review/corpus/` files.
- Scratch files only in the scratchpad subfolder your dispatch names; never run another agent's
  scripts.

Output: one JSON object per record, appended after each record (or in chunks of at most 25), to the
file your dispatch names, UTF-8:
{"id": "<id>", "decision": "include" | "exclude" | "unclear", "code": "<X0|X1|X2|X3|X4|X7|X8 or empty>", "reason": "<at most 15 words>", "screener": "<A-claude-sonnet | B-claude-opus | V-claude-sonnet>"}
Every input id must appear exactly once. If the file already has rows (a resumed batch), skip
those ids. If writing is refused, return the lines instead.

Final message: counts by decision and code, ids you could not decide, and up to five criteria
ambiguities (id and one sentence each).
