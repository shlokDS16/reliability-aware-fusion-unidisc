"""Model check of screener and adjudicator sessions: every assistant turn must come from the role's model
(criteria v1.6 s4 item 1: no fallback for A or B; only claude-fable-5-1 is C). Added 2026-10-20 after the
T1 gate audit found t1b081 B finished by claude-opus-5 after a safety-classifier stop.

    python -I tools/ft_model_check.py [--map tools/ft-session/agent-map.txt] [--transcript <jsonl> --role A|B|C]

With --map: checks every '<batch> <role> <agent id>' line whose transcript is found under
~/.claude/projects/*/*/subagents/ and prints one JSON line per mismatch plus a summary line.
Turns with model "<synthetic>" are harness-written API/network error notices, not model output; they are
allowed and shown in "models". With --transcript: checks one file and prints {"pass": bool, "models": {...}}.
"""
import collections, glob, json, re, sys
from pathlib import Path

EXP = {"A": "claude-sonnet-5-5", "B": "claude-opus-5-5", "C": "claude-fable-5-1"}
HOME = Path.home() / ".claude/projects"


def models(path):
    c = collections.Counter()
    for line in open(path, encoding="utf8", errors="replace"):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") == "assistant":
            c[(d.get("message") or {}).get("model")] += 1
    return dict(c)


if "--transcript" in sys.argv:
    t = sys.argv[sys.argv.index("--transcript") + 1]
    role = sys.argv[sys.argv.index("--role") + 1]
    m = models(t)
    real = {k: v for k, v in m.items() if k != "<synthetic>"}   # <synthetic> = harness turn (API/network error text)
    print(json.dumps({"pass": bool(real) and set(real) == {EXP[role]}, "expected": EXP[role], "models": m}))
    sys.exit(0)

amap = sys.argv[sys.argv.index("--map") + 1] if "--map" in sys.argv else "tools/ft-session/agent-map.txt"
checked = missing = 0
bad = []
for line in open(amap, encoding="utf-8"):
    p = line.split()
    if line.startswith("#") or len(p) < 3 or p[1] not in EXP or not re.fullmatch(r"a[0-9a-f]{16}", p[2]):
        continue
    fs = glob.glob(str(HOME / "*" / "*" / "subagents" / f"agent-{p[2]}.jsonl"))
    if not fs:
        missing += 1
        continue
    checked += 1
    m = models(fs[0])
    if set(k for k in m if k != "<synthetic>") != {EXP[p[1]]}:   # <synthetic> = harness turn (API/network error text)
        bad.append({"batch": p[0], "role": p[1], "agent": p[2], "models": m, "transcript": fs[0]})
for b in bad:
    print(json.dumps(b))
print(json.dumps({"checked": checked, "transcript_not_found": missing, "mismatches": len(bad)}))
