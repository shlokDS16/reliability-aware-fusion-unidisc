"""Supervisor's comments of 2026-10-22: cite the ACM Computing Surveys paper of Yang et al. (2023), and add recent
research on discrete, continuous and multimodal diffusion language models to the introduction, in the style of Yang
et al.'s introduction. Every cited key is already verified in references.bib except Yang et al., whose details are
taken from the article PDF (ACM Comput. Surv. 56(4), Article 105, 39 pages, doi 10.1145/3626235).
Run from paper/review."""
from pathlib import Path

BIB = r"""
@article{yang2023diffusion,
  author = {Ling Yang and Zhilong Zhang and Yang Song and Shenda Hong and Runsheng Xu and Yue Zhao and Wentao Zhang and Bin Cui and Ming-Hsuan Yang},
  title = {{Diffusion Models: A Comprehensive Survey of Methods and Applications}},
  journal = {ACM Computing Surveys},
  volume = {56},
  number = {4},
  articleno = {105},
  numpages = {39},
  year = {2023},
  month = nov,
  doi = {10.1145/3626235},
}
"""
b = Path("references.bib")
t = b.read_text(encoding="utf-8")
if "yang2023diffusion" not in t:
    b.write_text(t.rstrip("\n") + "\n" + BIB, encoding="utf-8")

I = Path("sections/01-introduction.tex")
t = I.read_text(encoding="utf-8")
PARA = (r"Diffusion models first rose to prominence in image synthesis~\cite{yang2023diffusion}, and research on diffusion "
        r"for language has since grown along three lines. Discrete, mostly masked, diffusion language models now reach the "
        r"scale of autoregressive models: LLaDA and Dream~7B train or adapt models with billions of parameters~\cite{arXiv:2502.09992,arXiv:2508.15487}, "
        r"Seed Diffusion targets high-speed inference and DiffuCoder code generation~\cite{arXiv:2508.02193,arXiv:2506.20639}, "
        r"block diffusion interpolates between autoregressive and diffusion decoding~\cite{arXiv:2503.09573}, and training-free "
        r"caching and parallel decoding accelerate inference~\cite{arXiv:2505.22618,arXiv:2605.15609}. Continuous diffusion "
        r"language models, which diffuse embeddings or relaxations on the probability simplex, have narrowed their gap to "
        r"discrete models~\cite{arXiv:2502.13917,arXiv:2604.11748,arXiv:2603.02547,arXiv:2608.10615}, and hybrid and dual "
        r"formulations connect the two families~\cite{arXiv:2510.22510,arXiv:2506.10892}. Multimodal diffusion language "
        r"models carry the same machinery to understanding and generating images and other modalities with one "
        r"network~\cite{arXiv:2505.15809,arXiv:2505.16839,arXiv:2505.16990,arXiv:2510.06308,arXiv:2604.00007,arXiv:2609.40362}. "
        r"Alongside these models, theoretical and evaluation studies examine parallel sampling, scaling at matched compute "
        r"and the reliability of reported results~\cite{arXiv:2505.21400,arXiv:2602.15014,arXiv:2507.15857,arXiv:2606.29228}.")
anchor = "This article reviews that literature systematically."
assert t.count(anchor) == 1
if "Diffusion models first rose to prominence" not in t:
    t = t.replace(anchor, PARA + "\n\n" + anchor)
old = r"Other surveys address unified multimodal models~\cite{arXiv:2505.02567,arXiv:2409.14993,arXiv:2605.25343},"
assert t.count(old) == 1
t = t.replace(old, r"\citet{yang2023diffusion} survey diffusion models across domains in this journal. Other surveys address unified multimodal models~\cite{arXiv:2505.02567,arXiv:2409.14993,arXiv:2605.25343},")
I.write_text(t, encoding="utf-8")
print("ok")
