"""Builds research/review/extraction/extractor-brief-v0.5.md from v0.4 by the edits of EXTRACTION-PLAN-v0.5 s1
(deterministic; v0.4 is read, never written). Each edit names its red-team finding (audit 4, 2026-10-20).
MA2: coding rules KA1-KA4 for the fields three gate criteria measure (higher_is_better, budget_across_arms,
arm scoring, credited_ablation), each with a synthetic example; credited_ablation added to the group field list.
Run: python -I analysis/extraction/make_brief_v05.py   (prints the sha256 of the output)
"""
import hashlib
from pathlib import Path

SRC = Path("research/review/extraction/extractor-brief-v0.4.md")
DST = Path("research/review/extraction/extractor-brief-v0.5.md")
t = SRC.read_text(encoding="utf-8")


def rep(old, new, count=1):
    global t
    assert t.count(old) == count, (old[:60], t.count(old))
    t = t.replace(old, new)


# header (outside the text block; no session sees it)
head_old = t[:t.index("```text")]
head_new = """# Extractor brief, form v0.5 (draft, 2026-10-20; not frozen)

Give the text block below, with extraction-schema-v0.5.json and CONTRACT.md, to every extraction session
(EA claude-opus-5-5; EB and ER claude-sonnet-5-5). The adjudicator (EC, claude-fable-5-1) gets the block plus
the adjudication paragraph; the public-version QA reader (EQ, claude-sonnet-5-5) gets only the EQ paragraph,
the QA block and the evidence rules. The block restates codebook v1.2 (block F, unchanged from v0.1, with the F1 readings C-F1a to C-F1e), rubric
v0.2 step 1 (CT) and the design choices C1-C5, so a session needs no other file. Plan and scoring:
EXTRACTION-PLAN-v0.5.md (not given to sessions). worked-examples-v0.3.md and worked-examples-v0.4.md are
reference files that no session sees: Stage A compares the sessions' units with them. Built from v0.4 by
analysis/extraction/make_brief_v05.py. Changes from v0.4 (red-team audit 4): attribute rules KA1-KA4 in
block K for higher_is_better, budget_across_arms, arm scoring and credited_ablation, each with a synthetic
example (MA2); credited_ablation added to the group field list; schema file v0.5. Every example is
synthetic; analysis/extraction/brief_contamination_v05.py checks every quoted span, number, number run and
word 5-gram of the session text against all 608 include texts (MA2, mi3).

"""
t = head_new + t[len(head_old):]

rep("Paper 1 (critical systematic review of diffusion language models), form v0.4.",
    "Paper 1 (critical systematic review of diffusion language models), form v0.5.")
rep("extraction-schema-v0.4.json", "extraction-schema-v0.5.json", count=2)

# H block: pointer to KA1
rep("metric_printed; metric_kind (G5); higher_is_better;", "metric_printed; metric_kind (G5); higher_is_better (KA1);")
# U6(a): pointer to KA4
rep("form ONE replacement group with the anchor, credited_ablation true;",
    "form ONE replacement group with the anchor, credited_ablation true (KA4);")

KA = """KA Attribute rules (block K, and higher_is_better in block H). The order of steps below holds under G4 too.
KA1 higher_is_better (every K unit and H unit): take the first step that gives a value.
   (a) Printed direction: an arrow (↑ or ↓) printed with this metric in the column header, row label or
       legend, or a sentence of the caption or text saying that higher (or lower) is better for this metric:
       true for higher, false for lower, even where step (b) says otherwise.
   (b) Convention list (the same list as the metric lookup the scripts use): true for accuracy (acc, acc.),
       exact match (EM), pass@k, BLEU, ROUGE-L, CIDEr, CLIP score, tokens per second (TPS), tokens per
       forward (TPF), speed-up; false for perplexity (PPL), NLL, bits per token, FID, latency, number of
       steps, NFE. A metric matches when its printed name is one of these, alone or with a qualifier (top-1,
       avg., gen.).
   (c) Otherwise null; add the unit id to doubt and name the metric in notes.
   Never take a direction from the arm the paper calls best, from bold or underlined numbers, or from your
   own knowledge of a metric that is not in the list. Units of one group with the same metric_printed get one
   value. Synthetic: a header "Drift-Q ↓" gives false (a); "Avg. acc" with no arrow gives true (b);
   "Cohesion index" with no arrow and no statement gives null (c).
KA2 budget_across_arms (group). The inference budget has two items: (1) the number of sampling steps or
   function evaluations (NFE) that produced the group's values; (2) the generation length (the output tokens
   the sampler fills). For an autoregressive arm, item (1) is its generation length. Items come from the
   table, its caption, the setup of this experiment or a hyperparameter table (G3 order); never compute them
   (a stated tokens per step and a stated length do not give a step count).
   matched: both items are stated for every arm and are equal across the arms, or a sentence about this
   experiment says that every compared arm uses the same steps (or NFE) and the same generation length;
   reported: item (1) is stated for every arm, but the arms are not matched (the factor changes steps, NFE or
   tokens per step; the lengths differ; or item (2) is missing for an arm);
   not reported: item (1) is missing for at least one arm.
   Wall-clock time, FLOPs, memory and training budgets are not budget items. Synthetic: a caption "Every
   variant decodes 192 tokens in 48 steps" gives matched; a steps-or-nfe group at 12, 24 and 48 steps gives
   reported; steps printed for the own arms but not for a baseline gives not reported.
KA3 scoring (each arm): how this arm's quality values in the group were obtained.
   likelihood: every quality unit of the group has metric_kind likelihood (G5), or the paper states that
   this arm's values (or the values of every arm in this table or experiment) come from likelihood scoring
   (option log-likelihood ranking, perplexity or NLL under the model);
   generated: otherwise, when the group has a K unit with metric_kind generated-sample (a benchmark accuracy
   is generated unless such a statement exists);
   not_stated: the group's units are all speed, steps or other (G5), or the paper says that some arms are
   likelihood-scored without saying which.
   Arms of one group may differ. A group with both generated-sample and likelihood units: code the scoring of
   its generated-sample units. Synthetic: a caption "Baselines are ranked by option log-likelihood" gives
   likelihood for every baseline arm and generated for the own arms; a group whose only unit is "Latency (s)"
   gives not_stated for every arm.
KA4 credited_ablation (group): true when an arm of the group removes the credited component (S13) or
   replaces it by another method on the same base model: the replacement groups of U6(a), and
   component-removal or task-or-modality-removal groups whose removed part is the credited component.
   false otherwise: groups that vary only a parameter of the credited component (its size, steps,
   threshold), groups that remove a different component or a part of it, model-class groups, and every group
   of a paper whose S13 type is analysis-only, benchmark-or-dataset or theory. Synthetic, for a paper that
   credits a "planner head": an arm "w/o planner head" gives true; arms with 2, 4 and 8 planner layers give
   false; an arm "w/o planner dropout" gives false.
"""
rep("Not groups: comparisons among baselines only;", KA + "Not groups: comparisons among baselines only;")
# E3 synthetic caption: v0.4's wording shares the 5-gram "table 3 ablation of the" with one include text (mi3 scan)
rep(""""caption": "Table 3: Ablation of the planner head on three synthetic test
   splits."}""", """"caption": "Table 3: Planner-head ablation on three synthetic test
   splits."}""")

# group, arm and unit field lists point to the KA rules
rep("""other_changes ('' if none stated), budget_across_arms (inference budget: matched,
reported, not reported), shape""", """other_changes ('' if none stated), budget_across_arms (KA2: matched, reported, not
reported), credited_ablation (KA4: true or false), shape""")
rep("shots_printed, scoring (generated, likelihood, not_stated), number_source",
    "shots_printed, scoring (KA3: generated, likelihood, not_stated), number_source")
rep("K unit fields: group_id, benchmark_printed, metric_printed, condition_printed, metric_kind, higher_is_better,",
    "K unit fields: group_id, benchmark_printed, metric_printed, condition_printed, metric_kind, higher_is_better (KA1),")

for bad in ("form v0.4.", "schema-v0.4.json"):
    assert bad not in t[t.index("```text"):], bad
DST.write_text(t, encoding="utf-8", newline="\n")
print("written", DST, "sha256", hashlib.sha256(DST.read_bytes()).hexdigest())
