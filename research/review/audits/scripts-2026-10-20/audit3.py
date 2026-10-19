import json, collections, os
R = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706"
S = R + "/analysis/screening"
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
st = json.load(open(os.path.dirname(__file__) + "/state.json"))
dec, rb, sids, c8 = st["dec"], st["rowbatch"], set(st["sids"]), set(st["c8"])
ft = {r["id"]: r for r in jl(R + "/research/review/fulltext/ft-routes.jsonl")}
ex = {r["id"]: r for r in jl(S + "/ft-routes-extra.jsonl")}
print("ft-routes", len(ft), "extra", len(ex), "groups", collections.Counter(r["group"] for r in ex.values()))
print("ids in both ft and extra:", sorted(set(ft) & set(ex)))
t1 = set(dec)
print("T1 in ft", len(t1 & set(ft)), "T1 in extra", len(t1 & set(ex)), "T1 in neither", sorted(t1 - set(ft) - set(ex)))
print("T1 extra by group", collections.Counter(ex[i]["group"] for i in t1 & set(ex)))
print("extra recheck groups in T1:", sum(1 for i in t1 & set(ex) if ex[i]["group"] != "ta-pass-unrouted"))
print("sample ids in ex:", len(sids & set(ex)), "c8 in ex:", len(c8 & set(ex)))
nr = {r["id"] for r in jl(S + "/ft-t1/t1-not-retrieved.jsonl")}
print("not-retrieved in ft:", len(nr & set(ft)))
print("extra not in T1 by group/route", collections.Counter((ex[i]["group"], ex[i]["route_type"]) for i in set(ex) - t1))
print("reports_sought:", len(ft) - sum(1 for r in ft.values() if r["route_type"] == "duplicate" and r["id"] not in t1) + len(ex))
# part 19 composition
p19 = [i for i in t1 if rb[i] >= "t1b077"]
comp = collections.Counter("sample" if i in sids else "c8" if i in c8 else ("extra:" + ex[i]["group"]) if i in ex else "ft-routes" for i in p19)
print("part19 composition", comp)
print("part19 decisions by comp", {k: dict(collections.Counter(dec[i]["decision"] for i in p19 if ("sample" if i in sids else "c8" if i in c8 else ("extra:" + ex[i]["group"]) if i in ex else "ft-routes") == k)) for k in comp})
# recheck ids appearing before part 19
print("recheck ids in batches < t1b077:", sorted(i for i in t1 if (i in sids or i in c8) and rb[i] < "t1b077"))
# records in T1 from TA-pass ft routes that are duplicates (route_type duplicate) but screened
print("T1 ids with ft route_type duplicate:", sorted(i for i in t1 & set(ft) if ft[i]["route_type"] == "duplicate"))
# T1 ids that are in the frame (other than sample)
frame = {json.loads(l)["id"] for l in open(S + "/ta-recheck-frame-v1.3-frozen.jsonl", encoding="utf-8") if l.strip()}
print("frame n", len(frame), "T1∩frame", len(t1 & frame), "T1∩frame not sample", sorted((t1 & frame) - sids))
print("T1 ∩ ft-routes ∩ frame (TA pass and TA exclusion at once?)", sorted(t1 & frame & set(ft)))
