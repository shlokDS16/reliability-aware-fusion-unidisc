"""Second-model adapter for GATE: Omni-Diffusion 8B (4-bit), SAP AD.7 / AB.5 (family R). Text and image only; no audio, no speech decoder.

Import hygiene: `layout` (torch + numpy only) is safe to import anywhere; `loader` and `scorer` import the omni stack lazily and only inside functions, so collecting the
existing test suite in the project venv never imports transformers, bitsandbytes or omni_diffusion.

Design in one paragraph. The whole gate stack (`exp_p2.gate.scores`, `pipeline`, `dcache`, `evidence`, `arms`, `calibrate`) is written against the UniDisc id space: mask id 32000,
image ids 32001 + code, log-softmax restricted to the slice [32001, 48385) of the logits, text slice [0, 32000). Those constants are imported by name inside `exp_p2/gate/scores.py`,
which this task may not edit. `OmniScorer` therefore presents a VIRTUAL id space with exactly those constants and translates at the model boundary: virtual ids -> Omni ids on the way in,
Omni logits -> virtual logits (image columns only: the 8192 Omni codes fill the first 8192 columns of the 16384-wide image slice, the rest are -inf, so the restricted log-softmax is the
conditional over the 8192 valid codes) on the way out, including Dream's one-position logit shift. The gate code then runs unchanged on Omni.
"""
