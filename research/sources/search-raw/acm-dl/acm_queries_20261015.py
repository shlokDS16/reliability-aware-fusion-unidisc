"""ACM DL query strings run 2026-10-15 (D0031). Each concept group is searched in Title, Abstract and Keyword:
G(list) = (Title:(list) OR Abstract:(list) OR Keyword:(list)), the same semantics as Scopus TITLE-ABS-KEY.
The strings were built in the page from these lists; the page sha256 must equal this script's output."""
import hashlib


def G(ts):
    s = "(" + " OR ".join(f'"{t}"' if (" " in t or "-" in t) else t for t in ts) + ")"
    return f"(Title:{s} OR Abstract:{s} OR Keyword:{s})"


A1 = ["diffusion language model", "diffusion language models", "language diffusion model", "language diffusion models",
      "diffusion llm", "diffusion llms", "diffusion lm", "diffusion lms", "dllm", "dllms", "diffusion-based language model",
      "diffusion-based language models", "diffusion-based llm", "diffusion-based llms", "diffusion large language model",
      "diffusion large language models", "diffusion-based large language model", "diffusion-based large language models",
      "text diffusion", "block diffusion", "absorbing diffusion", "diffusion mllm", "diffusion mllms", "diffusion vlm",
      "diffusion vlms", "diffusion vision-language model", "diffusion vision-language models", "dmllm", "dmllms", "dvlm",
      "dvlms", "non-autoregressive language model", "non-autoregressive language models"]
A2 = ["discrete diffusion", "masked diffusion", "discrete flow", "discrete flows", "discrete state-space", "discrete state-spaces"]
A2X = A2 + ["absorbing state", "any-order", "discrete flow matching", "diffusion LLM"]
L8 = ["language", "text", "token*", "language model", "language models", "llm*", "vocabulary", "autoregressive", "reasoning"]
UM = ["unified multimodal", "unified multi-modal", "unified understanding and generation", "understanding and generation",
      "any-to-any", "mixed-modal", "mixed-modals", "mixed-modality"]
GEN = ["diffusion", "masked generative", "discrete flow", "discrete flows", "flow matching", "rectified flow", "discrete denoising"]
MM = ["multimodal", "multi-modal", "vision-language", "text-to-image", "image generation", "mllm", "mllms",
      "visual understanding", "image understanding"]
VLA = ["vision-language-action", "vla", "vlas"]
VLA2 = ["discrete diffusion", "discrete denoising", "masked diffusion", "diffusion-based", "unified diffusion",
        "diffusion language model", "diffusion language models", "dllm", "dllms"]
BIO = ["protein*", "molecul*", "antibod*", "peptide*", "rna", "dna", "drug*", "crystal*", "chemi*", "genom*", "biolog*",
       "graph generation", "traveling salesman", "recommend*"]
VIS = ["image*", "video*", "3d", "audio", "visual*", "pixel*", "photo*", "segmentation"]
C = ["language model", "language models", "llm*"]
B = ["text generation", "language generation", "natural language generation", "sequence-to-sequence", "seq2seq",
     "discrete sequence", "discrete sequences", "speculative decoding", "categorical data", "discrete data", "paraphras*",
     "textual diffusion", "text modeling", "named entity", "sentiment", "summarization", "dialog*", "dialogue",
     "machine translation", "text style", "commonsense", "topic model", "topic models", "triple extraction",
     "information extraction"]
D, NA = G(["diffusion"]), G(["non-autoregressive"])

Q = {
    "Q1": f"{G(A1)} OR ({G(A2X)} AND {G(L8)}) OR ({NA} AND {D} AND {G(L8)}) OR ({G(UM)} AND {G(GEN)} AND {G(MM)}) OR ({G(VLA)} AND {G(VLA2)})",
    "Q2": f"(({G(A2)} NOT {G(BIO)}) NOT {G(VIS)})",
    "Q3": f"(({NA} AND {D}) NOT {G(BIO)})",
    "Q4": f"(({D} AND {G(B)}) NOT {G(BIO)})",
    "Q5": f"((({D} AND {G(C)}) NOT {G(BIO)}) NOT {G(VIS)})",
}

if __name__ == "__main__":
    for k, v in Q.items():
        print(k, hashlib.sha256(v.encode()).hexdigest()[:16], len(v))
