#!/bin/bash
# Later tranches (R797 D0035, S1243 D0037), session 741900f8; S and P now session 92c0b6b9. usage:
#   tr.sh <tranche> build <batch>                       -> dispatch folders A and B (tools/ft_dispatch.py)
#   tr.sh <tranche> postbatch <batch> <agentA> <agentB> -> FT_TRANCHE=<tranche> ft_postbatch.py, one-line summary, commit
#   tr.sh <tranche> cpost <c group> <agentC>            -> FT_TRANCHE=<tranche> ft_cpost.py, commit
# landmark tranche lmk (D0061, 2026-10-21): S and P now session bfefb6fe
S="C:/Users/Shlok/AppData/Local/Temp/claude/C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-resume-dlm-discovery-exp-003-334706/bfefb6fe-654c-43b1-a1f0-c80e3f972b2f/scratchpad/ft-dispatch"
P="C:/Users/Shlok/.claude/projects/C--Users-Shlok-Downloads-Multi-Modality-Language-model--claude-worktrees-resume-dlm-discovery-exp-003-334706/bfefb6fe-654c-43b1-a1f0-c80e3f972b2f/subagents"
cd "/c/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706" || exit 1
TR="$1"; shift
export FT_TRANCHE="$TR"
if [ "$1" = build ]; then
  for R in A B; do python -I tools/ft_dispatch.py --role $R --batch "$2" --ids "tools/ft-session/$2.ids" --root "$S" | sed 's/.*ft-dispatch.//'; done
elif [ "$1" = postbatch ]; then
  python -I tools/ft_postbatch.py "$2" "$S" "$P" "$3" "$4" | python -I -c "import json,sys; d=json.load(sys.stdin); print(d['batch'], 'iso', d['isolation_A'], d['isolation_B'], 'model', d.get('model_ok_A'), d.get('model_ok_B'), 'agree', d['agree'], '/', d['n'], 'dis', d['disagree'], 'adj', d['adjudicate'], 'qbad', d.get('quotes_not_accepted_A'), d.get('quotes_not_accepted_B'), 'miss', d['missing_A'], d['missing_B'])"
  git add "analysis/screening/ft-$TR" tools/ft-session/agent-map.txt >/dev/null 2>&1; git commit -q -m "Full-text $TR $2 filed

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" >/dev/null 2>&1 && echo committed
elif [ "$1" = cpost ]; then
  python -I tools/ft_cpost.py "$2" "$S" "$P" "$3"
  git add "analysis/screening/ft-$TR" analysis/screening/c-run-log.jsonl tools/ft-session/agent-map.txt >/dev/null 2>&1; git commit -q -m "Full-text $TR C group $2 filed

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" >/dev/null 2>&1 && echo committed
fi
