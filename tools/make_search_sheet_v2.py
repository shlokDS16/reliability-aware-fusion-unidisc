"""Write the S1'' / S2'' section (D0027, primary run) and the S1' / S2' section (D0026, broader run) of
research/review/corpus/subscription-search-sheet.md.

    python tools/make_search_sheet_v2.py

Each section sits between two HTML comment markers and is replaced on every run; the earlier text of the sheet (the
original strings S1 and S2) is left as it is and becomes the second run. The strings are rendered from the single
specification in tools/search_sources.py (S1P_PARTS, S2P_PARTS), per database dialect. Nothing written here has been run
against the subscription databases; syntax assumptions are marked [unverified], as in the rest of the sheet.

Adaptations, each stated in the sheet:
  - a string is run part by part (A1, A2, A3, B, C for S1'; M, VLA for S2'); the union of the parts is the string
  - phrases ending in * are written with singular and plural where the database does not document wildcards in phrases
  - the exclusion clauses (NOT ...) are kept where the database has NOT with parentheses (Scopus, Web of Science, ACM) and
    dropped where the term budget is small (IEEE Xplore, SpringerLink, ScienceDirect): those runs are broader and the
    excluded topics go out at screening (X1)
  - OR lists longer than the database's term budget are split into runs (union unchanged)
"""
from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_sources as ss  # noqa: E402

SHEET = ss.ROOT / "research" / "review" / "corpus" / "subscription-search-sheet.md"
BEGIN = "<!-- BEGIN S1p-S2p (D0026) -->"
END = "<!-- END S1p-S2p (D0026) -->"
BEGIN2 = "<!-- BEGIN S1pp-S2pp (D0027) -->"
END2 = "<!-- END S1pp-S2pp (D0027) -->"


def expand(p: str, keep_wild_in_phrase: bool):
    """Alternatives of one phrase for a dialect."""
    if not p.endswith("*"):
        return [p]
    if " " not in p and "-" not in p:
        return [p]                                   # single-word wildcard (token*, dllm*, protein*)
    if keep_wild_in_phrase:
        return [p]
    b = p[:-1]
    return [b, b + "s"]


def qt(t: str) -> str:
    return f'"{t}"' if (" " in t or "-" in t) else t


class Dialect:
    def __init__(self, name, wrap, not_op, keep_wild, limit, field_each=None):
        self.name, self.wrap, self.not_op, self.keep_wild, self.limit, self.field_each = name, wrap, not_op, keep_wild, limit, field_each

    def term(self, t):
        alts = [qt(x) for x in expand(t, self.keep_wild)]
        if self.field_each:
            alts = [self.field_each(a) for a in alts]
        return alts


def terms_of(items, d):
    out = []
    for i in items:
        out += d.term(i) if isinstance(i, str) else terms_of(i[1], d)
    return out


def render(spec, d, top=True):
    if isinstance(spec, str):
        a = d.term(spec)
        return a[0] if len(a) == 1 else "(" + " OR ".join(a) + ")"
    op, items = spec
    if op == "OR":
        body = " OR ".join(render(i, d, False) for i in items)
    else:
        pos = [i for i in items if not (isinstance(i, tuple) and i[0] == "NOT")]
        neg = [i for i in items if isinstance(i, tuple) and i[0] == "NOT"]
        body = " AND ".join(render(i, d, False) for i in pos)
        if d.not_op:
            for n in neg:
                body += d.not_op + "(" + " OR ".join(terms_of(n[1], d)) + ")"
    return body if top else "(" + body + ")"


def drop_not(spec):
    if isinstance(spec, str):
        return spec
    op, items = spec
    return (op, [drop_not(i) for i in items if not (isinstance(i, tuple) and i[0] == "NOT")])


def runs(spec, limit, d):
    """Split into runs whose OR lists carry at most `limit` rendered terms; the union of the runs is the spec."""
    if isinstance(spec, str):
        return [spec]
    op, items = spec
    if op == "NOT":
        return [spec]
    if op == "OR":
        strs = [i for i in items if isinstance(i, str)]
        rest = [i for i in items if not isinstance(i, str)]
        out = []
        cur, n = [], 0
        for s in strs:
            k = len(d.term(s))
            if n + k > limit and cur:
                out.append(("OR", cur))
                cur, n = [], 0
            cur.append(s)
            n += k
        if cur:
            out.append(cur[0] if len(cur) == 1 else ("OR", cur))
        for r in rest:
            out += runs(r, limit, d)
        return out
    prods = [runs(i, limit, d) for i in items]
    return [("AND", list(c)) for c in itertools.product(*prods)]


def label_runs(name, part, spec, d):
    rs = runs(spec, d.limit, d)
    return [(f"{name}-{part}" + (f"-r{i + 1}" if len(rs) > 1 else ""), r) for i, r in enumerate(rs)]


DIALECTS = {
    "scopus": Dialect("scopus", lambda s: f"TITLE-ABS-KEY({s}) AND PUBYEAR > 2020 AND PUBYEAR < 2027 AND LANGUAGE(english)", " AND NOT ", True, 40),
    "wos": Dialect("wos", lambda s: f"TS=({s}) AND PY=(2021-2026)", " NOT ", True, 40),
    "ieee": Dialect("ieee", lambda s: s, None, False, 6,
                    field_each=lambda a: f'("Document Title":{a} OR "Abstract":{a} OR "Author Keywords":{a})'),
    "acm": Dialect("acm", lambda s: f"(Title:({s}) OR Abstract:({s}) OR Keyword:({s}))", " NOT ", False, 40),
    "springer": Dialect("springer", lambda s: s, None, False, 8),
    "sciencedirect": Dialect("sciencedirect", lambda s: s, None, False, 4),
}

PARTS_NOTE = {
    "A1": "names of diffusion language models (no context clause)",
    "A2": "discrete diffusion, masked diffusion, discrete flow, discrete state space: with a language word, or, in the dialects that keep NOT, without a biochemical or visual word",
    "A3": "absorbing state, any-order generation, non-autoregressive language models, non-autoregressive with diffusion",
    "B": "diffusion with text-generation or NLP-task vocabulary",
    "C": "diffusion with a language model or LLM, outside biochemical and visual contexts",
    "M": "unified multimodal understanding and generation with diffusion, masked-generative or flow",
    "VLA": "vision-language-action models with discrete or unified diffusion",
}


PARTS_NOTE_PP = {
    "A1": "names of diffusion language models (no context clause); outside MRI and chemistry words",
    "A2": "discrete / masked diffusion and discrete flow: with a language word (and no physics, MRI, PDE, innovation-diffusion word), or without one (then outside biochemical, visual, physics, social-diffusion and non-text-output words)",
    "A3": "absorbing state, any-order generation (each with a language word and a language-model or diffusion word), non-autoregressive language models, non-autoregressive with diffusion (outside non-text outputs)",
    "B": "diffusion used as a model, together with text-generation or NLP-task vocabulary, outside the exclusion lists",
    "C": "diffusion used as a model, together with a language model or LLM, outside the exclusion lists",
    "M": "unified multimodal understanding and generation with diffusion, masked-generative or flow, with a language word",
    "VLA": "vision-language-action models with discrete or unified diffusion",
}


def exclusion_lists() -> list:
    return [("R4_INNOV (diffusion of innovation, information, technology, knowledge)", ss.R4_INNOV), ("R4_NET (social networks)", ss.R4_NET),
            ("R4_MRI (diffusion MRI)", ss.R4_MRI), ("R4_PHYS (physics, heat, fluids)", ss.R4_PHYS), ("R4_PDE (equations, waves, epidemics)", ss.R4_PDE),
            ("R4_CHEM (microextraction)", ss.R4_CHEM), ("R4_BIOMED (disc diffusion, antimicrobial)", ss.R4_BIOMED),
            ("R4_STABLE (B and C only)", ss.R4_STABLE), ("R4_NT (non-text outputs; A2 without context and A3 non-autoregressive)", ss.R4_NT),
            ("R4_NT_BC (non-text outputs and technique words; B and C only)", ss.R4_NT_BC)]


def section_pp() -> str:
    L = []
    a = L.append
    a(BEGIN2)
    a("## Final strings S1'' and S2'' (decision D0027, protocol section 10 amendment of 2026-10-15): primary run")
    a("")
    import json
    st = json.loads((ss.CORPUS / "final-filter-stats-2026-10-15.json").read_text(encoding="utf8"))
    r4 = json.loads((ss.CORPUS / "string-revision-round4-2026-10-15.json").read_text(encoding="utf8"))
    rc = r4["final"]["recall"]
    a(f"S1'' and S2'' are S1' and S2' with exclusions and extra requirements added for precision (round 4): they keep the same seed "
      f"entries as S1' and S2' ({rc['all540_entries']}/540, MM28 {rc['MM28']}/28, random 50 {rc['R50']}/50), and on the screening queue built from the free "
      f"sources they remove {st['auto_excluded']:,} of {st['queue_records']:,} records, leaving {st['passes']:,} (see `search-v2-report-2026-10-15.md`, "
      "section 12). Every part of S1'' / S2'' is a subset of the same part of S1' / S2', so "
      "nothing is found that S1' / S2' would not find. They are the **primary run**; **S1 and S2 (sections 1 to 6 at the end of this sheet) remain "
      "the second run** (protocol, D0026). Result files go in `...-S1pp-<part>...` and `...-S2pp-<part>...` (`.meta.txt`: string label `S1''` or `S2''`).")
    a("")
    a("Date window, language, part-by-part logging and run splitting are as in the next section. Generated from `tools/search_sources.py` "
      "(`S1PP_PARTS`, `S2PP_PARTS`, lists `R4_*`), the same specification that was applied locally to the queue.")
    a("")
    a("**Term-limited databases (IEEE Xplore, SpringerLink, ScienceDirect).** The requirements and exclusions of S1'' do not fit their term budgets "
      "(the run counts are given under each database). For these three, run the **S1' / S2' runs of the next section** (NOT clauses dropped); "
      "lit-scout then applies S1'' and S2'' to the exports locally on title and abstract, which gives exactly the S1'' / S2'' result for those records. "
      "For Scopus, Web of Science and ACM the strings below are run as written.")
    a("")
    a("### The final strings in database-neutral form (verbatim)")
    a("")
    a("Reading rule: AND binds tighter than OR; a trailing `*` is a word-prefix wildcard; `NOT (...)` excludes any of the listed words.")
    a("")
    for n in ("S1''", "S2''"):
        a(f"{n}:")
        a("```")
        a(ss.render_spec(ss.P_SPECS[n], "plain"))
        a("```")
        a("")
    a("Parts (each is a string on its own; S1'' = A1 OR A2 OR A3 OR B OR C; S2'' = M OR VLA):")
    a("")
    for n in ("S1''", "S2''"):
        for k, sp in ss.P_PARTS[n].items():
            a(f"- `{n}:{k}` ({PARTS_NOTE_PP[k]}):")
            a("  ```")
            a("  " + ss.render_spec(sp, "plain"))
            a("  ```")
    a("")
    a("Exclusion lists of round 4 (each term is a word or phrase; the lists are used in the parts as stated in the notes above):")
    a("")
    for nm, lst in exclusion_lists():
        a(f"- {nm}: " + ", ".join(f"`{t}`" for t in lst))
    a("")
    a("Biochemical and visual lists as in the next section.")
    a("")
    notes = {
        "scopus": "Advanced document search; NOT is written `AND NOT`. The query is long (the parts carry up to about 170 excluded terms) **[unverified: Scopus' query-length limit]**; if Scopus refuses a part, run the S1' form of the same part (next section) and let lit-scout apply S1'' locally.",
        "wos": "Advanced Search, Topic (`TS=`) as in the next section. Long NOT lists **[unverified: query-length limit]**; fall back to the S1' form of the part if refused.",
        "acm": "Advanced Search, query-syntax box. NOT written `NOT`; phrases with `*` written as singular and plural. Long NOT lists **[unverified]**; fall back to the S1' form of the part if refused.",
    }
    titles = {"scopus": "Scopus", "wos": "Web of Science Core Collection", "acm": "ACM Digital Library",
              "ieee": "IEEE Xplore", "springer": "SpringerLink", "sciencedirect": "ScienceDirect"}
    folders = {"scopus": "scopus", "wos": "web-of-science", "ieee": "ieee-xplore", "acm": "acm-dl", "springer": "springerlink",
               "sciencedirect": "sciencedirect"}
    for key, d in DIALECTS.items():
        fo = folders[key]
        a(f"### {titles[key]} (folder `{fo}`; file names `{fo}-S1pp-<part>[-rN]-<YYYYMMDD>` and `{fo}-S2pp-<part>[-rN]-<YYYYMMDD>`)")
        a("")
        if not d.not_op:
            total = 0
            for n, name in (("S1''", "S1pp"), ("S2''", "S2pp")):
                for k, sp in ss.P_PARTS[n].items():
                    total += len(label_runs(name, k, drop_not(sp), d))
            a(f"Not run here as S1'' / S2'': even without the NOT clauses the requirements of the final strings would need **{total} runs** at this database's "
              "term budget. Run the S1' / S2' runs of the next section (file names `...-S1p-...`, `...-S2p-...`); S1'' / S2'' are applied locally to the export.")
            a("")
            continue
        a(notes[key])
        a("")
        for n, name in (("S1''", "S1pp"), ("S2''", "S2pp")):
            for k, sp in ss.P_PARTS[n].items():
                for lab, r in label_runs(name, k, sp, d):
                    a(f"{lab}:")
                    a("```")
                    a(d.wrap(render(r, d)))
                    a("```")
        a("")
    a("After the exports are in place the checks at the end of this sheet apply unchanged. lit-scout applies S1'' and S2'' locally to every "
      "export record (title and abstract) before merging, so a database that ignores part of a string does not change what enters screening.")
    a(END2)
    return "\n".join(L) + "\n"


def section() -> str:
    L = []
    a = L.append
    a(BEGIN)
    a("## Revised strings S1' and S2' (decision D0026, protocol section 10 amendment of 2026-10-15): broader run (primary run on IEEE Xplore, SpringerLink and ScienceDirect)")
    a("")
    a("Since D0027 the primary run is S1'' / S2'' (previous section), which are subsets of the strings below. S1' / S2' are kept for three reasons: "
      "they are what was run on the free sources, they are the run for the three databases whose term budgets cannot hold S1'' / S2'', and "
      "they are the fallback when Scopus, Web of Science or ACM refuses a part of S1'' / S2''. Everything below is as written on 2026-10-15 (D0026).")
    a("")
    a("The pilot (all 28 multimodal and a random 50 other seed papers) found that S1 and S2 miss seed papers whose abstracts use other "
      "words (`dLLM`, `diffusion-based LLM`, `large language diffusion model`, discrete or masked diffusion without a language word, "
      "diffusion drafters for speculative decoding, continuous or latent diffusion language models, NLP-task diffusion models, "
      "vision-language-action). The revised strings S1' and S2' replaced S1 and S2 as the primary run until D0027. **Keep the original strings "
      "S1 and S2 (sections 1 to 6 below) as a second run** in the same databases, same search date: their results go in files named "
      "`...-S1-...` and `...-S2-...` as before; the revised ones in `...-S1p-...` and `...-S2p-...` (`.meta.txt`: string label `S1'` or `S2'`). "
      "The two result sets overlap and are deduplicated afterwards.")
    a("")
    a("Date window and language are those of section 3 of the protocol (2021-01-01 to the search date, English). Everything below is generated "
      "from one specification (`tools/search_sources.py`, `S1P_PARTS` and `S2P_PARTS`), so the strings cannot drift from what the agents ran on "
      "arXiv, Semantic Scholar, OpenAlex, OpenReview and the ACL Anthology. A string is run **part by part**; the union of the parts is the "
      "string. Log each part as its own search (`S1p-A1`, `S1p-A2`, ...); do not merge the export files. Where a database cannot hold a part "
      "in one query, the part is cut into runs (`-r1`, `-r2`, ...) whose union is the part.")
    a("")
    a("### The revised strings in database-neutral form (verbatim)")
    a("")
    a("Reading rule: AND binds tighter than OR; a trailing `*` is a word-prefix wildcard; `NOT (...)` excludes any of the listed words.")
    a("")
    for n in ("S1'", "S2'"):
        a(f"{n}:")
        a("```")
        a(ss.render_spec(ss.P_SPECS[n], "plain"))
        a("```")
        a("")
    a("Parts (each is a string on its own; S1' = A1 OR A2 OR A3 OR B OR C; S2' = M OR VLA):")
    a("")
    for n in ("S1'", "S2'"):
        for k, sp in ss.P_PARTS[n].items():
            a(f"- `{n}:{k}` ({PARTS_NOTE[k]}):")
            a("  ```")
            a("  " + ss.render_spec(sp, "plain"))
            a("  ```")
    a("")
    a("Biochemical exclusion list: " + ", ".join(f"`{t}`" for t in ss.P_BIO[1]) + ". Visual exclusion list: " + ", ".join(f"`{t}`" for t in ss.P_VIS[1]) +
      ". These implement exclusion X1 of the protocol (diffusion for molecules, proteins, images, video or audio without text) and keep the "
      "export sizes manageable; a paper that has a language word in the abstract is not removed by them in A2.")
    a("")
    notes = {
        "scopus": "Advanced document search. NOT is written `AND NOT`. Wildcards inside quoted phrases are the same **[unverified]** as in section 1; if Scopus warns, use the plural-expanded form of section 1's fallback.",
        "wos": "Advanced Search. Topic (`TS=`) as in section 2; replace `TS=(X)` by `(TI=(X) OR AB=(X) OR AK=(X))` for the strict title-abstract-keyword reading. Wildcards in phrases **[unverified]**.",
        "ieee": "Command Search. Each term is written in the three fields as in section 3. The NOT clauses are **dropped** here (term budget); the runs are broader than S1'/S2' and the excluded topics go out at screening (X1). Phrases are written with singular and plural instead of `*`. The term limit **[unverified]** is taken as 6 per OR list; shorten the lists if IEEE refuses a run.",
        "acm": "Advanced Search, query-syntax box as in section 4. NOT is written `NOT`; Title, Abstract and Keyword fields repeat the expression. Wildcards in phrases are not assumed (singular and plural written out) **[unverified]**.",
        "springer": "Main keyword box (full text, relevance sorted, 1,000-record cap) as Run B of section 5 and title box as Run A. NOT clauses are **dropped**; run the parts in the *title* box (Run A form) first, since the text cannot be limited to the abstract. Record which box each file came from.",
        "sciencedirect": "Field *Title, abstract or author-specified keywords* as in section 6. The reported cap of 8 Boolean operators per field **[unverified]** is met by cutting OR lists to 4 terms; NOT clauses are **dropped** (excluded topics go out at screening, X1).",
    }
    titles = {"scopus": "Scopus", "wos": "Web of Science Core Collection", "ieee": "IEEE Xplore", "acm": "ACM Digital Library",
              "springer": "SpringerLink", "sciencedirect": "ScienceDirect"}
    folders = {"scopus": "scopus", "wos": "web-of-science", "ieee": "ieee-xplore", "acm": "acm-dl", "springer": "springerlink",
               "sciencedirect": "sciencedirect"}
    for key, d in DIALECTS.items():
        fo = folders[key]
        a(f"### {titles[key]} (folder `{fo}`; file names `{fo}-S1p-<part>[-rN]-<YYYYMMDD>` and `{fo}-S2p-<part>[-rN]-<YYYYMMDD>`)")
        a("")
        a(notes[key])
        a("")
        for n, name in (("S1'", "S1p"), ("S2'", "S2p")):
            for k, sp in ss.P_PARTS[n].items():
                spec = sp if d.not_op else drop_not(sp)
                for lab, r in label_runs(name, k, spec, d):
                    a(f"{lab}:")
                    a("```")
                    a(d.wrap(render(r, d)))
                    a("```")
        a("")
    a("After the exports are in place the checks of the section at the end of this sheet apply unchanged. lit-scout evaluates each part "
      "again locally on title and abstract with the specification above before merging, so a database that ignores part of a string does not "
      "change what enters screening.")
    a(END)
    return "\n".join(L) + "\n"


def main():
    text = SHEET.read_text(encoding="utf8")
    sec2 = section_pp()
    if BEGIN2 in text:
        pre, rest = text.split(BEGIN2, 1)
        text = pre + sec2.rstrip("\n") + rest.split(END2, 1)[1]
    else:
        text = text.replace(BEGIN, sec2 + "\n" + BEGIN, 1)
    step2 = "2. For each database and each string (S1, S2): paste the string"
    if step2 in text:
        text = text.replace(step2, "2. For each database and each string (**primary run: S1'' and S2'', part by part, first section below; second run: S1 and S2**): paste the string", 1)
    sec = section()
    if BEGIN in text:
        pre, rest = text.split(BEGIN, 1)
        post = rest.split(END, 1)[1]
        new = pre + sec.rstrip("\n") + post
    else:
        marker = "## The protocol strings (verbatim, protocol.md section 3)"
        assert marker in text
        new = text.replace(marker, sec + "\n---\n\n## Original strings S1 and S2 (second run): " + marker[3:], 1)
        new = new.replace("## Original strings S1 and S2 (second run): The protocol strings (verbatim, protocol.md section 3)",
                          "## Original strings S1 and S2 (second run): the protocol strings, verbatim from protocol.md section 3")
    SHEET.write_text(new, encoding="utf8")
    print(f"sheet updated: {len(new)} characters; section {len(sec)} characters")


if __name__ == "__main__":
    main()
