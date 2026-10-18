from common import *
import collections,csv,re
controls=[json.loads(x) for x in gzip.decompress((ROOT/'extracts/county-controls.jsonl.gz').read_bytes()).decode().splitlines()];pos=[json.loads(x) for x in gzip.decompress((ROOT/'extracts/source-positions.jsonl.gz').read_bytes()).decode().splitlines()]
gaps=[]
for c in controls:
 f=c['county_fips'];e=c['election_key'];fields=[]
 if e!='2024NovGen':fields=['precincts','ballotItemWithBreakdown.breakdownResults(native precincts)','voterTurnout.native rows','usable ballotsCast','usable registration']
 else:
  if any(r['level']=='precinct' and r['county_fips']==f and r['kind']=='TOTAL' and r['votes'] is None for r in pos):fields.append('native candidate voteCount null (FultonJSON40; separately documented XLSX alternative retained)')
  if any(r['level']=='precinct' and r['county_fips']==f and r['kind']=='METHOD' and r['votes'] is None for r in pos):fields.append('native candidate/groupResults voteCount null')
  fields+=['complete county/native/method allocation of858 qualified presidential write-ins','registration active/inactive/date scope','approved current physical/reporting crosswalk']
 if fields:gaps.append({'county_fips':f,'county_name':c['county_name'],'election_key':e,'source_path':c['source_path'],'unavailable_source_fields':fields,'alternative_scope':'Historical state XLSX county totals recovered; no older native/usable ballot or registration recovery' if e!='2024NovGen' else '2024 XLSX contains only four named options; county canvasses may contain void choices/generic unresolved marks; do not substitute'})
for c in [c for c in controls if c['election_key']=='2024NovGen']:gaps.append({'county_fips':c['county_fips'],'county_name':c['county_name'],'election_key':'2026-11-03','unavailable_source_fields':['genuine general-election result payload','approved Senate contest/candidate IDs','November native/method reporting crosswalk','genuine release/correction series','compatible uncounted valid Senate vote count'],'current_root_receipt':'raw/current-tenant-'+c['county_fips']+'.http.json','negative_control':'200 redirectToShortName:Georgia,id:null,elections:[]'})
receipts=[js(p) for p in sorted((ROOT/'raw').glob('*.http.json'))]
failures=[{'id':r['id'],'url':r['url'],'status':r.get('status'),'county_fips':r.get('county_fips'),'error':r.get('error'),'receipt':'raw/'+r['id']+'.http.json'} for r in receipts if r.get('status')!=200]
save(ROOT/'gaps.json',{'status':'precise source/vintage gaps; no inferred zero or geographic approval','county_vintage_records':gaps,'all_failed_original_requests':failures,'general_scope_gaps':['Complete current statewide withdrawal/change register inaccessible; latest examined final sample/certified-list context is stated','November local poll extension orders cannot be preapproved before election; observe actual orders','Native PDF/XLSX label matches do not authorize current physical joins','No collector or calibrated probability produced']})
# Preserve observed application snippets at byte/character positions; no undocumented endpoint probing.
items=[]
for r in receipts:
 if r.get('role')=='published_bundle':
  s=entity(r).decode('utf-8','replace')
  for term in ['blobName','baseImageCdn','/data','isProduction','nextUpdateAt']:
   for m in list(re.finditer(re.escape(term),s))[:3]:items.append({'source_id':r['id'],'literal':term,'character_offset':m.start(),'excerpt':s[max(0,m.start()-140):m.start()+260]})
for file in ['sos-results-main-js.html.gz','sos-results-service-chunk-js.html.gz']:
 b=gzip.decompress((GA/'data/news'/file).read_bytes());s=b.decode()
 for term in ['imageCdn:','getData(t,r,o)','getJurisdiction(t,r)','reportingStatusFullyReported','electionNightComplete','/results/public/api']:
  for m in list(re.finditer(re.escape(term),s))[:2]:items.append({'source_path':'data/news/'+file,'literal':term,'character_offset':m.start(),'excerpt':s[max(0,m.start()-100):m.start()+500]})
save(ROOT/'extracts/application-evidence.json',items)
# Exact independent Chatham partial evidence; no assertion this fully allocates state858.
save(ROOT/'extracts/county-writein-observations.json',{'election':'2024-11-05 president','scope':'separate primary county canvas vintages, never substituted into frozen named-four contract','Chatham':{'source_id':'local-13051-2-sample-29','page':1,'printed_clock':'11/12/2024 10:48:06 AM','printed_clock_timezone':None,'status':'Official and Complete','named_four':141109,'void_DeLaCruz':207,'void_West':296,'shown_qualified_rows':{'Brian Kienitz':0,'Nomusa Venita Smith':0,'Peter Sonski':3,'Jay J Bowman':0,'President R Boddie':1,'Shiva Ayyadurai':0,'Susan Maude Buscher':0,'Emily Mathews':0},'absent_qualified_name_Andre_Ramon_McNeil_Sr':None,'unresolved_generic_marks':427,'total_votes_printed':141616,'ballots_cast':142417,'unclassified_ballots_minus_printed_votes':801,'Sonski_method':'Absentee by Mail3','Boddie_method':'Advance Voting1','compatible_full858_county_allocation':False},'Liberty':{'source':'data/turnout/source/liberty-bound-observation.json','scope':'coordinator-reviewed actual complete canvass/ballot ceiling; Sonski1 and7shownzeros; absentAndre unknown; do not treat generic/disqualified as qualified'},'Habersham':{'source':'data/turnout/source/habersham-2024-summary.body.gz and .http.json, pinned in shared-inputs','scope':'previously retained complete canvass has64 unresolved generic marks and26 void choices; not64 certified qualified write-ins'},'state_export2024':{'source_id':'observed-export-2024NovGen-0-0','named_four':5250047,'qualified_or_unresolved_rows':0,'all159_county_named_rows':636,'admin_ballot_and_total_rows':318,'additional858_allocation':None},'Fulton_export2024':{'source_id':'observed-export-fulton2024-0-0','native_labels':466,'qualified_or_unresolved_rows':0,'additional858_allocation':None}})
print('Gap matrix county/vintage entries',len(gaps),'failed requests',len(failures))
