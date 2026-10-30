"""Hard-negative builder (v2 Alg. 11): captions that are WRONG BY CONSTRUCTION for their image.

For an image with annotated COCO categories A and five reference captions: find in the scored caption a noun (via the fixed synonym table below,
written once before use) that maps to a category in A; replace it by a category name from the SAME supercategory that is (a) not annotated in the
image and (b) not mentioned in any of the five reference captions. Number (singular or plural) is kept by the table's singular and plural display
forms; a directly preceding a/an is re-chosen from the new word. Eligible nouns: the leftmost matched word whose category has such an alternative
(fixed rule). Items where nothing qualifies are skipped and counted by reason (notably any caption whose only annotated noun is 'person': that
supercategory has a single member).
The audit (step 4) is a separate reviewer pass: `audit_sheet` writes the items, `apply_audit` drops those judged correct or unsure and reports the
false-negative rate with a Wilson interval. Ambiguous words ('orange', 'plant', 'bag', 'bat') are deliberately absent from the table.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import numpy as np

# name: (singular display, plural display, singular synonyms, plural synonyms)   all lower case
CATS: dict[str, tuple[str, str, list[str], list[str]]] = {
    "person": ("person", "people", ["person", "man", "woman", "boy", "girl", "child", "kid", "player", "lady", "guy", "baby", "toddler", "skier", "surfer", "skateboarder", "snowboarder", "gentleman"],
               ["people", "men", "women", "boys", "girls", "children", "kids", "players", "ladies", "guys", "babies", "toddlers", "skiers", "surfers", "skateboarders", "snowboarders", "gentlemen"]),
    "bicycle": ("bicycle", "bicycles", ["bicycle", "bike"], ["bicycles", "bikes"]),
    "car": ("car", "cars", ["car", "sedan", "taxi"], ["cars", "sedans", "taxis"]),
    "motorcycle": ("motorcycle", "motorcycles", ["motorcycle", "motorbike"], ["motorcycles", "motorbikes"]),
    "airplane": ("airplane", "airplanes", ["airplane", "plane", "jet", "aircraft", "airliner"], ["airplanes", "planes", "jets", "airliners"]),
    "bus": ("bus", "buses", ["bus"], ["buses"]),
    "train": ("train", "trains", ["train", "locomotive"], ["trains", "locomotives"]),
    "truck": ("truck", "trucks", ["truck"], ["trucks"]),
    "boat": ("boat", "boats", ["boat", "ship", "sailboat"], ["boats", "ships", "sailboats"]),
    "traffic light": ("traffic light", "traffic lights", ["traffic light", "stoplight", "traffic signal"], ["traffic lights", "stoplights", "traffic signals"]),
    "fire hydrant": ("fire hydrant", "fire hydrants", ["fire hydrant", "hydrant"], ["fire hydrants", "hydrants"]),
    "stop sign": ("stop sign", "stop signs", ["stop sign"], ["stop signs"]),
    "parking meter": ("parking meter", "parking meters", ["parking meter"], ["parking meters"]),
    "bench": ("bench", "benches", ["bench"], ["benches"]),
    "bird": ("bird", "birds", ["bird", "seagull", "duck", "pigeon", "parrot", "owl", "goose"], ["birds", "seagulls", "ducks", "pigeons", "parrots", "owls", "geese"]),
    "cat": ("cat", "cats", ["cat", "kitten", "kitty"], ["cats", "kittens"]),
    "dog": ("dog", "dogs", ["dog", "puppy"], ["dogs", "puppies"]),
    "horse": ("horse", "horses", ["horse", "pony"], ["horses", "ponies"]),
    "sheep": ("sheep", "sheep", ["sheep", "lamb"], ["lambs"]),
    "cow": ("cow", "cows", ["cow", "bull", "calf"], ["cows", "cattle", "bulls", "calves"]),
    "elephant": ("elephant", "elephants", ["elephant"], ["elephants"]),
    "bear": ("bear", "bears", ["bear"], ["bears"]),
    "zebra": ("zebra", "zebras", ["zebra"], ["zebras"]),
    "giraffe": ("giraffe", "giraffes", ["giraffe"], ["giraffes"]),
    "backpack": ("backpack", "backpacks", ["backpack"], ["backpacks"]),
    "umbrella": ("umbrella", "umbrellas", ["umbrella"], ["umbrellas"]),
    "handbag": ("handbag", "handbags", ["handbag", "purse"], ["handbags", "purses"]),
    "tie": ("tie", "ties", ["tie", "necktie"], ["ties", "neckties"]),
    "suitcase": ("suitcase", "suitcases", ["suitcase", "luggage"], ["suitcases"]),
    "frisbee": ("frisbee", "frisbees", ["frisbee"], ["frisbees"]),
    "skis": ("pair of skis", "pairs of skis", ["ski"], ["skis"]),
    "snowboard": ("snowboard", "snowboards", ["snowboard"], ["snowboards"]),
    "sports ball": ("ball", "balls", ["ball", "soccer ball", "tennis ball"], ["balls", "soccer balls", "tennis balls"]),
    "kite": ("kite", "kites", ["kite"], ["kites"]),
    "baseball bat": ("baseball bat", "baseball bats", ["baseball bat"], ["baseball bats"]),
    "baseball glove": ("baseball glove", "baseball gloves", ["baseball glove", "mitt", "glove"], ["baseball gloves", "mitts", "gloves"]),
    "skateboard": ("skateboard", "skateboards", ["skateboard"], ["skateboards"]),
    "surfboard": ("surfboard", "surfboards", ["surfboard", "surf board"], ["surfboards", "surf boards"]),
    "tennis racket": ("tennis racket", "tennis rackets", ["tennis racket", "racket", "racquet", "tennis racquet"], ["tennis rackets", "rackets", "racquets"]),
    "bottle": ("bottle", "bottles", ["bottle"], ["bottles"]),
    "wine glass": ("wine glass", "wine glasses", ["wine glass"], ["wine glasses"]),
    "cup": ("cup", "cups", ["cup", "mug"], ["cups", "mugs"]),
    "fork": ("fork", "forks", ["fork"], ["forks"]),
    "knife": ("knife", "knives", ["knife"], ["knives"]),
    "spoon": ("spoon", "spoons", ["spoon"], ["spoons"]),
    "bowl": ("bowl", "bowls", ["bowl"], ["bowls"]),
    "banana": ("banana", "bananas", ["banana"], ["bananas"]),
    "apple": ("apple", "apples", ["apple"], ["apples"]),
    "sandwich": ("sandwich", "sandwiches", ["sandwich"], ["sandwiches"]),
    "orange": ("orange", "oranges", [], ["oranges"]),                      # singular 'orange' is a colour as often as a fruit: not matched
    "broccoli": ("broccoli", "broccoli", ["broccoli"], []),
    "carrot": ("carrot", "carrots", ["carrot"], ["carrots"]),
    "hot dog": ("hot dog", "hot dogs", ["hot dog"], ["hot dogs"]),
    "pizza": ("pizza", "pizzas", ["pizza"], ["pizzas"]),
    "donut": ("donut", "donuts", ["donut", "doughnut"], ["donuts", "doughnuts"]),
    "cake": ("cake", "cakes", ["cake", "cupcake"], ["cakes", "cupcakes"]),
    "chair": ("chair", "chairs", ["chair"], ["chairs"]),
    "couch": ("couch", "couches", ["couch", "sofa"], ["couches", "sofas"]),
    "potted plant": ("potted plant", "potted plants", ["potted plant", "houseplant"], ["potted plants", "houseplants"]),
    "bed": ("bed", "beds", ["bed"], ["beds"]),
    "dining table": ("table", "tables", ["table", "dining table"], ["tables", "dining tables"]),
    "toilet": ("toilet", "toilets", ["toilet"], ["toilets"]),
    "tv": ("television", "televisions", ["tv", "television"], ["tvs", "televisions"]),
    "laptop": ("laptop", "laptops", ["laptop"], ["laptops"]),
    "mouse": ("computer mouse", "computer mice", ["mouse"], ["mice"]),
    "remote": ("remote control", "remote controls", ["remote", "remote control"], ["remotes", "remote controls"]),
    "keyboard": ("keyboard", "keyboards", ["keyboard"], ["keyboards"]),
    "cell phone": ("phone", "phones", ["cell phone", "cellphone", "phone", "smartphone", "mobile phone"], ["cell phones", "cellphones", "phones", "smartphones", "mobile phones"]),
    "microwave": ("microwave", "microwaves", ["microwave"], ["microwaves"]),
    "oven": ("oven", "ovens", ["oven"], ["ovens"]),
    "toaster": ("toaster", "toasters", ["toaster"], ["toasters"]),
    "sink": ("sink", "sinks", ["sink"], ["sinks"]),
    "refrigerator": ("refrigerator", "refrigerators", ["refrigerator", "fridge"], ["refrigerators", "fridges"]),
    "book": ("book", "books", ["book"], ["books"]),
    "clock": ("clock", "clocks", ["clock"], ["clocks"]),
    "vase": ("vase", "vases", ["vase"], ["vases"]),
    "scissors": ("pair of scissors", "pairs of scissors", ["scissors"], []),
    "teddy bear": ("teddy bear", "teddy bears", ["teddy bear", "teddy"], ["teddy bears"]),
    "hair drier": ("hair dryer", "hair dryers", ["hair drier", "hair dryer", "blow dryer"], ["hair driers", "hair dryers"]),
    "toothbrush": ("toothbrush", "toothbrushes", ["toothbrush"], ["toothbrushes"]),
}

_SURFACE: dict[str, tuple[str, bool]] = {}          # phrase -> (category, is_plural)
for _c, (_s, _p, _ss, _ps) in CATS.items():
    for _w in _ss:
        _SURFACE.setdefault(_w, (_c, False))
    for _w in _ps:
        _SURFACE.setdefault(_w, (_c, True))
_MAX_PHRASE = max(len(k.split()) for k in _SURFACE)
_TOKEN = re.compile(r"[A-Za-z']+|[^A-Za-z']+")


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall(text)


def find_matches(text: str) -> list[dict]:
    """Left-to-right, longest-phrase-first matches of the synonym table. Each: dict(cat, plural, start, end) in token-list indices (inclusive start, exclusive end)."""
    toks = _tokens(text)
    word_idx = [i for i, t in enumerate(toks) if re.fullmatch(r"[A-Za-z']+", t)]
    out, k = [], 0
    while k < len(word_idx):
        hit = None
        for L in range(min(_MAX_PHRASE, len(word_idx) - k), 0, -1):
            idxs = word_idx[k:k + L]
            if any(toks[idxs[a + 1] - 1:idxs[a + 1]] != [" "] for a in range(L - 1)):         # phrase words must be separated by exactly one space
                continue
            phrase = " ".join(toks[i].lower() for i in idxs)
            if phrase in _SURFACE:
                c, pl = _SURFACE[phrase]
                hit = dict(cat=c, plural=pl, start=idxs[0], end=idxs[-1] + 1, phrase=phrase, nwords=L)
                break
        if hit:
            out.append(hit)
            k += hit["nwords"]
        else:
            k += 1
    return out


def mentioned_categories(captions: list[str]) -> set[str]:
    s: set[str] = set()
    for c in captions:
        s |= {m["cat"] for m in find_matches(c)}
    return s


def _article(prev_word: str, new_np: str) -> str:
    a = "an" if new_np[:1].lower() in "aeiou" else "a"
    return a.capitalize() if prev_word[:1].isupper() else a


def build_one(caption: str, annotated: set[str], ref_captions: list[str], cat_to_super: dict[str, str], rng: np.random.Generator) -> dict:
    """Returns dict(ok=True, negative, old_cat, new_cat, replaced) or dict(ok=False, reason)."""
    matches = find_matches(caption)
    if not matches:
        return dict(ok=False, reason="no_known_noun")
    in_img = [m for m in matches if m["cat"] in annotated]
    if not in_img:
        return dict(ok=False, reason="noun_not_annotated")
    mentioned = mentioned_categories(ref_captions) | mentioned_categories([caption])
    for m in in_img:                                                           # leftmost eligible
        sup = cat_to_super.get(m["cat"])
        if sup is None:
            continue
        alts = sorted(c for c in CATS if cat_to_super.get(c) == sup and c != m["cat"] and c not in annotated and c not in mentioned)
        if not alts:
            continue
        new = alts[int(rng.integers(0, len(alts)))]
        new_np = CATS[new][1] if m["plural"] else CATS[new][0]
        toks = _tokens(caption)
        old = "".join(toks[m["start"]:m["end"]])
        out = toks[:m["start"]] + [new_np] + toks[m["end"]:]
        j = m["start"] - 2                                                     # token before the single space before the noun
        if j >= 0 and toks[m["start"] - 1] == " " and toks[j].lower() in ("a", "an") and not m["plural"]:
            out[j] = _article(toks[j], new_np)
        return dict(ok=True, negative="".join(out), old_cat=m["cat"], new_cat=new, replaced=old)
    return dict(ok=False, reason="no_same_supercategory_alternative")


def build_hard_negatives(items: list[dict], image_cats: dict[int, set[str]], ref_captions: dict[int, list[str]], cat_to_super: dict[str, str], *, seed: int) -> tuple[list[dict], Counter]:
    """items: fold items (gid, image_id, caption). Returns (records for kept items, Counter of skip reasons)."""
    recs, skipped = [], Counter()
    for it in items:
        r = build_one(it["caption"], image_cats.get(it["image_id"], set()), ref_captions.get(it["image_id"], []), cat_to_super,
                      np.random.default_rng([seed, it["gid"], 11]))
        if r["ok"]:
            recs.append(dict(gid=it["gid"], idx=it["idx"], image_id=it["image_id"], caption=it["caption"], **{k: r[k] for k in ("negative", "old_cat", "new_cat", "replaced")}))
        else:
            skipped[r["reason"]] += 1
    return recs, skipped


# ------------------------------------------------------------------------------------------------ audit (step 4)
def audit_sheet(recs: list[dict], path: Path) -> None:
    """One JSON line per hard negative for the reviewer: id, image, the caption to judge. The reviewer answers 'incorrect' (a valid hard negative),
    'correct' or 'unsure' for each id; nothing else about how the negative was made is shown."""
    with open(path, "w", encoding="utf8") as fh:
        for r in recs:
            fh.write(json.dumps(dict(gid=r["gid"], image_id=r["image_id"], caption=r["negative"])) + "\n")


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return float(max(0.0, c - h)), float(min(1.0, c + h))


def apply_audit(recs: list[dict], verdicts: dict[int, str]) -> dict:
    """Keep only negatives judged 'incorrect' (i.e. not valid descriptions). Items judged 'correct' or 'unsure' (or missing) are dropped and counted;
    the false-negative rate (negatives that are in fact correct descriptions) is reported with a Wilson interval."""
    kept, n_correct, n_unsure, n_missing = [], 0, 0, 0
    for r in recs:
        v = verdicts.get(r["gid"])
        if v == "incorrect":
            kept.append(r)
        elif v == "correct":
            n_correct += 1
        elif v == "unsure":
            n_unsure += 1
        else:
            n_missing += 1
    n_j = len(recs) - n_missing
    lo, hi = wilson(n_correct, n_j)
    return dict(kept=kept, n_input=len(recs), n_kept=len(kept), n_judged_correct=n_correct, n_unsure=n_unsure, n_missing=n_missing,
                false_negative_rate=(n_correct / n_j if n_j else float("nan")), false_negative_ci95=[lo, hi])
