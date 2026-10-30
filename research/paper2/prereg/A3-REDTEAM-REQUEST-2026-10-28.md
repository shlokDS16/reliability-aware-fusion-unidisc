# Red-team request: SAP Addendum A3 (2026-10-28)

From: statistician. To: red-team. Scope: `research/paper2/prereg/SAP-GATE-2026-10-28.md`, from the heading "Addendum A3" (sections A3.1 to A3.11) to the end. Earlier text is byte-identical to the version before A3 (git shows 108 inserted lines and none deleted).
Status of A3: written before outcomes; no M2 to M5, S2, FOIL, Omni or suite item exists; no M1 outcome read by me (M1 at 106 of 200 after a memory-guard stop; per the lead nobody read outputs beyond probe-2 items 0 to 25; I opened nothing under `runs/P2-PROBE-02/`).

## SAP hashes (SHA-256, both conventions, as for A2 and A2b)

| State | CRLF working tree | LF form (git blob content) |
|---|---|---|
| before A3 (HEAD 8c8363de) | `9413de7570267bded82117d59d77eb2cf1d00299d3d4547fcbc655a616180353` | `7ba0c117ada747f23b24dac89c4b753c8d458e65fdeb25b9c438cf7bb59d30e7` |
| **after A3** | `7e1a24186cb2e41c4598b5751e994238fd03260c1f4992774fb938e23210ad2f` | `f26b8fa5fa2dfaf1649a978784b234590cb88243c3eda4632b5b40436e2493ee` |

Power script `analysis/paper2/gate/a3_power.py` SHA-256 `85f394ffbad7fe146eec16586f0922f55aaad46177ac7fdc3cfcb35e9e6b0c18`; output `runs/P2-GATE-A3/a3_power_output.txt` SHA-256 `760fe03313ce1a07946d93fec69d0cc26a7c41985ab25a24325b563b6b1fc1e0`; `a2_power.py` unchanged (`78fc0fb8...f7e`, asserted at run time).

## What changed (one line each)

1. **A3.1** S2 and B: n = 300 planned is primary (ANONYMIZED approved about 10:30 IST, before outcomes); the SAP's n = 150 (first 150 items or pool positions, a nested prefix) is a recorded sensitivity with no power to reject or rescue; floor of 120 kept; no optional stopping; power recomputed (derived; pi_d and theta ASSUMED).
2. **A3.2** S2: kept draw = chain log-likelihood with caption masked, and the fixed random-order unguided 16-step sampler (not UniDisc `_sample`), both accepted as readings of AD.5; the `--arms igate,irand` cut allowed only under AB.9, at launch, for all items; image direction only.
3. **A3.3** Swap in M4: own seed stream, no text arms, PS m = 2 unchanged.
4. **A3.4** FOIL: pair key `annotations[].id`; foil label noise (4.0 percent questionable, up to 8.7 percent, one reader) disclosed, no exclusion; text-only-cue wording rule for the ceiling rule (ii).
5. **A3.5** Omni R: corruptions at 512 px then tokenised at 256 px; exclusion without replacement; implementer thresholds adopted as committed and not loosened; adapter signature before any R stage; P+ under R3 read on d.
6. **A3.6** E-pred: fit module frozen (hashes), score module bug-fix-only after the first M4 item; no p-value; suite numbers must use the audited functions.
7. **A3.7 to A3.9** seeds by name (append-only), guard settings operational and the M1 resume continues the same list, disclosure additions.

## What I want checked

1. **A3.1 and "preregistration".** Is a pre-outcome change of n for two families, with the original n kept as a nested sensitivity, acceptable, or does it need the sensitivity to be primary? Is keeping the completed-n floor at 120 (now 40 percent of plan) sound, given the "partial prefix" label and the printed minimum detectable effect? Is the sentence "sensitivity can neither reject nor rescue" enough to stop a forking-paths reading when the two n disagree?
2. **A3.2 item 1.** Does "highest own caption-masked likelihood" admit the chain log-likelihood of the sampled tokens as a faithful reading? Could this selection statistic favour one arm (flagged set against random set) in a way the draw-level and all-four contrasts of AB.4 would not expose?
3. **A3.2 item 3.** Is the I-CHG cut (a descriptive oracle) correctly described as inferentially free for the confirmatory family, and is "decided at launch, all items, time only" adequate under AB.9?
4. **A3.2 item 2 smoke rule.** A 3-item S2 smoke whose Y values are not read: is that firewall adequate?
5. **A3.4.** Does the label-noise wording and the ban on exclusions hold up? Does the ceiling-rule wording ("text-only cues are not excluded as a cause") block a misleading reading of B?
6. **A3.5.** (i) 512 px then 256 px with JPEG/noise attenuation: is "same corrupted inputs as P, disclosed" the right reading of AD.7 "pixel-level corruption parameters"? (ii) Implementer-written thresholds (A5 shift margin 1.0 nat, 7,000 MiB, others) adopted as committed: is "tighten before the timing stage, never loosen" adequate? (iii) Does "the auditor runs the CPU checks and reviews the GPU `selfcheck.json`" meet AB.5 item 1 "run and signed by the gate-auditor"? (iv) P+ under R3 read on d with the sign of the d difference: acceptable?
7. **A3.6.** Is the fit/score split a way around AB.3 item 5 ("not edited afterwards")? Is "bug fix only, pre-fix output kept" a sufficient guard for `epred.py`? Is freezing `theory.py` (shared with `analysis_m4` and the suite) a risk to other families?
8. **A3.8.** Confirm that guard settings, including a candidate change to ceilings 11,000/11,000 MiB, rise 4,500 MiB and cap 0.75, touch no statistical rule, and that resuming M1 from item 106 on the same list needs no new addendum.
9. **Anything the addendum does not say** that you think it must, in particular about the M1 chance bar (AB.7 item 3) if M1 cannot complete the 200 items.

Withdrawal conditions of AB.8 apply to A3 as to A2b.
