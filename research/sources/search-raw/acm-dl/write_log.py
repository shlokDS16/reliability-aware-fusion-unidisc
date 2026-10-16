"""Write acm-queries-20261015.md from acm_queries_20261015.py (run from this folder)."""
import hashlib
from pathlib import Path

import acm_queries_20261015 as m

HERE = Path(__file__).resolve().parent
COUNTS = {"Q1": "65", "Q2": "17", "Q3": "8", "Q4": "148", "Q5": "91"}
WHAT = {"Q1": "combined NOT-free union (S1, S2, S1':A1, A2-r1, A3-r1..r3, S2':M, S2':VLA; language clause widened), as Scopus Q1",
        "Q2": "S1p-A2-r2", "Q3": "S1p-A3-r4", "Q4": "S1p-B", "Q5": "S1p-C"}

out = [
    "# ACM Digital Library queries run 2026-10-15/16 (Chrome, D0031)",
    "",
    "Platform: dl.acm.org, search target 'advanced', collection `expand=dl` (ACM Full-Text collection, not the Guide), "
    "AfterYear=2021, BeforeYear=2026; no language filter. Counts read 2026-10-16 about 00:25 IST. The tab showed "
    "'Basic Edition' (ACM DL open access); search pages sit behind a Cloudflare check that clears on a normal page load.",
    "",
    "Departure from the sheet: the sheet's S1' forms for ACM put a whole Boolean expression inside one field "
    "(Title:(A AND B) OR Abstract:(A AND B) ...), which is narrower than Scopus TITLE-ABS-KEY. Here every concept "
    "group is searched across the three fields, G(x) = (Title:(x) OR Abstract:(x) OR Keyword:(x)), and groups are "
    "combined with AND / NOT, the same semantics as the sheet's S1/S2 ACM forms and Scopus. Phrases are written "
    "singular and plural (no phrase wildcards). ACM's parsed query (page title) was checked for Q1-Q5: field groups "
    "and NOT clauses appear as written. Strings built in the page from acm_queries_20261015.py; sha256 in the page "
    "equalled the script output.",
    "",
    "A first attempt loaded Q1 as a page URL (about 15,000 characters); Cloudflare's challenge on that page made the "
    "Claude in Chrome safety check block all browser calls for about 20 minutes (cleared by restarting the "
    "extension). Counts and result lists were then read with in-page requests to the same search URL.",
    "",
]
for k in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
    v = m.Q[k]
    out += [f"{k} ({WHAT[k]}): hits {COUNTS[k]}; sha256 {hashlib.sha256(v.encode()).hexdigest()}; {len(v)} chars",
            "```", v, "```", ""]
out += ["Sum of hits 329 (overlaps removed locally).", "",
        "Export (user approved 2026-10-16, in-page route because Chrome downloads were unreliable): result pages "
        "(pageSize 50) read in the tab; DOI, title, type, date, venue, authors and the abstract shown on the results "
        "page saved to acm-dl-results-20261015.jsonl (see the file section below)."]
(HERE / "acm-queries-20261015.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("written")
