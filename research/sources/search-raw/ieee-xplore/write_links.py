"""Write ieee-download-links.html: one result-page link per remaining IEEE export slice (run from this folder)."""
import html
from pathlib import Path

import ieee_queries_20261015 as m

HERE = Path(__file__).resolve().parent
BASE = "https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&newsearch=true&matchBoolean=true&queryText="
SLICES = [  # (query, year range, expected hits, file name to save as)
    ("I1", "2025_2025", "506", "ieee-I1-2025-20261015.csv"),
    ("I1", "2026_2026", "467 (973 minus 506)", "ieee-I1-2026-20261015.csv"),
    ("I2", "2021_2026", "101", "ieee-I2-20261015.csv"),
    ("I3", "2021_2026", "245", "ieee-I3-20261015.csv"),
    ("I4", "2021_2026", "41", "ieee-I4-20261015.csv"),
    ("I5", "2021_2026", "12", "ieee-I5-20261015.csv"),
]

rows = []
for q, yr, n, name in SLICES:
    url = BASE + m.urllib.parse.quote(m.Q[q]) + f"&ranges={yr}_Year"
    rows.append(f'<li><a href="{html.escape(url)}" target="_blank">{q}, years {yr.replace("_", "-")}</a>'
                f' &mdash; expect {n} results; rename the download to <code>{name}</code></li>')

page = f"""<!doctype html><meta charset="utf-8"><title>IEEE export links</title>
<body style="font-family:sans-serif;max-width:760px;margin:24px auto;padding:0 16px">
<h1>IEEE Xplore: remaining CSV exports</h1>
<p>Done already: I1 2021-2024 (230 rows). For each link: open it, check the result count, click
<b>Export</b> &rarr; <b>Results</b> tab &rarr; <b>Download</b>. Leave the downloaded files in your Downloads
folder (or rename as shown); Claude moves and hashes them.</p>
<ol>{''.join(rows)}</ol>
</body>"""
(HERE / "ieee-download-links.html").write_text(page, encoding="utf-8")
print("written")
