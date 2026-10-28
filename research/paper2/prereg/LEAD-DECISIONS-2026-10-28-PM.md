# Lead decisions, Wed 28 Oct 2026 afternoon (Paper 2 lead; before any M2-M5, S2, FOIL, Omni or suite outcome)

Each decision below is the lead's, made before outcomes, and is to be cited by card v4. None changes a test in family P.

1. **Omni corruption resolution (A3.5).** Pixel corruptions are applied at 512 px with family P's seeds, then the image is
   tokenised at Omni's 256 px. Reason: Omni then sees exactly the corrupted pixels UniDisc sees. Cost, disclosed: JPEG and noise
   are attenuated by the downscale. `--corrupt-at 256` is not used.
2. **Omni adapter signing criteria T1-T3 (gate-auditor part 3, `GATE-CODE-AUDIT-A3-PART3-OMNI-2026-10-28.md`): accepted** as
   tightenings (allowed by A3b; the window closes before the timing stage). T1: check A5 floors mean_logp(s=1) >= -8.011 and
   top-1 >= 0.005. T2: pins and versions recorded in omni_env.json. T3: peak allocated memory during load and checks <= 7,000 MiB.
   T1 is applied as a separate signing check reading selfcheck.json, so `exp_p2/omni/checks.py` and its recorded hashes stay
   unchanged. HF_HUB_OFFLINE=1 is set for every Omni stage. Crash-event readings for Omni stages are recorded by the lead.
3. **A FAILED patch/swap chance bar does not block M3 or M4** (A3b.12 concern 3). The chance bar is the pre-registered
   detection pass/fail for PS (A2.5) and is reported as such; family P and the M4 schedule do not depend on it. The
   gate-auditor's match of `detect.py` / `analyze_gate_m1.py` to A3b.5a / A3b.12a (done, `GATE-CODE-AUDIT-A3-PART1`) must exist
   before M1 is analysed, and the M1 analysis runs before M3.
4. **Erratum.** The lead attestation extension heading says "~15:30 IST"; it was written and committed at 14:45 IST
   (48c7cece). Recorded also in SAP A3b.12; the attestation file stays unchanged because its hash is pinned.
5. **Guard settings and n = 300** are Shlok's decisions (`research/paper2/CONFIRM-EVENING-2026-10-28.md` items 1, 2 and 9). No
   GPU stage runs before his answer; S2 and FOIL-test do not start before a dated row records his n = 300 answer (A3b.6).
