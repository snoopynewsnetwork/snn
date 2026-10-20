#!/usr/bin/env python3
from pathlib import Path
import requests,gzip,json,hashlib,datetime
P=Path(__file__).resolve().parent

def main():
 rows=[]
 for sid,url in [('senate-class-II','https://www.senate.gov/senators/Class_II.htm'),('senate-class-I','https://www.senate.gov/senators/Class_I.htm')]:
  now=datetime.datetime.now(datetime.timezone.utc).isoformat();r=requests.get(url,timeout=45,headers={'Accept-Encoding':'identity'});b=r.content;z=gzip.compress(b,mtime=0);path=P/'source/current'/(sid+'.gz');path.write_bytes(z);rows.append(dict(id=sid,requested_url=url,final_url=r.url,retrieved_utc=now,status=r.status_code,response_headers=dict(r.headers),redirect_chain=[dict(url=x.url,status=x.status_code,headers=dict(x.headers)) for x in r.history],asset='source/current/'+path.name,raw_sha256=hashlib.sha256(b).hexdigest(),stored_sha256=hashlib.sha256(z).hexdigest(),raw_bytes=len(b),stored_bytes=len(z),discovery='Official Senate class rosters browsed directly; ClassII referenced by state README, ClassI linked there'))
  (P/'source/support-acquisition.json').write_text(json.dumps(rows,indent=2)+'\n')
 print([(r['id'],r['status'],r['raw_bytes']) for r in rows])
if __name__=='__main__':main()
