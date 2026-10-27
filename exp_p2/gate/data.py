"""COCO val2017 access for the gate experiments, found through `exp_p2.common` (COCO_DIR). Local files only; nothing is downloaded.

Captions: common.load_captions(). Instance annotations (categories per image, for the deranged-negative restriction and the hard negatives):
`annotations_trainval2017.zip` in COCO_DIR holds `annotations/instances_val2017.json` (20 MB); it is read straight from the zip (an extracted copy
under ann_extract/ is used if present)."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

from exp_p2 import common

INSTANCES_MEMBER = "annotations/instances_val2017.json"


def instances_paths() -> tuple[Path, Path]:
    return common.COCO_DIR / "ann_extract" / "annotations" / "instances_val2017.json", common.COCO_DIR / "annotations_trainval2017.zip"


def load_instances() -> tuple[dict[str, str], dict[int, set[str]]]:
    """Returns (category name -> supercategory, image id -> set of annotated category names). Raises FileNotFoundError if neither source exists."""
    ext, zp = instances_paths()
    if ext.exists():
        d = json.loads(ext.read_text(encoding="utf8"))
    elif zp.exists():
        with zipfile.ZipFile(zp) as z:
            d = json.loads(z.read(INSTANCES_MEMBER).decode("utf8"))
    else:
        raise FileNotFoundError(f"instances_val2017.json not found under {common.COCO_DIR}")
    cats = {int(c["id"]): c for c in d["categories"]}
    name_to_super = {c["name"]: c["supercategory"] for c in cats.values()}
    img: dict[int, set[str]] = {}
    for a in d["annotations"]:
        img.setdefault(int(a["image_id"]), set()).add(cats[int(a["category_id"])]["name"])
    return name_to_super, img


def probe_image_ids(runs: Path | None = None) -> set[int]:
    """Image ids used by probe 1 and probe 2 (excluded from every new fold, v2 7.5)."""
    runs = Path(runs) if runs is not None else Path(common.RUNS)
    out: set[int] = set()
    for rid in ("P2-PROBE-01", "P2-PROBE-02"):
        p = runs / rid / "selection.json"
        if p.exists():
            out |= {int(it["image_id"]) for it in json.loads(p.read_text(encoding="utf8"))["items"]}
    return out
