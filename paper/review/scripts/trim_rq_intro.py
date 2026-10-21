"""Page limit: merge the population and extraction-reliability paragraphs of Section 5 (both repeat Section 2)."""
import re
from pathlib import Path

p = Path("sections/05-rq-evidence.tex")
t = p.read_text(encoding="utf-8")
lines = t.split("\n")
out = []
for l in lines:
    if l.startswith("\\paragraph{Population and estimates.}"):
        com = l[l.index(" % src"):] if " % src" in l else ""
        out.append(r"\paragraph{Population and estimates.} The sample-based statements describe the included studies: 59 sampled from the 584 open to sampling. Shares are weighted to the stratum sizes and carry 95\% bootstrap intervals, with the unweighted count beside each share; directions rest on one extractor's reading and are stated per study (Section~\ref{sec:method-extraction}). Two further columns are reported apart: 20 seed-corpus studies, and 16 of the 42 landmark studies, whose results by question are in the Supplement." + com)
    elif l.startswith("\\paragraph{Reliability of the extraction.}"):
        continue
    else:
        out.append(l)
p.write_text("\n".join(out), encoding="utf-8")
print("ok")
