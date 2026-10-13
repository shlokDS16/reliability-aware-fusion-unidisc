"""Append-only research ledgers (JSON Lines) with schema checks.

    python tools/ledger.py init
    python tools/ledger.py add papers --file row.json
    python tools/ledger.py add decisions --json "{\"decision\": \"...\", ...}"
    python tools/ledger.py list hypotheses [--where status=open]
    python tools/ledger.py count

Rows are never edited or deleted. To change a fact, add a row that supersedes the old id.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent / "research" / "ledgers"

# ledger -> (id prefix, required keys)
SCHEMA = {
    "papers": ("P", ["title", "canonical_id", "url", "status", "cluster"]),
    "claims": ("C", ["statement", "source", "location", "status", "evidence_level"]),
    "hypotheses": ("H", ["observation", "claim", "mechanisms", "falsifier", "status"]),
    "experiments": ("X", ["hypothesis", "git_sha", "config", "seed", "status", "artifacts"]),
    "failures": ("F", ["symptom", "suspected_cause", "diagnostic", "outcome"]),
    "decisions": ("D", ["decision", "options", "evidence", "owner"]),
    "references": ("R", ["bibkey", "canonical_id", "verified_against", "status"]),
}
EVIDENCE = {"E0", "E1", "E2", "E3", "E4", "E5"}


def path(name: str) -> Path:
    if name not in SCHEMA:
        sys.exit(f"unknown ledger '{name}'. choose from: {', '.join(SCHEMA)}")
    return DIR / f"{name}.jsonl"


def rows(name: str) -> list[dict]:
    p = path(name)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def cmd_init(_: argparse.Namespace) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    for name in SCHEMA:
        path(name).touch()
    print(f"ledgers ready in {DIR}")


def cmd_add(args: argparse.Namespace) -> None:
    raw = Path(args.file).read_text(encoding="utf-8") if args.file else args.json
    if raw is None:
        raw = sys.stdin.read()
    row = json.loads(raw)
    prefix, required = SCHEMA[args.ledger]
    missing = [k for k in required if k not in row or row[k] in ("", None)]
    if missing:
        sys.exit(f"missing required keys for {args.ledger}: {missing}")
    if "evidence_level" in row and row["evidence_level"] not in EVIDENCE:
        sys.exit(f"evidence_level must be one of {sorted(EVIDENCE)}")
    row = {"id": f"{prefix}{len(rows(args.ledger)) + 1:04d}",
           "ts": dt.datetime.now().isoformat(timespec="seconds"), **row}
    with path(args.ledger).open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(row["id"])


def cmd_list(args: argparse.Namespace) -> None:
    out = rows(args.ledger)
    for cond in args.where or []:
        k, v = cond.split("=", 1)
        out = [r for r in out if str(r.get(k)) == v]
    for r in out[-args.last:]:
        print(json.dumps(r, ensure_ascii=False))


def cmd_count(_: argparse.Namespace) -> None:
    for name in SCHEMA:
        print(f"{name:<12} {len(rows(name))}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    a = sub.add_parser("add")
    a.add_argument("ledger")
    a.add_argument("--file")
    a.add_argument("--json")
    a.set_defaults(fn=cmd_add)
    ls = sub.add_parser("list")
    ls.add_argument("ledger")
    ls.add_argument("--where", action="append")
    ls.add_argument("--last", type=int, default=20)
    ls.set_defaults(fn=cmd_list)
    sub.add_parser("count").set_defaults(fn=cmd_count)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
