"""Landmark tranche (D0061) copy of analysis/extraction/d0052/postbatch.py: paths point to analysis/extraction/lmk and
session bfefb6fe's dispatch root and subagent dir; logic unchanged.

After one D0052 extraction session ends: model check, isolation check, validator (pass 1 or 2), copy to the repo.

    python -I analysis/extraction/lmk/postbatch.py <batch> [--pass 2]

Reads analysis/extraction/d0052/agent-map.txt (batch role alias agent folder-basename) and the session's transcript
(<subagents dir>/agent-<agent>.jsonl). Runs tools/ft_model_check.py --transcript --role <alias> (EA = B,
claude-opus-5-5; EB = A, claude-sonnet-5-5; EC = C, claude-fable-5-1), tools/ft_isolation_check.py and
tools/ex_validate_batch.py (--pass 1 into validate-pass1.jsonl, or --pass 2 into validate-pass2.jsonl with the pass-1
report as --first-pass). Copies dispatch.json and the output file into analysis/extraction/d0052/<role>/<batch>/ and
appends one line to analysis/extraction/d0052/batch-log.jsonl. Prints that line. A session that fails the model or
isolation check is logged with usable false; its records are not used (plan: rerun by a new session).
"""
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
D = ROOT / "analysis/extraction/lmk"
DISP = Path(r"C:/Users/Shlok/AppData/Local/Temp/claude/C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-resume-dlm-discovery-exp-003-334706/bfefb6fe-654c-43b1-a1f0-c80e3f972b2f/scratchpad/ex-dispatch")
SUB = Path(r"C:/Users/Shlok/.claude/projects/C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-resume-dlm-discovery-exp-003-334706/bfefb6fe-654c-43b1-a1f0-c80e3f972b2f/subagents")


def run(*a):
    p = subprocess.run([sys.executable, "-I", *map(str, a)], capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout, p.stderr


batch = sys.argv[1]
pss = 2 if "--pass" in sys.argv and sys.argv[sys.argv.index("--pass") + 1] == "2" else 1
rows = [l.split() for l in (D / "agent-map.txt").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
row = [r for r in rows if r[0] == batch][-1]
_, role, alias, agent, base = row
folder = DISP / base
tr = SUB / f"agent-{agent}.jsonl"
assert folder.is_dir() and tr.exists(), (folder, tr)
rc, out, err = run(ROOT / "tools/ft_model_check.py", "--transcript", tr, "--role", alias)
model = json.loads(out.strip().splitlines()[-1]) if out.strip() else {"pass": False, "error": err[-300:]}
rc, out, err = run(ROOT / "tools/ft_isolation_check.py", tr, folder)
iso = json.loads(out.strip().splitlines()[-1]) if out.strip() else {"pass": False, "error": err[-300:]}
dj = json.loads((folder / "dispatch.json").read_text(encoding="utf-8"))
name = dj["output_file"]
# the session can write inside its folder, so dispatch.json is not trusted as a path: plain file name, .jsonl, inside
assert name == f"{role}-{batch}.jsonl" and "/" not in name and "\\" not in name, name
outf = folder / name
assert outf.resolve().is_relative_to(folder.resolve()), outf
dest = D / role / batch
dest.mkdir(parents=True, exist_ok=True)
shutil.copy2(folder / "dispatch.json", dest / "dispatch.json")
recs = []
if outf.exists():
    shutil.copy2(outf, dest / (outf.stem + (f"-pass{pss}" if pss == 2 else "") + outf.suffix))
    recs = [json.loads(l)["id"] for l in outf.read_text(encoding="utf-8").splitlines() if l.strip().startswith("{")]
rep = D / f"validate-pass{pss}.jsonl"
args = [ROOT / "tools/ex_validate_batch.py", "--session", folder, "--lookups", ROOT / "analysis/extraction/lookups",
        "--out", rep, "--pass", str(pss)]
if rep.exists():
    args.append("--append")
if pss == 2:
    args += ["--first-pass", D / "validate-pass1.jsonl"]
vrc, vout, verr = run(*args) if outf.exists() else (2, "", "no output file")
fails = []
for l in vout.splitlines():
    if '"fail"' in l or "FAIL" in l:
        fails.append(l[:300])
line = {"batch": batch, "role": role, "agent": agent, "basename": base, "pass": pss,
        "ended_logged": datetime.now().isoformat(timespec="seconds"), "ids": dj.get("ids"), "records": recs,
        "model_ok": model.get("pass"), "models": model.get("models"), "isolation": iso.get("pass"),
        "isolation_flags": iso.get("flags", [])[:10], "validator_exit": vrc,
        "validator_summary": vout.strip().splitlines()[-1][:400] if vout.strip() else verr[-400:],
        "usable": bool(model.get("pass") and iso.get("pass") and outf.exists())}
with open(D / "batch-log.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(line) + "\n")
print(json.dumps(line))
if vout.strip():
    print(vout.strip()[-3000:])
