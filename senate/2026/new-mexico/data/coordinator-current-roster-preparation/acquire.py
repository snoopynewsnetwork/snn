"""Bounded coordinator public-link preparation; no form/auth/private lookups."""
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
import gzip
import hashlib
import json
import urllib.parse
import requests

D = Path(__file__).resolve().parent


def sha(b):
    return hashlib.sha256(b).hexdigest()


def store(b):
    z = gzip.compress(b, mtime=0)
    assert len(z) < 40000000
    p = D / (sha(b)+'.gz')
    if not p.exists():
        p.write_bytes(z)
    return dict(path=p.name, raw_bytes=len(b), raw_sha256=sha(b),
                stored_bytes=len(z), stored_sha256=sha(z))


def fetch(key, url, parent=None, literal_href=None):
    path = D / (key+'.receipt.json')
    if path.exists():
        r = json.loads(path.read_bytes())
        raw = gzip.decompress((D / r['body']['path']).read_bytes()) if r.get('body') else b''
        return raw, r
    r = dict(requested_url=url, parent=parent, literal_href=literal_href, method='GET',
             started_utc=datetime.now(timezone.utc).isoformat(), hops=[], status=None, error=None)
    try:
        current = url
        for _ in range(8):
            x = requests.get(current, headers={'User-Agent':'Public Senate research'}, timeout=(20,45), allow_redirects=False)
            r['hops'].append(dict(url=x.url, utc=datetime.now(timezone.utc).isoformat(),
                                 status=x.status_code, request_headers=dict(x.request.headers),
                                 response_headers=dict(x.headers), body=store(x.content)))
            r.update(status=x.status_code, final_url=x.url, body=store(x.content))
            if not x.is_redirect:
                break
            target = urllib.parse.urljoin(x.url,x.headers['Location'])
            assert not any(w in urllib.parse.urlsplit(target).path.lower().split('/') for w in ['login','account','admin','signin']), target
            current = target
        else:
            raise RuntimeError('bounded redirect limit')
        raw = x.content
    except Exception as e:
        r['error'] = str(e)
        raw = b''
    r['finished_utc'] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(r, indent=2)+'\n')
    print(key,r['status'],len(raw),flush=True)
    return raw,r


class Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and 'href' in a:
            self.links.append(dict(href=a['href'],raw_tag=self.get_starttag_text()))


if __name__=='__main__':
    raw,r=fetch('sos-home','https://www.sos.nm.gov/')
    p=Links();p.feed(raw.decode('utf-8','replace'))
    selected=[v for v in p.links if 'candidateportal.servis.sos.state.nm.us' in v['href'].lower()]
    (D/'observed-candidate-links.json').write_text(json.dumps(selected,indent=2)+'\n')
    observed=[v for v in selected if dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(v['href']).query))=={'eid':'2917','cty':'99'}]
    assert observed, 'Use only actual current home anchor; no guessed election ID'
    fetch('linked-candidate-list',observed[0]['href'],'sos-home.receipt.json',observed[0]['href'])
