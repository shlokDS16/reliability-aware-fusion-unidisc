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

## Screener A, batch 2
1. Generic discrete-diffusion/flow theory with no text (M07423, M13280, M08183, M06698, M01824): unclear; proposed rule: include only if language is named, else X1.
2. VLM/MLLM feeding a separately named diffusion decoder, presented as unified, joint training unstated (M19015, M15989, M16043, M18394, M14797, M08935): unclear; JanusFlow (M04162) included.
3. Discrete-diffusion VLA models, text generation unstated (M15330, M09851, M09916): unclear.
4. NLP-task diffusion producing labels or spans (NER, ABSA: M17653, M11849, M09557, M12328, M01553): unclear; M12807, M14235 X7.
5. Missing abstract with a clearly out-of-scope title excluded (e.g. M17320 X0; music, fonts, protein, motion X1): confirm this reading.

## Screener A, batch 3
Deviation to disclose: about 20 records with truncated abstracts were decided after reading the full text (title-and-abstract stage should not); ids not listed by the screener.
1. Frozen VLM plus added diffusion decoder, or MoT unified 3D (M15792, M09294): joint training unstated, unclear; M07750 X2.
2. Generic discrete-diffusion theory without text: unclear unless language named.
3. Diffusion VLA/driving on a diffusion-LM backbone outputting actions or trajectories: X1; possible reasoning-text output left unclear.
4. Masked-diffusion TTS/ASR/captioning: speech-token output X1; text output (transcripts, captions) included.
5. Diffusion as metaphor or non-generative role: X0 when no diffusion model; one ambiguous case unclear.

## Screener B, batch 3
1. Adapter-attached diffusion decoders on frozen/separate VLMs called unified (M15792 LayerBridge included, M07750 Forge-and-Quench unclear).
2. Domain-agnostic discrete/masked diffusion theory or methods (M10437, M10584, M03863, M18094, M10535, M07561, M00285): unclear; theory mentioning text generation included (M11387, M14364).
3. dWorldEval two versions (M08950 unclear, M17772 included): does a progress/success token count as natural-language output?
4. Embedding models on a diffusion-pretrained LM backbone (M08140 pplx-embed): I1(a)?
5. Non-diffusion parallel decoders benchmarked against DLMs (M09782 JetSpec, M12594 pcLLM): does evaluating a DLM only as a baseline meet I1?

## Screener A, batch 4
1. Humanoid motion/pose as the other modality (M15235 HumanExpert, M15236 HuMoGPT unclear; M12859 PoseDLLM included): does "3D" cover motion and pose?
2. LLM/VLM connected to separately trained diffusion decoders called unified or any-to-any (M03150 X-VILA, M17285 Qwen-Image-Omni, M14249 EmoSym unclear; M03633 UniFashion included).
3. Generic discrete-diffusion or flow-matching theory without text (M14735, M09141, M06218, M09003, M07228, M17869): A coded X1 here (batches 1-3 and B used unclear); text-framed theory included (M10159, M00847, M07124). Inconsistent across batches: adjudicate.
4. M12793 Binary Discrete Diffusion (Sudoku etc. plus Text8/OWT language modelling): included on the language-modelling results.
5. Abstract-less records: unclear unless obviously unrelated (M11786, M15533 X0) or a survey by title (M14799 X3).

## Rescue screener (Haiku), batches 1-2
- Batch 2 caveat: most abstracts read only to the visible 550-900 characters; about 14 ambiguous records read in full. Mitigation: every rescue record had already failed S1''/S2'' applied to the full title and abstract, so a diffusion-LM phrase in an unread tail would normally have matched the strings. Disclose.
- Pipelines (LLM + separate diffusion image generator) coded X2; tabular diffusion unclear; text rendered in images X2; symbolic music, graphs, molecules X1; missing abstract with a decisive title unclear.

## Screener B, batch 4
1. Puzzle/maze/ARC/chess-only discrete denoising (M15835, M12848, M19094): structured text or X1?
2. Motion/behaviour as the other modality (M15235, M15236).
3. Generic discrete diffusion/flow theory (M06218, M09141, M14735, M02145, M06714) unclear; masked-diffusion theory included (M10159, M06333). One shared rule needed.
4. SMILES, Newick, HLS pragma strings (M14279, M16987, M12789) coded X1; "structured text" note could cover them.
5. LLM + separately trained/offline diffusion decoder presented as unified (M03150, M06272, M03633, M14249) unclear; joint training or shared backbone stated (M19019, M17285, M15184) included.
