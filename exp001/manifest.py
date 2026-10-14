"""Build runs/EXP-001/gates/manifest.json: SHA-256 of every frozen list and rule of Appendix B, code hashes, pins and versions
(card 9 items 10 and 13, 3 item 7, 15). Re-run after any pin changes; the manifest is overwritten with a new generation number and
the previous one is kept as manifest.prev-<n>.json.

usage (eval venv):  python -m exp001.manifest
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AN = ROOT / "analysis" / "EXP-001"
OUT = ROOT / "runs" / "EXP-001" / "gates"
GEN_PY = Path(r"C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv\Scripts\python.exe")
EVAL_PY = Path(r"C:\Users\Shlok\Downloads\Multi-Modality Language model\.venv-eval\Scripts\python.exe")
HF_EVAL = Path(r"C:\Users\Shlok\.cache\dlm_dl\hf_eval")

FROZEN_APPENDIX_B = ["prefix_rule.py", "caption_end.py", "nonvisual_nouns.txt", "spatial_words.txt", "debris_patterns.txt",
                     "vlm_prompt.txt", "vlm_presence_prompt.txt", "completion.py", "ha_source.py"]
ANALYSIS_CODE = ["metrics.py", "hastats.py", "coco_draw.py", "evalmodels.py", "gates_eval.py", "frozen_analysis.py"]
GEN_CODE = ["config.py", "rng.py", "plan.py", "network.py", "sampler.py", "estimator.py", "probe_run.py", "unidisc_net.py", "runtools.py",
            "gate_gen.py", "gate_driver.py", "frozen.py", "manifest.py"]


def sha(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=str(ROOT)).stdout.strip()
    except Exception as e:
        return f"error: {e}"


def versions(py, pkgs):
    code = "import importlib.metadata as m,json;o={}\nfor p in %r:\n  try: o[p]=m.version(p)\n  except Exception: o[p]=None\nprint(json.dumps(o))" % (pkgs,)
    try:
        return json.loads(sh([str(py), "-c", code]))
    except Exception:
        return None


def model_pin(repo_dirname: str, rev: str):
    d = HF_EVAL / repo_dirname / "snapshots" / rev
    files = {}
    if d.exists():
        for f in sorted(x for x in d.iterdir() if x.is_file()):
            real = f.resolve()
            files[f.name] = {"size": real.stat().st_size, "sha256": sha(real) if real.stat().st_size < 400_000_000 else _sha_big(real)}
    return {"revision": rev, "dir": str(d), "files": files}


def _sha_big(p: Path):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 24), b""):
            h.update(chunk)
    return h.hexdigest()


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    prev = OUT / "manifest.json"
    gen = 1
    if prev.exists():
        old = json.loads(prev.read_text(encoding="utf8"))
        gen = int(old.get("generation", 1)) + 1
        (OUT / f"manifest.prev-{gen - 1}.json").write_text(json.dumps(old, indent=1), encoding="utf8")
    shim = ROOT / "runs" / "env-2026-10-14" / "scripts" / "shims" / "flash_attn" / "layers" / "rotary.py"
    m = {
        "generation": gen, "created": time.strftime("%Y-%m-%dT%H:%M:%S"), "card": "EXP-001 v0.5 SIGNED",
        "git": {"head": sh(["git", "rev-parse", "HEAD"]), "branch": sh(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
                "dirty_note": "files of this implementation are untracked at manifest time; the orchestrator commits"},
        "appendix_b_frozen": {f: sha(AN / f) for f in FROZEN_APPENDIX_B},
        "H_A_source_rule_and_L_c": {"ha_source.py": sha(AN / "ha_source.py"), "L_c.txt": sha(AN / "L_c.txt"),
                                     "note": "L_c.txt is written after PG-V passes; hashed again in runs/EXP-001/pilot/ before D0"},
        "derangements": {"pi1_seed": 9101, "pi2_seed": 9102, "generator": "analysis/EXP-001/metrics.py::derangement (numpy default_rng, rejection)",
                         "pgv_cross_prefix": "analysis/EXP-001/completion.py::pgv_derangements (base seed 4401, 4 derangements, different prefix)",
                         "pgv_same_prefix_pairing": "analysis/EXP-001/completion.py::same_prefix_partner",
                         "code_sha256": {"metrics.py": sha(AN / "metrics.py"), "completion.py": sha(AN / "completion.py")}},
        "analysis_code": {f: sha(AN / f) for f in ANALYSIS_CODE},
        "generation_code": {f: sha(ROOT / "exp001" / f) for f in GEN_CODE},
        "coco": {"draw": sha(OUT / "coco_draw.json"), "captions_val2017.json": sha(Path(r"C:\Users\Shlok\.cache\dlm_dl\coco\ann\annotations\captions_val2017.json")),
                 "annotations_trainval2017.zip": "113a836d90195ee1f884e704da6304dfaaecff1f023f49b6ca93c4aaae470268",
                 "val2017.zip": "4f7e2ccb2866ec5041993c9cf2a952bbed69647b115d0f74da7ce8f4bef82f05",
                 "licence": "annotations CC BY 4.0, images Flickr terms (cocodataset.org terms of use) [E0, as stated by the card; not re-verified]"},
        "pins": {
            "tagger": {"name": "spaCy en_core_web_sm", "version": "3.8.0", "wheel_sha256": "1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85",
                       "source": "github.com/explosion/spacy-models release en_core_web_sm-3.8.0", "tags": "Universal POS (pos_)"},
            "clip": dict(model_pin("models--openai--clip-vit-large-patch14", "32bd64288804d66eefd0ccbe215aa642df71cc41"), repo="openai/clip-vit-large-patch14"),
            "vlm": dict(model_pin("models--Qwen--Qwen3-VL-2B-Instruct", "89644892e4d85e24eaac8bacfd4f463576704203"), repo="Qwen/Qwen3-VL-2B-Instruct", licence="apache-2.0 (HF API)",
                        p_yes="two-way softmax of Yes/No answer logits at the first answer position",
                        prompt_template_file="analysis/EXP-001/vlm_prompt.txt", presence_template_file="analysis/EXP-001/vlm_presence_prompt.txt"),
            "clip_iqa": "Wang et al. 2023 formulation with the pinned CLIP ViT-L/14 weights: prompts 'Good photo.' / 'Bad photo.', logit scale 100 (analysis/EXP-001/evalmodels.py::ClipScorer.iqa); torchmetrics 1.9.0 class not used",
            "kid": "NOT PINNED YET (Inception weights for KID are needed from stage D3 on, not for PG-1/PG-V)",
            "llama2_tokenizer": "NousResearch/Llama-2-7b-hf rev 8efe6c9b93655b934e27bd9981e3ec13e55aee9d (setup.md)",
            "gpt2_large": "openai-community/gpt2-large rev 32b71b12589c2f8d625668d2335a01cac3249519 (setup.md)",
            "unidisc": "alexanderswerdlow/unidisc commit 3ee3e47a9e64bac2fdca59957726f14723371ced; weights aswerdlow/unidisc_interleaved rev 2b344ca856bd108b52a2d022a3463dace131249f (setup.md)",
        },
        "shim": {"file": str(shim.relative_to(ROOT)), "sha256": sha(shim), "note": "working copy is v2 (float32 rotation, one rounding) and uncommitted at card time"},
        "environments": {
            "generation_venv": {"python": str(GEN_PY), "versions": versions(GEN_PY, ["torch", "transformers", "numpy", "torchmetrics", "accelerate", "diffusers"])},
            "eval_venv": {"python": str(EVAL_PY), "versions": versions(EVAL_PY, ["torch", "transformers", "numpy", "scipy", "spacy", "en_core_web_sm", "pytest", "torchmetrics", "pillow"])},
        },
        "gpu": {"nvidia_smi": sh(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,clocks.max.sm", "--format=csv,noheader"])},
        "gpu_guard": {"tool": "tools/gpu_guard.py", "sha256": sha(ROOT / "tools" / "gpu_guard.py")},
    }
    (OUT / "manifest.json").write_text(json.dumps(m, indent=1, ensure_ascii=False), encoding="utf8")
    return m


if __name__ == "__main__":
    m = build()
    print("manifest generation", m["generation"], "frozen files:", len(m["appendix_b_frozen"]))
