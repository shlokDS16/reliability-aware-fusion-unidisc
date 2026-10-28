"""ps_frozen.json (SAP AD.4, AD.12 step 2, A3.3 item 1, AB.8; code audit A3 part 1, M-1 and M-2). The parameters of the token-level corruptions of family PS (patch, swap) are written ONCE, before the first
M4 item, next to `family.json`, and committed. M4 and the E-pred fit chunk refuse to start without it, and the run-time geometry (token grid 32, patch 8) is asserted in both.

    python -m exp_p2.gate.ps_freeze write [--run-id P2-GATE-M3] [--force]     # CPU: runs/P2-GATE-M3/ps_frozen.json, write-once (--force keeps the old file and logs an amendment); then COMMIT it
    python -m exp_p2.gate.ps_freeze check [--run-id P2-GATE-M3]               # CPU: the file exists, is committed and equals the parameters in the code

The file holds the patch block (config.PATCH tokens per side on the config.GRID map), SWAP_FRAC, the vocabulary size, the random-stream tags, the condition order (patch first, swap appended after it: a different
order or a dropped patch would change the swap condition index and its jitter stream), the denoise list that fixes the condition indices, the gate seed and the code commit. Nothing here depends on data."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2.gate import artifacts, config, corruptions     # noqa: E402

PS_FROZEN = "ps_frozen.json"
M3_RUN = "P2-GATE-M3"
SANITY_ORDER = ("patch", "swap")
EXPECTED_GEOMETRY = (config.GRID, config.PATCH)      # (token grid side, patch side) asserted at run time; production 32 and 8 (AB.7 item 2). tests/exp_p2/conftest.py sets (4, 2) for the 4 x 4 fake network.


class PsFrozenError(RuntimeError):
    """ps_frozen.json is missing, not committed, or differs from the parameters in the code."""


class PsGeometryError(AssertionError):
    """The scorer's token map or the derived patch is not the one the SAP freezes (AB.7 item 2, A3.3 item 3)."""


def params() -> dict:
    """The frozen parameters, from the code's constants (no data)."""
    from exp_p2.scoring import IMG_VOCAB
    grid = config.GRID
    return dict(grid=grid, n_tokens=grid * grid, patch=config.PATCH, patch_rule="max(2, grid // 4) = 8 on the 32 x 32 map", patch_share=config.PATCH ** 2 / grid ** 2, swap_frac=config.SWAP_FRAC,
                swap_n_positions=round(config.SWAP_FRAC * grid * grid), vocab=IMG_VOCAB, token_rng_tag=dict(corruptions.TOKEN_RNG_TAG), rng="np.random.default_rng([SEED_GATE, gid, tag])",
                seed_gate=config.SEED_GATE, sanity_order=list(SANITY_ORDER), condition_order="clean, each family corruption (with its denoised copy if in denoise_for), patch, swap",
                denoise_for=list(config.DENOISE_FOR), alphas=list(config.ALPHAS))


def path_for(runs: Path, m3_run: str = M3_RUN) -> Path:
    return Path(runs) / m3_run / PS_FROZEN


def git_head(repo: Path = ROOT) -> str | None:
    r = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def build() -> dict:
    return dict(kind="ps_frozen", version=1, created=time.strftime("%Y-%m-%dT%H:%M:%S%z"), spec="SAP-GATE-2026-10-28 AD.4, AD.12 step 2, A3.3 item 1, AB.7 item 2, AB.8", params=params(),
                code_commit=git_head(), note="written before the first M4 item and committed; M4 and the E-pred fit chunk refuse to start without it; the run-time geometry is asserted in both")


def write(runs: Path, m3_run: str = M3_RUN, force: bool = False) -> dict:
    out = path_for(runs, m3_run)
    out.parent.mkdir(parents=True, exist_ok=True)
    return artifacts.write_once(out, json.dumps(build(), indent=1), force)


def sha256(runs: Path, m3_run: str = M3_RUN) -> str:
    return hashlib.sha256(Path(path_for(runs, m3_run)).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def check(runs: Path, m3_run: str = M3_RUN, *, require_commit: bool = True) -> dict:
    """Returns the file's content. Raises PsFrozenError if the file is missing, differs from `params()` (a parameter changed after the freeze), or (require_commit) is not tracked and unmodified in git."""
    p = path_for(runs, m3_run)
    if not p.exists():
        raise PsFrozenError(f"{p} missing: the parameters of the token-level corruptions are frozen before the first M4 item (SAP AD.4, A3.3 item 1); create it with: python -m exp_p2.gate.ps_freeze write, then commit it")
    doc = json.loads(p.read_text(encoding="utf8"))
    cur = json.loads(json.dumps(params()))
    diff = sorted(k for k in set(cur) | set(doc.get("params", {})) if cur.get(k) != doc.get("params", {}).get(k))
    if diff:
        raise PsFrozenError(f"{p} differs from the parameters in the code in {diff}: a PS parameter changed after the freeze (SAP AB.8: needs a dated addendum)")
    if require_commit:
        from exp_p2.gate import foil
        try:
            foil.require_committed(p)
        except (RuntimeError, ValueError) as e:
            raise PsFrozenError(f"ps_frozen.json must be committed and unmodified before the first M4 item (SAP AD.12 step 2, AB.8): {e}")
    return doc


def assert_runtime(grid: int, patch: int) -> None:
    """AB.7 item 2 / A3.3 item 3: the token map and the derived patch must be the frozen ones (32 and 8 in production). Raises PsGeometryError with a STOP line."""
    if (int(grid), int(patch)) != tuple(EXPECTED_GEOMETRY):
        raise PsGeometryError(f"STOP: token grid {grid} and patch {patch} differ from the frozen geometry (grid, patch) = {tuple(EXPECTED_GEOMETRY)}; the PS corruptions are not the ones the SAP freezes (AB.7 item 2)")


def main(argv=None) -> int:
    from exp_p2 import common
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("write", "check"):
        s = sub.add_parser(name)
        s.add_argument("--run-id", default=M3_RUN)
        s.add_argument("--runs-dir", default=str(common.RUNS))
        if name == "write":
            s.add_argument("--force", action="store_true", help="overwrite (the old file is kept and an amendment is logged; a changed PS parameter after M4 started withdraws PS, AB.8)")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "write":
            print(json.dumps(write(Path(a.runs_dir), a.run_id, a.force)))
            print("commit runs/%s/%s before the first M4 item" % (a.run_id, PS_FROZEN))
        else:
            check(Path(a.runs_dir), a.run_id)
            print("ok")
    except (PsFrozenError, artifacts.WriteOnceError) as e:
        print("STOP:", e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
