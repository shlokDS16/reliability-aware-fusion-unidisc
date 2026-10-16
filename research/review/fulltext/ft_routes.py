#!/usr/bin/env python
"""Full-text ACCESS-ROUTE table for the 1,000 records that passed title/abstract screening.

Metadata/API lookups only. Nothing is downloaded (no PDF, no full text).
Run:  python -I ft_routes.py            (responses are cached in ./cache, reruns are cheap)

Inputs (read only):
  research/review/screening/v2/screener-{A,B}-batch-*.jsonl      (only the 'id' and 'decision' fields are used)
  research/review/corpus/new-records-2026-10-15-v2.jsonl         (metadata by 'nid')
  research/review/screening/v2/dual-subscription/passed-ta.jsonl (46 U-ids; only 'id' used)
  research/review/corpus/subscription-records-2026-10-15.jsonl   (metadata by 'id')
  research/review/screening/records.jsonl                        (earlier corpus, for duplicate check)
Outputs: ft-routes.jsonl, ft-routes-summary.json (same folder as this script).

APIs: OpenAlex (no key, no mailto; only batched ID/DOI filters, search is not used because it
costs 10x of the shared $0.10/day budget), Crossref (anonymous pool), arXiv API (3.1 s gap).
Semantic Scholar is NOT used.
"""
import glob, hashlib, json, os, re, sys, time, unicodedata, collections
import urllib.request, urllib.error, urllib.parse
import defusedxml.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'cache')
os.makedirs(CACHE, exist_ok=True)
REPO = "C:/Users/Shlok/Downloads/Multi-Modality Language model/.claude/worktrees/resume-dlm-discovery-exp-003-334706/"
R = REPO + 'research/review/'
UA = 'dlm-ft-routes/1.0 (metadata lookups for a literature review)'
THRESH = 0.85
OA_BUDGET_USD = 0.05          # stay well inside the shared $0.10/day OpenAlex allowance

# ---------------------------------------------------------------- http with cache
_last = {}
GAP = {'api.openalex.org': 0.6, 'api.crossref.org': 1.0, 'export.arxiv.org': 4.0, 'api.datacite.org': 0.5}
oa_spent = 0.0
stats = collections.Counter()


class Budget(Exception):
    pass


class ArxivBlocked(Exception):
    pass


def fetch(url, retries=6):
    """GET url -> (status, text). Cached by URL. 404 is cached; 429/5xx/timeouts are not."""
    global oa_spent
    key = hashlib.sha1(url.encode()).hexdigest()
    path = os.path.join(CACHE, key + '.json')
    if os.path.exists(path):
        d = json.load(open(path, encoding='utf-8'))
        stats['cache_hit'] += 1
        return d['status'], d['body']
    host = urllib.parse.urlparse(url).netloc
    if host == 'api.openalex.org' and oa_spent >= OA_BUDGET_USD:
        raise Budget('OpenAlex self-imposed budget reached')
    for attempt in range(retries):
        wait = _last.get(host, 0) + GAP.get(host, 1.0) - time.time()
        if wait > 0:
            time.sleep(wait)
        _last[host] = time.time()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=45) as r:
                body = r.read().decode('utf-8', 'replace')
                status = r.status
        except urllib.error.HTTPError as e:
            status = e.code
            body = e.read().decode('utf-8', 'replace') if e.fp else ''
            if status == 429:
                ra = e.headers.get('Retry-After')
                if host == 'api.openalex.org':
                    raise Budget('OpenAlex 429: ' + body[:200])
                if host == 'export.arxiv.org':
                    raise ArxivBlocked('arXiv 429')
                time.sleep(float(ra) if ra and ra.isdigit() else 10 * (attempt + 1))
                continue
            if status >= 500:
                time.sleep(5 * (attempt + 1))
                continue
        except Exception as e:  # timeout, DNS, ...
            if host == 'export.arxiv.org':
                raise ArxivBlocked('arXiv timeout/error: %s' % e)
            time.sleep(5 * (attempt + 1))
            body, status = str(e), -1
            continue
        stats['http_' + host] += 1
        if host == 'api.openalex.org' and status == 200:
            try:
                oa_spent += float(json.loads(body)['meta'].get('cost_usd', 0.0001))
            except Exception:
                oa_spent += 0.0001
        if status in (200, 404):
            json.dump({'url': url, 'status': status, 'body': body}, open(path, 'w', encoding='utf-8'))
        return status, body
    return -1, ''


# ---------------------------------------------------------------- title tools
def norm_tokens(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c)).casefold()
    return re.sub(r'[^a-z0-9]+', ' ', s).split()


def agree(a, b):
    """Title agreement: normalised exact, else token-set Jaccard. Returns (score, label)."""
    ta, tb = norm_tokens(a), norm_tokens(b)
    if not ta or not tb:
        return 0.0, 'none'
    if ta == tb or ''.join(ta) == ''.join(tb):    # exact after case/punctuation/whitespace normalisation
        return 1.0, 'exact'
    sa, sb = set(ta), set(tb)
    j = len(sa & sb) / len(sa | sb)
    return round(j, 3), 'jaccard'


def containment(a, b):
    """fraction of a's tokens found in b (a = shorter/fragment)"""
    sa, sb = set(norm_tokens(a)), set(norm_tokens(b))
    return len(sa & sb) / len(sa) if sa else 0.0


MONTHS = r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*'


def clean_title(t):
    t = unicodedata.normalize('NFKC', t or '')
    t = re.sub(r';\s*\[.*$', '', t)                       # "; [Chinese title]" suffix
    t = re.sub(r'\$\\[A-Za-z]+\{([^}]*)\}\$', r'\1', t)      # LaTeX wrapper like boldsymbol{d} -> its argument
    t = t.replace('$', '')
    t = re.sub(r'^\s*[\(\[]?\d{4}[a-z]?[\)\]]?[\.\):,]?\s+', '', t)   # "2023b. " / "2023). "
    t = re.sub(r'^\s*[:;,\.]\s*', '', t)
    t = re.sub(r',?\s*(?:' + MONTHS + r'\s+)?\d{4}[a-z]?\s*$', '', t, flags=re.I)  # ", July 2025b"
    t = re.sub(r'\s+A P REPRINT\s*$', '', t)
    t = re.sub(r'\s+', ' ', t).strip(' .,;:')
    return t


BLOG_RE = re.compile(r'blog|notion|deepmind|inceptionlabs|runwayml|\.com\b|medium\.com|news|introducing|press|techcrunch', re.I)


# ---------------------------------------------------------------- id tools
ARX_NEW = re.compile(r'(\d{4}\.\d{4,5})(v\d+)?', re.I)
ARX_OLD = re.compile(r'([a-z\-]+(?:\.[A-Za-z]{2})?/\d{7})(v\d+)?')


def norm_arxiv(x):
    if not x or str(x) == 'None':
        return None
    m = ARX_NEW.search(str(x))
    if m:
        return m.group(1)
    m = ARX_OLD.search(str(x))
    return m.group(1) if m else None


def norm_doi(x):
    if not x or str(x) in ('None', ''):
        return None
    x = str(x).strip().lower()
    x = re.sub(r'^https?://(dx\.)?doi\.org/', '', x)
    return x or None


def arxiv_from_doi(doi):
    if doi and doi.startswith('10.48550/arxiv.'):
        return norm_arxiv(doi[len('10.48550/arxiv.'):])
    return None


def acl_from_doi(doi):
    if doi and doi.startswith('10.18653/v1/'):
        return doi[len('10.18653/v1/'):]
    return None


def rd(p):
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


# ---------------------------------------------------------------- publisher canon
PUB_CANON = [
    (r'institute of electrical|ieee', 'IEEE'),
    (r'elsevier|sciencedirect', 'Elsevier'),
    (r'springer|nature|biomed central|bmc', 'Springer Nature'),
    (r'association for computing machinery|^acm', 'ACM'),
    (r'wiley', 'Wiley'),
    (r'taylor|routledge|francis', 'Taylor & Francis'),
    (r'mdpi|multidisciplinary digital', 'MDPI'),
    (r'frontiers', 'Frontiers'),
    (r'aaai|association for the advancement of artificial', 'AAAI'),
    (r'oxford university press', 'Oxford University Press'),
    (r'cambridge university press', 'Cambridge University Press'),
    (r'sage', 'SAGE'),
    (r'zenodo|cern', 'Zenodo'),
    (r'eurographics', 'Eurographics'),
    (r'science press|chinese academy|computer engineering and applications', 'Chinese domestic publisher'),
]


def canon_pub(p):
    if not p:
        return None
    pl = p.lower()
    for rx, name in PUB_CANON:
        if re.search(rx, pl):
            return name
    return p


# ---------------------------------------------------------------- load
def load_items():
    A, B, fA, fB = {}, {}, {}, {}
    for p in sorted(glob.glob(R + 'screening/v2/screener-A-batch-*.jsonl')):
        for r in rd(p):
            A[r['id']] = r['decision']
    for p in sorted(glob.glob(R + 'screening/v2/screener-B-batch-*.jsonl')):
        for r in rd(p):
            B[r['id']] = r['decision']
    ok = ('include', 'unclear')
    ids_a = sorted(set(i for i, d in A.items() if d in ok) | set(i for i, d in B.items() if d in ok))
    nr = {r['nid']: r for r in rd(R + 'corpus/new-records-2026-10-15-v2.jsonl')}
    items = []
    for i in ids_a:
        r = nr[i]
        items.append(dict(
            id=i, origin='a', title=r['title'], arxiv=norm_arxiv(r.get('arxiv')),
            openreview=r.get('openreview_id') or None, acl=r.get('acl_id') or None,
            doi=norm_doi(r.get('doi')), openalex=(r.get('openalex_id') or '').rsplit('/', 1)[-1] or None,
            venue=r.get('venue'), fragment=bool(r.get('title_fragment')),
            screen='A:%s/B:%s' % (A.get(i, '-'), B.get(i, '-'))))
    sr = {r['id']: r for r in rd(R + 'corpus/subscription-records-2026-10-15.jsonl')}
    ps = rd(R + 'screening/v2/dual-subscription/passed-ta.jsonl')
    for p in ps:
        r = sr[p['id']]
        items.append(dict(
            id=p['id'], origin='b', title=r['title'], arxiv=norm_arxiv(r.get('arxiv')), openreview=None, acl=None,
            doi=norm_doi(r.get('doi')), openalex=None, venue=r.get('venue'), fragment=False,
            screen='A:%s/B:%s' % (p.get('A'), p.get('B'))))
    return items


# ---------------------------------------------------------------- arXiv API
def parse_arxiv(xml):
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    out = []
    try:
        root = ET.fromstring(xml)
    except Exception:
        return out
    for e in root.findall('a:entry', ns):
        idt = e.findtext('a:id', '', ns)
        m = re.search(r'arxiv\.org/abs/(.+?)(v\d+)?$', idt)
        if not m:
            continue
        out.append(dict(id=m.group(1), ver=(m.group(2) or ''),
                        title=re.sub(r'\s+', ' ', e.findtext('a:title', '', ns)).strip(),
                        doi=norm_doi(e.findtext('{http://arxiv.org/schemas/atom}doi', '')) if e.find('{http://arxiv.org/schemas/atom}doi') is not None else None))
    return out


_arxiv_blocked_until = [0.0]
used_source = collections.Counter()


def datacite_query(q, n=5):
    url = 'https://api.datacite.org/dois?query=%s&prefix=10.48550&page%%5Bsize%%5D=%d' % (urllib.parse.quote(q, safe=':()"'), n)
    st, body = fetch(url)
    out = []
    if st == 200:
        for d in json.loads(body).get('data', []):
            a = d['attributes']
            ar = arxiv_from_doi(norm_doi(a.get('doi')))
            ts = a.get('titles') or []
            if ar and ts:
                out.append(dict(id=ar, ver='', title=re.sub(r'\s+', ' ', ts[0].get('title', '')).strip(), doi=norm_doi(a.get('doi'))))
    return out, url


def pp_query(kind, toks, n=5):
    """Preprint search. kind 'phrase' or 'and'. arXiv API first; if it answers 429/timeout, fall back to the
    DataCite index of arXiv DOIs (10.48550/arXiv.*) for 15 minutes, then try arXiv again."""
    if time.time() >= _arxiv_blocked_until[0]:
        if kind == 'phrase':
            q = 'ti:"%s"' % ' '.join(toks)
        else:
            q = ' AND '.join('ti:' + t for t in toks)
        url = 'https://export.arxiv.org/api/query?search_query=%s&max_results=%d' % (urllib.parse.quote(q, safe=':'), n)
        try:
            st, body = fetch(url)
            if st == 200:
                used_source['arxiv-api'] += 1
                return parse_arxiv(body), url, 'arXiv API'
        except ArxivBlocked as e:
            _arxiv_blocked_until[0] = time.time() + 900
            print('!! arXiv API unavailable (%s); using DataCite arXiv-DOI index for 15 min' % e, flush=True)
    if kind == 'phrase':
        q = 'titles.title:"%s"' % ' '.join(toks)
    else:
        q = 'titles.title:(%s)' % ' AND '.join(toks)
    out, url = datacite_query(q, n)
    used_source['datacite'] += 1
    return out, url, 'DataCite arXiv-DOI index'


def arxiv_query(q, n=5):   # kept for reference (unused)
    raise NotImplementedError


def arxiv_by_ids(ids):
    out = {}
    for k in range(0, len(ids), 50):
        chunk = ids[k:k + 50]
        url = 'https://export.arxiv.org/api/query?id_list=%s&max_results=%d' % (','.join(chunk), len(chunk))
        st, body = fetch(url)
        if st == 200:
            for e in parse_arxiv(body):
                out[e['id']] = e
    return out


STOP = set('the of and for with via from into using under over a an in on to by is are as at or its their'.split())


def arxiv_title_search(variants):
    """-> (best_entry|None, score, label, queries, cand_all). Phrase search per variant, then AND-token search."""
    best = (None, 0.0, 'none')
    queries = []
    tried = set()
    cand_all = []

    def consider(cands, srcname):
        nonlocal best
        for c in cands:
            c = dict(c, src=srcname)
            for v in variants:
                s, lab = agree(v, c['title'])
                cand_all.append((s, c, v))
                if s > best[1]:
                    best = (c, s, lab)

    for v in variants:
        toks = norm_tokens(v)
        if len(toks) < 2:
            continue
        key = ' '.join(toks)
        if key in tried:
            continue
        tried.add(key)
        c, url, srcname = pp_query('phrase', toks)
        queries.append(url)
        consider(c, srcname)
        if best[1] >= THRESH:
            return best + (queries, cand_all)
    toks = [t for t in norm_tokens(variants[0]) if len(t) >= 3 and t not in STOP]
    toks = sorted(set(toks), key=lambda t: -len(t))[:7]
    if len(toks) >= 3:
        c, url, srcname = pp_query('and', toks, 10)
        queries.append(url)
        consider(c, srcname)
    return best + (queries, cand_all)


# ---------------------------------------------------------------- Crossref
def crossref_search(variants):
    best = (None, 0.0, 'none')
    queries, cand_all = [], []
    for v in variants:
        if len(norm_tokens(v)) < 2:
            continue
        url = ('https://api.crossref.org/works?query.bibliographic=%s&rows=5&select=DOI,title,publisher,type,container-title'
               % urllib.parse.quote(v))
        st, body = fetch(url)
        queries.append(url)
        if st != 200:
            continue
        for it in json.loads(body)['message']['items']:
            ts = it.get('title') or []
            if not ts:
                continue
            for vv in variants:
                s, lab = agree(vv, ts[0])
                cand_all.append((s, dict(title=ts[0], doi=norm_doi(it['DOI']), publisher=it.get('publisher')), vv))
                if s > best[1]:
                    best = (dict(title=ts[0], doi=norm_doi(it['DOI']), publisher=it.get('publisher')), s, lab)
        if best[1] >= THRESH:
            break
    return best + (queries, cand_all)


def crossref_batch(dois):
    """doi -> {publisher, container, type, title}"""
    out = {}
    dois = sorted(set(dois))
    for k in range(0, len(dois), 40):
        chunk = dois[k:k + 40]
        flt = ','.join('doi:' + urllib.parse.quote(d, safe='/') for d in chunk)
        url = 'https://api.crossref.org/works?filter=%s&rows=%d&select=DOI,title,publisher,type,container-title' % (flt, len(chunk))
        st, body = fetch(url)
        if st == 200:
            for it in json.loads(body)['message']['items']:
                out[norm_doi(it['DOI'])] = dict(publisher=it.get('publisher'), type=it.get('type'),
                                                title=(it.get('title') or [''])[0],
                                                container=(it.get('container-title') or [''])[0])
    return out


def lookup_pub(doi):
    """publisher for one DOI: Crossref work, else DataCite record, else Crossref prefix owner."""
    try:
        st, body = fetch('https://api.crossref.org/works/' + urllib.parse.quote(doi, safe='/'))
        if st == 200:
            return json.loads(body)['message'].get('publisher')
        st, body = fetch('https://api.datacite.org/dois/' + urllib.parse.quote(doi, safe='/'))
        if st == 200:
            p = json.loads(body)['data']['attributes'].get('publisher')
            return p.get('name') if isinstance(p, dict) else p
        st, body = fetch('https://api.crossref.org/prefixes/' + doi.split('/')[0])
        if st == 200:
            return json.loads(body)['message'].get('name')
    except Budget:
        pass
    return None


# ---------------------------------------------------------------- OpenAlex (filters only)
OA_SEL = 'id,doi,title,open_access,best_oa_location,primary_location,locations'


def oa_batch(kind, keys):
    """kind 'doi' or 'openalex'; returns key -> work"""
    out = {}
    keys = sorted(set(keys))
    for k in range(0, len(keys), 50):
        chunk = keys[k:k + 50]
        flt = '%s:%s' % (kind, '|'.join(urllib.parse.quote(x, safe='/()_.-:;') for x in chunk))
        url = 'https://api.openalex.org/works?filter=%s&per-page=%d&select=%s' % (flt, len(chunk), OA_SEL)
        try:
            st, body = fetch(url)
        except Budget as e:
            print('!! OpenAlex stopped:', e)
            break
        if st != 200:
            print('!! OpenAlex status', st, body[:150])
            continue
        for w in json.loads(body)['results']:
            if kind == 'doi':
                out[norm_doi(w.get('doi'))] = w
            else:
                out[w['id'].rsplit('/', 1)[-1]] = w
    return out


ARX_URL = re.compile(r'arxiv\.org/(?:abs|pdf)/([^\s?#]+?)(?:\.pdf)?$', re.I)
OR_URL = re.compile(r'openreview\.net/(?:forum|pdf)\?id=([A-Za-z0-9_\-]+)')
ACL_URL = re.compile(r'aclanthology\.org/([A-Za-z0-9.\-_]+?)(?:\.pdf)?/?$')


def oa_route(w):
    """-> dict(route_type,url,source,oa_status) or None (no OA)"""
    if not w:
        return None
    oa = w.get('open_access') or {}
    locs = [l for l in (w.get('locations') or []) if l]
    bl = w.get('best_oa_location') or {}
    cand_urls = [bl.get('pdf_url'), bl.get('landing_page_url')]
    for l in locs:
        if l.get('is_oa'):
            cand_urls += [l.get('pdf_url'), l.get('landing_page_url')]
    cand_urls.append(oa.get('oa_url'))
    for u in cand_urls:
        if not u:
            continue
        m = ARX_URL.search(u)
        if m and norm_arxiv(m.group(1)):
            a = norm_arxiv(m.group(1))
            return dict(route_type='arxiv', url='https://arxiv.org/pdf/' + a, source='openalex-location', oa_status=oa.get('oa_status'), arxiv=a)
        m = OR_URL.search(u)
        if m:
            return dict(route_type='openreview', url='https://openreview.net/pdf?id=' + m.group(1), source='openalex-location', oa_status=oa.get('oa_status'))
        m = ACL_URL.search(u)
        if m and re.match(r'^[A-Z0-9]+[\.\-]', m.group(1)):
            return dict(route_type='acl', url='https://aclanthology.org/%s.pdf' % m.group(1), source='openalex-location', oa_status=oa.get('oa_status'))
    if oa.get('is_oa') or bl.get('is_oa'):
        u = bl.get('pdf_url') or oa.get('oa_url')
        if not u:
            for l in locs:
                if l.get('is_oa') and l.get('pdf_url'):
                    u = l['pdf_url']
                    break
        if not u:
            u = bl.get('landing_page_url')
        if u:
            return dict(route_type='oa_url', url=u, source='openalex-oa', oa_status=oa.get('oa_status'))
    return None


def oa_publisher(w):
    pl = (w or {}).get('primary_location') or {}
    src = pl.get('source') or {}
    return src.get('host_organization_name') or src.get('display_name')


# ---------------------------------------------------------------- main
def main():
    items = load_items()
    byid = {x['id']: x for x in items}
    print('items', len(items), collections.Counter(x['origin'] for x in items))
    res = {}   # id -> row

    def row(x, **kw):
        base = dict(id=x['id'], origin=x['origin'], screen=x['screen'], title=x['title'], route_type=None, url=None,
                    doi=x['doi'], publisher=None, duplicate_of=None, title_agreement=None, source_of_route=None,
                    oa_status=None, note=None, near_miss=None)
        base.update(kw)
        return base

    # 0. derive ids from DOIs
    for x in items:
        if not x['arxiv']:
            x['arxiv'] = arxiv_from_doi(x['doi'])
            x['arxiv_from'] = 'doi' if x['arxiv'] else None
        if not x['acl'] and not x['arxiv']:
            a = acl_from_doi(x['doi'])
            if a:
                x['acl'] = a
                x['acl_from'] = 'doi'

    # 1. direct routes
    pend_arxiv_check = []
    for x in items:
        if x['arxiv']:
            res[x['id']] = row(x, route_type='arxiv', url='https://arxiv.org/pdf/' + x['arxiv'],
                               source_of_route='record arxiv field' if not x.get('arxiv_from') else 'arXiv DOI (10.48550) in record',
                               title_agreement='unchecked')
            pend_arxiv_check.append(x['arxiv'])
        elif x['openreview']:
            res[x['id']] = row(x, route_type='openreview', url='https://openreview.net/pdf?id=' + x['openreview'],
                               source_of_route='record openreview_id', title_agreement='not_checked')
        elif x['acl']:
            res[x['id']] = row(x, route_type='acl', url='https://aclanthology.org/%s.pdf' % x['acl'],
                               source_of_route='record acl_id' if not x.get('acl_from') else 'ACL DOI (10.18653/v1) in record',
                               title_agreement='not_checked')
    print('direct routes', len(res))

    # 1b. verify arXiv ids by id_list (title agreement) - metadata only
    ax = arxiv_by_ids(sorted(set(pend_arxiv_check)))
    mism = []
    for x in items:
        r = res.get(x['id'])
        if r and r['route_type'] == 'arxiv' and r['title_agreement'] == 'unchecked':
            e = ax.get(x['arxiv'])
            if not e:
                r['title_agreement'] = 'arxiv id not returned by arXiv API'
                continue
            s, lab = agree(clean_title(x['title']), e['title'])
            r['title_agreement'] = '%s=%.2f (id verified via arXiv API id_list)' % (lab, s)
            r['note'] = 'latest version %s' % e['ver'] if e['ver'] else None
            if s < THRESH:
                mism.append((x['id'], x['arxiv'], s, x['title'][:60], e['title'][:60]))
                r['note'] = ((r['note'] or '') + ' ; ID/TITLE MISMATCH, check arxiv id').strip(' ;')
    print('arxiv id/title mismatches (<0.85):', len(mism))

    # 2. records needing more work
    todo = [x for x in items if x['id'] not in res]
    print('todo (DOI-only or no id)', len(todo))

    # duplicate pool
    prev = rd(R + 'screening/records.jsonl')
    pool = []   # (id_label, title, kind)
    for x in items:
        if not x['fragment']:
            pool.append((x['id'], clean_title(x['title']), 'set'))
    for p in prev:
        pool.append((p['sid'], p['title'], 'records.jsonl'))
    set_arx = collections.defaultdict(list)
    set_doi = collections.defaultdict(list)
    for x in items:
        if x['arxiv']:
            set_arx[x['arxiv']].append(x['id'])
        if x['doi']:
            set_doi[x['doi']].append(x['id'])
    prev_arx = {norm_arxiv(p.get('arxiv')): p['sid'] for p in prev if p.get('arxiv')}

    noid = [x for x in todo if not x['doi']]
    doi_only = [x for x in todo if x['doi']]
    print('no identifier (arxiv/openreview/acl/doi):', len(noid), ' doi-only:', len(doi_only))

    # 3. no-identifier records: duplicate check, then OpenAlex id, then title resolution
    def variants_of(x):
        v = [clean_title(x['title'])]
        ven = x.get('venue')
        if x['fragment'] and ven and str(ven) != 'None' and len(ven) < 45 and not re.search(r'arxiv|preprint|proceedings|conference|international|journal|neurips|iclr|icml', ven, re.I):
            v.append(clean_title(x['title'] + ' ' + ven))
        return [t for t in v if t]

    oa_ids = [x['openalex'] for x in noid if x['openalex']]
    oa_by_id = oa_batch('openalex', oa_ids) if oa_ids else {}
    need_doi_check = []   # (x, doi, source, agreement) resolved via crossref -> go to OpenAlex DOI stage

    for x in noid:
        vs = variants_of(x)
        # --- duplicate check (local)
        best = (None, 0.0, None)
        near = (None, 0.0, 0.0, None)
        for (lab, t, kind) in pool:
            if lab == x['id']:
                continue
            for v in vs:
                s, a = agree(v, t)
                if s > best[1]:
                    best = ((lab, t, kind), s, a)
                c = containment(v, t)
                if len(norm_tokens(v)) >= 4 and c == 1.0 and s > near[1] - 1 and s >= near[1]:
                    near = ((lab, t, kind), s, c, a)
        # lower-id fragments as duplicate targets
        for y in noid:
            if y['id'] < x['id'] and y['fragment']:
                for v in vs:
                    for w in variants_of(y):
                        s, a = agree(v, w)
                        if s > best[1]:
                            best = ((y['id'], w, 'set'), s, a)
        if best[0] and best[1] >= THRESH:
            lab, t, kind = best[0]
            res[x['id']] = row(x, route_type='duplicate', duplicate_of=lab if kind == 'set' else 'records.jsonl:%s' % lab,
                               title_agreement='%s=%.2f' % (best[2], best[1]),
                               source_of_route='local title agreement with %s %s' % (kind, lab),
                               note='matched title: ' + t[:100])
            continue
        if near[0] and near[0][2] == 'set':
            x['_near_dup'] = '%s (%s) containment=1.0 jaccard=%.2f' % (near[0][0], near[0][1][:70], near[1])
        elif near[0]:
            x['_near_dup'] = 'records.jsonl:%s (%s) containment=1.0 jaccard=%.2f' % (near[0][0], near[0][1][:70], near[1])
        # --- OpenAlex id
        if x['openalex'] and x['openalex'] in oa_by_id:
            w = oa_by_id[x['openalex']]
            rt = oa_route(w)
            s, a = agree(clean_title(x['title']), w.get('title') or '')
            wd = norm_doi(w.get('doi'))
            if rt:
                res[x['id']] = row(x, route_type=rt['route_type'], url=rt['url'], doi=x['doi'] or wd,
                                   title_agreement='openalex-id exact; title %s=%.2f' % (a, s),
                                   source_of_route='openalex_id %s -> %s' % (x['openalex'], rt['source']), oa_status=rt['oa_status'],
                                   publisher=canon_pub(oa_publisher(w)))
                continue
            if wd:
                x['doi'] = wd
                need_doi_check.append(x)
                x['_via'] = 'openalex_id %s -> doi' % x['openalex']
                continue
            res[x['id']] = row(x, route_type='no_full_text', title_agreement='openalex-id; title %s=%.2f' % (a, s),
                               source_of_route='openalex_id %s' % x['openalex'],
                               note='OpenAlex work has no OA location and no DOI', publisher=canon_pub(oa_publisher(w)))
            continue
        # --- title resolution
        ntok = len(norm_tokens(clean_title(x['title'])))
        if ntok > 22 or ntok == 0:
            res[x['id']] = row(x, route_type='no_full_text', title_agreement='n/a',
                               source_of_route='none', note='text fragment, not a title (%d tokens); unresolvable' % ntok)
            continue
        e, s, lab, qs, cands = arxiv_title_search(vs)
        found = None
        if e and s >= THRESH:
            found = dict(route_type='arxiv', url='https://arxiv.org/pdf/' + e['id'], arxiv=e['id'],
                         src='%s title search (%s)' % (e.get('src', 'arXiv API'), qs[-1]), ag='%s=%.2f' % (lab, s), matched=e['title'])
        else:
            c, s2, lab2, qs2, cands2 = crossref_search(vs)
            if c and s2 >= THRESH:
                ad = arxiv_from_doi(c['doi'])
                if ad:
                    found = dict(route_type='arxiv', url='https://arxiv.org/pdf/' + ad, arxiv=ad,
                                 src='Crossref title search -> arXiv DOI (%s)' % qs2[-1], ag='%s=%.2f' % (lab2, s2), matched=c['title'])
                else:
                    x['doi'] = c['doi']
                    x['_via'] = 'Crossref title search (%s)' % qs2[-1]
                    x['_ag'] = '%s=%.2f' % (lab2, s2)
                    x['_matched'] = c['title']
                    need_doi_check.append(x)
                    continue
            else:
                # near misses for the report
                allc = [(sc, cc['title'], 'arxiv:' + cc['id']) for sc, cc, v in cands] + \
                       [(sc, cc['title'], 'doi:' + (cc['doi'] or '')) for sc, cc, v in cands2]
                allc.sort(key=lambda t: -t[0])
                nm = None
                if allc and allc[0][0] >= 0.5:
                    nm = '%s jaccard=%.2f "%s"' % (allc[0][2], allc[0][0], allc[0][1][:90])
                # containment-only candidate (fragment fully contained in candidate title)
                if not nm:
                    for sc, cc, v in cands:
                        if len(norm_tokens(v)) >= 4 and containment(v, cc['title']) == 1.0:
                            nm = 'arxiv:%s containment=1.0 jaccard=%.2f "%s"' % (cc['id'], sc, cc['title'][:90])
                            break
                x['_near_miss'] = nm
        if found:
            # identifier-level duplicate check
            dup = set_arx.get(found['arxiv']) or []
            dup = [d for d in dup if d != x['id']]
            if dup or found['arxiv'] in prev_arx:
                tgt = dup[0] if dup else 'records.jsonl:%s' % prev_arx[found['arxiv']]
                res[x['id']] = row(x, route_type='duplicate', duplicate_of=tgt, title_agreement=found['ag'],
                                   source_of_route='resolved by ' + found['src'] + '; same arXiv id %s' % found['arxiv'],
                                   note='matched title: ' + found['matched'][:100])
            else:
                res[x['id']] = row(x, route_type=found['route_type'], url=found['url'], title_agreement=found['ag'],
                                   source_of_route=found['src'], note='matched title: ' + found['matched'][:100])
            continue
        # unresolved
        reason = None
        ven = str(x.get('venue') or '')
        if BLOG_RE.search(ven) or BLOG_RE.search(x['title'] or ''):
            reason = 'non-paper (blog/news/web post or product page); not in arXiv or Crossref by title'
        elif x['fragment']:
            reason = 'reference-list fragment, no arXiv/Crossref title agreement >= %.2f' % THRESH
        else:
            reason = 'no arXiv/Crossref title agreement >= %.2f' % THRESH
        res[x['id']] = row(x, route_type='no_full_text', title_agreement='best<%.2f' % THRESH,
                           source_of_route='title search (arXiv API blocked: HTTP 429; DataCite arXiv-DOI index + Crossref used)',
                           note=reason + ('; venue=%s' % ven if ven and ven != 'None' else ''),
                           near_miss=x.get('_near_miss') or x.get('_near_dup'))

    # 4. OpenAlex DOI stage (doi-only records + those resolved through Crossref/openalex id)
    stage = doi_only + need_doi_check
    dois = [x['doi'] for x in stage]
    oa_by_doi = oa_batch('doi', dois)
    print('OpenAlex DOI batch: asked %d, got %d; spent $%.4f' % (len(set(dois)), len(oa_by_doi), oa_spent))
    # Crossref for publisher / existence
    cr = crossref_batch(dois)
    print('Crossref batch: got', len(cr))
    for x in stage:
        d = x['doi']
        w = oa_by_doi.get(d)
        rt = oa_route(w)
        pub_raw = (cr.get(d) or {}).get('publisher') or lookup_pub(d) or oa_publisher(w)
        pub = canon_pub(pub_raw)
        if w:
            s, a = agree(clean_title(x['title']), w.get('title') or '')
            tagr = 'doi-exact; openalex title %s=%.2f' % (a, s)
        elif d in cr:
            s, a = agree(clean_title(x['title']), cr[d]['title'])
            tagr = 'doi-exact (Crossref only); title %s=%.2f' % (a, s)
        else:
            tagr = 'doi not found in OpenAlex or Crossref'
        via = x.get('_via')
        if via:
            tagr = x.get('_ag', tagr) + ' (resolved via %s)' % via
        src_prefix = (via + ' -> ') if via else ''
        dd = [i for i in set_doi.get(d, []) if i != x['id']]
        if x in need_doi_check and dd:
            res[x['id']] = row(x, route_type='duplicate', duplicate_of=dd[0], title_agreement=tagr,
                               source_of_route=src_prefix + 'same DOI as ' + dd[0])
            continue
        if rt:
            res[x['id']] = row(x, route_type=rt['route_type'], url=rt['url'], publisher=pub, title_agreement=tagr,
                               source_of_route=src_prefix + rt['source'], oa_status=rt['oa_status'],
                               note=('OpenAlex oa_status=%s' % rt['oa_status']) + (' (bronze: free-to-read, check licence)' if rt['oa_status'] == 'bronze' else ''))
        else:
            x['_gw'] = dict(pub=pub, tagr=tagr, src=src_prefix, pub_raw=pub_raw, oa=(w or {}).get('open_access', {}).get('oa_status'))

    # 5. arXiv preprint fallback for DOI records without OA
    gw = [x for x in stage if '_gw' in x]
    print('no OA via OpenAlex -> arXiv title fallback for', len(gw))
    for n, x in enumerate(gw):
        vs = [clean_title(x['title'])]
        e, s, lab, qs, cands = arxiv_title_search(vs)
        g = x['_gw']
        if e and s >= THRESH:
            res[x['id']] = row(x, route_type='arxiv', url='https://arxiv.org/pdf/' + e['id'], publisher=g['pub'],
                               title_agreement='%s=%.2f' % (lab, s), source_of_route=g['src'] + '%s title search fallback (%s)' % (e.get('src', 'arXiv API'), qs[-1]),
                               note='preprint version; publisher version (doi %s) is paywalled/closed; matched: %s' % (x['doi'], e['title'][:80]))
        else:
            nm = None
            if cands:
                cands.sort(key=lambda t: -t[0])
                if cands[0][0] >= 0.5:
                    nm = 'arxiv:%s jaccard=%.2f "%s"' % (cands[0][1]['id'], cands[0][0], cands[0][1]['title'][:80])
            res[x['id']] = row(x, route_type='e-gateway', url='https://doi.org/' + x['doi'], publisher=g['pub'],
                               title_agreement=g['tagr'], source_of_route=g['src'] + 'OpenAlex: no OA location; arXiv title search: no agreement >= %.2f' % THRESH,
                               oa_status=g['oa'], near_miss=nm,
                               note='publisher_raw=%s' % g['pub_raw'] + ('' if g['pub_raw'] else '; venue=%s' % x.get('venue')))
        if n % 20 == 0:
            print('  arxiv fallback', n, '/', len(gw), flush=True)

    # 6. anything still missing (should not happen)
    for x in items:
        if x['id'] not in res:
            res[x['id']] = row(x, route_type='no_full_text', note='no route computed (bug or API outage)')

    # 7. write outputs
    order = {x['id']: k for k, x in enumerate(items)}
    rows = [res[i] for i in sorted(res, key=lambda i: order[i])]
    FIELDS = ['id', 'origin', 'title', 'route_type', 'url', 'doi', 'publisher', 'duplicate_of', 'title_agreement',
              'source_of_route', 'oa_status', 'note', 'near_miss', 'candidate_url', 'screen']
    for r in rows:
        nm = r.get('near_miss') or ''
        m = re.match(r'arxiv:(\S+) ', nm)
        m2 = re.match(r'(?:records\.jsonl:)?doi:(\S+) ', nm)
        r['candidate_url'] = ('https://arxiv.org/pdf/' + m.group(1)) if m else (('https://doi.org/' + m2.group(1)) if m2 else None)
    with open(os.path.join(HERE, 'ft-routes.jsonl'), 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps({k: r.get(k) for k in FIELDS}, ensure_ascii=False) + '\n')

    # dup info: same arXiv id under several ids inside the set (informational)
    multi = {a: ids for a, ids in set_arx.items() if len(ids) > 1}
    summ = dict(
        n_records=len(rows),
        by_route_type=dict(collections.Counter(r['route_type'] for r in rows)),
        by_origin={o: dict(collections.Counter(r['route_type'] for r in rows if r['origin'] == o)) for o in 'ab'},
        n_by_origin=dict(collections.Counter(r['origin'] for r in rows)),
        e_gateway_by_publisher=dict(collections.Counter(r['publisher'] or 'unknown' for r in rows if r['route_type'] == 'e-gateway').most_common()),
        e_gateway_by_origin=dict(collections.Counter(r['origin'] for r in rows if r['route_type'] == 'e-gateway')),
        no_identifier_records=dict(
            total=len(noid),
            resolved_to_a_route=sum(1 for x in noid if res[x['id']]['route_type'] in ('arxiv', 'openreview', 'acl', 'oa_url', 'e-gateway')),
            duplicates=sum(1 for x in noid if res[x['id']]['route_type'] == 'duplicate'),
            unresolvable=sum(1 for x in noid if res[x['id']]['route_type'] == 'no_full_text'),
            fragments_total=sum(1 for x in noid if x['fragment']),
            fragments_by_route_type=dict(collections.Counter(res[x['id']]['route_type'] for x in noid if x['fragment'])),
            non_fragments_by_route_type=dict(collections.Counter(res[x['id']]['route_type'] for x in noid if not x['fragment'])),
            duplicates_of_records_jsonl=sum(1 for x in noid if str(res[x['id']].get('duplicate_of')).startswith('records.jsonl:')),
            duplicates_of_set_record=sum(1 for x in noid if res[x['id']]['route_type'] == 'duplicate' and not str(res[x['id']].get('duplicate_of')).startswith('records.jsonl:')),
            unresolvable_with_near_miss=sum(1 for x in noid if res[x['id']]['route_type'] == 'no_full_text' and res[x['id']].get('near_miss')),
        ),
        oa_status_counts=dict(collections.Counter(r.get('oa_status') for r in rows if r['route_type'] == 'oa_url')),
        doi_records_with_low_title_agreement=[dict(id=r['id'], doi=r['doi'], title=r['title'][:80], agreement=r['title_agreement'])
                                              for r in rows if r['origin'] and (r['title_agreement'] or '').startswith('doi-exact') and re.search(r'=(0\.\d+)', r['title_agreement']) and float(re.search(r'=(0\.\d+)', r['title_agreement']).group(1)) < 0.6],
        near_miss_candidates=sum(1 for r in rows if r['route_type'] == 'no_full_text' and r.get('candidate_url')),
        arxiv_id_title_mismatches=[dict(id=i, arxiv=a, jaccard=s, record_title=t, arxiv_title=at) for i, a, s, t, at in mism],
        same_arxiv_id_under_multiple_ids_in_set={a: ids for a, ids in multi.items()},
        api_calls=dict(stats), preprint_search_source=dict(used_source), openalex_spent_usd=round(oa_spent, 5),
        threshold=THRESH,
    )
    json.dump(summ, open(os.path.join(HERE, 'ft-routes-summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(summ, ensure_ascii=False, indent=1)[:6000])


if __name__ == '__main__':
    main()
