"""Full-text access routes (metadata only, nothing downloaded) for the re-check tranche: the 797 frame
candidates of criteria v1.6 s5.1, required at full text because K >= 1 (s5.2; ta-recheck-k.json).

Records already routed (ft-routes.jsonl, ft-routes-extra.jsonl) keep their route and are only flagged
(already_routed, already_screened_T1). Route order as in ft_routes_extra.py: arXiv -> OpenReview -> ACL ->
DOI via one batched anonymous OpenAlex filter per 50 DOIs (oa_url if an OA location has a PDF or landing
URL, else e-gateway with the publisher from the DOI prefix) -> no_identifier.

Outputs (orchestrator only; closed to the human author like the other re-check files):
  analysis/screening/ft-routes-recheck797.jsonl          one row per frame candidate
  analysis/screening/ft-routes-recheck797-summary.json   counts by route, by status

    python -I analysis/screening/ft_routes_recheck797.py
"""
import collections, hashlib, json, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCR, REV = ROOT / "analysis/screening", ROOT / "research/review"
FRAME = SCR / "ta-recheck-frame-v1.3-frozen.jsonl"
FRAME_SHA = "a9180fe4bdb7956b8d8e6c4340559c94ac4f877cbc6376d1dad99995bb32d79a"
PREFIX = {"10.1109": "IEEE", "10.1016": "Elsevier", "10.1007": "Springer Nature", "10.1038": "Springer Nature",
          "10.1145": "ACM", "10.1117": "SPIE", "10.1002": "Wiley", "10.1080": "Taylor & Francis",
          "10.3390": "MDPI", "10.18653": "ACL", "10.48550": "arXiv", "10.1609": "AAAI", "10.24963": "IJCAI"}
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]

assert hashlib.sha256(FRAME.read_bytes()).hexdigest() == FRAME_SHA, "frame file changed"
frame = [r["id"] for r in jl(FRAME)]
assert len(frame) == len(set(frame)) == 797, len(frame)
known = {r["id"]: r for r in jl(REV / "fulltext/ft-routes.jsonl")}
known.update({r["id"]: r for r in jl(SCR / "ft-routes-extra.jsonl")})
t1 = {r["id"] for r in jl(SCR / "ft-t1/t1-decisions-all.jsonl")}

meta = {}
for p, key in ((REV / "corpus/new-records-2026-10-15-v2.jsonl", "nid"), (REV / "screening/records.jsonl", "sid"),
               (REV / "corpus/subscription-records-2026-10-15.jsonl", "id")):
    for r in jl(p):
        if r[key] in frame and r[key] not in meta:
            meta[r[key]] = r
missing = sorted(set(frame) - set(meta))
assert not missing, missing[:20]

need = [i for i in frame if i not in known]
doi_only = sorted({meta[i]["doi"].lower() for i in need
                   if meta[i].get("doi") and not (meta[i].get("arxiv") or meta[i].get("openreview_id") or meta[i].get("acl_id"))})
oa = {}
for k in range(0, len(doi_only), 50):
    chunk = doi_only[k:k + 50]
    url = ("https://api.openalex.org/works?per-page=50&select=doi,open_access,best_oa_location&filter=doi:"
           + "|".join(urllib.parse.quote(d, safe="/.:()-_;") for d in chunk))
    req = urllib.request.Request(url, headers={"User-Agent": "dlm-ft-routes/1.0 (metadata lookups for a literature review)"})
    with urllib.request.urlopen(req, timeout=60) as fh:
        for w in json.load(fh)["results"]:
            oa[(w.get("doi") or "").lower().replace("https://doi.org/", "")] = w
    time.sleep(1)

rows = []
for i in sorted(frame):
    r = meta[i]; doi = (r.get("doi") or "").lower() or None
    row = {"id": i, "title": r.get("title"), "doi": doi, "publisher": None, "route_type": None, "url": None,
           "oa_status": None, "source_of_route": None, "already_routed": i in known, "already_screened_T1": i in t1}
    if i in known:
        k = known[i]
        row.update(route_type=k.get("route_type"), url=k.get("url"), publisher=k.get("publisher"),
                   source_of_route="existing route (ft-routes.jsonl or ft-routes-extra.jsonl)")
    elif r.get("arxiv"):
        row.update(route_type="arxiv", url=f"https://arxiv.org/pdf/{r['arxiv']}", source_of_route="record arxiv field")
    elif r.get("openreview_id"):
        row.update(route_type="openreview", url=f"https://openreview.net/pdf?id={r['openreview_id']}", source_of_route="record openreview_id field")
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
                row.update(route_type="oa_url", url=best.get("pdf_url") or best.get("landing_page_url"), source_of_route="OpenAlex best_oa_location")
            else:
                row.update(route_type="e-gateway", url=f"https://doi.org/{doi}", source_of_route="OpenAlex: not OA")
    else:
        row.update(route_type="no_identifier", source_of_route="no arxiv, openreview, acl or doi on the record")
    rows.append(row)

with open(SCR / "ft-routes-recheck797.jsonl", "w", encoding="utf-8", newline="\n") as fh:
    for row in rows:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
new = [r for r in rows if not r["already_routed"]]
summary = {"frame": len(rows), "already_screened_T1": sum(r["already_screened_T1"] for r in rows),
           "already_routed_not_screened": sum(r["already_routed"] and not r["already_screened_T1"] for r in rows),
           "new_routes": len(new), "new_by_route": dict(collections.Counter(r["route_type"] for r in new)),
           "new_e_gateway_by_publisher": dict(collections.Counter(r["publisher"] for r in new if r["route_type"] == "e-gateway")),
           "openalex_dois_queried": len(doi_only), "openalex_dois_found": len(oa)}
(SCR / "ft-routes-recheck797-summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
print(json.dumps(summary))
