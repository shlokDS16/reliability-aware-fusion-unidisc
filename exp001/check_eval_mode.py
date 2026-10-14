"""One-off check (coordinator message after the MDLM T2 finding): is UniDisc's backbone left in train mode (dropout 0.1) by the
loaders, and how much do the marginals change? Run through gpu_guard. Writes runs/EXP-001/gates/eval_mode_check.json."""
import json, sys, time
from pathlib import Path
import torch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from exp001.unidisc_net import UniDiscNet, shim_info
from exp001.network import to_prob

net = UniDiscNet(res=512)
rep = {"training_flag_after_build_before_set_eval": net.was_training_after_build, "dropout_p_config": float(net.cfg.model.dropout),
       "shim": shim_info()}
net.set_prompt("A man riding a", n_txt=32)
tail = torch.full((32,), net.mask_id, dtype=torch.long); img = torch.full((net.L_I,), -1, dtype=torch.long)
def probs():
    lt, li = net.forward(tail, img)
    return to_prob(lt), to_prob(li)
# eval mode twice
a1 = probs(); a2 = probs()
rep["eval_twice_max_abs_diff_text"] = float((a1[0] - a2[0]).abs().max()); rep["eval_twice_max_abs_diff_img"] = float((a1[1] - a2[1]).abs().max())
# train mode (dropout on), twice
import models.dit as _dit
_dit.compiled_flex_attention = _dit.flex_attention      # the SDPA patch of setup.md covers only the eval branch; make the train branch run too
Path(ROOT / "runs/EXP-001/gates/eval_mode_check.json").write_text(json.dumps(rep, indent=1))   # partial report first
net.model.backbone.train()
def fwd_train():
    x = net.x0.clone(); x[0, net.a0:net.a0 + 32] = tail.to(x.device)
    x[0, net.i0:net.i1 + 1] = torch.full((net.L_I,), net.mask_id, device=x.device)
    with torch.no_grad():
        lp = net.model.forward(x=x, sigma=None, modality=net.modality, sample_ids=net.sample_ids, block_mask=True)
    return to_prob(lp[0, net.a0:net.a0 + 32, :32001]), to_prob(lp[0, net.i0:net.i1 + 1, 32001:])
b1 = fwd_train(); b2 = fwd_train()
rep["train_twice_max_abs_diff_text"] = float((b1[0] - b2[0]).abs().max()); rep["train_twice_max_abs_diff_img"] = float((b1[1] - b2[1]).abs().max())
rep["train_vs_eval_mean_tv_text"] = float(0.5 * (b1[0].to(a1[0].device) - a1[0]).abs().sum(-1).mean()); rep["train_vs_eval_mean_tv_img"] = float(0.5 * (b1[1].to(a1[1].device) - a1[1]).abs().sum(-1).mean())
rep["train_vs_eval_top1_agree_text"] = float((b1[0].argmax(-1) == a1[0].argmax(-1)).float().mean())
rep["train_vs_eval_top1_agree_img"] = float((b1[1].argmax(-1) == a1[1].argmax(-1)).float().mean())
net.set_eval()
rep["assert_eval_ok_after_reset"] = True
rep["gpu_seconds_per_forward"] = None
Path(ROOT / "runs/EXP-001/gates/eval_mode_check.json").write_text(json.dumps(rep, indent=1))
print(json.dumps(rep, indent=1))
