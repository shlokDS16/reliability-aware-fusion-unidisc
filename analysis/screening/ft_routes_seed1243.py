"""Full-text access routes (metadata only, nothing downloaded) for tranche S1243 (D0037, 2026-10-20): the seed-corpus
records (research/review/screening/records.jsonl, round 1) that passed title/abstract screening (either screener
not 'exclude'; screener-A/B batch files).

Routes: arXiv id on the record -> arxiv. Records without one are the Awesome-DLMs list entries; their listed URL
(research/review/corpus/awesome-dlms@194aa6bd.jsonl, matched on the exact title) decides: openreview.net ->
openreview (note id from the URL), aclanthology.org -> acl, PeerJ/MDPI (open access) -> oa_url with the PDF URL,
a publisher site -> e-gateway, github.com ->
web_repository, any other page -> web_page (no PDF route; the human author decides how these are screened).
Duplicates: a seed pass whose arXiv id or normalised title equals a record already screened at full text (T1
decisions) or in the R797 tranche gets route_type 'duplicate' (not sought again); twins that were never
screened (auto-excluded copies, subscription records marked 'duplicate of records.jsonl') are listed in
twin_ids and the seed record stays the one screened.

Outputs: analysis/screening/ft-routes-seed1243.jsonl, ft-routes-seed1243-summary.json, s1243-tranche-ids.txt
(the tranche frame: every seed pass that is not a duplicate).

    python -I analysis/screening/ft_routes_seed1243.py
"""
import collections, glob, json, re, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCR, REV = ROOT / "analysis/screening", ROOT / "research/review"
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
na = lambda x: re.sub(r"v\d+$", "", (x or "").lower().replace("arxiv:", "").strip())
nt = lambda t: re.sub(r"[^a-z0-9]", "", (t or "").lower())

v1 = {r["sid"]: r for r in jl(REV / "screening/records.jsonl")}
A1 = {d["sid"]: d["decision"] for p in sorted(glob.glob(str(REV / "screening/screener-A/batch-*.jsonl"))) for d in jl(p)}
B1 = {d["sid"]: d["decision"] for p in sorted(glob.glob(str(REV / "screening/screener-B/batch-*.jsonl"))) for d in jl(p)}
assert set(A1) == set(B1) == set(v1)
passes = sorted(s for s in v1 if A1[s] != "exclude" or B1[s] != "exclude")

other = {r["nid"]: r for r in jl(REV / "corpus/new-records-2026-10-15-v2.jsonl")}
other.update({r["id"]: r for r in jl(REV / "corpus/subscription-records-2026-10-15.jsonl")})
by_ax, by_t = collections.defaultdict(set), collections.defaultdict(set)
for i, r in other.items():
    if r.get("arxiv"):
        by_ax[na(r["arxiv"])].add(i)
    if r.get("title"):
        by_t[nt(r["title"])].add(i)
t1 = {r["id"] for r in jl(SCR / "ft-t1/t1-decisions-all.jsonl")}
r797 = set((SCR / "r797-tranche-ids.txt").read_text(encoding="utf-8").split())
aw = collections.defaultdict(list)
for r in jl(REV / "corpus/awesome-dlms@194aa6bd.jsonl"):
    aw[nt(r["title"])].append(r)
PUB = ("sciencedirect.com", "springer.com", "ieeexplore.ieee.org", "dl.acm.org", "doi.org", "wiley.com", "tandfonline.com")

rows = []
for s in passes:
    r = v1[s]
    twins = sorted((by_ax.get(na(r.get("arxiv")), set()) if r.get("arxiv") else set()) | by_t.get(nt(r["title"]), set()))
    screened_twin = [i for i in twins if i in t1 or i in r797]
    row = {"id": s, "title": r["title"], "arxiv": r.get("arxiv"), "route_type": None, "url": None, "source_of_route": None,
           "twin_ids": twins, "duplicate_of": None}
    if screened_twin:
        row.update(route_type="duplicate", duplicate_of=screened_twin[0],
                   source_of_route=f"same paper as {screened_twin[0]} ({'T1, screened' if screened_twin[0] in t1 else 'R797 tranche'})")
    elif r.get("arxiv"):
        row.update(route_type="arxiv", url=f"https://arxiv.org/pdf/{r['arxiv']}", source_of_route="record arxiv field")
    else:
        hits = aw.get(nt(r["title"]), [])
        url = hits[0]["url"] if hits else None
        host = urllib.parse.urlparse(url or "").netloc.lower()
        if not url:
            row.update(route_type="no_identifier", source_of_route="no arxiv id; title not found in the Awesome-DLMs list")
        elif "openreview.net" in host:
            note = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get("id", [None])[0]
            row.update(route_type="openreview", url=f"https://openreview.net/pdf?id={note}" if note else url, source_of_route="Awesome-DLMs listed URL")
        elif "aclanthology.org" in host:
            row.update(route_type="acl", url=url if url.endswith(".pdf") else url.rstrip("/") + ".pdf", source_of_route="Awesome-DLMs listed URL")
        elif host.endswith("peerj.com") or host.endswith("mdpi.com"):   # open-access journals: PDF URL from the article URL
            pdf = url.rstrip("/") + (".pdf" if host.endswith("peerj.com") else "/pdf")
            row.update(route_type="oa_url", url=pdf, source_of_route="Awesome-DLMs listed URL (open-access journal; PDF URL pattern)")
        elif any(p in host for p in PUB):
            row.update(route_type="e-gateway", url=url, source_of_route="Awesome-DLMs listed URL (publisher site)")
        elif "github.com" in host:
            row.update(route_type="web_repository", url=url, source_of_route="Awesome-DLMs listed URL (code repository, no paper)")
        else:
            row.update(route_type="web_page", url=url, source_of_route="Awesome-DLMs listed URL (web page, no PDF route)")
    rows.append(row)

with open(SCR / "ft-routes-seed1243.jsonl", "w", encoding="utf-8", newline="\n") as fh:
    for row in rows:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
frame = sorted(r["id"] for r in rows if r["route_type"] != "duplicate")
(SCR / "s1243-tranche-ids.txt").write_text("\n".join(frame) + "\n", encoding="utf-8")
summary = {"seed_passes": len(rows), "by_route": dict(collections.Counter(r["route_type"] for r in rows)),
           "duplicates": {r["id"]: r["duplicate_of"] for r in rows if r["route_type"] == "duplicate"},
           "with_unscreened_twins": sum(1 for r in rows if r["twin_ids"] and r["route_type"] != "duplicate"),
           "tranche_frame_n": len(frame),
           "non_arxiv": [{k: r[k] for k in ("id", "title", "route_type", "url")} for r in rows if r["route_type"] not in ("arxiv", "duplicate")]}
(SCR / "ft-routes-seed1243-summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k != "non_arxiv"}))
for r in summary["non_arxiv"]:
    print(r["id"], r["route_type"], (r["url"] or "")[:70], "|", r["title"][:50])
