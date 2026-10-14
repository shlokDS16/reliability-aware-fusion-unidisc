"""Collect the per-run JSON files into timing.json, dump the resolved UniDisc config, and write token dumps as JSON (git ignores *.pt)."""
import json, glob, shutil
from pathlib import Path
from common import *  # noqa

SU = OUT / "smoke_unidisc"; SM = OUT / "smoke_mdlm"


def load(p):
    return json.loads(Path(p).read_text())


def main():
    t = {}
    mdlm = load(SM / "smoke_mdlm.json")
    t["mdlm"] = dict(source="smoke_mdlm/smoke_mdlm.json", log="logs/mdlm_smoke.log", env=mdlm["env"], load_s=mdlm["load_s"], n_params_backbone=mdlm["n_params_backbone"],
                     sample_128_steps=mdlm["sample"], sample_1000_steps=mdlm["sample_long"], gen_ppl_eval_one_sample=mdlm.get("gen_ppl"),
                     forward_L1024=mdlm["timing_forward_L1024"], marginals_fp32_vs_bf16=mdlm.get("marginals_fp32_check"))
    parts = {}
    for p in sorted(glob.glob(str(SU / "smoke_unidisc_bf16_1024px_stages_*.json"))):
        d = load(p); stage_key = Path(p).stem.split("_stages_")[1]
        parts[stage_key] = d
    u = dict(source="smoke_unidisc/smoke_unidisc_bf16_1024px_stages_*.json", logs=["logs/unidisc_smoke_1024_abd.log", "logs/unidisc_timing_c.log", "logs/unidisc_stage_e.log"])
    for k, d in parts.items():
        for stage, val in d.items():
            if stage != "info":
                u[f"stage_{stage}"] = val
        u.setdefault("info_by_run", {})[k] = d["info"]
    t["unidisc"] = u
    for f in sorted(glob.glob(str(OUT / "timing_llada*.json"))):
        t["llada_source"] = Path(f).name
    (OUT / "timing.json").write_text(json.dumps(t, indent=2))
    # resolved config
    import unidisc_setup as U
    from omegaconf import OmegaConf
    cfg = U.make_config(["eval.visualize_sample=false"])
    OmegaConf.resolve(cfg)
    (SU / "resolved_config.yaml").write_text(OmegaConf.to_yaml(cfg))
    dev = SU / "resolved_config_dev.yaml"
    if dev.exists():
        dev.unlink()
    # token dumps as JSON
    import torch
    d = torch.load(SU / "joint_tokens_1024px.pt", weights_only=True)
    (SU / "joint_tokens_1024px.json").write_text(json.dumps({k: v.flatten().tolist() for k, v in d.items()}))
    (SM / "sample_L1024_tokens.json").write_text(json.dumps(torch.load(SM / "sample_L1024_tokens.pt", weights_only=True).flatten().tolist()))
    # failed attempts
    fa = SU / "failed_attempts"; fa.mkdir(exist_ok=True)
    for f in glob.glob(str(SU / "exception_*.out")):
        shutil.move(f, fa / Path(f).name)
    print("ok")


if __name__ == "__main__":
    main()
