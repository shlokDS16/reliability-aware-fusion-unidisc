"""Rerunnable LaTeX -> DOCX converter for Paper 2 (IEEE TNNLS).

    python paper2-tnnls/scripts/make_docx.py                 # anonymous build: docx/Paper2_TNNLS_manuscript.docx (+ supplement)
    python paper2-tnnls/scripts/make_docx.py --camera        # camera-ready switch (\\anonfalse), authors and links shown
    python paper2-tnnls/scripts/make_docx.py --main-only     # skip the supplement
    python paper2-tnnls/scripts/make_docx.py --render        # also export the DOCX to PDF through Word (render check)

Run `latexmk -pdf main.tex` first: the converter reads main.aux (citation numbers, cross-reference text), main.bbl
(reference list) and compares the result with main.pdf. Needs: pandoc >= 3.1 on PATH, python-docx (system python),
pdftotext (poppler/MiKTeX) for the verification step. Nothing in the paper sources is modified.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import docx_ast  # noqa: E402
import docx_post  # noqa: E402
import docx_tex  # noqa: E402

TEMPLATE_REL = Path("research/paper2/tnnls/ieee-template/IEEE-Transactions-Word-template-2024-06-12.docx")
HEADER_TEXT = "IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS"


def find_template(src: Path, given: str | None) -> Path:
    if given:
        return Path(given)
    for base in [src, *src.parents]:
        cand = base / TEMPLATE_REL
        if cand.exists():
            return cand
    raise SystemExit("IEEE Word template not found; pass --template")


def convert(tex: Path, aux: Path, bbl: Path | None, out: Path, template: Path, anon: bool, unit: str,
            keep: Path | None) -> dict:
    stale = [p.name for p in [tex, *tex.parent.glob("sections/*.tex"), *tex.parent.glob("tables/*.tex"), *tex.parent.glob("back/*.tex")]
             if p.exists() and p.stat().st_mtime > aux.stat().st_mtime + 2]
    prep = docx_tex.Preprocessor(tex, aux, bbl, anon=anon, unit=unit)
    if stale:
        prep.warn(f"{aux.name} is older than {len(stale)} source file(s) ({', '.join(stale[:4])}...): run latexmk -pdf first, "
                  "or cross-reference numbers and the PDF comparison may be stale")
    res = prep.run()
    work = Path(keep) if keep else Path(tempfile.mkdtemp(prefix="docx_work_"))
    work.mkdir(parents=True, exist_ok=True)
    doc, err = docx_ast.run_pandoc_json(res["latex"], work)
    (work / "preprocessed.tex").write_text(res["latex"], encoding="utf-8")
    rs = docx_ast.Restructurer(res, doc)
    new = rs.run()
    raw = work / "raw.docx"
    err2 = docx_ast.run_pandoc_docx(new, template, raw, work)
    poster = docx_post.Poster(raw, rs.tbl_specs, anon, prep.meta["title"] and docx_ast.itext(rs.frag_inlines("title")), unit)
    log = poster.run(out, HEADER_TEXT if unit == "main" else HEADER_TEXT + " (SUPPLEMENTARY MATERIAL)")
    (work / "tbl_specs.json").write_text(json.dumps(rs.tbl_specs, indent=1), encoding="utf-8")
    return {"warnings": prep.warnings + rs.warnings + log + ([err.strip()] if err.strip() else []) +
            ([err2.strip()] if err2.strip() else []), "work": work}


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", default=str(HERE.parent), help="paper2-tnnls directory (default: parent of scripts/)")
    ap.add_argument("--out", default=None, help="output directory (default: <src>/docx)")
    ap.add_argument("--template", default=None)
    ap.add_argument("--camera", action="store_true", help="non-anonymous build (\\anonfalse)")
    ap.add_argument("--main-only", action="store_true")
    ap.add_argument("--keep", default=None, help="directory for intermediate files (pandoc input/AST/raw docx)")
    ap.add_argument("--no-verify", action="store_true")
    ap.add_argument("--render", action="store_true", help="export DOCX to PDF with Word (COM) for a visual check")
    ap.add_argument("--no-page1", action="store_true", help="skip the Word pass that keeps wide floats off page 1")
    a = ap.parse_args()
    src = Path(a.src).resolve()
    out = Path(a.out).resolve() if a.out else src / "docx"
    out.mkdir(parents=True, exist_ok=True)
    template = find_template(src, a.template)
    anon = not a.camera
    suffix = "" if anon else "_camera"
    results = {}
    jobs = [("manuscript", src / "main.tex", src / "main.aux", src / "main.bbl", "main", src / "main.pdf")]
    sup = src / "supplement" / "supplement.tex"
    if not a.main_only and sup.exists():
        jobs.append(("supplement", sup, sup.with_suffix(".aux"), None, "supplement", sup.with_suffix(".pdf")))
    for name, tex, aux, bbl, unit, pdf in jobs:
        if not aux.exists():
            print(f"[{name}] {aux.name} missing: run latexmk -pdf first", file=sys.stderr)
            continue
        dst = out / f"Paper2_TNNLS_{name}{suffix}.docx"
        keep = Path(a.keep) / name if a.keep else None
        r = convert(tex, aux, bbl, dst, template, anon, unit, keep)
        print(f"[{name}] wrote {dst}")
        if unit == "main" and not a.no_page1:
            import docx_page1
            try:
                fin = docx_page1.fix(dst, r["warnings"])
                print(f"[{name}] Word layout: {fin['pages']} pages; floats by page: "
                      + ", ".join(f"{f['text'][:12]!r}->{f['page']}" for f in fin["floats"]))
            except Exception as e:  # noqa: BLE001
                print(f"  ERROR page-1 float check failed ({e}); a wide figure may sit above the title in Word", file=sys.stderr)
        for w in r["warnings"]:
            print(f"  warning: {w}")
        results[name] = (dst, pdf)
    if not a.no_verify:
        import docx_verify
        for name, (dst, pdf) in results.items():
            docx_verify.report(dst, pdf, out / f"verify_{name}{suffix}.txt")
    if a.render:
        import docx_verify
        for name, (dst, pdf) in results.items():
            docx_verify.render_with_word(dst, dst.with_suffix(".word.pdf"))


if __name__ == "__main__":
    main()
