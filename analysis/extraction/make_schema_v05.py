"""Builds research/review/extraction/extraction-schema-v0.5.json from v0.4 by the edits of EXTRACTION-PLAN-v0.5 s4
(deterministic; v0.4 is read, never written). Red-team audit 4, MA2: the fields that gate criteria measure get
descriptions that point to the brief's attribute rules KA1-KA4. No field is added or removed (153).
Run: python -E -P analysis/extraction/make_schema_v05.py   (checks the result with jsonschema Draft 2020-12 when
importable and prints the sha256 of the output).
"""
import hashlib
import json
from pathlib import Path

SRC = Path("research/review/extraction/extraction-schema-v0.4.json")
DST = Path("research/review/extraction/extraction-schema-v0.5.json")
s = json.loads(SRC.read_text(encoding="utf-8"))
D = s["$defs"]


def find(node, key):
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


s["$id"] = "dlm-review/extraction-schema-v0.5.json"
s["title"] = "Paper 1 extraction record, form v0.5 (draft, not frozen)"
s["description"] = s["description"].replace("EXTRACTION-PLAN-v0.4.md", "EXTRACTION-PLAN-v0.5.md") + (
    " v0.5: higher_is_better, budget_across_arms, scoring and credited_ablation follow the brief's rules KA1-KA4.")
s["properties"]["form_version"]["const"] = "0.5"

hib = find(D, "higher_is_better")
assert len(hib) == 2, len(hib)          # h_unit and k_unit
for h in hib:
    h["description"] = ("KA1: printed direction (arrow or stated) first, else the convention list of the brief, "
                        "else null with the unit id in doubt")
b = find(D, "budget_across_arms")
assert len(b) == 1, len(b)
b[0]["description"] = ("KA2: matched = steps or NFE and generation length stated for every arm and equal (or "
                       "stated as the same); reported = steps or NFE stated for every arm, not matched; not "
                       "reported = steps or NFE missing for an arm")
sc = find(D, "scoring")
assert len(sc) == 1, len(sc)
sc[0]["description"] = "KA3: how this arm's quality values in the group were obtained"
ca = find(D, "credited_ablation")
assert len(ca) == 1, len(ca)
ca[0]["description"] = ("KA4: true when an arm removes the credited component (S13) or replaces it by another "
                        "method on the same base model; false otherwise")


def count_fields(node):
    n = 0
    if isinstance(node, dict):
        n += len(node.get("properties", {}))
        for v in node.values():
            n += count_fields(v)
    elif isinstance(node, list):
        for v in node:
            n += count_fields(v)
    return n


src_n = count_fields(json.loads(SRC.read_text(encoding="utf-8")))
assert count_fields(s) == src_n, (count_fields(s), src_n)
out = json.dumps(s, ensure_ascii=False, indent=1)
assert '"0.4"' not in out
DST.write_text(out + "\n", encoding="utf-8", newline="\n")
print(f"written {DST} sha256 {hashlib.sha256(DST.read_bytes()).hexdigest()}; property entries {src_n} (unchanged)")
try:
    import jsonschema
    jsonschema.Draft202012Validator.check_schema(s)
    print("jsonschema Draft 2020-12 check_schema: ok")
except ImportError:
    print("jsonschema not importable: schema not checked")
