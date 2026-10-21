"""Figure 1: PRISMA 2020 flow diagram, every number read from analysis/prisma/prisma-flow.json (itself written by
analysis/prisma/prisma_flow.py from the search, screening and full-text files) and analysis/rq1/rq1-counts.json.
Version 2 (2026-10-20, session 0839c9f4): three identification strands (seed corpus, free-source update,
subscription databases), title/abstract screening per strand, full-text tranche T1, the re-check tranche R797 frozen
by D0051, and the sets identified but not screened (dashed). Arithmetic between boxes is asserted, not typed.

    python paper/review/scripts/fig01_prisma.py
Writes paper/review/figures/fig01-prisma.pdf, preview/fig01-prisma.png and fig01-prisma.log (every number drawn).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from figstyle import C, FIGDIR, ROOT, TEXTWIDTH_IN, save, setup

setup()
F = json.load(open(ROOT / "analysis/prisma/prisma-flow.json", encoding="utf-8"))
RQ1 = json.load(open(ROOT / "analysis/rq1/rq1-counts.json", encoding="utf-8"))
sd, fr, sb, ft, rc, r7, ns = (F[k] for k in ("seed", "free", "subscription", "full_text_T1", "recheck",
                                              "full_text_R797", "not_screened_D0051"))


def f(x):
    return f"{x:,}"


n = {}
# ---------------------------------------------------------------- seed corpus
n["seed_id"] = sd["identified_arxiv_S1"] + sd["identified_arxiv_S2"] + sd["identified_awesome_dlms"]
assert n["seed_id"] - sd["duplicates_merged"] == sd["records_after_dedup"] == sd["ta_screened_dual_v1"]
assert sd["ta_screened_dual_v1"] - sd["ta_both_exclude"] == sd["ta_pass_either"]
n["s1243"] = ns["seed_tranche_S1243_D0037"]["frame"]
n["seed_pass_not_in_frame"] = sd["ta_pass_either"] - n["s1243"]          # duplicate of an update record (R0484)
assert n["seed_pass_not_in_frame"] >= 0
# ---------------------------------------------------------------- free-source update
n["upd_db"], n["upd_cit"] = fr["identified_databases"], fr["identified_citation_searching"]
n["upd_id"] = n["upd_db"] + n["upd_cit"]
ms = json.load(open(ROOT / "research/review/corpus/search-v2-merge-stats-2026-10-15.json", encoding="utf-8"))
new_per_source = sum(v["new"] for v in ms["sources"].values())
n["upd_across"] = new_per_source - fr["new_records_after_dedup"] - fr["extra_duplicate_key_merges"]
n["upd_dup"] = (fr["duplicates_within_source"] + fr["duplicates_against_seed_corpus"] + n["upd_across"]
                + fr["extra_duplicate_key_merges"])
assert n["upd_id"] - n["upd_dup"] == fr["new_records_after_dedup"]
n["upd_auto"] = fr["automation_excluded_D0026"] + fr["automation_excluded_D0027"]
assert fr["new_records_after_dedup"] - n["upd_auto"] == fr["queue_final_D0027"]
assert fr["queue_final_D0027"] + fr["released_D0028"] == fr["ta_screened_dual"]
assert fr["ta_screened_dual"] - fr["ta_both_exclude"] == fr["ta_pass_D0030"]
rf = ns["free_source_rescue_positives_D0036"]
assert fr["rescue_decisions"]["exclude"] + fr["rescue_positives"] == fr["rescue_screened_single_haiku"]
assert rf["positives"] == fr["rescue_positives"]
# ---------------------------------------------------------------- subscription databases
rb = sb["removed_before_screening"]
n["sub_dup"] = sum(v for k, v in rb.items() if k.startswith("duplicates"))
n["sub_front"] = rb["proceedings_front_matter_not_documents"]
assert sb["identified"] - n["sub_dup"] - n["sub_front"] == sb["new_unique_records"]
assert sb["new_unique_records"] - sb["automation_excluded_S1pp_S2pp"] == sb["queue_string_pass"]
assert sb["rescue_screened_single_haiku"] + sb["automation_excluded_without_abstract_pending"] == sb["automation_excluded_S1pp_S2pp"]
assert sb["dual_screened_from_queue"] + sb["dual_screened_from_rescue"] == sb["ta_screened_dual"]
n["sub_ta_excl"] = sb["ta_screened_dual"] - sb["ta_pass_D0030"]
# ---------------------------------------------------------------- full text T1
st = ft["status_ft_routes"]
sx = ft["status_ft_routes_extra"]
n["t1_not_retrieved"] = (st["no_full_text_found"] + st["pending_e_gateway"] + st["open_access_fetch_failed_not_pdf"]
                         + st["open_access_fetch_failed_error"] + st["not_retrieved_openreview_note_missing_X6"]
                         + sx.get("pending_oa_url", 0) + sx.get("pending_e-gateway", 0))
n["t1_awaitB"] = st.get("awaiting_second_screener_B_unavailable", 0) + sx.get("awaiting_second_screener_B_unavailable", 0)
n["t1_assessed"] = ft["screened"] + n["t1_awaitB"]
assert ft["reports_sought"] == n["t1_assessed"] + n["t1_not_retrieved"]
assert ft["screened"] == ft["include"] + ft["exclude"] == sum(ft["exclude_codes"].values()) + ft["include"]
n["t1_fromTA"] = F["title_abstract_total"]["ta_pass_total"]
assert n["t1_fromTA"] == fr["ta_pass_D0030"] + sb["ta_pass_D0030"]
# ---------------------------------------------------------------- re-check tranche R797
n["r7_assessed"] = r7["screened_decided"] + len(r7["awaiting_second_screener_B_unavailable"]) + len(r7["awaiting_C"])
assert r7["frame"] == n["r7_assessed"] + r7["identified_not_screened_D0051"]
assert r7["screened_decided"] == r7["include"] + r7["exclude"] == sum(r7["exclude_codes"].values()) + r7["include"]
n["included"] = ft["include"] + r7["include"]
assert n["included"] == RQ1["n"]
n["not_screened_total"] = n["s1243"] + r7["identified_not_screened_D0051"] + rf["positives"]

FIGDIR.mkdir(exist_ok=True)
(FIGDIR / "fig01-prisma.log").write_text("\n".join(f"{k} = {v}" for k, v in n.items()) + "\n", encoding="utf8")


def codes(d):
    return ", ".join(f"{k} {v}" for k, v in sorted(d.items()))


# ---------------------------------------------------------------- drawing (points)
W = TEXTWIDTH_IN * 72
LH, FS = 7.6, 6.3
B, N_ = "bold", "normal"
STRIP = 13.0
COLS = [STRIP + 2, STRIP + 2 + (W - STRIP - 2) / 3, STRIP + 2 + 2 * (W - STRIP - 2) / 3]
CW = (W - STRIP - 2) / 3 - 4                  # column width
GX = 20                                       # offset of the side boxes from the column's left edge
GW = CW - GX                                  # side-box width
VX = 9                                        # x of the column's vertical flow line from its left edge


def hb(lines):
    return len(lines) * LH + 5


class Canvas:
    def __init__(self):
        self.items = []

    def box(self, x, y, w, lines, kind="main"):
        self.items.append(("box", x, y, w, lines, kind))
        return y + hb(lines)

    def line(self, p, q, dashed=False, arrow=False):
        self.items.append(("line", p, q, dashed, arrow))


cv = Canvas()
GAP = 4
SIDE = 3


def column(ci, y, steps):
    """steps: list of ('main'|'dashed', lines) and ('side', lines) entries; side boxes hang off the flow line."""
    x0 = COLS[ci]
    prev_bottom = None
    for kind, lines in steps:
        if kind == "side":
            yc = y + SIDE
            cv.box(x0 + GX, yc, GW, lines, "side")
            cv.line((x0 + VX, yc + hb(lines) / 2), (x0 + GX, yc + hb(lines) / 2), arrow=True)
            y = yc + hb(lines) + SIDE
        else:
            if prev_bottom is not None:
                y += GAP
                cv.line((x0 + VX, prev_bottom), (x0 + VX, y), dashed=(kind == "dashed"), arrow=True)
            bottom = cv.box(x0, y, CW, lines, kind)
            prev_bottom, y = bottom, bottom
    return y, prev_bottom


y0 = 4.0
head = [[("Seed corpus", B), ("2026-10-13 and 10-14", N_)],
        [("Search update", B), ("2026-10-15", N_)],
        [("Subscription databases", B), ("2026-10-15 and 10-16", N_)]]
for ci, h in enumerate(head):
    cv.box(COLS[ci], y0, CW, h, "head")
yI = y0 + hb(head[0]) + 4

seed = [("main", [("Records identified", B), (f"n = {f(n['seed_id'])}", N_),
                  (f"arXiv S1 {f(sd['identified_arxiv_S1'])}, S2 {f(sd['identified_arxiv_S2'])}", N_),
                  (f"Awesome-DLMs list {f(sd['identified_awesome_dlms'])}", N_)]),
        ("side", [("Duplicates removed", B), (f"n = {f(sd['duplicates_merged'])}", N_)]),
        ("main", [("Title/abstract screened", B), ("two screeners, criteria v1", N_),
                  (f"n = {f(sd['ta_screened_dual_v1'])}", N_)]),
        ("side", [("Excluded by both", B), (f"n = {f(sd['ta_both_exclude'])}", N_)]),
        ("main", [("Passed by either screener", B), (f"n = {f(sd['ta_pass_either'])}", N_)]),
        ("side", [("Duplicate of an", B), ("update record", B), (f"n = {f(n['seed_pass_not_in_frame'])}", N_)]),
        ("dashed", [("Not assessed at full text", B), ("(screening frozen, D0051)", N_),
                    (f"n = {f(n['s1243'])}", N_),
                    (f"{f(ns['seed_tranche_S1243_D0037']['assessed_later_in_landmark_tranche_D0061'])} later assessed in tranche L", N_)])]
upd = [("main", [("Records identified", B), (f"n = {f(n['upd_id'])}", N_),
                 (f"5 databases {f(n['upd_db'])}", N_), (f"citation searching {f(n['upd_cit'])}", N_)]),
       ("side", [("Duplicates removed", B), (f"n = {f(n['upd_dup'])}", N_), (f"of seed records {f(fr['duplicates_against_seed_corpus'])}", N_)]),
       ("main", [("New records", B), (f"n = {f(fr['new_records_after_dedup'])}", N_)]),
       ("side", [("Removed by string filter", B), (f"n = {f(n['upd_auto'])}", N_),
                 (f"{f(fr['released_D0028'])} released back", N_)]),
       ("main", [("Title/abstract screened", B), ("two screeners", N_), (f"n = {f(fr['ta_screened_dual'])}", N_)]),
       ("side", [("Excluded by both", B), (f"n = {f(fr['ta_both_exclude'])}", N_)]),
       ("main", [("Passed to full text", B), (f"n = {f(fr['ta_pass_D0030'])}", N_)])]
sub = [("main", [("Records identified", B), (f"n = {f(sb['identified'])}", N_), ("Scopus, WoS, IEEE Xplore,", N_),
                 ("ACM DL, Springer, ScienceDirect", N_)]),
       ("side", [("Removed before screening", B), (f"duplicates {f(n['sub_dup'])}", N_), (f"front matter {f(n['sub_front'])}", N_)]),
       ("main", [("New records", B), (f"n = {f(sb['new_unique_records'])}", N_)]),
       ("side", [("Failed string filter", B), (f"n = {f(sb['automation_excluded_S1pp_S2pp'])}", N_),
                 (f"rescue-screened {f(sb['rescue_screened_single_haiku'])}", N_),
                 (f"{f(sb['rescue_positives'])} back to screening;", N_),
                 (f"{f(sb['automation_excluded_without_abstract_pending'])} without abstract", N_)]),
       ("main", [("Title/abstract screened", B), ("two screeners", N_), (f"n = {f(sb['ta_screened_dual'])}", N_)]),
       ("side", [("Excluded by both", B), (f"n = {f(n['sub_ta_excl'])}", N_)]),
       ("main", [("Passed to full text", B), (f"n = {f(sb['ta_pass_D0030'])}", N_)])]
ends = [column(i, yI, s) for i, s in enumerate((seed, upd, sub))]
yS_end = max(e[0] for e in ends)

# side note in the update column: single-screener rescue of filtered records (not screened further)
yR = ends[1][0] + 6
cv.box(COLS[1] + GX, yR, GW, [("Rescue screen of filtered", B), (f"records: {f(fr['rescue_screened_single_haiku'])}", N_),
                               (f"{f(rf['positives'])} positives; {f(rf['dual_ta_screened'])} dual-", N_),
                               (f"screened, {f(rf['dual_ta_pass'])} passed", N_), ("not assessed (D0051)", B)], "dashed")
yRb = yR + hb([1, 2, 3, 4, 5])

# ---------------------------------------------------------------- full text: T1 over the update and subscription columns
xL = COLS[1]
WW = COLS[2] + CW - COLS[1]
yT = max(yS_end, yRb) + 10
for ci in (1, 2):
    cv.line((COLS[ci] + VX, ends[ci][1]), (COLS[ci] + VX, yT - 2), arrow=False)
cv.line((COLS[1] + VX, yT - 2), (COLS[2] + VX, yT - 2))
cv.line((xL + VX + 30, yT - 2), (xL + VX + 30, yT), arrow=True)
t1 = [("main", [("Full-text tranche T1: reports sought", B),
                (f"n = {f(ft['reports_sought'])} ({f(n['t1_fromTA'])} title/abstract passes and re-check samples)", N_)]),
      ("side", [("Not retrieved", B), (f"n = {f(n['t1_not_retrieved'])}: no full text {st['no_full_text_found']}, e-gateway "
                                       f"{st['pending_e_gateway'] + sx.get('pending_e-gateway', 0)}, open access failed "
                                       f"{st['open_access_fetch_failed_not_pdf'] + st['open_access_fetch_failed_error'] + sx.get('pending_oa_url', 0)},", N_),
                (f"OpenReview note missing (X6) {st['not_retrieved_openreview_note_missing_X6']}", N_)]),
      ("main", [("Reports assessed (two screeners, adjudicator)", B), (f"n = {f(n['t1_assessed'])}", N_)]),
      ("side", [("Excluded", B), (f"n = {f(ft['exclude_incl_resolved'])}: {codes(ft['exclude_codes_incl_resolved'])}", N_),
                (f"incl. {len(ft['resolved_B_unavailable_D0058'])} read by screener A only, confirmed by the first author", N_)]),
      ("main", [("Included from T1", B), (f"n = {f(ft['include'])}", N_)])]
GX_save, GW_save, CW_save = GX, GW, CW
GX, GW, CW = 34, WW - 34, WW
COLS_save = COLS[:]
COLS = [None, xL, None]
yT_end, t1_bottom = column(1, yT, t1)

# R797 in the seed column, beside T1
COLS = COLS_save
GX, GW, CW = GX_save, GW_save, CW_save
r7s = [("main", [("Re-check of title/abstract", B), ("exclusions: K = " + str(rc["K"]["K"]) + " of " + str(sum(rc["K"]["counts"].values()) - rc["K"]["counts"]["not_in_T1"]), N_),
                 (f"triggered: {f(rc['frame'])} candidates,", N_), (f"tranche R797 n = {f(r7['frame'])}", N_)]),
       ("side", [("Not assessed", B), ("(frozen, D0051)", N_), (f"n = {f(r7['identified_not_screened_D0051'])}", N_)]),
       ("main", [("Reports assessed", B), (f"n = {f(n['r7_assessed'])}", N_)]),
       ("side", [("Excluded", B), (f"n = {f(r7['exclude_incl_resolved'])}", N_),
                 (f"incl. {len(r7['resolved_B_unavailable_D0058'])} confirmed by", N_), ("the first author", N_)]),
       ("main", [("Included from R797", B), (f"n = {f(r7['include'])}", N_)])]
yR7_end, r7_bottom = column(0, yT, r7s)

# ---------------------------------------------------------------- included
yInc = max(yT_end, yR7_end) + 10
inc = [("Studies included in the review", B), (f"n = {f(n['included'])} (T1 {f(ft['include'])} + R797 {f(r7['include'])})", N_),
       (f"extraction and appraisal on a stratified random sample of 80, with a seed stratum (D0052, D0054)", N_)]
cv.line((COLS[0] + VX, r7_bottom), (COLS[0] + VX, yInc - 3))
cv.line((xL + VX, t1_bottom), (xL + VX, yInc - 3))
cv.line((COLS[0] + VX, yInc - 3), (xL + VX, yInc - 3))
cv.line((COLS[0] + VX + 60, yInc - 3), (COLS[0] + VX + 60, yInc), arrow=True)
yEnd = cv.box(COLS[0], yInc, W - COLS[0] - 4, inc, "main")

# ---------------------------------------------------------------- landmark tranche L (D0061): other methods, one row
lt = F["landmark_tranche_D0061"]
assert lt["identified"] == lt["identified_from_unscreened_seed_S1243"] + lt["identified_removed_by_string_filter_D0026"]
assert lt["reports_assessed"] == lt["include"] + lt["exclude"] == sum(lt["exclude_codes"].values()) + lt["include"]
assert lt["frame_models"] - lt["models_already_included_615"] == lt["identified"]
n.update(lmk_identified=lt["identified"], lmk_assessed=lt["reports_assessed"], lmk_include=lt["include"])
yL = yEnd + 10
row = [[("Identification via", B), ("other methods (D0061):", B), ("landmark models not in", N_),
        (f"the {f(n['included'])}: n = {f(lt['identified'])}", N_),
        (f"seed {lt['identified_from_unscreened_seed_S1243']}, string filter {lt['identified_removed_by_string_filter_D0026']}", N_)],
       [("Reports sought", B), (f"n = {f(lt['reports_sought'])}", N_), ("Reports retrieved", B), (f"n = {f(lt['reports_retrieved'])}", N_)],
       [("Reports assessed", B), (f"n = {f(lt['reports_assessed'])}", N_), ("Excluded", B),
        (f"n = {f(lt['exclude'])}: {codes(lt['exclude_codes'])}", N_)],
       [("Landmark tranche", B), ("included", B), (f"n = {f(lt['include'])}, reported", N_), (f"apart from the {f(n['included'])}", N_)]]
GAPX = 8
BW = (W - COLS[0] - 4 - 3 * GAPX) / 4
hmax = max(len(r) for r in row)
for k, lines in enumerate(row):
    x = COLS[0] + k * (BW + GAPX)
    cv.box(x, yL, BW, lines + [("", N_)] * (hmax - len(lines)), "main")
    if k:
        cv.line((x - GAPX, yL + hb([0] * hmax) / 2), (x, yL + hb([0] * hmax) / 2), arrow=True)
yEnd = yL + hb([0] * hmax)
(FIGDIR / "fig01-prisma.log").write_text("\n".join(f"{k} = {v}" for k, v in n.items()) + "\n", encoding="utf8")
H = yEnd + 4

fig, ax = plt.subplots(figsize=(TEXTWIDTH_IN, H / 72))
fig.subplots_adjust(0, 0, 1, 1)
ax.set_xlim(0, W)
ax.set_ylim(H, 0)
ax.axis("off")
for it in cv.items:
    if it[0] == "box":
        _, x, y, w, lines, kind = it
        h = hb(lines)
        kw = dict(boxstyle="square,pad=0", linewidth=0.6, edgecolor=C["black"], facecolor="white", zorder=2)
        if kind == "side":
            kw["facecolor"] = C["lightgrey"]
        if kind == "head":
            kw.update(facecolor=C["sky"], alpha=0.35, linewidth=0)
        if kind == "dashed":
            kw.update(linestyle=(0, (3, 2)), edgecolor="#404040")
        ax.add_patch(FancyBboxPatch((x, y), w, h, **kw))
        for i, (txt, wt) in enumerate(lines):
            ax.text(x + w / 2, y + 2.5 + LH / 2 + i * LH, txt, ha="center", va="center", fontsize=FS, fontweight=wt,
                    color="#404040" if kind == "dashed" else C["black"], zorder=3)
    else:
        _, p, q, dashed, arrow = it
        if arrow:
            ax.annotate("", xy=q, xytext=p, zorder=1,
                        arrowprops=dict(arrowstyle="-|>", mutation_scale=5, lw=0.6, shrinkA=0, shrinkB=0,
                                        color="#404040" if dashed else C["black"],
                                        linestyle=(0, (3, 2)) if dashed else "-"))
        else:
            ax.plot([p[0], q[0]], [p[1], q[1]], color=C["black"], lw=0.6, zorder=1)


def band(top, bot, label, colour):
    ax.add_patch(Rectangle((0, top), STRIP - 3, bot - top, facecolor=colour, edgecolor="none", zorder=0, alpha=0.45))
    ax.text((STRIP - 3) / 2, (top + bot) / 2, label, rotation=90, ha="center", va="center", fontsize=FS, fontweight=B)


band(yI, yI + 50, "Identification", C["sky"])
band(yI + 52, yS_end, "Screening", C["green"])
band(yT, yL - 2, "Full text and included", C["orange"])
band(yL, yEnd, "Other methods", C["lightgrey"])
save(fig, "fig01-prisma")
