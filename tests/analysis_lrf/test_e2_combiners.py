"""E2 combiners (analysis/paper2/lrf/e2_combiners.py) on SYNTHETIC arrays only: no real array is read. CPU only."""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.paper2.lrf import e2_combiners as E2                                    # noqa: E402
from exp_p2.gate import tier3_fusion as T3                                            # noqa: E402

M = T3.M_TOKENS


def make_run(tmp: Path, n=12, seed=0, corrupt_y=False):
    rng = np.random.default_rng(seed)
    (tmp / "arrays").mkdir(parents=True)
    preds = []
    for i in range(n):
        d = {}
        for c in E2.CONDS:
            delta = rng.normal(0.02 * (1 + (i % 3)), 1.0, M).astype(np.float32)
            flag = rng.uniform(size=M) < (0.0 if i == 0 else 0.03)
            d[f"{c}_delta"], d[f"{c}_{E2.FLAG_KEY}"] = delta, flag
            dd = delta.astype(np.float64)
            y_none = int(dd.mean() > 0)
            y_gm = int(dd[~flag].mean() > 0)
            preds.append(dict(condition=c, idx=i, y_none=(1 - y_none) if (corrupt_y and i == 3 and c == "clean") else y_none, y_gatem=y_gm))
        np.savez(tmp / "arrays" / f"item{i:04d}.npz", **d)
    (tmp / "predictions.jsonl").write_text("\n".join(json.dumps(p) for p in preds) + "\n", encoding="utf-8")
    return tmp


def test_decisions_match_tier3_and_reference_definitions():
    rng = np.random.default_rng(1)
    for _ in range(20):
        delta = rng.normal(0.05, 1.0, M).astype(np.float32)
        flag = rng.uniform(size=M) < 0.04
        y = E2.decisions(delta, flag)
        d = delta.astype(np.float64)
        s = np.sort(d)
        g = int(flag.sum())
        k20 = math.floor(0.2 * M)
        assert y["NONE"] == int(d.mean() > 0)
        assert y["MED"] == int(np.median(d) > 0)
        assert y["TM20"] == int(s[k20:M - k20].mean() > 0)
        kg = g // 2
        assert y["TM-G"] == int((d.mean() if kg <= 0 else s[kg:M - kg].mean()) > 0)
        assert y["GM"] == int(d[~flag].mean() > 0)


def test_tmg_with_at_most_one_flag_equals_none_bit_for_bit():
    rng = np.random.default_rng(2)
    for g in (0, 1):
        delta = rng.normal(0.0, 1.0, M).astype(np.float32)
        flag = np.zeros(M, bool)
        flag[:g] = True
        mg = T3.item_margins(delta, flag, np.zeros(M), E2._POOL)
        assert mg["TM-G"][0] == mg["NONE"][0]


def test_ties_and_empty_are_wrong():
    delta = np.zeros(M, np.float32)
    y = E2.decisions(delta, np.zeros(M, bool))
    assert all(v == 0 for v in y.values())


def test_paired_counts_and_interval(tmp_path):
    ya = np.array([1, 1, 0, 0, 1, 0, 1, 1], np.int8)
    yr = np.array([1, 0, 0, 1, 0, 0, 1, 0], np.int8)
    idx = np.random.default_rng(0).integers(0, 8, size=(2000, 8))
    r = E2.paired(ya, yr, idx)
    assert (r["b"], r["c"]) == (3, 1)                                                  # items 1, 4, 7 gained; item 3 lost
    assert r["diff"] == pytest.approx(2 / 8)
    assert r["ci95"][0] <= r["diff"] <= r["ci95"][1]


def test_analyse_end_to_end_deterministic_and_complete(tmp_path):
    run = make_run(tmp_path / "r")
    a = E2.analyse(run)
    b = E2.analyse(run)
    assert a == b                                                                      # seed 0, nothing random beyond it
    assert list(a["cells"]) == list(E2.CONDS) and a["consistency"]["ok"] is True
    for c in E2.CONDS:
        cell = a["cells"][c]
        assert cell["n"] == 12 and set(cell["arms"]) == {"NONE", "MED", "TM20", "TM-G"}
        for arm in E2.ARMS:
            v = cell["arms"][arm]
            assert {"diff", "b", "c", "ci95"} == set(v["vs_NONE"])
            assert 0.0 <= v["acc"] <= 1.0 and "p" not in v["vs_NONE"]
    assert "p_value" not in json.dumps(a)


def test_consistency_gate_refuses_a_wrong_stored_label(tmp_path):
    run = make_run(tmp_path / "r", corrupt_y=True)
    with pytest.raises(RuntimeError, match="consistency gate failed"):
        E2.analyse(run)


def test_missing_array_is_an_error(tmp_path):
    run = make_run(tmp_path / "r")
    (run / "arrays" / "item0005.npz").unlink()
    with pytest.raises(FileNotFoundError):
        E2.analyse(run)
