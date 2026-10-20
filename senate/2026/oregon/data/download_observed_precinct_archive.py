"""Follow the actual public Download form; retain one exact split gzip stream."""
from pathlib import Path
from urllib.parse import urljoin, urlencode
import argparse
import datetime
import gzip
import hashlib
import json
import requests
from bs4 import BeautifulSoup

DATA = Path(__file__).resolve().parent
NEWS = DATA/'news'
CAP = 32000000


class Parts:
    def __init__(self,stem):
        self.stem = stem
        self.parts = []
        self.handle = None
        self.used = 0
        self.total = 0
        self.digest = hashlib.sha256()

    def write(self,b):
        self.digest.update(b)
        self.total += len(b)
        view = memoryview(b)
        while view:
            if self.handle is None or self.used == CAP:
                if self.handle:
                    self.handle.close()
                path = NEWS/f'{self.stem}.html.gz.part{len(self.parts):03d}'
                assert not path.exists()
                self.parts.append(path)
                self.handle = path.open('wb')
                self.used = 0
            n = min(len(view),CAP-self.used)
            self.handle.write(view[:n])
            self.used += n
            view = view[n:]
        return len(b)

    def flush(self):
        if self.handle:
            self.handle.flush()

    def close(self):
        if self.handle:
            self.handle.close()

    def pins(self):
        return [{'asset':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in self.parts]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('year',choices=['2020','2022'])
    args = ap.parse_args()
    mf = json.loads((NEWS/'manifest.json').read_bytes())
    sid = f'sos-{args.year}-precinct-zip-observed-download'
    assert sid not in {r['id'] for r in mf}
    parent = next(s for s in mf if s['id'] == f'sos-{args.year}-precinct-zip-public-detail-post')
    stored = (NEWS/parent['asset']).read_bytes()
    assert hashlib.sha256(stored).hexdigest() == parent['stored_sha256']
    original = gzip.decompress(stored)
    assert hashlib.sha256(original).hexdigest() == parent['raw_sha256']
    html = BeautifulSoup(original,'html.parser')
    form = html.find('form')
    payload = {}
    for i in form.find_all('input'):
        typ,name = i.get('type','text'),i.get('name')
        if not name or typ in ['button','submit'] or typ in ['radio','checkbox'] and not i.has_attr('checked'):
            continue
        payload[name] = i.get('value','')
    button = form.find('input',attrs={'value':'Download','type':'submit'})
    assert button is not None and button.get('aria-label') == 'Download Document'
    payload[button['name']] = button['value']
    request = urlencode(payload).encode()
    request_path = NEWS/f'{sid}.request.txt.gz'
    assert not request_path.exists()
    request_stored = gzip.compress(request,mtime=0)
    request_path.write_bytes(request_stored)
    url = urljoin(parent['final_url'],form['action'])
    record = {'id':sid,'url':url,'request_method':'POST read-only observed public Download button',
              'parent_source_id':parent['id'],'source_title_literal':parent['source_title_literal'],
              'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'request_body_asset':request_path.name,'request_body_sha256':hashlib.sha256(request).hexdigest(),
              'request_body_stored_sha256':hashlib.sha256(request_stored).hexdigest()}
    writer = Parts(sid)
    raw_sha = hashlib.sha256()
    raw_bytes = 0
    try:
        with requests.post(url,data=payload,stream=True,timeout=35) as response:
            record.update(status=response.status_code,final_url=response.url,headers=dict(response.headers),
                          redirects=[{'url':r.url,'status':r.status_code,'location':r.headers.get('Location')}
                                     for r in response.history])
            print(json.dumps({'id':sid,'status':response.status_code,'headers':dict(response.headers)}),flush=True)
            with gzip.GzipFile(filename='',fileobj=writer,mode='wb',mtime=0) as out:
                for chunk in response.iter_content(65536):
                    raw_sha.update(chunk)
                    raw_bytes += len(chunk)
                    out.write(chunk)
    except requests.RequestException as error:
        record['error'] = str(error)
        record['entity_completeness'] = 'transport_interrupted_prefix_retained_not_complete'
    finally:
        writer.close()
    record.update(completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  raw_sha256=raw_sha.hexdigest(),bytes=raw_bytes,stored_sha256=writer.digest.hexdigest(),
                  stored_bytes=writer.total,asset_parts=writer.pins(),
                  storage='Ordered exact segments of one lossless gzip response-entity stream, each<=32000000bytes')
    if 'error' not in record:
        record['entity_completeness'] = 'response_stream_finished_content_validation_pending'
    current = json.loads((NEWS/'manifest.json').read_bytes())
    assert sid not in {r['id'] for r in current}
    current.append(record)
    (NEWS/'manifest.json').write_text(json.dumps(current,indent=2)+'\n')
    print(json.dumps({k:record.get(k) for k in ['id','status','bytes','raw_sha256','stored_bytes','entity_completeness','error']}),flush=True)


if __name__ == '__main__':
    main()
