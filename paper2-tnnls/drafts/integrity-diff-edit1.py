"""Integrity diff for clarity edit 1: numbers, cite keys, labels/refs and binding sentences, original vs revised main paper."""
import re, sys, collections, pathlib

ORIG = pathlib.Path(sys.argv[1])   # scratch copy dir (sections/, tables/, supplement.tex)
NEW = pathlib.Path(sys.argv[2])    # paper2-tnnls
FILES = ["sections/" + f for f in ["abstract.tex", "introduction.tex", "related.tex", "setting.tex", "study1.tex", "study2.tex",
                                   "discussion.tex", "conclusion.tex", "appendix.tex", "declaration.tex"]]


def strip_comments(t):
    return "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in t.split("\n"))


def norm(t):
    return re.sub(r"\s+", " ", t).strip()


NUM = re.compile(r"(?<![A-Za-z_\\])-?\d+(?:[.,]\d+)*")


def nums(t):
    t = re.sub(r"\\(cite|label|ref|cref|Cref|eqref|nolinkurl|includegraphics|input)\{[^}]*\}", " ", t)
    t = re.sub(r"\\(?:,|;)", "", t)  # thin spaces inside numbers: 1\,024 -> 1024
    return collections.Counter(m.group(0) for m in NUM.finditer(t))


def keys(t, cmd):
    out = collections.Counter()
    for m in re.finditer(r"\\(?:%s)\{([^}]*)\}" % cmd, t):
        for k in m.group(1).split(","):
            out[k.strip()] += 1
    return out


def body(root, files, tables=True):
    t = ""
    for f in files:
        t += strip_comments((root / f).read_text(encoding="utf-8")) + "\n"
    return t


o_txt = body(ORIG, FILES)
n_txt = body(NEW, FILES)
# tables used in main
o_tab = "".join(strip_comments((ORIG / "tables" / p.name).read_text(encoding="utf-8")) for p in (ORIG / "tables").glob("*.tex"))
n_tab = "".join(strip_comments(p.read_text(encoding="utf-8")) for p in (NEW / "tables").glob("*.tex"))
o_sup = strip_comments((ORIG / "supplement.tex").read_text(encoding="utf-8"))
n_sup = strip_comments((NEW / "supplement" / "supplement.tex").read_text(encoding="utf-8"))

lines = ["# Integrity diff, clarity edit 1 (main paper prose, comments stripped)", ""]
on, nn = nums(o_txt), nums(n_txt)
lost = on - nn
gained = nn - on
sup_new = nums(n_sup) - nums(o_sup)
sup_all = nums(n_sup)
tab_all = nums(n_tab)
lines.append("## Numbers whose count in the main-paper prose fell")
lines.append("| number | times removed | still in main prose | in a main table file | added to supplement in this edit | already in supplement |")
lines.append("|---|---|---|---|---|---|")
for k in sorted(lost, key=lambda s: (len(s), s)):
    lines.append(f"| {k} | {lost[k]} | {nn.get(k,0)} | {tab_all.get(k,0)} | {sup_new.get(k,0)} | {sup_all.get(k,0)} |")
lines.append("")
lines.append("## Numbers whose count in the main-paper prose rose (must each be justified)")
for k in sorted(gained):
    lines.append(f"- {k} (+{gained[k]})")
lines.append("")
for cmd, name in [("cite", "citation keys"), ("label", "labels"), ("cref|Cref|ref|eqref", "cross-references")]:
    ok, nk = keys(o_txt + o_tab, cmd), keys(n_txt + n_tab, cmd)
    lines.append(f"## {name}: removed keys (count in revised main, any place)")
    for k in sorted(set(ok) - set(nk)):
        lines.append(f"- {k}: no longer in main text")
    lines.append(f"## {name}: keys with fewer occurrences")
    for k in sorted(ok):
        if k in nk and nk[k] < ok[k]:
            lines.append(f"- {k}: {ok[k]} -> {nk[k]}")
    lines.append(f"## {name}: new keys")
    for k in sorted(set(nk) - set(ok)):
        lines.append(f"- {k}")
    lines.append("")

BINDING = {
    "NEG abstract/Results sentence (A4.2.3)": "In the preregistered test no improvement was detected under JPEG quality~10, Gaussian noise with $\\sigma=0.10$ or a $128$-pixel splice.",
    "NEG 'not no effect' (A4.2.3)": "This does not show that the gate has no effect.",
    "NEG 6.1 opening (Discussion)": "The preregistered test excludes an improvement or a loss of more than five percentage points in image-direction verification accuracy from gating under JPEG quality~10, Gaussian noise with $\\sigma=0.1$ and a 128-pixel splice, for this model and these severities; it does not show that gating has no effect.",
    "A4.2.4 bullet 1": "We specify, and treat as the object of measurement, an input-level source-validation gate",
    "A4.2.4 bullet 4 (detection)": "At the token level the gate's score separates code-level random replacements",
    "A4.2.4 bullet 5": "We check the clean false-alarm statement on held-out clean test pairs",
    "A6.12 L1 sentence": "On a fresh preregistered fold, the frozen LRF raised image-direction verification accuracy under Gaussian noise ($\\sigma=0.1$) from 0.733 without reliability weighting to 0.802 (net 0.069, 95\\,\\% interval 0.029 to 0.109; exact one-sided McNemar $p=0.0005$; preregistered one-sided $\\alpha=0.05$), including with length-matched negatives",
    "A6.12 L-NI sentence": "On clean images LRF lost no more than three points (90\\,\\% interval of the net change 0.009 to 0.053); the margin was fixed after an exploratory clean interval had been seen.",
    "A6.12 scope {S2}": "in one pretrained unified masked diffusion model (UniDisc, 1.4B parameters), on 450 COCO val2017 images not used to design or fit the method, with Gaussian noise at one severity",
    "A6.12 baselines / Table III A6.6 sentence": "For reference, CLIP ViT-L/14~\\cite{radford2021clip} and SigLIP so400m~\\cite{zhai2023sigmoid}, different models trained on different data, reached accuracies of 0.996 to 1.000",
    "A6.13 disclosure (first)": "Study~2 was added after Study~1 had been analysed (primary result negative), when the target venue changed.",
    "A6.13 disclosure (last)": "Study~2 tests a different method on different images and does not bear on Study~1's conclusion.",
    "D0094 clause": "Before the re-freeze the analysts had also seen the result table of Study~1's re-infilling family",
    "Clean-estimate sentence": "The clean-image estimate was positive (0.887 without weighting, 0.918 with; net 0.031); superiority on clean images was not a preregistered hypothesis.",
    "L4 Holm 0.049": "the Holm-adjusted $p$ is 0.049, a margin of 0.001 below the 0.05 level",
    "LG shot (three p)": "one-sided $p=0.0002$, Holm-adjusted $p=0.0005$, two-sided $p=0.0003$",
    "LG speckle (three p)": "one-sided 0.006, Holm-adjusted 0.011, two-sided 0.011",
    "LG impulse (three p)": "The one-sided and Holm-adjusted $p$ are 0.029 and the two-sided $p$ is 0.058",
    "Impulse CI lower bound": "the 95\\,\\% interval has lower bound 0.0 (0.000 to 0.100)",
    "Multiplicity sentence": "The paper contains 17 preregistered families across the two studies, each tested at its own level with no adjustment across families",
    "Preregistered definition": "\\emph{Preregistered} has one meaning in this paper: a dated analysis-plan addendum was committed to a version-controlled repository",
    "H prefix (Results)": "In a separately labelled family added after the primary result was known (family H: SugarCrepe hard negatives~\\cite{hsieh2023sugarcrepe} on 50 COCO images not used elsewhere; Holm over the same three corruptions)",
    "prop:crc only-guarantee sentence": "This is the only guarantee in the paper",
    "Theory label": "theory under stated assumptions, not validated on UniDisc",
    "Lim: trained on tested corruption": "LRF was trained on the tested corruption",
    "Lim: generic gain": "No preregistered test separates corruption-specific weighting from a generic gain",
    "Lim: title names condition": "the title's ``under Gaussian noise'' names the tested condition, not a specificity",
    "Lim: L4/impulse": "The Holm-adjusted $p$ of L4 is 0.049, and the two-sided $p$ of the impulse-noise cell is 0.058.",
    "Lim: margin fixed": "The clean-image margin of L-NI was fixed after an exploratory clean interval had been seen.",
    "Lim: COCO overlap": "Whether COCO images were in the pretraining data of UniDisc, CLIP or SigLIP is unknown.",
    "Lim: realisation/seed": "Each image has one corruption realisation and one mask seed",
    "Lim: A-8 residual (replaced, runs values)": "it agreed on 98.8\\,\\% and 98.9\\,\\% of image tokens in the two stopped self-checks of card row A-8",
    "Lim: encoders": "The reference encoders almost solve this matching task",
    "Lim: no ablation prereg": "No ablation was preregistered",
    "Lim: random-caption negatives": "All results are for random-caption negatives.",
    "Lim: self-hosted, agent-run": "The preregistration is self-hosted",
}
nt = norm(n_txt + n_tab)
ot = norm(o_txt + o_tab)
lines.append("## Binding sentences (present verbatim in the revised main text, whitespace-normalised)")
lines.append("| item | in original | in revised |")
lines.append("|---|---|---|")
for k, s in BINDING.items():
    lines.append(f"| {k} | {'yes' if norm(s) in ot else 'no'} | {'yes' if norm(s) in nt else 'NO'} |")
dev_o = len(re.findall(r"^\(\d\)", strip_comments((ORIG / "sections/discussion.tex").read_text(encoding="utf-8")), re.M))
dev_n = len(re.findall(r"^\(\d\)", strip_comments((NEW / "sections/discussion.tex").read_text(encoding="utf-8")), re.M))
lines.append(f"\nDeviations box items: {dev_o} in original, {dev_n} in revised.")
print("\n".join(lines))
