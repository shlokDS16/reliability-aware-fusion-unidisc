# Red team: Mask-DiFuser presentation pass (HEAD 175efa89), 2026-10-31

Agent: red-team (Sonnet). Saved by the lead from the agent's returned text (the agent's harness barred writing .md files).
Verdict: **DO NOT SIGN as built**. One fatal finding (F1). Majors F2-F4 must be cleared with it. With F1-F7 fixed or ruled in the
ledger, the verdict becomes SIGN WITH CONDITIONS.
Hostile area chair: unchanged at 4/10 (confidence 4/5). The pass raised clarity but sharpened the novelty weakness (W3): a refitted
linear logit is at or above LRF in 3 of 4 columns.

## Verified clean
- Binding sentences and verdict words are unchanged.
- Table IV values match their run files.
- The exploratory plan was committed before the computations (83ac79f8, then E2, then E4).
- The qualitative figure's selection rule is correct, and the figure includes an LRF error.
- Algorithm 1 constants match `spec.json`.
- No "significantly" or superiority words.
- Anonymity holds, and AI is mentioned only in the Acknowledgment.
- No figure or table holds Study 1 and Study 2 numbers together.

## Findings (severity; fix)
- **F1 (fatal):** the M1 rival's sign and AUROC with CI left the main text, which A4.2.2 item 2 requires. Fix: restore one compact
  main-text element (a sentence or 4-row table) with the rival AUROCs, CIs and the paired difference, from `runs/P2-GATE-M1/analysis.json`.
- **F2 (major):** Study 1 objects sit inside Study 2's Table IV and Section V-H (TM-G defined by the gate's flag count, "gate"
  clauses, the hard-gate arm sentence, the CLIP/SigLIP pointer, the S-DN naming). This breaks A6.12, SPEC rule 3, C6-4, V2-2(b)
  and A6.6. Fix: delete the TM-G row and the gate clauses; define MED/TM20 and the denoiser by formula only; delete the
  CLIP/Table III pointer.
- **F3 (major):** the bold/underline ranking in Table IV clashes with SPEC section 5 and the paper's own bold = "rejected"
  convention. Fix: remove bold/underline and the "highest" sentences, or a lead ruling plus a different mark (e.g. italics).
- **F4 (major):** the overrides are not in the ledger (Prop. 2 / Fig. 3 / Fig. 5 move, the marks, the Tier-3 rows). Fix: dated
  decision rows, a SPEC v2.3 note, and a gate-auditor verdict.
- **F5 (major):** Table IV shows 4 of the 10 learned refits, chosen after scoring, with no stated rule. Fix: show all, or say
  "5 of 10 shown, chosen after the fold was scored; all in supplement S-VII".
- **F6 (major):** A-LIN is at or above LRF in 3 of 4 columns (clean 0.920 vs 0.918); its interval vs NONE excludes zero in all
  four conditions, including JPEG [0.007, 0.064], where LRF's L3 detected no difference. "Similar range" is loose. Fix: a VI-C
  sentence naming this; delete "similar range".
- **F7 (major, blocks submission):** the DN rows print "pending". Fix:
  - fill them after the run, with a result-agnostic sentence;
  - in the caption, state that LRF was not trained on denoised images;
  - if DN+NONE is at or above 0.802 under noise, add a sixth alternative reading in VI-B;
  - keep the paper at 15 pages;
  - note that `env-lock.txt` is empty (deviations item 9).
- **F8 (major, process):** the DOCX, Word PDFs and submission package predate the pass. `fig4` PNGs are uncommitted. Fix: rebuild and
  re-scan after the fixes.
- **F9 (major, author-owned):** the Acknowledgment says AI was used only "to improve the language and grammar", which understates the
  use (figures, Algorithm 1, Table IV, scripts and prose were agent-made). The authors and supervisor must settle the text before
  submission.
- **F10 (major):** COCO image attribution is generic. Fix: record each image's licence and Flickr URL, credit them in the caption
  or S-VIII, and cite [57].
  - The lead's check on 2026-10-31: 335177 is CC BY-NC-SA, 520324 is CC BY-SA and 224724 is CC BY-NC.
  - None is NoDerivs, so the figure may stay.
- **F11 (minor):** Algorithm 1 computes cross-token features inside a per-token loop, does not say which caption is chosen, and
  leaves the knots undefined. Fix: add a first step for item-level aggregates and the caption-masked scores, then state the
  true/wrong ordering.
- **F12 (minor):** internal code names (A-UNL, A-SF, A-LIN, A-S-BD, A-MIL) are back in the main text. Fix: plain names.
- **F13 (minor):** Lemma 1's proof is now only a pointer, and contribution 1 claims a result that lives in the supplement. Fix: a
  two-line derivation, or reword "stated and proved in the supplement".
- **F14 (minor):** in the qualitative paragraph:
  - the 62 both-wrong items are not stated;
  - "three of these items" is wrong (kind i is concordant);
  - "fixed beforehand" overstates the timing (the rule was set after the confirmatory result);
  - the deviations box does not list the figure.
  Fix: wording, and add the figure to deviations item (9).
- **F15 (minor):** the committed `runs/P2-PAPER-FIGS/fig4_meta.json` was edited in place. Fix: restore it and write a new meta file.

## Hostile area-chair notes
- Under noise, LRF's weights are nearly a hard selection of about 1% of tokens: the mean weight is 0.011 against 0.18 clean (item 0).
- The analyses fork along many paths on one fold.
- W1 and W2 are unchanged.
- A "pending" table at the page cap looks unfinished.
- The theory in the main text is now one lemma with a pointer proof.

## Order to clear
F1, F2, F3 with the F4 rulings, then F5/F6, then F7 (after DN), then the F8 rebuild. F9 and F10 are the authors'.
