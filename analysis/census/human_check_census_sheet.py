"""Blind human check of the value-rule census (Paper 1; third of three human checks).

    python -E -P analysis/census/human_check_census_sheet.py      (openpyxl is a user-site package)

Frame: rows of research/review/census/census-random-final.jsonl (the adjudicated random sample, codebook v1.2) that
are eligible, have an F2 code and a generated-sample headline metric (F1 not NA or QL): the F3-F6 denominator of
analysis/census/summary_random.py (152 rows; the F2 denominator of 153 adds one samples-only row). Papers the first
author has already seen with a model answer are left out (research/CONFIRM-2026-10-20.md, research/AUTHOR-CHECKS-
2026-10-21.md, the extraction-check ids).

Draw, stratified by the headline value-rule class (codebook v1.2 B-28): 12 non-plain, 8 not stated (NS), 4 plain (U),
random.Random(20261024) over the sorted sids of each class in that order, then the 24 shuffled with the same
generator for the row order. Plain is oversampled because it is the rare class the census claim turns on
(147 of 153 non-plain or not stated); the agreement script reports raw and frame-weighted agreement.

The sheet shows the census's headline result (task, metric, value, location) as the anchor and asks, blind:
Q1 is this the headline result the rules pick; Q2 value-rule class (non-plain / plain / not stated) and optional
letters; Q3 diversity reported with it; Q4 step sweep. Model answers go to
analysis/census/human-check-census-model-answers.json (the reader must not open it). Refuses to overwrite.
Agreement: human_check_census_agreement.py.
"""
import hashlib
import json
import random
import re
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[2]
SEED = 20261024
SIZES = {"non-plain": 12, "not stated": 8, "plain": 4}
OUT_X = ROOT / "research/HUMAN-CHECK-CENSUS.xlsx"
OUT_M = ROOT / "analysis/census/human-check-census-model-answers.json"
# census full texts live in the main checkout only (research/review/census/CLAUDE-CODER-BRIEF.md)
TXT = Path(r"C:\Users\Shlok\Downloads\Multi-Modality Language model\research\sources\census-text")

for p in (OUT_X, OUT_M):
    if p.exists():
        raise SystemExit(f"{p} exists: the draw is frozen")

rows = [json.loads(l) for l in open(ROOT / "research/review/census/census-random-final.jsonl", encoding="utf-8")
        if l.strip()]
titles = {}
for l in open(ROOT / "research/review/census/census-order.csv", encoding="utf-8").read().splitlines()[1:]:
    rank, sid, arx, title = l.split(",", 3)
    titles[sid] = title.strip().strip('"')


def low(v):
    return (str(v) if v is not None else "").strip().lower()


def klass(f2):
    t = {x.strip() for x in (f2 or "").split("+")}
    if f2.strip() == "U":
        return "plain"
    if t & set("ATPSGMC"):
        return "non-plain"
    return "not stated"


frame = [r for r in rows if low(r.get("eligible")) == "yes" and low(r.get("F2_codes")) not in ("", "na")
         and low(r.get("F1_value")) not in ("", "na", "ql")]
assert len(frame) == 152, len(frame)

seen = set()
for f in ("research/CONFIRM-2026-10-20.md", "research/AUTHOR-CHECKS-2026-10-21.md"):
    seen |= set(re.findall(r"\b[MRU]\d{4,5}\b", (ROOT / f).read_text(encoding="utf-8")))
seen |= {i for _, i in json.load(open(ROOT / "analysis/extraction/d0052/human-check-model-answers.json",
                                      encoding="utf-8"))["drawn"]}
left_out = sorted(r["sid"] for r in frame if r["sid"] in seen)
pool = {k: sorted(r["sid"] for r in frame if klass(r["F2_codes"]) == k and r["sid"] not in seen) for k in SIZES}
rng = random.Random(SEED)
drawn = {k: rng.sample(pool[k], n) for k, n in SIZES.items()}
order = rng.sample([i for k in SIZES for i in drawn[k]], sum(SIZES.values()))
by = {r["sid"]: r for r in frame}


def link(r):
    v = r.get("F0_version") or ""
    return f"https://arxiv.org/abs/{r['arxiv']}{v if re.fullmatch(r'v\d+', v) else ''}"


RULE_WORDS = r"\b(greedy|argmax|temperature|top-?[pk]|nucleus|deterministic|ancestral)\b"


def headline(r):
    """the census anchor, with any parenthetical that states a decoding setting removed (it would answer Q2)"""
    s = f"{r['F1_value']} {r['F1_metric']} on {r['F1_task']}"
    s = re.sub(r"\s*\([^()]*" + RULE_WORDS + r"[^()]*\)", "", s, flags=re.I)
    assert not re.search(RULE_WORDS, s, re.I), s
    return s


wb = openpyxl.Workbook()
ws = wb.active
ws.title = "check"
head = ["#", "Paper id", "Title", "Link (arXiv, version coded)", "Local text copy", "Headline result (census anchor)",
        "Where", "Q1 Headline right?", "Q2 Value rule", "Q2 Letters (optional)", "Q3 Diversity", "Q4 Step sweep",
        "Reader", "Notes"]
ws.append(head)
fill = PatternFill("solid", fgColor="DDEBF7")
for c in ws[1]:
    c.font, c.fill = Font(bold=True), fill
    c.alignment = Alignment(vertical="top", wrap_text=True)
DV = {
    8: ('"yes,no,unclear"', "Q1", "Is the shown result the one the rules pick? (rules sheet)"),
    9: ('"non-plain,plain,not stated,unclear"', "Q2", "Value rule for the shown result (rules sheet)"),
    11: ('"yes,no,unclear"', "Q3", "Diversity reported with the shown result?"),
    12: ('"yes,partial,no,unclear"', "Q4", "Steps / NFE / tokens per step varied for the paper's own method?"),
}
dvs = {}
for col, (f, t, p) in DV.items():
    dv = DataValidation(type="list", formula1=f, allow_blank=True, showErrorMessage=True, errorTitle=t,
                        error="Pick a value from the list.", promptTitle=t, prompt=p, showInputMessage=True)
    ws.add_data_validation(dv)
    dvs[col] = dv
out_rows, problems = [], []
for n, i in enumerate(order, 1):
    r = by[i]
    txt = TXT / f"{r['arxiv']}.txt"
    if not txt.exists() or txt.stat().st_size == 0:
        problems.append(f"{i}: no local text {txt}")
    if not titles.get(i):
        problems.append(f"{i}: no title")
    ws.append([n, i, titles.get(i, ""), link(r), str(txt), headline(r), r["F1_location"], "", "", "", "", "", "", ""])
    k = n + 1
    ws.cell(row=k, column=4).hyperlink, ws.cell(row=k, column=4).style = link(r), "Hyperlink"
    ws.cell(row=k, column=5).hyperlink, ws.cell(row=k, column=5).style = txt.as_uri(), "Hyperlink"
    for col, dv in dvs.items():
        dv.add(ws.cell(row=k, column=col))
    for col in range(1, 15):
        ws.cell(row=k, column=col).alignment = Alignment(vertical="top", wrap_text=col in (3, 6, 7, 14))
    out_rows.append({"row": n, "sid": i, "arxiv": r["arxiv"], "link": link(r), "local_text": str(txt)})
if problems:
    raise SystemExit("problems: " + "; ".join(problems))
for col, w in zip("ABCDEFGHIJKLMN", (4, 8, 40, 30, 30, 45, 30, 11, 13, 12, 10, 11, 8, 30)):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "C2"

R = wb.create_sheet("rules")
RULES = [
    ("HOW TO CODE", "Census codebook in plain language (research/review/coverage/census-codebook-v1.md, amended by v1.1 and v1.2). Code from the paper's text only (main text and appendix), not from its code. Answer every question for the headline result shown on the row."),
    ("Q1 Headline right?", "The census codes one result per paper: the first number in the abstract for the paper's own generative method on an in-scope task (text or code made by the diffusion model; for a unified model, the output of its diffusion or masked part). Skip numbers that are only speed or only likelihood (perplexity, throughput, one-step masked accuracy). If the abstract has none: the first main-text results table that reports the final method on the main task; in it, the row and metric the text quotes, else the default configuration, else the first row of the final method. Answer no only if the rules clearly pick another number (say which in Notes); then still answer Q2-Q4 for the shown result."),
    ("Q2 VALUE RULE", "How the paper says token values are chosen when it produced the shown result."),
    ("non-plain", "At least one of these is stated for that result (even if the rest is not stated):"),
    ("  A", "argmax or greedy commit at each step (temperature 0, \"deterministic\"). The final rounding of an embedding model is not A."),
    ("  T", "a stated temperature other than 1."),
    ("  P", "top-p, top-k or nucleus truncation."),
    ("  S", "values are sampled, then positions are chosen by a score of the sampled value (confidence of the sampled token, MaskGIT style, LLaDA low-confidence remasking at temperature above 0)."),
    ("  C", "positions chosen by a confidence, margin, entropy or threshold score of the predicted distribution, with the token rule not stated (if it is stated, it is A or S)."),
    ("  G", "steering at sampling time: classifier-free or classifier guidance, reward, value or constraint gradients, grammar or validity masks applied per step. Rewards used only in training are not G."),
    ("  M", "selection among complete outputs by a score available without the ground truth: best-of-N, MBR, reranking, verifier, beam or tree search, particle resampling, rejecting invalid outputs. Not M: pass@k or best-of-N against the references (oracle)."),
    ("plain", "Values sampled at temperature 1 (or \"ancestral\", \"standard sampling\", or a named sampler that fixes this), AND the position rule stated (random, scheduled, left-to-right or blockwise), AND no truncation, guidance or selection, shown by an explicit statement or by a settings list for the experiment that names none. \"Temperature 1.0\" alone is not enough: that is not stated."),
    ("not stated", "The paper does not let you read the rule for this result. Settings stated only for training, RL rollouts, data generation or distillation do not count. A caption or experiment-section sentence beats a hyperparameter table, which beats a method definition; a method definition counts only if the experiment uses that method by name. Two conflicting statements at the same level: not stated."),
    ("Q2 Letters", "Optional: the letters you found, joined by + (for example A, C, G+NS, M+T). Add +NS when guidance or selection is stated but the base token rule is not."),
    ("Q3 DIVERSITY", "yes if the same table or figure as the result, or one the text explicitly pairs with it (same model, sampler setting and task), reports a diversity measure: entropy, distinct-n, self-BLEU, MAUVE, pass@k with k > 1, unique or repetition rates, number of modes, pairwise dissimilarity among samples, Vendi; for images also recall or LPIPS diversity. Not diversity: quality scores, generative perplexity, novelty against training data, validity, best-of-N reward."),
    ("Q4 STEP SWEEP", "yes if the paper's own method is shown at three or more settings of denoising steps, NFE or tokens per step (set directly or through a threshold, schedule or cache interval), on the headline's task and output length, with a step measure printed for each setting and a generated-sample metric; partial if exactly two settings; no otherwise. Not a sweep: steps changing only because the output length changes; speed, latency or speed-up without a step measure; sweeps over guidance strength, candidates, beam width or particles, or block size across separately trained models."),
    ("unclear", "Use only if you cannot decide; say why in Notes."),
]
R.column_dimensions["A"].width = 22
R.column_dimensions["B"].width = 150
for a, b in RULES:
    R.append([a, b])
    k = R.max_row
    R.cell(row=k, column=1).font = Font(bold=True)
    for c in (1, 2):
        R.cell(row=k, column=c).alignment = Alignment(wrap_text=True, vertical="top")
    if a.isupper() or a.startswith("Q2 VALUE"):
        R.cell(row=k, column=1).fill = R.cell(row=k, column=2).fill = fill
    R.row_dimensions[k].height = 15 * max(1, -(-len(b) // 150))
wb.save(OUT_X)

OUT_M.write_text(json.dumps({
    "purpose": "model answers for the blind human census check; do not open before the sheet is filled",
    "script": "analysis/census/human_check_census_sheet.py", "seed": SEED, "sizes": SIZES,
    "frame": "census-random-final.jsonl rows: eligible yes, F2 coded, F1 not NA/QL (152)",
    "frame_class_counts": {k: sum(klass(r["F2_codes"]) == k for r in frame) for k in SIZES},
    "left_out_already_seen": left_out,
    "pool_class_counts": {k: len(v) for k, v in pool.items()},
    "frame_sha256": hashlib.sha256("\n".join(sorted(r["sid"] for r in frame)).encode()).hexdigest(),
    "rule": "rng=random.Random(seed); per class in the order non-plain, not stated, plain: rng.sample(sorted sids, n); rng.sample(all 24) = row order",
    "drawn": drawn, "rows": out_rows,
    "answers": {i: {"class": klass(by[i]["F2_codes"]), "F2_codes": by[i]["F2_codes"], "F2_detail": by[i].get("F2_detail"),
                    "F3": low(by[i]["F3"]), "F4": low(by[i]["F4"]), "F5": by[i].get("F5"), "F6": by[i].get("F6"),
                    "rank": by[i]["rank"], "F1_task": by[i]["F1_task"], "F1_metric": by[i]["F1_metric"],
                    "F1_value": by[i]["F1_value"], "F1_location": by[i]["F1_location"]} for i in order}},
    indent=1), encoding="utf-8")
LEAK = re.compile(r"greedy|argmax|temperature|top-?[pk]|nucleus|guidance|cfg|best-of|beam|remask|confiden|sampl", re.I)
print(OUT_X)
print("frame", len(frame), "left out", len(left_out), "pool", {k: len(v) for k, v in pool.items()})
print("anchor cells mentioning a decoding word (check by hand):",
      [i for i in order if LEAK.search(headline(by[i]) + " " + by[i]["F1_location"])])
