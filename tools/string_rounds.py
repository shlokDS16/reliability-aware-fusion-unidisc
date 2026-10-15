"""Record of the 2026-10-15 string revision (decision D0026, protocol section 10 amendment).

    python tools/string_rounds.py            # writes research/review/corpus/string-revision-2026-10-15.json

Evaluates, on title + abstract and locally, the original strings S1/S2 and three rounds of revised strings:
  recall on the 540 Awesome-DLMs seed entries (539 distinct arXiv IDs: 2506.17298 is listed twice), on the 28 'Multimodal
  DLMs' entries (MM28) and on the random 50 of the other entries (R50, random.Random(20261015), as pilot-recall-2026-10-15.json);
  the records a round adds over S1/S2 in the pool of records already collected (screening/records.jsonl is excluded: only
  records of new-records-2026-10-15.jsonl, v1), and the manual title labels of a random 200 of them
  (research/review/corpus/string-revision-labels-2026-10-15.json; sample seeds 20261015, 20261016, 20261017 for R1-R3).
Round 3 is the final S1'/S2' held in tools/search_sources.py (S1P_PARTS, S2P_PARTS).
"""
from __future__ import annotations

import collections
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_sources as ss  # noqa: E402

ROOT, CORPUS = ss.ROOT, ss.CORPUS
OR, AND, NOT = ss._OR, ss._AND, ss._NOT

# ---------------------------------------------------------------- round specifications
BIO, VIS = ss.P_BIO, ss.P_VIS
CTX = ss.P_CTX
A1_LIST = ["diffusion language model*", "language diffusion model*", "diffusion llm*", "diffusion lm*", "dllm*",
           "diffusion-based language model*", "diffusion-based llm*", "diffusion large language model*",
           "diffusion-based large language model*", "text diffusion", "block diffusion", "absorbing diffusion"]
R1_S1 = OR(*A1_LIST, "discrete diffusion", "masked diffusion", "discrete flow*", "discrete state-space*",
           AND("absorbing state", OR("language", "text", "token*")), AND("any-order", OR("language", "text", "token*")),
           AND("non-autoregressive", "diffusion"),
           AND("diffusion", OR("text generation", "language generation", "natural language", "language model*", "llm*",
                               "sequence-to-sequence", "seq2seq", "discrete sequence*", "speculative decoding")))
R1_S2 = OR(AND(OR("unified multimodal", "unified understanding and generation", "understanding and generation", "any-to-any",
                  "unified model*", "omni*"),
               OR("diffusion", "masked generative", "discrete flow*", "flow matching", "rectified flow"),
               OR("multimodal", "vision-language", "text-to-image", "image generation", "mllm*")),
           AND(OR("vision-language-action", "vla*"), OR("diffusion", "masked generative", "discrete flow*", "flow matching")))
DD = OR("discrete diffusion", "masked diffusion", "discrete flow*", "discrete state-space*")
R2_CTX3 = OR("language", "text", "token*", "language model*", "llm*", "vocabulary", "autoregressive", "reasoning", "code",
             "sequence*", "categorical")
R2_B = AND("diffusion", OR("text generation", "language generation", "natural language", "sequence-to-sequence", "seq2seq",
                           "discrete sequence*", "speculative decoding", "categorical data", "discrete data", "paraphras*",
                           "textual diffusion", "text modeling", "named entity", "sentiment", "summarization", "dialog*",
                           "dialogue", "machine translation", "text style", "commonsense", "topic model*", "triple extraction",
                           "information extraction"), NOT(BIO))
R2_S1 = OR(OR(*A1_LIST, "diffusion mllm*", "diffusion vlm*", "diffusion vision-language model*", "dmllm*", "dvlm*"),
           AND(DD, OR(R2_CTX3, AND(NOT(BIO), NOT(VIS)))),
           OR(AND("absorbing state", CTX), AND("any-order", CTX), "non-autoregressive language model*",
              AND("non-autoregressive", "diffusion", NOT(BIO))),
           R2_B, ss.S1P_PARTS["C"])
R2_S2 = ss.P_SPECS["S2'"]
ROUNDS = {"R1": (R1_S1, R1_S2), "R2": (R2_S1, R2_S2), "R3": (ss.P_SPECS["S1'"], ss.P_SPECS["S2'"])}

SAMPLED_BEFORE_TOKEN_FIX = {"R3": ["N01342"]}

# seeds the revised strings are not meant to capture (outside I1/X1 after D0020) and why
OUT_OF_SCOPE = {
    "2209.03003": "image generative-model foundation (rectified flow); no text (X1)",
    "2011.13456": "image generative-model foundation (score-based SDE); no text (X1)",
    "2010.02502": "image generative-model foundation (DDIM); no text (X1)",
    "2006.11239": "image generative-model foundation (DDPM); no text (X1)",
    "1907.05600": "image generative-model foundation (score matching); no text (X1)",
    "1503.03585": "image generative-model foundation (non-equilibrium thermodynamics); no text (X1)",
    "2402.04997": "discrete flows for protein co-design; biochemical exclusion (abstract mentions protein)",
    "2305.20009": "protein design with discrete diffusion; biochemical exclusion (X1)",
    "2406.01572": "guidance for discrete state-space models, natural-science applications; biochemical exclusion",
    "2604.24089": "molecular generation and captioning; biochemical exclusion (X1)",
    "2509.06040": "reinforcement-learning for image and video diffusion; no text (X1)",
    "2604.02028": "Gaussian diffusion on discrete data (toy model); abstract mentions protein, so the biochemical exclusion drops it",
    "2402.19009": "generalised diffusion with latent encoder-decoder; abstract mentions protein and image, dropped by both exclusions",
    "2506.21557": "multimodal fake-news detection with diffusion-generated images; visual exclusion",
    "2208.00638": "latent-space text control with ODEs; the abstract has no diffusion or flow term, no string reaches it",
}


OUT_KIND = {"2604.02028": "dropped by an exclusion, arguably in scope", "2402.19009": "dropped by an exclusion, arguably in scope",
            "2208.00638": "no diffusion or flow term in title or abstract"}


NAME = "name variant (dLLM, diffusion-based LLM, large language diffusion model, language diffusion)"
CTXC = "context clause (discrete or masked diffusion, no language word)"
CONT = "continuous or latent diffusion language model"
DRAFT = "diffusion drafter for speculative decoding"
NLP = "NLP task or text generation with a diffusion model"
OTHER = "other vocabulary (any-order, non-autoregressive language models; no diffusion term)"
VLA = "vision-language-action"
OUTIMG = "out of scope: image, video or foundation model without text (X1)"
OUTBIO = "out of scope: protein or molecule (X1)"
DROPPED = "dropped by an exclusion, arguably in scope"
NODIFF = "no diffusion or flow term in title or abstract"
CATEGORY = {}
for cat, ids in ((NAME, "2502.09992 2607.05722 2507.19227 2602.23792 2510.11052 2509.23094 2507.19081 2306.02531 2305.19512 2507.12469"),
                 (CTXC, "2608.10615 2603.21342 2509.13866 2512.21336"),
                 (CONT, "2605.14531 2605.11577 2604.24416 2510.04573 2307.13949 2302.10025 2211.15089 2206.05895 2305.15025"),
                 (DRAFT, "2608.13524 2608.05448 2607.25852 2606.31315 2606.02091 2606.01813 2604.12989"),
                 (OTHER, "2310.09930 2512.17065"), (VLA, "2511.01718"),
                 (NLP, "2303.07576 2304.12519 2305.04465 2501.00862 2410.22971 2409.13739 2404.10763 2404.08938 2404.06760 2402.17011 "
                       "2403.00808 2402.15289 2402.10699 2401.03514 2310.15587 2310.15296 2308.15459 2306.08456 2306.08505 2305.13298 2305.01735"),
                 (OUTIMG, "2209.03003 2011.13456 2010.02502 2006.11239 1907.05600 1503.03585 2509.06040 2506.21557"),
                 (OUTBIO, "2402.04997 2305.20009 2406.01572 2604.24089 2310.10605"),
                 (DROPPED, "2604.02028 2402.19009"), (NODIFF, "2208.00638")):
    for i in ids.split():
        CATEGORY[i] = cat


# ---------------------------------------------------------------- fast evaluation of nested specs on many documents
class Index:
    def __init__(self, docs: dict[str, list[str]]):
        self.docs, self.inv, self.cache = docs, collections.defaultdict(set), {}
        for k, t in docs.items():
            for w in set(t):
                self.inv[w].add(k)
        self.vocab = list(self.inv)
        self.all = set(docs)

    def term(self, p):
        if p in self.cache:
            return self.cache[p]
        w = ss.words(p)

        def cand(x):
            if x.endswith("*"):
                r = set()
                for v in self.vocab:
                    if v.startswith(x[:-1]):
                        r |= self.inv[v]
                return r
            return self.inv.get(x, set())

        c = set(cand(w[0]))
        for x in w[1:]:
            c &= cand(x)
        self.cache[p] = {k for k in c if ss.phrase_in(self.docs[k], p)}
        return self.cache[p]

    def ev(self, spec):
        if isinstance(spec, str):
            return self.term(spec)
        op, items = spec
        if op == "OR":
            return set().union(*(self.ev(i) for i in items))
        if op == "AND":
            r = None
            for i in items:
                e = self.ev(i)
                r = e if r is None else r & e
            return r
        return self.all - set().union(*(self.ev(i) for i in items))


def toks(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def load_seeds():
    venues = json.load(open(CORPUS / "venues-semantic-scholar.json"))["records"]
    out = []
    for line in open(CORPUS / "awesome-dlms@194aa6bd.jsonl", encoding="utf8"):
        a = json.loads(line)
        c = a["canonical_id"]
        if not c.startswith("arXiv:"):
            continue
        ax = a.get("arxiv") or {}
        out.append({"arxiv": re.sub(r"v\d+$", "", c[6:]), "title": ax.get("title") or a["title"], "abstract": ax.get("abstract") or "",
                    "mm": "Multimodal DLMs" in a["sections"], "sections": a["sections"]})
    return out


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def v1_retrieved():
    """arXiv IDs and normalised titles retrieved by the original strings from every source (as pilot-recall ALL-COMBINED)."""
    import merge_new_records as m
    rows = [json.loads(l) for l in open(ss.LOG, encoding="utf8") if l.strip()]
    mine = [r for r in rows if r["executed_utc"].startswith("20261015") and r["export"].startswith("research/sources/search-raw/")
            and "'" not in r["string"] and "snowball" not in r["string"]]
    latest_oa = {}
    for r in mine:
        if r["database"].startswith("OpenAlex"):
            latest_oa[r["string"]] = r["export"]
    A, T = set(), set()
    for r in mine:
        p = ROOT / r["export"]
        db, name = r["database"], r["string"]
        if not p.exists():
            continue
        if db.startswith("OpenAlex"):
            if latest_oa[name] != r["export"]:
                continue
            rs = m.parse_oa(p, name, "openalex")
        elif db.startswith("Semantic Scholar Graph API (paper/search/bulk)"):
            rs = m.parse_s2(p, name, "s2")
        elif db.startswith("arXiv"):
            rs = m.parse_arxiv(p, name, "arx")
        elif db.startswith("ACL"):
            rs = m.parse_acl(p, name, "acl")
        elif db.startswith("OpenReview"):
            rs = m.parse_orv(p, name, "orv", collections.Counter())
        else:
            continue
        for x in rs:
            if x["arxiv"]:
                A.add(x["arxiv"])
            T.add(norm_title(x["title"]))
    for f in CORPUS.glob("arxiv-S*-*.jsonl"):
        for l in open(f, encoding="utf8"):
            r = json.loads(l)
            A.add(re.sub(r"v\d+$", "", r["arxiv"]))
            T.add(norm_title(r["title"]))
    return A, T


def main():
    seeds = load_seeds()
    mm = [s for s in seeds if s["mm"]]
    others = sorted((s for s in seeds if not s["mm"]), key=lambda s: s["arxiv"])
    r50 = random.Random(20261015).sample(others, 50)
    v1 = [json.loads(l) for l in open(CORPUS / "new-records-2026-10-15.jsonl", encoding="utf8")]
    docs = {f"P:{r['nid']}": toks(r["title"] + " " + r["abstract"]) for r in v1}
    for i, s in enumerate(seeds):
        docs[f"S:{i}"] = toks(s["title"] + " " + s["abstract"])
    ix = Index(docs)
    sid = lambda grp: {f"S:{i}" for i, s in enumerate(seeds) if any(s is g for g in grp)}
    groups = {"all540_entries": {f"S:{i}" for i in range(len(seeds))}, "MM28": sid(mm), "R50": sid(r50)}
    old_match = {f"P:{r['nid']}" for r in v1 if ss.matches("S1", r["title"] + " " + r["abstract"]) or ss.matches("S2", r["title"] + " " + r["abstract"])}
    old_seed = {f"S:{i}" for i, s in enumerate(seeds) if ss.matches("S1", s["title"] + " " + s["abstract"]) or ss.matches("S2", s["title"] + " " + s["abstract"])}
    labels = json.load(open(CORPUS / "string-revision-labels-2026-10-15.json", encoding="utf8"))["rounds"]
    res = {"date": "2026-10-15", "decision": "D0026",
           "seed_list": "Awesome-DLMs@194aa6bd, 540 entries with an arXiv ID (539 distinct IDs; 2506.17298 is listed twice)",
           "matching": "title + abstract of the arXiv record, word-based, case-insensitive, trailing * = word prefix (tools/search_sources.py matches())",
           "original": {g: len(old_seed & s) for g, s in groups.items()}, "rounds": {}}
    for name, (s1, s2) in ROUNDS.items():
        m1, m2 = ix.ev(s1), ix.ev(s2)
        rr = {"recall": {g: len((m1 | m2) & s) for g, s in groups.items()},
              "recall_S1prime_only": {g: len(m1 & s) for g, s in groups.items()},
              "recall_S2prime_only": {g: len(m2 & s) for g, s in groups.items()}}
        added = sorted(k[2:] for k in (m1 | m2) if k.startswith("P:") and k not in old_match)
        rr["records_added_over_S1_S2_in_v1_pool"] = len(added)
        rr["v1_pool_records"] = len(v1)
        # R3 was sampled before dllm*, dmllm*, dvlm*, vla*, mllm* were written as exact tokens (DLLME, 'dispersive liquid-liquid
        # microextraction', matched dllm*); that change drops N01342 from the population and is not in the sample
        pop = sorted(set(added) | set(SAMPLED_BEFORE_TOKEN_FIX.get(name, [])))
        samp = random.Random(labels[name]["sample_seed"]).sample(pop, min(200, len(pop)))
        rr["sample"] = {"seed": labels[name]["sample_seed"], "n": len(samp), "reproduced": samp == labels[name]["sample_ids"]}
        c = collections.Counter(labels[name]["labels"][k] for k in samp if k in labels[name]["labels"])
        rr["sample"]["labels"] = dict(c)
        rr["sample"]["share_in"] = round(c["IN"] / len(samp), 3)
        rr["sample"]["share_in_or_unclear"] = round((c["IN"] + c["U"]) / len(samp), 3)
        rr["missed_seed_entries"] = [s["arxiv"] for i, s in enumerate(seeds) if f"S:{i}" not in (m1 | m2)]
        res["rounds"][name] = rr
    # ---- the seeds the v1 searches (S1, S2; every source; earlier logged arXiv runs included) did not retrieve
    A, T = v1_retrieved()
    miss = []
    seen = set()
    for s in seeds:
        if s["arxiv"] in A or norm_title(s["title"]) in T or s["arxiv"] in seen:
            continue
        seen.add(s["arxiv"])
        text = s["title"] + " " + s["abstract"]
        t = toks(text)
        c1 = [p for p in ss.S1_PHRASES if ss.phrase_in(t, p)]
        nar = ss.phrase_in(t, "non-autoregressive") and ss.phrase_in(t, "diffusion")
        c2 = [p for p in ss.S1_AND if ss.phrase_in(t, p)]
        s2g = [[p for p in g if ss.phrase_in(t, p)] for g in (ss.S2_A, ss.S2_B, ss.S2_C)]
        why = []
        if not c1 and not nar:
            why.append("S1: none of its phrases")
        elif not c2:
            why.append("S1: phrase '" + c1[0] + "' but no language word" if c1 else "S1: no language word")
        if not s2g[0]:
            why.append("S2: no group-A phrase")
        elif not all(s2g):
            why.append("S2: a group missing")
        p1, p2 = ss.part_of("S1'", text), ss.part_of("S2'", text)
        cat = CATEGORY[s["arxiv"]]
        note = OUT_OF_SCOPE.get(s["arxiv"]) or ("S1'/S2' part(s) " + "/".join(p1 + p2) if (p1 or p2) else "")
        miss.append({"arxiv": s["arxiv"], "title": s["title"], "sections": s["sections"], "fails_S1_S2_because": why,
                     "captured_by_S1prime_parts": p1, "captured_by_S2prime_parts": p2, "captured": bool(p1 or p2),
                     "category": cat, "note": note})
    res["missed_by_v1_searches"] = {"n": len(miss), "n_captured_by_revised": sum(m["captured"] for m in miss),
                                    "by_category": dict(collections.Counter(m["category"] for m in miss)), "seeds": miss}
    res["note_rounds"] = ("R1 broad (no exclusions), R2 adds biochemical and visual exclusions and NLP-task terms, R3 (final) narrows "
                          "the context clause of the discrete-diffusion branch, drops 'natural language' alone from B; see report")
    # by-tier precision of the final round
    final = labels["R3"]
    tiers = collections.defaultdict(collections.Counter)
    pool_text = {r["nid"]: r["title"] + " " + r["abstract"] for r in v1}
    for k in final["sample_ids"]:
        for p in ss.part_of("S1'", pool_text[k]) + ["S2':" + x for x in ss.part_of("S2'", pool_text[k])]:
            tiers[p][final["labels"][k]] += 1
    res["final_round_sample_by_part"] = {p: dict(c) for p, c in sorted(tiers.items())}
    res["S1prime_plain"] = ss.render_spec(ss.P_SPECS["S1'"], "plain")
    res["S2prime_plain"] = ss.render_spec(ss.P_SPECS["S2'"], "plain")
    res["parts"] = {n: {k: ss.render_part(n, k, "plain") for k in p} for n, p in ss.P_PARTS.items()}
    out = CORPUS / "string-revision-2026-10-15.json"
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf8")
    print(json.dumps({k: res[k] for k in ("original", "rounds")}, indent=1)[:4000])


if __name__ == "__main__":
    main()
