"""Census counts for Figures 1 and 4, taken through the definitions of analysis/census/summary_random.py.

The module runs summary_random.py itself (stdout captured), so every classification function (nonplain,
toks, isna, low, restored, wilson) is the one used for analysis/census/summary-random.log. The captured
output must equal that log byte for byte (after newline normalisation); if it does not, the figures are
not built.
"""
import contextlib
import io
import runpy
from collections import Counter

from figstyle import ROOT

SUMMARY = ROOT / "analysis" / "census" / "summary_random.py"
LOG = ROOT / "analysis" / "census" / "summary-random.log"


def _run():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        g = runpy.run_path(str(SUMMARY))
    return g, buf.getvalue()


def wilson_num(k, n, z=1.959964):
    """Same formula as summary_random.wilson, numeric."""
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / (1 + z * z / n)
    return p, c - h, c + h


def counts(g, R):
    low, isna, nonplain, toks = g["low"], g["isna"], g["nonplain"], g["toks"]
    el = [d for d in R if low(d.get("eligible")) == "yes"]
    v = [d for d in el if nonplain(d) != "NA"]
    m = [d for d in el if not isna(d.get("F1_metric"))]
    npc = Counter(nonplain(d) for d in v)
    sweeps = [d for d in m if low(d.get("F4")) in ("yes", "partial")]
    letters = Counter(t for d in v for t in toks(d.get("F2_codes")) if t in set("ATPSGMC"))
    return dict(
        ranks=len(R),
        no_text=sum(d.get("exclusion_code") == "NO_TEXT" for d in R),
        eligible=len(el),
        excluded=dict(Counter(d.get("exclusion_code") for d in R if low(d.get("eligible")) == "no")),
        n_v=len(v), n_ql=sum(isna(d.get("F1_metric")) for d in v), n_m=len(m), n_noF2=len(el) - len(v),
        stated=npc["yes"], U=npc["no"], NS=npc["unknown"],
        either=npc["yes"] + npc["unknown"],
        letters=dict(sorted(letters.items())),
        f3=sum(low(d.get("F3")) == "yes" for d in m),
        sweeps=len(sweeps),
        f5=sum(low(d.get("F5")) == "stated" for d in sweeps),
        n_sw=len(sweeps),
    )


def load():
    """Return (final, sensitivity, extra) count dictionaries, asserted against summary-random.log."""
    g, out = _run()
    log = LOG.read_text(encoding="utf8")
    assert out.replace("\r\n", "\n").rstrip() == log.replace("\r\n", "\n").rstrip(), \
        "re-running summary_random.py does not reproduce summary-random.log"
    rows = g["rows"]
    R = [rows[r] for r in sorted(rows)]
    S = [g["restored"](r, rows[r]) for r in sorted(rows)]
    fin, sen = counts(g, R), counts(g, S)
    W = g["wilson"]
    # independent assertion of every number used against the log text, line by line
    for name, c in (("final", fin), ("sensitivity", sen)):
        block = log.split("== final")[1] if name == "final" else log.split("== sensitivity")[1]
        if name == "final":
            block = block.split("== sensitivity")[0]
        lines = [
            f"value-rule denominator (eligible with an F2 code, incl. QL): {c['n_v']}; QL (F2 coded, no metric): {c['n_ql']}; "
            f"F3-F6 denominator (eligible with a metric): {c['n_m']}; eligible with no F2 code: {c['n_noF2']}",
            f"headline value rule: non-plain {c['stated']}, plain stated (U) {c['U']}, not stated (NS) {c['NS']}; "
            f"non-plain or not stated {c['either']} of {c['n_v']}",
            f"  non-plain or not stated: {W(c['either'], c['n_v'])}",
            f"  non-plain stated:        {W(c['stated'], c['n_v'])}",
            f"  diversity paired (F3):   {W(c['f3'], c['n_m'])}",
            f"  step settings >= 2 (F4 yes/partial): {W(c['sweeps'], c['n_m'])}",
            f"  rule fixed stated among sweeps (F5): {W(c['f5'], c['n_sw'])}",
            f"letters (papers with each): {c['letters']}",
        ]
        for ln in lines:
            assert ln in block, f"{name}: not in summary-random.log: {ln!r}"
        assert f"eligible {c['eligible']}; excluded {c['excluded']}" in block
        assert f"ranks {c['ranks']}; no text {c['no_text']};" in block
    return fin, sen, dict(log=log, rows=rows, wilson=W)
