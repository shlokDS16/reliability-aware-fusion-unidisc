#!/bin/bash
# After a D0052 extraction session (or its return) ends: postbatch, compact summary, return message (pass 1), commit,
# free RAM. usage: bash analysis/extraction/d0052/after.sh <batch> [2]
cd "/c/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706" || exit 1
B="$1"; P="${2:-1}"
if [ "$P" = 2 ]; then A="--pass 2"; else A=""; fi
python -I analysis/extraction/d0052/postbatch.py "$B" $A 2>&1 | python -I -c "
import sys, json
for l in sys.stdin:
    l = l.strip()
    if l.startswith('{'):
        d = json.loads(l)
        if 'batch' in d:
            print(d['batch'], 'pass', d['pass'], 'model', d['model_ok'], 'iso', d['isolation'], 'usable', d['usable'])
        elif 'id' in d:
            print(' ', d['id'], d['status'], 'fail', d['fail'], 'warn', d['warn'])
"
if [ "$P" = 1 ]; then
  python -I analysis/extraction/d0052/return_msg.py "$B" > /dev/null
  echo "  return items: $(grep -c '^(' analysis/extraction/d0052/returns/$B.txt)"
fi
git add analysis/extraction/d0052 research/review/extraction/dispatch-log.jsonl >/dev/null 2>&1
git commit -q -m "$B pass $P filed

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" >/dev/null 2>&1 && echo "  committed"
powershell -NoProfile -Command "'  free RAM ' + [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"
