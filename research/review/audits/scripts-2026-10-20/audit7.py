import json, glob, os, random
R = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706"
FT = R + "/analysis/screening/ft-t1"
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
A = {}; B = {}; rb = {}
for d in sorted(glob.glob(FT + "/t1b*")):
    b = os.path.basename(d)
    for r in jl(f"{d}/FA-{b}.jsonl"): A[r["id"]] = r["decision"]; rb[r["id"]] = b
    for r in jl(f"{d}/FB-{b}.jsonl"): B[r["id"]] = r["decision"]
pos = lambda x: x != "exclude"
def k(ids):
    n = len(ids); tp = sum(pos(A[i]) and pos(B[i]) for i in ids); tn = sum((not pos(A[i])) and (not pos(B[i])) for i in ids)
    ao = sum(pos(A[i]) and not pos(B[i]) for i in ids); bo = n - tp - tn - ao
    po = (tp + tn) / n; pa = (tp + ao) / n; pb = (tp + bo) / n; pe = pa * pb + (1 - pa) * (1 - pb)
    return n, tp, tn, ao, bo, round(po, 4), round((po - pe) / (1 - pe), 4)
ids715 = sorted(i for i in A if rb[i] <= "t1b076")
print("t1b001-076", k(ids715))
rnd = random.Random(20261024); ks = []
for _ in range(2000):
    s = [ids715[rnd.randrange(len(ids715))] for _ in ids715]; ks.append(k(s)[-1])
ks.sort(); print("boot", ks[49], ks[1949])
print("part19", k(sorted(i for i in A if rb[i] >= "t1b077")))
import hashlib
print("715 frame sha (sorted ids joined by newline):", hashlib.sha256("\n".join(ids715).encode()).hexdigest())
