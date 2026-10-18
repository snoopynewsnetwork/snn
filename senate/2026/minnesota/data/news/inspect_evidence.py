#!/usr/bin/env python3
"""Verify retained public captures; summarize bounded product inspections."""
from pathlib import Path
from html.parser import HTMLParser
import gzip,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'manifest.json').read_text())
for r in rows:
 if 'asset' not in r:continue
 b=(ROOT/r['asset']).read_bytes();assert hashlib.sha256(b).hexdigest()==r['stored_sha256'],r['id']
 raw=gzip.decompress(b);assert hashlib.sha256(raw).hexdigest()==r['raw_sha256'],r['id']
def raw(name):
 r=next(r for r in rows if r['id']==name);return gzip.decompress((ROOT/r['asset']).read_bytes()).decode(errors='replace')
obs={'captures':len(rows),'verified_assets':sum('asset' in r for r in rows)}
x=json.loads(raw('mpr-primary-senate-data'))
assert len(x['usSenate'])==2 and all(r['source']=='ap' for r in x['usSenate'])
assert all(r['precinctsTotal']==4105 for r in x['usSenate'])
assert '2026-08-11' in raw('mpr-app-js') and 'electionsapi.publicradio.org' in raw('mpr-app-js')
assert 'your activity and behavior' in raw('sos-media-current')
assert '"displayTestData":true' in raw('keyc-results') and '"selectedElection":{"id":null}' in raw('keyc-results')
obs.update(mpr_primary_races=2,mpr_supplier='ap',mpr_precincts_total=4105,state_media_http200_is_bot_challenge=True,keyc_empty_test_display=True)
canonical=[]
for id in ['bemidji-senate-debate','fergus-senate-debate']:
 s=raw(id);assert 'Forum News Service' in s and 'Mary Murphy' in s
 blocks=re.findall(r'<script[^>]*type=[\"\x27]application/ld\+json[\"\x27][^>]*>(.*?)</script>',s,re.S)
 articles=[json.loads(b) for b in blocks if 'NewsArticle' in b]
 assert articles and articles[0]['datePublished']=='October 16, 2026 04:07 PM'
 canonical.append(articles[0]['url'])
assert len(set(canonical))==1
obs['northwest_regional_reporting']={'bemidji_home':200,'bemidji_election_parent':200,'fergus_home':200,'shared_article_canonical':canonical[0],'shared_article_attribution':'Mary Murphy / Forum News Service','scope':'One syndicated October16 debate report in two regional publications, not independent count confirmation or a verified November scoreboard.'}
obs['st_cloud_times_direct_status']=next(r['status']for r in rows if r['id']=='stcloud-times-home')
report=next(r for r in rows if r['id']=='lrl-2024-election-report')
b=gzip.decompress((ROOT/report['asset']).read_bytes());assert b.startswith(b'%PDF-')
t=subprocess.run(['pdftotext','-f','1','-l','2','-layout','-','-'],input=b,capture_output=True,check=True).stdout.decode()
assert 'Postal Verification Card Report' in t
obs['rejected_result_candidate']={'id':report['id'],'actual_identity':'Postal Verification Card Report for2024 elections','scope':'Administrative registration-mail report, not candidate returns/write-in allocation or outstanding Senate votes; no additional extraction or use as count control.'}
class PageText(HTMLParser):
 def __init__(self):super().__init__();self.ignore=0;self.parts=[]
 def handle_starttag(self,tag,attrs):
  if tag in ['script','style']:self.ignore+=1
 def handle_endtag(self,tag):
  if tag in ['script','style']:self.ignore=max(0,self.ignore-1)
 def handle_data(self,data):
  if not self.ignore:self.parts.append(data)
def visible(id):
 p=PageText();p.feed(raw(id));return re.sub(r'\s+',' ',' '.join(p.parts))
s=visible('sos-november-observed201')
assert 'State General Election' in s and 'November 3, 2026' in s and 'TEST RESULTS' in s
obs['official_november201']={'actual_election_label':'State General Election Tuesday November3,2026','literal_status':'TEST RESULTS','body_is_full_result_index':True,'admitted_counts':False,'scope':'Actual discovered201 route, independent full HTTP200 HTML; explicit test setup excluded despite correct election label. November19 footer agrees with retained204C.33 sixteen-day statutory rule, not evidence of valid counts.'}
s=visible('townsquare-november-results');assert 'Last updated: 10-15-26 02:08pm' in s
assert '202,333 precincts of 4,105 precincts reporting' in s
for label,value in [('WRITE-IN','555,555'),('Peggy Flanagan (D)','111,111'),('Marisa Simonetti (I)','222,222'),('Michele Tafoya (R)','333,333'),('Rebecca Whiting (L)','444,444')]:assert label+' '+value in s
obs['townsquare_pre_election_invalid_results']={'source_clock_literal':'10-15-26 02:08pm','source_clock_timezone':'unspecified','reported_precincts':202333,'total_precincts':4105,'senate_display_total':1666665,'candidate_display_values':{'WRITE-IN':555555,'Peggy Flanagan (D)':111111,'Marisa Simonetti (I)':222222,'Michele Tafoya (R)':333333,'Rebecca Whiting (L)':444444},'literal_unofficial_label':True,'literal_test_label_observed':False,'admitted_counts':False,'scope':'Pre-election nonphysical reported>total units and repeated-pattern positive values; invalid setup-like display excluded. No claim that publisher explicitly labels these as test.'}
(ROOT/'inspection.json').write_text(json.dumps(obs,indent=2)+'\n');print(json.dumps(obs,indent=2))
