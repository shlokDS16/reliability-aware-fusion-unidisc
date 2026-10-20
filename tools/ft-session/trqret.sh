#!/bin/bash
# Later tranches (as qret.sh for T1). usage: trqret.sh <tranche> <batch> <role> <agent> <agentA> <agentB> <ids comma>
# Logs the one quote return, re-runs the batch post-check (ft_postbatch via tr.sh), logs quotes still not accepted.
cd "/c/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706" || exit 1
TR="$1"; B="$2"; R="$3"; AG="$4"; AA="$5"; AB="$6"; IDS="$7"
python -I -c "
import json,sys
t,b,r,a,ids=sys.argv[1:6]
open(f'analysis/screening/ft-{t}/batch-log.jsonl','a',encoding='utf-8',newline='\n').write(json.dumps({'event':'quote_return','batch':b,'role':r,'agent':a,'ids':ids.split(','),'outcome':'returned once; batch re-checked (result line follows)'})+'\n')" "$TR" "$B" "$R" "$AG" "$IDS"
bash tools/ft-session/tr.sh "$TR" postbatch "$B" "$AA" "$AB" >/dev/null
tail -1 "analysis/screening/ft-$TR/batch-log.jsonl" | cut -c1-400
python -I -c "
import json,sys
t,b,r,ids=sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4].split(',')
bad=[json.loads(l) for l in open(f'analysis/screening/ft-{t}/{b}/quote-check-{r}.jsonl',encoding='utf-8') if json.loads(l).get('status')!='found' and json.loads(l)['id'] in ids]
with open(f'analysis/screening/ft-{t}/batch-log.jsonl','a',encoding='utf-8',newline='\n') as f:
    for q in bad:
        f.write(json.dumps({'event':'quote_after_return','batch':b,'role':r,'id':q['id'],'i':q['i'],'status':q['status'],'action':'record goes to adjudication (criteria-v1.6 s5.2)'})+'\n')
print('still not accepted:',[(q['id'],q['i'],q['status']) for q in bad])" "$TR" "$B" "$R" "$IDS"
git add "analysis/screening/ft-$TR" >/dev/null 2>&1; git commit -q -m "$TR $B $R: quote return re-check

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" >/dev/null 2>&1 && echo committed
