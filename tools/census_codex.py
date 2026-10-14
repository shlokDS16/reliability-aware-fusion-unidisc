"""Census coder B: Codex codes one paper per call, 20 papers per resumed thread (codebook v1 as amended by v1.1).

For each paper in research/review/census/census-order.csv (in rank order, from --start), Codex opens
the plain-text full text in the main checkout's research/sources/census-text/<arxiv>.txt, decides
full-text eligibility (protocol I1-I4) and, if eligible, codes F1-F6. One JSON object is validated
and appended to research/review/census/coder-B.jsonl, with a run-log row (time, model, prompt and
response SHA-256). Stops when --target eligible papers are coded. Resumable.

    python tools/census_codex.py --target 150 [--start 1] [--model NAME]
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CEN = ROOT / "research" / "review" / "census"
COV = ROOT / "research" / "review" / "coverage"
TEXT = Path(r"C:\Users\Shlok\Downloads\Multi-Modality Language model\research\sources\census-text")
OUT = CEN / "coder-B.jsonl"
BATCH = 20  # papers per resumed Codex thread
FIELDS = ["eligible", "exclusion_code", "F0_version", "F1_task", "F1_metric", "F1_value", "F1_location",
          "F2_codes", "F2_detail", "F2_location", "F3", "F3_location", "F4", "F4_location", "F5", "F6", "notes"]

ELIG = """FULL-TEXT ELIGIBILITY (decide first). Eligible if all hold: I1 the paper proposes, analyses,
evaluates or benchmarks (a) a diffusion model (discrete or continuous, including masked or absorbing
diffusion, discrete flow matching, diffusion on embeddings or the simplex) whose output includes
natural-language text or code, or (b) a unified model that both understands and generates across
text and another modality using a diffusion, masked-generative or discrete-flow component; I2 it is
a primary study with a method, theory or empirical result; I3 English full text; I4 first version
from 2021-01-01. If not eligible, give one exclusion code: X0 no diffusion component, X1 non-text
diffusion only, X2 text only as conditioning, X3 secondary study, X4 no result, X5 duplicate,
X7 application of an unchanged model with no model-level finding, X8 date or language."""

ASK = """Open the file {fname} in the current directory (the paper's full text, extracted from its
arXiv HTML) and code it. Apply the codebook literally; code from the paper's text only.
Return exactly one JSON object on one line, nothing else, with these keys:
{keys}
Use "eligible": "yes" or "no". If "no", set exclusion_code and leave F fields as "NA".
F2_codes: letters joined by + from A, T, P, S, G, M, or "U", "NS", "NA" as the codebook defines.
F1 may be "QL" (codebook v1.1 A-10) or "NA". Quotes in notes at most 15 words."""


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf8")).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=150)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--model", default=None)
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()
    exe = shutil.which("codex.cmd") or shutil.which("codex")
    if not exe:
        sys.exit("codex CLI not found on PATH")
    codebook = (COV / "census-codebook-v1.md").read_text(encoding="utf8") + "\n\n" + \
        (COV / "census-codebook-v1.1.md").read_text(encoding="utf8")
    done = {}
    if OUT.exists():
        for line in open(OUT, encoding="utf8"):
            d = json.loads(line)
            done[d["arxiv"]] = d
    eligible = sum(1 for d in done.values() if d.get("eligible") == "yes")
    order = list(csv.DictReader(open(CEN / "census-order.csv", encoding="utf8")))
    thread, in_thread = None, 0  # one Codex thread per BATCH papers, resumed by explicit id (memory: codex-one-thread)
    for r in order[a.start - 1:]:
        if eligible >= a.target:
            break
        aid = r["arxiv"]
        if aid in done:
            continue
        f = TEXT / f"{aid}.txt"
        if not f.exists():
            print(f"rank {r['rank']} {aid}: no full text, skipped (counted as unavailable)")
            continue
        resume = thread is not None and in_thread < BATCH
        if resume:
            prompt = ("Next paper. Apply the same eligibility rules and codebook exactly, independently of earlier "
                      "papers.\n\n" + ASK.format(fname=f.name, keys=", ".join(FIELDS)))
        else:
            prompt = (ELIG + "\n\nCODEBOOK (v1, then amendments v1.1):\n" + codebook + "\n\n" +
                      ASK.format(fname=f.name, keys=", ".join(FIELDS)))
        resp = CEN / "codex-tmp-response.txt"
        if resp.exists():
            resp.unlink()
        if resume:
            cmd = [exe, "exec", "resume", "-c", 'sandbox_mode="read-only"', "--skip-git-repo-check", "-o", str(resp)] + \
                (["-m", a.model] if a.model else []) + [thread, "-"]
        else:
            cmd = [exe, "exec", "--sandbox", "read-only", "--skip-git-repo-check", "--color", "never",
                   "-C", str(TEXT), "-o", str(resp)] + (["-m", a.model] if a.model else []) + ["-"]
        t0 = dt.datetime.now(dt.timezone.utc)
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=a.timeout, cwd=str(TEXT))
        raw = (p.stdout or "") + (p.stderr or "")
        model = re.search(r"^model:\s*(\S+)", raw, re.M)
        text = resp.read_text(encoding="utf8") if resp.exists() else ""
        if "usage limit" in (raw + text).lower():
            sys.exit(f"rank {r['rank']}: Codex usage limit reached; stopping without further calls")
        sid = re.search(r"session id:\s*([0-9a-fA-F-]{8,})", raw)
        if p.returncode == 0:
            thread = (sid.group(1) if sid else None) or thread
            in_thread = in_thread + 1 if resume else 1
        obj = None
        for line in text.splitlines():
            line = line.strip().strip("`")
            if line.startswith("{"):
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    pass
        ok = isinstance(obj, dict) and obj.get("eligible") in ("yes", "no")
        log = {"ts": t0.isoformat(), "rank": r["rank"], "arxiv": aid, "exit": p.returncode, "ok": ok,
               "model": model.group(1) if model else a.model, "codex_session": sid.group(1) if sid else None,
               "thread_mode": "resume" if resume else "new", "prompt_sha": sha(prompt),
               "response_sha": sha(text) if text else None,
               "seconds": (dt.datetime.now(dt.timezone.utc) - t0).total_seconds()}
        with open(CEN / "coder-B-run-log.jsonl", "a", encoding="utf8") as fh:
            fh.write(json.dumps(log) + "\n")
        if not ok:
            print(f"rank {r['rank']} {aid}: failed (exit {p.returncode}); retry later")
            continue
        row = {"rank": int(r["rank"]), "sid": r["sid"], "arxiv": aid, **{k: obj.get(k, "") for k in FIELDS}}
        with open(OUT, "a", encoding="utf8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        eligible += row["eligible"] == "yes"
        print(f"rank {r['rank']} {aid}: eligible={row['eligible']} F2={row['F2_codes']} (eligible so far {eligible})")


if __name__ == "__main__":
    main()
