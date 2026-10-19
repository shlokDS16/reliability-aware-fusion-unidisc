"""Counts per option for the meaning of "all multimodal" (EXTRACTION-PLAN-v0.4 s2.3, OPEN-QUESTIONS-v0.4 OQ4-03;
red-team audit 3, M2, m3, m4). The choice is the human author's; this script decides nothing.

Reproduces the v0.3 classification of strata.py (same files, same mm_final rule; asserts C1 53, NL 12, C2 108,
FR 435 on the T1 decisions file it reads) and then prints, per option, the sizes of C1, C2 (and C2b), frame R and
the records that get block K, with the block-K token range under scope Option 1 and Option 2 (per-record figures
copied from cost_options.py: EA-K 40-80k; all blocks by one extractor 78-135k; E0).

Inputs for the construct options (provisional; replaced by the human check of OQ4-04 when it exists):
  SIDE  = the 29 C2 records whose only non-text work is a separate image, audio or music model, as listed by the
          red-team from the screener notes (audit 2026-10-20-redteam-extraction-v0.3.md s3; evidence E1).
  JOINT = frame-R records that may put a D4 modality into or out of the model that produces text. Candidates are
          found deterministically in the body text (before the first line 'References'/'REFERENCES'/
          'Bibliography'): tier J-a = at least two distinct multimodal benchmark names; tier J-b = at least one
          multimodal benchmark name and one multimodal diffusion-LM name; tier J-c = a table caption (a line
          starting 'Table <n>' plus its next two lines) with a keyword of strata.py's KW list. Confirmed: M18118 (red-team E2, LLaDA-V
          on MathVista). Candidates are an upper bound, not a classification.
  If analysis/extraction/mm-construct.jsonl exists ({"id", "class": "joint"|"side-experiment"|"text", "by",
  "date"}, written after the human check), it replaces both provisional inputs.

Also prints (m3) the includes where screeners A and B agree on the decision but differ on i1 or nonlang_only (the
decisions file then carries A's value), and (m4) the split text/multimodal records that v0.3 decided by keyword.

Run from the worktree root: python -I analysis/extraction/multimodal_options.py
"""
import hashlib
import json
import os
import platform
import re
import sys
from pathlib import Path

ROOT = Path(".")
DEC = ROOT / "analysis/screening/ft-t1/t1-decisions-all.jsonl"
FT1 = ROOT / "analysis/screening/ft-t1"
CORPUS = [(ROOT / "research/review/corpus/new-records-2026-10-15-v2.jsonl", "nid"),
          (ROOT / "research/review/corpus/subscription-records-2026-10-15.jsonl", "id"),
          (ROOT / "research/review/screening/records.jsonl", "sid")]
TEXTS = ROOT / "research/sources/md/fulltext-pymupdf"
CONSTRUCT = ROOT / "analysis/extraction/mm-construct.jsonl"
KW_TERMS = [  # identical to strata.py
    "multimodal", "multi-modal", "cross-modal", "vision", "visual", "vision-language", "image", "images",
    "video", "videos", "audio", "speech", "spoken", "vlm", "vlms", "lvlm", "lvlms", "mllm", "mllms",
    "vqa", "caption", "captions", "captioning", "text-to-image", "image-to-text", "text-to-video",
    "text-to-speech", "ocr", "x-ray", "radiology", "sign language", "asr", "omni", "any-to-any", "3d",
]
KW = re.compile(r"(?<![\w-])(" + "|".join(re.escape(t) for t in KW_TERMS) + r")(?![\w-])", re.IGNORECASE)

SIDE = ["M00285", "M02955", "M04297", "M04350", "M04373", "M05608", "M05642", "M05663", "M06218", "M09321",
        "M10881", "M11247", "M12175", "M13247", "M13444", "M13674", "M14706", "M15373", "M15652", "M15895",
        "M16133", "M16251", "M16263", "M16730", "M16813", "M18406", "M18456", "M19099", "U04378"]
JOINT_CONFIRMED = ["M18118"]
MM_BENCH = ["MathVista", "MMMU", "MME", "VQAv2", "GQA", "TextVQA", "ChartQA", "DocVQA", "AI2D", "ScienceQA",
            "POPE", "SEED-Bench", "MMBench", "MMStar", "LibriSpeech", "Flickr30k", "NoCaps", "GenEval",
            "DPG-Bench", "MS-COCO", "COCO Caption"]
MM_DLM = ["LLaDA-V", "LaViDa", "Dimple", "MMaDA", "Lumina-DiMOO", "Muddit", "UniDisc", "FUDOKI", "D-DiT",
          "Show-o", "LLaDA-o", "Dream-VL", "DiffusionVL"]
RX_B = {t: re.compile(r"(?<![\w-])" + re.escape(t) + r"(?![\w-])") for t in MM_BENCH}
RX_D = {t: re.compile(r"(?<![\w-])" + re.escape(t) + r"(?![\w-])", re.IGNORECASE) for t in MM_DLM}
CAP = re.compile(r"^Table\s+[A-Z]?\d+[.:]?.*(?:\n.*){0,2}", re.MULTILINE)
REFS = re.compile(r"^(References|REFERENCES|Bibliography|BIBLIOGRAPHY)\s*$", re.MULTILINE)
EA_K, FULLREC, SAMPLE = (40, 80), (78, 135), 120


def jl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def sha(ids):
    return hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()


def body(i):
    t = (TEXTS / f"{i}.txt").read_text(encoding="utf-8", errors="replace")
    m = REFS.search(t)
    return t[:m.start()] if m else t


def mm_hits(i):
    b = body(i)
    caps = sorted({KW.search(c).group(0).lower() for c in CAP.findall(b) if KW.search(c)})
    return (sorted(t for t, r in RX_B.items() if r.search(b)), sorted(t for t, r in RX_D.items() if r.search(b)),
            caps)


def tok(x):
    return f"{x[0]:.1f}M-{x[1]:.1f}M"


def main():
    print(f"python {platform.python_version()}  decisions sha256 {hashlib.sha256(DEC.read_bytes()).hexdigest()}")
    dec = {r["id"]: r for r in jl(DEC)}
    inc = sorted(i for i, r in dec.items() if r["decision"] == "include")
    A, B, C = {}, {}, {}
    for d in sorted(FT1.glob("t1b0*")):
        for role, st in (("A", A), ("B", B)):
            for r in jl(d / f"F{role}-{d.name}.jsonl"):
                st[r["id"]] = r
    sup = {(r["id"], r["group"]) for r in jl(FT1 / "c-superseded.jsonl")}
    for f in sorted(FT1.glob("c/c-t1-*/FC-*.jsonl")):
        for r in jl(f):
            if (r["id"], f.parent.name) not in sup:
                C[r["id"]] = r
    meta = {}
    for path, key in CORPUS:
        for r in jl(path):
            i = r.get(key)
            if i in dec and i not in meta and (r.get("title") or "").strip():
                meta[i] = (r.get("title") or "") + " " + (r.get("abstract") or "")

    def mm_final(i):
        if i in C and C[i].get("mm"):
            return C[i]["mm"]
        ma, mb = A.get(i, {}).get("mm"), B.get(i, {}).get("mm")
        if ma and mb:
            return ma if ma == mb else "split:" + "/".join(sorted([ma, mb]))
        return ma or mb or "none"

    C1, NL, C2, FR, split_mm = [], [], [], [], []
    for i in inc:
        r = dec[i]
        if r["i1"] in ("b", "ab"):
            C1.append(i)
        elif r["nonlang_only"]:
            NL.append(i)
        else:
            m = mm_final(i)
            if m.startswith("split:") and "multimodal" in m:
                split_mm.append(i)
                is_mm = bool(KW.search(meta.get(i, "")))
            else:
                is_mm = m == "multimodal"
            (C2 if is_mm else FR).append(i)
    print(f"v0.3 rule reproduced: C1 {len(C1)}  NL {len(NL)}  C2 {len(C2)}  FR {len(FR)}  (C2 sha256 {sha(C2)[:16]}, FR {sha(FR)[:16]})")
    assert (len(C1), len(NL), len(C2), len(FR)) == (53, 12, 108, 435), "frame changed: rerun strata.py and revise"

    # ---- construct inputs ------------------------------------------------------------------------------
    if CONSTRUCT.exists():
        rows = {r["id"]: r["class"] for r in jl(CONSTRUCT)}
        side = sorted(i for i in C2 if rows.get(i) == "side-experiment")
        joint_lo = joint_hi = sorted(i for i in FR if rows.get(i) == "joint")
        print(f"construct file found ({len(rows)} rows): side {len(side)}, joint in FR {len(joint_lo)}")
        cand_a = cand_b = []
    else:
        side = sorted(SIDE)
        assert set(side) <= set(C2), sorted(set(side) - set(C2))
        hits = {i: mm_hits(i) for i in FR}
        cand_a = sorted(i for i in FR if len(hits[i][0]) >= 2)
        cand_b = sorted(i for i in FR if hits[i][0] and hits[i][1])
        cand_c = sorted(i for i in FR if hits[i][2])
        joint_hi = sorted(set(cand_a) | set(cand_b) | set(cand_c) | set(JOINT_CONFIRMED))
        joint_lo = sorted(JOINT_CONFIRMED)
        print("construct file absent: provisional inputs (SIDE from the red-team's screener-note reading, E1; "
              "JOINT candidates by full-text search)")
        print(f"  SIDE {len(side)} (all in C2): {' '.join(side)}")
        print(f"  JOINT candidates in frame R: tier J-a (>= 2 multimodal benchmarks) {len(cand_a)}; tier J-b "
              f"(benchmark + multimodal DLM name) {len(cand_b)}; tier J-c (keyword in a table caption) {len(cand_c)}; "
              f"union with confirmed {len(joint_hi)}")
        for i in joint_hi:
            print(f"    {i}: bench {hits[i][0]} | mm-DLM {hits[i][1]} | caption keywords {hits[i][2]}")
        h2 = {i: mm_hits(i) for i in C2}
        s_hit = sum(1 for i in side if h2[i][0] or h2[i][1])
        o_hit = sum(1 for i in C2 if i not in side and (h2[i][0] or h2[i][1]))
        print(f"  SIDE records with a hit: {[i for i in side if h2[i][0] or h2[i][1]]}")
        print(f"  cross-check in C2: records with any multimodal benchmark or DLM name in the body: SIDE {s_hit} of "
              f"{len(side)}; other C2 {o_hit} of {len(C2) - len(side)}")

    # ---- options -----------------------------------------------------------------------------------------
    S, Jl, Jh = len(side), len(joint_lo), len(joint_hi)
    opts = [
        ("(a) C1 only", 0, 0, (len(FR) + len(C2), len(FR) + len(C2))),
        ("(b) C1 + C2 by the mm rule (v0.3)", len(C2), 0, (len(FR), len(FR))),
        ("(c) joint-model rule; side-experiment records to frame R", None, 0, None),
        ("(d) joint-model rule; side-experiment records as a labelled C2b census", None, S, None),
    ]
    print("\n== Options for 'all multimodal' (counts; K records = C1 + C2 [+ C2b] + frame-R sample 120) ==")
    print("  option                                                  C1   C2 (range)   C2b  frame R (range)   "
          "K records (range)   block K, Option 1      all blocks, Option 2")
    for name, c2, c2b, fr in opts:
        if c2 is None:
            c2r = (len(C2) - S + Jl, len(C2) - S + Jh)
            frr = ((len(FR) + S - Jh, len(FR) + S - Jl) if c2b == 0 else (len(FR) - Jh, len(FR) - Jl))
        else:
            c2r, frr = (c2, c2), fr
        kr = (len(C1) + c2r[0] + c2b + SAMPLE, len(C1) + c2r[1] + c2b + SAMPLE)
        o1 = (kr[0] * EA_K[0] / 1000, kr[1] * EA_K[1] / 1000)
        o2 = (kr[0] * FULLREC[0] / 1000, kr[1] * FULLREC[1] / 1000)
        rng = lambda x: f"{x[0]}" if x[0] == x[1] else f"{x[0]}-{x[1]}"
        print(f"  {name:<55} {len(C1):3d}  {rng(c2r):<11}  {c2b:3d}  {rng(frr):<16}  {rng(kr):<18}  {tok(o1):<21}  {tok(o2)}")
    print("  (block K and all-blocks ranges multiply the K-record range by the per-record ranges; under Option 1 the"
          " light blocks are on all 608 includes whatever the option, so only block K changes)")

    # ---- m3: asymmetric i1 / nonlang_only -----------------------------------------------------------------
    asym = []
    for i in inc:
        if dec[i].get("source") != "A=B" or i not in A or i not in B:
            continue
        for f in ("i1", "nonlang_only"):
            va, vb = A[i].get(f), B[i].get(f)
            if va != vb:
                asym.append((i, f, va, vb, dec[i].get(f)))
    print(f"\n== m3: includes with A = B on the decision but A != B on i1 or nonlang_only ({len(asym)}) ==")
    for i, f, va, vb, vd in asym:
        print(f"  {i}: {f} A={va!r} B={vb!r} decisions file={vd!r}")

    # ---- m4: split records decided by keyword in v0.3 -------------------------------------------------------
    print(f"\n== m4: split text/multimodal records decided by the keyword rule in v0.3 ({len(split_mm)}); "
          f"v0.4 routes them to the human check (full text) ==")
    for i in split_mm:
        print(f"  {i}: mm {mm_final(i)}; v0.3 class {'C2' if i in C2 else 'FR'}")
    print(f"\nC1 sha256 {sha(C1)}\nC2 sha256 {sha(C2)}\nFR sha256 {sha(FR)}\nSIDE sha256 {sha(side)}")


if __name__ == "__main__":
    sys.exit(main())
