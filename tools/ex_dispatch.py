"""Build an isolated dispatch folder for one extraction session, form v0.5 (EXTRACTION-PLAN-v0.2 s8.1, s9 as amended
by v0.3 s9 and v0.5 s10.2, s10.8; modelled on tools/ft_dispatch.py).

    python -I tools/ex_dispatch.py --role E1|E2|EC --batch <name> --ids <file with one id per line> --root <scratch dir>
        [--blocks LQHK | --blocks-json <{id: "LQHK"}>] [--manifest <draw manifest .json>]
        [--records-x <EA.jsonl> --records-y <EB.jsonl> --lookups <dir>]          (role EC)
        [--texts <dir>] [--log <path>] [--dry-run]
    python -I tools/ex_dispatch.py --self-test     (built-in synthetic fixtures in a temporary folder; exit 0 if all pass)

Roles and models (plan v0.2 s8.1; brief v0.5 header): E1 = EA, claude-opus-5-5 (ft_model_check alias B); E2 = EB,
claude-sonnet-5-5 (alias A); EC = adjudicator, claude-fable-5-1 (alias C). The schema's extractor pattern takes the
plan's role names, so dispatch.json carries EA, EB or EC.

Creates <root>/<EA|EB|EC>-<batch>-<uuid4>/ (basename never reused) holding only CONTRACT.md, brief.md (the session
text of extractor-brief-v0.5.md: its first ```text block, plus the adjudication block for EC), extraction-schema-v0.5.json,
fulltext/<id>.txt for each listed id (from research/sources/md/fulltext-pymupdf), dispatch.json (role, model, extractor
string, form version, full-text version string, ids in a seeded shuffle, blocks per id, output file name, versions
with sha256 values) and, for EC, records-<id>.jsonl (the two extractor records under neutral labels X and Y,
random per study with one random.Random(20261700) over the sorted ids, extractor field replaced by the label) and
lookups/ (benchmark-ids-v1.csv, metric-ids-v1.csv). Nothing says why a record is in the batch.
Appends a line to research/review/extraction/dispatch-log.jsonl (basename, role, model, model-check alias, batch, n,
ids sha256, files sha256, brief, schema and contract sha256, blocks, and for EC the X/Y key, which never enters
the folder).

Refuses (and writes nothing): an id without a full text; an id not in --manifest (when given); an id or batch name
that is not [A-Za-z0-9_-]; duplicate ids; a brief or schema whose sha256 differs from the pinned v0.5 files (plan
s10.8); a batch larger than the session-size rule of plan v0.2 s9 (an id with block K: one per session when its
text exceeds 133,280 bytes, else two; light-only ids: three per session up to 133,280 bytes, else one); for EC, a
missing record, record pair or lookup file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import shutil
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "research/sources/md/fulltext-pymupdf"
LOG = ROOT / "research/review/extraction/dispatch-log.jsonl"
BRIEF = ROOT / "research/review/extraction/extractor-brief-v0.5.md"
SCHEMA = ROOT / "research/review/extraction/extraction-schema-v0.5.json"
CONTRACT = ROOT / "research/CONTRACT.md"
PINNED = {"brief": "d390f9664ca63d33cba5d939f3bb57c9780839d304c15dd9d06eb453a3c81c9b",
          "schema": "b021c041c26cf5482b22876ba68e8fcec331d0cd9e8e6ba33387bcb0ca0bbc1c"}
ROLES = {"E1": ("EA", "claude-opus-5-5", "B"), "E2": ("EB", "claude-sonnet-5-5", "A"),
         "EC": ("EC", "claude-fable-5-1", "C")}
FT = ("pymupdf-1.27.2.3 text of the PDF, page markers '=== page N ===' (retrieval route per id: "
      "research/review/fulltext/fetch-log.jsonl; analysis/screening/ft-t1/t1-provenance.jsonl)")
FORM = "0.5"
LARGE = 133280
SEED_XY = 20261700
SAFE = re.compile(r"^[A-Za-z0-9_-]+$")
TOOL = "ex_dispatch.py 1.0.1 (extraction form v0.5)"


class Refused(SystemExit):
    pass


def refuse(msg):
    raise Refused(f"ex_dispatch.py: {msg} (nothing written)")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def session_text(role):
    b = BRIEF.read_text(encoding="utf-8")
    blocks = re.findall(r"```text\n(.*?)```", b, re.S)
    if len(blocks) < 2:
        refuse("brief has fewer than two ```text blocks")
    return blocks[0] if role != "EC" else blocks[0].rstrip("\n") + "\n\n" + blocks[1]


def parse_blocks(spec):
    s = spec.upper()
    if not s or any(c not in "LQHK" for c in s) or len(set(s)) != len(s):
        refuse(f"blocks {spec!r} must be distinct letters of LQHK")
    return [c for c in "LQHK" if c in s]


def per_session_limit(ids, blocks, size):
    """Plan v0.2 s9 (M17): K records one per session above 133,280 bytes, else two; light-only three up to 133,280
    bytes, else one. A batch takes the strictest limit of its ids."""
    lim = []
    for i in ids:
        big = size[i] > LARGE
        lim.append(1 if big else (2 if "K" in blocks[i] else 3))
    return min(lim)


def build(a):
    plan_role, model, alias = ROLES[a.role]
    if not SAFE.match(a.batch):
        refuse(f"batch name {a.batch!r} must match [A-Za-z0-9_-]+")
    ids = [l.strip() for l in open(a.ids, encoding="utf-8") if l.strip()]
    if not ids:
        refuse("no ids")
    bad = [i for i in ids if not SAFE.match(i)]
    if bad:
        refuse(f"unsafe ids: {bad[:5]}")
    if len(set(ids)) != len(ids):
        refuse("duplicate ids")
    texts = Path(a.texts)
    missing = [i for i in ids if not (texts / f"{i}.txt").is_file()]
    if missing:
        refuse(f"no full text for {len(missing)} ids: {missing[:10]}")
    man_sha = None
    if a.manifest:
        mb = Path(a.manifest).read_bytes()
        man = json.loads(mb)
        allowed = set(man.get("ids") or []) | set((man.get("stratum") or {}).keys())
        out = [i for i in ids if i not in allowed]
        if out:
            refuse(f"ids not in the draw manifest: {out[:10]}")
        man_sha = sha(mb)
    for name, p in (("brief", BRIEF), ("schema", SCHEMA)):
        if sha(p.read_bytes()) != PINNED[name]:
            refuse(f"{name} {p.name} differs from the pinned v0.5 file (plan s10.8)")
    if a.blocks_json:
        bj = json.loads(Path(a.blocks_json).read_text(encoding="utf-8"))
        if set(bj) != set(ids):
            refuse("--blocks-json must give blocks for exactly the listed ids")
        blocks = {i: parse_blocks(bj[i]) for i in ids}
    else:
        blocks = {i: parse_blocks(a.blocks) for i in ids}
    size = {i: (texts / f"{i}.txt").stat().st_size for i in ids}
    if plan_role in ("EA", "EB"):
        lim = per_session_limit(ids, blocks, size)
        if len(ids) > lim:
            refuse(f"{len(ids)} ids exceed the session-size rule (at most {lim} for these ids and blocks)")
    rec_pairs, xy, lookups = {}, {}, {}
    if plan_role == "EC":
        if not (a.records_x and a.records_y and a.lookups):
            refuse("role EC needs --records-x, --records-y and --lookups")
        RX = {r["id"]: r for r in read_jsonl(a.records_x)}
        RY = {r["id"]: r for r in read_jsonl(a.records_y)}
        for i in ids:
            if i not in RX or i not in RY:
                refuse(f"record pair missing for {i}")
            if not str(RX[i].get("extractor", "")).startswith("EA-") or not str(RY[i].get("extractor", "")).startswith("EB-"):
                refuse(f"--records-x must hold EA records and --records-y EB records ({i})")
        rng = random.Random(SEED_XY)
        for i in sorted(ids):
            swap = rng.random() < 0.5
            first, second = (RY[i], RX[i]) if swap else (RX[i], RY[i])
            xy[i] = {"X": "EB" if swap else "EA", "Y": "EA" if swap else "EB"}
            rx, ry = dict(first), dict(second)
            rx["extractor"], ry["extractor"] = "X", "Y"
            rec_pairs[i] = (rx, ry)
        for f in ("benchmark-ids-v1.csv", "metric-ids-v1.csv"):
            p = Path(a.lookups) / f
            if not p.is_file():
                refuse(f"lookup file missing: {p}")
            lookups[f] = p
    order = list(ids)
    random.Random(f"{a.batch}-{plan_role}").shuffle(order)
    name = f"{plan_role}-{a.batch}-{uuid.uuid4()}"
    d = Path(a.root) / name
    brief_text = session_text(plan_role).encode("utf-8")
    out_file = f"{plan_role}-{a.batch}.jsonl"
    versions = {"form_version": FORM, "brief_source": BRIEF.name, "brief_source_sha256": PINNED["brief"],
                "brief_session_text_sha256": sha(brief_text), "schema": SCHEMA.name, "schema_sha256": PINNED["schema"],
                "contract_sha256": sha(CONTRACT.read_bytes())}
    if lookups:
        versions["lookups_sha256"] = {f: sha(p.read_bytes()) for f, p in lookups.items()}
    disp = {"role": plan_role, "model": model, "extractor": f"{plan_role}-{model}", "batch": a.batch,
            "form_version": FORM, "ft": FT, "ids": order, "blocks": {i: blocks[i] for i in order},
            "output_file": out_file, "versions": versions}
    if rec_pairs:
        disp["records_files"] = {i: f"records-{i}.jsonl" for i in order}
    if a.dry_run:
        print(f"DRY RUN: would create {Path(a.root) / (plan_role + '-' + a.batch + '-<uuid4>')} with {len(ids)} full texts, "
              f"role {plan_role} ({model}), output {out_file}; nothing written")
        return None
    if d.exists():
        refuse(f"{d} exists")
    (d / "fulltext").mkdir(parents=True)
    shutil.copyfile(CONTRACT, d / "CONTRACT.md")
    (d / "brief.md").write_bytes(brief_text)
    shutil.copyfile(SCHEMA, d / SCHEMA.name)
    files = {}
    for i in order:
        b = (texts / f"{i}.txt").read_bytes()
        (d / "fulltext" / f"{i}.txt").write_bytes(b)
        files[i] = sha(b)
    for i, (rx, ry) in rec_pairs.items():
        (d / f"records-{i}.jsonl").write_text(json.dumps(rx, ensure_ascii=False) + "\n" +
                                              json.dumps(ry, ensure_ascii=False) + "\n", encoding="utf-8")
    if lookups:
        (d / "lookups").mkdir()
        for f, p in lookups.items():
            shutil.copyfile(p, d / "lookups" / f)
    (d / "dispatch.json").write_text(json.dumps(disp, indent=1), encoding="utf-8")
    row = {"basename": name, "role": plan_role, "cli_role": a.role, "model": model, "model_check_alias": alias,
           "batch": a.batch, "n": len(ids), "ids_sha256": sha("\n".join(sorted(ids)).encode()),
           "files_sha256": sha(json.dumps(files, sort_keys=True).encode()),
           "blocks_sha256": sha(json.dumps(blocks, sort_keys=True).encode()), "brief_sha256": PINNED["brief"],
           "brief_session_text_sha256": versions["brief_session_text_sha256"], "schema_sha256": PINNED["schema"],
           "contract_sha256": versions["contract_sha256"], "manifest_sha256": man_sha, "tool": TOOL,
           "tool_sha256": sha(Path(__file__).read_bytes())}
    if xy:
        row["xy"] = xy
        row["records_sha256"] = {"x": sha(Path(a.records_x).read_bytes()), "y": sha(Path(a.records_y).read_bytes())}
    log = Path(a.log)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")
    print(d)
    return d


def self_test(verbose=True):
    """Built-in synthetic texts and records in a temporary folder (the real brief, schema and contract are read,
    never written; the real dispatch log is never touched). Returns the number of failed checks."""
    import io  # noqa: PLC0415
    import tempfile  # noqa: PLC0415
    from contextlib import redirect_stdout  # noqa: PLC0415
    results = []

    def check(desc, fn):
        try:
            ok = bool(fn())
        except Exception as exc:  # noqa: BLE001 -- a crashing check is a failed check
            ok, desc = False, f"{desc} [{type(exc).__name__}: {exc}]"
        results.append(ok)
        if verbose:
            print(f"self-test {len(results):2d} {'ok  ' if ok else 'FAIL'} {desc}")

    log_before = LOG.read_bytes() if LOG.exists() else None
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        texts, root, log = tmp / "texts", tmp / "root", tmp / "log.jsonl"
        texts.mkdir()
        small = {"S00001": "=== page 1 ===\nA synthetic text.\n", "S00002": "=== page 1 ===\nAnother synthetic text.\n",
                 "S00003": "=== page 1 ===\nA third synthetic text.\n"}
        for i, t in small.items():
            (texts / f"{i}.txt").write_text(t, encoding="utf-8")
        (texts / "L00001.txt").write_bytes(b"=== page 1 ===\n" + b"x" * (LARGE + 10))

        counter = iter(range(10 ** 6))

        def ids_file(name, ids):
            p = tmp / f"{name}.txt"
            p.write_text("\n".join(ids) + "\n", encoding="utf-8")
            return str(p)

        def run(*args, ids=("S00001", "S00002"), role="E1", batch="st1"):
            argv = ["--role", role, "--batch", batch, "--ids", ids_file(f"ids-{len(results)}-{next(counter)}", ids), "--root", str(root),
                    "--texts", str(texts), "--log", str(log)] + list(args)
            buf = io.StringIO()
            try:
                with redirect_stdout(buf):
                    main(argv)
            except Refused:
                return "refused"
            return buf.getvalue().strip()

        def folder_ok():
            d = Path(run())
            disp = json.loads((d / "dispatch.json").read_text(encoding="utf-8"))
            files = sorted(str(q.relative_to(d)).replace("\\", "/") for q in d.rglob("*") if q.is_file())
            want = sorted(["CONTRACT.md", "brief.md", SCHEMA.name, "dispatch.json", "fulltext/S00001.txt", "fulltext/S00002.txt"])
            return (re.fullmatch(r"EA-st1-[0-9a-f-]{36}", d.name) and files == want
                    and disp["role"] == "EA" and disp["model"] == "claude-opus-5-5" and disp["extractor"] == "EA-claude-opus-5-5"
                    and disp["output_file"] == "EA-st1.jsonl" and disp["blocks"] == {i: list("LQHK") for i in disp["ids"]}
                    and (d / "brief.md").read_text(encoding="utf-8") == session_text("EA")
                    and (d / "fulltext/S00001.txt").read_bytes() == (texts / "S00001.txt").read_bytes()
                    and sorted(disp["ids"]) == ["S00001", "S00002"])
        check("E1 folder: only contract, session brief, schema, texts and dispatch.json; EA claude-opus-5-5", folder_ok)

        def log_ok():
            rows = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines() if x.strip()]
            r = rows[-1]
            return (r["role"] == "EA" and r["model_check_alias"] == "B" and r["n"] == 2
                    and r["ids_sha256"] == sha("\n".join(sorted(["S00001", "S00002"])).encode()) and "xy" not in r)
        check("dispatch log row goes to --log (alias B, ids sha256)", log_ok)

        def shuffle_ok():
            o1 = json.loads((Path(run(batch="sh")) / "dispatch.json").read_text(encoding="utf-8"))["ids"]
            o2 = json.loads((Path(run(batch="sh")) / "dispatch.json").read_text(encoding="utf-8"))["ids"]
            exp = ["S00001", "S00002"]
            random.Random("sh-EA").shuffle(exp)
            return o1 == o2 == exp
        check("ids order is the seeded shuffle random.Random('<batch>-<role>')", shuffle_ok)
        check("E2 maps to EB claude-sonnet-5-5",
              lambda: json.loads((Path(run(role="E2")) / "dispatch.json").read_text(encoding="utf-8"))["extractor"] == "EB-claude-sonnet-5-5")
        man = tmp / "manifest.json"
        man.write_text(json.dumps({"stage": "stage-a", "ids": ["S00001", "S00002"]}), encoding="utf-8")
        n_before = len(list(root.iterdir()))
        refusals = {"no full text": dict(ids=("S00001", "S09999")), "unsafe id": dict(ids=("S00001", "../x")),
                    "duplicate id": dict(ids=("S00001", "S00001")), "unsafe batch": dict(batch="b/1"),
                    "three K records": dict(ids=("S00001", "S00002", "S00003")),
                    "large text with another": dict(ids=("L00001", "S00001"))}
        check("refusals write nothing: " + ", ".join(refusals) + ", bad blocks, id not in the manifest",
              lambda: all(run(**kw) == "refused" for kw in refusals.values())
              and run("--blocks", "LQX") == "refused" and run("--manifest", str(man), ids=("S00001", "S00003")) == "refused"
              and len(list(root.iterdir())) == n_before)
        check("session-size rule: one large K record alone, three light records under the limit",
              lambda: run(ids=("L00001",), batch="big") != "refused"
              and run("--blocks", "LQH", ids=("S00001", "S00002", "S00003"), batch="light") != "refused")
        check("dry run writes nothing",
              lambda: "DRY RUN" in run("--dry-run", batch="dry") and not any(p.name.startswith("EA-dry-") for p in root.iterdir()))
        ex, ey, lk = tmp / "ex.jsonl", tmp / "ey.jsonl", tmp / "lookups"
        lk.mkdir()
        for f in ("benchmark-ids-v1.csv", "metric-ids-v1.csv"):
            (lk / f).write_text("printed,id\n" if f.startswith("bench") else "printed,id,higher_is_better\n", encoding="utf-8")
        ex.write_text("".join(json.dumps({"id": i, "extractor": "EA-claude-opus-5-5", "k": "x"}) + "\n" for i in small), encoding="utf-8")
        ey.write_text("".join(json.dumps({"id": i, "extractor": "EB-claude-sonnet-5-5", "k": "y"}) + "\n" for i in small), encoding="utf-8")

        def ec_ok():
            d = Path(run("--records-x", str(ex), "--records-y", str(ey), "--lookups", str(lk), role="EC", batch="ec"))
            rng, key = random.Random(SEED_XY), {}
            for i in sorted(["S00001", "S00002"]):
                key[i] = rng.random() < 0.5
            ok = sorted(p.name for p in (d / "lookups").iterdir()) == ["benchmark-ids-v1.csv", "metric-ids-v1.csv"]
            for i, swap in key.items():
                rx, ry = [json.loads(x) for x in (d / f"records-{i}.jsonl").read_text(encoding="utf-8").splitlines()]
                ok = ok and rx["extractor"] == "X" and ry["extractor"] == "Y" and (rx["k"], ry["k"]) == (("y", "x") if swap else ("x", "y"))
            row = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines() if x.strip()][-1]
            folder_text = " ".join(p.read_text(encoding="utf-8") for p in [d / "dispatch.json", *d.glob("records-*.jsonl")])
            return ok and row["xy"] == {i: ({"X": "EB", "Y": "EA"} if s else {"X": "EA", "Y": "EB"}) for i, s in key.items()} \
                and "EA-claude-opus-5-5" not in folder_text
        check("EC folder: neutral X/Y labels from random.Random(20261700), key only in the log", ec_ok)
        check("EC without records or lookups is refused", lambda: run(role="EC", batch="ec2") == "refused")
    check("the real dispatch log was not touched", lambda: (LOG.read_bytes() if LOG.exists() else None) == log_before)
    n_fail = results.count(False)
    if verbose:
        print(f"self-tests passed {len(results) - n_fail}/{len(results)}")
    return n_fail


def main(argv=None):
    ap = argparse.ArgumentParser(description="Isolated dispatch folder for one extraction session (form v0.5).")
    ap.add_argument("--role", choices=sorted(ROLES))
    ap.add_argument("--batch")
    ap.add_argument("--ids")
    ap.add_argument("--root")
    ap.add_argument("--blocks", default="LQHK")
    ap.add_argument("--blocks-json")
    ap.add_argument("--manifest")
    ap.add_argument("--records-x")
    ap.add_argument("--records-y")
    ap.add_argument("--lookups")
    ap.add_argument("--texts", default=str(MD))
    ap.add_argument("--log", default=str(LOG))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true",
                    help="built-in synthetic fixtures in a temporary folder; exit 0 if all pass, else 1")
    a = ap.parse_args(argv)
    if a.self_test:
        return 1 if self_test() else 0
    if not (a.role and a.batch and a.ids and a.root):
        ap.error("--role, --batch, --ids and --root are required (or --self-test)")
    build(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
