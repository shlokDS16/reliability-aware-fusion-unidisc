"""After an adjudicator (C) session ends: collect its rows, check isolation and quotes, log the session.

    python -I tools/ft_cpost.py <c batch> <dispatch root> <subagent transcript dir> <agent id> [--outcome complete|failed|discarded]

Copies FC-<batch>.jsonl into analysis/screening/ft-t1/c/<batch>/, runs tools/ft_isolation_check.py on the
transcript and analysis/screening/quote_check.py on the rows, and appends one line to
analysis/screening/c-run-log.jsonl (criteria-v1.6 section D: every C session is logged when it ends).
"""
import json, shutil, subprocess, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
batch, droot, tdir, agent = sys.argv[1:5]
outcome = sys.argv[sys.argv.index("--outcome") + 1] if "--outcome" in sys.argv else None
d = next(Path(droot).glob(f"C-{batch}-*"))
OUT = ROOT / "analysis/screening/ft-t1/c" / batch
OUT.mkdir(parents=True, exist_ok=True)
ids = json.loads((d / "dispatch.json").read_text(encoding="utf8"))["ids"]
f = d / f"FC-{batch}.jsonl"
rows = [json.loads(l) for l in f.read_text(encoding="utf8").splitlines() if l.strip()] if f.exists() else []
if f.exists():
    shutil.copy(f, OUT / f.name)
iso = json.loads(subprocess.run([sys.executable, "-I", str(ROOT / "tools/ft_isolation_check.py"), str(Path(tdir) / f"agent-{agent}.jsonl"), str(d)],
                                capture_output=True, text=True).stdout)
(OUT / "isolation-C.json").write_text(json.dumps({"basename": d.name, "agent": agent, **iso}), encoding="utf8")
qbad = None
if f.exists():
    subprocess.run([sys.executable, "-I", str(ROOT / "analysis/screening/quote_check.py"), "--rows", str(f), "--texts", str(d / "fulltext"),
                    "--out", str(OUT / "quote-check-C.jsonl")], capture_output=True, text=True)
    qbad = [json.loads(l) for l in (OUT / "quote-check-C.jsonl").read_text(encoding="utf8").splitlines() if l.strip()]
    qbad = sorted({(q["id"], q["i"], q["status"]) for q in qbad if q.get("status") != "found"})
got = {r["id"] for r in rows}
mc = json.loads(subprocess.run([sys.executable, "-I", str(ROOT / "tools/ft_model_check.py"), "--transcript", str(Path(tdir) / f"agent-{agent}.jsonl"),
                                "--role", "C"], capture_output=True, text=True).stdout)   # added 2026-10-20 (gate T1 finding)
res = {"event": "C-session", "batch": batch, "basename": d.name, "agent": agent, "model": "claude-fable-5-1",
       "model_ok": mc["pass"], "models_seen": mc["models"],
       "ended": datetime.datetime.now().isoformat(timespec="seconds"), "n": len(ids), "rows": len(rows),
       "missing": sorted(set(ids) - got), "isolation": iso["pass"], "isolation_flags": iso["flags"],
       "quotes_not_accepted": qbad, "decisions": {k: sum(1 for r in rows if r.get("decision") == k) for k in ("include", "exclude")},
       "outcome": outcome or ("complete" if iso["pass"] and mc["pass"] and not (set(ids) - got) else "check")}
with (ROOT / "analysis/screening/c-run-log.jsonl").open("a", encoding="utf8", newline="\n") as fh:
    fh.write(json.dumps(res, ensure_ascii=False) + "\n")
print(json.dumps(res, ensure_ascii=False))
