"""Revision 2026-10-21 (assessment, related work): verify the added references against the arXiv API and
append @misc entries to references.bib. Each id's arXiv title must contain the expected title words, else the
script stops. Writes the verification log to research/review/audits/2026-10-21-revision-refs.json.

    python paper/review/scripts/revision_refs.py   (from the repository root)
"""
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BIB = ROOT / "paper/review/references.bib"
EXPECT = {   # id: words that must occur in the arXiv title (lower case)
    "2410.18514": "scaling up masked diffusion models on text",
    "2602.15014": "scaling beyond masked diffusion language models",
    "2507.15857": "diffusion beats autoregressive",
    "2511.03276": "super data learners",
    "2604.02560": "dependency-guided parallel decoding",
    "2605.24697": "token-commitment policy",
    "2602.19619": "is your diffusion sampler actually correct",
    "2606.12232": "re-evaluating confidence remasking",
    "2604.11748": "langflow",
    "2603.02547": "codar",
    "2605.15609": "pareto frontier of diffusion llms",
    "2609.20539": "parallelism, critical windows",
    "2609.40362": "multimodal flow: unified flow modeling",
}
NS = {"a": "http://www.w3.org/2005/Atom"}
url = "http://export.arxiv.org/api/query?max_results=50&id_list=" + ",".join(EXPECT)
xml = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "dlm-review-refcheck"}), timeout=60).read()
root = ET.fromstring(xml)
found, log = {}, {}
for e in root.findall("a:entry", NS):
    aid = re.sub(r"v\d+$", "", e.find("a:id", NS).text.rsplit("/abs/", 1)[1])
    title = " ".join(e.find("a:title", NS).text.split())
    authors = [a.find("a:name", NS).text for a in e.findall("a:author", NS)]
    year = e.find("a:published", NS).text[:4]
    cat = e.find("{http://arxiv.org/schemas/atom}primary_category").get("term")
    found[aid] = (title, authors, year, cat)
bib = BIB.read_text(encoding="utf-8")
add = []
for aid, words in EXPECT.items():
    if aid not in found:
        raise SystemExit(f"not found on arXiv: {aid}")
    title, authors, year, cat = found[aid]
    if words not in title.lower():
        raise SystemExit(f"title mismatch {aid}: {title}")
    log[aid] = {"title": title, "authors": authors, "year": year, "status": "arXiv metadata OK 2026-10-21"}
    if f"{{arXiv:{aid}," in bib:
        continue
    t = title.replace("&", r"\&")
    add.append(f"@misc{{arXiv:{aid},\n  author = {{{' and '.join(authors)}}},\n  title = {{{{{t}}}}},\n  year = {{{year}}},\n"
               f"  eprint = {{{aid}}},\n  archivePrefix = {{arXiv}},\n  primaryClass = {{{cat}}},\n"
               f"  howpublished = {{arXiv preprint arXiv:{aid}}},\n}}\n\n% checked 2026-10-21: arXiv metadata OK (revision refs)\n")
if add:
    BIB.write_text(bib.rstrip("\n") + "\n\n" + "\n".join(add), encoding="utf-8")
out = ROOT / "research/review/audits/2026-10-21-revision-refs.json"
out.write_text(json.dumps(log, indent=1, ensure_ascii=False), encoding="utf-8")
for aid, x in log.items():
    print(aid, x["year"], "|", x["title"], "|", x["authors"][0], "et al." if len(x["authors"]) > 1 else "")
print("added", len(add))
