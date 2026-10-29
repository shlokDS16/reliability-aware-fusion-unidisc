# Paper 2: what needs Shlok's confirmation (evening of Wed 28 Oct 2026)

**State at ~17:00 IST.** Everything in the plan is built and audited on the CPU: swap in M4, S2 re-infill, FOIL family B,
the image-corruption suite, the Omni-Diffusion adapter, and the E-dec/E-pred analyses. There are 536 CPU tests, all passing. The
gate-auditor gives a plain PASS at code 9c4e1e25, and the red team signed SAP addenda A3/A3b with conditions. Card v4, which pins all of this, is being written. The GPU starts as soon as you answer items 1 and 2.

Reply "all recommended" to accept every recommendation below, or give a number and your choice.
Items 1 and 2 block the GPU; the rest can wait until Thursday morning.

## 1. Resume the GPU after the M1 guard stop (blocks all GPU work)
**What happened.** M1 (probe-2 completion) ran unattended from 09:56. It stopped at 10:26 with 106 of 200 items done: the
watchdog read 10,509 MiB of whole-GPU memory against its 10,000 MiB first-item ceiling, 0.2 s into the first item of chunk 3
(`runs/P2-PROBE-02/chunks.jsonl`, last line). The guard worked: no crash, no reboot (boot time still 27 Oct 23:25), and no
crash events since. By the approved rule a guard stop halts GPU work until you return, so the GPU has been idle since 10:26.

**Why it happened (telemetry only, no outcomes read).** On the open items 0-25, each item's peak allocated memory is either about
4.1 GB or about 8.2 GB (`peak_gb` in `items.jsonl`; items 0, 4, 20 and 21 are at 8.2-8.27 GB). Add the CUDA context and about
1.3 GB held by other apps, and an 8.2 GB item reaches about 10.5 GB of whole-GPU memory for under a second. The 1 s nvidia-smi
log never showed more than 7,453 MiB today, so these peaks are short. With the current ceilings (10,000 first item, 9,000
after, rise 1,500 MiB per second) any sample that lands on such a peak stops the run, so stops will recur at random in every
stage (M1-M5, S2, FOIL), not only in M1.

**Recommendation (D2/D3, CLI flags, no code change):** keep the PyTorch cap at 0.75 (about 9,170 MiB for our process, enforced by
PyTorch, which raises an out-of-memory error rather than fill the card); set both whole-GPU ceilings to **11,000 MiB** (the card
has 12,227 MiB; yesterday's crashes came at 12,087 MiB, i.e. a full card) and the rise rule to **4,500 MiB**, so that a
normal 4.1 to 8.2 GB step does not trip it but a jump towards a full card still does. Temperature limit 80 C, charger check and
the crash-log check stay as they are. Lowering the cap instead is not recommended: 0.70 leaves about 8,560 MiB, too close to the
8.2 GB items. Closing other GPU apps before the runs lowers the 1.3 GB baseline further.

Your answer: yes / other values.

## 2. GPU runs tonight and overnight, unattended under the guards (D8)
You said "Yes, guarded" this morning. Confirm it covers tonight and the night: M1 remainder (94 items, about 35-40 min wall, an estimate from
today's chunk rates of 37-39 items per 12.5 min chunk), then M1 detection stage, M2 + M3, M4 with patch/swap, M5, S2, FOIL, Omni timing, Omni R, suite
(cut order: suite first, S2 last). Any guard stop or crash-log event still halts everything until you return.
Please keep the laptop open and on the charger; the GPU jobs run locally, so the 23:00 / 00:15 network switch does not
stop a running stage, but my session needs the network to launch the next one.

Your answer: yes / no / only until a time.

## 3. Co-attestation (in your own words)
For the blinding record (`prereg/LEAD-ATTESTATION-A2-2026-10-28.md`): please state that you have not looked at any probe-2
(M1) output from item 26 onward. Your own sentence, not a copy of this one.

## 4. Results freeze time (D5)
Proposed earlier: Fri 30 Oct 12:00. The GPU will have been idle from 10:26 until your answer (about 8 hours if you answer at 18:30). **Recommendation: Fri 30 Oct 18:00**, with
Saturday 31 for figures, results text and final audits. Anything not finished by the freeze is cut in the cut order above.

## 5. JPEG denoiser setting (D17, before M4)
One denoiser setting for all corruptions helps on noise (+5.3 dB) but hurts JPEG (-1.7 dB). **Recommendation: (a) keep the one
setting** and word the JPEG result as "against an aggressive denoiser that harms the image" (honest, needs no new rule).
Alternatives: (b) a per-corruption setting by a new dated rule before M4; (c) drop the denoiser baseline on JPEG.

## 6. Second mask-seed check (D4)
50 headroom items with a second mask seed, descriptive only, after M4 and only if the GPU is idle. **Recommendation: yes**
(about 0.2 GPU-h, estimate; it answers the reviewer question "does the gate depend on the random mask partition?"). Its code is not built yet; on your yes I build and audit it while M4 runs, so it costs no GPU wait.

## 7. Fallback if the main test is null (D18)
The preregistration fixes that a null is reported as a null and no secondary family can rescue it (A2b). The open question is
what we submit. **Recommendation:** if P is null but S2, PS and FOIL are informative, submit to Information Fusion as a
"when does input gating help" article with the null stated in the abstract; if the GPU cannot finish M4 by the freeze,
move the deadline rather than submit without M4. Alternatives: a short CPU-only feasibility note, or another venue.

## 8. GPU timeline and the S2 size (all estimates from the implementer reports, not measured on these stages)
Busy GPU time, then wall time at the 0.5 duty cycle (the guard pauses as long as each item runs):
| Stage | Busy GPU-h | Wall h |
|---|---|---|
| M1 remainder (94 items) | about 0.3 | about 0.6 |
| M1 detection stage, M2, M3, M4 (with patch and swap), M5 | about 2.7 | about 5.4 |
| S2 re-infill, n = 300, three arms (GATE, random best-of-4, changed-code) | about 3.9 | about 8 |
| FOIL family B, n = 300 | about 0.13 | about 0.3 |
| imagecorruptions suite | 0.5-0.7 | 1.0-1.4 |
| Omni-Diffusion timing + family R | 0.6-1.6 | 1.2-3.2 |
| **Total** | **about 8-9** | **about 16-19** |
If you answer by about 19:00 tonight and nothing stops, the GPU work ends around midday to early afternoon Thursday, leaving
over a day before a Friday 18:00 freeze. **Recommendation: keep all three S2 arms**; if a stop costs time, the first cut is
the changed-code arm (S2 drops to about 2.6 GPU-h), then the cut order above.

## 9. Red-team conditions that need your words (A3 signature, `prereg/RED-TEAM-SIGNOFF-2026-10-28.md`)
- **n = 300 at the updated cost.** This morning I quoted "about +1 GPU-h" for raising S2 and FOIL to n = 300. The implementer's
  estimate for S2 alone is about +1.95 GPU-h (about +4 h wall). The red team signs n = 300 only if you confirm it at this cost.
  **Recommendation: yes** (at n = 150 S2 cannot detect gains below about 8-11 points; at n = 300 about 4-8 points, derived
  with assumed discordance rates, `runs/P2-GATE-A3/a3_power_output.txt`).
- **Item 3 above (co-attestation)** is also a condition of the signature.

## Already decided (no answer needed)
S2 re-infill is MUST; S2 and FOIL at n = 300; swap, FOIL, Omni adapter and suite are being built today (CPU only); then a
gate-auditor check and card v4 pin the code and SAP before the first new item.

## Shlok's answer (2026-10-28 19:14 IST, in this session, verbatim): "All recommended"
Dated row (card v4 section 5; A3b.6). Read as the recommendation of each item:
1. Guard settings: `--max-used-first-mib 11000 --max-used-mib 11000 --max-rise-mib 4500 --mem-frac 0.75` (MEM for every
   non-Omni stage; Omni stages keep their committed values).
2. Unattended GPU runs under the guards tonight and overnight: yes.
4. Results freeze: Fri 30 Oct 2026 18:00 IST.
5. D17: (a) keep the one denoiser setting; JPEG worded "against an aggressive denoiser that harms the image".
6. D4: yes; code to be built, audited and pinned in a dated row before it runs, after M4, only if the GPU is idle.
7. D18: if P is null but S2, PS and FOIL are informative, submit to Information Fusion as a "when does input gating help"
   article with the null in the abstract; if M4 cannot finish by the freeze, move the deadline rather than submit without M4.
8. S2: keep all three arms; the changed-code arm is the first cut.
9. n = 300 for S2 and FOIL at the updated cost (S2 about +1.95 GPU-h, +4 h wall): yes.
3. **Co-attestation: NOT given.** "All recommended" does not contain his own sentence, so it is not recorded as one. Asked
   again; if still absent when M1 is analysed, the lead writes the dated absence (card v4 section 5 row 3b).

## 10. M2 slow-item guard stop (20:07 IST) and Shlok's answer
**What happened.** M2 (calibration, n = 300) stopped at 20:07 with 106 of 300 rows done: `runs/P2-GATE-M2/chunks.jsonl`
records `guard_stop`, reason "slow_item 3.0s > 2.0x median 1.5s", idx 105. Diagnosis (telemetry only): GPU 52-63 C,
6.9 GB, throttle reason only the software power cap, no crash events, boot time unchanged (27 Oct 23:25); item 105 is
ordinary (13 caption tokens, peak 4.58 GB). Not caused by the lead's M1 analysis, which finished at 20:00:11.

**Question put to Shlok (wrap-up box):** "Relaunch M2 and use a 3x slow-item limit overnight?"

**Shlok's answer (2026-10-28, in this session, verbatim): "Yes, both"**
Read as:
1. Relaunch M2 unchanged (same MEM flags, same 2x rule); it resumes at row 106. Done at 21:40 IST (first run's driver
   log kept as `runs/P2-GATE-M2.driver.run1.out`).
2. Add `--slow-factor` / `--slow-min-s` CLI flags with defaults unchanged (2.0 / 1.0), gate-auditor delta check, and a
   dated card v4 amendment row pinning the new code SHA; overnight non-Omni stages then run with
   `--slow-factor 3 --slow-min-s 2`. Until that row exists, every stage runs with the defaults.

## 11. Second M2 slow-item stop (21:45 IST): GPU halted until Shlok answers
`runs/P2-GATE-M2/chunks.jsonl`: `guard_stop`, "slow_item 4.4s > 2.0x median 1.8s", idx 113; 114 of 300 rows done
(driver log `runs/P2-GATE-M2.driver.out`). Telemetry 21:45:05-21:45:16: GPU utilisation 0 % and memory flat at
5,290 MiB through most of the item, i.e. the GPU waited on the host. free_ram_gb fell to 4.15 (system 31.4 GB total);
at the time the lead had three CPU agents running (a new git worktree checkout, targeted pytest, PDF reading) and
Defender was active. No crash events, boot time unchanged (27 Oct 23:25), temperature 50-59 C.
Both stops (idx 105: 3.0 s vs 1.5 s; idx 113: 4.4 s vs 1.8 s) are below the proposed 3x / 2 s rule (4.5 s, 5.4 s).
By the standing rule no relaunch until Shlok answers. Question put: relaunch M2 with the 3x / 2 s rule once the
flag is audited and pinned, and keep CPU-heavy agent work off the machine while GPU stages run.

**Shlok's answer to section 11 (2026-10-28 ~22:40 IST, verbatim): "Go with what you think is the best for our project among these two options."**
(Options put: "Yes, relaunch" with the 3x / 2 s rule; "Wait for red-team" on the UniDisc time-input question.)
Lead's choice under that delegation: relaunch M2 now with `--slow-factor 3 --slow-min-s 2` (card v4 row A-2; code pin
f2f7b2e1, row A-1); M2's remaining 186 items are about 15 min of GPU and are stored unchanged whatever the verdict.
**M3 and later GPU stages are held** until the red-team's verdict on whether `sigma=None` is UniDisc's intended
inference path; a defect would need an audited fix before any stage that depends on the scores.

Erratum (lead): the time of the answer above is about 22:05 IST, not ~22:40; the M2 relaunch logged 22:06:29 (`runs/P2-GATE-M2.driver.out`; earlier log kept as `P2-GATE-M2.driver.run2.out`). Card v4 rows A-1/A-2 say ~22:30; they were committed shortly before 22:05.

## 12. D18 reading (SAP addendum A4.2.6, C4-2), before `analysis_m4`
Question put (wrap-up box, 2026-10-29 ~00:05 IST): "Under a null main result, keep 'when does gating help' out of the headline (reading 1)?"
**Shlok's answer (2026-10-29 ~00:10 IST, in this session, verbatim): "Done going to sleep continue. Choose whatever alleviate. We want the best paper till date proposed in any journal. Take all the experts researcher to another level of ascension."**
Read as a delegation of the choice to the lead. Lead's choice under it: **reading 1** (the stricter, certainly inside AB.1, and the
one the A4 outcome book is written to): under a P-null label the phrase "when does input gating help" stays out of the title,
abstract, highlights, conclusion and the opening of 6.1, and is discussed only through the closed-form condition and the P table.
D18's submission condition stands verbatim, with the **status-only definition of "informative"** of A4.2.6 adopted (S2, PS and
FOIL each "informative" iff AD.11 status "run, formal"). No M4 value had been read (M4 at about 115 of 500, running).

## 13. Operations log (no decision needed)
- 2026-10-29 01:34 IST: M4 driver stopped with "max chunks reached" (default 12 chunks; exit 6; not a guard stop, no crash event) at 334/500. Relaunched 01:35 with `--max-chunks 30`, same flags; resumes at row 334, same item list (driver log of the first run kept as `runs/P2-GATE-M4.driver.run1.out`). Card v4 row 6 printed no `--max-chunks`; this is an operational setting, recorded for the deviations box.
- 2026-10-29 02:59:17 IST: Windows Update (MoUsoCoreWorker.exe, then TrustedInstaller.exe at 03:04:19) restarted the laptop to install Intel/Realtek/A-Volute/SunplusIT driver updates (System log Id 1074, 43/19). The M5 child was terminated at 02:59:18 (exit 0x40010004) after 1 of 100 items; telemetry normal up to then (53-59 C, 5,210 MiB). No Kernel-Power 41, BugCheck, WHEA or nvlddmkm event; NVIDIA driver unchanged at 595.71 (runs/env-2026-10-14/setup.md). Not a guard stop or crash of the job. M4 E-dec/E-pred outputs had been written at 02:59 and were committed after the restart (cd0174ac). Shlok, 07:4x IST: "Restore everything and continue." Boot 03:04:59.
- 2026-10-29 08:13 IST: **M5 complete** (100/100, 08:11). coherence_report run with --mu from runs/P2-GATE-M5/mu_from_m4.json (script beside it). **A4.3.2 decision at the M5 boundary:** arm set logged first = three arms (I-GATE, I-RAND4, I-CHG; S2 run card 697af03a), so W_S2 = 8.0 wall-h; t_now = 2026-10-29 08:13; t_now + 0.3 h + 8.0 h + 2 h = Thu 29 Oct ~18:40 IST <= Fri 30 Oct 18:00 IST: **true**. Gate-auditor confirmation present (17500581). Order: row 10 (foil-fit), row 11 (foil-test), then 8a, 8, 9. analysis_foil analyze waits for the S2 table (rule 6). Deviations-box notes from the FOIL-first check (DCACHE null files; local generators in start-up checks and the 'fusion' seed child; citation run_gate_foil.py:1-149).
- 2026-10-29 08:29 IST: Shlok paused Windows Update until 4 Nov 2026 and set active hours (his words: "Updated pause until 4th of November. Active hours also set you can continue.").
- 2026-10-29 08:34 IST: FOIL test complete (298/300, 2 excluded) at 08:30. Pre-smoke crash-log check by hand: 0 crash-signature events since 03:04. **S2 smoke (row 8a) stopped at the pipeline self-check twice** (exit 2, before any item; image_tokens_frac_equal 0.9854 and 0.9844 < 0.99; M4 1.0, FOIL-FIT 0.999 on the same check). Not a guard stop or crash. Smoke outputs empty (no item ran). Diagnosis delegated (runs/P2-S2-SELFCHECK-DIAG, report research/paper2/method/S2-SELFCHECK-DIAG-2026-10-29.md); any fix goes through audit + pin row; the 0.99 rule is not changed. First attempt kept as runs/P2-GATE-S2-SMOKE.try1.
- 2026-10-29 09:02 IST: S2 smoke (row 8a) PASSED the self-check after fix A-5 (3 items: peak_gb 3.76, about 46 s each, 386 rows each; only these lists read). **S2 (row 8) launched 09:01** (n = 300, three arms, --max-chunks 60, MEM + slow rule), code 8d1bee3a. Expected about 7.7 wall-h. TMLR-format copy built in paper2-tmlr/ (f4519789) pending Shlok's venue choice; Elsevier version in paper2/ is the master.

## 14. Family H (SugarCrepe hard negatives): Shlok's go
Question put (2026-10-29 late morning): "Add the SugarCrepe hard-negative family tonight as a new preregistered test?" with the option text "Yes: add the SugarCrepe hard-negative family H as a new preregistered family (headroom stage first, then up to 300 test items), after S2 and before the suite. P stays the preregistered headline."
**Shlok's answer (2026-10-29 10:23 IST, verbatim): "Yes, add it"**. Read as: D-H1 go (A5.15); D-H3 GPU stages for H run under the same guards and unattended rules already approved (CONFIRM item 2, card A-2); D-H2 (H in the abstract) and D-H4 (patch/swap in H) take A5's stated defaults (H never in title, highlights or abstract; patch/swap as A5 drafts), since he gave no other instruction. Draft A5 committed 86064e57 before any H data.

## 15. Paper 2 retargeted to IEEE TNNLS (Shlok, 2026-10-29 12:25 IST)
Shlok verbatim (excerpt): "This TMLR is not even q1 dude. Let's make paper 2 for TNNLS itself. ... We have to propose the best paper till date in that journal. ... We need to provide something is not in existence with validated proofs. ... Deadline we can extent till sunday. ... We can even propose some limitation if present ... Follow the same prompts I gave on how to follow journal guidelines for paper build." Professor's advice relayed: top journals want critical reasoning why the proposed work is best even against corporate-level work; expect AI-based evaluation (Gemini/ChatGPT) to find issues. Read as: venue IEEE TNNLS (Full Paper, 10 + up to 5 paid pages; research/paper2/venue/TNNLS-DEEP-DIVE-2026-10-29.md); deadline Sun 1 Nov 2026; Paper 3 on hold; pipeline = research/paper2/MASTER-BRIEF-2026-10-27.md and memory paper-presentation-rules; AI only in the generative-AI declaration; a new validated method is required, the preregistered GATE study is kept and reported honestly.

## 16. TNNLS route (Shlok 2026-10-29 14:14 IST)
Shlok verbatim: "Two-three weeks is too much max by monday." Route B out; deadline Mon 2 Nov 2026 at the latest. Lead proceeds with Route C (recommended in-session after the learned-ceiling result bdc87e4e): learned reliability-aware evidence fusion (caption-withheld logistic-GAM token weights) as the new method, frozen on M4, confirmed on a fresh preregistered COCO fold (noise primary, held-out suite noise types, CLIP/SigLIP comparison), with the preregistered GATE study as motivation/analysis. Shlok may switch to Route A.
Shlok 2026-10-29 14:15 IST, verbatim: "Even tuesday morning after reset can contribute." Read as: final work may continue to Tue 3 Nov 2026 morning, using the weekly usage reset (Mon 2 Nov ~22:30 IST); heavy review/polish passes are scheduled after the reset.

## 17. D-H2, unattended H/Study 2 GPU runs, CLIP/SigLIP download (Shlok 2026-10-29 ~18:50 IST)
Questions put (this session, multiple-choice card) and Shlok's selected answers, verbatim:
1. "Family H (SugarCrepe hard negatives) is a late-added test. Keep it out of the title, abstract, highlights and conclusion (results section and supplement only)?" -> **"Yes, keep it out (Recommended)"**. D-H2 settled: H never in title, abstract, highlights or conclusion.
2. "Can the GPU stages for H3/H4 and Study 2 (rescore, about 2.5 h; L1, about 4 h; LG) run unattended overnight and over the weekend under the same guards (memory cap, 3x / 2 s slow-item stop, crash-log halt)?" -> **"Yes, unattended (Recommended)"**. Any guard stop or crash-log event still halts the GPU until Shlok answers.
3. "Can I download CLIP ViT-L/14 and SigLIP checkpoints (about 2-4 GB total from Hugging Face) for the descriptive baselines in Study 2?" -> **"Yes, download (Recommended)"**. Download in daytime, resumable, not near 23:00 / 00:15 IST.

## 18. Operations log (continued from section 13; no decision needed)
- 2026-10-29 18:45 IST: GPU idle (0 MiB, 50 C), code pin 725a1b5a clean, pre-launch check (card 1.4 at the A-6 pin) passes; AC on.
- 2026-10-29 ~18:50 IST: free RAM 3.2 GB, then 1.0-2.9 GB (psutil available 2.3 GB): another session's CPU job (Computer Networks paper 2, `analysis/incidents/replay.py`, 5 workers, `--min-free-gb 3.5`, started 18:14) holds about 7.5 GB private. GPU launch held until free RAM >= 6 GB (the M2 stop of 21:45 on 28 Oct coincided with 4.15 GB free). That session was messaged at ~18:55 to keep >= 6 GB free and off the GPU until Mon 2 Nov.
- 2026-10-29 18:54 IST: family H preconditions complete (card v4 row A-7, commits 8f1c338e, 3ecb55cb, 46e96660). Next: row 9 (S2 figures), then H3.
- 2026-10-29 18:56 IST: free RAM back to 6.7 GB (other session's job ended); pre-launch check passed; row 9 (S2 figures) launched with the run-card command (`--max-chunks 20`, MEM + slow rule).
- 2026-10-29 18:59 IST: row 9 COMPLETE: 10 figure items decoded (the preregistered subset of run_gate_s2.py FIG_FIRST/FIG_HARM after de-duplication; `effective_n.json` prints the driver's generic "real-tokenizer rule" reason, which does not apply here), chunk 0 exit 0, no guard stop. PNGs (62 MB) kept on disk, not committed.
- 2026-10-29 19:00 IST: A5.12 rule 1 checked: t_now + W_H3 0.75 + A_H3 0.5 + W_H4(200) 1.8 + A_H4 0.5 + M 2.0 h = Fri ~00:35 <= F Fri 30 Oct 18:00: H3 starts. H3 launched: `--stage h3 --max-chunks 10 --extra "--tbv auto <MEM> --slow-factor 3 --slow-min-s 2"`, unattended under D0085. C5-6: only driver chunk lines are read until the H4 analysis is committed.
- 2026-10-29 19:01 IST: D0087 (C6-1..C6-11 as the lead's dated row, A6.0 item 1) committed 19:01:18, after the H3 driver started (19:00:31) and before any H3 item row existed. Deviations box: the row's order relative to the H3 process start.
- 2026-10-29 19:23 IST: H3 COMPLETE (50/50; chunks exit 75, 75, 0; no guard stop, no crash event). `h3_gonogo decide` run at 19:23:51 (16 s after the last row; A_H3 0.5 h met): rule NO-GO (H-NOGO), test_fold 0, go false. **H4 is not run**; HJ, HN, HS take p = 1 (A5.5). Only n_rule, go and status were read; per-corruption H3 values not opened (C5-6). Next: Study 2 re-score (A6.10).
- 2026-10-29 19:24 IST: A6.10 rule 1 checked (re-score start by Mon 04:15): true. lrf-rescore launched: `--stage lrf-rescore --max-chunks 40 --extra "<MEM> --slow-factor 3 --slow-min-s 2"`, unattended (D0085); codebook and DI_n013 hashes equal the A6.2 table; pre-launch check passed; 7.7 GB RAM available.
- 2026-10-29 19:25 IST: CLIP/SigLIP size corrected: the pinned revisions are 1,631 MB (CLIP ViT-L/14 model.safetensors) + 3,349 MB (SigLIP so400m model.safetensors) = about 5.0 GB, not the 2-4 GB quoted in the CONFIRM 17 question; within the no-GB-limit download rule; only safetensors, configs and tokenizer files fetched (no flax/tf/bin duplicates), pinned revisions, resumable, started before the 23:00 network switch.
- 2026-10-29 19:30 IST: A6.2 steps 2-3 gate on the first 5 re-scored items x 4 conditions (`run_gate_lrf_rescore --check`): PASS, invariance max abs diff 0.0 (exact), positive control max abs diff 0.0 (tol 1e-5); no auditor row needed (runs/P2-LRF-RESCORE/gate_check_first5.json). Re-score continues; refreeze re-checks the gate on all rows.
- 2026-10-29 20:04 IST: CLIP ViT-L/14 (rev 32bd6428, 1.6 GB, done 19:38) and SigLIP so400m (rev 9fdffc58, 3.3 GB, done 20:04) in the HF cache at the pinned revisions; baselines run later with local_files_only (A6.6; never during a GPU stage).
- 2026-10-29 21:00 IST: LRF re-frozen (runs/P2-LRF-FROZEN-LFIX, model db7fdb4e..., 20:56-20:59, CPU, no accuracy computed); hash set committed with D0088 (A6.0 item 2), before the Mon 09:00 bound T_RF. Next: crossfit (CPU, GPU idle).
- 2026-10-29 21:06 IST: Study 2 fold built (4be79be8; 533 items; 2,503 images excluded by the C6-10 union; L8 pass) and L7 SIGNED by the data-steward (research/paper2/data/L7-SIGNOFF-LRF-FOLD-2026-10-29.md: union 2,526 ids = manifest, 0 of 533 in it). Steward notes for the deviations box: the builder collects image_id/image_ids only (neg/mismatch image ids are items of earlier folds and so already in the union; zero effect); 162 other runs/P2-* JSON files outside the C6-10 classes were not opened.
- 2026-10-29 21:17 IST: A6.10 rule 4 checked (L1 start by Mon 11:12): true. L1 launched: `--stage lrf-l1 --extra "<MEM> --slow-factor 3 --slow-min-s 2"` (n = n_L 450 from the plan file; --max-chunks 60 = STAGE_MAX_CHUNKS, passed explicitly), unattended (D0085). Available RAM 5.6 GB (one CPU worker of the Computer Networks paper 2 session, which now self-limits at 6 GB free; its remaining job is ~12 h, so waiting was not taken); GPU idle 47 C; pre-launch check passed.
- 2026-10-29 21:20 IST: **L1 first launch stopped at the pipeline self-check before any item** (21:19; exit 2, rows 0; image_tokens_frac_equal 0.98828 < 0.99; ids and modality equal). Not a guard stop or crash event. Same signature as the S2 smoke of 08:34 (per-process cuDNN algorithm choice in the VQ encoder, S2-SELFCHECK-DIAG; today's run_gate_m4 values: M4 1.0, H3 0.999, FOIL-TEST 0.995, re-score 1.0). The 'WindowsPath / NoneType' line in the log is start-up noise present at the same line in the M4 and H3 logs (lead grepped that single string in the H3 log; no H3 value read). Attempt kept as runs/P2-LRF-L1.try1 (+ driver logs). Under the S2-smoke precedent (one retry before a code fix) L1 is relaunched once, unchanged; if the self-check fails again, the A-5 deterministic-self-check fix is ported to run_gate_m4 through a gate-auditor delta audit and a card pin row (0.99 rule unchanged).
- 2026-10-29 21:24 IST: **L1 try 2 stopped at the self-check before any item** (21:21; 0.98926 < 0.99). Kept as runs/P2-LRF-L1.try2. Fix: run_gate_m4's self-check runs under deterministic cuDNN with the flags restored (port of the card A-5 fix; items unchanged, benchmark on as in M4; 0.99 rule unchanged), plus one test (fails on 725a1b5a, passes on the fix). Committed pending a gate-auditor delta audit; no GPU stage until the audit PASS and a card pin row A-8.
- 2026-10-29 21:33 IST: gate-auditor delta audit of 1871fe7d: PASS WITH FIXES (fix = card row A-8, added). Pin -> 1871fe7d. L1 relaunched as a fresh run (try 3) after the pre-launch check at the new pin.
- 2026-10-29 21:36 IST: L1 try 3 (fresh run id P2-LRF-L1 at pin 1871fe7d) passed the self-check (image_tokens_frac_equal 0.99902, deterministic backend) and started items (chunk 0: 4 rows). Unattended; expected completion ~01:00-01:30 Fri.
- 2026-10-29 22:43 IST: Shlok (chat, ~22:40): "I will be sleeping now, you continue working ... keep track of [tokens] along with gpu usage to prevent any restart today. There is one more paper being built nothing else. I will also switch to hotspot." Check at 22:41: L1 200/450, GPU 5.4 GB / 64 C, RAM 7.4 GB free, weekly 75%, Fable 0%. L1 is local (no network), so the hotspot switch does not affect it.
- 2026-10-29 22:43 IST: scorer pins file runs/P2-LRF-PINS/pins.json committed (fdfd8b97) before any L1 output is scored; values from the committed HASHES.json/spec.json, entry points at 1871fe7d. Dry run of the pin checks on P2-LRF-RESCORE (already-seen items, output to scratch, --n 5): all hash checks passed; the scorer then raised KeyError img (re-score rows are not M4-runner rows), as expected. No L1 file read.
- 2026-10-29 23:58 IST: **L1 COMPLETE** 23:56:49 (450/450, 12 chunks, no guard stop, no crash-log event; GPU idle after). Run files committed 6bc1650f (arrays untracked, SHA-256 manifest). Scored with the frozen LRF under the pins file: 1,800 lines, positive control 1,800/1,800 (0d580242). A6 analysis self-test ok, then run once: **L1 confirmed, branch A** (noise0.1 b 58, c 27, one-sided p 0.00051); L3 not rejected, L4 rejected at Holm 0.049, L-NI shown, L-LEN rejected (4a01f896). Gate-auditor verdict on the family L result pending. Next: LG after the pre-launch check.
