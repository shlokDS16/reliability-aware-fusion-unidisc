"""Integrity diff for the language edit (2026-10-30): numbers, \\cite, \\label/\\ref, math, binding regions, must-not words.
Usage: python integrity_lang.py ORIG_DIR PAPER_DIR > report.md"""
import re, sys, collections, pathlib, difflib

ORIG = pathlib.Path(sys.argv[1])
NEW = pathlib.Path(sys.argv[2])
MAIN = ["sections/" + f for f in ["abstract.tex", "introduction.tex", "related.tex", "setting.tex", "study1.tex", "study2.tex",
                                  "discussion.tex", "conclusion.tex", "declaration.tex"]]
SUP = ["supplement/supplement.tex"]


def rd(root, f):
    return open(root / f, encoding="utf-8", newline="").read().replace("\r\n", "\n")


def strip_comments(t):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in t.split("\n"))


def norm_ws(t):
    return re.sub(r"\s+", " ", t).strip()


def typo(t):
    """Typography-only normalisation: thin spaces, serial commas, whitespace."""
    t = strip_comments(t)
    t = t.replace("\\,", "")
    t = norm_ws(t)
    t = re.sub(r",\s+(and|or)\s", r" \1 ", t)
    t = t.replace("toward the", "towards the")
    return t


NUM = re.compile(r"(?<![A-Za-z_\\])-?\d+(?:[.,]\d+)*")


def nums(t):
    t = re.sub(r"\\(cite|label|ref|cref|Cref|eqref|nolinkurl|includegraphics|input)\{[^}]*\}", " ", t)
    t = t.replace("\\,", "")
    return collections.Counter(m.group(0) for m in NUM.finditer(t))


def keys(t, cmd):
    out = collections.Counter()
    for m in re.finditer(r"\\(?:%s)\{([^}]*)\}" % cmd, t):
        for k in m.group(1).split(","):
            out[k.strip()] += 1
    return out


def maths(t):
    out = collections.Counter()
    for m in re.finditer(r"\\begin\{(equation|align|aligned)\*?\}(.*?)\\end\{\1\*?\}", t, re.S):
        out["ENV:" + norm_ws(m.group(2))] += 1
    t2 = re.sub(r"\\begin\{(equation|align)\*?\}.*?\\end\{\1\*?\}", " ", t, flags=re.S)
    for m in re.finditer(r"(?<!\\)\$(.+?)(?<!\\)\$", t2, re.S):
        out[norm_ws(m.group(1))] += 1
    return out


lines = ["# Integrity diff: language edit (language expert, 2026-10-30)", "",
         "Baseline: copies of every touched file taken before the first edit (session scratchpad `orig/`).",
         "Generated tables (`tables/*.tex`) were not edited. Comments are stripped before every comparison.", ""]

for label, files in [("Main paper (sections/*.tex)", MAIN), ("Supplement (supplement/supplement.tex)", SUP)]:
    o = "".join(strip_comments(rd(ORIG, f if not f.startswith("supplement") else "supplement/supplement.tex")) + "\n" for f in files)
    n = "".join(strip_comments(rd(NEW, f)) + "\n" for f in files)
    lines.append(f"## {label}")
    on, nn = nums(o), nums(n)
    lines.append(f"- Numbers: {sum(on.values())} tokens before, {sum(nn.values())} after; "
                 f"lost {dict(on - nn) or 'none'}; gained {dict(nn - on) or 'none'}.")
    for cmd, name in [("cite", "\\cite keys"), ("label", "\\label keys"), ("cref|Cref|ref|eqref", "\\ref/\\cref/\\eqref keys")]:
        ok, nk = keys(o, cmd), keys(n, cmd)
        lines.append(f"- {name}: {sum(ok.values())} before, {sum(nk.values())} after; "
                     f"{'identical multiset' if ok == nk else 'DIFFERENT: lost ' + str(dict(ok - nk)) + ' gained ' + str(dict(nk - ok))}.")
    om, nm = maths(o), maths(n)
    lines.append(f"- Math (display environments and inline $...$): {sum(om.values())} before, {sum(nm.values())} after; "
                 f"{'identical multiset' if om == nm else 'DIFFERENT: lost ' + str(list((om - nm).keys())) + ' gained ' + str(list((nm - om).keys()))}.")
    lines.append("")

# Binding regions: (file, start marker, end marker)
REG = [
 ("sections/abstract.tex", None, None, "Abstract (statistician ruling R1-R12; NEG, L1, L-NI, scope)"),
 ("sections/introduction.tex", r"\paragraph*{Contributions}", r"\end{enumerate}", "Contribution list (A4.2.4 bullets, A6.12, A5.9 prefix)"),
 ("sections/setting.tex", "UniDisc's denoiser has no time input", "(evidence and limits in supplement S-I).", "Time-input sentence (A4.3.1)"),
 ("sections/setting.tex", "The paper contains 17", "0.58$.", "Multiplicity sentence (A6.7)"),
 ("sections/setting.tex", r"\emph{Preregistered} has one meaning", "independent reviews).", "Preregistered definition and audit wording (rules 6, 9)"),
 ("sections/study1.tex", r"\begin{proposition}[conformal", r"\begin{figure*}", "prop:crc and the only-guarantee paragraph (R1)"),
 ("sections/study1.tex", r"\paragraph*{A model of when", r"\begin{lemma}", "Theory label (R1.8)"),
 ("sections/study1.tex", r"\subsubsection{Operating points and family P}", r"\begin{figure}[!t]", "Family P result, NEG sentences, scope, label (A4.2.2, A4.2.3)"),
 ("sections/study1.tex", r"\subsubsection{Token detection}", r"\begin{figure}[!t]", "Detection with the M1 rival (A4.2.2 item 2)"),
 ("sections/study1.tex", r"\subsubsection{Family H", r"\subsubsection{Exploratory analyses}", "Family H (A5.9 prefix)"),
 ("sections/study1.tex", r"\subsubsection{Exploratory analyses}", r"\subsubsection{Cost}", "Tier-3 placement (A4.1.10)"),
 ("sections/study2.tex", r"\subsection{Provenance", r"\subsection{The Frozen Weighting}", "Provenance disclosure (A6.13, D0094 clause)"),
 ("sections/study2.tex", r"\paragraph*{Arms, families", r"\subsection{Results}", "Study 2 protocol: families and tests (A6.4-A6.7)"),
 ("sections/study2.tex", "On a fresh preregistered fold", r"\subsection{Reference Encoders}", "Study 2 results (A6.12 L1, L-NI, scope, LG three p-values, D0091)"),
 ("sections/study2.tex", "For reference, CLIP", "(supplement S-VI).", "Reference-encoder sentence (A6.6)"),
 ("sections/discussion.tex", r"\subsection{Study 1}", r"\subsection{Study 2}", "Discussion VI-A (NEG 6.1 opening, H paragraph)"),
 ("sections/discussion.tex", r"\subsection{Limitations}", r"\subsection{Deviations", "Limitations (SPEC section 7)"),
 ("sections/conclusion.tex", None, None, "Conclusion (binding sentences repeated)"),
 ("sections/declaration.tex", r"\section*{Declaration of Generative AI Use}", None, "Declaration of Generative AI Use (fixed by the authors)"),
 ("supplement/supplement.tex", r"\subsection{Disclosures of Addendum A4}", r"\subsection{Full", "Supplement: A4 disclosures"),
 ("supplement/supplement.tex", r"\section{Study 1: Family H", r"\section{Study 2: Exploratory", "Supplement S-III family H (A5.9)"),
]


def region(t, a, b):
    t = t.replace("\r\n", "\n")
    i = 0 if a is None else t.find(a)
    if i < 0:
        return None
    j = len(t) if b is None else t.find(b, i + (len(a) if a else 0))
    if j < 0:
        j = len(t)
    return t[i:j]


lines.append("## Binding regions (substance fixed; typography only)")
lines.append("Typography normalisation used for the check: thin spaces (`\\,`) removed, a comma before a final `and`/`or` "
             "removed (serial comma), whitespace collapsed, `toward`/`towards`.")
lines.append("")
lines.append("| Region | Raw text changed | Equal after typography normalisation |")
lines.append("|---|---|---|")
details = []
for f, a, b, name in REG:
    ro, rn = region(rd(ORIG, f), a, b), region(rd(NEW, f), a, b)
    if ro is None or rn is None:
        lines.append(f"| {name} | marker not found | CHECK |")
        continue
    raw = norm_ws(strip_comments(ro)) != norm_ws(strip_comments(rn))
    eq = typo(ro) == typo(rn)
    lines.append(f"| {name} | {'yes' if raw else 'no'} | {'yes' if eq else 'NO'} |")
    if raw:
        ow, nw = norm_ws(strip_comments(ro)).split(" "), norm_ws(strip_comments(rn)).split(" ")
        sm = difflib.SequenceMatcher(a=ow, b=nw, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                ctx = " ".join(ow[max(0, i1 - 4):i1])
                details.append(f"- {name}: ...{ctx} `{' '.join(ow[i1:i2])}` -> `{' '.join(nw[j1:j2])}`")
lines.append("")
lines.append("### Every edit inside a binding region")
lines += details or ["- none"]
lines.append("")

# Must-not scan of the revised prose (comments stripped), reported with counts before and after.
MUST = ["robust", "generalises", "generalizes", "state of the art", "calibrated", "guarantee", "validated", "outperform",
        "better than", "beats", "competitive", "unlike hard gating", "instead of discarding", "fixes", "overcomes", "solution",
        "addresses the limitation", "predicts", "explains", "accounts for", "is consistent with", "has no effect", "equivalent",
        "as good as", "on-manifold", "our detector", "decision-level fusion", "time-free", "compositional", "replication",
        "sugarcrepe score", "screening", "independent", "novel", "we prove", "trend", "first"]
o_all = "".join(strip_comments(rd(ORIG, f)) for f in MAIN + SUP).lower()
n_all = "".join(strip_comments(rd(NEW, f)) for f in MAIN + SUP).lower()
lines.append("## Must-not words (SPEC rule 5): occurrences in main + supplement prose, before -> after")
lines.append("A word that is present before and after is a pre-existing use (most are allowed contexts, e.g. 'only guarantee', "
             "'does not show that the gate has no effect', 'first author'); the edit added none.")
lines.append("")
for w in MUST:
    a, b = o_all.count(w), n_all.count(w)
    if a or b:
        lines.append(f"- {w}: {a} -> {b}{'  <-- CHANGED' if a != b else ''}")
print("\n".join(lines))
