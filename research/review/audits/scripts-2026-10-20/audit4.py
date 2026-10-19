import json
R = r"C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706"
log = [json.loads(l) for l in open(R + "/analysis/screening/ft-t1/batch-log.jsonl", encoding="utf-8") if l.strip()]
prev = {}
for n, e in enumerate(log, 1):
    if "event" in e:
        if e["event"] == "quote_return":
            e2 = prev.get(e["batch"])
            print(n, "return", e["batch"], e["role"], e["ids"], "| prev result line", e2[0] if e2 else None)
        continue
    b = e["batch"]
    if b in prev:
        pn, p = prev[b]
        keys = ("agree", "disagree", "adjudicate", "include_both")
        ch = {k: (p.get(k), e.get(k)) for k in keys if p.get(k) != e.get(k)}
        if ch: print(n, "result change vs line", pn, b, ch)
    prev[b] = (n, e)
