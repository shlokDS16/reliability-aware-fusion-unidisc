```yaml
agent: language-expert (clarity-editor role, research-humanizer toolkit, academic register)
date: 2026-10-30
brief: Independent IEEE Transactions copy-edit of Paper 2 (TNNLS) main paper and supplement; apply safe items, list the rest
sources_examined:
  - paper2-tnnls/main.tex
  - paper2-tnnls/sections/{abstract,introduction,related,setting,study1,study2,discussion,conclusion,declaration}.tex
  - paper2-tnnls/supplement/supplement.tex
  - paper2-tnnls/tables/{tab_families_glance,tab2_study2,tab3_baselines}.tex (read only; generated, not edited)
  - paper2-tnnls/SPEC.md v2.2 (rules 0-11), research/CONTRACT.md, drafts/integrity-diff-edit1.py (binding list)
coverage: every prose line of the main paper and supplement, all captions and table notes in the .tex sources. Not covered:
  generated table bodies (tables/*.tex, only spot-read), the .bib, the DOCX, appendix.tex (not input).
claims:
  - statement: The edit changed no number, \cite key, \label/\ref key or mathematical expression in main or supplement.
    status: supported
    evidence: paper2-tnnls/drafts/integrity-diff-language.md (script drafts/integrity-diff-language.py)
    level: E4
    confidence: 0.97
  - statement: Every edit inside a binding sentence is typography (serial comma, closed-up percent sign).
    status: supported
    evidence: same file, "Binding regions" table and "Every edit inside a binding region"
    level: E4
    confidence: 0.9
  - statement: Main paper builds clean at 15 pages; supplement at 18 pages; no float above the title.
    status: supported
    evidence: bash build.sh output; pdftoppm -r 45 pages 1-2 inspected
    level: E4
    confidence: 0.95
competing_explanations: []
unknowns:
  - Whether the authors intended British "no serial comma" as a house choice; the brief's IEEE rule was applied.
next_test: {hypothesis: n/a, intervention: authors resolve the (b) list, primary_metric: n/a, falsifier: n/a, gpu_hours: 0}
```

# Paper 2 (IEEE TNNLS): language evaluation and copy-edit

## 1. Overall grade

**B (good; publishable after a moderate copy-edit).** On an IEEE Transactions copy-edit scale (A = print as is,
B = routine copy-edit, C = substantive language revision, D = rewrite), the manuscript is grammatically sound, precise and
calibrated: hedges match the evidence, negative results are stated plainly, terminology is stable (one term per concept
holds for "image-direction evidence", "unweighted rule", "fresh fold", "net accuracy change"), British spelling is
consistent, and there are no contractions or AI-register tics. What keeps it from an A:

1. **Density.** Many sentences carry three or four qualifications joined by semicolons; about 30 exceed 45 words, several of
   them binding sentences (contribution bullets 1 and 2, the time-input sentence, the A4 disclosure). A referee will read
   them twice.
2. **Internal project vocabulary in reader-facing text**: "network rows", "gatekept", "pins", "card", "the lead", "edit 6",
   "fixed time inequality", "SAP". Most are explained in the supplement; a few are never defined.
3. **IEEE mechanics** that were systematically off: no serial comma anywhere (IEEE requires it), percent sign spaced in
   prose but closed up in tables, supplement subsection headings in sentence case, several undefined abbreviations (TbV, MIL,
   PSNR, KKT, SAP), two sentences starting with a numeral.
4. **Ambiguities in binding sentences** that only the authors may fix (the negative-caption definition, "three points",
   "This is in/on ...").

## 2. Method

research-humanizer workflow: originals copied to the session scratchpad before the first edit; protected-content inventory
(numbers, citations, labels, references, mathematics) frozen by script; four passes (argument, structure, sentence, surface);
mechanical checks for US spellings (one: "toward"), contractions (none), serial-comma sites (script plus a reading of every
list), undefined abbreviations, sentence-initial numerals, hyphen ranges (none in prose; prose uses "X to Y" throughout and
tables use en dashes, both acceptable in IEEE style, and binding sentences use "to", so no change). Binding sentences were
identified from SPEC rule 2 and the binding list of `drafts/integrity-diff-edit1.py`; inside them only typography was changed.
Generated tables were not edited (a script would overwrite them).

Totals: **139 numbered issues found: 105 type (a), applied (about 240 individual edits); 34 type (b), left for the authors.**
Locations are file:line in the revised files (line numbers of the supplement did not change).

## 3. Type (a): applied (no change of meaning)

### 3.1 Abstract and Introduction

| # | Location | Original | Correction | Issue |
|---|---|---|---|---|
| A1 | abstract.tex:16 | standard deviation 0.1 and a 128-pixel splice | 0.1, and a 128-pixel splice | serial comma (binding; typography) |
| A2 | introduction.tex:32 | the authors of UniDisc show, as examples, the repair of damaged image-caption pairs by masking, re-infilling and selection by the model's own likelihood | the authors of UniDisc give examples in which damaged image-caption pairs are repaired by masking, re-infilling, and selection by the model's own likelihood | awkward "show, as examples, the repair"; serial comma |
| A3 | introduction.tex:34 | evidence that the unified model computes itself | evidence that the unified model itself computes | ambiguity ("computes itself") |
| A4 | introduction.tex:36 | compression, sensor noise or editing | compression, sensor noise, or editing | serial comma |
| A5 | introduction.tex:43 | were each preregistered (...), with their own plan, test images and decision rule | were preregistered separately (...), each with its own plan, test images, and decision rule | agreement ("each ... their"); serial comma |
| A6 | introduction.tex:48 | compression, Gaussian noise and a pixel splice? | Gaussian noise, and a pixel splice? | serial comma |
| A7 | introduction.tex:64 | (exact McNemar, Holm over three realistic corruptions, $n$ fixed by a headroom rule) | (..., and $n$ fixed by a headroom rule) | list without conjunction |
| A8 | introduction.tex:67 | Gaussian noise with $\sigma=0.1$ and a 128-pixel splice | $\sigma=0.1$, and a 128-pixel splice | serial comma (binding NEG; typography) |
| A9 | introduction.tex:83 | images, frozen and pinned by SHA-256 | images, frozen, and pinned by SHA-256 | serial comma |
| A10 | introduction.tex:94 | every deviation and the full outputs ...; supplement S-I, S-II and S-IV | every deviation, and ...; S-I, S-II, and S-IV | serial comma (2) |
| A11 | introduction.tex:102 | data set, severity or kind | severity, or kind | serial comma |

### 3.2 Related Work and Shared Setting

| # | Location | Original | Correction | Issue |
|---|---|---|---|---|
| A12 | related.tex:15 | also with few labels | including with few labels | dangling "also" |
| A13 | related.tex:19 | The evidence of this paper | The evidence used in this paper | word choice |
| A14 | related.tex:33 | learned quality scores or critics | learned quality scores, or critics | serial comma |
| A15 | related.tex:34 | models (line break) \cite{...} | models~\cite{...} | citation could break from its word |
| A16 | related.tex:36 | is thinner | is scarcer | register |
| A17 | related.tex:41 | the classical combination weights each source | the classical combination rule weights each source | missing head noun (misreads as noun "weights") |
| A18 | related.tex:44 | ...static weighting~\cite{}, and a recent survey organises ... imbalanced and quality-varying | ...static weighting~\cite{}. A recent survey organises ... imbalanced, and quality-varying | 50-word sentence split; serial comma |
| A19 | related.tex:49-52 | four clauses after the colon joined by commas; "pseudo labels" | clauses separated by semicolons; "pseudo-labels" | list of clauses with internal commas; hyphenation |
| A20 | related.tex:57 | loss~\cite{ilse2018attention} and reliability weights | loss~\cite{ilse2018attention}, and reliability weights | serial comma |
| A21 | related.tex:64 | it did not read full texts | the search did not cover full texts | a search does not "read"; antecedent |
| A22 | setting.tex:26 | $c^+$ for the true caption and $c^-$ | $c^+$ for the true caption, and $c^-$ | serial comma |
| A23 | setting.tex:56 | the donor image and the splice location | the donor image, and the splice location | serial comma |
| A24 | setting.tex:61 | fresh in a fixed sense | fresh in a defined sense | ambiguity ("fixed" also means repaired/held constant) |
| A25 | setting.tex:62 | calibrate, fit or design | calibrate, fit, or design | serial comma |
| A26 | setting.tex:63 | excludes the union of every image used anywhere in the project, together with every image of the SugarCrepe release | excludes every image used anywhere in the project and every image of the SugarCrepe release | "union of every image" is ill-formed; redundancy |
| A27 | setting.tex:65 | \subsection{Tests, Multiplicity and Preregistration} | Tests, Multiplicity, and Preregistration | serial comma in heading |
| A28 | setting.tex:75 | Within a family of hypotheses the familywise level 0.05 is held by Holm's ... | Within a family of hypotheses, the familywise error rate is held at 0.05 by Holm's ... | a level is not "held"; standard term |
| A29 | setting.tex:98-99 | plans, pins and their amendments; the hash checks and the data checks | pins, and; checks, and | serial comma (2) |

### 3.3 Study 1

| # | Location | Original | Correction | Issue |
|---|---|---|---|---|
| A30 | study1.tex:82 | masking $G$ marginalises it | masking $G$ marginalises those tokens out | unclear antecedent of "it" |
| A31 | study1.tex:89 | with the model, caption masked, and keeps | with the model, with the caption masked, and keeps | absolute construction read as list item |
| A32 | study1.tex:185 | 1, 4 and 16 ... toward the diagonal | 1, 4, and 16 ... towards the diagonal | serial comma; British spelling |
| A33 | study1.tex:191 | with its addenda and a method specification; amendments and the protocol details | addenda, and; amendments, and | serial comma (2) |
| A34 | study1.tex:197 | asks for it) and the 200 items | asks for it), and the 200 items | serial comma |
| A35 | study1.tex:215 | a pixel denoiser and GATE-M on clean images | a pixel denoiser, and GATE-M | serial comma |
| A36 | study1.tex:218 | (TbV score~\cite{jhingran2026trustverify}) | (the TbV score, named after Trust but Verify~\cite{jhingran2026trustverify}) | abbreviation never expanded |
| A37 | study1.tex:222-223 | with Holm correction over three at familywise level 0.05 | over the three hypotheses at familywise level 0.05 | elliptical "over three" |
| A38 | study1.tex:230 | (sizes, tests and wording rules | (sizes, tests, and wording rules | serial comma |
| A39 | study1.tex:244-245 | $\sigma=0.10$ or a $128$-pixel splice; under noise and $-0.004$ | $\sigma=0.10$, or a ...; under noise, and $-0.004$ | serial comma (binding NEG; typography) |
| A40 | study1.tex:255 | Holm-level intervals and the exact bounds | intervals, and the exact bounds | serial comma |
| A41 | study1.tex:271 | evidence of violation of | evidence of a violation of | article |
| A42 | study1.tex:288-290 | The plan's audit (...) passed the unit tests ...; it found no defect, and since it cannot see ..., it is not read ... (60 words) | ... ran the unit tests ...; it found no defect. Because it cannot see ..., it is not read ... | an audit does not "pass" tests; sentence split |
| A43 | study1.tex:325 | The mechanism test tested no hypothesis and the second-model family was not run | No hypothesis of the mechanism test was tested, and the second-model family was not run | "test tested"; comma before independent clause |
| A44 | study1.tex:328 | (including E-pred) and the denoiser's | (including E-pred), and the denoiser's | serial comma |
| A45 | study1.tex:342 | from FOIL-COCO~\cite{}, clean images whose negative caption differs ..., so it is not a corruption test | from FOIL-COCO~\cite{}: clean images whose ..., so the family is not a corruption test | false apposition (pairs = images); "it" ambiguous |
| A46 | study1.tex:355 | (disclosure, caveats and decision record | caveats, and | serial comma |
| A47 | study1.tex:367-369 | 0.023, 0.014 and 0.017; comparator and limit | 0.014, and; comparator, and | serial comma (2) |

### 3.4 Study 2

| # | Location | Original | Correction | Issue |
|---|---|---|---|---|
| A48 | study2.tex:18, 20, 25 | comparators and an exploratory; perceptron and a grid model; family~B and the code | comparators,; perceptron,; family~B, | serial comma (3; binding A6.13, typography) |
| A49 | study2.tex:41 | a patch texture and a codebook-neighbour distance | a patch texture, and | serial comma |
| A50 | study2.tex:43 | the corruption labels or the identity | labels, or the identity | serial comma |
| A51 | study2.tex:65 | positive when the true caption wins | positive when the true caption is chosen | informal; matches decision wording |
| A52 | study2.tex:72 | deviation 0.1 and with a 128-pixel splice | 0.1, and with | serial comma |
| A53 | study2.tex:87 | a caption or the identity (Fig. 6 caption) | a caption, or the identity | serial comma |
| A54 | study2.tex:98 | Discordant Counts, $p$-Values and Decisions | $p$-Values, and Decisions | serial comma (Table II caption) |
| A55 | study2.tex:118 | 90\% interval and the margin | 90\% interval, and the margin | serial comma |
| A56 | study2.tex:132 | positive control) and the code passed | positive control), and the code | serial comma |
| A57 | study2.tex:138 | \paragraph*{Arms, families and tests} | Arms, families, and tests | serial comma |
| A58 | study2.tex:142 | three hypotheses under a fixed sequence then Holm | three hypotheses, tested in a fixed sequence followed by Holm | missing verb; "then" as conjunction |
| A59 | study2.tex:146 | title, abstract or highlights | abstract, or highlights | serial comma |
| A60 | study2.tex:155 | Per the operations log | According to the operations log | register (US business usage) |
| A61 | study2.tex:223 | no test and no comparison is made | no test and no comparison are made | subject-verb agreement |
| A62 | study2.tex:241, 250 | the primary, family~H and Study~2 results | family~H, and Study~2 | serial comma (2) |
| A63 | study2.tex:243 | Differences are variant minus reference; positive favours the variant. | A positive value favours the variant. | caption already says "variant minus the frozen LRF"; "reference" is a second name for LRF |
| A64 | study2.tex:244-245 | (Fig. 8 caption) setting a group to its mean gives inputs ...; an interval away from zero shows ... not that the group alone detects anything. | (see the text for how a knockout interval is read). | verbatim duplicate of the body sentence at study2.tex:263-264; body sentence unchanged |
| A65 | study2.tex:246 | marginal, dependent and unadjusted | dependent, and unadjusted | serial comma |
| A66 | study2.tex:255-257 | The intervals of a linear logit ..., of ..., of ... alone and of attention-weighted pooling in the style of gated attention MIL~\cite{} contained zero. | The following intervals contained zero: those of a linear logit ..., of ..., of ... alone, and of attention-weighted pooling in the style of gated-attention multiple-instance learning (MIL)~\cite{}. | 52-word subject before the verb; MIL undefined; serial comma |
| A67 | study2.tex:258 | the unlearned rank weight and a single-feature weight | weight, and a single-feature weight | serial comma |

### 3.5 Discussion, Conclusion, Reproducibility

| # | Location | Original | Correction | Issue |
|---|---|---|---|---|
| A68 | discussion.tex:13 | $\sigma=0.1$ and a 128-pixel splice | $\sigma=0.1$, and | serial comma (binding NEG 6.1; typography) |
| A69 | discussion.tex:32 | data set or severity | data set, or severity | serial comma |
| A70 | discussion.tex:36-37 | which Fig. 6 cannot separate and the exploratory ablation of Section V-G bears on only as an exploratory result | which Fig. 6 cannot separate and on which the ablation of Section V-G bears only as an exploratory result | repetition ("exploratory ... exploratory"); split preposition |
| A71 | discussion.tex:49, 56, 65 | one data set and one severity; CLIP or SigLIP; pass alone and attention-weighted pooling | serial commas | serial comma (3; Limitations, typography) |
| A72 | discussion.tex:75 | their parameters and the fallback seed; (its revisions r2 and r3) | parameters, and; (the addendum's revisions r2 and r3) | serial comma; unclear antecedent of "its" |
| A73 | discussion.tex:94 | re-score, L1 and other-noise stages | L1, and other-noise stages | serial comma |
| A74 | conclusion.tex:10 | $\sigma=0.1$ and a 128-pixel splice | $\sigma=0.1$, and | serial comma (binding; typography) |
| A75 | declaration.tex:10 | (cards, analysis plans and their addenda); the recorded predictions and the analysis outputs | plans, and; predictions, and | serial comma (Reproducibility section; the AI Declaration text is untouched) |
| A76 | introduction, study1, study2, discussion, conclusion, supplement (77 places) | 95\,\% | 95\% | percent sign closed up, as in IEEE practice and as already printed in the generated tables |

### 3.6 Supplement

| # | Location | Original | Correction | Issue |
|---|---|---|---|---|
| A77 | supplement.tex:50 | tables, equations and propositions | equations, and propositions | serial comma |
| A78 | supplement.tex:75 | re-infilling self-check) and A-6 | self-check), and A-6 | serial comma |
| A79 | supplement.tex:116-117 | code, commit-order and hash audit; family LG and the reference encoders | commit-order, and; family LG, and | serial comma (2) |
| A80 | supplement.tex:124 | there is no control across families | there is no error-rate control across families | incomplete term |
| A81 | supplement.tex:159 | scoring definition or frozen file | definition, or frozen file | serial comma |
| A82 | supplement.tex:179 | no unexpected key and no shape mismatch | key, and no | serial comma |
| A83 | supplement.tex:219 | noise and splices do not produce | noise, and splices | serial comma |
| A84 | supplement.tex:230 | highlights, conclusion or the opening | conclusion, or the opening | serial comma (A4 disclosure; typography) |
| A85 | supplement.tex:264 | before any item, from process-to-process nondeterminism | caused by process-to-process nondeterminism | causal "from" ambiguous |
| A86 | supplement.tex:282 | re-score, L1 and LG stages | L1, and LG stages | serial comma |
| A87 | supplement.tex:333 | no estimate, interval or $p$-value | interval, or | serial comma |
| A88 | supplement.tex:417 | at $\alpha=0.05$ (exploratory) the mean | (exploratory), the mean | comma after long introductory phrase |
| A89 | supplement.tex:511 | raises the PSNR | raises the peak signal-to-noise ratio | abbreviation undefined, used once |
| A90 | supplement.tex:520 | the recovery by GATE-M and the gap | GATE-M, and the gap | serial comma |
| A91 | supplement.tex:586 | vertically adjacent and 0.032 | adjacent, and 0.032 | serial comma |
| A92 | supplement.tex:633 | The sensitivity analysis ... was not rejected in either cell. | The sensitivity analysis ... rejected no hypothesis in either cell. | an analysis is not rejected; a hypothesis is |
| A93 | supplement.tex:714-716 | 72 intervals and no; items and decision rule; qualify or rescue | serial commas | serial comma (3) |
| A94 | supplement.tex:733, 739-740 | $B=0.014$) or splice; 18 and 12; 0.024 and 0.020 | serial commas | serial comma (3) |
| A95 | supplement.tex:752, 768 | (n.d.) or identical; reading and bold rule | serial commas | serial comma (table notes) |
| A96 | supplement.tex:867 | its KKT conditions | its Karush--Kuhn--Tucker conditions | abbreviation undefined |
| A97 | supplement.tex:911, 920, 922 | check and the clean-accuracy look; review and implemented; threshold and arms | serial commas | serial comma (S-III disclosure; typography) |
| A98 | supplement.tex:1015, 1020, 1068, 1071 (2), 1077, 1084 | (43) and; impulse noise and; 13 and 40; caption or padding; weight or margin; Group and Formula; order and counts | serial commas | serial comma (7) |
| A99 | supplement.tex:1084 | 35 features in seven groups; | There are 35 features in seven groups; | sentence begins with a numeral |
| A100 | supplement.tex:1146 | was written and checked by the plan's automated statistical review | was written and then checked by an automated statistical review | the review is not the plan's |
| A101 | supplement.tex:1132, 1158, 1164, 1198, 1199, 1203 | noise and splice; A-S-nbr and A-S-pos; design items and tuning budget; A-S-s3 and A-MIL; A-SF and A-UNL; (0.043 [...]) and KO-S-s3 | serial commas | serial comma (6) |
| A102 | supplement.tex:1163 | gated attention MIL (Ilse et al., 2018; | gated-attention multiple-instance learning (Ilse et al., 2018; | abbreviation undefined |
| A103 | supplement.tex:1174 | interval. 336 intervals were computed | interval. In all, 336 intervals were computed | sentence begins with a numeral |
| A104 | supplement.tex:1144, 1215, 1271 | primary, family H and Study 2 results | family H, and Study 2 | serial comma (3) |
| A105 | supplement.tex:156, 171, 204, 240, 298, 371, 425, 446, 467, 509, 518, 582, 589, 624, 635, 642, 712, 936, 958, 976, 1064 | e.g. \subsection{Calibration and flags} | \subsection{Calibration and Flags} (21 headings) | IEEE second-level headings are in title case, as in the main paper |

## 4. Type (b): left for the authors (meaning, binding text or a rule involved)

| # | Location | Original | Suggested correction | Why (b) |
|---|---|---|---|---|
| B1 | abstract.tex:19; study1.tex:250-251; discussion.tex:68; conclusion.tex:13-14 | a random caption of an image sharing no annotated (COCO) category | a random caption of another image that shares no annotated COCO category with the test image | "sharing no category" has no stated comparison set; binding (D0097 scope) |
| B2 | abstract.tex:24; introduction.tex:88; study2.tex:174; conclusion.tex:21 | lost no more than three points | lost no more than three percentage points (0.03 in accuracy) | accuracies are printed as proportions, so "points" is ambiguous; binding A6.12 L-NI |
| B3 | abstract.tex:25; introduction.tex:90; study2.tex:171 | This is on 450 ... / This is in one pretrained ... | These results are for 450 ... / This result holds for one pretrained ... | vague demonstrative subject; binding scope {S2} |
| B4 | introduction.tex:61-63 | Under an independent-token approximation, we give the condition ... (68 words) | split after "additive evidence sum"; second sentence "The condition is an approximation because image tokens are dependent; Proposition 2 extends it to exchangeably correlated tokens and is linked to no result." | over-long; binding A4.2.4 bullet 1 |
| B5 | introduction.tex:54 | Each item was delivered whatever the analysis found; items 1 and 2 are Study 1, item 3 is Study 2. | Each item was delivered regardless of the outcome; items 1 and 2 belong to Study 1, and item 3 to Study 2. | "items are Study 1" is a category error; lead-in of the binding list (tried and reverted) |
| B6 | introduction.tex:69-73 | (area under the receiver operating characteristic curve, AUROC, 0.961 ...) ... so the preregistered falsifier for the score was met (about 85 words) | "(AUROC)" in parentheses at definition; split into three sentences: separation, the TbV comparison, the falsifier | over-long, nested parentheses; binding A4.2.4 bullet 4 |
| B7 | introduction.tex:75, 77-79 | Re-infilling ... on foil captions: run, formal. / ...): run; headroom not met, its test stage not run | Re-infilling ... and the score-level combination ... were run as formal tests. / ... was run; its headroom condition was not met, so its test stage was not run. | verbless status fragments; binding status wording (A4.2.4 bullet 6, A5.9) |
| B8 | introduction.tex:102 | Not claimed: a verifier that ... | The paper does not claim a verifier that ... | fragment; scope paragraph (F14) wording chosen by the lead |
| B9 | related.tex:26-28 | Masked generation of image tokens~\cite{chang2022maskgit} and unified text-image models place several modalities in one sequence | MaskGIT generates image tokens by masking~\cite{chang2022maskgit}, and unified text-image models place several modalities in one sequence~\cite{...} | compound subject attributes multimodality to MaskGIT; citation-scope question |
| B10 | setting.tex:19-21 | UniDisc's denoiser has no time input ...: time conditioning is off, ..., and the released checkpoint contains no time-embedding weights; the scorer uses ... (57 words) | split before "the scorer uses" | over-long; binding A4.3.1 (mandatory wording) |
| B11 | setting.tex:99-100; study1.tex:288; study2.tex:133; discussion.tex:70; supplement.tex:114, 119 | (not independent reviews) / not an independent review / none is described as independent | per SPEC rule 6: "scripted and agent-run audits (see Declaration)" | **rule conflict**: SPEC rules 5 and 6 forbid "independent" for any audit, even negated; rule 6's prescribed wording points to a Declaration that (interim D0101) no longer lists the audit roles |
| B12 | declaration.tex:24-25 | The authors used Claude (Anthropic) to improve the language and grammar of the manuscript. | authors to decide (full-disclosure draft: drafts/declaration-full-disclosure-draft.tex) | **accuracy concern**: SPEC rule 6 / D0093 say the audits were run by AI agents and the Declaration lists each role; the interim text names only language and grammar. Text fixed by the authors; not edited |
| B13 | study1.tex:113 | $\Var(I_j\Delta_j)=k\sigma_z^2+k(1-k)\mu_z^2$ with $k$ the keep probability of the token's class | add "where $z$ is the token's class (clean or corrupted) and $\mu_z,\sigma_z^2$ its moments" | symbols $z$, $\mu_z$, $\sigma_z$ undefined in the main text; mathematics |
| B14 | study1.tex:207-208 | the first rung at which the size-normalised evidence falls ... and recovers under the changed-code gate, which keeps exactly ..., is the operating point (47 words) | "The operating point is the first rung at which ...; the changed-code gate keeps exactly the tokens whose code did not change." | subject separated from verb by 40 words; protocol wording (A4.2.2) |
| B15 | study1.tex:244 vs. elsewhere | Gaussian noise with $\sigma=0.10$ ... a $128$-pixel splice | $\sigma=0.1$ ... a 128-pixel splice (as in every other sentence) | number token and binding NEG sentence |
| B16 | study1.tex:246-247 | so an improvement larger than 0.05 is excluded and a loss larger than 0.05 is excluded | so an improvement or a loss larger than 0.05 is excluded (the abstract's form) | repetition; binding |
| B17 | study1.tex:253 | after Holm correction over three | after Holm correction over the three hypotheses | elliptical; outcome-label sentence |
| B18 | study1.tex:306-307 | the rival's win is read as this label-circularity concern | the rival's higher AUROC is attributed to this label circularity, not to any corruption effect | informal "win"; unclear "read as this concern"; A4.2.2 item 2 |
| B19 | study1.tex:377; study2.tex:232, 234; supplement cost tables | network rows | define at first use (e.g. "rows, i.e. sequences, processed by the network per item") | undefined term; only the authors know the exact unit |
| B20 | study2.tex:40-41 | the seven token scores are five from the model with the caption masked, a patch texture, and a codebook-neighbour distance, and the other groups summarise them | e.g. "One group holds seven token scores (five computed by the model with the caption masked, a patch-texture score and a codebook-neighbour distance); the other six groups summarise them." | structure unclear (which group holds the seven scores); needs the feature table to confirm |
| B21 | study2.tex:183-184 | the Holm-adjusted $p$ is 0.049, a margin of 0.001 below the 0.05 level | the Holm-adjusted $p$ is 0.049, 0.001 below the 0.05 level | "margin" collides with the L-NI non-inferiority margin; binding (SPEC "L4's Holm margin stated") |
| B22 | study2.tex:198 | one-sided 0.006, Holm-adjusted 0.011, two-sided 0.011 | one-sided $p=0.006$, Holm-adjusted $p=0.011$, two-sided $p=0.011$ (parallel to the shot-noise cell) | binding D0091 three-$p$ string |
| B23 | study2.tex:200 | The one-sided and Holm-adjusted $p$ are 0.029 | The one-sided and Holm-adjusted $p$-values are both 0.029 | binding D0091 |
| B24 | discussion.tex:81; supplement.tex:235 | under the plan's fixed time inequality | name the inequality once (e.g. "the plan's rule that B may run first when the coherence stage ends before time T") | undefined term; content only the authors can state |
| B25 | supplement.tex:252 | called blind on the lead's assertion | called blind on the assertion of the analyst who ran the stage | internal project role in a journal supplement |
| B26 | supplement.tex:312 | Moved from the main paper (edit 6; A4.2.5 keeps ...) | Moved from the main paper (A4.2.5 keeps ...) | internal edit-round label visible to readers; record text |
| B27 | supplement.tex:1150 | the frozen LRF's shape functions (main paper, Fig.~4) | (main paper, Fig.~\ref{M-fig:lrf_weights}) | **factual error**: main Fig. 4 is family P; the shape functions are Fig. 6 (main.aux). Not applied because it changes a number/reference |
| B28 | supplement.tex:919 | specified in SAP Addendum A5 | specified in Addendum A5 of the statistical analysis plan | abbreviation undefined in the supplement; binding S-III disclosure |
| B29 | supplement.tex:888-891 | ... so the family's test was not run. The family's test (H4) was not run, and nothing is stated ... | ... so the family's test (H4) was not run, and nothing is stated ... | duplicated clause; binding A5.9 text |
| B30 | supplement.tex:346, 375, 395, 477, 533, 558, 748, 804 | long sentence-case captions holding the table notes | short title-case caption above; notes in a \parbox below (as the other supplement tables do) | IEEE table style; layout task |
| B31 | tables/tab_families_glance.tex (generated by scripts/tab_glance.py) | not run (gatekept) | not run (conditional on a primary rejection) | jargon; edit the script, not the .tex |
| B32 | setting.tex:15 and elsewhere | $m=1\,024$, 16\,384, 10\,000 | check against the IEEE style manual (four-digit numbers are normally not grouped) | number typography |
| B33 | supplement.tex:229-231 | ... under that delegation the stricter reading (...) was adopted within the authors' study pipeline under that delegation at 18:42 UTC ... (64 words) | delete the second "under that delegation"; split before "(decision records" | duplicated phrase in a binding A4 disclosure (tried and reverted) |
| B34 | whole paper | "data set" (3); GPU, CPU undefined | optional: "dataset" (IEEE usage); expand GPU/CPU at first use if the editor asks | consistent as is; house choice |

## 5. Rule conflicts and concerns

1. **SPEC rule 5/6 against current text (B11).** "independent" appears in six audit sentences, always negated. Literal
   reading of rule 5 forbids it; rule 6's own wording ("scripted and agent-run audits (see Declaration)") depends on a
   Declaration that now mentions only language and grammar (B12).
2. **Declaration accuracy (B12).** Not edited (fixed by the authors), but the statement looks narrower than the AI use that
   SPEC rule 6 and D0093 describe. The clarity-editor contract requires flagging this.
3. **Serial comma vs. British house style.** Applied because the brief names it as IEEE style; spelling stays British.
4. **Page budget.** The serial commas alone pushed two reference lines onto p. 16; removing the duplicated caveat from the
   Fig. 8 caption (A64) brought the paper back to 15 pages. Net effect on the main text: about 47 words shorter (14,929
   against 14,976 PDF words), far less than a quarter column, so no room was freed for a figure.
5. **DOCX** (`docx/Paper2_TNNLS_manuscript.docx`) predates these edits and needs regenerating with `scripts/make_docx.py`.
6. **B27** is a real cross-reference error in the supplement and should be fixed before submission.

## 6. Verification

- `drafts/integrity-diff-language.md`: numbers 625/625 (main) and 1612/1612 (supplement); `\cite`, `\label`,
  `\ref`/`\cref`/`\eqref` and mathematics identical multisets; every binding-region edit listed (typography only, with the two
  non-binding protocol sentences explained); must-not word counts unchanged.
- `bash build.sh`: main 15 pp., supplement 18 pp., 0 undefined references or citations, 0 overfull boxes over 2 pt, all
  fonts embedded, 0 column gaps. Pages 1-2 rendered at 45 dpi: no float above the title, Fig. 1 at the top of p. 2.
- Hidden characters: all `.tex` and `.bib` files are pure ASCII.
- Abstract word count unchanged (247; only a comma added).
- Nothing committed.

## 7. Round 2 (decision D0105), 2026-10-30

Applied: B1-B10, B13-B18, B20-B23, B25-B31, B33, B34 ("dataset" only). B19 and B24 were defined because sources exist
(B19: `paper2/sections/appendix.tex` app:cost, "one row of a batch"; B24: SAP Addendum A4, FOIL-first rule item 3). Held:
B11, B12, B32. Details, number and reference changes, and the cuts that hold the main paper at 15 pages are in
`paper2-tnnls/drafts/integrity-diff-language.md`, section "Round 2". Points to note:
- The abstract used the pre-ruled R8/F1 valve (alpha clause to Results; 248 words). Its B2 is "three percentage points" only.
- B31 changes status wording that SAP A4.2.5 item 6 prescribes ("gatekept: P+ empty"); applied under D0105, and the supplement
  status map keeps the prescribed text. B30 keeps the F7 limits in the Tier-3 table caption (A4.2.5 item 5).
- Four sentences that repeated content kept elsewhere were removed, and six widow lines were trimmed.
