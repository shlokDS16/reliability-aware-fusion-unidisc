import csv, sys, collections, json
sys.path.insert(0, ".")
from data1 import P
from data2 import N
for r in N:
    if r["name"] == "Dynin-Omni":
        r["C4steps"] = "Image generation 16 steps (Table 6); editing 128; Fig 11 sweeps: GSM8K needs 512-1024, GenEval saturates 64-128"
rows = []
for i, r in enumerate(P + N, 1):
    r = dict(r)
    r["id"] = "M%02d" % i
    r.setdefault("ver", "")
    r.setdefault("aw", "")
    r["evlevel"] = "E2 as recorded in the primer (not re-read here)" if r["ev"].startswith("primer") else "E2 for the sections listed in 'evidence'; whole paper not read"
    rows.append(r)
COLS = ["id","name","arxiv","ver","aw","fam","evlevel","ev","C1","C2","C3","C4pos","C4val","C4steps","C4joint","C5","mem","lev","fit","missing","src","cls","esel","ent","sweep","swfix"]
HDR = {"id":"id","name":"name","arxiv":"arXiv ID","ver":"version read","aw":"corpus record","fam":"family","evlevel":"evidence level","ev":"evidence (sections)",
 "C1":"C1 channel per modality","C2":"C2 reveal law and objective weight","C3":"C3 predictor output and head layout","C4pos":"C4 position rule","C4val":"C4 value rule",
 "C4steps":"C4 tokens per step or steps in main results","C4joint":"C4 joint draw","C5":"C5 revision","mem":"memory m_n","lev":"lever row(s)","fit":"fits (yes/partly/no)",
 "missing":"what is missing","src":"source location","cls":"value-rule classes (A argmax, T low temp, P top-p/k, S sample-then-filter, G guidance, M sequence-level selection)",
 "esel":"headline uses E_sel-type rule","ent":"entropy or diversity reported","sweep":"step sweep reported","swfix":"value rule and guidance held fixed in sweep"}
out = sys.argv[1]
with open(out + ".csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([HDR[c] for c in COLS])
    for r in rows:
        w.writerow([r.get(c, "") for c in COLS])
# markdown table
def esc(s): return str(s).replace("|", "/").replace("\n", " ")
MC = ["id","name","arxiv","fam","C1","C2","C3","C4pos","C4val","C4steps","C4joint","C5","mem","lev","fit","missing","src"]
MH = ["id","name","arXiv","family","C1 channel","C2 reveal law, weight","C3 predictor, head","C4 position rule","C4 value rule","C4 steps / tokens per step","C4 joint draw","C5 revision","memory m_n","levers","fits","missing","source"]
with open(out + "_table.md", "w", encoding="utf-8") as f:
    f.write("| " + " | ".join(MH) + " |\n|" + "---|" * len(MH) + "\n")
    for r in rows:
        f.write("| " + " | ".join(esc(r.get(c, "")) for c in MC) + " |\n")
# counts
C = collections.Counter
print("n rows", len(rows))
print("families", C(r["fam"].split(" (")[0] for r in rows))
print("fit", C(r["fit"] for r in rows))
print("partly:", [r["name"] for r in rows if r["fit"] == "partly"])
print("esel", C(r["esel"] for r in rows))
for k in ["yes","controlled","no","unclear","na","subject"]:
    print(k, [r["name"] for r in rows if r["esel"] == k])
cl = C()
for r in rows:
    for t in [x for x in r["cls"].split(";") if x]:
        cl[t] += 1
print("classes", cl)
for t in "ATPSGM":
    print(t, [r["name"] for r in rows if t in r["cls"].split(";")])
print("sweep", C(r["sweep"] for r in rows))
print("swfix among sweep=yes/partial", C((r["sweep"], r["swfix"]) for r in rows if r["sweep"] in ("yes","partial","qual")))
for k in ["yes","co-varied","not stated"]:
    print("swfix", k, [r["name"] for r in rows if r["sweep"] in ("yes","partial","qual") and r["swfix"] == k])
print("ent", C(r["ent"] for r in rows))
print("ent yes", [r["name"] for r in rows if r["ent"] == "yes"])
print("joint", [(r["name"], r["C4joint"]) for r in rows if r["C4joint"].startswith("yes")])
print("mem nonnone", [(r["name"]) for r in rows if r["mem"] not in ("none",) ])
levc = C()
import re
for r in rows:
    for t in re.findall(r"L\d+", r["lev"]):
        levc[t] += 1
print("levers", sorted(levc.items(), key=lambda x: int(x[0][1:])))
for r in rows:
    if not re.search(r"L\d+", r["lev"]): print("no L code:", r["name"])
