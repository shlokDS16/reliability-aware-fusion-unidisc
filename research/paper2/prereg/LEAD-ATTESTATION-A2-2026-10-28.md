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
