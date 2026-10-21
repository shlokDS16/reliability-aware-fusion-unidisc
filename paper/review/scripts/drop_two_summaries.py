"""Keep 34 pages: drop the Section 3 and Section 7 closing summaries (both repeat text already in those sections)."""
from pathlib import Path

for f, start in (("sections/03-notation.tex", "In summary, every generator in scope is described by five choices"),
                 ("sections/07-error-budget.tex", "In summary, the error budget assigns each method to the term it changes")):
    p = Path(f)
    t = p.read_text(encoding="utf-8")
    i = t.index(start)
    j = t.index("\n", i)
    p.write_text(t[:i].rstrip("\n") + "\n" + t[j + 1:], encoding="utf-8")
print("ok")
