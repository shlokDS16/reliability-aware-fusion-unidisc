"""List bibliography items (main.bbl, supplement.bbl) that carry no URL or DOI. Run from paper/review."""
import re

for f in ("main.bbl", "supplement.bbl"):
    t = open(f, encoding="utf-8", errors="replace").read()
    items = re.split(r"\\bibitem", t)[1:]
    nolink = []
    for it in items:
        key = re.search(r"\]\s*\{([^}]+)\}", it) or re.search(r"\{([^}]+)\}", it)
        if not re.search(r"\\(url|doi|showURL|showDOI|href)\b", it):
            nolink.append(key.group(1) if key else "?")
    print(f, "items:", len(items), "without link:", nolink)
