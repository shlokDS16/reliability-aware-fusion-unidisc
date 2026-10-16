#!/bin/bash
# usage: qret.sh <batch> <role> <agent> <agentA> <agentB> <ids comma>  -- logs the return, rechecks the batch, logs leftovers
cd "/c/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706" || exit 1
python -I -c "
import json,sys
b,r,a,ids=sys.argv[1:5]
open('analysis/screening/ft-t1/batch-log.jsonl','a',encoding='utf-8',newline='\n').write(json.dumps({'event':'quote_return','batch':b,'role':r,'agent':a,'ids':ids.split(','),'outcome':'returned once; batch re-checked (result line follows)'})+'\n')" "$1" "$2" "$3" "$6"
bash tools/ft-session/next.sh postbatch "$1" "$4" "$5" >/dev/null
tail -1 analysis/screening/ft-t1/batch-log.jsonl | cut -c1-400
python -I -c "
import json,sys
b,r,ids=sys.argv[1],sys.argv[2],sys.argv[3].split(',')
bad=[json.loads(l) for l in open(f'analysis/screening/ft-t1/{b}/quote-check-{r}.jsonl',encoding='utf-8') if json.loads(l).get('status')!='found' and json.loads(l)['id'] in ids]
with open('analysis/screening/ft-t1/batch-log.jsonl','a',encoding='utf-8',newline='\n') as f:
    for q in bad:
        f.write(json.dumps({'event':'quote_after_return','batch':b,'role':r,'id':q['id'],'i':q['i'],'status':q['status'],'action':'record goes to adjudication (criteria-v1.6 s5.2)'})+'\n')
print('still not accepted:',[(q['id'],q['i'],q['status']) for q in bad])" "$1" "$2" "$6"
git add analysis/screening/ft-t1 >/dev/null 2>&1; git commit -q -m "T1 $1 $2: quote return re-check

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" >/dev/null 2>&1 && echo committed
