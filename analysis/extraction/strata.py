"""Frames, strata and the multimodal rule for Paper 1 extraction (form v0.3, EXTRACTION-PLAN-v0.3 s2).

Deterministic; reads only files that exist before any extraction. Prints counts, every borderline id,
the classification of every record the red-team named (audit 2026-10-20, F-MA5), duplicate-work
candidates, the frame-R strata and allocation, and sha256 values of the sorted id lists. It draws
nothing: the draws are made by draw_rq_sample.py / draw_pilot.py after their preconditions (plan s14).

Run from the worktree root:
    python -I analysis/extraction/strata.py [--n-sample 120] [--gate-n 45] [--no-dedup]

Multimodal rule (plan s2.3), in this order:
  1. C1 = T1 include with i1 in {b, ab}.
  2. mm_final = the screening field "mm" ("text" | "multimodal" | "other", criteria v1.6 screener
     brief: "multimodal" = takes or generates a D4 modality: image, video, audio or speech, 3D) of
     the adjudicator C row when C ruled the record and wrote mm; else the common value of screeners
     A and B when they agree; else, if only one of A and B wrote mm, that value; else "split".
  3. C2 = i1 = a, nonlang_only false, and mm_final = "multimodal"; a "split" record with one
     screener saying "multimodal" is C2 iff the keyword rule (KW) hits its title or abstract.
  4. Overrides: analysis/extraction/strata-overrides.jsonl rows {"id", "mm", "reason", "by", "date"},
     applied last and printed (file absent = no overrides).
  KW is a cross-check, not the definition, except for case 3's split records. Borderline ids:
    B1 split text/multimodal (decided by KW);  B2 mm_final multimodal but no KW hit in title or
    abstract;  B3 mm_final text or other but a KW hit in the title.
"""
import argparse
import hashlib
import json
import os
import platform
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(".")
DEC = ROOT / "analysis/screening/ft-t1/t1-decisions-all.jsonl"
FT1 = ROOT / "analysis/screening/ft-t1"
CORPUS = [  # (file, id key); first file that has a non-empty title wins
    (ROOT / "research/review/corpus/new-records-2026-10-15-v2.jsonl", "nid"),
    (ROOT / "research/review/corpus/subscription-records-2026-10-15.jsonl", "id"),
    (ROOT / "research/review/screening/records.jsonl", "sid"),
]
TEXTS = ROOT / "research/sources/md/fulltext-pymupdf"
OVERRIDES = ROOT / "analysis/extraction/strata-overrides.jsonl"

# Keyword list KW (case-insensitive, whole words; '-' and spaces inside a term are literal).
KW_TERMS = [
    "multimodal", "multi-modal", "cross-modal", "vision", "visual", "vision-language", "image", "images",
    "video", "videos", "audio", "speech", "spoken", "vlm", "vlms", "lvlm", "lvlms", "mllm", "mllms",
    "vqa", "caption", "captions", "captioning", "text-to-image", "image-to-text", "text-to-video",
    "text-to-speech", "ocr", "x-ray", "radiology", "sign language", "asr", "omni", "any-to-any", "3d",
]
KW = re.compile(r"(?<![\w-])(" + "|".join(re.escape(t) for t in KW_TERMS) + r")(?![\w-])", re.IGNORECASE)
OLD_C2 = re.compile(r"multi-?modal|vision|visual|image|video|audio|speech|\bVLM|MLLM|\bVQA", re.IGNORECASE)  # v0.2, retired
ANON = re.compile(r"Anonymous [Aa]uthors?")
NAMED = ["M06241", "M08240", "M09491", "M19267", "M13756", "M04245", "M15668", "M10855", "M16229",
         "M09298", "M08804", "M14667", "M01397", "M16622", "M13760", "M15684", "R0963"]


def sha(ids):
    return hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()


def jl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def norm_title(t):
    t = re.sub(r"[^a-z0-9 ]", " ", (t or "").lower())
    return re.sub(r"\s+", " ", t).strip()


def largest_remainder(sizes, n):
    tot = sum(sizes.values())
    quota = {k: n * v / tot for k, v in sizes.items()}
    alloc = {k: int(q) for k, q in quota.items()}
    rest = n - sum(alloc.values())
    for k in sorted(quota, key=lambda k: (-(quota[k] - alloc[k]), k))[:rest]:
        alloc[k] += 1
    return alloc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-sample", type=int, default=120)
    ap.add_argument("--gate-n", type=int, default=45)
    ap.add_argument("--no-dedup", action="store_true")
    a = ap.parse_args()

    print(f"python {platform.python_version()}  decisions sha256 {hashlib.sha256(DEC.read_bytes()).hexdigest()}")
    dec = {r["id"]: r for r in jl(DEC)}
    inc = sorted(i for i, r in dec.items() if r["decision"] == "include")
    print(f"T1 rows {len(dec)}, includes {len(inc)}")

    # screener rows: canonical FA/FB files per batch (DISCARDED copies ignored), C rows minus superseded
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
    pend = [r["id"] for r in jl(FT1 / "t1-pending-B.jsonl")] if (FT1 / "t1-pending-B.jsonl").exists() else []

    # titles and abstracts
    meta = {}
    for path, key in CORPUS:
        for r in jl(path):
            i = r.get(key)
            if i in dec and i not in meta and (r.get("title") or "").strip():
                meta[i] = {"title": r.get("title") or "", "abstract": r.get("abstract") or "", "src": path.name}
    miss_t = [i for i in inc if i not in meta]
    miss_a = [i for i in inc if i in meta and not meta[i]["abstract"].strip()]
    print(f"titles found {len(inc) - len(miss_t)} of {len(inc)}; missing title: {miss_t}; no abstract: {miss_a}")

    def mm_final(i):
        if i in C and C[i].get("mm"):
            return C[i]["mm"], "C"
        ma, mb = A.get(i, {}).get("mm"), B.get(i, {}).get("mm")
        if ma and mb:
            return (ma, "A=B") if ma == mb else ("split:" + "/".join(sorted([ma, mb])), "split")
        if ma or mb:
            return (ma or mb), "single"
        return "none", "none"

    over = {r["id"]: r for r in jl(OVERRIDES)} if OVERRIDES.exists() else {}
    rec = {}
    for i in inc:
        r = dec[i]
        m, src = mm_final(i)
        t, ab = meta.get(i, {}).get("title", ""), meta.get(i, {}).get("abstract", "")
        kt, ka = bool(KW.search(t)), bool(KW.search(ab))
        rec[i] = dict(i1=r["i1"], nl=bool(r["nonlang_only"]), mm=m, mmsrc=src, kw_title=kt, kw_abs=ka, title=t,
                      old_c2=bool(OLD_C2.search(t)))

    C1, NL, C2, FR = [], [], [], []
    B1, B2, B3, kw_abs_only = [], [], [], []
    for i in inc:
        x = rec[i]
        if x["i1"] in ("b", "ab"):
            C1.append(i)
            continue
        if x["nl"]:
            NL.append(i)
            continue
        m = x["mm"]
        if m.startswith("split:") and "multimodal" in m:
            mmc = x["kw_title"] or x["kw_abs"]
            B1.append(i)
        else:
            mmc = (m == "multimodal")
        if i in over:
            mmc = over[i]["mm"] == "multimodal"
        if mmc and not (x["kw_title"] or x["kw_abs"]):
            B2.append(i)
        if not mmc and x["kw_title"]:
            B3.append(i)
        if not mmc and not x["kw_title"] and x["kw_abs"]:
            kw_abs_only.append(i)
        (C2 if mmc else FR).append(i)
        x["c2"] = mmc

    print("\n== mm_final over i1 = a, not nonlang_only includes ==")
    cnt = Counter((rec[i]["mm"], rec[i]["mmsrc"]) for i in inc if rec[i]["i1"] == "a" and not rec[i]["nl"])
    for k, v in sorted(cnt.items(), key=lambda kv: -kv[1]):
        print(f"  {v:4d}  mm={k[0]:<22} source={k[1]}")
    print(f"\nC1 {len(C1)}  NL {len(NL)}  C2(rule) {len(C2)}  FR {len(FR)}  sum {len(C1)+len(NL)+len(C2)+len(FR)}")
    old = [i for i in inc if rec[i]["i1"] == "a" and not rec[i]["nl"] and rec[i]["old_c2"]]
    print(f"v0.2 title-regex C2 would be {len(old)}; cross-tab (old C2 x new C2): "
          f"both {len(set(old) & set(C2))}, old only {sorted(set(old) - set(C2))}, new only {len(set(C2) - set(old))}")
    print(f"\nBorderline B1 (split text/multimodal, decided by KW) {len(B1)}: "
          + ", ".join(f"{i}[{rec[i]['mm']};kw={'y' if rec[i]['kw_title'] or rec[i]['kw_abs'] else 'n'}]" for i in B1))
    print(f"Borderline B2 (mm multimodal, no KW hit in title or abstract) {len(B2)}: {B2}")
    print(f"Borderline B3 (mm text/other, KW hit in title) {len(B3)}: "
          + ", ".join(f"{i}[{rec[i]['mm']}]" for i in B3))
    print(f"Not borderline, listed for transparency: mm text/other with a KW hit in the abstract only {len(kw_abs_only)}: {kw_abs_only}")
    print(f"Overrides applied {len(over)}: {sorted(over)}")
    if pend:
        print(f"T1 pending (B unavailable) {len(pend)}: {pend} -> classified by the same rule if they become includes")

    print("\n== Records named by the red-team (F-MA5) ==")
    for i in NAMED:
        x = rec.get(i)
        if not x:
            print(f"  {i}: not a T1 include")
            continue
        cls = "C1" if i in C1 else "NL" if i in NL else "C2" if i in C2 else "FR"
        print(f"  {i}: i1={x['i1']} mm={x['mm']} ({x['mmsrc']}) kw_title={x['kw_title']} kw_abs={x['kw_abs']} "
              f"v0.2-regex={'C2' if x['old_c2'] and x['i1']=='a' and not x['nl'] else '-'} -> {cls} | {x['title'][:70]}")

    # duplicate works (F-mi10). Candidates: (a) the shorter normalised title (>= 3 words) is a word-boundary
    # prefix of the longer; (b) word-set Jaccard >= 0.7; (c) difflib ratio >= 0.9. Candidates are only printed.
    # A pair is applied (second id removed from the frames, linked to the first as a report of the same
    # study) only if it is listed in analysis/extraction/duplicate-works.jsonl ({"keep", "drop", "by", "date"}),
    # which a human writes after checking the candidates (plan s14 precondition A6).
    import difflib
    dups = []
    nt = {i: norm_title(rec[i]["title"]) for i in inc if rec[i]["title"]}
    ids = sorted(nt)
    for p in range(len(ids)):
        for q in range(p + 1, len(ids)):
            s, t = nt[ids[p]], nt[ids[q]]
            sh, lo = (s, t) if len(s) <= len(t) else (t, s)
            ws, wt = set(s.split()), set(t.split())
            why = []
            if len(sh.split()) >= 3 and (lo == sh or lo.startswith(sh + " ")):
                why.append("prefix")
            if ws and wt and len(ws & wt) / len(ws | wt) >= 0.7:
                why.append("jaccard")
            if difflib.SequenceMatcher(None, s, t).ratio() >= 0.9:
                why.append("ratio")
            if why:
                dups.append((ids[p], ids[q], "+".join(why)))
    print(f"\n== Duplicate-work candidates {len(dups)} (checked by a human before the draw; none applied unless listed) ==")
    for p, q, why in dups:
        print(f"  {p} | {q} | {why} | {rec[p]['title'][:55]} || {rec[q]['title'][:55]}")
    conf = jl(ROOT / "analysis/extraction/duplicate-works.jsonl") if (ROOT / "analysis/extraction/duplicate-works.jsonl").exists() else []
    drop = set() if a.no_dedup else {r["drop"] for r in conf}
    FRd = [i for i in FR if i not in drop]
    C2d = [i for i in C2 if i not in drop]
    C1d = [i for i in C1 if i not in drop]
    print(f"dedup {'off' if a.no_dedup else 'on'}: removed from frames {sorted(drop)}; C1 {len(C1d)} C2 {len(C2d)} FR {len(FRd)}")

    # strata of frame R
    size = {i: os.path.getsize(TEXTS / f"{i}.txt") for i in inc}
    anon = {}
    for i in inc:
        with open(TEXTS / f"{i}.txt", encoding="utf-8", errors="replace") as f:
            anon[i] = bool(ANON.search(f.read(6000)))
    srt = sorted(size[i] for i in FRd)
    med = srt[len(srt) // 2] if len(srt) % 2 else (srt[len(srt) // 2 - 1] + srt[len(srt) // 2]) / 2
    strata = {"anon-long": [], "anon-short": [], "named-long": [], "named-short": []}
    for i in FRd:
        strata[("anon" if anon[i] else "named") + "-" + ("long" if size[i] > med else "short")].append(i)
    alloc = largest_remainder({k: len(v) for k, v in strata.items()}, a.n_sample)
    print(f"\n== Frame R strata (median size {med:,.0f} bytes), n = {a.n_sample}, largest remainder ==")
    for k, v in strata.items():
        print(f"  {k:<12} N_h {len(v):4d}  n_h {alloc[k]:3d}  weight {len(v)/alloc[k]:.3f}  sha256 {sha(v)[:16]}")
    w = [len(v) / alloc[k] for k, v in strata.items() for _ in range(alloc[k])] + [1.0] * (len(C1d) + len(C2d))
    deff = len(w) * sum(x * x for x in w) / sum(w) ** 2
    print(f"  records with block K: C1 {len(C1d)} + C2 {len(C2d)} + sample {a.n_sample} = {len(C1d)+len(C2d)+a.n_sample}; "
          f"Kish deff over C1+C2+sample {deff:.2f} (effective n {len(w)/deff:.0f})")
    print(f"  anonymous among includes {sum(anon[i] for i in inc)} (C1 {sum(anon[i] for i in C1d)}, C2 {sum(anon[i] for i in C2d)}, "
          f"NL {sum(anon[i] for i in NL)}, FR {sum(anon[i] for i in FRd)}); texts above 133,280 bytes in FR+C2: "
          f"{sum(size[i] > 133280 for i in FRd + C2d)}")
    # 95% half-width of a study-level share over frame R (normal approximation, finite-population correction)
    print("  precision over frame R (N = %d), p = 0.5:  n   whole frame   subgroup at 50%%   at 30%%   at 20%%" % len(FRd))
    for nn in (90, 120, 150):
        hw = []
        for prev in (1.0, 0.5, 0.3, 0.2):
            m, N = nn * prev, len(FRd) * prev
            hw.append(1.96 * (0.25 / m * (1 - (m - 1) / (N - 1))) ** 0.5)
        print("                                            %3d   %.3f         %.3f            %.3f     %.3f" % ((nn,) + tuple(hw)))

    # pilot pools (plan s10): Stage A pools; Stage B gate strata (three equal strata of gate_n / 3)
    pool_ba = [i for i in FRd if re.search(r"benchmark|evaluat|analy[sz]|empirical|revisit|rethink|investigat|probing|understanding", rec[i]["title"], re.I)]
    rc2 = FRd + C2d
    srt2 = sorted(size[i] for i in rc2)
    med2 = (srt2[len(srt2) // 2 - 1] + srt2[len(srt2) // 2]) / 2 if len(srt2) % 2 == 0 else srt2[len(srt2) // 2]
    g_short = [i for i in rc2 if size[i] <= med2]
    g_long = [i for i in rc2 if size[i] > med2]
    print(f"\n== Pilot pools ==\n  Stage A: C1 i1=ab {sum(rec[i]['i1']=='ab' for i in C1d)}, C1 i1=b {sum(rec[i]['i1']=='b' for i in C1d)}, "
          f"FR benchmark/analysis-title pool {len(pool_ba)}, FR+C2 above 133,280 bytes {sum(size[i] > 133280 for i in rc2)}, FR {len(FRd)}")
    print(f"  Stage B (gate n {a.gate_n} = 3 x {a.gate_n // 3}): G-short {len(g_short)} and G-long {len(g_long)} from FR+C2 "
          f"({len(rc2)}, median {med2:,.0f} bytes); G-mm from C1 {len(C1d)}")

    print("\n== sha256 of newline-joined sorted id lists ==")
    for name, v in (("C1", C1d), ("C2", C2d), ("NL", NL), ("FR", FRd), ("B1", B1), ("B2", B2), ("B3", B3)):
        print(f"  {name:<3} {len(v):4d}  {sha(v)}")
    print("\nC2 ids:", " ".join(sorted(C2d)))


if __name__ == "__main__":
    sys.exit(main())
