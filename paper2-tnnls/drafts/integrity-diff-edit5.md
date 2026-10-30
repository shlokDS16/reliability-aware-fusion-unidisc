# Integrity diff: pass 5, red-team carried minors A9, A10 and the duplicated "link withheld" clause (clarity-editor, 2026-10-30; baseline a8c59c0c)

Baseline copies: `git show HEAD:` of sections, tables, supplement and main.tex in the session scratchpad `orig5/`. Number table:
`drafts/integrity-diff-edit5-numbers.md`. Nothing committed.

## Result

- Main: 15 pp. Supplement: 17 pp.
- Both build clean: 0 errors, 0 undefined references or citations, 0 overfull boxes over 2 pt, all fonts embedded, 0 column gaps.
- Floats end on p. 12 and the References start on p. 13, so no float follows the References.
- No number, citation key, label or cross-reference was added, removed or changed. No binding sentence and no Declaration sentence was
  touched; the four "NO" rows of the script are the dated edit-3 changes, not changes in this pass. The deviations box still has 18
  items. Symbols and one clause changed:

| Item | Change |
|---|---|
| A9: shared q_j | Study 1 keeps q_j = -u_j (IV-C, Table II). Study 2's feature B_j - D_j is now r_j in Table IV (`tables/tab_features_main.tex`) and in the full feature table (`scripts/tab_features.py`, `tables/tab_features.tex` regenerated: the formulas r_j = B_j - D_j, "their minimum of r", "mean of r", and (r_j - r̄)/(sd(r)+10^-6)). The code names (`q`, `nb3min_q`, ...) stay in the names column; the S-V crosswalk gains a Study 2 row mapping them to r_j. |
| A10: sigma | The logistic function of the weight model is now `sigm` in (13), its definition and the Fig. 4 caption; the crosswalk gains a row for `sigmoid`. The pixel variance in both feature tables changes from τ_j (which clashed with the CRC threshold τ) to v_j, with a crosswalk row. The noise standard deviation σ = 0.1 is unchanged, because it sits in binding sentences. The theory's σ², σ_c² gain one clarifying parenthesis in the Lemma 1 setup paragraph: "(moments of the evidence, not the noise level of Section III-C)". The symbols and statements are unchanged. |
| A10: n | The caption length is now ℓ ("a caption of ℓ text tokens", III-A), so n means only the item count. Other counts keep their subscripts (n_cal, n_d, n_L). |
| Link withheld | The Reproducibility paragraph printed "[link withheld for double-anonymous review]" (the `\anonlink` placeholder) and then the clause "the link is withheld for double-anonymous review". The clause is deleted, so the placeholder states it once. No other place in main or supplement repeats it. The Declaration of Generative AI Use is untouched (D0101). |

## For the coordinator: figure labels (not edited)

`scripts/fig4_study2_weights.py` draws panel titles with the old symbols: `q_j` (line 121, BASE["q"]), `log(1+τ_j)` (BASE["ltex"]) and
the y-axis label "weight w = σ(f(x))" (line 157). They should become r_j, log(1+v_j) and w = sigm(f(x)) so that Fig. 4 matches Table IV
and (13). The text and caption already use the new symbols.

## Checks

The must-not categories are unchanged: no word was added except "moments", "evidence", "noise level" and symbol names. Hidden
characters: not introduced; all edits were ASCII LaTeX.
