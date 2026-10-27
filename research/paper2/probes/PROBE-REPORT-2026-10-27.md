# Paper 2 feasibility probes, 2026-10-27

Model: UniDisc 1.4B (aswerdlow/unidisc_interleaved), 512 px, bf16, on the 12 GB laptop GPU. Code: `exp_p2/`.
All numbers below are copied from `runs/P2-PROBE-01/summary.json` (made by `python -m exp_p2.analyze_probe1`) or from the
telemetry CSVs named. Status: exploratory feasibility probes, not preregistered results.

## Probe 1: does UniDisc's masked likelihood tell a true caption from a wrong one? (P2-PROBE-01, complete)

Setup: 300 COCO images. Each image is scored with its own caption and with the caption of another image, chosen by a
derangement (seed 1303), so chance is 0.5. "Accuracy" is the share of the 300 images where the true caption gets the higher
score. 95% intervals come from a bootstrap with 10,000 resamples. Each item takes 58 network passes.

| Score | Accuracy | 95% CI | Role |
|---|---|---|---|
| a_text: mean log p(caption tokens given image), 8 complementary masks | 0.730 | 0.680-0.777 | primary |
| b_image: mean log p(image tokens given caption), 8 complementary masks | 0.783 | 0.737-0.830 | primary |
| a_plus_b: sum of the two | 0.733 | 0.683-0.780 | primary |
| control: a_text with the whole image masked (caption prior only) | 0.497 | 0.440-0.553 | control |
| a_pmi: a_text minus its image-masked null | 0.940 | 0.910-0.967 | exploratory |
| a_full: all caption tokens masked in one pass | 0.943 | 0.917-0.967 | exploratory |
| a_full_pmi: a_full minus its image-masked null | 0.990 | 0.977-1.000 | exploratory |
| b_k2: image direction, 2 passes | 0.827 | 0.783-0.867 | exploratory |
| b_full: image direction, all 1024 image tokens masked in one pass | 0.843 | 0.803-0.883 | exploratory |
| a_full_pmi + b_full | 0.990 | 0.977-1.000 | exploratory |

Kill rule (both primary directions at 0.55 or below): **not met**. The likelihood signal is clearly present in both directions.

Readings, flagged as exploratory:
- The caption-prior control sits at chance (0.497), so the text-direction signal comes from the image, not from caption
  length or wording.
- Subtracting the image-masked null (PMI) raises text-direction accuracy from 0.730 to 0.940, and to 0.990 with full masking.
  This supports using a prior-normalised score in GATE (red-team change 1) and C's PMI machinery.
- The image direction has a tiny per-token margin (mean difference +0.005 nats) but still ranks 0.783 correctly. The scale
  per token is small, which matters for any threshold (the CFAR gate in GATE).
- Masking everything in one pass (a_full, b_full) beat 8 complementary masks here. The K-mask design in ideas A and C should be
  re-checked rather than assumed.

Cost: median 7.0 s per item (mean 9.7 s; one item took 635 s; the crash diagnosis traced it to a system sleep at 18:44:40, not a GPU stall), 0.80 GPU-hours of item time for 300
items. Peak PyTorch allocation 8.2 GB. Highest whole-GPU memory in telemetry: 8,788 MiB (chunk 4). Highest temperature: 67 C.

## Probe 2: token-reliability AUROC under corruption (P2-PROBE-02, stopped at 20 of 200 items by a system crash)

The driver started at 20:12. At 20:20:21 the laptop crashed (blue screen, bugcheck 0x116 VIDEO_TDR_FAILURE, status
0xC000009A insufficient resources; minidump C:\Windows\Minidump\102726-18031-01.dmp; reboot 20:20:50). The last telemetry line
(`runs/P2-PROBE-02/telemetry-chunk01.csv`, 20:20:24) shows whole-GPU memory jumping from 7,031 to 12,087 MiB within 5 s, at
64 C or below. The PyTorch peak for the 20 finished items was 8.27 GB, so either the item in progress allocated much more, or
another process took GPU memory at that moment. The log cannot tell which. This is the seventh unexpected restart since 2026-10-14 (memory note laptop-gpu-crashes), and the second
0x116 after the one on 2026-10-16; it is the first with a project GPU job at full memory.

The 20 rows are kept in `runs/P2-PROBE-02/items.jsonl` but are too few to analyse. No AUROC is reported.

Before probe 2 restarts (it needs Shlok's go-ahead):
- cap PyTorch memory, e.g. `torch.cuda.set_per_process_memory_fraction(0.75)`, so an over-allocation raises an out-of-memory
  error instead of filling the card;
- add a gate on whole-GPU memory during the chunk (stop above about 10.5 GB), not only before it;
- close GPU-using apps (Ollama, the ChatGPT/Codex app) during the run.

### Second crash (2026-10-27 ~23:25 IST, after the safeguards)
With Shlok's go-ahead, probe 2 restarted at 23:22:51 with the 75% PyTorch memory cap and the per-item GPU memory stop, and with
Ollama closed (the ChatGPT/Codex app was still in the tray but held no GPU context). It finished item 20 (peak 8.2 GB), then
whole-GPU memory jumped from 4,566 to 12,087 MiB between 23:24:53 and 23:24:58 (`runs/P2-PROBE-02/telemetry-chunk00.csv`).
The laptop crashed with the same bugcheck, 0x116, status c000009a; reboot at 23:25:25. The PyTorch cap did not stop it, so the
memory that filled the card was outside PyTorch's caching allocator, or was the driver's own reset. The root cause is unknown.
Probe 1 ran 300 items on the same model without this. Probe 2 is on hold (`runs/P2-PROBE-02/HOLD.txt`; exp_p2/driver.py refuses
to run while it exists). Next steps need Shlok: a clean NVIDIA driver reinstall (his call), and/or a CPU-side diagnosis of what
probe 2 does differently from probe 1 before any GPU retry.

### Crash diagnosis (2026-10-28)
See `PROBE2-CRASH-DIAGNOSIS-2026-10-28.md`. Leading hypothesis (not confirmed; the minidumps need an elevated debugger): an NVIDIA
driver TDR (driver 595.71, Blackwell), not a probe 2 allocation. Both crashes share one Windows error bucket and each followed a
watchdog event (117). The first came 106 s after the laptop switched from AC to battery. Probe 2's per-item GPU work is close to
probe 1's. The proposed staged GPU test (with Shlok present, on AC) starts with a probe 1 control to separate environment from code.

## What this means for the ideas
Probe 1 supports the premise shared by A (GATE) and C: UniDisc's masked likelihood carries a usable, image-grounded signal in
both directions. It does not yet test GATE's own claim, that per-token scores find corrupted input tokens. That was probe 2.
