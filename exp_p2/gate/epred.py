"""E-pred (SAP Addendum A2 AD.3, as DEMOTED by Addendum A2b AB.3): out-of-sample sign prediction from Proposition 4 (spec v2 5.3, general form with mu_c not 0). Secondary, descriptive.
CPU only; no model. Two stages with a freeze between them.

    # after M3 (family.json committed) and the fit chunk runs/P2-GATE-EPRED-FIT (GATE flags on the 100 headroom items), BEFORE the first M4 item:
    python -m exp_p2.gate.epred fit --run-id P2-GATE-M3 --fit-run P2-GATE-EPRED-FIT [--boot 10000] [--audit-record PATH]
        -> runs/P2-GATE-EPRED-FIT/epred_frozen.json   (write-once; the fit-code SHA-256 and every input hash are inside)
    # after M4, family P and PS analysed (analysis.json exists), AD.12 step 5:
    python -m exp_p2.gate.epred score --frozen runs/P2-GATE-EPRED-FIT/epred_frozen.json --run-id P2-GATE-M4 --family-run P2-GATE-M3
        -> runs/P2-GATE-M4/epred_score.json
    python -m exp_p2.gate.epred selftest

What it is (AB.3). Per cell c in P1, P2, P3 (only those with an operating point), PS1 (patch), PS2 (swap): s_c = sign(SNR_after - SNR_before) of the additive image-direction statistic, from the
corrected Prop. 4 with the inputs rho, mu, sigma^2, mu_c, sigma_c^2, alpha_obs, beta_obs measured POOLED over the 100 headroom items at token level (classes from the changed-code labels Z; GATE flags
from the fit chunk). The sign does not depend on the number of tokens m. s_c is written to epred_frozen.json together with a stability share (the share of 10,000 headroom-ITEM bootstrap
resamples with the same sign); the stability figure never changes s_c. The observed sign is o_c = sign(b_c - c_cnt) of GATE-M versus none on the binary Y (under every n-rule, R3 included), and
o_c* = the same sign only where the 95 percent paired-bootstrap interval of the net accuracy difference excludes 0, else none. Reported: A = number of agreements out of K_eval with a Clopper-Pearson
95 percent interval, SEPARATELY for the P cells (K <= 3) and for the PS cells (labelled foregone), never pooled with the suite cells; the rival rules "always +" and "- for P, + for PS".
NO test, NO p-value, NO alpha (family E is withdrawn, AB.3 item 1). Allowed wording only: "the sign of the plug-in SNR change agreed with the sign of the net accuracy difference in A of K_eval
cells (CI)"; nobody writes that Prop. 4 "predicted", "explains" or "is supported" (AB.3 item 4), and no P result is called predicted, explained or caused (AB.1). The spec 5.3 refutation rule stays:
a plug-in sign that disagrees with a cell whose observed interval excludes 0 refutes the independent-token model for that cell.
The fit code lives in `epred_fit.py` (hashed with `theory.py` and its tests into epred_frozen.json); this module loads, scores and runs the CLI.
`reachability()` records what the withdrawn AD.3 binomial could have reached (K_eval = 5, A = 5 gives 0.03125; K <= 4 never rejects); it is used by the self-test and printed as a note, not as a result."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from exp_p2.gate import config, seeds                                      # noqa: E402
from exp_p2.gate import epred_fit as _fit                                  # noqa: E402
from exp_p2.gate.epred_fit import (CELLS, LABEL, N_BOOT, P_CELLS, P_CORRUPTION, PS_CELLS, PS_KEY, SEED_NAME, epred_fit, reachability, seed_fingerprint,   # noqa: E402,F401
                                   selftest as fit_selftest, sign_of_gating)

A0 = f"gate{config.ALPHA_PRIMARY:g}"
FIT_RUN_ID = "P2-GATE-EPRED-FIT"
FROZEN_NAME = "epred_frozen.json"
FIT_CODE_FILES = ("exp_p2/gate/epred_fit.py", "exp_p2/gate/theory.py", "tests/exp_p2/test_gate_epred_fit.py")   # the fit code, the Prop. 4 sign function and its self-test (AB.3 item 5); seeds.py enters as a fingerprint
ALLOWED_WORDING = "the sign of the plug-in SNR change agreed with the sign of the net accuracy difference in {A} of {K} cells (95 percent Clopper-Pearson interval [{lo:.3f}, {hi:.3f}])"


def selftest() -> dict:
    """The fit-code self-test (epred_fit.selftest, part of the frozen code) plus the score-side checks (the o_c* rule)."""
    ok = dict(fit_selftest())
    ok.pop("all_ok", None)
    ok["o_star_rule"] = bool(_o_star(1, [0.01, 0.2]) == 1 and _o_star(1, [-0.01, 0.2]) is None and _o_star(-1, [-0.3, -0.02]) == -1 and _o_star(1, [-0.3, -0.02]) is None)
    ok["all_ok"] = bool(all(ok.values()))
    return ok


def _sgn(x) -> int:
    return int(np.sign(x))


def _o_star(o: int, ci95) -> int | None:
    """o_c*: the observed sign only where the 95 percent paired-bootstrap interval of the net accuracy difference excludes 0 (and lies on the side of o), else None."""
    if ci95 is None or len(ci95) != 2 or not all(x is not None and math.isfinite(x) for x in ci95):
        return None
    lo, hi = ci95
    side = 1 if lo > 0 else (-1 if hi < 0 else 0)
    return side if (side != 0 and side == o) else None


RIVALS = {"always +": lambda c: 1, "- for P cells, + for PS cells": lambda c: -1 if c in P_CELLS else 1}


def _agg(cells: dict, names) -> dict:
    """A of K_eval with a Clopper-Pearson interval for the cells `names`; cells without s_c or without o_c are excluded and counted. The rival rules are scored on the same evaluable cells."""
    from exp_p2.gate import stats
    ev = {c: cells[c] for c in names if c in cells and cells[c]["evaluable"]}
    excl = {c: cells[c]["excluded_reason"] for c in names if c in cells and not cells[c]["evaluable"]}
    A, K = sum(1 for v in ev.values() if v["agree"]), len(ev)
    lo, hi = stats.clopper_pearson(A, K, 0.95) if K else (float("nan"), float("nan"))
    star = {c: v for c, v in ev.items() if v["o_star"] is not None}
    return dict(A=A, K_eval=K, cp95=[lo, hi], cells_evaluable=sorted(ev), excluded=excl,
                agreement_where_observed_interval_excludes_0=dict(A=sum(1 for v in star.values() if v["s"] == v["o_star"]), K=len(star), cells=sorted(star), note="descriptive column o_c*"),
                rivals={name: dict(A=sum(1 for c, v in ev.items() if fn(c) == v["o"]), K_eval=K) for name, fn in RIVALS.items()},
                sentence=(ALLOWED_WORDING.format(A=A, K=K, lo=lo, hi=hi) if K else "no cell is evaluable"), reachability_of_withdrawn_test=reachability(K))


def epred_score(frozen: dict, p_cells: dict) -> dict:
    """SAP AD.13 `epred_score(frozen, p_cells)` as AB.3 reshapes it. `frozen`: the content of epred_frozen.json (or `epred_fit` output): cells[c]["sign"]. `p_cells[c]`: the test of cell c on the
    test fold: b, c (counts of GATE-M right/none wrong and the reverse, on the binary Y), ci95 = 95 percent paired-bootstrap interval of the net accuracy difference ((b - c)/n), optionally n.
    Returns the table of s_c, o_c, o_c*, the agreement counts A of K_eval separately for the P cells and the PS cells (never pooled, never with the suite), the rival rules and the spec 5.3 refutation
    flags. No p-value, no test (AB.3). A cell without a committed sign, without a test in `p_cells`, or with b = c_cnt has no evaluable pair: excluded and counted."""
    fcells = frozen["cells"]
    unknown = sorted(set(p_cells) - set(CELLS))
    if unknown:
        raise ValueError(f"unknown cell(s) in p_cells: {unknown}")
    cells = {}
    for c in CELLS:
        s = fcells.get(c, {}).get("sign")
        pc = p_cells.get(c)
        row = dict(cell=c, s=s, s_text=fcells.get(c, {}).get("sign_text"), stability_share_same_sign=(fcells.get(c, {}).get("stability") or {}).get("share_same_sign"), group="P" if c in P_CELLS else "PS")
        if pc is None:
            row.update(o=None, o_star=None, b=None, c_cnt=None, evaluable=False, agree=None, excluded_reason="no test for this cell on the test fold (not run or no operating point)")
        else:
            b, cc = int(pc["b"]), int(pc["c"])
            o = _sgn(b - cc)
            row.update(b=b, c_cnt=cc, n=pc.get("n"), net_difference=pc.get("net_difference"), ci95=list(pc["ci95"]) if pc.get("ci95") is not None else None, o=o if o != 0 else None,
                       o_star=_o_star(o, pc.get("ci95")) if o != 0 else None)
            if s not in (1, -1):
                row.update(evaluable=False, agree=None, excluded_reason=("no committed sign: " + str((fcells.get(c) or {}).get("reason_no_sign") or "cell absent from epred_frozen.json")))
            elif o == 0:
                row.update(evaluable=False, agree=None, excluded_reason="b = c_cnt: no observed sign (counted, excluded)")
            else:
                row.update(evaluable=True, agree=bool(s == o), excluded_reason=None)
        cells[c] = row
    grp_P, grp_PS = _agg(cells, P_CELLS), _agg(cells, PS_CELLS)
    grp_PS["label"] = "foregone: patch and swap are expected to be detected and helped (AB.3 item 2); not evidence for the P cells"
    refuted = {c: bool(v["evaluable"] and v["o_star"] is not None and v["s"] != v["o_star"]) for c, v in cells.items()}
    return dict(cells=cells, P=grp_P, PS=grp_PS, refutation_rule_met_for_cells=sorted(c for c, r in refuted.items() if r),
                refutation_note="spec 5.3 / AB.3 item 4: a committed sign that disagrees with a cell whose observed 95 percent interval of the net accuracy difference excludes 0 refutes the independent-token model for that cell",
                formal_test=None, formal_test_note="no test, no p-value, no alpha: family E is withdrawn (AB.3 item 1)", label=LABEL,
                observed_sign_definition="o_c = sign(b_c - c_cnt) on the binary Y of GATE-M versus none under every n-rule, R3 included; o_c* only where the 95 percent paired-bootstrap interval excludes 0 (AB.3 item 3)")


def observed_cells_from_rows(rows: list[dict], family, *, n_boot: int = N_BOOT) -> dict:
    """The test of each cell on the M4 rows, whatever the n-rule: b, c_cnt, n and the 95 percent paired-bootstrap interval of the net accuracy difference of GATE-M versus none on the binary Y.
    The interval uses the seed of the cell's own family test (`primary` for P cells, `ps_family` for PS cells) with the same arrays, so it is the interval printed by `analysis_m4` for that test."""
    import numpy as _np
    from exp_p2.gate import report
    from exp_p2.gate.edec import cell_keys
    keys = cell_keys(family)
    out = {}
    for c in CELLS:
        k = keys[c]
        if k is None or not any(k in r.get("conds", {}) for r in rows):
            continue

        def arm(arm_name):
            return _np.array([r["conds"][k]["img"][arm_name]["y"] if k in r.get("conds", {}) and arm_name in r["conds"][k].get("img", {}) else _np.nan for r in rows], float)
        rep = report.report_test(arm(A0), arm("none"), n_boot=n_boot, seed=seeds.seed_for("primary" if c in P_CELLS else "ps_family"))
        out[c] = dict(b=rep["b"], c=rep["c"], n=rep["n"], net_difference=rep["delta"], ci95=rep["ci95"], key=k)
    return out


# ------------------------------------------------------------------------------------------------ hashes, git, files
def sha256_file(path: Path) -> dict:
    b = Path(path).read_bytes()
    lf = b.replace(b"\r\n", b"\n")
    return dict(sha256=hashlib.sha256(b).hexdigest(), sha256_lf=hashlib.sha256(lf).hexdigest(), git_blob_sha1=hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest(), bytes=len(b))


def fit_code_hashes(root: Path = ROOT, files=FIT_CODE_FILES) -> dict:
    """SHA-256 of the fit code (working-tree bytes, and with CRLF normalised to LF, as the SAP pins do) plus the git blob hash of the LF form, for each file of FIT_CODE_FILES."""
    return {f: sha256_file(Path(root) / f) for f in files}


def git_status_lines(paths, repo: Path = ROOT) -> list[str]:
    """`git status --porcelain -- paths`: any line is an uncommitted or untracked change. Fails closed (one error line) if git cannot be run."""
    r = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", *paths], capture_output=True, text=True)
    if r.returncode != 0:
        return [f"git status failed: {r.stderr.strip()[:200]}"]
    return [l for l in r.stdout.splitlines() if l.strip()]


def git_head(repo: Path = ROOT) -> str | None:
    r = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def git_commit_time(path: str, repo: Path = ROOT) -> int | None:
    """Committer time (epoch seconds) of the last commit that touched `path`, None if it was never committed."""
    r = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%ct", "--", path], capture_output=True, text=True)
    return int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip() else None


def write_once_exclusive(path: Path, text: str) -> None:
    """Create `path` with `text`; refuse if it exists (write-once, AB.3 item 5). No --force exists for this file: a changed freeze is a new, dated addendum, not an overwrite."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"{path} already exists; epred_frozen.json is write-once (SAP AB.3, AB.8: a freeze after the first M4 item invalidates E-pred)")
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    tmp.write_text(text, encoding="utf8")
    try:
        os.link(tmp, path)                                                    # fails if `path` appeared meanwhile
    except OSError as e:
        raise FileExistsError(f"could not create {path} exclusively: {e}") from e
    finally:
        tmp.unlink(missing_ok=True)


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        return float(x) if math.isfinite(float(x)) else None
    if isinstance(x, (np.bool_,)):
        return bool(x)
    return x


# ------------------------------------------------------------------------------------------------ loading the fit fold from runs
def load_fit_inputs(m3_dir: Path, fit_dir: Path, family: dict, n_expected: int | None = None) -> tuple[dict, dict, dict, dict]:
    """Headroom tokens and flags from disk. Contract for the fit chunk (runs/P2-GATE-EPRED-FIT/arrays/item{idx:04d}.npz, one per M3 item, and its items.jsonl):
        {key}_flag   bool[1024]   GATE-M flags (alpha 0.05, frozen M2 threshold, mask seed 20261029) on the corrupted headroom image of every P cell with an operating point (key from family.json)
        {name}_codes int16[1024], {name}_delta float32[1024], {name}_flag bool[1024]   for the PS cells patch and swap (codes made with corruptions.token_rng(SEED_GATE, gid, name) as in M4;
                                                                                        delta = Lambda^{c+}[codes] - Lambda^{c-}[codes])
    The P cells' Delta and codes are read from the M3 arrays ({key}_delta, {key}_codes, clean). Z = codes != clean. Returns (tokens, flags, absent, files) where `files` lists every path read."""
    from exp_p2 import common
    m3_dir, fit_dir = Path(m3_dir), Path(fit_dir)
    rows = {}
    for r in common.read_jsonl(m3_dir / "items.jsonl"):
        rows.setdefault(r["idx"], r)
    idxs = sorted(rows)
    if n_expected is not None and len(idxs) < n_expected:
        raise ValueError(f"only {len(idxs)} headroom items in {m3_dir}; the fit needs {n_expected}")
    fit_rows = {}
    if (fit_dir / "items.jsonl").exists():
        for r in common.read_jsonl(fit_dir / "items.jsonl"):
            fit_rows.setdefault(r["idx"], r)
    missing = [i for i in idxs if i not in fit_rows]
    if missing:
        raise ValueError(f"the fit chunk has not finished {len(missing)} of {len(idxs)} headroom items (first missing idx {missing[:5]}); a partial fit is refused")
    keys = {}
    for f in family["family"]:
        keys[f"P{config.REALISTIC.index(f['corruption']) + 1}"] = f["key"]
    tokens, flags, absent, files = {}, {}, {}, []
    for c in P_CELLS:
        if c not in keys:
            absent[c] = "no operating point in family.json"
    m3a, fita = {}, {}
    for i in idxs:
        pm, pf = m3_dir / "arrays" / f"item{i:04d}.npz", fit_dir / "arrays" / f"item{i:04d}.npz"
        m3a[i], fita[i] = np.load(pm), np.load(pf)
        files += [pm, pf]
    for c in CELLS:
        if c in absent:
            continue
        key = keys[c] if c in P_CELLS else PS_KEY[c]
        have = [f"{key}_flag" in fita[i].files for i in idxs]
        if not any(have):
            absent[c] = f"the fit chunk wrote no {key}_flag (cell not run)"
            continue
        if not all(have):
            raise ValueError(f"cell {c}: {key}_flag is missing for some headroom items")
        tk, fl = [], []
        for i in idxs:
            clean = m3a[i]["clean"]
            if c in P_CELLS:
                codes, delta = m3a[i][f"{key}_codes"], m3a[i][f"{key}_delta"]
            else:
                codes, delta = fita[i][f"{key}_codes"], fita[i][f"{key}_delta"]
            tk.append(dict(delta=np.asarray(delta, np.float64), z=np.asarray(codes) != np.asarray(clean)))
            fl.append(np.asarray(fita[i][f"{key}_flag"], bool))
        tokens[c], flags[c] = tk, fl
    return tokens, flags, absent, files


def combined_hash(paths) -> dict:
    h = hashlib.sha256()
    for p in sorted(str(x) for x in paths):
        h.update(p.replace("\\", "/").split("/")[-1].encode() + hashlib.sha256(Path(p).read_bytes()).digest())
    return dict(sha256_of_name_and_file_hashes=h.hexdigest(), n_files=len(list(paths)))


def check_fit_fold_disjoint(folds: dict, m3_rows: list[dict]) -> dict:
    """AD.3: the headroom ids are disjoint from the test ids (folds.json test and test_ext), and from cal; the M3 rows are exactly folds.json 'head' items (by image id)."""
    head = {it["image_id"] for it in folds["head"]}
    test = {it["image_id"] for k in ("test", "test_ext") for it in folds.get(k, [])}
    cal = {it["image_id"] for it in folds.get("cal", [])}
    if head & test:
        raise AssertionError(f"headroom and test folds share image ids: {sorted(head & test)[:5]}")
    if head & cal:
        raise AssertionError(f"headroom and calibration folds share image ids: {sorted(head & cal)[:5]}")
    used = {r["image_id"] for r in m3_rows}
    if not used <= head:
        raise AssertionError(f"M3 rows use image ids outside folds.json 'head': {sorted(used - head)[:5]}")
    return dict(n_head=len(head), n_used=len(used), n_test=len(test), disjoint_from_test=True, disjoint_from_cal=True, used_subset_of_head=True,
                head_image_ids_sha256=hashlib.sha256(json.dumps(sorted(used)).encode()).hexdigest())


# ------------------------------------------------------------------------------------------------ CLI
def build_frozen(fit: dict, *, run_id: str, fit_run: str, family_path: Path, m3_items: Path, folds_path: Path, fit_files, n_boot: int, st: dict, folds_check: dict,
                 allow_dirty: bool, dirty: list[str], audit_record: Path | None, root: Path = ROOT, extra_inputs: dict | None = None) -> dict:
    hashes = fit_code_hashes(root)
    inputs = {"family.json": sha256_file(family_path), "m3_items.jsonl": sha256_file(m3_items), "folds.json": sha256_file(folds_path), "arrays": combined_hash(fit_files)}
    inputs.update(extra_inputs or {})
    audit = None
    if audit_record is not None:
        audit = dict(path=str(audit_record), **sha256_file(audit_record))
    frozen = dict(kind="epred_frozen", version=1, created=time.strftime("%Y-%m-%dT%H:%M:%S%z"), spec="SAP-GATE-2026-10-28 AD.3 as demoted by AB.3; spec v2 5.3 (Prop. 4, general form)",
                  run_id=run_id, fit_run=fit_run, fit_fold="folds.json 'head' (the headroom items)", cells=fit["cells"], absent_cells=fit["absent"], s_c=fit["s_c"], n_boot=fit["n_boot"], seed=fit["seed"],
                  seeds_meta=seeds.meta(), method=fit["method"], label=LABEL, fit_fold_check=folds_check, inputs=inputs,
                  fit_code=dict(files=hashes, seed_fingerprint=seed_fingerprint(), git_head=git_head(root), note="sha256 = working-tree bytes; sha256_lf = CRLF normalised to LF; git_blob_sha1 = git blob id of the LF form. Not edited after this freeze (AB.3 item 5)."),
                  selftest=st, audit_record=audit, allow_dirty=bool(allow_dirty), dirty_files_at_freeze=dirty,
                  reminder="committed before the first M4 item (AB.3 item 5); no decision depends on this file or on the fit chunk (AB.3 item 6)")
    return _jsonable(frozen)


def verify_frozen(frozen: dict, root: Path = ROOT) -> list[str]:
    """Problems found when the current fit code is compared with the hashes inside the frozen file (empty = the same code). Compared on sha256_lf."""
    cur = fit_code_hashes(root)
    bad = []
    for f, h in frozen.get("fit_code", {}).get("files", {}).items():
        if f not in cur:
            bad.append(f"{f}: not in the current FIT_CODE_FILES")
        elif cur[f]["sha256_lf"] != h["sha256_lf"]:
            bad.append(f"{f}: sha256 (LF) {cur[f]['sha256_lf'][:12]} != frozen {h['sha256_lf'][:12]}")
    if set(frozen.get("fit_code", {}).get("files", {})) != set(cur):
        bad.append("the file list differs from FIT_CODE_FILES")
    fp = frozen.get("fit_code", {}).get("seed_fingerprint")
    if fp != _jsonable(seed_fingerprint()):
        bad.append("the seed fingerprint (root seed, analysis names up to prop4_plugin, child state) differs from the frozen one")
    return bad


def cmd_fit(a) -> int:
    from exp_p2 import common
    st = selftest()
    if not st["all_ok"]:
        print("SELFTEST FAILED:", st, file=sys.stderr)
        return 2
    runs = Path(a.runs_dir)
    m3, fit_dir, m4 = runs / a.run_id, runs / a.fit_run, runs / a.m4_run
    out = fit_dir / FROZEN_NAME
    if out.exists():
        print(f"STOP: {out} exists; it is write-once (AB.3 item 5). A different freeze needs a new dated addendum.", file=sys.stderr)
        return 2
    if (m4 / "items.jsonl").exists() and (m4 / "items.jsonl").stat().st_size > 0:
        print(f"STOP: {m4 / 'items.jsonl'} already has M4 items; epred_frozen.json must exist before the first M4 item (AB.3 item 5, AB.8). E-pred is 'not run'.", file=sys.stderr)
        return 3
    fam_path = m3 / "family.json"
    if not fam_path.exists():
        print(f"STOP: {fam_path} missing; E-pred is fitted only after family.json is committed (AD.3, AD.12)", file=sys.stderr)
        return 2
    rel_fam = os.path.relpath(fam_path, ROOT) if str(fam_path).startswith(str(ROOT)) else None
    dirty = []
    if not a.skip_git_checks:
        dirty = git_status_lines(list(FIT_CODE_FILES) + ([rel_fam] if rel_fam else []))
        if dirty and not a.allow_dirty:
            print("STOP: the fit code and family.json must be committed (and gate-auditor-checked) before the fit chunk is read (AB.3 item 5):" + "".join("\n  " + l for l in dirty), file=sys.stderr)
            return 11
    family = json.loads(fam_path.read_text(encoding="utf8"))
    if family.get("endpoint") != "d":
        print("STOP: family.json does not record endpoint d", file=sys.stderr)
        return 2
    folds_path = Path(a.folds) if a.folds else runs / "P2-GATE-FOLDS" / "folds.json"
    folds = json.loads(folds_path.read_text(encoding="utf8"))
    m3_rows = common.read_jsonl(m3 / "items.jsonl")
    check = check_fit_fold_disjoint(folds, m3_rows)
    eff = m3 / "effective_n.json"
    n_exp = a.min_items if a.min_items is not None else (json.loads(eff.read_text(encoding="utf8"))["effective"] if eff.exists() else config.N_HEAD)
    tokens, flags, absent, files = load_fit_inputs(m3, fit_dir, family, n_exp)
    fit = epred_fit(tokens, flags, n_boot=a.boot, absent=absent)
    extra = {}
    thr = runs / "P2-GATE-M2" / "threshold.json"
    if thr.exists():
        extra["m2_threshold.json"] = sha256_file(thr)
    for nm in ("config.json",):
        if (fit_dir / nm).exists():
            extra[f"fit_run_{nm}"] = sha256_file(fit_dir / nm)
    extra["fit_items.jsonl"] = sha256_file(fit_dir / "items.jsonl")
    frozen = build_frozen(fit, run_id=a.run_id, fit_run=a.fit_run, family_path=fam_path, m3_items=m3 / "items.jsonl", folds_path=folds_path, fit_files=files, n_boot=a.boot, st=st, folds_check=check,
                          allow_dirty=a.allow_dirty, dirty=dirty, audit_record=Path(a.audit_record) if a.audit_record else None, extra_inputs=extra)
    write_once_exclusive(out, json.dumps(frozen, indent=1, allow_nan=False))
    print(json.dumps(dict(out=str(out), s_c=frozen["s_c"], absent=frozen["absent_cells"], stability={c: v["stability"]["share_same_sign"] for c, v in frozen["cells"].items()},
                          fit_code_sha256_lf={f: h["sha256_lf"][:16] for f, h in frozen["fit_code"]["files"].items()}), indent=1))
    return 0


def cmd_score(a) -> int:
    from exp_p2 import common
    from exp_p2.gate import analysis_m4
    runs = Path(a.runs_dir)
    run_dir = runs / a.run_id
    frozen_path = Path(a.frozen)
    frozen = json.loads(frozen_path.read_text(encoding="utf8"))
    bad = verify_frozen(frozen)
    if bad and not a.ignore_code_mismatch:
        print("STOP: the fit code differs from the frozen hashes (AB.3 item 5):" + "".join("\n  " + b for b in bad), file=sys.stderr)
        return 2
    if not (run_dir / "analysis.json").exists():
        print(f"STOP: {run_dir / 'analysis.json'} missing: E-pred follows family P and PS in the order of analysis (SAP AD.12 step 5)", file=sys.stderr)
        return 3
    order = dict(checked=False)
    chunks = run_dir / "chunks.jsonl"
    if not a.skip_git_checks and chunks.exists():
        starts = [r["t"] for r in common.read_jsonl(chunks) if r.get("event") == "chunk_start" and "t" in r]
        rel = os.path.relpath(frozen_path.resolve(), ROOT) if str(frozen_path.resolve()).startswith(str(ROOT)) else None
        ct = git_commit_time(rel) if rel else None
        order = dict(checked=True, first_m4_chunk_start=min(starts) if starts else None, frozen_commit_time=ct)
        if ct is None or (starts and ct > min(starts)):
            order["violation"] = True
            print(f"STOP: epred_frozen.json was not committed before the first M4 item (committed {ct}, first M4 chunk {min(starts) if starts else None}); E-pred is 'not run' (AB.3 item 5, AB.8)", file=sys.stderr)
            return 3
    fam = json.loads((runs / a.family_run / "family.json").read_text(encoding="utf8"))
    rows, n_dup = analysis_m4.load_items(run_dir)
    p_cells = observed_cells_from_rows(rows, fam["family"], n_boot=a.boot)
    res = epred_score(frozen, p_cells)
    res.update(frozen_file=str(frozen_path), frozen_sha256=sha256_file(frozen_path)["sha256"], fit_code_matches_frozen=not bad, order_check=order, n_items=len(rows), n_duplicates_removed=n_dup,
               allow_partial_in_analysis_json=json.loads((run_dir / "analysis.json").read_text(encoding="utf8")).get("meta", {}).get("allow_partial"), meta=seeds.meta())
    out = Path(a.out) if a.out else run_dir / "epred_score.json"
    out.write_text(json.dumps(_jsonable(res), indent=1, allow_nan=False), encoding="utf8")
    print(json.dumps(dict(out=str(out), P=res["P"]["sentence"], PS=res["PS"]["sentence"], refutation_cells=res["refutation_rule_met_for_cells"]), indent=1))
    return 0


def main(argv=None) -> int:
    from exp_p2 import common
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit", help="freeze the sign predictions from the headroom fold (write-once), before the first M4 item")
    f.add_argument("--run-id", default="P2-GATE-M3", help="the M3 headroom run")
    f.add_argument("--fit-run", default=FIT_RUN_ID, help="the fit chunk run (GATE flags on the headroom items)")
    f.add_argument("--m4-run", default="P2-GATE-M4")
    f.add_argument("--runs-dir", default=str(common.RUNS))
    f.add_argument("--folds", default=None)
    f.add_argument("--boot", type=int, default=N_BOOT)
    f.add_argument("--min-items", type=int, default=None, help="default: effective_n.json of the M3 run, else 100")
    f.add_argument("--audit-record", default=None, help="the gate-auditor's record for the fit code; its SHA-256 is written into the frozen file")
    f.add_argument("--allow-dirty", action="store_true", help="recorded in the frozen file; AB.3 requires committed, audited fit code, so this is for rehearsals only")
    f.add_argument("--skip-git-checks", action="store_true", help="rehearsals on temporary run directories only")
    s = sub.add_parser("score", help="agreement table after M4 (AD.12 step 5)")
    s.add_argument("--frozen", default=str(Path(common.RUNS) / FIT_RUN_ID / FROZEN_NAME))
    s.add_argument("--run-id", default="P2-GATE-M4")
    s.add_argument("--family-run", default="P2-GATE-M3")
    s.add_argument("--runs-dir", default=str(common.RUNS))
    s.add_argument("--boot", type=int, default=N_BOOT)
    s.add_argument("--out", default=None)
    s.add_argument("--ignore-code-mismatch", action="store_true")
    s.add_argument("--skip-git-checks", action="store_true")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        st = selftest()
        print(json.dumps(st))
        return 0 if st["all_ok"] else 2
    return cmd_fit(a) if a.cmd == "fit" else cmd_score(a)


if __name__ == "__main__":
    sys.exit(main())
