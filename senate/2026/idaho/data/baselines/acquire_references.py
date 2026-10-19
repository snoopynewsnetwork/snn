#!/usr/bin/env python3
"""Fill original Census receipt and retain the actual primary write-in comparator."""
import datetime,gzip,json
import requests
from extract import D,sha,save
def main():
 out=[]
 for sid,url in [('Census-county-FIPS','https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt'),('actual-2022-primary-governor-writeins','https://archive.sos.idaho.gov/elections/data/results/2022/Primary/WriteIn_Governor.pdf')]:
  utc=datetime.datetime.now(datetime.timezone.utc).isoformat();r=requests.get(url,timeout=60);b=r.content
  rec=dict(id=sid,requested_url=url,final_url=r.url,retrieved_utc=utc,status=r.status_code,headers=dict(r.headers),redirects=[dict(url=a.url,status=a.status_code,headers=dict(a.headers))for a in r.history],raw_sha256=sha(b),raw_bytes=len(b))
  if sid=='Census-county-FIPS':
   path=D.parent/'turnout/source/fips2020.gz';stored=path.read_bytes();assert gzip.decompress(stored)==b;rec.update(relative_path='../turnout/source/fips2020.gz',stored_sha256=sha(stored),stored_bytes=len(stored),original_retained_once=True)
  else:
   path=D/'source/http/actual-2022-primary-governor-writeins.gz';stored=gzip.compress(b,mtime=0);path.write_bytes(stored);rec.update(relative_path=str(path.relative_to(D)),stored_sha256=sha(stored),stored_bytes=len(stored),parent_url='https://voteidaho.gov/election-results/',parent_literal_link='2022 Primary Election / Write-in Totals: Governor')
  out.append(rec)
 save('source/independent-reference-receipts.json',out)
if __name__=='__main__':main()
