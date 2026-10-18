#!/usr/bin/env python3
"""Read-only full independent peer agreement after own extraction; never changes peer files."""
import csv,gzip,json,re
from collections import Counter
from pathlib import Path
from parse_sources import D,FIELDS,sha,writejson
from build import readcsv,norm
P=D.parent/'turnout'
def jl(p):
 with gzip.open(p,'rt') as f:return [json.loads(line) for line in f]
def main():
 pinned=[]
 def pin(p):pinned.append({'path':str(p.relative_to(D.parent.parent)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())})
 own=readcsv(D/'native-source-rows.csv.gz');om={(r['source_id'],r['source_member'],int(r['source_row_1based'])):r for r in own};assert len(om)==len(own);fields=0;rawrows=0
 for year in [2024,2022,2020]:
  p=P/'extracts'/f'native-source-rows-{year}.jsonl.gz';pin(p)
  for peer in jl(p):
   key=(peer['source_id'],peer['source_member'],peer['source_row_1based']);r=om.pop(key);assert [r[k] for k in FIELDS]==peer['fields'],key;assert (r['base_selected']=='True')==(not peer['recount_overlap_excluded']);ids=json.loads(r['native_key']);assert ids[2:]==[peer['fields'][i] for i in [0,2,5,6]];fields+=19;rawrows+=1
 assert not om
 p=P/'extracts/primary-county-candidates.csv';pin(p);peer=readcsv(p);om={('_'.join([r['year'],r['contest']]),r['county'],r['candidate_name']+' ('+r['party']+')'):r for r in readcsv(D/'official-county-candidates.csv')}
 for r in peer:
  k=(r['context'],r['county'],r['candidate_party']);a=om.pop(k);assert int(a['votes'])==int(r['votes']) and int(a['source_tr_1based'])==int(r['source_tr']) and int(a['source_column_1based'])==int(r['source_td_1based'])
 assert not om
 p=P/'extracts/native-units.jsonl.gz';pin(p);peernative=jl(p);nm={(r['year']+'_'+r['contest'],r['county_code'],r['election_number'],r['precinct_id'],r['polling_location']):r for r in readcsv(D/'native-units.csv.gz')}
 for r in peernative:
  k=(r['context'],r['county_code'],r['election_number'],r['precinct_id'],r['polling_location']);a=nm.pop(k);assert json.loads(a['registration_contexts'])==r['registration_observations'];assert json.loads(a['candidate_keys'])==sorted([x['candidate_label'],x['party'],x['fvrs_id'],x['doe_candidate_id']] for x in r['candidate_category_rows']);assert sorted(json.loads(a['source_positions']))==sorted([r['source_member'],c['source_row_1based']] for c in r['candidate_category_rows'])
  for name,party in [('A','DEM'),('B','REP')]:assert int(a[name])==sum(c['votes'] for c in r['candidate_category_rows'] if c['party']==party)
  for field,code in [('generic_writein_marks','900'),('overvotes','901'),('undervotes','902')]:assert int(a[field])==sum(c['votes'] for c in r['candidate_category_rows'] if c['doe_candidate_id']==code)
  assert 'not separately coded' in r['method_scope'] and a['method']=='not_provided_in_19field_schema'
 assert not nm
 p=P/'priority-set.json';pin(p);prio=json.loads(p.read_text());gulf=next(r for r in prio['all_unit_order'] if r['fips']=='12045');assert gulf['ordinary_poll_close_2026_utc'] is None and gulf['ordinary_election_admin_clock'] is None;repair=json.loads((P/'priority-freeze-repair.json').read_text());assert sha(p.read_bytes())==repair['expected_repaired_sha256'] and p.stat().st_size==repair['expected_repaired_bytes'];pin(P/'priority-freeze-repair.json');ownp=json.loads((D/'priority-contract.json').read_text());assert [(r['county_fips'],r['all_candidate_votes'],r['cumulative_votes']) for r in ownp['all67_order']]==[(r['fips'],r['votes'],r['cumulative_votes']) for r in prio['all_unit_order']]
 # All shared EAVS controls, exact sentinel/blank/comment values and source row positions.
 ecount=0;p=P/'extracts/eavs-controls.jsonl.gz';pin(p);em={(r['year'],r['county_fips']):r for r in json.loads((D/'eavs-controls.json').read_text())}
 for r in jl(p):
  a=em.pop((r['context'],r['fips']));assert a['source_member']==r['source_member'] and a['source_csv_row_1based']==r['source_csv_row_1based']
  for k in set(a['fields'])&set(r['fields']):assert a['fields'][k]==r['fields'][k],(r['fips'],k);ecount+=1
 assert not em
 p=P/'extracts/bookclosing-controls.jsonl.gz';pin(p);bm={(r['year'],r['county_fips']):r for r in json.loads((D/'bookclosing-controls.json').read_text())};bcount=0
 for r in jl(p):
  a=bm.pop((r['context'],r['fips']));assert a['sheet']==r['sheet'] and a['row']==r['row'] and a['cells']==r['cells'];bcount+=len(a['cells'])
 assert not bm
 p=D.parent/'county-turnout.csv';pin(p);turnout=readcsv(p);ownc=readcsv(D.parent/'county-baselines.csv');summ={r['county_fips']:r for r in turnout};shared=0
 for a in ownc:
  r=summ[a['county_fips']];ctx=a['year']+'_'+a['contest'];assert norm(a['county'])==norm(r['county']) and a['county_code']==r['source_county_code']
  for ours,theirs in [('all_candidate_votes','candidate_votes'),('valid_named_writein_votes','valid_named_writeins'),('compiled_generic_writein_marks','generic_writein_marks'),('compiled_overvotes','overvotes'),('compiled_undervotes','undervotes'),('native_context_count','native_units')]:assert int(a[ours])==int(r[ctx+'_'+theirs]);shared+=1
  assert int(a['compiled_A_votes'])+int(a['compiled_B_votes'])+int(a['compiled_other_printed_votes'])==int(r[ctx+'_compiled_named_ballot_votes']);shared+=1
 for p in [D/'native-source-rows.csv.gz',D/'native-units.csv.gz',D/'official-county-candidates.csv',D/'priority-contract.json',D/'eavs-controls.json',D/'bookclosing-controls.json',D.parent/'county-baselines.csv']:pin(p)
 result={'status':'passed_read_only_independent_comparison','coordinator_acceptance':False,'raw_selected_source_rows':rawrows,'raw19_field_equalities':fields,'official_county_candidate_cells':len(peer),'native_contexts':len(peernative),'all_county_shared_control_cells':shared,'shared_EAVS_field_equalities':ecount,'bookclosing_exact_cells':bcount,'ordered_counties':67,'minimum80_count':ownp['minimum80_count'],'minimum80_total':ownp['minimum80_total'],'prior_total':ownp['prior_total'],'source_method_scope':'no explicit method field; identical raw labels preserved, no label-based method allocation','current_geography_approved':False,'Gulf_clock_metadata_repair':{'current_close':None,'current_admin_clock':None,'new_contract_sha256':repair['expected_repaired_sha256'],'new_contract_bytes':repair['expected_repaired_bytes'],'old_pin_superseded':repair['prior_pin']['sha256'],'verification':'all independent raw/candidate/native/order/control comparisons rerun unchanged; Gulf nulls explicitly checked'},'pinned_assets':pinned};writejson(D/'peer-agreement.json',result);print(json.dumps({k:v for k,v in result.items() if k!='pinned_assets'},indent=2))
if __name__=='__main__':main()
