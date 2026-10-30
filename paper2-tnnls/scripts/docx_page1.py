"""Place the wide (two-column) floats of the Word manuscript the way the PDF places them.

A wide float is a floating table (w:tblpPr, tblpXSpec="center") pinned to the top margin of the page that holds its
anchor. Two rules, checked with Word itself (COM):
  1. no wide float on page 1 (else Word draws it above the title; the DOCX twin of main.tex's dbltopnum = 0 rule);
  2. at most one wide float per page (two stacked wide floats make Word leave the rest of that page blank).
A float that breaks a rule is re-anchored before the first body paragraph that starts on the next page, and the layout is
probed again until both rules hold. Needs Microsoft Word; without it the caller reports the failure.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import docx
from docx.oxml.ns import qn

PROBE_PS = r"""
param([string]$In)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
$out = @{ paras = @(); floats = @(); pages = 0 }
try {
  $d = $w.Documents.Open($In, $false, $true)
  try { $d.Repaginate() } catch { }   # can fail on some layouts; page queries below paginate anyway
  $out.pages = $d.ComputeStatistics(2)
  foreach ($t in $d.Tables) {
    if ($t.Rows.WrapAroundText) {
      $out.floats += @{ text = $t.Range.Text.Substring(0, [Math]::Min(80, $t.Range.Text.Length)); page = $t.Range.Characters.First.Information(3) }
    }
  }
  foreach ($p in $d.Paragraphs) {
    $r = $p.Range
    if ($r.Information(12)) { continue }
    $out.paras += @{ text = $r.Text.Substring(0, [Math]::Min(80, $r.Text.Length)); page = $r.Characters.First.Information(3) }
  }
  $d.Close($false)
} finally { $w.Quit() }
$out | ConvertTo-Json -Depth 4 -Compress
"""


def _norm(s: str) -> str:
    # letters and digits only: Word's Range.Text carries image placeholders, cell marks and a different space character
    return re.sub(r"[^A-Za-z0-9]", "", s or "")[:40]


def probe(docx_path: Path, tries: int = 3) -> dict:
    ps = Path(tempfile.gettempdir()) / "docx_page1_probe.ps1"
    ps.write_text(PROBE_PS, encoding="utf-8")
    last = ""
    for _ in range(tries):   # Word occasionally returns an empty layout (busy COM server): ask again
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps), "-In", str(docx_path)],
                           capture_output=True, encoding="utf-8", errors="replace", timeout=900)
        txt = (r.stdout or "").strip()
        if txt.startswith("{"):
            out = json.loads(txt)
            if out.get("paras") and out.get("pages"):
                return out
        last = (r.stderr or txt)[:300]
    raise RuntimeError(f"Word probe failed {tries} times: {last}")


def _text(el) -> str:
    return "".join(x.text or "" for x in el.iter(qn("w:t")))


def _wide_floats(body):
    out = []
    for t in body.iterchildren(qn("w:tbl")):
        pp = t.find(f"{qn('w:tblPr')}/{qn('w:tblpPr')}")
        if pp is not None and pp.get(qn("w:tblpXSpec")) == "center":
            out.append(t)
    return out


def _para_index(body, key: str, after: int = -1) -> int:
    kids = list(body)
    for i, el in enumerate(kids):
        if i > after and el.tag == qn("w:p") and _norm(_text(el)) == key:
            return i
    return -1


def fix(docx_path: Path, log: list[str] | None = None) -> dict:
    """Place the wide floats one by one, in source order, at the top of a page. Returns the final probe."""
    log = log if log is not None else []
    docx_path = Path(docx_path)
    work = Path(tempfile.mkdtemp(prefix="docx_floats_"))
    cur = work / "cur.docx"
    shutil.copyfile(docx_path, cur)
    doc = docx.Document(str(cur))
    body = doc.element.body
    # Paragraphs are matched by position: Word's body paragraphs (outside tables) and the body-level w:p elements come in the
    # same order, and moving a float (a w:tbl) never changes that order. Text matching failed on paragraphs that start
    # with inline math (Word's text includes it, python-docx's does not).
    def body_ps(b):
        return [el for el in b if el.tag == qn("w:p")]
    order = []                                        # (float key, position of the body paragraph just before it)
    for t in _wide_floats(body):
        prev = t.getprevious()
        while prev is not None and prev.tag != qn("w:p"):
            prev = prev.getprevious()
        order.append((_norm(_text(t)), body_ps(body).index(prev) if prev is not None else 0))
    used_pages: set[int] = set()
    for k, (key, src_ord) in enumerate(order):
        # park this float and every later one at the end, so the layout up to here is final
        doc = docx.Document(str(cur))
        body = doc.element.body
        sect = body.find(qn("w:sectPr"))
        for t in _wide_floats(body):
            if _norm(_text(t)) in {o[0] for o in order[k:]}:
                body.remove(t)
                sect.addprevious(t)
        parked = work / f"park{k}.docx"
        doc.save(str(parked))
        pr = probe(parked)
        doc = docx.Document(str(parked))
        body = doc.element.body
        xps = body_ps(body)
        wps = pr["paras"]
        # Word adds one implicit empty paragraph after a table that ends the document (the parked floats): ignore it
        if len(wps) - len(xps) not in (0, 1):
            raise RuntimeError(f"wide floats: Word reports {len(wps)} body paragraphs, the file has {len(xps)}")
        wps = wps[:len(xps)]
        src_page = int(wps[src_ord]["page"])
        target = max(src_page, 2)
        while target in used_pages:
            target += 1
        # anchor: the first paragraph that starts on the target page (the float then sits at its top, text below).
        # Each placement is checked in Word; some anchors (for example between items of a numbered list) break Word's
        # layout, so the next paragraph is tried.
        js = [n for n, p in enumerate(wps) if int(p["page"]) >= target][:8]
        if not js:
            raise RuntimeError(f"wide floats: no paragraph on page {target} for {key[:24]!r}")
        placed = None
        for j in js:
            doc = docx.Document(str(parked))
            body = doc.element.body
            xps = body_ps(body)
            tbl = next(t for t in _wide_floats(body) if _norm(_text(t)) == key)
            body.remove(tbl)
            xps[j].addprevious(tbl)
            trial = work / f"trial{k}_{j}.docx"
            doc.save(str(trial))
            try:
                pt = probe(trial, tries=2)
            except RuntimeError:
                continue
            now = next((int(f["page"]) for f in pt["floats"] if _norm(f["text"]) == key), 0)
            if pt["pages"] > 1 and now >= target:
                placed = (j, now)
                shutil.copyfile(trial, cur)
                break
        if placed is None:
            raise RuntimeError(f"wide floats: no working anchor on page {target} for {key[:24]!r}")
        used_pages.add(placed[1])
        log.append(f"wide float {key[:24]!r}: top of page {placed[1]} (source text on page {src_page})")
    pr = probe(cur)
    pages = {}
    for f in pr["floats"]:
        if _norm(f["text"]) in {o[0] for o in order}:
            pages.setdefault(int(f["page"]), []).append(f["text"])
    bad = [p for p, v in pages.items() if p == 1 or len(v) > 1]
    if bad:
        raise RuntimeError(f"wide floats: rule broken on page(s) {bad} after placement")
    shutil.copyfile(cur, docx_path)
    return pr
