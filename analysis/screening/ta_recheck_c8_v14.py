"""Supplementary re-check class C8 (criteria v1.4, fix V1): title/abstract exclusions that name an existing text
diffusion model and were coded X1 or X2 (non-text output), which R14's precedence over R7 in v1.4 may include.

The frozen v1.3 frame and sample are not changed or redrawn. C8 is a separate frame: records already in the frozen
frame are left out. Same frames and same title/abstract inputs as ta_recheck_select.py (imported read-only from the
repository; nothing is written there). Design as for every later frame: all C8 candidates go to full text if there
are at most 150 (CAP); otherwise a simple random sample of 100 with seed 20261016 and the reversal rule K >= 1.

    python -I ta_recheck_c8_v14.py --repo <repository root> --out <output .jsonl> --log <output .log>
"""
import argparse
import hashlib
import importlib.util
import json
import random
import re
from collections import Counter
from pathlib import Path

I = re.IGNORECASE
EXISTING_DLM = re.compile(
    r"diffusion language model|diffusion llm|\bdllms?\b|large language diffusion|diffusion-based (large )?language model|"
    r"masked diffusion language|\bllada\b|\bmdlm\b|\bsedd\b|\bplaid\b|diffusion large language", I)
FROZEN_FRAME_SHA256 = "a9180fe4bdb7956b8d8e6c4340559c94ac4f877cbc6376d1dad99995bb32d79a"
CAP, SAMPLE_N, SEED = 150, 100, 20261016


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    repo = Path(a.repo)
    sel_path = repo / "analysis" / "screening" / "ta_recheck_select.py"
    spec = importlib.util.spec_from_file_location("ta_recheck_select", sel_path)
    sel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sel)                      # defines functions only; main() is not called
    frozen = repo / "analysis" / "screening" / "ta-recheck-frame-v1.3-frozen.jsonl"
    raw = frozen.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FROZEN_FRAME_SHA256:
        raise SystemExit("frozen frame digest changed; stopping")
    in_frozen = {json.loads(l)["id"] for l in raw.decode("utf-8").splitlines() if l.strip()}
    rows = sel.frames()
    cands = []
    for f, i, t, ab, codes, ta in rows:
        if i in in_frozen or not (codes & {"X1", "X2"}):
            continue
        if sel.DIFF.search(t + " " + ab) and EXISTING_DLM.search(t + " " + ab):
            cands.append({"id": i, "frame": f, "classes": ["C8_existing_text_dlm_nonlanguage"], "ta_codes": ta,
                          "title": t})
    cands.sort(key=lambda r: (r["frame"], r["id"]))
    sample = []
    if len(cands) > CAP:
        sample = sorted(random.Random(SEED).sample([r["id"] for r in cands], SAMPLE_N))
    with open(a.out, "w", encoding="utf-8") as fh:
        for r in cands:
            r["in_sample"] = (r["id"] in sample) if sample else True
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    digest = hashlib.sha256(Path(a.out).read_bytes()).hexdigest()
    by_frame = Counter(r["frame"] for r in cands)
    lines = ["ta_recheck_c8_v14.py (criteria v1.4, V1)",
             f"title/abstract exclusions scanned: {len(rows)}; already in frozen frame: {len(in_frozen)}",
             f"C8 candidates (not in frozen frame): {len(cands)} by frame {dict(sorted(by_frame.items()))}",
             (f"candidates > CAP {CAP}: sample {SAMPLE_N}, seed {SEED}" if sample
              else f"candidates <= CAP {CAP}: all go to full text"),
             f"candidates file sha256: {digest}"]
    Path(a.log).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
