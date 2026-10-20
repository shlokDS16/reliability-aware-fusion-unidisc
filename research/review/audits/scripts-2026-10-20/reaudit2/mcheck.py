import json, glob, re, collections, os, sys
from pathlib import Path
ROOT = Path(sys.argv[1])
HOME = Path.home() / ".claude/projects"
EXP = {"A": "claude-sonnet-5-5", "B": "claude-opus-5-5", "C": "claude-fable-5-1"}
pat = re.compile(r"\b([ABC])-((?:t1b\d+\w*)|(?:c-t1-\d+)|(?:ft-pilot\d+))-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")
files = glob.glob(str(HOME / "C--Users-Shlok-Downloads-Multi-Modality-Language-model*" / "*" / "subagents" / "agent-*.jsonl"))
info = {}
for f in files:
    models = collections.Counter(); first_user = None; switches = []; prev = None
    for n, line in enumerate(open(f, encoding="utf8", errors="replace"), 1):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") == "user" and first_user is None:
            c = (d.get("message") or {}).get("content")
            first_user = c if isinstance(c, str) else json.dumps(c)
        if d.get("type") == "assistant":
            m = (d.get("message") or {}).get("model"); models[m] += 1
            if m != prev and m != "<synthetic>":
                switches.append((n, m)); prev = m
    agent = Path(f).stem[6:]
    bn = pat.search(first_user or "")
    info.setdefault(agent, []).append(dict(path=f, models=dict(models), basename=bn.group(0) if bn else None,
                                           role=bn.group(1) if bn else None, switches=switches))
tot = 0; mism = []; inconsistent = []
for a, copies in info.items():
    sig = {json.dumps(c["models"], sort_keys=True) for c in copies}
    if len(sig) > 1:
        inconsistent.append((a, [(c["path"].split("projects")[1][:100], c["models"]) for c in copies]))
    for c in copies:
        if c["role"] is None:
            continue
        tot += 1
        real = {k for k in c["models"] if k != "<synthetic>"}
        if real != {EXP[c["role"]]}:
            mism.append((a, c["basename"], c["models"], c["switches"], c["path"].split("projects\\")[1][:110]))
print("transcript files", len(files), "agents", len(info), "screening copies", tot,
      "screening agents", sum(1 for a, c in info.items() if c[0]["role"]))
print("inconsistent copies", inconsistent)
for m in mism:
    print("MISMATCH", m)
used = []
for p in glob.glob(str(ROOT / "analysis/screening/ft-t1/**/isolation-*.json"), recursive=True):
    if "DISCARDED" in p:
        continue
    d = json.loads(open(p, encoding="utf8").read())
    used.append((p, d["agent"], d["basename"]))
bad = []; notfound = []
for p, a, bn in used:
    if a not in info:
        notfound.append((p, a)); continue
    role = bn[0]
    for c in info[a]:
        real = {k for k in c["models"] if k != "<synthetic>"}
        if real != {EXP[role]}:
            bad.append((p, a, c["models"]))
        if c["basename"] != bn:
            bad.append((p, a, "basename mismatch", c["basename"], bn))
print("used isolation files", len(used), "not found", notfound, "bad", bad)
syn = [(a, c[0]["basename"], c[0]["models"]) for a, c in info.items() if c[0]["role"] and "<synthetic>" in c[0]["models"]]
print("synthetic", syn)
json.dump(info, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcheck.json"), "w"))
