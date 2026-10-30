"""A2.3 pipeline audit of family PS (read-only, CPU). Recomputes from runs/P2-GATE-M4/arrays + items.jsonl; writes nothing in the repo."""
import hashlib, json, math, os, sys
from pathlib import Path
import numpy as np

os.environ["CUDA_VISIBLE_DEVICES"] = ""
ROOT = Path(sys.argv[1]); OUT = Path(sys.argv[2])
sys.path.insert(0, str(ROOT))
from exp_p2 import core                      # numpy only
from exp_p2.gate import arms, calibrate as cal, corruptions, evidence, config

run = ROOT / "runs" / "P2-GATE-M4"
thr = json.loads((ROOT / "runs/P2-GATE-M2/threshold.json").read_text())
TAU = {float(k): v["tau"] for k, v in thr["thresholds"].items()}; EPS0 = thr["eps0"]
rows = [json.loads(l) for l in open(run / "items.jsonl", encoding="utf8")]
seen, R = set(), []
for r in rows:
    if r["idx"] not in seen: seen.add(r["idx"]); R.append(r)
COND_ORDER = list(R[0]["conds"].keys())
ci_of = {n: i for i, n in enumerate(COND_ORDER)}
res = dict(n_rows=len(rows), n_unique=len(R), cond_order=COND_ORDER, eps0=EPS0, tau=TAU,
           sha256_items=hashlib.sha256((run / "items.jsonl").read_bytes()).hexdigest())

def ev(d, inc=None):
    return evidence.evidence_from_delta(d, inc)

def mcn(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    B, C = int((a & ~b).sum()), int((~a & b).sum()); n = B + C
    if n == 0: return dict(b=B, c=C, p=1.0)
    k = min(B, C); p = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
    return dict(b=B, c=C, p=p)

def auroc(score, lab):
    lab = np.asarray(lab, bool); s = np.asarray(score, float)
    if lab.all() or (~lab).all(): return float("nan")
    from scipy.stats import rankdata
    rk = rankdata(s); n1 = lab.sum(); n0 = (~lab).sum()
    return float((rk[lab].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

out = {}
for name in ("patch", "swap", "jpeg10", "noise0.1", "splice128", "clean"):
    mism = dict(codes_regen=0, z_regen=0, flag_regen={a: 0 for a in TAU}, y_none=0, y_gate=0, y_chg=0, n_gate=0, gate_counts=0, d_none=0, d_gate=0)
    recs = []
    for r in R:
        a = np.load(run / "arrays" / f"item{r['idx']:04d}.npz")
        cr = r["conds"][name]; gid = r["gid"]
        clean = a["clean_codes"].astype(np.int64)
        codes = a[f"{name}_codes"].astype(np.int64); z = a[f"{name}_z"]; delta = a[f"{name}_delta"]
        if name in ("patch", "swap"):
            tc = corruptions.apply_token(name, clean, corruptions.token_rng(config.SEED_GATE, gid, name), grid=32, patch=8, swap_frac=config.SWAP_FRAC, vocab=16384)
            mism["codes_regen"] += int(not np.array_equal(tc, codes))
        if name != "clean":
            mism["z_regen"] += int(not np.array_equal(clean != codes, z))
        u = -(a[f"{name}_B"].astype(np.float32) - a[f"{name}_D"].astype(np.float32))
        uj = cal.jitter(u, EPS0, arms.arm_rng(config.SEED_GATE, gid, ci_of[name], arms.ARM_TAG["jitter"], 0))
        for al, t in TAU.items():
            f = uj > t
            mism["flag_regen"][al] += int(not np.array_equal(f, a[f"{name}_flag{al:g}"]))
        G = a[f"{name}_flag0.05"]
        e_none, e_gate = ev(delta), ev(delta, ~G)
        st = cr["img"]
        mism["y_none"] += int(e_none["y"] != st["none"]["y"]); mism["y_gate"] += int(e_gate["y"] != st["gate0.05"]["y"])
        mism["n_gate"] += int(e_gate["n"] != st["gate0.05"]["n"])
        mism["d_none"] += int(not np.isclose(e_none["d"], st["none"]["d"], rtol=1e-9, atol=1e-12))
        mism["d_gate"] += int(not np.isclose(e_gate["d"], st["gate0.05"]["d"], rtol=1e-9, atol=1e-12, equal_nan=True))
        gs = cr["gate"]["0.05"]
        mism["gate_counts"] += int(gs["n_flag"] != int(G.sum()) or gs["n_tp"] != int((G & z).sum()))
        rec = dict(idx=r["idx"], y_none=e_none["y"], y_gate=e_gate["y"], mean_none=e_none["mean"], mean_gate=e_gate["mean"],
                   n_z=int(z.sum()), n_flag=int(G.sum()), tp=int((G & z).sum()), fp=int((G & ~z).sum()),
                   y_clean_none=int(r["conds"]["clean"]["img"]["none"]["y"]))
        if name != "clean":
            e_chg = ev(delta, ~z); mism["y_chg"] += int(e_chg["y"] != st["chg"]["y"])
            rec.update(y_chg=e_chg["y"], mean_chg=e_chg["mean"],
                       auroc_u=auroc(u, z) if 0 < z.sum() < len(z) else float("nan"),
                       mean_delta_z=float(delta[z].mean()) if z.any() else float("nan"),
                       mean_delta_notz=float(delta[~z].mean()),
                       sum_delta_z=float(delta[z].sum()), sum_delta_fp=float(delta[G & ~z].sum()), sum_delta_tp=float(delta[G & z].sum()),
                       mean_clean_delta_at_z=float(a["clean_delta"][z].mean()) if z.any() else float("nan"))
        recs.append(rec)
    df = {k: np.array([x.get(k, np.nan) for x in recs], float) for k in recs[0]}
    s = dict(mismatches=mism, n=len(recs))
    s["acc_none"] = float(df["y_none"].mean()); s["acc_gate"] = float(df["y_gate"].mean()); s["acc_clean_none"] = float(df["y_clean_none"].mean())
    s["gate_vs_none"] = mcn(df["y_gate"], df["y_none"])
    s["clean_vs_corrupt_none"] = mcn(df["y_clean_none"], df["y_none"])        # b = clean right & corrupted wrong (items the corruption flips to wrong)
    s["mean_flag_frac"] = float(df["n_flag"].mean() / 1024)
    if name != "clean":
        s["acc_chg"] = float(df["y_chg"].mean()); s["chg_vs_none"] = mcn(df["y_chg"], df["y_none"])
        s["chg_vs_clean_none"] = mcn(df["y_chg"], df["y_clean_none"])
        s["gate_vs_chg"] = mcn(df["y_gate"], df["y_chg"])
        s["tpr_pooled"] = float(df["tp"].sum() / df["n_z"].sum()); s["fpr_pooled"] = float(df["fp"].sum() / (1024 * len(recs) - df["n_z"].sum()))
        s["tpr_item_mean"] = float(np.nanmean(df["tp"] / np.where(df["n_z"] > 0, df["n_z"], np.nan)))
        s["precision_pooled"] = float(df["tp"].sum() / max(df["n_flag"].sum(), 1))
        s["mean_n_z"] = float(df["n_z"].mean())
        au = df["auroc_u"]; s["auroc_u_mean"] = float(np.nanmean(au)); s["auroc_u_n"] = int(np.isfinite(au).sum())
        s["mean_delta_changed"] = float(np.nanmean(df["mean_delta_z"])); s["mean_delta_unchanged"] = float(np.nanmean(df["mean_delta_notz"]))
        s["mean_clean_delta_at_changed_positions"] = float(np.nanmean(df["mean_clean_delta_at_z"]))
        s["mean_of_item_mean_none"] = float(df["mean_none"].mean()); s["mean_of_item_mean_gate"] = float(df["mean_gate"].mean()); s["mean_of_item_mean_chg"] = float(df["mean_chg"].mean())
        s["mean_sum_delta_changed"] = float(df["sum_delta_z"].mean()); s["mean_sum_delta_falseflag"] = float(df["sum_delta_fp"].mean()); s["mean_sum_delta_trueflag"] = float(df["sum_delta_tp"].mean())
        # decision-level: share of items where removing changed tokens could change the sign; margin of none-arm mean
        s["share_items_chg_differs_from_none"] = float((df["y_chg"] != df["y_none"]).mean())
        s["share_items_gate_differs_from_none"] = float((df["y_gate"] != df["y_none"]).mean())
        s["share_items_corruption_flips_clean_decision"] = float((df["y_clean_none"] != df["y_none"]).mean())
    out[name] = s

# power of the preregistered test for a PERFECT gate at the realised headroom (exact two-sided McNemar, Holm first step 0.025 / second 0.05)
def minb(alpha):
    for b in range(1, 50):
        if 2 * 0.5 ** b <= alpha: return b
out["min_b_with_c0"] = {"0.025": minb(0.025), "0.05": minb(0.05)}
res["per_condition"] = out
OUT.write_text(json.dumps(res, indent=1, default=float))
print(json.dumps(res, indent=1, default=float)[:20000])
