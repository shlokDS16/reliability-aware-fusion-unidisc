# Paper 2: candidate ideas for Shlok's choice (2026-10-27 night)

Target: Elsevier *Information Fusion* research article (10-35 pages, at most 50 references, highlights, abstract
at most 250 words), due Fri 31 Oct or Sat 1 Nov 2026. All work must run on the 12 GB laptop GPU.

How these were made (full reports linked; nothing below is a result yet):
- Ideation (7 ideas): `ideation/IDEAS-RAW-2026-10-27.md`
- Independent novelty audit (32 arXiv ids checked): `ideation/NOVELTY-AUDIT-2026-10-27.md`
- Independent red team (feasibility, validity, scope): `ideation/RED-TEAM-2026-10-27.md`
- Journal rules and paper anatomy: `style/STYLE-GUIDE-2026-10-27.md`, `style/IF-METHOD-ANATOMY-2026-10-27.md`
- Feasibility probes on the GPU: `probes/PROBE-REPORT-2026-10-27.md` (see the last section)

GPU-hour figures below are the agents' estimates, not measurements, except where a run directory is named.
The one measured fact: UniDisc 1.4B made a joint 512-px sample in about 6.6 s with 64 network calls, peak 8.2 GB
(EXP-003 run file in the Paper 1 worktree).

## Summary table

| # | Idea (one line) | Novelty audit | Red team | GPU estimate | Audio? | Figures it gives |
|---|---|---|---|---|---|---|
| A | **GATE**: a unified masked-diffusion model scores each *input* token by its own masked likelihood, re-masks unreliable ones (corrupted image codes, typo prompts), then marginalises or re-infills them | narrow delta, 0.60 | **GO with changes**, 0.55 | 12-18 h on UniDisc | no | reliability heat-maps on the token grid, corrupted -> repaired images, step-by-step re-infill strip, ROC curves, recovery-vs-severity curves |
| B | **Inherited boundary prior**: text-initialised unified models (Omni-Diffusion, MMaDA) commit the first and last image rows early, causing top-bottom duplication; null-prompt positional calibration as a fix, UniDisc as from-scratch control | narrow delta, 0.50 | KILL as lead, 0.70 (needs 8B models; 20-35 h) | 20-35 h | no | commit-step heat-maps per model, unmasking film strips, duplication grids with metrics |
| C | **Two-way evidence fusion**: fuse image->text and text->image mutual-information estimates by inverse variance, with adaptive mask allocation; the model verifies itself | narrow delta, 0.55 (assembly of known parts) | KILL standalone; GO as a component of A | 10-14 h | no | accuracy vs network-call curves, best-of-4 grids |
| D | **Equivalence-class confidence**: commit visual/speech tokens by the probability mass of near-equivalent codes, not the single best code | narrow delta, 0.65 (highest) | KILL, 0.75 (gain likely equals a temperature control) | 10-25 h | optional | confidence maps, 8-step unmasking, quality-vs-steps |
| E | **Text leads speech**: in Omni-Diffusion's one-canvas spoken answers, measure which modality commits first and gate speech on its aligned text | narrow delta, 0.55 | KILL for this deadline, 0.85 (speech stack on Windows; near-tautological metric) | unknown, 8-15 h if it runs | **yes** | joint text + spectrogram unmasking strip, commit-time scatter |

No idea was found to be anticipated, but every delta is narrow: the open part is a measurement or a new
combination, not a new principle. Ideas 6-7 of the raw file (modality dominance, information-triggered guidance)
were dropped (novelty unchecked / lowest novelty).

## Recommendation: A (GATE) as the main paper, with C's scoring machinery inside it

Why: best fit to *Information Fusion* (fusion of unreliable sources, with classical analogues: measurement gating,
false-alarm control, marginalising a missing source), it runs on the UniDisc stack already installed, it is a new
training-free method plus analysis, and it gives real-output figures (heat-maps, repaired images, re-infill strips).

Changes the red team requires (already applied to tonight's probes):
1. The reliability score as first written subtracted the prediction made with the other modality masked; that
   cancels the corruption signal (and is exactly zero for captions). Replaced by the plain masked log-likelihood and a
   prior-normalised version; the original kept only as a labelled control.
2. Use likelihood scoring (matching, verification) as the main task, not UniDisc's free-form captions, which are poor.
3. Controls: a random gate of equal size, an oracle gate, a gate on clean inputs, and the paired noise floor.

Main risks, stated plainly:
- One small model (UniDisc 1.4B, no stated licence) with weak text and image quality; a reviewer may ask for an 8B
  model. Adding MMaDA-8B or Omni-Diffusion needs the 8B path below.
- Closest work a reviewer will cite: Dropout Decoding (arXiv 2412.06474), DiSP (2602.22246, masks vision tokens of
  diffusion VLMs for backdoor defence), UniDisc's own appendix showing qualitative repair of corrupted pairs.
- Red team's estimate of a clean result set by Thursday: about 0.35.
- No audio in this idea. Only E brings speech, and it is the riskiest.

## Decisions needed from Shlok in the morning
1. **Pick the idea** (A recommended; or A with B's commit maps as a second analysis if the 8B path works).
2. **Omni-Diffusion code**: the permission check blocked cloning and installing the VITA-MLLM/Omni-Diffusion repository
   (third-party code). The 8B weights (16 GB) are downloading to the Hugging Face cache. Approve or decline cloning and
   installing its code in a separate environment (`.venv-omni`); it is needed for any 8B arm, for B and for audio (E).
3. **AI declaration policy**: Elsevier's guide wants a "Declaration of generative AI and AI-assisted technologies"
   section before the references; an older Elsevier policy page says AI used *in the research process* may need to be
   described in the methods. Your rule is "AI only in the declaration". Decide whether that holds (style guide Q1).
4. **Scope risk**: the journal's scope names fusion, not generative modelling. One precedent exists (TransDLM, a
   diffusion language model, Information Fusion 2025). Optional presubmission enquiry to the editor.
5. **Reference limit**: the guide says at most 50 references for research articles; plan to that.

## Feasibility probes run tonight
(Filled in from `probes/PROBE-REPORT-2026-10-27.md` when the runs finish.)
