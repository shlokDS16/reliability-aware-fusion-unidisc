"""Blind human check of the study-level flags behind the RQ2-RQ6 statements (red-team 2026-10-21 M6; decision D0060).

    python -E -P analysis/extraction/d0052/human_check_sheet.py          (openpyxl is a user-site package)

Draws 12 of the 59 sampled included studies, 4 per update stratum, with random.Random(20261022) over the sorted ids of
each stratum; writes research/HUMAN-CHECK-2026-10-21.xlsx (one row per study: id, title, link, six yes/no/unclear
questions, notes; no model answers shown) and analysis/extraction/d0052/human-check-model-answers.json (the final
record's answer to each question, kept out of the sheet). Agreement is computed afterwards by
human_check_agreement.py from the filled sheet.

Questions and the record fields they mirror:
  Q1 diffusion and autoregressive side by side           -> any comparison group with both generators (RQ2_has_ar)
  Q2 (if Q1) a budget of both arms stated or matched      -> any such group with budget_across_arms matched/reported
  Q3 a contrast of training choices                       -> RQ3_has_training
  Q4 a contrast of inference settings                     -> RQ4_has_inference
  Q5 main comparison repeated over two or more runs       -> QA4 sub-item a
  Q6 a limitations section or paragraph                   -> QA9 sub-item a
"""
import json
import random
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "analysis/extraction/d0052"
RES = json.load(open(D / "rq-results.json", encoding="utf-8"))
sample = json.load(open(D / "sample.json", encoding="utf-8"))
UPD = ("G-long", "G-mm", "G-short")


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip().startswith("{")]


# final records as rq_analysis.py chooses them (EA pass 2 else pass 1; EC for the second-reader ids)
seed = json.load(open(D / "seed-sample.json", encoding="utf-8"))
recs = {}
for folder in sorted((D / "EA").glob("*")):
    fs = sorted(folder.glob("EA-*.jsonl"))
    p2 = [f for f in fs if f.stem.endswith("-pass2")]
    for f in (p2 or [f for f in fs if not f.stem.endswith("-pass2")]):
        for r in jl(f):
            recs[r["id"]] = r
for f in sorted((D / "EC").glob("*/*.jsonl")):
    for r in jl(f):
        if r["id"] in seed["second_reader_ids"]:
            recs[r["id"]] = r
left = set(RES["left_frame_D0059"])
frame = {h: sorted(i for i in sample["strata"][h][:20] if i in recs and i not in left) for h in UPD}
rng = random.Random(20261022)
drawn = [(h, i) for h in UPD for i in rng.sample(frame[h], 4)]


def ar(r):
    return [g for g in r.get("groups") or [] if not g.get("duplicate")
            and {"autoregressive", "diffusion"} <= {a.get("generator") for a in g.get("arms") or []}]


TRAIN = {"pretraining-recipe", "ar-initialisation", "sft", "rl", "distillation", "objective"}
INFER = {"steps-or-nfe", "tokens-per-step", "order-rule", "remasking", "cache", "block-or-parallel", "value-rule",
         "guidance", "gen-length"}


def yn(b):
    return "yes" if b else "no"


def answers(r):
    q = r.get("qa") or {}
    a = ar(r)
    ft = {g.get("factor_type") for g in r.get("groups") or [] if not g.get("duplicate")}
    return {"Q1": yn(a), "Q2": (yn(any(g.get("budget_across_arms") in ("matched", "reported") for g in a)) if a else "NA"),
            "Q3": yn(ft & TRAIN), "Q4": yn(ft & INFER),
            "Q5": ((q.get("QA4") or {}).get("sub") or {}).get("a"), "Q6": ((q.get("QA9") or {}).get("sub") or {}).get("a")}


titles = {}
for f in ("screening-queue-final-2026-10-15.jsonl", "screening-queue-2026-10-15.jsonl"):
    for l in open(ROOT / "research/review/corpus" / f, encoding="utf-8"):
        r = json.loads(l)
        titles.setdefault(r.get("id"), r.get("title") or "")
for l in open(ROOT / "analysis/screening/ta-recheck-candidates-v1.2.jsonl", encoding="utf-8"):
    r = json.loads(l)
    if r.get("title"):
        titles.setdefault(r.get("id"), r["title"])
links = {}
for r in jl(ROOT / "research/review/fulltext/fetch-log.jsonl"):
    if r.get("status") == "ok" and str(r.get("url", "")).startswith("http"):
        links.setdefault(r["id"], r["url"])
    elif r.get("status") == "ok" and str(r.get("url", "")).startswith("openreview note "):
        links.setdefault(r["id"], "https://openreview.net/forum?id=" + r["url"].split()[-1])

Q = {"Q1": "Does any results table or figure put a diffusion model and an autoregressive model side by side on the same task?",
     "Q2": "If Q1 is yes: for at least one such comparison, does the paper state the compute budget of both (steps, network calls, tokens per second, FLOPs or time), or say they are matched? (write NA if Q1 is no)",
     "Q3": "Does the paper compare two or more training choices in its own experiments (objective, pretraining recipe, fine-tuning, RL, distillation, initialisation)?",
     "Q4": "Does the paper compare inference settings in its own experiments (number of steps, tokens per step, guidance, decoding order, caching, block size, remasking)?",
     "Q5": "Is the paper's main comparison repeated over two or more runs or seeds?",
     "Q6": "Is there a limitations section or a paragraph on limitations?"}
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "check"
head = ["#", "Study id", "Title", "Link (open the PDF)"] + [f"{k}" for k in Q] + ["Notes"]
ws.append(head)
for c in ws[1]:
    c.font = Font(bold=True)
dv = DataValidation(type="list", formula1='"yes,no,unclear,NA"', allow_blank=True)
ws.add_data_validation(dv)
model = {}
for n, (h, i) in enumerate(drawn, 1):
    ws.append([n, i, titles.get(i, ""), links.get(i, "see research/sources/md/fulltext-pymupdf/" + i + ".txt")] + [""] * 6 + [""])
    for col in range(5, 11):
        dv.add(ws.cell(row=n + 1, column=col))
    model[i] = {"stratum": h, **answers(recs[i])}
ws.column_dimensions["C"].width = 60
ws.column_dimensions["D"].width = 45
qs = wb.create_sheet("questions")
qs.append(["Question", "Text"])
for k, v in Q.items():
    qs.append([k, v])
qs.column_dimensions["B"].width = 120
for row in qs.iter_rows():
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical="top")
out = ROOT / "research/HUMAN-CHECK-2026-10-21.xlsx"
wb.save(out)
(D / "human-check-model-answers.json").write_text(json.dumps({"seed": 20261022, "drawn": drawn, "answers": model,
                                                              "questions": Q}, indent=1), encoding="utf-8")
print(out, [i for _, i in drawn], "links missing:", [i for _, i in drawn if i not in links])
