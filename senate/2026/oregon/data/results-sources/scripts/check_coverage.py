"""Full context/column/hierarchy assertions and research qualifications, read-only."""
from replay_inputs import load_catalogs,read,parse,sha,S,R,semantic
from resolve import resolve_object
import json,gzip,csv,io,collections

def rows(name):return [json.loads(x) for x in gzip.decompress((R/name).read_bytes()).splitlines()]
def validate_contract(c):
 assert len(c['all_36_county_parents'])==36
 for k in ['complete_order','ordered_priority_keys','top15','minimum80','remainder']:assert c[k] is None,'unavailable canonical field promoted '+k
 p=c['all_36_county_parents'];children=[u for r in p for u in r['source_native_constituents']]
 assert len(children)==510 and len({x['key'] for x in children})==510
 assert sum(r['native_reporting_unit_count'] is None for r in p)==31
 assert sum(u['reported_votes'] for u in children)==1128521
 assert sum(r['county_presidential_reported_votes'] for r in p)==2244493
 for r in p:
  if r['native_reporting_unit_count'] is None:assert not r['source_native_constituents']
  else:
   assert len(r['source_native_constituents'])==r['native_reporting_unit_count']
   assert sum(x['reported_votes'] for x in r['source_native_constituents'])==r['county_presidential_reported_votes']
  for u in r['source_native_constituents']:
   assert len(u['candidate_vector'])==8 and sum(u['candidate_vector'])==u['reported_votes']
   assert u['current_result_id'] is None and u['current_geometry_id'] is None and u['current_approval'] is False
   if len(u['source_native_constituent_ids'])>1:assert 'no' in u['count_allocation_to_constituents'].lower() or 'unalloc' in u['count_allocation_to_constituents'].lower()
 return True

def main():
 a=load_catalogs();refs={r['path']:r for r in a['complete_source_companion_files']};c=json.loads(read(a['frozen_contract']));validate_contract(c)
 parents=rows('parents.jsonl.gz');known=rows('known-contexts.jsonl.gz');unknown=rows('unavailable-parents.jsonl.gz');assert len(parents)==36 and len(known)==510 and len(unknown)==31
 assert [x['historical_context_key'] for x in known]==c['known_source_universe']['full_ordered_keys']
 n=0
 for p in parents:
  x=resolve_object(p['complete_original_parent']);assert x['county_key']==p['parent_key'];assert p['current_leaf_mapping'] is None and p['coordinator_acceptance'] is False
 for k in known:
  child=resolve_object(k['complete_source_context']);assert child['key']==k['historical_context_key']
  for p in k['full_presentations']:
   pr=resolve_object(p['complete_contract_presentation']);assert pr['observations_unit_key']==p['explicit_source_observation_unit_key']
   for r in p['full_normalized_object_references']+p['full_raw_observation_references']:
    obj=resolve_object(r);assert obj['unit_key']==pr['observations_unit_key'];n+=1
 assert {p['parent_key'] for p in unknown}=={p['parent_key'] for p in parents if p['native_membership_known_2024'] is None}
 # Independent explicit ordinal adapter, all864cells and every source row/party retained.
 tr=list(csv.DictReader(io.StringIO(read(refs['data/turnout/county-candidates.csv']).decode('utf-8-sig'))))
 br=list(csv.DictReader(io.StringIO(read(refs['data/baselines/county-candidates.csv']).decode('utf-8-sig'))))
 assert len(tr)==len(br)==864
 bmap={(r['contest'],r['fips'],int(r['source_candidate_column'])-1):r for r in br};sums=collections.Counter();counties=collections.defaultdict(set)
 for row in tr:
  key=(row['contest'],row['county_fips'],int(row['column_index']));b=bmap[key]
  for left,right in [('candidate','candidate'),('party_label','party_source'),('votes','votes'),('source_key','source_key'),('PDF_page','page'),('text_line_1based','line'),('raw_line','raw_line')]:assert row[left]==b[right],(key,left)
  sums[(key[0],key[2])]+=int(row['votes']);counties[key[0]].add(key[1])
 for f in parse(refs['data/turnout/source/statewide-footers.json']):
  assert len(counties[f['contest']])==36
  for i,v in enumerate(f['values']):assert sums[(f['contest'],i)]==v
 # Party scope must survive even where display-friendly coalitions differ.
 johnson=[r for r in tr if r['contest']=='2022-governor' and r['candidate']=='Betsy Johnson'];assert len(johnson)==36 and {r['party_label'] for r in johnson}=={'NAV'}
 # Current staging export keeps all fields, excess trailing blank and exact IDs.
 d=json.loads(gzip.decompress((R/'structures/sos-staging-csv-negative.json.gz').read_bytes()));assert len(d['complete_rows'])==26 and len(d['complete_rows'][0])==15 and {len(x) for x in d['complete_rows'][1:]}=={16}
 senate=[r for r in d['complete_rows'][1:] if r[1]=='US Senator'];assert len(senate)==5 and sum(int(r[12]) for r in senate)==209 and {r[14] for r in senate}=={'0/1318'}
 cov=json.loads((R/'coverage.json').read_bytes());assert cov['current_November_returns_admitted'] is False and cov['eligible_named_write_in_scope'] is None
 return {'status':'pass','all_parent_objects':36,'complete_known_contexts':510,'complete_unavailable_parent_cases':31,'full_native_and_raw_object_bindings':n,'all_county_candidate_positions':864,'whole_staging_csv_records':26,'staging_admitted':False,'historical_normalization':'partial','canonical_statewide_native_priority':None}
if __name__=='__main__':print(json.dumps(main(),indent=2))
