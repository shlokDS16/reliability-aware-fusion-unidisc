"""Builds research/review/extraction/extraction-schema-v0.4.json from v0.3 by the edits of EXTRACTION-PLAN-v0.4 s4
(deterministic; v0.3 is read, never written). Each edit names its red-team finding (audit 3, 2026-10-20).
Run: python -E -P analysis/extraction/make_schema_v04.py   (checks the result with jsonschema Draft 2020-12 when
importable and prints the sha256 of the output).
"""
import hashlib
import json
from pathlib import Path

SRC = Path("research/review/extraction/extraction-schema-v0.3.json")
DST = Path("research/review/extraction/extraction-schema-v0.4.json")
s = json.loads(SRC.read_text(encoding="utf-8"))
D = s["$defs"]


def find(node, key):
    """All dicts under node that have property `key` in their 'properties'."""
    out = []
    if isinstance(node, dict):
        if key in node.get("properties", {}):
            out.append(node["properties"][key])
        for v in node.values():
            out += find(v, key)
    elif isinstance(node, list):
        for v in node:
            out += find(v, key)
    return out


s["$id"] = "dlm-review/extraction-schema-v0.4.json"
s["title"] = "Paper 1 extraction record, form v0.4 (draft, not frozen)"
s["description"] = s["description"].replace("EXTRACTION-PLAN-v0.3.md", "EXTRACTION-PLAN-v0.4.md") + (
    " v0.4: anchor_rule gains 'full-configuration' (U3); examples in descriptions are synthetic.")

# form_version: v0.3 schema still carried const "0.2" (found while building v0.4)
s["properties"]["form_version"]["const"] = "0.4"

# M3: U3 clause for removal groups
ar = find(s, "anchor_rule")
assert len(ar) == 1, len(ar)
ar[0]["enum"] = ["focal-label", "other-own-model", "stated-default", "value-identity", "full-configuration",
                 "first-own-arm", "none"]
ar[0]["description"] = "which clause of U3 gave the anchor ('none' when anchor_arm is null)"

# M4: no example taken from a paper that can be drawn (descriptions are seen by every session)
f = find(s, "focal_config")
assert len(f) == 1
f[0]["description"] = ("U2e: the focal configuration's arm label as printed in the main-results table, with its "
                       "where (synthetic example: 'Table 2: Ours-L (k=4)')")
c = find(D, "cells")
assert len(c) == 1, len(c)
c[0]["description"] = c[0]["description"].replace("'Discrete Diff.'", "'Hybrid scan'")
lv = find(s, "level_printed")
assert len(lv) == 1, len(lv)
lv[0]["description"] = ("the factor value of this arm as printed (synthetic examples: '96', 'w/o planner', "
                        "'Base-Q 3B')")

# m7: shape only from prose
sh = find(s, "shape")
assert len(sh) == 1, len(sh)
sh[0]["description"] = ("figure-only group: the trend on the primary metric as a sentence of the text or the "
                        "caption states it (U10); 'unclear' when no sentence states it; NA for table groups")

out = json.dumps(s, ensure_ascii=False, indent=1)
for bad in ("FDM (K=2)", "Discrete Diff.", "w/o remasking", "LLaMA-3 8B", '"0.2"'):
    assert bad not in out, bad
DST.write_text(out + "\n", encoding="utf-8", newline="\n")
print("written", DST, "sha256", hashlib.sha256(DST.read_bytes()).hexdigest())
try:
    import jsonschema
    jsonschema.Draft202012Validator.check_schema(s)
    print("jsonschema Draft 2020-12 check_schema: ok")
except ImportError:
    print("jsonschema not importable: schema not checked")
