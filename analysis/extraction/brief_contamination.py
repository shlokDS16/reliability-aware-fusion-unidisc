"""Checks that the text a session sees (the brief's text blocks and every schema description) holds no example
taken from a paper that can be drawn (EXTRACTION-PLAN-v0.4 s10.2; red-team audit 3, M4).

Two checks, run on the v0.3 files (expected to fail: they are the red-team's evidence) and on the v0.4 files:
  (1) KNOWN: strings from the worked-example papers and the earlier E3 example (listed below with their source)
      must not occur in the session text.
  (2) SCAN: every double-quoted span of 3 to 80 characters and every decimal number in the session text is
      searched in the screened full texts of all 608 T1 includes (lower case, whitespace collapsed). A string
      found in 1 to 5 include texts is 'specific' and is printed with the ids; strings found in more than 5 texts
      are generic vocabulary (printed as a count only), strings found in none are synthetic.
Run from the worktree root: python -I analysis/extraction/brief_contamination.py
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(".")
DEC = ROOT / "analysis/screening/ft-t1/t1-decisions-all.jsonl"
TEXTS = ROOT / "research/sources/md/fulltext-pymupdf"
FILES = {"v0.3": ("research/review/extraction/extractor-brief-v0.3.md", "research/review/extraction/extraction-schema-v0.3.json"),
         "v0.4": ("research/review/extraction/extractor-brief-v0.4.md", "research/review/extraction/extraction-schema-v0.4.json")}
KNOWN = {  # string: source
    "FDM (K=2)": "M07474 focal configuration (worked-examples-v0.3 s1)",
    "Dream-v0-Instruct-7B": "M13864 focal model and row label (s4)",
    "for AR model, we report its scores only": "M08100 caption marker (s5)",
    "891.74": "M08100 trace cell (s5)",
    "Suffix / Short": "M09530 condition (s3)",
    "Discrete Diff.": "M12766 Table 2 cell (s2)",
    "VQAv2 / Acc.": "M12766 Table 2 leaf (s2)",
    "LLaDA / Accuracy": "M07474 Table 2 leaf (s1)",
    "DiffuseDef": "M03416 (E3 example of brief v0.2-v0.3)",
    "w/o diffusion denoising": "M03416 row label (E3 example)",
    "AGNews": "M03416 caption (E3 example)",
    "61.6": "M12766 GenEval percent value (H scale example)",
    "7.56 points": "H value_type example of brief v0.3",
    "64 steps": "M12766 setup (H setting example)",
    "K = 2 against 4": "M07474 Figure 5 series (U7 example)",
    "w/o remasking": "schema v0.3 level_printed example",
    "LLaMA-3 8B": "schema v0.3 level_printed example",
}
QUOTE = re.compile(r'"([^"\n]{3,80})"')
NUM = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")


def norm(t):
    return re.sub(r"\s+", " ", t.lower())


def session_text(brief, schema):
    b = Path(brief).read_text(encoding="utf-8")
    blocks = re.findall(r"```text\n(.*?)```", b, re.S)
    s = json.loads(Path(schema).read_text(encoding="utf-8"))
    desc = []

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "description" and isinstance(v, str):
                    desc.append(v)
                else:
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(s)
    # schema descriptions use single quotes for examples: turn them into double quotes for the scan
    d = "\n".join(re.sub(r"'([^'\n]{3,80})'", r'"\1"', t) for t in desc)
    return "\n".join(blocks), d


def main():
    inc = sorted(json.loads(l)["id"] for l in open(DEC, encoding="utf-8") if '"decision": "include"' in l)
    texts = {i: norm((TEXTS / f"{i}.txt").read_text(encoding="utf-8", errors="replace")) for i in inc}
    print(f"includes {len(inc)}; decisions sha256 {hashlib.sha256(DEC.read_bytes()).hexdigest()[:16]}")
    verdict = {}
    for ver, (brief, schema) in FILES.items():
        blk, desc = session_text(brief, schema)
        allt = blk + "\n" + desc
        print(f"\n===== {ver}: {brief} (text blocks {len(blk)} chars) + {schema} (descriptions {len(desc)} chars) =====")
        known = [(k, v) for k, v in KNOWN.items() if k in allt]
        print(f"(1) KNOWN strings present: {len(known)}")
        for k, v in known:
            print(f"    '{k}'  <- {v}")
        cands = sorted(set(QUOTE.findall(allt)) | set(NUM.findall(allt)))
        spec, gen, syn = [], [], []
        for c in cands:
            q = norm(c)
            hits = [i for i in inc if q in texts[i]]
            (syn if not hits else spec if len(hits) <= 5 else gen).append((c, hits))
        print(f"(2) SCAN: {len(cands)} candidate strings; synthetic (no include text) {len(syn)}; generic (> 5 texts) "
              f"{len(gen)}; specific (1-5 texts) {len(spec)}")
        for c, h in spec:
            print(f"    specific: '{c}' in {len(h)}: {' '.join(h)}")
        print("    generic: " + "; ".join(f"'{c}' ({len(h)})" for c, h in gen))
        verdict[ver] = (len(known), len(spec))
    print(f"\nSUMMARY: v0.3 known {verdict['v0.3'][0]}, specific {verdict['v0.3'][1]}; "
          f"v0.4 known {verdict['v0.4'][0]}, specific {verdict['v0.4'][1]}")
    return 0 if verdict["v0.4"][0] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
