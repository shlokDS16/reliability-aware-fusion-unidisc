"""Isolated dispatch folder and post-check for one title/abstract screening session (D0036 and later TA batches).

Same isolation and model checks as full-text screening (tools/ft_dispatch.py, ft_isolation_check.py,
ft_model_check.py), with the title/abstract brief and criteria the earlier dual batches used
(research/review/screening/v2/SCREENER-BRIEF.md, criteria-v1.md).

    python -I tools/ta_dispatch.py build --role A|B --batch <batch file> --root <scratch dir> --log <dispatch-log.jsonl>
    python -I tools/ta_dispatch.py post  --folder <dispatch folder> --transcript <agent jsonl> --dest <repo dir> --log <batch-log.jsonl> [--vault <root>]

build: creates <root>/<role>-<batch stem>-<uuid4>/ holding only CONTRACT.md, SCREENER-BRIEF.md, criteria-v1.md,
the batch file and dispatch.json (output file name, screener label); appends one line to the dispatch log.
post: checks the output (every batch id exactly once, allowed decisions and codes, the role's label), runs the
isolation check and the model check on the transcript, and only if all pass copies the output to
<dest>/screener-<role>-<batch stem>.jsonl. Appends a result line to the batch log either way; exit 1 on any failure.
"""
import argparse, hashlib, json, shutil, subprocess, sys, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABEL = {"A": "A-claude-sonnet", "B": "B-claude-opus"}
MODEL = {"A": "claude-sonnet-5-5", "B": "claude-opus-5-5"}
CODES = {"", "X0", "X1", "X2", "X3", "X4", "X7", "X8"}
sha = lambda b: hashlib.sha256(b).hexdigest()


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def build(a):
    batch = Path(a.batch)
    name = f"{a.role}-{batch.stem}-{uuid.uuid4()}"
    d = Path(a.root) / name
    d.mkdir(parents=True)
    shutil.copy(ROOT / "research/CONTRACT.md", d / "CONTRACT.md")
    shutil.copy(ROOT / "research/review/screening/v2/SCREENER-BRIEF.md", d / "SCREENER-BRIEF.md")
    shutil.copy(ROOT / "research/review/screening/criteria-v1.md", d / "criteria-v1.md")
    shutil.copy(batch, d / batch.name)
    ids = [r["id"] for r in jl(batch)]
    out = f"screener-{a.role}-{batch.stem}.jsonl"
    disp = {"role": a.role, "model": MODEL[a.role], "screener_label": LABEL[a.role], "input_file": batch.name,
            "n": len(ids), "output_file": out}
    (d / "dispatch.json").write_text(json.dumps(disp, indent=1), encoding="utf-8")
    with open(a.log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"event": "built", "basename": name, "role": a.role, "model": MODEL[a.role], "batch": batch.stem,
                             "n": len(ids), "batch_sha256": sha(batch.read_bytes())}) + "\n")
    print(d)


def post(a):
    d = Path(a.folder)
    disp = json.load(open(d / "dispatch.json", encoding="utf-8"))
    role, out = disp["role"], d / disp["output_file"]
    ids = [r["id"] for r in jl(d / disp["input_file"])]
    res = {"event": "result", "basename": d.name, "role": role, "batch": Path(disp["input_file"]).stem,
           "transcript": Path(a.transcript).name, "problems": []}
    rows = jl(out) if out.exists() else []
    got = [r.get("id") for r in rows]
    if not out.exists():
        res["problems"].append("no output file")
    if sorted(got) != sorted(ids):
        res["problems"].append(f"ids: missing {sorted(set(ids) - set(got))[:10]}, extra {sorted(set(got) - set(ids))[:10]}, "
                               f"duplicated {len(got) - len(set(got))}")
    for r in rows:
        if r.get("decision") not in ("include", "exclude", "unclear") or r.get("code", "") not in CODES \
                or r.get("screener") != LABEL[role] or (r.get("decision") == "exclude") != bool(r.get("code")):
            res["problems"].append(f"bad row {r.get('id')}")
    iso_cmd = [sys.executable, "-I", str(ROOT / "tools/ft_isolation_check.py"), a.transcript, str(d)] + (["--vault", a.vault] if a.vault else [])
    iso = json.loads(subprocess.run(iso_cmd, capture_output=True, text=True).stdout.strip().splitlines()[-1])
    mod = json.loads(subprocess.run([sys.executable, "-I", str(ROOT / "tools/ft_model_check.py"), "--transcript", a.transcript,
                                     "--role", role], capture_output=True, text=True).stdout.strip().splitlines()[-1])
    res.update({"isolation_pass": iso["pass"], "isolation_flags": iso.get("flags", [])[:10], "model_ok": mod["pass"],
                "models": mod["models"], "n_rows": len(rows),
                "counts": {k: sum(r.get("decision") == k for r in rows) for k in ("include", "exclude", "unclear")}})
    ok = not res["problems"] and iso["pass"] and mod["pass"]
    res["filed"] = ok
    if ok:
        dest = Path(a.dest) / disp["output_file"]
        if dest.exists():
            raise SystemExit(f"refusing to overwrite {dest}")
        shutil.copy(out, dest)
        res["output_sha256"] = sha(dest.read_bytes())
    with open(a.log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(res) + "\n")
    print(json.dumps(res))
    sys.exit(0 if ok else 1)


ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=("build", "post"))
ap.add_argument("--role", choices="AB")
ap.add_argument("--batch")
ap.add_argument("--root")
ap.add_argument("--log", required=True)
ap.add_argument("--folder")
ap.add_argument("--transcript")
ap.add_argument("--dest")
ap.add_argument("--vault")
a = ap.parse_args()
build(a) if a.mode == "build" else post(a)
