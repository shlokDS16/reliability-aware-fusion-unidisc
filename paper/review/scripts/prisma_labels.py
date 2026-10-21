"""2026-10-21 (D0072): plain labels in the PRISMA figure (no decision identifiers or internal tranche names).
Edits only the strings drawn in fig01_prisma.py; data keys are unchanged. Run from paper/review."""
from pathlib import Path

p = Path("scripts/fig01_prisma.py")
t = p.read_text(encoding="utf-8")
R = [('"(screening frozen, D0051)"', '"(screening stopped)"'),
     (" later assessed in tranche L\"", " later assessed in the landmark set\""),
     ('"not assessed (D0051)"', '"not assessed"'),
     ('"Full-text tranche T1: reports sought"', '"Full-text assessment: reports sought"'),
     ('"Included from T1"', '"Included at full text"'),
     ('"tranche R797 n = ', '"Reassessed exclusions n = '),
     ('"(frozen, D0051)"', '"(not reached)"'),
     ('"Included from R797"', '"Included on reassessment"'),
     ("(T1 {f(ft['include'])} + R797 {f(r7['include'])})", "({f(ft['include'])} + {f(r7['include'])})"),
     (" (D0052, D0054)\"", "\""),
     ('"other methods (D0061):"', '"other methods:"'),
     ('"Landmark tranche"', '"Landmark set"'),
     ("read by screener A only, confirmed by the first author", "settled by the first author"),
     ('"rescue-screened ', '"single-reviewer check '),
     ("{f(fr['released_D0028'])} released back", "{f(fr['released_D0028'])} returned to screening")]
for o, n in R:
    if o not in t:
        print("not found:", o)
    t = t.replace(o, n)
p.write_text(t, encoding="utf-8")
print("ok")
