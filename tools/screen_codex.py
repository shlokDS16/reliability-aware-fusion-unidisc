"""Screener B (protocol section 4): Codex screens title-and-abstract batches with the fixed criteria.

Each batch is one fresh read-only `codex exec` call (no thread is resumed: every batch must be
judged independently and identically). Prompt = criteria file + the batch's records. Output lines
are validated (one decision per sid, allowed values) and written to
research/review/screening/screener-B/batch-NN.jsonl; a run log row records the time, model,
criteria SHA-256, prompt SHA-256, response SHA-256 and exit code. Batches already done are
skipped, so the command resumes.

    python tools/screen_codex.py [--batches 1-15] [--model NAME] [--timeout 1200]
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCR = ROOT / "research" / "review" / "screening"
CRIT = SCR / "criteria-v1.md"
OUT = SCR / "screener-B"
ALLOWED = {"include", "exclude", "unclear"}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def parse(text: str, sids: list[str]) -> tuple[list[dict], list[str]]:
    got, problems = {}, []
    for line in text.splitlines():
        line = line.strip().strip("`")
        if not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("sid") in sids and d.get("decision") in ALLOWED:
            got[d["sid"]] = {"sid": d["sid"], "decision": d["decision"], "code": d.get("code", ""),
                             "reason": d.get("reason", "")}
    missing = [s for s in sids if s not in got]
    if missing:
        problems.append(f"missing {len(missing)}: {missing[:5]}")
    return [got[s] for s in sids if s in got], problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", default="1-15")
    ap.add_argument("--model", default=None)
    ap.add_argument("--timeout", type=int, default=1200)
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.batches.split("-"))
    exe = shutil.which("codex.cmd") or shutil.which("codex")
    if not exe:
        sys.exit("codex CLI not found on PATH")
    OUT.mkdir(parents=True, exist_ok=True)
    crit = CRIT.read_bytes()
    for b in range(lo, hi + 1):
        src = SCR / "batches" / f"batch-{b:02d}.jsonl"
        dst = OUT / f"batch-{b:02d}.jsonl"
        if dst.exists():
            print(f"batch {b:02d}: done, skipped")
            continue
        recs = [json.loads(l) for l in open(src, encoding="utf8")]
        sids = [r["sid"] for r in recs]
        body = "\n".join(json.dumps(r, ensure_ascii=False) for r in recs)
        prompt = (crit.decode("utf8") + "\n\nRECORDS (one JSON object per line):\n" + body +
                  f"\n\nReturn exactly {len(recs)} JSON lines, one per sid, and nothing else.")
        pfile = OUT / f"batch-{b:02d}.prompt.txt"
        pfile.write_text(prompt, encoding="utf8")
        rfile = OUT / f"batch-{b:02d}.response.txt"
        cmd = [exe, "exec", "--sandbox", "read-only", "--skip-git-repo-check", "--color", "never",
               "-C", str(OUT), "-o", str(rfile)] + (["-m", a.model] if a.model else []) + ["-"]
        t0 = dt.datetime.now(dt.timezone.utc)
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=a.timeout, cwd=str(OUT))
        raw = (r.stdout or "") + "\n--- stderr ---\n" + (r.stderr or "")
        (OUT / f"batch-{b:02d}.raw.log").write_text(raw, encoding="utf8")
        model = re.search(r"^model:\s*(\S+)", raw, re.M)
        text = rfile.read_text(encoding="utf8") if rfile.exists() else ""
        rows, problems = parse(text, sids)
        if rows and not problems:
            with open(dst, "w", encoding="utf8") as fh:
                fh.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in rows)
        log = {"ts": t0.isoformat(), "batch": b, "exit": r.returncode, "model": model.group(1) if model else a.model,
               "criteria_sha": sha(crit), "prompt_sha": sha(prompt.encode("utf8")),
               "response_sha": sha(text.encode("utf8")) if text else None, "n": len(rows),
               "problems": problems, "seconds": (dt.datetime.now(dt.timezone.utc) - t0).total_seconds()}
        with open(OUT / "run-log.jsonl", "a", encoding="utf8") as fh:
            fh.write(json.dumps(log) + "\n")
        print(f"batch {b:02d}: exit {r.returncode}, {len(rows)}/{len(sids)} decisions, {problems or 'ok'}")


if __name__ == "__main__":
    main()
