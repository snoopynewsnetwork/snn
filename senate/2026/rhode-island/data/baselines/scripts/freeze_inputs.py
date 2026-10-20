"""One-time receipt freeze, before any peer numerical derivative is read.
Only original acquisition receipts and original response bytes are inputs.
"""
import gzip, hashlib, json, re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
STATE = BASE.parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()

def main():
    dest = BASE / 'source/inputs.json'
    if dest.exists():
        raise SystemExit('Immutable inputs already frozen; use extraction, do not replace.')
    news = STATE / 'data/news'
    manifest = json.loads((news / 'manifest.json').read_text())
    wanted = ['boe-history', 'boe-publications', 'boe-2024-summary',
              'ri-2024-general-old-authority', 'ri-2024-data-index', 'ri-2024-senate',
              'ri-2024-original-data-zip', 'ri-2024-layout-zip', 'ri-2022-description',
              'ri-2020-observed-historical-seed', 'ri-2020-observed-state-summary',
              'ri-2020-observed-short-zip', 'ri-2020-observed-long-zip',
              'ri-2020-observed-format-description', 'ri-2022-observed-historical-seed',
              'ri-2022-observed-data-index', 'ri-2022-observed-short-zip',
              'ri-2022-observed-long-zip']
    out = []
    def add(r, path, receipt):
        stored = path.read_bytes(); raw = gzip.decompress(stored)
        assert sha(raw) == r['raw_sha256']
        if r.get('stored_sha256'): assert sha(stored) == r['stored_sha256']
        out.append(dict(id=r['id'], url=r['url'], final_url=r.get('final_url'),
                        status=r.get('status'), retrieved_at_utc=r.get('retrieved_at_utc'),
                        headers=r.get('headers'), raw_sha256=sha(raw), raw_bytes=len(raw),
                        stored_sha256=sha(stored), stored_bytes=len(stored),
                        body_path=str(path.relative_to(STATE)), compression='gzip',
                        original_receipt=receipt))
    for name in wanted:
        r = next(r for r in manifest if r['id'] == name)
        add(r, news / r['asset'], r)
    acquired = STATE / 'data/turnout/source/acquired'
    extras = ['board2024-xlsx','board2020-pdf','board2022-pdf','board2020-xlsx',
              'board2022-xlsx','board2024-writeins-xlsx','board2020-writeins-pdf',
              'board2022-writeins-pdf','boe-current-history','boe-publications-current',
              'boe-faq','boe-preresults','census-municipal-ids']
    for year, ident in [(2024,'ri-2024-general-old-authority'),
                        (2020,'ri-2020-observed-state-summary'),
                        (2022,'ri-2022-observed-historical-seed')]:
        item = next(x for x in out if x['id'] == ident)
        b = gzip.decompress((STATE / item['body_path']).read_bytes()).decode()
        towns = re.findall(r'href="/election/results/'+str(year)+r'/general_election/([^/\"]+)/"', b)
        towns = list(dict.fromkeys(t for t in towns if t not in ['data','races']))
        assert len(towns) == 39, towns
        extras += [f'{year}-town-{t}' for t in towns]
    for name in extras:
        receipt = json.loads((acquired / (name+'.receipt.json')).read_text())
        assert receipt.get('status') == 200, name
        add(receipt, STATE / 'data/turnout' / receipt['stored_path'], receipt)
    dest.write_text(json.dumps(out, indent=2)+'\n')
    print(len(out), 'fixed original receipts frozen', sha(dest.read_bytes()))

if __name__ == '__main__': main()
