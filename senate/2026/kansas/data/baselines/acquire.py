"""Acquire bounded current primary pages. Shared historical originals stay read-only."""
from pathlib import Path
import datetime, gzip, hashlib, json, urllib.request, urllib.error
H=Path(__file__).resolve().parent
STAT='https://www.kslegislature.gov/b2025_26/laws/'
SOURCES=[
 ('current-results','https://www.sos.ks.gov/elections/election-results.html','SOS election authority'),
 ('class-II','https://www.senate.gov/senators/Class_II.htm','US Senate class roster'),
 ('class-III','https://www.senate.gov/senators/Class_III.htm','US Senate class roster'),
 ('current-candidates','https://www.sos.ks.gov/elections/elections_upcoming_candidate.aspx','current-results: Candidate List'),
 ('current-dates','https://www.sos.ks.gov/elections/important-election-dates.html','current-results: Important Election Dates'),
 ('statute-25-702',STAT+'025_000_0000_chapter/025_007_0000_article/025_007_0002_section/025_007_0002_k/','general election plurality law'),
 ('statute-25-1132',STAT+'025_000_0000_chapter/025_011_0000_article/025_011_0032_section/025_011_0032_k/','operative advance receipt law'),
 ('statute-25-1221',STAT+'025_000_0000_chapter/025_012_0000_article/025_012_0021_section/025_012_0021_k/','federal services receipt exception'),
 ('statute-25-1216',STAT+'025_000_0000_chapter/025_012_0000_article/025_012_0016_section/025_012_0016_k/','federal services electronic transmission'),
 ('statute-25-1136',STAT+'025_000_0000_chapter/025_011_0000_article/025_011_0036_section/025_011_0036_k/','late/eligibility and provisional treatment'),
 ('statute-25-3002',STAT+'025_000_0000_chapter/025_030_0000_article/025_030_0002_section/025_030_0002_k/','canvass and write-in rule')]
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
    manifest=[]
    for sid,url,parent in SOURCES:
        m=dict(id=sid,requested_url=url,parent=parent,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        redirects=[]
        class Redirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,req,fp,code,msg,headers,newurl):
                redirects.append(dict(from_url=req.full_url,status=code,to_url=newurl,headers=dict(headers)))
                return super().redirect_request(req,fp,code,msg,headers,newurl)
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Kansas historical election research','Accept-Encoding':'identity'})
            try: response=urllib.request.build_opener(Redirect()).open(req,timeout=30)
            except urllib.error.HTTPError as e: response=e
            body=response.read(); headers=dict(response.headers)
            m.update(status=response.status,final_url=response.geturl(),headers=headers,redirects=redirects,response_body_sha256=sha(body),response_body_bytes=len(body))
            raw=gzip.decompress(body) if headers.get('Content-Encoding','').lower()=='gzip' else body
            stored=gzip.compress(raw,mtime=0); path='source/'+sid+'.body.gz'; (H/path).write_bytes(stored)
            m.update(path=path,raw_sha256=sha(raw),raw_bytes=len(raw),stored_sha256=sha(stored),stored_bytes=len(stored),content_decoding=headers.get('Content-Encoding','identity'))
        except Exception as e: m['error']=repr(e)
        manifest.append(m)
    (H/'source/acquisition.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__': main()
