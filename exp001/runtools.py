"""Run helpers shared by the stage scripts: atomic writes, duty cycle, soft deadline, free-commit log (card 12.2)."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

EXIT_MORE_WORK = 75        # soft deadline reached, work remains: the driver starts another chunk after the pause
EXIT_DONE = 0


def atomic_write_bytes(path: Path, data: bytes):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def atomic_write_json(path: Path, obj):
    atomic_write_bytes(path, json.dumps(obj, indent=1, ensure_ascii=False).encode("utf8"))


def atomic_save_npz(path: Path, **arrays):
    import io
    import numpy as np
    buf = io.BytesIO()
    np.savez_compressed(buf, **arrays)
    atomic_write_bytes(path, buf.getvalue())


class Duty:
    """Duty cycle ~ `duty` (compute / wall): after a unit that used `busy` seconds of GPU time, sleep busy * (1/duty - 1)."""

    def __init__(self, duty: float = 0.5):
        self.duty = duty
        self.busy = 0.0
        self.idle = 0.0

    def after_unit(self, busy_s: float):
        self.busy += busy_s
        s = busy_s * (1.0 / self.duty - 1.0)
        time.sleep(s)
        self.idle += s


class Deadline:
    def __init__(self, soft_minutes: float):
        self.t_end = time.time() + soft_minutes * 60

    def reached(self, margin_s: float = 0.0) -> bool:
        return time.time() + margin_s >= self.t_end


def log_jsonl(path: Path, row: dict):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf8") as fh:
        fh.write(json.dumps(row) + "\n")
