"""Run the lab engineer's own marginals()/marginals_fp32() (runs/env-2026-10-14/scripts/mdlm_smoke.py) on the same state and compare with fp64 truth,
to find where the reported 0.785 top-1 agreement / 0.32 nat entropy shift comes from."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from g4_common import *  # noqa  (puts the shim v2 first)
sys.path.insert(0, str(ENV_SCRIPTS))
import mdlm_smoke as S      # builds nothing at import; uses its own helpers
import torch, copy
cfg, tok, m = S.build(128)
toks = torch.load(str(G4.parent / "env-2026-10-14" / "smoke_mdlm" / "sample_L1024_tokens.pt")).to("cuda")[:1]
keep = torch.rand(toks.shape, device="cuda", generator=torch.Generator(device="cuda").manual_seed(0)) < 0.5
xm = torch.where(keep, toks, torch.full_like(toks, m.mask_index)); mk = xm == m.mask_index
MODE = os.environ.get("G4_MODE", "eval")
(m.backbone.train() if MODE == "train" else m.backbone.eval())     # restore_model_and_sample() ends with backbone.train(); the smoke script never switched back
out_mode = MODE
p = S.marginals(m, xm); p32 = S.marginals_fp32(m, xm)
# fp64 truth
net = copy.deepcopy(m.backbone).double().eval()
bm = sys.modules[type(m.backbone).__module__]
net.backbone.sigma_map.mlp.register_forward_pre_hook(lambda mod, a: (a[0].double(),))
import torch.nn.functional as F, contextlib, unittest.mock as um
bm.LayerNorm.forward = lambda self, x: F.layer_norm(x, [self.dim]) * self.weight[None, None, :]
with um.patch("torch.cuda.amp.autocast", lambda *a, **k: contextlib.nullcontext()), torch.no_grad():
    lg = net(xm, torch.zeros(1, device="cuda", dtype=torch.float64))
    lpT = m._subs_parameterization(lg.clone(), xm); pT = lpT.exp()
def ent(q): q = q.double(); return -(q * q.clamp_min(1e-30).log()).sum(-1)
out = dict(mode=out_mode, backbone_training_flag=bool(m.backbone.training), n_masked=int(mk.sum()), p_dtype=str(p.dtype), p32_dtype=str(p32.dtype),
           top1_agree_engineer_bf16_vs_fp32=float((p[mk].argmax(-1) == p32[mk].argmax(-1)).float().mean()),
           top1_agree_bf16_vs_truth=float((p[mk].argmax(-1) == pT[mk].argmax(-1)).float().mean()),
           top1_agree_fp32_vs_truth=float((p32[mk].argmax(-1) == pT[mk].argmax(-1)).float().mean()),
           ent_absdiff_engineer_bf16_vs_fp32=float((ent(p[mk]) - ent(p32[mk])).abs().mean()), ent_absdiff_two_bf16_calls=float((ent(S.marginals(m, xm)[mk]) - ent(p[mk])).abs().mean()), top1_agree_two_bf16_calls=float((S.marginals(m, xm)[mk].argmax(-1) == p[mk].argmax(-1)).float().mean()),
           ent_absdiff_bf16_vs_truth=float((ent(p[mk]) - ent(pT[mk])).abs().mean()), ent_absdiff_fp32_vs_truth=float((ent(p32[mk]) - ent(pT[mk])).abs().mean()),
           max_abs_p_diff_engineer=float((p32.double() - p.double()).abs().max()), max_abs_p_diff_fp32_vs_truth=float((p32.double() - pT).abs().max()),
           max_abs_p_diff_bf16_vs_truth=float((p.double() - pT).abs().max()))
# is the engineer's p32 really fp32-everywhere? compare with a second call of the same function and with the model's default
p_again = S.marginals(m, xm)
out["bf16_call_reproducible"] = bool(torch.equal(p, p_again))
out["rotary_module"] = str(sys.modules["flash_attn.layers.rotary"].__file__)
jdump(out, G4 / f"t2_engineer_exact_{out_mode}.json"); print(json.dumps(out, indent=1))
sys.stdout.flush(); os._exit(0)
