import json, glob, os
R = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706"
FT = R + "/analysis/screening/ft-t1"
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
for f in sorted(glob.glob(FT + "/t1b*/F*DISCARDED*.jsonl")):
    b = os.path.basename(os.path.dirname(f)); role = os.path.basename(f)[1]
    d = {r["id"]: r["decision"] for r in jl(f)}
    fin = {r["id"]: r["decision"] for r in jl(f"{FT}/{b}/F{role}-{b}.jsonl")}
    other = {r["id"]: r["decision"] for r in jl(f"{FT}/{b}/F{'B' if role=='A' else 'A'}-{b}.jsonl")}
    ch = {i: (d[i], fin.get(i)) for i in d if d[i] != fin.get(i)}
    # would the discarded session have changed agreement?
    dis_disc = sum(1 for i in d if d[i] != other[i]); dis_fin = sum(1 for i in fin if fin[i] != other[i])
    print(b, role, "n", len(d), "changed", ch, "disagreements discarded vs final:", dis_disc, dis_fin, "missing in discarded:", sorted(set(fin) - set(d)))
