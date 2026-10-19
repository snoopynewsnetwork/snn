#!/usr/bin/env python3
"""Bounded public acquisition; original historical assets reused read-only by extract.py."""
from pathlib import Path
import datetime,gzip,hashlib,json
import requests
D=Path(__file__).resolve().parent
SOURCES=[
 ('results-index','https://voteidaho.gov/election-results/',None),
 ('general-2026','https://voteidaho.gov/idaho-general-election/','results-index'),
 ('stats-2022','https://voteidaho.gov/election-results/2022-election-stats/','results-index'),
 ('results-2020','https://voteidaho.gov/election-results/2020-election-results/','results-index'),
 ('ballot-info','https://voteidaho.gov/on-the-ballots/','general-2026'),
 ('casting-ballot','https://voteidaho.gov/casting-your-ballot/','general-2026'),
 ('certificate-2026','https://voteidaho.gov/event/secretary-of-state-to-issue-certificates-2/','results-index'),
 ('law-34-1215','https://legislature.idaho.gov/statutesrules/idstat/Title34/T34CH12/SECT34-1215/',None),
 ('law-34-1216','https://legislature.idaho.gov/statutesrules/idstat/Title34/T34CH12/SECT34-1216/',None),
 ('law-34-1101','https://legislature.idaho.gov/statutesrules/idstat/Title34/T34CH11/SECT34-1101/',None),
 ('timezone','https://www.ecfr.gov/current/title-49/subtitle-A/part-71/section-71.9',None),
 ('calendar-2026','https://archive.voteidaho.gov/download/2026-election-calendar.pdf','general-2026'),
]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 out=[];folder=D/'source/http';folder.mkdir(parents=True,exist_ok=True)
 for sid,url,parent in SOURCES:
  receipt=dict(id=sid,requested_url=url,parent_id=parent,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),method='GET')
  try:
   r=requests.get(url,timeout=60);b=r.content;s=gzip.compress(b,mtime=0);p=folder/(sid+'-'+sha(b)[:12]+'.gz');p.write_bytes(s)
   receipt.update(status=r.status_code,final_url=r.url,headers=dict(r.headers),redirects=[dict(status=a.status_code,url=a.url,headers=dict(a.headers))for a in r.history],raw_bytes=len(b),raw_sha256=sha(b),stored_path=str(p.relative_to(D)),stored_bytes=len(s),stored_sha256=sha(s),representation='complete decoded HTTP response entity; lossless gzip; wire headers retained')
  except Exception as e:receipt.update(status=None,error=str(e))
  out.append(receipt);print(sid,receipt['status'],receipt.get('raw_bytes'))
 (D/'source/acquisition.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
