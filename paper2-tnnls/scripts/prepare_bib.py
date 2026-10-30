"""Make a copy of references.bib that IEEEtran.bst can print as links.

IEEEtran.bst (v1.14) prints the `url` field ("[Online]. Available: ...") but ignores `doi`. Shlok's rule: every reference has a DOI or
URL rendered as a blue link (hyperref colorlinks). So, for each entry in references.bib (the unmodified copy of paper2/references.bib):
  * has `url`            -> kept;
  * has `doi`            -> url = https://doi.org/<doi>;
  * has arXiv `eprint`   -> url = https://arxiv.org/abs/<id>;
  * none of these        -> reported (nothing is invented).
Output: references-ieee.bib (generated; not committed). Run from anywhere:  python -I scripts/prepare_bib.py
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
src = (root / "references.bib").read_text(encoding="utf8")
parts = re.split(r"\n(?=@\w+\s*\{)", src)
out = [parts[0]]            # header comments
missing, added_doi, added_arxiv, kept = [], 0, 0, 0
for e in parts[1:]:
    m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", e)
    key = m.group(2) if m else "?"
    has_url = re.search(r"^\s*url\s*=", e, re.M)
    doi = re.search(r"^\s*doi\s*=\s*[{\"]([^}\"]+)[}\"]", e, re.M)
    eprint = re.search(r"^\s*eprint\s*=\s*[{\"]([^}\"]+)[}\"]", e, re.M)
    add = None
    if has_url:
        kept += 1
    elif doi:
        # IEEE reference style prints a DOI as "doi: 10.xxxx/..." (IEEE Reference Guide), shorter than
        # "[Online]. Available: https://doi.org/..."; IEEEtran.bst ignores `doi`, so it goes into `note` as a blue link.
        d = doi.group(1).strip()
        link = "doi: \\href{https://doi.org/" + d + "}{\\nolinkurl{" + d + "}}"
        note = re.search(r"^(\s*note\s*=\s*)\{(.*)\}(\s*,?\s*)$", e, re.M)
        if note:
            e = e[:note.start()] + note.group(1) + "{" + note.group(2) + ", " + link + "}" + note.group(3) + e[note.end():]
        else:
            k = e.rstrip().rfind("}")
            body = e[:k].rstrip()
            if not body.endswith(","):
                body += ","
            e = body + "\n  note = {" + link + "}\n}"
        added_doi += 1
    elif eprint:
        add = "https://arxiv.org/abs/" + eprint.group(1).strip()
        added_arxiv += 1
    else:
        missing.append(key)
    if add:
        k = e.rstrip().rfind("}")
        body = e[:k].rstrip()
        if not body.endswith(","):
            body += ","
        e = body + "\n  url = {" + add + "}\n}"
    out.append(e)
(root / "references-ieee.bib").write_text("\n".join(out) + "\n", encoding="utf8")
print(f"prepare_bib: {len(parts) - 1} entries; url kept {kept}, doi notes {added_doi}, from arXiv {added_arxiv}; "
      f"no link: {len(missing)} {missing}")
sys.exit(0)
