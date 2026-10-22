"""Paper 2 scoping (2026-10-22): arXiv search for work related to the professor's sources (Omni-Diffusion,
Sparse-LaViDa, LaViDa, LaViDa-O, Apple tri-modal MDM). Writes research/paper2/related-arxiv-2026-10-22.md and marks
papers already cited in the survey bibliography. Metadata only; no full texts downloaded.
    python -I research/paper2/related_search.py   (from the repository root)"""
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUERIES = [
    'abs:"masked diffusion" AND abs:multimodal AND (abs:unified OR abs:"any-to-any")',
    'abs:"discrete diffusion" AND (abs:speech OR abs:audio) AND abs:multimodal',
    'abs:"masked diffusion" AND (abs:"text-to-image" OR abs:"image generation") AND abs:understanding',
    'abs:"masked diffusion" AND abs:multimodal AND (abs:sparse OR abs:acceleration OR abs:"KV cache" OR abs:efficient)',
    'abs:"diffusion language model" AND (abs:vision OR abs:visual) AND abs:"discrete"',
]
NS = {"a": "http://www.w3.org/2005/Atom"}
bib = (ROOT / "paper/review/references.bib").read_text(encoding="utf-8") + (ROOT / "paper/review/s6-refs.bib").read_text(encoding="utf-8")
seen = {}
for q in QUERIES:
    url = "http://export.arxiv.org/api/query?sortBy=submittedDate&sortOrder=descending&max_results=25&search_query=" + urllib.parse.quote(q)
    x = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "dlm-review-research"}), timeout=60).read()
    for e in ET.fromstring(x).findall("a:entry", NS):
        aid = re.sub(r"v\d+$", "", e.find("a:id", NS).text.rsplit("/abs/", 1)[1])
        if aid in seen:
            continue
        seen[aid] = (" ".join(e.find("a:title", NS).text.split()), e.find("a:published", NS).text[:10],
                     e.find("a:author/a:name", NS).text, aid in bib)
    time.sleep(3)
rows = sorted(seen.items(), key=lambda kv: kv[1][1], reverse=True)
out = ["# Related arXiv papers for Paper 2 (masked discrete diffusion, unified multimodal)", "",
       "Retrieved 2026-10-22 from the arXiv API by research/paper2/related_search.py (five queries, 25 newest each).",
       "Metadata only: read before relying on any of them. 'In survey' = already cited in the survey bibliography.", "",
       "| arXiv | first version | first author | title | in survey |", "|---|---|---|---|---|"]
for aid, (title, date, first, cited) in rows:
    out.append(f"| [{aid}](https://arxiv.org/abs/{aid}) | {date} | {first} | {title} | {'yes' if cited else ''} |")
(ROOT / "research/paper2/related-arxiv-2026-10-22.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(len(rows), "papers;", sum(v[3] for v in seen.values()), "already in the survey")
