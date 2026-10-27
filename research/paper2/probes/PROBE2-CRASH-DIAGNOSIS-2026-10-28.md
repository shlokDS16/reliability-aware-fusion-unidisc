# Probe 2 crash diagnosis (2026-10-28, CPU-side only)

Scope: read-only analysis. No GPU context created, no model loaded, no project code or system setting changed.
Observed = read from a file or log in this session. Hypothesis = inferred, not observed.

## 1. Verdict

Most likely cause (hypothesis, moderate-to-low confidence, about 50 percent): an NVIDIA Blackwell display-driver fault
(nvlddmkm, driver 595.71) on the idle-to-boost transition of the duty-cycled run, made more likely by an unstable power
supply (AC/battery flapping). It is not a probe-2-specific memory allocation. The "12,087 MiB" reading is most likely the
driver/WDDM accounting at the start of the failed reset, not a tensor that probe 2 allocated.

What is observed and what it excludes:

1. The two crashes are the same fault, not two causes. Both have fault bucket
   `0x116_TdrBCR:4:C000009A_Tdr:A_IMAGE_nvlddmkm.sys_Blackwell` (Application log, WER 1001 at 23:32:50 and 21:04:27), and each
   is preceded by a LiveKernelEvent 117 (WATCHDOG dump `WATCHDOG-20261027-2020.dmp` for 20:20, `WATCHDOG-20261027-2324.dmp`
   for 23:24). So the sequence is: GPU stops answering -> dxgkrnl watchdog (117) -> reset fails with c000009a -> 0x116.
2. "A kernel longer than the TDR delay" is excluded. HKLM TdrDelay = 10 and TdrDdiDelay = 10 (read-only registry query), already
   5x the 2 s default, and every kernel here is milliseconds (a batch-4 forward at 1.1k tokens is about 0.44 s; whole item 7.5-10 s,
   `items.jsonl`). A 10 s stall is a hang, not a long kernel.
3. The reading cannot be this process's allocations in crash 2. Telemetry row 0 of the second run shows memory.used = 0 MiB
   (`telemetry-chunk00.csv`, 23:22:51), so no other client held VRAM at start. With `set_per_process_memory_fraction(0.75)` PyTorch
   cannot hold more than 0.75 x 12,227 MiB = 9,170 MiB, and the CUDA context adds roughly 0.5-1 GB. That is at most about 10,000 MiB,
   short of 12,087 MiB. At least 2 GB must come from outside the PyTorch allocator (driver, another process, or the reset path).
   Both crashes read exactly 12,087 MiB. Different workload allocations would not land on the same number twice; "all free
   memory taken" (12,227 total minus about 140) does.
4. Probe 2 does not run heavier or different GPU math than probe 1 at the allocator level (details in section 3), and the failing
   item is not deterministic: item 20 crashed in the first run and then completed in the second run (peak 8.2 GB, 9.7 s).

## 2. Ranked hypotheses

| # | Hypothesis | Evidence for | Evidence against / unknown | Status |
|---|---|---|---|---|
| H1 | Driver/GPU fault (nvlddmkm 595.71, Blackwell) triggered by the idle-to-boost ramp, aggravated by power-delivery instability | Same WER bucket twice plus 117 watchdog events (above). `clocks.sm` 180 MHz and 11 W in each sleep gap, then 2,100-2,535 MHz and 92-105 W within one 5 s sample; the last sample before each crash is such a ramp-up (crash 1: 20:20:19 idle 9.5 W P5 -> 20:20:24 105 W 2,535 MHz, the highest clock in that file; crash 2: 23:24:48 11 W -> 23:24:53 33.8 W/2,752 MHz/85 % -> 23:24:58 92.9 W). Crash 1 came 106 s after an AC->battery switch (see H2). Same driver-bucket history: 10-16 0x116 with only a browser running, eight crashes since 10-14, three with no project GPU job. | Probe 1 made the same ramps about 600 times without a crash (300 items, 0.80 GPU-hours). So the per-ramp risk is not uniform; something environmental changes it. | Unproven; the minidumps are not readable (see section 6). |
| H2 | Power-supply transition: AC lost/regained shortly before the fault | `Kernel-Power 105 Power source change` at 20:18:38, battery report: Active Battery 45 % at 20:18:38. Telemetry shows the GPU power cap drop at exactly that time: bursts ~95 W/2,300 MHz before, 57-64 W/1,460-1,780 MHz with throttle reason 0x4 (SW power cap) after (`telemetry-chunk01.csv` from 20:18:42), items 15-19 slowed from 7.6 s to 10.2-10.4 s. The crash sample (105 W/2,535 MHz) shows the cap lifted again, i.e. AC likely returned in the last seconds. Before that the machine had been flapping: on battery from 18:54:50 (96 %) down to 9 % at 19:48:18 (during probe 1), four AC/battery changes 19:57:38-19:58:10. | Crash 2 has no logged power event (the battery report shows AC 21:01:17 to 23:20, last entry 5 min before the fault; the report's timestamps lag the crash, so a late event may not have been written). Probe 1 ran 53 min on battery at a 60 W cap without a crash, so battery operation alone is not fatal, a transition may be. | Observed for crash 1; unobserved for crash 2. |
| H3 | Another GPU client (Chrome/Electron GPU process, NVIDIA Overlay.exe, Codex app, Ollama, another session) took VRAM and oversubscribed WDDM | Whole-GPU memory is what nvidia-smi reports, so a 7.5 GB grab by a second process fits the numbers. Ollama is known to interfere: probe 1 telemetry is `NA` for 77 samples (16:38:10-16:44:32) while the job kept finishing items normally (items 31-57 at 6.5-8 s), and WER logged `ollama.exe` / `ollama app.exe` RADAR_PRE_LEAK at 16:38:32 and 16:43:37. NVIDIA Overlay.exe instances are running. | Crash 2 had Ollama closed (PROBE-REPORT) and a zero-memory start. `ollama.pid` was last written 15:54 and no ollama process exists after the reboots, so Ollama was probably not running at 23:24 (inferred). No other project's GPU telemetry or log was found modified in the two windows (search was partial: depth-limited, the second pass did not finish). A second client needing 7.5 GB inside 5 s, twice, is a coincidence. | Not excluded; cannot be tested after the fact. |
| H4 | Non-allocator GPU memory in this process (cuDNN/cuBLAS internal buffers, CUDA local-memory pool for a kernel with a large per-thread stack, NVRTC/JIT, cuDNN SDPA plan building) | It explains why the cap did not help. The first item of every chunk peaks at 8.2 GB allocated vs 4.11 GB steady (items 0, 4, 20; probe 1 items 7, 58, 109, ...), and whole-GPU memory then reached 9,611 MiB (`telemetry-chunk01.csv`, 20:15:50) with PyTorch's own number at 8.27 GB: the VQ encoder/decoder first-call workspace is a real multi-GB transient. | That transient is identical in probe 1 (max 8,788 MiB). The crash items were not first items in crash 1 (item 20 was the 17th after load) and the same item 20 ran clean later. No code in probe 2 launches a kernel that probe 1 does not (section 3). | Low. |
| H5 | Probe-2-specific input shape or content (logits size, noise/JPEG images, repeated token ids) | The only per-item additions are 3 VQ encodes instead of 1, a batch-1 prior pass, caption-masked passes and `np.savez_compressed`. | Item 20 was already clean on retry; caption length of the crash item 20 (13 tokens) had been seen 4 times in that process, so a "new sequence length" cuDNN plan is not the trigger in crash 1. All token ids are in range (codes < 16,384, ids < 48,385, gather indices < 16,384). | Refuted for deterministic triggers. |
| H6 | Hypervisor/VBS interaction | VBS enabled with "VSM Required" (Kernel-Boot 153), WSL running, 10-14 crash was HYPERVISOR_ERROR 0x20001. | No direct evidence for these two. | Background risk only. |

Not a cause: temperature (at most 64 C in both telemetry files; the guard threshold is 85 C), system RAM (free 5-9 GB in
`items.jsonl`; commit 47-55 GB free), sleep (the 635 s "stall" at probe 1 item 140 is a system sleep: `Kernel-Power 187
SetSuspendState` at 18:44:40, resume 18:44:51, clock jump 597,696 ms at 18:54:49; the guard's "timed out after -584.875 seconds"
is the same event. PROBE-REPORT line 38 should say sleep, not GPU stall).

## 3. Item-level comparison, probe 1 vs probe 2 (what differs)

Same: model, loader, bf16 backbone, SDPA patch (full attention, no mask), batch size 4, sequence length about 1.1k, steady-state
PyTorch peak (4.0-4.1 GB in both: `items.jsonl` `peak_gb`), per-item busy time (probe 1 median 7.0 s, probe 2 7.5-10.4 s), duty 0.5,
guard, driver, temperatures, power maximum (probe 1 113 W, probe 2 105 W).

Different (`exp_p2/run_probe2.py`):
- 16 forward rows per corruption x 4 corruptions = 64 batch-4 rows plus one batch-1 prior pass per item (line 163), versus about
  58 rows per item in probe 1 (29 specs x 2 captions; `run_probe1.py` `score_caption`). Same order of GPU work.
- 3 VQ encodes per item (clean, jpeg, noise; lines 159, 169 via `corrupt`) instead of 1 (`run_probe1.py` line 130). VQ-16 encoder
  runs in fp32 at 512 x 512 (`image_tokenizers.py` lines 196-237, autocast disabled). More fp32 conv time, but same shapes as the
  clean image, so no new cuDNN plans.
- `r_original` passes also mask the whole caption (`extra=cap`, line 88-89); only token content differs.
- VQ decode runs for items 0-5 only (lines 183-187), so it is not involved in items 20/21.
- Largest new tensors: `lp_all` [1024, 16384] fp32 = 64 MiB (line 163), log-softmax slices [128, 16384] fp32 = 8 MiB, logits
  [4, ~1.1k, 48,385] bf16 about 0.43 GB. None approaches GB scale beyond what probe 1 already allocates. `whole-GPU plateau`
  is higher in probe 2 (7,031 MiB vs 4,633-5,427 MiB in probe 1), about 2 GB more reserved-but-unallocated memory (allocator
  caching of the extra 64 MiB blocks, hypothesis), which narrows headroom to about 5 GB but does not explain a jump to full.
- `torch.cuda.mem_get_info()` per item (line 149) exists only in the crash-2 version; crash 1 had no such call, so it is not
  the trigger.
- New CPU work per item (savez_compressed, JPEG, auroc loops): raises CPU package power at the same moments the GPU ramps
  (hypothesis for shared-power-budget laptops).

## 4. Proposed safer probe 2 configuration (proposal only; not applied)

The code cannot remove a driver fault, so the diff is about (a) never starting a GPU burst when power is unstable, (b) removing
big idle-to-boost swings, (c) catching a runaway earlier, (d) leaving evidence.

Process steps for Shlok (system changes are his call; I changed none):
1. Run only on the original AC adapter, plugged into a stable outlet, battery at its 80 % cap; no GPU run if `Power source change`
   events appear in the last 30 min (`Get-WinEvent -FilterHashtable @{LogName='System';Id=105}`).
2. Quit Ollama, the Codex/ChatGPT app, Chrome, NVIDIA Overlay and the NVIDIA app before the run; confirm `nvidia-smi` shows 0
   compute processes and under 700 MiB used.
3. Optional, needs admin and is a driver setting: lock the SM clock range so the GPU does not swing 180 -> 2,500 MHz
   (`nvidia-smi -lgc <min>,<max>` with a modest max, and optionally `-pl`). Verify the exact flags on this driver first.
4. Run `!analyze -v` on `C:\Windows\Minidump\102726-16296-01.dmp` and `102726-18031-01.dmp` from an elevated WinDbg to read
   bugcheck arguments (needs an install; none exists here).

Code diff (illustrative; `exp_p2/run_probe2.py`):

```diff
+import ctypes
 ...
-MEM_FRAC, MAX_GPU_USED_MIB = 0.75, 10750.0
+MEM_FRAC, MAX_GPU_USED_MIB = 0.60, 9000.0       # first-item VQ transient reached 8.27 GB allocated; keep its headroom explicit
+FIRST_ITEM_MAX_MIB = 10000.0                    # only for the first item of a chunk (observed 9,611 MiB)
+
+def on_ac() -> bool:
+    class SPS(ctypes.Structure):
+        _fields_ = [("AC", ctypes.c_ubyte), ("Flag", ctypes.c_ubyte), ("Pct", ctypes.c_ubyte), ("Sav", ctypes.c_ubyte),
+                    ("Life", ctypes.c_ulong), ("Full", ctypes.c_ulong)]
+    s = SPS()
+    ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s))
+    return s.AC == 1
 ...
     for i in range(a.n):
         if i in done: continue
+        if not on_ac():                                    # H2: never start a burst on battery or right after a flap
+            common.append_jsonl(run / "chunks.jsonl", dict(event="power_stop", t=time.time()))
+            return EXIT_MORE_WORK
         ...
         free_b, total_b = torch.cuda.mem_get_info()
-        if (total_b - free_b) / 2**20 > MAX_GPU_USED_MIB:
+        if (total_b - free_b) / 2**20 > (FIRST_ITEM_MAX_MIB if n_new == 0 else MAX_GPU_USED_MIB):
```

Plus, in `exp_p2/driver.py` / `tools/gpu_guard.py` (not shown): sample every 1 s instead of 5 s (`--every 1`) and log `clocks_throttle_reasons.active`,
`power.draw`, `pcie.link.gen.current`; refuse to relaunch if System log has Id 105 within 30 min, or WER 117/116 since the last
launch; between chunks check `Get-WinEvent` for LiveKernelEvent 117. Duty cycling per batch rather than per item (sleep 0.3 s
after each batch-4 forward, no 7 s sleep) is a second option that reduces the size of the idle-to-boost swing; it is untested and
could equally be worse (the 10-14 sustained-load crash), so it is a stage-3 comparison, not a default.

## 5. Minimal staged GPU test plan (needs Shlok's approval; Shlok present, AC verified, other GPU apps closed)

Always: telemetry every 1 s to CSV flushed per row; `--max-temp 80`; abort rules apply at every stage.

Abort immediately (stop the process, do not retry the same stage until reviewed) if any of:
- whole-GPU used above 9,000 MiB (10,000 MiB during the first item), or a rise of more than 1.5 GB between two consecutive 1 s samples;
- GPU temperature at or above 75 C, or throttle reason other than 0x0/0x4 (any hardware slowdown or thermal bit);
- AC lost (`on_ac()` false) or a Power source change event;
- `nvidia-smi` slower than 3 s or returning NA/empty;
- an item takes more than 2x the stage median;
- any new LiveKernelEvent 117, nvlddmkm 153, Display 4101 in the System/Application log.

| Stage | Run | Purpose | Pass criterion |
|---|---|---|---|
| 0 (CPU only, now) | `CUDA_VISIBLE_DEVICES="" python -m pytest tests/exp_p2` with the fake network | confirm index ranges and shapes, count rows per item | all pass; log the per-item row counts |
| 1 (about 5 min) | Load UniDisc only, run 1 forward batch-4, then idle 5 min with 1 s telemetry | does the driver survive load, one ramp, and idle? | no abort rule trips |
| 2 (control, about 10 min) | `run_probe1` on 10 new items (`--limit 10`) under today's conditions | tests H1/H2 against the code: if this crashes, the cause is environment, not probe 2 | 10 items, no abort |
| 3 (about 10 min) | `run_probe2 --limit 5`, items 21-25, `MEM_FRAC=0.60`, new guards | item 21 is the one that crashed in run 2 | 5 items, memory plateau within 1 GB of stage 2 |
| 3b | same 5 items with per-batch micro-duty instead of per-item duty | compares the two duty patterns | same |
| 4 (isolation, about 15 min) | 10 items each with only swap+patch (no VQ), then only jpeg, then only noise (add `--only` switch) | finds a corruption path if any | 10 items each, no abort |
| 5 | resume the full run in 5 min chunks, check the System log between chunks | production | no abort across 4 consecutive chunks before lengthening to 12.5 min |

Decision rule: crash at stage 2 -> environment (H1/H2/H3), do not run any GPU job until the driver is reinstalled (Shlok's call) and
power is fixed; crash at stage 3-4 but not stage 2 -> H4/H5, bisect by corruption type; no crash through stage 5 -> the earlier
crashes were environment (power flap, a second client) and the guards above are the mitigation.

## 6. Checked and not available / limits

- Driver: `nvidia-smi` reports 595.71, "NVIDIA GeForce RTX 5070 Ti Laptop GPU".
- Minidumps in `C:\Windows\Minidump` (102726-18031-01.dmp 20:21, 102726-16296-01.dmp 23:25) are access-denied to this user; `cdb`,
  `windbg`, `kd` are not installed (only the system `dbgeng.dll`); nothing installed. `C:\Windows\LiveKernelReports\WATCHDOG`
  listing is also empty/denied. So bugcheck arguments (P1-P4) beyond WER's `ffffce8ef33eb050 / fffff8067e220440 / c000009a / 5`
  (crash 2) and `ffffdb8b65296030 / fffff8039e700440 / c000009a / 5` (crash 1) were not read, and the faulting process is unknown.
- Registry (read-only): TdrDelay 10, TdrDdiDelay 10; TdrLevel, TdrLimitCount, TdrLimitTime, HwSchMode not set (defaults).
  Someone raised the TDR delays earlier; that was not done in this session.
- The `6008` "previous shutdown at 11:01:16 PM" for crash 2 does not match the 23:24:58 telemetry; it is a last-alive stamp, not a
  crash time. Do not use it.
- `cudnn.benchmark`, `torch.compile` of the backbone and custom kernels: none are enabled in the probe path (UniDisc sets
  `compiled_flex_attention` only for training; the SDPA patch replaces the eval attention). `UNIDISC_FORCE_CUDNN_SPDA_CONTEXT=1`
  is set by `unidisc_setup.py` line 9 but with the patched attention it is not on the call path (hypothesis; not traced with a
  profiler).
- No timeline of other Claude sessions' GPU use was found for 20:10-20:21 or 23:12-23:26. A file-modification search under
  Downloads (depth 7, excluding P2-PROBE-02, .git, .venv) found no file written in either window, so no other project
  was logging output then; that weakens H3 for project jobs but says nothing about Chrome/Electron/NVIDIA Overlay.

Files read: `exp_p2/run_probe1.py`, `run_probe2.py`, `scoring.py`, `core.py`, `common.py`, `driver.py`; `tools/gpu_guard.py`;
`exp001/unidisc_net.py`; `runs/env-2026-10-14/scripts/unidisc_smoke.py`; UniDisc `image_tokenizers.py`, `models/dit.py`;
`runs/P2-PROBE-01` and `runs/P2-PROBE-02` telemetry, `chunks.jsonl`, `items.jsonl`, `driver.log`, `HOLD.txt`; the System and Application
event logs; the Windows battery report generated into `%TEMP%\claude_batt.html`.
