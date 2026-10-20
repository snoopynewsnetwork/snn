#!/usr/bin/env python3
"""Retain complete HTTP response body, lossless compressed, and immutable receipt."""
import argparse,datetime,gzip,hashlib,json,pathlib,requests
ROOT=pathlib.Path(__file__).resolve().parents[1]
def fetch(url,parent=None):
 t=datetime.datetime.now(datetime.timezone.utc).isoformat(); out=ROOT/'source/http';out.mkdir(parents=True,exist_ok=True)
 r=requests.get(url,timeout=(20,100),headers={'User-Agent':'Alabama-election-research/1.0 (public source archival)'})
 b=r.content; h=hashlib.sha256(b).hexdigest(); z=gzip.compress(b,mtime=0); parts=[]
 for i in range(0,len(z),30000000):
  p=out/(h+'.gz'+(f'.part{i//30000000:03}' if len(z)>=40000000 else ''))
  if p.exists():assert p.read_bytes()==z[i:i+30000000] if len(z)>=40000000 else p.read_bytes()==z
  else:p.write_bytes(z[i:i+30000000] if len(z)>=40000000 else z)
  parts.append({'path':str(p.relative_to(ROOT)), 'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  if len(z)<40000000:break
 rec={'requested_url':url,'final_url':r.url,'retrieved_at_utc':t,'status':r.status_code,'headers':dict(r.headers),'redirects':[{'url':a.url,'status':a.status_code,'headers':dict(a.headers)} for a in r.history],'original_sha256':h,'original_bytes':len(b),'storage':'concatenate parts in listed order then gzip.decompress; requests-decoded entity body; HTTP content-encoding retained in headers','parts':parts,'parent':parent}
 stamp=t.replace(':','').replace('.',''); p=out/(stamp+'-'+h[:12]+'.receipt.json');p.write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps({'receipt':str(p.relative_to(ROOT)),**rec}));return b,rec
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('url');a.add_argument('--parent');v=a.parse_args();fetch(v.url,v.parent)
