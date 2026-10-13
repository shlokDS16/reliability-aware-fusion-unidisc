"""Compute the slack share for the H2 pilot exactly as frozen in research/review/pilot-rules.md.

    python tools/h2_pilot.py

Reads research/review/pilot/h2-papers.jsonl and h2-units.jsonl, writes h2-results.jsonl and
prints the pilot summary. No number is entered by hand.
"""
from __future__ import annotations

import json
import math
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

PILOT = Path(__file__).resolve().parent.parent / "research" / "review" / "pilot"


def load(name: str) -> list[dict]:
    p = PILOT / name
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def num(x) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def first_crossing(sweep: list[tuple[float, float]], target: float, envelope: bool) -> tuple[float | None, str]:
    """Smallest T at which baseline quality (higher is better) reaches target; log-T interpolation."""
    if envelope:  # running maximum from the low-T side
        best, env = -math.inf, []
        for t, q in sweep:
            best = max(best, q)
            env.append((t, best))
        sweep = env
    if sweep[0][1] >= target:
        return sweep[0][0], "at-lowest"
    for (t0, q0), (t1, q1) in zip(sweep, sweep[1:]):
        if q0 < target <= q1:
            frac = (target - q0) / (q1 - q0)
            return math.exp(math.log(t0) + frac * (math.log(t1) - math.log(t0))), "interpolated"
    return None, "never"


def slack(u: dict, envelope: bool = False) -> dict:
    if u.get("cost_unit") not in ("NFE", "steps"):  # rules: wall-clock and rate units are a separate stratum
        return {"flag": "wall-clock", "sigma": None}
    tm, qm = num(u.get("method_T")), num(u.get("method_Q"))
    th = num(u.get("baseline_headline_T"))
    sweep = sorted((float(t), float(q)) for t, q in (u.get("baseline_sweep") or [])
                   if num(t) is not None and num(q) is not None and float(t) > 0)
    if tm is None or qm is None or th is None or tm <= 0:
        return {"flag": "incomplete", "sigma": None}
    s_head = th / tm
    if s_head <= 1:
        return {"flag": "no-headline-gain", "sigma": None, "s_head": s_head}
    if len(sweep) < 3:
        return {"flag": "no-sweep", "sigma": None, "s_head": s_head}
    hib = u.get("higher_is_better")
    sign = 1.0 if hib in (True, None) else -1.0
    sd = num(u.get("method_sd"))
    scale100 = max(abs(qm), max(abs(q) for _, q in sweep)) > 1.0
    eps = sd if sd else (0.5 if scale100 and sign > 0 else 0.01 * abs(qm))
    target = sign * qm - eps
    t_star, how = first_crossing([(t, sign * q) for t, q in sweep], target, envelope)
    if how == "never":
        return {"flag": "dominates", "sigma": 0.0, "s_head": s_head}
    if t_star <= tm:
        return {"flag": "baseline-sufficient", "sigma": 1.0, "s_head": s_head, "t_star": t_star}
    sigma = min(1.0, max(0.0, 1 - math.log(t_star / tm) / math.log(s_head)))
    flag = "censored" if how == "at-lowest" else "computed"
    return {"flag": flag, "sigma": sigma, "s_head": s_head, "t_star": t_star}


def main() -> None:
    papers, units = load("h2-papers.jsonl"), load("h2-units.jsonl")
    out, per_paper, per_paper_env = [], defaultdict(list), defaultdict(list)
    for u in units:
        r, e = slack(u), slack(u, envelope=True)
        copied = u.get("baseline_source") == "copied"
        out.append({k: u.get(k) for k in ("record_id", "arxiv", "block", "task", "model", "gen_length", "metric",
                                           "method_name", "baseline_name", "cost_unit", "baseline_source")}
                   | r | {"sigma_envelope": e["sigma"]})
        if r["sigma"] is not None and not copied:
            per_paper[u["record_id"]].append(r["sigma"])
            per_paper_env[u["record_id"]].append(e["sigma"])
    (PILOT / "h2-results.jsonl").write_text("\n".join(json.dumps(x) for x in out) + "\n", encoding="utf-8")

    fp = [p for p in papers if p.get("speedup_kind") in ("forward-passes", "both")]
    # claim (a) as frozen: a baseline sweep of 3+ levels, in forward passes or steps, reaching 2*T_m or fewer
    reach = set()
    for u in units:
        tm = num(u.get("method_T"))
        sw = [float(t) for t, q in (u.get("baseline_sweep") or []) if num(t) is not None and num(q) is not None]
        if u.get("cost_unit") in ("NFE", "steps") and tm and len(sw) >= 3 and min(sw) <= 2 * tm:
            reach.add(u["record_id"])
    swept = [p for p in fp if p["record_id"] in reach]
    print(f"papers: {len(papers)}  by speed-up kind: {dict(Counter(p.get('speedup_kind') for p in papers))}")
    print(f"claim (a): forward-pass speed-up papers {len(fp)}; with a baseline step sweep of 3+ levels reaching 2*T_m: "
          f"{len(swept)} {sorted(p['record_id'] for p in swept)}; agent's looser flag: {sum(1 for p in fp if p.get('baseline_swept'))}")
    print(f"units: {len(units)}  flags: {dict(Counter(x['flag'] for x in out))}")
    med = {k: st.median(v) for k, v in per_paper.items()}
    for k in sorted(med):
        print(f"  {k}: units {len(per_paper[k])}  paper-level sigma {med[k]:.2f}  (envelope {st.median(per_paper_env[k]):.2f})")
    if med:
        print(f"claim (b): papers with a computable sigma {len(med)}; median of paper-level sigma "
              f"{st.median(med.values()):.2f}; envelope variant {st.median(st.median(v) for v in per_paper_env.values()):.2f}")
    else:
        print("claim (b): no unit is computable")
    by_len = defaultdict(list)
    for x in out:
        if x["sigma"] is not None and x.get("gen_length"):
            by_len[(x["record_id"], x["task"], x["model"])].append((float(x["gen_length"]), x["sigma"]))
    multi = {k: sorted(v) for k, v in by_len.items() if len({a for a, _ in v}) > 1}
    print(f"claim (c): series with more than one generation length: {len(multi)}")
    for k, v in multi.items():
        print(f"  {k}: {[(int(a), round(b, 2)) for a, b in v]}")


if __name__ == "__main__":
    main()
