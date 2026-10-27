"""Per-item building blocks shared by the M1-M5 runners. All take a scorer with the UniScorer interface; none loads a model."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from exp_p2 import common, core
from exp_p2.gate import config, scores
from exp_p2.gate.evidence import gather_codes, evidence_from_delta, text_pmi, text_pair
from exp_p2.gate.dcache import DCache


def dcache_for(root: Path | None = None) -> DCache:
    return DCache(Path(common.RUNS) / config.DCACHE_RUN_ID if root is None else root)


def prep_image(sc, image_id: int):
    """COCO image -> (512x512 PIL as the model sees it, clean codes [m])."""
    pil = sc.preprocess(common.load_image(image_id))
    return pil, sc.encode(pil)


def item_groups(sc, gid: int, K: int = config.K) -> np.ndarray:
    """Complementary mask groups of the gate statistic: probe 2's seed rule with the gate seed and the item's global id."""
    return core.complementary_groups(sc.L_I, K, np.random.default_rng([config.SEED_GATE, gid, 99]))


def gate_scores(sc, cap_tok: list[int], codes: np.ndarray, groups: np.ndarray, dcache: DCache, K: int = config.K) -> dict:
    """B (K passes, caption masked), D (layout-only null, cached), u = -(B - D) float32, s3 = 1 - maxp."""
    st = sc.build(cap_tok, codes)
    sb = scores.image_B(sc, st, groups, K)
    D = dcache.image_logp(sc, st, len(cap_tok), codes)
    return dict(B=sb["B"], D=D, u=scores.suspicion_q(sb["B"], D), s3=(1.0 - sb["maxp"]).astype(np.float32), maxp=sb["maxp"])


def caption_lambdas(sc, cap_tok: list[int], neg_tok: list[int], any_codes: np.ndarray):
    """Lambda^{c+}, Lambda^{c-}: image fully masked, caption visible (2 passes). They do not depend on `any_codes`."""
    return (scores.full_image_lp(sc, sc.build(cap_tok, any_codes), caption_masked=False),
            scores.full_image_lp(sc, sc.build(neg_tok, any_codes), caption_masked=False))


def image_delta(lam_pos, lam_neg, codes: np.ndarray) -> np.ndarray:
    """Per-token paired evidence Delta_j = Lambda^{c+}_j[v_j] - Lambda^{c-}_j[v_j] (float32 [m])."""
    return (gather_codes(lam_pos, codes) - gather_codes(lam_neg, codes)).astype(np.float32)


def text_direction(sc, cap_tok: list[int], neg_tok: list[int], codes: np.ndarray, gates: list, dcache: DCache) -> list[dict]:
    """Text-direction conditioning arms for one image condition: for each gate (None = none) the paired pmi of c+ vs c- with the gated image tokens
    masked and the caption fully masked. 2 x len(gates) passes (batched in groups of 4); the null is the cached layout-only D^T."""
    out_lp = []
    for tok in (cap_tok, neg_tok):
        st = sc.build(tok, codes)
        lps = scores.text_arms_lp(sc, st, gates)
        null = dcache.text_logp(sc, st, len(tok), tok)
        out_lp.append([text_pmi(gather_codes(lp, np.asarray(tok)), null) for lp in lps])
    return [text_pair(p, n) for p, n in zip(*out_lp)]


def load_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def compact(ev: dict) -> dict:
    """Row-sized view of an evidence dict (drops the sum)."""
    return {k: ev[k] for k in ("n", "mean", "sd", "z", "d", "y")}


def require_frozen(runs: Path | None = None) -> Path:
    """detection_frozen.json (rival and sign, SAP A1.2 rule 5) must exist, committed, before M3 and M4 run (audit M4)."""
    p = Path(runs if runs is not None else common.RUNS) / "P2-GATE-M1" / "detection_frozen.json"
    if not p.exists():
        raise FileNotFoundError(f"{p} missing: complete M1, run python -m exp_p2.analyze_gate_m1 and commit detection_frozen.json first (required before M3 and M4, SAP A1.2 rule 5)")
    return p


class FoldDefect(RuntimeError):
    """More than 10 percent of one fold fails the real-tokenizer check: a fold-construction defect (SAP A2.1 item 2); stop and report."""


def check_fold_tokens(sc, folds_dict: dict, run: Path) -> dict:
    """Frozen token counts in folds.json versus the runtime tokenizer path (UniScorer.caption_ids). Per SAP Addendum 2 (A2.1 item 2) an item whose runtime count is outside 5-32 is
    EXCLUDED, counted and not replaced; the report is written to folds_check.json and token_exclusions.json in the run directory and returned. Raises FoldDefect when more than
    10 percent of any one fold is excluded (or differs from the frozen count): no refolding without a new card version."""
    from exp_p2.gate import folds as folds_mod
    rep = folds_mod.token_check(folds_dict, lambda c: len(sc.caption_ids(c)))
    Path(run).mkdir(parents=True, exist_ok=True)
    (Path(run) / "folds_check.json").write_text(json.dumps(rep), encoding="utf8")
    (Path(run) / "token_exclusions.json").write_text(json.dumps(dict(excluded=rep["excluded"], n_excluded_total=rep["n_excluded_total"])), encoding="utf8")
    if rep["defect"]:
        raise FoldDefect(f"fold-construction defect: more than {rep['max_fail_fraction']:.0%} of {rep['defect_folds']} fails the runtime tokenizer check; stop and report ({rep['per_fold']})")
    return rep


def drop_excluded(items: list[dict], rep: dict, fold: str) -> list[dict]:
    """Remove the excluded items of `fold` from an ordered item list, without replacement and without reordering."""
    bad = set(rep["excluded"].get(fold, []))
    return [it for it in items if it["idx"] not in bad]
