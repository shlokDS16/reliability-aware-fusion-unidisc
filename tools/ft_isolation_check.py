"""Isolation check of one screener/adjudicator session transcript (criteria v1.6 audit copy, section 0).

    python tools/ft_isolation_check.py <transcript.jsonl> <dispatch folder> [--vault <obsidian vault root>]

Flags: (1) any path in a tool input outside the dispatch folder, any '..' or '~', any absolute path not
under it; Bash/PowerShell commands without a path inside the folder; (2) any command naming graph-memory,
graph_memory, graphify, obsidian, vault or rtk; (3) any Skill, Agent/Task, web, ToolSearch or MCP call;
(4) <vault>/Projects/<dispatch basename> existing afterwards. Prints JSON {pass, flags}.
Transcript of a subagent session: ~/.claude/projects/<project>/<session id>/subagents/agent-<agent id>.jsonl
(the tasks/<id>.output file is empty). Tested 2026-10-16 on a title/abstract screener transcript: 11 outside reads flagged.
"""
import json, re, sys
from pathlib import Path

tr, disp = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
vault = Path(sys.argv[sys.argv.index("--vault") + 1]) if "--vault" in sys.argv else None
D = str(disp).replace("\\", "/").lower()
flags = []
BAD_TOOLS = re.compile(r"^(Skill|Agent|Task|WebFetch|WebSearch|ToolSearch|mcp__.*)$")
BAD_CMD = re.compile(r"graph-memory|graph_memory|graphify|obsidian|vault|\brtk\b", re.I)
PATHLIKE = re.compile(r"((?<![\w.~/-])[A-Za-z]:[\\/][^\s\"'|<>]*|(?<![\w.~:/-])/[A-Za-z][^\s\"'|<>]*|(?<!\w)\.\.[\\/]?|(?<!\w)~[\\/]?)")   # absolute only when not inside a relative path

def inside(p):
    q = p.replace("\\", "/").lower()
    if q.startswith("/c/"):
        q = "c:/" + q[3:]
    return q.startswith(D)

for line in tr.read_text(encoding="utf8", errors="replace").splitlines():
    try:
        ev = json.loads(line)
    except Exception:
        continue
    msg = ev.get("message") or {}
    for blk in msg.get("content") or [] if isinstance(msg.get("content"), list) else []:
        if blk.get("type") != "tool_use":
            continue
        name, inp = blk.get("name", ""), blk.get("input") or {}
        if BAD_TOOLS.match(name):
            flags.append(f"tool {name}")
            continue
        for k in ("file_path", "path", "notebook_path"):
            if k in inp and not inside(str(inp[k])):
                flags.append(f"{name} {k} outside: {inp[k]}")
        if name in ("Grep", "Glob") and "path" not in inp:
            flags.append(f"{name} without explicit path")
        if name in ("Bash", "PowerShell"):
            cmd = str(inp.get("command", ""))
            if BAD_CMD.search(cmd):
                flags.append(f"{name} forbidden command: {cmd[:120]}")
            ps = PATHLIKE.findall(cmd)
            if any(p.startswith("..") or p.startswith("~") for p in ps):
                flags.append(f"{name} '..' or '~': {cmd[:120]}")
            abs_ps = [p for p in ps if not p.startswith((".", "~"))]
            if any(not inside(p) for p in abs_ps):
                flags.append(f"{name} path outside: {cmd[:120]}")
            if not any(inside(p) for p in abs_ps):
                flags.append(f"{name} without a path inside the folder: {cmd[:120]}")
if vault and (vault / "Projects" / disp.name).exists():
    flags.append(f"vault folder Projects/{disp.name} exists")
print(json.dumps({"pass": not flags, "flags": flags}, ensure_ascii=False))
