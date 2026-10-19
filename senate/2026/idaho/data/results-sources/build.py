#!/usr/bin/env python3
"""Deterministic offline research products from retained complete evidence."""
from pathlib import Path
import argparse,csv,gzip,hashlib,io,json,sys
D=Path(__file__).resolve().parent;S=D.parent.parent

def sha(b):return hashlib.sha256(b).hexdigest()
def dig(x):return sha(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def products():
 c=load(S/'data/turnout/priority-set.json');graph=load(D/'historical-source-graph.json');receipts={p.stem:load(p) for p in sorted((D/'receipts').glob('*.json'))};notes=load(D/'county-findings.json');directory=load(D/'directory-native.json')['rows'];nav={n['receipt']:n for n in load(D/'navigation.json.gz')};extraction={x['receipt']:x for x in load(D/'extraction-index.json')};out={};sources=[];authorities=[];schema={}
 def body(id):return json.loads(gzip.decompress((D/receipts[id]['stored_path']).read_bytes()))
 def schemawalk(x,path=''):
  t=type(x).__name__;schema.setdefault(path,set()).add(t)
  if isinstance(x,dict):
   for k,v in x.items():schemawalk(v,path+'/'+k)
  elif isinstance(x,list):
   for v in x:schemawalk(v,path+'/*')
 def ref(id):
  r=receipts[id];return dict(receipt='receipts/'+id+'.json',requested_url=r['url'],http_status=r.get('http_status'),raw_sha256=r.get('raw_sha256'),stored_path=r.get('stored_path'),retrieved_utc=r['retrieved_utc'])
 def objects(p):
  i=c['all_county_constituents'].index(p);return dict(file='data/turnout/priority-set.json',pointer='/all_county_constituents/'+str(i),semantic_sha256=dig(p))
 for p in c['all_county_constituents']:
  name=p['county'].removesuffix(' County');slug=name.lower().replace(' ','-');appslug=slug+'-county-id';native=next(r for r in directory if r['County']==name);meta=body('api-'+appslug);data=body('data-'+appslug);schemawalk(data);priorities=c['ordered_priority_child_keys_by_parent'][p['key']];rid='county-'+slug
  county_receipts=[id for id in receipts if id==rid or id.startswith(rid+'-')];county_receipts.extend({'Kootenai':['kootenai-november'],'Bonneville':['bonneville-information'],'Canyon':['canyon-upcoming']}.get(name,[]));ids=['state-directory','directory-csv','state-results','sos-'+appslug,'api-'+appslug,'data-'+appslug]+county_receipts
  if priorities:ids+=['results-main-js','js-chunk-OJN5EB65','js-chunk-ZDE5TOJM','jurisdiction-'+appslug,'native-export-'+appslug]
  ids=list(dict.fromkeys(ids));candidate_records=[b for b in data['ballotItems'] if any('United States Senator' in n.get('text','') for n in b['name'])]
  src=dict(county=name,county_fips=p['county_fips'],historical_parent=objects(p),priority_child_count=len(priorities),historical_native_count=len(p['president_contexts']),acquired_shared_parent_sources=[ref(id) for id in ids],county_specific_finding=notes.get(name,'Monitoring county: actual directory home attempt, state-linked primary route, complete primary metadata and full native data retained. No historical/current leaf join or November return admitted.'),published_scope='2026-05-19 primary only for all app records',primary_election_metadata=meta,primary_jurisdiction_id=data['jurisdiction']['id'],primary_ballot_item_count=len(data['ballotItems']),primary_precinct_count=len(data['precincts']),primary_senate_contests=candidate_records,primary_precinct_sample=data['precincts'][:2],primary_count_group_keys=meta.get('countGroups'),primary_reporting_status=meta.get('precinctReportingStatus'),source_timezones='asOf and lastUpdated carry Z (UTC); client render uses browser-local Date formatting; no November publication timezone/cadence verified',current_leaf_id=None,current_contest_id=None,current_choice_ids=None,current_method_crosswalk=None,current_geography_crosswalk=None,current_November_returns_admitted=False,exact_outstanding_Senate_ballots=None,measured_cadence_seconds=None)
  if priorities:
   ex=extraction['native-export-'+appslug];wx=load(D/ex['derivative']);src['primary_export']=dict(receipt='native-export-'+appslug,complete_extraction=ex['derivative'],sheets=[dict(name=s['name'],native_rows=len(s['rows']),complete_header=s['rows'][0]) for s in wx['sheets']])
  sources.append(src)
  authorities.append(dict(authority='county',county=name,county_fips=p['county_fips'],priority_children=len(priorities),native_count=len(p['president_contexts']),directory_name=native['Full Name'],directory_phone=native['Phone'],directory_fax=native['Fax'],directory_email=native['Email'],directory_website=native['Website'],directory_mailing_address=native['Full Mailing Address'],directory_physical_address=native['Physical Address'],directory_native_json=json.dumps(native,ensure_ascii=False,sort_keys=True,separators=(',',':')),directory_source='https://archive.voteidaho.gov/data/county_clerk_contact_list.csv',directory_receipt='results-sources/receipts/directory-csv.json',authority_attempt_receipt='results-sources/receipts/'+rid+'.json',authority_http_status=receipts[rid].get('http_status') or '',authority_error=receipts[rid].get('error',''),published_primary_url=receipts['sos-'+appslug]['url'],primary_native_receipt='results-sources/receipts/data-'+appslug+'.json',primary_export_receipt='results-sources/receipts/native-export-'+appslug+'.json' if priorities else '',scope='May2026 primary; November results unverified',finding=src['county_specific_finding']))
 state=body('data-id');schemawalk(state);sources.insert(0,dict(authority='state',acquired_shared_parent_sources=[ref(id) for id in ['state-sos','state-results','api-id','data-id','jurisdiction-id','native-export-id']],complete_election_metadata=body('api-id'),complete_jurisdiction_configuration=body('jurisdiction-id'),scope='May2026 primary. No November election listed in acquired jurisdiction configuration.',current_November_returns_admitted=False))
 authorities.insert(0,dict(authority='state',county='Idaho',county_fips='',priority_children=528,native_count=985,directory_name='',directory_phone='',directory_fax='',directory_email='',directory_website='https://voteidaho.gov/election-results/',directory_mailing_address='',directory_physical_address='',directory_native_json='',directory_source='https://voteidaho.gov/election-results/',directory_receipt='results-sources/receipts/state-results.json',authority_attempt_receipt='results-sources/receipts/state-sos.json',authority_http_status=200,authority_error='',published_primary_url=receipts['sos-id']['url'],primary_native_receipt='results-sources/receipts/data-id.json',primary_export_receipt='results-sources/receipts/native-export-id.json',scope='May2026 primary; November results unverified',finding='State authority plus all44 county routes. State native data overlaps county observations; do not sum both.'))
 byparent={s['county_fips']:s for s in sources[1:]};nodes={u['key']:(i,j,p,u) for i,p in enumerate(c['all_county_constituents']) for j,u in enumerate(p['president_contexts'])};entries=[]
 for ordered in c['complete_order']:
  i,j,p,u=nodes[ordered['key']];src=byparent[p['county_fips']];selected=ordered['rank']<=528
  entry=dict(rank=ordered['rank'],historical_key=u['key'],historical_complete_object_reference=dict(file='data/turnout/priority-set.json',pointer=f'/all_county_constituents/{i}/president_contexts/{j}',semantic_sha256=dig(u)),historical_order_record=ordered,historical_parent_key=p['key'],historical_literal_label=u['literal_precinct'],historical_original_rows=[u['source_first_row'],u['source_last_row']],historical_method_flag=u['literal_method_flags'],primary_priority=selected,investigation_status='complete_bounded_shared_parent_research' if selected else 'retained_remainder_monitoring',shared_parent_analysis_pointer='/'+str(sources.index(src)),shared_parent_sources=src['acquired_shared_parent_sources'],actual_source_scope=src['published_scope'],source_specific_finding=src['county_specific_finding'],precise_current_leaf_gap=f"Historical {u['key']} is {p['county']}, literal {u['literal_precinct']!r}, original president rows{u['source_first_row']}-{u['source_last_row']}. Acquired May2026 parent has{src['primary_precinct_count']} native precinct records; none is approved as this historical observation or a November2026 leaf. No present result ID, method allocation, physical precinct or polygon match is established. Shared-parent research is substantive but cannot substitute a fabricated leaf source match.",current_leaf_id=None,current_contest_id=None,current_choice_ids=None,current_method=None,current_geometry=None,current_approved=False)
  entries.append(entry)
 hierarchy=dict(complete_contract_reference=graph['contract_path'],ordered_parent_keys=c['ordered_parent_keys'],ordered_child_keys_by_parent=c['ordered_child_keys_by_parent'],ordered_priority_child_keys_by_parent=c['ordered_priority_child_keys_by_parent'],ordered_remainder_child_keys_by_parent=c['ordered_remainder_child_keys_by_parent'],ordered_full_keys=[x['key'] for x in c['complete_order']],ordered_priority_keys=c['ordered_priority_keys'],ordered_remainder_keys=c['ordered_remainder_keys'],all_parent_complete_references=[objects(p) for p in c['all_county_constituents']],external_acceptance_path=graph['external_acceptance_path'])
 def emit(name,x):out[name]=(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
 index=[]
 for id,r in receipts.items():
  item={k:r.get(k) for k in ['id','url','parent_url','parent_receipt','discovery','scope','method','requested_url','final_url','retrieved_utc','finished_utc','http_status','error','raw_bytes','raw_sha256','stored_path','stored_bytes','stored_sha256']};item['receipt']='receipts/'+id+'.json';item['all_original_entities_retained']=r.get('stored_path') is not None;item['current_November_admitted']=False;item['actual_election_stage']='2026-05-19 primary' if id.startswith(('data-','api-')) else 'see complete source; no current November returns admission';index.append(item)
 emit('source-index.json',index)
 raw_directory=gzip.decompress((D/receipts['directory-csv']['stored_path']).read_bytes()).decode('cp1252')
 emit('directory-native.json',dict(encoding='cp1252',rows=list(csv.DictReader(io.StringIO(raw_directory)))))
 emit('parent-investigations.json',sources);emit('priority-investigations.json',entries[:528]);emit('remainder-monitoring.json',entries[528:]);emit('all985-hierarchy.json',hierarchy);emit('public-response-schema.json',[dict(path=p,types=sorted(t)) for p,t in sorted(schema.items())]);
 emit('coverage.json',dict(state_authorities=1,county_authorities=44,priority_parent_count=32,priority_entries=528,remainder_entries=457,native_observations=985,primary_named_candidate_votes=905057,top15_votes=65391,priority_votes=724515,preceding_votes=723753,crossing_key='ID:2024:pres:16079:11741',crossing_votes=762,remainder_votes=180542,county_sensitivities_only=c['county_sensitivity'],current_approved=False,external_acceptance_path=graph['external_acceptance_path'],observations=len(receipts),stored_entities=len(list((D/'bodies').glob('*')))))
 buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=list(authorities[0]));w.writeheader();w.writerows(authorities);out['../official-results-sources.csv']=buf.getvalue().encode()
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ns=ap.parse_args();out=products()
 for name,b in out.items():
  assert len(b)<40000000,(name,len(b));p=D/name
  if ns.check:assert p.read_bytes()==b,('offline_rebuild_difference',name)
  else:p.write_bytes(b)
 print('offline products verified' if ns.check else 'offline products written',len(out))
if __name__=='__main__':main()
