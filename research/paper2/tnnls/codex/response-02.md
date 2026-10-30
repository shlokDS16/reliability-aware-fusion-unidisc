## 1. Summary and recommendation

The manuscript reports two separately preregistered studies of image-text verification with UniDisc: a masked-likelihood token gate whose preregistered result is a bounded null, and a frozen learned token weighting that improves accuracy under Gaussian noise on a fresh fold. The methods, provenance, and limits are documented unusually candidly, but the paper offers narrow evidence from one model and one dataset; the second study’s method was designed after extensive analysis of the first study’s items, and its tested noise condition was also used in training. **Recommendation: reject, confidence 0.8.** The main concern is contribution and external validity, rather than an obvious failure of the reported primary statistics.

## 2. Seven most serious weaknesses, ranked

1. **The evidence is too narrow for the breadth implied by a TNNLS methods paper.** Both studies use one pretrained model and COCO; Study 1 uses random-caption negatives, while its hard-negative family did not run. Study 2’s positive confirmation is for one noise severity.  
   **Honest fix:** Make the scope limitation prominent in the abstract and conclusion; frame this as a bounded measurement on one model and benchmark.

2. **The paper’s two studies do not yet add up to a coherent contribution.** One is a negative test of input-token gating; the other is a positive test of a learned weighting. The shared setting connects them, but the method and outcomes differ, and the binding rules properly prohibit treating one as the explanation for the other.  
   **Honest fix:** State the two questions independently in the introduction, and present the paper as two measurements of UniDisc’s evidence rather than a unified method story.

3. **Study 2 confirms a frozen choice on new images, but not a general reliability principle.** Its method was selected after seeing Study 1’s primary and secondary results, its positive-control audit, comparators, and a learned-weighting analysis on Study 1 items. The new fold supports the frozen object’s result there, not a general claim that learned token reliability weighting works.  
   **Honest fix:** Keep the provenance disclosure adjacent to the confirmation claim, and use “confirmation” only for the preregistered L1 result.

4. **The “under Gaussian noise” result is not a held-out-corruption test.** Gaussian noise at σ=0.1 was among the training conditions for the weights. The new fold tests fresh images, not whether the method transfers to an unseen corruption.  
   **Honest fix:** Say “fresh images under the Gaussian-noise condition used in fitting” wherever space permits; retain the limitation that no preregistered test isolates corruption-specific from generic gains.

5. **The reference-encoder table is not a comparison, and the paper cannot establish practical advantage.** The manuscript says CLIP and SigLIP are “for reference” and nearly at ceiling; it correctly avoids a formal comparison. As a result, the reader cannot judge whether the learned weighting is useful relative to existing verifiers.  
   **Honest fix:** Keep the table explicitly descriptive, and state clearly that the paper makes no claim of verifier competitiveness.

6. **The “reliability-aware” name risks being read as an empirical finding.** The method’s weights are not shown to track token reliability or corruption, and the manuscript itself says that is unclaimed.  
   **Honest fix:** Define the term once as a design name and avoid calling the learned weights reliable, adaptive to corruption, or interpretable as reliability elsewhere.

7. **Study 1’s guarantee is easy to overread.** It bounds the expected flagged-token share for an exchangeable clean test pair. It says nothing about detection power, false flags among unchanged tokens in corrupted inputs, or shifted captions.  
   **Honest fix:** Put this scope directly beside each substantive description of conformal risk control; avoid using “calibrated” as a selling point.

## 3. Factual, statistical, or logical errors

I found **no confirmed arithmetic or p-value error** in the primary results as reported. In particular, the L1 discordance counts support the stated net change: \((58-27)/450 \approx 0.069\), and the manuscript correctly reports the impulse-noise two-sided p-value of 0.058 without making a two-sided rejection claim.

I do see several statements that need tighter interpretation:

- **“This is on 450 validation-split images not used to design or fit the method”** (abstract). The images were not used to design or fit the *frozen method*, but the method was designed after analyses of Study 1’s items and results. The nearby provenance statement clarifies this, but this wording on its own can suggest a more independent method-development process.  
  **Fix:** “On 450 fresh images not used to fit the frozen weighting…”

- **“On clean images it lost no more than three points”** (abstract and results). This is the preregistered non-inferiority interpretation of a 90% interval whose lower bound is above −0.03; the observed interval is actually positive, and the margin was fixed after an exploratory interval was seen. The manuscript discloses both facts, but the short wording reads like a general clean-image guarantee.  
  **Fix:** “It met the preregistered −0.03 non-inferiority criterion on clean images; the margin was fixed after an exploratory interval had been seen.”

- **“The clean-image estimate was positive … superiority on clean images was not a preregistered hypothesis.”** This is transparent, but placing the positive estimate in the results narrative invites a superiority reading despite the caveat.  
  **Fix:** Keep the estimate in the table and describe it as descriptive, or retain the sentence with “descriptive” immediately before the estimate.

- **“The best cheap rival … is the pixel variance …”** and **“q lies below it …”** (Study 1 detection). The manuscript says the rival and its sign were chosen on the same items. This is not a clean out-of-sample comparison; the text does disclose selection and later reports a frozen-rival test. Readers may still confuse the same-item comparison with confirmatory evidence.  
  **Fix:** Call this explicitly a same-item selection result and lead with the frozen-rival S-D2 comparison.

- **“On noise it is below the one-pass TbV score … the marginal intervals do not overlap”** (Study 1 detection). The manuscript correctly says no paired test was run. Non-overlap of marginal confidence intervals is not itself the paired test specified for a difference.  
  **Fix:** Say “the marginal intervals do not overlap; this was descriptive, and no paired test was run,” without implying a formal comparison.

These are wording/interpretation risks, not evidence that the reported primary estimates are wrong.

## 4. Ten passages likely to slow or mislead readers, with rewrites

1. **“Unified masked diffusion models verify captions against images, but received images may be damaged; we report two separately preregistered studies…”**  
   *Rewrite:* “We report two preregistered studies of image-text verification with UniDisc under image corruption.”

2. **“When the score is the model’s own likelihood of its input, the behaviour of that evidence is a property of the scorer itself, not of an attached encoder.”**  
   *Rewrite:* “We study evidence computed by the unified model itself, without an external image encoder.”

3. **“The same network can judge its own inputs…”**  
   *Rewrite:* “With image tokens masked and a caption visible, the model assigns probabilities to the observed image codes; these probabilities define the image-direction score.”

4. **“The one-sided form of (3) is used where a plan states a direction in advance, and the two-sided form otherwise…”**  
   *Rewrite:* “We use one-sided McNemar tests only for hypotheses with a preregistered direction; all other tests are two-sided.”

5. **“This is the only guarantee in the paper…”**  
   *Rewrite:* “The guarantee applies only to the expected fraction of tokens flagged in an exchangeable clean test pair.”

6. **“A model of when withholding helps an additive statistic…”**  
   *Rewrite:* “Under the assumptions below, we derive a condition under which withholding tokens increases the signal-to-noise ratio of the remaining evidence.”

7. **“A first freeze was found to read the true caption’s length through the layout of its inputs…”**  
   *Rewrite:* “The initial frozen model inadvertently used a feature that revealed caption length. We fixed the caption slot, then rescored and refroze the model before selecting Study 2’s test images.”

8. **“The configuration selected by successive halving on three inner folds … was refitted on all 500 items…”**  
   *Rewrite:* “We selected the configuration by successive halving and three-fold inner validation on the 500 design images, then refit it on all 500.”

9. **“Five inexpensive alternative readings remain open…”**  
   *Rewrite:* Replace the long sentence with a numbered list of the five alternatives, each paired with the evidence that bears on it.

10. **“The reference encoders almost solve this matching task…”**  
    *Rewrite:* “CLIP and SigLIP had accuracies near ceiling on these items. Because no statistical comparison was planned or made, these results are descriptive only.”

## 5. Overclaiming and study links

The paper mostly obeys its separation rules. It states the required Study 2 chronology in its provenance section, labels Study 1’s Tier-3 and hard-negative results separately, and does not place GATE and LRF results together in a comparison table.

The main overclaim risk is the title’s **“Raised Image-Text Verification Accuracy Under Gaussian Noise”**: it is supported for the reported fresh fold, but the weighting was trained with that noise condition, so it should not be read as transfer to unseen corruption. The title’s **“Preregistered Confirmation”** should likewise be understood as confirmation of L1 for the frozen model on fresh images, not independent validation of a general method.

A second risk is the repeated shorthand **“lost no more than three points”** for clean images. The limitation and methods disclose that the margin was fixed after an exploratory interval; keep that caveat attached to the claim. Finally, “reliability-aware” is acceptable as the method’s name under the specification, but prose should not imply the weights have been shown to measure reliability.
