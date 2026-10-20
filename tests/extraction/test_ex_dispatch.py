"""Tests of tools/ex_dispatch.py with synthetic full texts and records (plan v0.2 s8.1, s9; v0.5 s10.8). Every
folder and log line goes to a pytest tmp folder."""
import json
import random
import re
from pathlib import Path

import pytest

import ex_synth as synth

ROOT = Path(__file__).resolve().parents[2]
BRIEF = ROOT / "research/review/extraction/extractor-brief-v0.5.md"


@pytest.fixture()
def env(tmp_path):
    texts = tmp_path / "texts"
    texts.mkdir()
    for i in ("M00001", "M00002", "M00003", "M00004"):
        (texts / f"{i}.txt").write_text(f"=== page 1 ===\nSynthetic paper {i}.\n", encoding="utf-8")
    with open(texts / "M00009.txt", "wb") as f:              # a long text (> 133,280 bytes)
        f.truncate(140000)
    return {"tmp": tmp_path, "texts": texts, "root": tmp_path / "scratch", "log": tmp_path / "log.jsonl"}


def ids_file(env, ids, name="ids.txt"):
    p = env["tmp"] / name
    p.write_text("\n".join(ids) + "\n", encoding="utf-8")
    return p


def args(env, role, ids, *extra, batch="b01"):
    return ["--role", role, "--batch", batch, "--ids", str(ids_file(env, ids)), "--root", str(env["root"]),
            "--texts", str(env["texts"]), "--log", str(env["log"])] + list(extra)


def only_dir(env):
    ds = list(env["root"].iterdir())
    assert len(ds) == 1
    return ds[0]


def test_extractor_folder(ex_dispatch, env):
    ex_dispatch.main(args(env, "E1", ["M00001", "M00002"]))
    d = only_dir(env)
    assert re.fullmatch(r"EA-b01-[0-9a-f-]{36}", d.name)
    got = sorted(str(p.relative_to(d)).replace("\\", "/") for p in d.rglob("*") if p.is_file())
    assert got == ["CONTRACT.md", "brief.md", "dispatch.json", "extraction-schema-v0.5.json", "fulltext/M00001.txt",
                   "fulltext/M00002.txt"]
    disp = json.loads((d / "dispatch.json").read_text(encoding="utf-8"))
    assert disp["role"] == "EA" and disp["model"] == "claude-opus-5-5" and disp["extractor"] == "EA-claude-opus-5-5"
    assert sorted(disp["ids"]) == ["M00001", "M00002"] and disp["output_file"] == "EA-b01.jsonl"
    assert disp["form_version"] == "0.5" and disp["blocks"]["M00001"] == ["L", "Q", "H", "K"]
    assert disp["versions"]["schema_sha256"] == ex_dispatch.PINNED["schema"]
    block0 = re.findall(r"```text\n(.*?)```", BRIEF.read_text(encoding="utf-8"), re.S)[0]
    assert (d / "brief.md").read_text(encoding="utf-8") == block0
    assert "ADJUDICATION" not in block0
    row = json.loads(env["log"].read_text(encoding="utf-8").splitlines()[-1])
    assert row["basename"] == d.name and row["model_check_alias"] == "B" and row["n"] == 2 and "xy" not in row
    # the schema's extractor pattern accepts the dispatch string
    assert re.fullmatch(r"^(EA|EB|ER|EC|EQ)-[a-z0-9-]+$", disp["extractor"])


def test_second_extractor_role(ex_dispatch, env):
    ex_dispatch.main(args(env, "E2", ["M00003"]))
    disp = json.loads((only_dir(env) / "dispatch.json").read_text(encoding="utf-8"))
    assert disp["role"] == "EB" and disp["model"] == "claude-sonnet-5-5"
    assert json.loads(env["log"].read_text(encoding="utf-8"))["model_check_alias"] == "A"


def test_shuffle_is_seeded(ex_dispatch, env):
    ex_dispatch.main(args(env, "E1", ["M00001", "M00002"], batch="s1"))
    ex_dispatch.main(args(env, "E1", ["M00001", "M00002"], batch="s1"))
    orders = [json.loads((d / "dispatch.json").read_text(encoding="utf-8"))["ids"] for d in env["root"].iterdir()]
    exp = ["M00001", "M00002"]
    random.Random("s1-EA").shuffle(exp)
    assert orders[0] == orders[1] == exp


@pytest.mark.parametrize("case", ["no_full_text", "unsafe_id", "duplicate", "not_in_manifest", "too_many_K",
                                  "long_text_with_another", "bad_blocks", "unsafe_batch"])
def test_refusals_write_nothing(ex_dispatch, env, case):
    ids, extra, batch = ["M00001", "M00002"], [], "b01"
    if case == "no_full_text":
        ids = ["M00001", "M00077"]
    if case == "unsafe_id":
        ids = ["M00001", "../M00002"]
    if case == "duplicate":
        ids = ["M00001", "M00001"]
    if case == "not_in_manifest":
        man = env["tmp"] / "m.json"
        man.write_text(json.dumps({"stage": "stage-a", "ids": ["M00001"], "stratum": {"M00001": "C2"}}), encoding="utf-8")
        extra = ["--manifest", str(man)]
    if case == "too_many_K":
        ids = ["M00001", "M00002", "M00003"]
    if case == "long_text_with_another":
        ids = ["M00001", "M00009"]
        extra = ["--blocks", "LQH"]
    if case == "bad_blocks":
        extra = ["--blocks", "LQX"]
    if case == "unsafe_batch":
        batch = "../b"
    with pytest.raises(SystemExit):
        ex_dispatch.main(args(env, "E1", ids, *extra, batch=batch))
    assert not env["root"].exists() and not env["log"].exists()


def test_session_size_rule(ex_dispatch, env):
    ex_dispatch.main(args(env, "E1", ["M00001", "M00002", "M00003"], "--blocks", "LQH"))     # light-only: three
    ex_dispatch.main(args(env, "E1", ["M00009"], batch="big"))                                 # one long K record
    assert len(list(env["root"].iterdir())) == 2
    bj = env["tmp"] / "bj.json"
    bj.write_text(json.dumps({"M00001": "LQH", "M00002": "LQHK", "M00003": "LQH"}), encoding="utf-8")
    with pytest.raises(SystemExit):                                                           # one K id: two at most
        ex_dispatch.main(args(env, "E1", ["M00001", "M00002", "M00003"], "--blocks-json", str(bj), batch="mix"))


def test_dry_run_writes_nothing(ex_dispatch, env, capsys):
    ex_dispatch.main(args(env, "E1", ["M00001"], "--dry-run"))
    assert "DRY RUN" in capsys.readouterr().out
    assert not env["root"].exists() and not env["log"].exists()


def _ec_inputs(env, ids):
    xs, ys = [], []
    for i in ids:
        x, y = synth.pair(i)
        xs.append(x), ys.append(y)
    rx = synth.write_jsonl(env["tmp"] / "EA.jsonl", xs)
    ry = synth.write_jsonl(env["tmp"] / "EB.jsonl", ys)
    lk = synth.write_lookups(env["tmp"] / "lookups")
    return rx, ry, lk


def test_ec_folder_neutral_labels(ex_dispatch, env):
    ids = ["M00001", "M00002", "M00003", "M00004"]
    rx, ry, lk = _ec_inputs(env, ids)
    ex_dispatch.main(args(env, "EC", ids, "--records-x", str(rx), "--records-y", str(ry), "--lookups", str(lk)))
    d = only_dir(env)
    assert d.name.startswith("EC-b01-")
    disp = json.loads((d / "dispatch.json").read_text(encoding="utf-8"))
    assert disp["model"] == "claude-fable-5-1" and set(disp["records_files"]) == set(ids)
    brief = (d / "brief.md").read_text(encoding="utf-8")
    assert "ADJUDICATION." in brief and "PUBLIC-VERSION QA" not in brief
    assert sorted(p.name for p in (d / "lookups").iterdir()) == ["benchmark-ids-v1.csv", "metric-ids-v1.csv"]
    row = json.loads(env["log"].read_text(encoding="utf-8"))
    rng = random.Random(20261700)
    for i in sorted(ids):
        swap = rng.random() < 0.5
        assert row["xy"][i] == ({"X": "EB", "Y": "EA"} if swap else {"X": "EA", "Y": "EB"})
        lines = [json.loads(l) for l in (d / f"records-{i}.jsonl").read_text(encoding="utf-8").splitlines()]
        assert [r["extractor"] for r in lines] == ["X", "Y"] and all(r["id"] == i for r in lines)
    for p in d.rglob("*"):         # no extractor role or model in the records or dispatch.json (the pinned schema's
        if p.is_file() and (p.name.startswith("records-") or p.name == "dispatch.json"):   # own example is fixed text)
            t = p.read_text(encoding="utf-8")
            assert "opus" not in t and "sonnet" not in t and "EA-" not in t and "EB-" not in t, p.name
    assert "xy" not in json.dumps(disp)


def test_ec_refusals(ex_dispatch, env):
    ids = ["M00001", "M00002"]
    rx, ry, lk = _ec_inputs(env, ids)
    with pytest.raises(SystemExit):                                                   # no lookups
        ex_dispatch.main(args(env, "EC", ids, "--records-x", str(rx), "--records-y", str(ry)))
    with pytest.raises(SystemExit):                                                   # X and Y swapped
        ex_dispatch.main(args(env, "EC", ids, "--records-x", str(ry), "--records-y", str(rx), "--lookups", str(lk)))
    with pytest.raises(SystemExit):                                                   # a record missing
        ex_dispatch.main(args(env, "EC", ids + ["M00003"], "--records-x", str(rx), "--records-y", str(ry),
                              "--lookups", str(lk)))
    assert not env["root"].exists() and not env["log"].exists()
