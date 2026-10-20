"""Red-team v0.5 scratch: how many include texts print any direction cue KA1(a) could use? Run from the worktree root.
Counts include texts with an arrow character (U+2191, U+2193) anywhere, and with a sentence 'higher/lower is
(are) better' anywhere. A text with neither leaves every sign to the KA1(b) list."""
import json, pathlib, re
DEC = pathlib.Path("analysis/screening/ft-t1/t1-decisions-all.jsonl")
T = pathlib.Path("research/sources/md/fulltext-pymupdf")
inc = sorted(json.loads(l)["id"] for l in open(DEC, encoding="utf-8") if '"decision": "include"' in l)
arrow = hib = either = 0
for i in inc:
    t = (T / f"{i}.txt").read_text(encoding="utf-8", errors="replace")
    a = ("↑" in t) or ("↓" in t)
    h = bool(re.search(r"(higher|lower) (is|values? (are|is)|means?) better", t, re.I))
    arrow += a; hib += h; either += (a or h)
print("includes", len(inc), "with an arrow char", arrow, "with a higher/lower-is-better sentence", hib,
      "either", either, "neither", len(inc) - either)
