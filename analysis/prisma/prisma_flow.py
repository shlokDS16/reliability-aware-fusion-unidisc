"""PRISMA 2020 flow counts for Paper 1, every number read from files (status 2026-10-17, before the human
validation sample, the e-gateway papers and the re-check K test).

Strands: (1) seed corpus 2026-10-13/14 (arXiv S1/S2 + Awesome-DLMs; screening/records.jsonl); (2) free-source
search update 2026-10-15 (D0026-D0030); (3) six subscription databases (D0031; tools/ingest_subscription.py
summary); then title/abstract screening, the title/abstract re-check (criteria v1.6 A s5) and full-text
tranche T1. Writes prisma-flow.json and prisma-flow.md next to this script. Stages not run are marked
"pending"; gaps the counts expose are listed under "open".

    python analysis/prisma/prisma_flow.py
"""
import collections
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REV, SCR = ROOT / "research/review", ROOT / "analysis/screening"
HERE = Path(__file__).resolve().parent


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def jg(pattern):
    return [r for p in sorted(glob.glob(str(pattern))) for r in jl(p)]


def jload(p):
    return json.load(open(p, encoding="utf-8"))


F = {}  # every count, keyed by box

# ---------------------------------------------------------------- (1) seed corpus
search = {}
for r in jl(REV / "corpus/search-log.jsonl"):
    if r.get("string") in ("S1", "S2") and "records_retrieved" in r and "arxiv" in r.get("database", "").lower():
        search[r["string"]] = r["records_retrieved"]
awesome = len(jl(REV / "corpus/awesome-dlms@194aa6bd.jsonl"))
dd = jload(REV / "screening/dedup-report.json")
v1 = {r["sid"]: r for r in jl(REV / "screening/records.jsonl")}
assert len(v1) == dd["records"]
A1 = {d["sid"]: d["decision"] for d in jg(REV / "screening/screener-A/batch-*.jsonl")}
B1 = {d["sid"]: d["decision"] for d in jg(REV / "screening/screener-B/batch-*.jsonl")}
assert set(A1) == set(B1) == set(v1)
v1_either = {s for s in v1 if A1[s] != "exclude" or B1[s] != "exclude"}
v1_both = {s for s in v1 if A1[s] != "exclude" and B1[s] != "exclude"}
F["seed"] = {"identified_arxiv_S1": search.get("S1"), "identified_arxiv_S2": search.get("S2"),
             "identified_awesome_dlms": awesome, "duplicates_merged": dd["duplicates_merged"],
             "records_after_dedup": dd["records"], "ta_screened_dual_v1": len(v1),
             "ta_both_exclude": len(v1) - len(v1_either), "ta_pass_either": len(v1_either),
             "ta_pass_both": len(v1_both)}

# ---------------------------------------------------------------- (2) free-source search update
ms = jload(REV / "corpus/search-v2-merge-stats-2026-10-15.json")
db_src = {k: v for k, v in ms["sources"].items() if not k.startswith("snowball")}
cit_src = {k: v for k, v in ms["sources"].items() if k.startswith("snowball")}
new = jl(REV / "corpus/new-records-2026-10-15-v2.jsonl")
auto26 = sum(1 for r in new if r.get("auto_excluded"))
auto27 = len(jl(REV / "corpus/auto-excluded-2026-10-15.jsonl"))
queue = len(jl(REV / "corpus/screening-queue-final-2026-10-15.jsonl"))
man2 = jload(REV / "screening/v2/manifest.json")
A2 = {d["id"]: d["decision"] for d in jg(REV / "screening/v2/screener-A-batch-*.jsonl")}
B2 = {d["id"]: d["decision"] for d in jg(REV / "screening/v2/screener-B-batch-*.jsonl")}
assert set(A2) == set(B2) and len(A2) == man2["n_total"]
v2_pass = {i for i in A2 if A2[i] != "exclude" or B2[i] != "exclude"}
R2 = jg(REV / "screening/v2/rescue/screener-R-rescue-*.jsonl")
r2_pos = {r["id"] for r in R2 if r["decision"] != "exclude"}
tr = jload(REV / "corpus/title-resolution-2026-10-15.json")
F["free"] = {"identified_databases_by_source": {k: v["identified"] for k, v in db_src.items()},
             "identified_databases": sum(v["identified"] for v in db_src.values()),
             "identified_citation_searching_by_source": {k: v["identified"] for k, v in cit_src.items()},
             "identified_citation_searching": sum(v["identified"] for v in cit_src.values()),
             "duplicates_within_source": sum(v["duplicates_within_source"] for v in ms["sources"].values()),
             "duplicates_against_seed_corpus": sum(v["duplicates_against_existing"] for v in ms["sources"].values()),
             "extra_duplicate_key_merges": ms["extra_duplicate_keys_merges"],
             "new_records_after_dedup": len(new), "new_snowball_only": sum(1 for r in new if r.get("snowball_only")),
             "automation_excluded_D0026": auto26, "automation_excluded_D0027": auto27,
             "queue_final_D0027": queue, "released_D0028": man2["n_released_S1_S2"],
             "ta_screened_dual": len(A2), "ta_pass_D0030": len(v2_pass), "ta_both_exclude": len(A2) - len(v2_pass),
             "rescue_screened_single_haiku": len(R2),
             "rescue_decisions": dict(collections.Counter(r["decision"] for r in R2)),
             "rescue_positives": len(r2_pos),
             "title_only_snowball_population": tr["population"], "title_only_duplicates": tr["duplicates_of_existing_records"],
             "title_only_resolved": tr["resolved"], "title_only_unresolvable": tr["unresolvable"],
             "title_only_lookup_incomplete": tr["unresolved_lookup_incomplete"],
             "title_only_queued": len(jl(REV / "screening/v2/title-resolved-queue.jsonl"))}

# ---------------------------------------------------------------- (3) subscription databases
si = jload(REV / "corpus/subscription-ingest-2026-10-15.json")
pr = si["prisma"]
ieee_md = (ROOT / "research/sources/search-raw/ieee-xplore/ieee-queries-20261015.md").read_text(encoding="utf-8")
ieee_hits = {m.group(1): int(m.group(2).replace(",", "")) for m in re.finditer(r"^(I\d) \(.*?\): hits ([\d,]+);", ieee_md, re.M)}
RS = jg(REV / "screening/v2/rescue-subscription/screener-R-rescue-sub-*.jsonl")
rescued_q = jl(REV / "screening/v2/rescue-subscription/rescued-queue.jsonl")
no_abs = [l for l in open(REV / "screening/v2/rescue-subscription/pending-no-abstract.txt", encoding="utf-8") if l.strip()]
DSa = {d["id"]: d["decision"] for d in jg(REV / "screening/v2/dual-subscription/screener-A-batch-sub-*.jsonl")}
DSb = {d["id"]: d["decision"] for d in jg(REV / "screening/v2/dual-subscription/screener-B-batch-sub-*.jsonl")}
assert set(DSa) == set(DSb)
passed_sub = [r["id"] for r in jl(REV / "screening/v2/dual-subscription/passed-ta.jsonl")]
F["subscription"] = {"identified_by_database": pr["by_database"], "identified": pr["records_identified_subscription_databases"],
                     "removed_before_screening": {k: v for k, v in pr["removed_before_screening"].items() if not isinstance(v, dict)},
                     "new_unique_records": pr["new_unique_records"],
                     "automation_excluded_S1pp_S2pp": pr["excluded_by_automation_string_filter_S1pp_S2pp"],
                     "queue_string_pass": pr["passed_to_screening_subscription_queue"],
                     "rescue_screened_single_haiku": len(RS), "rescue_decisions": dict(collections.Counter(r["decision"] for r in RS)),
                     "rescued_queue": len(rescued_q), "automation_excluded_without_abstract_pending": len(no_abs),
                     "ta_screened_dual": len(DSa), "ta_pass_D0030": len(passed_sub),
                     "ieee_hits_by_query": ieee_hits, "ieee_not_exported": {k: ieee_hits[k] for k in ("I3", "I4", "I5") if k in ieee_hits},
                     "warnings": sorted(set(si.get("warnings", [])))}

# ---------------------------------------------------------------- title/abstract total, re-check, full text T1
ft = {r["id"]: r for r in jl(REV / "fulltext/ft-routes.jsonl")}
extra = {r["id"]: r for r in jl(SCR / "ft-routes-extra.jsonl")}
fetch = {}
for r in jl(REV / "fulltext/fetch-log.jsonl"):
    fetch[r["id"]] = r["status"]
t1 = {r["id"]: r for r in jl(SCR / "ft-t1/t1-decisions-all.jsonl")}
nr = {r["id"] for r in jl(SCR / "ft-t1/t1-not-retrieved.jsonl")}
ta_pass = v2_pass | set(passed_sub)
assert set(ft) <= ta_pass and set(t1) <= set(ft)
status = collections.Counter()
for i, r in ft.items():
    rt = r["route_type"]
    if i in t1:
        status["screened"] += 1
    elif i in nr:
        status["not_retrieved_openreview_note_missing_X6"] += 1
    elif rt == "duplicate":
        status["duplicate_of_known_record_not_sought"] += 1
    elif rt == "no_full_text":
        status["no_full_text_found"] += 1
    elif rt == "e-gateway":
        status["pending_e_gateway"] += 1
    else:
        status[f"open_access_fetch_failed_{fetch.get(i, 'not_fetched')}"] += 1
s = jload(SCR / "ft-t1/t1-summary-all.json")
ag = jload(SCR / "agreement-ft-t1.json")
grp = collections.Counter(r["group"] for r in extra.values())
F["title_abstract_total"] = {"ta_pass_free_sources": len(v2_pass), "ta_pass_subscription": len(passed_sub),
                             "ta_pass_total": len(ta_pass), "routed_in_ft_routes": len(ft),
                             "routed_later_ft_routes_extra": grp.get("ta-pass-unrouted", 0)}
F["recheck"] = {"frame": jload(SCR / "ta-recheck-sample-v1.3-frozen.json")["frame_n"],
                "sample": len(jload(SCR / "ta-recheck-sample-v1.3-frozen.json")["ids"]),
                "c8_outside_frame": len(jl(SCR / "ta-recheck-c8-candidates-v1.4.jsonl")),
                "to_full_text": grp.get("recheck-sample", 0) + grp.get("c8", 0) + grp.get("recheck-sample+c8", 0),
                "full_text_screened": sum(1 for i, r in extra.items() if r["group"] != "ta-pass-unrouted" and i in t1),
                "K": "pending (needs these records screened at full text)"}
F["full_text_T1"] = {"reports_sought": len(ft) - status["duplicate_of_known_record_not_sought"] + len(extra),
                     "status_ft_routes": dict(status),
                     "extra_routes_not_yet_retrieved": dict(collections.Counter(r["route_type"] for r in extra.values())),
                     "screened": len(t1), "screened_check": s["n"], "include": s["decision"]["include"],
                     "exclude": s["decision"]["exclude"], "exclude_codes": s["exclude_codes"],
                     "include_i1": s["include_i1"], "include_nonlang_only": s["include_nonlang_only"],
                     "adjudicated_by_C": s["adjudicated_by_C"],
                     "agreement_pass_exclude_kappa": ag["pass_vs_exclude"]["kappa"],
                     "agreement_pass_exclude_kappa_ci95": ag["pass_vs_exclude"]["kappa_ci95"],
                     "status": s["status"]}
assert F["full_text_T1"]["screened"] == s["n"] == s["decision"]["include"] + s["decision"]["exclude"]

tq = {r["id"] for r in jl(REV / "screening/v2/title-resolved-queue.jsonl")}
t1_prefix = collections.Counter(i[0] for i in t1)
F["open"] = [
    f"Free-source rescue pass: {len(r2_pos)} positives (include or unclear) of {len(R2)} were neither dual-screened nor "
    f"routed to full text ({len(r2_pos & set(A2))} in the dual batches, {len(r2_pos & set(ft))} in ft-routes); D0029 sends "
    "them to the dual queue, D0030 says they pass to full text. Needs a decision before T1 is closed.",
    f"Seed corpus: {len(v1_either)} of {len(v1)} records passed title/abstract (either screener; {len(v1_both)} both); "
    f"{sum(1 for s_ in v1_either if s_ in t1)} are in T1 (T1 ids by prefix: {dict(t1_prefix)}). Their full-text route "
    "(census reading vs criteria v1.6 full-text screening) is not in the PRISMA files; to be confirmed.",
    f"Open-access fetch failures: {sum(v for k, v in status.items() if k.startswith('open_access_fetch_failed'))} "
    "oa_url records not retrieved and not screened; need a retry or the e-gateway.",
    f"{grp.get('ta-pass-unrouted', 0)} subscription TA passes had no route in ft-routes.jsonl (now in ft-routes-extra.jsonl).",
    f"Subscription reconciliation: rescue screened {len(RS)} + without abstract {len(no_abs)} = {len(RS) + len(no_abs)} "
    f"against {pr['excluded_by_automation_string_filter_S1pp_S2pp']} string failures; dual-screened {len(DSa)} against "
    f"queue {pr['passed_to_screening_subscription_queue']} + rescued {len(rescued_q)} + title-resolved "
    f"{len(tq)} ({len(tq & set(DSa))} of the title-resolved ids are in the dual batches).",
    f"IEEE I3-I5 not exported ({sum(F['subscription']['ieee_not_exported'].values())} hits); 1,421-record "
    "Springer no-abstract set not screened; title-only lookups incomplete (D0033).",
]

(HERE / "prisma-flow.json").write_text(json.dumps(F, indent=1) + "\n", encoding="utf-8")

L = ["# PRISMA 2020 flow counts (script-generated; do not edit by hand)", "",
     "Generated by `analysis/prisma/prisma_flow.py`; every number is read from the files named there. Model screening "
     "results are before the human validation sample and author review (protocol s4): not final.", ""]
for sec, d in F.items():
    if sec == "open":
        continue
    L += [f"## {sec}", "", "| box | n |", "|---|---|"]
    for k, v in d.items():
        L.append(f"| {k} | {json.dumps(v) if isinstance(v, (dict, list)) else v} |")
    L.append("")
L += ["## open", ""] + [f"- {x}" for x in F["open"]] + [""]
(HERE / "prisma-flow.md").write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
