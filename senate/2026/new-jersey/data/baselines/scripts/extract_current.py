#!/usr/bin/env python3
"""Current official general publication evidence; no historical/live ID reuse."""
import json,gzip,re,subprocess,tempfile
from html.parser import HTMLParser
from extract_originals import D,S,E,save,sha,COUNTIES

def textof(sid):
 r=json.loads((S/(sid+'.receipt.json')).read_text());assert r['status']==200;b=gzip.decompress((S/r['asset']).read_bytes());assert sha(b)==r['raw_sha256']
 with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
  f.write(b);f.flush();t=subprocess.run(['pdftotext','-layout',f.name,'-'],capture_output=True,check=True).stdout
 (E/(sid+'.layout.txt.gz')).write_bytes(gzip.compress(t,mtime=0));return t.decode(),r

def main():
 sid='public-network-current-senate-roster';t,r=textof(sid);cert,cr=textof('public-network-current-general-certification');calendar,calr=textof('public-network-current-general-calendar');rows=[]
 expected=[('CORY BOOKER *','Democratic'),('JUSTIN MURPHY','Republican'),('VERONICA FERNANDEZ','END THE CORRUPTION!'),('JOANNE KUNIANSKY','SOCIALIST WORKERS PARTY')]
 for pn,(name,party) in enumerate(expected,1):
  page=t.split('\f')[pn-1];lines=page.splitlines();header=next((i,l) for i,l in enumerate(lines,1) if name in l);assert party in header[1];parents=[]
  for ln,l in enumerate(lines,1):
   for c in COUNTIES:
    if re.match(r'^\s*'+c.upper()+r'\s',l):parents.append({'county':c,'line':ln,'raw':l})
  assert len(parents)==21 and len({a['county'] for a in parents})==21
  assert page in cert,'general official list matches certification attachment literal page'
  rows.append({'literal_candidate_name':name,'party_ballot_label':party,'source_id':sid,'source_page':pn,'source_line':header[0],'literal_header':header[1],'county_rows':parents,'live_candidate_id':None})
 assert 'Total Candidates' in t and re.search(r'Total Candidates\s+4',t)
 save(D/'current-general-publication.json',{'status':'current linked official general list and certification attachment, as retrieved; later amendments remain external','publication_date':'07/27/2026','election_date':'2026-11-03','source_url':r['final_url'],'retrieved_at_utc':r['retrieved_at_utc'],'raw_sha256':r['raw_sha256'],'certification_url':cr['final_url'],'certification_raw_sha256':cr['raw_sha256'],'candidates':rows,'no_primary_nominee_substitution':True,'no_old_feed_ID_mapping':True,'ballot_order_or_current_reporting_ids_verified':False,'calculator_2026_candidate_effects_inferred':False,'general_calendar_url':calr['final_url'],'calendar_update_date':'January 9, 2026','calendar_election_page':7})
 # Retain literal law/result authority snippets with body hashes and source positions as bytes.
 evidence=[]
 for sid,patterns in [('public-network-current-election-rule',['19:3-4','greatest number of votes']),('public-network-current-results-authority',['does not post running results','periodic reporting','county clerk'])]:
  r=json.loads((S/(sid+'.receipt.json')).read_text());text=gzip.decompress((S/r['asset']).read_bytes()).decode();hits=[]
  for pattern in patterns:
   for m in re.finditer(re.escape(pattern),text,re.I):hits.append({'pattern':pattern,'character_start':m.start(),'literal_context':text[max(0,m.start()-200):m.end()+700]})
  assert hits,sid;evidence.append({'source_id':sid,'url':r['final_url'],'raw_sha256':r['raw_sha256'],'hits':hits})
 save(D/'current-authority-evidence.json',evidence);print('current official general four candidates/all21; statutory plurality evidence retained')
if __name__=='__main__':main()
