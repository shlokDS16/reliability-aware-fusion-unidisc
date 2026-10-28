import json, hashlib, os, zipfile, re, sys, collections
W = r"C:\Users\Shlok\Downloads\Multi-Modality Language model\.claude\worktrees\frosty-clarke-209639"
C = os.path.expanduser("~/.cache/dlm_dl/coco")
SP = os.path.dirname(os.path.abspath(__file__))
out = {}
raw = open(f"{C}/foil/foilv1.0_test_2017.json", "rb").read()
out["foil_sha256"] = hashlib.sha256(raw).hexdigest()
d = json.loads(raw)
imgs = {im["id"]: im for im in d["images"]}
by_img = collections.OrderedDict()
by_id = collections.defaultdict(list)
for pos, a in enumerate(d["annotations"]):
    a["_pos"] = pos
    by_img.setdefault(a["image_id"], []).append(a)
    by_id[a["id"]].append(a)
bad = 0
for k, v in by_id.items():
    if len(v) != 2 or sorted(x["foil"] for x in v) != [False, True] or v[0]["image_id"] != v[1]["image_id"]:
        bad += 1
out["n_ids"] = len(by_id)
out["n_ids_bad_pairing"] = bad
out["n_filename_mismatch"] = sum(1 for i, im in imgs.items() if int(re.search(r"(\d+)\.jpg$", im["file_name"]).group(1)) != i)
# foil_id uniqueness (the earlier steward note looked at foil_id)
fid = collections.Counter(a["foil_id"] for a in d["annotations"])
out["n_foil_id_unique"] = len(fid)
out["n_foil_id_repeated"] = sum(1 for v in fid.values() if v > 1)


def norm(s):
    return " ".join(str(s).lower().split())


def toks(s):
    return re.findall(r"[a-z0-9']+", norm(s))


def pair_for(img):
    first = by_img[img][0]
    partner = [x for x in by_id[first["id"]] if x["foil"]][0]
    return first, partner


caps = json.load(open(f"{C}/ann_extract/annotations/captions_val2017.json"))
cap_by_img = collections.defaultdict(list)
for a in caps["annotations"]:
    cap_by_img[a["image_id"]].append(norm(a["caption"]))
val_ids = {im["id"] for im in caps["images"]}
inst = json.loads(zipfile.ZipFile(f"{C}/annotations_trainval2017.zip").read("annotations/instances_val2017.json"))
cats = {c["id"]: c["name"] for c in inst["categories"]}
img_cats = collections.defaultdict(collections.Counter)
for a in inst["annotations"]:
    img_cats[a["image_id"]][cats[a["category_id"]]] += 1
out["n_inst_images_with_ann"] = len(img_cats)

SYN = {"bike": {"bicycle"}, "television": {"tv"}, "plane": {"airplane"}, "man": {"person"}, "woman": {"person"},
       "men": {"person"}, "women": {"person"}, "people": {"person"}, "boy": {"person"}, "girl": {"person"},
       "child": {"person"}, "phone": {"cell phone"}, "doughnut": {"donut"}, "sofa": {"couch"}, "motorbike": {"motorcycle"}}


def wc(w):
    w = w.lower()
    res = set()
    forms = {w, w + "s", w + "es"}
    if w.endswith("s"):
        forms.add(w[:-1])
    for n in cats.values():
        if n in forms or any(p in forms for p in n.split()):
            res.add(n)
    res |= SYN.get(w, set())
    return res


pool = json.load(open(f"{W}/runs/P2-GATE-FOIL/pool.json"))
folds = json.load(open(f"{W}/runs/P2-GATE-FOLDS/folds.json"))


def audit(rec):
    img = rec["image_id"]
    first, par = pair_for(img)
    r = {"image_id": img, "pair_id": rec["pair_id"], "gid": rec["gid"]}
    r["pair_id_ok"] = (first["id"] == rec["pair_id"] == par["id"])
    r["same_image_ok"] = (first["image_id"] == par["image_id"] == img) and (img in imgs)
    r["first_record_is_orig"] = (not first["foil"]) and first["target_word"] == "ORIG"
    r["file_order_ok"] = (first["_pos"] == rec["file_order"]) or (rec["file_order"] in (first["_pos"], first["_pos"] // 2))
    r["file_order_raw"] = (first["_pos"], rec["file_order"])
    cp, cn = norm(first["caption"]), norm(par["caption"])
    r["pool_caps_match_raw"] = (cp == rec["c_pos"] and cn == rec["c_neg"])
    tp, tn = toks(cp), toks(cn)
    r["orig_in_coco_val2017_caps"] = cp in cap_by_img.get(img, [])
    diffs = [i for i in range(len(tp)) if tp[i] != tn[i]] if len(tp) == len(tn) else None
    r["n_diff_positions"] = None if diffs is None else len(diffs)
    r["exactly_one_swap"] = (diffs is not None and len(diffs) == 1)
    r["swap_matches_fields"] = bool(r["exactly_one_swap"] and tp[diffs[0]] == par["target_word"].lower() and tn[diffs[0]] == par["foil_word"].lower())
    r["target_word"], r["foil_word"] = par["target_word"], par["foil_word"]
    r["foil_flags"] = (par["foil"] is True and not first["foil"])
    r["foil_ne_target"] = par["foil_word"].lower() != par["target_word"].lower()
    cs = img_cats.get(img, collections.Counter())
    r["coco_cats"] = dict(cs)
    fc, tc = wc(par["foil_word"]), wc(par["target_word"])
    r["foil_cats"], r["target_cats"] = sorted(fc), sorted(tc)
    r["foil_mapped"] = bool(fc)
    r["target_mapped"] = bool(tc)
    r["foil_cat_present"] = bool(fc & set(cs))
    r["target_cat_present"] = bool(tc & set(cs))
    r["c_pos"], r["c_neg"] = cp, cn
    r["excluded"] = rec.get("excluded")
    r["one_word_diff_flag"] = rec.get("one_word_diff")
    return r


res = {}
keys = ("pair_id_ok", "same_image_ok", "first_record_is_orig", "file_order_ok", "pool_caps_match_raw", "orig_in_coco_val2017_caps",
        "exactly_one_swap", "swap_matches_fields", "foil_flags", "foil_ne_target", "foil_mapped", "target_mapped",
        "foil_cat_present", "target_cat_present")
for sec in ("fit", "test"):
    res[sec] = [audit(p) for p in pool[sec]]
    L = res[sec]
    out[sec] = {"n": len(L)}
    for k in keys:
        out[sec][k] = sum(1 for r in L if r[k])
    out[sec]["not_exactly_one_swap"] = [(r["image_id"], r["c_pos"], r["c_neg"]) for r in L if not r["exactly_one_swap"]]
    out[sec]["foil_cat_present_cases"] = [(r["image_id"], r["foil_word"], r["foil_cats"], r["coco_cats"]) for r in L if r["foil_cat_present"]]
    out[sec]["foil_unmapped"] = sorted({r["foil_word"] for r in L if not r["foil_mapped"]})
    out[sec]["target_unmapped"] = sorted({r["target_word"] for r in L if not r["target_mapped"]})
    out[sec]["target_mapped_but_absent"] = [(r["image_id"], r["target_word"], r["target_cats"], r["coco_cats"]) for r in L if r["target_mapped"] and not r["target_cat_present"]]
    out[sec]["n_pool_flag_not_one_word"] = sum(1 for p in pool[sec] if not p.get("one_word_diff"))
    out[sec]["n_excluded_marked"] = sum(1 for p in pool[sec] if p.get("excluded"))
    out[sec]["file_order_raw_first5"] = [r["file_order_raw"] for r in L[:5]]

ids = lambda k: [x["image_id"] for x in folds[k]]
foil_ids = set(by_img)
p1 = [int(it["image_id"]) for it in json.load(open(f"{W}/runs/P2-PROBE-01/selection.json"))["items"]]
p2 = [int(it["image_id"]) for it in json.load(open(f"{W}/runs/P2-PROBE-02/selection.json"))["items"]]  # ids only
probe_all = set(p1) | set(p2)
out["probe_ids_total"] = len(probe_all)
fm = {}
for g in ("cal", "head", "test", "test_ext"):
    fm[g] = next(i for i in ids(g) if i in foil_ids)
fm["probe"] = next(i for i in p1 if i in foil_ids)
out["first_matched"] = fm
mc = {g: sum(1 for i in ids(g) if i in foil_ids) for g in ("cal", "head", "test", "test_ext")}
mc["probe"] = len(probe_all & foil_ids)
out["matched_counts"] = mc
fold_sets = {g: set(ids(g)) for g in ("cal", "head", "test", "test_ext")}
tp_ids = [p["image_id"] for p in pool["test"]]
fp_ids = [p["image_id"] for p in pool["fit"]]
out["test_pool_n"] = len(tp_ids)
out["test_pool_unique"] = len(set(tp_ids))
out["fit_pool_unique"] = len(set(fp_ids))
out["test_in_cal"] = len(set(tp_ids) & fold_sets["cal"])
out["test_in_head"] = len(set(tp_ids) & fold_sets["head"])
out["test_in_probe"] = len(set(tp_ids) & probe_all)
out["test_in_foldtest"] = len(set(tp_ids) & fold_sets["test"])
out["test_in_foldtestext"] = len(set(tp_ids) & fold_sets["test_ext"])
out["test_in_val2017"] = len(set(tp_ids) & val_ids)
out["fit_in_val2017"] = len(set(fp_ids) & val_ids)
out["fit_subset_of_cal"] = set(fp_ids) <= fold_sets["cal"]
out["fit_test_disjoint"] = not (set(fp_ids) & set(tp_ids))
out["fit_in_head_or_probe"] = len(set(fp_ids) & (fold_sets["head"] | probe_all))
ok = lambda i: i in foil_ids and i in val_ids and i not in fold_sets["cal"] and i not in fold_sets["head"] and i not in probe_all
et = [i for i in ids("test") if ok(i)]
ee = [i for i in ids("test_ext") if ok(i)]
out["elig_test"], out["elig_ext"] = len(et), len(ee)
out["pool_prefix_is_test_then_ext_order"] = tp_ids[:len(et) + len(ee)] == et + ee
out["pool_first_n_eq_elig_test_order"] = tp_ids[:len(et)] == et
out["first150_in_P_test_list"] = all(i in fold_sets["test"] or i in fold_sets["test_ext"] for i in tp_ids[:150])
out["all_in_P_test_list"] = all(i in fold_sets["test"] or i in fold_sets["test_ext"] for i in tp_ids)
out["first_record_orig_all_images"] = all(not v[0]["foil"] for v in by_img.values())
json.dump({"out": out, "res": res}, open(f"{SP}/l7_out.json", "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str)[:9000])
