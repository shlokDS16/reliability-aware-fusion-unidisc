"""Shared helpers: stubs for Linux-only imports, forward-pass timing, timing.json merge."""
import json, os, sys, time, types, statistics, platform
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent  # runs/env-2026-10-14
THIRD = Path(os.environ.get("DLM_THIRD_PARTY", r"C:\Users\Shlok\Downloads\Multi-Modality Language model\models\third_party"))


if not hasattr(os, "sched_getaffinity"):  # Linux-only call used at import time by the MDLM and UniDisc repos
    os.sched_getaffinity = lambda pid: set(range(os.cpu_count() or 1))


def commit_free_gb():
    """Windows free system commit (RAM+pagefile) in GB. On this machine every cudaMalloc byte also consumes commit, so
    low free commit caps usable VRAM far below 12 GB (see setup.md)."""
    import ctypes
    class MS(ctypes.Structure):
        _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("totp", ctypes.c_ulonglong), ("availp", ctypes.c_ulonglong),
                    ("totpf", ctypes.c_ulonglong), ("availpf", ctypes.c_ulonglong), ("totv", ctypes.c_ulonglong),
                    ("availv", ctypes.c_ulonglong), ("ext", ctypes.c_ulonglong)]
    m = MS(); m.l = ctypes.sizeof(MS); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return round(m.availpf / 1e9, 2)


def wait_commit(need_gb, timeout_s=900, poll_s=10):
    """Block until the machine has at least need_gb of free system commit (other sessions' stale processes make it swing
    between ~1 and ~17 GB; running while it is low produces spurious CUDA OOMs). Returns the last reading."""
    import time as _t
    t0 = _t.time(); c = commit_free_gb()
    while c < need_gb and _t.time() - t0 < timeout_s:
        _t.sleep(poll_s); c = commit_free_gb()
    return c


def add_shims():
    """Put the pure-PyTorch flash_attn stand-in first on sys.path."""
    p = str(HERE / "shims")
    if p not in sys.path:
        sys.path.insert(0, p)


def stub_modules(*names):
    """Register empty placeholder modules (attribute access returns a function that raises when called)."""
    for n in names:
        parts = n.split(".")
        for i in range(1, len(parts) + 1):
            k = ".".join(parts[:i])
            if k not in sys.modules:
                m = types.ModuleType(k)
                def _ga(attr, _k=k):
                    if attr.startswith("__"):
                        raise AttributeError(attr)
                    def _f(*a, **kw):
                        raise NotImplementedError(f"stub {_k}.{attr}")
                    return _f
                m.__getattr__ = _ga
                sys.modules[k] = m
            if i > 1:
                setattr(sys.modules[".".join(parts[:i - 1])], parts[i - 1], sys.modules[k])


def timeit_cuda(fn, warmup=2, iters=5):
    """Median seconds per call of fn() with CUDA sync; also returns peak allocated GB over the timed calls."""
    import torch
    for _ in range(warmup):
        fn()
    torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
    ts = []
    for _ in range(iters):
        torch.cuda.synchronize(); t0 = time.perf_counter()
        fn()
        torch.cuda.synchronize(); ts.append(time.perf_counter() - t0)
    return dict(median_s=statistics.median(ts), min_s=min(ts), max_s=max(ts), iters=iters,
                peak_alloc_gb=torch.cuda.max_memory_allocated() / 1e9,
                peak_reserved_gb=torch.cuda.max_memory_reserved() / 1e9)


def try_oom(fn):
    """Run fn(); turn CUDA OOM into a result dict instead of a crash."""
    import torch
    try:
        return fn()
    except torch.OutOfMemoryError as e:
        torch.cuda.empty_cache()
        return dict(status="OOM", message=str(e).splitlines()[0][:200], free_system_commit_gb=commit_free_gb())


def merge_json(path, section, data):
    path = Path(path)
    cur = json.loads(path.read_text()) if path.exists() else {}
    cur[section] = data
    path.write_text(json.dumps(cur, indent=2))


def env_info():
    import torch
    return dict(python=platform.python_version(), torch=torch.__version__, cuda=torch.version.cuda,
                gpu=torch.cuda.get_device_name(0), vram_total_gb=torch.cuda.get_device_properties(0).total_memory / 1e9,
                platform=platform.platform(), free_system_commit_gb_at_start=commit_free_gb())
