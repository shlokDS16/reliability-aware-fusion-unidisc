"""Build the one return message (plan v0.2 s9: one return per session) for a D0052 extraction session.

    python -I analysis/extraction/d0052/return_msg.py <batch>     -> prints the message; writes returns/<batch>.txt

Lists every fail-level validator finding of the session's pass-1 report (check, ref, status, detail) and asks the
session to correct only those entries of its output file. Nothing about other records or sessions is included.
"""
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
batch = sys.argv[1]
rows = [l.split() for l in (D / "agent-map.txt").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
base = [r for r in rows if r[0] == batch][-1][4]
F = [json.loads(l) for l in open(D / "validate-pass1.jsonl", encoding="utf-8") if l.strip()]
F = [f for f in F if f.get("session") == base and f.get("severity") == "fail"]
EXPL = {
    "not_found": "the quote is not a contiguous verbatim passage of the text file; copy it again character for character",
    "negation_before": "a negation or contrast word sits just before the quote in the same sentence; start the quote earlier",
    "negation_after": "a negation or contrast word follows the quote in the same sentence; extend the quote",
    "caption_start": "the caption must start with Table, Tab., Figure or Fig., as printed",
    "caption_not_found": "the caption is not on the stated page or the two next to it; check the page and the caption text",
    "schema_error": "the record does not match the schema; fix the named field",
    "benchmark_column_mismatch": "benchmark_printed must equal the column-map part you gave the role benchmark (and metric_printed the part with the role metric); where one header joins benchmark and metric, map them as the brief says",
    "cells_mismatch": "the row label was found but the cells you gave differ from the printed row; re-read the row in the text file",
    "map_not_in_header": "the column map names parts that are not in the printed header; use the header text as printed",
    "caption_length": "the caption quote is too short for the brief's caption rule; quote more of the printed caption",
    "s14_row_not_found": "give the row label exactly as it starts the printed row on that page, or fix the page",
    "metric_column_mismatch": "metric_printed must equal the column-map part you gave the role metric; map a split or benchmark part of the header as its own part, as the brief says",
    "where_mismatch":"the unit's 'where' and its cell's table differ; make them name the same table",
}
lines = [f"The validator did not accept some entries of your output file. Per the brief, they are returned to you once. "
         f"Correct only these entries, in place, with Read, Grep and Edit on paths from your earlier Glob result "
         f"(absolute paths inside your folder; no Bash or PowerShell). If an entry is right as it stands, leave it and say so.",
         ""]
for n, f in enumerate(F, 1):
    lines.append(f"({n}) {f['id']} {f['check']} {f.get('ref', '')}: {f['status']}"
                 + (f" ({str(f.get('detail'))[:160]})" if f.get("detail") else "")
                 + f" -> {EXPL.get(f['status'], 'see the brief')}")
lines += ["", "Reply with ONE line: how many entries you changed and how many you left as they were."]
msg = "\n".join(lines)
(D / "returns").mkdir(exist_ok=True)
(D / "returns" / f"{batch}.txt").write_text(msg, encoding="utf-8")
sys.stdout.buffer.write(msg.encode("utf-8") + b"\n")
