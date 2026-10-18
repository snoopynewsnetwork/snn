#!/usr/bin/env python3
"""Coordinator primary-text/hash and narrow operative-scope checks."""
from pathlib import Path
from html.parser import HTMLParser
import datetime,gzip,hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[1];D=R/'data';S=D/'results-sources/raw';sha=lambda b:hashlib.sha256(b).hexdigest()
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,s):self.parts.append(s)
def raw(id):
 m=json.loads((S/(id+'.meta.json')).read_text());b=gzip.decompress((S/(id+'.body.gz')).read_bytes());assert sha(b)==m['raw_sha256']and len(b)==m['raw_bytes'];return m,b
def html(id):
 m,b=raw(id);p=Text();p.feed(b.decode());return m,re.sub(r'\s+',' ',' '.join(p.parts))
def main():
 refs=[];findings=[]
 for id in ['law-203B.08','law-204C.33','law-204B.09','law-203B.24','scotus-docket']:
  m,t=html(id);refs.append({'id':id,'url':m['requested_url'],'raw_sha256':m['raw_sha256'],'raw_bytes':m['raw_bytes']})
  if id=='law-203B.08':assert 'by 5:00 p.m. on election day'in t and 'after 8:00 p.m.'in t;findings.append('Current retained203B.08 distinguishes5pm in-person return and envelopes receivedafter8pm electionday markedlate; no state deadline extended by federalUSPSdesigncase.')
  elif id=='law-204C.33':assert 'between the third and eighth days'in t and 'on the 16th day following'in t and 'highest number of votes for each federal office'in t;findings.append('County canvass days3–8, state16thday→November19,2026; timelyfiled namedwritein request and separate compilation. Prior thirdTuesday/Nov24 carryover corrected, not an operative-source conflict.')
  elif id=='law-204B.09':assert '19th day'in t and '5:00 p.m.'in t;findings.append('General writein request deadline19thdaybefore election5pm; eligibility and actual complete roster still separate from printed blankslot.')
  elif id=='scotus-docket':assert 'Sep 14 2026'in t and 'is denied'in t;findings.append('Captured SupremeCourt26A305 docket includesSeptember14staydenial; later unseen dispositions are not ruled out.')
 for id,pages in [('ag-usps-original-95',9),('scotus-primary-orders-appendix',50),('scotus-linked-50',11),('witness-mirror-original',28)]:
  m,b=raw(id);assert b.startswith(b'%PDF-');info=subprocess.run(['pdfinfo','-'],input=b,capture_output=True,check=True).stdout.decode();assert int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))==pages
  t=subprocess.run(['pdftotext','-layout','-','-'],input=b,capture_output=True,check=True).stdout.decode();tt=re.sub(r'\s+',' ',t)
  if id=='ag-usps-original-95':assert 'September 14, 2026'in tt and 'The application for stay'in tt and 'is denied.'in tt
  elif id=='scotus-primary-orders-appendix':assert 'Document 285'in tt and 'Filed 09/04/26'in tt and '/s/ Indira Talwani'in tt and 'Federal Ballot Mail Portal'in tt;findings.append('Full primary-hosted districtSeptember4Document285 in SCOTUSappendix enjoins specified USPSenvelope/portal-rule enforcement; separate COASeptember10 and SupremeCourtSeptember14 stay denials preserve preliminaryscope. No meritsfinal/stateballotreceiptextension inferred.')
  elif id=='scotus-linked-50':assert '09/10/2026'in tt and 'denied'in tt.lower()
  elif id=='witness-mirror-original':assert 'A24-1134'in tt and 'August 12, 2026'in tt and 'Affirmed.'in tt;findings.append('Court-authored MinnesotaA24-1134August12opinion affirmsdismissal of witness VRA/materiality claims; actualPDF is disclosedJustiamirror, originalhostaccess remainsgap. Exact amendedstatute/currentballotboardinstructions must be kept separate from holding.')
  refs.append({'id':id,'url':m['requested_url'],'raw_sha256':m['raw_sha256'],'raw_bytes':m['raw_bytes'],'fresh_PDF_pages':pages,'host_scope':'Court-authored opinion via disclosedJustiamirror'if id=='witness-mirror-original'else'Primaryofficialhost'})
 out={'status':'pass_narrow_primary_scope_checks_pending_final_source_package','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Fresh original-gzip SHA/bytes, independent standard-libraryHTMLtext and PopplerPDFtext/pagecounts; not worker legal parser. Findings bounded to captured source/date/operative language.','references':refs,'findings':findings,'scope':'Not exhaustive future docket, complete legal advice, valid ballot inventory or current production approval.'}
 p=D/'coordinator-legal-review.json'
 if p.exists():
  old=json.loads(p.read_text())
  if {k:v for k,v in old.items()if k!='checked_utc'}=={k:v for k,v in out.items()if k!='checked_utc'}:out['checked_utc']=old['checked_utc']
 p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'references':len(refs),'findings':len(findings)},indent=2))
if __name__=='__main__':main()
