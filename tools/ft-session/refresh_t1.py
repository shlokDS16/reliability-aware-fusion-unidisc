"""Refresh t1-decisions-all.jsonl and t1-summary-all.json (same logic as the 3f113e6 refresh; a third part for
part 19, t1b077 on). Run from the worktree root:  python -I refresh_t1.py <last batch, e.g. t1b082> <last C group, e.g. 16> <last queue part>"""
import json, collections, sys
from pathlib import Path
last, lastc, lastq = sys.argv[1:4]
base = Path('analysis/screening/ft-t1')
A = {}; B = {}; bo = {}
for d in sorted(base.glob('t1b0*')):
    for role, st in (('A', A), ('B', B)):
        for l in open(d / f'F{role}-{d.name}.jsonl', encoding='utf-8'):
            if l.strip(): r = json.loads(l); st[r['id']] = r; bo[r['id']] = d.name
PEND = {json.loads(l)['id']: json.loads(l) for l in open(base / 't1-pending-B.jsonl', encoding='utf-8') if l.strip()} if (base / 't1-pending-B.jsonl').exists() else {}
assert set(A) - set(PEND) == set(B), sorted((set(A) - set(PEND)) ^ set(B))   # B-unavailable records wait for the human author
for i in PEND:
    A.pop(i, None)
SUP = {(r['id'], r['group']) for r in map(json.loads, open(base / 'c-superseded.jsonl', encoding='utf-8')) if r} if (base / 'c-superseded.jsonl').exists() else set()
C = {}
for f in sorted(base.glob('c/c-t1-*/FC-*.jsonl')):
    for l in open(f, encoding='utf-8'):
        if l.strip():
            r = json.loads(l)
            if (r['id'], f.parent.name) not in SUP:   # superseded rulings (c-superseded.jsonl) are not used
                C[r['id']] = r
need = [i for i in A if (A[i]['decision'] != B[i]['decision'] or 'adjudicate' in (A[i]['decision'], B[i]['decision'])) and i not in C]
assert not need, need
rows = []
for i in sorted(A):
    src = 'C' if i in C else 'A=B'; r = C[i] if i in C else A[i]
    rows.append({'id': i, 'batch': bo[i], 'decision': r['decision'], 'code': r.get('code', ''), 'xsub': r.get('xsub', ''), 'i1': r.get('i1', ''),
                 'nonlang_only': r.get('nonlang_only', False), 'source': src, 'A': A[i]['decision'], 'B': B[i]['decision']})
with open(base / 't1-decisions-all.jsonl', 'w', encoding='utf-8', newline='\n') as f:
    for r in rows: f.write(json.dumps(r) + '\n')
def part(b):
    if b >= 't1b077': return f'part 19: retrieved after T1 (t1b077-{last})'
    return 'OpenReview (t1b035-t1b076)' if b >= 't1b035' else 'open access + remaps (t1b001-t1b034)'
s = {'scope': f'T1 full-text model screening, batches t1b001-{last}',
     'status': 'model screening (A, B, C route F); A-B agreement only (D0034); ' + ('T1 screened so far (interim): part 19 screened; 3 awaiting the second screener (D0041); 18 unscreened sampled records moved to R797 (D0035); records awaiting retrieval not yet screened' if last == 't1b093' else f'part 19 screened to {last}') + '; before the human author review (protocol s4 step 4); not final',
     'n': len(rows), 'pending_B_unavailable': sorted(PEND),
     'decision': dict(collections.Counter(r['decision'] for r in rows)),
     'by_part': {p: dict(collections.Counter(r['decision'] for r in rows if part(r['batch']) == p)) for p in sorted({part(r['batch']) for r in rows})},
     'exclude_codes': dict(collections.Counter(r['code'] for r in rows if r['decision'] == 'exclude')),
     'include_i1': dict(collections.Counter(r['i1'] for r in rows if r['decision'] == 'include')),
     'include_nonlang_only': sum(1 for r in rows if r['decision'] == 'include' and r['nonlang_only']),
     'adjudicated_by_C': len(C), 'C_decision': dict(collections.Counter(C[i]['decision'] for i in C)),
     'not_retrieved_X6': sum(1 for l in open(base / 't1-not-retrieved.jsonl', encoding='utf-8') if l.strip()),
     'files': f't1-decisions-all.jsonl; t1-not-retrieved.jsonl; c-queue-1..{lastq}.jsonl; c/c-t1-01..{lastc}; analysis/screening/c-run-log.jsonl; batch-log.jsonl'}
json.dump(s, open(base / 't1-summary-all.json', 'w', encoding='utf-8', newline='\n'), indent=1)
print(json.dumps(s, indent=1))
