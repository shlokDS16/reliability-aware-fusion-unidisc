# Project Timeline

Append-only chronology for DLM Discovery. Never rewrite an entry. When new information
contradicts an old entry, add a new entry that references the old one.

Entry template:

```
## YYYY-MM-DD - [short title]

**What happened:**
**Why:**
**Discovered:**   (facts learned, including surprises)
**Assumed:**      (flagged as assumption, not fact)
**Implications:** (what this constrains or unlocks later)
**Links:**        ADR-00N, session file
```

---

## 2026-10-13 - Project initialized

**What happened:** Project Operating System scaffolded via project-kickoff.
**Why:** Establish persistent standards and living memory from day one.
**Implications:** Every future session loads CLAUDE.md and follows the standards
in `claude/`. End-of-session routine runs before any session finishes.

## 2026-10-13 Kickoff
- Merged the ChatGPT blueprint and the Gemini proposal into research/FRAMEWORK.md; 19 agents generated; ledgers D0001 to D0003.
- Measured hardware: 12 GB laptop GPU, 66.7 GB free disk. ICLR 2027 and AAAI-27 already closed.
- First frontier sweep (E1): causal understanding-generation coupling and mechanistic interpretability are the sparse areas.
- Next: Python environment, then Gate 1.

## 2026-10-14 (late) - Primer chapters for the Gaussian family and unified multimodal models
- Two paper-reader agents, one at a time (FRUGAL budget; user's choice): `research/review/dossier/primer-gaussian.md` and `primer-multimodal.md`, each with an exact-enumeration check script that reruns cleanly.
- Discoveries: Gaussian samplers carry a final-rounding factorisation term the framework lacked; corollary 3 is unattested in six papers; the multimodal E_fact splits exactly into within-text, within-image and cross-modal CMI, which makes P5 as worded near an identity, so it is split into P5a/P5b (D0010). No paper measures a cross-modal quantity per step. Released MMaDA-Parallel-A code differs from the paper's "parallel at every step" (E3).
- Implications: framework-v1 must apply 25 edits; the cross-modal CMI per step is the most promising untested measurement for Paper 2. User set a two-week horizon with quality first.

## 2026-10-14 (build session) - Framework v1 and v2; the selection term fails audit
- framework-v1 applied 25 primer edits; a 47-model design-space table tested coverage (36 fit, 11 partly, 0 no).
- method-architect formalised E_sel; red-team found 2 fatal flaws (the tilt/selection split is not a law property; per-step impossibility depends on the coupling) and full-text prior art (2605.12522, Hayakawa et al. 2510.04525) already covers the k = 1 law and the resample fix. D0011 withdraws E_sel and E_tilt as new terms; framework-v2 keeps one signed value slot V.
- Implication: Paper 1's weight moves to the design space, an independently coded census of value rules and reporting, and stated open problems; the controlled four-arm value-rule result or the cross-modal measurement is the experiment that would carry Paper 2.
