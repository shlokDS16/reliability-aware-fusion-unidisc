"""Caption-end rule (4.1b) and prefix rule (4.2) tests."""
import pytest

import caption_end as ce
import prefix_rule as pr


def mk(tokens):
    """tokens: list of (id, piece) padded with (0, '') to 32."""
    toks = list(tokens) + [(0, "")] * (32 - len(tokens))
    return [t[0] for t in toks], [t[1] for t in toks]


def test_patterns_load_and_utf8():
    p = ce.load_patterns()
    assert "(" in p["contains"] and ")" in p["contains"] and "©" in p["contains"] and ".com" in p["contains"]
    assert set(p["equals_ci"]) == {"copyright", "stock"} and p["digits_only"] is True


def test_simple_completion_ends_at_terminator():
    ids, pcs = mk([(10, "surf"), (11, "board"), (12, "on"), (13, "a"), (14, "wave"), (15, ".")])
    r = ce.caption_end(ids, pcs)
    assert r.f == 1 and r.e1 == 6 and r.e0 == 7 and r.e == 6 and r.set_by == "e1"
    # literal card rule: the terminator itself is at i = e >= e, not in P, hence counted as debris (1 of 32)
    assert r.completion_len == 5 and r.n_debris == 1 and not r.e2_set


def test_pad_ends_caption_and_debris_share():
    ids, pcs = mk([(10, "dog"), (0, ""), (20, "x"), (21, "y")])
    r = ce.caption_end(ids, pcs)
    assert r.e == 2 and r.set_by == "e0" and r.completion_len == 1
    # post-caption tokens not in P: positions 3,4 are debris, the zero-padded rest is pad
    assert r.n_debris == 2 and r.debris_share == pytest.approx(2 / 32)


def test_e2_debris_pattern_sets_end():
    ids, pcs = mk([(10, "cat"), (11, "sitting"), (12, "(c)"), (13, "shutterstock")])
    r = ce.caption_end(ids, pcs)
    assert r.e2 == 3 and r.e == 3 and r.set_by == "e2" and r.e2_set and r.completion_len == 2
    for piece in ("copyright", "Stock", "123", "http", "www.x", "a/b", "|", "@", "©", ".com", "x)"):
        ids, pcs = mk([(10, "cat"), (11, piece)])
        assert ce.caption_end(ids, pcs).e2 == 2, piece
    for piece in ("stocks", "a1b", "c", "word"):      # not matching: 'stocks' is not 'stock', 'a1b' not digits only
        ids, pcs = mk([(10, "cat"), (11, piece)])
        assert ce.caption_end(ids, pcs).e2 == ce.INF, piece


def test_patterns_apply_only_after_first_alnum():
    # a leading '(' before any alphanumeric token (i < f) does not end the caption; terminator before f neither
    ids, pcs = mk([(5, "("), (6, "."), (10, "cat"), (11, "sat")])
    r = ce.caption_end(ids, pcs)
    assert r.f == 3 and r.e2 == ce.INF and r.e1 == ce.INF and r.e == 5     # ends at the first pad (index 5)
    assert r.completion_len == 4


def test_no_alnum_gives_empty_completion():
    ids, pcs = mk([(5, ","), (6, "."), (7, "-")])
    r = ce.caption_end(ids, pcs)
    assert r.f == ce.INF and r.completion_len == 0


def test_full_tail_no_terminator_caps_at_33():
    ids = list(range(100, 132))
    pcs = ["w"] * 32
    r = ce.caption_end(ids, pcs)
    assert r.e == 33 and r.set_by == "cap" and r.completion_len == 32 and r.n_debris == 0


def test_terminator_variants():
    for piece in ("!", "?", "\n", "end."):
        ids, pcs = mk([(10, "cat"), (11, piece)])
        assert ce.caption_end(ids, pcs).e1 == 2


def test_post_caption_mask():
    ids, pcs = mk([(10, "cat"), (11, ".")])
    r = ce.caption_end(ids, pcs)
    m = ce.post_caption_mask(r)
    assert m[:1] == [False] and all(m[1:])


class FakeTagger:
    def __init__(self, table):
        self.table = table

    def __call__(self, text):
        out, pos = [], 0
        for w in text.split(" "):
            i = text.index(w, pos)
            out.append((w, self.table.get(w, "X"), i))
            pos = i + len(w)
        return out


TAB = {"man": "NOUN", "surfboard": "NOUN", "wave": "NOUN", "a": "DET", "riding": "VERB", "on": "ADP", "the": "DET"}


def test_prefix_rung1_example():
    r = pr.prefix_for("A man riding a surfboard on a wave", FakeTagger(TAB), 1)
    assert r.eligible and r.prefix == "A man riding a" and r.n_words == 4 and r.target_noun == "surfboard"


def test_prefix_rung2_and_ineligible():
    r2 = pr.prefix_for("A man riding a surfboard on a wave", FakeTagger(TAB), 2)
    assert r2.eligible and r2.n_words == 7 and r2.prefix == "A man riding a surfboard on a" and r2.target_noun == "wave"
    r = pr.prefix_for("man surfboard", FakeTagger(TAB), 1)           # prefix has 1 word
    assert not r.eligible and r.n_words == 1
    r = pr.prefix_for("a man", FakeTagger(TAB), 1)                    # only one noun
    assert not r.eligible and "fewer than" in r.reason


def test_prefix_rung2_eligible():
    cap = "The man riding a big old surfboard on a wave"
    tab = dict(TAB, big="ADJ", old="ADJ", The="DET", **{"the": "DET"})
    # lower-cased tagging: 'the', 'man', 'riding', 'a', 'big', 'old', 'surfboard', ...
    r = pr.prefix_for(cap, FakeTagger(tab), 2)
    assert r.eligible and r.prefix == "The man riding a big old surfboard on a" and r.n_words == 9


def test_prompt_text():
    s = pr.prompt_text("A man riding a")
    assert s.startswith("A man riding a<m>") and s.count("<m>") == 32


def test_spacy_tagger_matches_card_example():
    spacy = pytest.importorskip("spacy")
    try:
        tg = pr.SpacyTagger()
    except Exception:
        pytest.skip("en_core_web_sm not installed")
    r = pr.prefix_for("A man riding a surfboard on a wave", tg, 1)
    assert r.eligible and r.prefix == "A man riding a"
