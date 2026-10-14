"""Prefix rule (EXP-001 card v0.5, section 4.2). FROZEN before PG-V; hash recorded in runs/EXP-001/gates/manifest.json.

A pure function of the COCO caption text and the pinned tagger. Tag the lower-cased caption; t1 = first NOUN/PROPN token,
t2 = first NOUN/PROPN token after t1 (rung 1), t3 = first after t2 (rung 2). The prefix is the words before t2 (rung 1) or
before t3 (rung 2), taken from the ORIGINAL (cased) caption text (the card's example: 'A man riding a surfboard on a wave'
gives 'A man riding a'). Eligible iff the rung's prefix has 3-6 words (rung 1) or 5-9 words (rung 2) and the target noun
exists. Items are never selected or dropped by any model output.

Layout convention (fixed here, v2): the prompt slot text is  PREFIX + '<m>' * 32  with NO space between the prefix and the masks.
(v1 used the official demo's  prompt + ' ' + '<m>'*n, which Llama-2 SentencePiece tokenises as [..., 'a', '▁', <m>...]: a lone
'▁' token right before the tail, after which the model almost always continues with a digit. PG-V try 1 and PG-1 condition-P
leg try 1 were run under v1 and are kept on disk; see IMPLEMENTATION.md.)
Tagger pin (recorded in the manifest): spaCy en_core_web_sm 3.8.0 (wheel SHA-256 in the manifest), Universal POS tags (pos_).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

RULE_VERSION = "prefix_rule v2 (EXP-001 v0.5; layout convention without the space before the masks)"
RUNG_WORDS = {1: (3, 6), 2: (5, 9)}
NOUN_TAGS = ("NOUN", "PROPN")


class Tagger(Protocol):
    def __call__(self, text: str) -> Sequence[tuple[str, str, int]]:
        """Return (token_text, UPOS, char_offset) for each token of text."""


class SpacyTagger:
    def __init__(self, name: str = "en_core_web_sm"):
        import spacy
        self.nlp = spacy.load(name, disable=["lemmatizer", "ner"])
        self.meta = self.nlp.meta

    def __call__(self, text: str):
        return [(t.text, t.pos_, t.idx) for t in self.nlp(text)]


@dataclass(frozen=True)
class PrefixResult:
    eligible: bool
    prefix: str | None
    n_words: int
    target_noun: str | None
    reason: str


def _nouns(tokens):
    return [i for i, (_, pos, _) in enumerate(tokens) if pos in NOUN_TAGS]


def prefix_for(caption: str, tagger: Tagger, rung: int = 1) -> PrefixResult:
    cap = " ".join(caption.strip().split())
    low = cap.lower()
    if len(low) != len(cap):          # case mapping changed the length: offsets would be wrong, so never eligible (deterministic)
        return PrefixResult(False, None, 0, None, "case-fold length change")
    toks = tagger(low)
    nouns = _nouns(toks)
    need = rung + 1                    # rung 1 needs t2 (second noun), rung 2 needs t3
    if len(nouns) < need:
        return PrefixResult(False, None, 0, None, f"fewer than {need} nouns")
    tgt = toks[nouns[need - 1]]
    prefix = cap[:tgt[2]].rstrip()
    n_words = len(prefix.split())
    lo, hi = RUNG_WORDS[rung]
    if not (lo <= n_words <= hi):
        return PrefixResult(False, prefix, n_words, tgt[0], f"prefix has {n_words} words, need {lo}-{hi}")
    return PrefixResult(True, prefix, n_words, tgt[0], "ok")


def prompt_text(prefix: str, n_mask: int = 32) -> str:
    """Prompt-slot text: the prefix immediately followed by the mask tokens '<m>' (no space: a space would add a lone U+2581 token)."""
    return prefix + "<m>" * n_mask
