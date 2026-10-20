"""Batch driver for tools/ex_validate.py: one call validates every record of one or more extractor sessions and
writes the concatenated report in the format analysis/extraction/agreement.py reads (--validator).
(EXTRACTION-PLAN-v0.2 s6.4-s6.5 and s9 as amended by v0.3-v0.5; analysis/extraction/stageA-gaps-log.txt G1.)

    python -I tools/ex_validate_batch.py --session <dispatch folder> [--session <folder> ...] --lookups <dir>
        --out <report.jsonl> [--pass 1|2] [--append] [--first-pass <report.jsonl>] [--output-file <jsonl>]
    python -I tools/ex_validate_batch.py --self-test

A session is a folder made by tools/ex_dispatch.py (role EA or EB): dispatch.json, fulltext/<id>.txt, the schema
copy and the extractor's output file (dispatch.json "output_file", <EA|EB>-<batch>.jsonl, one JSON record per line;
--output-file overrides it for a single session). For each session the driver
  - checks that the folder's schema copy has the sha256 dispatch.json names (else exit 2);
  - splits the output file into records; a line that is not a JSON object, a record whose id was not dispatched to
    this session, a second record with the same id, and a dispatched id with no record are findings (check
    "session", severity fail) and are not validated;
  - validates each record with ex_validate.validate_record against the dispatched text fulltext/<id>.txt and the
    shared direction list (ex_validate's KA1(b) list plus <lookups>/metric-ids-v1.csv);
  - adds the record-level block checks of plan v0.2 s6.4 (check "blocks"): the record's blocks equal dispatch.json's
    blocks for that id; no content in a block that was not dispatched (L: design, census, claims.CT, study fields
    other than main_comparison; Q: qa, claims.list, study.main_comparison; H: units_h; K: groups, units_k); study
    present when L was dispatched (schema: "Null only if 'L' is not in blocks") and qa present when Q was; and the
    record's extractor equals dispatch.json's extractor (check "session");
  - tags every line with "pass" (1 = first pass, 2 = the re-run after the one return to the session, plan s9) and
    "session" (the folder's basename). agreement.py counts lines with pass 1 only.
Pass rules: --pass 1 refuses an (id, extractor) that already has pass-1 lines in the --out file it appends to;
--pass 2 needs a first-pass report (--first-pass, or the --out file itself with --append) holding a pass-1 summary
for every (id, extractor) it writes, and refuses one that already has pass-2 lines there (one return only).
Output lines: ex_validate's finding lines and summary line per record (plus "pass" and "session"); stdout gets one
line per record and a total line. Nothing is written when an input is refused. Exit 0 if no check fails, 1 if any
check fails, 2 on a usage, input or refusal error.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = "ex_validate_batch.py 1.0.0 (extraction form v0.5)"
SAFE = re.compile(r"^[A-Za-z0-9_-]+$")
BLOCK_ORDER = "LQHK"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


EV = _load("ex_validate_for_batch", ROOT / "tools" / "ex_validate.py")


class Refused(SystemExit):
    def __init__(self, msg):
        super().__init__(2)
        self.msg = msg


def refuse(msg):
    raise Refused(f"ex_validate_batch.py: {msg} (nothing written)")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def _empty(v):
    return v is None or v == [] or v == {} or v == ""


# ------------------------------------------------------------------------------------------------ block checks
def check_blocks(rec, dispatched, rep):
    """Plan v0.2 s6.4 'blocks present match dispatch.json', as findings on the record's Report."""
    got = rec.get("blocks")
    want = [c for c in BLOCK_ORDER if c in dispatched]
    if not isinstance(got, list) or sorted(set(map(str, got))) != sorted(want) or len(got) != len(set(map(str, got))):
        rep.fail("blocks", "blocks", "blocks_mismatch", f"record {got!r}, dispatch.json {''.join(want)}")
    else:
        rep.ok("blocks", "blocks", "pass", "".join(want))
    study = rec.get("study") if isinstance(rec.get("study"), dict) else None
    claims = rec.get("claims") if isinstance(rec.get("claims"), dict) else None
    outside = []
    if "L" not in want:
        outside += [f for f in ("design", "census") if not _empty(rec.get(f))]
        if claims and not _empty(claims.get("CT")):
            outside.append("claims.CT")
        if study:
            outside += [f"study.{k}" for k, v in study.items() if k != "main_comparison" and not _empty(v)]
        elif not _empty(rec.get("study")):
            outside.append("study")
    if "Q" not in want:
        if not _empty(rec.get("qa")):
            outside.append("qa")
        if claims and not _empty(claims.get("list")):
            outside.append("claims.list")
        if study and not _empty(study.get("main_comparison")):
            outside.append("study.main_comparison")
    if "H" not in want and not _empty(rec.get("units_h")):
        outside.append("units_h")
    if "K" not in want:
        outside += [f for f in ("groups", "units_k") if not _empty(rec.get(f))]
    for f in outside:
        rep.fail("blocks", f, "content_outside_blocks", f"{f} filled but its block was not dispatched")
    if "L" in want and rec.get("study") is None:
        rep.fail("blocks", "study", "block_content_missing", "study is null but block L was dispatched")
    if "Q" in want and rec.get("qa") is None:
        rep.fail("blocks", "qa", "block_content_missing", "qa is null but block Q was dispatched")


# ------------------------------------------------------------------------------------------------ sessions
def read_dispatch(folder):
    folder = Path(folder)
    dp = folder / "dispatch.json"
    if not dp.is_file():
        refuse(f"{folder}: no dispatch.json")
    d = json.loads(dp.read_text(encoding="utf-8"))
    if d.get("role") not in ("EA", "EB"):
        refuse(f"{folder}: role {d.get('role')!r}; the batch driver validates EA and EB sessions")
    ids = d.get("ids") or []
    bad = [i for i in ids if not isinstance(i, str) or not SAFE.match(i)]
    if bad or not ids:
        refuse(f"{folder}: dispatch.json ids missing or unsafe: {bad[:5]}")
    if set(d.get("blocks") or {}) != set(ids):
        refuse(f"{folder}: dispatch.json blocks do not cover exactly its ids")
    schema_name = (d.get("versions") or {}).get("schema")
    schema_sha = (d.get("versions") or {}).get("schema_sha256")
    sp = folder / (schema_name or "")
    if not schema_name or not sp.is_file():
        refuse(f"{folder}: schema copy {schema_name!r} not found")
    if sha(sp.read_bytes()) != schema_sha:
        refuse(f"{folder}: schema copy sha256 differs from dispatch.json")
    for i in ids:
        if not (folder / "fulltext" / f"{i}.txt").is_file():
            refuse(f"{folder}: no dispatched text fulltext/{i}.txt")
    return d, sp


def session_lines(folder, output_file, lookup, lookup_sha, p):
    """All report lines of one session (dicts), with the pass and session tags."""
    folder = Path(folder)
    d, schema_path = read_dispatch(folder)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_sha = sha(schema_path.read_bytes())
    out_path = Path(output_file) if output_file else folder / d["output_file"]
    if not out_path.is_file():
        refuse(f"{folder}: extractor output {out_path.name} not found")
    ext, ids = d["extractor"], list(d["ids"])
    tag = {"pass": p, "session": folder.name}
    lines, seen = [], set()

    def finding(rid, extractor, ref, status, detail):
        lines.append({"id": rid, "extractor": extractor, "check": "session", "ref": ref, "status": status,
                      "severity": "fail", "detail": detail, **tag})

    raw = out_path.read_bytes().split(b"\n")
    for n, b in enumerate(raw, start=1):
        b = b.rstrip(b"\r")
        if not b.strip():
            continue
        try:
            rec = json.loads(b.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            finding(None, ext, f"line {n}", "json_error", f"{type(exc).__name__}: {exc}")
            continue
        if not isinstance(rec, dict):
            finding(None, ext, f"line {n}", "not_an_object", type(rec).__name__)
            continue
        rid, rext = rec.get("id"), rec.get("extractor")
        if rid not in ids:
            finding(rid if isinstance(rid, str) else None, rext if isinstance(rext, str) else ext, f"line {n}",
                    "id_not_dispatched", f"id {rid!r} is not in this session's dispatch.json")
            continue
        if rid in seen:
            finding(rid, rext if isinstance(rext, str) else ext, f"line {n}", "duplicate_record", "a second record with this id")
            continue
        seen.add(rid)
        text_path = folder / "fulltext" / f"{rid}.txt"
        rep, engine = EV.validate_record(rec, EV.Text.from_file(text_path), schema, lookup)
        if rext != ext:
            rep.fail("session", "extractor", "extractor_mismatch", f"record {rext!r}, dispatch.json {ext!r}")
        check_blocks(rec, d["blocks"][rid], rep)
        hashes = {"record_sha256": sha(b), "text_sha256": sha(text_path.read_bytes()), "schema_sha256": schema_sha,
                  "metric_lookup_sha256": lookup_sha}
        for x in EV.report_lines(rep, engine, hashes):
            lines.append({**x, **tag})
    for i in ids:
        if i not in seen:
            finding(i, ext, i, "record_missing", "dispatched id with no record in the output file")
    return lines


def _keys(lines, p, summary_only=False):
    return {(l.get("id"), l.get("extractor")) for l in lines
            if int(l.get("pass", 1) or 1) == p and (l.get("summary") or not summary_only)}


def read_report(path):
    path = Path(path)
    if not path.is_file():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def run(a):
    if a.output_file and len(a.session) != 1:
        refuse("--output-file needs exactly one --session")
    if a.pass_ not in (1, 2):
        refuse("--pass must be 1 or 2")
    out = Path(a.out)
    if out.exists() and not a.append:
        refuse(f"{out} exists (use --append to add sessions or a second pass)")
    mp = Path(a.lookups) / "metric-ids-v1.csv"
    if not mp.is_file():
        refuse(f"lookup file missing: {mp}")
    try:
        lookup = EV.load_metric_lookup(mp)
    except ValueError as exc:
        refuse(f"metric lookup: {exc}")
    lookup_sha = sha(mp.read_bytes())
    lines = []
    for s in a.session:
        lines += session_lines(s, a.output_file, lookup, lookup_sha, a.pass_)
    existing = read_report(out) if a.append else []
    new_keys = {(l.get("id"), l.get("extractor")) for l in lines}
    if a.pass_ == 1:
        dup = sorted(map(str, new_keys & _keys(existing, 1)))
        if dup:
            refuse(f"first-pass lines already in {out} for {dup[:5]}")
    else:
        fp = Path(a.first_pass) if a.first_pass else (out if a.append else None)
        if fp is None or not fp.is_file():
            refuse("--pass 2 needs the first-pass report (--first-pass, or --out with --append)")
        first = read_report(fp)
        validated = {(l.get("id"), l.get("extractor")) for l in lines if l.get("summary")}
        missing = sorted(map(str, validated - _keys(first, 1, summary_only=True)))
        if missing:
            refuse(f"no first-pass summary for {missing[:5]}: a second pass follows a returned first pass")
        again = sorted(map(str, validated & (_keys(first, 2) | _keys(existing, 2))))
        if again:
            refuse(f"second-pass lines already exist for {again[:5]} (one return only, plan s9)")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a" if a.append else "w", encoding="utf-8", newline="\n") as f:
        for l in lines:
            f.write(json.dumps(l, ensure_ascii=True) + "\n")
    summaries = [l for l in lines if l.get("summary")]
    session_fail = sum(1 for l in lines if l.get("check") == "session" and not l.get("summary") and l["severity"] == "fail")
    for x in summaries:
        print(json.dumps({"id": x["id"], "extractor": x["extractor"], "session": x["session"], "pass": x["pass"],
                          "status": x["status"], "fail": x["fail"], "warn": x["warn"], "route": x["route"]}))
    n_fail = sum(1 for l in lines if l.get("severity") == "fail")
    print(json.dumps({"total": True, "tool": TOOL, "pass": a.pass_, "sessions": len(a.session), "records": len(summaries),
                      "accepted": sum(1 for x in summaries if x["status"] == "accepted"),
                      "rejected": sum(1 for x in summaries if x["status"] == "rejected"),
                      "session_findings": session_fail, "out": str(out)}))
    return 1 if n_fail else 0


# ------------------------------------------------------------------------------------------------ self-test
def _st_folder(root, role, batch, ids_blocks, texts):
    """A dispatch-shaped session folder (no ex_dispatch call): dispatch.json, schema copy, fulltext/."""
    d = Path(root) / f"{role}-{batch}-selftest"
    (d / "fulltext").mkdir(parents=True)
    schema = EV.DEFAULT_SCHEMA.read_bytes()
    (d / EV.DEFAULT_SCHEMA.name).write_bytes(schema)
    for i, t in texts.items():
        (d / "fulltext" / f"{i}.txt").write_text("\n".join(t) + "\n", encoding="utf-8")
    disp = {"role": role, "model": "test-model", "extractor": f"{role}-test-model", "batch": batch, "form_version": "0.5",
            "ids": list(ids_blocks), "blocks": {i: list(b) for i, b in ids_blocks.items()},
            "output_file": f"{role}-{batch}.jsonl",
            "versions": {"schema": EV.DEFAULT_SCHEMA.name, "schema_sha256": sha(schema)}}
    (d / "dispatch.json").write_text(json.dumps(disp, indent=1), encoding="utf-8")
    return d, disp


def self_test(verbose=True):
    """Built-in synthetic sessions (ex_validate's synthetic sign record); returns the number of failed checks."""
    import io  # noqa: PLC0415
    from contextlib import redirect_stdout  # noqa: PLC0415
    results = []

    def check(desc, ok):
        results.append(bool(ok))
        if verbose:
            print(f"self-test {len(results):2d} {'ok  ' if ok else 'FAIL'} {desc}")

    def rec(rid, extractor, hib=True, blocks=("K",)):
        r = EV._st_sign_record([EV._st_kunit("K01", 1, "Acc.", "Acc. ↑", hib)])
        r.update(id=rid, extractor=extractor, blocks=list(blocks))
        return r

    def call(argv):
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                code = main(argv)
        except Refused as exc:
            return 2, exc.msg
        return code, buf.getvalue()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        lk = tmp / "lookups"
        lk.mkdir()
        (lk / "metric-ids-v1.csv").write_text("printed,id,higher_is_better\nacc.,accuracy,true\n", encoding="utf-8")
        txt = {"S00001": EV._SIGN_LINES, "S00002": EV._SIGN_LINES}
        da, _ = _st_folder(tmp, "EA", "st1", {"S00001": "K", "S00002": "K"}, txt)
        db, _ = _st_folder(tmp, "EB", "st1", {"S00001": "K", "S00002": "K"}, txt)
        a1, a2 = rec("S00001", "EA-test-model"), rec("S00002", "EA-test-model", hib=False)     # a2: arrow conflict
        (da / "EA-st1.jsonl").write_text(json.dumps(a1) + "\n" + json.dumps(a2) + "\n", encoding="utf-8")
        b1 = rec("S00001", "EB-test-model", blocks=("H", "K"))                                  # blocks mismatch
        b1x = rec("S00009", "EB-test-model")                                                     # not dispatched
        (db / "EB-st1.jsonl").write_text(json.dumps(b1) + "\n" + json.dumps(b1) + "\n" + json.dumps(b1x) + "\n{bad\n",
                                         encoding="utf-8")
        out = tmp / "report.jsonl"
        code, so = call(["--session", str(da), "--session", str(db), "--lookups", str(lk), "--out", str(out)])
        rows = read_report(out)
        summ = {(r["id"], r["extractor"]): r for r in rows if r.get("summary")}
        check("two sessions -> one report; exit 1 when any check fails", code == 1 and len(summ) == 3)
        check("every line carries pass 1 and its session", rows and all(r.get("pass") == 1 for r in rows)
              and {r["session"] for r in rows} == {da.name, db.name})
        check("EA record 1 accepted, record 2 rejected (arrow_conflict)",
              summ[("S00001", "EA-test-model")]["status"] == "accepted" and summ[("S00002", "EA-test-model")]["status"] == "rejected")
        sess = {(r["id"], r["status"]) for r in rows if r.get("check") == "session"}
        check("session findings: duplicate, not dispatched, bad JSON line, missing record",
              {("S00001", "duplicate_record"), ("S00009", "id_not_dispatched"), (None, "json_error"),
               ("S00002", "record_missing")} <= sess)
        check("blocks checked against dispatch.json (blocks_mismatch for EB S00001)",
              any(r.get("check") == "blocks" and r.get("status") == "blocks_mismatch" and r["id"] == "S00001" for r in rows))
        need = {"id", "extractor", "check", "ref", "status", "severity", "detail", "pass"}
        check("lines carry agreement's reader fields; one summary per validated record",
              all(need <= set(r) for r in rows if not r.get("summary")) and len(summ) == 3)
        code2, _ = call(["--session", str(da), "--lookups", str(lk), "--out", str(out), "--append"])
        check("a second first pass for the same records is refused", code2 == 2)
        a2b = rec("S00002", "EA-test-model", hib=True)
        (da / "EA-st1.jsonl").write_text(json.dumps(a1) + "\n" + json.dumps(a2b) + "\n", encoding="utf-8")
        code3, _ = call(["--session", str(da), "--lookups", str(lk), "--out", str(out), "--append", "--pass", "2"])
        rows3 = read_report(out)
        check("second pass appended with pass 2; the first-pass lines are unchanged",
              code3 == 0 and rows3[:len(rows)] == rows and rows3[len(rows):]
              and all(r.get("pass") == 2 for r in rows3[len(rows):]))
        code4, _ = call(["--session", str(da), "--lookups", str(lk), "--out", str(out), "--append", "--pass", "2"])
        check("a second return (another pass 2) is refused", code4 == 2)
        code5, _ = call(["--session", str(da), "--lookups", str(lk), "--out", str(tmp / "p2.jsonl"), "--pass", "2"])
        check("pass 2 without a first-pass report is refused and writes nothing", code5 == 2 and not (tmp / "p2.jsonl").exists())
        code6, _ = call(["--session", str(da), "--lookups", str(lk), "--out", str(out)])
        check("an existing --out without --append is refused", code6 == 2)
        r = rec("S00001", "EA-test-model", blocks=("K",))
        r["qa"] = {"QA1": {}}
        rp = EV.Report("S00001", "EA-test-model")
        check_blocks(r, ["K"], rp)
        rq = EV.Report("S00001", "EA-test-model")
        check_blocks(rec("S00001", "EA-test-model", blocks=("L", "K")), ["L", "K"], rq)
        check("content outside the dispatched blocks and missing L content are failures",
              [x["status"] for x in rp.items if x["severity"] == "fail"] == ["content_outside_blocks"]
              and [x["status"] for x in rq.items if x["severity"] == "fail"] == ["block_content_missing"])
    n_fail = results.count(False)
    if verbose:
        print(f"self-tests passed {len(results) - n_fail}/{len(results)}")
    return n_fail


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate every record of extractor sessions (ex_validate batch driver).")
    ap.add_argument("--session", action="append", default=[], help="dispatch folder of an EA or EB session (repeatable)")
    ap.add_argument("--lookups", help="folder with metric-ids-v1.csv (the same folder agreement.py reads)")
    ap.add_argument("--out", help="concatenated report (agreement.py --validator)")
    ap.add_argument("--pass", dest="pass_", type=int, default=1, help="1 first pass (default), 2 after the one return")
    ap.add_argument("--append", action="store_true", help="append to an existing --out")
    ap.add_argument("--first-pass", help="first-pass report checked by --pass 2 (default: --out with --append)")
    ap.add_argument("--output-file", help="extractor output to read instead of dispatch.json's output_file (one session)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return 1 if self_test() else 0
    if not (a.session and a.lookups and a.out):
        ap.error("--session, --lookups and --out are required (or --self-test)")
    return run(a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refused as exc:
        print(exc.msg, file=sys.stderr)
        sys.exit(2)
    except (OSError, ValueError) as exc:
        print(f"ex_validate_batch.py: {type(exc).__name__}: {exc} (input error)", file=sys.stderr)
        sys.exit(2)
