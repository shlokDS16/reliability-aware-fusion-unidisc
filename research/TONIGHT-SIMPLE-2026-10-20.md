# Two small jobs, step by step (about 30 minutes in all)

You do not need the Excel sheets. Open each PDF from the link, answer the one question, and reply in
chat with one line per item, for example:

    A1 exclude X1, A2 include a, A3 exclude X1, A4 exclude X1
    B1 X2, B2 X0, B3 X1, B4 a, B5 ab, B6 a, B7 b, B8 no, B9 no

I then file your answers in the sheets and the decision ledger. If you cannot tell, write "unsure" for
that item; that is a valid answer and is reported as such.

---

## Job A: four papers that screener B could not read (you are the second screener)

For each paper, read the abstract and skim the method section, then answer:

**Question: does the paper's own model generate natural-language text or code with a diffusion
model (masked, discrete or continuous diffusion)?**

- If yes: answer `include a`.
- If its diffusion model generates only something else (RNA, DNA, protein or molecule sequences,
  images, ...) and the paper has no text or code output from that diffusion model: answer
  `exclude X1`.
- Exception that still counts as include (criteria v1.6, the R7 rule): the model is a
  language-model-style discrete diffusion model over token strings, and the paper (i) proposes or
  changes its sampler, decoding, caching, schedule, remasking or guidance, or (ii) has a results
  table comparing it with another generator (autoregressive or diffusion) on the same task, or
  (iii) has a results table that varies a diffusion setting (steps, unmasking order, remasking, block
  length), even though the strings are biological. Then answer `include a bio`.

| Item | Paper | PDF |
|---|---|---|
| A1 | M13184, Conditional generation and inpainting of non-coding RNA sequences with masked discrete diffusion | [M13184.pdf](sources/pdfs/fulltext/M13184.pdf) |
| A2 | M15873, Ligand-conditioned discrete diffusion protein co-design model | [M15873.pdf](sources/pdfs/fulltext/M15873.pdf) |
| A3 | M17195, Prot2RNA: a diffusion language model for protein-conditioned mRNA coding sequence generation | [M17195.pdf](sources/pdfs/fulltext/M17195.pdf) |
| A4 | R0308, Predicting and generating antibiotics against future pathogens with ApexOracle | [R0308.pdf](sources/pdfs/fulltext/R0308.pdf) |

---

## Job B: nine papers where the two screeners agreed on in/out but not on one label

The decision (include or exclude) is settled. Only the label is open. Pick one of the two values
shown, after looking at the abstract.

**Exclusion reasons (B1-B3):** X0 = the paper has no diffusion model at all; X1 = its diffusion model
does not produce text or code; X2 = text only conditions a diffusion model that produces something
else; X3 = it is a survey or review; X4 = no method, theory or result of its own.

| Item | Paper | Choose | PDF |
|---|---|---|---|
| B1 | M17653, Reviving iterative refinement in diffusion-based NER | X1 or X2 | [M17653.pdf](sources/pdfs/fulltext/M17653.pdf) |
| B2 | M18667, The value of binging in streaming serials | X0 or X3 | [M18667.pdf](sources/pdfs/fulltext/M18667.pdf) |
| B3 | M17462, RegJEDI: a joint-embedding diffusion language model for regulatory DNA | X4 or X1 | [M17462.pdf](sources/pdfs/fulltext/M17462.pdf) |

**Inclusion basis (B4-B7):** a = a diffusion model that outputs text or code; b = one unified model
that both understands and generates across text and another modality (image, video, audio, 3D);
ab = both are true.

| Item | Paper | Choose | PDF |
|---|---|---|---|
| B4 | M10840, LEDFlow (entropy-guided flow) | a or ab | [M10840.pdf](sources/pdfs/fulltext/M10840.pdf) |
| B5 | M12859, Bridging semantic reasoning and geometric refinement with diffusion language models | a or ab | [M12859.pdf](sources/pdfs/fulltext/M12859.pdf) |
| B6 | U04330, Privacy-preserving synthetic medical image and report generation | a or ab | [U04330.pdf](sources/pdfs/fulltext/U04330.pdf) |
| B7 | M16043, Making multimodal generation easier: when diffusion models meet LLMs | ab or b | [M16043.pdf](sources/pdfs/fulltext/M16043.pdf) |

**Non-language only (B8-B9):** answer `yes` if none of the paper's reported results is natural-language
text or code (it generates only other strings), else `no`.

| Item | Paper | Choose | PDF |
|---|---|---|---|
| B8 | M11389, Backpropagating verifier rewards through continuous flow language models | yes or no | [M11389.pdf](sources/pdfs/fulltext/M11389.pdf) |
| B9 | M18059, SPMDM: simplifying sampling in masked diffusion models | yes or no | [M18059.pdf](sources/pdfs/fulltext/M18059.pdf) |
