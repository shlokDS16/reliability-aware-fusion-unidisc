import json, os, collections
out = json.load(open(os.path.dirname(__file__) + "/transcripts.json"))
exp = {"A": "claude-sonnet-5-5", "B": "claude-opus-5-5", "C": "claude-fable-5-1"}
res = collections.Counter(); bad = []
for (s, tr, folder) in out:
    rel, bn, agent, filed = s
    role = bn[0]
    models = collections.Counter()
    for line in open(tr, encoding="utf-8", errors="replace"):
        try: ev = json.loads(line)
        except Exception: continue
        m = (ev.get("message") or {}).get("model") if isinstance(ev.get("message"), dict) else None
        if m and m != "<synthetic>": models[m] += 1
    ok = set(models) == {exp[role]}
    res[(role, ok)] += 1
    if not ok: bad.append((rel, bn, dict(models)))
print(dict(res))
for b in bad: print(b)
