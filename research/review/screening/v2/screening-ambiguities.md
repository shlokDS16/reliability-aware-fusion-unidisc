# Screening ambiguities (search update 2026-10-15), compiled by the orchestrator for adjudication

## Validation screener V (300 auto-excluded records)
1. M19014 UniTMGE: text-to-motion and motion captioning; is human motion "another modality" under I1(b)? Marked unclear.
2. M02995 Ehrenfest process: discrete-state diffusion theory with no text application; I1(a)? Unclear.
3. M07984 LaDi-RL: latent diffusion decoded to text for reasoning; included (arguable).
4. M04871 INFO-SEDD: SEDD used as an estimator on synthetic/Ising data; excluded X1.
5. M03972 multi-sample preference optimization for LLMs and diffusion models in general; excluded X0.
Practice: title-only records clearly unrelated or non-text were excluded; DLM-like titles without abstract left unclear.

## Screener A, batch 1
1. M15992 Mobius (motion-language diffusion), VLA/robot cases (M08652): motion/actions as modality under I1(b)?
2. Generic discrete-diffusion theory with no text (M14971, M03831, M12175, M09321, M17892): unclear; continuous generic diffusion (M05850) X1.
3. Empty abstract with decisive title (M15918, M19130, M17812, M14533 excluded X1); about 40 DLM-pointing titles left unclear. Rule needed: can a title alone decide?
4. X1 vs X2 for text-conditioned non-text generation (TTS, T2I, text-to-motion, text-to-molecule): A used X2 when text is the stated conditioning input.
5. Adapter-coupled unified models (M15137 HieraQuery, M06731 UniVid, M13195, M03951): MLLM + diffusion decoder via adapter; "one jointly trained system"? Included.
Also: M18918 and M09530 duplicate (TrustLDM); M13102 Catalan title, English abstract (included); M11407, M11397 Ukrainian titles, English abstracts (not X8).

## Screener B, batch 1
1. Structured NLP outputs from diffusion (entity spans, tag sequences, denoised hidden states: M14484, M13889, M13881, M03416): coded X1; is structured NLP output "text"?
2. Diffusion VLM fine-tuned to robot actions (M15897 LLaDA-Nav unclear; M08652 MMaDA-VLA included because it also generates goal images): amendment covers actions only with autoregressive text.
3. Generic discrete-diffusion method/theory with unstated domain (M04373, M03831, M09321, M12175, M08827): unclear; X1 when explicitly non-text (M18900, M15208).
4. Diffusion LM repurposed as encoder or estimator (M16168 pplx-embed, M15450 InfoSEDD): does "output includes text" apply?
5. Motion or cell-expression as the other modality (M15992 unclear, M12951 CellUMM X1).
X7 practice: pipelines applying a DLM without saying whether it was modified (M17603, M13234, M14428, M15731) marked unclear.
