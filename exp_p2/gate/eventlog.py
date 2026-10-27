"""Read-only check of the Windows event logs for the crash signatures of the diagnosis (audit finding F3). Runs `Get-WinEvent` through PowerShell; never writes.

Watched since a given local time: System log Ids 41 (Kernel-Power), 105 (power source change), 117 and 141 (display driver / LiveKernelEvent) and 4101 (Display); Application
log Id 1001 (Windows Error Reporting) only when its text mentions a kernel-level GPU event (LiveKernelEvent, nvlddmkm, Bugcheck, BlueScreen), because Id 1001 also fires for any
ordinary application crash. If the log cannot be read the result says so and the driver stops (fail closed); `--no-eventlog-check` overrides."""
from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime

SYSTEM_IDS = (41, 105, 117, 141, 4101)
APP_ID = 1001
APP_PATTERN = re.compile(r"LiveKernelEvent|nvlddmkm|Bugcheck|BlueScreen", re.I)


def ps_script(since: datetime) -> str:
    t = since.strftime("%Y-%m-%dT%H:%M:%S")
    ids = ",".join(str(i) for i in SYSTEM_IDS)
    sel = "Select-Object Id,LogName,ProviderName,@{n='T';e={$_.TimeCreated.ToString('o')}},@{n='M';e={[string]$_.Message}}"
    return (f"$s=[datetime]'{t}'; "
            f"$a=Get-WinEvent -FilterHashtable @{{LogName='System';Id={ids};StartTime=$s}} -MaxEvents 200 -ErrorAction SilentlyContinue | {sel}; "
            f"$b=Get-WinEvent -FilterHashtable @{{LogName='Application';Id={APP_ID};StartTime=$s}} -MaxEvents 200 -ErrorAction SilentlyContinue | {sel}; "
            f"@($a)+@($b) | Where-Object {{ $_ -ne $null }} | ConvertTo-Json -Compress")


def parse(output: str) -> list[dict]:
    out = output.strip()
    if not out:
        return []
    obj = json.loads(out)
    return obj if isinstance(obj, list) else [obj]


def relevant(events: list[dict]) -> list[dict]:
    keep = []
    for e in events:
        if int(e["Id"]) in SYSTEM_IDS or (int(e["Id"]) == APP_ID and APP_PATTERN.search(str(e.get("M") or ""))):
            keep.append(dict(id=int(e["Id"]), log=e.get("LogName"), provider=e.get("ProviderName"), time=e.get("T"), message=str(e.get("M") or "")[:200]))
    return keep


def _run_powershell(script: str) -> str:
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script], capture_output=True, text=True, timeout=90)
    if r.returncode != 0:
        raise RuntimeError(f"powershell exit {r.returncode}: {r.stderr[:300]}")
    return r.stdout


def new_events(since: datetime, run=_run_powershell) -> dict:
    """-> dict(ok, events, error). ok=False means the log could not be read (the caller must treat that as 'unknown', not 'clean')."""
    try:
        return dict(ok=True, events=relevant(parse(run(ps_script(since)))), error=None)
    except Exception as e:                                   # noqa: BLE001 - any failure to read is reported, never swallowed
        return dict(ok=False, events=[], error=repr(e))
