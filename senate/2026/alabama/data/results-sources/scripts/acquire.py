"""Bounded public-source acquisition. No automatic URL discovery or retries."""
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {'User-Agent': 'Alabama-official-source-research/1.0 (bounded public read-only research)',
           'Accept': '*/*', 'Accept-Encoding': 'identity'}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def save_body(b):
    z = gzip.compress(b, mtime=0)
    parts = []
    for i in range(0, len(z), 30000000):
        chunk = z[i:i+30000000]
        name = f'http/{sha(b)}.{i//30000000:03d}.gzpart'
        p = ROOT/name
        if p.exists():
            assert p.read_bytes() == chunk
        else:
            p.write_bytes(chunk)
        parts.append({'path': name, 'bytes': len(chunk), 'sha256': sha(chunk)})
    return {'bytes': len(b), 'sha256': sha(b), 'parts': parts,
            'encoding': 'concatenate listed parts then gzip.decompress once; complete requests-decoded entity'}

def fetch(url, parent, method='GET', fields=None):
    assert method in ('GET', 'POST')
    assert url.startswith(('https://','http://'))
    start = dt.datetime.now(dt.timezone.utc).isoformat()
    record = {'requested_url': url, 'method': method, 'fields': fields,
              'parent_evidence': parent, 'started_utc': start,
              'configured_headers': HEADERS, 'hops': []}
    session = requests.Session()
    try:
        response = session.request(method, url, data=fields, headers=HEADERS,
                                   timeout=(15,45), allow_redirects=True)
        for r in [*response.history, response]:
            body = r.content
            record['hops'].append({'url': r.url, 'status': r.status_code,
                'headers': list(r.raw.headers.items()), 'request_url': r.request.url,
                'request_method': r.request.method, 'request_headers': dict(r.request.headers),
                'request_body': r.request.body.decode() if isinstance(r.request.body, bytes) else r.request.body,
                'body': save_body(body)})
        record['status'] = 'response-observed'
    except requests.RequestException as e:
        record.update(status='unavailable-no-response', error_type=type(e).__name__, error=str(e),
                      response_status=None, response_headers=None, response_body=None)
    finally:
        record['ended_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        name = 'http/'+start.replace(':','').replace('.','')+'-'+sha(url.encode())[:12]+'.receipt.json'
        (ROOT/name).write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')
    return name, record

def body(record):
    v = record['hops'][-1]['body']
    b = gzip.decompress(b''.join((ROOT/p['path']).read_bytes() for p in v['parts']))
    assert len(b)==v['bytes'] and sha(b)==v['sha256']
    return b

if __name__ == '__main__':
    import sys
    if sys.argv[1] == '--batch':
        from concurrent.futures import ThreadPoolExecutor
        jobs=json.loads(Path(sys.argv[2]).read_bytes())
        def run(j):
            name,r=fetch(**j)
            return {'receipt':name,'url':j['url'],'status':r['status'],
                    'responses':[(h['status'],h['body']['bytes']) for h in r['hops']]}
        with ThreadPoolExecutor(max_workers=4) as pool:
            for result in pool.map(run,jobs): print(json.dumps(result),flush=True)
    else:
        name, r = fetch(sys.argv[1], sys.argv[2])
        print(name, r['status'], [(h['status'],h['body']['bytes']) for h in r['hops']])
