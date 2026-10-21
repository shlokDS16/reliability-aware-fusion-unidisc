"""2026-10-21 (decision D0070): the first author's reviewed check sheets replace the earlier ones (research/HUMAN-CHECK-*.xlsx).
Screening agreement recomputed by analysis/screening/human_check_screening_agreement.py (18 of 24 decided, kappa 0.50,
95% interval 0.12 to 0.83, 16 unclear, code 9 of 9); census Q1 by analysis/census/human_check_census_agreement.py
(21 of 24 yes, 2 no, 1 unclear); extraction unchanged. The checks are described as the author's own; AI is named only
in the Declaration. Run from paper/review."""
from pathlib import Path


def edit(f, old, new):
    p = Path(f)
    t = p.read_text(encoding="utf-8")
    if t.count(old) != 1:
        raise SystemExit(f"{f}: anchor found {t.count(old)} times: {old[:80]}")
    p.write_text(t.replace(old, new), encoding="utf-8")


M, L, S = "sections/02-method.tex", "sections/10-limitations.tex", "supplement.tex"
edit(M, "checked three blind random samples instead, validated as described in the Declaration on the use of AI (decisions D0065, D0066).",
     "checked three blind random samples by hand instead (decisions D0065, D0066, D0070).")
edit(M, "the author and the final decision agree on 21 of the 30 both decided ($\\kappa=0.41$, 95\\% interval 0.09 to 0.71; 10 unclear; the exclusion code matches on all 11 joint exclusions)",
     "the author and the final decision agree on 18 of the 24 both decided ($\\kappa=0.50$, 95\\% interval 0.12 to 0.83; 16 unclear, all because the author could not open a full text; the exclusion code matches on all 9 joint exclusions)")
edit(L, "A later blind check of 40 records by the first author, AI-validated and so not an independent human-only check, agreed with the final decisions at only $\\kappa=0.41$",
     "A later blind check of 40 records by the first author agreed with the final decisions at only $\\kappa=0.50$ on the 24 he could decide")
edit(S, ", cross-checked with a separate AI assistant without project access, is in Section~S9.", ", is in Section~S9.")
edit(S, "agreed with the screening at $\\kappa=0.41$,", "agreed with the screening at $\\kappa=0.50$,")
edit(S, "a later blind check of 24 papers by the first author, cross-checked with a separate AI assistant, agrees", "a later blind check of 24 papers by the first author agrees")
edit(S, "checked three blind random samples, cross-checking the answers with a separate AI assistant, which had no access to the project files or to the model answers (decisions D0065, D0066).",
     "checked three blind random samples by hand, without access to the model answers (decisions D0065, D0066, D0070).")
edit(S, "blind checks (cross-checked with a separate AI assistant) and the models'", "blind checks and the models'")
edit(S, "Screening: include or exclude & 40 & 30 & 21 & 0.41 (0.09 to 0.71) \\\\", "Screening: include or exclude & 40 & 24 & 18 & 0.50 (0.12 to 0.83) \\\\")
edit(S, "Screening: exclusion code, both exclude & 11 & 11 & 11 & -- \\\\", "Screening: exclusion code, both exclude & 9 & 9 & 9 & -- \\\\")
p = Path(S)
t = p.read_text(encoding="utf-8")
a = t.index("\\emph{Screening.} The author included 6 records")
b = t.index("\\emph{Extraction.}", a)
t = t[:a] + ("\\emph{Screening.} The author included 4 records that the models excluded and excluded 2 that they included. "
             "All 16 unclear records are ones whose full text the author could not open, so the check rests on 24 decided records. "
             "Agreement is below the protocol's bar of $\\kappa\\ge0.70$, on 40 records rather than at least 100, and no screener prompt was revised; "
             "this is a departure (Section~\\Mref{sec:method-deviations}).\n") + t[b:]
p.write_text(t, encoding="utf-8")
edit(S, "for 20 of the 24 papers (2 no, 2 unclear).", "for 21 of the 24 papers (2 no, 1 unclear).")
print("ok")
