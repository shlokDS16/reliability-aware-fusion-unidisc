"""Revision 2026-10-21: fixes from the hostile-referee pass (research/review/audits/2026-10-21-revision-redteam.md,
findings 1-11). Exact-anchor edits. Run from paper/review."""
from pathlib import Path


def edit(f, old, new):
    p = Path(f)
    t = p.read_text(encoding="utf-8")
    if t.count(old) != 1:
        raise SystemExit(f"{f}: anchor found {t.count(old)} times: {old[:80]}")
    p.write_text(t.replace(old, new), encoding="utf-8")


S5, S7, S8, S10 = "sections/05-rq-evidence.tex", "sections/07-error-budget.tex", "sections/075-practice.tex", "sections/10-limitations.tex"
# 1
edit(S5, "Recent work outside the sample explains why curves bend and offers levers.",
     "Recent work outside the sample shows mechanisms that could produce such curves and offers levers.")
# 2
edit(S5, "With single-pass training, masked diffusion scales at a rate comparable to autoregressive models with a relatively small compute gap~\\cite{arXiv:2410.18514}.",
     "Masked diffusion scales at a rate comparable to autoregressive models, with a relatively small compute gap~\\cite{arXiv:2410.18514}.")
edit(S5, "and that a family with worse likelihood scaling can sit better on the speed--quality Pareto frontier because it samples faster~\\cite{arXiv:2602.15014}.",
     "and that, among diffusion families, one with worse likelihood scaling can sit better on the speed--quality Pareto frontier because it samples faster~\\cite{arXiv:2602.15014}.")
edit(S5, "These studies say when a diffusion model is the better choice (data-constrained pretraining, or deployment in which parallel decoding speed at a fixed quality matters), which the best-against-best comparisons of the sample cannot.",
     "These studies point to conditions under which a diffusion model may be preferable (data-constrained pretraining, or deployment in which parallel decoding speed matters), which the best-against-best comparisons of the sample cannot isolate.")
edit(S8, "In compute-matched studies, diffusion pays a compute gap on likelihood under single-pass training~\\cite{arXiv:2410.18514,arXiv:2602.15014}, but overtakes autoregressive training when unique data is scarce~\\cite{arXiv:2507.15857,arXiv:2511.03276} and can win on the speed--quality frontier when parallel decoding matters~\\cite{arXiv:2602.15014}.",
     "In compute-matched studies, masked diffusion shows a compute gap to autoregressive models~\\cite{arXiv:2410.18514} but overtakes autoregressive training when unique data is scarce~\\cite{arXiv:2507.15857,arXiv:2511.03276}; among diffusion families, faster sampling can outweigh worse likelihood on the speed--quality frontier~\\cite{arXiv:2602.15014}.")
# 3
edit(S5, "with a reported 1.7 to 2.2 times speed-up at matched or better accuracy~\\cite{arXiv:2604.02560}.",
     "with a reported 1.7 to 2.2 times speed-up at matched or better accuracy on one 7B model~\\cite{arXiv:2604.02560}.")
edit(S7, "Dependency-aware selection bounds the same term by choosing which positions to co-commit~\\cite{arXiv:2604.02560}, and a learned commitment policy acts on the position rule~\\cite{arXiv:2605.24697}; both lower the factorisation term at a given number of passes rather than $V$.",
     "Dependency-aware selection targets the same term by choosing which positions to co-commit, with a bound that holds under a sub-additivity assumption~\\cite{arXiv:2604.02560}, and a learned commitment policy acts on the position rule~\\cite{arXiv:2605.24697}; both change the commitment policy at a given number of passes, not the value rule behind $V$.")
# 4
edit(S5, "the thresholds never yield a well-supported verdict: RQ2 is mixed in all 60 settings, RQ3 weakly supported in 48, RQ4 mixed in 36, and RQ5 mixed or untested in 44. ",
     "the thresholds never yield a well-supported verdict, but the other verdicts move: RQ2 is mixed in all 60 settings, RQ3 weakly supported in 48 and mixed in 12, RQ4 mixed in 36 and weakly supported in 24, and RQ5 mixed in 24, untested in 20 and weakly supported in 16; only 16 settings reproduce all four main verdicts. ")
# 5
edit(S5, "and partly offsets the errors added by more stochastic decoding~\\cite{arXiv:2606.12232}; a remasking loop is a remedy whose value depends on stochasticity and block size, not a default.",
     "and partly offsets the errors added by more stochastic decoding~\\cite{arXiv:2606.12232}; for that method, the value of remasking depends on stochasticity and block size.")
edit(S8, "\\item \\emph{Use remasking as a remedy, not a default.} Its benefit depends on decoding stochasticity and block length~\\cite{arXiv:2606.12232}; test it at matched network calls against confidence-based unmasking.",
     "\\item \\emph{Test remasking rather than assume it helps.} A re-evaluation of one post-hoc confidence-based remasking method found little or no benefit at short block lengths and only partial help under more stochastic decoding~\\cite{arXiv:2606.12232}; other remaskers have not been re-evaluated this way, so compare any of them at matched network calls against confidence-based unmasking.")
# 6
edit(S8, "Each recommendation names the evidence it rests on; none is a measured optimum.",
     "Each recommendation names the evidence it rests on; none is a measured optimum. Some rest on single studies outside the review's sample and are suggestions for practice, not findings of the review.")
edit(S8, "are the current alternatives to a single confidence threshold.", "are two recent alternatives to a single confidence threshold.")
edit(S10, "and recent ones may be under-represented among the included studies. Section~\\ref{sec:rq} reconciles them with the verdicts qualitatively; none changes a verdict, because each verdict describes the sampled studies, but they change what a practitioner should take from it (Section~\\ref{sec:practice}).",
     "Section~\\ref{sec:rq} reconciles them with the verdicts qualitatively. They do not enter the verdicts, which describe the sampled studies, but they bear on how a practitioner should read them (Section~\\ref{sec:practice}).")
# 7
edit(S8, "``partly'': the notation fits only with a stated extension.}",
     "``partly'': the notation fits only with a stated extension. A row whose cells are not stated (Dream~7B) fits trivially.}")
# 8
edit(S5, "Two recent continuous models report likelihood and generation quality competitive with discrete diffusion: LangFlow, which links embedding-space diffusion to flow matching~\\cite{arXiv:2604.11748}, and CoDAR, which keeps diffusion continuous and rounds to tokens with a contextual autoregressive decoder~\\cite{arXiv:2603.02547}. Theory also narrows the gap in parallelism: uniform and Gaussian diffusion can sample in a number of forward passes that scales with the dual total correlation of the data, which was previously known only for masked diffusion~\\cite{arXiv:2609.20539}. In the notation these are changes of channel (C1) and, for CoDAR, of the final rounding step, not new commitment policies.",
     "Two recent continuous models close much of the gap to discrete diffusion: LangFlow, which links embedding-space diffusion to flow matching, reports likelihood and sample quality that rival discrete diffusion~\\cite{arXiv:2604.11748}, and CoDAR, which keeps diffusion continuous and rounds to tokens with a contextual autoregressive decoder, reports generation quality competitive with strong discrete models~\\cite{arXiv:2603.02547}. Theory compares their parallelism: uniform and Gaussian diffusion can sample in a number of forward passes that scales with the dual total correlation of the data, previously shown only for masked diffusion, and the same work proves separations among the three families~\\cite{arXiv:2609.20539}. In the notation, LangFlow and CoDAR change the channel (C1), and CoDAR also the final rounding step.")
# 9
edit(S5, "Because both modalities then share one objective and one sampler, joint and decoupled arms built on such a model would differ only in what they share, which is the comparison a synergy test needs.",
     "A shared objective and sampler across modalities would remove one source of difference between the joint and decoupled arms of a synergy ablation; whether such a model removes the others is open.")
# 11
edit(S8, "The census and the extraction sample give the checklist its content, and how often each item is missing.",
     "The census and the extraction sample give the checklist its content and, where they measure it, how often each item is missing.")
edit(S8, "and 5 copy the baseline numbers.", "and 5 state that they copied the baseline numbers.")
print("ok")
