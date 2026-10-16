"""Build IEEE Xplore command-search strings (Title, Abstract, Author Keywords) and result URLs."""
import sys
import urllib.parse

FIELDS = ("Document Title", "Abstract", "Author Keywords")


def f(t):
    q = f'"{t}"' if (" " in t or "-" in t) else t
    return "(" + " OR ".join(f'"{fld}":{q}' for fld in FIELDS) + ")"


def orl(ts):
    return "(" + " OR ".join(f(t) for t in ts) + ")"


def url(q):
    return ("https://ieeexplore.ieee.org/search/searchresult.jsp?action=search&newsearch=true&matchBoolean=true&queryText="
            + urllib.parse.quote(q) + "&ranges=2021_2026_Year")


C = ["language model", "language models", "llm*"]
B = ["text generation", "language generation", "sequence-to-sequence", "seq2seq", "discrete sequence", "discrete sequences",
     "speculative decoding", "categorical data", "discrete data", "paraphras*", "textual diffusion", "text modeling",
     "named entity", "sentiment", "summarization", "dialog*", "machine translation", "text style", "commonsense",
     "topic model", "topic models", "triple extraction", "information extraction"]

A1 = ["diffusion language model", "diffusion language models", "language diffusion model", "language diffusion models",
      "diffusion llm", "diffusion llms", "diffusion lm", "diffusion lms", "dllm", "dllms",
      "diffusion-based language model", "diffusion-based language models", "diffusion-based llm", "diffusion-based llms",
      "diffusion large language model", "diffusion large language models", "diffusion-based large language model",
      "diffusion-based large language models", "text diffusion", "block diffusion", "absorbing diffusion",
      "diffusion mllm", "diffusion mllms", "diffusion vlm", "diffusion vlms", "diffusion vision-language model",
      "diffusion vision-language models", "dmllm", "dmllms", "dvlm", "dvlms"]
A2 = ["discrete diffusion", "masked diffusion", "discrete flow", "discrete flows", "discrete state-space", "discrete state-spaces"]
LANG4 = ["language", "text", "token*", "language model", "language models"]
UM = ["unified multimodal", "unified multi-modal", "unified understanding and generation", "understanding and generation",
      "any-to-any", "mixed-modal", "mixed-modals", "mixed-modality"]
GEN = ["diffusion", "masked generative", "discrete flow", "discrete flows", "flow matching", "rectified flow", "discrete denoising"]
MM = ["multimodal", "multi-modal", "vision-language", "text-to-image", "image generation", "mllm", "mllms",
      "visual understanding", "image understanding"]
VLA = ["vision-language-action", "vla", "vlas"]
VLA2 = ["discrete diffusion", "discrete denoising", "masked diffusion", "diffusion-based", "unified diffusion",
        "diffusion language model", "diffusion language models", "dllm", "dllms"]

Q = {
    "TEST": f'{f("diffusion")} AND {orl(C + B)}',
    "I1": f'{f("diffusion")} AND {orl(C + B)}',                       # S1':B, S1':C (NOT dropped)
    "I2": orl(A1),                                                     # S1':A1
    "I3": (f'{orl(A2)} OR ({f("absorbing state")} AND {orl(LANG4)}) OR ({f("any-order")} AND {orl(LANG4)}) OR '
           f'{orl(["non-autoregressive language model", "non-autoregressive language models"])} OR '
           f'({f("non-autoregressive")} AND {f("diffusion")})'),        # S1':A2 (NOT dropped, so A2 alone), S1':A3
    "I4": f'{orl(UM)} AND {orl(GEN)} AND {orl(MM)}',                   # S2':M
    "I5": f'{orl(VLA)} AND {orl(VLA2)}',                               # S2':VLA
}

if __name__ == "__main__":
    k = sys.argv[1]
    print(Q[k])
    print(url(Q[k]))
