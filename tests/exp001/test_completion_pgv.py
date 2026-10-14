"""Completion nouns, POS labels of tail tokens, PG-V statistic and gate arithmetic (4.4)."""
import numpy as np
import pytest

import caption_end as ce
import completion as cp
from test_caption_prefix import FakeTagger


class FakeTok:
    """Piece-based tokenizer: id -> piece with '▁' marking a leading space, as SentencePiece decode does."""

    def __init__(self, table):
        self.table = table

    def decode(self, ids, skip_special_tokens=False):
        s = "".join(self.table.get(int(i), "") for i in ids).replace("▁", " ")
        return s[1:] if s.startswith(" ") else s


TABLE = {10: "▁surf", 11: "board", 12: "▁on", 13: "▁a", 14: "▁wave", 15: ".", 16: "▁photo", 17: "▁dog"}
TAGS = {"surfboard": "NOUN", "on": "ADP", "a": "DET", "wave": "NOUN", "photo": "NOUN", "dog": "NOUN", "man": "NOUN", "riding": "VERB",
        "the": "DET", "wave.": "NOUN"}


def tail(ids):
    return list(ids) + [0] * (32 - len(ids))


def test_completion_text_and_nouns():
    tok = FakeTok(TABLE)
    t = tail([10, 11, 12, 13, 14, 15])
    pcs = [TABLE.get(i, "").replace("▁", "") for i in t]
    cend = ce.caption_end(t, pcs)
    comp = cp.completion_text(tok, t, cend)
    assert comp == "surfboard on a wave"
    cap = cp.full_caption("A man riding a", comp)
    assert cap == "A man riding a surfboard on a wave"
    nouns = cp.completion_nouns("A man riding a", comp, FakeTagger(TAGS), set(cp.load_list("analysis/EXP-001/nonvisual_nouns.txt")))
    assert nouns == ["surfboard", "wave"]
    # stoplist and prefix words are excluded
    t2 = tail([16, 17])
    comp2 = tok.decode(t2[:2])
    assert cp.completion_nouns("A man riding a", comp2, FakeTagger(TAGS), {"photo"}) == ["dog"]
    assert cp.completion_nouns("A dog on a", "dog wave", FakeTagger(TAGS), set()) == ["wave"]


def test_label_tail_tokens():
    tok = FakeTok(TABLE)
    t = tail([10, 11, 12, 13, 14, 15])
    pcs = [TABLE.get(i, "").replace("▁", "") for i in t]
    cend = ce.caption_end(t, pcs)
    lab = cp.label_tail_tokens(tok, "A man riding a", t, cend, FakeTagger(TAGS))
    assert lab[:5] == ["NOUN", "SUB", "ADP", "DET", "NOUN"] and lab[5] == "POST" and set(lab[6:]) == {"POST"}
    assert [cp.stratum_of(x) for x in lab[:6]] == ["noun", None, "function", "function", "noun", None]
    assert cp.stratum_of("VERB") == "other" and cp.stratum_of("ADJ") == "other"


def test_pgv_derangements_and_partner():
    der = cp.pgv_derangements()
    assert der.shape == (4, 48)
    for d in der:
        assert sorted(d) == list(range(48)) and np.all(d // 2 != np.arange(48) // 2)       # different prefix, never the same
    sp = cp.same_prefix_partner()
    assert np.all(sp // 2 == np.arange(48) // 2) and np.all(sp != np.arange(48))


def test_pgv_statistic_and_gate_arithmetic():
    n = 48
    nouns = [["dog"] if i % 4 else [] for i in range(n)]                      # 75 percent non-empty
    img_has_dog = np.array([i % 2 == 0 for i in range(n)])                     # presence depends on the image only
    stat = cp.pgv_statistic(nouns, lambda nn, j: bool(img_has_dog[j]))
    assert stat["nonempty_share"] == pytest.approx(0.75)
    # matched presence: samples with nouns whose own image has a dog
    exp_m = np.mean([float(bool(nouns[i]) and img_has_dog[i]) for i in range(n)])
    assert stat["m"] == pytest.approx(exp_m)
    gate = cp.pgv_gate(stat, np.zeros(n))
    assert gate["a_nonempty_share_ge_0.60"] and gate["pass"] is False             # m - s near 0: criterion (c) fails
    # a perfectly depictive model: presence only for the own image
    own = lambda nn, j: True
    perfect = cp.pgv_statistic([["dog"]] * n, lambda nn, j, _c=[0]: False)
    assert perfect["m"] == 0.0


def test_pgv_gate_passes_with_matched_signal():
    n = 48
    nouns = [[f"n{i}"] for i in range(n)]
    stat = cp.pgv_statistic(nouns, lambda nn, j: nn == f"n{j}" or (j % 5 == 0 and nn.endswith("1")))
    g = cp.pgv_gate(stat, np.full(n, 0.3))
    assert stat["m"] >= 0.5 and g["pass"]
    g2 = cp.pgv_gate(stat, np.full(n, 0.6))
    assert not g2["d_median_debris_lt_0.5"] and not g2["pass"]
    mean, ci = cp.cluster_bootstrap_diff(stat["matched_i"], stat["same_i"], B=300)
    assert ci[0] <= mean <= ci[1]


def test_pcf_gate():
    assert cp.pcf_gate(0.8, 0.3)["pass"] and not cp.pcf_gate(0.8, 0.45)["pass"] and not cp.pcf_gate(0.6, 0.1)["pass"]
