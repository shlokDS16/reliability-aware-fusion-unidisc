"""Rule-based selection of title/abstract exclusions that full-text criteria v1.2 might have passed.

Criteria v1.2 (research/review/screening/criteria-v1.2.md, section 5) is more inclusive than the
title/abstract rules (criteria-v1.md plus SCREENER-BRIEF.md) in seven classes. This script applies one
declared, deterministic query per class to every title/abstract exclusion:

  frame D1  round 1 (criteria v1): both screeners exclude    research/review/screening/screener-{A,B}/batch-*.jsonl
  frame D2  round 2 (D0028-D0030): both screeners exclude     research/review/screening/v2/screener-{A,B}-batch-*.jsonl
  frame R   rescue pass (D0029): single screener excludes     research/review/screening/v2/rescue/screener-R-rescue-*.jsonl

A record is a candidate if it matches at least one class query (on title + abstract, case-insensitive)
and carries the stated exclusion codes. No record is chosen by reading. If the candidate set is larger
than CAP, a simple random sample of SAMPLE_N is drawn with SEED and the estimate is made from it.

    python analysis/screening/ta_recheck_select.py

Writes analysis/screening/ta-recheck-v1.2.log and analysis/screening/ta-recheck-candidates-v1.2.jsonl
(orchestrator-only: holds title/abstract outcomes, never given to full-text screeners).
"""
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCR = ROOT / "research" / "review" / "screening"
OUT_LOG = ROOT / "analysis" / "screening" / "ta-recheck-v1.2.log"
OUT_JSONL = ROOT / "analysis" / "screening" / "ta-recheck-candidates-v1.2.jsonl"
CAP = 150
SAMPLE_N = 100
SEED = 20261016

I = re.IGNORECASE
DIFF = re.compile(r"diffus|denois|flow[- ]matching|rectified flow|masked generative|mask-predict|\bcmlm\b", I)
LANGW = re.compile(r"\blanguage|\btext|\bllms?\b|\bmllms?\b|\bvlms?\b|\bnlp\b|\bcode\b|\bsentence|\bword", I)
DD = re.compile(r"\b(discrete|masked|absorbing|uniform)[- ](state[- ])?(diffusion|denoising|flow)|discrete flow[- ]matching|masked generative|any[- ]order", I)
DOMAIN_TITLE = re.compile(
    r"protein|molecul|\bdna\b|\brna\b|peptide|antibod|drug|crystal|material|image|video|audio|speech|music|"
    r"graph|robot|policy|policies|driving|trajector|point cloud|mesh|medical|\bcell|genom|chemi|recommend|"
    r"tabular|time[- ]series|wireless|mimo|channel|routing|combinatorial|path finding|vehicle|antenna|"
    r"\bct\b|\bmri\b|weather|traffic|sketch|layout|font|motion|pose|scene", I)
SERVE = re.compile(r"serving|inference (engine|system|framework)|kv[- ]?cache|throughput|accelerat", I)
UNIF_OR_DLM = re.compile(r"any-to-any|\bomni|unified multimodal|unified multi-modal|diffusion language|\bdllms?\b|diffusion llm", I)
BODY3D = re.compile(r"\bmotion|\bpose\b|\bposes\b|gesture|humanoid|\bdance|avatar|\b3d\b|point cloud|\bmesh", I)
UNDERSTAND = re.compile(r"unified|understand|caption|any-to-any|\bomni|language model|\bllms?\b|\bmllms?\b", I)
TEXTOUT = re.compile(r"captioning|image-to-text|video-to-text|speech-to-text|speech recognition|\basr\b|\bocr\b|"
                     r"text recognition|transcription|machine translation|summari[sz]ation|question answering|"
                     r"text generation|slot filling", I)
JOINT = re.compile(r"unified|understanding and generation|any-to-any|\bomni", I)
JOINT2 = re.compile(r"jointly|joint training|end-to-end|co-train|trained together|shared (backbone|weights|transformer)", I)
NARMASK = re.compile(r"mask-predict|\bcmlm\b|conditional masked language model|iterative refinement|"
                     r"non-autoregressive|flow matching|rectified flow", I)


def english_abstract(ab):
    letters = [c for c in ab if c.isalpha()]
    if len(letters) < 200:
        return False
    ascii_share = sum(c.isascii() for c in letters) / len(letters)
    return ascii_share >= 0.9 and " the " in ab.lower() and " of " in ab.lower()


def classes(title, abstract, codes):
    t = title or ""
    a = abstract or ""
    ta = t + " " + a
    c = []
    if "X8" in codes and english_abstract(a):
        c.append("C1_language_body")                       # R2
    if codes & {"X0", "X1"} and DD.search(ta) and not DOMAIN_TITLE.search(t):
        c.append("C2_generic_discrete")                    # R8
    if "X7" in codes or (SERVE.search(ta) and UNIF_OR_DLM.search(ta)):
        c.append("C3_serving_or_application")              # R14
    if codes & {"X1", "X2"} and DIFF.search(ta) and BODY3D.search(ta) and UNDERSTAND.search(ta):
        c.append("C4_3d_body_unified")                     # R11
    if codes & {"X0", "X1", "X2"} and DIFF.search(ta) and TEXTOUT.search(ta):
        c.append("C5_text_output_task")                    # R6
    if codes & {"X1", "X2"} and DIFF.search(ta) and JOINT.search(ta) and JOINT2.search(ta) and LANGW.search(ta):
        c.append("C6_jointly_trained_unified")             # R10
    if "X0" in codes and NARMASK.search(ta) and LANGW.search(ta):
        c.append("C7_component_reading")                   # R4
    return c


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def frames():
    out = []
    # D1: round 1
    recs = {r["sid"]: r for r in load_jsonl(SCR / "records.jsonl")}
    dec = {"A": {}, "B": {}}
    for s in ("A", "B"):
        for p in sorted((SCR / f"screener-{s}").glob("batch-*.jsonl")):
            for r in load_jsonl(p):
                dec[s][r["sid"]] = (r.get("decision", ""), r.get("code", "") or "")
    for sid, r in recs.items():
        a, b = dec["A"].get(sid), dec["B"].get(sid)
        if a and b and a[0] == "exclude" and b[0] == "exclude":
            out.append(("D1", sid, r.get("title", ""), r.get("abstract", ""), {a[1], b[1]} - {""}, f"A:{a[1]} B:{b[1]}"))
    # D2: round 2
    recs = {}
    for p in sorted((SCR / "v2").glob("batch-*.jsonl")):
        for r in load_jsonl(p):
            recs[r["id"]] = r
    dec = {"A": {}, "B": {}}
    for s in ("A", "B"):
        for p in sorted((SCR / "v2").glob(f"screener-{s}-batch-*.jsonl")):
            for r in load_jsonl(p):
                dec[s][r["id"]] = (r["decision"], r.get("code", "") or "")
    for i, r in recs.items():
        a, b = dec["A"].get(i), dec["B"].get(i)
        if a and b and a[0] == "exclude" and b[0] == "exclude":
            out.append(("D2", i, r.get("title", ""), r.get("abstract", ""), {a[1], b[1]} - {""}, f"A:{a[1]} B:{b[1]}"))
    # R: rescue
    recs = {}
    for p in sorted((SCR / "v2" / "rescue").glob("rescue-*.jsonl")):
        for r in load_jsonl(p):
            recs[r["id"]] = r
    for p in sorted((SCR / "v2" / "rescue").glob("screener-R-rescue-*.jsonl")):
        for r in load_jsonl(p):
            if r["decision"] == "exclude" and r["id"] in recs:
                rr = recs[r["id"]]
                out.append(("R", r["id"], rr.get("title", ""), rr.get("abstract", ""), {r.get("code", "") or ""} - {""}, f"R:{r.get('code', '')}"))
    return out


def main():
    rows = frames()
    frame_n = Counter(f for f, *_ in rows)
    cands = []
    for f, i, t, a, codes, ta in rows:
        c = classes(t, a, codes)
        if c:
            cands.append({"id": i, "frame": f, "classes": c, "ta_codes": ta, "title": t})
    cands.sort(key=lambda r: (r["frame"], r["id"]))
    by_frame = Counter(r["frame"] for r in cands)
    by_class = Counter(c for r in cands for c in r["classes"])
    by_class_frame = Counter((c, r["frame"]) for r in cands for c in r["classes"])
    sample = []
    if len(cands) > CAP:
        rng = random.Random(SEED)
        sample = sorted(rng.sample([r["id"] for r in cands], SAMPLE_N))
    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for r in cands:
            r["in_sample"] = (r["id"] in sample) if sample else True
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    digest = hashlib.sha256(OUT_JSONL.read_bytes()).hexdigest()
    lines = [
        "ta_recheck_select.py (criteria v1.2 section 5)",
        f"exclusions in frame: {dict(sorted(frame_n.items()))} total {sum(frame_n.values())}",
        f"candidates: {len(cands)}  by frame {dict(sorted(by_frame.items()))}",
        "by class (a record may match several):",
    ]
    for c in sorted(by_class):
        lines.append(f"  {c}: {by_class[c]}  " + " ".join(f"{fr}={by_class_frame[(c, fr)]}" for fr in ("D1", "D2", "R")))
    if sample:
        lines.append(f"candidates > CAP {CAP}: simple random sample of {SAMPLE_N}, seed {SEED}")
        lines.append("sample ids: " + " ".join(sample))
    else:
        lines.append(f"candidates <= CAP {CAP}: all candidates go to the re-check")
    lines.append(f"candidates file sha256: {digest}")
    OUT_LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:-2] if sample else lines))


if __name__ == "__main__":
    main()
