# Paper 2: what needs Shlok's confirmation (evening of Wed 28 Oct 2026)

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
(about 0.2 GPU-h, estimate; it answers the reviewer question "does the gate depend on the random mask partition?").

## 7. Fallback if the main test is null (D18)
The preregistration fixes that a null is reported as a null and no secondary family can rescue it (A2b). The open question is
what we submit. **Recommendation:** if P is null but S2, PS and FOIL are informative, submit to Information Fusion as a
"when does input gating help" article with the null stated in the abstract; if the GPU cannot finish M4 by the freeze,
move the deadline rather than submit without M4. Alternatives: a short CPU-only feasibility note, or another venue.

## Already decided (no answer needed)
S2 re-infill is MUST; S2 and FOIL at n = 300; swap, FOIL, Omni adapter and suite are being built today (CPU only); then a
gate-auditor check and card v4 pin the code and SAP before the first new item.
