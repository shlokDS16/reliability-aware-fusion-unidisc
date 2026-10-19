import json, glob, os, collections
R = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706"
FT = R + "/analysis/screening/ft-t1"
P = r"C:/Users/Shlok/.claude/projects"
idx = {}
for f in glob.glob(P + "/C--Users-Shlok-Downloads-Multi-Modality-Language-model*/*/subagents/agent-*.jsonl"):
    idx.setdefault(os.path.basename(f)[6:-6], []).append(f)
sess = []
for f in glob.glob(FT + "/t1b*/isolation-*.json") + glob.glob(FT + "/c/*/isolation-C.json"):
    d = json.load(open(f, encoding="utf-8"))
    sess.append((os.path.relpath(f, FT), d["basename"], d.get("agent"), d.get("pass")))
found = [(s, idx.get(s[2])) for s in sess]
print("sessions", len(sess), "with transcript found", sum(1 for s, t in found if t), "multiple", sum(1 for s, t in found if t and len(t) > 1))
miss = [s for s, t in found if not t]
print("missing transcripts:", miss[:20])
# find a basename-containing string in transcript to recover dispatch folder path
out = []
for s, t in found:
    if not t: continue
    txt = open(t[0], encoding="utf-8", errors="replace").read()
    i = txt.find(s[1])
    if i < 0: out.append((s, t[0], None)); continue
    j = txt.rfind('"', 0, i); start = j + 1
    folder = txt[start:i + len(s[1])].replace("\\\\", "/").replace("\\", "/")
    out.append((s, t[0], folder))
json.dump(out, open(os.path.dirname(__file__) + "/transcripts.json", "w"), indent=0)
print("folder path not found in transcript:", [o[0] for o in out if not o[2]][:10])
print(collections.Counter(o[2].split("/ft-dispatch")[0][-60:] if o[2] else None for o in out).most_common(6))
