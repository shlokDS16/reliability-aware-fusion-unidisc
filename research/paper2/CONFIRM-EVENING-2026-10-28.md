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
