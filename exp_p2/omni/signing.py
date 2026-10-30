"""Machine-checkable part of the gate-auditor's sign-off conditions for the Omni adapter (code audit part 3, section 5; lead decisions T1-T3 of 2026-10-28 PM). Pure json: no torch, no model.

    python -m exp_p2.omni.signing --run-id P2-OMNI-TIMING [--force]       # -> runs/P2-OMNI-TIMING/signing_check.json (write-once); exit 0 if every condition holds, 3 otherwise

This is NOT the signature. `adapter_signature.json` is written by the gate-auditor only (AB.5 item 1, A3b.4). This module reads `selfcheck.json`, `omni_env.json`, `items.jsonl` and `chunks.jsonl` of the
timing run and reports, condition by condition, whether:
  S-1  the self-check holds exactly A1..A7 once each, all ok, adapter.all_ok, ids_equal;
  S-3  (T1) the A5 floors: mean_logp(s=1) >= -8.011 (uniform over 8,192 codes is -9.011) and top-1(s=1) >= 0.005 -- a separate check on top of checks.py, which stays unchanged (its hash is recorded in SAP A3b.4);
  S-4  (T2) pins, versions and memory settings of omni_env.json: pins_match all true, the four skip modules, transformers 4.51.3, bitsandbytes 0.50.2, mem_frac 0.62;
  S-6  (T3) the load plus self-check peak allocation <= 7,000 MiB and every timing row peak_alloc_mib <= 7,000 and finite;
  S-7  allocated_after_load_mib within 5,000-7,000 (sanity band for a partial or missing quantisation, not a GO rule);
  S-8  no guard_stop, item_error, hold_stop or earlier failed self-check event in chunks.jsonl; plus the realised 4-bit module count (audit m-4) matches the plan.
S-2 (the per-check numbers of the table) and S-5 (the load notices in the first chunk's log) are read by the auditor by hand."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_CHECKS = tuple(f"A{i}" for i in range(1, 8))
T1_MEAN_LOGP_FLOOR = -8.011        # lead decision T1: the uniform distribution over 8,192 codes gives -9.011; a model that is not clearly better than uniform at the correct shift must not pass
T1_TOP1_FLOOR = 0.005
PEAK_LIMIT_MIB = 7000.0            # lead decision T3 (same figure as the per-item rule)
LOAD_BAND_MIB = (5000.0, 7000.0)
T2_VERSIONS = dict(transformers="4.51.3", bitsandbytes="0.50.2")
T2_SKIP_MODULES = ("audio_model", "audio_projection", "lm_head", "embed_tokens")
T2_MEM_FRAC = 0.62
BAD_EVENTS = ("guard_stop", "item_error", "hold_stop", "selfcheck_failed_earlier")


def _cond(ok, **kw) -> dict:
    return dict(ok=bool(ok), **kw)


def _a5(selfcheck: dict | None) -> dict | None:
    for r in ((selfcheck or {}).get("adapter") or {}).get("results") or []:
        if r.get("id") == "A5":
            return r
    return None


def t1_check(selfcheck: dict | None) -> dict:
    """T1: the A5 result must exist, be ok, and its shift-1 numbers must clear the floors (all three shifts are reported)."""
    a5 = _a5(selfcheck)
    ps = ((a5 or {}).get("detail") or {}).get("per_shift") or {}
    s1 = ps.get("1") or {}
    mlp, t1 = s1.get("mean_logp"), s1.get("top1")
    ok = bool(a5 and a5.get("ok") and mlp is not None and t1 is not None and mlp >= T1_MEAN_LOGP_FLOOR and t1 >= T1_TOP1_FLOOR)
    return _cond(ok, a5_present=a5 is not None, a5_ok=bool(a5 and a5.get("ok")), mean_logp_s1=mlp, top1_s1=t1, floors=dict(mean_logp=T1_MEAN_LOGP_FLOOR, top1=T1_TOP1_FLOOR), per_shift=ps,
                 margin_observed=((a5 or {}).get("detail") or {}).get("margin_observed"))


def checks_present(selfcheck: dict | None) -> dict:
    ad = (selfcheck or {}).get("adapter") or {}
    res = ad.get("results")
    ids = sorted(r.get("id") for r in res or [])
    ok = bool(selfcheck and selfcheck.get("ids_equal") and ad.get("all_ok") and res is not None and ids == sorted(REQUIRED_CHECKS) and all(r.get("ok") for r in res))
    return _cond(ok, ids=ids, missing=[c for c in REQUIRED_CHECKS if c not in ids], ids_equal=(selfcheck or {}).get("ids_equal"), failed=ad.get("failed"))


def t2_check(env: dict | None) -> dict:
    env = env or {}
    pins = env.get("pins_match") or {}
    ver = env.get("versions") or {}
    ok_pins = bool(pins) and all(v is True for v in pins.values())
    ok_ver = all(ver.get(k) == v for k, v in T2_VERSIONS.items())
    ok_skip = tuple(env.get("skip_modules") or ()) == T2_SKIP_MODULES
    ok_mem = env.get("mem_frac") == T2_MEM_FRAC and env.get("guard_cap_mib") is not None
    return _cond(ok_pins and ok_ver and ok_skip and ok_mem, pins_match=pins, versions={k: ver.get(k) for k in T2_VERSIONS}, expected_versions=T2_VERSIONS, skip_modules=env.get("skip_modules"),
                 mem_frac=env.get("mem_frac"), guard_cap_mib=env.get("guard_cap_mib"))


def t3_check(selfcheck: dict | None, rows: list[dict]) -> dict:
    pk = (selfcheck or {}).get("peak_alloc_mib_during_checks")
    pg = (selfcheck or {}).get("peak_gate") or {}
    timed = [r for r in rows if "fwd_s" in r]
    peaks = [r.get("peak_alloc_mib") for r in timed]
    rows_ok = bool(timed) and all(p is not None and p <= PEAK_LIMIT_MIB for p in peaks) and all(r.get("finite", True) for r in timed)
    return _cond(pk is not None and pk <= PEAK_LIMIT_MIB and pg.get("ok", True) and rows_ok, peak_alloc_mib_during_checks=pk, limit_mib=PEAK_LIMIT_MIB, max_row_peak_alloc_mib=max([p for p in peaks if p is not None], default=None),
                 n_timed_rows=len(timed), selfcheck_peak_gate=pg or None)


def quantisation_check(selfcheck: dict | None) -> dict:
    q = (selfcheck or {}).get("quantisation") or {}
    return _cond(q.get("matches") is True, **{k: q.get(k) for k in ("n_linear4bit", "expected_linear4bit", "n_plain_linear")})


def signing_check(selfcheck: dict | None, env: dict | None, rows: list[dict], events: list[dict]) -> dict:
    alloc = (env or {}).get("allocated_after_load_mib")
    bad = [e for e in events if e.get("event") in BAD_EVENTS]
    conds = {"S-1": checks_present(selfcheck), "S-3_T1": t1_check(selfcheck), "S-4_T2": t2_check(env), "S-6_T3": t3_check(selfcheck, rows),
             "S-7": _cond(alloc is not None and LOAD_BAND_MIB[0] <= alloc <= LOAD_BAND_MIB[1], allocated_after_load_mib=alloc, band_mib=list(LOAD_BAND_MIB)),
             "S-8": _cond(not bad, bad_events=bad[:3]), "m-4_quantisation": quantisation_check(selfcheck)}
    return dict(all_ok=all(c["ok"] for c in conds.values()), conditions=conds,
                not_checked_here="S-2 (the per-check numbers of the table) and S-5 (the load notices in stdout-chunk00.log) are read by the gate-auditor by hand; this file is not the signature",
                note="adapter_signature.json is written by the gate-auditor only (AB.5 item 1); T1-T3 are the lead's tightenings of 2026-10-28 PM (checks.py and its hash unchanged)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run-id", default="P2-OMNI-TIMING")
    ap.add_argument("--runs-dir", default=None)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    from exp_p2 import common
    from exp_p2.gate import artifacts
    d = Path(a.runs_dir or common.RUNS) / a.run_id

    def load(name):
        p = d / name
        return json.loads(p.read_text(encoding="utf8")) if p.exists() else None
    res = signing_check(load("selfcheck.json"), load("omni_env.json"), common.read_jsonl(d / "items.jsonl") if (d / "items.jsonl").exists() else [],
                        common.read_jsonl(d / "chunks.jsonl") if (d / "chunks.jsonl").exists() else [])
    artifacts.write_once(d / "signing_check.json", json.dumps(res, indent=1, default=str), a.force)
    print(json.dumps(dict(all_ok=res["all_ok"], failed=[k for k, c in res["conditions"].items() if not c["ok"]]), indent=1))
    return 0 if res["all_ok"] else 3


if __name__ == "__main__":
    sys.exit(main())
