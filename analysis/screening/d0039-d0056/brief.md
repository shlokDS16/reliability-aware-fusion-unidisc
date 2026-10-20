# Job B: nine label choices (proposal for the first author to confirm)

Each paper below is already decided (include or exclude) under criteria-v1.6-screener.md in this folder. Two readings differ on ONE label. Read the paper's full text (fulltext/<id>.txt; page markers '=== page N ===') and the criteria's definitions of that label, then choose one of the two options. Record what the paper states.

Labels: code = the exclusion code (criteria section C, applied in the stated order, first that applies); i1 = inclusion basis (a: diffusion model whose output includes text or code; b: one unified model that both understands and generates across text and another modality; ab: both); nonlang_only = true if no result of the paper is natural-language text or code (it is included only by rule R14 over R7), else false.

| Item | id | decision | label | option 1 | option 2 |
|---|---|---|---|---|---|
| B1 | M17653 | exclude | code | X1 | X2 |
| B2 | M18667 | exclude | code | X0 | X3 |
| B3 | M17462 | exclude | code | X4 | X1 |
| B4 | M10840 | include | i1 | a | ab |
| B5 | M12859 | include | i1 | a | ab |
| B6 | U04330 | include | i1 | a | ab |
| B7 | M16043 | include | i1 | ab | b |
| B8 | M11389 | include | nonlang_only | true | false |
| B9 | M18059 | include | nonlang_only | false | true |

OUTPUT: write proposals.jsonl in this folder, one line per item: {"item": "B1", "id": "...", "label": "...", "answer": "<one of the two options>", "confidence": "high|medium|low", "reason": "<one sentence>", "quote": "<6-40 words copied verbatim from the text file>", "loc": "p.<N>, <section>"}.
