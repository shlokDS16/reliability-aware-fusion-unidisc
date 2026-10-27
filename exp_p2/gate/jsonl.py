"""Tolerant JSONL reader for probe-2 `items.jsonl` (SAP Addendum 1 N16). `common.append_jsonl` can glue a new row onto a partial line left by a hard kill; the strict
reader then loses the new row too. This reader recovers every complete object that has an `idx` key from a damaged line and reports how many rows were lost, so the
count can go in the results table. It reads only; probe code and the file are untouched."""
from __future__ import annotations

import json
from pathlib import Path


def read_jsonl_tolerant(path: Path, key: str = "idx") -> tuple[list[dict], dict]:
    path = Path(path)
    rows, rep = [], dict(n_lines=0, n_clean_lines=0, n_glued_lines=0, n_recovered_rows=0, n_unparseable_lines=0)
    if not path.exists():
        return rows, dict(rep, exists=False)
    dec = json.JSONDecoder()
    for line in path.read_text(encoding="utf8").splitlines():
        line = line.strip()
        if not line:
            continue
        rep["n_lines"] += 1
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                rows.append(obj)
                rep["n_clean_lines"] += 1
                continue
        except json.JSONDecodeError:
            pass
        found, pos = [], line.find("{")
        while pos != -1:
            try:
                obj, end = dec.raw_decode(line, pos)
                if isinstance(obj, dict) and key in obj:
                    found.append(obj)
                    pos = line.find("{", end)
                    continue
            except json.JSONDecodeError:
                pass
            pos = line.find("{", pos + 1)
        if found:
            rows.extend(found)
            rep["n_glued_lines"] += 1
            rep["n_recovered_rows"] += len(found)
        else:
            rep["n_unparseable_lines"] += 1
    rep["exists"] = True
    return rows, rep


def probe2_row_report(run_dir: Path, array_idx: list[int]) -> dict:
    """Rows recovered versus the items whose arrays exist. Arrays are written before the row, so an item with arrays but no recoverable row lost only its row: its arrays
    are complete and the analysis keeps it; the loss count is reported."""
    rows, rep = read_jsonl_tolerant(Path(run_dir) / "items.jsonl")
    have = {r["idx"] for r in rows}
    return dict(rep, n_rows=len(have), n_array_items=len(array_idx), rows_lost_arrays_present=sorted(set(array_idx) - have), rows_without_arrays=sorted(have - set(array_idx)),
                n_duplicate_rows=len(rows) - len(have))
