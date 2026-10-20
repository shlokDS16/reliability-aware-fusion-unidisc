"""Checks that the text a session sees holds no string taken from a paper that can be drawn (EXTRACTION-PLAN-v0.5
s10.2; red-team audit 4, MA2 and mi3). brief_contamination.py (v0.4) is left unchanged so its log reproduces.

Session text = every ```text block of the brief (extraction block, EC paragraph, EQ paragraph) + every
description string in the schema. Include texts = the screened full texts of all 608 T1 includes, normalised:
lower case, ligatures expanded (fi, fl, ff, ffi, ffl), a hyphen at a line end joined to the next line,
whitespace collapsed. Checks, each run on the v0.4 files (for comparison) and the v0.5 files (verdict):
  (1) KNOWN: the 17 strings from drawable papers listed in brief_contamination.py must be absent.
  (2) SPANS: every span of 3-80 characters inside double, single, backtick or curly quotes, every decimal
      number and every integer of two or more digits is searched in the include texts.
  (3) 5-GRAMS: every word 5-gram of the session text (quoted or not; tokens as in the red-team's shingle.py) is
      searched in the include texts' 5-gram sets.
  (4) NUMBER RUNS: for every line of session text with two or more distinct decimal numbers, an include text
      holds the run if all of them occur within one window of 300 characters.
A hit in 1 to 5 include texts is 'specific'; in more than 5, generic; in none, synthetic. A specific hit passes
only if it is on the allowlist below (instrument ids by pattern; listed strings with a reason). The exit code
is 1 if a KNOWN string or a non-allowlisted specific hit is found in the v0.5 session text, else 0.
Run from the worktree root: python -I analysis/extraction/brief_contamination_v05.py
"""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(".")
spec = importlib.util.spec_from_file_location("bc04", ROOT / "analysis/extraction/brief_contamination.py")
bc04 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc04)
DEC, TEXTS, KNOWN = bc04.DEC, bc04.TEXTS, bc04.KNOWN
FILES = {"v0.4": ("research/review/extraction/extractor-brief-v0.4.md", "research/review/extraction/extraction-schema-v0.4.json"),
         "v0.5": ("research/review/extraction/extractor-brief-v0.5.md", "research/review/extraction/extraction-schema-v0.5.json")}
SPAN = re.compile(r'"([^"\n]{3,80})"|(?<![\w])\'([^\'\n]{3,80})\'(?![\w])|`([^`\n]{3,80})`|“([^”\n]{3,80})”|‘([^’\n]{3,80})’')
DECIMAL = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")
INTEGER = re.compile(r"(?<![\w.])\d{2,}(?![\w.])")
TOK = re.compile(r"[a-z0-9][a-z0-9.\-/%=()+]*")
LIG = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl"}
ID_PATTERN = re.compile(r"^(?:[A-Z]{1,2}\d{1,2}[a-z]?|[A-Z]\d{2}\.[a-z_]+|QA\d[a-z]?)$")   # C04, K02, QA1, T01, S10.steps
ALLOW = {  # specific string -> reason it is generic or the instrument's own (each reviewed by the method-architect)
    ": [...], ": "JSON punctuation of the output format",
    ": {...}, ": "JSON punctuation of the output format",
    "T>1": "codebook notation for more than one step",
    "beam B": "codebook term (search width)",
    "not stated": "codebook value",
    "tuned per task": "codebook value of the setting-provenance field",
}


def norm(t):
    for a, b in LIG.items():
        t = t.replace(a, b)
    t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)
    return re.sub(r"\s+", " ", t.lower())


def toks(t):
    return TOK.findall(t.lower())


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
    return "\n".join(blocks) + "\n" + "\n".join(desc)


def classify(hits):
    return "synthetic" if not hits else "specific" if len(hits) <= 5 else "generic"


def main():
    inc = sorted(json.loads(l)["id"] for l in open(DEC, encoding="utf-8") if '"decision": "include"' in l)
    raw = {i: (TEXTS / f"{i}.txt").read_text(encoding="utf-8", errors="replace") for i in inc}
    texts = {i: norm(t) for i, t in raw.items()}
    grams = {}
    for i, t in texts.items():
        tt = toks(t)
        grams[i] = {tuple(tt[j:j + 5]) for j in range(len(tt) - 4)}
    print(f"includes {len(inc)}; decisions sha256 {hashlib.sha256(DEC.read_bytes()).hexdigest()[:16]}; "
          f"script sha256 {hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]}")
    allow_ngrams = {tuple(k.split()): v for k, v in ALLOW_5GRAMS.items()}
    verdict = {}
    for ver, (brief, schema) in FILES.items():
        allt = session_text(brief, schema)
        print(f"\n===== {ver}: {brief} + {schema} (session text {len(allt)} chars; brief sha256 "
              f"{hashlib.sha256(Path(brief).read_bytes()).hexdigest()[:16]}, schema sha256 "
              f"{hashlib.sha256(Path(schema).read_bytes()).hexdigest()[:16]}) =====")
        known = [k for k in KNOWN if k in allt]
        print(f"(1) KNOWN strings present: {len(known)}" + ("".join(f"\n    '{k}' <- {KNOWN[k]}" for k in known)))
        bad = list(known)
        # (2) spans and numbers
        cands = set()
        for m in SPAN.finditer(allt):
            cands.add(next(g for g in m.groups() if g is not None))
        cands |= set(DECIMAL.findall(allt)) | set(INTEGER.findall(allt))
        res = {"synthetic": [], "generic": [], "specific": []}
        for c in sorted(cands):
            q = norm(c)
            hits = [i for i in inc if q in texts[i]] if len(q.strip()) >= 2 else []
            res[classify(hits)].append((c, hits))
        print(f"(2) SPANS and numbers: {len(cands)} candidates; synthetic {len(res['synthetic'])}; generic "
              f"{len(res['generic'])}; specific {len(res['specific'])}")
        for c, h in res["specific"]:
            why = "instrument id (pattern)" if ID_PATTERN.match(c) else ALLOW.get(c)
            print(f"    specific{' [allowlisted: ' + why + ']' if why else ' [NOT ALLOWLISTED]'}: '{c}' in {len(h)}: {' '.join(h)}")
            if not why:
                bad.append(c)
        # (3) word 5-grams
        st = toks(allt)
        sh = {tuple(st[j:j + 5]) for j in range(len(st) - 4)}
        hits = {}
        for i in inc:
            for g in sh & grams[i]:
                hits.setdefault(g, []).append(i)
        spec5 = sorted((g, v) for g, v in hits.items() if len(v) <= 5)
        print(f"(3) 5-GRAMS: {len(sh)} distinct session 5-grams; in any include {len(hits)}; generic (> 5 texts) "
              f"{len(hits) - len(spec5)}; specific (1-5 texts) {len(spec5)}")
        for g, v in spec5:
            why = allow_ngrams.get(g)
            print(f"    specific{' [allowlisted: ' + why + ']' if why else ' [NOT ALLOWLISTED]'}: '{' '.join(g)}' in {len(v)}: {' '.join(v)}")
            if not why:
                bad.append(" ".join(g))
        # (4) number runs
        runs = []
        for line in allt.splitlines():
            nums = sorted(set(DECIMAL.findall(line)))
            if len(nums) >= 2:
                runs.append(nums)
        nrun_spec = 0
        for nums in runs:
            found = []
            for i in inc:
                t = texts[i]
                pos = [[m.start() for m in re.finditer(r"(?<![\w.])" + re.escape(x) + r"(?![\w.])", t)] for x in nums]
                if not all(pos):
                    continue
                if any(all(any(p0 <= p < p0 + 300 for p in ps) for ps in pos) for p0 in pos[0]) or \
                   any(all(any(p0 - 300 < p <= p0 for p in ps) for ps in pos) for p0 in pos[0]):
                    found.append(i)
            kind = classify(found)
            if kind == "specific":
                nrun_spec += 1
                bad.append("run " + " ".join(nums))
            print(f"(4) NUMBER RUN {' '.join(nums)}: {kind} ({len(found)} include texts{': ' + ' '.join(found) if 0 < len(found) <= 5 else ''})")
        if not runs:
            print("(4) NUMBER RUNS: none")
        verdict[ver] = bad
        print(f"  {ver}: KNOWN {len(known)}; non-allowlisted specific hits {len(bad) - len(known)}")
    print(f"\nSUMMARY: v0.4 failures {len(verdict['v0.4'])}; v0.5 failures {len(verdict['v0.5'])}"
          + (f" ({'; '.join(verdict['v0.5'])})" if verdict["v0.5"] else ""))
    return 1 if verdict["v0.5"] else 0


ALLOW_5GRAMS = {   # 5-gram (space-joined tokens) -> reason; each reviewed by the method-architect, 2026-10-20
    "do not apply to the": "function words only",
    "does not say whether the": "function words only",
    "if at least one of": "function words only",
    "if the text does not": "function words only",
    "in the setting of the": "function words only",
    "in this family is a": "function words only",
    "inputs and outputs of the": "function words only",
    "is the one of the": "function words only",
    "model stands in for the": "function words only",
    "of every arm in this": "function words only",
    "only one of the two": "function words only",
    "that differ only in the": "function words only",
    "that differs from it in": "function words only",
    "the first row of the": "function words only",
    "whether or not it is": "function words only",
    "within a factor of two": "function words only",
    "forward passes or function evaluations": "the instrument's own codebook wording (rule text, no paper-specific content)",
    "how many positions are committed": "the instrument's own codebook wording (rule text, no paper-specific content)",
    "if it equals the reference": "the instrument's own codebook wording (rule text, no paper-specific content)",
    "the token distribution of the": "the instrument's own codebook wording (rule text, no paper-specific content)",
    "tokens per step on the": "the instrument's own codebook wording (rule text, no paper-specific content)",
    "which masked positions are committed": "the instrument's own codebook wording (rule text, no paper-specific content)",
}


if __name__ == "__main__":
    sys.exit(main())
