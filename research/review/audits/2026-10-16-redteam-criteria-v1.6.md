```yaml
agent: red-team
date: 2026-10-16
brief: Sixth, final focused check of full-text screening criteria v1.6 (commit dbaeab0). Covers the status of Y1, Y2 and y3-y7, new fatal or major problems introduced by v1.6, brief probes of quote_check, the D0032 row facts, and a verdict.
sources_examined:
  - research/CONTRACT.md
  - research/review/screening/criteria-v1.6-screener.md (diffed against v1.5; record-id grep)
  - research/review/screening/criteria-v1.6.md sections 0, 1 (R7, R12), 2.0, 4, 7 and the D0032 row
  - analysis/screening/quote_check.py at dbaeab0 (git diff against 83eb816; self-test)
  - frozen frame, sample, OC v1.4 and C8 files (digests); ~/.claude/tools/graph_memory.py (digest)
  - research/review/protocol.md s4 step 3 (15 percent, at least 100)
coverage: >
  The full screener diff from v1.5 to v1.6, the changed audit-copy sections, the row, and the quote_check
  diff. quote_check self-test: 38/38 (python -I, scratchpad/v16). I reran the 21 v1.5 probes and ran
  9 new ones. The route paragraph is identical across S, A and the row (normalised string comparison).
  The screener copy contains no record id (grep 0). NOT covered: no full text, no pilot. Settled items
  were not re-opened.
claims:
  - statement: "Y1 is resolved: the R7 trajectory sentence no longer reclassifies 3D human pose, motion or geometry"
    status: supported
    evidence: "S R7 (diff lines 110-114: robot, vehicle or navigating agent only; 'never reclassifies 3D human pose or motion or other 3D geometry ... the number encoding never decides eligibility'); A section 1 R12 row; row clause (3)"
    level: E2
    confidence: 0.9
  - statement: "Abbreviations and colons no longer hide a preceding negation in quote_check"
    status: supported
    evidence: "v1.5 probes eg_split, etal_split, colon now negation_before; new probes i_e and sec_neg negation_before"
    level: E4
    confidence: 0.9
  - statement: "Every D0032 row fact matches the files"
    status: supported
    evidence: "digests a9180fe4, 95886765, 3f9c610e, 6c4928af unchanged; quote_check e7d2b6ee and self-test 38/38; graph_memory.py ea9c3c07 recomputed equal; audit counts incl. 'v1.5 check: adopt with listed fixes, 2 major, 5 minor' correct; OC numbers unchanged"
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - "Whether Route F or H is chosen; the attestation is self-reported by design."
next_test: {hypothesis: "v1.6 rules are applied identically by two blind screeners", intervention: "blind dual pilot as named in the v1.3-v1.5 reports", primary_metric: "decision and code agreement per rule", falsifier: "any disagreement traced to D5, R7/R12/D4(2) or R10 b3", gpu_hours: 0}
```

# Red-team check of criteria v1.6 (sixth pass)

**Verdict: adopt as written.** All seven v1.5 findings are resolved. There is no new fatal or major
finding. Two new minor findings (z1, z2) in quote_check.py are listed below. Neither blocks adoption,
and neither needs another audit.

Counts:
- **Y1, Y2 and y3-y7:** 7 resolved.
- **New findings:** fatal 0, major 0, minor 2.

Line numbers: `S` = criteria-v1.6-screener.md (diff positions), `A` = criteria-v1.6.md.

## 1. Status of the v1.5 findings

| Finding | Status | v1.6 line |
|---|---|---|
| Y1 trajectory sentence vs D4(2) | resolved | S R7 l.110-114: only the waypoints, positions or path of a robot, vehicle or navigating agent count as a trajectory. The sentence "never reclassifies 3D human pose or motion or other 3D geometry ... the number encoding never decides eligibility". The A section 1 R12 row matches, and so does row clause (3). |
| Y2 Route H blindness and validation order | resolved | S section D l.237-239: validation records are screened per tranche before any A/B/C row of that tranche is seen. S section F l.312-314 and A section 4 item 4: an attestation, a prior-exposure statement and a files-opened list go in c-run-log.jsonl, and K is reported with and without any session that lacks them. A section 4 item 6 defines tranches T1, later queues and the 797, each with a seeded 15 percent draw and at least 100 in T1. This is consistent with protocol s4 step 3. |
| y3 Bash/PowerShell paths | resolved | A section 0 isolation rule (1) covers paths anywhere in Bash and PowerShell commands, `..`, `~` and absolute paths outside the folder. Rule (2) defines "explicit path". The brief S l.250-252 says the same. |
| y4 splitter, tags | resolved | quote_check.py: `_SENT_END` without the colon, `_ABBREV`, and stripping limited to known tags. The v1.5 probes eg_split, etal_split and colon now return negation_before. `<p and not q>` and `<q and not r>` stay in the text. A real `<span class=...>` is still stripped. |
| y5 D5(ii) | resolved | S D5 l.64-66: "to generate natural-language text or code ... text only as a condition or annotation, for example on text-molecule pairs, is not (ii)". Row clause (3) matches. |
| y6 graph_memory.py digest | resolved | A section 0 and the row evidence: sha256 ea9c3c07...f29a, which I recomputed and found equal. Re-check rule if the digest changes. |
| y7 short header evidence | resolved | S brief l.272-275: quote the header with its cell, or quote the caption and name the header in loc. |

## 2. New findings (v1.6 only)

No fatal or major findings.

Minor (non-blocking; for the next quote_check revision):
- **z1. Negations joined by a hyphen are no longer seen.** `_WORD` now treats a hyphenated compound as one word. In "keep not-shared weights between the understanding and generation branches", the quote `weights between the understanding and generation branches` returns `found`. v1.5 split "not" off and rejected the quote. The form is rare in papers.
- **z2. "No." is treated as an abbreviation.** `no` is in `_ABBREV`. In "Do both modules share weights? No. Both modules share all transformer weights...", the true sentence end after "No." is skipped, so the following affirmative quote is rejected (`negation_before`). This costs work, not correctness: the record goes back to the screener once and then to adjudication. "Sec." and "i.e." negations are now caught (probed).

## 3. D0032 row: fact check

| Statement | Result |
|---|---|
| audit counts, now incl. "v1.5 check: adopt with listed fixes, 2 major, 5 minor" | correct |
| frame a9180fe4..., sample 95886765..., OC v1.4 3f9c610e..., C8 6c4928af... | unchanged (sha256) |
| quote_check.py v1.6 sha256 e7d2b6ee55b794e211e63a2d27404334a90a51876acc1d05d303c704c4a2c45b; self-test 38/38 | correct |
| graph_memory.py sha256 ea9c3c071eb3a9318c628ddb1473f873a503aa7dd28ec07eb7330d414234f29a | correct (recomputed) |
| route paragraph | identical in S, A and the row |
| per-tranche validation (15 percent, seed 20261016, at least 100 in the first tranche); attestation in c-run-log.jsonl | matches A section 4 items 4 and 6 and S section D |
| K >= 1; 0.416/0.660/0.827/0.885; UB 22; L = 13 "that pass the automation filter" | unchanged and correct |
| clause (3): 3D pose, motion and geometry decided by the "3D" reading whatever the encoding; D5(ii) "pretrains to generate ... text used only as a condition does not count" | matches the screener copy |
| evidence list includes the v1.5 audit file | the file exists in research/review/audits/ |

## 4. Fixes

Blocking: none.

Non-blocking:
1. z1: split hyphenated compounds whose first part is a negation word ("not-", "no-") when checking the negation window.
2. z2: drop `no` from the abbreviation list, or require a following digit before treating "No." as an abbreviation.
