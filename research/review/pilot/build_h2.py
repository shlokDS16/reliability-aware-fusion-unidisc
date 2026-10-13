"""Build and validate h2-papers.jsonl and h2-units.jsonl (blind extraction, pilot batch of 15 papers).
All numbers are copied as printed in the per-paper extracts (research/review/pilot/papers/*.md) or, where noted,
from the cached arXiv HTML. Run from the project root: python research/review/pilot/build_h2.py
"""
import json, sys, os

ROOT = "research/review/pilot/"
batch = json.load(open(ROOT + "batch.json", encoding="utf-8"))
ARX = {b["record_id"]: b["arxiv"] for b in batch}

UNIT_KEYS = ["record_id", "arxiv", "block", "task", "model", "gen_length", "metric", "higher_is_better",
             "method_name", "method_T", "cost_unit", "method_Q", "method_sd", "baseline_name",
             "baseline_headline_T", "baseline_headline_Q", "baseline_sweep", "sweep_block",
             "baseline_source", "order_rule", "decoding", "note"]
PAPER_KEYS = ["record_id", "arxiv", "speedup_kind", "claim_quote", "claim_location", "baseline_swept", "note"]
COST_UNITS = {"NFE", "steps", "tokens-per-step", "other"}
ORDER = {"random", "confidence", "entropy", "margin", "left-to-right", "unclear"}
DEC = {"argmax", "sampled", "unclear"}
SRC = {"rerun", "copied", "unclear"}
KINDS = {"forward-passes", "wall-clock", "both", "none"}

units = []


def U(rid, block, task, model, gen, metric, mname, mT, cu, mQ, bname, bT, bQ, sweep, sblock, bsrc, order, dec, note,
      hib=True, sd=None):
    units.append(dict(record_id=rid, arxiv=ARX[rid], block=block, task=task, model=model, gen_length=gen,
                      metric=metric, higher_is_better=hib, method_name=mname, method_T=mT, cost_unit=cu,
                      method_Q=mQ, method_sd=sd, baseline_name=bname, baseline_headline_T=bT,
                      baseline_headline_Q=bQ, baseline_sweep=sweep, sweep_block=sblock, baseline_source=bsrc,
                      order_rule=order, decoding=dec, note=note))


FASTER = "T is a rate (higher = faster/cheaper)."

# ---------------------------------------------------------------- AW0403 rho-EOS (Table 1, LLaDA-Instruct-8B)
rid = "AW0403"
r403 = {  # task: (baseline fixed-length runtimes L=64..2048), accs, (sym T,Q), (asym T,Q), daedal
    "GSM8K": ([174, 360, 860, 2458, 8238, 30305], [47.9, 68.0, 77.8, 83.6, 83.9, 82.7], (645, 81.8), (823, 84.2), (1090, 84.6)),
    "MATH500": ([98, 208, 462, 1202, 3663, 12764], [24.0, 29.0, 35.4, 38.4, 40.4, 40.0], (1398, 37.0), (1968, 40.6), (2207, 40.0)),
    "MBPP": ([176, 332, 713, 1728, 4760, 15172], [21.0, 28.8, 36.7, 38.7, 37.5, 38.8], (2031, 39.6), (2030, 40.6), (3551, 39.4)),
    "HumanEval": ([111, 230, 543, 1474, 4569, 16046], [17.1, 26.2, 36.6, 45.1, 45.1, 48.2], (580, 43.3), (593, 43.9), (1283, 44.5)),
}
for task, (ts, qs, sym, asym, dae) in r403.items():
    sweep = [[t, q] for t, q in zip(ts, qs)]
    for lab, (t, q) in (("rho-EOS (L_init=64, Asym thresholds)", asym), ("rho-EOS (L_init=64, Sym thresholds)", sym)):
        U(rid, "Table 1 (read from HTML text; not in extract)", task, "LLaDA-Instruct-8B", None, "Acc (%)", lab, t, "other", q,
          "Fixed-length denoising, L=2048", ts[-1], qs[-1], sweep, "Table 1", "unclear", "unclear", "unclear",
          "T = T_runtime in seconds for the whole evaluation set (paper: 'runtime spent on the evaluation (in seconds)'), "
          "not NFE. Baseline sweep = fixed-length baseline at L=64,128,256,512,1024,2048 (cost knob is generation length; step counts not printed). "
          "Headline baseline = highest-cost row because the caption says the best baseline config is highlighted orange but colour is not in text. "
          f"DAEDAL (L_init=64) in same table: T={dae[0]}, Q={dae[1]}. Paper's main rho-EOS setting (Sym vs Asym) not identified; both recorded. "
          "method gen_length is variable (starts at 64). Table 2 (LLaDA-1.5) not read.")

# ---------------------------------------------------------------- AW0376 DOS (Tables 6, 7)
rid = "AW0376"
lens = {"HumanEval": 256, "MBPP": 256, "GSM8K": 512, "MATH500": 512}
tasks4 = ["HumanEval", "MBPP", "GSM8K", "MATH500"]
llada = dict(
    top1={"HumanEval": (256.00, 40.85), "MBPP": (256.00, 38.20), "GSM8K": (512.00, 82.56), "MATH500": (512.00, 38.80)},
    eb={"HumanEval": (104.28, 41.46), "MBPP": (73.39, 38.60), "GSM8K": (165.33, 82.71), "MATH500": (249.76, 39.20)},
    dos_wo={"HumanEval": (115.84, 45.12), "MBPP": (76.09, 38.80), "GSM8K": (163.48, 84.61), "MATH500": (244.24, 41.00)},
    dos_w={"HumanEval": (103.05, 43.90), "MBPP": (80.90, 39.00), "GSM8K": (170.06, 84.00), "MATH500": (257.55, 41.40)})
dream = dict(
    top1={"HumanEval": (256.00, 58.54), "MBPP": (256.00, 50.02), "GSM8K": (512.00, 81.50), "MATH500": (512.00, 40.08)},
    eb={"HumanEval": (78.86, 57.93), "MBPP": (71.90, 50.20), "GSM8K": (182.38, 81.96), "MATH500": (227.54, 39.80)},
    dos_wo={"HumanEval": (72.47, 58.54), "MBPP": (68.33, 51.00), "GSM8K": (182.43, 79.98), "MATH500": (229.36, 45.40)})
dos_note = ("T = NFE as printed (average per example). Baselines in Table 6/7 use block size 32; 'DOS + EB (w/o block)' is decoded as a single block, "
            "'(w/ block)' uses block 32. Headline baseline = highest-NFE baseline row (Confidence top-1; ties with Entropy, Margin at same NFE) because the "
            "paper states no speed-up reference. Sweep = Confidence top-1 and Confidence + EB (two selection policies, same order rule; Fast-dLLM threshold row "
            "is a separately named baseline and is excluded). Table 2 repeats the same DOS + EB row against single-block baselines "
            "(e.g. Confidence + EB at larger NFE and lower Acc). Temperature 0 stated in HTML.")
for model, D, tab, variants in (("LLaDA-Instruct-8B", llada, "Table 6", [("DOS + EB (w/o block)", "dos_wo"), ("DOS + EB (w/ block)", "dos_w")]),
                                ("Dream-v0-Instruct-7B", dream, "Table 7", [("DOS + EB (w/o block)", "dos_wo")])):
    for mname, key in variants:
        for task in tasks4:
            mT, mQ = D[key][task]
            sweep = sorted([list(D["eb"][task]), list(D["top1"][task])])
            U(rid, tab, task, model, lens[task], "Acc (%)", mname, mT, "NFE", mQ, "Confidence (top-1, block 32)",
              D["top1"][task][0], D["top1"][task][1], sweep, tab, "rerun", "confidence", "argmax", dos_note)

# ---------------------------------------------------------------- AW0335 VoidPadding (Table 3 LLaDA)
rid = "AW0335"
v = {"GSM8K": ((133.78, 78.32), (135.54, 79.38), (92.57, 73.39), (60.20,)),
     "MATH500": ((418.05, 39.60), (269.65, 37.40), (104.30, 27.00), (26.80,)),
     "HumanEval": ((73.06, 42.07), (254.66, 44.51), (191.52, 40.24), (29.27,)),
     "MBPP": ((63.50, 45.38), (255.43, 41.79), (170.41, 41.38), (41.27,))}
for task, (m, d, r, f) in v.items():
    U(rid, "Table 3 (NFE from Table 3(b))", task, "LLaDA-8B-Instruct (VoidPadding fine-tuned) for VoidExpansion; original LLaDA-8B-Instruct for baselines",
      None, "accuracy / pass@1 (as in Table 3)", "VoidExpansion (VoidPadding checkpoint, tau_nonvoid=0.09, tau_gap=-0.45)", m[0], "NFE", m[1],
      "Daedal (EOS-signal adaptive canvas expansion)", d[0], d[1], [], None, "rerun", "unclear", "unclear",
      f"Headline baseline = Daedal because Table 3(b) normalises wall speedup to it. Second baseline rho-EOS: NFE {r[0]}, Q {r[1]}. "
      f"Fixed-64 LLaDA (no expansion): Q {f[0]}. NFE counts decoding passes only. L0=64, Lmax=512, B=32, w=16 (HTML text). "
      "Dream rows not recorded: Table 1 accuracies are not in the extract or HTML text; only Table 2 NFE (Original/Rainbow 512.0 vs VoidPadding).")

# ---------------------------------------------------------------- AW0393 DSB (Tables 1, 2)
rid = "AW0393"
dsb_note = ("T = TPS (tokens per second), " + FASTER + " Method = DSB (greedy) with DSB Cache. Headline baseline = Confidence decoding with Dual cache and naive block "
            "(the TPS comparison the text draws for GSM8K, line 'naive block with Dual Cache'). Other Table 1 rows (Vanilla top-1 no cache, Confidence no cache, "
            "dKV, AdaBlock, DSB const.) not in sweep. Generation length 256, block length 32 (HTML text).")
dsb = [  # (model, table, task, mQ, mT, bQ, bT)
    ("LLaDA-8B-Instruct", "Table 1", "GSM8K", 80.29, 99.61, 77.40, 92.26),
    ("LLaDA-8B-Instruct", "Table 1", "MATH", 33.46, 89.90, 32.72, 83.58),
    ("LLaDA-8B-Instruct", "Table 1", "HumanEval", 39.63, 107.7, 37.80, 100.6),
    ("LLaDA-8B-Instruct", "Table 1", "MBPP", 42.80, 81.88, 37.80, 76.61),
    ("LLaDA-8B-Instruct", "Table 1", "BBH", 51.16, 100.1, 47.09, 90.79),
    ("Dream-v0-Instruct-7B", "Table 2", "GSM8K", 73.08, 75.27, 67.32, 72.18),
    ("Dream-v0-Instruct-7B", "Table 2", "MATH", 37.00, 82.63, 36.94, 80.76),
    ("Dream-v0-Instruct-7B", "Table 2", "HumanEval", 59.76, 65.28, 53.05, 65.91),
    ("Dream-v0-Instruct-7B", "Table 2", "MBPP", 56.40, 61.85, 53.80, 57.94),
    ("Dream-v0-Instruct-7B", "Table 2", "BBH", 57.93, 144.7, 58.47, 126.7),
    ("LLaDA-1.5", "Table 1", "GSM8K", 81.96, 95.54, 80.82, 86.42),
    ("LLaDA-1.5", "Table 1", "HumanEval", 34.70, 31.92, 34.10, 30.91)]
for model, tab, task, mq, mt, bq, bt in dsb:
    U(rid, tab, task, model, 256, "Acc. (%)", "DSB (greedy) + DSB Cache", mt, "other", mq, "Confidence + Dual cache + Naive block",
      bt, bq, [], None, "unclear", "confidence", "unclear", dsb_note)

# ---------------------------------------------------------------- AW0406 Streaming-dLLM (Tables 1, 2)
rid = "AW0406"
sd_note = ("T = decoding throughput in tokens/s (printed in blue in the source), " + FASTER + " Baseline = the unaccelerated model (1x in the paper; the 68.2X headline is "
           "MBPP 512 LLaDA-1.5 vs this baseline). Fast-dLLM, Prefix-Cache and dKV-Cache columns exist but are not the reference. "
           "Printed speedup of Ours over baseline: {sp}. Latency tables 9-11 give the same runs in seconds.")
sdl = [  # (model, table, task, gen, bQ, bT, mQ, mT, speedup, src)
    ("LLaDA-1.5", "Table 2", "HumanEval", 256, 43.9, 6.4, 39.0, 34.1, "5.3x", "rerun"),
    ("LLaDA-1.5", "Table 2", "HumanEval", 512, 40.5, 2.9, 40.2, 26.7, "9.2x", "rerun"),
    ("LLaDA-1.5", "Table 2", "GSM8K", 256, 80.5, 6.3, 80.8, 66.2, "10.5x", "rerun"),
    ("LLaDA-1.5", "Table 2", "GSM8K", 512, 81.0, 2.5, 81.2, 69.8, "28.0x", "rerun"),
    ("LLaDA-1.5", "Table 2", "MBPP", 256, 38.0, 2.2, 37.8, 54.7, "24.9x", "rerun"),
    ("LLaDA-1.5", "Table 2", "MBPP", 512, 38.2, 0.9, 38.4, 61.4, "68.2x", "rerun"),
    ("LLaDA-1.5", "Table 2", "MATH", 256, 32.7, 7.8, 33.7, 66.2, "8.5x", "rerun"),
    ("LLaDA-1.5", "Table 2", "MATH", 512, 37.1, 4.8, 35.1, 62.4, "13.0x", "rerun"),
    ("Dream-Base-7B", "Table 1", "HumanEval", 512, 54.3, 13.7, 54.6, 72.3, "5.3x", "unclear"),
    ("Dream-Base-7B", "Table 1", "GSM8K-CoT", 512, 74.2, 7.1, 74.7, 94.1, "13.3x", "unclear"),
    ("Dream-Base-7B", "Table 1", "MBPP", 512, 55.6, 8.7, 55.8, 92.4, "10.6x", "unclear"),
    ("Dream-Base-7B", "Table 1", "MATH", 512, 39.8, 8.6, 39.4, 96.0, "11.2x", "unclear")]
for model, tab, task, gen, bq, bt, mq, mt, sp, src in sdl:
    extra = (" Baseline Q is marked with an asterisk in the table (caption: asterisk = reproduced with official implementation because not reported)." if src == "rerun"
             else " Baseline Q carries no asterisk (caption implies reported in original papers); throughput provenance unclear.")
    U(rid, tab, task, model, gen, "Acc (%)", "Streaming-dLLM (Ours)", mt, "other", mq, model + " vanilla (no cache, no parallel threshold)", bt, bq, [], None,
      src, "unclear", "unclear", sd_note.format(sp=sp) + extra)

# ---------------------------------------------------------------- AW0333 SpecRef (Table 1, Table 3)
rid = "AW0333"
sr = {  # task: (baseline S=8,16,32,64), (specref S=8,16,32,64)
    "GSM8K": ([8.72, 12.43, 22.14, 44.81], [39.50, 45.26, 50.95, 54.28], 47.38),
    "HumanEval": ([0.00, 0.00, 1.74, 8.70], [20.12, 20.73, 20.73, 25.61], 44.51),
    "MBPP": ([0.20, 0.60, 2.00, 7.20], [20.80, 22.80, 26.00, 33.00], 43.00),
    "MATH*": ([10.76, 12.72, 16.12, 22.32], [14.16, 17.70, 20.44, 21.38], 5.22)}
lat = {16: "baseline 4.12 s vs SpecRef 5.18 s (0.80x)", 32: "baseline 8.24 s vs SpecRef 5.95 s (1.38x)", 64: "baseline 16.49 s vs SpecRef 6.79 s (2.43x)"}
Ss = [8, 16, 32, 64]
for task, (bs, ms, phi) in sr.items():
    sweep = [[s, q] for s, q in zip(Ss, bs)]
    for s in (16, 32, 64):
        i = Ss.index(s)
        n = (f"T = number of diffusion steps S only; SpecRef also pays one AR drafting pass (phi-2 under vLLM) not counted in S. Table values are percentages as printed. "
             f"Headline baseline = LLaDA at S=64 (the paper's claim is that SpecRef needs fewer steps to match baseline quality); sweep = LLaDA at S=8,16,32,64. "
             f"SpecRef at S=8: {ms[0]}. Phi-2 draft alone: {phi}%. Quality at S=64 for MATH* is a column labelled 'MATH*' in the paper. ")
        if task == "GSM8K":
            n += f"Table 3 latency (GSM8K, RTX 4090) at S={s}: {lat[s]}."
        U(rid, "Table 1", task, "LLaDA-8B-Instruct (refiner) + microsoft/phi-2 (drafter)", None, "accuracy / pass@1 (%)", "SpecRef", s, "steps", ms[i],
          "LLaDA-8B-Instruct baseline", 64, bs[3], sweep, "Table 1", "unclear", "unclear", "unclear", n)

# ---------------------------------------------------------------- AW0364 SWD (Tables 1,5,6,7)
rid = "AW0364"
swd_conf = {  # model: task: (baseQ, baseNFE, swdQ, swdNFE)
    "LLaDA-8B": {"HumanEval": (28.0, 102.9, 36.0, 77.2), "MBPP": (23.4, 110.3, 34.8, 66.8), "GSM8K": (31.5, 224.1, 67.3, 163.2), "MATH500": (19.6, 226.6, 26.2, 205.7)},
    "Dream-7B": {"HumanEval": (12.2, 179.7, 24.4, 67.4), "MBPP": (29.4, 212.4, 26.2, 86.2), "GSM8K": (29.3, 286.6, 61.6, 119.3), "MATH500": (10.8, 364.1, 35.0, 151.6)}}
swd_len = {"HumanEval": 256, "MBPP": 256, "GSM8K": 512, "MATH500": 512}
# LLaDA sweeps: Top-1 (Table 7), threshold tau (Table 6), EB (Table 1/5)
top1 = {"conf": {"HumanEval": (256.0, 26.2), "MBPP": (256.0, 23.8), "GSM8K": (512.0, 31.7), "MATH500": (512.0, 20.4)},
        "margin": {"HumanEval": (256.0, 22.0), "GSM8K": (512.0, 37.3)},
        "entropy": {"HumanEval": (256.0, 26.2), "GSM8K": (512.0, 24.3)}}
thr = {"conf": {"HumanEval": (66.16, 29.27), "MBPP": (52.45, 24.20), "GSM8K": (150.40, 27.90), "MATH500": (181.79, 18.20)},
       "margin": {"HumanEval": (65.77, 23.17), "GSM8K": (167.82, 36.24)},
       "entropy": {"HumanEval": (85.01, 27.44), "GSM8K": (90.49, 59.14)}}
swd_note = ("T = NFE (average per example). Method = EB sampler + SWD (lambda=5, Table 1). Baseline = 'Base' vanilla EB sampler with the stated score. "
            "Gen length 256 for code, 512 for reasoning (HTML text). ")
sweep_note = ("LLaDA sweep pairs = same score under three selection policies: Top-1 (Table 7, 'Top-1 (Base)'), threshold decoding (Table 6, lambda=0, tau as listed there: "
              "0.9 confidence/margin, -0.4 neg-entropy) and the EB sampler (headline); these are different policies, not one parameter sweep. ")
for task in tasks4:
    for model in ("LLaDA-8B", "Dream-7B"):
        bq, bn, sq, sn = swd_conf[model][task]
        if model == "LLaDA-8B":
            sweep = sorted([list(top1["conf"][task]), list(thr["conf"][task]), [bn, bq]])
            n = swd_note + sweep_note
        else:
            sweep = []
            n = swd_note + "No Top-1 or threshold baseline given for Dream full-sequence decoding (Table 10 is Dream block-32 only)."
        U(rid, "Table 1", task, model, swd_len[task], "Acc (%)", "EB + SWD (Confidence score, lambda=5)", sn, "NFE", sq,
          "EB sampler, Confidence score (Base)", bn, bq, sweep, "Tables 5/6/7" if sweep else None, "unclear", "confidence", "unclear", n)
for sc, scname, order, key in (("Margin", "Margin", "margin", "margin"), ("Entropy", "Entropy", "entropy", "entropy")):
    panel = {"Margin": {"HumanEval": (23.2, 100.8, 29.9, 66.4), "GSM8K": (38.7, 215.8, 64.4, 166.9)},
             "Entropy": {"HumanEval": (28.7, 108.9, 32.3, 103.5), "GSM8K": (26.3, 226.6, 48.7, 191.8)}}[sc]
    for task in ("HumanEval", "GSM8K"):
        bq, bn, sq, sn = panel[task]
        sweep = sorted([list(top1[key][task]), list(thr[key][task]), [bn, bq]])
        U(rid, "Table 1", task, "LLaDA-8B", swd_len[task], "Acc (%)", f"EB + SWD ({scname} score, lambda=5)", sn, "NFE", sq,
          f"EB sampler, {scname} score (Base)", bn, bq, sweep, "Tables 5/6/7", "unclear", order, "unclear",
          swd_note + sweep_note + ("Entropy score is reported as Entropy in Table 1 and Neg_Entropy in Tables 6/9." if sc == "Entropy" else ""))

# ---------------------------------------------------------------- AW0381 Stitching (Table 7, Table 10)
rid = "AW0381"
st7 = [("LLaDA-1.5", "GSM8K", 84.0, 101, 90.8, 87), ("LLaDA-1.5", "MATH500", 38.0, 163, 53.8, 134),
       ("Dream", "GSM8K", 82.6, 512, 85.4, 521), ("Dream", "MATH500", 48.2, 512, 53.2, 523),
       ("LLaDA 2.0", "GSM8K", 88.0, 256, 89.6, 266), ("LLaDA 2.0", "MATH500", 44.6, 256, 61.4, 267)]
for model, task, bq, bs, mq, ms in st7:
    U(rid, "Table 7", task, model, None, "Acc (%)", f"{model} w/ stitching (diffusion rollouts + PRM + AR solver)", ms, "steps", mq, f"{model} (plain decoding)",
      bs, bq, [], None, "unclear", "unclear", "unclear",
      "T = '#steps' as printed in Table 7 (Table 5 caption defines it as steps of the longest diffusion trajectory plus solver steps; Table 7 definition assumed identical). "
      "Stitching pipeline adds PRM scoring and an AR solver not counted in #steps. Generation length for Table 7 not stated in extract. "
      "Method uses lower-confidence sampling (gamma=0.7 elsewhere); baseline sampling threshold for Table 7 not stated.")
U(rid, "Table 10", "AIME25", "LLaDA2.0-mini (+ Qwen3 solver for method)", 8192, "AIME25 score (%)", "Ours (LLaDA2.0-mini + Qwen3, non-thinking, 8192 / 256 tokens)",
  112.54, "other", 46.67, "LLaDA2.0-mini (token limit 8192)", 91.43, 33.33, [], None, "unclear", "unclear", "unclear",
  "T = latency in seconds (lower = faster); the method is slower than the diffusion-only baseline here. Other rows in the table: Qwen3 solver-only non-thinking 4096 tokens 23.33 / 40.35 s; "
  "thinking 8192 tokens 16.70 / 148.75 s; thinking 16392 tokens 56.70 / 233.13 s. Table 13 (GSM8K, RSD 94.6 acc, 325/75 drafter/verifier steps vs ours 91.5, 80/6 diffusion/solver steps) not recorded as a unit: cost is two-part.")

# ---------------------------------------------------------------- AW0373 S2D2 (Tables 1, 2)
rid = "AW0373"
s2note = ("T = wall-clock speedup factor relative to the autoregressive baseline in the same table (AR = 1.0x), " + FASTER + " Headline baseline = Diffusion (dynamic), "
          "the 'tuned dynamic decoding baseline' of the abstract. Sweep = Diffusion (static) and Diffusion (dynamic) at the strongest baseline block size, as [speedup vs AR, accuracy]. "
          "Accuracy in percent as printed. Generation length and decoding temperature not stated in extract. AR accuracy for reference: {ar}.")
sd8 = {  # task: (AR, static, dynamic, A, B)
    "GSM8K": ((89.3,), (1.4, 89.6), (2.6, 89.3), (2.0, 89.6), (3.8, 88.3)),
    "MBPP": ((64.4,), (1.4, 61.0), (2.1, 60.6), (2.1, 62.0), (2.8, 61.4)),
    "HumanEval": ((75.6,), (1.6, 79.3), (2.9, 78.0), (2.2, 78.7), (3.2, 74.4))}
sd4 = {
    "GSM8K": ((88.5,), (1.4, 89.0), (2.7, 88.9), (3.7, 87.5), (4.3, 87.4)),
    "MBPP": ((59.6,), (1.5, 57.2), (2.1, 55.6), (1.3, 56.0), (2.3, 57.0)),
    "HumanEval": ((75.6,), (1.3, 73.8), (1.9, 73.8), (3.1, 69.5), (3.3, 68.3))}
for model, D in (("SDAR-8B-Chat", sd8), ("SDAR-4B-Chat", sd4)):
    for cfg, idx in (("S2D2 (config-B, speed)", 4), ("S2D2 (config-A, accuracy)", 3)):
        if model == "SDAR-4B-Chat" and idx == 3:
            continue
        for task, row in D.items():
            sweep = [[row[1][0], row[1][1]], [row[2][0], row[2][1]]]
            sweep.sort()
            U(rid, "Table 1", task, model, None, "Acc (%)", cfg, row[idx][0], "other", row[idx][1], "Diffusion (dynamic) block-diffusion decoding",
              row[2][0], row[2][1], sweep, "Table 1", "unclear", "confidence", "unclear", s2note.format(ar=row[0][0]))
fd = {"GSM8K": ((84.8, 2.5), (83.2, 3.3), (78.3, 3.5), 82.0, 3.9, 85.1), "MBPP": ((50.6, 2.3), (47.8, 2.9), (46.2, 3.6), 45.6, 3.8, 51.8),
      "HumanEval": ((14.6, 1.4), (11.0, 1.5), (8.5, 1.7), 19.5, 2.5, 32.9)}
for task, (a, b, c, mq, mt, ar) in fd.items():
    sweep = sorted([[a[1], a[0]], [b[1], b[0]], [c[1], c[0]]])
    U(rid, "Table 2", task, "Fast-dLLM v2 (B=32)", None, "Acc (%)", "S2D2 (config-C, SB=32)", mt, "other", mq, "Diffusion (config-C, SB=32), normal BD3 without sub-blocks",
      c[1], c[0], sweep, "Table 2", "unclear", "confidence", "unclear",
      "T = wall-clock speedup relative to the autoregressive-style baseline (B=4, SB=1), " + FASTER + f" AR accuracy {ar}. Headline baseline chosen as config-C because S2D2 config-C is its matched method row (paper states no single reference). "
      "Sweep = Diffusion config-A, B, C (sub-block size varied), as [speedup, accuracy]. Generation length not stated in extract.")

# ---------------------------------------------------------------- AW0350 Fast-dLLM++ (Tables 1, 4)
rid = "AW0350"
fp = [  # model, table, task, gen, thrQ, thrNFE, thrTok, frQ, frNFE, frTok, facQ, facNFE, facTok
    ("LLaDA-8B-Instruct", "Table 1", "GSM8K", 256, 77.6, 107135, 73.8, 77.2, 72881, 103.8, 78.1, 79047, 96.0),
    ("LLaDA-8B-Instruct", "Table 1", "MATH", 256, 33.1, 503377, 74.4, 32.5, 358178, 102.5, 32.7, 379330, 97.3),
    ("LLaDA-8B-Instruct", "Table 1", "HumanEval", 256, 40.2, 13666, 77.8, 40.9, 9740, 107.7, 40.7, 10538, 89.6),
    ("LLaDA-8B-Instruct", "Table 1", "MBPP", 256, 27.4, 34975, 66.0, 25.4, 25791, 85.4, 21.4, 26870, 81.6),
    ("LLaDA-8B-Instruct", "Table 1", "GSM8K", 512, 76.5, 129791, 45.3, 75.6, 91239, 59.4, 74.6, 99580, 53.3),
    ("LLaDA-8B-Instruct", "Table 1", "MATH", 512, 36.1, 764793, 56.4, 35.5, 545993, 77.7, 35.3, 585176, 69.1),
    ("LLaDA-8B-Instruct", "Table 1", "HumanEval", 512, 41.5, 27366, 54.1, 41.5, 18909, 75.5, 41.7, 20463, 70.3),
    ("LLaDA-8B-Instruct", "Table 1", "MBPP", 512, 14.2, 59999, 60.8, 14.2, 42893, 82.7, 12.0, 45186, 80.0),
    ("Dream-v0-Base-7B", "Table 4", "GSM8K", 256, 73.7, 202862, 51.1, 72.0, 171925, 63.8, 72.0, 176073, 63.1),
    ("Dream-v0-Base-7B", "Table 4", "MATH", 256, 34.0, 568643, 72.6, 33.1, 433971, 97.0, 33.2, 442791, 92.4),
    ("Dream-v0-Base-7B", "Table 4", "HumanEval", 256, 37.8, 25465, 53.7, 35.4, 20156, 70.6, 36.0, 20246, 68.3),
    ("Dream-v0-Base-7B", "Table 4", "MBPP", 256, 56.0, 47070, 85.1, 53.2, 35170, 111.2, 51.8, 38043, 106.6)]
for model, tab, task, gen, tq, tn, tt, fq, fn, ft, cq, cn, ct in fp:
    U(rid, tab, task, model, gen, "Acc. (%)", "Fast-dLLM++ (Frechet profile decoding, margin delta=0.25)", fn, "NFE", fq,
      "Threshold decoding (tau=0.9), Fast-dLLM primary rule", tn, tq, [], None, "unclear", "confidence", "unclear",
      f"T = total NFE over the benchmark run as printed (not per example). PrefixCache, block size 32, H100. Throughput tok/s: threshold {tt}, Frechet {ft}. "
      f"Factor (f=1.0) baseline row: Acc {cq}, NFE {cn}, tok/s {ct}; it is a different decision rule (the method generalises it), not in sweep.")

# ---------------------------------------------------------------- AW0351 SimSD (Tables 1, 2)
rid = "AW0351"
tps = {  # BL: task: (Vanilla, Vanilla+CG, S2D2, SimSD)
    4: {"GSM8K": (10.0, 50.1, 54.8, 72.6), "MBPP": (11.4, 50.7, 47.7, 72.2), "TriviaQA": (11.4, 50.5, 28.3, 73.3), "MMLU": (5.59, 56.04, 32.3, 68.4)},
    8: {"GSM8K": (15.3, 30.9, 57.6, 74.1), "MBPP": (18.7, 30.4, 50.2, 80.4), "TriviaQA": (20.4, 31.9, 30.0, 88.3), "MMLU": (6.21, 36.8, 28.0, 84.4)}}
acc = {4: {"GSM8K": (0.922, 0.896), "MBPP": (0.669, 0.662), "TriviaQA": (0.486, 0.537), "MMLU": (0.706, 0.758)},
       8: {"GSM8K": (0.906, 0.894), "MBPP": (0.642, 0.634), "TriviaQA": (0.471, 0.503), "MMLU": (0.704, 0.760)}}
for bl in (4, 8):
    for task in ("GSM8K", "MBPP", "MMLU", "TriviaQA"):
        v_, cg, s2, sd_ = tps[bl][task]
        va, sa = acc[bl][task]
        U(rid, "Table 1 (TPS) + Table 2 (accuracy)", task, f"SDAR-family target, block length {bl} (target size not stated in Table 1/2)", None,
          "accuracy (fraction, as printed; pass@1 for MBPP)", "SimSD", sd_, "other", sa, "Vanilla decoding (tensor parallel 2)", v_, va, [], None, "unclear", "unclear", "unclear",
          f"T = decoded tokens/s from Table 1, " + FASTER + f" Cost and quality come from different tables (assumed same runs). Vanilla + CUDA graph: {cg} tok/s; S2D2: {s2} tok/s "
          "(no accuracy given for those two in Table 2). Speedup is quoted relative to Vanilla with tensor parallelism 2 at the same block length.")

# ---------------------------------------------------------------- AW0385 JoT (Tables 1, 4, 5)
rid = "AW0385"
jot = [  # model, task, steps, baseQ, jotQ, step speedup, wall speedup, decoding
    ("Dream-7B-Instruct", "GSM8K", 256, 81.1, 78.8, "5.54x", "4.71x"), ("Dream-7B-Instruct", "HumanEval", 512, 59.1, 58.5, "19.60x", "15.15x"),
    ("Dream-7B-Instruct", "MMLU", 3, 68.2, 66.7, "1.57x", "1.55x"), ("Dream-7B-Instruct", "HellaSwag", 5, 73.3, 72.7, "2.26x", "2.22x"),
    ("LLaDA-8B-Instruct", "GSM8K", 256, 74.5, 73.4, "3.75x", "3.15x"), ("LLaDA-8B-Instruct", "HumanEval", 512, 47.6, 44.5, "2.12x", "1.77x"),
    ("LLaDA-8B-Instruct", "MMLU", 3, 67.3, 64.5, "1.98x", "1.85x"), ("LLaDA-8B-Instruct", "HellaSwag", 5, 76.7, 76.6, "3.42x", "3.08x")]
for model, task, stp, bq, mq, sp, wp in jot:
    dr = "Dream" in model
    glen = {"MMLU": 3, "HellaSwag": 5}.get(task)
    U(rid, "Table 1", task, model, glen, "score (%); pass@1 for HumanEval", "JoT (token-level early stopping)", None, "steps", mq, "Full Decoding", stp, bq, [], None, "unclear", "unclear",
      "sampled" if dr else "unclear",
      f"method_T null: cost reported only as step-speedup {sp} relative to Full Decoding (Table 1); wall-clock speedup {wp} (Table 5). Baseline T = steps from Table 4 (Dream and LLaDA share the value; LLaDA block 32/3/5/32). "
      "Gen length for GSM8K/HumanEval not stated in extract (steps 256/512 may equal it); 3 and 5 tokens for MMLU/HellaSwag from HTML text. "
      "Table 1 text says 'our Dream experiments sample at T=0.1' and JoT uses argmax filling; baseline decoding policy not stated. "
      "Binomial standard errors stated in text: about 1.1 points GSM8K (n=1319), 3.8-3.9 points HumanEval (n=164). Fast-dLLM, Prophet, KLASS rows exist but are other methods.")

# ---------------------------------------------------------------- AW0389 DAWN (Tables 1, 2)
rid = "AW0389"
dn = [  # NFE units (Table 2) with TPS/speedup from Table 1
    ("LLaDA-8B-Instruct", "Table 2", "GSM8K", 77.94, 55.76, 77.94, 256, "44.72 TPS (4.33x) vs Original 10.32 TPS"),
    ("LLaDA-8B-Instruct", "Table 2", "HumanEval", 40.24, 61.63, 40.24, 256, "108.99 TPS (4.12x) vs Original 26.46 TPS"),
    ("Dream-v0-Instruct-7B", "Table 2", "GSM8K", 73.16, 51.92, 76.35, 256, "32.99 TPS (4.52x) vs Original 7.30 TPS"),
    ("Dream-v0-Instruct-7B", "Table 2", "HumanEval", 54.88, 77.12, 53.66, 256, "60.23 TPS (2.66x) vs Original 22.66 TPS")]
for model, tab, task, mq, mt, bq, bt, extra in dn:
    U(rid, tab, task, model, 256, "Acc (%)", "DAWN", mt, "NFE", mq, "Original (default sampler, 1 token per step)", bt, bq, [], None, "unclear", "unclear", "unclear",
      "T = NFE from Table 2 ablation; gen length 256 inferred from Original NFE=256. Table 1 for same cell: " + extra + ". Ablation rows -AGD and -CBS not recorded. "
      "'Original' decoding rule and temperature not stated in extract; HTML lookups did not find them.")
tp = [  # model, task, baseQ, baseTPS, dawnQ, dawnTPS, speedup
    ("LLaDA-8B-Instruct", "MATH", 33.20, 14.10, 32.36, 48.16, "3.42x"), ("LLaDA-8B-Instruct", "MBPP", 29.60, 9.46, 30.80, 45.17, "4.77x"),
    ("LLaDA-1.5", "GSM8K", 81.12, 9.65, 80.82, 43.24, "4.48x"), ("LLaDA-1.5", "HumanEval", 43.90, 9.26, 42.07, 29.53, "3.19x"),
    ("Dream-v0-Base-7B", "GSM8K", 76.42, 14.37, 73.54, 25.88, "1.80x"), ("Dream-v0-Base-7B", "HumanEval", 38.41, 20.90, 39.63, 68.96, "3.29x"),
    ("Dream-v0-Instruct-7B", "MATH", 37.80, 17.73, 38.22, 44.18, "2.49x"), ("Dream-v0-Instruct-7B", "MBPP", 54.20, 8.37, 55.80, 44.03, "5.26x")]
for model, task, bq, bt, mq, mt, sp in tp:
    U(rid, "Table 1", task, model, None, "Acc (%)", "DAWN", mt, "other", mq, "Original (default sampler)", bt, bq, [], None, "unclear", "unclear", "unclear",
      f"T = TPS (tokens per second), {FASTER} Printed speedup {sp} vs Original. Generation length not stated for this cell (256 for GSM8K/HumanEval LLaDA/Dream-Instruct per Table 2 NFE). "
      "Confidence, KLASS, LocalLeap rows exist but are other baselines.")

# ---------------------------------------------------------------- AW0422 Elastic-Cache (Tables 1, 3, 6)
rid = "AW0422"
ec = [  # model, table, task, gen, baseQ, baseTPS, mQ, mTPS, speedup
    ("LLaDA-1.5", "Table 3", "GSM8K", 256, 80.36, 6.7, 81.50, 58.0, "8.7x"), ("LLaDA-1.5", "Table 3", "GSM8K", 512, 81.35, 2.6, 81.35, 117.2, "45.1x"),
    ("LLaDA-1.5", "Table 3", "MATH", 256, 33.52, 8.5, 33.50, 51.0, "6.5x"), ("LLaDA-1.5", "Table 3", "MATH", 512, 35.63, 5.0, 35.36, 74.8, "14.9x"),
    ("LLaDA-1.5", "Table 3", "HumanEval", 256, 43.29, 7.0, 36.59, 20.9, "3.0x"), ("LLaDA-1.5", "Table 3", "HumanEval", 512, 40.85, 3.2, 37.80, 16.8, "5.3x"),
    ("LLaDA-1.5", "Table 3", "MBPP", 256, 38.00, 2.4, 41.20, 32.7, "13.5x"), ("LLaDA-1.5", "Table 3", "MBPP", 512, 38.20, 1.0, 39.00, 32.8, "32.8x"),
    ("LLaDA-Instruct", "Table 1", "GSM8K", 512, 77.10, 3.6, 77.71, 90.1, "25.2x"), ("LLaDA-Instruct", "Table 1", "MATH", 512, 37.20, 7.1, 36.60, 59.3, "7.9x"),
    ("LLaDA-Instruct", "Table 1", "HumanEval", 512, 43.90, 17.7, 46.34, 100.7, "5.0x"), ("LLaDA-Instruct", "Table 1", "MBPP", 512, 15.0, 4.7, 15.6, 63.0, "13.4x")]
for model, tab, task, gen, bq, bt, mq, mt, sp in ec:
    sweep, sb = [], None
    n = (f"T = throughput in tokens/s, {FASTER} Baseline = first column (plain model, fixed tokens per step, no cache), printed 1.0x; Elastic-Cache printed {sp}. "
         "The Fast-dLLM and 'confidence-aware, no cache' columns are other comparators.")
    if model == "LLaDA-1.5" and task == "GSM8K" and gen == 512:
        sweep = [[2.6, 81.4], [5.1, 79.8], [10.3, 67.5], [17.2, 81.9], [26.6, 79.6]]
        sb = "Table 6"
        n += (" Sweep = Table 6 'Baseline' row at 1, 2, 4 tokens/step, 3.25 tokens/step (confidence threshold eps=0.9) and 5.12 tokens/step (eps=0.7), "
              "stored as [throughput t/s, accuracy] and sorted by throughput; accuracies printed to one decimal in Table 6.")
    U(rid, tab, task, model, gen, "Acc (%)", "Elastic-Cache", mt, "other", mq, "Baseline " + model + " (no cache)", bt, bq, sweep, sb, "unclear", "unclear", "unclear", n)

# ---------------------------------------------------------------- write papers
papers = [
    ("AW0403", "wall-clock", "achieves comparable performance while substantially improving inference efficiency and token utilization", "abstract", True,
     "Efficiency is generated-token count and runtime in seconds (Table 1); no step or NFE counts in extract. Baseline = fixed-length denoising at L=64..2048 with accuracy and runtime (Table 1, HTML text lines 176-400; not in extract). "
     "baseline_swept true because cost varies with L; step counts are not printed. Table 2 (LLaDA-1.5) not read. HTML lookups exceeded the cap of 4 (about 9 incl. reads of the stripped text copy)."),
    ("AW0376", "forward-passes", "leading to improved generation efficiency without sacrificing generation quality", "abstract", False,
     "NFE per example in Tables 2, 6, 7, 9; Table 9 adds TPS and time (not recorded). Baseline Confidence appears at only two cost points (top-1 and +EB), so baseline_swept false under a 3-point rule; "
     "Fast-dLLM, KLASS, Saber and WINO are separately named baselines. Temperature 0 from HTML."),
    ("AW0335", "both", "reducing decoding NFE by 55.7% on average", "abstract", False,
     "Abstract claim is NFE; Table 3(b) also gives wall speedup normalised to Daedal. Baselines vary canvas/length method, not step count; Dream accuracy table (Table 1) not available in extract or HTML text, so Dream not recorded."),
    ("AW0393", "wall-clock", "consistently improves both generation quality and inference efficiency for dLLMs", "abstract", False,
     "Efficiency measured only as TPS (Tables 1-3); no NFE. Generation-length ablation is a figure only (Fig 5). Generation length 256, block 32 from HTML text."),
    ("AW0406", "wall-clock", "achieves up to 68.2X speedup while maintaining generation quality", "abstract", True,
     "Throughput (tok/s, Tables 1,2,8) and latency (Tables 9-11) only; the early-exit mechanism is described as skipping iterations but no NFE is reported. "
     "baseline_swept true only on the generation-length axis (Tables 5 and 13: baseline at 512/1024/2048 with accuracy and tok/s), not steps."),
    ("AW0333", "both", "cutting wall-clock latency by up to 2.43x", "Section 1 contributions; Table 3 (abstract has no speed claim)", True,
     "Table 1 gives LLaDA baseline at S=8,16,32,64 and SpecRef at the same S; claim is that fewer diffusion steps match baseline quality (Table 3 caption). Latency in Table 3 is GSM8K only on RTX 4090. Generation length not found."),
    ("AW0364", "forward-passes", "consistently improves Accuracy ( Acc ) while maintaining high efficiency (lower NFE )", "Table 1 caption", True,
     "Central claim is accuracy; lower NFE is secondary. Baseline (lambda=0) appears for the same score under EB sampler (Tables 1,5), threshold (Table 6) and Top-1 (Table 7): three NFE levels but three different policies, not one parameter sweep. "
     "Acceleration-ratio sweep is a figure (Fig 3)."),
    ("AW0381", "both", "achieves up to a 1.8x latency reduction relative to both traditional diffusion models", "abstract", False,
     "Latency (Table 2, Table 10) and steps (#steps, Tables 3,5,7,13) both reported; Figure 3 Pareto of forward passes is a figure. Baselines are single operating points; Table 5/6 sweeps are of the proposed method. "
     "Table 1 baselines for LLaDA/Dream are quoted from the TiDAR paper (copied); gamma=0.9 and 512 steps for confidence-sampling variants."),
    ("AW0373", "both", "up to $4.7\\times$ speedup over autoregressive decoding", "abstract", True,
     "Speedups are wall-clock relative to AR (Tables 1-4); NFE speedups appear in Table 10 (SDAR-8B, B=16). baseline_swept true from Table 2 (Diffusion config-A/B/C) and Figure 3 (figure only); "
     "Table 1 baseline has only static and dynamic points. Cost direction in units is speedup (higher = cheaper)."),
    ("AW0350", "both", "achieving up to 37% higher throughput at comparable accuracy", "abstract", True,
     "Tok/s and total NFE (Tables 1,2,4,5). baseline_swept true on generation-length axis only (Table 2: Threshold at 256/512/1024 with accuracy and NFE); threshold tau fixed at 0.9. NFE values are totals over the run."),
    ("AW0351", "wall-clock", "achieves up to 7.46x higher decoding throughput", "abstract", False,
     "Throughput in Table 1 (accuracy in Table 2 for Vanilla vs SimSD only). Speculative decoding with a draft model; gamma sweep (Table 3) is of the method. Target model size not stated in Tables 1/2."),
    ("AW0385", "both", "substantially reducing the total number of diffusion steps required", "abstract", False,
     "Table 1 speedups are step-speedups; Table 5 gives wall-clock speedups. Baseline Full Decoding has one operating point per task (steps in Table 4); thresholds in Tables 2,3 vary the method."),
    ("AW0389", "both", "DAWN speedups the inference by 1.80-8.06x over baselines", "abstract", False,
     "TPS and speedup (Table 1) and NFE (Table 2 ablation, 2 models x 2 tasks). Generation-length and block-length sweeps are figures only (Figs 4,5)."),
    ("AW0422", "wall-clock", "consistent speedups: $8.7\\times$ on GSM8K (256 tokens), and $45.1\\times$ on longer sequences", "abstract", True,
     "Throughput in tokens/s only. Table 6 gives the baseline at five schedules (1, 2, 4, 3.25, 5.12 tokens per step) on GSM8K LLaDA-1.5 512 with accuracy and tok/s; Table 7b gives Fast-dLLM at 256/512/1024 lengths."),
    ("AW0352", "wall-clock", "attains average wall-clock speedups of 5.52x on Qwen3-4B", "abstract", False,
     "Block-diffusion drafter for speculative decoding of autoregressive Qwen3 / GPT-OSS targets; speedup and acceptance length only, no task-quality metric, so no units. Baseline EAGLE3/DFlash have one operating point."),
]
prow = []
for rid_, kind, quote, loc, sw, note in papers:
    prow.append(dict(record_id=rid_, arxiv=ARX[rid_], speedup_kind=kind, claim_quote=quote, claim_location=loc, baseline_swept=sw, note=note))

# ---------------------------------------------------------------- validate
errs = []
for r in prow:
    if list(r.keys()) != PAPER_KEYS:
        errs.append(("paper keys", r["record_id"]))
    if r["speedup_kind"] not in KINDS:
        errs.append(("kind", r["record_id"]))
    if r["claim_quote"] and len(r["claim_quote"].split()) > 15:
        errs.append(("quote len", r["record_id"], len(r["claim_quote"].split())))
    if not isinstance(r["baseline_swept"], bool):
        errs.append(("swept type", r["record_id"]))
assert [r["record_id"] for r in prow] == [b["record_id"] for b in batch], "paper order/ids"
for u in units:
    if set(u.keys()) != set(UNIT_KEYS):
        errs.append(("unit keys", u["record_id"], set(u.keys()) ^ set(UNIT_KEYS)))
    if u["cost_unit"] not in COST_UNITS: errs.append(("cost_unit", u["record_id"]))
    if u["order_rule"] not in ORDER: errs.append(("order", u["record_id"]))
    if u["decoding"] not in DEC: errs.append(("dec", u["record_id"]))
    if u["baseline_source"] not in SRC: errs.append(("src", u["record_id"]))
    if u["arxiv"] != ARX[u["record_id"]]: errs.append(("arxiv", u["record_id"]))
    for k in ("method_Q", "baseline_headline_T", "baseline_headline_Q"):
        if not isinstance(u[k], (int, float)) or isinstance(u[k], bool): errs.append((k, u["record_id"], u["task"], u[k]))
    if u["method_T"] is not None and not isinstance(u["method_T"], (int, float)): errs.append(("method_T", u["record_id"]))
    sw = u["baseline_sweep"]
    if sw != sorted(sw): errs.append(("sweep unsorted", u["record_id"], u["task"]))
    if any(len(p) != 2 for p in sw): errs.append(("sweep pair", u["record_id"]))
    if (sw and not u["sweep_block"]) or (not sw and u["sweep_block"]): errs.append(("sweep_block", u["record_id"], u["task"]))
    if len(u["note"]) == 0: errs.append(("note", u["record_id"]))
from collections import Counter
cnt = Counter(u["record_id"] for u in units)
if any(c > 12 for c in cnt.values()): errs.append(("cap 12", cnt))
dup = Counter((u["record_id"], u["block"], u["task"], u["model"], u["gen_length"], u["method_name"], u["method_T"]) for u in units)
if any(c > 1 for c in dup.values()): errs.append(("duplicate unit", [k for k, c in dup.items() if c > 1]))
if errs:
    print("VALIDATION ERRORS"); [print(e) for e in errs]; sys.exit(1)

with open(ROOT + "h2-papers.jsonl", "w", encoding="utf-8", newline="\n") as f:
    for r in prow: f.write(json.dumps(r, ensure_ascii=False) + "\n")
with open(ROOT + "h2-units.jsonl", "w", encoding="utf-8", newline="\n") as f:
    for u in units: f.write(json.dumps({k: u[k] for k in UNIT_KEYS}, ensure_ascii=False) + "\n")
print("papers", len(prow), "units", len(units))
for b in batch:
    r = b["record_id"]; us = [u for u in units if u["record_id"] == r]
    p = [x for x in prow if x["record_id"] == r][0]
    print(r, p["speedup_kind"], p["baseline_swept"], len(us), sum(1 for u in us if u["baseline_sweep"]))
