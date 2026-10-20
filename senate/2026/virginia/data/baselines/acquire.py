"""Public GET evidence recorder. Never overwrites an existing receipt."""
import argparse, datetime, gzip, hashlib, json, urllib.request, urllib.error
from pathlib import Path
ROOT = Path(__file__).resolve().parent
def fetch(key, url, parent):
    dest = ROOT/'source/acquired'
    dest.mkdir(parents=True, exist_ok=True)
    receipt = dest/(key+'.receipt.json')
    if receipt.exists():
        raise ValueError('receipt already exists; use a new vintage key')
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args): return None
    opener = urllib.request.build_opener(NoRedirect)
    hops=[]; requested=url
    for i in range(8):
        headers={'User-Agent':'Virginia-partisanship-public-research/1.0','Accept-Encoding':'identity'}
        now=datetime.datetime.now(datetime.timezone.utc).isoformat()
        try: response=opener.open(urllib.request.Request(url,headers=headers),timeout=60)
        except urllib.error.HTTPError as e: response=e
        body=response.read(); compressed=gzip.compress(body,mtime=0)
        assert len(compressed)<40000000
        file=dest/(key+f'.hop{i}.gz');file.write_bytes(compressed)
        hops.append(dict(request_url=url,request_headers=headers,retrieved_at_utc=now,status=response.code,response_headers=list(response.headers.items()),response_url=response.geturl(),body_path=str(file.relative_to(ROOT)),raw_bytes=len(body),raw_sha256=hashlib.sha256(body).hexdigest(),stored_bytes=len(compressed),stored_sha256=hashlib.sha256(compressed).hexdigest()))
        if response.code in (301,302,303,307,308):
            url=urllib.parse.urljoin(url,response.headers['Location']);continue
        break
    result=dict(id=key,requested_url=requested,parent_source=parent,final_url=url,hops=hops,transport='Complete response entity after HTTP transfer framing; identity requested. No TLS/wire packet capture.')
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(key,response.code,len(body))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('key');p.add_argument('url');p.add_argument('parent');a=p.parse_args();fetch(a.key,a.url,a.parent)
