"""Completion text, completion nouns (4.4), POS labels of tail tokens (2) and the PG-V gate statistic (4.4, 4.3). Pure functions of
token ids, the caption-end rule, a tagger (Protocol of prefix_rule) and VLM presence probabilities. Frozen before PG-V.

Detokenisation: caption = prefix + ' ' + decode(completion ids) with the pinned Llama-2 tokenizer (decode of ids drops a leading
'▁', so a completion token with a leading space starts a new word, and one without it continues the word of the prefix; the
official layout puts one space between the prefix and the mask run, so the first completion token is word-initial in the
detokenised caption by construction).
"""
from __future__ import annotations

import numpy as np

import caption_end as ce

FUNCTION_POS = ("DET", "ADP", "AUX", "PRON", "CCONJ", "SCONJ", "PART", "PUNCT")
NOUN_POS = ("NOUN", "PROPN")


def load_list(path) -> list[str]:
    return [l.strip().lower() for l in open(path, encoding="utf8").read().splitlines() if l.strip() and not l.startswith("#")]


def completion_text(tok, tail_ids, cend: ce.CaptionEnd) -> str:
    ids = [int(i) for i in tail_ids[:cend.completion_len]]
    return tok.decode(ids, skip_special_tokens=False).strip() if ids else ""


def full_caption(prefix: str, comp: str) -> str:
    return (prefix + " " + comp).strip() if comp else prefix


def completion_nouns(prefix: str, comp: str, tagger, stoplist) -> list[str]:
    """Nouns (NOUN/PROPN on the final caption) of the completion that are not in the prefix and not in the stoplist."""
    if not comp:
        return []
    cap = full_caption(prefix, comp)
    toks = tagger(cap.lower())
    start = len(prefix) + 1
    pre_words = {w.strip(".,!?;:").lower() for w in prefix.split()}
    out, seen = [], set()
    for text, pos, idx in toks:
        w = text.lower()
        if idx >= start and pos in NOUN_POS and w not in pre_words and w not in stoplist and w not in seen and any(c.isalpha() for c in w):
            out.append(w)
            seen.add(w)
    return out


def token_spans(tok, tail_ids, n: int) -> list[tuple[int, int]]:
    """Character spans of the first n tail tokens inside decode(tail_ids[:n]) (start of token k = length of the decode of the
    first k-1 tokens, plus one if the piece starts a new word)."""
    spans, prev = [], 0
    for k in range(1, n + 1):
        cur = len(tok.decode([int(i) for i in tail_ids[:k]], skip_special_tokens=False))
        spans.append((prev, cur))
        prev = cur
    return spans


def label_tail_tokens(tok, prefix: str, tail_ids, cend: ce.CaptionEnd, tagger) -> list[str]:
    """POS label per tail token (list of 32): UPOS of the word at word-initial completion subtokens, 'SUB' for non-word-initial
    subtokens, 'POST' for post-caption positions, 'NONE' for completion tokens without alphabetic content."""
    n = 32
    labels = ["POST"] * n
    L = cend.completion_len
    if L == 0:
        return labels
    comp = tok.decode([int(i) for i in tail_ids[:L]], skip_special_tokens=False)
    cap = full_caption(prefix, comp.strip())
    toks = tagger(cap.lower())
    offset = len(prefix) + 1 - (len(comp) - len(comp.lstrip()))         # caption position of comp[0]
    spans = token_spans(tok, tail_ids, L)
    for k, (a, b) in enumerate(spans):
        piece = comp[a:b]
        if not (k == 0 or piece.startswith(" ")):
            labels[k] = "SUB"                                   # continuation of a word (or attached punctuation)
            continue
        ca = offset + a + (len(piece) - len(piece.lstrip()))
        hit = [t for t in toks if t[2] <= ca < t[2] + max(len(t[0]), 1)]
        labels[k] = hit[0][1] if hit else "NONE"
    return labels


def stratum_of(label: str) -> str | None:
    """H-A strata: object noun / other content / function. Post-caption positions and sub-word continuations are excluded."""
    if label in NOUN_POS:
        return "noun"
    if label in FUNCTION_POS:
        return "function"
    if label in ("POST", "SUB", "NONE"):
        return None
    return "other"


# ------------------------------------------------------------------------------------------------------------------ PG-V
def pgv_derangements(n_prefix: int = 24, n_seed: int = 2, n_der: int = 4, base_seed: int = 4401) -> np.ndarray:
    """Fixed cross-prefix derangements over the n_prefix x n_seed samples (sample index = n_seed * p + e): each maps a sample to a
    sample with a DIFFERENT prefix (never the same prefix). Deterministic."""
    n = n_prefix * n_seed
    out = []
    for d in range(n_der):
        g = np.random.default_rng(base_seed + d)
        while True:
            p = g.permutation(n)
            if np.all(p // n_seed != np.arange(n) // n_seed):
                out.append(p)
                break
    return np.stack(out)


def same_prefix_partner(n_prefix: int = 24, n_seed: int = 2) -> np.ndarray:
    idx = np.arange(n_prefix * n_seed)
    return (idx // n_seed) * n_seed + ((idx % n_seed + 1) % n_seed)


def pgv_statistic(nouns: list[list[str]], present, n_prefix: int = 24, n_seed: int = 2, der: np.ndarray | None = None) -> dict:
    """nouns[i]: completion nouns of sample i; present(noun, j) -> bool (VLM P(yes) >= 0.5 for the image of sample j).
    presence_i(img) = any noun present (0 if no nouns)."""
    n = n_prefix * n_seed
    der = pgv_derangements(n_prefix, n_seed) if der is None else der
    sp = same_prefix_partner(n_prefix, n_seed)

    def pres(i, j):
        return float(any(present(nn, j) for nn in nouns[i])) if nouns[i] else 0.0

    matched = np.array([pres(i, i) for i in range(n)])
    cross = np.array([[pres(i, int(der[d, i])) for i in range(n)] for d in range(len(der))]).mean(0)
    same = np.array([pres(i, int(sp[i])) for i in range(n)])
    nonempty = np.array([len(x) > 0 for x in nouns])
    # per-noun rates (matched, cross-prefix, same-prefix) beside the OR-rule
    pm = ps = pc = cnt = 0
    for i in range(n):
        for nn in nouns[i]:
            pm += present(nn, i)
            ps += present(nn, int(sp[i]))
            pc += np.mean([present(nn, int(der[d, i])) for d in range(len(der))])
            cnt += 1
    return {"m": float(matched.mean()), "s": float(cross.mean()), "s_sp": float(same.mean()), "nonempty_share": float(nonempty.mean()),
            "matched_i": matched, "cross_i": cross, "same_i": same,
            "per_noun": {"n_nouns": int(cnt), "matched": pm / max(cnt, 1), "cross": pc / max(cnt, 1), "same_prefix": ps / max(cnt, 1)}}


def pgv_gate(stat: dict, debris_shares) -> dict:
    """Pass iff (a) non-empty share >= 0.60, (b) m >= 0.50, (c) m - s >= 0.25, (d) median debris share < 0.5."""
    a = stat["nonempty_share"] >= 0.60
    b = stat["m"] >= 0.50
    c = (stat["m"] - stat["s"]) >= 0.25
    d = float(np.median(debris_shares)) < 0.5
    return {"a_nonempty_share_ge_0.60": bool(a), "b_m_ge_0.50": bool(b), "c_m_minus_s_ge_0.25": bool(c), "d_median_debris_lt_0.5": bool(d),
            "pass": bool(a and b and c and d), "m_minus_s": float(stat["m"] - stat["s"]), "median_debris_share": float(np.median(debris_shares))}


def cluster_bootstrap_diff(matched_i, other_i, n_prefix=24, n_seed=2, B=10000, seed=0, level=0.90):
    """Cluster (prefix) bootstrap interval of mean(matched - other) (common-cause check m - s_sp, 90 percent)."""
    diff = (np.asarray(matched_i) - np.asarray(other_i)).reshape(n_prefix, n_seed).mean(1)
    g = np.random.default_rng(seed)
    reps = np.array([diff[g.integers(0, n_prefix, n_prefix)].mean() for _ in range(B)])
    a = (1 - level) / 2
    return float(diff.mean()), (float(np.quantile(reps, a)), float(np.quantile(reps, 1 - a)))


def pcf_gate(m_real: float, s_real: float) -> dict:
    """Checker precondition on 48 real COCO pairs: m_real >= 0.70 and m_real - s_real >= 0.40."""
    return {"m_real": m_real, "s_real": s_real, "pass": bool(m_real >= 0.70 and (m_real - s_real) >= 0.40)}
