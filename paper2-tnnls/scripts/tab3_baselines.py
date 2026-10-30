"""Table III (reference baselines CLIP ViT-L/14 and SigLIP so400m; descriptive; A6.6: own table, no test, no comparison word, no column of LRF numbers).
Sources: runs/P2-LRF-BASELINES/baselines.json (table.{clip,siglip}.<condition>.{acc,n,drop,drop_ci95}), and the pixel-parity minima of
runs/P2-LRF-BASELINES-PARITY-L1/baselines.json and runs/P2-LRF-BASELINES-PARITY-LG/baselines.json (pixel_parity.{min,ok,threshold}).
Output: paper2-tnnls/tables/tab3_baselines.tex. Nothing is bold or underlined: no test, no ranking."""
from __future__ import annotations

import json

import figstyle as S
from tablib import iv, num, row, write

B = S.jload("P2-LRF-BASELINES/baselines.json")
PL1 = S.jload("P2-LRF-BASELINES-PARITY-L1/baselines.json")
PLG = S.jload("P2-LRF-BASELINES-PARITY-LG/baselines.json")
assert B["n_items"] == 450 and PL1["pixel_parity"]["ok"] is True and PLG["pixel_parity"]["ok"] is True
assert B["models"]["clip"]["id"] == "openai/clip-vit-large-patch14" and B["models"]["siglip"]["id"] == "google/siglip-so400m-patch14-384"
F = "runs/P2-LRF-BASELINES/baselines.json"
assert isinstance(B["pixel_parity"], str) and B["pixel_parity"].startswith("not run")     # stale field of the main run; superseded by the two PARITY runs

# clean accuracy of each model on the SAME first 300 items as the three severity-3 cells (computed from predictions.jsonl into runs/P2-PAPER-TABLES/)
PRED = S.RUNS / "P2-LRF-BASELINES" / "predictions.jsonl"
prow = [json.loads(l) for l in open(PRED, encoding="utf-8")]
lg_idx = {m: set(r["idx"] for r in prow if r["model"] == m and r["condition"] == "shot_noise3") for m in ("clip", "siglip")}
for m in lg_idx:
    for c in ("impulse_noise3", "speckle_noise3"):
        assert lg_idx[m] == set(r["idx"] for r in prow if r["model"] == m and r["condition"] == c)
clean300 = {}
for m in ("clip", "siglip"):
    ys = [r["y"] for r in prow if r["model"] == m and r["condition"] == "clean" and r["idx"] in lg_idx[m]]
    clean300[m] = dict(n=len(ys), k=int(sum(ys)), acc=sum(ys) / len(ys), items=f"idx {min(lg_idx[m])}..{max(lg_idx[m])}")
    assert clean300[m]["n"] == 300 == B["table"][m]["shot_noise3"]["n"]
OUTT = S.RUNS / "P2-PAPER-TABLES"
OUTT.mkdir(exist_ok=True)
json.dump(dict(label="added at writing, descriptive; clean accuracy on the same items as the LG cells", source="runs/P2-LRF-BASELINES/predictions.jsonl",
               source_sha256=S.sha256(PRED), script="paper2-tnnls/scripts/tab3_baselines.py", script_sha256=S.sha256(S.HERE / "tab3_baselines.py"), models=clean300),
          open(OUTT / "baselines_clean300.json", "w", encoding="utf-8"), indent=1)
C300 = "runs/P2-PAPER-TABLES/baselines_clean300.json models.{clip,siglip}.{n,acc}"
ORDER = [("clean", "Clean images"), ("noise0.1", r"Gaussian noise, $\sigma=0.1$"), ("jpeg10", "JPEG, quality 10"), ("splice128", "Splice, 128 px"),
         ("shot_noise3", "Shot noise, severity 3"), ("impulse_noise3", "Impulse noise, severity 3"), ("speckle_noise3", "Speckle noise, severity 3")]


def acc(x):
    return f"{x:.3f}"


def drop(r):
    return "--" if "drop" not in r else f"{num(r['drop'])} {iv(*r['drop_ci95'])}"


def block(keys, first=None):
    out = []
    if first:
        out.append(row([r"Clean images, same 300 items", "300", acc(clean300["clip"]["acc"]), "--", acc(clean300["siglip"]["acc"]), "--"], [C300]))
    for k, nm in keys:
        c, s = B["table"]["clip"][k], B["table"]["siglip"][k]
        assert c["n"] == s["n"]
        out.append(row([nm, str(c["n"]), acc(c["acc"]), drop(c), acc(s["acc"]), drop(s)],
                       [f"{F} table.clip.{k}.{{n,acc,drop,drop_ci95}}; table.siglip.{k}.{{acc,drop,drop_ci95}}"]))
    return out


pp = []
for lab, d, path in (("the four conditions of the top block", PL1, "runs/P2-LRF-BASELINES-PARITY-L1/baselines.json"),
                     ("clean and three severity-3 conditions", PLG, "runs/P2-LRF-BASELINES-PARITY-LG/baselines.json")):
    q = d["pixel_parity"]
    pp.append(row([r"\multicolumn{6}{l}{" + f"Pixel parity, {d['n_items']} items, {lab}: minimum token agreement {q['min']:.3f} (threshold {q['threshold']:.2f})" + "}"],
                  [f"{path} pixel_parity.{{min,threshold,ok}}, n_items"]))

cost = [row([r"Cost per item", "--", r"\multicolumn{4}{l}{not measured (no timing in any committed baseline run)}"], ["runs/P2-LRF-BASELINES/baselines.json holds no timing; runs/P2-LRF-BASELINES.stdout.txt and .stderr.txt hold none"])]

write("tab3_baselines.tex", "@{}lrcccc@{}",
      ["Condition", "$n$", "CLIP acc.", "CLIP drop (95\\% interval)", "SigLIP acc.", "SigLIP drop (95\\% interval)"],
      [block(ORDER[:4]), block(ORDER[4:], first=True), cost, pp],
      preamble=["drop: clean minus corrupted accuracy of the same model on the same items (paired percentile bootstrap, 95% interval, from baselines.json)",
                "no test, no ranking, no LRF number in this table (A6.6); nothing bold",
                "stale field: runs/P2-LRF-BASELINES/baselines.json pixel_parity says 'not run' because the main run was made without --parity; the parity runs P2-LRF-BASELINES-PARITY-L1 and -LG supersede it",
                "models: openai/clip-vit-large-patch14 rev 32bd6428..., google/siglip-so400m-patch14-384 rev 9fdffc58... (runs/P2-LRF-BASELINES/baselines.json models.*)"])
