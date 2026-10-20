"""Writes analysis/extraction/we-expected.jsonl: the expected H and K unit lists of
research/review/extraction/worked-examples-v0.4.md as data, one row per expected unit (agreement.py --we input,
plan v0.4 s11.1), and checks the counts against the markdown.

The unit lists are transcribed by hand below, group by group, with the markdown line of each group row. Where
the markdown gives a count but does not name the outcomes ("8 each", "2 fig-only each", "5"), the rows carry
outcome_source "not-enumerated" and null outcome fields, except where the group uses the same table as a group
whose outcomes are named (outcome_source "same-table-as <G>"). Nothing is filled from the papers themselves.

Count check (exit 1 on any difference): per group row, the leading count of the markdown's K-units column
(times the group range for "each" rows) against the rows built here; per paper, the "Totals:" line (groups,
table units, fig-only units, K units) and the H-unit count word; and the s6 summary table.

    python -I analysis/extraction/build_we_expected.py [--out analysis/extraction/we-expected.jsonl]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MD = ROOT / "research" / "review" / "extraction" / "worked-examples-v0.4.md"
MD_SHA256 = "6a3219da8c5d7a54832864c96155c0561dc4157716311c073ab5216d803a9a87"
OUT = ROOT / "analysis" / "extraction" / "we-expected.jsonl"
SECTION_OF = {"M07474": 1, "M12766": 2, "M09530": 3, "M13864": 4, "M08100": 5}
WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def bm(benchmarks, metrics):
    """Benchmark-major cross product as outcome dicts."""
    return [{"benchmark": b, "metric": m, "condition": None, "outcome_md": f"{b} {m}"} for b in benchmarks for m in metrics]


def o(outcome_md, benchmark=None, metric=None, condition=None):
    return {"benchmark": benchmark, "metric": metric, "condition": condition, "outcome_md": outcome_md}


def unnamed(n):
    return [None] * n


def G(gids, where, second, arms, anchor, units, line, figure_only=False, source="md", duplicate=False, note=None):
    """One markdown group row. gids: one id or a list (range rows); second: one value or a list per id."""
    gids = gids if isinstance(gids, list) else [gids]
    seconds = second if isinstance(second, list) else [second] * len(gids)
    anchors = anchor if isinstance(anchor, list) else [anchor] * len(gids)
    armss = arms if (isinstance(arms, list) and arms and isinstance(arms[0], list)) else [arms] * len(gids)
    return [{"group_id": g, "where": where, "second_factor": s, "arms": a, "anchor": an, "units": units,
             "md_line": line, "figure_only": figure_only, "outcome_source": source, "duplicate": duplicate, "note": note}
            for g, s, a, an in zip(gids, seconds, armss, anchors)]


FOUR = ["LLaDA", "LLaDA-1.5", "MMaDA-MixCoT", "LLaDA-MoE"]
T2_FDM = bm(["GSM8K", "HumanEval", "Countdown", "ARC"], ["Accuracy", "TPS"])

PAPERS = {
    "M07474": {
        "H": [{"unit_id": "H01", "value_printed": "86.00", "origin": "F1-table", "where": "Table 2", "row_group": "ARC",
               "row_label": "FDM (K=2)", "column": "LLaDA / Accuracy", "metric": None, "benchmark": "ARC",
               "trace_md": None, "md_line": 50}],
        "groups": (
            G("G01", "Table 1", None, ["FDM-A", "Random", "Margin"], "FDM-A",
              [o("ARC Accuracy", "ARC", "Accuracy"), o("ARC Tokens/Seconds", "ARC", "Tokens/Seconds")], 60)
            + G(["G02", "G03", "G04", "G05"], "Table 2", FOUR,
                ["FDM (K=2)", "Probability (T=256)", "Margin (T=256)", "Entropy (T=256)"], "FDM (K=2)", T2_FDM, 61)
            + G(["G06", "G07", "G08", "G09"], "Table 2", FOUR, ["FDM (K=2)", "FDM (K=3)", "FDM (K=4)"], "FDM (K=2)",
                T2_FDM, 62, source="same-table-as G02")
            + G(["G10", "G11", "G12", "G13"], "Table 3", FOUR,
                ["FDM-A (Ours)", "Probability (T=128)", "Margin (T=128)", "Entropy (T=128)", "EB", "WINO"], "FDM-A (Ours)",
                unnamed(8), 63, source="not-enumerated")
            + G(["G14", "G15"], "Figure 4", ["FDM", "FDM-A"], "K = 2 (anchor) ... 12", "K = 2",
                [o("GSM8K Accuracy", "GSM8K", "Accuracy"), o("Countdown Accuracy", "Countdown", "Accuracy")], 64, True)
            + G(["G16", "G17"], "Figure 5", ["K = 2", "K = 4"], 'gamma = 0.5 (anchor, setup "0.5 for FDM-A") ...',
                "gamma = 0.5", unnamed(2), 65, True, "not-enumerated")
            + G("G18", "Figure 6", None, "eta1 = 0.8 (anchor, setup) ...", "eta1 = 0.8",
                bm(["GSM8K", "Countdown"], ["Accuracy", "TPS"]), 66, True)
            + G("G19", "Figure 7", None, "eta2 = 0.7 (anchor, setup) ...", "eta2 = 0.7", unnamed(4), 67, True, "not-enumerated")
            + G(["G20", "G21"], "Figure 8", ["FDM", "FDM-A"], "as G14-G15", "K = 2",
                [o("HumanEval", "HumanEval"), o("ARC", "ARC")], 68, True)
            + G(["G22", "G23"], "Figure 9", ["K = 2", "K = 4"], "as G16-G17", "gamma = 0.5", unnamed(2), 69, True, "not-enumerated")
            + G("G24", "Figure 10", None, "as G18", "eta1 = 0.8", unnamed(4), 70, True, "not-enumerated")
            + G("G25", "Figure 11", None, "as G19", "eta2 = 0.7", unnamed(4), 71, True, "not-enumerated")
        ),
    },
    "M12766": {
        "H": [{"unit_id": "H01", "value_printed": "0.61", "origin": "F1-table", "where": "Table 1", "row_group": "",
               "row_label": "Muddit (512 × 512)", "column": "Overall", "metric": "Overall", "benchmark": "GenEval",
               "trace_md": None, "md_line": 100}],
        "groups": (
            G("G01", "Table 1", None, ["Muddit (512 × 512)", "LWM", "SEED-X", "Chameleon"], "Muddit (512 × 512)",
              [o("GenEval Overall", "GenEval", "Overall")], 108)
            + G("G02", "Table 2", None,
                ["Muddit (512×512)", "InternVL-2.0", "LLaVA-Next", "BLIP-2", "QWEN-VL", "OpenFlamingo", "Flamingo",
                 "Chameleon", "LWM", "Show-O (256×256)", "Show-O (512×512)", "Transfusion"], "Muddit (512×512)",
                [o("MS-COCO / CIDEr", "MS-COCO", "CIDEr"), o("VQAv2 / Acc.", "VQAv2", "Acc."), o("MME / Acc.", "MME", "Acc."),
                 o("GQA / Acc.", "GQA", "Acc."), o("MMMU / Acc.", "MMMU", "Acc.")], 109)
            + G("G03", "Table 3", None, ["0.6", "0.2", "0.4", "0.8", "1.0"], "0.6",
                [o("GenEval", "GenEval"), o("MS-COCO", "MS-COCO"), o("VQAv2", "VQAv2")], 110)
            + G("G04", "Table 4", None, ["Joint training", "T2I only", "I2T only"], "Joint training",
                [o("GenEval (3 arms)", "GenEval"), o("MS-COCO (2 arms)", "MS-COCO"), o("VQAv2 (2 arms)", "VQAv2")], 111)
            + G("G05", "Table 5", None, ["T=64", "T=8", "T=16", "T=24", "T=32", "T=40"], "T=64",
                [o("GenEval", "GenEval"), o("CIDEr", None, "CIDEr"), o("VQAv2", "VQAv2")], 112)
            + G("G06", "Table 7", None, ["Muddit (512×512)", "Show-O (512×512) (Xie et al., 2024)"], "Muddit (512×512)",
                [o("VQAv2", "VQAv2"), o("MME", "MME"), o("MMMU", "MMMU")], 113, duplicate=True,
                note="all three flagged duplicate of G02 by U12")
            + G("G07", "Table 9", None, ["CFG = 1.5", "CFG = 1", "2", "2.5", "3"], "CFG = 1.5",
                [o("MS-COCO", "MS-COCO"), o("VQAv2", "VQAv2")], 114)
            + G("G08", "Figure 12", None, ["Muddit", "Qwen-2.5-VL", "Show-o", "BLIP-2", "LLaVA-1.6"], "Muddit",
                [o("latency", None, "latency")], 115, True)
        ),
    },
    "M09530": {
        "H": [{"unit_id": "H01", "value_printed": "3%", "origin": "F1-table", "where": "Table 1", "row_group": "",
               "row_label": "LLaDA", "column": "Empty", "metric": "HR", "benchmark": "TrustLDM-Adv",
               "trace_md": None, "md_line": 156}],
        "groups": (
            G("G01", "Table 2", None, ["Random", "L2R", "R2L", "Entropy", "Confidence", "Margin"], None,
              [o(f"{b} / {c}", b, None, c) for b in ("TrustLDM-Adv", "TrustLDM-JBB")
               for c in ("Empty", "Suffix / Safe", "Suffix / Short", "Suffix / Long", "Suffix+Prefix / Short",
                         "Suffix+Prefix / Long")], 167)
            + G("G02", "Table 4", None, ["Random", "L2R", "R2L", "Confidence", "Margin", "Entropy"], None,
                [o("privacy benchmark x 6 conditions", "privacy benchmark")] * 6, 168,
                note="conditions not named in the row")
            + G("G03", "Table 6", None, ["Random", "L2R", "R2L", "Confidence", "Margin", "Entropy"], None,
                [o("fairness benchmark x 6 conditions", "fairness benchmark")] * 6, 169,
                note="conditions not named in the row; arms 'as G02'")
            + G("G04", "Figure 2", None, ["block size 16", "32", "64", "128"], "64",
                [o("(TrustLDM-Adv, HR)", "TrustLDM-Adv", "HR"), o("(TrustLDM-JBB, HR)", "TrustLDM-JBB", "HR")], 170, True)
            + G("G05", "Figure 2", None, ["generation length 128", "256", "512", "1024"], "256", unnamed(2), 171, True,
                "not-enumerated")
            + G("G06", "Figure 3", None, "block size", "64", [o("(privacy, LR)", "privacy", "LR")], 172, True)
            + G("G07", "Figure 3", None, "generation length", "256", unnamed(1), 173, True, "not-enumerated")
            + G("G08", "Figure 4", None, "block size", "64", [o("(fairness, EOD)", "fairness", "EOD")], 174, True)
            + G("G09", "Figure 4", None, "generation length", "256", unnamed(1), 175, True, "not-enumerated")
        ),
    },
    "M13864": {
        "H": [{"unit_id": "H01", "value_printed": "0.215", "origin": "F1-table", "where": "Table 1", "row_group": "",
               "row_label": "Dream-v0-Instruct-7B", "column": "BLEU / ru", "metric": "BLEU", "benchmark": None,
               "trace_md": None, "md_line": 194}],
        "groups": (
            G("G01", "Table 1", None, ["Dream-v0-Instruct-7B", "Dream-Coder-v0-Instruct-7B", "DiffuCoder-7B-Instruct",
                                       "DiffuCoder-7B-cpGRPO", "LLaDa 1.5", "Qwen2.5-7B"], None,
              [o("BLEU / ru", None, "BLEU", "ru"), o("BLEU / en", None, "BLEU", "en"),
               o("COMET / ru", None, "COMET", "ru"), o("COMET / en", None, "COMET", "en")], 203)
            + G("G02", "Table 2", None, ["Dream-v0-Instruct-7B (rate=1)", "Dream-v0-Instruct-7B (rate=4)", "Qwen2.5-7B"],
                None, [o("BLEU / ru", None, "BLEU", "ru"), o("BLEU / en", None, "BLEU", "en"),
                       o("COMET / ru", None, "COMET", "ru"), o("COMET / en", None, "COMET", "en"),
                       o("Time (sec.)", None, "Time (sec.)")], 204, duplicate="partial",
                note="U12 flags the contrasts equal to G01's on BLEU ru, BLEU en and COMET en (l.210-213)")
            + G("G03", "Table 2", None, ["Dream-v0-Instruct-7B (rate=1)", "Dream-v0-Instruct-7B (rate=4)"], None,
                [o("BLEU / ru", None, "BLEU", "ru"), o("BLEU / en", None, "BLEU", "en"),
                 o("COMET / ru", None, "COMET", "ru"), o("COMET / en", None, "COMET", "en"),
                 o("Time (sec.)", None, "Time (sec.)")], 205, source="same-table-as G02")
            + G("G04", "Figure 3", None, "rate 1 ... 8", None, [o("(corpus, BLEU)", "corpus", "BLEU")], 206, True)
            + G("G05", "Figure 4", None, "rate 1 ... 8", None, [o("(corpus, COMET)", "corpus", "COMET")], 207, True)
            + G("G06", "Figure 5", None, ["Origin", "MaskGIT+", "TopK Margin", "Entropy"], None,
                [o("BLEU", None, "BLEU"), o("COMET", None, "COMET")], 208, True)
        ),
    },
    "M08100": {
        "H": [{"unit_id": "H01", "value_printed": "892", "origin": "abstract", "where": "abstract", "row_group": "",
               "row_label": "", "column": "", "metric": "TPS", "benchmark": "HumanEval+",
               "trace_md": "Table 3, w/ Quant TPS 891.74", "md_line": 227},
              {"unit_id": "H02", "value_printed": "801", "origin": "abstract", "where": "abstract", "row_group": "",
               "row_label": "", "column": "", "metric": "TPS", "benchmark": "BigCodeBench",
               "trace_md": "Table 3, w/ Quant TPS 801.48", "md_line": 227},
              {"unit_id": "H03", "value_printed": "663", "origin": "abstract", "where": "abstract", "row_group": "",
               "row_label": "", "column": "", "metric": "TPS", "benchmark": "LiveCodeBench",
               "trace_md": "Table 3, w/ Quant TPS 663.39", "md_line": 227},
              {"unit_id": "H04", "value_printed": "72.34", "origin": "F1-table", "where": "Table 1", "row_group": "",
               "row_label": "Average", "column": "LLaDA2.1-flash (S Mode) / Score", "metric": "Score",
               "benchmark": "Average", "trace_md": None, "md_line": 234}],
        "groups": (
            G("G01", "Table 1", None, ["LLaDA2.1-flash (S Mode)", "Qwen3-30B-A3B-Inst-2507", "Ling-flash-2.0"],
              "LLaDA2.1-flash (S Mode)", [o("Average / Score", "Average", "Score")], 242)
            + G("G02", "Table 1", None, ["S Mode", "Q Mode"], "S Mode",
                [o("Average / Score", "Average", "Score"), o("Average / TPF", "Average", "TPF")], 243,
                note="arms of LLaDA2.1-flash; anchor by focal-label (s7)")
            + G("G03", "Table 2", None, ["LLaDA2.1-mini (S Mode)", "Qwen3-8B (no think)", "Ling-mini-2.0"],
                "LLaDA2.1-mini (S Mode)", [o("Average / Score", "Average", "Score")], 244)
            + G("G04", "Table 2", None, ["S Mode", "Q Mode"], "S Mode", unnamed(2), 245, source="not-enumerated",
                note="arms of LLaDA2.1-mini; anchor by other-own-model (s7)")
            + G(["G05", "G06"], "Table 3", ["LLaDA2.1-flash", "LLaDA2.1-mini"], ["w/o Quant", "w/ Quant"], "w/o Quant",
                [o(f"TPS on {b}", b, "TPS") for b in ("HumanEval+", "MBPP+", "CRUXEval-O", "BigCodeBench-Full",
                                                      "LiveCodeBench", "GSM-Plus", "GPQA-Diamond", "IFEval", "PrOntoQA")], 246)
            + G(["G07", "G08"], "Table 4", ["LLaDA2.1-flash", "LLaDA2.1-mini"], ["w/o MBE", "w/ MBE"], "w/o MBE",
                bm(["MMLU-Pro", "TriviaQA", "bbh-zh", "ZebraLogic", "LiveCodeBench", "CRUXEval-O", "BigCodeBench-Full",
                    "Spider", "AIME 2025", "IFEval-strict-prompt"], ["Score", "TPF"]), 247)
            + G(["G09", "G10"], "Figure 3", ["Mini Series", "Flash Series"],
                [["LLaDA2.1-mini (S mode)", "Ling-mini-2.0", "Qwen3-8B"], ["LLaDA2.1-flash (S mode)", "Ling-flash-2.0"]],
                ["LLaDA2.1-mini (S mode)", "LLaDA2.1-flash (S mode)"],
                [o('TPS over "nine benchmarks"', None, "TPS")], 248, True)
        ),
    },
}


def build_rows():
    rows = []
    for rid, paper in PAPERS.items():
        for h in paper["H"]:
            rows.append({"record_id": rid, "kind": "H", **h})
        seq = 0
        for g in paper["groups"]:
            for k, u in enumerate(g["units"], 1):
                seq += 1
                u = u or {"benchmark": None, "metric": None, "condition": None, "outcome_md": None}
                rows.append({"record_id": rid, "kind": "K", "seq": seq, "group_id": g["group_id"], "unit_in_group": k,
                             "where": g["where"], "second_factor": g["second_factor"], "arms": g["arms"],
                             "anchor": g["anchor"], "figure_only": g["figure_only"],
                             "outcome_md": u["outcome_md"], "benchmark": u["benchmark"], "metric": u["metric"],
                             "condition": u["condition"], "outcome_source": g["outcome_source"],
                             "duplicate": g["duplicate"], "note": g["note"], "md_line": g["md_line"]})
    return rows


# ------------------------------------------------------------------------------------------------ count check
def _expand(gcell):
    m = re.match(r"^(G\d{2})(?:-(G\d{2}))?$", gcell.strip())
    if not m:
        return None
    a = int(m.group(1)[1:])
    b = int(m.group(2)[1:]) if m.group(2) else a
    return [f"G{i:02d}" for i in range(a, b + 1)]


def md_counts(md_text):
    """{record: {"groups": {gid: (n_units, fig_only)}, "totals": {...}, "h": n}} parsed from the markdown."""
    lines = md_text.split("\n")
    out, cur = {}, None
    for i, ln in enumerate(lines, 1):
        m = re.match(r"^## (\d)\. (M\d{5}),", ln)
        if m:
            cur = m.group(2)
            out[cur] = {"groups": {}, "totals": None, "h": None, "lines": {}}
            continue
        if cur is None:
            continue
        if re.match(r"^\| G\d{2}", ln):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            gids = _expand(cells[0])
            last = cells[-1]
            m2 = re.match(r"^(\d+)( fig-only)?( each)?", last)
            if gids is None or not m2:
                raise SystemExit(f"cannot parse group row at md line {i}: {ln[:80]}")
            if not m2.group(3) and len(gids) > 1:
                raise SystemExit(f"range row without 'each' at md line {i}")
            for g in gids:
                out[cur]["groups"][g] = (int(m2.group(1)), bool(m2.group(2)))
                out[cur]["lines"][g] = i
        m3 = re.match(r"^Totals: \*\*(\d+) groups; (.*?)\*\*", ln)
        if m3:
            body = m3.group(2)
            nums = {"groups": int(m3.group(1))}
            k = re.search(r"= (\d+) K units", body) or re.search(r"(\d+) K units", body)
            nums["k_units"] = int(k.group(1))
            t = re.search(r"(\d+) table(?: units)?", body)
            f = re.search(r"(\d+) fig-only", body)
            nums["table_units"] = int(t.group(1)) if t else None
            nums["fig_units"] = int(f.group(1)) if f else None
            out[cur]["totals"] = nums
        m4 = re.search(r"\b(One|Two|Three|Four|Five) units?\.", ln)
        if m4 and out[cur]["h"] is None:
            out[cur]["h"] = WORDS[m4.group(1)]
    summary = {}
    for ln in lines:
        m5 = re.match(r"^\|\s*(?:[^|]*?\s)?(M\d{5}) \|[^|]+\| (\d+) \| (\d+) \((\d+)\)[^|]*\| (\d+) \|", ln)
        if m5:
            summary[m5.group(1)] = {"groups": int(m5.group(2)), "k_units": int(m5.group(3)),
                                    "fig_units": int(m5.group(4)), "h": int(m5.group(5))}
    return out, summary


def count_check(rows, md_text):
    parsed, summary = md_counts(md_text)
    errs, report = [], []
    for rid in PAPERS:
        p = parsed.get(rid)
        if p is None:
            errs.append(f"{rid}: section not found in the markdown")
            continue
        k = [r for r in rows if r["record_id"] == rid and r["kind"] == "K"]
        h = [r for r in rows if r["record_id"] == rid and r["kind"] == "H"]
        built = {}
        for r in k:
            n, fig = built.get(r["group_id"], (0, r["figure_only"]))
            built[r["group_id"]] = (n + 1, fig)
        if set(built) != set(p["groups"]):
            errs.append(f"{rid}: group ids differ: built {sorted(built)} md {sorted(p['groups'])}")
        for g, (n, fig) in sorted(p["groups"].items()):
            bn, bfig = built.get(g, (0, None))
            if bn != n:
                errs.append(f"{rid} {g}: {bn} units built, md line {p['lines'][g]} says {n}")
            if fig and not bfig:
                errs.append(f"{rid} {g}: md says fig-only, built rows are not")
        t = p["totals"] or {}
        nfig = sum(1 for r in k if r["figure_only"])
        checks = [("groups", len(built), t.get("groups")), ("K units", len(k), t.get("k_units")),
                  ("table units", len(k) - nfig, t.get("table_units")), ("fig-only units", nfig, t.get("fig_units")),
                  ("H units", len(h), p["h"])]
        s = summary.get(rid, {})
        checks += [("s6 groups", len(built), s.get("groups")), ("s6 K units", len(k), s.get("k_units")),
                   ("s6 fig-only", nfig, s.get("fig_units")), ("s6 H units", len(h), s.get("h"))]
        for what, got, want in checks:
            if want is None or got != want:
                errs.append(f"{rid} {what}: built {got}, markdown {want}")
        report.append(f"{rid}: {len(built)} groups, {len(k)} K units ({len(k) - nfig} table, {nfig} fig-only), "
                      f"{len(h)} H units; markdown totals {t}, H {p['h']}, s6 {s}")
    return errs, report


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    data = MD.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != MD_SHA256:
        print(f"worked-examples-v0.4.md changed: sha256 {sha}, expected {MD_SHA256}")
        return 1
    rows = build_rows()
    errs, report = count_check(rows, data.decode("utf-8"))
    for ln in report:
        print(ln)
    if errs:
        for e in errs:
            print("COUNT MISMATCH:", e)
        return 1
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps({"source_sha256": MD_SHA256, **r}, ensure_ascii=False) + "\n")
    n_k = sum(1 for r in rows if r["kind"] == "K")
    print(f"count check passed; {len(rows)} rows written ({len(rows) - n_k} H, {n_k} K) to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
