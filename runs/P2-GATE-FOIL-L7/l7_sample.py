import json, os, random, zipfile, io, collections, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SP = os.path.dirname(os.path.abspath(__file__))
C = os.path.expanduser("~/.cache/dlm_dl/coco")
W = r"C:\Users\Shlok\Downloads\Multi-Modality Language model\.claude\worktrees\frosty-clarke-209639"
# reuse functions by exec of the checker up to the audit definition (it prints a lot; silence it)
src = open(f"{SP}/l7_check.py", encoding="utf8").read().split("res = {}")[0]
exec(src)
foil_ids = set(by_img)
o = json.load(open(f"{SP}/l7_out.json"))
res = o["res"]
tp = res["test"]
fp = res["fit"]
tp_ids = [r["image_id"] for r in tp]
# fix pool order check
et = [i for i in [x["image_id"] for x in folds["test"]] if i in foil_ids and i in val_ids] if False else None
rng = random.Random(20261028)
rand_test = rng.sample(range(10, len(tp)), 10)
sample = []  # (label, record)
fm = o["out"]["first_matched"]
# L7 core
for g in ("cal", "head", "test", "test_ext", "probe"):
    i = fm[g]
    sample.append((f"L7-{g}", i))
sample.append(("L7-probe-alt(min id used by script)", 2587))
for k in range(10):
    sample.append((f"test-pool-pos{k}", tp_ids[k]))
for k in rand_test:
    sample.append((f"test-pool-rand-pos{k}", tp_ids[k]))
for k in range(5):
    sample.append((f"fit-pos{k}", fp[k]["image_id"]))
seen = set()
rows = []
for lab, i in sample:
    if i in seen:
        continue
    seen.add(i)
    first, par = pair_for(i)
    # use audit on a synthetic record
    rec = {"image_id": i, "pair_id": first["id"], "gid": -1, "file_order": first["_pos"], "c_pos": norm(first["caption"]), "c_neg": norm(par["caption"]), "excluded": None, "one_word_diff": True}
    r = audit(rec)
    r["label"] = lab
    r["in_pool_test"] = i in tp_ids
    r["in_fit"] = i in [x["image_id"] for x in fp]
    r["file_name"] = imgs[i]["file_name"]
    r["raw_orig"] = first["caption"]
    r["raw_foil"] = par["caption"]
    rows.append(r)
json.dump(rows, open(f"{SP}/l7_rows.json", "w"), indent=1, default=str)
for r in rows:
    print(r["label"], r["image_id"], r["file_name"], "pool" if r["in_pool_test"] else ("fit" if r["in_fit"] else "-"),
          "| ", r["target_word"], "->", r["foil_word"], "| swap1", r["exactly_one_swap"], "match", r["swap_matches_fields"], "same_img", r["same_image_ok"], "origCOCO", r["orig_in_coco_val2017_caps"],
          "| foilcat_present", r["foil_cat_present"], "targetcat_present", r["target_cat_present"], "| cats", dict(r["coco_cats"]))
    print("    +", r["raw_orig"]); print("    -", r["raw_foil"])
# pool-order check
elig = lambda g: [x["image_id"] for x in folds[g] if x["image_id"] in foil_ids and x["image_id"] in val_ids and x["image_id"] not in set(y["image_id"] for y in folds["cal"]) and x["image_id"] not in set(y["image_id"] for y in folds["head"])]
probe_all = set(int(it["image_id"]) for it in json.load(open(f"{W}/runs/P2-PROBE-01/selection.json"))["items"]) | set(int(it["image_id"]) for it in json.load(open(f"{W}/runs/P2-PROBE-02/selection.json"))["items"])
et = [i for i in elig("test") if i not in probe_all]
ee = [i for i in elig("test_ext") if i not in probe_all]
print("pool order == (test elig + test_ext elig)[:300]:", tp_ids == (et + ee)[:300], len(et), len(ee))
# images
zf = zipfile.ZipFile(f"{C}/val2017.zip")
from PIL import Image, ImageDraw
def sheet(items, name):
    W_, H_ = 400, 300
    cols = 3
    rowsn = (len(items) + cols - 1) // cols
    S = Image.new("RGB", (cols * W_, rowsn * H_), "white")
    for k, (idx, i) in enumerate(items):
        im = Image.open(io.BytesIO(zf.read(f"val2017/{i:012d}.jpg"))).convert("RGB")
        im.thumbnail((W_, H_ - 18))
        S.paste(im, ((k % cols) * W_, (k // cols) * H_ + 18))
        ImageDraw.Draw(S).text(((k % cols) * W_ + 4, (k // cols) * H_ + 2), f"#{idx} id={i}", fill="black")
    S.save(f"{SP}/{name}.png")
idx_of = {r["image_id"]: n for n, r in enumerate(rows)}
sheet([(idx_of[r["image_id"]], r["image_id"]) for r in rows[:6]], "sheetA")
sheet([(idx_of[r["image_id"]], r["image_id"]) for r in rows[6:12]], "sheetB")
sheet([(idx_of[r["image_id"]], r["image_id"]) for r in rows[12:18]], "sheetC")
sheet([(idx_of[r["image_id"]], r["image_id"]) for r in rows[18:24]], "sheetD")
sheet([(idx_of[r["image_id"]], r["image_id"]) for r in rows[24:]], "sheetE")
print(len(rows))

VOW=set("aeiou")
def art_mis(c):
    t=toks(c); bad=0
    for a,b in zip(t,t[1:]):
        if a=="a" and b[0] in VOW: bad+=1
        if a=="an" and b[0] not in VOW: bad+=1
    return bad
for sec in ("fit","test"):
    L=res[sec]
    n_neg=sum(1 for r in L if art_mis(r["c_neg"])>art_mis(r["c_pos"]))
    n_pos=sum(1 for r in L if art_mis(r["c_pos"])>art_mis(r["c_neg"]))
    print(sec,"article mismatch introduced in foil:",n_neg,"in original:",n_pos,"of",len(L))
