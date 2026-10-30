# Abstract skeleton v1 (lead, 2026-10-30; RS-5). Binding sentences with abbreviations spelt out; numbers from runs (comments).

## Variant A: every binding sentence in full (separate scope sentences)

Unified masked diffusion models score how well a caption fits an image from per-token likelihood evidence, but the images they receive can be damaged. We report two separately preregistered studies in one such model. In the first, image tokens that the model finds unlikely with the caption withheld are discarded, with the threshold set by conformal risk control so that the expected flagged share of a clean pair's tokens is at most 0.05. In the preregistered test no improvement was detected under JPEG compression at quality 10, Gaussian noise with standard deviation 0.1 and a 128-pixel splice; for each tested corruption the 90 percent confidence interval of the net accuracy change lay inside plus or minus 0.05 (-0.002, -0.006 to 0.000; 0.000, 0.000 to 0.000; -0.004, -0.010 to 0.002; 500 pairs each), so an improvement larger than 0.05 is excluded and a loss larger than 0.05 is excluded. This does not show that the gate has no effect. This is in one pretrained unified masked diffusion model (UniDisc, 1.4 billion parameters) on COCO image-caption pairs with a random other caption as the negative. In the second, on a fresh preregistered fold, a frozen learned reliability-aware fusion of token evidence raised image-direction verification accuracy under Gaussian noise with standard deviation 0.1 from 0.733 without reliability weighting to 0.802 (net 0.069, 95 percent confidence interval 0.029 to 0.109; exact one-sided McNemar test p = 0.0005; preregistered one-sided level 0.05), including with length-matched negatives. On clean images it lost no more than three points (90 percent confidence interval 0.009 to 0.053); the margin was fixed after an exploratory clean interval had been seen. This is in the same model, on 450 COCO val2017 images not used to design or fit the method, with Gaussian noise at one severity.

## Variant B: shared scope merged once (needs the statistician's dated ruling)

(same as A, with the two scope sentences replaced by one sentence after the second study:)
Both studies use one pretrained unified masked diffusion model (UniDisc, 1.4 billion parameters) and COCO image-caption pairs with a random other caption as the negative; the second used 450 val2017 images not used to design or fit the method, with Gaussian noise at one severity.

## Substitutions (each needs a dated row)
- "This is not 'GATE-M has no effect'" -> "This does not show that the gate has no effect" (abbreviation rule; substance kept).
- "CI" -> "confidence interval"; "sigma 0.1" -> "standard deviation 0.1"; "LRF" -> "learned reliability-aware fusion of token evidence"; "{S}" sentence-initial "This is in ...".
- "1.4B" -> "1.4 billion". JPEG, COCO, McNemar kept as proper names.
