import json, collections, sys, os
R = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706"
FT = R + "/analysis/screening/ft-t1"
c = collections.Counter(); keys = collections.defaultdict(set)
for l in open(FT + "/batch-log.jsonl", encoding="utf-8"):
    r = json.loads(l); e = r.get("event"); c[e] += 1; keys[e] |= set(r)
for k, v in c.items():
    print(k, v, sorted(keys[k]))
print("---- first lines")
with open(FT + "/batch-log.jsonl", encoding="utf-8") as f:
    for i, l in enumerate(f):
        if i < 6: print(l[:700])
print(os.listdir(FT + "/c/c-t1-01"), os.listdir(FT + "/c/c-t1-12"))
print(open(FT + "/c-queue-1.jsonl", encoding="utf-8").readline()[:800])
