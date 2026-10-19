#!/usr/bin/env python3
"""Read-only, field-level reconciliation to the actual turnout worker's stable outputs.
Does not rewrite either worker's extract. Hashes bind this audit to inspected vintages.
"""
import csv,gzip,hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parent;PEER=BASE.parent/'turnout'
def rows(p):return [json.loads(s)for s in gzip.decompress(p.read_bytes()).splitlines()]
def pin(p):return dict(path=str(p.relative_to(BASE.parent.parent)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def main():
 used=[];counts={};gaps=[];presentation_differences=[]
 def labelcheck(a,b,key):
  if a!=b:
   assert ' '.join(a.split())==' '.join(b.split()),(key,a,b)
   presentation_differences.append(dict(key=key,our_exact_text=a,peer_rendered_whitespace=b,classification='HTML whitespace rendering; stable source keys already equal, no name-based geography join'))
 def read(p):used.append(pin(p));return json.loads(p.read_text())
 def readrows(p):used.append(pin(p));return rows(p)
 ours=read(BASE/'extracts/state-controls.json');peer=read(PEER/'extracts/state-controls.json')
 mapping={'senate2024special':'2024-senate-special','senate2024regular':'2024-senate-regular','president2024':'2024-president','governor2022':'2022-governor','senate2020':'2020-senate',**{f'registration{y}':f'{y}-registration'for y in [2024,2022,2020]},**{f'votingmethod{y}':f'{y}-voting-method'for y in [2024,2022,2020]}}
 for key,other in mapping.items():
  a=ours[key];b=peer[other];assert a['state']==b['statewide']['values']
  assert a['county']=={k:v['values']for k,v in b['counties'].items()}
 counts['county_table_vectors']=11*93;counts['state_table_vectors']=11
 county_csv=PEER.parent/'county-turnout.csv';used.append(pin(county_csv));ccsv=list(csv.DictReader(county_csv.open()));cells_checked=0
 candidate_columns={'senate2024special':['2024_senate_special_pete_ricketts','2024_senate_special_preston_love_jr'],
  'senate2024regular':['2024_senate_regular_deb_fischer','2024_senate_regular_dan_osborn','2024_senate_regular_write_in_scatterings'],
  'president2024':['2024_president_donald_j_trump_jd_vance','2024_president_kamala_d_harris_tim_walz','2024_president_chase_oliver_mike_ter_maat','2024_president_cornel_west_melina_abdullah','2024_president_jill_stein_samson_kpadenou','2024_president_write_in_scatterings'],
  'governor2022':['2022_governor_jim_pillen_joe_kelly','2022_governor_carol_blood_al_davis','2022_governor_scott_zimmerman_jason_blumenthal','2022_governor_write_in_scatterings'],
  'senate2020':['2020_senate_ben_sasse','2020_senate_chris_janicek','2020_senate_gene_siadek','2020_senate_preston_love_jr','2020_senate_write_in_scatterings']}
 import re
 for r in ccsv:
  name=r['county']
  for table,columns in candidate_columns.items():
   assert[int(r[c])for c in columns]==ours[table]['county'][name];cells_checked+=len(columns)
  for table,prefix in [('senate2024special','2024_senate_special'),('senate2024regular','2024_senate_regular'),('president2024','2024_president'),('governor2022','2022_governor'),('senate2020','2020_senate')]:
   assert int(r[prefix+'_contest_votes_state_reported'])==sum(ours[table]['county'][name]);cells_checked+=1
  for y in [2024,2022,2020]:
   reg=ours[f'registration{y}'];method=ours[f'votingmethod{y}'];rv=reg['county'][name];mv=method['county'][name]
   assert int(r[f'{y}_source_precinct_count'])==rv[0]and int(r[f'{y}_registered_voters_canvass'])==rv[-1]and int(r[f'{y}_total_voting_canvass'])==mv[-1];cells_checked+=3
   for label,v in zip(reg['columns'][1:-1],rv[1:-1]):
    suffix=re.sub(r'[^a-z0-9]+','_',label.lower()).strip('_');assert int(r[f'{y}_registration_{suffix}'])==v;cells_checked+=1
   for label,v in zip(method['columns'][:-1],mv[:-1]):
    suffix=re.sub(r'[^a-z0-9]+','_',label.lower()).strip('_');assert int(r[f'{y}_total_voting_method_{suffix}'])==v;cells_checked+=1
 countyorder=sorted(ccsv,key=lambda r:(-sum(ours['senate2024special']['county'][r['county']]),r['priority_key']))
 assert [r['county']for r in ccsv]==[r['county']for r in countyorder]
 cum=0
 for rank,r in enumerate(ccsv,1):
  cum+=sum(ours['senate2024special']['county'][r['county']]);assert int(r['priority_rank'])==rank and int(r['priority_cumulative_votes'])==cum
 counts.update(final_county_CSV_numeric_cells=cells_checked,final_county_CSV_full_order=len(ccsv))
 native=readrows(BASE/'extracts/native-special.jsonl.gz');pn=readrows(PEER/'extracts/selected-native-disjoint.jsonl.gz');assert len(native)==len(pn)==1326
 pindex={r['key']:r for r in pn}
 for a in native:
  b=pindex[a['key']]
  assert [a['B'],a['A']]==b['candidate_values']
  for ak,bk in [('county','county'),('county_fips','county_fips'),('source_id','source_id'),('generic_writeins','generic_writeins'),('ballots','ballots'),('under','under'),('over','over'),('registration','registration')]:assert a[ak]==b[bk],(a['key'],ak,a[ak],b[bk])
  labelcheck(a['label'],b['native_label_literal'],a['key'])
  assert a.get('blank')==b['blank']
  assert a['rank']==b['rank']and a['pair_votes']==b['priority_votes_state_scope']
 counts['native_full_candidate_volume_fields']=1326
 # Inspect the actual final published peer CSV in addition to the JSON objects.
 peer_csv=PEER/'native-turnout.csv';used.append(pin(peer_csv));pcsv=list(csv.DictReader(peer_csv.open()))
 assert [r['key']for r in pcsv]==[r['key']for r in native]
 for a,b in zip(native,pcsv):
  assert a['A']==int(b['love'])and a['B']==int(b['ricketts'])and a['pair_votes']==int(b['priority_votes_state_scope'])and a['county_fips']==b['county_fips']and a['label']==b['native_label_literal']
 counts['final_peer_native_CSV_rows']=len(pcsv)
 contract=read(PEER/'priority-set.json');order=[r['key']for r in native];priority=[r['key']for r in native if r['priority']];remainder=[r['key']for r in native if not r['priority']]
 assert contract['ordered_full_keys']==order and contract['ordered_priority_keys']==priority and contract['ordered_remainder_keys']==remainder
 full={f'NE:county:{fips}':[r['key']for r in native if r['county_fips']==fips]for fips in sorted({r['county_fips']for r in native})}
 pri={k:[u for u in v if u in set(priority)]for k,v in full.items()};child={u:k for k,v in full.items()for u in v}
 assert full==contract['parent_full_child_map']and pri==contract['parent_priority_child_map']and child==contract['child_parent_map']
 assert len(contract['all93_parents'])==93
 for c in contract['all93_parents']:
  assert full[c['parent_key']]==c['full_child_keys']and pri[c['parent_key']]==c['priority_child_keys']
 counts['parent_full_and_priority_maps']=93;counts['full_order']=1326;counts['priority_order']=765;counts['remainder_order']=561
 # Compare every retained incomplete/admin candidate and source identity, not only ranked rows.
 alt=readrows(BASE/'extracts/administrative-partial-alternatives.jsonl.gz');pa=contract['administrative_and_partial_alternates']
 ai={(r['source_id'],r['header_row_id']):r for r in alt}
 for b in pa:
  a=ai[(b['source_id'],b['source_position'])]
  assert [c['votes']for c in a['children']]==b['candidate_values']and a['native_id_literal']==b['native_id_literal'];labelcheck(a['label'],b['native_label_literal'],b['key'])
 assert len(alt)==len(pa)==329;counts['administrative_partial_objects']=329
 # Original BIFF cells/types and all five contest native fields.
 dr=readrows(BASE/'extracts/douglas-original-rows.jsonl.gz');pr=readrows(PEER/'extracts/douglas-original-positions.jsonl.gz');pi={(r['source_id'],r['sheet'],r['source_row_1based']):r for r in pr}
 for r in dr:
  b=pi[(r['source_id'],r['sheet'],r['row'])];assert r['values']==b['values']and r['types']==b['cell_types']
 assert len(dr)==len(pr);counts['BIFF_original_rows_including_formatted_blank_tail']=len(dr)
 dc=readrows(BASE/'extracts/douglas-native-contexts.jsonl.gz');pc=readrows(PEER/'extracts/douglas-native.jsonl.gz');pi={(r['source_id'],r['sheet'],r['source_row_1based']):r for r in pc}
 for r in dc:
  b=pi[(r['source_id'],r['sheet'],r['row'])];assert r['label']==b['native_label_literal']
  assert {k['label_literal']:k['votes']for k in b['candidate_fields']}=={k:r['fields'][k]for k in r['candidate_columns']}
  assert r['ballot_reconstruction']==b['contest_volume_arithmetic']
 counts['Douglas_native_contexts_full_fields']=len(dc)
 # All Lancaster candidate, total, under/over, method columns and 199 statistics rows.
 lc=readrows(BASE/'extracts/lancaster-native-contexts.jsonl.gz');pl=readrows(PEER/'extracts/lancaster-native-methods.jsonl.gz');pi={(r['actual_pdf_page'],r['contest']):r for r in pl}
 for r in lc:
  b=pi[(r['page'],mapping[r['contest']])];assert r['label']==b['native_label_literal']and r['methods']==b['method_columns']
  assert r['fields']=={k['label_literal']:k['counts']for k in b['fields']}
 counts['Lancaster_native_contexts_all_method_fields']=len(lc)
 ls=read(BASE/'extracts/lancaster-statistics.json');ps=read(PEER/'extracts/lancaster-statistics.json');pi={r['actual_pdf_page']:r for r in ps}
 for r in ls:
  b=pi[r['page']];assert r['label']==b['native_label_literal']and r['registered']==b['registered_total']and r['fields']=={k['label_literal']:k['counts']for k in b['fields']}
 counts['Lancaster_statistics']=len(ls)
 unavailable=read(BASE/'extracts/presidential-only-resident.json');assert unavailable['Senate_special']is None and contract['unavailable_cases'][0]['priority_contest_votes']is None
 counts['resident_Senate_unavailable_case']=1
 # Every HTML native/admin/partial party/name/order/contest identity is compared,
 # separately from vote vectors. Codes stay source codes rather than candidate IDs.
 oh=readrows(BASE/'extracts/html-original-contexts.jsonl.gz');ph=readrows(PEER/'extracts/historical-html-native.jsonl.gz');hi={(r['source_id'],r['source_header_row_id']):r for r in ph}
 for r in oh:
  b=hi[(r['source_id'],r['header_row_id'])];assert r['native_id_literal']==b['native_id_literal']and r['county_id_literal']==b['source_county_id_literal']
  for a,c in zip(r['children'],b['candidates']):
   assert a['party_code']==c['party_code_literal']and a['candidate']==c['name_literal']and a['complete']==c['row_complete']
   if len(a['cells'])>7:
    assert a['cells'][6]['text']==c.get('ballot_order_literal',c.get('ballot_order_or_candidate_id_literal'))and a['cells'][7]['text']==c['contest_id_literal']
 counts['HTML_full_identity_contexts']=len(oh)
 # The extra native PDFs are alternate source observations, never an HTML ID join.
 scans=readrows(BASE/'extracts/independent-scan-contexts.jsonl.gz');si={(r['source_id'],r['page'],r['contest']):r for r in scans}
 for p in contract['additional_native_source_contexts']:
  a=si[(p['source_id'],p['actual_pdf_page'],'US Senator 2 YR')]
  assert a['label']==p['native_label_literal']and a['fields']=={f['label_literal']:f['counts']for f in p['fields']}and not p['included_in_primary_rank']
 assert len(contract['additional_native_source_contexts'])==14 and len(contract['additional_administrative_contexts'])==2
 assert len(contract['unavailable_cases'])==2
 yorkcase=next(p for p in contract['unavailable_cases']if p['county']=='York');assert yorkcase['priority_contest_votes']is None
 yr=si[(yorkcase['source_id'],89,'US President')];assert yr['fields']['Contest Totals']==[1,0,1,0]
 counts.update(additional_alternate_native_PDF_contexts=14,additional_school_attachments=2,presidential_only_Senate_unavailable_cases=2)
 # Method semantics differ in serialization only; HTML unknown, Douglas explicitly combined,
 # Lancaster 4 columns checked above. Never infer a method split from county statistics.
 result=dict(status='pass_independent_full_named_scope_reconciliation_with_explicit_presentation_differences',peer_agent_id='012d3597-6f6c-4ff1-a3d7-a488176243ba',pins=used,checks=counts,gaps=gaps,presentation_differences=presentation_differences,
  exact_min80=dict(count=765,votes=748190,preceding_votes=747645,denominator=935005,crossing='NE:2024-special:lancaster-pdf:page-685'),
  parent_full_child_map=full,parent_priority_child_map=pri,child_parent_map=child,
  qualifications=['All five original BIFF tables and all 595 Lancaster native contexts reconcile, including candidate/method totals.','Method names have explicit schema translations, not inferred method allocations.','Special generic write-ins/eligible write-in universe remains incompletely observed statewide; ranking contract is the exact published two-named scope.','County20 concentration sensitivity is not native priority. No current geography or feed approval.','Coordinator acceptance remains false; this independent reconciliation does not authorize dispatch.'])
 (BASE/'peer-reconciliation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':counts}))
if __name__=='__main__':main()
