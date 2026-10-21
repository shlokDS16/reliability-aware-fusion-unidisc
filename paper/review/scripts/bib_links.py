"""Give every bibliography entry a link: entries with a DOI or URL keep it (ACM style links them); other entries get
url = https://arxiv.org/abs/<id> when an arXiv id is known (key arXiv:<id> or arXiv:<id> in the entry), or
https://openreview.net/forum?id=<id> for openreview: keys. Run from paper/review."""
import re
from pathlib import Path


def entry_end(t, start):
    i = t.index("{", start)
    depth = 0
    for j in range(i, len(t)):
        if t[j] == "{":
            depth += 1
        elif t[j] == "}":
            depth -= 1
            if depth == 0:
                return j
    raise ValueError("unbalanced entry at %d" % start)


for b in ("references.bib", "s6-refs.bib"):
    p = Path(b)
    t = p.read_text(encoding="utf-8")
    starts = [m.start() for m in re.finditer(r"(?m)^@\w+\{", t)]
    added, missing, pieces, last = 0, [], [], 0
    for s in starts:
        e = entry_end(t, s)
        entry = t[s:e]
        key = re.match(r"@\w+\{([^,]+),", entry).group(1).strip()
        link = None
        if not re.search(r"(?im)^\s*(doi|url)\s*=", entry):
            if key.startswith("arXiv:"):
                link = "https://arxiv.org/abs/" + key[6:]
            elif re.search(r"arXiv:(\d{4}\.\d{4,5})", entry):
                link = "https://arxiv.org/abs/" + re.search(r"arXiv:(\d{4}\.\d{4,5})", entry).group(1)
            elif key.startswith("openreview:"):
                link = "https://openreview.net/forum?id=" + key.split(":", 1)[1]
            else:
                missing.append(key)
        pieces.append(t[last:e])
        if link:
            body = pieces[-1].rstrip()
            if not body.endswith(","):
                body += ","
            pieces[-1] = body + f"\n  url = {{{link}}},\n"
            added += 1
        last = e
    pieces.append(t[last:])
    p.write_text("".join(pieces), encoding="utf-8")
    print(b, "entries:", len(starts), "| links added:", added, "| no link possible:", missing)
