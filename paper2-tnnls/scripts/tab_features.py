"""Study 2 table: the 35 input features of the frozen weight model, in groups, defined by formula (never by any Study 1 role).
Feature names, order and counts are read from analysis_posthoc/learned_ceiling/data.py (loaded by file path, numpy only) and checked against
runs/P2-LRF-FROZEN-LFIX/spec.json "features"; the group of every feature is assigned by its name prefix and the counts are asserted to sum to 35.
The scores B, D, s, v are defined as quantities of the masked network (see Section III notation); l and r are pixel/code quantities.
Output: paper2-tnnls/tables/tab_features.tex"""
from __future__ import annotations

import importlib.util

import figstyle as S
from tablib import row, write

spec = importlib.util.spec_from_file_location("lrf_data", S.REPO / "analysis_posthoc" / "learned_ceiling" / "data.py")
data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data)
names = data.feature_names()
frozen = S.jload("P2-LRF-FROZEN-LFIX/spec.json")
assert names == frozen["features"] and len(names) == 35

G = {
    "token scores": [n for n in names if n in data.RAW],
    "position": [n for n in names if n in ("row", "col", "rad")],
    "neighbourhood": [n for n in names if n.startswith(("nb3", "nb5"))],
    "within-image rank": [n for n in names if n.startswith("rank_")],
    "image mean": [n for n in names if n.startswith("itemmean_")],
    "image standard deviation": [n for n in names if n.startswith("itemsd_")],
    "image z-score": [n for n in names if n == "itemz_q"],
}
assert sum(len(v) for v in G.values()) == 35 and sorted(sum(G.values(), [])) == sorted(names)
L = lambda xs: ", ".join(f"\\texttt{{{x.replace('_', chr(92) + '_')}}}" for x in xs)
DEF = {
    "token scores": r"$B_j$: log-probability of the observed code at token $j$ with the tokens of $j$'s group masked, the other image tokens visible and the caption masked; "
                    r"$D_j$: the same with every token masked; $r_j=B_j-D_j$; \texttt{s3} $=1-\max_y p(y)$ of the pass that gives $B_j$; "
                    r"\texttt{tbv}: log-probability of the observed code from one raw-logit pass with all image tokens visible and the caption masked; "
                    r"\texttt{ltex} $=\log(1+v_j)$, $v_j$ the pixel variance of the $16\times16$ patch of token $j$; "
                    r"\texttt{nbr}: mean $L_2$ distance of the codebook vector of token $j$ to those of its eight neighbours",
    "position": r"\texttt{row}, \texttt{col}: grid row and column of the token divided by 31; \texttt{rad} $=\sqrt{(\mathrm{row}-\tfrac12)^2+(\mathrm{col}-\tfrac12)^2}$",
    "neighbourhood": r"\texttt{nb3mean\_}$k$: mean of score $k$ over the eight neighbours (edge-aware, token excluded); \texttt{nb3min\_q}: their minimum of $r$; "
                     r"\texttt{nb5mean\_q}: mean of $r$ over the $5\times5$ neighbourhood without the token",
    "within-image rank": r"percentile rank of the score among the 1\,024 tokens of the image, in $[0,1]$",
    "image mean": r"mean of the score over the 1\,024 tokens of the image",
    "image standard deviation": r"standard deviation of the score over the 1\,024 tokens of the image",
    "image z-score": r"$(r_j-\bar r)/(\mathrm{sd}(r)+10^{-6})$ within the image",
}
rows = [row([g, str(len(v)), L(v), DEF[g]],
            [f"analysis_posthoc/learned_ceiling/data.py feature_names(), engineer() (names and formulas); runs/P2-LRF-FROZEN-LFIX/spec.json features (order, n_features = 35); group counts computed"])
        for g, v in G.items()]
rows.append(row([r"\textbf{Total}", str(sum(len(v) for v in G.values())), "", ""], ["sum of the group counts (asserted equal to 35)"]))
write("tab_features.tex", "@{}lcp{0.30\\linewidth}p{0.42\\linewidth}@{}", ["Group", "Count", "Features", "Definition"], [rows],
      preamble=["Study 2 feature groups by formula; no feature is described by any role it has in another analysis. Use table* or a smaller font; the Definition column wraps."])
