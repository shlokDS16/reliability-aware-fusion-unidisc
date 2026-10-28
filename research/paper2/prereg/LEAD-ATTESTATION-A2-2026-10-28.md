# Lead attestation for SAP addendum A2 (2026-10-28, Paper 2 lead session)

Requested by the red-team signature on A2 (condition in RED-TEAM-SIGNOFF-2026-10-28.md, from line 178).

Between the start of M1 (probe-2 completion launched 09:56 IST, items 26-199) and the commit of A2 (3f998076), the lead read only:
- the number of rows in runs/P2-PROBE-02/items.jsonl (row counts);
- the driver's chunk lines (launch, exit code, row counts);
- machine health: nvidia-smi temperature and memory, boot time, and Windows crash-event counts.
Before M1, during M0 stage 3, the lead read only peak_gb and seconds for probe-2 items 21-25 (no scores and no AUROC).
No AUROC, score, corruption statistic or other outcome field of probe-2 items 26 onward was read, printed or summarised by the
lead or passed to any agent. The statistician and the red team say they opened nothing under runs/P2-PROBE-02.
Shlok has not seen M1 outputs either (he was away). His co-attestation is requested in the status for his review.

## Extension (2026-10-28 ~15:30 IST): the 10:26 stop investigation (red-team A3 condition C3-6)
M1 stopped at 10:26 (watchdog, whole-GPU 10,509 MiB > 10,000 MiB; 106 of 200 items). From then until this extension the lead
read only:
- `runs/P2-PROBE-02/chunks.jsonl` (last 3 lines: soft-deadline, chunk-start health, guard_stop), `driver.log` via the driver
  output file, the file listing of the run directory, and the tail of `stdout-chunk03.log` (library warnings and the
  watchdog line);
- the telemetry CSVs of the run (nvidia-smi time series: memory, temperature, power, clocks, utilisation), summarised as
  per-file maxima and the samples above 9,000 MiB;
- `items.jsonl` through one script that parsed every row (106 rows) but printed only the total row count and `idx`,
  `peak_gb`, `seconds` for rows with idx <= 25. Rows with idx >= 26 were parsed into memory and discarded; none of their
  fields was printed, summarised or passed to any agent. This is disclosed because the parse touched those rows.
- code (`exp_p2/run_probe2.py`, `exp_p2/gate/watchdog.py`, `guards.py`) and system state (boot time, nvidia-smi, process list).
No AUROC, score, corruption statistic or other outcome field of probe-2 items 26 onward was read. Agents dispatched since then
were told not to open items with idx > 25 or arrays; the FOIL L7 data-steward reports reading only the `image_id` field of
`runs/P2-PROBE-01|02/selection.json` (the input list, not outputs).
Shlok's own co-attestation is still pending (requested in `research/paper2/CONFIRM-EVENING-2026-10-28.md`); until it exists the
statement above about Shlok is the lead's belief, not his attestation.

## Shlok's co-attestation (2026-10-28 19:22 IST, typed by Shlok in the Paper 2 lead session, verbatim)
"have not looked at any M1 (probe 2) results from item 26 onward."
Recorded for SAP A3b.5 item 10 (d) and card v4 section 5 row 3b. It was given while the M1 resume (items 106-199, started
19:15 IST) was running and before any M1 analysis. This section is appended after the SHA-256 recorded in A3b and card v4;
those hashes cover the file up to the 14:45 extension.
