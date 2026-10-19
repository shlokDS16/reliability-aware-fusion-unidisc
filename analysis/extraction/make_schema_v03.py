"""Builds research/review/extraction/extraction-schema-v0.3.json from v0.2 by the edits listed in
EXTRACTION-PLAN-v0.3 s4.11 (deterministic; v0.2 is read, never written). Each edit names its red-team finding.
Run: python -I analysis/extraction/make_schema_v03.py   (then the script checks the result with jsonschema
if it is importable, and prints the sha256 of the output).
"""
import copy
import hashlib
import json
from pathlib import Path

SRC = Path("research/review/extraction/extraction-schema-v0.2.json")
DST = Path("research/review/extraction/extraction-schema-v0.3.json")
s = json.loads(SRC.read_text(encoding="utf-8"))
D = s["$defs"]

s["$id"] = "dlm-review/extraction-schema-v0.3.json"
s["title"] = "Paper 1 extraction record, form v0.3 (draft, not frozen)"
s["description"] = s["description"].replace("v0.2", "v0.3") + (
    " v0.3: tables are described once in 'table_evidence' (header, leaf-column map, row groups, caption) and "
    "cell entries point to a table; K units carry condition_printed instead of a free column string; rq_class "
    "is derived from factor_type by script (EXTRACTION-PLAN-v0.3 s4.11).")

# --- F-MA4: table entry and cell entry -------------------------------------------------------------
D["table"] = {
    "type": "object", "additionalProperties": False,
    "required": ["id", "where", "page", "orientation", "header", "header_levels", "columns", "column_roles",
                 "row_groups", "row_group_role", "caption"],
    "properties": {
        "id": {"type": "string", "pattern": "^T[0-9]{2,3}$"},
        "where": {"type": "string", "pattern": "^(Table|Figure) [A-Z]?[0-9]+[a-z]?$|^untitled table$"},
        "page": {"type": "integer", "minimum": 1, "description": "page of the header"},
        "orientation": {"enum": ["rows", "columns"], "description": "rows: arms are rows; columns: arms are columns"},
        "header": {"type": "string", "minLength": 1, "description": "contiguous run of the header tokens exactly as in the file (may span lines; 1-60 tokens)"},
        "header_levels": {"enum": [1, 2]},
        "columns": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1},
                    "description": "leaf map: every column after the row-label column, left to right, including descriptor columns; a two-level leaf is '<level 1> / <level 2>' with each part as printed (arrows and enclosing parentheses may be dropped)"},
        "column_roles": {"type": "array", "minItems": 1, "maxItems": 2,
                         "items": {"enum": ["arm", "second-factor", "benchmark", "metric", "condition"]},
                         "description": "role of header level 1 (and level 2) in the value columns"},
        "row_groups": {"type": "array", "items": {"type": "string", "minLength": 1},
                       "description": "row-group labels in order, each a whole line of the file; [] if none"},
        "row_group_role": {"enum": ["benchmark", "second-factor", "condition", "none"]},
        "caption": {"type": "string", "description": "6-40 words starting with 'Table n' or 'Figure n'; '' only for 'untitled table'"},
    },
}
cell = D["cell"]
for k in ("where", "header", "caption"):
    cell["properties"].pop(k)
    cell["required"].remove(k)
cell["properties"]["table"] = {"type": "string", "pattern": "^T[0-9]{2,3}$"}
cell["properties"]["row_group"] = {"type": "string", "description": "the row group of this row as printed (one of the table's row_groups), '' if the table has none"}
cell["properties"]["cells"] = {"type": "array", "minItems": 1, "items": {"type": "string"},
                               "description": "one element per table cell from first_col on, each exactly as printed (a cell may hold several tokens, e.g. 'Discrete Diff.'); '|' separators are not cells; '' marks a blank cell; label tokens plus cell tokens at most 40 per entry"}
cell["properties"]["first_col"]["description"] = "1-based index of the first element of 'cells' in the row's cell sequence; every cited row needs an entry with first_col 1"
cell["properties"]["occurrence"]["description"] = "needed only when label plus cells match more than once inside the row-group segment (1-based)"
cell["properties"]["row_label"]["description"] = "every token of the row label as printed, over all its lines, up to the first cell (U11)"
cell["required"] = ["id", "cond", "table", "page", "row_label", "row_group", "first_col", "cells", "occurrence"]
s["properties"]["table_evidence"] = {"type": "array", "description": "R07 tables cited by cell entries (plan s6.3).", "items": {"$ref": "#/$defs/table"}}
s["required"].insert(s["required"].index("cell_evidence"), "table_evidence")

# --- F-MA1 / F-MA2: K unit key fields; group attributes ------------------------------------------------
ku = D["k_unit"]
ku["properties"].pop("column_printed")
ku["required"].remove("column_printed")
ku["properties"]["condition_printed"] = {"type": "string", "description": "U9: header parts (rows orientation) or row label and row group (columns orientation) that name neither the benchmark, the metric, an arm nor the second factor, joined top-down with ' / '; '' if none"}
ku["required"].insert(ku["required"].index("metric_kind"), "condition_printed")
ku["properties"]["duplicate"] = {"type": ["boolean", "null"], "x-filled-by": "script", "description": "U12 de-duplication flag"}
kv = D["k_value"]
kv["properties"]["column_printed"] = {"type": ["string", "null"], "description": "the leaf of the table's column map the value sits in (null for prose or figure-only values); checked against columns[col]"}
kv["required"].append("column_printed")

g = D["group"]
g["properties"]["rq_class"] = {"type": ["string", "null"], "x-filled-by": "script", "description": "derived from factor_type by the map of plan s5.3 U8"}
g["properties"]["second_factor_printed"]["description"] = "U7: the level of the second factor as printed (a row group, a level-1 column part or a legend entry); '' if none"
g["properties"]["anchor_arm"]["description"] = "U3: the anchor; null only for analysis and benchmark groups without a stated default"
g["properties"]["anchor_rule"] = {"enum": ["focal-label", "other-own-model", "stated-default", "value-identity", "first-own-arm", "none"],
                                  "description": "which clause of U3 gave the anchor ('none' when anchor_arm is null)"}
g["required"].insert(g["required"].index("arms"), "anchor_rule")
g["properties"]["duplicate"] = {"type": ["boolean", "null"], "x-filled-by": "script", "description": "U12: every contrast of the group is a duplicate"}
a = D["arm"]
a["properties"]["ar_label_source"] = {"enum": ["this-table", "caption-marker", "other-table", "text", "NA"],
                                      "description": "U5: where the paper labels this arm's generator of the scored output autoregressive; NA unless generator is autoregressive"}
a["required"].append("ar_label_source")
a["properties"]["label_printed"]["description"] = "row label (all lines) or column label exactly as printed"

# --- F-MA1 S14 anchored on the F1 unit -----------------------------------------------------------
mc = s["properties"]["study"]["properties"]["main_comparison"]
obj = [x for x in mc["anyOf"] if x.get("type") == "object"][0]
obj["properties"]["basis"] = {"enum": ["F1-table", "first-main-results-table"], "description": "s5.6: the F1 unit's table, or the first main-results table when the F1 number is abstract-only without a trace"}
obj["properties"]["row_group"] = {"type": "string", "description": "row group of the two rows, '' if none"}
obj["required"].append("row_group")
s["properties"]["study"]["properties"]["focal_model"]["description"] = "S17 focal model by U2 (plan s5.3): the first own model or method the abstract names (training-free methods: on the base model of the first own arm of the main-results table); analysis and benchmark studies: the diffusion model that is an arm of most main-text results tables and figures."
s["properties"]["study"]["properties"]["focal_config"] = {"type": "string", "description": "U2e: the focal configuration's arm label as printed in the main-results table, with its where (e.g. 'Table 2: FDM (K=2)')"}
s["properties"]["study"]["required"].append("focal_config")

# --- F-mi13 provenance; F-mi5 null QA sub-items tied to n -------------------------------------------
D["prov"]["enum"] = ["contributed", "inherited", "inherited-from-cited-method", "not_stated", "NA"]
for item in ("QA4", "QA5", "QA6"):
    sub = s["properties"]["qa"]["properties"][item]["properties"]["sub"]
    nulls = [k for k in sub["properties"] if k not in ("n", "c")] if item != "QA5" else ["a"]
    if item == "QA6":
        nulls = ["a", "b", "c", "d"] if "d" in sub["properties"] else nulls
    sub["allOf"] = [
        {"if": {"properties": {"n": {"const": "yes"}}, "required": ["n"]},
         "then": {"properties": {k: {"const": None} for k in nulls}}},
        {"if": {"properties": {"n": {"const": "no"}}, "required": ["n"]},
         "then": {"properties": {k: {"enum": ["yes", "no", "unclear"]} for k in nulls}}},
    ]

out = json.dumps(s, ensure_ascii=False, indent=1)
DST.write_text(out + "\n", encoding="utf-8", newline="\n")
print("written", DST, "sha256", hashlib.sha256(DST.read_bytes()).hexdigest())
try:
    import jsonschema
    jsonschema.Draft202012Validator.check_schema(s)
    print("jsonschema Draft 2020-12 check_schema: ok")
except ImportError:
    print("jsonschema not importable under -I; schema well-formedness checked as JSON only")
