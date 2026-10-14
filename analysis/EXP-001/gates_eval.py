"""Gate evaluation runners (EXP-001 card v0.5: PG-1 4.3, PG-V 4.4, PC-F 4.4/8.8). EVAL venv, offline, after generation.

  python analysis/EXP-001/gates_eval.py pg1g   --stage-dir runs/EXP-001/gates/pg1g
  python analysis/EXP-001/gates_eval.py pg1p   --stage-dir runs/EXP-001/gates/pg1p --real-dir runs/EXP-001/gates/realvq
  python analysis/EXP-001/gates_eval.py pgv    --stage-dir runs/EXP-001/gates/pgv --rung 1
  python analysis/EXP-001/gates_eval.py pcf
Each writes runs/EXP-001/gates/verdict-<name>.json (numbers, thresholds, pass/fail, input hashes).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import caption_end as ce
import completion as cp
import metrics as M
import prefix_rule as pr

GATES = ROOT / "runs" / "EXP-001" / "gates"
COCO_ZIP = Path(r"C:\Users\Shlok\.cache\dlm_dl\coco\val2017.zip")
LLAMA_TOK = Path(r"C:\Users\Shlok\.cache\huggingface\hub\models--NousResearch--Llama-2-7b-hf\snapshots\8efe6c9b93655b934e27bd9981e3ec13e55aee9d")


def sha_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_draw():
    return json.loads((GATES / "coco_draw.json").read_text(encoding="utf8"))


def llama_tok():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(str(LLAMA_TOK), use_fast=False)


def pil_open(p):
    from PIL import Image
    return Image.open(p).convert("RGB")


def coco_image(zf, fname):
    from PIL import Image
    return Image.open(io.BytesIO(zf.read("val2017/" + fname))).convert("RGB")


def write_verdict(name, obj):
    GATES.mkdir(parents=True, exist_ok=True)
    p = GATES / f"verdict-{name}.json"
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, "item") else str(o)), encoding="utf8")
    print("wrote", p)
    return p


# ------------------------------------------------------------------------------------------------------------- PG-1 guided
def pg1_guided(stage_dir: Path):
    from evalmodels import ClipScorer
    metas = {}
    for res in (512, 1024):
        metas[res] = [json.loads(p.read_text(encoding="utf8")) for p in sorted(stage_dir.glob(f"item*_{res}px.json"))]
    n = len(metas[512])
    assert n == len(metas[1024]) and n > 0, "incomplete stage"
    clip = ClipScorer()
    caps = [m["caption"] for m in metas[512]]
    T = clip.texts(caps)
    S, raw, lifts = {}, {}, {}
    for res in (512, 1024):
        imgs = clip.images([pil_open(stage_dir / f"item{k:02d}_{res}px.png") for k in range(n)])
        S[res] = M.sim_matrix(imgs, T)
        raw[res] = 100.0 * np.diag(S[res])
        lifts[res] = float(M.lift(S[res]).mean())
    diff = raw[512] - raw[1024]
    boot = M.paired_bootstrap(S[512], S[1024], B=2000, seed=11, which="C")
    out = {"n_items": n, "mean_raw_matched_512": float(raw[512].mean()), "mean_raw_matched_1024": float(raw[1024].mean()),
           "mean_paired_diff_512_minus_1024": float(diff.mean()), "paired_diff_se": float(diff.std(ddof=1) / np.sqrt(n)),
           "lift_512": lifts[512], "lift_1024": lifts[1024], "lift_ratio": lifts[512] / lifts[1024] if lifts[1024] != 0 else None,
           "criterion_diff_ge_-2.0": bool(diff.mean() >= -2.0),
           "criterion_lift_ge_0.8x": bool(lifts[512] >= 0.8 * lifts[1024]),
           "clip_text_truncated": clip.truncated, "seconds_512_mean": float(np.mean([m["seconds"] for m in metas[512]])),
           "seconds_1024_mean": float(np.mean([m["seconds"] for m in metas[1024]])),
           "n_masked_after_max": int(max(m["n_masked_after"] for m in metas[512] + metas[1024]))}
    out["guided_leg_pass_512"] = bool(out["criterion_diff_ge_-2.0"] and out["criterion_lift_ge_0.8x"])
    return out


# ----------------------------------------------------------------------------------------------------------- PG-1 condition P
def code_share(codes) -> float:
    c = np.asarray(codes)
    return len(set(c.tolist())) / len(c)


def near_uniform(pil, thr=6.0) -> bool:
    a = np.asarray(pil.convert("L"), dtype=np.float64)
    return bool(a.std() < thr)


def make_grid(pils, path, cell=192):
    from PIL import Image
    g = Image.new("RGB", (4 * cell, 4 * cell))
    for i, p in enumerate(pils[:16]):
        g.paste(p.resize((cell, cell)), ((i % 4) * cell, (i // 4) * cell))
    g.save(path)


def pg1_pleg(stage_dir: Path, real_dir: Path, ressel=(512, 1024)):
    from evalmodels import ClipScorer
    out = {}
    metas = {r: [json.loads(p.read_text(encoding="utf8")) for p in sorted(stage_dir.glob(f"item*_{r}px.json"))] for r in ressel}
    n = len(metas[ressel[0]])
    assert n > 0 and all(len(v) == n for v in metas.values()), "incomplete stage"
    real = [json.loads(p.read_text(encoding="utf8")) for p in sorted(real_dir.glob("real*_512px.json"))]
    real_share = [m["n_distinct"] / m["n"] for m in real]
    clip = ClipScorer()
    for r in ressel:
        imgs = [pil_open(stage_dir / f"item{k:02d}_{r}px.png") for k in range(n)]
        shares = [code_share(np.load(stage_dir / f"item{k:02d}_{r}px.npz")["img"]) for k in range(n)]
        iqa = clip.iqa(imgs)
        make_grid(imgs, GATES / f"grid_pleg_{r}px.png")
        out[str(r)] = {"median_code_share": float(np.median(shares)), "mean_iqa": float(iqa.mean()), "sd_iqa": float(iqa.std(ddof=1)),
                       "near_uniform_proxy_count": int(sum(near_uniform(p) for p in imgs)), "grid": f"grid_pleg_{r}px.png",
                       "mean_seconds": float(np.mean([m["seconds"] for m in metas[r]]))}
    med_real = float(np.median(real_share)) if real_share else None
    s512, s1024 = out["512"], out["1024"]
    out["real_median_code_share_512px"] = med_real
    out["criterion_i_code_share"] = bool(med_real is not None and s512["median_code_share"] >= 0.5 * med_real)
    out["criterion_ii_iqa"] = bool(s512["mean_iqa"] >= s1024["mean_iqa"] - 0.5 * s1024["sd_iqa"])
    out["criterion_iii_near_uniform_proxy_le_2"] = bool(s512["near_uniform_proxy_count"] <= 2)
    out["criterion_iii_note"] = "the engineer's visual count (grid file) is recorded in IMPLEMENTATION.md; the proxy is pixel SD < 6 on 8-bit grey"
    return out


def pg1_decision(guided_pass: bool, pleg_pass_conf: bool, pleg_pass_rand: bool | None = None, pleg256: dict | None = None):
    """Decision table of 4.3."""
    if guided_pass and pleg_pass_conf:
        return {"resolution": 512, "position_rule": "P (confidence)", "fork": None}
    if guided_pass and not pleg_pass_conf:
        if pleg_pass_rand is None:
            return {"resolution": None, "position_rule": None, "fork": "repeat the condition-P leg with P_rand"}
        if pleg_pass_rand:
            return {"resolution": 512, "position_rule": "P_rand (primary)", "fork": "R12"}
        return {"resolution": None, "position_rule": None, "fork": "repeat both legs at 256 px"}
    return {"resolution": None, "position_rule": None, "fork": "guided leg failed: repeat both legs at 256 px"}


# ------------------------------------------------------------------------------------------------------------------- PG-V
def pgv(stage_dir: Path, rung: int):
    from evalmodels import ClipScorer, VlmScorer
    import evalmodels  # noqa
    spec = [json.loads(p.read_text(encoding="utf8")) for p in sorted(stage_dir.glob("seed*.json"))]
    assert len(spec) == 48, f"need 48 samples, found {len(spec)}"
    spec.sort(key=lambda m: m["i"])
    tok = llama_tok()
    table = ce.PieceTable.from_tokenizer(tok)
    from prefix_rule import SpacyTagger
    tagger = SpacyTagger()
    stop = set(cp.load_list(HERE / "nonvisual_nouns.txt"))
    pat = ce.load_patterns()
    ends, nouns, comps, caps = [], [], [], []
    for m in spec:
        t = np.load(stage_dir / f"seed{m['i']}.npz")["tail"].tolist()
        e = ce.caption_end(t, table(t), pat)
        comp = cp.completion_text(tok, t, e)
        ends.append(e)
        comps.append(comp)
        caps.append(cp.full_caption(m["prefix"], comp))
        nouns.append(cp.completion_nouns(m["prefix"], comp, tagger, stop))
    imgs = [pil_open(stage_dir / f"seed{m['i']}.png") for m in spec]
    del table
    vlm = VlmScorer()
    cache = {}

    def present(noun, j):
        k = (noun, j)
        if k not in cache:
            cache[k] = vlm.presence(imgs[j], noun)
        return cache[k] >= 0.5

    stat = cp.pgv_statistic(nouns, present)
    debris = [e.debris_share for e in ends]
    gate = cp.pgv_gate(stat, debris)
    mean_sp, ci_sp = cp.cluster_bootstrap_diff(stat["matched_i"], stat["same_i"], B=10000, seed=5)
    mean_x, ci_x = cp.cluster_bootstrap_diff(stat["matched_i"], stat["cross_i"], B=10000, seed=6)
    # reported alongside (descriptive)
    comp_len = [e.completion_len for e in ends]
    recs = [m["records"] for m in spec]
    def cls_at(q):
        flags = []
        for m, r in zip(spec, recs):
            rec = next((x for x in r if x["q"] == q), None)
            e = ends[spec.index(m)]
            if rec is None or not rec["text_pos"]:
                continue
            j = rec["text_pos"][0]
            flags.append(bool(rec["text_state_pad"][0]) or (j + 1 >= e.e))
        return float(np.mean(flags)) if flags else None
    import ha_source as hs
    src = {}
    for q in (1, 2, 6, 26, 30):
        avail, ws = [], []
        for m, r in zip(spec, recs):
            rec = next((x for x in r if x["q"] == q), None)
            if rec is None:
                continue
            s = hs.select_source(rec["masked_text_idx"], rec["maxp_text"], rec["padmass_text"], 16)   # provisional L_c upper bound
            avail.append(s is not None)
            if s is not None:
                ws.append(s[1])
        src[str(q)] = {"share_with_source_Lc16": float(np.mean(avail)) if avail else None, "mean_w": float(np.mean(ws)) if ws else None}
    L_c = hs.compute_L_c(comp_len)
    out = {"rung": rung, "n_samples": len(spec), "stat": {k: v for k, v in stat.items() if not k.endswith("_i")},
           "gate": gate, "m_minus_s_sp": {"estimate": mean_sp, "ci90_cluster": ci_sp,
                                           "line": ("no measurable co-generation dependence at this rung (PG-V, 24 prefixes)" if ci_sp[0] <= 0 else None)},
           "m_minus_s_cross": {"estimate": mean_x, "ci90_cluster": ci_x},
           "e2_share": float(np.mean([e.e2_set for e in ends])),
           "caption_end_set_by": {k: int(sum(e.set_by == k for e in ends)) for k in ("e0", "e1", "e2", "cap")},
           "completion_len": {"mean": float(np.mean(comp_len)), "p90": float(np.percentile(comp_len, 90)), "min": int(min(comp_len)), "max": int(max(comp_len))},
           "caption_end_index_hist": np.bincount([int(e.e) for e in ends], minlength=34).tolist(),
           "pad_share_of_tail": float(np.mean([sum(1 for q in np.load(stage_dir / f"seed{m['i']}.npz")["tail"] if int(q) in (0, 2)) / 32 for m in spec])),
           "debris_share": {"median": float(np.median(debris)), "mean": float(np.mean(debris))},
           "committed_text_token_state_pad_or_post_caption_share": {"pass2": cls_at(2), "pass6": cls_at(6)},
           "source_availability": src, "L_c": L_c,
           "tagger": "spaCy en_core_web_sm", "n_vlm_calls": len(cache),
           "nouns": [{"i": m["i"], "prefix": m["prefix"], "caption": c, "nouns": nn, "caption_end": e.e, "set_by": e.set_by}
                     for m, c, nn, e in zip(spec, caps, nouns, ends)]}
    if gate["pass"]:
        (HERE / "L_c.txt").write_text(f"{L_c}\n", encoding="utf8")
        out["L_c_written"] = str(HERE / "L_c.txt")
    return out


# ------------------------------------------------------------------------------------------------------------------- PC-F
def pcf():
    from evalmodels import VlmScorer
    draw = load_draw()
    items = draw["blocks"]["PCF"]
    assert len(items) == 48
    zf = zipfile.ZipFile(COCO_ZIP)
    imgs = [coco_image(zf, it["file"]) for it in items]
    from prefix_rule import SpacyTagger
    tagger = SpacyTagger()
    stop = set(cp.load_list(HERE / "nonvisual_nouns.txt"))
    nouns = []
    for it in items:
        toks = tagger(it["caption"].lower())
        nn = []
        for text, pos, _ in toks:
            if pos in ("NOUN", "PROPN") and text not in stop and text not in nn and text.isalpha():
                nn.append(text)
        nouns.append(nn)
    vlm = VlmScorer()
    cache = {}

    def present(noun, j):
        if (noun, j) not in cache:
            cache[(noun, j)] = vlm.presence(imgs[j], noun)
        return cache[(noun, j)] >= 0.5

    der = cp.pgv_derangements(n_prefix=48, n_seed=1)
    stat = cp.pgv_statistic(nouns, present, n_prefix=48, n_seed=1, der=der)
    gate = cp.pcf_gate(stat["m"], stat["s"])
    # V-lift of real pairs with two fixed derangements
    d1, d2 = M.derangement(48, 9101), M.derangement(48, 9102)
    caps = [it["caption"] for it in items]
    s_m = np.array([vlm.vqa_score(imgs[i], caps[i]) for i in range(48)])
    s_1 = np.array([vlm.vqa_score(imgs[i], caps[int(d1[i])]) for i in range(48)])
    s_2 = np.array([vlm.vqa_score(imgs[int(d2[i])], caps[i]) for i in range(48)])
    V = M.vlift(s_m, s_1, s_2)
    g = np.random.default_rng(3)
    reps = np.array([V[g.integers(0, 48, 48)].mean() for _ in range(10000)])
    ci = (float(np.quantile(reps, 0.025)), float(np.quantile(reps, 0.975)))
    return {"gate": gate, "stat": {k: v for k, v in stat.items() if not k.endswith("_i")}, "vlift_mean": float(V.mean()), "vlift_ci95": ci,
            "vlift_excludes_0": bool(ci[0] > 0), "pass": bool(gate["pass"] and ci[0] > 0), "n_vlm_calls": len(cache) + 48 * 3,
            "vqa_template": vlm.template, "presence_template": vlm.presence_template}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=["pg1g", "pg1p", "pgv", "pcf"])
    ap.add_argument("--stage-dir", default=None)
    ap.add_argument("--real-dir", default=str(GATES / "realvq"))
    ap.add_argument("--rung", type=int, default=1)
    ap.add_argument("--name", default=None)
    a = ap.parse_args()
    if a.which == "pg1g":
        res = pg1_guided(Path(a.stage_dir))
    elif a.which == "pg1p":
        res = pg1_pleg(Path(a.stage_dir), Path(a.real_dir))
    elif a.which == "pgv":
        res = pgv(Path(a.stage_dir), a.rung)
    else:
        res = pcf()
    write_verdict(a.name or a.which, res)


if __name__ == "__main__":
    main()
