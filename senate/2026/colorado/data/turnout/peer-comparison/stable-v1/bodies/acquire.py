#!/usr/bin/env python3
"""Preserve complete public response entities; no guessed election-feed routes."""
from pathlib import Path
import requests,gzip,hashlib,json,datetime,argparse
from html.parser import HTMLParser
from urllib.parse import urljoin
D=Path(__file__).resolve().parent
URLS={
'court-sept14':'https://www.supremecourt.gov/opinions/25pdf/26a305_4g15.pdf',
'law11':'https://www.sos.state.co.us/pubs/info_center/laws/Title1/Title1Article11.html',
'current-candidates-xlsx':'https://www.sos.state.co.us/pubs/elections/vote/files/2026/2026GeneralCandidateListOfficial.xlsx',
'current-candidates':'https://www.sos.state.co.us/pubs/elections/vote/generalCandidates.html',
'mail-faq':'https://www.sos.state.co.us/pubs/elections/FAQs/mailBallotsFAQ.html',
'uocava-faq':'https://www.sos.state.co.us/pubs/elections/FAQs/UOCAVA.html',
'cure':'https://countmyballot.coloradosos.gov/form/cure',
'calendar':'https://www.sos.state.co.us/pubs/elections/calendars/2026ElectionCalendar.pdf',
'rules':'https://www.sos.state.co.us/pubs/rule_making/CurrentRules/8CCR1505-1/ElectionRules.pdf',
'clerks-current':'https://www.clerkandrecorder.org/2026-general-election',
'ag-court':'https://coag.gov/press-releases/weiser-secures-court-order-temporarily-blocking-postal-services-unlawful-mail-voting-rule/',
'sos-court':'https://content.govdelivery.com/accounts/COSOS/bulletins/4272f35',
'senate-II':'https://www.senate.gov/senators/Class_II.htm',
'senate-III':'https://www.senate.gov/senators/Class_III.htm',
'election-law':'https://www.sos.state.co.us/pubs/info_center/laws/Title1/Title1Article4.html',
'canvass-law':'https://www.sos.state.co.us/pubs/info_center/laws/Title1/Title1Article10.html',
}
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--only',nargs='*');a=p.parse_args();out=[];session=requests.Session()
 for sid,u in URLS.items():
  if a.only and sid not in a.only:continue
  at=datetime.datetime.now(datetime.timezone.utc).isoformat()
  try:
   r=session.get(u,timeout=60);b=r.content;z=gzip.compress(b,mtime=0);target=D/'source'/(sid+'.gz');target.write_bytes(z)
   out.append(dict(id=sid,requested_url=u,final_url=r.url,retrieved_utc=at,status=r.status_code,headers=dict(r.headers),redirects=[dict(url=h.url,status=h.status_code,headers=dict(h.headers))for h in r.history],path=str(target.relative_to(D)),bytes=len(b),sha256=sha(b),stored_bytes=len(z),stored_sha256=sha(z),entity_definition='requests decoded content; full untruncated response entity; gzip decompression exactly restores this entity'))
  except Exception as e:out.append(dict(id=sid,requested_url=u,retrieved_utc=at,error=str(e)))
  print(sid,out[-1].get('status',out[-1].get('error')),flush=True)
 old=D/'source/acquisition.json';previous=json.loads(old.read_text())if old.exists()else[];old.write_text(json.dumps([x for x in previous if x['id']not in {r['id']for r in out}]+out,indent=2)+'\n')
if __name__=='__main__':main()
