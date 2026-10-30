import json, sys
import numpy as np
from pathlib import Path
run = Path(sys.argv[1]) / "runs/P2-GATE-M4"
R = [json.loads(l) for l in open(run / "items.jsonl", encoding="utf8")]
for name in ("patch", "swap"):
    print("==", name)
    flipped = []; margins = []
    for r in R:
        c = r["conds"]; im = c[name]["img"]; cl = c["clean"]["img"]["none"]
        margins.append(cl["mean"])
        if cl["y"] != im["none"]["y"] or im["none"]["y"] != im["gate0.05"]["y"] or im["none"]["y"] != im["chg"]["y"]:
            a = np.load(run / "arrays" / f"item{r['idx']:04d}.npz")
            z = a[f"{name}_z"]; G = a[f"{name}_flag0.05"]
            print(r["idx"], "clean_y", cl["y"], "clean_mean %.4f" % cl["mean"], "| none y", im["none"]["y"], "mean %.4f" % im["none"]["mean"],
                  "| gate y", im["gate0.05"]["y"], "mean %.4f n %d" % (im["gate0.05"]["mean"], im["gate0.05"]["n"]),
                  "| chg y", im["chg"]["y"], "mean %.4f" % im["chg"]["mean"], "| tp %d/%d fp %d" % ((G & z).sum(), z.sum(), (G & ~z).sum()))
    m = np.abs(np.array(margins))
    print("clean none-arm |mean| quantiles 5/10/25/50%:", np.round(np.quantile(m, [.05, .1, .25, .5]), 4))
    # shift of the item mean caused by the corruption (none arm) vs clean
    sh = np.array([r["conds"][name]["img"]["none"]["mean"] - r["conds"]["clean"]["img"]["none"]["mean"] for r in R])
    print("corruption shift of item mean (none - clean): mean %.4f sd %.4f q05 %.4f q95 %.4f" % (sh.mean(), sh.std(), *np.quantile(sh, [.05, .95])))
    print("share items with |clean mean| < |shift|:", float(np.mean(m < np.abs(sh))))
