"""Write-once artifacts (audit M6): family.json, threshold.json and detection_frozen.json are decisions that the SAP freezes before later stages run. Overwriting one
silently would change the experiment, so a second write is refused unless --force is given; a forced write keeps the old file as <name>.prev-<time> and logs an amendment
line (file, time, sha1 of the old and the new content) to amendments.jsonl in the same directory, because the SAP treats any such rerun as an amended run."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path


class WriteOnceError(FileExistsError):
    pass


def write_once(path: Path, text: str, force: bool = False) -> dict:
    path = Path(path)
    sha = lambda t: hashlib.sha1(t.encode("utf8")).hexdigest()[:16]
    if path.exists():
        if not force:
            raise WriteOnceError(f"{path} already exists; it is write-once (SAP). Re-run with --force to amend it; the old file is kept and an amendment is logged.")
        old = path.read_text(encoding="utf8")
        stamp = time.strftime("%Y%m%dT%H%M%S")
        path.with_name(f"{path.name}.prev-{stamp}").write_text(old, encoding="utf8")
        with open(path.with_name("amendments.jsonl"), "a", encoding="utf8") as fh:
            fh.write(json.dumps(dict(file=path.name, time=stamp, old_sha1=sha(old), new_sha1=sha(text))) + "\n")
    path.write_text(text, encoding="utf8")
    return dict(path=str(path), forced=bool(force))
