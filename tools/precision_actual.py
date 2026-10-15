"""Second precision estimate (D0026): what the revised searches actually returned, by screening tier.

    python tools/precision_actual.py sample    # stratified random sample of the screening queue, 40 per tier (seed 20261018)
    python tools/precision_actual.py report    # reads the title labels, writes precision-actual-2026-10-15.json
    python tools/precision_actual.py sample r4 # same design on the final queue (records passing S1''/S2'', D0027), seed 20261019
    python tools/precision_actual.py report r4 # reads precision-round4-labels-2026-10-15.json, writes precision-round4-2026-10-15.json

The first estimate (tools/string_rounds.py) used the pool of records already collected, which is made of citation neighbours of the
seed papers and therefore looks like the topic. This one uses the screening queue, i.e. what the databases returned for S1, S2, S1', S2'.
Labels: IN looks in scope from the title (diffusion, masked-generative or discrete-flow model of text; diffusion language model
method, analysis, benchmark or survey; speculative decoding with a diffusion drafter; unified multimodal model with such a component),
U unclear from the title, O other. Labelled by the agent that proposed the strings, from titles only: a proxy for ordering the
screening, not a screening decision.
"""
from __future__ import annotations

import collections
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import search_sources as ss  # noqa: E402

C = ss.CORPUS
ISO = "2026-10-15"
R4 = "r4" in sys.argv[2:]
SEED, PER_TIER = (20261019 if R4 else 20261018), 40
if R4:                      # round 4 (D0027): the same design on the queue of records that pass S1'' / S2''
    QUEUE = C / f"screening-queue-final-{ISO}.jsonl"
    SAMPLE = C / f"precision-round4-sample-{ISO}.json"
    LABELS = C / f"precision-round4-labels-{ISO}.json"
    OUT = C / f"precision-round4-{ISO}.json"
else:
    QUEUE = C / f"screening-queue-{ISO}.jsonl"
    SAMPLE = C / f"precision-actual-sample-{ISO}.json"
    LABELS = C / f"precision-actual-labels-{ISO}.json"
    OUT = C / f"precision-actual-{ISO}.json"


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(max(0, c - h), 3), round(min(1, c + h), 3))


def main(cmd):
    queue = [json.loads(l) for l in open(QUEUE, encoding="utf8") if l.strip()]
    by_tier = {}
    for r in queue:
        by_tier.setdefault(r["queue_tier"], []).append(r["id"])
    if cmd == "sample":
        rnd = random.Random(SEED)
        smp = {str(t): rnd.sample(sorted(ids), min(PER_TIER, len(ids))) for t, ids in sorted(by_tier.items())}
        SAMPLE.write_text(json.dumps({"seed": SEED, "per_tier": PER_TIER, "tier_sizes": {str(t): len(i) for t, i in sorted(by_tier.items())},
                                      "sample": smp}, indent=1), encoding="utf8")
        title = {r["id"]: r["title"] for r in queue}
        for t, ids in smp.items():
            print(f"== tier {t} ({len(by_tier[int(t)])} records)")
            for i, k in enumerate(ids):
                print(i, k, title[k].encode("ascii", "replace").decode()[:100])
        return
    smp = json.loads(SAMPLE.read_text(encoding="utf8"))
    lab = json.loads(LABELS.read_text(encoding="utf8"))
    res, tot = {}, sum(smp["tier_sizes"].values())
    est_in = est_inu = 0.0
    for t, ids in smp["sample"].items():
        c = {"IN": 0, "U": 0, "O": 0}
        for k in ids:
            c[lab[k]] += 1
        n = len(ids)
        size = smp["tier_sizes"][t]
        res[t] = {"records_in_tier": size, "sampled": n, **c, "share_in": round(c["IN"] / n, 3), "wilson95_in": wilson(c["IN"], n),
                  "share_in_or_unclear": round((c["IN"] + c["U"]) / n, 3), "estimated_in_records": round(size * c["IN"] / n),
                  "estimated_in_or_unclear_records": round(size * (c["IN"] + c["U"]) / n)}
        est_in += size * c["IN"] / n
        est_inu += size * (c["IN"] + c["U"]) / n
    res["queue_total"] = {"records": tot, "estimated_in": round(est_in), "estimated_share_in": round(est_in / tot, 3),
                          "estimated_in_or_unclear": round(est_inu), "estimated_share_in_or_unclear": round(est_inu / tot, 3)}
    what = "final screening queue (records passing S1'' and S2'', D0027)" if R4 else "screening queue"
    text = (f"Stratified random sample of the {what}: {PER_TIER} records per tier (seed {SEED}), labelled from the title as in 2.3 "
            f"(`{LABELS.name}`). Estimated number of in-scope-looking records in the queue of {tot:,}: {round(est_in):,} "
            f"({est_in / tot:.1%}); in scope or unclear: {round(est_inu):,} ({est_inu / tot:.1%}). Per tier:\n\n"
            "| Tier | Records | Sampled | IN | U | O | IN share (Wilson 95%) | Estimated IN records |\n|---|---|---|---|---|---|---|---|\n" +
            "\n".join(f"| T{t} | {v['records_in_tier']:,} | {v['sampled']} | {v['IN']} | {v['U']} | {v['O']} | {v['share_in']:.0%} "
                      f"({v['wilson95_in'][0]:.0%} to {v['wilson95_in'][1]:.0%}) | {v['estimated_in_records']:,} |"
                      for t, v in res.items() if t != "queue_total") +
            ("" if R4 else
             "\n\nThe local pool of 2.3 overstates precision because it is made of citation neighbours of the seeds; databases return papers from "
             "every field that use the words, e.g. diffusion of innovations, diffusion-weighted imaging, discrete diffusion equations, "
             "'dispersive liquid-liquid microextraction' (DLLME, until `dllm*` was written as the exact tokens `dllm` and `dllms`), "
             "'discrete flow' in fluid mechanics. Tier T3 (broad branches B and C) and T5 (returned by a database, not matching any string "
             "locally) carry most of the noise."))
    OUT.write_text(json.dumps({"seed": SEED, "tiers": res, "text": text}, indent=1), encoding="utf8")
    print(text)


# ---------------------------------------------------------------- what the round-4 filter removed (D0027), title labels by the proposing agent
LOST_SEED = 20261022
LOST_PER_TIER = {1: 30, 2: 10, 3: 40, 4: 20}
AUTO = C / f"auto-excluded-{ISO}.jsonl"
VALID_META = C / f"validation-autoexcl-sampling-{ISO}.json"
LOST_SAMPLE = C / f"lost-check-sample-{ISO}.json"
LOST_LABELS = C / f"lost-check-labels-{ISO}.json"
LOST_OUT = C / f"lost-check-{ISO}.json"


def lost(cmd):
    """Stratified random sample (by original tier T1 to T4) of the database records the filter removed, drawn from the records that are NOT
    in validation set V1, so that the validation set stays unseen. T5 (no string matches locally) was sampled in the second estimate
    (40 titles, none in scope)."""
    rows = [json.loads(l) for l in open(AUTO, encoding="utf8") if l.strip()]
    v1 = set(json.loads(VALID_META.read_text(encoding="utf8"))["V1"]["ids"])
    frame = {t: sorted(r["id"] for r in rows if r["queue_tier"] == t and not r["snowball_only"] and r["id"] not in v1) for t in LOST_PER_TIER}
    sizes = {t: sum(1 for r in rows if r["queue_tier"] == t and not r["snowball_only"]) for t in LOST_PER_TIER}
    if cmd == "lost-sample":
        rnd = random.Random(LOST_SEED)
        smp = {str(t): rnd.sample(ids, LOST_PER_TIER[t]) for t, ids in frame.items()}
        LOST_SAMPLE.write_text(json.dumps({"seed": LOST_SEED, "per_tier": LOST_PER_TIER, "records_removed_by_tier": sizes,
                                           "frame_without_V1": {str(t): len(i) for t, i in frame.items()}, "sample": smp}, indent=1), encoding="utf8")
        title = {r["id"]: r["title"] for r in rows}
        for t, ids in smp.items():
            print(f"== original tier T{t}: removed {sizes[int(t)]}")
            for i, k in enumerate(ids):
                print(i, k, title[k].encode("ascii", "replace").decode()[:100])
        return
    smp = json.loads(LOST_SAMPLE.read_text(encoding="utf8"))
    lab = json.loads(LOST_LABELS.read_text(encoding="utf8"))
    res, est_in, est_inu, tot = {}, 0.0, 0.0, 0
    for t, ids in smp["sample"].items():
        c = collections.Counter(lab[k] for k in ids)
        n, size = len(ids), smp["records_removed_by_tier"][t]
        res[f"T{t}"] = {"removed": size, "sampled": n, "IN": c["IN"], "U": c["U"], "O": c["O"], "wilson95_in": wilson(c["IN"], n),
                        "wilson95_in_or_unclear": wilson(c["IN"] + c["U"], n), "estimated_in_removed": round(size * c["IN"] / n, 1),
                        "estimated_in_or_unclear_removed": round(size * (c["IN"] + c["U"]) / n, 1)}
        est_in += size * c["IN"] / n
        est_inu += size * (c["IN"] + c["U"]) / n
        tot += size
    res["total_T1_to_T4"] = {"removed": tot, "estimated_in_removed": round(est_in, 1), "estimated_in_or_unclear_removed": round(est_inu, 1)}
    LOST_OUT.write_text(json.dumps({"seed": LOST_SEED, "tiers": res}, indent=1), encoding="utf8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].startswith("lost"):
        lost(sys.argv[1])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else "")
