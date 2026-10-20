"""Tests of analysis/extraction/draw_pilot.py on synthetic frames and a synthetic data tree (plan v0.5 s10.2,
s10.7, s11; red-team audit 5 mn1). No real draw is made: every write goes to a pytest tmp folder."""
import json
import random
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
REAL_STRATA_LOG = {"C1": "91615db39bc8c69600064164d9478da544b76c1a13b7e1d09e9cb99ed8f8a80e",
                   "C2": "6766a919f8e11c23805d1849726119686bb3c0a8cd7076d657b9d2ecb09f5383",
                   "NL": "0bc9bf7d746ea841be7ea4319b74213602ebab460e3d57aa7deebfe62766b8e4",
                   "FR": "c7508ab7876e83d40a83f97c0f29b06264102e7914b82e3c4ba8558873798e1a"}


def jw(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def build_tree(root: Path, n_c1=60, n_a=240):
    """Synthetic decisions, screener rows, corpus, texts (sparse files for sizes), config and ledger."""
    rng = random.Random(7)
    dec, fa, fb, corpus = [], [], [], []
    texts = root / "research/sources/md/fulltext-pymupdf"
    texts.mkdir(parents=True)
    ids = []
    for k in range(n_c1):
        i = "M12766" if k == 0 else f"C{k:05d}"
        dec.append({"id": i, "decision": "include", "i1": "ab" if k % 2 == 0 else "b", "nonlang_only": False})
        ids.append(i)
    for k in range(n_a):
        i = "M09530" if k == 0 else f"A{k:05d}"
        mm = "multimodal" if k % 5 == 1 else "text"
        if k == 2:
            fa.append({"id": i, "mm": "multimodal"}), fb.append({"id": i, "mm": "text"})   # split, KW decides
        else:
            fa.append({"id": i, "mm": mm}), fb.append({"id": i, "mm": mm})
        dec.append({"id": i, "decision": "include", "i1": "a", "nonlang_only": k % 40 == 39})
        ids.append(i)
    dec.append({"id": "X00001", "decision": "exclude", "i1": None, "nonlang_only": False})
    for n, i in enumerate(ids):
        title = ("A benchmark of synthetic decoding" if n % 9 == 0 else "Synthetic diffusion model " + i)
        if i == "A00002":
            title = "Image captioning with a synthetic model"            # KW hit for the split record
        corpus.append({"nid": i, "title": title, "abstract": "synthetic"})
        with open(texts / f"{i}.txt", "wb") as f:
            f.truncate(140000 if n % 13 == 0 else 20000 + rng.randrange(100000))
    ft1 = root / "analysis/screening/ft-t1"
    jw(ft1 / "t1-decisions-all.jsonl", dec)
    jw(ft1 / "t1b001" / "FA-t1b001.jsonl", fa)
    jw(ft1 / "t1b001" / "FB-t1b001.jsonl", fb)
    jw(ft1 / "c-superseded.jsonl", [])
    jw(ft1 / "c" / "c-t1-01" / "FC-c-t1-01.jsonl", [{"id": "A00003", "mm": "multimodal"}])
    jw(root / "research/review/corpus/new-records-2026-10-15-v2.jsonl", corpus)
    (root / "analysis/extraction").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "analysis/extraction/gate-config-v05.json", root / "analysis/extraction/gate-config-v05.json")
    jw(root / "research/ledgers/decisions.jsonl", [{"id": "D0099", "decision": "synthetic test row"}])
    return root


@pytest.fixture()
def tree(tmp_path):
    return build_tree(tmp_path / "data")


def run(dp, tree, *args):
    base = ["--data-root", str(tree), "--ledger", str(tree / "research/ledgers/decisions.jsonl")]
    return dp.main(list(args) + base)


def files(p):
    return sorted(str(q.relative_to(p)) for q in p.rglob("*") if q.is_file())


# ---- pure functions --------------------------------------------------------------------------------------------
def test_stage_a_draw_rule(draw_pilot):
    pools = {"C1-ab": [f"a{i}" for i in range(10)] + ["M12766"], "C1-b": [f"b{i}" for i in range(10)],
             "C2": [f"c{i}" for i in range(20)], "FR-bench-title": [f"f{i}" for i in range(5)] + ["M09530"],
             "FRC2-large": [f"c{i}" for i in range(3)] + [f"f{i}" for i in range(4)], "FR": [f"f{i}" for i in range(30)]}
    out = draw_pilot.draw_stage_a(pools)
    assert [p for _, p in out] == ["C1-ab", "C1-b", "C2", "C2", "FR-bench-title", "FRC2-large", "FR"]
    ids = [i for i, _ in out]
    assert len(set(ids)) == 7 and not set(ids) & set(draw_pilot.WORKED_EXAMPLES)
    rng, taken, exp = random.Random(20261100), set(draw_pilot.WORKED_EXAMPLES), []
    for name, k in draw_pilot.STAGE_A_POOLS:
        pick = rng.sample(sorted(set(pools[name]) - taken), k)
        exp += pick
        taken |= set(pick)
    assert ids == exp and draw_pilot.draw_stage_a(pools) == out


def test_gate_lists_spares_and_prefix(draw_pilot):
    strata = {"G-short": [f"s{i:03d}" for i in range(272)], "G-long": [f"l{i:03d}" for i in range(271)],
              "G-mm": [f"m{i:03d}" for i in range(53)]}
    excl = ["s001", "m000", "m001"]
    lists, sp, seeds = draw_pilot.draw_gate(strata, excl, 40, 5, 20261200)
    assert seeds == {"G-short": 20261200, "G-long": 20261201, "G-mm": 20261202}
    for h, s in enumerate(draw_pilot.GATE_STRATA):
        assert len(lists[s]) == 40 and len(sp[s]) == 5 and not set(lists[s] + sp[s]) & set(excl)
        avail = sorted(set(strata[s]) - set(excl))
        assert lists[s] == random.Random(20261200 + h).sample(avail, 40)        # spares leave the list unchanged
    lists0, sp0, _ = draw_pilot.draw_gate(strata, excl, 40, 0, 20261200)
    assert lists0 == lists and sp0 == {s: [] for s in lists}
    with pytest.raises(SystemExit):
        draw_pilot.draw_gate(strata, excl, 40, 46, 20261200)
    with pytest.raises(SystemExit):
        draw_pilot.draw_gate(strata, excl, 40, 12, 20261200)                    # G-mm: 51 available < 52


def test_mi4_excludes(draw_pilot):
    fr = [f"f{i:03d}" for i in range(20)]
    excl = fr[:14]
    ids = draw_pilot.draw_mi4(fr, excl)
    assert len(ids) == 5 and not set(ids) & set(excl) and ids == random.Random(20266200).sample(fr[14:], 5)
    with pytest.raises(SystemExit):
        draw_pilot.draw_mi4(fr, fr[:16])


def test_option_frames(draw_pilot):
    base = {"C1": ["c1"], "NL": ["n1"], "C2": ["m1", "m2", "s1"], "FR": ["r1", "r2", "j1"]}
    construct = {"s1": "side-experiment", "j1": "joint", "m1": "joint"}
    a = draw_pilot.option_frames(base, "a", construct)
    b = draw_pilot.option_frames(base, "b", construct)
    c = draw_pilot.option_frames(base, "c", construct)
    d = draw_pilot.option_frames(base, "d", construct)
    assert a["C2"] == [] and a["FR"] == sorted(base["FR"] + base["C2"])
    assert b["C2"] == base["C2"] and b["FR"] == base["FR"]
    assert c["C2"] == ["j1", "m1", "m2"] and c["FR"] == ["r1", "r2", "s1"] and c["C2b"] == []
    assert d["C2"] == ["j1", "m1", "m2"] and d["C2b"] == ["s1"] and d["FR"] == ["r1", "r2"]
    for f in (a, b, c, d):
        assert f["RC2"] == sorted(base["C2"] + base["FR"])


# ---- CLI on a synthetic data tree -------------------------------------------------------------------------------
def test_dry_run_counts_only_writes_nothing(draw_pilot, tree, capsys):
    before = files(tree)
    for st in ("stage-a", "gate", "mi4", "regate"):
        assert run(draw_pilot, tree, "--stage", st, "--option", "b", "--dry-run") == 0
    out = capsys.readouterr().out
    assert files(tree) == before
    assert "DRY RUN" in out and "C1 60" in out
    assert not any(t in out for t in ("C00001", "A00005", "M12766", "M09530"))       # counts only, no ids


def test_real_draw_needs_decision_row(draw_pilot, tree, tmp_path):
    out = tmp_path / "sa.json"
    for extra in ([], ["--i-have-the-decision-row", "D0100"], ["--i-have-the-decision-row", "yes"]):
        with pytest.raises(SystemExit):
            run(draw_pilot, tree, "--stage", "stage-a", "--option", "b", "--out", str(out), *extra)
    assert not out.exists()


def test_full_sequence(draw_pilot, tree, tmp_path):
    row = ["--i-have-the-decision-row", "D0099"]
    sa, gt, mi, rg = (tmp_path / f"{n}.json" for n in ("sa", "gate", "mi4", "regate"))
    run(draw_pilot, tree, "--stage", "stage-a", "--option", "b", "--out", str(sa), *row)
    m = json.loads(sa.read_text(encoding="utf-8"))
    assert m["ids"][:5] == draw_pilot.WORKED_EXAMPLES and len(m["drawn"]) == 7 and m["decision_row"] == "D0099"
    assert not set(m["drawn"]) & set(draw_pilot.WORKED_EXAMPLES) and m["stratum"]["M12766"] == "WE"
    with pytest.raises(SystemExit):                                                       # no overwrite
        run(draw_pilot, tree, "--stage", "stage-a", "--option", "b", "--out", str(sa), *row)
    with pytest.raises(SystemExit):                                                       # gate needs spares
        run(draw_pilot, tree, "--stage", "gate", "--option", "b", "--stage-a-manifest", str(sa), "--out", str(gt), *row)
    with pytest.raises(SystemExit):                                                       # option mismatch
        run(draw_pilot, tree, "--stage", "gate", "--option", "a", "--stage-a-manifest", str(sa), "--spares", "4",
            "--out", str(gt), *row)
    with pytest.raises(SystemExit):                                                       # mi4 before the gate lists
        run(draw_pilot, tree, "--stage", "mi4", "--option", "b", "--stage-a-manifest", str(sa), "--out", str(mi), *row)
    run(draw_pilot, tree, "--stage", "gate", "--option", "b", "--stage-a-manifest", str(sa), "--spares", "4",
        "--out", str(gt), *row)
    g = json.loads(gt.read_text(encoding="utf-8"))
    assert g["strata_order"] == ["G-short", "G-long", "G-mm"] and g["per_stratum_list"] == 40
    assert g["per_stratum_phase1"] == 20 and all(len(g["lists"][s]) == 40 and len(g["spares"][s]) == 4 for s in g["lists"])
    gids = [i for s in g["lists"] for i in g["lists"][s] + g["spares"][s]]
    assert len(set(gids)) == 132 and not set(gids) & set(m["ids"])
    assert set(g["lists"]["G-mm"]) <= {r for r in g["stratum"] if g["stratum"][r] == "G-mm"}
    run(draw_pilot, tree, "--stage", "mi4", "--option", "b", "--stage-a-manifest", str(sa), "--gate-manifest", str(gt),
        "--out", str(mi), *row)
    q = json.loads(mi.read_text(encoding="utf-8"))
    assert len(q["ids"]) == 5 and not set(q["ids"]) & (set(gids) | set(m["ids"]))
    # 60 C1 records minus Stage A and the first gate's 44 G-mm ids leave too few for a fresh G-mm list of 40: refused
    with pytest.raises(SystemExit, match="G-mm"):
        run(draw_pilot, tree, "--stage", "regate", "--option", "b", "--stage-a-manifest", str(sa), "--gate-manifest",
            str(gt), "--mi4-manifest", str(mi), "--spares", "2", "--out", str(rg), *row)
    assert not rg.exists()


def test_regate_excludes_everything_earlier(draw_pilot, tmp_path):
    tree = build_tree(tmp_path / "big", n_c1=130, n_a=300)
    row = ["--i-have-the-decision-row", "D0099"]
    sa, gt, mi, rg = (tmp_path / f"{n}.json" for n in ("sa", "gate", "mi4", "regate"))
    run(draw_pilot, tree, "--stage", "stage-a", "--option", "b", "--out", str(sa), *row)
    run(draw_pilot, tree, "--stage", "gate", "--option", "b", "--stage-a-manifest", str(sa), "--spares", "4",
        "--out", str(gt), *row)
    run(draw_pilot, tree, "--stage", "mi4", "--option", "b", "--stage-a-manifest", str(sa), "--gate-manifest", str(gt),
        "--out", str(mi), *row)
    run(draw_pilot, tree, "--stage", "regate", "--option", "b", "--stage-a-manifest", str(sa), "--gate-manifest", str(gt),
        "--mi4-manifest", str(mi), "--spares", "2", "--out", str(rg), *row)
    m, g, q, r = (json.loads(p.read_text(encoding="utf-8")) for p in (sa, gt, mi, rg))
    gids = [i for s in g["lists"] for i in g["lists"][s] + g["spares"][s]]
    rids = [i for s in r["lists"] for i in r["lists"][s] + r["spares"][s]]
    assert r["regate"] and r["stage"] == "gate" and r["seeds"]["G-short"] == 20261300
    assert not set(rids) & (set(gids) | set(q["ids"]) | set(m["ids"]))


def test_manifests_feed_agreement(draw_pilot, agreement, tree, tmp_path):
    """The manifests draw_pilot writes are the ones agreement.py reads (ids, strata, phase-1 positions)."""
    row = ["--i-have-the-decision-row", "D0099"]
    sa, gt = tmp_path / "sa.json", tmp_path / "gate.json"
    run(draw_pilot, tree, "--stage", "stage-a", "--option", "b", "--out", str(sa), *row)
    run(draw_pilot, tree, "--stage", "gate", "--option", "b", "--stage-a-manifest", str(sa), "--spares", "4",
        "--out", str(gt), *row)
    m, g = json.loads(sa.read_text(encoding="utf-8")), json.loads(gt.read_text(encoding="utf-8"))
    recs = {i: {"id": i} for i in m["ids"]}
    ids, stratum, order = agreement.analysis_ids("stage-a", m, recs, recs, [])
    assert ids == m["ids"] and order[0] == "WE" and stratum[m["drawn"][0]] == "C1-ab"
    recs = {i: {"id": i} for s in g["strata_order"] for i in g["lists"][s][:25]}
    ids, stratum, order = agreement.analysis_ids("gate-phase1", g, recs, recs, [])
    assert len(ids) == 60 and all(ids[20 * h:20 * h + 20] == g["lists"][s][:20] for h, s in enumerate(order))


def test_draw_is_deterministic(draw_pilot, tree, tmp_path):
    row = ["--i-have-the-decision-row", "D0099"]
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    run(draw_pilot, tree, "--stage", "stage-a", "--option", "b", "--out", str(a), *row)
    run(draw_pilot, tree, "--stage", "stage-a", "--option", "b", "--out", str(b), *row)
    assert json.loads(a.read_text())["ids"] == json.loads(b.read_text())["ids"]


def test_options_c_d_need_construct(draw_pilot, tree, tmp_path):
    row = ["--i-have-the-decision-row", "D0099"]
    with pytest.raises(SystemExit):
        run(draw_pilot, tree, "--stage", "stage-a", "--option", "c", "--out", str(tmp_path / "c.json"), *row)
    assert run(draw_pilot, tree, "--stage", "stage-a", "--option", "d", "--dry-run") == 0
    jw(tree / "analysis/extraction/mm-construct.jsonl", [{"id": "A00006", "class": "side-experiment", "by": "t", "date": "x"}])
    run(draw_pilot, tree, "--stage", "stage-a", "--option", "d", "--out", str(tmp_path / "d.json"), *row)
    m = json.loads((tmp_path / "d.json").read_text())
    assert m["frame_sizes"]["C2b"] == 1 and m["option"] == "d"


def test_option_a_stage_a_uses_mm_rule_c2(draw_pilot, tree, tmp_path):
    row = ["--i-have-the-decision-row", "D0099"]
    run(draw_pilot, tree, "--stage", "stage-a", "--option", "a", "--out", str(tmp_path / "a.json"), *row)
    m = json.loads((tmp_path / "a.json").read_text())
    assert m["frame_sizes"]["C2"] == 0 and m["pools"]["C2"]["size"] > 0
    assert sum(1 for i in m["drawn"] if m["stratum"][i] == "C2") == 2


def test_classification_rules(draw_pilot, tree):
    recs, _ = draw_pilot.load_records(tree)
    base = draw_pilot.base_frames(recs, {}, set())
    assert "A00002" in base["C2"]          # split text/multimodal with a KW hit in the title
    assert "A00003" in base["C2"]          # adjudicator C row wins
    assert "A00039" in base["NL"] and "X00001" not in recs
    over = draw_pilot.base_frames(recs, {"A00002": "text"}, {"A00006"})
    assert "A00002" in over["FR"] and "A00006" not in over["C2"] + over["FR"]


@pytest.mark.skipif(not (ROOT / "analysis/screening/ft-t1/t1-decisions-all.jsonl").exists(), reason="real frames absent")
def test_real_frames_equal_strata_log(draw_pilot):
    """Reads the real screening files (no draw): the frames equal strata-log.txt's list hashes."""
    recs, _ = draw_pilot.load_records(ROOT)
    base = draw_pilot.base_frames(recs, {}, set())
    assert {k: draw_pilot.sha_ids(base[k]) for k in REAL_STRATA_LOG} == REAL_STRATA_LOG
    fr = draw_pilot.option_frames(base, "b", None)
    strata, med = draw_pilot.gate_strata(fr, recs)
    pools = draw_pilot.stage_a_pools(fr, recs, "b")
    assert (len(strata["G-short"]), len(strata["G-long"]), len(strata["G-mm"]), med) == (272, 271, 53, 72648)
    assert [len(pools[p]) for p, _ in draw_pilot.STAGE_A_POOLS] == [15, 38, 108, 24, 52, 435]
