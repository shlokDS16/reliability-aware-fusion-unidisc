"""Download frozen checkpoints into the Hugging Face cache. Prints resolved snapshot paths and commit SHAs."""
import sys
from huggingface_hub import snapshot_download
for rid in sys.argv[1:]:
    p = snapshot_download(rid)
    print(rid, p, flush=True)
