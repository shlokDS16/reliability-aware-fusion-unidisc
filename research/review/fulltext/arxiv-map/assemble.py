import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, collections
from lib import *

def L(n):
    p = os.path.join(HERE, n)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}

F = {x['id']: x for x in L('failed.json')} if False else {x['id']: x for x in json.load(open(os.path.join(HERE, 'failed.json'), encoding='utf-8'))}
dc, dc2, ax, pat, zn, cr = L('dc_results.json'), L('dc2_results.json'), L('arxiv_api_results.json'), L('pattern_results.json'), L('zenodo_results.json'), L('crossref_results.json')

mapped, unmapped = [], []
for i, x in F.items():
    fr = x['log']['route']; title = x['route']['title']
    cands = list(dc.get(i) or []) + list(dc2.get(i) or []) + list((ax.get(i) or {}).get('found') or [])
    row = None
    if cands:
        # best score, prefer exact/non-loose; collect alternates with other arXiv ids
        cands.sort(key=lambda c: (c['loose'], -c['score']))
        best = cands[0]
        alts = sorted({c['arxiv_id'] for c in cands if c['arxiv_id'] != best['arxiv_id']})
        corroborated = sorted({c['method'].split('_')[0] for c in cands if c['arxiv_id'] == best['arxiv_id']})
        aid = best['arxiv_id']
        new_url = 'https://arxiv.org/pdf/' + aid
        note = None
        if i == 'M04571':
            new_url = 'https://arxiv.org/pdf/2501.15405v1'
            note = 'Same arXiv id as the failed route. v2 is a withdrawn stub (1 KB; withdrawn by arXiv Admin, disputed authorship per abs page) so /pdf/2501.15405 returns 404; v1 PDF returns 200 application/pdf on HEAD. Content of v1 not read. Flag for inclusion: withdrawn paper.'
        row = dict(id=i, failed_route=fr, new_url=new_url, route_kind='arxiv', arxiv_id=aid, method=best['method'],
                   title_agreement='%s=%.2f%s' % (best['label'], best['score'], ' (loose: prefix-extension, Jaccard>=0.75)' if best['loose'] else ''),
                   loose=bool(best['loose']), record_title=title, arxiv_title=best['cand_title'], query_url=best['query_url'],
                   confirmed_by=corroborated, alt_arxiv_ids=alts, note=note)
    elif i in pat and pat[i].get('head_status') == 200 and (
            'pdf' in (pat[i].get('content_type') or '').lower()
            or pat[i]['method'].startswith('zenodo') or pat[i]['method'].startswith('crossref_link:techscience')):
        p = pat[i]
        row = dict(id=i, failed_route=fr, new_url=p['url'], route_kind='direct_pdf', arxiv_id=None, method=p['method'],
                   title_agreement='doi-exact (route from same DOI)' if not p['method'].startswith('zenodo') else p['method'].split('(', 1)[-1].rstrip(')'),
                   loose=False, record_title=title, arxiv_title=None, query_url=None, confirmed_by=['HEAD'],
                   head_status=p['head_status'], head_content_type=p.get('content_type'),
                   note='HEAD only, nothing downloaded' + ('; Content-Type octet-stream (Zenodo API content endpoint serves PDFs this way), check %PDF magic on download' if (p.get('content_type') or '').startswith('application/octet') else ''))
    if row: mapped.append(row)
    else:
        reason = []
        if i in pat: reason.append('pattern candidate %s -> HEAD %s %s' % (pat[i]['url'][:80], pat[i].get('head_status'), (pat[i].get('content_type') or '')[:30]))
        if i in zn and zn[i].get('status') != 200: reason.append('zenodo api %s' % zn[i].get('status'))
        elif i in zn and not pat.get(i): reason.append('zenodo record has no matching PDF file: %s' % [f[0] for f in zn[i].get('files', [])][:3])
        unmapped.append(dict(id=i, failed_route=fr, url_tried=x['route']['url'], record_title=title, doi=x['route'].get('doi'), publisher=x['route'].get('publisher'), reason='; '.join(reason) or 'no arXiv title match in DataCite/arXiv API; no known OA PDF pattern'))

with open(os.path.join(HERE, 'arxiv-map.jsonl'), 'w', encoding='utf-8') as f:
    for r in mapped: f.write(json.dumps(r, ensure_ascii=False) + '\n')
with open(os.path.join(HERE, 'unmapped.jsonl'), 'w', encoding='utf-8') as f:
    for r in unmapped: f.write(json.dumps(r, ensure_ascii=False) + '\n')
tot = collections.Counter(x['log']['route'] for x in F.values())
m_arx = collections.Counter(r['failed_route'] for r in mapped if r['route_kind'] == 'arxiv')
m_dir = collections.Counter(r['failed_route'] for r in mapped if r['route_kind'] == 'direct_pdf')
loose = [r['id'] for r in mapped if r['loose']]
summ = dict(failed_total=len(F), failed_by_route=dict(tot), mapped_arxiv_by_route=dict(m_arx), mapped_direct_pdf_by_route=dict(m_dir),
            mapped_total=len(mapped), unmapped_total=len(unmapped), unmapped_by_route=dict(collections.Counter(r['failed_route'] for r in unmapped)),
            loose_ids=loose, arxiv_api_queries_done=len(ax), arxiv_api_coverage_of_unmapped_after_datacite=('%d of %d' % (len(ax), sum(1 for i in F if not dc.get(i)))),
            unmapped_ids=[r['id'] for r in unmapped])
json.dump(summ, open(os.path.join(HERE, 'arxiv-map-summary.json'), 'w', encoding='utf-8'), indent=1)
print(json.dumps({k: v for k, v in summ.items() if k != 'unmapped_ids'}, indent=1))
