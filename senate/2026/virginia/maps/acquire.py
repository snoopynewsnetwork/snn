"""Bounded public map acquisition. Complete entities once by hash; no overwrite.

Python -B acquire.py KEY URL PARENT [JSON_LOOKUP_FIELDS]
GET unless JSON_LOOKUP_FIELDS supplied (read-only form lookup POST).
"""
import datetime, gzip, hashlib, json, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs): return None

def fetch(key, url, parent, fields=None):
    path = HERE / 'requests' / (key + '.json'); path.parent.mkdir(exist_ok=True)
    if path.exists(): return json.loads(path.read_bytes())
    headers = {'User-Agent': 'Virginia precinct map research (public read-only sources)', 'Accept-Encoding': 'identity'}
    data = urllib.parse.urlencode(fields).encode() if fields is not None else None
    method = 'POST' if data is not None else 'GET'
    record = {'key': key, 'source_parent_edge': parent, 'requested_url': url, 'method': method, 'request_headers': headers, 'submitted_lookup_fields': fields, 'started_utc': now(), 'hops': [], 'entity_scope': 'complete HTTP response entities after transfer framing; not TLS wire captures'}
    opener = urllib.request.build_opener(NoRedirect())
    for _ in range(12):
        hop = {'url': url, 'request_method': method, 'request_headers': headers, 'submitted_lookup_fields': fields, 'started_utc': now()}
        try:
            try: response = opener.open(urllib.request.Request(url, headers=headers, data=data, method=method), timeout=65)
            except urllib.error.HTTPError as error: response = error
            with response:
                b = response.read()
                hop.update({'status': response.code, 'response_headers': list(response.headers.raw_items()), 'final_response_url': response.geturl(), 'complete_body': True, 'raw_bytes': len(b), 'raw_sha256': sha(b), 'parts': []})
                stored = gzip.compress(b, mtime=0)
                for i in range(0, len(stored), 39000000):
                    chunk = stored[i:i+39000000]; out = HERE / 'originals' / (sha(chunk) + '.gzpart')
                    out.parent.mkdir(exist_ok=True)
                    if out.exists(): assert out.read_bytes() == chunk
                    else: out.write_bytes(chunk)
                    hop['parts'].append({'path': str(out.relative_to(HERE)), 'bytes': len(chunk), 'sha256': sha(chunk)})
                hop['stored_gzip_bytes'] = len(stored); hop['stored_gzip_sha256'] = sha(stored)
                hop['source_clock_headers'] = [[k,v] for k,v in hop['response_headers'] if k.lower() in ('date','last-modified','etag','expires','age')]
                hop['finished_utc'] = now(); record['hops'].append(hop)
                location = response.headers.get('Location')
                if response.code in (301,302,303,307,308) and location:
                    url = urllib.parse.urljoin(url, location)
                    if response.code == 303 or response.code in (301,302) and method == 'POST': method='GET'; data=None
                    continue
                break
        except Exception as error:
            hop.update({'error_type': type(error).__name__, 'error': str(error), 'complete_body': False, 'status': None, 'response_headers': None, 'raw_bytes': None, 'raw_sha256': None, 'parts': [], 'finished_utc': now()})
            record['hops'].append(hop); break
    record.update({'finished_utc': now(), 'final_url': url})
    path.write_text(json.dumps(record, indent=2) + '\n')
    return record

def entity(record):
    hop=record['hops'][-1]
    if not hop['complete_body']: return None
    stored=b''.join((HERE / p['path']).read_bytes() for p in hop['parts'])
    assert len(stored)==hop['stored_gzip_bytes'] and sha(stored)==hop['stored_gzip_sha256']
    b=gzip.decompress(stored)
    assert len(b)==hop['raw_bytes'] and sha(b)==hop['raw_sha256']
    return b

if __name__=='__main__':
    result=fetch(sys.argv[1],sys.argv[2],sys.argv[3],json.loads(sys.argv[4]) if len(sys.argv)>4 else None)
    print(json.dumps({'key':result['key'],'final_url':result['final_url'],'hops':[{k:h.get(k) for k in ('status','raw_bytes','error_type','error')} for h in result['hops']]}))
