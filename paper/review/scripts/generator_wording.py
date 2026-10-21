"""Remove decision identifiers and internal set names from two generated supplement tables (run from repo root)."""
from pathlib import Path

q = Path("paper/review/scripts/qa_tables.py")
t = q.read_text(encoding="utf-8")
o = "for the landmark tranche (decisions D0061, D0063)"
if o in t:
    t = t.replace(o, "for the landmark set")
q.write_text(t, encoding="utf-8")

s = Path("paper/review/scripts/search_strings_table.py")
t = s.read_text(encoding="utf-8")
hook = '    return re.sub(r"  +", " ", s)'
if "combined query" not in t:
    assert hook in t
    t = t.replace(hook, '    s = re.sub(r",?\\s*D00\\d\\d combined query", ", combined query", s)\n' + hook)
s.write_text(t, encoding="utf-8")
print("ok")
