# Progress ledger

## RESUME
- **HANDOFF 66 (2026-10-30 ~00:15 IST; Paper 2 lead session local_81125db6; newest; supersedes 65).** L1 COMPLETE 23:56:49 (450/450, no guard stop; run files 6bc1650f). Scorer pins runs/P2-LRF-PINS/pins.json (fdfd8b97, written 22:42 during L1; deviations-box item). Predictions 0d580242 (positive control 1800/1800). **Family L analysed once (4a01f896): L1 CONFIRMED, BRANCH A** (noise0.1 b 58 c 27, one-sided p 0.00051); L3 jpeg10 not rejected (Holm 0.38); L4 splice128 rejected (Holm 0.049); L-NI shown; L-LEN rejected (n 449). Gate-auditor PASS WITH FIXES (research/paper2/prereg/GATE-AUDIT-FAMILY-L-2026-10-30.md; fixes applied d7c04842; ledger X0004, X0005). Binding wording for branch A: SAP A6 lines 276, 284-301, 307-310 (abstract = L1 + L-NI only; L3/L4 in Results with the harm sentence; no 'generalises', no GATE-M/CLIP comparison claim). **LG RUNNING since 00:00 Fri** (unattended, MEM + slow rule; CNP-S02 messaged; ETA ~02:15-02:30). NEXT: LG COMPLETE -> commit run files -> `python -m exp_p2.gate.lrf_score --run-id P2-LRF-LG --pins runs/P2-LRF-PINS/pins.json --n 300 --conds <LG conds>` (check its --help/L1_CONDS for LG conds) -> commit -> `a6_analysis --l1 runs/P2-LRF-L1/predictions.jsonl --lg runs/P2-LRF-LG/predictions.jsonl --n-rule runs/P2-LRF-PLAN/n_rule.json --out runs/P2-LRF-LG/a6_analysis.json` once -> commit -> gate-auditor -> baselines (no GPU stage running; fix hf_scorer env test with an audit + pin row) -> suite -> writing after the reset (HANDOFF 63 plan).
- **HANDOFF 65 (2026-10-29 ~21:40 IST; Paper 2 lead session local_81125db6; newest; supersedes 64).** Done since 64: re-score COMPLETE 20:55 (A6.2 gate PASS: invariance 0, positive control 0); re-freeze runs/P2-LRF-FROZEN-LFIX model db7fdb4e (D0088, hash set HASHES.json; no accuracy computed); cross-fit delta_cf 0.116 pi_cf 0.228 (exploratory); fold runs/P2-LRF-FOLD 533 (L7 SIGNED); n-rule n_L = 450 (power 0.80 at one-sided 0.05) + plan files (D0089: route C, TNNLS, GPU go D0085); CLIP/SigLIP cached at pinned revisions (5.0 GB). L1 self-check failed twice before any item (0.988, 0.989; runs/P2-LRF-L1.try1/.try2) -> run_gate_m4 deterministic self-check fix 1871fe7d, delta audit PASS WITH FIXES, **card row A-8: pin now 1871fe7d** (pre-launch: git diff --quiet 1871fe7d HEAD -- exp_p2 tools tests); tests/exp_p2 805 pass, 1 env-dependent fail (hf_scorer network test; weights now cached; fix with the baselines stage). **L1 RUNNING since 21:34 (try 3, self-check 0.999), ETA ~01:00-01:30 Fri.** NEXT: after L1 COMPLETE -> `python -m analysis.paper2.lrf.a6_analysis` (read its --help; L family once, commit at once; A6.4/A6.12 branch wording) -> lrf-lg (`--stage lrf-lg --max-chunks 40 --extra <MEM>`) -> a6_analysis LG -> baselines (`python -m analysis.paper2.lrf.baselines`, no GPU stage running; pixel-parity control) -> suite (`--stage suite --max-chunks 12`) -> writing after the reset (HANDOFF 63 plan). H: H-NOGO (H4 not run).
- **HANDOFF 64 (2026-10-29 ~19:35 IST; Paper 2 lead session local_81125db6; newest; supersedes 63).** SHLOK ANSWERED (CONFIRM 17, D0085, verbatim card answers): D-H2 H never in title/abstract/highlights/conclusion; H and Study 2 GPU stages UNATTENDED under the same guards; CLIP/SigLIP download yes (actual size ~5.0 GB, corrected in the ops log; downloading pinned safetensors only). D0086 D-H4 default; D0087 C6-1..C6-11 dated row (19:01:18, after the H3 driver start, before any H3 row; deviations box). Card v4 row A-7 (H preconditions; H-L7 signed by data-steward, research/paper2/data/HL7-SIGNOFF-2026-10-29.md; H-L3 M1/M5 0 overlap by lead). Items: runs/P2-HARDNEG-ITEMS (8f1c338e; leak_check.json). GPU: row 9 S2 figures COMPLETE 18:59 (10 items); H3 COMPLETE 19:23 (50/50, no guard stop); h3_gonogo decide 19:23:51: **H-NOGO, test_fold 0, H4 NOT RUN** (114ed8a4; per-corruption H3 values not opened, C5-6). lrf-rescore RUNNING since 19:25 (500 items, --max-chunks 40, MEM + slow rule; ETA ~22:00); A6.2 gate check (`python -m exp_p2.run_gate_lrf_rescore --check`) after 5 rows. NEXT (A6.10): after re-score COMPLETE + check pass -> `python -m analysis.paper2.lrf.refreeze` -> commit runs/P2-LRF-FROZEN-LFIX hash set + A6.0 item 2 dated row (what was seen before LRF config: S2, FOIL, H3 NO-GO flag) BY MON 09:00 -> `python -m analysis.paper2.lrf.crossfit` (by Mon 10:00) -> `python -m exp_p2.gate.build_lrf_fold` + data-steward L7 -> `exp_p2.gate.lrf_nrule` -> `exp_p2.gate.lrf_plan` -> route/venue dated row (C6-6) -> `--stage lrf-l1 --extra <MEM>` (start by Mon 11:12) -> lrf-lg (by Mon 13:15) -> baselines (CPU/GPU idle, by Mon 15:00) -> suite. RAM: another session's CPU job (Computer Networks paper 2 replay) took RAM to ~2 GB at 18:50; that session was asked to keep >= 6 GB free; check psutil available >= 6 GB before each launch. Ops log = CONFIRM-EVENING section 18. Writing after the weekly reset (Mon ~22:30 IST) as HANDOFF 63.
- **HANDOFF 63 (2026-10-29 ~18:10 IST; Paper 2 lead; newest; supersedes 62).** S2 COMPLETE 300/300 17:58, analysed f205ddec: inconclusive (patch b3 c0, splice b1 c2; Holm 0.5/1.0). FOIL B analysed 10e6bc0f: combination did not beat text direction (b0 c1, n 298). Family H + Study 2 (LRF) code MERGED 725a1b5a (audited PASS; byte-identical to bfae5c35); C5-8 regeneration of M4 analysis/E-dec/E-pred/Tier-3 identical; card row A-6 (c71065b0); pre-launch check `git diff --quiet 725a1b5a HEAD -- exp_p2 tools tests`. GPU IDLE since 17:58, waiting for Shlok: (1) D-H2 (H never in title/abstract/highlights/conclusion) and unattended H runs, (2) GPU go for Study 2 stages (lrf-rescore ~2.5 h, L1 ~4 h, LG), (3) CLIP/SigLIP download. NEXT GPU ORDER (A5.1 amendment; A6 r1 A6.10): H3 (build items with exp_p2/gate/h3_gonogo plan + build_hardneg_items; commit plan files; driver stage h3; must start by Fri 12:27 IST) -> h3_gonogo decide -> H4 -> lrf-rescore (P2-LRF-RESCORE; invariance + positive control must pass) -> re-freeze to P2-LRF-FROZEN-LFIX (hash commit before any accuracy; by Mon 09:00) -> crossfit -> n-rule (by Mon 10:00 else n=520) -> plan files (P2-LRF-PLAN, -LG) -> fresh fold build -> lrf-l1 (start by Mon 11:12) -> lrf-lg -> CLIP/SigLIP baselines (analysis/paper2/lrf/baselines.py) -> suite. Every stage with MEM + --slow-factor 3 --slow-min-s 2 and explicit --max-chunks. WRITING after the weekly reset (Mon ~22:30 IST): TNNLS IEEEtran build in paper2-tnnls/ to the exemplar blueprint; Study 1 (GATE, preregistered, all families) + Study 2 (LRF) as separate studies (AB.1; no problem/solution framing); writer team; Codex thread 01a18699-8f14-79c1-8343-0cdc7c2466f7 review; red team; citation audit; AI only in the Declaration.
- **HANDOFF 62 (2026-10-29 ~17:10 IST; Paper 2 lead; newest; supersedes 61 where they differ).** TNNLS (D0081), Route C (D0082), deadline Tue 3 Nov morning. PREREG: A5 r2 (A5.1 amendment admits A6 once; H and Study 2 are the last families; order S2 -> H3 -> H4 -> LRF re-score at L_FIX=13 -> re-freeze -> L1 -> LG -> baselines -> suite) and A6 r1+r2 (941a260b, 704042f5) signed by red team (91f78475); D0083 (L_FIX re-freeze chosen; old model ca5c4e2f retired), D0084 (conditions; no GATE->LRF problem/solution framing). CODE: family H branch worktree-agent-aef5385b66d6a3cbd b5b41d90 (audited PASS); Study 2 branch worktree-agent-aec5b3a0e0fa71ebc (merges H) fe1fce2c audited PASS WITH FIXES D1 (ChecksFailed final + deterministic cuDNN on re-score) and D2 (crossfit order guard) -> engineer applying now; then narrow auditor check; then MERGE only after S2 completes, with C5-8 byte-identical regeneration of committed M4 analysis/Tier-3/E-dec/E-pred outputs (on a copy, line endings normalised), then a dated card pin row. GPU: S2 at 259/300 16:39, ETA ~17:30 (watcher running); after S2: analysis_s2 --n 300, S2 figures (row 9, --max-chunks 20), analysis_foil analyze (after the S2 table), then H3 (needs Shlok: D-H2 placement + unattended; must start by Fri 12:27 IST), H4, LRF re-score (~2.5 GPU-h; Shlok's go), re-freeze (hash commit by Mon 09:00), cross-fit -> n-rule (by Mon 10:00 else n=520), L1 (start by Mon 11:12), LG, CLIP/SigLIP baselines (download needs Shlok's yes), suite. WRITING: paper2-tnnls/ IEEEtran skeleton (8791558b), checklist, exemplar blueprint (b6130f4d), novelty audits (LRF incremental 0.70, 8416070b), Codex thread 01a18699-8f14-79c1-8343-0cdc7c2466f7 (codex exec needs </dev/null). Writing passes and heavy reviews after the weekly reset (Mon ~22:30 IST). Pending Shlok: D-H2/unattended, GPU go for Study 2, CLIP/SigLIP download, e-gateway (TCPFMC, VGR), author details, AI declaration wording.
- **HANDOFF 61 (2026-10-29 ~14:20 IST; Paper 2 lead; newest).** VENUE: Paper 2 -> IEEE TNNLS (D0081; Shlok rejected TMLR as 'not Q1'); deadline Tue 3 Nov morning (after the weekly reset Mon 2 Nov ~22:30 IST; Shlok). ROUTE C (D0082): new method = learned reliability-aware evidence fusion (LRF, logistic-GAM token weights on caption-withheld features); post hoc evidence bdc87e4e (noise0.1 +0.102 [+0.060,+0.144]); frozen model in progress (runs/P2-LRF-FROZEN, research/paper2/posthoc/LRF-FROZEN-2026-10-29.md; also tests caption-length leak). A6 confirmatory prereg DRAFT 71c78306 (n=520 fresh fold; L1 one-sided McNemar noise0.1 LRF vs NONE; held-out shot/impulse/speckle; CLIP/SigLIP descriptive); BLOCKER: A5.1 stop rule C5-3 must be amended by red-team BEFORE any H3 item (red-team running); A6 code being built on a worktree branch (merges family H branch b5b41d90). GPU: S2 running (165/300 at 13:58, ETA ~18:00); then family H (code audited b5b41d90; merge only after S2 + byte-identical regeneration of P outputs C5-8; needs Shlok's own words on D-H2/D-H4 + unattended, else attended); H3 must start by Fri 12:27 IST; then A6 runs (L1 by Mon 11:18). FOIL test done (298), analysis waits S2 table. Suite and Omni: suite last, Omni not run (P+ empty). TNNLS assets: template/checklist/skeleton paper2-tnnls/ (8791558b); exemplar study research/paper2/tnnls/EXEMPLARS-2026-10-29.md (b6130f4d; e-gateway list: TCPFMC 10.1109/TNNLS.2026.3661974 first, VGR); designs A/B (SCER, CANAL) + novelty audit e2510e79 + Codex review 3556df15 (session 01a18699-8f14-79c1-8343-0cdc7c2466f7; codex exec needs </dev/null). Paper 3 (XBC) ON HOLD. Pending Shlok: D-H2/D-H4 + unattended H; e-gateway sign-in; author details/ORCID; AI-declaration wording; venue exclusivity (GATE not elsewhere). Rules: memory paper-presentation-rules, study-target-journal-exemplars, ml-expert-model-choice, quality-over-token-budget; AI only in the Declaration.
- **HANDOFF 60 (2026-10-29 ~08:20 IST; Paper 2 lead; newest).** Overnight: A4 r1-r3 (red team signed with conditions, all met), D18 reading 1 under Shlok's delegation (D0076, D0077), theory addendum r1 (Prop 2 correlated-token gating in method.tex 5794ddbb; Prop 1 withdrawn, known result; D0078-79; runs/P2-THEORY-CHECK). M4 COMPLETE 500/500 02:53; analysis.json 1028fb9a: P label NEGATIVE (R2; jpeg b/c 0/1, noise 0/0, splice 1/3; gains/losses >0.05 excluded); E-dec/E-pred cd0174ac. Windows Update restarted the laptop 02:59 (not a crash; NVIDIA driver unchanged 595.71; M5 killed after 1 item; ops log a726c05f). Tier-3 fusion merged (pin row A-4, code d81858c0; 584 tests) and run 758a11e7: GATE-M beats median/20%-trim by 2-3 points on JPEG/splice, indistinguishable from flag-rate trim and soft weights. M5 COMPLETE + coherence a451a92d. S2 run card 697af03a (three arms). FOIL-first confirmed (17500581) and decided true. FOIL fit RUNNING since 08:14 (240 items), then foil-test, S2 smoke 8a, S2 (--max-chunks 60), S2 figures, suite. Omni rows not run (P+ empty, AD.7). Next CPU: results writing (outcome book NEGATIVE, reading 1), 35-page cut, reference drop list (52>50) for Shlok, Zhou & Lu full text via e-gateway (Shlok).
- **HANDOFF 59 (2026-10-28 ~23:35 IST; Paper 2 lead; newest).** Shlok answered 'All recommended' (19:14), gave his co-attestation, and said quality beats token caps (memory quality-over-token-budget). M1 analysed (k=200): chance bar PASSED; K2 met (q near chance on JPEG/noise, texture rival wins; D0074). M2 stopped twice on the 2x slow-item rule (idx 105, 113; GPU idle waiting on host); Shlok 'Yes, both' then delegated: slow-item flags built (f2f7b2e1, delta audit PASS WITH NOTES 73e723f9), card v4 rows A-1/A-2 (pin f2f7b2e1; --slow-factor 3 --slow-min-s 2 on every stage), D0075. M2 COMPLETE 300 (threshold.json bae8143f; c1_cal 0.880). Benchmark: Shlok's quality bar Moser et al. TNNLS 2025; lens reports, PANEL-P2-PLAN (mdm-expert), REDTEAM-P2-PLAN (sigma=None verified as UniDisc's path; key check e954217e: all 342 tensors match) in research/paper2/benchmark/. SAP addendum A4 r1 (f1671c91; Tier-3 robust/soft combiners, outcome book, FOIL-before-S2 time rule) committed before family.json; red team SIGN WITH CONDITIONS (b3504aa3); HARM/MIXED sentences need re-signature; D18 reading NEEDS SHLOK before analysis_m4. M3 COMPLETE; family.json R2, test fold 500, endpoint Y (f6ad4c56); ps_frozen 34b480ae; epred-fit COMPLETE, epred_frozen a5a586ca. M4 RUNNING since 23:10 (--n 500 --tbv auto; ~2.2 items/min, ETA ~03:00). Figures F2-F5 built (01c4254b); manuscript writer pass 1 running. Next: M4 -> Omni window-closing row -> Shlok's D18 sentence -> analysis_m4 (commit P section at once) -> comparator code (isolated worktree, audit, pin row) -> M5 -> FOIL/S2 per A4 time rule -> Omni -> suite. Review lessons sent to dlm-paper1-manuscript.
- **HANDOFF 58 (2026-10-28 ~17:20 IST; Paper 2 lead; newest).** All building done on CPU; GPU idle since the 10:26 M1 guard stop, waiting for Shlok's answers in research/paper2/CONFIRM-EVENING-2026-10-28.md (items 1-2 block the GPU; 9 blocks S2/FOIL-test). Built: swap in M4 + ps_freeze, S2 re-infill (n=300), FOIL family B (L7 PASS), imagecorruptions suite (installed at c959e659), Omni-Diffusion 4-bit adapter + timing + R (adapter_signature.json, GPU checks pending), E-dec/E-pred (fit code frozen, EPRED-FIT-AUDIT PASS), A3b chance-bar/partial-pool code. SAP addenda A3 + A3b (+A3b.12) by statistician; red team SIGN WITH CONDITIONS on A3; audits parts 1-3 PASS WITH FIXES, re-audit PASS at code 9c4e1e25; card v4 research/paper2/prereg/PREREG-GATE-v4-2026-10-28.md (49c1f492; pins runs/P2-GATE-CARD-V4/pins.json; SAP LF e33f078c / CRLF d95fb87b). Note: LEAD-DECISIONS-2026-10-28-PM.md items 6-8 were appended after card v4 hashed it (8ff4b773); card's hash covers items 1-5. Next on Shlok's yes: message parallel sessions, then driver per card v4 run sheet: M1 resume (p2) -> m1 -> M1 close+analysis -> M2 -> M3 -> ps_freeze -> epred-fit -> M4 -> M5 -> S2 -> FOIL -> Omni -> suite.
- **HANDOFF 57 (2026-10-28 ~13:45 IST; Paper 2 lead).** Shlok after his review: continue building; he answers confirmations in the evening. M1 STOPPED 10:26 by the watchdog (whole-GPU 10,509 > 10,000 MiB, 106/200; no crash, boot unchanged); GPU idle until Shlok answers research/paper2/CONFIRM-EVENING-2026-10-28.md (proposal: ceilings 11,000/11,000, rise 4,500, cap 0.75). Coding wave A (swap + S2 n=300), B (FOIL n=300 + imagecorruptions + 179-item chance bar), C (Omni 4-bit adapter + timing + R) dispatched on sonnet; next E-dec/E-pred fit code, auditor, card v4.
- **HANDOFF 56 (2026-10-28 ~10:40 IST; Paper 2 lead; PAUSED at 11:00 for Shlok's review).** Shlok in this session: M0 yes, guarded unattended runs yes, the three significance additions plus more, no budget cap, pause at 11:00. The GPU HOLD was released (f12c455d). M0 passed all three stages (93f230bc). M1 (probe-2 completion) is running detached via gate_driver --stage p2 (runs/P2-GATE-M1-p2.driver.out); it halts for good on a guard stop or crash event. Debate round 1 and lead decision: research/paper2/debate/; SAP addenda A2 + A2b, red-team signature with conditions, lead attestation (research/paper2/prereg/). Status for Shlok: research/paper2/STATUS-1100-2026-10-28.md. Next after his continue: code for swap in M4, S2 re-infill, FOIL (data-steward check first), Omni adapter, E-dec/E-pred fit code, the 179-item chance-bar variant; then a gate-auditor check, a card v4 pinning SAP 7ba0c117 (LF) / 9413de75 (CRLF), then M2+M3 -> M4 -> M5 -> S2 -> FOIL -> Omni. Paper 2 deadline: Fri 30 / Sat 31 Oct.
- **HANDOFF 55 (2026-10-28 ~09:40 IST; Paper 2 lead; newest; paused for Shlok's review until he says continue).** Since HANDOFF 54: the code is pinned at 623faaff (prereg card v3 amendment A1: pin check needs blob and working copy; dirty-tree refusal, exit 11; slow-item 1 s floor). The delta audit PASSes (research/paper2/prereg/GATE-CODE-REAUDIT-2026-10-28.md); 209 tests pass. The outcome-independent manuscript draft compiles (paper2/main.tex, sections/*, 49-entry references.bib, 35 todos). Status and decisions for Shlok: research/paper2/MORNING-2026-10-28.md, including the significance and validation plan and the GPU needs. GPU HOLD unchanged; no GPU used since 23:25 on 27 Oct. Next, on Shlok's yes: the pre-launch check at 623faaff with a clean tree, then M0. Recommended additions to raise significance (his call): patch and swap in family P (disclosed), S2 re-infill with real repaired images, E7 second model. Weekly budget used this session: about 7 points (21% to 28%; Fable 0%).
- **HANDOFF 54 (2026-10-28 ~08:20 IST; Paper 2 lead; newest; overnight CPU-only work).** GATE is fully specified, preregistered and coded; no GPU was used and there were no crashes. Read research/paper2/MORNING-2026-10-28.md first. Freeze: research/paper2/prereg/PREREG-GATE-MUST-v3-2026-10-28.md at code commit 164a18a5 (SAP research/paper2/prereg/SAP-GATE-2026-10-28.md with addenda 1-2; folds runs/P2-GATE-FOLDS/folds.json). 202 CPU tests passed in 10 of 10 runs; code audit, re-audit and delta audit all PASS (research/paper2/prereg/GATE-CODE-*.md). Red team: SIGN WITH CONDITIONS, 0.6. The crash diagnosis points to an NVIDIA driver TDR. Probe 2 is still on HOLD (runs/P2-PROBE-02/HOLD.txt). Next, with Shlok present and his yes: M0 staged GPU test per the card's commands; decisions D1-D19 are in card section 15. Before M0, make the gpu_guard pin check also reject uncommitted edits (delta audit N4). Third-party code snapshots in research/sources/code_{dd,disp,fc} are deliberately not committed.
- **HANDOFF 53 (2026-10-27 ~23:50 IST; Paper 2 lead; newest).** Omni-Diffusion is installed: the clone c4f4625f plus the GLM-4-Voice and Matcha-TTS submodules in models/third_party/Omni-Diffusion, .venv-omni with torch 2.11+cu130. Security verdict: SAFE WITH CAVEATS (research/paper2/team/OMNI-DIFFUSION-SETUP-2026-10-27.md). Use trust_remote_code=False with the repo's registered classes, attn_implementation=sdpa and use_safetensors=True for MAGVIT; there is a deepspeed shim in the venv. MAGVIT-v2 and SenseVoiceSmall (1.3 GB) are downloading detached (log runs/downloads/omni-extras-2026-10-27.log). Read SenseVoiceSmall's model.py and pin its revision before the first load. No GPU work until Shlok says so (probe 2 HOLD). Next session: CPU diagnosis of probe 2 versus probe 1; then, with a GPU go-ahead, a 4-bit Omni-Diffusion load behind gpu_guard. This session's context is ~250k, so start a fresh session.
- **HANDOFF 52 (2026-10-27 ~23:35 IST; Paper 2 lead; newest).** Shlok's decisions are recorded in research/paper2/IDEAS.md: GATE; Omni-Diffusion code approved; Declaration-only AI disclosure; guarded probe 2 restart. Probe 2 restarted at 23:22 with the safeguards and crashed the laptop again (~23:25, 0x116, GPU memory to 12.1 GB) after item 20 (21/200 done). Probe 2 is ON HOLD: runs/P2-PROBE-02/HOLD.txt, and the driver exits 7 while it exists. Shlok asked that the overnight sessions not be crashed again, so there is no Paper 2 GPU work tonight, and the parent session was asked to keep the GPU idle. The Omni-Diffusion install agent (no GPU, CUDA_VISIBLE_DEVICES empty) was resumed; its partial state is the clone at models/third_party/Omni-Diffusion (c4f4625) and .venv-omni; report due at research/paper2/team/OMNI-DIFFUSION-SETUP-2026-10-27.md. Next: CPU-side diagnosis of probe 2 versus probe 1, and Shlok's call on an NVIDIA driver reinstall, before any GPU retry.
- **HANDOFF 51 (2026-10-27 ~21:15 IST; Paper 2 lead; newest).** Probe 1 COMPLETE 300/300 at 20:09; summary in runs/P2-PROBE-01/summary.json; kill rule not met (text 0.730, image 0.783; caption-only control 0.497; PMI exploratory 0.940/0.990). Probe 2 started 20:12 and the laptop crashed at 20:20 (bugcheck 0x116, GPU memory full at 12.1 GB) with 20/200 items; it needs Shlok's go-ahead plus a memory cap before any restart. Report: research/paper2/probes/PROBE-REPORT-2026-10-27.md; the IDEAS.md probes section is filled and decision 6 (GPU restart) added. Omni-Diffusion weights DONE (snapshot 2233ee1a; two stale .incomplete blobs from the stopped duplicate downloads remain). The probe agent (acea0bcafa5cb65f3) died with the reboot. Open for Shlok: decisions 1-6 in research/paper2/IDEAS.md.
- **HANDOFF 50 (2026-10-27 ~18:25 IST; Paper 2 lead; newest; Shlok's network may drop ~18:45).** The probe 1 driver had crashed at 16:45 (nvidia-smi returned empty output once; exp_p2/common.py gpu_state() now retries and fails closed). Its GPU-memory busy gate went from 1500 to 2500 MiB because the idle baseline was ~1550 MiB (desktop apps plus a uvicorn app on port 8000 that is not ours); the utilisation gate (<30%) is unchanged. The driver was relaunched detached at 18:21 (`.venv\Scripts\python.exe -m exp_p2.driver --probe 1 --run-id P2-PROBE-01 --n 300`, output in runs/P2-PROBE-01.driver.out); it was at 58/300 and needs no network. The probe agent (acea0bcafa5cb65f3) has ended, so nobody starts probe 2 automatically. Next: when driver.log says COMPLETE, run probe 2 (smoke first) via exp_p2.driver --probe 2, write research/paper2/probes/PROBE-REPORT-2026-10-27.md, and fill the last section of research/paper2/IDEAS.md. The Omni-Diffusion download was restarted detached with 720 retries of 60 s (scratchpad dl_long.py, log runs/downloads/omni-diffusion-2026-10-27.log). At restart, shards 1, 3 and 4 were complete and shard 2 was 4.5 GB in; the duplicate download processes were stopped. Shlok's 5 decisions are unchanged.
- **HANDOFF 49 (2026-10-27 ~16:40 IST; Paper 2 lead; newest; app restart requested by Shlok).** Interrupted mid-probe. State on disk: probe code in exp_p2/ (run_probe1/2, scoring, driver); P2-PROBE-01 (UniDisc caption-likelihood matching, 300 COCO images) had 13 of 300 items in runs/P2-PROBE-01/items.jsonl; P2-PROBE-02 (token-reliability AUROC) not started; report research/paper2/probes/PROBE-REPORT-2026-10-27.md not written. Resume: relaunch the last command in runs/P2-PROBE-01/driver.log (`.venv\Scripts\python.exe -m exp_p2.run_probe1 --run-id P2-PROBE-01 --n 300 --resume --duty 0.5 --soft-minutes 12.5` via exp_p2.driver / tools/gpu_guard.py), then probe 2 per the brief in research/paper2/IDEAS.md (red-team probes 1-3), then fill the last section of IDEAS.md. Omni-Diffusion weights download was at 3.3 of ~16 GB; resume by rerunning the snapshot_download (resumable). Open for Shlok: the 5 decisions at the end of research/paper2/IDEAS.md.
- **HANDOFF 48 (2026-10-27; Paper 2 lead, session frosty-clarke-209639; newest).** Paper 2 switched to a new method article on multimodal masked discrete diffusion for Information Fusion (brief research/paper2/MASTER-BRIEF-2026-10-27.md). Done: global skill ~/.claude/skills/assembling-expert-teams; project team (mdm-expert, gpu-runner; models and safety checks in tools/build_agents.py; research/paper2/team/TEAM.md); repo security audit (4 repos safe to read, none copied); Information Fusion style guide and method-paper anatomy (research/paper2/style/); 70 project Codex sessions archived (research/paper2/team/CODEX-ARCHIVE-2026-10-27.md); 7 ideas, novelty audit and red team -> research/paper2/IDEAS.md (recommend A: GATE reliability-gated conditioning on UniDisc). Running: UniDisc probes P2-PROBE-01/02 (report research/paper2/probes/PROBE-REPORT-2026-10-27.md); Omni-Diffusion weights download (runs/downloads log). Blocked: cloning/installing Omni-Diffusion code (permission check; Shlok to decide). Next: Shlok picks the idea; then preregister and run. Weekly usage 17 percent at this line.
- **HANDOFF 47 (2026-10-21; revision lead dc7ef7d8; newest).** Publication-level clarity pass on every main section and the supplement (brief research/review/EDIT-BRIEF-2026-10-21.md; number, citation and label integrity checked with scripts/integrity_diff.py); Sections 9 and 11 kept at their shorter reviewed versions for length; taxonomy tree moved to Supplement S5.1; generated captions without decision IDs; main 34 pp incl. references, supplement 59 pp; checks 0 problems. Stopped at 96 percent weekly usage.
- **HANDOFF 46 (2026-10-21; revision lead dc7ef7d8; D0072; newest).** Professor's second review applied (see research/RESPONSE-TO-PROFESSOR-2026-10-21.md, second part): Section 2 rewritten, AI only in the Declaration, main 34 pp incl. references, DOCX layout checked in Word; desk check in research/review/audits/2026-10-21-desk-check.md. Open: 1,242 unscreened seed records (stated as threat); ACM policy asks AI in Methods (author chose Declaration only).
- **HANDOFF 45 (2026-10-21; revision lead dc7ef7d8; D0070; newest).** The author's reviewed check sheets replace
  research/HUMAN-CHECK-*.xlsx; agreement rerun with the committed scripts: screening 18 of 24 decided, kappa 0.50
  (0.12 to 0.83), 16 unclear (no readable full text), code 9 of 9; extraction and census value rule unchanged; census
  headline 21 of 24. Methods, Limitations and Supplement S9 call them the author's own checks; AI appears only in the
  Declaration (ChatGPT sentence removed at the author's word, D0071). scripts/human_checks_update.py. main 37 pp, checks 0.
- **HANDOFF 44 (2026-10-21; revision lead session dc7ef7d8; professor's assessment, D0069; newest).** Commits b2ef278
  to c68559c. AI model names only in the Declaration (rewritten positively); no repository paths in prose
  (paper/review/scripts/final_checks.py: 0 problems in main.pdf, supplement.pdf, main.docx). New Section 8 "What the
  evidence means for practice" (sections/075-practice.tex: exemplar table, decoding defaults, checklist); per-RQ
  summary table in Section 5; Section 2 detail and census agreement table moved to supplement; verdict robustness
  (analysis/extraction/d0052/revision_sensitivity.py) and census by year/venue (analysis/census/census_by_year_venue.py);
  13 references verified via arXiv API (scripts/revision_refs.py); OP4 preregistrable design, OP5 bracketing V;
  human-validation plan in Section 11. Response: research/RESPONSE-TO-PROFESSOR-2026-10-21.md. At the author's request
  EXP-003 became a short subsection of Section 9 and the Section 7 step-sweep corollary moved to Supplement S8
  (scripts/revision_move3.py); then the formalism figure and the lever table moved to Supplement S8 (Figure S2,
  Table S15; scripts/revision_move4.py; supprefs.py now also emits \suppTabLevers and \suppFigFormalism). main.pdf
  37 pp (text to p32, references 5) against the 35-page target of D0068. Hostile-referee pass (research/review/audits/2026-10-21-revision-redteam.md): no number or name
  failures; findings 1-11 fixed in 3cdbd48 (scripts/revision_redteam_fixes.py); 12 (PSD in bib, uncited) harmless.
  Not done: research-humanizer pass on new text; release rebuild/push. Stopped at 94 percent weekly usage. Build order unchanged; make_docx.py now resolves
  \csname @@input\endcsname table inputs. Heredocs collapse backslashes here: use Write/Edit for .tex edits.
- **HANDOFF 43 (2026-10-21; orchestrator 00fe9279/0839c9f4 stopping at 95 percent context; newest).** State:
  branch claude/resume-dlm-discovery-exp-003-334706 at 5ecae26, all committed; release pushed to private
  shlokDS16/dlm-review-prisma at a667ce3; Zenodo 10.5281/zenodo.23524470 published v1.0.0 (its zip predates the
  dataset citation and later edits; a new version is optional; creator 2 shows family/given swapped on Zenodo).
  main.pdf 35 pp, supplement 48 pp, docx/main.docx (layout script make_docx.py; 7 equations, 6 tables).
  **Open, for the revision lead session:** (1) USER DECISION (relayed by 9d5203d7, user's words: "A sub chat is
  asking whether ai models needs to be removed from the paper so yeah it should be removed." and "portray use of ai
  in positive manner, I will still recommend to keep ai only in declaration of ai statements."): remove AI model
  names from the supplement too, keep AI only in the Declaration on the use of AI, framed positively; record as a
  decision row. Keep "automated" once in Methods (integrity note). (2) 8 arXiv references have published versions;
  22 anonymous ICLR citations to update when reviews close; R0963 (Bernini) scope question for the author.
  (3) research/AUTHOR-CHECKS-2026-10-21.md user items; ORCIDs, corresponding author, funding and competing
  interests placeholders; cover letter draft research/COVER-LETTER-paper1.md. Idle side sessions: paper1-fixes-abc
  (fixes A-C done), paper1-fix-d-landmark (landmark tranche, D0061-D0064), paper1-docx-quality (Word layout script),
  paper1-screening-check (author checks, D0065-D0068, AI declaration, S6 references, taxonomy figure). Build order:
  latexmk main; scripts/mainrefs.py; latexmk supplement; scripts/supprefs.py; latexmk main; then
  `python -E -P -W ignore paper/review/scripts/make_docx.py`; release: tools/build_release_paper1.py then
  tools/sync_release_repo.py.
- **HANDOFF 42 (2026-10-21; side session of 00fe9279; D0067 AI declaration, D0068 references, Yang-style pass).**
  AI use only in an unnumbered "Declaration on the use of AI" (main.tex, before the references); Section 2.8, Table 2,
  the abstract's last sentence and the Section 10 "Use of AI" paragraph removed; Methods say "automated" with a
  pointer; supplement keeps the detailed record with model names. Introduction: taxonomy tree of the 47 design-space
  models (scripts/fig_taxonomy.py, forest; cropped into the DOCX by make_docx.py), which adds 12 main citations (main
  list 81). Supplement Table S6 cites all 80 appraised studies (scripts/s6_bib.py arXiv/Crossref with title match;
  s6_bib_local.py from page 1 of the screened text because OpenReview's API now needs a bot challenge; s6_bib_fix.py
  applies the citation-validator report: 73 OK, 4 FIX, 1 FAIL, all fixed). Unique references 166. Supplement page 1
  marked as the electronic supplement; cover-letter draft research/COVER-LETTER-paper1.md (placeholders).
  hidden-unicode: no carriers in .tex/.bib/tables; DOCX has no author or AI metadata. main.pdf 35 pp, supplement 48 pp.
  Open: 8 arXiv entries have a published version (validator note); 22 anonymous ICLR citations will need updating
  when the reviews close.
- **HANDOFF 41 (2026-10-21; side session of 00fe9279; author checks in the paper, D0066).** Commit 4a634ba: Methods
  2.4/2.6/2.8, Table 2 (ChatGPT row), departure 4, 6.6, Section 10 and new Supplement S9 (Table S12) report the blind
  author checks validated with ChatGPT; twelve adjudicator items confirmed. main.pdf 35 pp, supplement 43 pp, DOCX
  rebuilt, AI-USE-STATEMENTS updated, release pushed (dlm-review-prisma ea90215; now includes the filled sheets).
  **Open with the user:** reference count (89 unique now; survey example 290). Proposal: cite the 80 S6 studies in
  the supplement (~167 unique, no page cost) or grow the main list past 150 (~4 more pages, over CSUR's 35).
- **HANDOFF 40 (2026-10-21; side session of 00fe9279; all three author checks returned, D0065).** Sheets copied
  from the user's Downloads into research/ (ids verified against the draws); agreement: extraction 31/34 pairs,
  kappa 0.82 (7 of 12 studies answered); screening 21/30, kappa 0.41 [0.09, 0.71], 10 unclear, codes 11/11, below the
  protocol's 0.70; census Q2 21/24, kappa 0.79, frame-weighted 0.93, Q3 0.86, Q4 0.64. Answers are the author's
  combined with an AI reading (user's words in D0065): the paper says "author checks assisted by an AI system".
  AUTHOR-CHECKS items confirmed by the author (D0065): remove "await the first author's confirmation".
  Full detail and paper wording: research/review/human-checks-results-2026-10-21.md. **Next:** manuscript session
  updates 02-method, 06-census, 10-limitations and the supplement, then the DOCX is rebuilt.
- **HANDOFF 39 (2026-10-21; side session of 00fe9279, after H37; human check 3 of 3, blind census sheet built, not
  yet filled).** analysis/census/human_check_census_sheet.py draws 24 of the 152 census rows with a headline metric
  and an F2 code (census-random-final.jsonl; 6 already-seen papers left out), stratified 12 non-plain / 8 not stated
  / 4 plain, seed 20261024. Sheet research/HUMAN-CHECK-CENSUS.xlsx ("check": census headline shown as anchor, with
  decoding-setting parentheticals stripped; Q1 headline right, Q2 value-rule class + optional letters, Q3 diversity,
  Q4 step sweep; "rules" = codebook v1-v1.2 in plain language); model answers analysis/census/human-check-census-
  model-answers.json. All 24 arXiv links return 200; local texts are in the MAIN checkout's research/sources/
  census-text. Instructions: AUTHOR-CHECKS Part 5. **Next:** when returned, run
  `python -E -P analysis/census/human_check_census_agreement.py` (tested on a dummy copy; reports raw and
  frame-weighted agreement because plain is oversampled).
- **HANDOFF 38 (2026-10-21; side session of 00fe9279; Word layout).** paper/review/scripts/make_docx.py Word pass
  rewritten for journal layout (commit 350801c): A4, 2.5 cm margins, Times New Roman 11 pt justified, 1.15 lines,
  0.5 cm first-line indent except after heading/figure/table/algorithm (conventions of the ISPRS, eTransportation,
  TPAMI and AIR Word manuscripts), figures to the 16 cm text width (height cap 20 cm) centred and kept with
  captions, tables with widths from the LaTeX column specs plus measured text, booktabs rules, bold header,
  right-aligned numeric columns, rows unsplit; numbered equations as a borderless row with the number at the right
  margin; references with hanging indent; auto-hyphenation (off in headings, title block, cells, references).
  Text check: 644 paragraphs equal to the previous build; 217 links, 140 bookmarks, highlight kept. Word export
  35 pages (was 38). Release folder rebuilt (2,687 files, secret hits 0) and pushed (dlm-review-prisma 4ff7a8b).
  Word export: PowerShell COM (Documents.Open read-only, ExportAsFixedFormat(out, 17)).
- **HANDOFF 37 (2026-10-21; side session of 00fe9279; human check 2 of 3, blind screening sheet built, not yet
  filled).** analysis/screening/human_check_screening_sheet.py draws 20 included + 20 excluded of the 885 final T1
  decisions (t1-decisions-all 882 + D0058 3, D0059 code overrides; 608/277), seed 20261023, after leaving out 28
  records the first author had already seen with a decision (CONFIRM-2026-10-20, AUTHOR-CHECKS Parts 1 and 3, the 12
  extraction-check studies); frame 586/271. Sheet research/HUMAN-CHECK-SCREENING.xlsx ("check" with drop-downs,
  "rules" = criteria v1.6 in plain language); model answers analysis/screening/human-check-screening-model-answers.json
  (user must not open). All 40 have a link (33 respond 200; 6 IEEE DOIs need VIT access; 1 Zenodo link blocks
  scripts) and a local text copy and PDF in this worktree only (git-ignored). Instructions: research/AUTHOR-CHECKS-
  2026-10-21.md Part 4. **Next:** when the user returns the sheet, run
  `python -E -P analysis/screening/human_check_screening_agreement.py` (tested on a dummy copy) and report kappa
  with its bootstrap interval in the paper; the census check (3 of 3) is still to build.
- **HANDOFF 36 (2026-10-21 ~14:30 IST; session bfefb6fe; fix D done, full D within the user's budget).** Landmark
  tranche L (D0061): the 44 design-space models whose papers are not among the 615 (41 unscreened S1243 seed records +
  3 D0026 string-filter drops; agrees with fix B's landmark-coverage.json). Full texts all retrieved (9 fetched,
  35 already on disk) and screened at full text, criteria v1.6, A Sonnet 5.5 / B Opus 5.5, batches lmkb001-006
  (analysis/screening/ft-lmk/): A=B on all 44 decisions, no adjudication, include 42, exclude 2 (X1: M00595 Campbell
  CTMC theory-no-text, M00430 MaskGIT nontext); one I1 split (R0523 A a, B ab; D0039 rule, author item). PRISMA flow +
  Figure 1: "identification via other methods" row (prisma_flow.py landmark_tranche_D0061; existing counts unchanged).
  Extraction (user: "Extract till 90 percent", then raised to 95, D0064): seeded order of the 42 fixed first
  (extraction-order.json, seed 20261024, commit 73c7b4b), one study per EA session, stopped at 87 percent with
  positions 1-16 extracted (D0063); EB Sonnet + EC Fable on R0268, R0326 (second-reader.json; agreement-2/: values
  128/128, signs 30/30, groups 14 of 116 listed). rq_analysis.py: separate stratum L-lmk (N 42, n 16), own column and
  verdicts (RQ2-RQ4 mixed, RQ5 untested; same without the 2 rejected records), every existing value unchanged (JSON
  diff). Paper: Section 2 (landmark paragraph, Figure 1 caption/Description, departures item, AI-use table row),
  Section 5 (RQ1 screening line, one landmark sentence per RQ, verdicts, Table 3 landmark column), Section 10, S1 rows
  8/9/16a, S6 rows + Table S-sens-landmark. Also this session (orchestrator requests): Zenodo DOI
  10.5281/zenodo.23524470 in the data statement (GitHub mirror clause removed), acmart `screen` option, DOCX citations
  linked to ref_n bookmarks + DOI/URL/arXiv links (Word check 129 internal, 86 external). Gate audit
  research/review/audits/2026-10-21-gate-landmark-tranche.md: PASS WITH FIXES (8) -> fixed (response file) -> re-check
  PASS. Decisions D0061-D0064. main.pdf 35 pp, supplement.pdf 42 pp, no LaTeX errors or undefined refs; DOCX rebuilt;
  release folder rebuilt (2,684 files). AI-USE-STATEMENTS-paper1.md pages re-checked. Author items: research/AUTHOR-
  CHECKS-2026-10-21.md part 3 (R0523 I1; EC items for R0326, R0268; proposed lookup ids). Not done: the remaining 26
  landmark includes are not extracted (budget); QA1 link check not run for L. Weekly usage ~90-91 percent.
- **HANDOFF 35 (2026-10-21; newest; side session of 0839c9f4/00fe9279; fixes A, B, C).** Commits 7032442 (A),
  1a4d47f (B), 7bc2f23 (C), 04d2d66 (rebuild). **A:** rq_analysis.py `verdict()` takes thresholds;
  rq-results.json D0060.verdicts_threshold_sensitivity (included column, one threshold changed at a time): direction
  share 0.60 -> RQ4 and RQ5 weakly supported (RQ5 share exactly 0.60); minimum 8 signed -> RQ5 untested; 0.75, control
  0.40/0.60, minimum 3 change nothing. Rows at the foot of Table S9 (qa_tables.py); one sentence in Section 5
  "Verdicts". Existing numbers unchanged (json diff additions only). **B:** scripts/landmark_coverage.py ->
  tables/landmark-coverage.{tex,json}; Table S7 in new S5.4 (sec:s-landmark); sentence in Section 10 "Selection of
  studies" via \suppTabLandmark. Counts: 3 of 47 design-space models included (ARDM, Transfusion, UDLM), 41 of the
  other 44 seed records, 7 of the 44 in the census sample, 32 of the 44 cited in the main text (match by arXiv id or
  normalised title; agrees with the D0061 frame of the parallel landmark-screening session). **If D0061 adds
  includes, rerun landmark_coverage.py and update the Section 10 and S5.4 sentences.** **C:** Section 9 cut to three
  paragraphs (supports the census reading; Delta1 0.126 [0.076, 0.177]; CLIP caveat; PC-1 failed; meaning); table
  tab:exp003-arms, design, full primary result, deviations and reading moved to new S7.6 (sec:s-exp003-main); S7.1-7.5
  numbering kept; \suppTabExp added to supprefs.py; Section 10 ref to deviations -> S7.1. Intro "is the 35 pages" ->
  "fits the journal's limit of 35 pages". **Build:** main.pdf 34 pp, supplement.pdf 40 pp, no errors or undefined refs;
  DOCX rebuilt, Word export 36 pp with 7 tables, 4 images (3 figures + Algorithm 1), same as main.pdf. PDFs are
  gitignored (paper/review/.gitignore), so not committed; they are in the release folder, rebuilt (2,499 files,
  185.7 MB, 0 secret hits), which also holds D0061's unfinished landmark files: rebuild it after D0061 finishes.
  AI-USE-STATEMENTS-paper1.md pages re-checked (item 13 moved to Section 10 / new item 19 S7.6).
- **HANDOFF 34 (2026-10-21 evening; session 0839c9f4 at 80 percent context).** Since H33: abstract cut to
  98 words, third person (CSUR rules); Word version paper/review/docx/main.docx (scripts/make_docx.py; numbering from
  main.aux, refs from main.bbl, placeholders highlighted); research/AI-USE-STATEMENTS-paper1.md; supplement-readme.txt;
  PRISMA items 25-27 pointers; competing-interests placeholder; release folder rebuilt with .zenodo.json and
  CITATION.cff; research/RELEASE-GUIDE-paper1.md rewritten as exact steps (user creates shlokDS16/dlm-review-prisma).
  Pending from user: GitHub link + Zenodo DOI, funding/competing interests/acks, ORCIDs, corresponding author, author
  checks parts 1-2. Open fix options (user to choose; run in a fresh session): verdict-threshold sensitivity (cheap),
  landmark-model coverage statement (cheap), move Section 9 to supplement (moderate), extend extraction or screen
  landmark seed papers (expensive, for revision).
- **HANDOFF 33 (2026-10-21 ~14:30 IST; session 0839c9f4). PAPER 1 READY EXCEPT USER ITEMS.** main.pdf 35 pp
  incl. references, supplement.pdf 37 pp, no LaTeX errors or undefined refs. Gates: Section 5 re-audit PASS WITH
  FIXES (fixed), citation gate fixes applied, census re-verified PASS (audit tags removed), clarity edit verified
  (numbers/keys/verdicts identical). Data and code availability statement added (DOI to-do). Release folder built
  locally by tools/build_release_paper1.py at ..\release\dlm-review-prisma-v1 (2,472 files, 185 MB; nothing
  uploaded). Remaining red to-dos in main.pdf: Zenodo DOI, funding/acknowledgements. User list:
  research/SUBMISSION-CHECKLIST-paper1.md (author checks parts 1-2, ORCIDs, corresponding author, funding, GitHub
  go-ahead, read-through). Build order: latexmk main; scripts/mainrefs.py; latexmk supplement; scripts/supprefs.py;
  latexmk main. Page margin is tight (35 pp exactly): any added text needs an equal cut after the census figure.
- **HANDOFF 32 (2026-10-21 ~11:30 IST; session 0839c9f4).** Gate re-audit: PASS WITH FIXES
  (research/review/audits/2026-10-21-gate-section5-reaudit.md); its text findings fixed (commit 6bf656b: included-only
  claim counts 179, direction-flag agreement 5/8 reported, matched-budget wording, S4/S6 captions). Open: M6 (blind
  human check, user) and supplement.tex:74 todo (prompts and raw outputs for the release). **Page limit met:** main
  35 pp including references (commits 5feb8e1, 0cbce1b, 30c96a8): Section 9 detail -> S7.5; Section 7 mechanisms,
  other terms, revision corollary -> S8.6-S8.8; Section 4 test limits + survey comparison -> S5.3; Section 6 coding
  sensitivity + census limits -> S3.3-S3.4; design-space figure -> S5.1 (Figure S1); census figure 0.82 width.
  Supplement table numbers now generated (scripts/supprefs.py -> supprefs.tex; build order in its docstring) - the
  old hard-coded Table S1/S2/S3 refs were wrong. Supplement 37 pp. **Running:** citation-validator ->
  research/review/audits/2026-10-21-citations-paper1.md. **Next:** apply citation fixes; clarity pass with
  research-humanizer on sections 2 (extraction), 5, 10, 11 and the abstract; recheck 35 pp; census \aud tag decision;
  user items (AUTHOR-CHECKS part 1 and 2); graph-memory sync.
- **HANDOFF 31 (2026-10-21 ~09:30 IST; session 0839c9f4).** EC complete for all 8 (ecx002b void, re-run as
  ecx002c). Gate-auditor FAILED Section 5 (22 findings) and red-team found 1 fatal + 8 major (reports in
  research/review/audits/2026-10-21-*.md). Response: **D0060** (orchestrator, listed for the user): included studies
  (update strata, 59 sampled of 584) primary, seed stratum (20 ~ 1,074) a separate column, stratified bootstrap
  intervals (exact Kish bound for zero cells), verdict thresholds stated and applied mechanically to RQ2-RQ5 (RQ1, RQ6
  described), RQ5 signs by joint arm (rq5-orientation.jsonl), no unit totals, agreement as matched counts (36 of 245
  groups, 150 of 1,227 units, 24 of 28 headline), plus QA-score (65/72), flag (55/62) and claim-status (kappa 0.44)
  agreement. Verdicts (included): RQ2 mixed, RQ3 weakly supported, RQ4 mixed, RQ5 mixed (2 vs 3); unchanged without
  rejected records except RQ5 -> untested, unchanged with extractor B. Section 5, method, limitations, intro, abstract,
  conclusion, S4, S6 rewritten (commit bda6ef7); main 39 pp, supplement 32 pp. EXP-003 confirmatory.json and
  postfreeze.json copied into runs/EXP-003/analysis (sha256 equal to ca3357's). **User items:**
  research/AUTHOR-CHECKS-2026-10-21.md part 1 (12 yes/no checks) and part 2 (blind 12-study check,
  research/HUMAN-CHECK-2026-10-21.xlsx; agreement by human_check_agreement.py, then report it in 02-method and S4).
  **Running:** gate re-audit -> research/review/audits/2026-10-21-gate-section5-reaudit.md. **Next:** fix re-audit
  findings; citation-validator; research-humanizer clarity pass; page cuts to ~35 pp; the census \aud tag (abstract
  vs conclusion) needs the census re-verification closed or the tag removed everywhere; graph-memory sync.
- **HANDOFF 30 (2026-10-21 ~06:30 IST; session 0839c9f4).** **EC adjudication (Fable, alias C):** filed
  ecx001 (M08783, M15033), ecx002 (M16154), ecx003 (M19021), ecx004a (R0171) in analysis/extraction/d0052/EC/;
  ecx002b (M15840) VOID (isolation: one mistyped nonexistent path; kept in EC-void/ with README) and re-run as ecx002c;
  RUNNING ecx004b (R0588, split from ecx004 because the records are 749 KB), ecx002c (M15840), ecx005 (R0738). Filing
  per batch: copy EC-<batch>.jsonl + dispatch.json from the scratchpad ex-dispatch folder (basename in agent-map.txt),
  `python -I tools/ft_model_check.py --transcript <subagents>/agent-<id>.jsonl --role C`, `python -I
  tools/ft_isolation_check.py <transcript> <folder>`, commit. EC "left for the author" items and proposed lookup
  entries are in agent-map.txt comments (to collect into one author sheet). **Agreement on the 8:**
  analysis/extraction/d0052/agreement-8-texts (canonical, with --texts; agreement_8.py): values M-val 616/616, M-sign
  75/76, headline units F1_H 48/52; groups F1_G 72/245, units F1_K 300/1227 (R0588 4/126, R0171 0/24) - below the
  0.6 warning line, disclosed. **Analysis:** rq_analysis.py has sensitivity S1-S3, QA1 full rule with the dated link
  check (qa1_link_check.py; 17/19 resolve; owner reads in qa1-owner-reads.jsonl for author confirmation), dose curves
  along compute, in-frame unit totals. **Manuscript:** Section 5 RQ1-RQ6 drafted from interim results (6 of 8 EC);
  supplement S4 (extraction agreement) and S6 (per-study appraisal, sensitivity) generated by
  paper/review/scripts/qa_tables.py and agreement_table.py; main 38 pp, supplement 32 pp. **Next:** when the 3 EC runs
  finish, file them, rerun rq_analysis.py + qa_tables.py, re-check every Section 5 number against rq-results.json,
  fill the 02-method extraction todo (counts, agreement, rejected-at-final-pass, voided session, verdict definitions
  as a departure), update abstract/intro/conclusion/limitations, then gates (gate-auditor, citation-validator,
  red-team, research-humanizer), cut main to ~35 pp, author sheet for EC items and owner reads.
- **HANDOFF 29 (2026-10-21 ~03:55 IST; session 0839c9f4 at 94 percent context, compacting).** **EA extraction
  DONE for all 80** (exb001-exb033 incl. exb033r; exc001-exc011 incl. exc003r); per-record validator status in
  analysis/extraction/d0052/batch-log.jsonl and validate-pass{1,2}.jsonl; pass-1 files keep groups some extractors
  deleted in pass 2 (M12879 G22-G31, R0717 G03/G08, R0188 arms): use them for an RQ4 sensitivity. **EB second reader
  (Sonnet, role EB, alias A):** ebx001, ebx002, ebx003r filed; RUNNING at 03:55: ebx004 (a1cd3117a9c35494b), ebx005
  (a62f20c0eba377290); then `after.sh ebx00N`, one return, `after.sh ebx00N 2`. **Next:** EC adjudication (Fable) on the
  8 ids: `python -I tools/ex_dispatch.py --role EC --batch ecx001 --ids <8 ids> --records-x <EA jsonl> --records-y <EB
  jsonl> --lookups analysis/extraction/lookups --root <scratchpad ex-dispatch>` (EA/EB records: analysis/extraction/
  d0052/EA|EB/<batch>/*-pass2.jsonl else pass 1); agreement: analysis/extraction/agreement.py (EA vs EB, stage-a mode);
  copy EC records to analysis/extraction/d0052/EC/<batch>/ so rq_analysis uses them. **Interim results (before EC; file
  rq-results.json, script rq_analysis.py):** census replication non-plain-or-unstated 74/76 (update 54/56, seed 20/20);
  RQ2 AR-comparison studies 35/79, budget matched in all AR groups 0/35, budget not reported 31/35, variance 3/35,
  copied AR numbers 7/35, direction mixed (15 better vs 14 worse of 32); RQ3 credited ablation 9/33; RQ4 non-monotone
  step curves 10/19; RQ5 G-mm 20: CT5 claims 3, synergy groups 8; QA8 unsupported-or-contradicted claim 7/74. Then:
  QA1 dated link check (downloads allowed), Section 5 RQ2-RQ6 + appraisal table S6, abstract/intro/conclusion, gates
  (gate-auditor, citation-validator, red-team, research-humanizer), page cuts, PDF. Weekly usage 63 percent at 03:55.
  Limits: D0057 3 agents, >= 4 GB RAM launch; count running agents BEFORE every launch or resume (two over-limit
  launches were stopped tonight).
- **HANDOFF 28 (2026-10-20 ~22:30 IST; newest; session 0839c9f4 continues, context 73 percent, will auto-compact).**
  **User decisions this evening (own words, this session):** D0053 launch >= 4.0 GB RAM; D0054 seed stratum (80 =
  60 update positions 1-20 + 20 seed from census eligible, seed-sample.json); D0055 P2 ok + 3 authors (Shlok Goenka,
  Subramaniyaswamy Vairavasundaram, Balaji G N; SCSE VIT 632014); D0056 model reads/author confirms; D0057 up to 3
  agents, none below 3 GB free; D0058 Job A (M13184/M15873/M17195 X1, R0308 X2); D0059 Job B (9 D0039 fields; M18059
  nonlang -> leaves the sampled frame). Downloads now allowed by the user for what serves the result (planned: QA1
  dated link check after extraction); screening stays frozen. Still open with the user: ORCIDs, corresponding
  author, GitHub/Zenodo go-ahead (research/RELEASE-GUIDE-paper1.md). No launches 23:50-00:10 (hotspot switch;
  CNP session local_ebaf6b57 coordinates RAM/GPU with us).
  **Extraction loop:** batches in analysis/extraction/d0052/batches (exb001-exb033 update phase 1; exc001-exc011
  seed, built with --texts research/sources/md/census-text-paged and an --ft provenance string; exc003 rerun as
  exc003r). Filed: exb001-exb013, exc001-exc004 (+exc003r). Running at 22:30: exb014 (a548b33bdd68ce02b), exc006
  (aa23b043e38e424fe), exc005 return (a080ca3a5530b6134). Agent ids and folders: analysis/extraction/d0052/agent-map.txt.
  Per session: `bash analysis/extraction/d0052/after.sh <batch>` -> send the summarised returns/<batch>.txt once via
  SendMessage to the agent id -> `after.sh <batch> 2`. Use the latest EA prompt text (agent-map notes list the
  added sentences). Analysis: `python -I analysis/extraction/d0052/rq_analysis.py` (census replication, QA8, RQ2-RQ6).
  **Codex** debate research/debates/2026-10-20-2026-10-20-paper1-significance: anchor = census (now replicated on the
  sample) + comparison audit; sensitivity without seed and without validator-rejected records. **Next after
  extraction:** second reader EB on the 8 ids (seed-sample.json second_reader_ids) + EC adjudication; QA1 link check;
  Section 5 RQ2-RQ6 + appraisal table (S6); abstract, intro, conclusion; gate-auditor, citation-validator, red-team,
  research-humanizer; page cuts to 35; PDF. Shared notes: side-session-notes/.../0839c9f4-paper1-build-status.md.
- **HANDOFF 27 (2026-10-20 ~19:00 IST; newest; manuscript session 0839c9f4, scratchpad
  .../0839c9f4-4e83-4067-9eb8-6394e5c875ef/scratchpad; subagents dir .../0839c9f4-.../subagents).** Paper 1
  build under D0051. **Done:** D0052 (extraction sample: draw_pilot stage-a + gate, option (b) frames = (d) frames,
  first 27 of each gate list = 81; second reader on 8, seed 20266300; files analysis/extraction/d0052/, batches
  exb001-exb045 in phase order, phase 1 = exb001-exb033 = positions 1-20); RQ1 counts over 615 includes
  (analysis/rq1/rq1-counts.json); prisma_flow.py seed-count bug fixed (seed arXiv 1158/173, was the 10-15 rerun
  1286/190); Fig 1 rebuilt (paper/review/scripts/fig01_prisma.py, all sums asserted). **Raised to the user
  (message to the starting session ~18:20):** the 615 includes hold none of the core papers (LLaDA R0205, MDLM
  R0128, Dream R0350, MMaDA R0246 are in the unscreened seed tranche S1243); options A (seed stratum of 20 from the
  census sample's 167 eligible records, texts in the main checkout research/sources/census-text, update strata
  cut to 20 each; recommended), B (lift the freeze), C (limitation only). Phase-1 batches serve A and C.
  **Extraction:** EA folders exb001, exb002 built (scratchpad/ex-dispatch), not launched: free RAM 3.8-4.3 GB, below
  the 5 GB rule (wait_ram.ps1). exs001/exs002 folders (v1 names) built, never launched. **Next:** launch EA
  sessions (opus, general-purpose, prompt in this session's transcript), validate with ex_validate_batch, model and
  isolation checks; rewrite 02-method (stale: describes the 10-15 state); PRISMA checklist in the supplement.
  **Update ~20:45 IST:** 02-method rewritten (current state), 10-limitations selection/screening paragraphs, 05 RQ1
  from all 615, supplement S1 (PRISMA checklist + every logged search), evening page research/EVENING-2026-10-20-paper1.md
  (P1-P3; sheets R0308 and D0039) sent to the user. EA sessions exb001 (a567490c8d2e8349e) and exb002 (ab487ab07c8bb436c)
  running since ~19:50; folders exb003, exb004 built. After each: `python -I analysis/extraction/d0052/postbatch.py <batch>`.
  NOTE: python heredocs in this Bash tool collapse double backslashes; write scripts with LaTeX to files first.
  **Update ~23:30 IST:** user answered P4 a (D0053: launch at >= 4.0 GB free RAM, max 2) and P1 A (D0054: seed
  stratum of 20 from the census eligible records; update strata positions 1-20; total 80; second reader redrawn:
  seed-sample.json). Design now: exb001-exb033 (update phase 1) + exc001-exc011 (seed; folders built with --texts
  research/sources/md/census-text-paged and an --ft provenance string; build more the same way). Queue: alternate
  exc and exb. Filed so far: exb001-exb005 (pass 2 done), exb006-exb007 running. After each session:
  `bash analysis/extraction/d0052/after.sh <batch>`; send returns/<batch>.txt via SendMessage to the agent once;
  then `after.sh <batch> 2`. Records still rejected after the return stay usable with their status (sensitivity
  without them in the synthesis). Analysis: `python -I analysis/extraction/d0052/rq_analysis.py`.
- **HANDOFF 26 (2026-10-20 ~17:10 IST; newest; session 92c0b6b9): SCREENING FROZEN PER D0051.** The human author
  (chat ~15:45 IST, relayed by session 9d5203d7, row D0051) stopped all further screening and downloads; a fresh session
  writes the manuscript next. **Final screened set:** T1 882 decided (608 include, 274 exclude; 3 B-unavailable with the
  human author: M13184, M15873, M17195), unchanged. **R797 (frozen at r797b001-r797b037):** 285 read by A and B; 284
  decided, include 7, exclude 277 (X0 78, X1 69, X2 116, X3 5, X4 2, X8 7), 15 ruled by C (c-r797-01..05), none awaiting
  C; R0308 B-unavailable -> human author (r797-pending-B.jsonl; B fell back to claude-opus-5 after a safety stop in 2 of 2
  sessions, r797b036 and r797b069 alone; A: exclude X2 pipeline; no third session because of the freeze). A-B agreement
  (n = 284, before adjudication): pass/exclude raw 0.961, kappa 0.602 [0.362, 0.793], AC1 0.957 (few passes, so kappa is
  low against high raw agreement). **Identified but not screened (D0051):** R797 remainder 430 (216 retrieved, 123
  e-gateway, 89 open-access not retrieved, 2 no identifier; part 3 plan r797b058-068 and part 4 r797b069 not run); S1243
  1,242 (0 screened; download stopped at 276 of 1,219 PDFs, last R0375 16:57:16, resumable but not to be resumed);
  free-source rescue positives 348 (131 dual-TA screened, 42 pass, none at full text; 217 without abstract held; D0044
  abstract lookup not run). D0043 public versions, D0045 routes, D0047 paper versions (tool tools/find_paper_versions.py
  written, not run): not run. Files: analysis/screening/ft-r797/r797-summary-all.json, r797-decisions-all.jsonl,
  analysis/screening/agreement-ft-r797.json (new script analysis/screening/agreement_ft_tranche.py: skips superseded rows,
  superseded C rulings, B-unavailable records, DISCARDED files), analysis/prisma/prisma-flow.{json,md} (new sections
  full_text_R797 and not_screened_D0051; open notes updated). Fixes this session: ft_title_check reads verified notes for
  no-route-row flags; cqueue skips superseded rows. r797b036 B (first run) discarded for model fallback; its first "filed"
  commit 545c38d is not used. Weekly usage ~26 percent at 16:20. Nothing running.
- **HANDOFF 25 (2026-10-20 ~15:00 IST; newest; execution session d7bb06 stopped at ~78 percent context to hand
  off; HANDOFF 22-24 describe the setup and tools).** **R797 (D0035):** batches r797b001-r797b034 filed (270
  records screened by A and B; every isolation and model check passed; bio batches had no B fallback; quote returns
  all accepted). Includes so far (A=B or C): M00589, M02061 (C), R1391, R0908, R1396, R0542. C groups c-r797-01..03
  filed (Fable, all checks pass). **Queued for C (not run):** M08792, M15920 (b032), M07991 (b033): run
  `FT_TRANCHE=r797 python -I tools/ft-session/cqueue.py <worktree> <S> 4 04 1 34`, ft_dispatch --role C --batch
  c-r797-04 --rows <S>/c-rows-4.jsonl, Fable prompt as in this session (agent-map), `tr.sh r797 cpost c-r797-04 <id>`.
  **Next batches:** r797b035-r797b057 (part 2 plan; b035, b036, b039, b042, b049, b054, b057 are bio batches of 3;
  build with `bash tools/ft-session/tr.sh r797 build r797bNNN`; the new session must edit S and P in
  tools/ft-session/tr.sh and trqret.sh to its own scratchpad and subagent dir, rebuild folders (old ones live in
  this session's scratchpad), and use the same screener prompts (agent-map history / this session's transcript).
  Pipelining: A of batch k with B of batch k+1; at most 2 agents; launch only at >= 5 GB free RAM (other sessions
  hold RAM near 4-6 GB; wait_ram.ps1); quote returns one at a time via SendMessage to the screener's agent id, then
  `trqret.sh`. **Downloads:** OpenReview fetch at 57/58 (scratchpad r797-fetch2.log); then pdf_to_text,
  ft_title_check (verify flags; held texts in analysis/screening/ft-r797/held-texts.jsonl), plan part 3
  (`FT_DISPATCH_ROOT=<S> python -I tools/ft_plan_tranche.py r797 3 58 20261029`; it re-plans M19102 from
  rescreen.jsonl and drops its superseded r797b020 rows when summaries are built). R797 summary/agreement script
  not yet written (model on tools/ft-session/refresh_t1.py + analysis/screening/agreement_ft_t1.py; must skip
  superseded-rows.jsonl). Then S1243 downloads (fetch_fulltext.py --routes analysis/screening/ft-routes-seed1243.jsonl
  --types arxiv,acl,oa_url) and its screening; D0043 public versions (tools/fetch_public_versions.py run); D0044
  abstract lookup after the OpenAlex reset (~05:30 IST); D0045 routes for passed-ta-rf.jsonl; D0047 paper versions
  for 20 web-only seed records. Weekly usage 24 percent at 14:40.
- **HANDOFF 24 (2026-10-20 ~14:15 IST; newest; HANDOFF 23 and 22 describe the setup).** User approved all
  recommendations at 12:40 -> **D0044-D0050** (N1 abstract lookup for the 217; N2 downloads for D0036 passes; N3
  D0041 note; N4 paper versions for 20 web-only seed records; N5 validation frame; item 12; Stage A S1-S24).
  **R797:** part 1 (b001-b013) and part 2 b014-b026 filed; b027 B done, **A for r797b027 not yet run** (folder built:
  A-r797b027-072b4342-...; B agent a4a1d40a193a8a0db); then `tr.sh r797 postbatch r797b027 <A> a4a1d40a193a8a0db`.
  Remaining part 2: b028-b057 (plan research/review/fulltext/r797-batches-part2.json). C groups: c-r797-01 (2 incl
  M00589, M02061; 2 excl) and c-r797-02 (5 excl) filed; queued for C: M09970 (b026), M10697 done; next
  `FT_TRANCHE=r797 python -I tools/ft-session/cqueue.py <worktree> <S> 3 03 1 57`. Held texts:
  analysis/screening/ft-r797/held-texts.jsonl (M16194, M16195 unreadable; M18905 wrong file -> e-gateway; M19102
  wrong file, rows superseded, correct HTML text fetched, listed in rescreen.jsonl for the next plan part). Quote
  returns: send one at a time (2-agent limit). OpenReview downloads (58) running in background (r797-fetch2.log,
  ~25/hour); after it: pdf_to_text, ft_title_check, plan part 3 (`ft_plan_tranche.py r797 3 58 20261029`).
  **D0044 abstract lookup:** tools/lookup_abstracts.py ready; OpenAlex 429 until ~05:30 IST: run `python -I
  tools/lookup_abstracts.py run` after that. **Codex** is back (debate 2026-10-20-paper1-novelty, rounds 1-2; Codex
  thread id in its log.jsonl; continue with tools/debate.py). **NotebookLM** not signed in (user step,
  research/SCHEDULE-2026-10-20.md). **RAM:** other sessions keep free RAM near 4-5 GB; launch only at >= 5 GB
  (wait_ram.ps1). Weekly usage 21 percent at 13:50. Context of session d7bb06 ~67 percent.
- **HANDOFF 23 (2026-10-20 ~09:10 IST; PAUSE at the user's request: laptop offline from 09:30 for a presentation;
  resume when the user says "continue"; HANDOFF 22 below still describes the setup).** **R797 full text:** batches
  r797b001-r797b009 screened by A and B (all isolation and model checks pass, incl. bio batches b007/b008: no B
  fallback); filed b001-b009 (82 records; b001 B and b009 A each had one quote returned once and accepted). C queue so far:
  M03713 (b001), M00589 (b002), M03752 (b005), M02061 (b007 adjudicate); C not yet run: build with
  `FT_TRANCHE=r797 python -I tools/ft-session/cqueue.py <worktree> <scratchpad>/ft-dispatch 1 01 1 9`, then
  ft_dispatch --role C --batch c-r797-01 --rows <scratchpad>/ft-dispatch/c-rows-1.jsonl, Fable, prompt as c-t1-19
  (agent-map history), then `tr.sh r797 cpost c-r797-01 <agent>`. Remaining part-1 batches: r797b010-r797b013 (built
  folders: none; build with tr.sh). **Downloads:** stopped cleanly at 09:05 for the pause: 510 of the 519 non-OpenReview routes logged (ok 434,
  not_pdf 43, error 33); the 58 OpenReview routes not started. Resume by rerunning both (resumable):
  `python -I tools/fetch_fulltext.py --routes analysis/screening/r797-oa-routes.jsonl --types arxiv,acl,oa_url` and
  `python tools/fetch_openreview.py --routes analysis/screening/r797-oa-routes.jsonl`. Then `python tools/pdf_to_text.py`,
  `python -I tools/ft_title_check.py` (4 new unverified flags to read: M15725, M16194, M16195, M18905; add notes to
  title-check-verified.json), then `FT_DISPATCH_ROOT=<scratchpad>/ft-dispatch python -I tools/ft_plan_tranche.py r797
  2 14 20261028`. The 76 OA failures (error/not_pdf) go to a retry (tools/fetch_oa_retry.py style) or the user's
  checklist. After R797 downloads: S1243 downloads (fetch_fulltext.py --routes analysis/screening/ft-routes-seed1243.jsonl
  --types arxiv,acl,oa_url), then D0043 (python tools/fetch_public_versions.py run). Evening page items N1-N6 + 12
  wait for the user.
- **HANDOFF 22 (2026-10-20 ~09:30 IST; newest; execution session d7bb06 = 741900f8, scratchpad .../741900f8-51c9-4f19-8878-9556d9ef107b/scratchpad).**
  **Gate T1 re-audit 2: PASS WITH CORRECTIONS** ("T1 screened so far (interim)", 882 decided; fixes 23/24 done in
  e7645bb; finding 25 = D0041 note row for the human author, EVENING N3). **D0036:** 131 rescue positives with an
  abstract dual-screened (research/review/screening/v2/dual-rescue-free/, tools/ta_dispatch.py, all isolation/model
  pass): kappa 0.792, 42 pass to full text (downloads need the user's yes, N2); 217 without abstract held
  (pending-no-abstract-rf.jsonl; N1). **D0035 (R797):** frame r797-tranche-ids.txt (715) and validation sample drawn
  BEFORE any download (human-validation-r797, 108; sheet built); 577 OA downloads running in background
  (fetch_fulltext.py on analysis/screening/r797-oa-routes.jsonl, then fetch_openreview.py; log in scratchpad
  r797-fetch.log; resumable: rerun the same two commands); e-gateway checklist-r797 (118). Harness tranche-aware:
  FT_TRANCHE env in ft_postbatch/ft_cpost/cqueue; tools/ft_plan_tranche.py (bio batches of 3); tools/ft-session/tr.sh
  (build/postbatch/cpost). Plan part 1 = r797b001-013 (102 records). r797b001 A/B dispatched. Next: convert new PDFs
  (python tools/pdf_to_text.py; python -I tools/ft_title_check.py), plan part 2, continue batches, C via cqueue
  (FT_TRANCHE=r797). **D0037 (S1243):** routes ft-routes-seed1243.jsonl (arxiv 1,214; R0484 duplicate of M17010; 20
  web-only, N4), frame s1243-tranche-ids.txt (1,242), sample 187 + sheet; downloads after R797's finish. **D0042:**
  OQ5-04 workbook built (research/review/extraction/human-check-oq5-04.xlsx); Stage A also needs plan v0.5 s14 A2-A4,
  A10 rows (N6, list to compile). **D0043:** tools/fetch_public_versions.py ready (287), run after R797 downloads.
  Item 12 drafted (ITEM12-RECOMMENDATIONS). Note: 0cbc855 (title resolution rerun) was committed onto this branch at
  08:14 by the starting session.
- **HANDOFF 21 (2026-10-20 ~08:10 IST; newest).** The human author approved every recommendation on
  research/EVENING-2026-10-20.md -> **D0035-D0043** (797 re-check tranche with OA downloads; 348 rescue positives to dual
  TA; 1,243 seed passes as a full-text tranche with OA downloads; P1 deviation; P2 rule; P3 note; B-unavailable records
  to the human author (M13184, M15873, M17195 now, any later ones too); extraction scope = light fields + QA on all,
  contrast data on stratified sample + multimodal option (d); public versions of anonymous texts, OA). Item 12 (tool
  rules G1, E1, derived fields): orchestrator drafts recommendations for the user. **Execution handed to a fresh
  session** (see its brief in the session list). User tasks this evening: P4 3-paper sheet; OQ4-04 borderline check;
  58 e-gateway PDFs; validation-sample sheets for each new tranche (before seeing any row of that tranche).
- **HANDOFF 20 (2026-10-20 ~07:50 IST; newest; HANDOFF 18 (T1) and 19 (instrument) stand).** **Stage A extraction
  tools built and tested, nothing drawn or extracted:** tools/ex_validate.py (table-aware validator), tools/ex_validate_batch.py
  (batch driver, pass tags, dispatch checks), tools/ex_dispatch.py (isolated E1/E2/EC folders), analysis/extraction/agreement.py
  1.0.x (stage-a/gate modes, MJ1 sign coverage, shared sign rules), analysis/extraction/draw_pilot.py (refuses a draw without a
  decision row), draft lookups v1, we-expected.jsonl (275 units); tests: `python -E -P -m pytest tests/extraction
  tests/test_ex_validate.py -q -p no:cacheprovider` 173/173 (do not run tests/exp001 and tests/exp003 in one process: 2
  pre-existing clash failures). Logs: analysis/extraction/stageA-*.txt, ex_validate-test-log.txt. Open tool questions for
  the human author: G1 (value-level failures reject the cell?), E1 coverage rule, derived-field filling; draw_pilot cannot
  draw a re-gate G-mm list (C1 has only 53 records). **Waiting on the user:** research/EVENING-2026-10-20.md items 1-11
  (+ 12 tool questions). Then: Stage A draw (needs the decision rows), T1 re-audit 2, 797 tranche downloads if yes.
  Weekly usage ~13 percent at 07:50.
- **HANDOFF 19 (2026-10-20 ~06:40 IST; newest; HANDOFF 18 stands for T1).** **Extraction instrument:** five
  architect/red-team rounds (research/review/extraction/*-v0.1..v0.5, audits 2026-10-20-redteam-extraction-v0.1..v0.5,
  scripts in analysis/extraction/ with logs). v0.5 red-team: 0 critical, 3 major (MJ1 final-sign pipeline undefined and
  unmeasured; MJ2 rule-selection approximation biased; MJ3 ceiling penalty), 5 minor; **Stage A (development, 12
  records) GO** once the human author's rows are entered (scope, multimodal option, rules: OPEN-QUESTIONS-v0.5.md;
  research/EVENING-2026-10-20.md items 9-11), the T1 gate passes, and the tools are built (ex_dispatch, ex_validate,
  draw_pilot, agreement.py with MJ1 sign-coverage counts, lookups, fixtures, we-expected.jsonl); **Stage B (gate) NO-GO**
  until MJ1-MJ3. Next: build Stage A tools (no draws), then a quality-engineer review; title resolution resumable after
  the OpenAlex daily reset (173 lookups incomplete).
- **HANDOFF 18 (2026-10-20 ~02:00 IST; newest; supersedes HANDOFF 17's numbers).** **T1 screened so far
  (INTERIM: T1 not closed until items 16a/16b and rows P1-P4 are decided): 885 records read; 882 decided, include
  608, exclude 274; 3 awaiting a second screener** (M13184, M15873, M17195: Opus B hits a safety-classifier stop on
  these biology papers and the harness falls back to claude-opus-5 in 3 of 3 sessions; t1-pending-B.jsonl). C ruled
  116. A/B agreement n = 882: pass/exclude kappa 0.894 [0.859, 0.927]. **K = 4** (unchanged) -> 797 re-check tranche
  (route table built, needs the user's yes for downloads). **Gate T1:** audit FAIL (finding 1: t1b081 B fallback
  model) -> fixed (B split rerun; C c-t1-19; superseded C rulings; tools/ft_model_check.py in postbatch/cpost);
  re-audit 1: finding 1 closed, minor 15-19 fixed; still FAIL only on items for the human author (findings 2, 4, 5,
  6, 14 -> research/review/audits/2026-10-20-gate-T1-response.md rows P1-P4). **Extraction:** form v0.1 drafted,
  red-teamed (3 critical); v0.2 revision running (scope per user decision 2026-10-16: stratified sample + all
  multimodal). Next: red-team v0.2; evening user list.
- **HANDOFF 17 (2026-10-20 ~01:00 IST; newest; overnight run while the user sleeps; HANDOFF 16 superseded
  for status).** **T1 part 19 COMPLETE** (t1b077-t1b093, 170 records; every batch isolation pass; every
  unaccepted quote returned once and accepted; C groups c-t1-15..18, all isolation pass). **T1 total: 885
  records, include 608, exclude 277, C ruled 116** (t1-summary-all.json, t1-decisions-all.jsonl via
  tools/ft-session/refresh_t1.py). A/B agreement over 885 before adjudication: pass/exclude kappa 0.895
  [0.860, 0.927] (agreement-ft-t1.json). **Re-check K = 4** (M03416 C, M10984 A=B, R0963 A=B, R1202 C;
  analysis/screening/ta_recheck_k.py -> ta-recheck-k.json; 18 sampled ids not yet retrieved): criteria v1.6
  s5.2 -> all 797 frame candidates go to full text (downloads need the user's yes). PRISMA counts refreshed
  (analysis/prisma/prisma_flow.py now accepts ft-routes-extra ids). Gate-auditor audit of T1 running ->
  research/review/audits/2026-10-20-gate-T1-fulltext.md. Session 9d5203d7 agent transcripts since 19 Oct
  22:44 are in the **fcff62** projects dir (next.sh P). Paper 5 session (local_6a268604) stopped its compute
  for good; light work only. **Next:** act on the audit; extraction pilot (protocol s5-s6) once the form is
  checked; 797-candidate tranche after the user's yes; items 16a/16b decisions.
- **HANDOFF 16 (2026-10-18 ~13:00 IST; HANDOFF 15 still applies except the status).** Stopped
  new agent work at **97 percent weekly** (user limit; resets Mon 19 Oct ~22:30 IST). Session 9d5203d7
  (entered this worktree via EnterWorktree; its transcripts are under the 334706 projects dir
  .../9d5203d7-a6be-4a10-8e9d-83c85c9e81ca/subagents; dispatch root is its scratchpad
  C:/Users/Shlok/AppData/Local/Temp/claude/C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-resume-dlm-discovery-exp-003-fcff62/9d5203d7-a6be-4a10-8e9d-83c85c9e81ca/scratchpad/ft-dispatch,
  which holds the t1b083-t1b093 .ids copies). **Filed: t1b077-t1b082** (60 records; all isolation pass;
  6 quotes returned once, all accepted on re-check; agreement 9, 10, 10, 10, 8, 9 of 10). **C queue part 8**
  (analysis/screening/ft-t1/c-queue-8.jsonl, 8 records): **c-t1-15 done** (M03416 include; M07919, R0927,
  M13335 exclude; isolation pass, quotes ok; c-run-log.jsonl). **c-t1-16 NOT run** (R1202, U03826, U04280,
  U06471; folder C-c-t1-16-caffdc0e-... built in the scratchpad above, unused: launch it as is, Fable,
  prompt as for c-t1-15 in tools/ft-session/agent-map.txt history). t1-decisions-all.jsonl /
  t1-summary-all.json NOT refreshed (needs c-t1-16; script ready: tools/ft-session/refresh_t1.py, logic of
  3f113e6 plus a part-19 label). Harness: ft_postbatch.py has --root-A (tested identical on t1b076);
  next.sh S/P point to session 9d5203d7 (a new session must set its own and rebuild folders; t1b083 not
  built). Two agents stopped at 04:30 on a session-replacement message (later withdrawn) are logged failed.
  Queue builder for C (adds quote_after_return ids): tools/ft-session/cqueue.py. **Next after the reset:**
  c-t1-16, t1b083-t1b093 (B then A, 2 agents, >= 5 GB RAM; Paper 5's launcher holds RAM near 3-5 GB),
  C on their queue, refresh summaries. User: e-gateway checklist built
  (research/review/fulltext/egateway-manual-checklist.xlsx, tools/egateway_sheet.py), USER-ACTIONS item 21.
- **HANDOFF 15 (2026-10-17 night, planned shutdown).** RESUME POINT for T1 part 19
  (research/review/fulltext/t1-batches-part19.json, t1b077-t1b093, 170 records; plan by the
  post-screening session, 824ab95; re-check/C8/unrouted records mixed in UNFLAGGED - keep them unflagged
  to A, B and C). Last fully filed batch: **t1b076**. **t1b077: A done and filed** (FA-t1b077.jsonl, 10
  rows, isolation pass, quotes all accepted; A said U03826 adjudicate on D1); **B to rerun** (logged failed,
  planned shutdown; build a fresh B folder: python -I tools/ft_dispatch.py --role B --batch t1b077 --ids
  tools/ft-session/t1b077.ids --root <new scratchpad>/ft-dispatch). Postbatch for t1b077 needs both
  transcripts in ONE dir: copy A's transcript
  C:/Users/Shlok/.claude/projects/C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-resume-dlm-discovery-exp-003-334706/c850154c-9b85-49b2-9b76-d75be8648cf9/subagents/agent-a283ac2b42c5f27c5.jsonl
  into the new session's subagents dir, and copy A's folder
  .../c850154c-9b85-49b2-9b76-d75be8648cf9/scratchpad/ft-dispatch/A-t1b077-9c28a9b4-6ce5-45b1-b42b-1f9c51632e4f
  into the new dispatch root (or pass the old root as S). t1b078 folders were built in the old scratchpad
  (unused): rebuild in the new one. Remaining: t1b078-t1b093 (16 batches), then C (route F, Fable) on
  every disagreement/adjudicate/failed-quote row in t1b077-t1b093, then refresh
  t1-decisions-all.jsonl / t1-summary-all.json (script as in 3f113e6) and a HANDOFF line so the
  orchestrator can compute K from the 100 sample ids. Procedure: tools/ft-session/next.sh (EDIT S and P
  at its top to the new session's scratchpad and subagents dir), qret.sh for quote returns, ft_cpost.py
  for C sessions, wait_ram.ps1 <GB> <min>. Screener prompts: file tools only (Read/Grep/Glob/Write/Edit),
  first a Glob of the folder, copy paths from it, no Bash/PowerShell. **Limits (user):** at most 2 agents
  at once; launch only with >= 5 GB free RAM; stop new agent work at 97 percent weekly usage (was 91
  percent at 19:00 IST 17 Oct); no GPU; no browser. Do not start a batch that cannot finish before 97
  percent.
- **HANDOFF 14 (2026-10-17 ~19:00 IST; newest; HANDOFF 13 still applies except the status).** User: yes to the
  21 OpenReview PDFs and the 119 e-gateway records; human validation not done by record, user states the sample is
  correct -> **D0034** (deviation: A-B agreement only; user may now see T1 rows); continue to 97 percent weekly.
  Done: `tools/fetch_openreview.py --routes` (21/21); `tools/egateway_import.py` (plan / import / remaining;
  Chrome saves one tar per page, built in the page, because Chrome blocks a second automatic download):
  IEEE 61/61 (in-page fetch of /stampPDF/getPDF.jsp, ~20 s per PDF in a background window); Springer stopped
  (chapters not subscribed; journal PDFs HTML/503 after a 22-request burst and the VIT access line vanished:
  user asked to check); ScienceDirect Cloudflare check (not answered); ACM downloads not saved by Chrome. 82 new
  PDFs converted, all ok; title check over 885 texts: no new flags. Manual list for the user:
  `research/review/fulltext/egateway-manual.csv` (58). **Next:** after 05:30 IST rerun `tools/fetch_oa_retry.py`;
  import any PDFs the user saves; cut M17477's abstract; then full-text screening of the newly retrieved T1
  records (re-check/C8 + passes) as T1 batches (agents: needs >= 8 GB free RAM, 2 at most), K test.
- **HANDOFF 13 (2026-10-17 ~16:30 IST; HANDOFF 12 still applies except the status).** User:
  will fill the T1 validation sheet later (not done: sheet unchanged); approved open-access downloads for
  the extra records and a retry of failed OA links, **no OpenReview, no e-gateway**. Done: `tools/fetch_fulltext.py`
  gained `--routes/--types`; 81 of 100 extra OA records fetched (arXiv 70, OA 28, ACL 2 attempted); new
  `tools/fetch_oa_retry.py` (OpenAlex other OA locations + landing-page citation_pdf_url; bot walls and
  bot-check pages are not answered) recovered 7 of 74 failures; 88 PDFs converted (`python -P -E
  tools/pdf_to_text.py`, all ok, max glued 0.0034); sha256 of each text's PDF = fetch-log sha256; new
  `tools/ft_title_check.py` over all 803 texts: 5 flags, all read and recorded in
  `research/review/fulltext/title-check-verified.json` (4 renamed titles, correct papers; **M17477 is a
  6.3-million-character congress supplement: cut its abstract (journal p. 400) before dispatch**). PRISMA
  script now reads retrieval status: extra records 84 retrieved, 16 OA pending, 21 OpenReview, 17 e-gateway; 67 OA
  without a PDF in all. **Open:** OpenAlex free daily budget used up (HTTP 429, resets 05:30 IST); the
  retry tool now caches OpenAlex answers and stops cleanly; rerun `python tools/fetch_oa_retry.py` after the
  reset to regenerate `oa-retry-unresolved.csv` and `oa-retry-summary.json` with the final labels (both left
  uncommitted until then; the run-2 version labels Elsevier linkinghub script pages as bot checks). RAM was ~1 GB
  free during this work: no agents.
- **HANDOFF 12 (2026-10-17 ~15:00 IST; HANDOFF 11 still applies except the status).** Low-token
  session (weekly 90 percent; reset Mon 19 Oct ~22:30 IST; no agents: free RAM 4.5 GB < 8 GB rule).
  **Done, committed:** (1) `analysis/screening/agreement_ft_t1.py` -> `agreement-ft-t1.json` (A vs B, 715,
  before adjudication): pass/exclude kappa 0.853 [0.799, 0.903], AC1 0.947, p_pos 0.977, p_neg 0.876;
  three-way kappa 0.812 [0.764, 0.856]; adjudicate rate A 0.101, B 0.056; 83 records sent by
  disagreement/adjudicate (C ruled 99; the other 16 presumably quote returns, not checked); joint exclusions 98/99 same code; per-rule
  citation agreement in the JSON. Not yet audited by statistician/gate-auditor. (2) Human validation sample
  T1: `analysis/screening/human_validation_t1.py`, 108 of 715 (seed 20261016, max(100, ceil 15%)), blind sheet +
  INSTRUCTIONS + manifest (sample sha256) in `research/review/screening/human-validation-t1/`. Frame = 715
  screened records; T1 records screened later get their own 15 percent draw (same seed) -> **log as a
  decision (deviation from one draw over the fixed T1 set)**. (3) Routes (metadata only, one OpenAlex
  call): `analysis/screening/ft_routes_extra.py` -> `ft-routes-extra.jsonl` for the re-check sample + C8
  (**132**, not 130: no overlap between the 100 and the 32) and **6** unrouted subscription TA passes (U04633,
  U04643, U04645, U06471 from sub-02 as well as U06894, U07166): arXiv 70, OA 28, OpenReview 21, ACL 2,
  e-gateway 17; unflagged user list `research/review/fulltext/egateway-list.csv` (119). (4)
  `analysis/prisma/prisma_flow.py` -> `prisma-flow.md/json`. **Gaps it found (USER-ACTIONS item 16):** 348
  free-source rescue positives never dual-screened nor routed (D0029 vs D0030 wording); 1,243 seed-corpus TA
  passes in no full-text tranche; 55 OA fetch failures; the 7 title-resolved queue records not dual-screened.
  **Quality pass (user via orchestrator: quality over budget):** the 16 C records without an A/B
  disagreement are quote-check cases (13 return not possible, 2 not accepted after return, 1 truncated;
  now computed in agreement-ft-t1.json C_queue); `check_agreement_ft_t1.py` recomputes the kappas with
  scikit-learn and AC1/p_pos/p_neg from cell formulas: 9/9 match. Subscription counts reconcile exactly:
  4,201 failures = 2,788 rescue-screened + 1,413 SpringerLink without abstract (pending-no-abstract.txt is
  stale by 8); dual 260 = queue 179 + 81 rescue positives. Still to do: statistician/gate-auditor audit
  of the agreement and PRISMA files (needs an agent: wait for >= 8 GB free RAM or after the reset). **NEXT (after the reset, with the
  user's yes):** user screens the validation sheet first; decisions on item 16; downloads of the 138 extra
  records (121 OA + 17 e-gateway) and the 102 e-gateway; screen them as T1 batches; K test; Springer abstracts;
  RQ extraction; section 05.
- **HANDOFF 11 (2026-10-17 ~12:40 IST).** **T1 full-text model screening COMPLETE:** batches
  t1b001-t1b076, 715 records (332 open-access/remap + 383 OpenReview), every A/B disagreement, adjudicate
  row and unreturnable/failed quote ruled by C (99 records, groups c-t1-01..14, all isolation pass, all
  logged in analysis/screening/c-run-log.jsonl). Model result: **include 564, exclude 151** (X1 57, X0 49,
  X2 38, X3 3, X4 3, X7 1); I1(a) 513, I1(b) 36, both 15; nonlang_only 10
  (analysis/screening/ft-t1/t1-summary-all.json, t1-decisions-all.jsonl). Before the human validation
  sample and author review (protocol s4): NOT final. OpenReview download complete (383 of 387); 4 notes
  not found on the API (M13187, M15046, M15574, M18918) recorded as X6 reports not retrieved
  (t1-not-retrieved.jsonl). **NEXT:** A/B agreement statistics before reconciliation (criteria-v1.6
  s5.3: kappa with bootstrap CI, p_pos/p_neg, prevalence/bias, adjudicate rate per screener, code
  agreement on joint exclusions); human validation sample of T1 (user, blind); routes for U06894 and
  U07166 (SD TA passes); re-check sample / C8 records; e-gateway papers (102).
- **HANDOFF 10 (2026-10-17 ~09:40 IST; newest; HANDOFF 9 still applies except the status).** User:
  continue to completion (weekly limit resets Mon 19 Oct ~22:30 IST). Laptop crashed twice on 17 Oct
  (04:10, 08:46; bugcheck 0x7E): now at most 2 agents at once, launch only with >= 8 GB free RAM
  (tools/ft-session/wait_ram.ps1), no GPU, no Chrome. T1 OpenReview batches t1b035-t1b068 screened and
  filed (part3-part11 plans; t1b061 = 3 records); adjudicator groups c-t1-09..12 done (c-t1-12 failed in
  the crash, rerun). Still to adjudicate: M18010, M18037 (t1b068) -> with the last OpenReview group.
  Screeners now use only Read/Grep/Glob/Write/Edit and copy paths from a first Glob (Bash /dev/null and
  mistyped paths caused 5 discards). OpenReview download (orchestrator): ~333 of 387 logged; next batch
  t1b069 when 10 PDFs wait (tools/ft-session/wait_pdfs.py 10 387 120; convert with
  python -P -E tools/pdf_to_text.py; tools/ft-session/orbatch.py <repo> <root> <n0> 69 12 202610172).
- **HANDOFF 9 (2026-10-16 ~17:00 IST; newest; HANDOFF 8/7 still apply except the status).** Screening
  session c850154c (this worktree) drives T1; the orchestrator (crash-a57ec7) runs the OpenReview download.
  **Done:** T1 t1b025-t1b034 screened and filed (all isolation checks pass after one discard: t1b026 A read
  a mistyped outside path -> discarded, rerun; t1b031 B stopped at launch, over the 3-agent limit). A
  duplicate driver (session 9c1bcaee, worktree paper-1-3ff9e1) briefly logged false 'failed' rows and
  reran t1b025/026; its 3 screeners were killed before rows; correction + 'discarded' rows in batch-log.
  Quote returns: t1b025-034 returned once to their screeners (all accepted except M09594 -> C);
  t1b001-024 not returnable (screeners belong to the orchestrator; it judged resuming too costly) ->
  logged quote_return_not_possible, 13 quote-only records to C. Adjudicator C (Fable, route F) on all 66
  queued records (c-queue-1/2.jsonl; groups c-t1-01..08, every session logged in c-run-log.jsonl, all
  isolation pass, C quotes returned once and accepted). **T1 b001-b034 model result: 332 records,
  include 228, exclude 104** (analysis/screening/ft-t1/t1-summary-b001-b034.json; before human
  validation and author review). ScienceDirect: rescue-sub-04 (293; 2 unclear) + dual TA batch-sub-03
  (4/4 agree; 2 pass: U06894, U07166) -> TA passes 1,006; those 2 need full-text routes.
  OpenReview: 26 PDFs so far (orchestrator download at ~25/hour), converted; batches t1b035-t1b037
  (t1-batches-part3.json) in progress. Tools: tools/ft_cpost.py (C session post-check and log);
  next.sh paths now point at session c850154c. **NEXT:** finish t1b035-037; screen later OpenReview
  arrivals as t1b038+ (convert only ids with fetch-log status ok); agreement statistics (criteria-v1.6
  s5.3) over A/B before reconciliation; human validation sample before the author sees any row; routes
  for U06894/U07166; re-check sample / C8 records; e-gateway papers.
  **Update ~17:45 IST, PAUSED at 55 percent weekly (user's pause rule).** OpenReview batches t1b035-t1b038
  (36 PDFs; part3/part4 plans) screened and filed, isolation pass (t1b036 B discarded once for a Bash
  redirect to /dev/null, rerun; t1b038 A stopped at launch, prompt pointed at the parent dir, rerun).
  Not yet adjudicated: M12594 (t1b035), M12741 (t1b036), M12775 + M12776 (t1b038) -> next C group
  c-t1-09; no quote returns pending for t1b035-038. Prompt lesson: name the exact folder path and say
  "no /dev/null"; never let a screener search the dispatch root.
  **Update ~18:00 IST (user: continue to 65 percent).** C group c-t1-09 done (M12594 include; M12741,
  M12775, M12776 X0). t1b039 (6 OpenReview PDFs, part5) screened: 6/6 agree, M12894 adjudicate -> next C
  group. Quote returns for t1b035 (M12752) and t1b039 (M12873) accepted. OpenReview download is
  rate-limited (~25/hour; 42 converted + 2 waiting); next batch t1b040 when about 10 are waiting
  (convert, then tools/ft-session/orbatch.py <repo> <root> <n0> 40 6 202610166, next.sh build). Weekly 55
  percent at 18:00; user's pause point now 65 percent.
- **HANDOFF 8 (2026-10-16 ~15:45 IST; newest; HANDOFF 7 below still applies except the status).**
  Full-text T1: t1b001-t1b024 COMPLETE (agreement 220/240; 39 ids to adjudication; all counted sessions
  isolated; one discarded for mkdir /tmp, one rerun after a network drop). NEXT: t1b025-t1b031 (part 1) and
  t1b032-t1b034 (part 2), ids in tools/ft-session/t1b0NN.ids. tools/ft-session/next.sh (build/postbatch) and
  agent-map.txt are copies from the old session: EDIT the two paths at its top (S = your dispatch root in your
  scratchpad, P = your session's subagents transcript dir ~/.claude/projects/<project>/<session>/subagents).
  ScienceDirect ingested (12 files kept after the user's cleanup; 7,170 unique, 179 queued): rescue pass on
  the new SD string failures with abstracts, then dual TA of the 2 new queued + rescued, still TO DO.
  OpenReview: .env template created at the repo root (user fills it; never open it); user is testing
  python tools/fetch_openreview.py --limit 3. IEEE I3-I5 blocked by IEEE's account outage.
- **HANDOFF 7 (2026-10-16 ~13:45 IST; newest, overrides older blocks).** Work happens in THIS worktree
  (exp-003-334706); the driving session runs in worktree crash-a57ec7, whose Edit/Write tools are blocked
  here by a hook, so files here are written by Bash/python (user approved).
  **User to-do:** `research/USER-ACTIONS-2026-10-16.md` (IEEE I3-I5; ScienceDirect 23 runs on
  `search-raw/sciencedirect/sd-download-links.html`; OpenReview 387 papers via `tools/fetch_openreview.py`
  with the user's own credentials in env vars - first test failed 'Invalid username or password', user is
  re-setting them in single quotes; 1,421 Springer records without abstracts (Springer Meta API key
  suggested); 9 near-miss arXiv matches; 102 e-gateway papers; routes+download of the 130 re-check/C8
  records; 15 percent human validation sample of T1 before seeing any screener row; HANDOFF 4 items).
  **Done today (after HANDOFF 6):** SpringerLink exported (5 CSVs, user downloads) and ingested (6,854 unique,
  177 queued); ScienceDirect: 8-connector limit, no wildcards, automatic plurals verified, 23 re-packed runs,
  automation blocked by bot protection (stopped); rescue pass 3 (687; 7 unclear) and dual TA batch-sub-02
  (4 pass) -> 1,004 TA passes. Adjudication route F (claude-fable-5-1) written as line 1 of
  analysis/screening/c-run-log.jsonl. Open-access full texts: 328 PDFs (fetch-log.jsonl); text via PyMuPDF
  (markitdown glued words; `tools/pdf_to_text.py`); OpenReview needs login (387 unmapped).
  **Full-text screening T1 (criteria v1.6, D0032), in progress:** harness `tools/ft_dispatch.py`
  (isolated folders), `tools/ft_isolation_check.py` (14 tests), `tools/ft_postbatch.py`; batches of 10 in
  `research/review/fulltext/t1-batches-part1.json` (t1b001-031) and `-part2.json` (t1b032-034); results in
  `analysis/screening/ft-t1/<batch>/` and `batch-log.jsonl`. Pilot: analysis/screening/ft-pilot01.
  Status at handoff: t1b001-t1b016 complete (149/160 agree; 23 ids to adjudication), t1b017 A done / B
  running, t1b018 A running. Per batch: Screener A = sonnet, B = opus, prompt = 'brief is section E of
  criteria-v1.6-screener.md in the dispatch folder; no /tmp; one-line reply'; after both: postbatch;
  a failed isolation check or API failure -> log 'discarded'/'failed' in batch-log and rerun in a fresh
  folder. Helper in the driving session's scratchpad: ft-dispatch/next.sh (build/postbatch) and
  agent-map.txt (batch -> agent ids). Cost about 0.4 percent of the weekly limit per batch (37 percent at
  t1b018); pause at 55 percent. **After all batches:** return non-accepted quotes once to their screener,
  then adjudicator C (Fable) on disagreements + 'adjudicate' rows (log every C session in c-run-log.jsonl),
  then the re-check sample/C8 records and OpenReview/e-gateway papers as further T1 batches, K test
  (criteria-v1.6.md s5), human validation.
- **HANDOFF 6 (2026-10-16 ~08:30 IST; newest, overrides older blocks).** Session resumed after the 04:48
  crash in this worktree (exp-003-334706); HANDOFF 5 was stale (v1.1 audit, criteria v1.2/v1.3, ACM DL,
  IEEE I1-2026 + I2 had all been done before the crash). **User-facing to-do list:
  `research/USER-ACTIONS-2026-10-16.md`** (IEEE I3-I5 'file limit exceeded'; SpringerLink; ScienceDirect;
  adjudicator route F/H; full-text download batches; title resolution API limits; HANDOFF 4 items).
  **Done this session:** D0032 = full-text criteria v1.6 adopted (red-team audits v1.3-v1.6 in
  `review/audits/`; protocol s10 amendment); D0033 = title-resolution design rule (check sample must be
  complete). Ingest now reads ACM in-page JSONL (`tools/ingest_subscription.py`): Scopus + WoS + IEEE
  (I1, I2) + ACM -> 4,606 unique, 174 queued, 1,808 string failures. Rescue pass (Haiku, D0029 design,
  `screening/v2/rescue-subscription/`): 10 include + 62 unclear. Dual screening (A Sonnet, B Opus) of 246
  (`screening/v2/dual-subscription/`): kappa 0.930 [0.861, 0.985]; D0030 -> 46 pass. Total title/abstract
  passes 1,000. Full-text access routes (`review/fulltext/ft-routes.jsonl`): 774 open access, 102
  e-gateway, 27 duplicates, 97 no full text (32 near-miss candidates for a human check).
  **Blocked:** title-resolution rerun stalled at 100/393 slow lookups (API limits), stopped; rerun
  `python tools/resolve_title_only.py run --s2-patient=90` after 05:30 IST or with an S2 key.
  **Next:** with the user: IEEE I3-I5, SpringerLink, ScienceDirect (then rerun ingest, rescue, dual screen
  the delta); adjudicator route; download batch 1 (open access) then batch 2 (e-gateway); then full-text
  screening per criteria v1.6 (dispatch rules in criteria-v1.6-screener.md: isolated folders, session
  rules, c-run-log.jsonl first line = route). Writes into this worktree from the crash-a57ec7 session are
  blocked for Edit/Write tools by a worktree hook; the user approved writing here (done via Bash).
- **HANDOFF 5 (2026-10-16 ~00:15 IST; newest, overrides older blocks; session in progress).**
  Date correction: Scopus ran 2026-10-15 ~22:20 IST (file times), not 10-16; the `-20261016` file names
  stay (hashed). Search date for all subscription databases = 2026-10-15.
  **Web of Science DONE:** Q1 599, Q2 376, Q3 105, Q4 1,012, Q5 543, union #6 2,267 exported (3 RIS,
  Full Record, user approved); `search-raw/web-of-science/wos-queries-20261015.md` (strings, hashes).
  **IEEE Xplore:** the sheet's 6-term limit was wrong (78 and 93 field terms accepted); 5 merged
  queries I1 1,203 / I2 101 / I3 245 / I4 41 / I5 12 (`search-raw/ieee-xplore/ieee-queries-20261015.md`,
  generator `ieee_queries_20261015.py`). CSV cap 1,000 -> I1 split by year: 2021-24 (230) and 2025
  (506) on disk; 2026, I2-I5 still to download (user downloads by hand from `ieee-download-links.html`,
  because Chrome stopped saving automated downloads). User approved IEEE downloads.
  **ACM DL:** queries Q1-Q5 built (per-concept Title/Abstract/Keyword groups, `search-raw/acm-dl/
  acm_queries_20261015.py`, hashes checked), NOT run: loading the long doSearch URL made the Claude in
  Chrome safety check block every call for ~20 min (fixed by restarting the extension). Retry with the
  advanced-search form or shorter queries. SpringerLink, ScienceDirect: not started.
  **Ingest:** `tools/ingest_subscription.py` (rerun: `python tools/ingest_subscription.py`), report
  `corpus/subscription-ingest-report-2026-10-15.md`: Scopus+WoS+IEEE slice -> 3,895 unique, 170 queued
  (`screening/v2/subscription-queue.jsonl`); 1,222 new string failures still need the D0029-style
  rescue pass; front-matter volumes excluded.
  **Title resolution (D0029-2) NOT complete:** 1,161/2,107 classified, 946 lookup-incomplete (S2/arXiv
  rate limits, OpenAlex quota until ~05:30 IST); queue empty because untested
  (`corpus/title-resolution-report-2026-10-16.md`). The previous session (Resume DLM Discovery
  EXP-003) edited `tools/resolve_title_only.py` at 23:50 to look up only reference-marker records plus a
  random check of 60 others, unrecorded, and left `nohup python tools/resolve_title_only.py run`
  (PID 37132) running; its outputs will overwrite the lit-scout outputs. Decide between the two designs
  from its random-check result, then record a decision.
  **Criteria v1.1** drafted (`screening/criteria-v1.1.md`, 14 rules, new X0, D0032 row proposed;
  recommends option b: 19 both-excluded records get a pre-declared full-text check). Red-team audit
  running -> `review/audits/2026-10-16-redteam-criteria-v1.1.md`; D0032 not yet recorded.
  Note: the `dlm-expert` agent type is not registered in sessions started outside this worktree; run
  it as general-purpose with `.claude/agents/dlm-expert.md`.
- **HANDOFF 4 (2026-10-16 early; overrides older blocks).**
  Read memory `dlm-tool-access-requests` and the KB `research/expert/dlm-expert-kb.md` (+ three
  `web-digest-*.md`). New core agent `dlm-expert` (tools/build_agents.py) is the default worker;
  auditors unchanged; max 3 agents at once (was breached twice; keep to it).
  **Done since HANDOFF 3:** EXP-003 done + audited (D0022-D0025; result in H0007-H0009); census v2
  (D0020-D0021); manuscript 35 pp + 8 pp supplement, abstract 100 words, citations validated;
  free-source searches + string revisions (D0026-D0028: S1''/S2''); screening of 1,953 records by
  A (Sonnet) and B (Opus): kappa 0.911 [0.892, 0.929] (`analysis/screening/agreement-v2.log`),
  rule D0030 = pass if either passes -> 954 pass; validation of the automation filter (D0029,
  reversal triggered) -> Haiku rescue pass over 4,421 exclusions done (15+ includes, ~300 unclear;
  sensitivity 2/2 on V1); `screening-ambiguities.md` lists every class to settle in criteria v1.1
  before full text. **User decisions 2026-10-16:** full-text screen ALL records, extract RQ data on
  a stratified sample + all multimodal; e-gateway first.
  **In progress:** (1) title resolution of 2,107 title-only snowball records (lit-scout running ->
  `research/review/screening/v2/title-resolved-queue.jsonl`, `corpus/title-resolution-2026-10-15.json`);
  (2) Scopus via the user's Chrome (Claude in Chrome; VIT access works there, the built-in browser
  lacks the user's access extension): five queries run (`research/sources/search-raw/scopus/
  scopus-queries-20261016.md`, counts 876/530/134/1,670/836); EXPORT needs the user to sign in to a
  personal Scopus account; user approved the five CSV downloads. Then Web of Science, IEEE, ACM DL,
  SpringerLink, ScienceDirect the same way (combined NOT-free query + NOT parts separately; record
  counts; ask download approval per database).
  **Update 2026-10-16 ~03:00 IST: Scopus DONE.** User signed in to a personal Scopus account in
  Chrome; five CSV exports (4,046 rows, all with abstracts) in `research/sources/search-raw/scopus/`
  (hashes in `scopus-queries-20261016.md`; D0031). Export dialog recipe: select all, Export > CSV,
  tick Bibliographical information + Abstract & keywords, turn OFF "Truncate to optimize for Excel",
  do not tick "Save as preference"; files land in C:\Users\Shlok\Downloads as scopus_export_*.csv.
  **Remaining databases (in the user's Chrome, Claude in Chrome tools):** Web of Science (TS=,
  export cap 1,000 per file: split by PY), IEEE Xplore, ACM DL, SpringerLink, ScienceDirect; same
  plan (combined NOT-free union query + NOT parts separately, counts first, then ask download
  approval per database). The title-resolution lit-scout agent was still running at handoff: check
  for `research/review/screening/v2/title-resolved-queue.jsonl` and
  `research/review/corpus/title-resolution-2026-10-15.json`; if absent, rerun it (brief in D0029 item 2).
  **Next after searches:** lit-scout ingest + dedup of exports; dual-screen new database records;
  criteria v1.1 from the ambiguities; full-text screening of all passing records (two screeners on
  key sections); extraction on the sample; section 05 RQ evidence; PRISMA counts final; red-team
  referee pass. **Still needs the user:** human screening sample (218) + 120 disagreements (RAISE
  validation); professor's name/school/e-mail, ORCIDs; OSF registration (retrospective) of the
  protocol; protocol freeze.
- **STATE 2026-10-15 ~17:30 IST (newest; overrides older blocks).** Order of work confirmed by the
  user: Paper 1 (review, ACM CSUR) first, Paper 2 (research article) second; keep the framework
  (D0011) as the spine. **EXP-003 done and audited** (gate PASS WITH CORRECTIONS): E3-H1 positive,
  Delta1 = 0.126 [0.076, 0.177] (not confirmed by CLIP; may include quality-mediated coupling);
  E3-H2a not detected (W2); E3-H2b positive 0.077 [0.024, 0.131]; ledger H0007-H0009, X0003,
  D0022-D0025; results committed on branch claude/dlm-discovery-resume-ca3357 (077fb1d, b007f05).
  **Manuscript** `paper/review/`: all sections drafted except 05 (RQ evidence, needs full-text
  extraction), main 35 pp (CSUR limit incl. references) + supplement 8 pp; clarity edit done;
  citations validated (96 entries). **Running:** lit-scout on the free databases (OpenReview, ACL
  Anthology, Semantic Scholar, OpenAlex, DBLP, snowballing) -> `review/corpus/new-records-2026-10-15.jsonl`
  and `subscription-search-sheet.md`. **Needs the user:** subscription databases (Scopus, WoS, IEEE,
  ACM DL, Springer, ScienceDirect) through the VIT e-gateway in the built-in browser (user logs in;
  Claude runs searches and exports with per-download consent); human screening sample (218) and
  120 disagreements; professor's details; protocol freeze decision. **Then:** screen new records,
  full-text screening and extraction for RQ1-RQ6 (section 05), PRISMA counts final, red-team
  referee pass, release package.
- **HANDOFF 3 (2026-10-15, about 08:45 IST; newest block, overrides all older). Start here.**
  **Two worktrees.** The EXP-003 driver runs in `.claude/worktrees/dlm-discovery-resume-ca3357`
  (its `runs/EXP-003/` is untracked and only there). All other work now happens in
  `.claude/worktrees/resume-dlm-discovery-exp-003-334706` (branch fast-forwarded to the ca3357 tip
  6573351; the harness blocks writes into another worktree). Check the driver at
  `<ca3357>/runs/EXP-003/driver.log`; when DONE.txt exists, run the frozen analysis there.
  **Done this session:** no restart since HANDOFF 2 (boot 04:32; no events 41, 1001, 6008, 1074
  after 08:00); driver PID 37236 alive in M1. D0018: engineer's interpretation calls accepted,
  card 1.2 erratum appended (unconditional branch masks all observed positions, verified in code),
  firewall disclosure recorded. **User decision 2026-10-15:** run everything now despite weekly
  88 percent (user will upgrade the plan if the limit is hit); save work often.
  **Running (agents write as they go):** novelty-auditor on EXP-003 ->
  `review/audits/2026-10-15-novelty-EXP-003.md`; census coder B (Claude Opus) ranks 92-128 ->
  `review/census/coder-B-claude-r092-r128.jsonl`; coder A (Claude Sonnet, blind) ranks 1-40 ->
  `coder-A-claude-r001-r040.jsonl`. Brief for all coders: `review/census/CLAUDE-CODER-BRIEF.md`.
  **Remaining batches:** B 129-165, 166-202 (stop when B's eligible count, Codex ranks 1-91 plus
  Claude, reaches 150; Codex had 66 eligible); A 41-80, 81-120, 121-160, 161-202 (A codes every rank
  B coded). Then agreement (before reconciliation, raw disagreements kept), adjudication,
  census-result-v2. Then EXP-003 analysis and gate-auditor, then manuscript.
  **Update 2026-10-15 ~10:00 IST.** Novelty audit done (D0019: incremental 0.65; wording limits).
  Census coding complete: sample = ranks 1-176; coder B (Codex 1-91, Claude Opus 92-176 plus
  19, 79) 151 eligible; coder A (Sonnet, blind) all 176 ranks. Agreement before reconciliation in
  `analysis/census/agreement-random.log` (script `agreement_random.py`), 158 field disagreements in
  `review/census/disagreements-random.csv`; ambiguities in `review/census/coder-ambiguities-2026-10-15.md`.
  **Running:** adjudicator (Opus) writing `review/coverage/census-codebook-v1.2.md` (rules only).
  **Next:** two adjudicators apply v1.2 to the disagreements (ranks 1-88, 89-176) ->
  `review/census/census-random-final.jsonl` + notes; census-result-v2; then EXP-003 analysis when
  DONE.txt exists; then manuscript. Datasets deleted by the user (C: 203 GB free).
  **Update 2026-10-15 ~10:35 IST.** Census adjudicated (v1.2, two adjudicators + harmoniser;
  D0020; protocol section 10 amended) -> `review/census/census-random-final.jsonl`; result
  `review/coverage/census-result-v2.md` (146/152 headlines non-plain or unstated; summary log
  `analysis/census/summary-random.log`). Codex coder B failed to read 15 papers in ranks 1-88
  (adjudicated from the paper; agreement also reported without them). **Running:** gate-auditor on
  census-result-v2 -> `review/audits/2026-10-15-gate-census-v2.md`; manuscript-writer: outline,
  acmart skeleton, Introduction, Review method, census section in `paper/review/`.
  **Next:** apply audit corrections; EXP-003 frozen analysis + gate-auditor when DONE.txt exists;
  manuscript sections design space, error budget, open problems; then research-humanizer.
  **Update 2026-10-15 ~10:50 IST.** Census v2 corrected after gate audit (D0021): 147/153 =
  0.961 [0.917, 0.982]. Manuscript started (`paper/review/`, commit 7c71535): OUTLINE.md, acmsmall
  skeleton, Introduction, Review method, census section drafted (18 pp; ~2.8 pp over budget);
  stubs: notation, design space, RQ evidence, error budget, open problems, EXP-003, limitations,
  conclusion. **PRISMA blockers found by the writer (need the user and professor):** (a) only two
  arXiv searches run; the protocol's other databases and snowballing not run; (b) logged S1 query
  differs from the protocol string; recall vs seed list 421/540 = 78 percent, no pilot record;
  (c) human validation (218 sample) and the 120 screening disagreements still undone; (d) no
  full-text screening of the 1123 passed records (only the 176-record census sample read);
  (e) protocol never frozen (still DRAFT); (f) PLAN.md and D0011 still cite the old meta-analysis
  title and 47-model counts; (g) professor's name, school, e-mail, ORCIDs, and exact model IDs of
  screener A and the Claude coders not recorded. Weekly usage 98 percent at 10:50.
  **Update 2026-10-15 ~12:00 IST (after weekly reset; user upgraded plan).** D0022: EXP-003 hard
  stop raised to 8.5 GPU-h with the user's yes (cost overrun ~1.4x; watcher kills the driver at
  8.5 h; `runs/EXP-003/ACK_STOP_BUDGET.txt`). Manuscript now 33 pp, sections 01-04, 06-08 drafted,
  figures 1-4 from scripts (`paper/review/scripts/`), Table 4 codes verified, citations validated
  (`review/audits/2026-10-15-citations-paper1.md`; support fixes applied; anonymous OpenReview
  source kept once, flagged). **Next:** when DONE.txt exists (expected ~15:00): frozen analysis in
  the ca3357 worktree, gate-auditor, ledger + section 09 under card rules W0-W5 and D0019 wording
  limits; then limitations, conclusion, abstract; clarity edit (research-humanizer); cut to budget
  (candidate: Table 4 to the supplement, Fig. 3 duplicates it).
  **User side task (done):** delete datasets for storage (Paper 3 `data/raw` 187.9 GB, ML paper `data`
  0.3 GB, Dam `periyar_ccd_rnn/data` 0.14 GB); commands given in chat; Claude does not hard-delete.
- **HANDOFF 2 (2026-10-15, 08:10 IST).**
  Overnight: the EXP-003 driver finished the pilot (no stop rule; n_generate 138, 120 eligible,
  share 0.875) and the controls generation and scoring, then stopped at 03:16 on a **code bug**
  (UTF-8 files read with the Windows code page; KeyError on a non-ASCII noun). The laptop
  restart at 04:29-04:32 was **Windows Update** (System log 1074, MoUsoCoreWorker and
  TrustedInstaller), not a GPU crash, and interrupted nothing. Fixed (explicit UTF-8 in
  tables.py, frozen_analysis.py, score.py, chunks.py; pilot_analysis.py left as run under its
  frozen hash). Controls (D0017): NC-1 pass (-0.0003), PC-2 pass (guided T2I matched 0.77 vs
  cross 0.17), **PC-1 fail** (TF - Ind = 0.031, p 0.40): under plain sampling even an image
  generated after the whole completion shows no detectable noun-level dependence on it, so every
  EXP-003 null is "not measurable with this instrument" (W2), while a positive G - P64 stays
  readable. Main stage restarted 08:06: driver PID 37236 (`runs/EXP-003/DRIVER_PID.txt`),
  M1 (P64 and G) -> M2 (O0) -> M3 (P32) -> scoring -> DONE.txt.
  **If the laptop restarts again:** check `runs/EXP-003/driver.log` tail and STOPPED.txt; restart
  with the `Start-Process` command in `runs/EXP-003/IMPLEMENTATION.md` section 4 (every unit is
  resumable; the GPU clock persists in clock.json). Ask Shlok to pause Windows Update while runs
  are going (Settings > Windows Update > Pause updates).
  Everything in HANDOFF (below) still applies.
- **HANDOFF (2026-10-15, about 01:50 IST).**
  **Running now, unattended:** EXP-003 driver, PID 54920 (`runs/EXP-003/DRIVER_PID.txt`, log
  `runs/EXP-003/driver.log`). Card `research/preregistration/EXP-003-value-rule-consistency.md`
  v0.3.2 SIGNED (statistician and red-team; ledger H0004-H0006, X0002). Implementation and how to
  check, stop or resume after a reboot: `runs/EXP-003/IMPLEMENTATION.md` (sections 4, 5; restart
  with the PowerShell `Start-Process` form, not `run_all.bat`). The driver runs pilot -> firewalled
  pilot analysis with the n rule and stop rules 9.1-9.3, 9.6 by script -> controls (NC-1 stop) ->
  M1-M3 -> analysis freeze -> scoring. It writes `runs/EXP-003/STOPPED.txt` (exit 3) if a stop
  rule fires, `DONE.txt` when finished.
  **First actions next session:** (1) `tasklist /FI "PID eq 54920"`; tail `driver.log`; if
  STOPPED.txt exists, read it: the likely trigger is stop rule 9.1 (scoring costs more than the
  card's 10.6 s per prefix: cross-prefix queries, placebo nouns for four arms and CLIP). The
  engineer's suggested remedy, scoring placebo for P64 and G only, needs a dated card amendment
  before any change. (2) Review and record the engineer's interpretation calls (IMPLEMENTATION.md
  section 5: noun-key -es rule, PC-2 derangement seed 5303, placebo pool smaller than |D|, the
  "such samples" definition in 9.2, the constant 1.21 in the n rule) and the factual correction
  that UniDisc's unconditional branch masks every observed position (system prompt, markers,
  prefix), not only the prefix (card 1.2 says prefix only). (3) Firewall disclosure to record: the
  engineer's smoke tests used pilot prefixes 0-1 in the scratchpad and printed a 2-prefix Delta1
  class; nothing entered `runs/`; pilot data never enter tests. (4) After DONE.txt:
  `python analysis/EXP-003/frozen_analysis.py main`, then gate-auditor check of the numbers.
  (5) Not implemented: tail-entropy hook, G-low/M4, CLIP lift bootstrap (embeddings stored).
  **State of the science.** EXP-001 stopped at PG-V (D0016): under plain T = 1 sampling UniDisc's
  joint completions show no completion-specific image link (textures). EXP-002 demoted (D0013).
  MDLM reproduced (G4, -0.50%). Framework v2 (`review/framework-v2.md`, D0011): E_sel/E_tilt
  withdrawn; contributions = design space (47 models), value-rule census (37 of 45 headlines
  non-plain or unstated; `review/coverage/census-result-v1.md`), budget as taxonomy, open
  problems. Screening done (1453 records, kappa 0.728); random-sample census: Codex coded 86 (66
  eligible) before its limit (until 2026-11-10, D0015).
  **After the 2026-10-19 17:00 UTC reset:** census coder B (Claude Opus) for the rest of the
  150-eligible sample, coder A (Claude Sonnet) blind on all, agreement, adjudication; novelty audit
  of EXP-003 before any claim; then manuscript drafting. **Human tasks for Shlok:** 218-record
  screening sample (`review/screening/HUMAN-SCREENING-INSTRUCTIONS.md`), 120 disagreements
  (`review/screening/disagreements.csv`).
  **Safety and process rules now in force:** every GPU job through `tools/gpu_guard.py`
  (two HYPERVISOR_ERROR crashes on 2026-10-14); Codex tools resume one read-only thread per 20
  calls; downloads have no size limit; hand off at about 850k context. Budget: weekly 86 percent.
- **Superseded (2026-10-15, early).**
  EXP-001 v0.5 was signed, implemented (130 tests pass; `exp001/`, `analysis/EXP-001/`,
  `runs/EXP-001/IMPLEMENTATION.md`) and STOPPED at its construct gate PG-V under preregistered
  rule 11.1 (D0016): under plain sampling at T = 1 UniDisc's joint completions show no
  completion-specific image link (rung 2 m - s 0.151 < 0.25; m - s_sp about 0; images are
  textures); checker valid (PC-F). One protocol deviation recorded (prefix layout space fix
  between rung-1 runs). Images are unlicensed and kept local (`runs/EXP-001/image-hashes.txt`).
  G4 done: MDLM reproduced (22.935 vs 23.05, -0.50%; `runs/G4-mdlm-repro-2026-10-14/report.md`);
  the bf16 gap was dropout (train mode).
  **EXP-003** (new, preregistration draft `research/preregistration/EXP-003-value-rule-consistency.md`):
  plain vs official guided sampler vs CFG-0 on fresh prefixes; primary discordant-noun link
  Lambda_d; about 6 wall-clock GPU-hours. Running: statistician and red-team reviews (sonnet).
  Codex exhausted until 2026-11-10 (D0015): census coding by Claude coders after the 2026-10-19
  reset; Codex tools fixed to resume one read-only thread per 20 calls.
  **Budget: weekly 86 percent on 2026-10-15** (resets 2026-10-19 17:00 UTC). Before reset: only
  EXP-003 review, sign-off and the guarded run. After reset: census coders A and B, novelty audit
  of EXP-003, then manuscript drafting. Human tasks pending: 218-record screening sample, 120
  screening disagreements.
- **Superseded (2026-10-14, night).**
  Laptop crashed twice under sustained GPU load (bugcheck 0x20001; memory `laptop-gpu-crashes`);
  user chose guarded runs: every GPU job through `tools/gpu_guard.py` (15-min chunks, 85 C stop,
  telemetry), checkpointed, duty cycle about 50 percent, batch <= 8. Python child processes exit
  0xC0000409 at teardown after finishing (results written); watch it.
  D0013: EXP-002 demoted (coupling negligible at N = 1024; red-team check reproduced). EXP-001 is
  the single preregistered experiment: card v0.4 "draft for signature" (commit 7bce081), task =
  prefix-conditioned joint completion (D0014), core path about 27.3 wall-clock GPU-hours.
  Novelty: per-step cross-modal measurement novel (audit 0.60 plus full-text check of VRCD,
  VIG-Sampler, PUNT: not reported); dependence-aware schedule incremental (DAPD 2603.12996).
  **Running:** statistician round 4 and red-team round 3 (signature checks); repro-engineer G4
  (MDLM, guarded; gates EXP-002's optional check only); Codex census coder B (86+ coded);
  LLaDA download (4 connections).
  **Next:** signatures -> ledger rows (hypotheses H-A, H-B, H-C; experiment EXP-001) -> lab-engineer
  implements EXP-001 (samplers with custom commit plans, S_theta estimator, gates PG-1, PG-2,
  PG-V) -> gates -> pilot -> core path. Budget: weekly 76 percent at 2026-10-14 night; Claude
  census coder A and manuscript drafting wait for the 2026-10-19 reset.
- **Superseded (2026-10-14, evening).**
  User: no download size limit; continue in this session to about 850k context (D0012).
  **Experiments (the significant result):** EXP-001 (cross-modal dependence on UniDisc) and EXP-002
  (sample-then-filter decomposed into sharpening and coupling at k >= 2; new: 2605.12522 and
  2609.34509 are k = 1 only, `review/dossier/prior-art-2605.12522-experiments.md`) are drafted in
  `research/preregistration/`; statistician: "sign with 12 required changes" each
  (`review-statistician-2026-10-14.md`). Toy prior `analysis/framework/check_coupling_k2.py`.
  Lab engineer (running) is setting up UniDisc and MDLM: `runs/env-2026-10-14/` (MDLM 21 ms per
  pass at L = 1024; UniDisc OOM issues, layout may be 1024 px). **Next:** apply statistician
  changes plus setup facts as card v0.2, red-team sign-off, pilots.
  **Census (Paper 1 contribution 2):** 47-model census reconciled (`review/coverage/census-
  result-v1.md`: 37 of 45 headlines use a non-plain value rule or do not state one; 12 report
  entropy; 10 of 37 sweeps state the rule fixed; blind kappa before reconciliation in
  `analysis/census/agreement.log`). Codebook v1.1 for the corpus. **Screening done:** 1453 records
  (`review/screening/`), A (Claude) vs B (Codex) pass/exclude kappa 0.728, 1123 pass both, 120
  disagreements for the human (`disagreements.csv`); human validation sample of 218 waiting for the
  user (`HUMAN-SCREENING-INSTRUCTIONS.md`). **Random-sample census:** order seed 20261015 over 1106
  records (`review/census/census-order.csv`), texts in main checkout `research/sources/
  census-text/`; Codex coder B running to 150 eligible (`review/census/coder-B.jsonl`); then a
  Claude coder A on the same ranks, blind; then agreement and adjudication.
- **Superseded (2026-10-14, end of build session).**
  Handoff because controller context passed 250k. Read `review/framework-v2.md` first (sections A
  and D), then decision D0011.
  **Outcome of the build:** the selection term failed. Red-team (`review/audits/2026-10-14-red-
  team-selection-term.md`, 2 fatal, 11 major, 10 minor; scripts reproduce) and the full-text
  prior-art check (`review/dossier/prior-art-selection.md`: 2605.12522 has the k = 1 commit law,
  majorisation and the sample-select-resample fix in code; Hayakawa et al. 2510.04525; 2609.34509;
  Beirami et al. 2401.01879) mean E_sel and E_tilt are withdrawn as new terms (D0011). framework-v2
  uses one signed value slot V; P2 withdrawn; P1 narrowed to k = 1; P5 restated in a named split
  S_theta with a mixture-reference estimator, checked by enumeration
  (`analysis/framework/check_crossmodal_mixture.py`, 0 failures). Paper 1's contribution is now:
  (1) design space tested on 47 models, (2) value-rule and reporting census (29 of 40 headlines use
  a non-plain value rule; 5 report entropy; 1 of 14 guided models sweeps steps with guidance fixed),
  (3) budget as taxonomy with credited identity, (4) open problems with the evidence each needs.
  Codex round 4 (`research/debates/2026-10-14-framework-v1/round-04-codex.md`): ACCEPT D3 and D4;
  NEEDS-EVIDENCE D1, D2, D5; census needs independent coding with agreement before reconciliation;
  the one addition that would move the review to acceptance is a controlled frozen-checkpoint
  four-arm value-rule result, unless 2605.12522 already has it.
  **Next, in order (fresh session; weekly budget 64 percent, reset 2026-10-19 17:00 UTC):**
  (1) paper-reader, short: do 2605.12522's experiments cover the four-arm comparison (SF,
  resampled twin, confidence-ranked RS, tilted twin) at matched passes with an entropy-matched
  frontier? This decides Paper 2 and D4. (2) Write the census fields and operational definitions
  into `review/protocol.md` section 6 (value rule classes, entropy reported, sweep with value rule
  fixed, guidance fixed), with statistician sign-off on the agreement plan. (3) Screening plan for
  the 883 new arXiv records (`review/corpus/arxiv-S1-*.jsonl`, `arxiv-S2-*.jsonl`). (4) Ask the user
  about downloads above 5 GB (UniDisc 5.63 GB for P5; LLaDA-8B 16 GB) once Paper 2's first
  experiment is chosen. (5) Tie correction to the k = 1 law in `method/selection-term.md` T2(a)
  (prior-art-selection.md concern 3). (6) Human authors read framework-v2.
  Dispatch record this session: paper-reader x4 (sonnet; primers, design space, prior art; all
  useful), method-architect (opus; useful, then refuted in part), red-team (opus; decisive),
  novelty-auditor (opus; useful but missed Hayakawa and was wrong on N4 at k = 1; E1 only),
  Codex rounds 2 and 4.
- **Superseded (2026-10-14, build session).**
  User said "start the build" with the recommended plan, despite FRUGAL budget (weekly 63 percent).
  Done and committed: `review/framework-v1.md` (25 primer edits applied, v0 kept);
  `review/coverage/design-space-v1.md` + `.csv` (47 models, 36 fit, 11 partly, 0 no; misfits:
  length-changing edit channels, stochastic memory, graded evidence, joint-over-set predictors,
  sequence-level selection; census: 29 of 40 headlines use a value tilt or selection, 5 of those
  report entropy); `review/method/selection-term.md` with `analysis/framework/check_selection.py`
  (61 exact checks pass on rerun). Key results: E_sel is defined only against a reference; the
  canonical one is matched rank-then-sample (same position law, values resampled), runnable as
  sample-select-resample; per-step forward E_sel is infinite for sample-then-filter; temperature,
  top-p, argmax and CFG are state-only tilts (E_tilt, inside the identity), so only 4 of the 29
  census headlines use true E_sel (sample-then-filter) [recount needed]; **P2's premise is false**
  (E_fact alone can push entropy far below H(q)); toy U-shape in steps under SF. arXiv S1+S2
  retrieved: 1303 unique, recall 78 percent, 883 new candidates (not yet screened). Codex debate
  `research/debates/2026-10-14-framework-v1` round 2: P1 not identified as stated, E_sel may be
  decomposition-dependent, framework risks reading as identity plus labels without one validated
  new prediction. `tools/debate.py` fixed (relative path bug).
  **Running at this point:** red-team (opus) on selection-term + framework-v1 + Codex objections,
  report `review/audits/2026-10-14-red-team-selection-term.md`; novelty-auditor (opus) on N1-N8,
  report `review/audits/2026-10-14-novelty-selection-term.md`.
  **Next:** read both audits; write `review/framework-v2.md` applying the 15 method edits as
  amended by the audits; Codex round 3 with the content pasted into the debate folder; recount
  the census with the tilt/selection split; screening plan for the 883 new records.
- **Earlier state (2026-10-14, late session).**
  User: two-week horizon for Paper 1 (about 2026-10-28), quality first, the review must carry a
  significant result (D0010). Budget was FRUGAL (weekly 58 percent at about 22 percent elapsed;
  resets 2026-10-19 17:00 UTC), so the user chose sequential primer agents only this session.
  **Done this session (step 1 and 2 of the plan):**
  - `review/dossier/primer-gaussian.md` (paper-reader, sonnet, 364k tokens; useful). Six papers
    read (Diffusion-LM, CDCD, Plaid, DFM, Duo, BD3-LM; SSD-LM method only; TESS, CANDI, Simplex
    Relaxation not read). Corollary 3 (step size as parallelism) not stated in any of them; toy
    per-step TC ~ step^2.16. Gaussian samplers add a final-rounding factorisation term
    TC(x given z_0); self-conditioning breaks "policy depends on z_n only"; "implicit revision"
    is qualified (pinned conditioning, freezing below an identifiability noise level); Duo's
    duality is per-position per-time only, not trajectories. 14 numbered edits in section 5.
    Two proof steps flagged as possibly unjustified (BD3-LM App. B.5; Duo Thm 3.2 setup), low
    confidence because of conversion: check against the PDFs.
  - `review/dossier/primer-multimodal.md` (paper-reader, sonnet, 374k tokens; useful). Show-o,
    UniDisc, MMaDA, MMaDA-Parallel, FUDOKI, Lumina-DiMOO, Transfusion, BAGEL, Show-o2, LaViDa-O
    at sections-read level (E2-); Muddit, LaViDa, Dynin-Omni not read. **P5: no paper measures a
    cross-modal quantity per step.** Premise has weak indirect support (UniDisc App. I CFG
    Fig. 24-25; LaViDa-O Table 13). The only joint-vs-sequential contrast (MMaDA-Parallel
    Tables 3, 10) favours joint but is confounded. E3: the released MMaDA-Parallel-A sampler
    commits no image tokens in the first quarter of steps (parallel_generator.py lines 156-160,
    219-220), unlike the paper's text. Toy [V]: E_fact = within-text + within-image + cross-modal
    CMI (error 6.6e-16), so P5 as worded is near an identity; split into P5a/P5b (D0010).
    "No new machinery" fails in four places (guidance, per-modality weights and schedules,
    continuous image channels, output-level revision). 11 numbered edits in section 6.
    Cheapest P5 test: frozen UniDisc 1.4B interleaved checkpoint, **5.63 GB download, which
    needs the user's yes (above 5 GB)**, licence not stated (E1), about 8 GPU-hours, not run.
  - arXiv count retry worked (S1 1158, S2 173, S1n 731 hits); `run` not yet executed.
  **Next, in order (fresh session):** (1) write `review/framework-v1.md` (v0 stays) applying the
  25 edits from both primers, with P5a/P5b and rewritten P1-P3; (2) method-architect (opus)
  formalises E_sel (law of committed values under keep-the-most-confident-sample selection,
  and CFG as an E_sel analogue) and the multimodal E_fact^X term; red-team (opus) attacks both;
  (3) 40-model design-space table and coverage test; (4) `python tools/search_arxiv.py run S1 S2`;
  (5) ask the user about the UniDisc download for the P5 pilot (Paper 2 candidate); (6) humans
  read framework-v1. Weekly budget should be checked first; heavy steps after the reset.
- **Earlier state (2026-10-14, end of day).**
  User decision: the target stays ACM Computing Surveys (D0009). Paper 1 is being rebuilt on an
  integrating framework: `review/framework-v0.md` (generation as a commitment process, five design
  choices C1 to C5, an error budget of factorisation, learning, selection and stale-computation
  terms, and a taxonomy of methods by the term they change). It has been checked once against
  sources: `review/dossier/competitor-anatomy.md` (organisation absent from both surveys),
  `review/dossier/primer-foundations.md` (three unification claims correct with restrictions),
  `review/dossier/primer-samplers.md` (the two-term identity is already published: ARDM
  2110.02037 and the entropy-bounded sampler 2505.24857; selection and stale-computation terms and
  the taxonomy not found), plus an exact-enumeration check in `analysis/framework/`.
  **Next, in order:** (1) primer chapters still missing: the Gaussian and embedding diffusion
  family; unified multimodal models (Show-o, UniDisc, MMaDA, MMaDA-Parallel, FUDOKI, Lumina-DiMOO
  and the hybrid autoregressive-plus-diffusion models), with a check of proposition P5;
  (2) rewrite P1 to P3 from the primers and have method-architect formalise the selection term
  (what is the law of committed values under keep-the-most-confident-sample selection) and
  red-team attack the derivations; (3) coverage test: place every corpus record on C1 to C5 and on
  the lever table, starting with a design-space table of about 40 major models; records that fit
  nowhere show where the framework is incomplete; (4) retry the arXiv searches; (5) the humans
  read `framework-v0.md`. The claim-evaluability rubric and hypotheses E1 to E3 stay suspended;
  quality appraisal will be a descriptive component.
- **STOP AND READ FIRST (2026-10-14): the plan failed its own audits.**
  `review/audits/2026-10-14-red-team-plan.md` (editor's decision: reject without review; three
  fatal findings: scope trap at ACM Computing Surveys, evaluability construct unreliable and
  unvalidated, no expert human reads the corpus) and
  `review/audits/2026-10-14-statistician-protocol.md` (claim-identification "pass" not
  established, lower bound 0.59; E2 and E3 not testable as written; a real validation needs about
  160 papers and human raters). **Hypotheses E1 to E3 and "organised around claim evaluability"
  are suspended** pending the user's and professor's decision on the orchestrator's proposal:
  (1) Paper 1 becomes a PRISMA systematic review whose core is an integrating framework and
  critical synthesis by research question, with quality appraisal as a descriptive component
  built from extractive, checkable items; (2) first target Artificial Intelligence Review, with a
  scope inquiry to the ACM Computing Surveys editors in parallel; (3) the slack and evaluability
  questions move to Paper 2 as an experimental re-evaluation with reruns; (4) a stated minimum of
  human author reading. Nothing below this block overrides it.
  Work that is valid under any outcome: the integrating framework (RQ1), the database searches,
  the published-version resolution, PRISMA bookkeeping.
- **Order of work changed 2026-10-13 (D0005):** Paper 1 is a systematic review for ACM Computing
  Surveys; Paper 2 (research article, Nature Machine Intelligence) follows. Plan and gates R0 to
  R6: `research/review/PLAN.md`. The G0 to G9 gates below now belong to Paper 2.
- **Title and journal approved by the professor (D0006):** "Diffusion Language Models and Unified
  Multimodal Generation: A Systematic Review and Meta-Analysis", ACM Computing Surveys.
- **Current gate:** R0. Done: dossier (`review/dossier/csur.md`, `exemplar-anatomy.md`), Codex
  round 2, corpus seed (572 records from Awesome-DLMs at 194aa6bd). Pending: survey landscape
  (lit-scout was still running at handoff), protocol.
- **Next action, in order:** (1) rerun `python tools/ingest_awesome.py
  research/sources/md/awesome-dlms@194aa6bd.md` to fill arXiv metadata (API returned 429 today);
  (2) read `review/survey-landscape.md` header and write Claude round 3 in
  `research/debates/2026-10-13-review-angle/` (concede cross-paper regression, propose matched
  within-paper contrasts, split CA); (3) experiment-designer plus statistician write
  `review/protocol.md` (PRISMA 2020, inclusion rules, extraction form, meta-analysis plan);
  (4) novelty-auditor on CA; (5) database searches beyond the repo, then dual screening.
- **Update after lit-scout and Codex round 4 (2026-10-13, evening); this replaces steps 2 to 4:**
  - `review/survey-landscape.md` is done (96 papers rows). No existing survey has a PRISMA-style
    protocol or a reporting audit (14 scanned at keyword level, 18 at abstract level only).
  - **CA is not new as a qualitative claim**: arXiv 2609.01607 (2026-09-01), 2607.04423 Sec. 3.2
    and RealUnify 2509.24897 already say synergy is conditional or absent. CA survives only as
    pooled questions Q1 and Q2, credited to them. New candidate CD (step-scaling law) and the
    questions Q1 to Q5 are in debate round 3.
  - Codex round 4 rejects fixing "Meta-Analysis" in the title before poolable contrasts are shown
    to exist, and rejects CD as untested. Agreed settling step, **do this first**: a feasibility
    inventory. paper-reader agents extract every within-paper matched contrast and step sweep
    (outcome, variance information, sampler, task, what was held fixed) from the 28 multimodal
    records plus a stratified sample of about 40 inference and training records, then count how
    many meet pre-set comparability rules per question. Output `review/feasibility-inventory.md`.
    The protocol is frozen and the conjecture chosen only after that count.
  - If fewer than about 8 poolable contrasts exist for every question, tell the user: the
    subtitle "and Meta-Analysis" must change before submission.
- **Professor's guidance received 2026-10-13 (late):** critical review matters most; full PRISMA
  protocol with exact dates, database-specific strings, exclusion reasons, reviewer agreement and
  a quality appraisal table; consistent table categories; RQ1 to RQ6 answered from evidence;
  "check Discrete Diffusion too" (title or scope, meaning to be confirmed). Draft protocol
  written: `review/protocol.md` v0.1 (not frozen). Samples in `Sample papers/`: an Artificial
  Intelligence Review survey of multimodal **video** diffusion (s10462-026-11699-z; not about
  DLMs; has a "research gap analysis" section and ends with a proposed framework) and arXiv
  2506.13759v5 (closest existing survey). Both converted to `research/sources/md/`; paper-reader
  should extract their anatomy into the dossier.
- **Decisions delegated to Claude by the user (2026-10-13, night). D0007:** working title is now
  "Diffusion Language Models and Unified Multimodal Generation: A Critical Systematic Review of
  Discrete and Continuous Approaches". Budget check: weekly limit 41 percent used with 14 percent
  of the week elapsed (FRUGAL), so no agents were dispatched; a script did the work instead.
- **Running at handoff:** `tools/table_inventory.py` over all 540 arXiv records (captions flagged
  for ablations, step sweeps, remasking, AR comparisons, synergy; text flagged for seeds,
  intervals, code), then the arXiv metadata rerun. Log: `review/feasibility-run.log`; output:
  `review/feasibility/captions.jsonl`. HTML is cached, so rerunning the command resumes.
- **First actions next session:** (1) read the summary table at the end of
  `review/feasibility-run.log`; (2) dispatch hypothesis-smith (opus) with the inventory counts,
  `survey-landscape.md` section on prior CA and CB statements, and the four debate turns, to
  propose conjectures that the available within-paper data can test; (3) novelty-auditor on its
  top two; (4) debate round 5 with Codex; (5) user approval; then freeze the protocol.
- **Conjecture work (2026-10-13, late night).** `review/conjectures.md` holds seven candidates
  H1 to H7 (all E0). Orchestrator selected **H2 (slack conjecture)** and **H5 (noise-floor
  conjecture)**; ruling: H5's between-paper spread is allowed as a dispersion yardstick, not as a
  regression. Codex round 6: accepts H2 as lead candidate, rejects merging H2 and H5 into one
  claim (they measure different things), keeps H5 as a separate RQ6 analysis, and asks for a
  table-level pilot with frozen rules (interpolation of the baseline sweep, non-monotonic sweeps,
  missing variance, exact cell matching) before either organises the review. Agreed.
  Running at this point: novelty-auditor on H2 and H5 (`review/novelty-H2-H5.md`), and two
  stage-2 readers (`review/feasibility/stage2/summary-*.md`).
  **Next:** (1) read the three reports; (2) write `review/pilot-rules.md` freezing the H2 and H5
  computation rules; (3) pilot extraction on about 15 inference papers that report both quality
  and forward passes, with the extra fields listed in conjectures.md section 9, and compute the
  slack share by script; (4) debate round 7 with the pilot numbers; (5) user approval.
- **Results 2026-10-14 (supersede the "Next" list above).** Stage-2 summaries saved
  (`review/feasibility/stage2/summary-*.md`): pooling not supported for remasking or synergy,
  borderline for steps; variance almost never reported. Novelty audit: H2 novel at 0.55 (closest
  arXiv 2609.33947), H5 incremental (arXiv 2606.29228). **H2 pilot** (`review/pilot/
  h2-pilot-summary.md`): claim (a) supported at pilot scale (2 of 9 papers publish the needed
  baseline sweep), claim (b) not supported (slack share 0.00 in both computable papers).
  Debate rounds 7 and 8: both models agree to organise the review around **claim evaluability**
  with three separate pre-registered hypotheses E1 to E3; H2(b) moves to Paper 2 as an experiment.
  **Waiting on the user:** approval of this direction. **Then:** (1) write the evaluability rubric
  (one criterion per claim type, justified from the estimand) into `review/protocol.md` section 6;
  (2) two-rater reliability check on about 40 stratified papers (Claude agent and Codex, plus the
  human sample); (3) red-team and statistician sign the protocol; freeze; (4) database searches.
  Note: auditor agents have no MCP tools, so the novelty-auditor could not use Exa; either add the
  Exa tool names to AUDIT_TOOLS in `tools/build_agents.py` or have lit-scout run its searches.
- **Direction approved by the user 2026-10-14:** review organised around claim evaluability;
  slack conjecture H2(b) becomes Paper 2's experiment. Rubric and two reliability rounds done:
  `review/reliability/RESULTS.md`. Round 2 (rubric v0.2): claim identification kappa 0.71
  (passes), evaluable flag kappa 0.33 (fails); Codex is systematically stricter. Debate round 10:
  rounds 1 and 2 are development only; v0.3 must be frozen before a fresh validation sample.
  **Blocked on the user:** blind human rating of `review/reliability/round2/human-adjudication.csv`
  (30 claims; ideally a second human too). **Then:** write rubric v0.3 (extractive items, computed
  budgets, wording fixes), freeze, validate on a fresh sample, then red-team and statistician sign
  the protocol. The first-round `reliability/human-sheet.csv` is superseded.
- **2026-10-14, searches and venues.** `tools/search_arxiv.py venues` done:
  `corpus/venues-semantic-scholar.json`, 537 of 539 arXiv records found, 156 with a non-arXiv
  venue (ACL 40, NeurIPS 35, ICLR 17, EMNLP 15, ICML 11, NAACL 8, AAAI 8), 20 with a non-arXiv DOI.
  Semantic Scholar venue strings need checking against DBLP or Crossref before use in E2.
  **arXiv API returned 429 for every search request** (this IP fetched about 540 HTML pages on
  2026-10-13); no search has been logged yet. Retry `python tools/search_arxiv.py count` on
  another day before `run S1 S2`. OpenAlex answers, but its `search` parameter now maps to
  full-text search and phrase plus date filters returned zero: read the current OpenAlex API
  documentation before using it as a source; do not guess the syntax.
  Running: red-team referee review of the plan and statistician review of the protocol (both
  return text; save to `review/audits/`).
- **Agent definitions fixed:** hypothesis-smith, experiment-designer and method-architect had not
  loaded (unquoted colon in the description); `tools/build_agents.py` now quotes descriptions.
- **Exemplar reading was structural only (E1).** Before drafting, paper-reader must read two
  exemplar surveys in full.
- **Waiting on the user:** approval of the conjecture once audited; VIT reimbursement cap.
  Python environment, disk space and `hf auth login` are no longer urgent (Paper 2 only).
- **Budget mode at last check (2026-10-13):** FRUGAL (weekly 29 percent used, 11 percent elapsed).

## Gates
### G0 Setup and source integrity
- [x] Git repo, Project OS scaffold, `research/` tree
- [x] Merged framework, agent contract, 19 agents generated
- [x] Ledgers initialised (`tools/ledger.py`)
- [x] graph-memory wrapper repaired (`C:\Users\Shlok\tools\graph-memory.cmd` had a literal tab in its path)
- [x] Venue calendar checked against official pages
- [x] First frontier sweep (E1) saved
- [ ] Python environment with CUDA build verified on the 5070 Ti, lock file committed
- [ ] Seed sources hashed: MMaDA PDF, Awesome-DLMs README at pinned SHA
- [ ] gate-auditor verdict for G0

### G1 Frontier map and anomaly list
- [ ] Awesome-DLMs link inventory in papers ledger (blueprint counted 594 unique URLs at SHA 194aa6bd; recount)
- [ ] MMaDA claim-evidence matrix, including the Table 4 versus abstract mismatch and the evaluation README gap
- [ ] Closest 10 works read in full for T1 and for T2
- [ ] ECCV 2026 understanding-generation transferability paper located and read
- [ ] `research/reports/anomalies.md`
- [ ] gate-auditor verdict

### G2 Hypothesis selection
- [ ] 3 or more candidates with prediction tables
- [ ] novelty-auditor verdict per candidate
- [ ] red-team report per candidate
- [ ] Codex independent review
- [ ] **User approval of one hypothesis and one backup**

### G3 to G9
Checklists are added when the previous gate passes (criteria in FRAMEWORK section 7).

## Dispatch log
| Date | Agent or tool | Brief | Output | Useful? |
|---|---|---|---|---|
| 2026-10-13 | Exa `web_search_exa` | 2027 venue deadlines | FRAMEWORK sections 2 and 10 | yes: two of four requested venues are closed |
| 2026-10-13 | Exa `agent_run` medium | 8-question frontier map | `reports/lit-scout/2026-10-13-frontier-map.md` | yes: rows 5 and 6 sparse; grounding block was verbose, trim the schema next time |

| 2026-10-13 | Exa `web_search_exa` x3 | journal metrics and policies | PLAN section 2 | yes: CSUR JIF 30.4 and scope rule confirmed on official pages |
| 2026-10-13 | Codex via `tools/debate.py` | round 2 on review angle and conjecture | `debates/2026-10-13-review-angle/` | pending |
| 2026-10-13 | venue-intel (sonnet) | CSUR dossier and exemplar anatomy | `review/dossier/` | pending |
| 2026-10-13 | lit-scout (sonnet) | existing-survey landscape, prior statements of CA and CB | `review/survey-landscape.md` | pending |

## Validation tracker
| Item | Validated by | Date | Result |
|---|---|---|---|
| GPU is 12 GB laptop part | `nvidia-smi` | 2026-10-13 | confirmed |
| ICLR 2027 and AAAI-27 deadlines passed | iclr.cc, aaai.org | 2026-10-13 | confirmed |
| IJCAI, ICML, NeurIPS 2027 dates | third-party trackers only | 2026-10-13 | **projected, recheck** |
| Frontier map paper IDs | none yet | | **E1, unverified** |

## Decisions (mirror of the decisions ledger)
- D0001 2026-10-13: Gemini's pre-chosen architecture is not adopted (prior art, no evidence).
- D0002 2026-10-13: venue shortlist ICML or IJCAI 2027, fallback NeurIPS 2027; frozen at G7.
- D0003 2026-10-13: detector evasion and watermark removal replaced by clarity editing plus disclosure.
- D0004 2026-10-13: journal first. Nature Machine Intelligence, then IEEE TPAMI (or Nature
  Communications if VIT covers 7,350 USD), then a Q1 fallback. Supersedes D0002.
- Open with the user: VIT's reimbursement cap per paper; whether rented GPU time is acceptable
  for full-precision confirmation runs after Gate 5; restricted-data requests (SETUP_STEPS section 6).
