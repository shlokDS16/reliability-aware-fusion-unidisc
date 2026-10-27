"""Shared run plumbing for the Paper 2 probes: run directory, config/SHA/env lock, resumable JSONL, COCO access, resource gates."""
from __future__ import annotations

import ctypes
import datetime as dt
import json
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"
GEN_PY = Path(r"C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe")
COCO_DIR = Path(r"C:\Users\Shlok\.cache\dlm_dl\coco")
CAPTIONS_JSON = COCO_DIR / "ann_extract" / "annotations" / "captions_val2017.json"
VAL_ZIP = COCO_DIR / "val2017.zip"
EXIT_MORE_WORK = 75


# ---------------------------------------------------------------------------------------------------------------- resources
def mem_status() -> dict:
    class MS(ctypes.Structure):
        _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("totp", ctypes.c_ulonglong), ("availp", ctypes.c_ulonglong),
                    ("totpf", ctypes.c_ulonglong), ("availpf", ctypes.c_ulonglong), ("totv", ctypes.c_ulonglong),
                    ("availv", ctypes.c_ulonglong), ("ext", ctypes.c_ulonglong)]
    m = MS()
    m.l = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return dict(free_ram_gb=round(m.availp / 1e9, 2), free_commit_gb=round(m.availpf / 1e9, 2))


def gpu_state() -> dict:
    r = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu,memory.used,utilization.gpu", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=30)
    t, m, u = [float(x) for x in r.stdout.strip().split(",")]
    return dict(temp_c=t, mem_used_mib=m, util_pct=u)


# ---------------------------------------------------------------------------------------------------------------- run dir
def git_sha() -> str:
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()


def git_dirty_files() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "exp_p2", "tools", "exp001"], capture_output=True, text=True).stdout
    return [l for l in out.splitlines() if l.strip()]


def init_run(run_id: str, config: dict) -> Path:
    """Create runs/<run_id>/ with config.json, git SHA, env lock (written once; later chunks only append telemetry and JSONL rows)."""
    d = RUNS / run_id
    d.mkdir(parents=True, exist_ok=True)
    cfg_path = d / "config.json"
    if not cfg_path.exists():
        cfg = dict(config, run_id=run_id, git_sha=git_sha(), created=dt.datetime.now().isoformat(timespec="seconds"),
                   python=sys.version, host_free=mem_status())
        cfg_path.write_text(json.dumps(cfg, indent=1), encoding="utf8")
    lock = d / "env-lock.txt"
    if not lock.exists():
        r = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
        lock.write_text(r.stdout, encoding="utf8")
    return d


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:                       # a torn last line after a hard kill: the item is redone
                pass
    return rows


def append_jsonl(path: Path, row: dict):
    with open(path, "a", encoding="utf8") as fh:
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


# ---------------------------------------------------------------------------------------------------------------- COCO
def load_captions() -> dict[int, list[str]]:
    d = json.loads(CAPTIONS_JSON.read_text(encoding="utf8"))
    caps: dict[int, list[str]] = {}
    for a in sorted(d["annotations"], key=lambda a: a["id"]):
        caps.setdefault(int(a["image_id"]), []).append(" ".join(a["caption"].split()))
    return caps


def select_items(n: int, seed: int, n_tok_fn, tok_range=(5, 32)) -> list[dict]:
    """Fixed-seed selection from the sorted val2017 image ids: walk a seeded permutation, pick one caption of the image (seeded), keep it if
    its token count lies in tok_range. Deterministic given (seed, tokenizer). Returns [{image_id, caption, n_tok}]."""
    caps = load_captions()
    ids = sorted(caps)
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(ids))
    out = []
    for j in order:
        iid = ids[int(j)]
        cs = caps[iid]
        c = cs[int(rng.integers(0, len(cs)))]
        nt = n_tok_fn(c)
        if tok_range[0] <= nt <= tok_range[1]:
            out.append(dict(image_id=iid, caption=c, n_tok=nt))
            if len(out) == n:
                break
    return out


_zip = None


def load_image(image_id: int):
    global _zip
    from PIL import Image
    import io
    if _zip is None:
        _zip = zipfile.ZipFile(VAL_ZIP)
    return Image.open(io.BytesIO(_zip.read(f"val2017/{image_id:012d}.jpg"))).convert("RGB")


def load_net(res: int = 512):
    """UniDisc via the EXP-001 adapter (waits for free system commit like every other run in this project)."""
    from exp001.unidisc_net import UniDiscNet
    return UniDiscNet(res=res)
