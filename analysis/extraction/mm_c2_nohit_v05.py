"""Lists the C2 records that are not side-experiment ids and have no multimodal benchmark or diffusion-LM name in the
body (EXTRACTION-PLAN-v0.5 s2.3; red-team audit 4, mi6). multimodal_options.py counts them (20) but does not print
their ids; it is imported read-only and its C2 rule is re-applied here line for line; the counts and the C2 list
hash are asserted against multimodal_options-log.txt.
Run from the worktree root: python -I analysis/extraction/mm_c2_nohit_v05.py
"""
import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("mo", Path("analysis/extraction/multimodal_options.py"))
mo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mo)


def main():
    dec = {r["id"]: r for r in mo.jl(mo.DEC)}
    inc = sorted(i for i, r in dec.items() if r["decision"] == "include")
    A, B, C = {}, {}, {}
    for d in sorted(mo.FT1.glob("t1b0*")):
        for role, st in (("A", A), ("B", B)):
            for r in mo.jl(d / f"F{role}-{d.name}.jsonl"):
                st[r["id"]] = r
    sup = {(r["id"], r["group"]) for r in mo.jl(mo.FT1 / "c-superseded.jsonl")}
    for f in sorted(mo.FT1.glob("c/c-t1-*/FC-*.jsonl")):
        for r in mo.jl(f):
            if (r["id"], f.parent.name) not in sup:
                C[r["id"]] = r
    meta = {}
    for path, key in mo.CORPUS:
        for r in mo.jl(path):
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

    C2 = []
    for i in inc:
        r = dec[i]
        if r["i1"] in ("b", "ab") or r["nonlang_only"]:
            continue
        m = mm_final(i)
        if m.startswith("split:") and "multimodal" in m:
            is_mm = bool(mo.KW.search(meta.get(i, "")))
        else:
            is_mm = m == "multimodal"
        if is_mm:
            C2.append(i)
    h = mo.sha(C2)
    print(f"C2 {len(C2)} records, sha256 {h}")
    assert len(C2) == 108 and h.startswith("6766a919f8e11c23"), "C2 differs from multimodal_options-log.txt"
    side = set(mo.SIDE)
    other = [i for i in C2 if i not in side]
    nohit = [i for i in other if not any(mo.mm_hits(i)[:2])]
    print(f"other C2 (not side-experiment ids) {len(other)}; with no multimodal benchmark or DLM name in the body {len(nohit)}")
    assert len(other) == 79 and len(other) - len(nohit) == 59, "counts differ from multimodal_options-log.txt"
    print("ids: " + " ".join(nohit))
    print(f"sha256 of the id list {mo.sha(nohit)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
