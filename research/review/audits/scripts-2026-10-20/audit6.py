import json, glob, os, collections, hashlib
R = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706"
S = R + "/analysis/screening"; FT = S + "/ft-t1"
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
allr = {r["id"]: r for r in jl(FT + "/t1-decisions-all.jsonl")}
old = {r["id"]: r for r in jl(FT + "/t1-decisions-b001-b034.jsonl")}
d = [(i, k, old[i].get(k), allr[i].get(k)) for i in old for k in ("decision", "code", "source") if old[i].get(k) != allr.get(i, {}).get(k)]
print("b001-b034 file vs all: n", len(old), "diffs", d[:10], "missing", [i for i in old if i not in allr])
print("old summary", json.load(open(FT + "/t1-summary-b001-b034.json", encoding="utf-8")).get("decision"))
pil = set()
for f in glob.glob(S + "/ft-pilot01/**/*.jsonl", recursive=True):
    for r in jl(f):
        if "id" in r: pil.add(r["id"])
print("pilot ids", len(pil), "in T1:", sorted(pil & set(allr)))
print(os.listdir(S + "/ft-pilot01"))
# human validation sample
hv = R + "/research/review/screening/human-validation-t1"
print(os.listdir(hv))
for f in os.listdir(hv):
    p = hv + "/" + f
    if os.path.isfile(p): print(f, hashlib.sha256(open(p, "rb").read()).hexdigest())
m = json.load(open(hv + "/sample-manifest.json", encoding="utf-8"))
print({k: (v if not isinstance(v, list) else len(v)) for k, v in m.items()})
