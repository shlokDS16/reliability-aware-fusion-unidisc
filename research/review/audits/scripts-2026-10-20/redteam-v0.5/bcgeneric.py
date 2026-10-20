"""Red-team v0.5 scratch: list what brief_contamination_v05 classifies as 'generic' (> 5 include texts, passes
silently) and which schema string values it never scans. Imports the committed script read-only.
Run from the worktree root."""
import importlib.util, json, re
from pathlib import Path
spec = importlib.util.spec_from_file_location("bc05", "analysis/extraction/brief_contamination_v05.py")
bc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bc)
inc = sorted(json.loads(l)["id"] for l in open(bc.DEC, encoding="utf-8") if '"decision": "include"' in l)
texts = {i: bc.norm((bc.TEXTS / f"{i}.txt").read_text(encoding="utf-8", errors="replace")) for i in inc}
brief, schema = bc.FILES["v0.5"]
allt = bc.session_text(brief, schema)
cands = set()
for m in bc.SPAN.finditer(allt):
    cands.add(next(g for g in m.groups() if g is not None))
cands |= set(bc.DECIMAL.findall(allt)) | set(bc.INTEGER.findall(allt))
gen = []
for c in sorted(cands):
    q = bc.norm(c)
    h = [i for i in inc if q in texts[i]] if len(q.strip()) >= 2 else []
    if len(h) > 5:
        gen.append((len(h), c))
print("GENERIC spans/numbers (count of include texts, string):")
for n, c in sorted(gen):
    print(f"  {n:4d}  {c!r}")
grams = {}
for i, t in texts.items():
    tt = bc.toks(t)
    grams[i] = {tuple(tt[j:j + 5]) for j in range(len(tt) - 4)}
st = bc.toks(allt)
sh = {tuple(st[j:j + 5]) for j in range(len(st) - 4)}
for g in sh:
    n = sum(g in grams[i] for i in inc)
    if n > 5:
        print("GENERIC 5-gram:", " ".join(g), n)
# schema string values outside 'description'
s = json.loads(Path(schema).read_text(encoding="utf-8"))
other = {}
def walk(x, key=None):
    if isinstance(x, dict):
        for k, v in x.items():
            if k != "description":
                walk(v, k)
    elif isinstance(x, list):
        for v in x:
            walk(v, key)
    elif isinstance(x, str) and key not in ("type", "$ref", "$schema", "$id", "description"):
        other.setdefault(key, set()).add(x)
walk(s)
print("schema string values not scanned, by key:", {k: len(v) for k, v in other.items()})
for k in other:
    if k not in ("required",):
        print(" ", k, sorted(other[k])[:40])
# how many session-text characters are in the brief outside ```text blocks (not seen by sessions; fine) vs dispatch?
