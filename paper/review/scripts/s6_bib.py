"""BibTeX entries for the studies of Supplement Table S6 (the 80 appraised studies), fetched from the source of
record and checked against the review's own record title.

    python -E -P paper/review/scripts/s6_bib.py

For each id of analysis/extraction/d0052/qa-table.jsonl: arXiv id (corpus record, census row, or an arxiv.org URL in
the fetch log) -> arXiv API; else DOI -> Crossref; else OpenReview forum id (fetch log) -> OpenReview API. An entry is
kept only if the fetched title matches the record title (normalised similarity >= 0.90). Writes
paper/review/tables/s6-keys.json (id -> key, source, similarity) and paper/review/s6-refs.bib; failures are listed in
s6-keys.json and get no citation. Existing keys in references.bib are reused, not duplicated.
"""
import difflib
import glob
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "paper/review"
UA = {"User-Agent": "dlm-review-prisma/1.0 (mailto:shlok.goenka2023@vitstudent.ac.in)"}


def jl(p):
    out = []
    for l in open(p, encoding="utf-8"):
        if l.strip():
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError:
                pass
    return out


ids = [r["id"] for r in jl(ROOT / "analysis/extraction/d0052/qa-table.jsonl")]
title, arx, doi, orv = {}, {}, {}, {}
for f in sorted(glob.glob(str(ROOT / "research/review/corpus/*.jsonl"))) + [str(ROOT / "research/review/fulltext/ft-routes.jsonl")]:
    for d in jl(f):
        i = d.get("id")
        if i not in ids:
            continue
        if d.get("title"):
            title.setdefault(i, d["title"])
        if d.get("arxiv"):
            arx.setdefault(i, str(d["arxiv"]).split("v")[0] if re.match(r"\d{4}\.\d{4,5}", str(d["arxiv"])) else None)
        if d.get("doi"):
            doi.setdefault(i, re.sub(r"^https?://(dx\.)?doi\.org/", "", d["doi"]))
for d in jl(ROOT / "research/review/census/census-random-final.jsonl"):
    if d.get("sid") in ids and d.get("arxiv"):
        arx[d["sid"]] = d["arxiv"]
for line in (ROOT / "research/review/census/census-order.csv").read_text(encoding="utf-8").splitlines()[1:]:
    rank, sid, a, t = line.split(",", 3)
    if sid in ids:
        title.setdefault(sid, t.strip().strip('"'))
for d in jl(ROOT / "research/review/fulltext/fetch-log.jsonl"):
    i, u = d.get("id"), str(d.get("url") or "")
    if i not in ids or d.get("status") != "ok":
        continue
    m = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", u)
    if m:
        arx.setdefault(i, m.group(1))
    m = re.search(r"openreview\.net/(?:pdf|forum)\?id=([A-Za-z0-9_-]+)", u) or re.match(r"openreview note (\S+)", u)
    if m:
        orv.setdefault(i, m.group(1))
for i in ids:  # arXiv DOIs
    if not arx.get(i) and doi.get(i):
        m = re.search(r"arxiv\.(\d{4}\.\d{4,5})", doi[i], re.I)
        if m:
            arx[i] = m.group(1)


def get(url, accept=None):
    h = dict(UA)
    if accept:
        h["Accept"] = accept
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=40) as r:
                return r.read()
        except Exception:
            time.sleep(3 * (k + 1))
    return None


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def tex(s):
    s = re.sub(r"\s+", " ", s or "").strip()
    for a, b in (("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"), ("$", r"\$")):
        s = s.replace(a, b)
    return s


def from_arxiv(a):
    x = get(f"http://export.arxiv.org/api/query?id_list={a}")
    if not x:
        return None
    ns = {"a": "http://www.w3.org/2005/Atom"}
    e = ET.fromstring(x).find("a:entry", ns)
    if e is None or e.find("a:title", ns) is None:
        return None
    return {"title": e.find("a:title", ns).text, "authors": [n.text for n in e.findall("a:author/a:name", ns)],
            "year": e.find("a:published", ns).text[:4], "howpublished": f"arXiv preprint arXiv:{a}", "eprint": a}


def from_crossref(d):
    x = get("https://api.crossref.org/works/" + urllib.parse.quote(d))
    if not x:
        return None
    m = json.loads(x)["message"]
    au = [" ".join(p for p in (a.get("given"), a.get("family")) if p) for a in m.get("author", [])]
    yr = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
    venue = (m.get("container-title") or [""])[0]
    return {"title": (m.get("title") or [""])[0], "authors": au, "year": str(yr or ""), "venue": venue, "doi": d}


def from_openreview(f):
    for base in ("https://api2.openreview.net", "https://api.openreview.net"):
        x = get(f"{base}/notes?id={f}")
        if not x:
            continue
        n = (json.loads(x).get("notes") or [None])[0]
        if not n:
            continue
        c = n.get("content", {})
        v = lambda k: (c.get(k) or {}).get("value") if isinstance(c.get(k), dict) else c.get(k)
        yr = time.gmtime((n.get("pdate") or n.get("cdate") or n.get("tcdate") or 0) / 1000).tm_year
        venue = v("venue") or ""
        return {"title": v("title"), "authors": v("authors") or [], "year": str(yr), "venue": venue,
                "url": f"https://openreview.net/forum?id={f}"}
    return None


bib_text = (P / "references.bib").read_text(encoding="utf-8")
have = set(re.findall(r"@\w+\{([^,]+),", bib_text))
log, entries = {}, []
for i in ids:
    tries = []
    if arx.get(i):
        tries.append(("arXiv:" + arx[i], "arxiv", lambda a=arx[i]: from_arxiv(a)))
    if doi.get(i) and not re.search(r"arxiv", doi[i], re.I):
        tries.append(("doi:" + doi[i], "crossref", lambda d=doi[i]: from_crossref(d)))
    if orv.get(i):
        tries.append(("openreview:" + orv[i], "openreview", lambda f=orv[i]: from_openreview(f)))
    rec = None
    for key, srcname, fn in tries:
        if key in have:
            rec = {"key": key, "source": "existing", "similarity": None}
            break
        m = fn()
        time.sleep(1.0)
        if not m or not m.get("title") or not m.get("authors"):
            continue
        s = sim(m["title"], title.get(i, ""))
        if s >= 0.90:
            rec = {"key": key, "source": srcname, "similarity": round(s, 3)}
            fields = [f"  author = {{{tex(' and '.join(m['authors']))}}}", f"  title = {{{{{tex(m['title'])}}}}}",
                      f"  year = {{{m['year']}}}"]
            if srcname == "arxiv":
                fields += [f"  eprint = {{{m['eprint']}}}", "  archivePrefix = {arXiv}", f"  howpublished = {{{m['howpublished']}}}"]
                typ = "misc"
            elif srcname == "crossref":
                fields += [f"  journal = {{{tex(m['venue'])}}}" if m["venue"] else None, f"  doi = {{{m['doi']}}}"]
                typ = "article" if m["venue"] else "misc"
            else:
                fields += [f"  howpublished = {{{tex(m['venue']) or 'OpenReview'}}}", f"  url = {{{m['url']}}}"]
                typ = "misc"
            entries.append(f"% fetched {time.strftime('%Y-%m-%d')} from {srcname}; title similarity to record {i}: {s:.3f}\n"
                           f"@{typ}{{{key},\n" + ",\n".join(x for x in fields if x) + ",\n}\n")
            have.add(key)
            break
        rec = rec or {"key": None, "source": srcname, "similarity": round(s, 3), "fetched_title": m["title"]}
    log[i] = rec or {"key": None, "source": None, "reason": "no identifier resolved"}
    print(i, log[i])
(P / "s6-refs.bib").write_text("% generated by scripts/s6_bib.py; do not edit\n\n" + "\n".join(entries), encoding="utf-8")
(P / "tables/s6-keys.json").write_text(json.dumps({"record_titles": title, "keys": log}, indent=1), encoding="utf-8")
print("cited:", sum(1 for v in log.values() if v.get("key")), "of", len(ids), "| new entries:", len(entries))
