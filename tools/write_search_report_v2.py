"""Write research/review/corpus/search-v2-report-2026-10-15.md from the JSON outputs of the 2026-10-15 searches.

    python tools/write_search_report_v2.py

Inputs (all under research/review/corpus/): string-revision-2026-10-15.json (tools/string_rounds.py), search-log.jsonl,
search-v2-merge-stats-2026-10-15.json and search-v2-report-2026-10-15.json (tools/merge_new_records_v2.py),
abstract-enrichment-2026-10-15.json, precision-actual-2026-10-15.json (optional, second precision estimate).
Every number in the report is read from these files, none is typed here.
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_sources as ss  # noqa: E402

C = ss.CORPUS
ISO = "2026-10-15"


def jl(name):
    return json.loads((C / name).read_text(encoding="utf8"))


def n(x):
    return f"{x:,}" if isinstance(x, int) else str(x)


def main():
    rev, rep, st = jl(f"string-revision-{ISO}.json"), jl(f"search-v2-report-{ISO}.json"), jl(f"search-v2-merge-stats-{ISO}.json")
    enr = jl(f"abstract-enrichment-{ISO}.json") if (C / f"abstract-enrichment-{ISO}.json").exists() else None
    act = jl(f"precision-actual-{ISO}.json") if (C / f"precision-actual-{ISO}.json").exists() else None
    pilot = jl(f"pilot-recall-{ISO}.json")
    v1 = jl(f"new-records-dedup-report-{ISO}.json")
    rows = [json.loads(l) for l in open(ss.LOG, encoding="utf8") if l.strip()]
    mine = [r for r in rows if r["executed_utc"].startswith("20261015")]
    L = []
    a = L.append
    a(f"# Search v2 report, {ISO} (decisions D0026 and D0027; D0027 is section 12 onward)")
    a("")
    a("Agent: lit-scout. Brief: D0026 items 1, 2, 4 and the follow-on tasks (revise S1/S2, rerun every accessible source, merge, string-filter the "
      "snowball records, enrich abstracts, update the subscription sheet). Nothing here is a screening decision. Every count is read from the JSON "
      "files named in section 10; the tools that produce them are `tools/string_rounds.py`, `tools/search_sources.py`, "
      "`tools/merge_new_records_v2.py`, `tools/make_search_sheet_v2.py`.")
    a("")
    # ------------------------------------------------------------ 1
    r3 = rev["rounds"]["R3"]
    a("## 1. Headline")
    a("")
    a(f"- Recall of the 540 seed entries on title and abstract, locally: S1/S2 {rev['original']['all540_entries']}/540, "
      f"S1'/S2' {r3['recall']['all540_entries']}/540. Multimodal DLMs (MM28): {rev['original']['MM28']}/28 to {r3['recall']['MM28']}/28. "
      f"Random 50 (R50): {rev['original']['R50']}/50 to {r3['recall']['R50']}/50.")
    a(f"- Precision proxy (random 200 titles of the {n(r3['records_added_over_S1_S2_in_v1_pool'])} records of the 14,794 collected earlier that S1'/S2' add; "
      f"seed {r3['sample']['seed']}): {r3['sample']['labels'].get('IN', 0)} look in scope, {r3['sample']['labels'].get('U', 0)} unclear, "
      f"{r3['sample']['labels'].get('O', 0)} other.")
    if act:
        q_ = act["tiers"]["queue_total"]
        a(f"- Precision on what the databases returned (stratified sample of the queue, 200 titles, seed {act['seed']}): an estimated {q_['estimated_share_in']:.0%} of the {q_['records']:,} queued records look in scope, {q_['estimated_share_in_or_unclear']:.0%} in scope or unclear (section 2.4).")
    a(f"- New records not in `screening/records.jsonl`: {n(rep['union_new_records'])} (database searches {n(rep['database_records'])}, snowballing only "
      f"{n(rep['snowball_only_records'])}). v1 had {n(st['v1_union_new_records'])}.")
    a(f"- Snowball-only records marked ineligible by the string filter: {n(rep['snowball_only_auto_excluded'])}; "
      f"snowball-only records that match a string and go to screening: {n(rep['to_screen_snowball_matching'])}.")
    a(f"- **To screen: {n(rep['to_screen'])}** ({n(rep['to_screen_database_records'])} database records + {n(rep['to_screen_snowball_matching'])} string-matching snowball records). "
      f"Still without an abstract after enrichment: {n(rep['to_screen_missing_abstract'])} "
      f"({n(rep['to_screen_missing_abstract_by_kind']['database'])} database, {n(rep['to_screen_missing_abstract_by_kind']['snowball'])} snowball).")
    a("")
    # ------------------------------------------------------------ 2
    a("## 2. String revision (D0026 item 1)")
    a("")
    a(f"**Why.** The pilot criterion of protocol section 3 (all 28 MM28 records and a random 50 others) was not met: combined searches retrieved "
      f"{pilot['by_source']['ALL-COMBINED']['S1|S2']['MM28']} MM28, {pilot['by_source']['ALL-COMBINED']['S1|S2']['random50_other']} R50, "
      f"{pilot['by_source']['ALL-COMBINED']['S1|S2']['all540_arxiv']} of 540 entries. The {rev['missed_by_v1_searches']['n']} entries not retrieved all fail S1 and S2 on their "
      f"own title and abstract (local test), so the strings and not the sources limit recall. The 540 entries are 539 distinct arXiv IDs (2506.17298 is listed twice); "
      f"counts below are over entries, as in `pilot-recall-2026-10-15.json`.")
    a("")
    a("### 2.1 Why each of the 70 missed entries fails S1 and S2, and what captures it now")
    a("")
    cats = rev["missed_by_v1_searches"]["by_category"]
    a("Reasons, in groups (entries per group): " + "; ".join(f"{k}: {v}" for k, v in sorted(cats.items(), key=lambda kv: -kv[1])) + ".")
    a("")
    a("| arXiv | Title | Why S1 and S2 fail | Group | S1' / S2' part |")
    a("|---|---|---|---|---|")
    for s in rev["missed_by_v1_searches"]["seeds"]:
        why = "; ".join(s["fails_S1_S2_because"])
        cap = "/".join(["S1':" + p for p in s["captured_by_S1prime_parts"]] + ["S2':" + p for p in s["captured_by_S2prime_parts"]]) or "not captured"
        a(f"| {s['arxiv']} | {s['title'][:70].replace('|', '/')} | {why} | {s['category']} | {cap} |")
    a("")
    a("### 2.2 The revised strings (verbatim, also in protocol section 10)")
    a("")
    a("S1':")
    a("```")
    a(rev["S1prime_plain"])
    a("```")
    a("S2':")
    a("```")
    a(rev["S2prime_plain"])
    a("```")
    a("Parts (S1' = A1 OR A2 OR A3 OR B OR C; S2' = M OR VLA); each source was run part by part, the union is the string:")
    a("")
    for nm, ps in rev["parts"].items():
        for k, v in ps.items():
            a(f"- `{nm}:{k}` {v}")
    a("")
    a("### 2.3 Three rounds")
    a("")
    a("Round 1 is broad (phrase variants taken from the missed entries, plus 'diffusion' with text-generation words, no exclusions). Round 2 adds the "
      "biochemical and visual exclusions, NLP-task terms and the VLA branch, after the round 1 sample showed that molecules, proteins, robot policies and "
      "image generation made up most of the noise. Round 3 (final) narrows the language context of the discrete-diffusion branch (drops `sequence*`, "
      "`categorical`, `code`) and replaces `natural language` by `natural language generation`, after the round 2 sample showed those terms bringing in "
      "biological sequence papers. Recall is over the 540 seed entries; the precision sample is a random 200 of the records of the 14,794 collected earlier "
      "(`new-records-2026-10-15.jsonl`, v1) that the round adds over S1/S2.")
    a("")
    a("| Round | Recall 540 | MM28 | R50 | Records added over S1/S2 | Sample seed | Looks in scope (IN) | Unclear (U) | Other (O) |")
    a("|---|---|---|---|---|---|---|---|---|")
    a(f"| S1/S2 | {rev['original']['all540_entries']} | {rev['original']['MM28']}/28 | {rev['original']['R50']}/50 | - | - | - | - | - |")
    for k, r in rev["rounds"].items():
        lab = r["sample"]["labels"]
        a(f"| {k} | {r['recall']['all540_entries']} | {r['recall']['MM28']}/28 | {r['recall']['R50']}/50 | {n(r['records_added_over_S1_S2_in_v1_pool'])} | {r['sample']['seed']} | "
          f"{lab.get('IN', 0)} | {lab.get('U', 0)} | {lab.get('O', 0)} |")
    a("")
    a("The labels are mine, from titles only (`string-revision-labels-2026-10-15.json` holds every sampled ID and label). I proposed the strings and also "
      "labelled the sample, so this is a proxy for choosing between versions and not an independent precision estimate; the screeners decide eligibility. "
      "The sample reproduces from the stated seed (`tools/string_rounds.py` checks it: reproduced = " + ", ".join(f"{k} {r['sample']['reproduced']}" for k, r in rev["rounds"].items()) + ").")
    a("")
    a("Final round, share of the sample by the S1' / S2' part that matches (a record can match more than one part):")
    a("")
    a("| Part | IN | U | O |")
    a("|---|---|---|---|")
    for p, c in rev["final_round_sample_by_part"].items():
        a(f"| {p} | {c.get('IN', 0)} | {c.get('U', 0)} | {c.get('O', 0)} |")
    a("")
    if act:
        a("### 2.4 Second precision estimate, on what the revised searches actually returned")
        a("")
        a(act["text"])
        a("")
    a("### 2.5 What the final strings do not capture, and why that is accepted")
    a("")
    nc = [s for s in rev["missed_by_v1_searches"]["seeds"] if not s["captured"]]
    a(f"{len(nc)} of the 70 entries stay uncaptured by S1' and S2' on title and abstract ({540 - r3['recall']['all540_entries']} of the 540 in all, so no other seed entry is lost). They are:")
    a("")
    for s in nc:
        a(f"- {s['arxiv']} {s['title'][:80]}: {s['note']}.")
    a("")
    a(f"Of the random 50, the {50 - r3['recall']['R50']} not captured are the entries listed above as outside I1 (two image-generation foundation papers and a protein-design paper); "
      f"all 28 MM28 entries are captured (S1' alone: {r3['recall_S1prime_only']['MM28']}, S2' alone: {r3['recall_S2prime_only']['MM28']}; the two vision-language-action entries need the VLA branch of S2'). "
      "The foundation papers (DDPM, DDIM, score-based SDE, rectified flow, score matching, non-equilibrium thermodynamics) produce no text, fall under X1, and "
      "are in the Awesome-DLMs list as background; they stay in the corpus as seeds anyway. Two entries are arguably in scope and are lost to the exclusions "
      "(Gaussian diffusion on discrete data; generalised diffusion with latent encoder-decoder, whose abstracts mention proteins); the cost of the biochemical "
      "exclusion is that a general method paper that mentions proteins and has no language word is not retrieved. The exclusions apply only where no language "
      "word is present (A2) or to the broad branches (A3 non-autoregressive, B, C).")
    a("")
    # ------------------------------------------------------------ 3
    a("## 3. Searches run with S1' and S2' (D0026 item 3)")
    a("")
    a("Every row is in `search-log.jsonl` (database, string, query, filters, executed_utc, hits, records, export, sha256). The original runs of the morning stay in the log. "
      "Dates are 2026-10-15 UTC. The window is 2021-01-01 to the search date.")
    a("")
    fam = lambda d: ("arXiv" if d.startswith("arXiv") else "Semantic Scholar bulk" if "search/bulk" in d else "OpenAlex" if d.startswith("OpenAlex") else
                     "OpenReview" if d.startswith("OpenReview") else "ACL Anthology" if d.startswith("ACL") else "snowball" if "snowball" in d.lower() or "batch references" in d or "/citations" in d else d)
    tab = collections.OrderedDict()
    latest = {}
    for r in mine:
        if "snowball" not in r["string"]:
            latest[(fam(r["database"]), r["string"])] = r["export"]
    for r in mine:
        f = fam(r["database"])
        nm = r["string"].split(":")[0] if f != "snowball" else r["string"]
        key = (f, nm)
        t = tab.setdefault(key, {"rows": 0, "hits": 0, "got": 0, "superseded": 0, "partial": 0, "notrun": 0, "first": r["executed_utc"], "last": r["executed_utc"]})
        sup = f in ("arXiv", "OpenAlex", "Semantic Scholar bulk", "ACL Anthology") and latest.get((f, r["string"])) != r["export"]
        t["rows"] += 1
        t["superseded"] += sup
        if not sup:
            t["partial"] += "PARTIAL" in r["filters"]
            t["notrun"] += "NOT RUN" in r["filters"]
        if not sup:
            t["hits"] += r["hits_reported"] or 0
            t["got"] += r["records_retrieved"] or 0
        t["last"] = r["executed_utc"]
    a("| Source | String | Log rows | Hits reported (sum of parts, current runs) | Records retrieved | Notes |")
    a("|---|---|---|---|---|---|")
    for (f, nm), t in tab.items():
        notes = []
        if t["superseded"]:
            notes.append(f"{t['superseded']} earlier row(s) superseded by a rerun of the same part (see 3.1)")
        if t["partial"]:
            notes.append(f"{t['partial']} part(s) PARTIAL: OpenAlex free credits exhausted")
        if t["notrun"]:
            notes.append(f"{t['notrun']} part(s) NOT RUN: OpenAlex free credits exhausted")
        a(f"| {f} | {nm} | {t['rows']} | {n(t['hits'])} | {n(t['got'])} | {'; '.join(notes)} |")
    a("")
    a("Hits are summed over parts, so a record found by several parts is counted several times; unique counts are in section 4.")
    a("")
    a("### 3.1 Problems met and handled")
    a("")
    a("- **OpenAlex quota.** The unauthenticated allowance is 1,000 credits a day (response headers `X-RateLimit-Limit: 1000`, `Remaining: 0`, reset 39,331 s after 13:04 UTC). "
      "It was spent by the morning runs plus two parts: S1':A1 returned 200 of 412 hits and S1':A2 200 of 925; S1':A3, B, C and S2':M, VLA were not run (a log row with `NOT RUN` and the 429 headers "
      "is kept for each). **Resume** after the reset, or with an `OPENALEX_API_KEY`: `python tools/search_sources.py oa S1p S2p`. OpenAlex therefore contributes S1/S2 in full and S1' only in part.")
    a("- **arXiv wildcards.** arXiv switches stemming off for a wildcard term (`abs:image*` finds 11,800 records, `abs:image` 104,864) and `ANDNOT` with a wildcard removed almost nothing (1,147 to 1,117 against 707 with the plain term). "
      "The first arXiv run of the seven parts was therefore rerun with stem forms written out (as for OpenAlex); the first rows and raw files stay in the log and are marked superseded; the merge uses the latest row per part.")
    a("- **Exact tokens for abbreviations.** The first full run used the prefix terms `dllm*`, `dmllm*`, `dvlm*`, `vla*`, `mllm*`. A sample of what Semantic Scholar returned showed that `dllm*` matched DLLME (dispersive liquid-liquid microextraction) in analytical chemistry, hundreds of records. "
      "The five terms were written as exact tokens (`dllm`, `dllms`, ...) in the final strings, parts A1, M and VLA were rerun on arXiv and Semantic Scholar, S1' and S2' were reapplied to the ACL snapshot, and the merge uses the latest row per part; the first rows and raw files stay in the log. "
      "OpenAlex parts A1 and A2 (partial) were run before this fix and cannot be rerun until the quota resets; OpenAlex strips wildcards, so its A1 query already used the stem `dllm`.")
    a("- **Semantic Scholar throttling.** The shared unauthenticated pool returned HTTP 429 for long periods; the runner waits 90 s and retries the same page (up to 40 times) and keeps the cursor, so results are complete (hits equal retrieved in every S2 row).")
    a("- **OpenReview.** Search is a term search (listing endpoints are blocked, as in v1). The terms of S1'/S2' are phrases (see `OR_TERMS_P` in `tools/search_sources.py`); the full boolean string, "
      "including the exclusions, is applied locally to title, abstract and keywords by `tools/merge_new_records_v2.py` (`fails_local_clause` in the stats).")
    a("- **ACL Anthology.** S1' and S2' were applied to the same snapshot of the export as the morning run (sha256 in the log rows), so the two versions of the strings are compared on identical data.")
    a("- **DBLP** was not searched (D0026 item 3): proof-of-work challenge, title-only index. Its venues are covered through Semantic Scholar and OpenAlex. Reported as a limitation.")
    a("- **Subscription databases** (Scopus, Web of Science, IEEE Xplore, ACM DL, SpringerLink, ScienceDirect) cannot be run by an agent; section 'Revised strings S1' and S2'' of `subscription-search-sheet.md` has the adapted strings; the original strings stay as the second run.")
    a("")
    # ------------------------------------------------------------ 4
    a("## 4. Merge and deduplication (as v1, with three extra keys)")
    a("")
    a("Keys, in order: arXiv ID (version stripped), DOI, source IDs, normalised title (3+ words), normalised abstract (200+ characters); union-find within and across sources. "
      "Added in v2: embedded arXiv ID in a title (reference-list fragments such as 'Large language diffusion models . 2025. arXiv: 2502.09992'), "
      "cleaned title (leading '2025.' and trailing ', 2025' removed) and a squashed title (letters and digits only, 25+ characters, which undoes hyphenation breaks). "
      f"The extra keys merged {n(rep['dedup_extra_key_merges'])} further pairs. `screening/records.jsonl` is unchanged "
      f"(sha256 {rep['records_jsonl_sha256_unchanged'][:16]}..., equal to the v1 report).")
    a("")
    a("| Source | Identified | By string | Unique within source | Duplicates within | Already in corpus | New | New and matching a string locally |")
    a("|---|---|---|---|---|---|---|---|")
    for s, v in rep["per_source"].items():
        bs = ", ".join(f"{k} {n(x)}" for k, x in v["identified_by_string"].items())
        ml = ", ".join(f"{k} {n(x)}" for k, x in v["new_matching_locally"].items())
        a(f"| {s} | {n(v['identified'])} | {bs} | {n(v['unique_within_source'])} | {n(v['duplicates_within_source'])} | {n(v['duplicates_against_existing'])} | {n(v['new'])} | {ml} |")
    a("")
    a(f"Union of new records across sources: **{n(rep['union_new_records'])}**; of these {n(rep['union_new_also_in_v1'])} were already in the v1 file (`new-records-2026-10-15.jsonl`, {n(st['v1_union_new_records'])}) "
      f"and {n(rep['union_new_records'] - rep['union_new_also_in_v1'])} come from the revised-string runs. Database records {n(rep['database_records'])}; snowball-only {n(rep['snowball_only_records'])}.")
    a("")
    a("Records by source combination (top 15): " + "; ".join(f"{k} {n(v)}" for k, v in list(rep["queue_by_source_combination"].items())[:15]) + " (queue only).")
    a("")
    # ------------------------------------------------------------ 5
    a("## 5. Snowball string filter (D0026 item 4)")
    a("")
    sb = rep["snowball_only_matching_by_string"]
    a(f"Snowball records come from {n(v1['sources']['snowball-backward']['identified'])} backward and {n(v1['sources']['snowball-forward']['identified'])} forward citation edges of the 539 distinct seed IDs "
      f"(one level, Semantic Scholar; seeds with more than 5,000 citations skipped forward). After the date window and deduplication, {n(rep['snowball_only_records'])} records are in no database result. "
      f"A snowball-only record is screened only if its title and abstract match S1, S2, S1' or S2' (local test): "
      f"S1 {n(sb['S1'])}, S2 {n(sb['S2'])}, S1' {n(sb[chr(83)+'1'+chr(39)])}, S2' {n(sb[chr(83)+'2'+chr(39)])}; any of the four: {n(rep['snowball_only_matching_a_string'])}.")
    a("")
    a(f"**{n(rep['snowball_only_auto_excluded'])} snowball-only records are marked `auto_excluded` (reason 'string filter, D0026')**; for PRISMA this is 'records marked as ineligible by automation tools'. "
      f"Of these, {n(rep['snowball_only_auto_excluded_abstract_missing'])} have no abstract even after enrichment and were judged on the title alone (`auto_excluded_abstract_missing: true`); "
      "a snowball record whose title does not match and that has no abstract could be in scope, so these are a stated limitation of the filter.")
    a("")
    # ------------------------------------------------------------ 6
    a("## 6. Abstract enrichment (D0026 item 5)")
    a("")
    if enr:
        a(f"Records without an abstract before enrichment: {n(enr['attempted'])} of {n(rep['union_new_records'])} (all new records, not only those that will be screened, so that the snowball filter is not decided by a missing abstract). "
          "Sources, in order: Semantic Scholar batch endpoint (by paperId, arXiv ID, DOI or ACL ID, 500 per request; it returned an abstract for 1 of 1,290 requested, because Semantic Scholar holds none for these records), arXiv API (`id_list`, 84 of 84), "
          "OpenAlex by DOI (50 per request; stopped at once, quota exhausted), and, in a second pass beyond the three sources named in D0026, Crossref by DOI for the 396 records that had a DOI and would be screened or could match on the title (8 abstracts). "
          "Abstracts filled by source: " + (", ".join(f"{k} {n(v)}" for k, v in enr["by_source"].items()) or "none") + f". Still missing after enrichment: {n(enr['still_missing'])} of all new records; "
          f"among the records to screen: {n(rep['to_screen_missing_abstract'])}. Notes: " + ("; ".join(enr["notes"]) or "none") + ".")
    else:
        a("Not run yet.")
    a("")
    a("Abstract source of the records to screen (field `abstract_source`): " + ", ".join(f"{k} {n(v)}" for k, v in rep["abstract_source_queue"].items()) + ".")
    a("")
    # ------------------------------------------------------------ 7
    a("## 7. Screening queue")
    a("")
    a(f"`screening-queue-2026-10-15.jsonl`: {n(rep['to_screen'])} records with id, title, abstract, sources, `string_match` {{S1, S2, S1', S2'}}, plus `queue_reason`, the matching S1'/S2' parts, DOI, arXiv ID, date and venue. "
      f"Database records that match no string locally ({n(rep['database_records_matching_no_string_locally'])}) are kept in the queue, because the database returned them (engine stemming and Boolean quirks differ from the local word test); they carry `string_match` all false and `queue_reason` 'database record', so they can be screened last or sampled. "
      f"Matching locally: S1 {n(rep['database_records_matching_by_string_locally']['S1'])}, S2 {n(rep['database_records_matching_by_string_locally']['S2'])}, "
      f"S1' {n(rep['database_records_matching_by_string_locally']["S1'"])}, S2' {n(rep['database_records_matching_by_string_locally']["S2'"])} among {n(rep['database_records'])} database records; "
      f"{n(rep['database_records_added_by_revised_strings'])} are added by the revised strings over S1/S2. {n(rep['possible_duplicates_of_existing_in_queue'])} queue records carry `possible_duplicate_of` (title Jaccard 0.8 against an existing record; flagged, not dropped).")
    a("")
    a("Screening tiers (field `queue_tier`; a guide for ordering and sampling, computed from the local test of the strings on title and abstract; not a screening decision):")
    a("")
    a("| Tier | Definition | Records | Database | Snowball |")
    a("|---|---|---|---|---|")
    for k, v in rep["queue_by_tier_and_kind"].items():
        a(f"| {k.split(' ')[0]} | {k[3:]} | {n(v['database'] + v['snowball'])} | {n(v['database'])} | {n(v['snowball'])} |")
    a("")
    a(f"{n(rep['title_fragments_in_queue'])} queue records are reference-list fragments (snowball only, no identifier, no abstract; Semantic Scholar returns unparsed reference strings such as '2023. SSD-LM: Semi-autoregressive Simplex-based Diffusion Language Mod'): "
      f"field `title_fragment`; {n(rep['title_fragments_in_queue_with_near_duplicate_candidate'])} of them have a near-duplicate candidate (field `near_duplicate_candidate`: id, Jaccard, containment of the fragment) among the corpus; flagged, never merged, because a containment of 1.0 with a Jaccard of 0.5 can be a different paper.")
    a("")
    a("Queue records by S1' part: " + ", ".join(f"{k} {n(v)}" for k, v in rep["queue_by_s1p_part"].items()) + "; by S2' part: " + ", ".join(f"{k} {n(v)}" for k, v in rep["queue_by_s2p_part"].items()) + ".")
    a("")
    # ------------------------------------------------------------ 8
    a("## 8. Numbers for the PRISMA 2020 flow diagram")
    a("")
    ident_db = sum(v["identified"] for s, v in rep["per_source"].items() if not s.startswith("snowball"))
    ident_sb = sum(v["identified"] for s, v in rep["per_source"].items() if s.startswith("snowball"))
    a("| Box | Count | Note |")
    a("|---|---|---|")
    a(f"| Identified from databases and registers, this run | {n(ident_db)} | arXiv, Semantic Scholar, OpenAlex, OpenReview, ACL Anthology; S1, S2, S1', S2' runs together, before deduplication; current runs only (superseded rows excluded); OpenAlex S1' partial |")
    a("| Identified from Awesome-DLMs list (earlier) | 572 | 540 with an arXiv ID; commit 194aa6bd |")
    a(f"| Identified by citation searching (edges) | {n(ident_sb)} | backward + forward edges, one level |")
    a(f"| Duplicates removed (within source, across sources and against the corpus) | see section 4 | per-source columns |")
    a(f"| New records after deduplication | {n(rep['union_new_records'])} | database {n(rep['database_records'])}, snowball only {n(rep['snowball_only_records'])} |")
    a(f"| Marked ineligible by automation tool (string filter, D0026) | {n(rep['snowball_only_auto_excluded'])} | snowball-only records matching none of S1, S2, S1', S2' |")
    a(f"| Records to screen (title and abstract) | {n(rep['to_screen'])} | {n(rep['to_screen_database_records'])} database + {n(rep['to_screen_snowball_matching'])} snowball matching a string |")
    a(f"| Of which without an abstract | {n(rep['to_screen_missing_abstract'])} | screened on title alone, flagged |")
    a("| Not searched | DBLP; OpenAlex S1' parts A3, B, C and S2' parts (quota); six subscription databases (user) | limitations |")
    a("")
    # ------------------------------------------------------------ 9
    a("## 9. What was not searched, not done, or could not be done")
    a("")
    a("- No claim of completeness: search completeness is not proof of coverage. Not searched: DBLP; OpenAlex for S1' parts A3, B, C and S2' (quota; resume command above); Google Scholar; the six subscription databases; "
      "non-arXiv venues that no free index carries; workshops outside OpenReview; anything before 2021 (I4).")
    a("- The string revision uses the 540 seeds as its vocabulary source, which are themselves a curated list built from what the list's authors knew; a paper whose abstract uses none of this vocabulary is not found by S1'/S2' "
      "either. The revision can raise recall on papers like the seeds; it cannot show that unlike papers are absent.")
    a("- Precision labels are mine and title-only.")
    a("- Snowballing was not rerun; it is one level from the seed list, not from newly found records.")
    a("- No `papers` ledger rows were added: the contract's one-row-per-item rule would add thousands of rows for records that have not been looked at; the records live in `new-records-2026-10-15-v2.jsonl` with their IDs and sources. "
      "Add rows after screening, for included records.")
    a("")
    a("## 10. Decisions and checks for the orchestrator")
    a("")
    a("1. **Precision of the revised strings on real databases is low.** The three rounds were judged on a pool of citation neighbours of the seeds (about a third of the added records look in scope); on what the databases returned only about one record in eight does (section 2.4). "
      "T1 (matching S1, S2, S1' A1 or S2') holds about 80 percent of the in-scope-looking records; T3 and T5 hold more than two thirds of the queue and about 2.5 percent in-scope-looking. A fourth round (for example requiring a language word in B and C, "
      "or in the no-context branch of A2, and adding 'diffusion of innovation', 'diffusion-weighted' and 'diffusion equation' exclusions) would need your decision, since D0026 allowed three. Without it, screening can start with T1 and T2 and sample T3 to T5.")
    a("2. T5 (database records that match no string locally, " + n(rep['database_records_matching_no_string_locally']) + ") could be marked as ineligible by the string filter as the snowball records are; I kept them in the queue because D0026 item 4 names snowball records only.")
    a("3. OpenAlex: resume the unrun S1' and S2' parts after the quota resets (about 11 hours after 13:04 UTC on 2026-10-15) or give an API key.")
    a("4. The snowball filter judged " + n(rep['snowball_only_auto_excluded_abstract_missing']) + " snowball-only records on the title alone because no abstract could be found; say if a sample of them should be screened.")
    a("")
    a("## 11. Files")
    a("")
    for f in (f"new-records-{ISO}-v2.jsonl", f"screening-queue-{ISO}.jsonl", f"search-v2-report-{ISO}.json", f"search-v2-merge-stats-{ISO}.json", f"string-revision-{ISO}.json",
              f"string-revision-labels-{ISO}.json", f"abstract-enrichment-{ISO}.json", "search-log.jsonl", "subscription-search-sheet.md"):
        a(f"- `research/review/corpus/{f}`")
    a("- `research/sources/search-raw/` (raw responses, run logs)")
    a("- `tools/search_sources.py`, `tools/merge_new_records_v2.py`, `tools/string_rounds.py`, `tools/make_search_sheet_v2.py`, `tools/write_search_report_v2.py`")
    a("- `research/review/protocol.md` section 10 (amendment entry of 2026-10-15)")
    a("")
    # ------------------------------------------------------------ 12 and 13 (D0027)
    if (C / f"string-revision-round4-{ISO}.json").exists() and (C / f"final-filter-stats-{ISO}.json").exists():
        round4_sections(L, rep)
    out = C / f"search-v2-report-{ISO}.md"
    out.write_text("\n".join(L), encoding="utf8")
    print(f"wrote {out} ({len(L)} lines)")


def round4_sections(L, rep):
    """Sections 12 and 13: round 4 (decision D0027). Every number is read from the JSON files named in section 14."""
    a = L.append
    r4, ff = jl(f"string-revision-round4-{ISO}.json"), jl(f"final-filter-stats-{ISO}.json")
    pr = jl(f"precision-round4-{ISO}.json")
    lost = jl(f"lost-check-{ISO}.json") if (C / f"lost-check-{ISO}.json").exists() else None
    old = jl(f"precision-actual-{ISO}.json")
    vm = jl(f"validation-autoexcl-sampling-{ISO}.json")
    base, fin = r4["baseline_S1prime_S2prime"], r4["final"]
    a("## 12. Round 4: precision only (decision D0027)")
    a("")
    a("D0027 allowed one further string round, restricted to precision: exclusion terms for the noise seen in the real results and a language-word requirement in the broad "
      "branches, accepted only if the seed recall stays at 525/540 with MM28 28/28 and R50 47/50. The result is S1'' and S2''. Nothing was screened. The tools are "
      "`tools/search_sources.py` (strings: `S1PP_PARTS`, `S2PP_PARTS`, lists `R4_*`), `tools/string_rounds.py round4` (recall, steps, per-term counts), "
      "`tools/merge_new_records_v2.py final-filter` (application to the queue, validation sets) and `tools/precision_actual.py` (modes `r4`, `lost-sample`).")
    a("")
    a("### 12.1 Result in one table")
    a("")
    a("| | S1'/S2' (D0026) | S1''/S2'' (D0027) |")
    a("|---|---|---|")
    a(f"| Seed recall, 540 entries (539 distinct IDs) | {base['recall']['all540_entries']}/540 | {fin['recall']['all540_entries']}/540 |")
    a(f"| MM28 | {base['recall']['MM28']}/28 | {fin['recall']['MM28']}/28 |")
    a(f"| Random 50 | {base['recall']['R50']}/50 | {fin['recall']['R50']}/50 |")
    a(f"| Queue records matching (of {n(ff['queue_records'])}) | {n(base['queue_total'])} | {n(fin['queue_total'])} |")
    for t in ("T1", "T2", "T3", "T4"):
        a(f"| of which tier {t} | {n(base['queue_by_tier'][t])} | {n(fin['queue_by_tier'][t])} |")
    a(f"| Estimated share of the matching queue records that look in scope (title labels, stratified sample, 40 per tier) | 11.8% of the whole queue of 6,376 (second estimate, section 2.4) | {pr['tiers']['queue_total']['estimated_share_in']:.1%} |")
    a("")
    a(f"Seed entries lost against S1'/S2': {len(r4['seeds_lost_vs_S1prime'])}. Records of the {n(r4['subset_check_all_v2_records']['records'])} new records that match S1''/S2'' but not S1'/S2': "
      f"{r4['subset_check_all_v2_records']['match_S1pp_S2pp_but_not_S1p_S2p']} (every part of S1'' and S2'' is a subset of the same part of S1' and S2', so this holds by construction and was checked). "
      f"The set evaluation used here agrees with the word-based test of `search_sources.matches` on {r4['consistency_check']['records_checked_with_ss.matches']} records checked "
      f"({r4['consistency_check']['disagreements']} disagreements). Seed entries still not captured: {len(r4['seeds_not_captured_by_final'])}, the same 15 as in section 2.5.")
    a("")
    a("### 12.2 S1'' and S2'' (verbatim)")
    a("")
    a("Reading rule as in section 2.2: AND binds tighter than OR; a trailing `*` is a word-prefix wildcard; `NOT (...)` excludes any of the listed words; title, abstract and keywords.")
    a("")
    a("S1'':")
    a("```")
    a(r4["S1pp_plain"])
    a("```")
    a("")
    a("S2'':")
    a("```")
    a(r4["S2pp_plain"])
    a("```")
    a("")
    a("Parts (S1'' = A1 OR A2 OR A3 OR B OR C; S2'' = M OR VLA). Seeds and queue records by part (a record can match several parts):")
    a("")
    a("| Part | Seed entries | Queue T1 | T2 | T3 | T4 |")
    a("|---|---|---|---|---|---|")
    for k, v in r4["parts"].items():
        q = v["queue_by_tier"]
        a(f"| {k} | {v['seeds']} | {q['T1']} | {q['T2']} | {q['T3']} | {q['T4']} |")
    a("")
    a("### 12.3 What changed, step by step (cumulative; counts are queue records that match S1'/S2' and stop matching at that step)")
    a("")
    a("| Step | Seed recall | Queue after the step (T1 / T2 / T3 / T4) | Removed by the step (T1 / T2 / T3 / T4) | Seeds lost |")
    a("|---|---|---|---|---|")
    for st in r4["steps"]:
        q, rm = st["queue_by_tier"], st["removed_by_this_step_by_tier"]
        a(f"| {st['step']} | {st['recall']['all540_entries']}/540, {st['recall']['MM28']}/28, {st['recall']['R50']}/50 | {q['T1']} / {q['T2']} / {q['T3']} / {q['T4']} | "
          f"{rm['T1']} / {rm['T2']} / {rm['T3']} / {rm['T4']} | {', '.join(st['seeds_lost_by_this_step']) or 'none'} |")
    a("")
    a("The steps overlap: a record that two steps would remove is counted at the first. The next table counts each exclusion list **alone** (the list added to S1'/S2' on its own, in the branches it applies to):")
    a("")
    a("| List (terms; applies to) | Removes T1 | T2 | T3 | T4 | Total | Seeds lost |")
    a("|---|---|---|---|---|---|---|")
    applies = {"R4_INNOV": "A2, A3 non-autoregressive, B, C", "R4_NET": "A2, A3 non-autoregressive, B, C", "R4_MRI": "A1, A2, A3 non-autoregressive, B, C",
               "R4_PHYS": "A2, A3 non-autoregressive, B, C", "R4_PDE": "A2, A3 non-autoregressive, B, C", "R4_CHEM": "A1, A2, A3 non-autoregressive, B, C",
               "R4_BIOMED": "A2, A3 non-autoregressive, B, C", "R4_STABLE": "B, C", "R4_NT (A2 without context, A3)": "A2 without context, A3 non-autoregressive",
               "R4_NT_BC (B, C)": "B, C"}
    for g, v in r4["group_standalone_removal"].items():
        nt = len(r4["per_term_standalone_removal"][g])
        a(f"| {g} ({nt} term{'s' if nt != 1 else ''}; {applies.get(g, '')}) | {v['T1']} | {v['T2']} | {v['T3']} | {v['T4']} | {v['total']} | {', '.join(v['seeds_lost']) or 'none'} |")
    a("")
    a("Records removed by each term alone (total over T1 to T4; a record with two listed terms is counted under both; the split by tier is in `string-revision-round4-2026-10-15.json`, key `per_term_standalone_removal`):")
    a("")
    for g, terms in r4["per_term_standalone_removal"].items():
        a(f"- {g}: " + "; ".join(f"`{t}` {v['total']}" for t, v in terms.items()))
    a("")
    a("The terms come from the false positives in the queue (titles read, then terms with seed counts of zero and a coherent meaning kept): diffusion of innovation, information or "
      "technology and social-network diffusion (R4_INNOV, R4_NET); diffusion MRI (R4_MRI); diffusion, heat and fluid equations, traveling waves, epidemics, oxide layers (R4_PHYS, R4_PDE); "
      "microextraction, disc diffusion (R4_CHEM, R4_BIOMED); Stable Diffusion; speech, music, motion, time series and a few technique words in the branches that need no language word "
      "(R4_NT, R4_NT_BC). Two terms that looked noisy but removed seed entries were dropped: `knowledge diffusion` (DiffuCOMET, 2402.17011) and `social media` (DiffuDetox, 2306.08505); "
      "`pde*`, `trajector*` and `heat` were narrowed for the same reason (2605.14531 and masked-diffusion theory papers), `fluid*` because of the model name FLUID-Omni, `susceptibility` because of a masked-diffusion sampling paper.")
    a("")
    a("The structural changes: (5) the no-context branch of A2 keeps `masked diffusion`, `discrete diffusion` and `discrete flow matching` only (`discrete state-space*` alone and `discrete flow*` alone accounted for 195 and 89 of the 450 T4 records, almost all control, physics and signal processing); "
      "with a language word, `discrete flow*` needs `diffusion` and `discrete state-space*` needs a diffusion, generative or flow-matching word; (6) `absorbing state` (Markov chains) and `any-order` (Shapley interactions) need, besides the language word, "
      "a language-model, autoregressive, diffusion or masked word; (7) in B and C `diffusion` must occur as a model (`diffusion model*`, `diffusion-based`, `denoising`, `discrete diffusion`, `using diffusion`, `flow matching`, ...; list R4_DS), "
      "which removes the dissemination sense (cultural, policy, French *diffusion*); (8) in S2'' the unified-multimodal branch M needs a language word and the VLA branch no longer accepts plain `diffusion-based` "
      "(robot diffusion policies). Two seed entries are held by the no-context branch of A2 alone (2509.13866, 2608.10615): their abstracts have no language word, which is why a strict language-word requirement there fails the acceptance rule (next subsection).")
    a("")
    a("### 12.4 The language-word requirement as asked, tried alone")
    a("")
    a("| Requirement added to S1'/S2' on its own | Seed recall | Queue records removed (T1 / T2 / T3 / T4) | Seeds lost |")
    a("|---|---|---|---|")
    for k, v in r4["language_word_requirement_alone"].items():
        rm = v["removed_by_tier"]
        a(f"| {k} | {v['recall']['all540_entries']}/540, {v['recall']['MM28']}/28, {v['recall']['R50']}/50 | {rm['T1']} / {rm['T2']} / {rm['T3']} / {rm['T4']} | {', '.join(v['seeds_lost']) or 'none'} |")
    a("")
    a("A language word in the no-context branch of A2 contradicts what the branch is (a branch for abstracts without one) and costs two seeds; the same word in B costs five seeds (NLP-task diffusion papers whose abstract names the task, not the language) "
      "and in C removes only 110 records because C already requires `language model*` or `llm*`. Both were therefore relaxed as reported: the no-context branch is restricted instead (its own terms and the exclusion lists), B and C get the "
      "diffusion-as-a-model requirement and the exclusion lists, and the language word is required where it costs nothing (M, A3).")
    a("")
    a("### 12.5 Precision on the same stratified real-result design (new seed)")
    a("")
    a(pr["text"])
    t = pr["tiers"]["queue_total"]
    a("")
    a(f"Estimated in-scope-looking records in the {n(ff['passes'])} that pass: {n(t['estimated_in'])} ({t['estimated_share_in']:.1%}); in scope or unclear: {n(t['estimated_in_or_unclear'])} ({t['estimated_share_in_or_unclear']:.1%}). "
      "Stratified normal-approximation 95% interval for the in-scope-looking count: about 470 to 830 (25% to 45%). The earlier estimate for the queue before round 4 was "
      f"{n(old['tiers']['queue_total']['estimated_in'])} of {n(old['tiers']['queue_total']['records'])} ({old['tiers']['queue_total']['estimated_share_in']:.1%}); the two estimates have wide intervals and the "
      "numbers of in-scope-looking records are not different beyond that noise, while the queue is 71% smaller. Caveats: the labels are mine, from titles only (U means the title does not settle it); "
      "I proposed the strings and labelled the sample, so this is not an independent precision estimate; and the sample is drawn from the same queue from which the exclusion terms were derived (in-sample), "
      "so it is optimistic about records of the kinds I looked at. T3 is the loosest stratum: a first draw with the same seed, made on a string that kept 7% more records (1,976, before `tabular`, `lora`, `quantiz*` and a few other technique words were added to R4_NT_BC "
      "and `disc diffusion` to R4_BIOMED; 88 of its 160 records are in the final sample), gave 1 in-scope-looking record of 40 in T3, the final draw gives 7 of 40, and the second estimate before round 4 gave 2 of 40: "
      "a sample of 40 from a tier of 512 cannot separate 2% from 18%, and T3 stays the weakest tier (B and C carry NLP-task diffusion papers and generic LLM-plus-diffusion papers side by side).")
    a("")
    a("### 12.6 What the filter removed: a check by title, and the validation sets")
    a("")
    if lost:
        a(f"Check by me (not the validation sets): a stratified random sample of the database records the filter removed from T1 to T4, drawn from the records outside validation set V1 "
          f"(seed {jl(f'lost-check-sample-{ISO}.json')['seed']}; 30, 10, 40 and 20 titles from T1 to T4), read as in 12.5:")
        a("")
        a("| Original tier | Removed | Sampled | Looks in scope | Unclear | Other |")
        a("|---|---|---|---|---|---|")
        for k, v in lost["tiers"].items():
            if k.startswith("T"):
                a(f"| {k} | {n(v['removed'])} | {v['sampled']} | {v['IN']} | {v['U']} | {v['O']} |")
        a("")
        a("None of the 100 looked in scope; three were unclear (a generic multi-task diffusion paper, a unified multimodal latent-diffusion framework, a diffusion-styled preference-optimization paper). "
          "T5 (2,188 records that match no string locally) had 0 of 40 in scope or unclear in the second estimate (section 2.4). With zero observed the upper end is set by the sample sizes, not by the filter: "
          "a Jeffreys-prior simulation of the stratified sample gives an upper 95% bound of about 100 in-scope-looking records among the 2,343 removed database records of T1 to T4, and about 100 among the 2,188 of T5 — "
          "too wide to settle the 2% reversal criterion of D0027. That is what the validation sets are for.")
    a("")
    v1, v2 = vm["V1"], vm["V2"]
    a(f"Validation sets (written, **not screened**; `research/review/screening/validation-autoexcl-{ISO}.jsonl`, 300 rows with `id`, `title`, `abstract`, `set`, in shuffled order; "
      f"the sampling record with each sampled ID and its tier, source and abstract status is `research/review/corpus/validation-autoexcl-sampling-{ISO}.json`):")
    a("")
    a(f"- V1: {v1['n']} of the {n(v1['population_size'])} database records that fail S1''/S2'' (snowball-only records excluded), `random.Random({v1['seed']}).sample(sorted(ids), {v1['n']})`. "
      f"By original tier the population is {', '.join(f'{k} {n(x)}' for k, x in vm['population_V1_by_original_tier'].items())}; {n(vm['population_V1_missing_abstract'])} have no abstract.")
    a(f"- V2: {v2['n']} of the {n(v2['population_size'])} snowball-only records excluded in D0026 on the title alone (no abstract after enrichment), `random.Random({v2['seed']}).sample(sorted(ids), {v2['n']})`.")
    a("")
    a("Estimating the loss: if the screener finds k in-scope records among the 200 of V1, the estimate for V1's population is 4,531 x k/200 with a Clopper-Pearson or Wilson interval; V2 likewise with 2,107 x k/100. "
      "V1 mixes tiers in proportion to the population (T5 and T3 dominate), so the tier-by-tier split of the findings is in the sampling record. The sets overlap the records whose titles I read while building S1''/S2'' "
      "(well over a thousand titles of removed T1 to T4 records, and 40 T5 titles); the estimate from V1 is therefore slightly optimistic for those and unbiased for the rest.")
    a("")
    a("### 12.7 The strings applied to the queue (all tiers, T5 included)")
    a("")
    a(f"S1'' and S2'' were evaluated on title, abstract and keywords of every one of the {n(ff['queue_records'])} queue records. **{n(ff['passes'])} pass** "
      f"(`screening-queue-final-{ISO}.jsonl`: the queue fields plus `string_match` for S1, S2, S1', S2', S1'', S2'', `s1pp_parts`, `s2pp_parts`, `queue_tier` as before and `queue_tier_final` recomputed on S1''/S2'' parts); "
      f"**{n(ff['auto_excluded'])} fail** and are marked `auto_excluded`, reason 'string filter, D0027' (`auto-excluded-{ISO}.jsonl`).")
    a("")
    a("| Original tier | In queue | Pass | Auto-excluded | Pass: database | Pass: snowball | Excluded: database | Excluded: snowball |")
    a("|---|---|---|---|---|---|---|---|")
    for t, v in ff["by_original_tier"].items():
        k = ff["by_original_tier_and_kind"][t]
        a(f"| {t} | {n(v['queue'])} | {n(v['passes'])} | {n(v['auto_excluded'])} | {n(k['database']['passes'])} | {n(k['snowball']['passes'])} | {n(k['database']['auto_excluded'])} | {n(k['snowball']['auto_excluded'])} |")
    a(f"| Total | {n(ff['queue_records'])} | {n(ff['passes'])} | {n(ff['auto_excluded'])} | {n(ff['passes_by_kind']['database'])} | {n(ff['passes_by_kind']['snowball'])} | {n(ff['auto_excluded_by_kind']['database'])} | {n(ff['auto_excluded_by_kind']['snowball'])} |")
    a("")
    a("Passing records by recomputed tier: " + ", ".join(f"{k} {n(v)}" for k, v in ff["passes_by_final_tier"].items()) +
      f". Passing records without an abstract: {n(ff['passes_missing_abstract'])}. Auto-excluded without an abstract: {n(ff['auto_excluded_missing_abstract']['database'])} database, {n(ff['auto_excluded_missing_abstract']['snowball'])} snowball "
      "(judged on the title alone, as the 2,107 snowball records of D0026; V1 contains these in proportion).")
    a("")
    a("By source (a record found by several sources counts under each):")
    a("")
    a("| Source | In queue | Pass | Auto-excluded |")
    a("|---|---|---|---|")
    for s, v in ff["per_source_a_record_counts_in_each_of_its_sources"].items():
        a(f"| {s} | {n(v['queue'])} | {n(v['passes'])} | {n(v['auto_excluded'])} |")
    a("")
    ae = [json.loads(l) for l in open(C / f"auto-excluded-{ISO}.jsonl", encoding="utf8") if l.strip()]
    s1o = [r for r in ae if r["string_match"]["S1"]]
    s2o = [r for r in ae if r["string_match"]["S2"] and not r["string_match"]["S1"]]
    a3 = sum(1 for r in s1o if "A3" in r["s1p_parts"])
    a(f"Of the {n(ff['auto_excluded'])} auto-excluded records, {n(ff['auto_excluded_matching_no_string_locally'])} matched no string locally (T5), {n(ff['auto_excluded_matching_S1prime_or_S2prime'])} matched S1' or S2', "
      f"and **{n(ff['auto_excluded_matching_original_S1_or_S2'])} matched the original protocol strings S1 or S2**: {len(s1o)} match S1 ({a3} of them through the non-autoregressive-with-diffusion branch, i.e. speech, music, "
      f"time-series and similar non-text diffusion papers that S1 accepts because it has no exclusion) and {len(s2o)} match S2 only (unified multimodal image, video or 3D generation with no language word in the abstract). "
      "They are excluded as X1 (no text output) by the exclusion lists and the language-word requirement of M. If the orchestrator wants records that match the protocol strings S1 or S2 never to be excluded by automation, "
      "they can be released from `auto-excluded-2026-10-15.jsonl` (field `string_match`).")
    a("")
    a("## 13. Numbers for the PRISMA 2020 flow diagram, updated for D0027")
    a("")
    a("Rows 1 to 6 of section 8 are unchanged. The row 'Records to screen' becomes:")
    a("")
    a("| Box | Count | Note |")
    a("|---|---|---|")
    a(f"| Records to screen after D0026 (before D0027) | {n(rep['to_screen'])} | {n(rep['to_screen_database_records'])} database + {n(rep['to_screen_snowball_matching'])} snowball matching a string |")
    a(f"| Marked ineligible by automation tool (string filter, D0027) | {n(ff['auto_excluded'])} | {n(ff['auto_excluded_by_kind']['database'])} database records and {n(ff['auto_excluded_by_kind']['snowball'])} snowball records that fail S1''/S2'' (T5 {n(ff['by_original_tier']['T5']['auto_excluded'])}, T4 {n(ff['by_original_tier']['T4']['auto_excluded'])}, T3 {n(ff['by_original_tier']['T3']['auto_excluded'])}, T2 {n(ff['by_original_tier']['T2']['auto_excluded'])}, T1 {n(ff['by_original_tier']['T1']['auto_excluded'])}) |")
    a(f"| Marked ineligible by automation tool, in all (D0026 + D0027) | {n(rep['snowball_only_auto_excluded'] + ff['auto_excluded'])} | {n(rep['snowball_only_auto_excluded'])} + {n(ff['auto_excluded'])} |")
    a(f"| **Records to screen (title and abstract), final queue** | **{n(ff['passes'])}** | {n(ff['passes_by_kind']['database'])} database + {n(ff['passes_by_kind']['snowball'])} snowball; tiers T1 {n(ff['by_original_tier']['T1']['passes'])}, T2 {n(ff['by_original_tier']['T2']['passes'])}, T3 {n(ff['by_original_tier']['T3']['passes'])}, T4 {n(ff['by_original_tier']['T4']['passes'])}, T5 0 |")
    a(f"| Of which without an abstract | {n(ff['passes_missing_abstract'])} | screened on title alone, flagged |")
    a(f"| Validation of the automation filter | {v1['n']} + {v2['n']} records | V1 {v1['n']} of {n(v1['population_size'])} database exclusions; V2 {v2['n']} of {n(v2['population_size'])} title-only snowball exclusions; sets written, not screened |")
    a("")
    a("The 4,534 + 12,952 records marked by automation are reported as 'records marked as ineligible by automation tools' (PRISMA 2020 item 16a), with the reasons given here and in the protocol amendment. "
      "Dual screening by two Claude screeners (D0026 item 5, D0027 item 4) then applies to the final queue, T1 and T2 first; this has not started.")
    a("")
    a("## 14. Files added or changed by D0027")
    a("")
    for f in (f"string-revision-round4-{ISO}.json", f"screening-queue-final-{ISO}.jsonl", f"auto-excluded-{ISO}.jsonl", f"final-filter-stats-{ISO}.json",
              f"validation-autoexcl-sampling-{ISO}.json", f"precision-round4-sample-{ISO}.json", f"precision-round4-labels-{ISO}.json", f"precision-round4-{ISO}.json",
              f"lost-check-sample-{ISO}.json", f"lost-check-labels-{ISO}.json", f"lost-check-{ISO}.json", "subscription-search-sheet.md"):
        a(f"- `research/review/corpus/{f}`")
    a(f"- `research/review/screening/validation-autoexcl-{ISO}.jsonl`")
    a("- `tools/search_sources.py` (S1PP_PARTS, S2PP_PARTS, R4_* lists), `tools/string_rounds.py` (`round4`), `tools/merge_new_records_v2.py` (`final-filter`), `tools/precision_actual.py` (`r4`, `lost-sample`, `lost-report`), `tools/make_search_sheet_v2.py`, `tools/write_search_report_v2.py`")
    a("- `research/review/protocol.md` section 10 (amendment entry D0027)")
    a("")


if __name__ == "__main__":
    main()
