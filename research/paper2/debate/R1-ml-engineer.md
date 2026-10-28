---
agent: lab-engineer (ML engineer role)
date: 2026-10-28
brief: debate R1, feasibility view of Q1-Q5 for one 12 GB GPU, deadline Thu 29 Oct evening IST
evidence: E1 for web facts (page text via fetch, nothing downloaded); E4-derived for timings (runs/P2-PROBE-01, P2-PROBE-02 items.jsonl); everything else labelled estimate
---

# R1, ML engineer: what fits

## 0. Timing basis (measured, then derived)
- Probe 1 (runs/P2-PROBE-01/items.jsonl): median 7.02 s per item for 58 passes, i.e. at most 0.12 s per row (it includes encodes). The mean 9.65 s is inflated by stalls (max 635 s).
- Probe 2 (runs/P2-PROBE-02/items.jsonl, 21 items): 7.5-8.8 s for items 0-14, 9.7-10.4 s for items 15-20, about 65 rows plus 3 VQ encodes each, so 0.11-0.16 s per row. The step up at item 15 is unexplained (power state or thermal; not diagnosed).
- I use **0.12-0.16 s per row** as the range. Chunk loads cost 19-82 s each (chunks.jsonl), 3-11 percent of a 12.5-minute chunk. Wall time = 2 x item time at duty 0.5, plus that overhead.
- Capacity assumption (mine): GPU from Wed 12:00 to Thu 13:00 with Shlok present about 18 h of that wall, giving about 8 GPU-h of item time on paper and **about 5.5 planned** after a 30 percent allowance for stalls, restarts and one crash.

## 1. (a) GPU-hours (derived by scaling the card's row counts; all estimates)
| Item | Rows | GPU-h | Wall | Note |
|---|---|---|---|---|
| MUST M0-M5 | card v3: 2.61 at 0.15 s | **2.1-2.8** | 4.5-6.2 h | +0.8-1.0 only if rule R2 sets the test fold to 500 |
| Patch in the main test | 0 extra | 0 | 0 | M4 already encodes a patch image per item as the sanity arm; promotion is analysis and disclosure only |
| Swap in the main test | about 17 rows per item (8 gate + 8 text arms + 1 TbV) | +0.17-0.23 at 300 items | +0.4 h | new arm in the M4 runner |
| S2 re-infill, 150 items | 208 rows per item (spec 11.2) | **1.0-1.4** | 2.2-3.1 h | excludes VQ decode and the unmeasured sampling-loop overhead |
| FOIL-COCO text arm, 600 items | about 20 rows per item (2 captions: 1 full-mask pass each, 8 word-gate passes each, 2 caption-only) + 1 encode | 0.4-0.8 | 1.0-1.8 h | my row count, not in any card |
| Real image corruptions (imagecorruptions, per corruption, 300 items) | about 17 rows | 0.17-0.23 each | 0.4 h | |
| Omni-Diffusion 8B 4-bit | **unmeasured** | load plus 20-pass timing 0.1; "lite" run (100 calibration x 12 rows + 150 test x about 50 rows, about 8,700 rows) 0.6-1.6 | 1.5-3.5 h | the 0.25-0.65 s per row is an assumption (2-4 x UniDisc), not a measurement |

Demand if all but Omni run: 3.7-5.2 GPU-h; with Omni 4.4-6.9. Against about 5.5 planned, **Omni is the first thing that does not fit**.

**FOIL-COCO and real corruptions (web metadata only; the fetch tool auto-saved the arXiv PDF in its tool-results folder, I did not open or use it).**
- FOIL-COCO (Shekhar et al. 2017, arXiv 1705.01359): train 197,788 datapoints / 65,697 images, test 99,480 / 32,150 images (ar5iv HTML, Table 1). Each datapoint has the original caption and a foil with one wrong noun, hardest of the candidates for a captioner. Licence: CC BY 4.0 (University of Trento); COCO annotations CC BY 4.0; images under Flickr terms (foilunitn.github.io). Hosting: Dropbox JSON files (train, test); **file size not stated anywhere I could read**; use the October 2018 release (earlier release had a language bias). Not on Hugging Face as far as one search shows (unconfirmed).
- Overlap: the paper says test comes from the COCO validation set; the page does not say 2014 or 2017. My inference (not verified here): val2017 is a 5k subset of val2014, so most val2017 ids should be inside the FOIL test images. That is a **benefit**: we already hold val2017 images locally (exp_p2/common.py), so FOIL needs only the annotation JSON (a download, needs Shlok's yes after the size is known), and we filter to val2017 ids not used by any fold. The overlap check is a 5-line CPU job once the JSON is on disk. Contamination of UniDisc by COCO (spec U8) stays open and applies to every COCO item.
- FOIL corrupts the **caption**, one word; it tests the text direction and the word gate, not the image-token claim. It gives a real, published, hard-negative test where the clean text direction may sit below the 0.95 ceiling that makes fusion untestable (card section 13: text direction 0.990 on deranged negatives). That is its main value.
- Real image corruptions: no natural-corruption image-text set was found that I could verify. The standard option is the bethgelab `imagecorruptions` package (ImageNet-C functions; 15 common corruptions, 5 severities; Apache-2.0 per the GitHub page; PyPI page failed to load, so version and dependency size are unchecked), the same code behind COCO-C (Michaelis et al., arXiv 1907.07484). It generates locally from our own val2017 ids, so there is no id-overlap problem. They are global pixel corruptions, where the theory predicts the least gain; JPEG and noise are already ours. Needs `pip install` (Shlok's yes). Treat as optional breadth.

## 2. (b) Code still to write (hours; my estimates, CPU tests included)
| Item | Hours | Detail |
|---|---|---|
| Patch/swap promotion | 1.5-2 | swap arm in run_gate_m4, family P' in analysis_m4, tests; prereg addendum |
| FOIL runner | 6-8 | JSON loader, id filter and fold disjointness, caption-length filter 5-32, runner reusing the S1 word-unit helpers, analysis (accuracy, word-localisation AUROC vs baselines), tests |
| S2 re-infill | 7-9 | sampling loop (S_r = 16) over `logits_fn`, arms I, M+I, R1, leakage control, UniDisc G.1 best-of-n, resume runner, decode to PNG (`sc.decode` exists), tests with the fake network |
| Omni-Diffusion adapter | 8-10 | (i) audio encoder: **stub it** in the loader (the smoke script already did) instead of patching funasr; text and image never touch audio, and this removes the `trust_remote_code` pip-install of numpy<=1.26.4 and about 1 GB; fallback is the two-line patch at modeling_sensevoice.py:731 and :1082 with `trust_remote_code=False` and the local snapshot; (ii) NF4 loader with `llm_int8_skip_modules` for audio, lm_head, embeddings, sdpa, offline; (iii) scorer adapter: Dream **shifts logits by one position** (generation_utils.py:526,531), so `masked_logprobs` indices change; prompt template with image start/end tokens; MAGVIT-v2 encode/decode; (iv) selfcheck against a direct forward, tiny-config CPU test; (v) addendum |
| imagecorruptions wrapper | 2-3 | per-corruption seeds, severity rule, tokenise, tests |

Total about 25-30 h serial. Two coding streams fit: A = patch/swap then FOIL (8-10 h), B = S2 (7-9 h); Omni (stream C) only as a CPU-side stream that cannot delay A or B.

**Omni fit risk (nothing run):** weights about 6 GB in NF4 (blocks about 3.3 GB, embedding and lm_head bf16 about 2.5 GB, MAGVIT 95 M, audio stubbed) against UniDisc's measured 8.2 GB peak, so fit is likely; the risks are (1) bitsandbytes 0.50.2 kernels on sm_120 untested, (2) a 15 GB shard stream through 5-9 GB free RAM at load, a ramp like the one in the TDR crash hypothesis, (3) 4-bit logits are a different model, so a second-model claim must say "4-bit", (4) the logit-shift bug class, which silently gives chance-level results.

## 3. Answers to Q1-Q5 (feasibility view)
- **Q1.** One real-benchmark result on the text direction (FOIL) plus patch/swap in the family are the cheapest changes that move the paper from "one small model, injected noise" to "an effect on a published hard-negative set". A pure measurement claim is thin for Information Fusion; FOIL is the only addition that can unlock a fusion result.
- **Q2.** S2 should be MUST **conditionally**: it is the only arm that is true re-masking and gives repaired-image figures. Rule: it becomes MUST if its CPU tests are green and committed by Wed 20:00; otherwise it is dropped and not claimed. It is 7-9 h of unbuilt code.
- **Q3.** Patch/swap: value high, risk low (post-dry-run decision, disclose; Holm family grows, so split it as a separate declared family), cost 0-0.23. Second model: value medium, risk high, 0.7-1.7. Real benchmark: FOIL 0.4-0.8 (value high, risk: download size unknown, caption-only); imagecorruptions 0.2 each (value low).
- **Q4.** (1) FOIL word-localisation vs the cheap baselines (about 0 extra rows beyond the above). (2) Report the per-row timing and the whole-GPU memory log as a reproducibility table (free).
- **Q5.** Below.

## 4. (c) Crash-safe order with kill points (IST; every run: charger on, Ollama/Chrome/overlay closed, chunks of at most 12.5 min, resume, no auto-relaunch)
| When | Run | Kill point |
|---|---|---|
| Wed 12:00 | M0 (0.75 h wall) | any guard abort or bugcheck: stop all GPU, go to the CPU fallback (spec 11.4) |
| Wed 13:00 | M1 | crash: stop; no further GPU until Shlok says |
| Wed ~14:30 | M2 + M3 (0.9 h wall) | **Wed 20:00: if M1-M3 are not done, cut S2, FOIL, Omni; run M4 only** |
| Wed ~16:00 | M4 with patch + swap; addenda for patch/swap, FOIL, S2 committed before its first item | M4 not done by Thu 07:00: cut everything else |
| Wed ~19:30 | M5 | |
| Wed ~20:00 | FOIL (only if its tests are green and the JSON overlap check passed) | stall of more than 2 x median item time: stop and keep partial |
| Thu 07:00 | S2 (150 items) | S2 CPU tests not green by Wed 20:00: do not run |
| Thu 10:00 | Omni stage O: load + 20-pass timing only | per row above about 0.65 s, whole-GPU above 9,000 MiB, any bnb error, or not loaded by 11:30: abandon, report "not tested" |
| Thu 11:30 | last launch of anything longer than 1 h | |
| **Thu 13:00** | **GPU freeze** | text and figures from what is in runs/ |

Unattended overnight GPU runs would add about 4 GPU-h but are Shlok's call; I do not assume them.

## 5. Concerns
1. Every addendum (patch/swap, FOIL, S2) must be committed before the first item of the run it covers (card section 13); the order above leaves about 2 h for it before M4.
2. FOIL JSON size and the val2017 overlap are unverified; the overlap rests on my inference.
3. All timings are scaled from a 0.12-0.16 s per-row range; the step up at probe-2 item 15 is unexplained and could widen it.
4. Omni: cost is an assumption, not a measurement; I recommend cutting it.
5. Holm family size changes with patch/swap; the statistician must set it before M4.
