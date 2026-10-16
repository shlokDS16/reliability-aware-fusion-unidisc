"""SpringerLink query strings (D0031 union approach; NOT clauses dropped as in the sheet's SpringerLink section).

Run A: advanced-search Title field (link.springer.com/search?advancedSearch=true&title=...&dateFrom=2021&dateTo=2026).
Run B: Keywords box (full text, relevance-sorted, export cap 1,000): a sample, reported as supplementary.
Phrases singular and plural; wildcards kept where SpringerLink accepts them (token*, llm*, paraphras*, dialog*).
    python springer_queries_20261016.py      # prints label, length, sha256 and the string
"""
import hashlib

def OR(*t):
    return "(" + " OR ".join(t) + ")"

A1 = OR('"diffusion language model"', '"diffusion language models"', '"language diffusion model"', '"language diffusion models"',
        '"diffusion llm"', '"diffusion llms"', '"diffusion lm"', '"diffusion lms"', 'dllm', 'dllms',
        '"diffusion-based language model"', '"diffusion-based language models"', '"diffusion-based llm"', '"diffusion-based llms"',
        '"diffusion large language model"', '"diffusion large language models"', '"diffusion-based large language model"',
        '"diffusion-based large language models"', '"text diffusion"', '"block diffusion"', '"absorbing diffusion"',
        '"diffusion mllm"', '"diffusion mllms"', '"diffusion vlm"', '"diffusion vlms"', '"diffusion vision-language model"',
        '"diffusion vision-language models"', 'dmllm', 'dmllms', 'dvlm', 'dvlms')
DISC = OR('"discrete diffusion"', '"masked diffusion"', '"discrete flow"', '"discrete flows"', '"discrete state-space"', '"discrete state-spaces"')
A3 = OR('"non-autoregressive language model"', '"non-autoregressive language models"',
        '("absorbing state" AND ' + OR('language', 'text', 'token*', '"language model"', '"language models"') + ')',
        '("any-order" AND ' + OR('language', 'text', 'token*', '"language model"', '"language models"') + ')',
        '("non-autoregressive" AND diffusion)')
B = 'diffusion AND ' + OR('"text generation"', '"language generation"', '"natural language generation"', '"sequence-to-sequence"', 'seq2seq',
                          '"discrete sequence"', '"discrete sequences"', '"speculative decoding"', '"categorical data"', '"discrete data"',
                          'paraphras*', '"textual diffusion"', '"text modeling"', '"named entity"', 'sentiment', 'summarization', 'dialog*',
                          'dialogue', '"machine translation"', '"text style"', 'commonsense', '"topic model"', '"topic models"',
                          '"triple extraction"', '"information extraction"')
C = 'diffusion AND ' + OR('"language model"', '"language models"', 'llm*')
M = (OR('"unified multimodal"', '"unified multi-modal"', '"unified understanding and generation"', '"understanding and generation"',
        '"any-to-any"', '"mixed-modal"', '"mixed-modals"', '"mixed-modality"') + ' AND ' +
     OR('diffusion', '"masked generative"', '"discrete flow"', '"discrete flows"', '"flow matching"', '"rectified flow"', '"discrete denoising"') + ' AND ' +
     OR('multimodal', '"multi-modal"', '"vision-language"', '"text-to-image"', '"image generation"', 'mllm', 'mllms', '"visual understanding"', '"image understanding"'))
VLA = OR('"vision-language-action"', 'vla', 'vlas') + ' AND ' + OR('"discrete diffusion"', '"discrete denoising"', '"masked diffusion"', '"diffusion-based"',
                                                                  '"unified diffusion"', '"diffusion language model"', '"diffusion language models"', 'dllm', 'dllms')
QUERIES = {
    "S1": A1,                       # S1p-A1 (all names)
    "S2": DISC,                     # S1p-A2-r3 (superset of A2-r1, r2)
    "S3": A3,                       # S1p-A3-r1..r4
    "S4": "(" + B + ")",            # S1p-B-r1..r4
    "S5": "(" + C + ")",            # S1p-C
    "S6": "(" + M + ")",            # S2p-M-r1, r2
    "S7": "(" + VLA + ")",          # S2p-VLA-r1, r2
}
QUERIES["U"] = " OR ".join(QUERIES[k] for k in ("S1", "S2", "S3", "S4", "S5", "S6", "S7"))

if __name__ == "__main__":
    for k, q in QUERIES.items():
        print(k, len(q), hashlib.sha256(q.encode("utf8")).hexdigest())
