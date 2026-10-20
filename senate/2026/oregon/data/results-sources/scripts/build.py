"""Deterministic report/inventory/context rebuild from fixed complete input references."""
from pathlib import Path
from replay_inputs import load_catalogs,read,parse,semantic,sha,R,S
import gzip,json,csv,io,re,collections,sys

def enc(x):return (json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
def jsonl(x):return gzip.compress(b''.join(json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()+b'\n' for v in x),mtime=0)
def owned_ref(p):
 b=p.read_bytes();return {'path':str(p.relative_to(S)),'bytes':len(b),'sha256':sha(b)}
def whole_ref(ref,obj,pointer=''):
 return {'file':ref,'pointer':pointer,'whole_object_semantic_sha256':semantic(obj),'retention':'complete_recursive_object_no_projection'}
def derive():
 a=load_catalogs();refs={x['path']:x for x in a['complete_source_companion_files']};contract_ref=a['frozen_contract'];contract=json.loads(read(contract_ref))
 index=json.loads((R/'acquisition-index.json').read_bytes());requests={};structures={}
 for row in index:
  requests[row['key']]=json.loads(read(row['request']));structures[row['key']]=json.loads(gzip.decompress(read(row['structure'])))
 notes=json.loads((R/'parent-findings.json').read_bytes());assert len(notes)==36
 dirrecords=[]
 for key in ['fvap-offices-1','fvap-offices-2']:
  d=structures[key]['complete_object'];assert d['recordsTotal']==d['recordsFiltered']==36
  for i,obj in enumerate(d['data']):dirrecords.append({'raw':obj,'full_response':next(x['structure'] for x in index if x['key']==key),'pointer':'/complete_object/data/'+str(i),'raw_record_semantic_sha256':semantic(obj)})
 assert len(dirrecords)==36
 directory={d['raw']['jurisdiction']['name']:d for d in dirrecords}
 units_ref=refs['data/turnout/native/units.json'];units=parse(units_ref);unit_index=collections.defaultdict(list)
 for i,u in enumerate(units):unit_index[u['unit_key']].append((i,u))
 raw_ref=refs['data/turnout/native/observations.jsonl.gz'];raw=parse(raw_ref);raw_index=collections.defaultdict(list)
 for i,o in enumerate(raw):raw_index[o['unit_key']].append((i,o))
 parentout=[];contexts=[];unavailable=[];csvrows=[]
 def current_requests(slug):
  # Explicit index snapshots only; no mutable peer/receipt discovery.
  return [row for row in index if row['key'].startswith('county-'+slug+'-') or row['key'].startswith(slug+'-') or (slug=='multnomah' and row['key'].startswith('multnomah-')) or (slug=='washington' and row['key'].startswith('washington-')) or (slug=='deschutes' and row['key'].startswith('deschutes-')) or (slug=='columbia' and row['key'].startswith('columbia-')) or (slug=='wallowa' and row['key'].startswith('wallowa-')) or (slug=='yamhill' and row['key'].startswith('yamhill-')) or (slug=='coos' and row['key'].startswith('coos-')) or (slug=='tillamook' and row['key'].startswith('tillamook-'))]
 for i,p in enumerate(contract['all_36_county_parents']):
  slug=p['county'].lower().replace(' ','-');dirrow=directory[p['county']];assert dirrow['raw']['jurisdiction']['fipsCode'][:5]==p['county_fips']
  req=current_requests(slug);assert req
  bb=next(x for x in index if x['key']=='bluebook-'+slug)
  obj={'parent_key':p['county_key'],'county':p['county'],'county_fips':p['county_fips'],'complete_original_parent':whole_ref(contract_ref,p,'/all_36_county_parents/'+str(i)), 'directory':dirrow,'bluebook_authority':bb,'investigation':notes[slug],'complete_current_response_references':req,'investigation_scope':'bounded shared-parent public chain; not independent feeds for each historical leaf','native_membership_known_2024':p['native_reporting_unit_count'],'current_native_membership':None,'current_leaf_mapping':None,'method_crosswalk':None,'source_field_absence_claim':False,'measured_genuine_update_cadence':None,'eligible_outstanding_pool':None,'current_source_admission':False,'geometry_approval':False,'final_exhaustive_roster_approval':False,'eligible_named_write_in_universe':None,'coordinator_acceptance':False}
  parentout.append(obj)
  if p['native_reporting_unit_count'] is None:
   unavailable.append(obj)
  for j,child in enumerate(p['source_native_constituents']):
   presentations=[]
   for pres in child['source_presentations']:
    k=pres.get('observations_unit_key');uu=unit_index.get(k,[]);rr=raw_index.get(k,[])
    assert uu and rr,(child['key'],k)
    presentations.append({'complete_contract_presentation':whole_ref(contract_ref,pres,f'/all_36_county_parents/{i}/source_native_constituents/{j}/source_presentations/{len(presentations)}'),'explicit_source_observation_unit_key':k,'full_normalized_object_references':[whole_ref(units_ref,u,'/'+str(n)) for n,u in uu],'full_raw_observation_references':[whole_ref(raw_ref,o,'/'+str(n)) for n,o in rr]})
   contexts.append({'historical_context_key':child['key'],'parent_key':p['county_key'],'complete_source_context':whole_ref(contract_ref,child,f'/all_36_county_parents/{i}/source_native_constituents/{j}'),'full_presentations':presentations,'investigation_parent':'data/results-sources/parents.jsonl.gz#'+p['county_key'],'current_observation_chain':[r['key'] for r in req],'scope':'one complete historical context investigated through its shared authoritative parent; not an independent current feed','current_leaf_ID':None,'current_geometry_ID':None,'method_identity_join':None,'current_approval':False})
  root=next(x for x in req if x['key']=='county-'+slug+'-root');r=requests[root['key']]
  local=[q for q in req if any(w in q['key'] for w in ['publication','chain','elections','current-results'])]
  csvrows.append({'authority':'county','county':p['county'],'fips':p['county_fips'],'role_literal':dirrow['raw']['name'],'directory_website_literal':dirrow['raw']['website'],'directory_record':'data/results-sources/directory-records.json.gz#'+p['county'],'county_requested_url':r['requested_url'],'county_final_url':r['final_url'],'root_status':r['entities'][-1]['status'] if r['entities'] else '', 'root_access_error':r['error'] or '', 'publication_urls_json':json.dumps([requests[q['key']]['requested_url'] for q in local],ensure_ascii=False),'historical_known_native_rows':p['native_reporting_unit_count'] if p['native_reporting_unit_count'] is not None else 'NULL','native_membership_status':p['native_priority_status'],'current_senate_return_admitted':'false','current_leaf_crosswalk':'NULL','measured_cadence':'NULL','eligible_remaining_pool':'NULL','complete_parent':'data/results-sources/parents.jsonl.gz#'+p['county_key'],'findings':notes[slug]})
 assert len(contexts)==510 and len(unavailable)==31
 keys=[x['historical_context_key'] for x in contexts];assert len(set(keys))==510 and set(keys)==set(contract['known_source_universe']['full_ordered_keys'])
 # Retain canonical known order; it remains descriptive and never becomes statewide native order.
 bykey={x['historical_context_key']:x for x in contexts};contexts=[bykey[k] for k in contract['known_source_universe']['full_ordered_keys']]
 for k in ['complete_order','ordered_priority_keys','top15','minimum80','remainder']:assert contract[k] is None
 state={k:'' for k in csvrows[0]};state.update(authority='state',county='Oregon',role_literal='Secretary of State Elections Division',county_requested_url=requests['sos-current']['requested_url'],county_final_url=requests['sos-current']['final_url'],root_status=200,publication_urls_json=json.dumps([requests[k]['requested_url'] for k in ['sos-history','sos-results-root']]),historical_known_native_rows='510 known across5;31 parents unavailable',native_membership_status='canonical_statewide_native_unavailable',current_senate_return_admitted='false',current_leaf_crosswalk='NULL',measured_cadence='NULL',eligible_remaining_pool='NULL',findings='Complete state/36county inventory. Actual production root redirects to generic SOS welcome; literal older county routes404. Search-visible staging and public CSV are rejected. Registered/received/accepted/tallied/reported lanes remain separate.')
 stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=list(csvrows[0]),lineterminator='\n');w.writeheader();w.writerows([state]+csvrows)
 coverage={'external_acceptance_authority':'data/coordinator-source-research-acceptance.json','complete_contract_roots':23,'whole_companions':1994,'ordered_ledger_partitions':4,'complete_recursive_containers':495672,'immutable_current_file_pins':5029,'historical_virtual_bodies':5261,'whole_original_entity_texts':113,'zip_members':72,'counties':36,'known_source_contexts':510,'shared_known_parents':{'Multnomah':107,'Washington':155,'Clackamas':118,'Marion':118,'Wasco':12},'unavailable_native_parent_cases':31,'historical_normalization':'partial; original byte retention complete','turnout_historical_closure':[16,13,12],'baseline_historical_closure':[16,13,13],'statewide_president_reported_2024':2244493,'seven_named_choice_votes':2229467,'generic_Misc':15026,'eligible_named_write_in_scope':None,'known_native_reported_votes':1128521,'unclosed_parent_reported_votes':1115972,'known_only_top15':112024,'known_only_min80':{'rows':213,'votes':904600,'preceding_rows':212,'preceding_votes':902447},'separate_county_min80':{'counties':11,'votes':1814630,'preceding_counties':10,'preceding_votes':1764398},'canonical_native_full_order':None,'canonical_native_top15':None,'canonical_native_minimum80':None,'canonical_native_priority':None,'canonical_native_remainder':None,'current_geography_approved':False,'current_November_returns_admitted':False,'current_choice_or_reporting_IDs_approved':False,'legal_native_80_robustness_approved':False,'live_cadence_or_exact_remainder_approved':False,'collector_or_probability_approval':False,'coordinator_acceptance':False,'bounded_worker_research_complete':True,'actual_acquisition_requests':len(index)}
 report=(R/'report-body.md').read_text()
 report+='\n\nAll 36 county investigations are indexed below. The linked parent records carry the full directory object, exact complete historical parent reference and every captured current response; the separate context ledger carries all 510 complete source contexts. A blank directory website is preserved as a blank.\n\n| County | Bounded source finding |\n| --- | --- |\n'
 for obj in parentout:
  slug=obj['county'].lower().replace(' ','-');root=next(x for x in obj['complete_current_response_references'] if x['key']=='county-'+slug+'-root');url=requests[root['key']]['requested_url'];report+='| ['+obj['county']+']('+url+') | '+notes[slug].replace('|','\\|')+' |\n'
 report+='\nRebuild and verification: [schema and reproduction](data/results-sources/SCHEMA.md), [coverage](data/results-sources/coverage.json), [input replay](data/results-sources/input-replay.json), [original replay](data/results-sources/original-replay.json), [complete source inventory](data/official-results-sources.csv).\n'
 return {'data/results-sources/parents.jsonl.gz':jsonl(parentout),'data/results-sources/known-contexts.jsonl.gz':jsonl(contexts),'data/results-sources/unavailable-parents.jsonl.gz':jsonl(unavailable),'data/results-sources/directory-records.json.gz':gzip.compress(enc(dirrecords),mtime=0),'data/results-sources/coverage.json':enc(coverage),'data/official-results-sources.csv':stream.getvalue().encode(),'official-results.md':report.encode()}

def main():
 outputs=derive()
 if '--write' in sys.argv:
  for path,b in outputs.items():(S/path).write_bytes(b)
  print('built',len(outputs),'complete reports/context artifacts')
 else:
  for path,b in outputs.items():assert (S/path).read_bytes()==b,'deterministic offline rebuild differs: '+path
  print('pass deterministic offline rebuild',len(outputs))
if __name__=='__main__':main()
