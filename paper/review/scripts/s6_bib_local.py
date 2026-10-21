"""Second pass of scripts/s6_bib.py for the S6 studies it could not resolve (run after it).

    python -E -P paper/review/scripts/s6_bib_local.py

OpenReview's API now answers scripted requests with a bot challenge, so OpenReview submissions are built from the
first page of the screened full text (research/sources/md/fulltext-pymupdf/<id>.txt): anonymous submissions as
"Anonymous", submitted to the venue the page header names (an ICLR submission is made in the autumn of the year
before the conference); papers whose first page names the authors with those authors. Every header string below is
asserted against the local text before an entry is written. R0963 (record title missing in s6_bib.py's sources) is
fetched from arXiv and checked against the title in ta-recheck-candidates-v1.2.jsonl. Appends to s6-refs.bib and
updates tables/s6-keys.json.
"""
import difflib
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / "paper/review"
TXT = ROOT / "research/sources/md/fulltext-pymupdf"
K = json.loads((P / "tables/s6-keys.json").read_text(encoding="utf-8"))

ANON = {  # id: (OpenReview forum id, venue header on page 1, title)
    "M12879": ("5zIRF3OVtd", "ICLR 2027"), "M12904": ("mPaaLb4tAX", "ICLR 2027"), "M13196": ("UNz3iuVVbo", "ICLR 2027"),
    "M13397": ("UUcPqCJLiM", "ICLR 2027"), "M13760": ("u8lN11Gqbx", "ICLR 2026"), "M13884": ("2Hw1zOBH3e", "ICLR 2027"),
    "M14000": ("UmdmJRGb9u", "ICLR 2026"), "M14293": ("fTscnIoaJx", "ICLR 2027"), "M14326": ("bVxla4Ov6X", "ICLR 2027"),
    "M14365": ("kBBg5ns9EU", "ICLR 2027"), "M14664": ("OXASG2dO4Z", "ICLR 2027"), "M15033": ("TDqycsDdqm", "ICLR 2027"),
    "M15781": ("IhQbFddkBp", "ICLR 2027"), "M15792": ("iMx3DYsxIj", "ICLR 2027"), "M15840": ("zEN2tdHWyN", "ICLR 2027"),
    "M15992": ("U2TiiqO18x", "ICLR 2027"), "M16080": ("db6NrHuZbK", "ICLR 2027"), "M16154": ("WztUti733r", "ICLR 2027"),
    "M16269": ("UE3okxYTUR", "ICLR 2025"), "M16729": ("Y6NULorfY2", "ICLR 2026"), "M17285": ("Sp0MJHtJYd", "ICLR 2027"),
    "M19012": ("LcOkxPiWv4", "ICLR 2026"), "M19293": ("TreNQ0xS5A", "ICLR 2027"), "M19013": ("3oLO4KQuhU", None),
}
NAMED = {  # id: (key, authors as printed on page 1, year, howpublished, url, page-1 strings that must be present)
    "M12476": ("openreview:3JM0DTKxgE", ["Gert Lek", "Chaoyi Zhu", "Pin-Yu Chen", "Robert Birke", "Lydia Y. Chen"], 2026,
               "ICLR 2026 Workshop on Test-Time Updates (TTU)", "https://openreview.net/forum?id=3JM0DTKxgE",
               ["ICLR 2026 Test-Time Updates (TTU) Workshop", "Gert Lek", "Lydia Y. Chen"]),
    "M17834": ("openreview:hZnibTOke7", ["Gabe Guo", "Stefano Ermon"], 2026, "International Conference on Learning Representations (ICLR 2026)",
               "https://openreview.net/forum?id=hZnibTOke7", ["Published as a conference paper at ICLR 2026", "Gabe Guo", "Stefano Ermon"]),
    "M18994": ("openreview:LV01JdxARe", ["Junzhe Li", "Sifan Zhou", "Liya Guo", "Xuerui Qiu", "Linrui Xu", "Delin Qu", "Tingting Long",
                                         "Chun Fan", "Hehe Fan", "Jun Liu", "Ming Li", "Shuicheng Yan"], 2026,
               "International Conference on Learning Representations (ICLR 2026)", "https://openreview.net/forum?id=LV01JdxARe",
               ["Published as a conference paper at ICLR 2026", "Junzhe Li", "Shuicheng Yan"]),
}
CLEAN_TITLE = {  # record titles with extraction or encoding damage
    "M15033": "GRAFT: Restoring the Missing Sampling Interface in Continuous Diffusion Language Models",
    "M15992": "M\\\"obius: A Unified Motion-Language Model Bridging Understanding and Generation",
    "M18994": "UniF$^2$ace: A Unified Fine-grained Face Understanding and Generation Model",
}


def page1(i):
    return re.sub(r"\s+", " ", (TXT / f"{i}.txt").read_text(encoding="utf-8", errors="replace")[:3000])


def tex(s):
    for a, b in (("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_")):
        s = s.replace(a, b)
    return s


def title(i):
    t = CLEAN_TITLE.get(i) or K["record_titles"].get(i, "")
    assert t and "�" not in t, (i, t)
    return t


entries = []
for i, (forum, venue) in ANON.items():
    h = page1(i)
    assert re.search(r"anonymous", h, re.I), i
    if venue:
        assert f"Under review as a conference paper at {venue}" in h, (i, venue)
        year = int(venue[-4:]) - 1
        how = f"Submitted to {venue} (under double-blind review), OpenReview"
    else:
        assert "Paper under double-blind review" in h, i
        year, how = 2026, "Paper under double-blind review, OpenReview"
    key = f"openreview:{forum}"
    entries.append((i, key, f"% built {i} from local full text page 1 (anonymous submission; OpenReview API blocked by a bot challenge)\n"
                    f"@misc{{{key},\n  author = {{Anonymous}},\n  title = {{{{{tex(title(i))}}}}},\n  year = {{{year}}},\n"
                    f"  howpublished = {{{how}}},\n  url = {{https://openreview.net/forum?id={forum}}},\n}}\n"))
for i, (key, au, year, how, url, must) in NAMED.items():
    h = page1(i)
    for m in must:
        assert m in h, (i, m)
    entries.append((i, key, f"% built {i} from local full text page 1 (authors and venue as printed there)\n"
                    f"@misc{{{key},\n  author = {{{' and '.join(au)}}},\n  title = {{{{{tex(title(i))}}}}},\n  year = {{{year}}},\n"
                    f"  howpublished = {{{how}}},\n  url = {{{url}}},\n}}\n"))
# M18816: doctoral dissertation (page 1 names author, institution and date)
h = page1("M18816")
assert "Dissertation submitted to the Faculty of the Virginia Polytechnic Institute and State University" in h and "Zhiyang Xu" in h
entries.append(("M18816", "xu2026unified", "% built M18816 from local full text page 1 (dissertation)\n"
                "@phdthesis{xu2026unified,\n  author = {Zhiyang Xu},\n  title = {{" + title("M18816") + "}},\n"
                "  school = {Virginia Polytechnic Institute and State University},\n  year = {2026},\n"
                "  url = {https://vtechworks.lib.vt.edu/bitstreams/34a72062-8fb0-4bbf-ba4e-f10826655b3e/download},\n}\n"))
# R0963 from arXiv
rt = next(json.loads(l)["title"] for l in open(ROOT / "analysis/screening/ta-recheck-candidates-v1.2.jsonl", encoding="utf-8")
          if '"R0963"' in l)
x = urllib.request.urlopen(urllib.request.Request("https://export.arxiv.org/api/query?id_list=2605.22344",
                                                  headers={"User-Agent": "dlm-review-prisma/1.0"}), timeout=90).read()
ns = {"a": "http://www.w3.org/2005/Atom"}
e = ET.fromstring(x).find("a:entry", ns)
at = re.sub(r"\s+", " ", e.find("a:title", ns).text).strip()
s = difflib.SequenceMatcher(None, at.lower(), rt.lower()).ratio()
assert s >= 0.9, (at, rt)
au = [n.text for n in e.findall("a:author/a:name", ns)]
entries.append(("R0963", "arXiv:2605.22344", f"% fetched from arxiv; title similarity to record R0963 (ta-recheck title): {s:.3f}\n"
                f"@misc{{arXiv:2605.22344,\n  author = {{{tex(' and '.join(au))}}},\n  title = {{{{{tex(at)}}}}},\n"
                f"  year = {{{e.find('a:published', ns).text[:4]}}},\n  eprint = {{2605.22344}},\n  archivePrefix = {{arXiv}},\n"
                f"  howpublished = {{arXiv preprint arXiv:2605.22344}},\n}}\n"))

bib = (P / "s6-refs.bib").read_text(encoding="utf-8")
for i, key, ent in entries:
    assert not K["keys"][i].get("key"), i
    if "{" + key + "," not in bib:
        bib += "\n" + ent
    K["keys"][i] = {"key": key, "source": "local-page1" if not key.startswith("arXiv") else "arxiv", "similarity": None}
(P / "s6-refs.bib").write_text(bib, encoding="utf-8")
(P / "tables/s6-keys.json").write_text(json.dumps(K, indent=1), encoding="utf-8")
print("added", len(entries), "| cited now", sum(1 for v in K["keys"].values() if v.get("key")), "of", len(K["keys"]))
