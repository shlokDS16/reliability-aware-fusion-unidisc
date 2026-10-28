# LENS-CRAFT: how Moser et al. build figures, tables and theory

Reference paper: Moser, Shanbhag, Raue, Frolov, Palacio, Dengel, "Diffusion Models, Image Super-Resolution, and Everything: A Survey", IEEE TNNLS 36(7), July 2025.
PDF: `Paper to refer/Diffusion_Models_Image_Super-Resolution_and_Everything_A_Survey.pdf` (2.2 MB).

## How this was done

- All 21 PDF pages were opened as images with the Read tool (pages 1-10, 11-20, 21). Every page rendered. Tables I and IV were re-rendered at 220 dpi to check bold and underline marks. `pdffonts` and `pdfimages -list` were used for fonts and embedded images.
- The text dump `sr-survey.md` was used only to grep (no algorithm boxes, no notation table, no PRISMA, no timeline appear in it, which matches what the page images show).
- Page convention: **p.N is the PDF page number**; journal page = N + 11792 (p.1 = 11793, p.21 = 11813). Pages 1-17 are the article, pp.17-21 are references and author bios.
- Scope facts: 8 figures, 4 tables, 47 numbered equations plus 3 unnumbered display equations (p.6-7), 185 references, no appendix, no supplementary pointer, no algorithm environment. It is a narrative survey: no search protocol, no inclusion counts. It is a craft model for exposition, not for review method.
- Where I say "appears", I am reading a rendered image, not source files.

---

## 1. Figure catalogue

All eight figures are single-column width, placed at the top of a column, caption below, 1 to 5 lines. None spans two columns. There is no plot of data, no timeline, no taxonomy tree, no qualitative grid with zoom insets. Seven of the eight are drawn schematics; two (Fig. 6, Fig. 7) use real photographs.

| Fig | Page (journal) | Type | Single message | How it is built | Caption |
|---|---|---|---|---|---|
| 1 | p.5 (11797) | Unifying schematic | "DDPM, SGM and SDE are three implementations of one forward/backward process between image space and corruption space." | Centre: a horizontal chain of circles z_T ... z_t, z_{t-1} ... z_0 with dashed red arrows (forward, q) below and dashed blue arrows (backward, p) above, each labelled with its kernel. Above the chain, a blue rounded box "backward"; below, a red box "forward". Each box holds three stacked coloured rows (green SDE, purple SGM, orange DDPM) with the actual update equation in each row. Ends of the chain labelled "Corruption Space" and "Image Space". Formula text is small, 3 rows x 2 boxes = 6 equations visible at a glance. | 5 lines. Says what red and blue mean, what the chain does, and that three implementations are shown. |
| 2 | p.7 (11799) | Parallel block diagrams | "GAN, VAE, NF and DM all map LR input to SR output; they differ in where the generative step sits." | Four stacked rows with a bold row title each. Boxes are red (analysis side: Discriminator, Encoder, Forward) or blue (generation side: Generator, Decoder, Backward). Inputs and outputs are small coloured squares: x purple, y green, ŷ light green, latent z yellow. DM row has a "T times" loop on the backward block. Same symbols in every row. | 1 line: "Conceptual overview of generative models (GANs, VAEs, NFs, and DMs)". The text beside it (p.7) carries the explanation. |
| 3 | p.9 (11801) | Taxonomy-as-annotated-schematic (topology of the paper) | "The review is organised along four axes hung on one diffusion chain: conditioning, guidance, state domain, corruption space." | The same z_T ... z_0 chain in a dashed blue rounded rectangle. Four callouts attached by thin arrows: Conditioning (red, attached to the symbol **x** inside p_θ(z_{t-1} \| z_t, x), which is boxed in red) and Guidance (red, double-headed arrow between the two); Corruption Space (purple, attached to z_T, which is circled in purple); State Domain (blue, attached below the chain). Each callout has a bold name, an italic question ("What information guides sampling?") and a short dash list of options. Colour of the callout text equals colour of its anchor. | 5 lines, the longest in the paper. Maps each axis to a section number (V-D, V-B, V-C, V-E), all hyperlinked. |
| 4 | p.10 (11802) | Schematic, three-way comparison | "The same chain can run in pixel, latent or wavelet space; the only change is an encoder/decoder or DWT/IDWT at the ends." | Top: the chain with Enc., Dec., DWT, IDWT arrows to x. Below: three thin full-width coloured bars (green pixel-based, blue latent space, red frequency-based), each labelled left to right "Corruption Space", the diffusion in italics, "Clean image" (or "Latent representation", "Wavelet representation"). | 3 lines, explains which colour is which. |
| 5 | p.11 (11803) | Two-stage pipeline | "DiffuseVAE: a VAE output x̂ becomes the condition for the diffusion model." | Upper blue box "Stage 1: VAE Training" (x, Encoder trapezoid, μ and σ boxes, sum node, Decoder trapezoid, x̂). Lower blue box "Stage 2: Diffusion Training" with the usual chain. A dashed red arrow goes from x̂ to a red dotted box around **x̂** inside the kernel label p_θ(z_{t-1} \| z_t, x̂). | 3 lines, names the two stages and the role of the VAE. |
| 6 | p.12 (11804) | Real-image process comparison | "Standard diffusion ends in noise; I²SB ends in the degraded image." | 2 rows x 3 photographs of one dog image (z_0, z_t, z_T). Row 1 labelled "Standard": z_T is noise. Row 2 labelled "Image-to-Image Schrödinger": z_T is the blurred input. Forward arrows blue and backward arrows red, with labels between columns. Row labels rotated 90 degrees on the left. | 3 lines. States the contrast in one sentence. |
| 7 | p.12 (11804) | Failure example | "Vanilla SR3 shifts colour when trained with a small batch." | Two photographs side by side with bold sans-serif labels "SR3" and "HR". Single example, no zoom inset, no difference map. | 3 lines. Names method, scale (64x64 to 256x256) and the cause (batch size 8 instead of 256). |
| 8 | p.14 (11806) | Equation-mapped flow diagram | "DDNM builds z_{t-1} from the range-space part A†y and the null-space part (I-A†A)z_{0\|t}." | Nodes labelled with the exact symbols of Eqs. (41)-(43): z_t (blue circle), z_{0\|t} and ẑ_{0\|t} (green circles), A†y, (I-A†A)z_{0\|t}, μ_t, σ_tε, z_{t-1}. A faded grey branch shows the term that is dropped. | 2 lines. Names the method and the tasks it covers. |

### Which figures do the most work

1. **Fig. 1 (p.5).** Unifies three formalisms in one picture before any equation is derived. The reader gets the whole of Section III in one glance.
2. **Fig. 3 (p.9).** It is the table of contents for Section V and also the taxonomy of the survey. It ties every axis to the symbol it changes in the chain.
3. **Fig. 2 (p.7).** One-line-per-family comparison with fixed colour roles. Cheap and very readable.
4. **Fig. 8 (p.14).** Makes a three-equation derivation followable; every node is an equation symbol.
5. **Fig. 4 and Fig. 5 (p.10, p.11).** Each isolates a single change to the chain (state domain; condition source).

Figs. 6 and 7 are the weakest as evidence: single photographs, no insets, no metric on the figure. Fig. 7 does carry a real finding because the caption states the training condition that produces it.

### Recurring figure devices

- **Home-base chain.** The glyph z_T ... z_t, z_{t-1} ... z_0 appears in Figs. 1, 3, 4, 5, and as a reduced form in 6 and 8. Each figure changes one thing on it (p.5, p.9, p.10, p.11).
- **Symbol-in-kernel highlight.** The injected quantity is boxed inside the transition label and joined by an arrow to its source (Fig. 3 on p.9, boxed **x**; Fig. 5 on p.11, boxed **x̂**).
- **Question-and-options callouts.** Each taxonomy axis is posed as a question with 2-4 options (Fig. 3, p.9).
- **Caption as map.** Captions state what each colour or part means and which section develops it (Figs. 1, 3, 4).

### Defects to avoid (seen, not inferred)

- Forward/backward colour is **reversed** between Fig. 1 (forward red, backward blue; p.5) and Fig. 6 (forward arrows blue, backward arrows red; p.12). Green means SDE in Fig. 1 (p.5) and pixel space in Fig. 4 (p.10). The palette is consistent inside a figure but not across the paper.
- Figure text appears smaller than caption text in Figs. 1, 3, 5 (p.5, p.9, p.11).
- Figs. 6-7 are small photographs embedded at about 420 px wide (pdfimages), adequate at column width but with no zoom.

---

## 2. Table catalogue

Four tables, all quantitative result copies from other papers. Table numbers are Roman, captions are in small caps centred **above** the table.

| Table | Page | Compares | Columns | Rows and grouping | Missing values | Marking | Citation handling |
|---|---|---|---|---|---|---|---|
| I | p.11 (11803) | 4x SR on DIV2K val, regression vs GAN/flow vs diffusion | Methods, PSNR↑, SSIM↑, LPIPS↓ | Three blocks separated by a horizontal rule: Bicubic + regression (EDSR, FxSR-PD, RRDB, CAR); RankSRGAN, ESRGAN, SRFlow; SRDiff, IDM, DiWa. Grouped by method family, not sorted by metric (within-block order is roughly but not strictly ascending PSNR). | "-" for CAR and IDM LPIPS; no footnote saying why | Only **one** underline (SRFlow LPIPS 0.120, which is second-best); the best value (DiWa 0.104) carries no bold. The caption does not define the marks. | Source [15] in the caption only; no refs in cells. Caption also states the lesson ("regression-based methods generally produce better PSNR and SSIM"). |
| II | p.11 (11803) | CelebA-HQ face SR 16x16 to 128x128 | Methods, PSNR↑, SSIM↑, Consistency↓ (MSE x10^-5) | Two blocks: PULSE, FSRGAN, SR3 (regression) \| SR3 (diffusion), DiWa, IDM. The SR3 regression/diffusion pair sits across the divide, so the paired contrast is visible. | "-" for DiWa and IDM consistency | None | No source cited in caption |
| III | p.12 (11804) | 4x SR on resized DIV2K val, 128 to 512 | Methods, PSNR↑, SSIM↑, LPIPS↓ | Two blocks: GAN-based (BSRGAN, Real-ESRGAN, LDL, FeMaSR, SwinIR-GAN) \| diffusion (LDM, SD Upscaler, StableSR, PASD) | none | None | No source cited in caption. The text points to it ("Comparisons between PASD and other approaches can be found in Table III", p.11) |
| IV | p.14 (11806), two-column width | Zero-shot methods | Two-level header: ImageNet 1K (PSNR, SSIM, LPIPS) and CelebA 1K (PSNR, SSIM, LPIPS) with a vertical rule between datasets, then Time [s/image] and Flops [G] with their own rules | Bicubic as baseline first, then ILVR, SNIPS, DDRM, DPS, DDNM, GDP (no visible sort) | "-" for Bicubic time/flops and SNIPS flops | Caption defines it: **best bold, second-best underlined**; ties are both bold (DDRM and DDNM 31.64 on CelebA PSNR). Marks are applied per column, in all 8 metric columns. | "Values derived from Li et al. [17]" in the caption. Table has vertical rules, which booktabs style avoids. |

Observations on handling:
- Tables I-III use the same three metrics with arrows (↑, ↓) in the header, which tells the reader direction at once. Table IV does the same.
- No confidence intervals, no number of runs, no seed information in any table. A fusion review must do better here (our own rule: intervals included).
- Marking convention is inconsistent across Tables I-III (no bold, one stray underline) versus Table IV (full convention). Pick one convention and define it in every caption.
- Missing values are always a bare hyphen. There is no footnote distinguishing "not reported" from "not applicable".
- Table IV's Flops column is almost constant (1113.75 for five rows, 1113.76 for one); the column adds little. A column with no variation should be dropped or footnoted.
- Tables are small and sit next to the text that interprets them (Tables I-II are cited at the end of the V-D.1 paragraph, p.11). The caption of Table I carries the interpretive sentence so the table can be read alone.

---

## 3. Equations and notation

### Numbering and referencing
- 47 numbered display equations, flush-right numbers in parentheses. No boxed equations, no equation environment titles. Three unnumbered display lines in III-D (p.6-7) restate (18) and (22) in the form needed for the comparison.
- In text, equations are cited as a hyperlinked blue "(18)" without the word "Eq." (e.g. "the optimization target in (22)" p.7; "reformulate (14)" p.9). Sections are cited as "Section V-D" with the number hyperlinked in blue (p.9, Fig. 3 caption).
- Every display equation is followed by a "where ..." sentence defining each symbol (after Eq. 1, 4, 7, 12, 22, 32, 34, 36 and others). Annotated derivation steps use stacked tags (i), (ii), (iii) over the relation sign, and the sentence below says what justifies each tag (Eq. 18 on p.5: "(i) is possible because both terms are products of distributions and (ii) is the product of Jensen's inequality"; Eq. 22 on p.6: "(i) is derived by Vincent [68], (ii) is from (19), (iii) is from z_t = z_0 + σ_t ε").
- Roadmap paragraph on p.2 lists each section in one sentence ("Section III-DMs Basics: ...").

### Order of the theory section (pp.4-7)
1. **p.4 text:** define "forward q" (adds noise, t increases) and "backward p" (removes noise, t decreases) in two numbered bullets, and define z_t, T, p_θ before any equation. Points to Fig. 1.
2. **Fig. 1 (p.5):** all three formalisms visible side by side.
3. **III-A DDPM (p.5):** Eq. 12 one-step kernel, 13 closed form via γ_t = ∏(1-α_i), 14 reparameterised sample, 15 learned reverse kernel, 16-17 joint distributions, 18 KL to variational bound.
4. **III-B SGM (p.5-6):** Eq. 19 forward, 20-21 Langevin sampling steps, 22 denoising score matching with a three-step chain of equalities.
5. **III-C SDE (p.6):** Eq. 23 general forward SDE; 24 and 25 as the DDPM and SGM special cases; 26 reverse-time SDE; 27 probability-flow ODE; 28 continuous score-matching loss.
6. **III-D Relation between DMs (p.6-7):** reweight the DDPM loss with λ(t) and compare with (22); setting ε_θ(z_t,t) = -σ_t s_θ(z_t,t) makes the two objectives identical up to a constant. This is the short proof that closes the unification.
7. **III-E Relation to GAN, VAE, ARM, NF (p.7):** prose plus Fig. 2, no new equations.
Each of III-A, III-B, III-C uses the same three run-in headings: **1) Forward Diffusion, 2) Backward Diffusion, 3) Optimization**. This lets a reader compare the formalisms by flipping between subsections.

### How different formalisms are unified in one notation
- **One state symbol.** z_t (bold) is used for DDPM, SGM and SDE alike. The same chain glyph appears in Fig. 1 with the three update rules written in that notation (p.5).
- **One conditioning symbol.** x (bold) is always the conditioning input (the LR image); the conditional versions are obtained by adding "x" to the arguments: p_θ(z_{t-1} \| z_t, x), s_θ(z_t, x, t) (p.6, p.9). Eq. 32-33 add guidance in the same ∇ log q notation.
- **SDE as the parent.** Eq. 23 is the single general form; 24 and 25 give the DDPM and SGM drift and diffusion functions, with the sentence "This generalized formulation allows uniform representation of both DDPMs and SGMs" (p.6). Discretisation relations are given as "α((t/T)) = Tα_t for T→∞" and "σ((t/T)) = σ_t for T→∞".
- **Same loss form.** (18), (22) and (28) are placed so that the "E over t, z_0, z_t of a λ(t)-weighted squared norm" structure is visible, then III-D equates them (p.6-7).
- **Unification extended to methods (Section VI).** Eq. 35-36 give one projection-based update with f and g "depending on the type of DM"; Eq. 37-40 decompose zero-shot SR as x = Ay + b; Eq. 44-47 show DPS, MCG and GDP as approximations of the same posterior (p.13-15). Section VI is a good example of a family of methods compared through shared equations.
- **Unification across families (Fig. 2, p.7).** GAN, VAE, NF and DM are drawn with the same x, y, ŷ, z symbols.

### Weaknesses to avoid (all read off the pages)
- **Symbol overload.** α_t is a noise variance in Eq. 12 (p.5, "0 < α_{1:T} < 1 represent the variance") but its complement in Eq. 31 (p.9) and Eq. 43 (p.14: "α_t = 1-β_t and ᾱ_t = ∏ α_i"). γ_t (Eq. 13) and ᾱ_t (Eq. 43) denote the same cumulative product under two names. α_t also names the Langevin step size (p.6) and α(t) the SDE function (Eq. 24).
- **Roles of y and z_0.** y is HR in Eq. 1 (p.2) and in Eq. 37-40 (p.13) but z_0 is the HR image in Section III-V. The paper says so in the text, but a notation table would have saved the reader.
- **No notation table, no algorithm boxes.** None appears in the 21 pages.
- **Single-sentence derivation gaps.** Eq. 12-14 jump from the one-step kernel to the closed form with one sentence (p.5). Our review can add a one-line justification.

---

## 4. Visual identity

- **Body font:** NimbusRomNo9L (Times-like) at the IEEE two-column size; math in MathTime/CM-style fonts (BLEX, RMTMI, CMSY, MSBM per `pdffonts`). Bold upright z, x, y for vectors; calligraphic D, M, L; blackboard E and N for expectation and Gaussian. Page header in small sans, two-column body.
- **Headings:** section titles centred small caps with Roman numerals ("I. INTRODUCTION"); subsection titles italic ("A. Datasets"); paragraph run-ins are italic with "1)" numbering (e.g. "1) Forward Diffusion:"). Table captions in small caps; figure captions in regular roman below.
- **Figure typography:** sans-serif (Helvetica/Arial look) in drawings; equations in figures in the same math font as the text, so symbols match. Bold labels for row titles (Fig. 2, p.7) and rotated labels for rows (Fig. 6, p.12).
- **Palette:** flat pastel fills with a darker outline of the same hue: light blue, light red/pink, light green, lavender, light orange/yellow, plus black arrows. It looks like the default diagrams.net palette. Colour is semantic inside each figure (red/blue = analysis/generation in Fig. 2; green/blue/red = pixel/latent/frequency in Fig. 4) but is reused for different meanings across figures (see the Defects list in section 1).
- **Colour in text:** only hyperlinks are coloured (blue) for citations, equations, sections, figures and tables. Tables are black and white.
- **Icons:** none. Trapezoids for encoder/decoder and circled plus signs follow the standard VAE drawing convention (Fig. 2, Fig. 5).
- **Whitespace:** figures are flush to the column top with a small gap to the caption; no figure is wider than a column except Table IV. Equation blocks have generous vertical space; page 4-6 are equation-dense but still have 1-2 lines of prose between displays.
- **Imagery:** natural photographs only in Figs. 6-7. Author portraits on the last page (p.21) as is the IEEE style.
- **Density:** roughly one figure or table per page on average (8 figures + 4 tables over 17 body pages), most of them small. The text between figures is dense and long (a method per sentence), which is the main readability cost; there is no summary table of methods.

---

## 5. Ten transferable craft rules

1. **Open the theory section with a one-glance unification figure.** Fig. 1 (p.5) puts DDPM, SGM and SDE side by side as three rows of equations on one chain, before any derivation. For our review, draw the same for discrete masked, uniform and continuous-embedding diffusion; for GATE, draw the baseline and gated sampler as two rows on one chain.
2. **Give every formalism the same three run-in headings.** "1) Forward Diffusion / 2) Backward Diffusion / 3) Optimization" repeated in III-A, B, C (p.5-6) lets readers compare by flipping. Use one fixed skeleton per family in the review (corruption, reverse, objective) and per method in the GATE paper.
3. **Close a unification with a short, explicit equivalence.** III-D (p.6-7) ends with ε_θ = -σ_t s_θ and says "there is a mathematical connection". State each equivalence in one line, including the condition under which it holds, and place it directly after the two formulations it joins.
4. **Reuse one "home-base" glyph for the whole paper.** The chain z_T ... z_0 recurs in Figs. 1, 3, 4, 5 (p.5, 9, 10, 11) with exactly one change per figure. Choose one canonical GATE pipeline figure and alter only the element under discussion in later figures.
5. **Highlight the injected symbol inside the kernel and arrow it to its source.** Fig. 3 (p.9) and Fig. 5 (p.11) box x or x̂ in p_θ(z_{t-1} \| z_t, ·). For GATE, box the reliability gate r in the denoiser's argument list and draw an arrow from the module that computes it.
6. **Make the taxonomy figure a map of the paper, not a decoration.** Fig. 3 (p.9) pairs each axis with a question and its options, anchors each to a symbol, and its caption maps each to a section number. Our review's design-space figure should name every axis as a question, list the options, and cite the section.
7. **Write the caption so the figure can be read alone.** Fig. 7 (p.12) gives method, resolution and training condition in 3 lines; Fig. 1 (p.5) defines the colours; Table I (p.11) carries its own take-away sentence. Every caption in our papers should state what is shown, what the colours mean, and the one finding.
8. **Define one marking convention and apply it to every table.** Table IV (p.14) defines "best bold, second-best underlined" and applies it to every column, with ties both bold, whereas Tables I-III (p.11-12) do not apply it and the sole underline in Table I is unexplained. Define the convention in the caption of every table, add intervals (the reference has none), and use booktabs rules without vertical lines.
9. **Group table rows by family with a rule and put the controlled pair across the divide.** Tables I-III (p.11-12) separate regression, GAN/flow and diffusion rows, and Table II puts SR3 (regression) next to SR3 (diffusion). Group our rows by decoding family and include the matched ablation row directly beside its parent method. Flag copied numbers with "Values derived from [ref]" in the caption (Table IV, p.14) and say what "-" means in a footnote (the reference does not).
10. **Fix notation once and avoid reusing a symbol for two quantities.** The reference unifies on z_t and x (p.5-9) but reuses α_t with opposite meanings (Eq. 12 p.5 against Eq. 31 p.9 and Eq. 43 p.14) and names the cumulative product γ_t in one place and ᾱ_t in another. Put a notation table in the paper (the reference has none), choose one convention for the noise/mask schedule, and keep the colour code (forward, backward, text, image) identical across all figures, which the reference does not (Fig. 1 against Fig. 6).

Additional smaller points (from the same pages): cite equations as a hyperlinked "(n)" and sections as "Section V-D"; follow every display with a "where" sentence; annotate multi-step derivations with (i), (ii), (iii) and explain each tag (p.5, p.6); give a roadmap paragraph per section on p.2; end the paper with a Discussion section whose subsections mirror and point back to earlier sections (p.16-17, "As discussed in Section V-F").

---

## Limits of this lens

- It reads typography and layout from rendered images; exact font sizes and hex colours were not measured.
- The paper's evidence content (numbers in Tables I-IV) was not checked against the sources it copies from; only the layout and marking were inspected.
- It is a narrative survey; nothing here informs the PRISMA conduct or reporting of Paper 1.
