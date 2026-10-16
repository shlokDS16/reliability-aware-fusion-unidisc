"""ScienceDirect query runs (S1', S2' of D0026, NOT clauses dropped as in the sheet), re-packed 2026-10-16.

Field: Title, abstract or author-specified keywords (tak=), years 2021-2026.
Platform facts checked in the user's Chrome on 2026-10-16: at most 8 Boolean connectors per field
('Use fewer boolean connectors (max 8 per field)'; the sheet's M runs with 11 were refused);
wildcards are refused ("Wildcards '*' are not supported"); plural forms are matched automatically
("discrete diffusion" 39 = "discrete diffusions" 39; llm 131 = llms 131). Hence: singular phrases only,
wildcards written out (token* -> token, tokenization, tokenizer; llm* -> llm; paraphras* -> paraphrase,
paraphrasing; dialog* -> dialog, dialogue), and every run has <= 8 connectors (asserted below).
Phrases contained in a broader phrase of the same list are dropped ("natural language generation" is
matched by "language generation"; "unified understanding and generation" by "understanding and generation").
    python -I sd_queries_20261016.py     # label, connectors, sha256, string
"""
import hashlib, itertools, re

def OR(ts):
    return ts[0] if len(ts) == 1 else "(" + " OR ".join(ts) + ")"

def chunks(ts, k):
    return [ts[i:i + k] for i in range(0, len(ts), k)]

def connectors(q):
    return len(re.findall(r"\b(?:AND|OR|NOT)\b", q))

RUNS = {}
A1 = ['"diffusion language model"', '"language diffusion model"', '"diffusion llm"', '"diffusion lm"', 'dllm',
      '"diffusion-based language model"', '"diffusion-based llm"', '"diffusion large language model"',
      '"diffusion-based large language model"', '"text diffusion"', '"block diffusion"', '"absorbing diffusion"',
      '"diffusion mllm"', '"diffusion vlm"', '"diffusion vision-language model"', 'dmllm', 'dvlm']
for i, c in enumerate(chunks(A1, 9), 1):
    RUNS[f"A1-r{i}"] = OR(c)
RUNS["A2"] = OR(['"discrete diffusion"', '"masked diffusion"', '"discrete flow"', '"discrete state-space"'])  # = S1'-A2 r7 + r8 (supersets)
LANG = OR(['language', 'text', 'token', 'tokenization', 'tokenizer'])
RUNS["A3-r1"] = '"non-autoregressive language model" OR ("absorbing state" AND ' + LANG + ")"
RUNS["A3-r2"] = '("any-order" AND ' + LANG + ') OR ("non-autoregressive" AND diffusion)'
B = ['"text generation"', '"language generation"', '"sequence-to-sequence"', 'seq2seq', '"discrete sequence"',
     '"speculative decoding"', '"categorical data"', '"discrete data"', 'paraphrase', 'paraphrasing', '"textual diffusion"',
     '"text modeling"', '"named entity"', 'sentiment', 'summarization', 'dialog', 'dialogue', '"machine translation"',
     '"text style"', 'commonsense', '"topic model"', '"triple extraction"', '"information extraction"']
for i, c in enumerate(chunks(B, 8), 1):
    RUNS[f"B-r{i}"] = "diffusion AND " + OR(c)
RUNS["C"] = 'diffusion AND ("language model" OR llm)'
M1 = ['"unified multimodal"', '"unified multi-modal"', '"understanding and generation"', '"any-to-any"', '"mixed-modal"', '"mixed-modality"']
M2 = ['diffusion', '"masked generative"', '"discrete flow"', '"flow matching"', '"rectified flow"', '"discrete denoising"']
M3 = ['multimodal', '"multi-modal"', '"vision-language"', '"text-to-image"', '"image generation"', 'mllm', '"visual understanding"', '"image understanding"']
for i, (a, b, c) in enumerate(itertools.product(chunks(M1, 3), chunks(M2, 3), chunks(M3, 4)), 1):  # (2+2+3)+2 = 9 > 8 -> M3 in 3s
    pass
RUNS_M = {}
for i, (a, b, c) in enumerate(itertools.product(chunks(M1, 3), chunks(M2, 3), chunks(M3, 3)), 1):
    RUNS_M[f"M-r{i}"] = OR(a) + " AND " + OR(b) + " AND " + OR(c)
RUNS.update(RUNS_M)
V1 = ['"vision-language-action"', 'vla']
V2 = ['"discrete diffusion"', '"discrete denoising"', '"masked diffusion"', '"diffusion-based"', '"unified diffusion"', '"diffusion language model"', 'dllm']
for i, c in enumerate(chunks(V2, 6), 1):
    RUNS[f"VLA-r{i}"] = OR(V1) + " AND " + OR(c)
for k, q in RUNS.items():
    assert connectors(q) <= 8, (k, connectors(q), q)

if __name__ == "__main__":
    import json, sys
    if "--json" in sys.argv:
        print(json.dumps(RUNS))
    else:
        for k, q in RUNS.items():
            print(k, connectors(q), hashlib.sha256(q.encode("utf8")).hexdigest()[:12], q)
