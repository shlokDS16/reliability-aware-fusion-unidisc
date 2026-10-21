"""Blind human check of the full-text screening of tranche T1 (Paper 1; second of three human checks).

    python -E -P analysis/screening/human_check_screening_sheet.py      (openpyxl is a user-site package)

Frame: the final T1 full-text decisions = analysis/screening/ft-t1/t1-decisions-all.jsonl (882 rows, A=B or
adjudicator C) plus the three T1 records of b-unavailable-resolved.jsonl (D0058, exclude X1), with the D0059
code overrides of d0039-resolved.jsonl applied (885 records). Records the first author has already seen with
their decision are left out of the frame, because they cannot be judged blind: the D0058/D0059 items
(research/CONFIRM-2026-10-20.md), the items of research/AUTHOR-CHECKS-2026-10-21.md and the 12 studies of the
extraction check (analysis/extraction/d0052/human-check-model-answers.json, ids only).

Draw: random.Random(20261023); 20 of the sorted included ids, then 20 of the sorted excluded ids, then the 40
are shuffled with the same generator for the row order.

Writes research/HUMAN-CHECK-SCREENING.xlsx (sheet "check": no model decision shown; sheet "rules": criteria v1.6
in plain language) and analysis/screening/human-check-screening-model-answers.json (the final decision and code
per drawn record; the human reader must not open it before finishing). Refuses to overwrite either file.
Agreement: human_check_screening_agreement.py.
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
S = ROOT / "analysis/screening"
SEED = 20261023
OUT_X = ROOT / "research/HUMAN-CHECK-SCREENING.xlsx"
OUT_M = S / "human-check-screening-model-answers.json"
TXT = ROOT / "research/sources/md/fulltext-pymupdf"
CODES = ["X8", "X3", "X5", "X4", "X0", "X1", "X2", "X7"]

for p in (OUT_X, OUT_M):
    if p.exists():
        raise SystemExit(f"{p} exists: the draw is frozen")


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip().startswith("{")]


# final decisions
final = {}
for r in jl(S / "ft-t1/t1-decisions-all.jsonl"):
    final[r["id"]] = {"decision": r["decision"], "code": r["code"], "xsub": r.get("xsub", ""), "i1": r.get("i1", ""),
                      "nonlang_only": r.get("nonlang_only", False), "source": r["source"], "decision_rows": []}
for r in jl(S / "b-unavailable-resolved.jsonl"):
    if r["tranche"] == "T1":
        assert r["id"] not in final
        final[r["id"]] = {"decision": r["decision"], "code": r["code"], "xsub": "", "i1": "", "nonlang_only": False,
                          "source": "A, confirmed by the first author", "decision_rows": [r["decision_row"]]}
for r in jl(S / "d0039-resolved.jsonl"):
    if r["id"] in final:
        final[r["id"]][r["field"]] = r["value"]
        final[r["id"]]["decision_rows"].append(r["decision_row"])
n_inc = sum(v["decision"] == "include" for v in final.values())
n_exc = sum(v["decision"] == "exclude" for v in final.values())
assert (len(final), n_inc, n_exc) == (885, 608, 277), (len(final), n_inc, n_exc)

# records already seen by the first author with their decision
seen_src = {"research/CONFIRM-2026-10-20.md": None, "research/AUTHOR-CHECKS-2026-10-21.md": None}
seen = set()
for f in seen_src:
    ids = set(re.findall(r"\b[MRU]\d{4,5}\b", (ROOT / f).read_text(encoding="utf-8")))
    seen_src[f] = sorted(ids & set(final))
    seen |= ids
ex = json.load(open(ROOT / "analysis/extraction/d0052/human-check-model-answers.json", encoding="utf-8"))
seen_src["analysis/extraction/d0052/human-check-model-answers.json (drawn ids)"] = sorted({i for _, i in ex["drawn"]} & set(final))
seen |= {i for _, i in ex["drawn"]}
left_out = sorted(seen & set(final))

inc = sorted(i for i, v in final.items() if v["decision"] == "include" and i not in seen)
exc = sorted(i for i, v in final.items() if v["decision"] == "exclude" and i not in seen)
rng = random.Random(SEED)
d_inc = rng.sample(inc, 20)
d_exc = rng.sample(exc, 20)
order = rng.sample(d_inc + d_exc, 40)

# titles, links, DOIs
titles, dois = {}, {}
for f in ("screening-queue-final-2026-10-15.jsonl", "screening-queue-2026-10-15.jsonl"):
    for r in jl(ROOT / "research/review/corpus" / f):
        if r.get("title"):
            titles.setdefault(r["id"], r["title"])
        if r.get("doi"):
            dois.setdefault(r["id"], r["doi"])
for r in jl(S / "ta-recheck-candidates-v1.2.jsonl"):
    if r.get("title"):
        titles.setdefault(r["id"], r["title"])
for r in jl(ROOT / "research/review/fulltext/ft-routes.jsonl"):
    if r.get("title"):
        titles.setdefault(r["id"], r["title"])
    if r.get("doi"):
        dois.setdefault(r["id"], r["doi"])
log = jl(ROOT / "research/review/fulltext/fetch-log.jsonl")
wrong = {(r["id"], r.get("url")) for r in log if r.get("status") == "wrong_pdf"}
links = {}
for r in log:  # last usable ok row wins
    u = str(r.get("url") or "")
    if r.get("status") != "ok" or (r["id"], u) in wrong:
        continue
    if u.startswith("http"):
        links[r["id"]] = u
    elif u.startswith("openreview note "):
        links[r["id"]] = "https://openreview.net/forum?id=" + u.split()[-1]


def link(i):
    if i in links:
        return links[i], "fetch-log"
    if i in dois:
        d = re.sub(r"^https?://(dx\.)?doi\.org/", "", dois[i])
        return "https://doi.org/" + d, "doi"
    return "", "none"


# sheet "check"
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "check"
head = ["#", "Record id", "Title", "Link", "Local text copy", "Decision", "Exclusion code", "Reader", "Notes"]
ws.append(head)
hdr_fill = PatternFill("solid", fgColor="DDEBF7")
for c in ws[1]:
    c.font = Font(bold=True)
    c.fill = hdr_fill
    c.alignment = Alignment(vertical="top", wrap_text=True)
dv_dec = DataValidation(type="list", formula1='"include,exclude,unclear"', allow_blank=True,
                        showErrorMessage=True, errorTitle="Decision", error="Pick include, exclude or unclear.")
dv_code = DataValidation(type="list", formula1='"' + ",".join(CODES) + '"', allow_blank=True,
                         showErrorMessage=True, errorTitle="Exclusion code",
                         error="Pick one of X8, X3, X5, X4, X0, X1, X2, X7, or leave blank.")
dv_dec.promptTitle, dv_dec.prompt, dv_dec.showInputMessage = "Decision", "include / exclude / unclear", True
dv_code.promptTitle, dv_code.prompt, dv_code.showInputMessage = "Exclusion code", "Only for exclude: first code that applies (sheet rules)", True
ws.add_data_validation(dv_dec)
ws.add_data_validation(dv_code)
rows, problems = [], []
for n, i in enumerate(order, 1):
    url, how = link(i)
    txt = TXT / f"{i}.txt"
    if not txt.exists() or txt.stat().st_size == 0:
        problems.append(f"{i}: local text missing or empty")
    if not titles.get(i):
        problems.append(f"{i}: no title")
    local = str(txt)
    ws.append([n, i, titles.get(i, ""), url, local, "", "", "", ""])
    r = n + 1
    if url:
        ws.cell(row=r, column=4).hyperlink = url
        ws.cell(row=r, column=4).style = "Hyperlink"
    ws.cell(row=r, column=5).hyperlink = txt.as_uri()
    ws.cell(row=r, column=5).style = "Hyperlink"
    dv_dec.add(ws.cell(row=r, column=6))
    dv_code.add(ws.cell(row=r, column=7))
    for col in (1, 2, 3, 6, 7, 8, 9):
        ws.cell(row=r, column=col).alignment = Alignment(vertical="top", wrap_text=col in (3, 9))
    rows.append({"row": n, "id": i, "link": url, "link_source": how, "local_text": local})
for col, w in zip("ABCDEFGHI", (5, 10, 60, 42, 40, 12, 15, 9, 40)):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "C2"
if problems:
    raise SystemExit("problems: " + "; ".join(problems))

# sheet "rules" (criteria v1.6 screener copy, sections A-C and R9, and protocol section 2 I1-I4)
R = wb.create_sheet("rules")
RULES = [
    ("HOW TO DECIDE", "Full-text screening rules v1.6 in plain language (normative text: research/review/screening/criteria-v1.6-screener.md; eligibility I1-I4: research/review/protocol.md section 2). Judge from the paper itself (text, figures, tables, appendix), not from its title or the model's name."),
    ("INCLUDE only if all four hold", ""),
    ("I1 Topic", "(a) A diffusion component of the paper's own method produces TEXT as the final output in at least one result (table, figure or sample); or (b) ONE unified model (shared weights or one jointly trained system, not a pipeline of separately trained models) that both understands (writes text from an image, video, audio/speech or 3D input) and generates image, video, audio/speech or 3D with a diffusion, masked-generative or discrete-flow component (its text may be autoregressive). The word \"unified\", \"omni\" or \"any-to-any\" alone does not count."),
    ("I2 Primary study", "The paper has a method, theory or empirical result of its own."),
    ("I3 English", "The main body (method and results) is in English, whatever the language of the title or abstract."),
    ("I4 Date", "First public version from 2021-01-01 to the search date."),
    ("Text means", "Words or sentences of a human language of any length (answers, labels written as words, captions, transcripts, translations, reasoning, maths solutions in words), or source code, queries, markup or formal proofs. NOT text: SMILES, protein/DNA/RNA sequences, puzzle grids and moves, numbers or equations alone, class ids, tags, span positions, robot actions or trajectories, pixels (also words drawn in an image), audio tokens, embeddings."),
    ("Diffusion means", "Trained to undo corruption at a range of levels (masking at a varying rate, token-substitution noise, Gaussian noise on embeddings or latents, or a flow-matching path) and generates in more than one step (or with a few-step sampler distilled from such a model). A masked language model at one fixed masking rate with one-pass prediction is not diffusion. Diffusion in the sense of spread (information, heat), cryptography, graph kernels or imaging is not."),
    ("Own method", "What the paper says it contributes (introduction). If the contribution is an evaluation or benchmark, the models it evaluates are its own method. Baselines are not: a paper with diffusion models only as baselines is X0."),
    ("Special cases", "A paper that generates with a diffusion model already pretrained on text (it loads such weights, e.g. a diffusion LLM) is included if it fine-tunes it as a generator, changes its sampler, decoding, caching, schedule, remasking or guidance, compares it with another generator on the same task, or varies steps, unmasking order, remasking or block length in a results table, even when its outputs are only non-language strings (not robot actions, not images or speech); otherwise X7. A paper whose final model does not generate (encoder, scorer, classifier) is included if it trains a diffusion component on text, reports results on a text diffusion model's likelihoods, internals, outputs or robustness, or compares a text diffusion backbone with a non-diffusion one."),
    ("EXCLUDE: pick the FIRST code that applies, in this order", ""),
    ("X8", "First public version before 2021 (or after the search date), or main body not in English."),
    ("X3", "Secondary study: survey, review, tutorial, position or perspective (also one proposing a taxonomy or framework) with no new experiment or proof of its own. A survey that runs its own experiments is primary."),
    ("X5", "Another report of a study already in the review (revision, extension or published version: same method or benchmark name and at least one shared author). Normally set by script; use it only if you notice it."),
    ("X4", "No method, theory or empirical result: abstract only, poster, slides, demo, blog, editorial."),
    ("X0", "No diffusion component in the paper's own method (diffusion only as baselines counts as X0)."),
    ("X1", "The diffusion output is not text, the paper is not a unified model (I1 b), and the X1/X2 steps below give X1."),
    ("X2", "The diffusion output is not text, the paper is not a unified model (I1 b), and the X1/X2 steps below give X2."),
    ("X7", "A text diffusion model or unified model used unchanged, with no finding about the model itself (for example an off-the-shelf model used only as a tool)."),
    ("X1 or X2: take the first step that applies", ""),
    ("Step 1 -> X1", "The system writes its text with an autoregressive model, and its diffusion part generates only robot actions, trajectories, molecules or another output that is not image, video, audio/speech or 3D. X1 even when the text or instruction conditions the diffusion part."),
    ("Step 2 -> X2", "The paper states anywhere (also in the appendix) that text conditions the diffusion part: directly, through a text encoder, or through an LLM, VLM or MLLM, frozen or trained; written by a person or by another component (prompt, caption, instruction, plan, transcript, lyrics, source sentence, program). Text plus other conditions is still X2. Class labels and category ids are not text."),
    ("Step 3 -> X1", "Everything else, including when the paper does not say that text reaches the diffusion part."),
    ("Unclear", "Use 'unclear' only if you cannot decide after reading; say why in Notes. Leave the code blank for include and unclear."),
]
R.column_dimensions["A"].width = 30
R.column_dimensions["B"].width = 150
sec_fill = PatternFill("solid", fgColor="DDEBF7")
for a, b in RULES:
    R.append([a, b])
    r = R.max_row
    R.cell(row=r, column=1).font = Font(bold=True)
    for c in (1, 2):
        R.cell(row=r, column=c).alignment = Alignment(wrap_text=True, vertical="top")
    if not b:
        R.cell(row=r, column=1).fill = sec_fill
        R.cell(row=r, column=2).fill = sec_fill
    else:
        R.row_dimensions[r].height = 15 * max(1, -(-len(b) // 150))
wb.save(OUT_X)

frame = inc + exc
OUT_M.write_text(json.dumps({
    "purpose": "model answers for the blind human screening check; do not open before the sheet is filled",
    "script": "analysis/screening/human_check_screening_sheet.py", "seed": SEED,
    "final_decisions": "t1-decisions-all.jsonl (882) + b-unavailable-resolved.jsonl T1 (3, D0058) + d0039-resolved.jsonl overrides (D0059)",
    "final_counts": {"records": len(final), "include": n_inc, "exclude": n_exc},
    "left_out_already_seen": {"n": len(left_out), "ids": left_out, "sources": seen_src},
    "frame_counts": {"include": len(inc), "exclude": len(exc)},
    "frame_sha256": hashlib.sha256("\n".join(frame).encode()).hexdigest(),
    "rule": "rng=random.Random(seed); rng.sample(sorted include, 20); rng.sample(sorted exclude, 20); rng.sample(both, 40) = row order",
    "drawn": {"include": d_inc, "exclude": d_exc}, "rows": rows,
    "answers": {i: final[i] for i in order}}, indent=1), encoding="utf-8")
print(OUT_X)
print("frame include/exclude:", len(inc), len(exc), "left out:", len(left_out))
print("links:", {k: sum(r["link_source"] == k for r in rows) for k in ("fetch-log", "doi", "none")})
