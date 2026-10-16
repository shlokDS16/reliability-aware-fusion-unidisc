# usage: python -I orbatch.py <repo> <dispatch root> <n0 convert-log lines before> <first batch number> <part number> <seed>
import json,random,sys
from pathlib import Path
R,S,n0,first,part,seed=Path(sys.argv[1]),Path(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6])
log=[json.loads(l) for l in open(R/'research/review/fulltext/convert-pymupdf-log.jsonl',encoding='utf-8')]
new=log[n0:]; print('converted',len(new),{r['status'] for r in new},max([r.get('glued_rate',0) for r in new] or [0]))
screened=set()
for p in (R/'research/review/fulltext').glob('t1-batches-part*.json'):
    for v in json.load(open(p))['batches'].values(): screened|=set(v)
ids=[r['id'] for r in new if r['status']=='ok' and r['id'] not in screened]
random.Random(seed).shuffle(ids)
b={f't1b{first+k//10:03d}':ids[k:k+10] for k in range(0,len(ids),10)}
json.dump({'tranche':'T1','part':f'OpenReview API downloads (route openreview-api), converted log lines {n0+1}-{len(log)}','seed':seed,'n':len(ids),'batches':b},open(R/f'research/review/fulltext/t1-batches-part{part}.json','w'),indent=1)
for k,v in b.items():
    open(S/f'{k}.ids','w').write('\n'.join(v)+'\n'); open(R/f'tools/ft-session/{k}.ids','w').write('\n'.join(v)+'\n')
print(b)
