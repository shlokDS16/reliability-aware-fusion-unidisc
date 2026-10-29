# Unanswered Questions

Open questions that should become future work items. Append only.
Move to the timeline with an answer when resolved. Do not delete.

Format: **[date]** - the question, why it matters, what would answer it.

**[2026-10-14]** - Which sampler schedule produced MMaDA-Parallel's Tables 3 and 10 (the released A-variant delays image commits to the last three quarters of steps)? It decides whether the only joint-vs-sequential contrast is what the paper says. Answer: read the M-variant generator and any config used for the tables, or ask the authors.
**[2026-10-14]** - Are BD3-LM App. B.5 (monotonicity in block size) and Duo Thm 3.2's setup correct as printed? Flagged from markdown conversions only. Answer: read the PDFs.
**[2026-10-14]** - May we download the 5.63 GB UniDisc interleaved checkpoint for the P5 pilot (above the 5 GB rule; licence not stated)? Answer: user decision plus a licence check on the model card and repository.
**[2026-10-14]** Do 2605.12522's experiments already include the four-arm comparison (sample-then-filter, resampled twin, confidence-ranked sampler, tilted twin) at matched forward passes with an entropy-matched frontier? It decides whether Paper 2 leads with a text value-rule experiment or the cross-modal measurement. Answer: short paper-reader pass on its Sec. 5 and App. C, plus its code at 8bafc9e.

- 2026-10-30: CLIP and SigLIP score 0.996-1.000 on the Study 2 matching task under every corruption. How should the TNNLS paper frame a UniDisc-internal fusion gain when off-the-shelf contrastive models almost solve the task? (No LRF-vs-CLIP claim is allowed by A6.6; red team to decide the framing at writing time.)
