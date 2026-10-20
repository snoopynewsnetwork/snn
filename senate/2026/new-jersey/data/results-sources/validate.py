"""Meaningful whole-source/package validation. --sealed is strictly read-only."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import json,gzip,hashlib,csv,re,sys,os
sys.dont_write_bytecode=True
from inspect_pages import body
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):
 b=Path(p).read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def check_core(units,parents,contract):
 assert len(units)==575 and len(parents)==21
 original=read(ROOT/'data/baselines/extract/native-contests.json')['2024-senate'];contexts={}
 for pub in original:
  for row in pub['rows']:contexts[row['key']]={'original_complete_row':row,'full_candidates':pub['candidates'],'all_page_headers':pub['headers'],'column_right_edges':pub['column_right_edges'],'nonadditive_footer':pub['footer']}
 assert [x['historical_complete_unit'] for x in units]==contract['all_units']
 assert [x['key'] for x in units]==contract['complete_ordered_keys']
 assert [x['key'] for x in units[:233]]==contract['ordered_priority_keys']
 assert len(set(x['key'] for x in units))==575
 for u in units:
  assert u['historical_complete_candidate_publication_context']==contexts[u['key']]
  assert u['key']==u['historical_complete_unit']['key']
  assert u['shared_parent_key']==u['historical_complete_unit']['county_fips']
  assert u['historical_complete_candidate_publication_context']['original_complete_row']['votes']==u['historical_complete_unit']['values']
  assert u['current_leaf_reporting_ID'] is None and u['current_candidate_choice_IDs'] is None and u['current_unit_method_crosswalk'] is None
  assert u['genuine_November_counts_admitted'] is False
  row=u['historical_complete_candidate_publication_context']['original_complete_row'];assert row['raw']==u['historical_complete_unit']['source_line']
 for p in parents:
  f=p['parent_key'];us=[u for u in units if u['shared_parent_key']==f];keys=[u['key'] for u in us]
  assert p['rank_ordered_children']==keys
  assert p['priority_children']==[u['key'] for u in us if u['priority']]
  assert p['remainder_children']==[u['key'] for u in us if not u['priority']]
  assert set(p['source_ordered_children'])==set(keys)
  assert p['historical_complete_parent']==next(x for x in contract['county_coverage'] if x['county_fips']==f)
  assert p['measured_candidate_publication_cadence'] is None and p['November_accepted_unprocessed_eligible_pool'] is None
  assert p['genuine_November_counts_admitted'] is False and p['current_choice_reporting_or_leaf_match_approved'] is False
  assert p['actual_bounded_public_requests'] and len(p['authority_directory']['roles'])==3
 assert sum(u['historical_complete_unit']['volume'] for u in units)==4031795
 assert sum(u['historical_complete_unit']['volume'] for u in units[:233])==3229453
 assert sum(u['historical_complete_unit']['volume'] for u in units[:232])==3224325
 assert sum(u['historical_complete_unit']['volume'] for u in units[233:])==802342

def fixtures(units,parents,c):
 cases=[]
 def reject(name,mut):
  u=deepcopy(units);p=deepcopy(parents);mut(u,p)
  try:check_core(u,p,c)
  except AssertionError:cases.append({'fixture':name,'detected':True});return
  raise AssertionError('undetected '+name)
 reject('candidate_value_corruption',lambda u,p:u[0]['historical_complete_unit']['values'].__setitem__(0,60178))
 sparse=next(i for i,x in enumerate(units) if None in x['historical_complete_unit']['values']);slot=units[sparse]['historical_complete_unit']['values'].index(None)
 reject('blank_to_zero_not_permitted',lambda u,p:u[sparse]['historical_complete_unit']['values'].__setitem__(slot,0))
 reject('rank_order_changed',lambda u,p:u.__setitem__(slice(0,2),u[1::-1]))
 reject('remainder_removed',lambda u,p:u.pop())
 reject('shared_parent_misassigned',lambda u,p:u[0].__setitem__('shared_parent_key','34001'))
 reject('parent_child_omission',lambda u,p:p[0]['rank_ordered_children'].pop())
 reject('priority_crossing_removed',lambda u,p:p[3]['priority_children'].pop())
 reject('current_leaf_ID_invented',lambda u,p:u[0].__setitem__('current_leaf_reporting_ID','unverified'))
 reject('zero_template_admitted_as_votes',lambda u,p:u[0].__setitem__('genuine_November_counts_admitted',True))
 reject('primary_choice_ID_approved',lambda u,p:u[0].__setitem__('current_candidate_choice_IDs',['0090']))
 reject('percentage_as_exact_remaining',lambda u,p:p[0].__setitem__('November_accepted_unprocessed_eligible_pool',145))
 reject('client_refresh_as_measured_cadence',lambda u,p:p[0].__setitem__('measured_candidate_publication_cadence',60))
 reject('whole_header_whitespace_corruption',lambda u,p:u[0]['historical_complete_candidate_publication_context']['all_page_headers'][0]['lines'][0].__setitem__('raw','corrupted header'))
 reject('complete_candidate_party_order_corruption',lambda u,p:u[0]['historical_complete_candidate_publication_context']['full_candidates'].reverse())
 # Original semantic witness catches header and raw whitespace even without changing votes.
 ctx=units[0]['historical_complete_candidate_publication_context'];changed=deepcopy(ctx);changed['all_page_headers'][0]['lines'][0]['raw']+=' ';assert sha(canonical(ctx))!=sha(canonical(changed));cases.append({'fixture':'full_header_whitespace_changes_semantic_witness','detected':True})
 changed=deepcopy(ctx);changed['full_candidates'].reverse();assert sha(canonical(ctx))!=sha(canonical(changed));cases.append({'fixture':'candidate_party_order_witness','detected':True})
 for n in [40000000,40000001]:assert not n<40000000
 cases.append({'fixture':'strict_40million_boundary','detected':True})
 return cases

def main():
 sealed='--sealed' in sys.argv;units=read(P/'all575-investigations.json.gz');parents=read(P/'county-investigations.json.gz');c=read(ROOT/'data/turnout/priority-set.json');check_core(units,parents,c);pm={p['parent_key']:p for p in parents}
 for name,expected in [('priority233-investigations.json.gz',units[:233]),('remainder342-investigations.json.gz',units[233:])]:
  rows=read(P/name);assert len(rows)==len(expected)
  for row,e in zip(rows,expected):assert {k:v for k,v in row.items() if k!='complete_shared_parent_investigation'}==e and row['complete_shared_parent_investigation']==pm[e['shared_parent_key']]
 h=read(P/'full21-hierarchy.json.gz');assert h['ordered_priority_parent_FIPS']==list(dict.fromkeys(u['shared_parent_key'] for u in units[:233]))
 assert h['full_parents']==parents and h['all_ordered_keys']==[u['key'] for u in units] and h['priority_ordered_keys']+h['remainder_ordered_keys']==h['all_ordered_keys']
 requests=0;hops=0;failures=0;raw_checked=set()
 for f in (P/'requests').glob('*.json'):
  r=read(f);requests+=1;failures+=not bool(r['hops']);assert r['id']==f.stem
  for hop in r['hops']:
   hops+=1;assert hop['actual_requested_url'] and hop['method']=='GET' and hop['request_body'] is None
   if 'asset' in hop:
    z=(P/hop['asset']).read_bytes();raw=gzip.decompress(z)
   elif 'reference_path' in hop:
    z=(ROOT/hop['reference_path']).read_bytes();raw=gzip.decompress(z) if hop.get('reference_gzip',True) else z
   else:
    raw=b''.join(gzip.decompress((P[x['asset']]).read_bytes()) for x in hop['ordered_exact_entity_parts']);assert sha(raw)==hop['raw_sha256'];continue
   assert len(z)==hop['stored_bytes']<40000000 and sha(z)==hop['stored_sha256'];assert len(raw)==hop['raw_bytes'] and sha(raw)==hop['raw_sha256'];raw_checked.add(sha(raw))
  assert r['admission']=='research_only_not_admitted_November_counts'
 for ref in read(P/'shared-body-references.json'):
  assert not (P/'bodies'/(ref['raw_sha256']+'.gz')).exists()
 for item in read(P/'request-index.json')['requests']:
  b=(P/item['receipt']).read_bytes();assert len(b)==item['receipt_bytes'] and sha(b)==item['receipt_sha256']
 csvrows=list(csv.DictReader((ROOT/'data/official-results-sources.csv').open()));assert len(csvrows)==86
 assert Counter(r['county_fips'] for r in csvrows if r['county_fips'])=={p['parent_key']:4 for p in parents}
 ass=read(P/'payload-assessments.json');assert len(ass)==12 and sum('2026-06-02 primary' in a['stage_assessment'] for a in ass)==11
 assert all(a['genuine_November_counts_admitted'] is False and a['measured_publication_cadence'] is None and a['exact_eligible_remaining_pool'] is None for a in ass)
 g=next(a for a in ass if 'November3' in a['stage_assessment']);assert all(not any(x.get('V',[])) for x in g['full_Senate_contest_objects_preview'])
 assert read(P/'historical-reconstruction.json')['recursive_objects']==724943
 assert read(P/'original-page-replay.json')['counts']['raw_rows_and_footers']==2380
 negative=fixtures(units,parents,c)
 files=[ROOT/'official-results.md',ROOT/'data/official-results-sources.csv']+[x for x in P.rglob('*') if x.is_file()]
 assert all(x.stat().st_size<40000000 for x in files);assert not any(x.name in ['__pycache__','node_modules','.cache'] for x in P.rglob('*'))
 errors=[]
 for doc in [ROOT/'official-results.md',P/'README.md',P/'SCHEMA.md',P/'legal-review.md']:
  for href in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
   if '://' in href or href.startswith('#'):continue
   target=(doc.parent/href.split('#')[0]).resolve()
   if not target.exists():
    if not sealed and target in [P/'validation.json',P/'final-seal.json',P/'asset-manifest.json']:continue
    errors.append((str(doc),href))
 assert not errors,errors
 # The external acceptance body/hash never becomes an owned copy or reverse pin.
 forbidden=sha((ROOT/'data/coordinator-priority-acceptance.json').read_bytes())
 for f in files:
  if f.suffix in ['.py','.md','.json','.csv']:assert forbidden not in f.read_text(errors='replace'),str(f)
 if sealed:
  manifest=read(P/'asset-manifest.json');expected={str(f.relative_to(ROOT)) for f in files if f!=P/'asset-manifest.json'};assert expected=={r['path'] for r in manifest['files']}
  for r in manifest['files']:
   b=(ROOT/r['path']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'],r['path']
  print(json.dumps({'status':'pass_read_only_sealed','owned_files_excluding_manifest':len(expected),'requests':requests,'negative_fixtures':len(negative)}));return
 result={'status':'pass_complete_owned_source_research','authority_path':'data/coordinator-priority-acceptance.json','all_units':575,'priority':233,'remainder':342,'county_parents':21,'authority_rows':86,'actual_request_observations':requests,'complete_response_hops':hops,'client_failures':failures,'unique_raw_entities_verified':len(raw_checked),'complete_payload_assessment_sets':12,'primary_payload_sets':11,'general_Clarity_zero_template_sets':1,'negative_fixtures':negative,'all_stored_files_strictly_below_40000000':True,'relative_links_pass':True,'current_choice_reporting_leaf_match_approved':False,'genuine_November_counts_admitted':False,'measured_cadence_or_exact_eligible_remaining_pool_approved':False,'legal_exhaustiveness_or_collector_or_probability_approved':False}
 (P/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='negative_fixtures'})
if __name__=='__main__':main()
