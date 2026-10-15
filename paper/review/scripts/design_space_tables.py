"""Build the condensed design-space table (Table 4) and the counts quoted in Sections 4 and 7.

Reads  research/review/coverage/design-space-v1.csv  (47 rows; long form).
Writes paper/review/tables/design-space-condensed.tex and paper/review/tables/design-space-counts.log.
The C1 / C4-position / C5 codes below are the writer's condensation of the long-form free-text cells
(design-space-v1.md section 1); they are NOT columns of the CSV and need a check by the table's author.
Run from paper/review:  python scripts/design_space_tables.py
"""
import csv, re, collections, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[3]
CSV = ROOT / "research/review/coverage/design-space-v1.csv"
BIB = ROOT / "paper/review/references.bib"
OUT = ROOT / "paper/review/tables"
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
K_FIT = "fits (yes/partly/no)"
K_VAL = "value-rule classes (A argmax, T low temp, P top-p/k, S sample-then-filter, G guidance, M sequence-level selection)"
K_HEAD = "headline uses E_sel-type rule"
K_LEV = "lever row(s)"

# id -> (C1 channel, C4 position rule, C5 revision)
CODE = {
 "M01": ("Q", "rnd", "none/impl"), "M02": ("Q", "rnd", "corr"), "M03": ("Er/Un", "rnd", "none/impl"),
 "M04": ("Er", "rnd", "none"), "M05": ("Er", "rnd", "none"), "M06": ("Er", "rnd", "none"),
 "M07": ("Er", "rnd", "none"), "M08": ("Er", "rnd", "none"), "M09": ("Er", "cnf", "none"),
 "M10": ("Er", "cnf", "none"), "M11": ("Er", "rnd", "remask"), "M12": ("Er", "ent", "none"),
 "M13": ("Gs", "all", "impl"), "M14": ("Gs", "all", "impl"), "M15": ("Gs", "all", "impl"),
 "M16": ("Fl", "rnd", "corr"), "M17": ("Un", "all", "impl"), "M18": ("Er", "blk", "none"),
 "M19": ("Sx", "blk", "impl"), "M20": ("AR+Er", "ar, cnf", "none"), "M21": ("Er", "cnf", "none"),
 "M22": ("Er", "cnf", "none"), "M23": ("Er", "cnf", "none"), "M24": ("Fl", "all", "impl"),
 "M25": ("Er", "cnf", "none"), "M26": ("AR+Gs", "ar, all", "impl"), "M27": ("AR+Fl", "ar, all", "impl, out"),
 "M28": ("AR+Fl", "ar, all", "impl"), "M29": ("Er", "ns", "out"), "M30": ("Sx", "all", "impl"),
 "M31": ("Sx", "all", "impl"), "M32": ("Gs", "all", "impl"), "M33": ("Er+Gs", "rnd", "none"),
 "M34": ("Un+aux", "all", "impl"), "M35": ("Er", "ns", "ns"), "M36": ("Er", "rnd", "none"),
 "M37": ("Er", "cnf", "none"), "M38": ("Er+Ed", "blk", "edit"), "M39": ("Er", "ent", "none"),
 "M40": ("Er", "rnd", "none"), "M41": ("Er", "blk", "none"), "M42": ("Un", "all", "impl"),
 "M43": ("Er", "ns", "none"), "M44": ("Er", "ns", "none"), "M45": ("Er", "cnf", "none"),
 "M46": ("Er+Fl", "all, rnd", "impl"), "M47": ("Er", "cnf", "none"),
}
assert set(CODE) == {r["id"] for r in rows}, "code dict does not cover the CSV"

def value_cell(r):
    cls = r[K_VAL].strip()
    head = r[K_HEAD].strip()
    if r["id"] == "M24":
        return "plain (M)"
    if cls:
        c = ",".join(cls.replace(";", ",").split(","))
        return c + (r"$^\dagger$" if head == "controlled" else "")
    return {"na": "lik.", "unclear": "ns", "no": "plain"}.get(head, "ns")

def lever_cell(r):
    s = r[K_LEV]
    codes = sorted({int(x) for x in re.findall(r"\bL(\d+)\b", s)})
    out = ["L%d" % c for c in codes]
    if "sequence-level selection" in s:
        out.append("SL")
    return ",".join(out)

def tex(s):
    return s.replace("&", r"\&").replace("_", r"\_")

name_fix = {"Zheng et al. (time-agnostic, first-hitting)": "Zheng et al.", "Campbell et al. (CTMC)": "Campbell et al.",
            "DFM (discrete flow matching)": "DFM", "Simplax (Simplex Relaxation)": "Simplax",
            "Discrete Copula Diffusion (DCD)": "DCD", "UDLM (Schiff et al., guidance)": "UDLM",
            "D-DiT (Dual Diffusion)": "D-DiT"}
bib = open(BIB, encoding="utf-8").read()
lines = []
for r in rows:
    key = "arXiv:" + r["arXiv ID"].strip()
    if "@misc{%s," % key not in bib:
        sys.exit("missing bib key " + key)
    c1, pos, c5 = CODE[r["id"]]
    nm = tex(name_fix.get(r["name"], r["name"]))
    fit = r[K_FIT]
    fit = r"\textbf{partly}" if fit == "partly" else fit
    lines.append(r"%s & %s~\cite{%s} & %s & %s & %s & %s & %s & %s \\" % (
        r["id"], nm, key, c1, pos, value_cell(r), c5, lever_cell(r), fit))
    if r["id"] == "M29":
        lines.append(r"\midrule")
OUT.mkdir(exist_ok=True)
(OUT / "design-space-condensed.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

log = []
log.append("rows %d" % len(rows))
log.append("fits %s" % dict(collections.Counter(r[K_FIT] for r in rows)))
log.append("evidence level %s" % dict(collections.Counter(r["evidence level"][:2] + ("/primer" if "primer" in r["evidence level"] else "/sections") for r in rows)))
# family groups used in the text (multimodal = any family containing 'unified' or 'hybrid AR+diffusion' or FUDOKI)
def grp(r):
    f = r["family"]
    if "unified" in f or "hybrid AR+diffusion" in f: return "unified multimodal (incl. hybrids)"
    if "Gaussian" in f: return "Gaussian/embedding/logit simplex"
    if f.startswith("absorbing"): return "absorbing"
    if f.startswith("sampler-only"): return "sampler-only"
    if f.startswith("general discrete"): return "general discrete"
    if f.startswith("uniform"): return "uniform"
    if f.startswith("AR-adapted"): return "AR-adapted absorbing (incl. edit)"
    return f
log.append("groups %s" % dict(collections.Counter(grp(r) for r in rows)))
lev = collections.Counter()
for r in rows:
    for c in {int(x) for x in re.findall(r"\bL(\d+)\b", r[K_LEV])}: lev[c] += 1
log.append("lever counts (rows listing the lever) %s" % dict(sorted(lev.items())))
val = [r for r in rows if re.search(r"\bL(11|12)\b", r[K_LEV]) or "sequence-level selection" in r[K_LEV]]
log.append("value-rule row (L11 or L12 or sequence-level selection): %d" % len(val))
part = [(r["id"], r["name"]) for r in rows if r[K_FIT] == "partly"]
log.append("partly rows %s" % part)
(OUT / "design-space-counts.log").write_text("\n".join(log) + "\n", encoding="utf-8")
print("\n".join(log))

# in-sample versus later rows (M01-M29 were copied from the primers on which framework-v1 was built; M30-M47 were read afterwards)
first = [r for r in rows if int(r["id"][1:]) <= 29]
later = [r for r in rows if int(r["id"][1:]) >= 30]
extra = ["M01-M29: %s" % dict(collections.Counter(r[K_FIT] for r in first)),
         "M30-M47: %s" % dict(collections.Counter(r[K_FIT] for r in later))]
with open(OUT / "design-space-counts.log", "a", encoding="utf-8") as f:
    f.write("\n".join(extra) + "\n")
print("\n".join(extra))
