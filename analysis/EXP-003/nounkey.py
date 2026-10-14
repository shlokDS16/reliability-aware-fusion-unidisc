"""Noun key kappa (EXP-003 card v0.3.2, 4.1). FROZEN before the pilot. Used for set operations only; the VLM is asked the surface form.

kappa(n) = lower-cased surface with a final plural -s or -es removed when at least three letters remain.
Reading of "-s or -es" (the card gives only that sentence): the suffix -es is removed when the stem before it ends in s, x, z, ch or sh
(boxes -> box, glasses -> glass, sandwiches -> sandwich), otherwise a final -s is removed (giraffes -> giraffe, kites -> kite), never
from a word ending in -ss (glass stays glass); a removal that would leave fewer than three letters is not done.
"""
from __future__ import annotations


def key(surface: str) -> str:
    w = surface.strip().lower()
    if w.endswith("es") and len(w) - 2 >= 3 and w[:-2].endswith(("s", "x", "z", "ch", "sh")):
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) - 1 >= 3:
        return w[:-1]
    return w


def keys(surfaces) -> set:
    return {key(s) for s in surfaces}


def exact(surface: str) -> str:
    """Sensitivity (card 7): discordance by the exact lower-cased surface string instead of the key."""
    return surface.strip().lower()
