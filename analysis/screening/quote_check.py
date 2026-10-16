"""Check that every evidence quote in full-text screening rows occurs in the screened full text.

Criteria v1.6 (screener copy, brief): each row carries "evidence": [{"cond", "quote", "loc"}]. A quote is
ONE CONTIGUOUS passage of at least 6 and at most 40 words copied from the full-text file of that record. It
must occur there verbatim, up to:
  - Unicode compatibility forms (NFKC: ligatures such as "fi", full-width characters, the ellipsis character),
  - quote and dash variants (curly quotes, en/em dashes, minus sign),
  - whitespace (any run of spaces, tabs or line breaks counts as one space),
  - line-end hyphenation ("exam-\\nple" matches "example") and soft hyphens,
  - markdown emphasis and link markup left by PDF-to-markdown conversion (*, _, `, [, ]); since v1.5 also
    the target of a markdown link ("[LLaDA](https://...)" reads as "LLaDA"),
  - HTML tags (since v1.5): a <sup> element holding only a footnote marker (digits, commas, *, daggers, at most
    6 characters) is removed with its content; every other tag is removed and its content kept. Since v1.6 only
    known HTML tag names with well-formed attributes count as tags, so inline maths such as "<q and not r>" is
    kept as text on both sides.
Case is kept (verbatim means verbatim). Citations, page headers and footers inside a passage are part of the
file: a quote either copies them as they appear or is split into two entries.

Checks (a quote is accepted if at least one occurrence passes all of them):
  - Length (v1.5): at least 6 words, else status "too_short".
  - No elision (v1.4): an ellipsis matches only an ellipsis at the same place in the file; a quote with an
    ellipsis that is not found as a contiguous passage gets status "elided".
  - Whole words (v1.4): a letter, digit or hyphen joined to either end of the match rejects that occurrence.
  - Negation before (v1.4, widened in v1.5): an occurrence is rejected with status "negation_before" if any of
    the 6 words before it, in the same sentence, is a negation word. Sentences end at ".", ";", "!" or "?"
    followed by a space; since v1.6 not at a colon and not at the period of an abbreviation (e.g., i.e., et al.,
    Fig., Eq., cf., vs., etc., a single initial), and "e.g." or "Show-o" count as one word (NEG_BEFORE below, any word ending in
    n't, or "w/o"). The screener must extend the quote back to include that word.
  - Negation after (v1.5): an occurrence is rejected with status "negation_after" if any of the 3 words after
    it, in the same sentence, is a strong negation word (NEG_AFTER below). The screener extends the quote.
What the script cannot check: a qualifier that is not a negation ("only in stage 1", "which is kept frozen")
outside these windows, and the meaning of a passage. Those stay with the adjudicator and the human author.

    python analysis/screening/quote_check.py --rows <screener.jsonl> --texts <dir> [--out <report.jsonl>]
    python analysis/screening/quote_check.py --self-test

The full text of record <id> is the first file in <dir> named <id>.md, <id>.txt or <id>.html.
Statuses: found, not_found, too_short, elided, negation_before, negation_after, no_text, no_evidence.
Exit status: 0 if every quote is found, 1 otherwise.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

MIN_WORDS = 6
WINDOW_BEFORE = 6
WINDOW_AFTER = 3
NEG_BEFORE = {"not", "no", "never", "without", "nor", "neither", "cannot", "none", "nothing", "lack", "lacks",
              "lacking", "lacked", "rather", "instead", "unlike", "dont", "doesnt", "didnt", "isnt", "arent",
              "wasnt", "werent", "cant", "wont", "hardly", "neglect", "neglects", "absent", "fail", "fails",
              "failed"}
NEG_AFTER = {"not", "no", "never", "neither", "nor", "without", "none"}

_TRANS = str.maketrans({
    "‘": "'", "’": "'", "‚": "'", "‛": "'", "′": "'",
    "“": '"', "”": '"', "„": '"', "″": '"',
    "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-", "−": "-",
    " ": " ", " ": " ", " ": " ",
    "*": "", "_": "", "`": "", "[": "", "]": "",
})
_ELLIPSIS = re.compile(r"\.\.\.|…")
_LINK_TARGET = re.compile(r"\]\([^)\s]*\)")
_SUP_MARK = re.compile(r"<sup>\s*[0-9,*†‡\s]{1,6}\s*</sup>", re.IGNORECASE)
_HTML_TAGS = ("a|abbr|b|big|blockquote|br|caption|center|cite|code|col|colgroup|dd|del|div|dl|dt|em|figcaption|"
              "figure|font|h[1-6]|hr|i|img|ins|kbd|li|mark|ol|p|pre|q|s|samp|small|span|strike|strong|sub|sup|"
              "table|tbody|td|tfoot|th|thead|tr|tt|u|ul|var")
_ATTR = r"\s+[A-Za-z_:][-A-Za-z0-9_:.]*\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s\"'=<>`]+)"
_TAG = re.compile(r"</?(?:" + _HTML_TAGS + r")(?:" + _ATTR + r")*\s*/?>", re.IGNORECASE)
_SENT_END = re.compile(r"[.;!?](\s|$)")
_ABBREV = re.compile(r"(?:\b(?:e\.g|i\.e|et al|al|figs?|eqs?|cf|vs|etc|resp|approx|sec|tab|no|ref|refs)|"
                     r"(?<![A-Za-z])[A-Za-z])$", re.IGNORECASE)
_WORD = re.compile(r"w/o|[A-Za-z](?:[A-Za-z'\-]|\.(?=[A-Za-z]))*")


def normalise(s):
    s = unicodedata.normalize("NFKC", s)                # also turns the ellipsis character into "..."
    s = s.replace("­", "")                         # soft hyphen
    s = _LINK_TARGET.sub("]", s)                        # [text](url) -> [text]
    s = _SUP_MARK.sub("", s)                            # footnote markers
    s = _TAG.sub("", s)                                 # other HTML tags, content kept
    s = s.translate(_TRANS)
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)        # line-end hyphenation
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _dehyphen(s):
    return s.replace("-", "").replace("  ", " ")


def _joined(ch):
    """True if character ch, adjacent to a match, would make the match part of a longer word."""
    return ch.isalnum() or ch == "-"


def _words(s):
    return [w.lower().replace("'", "") if not w.lower().endswith("n't") else "n't" for w in _WORD.findall(s)]


def _sentence_ends(t):
    """Sentence-end matches in t, skipping the period of an abbreviation or a single initial."""
    out = []
    for m in _SENT_END.finditer(t):
        if t[m.start()] == "." and _ABBREV.search(t[:m.start()]):
            continue
        out.append(m)
    return out


def _negated_before(prefix):
    clause = prefix[-300:]
    ends = _sentence_ends(clause)
    if ends:
        clause = clause[ends[-1].end():]
    for w in _words(clause)[-WINDOW_BEFORE:]:
        if w in NEG_BEFORE or w == "n't" or w == "w/o":
            return True
    return False


def _negated_after(suffix):
    clause = suffix[:200]
    ends = _sentence_ends(clause)
    if ends:
        clause = clause[:ends[0].start()]
    return any(w in NEG_AFTER for w in _words(clause)[:WINDOW_AFTER])


def quote_status(quote, text):
    """Return found, not_found, too_short, elided, negation_before or negation_after for one quote."""
    q = normalise(quote)
    if not q:
        return "not_found"
    if len(q.split()) < MIN_WORDS:
        return "too_short"
    t = normalise(text)
    seen = None
    for hay, needle in ((t, q), (_dehyphen(t), _dehyphen(q))):
        if not needle:
            continue
        start = hay.find(needle)
        while start >= 0:
            end = start + len(needle)
            left_ok = start == 0 or not (_joined(hay[start - 1]) and _joined(needle[0]))
            right_ok = end == len(hay) or not (_joined(hay[end]) and _joined(needle[-1]))
            if left_ok and right_ok:
                if _negated_before(hay[:start]):
                    seen = seen or "negation_before"
                elif _negated_after(hay[end:]):
                    seen = seen or "negation_after"
                else:
                    return "found"
            start = hay.find(needle, start + 1)
    if seen:
        return seen
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
            "transformer weights (Table 3). Efﬁcient decoding uses “remasking” in every "
            "experiment we report.")
    # Probe text of the v1.3 red-team audit (V2): the source says the modules do NOT share weights.
    neg = ("The understanding module and the generation module are trained separately; the two modules "
           "do not share weights. Unlike non-autoregressive decoding, the unshared weights keep each "
           "module fixed in all runs. We index the tokens of a sequence as x_1, ..., x_n in this paper.")
    # Probes of the v1.4 red-team audit (n1, n2).
    neg2 = ("In our design the encoder and the decoder do not fully share weights across layers. "
            "We do not, however, share weights between the two branches in any stage. "
            "It is not the case that both modules share weights in our final system. "
            "The baseline lacks shared weights between the vision and text towers entirely. "
            "Our variant w/o shared weights between towers is weaker on every benchmark. "
            "Both towers of the model share weights in neither stage of training.")
    # Probes of the v1.5 red-team audit (y4): abbreviations and colons between negation and quote; inline maths.
    abbr = ("We do not, e.g. as Show-o does, share weights between the understanding and generation modules. "
            "The model does not, following Chen et al. 2024, share weights between the two towers of the system. "
            "The branches do not have this property: shared weights across the understanding and generation paths. "
            "Under the condition <p and not q> the decoder shares weights with the encoder in each layer. "
            "We report <span class=\"hl\">joint training of both branches</span> in all of our experiments.")
    md = ("We fine-tune [LLaDA](https://github.com/ML-GSAI/LLaDA) on SMILES strings from the ZINC "
          "database.<sup>2</sup> The model<sup>*</sup> generates valid molecules in most trials. "
          "Energy is E = mc<sup>2</sup> in this toy example.")
    cases = [
        # (quote, text, expected status)
        ("masked diffusion language model with a random masking ratio", text, "found"),   # hyphenation + newline
        ("ratio - sampled uniformly - per sequence", text, "found"),                      # en dash vs hyphen
        ("The understanding and generation branches share all transformer weights", text, "found"),  # markdown
        ("Efficient decoding uses \"remasking\" in every experiment", text, "found"),     # ligature + curly quotes
        ("We train a masked ... share all transformer weights", text, "elided"),          # v1.3 accepted this
        ("share all transformer weights ... We train a masked", text, "elided"),          # elision, wrong order
        ("we train a masked diffusion language model", text, "not_found"),                # case kept
        ("The understanding and generation branches share no weights", text, "not_found"),  # altered wording
        ("", text, "not_found"),                                                          # empty quote
        # v1.4 adversarial cases (audit of v1.3, V2)
        ("The understanding ... and the generation ... share weights", neg, "elided"),    # audit probe 1
        ("the two modules ... share weights", neg, "elided"),                             # audit probe 2
        ("share weights", neg, "too_short"),                                              # v1.5: minimum length
        ("the two modules do not share weights", neg, "found"),                           # negation kept
        ("shared weights keep each module fixed in all runs", neg, "not_found"),          # inside "unshared"
        ("autoregressive decoding, the unshared weights keep each", neg, "not_found"),    # inside "non-autoregressive"
        ("Unlike non-autoregressive decoding, the unshared weights keep", neg, "found"),   # whole hyphenated word
        ("We index the tokens of a sequence as x_1, ..., x_n", neg, "found"),             # literal ellipsis
        ("We index the tokens of a sequence as x_1, …, x_n", neg, "found"),          # ellipsis character
        ("ransformer weights (Table 3). Efficient decoding", text, "not_found"),          # starts inside a word
        # v1.5 adversarial cases (audit of v1.4, n1): negation further back, other lexicon, after
        ("fully share weights across layers", neg2, "too_short"),                         # 5 words
        ("the decoder do not fully share weights across layers", neg2, "found"),          # negation included
        ("fully share weights across layers in our design", neg2, "not_found"),           # not a passage
        ("encoder and the decoder do not fully share", neg2, "found"),
        ("share weights between the two branches in any stage", neg2, "negation_before"),  # "not, however,"
        ("both modules share weights in our final system", neg2, "negation_before"),      # "not the case that"
        ("shared weights between the vision and text towers", neg2, "negation_before"),   # "lacks"
        ("shared weights between towers is weaker on every", neg2, "negation_before"),    # "w/o"
        ("Both towers of the model share weights", neg2, "negation_after"),               # "in neither" after
        ("Both towers of the model share weights in neither stage", neg2, "found"),       # negation included
        # v1.5 markup cases (audit of v1.4, n2)
        ("We fine-tune LLaDA on SMILES strings from the ZINC database.", md, "found"),    # link target dropped
        ("The model generates valid molecules in most trials.", md, "found"),             # footnote marker dropped
        ("Energy is E = mc2 in this toy example.", md, "not_found"),                      # sup content typed in
        # v1.6 cases (audit of v1.5, y4)
        ("share weights between the understanding and generation modules", abbr, "negation_before"),  # e.g.
        ("share weights between the two towers of the system", abbr, "negation_before"),  # et al.
        ("shared weights across the understanding and generation paths", abbr, "negation_before"),  # colon
        ("the decoder shares weights with the encoder in each layer", abbr, "negation_before"),  # maths span kept
        ("Under the condition <p and not q> the decoder shares weights", abbr, "found"),  # span quoted verbatim
        ("We report joint training of both branches in all", abbr, "found"),              # real tag still removed
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
