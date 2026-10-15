"""Merge, deduplicate, enrich and filter the 2026-10-15 searches with the original (S1, S2) and revised (S1', S2')
strings (decision D0026; protocol section 10 amendment of 2026-10-15). Extends tools/merge_new_records.py: its parsers,
union-find rules and existing-record index are reused; this file adds the revised strings, three extra duplicate keys,
the snowball string filter, abstract enrichment, and the screening queue.

    python tools/merge_new_records_v2.py merge       # raw files -> new-records-2026-10-15-v2.jsonl (pre-enrichment)
    python tools/merge_new_records_v2.py enrich      # fetch missing abstracts (Semantic Scholar batch, arXiv API)
    python tools/merge_new_records_v2.py finalize    # string_match, snowball filter, screening queue, report

Reads research/review/corpus/search-log.jsonl rows executed on 2026-10-15 whose export is under
research/sources/search-raw/ (both string versions and both snowball directions). Does NOT modify
research/review/screening/records.jsonl and does NOT screen anything.

Extra duplicate keys (v1 used arXiv ID, DOI, source IDs, normalised title, normalised abstract):
  - embedded arXiv ID: reference-list fragments such as "Large language diffusion models . 2025. arXiv: 2502.09992 [cs.CL"
  - cleaned title: leading "2025." / "2025b." and trailing ", 2025" / ", 2025a" stripped
  - squashed cleaned title: letters and digits only (undoes hyphenation breaks such as "Ac-celeration"), 25+ characters
"""
from __future__ import annotations

import collections
import hashlib
import json
import random
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import merge_new_records as m  # noqa: E402
import search_sources as ss  # noqa: E402

ROOT, CORPUS = ss.ROOT, ss.CORPUS
DATE, ISO = "20261015", "2026-10-15"
V2 = CORPUS / f"new-records-{ISO}-v2.jsonl"
QUEUE = CORPUS / f"screening-queue-{ISO}.jsonl"
REPORT = CORPUS / f"search-v2-report-{ISO}.json"
ENRICH_LOG = CORPUS / f"abstract-enrichment-{ISO}.json"
STRINGS = ("S1", "S2", "S1'", "S2'")


# ------------------------------------------------------------------ extra duplicate keys
def clean_title(t: str) -> str:
    t = " ".join((t or "").split())
    t = re.sub(r"^(?:19|20)\d\d[a-z]?[.)]?\s+", "", t)                 # "2025. ", "2025b. "
    t = re.sub(r"[,.]?\s*(?:19|20)\d\d[a-z]?\.?$", "", t)               # ", 2025", ", 2025a"
    t = re.sub(r"\s*\.?\s*(?:19|20)\d\d\.\s*arXiv:.*$", "", t)         # ". 2025. arXiv: 2502.09992 [cs.CL"
    return t.strip()


def squash(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", clean_title(t).lower())


def embedded_arxiv(t: str):
    mm = re.search(r"arXiv:\s*(\d{4}\.\d{4,5})", t or "", re.I)
    return mm.group(1) if mm else None


def keys_v2(r):
    ks = m.keys_of(r)
    ea = embedded_arxiv(r["title"])
    if ea:
        ks.append(("arxiv", ea))
    ct = m.norm_title(clean_title(r["title"]))
    if len(ct.split()) >= 3 and ct != m.norm_title(r["title"]):
        ks.append(("t", ct))
    sq = squash(r["title"])
    if len(sq) >= 25:
        ks.append(("q", sq))
    return ks


def cluster_v2(rows):
    parent = list(range(len(rows)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    seen, extra_merges = {}, 0
    for i, r in enumerate(rows):
        for k in keys_v2(r):
            if k in seen:
                a, b = find(i), find(seen[k])
                if a != b:
                    parent[a] = b
                    if k[0] == "q" or (k[0] == "t" and k[1] != m.norm_title(r["title"])) or (k[0] == "arxiv" and not r.get("arxiv")):
                        extra_merges += 1
            else:
                seen[k] = i
    groups = collections.defaultdict(list)
    for i in range(len(rows)):
        groups[find(i)].append(i)
    return list(groups.values()), extra_merges


def merge_group_v2(rs):
    out = m.merge_group(rs)
    first_abs = next((r for r in sorted(rs, key=lambda x: (not x["abstract"], x["src"])) if r["abstract"]), None)
    out["abstract_source"] = (first_abs.get("abstract_source") or first_abs["src"]) if first_abs else None
    return out


# ------------------------------------------------------------------ existing-record index (as tools/merge_new_records.py main())
def existing_index():
    existing = [json.loads(l) for l in open(ROOT / "research/review/screening/records.jsonl", encoding="utf8")]
    idx = {"arxiv": {}, "t": {}, "a": {}, "doi": {}, "q": {}}
    venues = json.load(open(CORPUS / "venues-semantic-scholar.json"))["records"]
    for e in existing:
        if e["arxiv"]:
            idx["arxiv"][e["arxiv"]] = e["sid"]
            d = (venues.get(e["arxiv"]) or {}).get("doi")
            if d:
                idx["doi"][d.lower()] = e["sid"]
        idx["t"].setdefault(m.norm_title(e["title"]), e["sid"])
        sq = squash(e["title"])
        if len(sq) >= 25:
            idx["q"].setdefault(sq, e["sid"])
        na = m.norm_title(e["abstract"])
        if len(na) >= 200:
            idx["a"].setdefault(hashlib.md5(na.encode()).hexdigest(), e["sid"])
    ts = {e["sid"]: m.tset(e["title"]) for e in existing}
    inv = collections.defaultdict(set)
    for sid, t in ts.items():
        for w in t:
            inv[w].add(sid)

    def match(r):
        ea = embedded_arxiv(r["title"])
        for ax in (r.get("arxiv"), ea):
            if ax and ax in idx["arxiv"]:
                return idx["arxiv"][ax], "arxiv"
        if r.get("doi") and r["doi"] in idx["doi"]:
            return idx["doi"][r["doi"]], "doi"
        nt = m.norm_title(r["title"])
        if len(nt.split()) >= 3 and nt in idx["t"]:
            return idx["t"][nt], "title"
        ct = m.norm_title(clean_title(r["title"]))
        if len(ct.split()) >= 3 and ct in idx["t"]:
            return idx["t"][ct], "cleaned-title"
        sq = squash(r["title"])
        if len(sq) >= 25 and sq in idx["q"]:
            return idx["q"][sq], "squashed-title"
        na = m.norm_title(r["abstract"])
        if len(na) >= 200 and hashlib.md5(na.encode()).hexdigest() in idx["a"]:
            return idx["a"][hashlib.md5(na.encode()).hexdigest()], "abstract"
        return None, None

    def near(r):
        t = m.tset(r["title"])
        if len(t) < 4:
            return None
        cand = collections.Counter(s for w in t for s in inv.get(w, ()))
        best = None
        for s, _ in cand.most_common(8):
            u = len(t | ts[s])
            j = len(t & ts[s]) / u if u else 0
            if j >= 0.8 and (best is None or j > best[1]):
                best = (s, j)
        return best[0] if best else None

    return existing, match, near


# ------------------------------------------------------------------ raw files -> normalised records
def load_per_source():
    rows = [json.loads(l) for l in open(ss.LOG, encoding="utf8") if l.strip()]
    mine = [r for r in rows if r["executed_utc"].startswith(DATE) and r["export"].startswith("research/sources/search-raw/")]
    latest_oa, latest_arx, latest_s2, latest_acl = {}, {}, {}, {}
    for r in mine:
        if r["database"].startswith("OpenAlex"):
            latest_oa[r["string"]] = r["export"]
        if r["database"].startswith("arXiv"):
            latest_arx[r["string"]] = r["export"]       # a rerun of a part supersedes the earlier run (raw files and log rows stay)
        if r["database"].startswith("Semantic Scholar Graph API (paper/search/bulk)"):
            latest_s2[r["string"]] = r["export"]
        if r["database"].startswith("ACL"):
            latest_acl[r["string"]] = r["export"]
    per_source, notes = collections.OrderedDict(), collections.defaultdict(dict)
    for r in mine:
        p = ROOT / r["export"]
        db, name = r["database"], r["string"]
        if not p.exists():
            continue
        if db.startswith("OpenAlex"):
            if latest_oa[name] != r["export"]:
                continue
            src, rs = "openalex", m.parse_oa(p, name, "openalex")
        elif db.startswith("Semantic Scholar Graph API (paper/search/bulk)"):
            if latest_s2[name] != r["export"]:
                continue
            src, rs = "semantic-scholar-bulk", m.parse_s2(p, name, "semantic-scholar-bulk")
        elif db.startswith("arXiv"):
            if latest_arx[name] != r["export"]:
                continue
            src, rs = "arxiv-protocol-rerun", m.parse_arxiv(p, name, "arxiv-protocol-rerun")
        elif db.startswith("ACL"):
            if latest_acl[name] != r["export"]:
                continue
            src, rs = "acl-anthology", m.parse_acl(p, name, "acl-anthology")
        elif db.startswith("OpenReview"):
            st = notes["openreview"].setdefault("stats", collections.Counter())
            src, rs = "openreview", m.parse_orv(p, name, "openreview", st)
        elif "snowball" in name:
            src = name
            st = notes[src].setdefault("stats", collections.Counter())
            rs = m.parse_snow(p, name, src, st)
        else:
            continue
        for x in rs:
            x["abstract_source"] = src
        per_source.setdefault(src, []).extend(rs)
    return per_source, notes


def string_of(label: str) -> str:
    return label.split(":")[0]


def text_of(r):
    return r["title"] + " " + r["abstract"] + " " + " ".join((r["extra"].get("keywords") or []) if r.get("extra") else [])


def string_match(r):
    t = text_of(r)
    return {s: ss.matches(s, t) for s in STRINGS}


# ------------------------------------------------------------------ merge
def cmd_merge():
    per_source, notes = load_per_source()
    existing, existing_match, near = existing_index()
    report = {"date": ISO, "existing_records": len(existing), "sources": {}, "extra_duplicate_keys_merges": {}}
    all_new, extra_total = [], 0
    for src, rs in per_source.items():
        cl, ex_merges = cluster_v2(rs)
        extra_total += ex_merges
        uniq = [merge_group_v2([rs[i] for i in g]) for g in cl]
        n_ex = sum(1 for u in uniq if existing_match(u)[0])
        by_string = collections.Counter(string_of(r["label"]) for r in rs)
        rep = {"identified": len(rs), "identified_by_string": dict(by_string), "unique_within_source": len(uniq),
               "duplicates_within_source": len(rs) - len(uniq), "duplicates_against_existing": n_ex, "new": len(uniq) - n_ex}
        if "stats" in notes[src]:
            rep["filter_stats"] = dict(notes[src]["stats"])
        # records the revised strings add within the source, over the original strings (title + abstract, local test)
        new_u = [u for u in uniq if not existing_match(u)[0]]
        sm = [string_match(u) for u in new_u]
        rep["new_matching_locally"] = {s: sum(1 for x in sm if x[s]) for s in STRINGS}
        report["sources"][src] = rep
        all_new += new_u
    flat = [{**u, "src": ",".join(u["sources"]), "label": ""} for u in all_new]
    cl, ex_merges = cluster_v2(flat)
    extra_total += ex_merges
    union = []
    for g in cl:
        rs = [flat[i] for i in g]
        mm = merge_group_v2(rs)
        mm["sources"] = sorted({s for r in rs for s in r["sources"]})
        mm["found_by"] = sorted({f for r in rs for f in r["found_by"]})
        union.append(mm)
    union.sort(key=lambda r: (r["arxiv"] or "9999", m.norm_title(r["title"])))
    # v1 ids for cross-reference
    v1 = [json.loads(l) for l in open(CORPUS / f"new-records-{ISO}.jsonl", encoding="utf8")]
    v1_idx = {}
    for r in v1:
        for k in (("arxiv", r["arxiv"]), ("doi", r["doi"]), ("s2", r["s2_id"]), ("oa", r["openalex_id"]), ("orid", r["openreview_id"]),
                  ("t", m.norm_title(r["title"]))):
            if k[1] and (k[0] != "t" or len(k[1].split()) >= 3):
                v1_idx.setdefault(k, r["nid"])
    n_in_v1 = 0
    with V2.open("w", encoding="utf8") as fh:
        for i, u in enumerate(union, 1):
            # a record is "existing in v1" if it carries a v1 identifier
            v1id = next((v1_idx[k] for k in (("arxiv", u["arxiv"]), ("doi", u["doi"]), ("s2", u["s2"]), ("oa", u["oa"]), ("orid", u["orid"]),
                                             ("t", m.norm_title(u["title"]))) if k[1] and k in v1_idx), None)
            n_in_v1 += bool(v1id)
            rec = {"nid": f"M{i:05d}", "v1_nid": v1id, "arxiv": u["arxiv"], "doi": u["doi"], "s2_id": u["s2"], "openalex_id": u["oa"],
                   "openreview_id": u["orid"], "acl_id": u["acl"], "title": u["title"], "abstract": u["abstract"],
                   "abstract_source": u["abstract_source"], "published": u["published"], "venue": u["venue"], "sources": u["sources"],
                   "found_by": u["found_by"], "possible_duplicate_of": near(u), "extra": u["extra"] or None}
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    report["union_new_records"] = len(union)
    report["union_new_also_in_v1"] = n_in_v1
    report["union_new_only_in_v2_runs"] = len(union) - n_in_v1
    report["extra_duplicate_keys_merges"] = extra_total
    report["v1_union_new_records"] = len(v1)
    (CORPUS / f"search-v2-merge-stats-{ISO}.json").write_text(json.dumps(report, indent=2), encoding="utf8")
    print(json.dumps({k: v for k, v in report.items() if k != "sources"}, indent=2))
    print(f"wrote {V2.relative_to(ROOT)} ({len(union)} records)")


# ------------------------------------------------------------------ enrichment
def load_v2():
    return [json.loads(l) for l in open(V2, encoding="utf8") if l.strip()]


def save_v2(rows):
    with V2.open("w", encoding="utf8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def snowball_only(r):
    return set(r["sources"]) <= {"snowball-backward", "snowball-forward"}


def clean_abs(a):
    return " ".join((a or "").split())


def oa_abs(w):
    inv = w.get("abstract_inverted_index") or {}
    pos = sorted((i, t) for t, ix in inv.items() for i in ix)
    return " ".join(t for _, t in pos)


def cmd_enrich(scope="all"):
    skip = {a[7:] for a in sys.argv[2:] if a.startswith("--skip-")}          # --skip-s2 --skip-arxiv --skip-openalex --skip-crossref
    prev = json.loads(ENRICH_LOG.read_text(encoding="utf8")) if ENRICH_LOG.exists() else None
    """Fill empty abstracts. scope all: every record without one (done BEFORE the snowball string filter so that the filter
    is not decided by a missing abstract). Order: Semantic Scholar batch (arXiv, DOI, paperId, ACL), arXiv API (id_list),
    OpenAlex (DOI, 50 per call; stops when the free quota is exhausted)."""
    rows = load_v2()
    log = {"date": ISO, "attempted": 0, "by_source": collections.Counter(), "notes": []}
    todo = [r for r in rows if not r["abstract"]]
    log["attempted"] = len(todo)
    print(f"records without abstract: {len(todo)} of {len(rows)}", flush=True)

    def ids_for_s2(r):
        out = []
        if r["s2_id"]:
            out.append(r["s2_id"])
        if r["arxiv"]:
            out.append("ARXIV:" + r["arxiv"])
        if r["doi"]:
            out.append("DOI:" + r["doi"])
        if r["acl_id"]:
            out.append("ACL:" + r["acl_id"])
        return out[:1]                                          # one identifier per record, most specific first

    # 1. Semantic Scholar batch
    cand = [(r, ids_for_s2(r)) for r in todo]
    cand = [(r, i[0]) for r, i in cand if i]
    for i in range(0, 0 if "s2" in skip else len(cand), 500):
        chunk = cand[i:i + 500]
        st, raw, _ = ss.http("https://api.semanticscholar.org/graph/v1/paper/batch?fields=paperId,abstract,externalIds",
                             4.0, data=json.dumps({"ids": [c[1] for c in chunk]}).encode(), headers={"Content-Type": "application/json"})
        if st != 200:
            log["notes"].append(f"Semantic Scholar batch status {st} at {i}; stopped")
            print(log["notes"][-1], flush=True)
            break
        for (r, _), p in zip(chunk, json.loads(raw)):
            if p and clean_abs(p.get("abstract")):
                r["abstract"], r["abstract_source"] = clean_abs(p["abstract"]), "semantic-scholar-batch"
                if not r["s2_id"]:
                    r["s2_id"] = p.get("paperId")
                log["by_source"]["semantic-scholar-batch"] += 1
        print(f"  S2 batch {min(i + 500, len(cand))}/{len(cand)}", flush=True)
        save_v2(rows)

    # 2. arXiv API id_list
    todo = [r for r in rows if not r["abstract"] and r["arxiv"]]
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for i in range(0, 0 if "arxiv" in skip else len(todo), 80):
        chunk = todo[i:i + 80]
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
            {"id_list": ",".join(r["arxiv"] for r in chunk), "max_results": 100})
        st, raw, _ = ss.http(url, 3.5)
        if st != 200 or b"<!ENTITY" in raw or b"<!DOCTYPE" in raw:
            log["notes"].append(f"arXiv id_list status {st} at {i}; stopped")
            break
        got = {}
        for e in ET.fromstring(raw).findall("a:entry", ns):
            aid = re.sub(r"v\d+$", "", e.findtext("a:id", "", ns).rsplit("/", 1)[-1])
            got[aid] = clean_abs(e.findtext("a:summary", "", ns))
        for r in chunk:
            if got.get(r["arxiv"]):
                r["abstract"], r["abstract_source"] = got[r["arxiv"]], "arxiv-api"
                log["by_source"]["arxiv-api"] += 1
        print(f"  arXiv id_list {min(i + 80, len(todo))}/{len(todo)}", flush=True)
    save_v2(rows)

    # 3. OpenAlex by DOI (free credits are limited; stop on 429)
    todo = [r for r in rows if not r["abstract"] and r["doi"]]
    for i in range(0, 0 if "openalex" in skip else len(todo), 50):
        chunk = todo[i:i + 50]
        flt = "doi:" + "|".join(r["doi"] for r in chunk)
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(
            {"filter": flt, "per-page": 50, "select": "id,doi,abstract_inverted_index"}, safe=":|/")
        st, raw, hdr = ss.http(url, 1.5, tries=2)
        if st != 200:
            log["notes"].append(f"OpenAlex status {st} at {i} (remaining credits {hdr.get('X-RateLimit-Remaining')}); stopped")
            print(log["notes"][-1], flush=True)
            break
        by_doi = {(w.get("doi") or "").lower().replace("https://doi.org/", ""): oa_abs(w) for w in json.loads(raw)["results"]}
        for r in chunk:
            a = clean_abs(by_doi.get(r["doi"]))
            if a:
                r["abstract"], r["abstract_source"] = a, "openalex-doi"
                log["by_source"]["openalex-doi"] += 1
    save_v2(rows)

    # 4. Crossref by DOI (abstracts are deposited by some publishers only): records that will be screened or may match a string
    #    on the title alone (database records, and snowball records whose title matches a string); one request per record, 1 per second
    todo = [r for r in rows if not r["abstract"] and r["doi"] and (not snowball_only(r) or any(ss.matches(s, r["title"]) for s in STRINGS))]
    log["crossref_attempted"] = len(todo)
    for i, r in enumerate([] if "crossref" in skip else todo):
        st, raw, _ = ss.http("https://api.crossref.org/works/" + urllib.parse.quote(r["doi"], safe="/"), 1.0, tries=2, timeout=60)
        if st == 200:
            ab = re.sub(r"<[^>]+>", " ", json.loads(raw)["message"].get("abstract") or "")
            ab = re.sub(r"^\s*Abstract\s*[:.]?\s*", "", clean_abs(ab), flags=re.I)
            if len(ab) >= 80:
                r["abstract"], r["abstract_source"] = ab, "crossref-doi"
                log["by_source"]["crossref-doi"] += 1
        elif st is None:
            log["notes"].append(f"Crossref unreachable at {i}; stopped")
            break
        if (i + 1) % 100 == 0:
            print(f"  Crossref {i + 1}/{len(todo)}", flush=True)
            save_v2(rows)
    save_v2(rows)
    log["still_missing"] = sum(1 for r in rows if not r["abstract"])
    log["by_source"] = dict(log["by_source"])
    log["skipped"] = sorted(skip)
    if prev:                                                                # a second pass appends to the first
        passes = prev.get("passes") or [{k: v for k, v in prev.items() if k != "passes"}]
        passes.append(log)
        by = collections.Counter()
        for p_ in passes:
            by.update(p_["by_source"])
        log = {"date": ISO, "attempted": passes[0]["attempted"], "by_source": dict(by), "notes": [n_ for p_ in passes for n_ in p_["notes"]],
               "still_missing": log["still_missing"], "passes": passes}
    ENRICH_LOG.write_text(json.dumps(log, indent=2), encoding="utf8")
    print(json.dumps(log, indent=2))


# ------------------------------------------------------------------ finalize
TIER_NAMES = {
    1: "T1 matches S1 or S2, S1' part A1, or S2'",
    2: "T2 matches S1' A2 with a language word, or A3",
    3: "T3 matches only S1' B or C (diffusion with text-generation, NLP-task or language-model words)",
    4: "T4 matches only S1' A2 without a language word",
    5: "T5 database record that matches no string locally",
}


def tier_of(r):
    """Screening priority of a queue record, from the local test of the strings on title and abstract. A guide for ordering and
    sampling (decision for the orchestrator), not a screening decision."""
    t = re.findall(r"[a-z0-9]+", text_of(r).lower())
    sm, parts = r["string_match"], r["s1p_parts"]
    if sm["S1"] or sm["S2"] or "A1" in parts or r["s2p_parts"]:
        return 1
    if "A3" in parts or ss.ev_p(ss.A2_WITH_CONTEXT, t):
        return 2
    if "B" in parts or "C" in parts:
        return 3
    if "A2" in parts:
        return 4
    return 5


def mark_fragments(rows):
    """Reference-list fragments: snowball-only records with no identifier and no abstract (Semantic Scholar returns unparsed reference
    strings such as '2023. SSD-LM: Semi-autoregressive Simplex-based Diffusion Language Mod'). Flagged, never merged: for each, the
    best-matching record (token-set Jaccard or containment of the fragment in the target, cleaned titles) is stored for a human check."""
    existing = [json.loads(l) for l in open(ROOT / "research/review/screening/records.jsonl", encoding="utf8")]
    ct = lambda title: m.tset(clean_title(title))
    targets = [(e["sid"], ct(e["title"])) for e in existing] + [(r["nid"], ct(r["title"])) for r in rows if r["arxiv"] or r["doi"] or r["abstract"]]
    inv = collections.defaultdict(set)
    for i, (_, ts) in enumerate(targets):
        for w in ts:
            inv[w].add(i)
    for r in rows:
        ids = r["arxiv"] or r["doi"] or r["s2_id"] or r["openalex_id"] or r["openreview_id"] or r["acl_id"]
        r["title_fragment"] = bool(snowball_only(r) and not ids and not r["abstract"])
        r["near_duplicate_candidate"] = None
        if not r["title_fragment"]:
            continue
        ts = ct(r["title"])
        if len(ts) < 3:
            continue
        cand = collections.Counter(i for w in ts for i in inv.get(w, ()))
        best = None
        for i, _ in cand.most_common(10):
            k, t2 = targets[i]
            if k == r["nid"]:
                continue
            u = len(ts | t2)
            j = len(ts & t2) / u if u else 0
            cont = len(ts & t2) / len(ts)
            if best is None or max(j, cont * 0.9) > best[0]:
                best = (max(j, cont * 0.9), k, round(j, 2), round(cont, 2))
        if best and best[0] >= 0.8:
            r["near_duplicate_candidate"] = {"id": best[1], "jaccard": best[2], "containment": best[3]}


def cmd_finalize():
    rows = load_v2()
    queue, counts = [], collections.Counter()
    for r in rows:
        t = text_of(r)
        sm = {s: ss.matches(s, t) for s in STRINGS}
        r["string_match"] = sm
        r["s1p_parts"] = ss.part_of("S1'", t)
        r["s2p_parts"] = ss.part_of("S2'", t)
        r["queue_tier"] = tier_of(r)
        any_match = any(sm.values())
        r["snowball_only"] = snowball_only(r)
        if r["snowball_only"] and not any_match:
            r["queue_tier"] = None
            r["auto_excluded"] = True
            r["auto_excluded_reason"] = "string filter, D0026"
            r["auto_excluded_abstract_missing"] = not r["abstract"]
        else:
            r["auto_excluded"] = False
            r["auto_excluded_reason"] = None
            r["auto_excluded_abstract_missing"] = None
            queue.append(r)
    mark_fragments(rows)
    save_v2(rows)
    with QUEUE.open("w", encoding="utf8") as fh:
        for r in queue:
            fh.write(json.dumps({"id": r["nid"], "title": r["title"], "abstract": r["abstract"], "sources": r["sources"],
                                 "string_match": r["string_match"], "arxiv": r["arxiv"], "doi": r["doi"],
                                 "published": r["published"], "venue": r["venue"],
                                 "queue_reason": "database record" if not r["snowball_only"] else "snowball record matching a string",
                                 "queue_tier": r["queue_tier"], "title_fragment": r["title_fragment"],
                                 "near_duplicate_candidate": r["near_duplicate_candidate"],
                                 "s1p_parts": r["s1p_parts"], "s2p_parts": r["s2p_parts"],
                                 "abstract_source": r["abstract_source"], "possible_duplicate_of": r["possible_duplicate_of"]},
                                ensure_ascii=False) + "\n")
    # ---- counts for the report
    st = json.loads((CORPUS / f"search-v2-merge-stats-{ISO}.json").read_text(encoding="utf8"))
    db = [r for r in rows if not r["snowball_only"]]
    sb = [r for r in rows if r["snowball_only"]]
    rep = {
        "date": ISO, "new_records_v2_file": V2.relative_to(ROOT).as_posix(), "queue_file": QUEUE.relative_to(ROOT).as_posix(),
        "union_new_records": len(rows), "union_new_also_in_v1": st["union_new_also_in_v1"],
        "database_records": len(db), "snowball_only_records": len(sb),
        "snowball_only_matching_a_string": sum(1 for r in sb if any(r["string_match"].values())),
        "snowball_only_matching_by_string": {s: sum(1 for r in sb if r["string_match"][s]) for s in STRINGS},
        "snowball_only_auto_excluded": sum(1 for r in sb if r["auto_excluded"]),
        "snowball_only_auto_excluded_abstract_missing": sum(1 for r in sb if r["auto_excluded"] and not r["abstract"]),
        "to_screen": len(queue),
        "to_screen_database_records": sum(1 for r in queue if not r["snowball_only"]),
        "to_screen_snowball_matching": sum(1 for r in queue if r["snowball_only"]),
        "to_screen_missing_abstract": sum(1 for r in queue if not r["abstract"]),
        "to_screen_missing_abstract_by_kind": {"database": sum(1 for r in queue if not r["abstract"] and not r["snowball_only"]),
                                               "snowball": sum(1 for r in queue if not r["abstract"] and r["snowball_only"])},
        "database_records_matching_by_string_locally": {s: sum(1 for r in db if r["string_match"][s]) for s in STRINGS},
        "database_records_matching_no_string_locally": sum(1 for r in db if not any(r["string_match"].values())),
        "database_records_added_by_revised_strings": sum(1 for r in db if (r["string_match"]["S1'"] or r["string_match"]["S2'"]) and not (r["string_match"]["S1"] or r["string_match"]["S2"])),
        "queue_by_tier": {TIER_NAMES[k]: sum(1 for r in queue if r["queue_tier"] == k) for k in sorted(TIER_NAMES)},
        "queue_by_tier_and_kind": {TIER_NAMES[k]: {"database": sum(1 for r in queue if r["queue_tier"] == k and not r["snowball_only"]),
                                                    "snowball": sum(1 for r in queue if r["queue_tier"] == k and r["snowball_only"])} for k in sorted(TIER_NAMES)},
        "queue_by_s1p_part": dict(collections.Counter(p for r in queue for p in r["s1p_parts"])),
        "queue_by_s2p_part": dict(collections.Counter(p for r in queue for p in r["s2p_parts"])),
        "queue_by_source_combination": dict(collections.Counter("+".join(r["sources"]) for r in queue).most_common(40)),
        "abstract_source_all_records": dict(collections.Counter(r["abstract_source"] or "none" for r in rows)),
        "abstract_source_queue": dict(collections.Counter(r["abstract_source"] or "none" for r in queue)),
        "title_fragments_in_queue": sum(1 for r in queue if r["title_fragment"]),
        "title_fragments_in_queue_with_near_duplicate_candidate": sum(1 for r in queue if r["title_fragment"] and r["near_duplicate_candidate"]),
        "possible_duplicates_of_existing_in_queue": sum(1 for r in queue if r["possible_duplicate_of"]),
        "dedup_extra_key_merges": st["extra_duplicate_keys_merges"], "per_source": st["sources"],
        "records_jsonl_sha256_unchanged": hashlib.sha256((ROOT / "research/review/screening/records.jsonl").read_bytes()).hexdigest(),
        "queue_sha256": hashlib.sha256(QUEUE.read_bytes()).hexdigest(),
        "v2_sha256": hashlib.sha256(V2.read_bytes()).hexdigest(),
    }
    if ENRICH_LOG.exists():
        rep["enrichment"] = json.loads(ENRICH_LOG.read_text(encoding="utf8"))
    REPORT.write_text(json.dumps(rep, indent=2), encoding="utf8")
    print(json.dumps({k: v for k, v in rep.items() if k not in ("per_source", "queue_by_source_combination")}, indent=2))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"merge": cmd_merge, "enrich": cmd_enrich, "finalize": cmd_finalize}.get(cmd, lambda: sys.exit(__doc__))()
