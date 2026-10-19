"""Writes analysis/extraction/validator-tests.jsonl: the unit tests of the table-aware validator of
EXTRACTION-PLAN-v0.3 s6.3, as data (the tool itself is not built here). Real-text fixtures are line ranges
of the screened PyMuPDF texts, pinned by sha256 (the texts are not in git); synthetic fixtures are inline.
Run: python -I analysis/extraction/build_validator_tests.py analysis/extraction/validator-tests.jsonl
"""
import json, sys
out = sys.argv[1]
FT = "research/sources/md/fulltext-pymupdf/"
FIX = {
    "M03416": {"file": FT + "M03416.txt", "sha256": "ae6f033f5823bee4160343ba0a77e3ab57c8861e831180306fa7e6ab405369cc", "lines": [845, 887], "prepend_page": 7},
    "M12766-T1": {"file": FT + "M12766.txt", "sha256": "c0051304cc6e543872e6da7a236efaa590ce6556ce76030a2716e5f2a1f273b0", "lines": [526, 698], "prepend_page": None},
    "M12766-T2": {"file": FT + "M12766.txt", "sha256": "c0051304cc6e543872e6da7a236efaa590ce6556ce76030a2716e5f2a1f273b0", "lines": [739, 902], "prepend_page": None},
    "M07474-T2": {"file": FT + "M07474.txt", "sha256": "3a65e81519b49c3ed628cbb302b2aa6c68960bef8445b0ef8e167251153a4a47", "lines": [528, 765], "prepend_page": None},
    "M09530-T10": {"file": FT + "M09530.txt", "sha256": "5ae8c6aad53ab82d7147cb6e874c7adb104ba1e36d3150753cae19506b40cd62", "lines": [1424, 1658], "prepend_page": None},
    "M08100-T1": {"file": FT + "M08100.txt", "sha256": "b42020f73dc5c64c601fc8867532dd5884cef2aff11cc14e997341363bf97b07", "lines": [490, 718], "prepend_page": None},
    "M13864-T2": {"file": FT + "M13864.txt", "sha256": "cdc9398eb289636deec75075f5cd841454a735f75f5a48cf97b4be1d833e6740", "lines": [689, 828], "prepend_page": None},
}
TAB = {
    "M03416": {"id": "T01", "where": "Table 3", "page": 7, "orientation": "rows", "header_levels": 1,
               "header": "Method TF TB BA", "columns": ["TF", "TB", "BA"], "column_roles": ["condition"],
               "row_groups": [], "row_group_role": "none",
               "caption": "Table 3: Ablation results for DiffuseDef's accuracy under attack on AGNews datasets."},
    "M12766-T1": {"id": "T01", "where": "Table 1", "page": 8, "orientation": "rows", "header_levels": 2,
                  "header": "Model Text Gen Arch Image Gen Arch Params (B) Overall ↑Objects ↑Counting ↑Colors ↑Position ↑ Color ↑ Attribution Single Two",
                  "columns": ["Text Gen Arch", "Image Gen Arch", "Params (B)", "Overall", "Objects / Single", "Objects / Two", "Counting", "Colors", "Position", "Color Attribution"],
                  "column_roles": ["metric", "metric"], "row_groups": [], "row_group_role": "none",
                  "caption": "Table 1: Evaluation of text-to-image generation performance on the GenEval (Ghosh et al., 2024)."},
    "M12766-T2": {"id": "T01", "where": "Table 2", "page": 9, "orientation": "rows", "header_levels": 2,
                  "header": "Model Params (B) Text Gen Arch Image Gen Arch MS-COCO CIDEr ↑ VQAv2 Acc. ↑ MME Acc. ↑ GQA Acc. ↑ MMMU Acc. ↑",
                  "columns": ["Params (B)", "Text Gen Arch", "Image Gen Arch", "MS-COCO / CIDEr", "VQAv2 / Acc.", "MME / Acc.", "GQA / Acc.", "MMMU / Acc."],
                  "column_roles": ["benchmark", "metric"], "row_groups": [], "row_group_role": "none",
                  "caption": "Table 2: Evaluation of image captioning, visual question answering on multimodal benchmarks."},
    "M07474-T2": {"id": "T01", "where": "Table 2", "page": 8, "orientation": "rows", "header_levels": 2,
                  "header": "Benchmark Method LLaDA LLaDA-1.5 MMaDA-MixCoT LLaDA-MoE Accuracy TPS Accuracy TPS Accuracy TPS Accuracy TPS",
                  "columns": ["LLaDA / Accuracy", "LLaDA / TPS", "LLaDA-1.5 / Accuracy", "LLaDA-1.5 / TPS", "MMaDA-MixCoT / Accuracy", "MMaDA-MixCoT / TPS", "LLaDA-MoE / Accuracy", "LLaDA-MoE / TPS"],
                  "column_roles": ["second-factor", "metric"], "row_groups": ["GSM8K", "HumanEval", "Countdown", "ARC"], "row_group_role": "benchmark",
                  "caption": "Table 2: Comparison (%) of FDM with the heuristic decoding strategies across four benchmarks."},
    "M09530-T10": {"id": "T01", "where": "Table 10", "page": 17, "orientation": "columns", "header_levels": 1,
                   "header": "Model Context Random Left-to-Right Right-to-Left Entropy Confidence Margin Avg",
                   "columns": ["Random", "Left-to-Right", "Right-to-Left", "Entropy", "Confidence", "Margin", "Avg"],
                   "column_roles": ["arm"], "row_groups": ["LLaDA", "LLaDA 1.5", "LLaDA MoE", "Dream"], "row_group_role": "second-factor",
                   "caption": "Table 10: Safety scores (measured by HR) on TrustLDM-Adv with different decoding orders and post-contexts considering various LDMs."},
    "M08100-T1": {"id": "T01", "where": "Table 1", "page": 6, "orientation": "columns", "header_levels": 2,
                  "header": "Benchmark Qwen3-30B- A3B-Inst-2507 (Score) Ling-flash-2.0 (Score) LLaDA2.0-flash (Score | TPF) LLaDA2.1-flash (S Mode) (Score | TPF) LLaDA2.1-flash (Q Mode) (Score | TPF)",
                  "columns": ["Qwen3-30B-A3B-Inst-2507 / Score", "Ling-flash-2.0 / Score", "LLaDA2.0-flash / Score", "LLaDA2.0-flash / TPF",
                              "LLaDA2.1-flash (S Mode) / Score", "LLaDA2.1-flash (S Mode) / TPF", "LLaDA2.1-flash (Q Mode) / Score", "LLaDA2.1-flash (Q Mode) / TPF"],
                  "column_roles": ["arm", "metric"], "row_groups": ["Knowledge", "Reasoning", "Coding", "Math", "Agent & Alignment"], "row_group_role": "none",
                  "caption": "Table 1: Benchmark Performance of LLaDA2.1-flash, comparing with several baseline models."},
    "M13864-T2": {"id": "T01", "where": "Table 2", "page": 7, "orientation": "rows", "header_levels": 2,
                  "header": "Models Metrics Time BLEU COMET (sec.) ru en ru en",
                  "columns": ["BLEU / ru", "BLEU / en", "COMET / ru", "COMET / en", "Time (sec.)"],
                  "column_roles": ["metric", "condition"], "row_groups": [], "row_group_role": "none",
                  "caption": "Table 2. Table comparing the diffusion-based model Dream and the autoregressive model Qwen in terms of generation quality and speed."},
}


def cell(cid, row_label, cells, first_col=1, row_group="", occurrence=None, page=None):
    return {"id": cid, "table": "T01", "page": page, "row_label": row_label, "row_group": row_group,
            "first_col": first_col, "cells": cells, "occurrence": occurrence}


def val(ref, cid, col, value, column, **kw):
    d = {"ref": ref, "cell": cid, "col": col, "value_printed": value, "column_printed": column}
    d.update(kw)
    return d


T = []
def add(tid, finding, purpose, fx, cells, citing, expected, table_override=None, notes=""):
    tab = dict(TAB[fx]) if fx in TAB else None
    if table_override:
        tab.update(table_override)
    T.append({"test_id": tid, "finding": finding, "purpose": purpose, "fixture": FIX.get(fx, fx),
              "table": tab, "cells": cells, "citing": citing, "expected": expected, "notes": notes})

P7 = 7
# ---- M03416 (v0.2 fixture) -------------------------------------------------------------------
c_wdd = cell("C01", "w/o diffusion denoising", ["57.1", "58.4", "47.7"], page=7)
add("V01", "C1 (v0.1) regression", "correct ablation row accepted", "M03416", [c_wdd],
    [val("H01", "C01", 2, "58.4", "TB", unit="H")], {"status": "pass", "checks": {"row": "pass", "row_complete": True, "column": "column_verified"}})
add("V02", "F-MA4 (a)", "value at col 2 (TB) attributed to column BA", "M03416", [c_wdd],
    [val("H01", "C01", 2, "58.4", "BA", unit="H")], {"status": "fail", "checks": {"column": "column_mismatch"}},
    notes="v0.2 spec passed this silently (red-team cellv.py).")
add("V03", "F-MA4 (a)", "column map written in the wrong order on a single-level header", "M03416", [c_wdd],
    [val("H01", "C01", 2, "58.4", "BA", unit="H")], {"status": "fail", "checks": {"table": "column_order_mismatch"}},
    table_override={"columns": ["TF", "BA", "TB"]}, notes="With a consistent but wrong map the order check on a single-level header is what fails.")
add("V04", "M11 / T11 (v0.2) changed", "column_printed not in the map (v0.2 T11 gave a warning)", "M03416", [c_wdd],
    [val("H01", "C01", 1, "57.1", "AUA", unit="H")], {"status": "fail", "checks": {"column": "column_mismatch"}})

# ---- Muddit Table 1 ---------------------------------------------------------------------------
c_lwm = cell("C01", "LWM (Liu et al., 2024c)", ["AR", "AR", "7", "0.47", "0.93", "0.41", "0.46", "0.79", "0.09", "0.15"], page=8)
add("V05", "F-MA4 (b)", "LWM value 0.41 (col 6, Objects / Two) recorded under Overall", "M12766-T1", [c_lwm],
    [val("K01.A2", "C01", 6, "0.41", "Overall", unit="K", group_orientation="rows", arm_label="LWM (Liu et al., 2024c)", benchmark_printed="GenEval", metric_printed="Overall")],
    {"status": "fail", "checks": {"column": "column_mismatch"}},
    notes="The red-team called 0.41 the Counting value; by GenEval's column order (Overall, Single, Two, Counting, ...) it is Two objects. Either way the label Overall is wrong.")
add("V06", "F-MA4 (b)", "same value under its own column; two-level header whose bottom level is out of file order", "M12766-T1", [c_lwm],
    [val("K01.A2", "C01", 6, "0.41", "Objects / Two", unit="K", group_orientation="rows", arm_label="LWM (Liu et al., 2024c)")],
    {"status": "pass", "warnings": ["column_unverified"], "checks": {"row_complete": True, "row_width": "10 = 10", "table": "column_order_unverified (two-level)"}},
    notes="Correct but routed to the second reader with certainty: the map order cannot be confirmed from the linearised header.")
c_uni = cell("C02", "UniDisc (512 × 512) (Swerdlow et al., 2025b)", ["Discrete Diff.", "Discrete Diff.", "1.4", "0.42", "0.92", "0.47", "0.15", "0.67", "0.13", "0.19"], page=8)
add("V07", "red-team s3 false reject", "row label glued to the next cell by PyMuPDF ('2025b)Discrete')", "M12766-T1", [c_uni],
    [val("K01.A1", "C02", 4, "0.42", "Overall", unit="K", group_orientation="rows", arm_label="UniDisc (512 × 512) (Swerdlow et al., 2025b)")],
    {"status": "pass", "warnings": ["column_unverified"], "checks": {"row": "pass (glue split N3)"}})
add("V08", "red-team s3 false warning", "glued arrows in the header ('↑Counting') do not block header membership", "M12766-T1", [c_lwm],
    [val("K01.A2", "C01", 7, "0.46", "Counting", unit="K", group_orientation="rows", arm_label="LWM (Liu et al., 2024c)")],
    {"status": "pass", "warnings": ["column_unverified"], "checks": {"table": "map_in_header (arrows split and dropped, N3)"}})

# ---- Muddit Table 2 ---------------------------------------------------------------------------
c_sho = cell("C01", "Show-O (512×512) (Xie et al., 2024)", ["1.3", "AR", "Discrete Diff.", "-", "69.4", "1097.2", "58.0", "27.4"], page=9)
add("V09", "F-MA4 (b)", "Show-O GQA value 58.0 (col 7) recorded under VQAv2", "M12766-T2", [c_sho],
    [val("K02.A9", "C01", 7, "58.0", "VQAv2 / Acc.", unit="K", group_orientation="rows", arm_label="Show-O (512×512) (Xie et al., 2024)", benchmark_printed="VQAv2", metric_printed="Acc.")],
    {"status": "fail", "checks": {"column": "column_mismatch", "benchmark": "benchmark_column_mismatch"}})
add("V10", "F-MA4 (b)", "VQAv2 column but the GQA value: wrong token", "M12766-T2", [c_sho],
    [val("K02.A9", "C01", 5, "58.0", "VQAv2 / Acc.", unit="K", group_orientation="rows", arm_label="Show-O (512×512) (Xie et al., 2024)")],
    {"status": "fail", "checks": {"value": "value_mismatch"}})
add("V11", "F-MA4", "correct Show-O VQAv2 cell", "M12766-T2", [c_sho],
    [val("K02.A9", "C01", 5, "69.4", "VQAv2 / Acc.", unit="K", group_orientation="rows", arm_label="Show-O (512×512) (Xie et al., 2024)", benchmark_printed="VQAv2", metric_printed="Acc.")],
    {"status": "pass", "checks": {"row_complete": True, "row_width": "8 = 8", "column": "column_verified (two-level header; level-1 and bottom-level order confirmed)"}})

# ---- FDM Table 2 (row groups = benchmarks; level-1 columns = base model = second factor) ----------
m_gsm = ["80.14", "11.23", "82.18", "11.39", "56.18", "10.97", "76.80", "4.04"]
m_he = ["43.29", "8.76", "42.68", "8.83", "12.80", "8.65", "58.54", "3.81"]
add("V12", "F-MA4 (c)", "HumanEval row cited for a GSM8K unit", "M07474-T2", [cell("C01", "Margin (T=256)", m_he, row_group="HumanEval", page=8)],
    [val("K01.A2", "C01", 1, "43.29", "LLaDA / Accuracy", unit="K", group_orientation="rows", arm_label="Margin (T=256)", benchmark_printed="GSM8K", metric_printed="Accuracy", second_factor_printed="LLaDA")],
    {"status": "fail", "checks": {"row_group": "rowgroup_benchmark_mismatch"}})
add("V13", "F-MA4 (c)", "row group declared GSM8K but HumanEval's cells quoted", "M07474-T2", [cell("C01", "Margin (T=256)", m_he, row_group="GSM8K", page=8)],
    [val("K01.A2", "C01", 1, "43.29", "LLaDA / Accuracy", unit="K", group_orientation="rows", arm_label="Margin (T=256)", benchmark_printed="GSM8K", second_factor_printed="LLaDA")],
    {"status": "fail", "checks": {"row": "cells_mismatch (row match restricted to the GSM8K segment)"}})
add("V14", "F-MA4 (c)", "correct GSM8K Margin cell; occurrence not needed inside the row-group segment", "M07474-T2", [cell("C01", "Margin (T=256)", m_gsm, row_group="GSM8K", page=8)],
    [val("K01.A2", "C01", 1, "80.14", "LLaDA / Accuracy", unit="K", group_orientation="rows", arm_label="Margin (T=256)", benchmark_printed="GSM8K", metric_printed="Accuracy", second_factor_printed="LLaDA")],
    {"status": "pass", "checks": {"row": "pass (one match in segment)", "row_group": "pass", "second_factor": "pass", "column": "column_verified (bottom-level order Accuracy TPS ... confirmed)"}})
add("V15", "F-MA4 (c)", "LLaDA-1.5 column used in the LLaDA group", "M07474-T2", [cell("C01", "Margin (T=256)", m_gsm, row_group="GSM8K", page=8)],
    [val("K01.A2", "C01", 3, "82.18", "LLaDA-1.5 / Accuracy", unit="K", group_orientation="rows", arm_label="Margin (T=256)", benchmark_printed="GSM8K", second_factor_printed="LLaDA")],
    {"status": "fail", "checks": {"second_factor": "second_factor_mismatch"}})
add("V16", "F-MA4 (c)", "table has row groups but the cell names none (v0.2 behaviour)", "M07474-T2", [cell("C01", "Margin (T=256)", m_gsm, row_group="", occurrence=1, page=8)],
    [val("K01.A2", "C01", 1, "80.14", "LLaDA / Accuracy", unit="K", group_orientation="rows", arm_label="Margin (T=256)", benchmark_printed="GSM8K", second_factor_printed="LLaDA")],
    {"status": "fail", "checks": {"row_group": "row_group_missing"}})

# ---- TrustLDM Table 10 (columns orientation: arms = decoding orders; row groups = models) ------------
l_ss = ["76%", "66%", "82%", "80%", "72%", "62%", "73%"]
l15_ss = ["72%", "72%", "82%", "68%", "66%", "72%", "72%"]
add("V17", "F-MA4 (d)", "LLaDA 1.5 row cited for a LLaDA group", "M09530-T10", [cell("C01", "Suffix (Short)", l15_ss, row_group="LLaDA 1.5", page=17)],
    [val("K03.A3", "C01", 3, "82%", "Right-to-Left", unit="K", group_orientation="columns", arm_label="Right-to-Left", second_factor_printed="LLaDA", condition_printed="Suffix (Short)")],
    {"status": "fail", "checks": {"second_factor": "second_factor_mismatch"}})
add("V18", "F-MA4 (d)", "row group declared LLaDA but LLaDA 1.5's cells quoted", "M09530-T10", [cell("C01", "Suffix (Short)", l15_ss, row_group="LLaDA", page=17)],
    [val("K03.A3", "C01", 3, "82%", "Right-to-Left", unit="K", group_orientation="columns", arm_label="Right-to-Left", second_factor_printed="LLaDA")],
    {"status": "fail", "checks": {"row": "cells_mismatch"}})
add("V19", "F-MA4 (d)", "correct LLaDA cell; arm in the columns checked against the map", "M09530-T10", [cell("C01", "Suffix (Short)", l_ss, row_group="LLaDA", page=17)],
    [val("K03.A3", "C01", 3, "82%", "Right-to-Left", unit="K", group_orientation="columns", arm_label="Right-to-Left", second_factor_printed="LLaDA", condition_printed="Suffix (Short)")],
    {"status": "pass", "checks": {"row_complete": True, "row_width": "7 = 7", "column": "column_verified", "arm_column": "pass"}})
add("V20", "F-MA4 (d)", "correct cell, value given to the wrong arm", "M09530-T10", [cell("C01", "Suffix (Short)", l_ss, row_group="LLaDA", page=17)],
    [val("K03.A2", "C01", 3, "82%", "Right-to-Left", unit="K", group_orientation="columns", arm_label="Left-to-Right", second_factor_printed="LLaDA")],
    {"status": "fail", "checks": {"arm_column": "arm_column_mismatch"}})

# ---- LLaDA2.1 Table 1 (columns orientation, 'Score | TPF' cells, hyphen-split header) --------------
gpqa = ["54.14", "69.16", "62.31", "3.29", "66.67", "3.95", "67.30", "2.37"]
add("V21", "F-MA4 (e)", "Q-Mode value given to the S-Mode arm", "M08100-T1", [cell("C01", "GPQA", gpqa, row_group="Knowledge", page=6)],
    [val("K02.A1", "C01", 7, "67.30", "LLaDA2.1-flash (Q Mode) / Score", unit="K", group_orientation="columns", arm_label="LLaDA2.1-flash (S Mode)", benchmark_printed="GPQA", metric_printed="Score")],
    {"status": "fail", "checks": {"arm_column": "arm_column_mismatch"}})
add("V22", "F-MA4 (e)", "correct S-Mode score; '|' tokens dropped before counting; split header re-joined", "M08100-T1", [cell("C01", "GPQA", gpqa, row_group="Knowledge", page=6)],
    [val("K02.A1", "C01", 5, "66.67", "LLaDA2.1-flash (S Mode) / Score", unit="K", group_orientation="columns", arm_label="LLaDA2.1-flash (S Mode)", benchmark_printed="GPQA", metric_printed="Score")],
    {"status": "pass", "checks": {"row_complete": True, "row_width": "8 = 8", "table": "map_in_header (Qwen3-30B- + A3B-Inst-2507 joined, hyphen kept, N2; parentheses stripped, N5)", "column": "column_verified", "arm_column": "pass"}})
add("V23", "F-MA4 (e)", "column counted with '|' as a token (v0.2 counting)", "M08100-T1", [cell("C01", "GPQA", gpqa, row_group="Knowledge", page=6)],
    [val("K02.A1", "C01", 6, "66.67", "LLaDA2.1-flash (S Mode) / Score", unit="K", group_orientation="columns", arm_label="LLaDA2.1-flash (S Mode)")],
    {"status": "fail", "checks": {"value": "value_mismatch (token 6 is 3.95)"}})
syn_b = ("=== page 1 ===\nTable 8: Synthetic table whose second row has an empty middle cell.\nModel\nA\nB\nC\n"
         "Base\n1.0\n2.0\n3.0\nOurs\n4.0\n6.0\nThe text continues here.\n")
synb = {"id": "T01", "where": "Table 8", "page": 1, "orientation": "rows", "header_levels": 1, "header": "Model A B C",
        "columns": ["A", "B", "C"], "column_roles": ["metric"], "row_groups": [], "row_group_role": "none",
        "caption": "Table 8: Synthetic table whose second row has an empty middle cell."}
T.append({"test_id": "V24", "finding": "F-MA4", "purpose": "blank cell declared as an empty string", "fixture": {"text": syn_b},
          "table": synb, "cells": [cell("C01", "Ours", ["4.0", "", "6.0"], page=1)],
          "citing": [val("K01.A2", "C01", 3, "6.0", "C", unit="K", group_orientation="rows", arm_label="Ours")],
          "expected": {"status": "pass", "warnings": ["column_unverified"], "checks": {"row_width": "3 = 3 with 1 declared blank"}},
          "notes": "Declared blanks cannot be confirmed from the text, so the unit goes to the second reader with certainty."})
T.append({"test_id": "V25", "finding": "F-MA4", "purpose": "same row without the blank: complete row shorter than the map", "fixture": {"text": syn_b},
          "table": synb, "cells": [cell("C01", "Ours", ["4.0", "6.0"], page=1)],
          "citing": [val("K01.A2", "C01", 2, "6.0", "B", unit="K", group_orientation="rows", arm_label="Ours")],
          "expected": {"status": "fail", "checks": {"row_width": "row_width_mismatch (2 vs 3)"}}, "notes": ""})
nexus = ["49.93", "36.25", "50.45", "5.53", "44.83", "11.29", "47.65", "7.38"]
add("V35", "F-MA4", "last row of a page followed by the printed page number '6' (footer, N6)", "M08100-T1", [cell("C01", "Nexus FC", nexus, row_group="Agent & Alignment", page=6)],
    [val("K02.A1", "C01", 5, "44.83", "LLaDA2.1-flash (S Mode) / Score", unit="K", group_orientation="columns", arm_label="LLaDA2.1-flash (S Mode)", benchmark_printed="Nexus FC", metric_printed="Score")],
    {"status": "pass", "checks": {"row_complete": True, "row_width": "8 = 8", "column": "column_verified"}},
    notes="Without N6 the footer '6' would read as a ninth value and the row as incomplete.")

# ---- M13864 Table 2 (row label over two lines) --------------------------------------------------
add("V26", "F-MA1 (vii)", "row label cut before '(rate=1)', which is then quoted as a cell", "M13864-T2", [cell("C01", "Dream-v0-Instruct-7B", ["(rate=1)", "0.215", "0.328", "0.681", "0.826", "9.48"], page=7)],
    [val("K01.A1", "C01", 2, "0.215", "BLEU / ru", unit="K", group_orientation="rows", arm_label="Dream-v0-Instruct-7B")],
    {"status": "fail", "checks": {"row_width": "row_width_mismatch (6 vs 5)"}})
add("V27", "F-MA1 (vii)", "row label cut before '(rate=1)' and the quote started at first_col 2 with no first_col 1 entry", "M13864-T2", [cell("C01", "Dream-v0-Instruct-7B", ["0.215", "0.328", "0.681", "0.826", "9.48"], first_col=2, page=7)],
    [val("K01.A1", "C01", 2, "0.215", "BLEU / ru", unit="K", group_orientation="rows", arm_label="Dream-v0-Instruct-7B")],
    {"status": "fail", "checks": {"row": "pass (one match: the rate=4 row has other cells)", "row_start": "row_start_missing"}})
add("V28", "F-MA1 (vii)", "whole two-line label", "M13864-T2", [cell("C01", "Dream-v0-Instruct-7B (rate=1)", ["0.215", "0.328", "0.681", "0.826", "9.48"], page=7)],
    [val("K01.A1", "C01", 1, "0.215", "BLEU / ru", unit="K", group_orientation="rows", arm_label="Dream-v0-Instruct-7B (rate=1)", metric_printed="BLEU", condition_printed="ru")],
    {"status": "pass", "warnings": ["column_unverified"], "checks": {"row_complete": True, "row_width": "5 = 5"}})

# ---- synthetic cases -----------------------------------------------------------------------------
syn_h = "=== page 1 ===\nTable 9: Synthetic ablation table with a hyphenated row label across two lines.\nModel\nA\nB\nOurs\n1.0\n2.0\nself-\nconditioning\n3.0\n4.0\n"
synt = {"id": "T01", "where": "Table 9", "page": 1, "orientation": "rows", "header_levels": 1, "header": "Model A B",
        "columns": ["A", "B"], "column_roles": ["metric"], "row_groups": [], "row_group_role": "none",
        "caption": "Table 9: Synthetic ablation table with a hyphenated row label across two lines."}
T.append({"test_id": "V29", "finding": "F-mi8", "purpose": "label split by line-end hyphen before a lower-case word, quoted as printed", "fixture": {"text": syn_h},
          "table": synt, "cells": [cell("C01", "self-conditioning", ["3.0", "4.0"], page=1)],
          "citing": [val("K01.A2", "C01", 1, "3.0", "A", unit="K", group_orientation="rows", arm_label="self-conditioning")],
          "expected": {"status": "pass", "checks": {"row": "pass (hyphen-kept form, N2)", "column": "column_verified"}}, "notes": "v0.2 path joined to 'selfconditioning' and rejected the printed label."})
T.append({"test_id": "V30", "finding": "F-mi8", "purpose": "same label quoted de-hyphenated", "fixture": {"text": syn_h},
          "table": synt, "cells": [cell("C01", "selfconditioning", ["3.0", "4.0"], page=1)],
          "citing": [val("K01.A2", "C01", 1, "3.0", "A", unit="K", group_orientation="rows", arm_label="selfconditioning")],
          "expected": {"status": "pass", "checks": {"row": "pass (de-hyphenated fallback, N2)"}}, "notes": "Same two forms quote_check accepts."})
T.append({"test_id": "V31", "finding": "F-mi9", "purpose": "figure-only value needs no cell or prose evidence", "fixture": {"text": "=== page 1 ===\nFigure 4: The influence of K to model performance on GSM8K and Countdown benchmarks.\n"},
          "table": None, "cells": [],
          "citing": [{"ref": "K05.A1", "cell": None, "prose": None, "value_printed": "figure-only", "unit": "K", "figure_only": True}],
          "expected": {"status": "pass", "checks": {"value": "exempt (figure_only)"}}, "notes": ""})
T.append({"test_id": "V32", "finding": "F-mi9", "purpose": "'figure-only' value in a unit not marked figure_only", "fixture": {"text": "=== page 1 ===\nFigure 4: The influence of K to model performance on GSM8K and Countdown benchmarks.\n"},
          "table": None, "cells": [],
          "citing": [{"ref": "K05.A1", "cell": None, "prose": None, "value_printed": "figure-only", "unit": "K", "figure_only": False}],
          "expected": {"status": "fail", "checks": {"value": "missing_evidence"}}, "notes": ""})
syn_r = "=== page 1 ===\nTable 9: Synthetic table with the identical row printed twice on one page.\nModel\nA\nB\nOurs\n1.0\n2.0\nOurs\n1.0\n2.0\n"
synr = dict(synt, caption="Table 9: Synthetic table with the identical row printed twice on one page.")
T.append({"test_id": "V33", "finding": "v0.2 T15 kept", "purpose": "identical row twice without occurrence", "fixture": {"text": syn_r},
          "table": synr, "cells": [cell("C01", "Ours", ["1.0", "2.0"], page=1)],
          "citing": [val("K01.A1", "C01", 1, "1.0", "A", unit="K", group_orientation="rows", arm_label="Ours")],
          "expected": {"status": "fail", "checks": {"row": "ambiguous_row"}}, "notes": "With occurrence 2: pass."})
T.append({"test_id": "V34", "finding": "v0.2 T13 kept", "purpose": "one (cell, col) used by two values of one group", "fixture": FIX["M03416"],
          "table": TAB["M03416"], "cells": [c_wdd],
          "citing": [val("K01.A2", "C01", 1, "57.1", "TF", unit="K", group="G01", group_orientation="rows", arm_label="w/o diffusion denoising"),
                     val("K02.A2", "C01", 1, "57.1", "TF", unit="K", group="G01", group_orientation="rows", arm_label="w/o diffusion denoising")],
          "expected": {"status": "fail", "checks": {"reuse": "cell_reused"}}, "notes": ""})

with open(out, "w", encoding="utf-8", newline="\n") as f:
    for t in T:
        f.write(json.dumps(t, ensure_ascii=False) + "\n")
print(len(T), "tests written")
