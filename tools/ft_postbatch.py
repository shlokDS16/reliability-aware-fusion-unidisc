"""After both screeners of a full-text batch finish: collect rows, check isolation and quotes, log agreement.

    python tools/ft_postbatch.py <batch> <dispatch root> <subagent transcript dir> <agentA id> <agentB id> [--root-A <dir>]

--root-A: dispatch root of role A when A ran in an earlier session (its transcript names that folder).
Tranche: environment variable FT_TRANCHE (default t1) selects analysis/screening/ft-<tranche>/ (2026-10-20: r797, s1243).

Copies F{A,B}-<batch>.jsonl into analysis/screening/ft-t1/<batch>/, runs tools/ft_isolation_check.py on
both transcripts and analysis/screening/quote_check.py on both row files, and appends one line to
analysis/screening/ft-t1/batch-log.jsonl (n, rows per screener, ids missing, isolation pass, quotes not
accepted, decision agreement, disagreement ids, adjudicate ids). Prints that line.
"""
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
batch, droot, tdir, aid, bid = sys.argv[1:6]
BASE = ROOT / "analysis/screening" / f"ft-{os.environ.get('FT_TRANCHE', 't1')}"
OUT = BASE / batch
OUT.mkdir(parents=True, exist_ok=True)
res = {"batch": batch}
rows = {}
for role, agent in (("A", aid), ("B", bid)):
    r = sys.argv[sys.argv.index("--root-A") + 1] if role == "A" and "--root-A" in sys.argv else droot
    d = next(Path(r).glob(f"{role}-{batch}-*"))
    ids = json.loads((d / "dispatch.json").read_text(encoding="utf8"))["ids"]
    f = d / f"F{role}-{batch}.jsonl"
    rr = [json.loads(l) for l in f.read_text(encoding="utf8").splitlines() if l.strip()] if f.exists() else []
    shutil.copy(f, OUT / f.name) if f.exists() else None
    rows[role] = {r["id"]: r for r in rr}
    res[f"rows_{role}"] = len(rr)
    res[f"missing_{role}"] = sorted(set(ids) - set(rows[role]))
    iso = json.loads(subprocess.run([sys.executable, "-I", str(ROOT / "tools/ft_isolation_check.py"), str(Path(tdir) / f"agent-{agent}.jsonl"), str(d)],
                                    capture_output=True, text=True).stdout)
    res[f"isolation_{role}"] = iso["pass"]
    mc = json.loads(subprocess.run([sys.executable, "-I", str(ROOT / "tools/ft_model_check.py"), "--transcript", str(Path(tdir) / f"agent-{agent}.jsonl"),
                                    "--role", role], capture_output=True, text=True).stdout)
    res[f"model_ok_{role}"] = mc["pass"]           # criteria v1.6 s4 item 1: no fallback model (added 2026-10-20)
    if not mc["pass"]:
        res[f"models_{role}"] = mc["models"]
    (OUT / f"isolation-{role}.json").write_text(json.dumps({"basename": d.name, "agent": agent, **iso}), encoding="utf8")
    if f.exists():
        q = subprocess.run([sys.executable, "-I", str(ROOT / "analysis/screening/quote_check.py"), "--rows", str(f), "--texts", str(d / "fulltext"),
                            "--out", str(OUT / f"quote-check-{role}.jsonl")], capture_output=True, text=True).stdout
        bad = [json.loads(l) for l in (OUT / f"quote-check-{role}.jsonl").read_text(encoding="utf8").splitlines() if l.strip()]
        res[f"quotes_not_accepted_{role}"] = sum(1 for b in bad if b.get("status") != "found")
common = sorted(set(rows["A"]) & set(rows["B"]))
dis = [i for i in common if rows["A"][i]["decision"] != rows["B"][i]["decision"]]
res.update(n=len(common), agree=len(common) - len(dis), disagree=dis,
           adjudicate=sorted(i for i in common if "adjudicate" in (rows["A"][i]["decision"], rows["B"][i]["decision"])),
           include_both=sum(1 for i in common if rows["A"][i]["decision"] == rows["B"][i]["decision"] == "include"))
with (BASE / "batch-log.jsonl").open("a", encoding="utf8") as fh:
    fh.write(json.dumps(res) + "\n")
print(json.dumps(res))
