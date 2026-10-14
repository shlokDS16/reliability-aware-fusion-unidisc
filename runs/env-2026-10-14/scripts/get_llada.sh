#!/bin/bash
# download GSAI-ML/LLaDA-8B-Instruct (16 GB) with the parallel downloader; small files first
D="C:/Users/Shlok/.cache/dlm_dl/llada"
B="https://huggingface.co/GSAI-ML/LLaDA-8B-Instruct/resolve/main"
for f in config.json configuration_llada.py generation_config.json modeling_llada.py special_tokens_map.json tokenizer.json tokenizer_config.json model.safetensors.index.json; do
  python scripts/pardl.py "$B/$f" "$D/$f" 2 1
done
for i in 1 2 3 4 5 6; do
  f=$(printf "model-%05d-of-00006.safetensors" $i)
  python scripts/pardl.py "$B/$f" "$D/$f" 12 16
done
echo ALLDONE
