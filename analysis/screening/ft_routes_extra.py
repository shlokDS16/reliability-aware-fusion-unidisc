"""Full-text access routes (metadata only, nothing downloaded) for the T1 records that ft-routes.jsonl lacks:
the title/abstract re-check sample (100, ta-recheck-sample-v1.3-frozen.json), the C8 records (32,
ta-recheck-c8-candidates-v1.4.jsonl) and the subscription title/abstract passes added after ft-routes.jsonl
was built (passed-ta.jsonl ids not in ft-routes.jsonl).

Route order: arXiv id -> arxiv; OpenReview id -> openreview; ACL id -> acl; DOI -> OpenAlex batched DOI
filter (one anonymous call, no key, no mailto) for open-access status: an OA location with a PDF or landing
URL -> oa_url, otherwise e-gateway with the publisher from the DOI prefix.

Outputs (orchestrator only; this folder is closed to the human author until the adjudication queue is done):
  analysis/screening/ft-routes-extra.jsonl            one row per record, with its group
  research/review/fulltext/egateway-list.csv          user-facing access list: every T1 record whose route
                                                      is e-gateway (ft-routes.jsonl and this file), id order,
                                                      no group, no screening field

    python analysis/screening/ft_routes_extra.py
"""
import collections
import csv
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCR = ROOT / "analysis/screening"
REV = ROOT / "research/review"
PREFIX = {"10.1109": "IEEE", "10.1016": "Elsevier", "10.1007": "Springer Nature", "10.1038": "Springer Nature",
          "10.1145": "ACM", "10.1117": "SPIE", "10.1002": "Wiley", "10.1080": "Taylor & Francis",
          "10.3390": "MDPI", "10.18653": "ACL", "10.48550": "arXiv", "10.1609": "AAAI", "10.24963": "IJCAI"}


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


ft = {r["id"]: r for r in jl(REV / "fulltext/ft-routes.jsonl")}
sample = json.load(open(SCR / "ta-recheck-sample-v1.3-frozen.json", encoding="utf-8"))["ids"]
c8 = [r["id"] for r in jl(SCR / "ta-recheck-c8-candidates-v1.4.jsonl")]
passes = [r["id"] for r in jl(REV / "screening/v2/dual-subscription/passed-ta.jsonl") if r["id"] not in ft]
group = collections.defaultdict(list)
for i in sample:
    group[i].append("recheck-sample")
for i in c8:
    group[i].append("c8")
for i in passes:
    group[i].append("ta-pass-unrouted")

meta = {}
for r in jl(REV / "corpus/new-records-2026-10-15-v2.jsonl"):
    if r["nid"] in group:
        meta[r["nid"]] = r
for r in jl(REV / "screening/records.jsonl"):
    if r["sid"] in group:
        meta[r["sid"]] = r
for r in jl(REV / "corpus/subscription-records-2026-10-15.jsonl"):
    if r["id"] in group:
        meta[r["id"]] = r
missing = sorted(set(group) - set(meta))
assert not missing, missing

doi_only = sorted({meta[i]["doi"].lower() for i in group
                   if meta[i].get("doi") and not (meta[i].get("arxiv") or meta[i].get("openreview_id") or meta[i].get("acl_id"))})
oa = {}
for k in range(0, len(doi_only), 50):
    chunk = doi_only[k:k + 50]
    url = ("https://api.openalex.org/works?per-page=50&select=doi,open_access,best_oa_location,primary_location&filter=doi:"
           + "|".join(urllib.parse.quote(d, safe="/.:()-_;") for d in chunk))
    req = urllib.request.Request(url, headers={"User-Agent": "dlm-ft-routes/1.0 (metadata lookups for a literature review)"})
    with urllib.request.urlopen(req, timeout=60) as fh:
        for w in json.load(fh)["results"]:
            oa[(w.get("doi") or "").lower().replace("https://doi.org/", "")] = w

rows = []
for i in sorted(group):
    r = meta[i]; doi = (r.get("doi") or "").lower() or None
    row = {"id": i, "group": "+".join(group[i]), "title": r.get("title"), "doi": doi, "publisher": None,
           "route_type": None, "url": None, "oa_status": None, "source_of_route": None}
    if r.get("arxiv"):
        row.update(route_type="arxiv", url=f"https://arxiv.org/pdf/{r['arxiv']}", source_of_route="record arxiv field")
    elif r.get("openreview_id"):
        row.update(route_type="openreview", url=f"https://openreview.net/pdf?id={r['openreview_id']}",
                   source_of_route="record openreview_id field")
    elif r.get("acl_id"):
        row.update(route_type="acl", url=f"https://aclanthology.org/{r['acl_id']}.pdf", source_of_route="record acl_id field")
    elif doi:
        row["publisher"] = PREFIX.get(doi.split("/")[0], "unknown")
        w = oa.get(doi)
        if w is None:
            row.update(route_type="e-gateway", url=f"https://doi.org/{doi}", source_of_route="DOI not found in OpenAlex")
        else:
            o = w.get("open_access") or {}; best = w.get("best_oa_location") or {}
            row["oa_status"] = o.get("oa_status")
            if o.get("is_oa") and (best.get("pdf_url") or best.get("landing_page_url")):
                row.update(route_type="oa_url", url=best.get("pdf_url") or best.get("landing_page_url"),
                           source_of_route="OpenAlex best_oa_location")
            else:
                row.update(route_type="e-gateway", url=f"https://doi.org/{doi}", source_of_route="OpenAlex: not OA")
    else:
        row.update(route_type="no_identifier", source_of_route="no arxiv, openreview, acl or doi on the record")
    rows.append(row)

with open(SCR / "ft-routes-extra.jsonl", "w", encoding="utf-8") as fh:
    for row in rows:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")

eg = [{"id": r["id"], "title": r["title"], "doi": r.get("doi"), "publisher": r.get("publisher"), "url": r.get("url")}
      for r in list(ft.values()) + rows if r["route_type"] == "e-gateway"]
eg.sort(key=lambda r: r["id"])
with open(REV / "fulltext/egateway-list.csv", "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=["id", "title", "doi", "publisher", "url", "downloaded"])
    w.writeheader()
    for r in eg:
        w.writerow({**r, "downloaded": ""})

summary = {"n": len(rows), "by_group": dict(collections.Counter(r["group"] for r in rows)),
           "by_route": dict(collections.Counter(r["route_type"] for r in rows)),
           "by_group_route": {f"{g}|{t}": n for (g, t), n in
                              sorted(collections.Counter((r["group"], r["route_type"]) for r in rows).items())},
           "e_gateway_new_by_publisher": dict(collections.Counter(r["publisher"] for r in rows if r["route_type"] == "e-gateway")),
           "egateway_list_total": len(eg), "openalex_dois_queried": len(doi_only), "openalex_dois_found": len(oa)}
(SCR / "ft-routes-extra-summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
print(json.dumps(summary))
