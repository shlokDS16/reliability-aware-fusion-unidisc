"""Normalise, deduplicate and report the 2026-10-15 searches (protocol section 4, step 1).

    python tools/merge_new_records.py [YYYYMMDD]      # default 20261015

Reads the raw files named in research/review/corpus/search-log.jsonl rows executed on that date (only
rows whose export is under research/sources/search-raw/), normalises identifiers (arXiv ID without
version, DOI lower-case, OpenReview forum ID, ACL ID, S2 paperId, OpenAlex ID), and deduplicates with
the existing rules of tools/build_screening_set.py (arXiv ID, then normalised title) plus the third key
recommended in screening/dedup-addendum.md (normalised abstract). It does NOT modify records.jsonl and
does NOT screen anything.

Writes into research/review/corpus/:
  new-records-<date>.jsonl            records not present in screening/records.jsonl (one per line)
  new-records-dedup-report-<date>.json counts per source and string
  pilot-recall-<date>.json            recall of the protocol seed list per source
"""
from __future__ import annotations

import collections
import datetime as dt
import hashlib
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_sources as ss  # noqa: E402

ROOT = ss.ROOT
CORPUS = ss.CORPUS
DATE = sys.argv[1] if len(sys.argv) > 1 else "20261015"
ISO = f"{DATE[:4]}-{DATE[4:6]}-{DATE[6:]}"


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def arxiv_in(*xs):
    for x in xs:
        m = re.search(r"arxiv(?:\.org/(?:abs|pdf)/|\.)(\d{4}\.\d{4,5})", (x or "").lower())
        if m:
            return m.group(1)
    return None


def arxiv_ext(ex):
    ex = ex or {}
    if ex.get("ArXiv"):
        return re.sub(r"v\d+$", "", ex["ArXiv"])
    m = re.search(r"10\.48550/arxiv\.(\d{4}\.\d{4,5})", (ex.get("DOI") or "").lower())
    return m.group(1) if m else None


def doi_norm(d):
    d = (d or "").lower().strip()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d or None


STOP = set("a an the of for and in on to with via from by as at is are using towards toward do does".split())


def tset(t):
    return {w for w in norm_title(t).split() if w not in STOP}


# ------------------------------------------------------------------ parsers: raw file -> normalised dicts
def rec(src, label, **kw):
    d = {"src": src, "label": label, "arxiv": None, "doi": None, "s2": None, "oa": None, "orid": None, "acl": None,
         "title": "", "abstract": "", "published": None, "venue": None, "extra": {}}
    d.update(kw)
    d["title"] = " ".join((d["title"] or "").split())
    d["abstract"] = " ".join((d["abstract"] or "").split())
    return d


def parse_s2(path, label, src):
    out = []
    j = json.load(open(path, encoding="utf8"))
    for p in j["records"]:
        ex = p.get("externalIds") or {}
        out.append(rec(src, label, arxiv=arxiv_ext(ex),
                     doi=doi_norm(ex.get("DOI")), s2=p.get("paperId"), title=p.get("title"), abstract=p.get("abstract"),
                     published=p.get("publicationDate") or (str(p["year"]) if p.get("year") else None), venue=p.get("venue") or None,
                     acl=ex.get("ACL")))
    return out


def parse_oa(path, label, src):
    out = []
    for w in json.load(open(path, encoding="utf8"))["records"]:
        inv = w.get("abstract_inverted_index") or {}
        pos = sorted((i, t) for t, ix in inv.items() for i in ix)
        urls = [(l or {}).get("landing_page_url") or "" for l in w.get("locations") or []] + \
               [(l or {}).get("pdf_url") or "" for l in w.get("locations") or []]
        doi = doi_norm(w.get("doi"))
        out.append(rec(src, label, arxiv=arxiv_in(*urls, doi and ("arxiv." + doi.split("arxiv.")[-1] if "arxiv" in doi else "")),
                       doi=doi, oa=w.get("id"), title=w.get("title"), abstract=" ".join(t for _, t in pos),
                       published=w.get("publication_date"), venue=(((w.get("primary_location") or {}).get("source") or {}).get("display_name"))))
    return out


def parse_arxiv(path, label, src):
    return [rec(src, label, arxiv=r["arxiv"], title=r["title"], abstract=r["abstract"], published=r["published"])
            for r in json.load(open(path, encoding="utf8"))["records"]]


def parse_acl(path, label, src):
    out = []
    for r in json.load(open(path, encoding="utf8"))["records"]:
        pub = f"{r['year']}"
        out.append(rec(src, label, acl=r.get("acl_id"), doi=doi_norm(r.get("doi")), title=r["title"], abstract=r["abstract"],
                       published=pub, venue=r.get("booktitle") or None, extra={"published_precision": "year"}))
    return out


def parse_orv(path, label, src, stats):
    out = []
    lo = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000
    hi = dt.datetime.now(dt.timezone.utc).timestamp() * 1000
    for n in json.load(open(path, encoding="utf8"))["notes"]:
        c = n.get("content") or {}
        v = lambda k: (c.get(k) or {}).get("value")
        stats["retrieved"] += 1
        cd = n.get("cdate") or n.get("tcdate")
        if cd is None or not (lo <= cd <= hi):
            stats["outside_window"] += 1
            continue
        kw = v("keywords") or []
        text = " ".join([v("title") or "", v("abstract") or "", " ".join(kw) if isinstance(kw, list) else str(kw)])
        name = label.split(":")[0]
        if not ss.matches(name, text):
            stats["fails_local_clause"] += 1
            continue
        vid, ven = v("venueid") or "", v("venue") or ""
        cls = ("workshop" if "/workshop" in vid.lower() or "workshop" in ven.lower() else
               "declined_or_withdrawn" if re.search(r"reject|withdraw|desk", vid, re.I) else
               "under_review_or_submission" if re.search(r"submission", ven, re.I) and not re.search(r"reject|withdraw", ven, re.I) else "venue")
        out.append(rec(src, label, orid=n.get("forum") or n.get("id"), title=v("title"), abstract=v("abstract"),
                       published=dt.datetime.fromtimestamp(cd / 1000, dt.timezone.utc).strftime("%Y-%m-%d"), venue=ven or vid or None,
                       extra={"venueid": vid, "venue_class": cls, "keywords": kw}))
    return out


def parse_snow(path, label, src, stats):
    out = []
    key = "references" if "backward" in label else "citations"
    for line in open(path, encoding="utf8"):
        r = json.loads(line)
        for p in r.get(key) or []:
            stats["edges"] += 1
            if not p or not p.get("title"):
                stats["no_title"] += 1
                continue
            y = p.get("year")
            pd = p.get("publicationDate")
            if (pd and pd < "2021-01-01") or (not pd and y and y < 2021):
                stats["before_2021"] += 1
                continue
            if not pd and not y:
                stats["no_date_kept"] += 1
            ex = p.get("externalIds") or {}
            d = rec(src, label, arxiv=arxiv_ext(ex),
                    doi=doi_norm(ex.get("DOI")), s2=p.get("paperId"), acl=ex.get("ACL"), title=p["title"], abstract=p.get("abstract"),
                    published=pd or (str(y) if y else None), venue=p.get("venue") or None)
            d["extra"]["seed"] = r["seed"]
            out.append(d)
    return out


# ------------------------------------------------------------------ union-find dedup
def keys_of(r):
    ks = []
    for k in ("arxiv", "doi", "s2", "oa", "orid", "acl"):
        if r.get(k):
            ks.append((k, r[k]))
    nt = norm_title(r["title"])
    if len(nt.split()) >= 3:
        ks.append(("t", nt))
    na = norm_title(r["abstract"])
    if len(na) >= 200:
        ks.append(("a", hashlib.md5(na.encode()).hexdigest()))
    return ks


def cluster(rows):
    parent = list(range(len(rows)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    seen = {}
    for i, r in enumerate(rows):
        for k in keys_of(r):
            if k in seen:
                parent[find(i)] = find(seen[k])
            else:
                seen[k] = i
    groups = collections.defaultdict(list)
    for i in range(len(rows)):
        groups[find(i)].append(i)
    return list(groups.values())


def merge_group(rs):
    out = {"arxiv": None, "doi": None, "s2": None, "oa": None, "orid": None, "acl": None, "title": "", "abstract": "",
           "published": None, "venue": None, "found_by": [], "sources": [], "extra": {}}
    for r in sorted(rs, key=lambda x: (not x["abstract"], x["src"])):
        for k in ("arxiv", "doi", "s2", "oa", "orid", "acl", "venue"):
            out[k] = out[k] or r.get(k)
        out["title"] = out["title"] or r["title"]
        out["abstract"] = out["abstract"] or r["abstract"]
        if r.get("published") and (not out["published"] or len(r["published"]) > len(out["published"]) or r["published"] < out["published"] and len(r["published"]) == len(out["published"])):
            out["published"] = r["published"]
        out["found_by"].append(f"{r['src']}:{r['label']}")
        out["sources"].append(r["src"])
        for k, v in r["extra"].items():
            out["extra"].setdefault(k, v)
    out["sources"] = sorted(set(out["sources"]))
    out["found_by"] = sorted(set(out["found_by"]))
    return out


def main():
    # ---- existing records and their keys
    existing = [json.loads(l) for l in open(ROOT / "research/review/screening/records.jsonl", encoding="utf8")]
    ex_idx = {"arxiv": {}, "t": {}, "a": {}, "doi": {}}
    venues = json.load(open(CORPUS / "venues-semantic-scholar.json"))["records"]
    for e in existing:
        if e["arxiv"]:
            ex_idx["arxiv"][e["arxiv"]] = e["sid"]
            d = (venues.get(e["arxiv"]) or {}).get("doi")
            if d:
                ex_idx["doi"][d.lower()] = e["sid"]
        ex_idx["t"].setdefault(norm_title(e["title"]), e["sid"])
        na = norm_title(e["abstract"])
        if len(na) >= 200:
            ex_idx["a"].setdefault(hashlib.md5(na.encode()).hexdigest(), e["sid"])
    ex_tsets = [(e["sid"], tset(e["title"])) for e in existing]
    inv = collections.defaultdict(set)
    for sid, ts in ex_tsets:
        for w in ts:
            inv[w].add(sid)
    tset_by_sid = dict(ex_tsets)

    def existing_match(r):
        if r["arxiv"] and r["arxiv"] in ex_idx["arxiv"]:
            return ex_idx["arxiv"][r["arxiv"]], "arxiv"
        if r["doi"] and r["doi"] in ex_idx["doi"]:
            return ex_idx["doi"][r["doi"]], "doi"
        nt = norm_title(r["title"])
        if len(nt.split()) >= 3 and nt in ex_idx["t"]:
            return ex_idx["t"][nt], "title"
        na = norm_title(r["abstract"])
        if len(na) >= 200 and hashlib.md5(na.encode()).hexdigest() in ex_idx["a"]:
            return ex_idx["a"][hashlib.md5(na.encode()).hexdigest()], "abstract"
        return None, None

    def near(r):
        ts = tset(r["title"])
        if len(ts) < 4:
            return None
        cand = collections.Counter(s for w in ts for s in inv.get(w, ()))
        best = None
        for s, c in cand.most_common(8):
            u = len(ts | tset_by_sid_title(s))
            j = len(ts & tset_by_sid_title(s)) / u if u else 0
            if j >= 0.8 and (best is None or j > best[1]):
                best = (s, j)
        return best[0] if best else None

    def tset_by_sid_title(s):
        return tset_by_sid[s]

    # ---- raw files from the log
    rows = [json.loads(l) for l in open(ss.LOG, encoding="utf8") if l.strip()]
    mine = [r for r in rows if r["executed_utc"].startswith(DATE) and r["export"].startswith("research/sources/search-raw/")]
    latest_oa = {}
    for r in mine:
        if r["database"].startswith("OpenAlex"):
            latest_oa[r["string"]] = r["export"]
    per_source = collections.OrderedDict()   # src -> list of rec
    src_notes = collections.defaultdict(dict)
    for r in mine:
        p = ROOT / r["export"]
        db, name = r["database"], r["string"]
        if not p.exists():
            continue
        if db.startswith("OpenAlex"):
            if latest_oa[name] != r["export"]:
                continue
            src, rs = "openalex", parse_oa(p, name, "openalex")
        elif db.startswith("Semantic Scholar Graph API (paper/search/bulk)"):
            src, rs = "semantic-scholar-bulk", parse_s2(p, name, "semantic-scholar-bulk")
        elif db.startswith("arXiv"):
            src, rs = "arxiv-protocol-rerun", parse_arxiv(p, name, "arxiv-protocol-rerun")
        elif db.startswith("ACL"):
            src, rs = "acl-anthology", parse_acl(p, name, "acl-anthology")
        elif db.startswith("OpenReview"):
            st = src_notes["openreview"].setdefault("stats", collections.Counter())
            src, rs = "openreview", parse_orv(p, name, "openreview", st)
        elif "snowball" in name:
            src = name.replace("snowball-", "snowball-")
            st = src_notes[src].setdefault("stats", collections.Counter())
            rs = parse_snow(p, name, src, st)
        else:
            continue
        per_source.setdefault(src, []).extend(rs)

    # ---- per source stats
    report = {"date": ISO, "existing_records": len(existing), "sources": {}}
    all_new_rows = []
    for src, rs in per_source.items():
        cl = cluster(rs)
        uniq = [merge_group([rs[i] for i in g]) for g in cl]
        n_ex = sum(1 for u in uniq if existing_match({**u, "title": u["title"], "abstract": u["abstract"]})[0])
        by_string = collections.Counter(r["label"].split(":")[0] for r in rs)
        rep = {"identified": len(rs), "identified_by_string": dict(by_string), "unique_within_source": len(uniq),
               "duplicates_within_source": len(rs) - len(uniq), "duplicates_against_existing": n_ex,
               "new": len(uniq) - n_ex}
        if "stats" in src_notes[src]:
            rep["filter_stats"] = dict(src_notes[src]["stats"])
        report["sources"][src] = rep
        for u in uniq:
            m, how = existing_match(u)
            if not m:
                all_new_rows.append(u)

    # ---- union of new records across sources (dedupe again across sources)
    flat = []
    for u in all_new_rows:
        flat.append({**u, "src": ",".join(u["sources"]), "label": ""})
    cl = cluster(flat)
    union = []
    for g in cl:
        rs = [flat[i] for i in g]
        m = merge_group(rs)
        m["sources"] = sorted({s for r in rs for s in r["sources"]})
        m["found_by"] = sorted({f for r in rs for f in r["found_by"]})
        union.append(m)
    union.sort(key=lambda r: (r["arxiv"] or "9999", norm_title(r["title"])))
    excl = collections.Counter()
    out_path = CORPUS / f"new-records-{ISO}.jsonl"
    with out_path.open("w", encoding="utf8") as fh:
        for i, u in enumerate(union, 1):
            text = u["title"] + " " + u["abstract"] + " " + " ".join((u["extra"].get("keywords") or []))
            pm = {"S1": ss.matches("S1", text), "S2": ss.matches("S2", text)}
            nr = near(u)
            if len(u["sources"]) == 1:
                excl[u["sources"][0]] += 1
            rec_out = {"nid": f"N{i:05d}", "arxiv": u["arxiv"], "doi": u["doi"], "s2_id": u["s2"], "openalex_id": u["oa"],
                       "openreview_id": u["orid"], "acl_id": u["acl"], "title": u["title"], "abstract": u["abstract"],
                       "published": u["published"], "venue": u["venue"], "sources": u["sources"], "found_by": u["found_by"],
                       "protocol_string_match": pm, "possible_duplicate_of": nr, "extra": u["extra"] or None}
            fh.write(json.dumps(rec_out, ensure_ascii=False) + "\n")
    report["union_new_records"] = len(union)
    report["union_new_by_source_combination"] = dict(collections.Counter("+".join(u["sources"]) for u in union))
    report["exclusive_new_by_source"] = dict(excl)
    report["union_new_matching_S1_or_S2_locally"] = None
    n_match = sum(1 for l in open(out_path, encoding="utf8") if (lambda d: d["protocol_string_match"]["S1"] or d["protocol_string_match"]["S2"])(json.loads(l)))
    report["union_new_matching_S1_or_S2_locally"] = n_match
    new_db = [u for u in union if set(u["sources"]) - {"snowball-backward", "snowball-forward"}]
    report["union_new_from_database_searches_only"] = len(new_db)
    report["union_new_without_abstract"] = sum(1 for u in union if not u["abstract"])
    report["new_records_file"] = out_path.relative_to(ROOT).as_posix()
    report["new_records_sha256"] = hashlib.sha256(out_path.read_bytes()).hexdigest()
    report["records_jsonl_sha256_unchanged"] = hashlib.sha256((ROOT / "research/review/screening/records.jsonl").read_bytes()).hexdigest()
    report["dedup_rules"] = ("keys in order: arXiv ID (version stripped), DOI (via S2 venue file for existing records), normalised title "
                             "(>=3 words), normalised abstract (>=200 characters); union-find within and across sources; "
                             "possible_duplicate_of = title token-set Jaccard >= 0.8 against an existing record (flag only, not dropped)")
    (CORPUS / f"new-records-dedup-report-{ISO}.json").write_text(json.dumps(report, indent=2), encoding="utf8")

    # ---- pilot recall
    recall(per_source, existing)
    print(json.dumps(report, indent=2))


def venue_in_scope(v, kind):
    v = v or ""
    if kind == "openreview":
        return bool(re.search(r"ICLR|Learning Representations|NeurIPS|Neural Information Processing|ICML|International Conference on Machine Learning|Transactions on Machine Learning|TMLR", v))
    return bool(re.search(r"\bACL\b|EMNLP|NAACL|EACL|COLING|Findings|Computational Linguistics|Association for Computational|Empirical Methods|LREC|CoNLL|AACL|IJCNLP", v))


def recall(per_source, existing):
    aw = [json.loads(l) for l in open(CORPUS / "awesome-dlms@194aa6bd.jsonl", encoding="utf8")]
    venues = json.load(open(CORPUS / "venues-semantic-scholar.json"))["records"]

    def sid_of(a):
        c = a["canonical_id"]
        return re.sub(r"v\d+$", "", c[6:]) if c.startswith("arXiv:") else None

    seed = []
    for a in aw:
        ax = a.get("arxiv") or {}
        seed.append({"arxiv": sid_of(a), "title": ax.get("title") or a["title"], "abstract": ax.get("abstract") or "",
                     "mm": "Multimodal DLMs" in a["sections"], "venue": (venues.get(sid_of(a)) or {}).get("venue")})
    arx = [s for s in seed if s["arxiv"]]
    mm = [s for s in arx if s["mm"]]
    others = sorted((s for s in arx if not s["mm"]), key=lambda s: s["arxiv"])
    r50 = random.Random(20261015).sample(others, 50)
    sets = {"MM28": mm, "random50_other": r50, "all540_arxiv": arx}
    # retrieved sets per source and string
    ret = collections.defaultdict(lambda: collections.defaultdict(lambda: (set(), set())))
    for src, rs in per_source.items():
        if src.startswith("snowball"):
            continue
        for r in rs:
            nm = r["label"].split(":")[0]
            for key in (nm, "S1|S2"):
                a, t = ret[src][key]
                if r["arxiv"]:
                    a.add(r["arxiv"])
                t.add(norm_title(r["title"]))
    for f in sorted(CORPUS.glob("arxiv-S*-*.jsonl")):
        nm = f.stem.split("-")[1]
        for l in open(f, encoding="utf8"):
            r = json.loads(l)
            for key in (nm, "S1|S2"):
                a, t = ret["arxiv-existing-logged"][key]
                a.add(re.sub(r"v\d+$", "", r["arxiv"]))
                t.add(norm_title(r["title"]))
    for key in ("S1", "S2", "S1|S2"):                      # all sources combined (new database searches + earlier arXiv runs)
        A, T = set(), set()
        for src in list(ret):
            a, t = ret[src][key] if key in ret[src] else (set(), set())
            A |= a
            T |= t
        ret["ALL-COMBINED"][key] = (A, T)
    out = {"date": ISO, "seed_list": "Awesome-DLMs@194aa6bd: 572 records, 540 with arXiv IDs; recall is over the 540 arXiv-ID records",
           "random_seed": 20261015, "random50_note": "50 drawn without replacement from the 512 non-'Multimodal DLMs' arXiv records, sorted by arXiv ID, random.Random(20261015).sample",
           "matching": "arXiv ID where the source has one, else normalised title; snowballing excluded (seeds are cited by construction)",
           "local_string_recall": {}, "by_source": {}, "scope_restricted_recall": {}, "missed_MM28_combined": [], "missed_by_string_logic": {}}
    for sname, S in sets.items():
        out["local_string_recall"][sname] = {k: sum(1 for s in S if (ss.matches("S1", s["title"] + " " + s["abstract"]) if k == "S1" else
                                             ss.matches("S2", s["title"] + " " + s["abstract"]) if k == "S2" else
                                             ss.matches("S1", s["title"] + " " + s["abstract"]) or ss.matches("S2", s["title"] + " " + s["abstract"])))
                                             for k in ("S1", "S2", "S1|S2")} | {"n": len(S)}
    for src in ret:
        out["by_source"][src] = {}
        for key, (A, T) in ret[src].items():
            out["by_source"][src][key] = {"retrieved_titles": len(T)}
            for sname, S in sets.items():
                out["by_source"][src][key][sname] = f"{sum(1 for s in S if s['arxiv'] in A or norm_title(s['title']) in T)}/{len(S)}"
    for kind, src in (("openreview", "openreview"), ("acl", "acl-anthology")):
        if src in ret:
            A, T = ret[src]["S1|S2"]
            inscope = [s for s in arx if venue_in_scope(s["venue"], kind)]
            out["scope_restricted_recall"][src] = {
                "definition": "seeds whose Semantic Scholar venue string (venues-semantic-scholar.json, 2026-10-14) matches the source's venue family by regex (heuristic)",
                "seeds_in_scope": len(inscope), "retrieved": sum(1 for s in inscope if s["arxiv"] in A or norm_title(s["title"]) in T)}
    A, T = ret["ALL-COMBINED"]["S1|S2"]
    out["missed_MM28_combined"] = [{"arxiv": s["arxiv"], "title": s["title"], "matches_S1_locally": ss.matches("S1", s["title"] + " " + s["abstract"]),
                                    "matches_S2_locally": ss.matches("S2", s["title"] + " " + s["abstract"])}
                                   for s in mm if not (s["arxiv"] in A or norm_title(s["title"]) in T)]
    miss_all = [s for s in arx if not (s["arxiv"] in A or norm_title(s["title"]) in T)]
    out["missed_by_string_logic"] = {"all540_missed_by_combined_searches": len(miss_all),
                                     "of_which_text_matches_neither_string_locally": sum(1 for s in miss_all if not (ss.matches("S1", s["title"] + " " + s["abstract"]) or ss.matches("S2", s["title"] + " " + s["abstract"]))),
                                     "of_which_text_matches_a_string_locally_but_not_retrieved": sum(1 for s in miss_all if (ss.matches("S1", s["title"] + " " + s["abstract"]) or ss.matches("S2", s["title"] + " " + s["abstract"])))}
    (CORPUS / f"pilot-recall-{ISO}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf8")


if __name__ == "__main__":
    main()
