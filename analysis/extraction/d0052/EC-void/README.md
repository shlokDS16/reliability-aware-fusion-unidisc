# Voided EC sessions (not read by rq_analysis.py, which reads EC/*/*.jsonl only)

- ecx002b (M15840, 2026-10-21): ft_isolation_check failed. One Grep call carried a mistyped folder segment
  (0839c9f4-4e83-4067-9ebf-... for ...-9eb8-...). That path does not exist (checked with ls), the call returned "path
  does not exist" and read nothing; model check passed (fable 106). The brief voids a session for any mistyped or
  outside path, so the record is kept here for reference only and M15840 is re-adjudicated as ecx002c.
