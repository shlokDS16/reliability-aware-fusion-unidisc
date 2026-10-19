import json, re, sys, importlib.util
from pathlib import Path
from collections import defaultdict
spec = importlib.util.spec_from_file_location("bc", "analysis/extraction/brief_contamination.py")
bc = importlib.util.module_from_spec(spec); spec.loader.exec_module(bc)
blk, desc = bc.session_text("research/review/extraction/extractor-brief-v0.4.md", "research/review/extraction/extraction-schema-v0.4.json")
allt = blk + "\n" + desc
def toks(t): return re.findall(r"[a-z0-9][a-z0-9.\-/%=()+]*", t.lower())
inc = sorted(json.loads(l)["id"] for l in open(bc.DEC, encoding="utf-8") if '"decision": "include"' in l)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
st = toks(allt)
sh = set(tuple(st[i:i+N]) for i in range(len(st)-N+1))
hits = defaultdict(list)
for i in inc:
    tt = toks((bc.TEXTS / f"{i}.txt").read_text(encoding="utf-8", errors="replace"))
    s2 = set(tuple(tt[j:j+N]) for j in range(len(tt)-N+1))
    for g in sh & s2: hits[g].append(i)
spec_ = sorted((len(v), " ".join(g), v) for g, v in hits.items() if len(v) <= 3)
print("n", N, "session shingles", len(sh), "found in any include", len(hits), "in 1-3 includes", len(spec_))
for c, g, v in spec_: print(c, "|", g, "|", " ".join(v))
# number co-occurrence
nums = sorted(set(re.findall(r"(?<![\w.])\d+\.\d+(?![\w.])", allt)))
print("decimal numbers in session text:", nums)
best = []
for i in inc:
    t = (bc.TEXTS / f"{i}.txt").read_text(encoding="utf-8", errors="replace")
    have = [x for x in nums if re.search(r"(?<![\w.])" + re.escape(x) + r"(?![\w.])", t)]
    best.append((len(have), i, have))
best.sort(reverse=True)
for b in best[:6]: print(b)
