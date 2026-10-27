"""In-process watchdog for the gate runners (audit finding M1; tools/gpu_guard.py is NOT edited: its SHA-256 is pinned by the Paper 1 EXP-003 manifest).

The per-item checks of `guards.Guards` cannot see a memory jump inside an item (the 2026-10-27 crash happened within 5 s; an item takes 7-10 s). This thread samples
whole-GPU memory and AC power every second while the model runs and applies the diagnosis' abort rules: used memory above the limit (higher allowance during the first
item), a rise of more than 1.5 GB between two consecutive samples, AC lost. On a trip it calls `on_trip(reason)`; the default writes a `guard_stop` event, flushes and
ends the process at once with EXIT_GUARD (76), because a GPU job in the middle of a forward cannot be interrupted any other way. Readers and the sleep are injectable, so
the logic is unit-tested without a GPU."""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from pathlib import Path

EXIT_GUARD = 76          # a guard abort; distinct from the soft-deadline code 75 (the driver relaunches after 75, never after 76)


class Watchdog:
    def __init__(self, guards, *, used_fn=None, ac_fn=None, on_trip=None, every: float = 1.0, sleep=time.sleep):
        self.g = guards
        self.used_fn = used_fn or guards.used_fn
        self.ac_fn = ac_fn or guards.ac_fn
        self.on_trip = on_trip or (lambda why: None)
        self.every, self.sleep = every, sleep
        self._last: float | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.tripped: str | None = None

    def check_once(self) -> str | None:
        if self.g.require_ac and self.ac_fn() is False:
            return "ac_lost"
        used = float(self.used_fn())
        lim = self.g.max_used_first_mib if self.g.first_item_active else self.g.max_used_mib
        if used > lim:
            return f"gpu_memory {used:.0f} MiB > {lim:.0f}"
        if self._last is not None and used - self._last > self.g.max_rise_mib:
            return f"gpu_memory_rise {used - self._last:.0f} MiB in {self.every:g} s"
        self._last = used
        return None

    def _loop(self):
        while not self._stop.is_set():
            try:
                why = self.check_once()
            except Exception as e:                       # an unreadable sensor is itself a reason to stop (fail closed)
                why = f"sensor_error {e!r}"
            if why:
                self.tripped = why
                self.on_trip(why)
                return
            self.sleep(self.every)

    def start(self) -> "Watchdog":
        self._thread = threading.Thread(target=self._loop, daemon=True, name="gate-watchdog")
        self._thread.start()
        return self

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)


def kill_process_on_trip(events_path: Path):
    """Default on_trip for production: log, flush, end the process with EXIT_GUARD."""
    def trip(why: str):
        try:
            with open(events_path, "a", encoding="utf8") as fh:
                fh.write(json.dumps(dict(event="guard_stop", source="watchdog", t=time.time(), reason=why)) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
        finally:
            print("WATCHDOG STOP:", why, file=sys.stderr, flush=True)
            os._exit(EXIT_GUARD)
    return trip
