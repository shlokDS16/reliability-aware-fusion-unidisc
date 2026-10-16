"""Write ieee-queries-20261015.md from the word lists in ieee_queries_20261015.py (run from this folder)."""
import hashlib
from pathlib import Path

import ieee_queries_20261015 as m

HERE = Path(__file__).resolve().parent
COUNTS = {"I1": "1,203", "I2": "101", "I3": "245", "I4": "41", "I5": "12"}
WHAT = {"I1": "S1':B + S1':C (NOT dropped): diffusion AND (C + B word lists)",
        "I2": "S1':A1 (all names)",
        "I3": "S1':A2 without NOT (= A2-r3, a superset of A2-r1/r2) + S1':A3",
        "I4": "S2':M (sheet runs r1-r8 merged)",
        "I5": "S2':VLA (sheet runs r1-r2 merged)"}

out = [
    "# IEEE Xplore queries run 2026-10-15 (Chrome, VIT institutional access: \"Access provided by VIT University\"; D0031)",
    "",
    "Platform: ieeexplore.ieee.org command search via the results URL (matchBoolean=true), filter ranges=2021_2026_Year; "
    "no language filter. Run 2026-10-15, about 23:25-23:40 IST, in the user's Chrome (Claude in Chrome).",
    "",
    "Departure from the sheet: the sheet split S1'/S2' into about 30 runs on an assumed limit of 6 terms per OR list "
    "[unverified]. A test query with 78 field terms ran (1,203 hits, the same string as I1) and I2 with 93 field terms ran, "
    "so the parts were merged into five queries (the D0031 fallback was not needed). As in the sheet, the NOT clauses are "
    "dropped on IEEE (broader than S1'), and singular/plural phrases replace phrase wildcards; S1''/S2'' are applied "
    "locally to the exports. Every term is searched in Document Title, Abstract and Author Keywords. The strings were built "
    "in the page from the word lists in ieee_queries_20261015.py (this folder); the sha256 of each string in the page "
    "equalled this script's output.",
    "",
]
for k in ["I1", "I2", "I3", "I4", "I5"]:
    v = m.Q[k]
    out += [f"{k} ({WHAT[k]}): hits {COUNTS[k]}; sha256 {hashlib.sha256(v.encode()).hexdigest()}; {len(v)} chars",
            "```", v, "```", ""]
out += ["Sum of hits 1,602 (overlaps removed locally).", "",
        "Exports: pending the user's approval (CSV, all results per query; IEEE export cap 2,000 per file)."]
(HERE / "ieee-queries-20261015.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("written")
