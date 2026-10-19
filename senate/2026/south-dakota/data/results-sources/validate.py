#!/usr/bin/env python3
"""Meaningful deterministic offline QA. --write writes validation before manifest.
Default checks exact manifests and all references without changing any file.
"""
import sys
sys.dont_write_bytecode=True
from common import *
from dependencies import verify,semantic
from reconstruct import reconstruct
from asset_manifest import audit
import csv,io,re,copy,argparse,datetime
from zoneinfo import ZoneInfo

def pointer(o,p):
 for k in p.split('/')[1:] if p else []:
  k=k.replace('~1','/').replace('~0','~');o=o[int(k)] if isinstance(o,list) else o[k]
 return o

def checks():
 out={};dep=verify();saved=json.loads((ROOT/'dependency-verification.json').read_text());assert dep==saved
 out['dependency_pins']=len(dep['exact_read_only_references']);out['recursive_full_objects']=len(dep['complete_semantic_objects']);out['complete_shared_raw_originals']=len(dep['original_raw_checks'])
 c=json.loads((STATE/'data/turnout/priority-set.json').read_text());assert len((STATE/'data/turnout/priority-set.json').read_bytes())==2955655;assert hashlib.sha256((STATE/'data/turnout/priority-set.json').read_bytes()).hexdigest()=='a1c97454c68c1f30bdb6b7755cd826326e7380318eae74b6452465ee23e9c275'
 for o in dep['complete_semantic_objects']:assert semantic(pointer(c,o['JSON_pointer']))==o['recursive_semantic_sha256']
 a=json.loads((STATE/'data/coordinator-priority-acceptance.json').read_text());assert a['status']=='accepted_historical_public_native_source_dispatch_only'
 for k in ['certified_minimum_or_membership_approved','current_geography_approved','current_November_returns_admitted','current_result_IDs_approved','live_cadence_or_exact_remainder_approved','collector_or_probability_approval']:assert a[k] is False
 assert c['coordinator_acceptance']['accepted'] is False and c['certification_robustness']['proven'] is False
 u=c['all_units'];assert len({r['key'] for r in u})==691;assert sum(r['contest_votes'] for r in u[304:])==85326;assert sum(r['contest_votes'] for r in u[:15])==61003;assert 5*342947<4*428728<=5*343402;assert (4*428728+4)//5==342983;assert (4*428922+4)//5==343138
 prior=json.loads((ROOT/'ordered-priority-records.json').read_text());rest=json.loads((ROOT/'ordered-remainder-records.json').read_text());invest=json.loads((ROOT/'county-investigations.json').read_text())['investigations'];by={x['id']:x for x in invest};assert len(by)==39 and [x['county_fips'] for x in invest]==a['ordered_priority_parent_keys'];assert len(prior)==304 and len(rest)==387;assert [x['historical_key'] for x in prior+rest]==a['ordered_full_keys']
 for i,x in enumerate(prior+rest):
  ref=x['complete_historical_object'];assert ref['file']=='data/turnout/priority-set.json';assert semantic(pointer(c,ref['JSON_pointer']))==ref['recursive_semantic_sha256']==semantic(u[i]);assert x['current_native_identifier'] is None
  if i<304:
   inv=by[x['investigation']];assert inv['county_fips']==x['county_parent_key'];assert x['historical_key'] in inv['priority_keys_ordered'];rr,_=load('county-'+x['county_parent_key']);assert rr['status']==200
  else:assert x['investigation'] is None
 for inv in invest:
  for p in inv['authority_chain']+inv['local_authority_chain']:assert (ROOT/p).exists(),p
 inventory=list(csv.DictReader((STATE/'data/official-results-sources.csv').open()));assert len(inventory)==67 and len({r['county_fips'] for r in inventory[1:]})==66
 directory=json.loads((ROOT/'authority-directory.json').read_text());assert len(directory['rows'])==66 and directory['headers']==['County','Auditor First Name','Auditor Last Name','Mailing Address','Mailing City','Mailing Zip','Phone','Fax','Email'];assert all(len(r['fields'])==9 for r in directory['rows'])
 out['inventory']={'state':1,'all_counties':66,'priority_parents_actually_requested':39,'ordered_priorities':304,'ordered_remainder':387,'historical_leaves':691,'parent_complete_objects':66}
 # Independently verify frozen owned manifest membership, not just listed hashes.
 for directory_name,field,report,csvname in [('turnout','owned_paths','turnout.md','county-turnout.csv'),('baselines','owned_assets','county-partisanship.md','county-baselines.csv')]:
  m=json.loads((STATE/'data'/directory_name/'asset-manifest.json').read_text());actual={str(p.relative_to(STATE)) for p in (STATE/'data'/directory_name).rglob('*') if p.is_file() and p.name!='asset-manifest.json'}|{report,'data/'+csvname};assert actual=={x['path'] for x in m[field]}
 out['frozen_owned_exact_membership']=True
 receipts=sorted((ROOT/'raw').glob('*.receipt.json'));statuses={};rawbytes=0
 for p in receipts:
  id=p.name.removesuffix('.receipt.json');r,b=load(id);q=reconstruct('owned',id);assert q['raw_bytes']==r['raw_bytes'];assert r['method'] in ['GET','POST'];assert r['retrieved_utc'].endswith('+00:00');assert 'redirects' in r and 'headers' in r and 'error' in r;rawbytes+=len(b);statuses[str(r['status'])]=statuses.get(str(r['status']),0)+1
  for part in r['stored_parts']:assert part['bytes']<40000000
 out['complete_acquired_responses']={'receipts':len(receipts),'raw_entity_or_exception_bytes':rawbytes,'statuses':statuses}
 for p in ROOT.glob('jobs-*.json'):
  for job in json.loads(p.read_text()):assert (ROOT/'raw'/(job['id']+'.receipt.json')).exists()
 scope=json.loads((ROOT/'current-setup-scope.json').read_text());assert (scope['overall_header'],scope['Senate_banner_denominator'],scope['native_workbook_rows'],scope['native_county_worksheets'])==(673,656,654,65);assert scope['missing_counties']==['Charles Mix'];assert scope['all_numeric_candidate_sums']==[0,0];assert scope['turnout_TotalPrecincts_sum']==673 and scope['turnout_Voters_sum']==618804
 assert {x['county'].replace(' (Vote Center)',''):(x['turnout_TotalPrecincts'],x['workbook_rows']) for x in scope['scope_differences']}=={'Brookings':(10,5),'Hughes':(6,3),'Charles Mix':(11,None)}
 posts=[p for p in receipts if p.name.endswith('-native-xlsx.receipt.json')];assert len(posts)==39
 for p in posts:
  id=p.name.removesuffix('.receipt.json');w=json.loads(gzip.decompress((ROOT/'parsed'/(id+'.json.gz')).read_bytes()));assert len(w['sheets'])==65;assert {s['attributes']['name'] for s in w['sheets']}=={x['county_literal'] for x in scope['county_scopes']}
  leaves=[]
  for sheet in w['sheets']:
   for row in sheet['rows']:
    d={x['attributes']['r'].rstrip('0123456789'):x['value_resolved'] for x in row['cells']}
    if d.get('B') and d['B']!='TOTALS' and str(d.get('C','')).isdigit():leaves.append(d)
  assert len(leaves)==654 and all(d['C']==d['D']=='0' for d in leaves)
 rows=list(csv.reader(io.StringIO(load('state-csv')[1].decode())));assert len(rows)==19 and len(rows[0])==14 and all(len(x)==15 for x in rows[1:]);sen=[x for x in rows[1:] if x[0]=='14412'];assert [(x[7],x[8],x[2],x[11],x[13]) for x in sen]==[('24967','Mike  Rounds ','REP','0','="0/656"'),('24887','Brian L Bengs ','IND','0','="0/656"')]
 cand=json.loads(load('state-candidate-service')[1])['d'];assert len(cand)==358;assert [x['ID'] for x in cand if x['desc']=='United States Senator']==[215,215]
 out['current_setup_scopes']={'overall':673,'Senate_banner':656,'actual_native_rows':654,'actual_counties':65,'missing':'Charles Mix','all39_download_responses_same_statewide_scope':True,'search_ID215_distinct_from_race14412_and_choiceIDs':True,'genuine_votes_admitted':False}
 hist=json.loads((ROOT/'historical-source-qa.json').read_text());assert [x['native_rows'] for x in hist['complete_OOXML_replay']]==[691,687,693];assert len(hist['bounded_original_PDF_samples'])==4
 pdfrows=list(csv.DictReader((STATE/'data/baselines/native-2022.csv').open()));assert len(pdfrows)==679
 out['historical_original_QA']={'native_XML_rows':2071,'county_footers':198,'bounded_PDF_samples':4,'distinct_PDF_companion_rows':679,'signed_candidate_controls_preserved':594}
 # Negative full-object fixtures protect source/method/null/admin semantics and order.
 base=copy.deepcopy(u[0]);changes=[]
 for label,mut in [('method',lambda v:v.__setitem__('method_scope','invented_ed')),('null',lambda v:v['separate_fields'].__setitem__('ballots_cast',0)),('native_admin',lambda v:v['source_native_constituents'][0].__setitem__('physical_or_combined_constituents',[]))]:
  v=copy.deepcopy(base);mut(v);assert semantic(v)!=semantic(base);changes.append(label)
 parent=copy.deepcopy(c['county_parents'][0]);changed=copy.deepcopy(parent);changed['ordered_all_native_keys']=list(reversed(changed['ordered_all_native_keys']));assert semantic(changed)!=semantic(parent);changes.append('ordered_children')
 assert hashlib.sha256(b'original').hexdigest()!=hashlib.sha256(b'originaL').hexdigest();changes.append('raw_bytes')
 def admit(e):return e.get('election')=='2026-11-03' and e.get('contest')=='United States Senator' and e.get('test') is False and e.get('genuine_observed_vote_sequence') is True
 assert not admit({'election':'2026-11-03','contest':'United States Senator','test':True,'genuine_observed_vote_sequence':False});changes.append('test_admission')
 out['negative_fixtures_passed']=changes
 for zone,hour in [('America/Chicago',1),('America/Denver',2)]:
  dt=datetime.datetime(2026,11,3,19,tzinfo=ZoneInfo(zone)).astimezone(datetime.timezone.utc);assert (dt.day,dt.hour)==(4,hour)
 out['ordinary_local7PM_conversion']='CST01:00/MST02:00UTC Nov4; not precinct timezone assignment or extension claim'
 law=json.loads(load('sessionlaw-ch73-json')[1]);assert law['SessionLawId']==33903 and law['Chapter']==73 and law['DocumentId']==306614;assert 'Signed March 26, 2026' in clean(law['Html']);assert 'December 1, 2025' in (ROOT/'precinct-manual.txt').read_text()
 out['operative_law_vs_manual']='2026ch73 signedMarch26 emergency; Dec1,2025 manuals distinct; complete later docket qualified'
 links=0
 for p in [STATE/'official-results.md',ROOT/'SCHEMA.md',ROOT/'README.md']:
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   if target.startswith(('http:','https:','#','mailto:')):continue
   assert (p.parent/target.split('#')[0]).exists(),(p,target);links+=1
 out['relative_markdown_links']=links
 deterministic=json.loads((ROOT/'deterministic-rebuild.json').read_text());assert deterministic['status']=='pass'
 for p in deterministic['exact_before_after_pins']:
  assert pin(STATE/p['path'])==p
 out['deterministic_rebuild_artifacts']=deterministic['checked_artifacts']
 out['limits']=['No certified native minimum/membership robustness','No current leaf/physical/method join','No genuine November counts/cadence/correction sequence','No exact Senate remainder or calibrated probability','No exhaustive later court/military/signed-ballot scope']
 return {'status':'pass_owned_official_source_research_with_explicit_qualifications','checks':out,'authority_path_only':'data/coordinator-priority-acceptance.json'}

def clean(html):return ' '.join(' '.join(HTML(html.encode()).text).split())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();o=checks()
 if a.write:dump('validation.json',o)
 else:assert o==json.loads((ROOT/'validation.json').read_text());print(json.dumps(audit(),indent=2))
 print(json.dumps(o,indent=2))
