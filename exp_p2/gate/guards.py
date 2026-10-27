"""Per-item resource guards for the gate runners, with the thresholds proposed in PROBE2-CRASH-DIAGNOSIS-2026-10-28.md section 5
(abort rules). They are PROPOSED values: using them as defaults needs Shlok's approval (the diagnosis says so); every threshold
is a constructor argument and a CLI flag in the runners. The checks are pure functions of injected readings so they are unit-tested."""
from __future__ import annotations

import ctypes
import statistics
from dataclasses import dataclass, field


def on_ac() -> bool | None:
    """True on mains power, False on battery, None if unknown (Windows GetSystemPowerStatus: ACLineStatus 1/0/255)."""
    class SPS(ctypes.Structure):
        _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte), ("BatteryLifePercent", ctypes.c_ubyte),
                    ("SystemStatusFlag", ctypes.c_ubyte), ("BatteryLifeTime", ctypes.c_ulong), ("BatteryFullLifeTime", ctypes.c_ulong)]
    try:
        s = SPS()
        if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s)):
            return None
        return {1: True, 0: False}.get(int(s.ACLineStatus))
    except Exception:
        return None


def gpu_used_mib() -> float:
    """Whole-GPU memory used (all processes), MiB, from torch.cuda.mem_get_info (cheap, no nvidia-smi)."""
    import torch
    free_b, total_b = torch.cuda.mem_get_info()
    return (total_b - free_b) / 2**20


@dataclass
class Guards:
    max_used_mib: float = 9000.0          # diagnosis: abort above 9,000 MiB ...
    max_used_first_mib: float = 10000.0   # ... 10,000 MiB during the first item
    max_rise_mib: float = 1500.0          # ... or a rise of more than 1.5 GB between two consecutive readings
    slow_factor: float = 2.0              # ... or an item taking more than 2x the median of the earlier items of this chunk
    min_items_for_median: int = 3
    require_ac: bool = True
    used_fn: object = gpu_used_mib
    ac_fn: object = on_ac
    _last_used: float | None = field(default=None, repr=False)
    _times: list = field(default_factory=list, repr=False)

    def before_item(self, n_done_in_chunk: int) -> str | None:
        """Reason to stop before starting the next item, or None."""
        if self.require_ac and self.ac_fn() is False:
            return "ac_lost"
        used = float(self.used_fn())
        lim = self.max_used_first_mib if n_done_in_chunk == 0 else self.max_used_mib
        if used > lim:
            return f"gpu_memory {used:.0f} MiB > {lim:.0f}"
        if self._last_used is not None and used - self._last_used > self.max_rise_mib:
            return f"gpu_memory_rise {used - self._last_used:.0f} MiB"
        self._last_used = used
        return None

    def after_item(self, busy_s: float) -> str | None:
        prior = list(self._times)
        self._times.append(busy_s)
        if len(prior) >= self.min_items_for_median and busy_s > self.slow_factor * statistics.median(prior):
            return f"slow_item {busy_s:.1f}s > {self.slow_factor}x median {statistics.median(prior):.1f}s"
        return None
