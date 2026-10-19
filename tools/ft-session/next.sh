#!/bin/bash
# usage: next.sh postbatch <batch> <agentA> <agentB>   |   next.sh build <batch>
S="C:/Users/Shlok/AppData/Local/Temp/claude/C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-resume-dlm-discovery-exp-003-fcff62/9d5203d7-a6be-4a10-8e9d-83c85c9e81ca/scratchpad/ft-dispatch"
P="C:/Users/Shlok/.claude/projects/C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-resume-dlm-discovery-exp-003-fcff62/9d5203d7-a6be-4a10-8e9d-83c85c9e81ca/subagents"
cd "/c/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706" || exit 1
if [ "$1" = postbatch ]; then
  python -I tools/ft_postbatch.py "$2" "$S" "$P" "$3" "$4" | python -I -c "import json,sys; d=json.load(sys.stdin); print(d['batch'], 'iso', d['isolation_A'], d['isolation_B'], 'agree', d['agree'], '/', d['n'], 'dis', d['disagree'], 'adj', d['adjudicate'], 'qbad', d.get('quotes_not_accepted_A'), d.get('quotes_not_accepted_B'), 'miss', d['missing_A'], d['missing_B'], 'model', d.get('model_ok_A'), d.get('model_ok_B'))"
  git add analysis/screening/ft-t1 >/dev/null 2>&1; git commit -q -m "Full-text T1 $2 complete

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" >/dev/null 2>&1 && echo committed
elif [ "$1" = build ]; then
  for R in A B; do python -I tools/ft_dispatch.py --role $R --batch "$2" --ids "$S/$2.ids" --root "$S" | sed 's/.*ft-dispatch.//'; done
fi
