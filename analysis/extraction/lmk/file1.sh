#!/bin/bash
# File pass 1 of a landmark extraction session; when the validator returned entries, copy the return list into the
# session folder as return-1.txt (one return per session). usage: bash analysis/extraction/lmk/file1.sh <batch>
cd "/c/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706" || exit 1
B="$1"
bash analysis/extraction/lmk/after.sh "$B" 2>&1 | tail -5
base=$(grep "^$B " analysis/extraction/lmk/agent-map.txt | tail -1 | awk '{print $5}')
n=$(grep -c '^(' "analysis/extraction/lmk/returns/$B.txt")
if [ "$n" -gt 0 ]; then
  cp "analysis/extraction/lmk/returns/$B.txt" "C:/Users/Shlok/AppData/Local/Temp/claude/C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-resume-dlm-discovery-exp-003-334706/bfefb6fe-654c-43b1-a1f0-c80e3f972b2f/scratchpad/ex-dispatch/$base/return-1.txt" && echo "  return-1.txt copied ($n entries)"
fi
