"""Two-rater reliability check for the claim-evaluability rubric.

    python tools/reliability.py sample            # fixed-seed stratified sample of 40, extracts, human sheet
    python tools/reliability.py codex [--limit N] # rater B: one fresh read-only `codex exec` per paper, logged
    python tools/reliability.py agree             # agreement between rater-claude.jsonl and rater-codex.jsonl

Rater A (a Claude agent) writes research/review/reliability/rater-claude.jsonl from the same
extracts and the same rubric file. Neither rater sees the other's output.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import random
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import stage2_extract as s2

ROOT = s2.ROOT
REL = ROOT / "research" / "review" / "reliability"
RUBRIC = ROOT / "research" / "review" / "evaluability-rubric.md"
QUOTA = {"Inference Optimization": 12, "Discrete DLMs": 10, "Training Strategies": 6,
         "Multimodal DLMs": 6, "Continuous DLMs": 4, "Applications": 2}
TYPES = ["CT1", "CT2", "CT3", "CT4", "CT5", "CT6", "CT7", "none"]
MEC = ["absent", "partial", "met"]
BATCH = 20  # papers per Codex thread before a fresh thread is started


def load(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def all_blocks(text: str) -> tuple[list[str], list[str]]:
    spans, caps, tables, seen = s2.figure_spans(text), [], [], set()
    for m in s2.CAP.finditer(text):
        cap = s2.clean(m.group(1))
        caps.append(cap[:260])
        inner = min((s for s in spans if s[0] <= m.start() < s[1]), key=lambda s: s[1] - s[0], default=None)
        if inner is None or inner in seen or not cap.lower().startswith("table"):
            continue
        seen.add(inner)
        rows = [" | ".join(s2.clean(c) for c in s2.CELL.findall(r)) for r in s2.ROW.findall(text[inner[0]:inner[1]])]
        rows = [r for r in rows if r.strip(" |")]
        if rows:
            tables.append(f"### {cap[:300]}\n\n" + "\n".join(rows[:45])[:3000] + "\n")
    return caps, tables


def cmd_sample() -> None:
    rows = [r for r in load(s2.FEAS / "captions.jsonl") if r["has_html"]]
    corpus = {}
    for f in (ROOT / "research" / "review" / "corpus").glob("awesome-dlms@*.jsonl"):
        for r in load(f):
            corpus[r["record_id"]] = r
    used = set()  # papers rated in any earlier round are never reused
    for f in BASE.rglob("sample.json"):
        if f.parent != REL:
            used |= {m["record_id"] for m in json.loads(f.read_text(encoding="utf-8"))}
    rng, chosen = random.Random(s2.SEED + 2 + 10 * ROUND), []
    for sec, k in QUOTA.items():
        pool = sorted((r for r in rows if sec in r["sections"] and r not in chosen and r["record_id"] not in used),
                      key=lambda r: r["record_id"])
        chosen += rng.sample(pool, min(k, len(pool)))
    (REL / "papers").mkdir(parents=True, exist_ok=True)
    manifest = []
    for r in chosen:
        text = (s2.CACHE / f"{r['arxiv']}.html").read_text(encoding="utf-8", errors="replace")
        caps, tables = all_blocks(text)
        meta = corpus.get(r["record_id"], {}).get("arxiv") or {}
        body = (f"# {r['title']}\n\nrecord {r['record_id']} | arXiv:{r['arxiv']} | first version "
                f"{str(meta.get('published'))[:10]}\n\n**Abstract.** {meta.get('abstract', '(missing)')}\n\n"
                "## All captions\n\n" + "\n".join(f"- {c}" for c in caps) + "\n\n## Tables as text\n\n"
                + "\n".join(tables[:14]))[:30000]
        md = REL / "papers" / f"{r['record_id']}.md"
        md.write_text(body + "\n", encoding="utf-8")
        manifest.append({"record_id": r["record_id"], "arxiv": r["arxiv"], "title": r["title"],
                         "section": r["sections"][0], "file": str(md.relative_to(ROOT)).replace("\\", "/")})
    (REL / "sample.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    human = random.Random(s2.SEED + 3).sample(manifest, 15)
    with (REL / "human-sheet.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "title", "arxiv_url", "primary_claim", "claim_type", "mec", "uncertainty", "notes"])
        for m in human:
            w.writerow([m["record_id"], m["title"], f"https://arxiv.org/abs/{m['arxiv']}", "", "", "", "", ""])
    print(f"sampled {len(manifest)} papers; sections {dict(Counter(m['section'] for m in manifest))}; "
          f"human sheet: 15 rows; mean extract {sum((ROOT / m['file']).stat().st_size for m in manifest) // len(manifest)} bytes")


def cmd_codex(limit: int) -> None:
    exe = shutil.which("codex.cmd") or shutil.which("codex") or sys.exit("codex CLI not found")
    rubric = RUBRIC.read_text(encoding="utf-8")
    out, logf = REL / "rater-codex.jsonl", REL / "codex-log.jsonl"
    done = {r["record_id"] for r in load(out)} if out.exists() else set()
    work = REL / "codex-runs"
    work.mkdir(exist_ok=True)
    todo = [m for m in json.loads((REL / "sample.json").read_text(encoding="utf-8")) if m["record_id"] not in done]
    thread, in_thread = None, 0  # one Codex thread per batch of BATCH papers, resumed by explicit id
    for m in (todo[:limit] if limit else todo):
        prompt = work / f"{m['record_id']}.prompt.txt"
        paper = (ROOT / m["file"]).read_text(encoding="utf-8")
        resp, raw, t0 = work / f"{m['record_id']}.response.txt", work / f"{m['record_id']}.raw.log", time.time()
        resume = thread is not None and in_thread < BATCH
        if resume:
            prompt.write_text("Next paper. Apply the same rubric exactly, independently of earlier papers. Reply with ONE "
                              "JSON object and nothing else.\n\n=== PAPER ===\n" + paper, encoding="utf-8")
            cmd = [exe, "exec", "resume", "--skip-git-repo-check", "-o", str(resp), thread, "-"]
        else:
            prompt.write_text("You will rate research papers one at a time with the rubric below. Apply it exactly. "
                              "Reply with ONE JSON object and nothing else. Do not use tools or read files.\n\n"
                              "=== RUBRIC ===\n" + rubric + "\n\n=== PAPER ===\n" + paper, encoding="utf-8")
            cmd = [exe, "exec", "--sandbox", "read-only", "--skip-git-repo-check", "--color", "never",
                   "-C", str(work), "-o", str(resp), "-"]
        r = subprocess.run(cmd, input=prompt.read_text(encoding="utf-8"), cwd=str(work),
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        raw.write_text((r.stdout or "") + "\n--- stderr ---\n" + (r.stderr or ""), encoding="utf-8")
        text = resp.read_text(encoding="utf-8") if resp.exists() else ""
        sid = re.search(r"session id:\s*([0-9a-fA-F-]{8,})", raw.read_text(encoding="utf-8"))
        if r.returncode == 0:
            thread = (sid.group(1) if sid else None) or thread
            in_thread = in_thread + 1 if resume else 1
        j = re.search(r"\{.*\}", text, re.S)
        row, ok = None, False
        try:
            row = json.loads(j.group(0)) if j else None
            ok = bool(row) and (row.get("claim_type") in TYPES or set(row.get("claims", {})) == set(TYPES[:6]))
        except json.JSONDecodeError:
            pass
        with logf.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": dt.datetime.now().isoformat(timespec="seconds"), "record_id": m["record_id"],
                                 "cwd": str(work), "seconds": round(time.time() - t0, 1), "exit": r.returncode, "ok": ok,
                                 "codex_session": sid.group(1) if sid else None, "prompt": prompt.name,
                                 "prompt_sha": hashlib.sha256(prompt.read_bytes()).hexdigest()[:16],
                                 "response": resp.name}) + "\n")
        if ok:
            row["record_id"] = m["record_id"]
            with out.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"{m['record_id']} {'ok' if ok else 'FAILED'} {round(time.time() - t0)}s", flush=True)


def kappa(a: list, b: list, cats: list, weighted: bool = False) -> float:
    n, k = len(a), len(cats)
    idx = {c: i for i, c in enumerate(cats)}
    obs = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b):
        obs[idx[x]][idx[y]] += 1 / n
    pa, pb = [sum(r) for r in obs], [sum(obs[i][j] for i in range(k)) for j in range(k)]
    w = lambda i, j: (abs(i - j) / (k - 1)) if weighted else float(i != j)
    do = sum(w(i, j) * obs[i][j] for i in range(k) for j in range(k))
    de = sum(w(i, j) * pa[i] * pb[j] for i in range(k) for j in range(k))
    return 1 - do / de if de else float("nan")


def cmd_agree() -> None:
    A = {r["record_id"]: r for r in load(REL / "rater-claude.jsonl")}
    B = {r["record_id"]: r for r in load(REL / "rater-codex.jsonl")}
    ids = sorted(set(A) & set(B))
    ta, tb = [A[i]["claim_type"] for i in ids], [B[i]["claim_type"] for i in ids]
    print(f"papers rated by both: {len(ids)} (claude {len(A)}, codex {len(B)})")
    print(f"claim type: raw agreement {sum(x == y for x, y in zip(ta, tb)) / len(ids):.2f}, Cohen kappa {kappa(ta, tb, TYPES):.2f}")
    print("  claude:", dict(Counter(ta)), "\n  codex: ", dict(Counter(tb)))
    same = [i for i in ids if A[i]["claim_type"] == B[i]["claim_type"] and A[i]["mec"] in MEC and B[i]["mec"] in MEC]
    if same:
        ma, mb = [A[i]["mec"] for i in same], [B[i]["mec"] for i in same]
        print(f"MEC, where both chose the same scored type (n={len(same)}): raw {sum(x == y for x, y in zip(ma, mb)) / len(same):.2f}, "
              f"linear weighted kappa {kappa(ma, mb, MEC, True):.2f}")
        print("  claude:", dict(Counter(ma)), "\n  codex: ", dict(Counter(mb)))
    both = [i for i in ids if A[i].get("uncertainty") in ("yes", "no") and B[i].get("uncertainty") in ("yes", "no")]
    if both:
        ua, ub = [A[i]["uncertainty"] for i in both], [B[i]["uncertainty"] for i in both]
        print(f"uncertainty (n={len(both)}): raw {sum(x == y for x, y in zip(ua, ub)) / len(both):.2f}, kappa {kappa(ua, ub, ['no', 'yes']):.2f}; "
              f"yes: claude {ua.count('yes')}, codex {ub.count('yes')}")
    dis = [(i, A[i]["claim_type"], B[i]["claim_type"], A[i]["mec"], B[i]["mec"]) for i in ids
           if A[i]["claim_type"] != B[i]["claim_type"] or A[i]["mec"] != B[i]["mec"]]
    (REL / "disagreements.json").write_text(json.dumps(dis, indent=1), encoding="utf-8")
    print(f"disagreements on type or MEC: {len(dis)} -> {REL / 'disagreements.json'}")
    print("type confusions:", dict(Counter((x, y) for x, y in zip(ta, tb) if x != y)))


def cmd_agree2() -> None:
    """Agreement for rubric v0.2: per-type 'asserted', per-item answers, and the evaluable flag."""
    A = {r["record_id"]: r for r in load(REL / "rater-claude.jsonl")}
    B = {r["record_id"]: r for r in load(REL / "rater-codex.jsonl")}
    ids, yn = sorted(set(A) & set(B)), ["no", "yes"]
    print(f"papers rated by both: {len(ids)}")
    pa, pb, ea, eb, ia, ib = [], [], [], [], [], []
    for t in TYPES[:6]:
        a = [A[i]["claims"][t]["asserted"] for i in ids]
        b = [B[i]["claims"][t]["asserted"] for i in ids]
        pa += a
        pb += b
        both = [i for i in ids if A[i]["claims"][t]["asserted"] == "yes" == B[i]["claims"][t]["asserted"]]
        ev = lambda R, i: "yes" if R[i]["claims"][t]["a"] == "yes" == R[i]["claims"][t]["b"] else "no"
        xa, xb = [ev(A, i) for i in both], [ev(B, i) for i in both]
        ea += xa
        eb += xb
        for item in "ab":
            ia += [A[i]["claims"][t][item] if A[i]["claims"][t][item] in yn else "no" for i in both]
            ib += [B[i]["claims"][t][item] if B[i]["claims"][t][item] in yn else "no" for i in both]
        print(f"  {t}: asserted yes claude {a.count('yes')}, codex {b.count('yes')}, kappa {kappa(a, b, yn):.2f} | "
              f"both asserted {len(both)}; evaluable claude {xa.count('yes')}, codex {xb.count('yes')}, "
              f"agree {sum(x == y for x, y in zip(xa, xb))}/{len(both)}")
    print(f"asserted, pooled over 6 types x {len(ids)} papers: raw {sum(x == y for x, y in zip(pa, pb)) / len(pa):.2f}, kappa {kappa(pa, pb, yn):.2f}")
    print(f"items, pooled where both asserted (n={len(ia)}): raw {sum(x == y for x, y in zip(ia, ib)) / max(1, len(ia)):.2f}, kappa {kappa(ia, ib, yn):.2f}")
    print(f"evaluable, pooled where both asserted (n={len(ea)}): raw {sum(x == y for x, y in zip(ea, eb)) / max(1, len(ea)):.2f}, "
          f"kappa {kappa(ea, eb, yn):.2f}; evaluable share claude {ea.count('yes') / max(1, len(ea)):.2f}, codex {eb.count('yes') / max(1, len(eb)):.2f}")
    ua, ub = [A[i]["uncertainty"] for i in ids], [B[i]["uncertainty"] for i in ids]
    print(f"uncertainty: raw {sum(x == y for x, y in zip(ua, ub)) / len(ids):.2f}, kappa {kappa(ua, ub, yn):.2f}; yes claude {ua.count('yes')}, codex {ub.count('yes')}")


if __name__ == "__main__":
    BASE, ROUND = REL, 1
    if len(sys.argv) > 1 and sys.argv[1].startswith("round"):
        ROUND = int(sys.argv[1][5:])
        REL = BASE / sys.argv[1]
        del sys.argv[1]
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "agree2":
        cmd_agree2()
        sys.exit()
    REL.mkdir(parents=True, exist_ok=True)
    if cmd == "sample":
        cmd_sample()
    elif cmd == "codex":
        cmd_codex(int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--limit" else 0)
    elif cmd == "agree":
        cmd_agree()
    else:
        sys.exit(__doc__)
