# Value-rule census, recounted after the tilt/selection split (2026-10-14)

Source: `design-space-v1.csv`, column "value-rule classes" (A argmax, T low temperature, P top-p or
top-k, S sample-then-filter, G guidance, M sequence-level selection), restricted to the 29 rows
whose headline "uses E_sel-type rule" = yes. Reason for the recount: `review/method/
selection-term.md` T1.5 reclassifies A, T, P and G as state-only tilts (E_tilt, inside the
factorisation identity); only value-dependent selection (S, and sequence-level M) is E_sel.
The reclassification is under red-team review; this recount is conditional on it.

Class counts among the 29 (a row can carry several): G 14, A 12, P 5, T 4, S 4, M 1.

| Group | Rows | Entropy or diversity reported |
|---|---|---|
| tilt only (A, T, P, G) | 24 | see CSV |
| value-dependent selection (S or M) | 5: MaskGIT (S, T), Show-o (G, S), UniDisc (G, P, S, T), Dynin-Omni (G, S), DiffuSeq (A, M) | 1 of 5 (DiffuSeq); 0 of the 4 sample-then-filter rows |

Reading: the census claim must be worded as "24 of 40 headlines use a value tilt and 5 use
value-dependent selection", not "29 use E_sel". All four sample-then-filter headlines are
image or unified multimodal models, and none reports entropy or diversity. The agent's report
also names FUDOKI best-of-n as sequence-level selection; that row is not flagged "yes" in the CSV,
so it is not counted here (to be checked).

Command: inline Python over the CSV, run in the orchestrator session on 2026-10-14 (regex
`\b([ATPSGM])\b` on the class column).
