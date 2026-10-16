"""Check that every evidence quote in full-text screening rows occurs in the screened full text.

Criteria v1.4 (screener copy, brief): each row carries "evidence": [{"cond", "quote", "loc"}]. A quote is
ONE CONTIGUOUS passage copied from the full-text file of that record. It must occur there verbatim, up to:
  - Unicode compatibility forms (NFKC: ligatures such as "fi", full-width characters, the ellipsis character),
  - quote and dash variants (curly quotes, en/em dashes, minus sign),
  - whitespace (any run of spaces, tabs or line breaks counts as one space),
  - line-end hyphenation ("exam-\\nple" matches "example") and soft hyphens,
  - markdown emphasis and link markup left by PDF-to-markdown conversion (*, _, `, [, ]).
Case is kept (verbatim means verbatim).

v1.4 changes (red-team audit of criteria v1.3, finding V2):
  - No elision. An ellipsis ("..." or the ellipsis character) is an ordinary character sequence: it matches
    only an ellipsis at the same place in the file. A quote that contains an ellipsis and is not found as a
    contiguous passage gets status "elided" (v1.3 split it into fragments with an unbounded gap, so a quote
    could drop a negation and still pass).
  - Whole words. A match must start and end at a word boundary; a letter, digit or hyphen joined to either
    end of the match rejects that occurrence ("shared" inside "unshared", "autoregressive" inside
    "non-autoregressive").
  - Negation guard. An occurrence whose preceding word in the file is a negation (not, no, never, without,
    nor, neither, cannot, none, nothing, or a word ending in n't) is rejected with status
    "negation_before": the screener must extend the quote to include that word.
A quote is accepted if at least one occurrence passes all checks.

    python analysis/screening/quote_check.py --rows <screener.jsonl> --texts <dir> [--out <report.jsonl>]
    python analysis/screening/quote_check.py --self-test

The full text of record <id> is the first file in <dir> named <id>.md, <id>.txt or <id>.html.
Statuses: found, not_found, elided, negation_before, no_text, no_evidence.
Exit status: 0 if every quote is found, 1 otherwise.
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
    " ": " ", " ": " ", " ": " ",
    "*": "", "_": "", "`": "", "[": "", "]": "",
})
_ELLIPSIS = re.compile(r"\.\.\.|…")
_NEGATIONS = {"not", "no", "never", "without", "nor", "neither", "cannot", "none", "nothing"}
_PREV_WORD = re.compile(r"([A-Za-z']+)\W*$")


def normalise(s):
    s = unicodedata.normalize("NFKC", s)                # also turns the ellipsis character into "..."
    s = s.replace("­", "")                         # soft hyphen
    s = s.translate(_TRANS)
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)        # line-end hyphenation
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _dehyphen(s):
    return s.replace("-", "").replace("  ", " ")


def _joined(ch):
    """True if character ch, adjacent to a match, would make the match part of a longer word."""
    return ch.isalnum() or ch == "-"


def _negated(prefix):
    m = _PREV_WORD.search(prefix[-40:])
    if not m:
        return False
    w = m.group(1).lower()
    return w in _NEGATIONS or w.endswith("n't")


def quote_status(quote, text):
    """Return 'found', 'not_found', 'elided' or 'negation_before' for one quote against one text."""
    q = normalise(quote)
    if not q:
        return "not_found"
    t = normalise(text)
    saw_negation = False
    for hay, needle in ((t, q), (_dehyphen(t), _dehyphen(q))):
        if not needle:
            continue
        start = hay.find(needle)
        while start >= 0:
            end = start + len(needle)
            left_ok = start == 0 or not (_joined(hay[start - 1]) and _joined(needle[0]))
            right_ok = end == len(hay) or not (_joined(hay[end]) and _joined(needle[-1]))
            if left_ok and right_ok:
                if _negated(hay[:start]):
                    saw_negation = True
                else:
                    return "found"
            start = hay.find(needle, start + 1)
    if saw_negation:
        return "negation_before"
    if _ELLIPSIS.search(q):
        return "elided"
    return "not_found"


def quote_found(quote, text):
    return quote_status(quote, text) == "found"


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
                status = "no_text" if text is None else quote_status(ev.get("quote", ""), text)
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
    print(f"quotes checked: {n}; not accepted or missing: {bad}")
    for r in report:
        if r["status"] != "found":
            print(f"  {r['id']} {r['screener']} #{r['i']} {r['cond']} {r['loc']}: {r['status']}")
    return bad


def self_test():
    text = ("We train a masked diffusion lan-\nguage model with a random masking ratio – sampled "
            "uniformly – per sequence.\n\nThe **understanding** and genera-\ntion branches share all "
            "transformer weights (Table 3). Efﬁcient decoding uses “remasking”.")
    # Probe text of the v1.3 red-team audit (V2): the source says the modules do NOT share weights.
    neg = ("The understanding module and the generation module are trained separately; the two modules "
           "do not share weights. Unlike non-autoregressive decoding, the unshared weights keep each "
           "module fixed. We index tokens as x_1, ..., x_n.")
    cases = [
        # (quote, text, expected status)
        ("masked diffusion language model with a random masking ratio", text, "found"),   # hyphenation + newline
        ("ratio - sampled uniformly - per sequence", text, "found"),                      # en dash vs hyphen
        ("The understanding and generation branches share all transformer weights", text, "found"),  # markdown
        ("Efficient decoding uses \"remasking\"", text, "found"),                         # ligature + curly quotes
        ("We train a masked ... share all transformer weights", text, "elided"),          # v1.3 accepted this
        ("share all transformer weights ... We train a masked", text, "elided"),          # elision, wrong order
        ("we train a masked diffusion language model", text, "not_found"),                # case kept
        ("The understanding and generation branches share no weights", text, "not_found"),  # altered wording
        ("", text, "not_found"),                                                          # empty quote
        # adversarial cases added in v1.4
        ("The understanding ... and the generation ... share weights", neg, "elided"),    # audit probe 1
        ("understanding ... share weights", neg, "elided"),                               # audit probe 2
        ("share weights", neg, "negation_before"),                                        # drops the "not"
        ("the two modules do not share weights", neg, "found"),                           # negation kept
        ("shared weights keep each module fixed", neg, "not_found"),                      # inside "unshared"
        ("autoregressive decoding", neg, "not_found"),                                    # inside "non-autoregressive"
        ("Unlike non-autoregressive decoding", neg, "found"),                             # whole hyphenated word
        ("x_1, ..., x_n", neg, "found"),                                                  # literal ellipsis in source
        ("x_1, …, x_n", neg, "found"),                                               # ellipsis character form
        ("ransformer weights", text, "not_found"),                                        # starts inside a word
    ]
    fails = 0
    for q, t, want in cases:
        got = quote_status(q, t)
        ok = got == want
        fails += 0 if ok else 1
        print(f"{'ok' if ok else 'FAIL'}: expected {want}, got {got}: {q!r}")
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
