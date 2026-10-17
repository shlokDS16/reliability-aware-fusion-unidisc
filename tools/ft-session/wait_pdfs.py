# Exit when >= N unconverted complete PDFs are waiting, or the OpenReview download looks finished (ok+error >= TOTAL), or after MAXMIN minutes.
import json, sys, time
from pathlib import Path
N, TOTAL, MAXMIN = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
t0 = time.time()
while True:
    try:
        fl = [json.loads(l) for l in open('research/review/fulltext/fetch-log.jsonl', encoding='utf-8') if l.strip()]
        ok = {r['id'] for r in fl if r.get('status') == 'ok'}
        orr = [r for r in fl if r.get('route') == 'openreview-api']
        done = {json.loads(l)['id'] for l in open('research/review/fulltext/convert-pymupdf-log.jsonl', encoding='utf-8') if l.strip()}
        todo = ({p.stem for p in Path('research/sources/pdfs/fulltext').glob('*.pdf')} - done) & ok
        if len(todo) >= N or len(orr) >= TOTAL or time.time() - t0 > MAXMIN * 60:
            print(f"waiting={len(todo)} openreview_logged={len(orr)} minutes={int((time.time()-t0)/60)}")
            break
    except Exception as e:
        pass
    time.sleep(60)
