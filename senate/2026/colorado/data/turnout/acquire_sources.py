#!/usr/bin/env python3
"""Retain complete decoded HTTP entities, response chains and lossless gzip; shared originals by hash."""
from pathlib import Path
import requests,datetime,gzip,hashlib,json,re
from urllib.parse import urljoin
O=Path(__file__).resolve().parent; N=O.parent/'news'; S=O/'source'; S.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 shared=json.loads((N/'manifest.json').read_text()); pins=[]
 for a in shared:
  if not a['id'].startswith('sos'):continue
  b=(N/a['asset']).read_bytes();raw=gzip.decompress(b); assert sha(b)==a['stored_sha256'] and sha(raw)==a['raw_sha256'] and len(raw)==a['bytes']
  pins.append(dict(a,reference_path='../../news/'+a['asset'],reuse='original shared asset read-only; no duplicate'))
 (S/'shared-source-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
 records=[];bodies={}
 def get(sid,url,parent=None):
  t=datetime.datetime.now(datetime.timezone.utc).isoformat();r=requests.get(url,timeout=90);raw=r.content;b=gzip.compress(raw,mtime=0);p=S/(sid+'.body.gz');p.write_bytes(b)
  assert len(b)<40000000
  rec=dict(id=sid,requested_url=url,final_url=r.url,retrieved_at_utc=t,status=r.status_code,headers=dict(r.headers),redirects=[dict(url=x.url,status=x.status_code,headers=dict(x.headers))for x in r.history],raw_sha256=sha(raw),raw_bytes=len(raw),stored_sha256=sha(b),stored_bytes=len(b),asset=p.name,parent=parent,entity_scope='requests decoded complete response body; HTTP content-encoding decoded, no truncation')
  records.append(rec);bodies[sid]=raw
  (S/'acquisition.json').write_text(json.dumps(records,indent=2)+'\n');print(sid,r.status_code,len(raw),flush=True)
  return raw
 get('current-results-index','https://www.sos.state.co.us/pubs/elections/resultsData.html')
 get('current-archive','https://www.sos.state.co.us/pubs/elections/Results/Archives.html','current-results-index')
 for year,kind,cid in [(2024,'president','26499'),(2022,'senate','25990'),(2020,'senate','3602')]:
  sid=f'current-{year}-{kind}';s=get(sid,f'https://historicalelectiondata.coloradosos.gov/contest/{cid}','current-results-index').decode()
  anchors=re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>',s,re.S)
  urls=[u.replace('&amp;','&')for u,t in anchors if 'download_contest' in u and '_table.csv' in u];assert len(set(urls))==1
  get(sid+'-csv',urls[0],sid+' literal download href')
 for year in [2022,2020]:
  get(f'turnout-{year}',f'https://www.sos.state.co.us/pubs/elections/Results/Abstract/{year}/general/turnout.html',f'shared sos-{year}-abstract-index observed link')
  get(f'format-{year}',f'https://www.sos.state.co.us/pubs/elections/Results/Abstract/{year}/format.html',f'shared sos-{year}-abstract-index observed link')
 get('rules-resource','https://www.sos.state.co.us/pubs/elections/lawsRulesResources.html?menuheaders=5')
 get('calendar-2026','https://www.sos.state.co.us/pubs/elections/calendars/2026ElectionCalendar.pdf','current clerks page link')
 c=get('clerks-2026','https://www.clerkandrecorder.org/2026-general-election').decode()
 get('boulder-2026','https://bouldercounty.gov/elections/information/')
 get('cure-current','https://countmyballot.coloradosos.gov/form/cure','clerks-2026')
 u='https://coag.gov/press-releases/weiser-secures-court-order-temporarily-blocking-postal-services-unlawful-mail-voting-rule/'
 c=get('ag-usps-order',u).decode()
 for href,label in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',c,re.S):
  if 'restraining order' in re.sub('<[^>]*>','',label).lower():get('usps-tro',urljoin(u,href),'ag-usps-order literal TRO link')
 for href,label in re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',bodies['rules-resource'].decode(),re.S):
  if 'current' in label.lower() and 'rule' in label.lower():get('rules-current',urljoin('https://www.sos.state.co.us/pubs/elections/lawsRulesResources.html',href),'rules-resource observed current rules link');break
if __name__=='__main__':main()
