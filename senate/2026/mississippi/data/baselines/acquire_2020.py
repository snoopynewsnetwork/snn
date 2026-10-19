"""Acquire every actual parent-linked 2020 county original, including amendments."""
import concurrent.futures,datetime,gzip,html,json,re,urllib.parse,urllib.request
from sources import *
def main():
    parent='sos-2020-county-index';text=original(parent).decode();url=references()[parent]['final_url']
    links=[(html.unescape(label),urllib.parse.urljoin(url,html.unescape(href))) for href,label in re.findall(r'<a[^>]+href="([^"]+\.pdf)"[^>]*>(.*?)</a>',text,re.I)]
    save(OUT/'source/county-2020-links.json',[dict(label=l,url=u,parent_source_id=parent) for l,u in links])
    existing={r['url']:r for r in references().values()};todo=[(l,u) for l,u in links if u not in existing]
    def fetch(pair):
        label,url=pair;key='sos-2020-county-'+re.sub('[^a-z0-9]+','-',label.lower()).strip('-')
        p=OUT/'source'/(key+'.body.gz');receipt=p.with_suffix('.json')
        if receipt.exists():return json.loads(receipt.read_text())
        redirects=[]
        class Redirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,req,fp,code,msg,headers,newurl):
                redirects.append(dict(url=req.full_url,status=code,headers=dict(headers),location=newurl))
                return super().redirect_request(req,fp,code,msg,headers,newurl)
        start=datetime.datetime.now(datetime.timezone.utc).isoformat();opener=urllib.request.build_opener(Redirect())
        requested=urllib.parse.quote(url,safe=':/%?=&')
        with opener.open(urllib.request.Request(requested,headers={'User-Agent':'Public historical election research'}),timeout=90) as response:
            raw=response.read();headers=dict(response.headers);final=response.url;status=response.status
        assert raw.startswith(b'%PDF'),(url,raw[:30]);packed=gzip.compress(raw,mtime=0);assert len(packed)<40000000
        p.write_bytes(packed);r=dict(id=key,source_label=label,url=url,final_url=final,redirects=redirects,status=status,headers=headers,retrieved_at_utc=start,raw_sha256=sha(raw),raw_bytes=len(raw),stored_sha256=sha(packed),stored_bytes=len(packed),path=str(p.relative_to(BASE)),parent_source_id=parent,storage='owned_lossless_gzip');save(receipt,r);return r
    dest=OUT/'source/downloads.json';records=json.loads(dest.read_text()) if dest.exists() else [];byid={r['id']:r for r in records}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for r in pool.map(fetch,todo):
            byid[r['id']]=r;save(dest,list(byid.values()));print(r['id'],r['raw_bytes'],flush=True)
    pin()
if __name__=='__main__':main()
