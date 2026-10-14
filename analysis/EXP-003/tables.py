"""Samples, completions, nouns, query plans and prefix records of EXP-003 (eval venv for the loaders; the plan functions are pure)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(HERE), str(ROOT / "analysis" / "EXP-001")]

import nounkey                                   # noqa: E402
import stats as S                                # noqa: E402
from exp003.config import RUNS, DERANGEMENT_SEED_CROSS, DERANGEMENT_SEED_PLACEBO  # noqa: E402

GEN = RUNS / "gen"
SCORE = RUNS / "score"
LLAMA_TOK = Path(r"C:\Users\Shlok\.cache\huggingface\hub\models--NousResearch--Llama-2-7b-hf\snapshots\8efe6c9b93655b934e27bd9981e3ec13e55aee9d")
SCOPE_ARMS = {"pilot": ("P64", "G", "O0", "P32", "Ind", "TF"), "ctrl": ("Ind", "TF"), "main": ("P64", "G", "O0", "P32")}
MAIN_DIR = {"P64": "m1", "G": "m1", "O0": "m2", "P32": "m3"}
NO_CROSS = {"P32"}                               # card 4.3 item 3: P32 has no cross-prefix calls
NO_PLACEBO = {"TF"}


def arm_dir(scope: str, arm: str, gen_dir: Path = GEN) -> Path:
    return gen_dir / (MAIN_DIR[arm] if scope == "main" else scope) / arm


def derangement(n: int, seed: int) -> np.ndarray:
    g = np.random.default_rng(seed)
    while True:
        p = g.permutation(n)
        if n < 2 or not np.any(p == np.arange(n)):
            return p


class Tools:
    """Tokenizer, piece table, tagger, stoplist, debris patterns (all frozen EXP-001 objects)."""

    def __init__(self):
        import caption_end as ce, completion as cp, prefix_rule as pr
        from transformers import AutoTokenizer
        self.ce, self.cp = ce, cp
        self.tok = AutoTokenizer.from_pretrained(str(LLAMA_TOK), use_fast=False)
        self.table = ce.PieceTable.from_tokenizer(self.tok)
        self.tagger = pr.SpacyTagger()
        self.stop = set(cp.load_list(ROOT / "analysis" / "EXP-001" / "nonvisual_nouns.txt"))
        self.pat = ce.load_patterns()


def load_sample(base: Path, item: dict, tools: Tools):
    """One generated sample or None (missing or failed unit)."""
    j = base.with_suffix(".json")
    if not j.exists():
        return None
    m = json.loads(j.read_text(encoding="utf8"))
    if m.get("failed"):
        return None
    z = np.load(base.with_suffix(".npz"))
    tail = [int(x) for x in z["tail"]]
    ce, cp = tools.ce, tools.cp
    e = ce.caption_end(tail, tools.table(tail), tools.pat)
    comp = cp.completion_text(tools.tok, tail, e)
    prefix = item["prefix"]
    return dict(meta=m, tail=tail, cend=e, comp=comp, prefix=prefix, caption=cp.full_caption(prefix, comp),
                nouns=cp.completion_nouns(prefix, comp, tools.tagger, tools.stop), png=base.with_suffix(".png"),
                commit_step=z["commit_step"] if "commit_step" in z.files else None)


def load_arm(scope, arm, n_prefix, items, tools, gen_dir: Path = GEN):
    d = arm_dir(scope, arm, gen_dir)
    return [[load_sample(d / f"p{p:03d}_e{e}", items[p], tools) for e in (0, 1)] for p in range(n_prefix)]


# ------------------------------------------------------------------------------------------------------------------- query plan
def noun_sets(samples):
    """Per prefix: N (list of 2), D (discordant by the noun key), or None when a seed is missing."""
    out = []
    for pair in samples:
        if pair[0] is None or pair[1] is None:
            out.append(None)
            continue
        N = [pair[0]["nouns"], pair[1]["nouns"]]
        D = list(S.discordant(N[0], N[1], nounkey.key))
        out.append(dict(N=N, D=D))
    return out


def placebo_sets(sets, n_prefix, seed=DERANGEMENT_SEED_PLACEBO):
    """NC-2 placebo nouns (card 4.1): for prefix p and seed e, as many placebo nouns as |D_pe|, drawn without replacement from the discordant
    nouns of the prefix pi(p) of the same arm (one fixed derangement, seed 5302) whose key is absent from both completions of p. When the pool
    is smaller than |D_pe| all of it is used (flagged in the report); a prefix with an empty placebo side is not eligible for NC-2."""
    pi = derangement(n_prefix, seed)
    out = []
    for p in range(n_prefix):
        s, t = sets[p], sets[int(pi[p])]
        if s is None or t is None:
            out.append(None)
            continue
        bad = nounkey.keys(s["N"][0]) | nounkey.keys(s["N"][1])
        pool, seen = [], set()
        for n in t["D"][0] + t["D"][1]:
            k = nounkey.key(n)
            if k not in bad and k not in seen:
                pool.append(n)
                seen.add(k)
        pl = []
        for e in (0, 1):
            g = np.random.default_rng([seed, p, e])
            k = min(len(s["D"][e]), len(pool))
            pl.append([pool[i] for i in g.choice(len(pool), k, replace=False)] if k else [])
        out.append(dict(PL=pl, short=[len(pl[e]) < len(s["D"][e]) for e in (0, 1)]))
    return out


def queries_for_prefix(p, sets, plac, arm, n_prefix, cross_pi=None):
    """List of (noun, image_key 'p:e') VLM queries of one prefix: every completion noun on its own image, its sibling's image and (unless
    P32) the image of the same seed of the cross-prefix partner; the placebo nouns on both images of the prefix."""
    s = sets[p]
    if s is None:
        return []
    q = []
    for e in (0, 1):
        for n in s["N"][e]:
            q += [(n, f"{p}:{e}"), (n, f"{p}:{1 - e}")]
            if arm not in NO_CROSS and cross_pi is not None and sets[int(cross_pi[p])] is not None:
                q.append((n, f"{int(cross_pi[p])}:{e}"))
        if plac is not None and plac[p] is not None:
            for n in plac[p]["PL"][e]:
                q += [(n, f"{p}:{e}"), (n, f"{p}:{1 - e}")]
    return q


# --------------------------------------------------------------------------------------------------------------- scored records
def score_dir(scope, arm, root: Path = SCORE) -> Path:
    return Path(root) / scope / arm


def build_records(scope, arm, n_prefix, sets, plac, root: Path = SCORE, cross_pi=None):
    """Prefix records for stats.py from the per-prefix score files (p_yes >= 0.5 -> y = 1)."""
    d = score_dir(scope, arm, root)
    recs = []
    for p in range(n_prefix):
        f = d / f"p{p:03d}.json"
        s = sets[p]
        if s is None or not f.exists():
            recs.append(dict(ok=False))
            continue
        js = json.loads(f.read_text())
        y = {(n, k): (1.0 if v >= 0.5 else 0.0) for n, k, v in js["q"]}
        g = lambda n, k: y[(n, k)]
        r = dict(ok=True, N=s["N"], D=s["D"], iqa=js.get("iqa"))
        r["own"] = [np.array([g(n, f"{p}:{e}") for n in s["D"][e]]) for e in (0, 1)]
        r["sib"] = [np.array([g(n, f"{p}:{1 - e}") for n in s["D"][e]]) for e in (0, 1)]
        r["all_own"] = [np.array([g(n, f"{p}:{e}") for n in s["N"][e]]) for e in (0, 1)]
        r["all_sib"] = [np.array([g(n, f"{p}:{1 - e}") for n in s["N"][e]]) for e in (0, 1)]
        if arm not in NO_CROSS and cross_pi is not None and sets[int(cross_pi[p])] is not None:
            r["all_cross"] = [np.array([g(n, f"{int(cross_pi[p])}:{e}") for n in s["N"][e]]) for e in (0, 1)]
        if plac is not None and plac[p] is not None:
            r["PL"] = plac[p]["PL"]
            r["pown"] = [np.array([g(n, f"{p}:{e}") for n in plac[p]["PL"][e]]) for e in (0, 1)]
            r["psib"] = [np.array([g(n, f"{p}:{1 - e}") for n in plac[p]["PL"][e]]) for e in (0, 1)]
        else:
            r["pown"] = r["psib"] = [np.array([]), np.array([])]
        recs.append(r)
    return recs


def arm_bundle(scope, arm, n, items, tools, gen_dir: Path = GEN, score_root: Path = SCORE):
    """(samples, noun sets, placebo sets, prefix records) of one arm."""
    smp = load_arm(scope, arm, n, items, tools, gen_dir)
    sets = noun_sets(smp)
    plac = None if arm in NO_PLACEBO else placebo_sets(sets, n)
    recs = build_records(scope, arm, n, sets, plac, score_root, derangement(n, DERANGEMENT_SEED_CROSS))
    return smp, sets, plac, recs
