"""E-gateway full texts (user approved 2026-10-17): the user's Chrome with VIT access, driven by Claude in Chrome,
saves each publisher PDF as <id>.pdf in the user's Downloads folder; this script files them.

  python tools/egateway_import.py plan     -> research/review/fulltext/egateway-plan.json: per record of
                                              egateway-list.csv the publisher PDF path to fetch in the browser
                                              (IEEE arnumber from the doi.org redirect header, no body read;
                                              Springer /content/pdf/<doi>.pdf; ACM /doi/pdf/<doi>; others: page)
  python tools/egateway_import.py import   -> unpacks Downloads/egateway-*.tar (one per site, built in the page),
                                              then moves Downloads/<id>.pdf (ids of the list only, must start with
                                              %PDF) to research/sources/pdfs/fulltext/<id>.pdf and appends a
                                              fetch-log.jsonl row (route 'e-gateway-chrome', sha256)
  python tools/egateway_import.py remaining -> research/review/fulltext/egateway-manual.csv: list records still
                                              without a PDF, with what the browser showed for that publisher
Nothing is downloaded by this script.
"""
import csv
import datetime as dt
import hashlib
import json
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FT = ROOT / "research/review/fulltext"
LIST = FT / "egateway-list.csv"
PLAN = FT / "egateway-plan.json"
LOG = FT / "fetch-log.jsonl"
OUT = ROOT / "research/sources/pdfs/fulltext"
DL = Path.home() / "Downloads"
UA = "dlm-ft-routes/1.0 (metadata lookups for a literature review)"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def location(url, hops=4):
    """Follow redirects by reading Location headers only (HEAD); returns the last URL seen."""
    op = urllib.request.build_opener(NoRedirect)
    for _ in range(hops):
        try:
            op.open(urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA}), timeout=30)
            return url
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308) and e.headers.get("Location"):
                url = urllib.parse.urljoin(url, e.headers["Location"])
                continue
            return url
        except Exception:
            return url
    return url


def plan():
    rows = list(csv.DictReader(open(LIST, encoding="utf-8-sig")))
    out = []
    for r in rows:
        doi = (r["doi"] or "").lower()
        p = {"id": r["id"], "doi": doi, "publisher": r["publisher"], "site": None, "pdf_path": None}
        if doi.startswith("10.1109/"):
            final = location(f"https://doi.org/{doi}")
            num = final.rstrip("/").split("/document/")[-1].split("/")[0] if "/document/" in final else None
            p.update(site="https://ieeexplore.ieee.org", pdf_path=f"/stampPDF/getPDF.jsp?tp=&arnumber={num}&ref=" if num else None,
                     resolved=final)
            time.sleep(1)
        elif doi.startswith(("10.1007/", "10.1186/")):
            p.update(site="https://link.springer.com", pdf_path=f"/content/pdf/{doi}.pdf")
        elif doi.startswith("10.1145/"):
            p.update(site="https://dl.acm.org", pdf_path=f"/doi/pdf/{doi}")
        else:
            p.update(site=None, pdf_path=None, note="publisher page; PDF link found in the browser")
        out.append(p)
    PLAN.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    by = {}
    for p in out:
        by[p["site"] or "page"] = by.get(p["site"] or "page", 0) + 1
    print(json.dumps({"n": len(out), "by_site": by, "ieee_unresolved": [p["id"] for p in out
                      if p["site"] == "https://ieeexplore.ieee.org" and not p["pdf_path"]]}))


def unpack_archives(rows):
    """Chrome lets a page start one automatic download, so the page packs one site's PDFs into a single tar
    (Downloads/egateway-<site>-<n>.tar). Members must be named <id>.pdf with an id of the list; anything else
    is skipped and reported. Unpacked files are written to Downloads/<id>.pdf for the import step."""
    import tarfile
    for t in sorted(DL.glob("egateway-*.tar")):
        skipped = []
        with tarfile.open(t) as tf:
            for m in tf.getmembers():
                stem = m.name[:-4] if m.name.endswith(".pdf") else None
                if not m.isfile() or "/" in m.name or "\\" in m.name or stem not in rows:
                    skipped.append(m.name); continue
                dst = DL / m.name
                if not dst.exists():
                    dst.write_bytes(tf.extractfile(m).read())
        done = DL / "egateway-imported"; done.mkdir(exist_ok=True)
        shutil.move(str(t), done / t.name)
        print(f"{t.name}: unpacked, skipped {skipped}")


def do_import():
    rows = {r["id"]: r for r in csv.DictReader(open(LIST, encoding="utf-8-sig"))}
    manual = {}   # later tranches' hand-download lists (egateway-manual-<tranche>.csv, 2026-10-20): the user saves by hand
    for f in sorted(FT.glob("egateway-manual-*.csv")):
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            if r["id"] not in rows:
                manual[r["id"]] = r
    rows.update(manual)
    unpack_archives(rows)
    have = {json.loads(l)["id"] for l in LOG.read_text(encoding="utf8").splitlines()
            if l.strip() and json.loads(l).get("status") == "ok"}
    n = 0
    for i, r in rows.items():
        src = DL / f"{i}.pdf"
        if not src.exists() or i in have:
            continue
        b = src.read_bytes()
        rec = {"id": i, "route": "e-gateway-manual" if i in manual else "e-gateway-chrome",
               "url": f"https://doi.org/{r['doi']}" if r["doi"] else r["url"],
               "note": "saved by the user by hand through the VIT e-gateway, moved here" if i in manual else
                       "user's Chrome with VIT access (Claude in Chrome), saved to Downloads, moved here"}
        if not b.startswith(b"%PDF"):
            rec.update(status="not_pdf", bytes=len(b))
        else:
            OUT.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), OUT / f"{i}.pdf")
            rec.update(status="ok", bytes=len(b), sha256=hashlib.sha256(b).hexdigest())
            n += 1
        rec["ts"] = dt.datetime.now().isoformat(timespec="seconds")
        with LOG.open("a", encoding="utf8") as fh:
            fh.write(json.dumps(rec) + "\n")
    print(f"imported {n}")


# What Claude in Chrome observed per site on 2026-10-17 (user's Chrome, VIT access); the reason column of the list.
SEEN = {
    "https://link.springer.com": "Springer: chapters show no VIT access (purchase page); journal PDFs returned HTML or "
                                 "HTTP 503 after a burst of requests and the VIT access line then disappeared; "
                                 "automated access stopped; download by hand",
    "https://dl.acm.org": "ACM: PDF fetched in the page but Chrome saved no file (downloads from dl.acm.org seem "
                          "blocked in this Chrome); download by hand",
    "elsevier": "ScienceDirect: Cloudflare 'Just a moment' check in the automated tab, not answered; download by hand",
    None: "not attempted in the browser (publisher page only); download by hand",
}


def remaining():
    plan_rows = {p["id"]: p for p in json.loads(PLAN.read_text(encoding="utf-8"))}
    have = {json.loads(l)["id"] for l in LOG.read_text(encoding="utf8").splitlines()
            if l.strip() and json.loads(l).get("status") == "ok"}
    out = []
    for r in csv.DictReader(open(LIST, encoding="utf-8-sig")):
        if r["id"] in have:
            continue
        site = plan_rows[r["id"]]["site"]
        key = "elsevier" if (r["doi"] or "").startswith("10.1016/") else site
        out.append({"id": r["id"], "title": r["title"], "doi": r["doi"], "publisher": r["publisher"],
                    "url": r["url"], "reason": SEEN.get(key, SEEN[None]),
                    "save_as": f"Downloads/{r['id']}.pdf (then tell Claude: tools/egateway_import.py import)"})
    with open(FT / "egateway-manual.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]) if out else ["id"]); w.writeheader(); w.writerows(out)
    by = {}
    for o in out:
        by[o["reason"][:20]] = by.get(o["reason"][:20], 0) + 1
    print(json.dumps({"remaining": len(out), "by_reason": by}))


if __name__ == "__main__":
    {"plan": plan, "import": do_import, "remaining": remaining}[sys.argv[1]]()
