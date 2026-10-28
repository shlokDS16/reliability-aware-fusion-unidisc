"""Shared plumbing of the two Omni runners (`run_omni_timing.py`, `run_gate_omni_r.py`): CLI flags, the pre-load GPU check, guards with a peak-allocation rule, the production loader,
the Omni token rule for items, the environment record. Nothing here loads a model at import time."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from exp_p2 import common
from exp_p2.gate import config, runner
from exp_p2.gate.guards import Guards
from exp_p2.gate.watchdog import EXIT_GUARD

# Proposed GPU settings (see the report, section "memory"). UNVERIFIED estimates: 4-bit weights about 3.67 GB + bf16 embedding, lm_head and audio projection 2.56 GB = about 6.2 GB.
PROPOSED = dict(mem_frac=0.62, max_used_first_mib=9500.0, max_used_mib=9000.0, max_rise_mib=1500.0, max_peak_alloc_mib=7000.0, max_used_before_load_mib=2500.0)


@dataclass
class OmniGuards(Guards):
    """Guards plus one rule that the generic stack does not have: the peak ALLOCATED memory of an item (the runner resets the peak statistics before each item) must stay under a ceiling.
    A breach is a guard stop (exit 76, never relaunched automatically): the 4-bit estimate was wrong and a person decides."""
    max_peak_alloc_mib: float = PROPOSED["max_peak_alloc_mib"]
    peak_fn: object = None

    def after_item(self, busy_s: float) -> str | None:
        why = super().after_item(busy_s)
        if why:
            return why
        if self.peak_fn is not None:
            pk = float(self.peak_fn())
            if pk > self.max_peak_alloc_mib:
                return f"peak_allocated {pk:.0f} MiB > {self.max_peak_alloc_mib:.0f}"
        return None


def cuda_peak_mib() -> float:
    import torch
    return torch.cuda.max_memory_allocated() / 2 ** 20


def add_omni_args(ap):
    ap.add_argument("--micro-bs", type=int, default=1, help="rows per forward (the gate code asks for batches of 4; the scorer splits them). 1 until the timing stage has measured memory")
    ap.add_argument("--magvit-device", default="cpu", choices=["cpu", "cuda"], help="MAGVIT-v2 encoder device; cpu saves about 0.4 GB of GPU memory (about 0.5 s per image)")
    ap.add_argument("--max-peak-alloc-mib", type=float, default=PROPOSED["max_peak_alloc_mib"], help="guard stop if an item's peak allocated GPU memory exceeds this")
    ap.add_argument("--max-used-before-load-mib", type=float, default=PROPOSED["max_used_before_load_mib"], help="refuse to load if whole-GPU memory in use (other processes) is above this")
    return ap


def omni_parser(default_run_id: str, default_n: int | None):
    ap = runner.base_parser(default_run_id, default_n)
    ap.set_defaults(mem_frac=PROPOSED["mem_frac"], max_used_first_mib=PROPOSED["max_used_first_mib"], max_used_mib=PROPOSED["max_used_mib"], max_rise_mib=PROPOSED["max_rise_mib"])
    return add_omni_args(ap)


def omni_guards_from_args(a, peak_fn=None) -> OmniGuards:
    return OmniGuards(max_used_mib=a.max_used_mib, max_used_first_mib=a.max_used_first_mib, max_rise_mib=a.max_rise_mib, require_ac=not a.no_ac_check,
                      max_peak_alloc_mib=a.max_peak_alloc_mib, peak_fn=peak_fn if peak_fn is not None else cuda_peak_mib)


def preload_check(a, gpu_state_fn=None) -> int | None:
    """Whole-GPU memory in use before the model is touched (nvidia-smi, no CUDA context). Returns EXIT_GUARD to stop, None to go on. An unreadable sensor (the 99999 sentinel of
    `common.gpu_state`) stops too: fail closed."""
    st = (gpu_state_fn or common.gpu_state)()
    used = float(st.get("mem_used_mib", 99999.0))
    if used > a.max_used_before_load_mib:
        print(f"STOP: whole-GPU memory in use before the load is {used:.0f} MiB > {a.max_used_before_load_mib:.0f} MiB (other processes?); not loading", file=sys.stderr)
        return EXIT_GUARD
    return None


def production_loader(a, info: dict):
    """-> load() for runner.run_items. Fills `info` (paths, stub class, pre-load memory) for the environment record. GPU + omni venv only."""
    def load():
        from exp_p2.omni import loader
        from exp_p2.omni.scorer import OmniScorer
        t0 = time.time()
        loader.offline_env()
        repo = loader.ensure_import_paths()
        snap, mag = loader.snapshot(loader.OMNI_REPO_ID), loader.snapshot(loader.MAGVIT_REPO_ID)
        model, stub = loader.load_model(snap, device_index=0, quantize=True)
        tok = loader.load_tokenizer(snap)
        magvit = loader.load_magvit(mag, a.magvit_device)
        sc = OmniScorer(model, tok, magvit, micro_bs=a.micro_bs, magvit_device=a.magvit_device)
        info.update(repo=str(repo), snapshot=str(snap), magvit=str(mag), stub=stub, load_seconds=time.time() - t0)
        return runner.Counting(sc)
    return load


def git_head(path: Path) -> str | None:
    r = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() or None


def write_env(run: Path, sc, info: dict, a=None) -> dict:
    """omni_env.json: everything needed to judge a timing/memory result later. Written once per run directory; later chunks append an event instead."""
    from exp_p2.omni import loader
    path = Path(run) / "omni_env.json"
    env = dict(versions=loader.versions(), snapshot=info.get("snapshot"), magvit_snapshot=info.get("magvit"), omni_repo_head=git_head(Path(info["repo"])) if info.get("repo") else None,
               expected=dict(omni_sha=loader.EXPECTED_OMNI_SHA, snapshot=loader.EXPECTED_SNAPSHOT, magvit=loader.EXPECTED_MAGVIT),
               pins_match=dict(omni_sha=(git_head(Path(info["repo"])) == loader.EXPECTED_OMNI_SHA) if info.get("repo") else None,
                               snapshot=(Path(info["snapshot"]).name == loader.EXPECTED_SNAPSHOT) if info.get("snapshot") else None,
                               magvit=(Path(info["magvit"]).name == loader.EXPECTED_MAGVIT) if info.get("magvit") else None), skip_modules=list(loader.SKIP_MODULES),
               quantisation="bitsandbytes NF4, bf16 compute, no double quantisation", micro_bs=getattr(sc, "micro_bs", None), magvit_device=getattr(sc, "magvit_device", None),
               load_seconds=info.get("load_seconds"), args={k: v for k, v in vars(a).items()} if a is not None else None, pip_freeze_note="the run's env-lock.txt is empty in a uv venv (no pip); see .venv-omni/freeze-2026-10-27.txt")
    try:
        import torch
        if torch.cuda.is_available():
            props = torch.cuda.get_device_properties(0)
            total = props.total_memory / 2 ** 20
            env.update(device=props.name, device_total_mib=total, mem_frac=getattr(a, "mem_frac", None), guard_cap_mib=(total * a.mem_frac) if a is not None and a.mem_frac else None,
                       allocated_after_load_mib=torch.cuda.memory_allocated() / 2 ** 20, reserved_after_load_mib=torch.cuda.memory_reserved() / 2 ** 20, gpu_used_after_load_mib=common.gpu_state().get("mem_used_mib"))
    except Exception as e:                                                                   # noqa: BLE001
        env["cuda_note"] = repr(e)
    if path.exists():
        common.append_jsonl(Path(run) / "chunks.jsonl", dict(event="omni_env_chunk", t=time.time(), allocated_after_load_mib=env.get("allocated_after_load_mib"),
                                                             reserved_after_load_mib=env.get("reserved_after_load_mib"), gpu_used_after_load_mib=env.get("gpu_used_after_load_mib")))
        return json.loads(path.read_text(encoding="utf8"))
    path.write_text(json.dumps(env, indent=1, default=str), encoding="utf8")
    return env


# ------------------------------------------------------------------------------------------------ the Omni token rule (SAP AB.5 item 3: exclude, count by reason, never replace)
def omni_token_filter(sc, items: list[dict], *, need_neg: bool = True) -> tuple[list[dict], dict]:
    """An item is excluded when c+ (or c-, if need_neg) has an Omni runtime token count outside 5-32 or tokenises to a special token. Order of the survivors unchanged."""
    lo, hi = config.TOK_RANGE
    kept, excluded = [], {"too_short": [], "too_long": [], "special_token": []}
    counts = []
    for it in items:
        bad = None
        n_pos = n_neg = None
        for which, cap in (("c+", it["caption"]), ("c-", it.get("neg_caption") if need_neg else None)):
            if cap is None:
                continue
            try:
                n = len(sc.caption_ids(cap))
            except ValueError:
                bad = "special_token"
                break
            if which == "c+":
                n_pos = n
            else:
                n_neg = n
            if n < lo:
                bad = "too_short"
            elif n > hi:
                bad = bad or "too_long"
        counts.append((it["idx"], n_pos, n_neg))
        if bad:
            excluded[bad].append(it["idx"])
        else:
            kept.append(dict(it, n_tok_omni=n_pos, n_tok_neg_omni=n_neg))
    rep = dict(n_in=len(items), n_kept=len(kept), excluded=excluded, n_excluded=sum(len(v) for v in excluded.values()), rule="runtime Omni token count of c+ and c- in 5-32; excluded, counted, not replaced (SAP AB.5 item 3)",
               frozen_counts_are_llama2=True)
    return kept, rep


def write_exclusions(run: Path, rep: dict) -> None:
    Path(run).mkdir(parents=True, exist_ok=True)
    (Path(run) / "omni_token_exclusions.json").write_text(json.dumps(rep), encoding="utf8")
