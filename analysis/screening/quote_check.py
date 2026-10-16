"""Check that every evidence quote in full-text screening rows occurs in the screened full text.

Criteria v1.3 (screener copy, brief): each row carries "evidence": [{"cond", "quote", "loc"}]. A quote
must occur verbatim in the full-text file of that record, up to:
  - Unicode compatibility forms (NFKC: ligatures such as "fi", full-width characters),
  - quote and dash variants (curly quotes, en/em dashes, minus sign),
  - whitespace (any run of spaces, tabs or line breaks counts as one space),
  - line-end hyphenation ("exam-\\nple" matches "example") and soft hyphens,
  - markdown emphasis and link markup left by PDF-to-markdown conversion (*, _, `, [, ]).
Case is kept (verbatim means verbatim). An ellipsis ("..." or the ellipsis character) inside a quote
splits it into fragments that must all occur, in order.

    python analysis/screening/quote_check.py --rows <screener.jsonl> --texts <dir> [--out <report.jsonl>]
    python analysis/screening/quote_check.py --self-test

The full text of record <id> is the first file in <dir> named <id>.md, <id>.txt or <id>.html.
Exit status: 0 if every quote is found, 1 if any quote is not found or any text is missing.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

_TRANS = str.maketrans({
    "‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'",
    "“": '"', "”": '"', "„": '"', "″": '"',
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-",
    " ": " ", " ": " ", " ": " ",
    "*": "", "_": "", "`": "", "[": "", "]": "",
})
_ELLIPSIS = re.compile(r"\s*(?:\.\.\.|…)\s*")


def normalise(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("­", "")                      # soft hyphen
    s = s.translate(_TRANS)
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)     # line-end hyphenation
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _variants(text):
    """Normalised text, plus a copy with every hyphen removed (covers hyphenation the converter kept
    as a real hyphen, or removed, on either side)."""
    t = normalise(text)
    return t, t.replace("-", "").replace("  ", " ")


def quote_found(quote, text):
    t, t_nohy = _variants(text)
    frags = [normalise(f) for f in _ELLIPSIS.split(quote) if normalise(f)]
    if not frags:
        return False
    for hay, conv in ((t, lambda x: x), (t_nohy, lambda x: x.replace("-", "").replace("  ", " "))):
        pos, ok = 0, True
        for f in frags:
            i = hay.find(conv(f), pos)
            if i < 0:
                ok = False
                break
            pos = i + len(conv(f))
        if ok:
            return True
    return False


def find_text(texts_dir, rid):
    for ext in (".md", ".txt", ".html"):
        p = Path(texts_dir) / f"{rid}{ext}"
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")
    return None


def check(rows_path, texts_dir, out_path=None):
    bad = 0
    report = []
    with open(rows_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            rid = row["id"]
            text = find_text(texts_dir, rid)
            for j, ev in enumerate(row.get("evidence") or []):
                if text is None:
                    status = "no_text"
                else:
                    status = "found" if quote_found(ev.get("quote", ""), text) else "not_found"
                if status != "found":
                    bad += 1
                report.append({"id": rid, "screener": row.get("screener", ""), "i": j,
                               "cond": ev.get("cond", ""), "loc": ev.get("loc", ""), "status": status})
            if not row.get("evidence"):
                bad += 1
                report.append({"id": rid, "screener": row.get("screener", ""), "i": -1,
                               "cond": "", "loc": "", "status": "no_evidence"})
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            for r in report:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    n = len(report)
    print(f"quotes checked: {n}; not found or missing: {bad}")
    for r in report:
        if r["status"] != "found":
            print(f"  {r['id']} {r['screener']} #{r['i']} {r['cond']} {r['loc']}: {r['status']}")
    return bad


def self_test():
    text = ("We train a masked diffusion lan-\nguage model with a random masking ratio – sampled "
            "uniformly – per sequence.\n\nThe **understanding** and genera-\ntion branches share all "
            "transformer weights (Table 3). Efﬁcient decoding uses “remasking”.")
    cases = [
        ("masked diffusion language model with a random masking ratio", True),     # hyphenation + newline
        ("ratio - sampled uniformly - per sequence", True),                        # en dash vs hyphen
        ("The understanding and generation branches share all transformer weights", True),  # markdown + hyphenation
        ("Efficient decoding uses \"remasking\"", True),                           # ligature + curly quotes
        ("We train a masked ... share all transformer weights", True),             # ellipsis, in order
        ("share all transformer weights ... We train a masked", False),            # ellipsis, wrong order
        ("we train a masked diffusion language model", False),                     # case kept
        ("The understanding and generation branches share no weights", False),     # altered wording
        ("", False),                                                               # empty quote
    ]
    fails = 0
    for q, want in cases:
        got = quote_found(q, text)
        flag = "ok" if got == want else "FAIL"
        if got != want:
            fails += 1
        print(f"{flag}: expected {want}, got {got}: {q!r}")
    print(f"self-test: {len(cases) - fails}/{len(cases)} passed")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows")
    ap.add_argument("--texts")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.exit(1 if self_test() else 0)
    if not (a.rows and a.texts):
        ap.error("--rows and --texts are required (or --self-test)")
    sys.exit(1 if check(a.rows, a.texts, a.out) else 0)


if __name__ == "__main__":
    main()
