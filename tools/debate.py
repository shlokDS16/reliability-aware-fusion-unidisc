"""Logged two-model debate between Claude (this session) and Codex (GPT).

    python tools/debate.py new <slug> --topic "..." [--session <claude-session-id>]
    python tools/debate.py claude <debate-dir> --file turn.md
    python tools/debate.py codex  <debate-dir> [--model <name>] [--timeout 900]
    python tools/debate.py status <debate-dir>

Every turn is a file (`round-NN-<speaker>.md`) plus a row in the debate's `log.jsonl` and in the
project-wide `research/debates/index.jsonl`: time, duration, working folder, Claude session,
Codex session, model, prompt and response paths with SHA-256.

Isolation from other sessions that use Codex: each Codex turn is a fresh `codex exec` run in a
read-only sandbox, started in the debate folder, and is sent the whole transcript. Nothing is
resumed with `--last`, so another session's thread can never be picked up.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEBATES = ROOT / "research" / "debates"

RULES = """You are one of two senior researchers in a recorded debate. The other is Claude.
Rules for your turn:
1. Do not agree to be agreeable. Concede a point only when the argument or evidence compels it,
   and say what compelled you.
2. For each numbered claim in the latest turn answer ACCEPT, REJECT or NEEDS-EVIDENCE with a reason.
3. Give the strongest counter-argument to the other side's main position, and the cheapest
   observation that would settle the disagreement.
4. Cite a paper only if you are sure it exists; otherwise write "unverified". Never invent IDs.
5. You have no need to edit files or run experiments. Reason from the transcript.
6. End with four short sections: POSITION, CONCESSIONS, OPEN DISAGREEMENTS, WHAT WOULD CHANGE MY MIND.
Keep the turn under 700 words.
"""


def now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def turns(d: Path) -> list[Path]:
    return sorted(d.glob("round-*-*.md"))


def log(d: Path, row: dict) -> None:
    row = {"ts": now(), "debate": d.name, "cwd": str(d), **row}
    for f in (d / "log.jsonl", DEBATES / "index.jsonl"):
        with f.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def cmd_new(a: argparse.Namespace) -> None:
    d = DEBATES / f"{dt.date.today().isoformat()}-{a.slug}"
    d.mkdir(parents=True, exist_ok=False)
    meta = {"topic": a.topic, "created": now(), "claude_session": a.session, "project": str(ROOT)}
    (d / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    log(d, {"event": "created", **meta})
    print(d)


def cmd_claude(a: argparse.Namespace) -> None:
    d = Path(a.dir)
    n = len(turns(d)) + 1
    out = d / f"round-{n:02d}-claude.md"
    shutil.copyfile(a.file, out)
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    log(d, {"event": "turn", "speaker": "claude", "round": n, "response": out.name,
            "response_sha": sha(out), "claude_session": meta.get("claude_session")})
    print(out)


def cmd_codex(a: argparse.Namespace) -> None:
    d = Path(a.dir)
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    prior = turns(d)
    if not prior or "claude" not in prior[-1].name:
        sys.exit("the last turn must be Claude's before Codex replies")
    n = len(prior) + 1
    transcript = "\n\n".join(f"===== {p.stem} =====\n{p.read_text(encoding='utf-8')}" for p in prior)
    prompt = d / f"round-{n:02d}-codex.prompt.txt"
    prompt.write_text(f"{RULES}\nTOPIC: {meta['topic']}\n\nTRANSCRIPT SO FAR:\n{transcript}\n\n"
                      "Write your turn now.", encoding="utf-8")
    out = d / f"round-{n:02d}-codex.md"
    raw = d / f"round-{n:02d}-codex.raw.log"
    exe = shutil.which("codex.cmd") or shutil.which("codex")
    if not exe:
        sys.exit("codex CLI not found on PATH")
    cmd = [exe, "exec", "--sandbox", "read-only", "--skip-git-repo-check", "--color", "never",
           "-C", str(d), "-o", str(out)]
    if a.model:
        cmd += ["-m", a.model]
    cmd.append("-")
    t0 = time.time()
    r = subprocess.run(cmd, input=prompt.read_text(encoding="utf-8"), capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=a.timeout)
    raw.write_text((r.stdout or "") + "\n--- stderr ---\n" + (r.stderr or ""), encoding="utf-8")
    text = raw.read_text(encoding="utf-8")
    sid = re.search(r"session id:\s*([0-9a-fA-F-]{8,})", text)
    model = re.search(r"^model:\s*(\S+)", text, re.M)
    ok = r.returncode == 0 and out.exists() and out.stat().st_size > 0
    log(d, {"event": "turn", "speaker": "codex", "round": n, "exit": r.returncode, "ok": ok,
            "seconds": round(time.time() - t0, 1), "codex_session": sid.group(1) if sid else None,
            "model": model.group(1) if model else a.model, "prompt": prompt.name,
            "prompt_sha": sha(prompt), "response": out.name if ok else None,
            "response_sha": sha(out) if ok else None, "raw_log": raw.name,
            "claude_session": meta.get("claude_session")})
    if not ok:
        sys.exit(f"codex turn failed (exit {r.returncode}); see {raw}")
    print(out)


def cmd_status(a: argparse.Namespace) -> None:
    d = Path(a.dir)
    for line in (d / "log.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        print(r["ts"], r.get("event"), r.get("speaker", ""), r.get("round", ""),
              r.get("seconds", ""), r.get("codex_session") or "")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new"); n.add_argument("slug"); n.add_argument("--topic", required=True)
    n.add_argument("--session"); n.set_defaults(fn=cmd_new)
    c = sub.add_parser("claude"); c.add_argument("dir"); c.add_argument("--file", required=True)
    c.set_defaults(fn=cmd_claude)
    x = sub.add_parser("codex"); x.add_argument("dir"); x.add_argument("--model")
    x.add_argument("--timeout", type=int, default=900); x.set_defaults(fn=cmd_codex)
    s = sub.add_parser("status"); s.add_argument("dir"); s.set_defaults(fn=cmd_status)
    a = ap.parse_args()
    DEBATES.mkdir(parents=True, exist_ok=True)
    a.fn(a)


if __name__ == "__main__":
    main()
