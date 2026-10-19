import json, os, subprocess, sys, collections
R = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706"
CHK = R + "/tools/ft_isolation_check.py"
V = r"C:\Users\Shlok\Downloads\obsidian\Claude code obsidian"
out = json.load(open(os.path.dirname(__file__) + "/transcripts.json"))
res = collections.Counter(); bad = []
for (s, tr, folder) in out:
    rel, bn, agent, filed = s
    p = subprocess.run([sys.executable, "-I", CHK, tr, folder, "--vault", V], capture_output=True, text=True, encoding="utf-8")
    try:
        d = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        bad.append((rel, "checker error", p.stderr[-300:])); continue
    key = ("filed_pass" if filed else "filed_fail", "recheck_pass" if d["pass"] else "recheck_fail")
    res[key] += 1
    if bool(d["pass"]) != bool(filed):
        bad.append((rel, bn, filed, d["flags"][:3]))
print(dict(res))
for b in bad: print(b)
