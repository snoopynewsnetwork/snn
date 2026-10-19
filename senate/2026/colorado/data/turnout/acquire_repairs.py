#!/usr/bin/env python3
from pathlib import Path
import requests,gzip,json,hashlib,datetime
O=Path(__file__).resolve().parent;S=O/'source'
def main():
 a=json.loads((S/'acquisition.json').read_text())
 for sid,url,parent in [
 ('census-colorado-codes','https://tigerweb.geo.census.gov/tigerwebmain/Files/acs26/tigerweb_acs26_county_2020_tab20_co.html','actual indexed Census primary county table'),
 ('scotus-stay-opinion','https://www.supremecourt.gov/opinions/25pdf/26a305_4g15.pdf','official docket literal Opinion anchor independently opened in browser'),
 ('booklet-2022-official','https://www.sos.state.co.us/pubs/elections/Results/Abstract/2022/2022BiennialAbstractOfVotesCast.pdf','actual indexed official original; vendor file497403retained')]:
  r=requests.get(url,timeout=90);b=r.content;z=gzip.compress(b,mtime=0);(S/(sid+'.body.gz')).write_bytes(z);a.append(dict(id=sid,requested_url=url,final_url=r.url,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=r.status_code,headers=dict(r.headers),redirects=[dict(url=x.url,status=x.status_code,headers=dict(x.headers))for x in r.history],raw_sha256=hashlib.sha256(b).hexdigest(),raw_bytes=len(b),stored_sha256=hashlib.sha256(z).hexdigest(),stored_bytes=len(z),asset=sid+'.body.gz',parent=parent,entity_scope='complete decoded response body'));assert len(z)<40000000;(S/'acquisition.json').write_text(json.dumps(a,indent=2)+'\n');print(sid,r.status_code,len(b),flush=True)
if __name__=='__main__':main()
